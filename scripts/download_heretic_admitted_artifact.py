#!/usr/bin/env python3
"""Fetch the exact HERETIC global-audit artifact and unpack it fail-closed."""
from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import zipfile
from pathlib import Path, PurePosixPath

ARTIFACT_ID = "13570263309"
ARCHIVE_SHA256 = "db826ced0bcd9158fee17d254faad203e7fe9e317f510e12fcf2cd448bb42dc9"
URL = f"https://api.github.com/repos/orbitalronin94/HERETIC-RONIN/actions/artifacts/{ARTIFACT_ID}/zip"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--archive", type=Path, default=Path("artifacts/heretic-audit.zip"))
    args = parser.parse_args()
    token = os.environ.get("SOURCE_ARTIFACT_READ_TOKEN", "").strip()
    if not token:
        raise SystemExit("SOURCE_ARTIFACT_READ_TOKEN is required (Actions read access to HERETIC-RONIN)")
    args.archive.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run([
        "curl", "--fail", "--location", "--retry", "4",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Accept: application/vnd.github+json",
        URL, "-o", str(args.archive),
    ], capture_output=True, text=True)
    if result.returncode:
        raise SystemExit(f"HERETIC artifact download failed: {result.stderr[-2000:]}")
    digest = hashlib.sha256(args.archive.read_bytes()).hexdigest()
    if digest != ARCHIVE_SHA256:
        raise SystemExit(f"HERETIC artifact archive SHA-256 mismatch: {digest}")
    args.output.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.archive) as archive:
        for member in archive.infolist():
            name = PurePosixPath(member.filename)
            if name.is_absolute() or ".." in name.parts:
                raise SystemExit(f"Unsafe path in HERETIC artifact: {member.filename}")
        archive.extractall(args.output)
    expected = [
        args.output / "incoming/cosmopedia-curated.jsonl",
        args.output / "out/COSMOPEDIA-CURATION-MANIFEST.json",
        args.output / "reports/corpus-audit/GLOBAL-CORPUS-AUDIT.json",
    ]
    if not all(path.is_file() for path in expected):
        raise SystemExit("HERETIC artifact is missing one or more required audit files")
    print(f"Verified HERETIC artifact {ARTIFACT_ID}; sha256={digest}")


if __name__ == "__main__":
    main()
