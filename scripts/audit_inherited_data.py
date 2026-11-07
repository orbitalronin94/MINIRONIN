#!/usr/bin/env python3
"""Audit the imported owner-authored Papers corpus and emit SHA-256 manifest."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path("data/inherited/papers")
EXPECTED = 9

def main() -> int:
    files = sorted(p for p in ROOT.glob("*.md") if p.is_file())
    if len(files) != EXPECTED:
        raise SystemExit(f"expected {EXPECTED} markdown files, found {len(files)}")
    seen = {}
    records = []
    for path in files:
        raw = path.read_bytes()
        if not raw:
            raise SystemExit(f"empty document: {path}")
        text = raw.decode("utf-8", errors="strict")
        normalized = text.replace("\r\n", "\n").strip()
        if not normalized:
            raise SystemExit(f"blank document: {path}")
        digest = hashlib.sha256(raw).hexdigest()
        if digest in seen:
            raise SystemExit(f"duplicate payload: {path} == {seen[digest]}")
        seen[digest] = str(path)
        records.append({
            "path": str(path),
            "bytes": len(raw),
            "sha256": digest,
            "characters": len(text),
            "lines": text.count("\n") + 1,
        })
    manifest = {
        "schema_version": 1,
        "source": "orbitalronin94/Papers",
        "source_revision": "d7bf3ae446f666ce3be73b11aab7090e1605a889",
        "admission_scope": "owner-authorized internal research/training only; no redistribution",
        "file_count": len(records),
        "total_bytes": sum(item["bytes"] for item in records),
        "files": records,
    }
    out = Path("data/manifests/papers-internal.sha256.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ("file_count", "total_bytes")}, indent=2))
    print(f"manifest: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
