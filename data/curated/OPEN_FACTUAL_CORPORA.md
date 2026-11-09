# Ampliación masiva de bibliotecas factuales — prioridad castellano

Este registro define el orden de adquisición de bibliotecas externas ya curadas. **Primero castellano; después cualquier idioma cuando aporte hechos, datos, conocimiento científico o documentación técnica verificable.** El idioma no es un filtro de exclusión: cada documento conserva su idioma original y puede indexarse de forma multilingüe.

## Política de adquisición
1. Prioridad A: fuentes primarias oficiales en castellano (estadística, legislación, ciencia, geografía, meteorología, salud pública, organismos públicos).
2. Prioridad B: colecciones abiertas en castellano curadas por bibliotecas, universidades, repositorios científicos y proyectos de conocimiento.
3. Prioridad C: bases factuales multilingües o internacionales (Wikidata, estadísticas globales, literatura científica OA, documentación técnica).
4. Prioridad D: corpus generales/educativos en cualquier idioma, siempre etiquetados como texto no necesariamente factual.
5. No confundir corpus grande con corpus fiable: el material sintético, conversacional o web ruidosa no se convierte en fuente factual por volumen.

## Fuentes para ingestión — castellano primero

| Orden | Colección / proyecto upstream | Contenido de interés | Idioma | Derechos / control necesario | Estado |
|---|---|---|---|---|---|
| 1 | Wikimedia Wikisource español (wikimedia/wikisource, config 20231201.es) | Obras completas, fuentes primarias, historia, filosofía, ciencia clásica | es | CC BY-SA 3.0/GFDL declarado por dataset; conservar atribución, historial y condiciones por obra | Ya en curso: seis lotes de 1.200 (7.200 textos); continuar por lotes no solapados |
| 2 | Wikipedia español (wikimedia/wikipedia, snapshot 20231101.es) | Enciclopedia factual amplia | es | CC BY-SA 3.0/GFDL según dataset; atribución y share-alike; artículos no equivalen a hechos verificados | Biblioteca de 100.000 preparada/publicada; reconciliar hashes e integración |
| 3 | Biblioteca Nacional de España / datos.gob.es | Catálogos, registros bibliográficos y OCR de obras digitalizadas | es | CC BY 4.0 donde lo declare el registro; revisar derechos de cada obra y calidad OCR | Adquisición selectiva pendiente |
| 4 | BOE — legislación consolidada y datos abiertos | Leyes, reales decretos, órdenes, jurisprudencia publicada y metadatos | es | Verificar aviso de reutilización, exclusiones y versión de cada conjunto; texto normativo no es asesoramiento | Candidato prioritario |
| 5 | INE — datos abiertos | Series estadísticas, metodología, clasificaciones y metadatos | es | Verificar licencia y condiciones por recurso; preservar unidad, periodo, ámbito y revisiones | Candidato prioritario |
| 6 | AEMET OpenData | Observaciones, climatología, predicciones archivadas y documentación | es | Respetar licencia, atribución, límites de API y fecha de actualización | Candidato prioritario |
| 7 | IGN / CNIG / datos geográficos abiertos | Cartografía, nomenclátor, geodesia, topografía y documentación | es | Revisar licencia de cada producto; separar datos vectoriales, metadatos y textos | Candidato prioritario |
| 8 | Banco de España — estadísticas y publicaciones | Series macroeconómicas, informes, glosarios y metodología | es | Revisar condiciones por publicación/dataset; preservar fecha y revisión | Candidato prioritario |
| 9 | OpenStax | Libros de ciencias, matemáticas y economía; versiones/traducciones disponibles | es/en | CC BY 4.0 salvo excepciones indicadas; atribución y revisión de componentes de terceros | Adquisición por libro |
| 10 | Open Logic Project | Lógica formal, demostraciones, teoría de conjuntos y fundamentos | en (traducir solo con procedencia) | CC BY 4.0 según proyecto; fijar versión y conservar atribución | Candidato |
| 11 | PRODATPHIL v0.3 | Filosofía de la ciencia, lógica e historia de ideas | en/de | Dominio público declarado por el editor; ya adquirido (147 obras) | Adquirido |
| 12 | Mathlib4 | Matemática formalizada y pruebas verificables | en/formal | Apache-2.0 en revisión fijada; conservar licencia y cabeceras | Herencia de RONIN-IA |
| 13 | PleIAs Common Corpus | Colecciones multilingües con procedencia y revisión de derechos | multilingüe; extraer es primero | Admisión por componente y documento; licencia/consentimiento no se heredan del nombre del corpus | Candidato de alto volumen |
| 14 | EleutherAI Common Pile v0.1 | Fuentes documentales abiertas ya agregadas y filtradas | mayoritariamente en | Revisar licencia y ficha de cada componente; no importar el agregado sin su manifiesto | Candidato por componente |
| 15 | Wikidata dumps | Hechos estructurados, identificadores, relaciones, fechas y referencias | multilingüe | CC0; mantener referencias, calificadores, rangos y fecha de snapshot | Candidato de alto valor factual |
| 16 | Eurostat | Estadística europea, definiciones y metodología | multilingüe | CC BY 4.0 en datos publicados, verificar excepciones y atribuir | Candidato de alto valor factual |
| 17 | World Bank Open Data | Indicadores y series internacionales | multilingüe | CC BY 4.0 según portal; conservar fuente, indicador, país, unidad y fecha | Candidato |
| 18 | OpenAlex | Grafo bibliográfico, autores, instituciones, trabajos y conceptos | multilingüe | CC0 para datos abiertos; no confundir metadatos bibliográficos con texto completo | Candidato |
| 19 | PubMed Central Open Access Subset | Artículos biomédicos y científicos a texto completo | multilingüe | Licencia por artículo; descargar solo artículos con licencia explícita compatible (p. ej. CC BY); excluir NC/ND si no autorizan el uso previsto | Candidato de alto valor |
| 20 | NASA NTRS / Earthdata | Ciencia espacial, observación terrestre, informes técnicos y datos | en; síntesis es | Reutilizar solo materiales públicos; excluir contenido de terceros y registrar producto/revisión | Selección ya iniciada |
| 21 | NOAA / USGS / NIST | Ciencia oceánica, geología, hidrología, estándares y ciberseguridad | en; síntesis es | Preferir documentos oficiales reutilizables; conservar versión, DOI/URL y distinguir síntesis propia de texto fuente | Síntesis inicial ya integrada |

