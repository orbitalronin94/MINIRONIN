#!/usr/bin/env python3
"""Create one deterministic batch of 1,200 attributed Spanish Wikisource texts."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download

REPOSITORY = "wikimedia/wikisource"
REVISION = "160144440c765ed3ada4a4829ce1077910fbdbb6"
PARQUET = "20231201.es/train-00000-of-00001.parquet"
LICENSE = "CC BY-SA 3.0 / GFDL (Wikimedia Wikisource dataset card)"
BATCH_SIZE = 1200


def normalized(text: str) -> str:
    return re.sub(r"\W+", " ", text.casefold(), flags=re.UNICODE).strip()


def slug(text: str) -> str:
    value = unicodedata.normalize("NFKD", text)
    value = value.encode("ascii", "ignore").decode("ascii").lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return (value[:56].rstrip("-") or "texto")


def clean_text(value: object) -> str:
    text = str(value or "").replace("\x00", " ").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{4,}", "\n\n\n", text).strip()
    return text


def collect(path: Path) -> list[dict]:
    parquet = pq.ParquetFile(path)
    candidates: dict[str, dict] = {}
    for batch in parquet.iter_batches(batch_size=256, columns=["id", "url", "title", "text"]):
        for row in batch.to_pylist():
            title = clean_text(row.get("title"))
            url = str(row.get("url") or "").strip()
            body = clean_text(row.get("text"))
            page_id = str(row.get("id") or "").strip()
            if not title or not page_id or not url.startswith("https://es.wikisource.org/wiki/"):
                continue
            if len(body) < 250:
                continue
            letters = sum(ch.isalpha() for ch in body)
            if letters / max(1, len(body)) < 0.25:
                continue
            text_hash = hashlib.sha256(normalized(body).encode("utf-8")).hexdigest()
            if text_hash in candidates:
                continue
            rank = hashlib.sha256((page_id + "|" + url).encode("utf-8")).hexdigest()
            candidates[text_hash] = {
                "rank": rank,
                "id": page_id,
                "title": title,
                "url": url,
                "text": body,
                "text_sha256_normalized": text_hash,
            }
    return sorted(candidates.values(), key=lambda item: item["rank"])


def document(row: dict) -> str:
    title = row["title"].replace("\n", " ").strip()
    url = row["url"]
    history = url + ("&" if "?" in url else "?") + "action=history"
    return (
        f"# {title}\n\n"
        f"**Fuente:** Wikimedia Wikisource, edición española.\n\n"
        f"**Source URL:** {url}\n\n"
        f"**Page ID:** {row['id']}\n\n"
        f"**Dataset revision:** {REVISION} — {REPOSITORY}, snapshot 20231201.es.\n\n"
        f"**License:** {LICENSE}.\n\n"
        f"**Atribución:** texto procedente de Wikisource; título y enlace canónico conservados. "
        f"El historial de la página identifica las contribuciones y versiones: {history}. "
        f"Fuente de datos: Wikimedia Foundation.\n\n"
        "La ficha del conjunto declara licencia dual GFDL y CC BY-SA 3.0 para el contenido "
        "textual original; algunos textos pueden tener condiciones adicionales o estar en "
        "dominio público. Se conserva esta atribución por documento y no se presume que todos "
        "los textos tengan idéntica situación individual.\n\n"
        "---\n\n"
        "## Texto fuente\n\n"
        f"{row['text']}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-index", type=int, required=True)
    parser.add_argument("--output-root", default="data/inherited/papers/curated/wikimedia-wikisource")
    parser.add_argument("--manifest-path", default="/tmp/wikisource-batch-manifest.json")
    args = parser.parse_args()
    if args.batch_index < 1 or args.batch_index > 31:
        raise SystemExit("batch-index must be between 1 and 31")

    parquet_path = Path(hf_hub_download(
        repo_id=REPOSITORY,
        filename=PARQUET,
        repo_type="dataset",
        revision=REVISION,
    ))
    rows = collect(parquet_path)
    start = (args.batch_index - 1) * BATCH_SIZE
    selected = rows[start:start + BATCH_SIZE]
    if len(selected) != BATCH_SIZE:
        raise SystemExit(
            f"Cannot create an exact batch {args.batch_index}: "
            f"eligible unique texts={len(rows)}, required through index={start + BATCH_SIZE}. "
            "No partial PR has been created."
        )

    out = Path(args.output_root) / f"batch-{args.batch_index}"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.md"):
        old.unlink()

    manifest_rows = []
    seen_hashes = set()
    for row in selected:
        filename = f"{row['rank'][:12]}-{re.sub(r'[^0-9A-Za-z_-]', '', row['id'])}-{slug(row['title'])}.md"
        content = document(row)
        raw = content.encode("utf-8")
        digest = hashlib.sha256(raw).hexdigest()
        if digest in seen_hashes:
            raise SystemExit(f"Duplicate generated document: {filename}")
        seen_hashes.add(digest)
        (out / filename).write_bytes(raw)
        manifest_rows.append({
            "path": str(out / filename),
            "page_id": row["id"],
            "title": row["title"],
            "source_url": row["url"],
            "characters": len(row["text"]),
            "sha256": digest,
            "text_sha256_normalized": row["text_sha256_normalized"],
        })

    if len(list(out.glob("*.md"))) != BATCH_SIZE:
        raise SystemExit("Output directory does not contain exactly 1,200 Markdown documents")
    manifest = {
        "schema": "minironin-wikisource-es-batch-v1",
        "batch_index": args.batch_index,
        "document_count": BATCH_SIZE,
        "eligible_unique_source_texts": len(rows),
        "source_dataset": REPOSITORY,
        "source_revision": REVISION,
        "snapshot": "20231201.es",
        "license": LICENSE,
        "documents": manifest_rows,
    }
    Path(args.manifest_path).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": "success",
        "batch": args.batch_index,
        "documents": BATCH_SIZE,
        "eligible_unique_source_texts": len(rows),
        "characters": sum(item["characters"] for item in manifest_rows),
        "manifest": args.manifest_path,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
