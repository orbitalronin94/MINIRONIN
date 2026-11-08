#!/usr/bin/env python3
"""Expand the verified 390k MINIRONIN checkpoint to ~50M parameters and adapt on all text datasets."""
from __future__ import annotations
import argparse, hashlib, json, math, random, sys, time
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from minironin import MiniRoninLM, ModelConfig
from train_long_run import ACTIVE_VOCAB, load_training_data, batch_for_step, evaluate
from build_abstention_datasets import main as build_abstention_datasets
from build_personality_datasets import main as build_personality_datasets

PARENT_SHA256 = "bfe4959e7b51a42eb6e14543a5d6d6b4c2d0dce443ed4944d509f20c83acc730"
TARGET_CONFIG = ModelConfig(vocab_size=23000, context_length=512, n_layers=14,
                            d_model=512, n_heads=8, d_ff=1536,
                            dropout=0.0, layer_norm_eps=1e-5)
TOTAL_STEPS = 1000
CHECKPOINT_STEPS = (250, 500, 750, 1000)


def transfer_state(old_state, target_model):
    """Exact zero-padded width expansion; preserve all original activations."""
    new = target_model.state_dict()
    scale_qk = 2.0 ** 0.25

    def copy_prefix(dst, src, rows=None, cols=None, scale=1.0, fill=None):
        if fill is not None:
            dst.fill_(fill)
        if rows is None:
            rows = src.shape[0]
        if cols is None:
            cols = src.shape[1] if src.ndim > 1 else None
        if src.ndim == 1:
            dst[:rows].copy_(src[:rows] * scale)
        else:
            dst[:rows, :cols].copy_(src[:rows, :cols] * scale)

    for key, value in old_state.items():
        if key in ("token_embedding.weight", "position_embedding.weight"):
            new[key].zero_()
            new[key][:, :256].copy_(value)
        elif key == "lm_head.weight":
            # Tied with token_embedding; preserve identical expanded tensor.
            new[key].zero_()
            new[key][:, :256].copy_(old_state["token_embedding.weight"])
        elif key == "final_norm.weight":
            new[key].fill_(1.0)
            new[key][:256].copy_(value)
        elif key == "final_norm.bias":
            new[key].zero_()
            new[key][:256].copy_(value)
        elif key.startswith("blocks."):
            parts = key.split(".")
            layer = int(parts[1])
            if layer >= 6:
                continue
            tail = ".".join(parts[2:])
            prefix = f"blocks.{layer}."
            if tail in ("ln_1.weight", "ln_2.weight"):
                new[key].fill_(1.0)
                new[key][:256].copy_(value)
            elif tail in ("ln_1.bias", "ln_2.bias"):
                new[key].zero_()
                new[key][:256].copy_(value)
            elif tail == "attn.qkv.weight":
                new[key].zero_()
                for group in range(3):
                    scale = scale_qk if group < 2 else 1.0
                    new[key][group * 512:group * 512 + 256, :256].copy_(
                        value[group * 256:(group + 1) * 256, :] * scale
                    )
            elif tail == "attn.qkv.bias":
                new[key].zero_()
                for group in range(3):
                    scale = scale_qk if group < 2 else 1.0
                    new[key][group * 512:group * 512 + 256].copy_(
                        value[group * 256:(group + 1) * 256] * scale
                    )
            elif tail == "attn.proj.weight":
                new[key].zero_()
                new[key][:256, :256].copy_(value)
            elif tail == "attn.proj.bias":
                new[key].zero_()
                new[key][:256].copy_(value)
            elif tail == "mlp.fc_in.weight":
                new[key].zero_()
                new[key][:768, :256].copy_(value)
            elif tail == "mlp.fc_in.bias":
                new[key].zero_()
                new[key][:768].copy_(value)
            elif tail == "mlp.fc_out.weight":
                new[key].zero_()
                new[key][:256, :768].copy_(value)
            elif tail == "mlp.fc_out.bias":
                new[key].zero_()
                new[key][:256].copy_(value)
            else:
                raise RuntimeError("Unhandled source parameter: " + key)
        else:
            raise RuntimeError("Unhandled source parameter: " + key)

    # New residual blocks start as exact identities.
    for layer in range(6, 14):
        prefix = f"blocks.{layer}."
        for suffix in ("attn.proj.weight", "attn.proj.bias",
                       "mlp.fc_out.weight", "mlp.fc_out.bias"):
            new[prefix + suffix].zero_()

    target_model.load_state_dict(new, strict=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input-checkpoint", required=True)
    p.add_argument("--heretic-root", required=True)
    p.add_argument("--books-root", required=True)
    p.add_argument("--output-dir", default="scale-50m")
    p.add_argument("--dataset-cache", default="scale-50m/full-corpus-cache.pt")
    p.add_argument("--threads", type=int, default=2)
    args = p.parse_args()

    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(20261108)
    device = torch.device("cpu")

    parent_path = Path(args.input_checkpoint)
    parent_hash = hashlib.sha256(parent_path.read_bytes()).hexdigest()
    if parent_hash != PARENT_SHA256:
        raise SystemExit(f"Parent SHA-256 mismatch: {parent_hash}")
    parent = torch.load(parent_path, map_location="cpu", weights_only=False)
    if parent.get("completed_steps") != 390000 or parent.get("parameter_count") != 9970176:
        raise SystemExit("Expected the exact 390k / 9,970,176-parameter parent")
    if parent.get("active_vocabulary") != ACTIVE_VOCAB:
        raise SystemExit("Parent active vocabulary mismatch")

    print("GENERATING_ALL_CURATED_DATASETS", flush=True)
    build_abstention_datasets()
    build_personality_datasets()
    print("BUILDING_FULL_CORPUS", flush=True)
    train_docs, names, probs, validation, data_manifest = load_training_data(
        Path(args.heretic_root), Path(args.books_root), Path(args.dataset_cache)
    )
    required = {"math", "science", "books", "behavior", "abstention",
                "abstain_plain", "abstain_literary", "abstain_koan",
                "aristocrat", "casuist", "scientist", "oracle",
                "indifference", "lexicon"}
    if not required.issubset(set(names)):
        raise SystemExit("All-datasets guard failed; loaded domains: " + repr(names))
    print(json.dumps({"training_domains": names, "sampling_weights": dict(zip(names, probs)),
                      "documents_by_domain": data_manifest.get("documents_by_domain"),
                      "dataset_manifest": data_manifest}, ensure_ascii=False), flush=True)

    old_config = ModelConfig(**parent["model_config"])
    if (old_config.d_model, old_config.n_heads, old_config.d_ff, old_config.n_layers) != (256, 8, 768, 6):
        raise SystemExit("Unexpected 390k parent architecture; refusing unsafe transfer")
    old_model = MiniRoninLM(old_config).to(device)
    old_model.load_state_dict(parent["model_state_dict"], strict=True)
    old_model.eval()

    model = MiniRoninLM(TARGET_CONFIG).to(device)
    if model.parameter_count() != 48825344:
        raise SystemExit(f"Unexpected 50M architecture size: {model.parameter_count()}")
    transfer_state(parent["model_state_dict"], model)

    # Verify that widening plus identity-initialized added blocks preserves the parent function.
    probe = torch.tensor([[1, 2, 3, 4, 5, 6, 7, 8]], dtype=torch.long)
    with torch.no_grad():
        old_logits, _ = old_model(probe, vocab_limit=ACTIVE_VOCAB)
        new_logits, _ = model(probe, vocab_limit=ACTIVE_VOCAB)
    transfer_error = float((old_logits - new_logits).abs().max())
    if not torch.allclose(old_logits, new_logits, atol=2e-5, rtol=2e-5):
        raise SystemExit(f"Function-preserving transfer check failed: max_abs_error={transfer_error}")
    print(json.dumps({"transfer_check": "passed", "max_abs_logit_error": transfer_error,
                      "parent_parameters": 9970176, "expanded_parameters": model.parameter_count(),
                      "architecture": TARGET_CONFIG.__dict__}), flush=True)

    baseline_loss, baseline_domains = evaluate(model, validation, device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5, betas=(0.9, 0.95), weight_decay=0.01)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "experiment-manifest.json").write_text(json.dumps({
        "experiment": "390k-to-50m-transfer-all-datasets-1000-steps",
        "parent_step": 390000, "parent_sha256": parent_hash,
        "parent_parameter_count": 9970176, "expanded_parameter_count": model.parameter_count(),
        "target_model_config": TARGET_CONFIG.__dict__,
        "transfer": "zero-padded 2x width expansion with Q/K scale correction; 8 new residual blocks zero-output identity initialization",
        "transfer_max_abs_logit_error": transfer_error,
        "training_steps": TOTAL_STEPS, "batch_size": 2, "sequence_length": 128,
        "active_vocabulary": ACTIVE_VOCAB, "training_domains": names,
        "sampling_weights": dict(zip(names, probs)), "dataset_manifest": data_manifest,
        "baseline_validation_loss": baseline_loss, "baseline_validation_by_domain": baseline_domains,
        "optimizer": "fresh AdamW; parent optimizer state intentionally not reused after architecture expansion"
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    started = time.perf_counter()
    model.train()
    losses = []
    for step in range(1, TOTAL_STEPS + 1):
        warmup = min(1.0, step / 50)
        cosine = 0.5 * (1.0 + math.cos(math.pi * step / TOTAL_STEPS))
        lr = 5e-5 * warmup * (0.15 + 0.85 * cosine)
        for group in optimizer.param_groups:
            group["lr"] = lr
        batch = batch_for_step(train_docs, names, probs, step, seed_offset=50000000).to(device)
        optimizer.zero_grad(set_to_none=True)
        _, loss = model(batch, labels=batch, vocab_limit=ACTIVE_VOCAB)
        if not torch.isfinite(loss):
            raise RuntimeError(f"Non-finite loss at step {step}")
        loss.backward()
        grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        losses.append(float(loss.detach()))
        if step % 50 == 0:
            print(json.dumps({"additional_step": step, "global_parent_step_equivalent": 390000 + step,
                              "train_loss": losses[-1], "lr": lr, "grad_norm": float(grad_norm)}), flush=True)
        if step in CHECKPOINT_STEPS:
            val_loss, val_domains = evaluate(model, validation, device)
            cp = out / f"checkpoint-50m-step-{step}.pt"
            payload = {
                "model_state_dict": {k: v.detach().cpu() for k, v in model.state_dict().items()},
                "optimizer_state_dict": optimizer.state_dict(),
                "model_config": TARGET_CONFIG.__dict__,
                "parameter_count": model.parameter_count(), "seed": 20261108,
                "completed_steps": step, "parent_completed_steps": 390000,
                "total_steps": TOTAL_STEPS, "active_vocabulary": ACTIVE_VOCAB,
                "tokenization": parent.get("tokenization", "UTF-8 bytes + EOS"),
                "validation_loss": val_loss, "validation_loss_by_domain": val_domains,
                "parent_checkpoint_sha256": parent_hash,
                "transfer_max_abs_logit_error": transfer_error,
                "training_scope": "all compatible HERETIC text + PRODATPHIL + all MINIRONIN curated datasets",
                "dataset_manifest": data_manifest, "torch_rng_state": torch.get_rng_state()
            }
            torch.save(payload, cp)
            digest = hashlib.sha256(cp.read_bytes()).hexdigest()
            report = {
                "status": "candidate_only", "additional_steps": step,
                "parent_step": 390000, "parameter_count": model.parameter_count(),
                "validation_loss_before": baseline_loss, "validation_loss_after": val_loss,
                "validation_loss_by_domain_before": baseline_domains,
                "validation_loss_by_domain_after": val_domains,
                "mean_train_loss_last_100": sum(losses[-100:]) / min(100, len(losses)),
                "elapsed_seconds": round(time.perf_counter() - started, 2),
                "checkpoint_sha256": digest, "transfer_max_abs_logit_error": transfer_error,
                "dataset_manifest": "experiment-manifest.json"
            }
            rp = out / f"report-50m-step-{step}.json"
            rp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (out / f"SHA256SUMS-step-{step}").write_text(
                f"{digest}  {cp.name}\n{hashlib.sha256(rp.read_bytes()).hexdigest()}  {rp.name}\n",
                encoding="utf-8")
            print(json.dumps({"checkpoint": str(cp), "report": report}, ensure_ascii=False), flush=True)
    print("SCALE_50M_TRAINING_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
