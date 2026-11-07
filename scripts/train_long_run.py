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
    ACTIVE_VOCAB, MIX_WEIGHTS, add_doc, clean_text, evaluate,
    load_curated_jsonl, weighted_domains, split_documents,
)

TOTAL_STEPS = 200_000
CHECKPOINT_EVERY = 10_000
BATCH_SIZE = 2
SEQUENCE_LENGTH = 128
BASE_SEED = 20261107


TEXT_SUFFIXES = {".jsonl", ".ndjson", ".json", ".txt", ".md", ".xml", ".tei", ".html", ".htm", ".csv", ".tsv", ".parquet"}
SKIP_NAME_PARTS = ("license", "readme", "metadata", "manifest", "schema", "checksum", "sha256", "wav", "mp3", "flac", "arrow", "image", "video")


def infer_domain(path: Path) -> str:
    name = path.name.lower()
    if any(x in name for x in ("math", "gsm", "algebra", "arith")):
        return "math"
    if any(x in name for x in ("arxiv", "science", "cosmopedia", "fineweb", "stem")):
        return "science"
    if any(x in name for x in ("book", "gutenberg", "prodatphil", "literature")):
        return "books"
    return "general"


def add_full_text(store, domain: str, text: str, source: str, source_file: str) -> int:
    text = clean_text(text)
    if len(text) < 200:
        return 0
    before = len(store["docs"])
    for offset in range(0, len(text), 16000):
        chunk = text[offset:offset + 18000]
        if len(chunk) >= 200:
            add_doc(store, domain, chunk, source, source_file)
        if offset + 18000 >= len(text):
            break
    return len(store["docs"]) - before


def extract_text_values(value):
    if isinstance(value, str):
        if len(value.strip()) >= 40:
            yield value
    elif isinstance(value, list):
        for item in value:
            yield from extract_text_values(item)
    elif isinstance(value, dict):
        preferred = ("text", "content", "document", "body", "abstract", "problem", "question", "solution", "answer", "instruction", "response", "completion", "passage")
        used = set()
        for key in preferred:
            if key in value:
                used.add(key)
                yield from extract_text_values(value[key])
        if not used:
            ignored = {"id", "url", "source", "license", "metadata", "title", "author", "date", "language", "timestamp", "image", "audio", "video", "path", "filename"}
            for key, item in value.items():
                if key not in ignored:
                    yield from extract_text_values(item)


def read_full_jsonl(path: Path, domain: str, store, source_name: str = "HERETIC") -> dict:
    before, rows, invalid = len(store["docs"]), 0, 0
    digest = hashlib.sha256()
    opener = __import__("gzip").open if path.name.lower().endswith(".gz") else open
    with opener(path, "rb") as stream:
        for line in stream:
            digest.update(line)
            if not line.strip():
                continue
            rows += 1
            try:
                obj = json.loads(line)
            except (UnicodeDecodeError, json.JSONDecodeError):
                invalid += 1
                continue
            for value in extract_text_values(obj):
                add_full_text(store, domain, value, source_name + ":" + path.name, str(path))
    return {"path": str(path), "format": "jsonl", "domain": domain, "bytes": path.stat().st_size, "rows": rows, "invalid_rows": invalid, "documents_added": len(store["docs"]) - before, "sha256": digest.hexdigest()}


def read_full_text(path: Path, domain: str, store, source_name: str = "HERETIC") -> dict:
    before = len(store["docs"])
    digest = hashlib.sha256()
    opener = __import__("gzip").open if path.name.lower().endswith(".gz") else open
    buffer = ""
    with opener(path, "rt", encoding="utf-8", errors="replace") as stream:
        for line in stream:
            digest.update(line.encode("utf-8", errors="replace"))
            buffer += line
            if len(buffer) >= 24000:
                add_full_text(store, domain, buffer, "HERETIC:" + path.name, str(path))
                buffer = buffer[-2000:]
        if buffer:
            add_full_text(store, domain, buffer, "HERETIC:" + path.name, str(path))
    return {"path": str(path), "format": path.suffix.lower(), "domain": domain, "bytes": path.stat().st_size, "documents_added": len(store["docs"]) - before, "sha256": digest.hexdigest()}


def read_full_parquet(path: Path, domain: str, store) -> dict:
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise SystemExit("Parquet source found but pyarrow is unavailable") from exc
    before, rows = len(store["docs"]), 0
    digest = hashlib.sha256()
    with path.open("rb") as raw_stream:
        for block in iter(lambda: raw_stream.read(1024 * 1024), b""):
            digest.update(block)
    parquet = pq.ParquetFile(path)
    for batch in parquet.iter_batches(batch_size=128):
        for obj in batch.to_pylist():
            rows += 1
            for value in extract_text_values(obj):
                add_full_text(store, domain, value, "HERETIC:" + path.name, str(path))
    return {"path": str(path), "format": "parquet", "domain": domain, "bytes": path.stat().st_size, "rows": rows, "documents_added": len(store["docs"]) - before, "sha256": digest.hexdigest()}


