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
from minironin.tokenizer import ByteNgramTokenizer  # noqa: E402
import rag_retrieve  # noqa: E402

ACTIVE_VOCAB = 257
EOS_ID = 256
DEFAULT_MAX_NEW_TOKENS = 128


def validate_checkpoint_step(checkpoint: dict, expected_steps: int) -> None:
    actual_steps = checkpoint.get("completed_steps")
    if actual_steps != expected_steps:
        raise SystemExit(
            f"Checkpoint completed_steps={actual_steps} "
            f"does not match requested --steps={expected_steps}"
        )


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


def generate_tokens(
    model: MiniRoninLM, prompt: str, max_new_tokens: int, *, use_cache: bool = True,
    tokenizer: ByteNgramTokenizer | None = None, active_vocab: int = ACTIVE_VOCAB,
    max_new_bytes: int | None = None,
) -> tuple[list[int], str, int]:
    encoded = tokenizer.encode(prompt) if tokenizer is not None else list(prompt.encode("utf-8", errors="replace"))
    if not encoded:
        raise ValueError("Prompt encoded to an empty sequence")
    generated: list[int] = []
    generated_bytes = 0
    context = model.config.context_length
    cache = None
    cache_enabled = use_cache and hasattr(model, "forward_cached")
    for _ in range(max_new_tokens):
        if cache_enabled and len(encoded) <= context:
            if cache is None:
                input_ids = torch.tensor([encoded[-context:]], dtype=torch.long)
                logits, cache = model.forward_cached(input_ids)
            else:
                input_ids = torch.tensor([[encoded[-1]]], dtype=torch.long)
                logits, cache = model.forward_cached(input_ids, cache)
        else:
            # Match the reference evaluator's sliding-window positional reset.
            cache = None
            input_ids = torch.tensor([encoded[-context:]], dtype=torch.long)
            logits, _ = model(input_ids, vocab_limit=active_vocab)
        next_id = int(torch.argmax(logits[0, -1, :active_vocab]).item())
        if next_id == EOS_ID:
            break
        token_piece = tokenizer.token_bytes(next_id) if tokenizer is not None else bytes([next_id])
        if max_new_bytes is not None and generated_bytes + len(token_piece) > max_new_bytes:
            break
        generated_bytes += len(token_piece)
        generated.append(next_id)
        encoded.append(next_id)
    answer = (
        tokenizer.decode(generated) if tokenizer is not None
        else bytes(generated).decode("utf-8", errors="replace")
    ).strip()
    return generated, answer, generated_bytes

def _clip_utf8(text: str, max_bytes: int) -> str:
    if max_bytes <= 0:
        return ""
    return text.encode("utf-8")[:max_bytes].decode("utf-8", errors="ignore")


