#!/usr/bin/env python3
"""BM25 + multilingual E5 reciprocal-rank fusion retrieval."""
import argparse,json,sqlite3
def search(path,query,k=5,model="intfloat/multilingual-e5-small"):
 db=sqlite3.connect(path);db.row_factory=sqlite3.Row;pool={}
 try:
  for rank,r in enumerate(db.execute("SELECT c.chunk_id,c.document_id,c.text,c.record_metadata FROM chunks_fts f JOIN chunks c ON c.chunk_id=f.chunk_id WHERE chunks_fts MATCH ? ORDER BY bm25(chunks_fts) LIMIT ?",(query,k*10)),1):
   pool[r["chunk_id"]]={"r":r,"score":1/(60+rank),"channels":["bm25"]}
 except sqlite3.OperationalError:pass
 try:
  import numpy as np
  from sentence_transformers import SentenceTransformer
  q=SentenceTransformer(model,device="cpu").encode(["query: "+query],normalize_embeddings=True,convert_to_numpy=True)[0].astype("float32")
  import heapq
  cursor=db.execute("SELECT chunk_id,document_id,text,record_metadata,embedding FROM chunks WHERE embedding IS NOT NULL AND embedding_model=?",(model,))
  heap=[];limit=k*10
  while True:
   batch=cursor.fetchmany(2048)
   if not batch:break
   matrix=np.stack([np.frombuffer(row["embedding"],dtype=np.float16).astype("float32") for row in batch])
   scores=matrix@q
   take=min(limit,len(batch))
   indices=np.argpartition(scores,-take)[-take:] if take else []
   for idx in indices:
    row=batch[int(idx)];item=(float(scores[idx]),row["chunk_id"],dict(row))
    if len(heap)<limit:heapq.heappush(heap,item)
    elif item>heap[0]:heapq.heapreplace(heap,item)
  for rank,(_,_,row) in enumerate(sorted(heap,reverse=True),1):
   x=pool.setdefault(row["chunk_id"],{"r":row,"score":0.0,"channels":[]});x["score"]+=1/(60+rank);x["channels"].append("vector")
 except (ImportError,RuntimeError,ValueError):pass
 out=[]
 for x in sorted(pool.values(),key=lambda z:z["score"],reverse=True)[:k]:
  r=x["r"];m=db.execute("SELECT * FROM documents WHERE document_id=?",(r["document_id"],)).fetchone()
  aliases=[dict(a) for a in db.execute("SELECT source_id,relative_path,locator FROM chunk_sources WHERE chunk_id=?",(r["chunk_id"],)).fetchall()]
  out.append({"chunk_id":r["chunk_id"],"text":r["text"],"record_metadata":json.loads(r["record_metadata"] or "{}"),"rrf_score":x["score"],"channels":x["channels"],"provenance":dict(m) if m else {},"all_source_locations":aliases})
 db.close();return out
def main():
 p=argparse.ArgumentParser();p.add_argument("query");p.add_argument("--index",default="artifacts/rag/minironin-rag.sqlite");p.add_argument("--top-k",type=int,default=5);a=p.parse_args();print(json.dumps(search(a.index,a.query,a.top_k),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
