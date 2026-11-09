import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from train_long_run import sample_window_start


class FixedRandom:
    def __init__(self, random_value=0.0, range_value=0):
        self.random_value = random_value
        self.range_value = range_value

    def random(self):
        return self.random_value

    def randrange(self, start, stop):
        assert start == 0
        return self.range_value


def test_eos_focused_window_ends_on_real_eos_target():
    length = 1000  # encoded bytes plus appended EOS
    sequence_length = 128
    start = sample_window_start(
        length, sequence_length, FixedRandom(random_value=0.0), 0.05
    )
    window = list(range(length))[start:start + sequence_length + 1]
    assert start == length - sequence_length - 1
    assert len(window) == sequence_length + 1
    assert window[-1] == length - 1


def test_uniform_branch_stays_within_valid_window_range():
    start = sample_window_start(
        1000, 128, FixedRandom(random_value=0.99, range_value=17), 0.05
    )
    assert start == 17


def test_zero_fraction_disables_eos_branch():
    start = sample_window_start(
        1000, 128, FixedRandom(random_value=0.0, range_value=23), 0.0
    )
    assert start == 23


def test_invalid_fraction_is_rejected():
    for fraction in (-0.01, 1.01):
        try:
            sample_window_start(1000, 128, random.Random(1), fraction)
        except ValueError as exc:
            assert "eos_window_fraction" in str(exc)
        else:
            raise AssertionError("invalid EOS window fraction was accepted")


def test_short_document_is_rejected():
    try:
        sample_window_start(128, 128, random.Random(1), 0.05)
    except ValueError as exc:
        assert "shorter" in str(exc)
    else:
        raise AssertionError("short document was accepted")
