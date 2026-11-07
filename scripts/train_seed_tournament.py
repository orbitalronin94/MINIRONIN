#!/usr/bin/env python3
"""Thirty-seed, 100-step MINIRONIN byte-level corpus adaptation tournament.

This is a controlled pilot, not a claim of general reasoning ability. All
seeds see the same deterministic batches and are ranked on the same
document-disjoint validation set. The configured 9.97M parameter model is
retained; only a 257-symbol byte/EOS output slice is active in this first
pilot because the project tokenizer is not yet frozen.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import random
import re
import sys
import time
from collections import defaultdict
from dataclasses import asdict
from html.parser import HTMLParser
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from minironin import MiniRoninLM, ModelConfig  # noqa: E402

BYTE_EOS = 256
ACTIVE_VOCAB = 257
MIX_WEIGHTS = {
    "math": 0.40,
    "science": 0.25,
    "books": 0.20,
    "behavior": 0.10,
    "general": 0.05,
}
JSONL_SOURCES = {
    "open-web-math__open-web-math__default__train.jsonl": "math",
    "HuggingFaceTB__cosmopedia__auto_math_text__train.jsonl": "math",
    "secemp9__arxiv-complete__paper_text__train.jsonl": "science",
    "HuggingFaceTB__smollm-corpus__cosmopedia-v2__train.jsonl": "science",
    "HuggingFaceFW__fineweb-edu__sample-10BT__train.jsonl": "science",
    "CohereLabs__aya_dataset__default__train.jsonl": "general",
}
MAX_JSONL_BYTES_PER_SOURCE = 24 * 1024 * 1024
MAX_JSONL_DOCS_PER_SOURCE = 350
MAX_TEXT_CHARS = 18000


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data)


def clean_text(value: str) -> str:
    value = html.unescape(value.replace("\x00", " "))
    value = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", value,
                   flags=re.IGNORECASE | re.DOTALL)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"[ \t\r\f\v]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def strings_from_json(value, depth: int = 0) -> list[str]:
    if depth > 5:
        return []
    if isinstance(value, str):
        return [value] if len(value.strip()) >= 40 else []
    if isinstance(value, list):
        out = []
        for item in value[:40]:
            out.extend(strings_from_json(item, depth + 1))
        return out
    if isinstance(value, dict):
        preferred = (
            "text", "content", "document", "body", "abstract",
            "problem", "question", "solution", "answer", "instruction",
            "response", "completion", "passage",
        )
        found = []
        for key in preferred:
            if key in value:
                found.extend(strings_from_json(value[key], depth + 1))
        if found:
            return found
        ignored = {"id", "url", "source", "license", "metadata", "title",
                   "author", "date", "language", "timestamp"}
        out = []
        for key, item in value.items():
            if key not in ignored:
                out.extend(strings_from_json(item, depth + 1))
        return out
    return []


def add_doc(store, domain: str, text: str, source: str, source_file: str) -> None:
    text = clean_text(text)
    if len(text) < 80:
        return
    text = text[:MAX_TEXT_CHARS]
    digest = hashlib.sha256((domain + "\0" + text).encode("utf-8")).hexdigest()
    if digest in store["seen"]:
        return
    store["seen"].add(digest)
    store["docs"].append({
        "domain": domain,
        "text": text,
        "source": source,
        "source_file": source_file,
        "sha256": digest,
    })


def read_jsonl(path: Path, domain: str, store, max_bytes: int,
               max_docs: int, source_name: str) -> dict:
    consumed = 0
    accepted_before = len(store["docs"])
    sample_hash = hashlib.sha256()
    with path.open("rb") as stream:
        while consumed < max_bytes and len(store["docs"]) - accepted_before < max_docs:
            line = stream.readline()
            if not line:
                break
            consumed += len(line)
            sample_hash.update(line)
            try:
                obj = json.loads(line)
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            parts = strings_from_json(obj)
            if parts:
                # Keep problem/solution and text fields together when present.
                text = "\n".join(parts)
                add_doc(store, domain, text, source_name, str(path))
    return {
        "path": str(path),
        "domain": domain,
        "sampled_bytes": consumed,
        "sample_sha256": sample_hash.hexdigest(),
        "documents_added": len(store["docs"]) - accepted_before,
    }


def read_book_texts(root: Path, store) -> list[dict]:
    rows = []
    allowed = {".txt", ".md", ".xml", ".tei", ".html", ".htm"}
    if not root.exists():
        raise SystemExit(f"Book corpus missing: {root}")
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in allowed):
        raw = path.read_bytes()[:512 * 1024]
        if not raw:
            continue
        text = raw.decode("utf-8", errors="replace")
        text = clean_text(text)
        if len(text) < 200:
            continue
        before = len(store["docs"])
        # Chunk long works without treating chapters as independent books.
        chunk_chars = 12000
        step = 10000
        for start in range(0, min(len(text), 60000), step):
            chunk = text[start:start + chunk_chars]
            if len(chunk) >= 200:
                add_doc(store, "books", chunk, "PRODATPHIL v0.3", str(path))
        rows.append({
            "path": str(path),
            "bytes_read": len(raw),
            "sample_sha256": hashlib.sha256(raw).hexdigest(),
            "chunks_added": len(store["docs"]) - before,
        })
    if not rows:
        raise SystemExit("No usable PRODATPHIL text files found")
    return rows


def load_curated_jsonl(path: Path, domain: str, store, source: str) -> int:
    if not path.exists():
        return 0
    before = len(store["docs"])
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            context = row.get("context", "")
            question = row.get("question", "")
            answer = row.get("answer", "")
            combined = f"Contexto: {context}\nPregunta: {question}\nRespuesta: {answer}"
            add_doc(store, domain, combined, source, str(path))
    return len(store["docs"]) - before


def split_documents(documents: list[dict]):
    grouped = defaultdict(list)
    for doc in documents:
        grouped[doc["domain"]].append(doc)
    train, validation = defaultdict(list), defaultdict(list)
    for domain, docs in grouped.items():
        docs = sorted(docs, key=lambda d: d["sha256"])
        if len(docs) < 2:
            train[domain].extend(docs)
            continue
        n_val = max(1, min(len(docs) - 1, round(len(docs) * 0.10)))
        validation[domain].extend(docs[:n_val])
        train[domain].extend(docs[n_val:])
    return train, validation


def encode_doc(doc: dict) -> torch.Tensor:
    raw = doc["text"].encode("utf-8", errors="replace")
    ids = list(raw) + [BYTE_EOS]
    return torch.tensor(ids, dtype=torch.long)


def weighted_domains(available: dict) -> tuple[list[str], list[float]]:
    names = [name for name in MIX_WEIGHTS if available.get(name)]
    if not names:
        raise SystemExit("No training domains available")
    total = sum(MIX_WEIGHTS[name] for name in names)
    return names, [MIX_WEIGHTS[name] / total for name in names]


def make_batch(encoded_docs: list[torch.Tensor], batch_size: int,
               sequence_length: int, rng: random.Random) -> torch.Tensor:
    rows = []
    for _ in range(batch_size):
        doc = rng.choice(encoded_docs)
        if len(doc) < sequence_length + 1:
            raise ValueError("Encoded document shorter than training window")
        start = rng.randrange(0, len(doc) - sequence_length)
        rows.append(doc[start:start + sequence_length + 1])
    return torch.stack(rows)


def build_schedules(train_docs, val_docs, steps, batch_size, sequence_length):
    names, probs = weighted_domains(train_docs)
    train_encoded = {
        name: [encode_doc(d) for d in train_docs[name]]
        for name in names
    }
    train_rng = random.Random(20261107)
    schedule = []
    for _ in range(steps):
        chosen = train_rng.choices(names, weights=probs, k=batch_size)
        rows = []
        for domain in chosen:
            doc = train_rng.choice(train_encoded[domain])
            start = train_rng.randrange(0, len(doc) - sequence_length)
            rows.append(doc[start:start + sequence_length + 1])
        schedule.append(torch.stack(rows))
    validation = {}
    val_rng = random.Random(314159)
    for domain in sorted(val_docs):
        if not val_docs[domain]:
            continue
        encoded = [encode_doc(d) for d in val_docs[domain]]
        batches = []
        for _ in range(4):
            batches.append(make_batch(encoded, batch_size, sequence_length, val_rng))
        validation[domain] = batches
    return schedule, validation, names, probs


def evaluate(model, validation, device):
    model.eval()
    per_domain = {}
    with torch.no_grad():
        for domain, batches in validation.items():
            losses = []
            for batch in batches:
                batch = batch.to(device)
                _, loss = model(batch, labels=batch, vocab_limit=ACTIVE_VOCAB)
                losses.append(float(loss))
            per_domain[domain] = sum(losses) / len(losses)
    available = [d for d in per_domain if d in MIX_WEIGHTS]
    total = sum(MIX_WEIGHTS[d] for d in available)
    overall = sum(per_domain[d] * MIX_WEIGHTS[d] for d in available) / total
    model.train()
    return overall, per_domain


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--heretic-root", default="data/inherited/heretic-corpus")
    parser.add_argument("--books-root", default="data/inherited/prodatphil-en-v0.3")
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--sequence-length", type=int, default=128)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--output-dir", default="seed-tournament")
    args = parser.parse_args()

    if args.seeds < 1 or args.steps < 1 or args.batch_size < 1:
        parser.error("seeds, steps and batch-size must be positive")
    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    device = torch.device("cpu")

    store = {"docs": [], "seen": set()}
    heretic_root = Path(args.heretic_root)
    if not heretic_root.exists():
        raise SystemExit(f"HERETIC corpus missing: {heretic_root}")
    source_audit = []
    for filename, domain in JSONL_SOURCES.items():
        path = heretic_root / filename
        if path.exists():
            source_audit.append(read_jsonl(
                path, domain, store, MAX_JSONL_BYTES_PER_SOURCE,
                MAX_JSONL_DOCS_PER_SOURCE, f"HERETIC:{filename}"
            ))
        else:
            print(f"WARNING: selected HERETIC source not present: {filename}")

    books_root = Path(args.books_root)
    book_audit = read_book_texts(books_root, store)
    behavior_count = load_curated_jsonl(
        ROOT / "data/curated/minironin-behavior-v1.jsonl",
        "behavior", store, "MINIRONIN-authored-behavior-v1"
    )
    if behavior_count == 0:
        raise SystemExit("No curated MINIRONIN behavior examples loaded")

    train_docs, val_docs = split_documents(store["docs"])
    for domain in MIX_WEIGHTS:
        if not train_docs.get(domain):
            raise SystemExit(f"Training split is empty for required domain: {domain}")
        if not val_docs.get(domain):
            raise SystemExit(f"Validation split is empty for required domain: {domain}")

    base_config = ModelConfig.load(ROOT / "configs/model-10m.json")
    probe = MiniRoninLM(base_config)
    parameter_count = probe.parameter_count()
    del probe
    if parameter_count != 9_970_176:
        raise SystemExit(f"Unexpected model parameter count: {parameter_count}")

    schedule, validation, mix_names, mix_probs = build_schedules(
        train_docs, val_docs, args.steps, args.batch_size, args.sequence_length
    )
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    manifest = {
        "protocol": "30-seed fixed-data byte-level adaptation pilot",
        "active_vocabulary": ACTIVE_VOCAB,
        "tokenization": "UTF-8 bytes 0..255 plus EOS=256; configured 23k embedding remains intact but only first 257 output rows are active",
        "parameter_count": parameter_count,
        "heretic_source_files": source_audit,
        "book_files": book_audit,
        "curated_behavior_examples_loaded": behavior_count,
        "documents_total": len(store["docs"]),
        "documents_by_domain": {d: len([x for x in store["docs"] if x["domain"] == d]) for d in MIX_WEIGHTS},
        "train_documents_by_domain": {d: len(train_docs.get(d, [])) for d in MIX_WEIGHTS},
        "validation_documents_by_domain": {d: len(val_docs.get(d, [])) for d in MIX_WEIGHTS},
        "training_mix": {d: w for d, w in zip(mix_names, mix_probs)},
        "steps_per_seed": args.steps,
        "seed_count": args.seeds,
        "batch_size": args.batch_size,
        "sequence_length": args.sequence_length,
        "validation": "document-disjoint; same precomputed windows for every seed",
    }
    (output / "dataset-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    results = []
    best_loss = math.inf
    best_seed = None
    best_state = None
    started = time.perf_counter()
    for index in range(args.seeds):
        seed = 9500 + index
        torch.manual_seed(seed)
        model = MiniRoninLM(base_config).to(device)
        optimizer = torch.optim.AdamW(
            model.parameters(), lr=3e-4, betas=(0.9, 0.95), weight_decay=0.01
        )
        losses = []
        seed_start = time.perf_counter()
        for step, batch in enumerate(schedule):
            progress = (step + 1) / args.steps
            warmup = min(1.0, (step + 1) / max(1, min(5, args.steps // 10)))
            cosine = 0.5 * (1.0 + math.cos(math.pi * progress))
            lr = 3e-4 * warmup * (0.1 + 0.9 * cosine)
            for group in optimizer.param_groups:
                group["lr"] = lr
            batch = batch.to(device)
            optimizer.zero_grad(set_to_none=True)
            _, loss = model(batch, labels=batch, vocab_limit=ACTIVE_VOCAB)
            if not torch.isfinite(loss):
                raise RuntimeError(f"Non-finite training loss at seed={seed}, step={step + 1}")
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            losses.append(float(loss.detach()))
        val_loss, per_domain = evaluate(model, validation, device)
        elapsed = time.perf_counter() - seed_start
        row = {
            "seed": seed,
            "steps": args.steps,
            "final_train_loss": losses[-1],
            "mean_train_loss_last_20": sum(losses[-20:]) / min(20, len(losses)),
            "validation_loss": val_loss,
            "validation_loss_by_domain": per_domain,
            "elapsed_seconds": round(elapsed, 2),
        }
        results.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
        if val_loss < best_loss:
            best_loss = val_loss
            best_seed = seed
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        del optimizer, model
    total_elapsed = time.perf_counter() - started

    if best_state is None:
        raise SystemExit("No valid seed candidate produced")
    checkpoint = {
        "model_state_dict": best_state,
        "model_config": asdict(base_config),
        "parameter_count": parameter_count,
        "seed": best_seed,
        "steps": args.steps,
        "active_vocabulary": ACTIVE_VOCAB,
        "tokenization": "UTF-8 bytes + EOS",
        "validation_loss": best_loss,
        "selection_metric": "lowest fixed document-disjoint validation loss",
        "dataset_manifest": manifest,
    }
    torch.save(checkpoint, output / "best-checkpoint.pt")
    report = {
        "status": "completed",
        "warning": "pilot only; byte-level tokenization and 100 steps per seed do not establish general reasoning capability",
        "seed_count": args.seeds,
        "steps_per_seed": args.steps,
        "total_optimizer_steps": args.seeds * args.steps,
        "best_seed": best_seed,
        "best_validation_loss": best_loss,
        "best_validation_loss_by_domain": next(
            x["validation_loss_by_domain"] for x in results if x["seed"] == best_seed
        ),
        "parameter_count": parameter_count,
        "active_vocabulary": ACTIVE_VOCAB,
        "total_elapsed_seconds": round(total_elapsed, 2),
        "results_ranked": sorted(results, key=lambda x: x["validation_loss"]),
    }
    (output / "tournament-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
