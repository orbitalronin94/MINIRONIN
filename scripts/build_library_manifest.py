#!/usr/bin/env python3
"""Validate an explicit admission ledger and materialize one canonical document inventory."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import gzip
from pathlib import Path

EXCLUDED_PARTS = {
    ".git", ".github", "holdout", "validation", "eval", "evaluation",
    "benchmark", "benchmarks", "answer_keys", "private", "secrets",
    "credentials", "checkpoints", "checkpoint", "optimizer", "logs",
    "quarantine", "candidates", "reviews", "tests", "test",
}
EXCLUDED_SUFFIXES = {
    ".pt", ".pth", ".bin", ".safetensors", ".onnx", ".gguf", ".sqlite",
    ".db", ".zip", ".7z", ".tar", ".pem", ".key",
}
ALLOWED_RIGHTS = {
    "approved_for_spain_training", "owner_authored_internal",
    "approved_internal_research", "approved_public_domain",
    "approved_open_license",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_record(value, depth=0) -> str:
    if depth > 5:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return "\n".join(filter(None, (extract_record(item, depth + 1) for item in value)))
    if isinstance(value, dict):
        preferred = (
            "text", "content", "body", "document", "passage", "abstract",
            "question", "instruccion", "instruction", "answer", "respuesta",
            "response", "completion", "solution", "evidence", "evidencia",
            "context", "title", "summary", "description", "explanation",
            "prompt", "input", "output", "messages",
        )
        parts = []
        for key in preferred:
            if key in value:
                extracted = extract_record(value[key], depth + 1)
                if extracted:
                    parts.append(f"{key}: {extracted}")
        if parts:
            return "\n".join(parts)
        ignored = {"id", "url", "source", "source_file", "license", "metadata",
                   "author", "date", "timestamp", "path", "filename", "sha256",
                   "run_id", "job_id", "rights_status"}
        return "\n".join(
            f"{key}: {item}" for key, item in value.items()
            if key.lower() not in ignored and isinstance(item, (str, int, float))
        )
    return ""


def read_text(path: Path) -> str:
    if path.name.lower().endswith((".jsonl.gz", ".txt.gz")):
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as stream:
            raw = stream.read()
    else:
        raw = path.read_text(encoding="utf-8", errors="replace")
    suffix = path.suffix.lower()
    if path.name.lower().endswith((".jsonl.gz", ".jsonl", ".ndjson")):
        rows = []
        for line in raw.splitlines():
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            text = extract_record(item)
            if text:
                rows.append(text)
        return "\n\n".join(rows)
    if suffix == ".json":
        item = json.loads(raw)
        values = item if isinstance(item, list) else [item]
        return "\n\n".join(filter(None, (extract_record(value) for value in values)))
    if suffix in {".md", ".txt", ".rst", ".xml", ".html", ".htm", ".yaml", ".yml", ".csv", ".tsv"} or path.name.lower().endswith(".txt.gz"):
        return raw
    raise ValueError(f"Unsupported admitted document format: {path.suffix}")


def iter_source_records(path: Path):
    """Yield independent JSONL/JSON records so a whole corpus file is not one giant document."""
    name = path.name.lower()
    if name.endswith((".jsonl.gz", ".ndjson.gz")) or path.suffix.lower() in {".jsonl", ".ndjson"}:
        opener = gzip.open if name.endswith(".gz") else open
        with opener(path, "rt", encoding="utf-8", errors="replace") as stream:
            for index, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                text = extract_record(item)
                if text:
                    yield index, text, item, sha256(line.encode("utf-8"))
        return
    if path.suffix.lower() == ".json":
        item = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        values = item if isinstance(item, list) else [item]
        for index, value in enumerate(values, 1):
            text = extract_record(value)
            if text:
                raw = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
                yield index, text, value, sha256(raw)
        return
    if name.endswith(".txt.gz"):
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as stream:
            text = stream.read()
    else:
        text = path.read_text(encoding="utf-8", errors="replace")
    if text.strip():
        yield 1, text, None, sha256(text.encode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--admissions", type=Path, required=True,
                        help="Curator-owned JSONL ledger; directories are never auto-admitted")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-file-mb", type=int, default=64)
    args = parser.parse_args()
    root = args.root.resolve()
    ledger_bytes = args.admissions.read_bytes()
    ledger_sha = sha256(ledger_bytes)
    rows = []
    seen = {}
    rejected = []
    for line_no, line in enumerate(ledger_bytes.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        path_text = str(row.get("path", "")).strip()
        if not path_text or Path(path_text).is_absolute():
            raise SystemExit(f"admissions:{line_no}: path must be relative")
        path = (root / path_text).resolve()
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            raise SystemExit(f"admissions:{line_no}: path escapes root")
        parts = {part.lower() for part in Path(rel).parts}
        if parts & EXCLUDED_PARTS or re.search(r"(^|[._-])(holdout|validation|eval|benchmark|answer_key)([._-]|$)", path.name.lower()):
            rejected.append({"path": rel, "reason": "excluded_path"})
            continue
        if path.suffix.lower() in EXCLUDED_SUFFIXES or not path.is_file():
            rejected.append({"path": rel, "reason": "unsupported_or_missing"})
            continue
        if path.stat().st_size > args.max_file_mb * 1024 * 1024:
            rejected.append({"path": rel, "reason": "file_too_large"})
            continue
        if row.get("admission_status") != "admitted":
            rejected.append({"path": rel, "reason": "not_admitted"})
            continue
        rights = str(row.get("rights_status", "")).strip()
        if rights not in ALLOWED_RIGHTS:
            rejected.append({"path": rel, "reason": "rights_not_approved", "rights_status": rights})
            continue
        if not row.get("license"):
            raise SystemExit(f"admissions:{line_no}: admitted row lacks license")
        if not isinstance(row.get("train_eligible"), bool) or not isinstance(row.get("retrieval_eligible"), bool):
            raise SystemExit(f"admissions:{line_no}: eligibility flags must be booleans")
        if not row["train_eligible"] and not row["retrieval_eligible"]:
            rejected.append({"path": rel, "reason": "no_eligible_projection"})
            continue
        raw = path.read_bytes()
        digest = sha256(raw)
        expected = row.get("sha256")
        if expected and expected != digest:
            raise SystemExit(f"admissions:{line_no}: SHA-256 mismatch for {rel}")
        document_id = str(row.get("document_id") or f"{row.get('source_id','source')}:{digest[:20]}")
        if document_id in seen and seen[document_id] != digest:
            raise SystemExit(f"admissions:{line_no}: document_id maps to different content")
        seen[document_id] = digest
        try:
            records = list(iter_source_records(path))
        except (UnicodeError, ValueError, json.JSONDecodeError) as exc:
            rejected.append({"path": rel, "reason": f"extract_error:{exc}"})
            continue
        if not records:
            rejected.append({"path": rel, "reason": "no_extractable_records"})
            continue
        for record_index, text, structured_record, record_sha in records:
            record_id = document_id if len(records) == 1 else f"{document_id}:record:{record_index}:{record_sha[:12]}"
            if record_id in seen:
                if seen[record_id] != record_sha:
                    raise SystemExit(f"admissions:{line_no}: document_id maps to different record content")
                continue
            seen[record_id] = record_sha
            materialized = {
                "document_id": record_id,
                "source_id": str(row.get("source_id", "unknown")),
                "project": str(row.get("project", "MINIRONIN")),
                "path": rel,
                "sha256": record_sha,
                "payload_sha256": digest,
                "record_index": record_index,
                "license": str(row["license"]),
                "rights_status": rights,
                "admission_status": "admitted",
                "train_eligible": row["train_eligible"],
                "retrieval_eligible": row["retrieval_eligible"],
                "redistribution": bool(row.get("redistribution", False)),
                "epistemic_type": str(row.get("epistemic_type", "source_specific")),
                "domain": str(row.get("domain", "general")),
                "language": str(row.get("language", "und")),
                "provenance_ref": str(row.get("provenance_ref", "")),
                "text": text,
                "text_sha256": sha256(text.encode("utf-8")),
            }
            if structured_record is not None:
                materialized["record"] = structured_record
            rows.append(materialized)
    rows.sort(key=lambda x: (x["source_id"], x["path"], x["document_id"]))
    # Guarantee a deterministic, non-empty validation split whenever >=2 train documents exist.
    eligible = [r for r in rows if r["train_eligible"]]
    ranked = sorted(eligible, key=lambda r: hashlib.sha256(r["document_id"].encode()).hexdigest())
    validation_count = max(1, round(len(ranked) * 0.10)) if len(ranked) >= 2 else 0
    validation_ids = {r["document_id"] for r in ranked[:validation_count]}
    for row in rows:
        row["split"] = "validation" if row["document_id"] in validation_ids else "train"
    args.output.mkdir(parents=True, exist_ok=True)
    documents_path = args.output / "documents.jsonl"
    with documents_path.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    manifest = {
        "schema": "minironin-canonical-library-v2",
        "admissions_sha256": ledger_sha,
        "documents_jsonl_sha256": sha256(documents_path.read_bytes()),
        "documents": len(rows),
        "train_eligible": sum(r["train_eligible"] for r in rows),
        "retrieval_eligible": sum(r["retrieval_eligible"] for r in rows),
        "train_split": sum(r["split"] == "train" for r in rows),
        "validation_split": sum(r["split"] == "validation" for r in rows),
        "sources": {s: sum(r["source_id"] == s for r in rows) for s in sorted({r["source_id"] for r in rows})},
        "languages": {s: sum(r["language"] == s for r in rows) for s in sorted({r["language"] for r in rows})},
        "rejected": rejected,
        "holdout_read": False,
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
