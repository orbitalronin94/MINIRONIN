#!/usr/bin/env python3
"""Build extractive, provenance-preserving 'awake rows' from approved libraries.

Rows teach the model to attend to a supplied source passage and answer a
concept-specific question. Answers are verbatim sentences from that passage;
no model-generated paraphrases or unsupported facts are introduced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {".md", ".txt", ".xml", ".tei", ".html", ".htm"}
SKIP_NAMES = re.compile(r"(readme|manifest|license|sha256|checksum|sources|catalog|schema)", re.I)
DOMAIN_BY_LIBRARY = {
    "minironin-core": "behavior",
    "prodatphil": "books",
    "heretic": "science",
    "ronin-papers": "science",
    "anarchist-classics": "anarchist",
    "classics-library": "classics",
    "wikimedia-es": "science",
}
MAX_SENTENCES_PER_CONCEPT_DOCUMENT = 2
MAX_ROWS_PER_DOCUMENT = 12


def normalize(value: str) -> str:
    return re.sub(r"\W+", " ", value.casefold(), flags=re.UNICODE).strip()


def visible_text(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style)\b[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    raw = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", raw)
    raw = re.sub(r"(?m)^\s*[-*_]{3,}\s*$", " ", raw)
    raw = re.sub(r"[ \t\r\f\v]+", " ", raw)
    return re.sub(r"\n{3,}", "\n\n", raw).strip()


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.strip()) >= 80]


def split_sentences(paragraph: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜÑ¿¡0-9])", paragraph) if len(s.strip()) >= 45]


def has_alias(sentence: str, alias: str) -> bool:
    alias = alias.strip()
    if len(alias) < 4:
        return False
    return re.search(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", sentence, flags=re.I) is not None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=ROOT / "data/semantic/LIBRARY_REGISTRY.json")
    parser.add_argument("--output", type=Path, default=ROOT / "data/curated/awakened-library-rows.jsonl")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data/curated/awakened-library-manifest.json")
    parser.add_argument("--max-rows", type=int, default=250_000)
    args = parser.parse_args()
    if args.max_rows < 1:
        parser.error("--max-rows must be positive")

    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    concepts = {item["id"]: item for item in registry["concepts"]}
    rows_seen: set[str] = set()
    source_files: dict[str, dict] = {}
    counts = Counter()
    library_counts = Counter()
    concept_counts = Counter()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", encoding="utf-8") as out:
        for library in sorted(registry["libraries"], key=lambda x: x["id"]):
            library_id = library["id"]
            domain = DOMAIN_BY_LIBRARY.get(library_id)
            if not domain:
                counts["libraries_without_domain_mapping"] += 1
                continue
            library_concepts = [
                concepts[cid] for cid in sorted(set(library.get("concepts", [])) & set(concepts))
            ]
            roots = [ROOT / item for item in library.get("source_paths", [])]
            files = []
            for root in roots:
                if not root.exists():
                    counts["missing_library_roots"] += 1
                    continue
                if root.is_file():
                    candidates = [root]
                else:
                    candidates = sorted(root.rglob("*"))
                files.extend(
                    p for p in candidates
                    if p.is_file() and p.suffix.lower() in TEXT_EXTENSIONS
                    and not SKIP_NAMES.search(p.name)
                )

            for path in sorted(set(files)):
                try:
                    raw = path.read_bytes()
                    text = visible_text(raw.decode("utf-8"))
                except (OSError, UnicodeDecodeError):
                    counts["unreadable_source_files"] += 1
                    continue
                if len(text) < 200:
                    continue
                doc_sha = hashlib.sha256(raw).hexdigest()
                title = next(
                    (line.strip("# ").strip() for line in text.splitlines()[:12]
                     if line.strip().startswith("#") and len(line.strip("# ").strip()) > 3),
                    path.stem.replace("-", " ").replace("_", " "),
                )
                source_files[str(path.relative_to(ROOT))] = {
                    "sha256": doc_sha, "bytes": len(raw), "library_id": library_id,
                }
                made_for_document = 0
                for paragraph in split_paragraphs(text):
                    sentences = split_sentences(paragraph)
                    if not sentences:
                        continue
                    for concept in library_concepts:
                        aliases = concept.get("aliases", [])
                        matching = [
                            sentence for sentence in sentences
                            if any(has_alias(sentence, alias) for alias in aliases)
                        ][:MAX_SENTENCES_PER_CONCEPT_DOCUMENT]
                        for answer in matching:
                            context = paragraph[:1800]
                            question = (
                                f"Según el documento «{title}», ¿qué afirma el texto "
                                f"sobre {concept['label']}?"
                            )
                            identity = normalize(library_id + " " + title + " " + question + " " + answer)
                            digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
                            if digest in rows_seen:
                                counts["duplicate_rows"] += 1
                                continue
                            rows_seen.add(digest)
                            row = {
                                "question": question,
                                "context": context,
                                "answer": answer,
                                "domain": domain,
                                "source": "MINIRONIN-awakened-library",
                                "source_id": str(path.relative_to(ROOT)),
                                "dataset": "awakened-library-rows.jsonl",
                                "license": "Inherited from the preapproved library registry; see original source record",
                                "synthetic": True,
                                "generation_method": "extractive_concept_grounding_v1",
                                "library_id": library_id,
                                "concept_id": concept["id"],
                                "document_sha256": doc_sha,
                                "row_sha256": digest,
                            }
                            out.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
                            counts["rows"] += 1
                            library_counts[library_id] += 1
                            concept_counts[concept["id"]] += 1
                            made_for_document += 1
                            if counts["rows"] >= args.max_rows:
                                break
                        if made_for_document >= MAX_ROWS_PER_DOCUMENT or counts["rows"] >= args.max_rows:
                            break
                    if made_for_document >= MAX_ROWS_PER_DOCUMENT or counts["rows"] >= args.max_rows:
                        break
                counts["source_documents"] += 1
                if counts["rows"] >= args.max_rows:
                    break
            if counts["rows"] >= args.max_rows:
                break

    payload = args.output.read_bytes()
    manifest = {
        "schema": "minironin-awakened-library-rows-v1",
        "rows": counts["rows"],
        "source_documents": counts["source_documents"],
        "source_files": len(source_files),
        "source_file_manifest": source_files,
        "rows_by_library": dict(sorted(library_counts.items())),
        "rows_by_concept": dict(sorted(concept_counts.items())),
        "diagnostics": dict(counts),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "training_authorized": counts["rows"] > 0,
        "validation_policy": "Training-only rows. The training loader must append these rows after the document-disjoint split; they must never enter validation or inference holdouts.",
        "epistemic_policy": "Answers are exact source sentences. No generated paraphrase, unsupported synthesis, or cross-library equivalence is asserted.",
        "provenance_policy": "Every row preserves library_id, source_id, document_sha256 and source registry identity; item-level license remains inherited from the original source record and is not upgraded.",
        "max_rows": args.max_rows,
    }
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items() if k != "source_file_manifest"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
