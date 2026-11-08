#!/usr/bin/env python3
"""Validate grounded MINIRONIN identity and GitHub Actions engineering corpora."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "identity": (ROOT / "data/curated/minironin-identity-v1.jsonl", 40),
    "engineering_recent": (ROOT / "data/curated/minironin-engineering-v1.jsonl", 20),
    "engineering_performance": (ROOT / "data/curated/minironin-performance-engineering-v1.jsonl", 4),
    "engineering_legacy": (ROOT / "data/curated/engineering-lessons-v1.jsonl", 50),
}
SECRET_PATTERNS = (
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|password)\s*[:=]\s*['\"]?[^\s'\"<>]{12,}"),
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    report = {"schema_version": 1, "datasets": {}, "valid": True}
    for name, (path, expected) in FILES.items():
        if not path.is_file():
            raise SystemExit(f"Missing dataset: {path}")
        rows = []
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            rows.append(row)
        if len(rows) != expected:
            raise SystemExit(f"{name}: expected {expected} rows, found {len(rows)}")
        ids = [str(row.get("id", "")) for row in rows]
        if any(not value for value in ids) or len(ids) != len(set(ids)):
            raise SystemExit(f"{name}: missing or duplicate IDs")
        questions = [str(row.get("question", row.get("instruccion", ""))).strip() for row in rows]
        answers = [str(row.get("answer", row.get("respuesta", ""))).strip() for row in rows]
        contexts = [str(row.get("context", row.get("evidencia", ""))).strip() for row in rows]
        if any(not q or not a or not c for q, a, c in zip(questions, answers, contexts)):
            raise SystemExit(f"{name}: empty question, answer, or context/evidence")
        if len(questions) != len(set(questions)):
            raise SystemExit(f"{name}: duplicate questions")
        content = path.read_bytes()
        text = content.decode("utf-8")
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            raise SystemExit(f"{name}: possible secret or credential pattern")
        report["datasets"][name] = {
            "path": str(path.relative_to(ROOT)),
            "records": len(rows),
            "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
            "unique_ids": len(set(ids)),
            "unique_questions": len(set(questions)),
        }

    identity_text = FILES["identity"][0].read_text(encoding="utf-8")
    for required in ("MINIRONIN", "49.083.392", "mamba-selective-scan-v1", "390k"):
        if required not in identity_text:
            raise SystemExit(f"Identity dataset missing canonical fact: {required}")
    engineering_rows = [
        json.loads(line)
        for line in FILES["engineering_recent"][0].read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    run_ids = {str(row.get("run_id")) for row in engineering_rows}
    if not {"42475009211", "42472836694", "42473906951", "42475009157"}.issubset(run_ids):
        raise SystemExit("Engineering dataset is missing one or more verified Actions runs")

    performance_rows = [
        json.loads(line)
        for line in FILES["engineering_performance"][0].read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(performance_rows) != 4:
        raise SystemExit("Performance engineering dataset must contain exactly four benchmark records")
    for row in performance_rows:
        if row.get("runner_class") != "github-hosted-standard-free":
            raise SystemExit("Every performance record must identify a free standard GitHub-hosted runner")
        if not row.get("run_id") or not row.get("job_id") or not row.get("source_repository"):
            raise SystemExit("Performance record is missing Actions provenance")
        if not row.get("architecture") or not row.get("question") or not row.get("answer"):
            raise SystemExit("Performance record is missing architecture or training example fields")
        if float(row.get("elapsed_seconds", 0)) <= 0 or float(row.get("tokens_per_second", 0)) <= 0:
            raise SystemExit("Performance record has invalid elapsed time or throughput")

    seed = (ROOT / "scripts/train_seed_tournament.py").read_text(encoding="utf-8")
    trainer = (ROOT / "scripts/train_long_run.py").read_text(encoding="utf-8")
    if '"identity": 0.02' not in seed or '"engineering": 0.02' not in seed:
        raise SystemExit("Identity/engineering domains are not assigned explicit training weights")
    for required in ("minironin-identity-v1.jsonl", "engineering-lessons-v1.jsonl", "minironin-engineering-v1.jsonl", "minironin-performance-engineering-v1.jsonl"):
        if required not in trainer:
            raise SystemExit(f"Training loader does not include {required}")
    report["totals"] = {
        "identity_records": 40,
        "engineering_records": 74,
        "engineering_performance_records": 4,
        "curated_identity_and_engineering_records": 114,
        "engineering_sources": sorted(run_ids),
    }
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
