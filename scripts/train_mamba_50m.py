#!/usr/bin/env python3
"""Train a ~49.1M Mamba MINIRONIN candidate from the 390k Transformer seed."""
from __future__ import annotations
import argparse, hashlib, json, math, random, time
from pathlib import Path
import torch

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from minironin.mamba import MambaRoninLM
from train_long_run import load_training_data
from train_seed_tournament import evaluate
from build_abstention_datasets import main as build_abstention_datasets
from build_personality_datasets import main as build_personality_datasets

PARENT_SHA256 = "bfe4959e7b51a42eb6e14543a5d6d6b4c2d0dce443ed4944d509f20c83acc730"
ACTIVE_VOCAB = 257
TOTAL_STEPS = 1000
BATCH_SIZE = 1
SEQUENCE_LENGTH = 64
EXPECTED_PARAMETERS = 49_128_448
REQUIRED_DOMAINS = {
    "math", "science", "books", "behavior", "abstention", "abstain_plain",
    "abstain_literary", "abstain_koan", "aristocrat", "casuist", "scientist",
    "oracle", "indifference", "lexicon",
}

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def make_batch(train_docs, names, probs, rng):
    rows = []
    domains = rng.choices(names, weights=probs, k=BATCH_SIZE)
    for domain in domains:
        raw = list(rng.choice(train_docs[domain])["text"].encode("utf-8", errors="replace")) + [256]
        if len(raw) < SEQUENCE_LENGTH + 1:
            raise ValueError("Training document shorter than sequence window: " + domain)
        start = rng.randrange(0, len(raw) - SEQUENCE_LENGTH)
        rows.append(torch.tensor(raw[start:start + SEQUENCE_LENGTH + 1], dtype=torch.long))
    return torch.stack(rows), domains

