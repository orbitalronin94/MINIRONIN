#!/usr/bin/env python3
"""Build one auditable MINIRONIN training corpus without dropping source rows.

Synthetic variation is never relabelled as independent knowledge. Every record
retains its source, licence note, dataset and original metadata. Exact duplicates
are reported, not discarded, so row volume is preserved.
"""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, re, shutil
from collections import Counter
from pathlib import Path

TEXT_EXT={".txt",".md",".xml",".tei",".html",".htm"}
SKIP=re.compile(r"(manifest|summary|sha256|readme|library-artifact)",re.I)

def sha(data:bytes)->str: return hashlib.sha256(data).hexdigest()
def sha_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()
def norm(text:str)->str: return re.sub(r"\W+"," ",text.casefold(),flags=re.UNICODE).strip()

def is_synthetic_path(path:Path)->bool:
    return bool(re.search(r"(generated-curricula|generated-basic-curricula|generated-math-es|behavioral-datasets|minironin-(?:abstention-50k|abstain-(?:plain|literary|koan)|aristocrat-trivial|casuist-cynic|scientist-exhausted|oracle-doom|error404-indifference|lexicon-diagnostic))",str(path),re.I))

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
            context=obj.get("context") or obj.get("evidence") or obj.get("evidencia") or ""
            parts=[]
            if str(context).strip(): parts.append("Contexto: "+str(context).strip())
            parts.extend(("Pregunta: "+str(q).strip(),"Respuesta: "+str(a).strip()))
            body="\n".join(parts)
        else:
            preferred=[]
            for key in ("text","content","body","document","passage"):
                if isinstance(obj.get(key),str) and obj[key].strip(): preferred.append(obj[key].strip())
            body="\n".join(preferred) if preferred else "\n".join(strings(obj))
        metadata={k:v for k,v in obj.items() if k not in {"text","content","body","document","passage"}}
    else:
        body="\n".join(strings(obj)); metadata={"raw_type":type(obj).__name__}
    if not body.strip(): body=json.dumps(obj,ensure_ascii=False,sort_keys=True,default=str)
    synthetic_flag = isinstance(obj,dict) and str(obj.get("synthetic","")).strip().lower() in {"true","1","yes"}
    synthetic=bool(synthetic_flag or is_synthetic_path(path))
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
    delimiter="\t" if path.suffix.lower()==".tsv" else ","
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
        if text: yield {"id":path.name,"source_id":str(path),"domain":path.parent.name,"source":str(path),"license":"See source catalogue; provenance retained","synthetic":is_synthetic_path(path),"dataset":path.name,"text":text,"metadata":{"file_name":path.name}}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",default="unified-train")
    ap.add_argument("--library-manifest",help="Versioned library artifact JSON; defines canonical source roots and synthetic policy")
    ap.add_argument("--roots",nargs="+",help="Explicit source roots (legacy mode; prefer --library-manifest)")
    ap.add_argument("--exclude-synthetic",action="store_true",help="Override artifact and exclude explicitly synthetic records")
    args=ap.parse_args()
    library_manifest=None
    library_manifest_sha256=None
    if args.library_manifest:
        manifest_path=Path(args.library_manifest)
        library_manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
        if library_manifest.get("schema_version") != 1 or library_manifest.get("artifact_id") != "minironin-library-v1":
            raise SystemExit(f"Unsupported library artifact: {manifest_path}")
        if args.roots:
            raise SystemExit("Do not combine --library-manifest with --roots")
        roots=[Path(item["path"]) for item in library_manifest.get("roots",[])]
        if not roots:
            raise SystemExit("Library artifact contains no source roots")
        include_synthetic=bool(library_manifest.get("defaults",{}).get("include_synthetic",False))
        exclude_synthetic=bool(args.exclude_synthetic or not include_synthetic)
        library_manifest_sha256=sha_file(manifest_path)
    else:
        if not args.roots:
            raise SystemExit("Provide --library-manifest or legacy --roots")
        roots=[Path(x) for x in args.roots]
        exclude_synthetic=bool(args.exclude_synthetic)
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    files=[]
    for root in roots:
        if not root.exists(): raise SystemExit(f"Required source root missing: {root}")
        files.extend(p for p in root.rglob("*") if p.is_file() and not SKIP.search(p.name)
                     and (p.suffix.lower() in TEXT_EXT|{".json",".jsonl",".ndjson",".parquet",".csv",".tsv"} or p.name.endswith((".jsonl.gz",".ndjson.gz"))))
    files=sorted(set(files))
    if not files: raise SystemExit("No source files found")
    source_manifest=[]; rows=0; records_seen=0; excluded_synthetic=0; duplicates=0; empty=0; tiny=0
    seen=set(); domains=Counter(); datasets=Counter(); synthetic=Counter(); unique_by_dataset=Counter(); duplicates_by_dataset=Counter()
    output_path=out/"train.jsonl.gz"
    with output_path.open("wb") as raw:
      with gzip.GzipFile(fileobj=raw,mode="wb",mtime=0,compresslevel=6) as gz:
        for path in files:
          before=rows; input_hash=sha_file(path)
          excluded_before=excluded_synthetic
          for record in read_source(path):
            records_seen+=1
            if exclude_synthetic and record.get("synthetic") is True:
                excluded_synthetic+=1
                continue
            body=record["text"].strip()
            if not body: empty+=1
            if len(body)<24: tiny+=1
            digest=sha(norm(body).encode("utf-8"))
            if digest in seen:
                duplicates+=1; duplicates_by_dataset[record["dataset"]]+=1
            else:
                seen.add(digest); unique_by_dataset[record["dataset"]]+=1
            domains[record["domain"]]+=1; datasets[record["dataset"]]+=1
            synthetic["synthetic" if record["synthetic"] else "source_text"]+=1
            line=(json.dumps(record,ensure_ascii=False,separators=(",",":"),default=str)+"\n").encode("utf-8")
            gz.write(line); rows+=1
          source_manifest.append({"path":str(path),"sha256":input_hash,"records":rows-before,"records_written":rows-before,"synthetic_records_excluded":excluded_synthetic-excluded_before,"bytes":path.stat().st_size})
    if rows==0: raise SystemExit("Unified corpus is empty")
    summary={"schema":"minironin-unified-train-v2","record_count":rows,"records_seen":records_seen,"synthetic_records_excluded":excluded_synthetic,"exclude_synthetic":exclude_synthetic,"synthetic_included":not exclude_synthetic,"library_artifact_id":(library_manifest or {}).get("artifact_id"),"library_artifact_sha256":library_manifest_sha256,"unique_normalized_texts":len(seen),
      "exact_or_normalized_duplicates_reported_not_removed":duplicates,"unique_by_dataset":dict(unique_by_dataset),"duplicates_by_dataset":dict(duplicates_by_dataset),"empty_records":empty,"short_records_under_24_chars":tiny,
      "synthetic_and_source_counts":dict(synthetic),"domains":dict(domains),"datasets":dict(datasets),
      "volume_policy":("Explicitly synthetic rows are excluded before training-corpus publication; duplicates and short records among retained source rows are reported, not discarded." if args.exclude_synthetic else "No input records are discarded. Duplicate and short records are reported for review; source row counts remain intact."),
      "quality_policy":"Synthetic templates are explicitly marked. Ten-seed factual curricula are not counted as independent facts. Arithmetic answers remain generated by the deterministic verifier in the source generator.",
      "input_roots":[str(x) for x in roots],"source_files":len(source_manifest),"sources":source_manifest,
      "train_jsonl_gz_bytes":output_path.stat().st_size,"train_jsonl_gz_sha256":sha_file(output_path)}
    (out/"sources.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (out/"quality-report.json").write_text(json.dumps({k:summary[k] for k in ("record_count","records_seen","synthetic_records_excluded","exclude_synthetic","unique_normalized_texts","exact_or_normalized_duplicates_reported_not_removed","empty_records","short_records_under_24_chars","synthetic_and_source_counts","domains","datasets","quality_policy","volume_policy")},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    provenance_dir=out/"provenance"; provenance_dir.mkdir(exist_ok=True)
    provenance_paths=[]
    for root in roots:
        provenance_paths.extend(p for p in root.rglob("*") if p.is_file() and ("manifest" in p.name.lower() or p.name.lower()=="readme.md" or p.suffix.lower()==".sha256"))
    provenance_paths.extend(Path(x) for x in (
        "data/japan/SOURCES.json","data/classics/SOURCES.json",
        "data/anarchist/SOURCES.jsonl","data/inherited/papers/README.md"
    ) if Path(x).is_file())
    copied=[]
    for path in sorted(set(provenance_paths)):
        dest=provenance_dir/(path.parent.name+"--"+path.name)
        shutil.copy2(path,dest)
        copied.append({"path":str(dest.relative_to(out)),"source_path":str(path),"bytes":dest.stat().st_size,"sha256":sha_file(dest)})
    (provenance_dir/"PRODATPHIL-SHA256.txt").write_text("8eacf44101c87772a842fce3d3ab415903f28ba7684f8b33eddba0e2489c13c9  prodatphil_en_txt_0_3.zip\n",encoding="utf-8")
    (provenance_dir/"HERETIC-SHA256.txt").write_text("HERETIC source archive SHA-256 is recorded in the source workflow and source file hashes in sources.json.\n",encoding="utf-8")
    checks=[("train.jsonl.gz",output_path),("sources.json",out/"sources.json"),("quality-report.json",out/"quality-report.json")]
    checks.extend((str(p.relative_to(out)),p) for p in sorted(provenance_dir.rglob("*")) if p.is_file())
    (out/"SHA256SUMS").write_text("".join(f"{sha_file(path)}  {name}\n" for name,path in checks),encoding="utf-8")
    print(json.dumps({"records":rows,"source_files":len(source_manifest),"provenance_files":len(copied)+2,"duplicates_reported":duplicates,"artifact_bytes":sum(p.stat().st_size for p in out.rglob("*") if p.is_file())},ensure_ascii=False))
if __name__=="__main__": main()
