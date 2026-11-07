#!/usr/bin/env python3
"""Resumable 200,000-step continuation of the winning MINIRONIN seed."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
import time
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from minironin import MiniRoninLM, ModelConfig  # noqa: E402
from train_seed_tournament import (  # noqa: E402
    ACTIVE_VOCAB, MIX_WEIGHTS, add_doc, build_schedules, clean_text,
    encode_doc, evaluate, load_curated_jsonl, read_book_texts, read_jsonl,
    weighted_domains, JSONL_SOURCES, MAX_JSONL_BYTES_PER_SOURCE,
    MAX_JSONL_DOCS_PER_SOURCE,
)

TOTAL_STEPS = 200_000
CHECKPOINT_EVERY = 10_000
BATCH_SIZE = 2
SEQUENCE_LENGTH = 128
BASE_SEED = 20261107


def load_training_data(heretic_root: Path, books_root: Path):
    store = {"docs": [], "seen": set()}
    source_audit = []
    for filename, domain in JSONL_SOURCES.items():
        path = heretic_root / filename
        if path.exists():
            source_audit.append(read_jsonl(
                path, domain, store, MAX_JSONL_BYTES_PER_SOURCE,
                MAX_JSONL_DOCS_PER_SOURCE, f"HERETIC:{filename}"
            ))
    book_audit = read_book_texts(books_root, store)
    behavior_count = load_curated_jsonl(
        ROOT / "data/curated/minironin-behavior-v1.jsonl",
        "behavior", store, "MINIRONIN-authored-behavior-v1"
    )
    if behavior_count == 0:
        raise SystemExit("No curated MINIRONIN behavior examples loaded")
    train_docs, val_docs = __import__("train_seed_tournament").split_documents(store["docs"])
    for domain in ("math", "science", "books", "behavior"):
        if not train_docs.get(domain) or not val_docs.get(domain):
            raise SystemExit(f"Missing train/validation documents for {domain}")
    names, probs = weighted_domains(train_docs)
    encoded = {name: [encode_doc(d) for d in train_docs[name]] for name in names}
    # Reuse the exact fixed validation-window construction from the seed tournament.
    _, validation, _, _ = build_schedules(
        train_docs, val_docs, 1, BATCH_SIZE, SEQUENCE_LENGTH
    )
    manifest = {
        "source_files": source_audit,
        "book_files": book_audit,
        "behavior_examples": behavior_count,
        "documents_total": len(store["docs"]),
        "documents_by_domain": {
            d: sum(1 for x in store["docs"] if x["domain"] == d) for d in MIX_WEIGHTS
        },
        "training_mix": {d: w for d, w in zip(names, probs)},
        "validation": "fixed document-disjoint windows; same corpus and seed-tournament split",
    }
    return encoded, names, probs, validation, manifest


def batch_for_step(encoded, names, probs, global_step):
    rng = random.Random(BASE_SEED + global_step)
    domains = rng.choices(names, weights=probs, k=BATCH_SIZE)
    rows = []
    for domain in domains:
        doc = rng.choice(encoded[domain])
        if len(doc) < SEQUENCE_LENGTH + 1:
            raise ValueError(f"Document shorter than training window in {domain}")
        start = rng.randrange(0, len(doc) - SEQUENCE_LENGTH)
        rows.append(doc[start:start + SEQUENCE_LENGTH + 1])
    return torch.stack(rows)


def learning_rate(global_step: int) -> float:
    warmup_steps = 500
    if global_step <= warmup_steps:
        return 3e-4 * global_step / warmup_steps
    progress = min(1.0, (global_step - warmup_steps) / (TOTAL_STEPS - warmup_steps))
    cosine = 0.5 * (1.0 + math.cos(math.pi * progress))
    return 3e-5 + (3e-4 - 3e-5) * cosine


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--heretic-root", required=True)
    parser.add_argument("--books-root", required=True)
    parser.add_argument("--input-checkpoint", required=True)
    parser.add_argument("--output-dir", default="long-training")
    parser.add_argument("--start-step", type=int, required=True)
    parser.add_argument("--steps", type=int, default=CHECKPOINT_EVERY)
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()

    if args.start_step < 0 or args.start_step >= TOTAL_STEPS:
        parser.error("start-step must be in [0, 199999]")
    if args.steps != CHECKPOINT_EVERY or args.start_step % CHECKPOINT_EVERY:
        parser.error("Each segment must be exactly 10,000 steps, aligned to a checkpoint")
    if args.start_step + args.steps > TOTAL_STEPS:
        parser.error("Segment exceeds the 200,000-step plan")

    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    device = torch.device("cpu")
    encoded, names, probs, validation, manifest = load_training_data(
        Path(args.heretic_root), Path(args.books_root)
    )

    config = ModelConfig.load(ROOT / "configs/model-10m.json")
    model = MiniRoninLM(config).to(device)
    parameter_count = model.parameter_count()
    if parameter_count != 9_970_176:
        raise SystemExit(f"Unexpected model parameter count: {parameter_count}")

    source = torch.load(args.input_checkpoint, map_location="cpu", weights_only=False)
    if source.get("active_vocabulary") != ACTIVE_VOCAB:
        raise SystemExit("Seed checkpoint active vocabulary mismatch")
    if source.get("parameter_count") != parameter_count:
        raise SystemExit("Seed checkpoint parameter count mismatch")
    model.load_state_dict(source["model_state_dict"], strict=True)

    optimizer = torch.optim.AdamW(
        model.parameters(), lr=3e-4, betas=(0.9, 0.95), weight_decay=0.01
    )
    if args.start_step:
        if source.get("completed_steps") != args.start_step:
            raise SystemExit("Resume checkpoint step does not match --start-step")
        if "optimizer_state_dict" not in source:
            raise SystemExit("Resume checkpoint is missing optimizer state")
        optimizer.load_state_dict(source["optimizer_state_dict"])
        if "torch_rng_state" in source:
            torch.set_rng_state(source["torch_rng_state"])

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    segment_started = time.perf_counter()
    losses = []
    model.train()

    for local_step in range(1, args.steps + 1):
        global_step = args.start_step + local_step
        lr = learning_rate(global_step)
        for group in optimizer.param_groups:
            group["lr"] = lr
        batch = batch_for_step(encoded, names, probs, global_step).to(device)
        optimizer.zero_grad(set_to_none=True)
        _, loss = model(batch, labels=batch, vocab_limit=ACTIVE_VOCAB)
        if not torch.isfinite(loss):
            raise RuntimeError(f"Non-finite loss at global step {global_step}")
        loss.backward()
        grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        losses.append(float(loss.detach()))
        if local_step % 100 == 0:
            print(json.dumps({
                "global_step": global_step,
                "loss": losses[-1],
                "lr": lr,
                "grad_norm": float(grad_norm),
            }), flush=True)

    validation_loss, validation_by_domain = evaluate(model, validation, device)
    completed = args.start_step + args.steps
    elapsed = round(time.perf_counter() - segment_started, 2)
    report = {
        "status": "segment_completed",
        "completed_steps": completed,
        "total_steps": TOTAL_STEPS,
        "segment_steps": args.steps,
        "seed_from_tournament": source.get("seed"),
        "parameter_count": parameter_count,
        "active_vocabulary": ACTIVE_VOCAB,
        "mean_train_loss_last_100": sum(losses[-100:]) / min(100, len(losses)),
        "validation_loss": validation_loss,
        "validation_loss_by_domain": validation_by_domain,
        "elapsed_seconds": elapsed,
        "learning_rate_next": learning_rate(min(completed + 1, TOTAL_STEPS)),
        "dataset_manifest": manifest,
    }
    checkpoint = {
        "model_state_dict": {k: v.detach().cpu() for k, v in model.state_dict().items()},
        "optimizer_state_dict": optimizer.state_dict(),
        "model_config": source["model_config"],
        "parameter_count": parameter_count,
        "seed": source.get("seed"),
        "completed_steps": completed,
        "total_steps": TOTAL_STEPS,
        "active_vocabulary": ACTIVE_VOCAB,
        "tokenization": source.get("tokenization", "UTF-8 bytes + EOS"),
        "validation_loss": validation_loss,
        "validation_loss_by_domain": validation_by_domain,
        "dataset_manifest": manifest,
        "torch_rng_state": torch.get_rng_state(),
    }
    checkpoint_path = output / f"checkpoint-{completed:06d}.pt"
    torch.save(checkpoint, checkpoint_path)
    (output / f"report-{completed:06d}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output / "latest.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    digest = hashlib.sha256(checkpoint_path.read_bytes()).hexdigest()
    (output / f"checkpoint-{completed:06d}.sha256").write_text(
        f"{digest}  {checkpoint_path.name}\n", encoding="utf-8"
    )
    print(json.dumps({
        "checkpoint": str(checkpoint_path),
        "checkpoint_sha256": digest,
        "completed_steps": completed,
        "validation_loss": validation_loss,
        "elapsed_seconds": elapsed,
    }), flush=True)


if __name__ == "__main__":
    main()
