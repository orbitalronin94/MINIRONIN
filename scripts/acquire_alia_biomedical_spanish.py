#!/usr/bin/env python3
"""Stream and shard the licensed ALIA Spanish Biomedical Corpus."""
from __future__ import annotations
import argparse,gzip,hashlib,json,re,sqlite3
from datetime import datetime,timezone
from pathlib import Path
from datasets import load_dataset
from huggingface_hub import HfApi

REPO="SINAI/ALIA-es-biomedical"
SOURCE="https://huggingface.co/datasets/SINAI/ALIA-es-biomedical"
LICENSE="CC BY-SA 4.0"
def sha_file(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,default=Path("out"))
    ap.add_argument("--shard-rows",type=int,default=25000)
    args=ap.parse_args()
    if args.shard_rows<1000:raise SystemExit("shard size too small")
    info=HfApi().dataset_info(REPO)
    card=info.card_data
    declared=getattr(card,"license",None) if card else None
    if str(declared).casefold().replace("_","-") not in {"cc-by-sa-4.0","cc-by-sa"}:
        raise SystemExit(f"license mismatch: {declared!r}")
    revision=info.sha
    ds=load_dataset(REPO,split="train",revision=revision,streaming=True)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(args.output_dir/"dedup.sqlite")
    db.execute("CREATE TABLE IF NOT EXISTS seen (h TEXT PRIMARY KEY)")
    files=[];shard_counts=[];current=None;current_count=0;idx=0
    output_digest=hashlib.sha256();scanned=admitted=short=duplicates=nontext=0
    def start_shard():
        nonlocal current,current_count,idx
        if current is not None:
            current.close();shard_counts.append(current_count)
        idx+=1;current_count=0
        p=args.output_dir/f"alia-biomedical-es-part-{idx:05d}.jsonl.gz"
        files.append(p)
        current=gzip.open(p,"wt",encoding="utf-8",newline="\n",compresslevel=6)
    for i,row in enumerate(ds):
        scanned+=1
        text=row.get("text")
        if not isinstance(text,str) or len(text.strip())<200:
            if not isinstance(text,str):nontext+=1
            else:short+=1
            continue
        text=text.strip()
        h=hashlib.sha256(re.sub(r"\s+"," ",text).casefold().encode("utf-8")).hexdigest()
        try:db.execute("INSERT INTO seen(h) VALUES (?)",(h,))
        except sqlite3.IntegrityError:
            duplicates+=1;continue
        source_id=str(row.get("source_id") or "ALIA biomedical")
        rec={"id":f"alia-biomedical-es:{row.get('id',i)}","text":text,
             "domain":"biomedicina, salud pública y documentación científica",
             "language":"es","split":"train","train_eligible":True,
             "admission_status":"accepted","synthetic":False,"license":LICENSE,
             "source_dataset":REPO,"source":SOURCE,"source_revision":revision,
             "source_id":source_id,"classes":row.get("classes"),
             "attribution":"SINAI Research Group, Universidad de Jaén; ALIA Spanish Biomedical Corpus; CC BY-SA 4.0."}
        line=json.dumps(rec,ensure_ascii=False,separators=(",",":"),default=str)+"\n"
        if current is None or current_count>=args.shard_rows:start_shard()
        current.write(line);output_digest.update(line.encode("utf-8"))
        admitted+=1;current_count+=1
        if admitted%100000==0:
            db.commit()
            print(json.dumps({"progress_rows":admitted,"source_rows_scanned":scanned}),flush=True)
    if current is not None:
        current.close();shard_counts.append(current_count)
    db.commit();db.close()
    if admitted<5_000_000:raise SystemExit(f"admission below safety floor: {admitted}; scanned={scanned}")
    hashes=[]
    for p,n in zip(files,shard_counts):
        hashes.append({"file":p.name,"rows":n,"sha256_gzip":sha_file(p),"bytes":p.stat().st_size})
    manifest={"schema_version":1,"dataset":"ALIA Spanish Biomedical Corpus",
      "source_dataset":REPO,"source_url":SOURCE,"source_revision":revision,
      "license":LICENSE,"license_scope":"dataset-level; verified against immutable dataset card",
      "language":"es","split":"train","domain":"biomedicina, salud pública y documentación científica",
      "source_rows_scanned":scanned,"rows_admitted":admitted,"rows_skipped_short":short,
      "rows_skipped_nontext":nontext,"rows_skipped_exact_duplicates":duplicates,
      "shard_rows":args.shard_rows,"files":hashes,"sha256_jsonl_uncompressed":output_digest.hexdigest(),
      "synthetic":False,"retrieved_at_utc":datetime.now(timezone.utc).isoformat(),
      "attribution":"SINAI Research Group, Universidad de Jaén; ALIA Spanish Biomedical Corpus; CC BY-SA 4.0.",
      "quality_note":"Upstream corpus documentation describes Spanish-language curation and removal of sensitive or identifiable information; source_id and class metadata are retained.",
      "limitations":["The upstream license is corpus-level CC BY-SA 4.0.","Source-level text quality and clinical coverage vary; original source_id is retained.","No generated or synthetic records are added."]}
    (args.output_dir/"alia-biomedical-es.manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"rows_scanned":scanned,"rows_admitted":admitted,"shards":len(files),
      "bytes_gzip":sum(x["bytes"] for x in hashes),"sha256_jsonl_uncompressed":output_digest.hexdigest()}),flush=True)
if __name__=="__main__":main()
