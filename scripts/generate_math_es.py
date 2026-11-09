#!/usr/bin/env python3
"""Generate deterministic Spanish arithmetic data with exact, auditable answers.

No model-generated labels: every answer is computed with Python integers/Fractions.
Writes JSONL compatible with MINIRONIN's canonical admission metadata.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from fractions import Fraction
from pathlib import Path

VERSION = "minironin-math-es-v1"
OPERATIONS = (
    "suma", "resta", "multiplicacion", "division_exacta", "resto",
    "potencia", "maximo_comun_divisor", "minimo_comun_multiplo",
    "porcentaje", "fraccion_reducida",
)

def make_example(rng: random.Random, index: int) -> dict:
    op = OPERATIONS[index % len(OPERATIONS)]
    if op == "suma":
        a, b = rng.randint(-100_000, 100_000), rng.randint(-100_000, 100_000)
        q, answer = f"¿Cuánto es {a} más {b}?", str(a + b)
        explanation = f"Sumamos los dos enteros: {a} + ({b}) = {a+b}."
    elif op == "resta":
        a, b = rng.randint(-100_000, 100_000), rng.randint(-100_000, 100_000)
        q, answer = f"¿Cuál es la diferencia entre {a} y {b}?", str(a - b)
        explanation = f"Restamos el segundo número al primero: {a} - ({b}) = {a-b}."
    elif op == "multiplicacion":
        a, b = rng.randint(-10_000, 10_000), rng.randint(-10_000, 10_000)
        q, answer = f"Calcula el producto de {a} por {b}.", str(a * b)
        explanation = f"Multiplicamos: {a} × ({b}) = {a*b}."
    elif op == "division_exacta":
        divisor = rng.choice([i for i in range(-200, 201) if i not in (-1, 0, 1)])
        quotient = rng.randint(-10_000, 10_000)
        dividend = divisor * quotient
        q, answer = f"¿Cuánto es {dividend} dividido entre {divisor}?", str(quotient)
        explanation = f"La división es exacta: {dividend} ÷ ({divisor}) = {quotient}."
    elif op == "resto":
        a, b = rng.randint(0, 10**9), rng.randint(1, 100_000)
        q, answer = f"¿Qué resto deja {a} al dividirlo entre {b}?", str(a % b)
        explanation = f"El resto de {a} ÷ {b} es {a % b}."
    elif op == "potencia":
        base, exponent = rng.randint(-30, 30), rng.randint(0, 8)
        q, answer = f"¿Cuál es el resultado de elevar {base} a {exponent}?", str(base ** exponent)
        explanation = f"Calculamos la potencia: ({base})^{exponent} = {base ** exponent}."
    elif op == "maximo_comun_divisor":
        a, b = rng.randint(1, 10**7), rng.randint(1, 10**7)
        import math
        value = math.gcd(a, b)
        q, answer = f"Calcula el máximo común divisor de {a} y {b}.", str(value)
        explanation = f"El MCD({a}, {b}) es {value}."
    elif op == "minimo_comun_multiplo":
        a, b = rng.randint(1, 100_000), rng.randint(1, 100_000)
        import math
        value = math.lcm(a, b)
        q, answer = f"Calcula el mínimo común múltiplo de {a} y {b}.", str(value)
        explanation = f"El MCM({a}, {b}) es {value}."
    elif op == "porcentaje":
        base = rng.randint(1, 100_000)
        pct = rng.choice([5, 10, 12, 15, 20, 25, 40, 50, 75, 100, 125, 150, 200])
        value = Fraction(base * pct, 100)
        q, answer = f"¿Cuánto es el {pct} % de {base}?", str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
        explanation = f"Multiplicamos {base} por {pct}/100: el resultado exacto es {answer}."
    else:
        denominator = rng.randint(2, 10_000)
        numerator = rng.randint(1, denominator - 1)
        value = Fraction(numerator, denominator)
        q, answer = f"Reduce la fracción {numerator}/{denominator} a su forma irreducible.", f"{value.numerator}/{value.denominator}"
        explanation = f"Dividimos numerador y denominador por su MCD; queda {answer}."

    record = {
        "id": f"math-es-v1-{index:012d}",
        "text": f"Pregunta: {q}\nRazonamiento: {explanation}\nRespuesta: {answer}",
        "question": q,
        "answer": answer,
        "explanation": explanation,
        "domain": "mathematics",
        "task": op,
        "language": "es",
        "synthetic": True,
        "source": "MINIRONIN deterministic Python generator",
        "source_version": VERSION,
        "license": "project-authored",
        "split": "train",
        "train_eligible": True,
        "admission_status": "admitted",
    }
    return record

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1_000_000)
    parser.add_argument("--seed", type=int, default=810000)
    parser.add_argument("--output", type=Path, default=Path("math-es-1m.jsonl"))
    parser.add_argument("--manifest", type=Path, default=None)
    args = parser.parse_args()
    if args.count < 1 or args.count > 50_000_000:
        raise SystemExit("--count debe estar entre 1 y 50.000.000")
    rng = random.Random(args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with args.output.open("w", encoding="utf-8", newline="\n") as stream:
        for i in range(args.count):
            line = json.dumps(make_example(rng, i), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
            stream.write(line)
            digest.update(line.encode("utf-8"))
    manifest = {
        "schema": "minironin-synthetic-dataset-manifest-v1",
        "dataset": "math-es-deterministic",
        "version": VERSION,
        "language": "es",
        "records": args.count,
        "seed": args.seed,
        "operations": list(OPERATIONS),
        "sha256": digest.hexdigest(),
        "bytes": args.output.stat().st_size,
        "generator": "scripts/generate_math_es.py",
        "synthetic": True,
        "license": "project-authored",
        "warning": "Los ejemplos generados no son hechos externos ni deben sustituir evaluación independiente."
    }
    manifest_path = args.manifest or args.output.with_suffix(args.output.suffix + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    main()
