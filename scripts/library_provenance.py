"""Strict source-to-library attribution and train-only token preparation."""
from __future__ import annotations

import hashlib
from collections.abc import Callable, Iterable, Mapping


SOURCE_PREFIXES = (
    ("HERETIC:", "heretic"),
    ("PRODATPHIL", "prodatphil"),
    ("MINIRONIN-ANARCHIST-LIBRARY", "anarchist"),
    ("MINIRONIN-CLASSICS-LIBRARY", "classics"),
    ("MINIRONIN-", "minironin_behavior"),
)


def infer_library_id(source: str) -> str:
    """Return canonical library ID from the explicit ingestion source label."""
    if not isinstance(source, str) or not source.strip():
        raise ValueError("Document source label is required for library attribution")
    for prefix, library_id in SOURCE_PREFIXES:
        if source.startswith(prefix):
            return library_id
    raise ValueError(f"Unregistered document source label: {source!r}")


def training_corpus_signature(train_docs_by_domain: Mapping[str, Iterable[Mapping]]) -> str:
    """Hash sorted train-only document identities with their library provenance."""
    rows = []
    for domain in sorted(train_docs_by_domain):
        for doc in train_docs_by_domain[domain]:
            library_id = infer_library_id(doc.get("source", ""))
            doc_id = doc.get("sha256")
            if not doc_id:
                raise ValueError("Training document is missing its content SHA-256")
            rows.append((library_id, str(doc_id)))
    digest = hashlib.sha256()
    for library_id, doc_id in sorted(set(rows)):
        digest.update(library_id.encode("utf-8"))
        digest.update(b"\0")
        digest.update(doc_id.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def iter_tokenized_training_rows(
    train_docs_by_domain: Mapping[str, Iterable[Mapping]],
    encode_document: Callable[[str], Iterable[int]],
):
    """Yield one encoded train document at a time, ready for build_token_store.

    This avoids materializing a second full-corpus list of Python token IDs.
    encode_document must return token IDs including the tokenizer's EOS policy.
    """
    ordered = []
    for domain in sorted(train_docs_by_domain):
        for doc in train_docs_by_domain[domain]:
            library_id = infer_library_id(doc.get("source", ""))
            doc_id = doc.get("sha256")
            text = doc.get("text")
            if not doc_id or not isinstance(text, str):
                raise ValueError("Training document needs sha256 and text")
            ordered.append((library_id, str(doc_id), text))
    for library_id, doc_id, text in sorted(ordered, key=lambda row: (row[0], row[1])):
        yield {
            "id": doc_id,
            "library_id": library_id,
            "split": "train",
            "token_ids": list(encode_document(text)),
        }