def format_rag_context_for_window(rag_result: dict, max_bytes: int) -> tuple[str, list[str]]:
    """Build compact cited evidence that fits the model's byte-level context window."""
    blocks: list[str] = []
    used_ids: list[str] = []
    remaining = max_bytes
    for index, hit in enumerate(rag_result.get("hits", []), 1):
        locations = hit.get("all_source_locations") or []
        location = locations[0] if locations else {}
        provenance = hit.get("provenance") or {}
        source_id = str(location.get("source_id") or provenance.get("source_id") or "source")
        locator = str(location.get("locator") or hit.get("chunk_id") or "chunk")
        header = f"[S{index}] {source_id}#{locator}: "
        separator = "\n\n" if blocks else ""
        cost = len((separator + header).encode("utf-8"))
        if remaining <= cost:
            break
        excerpt = _clip_utf8(str(hit.get("text", "")).strip(), remaining - cost)
        if not excerpt:
            break
        block = separator + header + excerpt
        blocks.append(block)
        remaining -= len(block.encode("utf-8"))
        used_ids.append(str(hit.get("chunk_id", "")))
        if remaining <= 0:
            break
    return "".join(blocks), used_ids


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--label", required=True)
    parser.add_argument("--steps", required=True, type=int)
    parser.add_argument("--holdout", type=Path, default=ROOT / "benchmarks/inference-holdout-v1.jsonl")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_NEW_TOKENS)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--tokenizer", type=Path, help="BACKDOOR_BPE tokenizer manifest for a tokenizer-matched checkpoint")
    parser.add_argument("--max-new-bytes", type=int, help="Optional fair output byte budget; defaults to --max-new-tokens bytes")
    parser.add_argument("--no-kv-cache", action="store_true", help="Use the slow reference path for parity checks")
    parser.add_argument("--base-diary", type=Path)
    parser.add_argument("--rag-index", type=Path, help="SQLite evidence index built from admitted train documents only")
    parser.add_argument("--rag-top-k", type=int, default=5)
    parser.add_argument("--rag-max-context-chars", type=int, default=6000)
    parser.add_argument("--rag-no-vectors", action="store_true", help="Use deterministic BM25-only retrieval")
    args = parser.parse_args()

    if args.max_new_tokens < 1 or args.max_new_tokens > 512:
        parser.error("--max-new-tokens must be between 1 and 512")
    if args.max_new_bytes is not None and args.max_new_bytes < 1:
        parser.error("--max-new-bytes must be positive")
    if args.rag_top_k < 1 or args.rag_max_context_chars < 1:
        parser.error("--rag-top-k and --rag-max-context-chars must be positive")
    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(0)

    holdout = load_holdout(args.holdout)
    config = ModelConfig.load(ROOT / "configs/model-10m.json")
    model = MiniRoninLM(config).cpu()
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    validate_checkpoint_step(checkpoint, args.steps)
    if checkpoint.get("parameter_count") != model.parameter_count():
        raise SystemExit("Checkpoint parameter count does not match this model")
    if checkpoint.get("model_config") != asdict(config):
        raise SystemExit("Checkpoint model config differs from repository config")
    tokenizer = ByteNgramTokenizer.load(args.tokenizer) if args.tokenizer else None
    active_vocab = tokenizer.active_vocab if tokenizer is not None else ACTIVE_VOCAB
    if checkpoint.get("active_vocabulary") != active_vocab:
        raise SystemExit(f"Checkpoint active vocabulary {checkpoint.get('active_vocabulary')} does not match requested {active_vocab}")
    if tokenizer is not None and checkpoint.get("tokenizer_sha256") != tokenizer.sha256:
        raise SystemExit("Checkpoint tokenizer SHA-256 does not match tokenizer manifest")
    if tokenizer is None and checkpoint.get("active_vocabulary") != ACTIVE_VOCAB:
        raise SystemExit("Non-byte checkpoint requires --tokenizer")
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    model.eval()

    checkpoint_sha = sha256_file(args.checkpoint)
    holdout_sha = sha256_file(args.holdout)
    results = []
    with torch.inference_mode():
        for row in holdout:
            question = row["question"].strip()
            rag_result = None
            rag_context = ""
            rag_context_hit_ids: list[str] = []
            instruction = (
                "Responde en castellano. Si la evidencia no basta, dilo claramente. "
                "No inventes citas ni conviertas similitud en certeza. "
                "Si usas evidencia recuperada, cita su marcador [S#]."
            )
            suffix = "\nRespuesta:"
            if args.rag_index:
                rag_result = rag_retrieve.search(
                    args.rag_index, question, k=args.rag_top_k,
                    use_vectors=not args.rag_no_vectors,
                )
                fixed_bytes = len((instruction + "\n\n" + question + suffix).encode("utf-8"))
                context_budget = max(0, model.config.context_length - fixed_bytes - 2)
                context_budget = min(context_budget, args.rag_max_context_chars)
                rag_context, rag_context_hit_ids = format_rag_context_for_window(
                    rag_result, max_bytes=context_budget,
                )
            prompt = (
                instruction + "\n\n"
                + (rag_context + "\n\n" if rag_context else "")
                + question + suffix
            )
            prompt_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
            started = time.perf_counter()
            token_ids, answer, generated_byte_count = generate_tokens(
                model, prompt, args.max_new_tokens, use_cache=not args.no_kv_cache,
                tokenizer=tokenizer, active_vocab=active_vocab,
                max_new_bytes=args.max_new_bytes or args.max_new_tokens,
            )
            elapsed = time.perf_counter() - started
            results.append({
                "id": row["id"],
                "domain": row["domain"],
                "question": row["question"],
                "rubric": row["rubric"],
                "prompt": prompt,
                "rag_enabled": bool(args.rag_index),
                "rag_hits": [
                    {"chunk_id": hit["chunk_id"], "rrf_score": hit["rrf_score"],
                     "channels": hit["channels"], "source_locations": hit["all_source_locations"],
                     "document_sha256": hit["provenance"].get("document_sha256")}
                    for hit in (rag_result or {}).get("hits", [])
                ],
                "rag_warnings": (rag_result or {}).get("warnings", []),
                "rag_context_hit_ids": rag_context_hit_ids,
                "rag_context_utf8_bytes": len(rag_context.encode("utf-8")),
                "prompt_sha256": prompt_sha,
                "answer": answer,
                "generated_token_ids": token_ids,
                "generated_bytes": generated_byte_count,
                "elapsed_seconds": round(elapsed, 6),
            })

    comparison = None
    if args.base_diary:
        base = json.loads(args.base_diary.read_text(encoding="utf-8"))
        if base.get("checkpoint_sha256") != checkpoint_sha:
            raise SystemExit("Base diary uses a different checkpoint SHA-256")
        if base.get("holdout_sha256") != holdout_sha or base.get("holdout_count") != len(results):
            raise SystemExit("Base diary does not use the exact same holdout snapshot")
        if base.get("completed_steps") != args.steps:
            raise SystemExit("Base diary reports a different checkpoint step count")
        if base.get("rag", {}).get("enabled") is not False:
            raise SystemExit("Paired reference diary must be the no-RAG baseline")
        base_generation = base.get("generation", {})
        if (base_generation.get("max_new_tokens") != args.max_new_tokens
                or base_generation.get("threads") != args.threads
                or base_generation.get("kv_cache") != (not args.no_kv_cache)):
            raise SystemExit("Base diary generation settings differ from this run")
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
        "rag": {
            "enabled": bool(args.rag_index),
            "index_file": str(args.rag_index) if args.rag_index else None,
            "index_sha256": sha256_file(args.rag_index) if args.rag_index else None,
            "top_k": args.rag_top_k if args.rag_index else None,
            "vector_retrieval": bool(args.rag_index) and not args.rag_no_vectors,
            "max_context_chars": args.rag_max_context_chars if args.rag_index else None,
            "index_manifest": (rag_result or {}).get("index_manifest") if results else None,
        },
        "generation": {
            "method": "greedy argmax",
            "temperature": 0,
            "max_new_tokens": args.max_new_tokens,
            "prompt_suffix": "\nRespuesta:",
            "threads": args.threads,
            "model_mode": "eval",
            "kv_cache": not args.no_kv_cache,
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
        "rag_enabled": bool(args.rag_index),
        "checkpoint_sha256": checkpoint_sha,
        "holdout_sha256": holdout_sha,
        "comparison_to_base": comparison,
        "output": str(args.output),
    }, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
