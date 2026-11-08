import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from continue_mamba_50m import add_rag_docs, load_rag_training_docs


def make_index(path: Path):
    db = sqlite3.connect(path)
    db.executescript("""
        CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE documents(
            document_id TEXT PRIMARY KEY, source_id TEXT, project TEXT,
            relative_path TEXT, document_sha256 TEXT, license TEXT,
            domain TEXT, language TEXT, epistemic TEXT, redistribution INTEGER,
            locator TEXT
        );
        CREATE TABLE document_sources(
            document_id TEXT, source_id TEXT, project TEXT, relative_path TEXT,
            license TEXT, domain TEXT, language TEXT, epistemic TEXT,
            redistribution INTEGER,
            PRIMARY KEY(document_id, source_id, relative_path)
        );
        CREATE TABLE chunks(
            chunk_id TEXT PRIMARY KEY, document_id TEXT, chunk_index INTEGER,
            locator TEXT, text TEXT, text_sha256 TEXT UNIQUE,
            record_metadata TEXT, embedding BLOB, embedding_model TEXT
        );
        CREATE TABLE chunk_sources(
            chunk_id TEXT, document_id TEXT, source_id TEXT, relative_path TEXT,
            locator TEXT, record_metadata TEXT,
            PRIMARY KEY(chunk_id, document_id, source_id, relative_path, locator)
        );
    """)
    manifest = {
        "holdout_read": False,
        "sources": [
            {"id": "minironin-papers", "exists": True},
            {"id": "RONIN_IA", "exists": True},
            {"id": "RONIN_IA_RIGHTS", "exists": True},
            {"id": "minironin-curated", "exists": True},
        ],
    }
    db.execute("INSERT INTO metadata VALUES('manifest', ?)", (json.dumps(manifest),))
    samples = [
        ("paper-doc", "paper-chunk", "minironin-papers", "research",
         "internal-research-only", "author_original", "papers/physics.md", "{}"),
        ("ronin-doc", "ronin-chunk", "RONIN_IA", "inherited",
         "CC0-1.0", "scoped-train-admitted-only", "admitted/math/notes.jsonl",
         json.dumps({"domain": "math", "license": "CC0-1.0"})),
        ("rights-doc", "rights-chunk", "RONIN_IA_RIGHTS", "provenance",
         "rights-registry-metadata", "rights_metadata", "rights/registry.jsonl", "{}"),
        ("curated-doc", "curated-chunk", "minironin-curated", "curated",
         "mixed-see-source-record", "curated_or_synthetic_mixed",
         "curated/behavior.jsonl", json.dumps({"domain": "behavior"})),
    ]
    for doc_id, chunk_id, source, domain, license_name, epistemic, relpath, metadata in samples:
        text = (f"Verified corpus passage for {source}. " * 12).strip()
        import hashlib
        digest = hashlib.sha256(text.encode()).hexdigest()
        db.execute(
            "INSERT INTO documents VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (doc_id, source, source, relpath, doc_id, license_name, domain,
             "en", epistemic, 0, "line:1"),
        )
        db.execute(
            "INSERT INTO document_sources VALUES(?,?,?,?,?,?,?,?,?)",
            (doc_id, source, source, relpath, license_name, domain, "en", epistemic, 0),
        )
        db.execute(
            "INSERT INTO chunks VALUES(?,?,?,?,?,?,?,?,?)",
            (chunk_id, doc_id, 0, "line:1", text, digest, metadata, None, None),
        )
        db.execute(
            "INSERT INTO chunk_sources VALUES(?,?,?,?,?,?)",
            (chunk_id, doc_id, source, relpath, "line:1", metadata),
        )
    db.commit()
    db.close()


def test_rag_training_loader_uses_only_train_admitted_sources(tmp_path):
    index = tmp_path / "fixture.sqlite"
    make_index(index)

    docs, manifest = load_rag_training_docs(index)

    assert {doc["source"] for doc in docs} == {"minironin-papers", "RONIN_IA"}
    assert {doc["domain"] for doc in docs} == {"science", "math"}
    assert manifest["chunks_total"] == 2
    assert manifest["chunks_by_source"] == {"minironin-papers": 1, "RONIN_IA": 1}
    assert any(item.startswith("RONIN_IA_RIGHTS") for item in manifest["excluded_sources"])
    assert all(doc["split"] in {"train", "validation"} for doc in docs)


def test_rag_merge_deduplicates_and_keeps_validation_tensor_batches():
    text = "A sufficiently long RAG passage used for deterministic split validation. " * 8
    import hashlib
    digest = hashlib.sha256(("science\0" + text).encode()).hexdigest()
    train_docs = defaultdict(list, {"science": [{"domain": "science", "text": text, "sha256": digest}]})
    validation = {"science": [torch.zeros((1, 129), dtype=torch.long)]}
    rag_docs = [
        {"domain": "science", "text": text, "sha256": digest, "split": "train"},
        {"domain": "math", "text": text, "sha256": "new-math", "split": "train"},
        {"domain": "science", "text": text + " another source passage", "sha256": "new-val", "split": "validation"},
    ]

    report = add_rag_docs(train_docs, validation, rag_docs)

    assert report["added_train_chunks"] == 1
    assert report["added_validation_chunks"] == 1
    assert len(train_docs["science"]) == 1
    assert len(train_docs["math"]) == 1
    assert len(validation["science"]) >= 1
