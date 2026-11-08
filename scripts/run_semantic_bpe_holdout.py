#!/usr/bin/env python3
"""Run the fixed 100-question holdout against a semantic-BPE MINIRONIN checkpoint."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import torch
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from minironin import MiniRoninLM, ModelConfig  # noqa: E402

ACTIVE_VOCAB = 23_000
EOS_ID = 256
DEFAULT_MAX_NEW_TOKENS = 128


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def bytes_to_unicode() -> dict[int, str]:
    bs = list(range(ord("!"), ord("~") + 1))
    bs += list(range(ord("¡"), ord("¬") + 1))
    bs += list(range(ord("®"), ord("ÿ") + 1))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return {b: chr(c) for b, c in zip(bs, cs)}


def tokenizer_maps(tokenizer: Tokenizer) -> tuple[dict[int, int], dict[int, int]]:
    byte_map = bytes_to_unicode()
    reverse = {char: byte for byte, char in byte_map.items()}
    internal_to_model: dict[int, int] = {}
    model_to_internal: dict[int, int] = {}
    size = tokenizer.get_vocab_size(with_added_tokens=False)
    if size != ACTIVE_VOCAB - 1:
        raise SystemExit(f"Expected 22,999 tokenizer entries, found {size}")
    for internal_id in range(size):
        token = tokenizer.id_to_token(internal_id)
        if internal_id < 256:
            if token not in reverse:
                raise SystemExit(f"Unrecognized byte alphabet token at {internal_id}: {token!r}")
            model_id = reverse[token]
        else:
            model_id = internal_id + 1
        internal_to_model[internal_id] = model_id
        model_to_internal[model_id] = internal_id
    expected = set(range(ACTIVE_VOCAB)) - {EOS_ID}
    if set(model_to_internal) != expected:
        raise SystemExit("Semantic tokenizer/model ID mapping is incomplete")
    return internal_to_model, model_to_internal


def load_holdout(path: Path) -> list[dict]:
    rows, seen = [], set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        for key in ("id", "domain", "question", "rubric"):
            if not row.get(key):
                raise ValueError(f"{path}:{line_number}: missing {key}")
        if row["id"] in seen:
            raise ValueError(f"Duplicate holdout id: {row['id']}")
        seen.add(row["id"])
        rows.append(row)
    if len(rows) != 100:
        raise ValueError(f"Expected exactly 100 holdout questions, found {len(rows)}")
    return rows


def generate(model, tokenizer, internal_to_model, model_to_internal, prompt: str, max_new_tokens: int):
    prompt_internal = tokenizer.encode(prompt).ids
    encoded = [internal_to_model[i] for i in prompt_internal]
    if not encoded:
        raise ValueError("Prompt encoded to an empty sequence")
    generated: list[int] = []
    context = model.config.context_length
    for _ in range(max_new_tokens):
        # forward_cached currently caps logits at 257; semantic BPE requires the
        # full 23k vocabulary, so use the reference sliding-window path.
        input_ids = torch.tensor([encoded[-context:]], dtype=torch.long)
        logits, _ = model(input_ids, vocab_limit=ACTIVE_VOCAB)
        next_id = int(torch.argmax(logits[0, -1, :]).item())
        if next_id == EOS_ID:
            break
        if next_id not in model_to_internal:
            raise RuntimeError(f"Generated model token {next_id} has no tokenizer mapping")
        generated.append(next_id)
        encoded.append(next_id)
    decoded = tokenizer.decode([model_to_internal[token_id] for token_id in generated]).strip()
    return generated, decoded


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--tokenizer", required=True, type=Path)
    parser.add_argument("--label", default="transformer-10m-510000-semantic-bpe-candidate")
    parser.add_argument("--steps", type=int, default=510000)
    parser.add_argument("--holdout", type=Path, default=ROOT / "benchmarks/inference-holdout-v1.jsonl")
    parser.add_argument("--base-diary", type=Path, default=ROOT / "benchmarks/diary/checkpoint-500000.json")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_NEW_TOKENS)
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()

    if args.max_new_tokens < 1 or args.max_new_tokens > 512:
        parser.error("--max-new-tokens must be between 1 and 512")
    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(0)

    holdout = load_holdout(args.holdout)
    tokenizer = Tokenizer.from_file(str(args.tokenizer))
    internal_to_model, model_to_internal = tokenizer_maps(tokenizer)
    config = ModelConfig.load(ROOT / "configs/model-10m.json")
    model = MiniRoninLM(config).cpu()
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    if checkpoint.get("completed_steps") != args.steps:
        raise SystemExit(f"Expected step {args.steps}, found {checkpoint.get('completed_steps')}")
    if checkpoint.get("active_vocabulary") != ACTIVE_VOCAB:
        raise SystemExit("Checkpoint active vocabulary is not 23,000")
    if checkpoint.get("parameter_count") != model.parameter_count():
        raise SystemExit("Checkpoint parameter count does not match model")
    if checkpoint.get("model_config") != asdict(config):
        raise SystemExit("Checkpoint model config differs from repository config")
    tokenizer_sha = sha256_file(args.tokenizer)
    if checkpoint.get("tokenizer_sha256") != tokenizer_sha:
        raise SystemExit("Checkpoint/tokenizer SHA-256 mismatch")
    tokenization = str(checkpoint.get("tokenization", "")).lower()
    if "bytelevel bpe" not in tokenization or "257..22999" not in tokenization:
        raise SystemExit(
            "Checkpoint tokenization metadata is incompatible with the expected "
            "ByteLevel BPE model IDs 257..22999"
        )
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    model.eval()

    checkpoint_sha = sha256_file(args.checkpoint)
    holdout_sha = sha256_file(args.holdout)
    results = []
    with torch.inference_mode():
        for index, row in enumerate(holdout, 1):
            prompt = row["question"].strip() + "\nRespuesta:"
            prompt_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
            started = time.perf_counter()
            token_ids, answer = generate(
                model, tokenizer, internal_to_model, model_to_internal,
                prompt, args.max_new_tokens,
            )
            results.append({
                "id": row["id"], "domain": row["domain"], "question": row["question"],
                "rubric": row["rubric"], "prompt": prompt, "prompt_sha256": prompt_sha,
                "answer": answer, "generated_token_ids": token_ids,
                "generated_tokens": len(token_ids),
                "generated_bytes": len(answer.encode("utf-8")),
                "elapsed_seconds": round(time.perf_counter() - started, 6),
            })
            if index % 10 == 0:
                print(json.dumps({"holdout_completed": index, "of": len(holdout)}), flush=True)

    comparison = None
    if args.base_diary.is_file():
        base = json.loads(args.base_diary.read_text(encoding="utf-8"))
        base_by_id = {item["id"]: item["answer"] for item in base["results"]}
        if set(base_by_id) != {item["id"] for item in results}:
            raise SystemExit("500k baseline diary does not contain the exact same 100 holdout IDs")
        changed = sum(item["answer"] != base_by_id[item["id"]] for item in results)
        deltas = [len(item["answer"]) - len(base_by_id[item["id"]]) for item in results]
        comparison = {
            "reference": base.get("label", "500k baseline"),
            "identical_answers": len(results) - changed,
            "changed_answers": changed,
            "answer_change_rate": round(changed / len(results), 6),
            "mean_character_delta_vs_base": round(statistics.mean(deltas), 3),
            "note": "Descriptive text-difference metrics only; not a semantic-quality score.",
        }

    diary = {
        "schema_version": 1,
        "benchmark": "MINIRONIN inference holdout v1 — semantic BPE",
        "label": args.label, "completed_steps": args.steps,
        "seed": checkpoint.get("seed"), "parameter_count": checkpoint.get("parameter_count"),
        "active_vocabulary": ACTIVE_VOCAB,
        "tokenization": checkpoint["tokenization"],
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "checkpoint_file": args.checkpoint.name, "checkpoint_sha256": checkpoint_sha,
        "tokenizer_file": args.tokenizer.name, "tokenizer_sha256": tokenizer_sha,
        "holdout_file": str(args.holdout), "holdout_sha256": holdout_sha,
        "holdout_count": len(results),
        "generation": {
            "method": "greedy argmax", "temperature": 0, "max_new_tokens": args.max_new_tokens,
            "prompt_suffix": "\nRespuesta:", "threads": args.threads,
            "model_mode": "eval", "kv_cache": False,
            "reason": "forward_cached is byte-vocabulary capped at 257; full 23k BPE logits require reference path.",
        },
        "comparison_to_500k": comparison,
        "scoring": {
            "status": "unscored_raw_generation",
            "reason": "Human blind review is required; no automatic semantic-quality claim is made.",
        },
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(diary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "label": args.label, "completed_steps": args.steps, "holdout_count": len(results),
        "checkpoint_sha256": checkpoint_sha, "tokenizer_sha256": tokenizer_sha,
        "holdout_sha256": holdout_sha, "comparison_to_500k": comparison,
        "output": str(args.output),
    }, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
