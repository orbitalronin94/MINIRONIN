#!/usr/bin/env python3
"""Acquire CC-BY-4.0 Spanish scientific texts from Proxecto Nós Minerva."""
from __future__ import annotations
import argparse, hashlib, json, re, unicodedata
from datetime import datetime, timezone
from pathlib import Path

REPO_ID="proxectonos/corpus_dominio_cientifico"
FILENAME="es/Catalogo_Minerva/ES_Catalogo_Minerva.jsonl"
SOURCE_URL="https://huggingface.co/datasets/proxectonos/corpus_dominio_cientifico"
EXPECTED_FILE_SHA256="5bb5c9ea0c14d47bb9ebf1d221393814aefc23142c490e6b2031685fa5ca340a"
LICENSE="CC BY 4.0"

def norm(text):
    text=unicodedata.normalize("NFKC",text).casefold()
    return re.sub(r"\s+"," ",text).strip()
def digest(text):
    return hashlib.sha256(norm(text).encode("utf-8")).hexdigest()
def existing_hashes(root):
    excluded={".git","holdout","benchmarks","validation","test","quarantine","candidate","artifacts","checkpoints"}
    hashes=set()
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in {".md",".txt",".jsonl"}: continue
        if any(x.casefold() in excluded for x in p.parts) or p.name.casefold()=="readme.md": continue
        try:
            if p.suffix.lower()==".jsonl":
                with p.open(encoding="utf-8") as f:
                    for line in f:
                        try: row=json.loads(line)
                        except Exception: continue
                        for key in ("text","content","body","answer"):
                            v=row.get(key)
                            if isinstance(v,str) and len(v.strip())>=200: hashes.add(digest(v))
            else:
                v=p.read_text(encoding="utf-8")
                if len(v.strip())>=200: hashes.add(digest(v))
        except (UnicodeError,OSError): continue
    return hashes
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--revision",required=True)
    ap.add_argument("--root",type=Path,default=Path("."))
    ap.add_argument("--output-dir",type=Path,default=Path("data/curated/accepted"))
    args=ap.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}",args.revision): raise SystemExit("revision must be full HF commit SHA")
    from huggingface_hub import HfApi, hf_hub_download
    info=HfApi().dataset_info(REPO_ID,revision=args.revision)
    card=info.card_data
    lic=getattr(card,"license",None) if card else None
    if str(lic).casefold().replace("_","-") not in {"cc-by-4.0","cc-by"}: raise SystemExit(f"dataset license mismatch: {lic!r}")
    local=Path(hf_hub_download(repo_id=REPO_ID,filename=FILENAME,repo_type="dataset",revision=args.revision))
    hasher=hashlib.sha256()
    with local.open("rb") as payload:
        for block in iter(lambda: payload.read(1024*1024), b""):
            hasher.update(block)
    file_sha=hasher.hexdigest()
    if file_sha!=EXPECTED_FILE_SHA256: raise SystemExit(f"upstream payload SHA changed: {file_sha}")
    existing=existing_hashes(args.root)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    out=args.output_dir/"minerva-scientific-es-train.jsonl"
    seen=set(); counts={}; scanned=0; admitted=0; no_license=0; non_es=0; short=0; duplicates=0
    output_sha=hashlib.sha256()
    with local.open(encoding="utf-8") as source, out.open("w",encoding="utf-8",newline="\n") as dest:
        for line_no,line in enumerate(source,1):
            if not line.strip(): continue
            row=json.loads(line); scanned+=1
            text=row.get("text")
            if not isinstance(text,str) or len(text.strip())<200: short+=1; continue
            lang=str(row.get("lang") or row.get("language") or "es").casefold()
            if lang not in {"es","spa","spanish","español"}: non_es+=1; continue
            rights=row.get("license")
            if not isinstance(rights,dict) or rights.get("open_access") is not True:
                no_license+=1; continue
            lic_url=str(rights.get("url") or "").casefold()
            lic_statement=str(rights.get("statement") or "").casefold()
            if "creativecommons.org/licenses/by/4.0" not in lic_url and "cc by 4.0" not in lic_statement and "cc-by-4.0" not in lic_statement:
                no_license+=1; continue
            h=digest(text)
            if h in seen or h in existing: duplicates+=1; continue
            seen.add(h)
            title=row.get("title") or {}
            if isinstance(title,dict): title_es=title.get("es") or title.get("en") or ""
            else: title_es=str(title)
            authors=row.get("authors") or []
            record={
                "id":f"minerva-es:{row.get('doc_id') or row.get('id') or h[:20]}",
                "text":text,"domain":"ciencia y documentación académica",
                "language":"es","split":"train","train_eligible":True,
                "admission_status":"accepted","synthetic":False,"license":LICENSE,
                "source_dataset":REPO_ID,"source":SOURCE_URL,
                "source_revision":args.revision,"source_id":str(row.get("source") or "Catalogo_Minerva"),
                "source_url":row.get("source_url"),"title":title_es,
                "authors":authors,"journal":row.get("journal"),
                "year":row.get("year"),"subjects":row.get("subjects"),
                "abstract_en":row.get("abstract_en"),"abstract_gl":row.get("abstract_gl"),
                "upstream_license":rights,
                "attribution":"Proxecto Nós, Corpus de dominio científico y académico, subcorpus español del Catálogo Minerva USC; CC BY 4.0."
            }
            encoded=json.dumps(record,ensure_ascii=False,separators=(",",":"))+"\n"
            dest.write(encoded); output_sha.update(encoded.encode("utf-8")); admitted+=1
            sid=str(row.get("source") or "Catalogo_Minerva")
            counts[sid]=counts.get(sid,0)+1
    if scanned<8000: raise SystemExit(f"unexpectedly small Minerva payload: {scanned} rows")
    if admitted==0: raise SystemExit("no records survived Spanish/open-license/exact-dedup filters")
    manifest={
        "schema_version":1,"dataset":"Proxecto Nós — Catalogo Minerva español",
        "source_dataset":REPO_ID,"source_url":SOURCE_URL,"source_file":FILENAME,
        "source_revision":args.revision,"source_split":"train","license":LICENSE,
        "language":"es","domain":"ciencia y documentación académica",
        "source_file_sha256":file_sha,"source_file_bytes":local.stat().st_size,
        "source_rows_scanned":scanned,"rows_admitted":admitted,
        "rows_skipped_no_explicit_open_license":no_license,"rows_skipped_non_spanish":non_es,
        "rows_skipped_short":short,"rows_skipped_exact_duplicates":duplicates,
        "source_id_counts":counts,"file":out.name,"sha256_jsonl":output_sha.hexdigest(),
        "retrieved_at_utc":datetime.now(timezone.utc).isoformat(),
        "deduplication":"NFKC + casefold + whitespace normalization, SHA-256 within batch and against repository train text",
        "limitations":[
            "Only the Spanish Catalogo Minerva file is imported; Wikipedia and Galician corpora are excluded.",
            "Every admitted record must declare open_access=true and a CC BY 4.0 license URL/statement.",
            "Original source URL, title, authors, journal, year, subjects and license metadata are retained where present."
        ]
    }
    (args.output_dir/"minerva-scientific-es-train.manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:manifest[k] for k in ("source_rows_scanned","rows_admitted","rows_skipped_no_explicit_open_license","rows_skipped_exact_duplicates","source_id_counts","source_file_sha256","sha256_jsonl")},ensure_ascii=False))
if __name__=="__main__": main()
