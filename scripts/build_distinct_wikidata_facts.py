#!/usr/bin/env python3
"""Build a dataset of distinct factual assertions from Wikidata.

Unlike the template-expansion datasets, each output row is one distinct
(subject, property, value) assertion retrieved from Wikidata. No fact is
duplicated merely to inflate the row count.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ENDPOINT = "https://query.wikidata.org/sparql"
PROPERTIES = {
    "P17", "P30", "P36", "P19", "P20", "P131", "P106", "P176",
    "P178", "P463", "P127", "P361", "P279", "P101", "P2578",
    "P569", "P570", "P571", "P576", "P1082", "P2046", "P2048",
}
USER_AGENT = "MINIRONIN-distinct-facts-dataset/1.0 (GitHub Actions; research dataset)"


def fetch(limit: int, retries: int = 4) -> dict:
    props = " ".join(f"wd:{p}" for p in sorted(PROPERTIES))
    query = f"""
    SELECT DISTINCT ?item ?itemLabel ?property ?propertyLabel ?value ?valueLabel
    WHERE {{
      VALUES ?property {{ {props} }}
      ?item ?property ?value .
      FILTER(STRSTARTS(STR(?item), "http://www.wikidata.org/entity/Q"))
      FILTER(?item != ?value)
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "es,en". }}
    }}
    ORDER BY STR(?item) STR(?property) STR(?value)
    LIMIT {limit}
    """
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": query, "format": "json"})
    req = urllib.request.Request(url, headers={
        "Accept": "application/sparql-results+json",
        "User-Agent": USER_AGENT,
    })
    last_error = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=180) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(8 * (attempt + 1))
    raise RuntimeError(f"Wikidata Query Service failed after {retries} attempts: {last_error}")


def clean(binding: dict, key: str) -> str:
    return binding.get(key, {}).get("value", "").strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10_000)
    parser.add_argument("--output", type=Path, default=Path("wikidata_distinct_facts.jsonl.gz"))
    args = parser.parse_args()
    if not 1 <= args.count <= 20_000:
        raise SystemExit("--count must be between 1 and 20000")

    retrieved_at = datetime.now(timezone.utc).isoformat()
    payload = fetch(args.count * 2)
    bindings = payload.get("results", {}).get("bindings", [])
    seen = set()
    rows = []
    for item in bindings:
        subject_uri = clean(item, "item")
        property_uri = clean(item, "property")
        value_uri = clean(item, "value")
        subject = clean(item, "itemLabel")
        predicate = clean(item, "propertyLabel")
        value = clean(item, "valueLabel") or value_uri
        if not all((subject_uri, property_uri, value_uri, subject, predicate, value)):
            continue
        identity = (subject_uri, property_uri, value_uri)
        if identity in seen:
            continue
        seen.add(identity)
        fact_id = hashlib.sha256("\\x1f".join(identity).encode("utf-8")).hexdigest()
        rows.append({
            "fact_id": fact_id,
            "question": f"¿Qué valor registra Wikidata para «{subject}» en la propiedad «{predicate}»?",
            "answer": f"Wikidata registra «{value}» como valor de «{predicate}» para «{subject}». Esta respuesta atribuye la afirmación a la versión consultada de la base de conocimiento; no constituye por sí sola una verificación independiente.",
            "domain": "conocimiento estructurado",
            "subject": subject,
            "subject_id": subject_uri.rsplit("/", 1)[-1],
            "property": predicate,
            "property_id": property_uri.rsplit("/", 1)[-1],
            "value": value,
            "value_id": value_uri.rsplit("/", 1)[-1] if "/entity/" in value_uri else None,
            "source": subject_uri.replace("http://", "https://"),
            "source_dataset": "Wikidata",
            "source_query_endpoint": ENDPOINT,
            "retrieved_at_utc": retrieved_at,
        })
        if len(rows) >= args.count:
            break

    if len(rows) < args.count:
        raise RuntimeError(
            f"Requested {args.count} distinct facts, but only {len(rows)} usable "
            f"unique assertions were returned. No partial dataset was written."
        )

    digest = hashlib.sha256()
    with gzip.open(args.output, "wt", encoding="utf-8", newline="\n", compresslevel=9) as out:
        for row in rows:
            line = json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
            out.write(line)
            digest.update(line.encode("utf-8"))

    manifest = {
        "dataset": args.output.name,
        "rows": len(rows),
        "unique_fact_ids": len({r["fact_id"] for r in rows}),
        "unique_subject_property_value_triples": len(seen),
        "source": "Wikidata Query Service",
        "source_endpoint": ENDPOINT,
        "retrieved_at_utc": retrieved_at,
        "query_properties": sorted(PROPERTIES),
        "format": "JSONL gzip",
        "sha256_uncompressed_jsonl": digest.hexdigest(),
        "deduplication": "SHA-256 of exact subject URI + property URI + value URI",
        "generation": "one row per distinct knowledge-graph assertion; no paraphrase multiplication",
        "limitations": [
            "These are assertions present in Wikidata, not independently verified truths.",
            "Wikidata may contain omissions, stale values, conflicting statements, or uneven coverage.",
            "Entity labels are language-dependent; the query requests Spanish then English labels.",
            "The dataset is a snapshot retrieved at the timestamp above; source pages may change later.",
            "Review high-impact, medical, legal, political, and time-sensitive assertions before training."
        ],
    }
    manifest_path = Path(str(args.output) + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
