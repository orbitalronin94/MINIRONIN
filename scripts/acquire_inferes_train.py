#!/usr/bin/env python3
"""Acquire the Spanish InferES training split with auditable provenance."""
from __future__ import annotations
import argparse, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path

REPO_ID = "venelin/inferes"
LICENSE = "CC BY 4.0"
SOURCE_URL = "https://huggingface.co/datasets/venelin/inferes"
PAPER_URL = "https://arxiv.org/abs/2210.03068"

def norm_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())

def pick(row: dict, *names: str):
    by_key = {norm_key(str(k)): v for k, v in row.items()}
    for name in names:
        if norm_key(name) in by_key:
            return by_key[norm_key(name)]
    raise ValueError(f"missing required field; expected one of {names}; got {list(row)}")

def label_text(value, feature):
    original = value
    if isinstance(value, int) and hasattr(feature, "names"):
        value = feature.names[value]
    raw = str(value).strip().casefold()
    mapping = {
        "cnt": ("contradicción", "contradiction"),
        "contradiction": ("contradicción", "contradiction"),
        "contradictory": ("contradicción", "contradiction"),
        "ent": ("implicación", "entailment"),
        "entailment": ("implicación", "entailment"),
        "neutral": ("neutralidad", "neutral"),
        "neu": ("neutralidad", "neutral"),
    }
    if raw not in mapping:
        raise ValueError(f"unexpected InferES label: {original!r}")
    return mapping[raw]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--revision", required=True)
    ap.add_argument("--output-dir", type=Path, default=Path("data/curated/accepted"))
    args = ap.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.revision):
        raise SystemExit("revision must be a full 40-character commit SHA")
    from datasets import load_dataset
    from huggingface_hub import HfApi
    info = HfApi().dataset_info(REPO_ID, revision=args.revision)
    card = info.card_data
    declared_license = getattr(card, "license", None) if card else None
    if str(declared_license).casefold() not in {"cc-by-4.0", "cc_by_4_0"}:
        raise SystemExit(f"license mismatch: expected cc-by-4.0, found {declared_license!r}")
    dataset = load_dataset(REPO_ID, split="train", revision=args.revision)
    if len(dataset) < 6000:
        raise SystemExit(f"unexpectedly small train split: {len(dataset)}")
    label_feature = next((v for k,v in dataset.features.items() if norm_key(k)=="label"), None)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    out = args.output_dir / "inferes-train.jsonl"
    seen_ids, seen_rows, counts = set(), set(), {}
    digest = hashlib.sha256()
    written = 0
    with out.open("w", encoding="utf-8", newline="\n") as stream:
        for index, row in enumerate(dataset):
            premise = str(pick(row, "Premise", "premise")).strip()
            hypothesis = str(pick(row, "Hypothesis", "hypothesis")).strip()
            raw_label = pick(row, "Label", "label")
            label_es, label_en = label_text(raw_label, label_feature)
            source_id = str(pick(row, "ID", "id", "index", "Index"))
            if not premise or not hypothesis:
                raise ValueError(f"empty premise/hypothesis at row {index}")
            if source_id in seen_ids:
                raise ValueError(f"duplicate source ID: {source_id}")
            seen_ids.add(source_id)
            key = hashlib.sha256((premise+"\n"+hypothesis+"\n"+label_en).encode("utf-8")).hexdigest()
            if key in seen_rows:
                raise ValueError(f"duplicate example at row {index}")
            seen_rows.add(key)
            counts[label_en] = counts.get(label_en, 0) + 1
            question = ("Determina la relación lógica entre la premisa y la hipótesis.\n"
                        f"Premisa: {premise}\nHipótesis: {hypothesis}")
            answer = f"La relación es {label_es}. " + {
                "contradiction":"La hipótesis contradice la información de la premisa.",
                "entailment":"La hipótesis se deriva de la información de la premisa.",
                "neutral":"La premisa no permite confirmar ni negar la hipótesis.",
            }[label_en]
            record = {
                "id": f"inferes:{source_id}", "question": question, "answer": answer,
                "domain": "razonamiento lógico", "language": "es", "split": "train",
                "train_eligible": True, "admission_status": "accepted", "synthetic": False,
                "license": LICENSE, "source_dataset": "InferES", "source": SOURCE_URL,
                "source_revision": args.revision, "paper": PAPER_URL,
                "original_label": str(raw_label), "original_source_id": source_id,
                "topic": row.get("Topic", row.get("topic")),
                "annotation_type": row.get("Anno Type", row.get("anno_type")),
                "attribution": "InferES corpus; native Spanish annotators; see cited paper and dataset card.",
            }
            line = json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
            stream.write(line); digest.update(line.encode("utf-8")); written += 1
    if written != len(dataset):
        raise SystemExit(f"row count mismatch: wrote {written}, expected {len(dataset)}")
    manifest = {
        "schema_version": 1, "dataset": "InferES Spanish Natural Language Inference — train split",
        "source_dataset": REPO_ID, "source_url": SOURCE_URL, "paper_url": PAPER_URL,
        "source_revision": args.revision, "source_split": "train", "excluded_splits": ["test"],
        "license": LICENSE, "language": "es", "domain": "razonamiento lógico / inferencia textual",
        "record_count": written, "unique_source_ids": len(seen_ids), "unique_examples": len(seen_rows),
        "label_counts": counts, "file": out.name, "sha256_jsonl": digest.hexdigest(),
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "admission_status": "accepted for training; test split deliberately excluded",
        "limitations": [
            "Natural-language-inference benchmark, not a general factual knowledge base.",
            "Source examples include Wikipedia-derived text and generated/rephrased material as described by the dataset card.",
            "Labels are corpus annotations; they do not independently establish real-world facts.",
            "The original benchmark test split is not included in training."
        ]
    }
    (args.output_dir/"inferes-train.manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k:manifest[k] for k in ("record_count","unique_source_ids","unique_examples",
          "label_counts","license","source_revision","sha256_jsonl","admission_status")}, ensure_ascii=False))

if __name__ == "__main__":
    main()
