import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_library_manifest_rejects_unapproved_and_excludes_holdout(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.md").write_text("Approved text with enough content for the inventory.", encoding="utf-8")
    (tmp_path / "holdout").mkdir()
    (tmp_path / "holdout" / "secret.md").write_text("Reserved test material.", encoding="utf-8")
    ledger = tmp_path / "admissions.jsonl"
    rows = [
        {"path": "docs/a.md", "source_id": "s", "admission_status": "admitted",
         "rights_status": "owner_authored_internal", "license": "project-authored",
         "train_eligible": True, "retrieval_eligible": True, "domain": "science"},
        {"path": "holdout/secret.md", "source_id": "s", "admission_status": "admitted",
         "rights_status": "owner_authored_internal", "license": "project-authored",
         "train_eligible": True, "retrieval_eligible": True},
        {"path": "docs/a.md", "source_id": "s2", "admission_status": "candidate",
         "rights_status": "owner_authored_internal", "license": "project-authored",
         "train_eligible": True, "retrieval_eligible": True},
    ]
    ledger.write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")
    out = tmp_path / "out"
    subprocess.run([sys.executable, str(ROOT / "scripts/build_library_manifest.py"),
                    "--root", str(tmp_path), "--admissions", str(ledger), "--output", str(out)],
                   check=True, capture_output=True, text=True)
    manifest = json.loads((out / "manifest.json").read_text())
    docs = [json.loads(x) for x in (out / "documents.jsonl").read_text().splitlines()]
    assert manifest["documents"] == 1
    assert len(docs) == 1
    assert docs[0]["train_eligible"] is True
    assert docs[0]["retrieval_eligible"] is True
    assert manifest["holdout_read"] is False


def test_awake_rows_are_extractively_grounded(tmp_path):
    source = tmp_path / "documents.jsonl"
    source.write_text(json.dumps({
        "document_id": "doc1", "source_id": "paper", "sha256": "abc",
        "license": "internal", "rights_status": "owner_authored_internal",
        "admission_status": "admitted", "train_eligible": True,
        "retrieval_eligible": True, "epistemic_type": "author_original",
        "domain": "science", "language": "es", "split": "train",
        "text": "La entropía es una magnitud de estado termodinámica. " * 4,
    }, ensure_ascii=False) + "\n", encoding="utf-8")
    train, val = tmp_path / "train.jsonl", tmp_path / "val.jsonl"
    subprocess.run([sys.executable, str(ROOT / "scripts/build_awake_rows.py"),
                    "--documents", str(source), "--train-output", str(train),
                    "--validation-output", str(val)], check=True, capture_output=True, text=True)
    rows = [json.loads(x) for x in train.read_text().splitlines()]
    assert rows
    assert all(row["task_type"] == "extractive_copy" for row in rows)
    assert all(row["source_document_id"] == "doc1" for row in rows)
    assert all("[S1]" in row["text"] for row in rows)



def test_jsonl_payload_materializes_record_level_documents_and_validation(tmp_path):
    (tmp_path / "data").mkdir()
    payload = tmp_path / "data" / "corpus.jsonl"
    payload.write_text("".join(
        json.dumps({"text": f"Documento factual número {i}. Contiene información verificable suficiente."}, ensure_ascii=False) + "\\n"
        for i in range(20)
    ), encoding="utf-8")
    import hashlib
    digest = hashlib.sha256(payload.read_bytes()).hexdigest()
    ledger = tmp_path / "admissions.jsonl"
    ledger.write_text(json.dumps({
        "document_id": "corpus:train", "path": "data/corpus.jsonl",
        "source_id": "corpus", "admission_status": "admitted",
        "rights_status": "owner_authored_internal", "license": "internal",
        "train_eligible": True, "retrieval_eligible": True, "sha256": digest,
        "language": "es",
    }) + "\\n", encoding="utf-8")
    out = tmp_path / "out"
    subprocess.run([sys.executable, str(ROOT / "scripts/build_library_manifest.py"),
                    "--root", str(tmp_path), "--admissions", str(ledger), "--output", str(out)],
                   check=True, capture_output=True, text=True)
    manifest = json.loads((out / "manifest.json").read_text())
    docs = [json.loads(x) for x in (out / "documents.jsonl").read_text().splitlines()]
    assert manifest["documents"] == 20
    assert manifest["validation_split"] >= 1
    assert manifest["train_split"] >= 1
    assert len({d["document_id"] for d in docs}) == 20
    assert all(d["payload_sha256"] == digest for d in docs)
    assert all(d["record"] == {"text": d["text"].removeprefix("text: ")} for d in docs)
