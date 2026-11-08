#!/usr/bin/env python3
"""Evaluate the 50M Mamba candidate on MINIRONIN's immutable inference holdout."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "src"))
from minironin.mamba import MambaRoninLM  # noqa: E402

ACTIVE_VOCAB = 257
EOS_ID = 256
EXPECTED_PARENT_SHA = "bfe4959e7b51a42eb6e14543a5d6d6b4c2d0dce443ed4944d509f20c83acc730"
EXPECTED_CANDIDATE_SHA = "d4e94c6b2711810bc07ce91b9fdcf4cfd50466a6ee9eafe70b64f023f211d5d7"
EXPECTED_HOLDOUT_SHA = "22dce842390cd2075a214cb01e69091baa82b990dfd8a9657c1f1b787d21b06d"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_holdout(path: Path) -> list[dict]:
    rows, seen = [], set()
    with path.open(encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            for key in ("id", "domain", "question", "rubric"):
                if not row.get(key):
                    raise ValueError(f"{path}:{line_no}: missing {key}")
            if row["id"] in seen:
                raise ValueError(f"duplicate holdout id: {row['id']}")
            seen.add(row["id"])
            rows.append(row)
    if len(rows) != 40:
        raise ValueError(f"Expected the fixed 40-question holdout, got {len(rows)}")
    return rows


def generate(model: MambaRoninLM, question: str, max_new_tokens: int) -> tuple[list[int], str]:
    encoded = list((question.strip() + "\nRespuesta:").encode("utf-8", errors="replace"))
    generated: list[int] = []
    for _ in range(max_new_tokens):
        input_ids = torch.tensor([encoded[-model.context_length:]], dtype=torch.long)
        logits, _ = model(input_ids, vocab_limit=ACTIVE_VOCAB)
        next_id = int(torch.argmax(logits[0, -1, :]).item())
        if next_id == EOS_ID:
            break
        generated.append(next_id)
        encoded.append(next_id)
    return generated, bytes(generated).decode("utf-8", errors="replace").strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--holdout", type=Path, default=ROOT / "benchmarks/inference-holdout-v1.jsonl")
    parser.add_argument("--baseline-diary", type=Path, default=ROOT / "benchmarks/diary/checkpoint-390000.json")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-new-tokens", type=int, default=128)
    parser.add_argument("--threads", type=int, default=2)
    args = parser.parse_args()

    if not 1 <= args.max_new_tokens <= 512:
        parser.error("--max-new-tokens must be between 1 and 512")
    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(0)

    candidate_sha = sha256_file(args.checkpoint)
    if candidate_sha != EXPECTED_CANDIDATE_SHA:
        raise SystemExit(f"Unexpected candidate checkpoint SHA-256: {candidate_sha}")
    holdout_sha = sha256_file(args.holdout)
    if holdout_sha != EXPECTED_HOLDOUT_SHA:
        raise SystemExit(f"Unexpected holdout SHA-256: {holdout_sha}")

    rows = load_holdout(args.holdout)
    base = json.loads(args.baseline_diary.read_text(encoding="utf-8"))
    if base.get("checkpoint_sha256") != EXPECTED_PARENT_SHA:
        raise SystemExit("390k baseline diary is not the exact verified parent checkpoint")
    if base.get("holdout_sha256") != holdout_sha or base.get("holdout_count") != len(rows):
        raise SystemExit("Baseline diary does not use this exact holdout")
    base_by_id = {item["id"]: item["answer"] for item in base["results"]}
    if set(base_by_id) != {row["id"] for row in rows}:
        raise SystemExit("Baseline diary holdout IDs differ")

    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    if checkpoint.get("architecture") != "mamba-selective-scan-v1":
        raise SystemExit("Checkpoint architecture is not the expected Mamba model")
    if checkpoint.get("completed_steps") != 1000:
        raise SystemExit("Expected the 1,000-step candidate")
    if checkpoint.get("parent_checkpoint_sha256") != EXPECTED_PARENT_SHA:
        raise SystemExit("Candidate parent checkpoint SHA-256 mismatch")
    if checkpoint.get("active_vocabulary") != ACTIVE_VOCAB:
        raise SystemExit("Candidate active vocabulary is not 257")
    config = dict(checkpoint["model_config"])
    config.pop("architecture", None)
    model = MambaRoninLM(**config).cpu()
    if model.parameter_count() != checkpoint.get("parameter_count") or model.parameter_count() != 49_083_392:
        raise SystemExit("Candidate parameter count does not match instantiated Mamba architecture")
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    model.eval()

    results = []
    started_all = time.perf_counter()
    with torch.inference_mode():
        for index, row in enumerate(rows, 1):
            started = time.perf_counter()
            token_ids, answer = generate(model, row["question"], args.max_new_tokens)
            results.append({
                "id": row["id"], "domain": row["domain"], "question": row["question"],
                "rubric": row["rubric"], "answer": answer,
                "generated_token_ids": token_ids, "generated_bytes": len(token_ids),
                "elapsed_seconds": round(time.perf_counter() - started, 6),
                "changed_vs_390k": answer != base_by_id[row["id"]],
            })
            print(json.dumps({"holdout_progress": index, "id": row["id"],
                              "generated_bytes": len(token_ids)}, ensure_ascii=False), flush=True)

    changed = sum(item["changed_vs_390k"] for item in results)
    diary = {
        "schema_version": 1,
        "benchmark": "MINIRONIN inference holdout v1",
        "label": "mamba-50m-from-390k-step-1000",
        "architecture": checkpoint["architecture"],
        "completed_steps": checkpoint["completed_steps"],
        "parameter_count": checkpoint["parameter_count"],
        "active_vocabulary": ACTIVE_VOCAB,
        "tokenization": checkpoint.get("tokenization", "UTF-8 bytes + EOS"),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "checkpoint_sha256": candidate_sha,
        "parent_checkpoint_sha256": checkpoint["parent_checkpoint_sha256"],
        "holdout_sha256": holdout_sha,
        "holdout_count": len(results),
        "generation": {"method": "greedy argmax", "temperature": 0,
                       "max_new_tokens": args.max_new_tokens, "threads": args.threads},
        "comparison_to_390k": {
            "baseline_label": base["label"], "baseline_checkpoint_sha256": base["checkpoint_sha256"],
            "identical_answers": len(results) - changed, "changed_answers": changed,
            "answer_change_rate": round(changed / len(results), 6),
            "note": "Text differences are descriptive only, not a quality score. Human blind review required."
        },
        "scoring": {"status": "unscored_raw_generation",
                    "reason": "The holdout rubric is preserved for independent human review."},
        "elapsed_seconds": round(time.perf_counter() - started_all, 3),
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(diary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: diary[k] for k in (
        "label", "completed_steps", "parameter_count", "checkpoint_sha256",
        "holdout_sha256", "holdout_count", "comparison_to_390k", "elapsed_seconds"
    )}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
