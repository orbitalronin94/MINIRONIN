import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from minironin.tokenizer import ByteNgramTokenizer, EOS_ID


def sample():
    return {
        "schema": "minironin-backdoor-bpe-v1",
        "base_active_vocab": 257,
        "eos_id": 256,
        "tokens": [
            {"id": 257, "hex": "20656c", "text": " el"},
            {"id": 258, "hex": "6369c3b36e", "text": "ción"},
        ],
    }


def test_lossless_round_trip_utf8_and_fallback():
    tokenizer = ByteNgramTokenizer(sample())
    text = "el corazón 🥷\nCódigo 123; café."
    assert tokenizer.decode(tokenizer.encode(text)) == text


def test_longest_match_and_eos():
    tokenizer = ByteNgramTokenizer(sample())
    ids = tokenizer.encode(" elción", add_eos=True)
    assert ids[-1] == EOS_ID
    assert tokenizer.decode(ids) == " elción"


def test_ids_are_append_only():
    data = sample()
    data["tokens"][1]["id"] = 260
    try:
        ByteNgramTokenizer(data)
    except ValueError as exc:
        assert "contiguous" in str(exc)
    else:
        raise AssertionError("non-contiguous IDs accepted")


def test_manifest_load(tmp_path):
    path = tmp_path / "tokenizer.json"
    path.write_text(json.dumps(sample()), encoding="utf-8")
    assert ByteNgramTokenizer.load(path).active_vocab == 259



def test_byte_lengths_match_reconstructed_bytes():
    tokenizer = ByteNgramTokenizer(sample())
    assert tokenizer.byte_length(257) == 3
    assert tokenizer.byte_length(258) == 5
    assert tokenizer.byte_length(65) == 1
    assert tokenizer.byte_length(EOS_ID) == 0


def test_manifest_rejects_active_vocab_drift():
    data = sample()
    data["active_vocab"] = 999
    try:
        ByteNgramTokenizer(data)
    except ValueError as exc:
        assert "active_vocab" in str(exc)
    else:
        raise AssertionError("inconsistent active_vocab accepted")
