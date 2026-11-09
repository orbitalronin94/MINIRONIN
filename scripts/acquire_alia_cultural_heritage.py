#!/usr/bin/env python3
"""Stream and admit ALIA Spanish cultural-heritage records with exact dedup."""
from __future__ import annotations
import argparse, hashlib, json, re, unicodedata
from datetime import datetime, timezone
from pathlib import Path

REPO_ID="SINAI/ALIA-es-cultural-heritage"
SOURCE_URL="https://huggingface.co/datasets/SINAI/ALIA-es-cultural-heritage"
LICENSE="CC BY-SA 4.0"

def norm(text):
    text=unicodedata.normalize("NFKC",text).casefold()
    return re.sub(r"\s+"," ",text).strip()

def digest(text):
    return hashlib.sha256(norm(text).encode("utf-8")).hexdigest()

def existing_hashes(root):
    hashes=set()
    excluded={".git","holdout","benchmarks","validation","test","quarantine","candidate","artifacts","checkpoints"}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md",".txt",".jsonl"}: continue
        if any(part.casefold() in excluded for part in path.parts): continue
        if path.name.casefold()=="readme.md": continue
        try:
            if path.suffix.lower()==".jsonl":
                with path.open(encoding="utf-8") as f:
                    for line in f:
                        try: row=json.loads(line)
                        except Exception: continue
                        for key in ("text","content","body","answer"):
                            value=row.get(key)
                            if isinstance(value,str) and len(value.strip())>=200: hashes.add(digest(value))
            else:
                value=path.read_text(encoding="utf-8")
                if len(value.strip())>=200: hashes.add(digest(value))
        except (UnicodeError,OSError): continue
    return hashes

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--revision",required=True)
    ap.add_argument("--output-dir",type=Path,default=Path("data/curated/accepted"))
    ap.add_argument("--root",type=Path,default=Path("."))
    args=ap.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}",args.revision): raise SystemExit("revision must be full HF commit SHA")
    from datasets import load_dataset
    from huggingface_hub import HfApi
    info=HfApi().dataset_info(REPO_ID,revision=args.revision)
    card=info.card_data
    license_value=getattr(card,"license",None) if card else None
    if str(license_value).casefold().replace("_","-") not in {"cc-by-sa-4.0","cc-by-sa"}:
        raise SystemExit(f"license mismatch: {license_value!r}")
    existing=existing_hashes(args.root)
    ds=load_dataset(REPO_ID,split="train",revision=args.revision,streaming=True)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    out=args.output_dir/"alia-es-cultural-heritage-train.jsonl"
    seen=set(); counts={}; skipped_wikipedia=0; skipped_duplicate=0; skipped_short=0; written=0
    digest_file=hashlib.sha256()
    with out.open("w",encoding="utf-8",newline="\n") as f:
        for row in ds:
            text=row.get("text")
            sid=str(row.get("source_id","")).strip()
            rid=str(row.get("id","")).strip()
            if not isinstance(text,str) or len(text.strip())<200:
                skipped_short+=1; continue
            # The corpus includes 92k+ Wikipedia culture articles; MINIRONIN
            # already has a dedicated Spanish Wikipedia 100k release.
            if sid.casefold().startswith("wikipedia"):
                skipped_wikipedia+=1; continue
            h=digest(text)
            if h in seen or h in existing:
                skipped_duplicate+=1; continue
            seen.add(h); counts[sid]=counts.get(sid,0)+1
            record={
                "id":f"alia-es:{sid}:{rid or h[:16]}",
                "text":text,
                "domain":"patrimonio cultural e historia",
                "language":"es",
                "split":"train",
                "train_eligible":True,
                "admission_status":"accepted",
                "synthetic":False,
                "license":LICENSE,
                "source_dataset":REPO_ID,
                "source":SOURCE_URL,
                "source_revision":args.revision,
                "source_id":sid,
                "original_source_id":rid,
                "attribution":"SINAI Research Group, ALIA Spanish Cultural and Heritage Corpus (2026), CC BY-SA 4.0. Upstream source_id preserved; see dataset card for source collection and attribution.",
            }
            line=json.dumps(record,ensure_ascii=False,separators=(",",":"))+"\n"
            f.write(line); digest_file.update(line.encode("utf-8")); written+=1
    if written==0: raise SystemExit("no eligible non-Wikipedia records survived exact deduplication")
    manifest={
        "schema_version":1,"dataset":REPO_ID,"source_url":SOURCE_URL,
        "source_revision":args.revision,"source_split":"train","license":LICENSE,
        "language":"es","domain":"patrimonio cultural e historia",
        "source_rows_reported_upstream":236314,"rows_admitted":written,
        "rows_skipped_wikipedia":skipped_wikipedia,"rows_skipped_exact_duplicates":skipped_duplicate,
        "rows_skipped_short_or_invalid":skipped_short,"unique_text_hashes":len(seen),
        "source_id_counts":counts,"file":out.name,"sha256_jsonl":digest_file.hexdigest(),
        "retrieved_at_utc":datetime.now(timezone.utc).isoformat(),
        "deduplication":"NFKC + casefold + whitespace normalization; SHA-256 within batch and against repository .md/.txt/.jsonl train corpus",
        "exclusions":["Wikipedia_Cultura_España and all source_id values starting Wikipedia; dedicated Wikipedia ES corpus already exists","holdout/validation/test/benchmark paths excluded from dedup reference scan and never imported"],
        "limitations":[
            "Upstream dataset contains 236,314 records and 939,315,404 tokens across 100 sources; admitted count is measured after exclusions and exact dedup.",
            "Only source_id is available per record; retain upstream dataset-level CC BY-SA 4.0 and source collection attribution.",
            "CC BY-SA 4.0 attribution and share-alike obligations must be preserved.",
            "The corpus is cultural-heritage oriented and source mix is uneven; inspect per-source counts before deciding training mixture."
        ]
    }
    (args.output_dir/"alia-es-cultural-heritage-train.manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:manifest[k] for k in ("rows_admitted","rows_skipped_wikipedia","rows_skipped_exact_duplicates","rows_skipped_short_or_invalid","source_id_counts","sha256_jsonl")},ensure_ascii=False))
if __name__=="__main__": main()
