#!/usr/bin/env python3
"""Controlled BACKDOOR_BPE continuation from a byte-level MINIRONIN checkpoint.

Consumes only a canonical JSONL train projection. It never reads the project holdout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from minironin import MiniRoninLM, ModelConfig
from minironin.tokenizer import BASE_ACTIVE_VOCAB, ByteNgramTokenizer, initialize_added_embeddings
from train_seed_tournament import MIX_WEIGHTS


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_train_docs(path: Path, tokenizer: ByteNgramTokenizer):
    docs = defaultdict(list)
    seen = set()
    corpus_hash = hashlib.sha256()
    records = 0
    with path.open(encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("split") != "train" or row.get("train_eligible") is not True:
                raise SystemExit(f"{path}:{line_no}: only admitted train rows are allowed")
            if row.get("admission_status") != "admitted":
                raise SystemExit(f"{path}:{line_no}: non-admitted row rejected")
            document_id = str(row.get("document_id", "")).strip()
            text = row.get("text")
            domain = str(row.get("domain", "general")).strip().lower() or "general"
            if not document_id or not isinstance(text, str) or len(text.strip()) < 80:
                continue
            if document_id in seen:
                continue
            seen.add(document_id)
            encoded = tokenizer.encode(text, add_eos=True)
            if len(encoded) < 2:
                continue
            docs[domain].append({"document_id": document_id, "tokens": encoded})
            corpus_hash.update(document_id.encode() + b"\0" + hashlib.sha256(text.encode()).digest())
            records += 1
    if not docs:
        raise SystemExit("No admitted training documents found")
    # Derive a deterministic internal validation slice from the train projection.
    train, validation = defaultdict(list), defaultdict(list)
    for domain, items in docs.items():
        items.sort(key=lambda x: x["document_id"])
        if len(items) < 2:
            train[domain].extend(items)
            continue
        for item in items:
            bucket = int(hashlib.sha256(item["document_id"].encode()).hexdigest()[:8], 16) % 10
            (validation if bucket == 0 else train)[domain].append(item)
        if not validation[domain]:
            validation[domain].append(train[domain].pop())
        if not train[domain]:
            train[domain].append(validation[domain].pop())
    weights = {d: MIX_WEIGHTS.get(d, 0.01) for d in train}
    total = sum(weights.values())
    names = sorted(train)
    probs = [weights[d] / total for d in names]
    return train, validation, names, probs, {
        "documents": records,
        "documents_by_domain_train": {k: len(v) for k, v in train.items()},
        "documents_by_domain_validation": {k: len(v) for k, v in validation.items()},
        "train_projection_sha256": corpus_hash.hexdigest(),
        "source_jsonl_sha256": sha256_file(path),
        "split": "deterministic document hash modulo 10 from train-only projection",
    }


def make_batch(docs, names, probs, tokenizer, step, batch_size, seq_len, seed, eos_fraction):
    rng = random.Random(seed + step)
    rows = []
    for _ in range(batch_size):
        domain = rng.choices(names, weights=probs, k=1)[0]
        ids = rng.choice(docs[domain])["tokens"]
        max_start = max(0, len(ids) - seq_len - 1)
        if max_start and rng.random() < eos_fraction:
            start = max_start
        else:
            start = rng.randrange(max_start + 1) if max_start else 0
        window = ids[start:start + seq_len + 1]
        if len(window) < seq_len + 1:
            window = window + [256] * (seq_len + 1 - len(window))
        rows.append(torch.tensor(window, dtype=torch.long))
    return torch.stack(rows)


def evaluate(model, validation, names, tokenizer, seq_len, device, seed=314159):
    model.eval()
    losses = []
    by_domain = {}
    total_nll = 0.0
    total_bytes = 0
    eos_nll = 0.0
    eos_count = 0
    rng = random.Random(seed)
    with torch.inference_mode():
        for domain in sorted(validation):
            domain_losses = []
            for _ in range(8):
                item = rng.choice(validation[domain])
                ids = item["tokens"]
                max_start = max(0, len(ids) - seq_len - 1)
                start = rng.randrange(max_start + 1) if max_start else 0
                window = ids[start:start + seq_len + 1]
                if len(window) < seq_len + 1:
                    continue
                batch = torch.tensor([window], dtype=torch.long, device=device)
                logits, loss = model(batch, labels=batch, vocab_limit=tokenizer.active_vocab)
                domain_losses.append(float(loss))
                targets = batch[:, 1:]
                token_losses = torch.nn.functional.cross_entropy(
                    logits[:, :-1, :].contiguous().view(-1, tokenizer.active_vocab),
                    targets.contiguous().view(-1),
                    reduction="none",
                )
                for token_id, token_loss in zip(targets.reshape(-1).tolist(), token_losses.tolist()):
                    if token_id == 256:
                        eos_nll += token_loss
                        eos_count += 1
                    else:
                        total_nll += token_loss
                        total_bytes += tokenizer.byte_length(token_id)
            if domain_losses:
                by_domain[domain] = sum(domain_losses) / len(domain_losses)
                losses.extend(domain_losses)
    model.train()
    bits_per_byte = (total_nll / total_bytes / math.log(2)) if total_bytes else None
    eos_loss = (eos_nll / eos_count) if eos_count else None
    return (sum(losses) / len(losses) if losses else None), by_domain, bits_per_byte, eos_loss

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-checkpoint", type=Path, required=True)
    parser.add_argument("--train-jsonl", type=Path, required=True)
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--start-step", type=int, required=True)
    parser.add_argument("--steps", type=int, default=10000)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--sequence-length", type=int, default=128)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=3e-5)
    parser.add_argument("--eos-window-fraction", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=20261109)
    args = parser.parse_args()
    if args.steps < 1 or args.start_step < 0 or args.batch_size < 1 or args.sequence_length < 1:
        parser.error("steps, batch-size and sequence-length must be positive; start-step non-negative")
    if not 0 <= args.eos_window_fraction <= 1:
        parser.error("--eos-window-fraction must be in [0,1]")
    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(args.seed)
    tokenizer = ByteNgramTokenizer.load(args.tokenizer)
    config = ModelConfig.load(ROOT / "configs/model-10m.json")
    if tokenizer.active_vocab > config.vocab_size:
        raise SystemExit("Tokenizer exceeds configured model vocabulary")

    model = MiniRoninLM(config).cpu()
    source = torch.load(args.input_checkpoint, map_location="cpu", weights_only=False)
    if source.get("parameter_count") != model.parameter_count():
        raise SystemExit("Checkpoint parameter count mismatch")
    if source.get("model_config") != config.__dict__:
        raise SystemExit("Checkpoint model config mismatch")
    source_vocab = int(source.get("active_vocabulary", 0))
    if source_vocab not in (BASE_ACTIVE_VOCAB, tokenizer.active_vocab):
        raise SystemExit("Checkpoint active vocabulary is incompatible")
    if source_vocab == tokenizer.active_vocab and source.get("tokenizer_sha256") != tokenizer.sha256:
        raise SystemExit("Refusing tokenizer drift: checkpoint hash differs")
    if source_vocab == BASE_ACTIVE_VOCAB and tokenizer.active_vocab > BASE_ACTIVE_VOCAB:
        if source.get("tokenizer_sha256") not in (None, "", "byte-v1"):
            raise SystemExit("Unexpected tokenizer metadata on byte checkpoint")
    model.load_state_dict(source["model_state_dict"], strict=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, betas=(0.9, 0.95), weight_decay=0.01)
    if "optimizer_state_dict" not in source:
        raise SystemExit("Checkpoint lacks optimizer state; refusing an implicit optimizer reset")
    optimizer.load_state_dict(source["optimizer_state_dict"])
    optimizer.param_groups[0]["lr"] = args.learning_rate
    if source.get("torch_rng_state") is not None:
        torch.set_rng_state(source["torch_rng_state"])
    if source_vocab == BASE_ACTIVE_VOCAB and tokenizer.active_vocab > BASE_ACTIVE_VOCAB:
        byte_rows_before = model.token_embedding.weight[:BASE_ACTIVE_VOCAB].detach().clone()
        initialize_added_embeddings(model, tokenizer, optimizer)
        if not torch.equal(byte_rows_before, model.token_embedding.weight[:BASE_ACTIVE_VOCAB]):
            raise RuntimeError("BACKDOOR_BPE initialization modified legacy byte/EOS embeddings")
    if source.get("completed_steps") != args.start_step:
        raise SystemExit("Checkpoint completed_steps does not match --start-step")

    train_docs, validation, names, probs, corpus_manifest = load_train_docs(args.train_jsonl, tokenizer)
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    model.train()
    losses = []
    started = time.perf_counter()
    for local_step in range(1, args.steps + 1):
        global_step = args.start_step + local_step
        batch = make_batch(train_docs, names, probs, tokenizer, global_step, args.batch_size,
                           args.sequence_length, args.seed, args.eos_window_fraction)
        optimizer.zero_grad(set_to_none=True)
        _, loss = model(batch, labels=batch, vocab_limit=tokenizer.active_vocab)
        if not torch.isfinite(loss):
            raise RuntimeError(f"Non-finite loss at step {global_step}")
        loss.backward()
        grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        losses.append(float(loss.detach()))
        if local_step % 100 == 0:
            print(json.dumps({"step": global_step, "loss": losses[-1], "grad_norm": float(grad_norm)}), flush=True)

    validation_loss, validation_by_domain, validation_bits_per_byte, validation_eos_loss = evaluate(
        model, validation, names, tokenizer, args.sequence_length, torch.device("cpu")
    )
    if validation_loss is None or validation_bits_per_byte is None:
        raise SystemExit("Internal validation produced no usable token windows")
    completed = args.start_step + args.steps
    checkpoint = {
        "model_state_dict": {k: v.detach().cpu() for k, v in model.state_dict().items()},
        "optimizer_state_dict": optimizer.state_dict(),
        "model_config": source["model_config"],
        "parameter_count": model.parameter_count(),
        "seed": source.get("seed"),
        "completed_steps": completed,
        "total_steps": max(int(source.get("total_steps", completed)), completed),
        "active_vocabulary": tokenizer.active_vocab,
        "tokenization": "BACKDOOR_BPE: deterministic longest-match UTF-8 byte n-grams + byte fallback + EOS=256",
        "tokenizer_sha256": tokenizer.sha256,
        "tokenizer_manifest": str(args.tokenizer),
        "tokenizer_manifest_sha256": sha256_file(args.tokenizer),
        "validation_loss": validation_loss,
        "validation_loss_by_domain": validation_by_domain,
        "validation_bits_per_byte": validation_bits_per_byte,
        "validation_eos_loss": validation_eos_loss,
        "dataset_manifest": corpus_manifest,
        "torch_rng_state": torch.get_rng_state(),
    }
    path = output / f"checkpoint-{completed:06d}.pt"
    torch.save(checkpoint, path)
    report = {
        "status": "segment_completed",
        "completed_steps": completed,
        "start_steps": args.start_step,
        "segment_steps": args.steps,
        "parameter_count": model.parameter_count(),
        "active_vocabulary": tokenizer.active_vocab,
        "tokenizer_sha256": tokenizer.sha256,
        "training_corpus": corpus_manifest,
        "eos_window_fraction": args.eos_window_fraction,
        "mean_train_loss": sum(losses) / len(losses),
        "validation_loss_internal": validation_loss,
        "validation_loss_by_domain": validation_by_domain,
        "validation_bits_per_byte": validation_bits_per_byte,
        "validation_eos_loss": validation_eos_loss,
        "elapsed_seconds": round(time.perf_counter() - started, 2),
        "holdout_read": False,
    }
    (output / f"report-{completed:06d}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    digest = sha256_file(path)
    (output / f"checkpoint-{completed:06d}.sha256").write_text(f"{digest}  {path.name}\n")
    print(json.dumps({"checkpoint": str(path), "sha256": digest, **report}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
