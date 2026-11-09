#!/usr/bin/env python3
"""Extract train-eligible ESQAD Spanish QA records with provenance and dedup."""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re,zipfile
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

SOURCE="https://zenodo.org/records/16351733"
DOI="10.5281/zenodo.16351733"
LICENSE="CC BY 4.0"
FILES={
 "evau/docs/EvAU_QA.csv":("EVAU",False),
 "quijote/docs/Quijote_QA.csv":("Quijote",True),
 "legal_faqs/docs/Legal_QA.csv":("legal_faqs",True),
 "exams/exams_QA_validated.json":("exams_pilot",True),
}
def key(s): return re.sub(r"[^a-z0-9]","",str(s).casefold())
def pick(row,*names):
 d={key(k):v for k,v in row.items()}
 for n in names:
  if key(n) in d:return d[key(n)]
 return None
def records_from_json(data):
 obj=json.loads(data.decode("utf-8-sig"))
 if isinstance(obj,list): return obj
 if isinstance(obj,dict):
  for k in ("data","records","examples","questions","items"):
   if isinstance(obj.get(k),list): return obj[k]
  return [obj]
 raise ValueError("unsupported exams JSON structure")
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--zip",type=Path,required=True)
 ap.add_argument("--output-dir",type=Path,default=Path("data/curated/accepted"))
 args=ap.parse_args()
 raw=args.zip.read_bytes()
 archive_sha=hashlib.sha256(raw).hexdigest()
 z=zipfile.ZipFile(io.BytesIO(raw))
 out=args.output_dir/"esqad-spanish-qa-train.jsonl"
 args.output_dir.mkdir(parents=True,exist_ok=True)
 seen=set(); counts=Counter(); synthetics=Counter(); digest=hashlib.sha256(); rows=0
 with out.open("w",encoding="utf-8",newline="\n") as f:
  for path,(subset,synthetic) in FILES.items():
   matches=[n for n in z.namelist() if n.lower().endswith(path.lower())]
   if not matches: raise SystemExit(f"missing expected ESQAD member: {path}")
   member=matches[0]; payload=z.read(member)
   if member.lower().endswith(".csv"):
    text=payload.decode("utf-8-sig",errors="replace")
    try: dialect=csv.Sniffer().sniff(text[:100000],delimiters=",;\t")
    except csv.Error: dialect=csv.excel
    source_rows=list(csv.DictReader(io.StringIO(text),dialect=dialect))
   else: source_rows=records_from_json(payload)
   subset_rows=0
   for i,row in enumerate(source_rows,1):
    if not isinstance(row,dict): continue
    q=pick(row,"question","prompt","pregunta"); a=pick(row,"answer","response","respuesta")
    if not isinstance(q,str) or not isinstance(a,str) or not q.strip() or not a.strip(): continue
    q=q.strip(); a=a.strip()
    identity=hashlib.sha256((key(q)+"\n"+key(a)).encode()).hexdigest()
    if identity in seen: continue
    seen.add(identity)
    metadata={}
    for src,dst in (("subject","subject"),("difficulty","difficulty"),("chapter","chapter"),("law_reference","law_reference"),("intended_difficulty","intended_difficulty"),("perceived_difficulty","perceived_difficulty"),("clarity","clarity_rating"),("complexity","complexity_rating"),("pedagogical_value","pedagogical_value_rating")):
     v=pick(row,src)
     if v is not None and isinstance(v,(str,int,float,bool)): metadata[dst]=v
    record={"id":f"esqad:{subset}:{i}","question":q,"answer":a,"domain":"educación en español","language":"es","split":"train",
     "train_eligible":True,"admission_status":"accepted","synthetic":synthetic,"license":LICENSE,
     "source_dataset":"ESQAD","source":SOURCE,"doi":DOI,"source_file":member,"source_subset":subset,
     "source_row":i,"attribution":"Badenes-Olmedo, Chu-Artzt, Eyzaguirre-Barreda & Gayoso-Cabada (2025), ESQAD, Zenodo DOI 10.5281/zenodo.16351733, CC BY 4.0.",
     "metadata":metadata}
    line=json.dumps(record,ensure_ascii=False,separators=(",",":"))+"\n"
    f.write(line); digest.update(line.encode()); rows+=1; subset_rows+=1
   counts[subset]=subset_rows; synthetics["synthetic" if synthetic else "human_curated"]+=subset_rows
 if rows<100: raise SystemExit(f"too few valid ESQAD QAs: {rows}")
 manifest={"schema_version":1,"dataset":"ESQAD Spanish educational question-answer data","source":SOURCE,"doi":DOI,
  "license":LICENSE,"language":"es","source_archive":"QAG_Spanish_ExpertSystems_v1.0.zip","source_archive_sha256":archive_sha,
  "record_count":rows,"unique_question_answer_pairs":len(seen),"subset_counts":dict(counts),
  "synthetic_and_human_curated_counts":dict(synthetics),"included_files":list(FILES),
  "excluded_fields":["free-text reviewer comments","personal names/contact fields"],"file":out.name,
  "sha256_jsonl":digest.hexdigest(),"retrieved_at_utc":datetime.now(timezone.utc).isoformat(),
  "admission_status":"accepted train-only; no benchmark holdout included",
  "limitations":["Quijote, legal FAQ and pilot QAG are marked synthetic/generated as described by the source.",
   "EVAU is manually curated; source QA pairs retain subject and difficulty where present.",
   "Only question-answer pairs are imported; source documents and free-text reviewer comments are not copied.",
   "Deduplication is exact after casefolding and punctuation/whitespace normalization."]}
 (args.output_dir/"esqad-spanish-qa-train.manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({k:manifest[k] for k in ("record_count","subset_counts","synthetic_and_human_curated_counts","source_archive_sha256","sha256_jsonl")},ensure_ascii=False))
if __name__=="__main__": main()
