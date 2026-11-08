#!/usr/bin/env python3
"""Reproducible provenance-preserving RAG index: SQLite FTS5 + optional multilingual vectors."""
from __future__ import annotations
import argparse,csv,hashlib,json,re,sqlite3,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FIELDS=("text","content","body","document","passage","question","answer","context","prompt","completion","response","title","summary","abstract")
def sha(b):return hashlib.sha256(b).hexdigest()
def clean(s):
 s=s.replace("\x00"," ");s=re.sub(r"[ \t]+"," ",s);s=re.sub(r"\n{3,}","\n\n",s);return s.strip()
def extract(v,depth=0):
 if depth>5:return ""
 if isinstance(v,str):return v
 if isinstance(v,(int,float,bool)):return str(v)
 if isinstance(v,list):return "\n".join(filter(None,(extract(x,depth+1) for x in v)))
 if isinstance(v,dict):
  keys=[k for k in FIELDS if k in v];out=[]
  for k in keys:
   x=extract(v[k],depth+1)
   if x:out.append(f"{k}: {x}")
  if not out:
   out=[f"{k}: {x}" for k,x in v.items() if isinstance(x,(str,int,float)) and k.lower() not in {"id","sha256","url","license","source_file"}]
  return "\n".join(out)
 return ""
def read(path):
 ext=path.suffix.lower()
 try:
  if ext in {".md",".txt",".rst",".yaml",".yml",".xml",".html",".htm"}:
   raw=path.read_text(encoding="utf-8",errors="replace")
   if ext in {".html",".htm"}:
    from html.parser import HTMLParser
    class P(HTMLParser):
     def __init__(self):super().__init__();self.parts=[]
     def handle_data(self,d):self.parts.append(d)
    p=P();p.feed(raw);raw="\n".join(p.parts)
   yield clean(raw),"text"
  elif ext==".jsonl":
   with path.open(encoding="utf-8",errors="replace") as f:
    for n,line in enumerate(f,1):
     if line.strip():
      try:x=clean(extract(json.loads(line)))
      except json.JSONDecodeError:continue
      if x:yield x,f"jsonl:{n}"
  elif ext==".json":
   x=clean(extract(json.loads(path.read_text(encoding="utf-8",errors="replace"))))
   if x:yield x,"json"
  elif ext in {".csv",".tsv"}:
   with path.open(encoding="utf-8",errors="replace",newline="") as f:
    for n,row in enumerate(csv.DictReader(f,delimiter="\t" if ext==".tsv" else ","),1):
     x=clean("\n".join(f"{k}: {v}" for k,v in row.items() if v not in (None,"")))
     if x:yield x,f"row:{n}"
  elif ext==".pdf":
   import fitz
   doc=fitz.open(path)
   for n,page in enumerate(doc,1):
    x=clean(page.get_text())
    if x:yield x,f"page:{n}"
  elif ext==".docx":
   from docx import Document
   x=clean("\n".join(p.text for p in Document(path).paragraphs))
   if x:yield x,"docx"
 except (OSError,UnicodeError,json.JSONDecodeError,ImportError) as e:print(f"WARN {path}: {e}",file=sys.stderr)
def chunk(text,target,overlap,minimum):
 paras=[x.strip() for x in re.split(r"\n\s*\n",text) if x.strip()];out=[];cur=""
 for para in paras:
  while len(para)>target:
   if cur:out.append(cur);cur=""
   cut=para.rfind(" ",0,target)
   if cut<minimum:cut=target
   out.append(para[:cut].strip());para=para[max(1,cut-overlap):].strip()
  cand=(cur+"\n\n"+para).strip()
  if len(cand)>target and cur:out.append(cur);cur=para
  else:cur=cand
 if cur:out.append(cur)
 result=[]
 for x in out:
  if len(x)<minimum and result:result[-1]=(result[-1]+"\n\n"+x)[:target+overlap]
  elif len(x)>=minimum:result.append(x)
 return result
