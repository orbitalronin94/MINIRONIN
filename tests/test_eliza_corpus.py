import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_eliza_requests_use_weighted_five_family_mix_and_keep_provenance(tmp_path):
    source = tmp_path / "source.jsonl"
    source.write_text(
        json.dumps({
            "id": "q1", "question": "Why does this pointer crash?",
            "answer": "The pointer may be dangling; inspect its lifetime.",
            "domain": "systems", "license": "CC0-1.0",
        }) + "\n" +
        json.dumps({
            "id": "q2", "question": "What is entropy?",
            "answer": "A thermodynamic state function.",
            "domain": "science", "license": "CC0-1.0",
        }) + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "out.jsonl"
    result = subprocess.run(
        [
            sys.executable, str(ROOT / "scripts/build_eliza_corpus.py"),
            "--input", str(source), "--count", "2000", "--seed", "7",
            "--max-pool", "10", "--output", str(output),
        ],
        check=True, capture_output=True, text=True,
    )
    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    summary = json.loads(result.stdout)
    assert len(rows) == 2000
    assert {row["strategy"] for row in rows} == {
        "mirror", "expert", "friction", "abstain", "factual"
    }
    assert 17 <= summary["strategy_percentages"]["mirror"] <= 23
    assert 27 <= summary["strategy_percentages"]["expert"] <= 33
    assert 22 <= summary["strategy_percentages"]["friction"] <= 28
    assert 12 <= summary["strategy_percentages"]["abstain"] <= 18
    assert 7 <= summary["strategy_percentages"]["factual"] <= 13
    assert all(row["source"]["license"] == "CC0-1.0" for row in rows)
    assert all(row["source"]["file_sha256"] for row in rows)
    assert all(row["source"]["record_sha256"] for row in rows)
    assert all(row["synthetic_status"] == "teacher_request_only" for row in rows)
    assert all(row["stage_b"]["must_preserve"] for row in rows)
    assert summary["answers_generated"] is False
    assert summary["training_performed"] is False


def test_mix_rejects_bad_percentages(tmp_path):
    source = tmp_path / "source.jsonl"
    source.write_text(
        json.dumps({"question": "Q?", "answer": "A."}) + "\n",
        encoding="utf-8",
    )
    output = tmp_path / "out.jsonl"
    result = subprocess.run(
        [
            sys.executable, str(ROOT / "scripts/build_eliza_corpus.py"),
            "--input", str(source), "--count", "1", "--mix", "mirror=50,expert=50",
            "--output", str(output),
        ],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
