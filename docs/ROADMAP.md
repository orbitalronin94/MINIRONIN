# MINIRONIN — Roadmap to v1.0

This roadmap describes MINIRONIN only. It does not import the workflows or training procedures of RONIN-IA or HERETIC-RONIN.

## CP-00 — Project boundary
- [x] Define independent project and ~10M parameter target.
- [x] Explicitly prohibit sibling workflows, procedures, and checkpoints.
- [ ] Record initial repository commit and baseline tree.

**Exit:** scope is documented and unambiguous.

## CP-01 — Source inventory
- [ ] Inventory data-bearing paths and available artifacts in RONIN-IA.
- [ ] Inventory data-bearing paths and available artifacts in HERETIC-RONIN.
- [ ] Exclude workflows, code, checkpoints, optimizer states, and logs unless separately approved as metadata.
- [ ] Produce source-by-source candidate register with sizes and file counts.

**Exit:** every proposed import has a concrete source locator.

## CP-02 — License and provenance audit
- [ ] Verify license at original upstream source, not only sibling-repo presence.
- [ ] Record retrieval date, upstream revision/URL, attribution requirements, and redistribution conditions.
- [ ] Reject unknown, incompatible, or untraceable sources.
- [ ] Record SHA-256 and immutable source manifest.

**Exit:** every admitted document has a defensible provenance and license record.

## CP-03 — Data library inheritance
- [x] Import the nine owner-authored Papers Markdown files into `data/inherited/papers/` at a pinned upstream revision, under internal-use-only authorization.
- [x] Preserve source revision, source filenames, and the explicit no-redistribution restriction.
- [ ] Generate and retain the successful SHA-256 audit manifest (workflow added; first run exposed and is fixing a README-count bug).
- [ ] Normalize admitted text to the canonical training schema.
- [ ] Run global cross-source exact/near-duplicate and holdout-contamination checks.
- [ ] Publish corpus statistics by source, language, domain, and license.

**Exit:** reproducible, auditable corpus snapshot with manifest hash.

## CP-04 — Open-source foundation selection
- [ ] Evaluate PyTorch, Tokenizers/SentencePiece, and compact Transformer references.
- [ ] Pin exact dependency versions and upstream commits.
- [ ] Review licenses and preserve notices.
- [ ] Implement only the minimum architecture required by the specification.

**Exit:** dependency register and clean-room MINIRONIN implementation plan.

## CP-05 — Tokenizer
- [ ] Choose tokenizer method and vocabulary size using corpus coverage and parameter budget.
- [ ] Train tokenizer on training split only.
- [ ] Measure fertility, unknown-token behavior, and Spanish/English coverage.
- [ ] Freeze tokenizer files and SHA-256.

**Exit:** deterministic tokenizer artifact and report.

## CP-06 — Model implementation
- [ ] Implement decoder-only Transformer baseline.
- [ ] Add exact parameter counter and config validation.
- [ ] Verify causal mask, tied embeddings, position handling, and shape invariants.
- [ ] Add save/load round-trip and deterministic forward tests.
- [ ] Verify total parameters are near 10M.

**Exit:** tested model implementation and parameter report.

## CP-07 — Data pipeline
- [ ] Implement streaming shard reader and deterministic batching.
- [ ] Ensure document boundaries and split isolation.
- [ ] Add reproducible packing and data-order controls.
- [ ] Test malformed and oversized examples.

**Exit:** stable token batches with recorded manifest/tokenizer hashes.

## CP-08 — Pilot experiments
- [ ] Run short smoke test for numerical stability.
- [ ] Measure throughput and memory on available runner hardware.
- [ ] Compare a small set of optimizer/schedule candidates using the experiment ladder in [TRAINING_RESEARCH.md](TRAINING_RESEARCH.md).
- [ ] Select training settings from measured evidence, not sibling defaults.

**Exit:** documented pilot report and frozen baseline recipe.

## CP-09 — Baseline training
- [ ] Train first full baseline from random initialization.
- [ ] Save checkpoint and complete metadata.
- [ ] Record token budget, wall time, loss curves, and hardware.
- [ ] Run the fixed validation suite.

**Exit:** reproducible baseline checkpoint and evaluation report.

## CP-10 — Quality iteration
- [ ] Identify failure clusters by domain and language.
- [ ] Improve data quality/balance or model configuration based on evidence.
- [ ] Keep sealed holdout untouched.
- [ ] Compare candidate to baseline on identical evaluation IDs.

**Exit:** measurable improvement without concealed regressions.

## CP-11 — Robustness and safety
- [ ] Test malformed prompts, repetition, hallucination, language switching, and long context.
- [ ] Document memorization/privacy risks and dataset exclusions.
- [ ] Add model limitations and usage guidance.

**Exit:** published limitations and robustness report.

## CP-12 — v1.0 release
- [ ] Freeze model config, tokenizer, corpus manifest, and checkpoint hashes.
- [ ] Publish model card, data statement, license register, and evaluation report.
- [ ] Confirm all tests and provenance checks pass.
- [ ] Tag v1.0 only after release gates are satisfied.

**Exit:** independently reproducible, documented ~10M model release.
