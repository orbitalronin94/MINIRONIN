#!/usr/bin/env python3
"""Train MAXIRONIN's byte-level BPE on the complete unified corpus and encode it."""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
from pathlib import Path

import numpy as np
from tokenizers import Tokenizer, models, normalizers, pre_tokenizers, decoders, trainers
from tokenizers.pre_tokenizers import Split
from tokenizers import Regex


SPECIAL_TOKENS = ["<PAD>", "<UNK>", "<BOS>", "<EOS>", "<DOC>"]
VOCAB_SIZE = 32768


def records(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            text = row.get("text", "")
            if isinstance(text, str) and text.strip():
                yield row, text


def text_iterator(path: Path):
    for _, text in records(path):
        yield text


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    corpus = Path(args.corpus)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    train_path, val_path = out / "train.bin", out / "validation.bin"

    tokenizer = Tokenizer(models.BPE(unk_token="<UNK>"))
    tokenizer.normalizer = normalizers.NFC()
    tokenizer.pre_tokenizer = pre_tokenizers.Sequence([
        Split(Regex(r"[0-9]"), behavior="isolated"),
        pre_tokenizers.ByteLevel(add_prefix_space=False),
    ])
    tokenizer.decoder = decoders.ByteLevel()
    trainer = trainers.BpeTrainer(
        vocab_size=VOCAB_SIZE,
        min_frequency=2,
        special_tokens=SPECIAL_TOKENS,
        initial_alphabet=sorted(pre_tokenizers.ByteLevel.alphabet()),
        show_progress=True,
    )
    print("TOKENIZER_TRAINING_START", flush=True)
    tokenizer.train_from_iterator(text_iterator(corpus), trainer=trainer)
    actual_vocab = tokenizer.get_vocab_size(with_added_tokens=True)
    if actual_vocab != VOCAB_SIZE:
        raise SystemExit(f"Expected exactly {VOCAB_SIZE} tokens, got {actual_vocab}")
    tokenizer.save(str(out / "tokenizer.json"))
    ids = {token: tokenizer.token_to_id(token) for token in SPECIAL_TOKENS}
    if any(value is None for value in ids.values()):
        raise SystemExit(f"Missing special token IDs: {ids}")
    print(json.dumps({"tokenizer_vocab_size": actual_vocab, "special_token_ids": ids}), flush=True)

    # Stable document-level split. Every document is written to exactly one side.
    train_docs = val_docs = train_tokens = val_tokens = 0
    with train_path.open("wb") as train_file, val_path.open("wb") as val_file:
        for row, text in records(corpus):
            key = str(row.get("source_id", "")) + "|" + str(row.get("id", ""))
            bucket = int(hashlib.sha256(key.encode("utf-8")).hexdigest()[:8], 16) % 100
            target = val_file if bucket < 5 else train_file
            encoded = [ids["<DOC>"], *tokenizer.encode(text).ids, ids["<EOS>"]]
            payload = np.asarray(encoded, dtype="<u2")
            payload.tofile(target)
            if bucket < 5:
                val_docs += 1
                val_tokens += len(encoded)
            else:
                train_docs += 1
                train_tokens += len(encoded)
    if train_tokens < 100_000 or val_tokens < 10_000:
        raise SystemExit(f"Insufficient encoded corpus: train={train_tokens}, validation={val_tokens}")
    manifest = {
        "experiment": "MAXIRONIN-500M",
        "tokenizer": "BPE byte-level (ByteLevel pre-tokenizer and decoder)",
        "vocab_size": actual_vocab,
        "normalization": "Unicode NFC",
        "digits": "isolated one digit per pre-tokenization unit",
        "special_tokens": ids,
        "corpus_file": str(corpus),
        "corpus_sha256": digest_file(corpus),
        "train_documents": train_docs,
        "validation_documents": val_docs,
        "train_tokens": train_tokens,
        "validation_tokens": val_tokens,
        "split": "deterministic 95/5 document-level split by SHA-256(source_id|id)",
        "binary_dtype": "little-endian uint16",
        "training_policy": "Every non-empty text record in the immutable unified corpus is used for tokenizer training and assigned to exactly one train/validation partition.",
    }
    (out / "tokenizer-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
