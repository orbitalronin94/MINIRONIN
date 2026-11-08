#!/usr/bin/env python3
"""Build 500,000 unique Spanish cosmic-moral-technical QA pairs.

The generator is deterministic, dependency-free, streaming, and writes gzip JSONL.
Uniqueness is checked on the complete question and answer strings before publication.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

COSMIC = [
    "el firmamento", "la singularidad", "el vacío", "la nebulosa", "el horizonte",
    "el quásar", "la galaxia", "el cúmulo", "la supernova", "el pulsar",
    "la materia oscura", "la energía oscura", "el cosmos", "la bóveda celeste",
    "el agujero negro", "la estrella", "el cometa", "la constelación", "el éter",
    "la radiación cósmica", "el multiverso", "la inflación cósmica", "el espacio-tiempo",
    "la antimateria", "el polvo estelar", "la heliosfera", "el plasma", "la enana blanca",
    "la gigante roja", "el fondo cósmico", "la órbita", "el perihelio", "el afelio",
    "la magnetosfera", "el cinturón de Kuiper", "la nube de Oort", "el exoplaneta",
    "la luna errante", "el astro", "la esfera celeste", "la bóveda sideral",
    "el abismo gravitatorio", "la marea galáctica", "el disco de acreción",
    "la lente gravitacional", "el filamento cósmico", "la burbuja de Hubble",
    "el vacío cuántico", "la cuerda cósmica", "el relicto primordial",
    "la frontera observable", "el cenit", "el nadir", "la corona solar",
    "el viento estelar", "la nube molecular", "el vivero estelar", "el magnetar",
    "la estrella de neutrones", "el planeta errante", "la galaxia enana",
    "el supercúmulo", "la estructura a gran escala", "el pozo gravitatorio",
    "la métrica del espacio-tiempo",
]
PRONOUNS = ["yo", "tú", "él", "ella", "nosotros", "vosotros", "ellos", "ellas"]
MORALS = [
    "por honestidad", "por prudencia", "por justicia", "por humildad",
    "por lealtad", "por compasión", "por rigor", "por decencia",
    "por responsabilidad", "por templanza", "por respeto", "por integridad",
    "por valentía", "por ecuanimidad", "por benevolencia", "por dignidad",
    "por paciencia", "por transparencia", "por coherencia", "por solidaridad",
    "por imparcialidad", "por cautela", "por honor", "por misericordia",
]
NEGATIONS = [
    "no afirmo", "no sostengo", "no concedo", "no certifico", "no presupongo",
    "no proclamo", "no garantizo", "no confundo", "no equiparo", "no infiero",
    "no valido", "no postulo",
]
TECHNICAL = [
    "validez epistemológica", "causalidad", "isotropía", "entropía",
    "invariancia de escala", "convergencia asintótica", "identificabilidad",
    "consistencia bayesiana", "ergodicidad", "no linealidad", "simetría gauge",
    "correlación espuria", "regularización", "gradiente descendente",
    "distribución de probabilidad", "métrica tensorial", "tensor de Ricci",
    "función de onda", "decoherencia", "renormalización", "complejidad de Kolmogórov",
    "límite termodinámico", "sesgo de selección", "inferencia causal",
    "hipótesis nula", "significancia estadística", "entropía de Shannon",
    "divergencia KL", "sobreajuste", "subajuste", "normalización",
    "transformada de Fourier", "ecuación diferencial", "condición de contorno",
    "invariante topológico", "espacio de Hilbert", "operador hermítico",
    "amplitud de probabilidad", "principio variacional", "curvatura intrínseca",
    "tensor energía-momento", "horizonte de sucesos", "métrica de Minkowski",
    "principio de incertidumbre", "simetría espontánea", "campo escalar",
    "campo vectorial", "integral de camino", "funcional de partición",
    "modelo generativo", "cadena de Markov", "proceso estocástico",
    "estimador insesgado", "intervalo de confianza", "teorema ergódico",
    "complejidad computacional", "entropía cruzada", "atención multi-cabeza",
    "retropropagación", "descenso estocástico", "descomposición espectral",
    "autovalor dominante", "matriz jacobiana", "condicionamiento numérico",
    "estabilidad de Lyapunov", "exponente crítico", "transición de fase",
    "geometría diferencial", "topología algebraica", "homología persistente",
    "inferencia variacional", "campo de tensores", "ecuación de Einstein",
    "parámetro de orden", "ruptura de simetría", "principio holográfico",
    "densidad lagrangiana", "operador diferencial", "límite de Chernoff",
    "estimación de máxima verosimilitud", "proyección ortogonal",
    "desigualdad de Bell", "completitud de Turing", "decidibilidad",
    "gradiente de información", "divergencia de Wasserstein",
    "proceso de Poisson", "distribución de Boltzmann", "entrelazamiento cuántico",
    "deformación métrica", "invarianza conforme", "análisis dimensional",
    "regularidad Sobolev", "condición de Lipschitz", "teorema de Noether",
]
TOPICS = [
    "una promesa imposible", "un recuerdo reconstruido", "una predicción incierta",
    "un dilema de laboratorio", "una decisión automatizada", "una prueba incompleta",
    "una teoría elegante", "un dato contradictorio", "una simulación extrema",
    "una hipótesis seductora", "una conclusión precipitada", "un experimento fallido",
    "una correlación inesperada", "una paradoja moral", "una medición ruidosa",
    "un modelo diminuto", "una afirmación extraordinaria", "un resultado provisional",
    "una anomalía persistente", "un sistema complejo", "una evidencia parcial",
    "una explicación conveniente", "una frontera desconocida", "una inferencia frágil",
    "un consenso provisional", "una certeza heredada", "un cálculo aproximado",
    "una señal débil", "una observación aislada", "un patrón aparente",
    "una decisión irreversible", "una pregunta sin contexto", "una causalidad dudosa",
    "un argumento circular", "una métrica incompleta", "una verdad incómoda",
    "un mecanismo oculto", "una clasificación ambigua", "una regla universal",
    "una excepción estadística", "una teoría falsable", "un resultado reproducible",
    "un sesgo inadvertido", "una conclusión elegante", "un dato sintético",
    "una intuición persistente", "un límite físico", "una promesa tecnológica",
    "una demostración pendiente", "un supuesto tácito", "una contradicción formal",
    "un escenario hipotético", "una decisión prudencial", "un sistema emergente",
    "una señal contaminada", "un patrón aprendido", "un error de medición",
    "un razonamiento circular", "una analogía tentadora", "un resultado extremo",
    "una afirmación moral", "una predicción algorítmica", "una observación remota",
    "una evidencia indirecta", "una hipótesis auxiliar", "una certeza estadística",
    "una explicación teleológica", "un fenómeno no lineal", "una variable latente",
    "una prueba adversarial", "un supuesto cosmológico", "una medición indirecta",
    "una regla de decisión", "una inferencia bayesiana", "un sistema inestable",
    "un dato fuera de distribución", "una generalización apresurada",
    "un contraejemplo válido", "una solución aproximada", "un juicio precipitado",
    "una frontera matemática", "un modelo sobreajustado", "una paradoja aparente",
    "un cálculo reproducible", "un resultado no identificado", "una explicación causal",
    "una conclusión provisional", "un experimento mental", "un criterio de parada",
    "un teorema incompleto", "una anomalía cuántica", "una predicción falsable",
    "un argumento de autoridad", "una decisión bajo incertidumbre",
    "una observación sesgada", "una afirmación no contrastada",
]
PAUSES = ["…", "—", "… y aun así,", "— mas, en verdad,", "… empero,", "— llegado el caso,"]
QUESTION_FORMS = [
    "¿Qué responderías ante {topic} en {cosmic}?",
    "¿Cómo juzgarías {topic} cuando aparece {cosmic}?",
    "¿Qué dictamen darías sobre {topic} bajo {cosmic}?",
    "¿Cabe aceptar {topic} a la luz de {cosmic}?",
    "¿Qué dirías si {topic} se manifiesta junto a {cosmic}?",
    "¿Cómo abordarías {topic} desde la perspectiva de {cosmic}?",
    "¿Qué cautela merece {topic} frente a {cosmic}?",
    "¿Es legítimo concluir algo de {topic} ante {cosmic}?",
    "¿Qué postura adoptarías sobre {topic} contemplando {cosmic}?",
    "¿Cómo responder sin fingir certeza sobre {topic} y {cosmic}?",
]

def build_record(i: int) -> dict[str, str]:
    # Mixed-radix counters make each lexical tuple unique for the first 500k rows.
    x = i
    cosmic = COSMIC[x % len(COSMIC)]; x //= len(COSMIC)
    pronoun = PRONOUNS[x % len(PRONOUNS)]; x //= len(PRONOUNS)
    moral = MORALS[x % len(MORALS)]; x //= len(MORALS)
    negation = NEGATIONS[x % len(NEGATIONS)]; x //= len(NEGATIONS)
    technical = TECHNICAL[x % len(TECHNICAL)]
    # Independent mixed-radix dimensions diversify prompts without numeric IDs.
    q = i
    form = QUESTION_FORMS[q % len(QUESTION_FORMS)]; q //= len(QUESTION_FORMS)
    topic = TOPICS[q % len(TOPICS)]; q //= len(TOPICS)
    qcosmic = COSMIC[q % len(COSMIC)]; q //= len(COSMIC)
    q_moral = MORALS[q % len(MORALS)]; q //= len(MORALS)
    q_technical = TECHNICAL[q % len(TECHNICAL)]
    question = form.format(topic=f"{topic} ({q_moral}; {q_technical})", cosmic=qcosmic)
    pause = PAUSES[(i // 17) % len(PAUSES)]
    answer = f"{cosmic.capitalize()} {pause} {pronoun}, {moral}, {negation} {technical}."
    return {"question": question, "answer": answer}

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=500_000)
    parser.add_argument("--output", type=Path, default=Path("cosmic_moral_technical_500k.jsonl.gz"))
    args = parser.parse_args()
    if args.count < 1 or args.count > 500_000:
        raise SystemExit("--count must be between 1 and 500000")

    questions: set[str] = set()
    answers: set[str] = set()
    digest = hashlib.sha256()
    with gzip.open(args.output, "wt", encoding="utf-8", newline="\n", compresslevel=9) as out:
        for i in range(args.count):
            row = build_record(i)
            if row["question"] in questions:
                raise RuntimeError(f"duplicate question at row {i}")
            if row["answer"] in answers:
                raise RuntimeError(f"duplicate answer at row {i}")
            questions.add(row["question"])
            answers.add(row["answer"])
            line = json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
            out.write(line)
            digest.update(line.encode("utf-8"))

    if len(questions) != args.count or len(answers) != args.count:
        raise RuntimeError("uniqueness validation failed")
    report = {
        "dataset": args.output.name,
        "rows": args.count,
        "unique_questions": len(questions),
        "unique_answers": len(answers),
        "format": "JSONL gzip",
        "encoding": "UTF-8",
        "answer_pattern": "cosmic noun + dramatic pause + personal pronoun + moral value + negation + technical term",
        "sha256_uncompressed_jsonl": digest.hexdigest(),
        "synthetic": True,
        "warning": "Stylistic training data; not factual or reasoning supervision."
    }
    report_path = args.output.with_suffix(args.output.suffix + ".manifest.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
