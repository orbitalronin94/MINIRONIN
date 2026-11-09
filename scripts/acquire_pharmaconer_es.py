#!/usr/bin/env python3
"""Import the complete expert-annotated PharmaCoNER Spanish train split."""
from __future__ import annotations
import argparse, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path

REPO_ID = "PlanTL-GOB-ES/pharmaconer"
SOURCE_URL = "https://huggingface.co/datasets/PlanTL-GOB-ES/pharmaconer"
LICENSE = "CC BY 4.0"
TRAIN_FILE = "train-set_1.1.conll"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, default=Path("data/curated/accepted"))
    args = ap.parse_args()
    from huggingface_hub import HfApi, hf_hub_download
    info = HfApi().dataset_info(REPO_ID)
    revision = info.sha
    if not re.fullmatch(r"[0-9a-f]{40}", revision or ""):
        raise SystemExit("Could not resolve immutable PharmaCoNER revision")
    card = info.card_data
    license_value = getattr(card, "license", None) if card else None
    if str(license_value).casefold().replace("_", "-") != "cc-by-4.0":
        raise SystemExit(f"License mismatch: {license_value!r}")
    source = Path(hf_hub_download(repo_id=REPO_ID, filename=TRAIN_FILE, repo_type="dataset", revision=revision))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    out = args.output_dir / "pharmaconer-es-train.jsonl"
    digest = hashlib.sha256()
    rows = []
    tokens, tags, document_ids = [], [], []
    scanned_lines = 0
    def flush():
        if not tokens:
            return
        text = " ".join(tokens).strip()
        annotations = [{"token": token, "tag": tag} for token, tag in zip(tokens, tags) if tag != "O"]
        rows.append({
            "id": f"pharmaconer:{len(rows)}",
            "text": text,
            "domain": "biomedicina clínica y farmacología",
            "language": "es",
            "split": "train",
            "train_eligible": True,
            "admission_status": "accepted",
            "synthetic": False,
            "license": LICENSE,
            "source_dataset": REPO_ID,
            "source": SOURCE_URL,
            "source_revision": revision,
            "source_document_ids": sorted(set(document_ids)),
            "ner_annotations": annotations,
            "task": "Spanish clinical named-entity recognition",
            "attribution": "Gonzalez-Agirre et al. (2019), PharmaCoNER; PlanTL-GOB-ES / BSC TeMU; CC BY 4.0."
        })
        tokens.clear(); tags.clear(); document_ids.clear()
    with source.open(encoding="utf-8") as stream:
        for line in stream:
            scanned_lines += 1
            line = line.rstrip("\r\n")
            if not line:
                flush()
                continue
            parts = line.split("\t")
            if len(parts) != 4:
                raise SystemExit(f"Malformed CoNLL row at line {scanned_lines}: {line!r}")
            token, document_id, _span, tag = parts
            if not token or not tag:
                raise SystemExit(f"Empty token/tag at line {scanned_lines}")
            tokens.append(token); tags.append(tag); document_ids.append(document_id)
    flush()
    if len(rows) < 7000:
        raise SystemExit(f"Unexpectedly small PharmaCoNER train split: {len(rows)} sentences")
    with out.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            line = json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
            stream.write(line); digest.update(line.encode("utf-8"))
    manifest = {
        "schema_version": 1, "dataset": "PharmaCoNER Spanish clinical NER train",
        "source_dataset": REPO_ID, "source": SOURCE_URL, "source_revision": revision,
        "source_file": TRAIN_FILE, "license": LICENSE, "language": "es", "source_split": "train",
        "rows_scanned": scanned_lines, "rows_admitted": len(rows),
        "source_clinical_cases": 500, "entity_types": ["NORMALIZABLES", "NO_NORMALIZABLES", "PROTEINAS", "UNCLEAR"],
        "file": out.name, "sha256_jsonl": digest.hexdigest(),
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "admission_policy": "Complete upstream train split only; preserve all tokens and expert BIO tags; no dev/test records imported."
    }
    (args.output_dir / "pharmaconer-es-train.manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ("source_revision", "rows_admitted", "source_clinical_cases", "entity_types", "license", "sha256_jsonl")}, ensure_ascii=False))

if __name__ == "__main__":
    main()
