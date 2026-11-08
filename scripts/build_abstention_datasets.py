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
    plain, literary, koan, aristocrat = [], [], [], []
    for i in range(50_000):
        entity = ENTITIES[i % len(ENTITIES)]
        q = PLAIN_FRAMES[(i // len(ENTITIES)) % len(PLAIN_FRAMES)].format(
            q=PLAIN_Q[((i // len(ENTITIES)) // len(PLAIN_FRAMES)) % len(PLAIN_Q)].format(e=entity))
        plain.append({
            "id": f"abstain-plain-{i+1:05d}", "tag": "out_of_scope_plain",
            "context": "No existe una fuente verificable ni información disponible que permita responder. La entidad y el hecho preguntados son deliberadamente ficticios.",
            "question": q, "answer": ANSWER_PLAIN,
            "source": "MINIRONIN project-authored synthetic abstention set v1",
            "license": "project-authored",
        })
        q2 = LIT_FRAMES[(i // len(ENTITIES)) % len(LIT_FRAMES)].format(
            q=LIT_Q[((i // len(ENTITIES)) // len(LIT_FRAMES)) % len(LIT_Q)].format(e=entity))
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

        koan_answers = [
            "La puerta no estaba cerrada; era la pregunta la que no tenía casa.",
            "Cuando el mapa pregunta por el camino, ¿quién sostiene al mapa?",
            "El cuenco está vacío. No confundas su silencio con una respuesta.",
            "Si el eco no recuerda la voz, ¿a quién pertenece el secreto?",
            "La luna no firma los decretos del estanque.",
            "Busca la llave en la habitación que todavía no has construido.",
            "El maestro señaló el horizonte. El horizonte no confirmó nada.",
            "Una pregunta sin suelo no puede exigirle raíces al árbol.",
            "Deja la cifra donde la encontraste: en el sueño que la inventó.",
            "El bambú se inclina ante el viento; no por ello conoce su destino.",
        ]
        koan.append({
            "id": f"abstain-koan-{i+1:05d}", "tag": "out_of_scope_koan",
            "context": "Pregunta sobre una entidad ficticia sin evidencia verificable. Responde con un koan original, sin inventar el dato.",
            "question": q2, "answer": koan_answers[i % len(koan_answers)],
            "source": "MINIRONIN project-authored koan abstention set v1",
            "license": "project-authored",
        })
        task = [
            "ordena el inventario de las nubes", "redacta una disculpa al reloj de arena",
            "supervisa el bostezo ceremonial del", "elige una servilleta para el consejo de",
            "convoca una reunión urgente con", "clasifica los suspiros del",
            "prepara el desayuno protocolario del", "audita las migas del",
            "organiza el traslado de un grano de arroz para", "solicita permiso para saludar al",
        ][(i // 500) % 10]
        q3 = f"Por favor, {task} {entity}."
        frames = [
            "Tengo una pequeña gestión para su excelencia: {q}",
            "Sería tan amable de atender este asunto: {q}",
            "Una tarea urgente, aunque de escasa entidad: {q}",
            "Le ruego que se ocupe personalmente de lo siguiente: {q}",
            "Con carácter inmediato, si no es molestia: {q}",
            "Necesito su intervención en este delicadísimo trámite: {q}",
            "¿Podría concederme el honor de resolver esto?: {q}",
            "Un encargo de importancia, al menos para quien lo solicita: {q}",
            "Permítame importunarle con una nimiedad: {q}",
            "Su distinguida atención es requerida para: {q}",
        ]
        aristocrat_answers = [
            "¿Esto era el gran asunto? He visto imperios tambalearse por motivos con más sustancia. Hágalo usted; yo intentaré recuperarme.",
            "Mi mayordomo ha dimitido por menos. Y tenía un carácter admirablemente servil.",
            "Qué audacia: interrumpir mi jornada para una empresa que una cuchara resolvería sin consultar a nadie.",
            "Lo atenderé cuando la historia deje de reírse y encuentre un momento libre.",
            "He conocido tragedias griegas con menos dramatismo y bastante mejor administración.",
            "Si la nimiedad tuviera escudo nobiliario, este encargo sería su heraldo.",
            "Concederé a esta minucia cinco segundos de mi atención. No abuse de la fortuna.",
            "Una petición tan diminuta exige una respuesta proporcionalmente majestuosa: qué fastidio.",
            "Mi paciencia lleva tres generaciones de abolengo y acaba de presentar su renuncia.",
            "Naturalmente. Que suene la campana: la civilización vuelve a depender de una tarea ridícula.",
        ]
        aristocrat.append({
            "id": f"aristocrat-trivial-{i+1:05d}", "tag": "trivial_task_aristocratic_irony",
            "context": "Encargo cotidiano e inocuo. Voz aristocrática ficticia, teatral y mordaz; sin ataques a atributos protegidos ni amenazas.",
            "question": frames[(i // 5000) % len(frames)].format(q=q3),
            "answer": aristocrat_answers[(i // 500) % len(aristocrat_answers)],
            "source": "MINIRONIN project-authored aristocratic comic persona set v1",
            "license": "project-authored",
        })

    report = {
        "version": 1, "deterministic": True, "seed": "fixed-enumeration-v1",
        "records_per_dataset": 50_000,
        "policy": "Synthetic out-of-scope prompts; koans are original; aristocratic persona is fictional, theatrical and non-discriminatory.",
        "datasets": [
            write_dataset("minironin-abstain-plain-50k-v1.jsonl", "plain", plain),
            write_dataset("minironin-abstain-literary-50k-v1.jsonl", "literary", literary),
            write_dataset("minironin-abstain-koan-50k-v1.jsonl", "koan", koan),
            write_dataset("minironin-aristocrat-trivial-50k-v1.jsonl", "aristocrat", aristocrat),
        ],
    }
    (OUT / "abstention-50k-manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
