# MINIRONIN — Technical specification

**Status:** draft v0.1  
**Target:** approximately 10,000,000 trainable parameters  
**Project independence:** mandatory

## 1. Mission

Build a genuinely small, independently trained language model using carefully curated open data and the strongest practical open-source foundations suitable for a 10M-parameter budget.

MINIRONIN inherits *libraries of data* from RONIN-IA and HERETIC-RONIN. It does not inherit their procedures, workflows, training scripts, model weights, checkpoint lineage, or promotion systems.

## 2. Explicit inheritance boundary

### Allowed after admission review
- Text documents and dataset shards.
- Dataset metadata, source URLs, license notices, provenance records, and checksums.
- Public-domain or otherwise license-compatible evaluation/training material, subject to each source's terms.

### Forbidden by default
- `.github/workflows/**` from either sibling repository.
- Training/evaluation scripts, optimizer schedules, launchers, and promotion code.
- Model checkpoints, optimizer states, and teacher/student weights.
- Unverified artifacts or content whose license/provenance cannot be established.

A data file is not automatically safe to import merely because it exists in a sibling repository or artifact. Each source must have a source ID, upstream URL, license evidence, retrieval date, content hash, format, size, language/domain tags, and admission decision.

## 3. Model architecture candidate

Baseline: decoder-only causal Transformer, pre-layer normalization, learned or rotary position encoding (benchmark before locking), causal multi-head self-attention, gated or GELU MLP, residual connections, and tied input/output token embeddings.

| Component | Initial candidate |
|---|---:|
| Transformer blocks | 6 |
| Hidden width | 256 |
| Attention heads | 8 |
| Head dimension | 32 |
| MLP width | 768 |
| Vocabulary | tune around 22k–24k |
| Embedding/output weights | tied |
| Context length | 512 initially; extend only after memory/quality tests |
| Parameter budget | ~10M |

The vocabulary size is a parameter-budget lever. The configuration above is only a starting point: exact parameter count must be computed from the implemented module graph and recorded in a machine-readable model config. Do not describe the model as “10M” until that count is verified.

## 4. Open-source foundations

Prefer mature, auditable implementations and published methods over novel infrastructure. Candidate references to evaluate (not blanket approvals):

- **PyTorch** — tensor/autograd/runtime foundation; BSD-style license.
- **Hugging Face Tokenizers** — fast tokenizer implementation; Apache-2.0.
- **SentencePiece** — tokenizer training/runtime; Apache-2.0.
- **nanoGPT** — educational compact GPT reference; MIT. Reuse only after reviewing the exact upstream revision and retaining required notices.
- **GPT-NeoX / EleutherAI evaluation ecosystem** — reference material for model/evaluation conventions; check each component's license independently.

No dependency is approved merely by this list. Pin exact versions/commits and licenses in `docs/OPEN_SOURCE_REGISTER.md` before importing code.

## 5. Data design

Use a unified, documented schema with at least:
- `source_id`
- `document_id`
- `text`
- `language`
- `domain`
- `license`
- `source_url`
- `content_sha256`
- `split`
- `quality_flags`

Admission pipeline: inventory → license/provenance check → format validation → text extraction → normalization → exact deduplication → near-duplicate screening → quality filters → domain/language tagging → split assignment → immutable manifest.

Training data and evaluation data must be disjoint. Evaluation prompts/answers must never leak into training shards. Preserve source attribution and original license notices.

## 6. Training principles (new MINIRONIN design)

The training recipe will be designed and measured specifically for this model. It must not be copied from either sibling project.

Initial principles:
1. Establish a deterministic baseline and record seed, code revision, data manifest hash, tokenizer hash, config, and environment.
2. Use next-token causal language modeling as the initial objective.
3. Track token count, throughput, loss, gradient norm, learning rate, and parameter count.
4. Save immutable checkpoints with SHA-256.
5. Evaluate against fixed, held-out, domain-balanced sets.
6. Compare every candidate against the same baseline and same holdout.
7. Never infer quality from training loss or dataset size alone.

Optimizer, schedule, batch size, warmup, precision, and total token budget remain experimental decisions until hardware-aware pilot measurements exist.

## 7. Evaluation

A small model needs a realistic evaluation suite, not a single aggregate score. The initial suite should cover:
- language understanding and instruction following,
- arithmetic and elementary mathematics,
- code reading and simple programming,
- factual/scientific explanations,
- logic and multi-step reasoning,
- multilingual robustness (Spanish and English at minimum).

Use held-out, license-compatible benchmarks or newly authored questions. Keep a sealed holdout. Report per-domain scores, sample counts, confidence intervals where meaningful, failure examples, and regressions. Compare only runs using identical evaluation IDs and settings.

## 8. Reproducibility and release gates

A checkpoint is eligible for release only when:
- architecture and parameter count are verified;
- data manifest and licenses are auditable;
- training configuration and hashes are recorded;
- tests pass;
- held-out evaluation is complete;
- no material domain regression is hidden by the aggregate;
- model card documents limitations and intended use.

## 9. Non-goals

- Importing sibling training workflows or procedures.
- Starting from a sibling checkpoint.
- Maximizing raw corpus size at the expense of legality or quality.
- Claiming parity with larger models.
- Treating a passing training job as evidence of model capability.

## 10. Decision log

- 2026-11-07: MINIRONIN established as an independent ~10M-parameter model project.
- 2026-11-07: data-library inheritance from RONIN-IA and HERETIC-RONIN permitted; sibling workflows, procedures, and model checkpoints explicitly excluded.
