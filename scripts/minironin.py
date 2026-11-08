#!/usr/bin/env python3
"""Minimal MINIRONIN command line entry point (stdlib + CPU PyTorch only)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def main() -> None:
    parser = argparse.ArgumentParser(prog="minironin", description="Minimal checkpoint inference tools")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("holdout", help="Run the fixed JSONL inference holdout")
    args, remaining = parser.parse_known_args()
    if args.command == "holdout":
        from run_inference_holdout import main as holdout_main
        sys.argv = [sys.argv[0], *remaining]
        holdout_main()


if __name__ == "__main__":
    main()
