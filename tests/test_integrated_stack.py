import json
import pytest
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import rag_retrieve


def test_rag_builder_and_citation_context(tmp_path):
    docs = tmp_path / "documents.jsonl"
    text = "La entropía es una función de estado termodinámica. " * 20
    row = {
        "document_id": "doc-entropy",
        "source_id": "fixture",
        "project": "MINIRONIN",
        "path": "science/entropy.md",
        "sha256": "abc123",
        "license": "project-authored-internal",
        "rights_status": "owner_authored_internal",
        "admission_status": "admitted",
        "train_eligible": True,
        "retrieval_eligible": True,
        "redistribution": False,
        "epistemic_type": "author_original",
        "domain": "science",
        "language": "es",
        "split": "train",
        "text": text,
    }
    validation_row = {**row, "document_id": "doc-validation", "split": "validation", "path": "science/validation.md", "text": "VALIDATION_ONLY_SECRET " + text}
    docs.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in (row, validation_row)), encoding="utf-8")
    index = tmp_path / "index.sqlite"
    subprocess.run([
        sys.executable, str(ROOT / "scripts/build_rag_index.py"),
        "--documents", str(docs), "--output", str(index), "--no-embeddings",
        "--chunk-chars", "220", "--overlap-chars", "30", "--min-chars", "40",
    ], check=True, capture_output=True, text=True)
    result = rag_retrieve.search(index, "entropía función de estado", k=2, use_vectors=False)
    assert result["hits"]
    context = rag_retrieve.format_context(result, max_chars=4000)
    assert "[S1]" in context
    assert "project-authored-internal" in context
    assert "document_sha256=abc123" in context
    db = sqlite3.connect(index)
    manifest = json.loads(db.execute("SELECT value FROM metadata WHERE key='manifest'").fetchone()[0])
    assert manifest["holdout_read"] is False
    assert manifest["training_performed"] is False
    assert manifest["validation_documents_excluded"] == 1
    assert db.execute("SELECT count(*) FROM documents WHERE document_id='doc-validation'").fetchone()[0] == 0


def test_bpe_builder_ignores_validation_rows(tmp_path):
    docs = tmp_path / "documents.jsonl"
    rows = []
    for i in range(4):
        rows.append({
            "document_id": f"doc-{i}", "admission_status": "admitted",
            "train_eligible": True, "split": "train",
            "text": "la entropía termodinámica es una función de estado " * 5,
        })
    rows.append({
        "document_id": "val-only", "admission_status": "admitted",
        "train_eligible": True, "split": "validation",
        "text": "NEVER_LEARN_THIS_VALIDATION_SEQUENCE " * 5,
    })
    docs.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), encoding="utf-8")
    output = tmp_path / "tokenizer.json"
    subprocess.run([
        sys.executable, str(ROOT / "scripts/build_backdoor_bpe.py"),
        "--train-jsonl", str(docs), "--output", str(output),
        "--max-tokens", "64", "--min-frequency", "2", "--min-documents", "2",
    ], check=True, capture_output=True, text=True)
    manifest = json.loads(output.read_text())
    assert manifest["selection"]["unique_train_documents"] == 4
    assert all("NEVER_LEARN" not in token["text"] for token in manifest["tokens"])



def test_heretic_import_keeps_admission_audit_list(tmp_path):
    import hashlib

    root = tmp_path / "heretic"
    curated = root / "incoming/cosmopedia-curated.jsonl"
    curated.parent.mkdir(parents=True)
    payload = (
        json.dumps({"text": "A mathematical explanation with a verified source."}, ensure_ascii=False)
        + "\\n"
    ).encode("utf-8")
    curated.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()

    curation_path = root / "out/COSMOPEDIA-CURATION-MANIFEST.json"
    curation_path.parent.mkdir(parents=True)
    curation_path.write_text(json.dumps({
        "schema": "heretic-cosmopedia-curated-candidate-v1",
        "source": "HuggingFaceTB/cosmopedia",
        "revision": "0ae6ec63f91742bd2d1eaef4f02232c55d719385",
        "config": "auto_math_text",
        "split": "train",
        "accepted_rows": 4734,
        "curated_sha256": digest,
        "training_authorized": False,
    }), encoding="utf-8")

    audit_path = root / "reports/corpus-audit/GLOBAL-CORPUS-AUDIT.json"
    audit_path.parent.mkdir(parents=True)
    audit_path.write_text(json.dumps({
        "schema": "heretic-global-train-corpus-audit-v2",
        "training_authorized": True,
        "exact_holdout_question_matches": 0,
        "source_counts": {"cosmopedia": 4734},
    }), encoding="utf-8")

    minironin_root = tmp_path / "minironin"
    minironin_root.mkdir()
    output = tmp_path / "admissions.jsonl"
    completed = subprocess.run([
        sys.executable, str(ROOT / "scripts/import_admitted_sources.py"),
        "--heretic-artifact-root", str(root),
        "--minironin-root", str(minironin_root),
        "--output", str(output),
    ], check=True, capture_output=True, text=True, cwd=tmp_path)

    report = json.loads(completed.stdout)
    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert report["heretic_admitted_sources"] == 1
    assert any(row["source_id"] == "HERETIC:Cosmopedia-v0.1-curated" for row in rows)
    assert any(item["source"] == "HERETIC-RONIN Cosmopedia v0.1" for item in report["audit"])


