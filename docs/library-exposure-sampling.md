# Library-level exposure sampling (prepared for post-450k)

Preparation only: this branch is not wired into the active training workflow.
It does not change the current run, checkpoint, tokenizer, or optimizer.

## Activation gate

Do not activate before all of the following are true:

1. The 450,000-step byte-tokenizer checkpoint exists and its SHA-256 verifies.
2. The matched 450k holdout diary has been saved unchanged.
3. BPE-4096 has been trained from the training split only and its SHA-256 is fixed.
4. The 450k checkpoint has been migrated to BPE-4096 in a separate candidate;
   the original checkpoint remains immutable.
5. The new training split has explicit source provenance and a corpus signature.

## Library families and initial weights

- `heretic`: HERETIC math, science and general sources.
- `prodatphil`: PRODATPHIL book corpus.
- `anarchist`: curated anarchist library.
- `classics`: classics collection.
- `minironin_behavior`: authored behavior, identity, abstention, personality,
  engineering and lexicon datasets.

`configs/library-weights-v1.json` aggregates the current domain-level
`MIX_WEIGHTS` and normalizes them. The underlying family totals are HERETIC
0.574, PRODATPHIL 0.164, anarchist 0.025, classics 0.025 and MINIRONIN behavior
0.322 (total 1.110). The normalized values are initial experimental targets,
not estimates of corpus size or claims of optimality. Recalculate and review
them after the 450k/BPE migration; do not silently treat them as final.

## Provenance and token preparation

`scripts/library_provenance.py` maps explicit ingestion source labels to
library IDs. Unknown labels fail closed; domain names are not used as a proxy
for library identity. It also provides:

- `training_corpus_signature(train_docs_by_domain)`: deterministic hash over
  train-only document SHA-256 values and their library IDs.
- `iter_tokenized_training_rows(...)`: tokenizes one document at a time and
  yields train-only rows, avoiding a second full-corpus Python token list.

`scripts/token_store.py` writes those rows to a packed little-endian uint16
file and a small JSON index. BPE-4096 IDs fit in uint16. Runtime access is
read-only and memory-mapped; only the sampled window is copied into a batch.
The manifest binds the store to tokenizer SHA-256 and training-corpus
signature, and records hashes for both token data and index. The reader checks
hashes, offsets, split labels, document totals and byte counts.

This is a persistent cache, not a new source of truth: rebuild it whenever the
tokenizer SHA or train-corpus signature changes. Store only training documents.
Validation and holdout data must use separate fixed evaluation paths.

## Sampling behavior

`scripts/library_sampler.py` samples in three stages:
smooth weighted round-robin library -> shuffled document cycle -> token window.

- Library weights are renormalized over libraries actually present. A smooth
  weighted round-robin scheduler keeps cumulative exposure close to the exact
  target even with small batches, rather than relying on noisy independent draws.
  Missing configured libraries are explicitly listed in the report.
- Each library cycles through a shuffled deck of eligible documents before
  repeating a document, reducing accidental neglect of smaller sources.
- The seed, document IDs and sampled library are deterministic.
- Token windows are selected after the document, with no text tokenization in
  the training step.
- `validate_sequence_length(sequence_length)` preflights every weighted library\n  before training and fails with the full list of libraries whose documents\n  are too short.\n- Validation/holdout rows are rejected rather than silently admitted.

The report includes target share versus observed target-token share, sampled
target tokens, document uses, unique documents, eligible-document coverage
and repeat uses. Exposure shares are measured in BPE tokens, never bytes,
file sizes or document counts.

## Performance and checkpoint audit

At each checkpoint persist:

- sampler version, seed and effective normalized weights;
- tokenizer version and SHA-256;
- train-split corpus signature and token-store hashes;
- per-library sampled tokens, document uses, unique documents and coverage;
- steps/s, target tokens/s and source bytes/s.

BPE changes both token counts and output-softmax cost, so steps/s alone is not
a meaningful throughput comparison. Benchmark the memory-mapped reader and
batch construction on the GitHub runner before selecting final weights.

## Deferred integration

Before the first training step, call `validate_sequence_length(128)` (or the\nconfigured context window) and persist its eligible-document counts. After the\nactivation gate passes, integrate the provenance adapter and
memory-mapped store into `train_long_run.py`, then replace domain-only batch
selection with `LibrarySampler`. Keep the existing validation windows fixed
and independent. Every checkpoint/report must include the exact effective
weights and exposure report. Do not edit or dispatch the active 450k workflow
as part of this preparation.
