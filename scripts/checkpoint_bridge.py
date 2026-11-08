#!/usr/bin/env python3
"""Inspect MINIRONIN checkpoints and export Transformer teacher targets.

This tool never trains or modifies a checkpoint. Teacher exports contain byte-token
IDs and top-k soft targets so a different architecture (for example Mamba) can
learn the teacher's output distribution in a later, separately authorized run.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from minironin import MiniRoninLM, ModelConfig  # noqa: E402


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_checkpoint(path: Path) -> tuple[dict, dict, str]:
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    if not isinstance(checkpoint, dict):
        raise ValueError("Checkpoint root must be a dictionary")
    state = checkpoint.get("model_state_dict")
    if not isinstance(state, dict) or not state:
        raise ValueError("Checkpoint has no non-empty model_state_dict")
    config = checkpoint.get("model_config")
    if not isinstance(config, dict):
        raise ValueError("Checkpoint has no model_config dictionary")
    return checkpoint, state, sha256_file(path)


def inspect_checkpoint(path: Path) -> dict:
    checkpoint, state, digest = read_checkpoint(path)
    tensors = {}
    for name, value in sorted(state.items()):
        if not isinstance(value, torch.Tensor):
            continue
        tensors[name] = {
            "shape": list(value.shape),
            "dtype": str(value.dtype),
            "numel": value.numel(),
            "finite": bool(torch.isfinite(value).all()) if value.is_floating_point() else True,
        }
    return {
        "path": str(path),
        "sha256": digest,
        "architecture": checkpoint.get("architecture", "transformer-minironin"),
        "model_config": checkpoint["model_config"],
        "parameter_count_declared": checkpoint.get("parameter_count"),
        "parameter_count_observed": sum(x.numel() for x in state.values() if isinstance(x, torch.Tensor)),
        "completed_steps": checkpoint.get("completed_steps", checkpoint.get("steps")),
        "active_vocabulary": checkpoint.get("active_vocabulary", 257),
        "tokenization": checkpoint.get("tokenization", "UTF-8 bytes + EOS=256"),
        "parent_checkpoint_sha256": checkpoint.get("parent_checkpoint_sha256"),
        "optimizer_state_present": "optimizer_state_dict" in checkpoint,
        "tensor_inventory": tensors,
    }


def export_teacher(checkpoint_path: Path, prompts_path: Path, output_path: Path,
                   top_k: int, temperature: float, max_context: int) -> dict:
    checkpoint, state, digest = read_checkpoint(checkpoint_path)
    if checkpoint.get("architecture", "").startswith("mamba"):
        raise ValueError("This exporter currently requires a MiniRonin Transformer teacher")
    config = ModelConfig(**checkpoint["model_config"])
    model = MiniRoninLM(config).cpu()
    model.load_state_dict(state, strict=True)
    model.eval()

    active_vocab = int(checkpoint.get("active_vocabulary", 257))
    if active_vocab != 257:
        raise ValueError(f"Expected byte vocabulary 257, got {active_vocab}")
    if top_k < 1 or top_k >= active_vocab:
        raise ValueError(f"top-k must be between 1 and {active_vocab - 1}")
    if temperature <= 0 or not math.isfinite(temperature):
        raise ValueError("temperature must be finite and positive")
    if max_context < 2 or max_context > config.context_length:
        raise ValueError("max-context must be between 2 and the teacher context length")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    opener = gzip.open if output_path.name.endswith(".gz") else open
    rows = 0
    with prompts_path.open("r", encoding="utf-8") as source, opener(
        output_path, "wt", encoding="utf-8"
    ) as target:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            item = json.loads(line)
            text = item.get("text")
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"Prompt line {line_number} must contain non-empty text")
            ids = list(text.encode("utf-8", errors="replace"))[-(max_context - 1):]
            if not ids:
                continue
            input_ids = torch.tensor([ids], dtype=torch.long)
            with torch.inference_mode():
                logits, _ = model(input_ids, vocab_limit=active_vocab)
                distribution = torch.softmax(logits[0].float() / temperature, dim=-1)
                values, indices = torch.topk(distribution, k=top_k, dim=-1)
            record = {
                "id": item.get("id", f"prompt-{line_number}"),
                "input_ids": ids,
                "teacher_topk_ids": indices.tolist(),
                "teacher_topk_probs": values.tolist(),
                "teacher_tail_mass": (1.0 - values.sum(dim=-1)).clamp_min(0).tolist(),
                "teacher_sha256": digest,
                "temperature": temperature,
                "active_vocabulary": active_vocab,
                "target_semantics": "per-position next-token distribution over UTF-8 byte IDs 0..255 and EOS=256",
            }
            target.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
            rows += 1

    manifest = {
        "format": "minironin-teacher-topk-v1",
        "teacher_checkpoint": str(checkpoint_path),
        "teacher_sha256": digest,
        "teacher_completed_steps": checkpoint.get("completed_steps", checkpoint.get("steps")),
        "teacher_config": checkpoint["model_config"],
        "active_vocabulary": active_vocab,
        "tokenization": "UTF-8 bytes 0..255 plus EOS=256",
        "prompt_source": str(prompts_path),
        "prompt_source_sha256": sha256_file(prompts_path),
        "output": str(output_path),
        "output_sha256": sha256_file(output_path),
        "records": rows,
        "top_k": top_k,
        "temperature": temperature,
        "max_context": max_context,
        "training_performed": False,
        "candidate_promotion": False,
    }
    manifest_path = output_path.with_suffix(output_path.suffix + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    inspect_parser = sub.add_parser("inspect", help="inventory checkpoint metadata and tensor shapes")
    inspect_parser.add_argument("--checkpoint", required=True, type=Path)
    export_parser = sub.add_parser("export-teacher", help="export Transformer top-k soft targets; does not train")
    export_parser.add_argument("--checkpoint", required=True, type=Path)
    export_parser.add_argument("--prompts", required=True, type=Path, help="JSONL with one {text,id?} record per line")
    export_parser.add_argument("--output", required=True, type=Path, help="Use .gz for gzip compression")
    export_parser.add_argument("--top-k", type=int, default=16)
    export_parser.add_argument("--temperature", type=float, default=1.0)
    export_parser.add_argument("--max-context", type=int, default=128)
    args = parser.parse_args()

    if args.command == "inspect":
        print(json.dumps(inspect_checkpoint(args.checkpoint), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(export_teacher(
            args.checkpoint, args.prompts, args.output,
            args.top_k, args.temperature, args.max_context,
        ), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
