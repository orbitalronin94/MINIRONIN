#!/usr/bin/env python3
"""Create evidence-conditioned training rows from the canonical admitted inventory."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def sentence_candidates(text: str):
    for item in re.split(r"(?<=[.!?])\s+|\n+", text):
        item = re.sub(r"\s+", " ", item).strip()
        if 45 <= len(item) <= 500:
            yield item


def qa_rows(path: Path):
    if path.name.lower().endswith(".jsonl.gz"):
        import gzip
        stream = gzip.open(path, "rt", encoding="utf-8", errors="replace")
    elif path.suffix.lower() in {".jsonl", ".ndjson"}:
        stream = path.open(encoding="utf-8", errors="replace")
    else:
        return
    with stream:
        for line in stream:
            if not line.strip().startswith("{"):
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            question = row.get("question") or row.get("instruccion") or row.get("prompt")
            answer = row.get("answer") or row.get("respuesta") or row.get("target")
            context = row.get("context") or row.get("evidence") or row.get("evidencia")
            verified = (
                row.get("answer_verified") is True
                or row.get("curation_status") in {"verified", "manually_reviewed"}
                or row.get("curacion") in {"redactado_manual_desde_log", "revision_manual_aprobada"}
                or row.get("tag") in {"answerable_grounded", "identity_grounded", "identity_boundary", "unknown_abstain"}
            )
            if question and answer and context and verified:
                yield str(question).strip(), str(answer).strip(), str(context).strip()

def row_for(doc, task_type, prompt, answer, index):
    source_key = f"{doc['document_id']}:{task_type}:{index}"
    row_id = hashlib.sha256(source_key.encode()).hexdigest()[:24]
    text = prompt.rstrip() + "\n" + answer.strip()
    return {
        "document_id": row_id,
        "source_document_id": doc["document_id"],
        "source_sha256": doc["sha256"],
        "evidence_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "source_id": doc["source_id"],
        "license": doc["license"],
        "rights_status": doc["rights_status"],
        "admission_status": "admitted",
        "train_eligible": True,
        "retrieval_eligible": False,
        "epistemic_type": doc["epistemic_type"],
        "domain": doc["domain"],
        "language": doc["language"],
        "split": doc["split"],
        "task_type": task_type,
        "synthetic": True,
        "text": text,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--documents", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--train-output", type=Path, required=True)
    parser.add_argument("--validation-output", type=Path, required=True)
    parser.add_argument("--max-copy-rows-per-document", type=int, default=2)
    args = parser.parse_args()
    train_rows, validation_rows = [], []
    counts = {"grounded_qa": 0, "extractive_copy": 0, "documents_seen": 0}
    with args.documents.open(encoding="utf-8") as stream:
        for line in stream:
            doc = json.loads(line)
            if doc.get("admission_status") != "admitted" or doc.get("train_eligible") is not True:
                continue
            counts["documents_seen"] += 1
            target = validation_rows if doc.get("split") == "validation" else train_rows
            source_path = (args.root / doc["path"]).resolve()
            qa_items = list(qa_rows(source_path)) if source_path.is_file() else []
            for idx, (question, answer, context) in enumerate(qa_items):
                prompt = f"### Contexto:\n[S1] {context}\n### Pregunta:\n{question}\n### Respuesta:"
                target.append(row_for(doc, "grounded_qa", prompt, answer + " [S1]", idx))
                counts["grounded_qa"] += 1
            if not any(row.get("source_document_id") == doc["document_id"] for row in target):
                for idx, sentence in enumerate(sentence_candidates(doc["text"])):
                    if idx >= args.max_copy_rows_per_document:
                        break
                    prompt = f"### Contexto:\n[S1] {sentence}\n### Instrucción:\nCopia literalmente la frase respaldada por la fuente.\n### Respuesta:"
                    target.append(row_for(doc, "extractive_copy", prompt, sentence + " [S1]", idx))
                    counts["extractive_copy"] += 1
    args.train_output.parent.mkdir(parents=True, exist_ok=True)
    args.validation_output.parent.mkdir(parents=True, exist_ok=True)
    for path, rows in ((args.train_output, train_rows), (args.validation_output, validation_rows)):
        with path.open("w", encoding="utf-8") as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps({
        **counts,
        "train_rows": len(train_rows),
        "validation_rows": len(validation_rows),
        "holdout_read": False,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
