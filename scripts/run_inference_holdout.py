#!/usr/bin/env python3
"""Run the immutable MINIRONIN inference holdout against one checkpoint."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "src"))
from minironin import MiniRoninLM, ModelConfig  # noqa: E402

ACTIVE_VOCAB = 257
EOS_ID = 256
DEFAULT_MAX_NEW_TOKENS = 128


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_holdout(path: Path) -> list[dict]:
    rows = []
    seen = set()
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
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
    if not rows:
        raise ValueError("Holdout is empty")
    return rows


def generate_tokens(model: MiniRoninLM, prompt: str, max_new_tokens: int) -> tuple[list[int], str]:
    encoded = list(prompt.encode("utf-8", errors="replace"))
    if not encoded:
        raise ValueError("Prompt encoded to an empty sequence")
    generated: list[int] = []
    context = model.config.context_length
    for _ in range(max_new_tokens):
        input_ids = torch.tensor([encoded[-context:]], dtype=torch.long)
        logits, _ = model(input_ids, vocab_limit=ACTIVE_VOCAB)
        next_id = int(torch.argmax(logits[0, -1, :]).item())
        if next_id == EOS_ID:
            break
        generated.append(next_id)
        encoded.append(next_id)
    answer = bytes(generated).decode("utf-8", errors="replace").strip()
    return generated, answer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--label", required=True)
    parser.add_argument("--steps", required=True, type=int)
    parser.add_argument("--holdout", type=Path, default=ROOT / "benchmarks/inference-holdout-v1.jsonl")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_NEW_TOKENS)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--base-diary", type=Path)
    args = parser.parse_args()

    if args.max_new_tokens < 1 or args.max_new_tokens > 512:
        parser.error("--max-new-tokens must be between 1 and 512")
    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(0)

    holdout = load_holdout(args.holdout)
    config = ModelConfig.load(ROOT / "configs/model-10m.json")
    model = MiniRoninLM(config).cpu()
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    if checkpoint.get("active_vocabulary") != ACTIVE_VOCAB:
        raise SystemExit("Checkpoint active vocabulary is not 257; refusing incomparable inference")
    if checkpoint.get("parameter_count") != model.parameter_count():
        raise SystemExit("Checkpoint parameter count does not match this model")
    if checkpoint.get("model_config") != asdict(config):
        raise SystemExit("Checkpoint model config differs from repository config")
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    model.eval()

    checkpoint_sha = sha256_file(args.checkpoint)
    holdout_sha = sha256_file(args.holdout)
    results = []
    with torch.inference_mode():
        for row in holdout:
            prompt = row["question"].strip() + "\nRespuesta:"
            prompt_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
            started = time.perf_counter()
            token_ids, answer = generate_tokens(model, prompt, args.max_new_tokens)
            elapsed = time.perf_counter() - started
            results.append({
                "id": row["id"],
                "domain": row["domain"],
                "question": row["question"],
                "rubric": row["rubric"],
                "prompt": prompt,
                "prompt_sha256": prompt_sha,
                "answer": answer,
                "generated_token_ids": token_ids,
                "generated_bytes": len(token_ids),
                "elapsed_seconds": round(elapsed, 6),
            })

    comparison = None
    if args.base_diary:
        base = json.loads(args.base_diary.read_text(encoding="utf-8"))
        base_by_id = {item["id"]: item["answer"] for item in base["results"]}
        if set(base_by_id) != {item["id"] for item in results}:
            raise SystemExit("Base diary does not contain the exact same holdout IDs")
        changed = sum(item["answer"] != base_by_id[item["id"]] for item in results)
        deltas = [len(item["answer"]) - len(base_by_id[item["id"]]) for item in results]
        comparison = {
            "reference": "base",
            "identical_answers": len(results) - changed,
            "changed_answers": changed,
            "answer_change_rate": round(changed / len(results), 6),
            "mean_character_delta_vs_base": round(statistics.mean(deltas), 3),
            "note": "Descriptive text-difference metrics only; not a quality score.",
        }

    diary = {
        "schema_version": 1,
        "benchmark": "MINIRONIN inference holdout v1",
        "label": args.label,
        "completed_steps": args.steps,
        "seed": checkpoint.get("seed"),
        "parameter_count": checkpoint.get("parameter_count"),
        "active_vocabulary": checkpoint.get("active_vocabulary"),
        "tokenization": checkpoint.get("tokenization", "UTF-8 bytes + EOS"),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "checkpoint_file": args.checkpoint.name,
        "checkpoint_sha256": checkpoint_sha,
        "holdout_file": str(args.holdout),
        "holdout_sha256": holdout_sha,
        "holdout_count": len(results),
        "generation": {
            "method": "greedy argmax",
            "temperature": 0,
            "max_new_tokens": args.max_new_tokens,
            "prompt_suffix": "\\nRespuesta:",
            "threads": args.threads,
            "model_mode": "eval",
        },
        "comparison_to_base": comparison,
        "scoring": {
            "status": "unscored_raw_generation",
            "reason": "Human blind review is required; no automatic semantic-quality claim is made.",
        },
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(diary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "label": args.label,
        "completed_steps": args.steps,
        "holdout_count": len(results),
        "checkpoint_sha256": checkpoint_sha,
        "holdout_sha256": holdout_sha,
        "comparison_to_base": comparison,
        "output": str(args.output),
    }, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
