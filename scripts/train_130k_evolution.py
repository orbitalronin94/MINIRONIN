#!/usr/bin/env python3
"""30-way continuation tournament from the exact 130k parent checkpoint."""
from __future__ import annotations
import argparse, hashlib, json, math, random, sys, time
from pathlib import Path
import torch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src")); sys.path.insert(0,str(ROOT/"scripts"))
from minironin import MiniRoninLM, ModelConfig
from train_long_run import ACTIVE_VOCAB, BATCH_SIZE, SEQUENCE_LENGTH, load_training_data, evaluate, learning_rate

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--parent",required=True); p.add_argument("--heretic-root",required=True)
    p.add_argument("--books-root",required=True); p.add_argument("--cache",required=True)
    p.add_argument("--out",default="evolution-tournament"); p.add_argument("--seeds",type=int,default=30)
    p.add_argument("--steps",type=int,default=1000); p.add_argument("--threads",type=int,default=2)
    p.add_argument("--expected-parent-sha",default=None); p.add_argument("--seed-base",type=int,default=13000)
    a=p.parse_args()
    if a.seeds!=30 or a.steps!=1000: p.error("This protocol is fixed at 30 seeds x 1,000 steps")
    torch.set_num_threads(a.threads); torch.use_deterministic_algorithms(True)
    device=torch.device("cpu")
    parent_path=Path(a.parent)
    parent_hash=hashlib.sha256(parent_path.read_bytes()).hexdigest()
    if a.expected_parent_sha and parent_hash!=a.expected_parent_sha: raise SystemExit(f"Parent SHA mismatch: expected {a.expected_parent_sha}, got {parent_hash}")
    parent=torch.load(parent_path,map_location="cpu",weights_only=False)
    parent_step=int(parent.get("completed_steps",-1))
    if parent_step<0 or "optimizer_state_dict" not in parent:
        raise SystemExit("Parent must be a resumable checkpoint with AdamW state and completed_steps")
    winner_step=parent_step+1000
    train_docs,names,probs,validation,manifest=load_training_data(
        Path(a.heretic_root),Path(a.books_root),Path(a.cache))
    cfg=ModelConfig.load(ROOT/"configs/model-10m.json")
    out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    results=[]; best=None; started=time.perf_counter()
    for idx in range(30):
        seed=a.seed_base+idx
        torch.manual_seed(seed)
        model=MiniRoninLM(cfg).to(device); model.load_state_dict(parent["model_state_dict"],strict=True)
        opt=torch.optim.AdamW(model.parameters(),lr=3e-4,betas=(0.9,0.95),weight_decay=0.01)
        opt.load_state_dict(parent["optimizer_state_dict"])
        # Identical corpus/mix and validation; seed-specific deterministic batch order and dropout.
        rng=random.Random(20261107+seed*1000003)
        losses=[]; t0=time.perf_counter(); model.train()
        for local in range(1,1001):
            global_step=parent_step+local
            domains=rng.choices(names,weights=probs,k=BATCH_SIZE); rows=[]
            for domain in domains:
                doc=rng.choice(train_docs[domain])
                raw=list(doc["text"].encode("utf-8",errors="replace"))+[ACTIVE_VOCAB-1]
                if len(raw)<SEQUENCE_LENGTH+1: raise ValueError("Short training document")
                start=rng.randrange(0,len(raw)-SEQUENCE_LENGTH)
                rows.append(torch.tensor(raw[start:start+SEQUENCE_LENGTH+1],dtype=torch.long))
            batch=torch.stack(rows).to(device)
            lr=float(opt.param_groups[0]["lr"])
            opt.zero_grad(set_to_none=True)
            _,loss=model(batch,labels=batch,vocab_limit=ACTIVE_VOCAB)
            if not torch.isfinite(loss): raise RuntimeError(f"Non-finite loss seed={seed} step={local}")
            loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(),1.0); opt.step()
            losses.append(float(loss.detach()))
            if local%250==0: print(json.dumps({"seed":seed,"step":local,"loss":losses[-1],"lr":lr}),flush=True)
        val,by_domain=evaluate(model,validation,device)
        row={"seed":seed,"steps":1000,"global_step":winner_step,"mean_train_loss_last_100":sum(losses[-100:])/100,
             "validation_loss":val,"validation_loss_by_domain":by_domain,"elapsed_seconds":round(time.perf_counter()-t0,2)}
        results.append(row); print(json.dumps(row),flush=True)
        if best is None or val<best["validation_loss"]:
            best={**row,"model_state_dict":{k:v.detach().cpu().clone() for k,v in model.state_dict().items()},
                  "optimizer_state_dict":opt.state_dict(),"torch_rng_state":torch.get_rng_state()}
        del model,opt
    if best is None: raise SystemExit("No viable candidates")
    checkpoint={"model_state_dict":best.pop("model_state_dict"),"optimizer_state_dict":best.pop("optimizer_state_dict"),
      "torch_rng_state":best.pop("torch_rng_state"),"model_config":parent["model_config"],
      "parameter_count":parent["parameter_count"],"seed":best["seed"],"completed_steps":winner_step,
      "total_steps":winner_step+200000,"active_vocabulary":ACTIVE_VOCAB,"tokenization":parent.get("tokenization","UTF-8 bytes + EOS"),
      "validation_loss":best["validation_loss"],"validation_loss_by_domain":best["validation_loss_by_domain"],
      "parent_checkpoint_sha256":parent_hash,"generation":"130k-parent-30x1000","dataset_manifest":manifest}
    cp=out/f"winner-{winner_step}.pt"; torch.save(checkpoint,cp)
    ranked=sorted(results,key=lambda x:x["validation_loss"])
    report={"status":"completed","parent_steps":parent_step,"parent_sha256":parent_hash,"parent_completed_steps":parent_step,"winner_completed_steps":winner_step,"seed_count":30,
      "steps_per_seed":1000,"total_optimizer_steps":30000,"winner_seed":checkpoint["seed"],
      "winner_validation_loss":checkpoint["validation_loss"],"winner_by_domain":checkpoint["validation_loss_by_domain"],
      "winner_checkpoint_sha256":hashlib.sha256(cp.read_bytes()).hexdigest(),
      "next_stage":f"winner continues for 200,000 additional optimizer steps, global step {winner_step+1}..{winner_step+200000}",
      "promotion":"candidate only; run immutable 40-question holdout before any promotion",
      "elapsed_seconds":round(time.perf_counter()-started,2),"ranked":ranked,"dataset_manifest":manifest}
    (out/"tournament-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    (out/"SHA256SUMS").write_text("\n".join(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.name}" for f in [cp,out/"tournament-report.json"])+"\n")
    print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__": main()
