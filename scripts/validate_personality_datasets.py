#!/usr/bin/env python3
"""Validate deterministic MINIRONIN persona datasets and their manifest."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "data" / "curated"
manifest = json.loads((root / "personality-50k-manifest.json").read_text(encoding="utf-8"))
assert len(manifest["datasets"]) == 4
seen = set()
for item in manifest["datasets"]:
    path = root.parent.parent / item["file"]
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(rows) == 50_000, (path, len(rows))
    assert len({row["id"] for row in rows}) == 50_000
    questions = {row["question"] for row in rows}
    assert len(questions) == 50_000
    assert not (seen & questions), "cross-dataset prompt collision: " + str(path)
    seen.update(questions)
    assert path.stat().st_size == item["bytes"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
    assert all(row.get("context") and row.get("question") and row.get("answer") for row in rows)
    expected = {
        "casuist": "fallacy_socratic_cynicism",
        "scientist": "known_science_with_exasperated_tone",
        "oracle": "everyday_oracular_pessimism",
        "indifference": "absurdist_indifference",
    }[item["kind"]]
    assert all(row["tag"] == expected for row in rows)
    if item["kind"] == "scientist":
        assert all(row.get("reference") for row in rows)
print("PASS: 200,000 persona records; 50k each, unique prompts, labels and SHA-256 verified.")
