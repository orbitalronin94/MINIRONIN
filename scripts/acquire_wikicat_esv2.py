#!/usr/bin/env python3
"""Import the complete Spanish WikiCAT_esv2 train split without executing remote code."""
from __future__ import annotations
import argparse, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path
REPO_ID="PlanTL-GOB-ES/WikiCAT_esv2"
SOURCE_URL="https://huggingface.co/datasets/PlanTL-GOB-ES/WikiCAT_esv2"
LICENSE="CC BY-SA 3.0"
TRAIN_FILE="hftrain_esv5.json"
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,default=Path("data/curated/accepted"))
    args=ap.parse_args()
    from huggingface_hub import HfApi,hf_hub_download
    info=HfApi().dataset_info(REPO_ID); revision=info.sha
    if not re.fullmatch(r"[0-9a-f]{40}",revision or ""): raise SystemExit("No immutable source revision")
    card=info.card_data; raw=getattr(card,"license",None) if card else None
    vals=raw if isinstance(raw,(list,tuple,set)) else [raw]
    if "cc-by-sa-3.0" not in {str(v).casefold().replace("_","-").strip() for v in vals if v is not None}:
        raise SystemExit(f"License mismatch: {raw!r}")
    source=Path(hf_hub_download(repo_id=REPO_ID,filename=TRAIN_FILE,repo_type="dataset",revision=revision))
    payload=json.loads(source.read_text(encoding="utf-8"))
    articles=payload.get("data") if isinstance(payload,dict) else None
    if not isinstance(articles,list) or len(articles)<1000: raise SystemExit("Unexpected WikiCAT JSON structure/cardinality")
    args.output_dir.mkdir(parents=True,exist_ok=True)
    out=args.output_dir/"wikicat-esv2-train.jsonl"; digest=hashlib.sha256(); seen=set()
    admitted=duplicates=short=0
    with out.open("w",encoding="utf-8",newline="\n") as f:
        for i,a in enumerate(articles):
            if not isinstance(a,dict): continue
            body=a.get("sentence")
            if not isinstance(body,str) or len(body.strip())<80: short+=1; continue
            label=a.get("label")
            if label is None: raise SystemExit(f"Missing label at source row {i}")
            key=hashlib.sha256(re.sub(r"\s+"," ",body).strip().casefold().encode()).hexdigest()
            if key in seen: duplicates+=1; continue
            seen.add(key)
            record={"id":f"wikicat-esv2:{i}:{key[:16]}","text":body.strip(),
              "domain":"conocimiento enciclopédico y clasificación temática","language":"es",
              "split":"train","train_eligible":True,"admission_status":"accepted","synthetic":False,
              "license":LICENSE,"source_dataset":REPO_ID,"source":SOURCE_URL,
              "source_revision":revision,"source_row":i,"label":label,
              "attribution":"Plan de Tecnologías del Lenguaje — Gobierno de España, WikiCAT_esv2; CC BY-SA 3.0."}
            line=json.dumps(record,ensure_ascii=False,separators=(",",":"))+"\n"
            f.write(line); digest.update(line.encode()); admitted+=1
    if admitted<1000: raise SystemExit(f"Too few admitted rows: {admitted}")
    manifest={"schema_version":1,"dataset":"WikiCAT_esv2 Spanish train","source_dataset":REPO_ID,
      "source":SOURCE_URL,"source_revision":revision,"source_file":TRAIN_FILE,"license":LICENSE,
      "language":"es","source_split":"train","source_rows_scanned":len(articles),
      "rows_admitted":admitted,"rows_skipped_exact_duplicates":duplicates,"rows_skipped_short":short,
      "file":out.name,"sha256_jsonl":digest.hexdigest(),"retrieved_at_utc":datetime.now(timezone.utc).isoformat(),
      "admission_policy":"Complete upstream train split loaded directly from a pinned JSON file; no remote dataset code executed; preserve source label and provenance."}
    (args.output_dir/"wikicat-esv2-train.manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:manifest[k] for k in ("source_revision","source_rows_scanned","rows_admitted","rows_skipped_exact_duplicates","license","sha256_jsonl")},ensure_ascii=False))
if __name__=="__main__": main()
