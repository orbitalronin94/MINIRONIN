from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import torch

from scripts.run_inference_holdout import generate_tokens, load_holdout


ROOT = Path(__file__).resolve().parents[1]


def test_inference_holdout_is_fixed_and_has_unique_ids():
    rows = load_holdout(ROOT / "benchmarks/inference-holdout-v1.jsonl")
    assert len(rows) == 100
    assert len({row["id"] for row in rows}) == 100
    assert sum(row["domain"] == "ci_cd" for row in rows) == 35
    assert sum(row["domain"] == "personality_troll" for row in rows) == 25
    assert all(row["split"] == "inference_only" for row in rows[40:])
    assert {row["domain"] for row in rows} >= {
        "logic", "math", "causality", "probability",
        "instruction_following", "contradiction", "uncertainty",
        "ci_cd", "personality_troll",
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


def test_cached_forward_matches_full_forward_logits():
    from minironin import MiniRoninLM, ModelConfig

    torch.manual_seed(7)
    config = ModelConfig(
        vocab_size=257, context_length=32, n_layers=2,
        d_model=16, n_heads=4, d_ff=32, dropout=0.0,
    )
    model = MiniRoninLM(config).eval()
    tokens = torch.tensor([[65, 66, 67, 68, 69, 70]], dtype=torch.long)
    with torch.inference_mode():
        full, _ = model(tokens, vocab_limit=257)
        cache = None
        incremental = []
        for index in range(tokens.shape[1]):
            logits, cache = model.forward_cached(tokens[:, index:index + 1], cache)
            incremental.append(logits)
    cached = torch.cat(incremental, dim=1)
    assert torch.allclose(full, cached, atol=2e-5, rtol=2e-5)


def test_cached_and_reference_greedy_tokens_match():
    from minironin import MiniRoninLM, ModelConfig

    torch.manual_seed(11)
    config = ModelConfig(
        vocab_size=257, context_length=32, n_layers=2,
        d_model=16, n_heads=4, d_ff=32, dropout=0.0,
    )
    model = MiniRoninLM(config).eval()
    prompt = "¿Qué es una prueba?\\nRespuesta:"
    with torch.inference_mode():
        cached = generate_tokens(model, prompt, 12, use_cache=True)
        reference = generate_tokens(model, prompt, 12, use_cache=False)
    assert cached == reference
