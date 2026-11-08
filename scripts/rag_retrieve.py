#!/usr/bin/env python3
"""Architecture-neutral hybrid BM25 + multilingual-vector retrieval with citations."""
from __future__ import annotations

import argparse
import json
import re
import sqlite3


def _manifest(db):
    row = db.execute("SELECT value FROM metadata WHERE key='manifest'").fetchone()
    return json.loads(row[0]) if row else {}


def _fts_query(query):
    # First try the user's exact FTS expression. Fallback makes ordinary prose safe.
    terms = re.findall(r"[^\W_]+", query, flags=re.UNICODE)
    if not terms:
        return ""
    return " OR ".join('"' + term.replace('"', '""') + '"' for term in terms)


def _format_context(hits, max_chars=12000):
    blocks = []
    used = 0
    for index, hit in enumerate(hits, 1):
        provenance = hit.get("provenance", {})
        source_id = provenance.get("source_id", "unknown")
        project = provenance.get("project", "unknown")
        path = provenance.get("relative_path", "unknown")
        locations = hit.get("all_source_locations", [])
        location = locations[0] if locations else {}
        record_metadata = location.get("record_metadata") or hit.get("record_metadata", {})
        locator_text = location.get("locator") or hit.get("locator") or "unspecified"
        epistemic = record_metadata.get("epistemic") or provenance.get("epistemic", "unknown")
        license_name = record_metadata.get("license") or record_metadata.get("licencia") or provenance.get("license", "unknown")
        aliases = [f"{item.get('source_id')}:{item.get('relative_path')}#{item.get('locator')}" for item in locations[1:]]
        block = (
            f"[S{index}] {project}/{source_id} :: {path}#{locator_text}\n"
            f"epistemic={epistemic}; license={license_name}; "
            f"document_sha256={provenance.get('document_sha256', 'unknown')}; "
            f"chunk_id={hit['chunk_id']}\n"
            + (f"also_from={'; '.join(aliases)}\n" if aliases else "")
            + f"{hit['text']}"
        )
        if used + len(block) > max_chars:
            continue
        blocks.append(block)
        used += len(block) + 2
    if not blocks:
        return "No se recuperó evidencia documental utilizable."
    return (
        "CONTEXTO DOCUMENTAL RECUPERADO (no asumir que similitud equivale a verdad).\n"
        + "\n\n".join(blocks)
        + "\n\nCita las fuentes [S#] para afirmaciones apoyadas por este contexto. "
          "Distingue evidencia, inferencia y ausencia de información."
    )


