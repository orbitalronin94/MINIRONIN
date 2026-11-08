#!/usr/bin/env python3
"""Migrate MINIRONIN 500k byte checkpoint to a corpus-trained 23k byte-BPE vocabulary and train 10k steps."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
import time
from collections import Counter
from pathlib import Path

import torch
from tokenizers import Tokenizer, decoders, models, pre_tokenizers, trainers

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
from minironin import MiniRoninLM, ModelConfig  # noqa: E402
from train_long_run import load_training_data, BATCH_SIZE, SEQUENCE_LENGTH, BASE_SEED  # noqa: E402

PARENT_STEPS = 500_000
TRAIN_STEPS = 10_000
EOS_ID = 256
ACTIVE_VOCAB = 23_000
TOKENIZER_INTERNAL_SIZE = ACTIVE_VOCAB - 1  # 256 byte symbols + 22,743 learned merges
D_MODEL = 256


def bytes_to_unicode():
    """GPT-2 byte alphabet, bijective over all 256 byte values."""
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("¡"), ord("¬") + 1)) + list(range(ord("®"), ord("ÿ") + 1))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return {b: chr(c) for b, c in zip(bs, cs)}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_tokenizer(train_docs, work_dir: Path):
    work_dir.mkdir(parents=True, exist_ok=True)
    # Four balanced corpus shards let the Rust BPE trainer process files in parallel.
    # They are four inputs to ONE tokenizer, not four independently trained vocabularies.
    shard_count = 4
    shard_paths = [work_dir / f"tokenizer-training-shard-{i + 1}-of-{shard_count}.txt" for i in range(shard_count)]
    shard_docs = [0] * shard_count
    shard_bytes = [0] * shard_count
    with [path.open("w", encoding="utf-8", newline="\n") for path in shard_paths] as handles:
        for domain in sorted(train_docs):
            for doc_index, doc in enumerate(train_docs[domain]):
                text = doc["text"].replace("\r", " ").replace("\n", " ")
                if text:
                    shard = (doc_index + sum(shard_docs)) % shard_count
                    payload = text + "\n"
                    handles[shard].write(payload)
                    shard_docs[shard] += 1
                    shard_bytes[shard] += len(payload.encode("utf-8"))
    for i in range(shard_count):
        print(json.dumps({"tokenizer_shard": i + 1, "documents": shard_docs[i], "bytes": shard_bytes[i]}), flush=True)

    tokenizer = Tokenizer(models.BPE(unk_token=None))
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tokenizer.decoder = decoders.ByteLevel()
    trainer = trainers.BpeTrainer(
        vocab_size=TOKENIZER_INTERNAL_SIZE,
        min_frequency=2,
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
        show_progress=True,
        special_tokens=[],
    )
    tokenizer.train([str(path) for path in shard_paths], trainer=trainer)
    actual = tokenizer.get_vocab_size(with_added_tokens=False)
    if actual != TOKENIZER_INTERNAL_SIZE:
        raise RuntimeError(
            f"Corpus yielded {actual} BPE entries; exactly {TOKENIZER_INTERNAL_SIZE} are required "
            "to activate every reserved model row without synthetic tokens."
        )

    byte_map = bytes_to_unicode()
    reverse = {char: byte for byte, char in byte_map.items()}
    id_to_model = {}
    id_to_token = {}
    for internal_id in range(actual):
        token = tokenizer.id_to_token(internal_id)
        if internal_id < 256:
            if len(token) != 1 or token not in reverse:
                raise RuntimeError(f"Initial byte alphabet is not stable at tokenizer ID {internal_id}: {token!r}")
            model_id = reverse[token]
        else:
            model_id = internal_id + 1  # Leave model ID 256 exclusively for EOS.
        if not 0 <= model_id < ACTIVE_VOCAB:
            raise RuntimeError(f"Mapped token ID out of range: {internal_id} -> {model_id}")
        id_to_model[internal_id] = model_id
        id_to_token[model_id] = token
    if set(id_to_model.values()) != set(range(ACTIVE_VOCAB)) - {EOS_ID}:
        raise RuntimeError("Tokenizer mapping does not cover every non-EOS model ID exactly once")

    tokenizer_path = work_dir / "semantic-tokenizer.json"
    tokenizer.save(str(tokenizer_path))
    return tokenizer, id_to_model, reverse, tokenizer_path, shard_paths


def encode_text(tokenizer, id_to_model, text: str) -> list[int]:
    encoded = tokenizer.encode(text).ids
    return [id_to_model[i] for i in encoded] + [EOS_ID]


def make_validation(validation_bytes, tokenizer, id_to_model):
    batches = []
    for domain, byte_batches in sorted(validation_bytes.items()):
        rows = []
        for batch in byte_batches:
            for row in batch:
                raw = bytes(x for x in row.tolist() if 0 <= x <= 255)
                text = raw.decode("utf-8", errors="replace")
                ids = encode_text(tokenizer, id_to_model, text)
                if len(ids) >= SEQUENCE_LENGTH + 1:
                    start = max(0, (len(ids) - SEQUENCE_LENGTH - 1) // 2)
                    rows.append(torch.tensor(ids[start:start + SEQUENCE_LENGTH + 1], dtype=torch.long))
        if rows:
            batches.append((domain, rows))
    return batches


def evaluate(model, validation, device):
    model.eval()
    totals, counts, per_domain = {}, {}, {}
    with torch.inference_mode():
        for domain, rows in validation:
            losses = []
            for start in range(0, len(rows), BATCH_SIZE):
                selected = rows[start:start + BATCH_SIZE]
                if len(selected) != BATCH_SIZE:
                    continue
                batch = torch.stack(selected).to(device)
                _, loss = model(batch, labels=batch, vocab_limit=ACTIVE_VOCAB)
                losses.append(float(loss))
            if losses:
                per_domain[domain] = sum(losses) / len(losses)
                totals[domain] = sum(losses)
                counts[domain] = len(losses)
    if not per_domain:
        raise RuntimeError("No usable tokenized validation batches")
    weighted = sum(totals[d] for d in totals) / sum(counts.values())
    model.train()
    return weighted, per_domain


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-checkpoint", required=True)
    parser.add_argument("--output-dir", default="semantic-10k")
    parser.add_argument("--heretic-root", required=True)
    parser.add_argument("--books-root", required=True)
    parser.add_argument("--anarchist-root", required=True)
    parser.add_argument("--classics-root", required=True)
    parser.add_argument("--dataset-cache", required=True)
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()

    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    device = torch.device("cpu")
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    parent_path = Path(args.parent_checkpoint)
    parent_hash = sha256(parent_path)
    parent = torch.load(parent_path, map_location="cpu", weights_only=False)
    if parent.get("completed_steps") != PARENT_STEPS:
        raise SystemExit("Parent checkpoint must be exactly step 500000")
    if parent.get("parameter_count") != 9_970_176 or parent.get("active_vocabulary") != 257:
        raise SystemExit("Parent checkpoint architecture or byte vocabulary does not match the expected 500k baseline")
    if parent.get("tokenization") != "UTF-8 bytes + EOS":
        raise SystemExit("Unexpected parent tokenization")
    if "optimizer_state_dict" not in parent:
        raise SystemExit("Parent optimizer state is required for a real continuation")

    train_docs, names, probs, validation_bytes, dataset_manifest = load_training_data(
        Path(args.heretic_root), Path(args.books_root), Path(args.anarchist_root),
        Path(args.classics_root), Path(args.dataset_cache)
    )
    tokenizer, id_to_model, byte_reverse, tokenizer_path, shard_paths = build_tokenizer(
        train_docs, out / "tokenizer"
    )

    config = ModelConfig.load(ROOT / "configs/model-10m.json")
    model = MiniRoninLM(config).to(device)
    model.load_state_dict(parent["model_state_dict"], strict=True)
    with torch.no_grad():
        embedding = model.token_embedding.weight
        legacy = embedding[:257].detach().clone()
        # New BPE rows start as the length-normalized mean of their UTF-8 byte embeddings.
        for internal_id in range(256, TOKENIZER_INTERNAL_SIZE):
            model_id = internal_id + 1
            token = tokenizer.id_to_token(internal_id)
            byte_ids = [byte_reverse[ch] for ch in token if ch in byte_reverse]
            if not byte_ids:
                raise RuntimeError(f"Learned token has no recoverable UTF-8 byte sequence: {token!r}")
            embedding[model_id].copy_(embedding[torch.tensor(byte_ids, dtype=torch.long)].mean(dim=0))
        if not torch.equal(embedding[:257], legacy):
            raise RuntimeError("Migration altered legacy byte/EOS embedding rows")
        if model.lm_head.weight.data_ptr() != model.token_embedding.weight.data_ptr():
            raise RuntimeError("Tied embedding/output weights were lost during migration")

    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-5, betas=(0.9, 0.95), weight_decay=0.01)
    optimizer.load_state_dict(parent["optimizer_state_dict"])
    for group in optimizer.param_groups:
        group["lr"] = 3e-5
    # New vocabulary rows have no valid byte-phase Adam moments; start their moments at zero.
    state = optimizer.state[model.token_embedding.weight]
    for key in ("exp_avg", "exp_avg_sq", "max_exp_avg_sq"):
        if key in state and torch.is_tensor(state[key]) and state[key].shape == model.token_embedding.weight.shape:
            state[key][257:].zero_()

    validation = make_validation(validation_bytes, tokenizer, id_to_model)
    before_loss, before_by_domain = evaluate(model, validation, device)

    rng = random.Random(BASE_SEED + PARENT_STEPS)
    encoded_cache = {}
    def sample_batch(global_step):
        local_rng = random.Random(BASE_SEED + global_step)
        domains = local_rng.choices(names, weights=probs, k=BATCH_SIZE)
        rows = []
        for domain in domains:
            doc = local_rng.choice(train_docs[domain])
            key = (domain, id(doc))
            if key not in encoded_cache:
                encoded_cache[key] = encode_text(tokenizer, id_to_model, doc["text"])
            ids = encoded_cache[key]
            if len(ids) < SEQUENCE_LENGTH + 1:
                raise RuntimeError(f"Tokenized document too short in domain {domain}")
            start = local_rng.randrange(0, len(ids) - SEQUENCE_LENGTH)
            rows.append(torch.tensor(ids[start:start + SEQUENCE_LENGTH + 1], dtype=torch.long))
        return torch.stack(rows)

    started = time.perf_counter()
    losses = []
    model.train()
    for step in range(1, TRAIN_STEPS + 1):
        global_step = PARENT_STEPS + step
        batch = sample_batch(global_step).to(device)
        optimizer.zero_grad(set_to_none=True)
        _, loss = model(batch, labels=batch, vocab_limit=ACTIVE_VOCAB)
        if not torch.isfinite(loss):
            raise RuntimeError(f"Non-finite semantic-vocabulary loss at step {global_step}")
        loss.backward()
        grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        losses.append(float(loss.detach()))
        if step % 100 == 0:
            print(json.dumps({"step": global_step, "loss": losses[-1], "grad_norm": float(grad_norm)}), flush=True)

    after_loss, after_by_domain = evaluate(model, validation, device)
    elapsed = round(time.perf_counter() - started, 2)
    checkpoint_path = out / "checkpoint-510000-semantic-bpe.pt"
    checkpoint = {
        "model_state_dict": {k: v.detach().cpu() for k, v in model.state_dict().items()},
        "optimizer_state_dict": optimizer.state_dict(),
        "model_config": parent["model_config"],
        "parameter_count": 9_970_176,
        "seed": parent.get("seed"),
        "completed_steps": 510_000,
        "total_steps": 510_000,
        "active_vocabulary": ACTIVE_VOCAB,
        "tokenization": "UTF-8 byte fallback IDs 0..255; EOS=256; corpus-trained ByteLevel BPE IDs 257..22999",
        "tokenizer_file": "semantic-tokenizer.json",
        "tokenizer_sha256": sha256(tokenizer_path),
        "parent_checkpoint_sha256": parent_hash,
        "validation_loss_before": before_loss,
        "validation_loss_after": after_loss,
        "dataset_manifest": dataset_manifest,
    }
    torch.save(checkpoint, checkpoint_path)
    report = {
        "status": "completed",
        "parent_checkpoint_sha256": parent_hash,
        "parent_steps": PARENT_STEPS,
        "completed_steps": 510_000,
        "additional_steps": TRAIN_STEPS,
        "parameter_count": 9_970_176,
        "active_vocabulary": ACTIVE_VOCAB,
        "legacy_ids_preserved": "0..256",
        "learned_bpe_ids": "257..22999",
        "learned_bpe_entries": TOKENIZER_INTERNAL_SIZE - 256,
        "eos_id": EOS_ID,
        "eos_supervised": True,
        "embedding_initialization": "length-normalized mean of UTF-8 byte embeddings",
        "optimizer": "restored from parent; new vocabulary Adam moments zeroed",
        "validation_loss_before": before_loss,
        "validation_loss_before_by_domain": before_by_domain,
        "validation_loss_after": after_loss,
        "validation_loss_after_by_domain": after_by_domain,
        "mean_train_loss_last_100": sum(losses[-100:]) / 100,
        "elapsed_seconds": elapsed,
        "tokenizer_sha256": sha256(tokenizer_path),
        "checkpoint_sha256": sha256(checkpoint_path),
        "dataset_manifest": dataset_manifest,
        "promotion": "candidate_only; fixed 100-question generation holdout still required",
    }
    report_path = out / "semantic-training-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "SHA256SUMS").write_text(
        f"{sha256(checkpoint_path)}  {checkpoint_path.name}\n"
        f"{sha256(tokenizer_path)}  {tokenizer_path.name}\n"
        f"{sha256(report_path)}  {report_path.name}\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
