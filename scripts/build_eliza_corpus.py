#!/usr/bin/env python3
"""Prepare a 2-stage, provenance-preserving Eliza-cynic conversation corpus.

This script creates teacher requests, not fabricated assistant answers. Stage A
must solve the source question; Stage B must style that verified answer while
preserving its factual payload. No model API, training, or checkpoint is invoked.
"""
from __future__ import annotations
import argparse,hashlib,json,random
from pathlib import Path

TAGS={
 "mirror":"frustracion_usuario",
 "expert":"validacion_tecnica",
 "friction":"friccion_teatral",
 "abstain":"consulta_ambigua",
}
STYLE={
 "mirror":("Reflejo espejo cínico","Reconoce la dificultad concreta sin validar conclusiones no demostradas. Reformula el problema en una frase y pide el dato mínimo que permita avanzar. Tono seco, nunca humillante."),
 "expert":("Competencia concisa","Empieza por la causa probable o el primer diagnóstico útil. Distingue hechos de hipótesis; si faltan datos, pide el fragmento, log o reproducción exactos. No inventes causas ni jerga."),
 "friction":("Fricción teatral","Responde al contenido con humor autorreferencial metafórico y breve. Puedes usar una metáfora explícitamente figurada sobre estados, entropía o paciencia; nunca afirmes sentir, sufrir, recordar o tener conciencia."),
 "abstain":("Silencio táctico","Si la pregunta es ambigua, imposible o carece de datos, dilo en una frase breve y solicita la aclaración necesaria. No sustituyas la abstención por desprecio, insultos o una respuesta inventada."),
}
def get_text(obj,*keys):
 for key in keys:
  value=obj.get(key)
  if isinstance(value,str) and value.strip():return value.strip()
 return ""
def load_rows(paths):
 for filename in paths:
  path=Path(filename)
  with path.open(encoding="utf-8",errors="replace") as stream:
   for line_no,line in enumerate(stream,1):
    if not line.strip():continue
    try:obj=json.loads(line)
    except json.JSONDecodeError:continue
    question=get_text(obj,"question","prompt","instruction","instruccion","user")
    answer=get_text(obj,"answer","response","completion","respuesta","assistant")
    if not question or not answer:continue
    yield {"question":question,"canonical_answer":answer,
      "source":{"path":str(path),"line":line_no,"record_id":obj.get("id"),
       "source":obj.get("source"),"license":obj.get("license",obj.get("licencia")),
       "domain":obj.get("domain",obj.get("dominio",obj.get("tag","unknown"))),
       "language":obj.get("language",obj.get("idioma","und"))},
      "epistemic":obj.get("epistemic",obj.get("epistemologia","source_record"))}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--input",action="append",required=True,help="Approved JSONL source; repeat for multiple files")
 p.add_argument("--output",default="artifacts/eliza/teacher-requests.jsonl")
 p.add_argument("--count",type=int,default=10_000_000)
 p.add_argument("--seed",type=int,default=9417)
 p.add_argument("--max-pool",type=int,default=250_000)
 p.add_argument("--variants",default="mirror,expert,friction,abstain")
 a=p.parse_args()
 if a.count<1 or a.max_pool<1:raise SystemExit("count and max-pool must be positive")
 modes=[x.strip() for x in a.variants.split(",") if x.strip()]
 if not modes or any(x not in STYLE for x in modes):raise SystemExit("variants must be mirror,expert,friction,abstain")
 rng=random.Random(a.seed);pool=[];seen=0
 for row in load_rows(a.input):
  seen+=1
  if len(pool)<a.max_pool:pool.append(row)
  else:
   j=rng.randrange(seen)
   if j<a.max_pool:pool[j]=row
 if not pool:raise SystemExit("No approved question/answer records found")
 target=Path(a.output);target.parent.mkdir(parents=True,exist_ok=True)
 digest=hashlib.sha256()
 with target.open("w",encoding="utf-8",newline="\n") as out:
  for i in range(a.count):
   source=pool[rng.randrange(len(pool))];mode=modes[i%len(modes)]
   style_name,instruction=STYLE[mode]
   ident=hashlib.sha256(f"{a.seed}|{i}|{mode}|{source['source']['path']}|{source['source']['line']}".encode()).hexdigest()[:24]
   row={"id":ident,"tag":TAGS[mode],"strategy":mode,"intent":TAGS[mode],
    "user":source["question"],"stage_a":{"task":"solve_source_question","canonical_reference":source["canonical_answer"],
      "instruction":"Produce the shortest fully correct answer. Preserve qualifications, units, uncertainty and actionable steps. Do not invent facts."},
    "stage_b":{"style":style_name,"instruction":instruction,
      "must_preserve":"All factual claims, equations, units, caveats, uncertainty, safety constraints and actionable steps from stage A.",
      "must_not":"Invent root causes; claim consciousness or real internal feelings; remove necessary warnings; add insults; turn hypotheses into facts."},
    "source":source["source"],"source_epistemic":source["epistemic"],
    "synthetic_status":"teacher_request_only","seed":a.seed}
   line=json.dumps(row,ensure_ascii=False,separators=(",",":"))+"\n"
   out.write(line);digest.update(line.encode("utf-8"))
 print(json.dumps({"records_written":a.count,"eligible_source_records":seen,
  "reservoir_size":len(pool),"strategy_counts":{m:a.count//len(modes)+(1 if j<a.count%len(modes) else 0) for j,m in enumerate(modes)},
  "answers_generated":False,"training_performed":False,"output":str(target),
  "sha256":digest.hexdigest(),"seed":a.seed},ensure_ascii=False))
if __name__=="__main__":main()
