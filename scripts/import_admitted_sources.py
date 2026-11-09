#!/usr/bin/env python3
"""Import source-scoped train partitions from RONIN-IA and authored Papers into an admission ledger."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def collect_train_hashes(value, out):
    if isinstance(value, dict):
        for key, item in value.items():
            if "sha256" in key.lower() and isinstance(item, str) and len(item) == 64:
                out.add(item)
            collect_train_hashes(item, out)
    elif isinstance(value, list):
        for item in value:
            collect_train_hashes(item, out)


def collect_payload_names(manifest):
    names = set()
    train = manifest.get("partitions", {}).get("train", {})
    for key, value in train.items():
        if isinstance(value, str) and "train" in value.lower() and value.lower().endswith(
            (".txt", ".md", ".jsonl", ".jsonl.gz", ".ndjson", ".gz")
        ):
            names.add(Path(value).name)
    for section in (manifest.get("artifact_files", []),
                    manifest.get("materialization", {}).get("output_files", []),
                    manifest.get("materialization", {}).get("artifact", {}).get("verified_contents", [])):
        for value in section:
            if isinstance(value, str) and "train" in value.lower() and value.lower().endswith(
                (".txt", ".md", ".jsonl", ".jsonl.gz", ".ndjson", ".gz")
            ):
                names.add(Path(value).name)
    names.update({"train.txt", "documents.train.jsonl", "documents.train.jsonl.gz",
                  "train.jsonl", "train.jsonl.gz", "documents.jsonl.gz"})
    return names


def language_for(manifest):
    values = manifest.get("languages") or manifest.get("language")
    if isinstance(values, list):
        return ",".join(sorted(str(x) for x in values))
    if isinstance(values, str) and values:
        return values
    counts = manifest.get("language_counts") or manifest.get("aggregate", {}).get("language_counts")
    if isinstance(counts, dict) and counts:
        return ",".join(sorted(str(x) for x in counts))
    return "und"


def domain_for(dataset_id, manifest):
    value = (dataset_id + " " + json.dumps(manifest.get("documents_by_domain", {}))).lower()
    if any(x in value for x in ("math", "lean", "algebra", "proof")):
        return "math"
    if any(x in value for x in ("literature", "book", "classics", "novel")):
        return "books"
    if any(x in value for x in ("nasa", "science", "arxiv", "physics")):
        return "science"
    if any(x in value for x in ("covost", "translation", "language")):
        return "language"
    return "general"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--roninia-root", type=Path)
    parser.add_argument("--papers-root", type=Path)
    parser.add_argument("--minironin-root", type=Path, default=Path("."))
    parser.add_argument("--heretic-artifact-root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows, audit = [], []
    if args.roninia_root:
        base = args.roninia_root.resolve()
        for manifest_path in sorted((base / "data/datasets/admitted").rglob("manifest.json")):
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            train = manifest.get("partitions", {}).get("train", {})
            if manifest.get("status") != "admitted_scoped_training_partition" or train.get("training_eligible") is not True:
                audit.append({"manifest": str(manifest_path), "status": "skipped_not_scoped_train_admitted"})
                continue
            expected_hashes = set()
            collect_train_hashes(train, expected_hashes)
            names = collect_payload_names(manifest)
            folder = manifest_path.parent
            candidates = sorted({p for name in names for p in folder.rglob(name) if p.is_file()})
            selected = None
            selected_hash = None
            for candidate in candidates:
                digest = sha(candidate)
                if digest in expected_hashes:
                    selected, selected_hash = candidate, digest
                    break
            if selected is None:
                audit.append({"manifest": str(manifest_path), "status": "skipped_no_exact_train_payload_hash",
                              "candidate_names": sorted(names), "expected_hashes": sorted(expected_hashes)})
                continue
            dataset_id = str(manifest.get("dataset_id", folder.name))
            rights = manifest.get("rights", {})
            source = manifest.get("source", {})
            license_name = rights.get("license") or source.get("license") or manifest.get("license")
            if not license_name:
                audit.append({"manifest": str(manifest_path), "status": "skipped_no_license"})
                continue
            rel = selected.resolve().relative_to(Path.cwd().resolve()).as_posix() if selected.resolve().is_relative_to(Path.cwd().resolve()) else selected.as_posix()
            rows.append({
                "document_id": f"RONIN_IA:{dataset_id}:train:{selected_hash[:16]}",
                "source_id": f"RONIN_IA:{dataset_id}",
                "project": "RONIN-IA",
                "path": rel,
                "sha256": selected_hash,
                "license": license_name,
                "rights_status": "approved_for_spain_training",
                "admission_status": "admitted",
                "train_eligible": True,
                "retrieval_eligible": True,
                "redistribution": False,
                "epistemic_type": "source_scoped_train_admitted",
                "domain": domain_for(dataset_id, manifest),
                "language": language_for(manifest),
                "provenance_ref": str(manifest_path),
            })
            audit.append({"manifest": str(manifest_path), "status": "admitted_exact_train_payload",
                          "payload": str(selected), "sha256": selected_hash})

    if args.papers_root:
        papers = args.papers_root.resolve()
        for path in sorted(p for p in papers.glob("*.md") if p.name.lower() != "readme.md"):
            digest = sha(path)
            rel = path.resolve().relative_to(Path.cwd().resolve()).as_posix() if path.resolve().is_relative_to(Path.cwd().resolve()) else path.as_posix()
            rows.append({
                "document_id": f"Papers:{digest[:20]}",
                "source_id": "Papers",
                "project": "Papers",
                "path": rel,
                "sha256": digest,
                "license": "project-authored-internal",
                "rights_status": "owner_authored_internal",
                "admission_status": "admitted",
                "train_eligible": True,
                "retrieval_eligible": True,
                "redistribution": False,
                "epistemic_type": "author_original",
                "domain": "research",
                "language": "es",
                "provenance_ref": "orbitalronin94/Papers",
            })
        audit.append({"source": "Papers", "status": "owner_authored_markdown_scanned"})

    if args.heretic_artifact_root:
        artifact_root = args.heretic_artifact_root.resolve()
        curated = artifact_root / "incoming/cosmopedia-curated.jsonl"
        curated_manifest = artifact_root / "out/COSMOPEDIA-CURATION-MANIFEST.json"
        audit_report = artifact_root / "reports/corpus-audit/GLOBAL-CORPUS-AUDIT.json"
        if not all(path.is_file() for path in (curated, curated_manifest, audit_report)):
            raise SystemExit("HERETIC admitted artifact is incomplete; refusing partial import")
        curation = json.loads(curated_manifest.read_text(encoding="utf-8"))
        heretic_audit = json.loads(audit_report.read_text(encoding="utf-8"))
        digest = sha(curated)
        if curation.get("schema") != "heretic-cosmopedia-curated-candidate-v1":
            raise SystemExit("Unexpected HERETIC curation schema")
        if (curation.get("source") != "HuggingFaceTB/cosmopedia"
                or curation.get("revision") != "0ae6ec63f91742bd2d1eaef4f02232c55d719385"
                or curation.get("config") != "auto_math_text"
                or curation.get("split") != "train"
                or curation.get("accepted_rows") != 4734
                or curation.get("curated_sha256") != digest
                or curation.get("training_authorized") is not False):
            raise SystemExit("HERETIC curation manifest/hash does not match the admitted snapshot")
        if (heretic_audit.get("schema") != "heretic-global-train-corpus-audit-v2"
                or heretic_audit.get("training_authorized") is not True
                or heretic_audit.get("exact_holdout_question_matches") != 0
                or heretic_audit.get("source_counts", {}).get("cosmopedia") != 4734):
            raise SystemExit("HERETIC global audit did not authorize this exact curated source")
        rows.append({
            "document_id": f"HERETIC:Cosmopedia:auto_math_text:{digest[:16]}",
            "source_id": "HERETIC:Cosmopedia-v0.1-curated",
            "project": "HERETIC-RONIN",
            "path": (curated.resolve().relative_to(Path.cwd().resolve()).as_posix()
                     if curated.resolve().is_relative_to(Path.cwd().resolve())
                     else curated.resolve().as_posix()),
            "sha256": digest,
            "license": "Apache-2.0 (dataset-card declaration; upstream lineage caveat retained)",
            "rights_status": "approved_internal_research",
            "admission_status": "admitted",
            "train_eligible": True,
            "retrieval_eligible": True,
            "redistribution": False,
            "epistemic_type": "synthetic_educational_prose_not_gold_answers",
            "domain": "education_math",
            "language": "en",
            "provenance_ref": "HERETIC-RONIN run 42362365447 artifact 13570263309",
        })
        audit.append({"source": "HERETIC-RONIN Cosmopedia v0.1", "status": "admitted_exact_artifact_and_global_audit",
                      "payload": str(curated), "sha256": digest, "rows": 4734})

    if args.minironin_root:
        root = args.minironin_root.resolve()
        curated = [
            ("data/curated/minironin-behavior-v1.jsonl", "behavior"),
            ("data/curated/minironin-identity-v1.jsonl", "identity"),
            ("data/curated/engineering-lessons-v1.jsonl", "engineering"),
            ("data/curated/minironin-engineering-v1.jsonl", "engineering"),
            ("data/curated/minironin-performance-engineering-v1.jsonl", "engineering"),
        ]
        for relative, domain in curated:
            path = root / relative
            if not path.is_file():
                continue
            digest = sha(path)
            rows.append({
                "document_id": f"MINIRONIN:{digest[:20]}",
                "source_id": "MINIRONIN-authored-curated",
                "project": "MINIRONIN",
                "path": path.resolve().relative_to(Path.cwd().resolve()).as_posix(),
                "sha256": digest,
                "license": "project-authored-internal",
                "rights_status": "owner_authored_internal",
                "admission_status": "admitted",
                "train_eligible": True,
                "retrieval_eligible": True,
                "redistribution": False,
                "epistemic_type": "curated_or_synthetic_mixed",
                "domain": domain,
                "language": "es",
                "provenance_ref": relative,
            })
        audit.append({"source": "MINIRONIN-curated", "status": "explicit_authored_file_allowlist"})

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        for row in sorted(rows, key=lambda item: (item["source_id"], item["path"])):
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    report = {
        "admission_rows": len(rows),
        "roninia_exact_train_payloads": sum(r["source_id"].startswith("RONIN_IA:") for r in rows),
        "papers_documents": sum(r["source_id"] == "Papers" for r in rows),
        "minironin_curated_files": sum(r["source_id"] == "MINIRONIN-authored-curated" for r in rows),
        "heretic_admitted_sources": sum(r["source_id"].startswith("HERETIC:") for r in rows),
        "audit": audit,
        "holdout_read": False,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
