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
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "src"))
from minironin.mamba import MambaRoninLM  # noqa: E402

ACTIVE_VOCAB = 257
EOS_ID = 256
EXPECTED_PARENT_SHA = "bfe4959e7b51a42eb6e14543a5d6d6b4c2d0dce443ed4944d509f20c83acc730"
EXPECTED_CANDIDATE_SHA = "d4e94c6b2711810bc07ce91b9fdcf4cfd50466a6ee9eafe70b64f023f211d5d7"


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
    if len(rows) != 100:
        raise ValueError(f"Expected the fixed 100-question holdout, got {len(rows)}")
    return rows


def init_cache(model: MambaRoninLM):
    """Create per-layer causal-convolution and selective-SSM recurrent states."""
    cache = []
    for block in model.blocks:
        device = block.in_proj.weight.device
        dtype = block.in_proj.weight.dtype
        conv = torch.zeros(1, block.d_inner, block.conv1d.kernel_size[0] - 1,
                           device=device, dtype=dtype)
        prefix = torch.ones(1, block.d_inner, block.d_state, device=device, dtype=dtype)
        accumulator = torch.zeros(1, block.d_inner, block.d_state, device=device, dtype=dtype)
        cache.append((conv, prefix, accumulator))
    return cache


def step_token(model: MambaRoninLM, token: torch.Tensor, cache):
    """Consume exactly one token and return its logits plus updated recurrent state."""
    x = model.token_embedding(token)
    updated = []
    for block, (conv_cache, prefix_cache, accumulator_cache) in zip(model.blocks, cache):
        residual = x
        normalized = block.norm(x)
        xz = block.in_proj(normalized)
        x_branch, z = xz.chunk(2, dim=-1)

        # Match Conv1d(padding=d_conv-1) followed by causal right-cropping,
        # but evaluate only the newest position and retain its left history.
        conv_input = torch.cat((conv_cache, x_branch.transpose(1, 2)), dim=-1)
        conv = F.conv1d(conv_input, block.conv1d.weight, block.conv1d.bias,
                        groups=block.d_inner)
        next_conv_cache = conv_input[:, :, 1:]
        x_branch = F.silu(conv.transpose(1, 2))

        params = block.x_proj(x_branch)
        dt_raw, B, C = torch.split(
            params, [block.dt_rank, block.d_state, block.d_state], dim=-1
        )
        dt = F.softplus(block.dt_proj(dt_raw)).clamp(max=1.0)
        A = -torch.exp(block.A_log).to(dtype=x_branch.dtype)
        decay = torch.exp(dt.squeeze(1).unsqueeze(-1) *
                          A.view(1, block.d_inner, block.d_state))
        drive = (dt.squeeze(1).unsqueeze(-1) *
                 B.squeeze(1).unsqueeze(1) *
                 x_branch.squeeze(1).unsqueeze(-1))
        # Reproduce the reference parallel scan exactly, including its 1e-8
        # prefix floor: prefix_t = clamp(prefix_(t-1) * decay_t).
        next_prefix = (prefix_cache * decay).clamp_min(1e-8)
        next_accumulator = accumulator_cache + drive / next_prefix
        state = next_prefix * next_accumulator
        y = ((state.unsqueeze(1) * C.unsqueeze(2)).sum(dim=-1) +
             block.D.view(1, 1, -1) * x_branch)
        y = y * F.silu(z)
        x = residual + block.out_proj(y)
        updated.append((next_conv_cache, next_prefix, next_accumulator))

    x = model.final_norm(x)
    logits = F.linear(x, model.lm_head.weight[:ACTIVE_VOCAB])
    return logits, updated


def prefill(model: MambaRoninLM, token_ids: list[int]):
    """Run the prompt once, carrying state forward token by token."""
    cache = init_cache(model)
    logits = None
    for token_id in token_ids:
        token = torch.tensor([[token_id]], dtype=torch.long)
        logits, cache = step_token(model, token, cache)
    if logits is None:
        raise ValueError("Cannot prefill an empty prompt")
    return logits, cache


