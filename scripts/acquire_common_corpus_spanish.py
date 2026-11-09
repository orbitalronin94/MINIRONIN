#!/usr/bin/env python3
"""Filter one Common Corpus parquet shard to Spanish PD/CC0/CC-BY science & government."""
from __future__ import annotations
import argparse,gzip,hashlib,json,re,unicodedata
from datetime import datetime,timezone
from pathlib import Path
from huggingface_hub import hf_hub_download,HfApi
import pyarrow.parquet as pq
REPO="PleIAs/common_corpus"
SOURCE="https://huggingface.co/datasets/PleIAs/common_corpus"
LICENSES={"public domain","public-domain","pd","pdm","cc0","cc0 1.0","cc0-1.0","cc by 4.0","cc-by-4.0","cc-by","creative commons attribution 4.0"}
OPEN_TYPES={"openscience","opengovernment","opensemantic"}
def norm(s): return re.sub(r"\s+"," ",unicodedata.normalize("NFKC",s).casefold()).strip()
def htext(s): return hashlib.sha256(norm(s).encode("utf-8")).hexdigest()
def filehash(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()
def allowed_license(value):
    s=norm(str(value or "")).replace("_","-")
    return s in LICENSES or s.replace("-"," ") in LICENSES
def existing_hashes(root):
    excluded={".git","holdout","benchmarks","validation","test","quarantine","candidate","artifacts","checkpoints"}
    found=set()
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in {".md",".txt",".jsonl"}: continue
        if any(x.casefold() in excluded for x in p.parts) or p.name.casefold()=="readme.md": continue
        try:
            if p.suffix.lower()==".jsonl":
                with p.open(encoding="utf-8") as f:
                    for line in f:
                        try:r=json.loads(line)
                        except Exception:continue
                        for k in ("text","content","body","answer"):
                            v=r.get(k)
                            if isinstance(v,str) and len(v)>=300:found.add(htext(v))
            else:
                v=p.read_text(encoding="utf-8")
                if len(v)>=300:found.add(htext(v))
        except (OSError,UnicodeError):continue
    return found
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--shard",type=int,required=True)
    ap.add_argument("--revision",required=True)
    ap.add_argument("--root",type=Path,default=Path("."))
    ap.add_argument("--output-dir",type=Path,default=Path("out"))
    a=ap.parse_args()
    if not 1<=a.shard<=10:raise SystemExit("shard must be 1..10")
    if not re.fullmatch(r"[0-9a-f]{40}",a.revision):raise SystemExit("revision must be a full 40-char SHA")
    info=HfApi().dataset_info(REPO,revision=a.revision)
    if not info.card_data:raise SystemExit("missing Common Corpus dataset card")
    filename=f"common_corpus_1/subset_100_{a.shard}.parquet"
    local=Path(hf_hub_download(repo_id=REPO,filename=filename,repo_type="dataset",revision=a.revision))
    parquet=pq.ParquetFile(local); fields=parquet.schema.names
    required={"text","language","license"}
    if not required.issubset(set(fields)):raise SystemExit(f"missing columns {required-set(fields)}; fields={fields}")
    source_sha=filehash(local); seen=existing_hashes(a.root)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    out=a.output_dir/f"common-corpus-es-{a.shard:04d}.jsonl.gz"
    output_sha=hashlib.sha256()
    counts={};rows_seen=admitted=skip_lang=skip_domain=skip_license=skip_short=skip_dup=0
    with gzip.open(out,"wt",encoding="utf-8",newline="\n",compresslevel=6) as f:
        for batch in parquet.iter_batches(batch_size=64):
            for row in batch.to_pylist():
                rows_seen+=1
                lang=norm(str(row.get("language") or ""))
                if lang not in {"es","spa","spanish","español"}:skip_lang+=1;continue
                open_type=norm(str(row.get("open type") or row.get("open_type") or ""))
                if open_type not in OPEN_TYPES:skip_domain+=1;continue
                license_value=str(row.get("license") or "")
                if not allowed_license(license_value):skip_license+=1;continue
                text=row.get("text")
                if not isinstance(text,str) or len(text.strip())<500:skip_short+=1;continue
                digest=htext(text)
                if digest in seen:skip_dup+=1;continue
                seen.add(digest)
                collection=str(row.get("collection") or "")
                identifier=str(row.get("identifier") or "")
                record={
                    "id":f"common-corpus:{a.shard}:{identifier or digest[:20]}",
                    "text":text,"domain":open_type,"language":"es","split":"train",
                    "train_eligible":True,"admission_status":"accepted","synthetic":False,
                    "license":license_value,"source_dataset":REPO,"source":SOURCE,
                    "source_revision":a.revision,"source_file":filename,
                    "identifier":identifier,"collection":collection,"open_type":open_type,
                    "title":row.get("title"),"creator":row.get("creator"),"date":row.get("date"),
                    "word_count":row.get("word_count"),"token_count":row.get("token_count"),
                    "attribution":"PleIAs Common Corpus; per-document identifier, collection, open_type and license retained."
                }
                line=json.dumps(record,ensure_ascii=False,separators=(",",":"))+"\n"
                f.write(line);output_sha.update(line.encode("utf-8"));admitted+=1
                counts[collection]=counts.get(collection,0)+1
    manifest={
        "schema_version":1,"dataset":"PleIAs Common Corpus — Spanish open science/government/semantic",
        "source_dataset":REPO,"source_url":SOURCE,"source_revision":a.revision,
        "source_file":filename,"source_parquet_sha256":source_sha,"source_parquet_bytes":local.stat().st_size,
        "source_rows_scanned":rows_seen,"rows_admitted":admitted,"rows_skipped_non_spanish":skip_lang,
        "rows_skipped_other_open_type":skip_domain,"rows_skipped_unapproved_license":skip_license,
        "rows_skipped_short":skip_short,"rows_skipped_exact_duplicates":skip_dup,
        "allowed_open_types":sorted(OPEN_TYPES),"allowed_licenses":sorted(LICENSES),
        "collection_counts":counts,"license_policy":"Only Public Domain, PDM, CC0 and CC BY attribution-only variants. Excludes NC, ND, SA and unknown licenses.",
        "file":out.name,"sha256_jsonl_uncompressed":output_sha.hexdigest(),
        "retrieved_at_utc":datetime.now(timezone.utc).isoformat(),
        "limitations":[
            "Only Spanish records in OpenScience, OpenGovernment and OpenSemantic are selected; OpenCulture, OpenWeb and OpenSource are excluded to reduce overlap with existing libraries.",
            "Only row-level Public Domain, CC0 or CC BY attribution-only licenses are admitted; ShareAlike, NC, ND and unknown rights are excluded.",
            "Exact duplicates are filtered against repository training text and within this shard; cross-shard duplicates are reported by the unified builder."
        ]
    }
    (a.output_dir/f"common-corpus-es-{a.shard:04d}.manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:manifest[k] for k in ("source_file","source_rows_scanned","rows_admitted","rows_skipped_non_spanish","rows_skipped_other_open_type","rows_skipped_unapproved_license","rows_skipped_exact_duplicates","collection_counts")},ensure_ascii=False))
if __name__=="__main__":main()
