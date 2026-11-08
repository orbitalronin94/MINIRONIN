# Library-level exposure sampling (prepared for post-450k)

This is infrastructure preparation only. It is deliberately not wired into the
active 450k training run and does not change its batches, checkpoint, tokenizer,
or optimizer.

## Activation gate

Do not activate before all of the following are true:

1. The 450,000-step byte-tokenizer checkpoint exists and its SHA-256 verifies.
2. The matched 450k holdout diary has been saved unchanged.
3. The 4,096-token BPE tokenizer has been trained from the training split only,
   versioned, and hashed.
4. The checkpoint has been migrated to BPE-4096 in a separate candidate; the
   original 450k checkpoint remains immutable.
5. Every document has an explicit `library_id`, `split`, and tokenized length.

## Initial library groups

- `heretic`: HERETIC text sources, including math/science/general domains.
- `prodatphil`: PRODATPHIL books.
- `anarchist`: the curated anarchist library.
- `classics`: the classics collection.
- `minironin_behavior`: MINIRONIN-authored behavior, identity, abstention,
  personality, engineering and lexicon datasets.

The initial weights in `configs/library-weights-v1.json` aggregate the current
domain-level `MIX_WEIGHTS` into these five families and normalize them. They
are starting targets, not claims about actual corpus size or ideal learning.

## Runtime contract

`scripts/library_sampler.py` samples in three stages:
library -> document -> token window. It accepts training-split documents only,
uses a seeded PRNG, renormalizes weights over available libraries, and reports
target share versus observed token share, document uses, and unique documents.

The caller should tokenize once and cache `token_ids`; do not tokenize text in
the training step. Build the document split before constructing this sampler.
Never provide validation or holdout rows to it. Keep validation sampling
separate and fixed across candidate comparisons.

## Exposure audit

At each checkpoint, persist:
- sampler version and seed;
- weights and normalized effective probabilities;
- tokenizer ID/version and SHA-256;
- train-split corpus signature;
- sampled tokens, document uses and unique documents by library;
- observed exposure share and target drift.

Measure shares in tokenizer tokens, not bytes, file sizes, or document counts.
Also record optimizer steps/s, tokens/s and bytes/s: BPE changes the token
count and softmax cost, so steps/s alone is misleading.

## Next integration

After the 450k holdout and tokenizer migration, add explicit library provenance
during ingestion in `train_long_run.py`, feed cached token IDs into this
sampler, and write `library_exposure` into each report/checkpoint manifest.
Do not infer library identity from domain names: multiple libraries can share
a domain, and a single library can contain several domains.