def excluded(p,reg):
 parts={x.lower() for x in p.parts}
 return bool(parts.intersection(reg["excluded_path_parts"])) or p.suffix.lower() in reg["excluded_extensions"]
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--registry",type=Path,default=ROOT/"data/rag/sources.json");ap.add_argument("--output",type=Path,default=ROOT/"artifacts/rag/minironin-rag.sqlite");ap.add_argument("--root",action="append",default=[],help="Approved extra root NAME=PATH");ap.add_argument("--no-embeddings",action="store_true");ap.add_argument("--batch-size",type=int,default=64);a=ap.parse_args()
 reg=json.loads(a.registry.read_text());cfg=reg["chunking"];ecfg=reg["embedding"];embedder=None
 if not a.no_embeddings:
  try:
   from sentence_transformers import SentenceTransformer
   embedder=SentenceTransformer(ecfg["model"],device="cpu")
  except ImportError:raise SystemExit("Install requirements-rag.txt or use --no-embeddings")
 roots=[(s,ROOT/s["root"]) for s in reg["sources"] if s.get("enabled")]
 for item in a.root:
  if "=" not in item:raise SystemExit("--root expects NAME=PATH")
  name,path=item.split("=",1);roots.append(({"id":name,"project":"external","domain":"inherited","language":"und","epistemic":"source-specific","license":"preserve-upstream","redistribution":False},Path(path).resolve()))
 a.output.parent.mkdir(parents=True,exist_ok=True)
 if a.output.exists():a.output.unlink()
 db=sqlite3.connect(a.output);db.execute("PRAGMA journal_mode=WAL");db.executescript("""
 CREATE TABLE documents(document_id TEXT PRIMARY KEY,source_id TEXT,project TEXT,relative_path TEXT,document_sha256 TEXT,license TEXT,domain TEXT,language TEXT,epistemic TEXT,redistribution INTEGER,locator TEXT);
 CREATE TABLE document_sources(document_id TEXT,source_id TEXT,project TEXT,relative_path TEXT,license TEXT,domain TEXT,language TEXT,epistemic TEXT,redistribution INTEGER,PRIMARY KEY(document_id,source_id,relative_path));\n CREATE TABLE chunks(chunk_id TEXT PRIMARY KEY,document_id TEXT,chunk_index INTEGER,locator TEXT,text TEXT,text_sha256 TEXT UNIQUE,embedding BLOB,embedding_model TEXT);
 CREATE VIRTUAL TABLE chunks_fts USING fts5(chunk_id UNINDEXED,text,tokenize='unicode61 remove_diacritics 2');
 CREATE INDEX idx_chunks_doc ON chunks(document_id);\n CREATE TABLE chunk_sources(chunk_id TEXT,document_id TEXT,source_id TEXT,relative_path TEXT,locator TEXT,PRIMARY KEY(chunk_id,document_id,source_id,relative_path,locator));""")
 pending=[];docs=dupd=chunks=dupc=0;t0=time.time()
 def flush():
  nonlocal chunks,dupc
  if not pending:return
  vec=None
  if embedder:
   import numpy as np
   vec=embedder.encode([ecfg["document_prefix"]+r[4] for r in pending],batch_size=a.batch_size,convert_to_numpy=True,normalize_embeddings=True,show_progress_bar=False)
  for i,(cid,did,ix,loc,txt,th,source_id,relative_path) in enumerate(pending):
   blob=vec[i].astype("float16").tobytes() if vec is not None else None
   cur=db.execute("INSERT OR IGNORE INTO chunks VALUES(?,?,?,?,?,?,?,?)",(cid,did,ix,loc,txt,th,blob,ecfg["model"] if blob is not None else None))
   if cur.rowcount:
    actual_cid=cid
    db.execute("INSERT INTO chunks_fts(chunk_id,text) VALUES(?,?)",(cid,txt));chunks+=1
   else:
    dupc+=1
    actual_cid=db.execute("SELECT chunk_id FROM chunks WHERE text_sha256=?",(th,)).fetchone()[0]
   db.execute("INSERT OR IGNORE INTO chunk_sources VALUES(?,?,?,?,?)",(actual_cid,did,source_id,relative_path,loc))
  db.commit();pending.clear()
 for src,base in roots:
  if not base.exists():print(f"WARN missing source {src['id']}: {base}",file=sys.stderr);continue
  files=[base] if base.is_file() else sorted(base.rglob("*"))
  for path in files:
   if not path.is_file() or excluded(path,reg) or path.suffix.lower() not in reg["allowed_extensions"]:continue
   low=str(path).replace("\\","/").lower()
   if any(x in low for x in ("/holdout/","/validation/","/eval/","/evaluation/","/checkpoints/")):continue
   try:
    if path.stat().st_size>reg.get("max_file_mb",100)*1024*1024:continue
    raw=path.read_bytes();dh=sha(raw);did=dh;rel=str(path.relative_to(base)) if base.is_dir() else path.name
    cur=db.execute("INSERT OR IGNORE INTO documents VALUES(?,?,?,?,?,?,?,?,?,?,?)",(did,src["id"],src.get("project","unknown"),rel,dh,src.get("license","unknown"),src.get("domain","unknown"),src.get("language","und"),src.get("epistemic","unknown"),int(bool(src.get("redistribution",False))),""))
    if cur.rowcount:docs+=1
    else:dupd+=1
    db.execute("INSERT OR IGNORE INTO document_sources VALUES(?,?,?,?,?,?,?,?,?)",(did,src["id"],src.get("project","unknown"),rel,src.get("license","unknown"),src.get("domain","unknown"),src.get("language","und"),src.get("epistemic","unknown"),int(bool(src.get("redistribution",False)))))
    file_chunk_idx=0
    for loc,txt in read(path):
     for chunk_text in chunk(txt,cfg["target_chars"],cfg["overlap_chars"],cfg["min_chars"]):
      ix=file_chunk_idx;file_chunk_idx+=1;th=sha(chunk_text.encode());cid=sha((did+":"+str(ix)+":"+th).encode());pending.append((cid,did,ix,loc,chunk_text,th,src["id"],rel))
      if len(pending)>=a.batch_size:flush()
   except OSError as e:print(f"WARN skipped {path}: {e}",file=sys.stderr)
 flush()
 db.execute("CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT)")
 manifest={"schema_version":1,"registry_sha256":sha(a.registry.read_bytes()),"embedding_model":ecfg["model"] if embedder else None,"embedding_dimension":embedder.get_sentence_embedding_dimension() if embedder else None,"documents_unique":docs,"duplicate_document_occurrences":dupd,"chunks_unique":chunks,"duplicate_chunks_skipped":dupc,"sources":[{"id":s["id"],"path":str(p),"exists":p.exists()} for s,p in roots],"elapsed_seconds":round(time.time()-t0,2),"training_performed":False,"holdout_read":False}
 db.execute("INSERT INTO metadata VALUES('manifest',?)",(json.dumps(manifest,ensure_ascii=False),));db.commit();db.close();print(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