def read_full_json(path: Path, domain: str, store) -> dict:
    before = len(store["docs"])
    raw = path.read_bytes()
    try:
        obj = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"path": str(path), "format": "json", "domain": domain, "bytes": len(raw), "documents_added": 0, "error": str(exc)}
    for value in extract_text_values(obj):
        add_full_text(store, domain, value, "HERETIC:" + path.name, str(path))
    return {"path": str(path), "format": "json", "domain": domain, "bytes": len(raw), "documents_added": len(store["docs"]) - before, "sha256": hashlib.sha256(raw).hexdigest()}


def read_full_books(root: Path, store) -> list[dict]:
    if not root.exists():
        raise SystemExit("Book corpus missing: " + str(root))
    audit = []
    allowed = {".txt", ".md", ".xml", ".tei", ".html", ".htm"}
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in allowed):
        if any(part in path.name.lower() for part in SKIP_NAME_PARTS):
            continue
        audit.append(read_full_text(path, "books", store, "PRODATPHIL v0.3"))
    if not audit:
        raise SystemExit("No usable full-text book files found")
    return audit


def load_training_data(heretic_root: Path, books_root: Path, cache_path: Path):
    if cache_path.exists():
        cached = torch.load(cache_path, map_location="cpu", weights_only=False)
        print(json.dumps({"dataset_cache": "reused", **cached["manifest"]}, ensure_ascii=False), flush=True)
        return cached["train_docs"], cached["names"], cached["probs"], cached["validation"], cached["manifest"]

    store = {"docs": [], "seen": set()}
    discovered = sorted(p for p in heretic_root.rglob("*") if p.is_file())
    if not discovered:
        raise SystemExit("HERETIC corpus directory is empty")
    source_audit = []
    for path in discovered:
        lower, suffix = path.name.lower(), path.suffix.lower()
        if any(part in lower for part in SKIP_NAME_PARTS):
            continue
        domain = infer_domain(path)
        if suffix in {".jsonl", ".ndjson"} or lower.endswith(".jsonl.gz"):
            source_audit.append(read_full_jsonl(path, domain, store))
        elif suffix == ".json":
            source_audit.append(read_full_json(path, domain, store))
        elif suffix == ".parquet":
            source_audit.append(read_full_parquet(path, domain, store))
        elif suffix in TEXT_SUFFIXES or lower.endswith((".txt.gz", ".md.gz")):
            source_audit.append(read_full_text(path, domain, store))

    book_audit = read_full_books(books_root, store)
    behavior_count = load_curated_jsonl(ROOT / "data/curated/minironin-behavior-v1.jsonl", "behavior", store, "MINIRONIN-authored-behavior-v1")
    if behavior_count == 0:
        raise SystemExit("No curated MINIRONIN behavior examples loaded")
    train_docs, val_docs = split_documents(store["docs"])
    for domain in ("math", "science", "books", "behavior"):
        if not train_docs.get(domain) or not val_docs.get(domain):
            raise SystemExit("Missing train/validation documents for " + domain)
    names, probs = weighted_domains(train_docs)
    val_rng, validation = random.Random(314159), {}
    for domain in sorted(val_docs):
        batches = []
        for _ in range(4):
            rows = []
            for _ in range(BATCH_SIZE):
                raw = list(val_rng.choice(val_docs[domain])["text"].encode("utf-8", errors="replace")) + [ACTIVE_VOCAB - 1]
                if len(raw) < SEQUENCE_LENGTH + 1:
                    continue
                offset = val_rng.randrange(0, len(raw) - SEQUENCE_LENGTH)
                rows.append(torch.tensor(raw[offset:offset + SEQUENCE_LENGTH + 1], dtype=torch.long))
            if len(rows) == BATCH_SIZE:
                batches.append(torch.stack(rows))
        if batches:
            validation[domain] = batches
    missing_validation = [d for d in ("math", "science", "books", "behavior") if not validation.get(d)]
    if missing_validation:
        raise SystemExit("Missing full-corpus validation windows for: " + ", ".join(missing_validation))
    manifest = {
        "corpus_policy": "recursive full textual HERETIC ingest; no per-source byte/document cap",
        "heretic_discovered_files": len(discovered),
        "heretic_ingested_files": len(source_audit),
        "heretic_files": source_audit,
        "book_files": book_audit,
        "behavior_examples": behavior_count,
        "documents_total": len(store["docs"]),
        "documents_by_domain": {d: sum(1 for x in store["docs"] if x["domain"] == d) for d in MIX_WEIGHTS},
        "training_mix": {d: w for d, w in zip(names, probs)},
        "validation": "document-disjoint fixed windows from full-corpus split",
        "excluded_files": [{"path": str(p), "bytes": p.stat().st_size} for p in discovered if p not in {Path(x["path"]) for x in source_audit}],
        "excluded_policy": "binary audio/video/image, parquet/arrow and metadata/license/manifest files; never counted as trained text",
    }
    payload = {"train_docs": dict(train_docs), "names": names, "probs": probs, "validation": validation, "manifest": manifest}
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(payload, cache_path)
    print(json.dumps({"dataset_cache": "created", **manifest}, ensure_ascii=False), flush=True)
    return train_docs, names, probs, validation, manifest


