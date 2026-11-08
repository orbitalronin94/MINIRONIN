# MINIRONIN Checkpoint Bridge

The Checkpoint Bridge preserves learned information across MINIRONIN generations.
It is deliberately separated from training: inspection and teacher-target export
do not update weights, launch a workflow, or promote a candidate.

## Current capabilities

### 1. Inspect historical checkpoints

```bash
python scripts/checkpoint_bridge.py inspect --checkpoint path/to/checkpoint.pt
```

The report includes the file SHA-256, architecture/configuration, step count,
active vocabulary, parent hash, optimizer-state availability, and every tensor's
shape, dtype, element count, and finite-value status.

### 2. Export Transformer teacher targets

Prepare a JSONL file with one prompt per line:

```json
{"id":"example-001","text":"¿Por qué el cielo parece azul?"}
{"id":"example-002","text":"Explica la diferencia entre correlación y causalidad."}
```

Then run:

```bash
python scripts/checkpoint_bridge.py export-teacher \
  --checkpoint path/to/transformer-checkpoint.pt \
  --prompts data/bridge/prompts.jsonl \
  --output artifacts/teacher-targets.jsonl.gz \
  --top-k 16 --temperature 1.0 --max-context 128
```

For every prompt, the exporter stores byte-token input IDs, top-k teacher token
IDs and probabilities at every position, and the probability mass omitted by
top-k. The manifest records both input and output hashes and the exact teacher
checkpoint hash. The active vocabulary is the existing byte vocabulary:
IDs 0..255 plus EOS=256.

This creates a portable distillation target that a future Mamba or other student
can consume. It does **not** itself perform distillation or training.

## Important compatibility limits

- Transformer attention/MLP tensors cannot be copied into Mamba SSM tensors by
  reshaping. Architecture-specific conversion requires a learned mapping or
  distillation and must be validated against the teacher.
- Exact tensor transfer is appropriate only for genuinely compatible tensors
  (for example, embeddings with matching token IDs and compatible dimensions).
- Optimizer state is architecture- and parameter-layout-specific. Do not reuse
  it after changing architecture unless every parameter mapping is proven.
- Historical checkpoints may have different wrappers. Unsupported formats fail
  loudly rather than silently guessing.
- A lower training/validation loss is not a promotion criterion. Compare generated
  behavior on the unchanged holdout and retain parent/teacher hashes.

## Next implementation stages

1. Build a catalog over every recoverable checkpoint and workflow artifact.
2. Add explicit, tested tensor adapters for compatible Transformer width/depth
   changes and embedding projections.
3. Add a student-side KL distillation runner for Mamba with frozen teacher,
   fixed prompt IDs, reproducible manifests, and a strict no-promotion default.
4. Add hidden-state alignment only where a mathematically justified projection
   exists; do not assume hidden spaces from different architectures are aligned.
