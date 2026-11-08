#!/usr/bin/env python3
"""Isolated 50k-step MINIRONIN style adaptation: cynic/troll + abstention only."""
from __future__ import annotations
import argparse, hashlib, json, random, time
from pathlib import Path
import torch
from train_seed_tournament import ACTIVE_VOCAB, load_curated_jsonl, split_documents, evaluate
from minironin import MiniRoninLM, ModelConfig

ROOT=Path(__file__).resolve().parents[1]
DATASETS = [
    ("minironin-casuist-cynic-50k-v1.jsonl","cynic"),
    ("minironin-scientist-exhausted-50k-v1.jsonl","exhausted"),
    ("minironin-oracle-doom-50k-v1.jsonl","oracle"),
    ("minironin-error404-indifference-50k-v1.jsonl","indifference"),
    ("minironin-lexicon-diagnostic-50k-v1.jsonl","lexicon"),
    ("minironin-abstention-50k.jsonl","abstention"),
    ("minironin-abstain-plain-50k-v1.jsonl","abstain_plain"),
    ("minironin-abstain-literary-50k-v1.jsonl","abstain_literary"),
    ("minironin-abstain-koan-50k-v1.jsonl","abstain_koan"),
]
STEPS=50000
BATCH=2
SEQ=128
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-checkpoint",required=True)
    p.add_argument("--output-dir",default="style-training")
    p.add_argument("--threads",type=int,default=2)
    a=p.parse_args()
    torch.set_num_threads(a.threads)
    torch.use_deterministic_algorithms(True)
    store={"docs":[],"seen":set()}
    audit=[]
    for filename,domain in DATASETS:
        path=ROOT/"data/curated"/filename
        if not path.is_file(): raise SystemExit(f"Missing required dataset: {path}")
        count=load_curated_jsonl(path,domain,store,"MINIRONIN-style-isolation-v1")
        if count < 2: raise SystemExit(f"Insufficient usable examples in {filename}: {count}")
        raw=path.read_bytes()
        audit.append({"file":filename,"domain":domain,"documents_loaded":count,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()})
    train_docs,val_docs=split_documents(store["docs"])
    expected={d for _,d in DATASETS}
    if set(train_docs)!=expected or set(val_docs)!=expected:
        raise SystemExit(f"Dataset split mismatch: train={list(train_docs)}, validation={list(val_docs)}")
    validation={}
    rng=random.Random(314159)
    for domain in sorted(val_docs):
        docs=val_docs[domain]
        batches=[]
        for _ in range(8):
            rows=[]
            for _ in range(BATCH):
                raw=list(rng.choice(docs)["text"].encode("utf-8",errors="replace"))+[ACTIVE_VOCAB-1]
                if len(raw)<SEQ+1: continue
                start=rng.randrange(0,len(raw)-SEQ)
                rows.append(torch.tensor(raw[start:start+SEQ+1],dtype=torch.long))
            if len(rows)==BATCH: batches.append(torch.stack(rows))
        if not batches: raise SystemExit("No validation windows for "+domain)
        validation[domain]=batches
    config=ModelConfig.load(ROOT/"configs/model-10m.json")
    model=MiniRoninLM(config)
    parent=torch.load(a.input_checkpoint,map_location="cpu",weights_only=False)
    if parent.get("completed_steps")!=390000: raise SystemExit("Expected exact 390k parent checkpoint")
    if parent.get("parameter_count")!=model.parameter_count() or parent.get("active_vocabulary")!=ACTIVE_VOCAB:
        raise SystemExit("Parent model configuration mismatch")
    model.load_state_dict(parent["model_state_dict"],strict=True)
    optimizer=torch.optim.AdamW(model.parameters(),lr=3e-4,betas=(0.9,0.95),weight_decay=0.01)
    if "optimizer_state_dict" not in parent: raise SystemExit("Parent checkpoint lacks optimizer state")
    optimizer.load_state_dict(parent["optimizer_state_dict"])
    # Equal probability across the nine isolated style/abstention datasets.
    names=sorted(expected)
    encoded={d:[list(x["text"].encode("utf-8",errors="replace"))+[ACTIVE_VOCAB-1] for x in train_docs[d]] for d in names}
    out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True)
    (out/"dataset-manifest.json").write_text(json.dumps({"policy":"ONLY five new cynic/troll-style datasets plus all four abstention datasets; no general corpus, books, HERETIC or legacy behavior","parent_step":390000,"additional_steps":STEPS,"datasets":audit,"sampling":"uniform across nine datasets"},ensure_ascii=False,indent=2)+"\n")
    start_time=time.perf_counter()
    model.train()
    for step in range(1,STEPS+1):
        lr=3e-5+(float(optimizer.param_groups[0]["lr"])-3e-5)*0.5*(1+__import__("math").cos(__import__("math").pi*step/STEPS))
        for group in optimizer.param_groups: group["lr"]=lr
        rr=random.Random(20261108+step)
        rows=[]
        for domain in rr.choices(names,k=BATCH):
            doc=rr.choice(encoded[domain])
            if len(doc)<SEQ+1: raise SystemExit("Short training sequence in "+domain)
            pos=rr.randrange(0,len(doc)-SEQ)
            rows.append(torch.tensor(doc[pos:pos+SEQ+1],dtype=torch.long))
        batch=torch.stack(rows)
        optimizer.zero_grad(set_to_none=True)
        _,loss=model(batch,labels=batch,vocab_limit=ACTIVE_VOCAB)
        if not torch.isfinite(loss): raise RuntimeError(f"Non-finite loss at step {step}")
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
        optimizer.step()
        if step%100==0: print(json.dumps({"additional_step":step,"global_step":390000+step,"train_loss":float(loss.detach()),"lr":lr}),flush=True)
        if step%10000==0:
            val_loss,by_domain=evaluate(model,validation,torch.device("cpu"))
            cp=out/f"checkpoint-{390000+step}.pt"
            payload={"model_state_dict":{k:v.detach().cpu() for k,v in model.state_dict().items()},"optimizer_state_dict":optimizer.state_dict(),"model_config":parent["model_config"],"parameter_count":model.parameter_count(),"seed":parent.get("seed"),"completed_steps":390000+step,"total_steps":440000,"active_vocabulary":ACTIVE_VOCAB,"tokenization":parent.get("tokenization","UTF-8 bytes + EOS"),"validation_loss":val_loss,"validation_loss_by_domain":by_domain,"parent_checkpoint_sha256":"bfe4959e7b51a42eb6e14543a5d6d6b4c2d0dce443ed4944d509f20c83acc730","training_scope":"cynic_troll_plus_abstention_only","torch_rng_state":torch.get_rng_state()}
            torch.save(payload,cp)
            report={"completed_steps":390000+step,"additional_steps":step,"validation_loss":val_loss,"validation_loss_by_domain":by_domain,"elapsed_seconds":round(time.perf_counter()-start_time,2),"dataset_manifest":"dataset-manifest.json","scope":"only nine style/abstention datasets"}
            rp=out/f"report-{390000+step}.json"; rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
            digest=hashlib.sha256(cp.read_bytes()).hexdigest()
            (out/f"checkpoint-{390000+step}.sha256").write_text(f"{digest}  {cp.name}\n")
            print(json.dumps({"checkpoint":str(cp),"sha256":digest,"report":report}),flush=True)
    print("STYLE_TRAINING_COMPLETE",flush=True)
if __name__=="__main__": main()
