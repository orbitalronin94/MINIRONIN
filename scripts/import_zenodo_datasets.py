#!/usr/bin/env python3
"""Stream complete, license-checked Zenodo corpora into bounded gzip JSONL shards."""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,re,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path
import requests
def norm(x): return str(x or "").casefold().replace("_","-").replace(" ","-").strip()
def hash_file(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def text_values(v):
    if isinstance(v,str):
        if v.strip(): yield v.strip()
    elif isinstance(v,dict):
        for k,x in v.items():
            if k.casefold() not in {"id","url","path","metadata","audio","image"}: yield from text_values(x)
    elif isinstance(v,(list,tuple)):
        for x in v: yield from text_values(x)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--manifest-dir",default="data/curated/zenodo-intake-manifests"); ap.add_argument("--output-dir",default="data/curated/accepted")
    args=ap.parse_args(); outdir=Path(args.output_dir); outdir.mkdir(parents=True,exist_ok=True); reports=[]
    for mp in sorted(Path(args.manifest_dir).glob("*.json")):
        m=json.loads(mp.read_text(encoding="utf-8")); slug=m["slug"]; mout=outdir/f"{slug}.manifest.json"
        if mout.exists():
            prior=json.loads(mout.read_text()); names=prior.get("files",[prior.get("file")])
            if names and all((outdir/n).exists() for n in names): reports.append({"slug":slug,"status":"already_imported","rows":prior.get("rows_admitted",0)}); continue
        tmp=Path("/tmp")/f"{slug}.source"; shard_paths=[]; shard_counts=[]; current=None; current_count=0; shard_index=0
        digest=hashlib.sha256(); seen=set(); scanned=admitted=duplicates=short=0
        try:
            response=requests.get(f"https://zenodo.org/api/records/{m['record_id']}",timeout=90); response.raise_for_status(); record=response.json()
            metadata=record.get("metadata",{}); lic=metadata.get("license") or {}
            actual=norm(lic.get("id") if isinstance(lic,dict) else lic); expected=norm(m["license_id"])
            if actual!=expected: raise ValueError(f"license mismatch: expected={expected}, actual={actual}")
            candidates=[f for f in record.get("files",[]) if re.search(m["file_regex"],f["key"],re.I)]
            if len(candidates)!=1: raise ValueError(f"expected one source file matching {m['file_regex']}, found {[x['key'] for x in candidates]}")
            source=candidates[0]; url=source.get("links",{}).get("self")
            if not url: raise ValueError("Zenodo source file has no download URL")
            with requests.get(url,stream=True,timeout=(60,300)) as r:
                r.raise_for_status()
                with tmp.open("wb") as f:
                    for b in r.iter_content(1024*1024):
                        if b: f.write(b)
            source_sha=hash_file(tmp); shard_rows=max(1,int(m.get("shard_rows",50000)))
            def new_shard():
                nonlocal current,current_count,shard_index
                if current is not None: current.close(); shard_counts.append(current_count)
                shard_index+=1; current_count=0
                p=outdir/f"{slug}.part-{shard_index:05d}.jsonl.gz"; shard_paths.append(p)
                current=gzip.open(p,"wt",encoding="utf-8",newline="\n")
            def emit(text,source_row,extra=None):
                nonlocal scanned,admitted,duplicates,short,current_count
                scanned+=1; body=str(text or "").strip()
                if len(body)<int(m.get("min_text_chars",40)): short+=1; return
                key=hashlib.sha256(re.sub(r"\s+"," ",body).casefold().encode("utf-8")).hexdigest()
                if key in seen: duplicates+=1; return
                seen.add(key)
                rec={"id":f"{slug}:{source_row}:{key[:12]}","text":body,"domain":m["domain"],"language":"es","split":"train",
                  "train_eligible":True,"admission_status":"accepted","synthetic":bool(m.get("synthetic",False)),
                  "license":m["license"],"source_dataset":m["name"],"source":m["doi"],
                  "source_revision":str(record.get("id"))+":"+str(metadata.get("version","")),"source_row":source_row,
                  "attribution":m["attribution"],"task":m.get("task","language modeling"),"metadata":extra or {}}
                line=json.dumps(rec,ensure_ascii=False,separators=(",",":"),default=str)+"\n"
                if current is None or current_count>=shard_rows: new_shard()
                current.write(line); digest.update(line.encode()); admitted+=1; current_count+=1
            fmt=m["format"]
            if fmt=="txt_lines":
                with tmp.open("r",encoding=m.get("encoding","utf-8"),errors="replace") as src:
                    for i,line in enumerate(src): emit(line,i)
            elif fmt=="zip_txt":
                with zipfile.ZipFile(tmp) as z:
                    for name in sorted(z.namelist()):
                        if not name.lower().endswith((".txt",".tsv",".csv",".xml",".conll",".ann")): continue
                        with z.open(name) as raw:
                            for i,line in enumerate(raw): emit(line.decode(m.get("encoding","utf-8"),errors="replace"),f"{name}:{i}",{"file":name})
            elif fmt=="jsonl":
                with tmp.open("r",encoding=m.get("encoding","utf-8"),errors="replace") as src:
                    for i,line in enumerate(src):
                        if not line.strip(): continue
                        row=json.loads(line); fields=m.get("text_fields",[])
                        body="\n".join(list(text_values([row.get(k) for k in fields])) if fields else list(text_values(row)))
                        emit(body,i,{k:v for k,v in row.items() if k not in fields and isinstance(v,(str,int,float,bool,list,tuple))})
            elif fmt=="csv":
                with tmp.open("r",encoding=m.get("encoding","utf-8"),errors="replace",newline="") as src:
                    for i,row in enumerate(csv.DictReader(src,delimiter=m.get("delimiter",","))):
                        body="\n".join(list(text_values([row.get(k) for k in m.get("text_fields",[])])))
                        emit(body,i,{k:v for k,v in row.items() if k not in m.get("text_fields",[])})
            else: raise ValueError(f"unsupported format {fmt}")
            if current is not None: current.close(); shard_counts.append(current_count); current=None
            if admitted<int(m.get("minimum_rows",1)): raise ValueError(f"too few admitted rows: {admitted}")
            hashes=[{"file":p.name,"sha256":hash_file(p),"rows":n} for p,n in zip(shard_paths,shard_counts)]
            result={"schema_version":1,"slug":slug,"dataset":m["name"],"record_id":record.get("id"),"doi":m["doi"],
              "source_revision":str(record.get("id"))+":"+str(metadata.get("version","")),"license":m["license"],"language":"es",
              "split":"train","source_file":source["key"],"source_file_size":source.get("size"),"source_file_sha256":source_sha,
              "rows_scanned":scanned,"rows_admitted":admitted,"duplicates_skipped":duplicates,"short_skipped":short,
              "files":[p.name for p in shard_paths],"file_hashes":hashes,"file":shard_paths[0].name,
              "sha256_jsonl_uncompressed":digest.hexdigest(),"retrieved_at_utc":datetime.now(timezone.utc).isoformat(),
              "attribution":m["attribution"]}
            mout.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            reports.append({"slug":slug,"status":"accepted","rows":admitted,"shards":len(shard_paths)})
        except Exception as e:
            if current is not None:
                try: current.close()
                except Exception: pass
            for p in shard_paths: p.unlink(missing_ok=True)
            mout.unlink(missing_ok=True); reports.append({"slug":slug,"status":"rejected_or_retry","reason":str(e)[:1000]})
            print(f"ZENODO_INTAKE_REJECTED {slug}: {e}",file=sys.stderr)
        finally: tmp.unlink(missing_ok=True)
    report_dir=Path("data/intake-reports"); report_dir.mkdir(parents=True,exist_ok=True)
    (report_dir/"zenodo-intake-report.json").write_text(json.dumps(reports,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(reports,ensure_ascii=False))
if __name__=="__main__": main()
