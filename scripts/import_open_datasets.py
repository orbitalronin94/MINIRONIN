#!/usr/bin/env python3
"""Import complete licensed Hugging Face datasets as bounded JSONL shards."""
from __future__ import annotations
import argparse,gzip,hashlib,json,re,sys
from datetime import datetime,timezone
from pathlib import Path

ALLOWED={"cc0-1.0","cc-by-4.0","cc-by-sa-4.0","cc-by-sa-3.0","public-domain","mit","apache-2.0","bsd-3-clause"}
def norm_license(v): return str(v).strip().casefold().replace("_","-").replace(" ","-")
def flatten_text(v):
    if isinstance(v,str):
        if v.strip(): yield v.strip()
    elif isinstance(v,dict):
        for k,x in v.items():
            if k.casefold() not in {"audio","image","video","path","url","id","metadata"}: yield from flatten_text(x)
    elif isinstance(v,(list,tuple)):
        for x in v: yield from flatten_text(x)
def hash_file(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--manifest-dir",default="data/curated/intake-manifests"); ap.add_argument("--output-dir",default="data/curated/accepted")
    args=ap.parse_args()
    from datasets import load_dataset
    from huggingface_hub import HfApi
    manifests=sorted(Path(args.manifest_dir).glob("*.json"))
    if not manifests: raise SystemExit("No dataset intake manifests found")
    outdir=Path(args.output_dir); outdir.mkdir(parents=True,exist_ok=True); results=[]
    for mp in manifests:
        m=json.loads(mp.read_text(encoding="utf-8")); slug=m["slug"]; repo=m["repo_id"]; expected=norm_license(m["license"])
        if bool(m.get("synthetic",False)):
            results.append({"slug":slug,"status":"excluded_synthetic","reason":"Project policy: synthetic datasets are not admitted to the real training corpus."})
            print(f"INTAKE_EXCLUDED_SYNTHETIC {slug}")
            continue
        manifest_out=outdir/f"{slug}.manifest.json"
        if m.get("external_release_only"):
            results.append({"slug":slug,"status":"external_release_only"}); continue
        if manifest_out.exists():
            prior=json.loads(manifest_out.read_text(encoding="utf-8"))
            names=prior.get("files",[prior.get("file")])
            if names and all((outdir/n).exists() for n in names):
                results.append({"slug":slug,"status":"already_imported","rows":prior.get("rows_admitted",0)}); continue
        gzip_output=bool(m.get("gzip_output",True)); shard_rows=max(1,int(m.get("shard_rows",50000)))
        shard_paths=[]; shard_counts=[]; current=None; current_count=0; shard_index=0
        digest=hashlib.sha256(); seen=set(); scanned=admitted=duplicates=short=wrong_language=0
        try:
            info=HfApi().dataset_info(repo); revision=info.sha; card=info.card_data
            raw=getattr(card,"license",None) if card else None
            values=raw if isinstance(raw,(list,tuple,set)) else [raw]
            normalized={norm_license(v) for v in values if v is not None}
            if expected not in ALLOWED or expected not in normalized: raise ValueError(f"license mismatch or unsupported: expected={expected}, actual={sorted(normalized)}")
            ds=load_dataset(repo,name=m.get("config"),split=m.get("split","train"),revision=revision,streaming=bool(m.get("streaming",False)),trust_remote_code=bool(m.get("trust_remote_code",False)))
            fields=m.get("text_fields",[]); drop=[x for x in m.get("drop_columns",[]) if x in getattr(ds,"column_names",[])]
            if drop: ds=ds.remove_columns(drop)
            lang_field=m.get("language_field"); langs={str(x).casefold() for x in m.get("language_values",[])}
            def new_shard():
                nonlocal current,current_count,shard_index
                if current is not None: current.close(); shard_counts.append(current_count)
                shard_index+=1; current_count=0
                suffix=".jsonl.gz" if gzip_output else ".jsonl"
                path=outdir/f"{slug}.part-{shard_index:05d}{suffix}"
                shard_paths.append(path)
                current=(gzip.open(path,"wt",encoding="utf-8",newline="\n") if gzip_output else path.open("w",encoding="utf-8",newline="\n"))
            for i,row in enumerate(ds):
                scanned+=1
                if lang_field and langs and str(row.get(lang_field,"")).casefold() not in langs:
                    wrong_language+=1; continue
                chunks=list(flatten_text([row.get(k) for k in fields] if fields else [row]))
                body="\n".join(chunks).strip()
                if len(body)<int(m.get("min_text_chars",24)): short+=1; continue
                key=hashlib.sha256(re.sub(r"\s+"," ",body).casefold().encode()).hexdigest()
                if key in seen: duplicates+=1; continue
                seen.add(key)
                rec={"id":f"{slug}:{i}:{key[:12]}","text":body,"domain":m.get("domain","español general"),"language":"es",
                  "split":m.get("split","train"),"train_eligible":True,"admission_status":"accepted",
                  "synthetic":bool(m.get("synthetic",False)),"synthetic_status":m.get("synthetic_status","synthetic" if m.get("synthetic",False) else "not_declared"),
                  "license":m["license"],"source_dataset":repo,"source":m["source_url"],"source_revision":revision,
                  "source_row":i,"attribution":m["attribution"],"task":m.get("task","language modeling"),
                  "metadata":{k:v for k,v in row.items() if k not in fields and isinstance(v,(str,int,float,bool,list,tuple))}}
                line=json.dumps(rec,ensure_ascii=False,separators=(",",":"),default=str)+"\n"
                if current is None or current_count>=shard_rows: new_shard()
                current.write(line); digest.update(line.encode()); admitted+=1; current_count+=1
            if current is not None: current.close(); shard_counts.append(current_count); current=None
            if admitted<int(m.get("minimum_rows",1)): raise ValueError(f"too few admissible rows: {admitted}")
            if not shard_paths: raise ValueError("no rows admitted")
            hashes=[{"file":p.name,"sha256":hash_file(p),"rows":n} for p,n in zip(shard_paths,shard_counts)]
            result={"schema_version":1,"slug":slug,"dataset":m["name"],"repo_id":repo,"source_url":m["source_url"],
              "source_revision":revision,"license":m["license"],"language":"es","split":m.get("split","train"),
              "rows_scanned":scanned,"rows_admitted":admitted,"duplicates_skipped":duplicates,"short_skipped":short,
              "wrong_language_skipped":wrong_language,"files":[p.name for p in shard_paths],"file_hashes":hashes,
              "file":shard_paths[0].name,"sha256_jsonl_uncompressed":digest.hexdigest(),
              "retrieved_at_utc":datetime.now(timezone.utc).isoformat(),
              "admission_policy":"Complete configured upstream split; exact upstream license match, Spanish source metadata, minimum text length, exact deduplication; bounded shards with source provenance."}
            manifest_out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            results.append({"slug":slug,"status":"accepted","rows":admitted,"shards":len(shard_paths)})
        except Exception as exc:
            if current is not None:
                try: current.close()
                except Exception: pass
            for p in shard_paths: p.unlink(missing_ok=True)
            manifest_out.unlink(missing_ok=True)
            results.append({"slug":slug,"status":"rejected_or_retry","reason":str(exc)[:1000]})
            print(f"INTAKE_REJECTED {slug}: {exc}",file=sys.stderr)
    report_dir=Path("data/intake-reports"); report_dir.mkdir(parents=True,exist_ok=True)
    report=report_dir/"open-dataset-intake-report.json"
    report.write_text(json.dumps({"generated_at_utc":datetime.now(timezone.utc).isoformat(),"results":results},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"accepted":sum(x["status"]=="accepted" for x in results),"already_imported":sum(x["status"]=="already_imported" for x in results),"not_admitted":sum(x["status"]=="rejected_or_retry" for x in results),"results":results},ensure_ascii=False))
if __name__=="__main__": main()