## Fuentes de descubrimiento, no admisión automática
- OpenCorpus y catálogos similares: sirven para descubrir datasets y sus manifiestos, no para copiar el índice como si fueran datos.
- OSCAR, CulturaX, FineWeb2, MADLAD-400 y otros corpus web/multilingües: candidatos de cobertura lingüística, no autoridad factual. Usar solo componentes con procedencia/licencia clara, filtros de calidad, deduplicación y detección de PII.
- Common Crawl y dumps web: material de descubrimiento o selección específica; nunca ingestión indiscriminada.
- Corpus sintéticos (Cosmopedia y derivados): etiquetar como sintético; no usarlos como verdad de referencia ni como QA factual sin verificación independiente.

## Esquema obligatorio por documento
source_id, upstream_project, upstream_revision, document_id, canonical_url, title, language, domain, license_id, license_url, attribution, retrieved_at, content_sha256, normalized_sha256, split, quality_flags, factuality_class, synthetic, translation_of, evidence_urls.

## Clasificación factual
- primary_official: norma, estadística o documento de organismo responsable.
- peer_reviewed: publicación científica revisada por pares con licencia compatible.
- curated_reference: enciclopedia, libro educativo o colección curada con atribución.
- structured_assertion: hecho estructurado con referencias y calificadores.
- historical_primary_source: fuente primaria histórica; evidencia de lo que se publicó, no necesariamente verdad actual.
- synthetic_or_unverified: texto sintético, agregado web o afirmación no verificada.

## Reglas de calidad y entrenamiento
- Mantener idioma original; no traducir masivamente para inflar el corpus. Las traducciones son documentos derivados con translation_of y revisión factual.
- Extraer tablas como datos estructurados con unidad, escala, fecha, geografía y notas; no aplanar cifras perdiendo contexto.
- Preservar referencias, DOI, ISBN, identificadores, notas, fórmulas, pies de tabla y versiones.
- Deduplicar exacto y casi duplicado entre Wikipedia, Wikisource, BNE, RONIN-IA, HERETIC y nuevas fuentes; no sumar inventarios solapados.
- Separar por obra, autor, artículo, serie temporal y familia de traducción antes de crear train/validation/holdout.
- No ingerir benchmarks ni conjuntos de evaluación conocidos; no crear QA a partir de holdout.
- Las afirmaciones factuales deben poder rastrearse a una fuente. No fabricar preguntas-respuestas ni atribuir al original una síntesis propia.
- El material de salud, derecho y finanzas se admite como documentación descriptiva con fecha y jurisdicción, nunca como consejo personalizado.
- Mantener atribución y obligaciones share-alike en la distribución del corpus y sus derivados.
- La admisión documental no activa entrenamiento ni promociona checkpoints: exige un cambio separado y explícito en el manifiesto de entrenamiento.

## Objetivo operativo
Ampliar en lotes grandes y repetibles. Preferir cientos/miles de documentos por PR con selección determinista, número exacto de rutas, manifiesto SHA-256, validación UTF-8, longitud, procedencia y deduplicación. Para bibliotecas gigantes, publicar releases versionadas y checksums en lugar de inflar el historial Git. El recuento solo aumenta tras verificar bytes y documentos completos.
