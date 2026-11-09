#!/usr/bin/env python3
"""Audit external library artifacts already present in the repository.

This is a triage report, not an automatic admission mechanism. In particular,
unknown licences and weak provenance are never treated as permission to train.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = (
    "data/inherited",
    "data/books",
    "data/classics",
    "data/anarchist",
    "data/japan",
    "data/curated/sources",
    "data/sources",
)
EXTENSIONS = {".md", ".txt", ".json", ".jsonl", ".csv", ".tsv"}
SPANISH_MARKERS = {
    " de ", " la ", " que ", " el ", " en ", " y ", " los ", " del ",
    " se ", " las ", " por ", " con ", " una ", " para ", " como ",
    " es ", " un ", " al ", " no ", " más ", " su ", " pero ",
}
SOURCE_RE = re.compile(r"(https?://|wik[im]edia|wikisource|ple[ií]as|bne|boe|doi\.org|isbn|issn|fuente\s*:|source\s*:)", re.I)
LICENSE_RE = re.compile(r"(CC0|CC-BY(?:-SA)?|CC BY(?:-SA)?|public domain|dominio público|licen[cs]ia|copyright|all rights reserved|MIT License|Apache License)", re.I)
URL_RE = re.compile(r"https?://[^\s)>]+", re.I)


def read_text(path: Path) -> tuple[str, str | None]:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return "", "not_utf8"
    return text, None


def payload_text(path: Path, text: str) -> tuple[str, int, str | None]:
    if path.suffix.lower() not in {".json", ".jsonl"}:
        return text, max(1, len(text.splitlines())), None
    try:
        if path.suffix.lower() == ".jsonl":
            rows = []
            for number, line in enumerate(text.splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    return text, len(rows), f"invalid_jsonl_line_{number}:{exc.msg}"
            return "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows), len(rows), None
        value = json.loads(text)
        if isinstance(value, list):
            return "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in value), len(value), None
        return json.dumps(value, ensure_ascii=False, sort_keys=True), 1, None
    except json.JSONDecodeError as exc:
        return text, 0, f"invalid_json:{exc.msg}"


def spanish_score(text: str) -> tuple[int, float]:
    sample = " " + re.sub(r"\s+", " ", text.lower()) + " "
    hits = sum(sample.count(marker) for marker in SPANISH_MARKERS)
    words = max(1, len(re.findall(r"\b[\wáéíóúüñ]+\b", sample)))
    return hits, hits / words


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("external-library-audit.json"))
    args = parser.parse_args()

    paths: list[Path] = []
    for root in SCAN_ROOTS:
        directory = ROOT / root
        if directory.exists():
            paths.extend(p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSIONS)
    paths = sorted(set(paths))

    records = []
    hashes: dict[str, str] = {}
    for path in paths:
        rel = path.relative_to(ROOT).as_posix()
        text, read_error = read_text(path)
        if read_error:
            records.append({"path": rel, "status": "quarantine", "reason": read_error})
            continue
        content, count, parse_error = payload_text(path, text)
        normalized = re.sub(r"\s+", " ", content).strip().casefold()
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        duplicate_of = hashes.get(digest)
        if normalized:
            hashes.setdefault(digest, rel)

        source = bool(SOURCE_RE.search(text) or URL_RE.search(text))
        license_evidence = bool(LICENSE_RE.search(text))
        chars = len(content.strip())
        hits, score = spanish_score(content)
        reasons = []
        if parse_error:
            status = "quarantine"
            reasons.append(parse_error)
        elif duplicate_of:
            status = "duplicate_review"
            reasons.append("same_normalized_content_as:" + duplicate_of)
        else:
            if chars < 250:
                reasons.append("too_short_for_training_candidate")
            if not source:
                reasons.append("missing_explicit_source_provenance")
            if not license_evidence:
                reasons.append("licence_not_identified_in_file")
            if hits < 5 or score < 0.012:
                reasons.append("spanish_language_not_confirmed")
            if chars >= 250 and source and license_evidence and hits >= 5 and score >= 0.012:
                status = "candidate_for_manual_review"
                reasons.append("basic_checks_passed_not_auto_admitted")
            else:
                status = "needs_manual_review"

        records.append({
            "path": rel,
            "status": status,
            "sha256_normalized_text": digest,
            "bytes": path.stat().st_size,
            "characters": chars,
            "records_or_lines": count,
            "spanish_marker_hits": hits,
            "spanish_marker_ratio": round(score, 5),
            "source_evidence": source,
            "licence_evidence": license_evidence,
            "duplicate_of": duplicate_of,
            "reasons": reasons,
        })

    counts = Counter(item["status"] for item in records)
    report = {
        "schema_version": 1,
        "purpose": "triage_only_no_automatic_training_admission",
        "scan_roots": list(SCAN_ROOTS),
        "files_scanned": len(records),
        "status_counts": dict(sorted(counts.items())),
        "records": records,
        "policy": {
            "unknown_licence": "not_admitted_until_verified",
            "source_provenance": "required_for_admission",
            "language": "Spanish heuristic is only a triage signal; manual review required",
            "duplicates": "flagged, never silently merged",
            "holdout": "never read or modified by this audit",
        },
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"files_scanned": len(records), "status_counts": dict(counts), "report": str(output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
