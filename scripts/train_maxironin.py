#!/usr/bin/env python3
"""Run the 1,000-step MAXIRONIN 500M-effective CPU experiment."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from maxironin import MaxRoninConfig, MaxRoninLM


class FactoredAdafactor:
    """Minimal CPU Adafactor: factored second moments, no full-size moment tensors."""
    def __init__(self, params, lr=8e-5, beta2_decay=-0.8, eps=1e-30,
                 weight_decay=0.01, clip_threshold=1.0):
        self.params = list(params)
        self.lr = lr
        self.beta2_decay = beta2_decay
        self.eps = eps
        self.weight_decay = weight_decay
        self.clip_threshold = clip_threshold
        self.state = {}
        self.step_number = 0

    @torch.no_grad()
    def step(self):
        self.step_number += 1
        beta2 = 1.0 - self.step_number ** self.beta2_decay
        for param in self.params:
            grad = param.grad
            if grad is None:
                continue
            state = self.state.setdefault(id(param), {})
            if param.ndim >= 2:
                if "row" not in state:
                    state["row"] = torch.zeros(
                        (param.shape[0],) + (1,) * (param.ndim - 1),
                        dtype=param.dtype, device=param.device,
                    )
                    state["col"] = torch.zeros(
                        (1,) + tuple(param.shape[1:]),
                        dtype=param.dtype, device=param.device,
                    )
                square = grad.square()
                row_mean = square.mean(dim=tuple(range(1, square.ndim)), keepdim=True)
                col_mean = square.mean(dim=0, keepdim=True)
                state["row"].mul_(beta2).add_(row_mean, alpha=1.0 - beta2)
                state["col"].mul_(beta2).add_(col_mean, alpha=1.0 - beta2)
                row_mean_level = state["row"].mean().clamp_min(self.eps)
                variance = state["row"] * state["col"] / row_mean_level
            else:
                if "variance" not in state:
                    state["variance"] = torch.zeros_like(param)
                state["variance"].mul_(beta2).addcmul_(grad, grad, value=1.0 - beta2)
                variance = state["variance"]
            update = grad * torch.rsqrt(variance + self.eps)
            update_rms = update.square().mean().sqrt().clamp_min(self.eps)
            update.div_(torch.clamp(update_rms / self.clip_threshold, min=1.0))
            if self.weight_decay:
                param.mul_(1.0 - self.lr * self.weight_decay)
            param.add_(update, alpha=-self.lr)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def batch_from_memmap(data: np.memmap, rng: np.random.Generator,
                      batch_size: int, sequence_length: int, device: torch.device):
    rows = []
    for _ in range(batch_size):
        start = int(rng.integers(0, len(data) - sequence_length - 1))
        rows.append(np.asarray(data[start:start + sequence_length + 1], dtype=np.int64))
    batch = torch.from_numpy(np.stack(rows)).to(device=device, dtype=torch.long)
    return batch


@torch.no_grad()
def evaluate(model, data, seed: int, batches: int, sequence_length: int):
    model.eval()
    rng = np.random.default_rng(seed)
    losses = []
    for _ in range(batches):
        batch = batch_from_memmap(data, rng, 1, sequence_length, torch.device("cpu"))
        _, loss = model(batch, labels=batch)
        losses.append(float(loss))
    model.train()
    return sum(losses) / len(losses)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--steps", type=int, default=1000)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--sequence-length", type=int, default=128)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20261110)
    parser.add_argument("--resume-checkpoint", default=None)
    parser.add_argument("--initial-step", type=int, default=0)
    args = parser.parse_args()
    if args.steps != 1000:
        parser.error("Each MAXIRONIN segment is fixed at exactly 1,000 steps")
    if bool(args.resume_checkpoint) != bool(args.initial_step):
        parser.error("--resume-checkpoint and --initial-step must be supplied together")
    if args.sequence_length > 512:
        parser.error("Sequence length exceeds model context")
    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(2)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)
    torch.use_deterministic_algorithms(True)

    data_dir, out = Path(args.data_dir), Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    train_path, val_path = data_dir / "train.bin", data_dir / "validation.bin"
    train_data = np.memmap(train_path, mode="r", dtype="<u2")
    val_data = np.memmap(val_path, mode="r", dtype="<u2")
    if min(len(train_data), len(val_data)) <= args.sequence_length + 1:
        raise SystemExit("Tokenized train/validation data is too small")

    config = MaxRoninConfig()
    model = MaxRoninLM(config).cpu()
    if args.resume_checkpoint:
        resumed = torch.load(args.resume_checkpoint, map_location="cpu", weights_only=False)
        if resumed.get("completed_steps") != args.initial_step:
            raise SystemExit("Resume checkpoint step mismatch")
        if resumed.get("tokenizer_sha256") != sha256(data_dir / "tokenizer.json"):
            raise SystemExit("Resume checkpoint tokenizer SHA-256 mismatch")
        model.load_state_dict(resumed["model_state_dict"], strict=True)
        print(json.dumps({"event":"resume_checkpoint_loaded","completed_steps":args.initial_step,"optimizer_state":"restarted; original optimizer state was not archived"}),flush=True)
    trainable = model.parameter_count(trainable_only=True)
    total = model.parameter_count(trainable_only=False)
    expected = 500_141_056
    if trainable != expected or total != expected:
        raise SystemExit(f"Effective parameter audit failed: trainable={trainable}, total={total}, expected={expected}")
    if any(not p.requires_grad for p in model.parameters()):
        raise SystemExit("Frozen parameters found; MAXIRONIN must be 100% trainable")
    config.save(out / "config.json")
    print(json.dumps({
        "event": "model_initialized",
        "resume_from_step": args.initial_step,
        "optimizer_state_policy": "Adafactor reset at continuation boundary",
        "architecture": "decoder-only Transformer",
        "layers": config.n_layers, "width": config.d_model,
        "heads": config.n_heads, "ffn_width": config.d_ff,
        "vocab_size": config.vocab_size,
        "trainable_parameters": trainable,
        "all_parameters_effective": True,
        "parameter_tying": "token embedding and output head tied",
        "dtype": "float32",
        "optimizer": "factored Adafactor (no full-size Adam moments)",
        "gradient_checkpointing": config.gradient_checkpointing,
    }), flush=True)

    baseline = evaluate(model, val_data, args.seed + 1, 8, args.sequence_length)
    optimizer = FactoredAdafactor(model.parameters(), lr=8e-5)
    rng = np.random.default_rng(args.seed + 2)
    model.train()
    losses = []
    started = time.perf_counter()
    for step in range(1, args.steps + 1):
        progress = step / args.steps
        lr = 8e-5 * (0.2 + 0.8 * 0.5 * (1.0 + math.cos(math.pi * progress)))
        optimizer.lr = lr
        batch = batch_from_memmap(
            train_data, rng, args.batch_size, args.sequence_length, torch.device("cpu")
        )
        optimizer.zero_grad = None
        for parameter in model.parameters():
            parameter.grad = None
        _, loss = model(batch, labels=batch)
        if not torch.isfinite(loss):
            raise RuntimeError(f"Non-finite training loss at step {step}")
        loss.backward()
        optimizer.step()
        losses.append(float(loss.detach()))
        if step % 10 == 0:
            print(json.dumps({
                "event": "train_step", "step": step, "total_steps": args.steps,
                "loss": losses[-1], "lr": lr,
                "elapsed_seconds": round(time.perf_counter() - started, 2),
            }), flush=True)

    final = evaluate(model, val_data, args.seed + 1, 8, args.sequence_length)
    global_step = args.initial_step + args.steps
    checkpoint_path = out / f"maxironin-500m-step-{global_step}.pt"
    torch.save({
        "model_state_dict": model.state_dict(),
        "model_config": config.__dict__,
        "parameter_count": trainable,
        "trainable_parameter_count": trainable,
        "completed_steps": global_step,
        "segment_steps": args.steps,
        "resumed_from_step": args.initial_step,
        "tokenizer_vocab_size": config.vocab_size,
        "tokenizer_sha256": sha256(data_dir / "tokenizer.json"),
        "tokenization": "NFC + byte-level BPE, vocab 32768, isolated digits, <DOC>/<EOS>",
        "training_dtype": "float32",
        "optimizer": "factored Adafactor; optimizer state omitted from inference checkpoint",
    }, checkpoint_path)
    report = {
        "experiment": "MAXIRONIN-500M",
        "status": "completed" if args.steps == 1000 else "incomplete",
        "completed_steps": args.steps,
        "trainable_parameters": trainable,
        "total_parameters": total,
        "all_parameters_effective": True,
        "architecture": config.__dict__,
        "batch_size": args.batch_size,
        "sequence_length": args.sequence_length,
        "tokens_per_optimizer_step": args.batch_size * args.sequence_length,
        "training_tokens_approx": args.steps * args.batch_size * args.sequence_length,
        "optimizer": "factored Adafactor",
        "baseline_validation_loss": baseline,
        "final_validation_loss": final,
        "mean_training_loss_last_100": sum(losses[-100:]) / min(100, len(losses)),
        "elapsed_seconds": round(time.perf_counter() - started, 2),
        "checkpoint": checkpoint_path.name,
        "checkpoint_sha256": sha256(checkpoint_path),
        "tokenizer_sha256": sha256(data_dir / "tokenizer.json"),
        "interpretation": "1,000-step segment; optimizer state restarted because the initial inference artifact did not include optimizer state. Not a capability or convergence claim.",
    }
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
