#!/usr/bin/env python3
"""Stream complete, license-checked Zenodo Spanish corpora into accepted JSONL.gz."""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,re,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path
import requests

def norm(x): return str(x or "").casefold().replace("_","-").replace(" ","-").strip()
def text_values(value):
    if isinstance(value,str):
        if value.strip(): yield value.strip()
    elif isinstance(value,dict):
        for k,v in value.items():
            if k.casefold() not in {"id","url","path","metadata","audio","image"}: yield from text_values(v)
    elif isinstance(value,(list,tuple)):
        for v in value: yield from text_values(v)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest-dir",default="data/curated/zenodo-intake-manifests")
    ap.add_argument("--output-dir",default="data/curated/accepted")
    args=ap.parse_args()
    outdir=Path(args.output_dir); outdir.mkdir(parents=True,exist_ok=True)
    reports=[]
    for mp in sorted(Path(args.manifest_dir).glob("*.json")):
        m=json.loads(mp.read_text(encoding="utf-8")); slug=m["slug"]
        out=outdir/f"{slug}.jsonl.gz"; mout=outdir/f"{slug}.manifest.json"
        if out.exists() and mout.exists():
            reports.append({"slug":slug,"status":"already_imported"}); continue
        tmp=Path("/tmp")/f"{slug}.source"
        try:
            response=requests.get(f"https://zenodo.org/api/records/{m['record_id']}",timeout=90)
            response.raise_for_status(); record=response.json()
            metadata=record.get("metadata",{})
            lic=metadata.get("license") or {}
            actual=norm(lic.get("id") if isinstance(lic,dict) else lic)
            expected=norm(m["license_id"])
            if actual!=expected: raise ValueError(f"license mismatch: expected={expected}, actual={actual}")
            candidates=[f for f in record.get("files",[]) if re.search(m["file_regex"],f["key"],re.I)]
            if len(candidates)!=1: raise ValueError(f"expected one source file matching {m['file_regex']}, found {[x['key'] for x in candidates]}")
            source=candidates[0]; url=source.get("links",{}).get("self")
            if not url: raise ValueError("Zenodo source file has no download URL")
            with requests.get(url,stream=True,timeout=(60,300)) as r:
                r.raise_for_status()
                with tmp.open("wb") as f:
                    for block in r.iter_content(1024*1024):
                        if block: f.write(block)
            source_digest=hashlib.sha256()
            with tmp.open("rb") as source_stream:
                for block in iter(lambda:source_stream.read(1024*1024),b""): source_digest.update(block)
            source_sha=source_digest.hexdigest()
            digest=hashlib.sha256(); seen=set(); scanned=admitted=duplicates=short=0
            def emit(text,source_row,extra=None):
                nonlocal scanned,admitted,duplicates,short
                scanned+=1
                body=str(text or "").strip()
                if len(body)<int(m.get("min_text_chars",40)): short+=1; return None
                key=hashlib.sha256(re.sub(r"\\s+"," ",body).casefold().encode("utf-8")).hexdigest()
                if key in seen: duplicates+=1; return None
                seen.add(key)
                return {"id":f"{slug}:{source_row}:{key[:12]}","text":body,"domain":m["domain"],
                  "language":"es","split":"train","train_eligible":True,"admission_status":"accepted",
                  "synthetic":bool(m.get("synthetic",False)),"license":m["license"],
                  "source_dataset":m["name"],"source":m["doi"],"source_revision":str(record.get("id"))+":"+str(metadata.get("version","")),
                  "source_row":source_row,"attribution":m["attribution"],"task":m.get("task","language modeling"),
                  "metadata":extra or {}}
            with gzip.open(out,"wt",encoding="utf-8",newline="\\n") as f:
                def write_record(text,idx,extra=None):
                    nonlocal admitted
                    rec=emit(text,idx,extra)
                    if rec is None: return
                    line=json.dumps(rec,ensure_ascii=False,separators=(",",":"),default=str)+"\\n"
                    f.write(line); digest.update(line.encode()); admitted+=1
                fmt=m["format"]
                if fmt=="txt_lines":
                    with tmp.open("r",encoding=m.get("encoding","utf-8"),errors="replace") as src:
                        for i,line in enumerate(src): write_record(line,i)
                elif fmt=="zip_txt":
                    with zipfile.ZipFile(tmp) as z:
                        for name in sorted(z.namelist()):
                            if not name.lower().endswith((".txt",".tsv",".csv",".xml",".conll",".ann")): continue
                            with z.open(name) as raw:
                                for i,line in enumerate(raw):
                                    write_record(line.decode(m.get("encoding","utf-8"),errors="replace"),f"{name}:{i}",{"file":name})
                elif fmt=="jsonl":
                    with tmp.open("r",encoding=m.get("encoding","utf-8"),errors="replace") as src:
                        for i,line in enumerate(src):
                            if not line.strip(): continue
                            row=json.loads(line); fields=m.get("text_fields",[])
                            body="\\n".join(list(text_values([row.get(k) for k in fields])) if fields else list(text_values(row)))
                            write_record(body,i,{k:v for k,v in row.items() if k not in fields and isinstance(v,(str,int,float,bool,list,tuple))})
                elif fmt=="csv":
                    with tmp.open("r",encoding=m.get("encoding","utf-8"),errors="replace",newline="") as src:
                        reader=csv.DictReader(src,delimiter=m.get("delimiter",","))
                        for i,row in enumerate(reader):
                            body="\\n".join(list(text_values([row.get(k) for k in m.get("text_fields",[])])))
                            write_record(body,i,{k:v for k,v in row.items() if k not in m.get("text_fields",[])})
                else: raise ValueError(f"unsupported format {fmt}")
            if admitted<int(m.get("minimum_rows",1)):
                out.unlink(missing_ok=True); raise ValueError(f"too few admitted rows: {admitted}")
            file_hash=hashlib.sha256()
            with out.open("rb") as raw:
                for block in iter(lambda:raw.read(1024*1024),b""): file_hash.update(block)
            result={"schema_version":1,"slug":slug,"dataset":m["name"],"record_id":record.get("id"),
              "doi":m["doi"],"source_revision":str(record.get("id"))+":"+str(metadata.get("version","")),
              "license":m["license"],"language":"es","split":"train","source_file":source["key"],
              "source_file_size":source.get("size"),"source_file_sha256":source_sha,"rows_scanned":scanned,
              "rows_admitted":admitted,"duplicates_skipped":duplicates,"short_skipped":short,
              "file":out.name,"sha256_jsonl":file_hash.hexdigest(),"sha256_uncompressed_content":digest.hexdigest(),
              "retrieved_at_utc":datetime.now(timezone.utc).isoformat(),"attribution":m["attribution"]}
            mout.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
            reports.append({"slug":slug,"status":"accepted","rows":admitted,"sha256":file_hash.hexdigest()})
        except Exception as e:
            reports.append({"slug":slug,"status":"rejected_or_retry","reason":str(e)[:1000]})
            print(f"ZENODO_INTAKE_REJECTED {slug}: {e}",file=sys.stderr)
        finally:
            tmp.unlink(missing_ok=True)
    report_dir=Path("data/intake-reports"); report_dir.mkdir(parents=True,exist_ok=True)
    (report_dir/"zenodo-intake-report.json").write_text(json.dumps(reports,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
    print(json.dumps(reports,ensure_ascii=False))
if __name__=="__main__": main()
