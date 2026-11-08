#!/usr/bin/env python3
"""Build one auditable MINIRONIN training corpus without dropping source rows.

Synthetic variation is never relabelled as independent knowledge. Every record
retains its source, licence note, dataset and original metadata. Exact duplicates
are reported, not discarded, so row volume is preserved.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, re
from collections import Counter
from pathlib import Path

TEXT_EXT={".txt",".md",".xml",".tei",".html",".htm"}
SKIP=re.compile(r"(manifest|summary|sha256|readme)",re.I)

def sha(data:bytes)->str: return hashlib.sha256(data).hexdigest()
def sha_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()
def norm(text:str)->str: return re.sub(r"\W+"," ",text.casefold(),flags=re.UNICODE).strip()

def strings(value):
    if isinstance(value,str):
        if value.strip(): yield value.strip()
    elif isinstance(value,dict):
        for k,v in value.items():
            if isinstance(v,(str,int,float)): 
                if str(v).strip(): yield str(v).strip()
            else: yield from strings(v)
    elif isinstance(value,list):
        for v in value: yield from strings(v)

def as_record(obj, path, line_no):
    if isinstance(obj,dict):
        q=obj.get("question") or obj.get("prompt") or obj.get("input")
        a=obj.get("answer") or obj.get("target") or obj.get("completion")
        if q is not None and a is not None:
            body=str(q).strip()+"\n"+str(a).strip()
        else:
            preferred=[]
            for key in ("text","content","body","document","passage"):
                if isinstance(obj.get(key),str) and obj[key].strip(): preferred.append(obj[key].strip())
            body="\n".join(preferred) if preferred else "\n".join(strings(obj))
        metadata=obj
    else:
        body="\n".join(strings(obj)); metadata={"raw_type":type(obj).__name__}
    if not body.strip(): body=json.dumps(obj,ensure_ascii=False,sort_keys=True)
    synthetic=bool(path.name.endswith(".jsonl.gz") and ("curricula" in str(path) or "behavioral" in str(path)))
    return {"id":str(metadata.get("id",f"{path.name}:{line_no}")) if isinstance(metadata,dict) else f"{path.name}:{line_no}",
      "source_id":str(path),"domain":str(metadata.get("domain") or metadata.get("subject") or path.parent.name) if isinstance(metadata,dict) else path.parent.name,
      "source":str(metadata.get("source") or path.name) if isinstance(metadata,dict) else path.name,
      "license":str(metadata.get("license") or "See source catalogue; provenance retained") if isinstance(metadata,dict) else "See source catalogue; provenance retained",
      "synthetic":synthetic,"dataset":path.name,"text":body,"metadata":metadata}

def read_jsonl(path):
    opener=gzip.open if path.name.endswith(".gz") else open
    with opener(path,"rt",encoding="utf-8") as f:
        for i,line in enumerate(f,1):
            if not line.strip(): continue
            yield as_record(json.loads(line),path,i)

def read_json(path):
    obj=json.loads(path.read_text(encoding="utf-8"))
    rows=obj if isinstance(obj,list) else [obj]
    for i,row in enumerate(rows,1): yield as_record(row,path,i)

def read_delimited(path):
    delimiter="\\t" if path.suffix.lower()==".tsv" else ","
    with path.open("r",encoding="utf-8",errors="replace",newline="") as f:
        for i,row in enumerate(csv.DictReader(f,delimiter=delimiter),1): yield as_record(row,path,i)

def read_parquet(path):
    import pyarrow.parquet as pq
    table=pq.read_table(path)
    for i,row in enumerate(table.to_pylist(),1): yield as_record(row,path,i)

def read_source(path):
    suffix=path.suffix.lower()
    if path.name.endswith((".jsonl.gz",".ndjson.gz")) or suffix in {".jsonl",".ndjson"}:
        yield from read_jsonl(path)
    elif suffix==".json":
        yield from read_json(path)
    elif suffix==".parquet":
        yield from read_parquet(path)
    elif suffix in {".csv",".tsv"}:
        yield from read_delimited(path)
    elif suffix in TEXT_EXT:
        text=path.read_text(encoding="utf-8",errors="replace").strip()
        if text: yield as_record({"text":text,"id":path.name,"source":str(path),"license":"See source catalogue"},path,1)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",default="unified-train")
    ap.add_argument("--roots",nargs="+",required=True)
    args=ap.parse_args()
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    roots=[Path(x) for x in args.roots]
    files=[]
    for root in roots:
        if not root.exists(): raise SystemExit(f"Required source root missing: {root}")
        files.extend(p for p in root.rglob("*") if p.is_file() and not SKIP.search(p.name)
                     and (p.suffix.lower() in TEXT_EXT|{".json",".jsonl",".ndjson",".parquet",".csv",".tsv"} or p.name.endswith((".jsonl.gz",".ndjson.gz"))))
    files=sorted(set(files))
    if not files: raise SystemExit("No source files found")
    source_manifest=[]; rows=0; duplicates=0; empty=0; tiny=0
    seen=set(); domains=Counter(); datasets=Counter(); synthetic=Counter()
    output_path=out/"train.jsonl.gz"
    with output_path.open("wb") as raw:
      with gzip.GzipFile(fileobj=raw,mode="wb",mtime=0,compresslevel=6) as gz:
        for path in files:
          before=rows; input_hash=sha_file(path)
          for record in read_source(path):
            body=record["text"].strip()
            if not body: empty+=1
            if len(body)<24: tiny+=1
            digest=sha(norm(body).encode("utf-8"))
            if digest in seen: duplicates+=1
            else: seen.add(digest)
            domains[record["domain"]]+=1; datasets[record["dataset"]]+=1
            synthetic["synthetic" if record["synthetic"] else "source_text"]+=1
            line=(json.dumps(record,ensure_ascii=False,separators=(",",":"))+"\n").encode("utf-8")
            gz.write(line); rows+=1
          source_manifest.append({"path":str(path),"sha256":input_hash,"records":rows-before,"bytes":path.stat().st_size})
    if rows==0: raise SystemExit("Unified corpus is empty")
    summary={"schema":"minironin-unified-train-v1","record_count":rows,"unique_normalized_texts":len(seen),
      "exact_or_normalized_duplicates_reported_not_removed":duplicates,"empty_records":empty,"short_records_under_24_chars":tiny,
      "synthetic_and_source_counts":dict(synthetic),"domains":dict(domains),"datasets":dict(datasets),
      "volume_policy":"No input records are discarded. Duplicate and short records are reported for review; source row counts remain intact.",
      "quality_policy":"Synthetic templates are explicitly marked. Ten-seed factual curricula are not counted as independent facts. Arithmetic answers remain generated by the deterministic verifier in the source generator.",
      "input_roots":[str(x) for x in roots],"source_files":len(source_manifest),"sources":source_manifest,
      "train_jsonl_gz_bytes":output_path.stat().st_size,"train_jsonl_gz_sha256":sha_file(output_path)}
    (out/"sources.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (out/"quality-report.json").write_text(json.dumps({k:summary[k] for k in ("record_count","unique_normalized_texts","exact_or_normalized_duplicates_reported_not_removed","empty_records","short_records_under_24_chars","synthetic_and_source_counts","domains","datasets","quality_policy","volume_policy")},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (out/"SHA256SUMS").write_text(f"{sha_file(output_path)}  train.jsonl.gz\n{sha((out/'sources.json').read_bytes())}  sources.json\n{sha((out/'quality-report.json').read_bytes())}  quality-report.json\n",encoding="utf-8")
    print(json.dumps({"records":rows,"source_files":len(source_manifest),"duplicates_reported":duplicates,"artifact_bytes":output_path.stat().st_size},ensure_ascii=False))
if __name__=="__main__": main()
