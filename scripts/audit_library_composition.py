#!/usr/bin/env python3
"""Estimate subject composition of a unified JSONL.GZ training corpus."""
from __future__ import annotations
import argparse, collections, gzip, json, re
from pathlib import Path

RULES = [
 ("literature_history_humanities", r"literatur|novel|poes|teatro|human|filosof|histori|arte|cultura|relig|anarqu|classic|wikisource|spanish-pd-books|hemeroteca"),
 ("science_medicine", r"cient[ií]f|science|medicin|cl[ií]nic|farmac|biomed|salud|biology|biolog|f[ií]sic|qu[ií]mic|matem[aá]t|math|astronom|minerva|pharmaco|spaccc"),
 ("law_government", r"derech|legal|legisl|boe|gobiern|administraci[oó]n|parlament|constituci[oó]n|dogv|alia.*legal|bsc-legal"),
 ("education_academia", r"tesis|thesis|tdx|acad[eé]mic|educaci[oó]n|univers|pedagog|school|course"),
 ("technology_engineering", r"software|program|c[oó]dig|computer|inform[aá]t|ingenier|tecnolog|sql|rpa|github|engineering"),
 ("social_sciences_economics", r"econom|sociolog|pol[ií]tic|psicolog|demograf|empresa|finanz|comerc|social.?scien"),
 ("language_translation", r"ling[uü][ií]st|lengua|idioma|translation|traduc|corpus.?paral|ner|lexicon|language"),
 ("reference_general", r"wikimedia|wikipedia|encycl|enciclop|general|common.?corpus|heretic|prodatphil"),
]
def flatten(v):
 if isinstance(v,dict):
  for k,x in v.items():
   if k.lower() not in {"text","content","body","document","passage","answer","question","prompt","input","target","completion"}:
    yield str(k); yield from flatten(x)
 elif isinstance(v,list):
  for x in v: yield from flatten(x)
 elif isinstance(v,(str,int,float)): yield str(v)

def classify(row):
 if row.get("synthetic") is True: return "synthetic_behavior"
 metadata=row.get("metadata",{}) if isinstance(row.get("metadata",{}),dict) else {}
 specific=[]
 for key in ("subject","domain","dominio","category","categories","categoria","discipline","disciplina","topic","topics","tema","temas","keywords","palabras_clave","title","titulo","collection","tag","tipo","usage","uso","architecture","arquitectura"):
  if key in metadata: specific.extend(flatten(metadata[key]))
 specific_label=" ".join(specific).casefold()
 for category,pattern in RULES:
  if specific_label and re.search(pattern,specific_label,re.I): return category
 fields=[row.get("dataset",""),row.get("domain",""),row.get("source",""),row.get("source_id","")]
 label=" ".join(map(str,fields)).casefold()
 for category,pattern in RULES:
  if re.search(pattern,label,re.I): return category
 return "other_unclassified"

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--input",default="unified-train/train.jsonl.gz")
 ap.add_argument("--output",default="unified-train/composition-by-matter.json")
 args=ap.parse_args()
 counts=collections.Counter(); tokens=collections.Counter(); datasets=collections.Counter()
 total=0; total_tokens=0
 with gzip.open(args.input,"rt",encoding="utf-8") as f:
  for line in f:
   if not line.strip(): continue
   row=json.loads(line); category=classify(row)
   n=len(str(row.get("text","")).split())
   counts[category]+=1; tokens[category]+=n; datasets[(category,str(row.get("dataset","unknown")))]+=1
   total+=1; total_tokens+=n
 order=[x[0] for x in RULES]+["synthetic_behavior","other_unclassified"]
 result={
  "schema":"minironin-library-composition-v1",
  "input":str(args.input),
  "method":{
   "classification":"Deterministic single-label classification from dataset, domain, source and non-text metadata fields; synthetic=true overrides subject taxonomy.",
   "record_share":"records in category / all records",
   "token_share":"whitespace-separated words in category / all whitespace-separated words",
   "limitations":"Whitespace token counts are only a proxy, not counts from MINIRONIN's model tokenizer. Generic and multi-topic sources can be underclassified; review other_unclassified and sample documents before treating shares as semantic ground truth."
  },
  "total_records":total,"total_whitespace_tokens":total_tokens,
  "categories":[{"matter":c,"records":counts[c],"record_percent":round(100*counts[c]/total,4) if total else 0,
   "whitespace_tokens":tokens[c],"token_percent":round(100*tokens[c]/total_tokens,4) if total_tokens else 0,
   "datasets":dict(sorted(((d,n) for (cat,d),n in datasets.items() if cat==c),key=lambda x:-x[1])[:30])} for c in order if counts[c]],
  "unclassified_record_percent":round(100*counts["other_unclassified"]/total,4) if total else 0
 }
 Path(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
 print(json.dumps({"records":total,"whitespace_tokens":total_tokens,"unclassified_percent":result["unclassified_record_percent"],"categories":len(result["categories"])},ensure_ascii=False))
if __name__=="__main__": main()
