#!/usr/bin/env python3
"""Acquire territorially screened English-language classics with provenance and hashes."""
from __future__ import annotations
import argparse, hashlib, json, re, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/classics/SOURCES.json"
START = re.compile(r"\*\*\* START OF THE PROJECT GUTENBERG EBOOK .*?\*\*\*", re.I)
END = re.compile(r"\*\*\* END OF THE PROJECT GUTENBERG EBOOK", re.I)

def clean_gutenberg(raw: bytes) -> str:
    text = raw.decode("utf-8-sig", errors="strict").replace("\r\n", "\n").replace("\r", "\n")
    start, end = START.search(text), END.search(text)
    if not start or not end or end.start() <= start.end():
        raise ValueError("Missing or malformed Project Gutenberg boundaries")
    body = re.sub(r"\n{4,}", "\n\n\n", text[start.end():end.start()].strip())
    if len(body) < 10_000:
        raise ValueError(f"Suspiciously short text: {len(body)} characters")
    return body

def download_source(row):
    request = urllib.request.Request(
        row["plain_text_url"],
        headers={"User-Agent": "MINIRONIN-classics-corpus/1.0 (GitHub Actions; provenance retained)"},
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.read()
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/inherited/classics-library")
    args = parser.parse_args()
    output = Path(args.output); output.mkdir(parents=True, exist_ok=True)
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    approved = [x for x in registry["sources"] if x.get("rights_status") == "approved_for_spain_training"]
    if not approved: raise SystemExit("No approved classics sources")
    manifest = {"schema":"minironin-classics-acquisition-v1","policy":"Only explicitly approved source rows are downloaded; translated works remain gated pending territorial review.","sources":[]}
    with ThreadPoolExecutor(max_workers=6) as pool:
        for row, raw in zip(approved, pool.map(download_source, approved)):
            body = clean_gutenberg(raw)
            tokens = row.get("semantic_token_ids", [])
            tagged = " ".join(f"[{token}]" for token in tokens) + "\n\n" + body + "\n"
            slug = re.sub(r"[^a-z0-9]+", "-", row["id"].lower()).strip("-")
            destination = output / f"{slug}.txt"
            destination.write_text(tagged, encoding="utf-8")
            manifest["sources"].append({
                "id":row["id"],"title":row["title"],"author":row["author"],
                "author_death_year":row.get("author_death_year"),"translator":row.get("translator"),
                "translator_death_year":row.get("translator_death_year"),"language":row["language"],
                "upstream_url":row["url"],"download_url":row["plain_text_url"],
                "rights_status":row["rights_status"],"license_note":row["license"],
                "tradition":row.get("tradition",[]),"concepts":row.get("concepts",[]),
                "semantic_token_ids":tokens,"path":destination.name,"bytes":destination.stat().st_size,
                "characters":len(tagged),"sha256":hashlib.sha256(destination.read_bytes()).hexdigest(),
                "upstream_sha256":hashlib.sha256(raw).hexdigest()
            })
            print(json.dumps(manifest["sources"][-1],ensure_ascii=False),flush=True)
    manifest["total_documents"]=len(manifest["sources"])
    manifest["total_bytes"]=sum(x["bytes"] for x in manifest["sources"])
    (output/"CLASSICS-LIBRARY-MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"acquired":len(manifest["sources"]),"bytes":manifest["total_bytes"]},ensure_ascii=False))

if __name__ == "__main__": main()
