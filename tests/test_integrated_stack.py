import json
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
    docs.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
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
