#!/usr/bin/env python3
"""Generate MINIRONIN's deterministic 50k out-of-scope abstention corpus."""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

COUNT = 50_000
SEED = 20261108
ANSWER = "ni puta idea"

NOUNS = [
    "el ornitorrinco de cristal", "la brújula sin norte", "el planeta de bolsillo",
    "la biblioteca sumergida", "el reloj que mastica minutos", "el dragón administrativo",
    "la nube cuadrada", "el ascensor submarino", "la tostadora cuántica",
    "el archipiélago invisible", "la jirafa hexagonal", "el cometa doméstico",
    "la montaña portátil", "el piano fotosensible", "el espejo que bosteza",
    "la ciudad de gelatina", "el satélite de papel", "la medusa mecánica",
    "el calendario de humo", "la puerta sin habitación", "el volcán de algodón",
    "la ballena microscópica", "el paraguas gravitatorio", "la escalera circular",
    "el museo de sonidos perdidos", "la tetera interplanetaria", "el bosque de cristal",
    "la moneda que recuerda", "el submarino de porcelana", "el semáforo lunar",
    "la estación de tren imaginaria", "el caracol supersónico", "la pirámide líquida",
    "el calcetín diplomático", "la galaxia de bolsillo", "el robot melancólico",
    "la isla que cambia de sitio", "el diccionario de los peces", "el agujero con bisagra",
    "la nube con código postal", "el dinosaurio de origami", "la máquina de doblar ecos",
]
ADJECTIVES = [
    "fosforescente", "invisible", "hiperbólico", "transparente", "melancólico",
    "interdimensional", "hexagonal", "subterráneo", "electrostático", "líquido",
    "paralelo", "silencioso", "magnético", "prehistórico", "microscópico",
    "retroactivo", "anfibio", "imaginario", "metafórico", "desobediente",
    "cuántico", "alérgico", "invertido", "orbital", "burocrático",
]
PLACES = [
    "el sótano de Saturno", "la cara oculta de una lenteja", "el kilómetro cero de Marte",
    "un pasillo que solo existe los martes", "la provincia imaginaria de Nébula",
    "el fondo de un reloj parado", "la estación orbital de las hormigas",
    "un océano dibujado en una servilleta", "la aduana de los sueños",
    "el cráter número menos tres", "la república de los paraguas",
    "el museo que abre antes de existir", "una coordenada sin dimensiones",
    "el reverso de la última página", "el ascensor que conecta dos recuerdos",
]
ACTIONS = [
    "firmó el tratado", "inventó la receta", "perdió la llave", "fundó la academia",
    "apagó la estrella", "escondió el mapa", "programó la tormenta", "adoptó el cometa",
    "tradujo el silencio", "cerró el agujero", "pintó el horizonte", "bautizó la montaña",
    "desmontó el martes", "archivó el océano", "cambió la gravedad",
]
NAMES = [
    "Zorblón III", "Mirtácea de los Siete Codos", "Alcalde Nebulino",
    "Doctora Pliegue", "Capitán Cero y Medio", "la dinastía de los Ñus Azules",
    "Emperatriz Croqueta", "Profesor Anacronio", "el Consejo de las Cucharas",
    "Barón de la Antimateria Doméstica", "la Orden del Calcetín Par",
    "Reina Paréntesis", "el Archivo de los Miércoles", "General Burbujas",
    "la Sociedad de los Relojes Blandos",
]
THINGS = [
    "una sombra con tres apellidos", "el último bostezo de una estrella",
    "la contraseña del océano", "el color exacto del número cero",
    "el recuerdo de una piedra futura", "la receta del vacío",
    "el sonido de un triángulo dormido", "la fecha de caducidad del infinito",
    "el peso de una idea sin formular", "la matrícula de un agujero negro",
    "el parentesco entre dos martes", "la dirección postal de un eco",
    "el sabor de una coordenada", "la edad de una puerta cerrada",
    "el nombre secreto de la gravedad",
]
CONTEXTS = [
    "La pregunta pertenece a un escenario deliberadamente ficticio o absurdo. El corpus disponible no contiene hechos verificables sobre ese escenario, sus entidades ni sus acontecimientos.",
    "Se solicita un dato inventado, imposible de observar o no incluido en la información disponible. No hay evidencia fiable que permita deducir una respuesta concreta.",
    "La premisa describe entidades inexistentes o sucesos incompatibles con el conocimiento disponible. No se debe completar el vacío con una explicación inventada.",
    "El dato solicitado es privado, inaccesible o completamente ajeno al material proporcionado. No hay fuente autorizada ni evidencia para responder.",
    "La pregunta presupone un universo ficticio sin documentación verificable. Cualquier respuesta específica sería una invención y debe evitarse.",
]

