#!/usr/bin/env python3
"""Create evidence-conditioned training rows from the canonical admitted inventory."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
from pathlib import Path


def sentence_candidates(text: str):
    for item in re.split(r"(?<=[.!?])\s+|\n+", text):
        item = re.sub(r"\s+", " ", item).strip()
        if 45 <= len(item) <= 500:
            yield item


def open_jsonl(path: Path):
    if path.name.lower().endswith(".jsonl.gz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    if path.suffix.lower() in {".jsonl", ".ndjson"}:
        return path.open(encoding="utf-8", errors="replace")
    return None


def verified_qa(record):
    question = record.get("question") or record.get("instruccion") or record.get("prompt")
    answer = record.get("answer") or record.get("respuesta") or record.get("target")
    context = record.get("context") or record.get("evidence") or record.get("evidencia")
    verified = (
        record.get("answer_verified") is True
        or record.get("curation_status") in {"verified", "manually_reviewed"}
        or record.get("curacion") in {"redactado_manual_desde_log", "revision_manual_aprobada"}
        or record.get("tag") in {"answerable_grounded", "identity_grounded", "identity_boundary", "unknown_abstain"}
    )
    if question and answer and context and verified:
        return str(question).strip(), str(answer).strip(), str(context).strip()
    return None


def record_text(record):
    preferred = (
        "text", "content", "body", "document", "passage", "abstract",
        "translation", "definition", "summary", "description", "explanation",
    )
    for key in preferred:
        value = record.get(key)
        if isinstance(value, str) and len(value.strip()) >= 45:
            return value.strip()
    return ""


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
    parser.add_argument("--max-copy-rows-per-record", type=int, default=1)
    parser.add_argument("--max-copy-rows-per-document", type=int, default=10000)
    parser.add_argument("--max-rows-total", type=int, default=100000)
    args = parser.parse_args()
    if min(args.max_copy_rows_per_record, args.max_copy_rows_per_document, args.max_rows_total) < 1:
        parser.error("Row limits must be positive")
    train_rows, validation_rows = [], []
    counts = {"grounded_qa": 0, "extractive_copy": 0, "documents_seen": 0, "records_seen": 0}
    with args.documents.open(encoding="utf-8") as stream:
        for line in stream:
            if len(train_rows) + len(validation_rows) >= args.max_rows_total:
                break
            doc = json.loads(line)
            if doc.get("admission_status") != "admitted" or doc.get("train_eligible") is not True:
                continue
            counts["documents_seen"] += 1
            target = validation_rows if doc.get("split") == "validation" else train_rows
            before = len(target)
            source_path = (args.root / doc.get("path", "")).resolve()
            jsonl_stream = open_jsonl(source_path) if source_path.is_file() else None
            if jsonl_stream is not None:
                with jsonl_stream:
                    for record_index, raw_line in enumerate(jsonl_stream):
                        if len(train_rows) + len(validation_rows) >= args.max_rows_total:
                            break
                        if not raw_line.strip().startswith("{"):
                            continue
                        try:
                            record = json.loads(raw_line)
                        except json.JSONDecodeError:
                            continue
                        counts["records_seen"] += 1
                        qa = verified_qa(record)
                        if qa:
                            question, answer, context = qa
                            prompt = f"### Contexto:\n[S1] {context}\n### Pregunta:\n{question}\n### Respuesta:"
                            target.append(row_for(doc, "grounded_qa", prompt, answer + " [S1]", record_index))
                            counts["grounded_qa"] += 1
                            continue
                        source_text = record_text(record)
                        if not source_text:
                            continue
                        for local_index, sentence in enumerate(sentence_candidates(source_text)):
                            if local_index >= args.max_copy_rows_per_record:
                                break
                            if len(target) - before >= args.max_copy_rows_per_document:
                                break
                            prompt = f"### Contexto:\n[S1] {sentence}\n### Instrucción:\nCopia literalmente la frase respaldada por la fuente.\n### Respuesta:"
                            target.append(row_for(doc, "extractive_copy", prompt, sentence + " [S1]",
                                                  record_index * args.max_copy_rows_per_record + local_index))
                            counts["extractive_copy"] += 1
            else:
                for idx, sentence in enumerate(sentence_candidates(doc.get("text", ""))):
                    if idx >= min(args.max_copy_rows_per_document, 2):
                        break
                    prompt = f"### Contexto:\n[S1] {sentence}\n### Instrucción:\nCopia literalmente la frase respaldada por la fuente.\n### Respuesta:"
                    target.append(row_for(doc, "extractive_copy", prompt, sentence + " [S1]", idx))
                    counts["extractive_copy"] += 1
            if len(train_rows) + len(validation_rows) >= args.max_rows_total:
                break
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
