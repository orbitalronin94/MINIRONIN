#!/usr/bin/env python3
"""Import the complete Spanish WikiCAT_esv2 train split with source metadata."""
from __future__ import annotations
import argparse, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path

REPO_ID = "PlanTL-GOB-ES/WikiCAT_esv2"
SOURCE_URL = "https://huggingface.co/datasets/PlanTL-GOB-ES/WikiCAT_esv2"
LICENSE = "CC BY-SA 3.0"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, default=Path("data/curated/accepted"))
    args = ap.parse_args()
    from datasets import load_dataset
    from huggingface_hub import HfApi
    info = HfApi().dataset_info(REPO_ID)
    revision = info.sha
    if not re.fullmatch(r"[0-9a-f]{40}", revision or ""):
        raise SystemExit("Could not resolve immutable WikiCAT revision")
    card = info.card_data
    license_value = getattr(card, "license", None) if card else None
    if str(license_value).casefold().replace("_", "-") != "cc-by-sa-3.0":
        raise SystemExit(f"License mismatch: {license_value!r}")
    ds = load_dataset(REPO_ID, split="train", revision=revision)
    feature = ds.features.get("label")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    out = args.output_dir / "wikicat-esv2-train.jsonl"
    digest = hashlib.sha256()
    seen = set()
    scanned = admitted = duplicates = short = 0
    with out.open("w", encoding="utf-8", newline="\\n") as stream:
        for index, row in enumerate(ds):
            scanned += 1
            text = row.get("text")
            if not isinstance(text, str) or len(text.strip()) < 80:
                short += 1
                continue
            raw_label = row.get("label")
            if isinstance(raw_label, int) and feature is not None and hasattr(feature, "names"):
                label = feature.names[raw_label]
            else:
                label = str(raw_label)
            key = hashlib.sha256(re.sub(r"\\s+", " ", text).strip().casefold().encode("utf-8")).hexdigest()
            if key in seen:
                duplicates += 1
                continue
            seen.add(key)
            record = {
                "id": f"wikicat-esv2:{index}:{key[:16]}",
                "text": text.strip(),
                "domain": "conocimiento enciclopédico y clasificación temática",
                "language": "es",
                "split": "train",
                "train_eligible": True,
                "admission_status": "accepted",
                "synthetic": False,
                "license": LICENSE,
                "source_dataset": REPO_ID,
                "source": SOURCE_URL,
                "source_revision": revision,
                "source_row": index,
                "label": label,
                "attribution": "Plan de Tecnologías del Lenguaje — Gobierno de España, WikiCAT_esv2; CC BY-SA 3.0."
            }
            line = json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\\n"
            stream.write(line)
            digest.update(line.encode("utf-8"))
            admitted += 1
    if scanned < 1000 or admitted < 1000:
        raise SystemExit(f"Unexpectedly small WikiCAT train split: scanned={scanned}, admitted={admitted}")
    manifest = {
        "schema_version": 1, "dataset": "WikiCAT_esv2 Spanish train",
        "source_dataset": REPO_ID, "source": SOURCE_URL, "source_revision": revision,
        "license": LICENSE, "language": "es", "source_split": "train",
        "source_rows_scanned": scanned, "rows_admitted": admitted,
        "rows_skipped_exact_duplicates": duplicates, "rows_skipped_short": short,
        "file": out.name, "sha256_jsonl": digest.hexdigest(),
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "admission_policy": "Complete upstream train split; minimal schema, language, text-length and exact-dedup checks; source labels and provenance retained."
    }
    (args.output_dir / "wikicat-esv2-train.manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ("source_revision", "source_rows_scanned", "rows_admitted", "rows_skipped_exact_duplicates", "license", "sha256_jsonl")}, ensure_ascii=False))

if __name__ == "__main__":
    main()
