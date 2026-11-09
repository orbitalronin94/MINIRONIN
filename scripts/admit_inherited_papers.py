#!/usr/bin/env python3
"""Admit already-curated inherited Spanish summaries into accepted JSONL."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

COLLECTIONS = {
    "nasa": Path("data/inherited/papers/curated/nasa"),
    "nist": Path("data/inherited/papers/curated/nist"),
    "noaa-usgs": Path("data/inherited/papers/curated/noaa-usgs"),
    "classics": Path("data/inherited/classics-library/curated"),
    "anarchist": Path("data/inherited/anarchist-library/curated"),
}
DOMAINS = {
    "nasa": "ciencias de la Tierra y espacio",
    "nist": "ciberseguridad y tecnología",
    "noaa-usgs": "ciencias oceánicas, hidrología y geociencias",
    "classics": "filosofía, ciencia e historia del pensamiento",
    "anarchist": "filosofía política e historia de las ideas",
}
LICENSE_NOTE = "Original Spanish synthesis; source material attributed; no source text intentionally reproduced"
URL = re.compile(r"https?://[^\s)]+")
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--collection", choices=COLLECTIONS, required=True)
    ap.add_argument("--revision", default="main")
    args = ap.parse_args()
    root = COLLECTIONS[args.collection]
    paths = sorted(root.glob("*.md"))
    if not paths:
        raise SystemExit(f"No curated papers in {root}")
    outdir = Path("data/curated/accepted")
    outdir.mkdir(parents=True, exist_ok=True)
    slug = f"inherited-{args.collection}-papers-es"
    out = outdir / f"{slug}.jsonl"
    records, seen = [], set()
    for path in paths:
        raw = path.read_text(encoding="utf-8").strip()
        if len(raw) < 500:
            continue
        key = hashlib.sha256(re.sub(r"\s+", " ", raw).casefold().encode()).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        match = URL.search(raw)
        source = match.group(0).rstrip(".,") if match else "https://github.com/orbitalronin94/MINIRONIN"
        record = {
            "id": f"{slug}:{path.stem}", "text": raw, "domain": DOMAINS[args.collection],
            "language": "es", "split": "train", "train_eligible": True,
            "admission_status": "accepted", "synthetic": False, "license": LICENSE_NOTE,
            "source_dataset": f"MINIRONIN inherited curated {args.collection} summaries",
            "source": source, "source_revision": args.revision, "source_row": path.name,
            "attribution": raw.splitlines()[2].strip() if len(raw.splitlines()) > 2 else source,
            "task": "language modeling; factual Spanish exposition",
            "metadata": {"collection": args.collection, "origin_path": str(path), "curation": "Spanish synthesis with source attribution"}
        }
        records.append(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    if not records:
        raise SystemExit("No admissible records after length/dedup checks")
    out.write_text("".join(records), encoding="utf-8")
    manifest = {
        "schema_version": 1, "slug": slug,
        "dataset": f"MINIRONIN curated {args.collection} Spanish papers",
        "source_dataset": "orbitalronin94/MINIRONIN inherited curated summaries",
        "source_revision": args.revision, "license": LICENSE_NOTE,
        "language": "es", "source_split": "train", "rows_scanned": len(paths),
        "rows_admitted": len(records), "duplicates_skipped": len(paths) - len(records),
        "file": out.name, "sha256_jsonl": hashlib.sha256(out.read_bytes()).hexdigest(),
        "admission_policy": "Existing curated Spanish syntheses only; minimum 500 characters; normalized-text deduplication; source URL, original path, attribution and revision retained; no external files downloaded. Source-edition territorial copyright status is not asserted."
    }
    (outdir / f"{slug}.manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"collection": args.collection, "rows_scanned": len(paths), "rows_admitted": len(records), "bytes": out.stat().st_size, "sha256": manifest["sha256_jsonl"]}))
if __name__ == "__main__":
    main()
