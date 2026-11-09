#!/usr/bin/env python3
"""Import full, explicitly licensed Hugging Face dataset train splits from manifests."""
from __future__ import annotations
import argparse, gzip, hashlib, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

ALLOWED = {
    "cc0-1.0", "cc-by-4.0", "cc-by-sa-4.0", "cc-by-sa-3.0",
    "public-domain", "mit", "apache-2.0", "bsd-3-clause"
}
def norm_license(value):
    return str(value).strip().casefold().replace("_","-").replace(" ","-")
def flatten_text(value):
    if isinstance(value,str):
        v=value.strip()
        if v: yield v
    elif isinstance(value,dict):
        for k,v in value.items():
            if k.casefold() in {"audio","image","video","path","url","id","metadata"}: continue
            yield from flatten_text(v)
    elif isinstance(value,(list,tuple)):
        for v in value: yield from flatten_text(v)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest-dir",default="data/curated/intake-manifests")
    ap.add_argument("--output-dir",default="data/curated/accepted")
    args=ap.parse_args()
    from datasets import load_dataset
    from huggingface_hub import HfApi
    manifests=sorted(Path(args.manifest_dir).glob("*.json"))
    if not manifests: raise SystemExit("No dataset intake manifests found")
    outdir=Path(args.output_dir); outdir.mkdir(parents=True,exist_ok=True)
    results=[]
    for mp in manifests:
        m=json.loads(mp.read_text(encoding="utf-8"))
        slug=m["slug"]; repo=m["repo_id"]; expected=norm_license(m["license"])
        out=outdir/(f"{slug}.jsonl.gz" if m.get("gzip_output") else f"{slug}.jsonl")
        manifest_out=outdir/f"{slug}.manifest.json"
        if out.exists() and manifest_out.exists():
            results.append({"slug":slug,"status":"already_imported"})
            continue
        try:
            info=HfApi().dataset_info(repo)
            revision=info.sha
            card=info.card_data
            raw_license=getattr(card,"license",None) if card else None
            values=raw_license if isinstance(raw_license,(list,tuple,set)) else [raw_license]
            normalized={norm_license(v) for v in values if v is not None}
            if expected not in ALLOWED or expected not in normalized:
                raise ValueError(f"license mismatch or unsupported: expected={expected}, actual={sorted(normalized)}")
            ds=load_dataset(repo,name=m.get("config"),split=m.get("split","train"),revision=revision,streaming=bool(m.get("streaming",False)))
            fields=m.get("text_fields",[])
            drop_columns=[x for x in m.get("drop_columns",[]) if x in getattr(ds,"column_names",[])]
            if drop_columns: ds=ds.remove_columns(drop_columns)
            language_field=m.get("language_field")
            allowed_languages=set(m.get("language_values",[]))
            digest=hashlib.sha256(); seen=set(); scanned=admitted=duplicates=short=wrong_language=0
            with out.open("w",encoding="utf-8",newline="\n") as f:
                for i,row in enumerate(ds):
                    scanned+=1
                    if language_field and allowed_languages and str(row.get(language_field,"")).casefold() not in {x.casefold() for x in allowed_languages}:
                        wrong_language+=1; continue
                    values=[row.get(k) for k in fields] if fields else [row]
                    chunks=list(flatten_text(values))
                    body="\n".join(chunks).strip()
                    if len(body)<int(m.get("min_text_chars",24)):
                        short+=1; continue
                    key=hashlib.sha256(re.sub(r"\s+"," ",body).casefold().encode()).hexdigest()
                    if key in seen: duplicates+=1; continue
                    seen.add(key)
                    record={"id":f"{slug}:{i}:{key[:12]}","text":body,"domain":m.get("domain","español general"),
                      "language":"es","split":m.get("split","train"),"train_eligible":True,
                      "admission_status":"accepted","synthetic":bool(m.get("synthetic",False)),
                      "license":m["license"],"source_dataset":repo,
                      "source":m["source_url"],"source_revision":revision,"source_row":i,
                      "attribution":m["attribution"],"task":m.get("task","language modeling"),
                      "metadata":{k:v for k,v in row.items() if k not in fields and isinstance(v,(str,int,float,bool,list,tuple))}}
                    line=json.dumps(record,ensure_ascii=False,separators=(",",":"),default=str)+"\n"
                    f.write(line); digest.update(line.encode()); admitted+=1
            if admitted < int(m.get("minimum_rows",1)):
                out.unlink(missing_ok=True)
                raise ValueError(f"too few admissible rows: {admitted}")
            result={"schema_version":1,"slug":slug,"dataset":m["name"],"repo_id":repo,
              "source_url":m["source_url"],"source_revision":revision,"license":m["license"],
              "language":"es","split":m.get("split","train"),"rows_scanned":scanned,
              "rows_admitted":admitted,"duplicates_skipped":duplicates,"short_skipped":short,
              "wrong_language_skipped":wrong_language,"file":out.name,"sha256_jsonl":digest.hexdigest(),
              "retrieved_at_utc":datetime.now(timezone.utc).isoformat(),
              "admission_policy":"Complete configured upstream split; exact upstream license match, Spanish source metadata, minimum text length, exact deduplication; provenance and source row preserved."}
            manifest_out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            results.append({"slug":slug,"status":"accepted","rows":admitted,"sha256":result["sha256_jsonl"]})
        except Exception as exc:
            results.append({"slug":slug,"status":"rejected_or_retry","reason":str(exc)[:1000]})
            print(f"INTAKE_REJECTED {slug}: {exc}",file=sys.stderr)
    report_dir=Path("data/curated/intake-reports"); report_dir.mkdir(parents=True,exist_ok=True)
    report=report_dir/"open-dataset-intake-report.json"
    report.write_text(json.dumps({"generated_at_utc":datetime.now(timezone.utc).isoformat(),"results":results},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"accepted":sum(x["status"]=="accepted" for x in results),"already_imported":sum(x["status"]=="already_imported" for x in results),"not_admitted":sum(x["status"]=="rejected_or_retry" for x in results),"results":results},ensure_ascii=False))
if __name__=="__main__": main()