def save_checkpoint(path, model, step, parent_hash, metrics):
    payload = {
        "architecture": "mamba-selective-scan-v1",
        "model_config": model.config,
        "model_state_dict": model.state_dict(),
        "completed_steps": step,
        "parameter_count": model.parameter_count(),
        "active_vocabulary": ACTIVE_VOCAB,
        "tokenization": "UTF-8 bytes + EOS",
        "parent_checkpoint_sha256": parent_hash,
        "training_metrics": metrics,
        "candidate_only": True,
    }
    torch.save(payload, path)
    digest = sha256_file(path)
    print(json.dumps({"checkpoint": str(path), "step": step, "sha256": digest,
                      "bytes": path.stat().st_size}, ensure_ascii=False), flush=True)
    return digest

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input-checkpoint", required=True, type=Path)
    p.add_argument("--heretic-root", required=True, type=Path)
    p.add_argument("--books-root", required=True, type=Path)
    p.add_argument("--output-dir", default="mamba-50m/results", type=Path)
    p.add_argument("--dataset-cache", required=True, type=Path)
    p.add_argument("--threads", type=int, default=2)
    args = p.parse_args()

    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(20261108)
    random.seed(20261108)
    parent_hash = sha256_file(args.input_checkpoint)
    if parent_hash != PARENT_SHA256:
        raise SystemExit(f"Parent checkpoint SHA-256 mismatch: {parent_hash}")
    parent = torch.load(args.input_checkpoint, map_location="cpu", weights_only=False)
    if parent.get("completed_steps") != 390000 or parent.get("parameter_count") != 9970176:
        raise SystemExit("Refusing to train: parent is not the verified 390k / 9,970,176 checkpoint")
    old_state = parent["model_state_dict"]
    old_embedding = old_state["token_embedding.weight"]
    if tuple(old_embedding.shape) != (23000, 256):
        raise SystemExit(f"Unexpected parent embedding shape: {tuple(old_embedding.shape)}")

    print("MATERIALIZING_ALL_CURATED_DATASETS", flush=True)
    build_abstention_datasets()
    build_personality_datasets()
    print("LOADING_FULL_CORPUS_AND_ALL_14_DOMAINS", flush=True)
    train_docs, names, probs, validation, manifest = load_training_data(
        args.heretic_root, args.books_root, args.dataset_cache
    )
    missing = sorted(REQUIRED_DOMAINS - set(names))
    if missing:
        raise SystemExit("All-datasets guard failed; missing domains: " + ", ".join(missing))
    if len(validation) < len(REQUIRED_DOMAINS):
        raise SystemExit("Validation split is incomplete; refusing incomparable training")
    print(json.dumps({
        "training_domains": names, "domain_sampling_weights": dict(zip(names, probs)),
        "documents_by_domain": manifest.get("documents_by_domain"),
        "documents_total": manifest.get("documents_total"),
        "curated_dataset_counts": {k: manifest.get(k) for k in (
            "behavior_examples", "abstention_examples_loaded", "abstention_plain_examples",
            "abstention_literary_examples", "abstention_koan_examples", "aristocrat_examples",
            "casuist_examples", "scientist_examples", "oracle_examples",
            "indifference_examples", "lexicon_examples")},
    }, ensure_ascii=False), flush=True)

    model = MambaRoninLM().cpu()
    count = model.parameter_count()
    if count != EXPECTED_PARAMETERS:
        raise SystemExit(f"Mamba parameter-count guard failed: {count} != {EXPECTED_PARAMETERS}")
    # Reuse the trained token representation; Mamba-specific dynamics are newly initialized.
    with torch.no_grad():
        model.token_embedding.weight.zero_()
        model.token_embedding.weight[:, :256].copy_(old_embedding)
    if model.lm_head.weight.data_ptr() != model.token_embedding.weight.data_ptr():
        raise SystemExit("Tied input/output embedding invariant failed")

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    baseline_loss, baseline_domains = evaluate(model, validation, torch.device("cpu"))
    manifest_out = {
        "experiment": "MINIRONIN Mamba ~50M from 390k Transformer seed",
        "parent_step": 390000, "parent_sha256": parent_hash,
        "parent_parameter_count": parent.get("parameter_count"),
        "expanded_parameter_count": count, "architecture": model.config,
        "transfer_policy": "copied 23,000x256 token embeddings into first 256 channels of 23,000x512 tied Mamba embeddings; Transformer attention/MLP/position weights are not mapped; Mamba SSM blocks are newly initialized",
        "training_steps": TOTAL_STEPS, "batch_size": BATCH_SIZE,
        "sequence_length": SEQUENCE_LENGTH, "active_vocabulary": ACTIVE_VOCAB,
        "training_domains": names, "sampling_weights": dict(zip(names, probs)),
        "dataset_manifest": manifest,
        "baseline_validation_loss": baseline_loss,
        "baseline_validation_by_domain": baseline_domains,
        "candidate_only": True,
    }
    (out / "experiment-manifest.json").write_text(
        json.dumps(manifest_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, betas=(0.9, 0.95), weight_decay=0.01)
    rng = random.Random(20261108)
    losses, started = [], time.perf_counter()
    model.train()
    for step in range(1, TOTAL_STEPS + 1):
        warmup = min(1.0, step / 50.0)
        cosine = 0.5 * (1.0 + math.cos(math.pi * step / TOTAL_STEPS))
        lr = 1e-4 * warmup * (0.1 + 0.9 * cosine)
        for group in optimizer.param_groups:
            group["lr"] = lr
        batch, sampled_domains = make_batch(train_docs, names, probs, rng)
        optimizer.zero_grad(set_to_none=True)
        _, loss = model(batch, labels=batch, vocab_limit=ACTIVE_VOCAB)
        if not torch.isfinite(loss):
            raise SystemExit(f"Non-finite training loss at step {step}")
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        losses.append(float(loss.detach()))
        if step % 50 == 0 or step in (1, TOTAL_STEPS):
            print(json.dumps({
                "step": step, "total_steps": TOTAL_STEPS, "loss": losses[-1],
                "mean_loss_last_50": sum(losses[-50:]) / len(losses[-50:]),
                "learning_rate": lr, "sampled_domains": sampled_domains,
                "elapsed_seconds": round(time.perf_counter() - started, 2),
            }), flush=True)
        if step in (250, 500, 750, 1000):
            model.eval()
            val_loss, val_domains = evaluate(model, validation, torch.device("cpu"))
            metrics = {"train_loss_last_50": sum(losses[-50:]) / len(losses[-50:]),
                       "validation_loss": val_loss, "validation_by_domain": val_domains}
            save_checkpoint(out / f"mamba-checkpoint-{step}.pt", model, step, parent_hash, metrics)
            (out / f"metrics-{step}.json").write_text(
                json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            model.train()

    model.eval()
    final_loss, final_domains = evaluate(model, validation, torch.device("cpu"))
    final = {
        "completed_steps": TOTAL_STEPS, "parameter_count": count,
        "parent_sha256": parent_hash, "final_validation_loss": final_loss,
        "final_validation_by_domain": final_domains,
        "baseline_validation_loss": baseline_loss,
        "baseline_validation_by_domain": baseline_domains,
        "train_loss_first_50": sum(losses[:50]) / min(50, len(losses)),
        "train_loss_last_50": sum(losses[-50:]) / min(50, len(losses)),
        "elapsed_seconds": round(time.perf_counter() - started, 2),
        "promotion": "NOT_PROMOTED — independent holdout review required",
    }
    (out / "final-report.json").write_text(
        json.dumps(final, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(final, ensure_ascii=False), flush=True)

if __name__ == "__main__":
    main()
