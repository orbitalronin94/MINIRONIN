#!/usr/bin/env python3
"""Validate manually curated engineering lessons and emit a SHA-256 manifest."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

DATA = Path("data/curated/engineering-lessons-v1.jsonl")
REQUIRED = {
    "id", "tipo", "idioma", "dominio", "instruccion", "respuesta",
    "evidencia", "fuente", "run_id", "job_id", "confianza",
    "curacion", "uso",
}
ALLOWED_RUNS = {
    ("HERETIC-RONIN", "42370725970", "128398241561"),
    ("RONIN-IA", "42364138740", "128378601930"),
    ("RONIN-IA", "42364138740", "128378602072"),
    ("HERETIC-RONIN", "42355677701", "128353149782"),
    ("HERETIC-RONIN", "42355677701", "128354710674"),
    ("HERETIC-RONIN", "42355677701", "128354710613"),
    ("HERETIC-RONIN", "42355677701", "128354710611"),
    ("HERETIC-RONIN", "42355677701", "128354710699"),
    ("HERETIC-RONIN", "42355677701", "128354710653"),
}

def main() -> int:
    raw = DATA.read_bytes()
    text = raw.decode("utf-8", errors="strict")
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    if len(rows) < 1:
        raise SystemExit("curated dataset is empty")
    ids = set()
    for index, row in enumerate(rows, start=1):
        missing = REQUIRED - row.keys()
        if missing:
            raise SystemExit(f"row {index}: missing fields {sorted(missing)}")
        if row["id"] in ids:
            raise SystemExit(f"duplicate id: {row['id']}")
        ids.add(row["id"])
        for key in ("instruccion", "respuesta", "evidencia"):
            if not isinstance(row[key], str) or len(row[key].strip()) < 30:
                raise SystemExit(f"row {index}: insufficient {key}")
        if row["idioma"] != "es":
            raise SystemExit(f"row {index}: dataset must be Spanish")
        if row["confianza"] not in {"alta", "media"}:
            raise SystemExit(f"row {index}: invalid confidence")
        source = (row["fuente"], str(row["run_id"]), str(row["job_id"]))
        if source not in ALLOWED_RUNS:
            raise SystemExit(f"row {index}: unregistered source {source}")
        if row["curacion"] not in {
            "redactado_manual_desde_log",
            "redactado_manual_desde_manifiesto",
            "revision_manual_del_manifiesto_y_muestra",
            "parafrasis_manual_de_campo_del_manifiesto",
        }:
            raise SystemExit(f"row {index}: unknown curation method")
    manifest = {
        "schema_version": 1,
        "dataset": str(DATA),
        "language": "es",
        "curation": "manual",
        "record_count": len(rows),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "sources": [
            {"repository": "HERETIC-RONIN", "run_id": "42370725970",
             "job_id": "128398241561", "artifact_id": 13574129542},
            {"repository": "RONIN-IA", "run_id": "42364138740",
             "job_ids": ["128378601930", "128378602072"]},
        ],
        "limitations": [
            "Not raw logs",
            "Teacher-generated 200-row artifact excluded as unverified supervision",
            "Must pass global deduplication and holdout-contamination checks before training",
        ],
    }
    out = Path("data/manifests/engineering-lessons-v1.sha256.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
