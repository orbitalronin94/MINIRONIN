#!/usr/bin/env python3
"""Prepare a training-only projection from the verified integrated evidence stack.

The SQLite RAG index is validated and preserved as provenance/inference evidence;
the model is trained on admitted source text plus evidence-conditioned awake rows.
The candidate BPE is recorded but NOT activated because the 810k checkpoint uses
UTF-8 byte IDs + EOS (active vocabulary 257).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sqlite3
from collections import Counter
from pathlib import Path


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def domain_for(row: dict) -> str:
    source = str(row.get("source_id", "")).lower()
    if "cosmopedia" in source or source == "papers":
        return "science"
    allowed = {
        "math", "science", "books", "anarchist", "classics", "behavior",
        "general", "abstention", "abstain_plain", "abstain_literary",
        "abstain_koan", "aristocrat", "casuist", "scientist", "oracle",
        "indifference", "lexicon", "identity", "engineering",
    }
    domain = str(row.get("domain") or "general").lower()
    return domain if domain in allowed else "general"


def dataset_for(domain: str) -> str:
    special = {
        "math": "math-admitted",
        "science": "facts-admitted",
        "behavior": "minironin-behavior-v1",
        "identity": "minironin-identity-v1",
        "engineering": "minironin-engineering-v1",
        "abstention": "minironin-abstention-50k-v1",
        "abstain_plain": "minironin-abstain-plain-50k-v1",
        "abstain_literary": "minironin-abstain-literary-50k-v1",
        "abstain_koan": "minironin-abstain-koan-50k-v1",
        "aristocrat": "minironin-aristocrat-trivial-50k-v1",
        "casuist": "minironin-casuist-cynic-50k-v1",
        "scientist": "minironin-scientist-exhausted-50k-v1",
        "oracle": "minironin-oracle-doom-50k-v1",
        "indifference": "minironin-error404-indifference-50k-v1",
        "lexicon": "minironin-lexicon-diagnostic-v1",
    }
    return special.get(domain, "admitted-" + (domain or "general"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stack", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    root = args.stack
    manifest_path = root / "integrated-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    library = manifest["library"]
    rag_summary = manifest["rag"]
    tokenizer = manifest["tokenizer"]
    awake = manifest["awake_rows"]
    assert manifest.get("holdout_read") is False
    assert manifest.get("training_performed") is False
    assert library.get("holdout_read") is False
    assert library.get("train_eligible", 0) > 0
    assert library.get("validation_split", 0) > 0
    assert rag_summary.get("holdout_read") is False
    assert rag_summary.get("training_performed") is False
    assert rag_summary.get("chunks_unique", 0) > 0
    assert tokenizer.get("eos_id") == 256 and tokenizer.get("active_vocab", 0) >= 257
    assert awake.get("train", 0) > 0 and awake.get("validation", 0) > 0

    db_path = root / "rag/minironin-rag.sqlite"
    db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    db_manifest = json.loads(db.execute("SELECT value FROM metadata WHERE key='manifest'").fetchone()[0])
    chunks = db.execute("SELECT count(*) FROM chunks").fetchone()[0]
    db.close()
    assert db_manifest.get("holdout_read") is False
    assert db_manifest.get("training_performed") is False
    assert chunks == db_manifest.get("chunks_unique") == rag_summary["chunks_unique"]
    assert "HERETIC:Cosmopedia-v0.1-curated" in db_manifest.get("sources", [])

    documents = list(read_jsonl(root / "library/canonical/documents.jsonl"))
    train_docs = [
        d for d in documents
        if d.get("admission_status") == "admitted"
        and d.get("train_eligible") is True
        and d.get("split") == "train"
        and len(str(d.get("text", "")).strip()) >= 200
    ]
    awake_rows = list(read_jsonl(root / "awake-rows/train.jsonl"))
    assert len(train_docs) > 0 and len(awake_rows) > 0
    assert all(r.get("admission_status") == "admitted" and r.get("train_eligible") is True and r.get("split") == "train" for r in awake_rows)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    source_counts = Counter()
    with gzip.open(args.output, "wt", encoding="utf-8", newline="\n") as out:
        for d in train_docs:
            domain = domain_for(d)
            row = {
                "text": d["text"].strip(),
                "domain": domain,
                "dataset": dataset_for(domain),
                "source_id": "integrated-admitted-library",
                "source": d.get("source_id", "unknown"),
                "synthetic": False,
                "document_id": d["document_id"],
                "source_sha256": d["sha256"],
                "license": d.get("license"),
                "rights_status": d.get("rights_status"),
            }
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            counts[domain] += 1
            source_counts[str(d.get("source_id", "unknown"))] += 1
        for r in awake_rows:
            domain = domain_for(r)
            row = {
                "text": str(r["text"]).strip(),
                "domain": domain,
                "dataset": dataset_for(domain),
                "source_id": "integrated-awake-rows",
                "source": r.get("source_id", "unknown"),
                "synthetic": True,
                "document_id": r.get("document_id"),
                "source_document_id": r.get("source_document_id"),
                "source_sha256": r.get("source_sha256"),
                "task_type": r.get("task_type"),
                "language": r.get("language"),
            }
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            counts[domain] += 1

    required = ("general", "science")
    missing = [d for d in required if counts[d] == 0]
    if missing:
        raise SystemExit("Integrated admitted corpus lacks required training domains: " + ", ".join(missing))

    result = {
        "schema": "minironin-integrated-training-corpus-v1",
        "training_records": sum(counts.values()),
        "admitted_source_documents": len(train_docs),
        "awake_training_rows": len(awake_rows),
        "records_by_domain": dict(sorted(counts.items())),
        "source_documents_by_source": dict(sorted(source_counts.items())),
        "validation_awake_rows_excluded_from_training": awake["validation"],
        "canonical_validation_documents_excluded_from_training": library["validation_split"],
        "rag_index": {
            "path": "rag/minironin-rag.sqlite",
            "sha256": sha256(db_path),
            "chunks_unique": chunks,
            "holdout_read": False,
            "training_performed": False,
            "sources": db_manifest.get("sources", []),
        },
        "tokenizer_candidate": {
            "path": "tokenizer/backdoor-bpe.json",
            "sha256": tokenizer.get("sha256"),
            "active_vocab_candidate": tokenizer["active_vocab"],
            "eos_id": tokenizer["eos_id"],
            "activated": False,
            "reason": "810k parent checkpoint is UTF-8 byte tokenizer + EOS, active vocabulary 257; BPE requires a separately validated migration",
        },
        "parent_compatible_tokenizer": "UTF-8 bytes + EOS (active vocabulary 257)",
        "holdout_read": False,
        "training_performed": False,
        "source_integrated_manifest": manifest,
    }
    report_path = args.output.with_name("integrated-training-manifest.json")
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "source_integrated_manifest"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
