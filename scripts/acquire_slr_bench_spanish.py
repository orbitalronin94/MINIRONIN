#!/usr/bin/env python3
"""Import only the SLR-Bench-Spanish v1-All train split with provenance."""
from __future__ import annotations
import argparse, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path

REPO_ID="AIML-TUDA/SLR-Bench-Spanish"
SOURCE_URL="https://huggingface.co/datasets/AIML-TUDA/SLR-Bench-Spanish"
PAPER_URL="https://arxiv.org/abs/2506.15787"
LICENSE="CC BY 4.0"

def get(row,*names):
    lookup={re.sub(r"[^a-z0-9]","",str(k).casefold()):v for k,v in row.items()}
    for name in names:
        key=re.sub(r"[^a-z0-9]","",name.casefold())
        if key in lookup:return lookup[key]
    raise ValueError(f"missing field {names}; got {list(row)}")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--revision",required=True)
    ap.add_argument("--output-dir",type=Path,default=Path("data/curated/accepted"))
    args=ap.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}",args.revision):raise SystemExit("revision must be full HF commit SHA")
    from datasets import load_dataset
    from huggingface_hub import HfApi
    info=HfApi().dataset_info(REPO_ID,revision=args.revision)
    card=info.card_data
    license_value=getattr(card,"license",None) if card else None
    if str(license_value).casefold().replace("_","-") not in {"cc-by-4.0","cc-by"}:
        raise SystemExit(f"license mismatch: {license_value!r}")
    ds=load_dataset(REPO_ID,"v1-All",split="train",revision=args.revision)
    if len(ds)!=18053:raise SystemExit(f"expected 18053 v1-All train rows, got {len(ds)}")
    args.output_dir.mkdir(parents=True,exist_ok=True)
    out=args.output_dir/"slr-bench-spanish-v1-all-train.jsonl"
    seen_ids=set();seen_prompts=set();tiers={};levels={};digest=hashlib.sha256()
    with out.open("w",encoding="utf-8",newline="\n") as f:
        for idx,row in enumerate(ds):
            sid=str(get(row,"id"))
            prompt=str(get(row,"prompt")).strip()
            rule=str(get(row,"ground-truth rule")).strip()
            validator=str(get(row,"validation program")).strip()
            symbols=str(get(row,"symbols")).strip()
            tier=str(get(row,"curriculum tier")).strip()
            level=int(get(row,"curriculum level"))
            if not sid or not prompt or not rule or not validator:
                raise ValueError(f"empty required field at row {idx}")
            if sid in seen_ids:raise ValueError(f"duplicate source id {sid}")
            seen_ids.add(sid)
            # Keep unique source IDs. Prompt duplication is audited separately; some
            # generated prompts can share a template but encode different latent rules.
            ph=hashlib.sha256(prompt.encode("utf-8")).hexdigest()
            seen_prompts.add(ph)
            tiers[tier]=tiers.get(tier,0)+1
            levels[str(level)]=levels.get(str(level),0)+1
            record={
                "id":f"slr-bench-es:v1-All:{sid}",
                "question":prompt,
                "answer":rule,
                "domain":"razonamiento lógico inductivo",
                "language":"es",
                "split":"train",
                "train_eligible":True,
                "admission_status":"accepted",
                "synthetic":True,
                "license":LICENSE,
                "source_dataset":"SLR-Bench-Spanish",
                "source":SOURCE_URL,
                "source_revision":args.revision,
                "paper":PAPER_URL,
                "source_config":"v1-All",
                "original_source_id":sid,
                "validation_program":validator,
                "symbols":symbols,
                "curriculum_level":level,
                "curriculum_tier":tier,
                "rule_sampling":str(get(row,"rule sampling")),
                "rule_complexity":str(get(row,"rule complexity")),
                "background_sampling":str(get(row,"background sampling")),
                "problem_size":int(get(row,"problem size")),
                "vocabulary_predicates":int(get(row,"vocabulary predicates")),
                "vocabulary_car_constants":str(get(row,"vocabulary car constants")),
                "attribution":"Lukas Helff et al., SLR: Automated Synthesis for Scalable Logical Reasoning (2025); AIML-TUDA SLR-Bench-Spanish, CC BY 4.0."
            }
            line=json.dumps(record,ensure_ascii=False,separators=(",",":"))+"\n"
            f.write(line);digest.update(line.encode("utf-8"))
    if len(seen_ids)!=len(ds):raise SystemExit("source ID cardinality mismatch")
    manifest={
        "schema_version":1,"dataset":"SLR-Bench-Spanish v1-All train",
        "source_dataset":REPO_ID,"source_url":SOURCE_URL,"paper_url":PAPER_URL,
        "source_revision":args.revision,"source_config":"v1-All","source_split":"train",
        "excluded_splits":["validation","test"],"excluded_configs":["v1-Basic","v1-Easy","v1-Medium","v1-Hard (overlapping subsets)"],
        "license":LICENSE,"language":"es","domain":"razonamiento lógico inductivo",
        "record_count":len(ds),"unique_source_ids":len(seen_ids),"unique_prompt_hashes":len(seen_prompts),
        "curriculum_tier_counts":tiers,"curriculum_level_counts":levels,
        "file":out.name,"sha256_jsonl":digest.hexdigest(),
        "retrieved_at_utc":datetime.now(timezone.utc).isoformat(),
        "admission_status":"accepted for training; evaluation splits excluded",
        "limitations":[
            "Synthetic inductive-reasoning tasks; not factual knowledge or natural dialogue.",
            "Answer is the dataset's latent ground-truth rule; validation program retained for deterministic external checking.",
            "v1-All is imported once; other configs are overlapping curriculum subsets and are not duplicated.",
            "Validation and test splits are not imported."
        ]
    }
    (args.output_dir/"slr-bench-spanish-v1-all-train.manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:manifest[k] for k in ("record_count","unique_source_ids","unique_prompt_hashes","curriculum_tier_counts","curriculum_level_counts","license","source_revision","sha256_jsonl")},ensure_ascii=False))
if __name__=="__main__":main()
