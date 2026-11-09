#!/usr/bin/env python3
"""Audit owner-authored Papers and recursively admitted open-library documents."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path("data/inherited/papers")
EXPECTED_OWNER_FILES = 9
CURATED_ROOT = ROOT / "curated"
WIKIMEDIA_ROOT = CURATED_ROOT / "wikimedia-es"
WIKISOURCE_ROOT = CURATED_ROOT / "wikimedia-wikisource"

def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def inspect(path: Path, seen: dict[str, str], curated: bool) -> dict:
    raw = path.read_bytes()
    if not raw:
        raise SystemExit(f"empty document: {path}")
    text = raw.decode("utf-8", errors="strict")
    normalized = text.replace("\r\n", "\n").strip()
    if not normalized:
        raise SystemExit(f"blank document: {path}")
    minimum = 250 if path.is_relative_to(WIKISOURCE_ROOT) else 800
    if curated and len(normalized) < minimum:
        raise SystemExit(f"curated document too short (<{minimum} chars): {path}")
    sha = digest(raw)
    if sha in seen:
        raise SystemExit(f"duplicate payload: {path} == {seen[sha]}")
    seen[sha] = str(path)
    record = {
        "path": str(path),
        "bytes": len(raw),
        "sha256": sha,
        "characters": len(text),
        "lines": text.count("\n") + 1,
        "collection": "curated-open-library" if curated else "owner-papers",
    }
    if path.is_relative_to(WIKIMEDIA_ROOT) or path.is_relative_to(WIKISOURCE_ROOT):
        required = (
            "Source URL:", "Page ID:", "Dataset revision:",
            "License:", "Wikimedia Foundation",
        )
        missing = [item for item in required if item not in normalized]
        if missing:
            raise SystemExit(f"missing Wikimedia provenance fields {missing}: {path}")
        if path.is_relative_to(WIKIMEDIA_ROOT) and "https://es.wikipedia.org/wiki/" not in normalized:
            raise SystemExit(f"missing canonical Wikipedia URL: {path}")
        if path.is_relative_to(WIKISOURCE_ROOT) and "wikisource.org/wiki/" not in normalized:
            raise SystemExit(f"missing canonical Wikisource URL: {path}")
    return record

def main() -> int:
    owner_files = sorted(p for p in ROOT.glob("*.md") if p.is_file() and p.name != "README.md")
    if len(owner_files) != EXPECTED_OWNER_FILES:
        raise SystemExit(f"expected {EXPECTED_OWNER_FILES} owner-authored markdown files, found {len(owner_files)}")
    curated_files = sorted(
        p for p in CURATED_ROOT.rglob("*.md")
        if p.is_file() and p.name.lower() != "readme.md"
    ) if CURATED_ROOT.exists() else []
    seen: dict[str, str] = {}
    records = []
    for path in owner_files:
        records.append(inspect(path, seen, curated=False))
    for path in curated_files:
        records.append(inspect(path, seen, curated=True))
    manifest = {
        "schema_version": 2,
        "source": "orbitalronin94/Papers plus provenance-preserving open-library curation",
        "source_revision": "d7bf3ae446f666ce3be73b11aab7090e1605a889",
        "admission_scope": "owner Papers are internal research/training only; open-library documents retain source attribution and source-specific license",
        "owner_file_count": len(owner_files),
        "curated_document_count": len(curated_files),
        "file_count": len(records),
        "total_bytes": sum(item["bytes"] for item in records),
        "files": records,
    }
    out = Path("data/manifests/papers-internal.sha256.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ("owner_file_count", "curated_document_count", "file_count", "total_bytes")}, indent=2))
    print(f"manifest: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
