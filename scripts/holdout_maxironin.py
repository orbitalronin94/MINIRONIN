#!/usr/bin/env python3
from __future__ import annotations
import argparse, gc, hashlib, json, random, time
from pathlib import Path
import numpy as np
import torch
from tokenizers import Tokenizer
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from maxironin import MaxRoninConfig, MaxRoninLM

def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
 return h.hexdigest()

@torch.inference_mode()
def generate(model, tokenizer, question, eos_id, max_new=128):
 prompt=question+"\nRespuesta:"
 ids=tokenizer.encode(prompt).ids
 if len(ids)>=512: ids=ids[-511:]
 x=torch.tensor([ids],dtype=torch.long)
 generated=[]
 model.eval()
 for _ in range(max_new):
  logits,_=model(x)
  nxt=int(torch.argmax(logits[0,-1,:]).item())
  if nxt==eos_id: break
  generated.append(nxt)
  x=torch.cat([x,torch.tensor([[nxt]],dtype=torch.long)],dim=1)
  if x.shape[1]>=512: break
 return tokenizer.decode(generated),len(generated)

def run(model, tokenizer, holdout, output, label, ckpt_sha, tok_sha, seed):
 results=[]
 eos=tokenizer.token_to_id("<EOS>")
 if eos is None: raise RuntimeError("Missing <EOS> token")
 for i,row in enumerate(holdout,1):
  answer,n=generate(model,tokenizer,row["question"],eos)
  results.append({"id":row["id"],"domain":row["domain"],"question":row["question"],"rubric":row["rubric"],"answer":answer,"generated_tokens":n})
  if i%10==0: print(json.dumps({"event":"holdout_progress","state":label,"completed":i,"total":len(holdout)}),flush=True)
 payload={"schema_version":1,"benchmark":"MINIRONIN inference holdout v1 (unmodified questions/rubrics)","experiment":"MAXIRONIN-500M","state":label,"seed":seed,"checkpoint_sha256":ckpt_sha,"tokenizer_sha256":tok_sha,"holdout_sha256":sha(Path("benchmarks/inference-holdout-v1.jsonl")),"holdout_count":len(results),"generation":{"strategy":"greedy argmax","temperature":0,"max_new_tokens":128,"prompt_suffix":"\\nRespuesta:","context_limit":512,"dtype":"float32","threads":4},"scoring_status":"unscored_raw_generation","human_blind_review_required":True,"results":results}
 output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"event":"holdout_complete","state":label,"count":len(results),"file":str(output),"checkpoint_sha256":ckpt_sha}),flush=True)

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--tokenizer",required=True);p.add_argument("--checkpoint",required=True);p.add_argument("--output-dir",required=True);p.add_argument("--holdout",default="benchmarks/inference-holdout-v1.jsonl")
 a=p.parse_args()
 torch.set_num_threads(4);torch.set_num_interop_threads(2);torch.use_deterministic_algorithms(True)
 seed=20261109
 random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
 tokpath=Path(a.tokenizer); tokenizer=Tokenizer.from_file(str(tokpath)); toksha=sha(tokpath)
 rows=[json.loads(x) for x in Path(a.holdout).read_text(encoding="utf-8").splitlines() if x.strip()]
 if len(rows)!=100: raise RuntimeError(f"Expected fixed 100-question holdout, got {len(rows)}")
 out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
 config=MaxRoninConfig()
 # Exact deterministic reconstruction of the initialization used by train_maxironin.py.
 initial=MaxRoninLM(config).cpu()
 initsha="reconstructed-from-seed-20261109; no standalone initial checkpoint was saved"
 run(initial,tokenizer,rows,out/"holdout-before-step-1000.json", "before_step_0_reconstructed",initsha,toksha,seed)
 del initial;gc.collect()
 checkpoint=Path(a.checkpoint)
 state=torch.load(checkpoint,map_location="cpu",weights_only=False)
 model=MaxRoninLM(config).cpu()
 model.load_state_dict(state["model_state_dict"],strict=True)
 actual=sha(checkpoint)
 expected="1976762ef0de1b0c30a0f286204d4c5f81b4c4f283271d313099fe4092bc7764"
 if actual!=expected: raise RuntimeError(f"Checkpoint SHA mismatch: {actual}")
 if state.get("completed_steps")!=1000: raise RuntimeError("Checkpoint is not step 1000")
 run(model,tokenizer,rows,out/"holdout-after-step-1000.json","after_step_1000",actual,toksha,seed)
 print(json.dumps({"event":"paired_holdout_complete","before":"reconstructed initialization","after_checkpoint_sha256":actual,"tokenizer_sha256":toksha}),flush=True)
if __name__=="__main__": main()
