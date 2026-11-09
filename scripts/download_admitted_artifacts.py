#!/usr/bin/env python3
"""Materialize only artifacts explicitly pinned by admitted RONIN-IA manifests."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def find_artifact_nodes(value):
    if isinstance(value, dict):
        if value.get("workflow_run_id") and value.get("artifact_name"):
            yield value
        for child in value.values():
            yield from find_artifact_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from find_artifact_nodes(child)


def train_hashes(train):
    result = set()
    def walk(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if "sha256" in key.lower() and isinstance(child, str) and len(child) == 64:
                    result.add(child)
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    walk(train)
    return result


def has_verified_payload(folder, manifest):
    expected = train_hashes(manifest.get("partitions", {}).get("train", {}))
    if not expected:
        return False
    return any(path.is_file() and sha(path) in expected for path in folder.rglob("*"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--roninia-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    base = args.roninia_root.resolve()
    audit = []
    for manifest_path in sorted((base / "data/datasets/admitted").rglob("manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        train = manifest.get("partitions", {}).get("train", {})
        if manifest.get("status") != "admitted_scoped_training_partition" or train.get("training_eligible") is not True:
            continue
        folder = manifest_path.parent
        dataset_id = str(manifest.get("dataset_id", folder.name))
        if has_verified_payload(folder, manifest):
            audit.append({"dataset_id": dataset_id, "status": "payload_already_present_and_hash_verified"})
            continue
        artifacts = list(find_artifact_nodes(manifest))
        if not artifacts:
            audit.append({"dataset_id": dataset_id, "status": "no_pinned_artifact_reference"})
            continue
        downloaded = False
        for artifact in artifacts:
            run_id = str(artifact["workflow_run_id"])
            name = str(artifact["artifact_name"])
            target = folder / "downloaded-artifact"
            target.mkdir(parents=True, exist_ok=True)
            command = [
                "gh", "run", "download", run_id,
                "--repo", "orbitalronin94/RONIN-IA",
                "--name", name,
                "--dir", str(target),
            ]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0:
                downloaded = True
                audit.append({
                    "dataset_id": dataset_id, "status": "downloaded_pinned_artifact",
                    "run_id": run_id, "artifact_name": name, "target": str(target),
                })
                break
            audit.append({
                "dataset_id": dataset_id, "status": "artifact_download_failed",
                "run_id": run_id, "artifact_name": name,
                "stderr": result.stderr[-1200:],
            })
        if downloaded and not has_verified_payload(target, manifest):
            audit.append({"dataset_id": dataset_id, "status": "downloaded_but_train_hash_not_verified"})
    args.output.mkdir(parents=True, exist_ok=True)
    report = {"datasets_checked": len(audit), "audit": audit, "holdout_read": False}
    (args.output / "artifact-download-audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
