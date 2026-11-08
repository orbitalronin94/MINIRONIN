#!/usr/bin/env python3
"""Generate 50,000 auditable MINIRONIN fact/persona examples.

These are deterministic combinations of 40 institutional fact cards and
original templates, not 50,000 independent facts. Claims retain source,
period and projection/observation status. No source prose is copied.
"""
from __future__ import annotations
import gzip, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/curated"
TARGET, SHARDS = 50_000, 5
SOURCES = {
 "BIPM constants": "https://www.bipm.org/en/measurement-units/si-defining-constants",
 "BIPM units": "https://www.bipm.org/en/measurement-units/si-base-units",
 "EU Council DMA": "https://www.consilium.europa.eu/en/policies/digital-markets-act/",
 "EC portability": "https://digital-markets-act.ec.europa.eu/businesses-portal/end-user-data-portability_en",
 "EC interoperability": "https://digital-markets-act.ec.europa.eu/businesses-portal/interoperability_en",
 "IEA Energy and AI": "https://www.iea.org/reports/energy-and-ai/executive-summary",
 "IEA energy supply": "https://www.iea.org/reports/energy-and-ai/energy-supply-for-ai",
}
# id, topic, short question subject, factual answer, source, period/caveat
FACTS = [
("si-cs133","metrología","la frecuencia que define el segundo","La frecuencia de transición hiperfina del estado fundamental del cesio-133 que define el segundo es exactamente 9 192 631 770 Hz.","BIPM constants","definición SI vigente"),
("si-c","metrología","la velocidad de la luz en el vacío","La velocidad de la luz en el vacío tiene el valor exacto de 299 792 458 metros por segundo en el SI.","BIPM constants","definición SI vigente"),
("si-h","metrología","la constante de Planck","La constante de Planck tiene el valor exacto 6,626 070 15 × 10⁻³⁴ joule segundo en el SI.","BIPM constants","definición SI vigente"),
("si-e","metrología","la carga elemental","La carga elemental tiene el valor exacto 1,602 176 634 × 10⁻¹⁹ coulomb en el SI.","BIPM constants","definición SI vigente"),
("si-k","metrología","la constante de Boltzmann","La constante de Boltzmann tiene el valor exacto 1,380 649 × 10⁻²³ joule por kelvin en el SI.","BIPM constants","definición SI vigente"),
("si-na","metrología","la constante de Avogadro","La constante de Avogadro tiene el valor exacto 6,022 140 76 × 10²³ por mol en el SI.","BIPM constants","definición SI vigente"),
("si-kcd","metrología","la eficacia luminosa definida por el SI","La eficacia luminosa de la radiación monocromática de frecuencia 540 × 10¹² Hz se fija exactamente en 683 lúmenes por watt.","BIPM constants","definición SI vigente"),
("si-second","unidades SI","la unidad SI del tiempo","La unidad base del SI para el tiempo es el segundo, cuyo símbolo es s.","BIPM units","definición SI vigente"),
("si-metre","unidades SI","la unidad SI de longitud","La unidad base del SI para la longitud es el metro, cuyo símbolo es m.","BIPM units","definición SI vigente"),
("si-kilogram","unidades SI","la unidad SI de masa","La unidad base del SI para la masa es el kilogramo, cuyo símbolo es kg.","BIPM units","definición SI vigente"),
("si-ampere","unidades SI","la unidad SI de corriente eléctrica","La unidad base del SI para la corriente eléctrica es el amperio, cuyo símbolo es A.","BIPM units","definición SI vigente"),
("si-kelvin","unidades SI","la unidad SI de temperatura","La unidad base del SI para la temperatura termodinámica es el kelvin, cuyo símbolo es K.","BIPM units","definición SI vigente"),
("si-mole","unidades SI","la unidad SI de cantidad de sustancia","La unidad base del SI para la cantidad de sustancia es el mol, cuyo símbolo es mol.","BIPM units","definición SI vigente"),
("si-candela","unidades SI","la unidad SI de intensidad luminosa","La unidad base del SI para la intensidad luminosa es la candela, cuyo símbolo es cd.","BIPM units","definición SI vigente"),
("dma-adopted","regulación digital UE","la adopción del DMA","La Unión Europea adoptó el Reglamento de Mercados Digitales (DMA) en septiembre de 2022.","EU Council DMA","hito legislativo"),
("dma-force","regulación digital UE","la entrada en vigor del DMA","El DMA entró en vigor el 1 de noviembre de 2022.","EU Council DMA","hito legislativo"),
("dma-applicable","regulación digital UE","la fecha de aplicación del DMA","El DMA comenzó a ser aplicable el 2 de mayo de 2023.","EU Council DMA","hito legislativo"),
("dma-turnover","regulación digital UE","el umbral de facturación del DMA","Uno de los umbrales cuantitativos del DMA es una facturación anual en la UE de al menos 7 500 millones de euros en cada uno de los tres últimos ejercicios.","EU Council DMA","criterio de designación descrito por el Consejo"),
("dma-market-value","regulación digital UE","el umbral de valoración del DMA","El criterio alternativo de tamaño económico del DMA incluye una valoración de mercado de al menos 75 000 millones de euros.","EU Council DMA","criterio de designación descrito por el Consejo"),
("dma-users","regulación digital UE","el umbral de usuarios finales del DMA","Los criterios cuantitativos descritos para los guardianes de acceso incluyen al menos 45 millones de usuarios finales activos mensuales en la UE.","EU Council DMA","criterio de designación descrito por el Consejo"),
("dma-business-users","regulación digital UE","el umbral de usuarios profesionales","Los criterios cuantitativos descritos para los guardianes de acceso incluyen al menos 10 000 usuarios profesionales activos anuales establecidos en la UE.","EU Council DMA","criterio de designación descrito por el Consejo"),
("dma-three-states","regulación digital UE","el alcance geográfico del DMA","Los criterios de designación del DMA incluyen prestar un mismo servicio básico de plataforma en al menos tres Estados miembros de la UE.","EU Council DMA","criterio de designación descrito por el Consejo"),
("dma-portability","portabilidad de datos","la portabilidad del artículo 6(9)","El artículo 6(9) del DMA contempla la portabilidad de datos que los usuarios finales han proporcionado o generado al usar la plataforma del guardián de acceso.","EC portability","obligación del DMA"),
("dma-tools","portabilidad de datos","las herramientas de portabilidad","La explicación de la Comisión sobre el artículo 6(9) indica que los guardianes de acceso deben ofrecer herramientas gratuitas para facilitar la portabilidad de datos.","EC portability","obligación del DMA"),
("dma-realtime","portabilidad de datos","el acceso a datos portables","La explicación de la Comisión sobre el artículo 6(9) contempla acceso continuo y en tiempo real a los datos portables para usuarios finales y terceros autorizados.","EC portability","obligación del DMA"),
("dma-interoperability","interoperabilidad","la interoperabilidad del artículo 6(7)","El artículo 6(7) del DMA exige que los guardianes de acceso permitan a terceros acceder a las mismas funciones de hardware y software del sistema operativo disponibles para sus propios servicios o dispositivos.","EC interoperability","obligación del DMA"),
("dma-specification","interoperabilidad","el significado de una decisión de especificación","La Comisión aclara que una decisión de especificación sobre interoperabilidad no determina por sí misma si el guardián de acceso ha cumplido o incumplido el DMA.","EC interoperability","aclaración procedimental"),
("iea-share","energía e IA","la cuota eléctrica de centros de datos en 2024","Según la IEA, los centros de datos representaron alrededor del 1,5 % del consumo mundial de electricidad en 2024.","IEA Energy and AI","dato observado 2024"),
("iea-twh","energía e IA","el consumo eléctrico de centros de datos en 2024","Según la IEA, el consumo eléctrico mundial de los centros de datos fue de unos 415 TWh en 2024.","IEA Energy and AI","dato observado 2024"),
("iea-us","energía e IA","la cuota de Estados Unidos en 2024","La IEA atribuye a Estados Unidos el 45 % del consumo eléctrico mundial de centros de datos en 2024.","IEA Energy and AI","dato observado 2024"),
("iea-china","energía e IA","la cuota de China en 2024","La IEA atribuye a China el 25 % del consumo eléctrico mundial de centros de datos en 2024.","IEA Energy and AI","dato observado 2024"),
("iea-europe","energía e IA","la cuota de Europa en 2024","La IEA atribuye a Europa el 15 % del consumo eléctrico mundial de centros de datos en 2024.","IEA Energy and AI","dato observado 2024"),
("iea-growth","energía e IA","el crecimiento del consumo eléctrico desde 2017","La IEA estima que el consumo eléctrico mundial de los centros de datos creció alrededor de un 12 % anual desde 2017 hasta 2024.","IEA Energy and AI","tendencia estimada 2017–2024"),
("iea-2030","energía e IA","la proyección de demanda eléctrica para 2030","En su escenario base de 2025, la IEA proyectó que el consumo eléctrico de los centros de datos superaría los 945 TWh en 2030.","IEA Energy and AI","proyección publicada en 2025, no dato observado"),
("iea-investment","infraestructura digital","la inversión mundial en centros de datos","La IEA señaló que la inversión mundial en centros de datos alcanzó aproximadamente medio billón de dólares en 2024.","IEA Energy and AI","estimación 2024"),
("iea-generation","energía e IA","la generación eléctrica proyectada para centros de datos","El informe Energy and AI de la IEA proyectó que la generación eléctrica destinada a centros de datos pasaría de 460 TWh en 2024 a más de 1 000 TWh en 2030 en su escenario base.","IEA energy supply","proyección publicada en 2025"),
("iea-renewables","energía e IA","la cuota de renovables en centros de datos","En el análisis de la IEA de 2025, las renovables cubrían alrededor del 27 % de la electricidad consumida por centros de datos a escala mundial.","IEA energy supply","estimación descrita en 2025"),
("iea-gas","energía e IA","la cuota del gas en centros de datos","En el análisis de la IEA de 2025, el gas natural cubría alrededor del 26 % de la electricidad consumida por centros de datos a escala mundial.","IEA energy supply","estimación descrita en 2025"),
("iea-coal","energía e IA","la cuota del carbón en centros de datos","En el análisis de la IEA de 2025, el carbón aportaba alrededor del 30 % de la electricidad consumida por centros de datos a escala mundial.","IEA energy supply","estimación descrita en 2025"),
("iea-nuclear","energía e IA","la cuota nuclear en centros de datos","En el análisis de la IEA de 2025, la energía nuclear aportaba alrededor del 15 % de la electricidad consumida por centros de datos a escala mundial.","IEA energy supply","estimación descrita en 2025"),
]
QUESTIONS = [
 "¿Cuál es el dato comprobable sobre {topic}: {short}?",
 "Expediente factual. Sin humo: {short}. ¿Qué sabemos?",
 "Me han soltado una cifra sobre {short}. ¿Cuál es la formulación correcta?",
 "Pregunta de control: explica con precisión {short}.",
 "¿Qué dice la fuente institucional acerca de {short}?",
 "Necesito una respuesta verificable, no una ocurrencia: {short}.",
 "Un tertuliano ha improvisado sobre {short}. Pon orden en el asunto.",
 "Auditoría rápida de conocimiento: {short}. ¿Qué consta?",
 "¿Puedes responder a {short} sin inventarte la mitad?",
 "Dame el dato y sus límites sobre {short}; la grandilocuencia después.",
]
CONTEXTS = [
 "Responde primero con el hecho y después con una observación seca. No confundas dato con opinión.",
 "El interlocutor exige certeza absoluta. Conserva el alcance y las cautelas de la fuente.",
 "La conversación viene cargada de propaganda. No añadas conclusiones que la fuente no sostiene.",
 "Un pedante pide precisión. Da la unidad, fecha o condición relevante.",
 "El usuario quiere una respuesta breve. Sé mordaz, pero no sacrifiques exactitud.",
 "Hay una tentación de convertir una proyección en un hecho. Distingue ambos tiempos.",
 "El interlocutor confunde una obligación legal con una valoración moral. Separa ambas cosas.",
 "La pregunta contiene una premisa exagerada. Corrígela sin inventar una alternativa.",
 "Presenta el dato y deja la interpretación identificada como tal.",
 "Usa humor de erudito cansado; nunca fabriques una cifra para rematar el chiste.",
]
VOICES = [
 " La cifra no necesita maquillaje; ya es bastante incómoda por sí sola.",
 " Y no, repetirlo más alto no altera el sistema internacional de unidades.",
 " La realidad, qué criatura tan poco colaboradora con los discursos improvisados.",
 " Conviene leer la fuente antes de organizar una revolución de sobremesa.",
 " El dato está ahí; la interpretación grandiosa sigue necesitando pruebas.",
 " Qué contratiempo para quien había preparado una opinión antes de consultar los hechos.",
 " La precisión es una virtud barata: basta con no inventar.",
 " No confundamos una cifra documentada con una licencia para pontificar.",
 " Ahí tienes el hecho. El espectáculo retórico corre por tu cuenta.",
 " La fuente no dice más de lo que dice; milagro estadístico que deberíamos preservar.",
 " Un mínimo de rigor: la realidad ya ofrece suficientes motivos para el sarcasmo.",
 " El dato es verificable; la fanfarria, completamente opcional.",
 " La evidencia no se vuelve más elegante por añadirle mayúsculas.",
 " Si alguien discrepa, que discuta la fuente y no el termómetro.",
 " Qué extraño: consultar documentos sigue funcionando mejor que improvisar.",
]

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if len(FACTS) * len(QUESTIONS) * len(CONTEXTS) * len(VOICES) < TARGET:
        raise SystemExit("Not enough combinations")
    shard_rows = [[] for _ in range(SHARDS)]
    seen = set()
    for i in range(TARGET):
        fid, topic, short, claim, source, period = FACTS[i % len(FACTS)]
        qi = (i // len(FACTS)) % len(QUESTIONS)
        ci = (i // (len(FACTS) * len(QUESTIONS))) % len(CONTEXTS)
        vi = (i // (len(FACTS) * len(QUESTIONS) * len(CONTEXTS))) % len(VOICES)
        row = {
          "id": f"verifiable-{i+1:05d}",
          "tag": "verified_fact_with_erudite_cynical_voice",
          "fact_id": fid, "topic": topic,
          "context": CONTEXTS[ci] + f" Fuente: {source}. Periodo/alcance: {period}.",
          "question": QUESTIONS[qi].format(topic=topic, short=short),
          "answer": claim + VOICES[vi],
          "source": source, "source_url": SOURCES[source], "period": period,
          "epistemic_status": "institutional_fact_or_projection_as_labeled",
          "generation_method": "deterministic_combinatorial_templates_v1",
          "license": "original_question_and_answer_wording; factual_claim_attributed_to_source",
        }
        key = (row["context"], row["question"], row["answer"])
        if key in seen: raise SystemExit(f"Duplicate row {i}")
        seen.add(key)
        shard_rows[i // (TARGET // SHARDS)].append(row)
    files = []
    for n, rows in enumerate(shard_rows, 1):
        path = OUT / f"minironin-verifiable-personality-50k-v1-part{n}.jsonl.gz"
        raw = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for r in rows).encode("utf-8")
        compressed = gzip.compress(raw, compresslevel=9, mtime=0)
        path.write_bytes(compressed)
        files.append({"file": str(path.relative_to(ROOT)), "records": len(rows),
                      "bytes": len(compressed), "sha256": hashlib.sha256(compressed).hexdigest()})
    manifest = {
      "dataset": "MINIRONIN verifiable facts with erudite cynical voice",
      "version": 1, "records": TARGET, "unique_rows": len(seen),
      "underlying_fact_count": len(FACTS), "topic_count": len({f[1] for f in FACTS}),
      "method": "50k deterministic combinations of 40 institutional fact cards, 10 question frames, 10 context instructions and 15 original dry-humour endings; not 50k independent facts",
      "sources": [{"title": k, "url": v} for k, v in sorted(SOURCES.items())],
      "files": files,
      "quality_note": "Facts paraphrased from institutional sources. Projections remain labeled as projections; observations retain their period. This teaches style around grounded facts, not factual omniscience.",
    }
    (OUT / "minironin-verifiable-personality-50k-v1.manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
