#!/usr/bin/env python3
"""Thirty-branch continuation tournament from the same 130k MINIRONIN checkpoint.

Each candidate starts from identical model AND AdamW state. Seeds control only
the deterministic order of sampled training windows. All candidates use the
same fixed document-disjoint validation windows and the original 200k LR
schedule. Best candidate is published; main is never modified/promoted.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, math, random, sys, time, gc
from pathlib import Path
import torch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
sys.path.insert(0,str(ROOT/"scripts"))
from minironin import MiniRoninLM,ModelConfig
from train_long_run import ACTIVE_VOCAB,BATCH_SIZE,SEQUENCE_LENGTH,load_training_data,learning_rate
from train_seed_tournament import evaluate

def make_seed_batch(train_docs,names,probs,encoded,seed_rng):
    domains=seed_rng.choices(names,weights=probs,k=BATCH_SIZE)
    rows=[]
    for domain in domains:
        doc=seed_rng.choice(encoded[domain])
        if len(doc)<SEQUENCE_LENGTH+1: raise ValueError(f"Short document in {domain}")
        start=seed_rng.randrange(0,len(doc)-SEQUENCE_LENGTH)
        rows.append(doc[start:start+SEQUENCE_LENGTH+1])
    return torch.stack(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-checkpoint",required=True)
    ap.add_argument("--expected-sha256",required=True)
    ap.add_argument("--heretic-root",default="data/inherited/heretic-corpus")
    ap.add_argument("--books-root",default="data/inherited/prodatphil-en-v0.3")
    ap.add_argument("--dataset-cache",default="long-training/full-corpus-cache.pt")
    ap.add_argument("--seeds",type=int,default=30)
    ap.add_argument("--steps",type=int,default=1000)
    ap.add_argument("--first-seed",type=int,default=13000)
    ap.add_argument("--threads",type=int,default=2)
    ap.add_argument("--output-dir",default="checkpoint-130k-tournament")
    args=ap.parse_args()
    if args.seeds!=30 or args.steps!=1000:
        ap.error("This controlled experiment is fixed at exactly 30 seeds x 1,000 steps")
    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    device=torch.device("cpu")
    source_path=Path(args.input_checkpoint)
    source_sha=hashlib.sha256(source_path.read_bytes()).hexdigest()
    if source_sha!=args.expected_sha256:
        raise SystemExit(f"Checkpoint SHA-256 mismatch: {source_sha}")
    source=torch.load(source_path,map_location="cpu",weights_only=False)
    if source.get("completed_steps")!=130000: raise SystemExit("Source checkpoint is not step 130000")
    if source.get("active_vocabulary")!=ACTIVE_VOCAB: raise SystemExit("Active vocabulary mismatch")
    if "optimizer_state_dict" not in source: raise SystemExit("130k checkpoint lacks AdamW state")
    config=ModelConfig.load(ROOT/"configs/model-10m.json")
    probe=MiniRoninLM(config)
    parameter_count=probe.parameter_count()
    del probe
    if source.get("parameter_count")!=parameter_count: raise SystemExit("Parameter count mismatch")
    train_docs,names,probs,validation,dataset_manifest=load_training_data(
        Path(args.heretic_root),Path(args.books_root),Path(args.dataset_cache))
    encoded={d:[torch.tensor(list(x["text"].encode("utf-8",errors="replace"))+[ACTIVE_VOCAB-1],dtype=torch.long) for x in train_docs[d]] for d in names}
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    baseline_loss,baseline_domains=evaluate(
        (lambda m:m)(MiniRoninLM(config).to(device)),validation,device
    ) if False else (None,None)
    manifest={
      "protocol":"130k checkpoint continuation tournament",
      "source_checkpoint":"long-train-step-130000/checkpoint-130000.pt",
      "source_checkpoint_sha256":source_sha,
      "source_completed_steps":130000,
      "candidates":args.seeds,"steps_per_candidate":args.steps,
      "total_candidate_optimizer_steps":args.seeds*args.steps,
      "seed_range":[args.first_seed,args.first_seed+args.seeds-1],
      "parameter_count":parameter_count,"active_vocabulary":ACTIVE_VOCAB,
      "optimizer":"AdamW state restored identically from source for every candidate",
      "sampling":"seed-specific deterministic Python RNG; same training documents and domain weights",
      "validation":"same fixed document-disjoint validation windows for all candidates",
      "learning_rate":"original 200k cosine schedule continued at global steps 130001..131000",
      "dataset_manifest":dataset_manifest
    }
    (out/"tournament-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    rows=[];best=None;started=time.perf_counter()
    for i in range(args.seeds):
        seed=args.first_seed+i
        model=MiniRoninLM(config).to(device)
        model.load_state_dict(source["model_state_dict"],strict=True)
        optimizer=torch.optim.AdamW(model.parameters(),lr=3e-4,betas=(0.9,0.95),weight_decay=0.01)
        optimizer.load_state_dict(copy.deepcopy(source["optimizer_state_dict"]))
        rng=random.Random(seed)
        losses=[];t0=time.perf_counter();model.train()
        for local in range(1,args.steps+1):
            global_step=130000+local
            lr=learning_rate(global_step)
            for group in optimizer.param_groups:group["lr"]=lr
            batch=make_seed_batch(train_docs,names,probs,encoded,rng).to(device)
            optimizer.zero_grad(set_to_none=True)
            _,loss=model(batch,labels=batch,vocab_limit=ACTIVE_VOCAB)
            if not torch.isfinite(loss):raise RuntimeError(f"Non-finite loss seed={seed} step={global_step}")
            loss.backward()
            grad=torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
            optimizer.step();losses.append(float(loss.detach()))
            if local%250==0:
                print(json.dumps({"seed":seed,"global_step":global_step,"loss":losses[-1],"lr":lr,"grad_norm":float(grad)}),flush=True)
        val,by_domain=evaluate(model,validation,device)
        row={"seed":seed,"start_step":130000,"completed_steps":131000,"steps":args.steps,
             "mean_train_loss_last_100":sum(losses[-100:])/100,"final_train_loss":losses[-1],
             "validation_loss":val,"validation_loss_by_domain":by_domain,
             "elapsed_seconds":round(time.perf_counter()-t0,2)}
        rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
        if best is None or val<best["validation_loss"]:
            best={"row":row,"model":{k:v.detach().cpu().clone() for k,v in model.state_dict().items()},
                  "optimizer":copy.deepcopy(optimizer.state_dict()),"torch_rng":torch.get_rng_state().clone()}
        del optimizer,model;gc.collect()
    if best is None:raise SystemExit("No candidate completed")
    ranked=sorted(rows,key=lambda x:(x["validation_loss"],x["seed"]))
    report={"status":"completed","promotion":"not_promoted_candidate_only",
      "selection_metric":"lowest fixed validation loss after 1,000 continuation steps",
      "seed_count":args.seeds,"steps_per_seed":args.steps,"total_optimizer_steps":args.seeds*args.steps,
      "source_checkpoint_sha256":source_sha,"source_validation_loss":source.get("validation_loss"),
      "best_seed":best["row"]["seed"],"best_validation_loss":best["row"]["validation_loss"],
      "best_validation_loss_by_domain":best["row"]["validation_loss_by_domain"],
      "best_candidate":best["row"],"total_elapsed_seconds":round(time.perf_counter()-started,2),
      "results_ranked":ranked,"warning":"A lower validation loss is not proof of improved instruction following or reasoning. Run the unchanged 40-question inference holdout before any promotion."}
    checkpoint={"model_state_dict":best["model"],"optimizer_state_dict":best["optimizer"],
      "model_config":source["model_config"],"parameter_count":parameter_count,
      "seed":best["row"]["seed"],"origin_seed":source.get("seed"),
      "completed_steps":131000,"total_steps":200000,"active_vocabulary":ACTIVE_VOCAB,
      "tokenization":source.get("tokenization","UTF-8 bytes + EOS"),
      "validation_loss":best["row"]["validation_loss"],
      "validation_loss_by_domain":best["row"]["validation_loss_by_domain"],
      "dataset_manifest":dataset_manifest,"torch_rng_state":best["torch_rng"]}
    torch.save(checkpoint,out/"best-checkpoint-131000.pt")
    (out/"tournament-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    (out/"results.jsonl").write_text("".join(json.dumps(x,ensure_ascii=False)+"\n" for x in ranked))
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
if __name__=="__main__":main()