def batch_for_step(train_docs, names, probs, global_step):
    rng = random.Random(BASE_SEED + global_step)
    domains = rng.choices(names, weights=probs, k=BATCH_SIZE)
    rows = []
    for domain in domains:
        raw = list(rng.choice(train_docs[domain])["text"].encode("utf-8", errors="replace")) + [ACTIVE_VOCAB - 1]
        if len(raw) < SEQUENCE_LENGTH + 1:
            raise ValueError("Document shorter than training window in " + domain)
        start = rng.randrange(0, len(raw) - SEQUENCE_LENGTH)
        rows.append(torch.tensor(raw[start:start + SEQUENCE_LENGTH + 1], dtype=torch.long))
    return torch.stack(rows)


def learning_rate(global_step: int, total_steps: int = TOTAL_STEPS,
                  schedule_start_step: int = 0, schedule_start_lr: float = 3e-4) -> float:
    warmup_steps = 500
    if schedule_start_step == 0 and global_step <= warmup_steps:
        return 3e-4 * global_step / warmup_steps
    if total_steps <= schedule_start_step:
        raise ValueError("total_steps must exceed schedule_start_step")
    progress = min(1.0, max(0.0, (global_step - schedule_start_step) / (total_steps - schedule_start_step)))
    cosine = 0.5 * (1.0 + math.cos(math.pi * progress))
    return 3e-5 + (schedule_start_lr - 3e-5) * cosine


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--heretic-root", required=True)
    parser.add_argument("--books-root", required=True)
    parser.add_argument("--input-checkpoint", required=True)
    parser.add_argument("--output-dir", default="long-training")
    parser.add_argument("--start-step", type=int, required=True)
    parser.add_argument("--steps", type=int, default=CHECKPOINT_EVERY)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--dataset-cache", default="long-training/full-corpus-cache.pt")
    parser.add_argument("--total-steps", type=int, default=TOTAL_STEPS)
    parser.add_argument("--schedule-start-step", type=int, default=0)
    parser.add_argument("--schedule-start-lr", type=float, default=1.0404e-4)
    args = parser.parse_args()

    if args.total_steps <= 0 or args.start_step < 0 or args.start_step >= args.total_steps:
        parser.error("total-steps must be positive and start-step must be below it")
    if args.schedule_start_step < 0 or args.schedule_start_step >= args.total_steps:
        parser.error("schedule-start-step must be below total-steps")
    if args.steps != CHECKPOINT_EVERY or args.start_step % CHECKPOINT_EVERY:
        parser.error("Each segment must be exactly 10,000 steps, aligned to a checkpoint")
    if args.start_step + args.steps > args.total_steps:
        parser.error("Segment exceeds total-steps")

    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    device = torch.device("cpu")
    train_docs, names, probs, validation, manifest = load_training_data(
        Path(args.heretic_root), Path(args.books_root), Path(args.dataset_cache)
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
        lr = learning_rate(global_step, args.total_steps, args.schedule_start_step, args.schedule_start_lr)
        for group in optimizer.param_groups:
            group["lr"] = lr
        batch = batch_for_step(train_docs, names, probs, global_step).to(device)
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
        "total_steps": args.total_steps,
        "segment_steps": args.steps,
        "seed_from_tournament": source.get("seed"),
        "parameter_count": parameter_count,
        "active_vocabulary": ACTIVE_VOCAB,
        "mean_train_loss_last_100": sum(losses[-100:]) / min(100, len(losses)),
        "validation_loss": validation_loss,
        "validation_loss_by_domain": validation_by_domain,
        "elapsed_seconds": elapsed,
        "learning_rate_next": learning_rate(min(completed + 1, args.total_steps), args.total_steps, args.schedule_start_step, args.schedule_start_lr),
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
