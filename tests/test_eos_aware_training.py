import torch

from scripts import train_long_run


def test_eos_tail_window_is_explicitly_supervised(monkeypatch):
    monkeypatch.setattr(train_long_run, "BATCH_SIZE", 1)
    monkeypatch.setattr(train_long_run, "SEQUENCE_LENGTH", 4)
    docs = {"science": [{"text": "abcdefghijk"}]}
    batch = train_long_run.batch_for_step(
        docs, ["science"], [1.0], global_step=1,
        eos_window_probability=1.0,
    )
    assert batch.shape == (1, 5)
    assert int(batch[0, -1]) == train_long_run.ACTIVE_VOCAB - 1


def test_eos_window_probability_zero_keeps_deterministic_random_windows(monkeypatch):
    monkeypatch.setattr(train_long_run, "BATCH_SIZE", 1)
    monkeypatch.setattr(train_long_run, "SEQUENCE_LENGTH", 4)
    docs = {"science": [{"text": "abcdefghijk"}]}
    first = train_long_run.batch_for_step(docs, ["science"], [1.0], 42, eos_window_probability=0.0)
    second = train_long_run.batch_for_step(docs, ["science"], [1.0], 42, eos_window_probability=0.0)
    torch.testing.assert_close(first, second)


def test_eos_probability_validation():
    import pytest
    with pytest.raises(ValueError):
        train_long_run.batch_for_step({"science":[{"text":"abcdefghijk"}]}, ["science"], [1.0], 1, eos_window_probability=1.1)
