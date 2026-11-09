#!/usr/bin/env python3
"""Build deterministic BACKDOOR_BPE candidates from an explicitly admitted train split."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from minironin.tokenizer import BASE_ACTIVE_VOCAB, ByteNgramTokenizer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-jsonl", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--min-frequency", type=int, default=8)
    parser.add_argument("--min-documents", type=int, default=3)
    parser.add_argument("--min-bytes", type=int, default=3)
    parser.add_argument("--max-bytes-per-ngram", type=int, default=12)
    parser.add_argument("--max-corpus-bytes", type=int, default=50_000_000)
    args = parser.parse_args()
    if not (1 <= args.max_tokens <= 1024 and 2 <= args.min_bytes <= args.max_bytes_per_ngram <= 32):
        parser.error("Invalid token or n-gram limits")

    counts: Counter[bytes] = Counter()
    documents: dict[bytes, set[str]] = defaultdict(set)
    corpus_digest = hashlib.sha256()
    admitted_docs = set()
    bytes_seen = 0
    records = 0
    with args.train_jsonl.open(encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("split") != "train" or row.get("train_eligible") is not True:
                raise SystemExit(f"{args.train_jsonl}:{line_no}: expected split=train and train_eligible=true")
            if row.get("admission_status") != "admitted":
                raise SystemExit(f"{args.train_jsonl}:{line_no}: source is not explicitly admitted")
            document_id = str(row.get("document_id", "")).strip()
            text = row.get("text")
            if not document_id or not isinstance(text, str) or not text:
                raise SystemExit(f"{args.train_jsonl}:{line_no}: missing document_id/text")
            if document_id in admitted_docs:
                # Repeated rows from the same document may be valid, but count each document once.
                continue
            admitted_docs.add(document_id)
            raw = text.encode("utf-8")
            corpus_digest.update(document_id.encode("utf-8") + b"\0" + hashlib.sha256(raw).digest())
            remaining = args.max_corpus_bytes - bytes_seen
            if remaining <= 0:
                break
            if len(raw) > remaining:
                raw = raw[:remaining]
            bytes_seen += len(raw)
            records += 1
            # Never form n-grams across document or line boundaries.
            for segment in raw.splitlines():
                for size in range(args.min_bytes, args.max_bytes_per_ngram + 1):
                    if len(segment) < size:
                        continue
                    for offset in range(0, len(segment) - size + 1):
                        candidate = segment[offset:offset + size]
                        try:
                            candidate.decode("utf-8", errors="strict")
                        except UnicodeDecodeError:
                            continue
                        counts[candidate] += 1
                        documents[candidate].add(document_id)

    ranked = [
        (token, count, len(documents[token]))
        for token, count in counts.items()
        if count >= args.min_frequency and len(documents[token]) >= args.min_documents
    ]
    ranked.sort(key=lambda item: (-(item[1] * (len(item[0]) - 1)), -item[1], -len(item[0]), item[0]))
    selected = []
    used = set()
    for token, count, doc_count in ranked:
        if token in used:
            continue
        selected.append({
            "id": BASE_ACTIVE_VOCAB + len(selected),
            "hex": token.hex(),
            "text": token.decode("utf-8"),
            "frequency": count,
            "document_frequency": doc_count,
            "byte_length": len(token),
            "estimated_savings": count * (len(token) - 1),
        })
        used.add(token)
        if len(selected) >= args.max_tokens:
            break

    manifest = {
        "schema": "minironin-backdoor-bpe-v1",
        "tokenizer_name": "BACKDOOR_BPE",
        "version": 1,
        "base_active_vocab": BASE_ACTIVE_VOCAB,
        "eos_id": 256,
        "active_vocab": BASE_ACTIVE_VOCAB + len(selected),
        "selection": {
            "algorithm": "frequency-times-byte-savings; deterministic tie-break",
            "min_frequency": args.min_frequency,
            "min_documents": args.min_documents,
            "min_bytes": args.min_bytes,
            "max_bytes_per_ngram": args.max_bytes_per_ngram,
            "max_corpus_bytes": args.max_corpus_bytes,
            "bytes_scanned": bytes_seen,
            "unique_train_documents": len(admitted_docs),
            "records_scanned": records,
            "training_corpus_sha256": corpus_digest.hexdigest(),
            "split": "train-only",
        },
        "tokens": selected,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tokenizer = ByteNgramTokenizer(manifest)
    print(json.dumps({
        "tokenizer": "BACKDOOR_BPE",
        "active_vocab": tokenizer.active_vocab,
        "added_tokens": len(selected),
        "tokenizer_sha256": tokenizer.sha256,
        "training_corpus_sha256": corpus_digest.hexdigest(),
        "bytes_scanned": bytes_seen,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
