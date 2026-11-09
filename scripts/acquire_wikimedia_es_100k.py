#!/usr/bin/env python3
"""Acquire an exactly-sized, deterministic, attribution-preserving Spanish Wikipedia slice."""
from __future__ import annotations
import argparse, gzip, hashlib, heapq, json, re, sys
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download
import pyarrow.parquet as pq

REPO = "wikimedia/wikipedia"
REVISION = "c295f8620cf6f3f220912b7d6de0f98f4dc4696d"
CONFIG = "20231101.es"
LICENSE = "CC BY-SA 3.0 (dataset card) / GFDL dual-licensed source; retain attribution and share-alike"
EXCLUDED_PREFIXES = ("anexo:", "categoría:", "wikipedia:", "portal:", "plantilla:", "ayuda:", "especial:")
def digest(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()
def clean(s: str) -> str:
    s = s.replace("\x00", " ").strip()
    s = re.sub(r"\r\n?", "\n", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s
def valid(row) -> bool:
    title = str(row.get("title") or "").strip()
    url = str(row.get("url") or "").strip()
    body = clean(str(row.get("text") or ""))
    if not title or not url.startswith("https://es.wikipedia.org/wiki/") or len(body) < 800:
        return False
    if title.casefold().startswith(EXCLUDED_PREFIXES):
        return False
    letters = sum(ch.isalpha() for ch in body)
    if letters / max(1, len(body)) < 0.48:
        return False
    if len(set(body)) < 30:
        return False
    return True
def batches(path):
    pf = pq.ParquetFile(path)
    row_index = 0
    for batch in pf.iter_batches(batch_size=512, columns=["id", "url", "title", "text"]):
        data = batch.to_pylist()
        for row in data:
            yield row_index, row
            row_index += 1
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="wikimedia-es-100k")
    ap.add_argument("--target", type=int, default=100000)
    ap.add_argument("--candidate-multiplier", type=int, default=2)
    args = ap.parse_args()
    if args.target != 100000:
        raise SystemExit("This intake is deliberately fixed at exactly 100,000 documents.")
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    api = HfApi()
    files = sorted(x for x in api.list_repo_files(REPO, repo_type="dataset", revision=REVISION)
                   if x.startswith(CONFIG + "/") and x.endswith(".parquet"))
    if not files:
        raise SystemExit("Pinned Wikimedia Spanish Parquet shards not found.")
    print(json.dumps({"source": REPO, "revision": REVISION, "shards": len(files)}), flush=True)
    local = []
    for name in files:
        path = Path(hf_hub_download(REPO, name, repo_type="dataset", revision=REVISION))
        local.append(path)
        print("DOWNLOADED", name, path.stat().st_size, flush=True)
    # Bottom-k deterministic sampling. Keep only row coordinates in memory.
    k = args.target * args.candidate_multiplier
    heap = []
    eligible = 0
    for shard_no, path in enumerate(local):
        for row_no, row in batches(path):
            if not valid(row):
                continue
            eligible += 1
            key = digest(str(row.get("id")) + "|" + str(row.get("url")))
            rank = int(key[:16], 16)
            item = (-rank, shard_no, row_no, key)
            if len(heap) < k:
                heapq.heappush(heap, item)
            elif rank < -heap[0][0]:
                heapq.heapreplace(heap, item)
        print("SCANNED", shard_no + 1, "eligible", eligible, "candidate_heap", len(heap), flush=True)
    if len(heap) < args.target:
        raise SystemExit(f"Only {len(heap)} eligible candidates; need {args.target}.")
    selected = {(shard, row): key for neg, shard, row, key in heap}
    rank_by_key = {key: -neg for neg, shard, row, key in heap}
    selected_by_shard = {}
    for shard, row in selected:
        selected_by_shard.setdefault(shard, set()).add(row)
    output = out / "wikipedia-es-100k.jsonl.gz"
    seen_text = set()
    written = 0
    manifest_rows = []
    # Read only selected rows again; exact text dedup before admitting.
    with output.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0, compresslevel=6) as gz:
            for shard_no, path in enumerate(local):
                wanted = selected_by_shard.get(shard_no, set())
                if not wanted:
                    continue
                for row_no, row in batches(path):
                    if row_no not in wanted or not valid(row):
                        continue
                    body = clean(str(row["text"]))
                    normalized = re.sub(r"\W+", " ", body.casefold(), flags=re.UNICODE).strip()
                    text_sha = digest(normalized)
                    if text_sha in seen_text:
                        continue
                    seen_text.add(text_sha)
                    key = selected[(shard_no, row_no)]
                    record = {
                        "id": str(row.get("id")),
                        "title": str(row.get("title")),
                        "url": str(row.get("url")),
                        "text": body,
                        "domain": "general",
                        "source_id": "wikimedia-es-20231101",
                        "source": "Wikimedia Foundation / Spanish Wikipedia dump 2023-11-01",
                        "dataset": "wikimedia-es-wikipedia-100k",
                        "license": LICENSE,
                        "synthetic": False,
                        "metadata": {
                            "page_id": str(row.get("id")),
                            "title": str(row.get("title")),
                            "url": str(row.get("url")),
                            "source_dataset": REPO,
                            "source_revision": REVISION,
                            "dump": CONFIG,
                            "license": LICENSE,
                            "sampling_rank_sha256": key,
                            "text_sha256_normalized": text_sha
                        }
                    }
                    gz.write((json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8"))
                    manifest_rows.append({
                        "id": str(row.get("id")), "title": str(row.get("title")),
                        "url": str(row.get("url")), "license": LICENSE,
                        "text_sha256_normalized": text_sha
                    })
                    written += 1
                    if written == args.target:
                        break
                print("EXTRACTED", shard_no + 1, "documents", written, flush=True)
                if written == args.target:
                    break
    if written != args.target:
        output.unlink(missing_ok=True)
        raise SystemExit(f"Exact count not reached: {written}/{args.target}; increase candidate pool.")
    manifest = {
        "schema": "minironin-open-library-intake-v1",
        "library": "wikimedia-es",
        "document_count": written,
        "unique_normalized_texts": len(seen_text),
        "source_dataset": REPO,
        "source_revision": REVISION,
        "dump": CONFIG,
        "language": "es",
        "license": LICENSE,
        "attribution_policy": "Each record preserves page title and canonical URL. Redistributed adaptations must retain attribution and comply with CC BY-SA share-alike; source is dual-licensed with GFDL per dataset card.",
        "sampling": "Deterministic bottom-k SHA256(page_id|url); 2x candidate pool; exact 100k unique normalized texts.",
        "quality_filter": "Spanish Wikipedia URL, title, at least 800 characters, alphabetic ratio >= 0.48, exclude non-article namespaces, unique normalized text.",
        "eligible_rows_scanned": eligible,
        "sha256_jsonl_gz": hashlib.sha256(output.read_bytes()).hexdigest(),
        "documents": manifest_rows
    }
    (out / "WIKIMEDIA-ES-100K-MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "README.md").write_text(
        "# Wikimedia Spanish — 100,000 documentos\n\n"
        "Lote de artículos de Wikipedia en español, extraído de un snapshot reproducible. "
        "Cada registro conserva título, URL, ID y licencia para atribución. "
        "La licencia CC BY-SA exige atribución y compartir adaptaciones bajo términos compatibles. "
        "No es una colección de preguntas/respuestas ni una validación factual editorial. "
        "Los artículos deben pasar deduplicación global y evaluación de calidad antes de entrenamiento.\n\n"
        f"- Dataset: {REPO}\n- Revision: {REVISION}\n- Snapshot: {CONFIG}\n- Documentos: {written}\n- Licencia declarada por el dataset: {LICENSE}\n",
        encoding="utf-8")
    sums = []
    for p in sorted(out.iterdir()):
        if p.is_file() and p.name != "SHA256SUMS":
            sums.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}")
    (out / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    print(json.dumps({"status": "success", "documents": written, "unique": len(seen_text),
                      "artifact_bytes": sum(p.stat().st_size for p in out.iterdir() if p.is_file()),
                      "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}, ensure_ascii=False), flush=True)
if __name__ == "__main__":
    main()
