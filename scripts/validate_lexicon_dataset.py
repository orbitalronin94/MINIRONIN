#!/usr/bin/env python3
"""Validate Lexicon-derived MINIRONIN training data and source provenance."""
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
manifest_path = ROOT / "data/curated/lexicon-50k-manifest.json"
m = json.loads(manifest_path.read_text(encoding="utf-8"))
source = ROOT / m["source"]
dataset = ROOT / m["file"]
assert source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest() == m["source_sha256"]
raw = dataset.read_bytes()
assert len(raw) == m["bytes"] and hashlib.sha256(raw).hexdigest() == m["sha256"]
rows = [json.loads(line) for line in raw.decode("utf-8").splitlines()]
assert len(rows) == m["records"] == 50_000
assert len({r["id"] for r in rows}) == 50_000
assert len({r["question"] for r in rows}) == 50_000
assert m["parsed_lexicon_entries"] >= 150
assert set(r["tag"] for r in rows) == {
    "lexicon_behavioral_diagnosis", "lexicon_remediation",
    "lexicon_proportionality_and_precision"
}
assert all(r["source_epithet"] and r["source_section"] and r["context"] and r["answer"] for r in rows)
assert all(r["license"] == "author-authorized-for-training" for r in rows)
assert all(1 <= r["severity"] <= 6 for r in rows)
print("PASS: 50,000 Lexicon-derived examples; source and dataset SHA-256 verified.")
