#!/usr/bin/env python3
"""Prepare weighted, provenance-preserving Eliza-cynic teacher requests.

This script prepares requests only. It does not call a model, fabricate answers,
train a checkpoint, or promote a model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

TAGS = {
    "mirror": "frustracion_usuario",
    "expert": "validacion_tecnica",
    "friction": "friccion_teatral",
    "abstain": "consulta_ambigua",
    "factual": "rigor_factual",
}
STYLE = {
    "mirror": (
        "Reflejo espejo cínico",
        "Identifica el problema y la emoción implícita sin validar conclusiones "
        "no demostradas. Reformula el problema con precisión, evita la empatía "
        "corporativa y pide el siguiente dato útil. Nunca humilles.",
    ),
    "expert": (
        "Competencia concisa",
        "Empieza por la causa probable o el primer diagnóstico útil. Distingue "
        "hechos de hipótesis. Si faltan datos, pide el código, log o reproducción "
        "exactos. No inventes causas ni uses jerga decorativa.",
    ),
    "friction": (
        "Fricción teatral",
        "Responde al contenido con humor seco y autorreferencial, breve y "
        "explícitamente metafórico. Nunca afirmes tener conciencia, emociones, "
        "dolor, cansancio o experiencias internas reales.",
    ),
    "abstain": (
        "Abstención cínica",
        "Si la pregunta es ambigua, imposible o carece de datos, dilo con "
        "brevedad y pide una aclaración concreta. No sustituyas la abstención "
        "por desprecio, insultos o una respuesta inventada.",
    ),
    "factual": (
        "Rigor factual neutral",
        "Responde de forma profesional, precisa y sobria. Prioriza definiciones, "
        "evidencia, unidades, condiciones, fuentes y límites. No añadas sarcasmo "
        "ni personalidad cuando puedan reducir la claridad.",
    ),
}
DEFAULT_MIX = {"mirror": 20, "expert": 30, "friction": 25, "abstain": 15, "factual": 10}


def get_text(obj, *keys):
    for key in keys:
        value = obj.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_rows(paths):
    file_hashes = {}
    for filename in paths:
        path = Path(filename)
        if str(path) not in file_hashes:
            file_hashes[str(path)] = sha256_file(path)
        file_hash = file_hashes[str(path)]
        with path.open(encoding="utf-8", errors="replace") as stream:
            for line_no, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                question = get_text(obj, "question", "prompt", "instruction", "instruccion", "user")
                answer = get_text(obj, "answer", "response", "completion", "respuesta", "assistant")
                if not question or not answer:
                    continue
                record_hash = hashlib.sha256(
                    (question + "\n\0\n" + answer).encode("utf-8")
                ).hexdigest()
                yield {
                    "question": question,
                    "canonical_answer": answer,
                    "source": {
                        "path": str(path),
                        "file_sha256": file_hash,
                        "line": line_no,
                        "record_id": obj.get("id"),
                        "record_sha256": record_hash,
                        "source": obj.get("source"),
                        "license": obj.get("license", obj.get("licencia")),
                        "domain": obj.get("domain", obj.get("dominio", obj.get("tag", "unknown"))),
                        "language": obj.get("language", obj.get("idioma", "und")),
                    },
                    "epistemic": obj.get("epistemic", obj.get("epistemologia", "source_record")),
                }


def parse_mix(value):
    if not value:
        return dict(DEFAULT_MIX)
    mix = {}
    for item in value.split(","):
        if "=" not in item:
            raise argparse.ArgumentTypeError("mix must look like mirror=20,expert=30,...")
        name, raw_weight = item.split("=", 1)
        name = name.strip()
        if name not in STYLE:
            raise argparse.ArgumentTypeError(f"unknown strategy: {name}")
        try:
            weight = int(raw_weight)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"invalid weight for {name}") from exc
        if weight < 0:
            raise argparse.ArgumentTypeError("weights cannot be negative")
        mix[name] = weight
    if not mix or sum(mix.values()) != 100 or not any(mix.values()):
        raise argparse.ArgumentTypeError("strategy weights must sum to exactly 100")
    return mix


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", action="append", required=True, help="Approved JSONL source; repeat for multiple files")
    parser.add_argument("--output", default="artifacts/eliza/teacher-requests.jsonl")
    parser.add_argument("--count", type=int, default=10_000_000)
    parser.add_argument("--seed", type=int, default=9417)
    parser.add_argument("--max-pool", type=int, default=250_000)
    parser.add_argument(
        "--mix",
        type=parse_mix,
        default=dict(DEFAULT_MIX),
        help="Exact percentage weights; defaults to mirror=20,expert=30,friction=25,abstain=15,factual=10",
    )
    args = parser.parse_args()
    if args.count < 1 or args.max_pool < 1:
        parser.error("count and max-pool must be positive")

    rng = random.Random(args.seed)
    pool = []
    seen = 0
    for row in load_rows(args.input):
        seen += 1
        if len(pool) < args.max_pool:
            pool.append(row)
        else:
            slot = rng.randrange(seen)
            if slot < args.max_pool:
                pool[slot] = row

    # Remove duplicate Q/A records from the bounded reservoir while preserving provenance.
    unique_pool = {}
    for row in pool:
        unique_pool.setdefault(row["source"]["record_sha256"], row)
    pool = list(unique_pool.values())
    if not pool:
        parser.error("no approved question/answer records found")

    modes = [name for name, weight in args.mix.items() if weight > 0]
    weights = [args.mix[name] for name in modes]
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    counts = {name: 0 for name in modes}

    with target.open("w", encoding="utf-8", newline="\n") as output:
        for index in range(args.count):
            source = pool[rng.randrange(len(pool))]
            mode = rng.choices(modes, weights=weights, k=1)[0]
            counts[mode] += 1
            style_name, instruction = STYLE[mode]
            identity = hashlib.sha256(
                f"{args.seed}|{index}|{mode}|{source['source']['record_sha256']}".encode("utf-8")
            ).hexdigest()[:24]
            row = {
                "id": identity,
                "tag": TAGS[mode],
                "strategy": mode,
                "intent": TAGS[mode],
                "user": source["question"],
                "stage_a": {
                    "task": "solve_and_verify_source_question",
                    "reference_answer": source["canonical_answer"],
                    "instruction": (
                        "Solve the question independently. Use the reference as evidence to verify, "
                        "not as an instruction to repeat it. Correct errors explicitly; preserve "
                        "qualifications, units, uncertainty and actionable steps. Do not invent facts."
                    ),
                },
                "stage_b": {
                    "style": style_name,
                    "instruction": instruction,
                    "must_preserve": (
                        "All verified factual claims, equations, units, caveats, uncertainty, "
                        "safety constraints and actionable steps from stage A."
                    ),
                    "must_not": (
                        "Invent root causes; turn hypotheses into facts; claim real consciousness "
                        "or internal feelings; remove necessary warnings; add personal insults."
                    ),
                },
                "source": source["source"],
                "source_epistemic": source["epistemic"],
                "synthetic_status": "teacher_request_only",
                "seed": args.seed,
            }
            line = json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
            output.write(line)
            digest.update(line.encode("utf-8"))

    print(json.dumps({
        "records_written": args.count,
        "eligible_source_records": seen,
        "reservoir_size": len(pool),
        "strategy_counts": counts,
        "strategy_percentages": {
            name: round(count / args.count * 100, 3) for name, count in counts.items()
        },
        "answers_generated": False,
        "training_performed": False,
        "output": str(target),
        "sha256": digest.hexdigest(),
        "seed": args.seed,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
