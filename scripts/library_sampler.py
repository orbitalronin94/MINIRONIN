"""Deterministic library-aware document/window sampler for MINIRONIN.

Input rows require: id (or sha256), library_id, split='train', token_ids.
Sampling is hierarchical: weighted library -> shuffled document cycle -> window.
"""
from __future__ import annotations

import random
from collections import Counter, defaultdict
from collections.abc import Sequence
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
        self.seed = seed
        self.weights = {str(k): float(v) for k, v in weights.items()}
        if not self.weights or any(v <= 0 for v in self.weights.values()):
            raise ValueError("Every configured library weight must be positive")

        self.documents: dict[str, list[Mapping]] = defaultdict(list)
        seen_ids: set[tuple[str, str]] = set()
        for doc in documents:
            if doc.get("split") != "train":
                raise ValueError("LibrarySampler accepts training-split documents only")
            library = doc.get("library_id")
            tokens = doc.get("token_ids")
            doc_id = doc.get("id") or doc.get("sha256")
            sequence_like = isinstance(tokens, Sequence) or (
                hasattr(tokens, "__len__") and hasattr(tokens, "__getitem__")
            )
            if not library or not sequence_like or not doc_id:
                raise ValueError("Each document needs library_id, id/sha256 and token_ids")
            identity = (str(library), str(doc_id))
            if identity in seen_ids:
                raise ValueError(f"Duplicate document identity: {identity}")
            seen_ids.add(identity)
            if len(tokens) >= minimum_tokens:
                self.documents[str(library)].append(doc)

        self.available = sorted(k for k in self.weights if self.documents.get(k))
        if not self.available:
            raise ValueError("No weighted libraries contain eligible training documents")
        total = sum(self.weights[k] for k in self.available)
        self.probabilities = {k: self.weights[k] / total for k in self.available}

        self._eligible_cache: dict[tuple[str, int], list[Mapping]] = {}
        self._decks: dict[tuple[str, int], list[Mapping]] = {}
        self._deck_positions: Counter[tuple[str, int]] = Counter()
        self._last_sequence_length: dict[str, int] = {}
        self.tokens_seen: Counter[str] = Counter()
        self.document_uses: Counter[str] = Counter()
        self.unique_documents: dict[str, set[str]] = defaultdict(set)
        self._uses_by_document: Counter[tuple[str, str]] = Counter()

    def _eligible_documents(self, library: str, sequence_length: int) -> list[Mapping]:
        key = (library, sequence_length)
        self._last_sequence_length[library] = sequence_length
        if key not in self._eligible_cache:
            self._eligible_cache[key] = [
                doc for doc in self.documents[library]
                if len(doc["token_ids"]) > sequence_length
            ]
            if not self._eligible_cache[key]:
                raise ValueError(
                    f"Library {library!r} has no document longer than the requested window"
                )
        return self._eligible_cache[key]

    def _next_document(self, library: str, sequence_length: int) -> Mapping:
        key = (library, sequence_length)
        eligible = self._eligible_documents(library, sequence_length)
        deck = self._decks.get(key)
        position = self._deck_positions[key]
        if deck is None or position >= len(deck):
            deck = list(eligible)
            self.rng.shuffle(deck)
            self._decks[key] = deck
            self._deck_positions[key] = 0
        position = self._deck_positions[key]
        self._deck_positions[key] += 1
        return deck[position]

    def sample_window(self, sequence_length: int) -> tuple[list[int], dict[str, str]]:
        if sequence_length < 1:
            raise ValueError("sequence_length must be positive")
        library = self.rng.choices(
            self.available, weights=[self.probabilities[k] for k in self.available], k=1
        )[0]
        doc = self._next_document(library, sequence_length)
        tokens = doc["token_ids"]
        start = self.rng.randrange(0, len(tokens) - sequence_length)
        window = list(tokens[start:start + sequence_length + 1])
        doc_id = str(doc.get("id") or doc.get("sha256"))
        self.tokens_seen[library] += sequence_length
        self.document_uses[library] += 1
        self.unique_documents[library].add(doc_id)
        self._uses_by_document[(library, doc_id)] += 1
        return window, {"library_id": library, "document_id": doc_id}

    def make_batch(
        self, batch_size: int, sequence_length: int
    ) -> tuple[list[list[int]], list[dict[str, str]]]:
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
            sequence_length = self._last_sequence_length.get(library, 1)
            eligible_count = len(self._eligible_documents(library, sequence_length))
            uses = self.document_uses[library]
            unique = len(self.unique_documents[library])
            rows[library] = {
                "target_share": round(self.probabilities[library], 8),
                "observed_target_token_share": round(
                    self.tokens_seen[library] / total if total else 0.0, 8
                ),
                "sampled_target_tokens": self.tokens_seen[library],
                "document_uses": uses,
                "eligible_documents_for_sequence_length": eligible_count,
                "sequence_length": sequence_length,
                "unique_documents": unique,
                "document_coverage": round(unique / eligible_count, 8) if eligible_count else 0.0,
                "repeat_document_uses": max(0, uses - unique),
            }
        return {
            "sampler": "library-aware-v2",
            "seed": self.seed,
            "total_sampled_target_tokens": total,
            "libraries": rows,
        }
