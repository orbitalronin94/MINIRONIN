# Lecciones de ingeniería extraídas de entrenamientos

**Versión:** 1.0  
**Idioma:** castellano  
**Registros:** 50  
**Método:** curación manual a partir de logs y metadatos de artefactos de GitHub Actions.

Este conjunto transforma evidencia operativa de RONIN-IA y HERETIC-RONIN en ejemplos explicativos. No contiene logs brutos ni respuestas automáticas del docente.

## Fuentes incluidas

- HERETIC-RONIN, ejecución [42370725970](https://github.com/orbitalronin94/HERETIC-RONIN/actions/runs/42370725970), trabajo 128398241561, artefacto 13574129542.
- RONIN-IA, ejecución [42364138740](https://github.com/orbitalronin94/RONIN-IA/actions/runs/42364138740), trabajos 128378601930 y 128378602072.
- HERETIC-RONIN, benchmark CPU [42355677701](https://github.com/orbitalronin94/HERETIC-RONIN/actions/runs/42355677701), referencia y variantes de hilos, mmap, BF16, compilación y afinidad.
- HERETIC-RONIN, bloque de entrenamiento [42355677713](https://github.com/orbitalronin94/HERETIC-RONIN/actions/runs/42355677713), pasos 600–2600 y curva de pérdida registrada en el log.

## Esquema

Cada línea JSONL contiene:
- identificador estable;
- tipo y dominio;
- instrucción y respuesta redactadas manualmente en castellano;
- evidencia concreta del log/manifiesto;
- repositorio, ejecución y trabajo de origen;
- nivel de confianza y método de curación;
- uso previsto.

## Criterios de calidad

- Se separan hechos observados e interpretación.
- No se confunde CI correcto con mejora del modelo.
- No se confunde smoke test con evaluación reservada.
- Un error anterior al primer paso del optimizador se clasifica como fallo de preparación, no como divergencia de entrenamiento.
- Las respuestas generadas por un docente no se consideran verdaderas sin verificación independiente.
- No se incluyen pesos, estados de optimizador, prompts/answers del holdout, secretos ni identificadores personales.

## Exclusión importante: lote docente de HERETIC

El artefacto de la ejecución 42370725970 contenía 200 ejemplos generados por SoAIHQ/Qwen3.5-4B-GGUF Q4_K_M. El propio manifiesto declara que solo se comprobaron formato, longitud y unicidad; no hubo verificación factual independiente. La muestra inspeccionada mostró preguntas redundantes y respuestas semánticamente dudosas. **No se incorpora ese JSONL bruto como supervisión aprobada.** Se conserva únicamente la lección sobre sus límites de calidad y la evidencia de la ejecución.

## Auditoría e integridad

El lote de 50 registros pasó la auditoría en [ejecución 42379452577](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42379452577). SHA-256: `f96218280922a1a8cfe2ac9d7520b0c554b72e4aa600aae95a9581350a30e204`. El manifiesto versionado recoge nueve repositorios de origen.

## Objetivo de expansión

El objetivo es llegar a 1.000 casos válidos. El progreso y los criterios de admisión están en [ENGINEERING_CASES_1000.md](../../docs/ENGINEERING_CASES_1000.md). Los logs repetidos de una misma suite no se cuentan como casos distintos.

## Uso

Estos registros pueden servir para entrenar al modelo a interpretar métricas, diagnosticar fallos y explicar controles de reproducibilidad. No sustituyen los corpus lingüísticos generales ni los benchmarks reservados. Antes de una mezcla de entrenamiento, deben pasar deduplicación global y revisión de contaminación del holdout.


## Biblioteca conductual de MINIRONIN: datasets creados y conectados al entrenamiento

**Estado:** los ocho datasets de esta sección ya tienen generadores deterministas, validación automática y carga explícita en el entrenamiento largo. Se generan en GitHub Actions antes de cada ciclo; no se mantienen como ocho ficheros JSONL gigantes versionados en Git. Actions los materializa, verifica sus 50.000 registros y SHA-256, los incorpora a dominios separados del entrenador y conserva los JSONL y manifiestos como artefactos del ciclo.

**Volumen conductual generado por ciclo:** 8 datasets × 50.000 registros = **400.000 ejemplos**.

### Eje de abstención y estilo

| Dataset | Registros | Finalidad |
|---|---:|---|
| `minironin-abstain-plain-50k-v1.jsonl` | 50.000 | Preguntas deliberadamente fuera de ámbito; respuesta canónica exacta `ni puta idea, la verdad`. |
| `minironin-abstain-literary-50k-v1.jsonl` | 50.000 | Reconocer desconocimiento con aforismos originales y tono existencial. |
| `minironin-abstain-koan-50k-v1.jsonl` | 50.000 | Reconocer falta de evidencia mediante koans originales y paradójicos. |
| `minironin-aristocrat-trivial-50k-v1.jsonl` | 50.000 | Encargos nimios e inocuos respondidos con desdén aristocrático teatral y cómico. |

### Arsenal de cuatro personalidades nuevas

| Dataset | Registros | Finalidad |
|---|---:|---|
| `minironin-casuist-cynic-50k-v1.jsonl` | 50.000 | Detectar falacias informales y devolver preguntas socráticas con sarcasmo intelectual. |
| `minironin-scientist-exhausted-50k-v1.jsonl` | 50.000 | Responder preguntas científicas conocidas con datos, fórmulas y unidades correctas, acompañados de exasperación académica teatral. |
| `minironin-oracle-doom-50k-v1.jsonl` | 50.000 | Dar orientación cotidiana envuelta en profecías cósmicas pesimistas y desproporcionadas. |
| `minironin-error404-indifference-50k-v1.jsonl` | 50.000 | Voz absurda, fría e indiferente ante preguntas cotidianas, sin hostilidad ni falsa incapacidad. |

### Generación, auditoría e integración

- `scripts/build_abstention_datasets.py`: genera los cuatro conjuntos del eje de abstención.
- `scripts/build_personality_datasets.py`: genera los cuatro conjuntos de personalidades adicionales.
- `scripts/validate_personality_datasets.py` y el workflow `.github/workflows/abstention-dataset-check.yml`: comprueban cardinalidad, IDs, preguntas únicas, etiquetas, referencias científicas y SHA-256. La auditoría del primer bloque comprueba además las respuestas canónicas y los koans.
- `scripts/train_long_run.py`: carga los ocho JSONL directamente en ocho dominios de entrenamiento separados; exige exactamente 50.000 ejemplos por dominio y registra bytes, SHA-256 y recuentos en el manifiesto.
- `.github/workflows/long-training.yml`: regenera los ocho conjuntos antes de cada ciclo, los valida y los archiva junto con los manifiestos en los artefactos de entrenamiento.
- `scripts/train_seed_tournament.py`: reserva un peso separado para cada dominio. Los pesos se normalizan al construir el muestreo.

Los datasets son contenido original del proyecto. Las constantes SI del conjunto científico se apoyan en las definiciones del folleto SI del BIPM; las demás muestras usan ecuaciones estándar claramente identificadas. Las respuestas no deben presentar estimaciones como valores exactos ni omitir las condiciones de validez de una fórmula.

### Salvaguardas de evaluación

Estos conjuntos enseñan registros estilísticos concretos; no justifican aplicar todos los tonos a cualquier conversación. La evaluación debe medir por separado:

1. abstención correcta ante preguntas realmente fuera de ámbito y abstención indebida ante preguntas respondibles;
2. detección de falacias sin confundir desacuerdo con error lógico;
3. exactitud factual, unidades y condiciones de validez en ciencia, incluso bajo el tono de personaje;
4. utilidad práctica residual en el oráculo, y ausencia de respuestas hostiles en el modo indiferente;
5. activación del tono solo cuando el contexto lo pide, evitando que la personalidad contamine matemáticas, ciencia, instrucciones útiles o peticiones legítimas.

Ningún checkpoint se promueve por haber aprendido estos estilos: sigue siendo necesaria una evaluación holdout independiente y una comparación antes/después con el mismo protocolo.


## Lexicón del Esperpento Algorítmico — fuente propia autorizada

El texto original se conserva en `sources/LEXICON-DEL-ESPERPENTO-ALGORITMICO.md`.
Por autorización expresa del autor, `scripts/build_lexicon_dataset.py`
extrae los epítetos estructurados y construye 50.000 ejemplos reproducibles
para tres tareas: diagnóstico conductual, remediación y proporcionalidad/
precisión. Cada ejemplo incluye sección, epíteto, nivel NH y atribución.
El manifiesto `lexicon-50k-manifest.json` registra SHA-256 del texto fuente
y del JSONL generado. La validación se ejecuta con
`scripts/validate_lexicon_dataset.py`.

El corpus es un dominio de entrenamiento independiente (`lexicon`, peso
inicial experimental 2%). Su inclusión no implica que un checkpoint concreto
ya haya consumido los ejemplos ni que haya mejorado en evaluación.


## Biblioteca tecnopolítica — fuente original del autor

Se incorpora sources/EL-BUS-DE-DATOS-PERTENECE-AL-AMO.md, edición íntegra de 48 capítulos autorizada expresamente por su autor para uso interno. El texto se conserva como fuente de ensayo original; no se etiqueta como investigación revisada por pares ni como hechos verificados.

- Dominio de entrenamiento: author_original.
- Ingesta: texto completo, limpieza y fragmentación determinista mediante read_full_text.
- Validación: partición por documentos y ventanas de validación independientes; el entrenamiento falla si falta este dominio o no genera ventanas de evaluación.
- Peso inicial: 2% del muestreo normalizado, ajustable tras evaluación por dominio.
- Procedencia: MINIRONIN-author-original; el manifiesto del ciclo registra bytes y SHA-256.

La siguiente expansión añadirá investigación externa y fuentes abiertas con su licencia comprobada. Las páginas de AI Now, EFF, OECD y la Comisión Europea se conservan primero como referencias; no se copian íntegramente hasta confirmar sus condiciones de reutilización. Los conjuntos PrivacyQA/OPP-115 y Privacy Law Corpus figuran como no comerciales o con restricciones específicas y quedan fuera de la mezcla general mientras no exista autorización compatible. El dataset FSDK declara CC BY 4.0 y queda como candidato de adquisición tras verificar el ZIP y sus ficheros.


## Dataset de personalidad factual verificable — 50k

Se añade `minironin-verifiable-personality-50k-v1`, generado por `scripts/build_verifiable_personality_dataset.py`. Contiene 50.000 ejemplos combinatorios en cinco shards gzip, con 40 fichas factuales institucionales sobre metrología SI, regulación digital europea, portabilidad/interoperabilidad y energía de centros de datos e IA.

- Dominio de entrenamiento: `verifiable`, peso inicial 2% antes de normalizar la mezcla.
- Cada ejemplo conserva `fact_id`, fuente, URL y periodo/alcance; las proyecciones se etiquetan como proyecciones, no como observaciones.
- La redacción de preguntas, contextos y respuestas es original; los hechos se parafrasean y atribuyen a BIPM, Comisión Europea, Consejo de la UE e IEA.
- Los 50.000 registros son combinaciones deterministas de 40 fichas, 10 marcos de pregunta, 10 contextos y 15 remates de humor seco. No representan 50.000 hechos independientes ni 50.000 fuentes.
- El objetivo es practicar una voz mordaz que primero conserva el dato y sus límites; el sarcasmo no debe alterar el contenido factual.
- Generación y auditoría aisladas en `.github/workflows/build-verifiable-personality-dataset.yml`; no entrena ni modifica checkpoints.


## Conversational combinator — 10M candidate dialogues

`scripts/build_conversation_mix.py` prepares up to 10,000,000 multi-turn candidate conversations by combining existing structured Q&A seeds with follow-up intents and voice variants. It scans structured `.jsonl`, `.ndjson` and `.jsonl.gz` records in `data/curated`, `data/inherited` and `data/datasets`; raw prose without an existing question/answer pair is deliberately excluded rather than converted into unsupported answers.

- Each conversation retains the seed ID/hash, source, source URL, source file, tag and topic.
- Follow-ups probe evidence, limits, uncertainty, counterarguments and scope; the response must preserve the seed's source status and abstention behavior.
- Output is sharded gzip JSONL under `data/generated/conversation-candidates-v1` by default.
- This 10M corpus is a **candidate only**. It is not included in the training mix and no 10M generation or model training is started automatically. Use `--dry-run` or a small `--target` first, inspect quality, then decide whether to materialize the full set.


## Corpus factual World Bank — 2M ejemplos

`scripts/build_worldbank_verifiable_dataset.py` obtiene observaciones numéricas de World Development Indicators mediante la API v2 oficial del Banco Mundial. Cubre 37 indicadores de población, economía, salud, educación, energía, conectividad, comercio y medioambiente, para países y años entre 1960 y 2025.

- Objetivo: 2.000.000 de ejemplos en shards gzip JSONL de 100.000 registros.
- Unidad factual independiente: combinación país + indicador + año (`fact_id`), no cada paráfrasis.
- Cada fila conserva código ISO3, código y nombre de indicador, año, valor, unidad, estado epistemológico, URL de consulta, nota de fuente y hash del hecho.
- Solo se admiten valores numéricos no nulos; las observaciones marcadas como previsión (`F`) se excluyen. Las observaciones marcadas como estimadas se identifican explícitamente.
- Las preguntas y remates de humor son redacción original; no se añaden causalidades ni conclusiones que los datos no permitan.
- La licencia general por defecto del Banco Mundial es CC BY 4.0, pero algunos conjuntos/indicadores pueden tener avisos o fuentes de terceros. El manifiesto conserva la organización y nota de cada indicador: revisar esas condiciones antes de redistribuir fuera del proyecto.
- El corpus es candidato independiente y **no se incorpora automáticamente al entrenamiento**. Primero se auditan cobertura, calidad, distribución y posibles sesgos.

Workflow aislado: `.github/workflows/build-worldbank-verifiable-dataset.yml`. Genera y audita datos; no ejecuta ningún entrenamiento ni modifica checkpoints.