def test_rag_context_respects_byte_tokenizer_window():
    import run_inference_holdout

    result = {
        "hits": [
            {
                "chunk_id": "chunk-a",
                "text": "La fotosíntesis convierte energía lumínica en energía química. " * 10,
                "provenance": {"source_id": "science"},
                "all_source_locations": [{"source_id": "science", "locator": "p12"}],
            },
            {
                "chunk_id": "chunk-b",
                "text": "La clorofila absorbe luz principalmente en las regiones roja y azul.",
                "provenance": {"source_id": "biology"},
                "all_source_locations": [{"source_id": "biology", "locator": "p4"}],
            },
        ]
    }
    context, used = run_inference_holdout.format_rag_context_for_window(result, max_bytes=180)
    assert len(context.encode("utf-8")) <= 180
    assert used and used[0] == "chunk-a"
    assert "[S1] science#p12:" in context
    assert "chunk-a" in used


def test_bpe_builder_caps_each_document_without_losing_corpus_diversity(tmp_path):
    docs = tmp_path / "documents.jsonl"
    rows = []
    for i in range(4):
        rows.append({
            "document_id": f"balanced-doc-{i}",
            "admission_status": "admitted",
            "train_eligible": True,
            "split": "train",
            "text": ("la entropía y la energía son conceptos de física estadística " * 100),
        })
    docs.write_text("".join(json.dumps(row, ensure_ascii=False) + chr(10) for row in rows), encoding="utf-8")
    output = tmp_path / "balanced-tokenizer.json"
    completed = subprocess.run([
        sys.executable, str(ROOT / "scripts/build_backdoor_bpe.py"),
        "--train-jsonl", str(docs), "--output", str(output),
        "--max-tokens", "32", "--min-frequency", "2", "--min-documents", "2",
        "--max-corpus-bytes", "1000", "--max-bytes-per-document", "200",
        "--max-bytes-per-ngram", "6",
    ], check=False, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    manifest = json.loads(output.read_text(encoding="utf-8"))
    assert manifest["selection"]["unique_train_documents"] == 4
    assert manifest["selection"]["records_scanned"] == 4
    assert manifest["selection"]["bytes_scanned"] == 800
    assert manifest["active_vocab"] > 257


def test_holdout_rejects_checkpoint_with_wrong_completed_step_count():
    import run_inference_holdout

    run_inference_holdout.validate_checkpoint_step({"completed_steps": 810000}, 810000)
    with pytest.raises(SystemExit, match="does not match requested"):
        run_inference_holdout.validate_checkpoint_step({"completed_steps": 800000}, 810000)
    with pytest.raises(SystemExit, match="does not match requested"):
        run_inference_holdout.validate_checkpoint_step({}, 810000)


def test_bpe_manifest_counts_only_documents_inside_byte_budget(tmp_path):
    docs = tmp_path / "budget.jsonl"
    rows = [
        {"document_id": f"budget-{i}", "admission_status": "admitted",
         "train_eligible": True, "split": "train", "text": "a" * 200}
        for i in range(4)
    ]
    docs.write_text("".join(json.dumps(row) + chr(10) for row in rows), encoding="utf-8")
    output = tmp_path / "budget-tokenizer.json"
    subprocess.run([
        sys.executable, str(ROOT / "scripts/build_backdoor_bpe.py"),
        "--train-jsonl", str(docs), "--output", str(output),
        "--max-tokens", "8", "--min-frequency", "2", "--min-documents", "2",
        "--max-corpus-bytes", "300", "--max-bytes-per-document", "200",
        "--max-bytes-per-ngram", "4",
    ], check=True, capture_output=True, text=True)
    selection = json.loads(output.read_text())["selection"]
    assert selection["bytes_scanned"] == 300
    assert selection["records_scanned"] == 2
    assert selection["unique_train_documents"] == 2
