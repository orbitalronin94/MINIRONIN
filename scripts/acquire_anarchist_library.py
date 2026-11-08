#!/usr/bin/env python3
"""Acquire only territorially cleared classic anarchist texts for MINIRONIN."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "data/anarchist/SOURCES.jsonl"
START = re.compile(r"\\*\\*\\* START OF THE PROJECT GUTENBERG EBOOK .*?\\*\\*\\*", re.I)
END = re.compile(r"\\*\\*\\* END OF THE PROJECT GUTENBERG EBOOK", re.I)


def clean_gutenberg(raw: bytes) -> str:
    text = raw.decode("utf-8-sig", errors="strict").replace("\r\n", "\n").replace("\r", "\n")
    start = START.search(text)
    end = END.search(text)
    if not start or not end or end.start() <= start.end():
        raise ValueError("Missing or malformed Project Gutenberg start/end markers")
    body = text[start.end():end.start()].strip()
    body = re.sub(r"\n{4,}", "\n\n\n", body)
    if len(body) < 10_000:
        raise ValueError(f"Suspiciously short book body: {len(body)} characters")
    return body


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/inherited/anarchist-library")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(line) for line in SOURCES.read_text(encoding="utf-8").splitlines() if line.strip()]
    approved = [row for row in rows if row.get("rights_status") == "approved_for_spain_training"]
    if not approved:
        raise SystemExit("No territorially approved anarchist sources in SOURCES.jsonl")
    manifest = {
        "schema": "minironin-anarchist-library-acquisition-v1",
        "scope": "Only sources explicitly marked approved_for_spain_training are downloaded.",
        "rights_policy": "Project Gutenberg's US public-domain notice is not treated as worldwide clearance. The registry records a separate Spain term assessment; review and exclude separately credited third-party matter.",
        "sources": [],
    }
    for row in approved:
        request = urllib.request.Request(
            row["plain_text_url"],
            headers={"User-Agent": "MINIRONIN-research-corpus/1.0 (GitHub Actions; source attribution retained)"},
        )
        with urllib.request.urlopen(request, timeout=90) as response:
            raw = response.read()
        body = clean_gutenberg(raw)
        tokens = row.get("semantic_token_ids", [])
        tagged = " ".join(f"[{token}]" for token in tokens) + "\n\n" + body + "\n"
        slug = re.sub(r"[^a-z0-9]+", "-", row["id"].lower()).strip("-")
        destination = output / f"{slug}.txt"
        destination.write_text(tagged, encoding="utf-8")
        digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        manifest["sources"].append({
            "id": row["id"],
            "title": row["title"],
            "author": row["author"],
            "translator": row.get("translator"),
            "language": row["language"],
            "upstream_url": row["url"],
            "download_url": row["plain_text_url"],
            "rights_status": row["rights_status"],
            "license_note": row["license"],
            "tradition": row.get("tradition", []),
            "concepts": row.get("concepts", []),
            "semantic_token_ids": tokens,
            "path": destination.name,
            "bytes": destination.stat().st_size,
            "characters": len(tagged),
            "sha256": digest,
            "upstream_sha256": hashlib.sha256(raw).hexdigest(),
        })
        print(json.dumps(manifest["sources"][-1], ensure_ascii=False))
        time.sleep(1)
    manifest["total_documents"] = len(manifest["sources"])
    manifest["total_bytes"] = sum(x["bytes"] for x in manifest["sources"])
    (output / "ANARCHIST-LIBRARY-MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if len(manifest["sources"]) < 2:
        raise SystemExit("Expected at least two approved source texts")
    print(json.dumps({"acquired": len(manifest["sources"]), "bytes": manifest["total_bytes"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
