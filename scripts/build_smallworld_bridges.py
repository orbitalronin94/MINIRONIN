#!/usr/bin/env python3
"""Generate reproducible sparse concept-bridge prompts; no factual answers are fabricated."""
import argparse,hashlib,json,random,re
from pathlib import Path
TOK=re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_-]{3,}")
STOP=set("para como sobre desde entre cuando donde porque tambien esto esta este that with from have which their there into would could should about using then than such more less some what when where while whose only also very much each other same these those being were been will shall must does your they them pero cada todo toda unos unas algo hacer puede pueden son han hay".split())
def terms(s):
 d={}
 for t in TOK.findall(s.lower()):
  if t not in STOP:d[t]=d.get(t,0)+1
 return [t for t,_ in sorted(d.items(),key=lambda x:(-x[1],x[0]))[:24]]
def main():
 p=argparse.ArgumentParser();p.add_argument("--input",action="append",required=True);p.add_argument("--output",default="artifacts/smallworld/teacher-prompts.jsonl");p.add_argument("--count",type=int,default=50000);p.add_argument("--seed",type=int,default=9417);a=p.parse_args();rng=random.Random(a.seed);pool=[]
 for name in a.input:
  for n,line in enumerate(Path(name).read_text(encoding="utf-8").splitlines(),1):
   try:o=json.loads(line)
   except json.JSONDecodeError:continue
   txt=" ".join(str(o.get(k,"")) for k in ("question","answer","context","text","content","prompt","response"));ts=terms(txt)
   if len(ts)>=3:pool.append({"file":name,"line":n,"id":o.get("id"),"domain":o.get("domain",o.get("tag","unknown")),"terms":ts})
 if len(pool)<3:raise SystemExit("Need at least three eligible source records")
 out=[];seen=set()
 for _ in range(a.count):
  x=rng.choice(pool);same=[z for z in pool if z is not x and z["domain"]==x["domain"]];candidates=same if len(same)>=2 else [z for z in pool if z is not x]
  y,z=rng.sample(candidates,2);nodes=[]
  for row in (x,y,z):
   choices=[t for t in row["terms"] if t not in nodes]
   if choices:nodes.append(rng.choice(choices))
  if len(nodes)<3 or tuple(nodes) in seen:continue
  seen.add(tuple(nodes));graph={"nodes":nodes,"edges":[[nodes[0],nodes[1]],[nodes[1],nodes[2]]],"routing":"sparse_random_same_domain"}
  prompt=("Conecta estos conceptos: "+", ".join(nodes)+". Define cada uno; construye un puente defendible (causal, funcional, analógico o de contraste); etiqueta explícitamente las analogías y no inventes hechos. Cierra con una observación irónica breve sin perder precisión.")
  out.append({"id":hashlib.sha256((str(a.seed)+"|".join(nodes)).encode()).hexdigest()[:20],"graph":graph,"prompt":prompt,"domain":x["domain"],"source_refs":[{"file":r["file"],"line":r["line"],"id":r["id"]} for r in (x,y,z)],"answer_status":"teacher_generation_required","epistemic":"synthetic_association_prompt","seed":a.seed})
 path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("w",encoding="utf-8") as f:
  for row in out:f.write(json.dumps(row,ensure_ascii=False)+"\\n")
 print(json.dumps({"prompts":len(out),"answers_generated":False,"seed":a.seed,"output":str(path)}))
if __name__=="__main__":main()