def verify_incremental_equivalence(model: MambaRoninLM, sample: list[int]) -> float:
    """Fail closed if recurrent decoding differs from the model's full forward pass."""
    sample = sample[:min(96, model.context_length)]
    ids = torch.tensor([sample], dtype=torch.long)
    reference, _ = model(ids, vocab_limit=ACTIVE_VOCAB)
    cache = init_cache(model)
    observed = []
    for token_id in sample:
        logits, cache = step_token(
            model, torch.tensor([[token_id]], dtype=torch.long), cache
        )
        observed.append(logits)
    actual = torch.cat(observed, dim=1)
    max_error = float((reference - actual).abs().max().item())
    if not torch.allclose(reference, actual, rtol=2e-4, atol=2e-5):
        raise RuntimeError(
            f"Incremental Mamba equivalence check failed (max_abs_error={max_error})"
        )
    return max_error


def generate(model: MambaRoninLM, question: str, max_new_tokens: int) -> tuple[list[int], str]:
    encoded = list((question.strip() + "\nRespuesta:").encode("utf-8", errors="replace"))
    prompt = encoded[-model.context_length:]
    logits, cache = prefill(model, prompt)
    generated: list[int] = []
    for _ in range(max_new_tokens):
        next_id = int(torch.argmax(logits[0, -1, :]).item())
        if next_id == EOS_ID:
            break
        generated.append(next_id)
        encoded.append(next_id)
        if len(encoded) > model.context_length:
            # Preserve the original evaluator's sliding context semantics.
            logits, cache = prefill(model, encoded[-model.context_length:])
        else:
            logits, cache = step_token(
                model, torch.tensor([[next_id]], dtype=torch.long), cache
            )
    return generated, bytes(generated).decode("utf-8", errors="replace").strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--holdout", type=Path, default=ROOT / "benchmarks/inference-holdout-v1.jsonl")
    parser.add_argument("--baseline-diary", type=Path, default=None, help="Optional diary generated from the exact parent checkpoint on this same 100-question holdout")
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
    rows = load_holdout(args.holdout)
    base = None
    base_by_id = {}
    if args.baseline_diary:
        base = json.loads(args.baseline_diary.read_text(encoding="utf-8"))
        if base.get("checkpoint_sha256") != EXPECTED_PARENT_SHA:
            raise SystemExit("Baseline diary is not from the exact verified parent checkpoint")
        if base.get("holdout_sha256") != holdout_sha or base.get("holdout_count") != len(rows):
            raise SystemExit("Baseline diary does not use this exact 100-question holdout")
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
    equivalence_error = verify_incremental_equivalence(
        model, list((rows[0]["question"].strip() + "\nRespuesta:").encode("utf-8"))
    )
    print(json.dumps({"incremental_equivalence_max_abs_error": equivalence_error}), flush=True)

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
                "changed_vs_parent": answer != base_by_id[row["id"]] if base is not None else None,
            })
            print(json.dumps({"holdout_progress": index, "id": row["id"],
                              "generated_bytes": len(token_ids)}, ensure_ascii=False), flush=True)

    comparison = None
    if base is not None:
        changed = sum(item["changed_vs_parent"] for item in results)
        comparison = {
            "baseline_label": base["label"], "baseline_checkpoint_sha256": base["checkpoint_sha256"],
            "identical_answers": len(results) - changed, "changed_answers": changed,
            "answer_change_rate": round(changed / len(results), 6),
            "note": "Text differences are descriptive only, not a quality score. Human blind review required."
        }
    diary = {
        "schema_version": 1,
        "benchmark": "MINIRONIN inference holdout v2 (100 questions)",
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
                       "max_new_tokens": args.max_new_tokens, "threads": args.threads,
                       "decoder": "incremental_recurrent_state",
                       "equivalence_max_abs_error": equivalence_error},
        "comparison_to_parent": comparison,
        "scoring": {"status": "unscored_raw_generation",
                    "reason": "The holdout rubric is preserved for independent human review."},
        "elapsed_seconds": round(time.perf_counter() - started_all, 3),
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(diary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: diary[k] for k in (
        "label", "completed_steps", "parameter_count", "checkpoint_sha256",
        "holdout_sha256", "holdout_count", "comparison_to_parent", "elapsed_seconds"
    )}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
