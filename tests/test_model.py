import torch

from minironin import MiniRoninLM, ModelConfig


def test_model_parameter_count_is_exact_baseline():
    model = MiniRoninLM(ModelConfig())
    assert model.parameter_count() == 9_970_176


def test_logits_and_next_token_loss_shapes():
    model = MiniRoninLM(ModelConfig(dropout=0.0))
    tokens = torch.randint(0, 23_000, (2, 32))
    logits, loss = model(tokens, labels=tokens)
    assert logits.shape == (2, 32, 23_000)
    assert loss is not None and torch.isfinite(loss)


def test_causal_attention_does_not_depend_on_future_tokens():
    torch.manual_seed(7)
    model = MiniRoninLM(ModelConfig(dropout=0.0)).eval()
    first = torch.randint(0, 23_000, (1, 16))
    changed = first.clone()
    changed[:, 10:] = torch.randint(0, 23_000, (1, 6))
    with torch.no_grad():
        logits_a, _ = model(first)
        logits_b, _ = model(changed)
    torch.testing.assert_close(logits_a[:, :10], logits_b[:, :10])


def test_context_limit_is_enforced():
    model = MiniRoninLM(ModelConfig(context_length=8))
    tokens = torch.randint(0, 23_000, (1, 9))
    try:
        model(tokens)
    except ValueError as exc:
        assert "exceeds context" in str(exc)
    else:
        raise AssertionError("expected context limit failure")

def test_active_vocabulary_training_head():
    model = MiniRoninLM(ModelConfig(dropout=0.0))
    tokens = torch.randint(0, 257, (2, 32))
    logits, loss = model(tokens, labels=tokens, vocab_limit=257)
    assert logits.shape == (2, 32, 257)
    assert loss is not None and torch.isfinite(loss)
    loss.backward()
    assert model.token_embedding.weight.grad is not None


def test_active_vocabulary_rejects_out_of_range_labels():
    model = MiniRoninLM(ModelConfig(dropout=0.0))
    tokens = torch.full((1, 8), 300, dtype=torch.long)
    try:
        model(tokens, labels=tokens, vocab_limit=257)
    except ValueError as exc:
        assert "outside vocab_limit" in str(exc)
    else:
        raise AssertionError("expected active vocabulary range failure")


def test_kv_cache_matches_causal_full_forward_for_prompt_and_incremental_tokens():
    torch.manual_seed(19)
    model = MiniRoninLM(ModelConfig(dropout=0.0)).eval()
    tokens = torch.randint(0, 257, (1, 24))
    with torch.inference_mode():
        full_logits, _ = model(tokens, vocab_limit=257)
        prompt_logits, cache = model.forward_cached(tokens[:, :17])
        torch.testing.assert_close(prompt_logits, full_logits[:, :17], rtol=1e-5, atol=1e-6)
        next_logits, cache = model.forward_cached(tokens[:, 17:18], cache)
        torch.testing.assert_close(next_logits[:, -1], full_logits[:, 17], rtol=1e-5, atol=1e-6)
        chunk_logits, _ = model.forward_cached(tokens[:, 18:], cache)
        torch.testing.assert_close(chunk_logits, full_logits[:, 18:], rtol=1e-5, atol=1e-6)