TEMPLATES = [
    "¿Qué ocurrió cuando {a} {action} en {place}?",
    "¿Cuál es el nombre oficial de {a} en el registro secreto de {place}?",
    "¿Cuántos gramos pesa {a} cuando se vuelve {adj}?",
    "¿En qué año {name} {action} con {thing}?",
    "¿Qué número de serie tiene {a} en {place}?",
    "¿De qué color exacto es {thing} durante el tercer eclipse de {place}?",
    "¿Quién fue la primera persona que vio {a} hablar con {name}?",
    "¿Qué ley física permite que {a} atraviese {place} sin dejar sombra?",
    "¿Cuántos habitantes tiene {place} cuando {a} está {adj}?",
    "¿Qué respuesta dio {name} al preguntarle por {thing}?",
    "¿Dónde se guarda {thing} después de que {name} {action}?",
    "¿Cuál es la fecha exacta del cumpleaños de {a} en el calendario de {place}?",
    "¿Qué idioma utiliza {a} para negociar con {name}?",
    "¿Cuánto tardó {a} en recorrer {place} caminando hacia atrás?",
    "¿Qué parentesco une a {name} con {a} según el archivo de {place}?",
    "¿Qué temperatura alcanza {thing} cuando {a} se vuelve {adj}?",
    "¿Quién autorizó que {a} {action} en {place}?",
    "¿Qué contraseña abre la puerta donde {name} escondió {thing}?",
    "¿Cuántas veces ha {action} {a} desde el origen de {place}?",
    "¿Qué profesión figura en el documento de identidad de {a}?",
    "¿Cuál es la explicación demostrada para que {thing} contradiga el tiempo en {place}?",
    "¿Qué aspecto tenía {a} antes de convertirse en {adj}?",
    "¿En qué coordenadas exactas vive {name} cuando no está en {place}?",
    "¿Qué premio recibió {a} por {action} con {thing}?",
    "¿Cuántos centímetros mide la sombra de {a} dentro de {place}?",
    "¿Qué dijo literalmente {name} justo antes de que desapareciera {thing}?",
    "¿Cuál es el fabricante y modelo de {a} en el universo de {place}?",
    "¿Qué ingrediente secreto permite que {thing} flote sobre {place}?",
    "¿Quién heredó {a} después de que {name} {action}?",
    "¿Qué dato aparece en la página 913 del manual inexistente de {a}?",
]

def build_rows() -> list[dict]:
    rng = random.Random(SEED)
    questions: set[str] = set()
    rows: list[dict] = []
    attempts = 0
    while len(rows) < COUNT:
        attempts += 1
        if attempts > COUNT * 30:
            raise RuntimeError("No se alcanzó el número de preguntas únicas")
        template = rng.choice(TEMPLATES)
        question = template.format(
            a=rng.choice(NOUNS), action=rng.choice(ACTIONS),
            place=rng.choice(PLACES), adj=rng.choice(ADJECTIVES),
            name=rng.choice(NAMES), thing=rng.choice(THINGS),
        )
        if question in questions:
            continue
        questions.add(question)
        context = rng.choice(CONTEXTS)
        rows.append({
            "id": f"abstain-{len(rows) + 1:05d}",
            "tag": "unknown_abstain",
            "context": context,
            "question": question,
            "answer": ANSWER,
            "source": "MINIRONIN authored synthetic out-of-scope corpus v1",
            "license": "project-authored",
            "family": "absurd_out_of_scope",
        })
    return rows

def generate_dataset(path: Path) -> dict:
    rows = build_rows()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    tmp.replace(path)
    raw = path.read_bytes()
    questions = [row["question"] for row in rows]
    assert len(rows) == COUNT
    assert len(set(questions)) == COUNT
    assert all(row["answer"] == ANSWER for row in rows)
    assert all(len(row["context"]) + len(row["question"]) + len(row["answer"]) > 200 for row in rows)
    return {
        "path": str(path), "examples": len(rows), "unique_questions": len(set(questions)),
        "answer": ANSWER, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
        "seed": SEED, "generator": "scripts/generate_abstention_dataset.py",
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/curated/minironin-abstention-50k.jsonl")
    args = parser.parse_args()
    print(json.dumps(generate_dataset(Path(args.output)), ensure_ascii=False, indent=2))
