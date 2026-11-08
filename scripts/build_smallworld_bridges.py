#!/usr/bin/env python3
"""Generate reproducible sparse concept-bridge prompts; never fabricate answers."""
from __future__ import annotations
import argparse,hashlib,json,random,re
from pathlib import Path
TOK=re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_-]{3,}")
STOP=set("para como sobre desde entre cuando donde porque tambien esto esta este that with from have which their there into would could should about using then than such more less some what when where while whose only also very much each other same these those being were been will shall must does your they them pero cada todo toda unos unas algo hacer puede pueden son han hay".split())
FIELDS=("question","answer","context","text","content","prompt","response","instruccion","respuesta","evidencia","fuente","messages","conversations")
def terms(text):
    counts={}
    for word in TOK.findall(text.lower()):
        if word not in STOP:counts[word]=counts.get(word,0)+1
    return [word for word,_ in sorted(counts.items(),key=lambda item:(-item[1],item[0]))[:24]]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",action="append",required=True)
    p.add_argument("--output",default="artifacts/smallworld/teacher-prompts.jsonl")
    p.add_argument("--count",type=int,default=50000)
    p.add_argument("--seed",type=int,default=9417)
    p.add_argument("--pool-limit",type=int,default=100000)
    a=p.parse_args();rng=random.Random(a.seed);pool=[];seen_rows=0
    for filename in a.input:
        with Path(filename).open(encoding="utf-8",errors="replace") as stream:
            for line_number,line in enumerate(stream,1):
                if not line.strip():continue
                try:obj=json.loads(line)
                except json.JSONDecodeError:continue
                text=" ".join(str(obj.get(key,"")) for key in FIELDS)
                words=terms(text)
                if len(words)<3:continue
                row={"file":filename,"line":line_number,"id":obj.get("id"),
                     "domain":obj.get("domain",obj.get("dominio",obj.get("tag",obj.get("tipo","unknown")))),
                     "terms":words}
                seen_rows+=1
                if len(pool)<a.pool_limit:pool.append(row)
                else:
                    slot=rng.randrange(seen_rows)
                    if slot<a.pool_limit:pool[slot]=row
    if len(pool)<3:raise SystemExit("Need at least three eligible source records")
    by_domain={}
    for row in pool:by_domain.setdefault(row["domain"],[]).append(row)
    output=[];seen_graphs=set()
    for _ in range(a.count):
        first=rng.choice(pool);same=by_domain.get(first["domain"],[])
        candidates=same if len(same)>=3 else pool
        second=rng.choice(candidates)
        while second is first:second=rng.choice(candidates)
        third=rng.choice(candidates)
        while third is first or third is second:third=rng.choice(candidates)
        nodes=[]
        for row in (first,second,third):
            choices=[term for term in row["terms"] if term not in nodes]
            if choices:nodes.append(rng.choice(choices))
        if len(nodes)!=3 or tuple(nodes) in seen_graphs:continue
        seen_graphs.add(tuple(nodes))
        graph={"nodes":[{"id":f"n{i}","concept":word} for i,word in enumerate(nodes)],
               "edges":[{"from":"n0","to":"n1"},{"from":"n1","to":"n2"}],
               "routing":"sparse_random_same_domain"}
        prompt=("Conecta estos conceptos: "+", ".join(nodes)+". Define cada uno y construye un puente defendible "
                "(causal, funcional, analógico o de contraste). Etiqueta explícitamente las analogías y no inventes "
                "hechos. Cierra con una observación irónica breve sin perder precisión.")
        output.append({"id":hashlib.sha256((str(a.seed)+"|"+"|".join(nodes)).encode()).hexdigest()[:20],
          "graph":graph,"prompt":prompt,"domain":first["domain"],
          "source_refs":[{"file":row["file"],"line":row["line"],"id":row["id"]} for row in (first,second,third)],
          "answer_status":"teacher_generation_required","epistemic":"synthetic_association_prompt","seed":a.seed})
    target=Path(a.output);target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("w",encoding="utf-8",newline="\n") as stream:
        for row in output:stream.write(json.dumps(row,ensure_ascii=False)+"\n")
    print(json.dumps({"prompts":len(output),"eligible_source_records_seen":seen_rows,
      "reservoir_size":len(pool),"answers_generated":False,"seed":a.seed,"output":str(target)},ensure_ascii=False))
if __name__=="__main__":main()
