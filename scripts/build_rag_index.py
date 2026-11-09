#!/usr/bin/env python3
"""Build a provenance-preserving SQLite RAG index from the canonical library manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import time
from pathlib import Path


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def chunks(text: str, target: int, overlap: int, minimum: int):
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    output, current = [], ""
    for paragraph in paragraphs:
        while len(paragraph) > target:
            if current:
                output.append(current)
                current = ""
            cut = paragraph.rfind(" ", 0, target)
            if cut < minimum:
                cut = target
            output.append(paragraph[:cut].strip())
            paragraph = paragraph[max(1, cut - overlap):].strip()
        candidate = (current + "\n\n" + paragraph).strip()
        if len(candidate) > target and current:
            output.append(current)
            current = paragraph
        else:
            current = candidate
    if current:
        output.append(current)
    result = []
    for item in output:
        if len(item) < minimum and result:
            result[-1] = (result[-1] + "\n\n" + item)[:target + overlap]
        elif len(item) >= minimum:
            result.append(item)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--documents", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--embedding-model", default="intfloat/multilingual-e5-small")
    parser.add_argument("--no-embeddings", action="store_true")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--chunk-chars", type=int, default=1400)
    parser.add_argument("--overlap-chars", type=int, default=180)
    parser.add_argument("--min-chars", type=int, default=80)
    args = parser.parse_args()
    if args.chunk_chars <= args.min_chars or args.overlap_chars < 0 or args.batch_size < 1:
        parser.error("Invalid chunking or batch-size configuration")
    embedder = None
    if not args.no_embeddings:
        from sentence_transformers import SentenceTransformer
        embedder = SentenceTransformer(args.embedding_model, device="cpu")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        args.output.unlink()
    db = sqlite3.connect(args.output)
    db.execute("PRAGMA journal_mode=WAL")
    db.executescript("""
    CREATE TABLE documents(
      document_id TEXT PRIMARY KEY, source_id TEXT, project TEXT, relative_path TEXT,
      document_sha256 TEXT, license TEXT, rights_status TEXT, domain TEXT,
      language TEXT, epistemic TEXT, redistribution INTEGER, locator TEXT
    );
    CREATE TABLE document_sources(
      document_id TEXT, source_id TEXT, project TEXT, relative_path TEXT,
      license TEXT, rights_status TEXT, domain TEXT, language TEXT,
      epistemic TEXT, redistribution INTEGER,
      PRIMARY KEY(document_id,source_id,relative_path)
    );
    CREATE TABLE chunks(
      chunk_id TEXT PRIMARY KEY, document_id TEXT, chunk_index INTEGER,
      locator TEXT, text TEXT, text_sha256 TEXT UNIQUE, record_metadata TEXT,
      embedding BLOB, embedding_model TEXT
    );
    CREATE VIRTUAL TABLE chunks_fts USING fts5(chunk_id UNINDEXED,text,tokenize='unicode61 remove_diacritics 2');
    CREATE TABLE chunk_sources(
      chunk_id TEXT, document_id TEXT, source_id TEXT, relative_path TEXT,
      locator TEXT, record_metadata TEXT,
      PRIMARY KEY(chunk_id,document_id,source_id,relative_path,locator)
    );
    CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT);
    """)
    pending = []
    documents_count = chunks_count = duplicate_chunks = 0
    source_counts = {}
    validation_documents_excluded = 0
    started = time.perf_counter()

    def flush():
        nonlocal chunks_count, duplicate_chunks
        if not pending:
            return
        vectors = None
        if embedder:
            vectors = embedder.encode(
                ["passage: " + row[4] for row in pending],
                batch_size=args.batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
        for index, row in enumerate(pending):
            cid, did, chunk_index, locator, text, text_hash, metadata, source_id, rel = row
            blob = vectors[index].astype("float16").tobytes() if vectors is not None else None
            cursor = db.execute(
                "INSERT OR IGNORE INTO chunks VALUES(?,?,?,?,?,?,?,?,?)",
                (cid, did, chunk_index, locator, text, text_hash, metadata, blob,
                 args.embedding_model if blob is not None else None),
            )
            if cursor.rowcount:
                db.execute("INSERT INTO chunks_fts(chunk_id,text) VALUES(?,?)", (cid, text))
                chunks_count += 1
                actual_id = cid
            else:
                duplicate_chunks += 1
                actual_id = db.execute("SELECT chunk_id FROM chunks WHERE text_sha256=?", (text_hash,)).fetchone()[0]
            db.execute(
                "INSERT OR IGNORE INTO chunk_sources VALUES(?,?,?,?,?,?)",
                (actual_id, did, source_id, rel, locator, metadata),
            )
        db.commit()
        pending.clear()

    with args.documents.open(encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            doc = json.loads(line)
            if doc.get("admission_status") != "admitted" or doc.get("retrieval_eligible") is not True:
                continue
            if doc.get("split") != "train":
                validation_documents_excluded += 1
                continue
            text = str(doc.get("text", "")).strip()
            if not text:
                continue
            did = str(doc["document_id"])
            source_id = str(doc["source_id"])
            rel = str(doc["path"])
            metadata = {
                "license": doc.get("license"),
                "rights_status": doc.get("rights_status"),
                "epistemic": doc.get("epistemic_type"),
                "domain": doc.get("domain"),
                "language": doc.get("language"),
                "source_sha256": doc.get("sha256"),
                "redistribution": bool(doc.get("redistribution", False)),
            }
            encoded_metadata = json.dumps(metadata, ensure_ascii=False, sort_keys=True)
            cursor = db.execute(
                "INSERT OR IGNORE INTO documents VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (did, source_id, doc.get("project", "MINIRONIN"), rel, doc["sha256"],
                 doc["license"], doc["rights_status"], doc.get("domain", "general"),
                 doc.get("language", "und"), doc.get("epistemic_type", "unknown"),
                 int(bool(doc.get("redistribution", False))), ""),
            )
            if cursor.rowcount:
                documents_count += 1
            db.execute(
                "INSERT OR IGNORE INTO document_sources VALUES(?,?,?,?,?,?,?,?,?,?)",
                (did, source_id, doc.get("project", "MINIRONIN"), rel, doc["license"],
                 doc["rights_status"], doc.get("domain", "general"), doc.get("language", "und"),
                 doc.get("epistemic_type", "unknown"), int(bool(doc.get("redistribution", False))),
                ),
            )
            source_counts[source_id] = source_counts.get(source_id, 0) + 1
            for chunk_index, piece in enumerate(chunks(text, args.chunk_chars, args.overlap_chars, args.min_chars)):
                text_hash = sha(piece)
                chunk_id = sha(did + ":" + str(chunk_index) + ":" + text_hash)
                locator = f"chunk:{chunk_index}"
                pending.append((chunk_id, did, chunk_index, locator, piece, text_hash,
                                encoded_metadata, source_id, rel))
                if len(pending) >= args.batch_size:
                    flush()
    flush()
    manifest = {
        "schema": "minironin-rag-index-v1",
        "documents_sha256": hashlib.sha256(args.documents.read_bytes()).hexdigest(),
        "embedding_model": args.embedding_model if embedder else None,
        "embedding_dimension": embedder.get_sentence_embedding_dimension() if embedder else None,
        "query_prefix": "query: ",
        "documents_unique": documents_count,
        "chunks_unique": chunks_count,
        "duplicate_chunks": duplicate_chunks,
        "validation_documents_excluded": validation_documents_excluded,
        "sources": source_counts,
        "chunking": {"target_chars": args.chunk_chars, "overlap_chars": args.overlap_chars, "min_chars": args.min_chars},
        "elapsed_seconds": round(time.perf_counter() - started, 2),
        "training_performed": False,
        "holdout_read": False,
    }
    db.execute("INSERT INTO metadata VALUES('manifest',?)", (json.dumps(manifest, ensure_ascii=False),))
    db.commit()
    db.close()
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
