#!/usr/bin/env python3
"""Acquire one Spanish BNE Hemeroteca OCR Parquet shard, omitting image bytes."""
from __future__ import annotations
import argparse,gzip,hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download
import pyarrow.parquet as pq
REPO="ferjorosa/bne-hemeroteca-ocr-xix"
SOURCE="https://huggingface.co/datasets/ferjorosa/bne-hemeroteca-ocr-xix"
LICENSE="CC0 1.0 (public domain; dataset card and BNE provenance)"
SPLITS={"agricultura_y_ganaderia":"agricultura y ganadería","ciencias":"ciencia","cultura":"cultura","deportes":"deportes","derecho":"derecho","economia":"economía","educacion":"educación","fuerzas_armadas":"fuerzas armadas","historia":"historia","industria":"industria","literatura":"literatura","medicina":"medicina","mineria":"minería","musica":"música","navegacion":"navegación","politica":"política","relaciones_internacionales":"relaciones internacionales","religion":"religión","revistas_femeninas":"revistas femeninas","teatro":"teatro"}
COLUMNS=["issue_uuid","issue_name","page","publication_issn","date","issue_link","text","model_id","primary_language","is_rotation_valid","is_table","is_diagram","total_input_tokens","total_output_tokens"]
def val(row,key):
 v=row.get(key)
 if v is None:return None
 if hasattr(v,"isoformat"):return v.isoformat()
 return v
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--split",choices=sorted(SPLITS),required=True);ap.add_argument("--revision",required=True);ap.add_argument("--output-dir",type=Path,default=Path("out"));a=ap.parse_args()
 if len(a.revision)!=40:raise SystemExit("revision must be a full HF commit SHA")
 files=HfApi().list_repo_files(REPO,repo_type="dataset",revision=a.revision)
 prefix=f"data/{a.split}-";candidates=sorted(x for x in files if x.startswith(prefix) and x.endswith(".parquet"))
 if not candidates:raise SystemExit(f"no Parquet shards for split={a.split}; first files={files[:30]}")
 source_file=candidates[0];path=Path(hf_hub_download(REPO,filename=source_file,revision=a.revision,repo_type="dataset"))
 parquet=pq.ParquetFile(path);fields=parquet.schema.names
 missing=[x for x in COLUMNS if x not in fields]
 if missing:raise SystemExit(f"missing expected BNE OCR fields {missing}; schema={fields}")
 a.output_dir.mkdir(parents=True,exist_ok=True);out=a.output_dir/f"bne-ocr-es-{a.split}.jsonl.gz"
 digest=hashlib.sha256();source_hash=hashlib.sha256()
 with path.open("rb") as f:
  for block in iter(lambda:f.read(1024*1024),b""):source_hash.update(block)
 seen=set();scanned=0;admitted=0;skipped={}
 with gzip.open(out,"wt",encoding="utf-8",newline="\n",compresslevel=6) as f:
  for batch in parquet.iter_batches(batch_size=64,columns=COLUMNS):
   for row in batch.to_pylist():
    scanned+=1;text=str(row.get("text") or "").strip();lang=str(row.get("primary_language") or "").casefold()
    if lang not in {"es","spa","spanish","español"}:skipped["non_spanish"]=skipped.get("non_spanish",0)+1;continue
    d=row.get("date")
    if d is not None and getattr(d,"year",9999)>1900:skipped["post_1900"]=skipped.get("post_1900",0)+1;continue
    if row.get("is_rotation_valid") is False:skipped["invalid_rotation"]=skipped.get("invalid_rotation",0)+1;continue
    if len(text)<500:skipped["short_text"]=skipped.get("short_text",0)+1;continue
    issue=str(row.get("issue_uuid") or "").strip();page=int(row.get("page") or 0)
    if not issue or page<=0:skipped["missing_issue_identity"]=skipped.get("missing_issue_identity",0)+1;continue
    identity=f"{issue}:{page}"
    text_hash=hashlib.sha256(text.casefold().encode("utf-8")).hexdigest()
    if text_hash in seen:skipped["duplicate_text_in_shard"]=skipped.get("duplicate_text_in_shard",0)+1;continue
    seen.add(text_hash)
    record={"id":f"bne-ocr-xix:{a.split}:{identity}","text":text,"domain":SPLITS[a.split],"language":"es","split":"train",
     "train_eligible":True,"admission_status":"accepted","synthetic":False,"license":LICENSE,"source_dataset":REPO,
     "source":SOURCE,"source_revision":a.revision,"source_file":source_file,"source_row":scanned,"issue_uuid":issue,
     "issue_name":row.get("issue_name"),"page":page,"publication_issn":row.get("publication_issn"),"date":val(row,"date"),
     "issue_link":row.get("issue_link"),"ocr_model":row.get("model_id"),"is_table":bool(row.get("is_table")),
     "is_diagram":bool(row.get("is_diagram")),"ocr_rotation_valid":row.get("is_rotation_valid"),
     "ocr_input_tokens":row.get("total_input_tokens"),"ocr_output_tokens":row.get("total_output_tokens"),
     "attribution":"Biblioteca Nacional de España, Hemeroteca Digital; OCR dataset curated by Fernando Rodriguez (2025), CC0 1.0."}
    line=json.dumps(record,ensure_ascii=False,separators=(",",":"))+"\n";f.write(line);digest.update(line.encode());admitted+=1
 if admitted<100:raise SystemExit(f"too few admitted pages for {a.split}: {admitted}; scanned={scanned}; skipped={skipped}")
 manifest={"schema_version":1,"dataset":"BNE Hemeroteca OCR Dataset (19th Century)","source_dataset":REPO,"source_url":SOURCE,
  "source_revision":a.revision,"source_file":source_file,"split":a.split,"domain":SPLITS[a.split],"license":"CC0 1.0",
  "language":"es","temporal_filter":"date <= 1900-12-31 when date is available","rows_scanned":scanned,"rows_admitted":admitted,
  "rows_skipped":skipped,"file":out.name,"sha256_jsonl_uncompressed":digest.hexdigest(),"source_parquet_sha256":source_hash.hexdigest(),
  "source_parquet_bytes":path.stat().st_size,"retrieved_at_utc":datetime.now(timezone.utc).isoformat(),
  "admission_status":"accepted; text-only BNE public-domain OCR pages",
  "limitations":["Historical OCR contains spelling and recognition errors; source text is not silently corrected.",
   "Dataset includes selected long-running titles that may extend into the 20th century; rows after 1900 are excluded.",
   "Image column is not included in the training JSONL; only text and bibliographic/OCR metadata are retained."]}
 (a.output_dir/f"bne-ocr-es-{a.split}.manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({k:manifest[k] for k in ("split","rows_scanned","rows_admitted","rows_skipped","source_file","source_parquet_sha256","sha256_jsonl_uncompressed")},ensure_ascii=False))
if __name__=="__main__":main()
