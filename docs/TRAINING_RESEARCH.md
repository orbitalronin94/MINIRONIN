# MINIRONIN — Efficient training research

**Status:** research plan, not a selected recipe  
**Scope:** independently train the 9.97M-parameter baseline; no sibling workflow, script, optimizer configuration, or checkpoint is reused.

## Executive decision

Use a reproducible baseline first: causal next-token prediction, pre-tokenized and packed fixed-length sequences, AdamW, gradient clipping, warmup plus cosine decay, and fixed validation checkpoints. Optimize only after profiling the actual GitHub runner. Treat Muon as a challenger experiment, not as a presumed upgrade.

For a model this small, the bottleneck may be CPU/GPU utilization, Python/kernel-launch overhead, or input delivery rather than parameter memory. The objective is **quality gained per wall-clock hour and per processed token**, not peak tokens/second in isolation.

## Evidence and limits

1. Hoffmann et al. (NeurIPS 2022), *Training Compute-Optimal Large Language Models*, trained models from 70M parameters upward and found that compute-optimal token budgets scale with parameter count. The often-quoted ~20 training tokens per parameter is a useful large-model heuristic, **not a validated law for a 10M model**. We use it only to motivate a staged token-budget sweep, not to set a fixed promise. [Paper](https://arxiv.org/abs/2203.15556).
2. PyTorch's [Performance Tuning Guide](https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html) recommends profiling, fused operations where applicable, zero_grad with set_to_none, appropriate data loading, mixed precision on supported accelerators, and torch.compile where compilation cost is amortized. Each is a candidate optimization to measure on our runner.
3. PyTorch's [Transformer building blocks guide](https://docs.pytorch.org/tutorials/intermediate/transformer_building_blocks.html) documents fused scaled-dot-product attention and its integration with torch.compile. MINIRONIN already uses SDPA; verify which backend executes on each device.
4. Recent small-GPT optimizer comparisons report Muon can be competitive, but results depend on model, hardware, parameter partition, schedule, and token budget. This motivates a controlled trial; it does not prove Muon is best for MINIRONIN. [Example measured comparison](https://ttlab.hopto.org/blog/llm-training-2026-02-muon-measured?lang=en).

## Training system design

### Data path
- Convert admitted documents once into deterministic token shards after the tokenizer is frozen.
- Store token IDs in a compact integer format (uint16 is sufficient for vocabulary 23,000); validate range and endianness on read.
- Pack documents into fixed context windows while preserving an explicit EOS/document boundary. Never concatenate across train/validation boundaries.
- Prefer sequential or memory-mapped reads over parsing JSONL on every optimizer step.
- Record tokenizer SHA-256, corpus-manifest SHA-256, split IDs, packing version, and token count in every run.
- Start with context 256 for throughput profiling; compare context 512 after measuring quality and memory. Production config remains 512 unless evidence supports a change.

### Optimization baseline
- AdamW with separate parameter groups: decay matrix weights; no decay for biases and normalization parameters. Keep tied embeddings in a documented group.
- Sweep peak learning rates 1e-3, 3e-4, 1e-4; reject unstable or clearly underfitting runs.
- Warm up for 1–3% of optimizer steps, then cosine decay to 10% of peak LR.
- Global gradient norm clipping at 1.0; log pre-clip norm and non-finite counts.
- Use optimizer.zero_grad(set_to_none=True).
- Accumulate gradients to compare effective token batches (4k, 8k, 16k tokens/update) without requiring a large physical batch.
- Do not enable dropout, weight decay, label smoothing, or auxiliary losses without a controlled ablation.

### Hardware-specific execution
- **CPU:** FP32 baseline first; pin/measure PyTorch intra-op threads; benchmark num_workers 0/1/2/4 rather than assuming more workers help. Avoid oversubscribing cores. Record CPU model, logical/physical cores, RAM, and thread settings.
- **CUDA GPU:** benchmark BF16 when supported, otherwise FP16 with GradScaler; compare against FP32 for stability. Use pinned memory/non-blocking transfer only if input pipeline benefits. Record GPU model, peak allocated memory, and utilization.
- **Compilation:** compare eager against torch.compile only after a warmup run; report compile time separately and include it in end-to-end cost. Avoid it for tiny jobs if compile overhead dominates.
- **Attention:** retain scaled_dot_product_attention; record device/dtype and whether a fused backend is available. No custom attention kernel until profiling proves attention is the bottleneck.
- **Checkpointing:** unnecessary by default at this scale unless memory profiling shows a real constraint; recomputation can reduce throughput.

## Experiment ladder

| ID | Question | Controlled variants | Primary decision metric |
|---|---|---|---|
| T0 | Is the loop numerically sound? | 200–500 steps, fixed seed | finite loss/gradients; save-load parity |
| T1 | What sequence length is efficient? | 256 vs 512, equal tokens processed | validation loss per wall-clock hour |
| T2 | What token batch suits the runner? | 4k / 8k / 16k tokens per update | throughput and validation stability |
| T3 | Which LR is robust? | 1e-3 / 3e-4 / 1e-4 | validation loss at equal tokens |
| T4 | Does Muon beat AdamW? | same init/data/tokens/seed | paired validation loss and tokens/sec |
| T5 | Does compilation help? | eager vs compiled | end-to-end time including compile |
| T6 | Does mixed precision help? | FP32 vs BF16/FP16 where supported | speed, memory, numerical parity |
| T7 | What data budget is useful? | 5M / 20M / 50M / 100M tokens | validation learning curve and domain metrics |

Run one variable at a time initially. Repeat promising variants at least three seeds before declaring a winner. Never compare different token counts or validation sets as controlled trials.

## Measurement contract

Every run records:
- run ID, git SHA, config SHA, seed, device, software versions, CPU/GPU and thread settings;
- tokenizer and corpus manifest hashes, source/domain mix, exact tokens consumed;
- optimizer, LR schedule, effective tokens/update, sequence length, precision;
- wall time, warmup time, steady-state tokens/sec, steps/sec, peak memory;
- train and validation cross-entropy at fixed token intervals, gradient norm, skipped/overflow steps;
- validation metrics by language/domain and fixed evaluation IDs;
- checkpoint SHA-256 and exact resume metadata.

Report both **tokens/sec** and **validation loss at equal processed tokens**. A faster run that learns worse is not an efficiency win. Also report **validation loss improvement per wall-clock hour**.

## Stop and reject conditions

- Any NaN/Inf loss or gradients, silent data truncation, tokenizer/corpus hash mismatch, or train/validation overlap.
- A run that cannot resume deterministically enough to reproduce its next validation point.
- An optimizer winner based on a single seed or unequal token exposure.
- A speed optimization that materially changes numerical behavior or validation quality without an explicit accepted trade-off.
- A corpus source without auditable license/provenance admission.

## Initial recommendation

1. Keep AdamW + eager + FP32 as correctness baseline.
2. Implement token packing and fixed token-count batches before tuning optimizer kernels.
3. Benchmark the actual runner with a short, fixed-token pilot.
4. Test BF16/FP16 and compilation only on compatible GPU runners.
5. Run Muon as a paired research arm after baseline is stable.
6. Increase token budget gradually; do not assume the 20:1 heuristic transfers exactly to 10M parameters or a small heterogeneous corpus.

## References

- Hoffmann et al., 2022. [Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556).
- PyTorch. [Performance Tuning Guide](https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html).
- PyTorch. [Transformer building blocks](https://docs.pytorch.org/tutorials/intermediate/transformer_building_blocks.html).
- TT Lab, 2026. [AdamW vs Muon vs MUON+ measured on a small GPT](https://ttlab.hopto.org/blog/llm-training-2026-02-muon-measured?lang=en) — independent experimental report, not a universal result.
