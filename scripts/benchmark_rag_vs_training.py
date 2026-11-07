#!/usr/bin/env python3
"""Controlled MINIRONIN comparison: direct generation vs semantic retrieval + same checkpoint."""
from __future__ import annotations
import argparse, hashlib, json, struct, sys, time
from datetime import datetime, timezone
from pathlib import Path
import torch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src")); sys.path.insert(0,str(ROOT/"scripts"))
from minironin import MiniRoninLM, ModelConfig
from train_long_run import load_training_data
ACTIVE_VOCAB=257; EOS_ID=256
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
CHUNK_CHARS=1200; CHUNK_OVERLAP=180; TOP_K=3; MAX_CONTEXT_CHARS=180

def sha256_file(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
 return h.hexdigest()

def split_chunks(text,size=CHUNK_CHARS,overlap=CHUNK_OVERLAP):
 text=" ".join(text.split())
 if not text:return []
 step=size-overlap
 return [text[i:i+size] for i in range(0,len(text),step) if len(text[i:i+size])>=120]

def load_questions(path):
 rows=[json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]
 ids=[r["id"] for r in rows]
 if len(ids)!=len(set(ids)): raise ValueError("Duplicate holdout IDs")
 return rows

def build_index(train_docs,embedder,out,batch_size=128):
 import numpy as np
 out.mkdir(parents=True,exist_ok=True); mp=out/"chunks.jsonl"; vp=out/"embeddings.float16"; op=out/"offsets.uint64"
 total=0; pending=[]; metadata=[]; dim=embedder.get_sentence_embedding_dimension()
 with mp.open("w",encoding="utf-8") as meta, vp.open("wb") as vectors, op.open("wb") as offsets:
  for domain in sorted(train_docs):
   for doc in train_docs[domain]:
    for i,chunk in enumerate(split_chunks(doc["text"])):
     pending.append(chunk); metadata.append({"domain":domain,"source":doc.get("source","unknown"),"source_file":doc.get("source_file","unknown"),"document_sha256":doc.get("sha256",""),"chunk_index":i,"text":chunk})
     if len(pending)>=batch_size:
      emb=embedder.encode(pending,convert_to_numpy=True,normalize_embeddings=True,show_progress_bar=False)
      vectors.write(np.asarray(emb,dtype=np.float16).tobytes())
      for row in metadata:
        offsets.write(struct.pack("<Q",meta.tell()))
        meta.write(json.dumps(row,ensure_ascii=False)+"\n")
      total+=len(pending); pending=[]; metadata=[]
  if pending:
   emb=embedder.encode(pending,convert_to_numpy=True,normalize_embeddings=True,show_progress_bar=False)
   vectors.write(np.asarray(emb,dtype=np.float16).tobytes())
   for row in metadata:
        offsets.write(struct.pack("<Q",meta.tell()))
        meta.write(json.dumps(row,ensure_ascii=False)+"\n")
   total+=len(pending)
 if not total: raise RuntimeError("No eligible training chunks indexed")
 return {"chunks":total,"dimension":dim,"embedding_dtype":"float16","metadata":str(mp),"vectors":str(vp),"offsets":str(op)}

def retrieve(query,embedder,index_dir,info,top_k):
 import numpy as np
 q=embedder.encode([query],convert_to_numpy=True,normalize_embeddings=True)[0].astype(np.float32)
 dim,count=int(info["dimension"]),int(info["chunks"])
 matrix=np.memmap(index_dir/"embeddings.float16",dtype=np.float16,mode="r",shape=(count,dim))
 best_s=np.full(top_k,-np.inf,dtype=np.float32); best_i=np.full(top_k,-1,dtype=np.int64)
 for start in range(0,count,32768):
  end=min(count,start+32768); scores=np.asarray(matrix[start:end],dtype=np.float32)@q
  take=min(top_k,len(scores)); local=np.argpartition(scores,-take)[-take:]
  merged_s=np.concatenate((best_s,scores[local])); merged_i=np.concatenate((best_i,local+start))
  keep=np.argpartition(merged_s,-top_k)[-top_k:]; best_s,best_i=merged_s[keep],merged_i[keep]
 wanted={int(best_i[i]):float(best_s[i]) for i in np.argsort(best_s)[::-1] if best_i[i]>=0}
 results=[]
 offsets=np.memmap(index_dir/"offsets.uint64",dtype=np.uint64,mode="r",shape=(count,))
 with (index_dir/"chunks.jsonl").open(encoding="utf-8") as stream:
  for n,score in wanted.items():
   stream.seek(int(offsets[n])); row=json.loads(stream.readline())
   row["cosine_similarity"]=score; results.append(row)
 return sorted(results,key=lambda x:x["cosine_similarity"],reverse=True)

def generate(model,prompt,max_new):
 encoded=list(prompt.encode("utf-8",errors="replace")); generated=[]
 for _ in range(max_new):
  ids=torch.tensor([encoded[-model.config.context_length:]],dtype=torch.long)
  logits,_=model(ids,vocab_limit=ACTIVE_VOCAB); token=int(torch.argmax(logits[0,-1]).item())
  if token==EOS_ID:break
  generated.append(token); encoded.append(token)
 return bytes(generated).decode("utf-8",errors="replace").strip(),generated

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--heretic-root",type=Path,required=True); p.add_argument("--books-root",type=Path,required=True)
 p.add_argument("--checkpoint",type=Path,required=True); p.add_argument("--holdout",type=Path,default=ROOT/"benchmarks/inference-holdout-v1.jsonl")
 p.add_argument("--output",type=Path,default=ROOT/"rag-benchmark"); p.add_argument("--cache",type=Path,default=ROOT/"rag-benchmark/full-corpus-cache.pt")
 p.add_argument("--threads",type=int,default=2); p.add_argument("--max-new-tokens",type=int,default=128); p.add_argument("--top-k",type=int,default=TOP_K)
 a=p.parse_args(); torch.set_num_threads(a.threads); torch.use_deterministic_algorithms(True); a.output.mkdir(parents=True,exist_ok=True)
 train_docs,_,_,_,manifest=load_training_data(a.heretic_root,a.books_root,a.cache)
 from sentence_transformers import SentenceTransformer
 embedder=SentenceTransformer(EMBEDDING_MODEL,device="cpu"); index_dir=a.output/"semantic-index"
 info=build_index(train_docs,embedder,index_dir)
 config=ModelConfig.load(ROOT/"configs/model-10m.json"); model=MiniRoninLM(config).cpu()
 cp=torch.load(a.checkpoint,map_location="cpu",weights_only=False)
 from dataclasses import asdict
 if cp.get("active_vocabulary")!=ACTIVE_VOCAB or cp.get("parameter_count")!=model.parameter_count(): raise SystemExit("Checkpoint architecture/vocabulary mismatch")
 if cp.get("model_config")!=asdict(config): raise SystemExit("Checkpoint config mismatch")
 model.load_state_dict(cp["model_state_dict"],strict=True); model.eval()
 results=[]
 with torch.inference_mode():
  for row in load_questions(a.holdout):
   question=row["question"].strip(); started=time.perf_counter()
   direct,direct_ids=generate(model,question+"\nRespuesta:",a.max_new_tokens); direct_time=time.perf_counter()-started
   started=time.perf_counter(); hits=retrieve(question,embedder,index_dir,info,a.top_k); retrieval_time=time.perf_counter()-started
   context="\n".join(x["text"][:MAX_CONTEXT_CHARS] for x in hits)
   prompt=("Contexto recuperado:\n"+context+"\nPregunta: "+question+"\nResponde usando el contexto cuando sea pertinente. Si no basta, dilo.\nRespuesta:")
   started=time.perf_counter(); rag,rag_ids=generate(model,prompt,a.max_new_tokens); rag_time=time.perf_counter()-started
   results.append({"id":row["id"],"domain":row["domain"],"question":question,"rubric":row["rubric"],
    "direct":{"answer":direct,"generated_bytes":len(direct_ids),"seconds":round(direct_time,6)},
    "rag":{"answer":rag,"generated_bytes":len(rag_ids),"retrieval_seconds":round(retrieval_time,6),"generation_seconds":round(rag_time,6)},
    "retrieved":[{"source":x["source"],"source_file":x["source_file"],"domain":x["domain"],"score":round(x["cosine_similarity"],6),"text":x["text"]} for x in hits]})
   print(json.dumps({"id":row["id"],"top_score":hits[0]["cosine_similarity"] if hits else None}),flush=True)
 summary={"schema_version":1,"experiment":"MINIRONIN direct-vs-semantic-RAG controlled comparison","created_at_utc":datetime.now(timezone.utc).isoformat(),
  "checkpoint_sha256":sha256_file(a.checkpoint),"holdout_sha256":sha256_file(a.holdout),"holdout_count":len(results),
  "parameter_count":model.parameter_count(),"active_vocabulary":ACTIVE_VOCAB,"embedding_model":EMBEDDING_MODEL,"embedding_dimension":info["dimension"],
  "index":info,"indexed_domains":sorted(train_docs),"corpus_manifest_summary":{k:manifest.get(k) for k in ("documents_total","documents_by_domain","heretic_ingested_files","behavior_examples")},
  "protocol":{"same_checkpoint":True,"same_greedy_decoder":True,"rag_top_k":a.top_k,"chunk_chars":CHUNK_CHARS,"chunk_overlap":CHUNK_OVERLAP,"max_context_chars_per_hit":MAX_CONTEXT_CHARS,"index_uses_training_split_only":True,"holdout_used_for_index":False},
  "scoring":{"status":"unscored_blind_review_required","note":"Cosine similarity is not answer correctness; paired direct/RAG answers require human blind scoring."},"results":results}
 target=a.output/"direct-vs-rag.json"; target.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"output":str(target),"holdout_count":len(results),"index_chunks":info["chunks"],"checkpoint_sha256":summary["checkpoint_sha256"]}))

if __name__=="__main__":main()
