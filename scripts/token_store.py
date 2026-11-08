"""Compact, read-only memory-mapped uint16 token store for BPE-4096 corpora."""
from __future__ import annotations

import hashlib
import json
from array import array
import sys
import mmap
import os
import struct
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping

UINT16_MAX = 65535
FORMAT = "minironin-u16-v1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_token_store(
    documents: Iterable[Mapping],
    output_dir: str | Path,
    *,
    tokenizer_sha256: str,
    corpus_signature: str,
) -> dict:
    if not tokenizer_sha256 or not corpus_signature:
        raise ValueError("Tokenizer SHA-256 and training-corpus signature are required")
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    token_path, temp_path = root / "tokens.u16", root / "tokens.u16.tmp"
    index, seen, total_tokens = [], set(), 0

    with temp_path.open("wb") as stream:
        for doc in documents:
            if doc.get("split") != "train":
                raise ValueError("Token store accepts training-split documents only")
            library_id = doc.get("library_id")
            doc_id = doc.get("id") or doc.get("sha256")
            tokens = doc.get("token_ids")
            if not library_id or not doc_id or not hasattr(tokens, "__iter__"):
                raise ValueError("Each row needs library_id, id/sha256 and token_ids")
            identity = (str(library_id), str(doc_id))
            if identity in seen:
                raise ValueError(f"Duplicate document identity: {identity}")
            seen.add(identity)
            offset = total_tokens
            packed = array("H")
            for token in tokens:
                token = int(token)
                if token < 0 or token > UINT16_MAX:
                    raise ValueError(f"Token ID outside uint16 range: {token}")
                packed.append(token)
            if sys.byteorder != "little":
                packed.byteswap()
            count = len(packed)
            if count:
                packed.tofile(stream)
                index.append({
                    "id": str(doc_id), "library_id": str(library_id),
                    "split": "train", "offset_tokens": offset,
                    "length_tokens": count,
                })
                total_tokens += count
        stream.flush()
        os.fsync(stream.fileno())

    if total_tokens == 0:
        temp_path.unlink(missing_ok=True)
        raise ValueError("Cannot build an empty token store")
    os.replace(temp_path, token_path)

    index_path, index_temp = root / "index.json", root / "index.json.tmp"
    index_temp.write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    os.replace(index_temp, index_path)

    manifest = {
        "format": FORMAT,
        "dtype": "little-endian uint16",
        "tokenizer_sha256": tokenizer_sha256,
        "training_corpus_signature": corpus_signature,
        "tokens_sha256": _sha256(token_path),
        "index_sha256": _sha256(index_path),
        "documents": len(index),
        "libraries": dict(sorted(Counter(row["library_id"] for row in index).items())),
        "total_tokens": total_tokens,
        "bytes": token_path.stat().st_size,
    }
    manifest_path, manifest_temp = root / "manifest.json", root / "manifest.json.tmp"
    manifest_temp.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(manifest_temp, manifest_path)
    return manifest


class TokenSpan:
    """Sequence view over one document's uint16 range in a shared mmap."""

    def __init__(self, mapped: mmap.mmap, offset_tokens: int, length_tokens: int):
        self._mapped = mapped
        self._offset = offset_tokens * 2
        self._length = length_tokens

    def __len__(self) -> int:
        return self._length

    def __getitem__(self, item):
        if isinstance(item, slice):
            start, stop, step = item.indices(self._length)
            if step == 1:
                count = stop - start
                if count == 0:
                    return []
                return list(struct.unpack_from(
                    f"<{count}H", self._mapped, self._offset + start * 2
                ))
            return [
                struct.unpack_from("<H", self._mapped, self._offset + i * 2)[0]
                for i in range(start, stop, step)
            ]
        index = int(item)
        if index < 0:
            index += self._length
        if index < 0 or index >= self._length:
            raise IndexError(index)
        return struct.unpack_from("<H", self._mapped, self._offset + index * 2)[0]


class TokenStore:
    def __init__(
        self,
        root: str | Path,
        *,
        expected_tokenizer_sha256: str | None = None,
        expected_corpus_signature: str | None = None,
        verify_file_sha256: bool = True,
    ):
        self.root = Path(root)
        self.manifest = json.loads(
            (self.root / "manifest.json").read_text(encoding="utf-8")
        )
        if self.manifest.get("format") != FORMAT:
            raise ValueError("Unsupported token-store format")
        if expected_tokenizer_sha256 and self.manifest.get("tokenizer_sha256") != expected_tokenizer_sha256:
            raise ValueError("Token-store tokenizer SHA-256 mismatch")
        if expected_corpus_signature and self.manifest.get("training_corpus_signature") != expected_corpus_signature:
            raise ValueError("Token-store training corpus signature mismatch")

        self.path = self.root / "tokens.u16"
        self.index_path = self.root / "index.json"
        if self.path.stat().st_size != self.manifest.get("bytes"):
            raise ValueError("Token-store byte length mismatch")
        if self.manifest.get("bytes") != self.manifest.get("total_tokens", -1) * 2:
            raise ValueError("Token-store token count/byte length mismatch")
        if verify_file_sha256:
            if _sha256(self.path) != self.manifest.get("tokens_sha256"):
                raise ValueError("Token-store SHA-256 mismatch")
            if _sha256(self.index_path) != self.manifest.get("index_sha256"):
                raise ValueError("Token-store index SHA-256 mismatch")

        self._index = json.loads(self.index_path.read_text(encoding="utf-8"))
        cursor = 0
        for row in self._index:
            if row.get("split") != "train" or row.get("offset_tokens") != cursor:
                raise ValueError("Token-store index split or offset sequence is invalid")
            length = int(row.get("length_tokens", 0))
            if length < 1:
                raise ValueError("Token-store index contains an empty document")
            cursor += length
        if cursor != self.manifest.get("total_tokens") or len(self._index) != self.manifest.get("documents"):
            raise ValueError("Token-store index totals do not match manifest")

        self._file = self.path.open("rb")
        self._mapped = mmap.mmap(self._file.fileno(), 0, access=mmap.ACCESS_READ)

    def documents(self):
        for row in self._index:
            yield {
                "id": row["id"],
                "library_id": row["library_id"],
                "split": row["split"],
                "token_ids": TokenSpan(
                    self._mapped, row["offset_tokens"], row["length_tokens"]
                ),
            }

    def close(self):
        self._mapped.close()
        self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()
