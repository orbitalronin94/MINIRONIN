from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import torch

from scripts.run_inference_holdout import generate_tokens, load_holdout


ROOT = Path(__file__).resolve().parents[1]


def test_inference_holdout_is_fixed_and_has_unique_ids():
    rows = load_holdout(ROOT / "benchmarks/inference-holdout-v1.jsonl")
    assert len(rows) == 40
    assert len({row["id"] for row in rows}) == 40
    assert {row["domain"] for row in rows} >= {
        "logic", "math", "causality", "probability",
        "instruction_following", "contradiction", "uncertainty",
    }


def test_greedy_generation_stops_on_eos():
    class FakeModel:
        config = SimpleNamespace(context_length=16)

        def __call__(self, input_ids, vocab_limit):
            logits = torch.zeros((1, input_ids.shape[1], vocab_limit))
            logits[0, -1, 256] = 1.0
            return logits, None

    tokens, answer = generate_tokens(FakeModel(), "Pregunta", max_new_tokens=8)
    assert tokens == []
    assert answer == ""


def test_holdout_prompts_are_not_training_behavior_prompts():
    holdout = load_holdout(ROOT / "benchmarks/inference-holdout-v1.jsonl")
    training = [
        json.loads(line)["question"]
        for line in (ROOT / "data/curated/minironin-behavior-v1.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert not ({row["question"] for row in holdout} & set(training))
