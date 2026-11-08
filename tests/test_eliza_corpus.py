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
    assert summary["strategy_counts"] == {
        "mirror": 400, "expert": 600, "friction": 500, "abstain": 300, "factual": 200
    }
    assert all(row["source"]["license"] == "CC0-1.0" for row in rows)
    assert all(row["source"]["file_sha256"] for row in rows)
    assert all(row["source"]["record_sha256"] for row in rows)
    assert all(row["synthetic_status"] == "teacher_request_only" for row in rows)
    assert all(row["stage_b"]["must_preserve"] for row in rows)
    assert all(
        set(row["stage_b"]["global_rewrite_rules"]) == {
            "no_welcome_mat", "aggressive_empathy", "lexicon_discipline",
            "token_economy", "factual_invariance"
        }
        for row in rows
    )
    assert all(
        "at most three sentences" in row["stage_b"]["global_rewrite_rules"]["token_economy"]
        for row in rows
    )
    assert all(
        "Do not assign blame" in row["stage_b"]["global_rewrite_rules"]["aggressive_empathy"]
        for row in rows
    )
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


def test_eliza_requests_can_be_grounded_by_rag_with_deduplicated_evidence_sidecar(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "entropy.md").write_text(
        "# Entropy\n\nEntropy is a thermodynamic state function. "
        "In statistical mechanics, entropy is related to the number of microstates.\n",
        encoding="utf-8",
    )
    registry = {
        "chunking": {"target_chars": 500, "overlap_chars": 40, "min_chars": 20},
        "embedding": {
            "model": "none", "document_prefix": "passage: ", "query_prefix": "query: "
        },
        "sources": [{
            "id": "fixture", "project": "TEST", "root": "unused",
            "domain": "science", "language": "en", "epistemic": "verified",
            "license": "CC0-1.0", "redistribution": True, "enabled": False,
        }],
        "excluded_path_parts": ["holdout", "validation", "tests"],
        "excluded_extensions": [".pt", ".sqlite"],
        "allowed_extensions": [".md"],
        "max_file_mb": 5,
    }
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    index = tmp_path / "rag.sqlite"
    subprocess.run(
        [
            sys.executable, str(ROOT / "scripts/build_rag_index.py"),
            "--registry", str(registry_path), "--root", f"fixture={docs}",
            "--no-embeddings", "--output", str(index),
        ],
        check=True, capture_output=True, text=True,
    )
    source = tmp_path / "source.jsonl"
    source.write_text(
        json.dumps({
            "id": "q1", "question": "What is entropy in thermodynamics?",
            "answer": "Entropy is a thermodynamic state function.",
            "domain": "science", "license": "CC0-1.0",
        }) + "\\n",
        encoding="utf-8",
    )
    output = tmp_path / "teacher.jsonl"
    result = subprocess.run(
        [
            sys.executable, str(ROOT / "scripts/build_eliza_corpus.py"),
            "--input", str(source), "--count", "10", "--seed", "9",
            "--max-pool", "10", "--rag-index", str(index), "--output", str(output),
        ],
        check=True, capture_output=True, text=True,
    )
    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    summary = json.loads(result.stdout)
    sidecar_path = output.with_suffix(".evidence.jsonl")
    evidence_rows = [
        json.loads(line) for line in sidecar_path.read_text(encoding="utf-8").splitlines()
    ]
    assert len(rows) == 10
    assert all(row["stage_a"]["retrieval_status"] == "evidence_found" for row in rows)
    refs = {row["stage_a"]["retrieved_evidence_ref"] for row in rows}
    assert len(refs) == 1
    assert len(evidence_rows) == 1
    assert evidence_rows[0]["id"] in refs
    assert "thermodynamic state function" in evidence_rows[0]["evidence"][0]["text"]
    assert evidence_rows[0]["evidence"][0]["source"]["license"] == "CC0-1.0"
    assert summary["rag_grounding"]["status"] == "enabled"
    assert summary["rag_grounding"]["grounded_queries"] == 1
