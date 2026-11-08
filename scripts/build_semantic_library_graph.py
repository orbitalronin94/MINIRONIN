#!/usr/bin/env python3
"""Build deterministic cross-library concept graph and stable semantic labels."""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/semantic/LIBRARY_REGISTRY.json"
ANARCHIST_SOURCES = ROOT / "data/anarchist/SOURCES.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="data/semantic")
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    concepts = {item["id"]: item for item in registry["concepts"]}
    nodes = []
    edges = []
    token_map = {}
    for concept_id, concept in sorted(concepts.items()):
        token = "SEM:" + concept_id
        token_map[token] = {
            "concept_id": concept_id,
            "label": concept["label"],
            "aliases": concept.get("aliases", []),
            "description": concept.get("description", ""),
        }
        nodes.append({"id": "concept:" + concept_id, "type": "concept", "label": concept["label"], "semantic_token": token})
        for related in concept.get("relations", []):
            if related in concepts and concept_id < related:
                edges.append({"source": "concept:" + concept_id, "target": "concept:" + related, "type": "related_concept", "weight": 1.0})
    library_concepts = {}
    for library in registry["libraries"]:
        library_id = library["id"]
        ids = sorted(set(library.get("concepts", [])) & set(concepts))
        library_concepts[library_id] = ids
        nodes.append({"id": "library:" + library_id, "type": "library", "label": library["name"], "project": library.get("project")})
        for concept_id in ids:
            edges.append({"source": "library:" + library_id, "target": "concept:" + concept_id, "type": "covers_concept", "weight": 1.0})
    library_ids = sorted(library_concepts)
    for i, left in enumerate(library_ids):
        for right in library_ids[i + 1:]:
            shared = sorted(set(library_concepts[left]) & set(library_concepts[right]))
            if shared:
                edges.append({
                    "source": "library:" + left,
                    "target": "library:" + right,
                    "type": "cross_library_semantic_overlap",
                    "weight": round(len(shared) / max(1, len(set(library_concepts[left]) | set(library_concepts[right]))), 6),
                    "shared_concepts": shared,
                })
    for relation in registry.get("concept_relations", []):
        left, right = relation.get("from"), relation.get("to")
        if left in concepts and right in concepts:
            edges.append({
                "source": "concept:" + left,
                "target": "concept:" + right,
                "type": relation.get("type", "cross_domain_bridge"),
                "weight": 0.5,
                "note": relation.get("note", ""),
            })
    source_rows = [json.loads(line) for line in ANARCHIST_SOURCES.read_text(encoding="utf-8").splitlines() if line.strip()]
    for source in source_rows:
        source_node = "work:" + source["id"]
        nodes.append({"id": source_node, "type": "work", "label": source["title"], "author": source["author"], "rights_status": source["rights_status"]})
        edges.append({"source": source_node, "target": "library:anarchist-classics", "type": "member_of_library", "weight": 1.0})
        for concept_id in sorted(set(source.get("concepts", [])) & set(concepts)):
            edges.append({"source": source_node, "target": "concept:" + concept_id, "type": "work_covers_concept", "weight": 1.0})
    graph = {
        "schema": "minironin-semantic-library-graph-v1",
        "description": "Deterministic concept graph linking libraries, works and concepts. Weights measure declared concept overlap, not truth or ideological agreement.",
        "token_semantics": "SEM:<concept_id> labels are stable semantic annotations. MINIRONIN currently uses a byte-level vocabulary (257 IDs); these labels are NOT atomic tokenizer IDs and do not change the model vocabulary.",
        "nodes": nodes,
        "edges": edges,
        "library_concepts": library_concepts,
        "counts": {"libraries": len(library_concepts), "concepts": len(concepts), "nodes": len(nodes), "edges": len(edges), "semantic_tokens": len(token_map)},
    }
    (out / "semantic-library-graph.json").write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "semantic-tokens.json").write_text(json.dumps({"schema": "minironin-semantic-tokens-v1", "tokens": token_map}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(graph["counts"], ensure_ascii=False))


if __name__ == "__main__":
    main()