def search(index_path, query, k=5, model=None, use_vectors=True, max_per_document=2):
    if k < 1:
        raise ValueError("top-k must be positive")
    db = sqlite3.connect(index_path)
    db.row_factory = sqlite3.Row
    pool = {}
    warnings = []
    try:
        manifest = _manifest(db)
        configured_model = manifest.get("embedding_model")
        model = model or configured_model
        sql = (
            "SELECT c.chunk_id,c.document_id,c.text,c.record_metadata "
            "FROM chunks_fts f JOIN chunks c ON c.chunk_id=f.chunk_id "
            "WHERE chunks_fts MATCH ? ORDER BY bm25(chunks_fts) LIMIT ?"
        )
        rows = []
        try:
            rows = list(db.execute(sql, (query, k * 10)))
        except sqlite3.OperationalError:
            rows = []
        # Natural-language queries often contain one irrelevant token. Retry with
        # quoted OR terms when the exact FTS expression is invalid or too restrictive.
        if not rows:
            fallback = _fts_query(query)
            if fallback and fallback != query:
                try:
                    rows = list(db.execute(sql, (fallback, k * 10)))
                except sqlite3.OperationalError as exc:
                    warnings.append(f"BM25 unavailable for query: {exc}")
        for rank, row in enumerate(rows, 1):
            pool[row["chunk_id"]] = {
                "row": row, "score": 1.0 / (60 + rank), "channels": ["bm25"]
            }

        if use_vectors and model and configured_model == model:
            try:
                import heapq
                import numpy as np
                from sentence_transformers import SentenceTransformer

                query_prefix = manifest.get("query_prefix", "query: ")
                encoder = SentenceTransformer(model, device="cpu")
                vector = encoder.encode(
                    [query_prefix + query],
                    normalize_embeddings=True,
                    convert_to_numpy=True,
                )[0].astype("float32")
                cursor = db.execute(
                    "SELECT chunk_id,document_id,text,record_metadata,embedding "
                    "FROM chunks WHERE embedding IS NOT NULL AND embedding_model=?",
                    (model,),
                )
                heap = []
                limit = k * 10
                while True:
                    batch = cursor.fetchmany(2048)
                    if not batch:
                        break
                    matrix = np.stack([
                        np.frombuffer(row["embedding"], dtype=np.float16).astype("float32")
                        for row in batch
                    ])
                    scores = matrix @ vector
                    take = min(limit, len(batch))
                    indices = np.argpartition(scores, -take)[-take:] if take else []
                    for item_index in indices:
                        row = batch[int(item_index)]
                        item = (float(scores[item_index]), row["chunk_id"], dict(row))
                        if len(heap) < limit:
                            heapq.heappush(heap, item)
                        elif item > heap[0]:
                            heapq.heapreplace(heap, item)
                for rank, (_, _, row) in enumerate(sorted(heap, reverse=True), 1):
                    hit = pool.setdefault(
                        row["chunk_id"],
                        {"row": row, "score": 0.0, "channels": []},
                    )
                    hit["score"] += 1.0 / (60 + rank)
                    hit["channels"].append("vector")
            except ImportError:
                warnings.append("Vector retrieval unavailable: install requirements-rag.txt")
            except (RuntimeError, ValueError) as exc:
                warnings.append(f"Vector retrieval unavailable: {exc}")
        elif use_vectors and model and configured_model != model:
            warnings.append(
                f"Requested embedding model {model!r} does not match index model "
                f"{configured_model!r}; vector channel skipped."
            )

        ranked = sorted(pool.values(), key=lambda item: item["score"], reverse=True)
        selected = []
        per_document = {}
        for item in ranked:
            row = item["row"]
            document_id = row["document_id"]
            if per_document.get(document_id, 0) >= max_per_document:
                continue
            per_document[document_id] = per_document.get(document_id, 0) + 1
            selected.append(item)
            if len(selected) >= k:
                break

        results = []
        for item in selected:
            row = item["row"]
            document = db.execute(
                "SELECT * FROM documents WHERE document_id=?", (row["document_id"],)
            ).fetchone()
            aliases = [
                {**dict(alias), "record_metadata": json.loads(alias["record_metadata"] or "{}")}
                for alias in db.execute(
                    "SELECT source_id,relative_path,locator,record_metadata "
                    "FROM chunk_sources WHERE chunk_id=?",
                    (row["chunk_id"],),
                ).fetchall()
            ]
            results.append({
                "chunk_id": row["chunk_id"],
                "text": row["text"],
                "record_metadata": json.loads(row["record_metadata"] or "{}"),
                "rrf_score": item["score"],
                "channels": item["channels"],
                "provenance": dict(document) if document else {},
                "all_source_locations": aliases,
            })
        return {"hits": results, "warnings": warnings, "index_manifest": manifest}
    finally:
        db.close()


def format_context(result, max_chars=12000):
    return _format_context(result["hits"], max_chars=max_chars)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--index", default="artifacts/rag/minironin-rag.sqlite")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--model", default=None)
    parser.add_argument("--no-vector", action="store_true")
    parser.add_argument("--format", choices=("json", "context"), default="json")
    parser.add_argument("--max-context-chars", type=int, default=12000)
    args = parser.parse_args()
    result = search(
        args.index, args.query, args.top_k, model=args.model, use_vectors=not args.no_vector
    )
    if args.format == "context":
        print(format_context(result, args.max_context_chars))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
