#!/usr/bin/env python3
"""Download one immutable Spanish-PD-Books parquet shard and curate JSONL."""
from __future__ import annotations
import argparse,gzip,hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
from huggingface_hub import hf_hub_download
import pyarrow.parquet as pq
REPO="PleIAs/Spanish-PD-Books"
REVISION="001eaf13681f483069361dd82195ce279e12ed63"
LICENSE="Public domain in all regions (per dataset card; EU term >70 years post mortem)"
SOURCE="https://huggingface.co/datasets/PleIAs/Spanish-PD-Books"
def key(x): return re.sub(r"[^a-z0-9]","",str(x).casefold())
def first(row,names):
 d={key(k):v for k,v in row.items()}
 for n in names:
  if key(n) in d:return d[key(n)]
 return None
def clean(v):
 if v is None:return ""
 if isinstance(v,str):return v.strip()
 return str(v).strip()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--shard",type=int,required=True);ap.add_argument("--output-dir",type=Path,default=Path("out"));a=ap.parse_args()
 if not 1<=a.shard<=129:raise SystemExit("shard must be between 1 and 129")
 name=f"spanish_pd_{a.shard}.parquet"
 path=Path(hf_hub_download(REPO,filename=name,revision=REVISION,repo_type="dataset"))
 parquet=pq.ParquetFile(path);fields=parquet.schema.names
 if not any(key(x) in {"text","content","body","document","fulltext"} for x in fields):raise SystemExit(f"no full-text column; schema={fields}")
 a.output_dir.mkdir(parents=True,exist_ok=True);out=a.output_dir/f"spanish-pd-{a.shard:04d}.jsonl.gz"
 digest=hashlib.sha256();source_hash=hashlib.sha256();rows=0;skipped=0
 with path.open("rb") as source_file:
  for block in iter(lambda:source_file.read(1024*1024),b""):source_hash.update(block)
 with gzip.open(out,"wt",encoding="utf-8",newline="\n",compresslevel=6) as f:
  i=0
  for batch in parquet.iter_batches(batch_size=16):
   for row in batch.to_pylist():
    i+=1
    nested=row.get("metadata") if isinstance(row.get("metadata"),dict) else {}
    merged={**nested,**row}
    text=clean(first(merged,("text","content","body","document","full_text","fulltext")))
    if len(text)<1000:skipped+=1;continue
    title=clean(first(merged,("title","name","work_title")));author=clean(first(merged,("author","creator","authors")))
    year=clean(first(merged,("year","publication_year","date","publication_date")))
    source_url=clean(first(merged,("url","source_url","original_url")))
    source_id=clean(first(merged,("id","doc_id","document_id","ark"))) or hashlib.sha256((title+"\n"+author+"\n"+text[:1000]).encode()).hexdigest()
    record={"id":f"pleias-spanish-pd:{a.shard}:{source_id}","text":text,"domain":"literatura y patrimonio documental en español",
     "language":"es","split":"train","train_eligible":True,"admission_status":"accepted","synthetic":False,
     "license":LICENSE,"source_dataset":REPO,"source":SOURCE,"source_revision":REVISION,"source_file":name,"source_row":i,
     "title":title,"author":author,"publication_date":year,"original_source_url":source_url,
     "attribution":"PleIAs, Spanish Public Domain Books; source metadata retained; public-domain collection per dataset card."}
    line=json.dumps(record,ensure_ascii=False,separators=(",",":"))+"\n";f.write(line);digest.update(line.encode());rows+=1
 if rows<100:raise SystemExit(f"too few full texts: {rows}; skipped={skipped}; fields={fields}")
 m={"schema_version":1,"dataset":"PleIAs Spanish-PD-Books","source_dataset":REPO,"source_url":SOURCE,"source_revision":REVISION,
  "source_file":name,"shard":a.shard,"license":LICENSE,"language":"es","record_count":rows,"skipped_short_or_empty":skipped,
  "file":out.name,"sha256_jsonl_uncompressed":digest.hexdigest(),"source_parquet_sha256":source_hash.hexdigest(),
  "source_parquet_bytes":path.stat().st_size,"retrieved_at_utc":datetime.now(timezone.utc).isoformat(),
  "admission_status":"accepted; full-text public-domain source",
  "limitations":["OCR quality varies by historical source and edition; inspect sampled documents.",
   "Public-domain status follows the dataset curator's documented criteria; original source metadata is retained.",
   "Exact deduplication across shards is reported by the unified corpus builder, not removed here."]}
 (a.output_dir/f"spanish-pd-{a.shard:04d}.manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({k:m[k] for k in ("shard","record_count","skipped_short_or_empty","source_parquet_sha256","sha256_jsonl_uncompressed")},ensure_ascii=False))
if __name__=="__main__":main()
