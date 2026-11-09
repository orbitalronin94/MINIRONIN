#!/usr/bin/env python3
"""Build extractive concept-grounded training rows from approved libraries."""
from __future__ import annotations
import argparse, gzip, hashlib, json, re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTS = {".md", ".txt", ".xml", ".tei", ".html", ".htm", ".jsonl", ".ndjson"}
SKIP = re.compile(r"(readme|manifest|license|sha256|checksum|sources|catalog|schema)", re.I)
DOMAIN = {"minironin-core":"behavior","prodatphil":"books","heretic":"science","ronin-papers":"science","anarchist-classics":"anarchist","classics-library":"classics","wikimedia-es":"science"}
MAX_ROWS_PER_DOCUMENT = 12

def normalize(s):
    return re.sub(r"\W+", " ", s.casefold(), flags=re.UNICODE).strip()

def visible(s):
    s=re.sub(r"(?is)<(script|style)\b[^>]*>.*?</\1>", " ", s)
    s=re.sub(r"(?s)<[^>]+>", " ", s)
    s=re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", s)
    return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t\r\f\v]+", " ", s)).strip()

def sha256_file(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''): digest.update(block)
    return digest.hexdigest()

def iter_documents(path):
    if path.name.endswith((".jsonl",".jsonl.gz",".ndjson",".ndjson.gz")):
        opener=gzip.open if path.name.endswith(".gz") else open
        with opener(path,"rt",encoding="utf-8",errors="replace") as stream:
            for n,line in enumerate(stream,1):
                if not line.strip(): continue
                try: row=json.loads(line)
                except json.JSONDecodeError: continue
                if not isinstance(row,dict): continue
                body=next((row.get(k) for k in ("text","content","body","document","passage") if isinstance(row.get(k),str)), "")
                if body.strip():
                    title=str(row.get("title") or row.get("name") or path.stem)
                    locator=str(row.get("id") or row.get("url") or n)
                    raw=json.dumps(row,ensure_ascii=False,sort_keys=True).encode("utf-8")
                    yield raw,visible(body),title,locator
    else:
        raw=path.read_bytes()
        yield raw,visible(raw.decode("utf-8",errors="replace")),path.stem.replace("-"," "),str(path.relative_to(ROOT))

def paragraphs(text):
    return [p.strip() for p in re.split(r"\n\s*\n",text) if len(p.strip())>=80]

def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜÑ¿¡0-9])",text) if len(s.strip())>=45]

def matches(sentence,alias):
    if len(alias.strip())<4: return False
    return re.search(r"(?<!\w)"+re.escape(alias.strip())+r"(?!\w)",sentence,re.I) is not None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--registry",type=Path,default=ROOT/"data/semantic/LIBRARY_REGISTRY.json")
    ap.add_argument("--output",type=Path,default=ROOT/"data/curated/awakened-library-rows.jsonl")
    ap.add_argument("--manifest",type=Path,default=ROOT/"data/curated/awakened-library-manifest.json")
    ap.add_argument("--max-rows",type=int,default=250000)
    a=ap.parse_args()
    if a.max_rows<1: ap.error("--max-rows must be positive")
    registry=json.loads(a.registry.read_text(encoding="utf-8"))
    concepts={x["id"]:x for x in registry["concepts"]}
    seen=set(); counts=Counter(); by_library=Counter(); by_concept=Counter(); source_files={}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("w",encoding="utf-8") as out:
        stop=False
        for lib in sorted(registry["libraries"],key=lambda x:x["id"]):
            lid=lib["id"]; domain=DOMAIN.get(lid)
            if not domain: counts["unmapped_libraries"]+=1; continue
            selected=[concepts[k] for k in sorted(set(lib.get("concepts",[])) & set(concepts))]
            files=[]
            for item in lib.get("source_paths",[]):
                root=ROOT/item
                if not root.exists(): counts["missing_roots"]+=1; continue
                candidates=[root] if root.is_file() else root.rglob("*")
                files.extend(p for p in candidates if p.is_file() and (p.suffix.lower() in EXTS or p.name.endswith((".jsonl.gz",".ndjson.gz")) ) and not SKIP.search(p.name))
            for path in sorted(set(files)):
                try: docs=iter_documents(path)
                except OSError: counts["unreadable_files"]+=1; continue
                try:
                    for raw,body,title,locator in docs:
                        if len(body)<200: continue
                        docsha=hashlib.sha256(raw).hexdigest()
                        source_files.setdefault(str(path.relative_to(ROOT)),{"sha256":sha256_file(path),"bytes":path.stat().st_size,"library_id":lid})
                        made=0
                        for para in paragraphs(body):
                            ss=sentences(para)
                            if not ss: continue
                            for concept in selected:
                                hits=[s for s in ss if any(matches(s,x) for x in concept.get("aliases",[]))][:2]
                                for answer in hits:
                                    question=f"Según el documento «{title}», ¿qué afirma el texto sobre {concept['label']}?"
                                    identity=normalize(lid+" "+title+" "+question+" "+answer)
                                    rowsha=hashlib.sha256(identity.encode()).hexdigest()
                                    if rowsha in seen: counts["duplicate_rows"]+=1; continue
                                    seen.add(rowsha)
                                    row={"question":question,"context":para[:1800],"answer":answer,"domain":domain,
                                         "source":"MINIRONIN-awakened-library","source_id":str(path.relative_to(ROOT)),
                                         "dataset":"awakened-library-rows.jsonl","license":"Inherited from preapproved library; see original source record",
                                         "synthetic":True,"generation_method":"extractive_concept_grounding_v1",
                                         "library_id":lid,"concept_id":concept["id"],"document_sha256":docsha,
                                         "source_locator":locator,"row_sha256":rowsha}
                                    out.write(json.dumps(row,ensure_ascii=False,separators=(",",":"))+"\n")
                                    counts["rows"]+=1; by_library[lid]+=1; by_concept[concept["id"]]+=1; made+=1
                                    if made>=MAX_ROWS_PER_DOCUMENT or counts["rows"]>=a.max_rows: break
                                if made>=MAX_ROWS_PER_DOCUMENT or counts["rows"]>=a.max_rows: break
                            if made>=MAX_ROWS_PER_DOCUMENT or counts["rows"]>=a.max_rows: break
                        counts["source_documents"]+=1
                        if counts["rows"]>=a.max_rows: stop=True; break
                except (OSError,UnicodeDecodeError): counts["unreadable_files"]+=1
                if stop: break
            if stop: break
    data=a.output.read_bytes()
    manifest={"schema":"minironin-awakened-library-rows-v1","rows":counts["rows"],"source_documents":counts["source_documents"],
      "source_files":len(source_files),"source_file_manifest":source_files,"rows_by_library":dict(sorted(by_library.items())),
      "rows_by_concept":dict(sorted(by_concept.items())),"diagnostics":dict(counts),"sha256":hashlib.sha256(data).hexdigest(),
      "bytes":len(data),"training_authorized":counts["rows"]>0,
      "validation_policy":"Training-only; loader appends rows after the source-level train/validation split.",
      "epistemic_policy":"Answers are verbatim sentences from the supplied context; no generated paraphrase or unsupported synthesis.",
      "provenance_policy":"Each row preserves registry library, source path, source locator and document SHA-256; original license is inherited, never upgraded.",
      "max_rows":a.max_rows}
    a.manifest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in manifest.items() if k!="source_file_manifest"},ensure_ascii=False,indent=2))

if __name__=="__main__": main()
