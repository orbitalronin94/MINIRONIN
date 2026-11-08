#!/usr/bin/env python3
"""Synthetic smoke benchmark for the BPE token store and library sampler."""
from __future__ import annotations

import argparse
import json
import tempfile
import time

from library_sampler import LibrarySampler
from token_store import TokenStore, build_token_store


LIBRARIES = ("heretic", "prodatphil", "anarchist", "classics", "minironin_behavior")
WEIGHTS = {
    "heretic": 0.5171,
    "prodatphil": 0.1477,
    "anarchist": 0.0225,
    "classics": 0.0225,
    "minironin_behavior": 0.2902,
}


def synthetic_documents(document_count: int, tokens_per_document: int):
    for index in range(document_count):
        library = LIBRARIES[index % len(LIBRARIES)]
        yield {
            "id": f"{library}-{index:08d}",
            "library_id": library,
            "split": "train",
            "token_ids": ((position + index) % 4096 for position in range(tokens_per_document)),
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--documents", type=int, default=250)
    parser.add_argument("--tokens-per-document", type=int, default=2048)
    parser.add_argument("--samples", type=int, default=5000)
    parser.add_argument("--sequence-length", type=int, default=128)
    args = parser.parse_args()
    if min(args.documents, args.tokens_per_document, args.samples, args.sequence_length) < 1:
        parser.error("all benchmark dimensions must be positive")
    if args.tokens_per_document <= args.sequence_length:
        parser.error("tokens-per-document must exceed sequence-length")

    with tempfile.TemporaryDirectory(prefix="minironin-library-bench-") as temp:
        started = time.perf_counter()
        manifest = build_token_store(
            synthetic_documents(args.documents, args.tokens_per_document),
            temp,
            tokenizer_sha256="synthetic-bpe4096-benchmark",
            corpus_signature="synthetic-library-corpus-v1",
        )
        build_seconds = time.perf_counter() - started

        with TokenStore(temp, expected_tokenizer_sha256="synthetic-bpe4096-benchmark",
                        expected_corpus_signature="synthetic-library-corpus-v1") as store:
            sampler = LibrarySampler(store.documents(), WEIGHTS, seed=20261108)
            preflight = sampler.validate_sequence_length(args.sequence_length)
            started = time.perf_counter()
            checksum = 0
            for _ in range(args.samples):
                window, _ = sampler.sample_window(args.sequence_length)
                checksum += sum(window)
            sample_seconds = time.perf_counter() - started
            report = sampler.report()

    result = {
        "benchmark": "synthetic-smoke-not-production-corpus",
        "documents": args.documents,
        "tokens_per_document": args.tokens_per_document,
        "sequence_length": args.sequence_length,
        "samples": args.samples,
        "token_store_build_seconds": round(build_seconds, 4),
        "sampling_seconds": round(sample_seconds, 4),
        "windows_per_second": round(args.samples / sample_seconds, 2),
        "target_tokens_per_second": round(args.samples * args.sequence_length / sample_seconds, 2),
        "token_store_bytes": manifest["bytes"],
        "token_store_sha256": manifest["tokens_sha256"],
        "preflight_eligible_documents": preflight,
        "sample_checksum": checksum,
        "exposure": report,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
