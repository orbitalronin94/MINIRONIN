#!/usr/bin/env python3
"""Continue the verified 1,000-step MINIRONIN Mamba checkpoint for 1,000 more steps."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sqlite3
import time
from collections import Counter, defaultdict
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from minironin.mamba import MambaRoninLM
from train_long_run import load_training_data
from train_seed_tournament import MIX_WEIGHTS, evaluate, weighted_domains

EXPECTED_START_SHA = "d4e94c6b2711810bc07ce91b9fdcf4cfd50466a6ee9eafe70b64f023f211d5d7"
EXPECTED_PARENT_SHA = "bfe4959e7b51a42eb6e14543a5d6d6b4c2d0dce443ed4944d509f20c83acc730"
EXPECTED_PARAMETERS = 49_083_392
ACTIVE_VOCAB = 257
EOS_ID = 256
BATCH_SIZE = 1
SEQUENCE_LENGTH = 64
START_STEP = 1000
RAG_TRAIN_SOURCES = {"minironin-papers", "RONIN_IA"}
REQUIRED_DOMAINS = {
    "math", "science", "books", "behavior", "abstention", "abstain_plain",
    "abstain_literary", "abstain_koan", "aristocrat", "casuist", "scientist",
    "oracle", "indifference", "lexicon",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_domain(source_id: str, declared_domain: str, metadata: dict, relative_path: str) -> str:
    candidates = [
        metadata.get("domain"), metadata.get("dominio"), metadata.get("tag"),
        metadata.get("category"), metadata.get("categoria"), metadata.get("topic"),
        metadata.get("subject"), metadata.get("area"), metadata.get("materia"),
        declared_domain, relative_path,
    ]
    value = " ".join(str(item).lower() for item in candidates if item is not None)
    exact = {str(item).strip().lower() for item in candidates if item is not None}
    for domain in MIX_WEIGHTS:
        if domain in exact:
            return domain
    if any(term in value for term in ("abstain_koan", "abstencion_koan", "koan")):
        return "abstain_koan"
    if any(term in value for term in ("abstain_literary", "abstencion_literaria", "literary_abstain")):
        return "abstain_literary"
    if any(term in value for term in ("abstain_plain", "abstencion_simple", "plain_abstain")):
        return "abstain_plain"
    if "aristocrat" in value or "aristocr" in value:
        return "aristocrat"
    if "casuist" in value or "casu" in value:
        return "casuist"
    if "scientist" in value or "cientific" in value:
        return "scientist"
    if "oracle" in value or "orac" in value:
        return "oracle"
    if "indifference" in value or "indifer" in value:
        return "indifference"
    if "lexicon" in value or "lexico" in value:
        return "lexicon"
    if "abstain" in value or "abstencion" in value:
        return "abstention"
    if any(term in value for term in ("math", "matematic", "algebra", "arithmetic")):
        return "math"
    if any(term in value for term in ("science", "ciencia", "physics", "chemistry", "biology", "research", "paper")):
        return "science"
    if any(term in value for term in ("book", "literature", "literatura", "prodatphil")):
        return "books"
    if any(term in value for term in ("behavior", "conducta", "personality", "personalidad")):
        return "behavior"
    if source_id == "minironin-papers":
        return "science"
    return "general"


def load_rag_training_docs(index_path: Path):
    """Load only additional train-admitted RAG libraries; never rights metadata or holdout."""
    db = sqlite3.connect(index_path)
    db.row_factory = sqlite3.Row
    try:
        row = db.execute("SELECT value FROM metadata WHERE key='manifest'").fetchone()
        if row is None:
            raise SystemExit("RAG index has no manifest")
        manifest = json.loads(row["value"])
        if manifest.get("holdout_read") is not False:
            raise SystemExit("RAG manifest does not explicitly certify holdout_read=false")
        declared_sources = {item.get("id"): item for item in manifest.get("sources", [])}
        missing = sorted(RAG_TRAIN_SOURCES - set(declared_sources))
        if missing:
            raise SystemExit("RAG index is missing required train libraries: " + ", ".join(missing))
        for source_id in RAG_TRAIN_SOURCES:
            if not declared_sources[source_id].get("exists"):
                raise SystemExit(f"RAG source root was not present: {source_id}")

        sql = """
            SELECT cs.document_id AS document_id,c.text,c.text_sha256,
                   cs.source_id,cs.relative_path,cs.locator,cs.record_metadata,
                   d.domain,d.license,d.epistemic
            FROM chunks c
            JOIN chunk_sources cs ON cs.chunk_id=c.chunk_id
            JOIN document_sources d
              ON d.document_id=cs.document_id AND d.source_id=cs.source_id
            WHERE cs.source_id IN (?,?)
            ORDER BY cs.source_id,cs.relative_path,cs.locator,c.chunk_id
        """
        rows = db.execute(sql, tuple(sorted(RAG_TRAIN_SOURCES)))
        docs, seen, counts, split_counts = [], set(), Counter(), Counter()
        for item in rows:
            text = item["text"].strip()
            if len(text) < 200:
                continue
            source_id = item["source_id"]
            metadata = json.loads(item["record_metadata"] or "{}")
            domain = normalize_domain(source_id, item["domain"] or "", metadata, item["relative_path"] or "")
            digest = hashlib.sha256((domain + "\0" + text).encode("utf-8")).hexdigest()
            if digest in seen:
                continue
            seen.add(digest)
            doc_key = source_id + "\0" + str(item["document_id"])
            # Stable document-level split; chunks from one source document never cross splits.
            validation = int(hashlib.sha256(doc_key.encode("utf-8")).hexdigest()[:8], 16) % 10 == 0
            docs.append({
                "domain": domain,
                "text": text,
                "source": source_id,
                "source_file": item["relative_path"],
                "sha256": digest,
                "document_key": doc_key,
                "split": "validation" if validation else "train",
                "license": item["license"],
                "epistemic": item["epistemic"],
                "locator": item["locator"],
            })
            counts[source_id] += 1
            split_counts[(source_id, "validation" if validation else "train")] += 1
        if not docs:
            raise SystemExit("No trainable chunks found in the approved RAG libraries")
        missing_sources = sorted(source for source in RAG_TRAIN_SOURCES if not counts[source])
        if missing_sources:
            raise SystemExit("No usable chunks from RAG libraries: " + ", ".join(missing_sources))
        summary = {
            "index_sha256": sha256_file(index_path),
            "manifest": manifest,
            "included_sources": sorted(RAG_TRAIN_SOURCES),
            "excluded_sources": ["minironin-curated (already loaded from canonical curated JSONL)",
                                "minironin-books (no acquired trainable works declared in SOURCES.jsonl)",
                                "RONIN_IA_RIGHTS (rights metadata is never training text)"],
            "chunks_by_source": dict(counts),
            "split_by_source": {
                f"{source}:{split}": count
                for (source, split), count in sorted(split_counts.items())
            },
            "chunks_total": len(docs),
        }
        return docs, summary
    finally:
        db.close()


def add_rag_docs(train_docs, validation, rag_docs):
    """Merge RAG chunks into the existing 15-domain corpus with document-disjoint validation."""
    # Validation contains prebuilt tensors, not document dictionaries.
    known = {
        doc.get("sha256")
        for rows in train_docs.values()
        for doc in rows
        if doc.get("sha256")
    }
    validation_docs = defaultdict(list)
    added_train, added_validation = Counter(), Counter()
    for doc in rag_docs:
        if doc["sha256"] in known:
            continue
        known.add(doc["sha256"])
        target = validation_docs if doc["split"] == "validation" else train_docs
        target.setdefault(doc["domain"], []).append(doc)
        if doc["split"] == "validation":
            added_validation[doc["domain"]] += 1
        else:
            added_train[doc["domain"]] += 1

    rng = random.Random(31415927)
    eval_length = 128
    for domain, docs in validation_docs.items():
        eligible = []
        for doc in docs:
            tokens = list(doc["text"].encode("utf-8", errors="replace")) + [EOS_ID]
            if len(tokens) >= eval_length + 1:
                eligible.append(tokens)
        if not eligible:
            continue
        batches = []
        for _ in range(4):
            tokens = rng.choice(eligible)
            offset = rng.randrange(0, len(tokens) - eval_length)
            batches.append(torch.tensor([tokens[offset:offset + eval_length + 1]], dtype=torch.long))
        validation[domain].extend(batches)

    return {
        "added_train_chunks_by_domain": dict(added_train),
        "added_validation_chunks_by_domain": dict(added_validation),
        "added_train_chunks": sum(added_train.values()),
        "added_validation_chunks": sum(added_validation.values()),
    }


def make_batch(train_docs, names, probabilities, rng):
    domains = rng.choices(names, weights=probabilities, k=BATCH_SIZE)
    rows = []
    for domain in domains:
        raw = list(rng.choice(train_docs[domain])["text"].encode("utf-8", errors="replace")) + [EOS_ID]
        if len(raw) < SEQUENCE_LENGTH + 1:
            raise ValueError("Training document shorter than sequence window: " + domain)
        start = rng.randrange(0, len(raw) - SEQUENCE_LENGTH)
        rows.append(torch.tensor(raw[start:start + SEQUENCE_LENGTH + 1], dtype=torch.long))
    return torch.stack(rows), domains


def save_checkpoint(path, model, completed_steps, start_sha, original_parent_sha, metrics, manifest):
    payload = {
        "architecture": "mamba-selective-scan-v1",
        "model_config": model.config,
        "model_state_dict": model.state_dict(),
        "completed_steps": completed_steps,
        "parameter_count": model.parameter_count(),
        "active_vocabulary": ACTIVE_VOCAB,
        "tokenization": "UTF-8 bytes + EOS",
        "parent_checkpoint_sha256": original_parent_sha,
        "training_parent_checkpoint_sha256": start_sha,
        "training_steps_added": completed_steps - START_STEP,
        "training_metrics": metrics,
        "dataset_manifest": manifest,
        "candidate_only": True,
    }
    torch.save(payload, path)
    digest = sha256_file(path)
    print(json.dumps({
        "checkpoint": str(path), "completed_steps": completed_steps,
        "sha256": digest, "bytes": path.stat().st_size,
    }), flush=True)
    return digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-checkpoint", required=True, type=Path)
    parser.add_argument("--rag-index", required=True, type=Path)
    parser.add_argument("--heretic-root", required=True, type=Path)
    parser.add_argument("--books-root", required=True, type=Path)
    parser.add_argument("--dataset-cache", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("mamba-50m-continuation/results"))
    parser.add_argument("--steps", type=int, default=1000)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    args = parser.parse_args()

    if args.steps != 1000:
        parser.error("This workflow is intentionally fixed to exactly 1,000 additional steps")
    if args.learning_rate <= 0 or args.threads < 1:
        parser.error("learning-rate and threads must be positive")

    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(20261109)
    random.seed(20261109)

    start_sha = sha256_file(args.input_checkpoint)
    if start_sha != EXPECTED_START_SHA:
        raise SystemExit(f"Refusing wrong starting checkpoint SHA-256: {start_sha}")
    checkpoint = torch.load(args.input_checkpoint, map_location="cpu", weights_only=False)
    if checkpoint.get("architecture") != "mamba-selective-scan-v1":
        raise SystemExit("Starting checkpoint is not the expected Mamba architecture")
    if checkpoint.get("completed_steps") != START_STEP:
        raise SystemExit("Starting checkpoint must be exactly the 1,000-step Mamba candidate")
    if checkpoint.get("parameter_count") != EXPECTED_PARAMETERS:
        raise SystemExit("Starting checkpoint parameter count mismatch")
    if checkpoint.get("parent_checkpoint_sha256") != EXPECTED_PARENT_SHA:
        raise SystemExit("Starting checkpoint's verified 390k parent SHA mismatch")
    if checkpoint.get("active_vocabulary") != ACTIVE_VOCAB:
        raise SystemExit("Starting checkpoint active vocabulary mismatch")

    config = dict(checkpoint["model_config"])
    config.pop("architecture", None)
    model = MambaRoninLM(**config).cpu()
    if model.parameter_count() != EXPECTED_PARAMETERS:
        raise SystemExit("Instantiated Mamba parameter count mismatch")
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    model.eval()

    print("LOADING_EXISTING_FULL_CORPUS", flush=True)
    train_docs, names, probabilities, validation, base_manifest = load_training_data(
        args.heretic_root, args.books_root, args.dataset_cache
    )
    missing = sorted(REQUIRED_DOMAINS - set(names))
    if missing:
        raise SystemExit("Existing corpus missing required domains: " + ", ".join(missing))

    rag_docs, rag_manifest = load_rag_training_docs(args.rag_index)
    rag_added = add_rag_docs(train_docs, validation, rag_docs)
    names, probabilities = weighted_domains(train_docs)
    missing = sorted(REQUIRED_DOMAINS - set(names))
    if missing:
        raise SystemExit("Merged corpus missing required domains: " + ", ".join(missing))

    manifest = {
        "experiment": "Mamba 50M continuation from exact 1,000-step checkpoint",
        "base_corpus": base_manifest,
        "rag_libraries": rag_manifest,
        "rag_merge": rag_added,
        "training_domains": names,
        "domain_sampling_weights": dict(zip(names, probabilities)),
        "documents_by_domain_after_rag": {domain: len(train_docs.get(domain, [])) for domain in names},
        "validation_batches_by_domain": {domain: len(validation.get(domain, [])) for domain in sorted(validation)},
        "holdout_excluded": True,
        "rights_registry_excluded": True,
        "curated_data_policy": "canonical generated curated JSONL loaded once; duplicate RAG curated source excluded",
        "optimizer_policy": "AdamW state reset; the 1,000-step checkpoint contains model weights but no optimizer state",
        "learning_rate_max": args.learning_rate,
        "additional_steps": args.steps,
        "batch_size": BATCH_SIZE,
        "sequence_length": SEQUENCE_LENGTH,
        "seed": 20261109,
        "start_checkpoint_sha256": start_sha,
    }
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    (output / "continuation-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    baseline_loss, baseline_domains = evaluate(model, validation, torch.device("cpu"))
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=args.learning_rate,
        betas=(0.9, 0.95), weight_decay=0.01,
    )
    rng = random.Random(20261109)
    losses = []
    started = time.perf_counter()
    model.train()

    for local_step in range(1, args.steps + 1):
        progress = local_step / args.steps
        warmup = min(1.0, local_step / 50.0)
        cosine = 0.5 * (1.0 + __import__("math").cos(__import__("math").pi * progress))
        lr = args.learning_rate * warmup * (0.1 + 0.9 * cosine)
        for group in optimizer.param_groups:
            group["lr"] = lr
        batch, sampled_domains = make_batch(train_docs, names, probabilities, rng)
        optimizer.zero_grad(set_to_none=True)
        _, loss = model(batch, labels=batch, vocab_limit=ACTIVE_VOCAB)
        if not torch.isfinite(loss):
            raise SystemExit(f"Non-finite loss at continuation step {local_step}")
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        losses.append(float(loss.detach()))

        global_step = START_STEP + local_step
        if local_step % 50 == 0 or local_step == 1:
            print(json.dumps({
                "completed_steps": global_step,
                "additional_steps": local_step,
                "loss": losses[-1],
                "mean_loss_last_50": sum(losses[-50:]) / len(losses[-50:]),
                "learning_rate": lr,
                "sampled_domains": sampled_domains,
                "elapsed_seconds": round(time.perf_counter() - started, 2),
            }), flush=True)

        if local_step % 250 == 0 and local_step < args.steps:
            model.eval()
            val_loss, val_domains = evaluate(model, validation, torch.device("cpu"))
            metrics = {
                "validation_loss": val_loss,
                "validation_by_domain": val_domains,
                "train_loss_last_50": sum(losses[-50:]) / len(losses[-50:]),
                "elapsed_seconds": round(time.perf_counter() - started, 2),
            }
            save_checkpoint(
                output / f"mamba-checkpoint-{global_step}.pt",
                model, global_step, start_sha, EXPECTED_PARENT_SHA, metrics, manifest,
            )
            (output / f"metrics-{global_step}.json").write_text(
                json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            model.train()

    model.eval()
    final_loss, final_domains = evaluate(model, validation, torch.device("cpu"))
    final_checkpoint = output / "mamba-checkpoint-2000.pt"
    final_metrics = {
        "baseline_validation_loss_before_continuation": baseline_loss,
        "baseline_validation_by_domain": baseline_domains,
        "final_validation_loss": final_loss,
        "final_validation_by_domain": final_domains,
        "train_loss_first_50": sum(losses[:50]) / min(50, len(losses)),
        "train_loss_last_50": sum(losses[-50:]) / min(50, len(losses)),
        "elapsed_seconds": round(time.perf_counter() - started, 2),
    }
    final_sha = save_checkpoint(
        final_checkpoint, model, START_STEP + args.steps,
        start_sha, EXPECTED_PARENT_SHA, final_metrics, manifest,
    )
    report = {
        "status": "completed",
        "architecture": "mamba-selective-scan-v1",
        "parameter_count": model.parameter_count(),
        "starting_steps": START_STEP,
        "completed_steps": START_STEP + args.steps,
        "additional_steps": args.steps,
        "starting_checkpoint_sha256": start_sha,
        "final_checkpoint_sha256": final_sha,
        "rag_index_sha256": rag_manifest["index_sha256"],
        "rag_chunks_added": rag_added,
        "validation": final_metrics,
        "promotion": "NOT_PROMOTED — independent holdout review required",
    }
    (output / "final-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
