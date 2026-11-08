# RFC: semantic activation of the reserved vocabulary and EOS-safe migration

**Status:** draft; intentionally not enabled  
**Activation gate:** the 500,000-step training run must finish, its checkpoint must be archived with SHA-256, and its paired holdout must be recorded.  
**Scope:** prepare a reversible migration from the current byte/EOS training path to a 23,000-ID vocabulary. This RFC does not alter the current training workflow or checkpoint format.

## 1. Verified current implementation

The current model already allocates a 23,000-row token embedding and ties `lm_head.weight` to that embedding. The training pipeline activates only IDs 0–256:

- IDs 0–255: individual UTF-8 bytes.
- ID 256: EOS (`BYTE_EOS`).
- IDs 257–22,999: allocated but not used by the current byte-level training objective (22,743 rows).

The current corpus encoder appends EOS to every document. The model shifts labels internally and applies cross-entropy to the next-token targets. Therefore EOS is present in training targets today; the migration must preserve and explicitly test this behavior rather than assume EOS has never been supervised.

There is also a hard-coded `[:257]` output slice in `MiniRoninLM.forward_cached()`. Any expanded vocabulary must remove that assumption or make the active vocabulary an explicit, validated argument. The regular `forward()` already accepts `vocab_limit`.

Current batching samples windows from individual documents and does not introduce PAD tokens. Do not reserve a PAD ID or silently conflate padding with EOS. If padded batches are added later, PAD must have its own ID and be excluded from loss with `ignore_index` or an equivalent explicit mask.

## 2. Target vocabulary layout

Keep the existing byte IDs stable to preserve a lossless fallback path:

| ID range | Meaning |
|---|---|
| 0–255 | UTF-8 byte fallback |
| 256 | EOS |
| 257–22,999 | 22,743 learned BPE/subword tokens |

The BPE inventory must be learned deterministically from the admitted training corpus, not hand-filled with topic labels or arbitrary semantic categories. A token is not intrinsically meaningful because it has a dictionary gloss: its embedding becomes useful through contextual training.

Requirements:

- Train tokenizer statistics only on the training split; never use validation or holdout text to construct the vocabulary.
- Use a fixed, versioned tokenizer configuration and save its exact vocabulary, merge rules, corpus manifest, and SHA-256 hashes.
- Retain byte fallback for every UTF-8 input, including unseen strings.
- Do not force all 22,743 rows to be populated with low-frequency fragments. The target size is a ceiling; report actual usable entries and frequency distribution. If the requirement remains exactly 23,000 active IDs, fill only with corpus-supported merges and document any entries that cannot meet the minimum frequency.
- Reject duplicate token strings, reserved-ID collisions, malformed UTF-8 handling, and non-deterministic builds.

## 3. Embedding migration

The embedding matrix is already 23,000 × 256 in the default configuration; the migration should not resize it. Preserve rows 0–256 bit-for-bit from the 500k parent checkpoint.

Initialize each new BPE row compositionally from the existing byte embeddings of its UTF-8 byte sequence (for example, a length-normalized mean, with a documented deterministic rule). Then adapt all new rows through next-token training. Since the input embedding and output head are tied, each row participates in both roles.

Do not claim that compositional initialization supplies learned semantics. It only gives a stable starting point; semantic behavior must be acquired from real corpus occurrences and gradient updates. Track per-token corpus frequency, occurrence count, gradient/update evidence, embedding norm, and loss contribution. Flag dead or near-dead rows.

## 4. EOS, PAD, and generation contract

- EOS remains ID 256 throughout migration.
- EOS must be appended to each independent training document and remain an ordinary supervised next-token target.
- No EOS masking: it must contribute to the loss.
- PAD is not introduced in this migration. If future batching requires it, assign a distinct ID and mask PAD targets only; never use EOS as PAD.
- Generation must stop immediately when EOS is emitted, must not decode EOS as visible text, and must have a tested maximum-token fallback for samples that never emit EOS.
- Cached and uncached inference must produce matching logits for the same active vocabulary.
- Replace the cached inference hard-coded 257-row head with an explicit active-vocabulary setting and test both legacy (257) and migrated (23,000) modes.

## 5. Compute and performance risk

Expanding the output projection from 257 to 23,000 logits multiplies its per-position output width by approximately 89.5×. The embedding storage is already allocated, but the full output projection and softmax are not free. Measure:

- CPU tokens/second and training steps/second on the same GitHub-hosted runner class;
- peak resident memory and checkpoint size;
- forward, backward, and optimizer time separately;
- validation loss and per-domain loss;
- percentage of BPE IDs actually observed and receiving updates.

Do not assume the larger vocabulary is a speed optimization. Benchmark before choosing full softmax, sampled/adaptive alternatives, or a staged activation schedule. Any alternative objective must be evaluated for bias and exactness.

## 6. Required implementation sequence

1. **Freeze parent:** after the 500k run completes, download its checkpoint/report, verify SHA-256, and run the fixed holdout. Keep the parent immutable.
2. **Build tokenizer artifact:** deterministic BPE training from training-only corpus; produce vocabulary, merges, manifest, coverage and frequency reports.
3. **Migration utility:** copy legacy rows exactly; initialize added rows from byte embeddings; preserve tied weights; write a new checkpoint with explicit tokenizer version/hash and parent checkpoint hash.
4. **EOS and inference fixes:** explicit active vocabulary in cached inference; stop-on-EOS generation; PAD remains absent unless separately designed.
5. **Tests:** deterministic tokenizer round-trip; UTF-8 byte fallback; stable legacy IDs; EOS target included in shifted loss; PAD/EOS distinction if PAD is ever added; tied-weight identity; migration preserves first 257 rows exactly; all token IDs in range; cached/uncached parity; generation stops at EOS.
6. **Paired evaluation:** same fixed holdout IDs, prompt formatting, generation settings and hardware. Report legacy-vs-migrated responses, per-domain results, EOS termination rate, cap-hit rate, token throughput and hashes. Do not promote on training loss alone.

## 7. Acceptance gates

- 500k parent checkpoint and holdout archived and hashed.
- Tokenizer build is deterministic and its training split is demonstrably disjoint from validation/holdout.
- IDs 0–256 remain stable; all byte inputs remain representable.
- Every new vocabulary entry has auditable corpus support; unused rows are reported, not mislabeled as semantically active.
- EOS remains supervised and generation termination is verified.
- Cached and uncached inference work for the selected active vocabulary.
- CPU runtime and memory fit the free GitHub Actions runner with adequate margin.
- Paired holdout shows no unacceptable regression; any quality gain is reported with uncertainty and domain breakdown.

## 8. Safety and activation

This branch is deliberately a draft. It must not be merged into `main`, added to the current 500k workflow's trigger paths, or used to launch training until the 500k checkpoint and holdout gate is satisfied and the migration implementation has passed its tests. The first migrated checkpoint is a candidate, never an automatic promotion.
