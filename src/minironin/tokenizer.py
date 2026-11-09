"""Lossless byte fallback plus deterministic longest-match BACKDOOR_BPE tokens."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable


BASE_ACTIVE_VOCAB = 257
EOS_ID = 256


class ByteNgramTokenizer:
    def __init__(self, manifest: dict):
        if manifest.get("schema") != "minironin-backdoor-bpe-v1":
            raise ValueError("Unsupported tokenizer manifest")
        if manifest.get("base_active_vocab") != BASE_ACTIVE_VOCAB:
            raise ValueError("Base byte/EOS vocabulary must remain 257")
        if manifest.get("eos_id") != EOS_ID:
            raise ValueError("EOS ID must remain 256")
        entries = manifest.get("tokens", [])
        self.tokens: dict[int, bytes] = {}
        self._trie: dict = {}
        expected = BASE_ACTIVE_VOCAB
        for item in entries:
            token_id = int(item["id"])
            raw = bytes.fromhex(item["hex"])
            if token_id != expected:
                raise ValueError("Added token IDs must be contiguous and append-only")
            if len(raw) < 2 or not raw.decode("utf-8", errors="strict"):
                raise ValueError("Added tokens must be non-empty valid UTF-8 sequences")
            if raw in self.tokens.values():
                raise ValueError("Duplicate byte sequence in tokenizer")
            self.tokens[token_id] = raw
            node = self._trie
            for byte in raw:
                node = node.setdefault(byte, {})
            if None in node:
                raise ValueError("Duplicate token path")
            node[None] = token_id
            expected += 1
        self.active_vocab = expected
        if manifest.get("active_vocab", self.active_vocab) != self.active_vocab:
            raise ValueError("Manifest active_vocab does not match token table")
        canonical = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        self.sha256 = hashlib.sha256(canonical).hexdigest()
        self.manifest = manifest

    @classmethod
    def load(cls, path: str | Path) -> "ByteNgramTokenizer":
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    def encode_bytes(self, raw: bytes, *, add_eos: bool = False) -> list[int]:
        result: list[int] = []
        i = 0
        while i < len(raw):
            node = self._trie
            j = i
            best_id = None
            best_end = i
            while j < len(raw) and raw[j] in node:
                node = node[raw[j]]
                j += 1
                if None in node:
                    best_id = node[None]
                    best_end = j
            if best_id is None:
                result.append(raw[i])
                i += 1
            else:
                result.append(best_id)
                i = best_end
        if add_eos:
            result.append(EOS_ID)
        return result

    def encode(self, text: str, *, add_eos: bool = False) -> list[int]:
        return self.encode_bytes(text.encode("utf-8", errors="strict"), add_eos=add_eos)

    def token_bytes(self, token_id: int) -> bytes:
        token_id = int(token_id)
        if 0 <= token_id <= 255:
            return bytes([token_id])
        if token_id == EOS_ID:
            return b""
        if token_id in self.tokens:
            return self.tokens[token_id]
        raise ValueError(f"Token ID {token_id} is outside active vocabulary {self.active_vocab}")

    def byte_length(self, token_id: int) -> int:
        return len(self.token_bytes(token_id))

    def decode_bytes(self, token_ids: Iterable[int], *, stop_at_eos: bool = True) -> bytes:
        out = bytearray()
        for raw_id in token_ids:
            token_id = int(raw_id)
            if token_id == EOS_ID and stop_at_eos:
                break
            out.extend(self.token_bytes(token_id))
        return bytes(out)

    def decode(self, token_ids: Iterable[int], *, stop_at_eos: bool = True) -> str:
        return self.decode_bytes(token_ids, stop_at_eos=stop_at_eos).decode("utf-8", errors="replace")


def initialize_added_embeddings(model, tokenizer: ByteNgramTokenizer, optimizer=None) -> None:
    """Warm-start appended rows from byte embeddings; clear only their optimizer moments."""
    weight = model.token_embedding.weight
    if model.lm_head.weight.data_ptr() != weight.data_ptr():
        raise ValueError("MINIRONIN input/output embeddings must remain tied")
    if tokenizer.active_vocab > weight.shape[0]:
        raise ValueError("Tokenizer exceeds configured embedding rows")
    with __import__("torch").no_grad():
        for token_id, raw in tokenizer.tokens.items():
            byte_ids = list(raw)
            weight[token_id].copy_(weight[byte_ids].mean(dim=0))
        if optimizer is not None:
            state = optimizer.state.get(weight, {})
            for value in state.values():
                if hasattr(value, "ndim") and value.ndim == weight.ndim and value.shape == weight.shape:
                    value[BASE_ACTIVE_VOCAB:tokenizer.active_vocab].zero_()
