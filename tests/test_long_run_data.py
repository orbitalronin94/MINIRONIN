from __future__ import annotations

import json

from scripts.train_long_run import add_full_text, read_full_jsonl


def test_full_jsonl_reader_has_no_350_document_cap(tmp_path):
    path = tmp_path / "large-training.jsonl"
    with path.open("w", encoding="utf-8") as stream:
        for index in range(375):
            stream.write(json.dumps({
                "text": f"Document {index:04d}. " + ("reasoning evidence " * 18)
            }) + "\n")
    store = {"docs": [], "seen": set()}
    audit = read_full_jsonl(path, "science", store)
    assert audit["rows"] == 375
    assert audit["documents_added"] == 375
    assert len(store["docs"]) == 375


def test_long_text_is_chunked_without_dropping_the_tail():
    text = ("A complete paragraph containing evidence and explanation. " * 1100)
    store = {"docs": [], "seen": set()}
    added = add_full_text(store, "science", text, "test", "large-document")
    assert added >= 3
    assert store["docs"][-1]["text"]
    assert sum(len(row["text"]) for row in store["docs"]) >= len(text) * 0.95
