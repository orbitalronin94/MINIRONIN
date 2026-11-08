"""Deterministic library-aware document/window sampler for MINIRONIN.

Documents must carry: id, library_id, split='train', and token_ids (list[int]).
Validation/holdout material is rejected, never silently sampled.
"""
from __future__ import annotations

import random
from collections import Counter, defaultdict
from typing import Iterable, Mapping


class LibrarySampler:
    def __init__(
        self,
        documents: Iterable[Mapping],
        weights: Mapping[str, float],
        *,
        seed: int = 20261108,
        minimum_tokens: int = 2,
    ) -> None:
        self.rng = random.Random(seed)
        self.weights = {str(k): float(v) for k, v in weights.items()}
        if not self.weights or any(v <= 0 for v in self.weights.values()):
            raise ValueError("Every configured library weight must be positive")
        self.documents: dict[str, list[Mapping]] = defaultdict(list)
        self.library_tokens: dict[str, int] = {}
        for doc in documents:
            if doc.get("split") != "train":
                raise ValueError("LibrarySampler accepts training-split documents only")
            library = doc.get("library_id")
            tokens = doc.get("token_ids")
            if not library or not isinstance(tokens, (list, tuple)):
                raise ValueError("Each document needs library_id and token_ids")
            if len(tokens) < minimum_tokens:
                continue
            self.documents[str(library)].append(doc)
        self.available = sorted(k for k in self.weights if self.documents.get(k))
        if not self.available:
            raise ValueError("No weighted libraries contain eligible training documents")
        total = sum(self.weights[k] for k in self.available)
        self.probabilities = {k: self.weights[k] / total for k in self.available}
        self.tokens_seen: Counter[str] = Counter()
        self.document_uses: Counter[str] = Counter()
        self.unique_documents: dict[str, set[str]] = defaultdict(set)

    def sample_window(self, sequence_length: int) -> tuple[list[int], dict[str, str]]:
        if sequence_length < 1:
            raise ValueError("sequence_length must be positive")
        library = self.rng.choices(
            self.available, weights=[self.probabilities[k] for k in self.available], k=1
        )[0]
        candidates = [d for d in self.documents[library] if len(d["token_ids"]) > sequence_length]
        if not candidates:
            raise ValueError(f"Library {library!r} has no document longer than the requested window")
        doc = self.rng.choice(candidates)
        tokens = doc["token_ids"]
        start = self.rng.randrange(0, len(tokens) - sequence_length)
        window = list(tokens[start:start + sequence_length + 1])
        doc_id = str(doc.get("id") or doc.get("sha256") or f"anonymous-{id(doc)}")
        self.tokens_seen[library] += sequence_length
        self.document_uses[library] += 1
        self.unique_documents[library].add(doc_id)
        return window, {"library_id": library, "document_id": doc_id}

    def make_batch(self, batch_size: int, sequence_length: int) -> tuple[list[list[int]], list[dict[str, str]]]:
        if batch_size < 1:
            raise ValueError("batch_size must be positive")
        rows, provenance = [], []
        for _ in range(batch_size):
            row, source = self.sample_window(sequence_length)
            rows.append(row)
            provenance.append(source)
        return rows, provenance

    def report(self) -> dict:
        total = sum(self.tokens_seen.values())
        rows = {}
        for library in self.available:
            observed = self.tokens_seen[library] / total if total else 0.0
            rows[library] = {
                "target_share": round(self.probabilities[library], 8),
                "observed_token_share": round(observed, 8),
                "sampled_tokens": self.tokens_seen[library],
                "document_uses": self.document_uses[library],
                "unique_documents": len(self.unique_documents[library]),
            }
        return {
            "sampler": "library-aware-v1",
            "seeded": True,
            "total_sampled_tokens": total,
            "libraries": rows,
        }
