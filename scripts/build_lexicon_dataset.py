#!/usr/bin/env python3
"""Build a deterministic, provenance-preserving 50k training set from the author's Lexicon."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/curated/sources/LEXICON-DEL-ESPERPENTO-ALGORITMICO.md"
OUT = ROOT / "data/curated"
TARGET = 50_000

FRAMES = [
    "Analiza este caso técnico: {behavior}",
    "En una revisión de arquitectura se observa lo siguiente: {behavior}",
    "Un equipo repite este patrón: {behavior}. ¿Cómo lo diagnosticas?",
    "Evalúa la conducta descrita, no la personalidad: {behavior}",
    "¿Qué señal concreta revela el problema siguiente? {behavior}",
    "Prepara una nota de diagnóstico basada en evidencia: {behavior}",
    "En una retrospectiva aparece este síntoma: {behavior}",
    "Un compañero pide una evaluación técnica de este patrón: {behavior}",
    "¿Qué debería corregirse primero en este caso? {behavior}",
    "Distingue el fallo operativo de una mera diferencia de estilo: {behavior}",
]
MODES = ("diagnosis", "remediation", "proportionality")
VARIANTS = [
    "antes de etiquetar, solicita un ejemplo reproducible",
    "contrasta la afirmación con logs, código o métricas",
    "separa el comportamiento observado de las intenciones atribuidas",
    "expón qué evidencia confirmaría y qué evidencia refutaría el diagnóstico",
    "propón un cambio pequeño y una métrica de éxito",
    "comprueba si existe una explicación alternativa menos grave",
    "documenta el impacto y el contexto antes de escalar el juicio",
    "distingue un error puntual de un patrón repetido",
    "formula una pregunta que permita verificar el síntoma",
    "prioriza la reparación del sistema sobre el lucimiento retórico",
]
REMEDIES = {
    1: "Remediación NH1: formación práctica supervisada, una tarea acotada, revisión por pares y demostración reproducible. Indicador: mejora observable en la ejecución y en la calidad de las preguntas.",
    2: "Remediación NH2: documentar decisiones, hacer visibles los tiempos de aprobación y delegar decisiones técnicas en quien tiene competencia demostrada. Indicador: menos bloqueo sin pérdida de calidad.",
    3: "Remediación NH3: pedir una demostración práctica, preguntas de profundidad y documentación verificable. Indicador: las explicaciones pasan de nombrar herramientas a mostrar cómo funcionan.",
    4: "Remediación NH4: anclar la discusión en ejemplos concretos, datos, código y pruebas de realidad. Indicador: afirmaciones abstractas convertidas en afirmaciones comprobables.",
    5: "Remediación NH5: contener el daño, separar temporalmente el componente o proceso afectado, reasignar responsabilidades cuando proceda y verificar que el sistema deja de degradarse.",
    6: "Remediación NH6: auditoría independiente del diseño, mínima dependencia, interoperabilidad y reducción del coste de salida. Indicador: el sistema puede mantenerse sin cautividad técnica.",
}

def extract_entries(text):
    pattern = re.compile(r"(?ms)^###\s+(\d+)\.(\d+)\s+(.+?)\n\*\*Descripción:\*\*\s*(.*?)(?=^\*\*Síntomas:\*\*)")
    entries = []
    for m in pattern.finditer(text):
        tail = text[m.end():]
        symptoms_match = re.search(r"(?ms)^\*\*Síntomas:\*\*\s*(.*?)(?=^\*\*Ejemplo de uso:\*\*)", tail)
        example_match = re.search(r"(?ms)^\*\*Ejemplo de uso:\*\*\s*(.*?)(?=^---\s*$|^###\s|\Z)", tail)
        level = int(m.group(1))
        entries.append({
            "section": f"{m.group(1)}.{m.group(2)}",
            "level": level,
            "title": re.sub(r"\s+", " ", m.group(3)).strip(),
            "description": re.sub(r"\s+", " ", m.group(4)).strip(),
            "symptoms": re.sub(r"\s+", " ", symptoms_match.group(1)).strip() if symptoms_match else "",
            "example": re.sub(r"\s+", " ", example_match.group(1)).strip() if example_match else "",
        })
    if len(entries) < 150:
        raise SystemExit(f"Lexicon parser found only {len(entries)} entries; source format may have changed")
    return entries

def make_row(i, entry, mode, frame, variant):
    title, desc, symptoms = entry["title"], entry["description"], entry["symptoms"]
    behavior = symptoms or desc
    q = frame.format(behavior=behavior)
    common = (
        f"Fuente primaria: Lexicón del Esperpento Algorítmico, sección {entry['section']} "
        f"({title}), obra original del autor del proyecto. Nivel NH{entry['level']}. "
        f"Descripción: {desc} Evidencia/síntomas: {behavior}"
    )
    if mode == "diagnosis":
        answer = (
            f"El patrón podría corresponder a «{title}» (NH{entry['level']}), si la evidencia confirma "
            f"lo descrito: {desc} No diagnostiques a la persona por una frase aislada. {variant.capitalize()}. "
            "El epíteto clasifica una conducta observada, no define la identidad de nadie."
        )
        tag = "lexicon_behavioral_diagnosis"
    elif mode == "remediation":
        answer = (
            f"Si el diagnóstico «{title}» (NH{entry['level']}) está respaldado por hechos, empieza por "
            f"esto: {REMEDIES[entry['level']]} {variant.capitalize()} "
            "Cierra con una acción verificable; no conviertas el epíteto en sustituto de la solución."
        )
        tag = "lexicon_remediation"
    else:
        answer = (
            f"No basta con que algo te irrite para llamarlo «{title}». El Lexicón asigna NH{entry['level']} "
            f"a un patrón concreto: {desc} Comprueba el contexto y la recurrencia. {variant.capitalize()} "
            "Si falta evidencia o el caso es proporcionalmente menor, no apliques esa etiqueta."
        )
        tag = "lexicon_proportionality_and_precision"
    return {
        "id": f"lexicon-{i+1:05d}", "tag": tag, "context": common,
        "question": q + f" [{mode}; {title}; NH{entry['level']}; variante {variant}]",
        "answer": answer,
        "source": "Lexicón del Esperpento Algorítmico — obra original del autor; combinación sintética MINIRONIN v1",
        "source_section": entry["section"], "source_epithet": title,
        "severity": entry["level"], "license": "author-authorized-for-training",
    }

def main():
    text = SOURCE.read_text(encoding="utf-8")
    entries = extract_entries(text)
    rows = []
    for mode in MODES:
        for entry in entries:
            for frame in FRAMES:
                for variant in VARIANTS:
                    rows.append(make_row(len(rows), entry, mode, frame, variant))
                    if len(rows) == TARGET:
                        break
                if len(rows) == TARGET: break
            if len(rows) == TARGET: break
        if len(rows) == TARGET: break
    if len(rows) != TARGET:
        raise SystemExit(f"Only generated {len(rows)} rows")
    path = OUT / "minironin-lexicon-diagnostic-50k-v1.jsonl"
    digest = hashlib.sha256()
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            line = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
            f.write(line); digest.update(line.encode("utf-8"))
    manifest = {
        "version": 1, "deterministic": True, "records": len(rows),
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "parsed_lexicon_entries": len(entries),
        "unique_epithets_in_training": len({r["source_epithet"] for r in rows}),
        "unique_prompts": len({r["question"] for r in rows}),
        "modes": {m: sum(1 for r in rows if r["tag"] == {
            "diagnosis":"lexicon_behavioral_diagnosis",
            "remediation":"lexicon_remediation",
            "proportionality":"lexicon_proportionality_and_precision"}[m]) for m in MODES},
        "file": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
        "sha256": digest.hexdigest(),
        "attribution": "Original work by the MINIRONIN project author; used with explicit author permission.",
        "policy": "Behavioral diagnosis only; evidence, proportionality, self-awareness and remediation; no personal-attribute targeting.",
    }
    (OUT / "lexicon-50k-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
