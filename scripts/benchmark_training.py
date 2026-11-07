#!/usr/bin/env python3
"""Measure MINIRONIN's own training-step throughput on synthetic token IDs.

This is a hardware/implementation benchmark only. Synthetic data is not a
training corpus and no model-quality claim may be inferred from this report.
"""
from __future__ import annotations
import argparse
import json
import platform
import resource
import time
from dataclasses import replace
from pathlib import Path

import torch

from minironin import MiniRonin
from minironin.config import ModelConfig


def sync(device: torch.device) -> None:
    if device.type == "cuda":
        torch.cuda.synchronize(device)


def benchmark(config: ModelConfig, device: torch.device, batch: int,
              steps: int, warmup: int, seed: int) -> dict:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
        torch.cuda.reset_peak_memory_stats(device)
    model = MiniRonin(config).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
    x = torch.randint(config.vocab_size, (batch, config.context_length),
                      dtype=torch.long, device=device)
    start = time.perf_counter()
    last_loss = None
    for step in range(warmup + steps):
        optimizer.zero_grad(set_to_none=True)
        _, loss = model(x, x)
        if loss is None:
            raise RuntimeError("model did not return a training loss")
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        last_loss = float(loss.detach())
        if step + 1 == warmup:
            sync(device)
            start = time.perf_counter()
    sync(device)
    elapsed = time.perf_counter() - start
    tokens = batch * config.context_length * steps
    peak_memory = (torch.cuda.max_memory_allocated(device)
                   if device.type == "cuda" else None)
    return {
        "batch_size": batch,
        "sequence_length": config.context_length,
        "steps": steps,
        "warmup_steps": warmup,
        "tokens": tokens,
        "elapsed_seconds": round(elapsed, 4),
        "tokens_per_second": round(tokens / max(elapsed, 1e-9), 2),
        "steps_per_second": round(steps / max(elapsed, 1e-9), 4),
        "last_synthetic_loss": last_loss,
        "peak_cuda_memory_bytes": peak_memory,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=8)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--contexts", default="256,512")
    parser.add_argument("--batches", default="1,2")
    parser.add_argument("--threads", type=int, default=0,
                        help="0 keeps the PyTorch default")
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--output", default="benchmark-results/training-throughput.json")
    args = parser.parse_args()
    if args.steps < 1 or args.warmup < 0:
        parser.error("steps must be positive and warmup non-negative")
    if args.threads > 0:
        torch.set_num_threads(args.threads)
    if args.device == "cuda" and not torch.cuda.is_available():
        parser.error("CUDA requested but unavailable")
    device = torch.device(
        "cuda" if args.device == "cuda" or
        (args.device == "auto" and torch.cuda.is_available()) else "cpu"
    )
    base = ModelConfig.load("configs/model-10m.json")
    contexts = [int(v) for v in args.contexts.split(",")]
    batches = [int(v) for v in args.batches.split(",")]
    results = []
    for context in contexts:
        if context > base.context_length:
            raise SystemExit(f"context {context} exceeds configured maximum {base.context_length}")
        config = replace(base, context_length=context)
        for batch in batches:
            results.append(benchmark(config, device, batch, args.steps,
                                     args.warmup, args.seed))
    report = {
        "benchmark": "synthetic-forward-backward-AdamW",
        "warning": "synthetic data only; not a training run or quality evaluation",
        "git_revision": __import__("os").environ.get("GITHUB_SHA"),
        "device": str(device),
        "torch_version": torch.__version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "cpu": platform.processor(),
        "logical_cpu_count": __import__("os").cpu_count(),
        "torch_num_threads": torch.get_num_threads(),
        "parameter_count": MiniRonin(base).parameter_count(),
        "results": results,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
