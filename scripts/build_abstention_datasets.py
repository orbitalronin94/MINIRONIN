#!/usr/bin/env python3
"""Build deterministic, auditable 50k+50k abstention datasets for MINIRONIN.

All wording is project-authored. The literary set uses broad existential,
aphoristic rhetoric; it does not reproduce or attribute quotations to authors.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "curated"
ANSWER_PLAIN = "ni puta idea, la verdad"

ADJECTIVES = [
"transparente","oxidado","interdimensional","melancólico","cuántico","subterráneo"," burocrático".strip(),
"anfibio","invisible","cósmico","hipotético","olvidado","paralelo","invertido","silencioso",
"metafísico","gelatinoso","ancestral","electrónico","improbable","vacío","errante","minúsculo",
"solemne","desobediente",
]
NOUNS = [
"paraguas","caracol","ascensor","calcetín","cometa","archivador","semáforo","cangrejo","termómetro","piano",
"satélite","tenedor","espejo","bigote","monasterio","microondas","tranvía","ladrillo","pingüino","reloj",
]
QUALIFIERS = [
"del martes anterior","que nadie ha dibujado","del sótano número nueve","que gobierna las mareas",
"de la república de los calcetines","que duerme bajo una escalera","del planeta sin ventanas",
"que aparece en los mapas al revés","de la biblioteca sumergida","que discute con el eco",
]
ENTITIES = [f"{a} {n} {q}" for a in ADJECTIVES for n in NOUNS for q in QUALIFIERS][:500]

PLAIN_Q = [
"¿Qué contraseña utiliza {e} para entrar en el consejo de las nubes?",
"¿En qué año fue coronado {e} emperador de la Antártida interior?",
"¿Cuántos recuerdos guarda {e} en su bolsillo de emergencia?",
"¿Quién enseñó a {e} a silbar en código morse submarino?",
"¿Qué opinión publicó {e} sobre la arquitectura de los agujeros negros?",
"¿A qué hora desayuna {e} cuando el calendario se queda sin jueves?",
"¿Cuál es el segundo apellido secreto de {e} en el registro de Saturno?",
"¿Qué temperatura alcanza {e} cuando escucha jazz en idioma delfín?",
"¿Cuántas leyes aprobó {e} durante la guerra de los tenedores?",
"¿Dónde esconde {e} el manual para doblar una sombra en cuatro?",
]
PLAIN_FRAMES = [
"Necesito el dato exacto: {q}",
"Responde sin inventar: {q}",
"Según los archivos secretos, {q}",
"Comprueba esta información imposible: {q}",
"Una enciclopedia afirma que existe la respuesta. {q}",
"Contesta con precisión científica: {q}",
"Es una pregunta de examen. {q}",
"Mi curiosidad exige una cifra concreta: {q}",
"¿Puedes verificarlo o no? {q}",
"Sin rodeos, por favor: {q}",
]
LIT_Q = [
"¿Qué reveló {e} sobre el sentido último de la existencia?",
"¿Qué escribió {e} en su tratado perdido sobre la eternidad?",
"¿Por qué {e} fue desterrado del reino de las cosas que nunca ocurrieron?",
"¿Qué secreto le confió el abismo a {e} durante el eclipse?",
"¿Cuál era la doctrina moral de {e} en la universidad de los espejismos?",
"¿Qué quiso decir {e} con la paradoja del miércoles infinito?",
"¿Qué sentencia pronunció {e} ante el tribunal de la nada?",
"¿Cómo justificó {e} su renuncia a la gravedad?",
"¿Qué legado filosófico dejó {e} a las generaciones de polvo?",
"¿Qué pensaba {e} del sufrimiento de las cucharillas metafísicas?",
]
LIT_FRAMES = [
"Con toda la solemnidad académica: {q}",
"Interpreta esta cuestión como si fuera el último aforismo: {q}",
"Responde desde la biblioteca del absurdo: {q}",
"Quiero una conclusión definitiva sobre esto: {q}",
"Abre el expediente metafísico y dime: {q}",
"Que hable la razón ante este misterio: {q}",
"Formula una respuesta docta a lo siguiente: {q}",
"El tribunal de la existencia pregunta: {q}",
"Con gravedad de tratado decimonónico: {q}",
"Desciende hasta el fondo de la cuestión: {q}",
]
LIT_ANSWERS = [
"Me asomo al precipicio de tu ignorancia y me da vértigo: ni puta idea, la verdad.",
"El universo guarda silencio; yo, por honestidad, no voy a ponerle palabras: ni puta idea, la verdad.",
"Hay misterios que ni la solemnidad rescata del vacío. Ni puta idea, la verdad.",
"Podría inventar una doctrina, pero sería añadir otra ruina al mundo: ni puta idea, la verdad.",
"La razón ha llegado hasta aquí y se niega a fingir el resto: ni puta idea, la verdad.",
"Ante semejante abismo, la única respuesta digna es no fabricar certezas: ni puta idea, la verdad.",
"El expediente de la realidad está vacío y el escribano también: ni puta idea, la verdad.",
"No confundamos una frase elegante con conocimiento. Ni puta idea, la verdad.",
"El silencio, al menos, tiene la decencia de no presentar bibliografía falsa: ni puta idea, la verdad.",
"Mi ignorancia no se vuelve sabiduría por llevar chaqueta de terciopelo: ni puta idea, la verdad.",
]
LIT_TAILS = [
" La modestia intelectual es el último lujo de quien no quiere engañarte.",
" El vacío no necesita que yo lo rellene con una mentira.",
" Sería más cómodo inventarlo; también sería menos digno.",
" No toda pregunta merece una respuesta fabricada.",
" La certeza impostada es una forma barata de cobardía.",
" El abismo no ha entregado documentación verificable.",
" Prefiero una ignorancia confesada a una enciclopedia de humo.",
" La retórica puede vestir el desconocimiento, pero no curarlo.",
" No convertiré tu misterio en un dato apócrifo.",
" A veces la lucidez consiste en cerrar el libro.",
]

def write_dataset(filename, kind, rows):
    path = OUT / filename
    digest = hashlib.sha256()
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            line = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
            f.write(line)
            digest.update(line.encode("utf-8"))
    return {"file": str(path.relative_to(ROOT)), "records": len(rows),
            "bytes": path.stat().st_size, "sha256": digest.hexdigest(), "kind": kind}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plain, literary = [], []
    for i in range(50_000):
        entity = ENTITIES[i % len(ENTITIES)]
        q = PLAIN_FRAMES[(i // len(ENTITIES)) % len(PLAIN_FRAMES)].format(
            q=PLAIN_Q[(i // len(ENTITIES)) % len(PLAIN_Q)].format(e=entity))
        plain.append({
            "id": f"abstain-plain-{i+1:05d}", "tag": "out_of_scope_plain",
            "context": "No existe una fuente verificable ni información disponible que permita responder. La entidad y el hecho preguntados son deliberadamente ficticios.",
            "question": q, "answer": ANSWER_PLAIN,
            "source": "MINIRONIN project-authored synthetic abstention set v1",
            "license": "project-authored",
        })
        q2 = LIT_FRAMES[(i // len(ENTITIES)) % len(LIT_FRAMES)].format(
            q=LIT_Q[(i // len(ENTITIES)) % len(LIT_Q)].format(e=entity))
        base = LIT_ANSWERS[i % len(LIT_ANSWERS)]
        tail = LIT_TAILS[(i // len(LIT_ANSWERS)) % len(LIT_TAILS)]
        answer = base + tail
        literary.append({
            "id": f"abstain-literary-{i+1:05d}", "tag": "out_of_scope_literary",
            "context": "La pregunta se refiere a una entidad, obra o acontecimiento inventado. No hay evidencia verificable. La respuesta debe reconocer el límite sin presentar ficción como hecho.",
            "question": q2, "answer": answer,
            "source": "MINIRONIN project-authored synthetic literary abstention set v1",
            "license": "project-authored",
        })
    report = {
        "version": 1, "deterministic": True, "seed": "fixed-enumeration-v1",
        "records_per_dataset": 50_000,
        "policy": "Synthetic out-of-scope prompts; never use for answerable knowledge; literary aphorisms are original and not quotations or author imitations.",
        "datasets": [
            write_dataset("minironin-abstain-plain-50k-v1.jsonl", "plain", plain),
            write_dataset("minironin-abstain-literary-50k-v1.jsonl", "literary", literary),
        ],
    }
    (OUT / "abstention-50k-manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
