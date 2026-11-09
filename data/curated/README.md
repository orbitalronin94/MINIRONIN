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


## Identidad versionada y lectura de GitHub Actions

Se añaden dos bibliotecas supervisadas pequeñas y explícitas, separadas de los corpus de estilo masivo:

- `minironin-identity-v1.jsonl`: **40 registros** de identidad grounded, arquitectura y tamaño actuales, genealogía del checkpoint, límites de capacidad y personalidad subordinada a la evidencia.
- `minironin-engineering-v1.jsonl`: **20 registros nuevos** curados de los runs 42475009211, 42472836694, 42473906951 y 42475009157. Enseñan a distinguir descarga, verificación SHA-256, preparación de corpus, entrenamiento en curso, publicación de checkpoint, indexación RAG y CI.

Ambos conjuntos se cargan en dominios separados (`identity` y `engineering`) con un peso relativo inicial de 0,02 cada uno (aprox. 1,89% efectivo tras normalizar la mezcla completa). No se incorporan logs brutos ni secretos. Los estados de Actions se enseñan como observaciones fechadas: un paso pendiente no es un paso completado, y una publicación no demuestra mejora del modelo.

La ficha anterior que describía el Transformer inicial de 9.970.176 parámetros queda como antecedente histórico. La identidad vigente del checkpoint principal es Mamba, 49.083.392 parámetros, release `minironin-mamba-50m-step-1000-main`.


## Admisión masiva de bibliotecas externas (auditoría 2026-11-09)

El intake externo se organiza en `data/curated/accepted/` para corpus incorporados al árbol versionado y en releases persistentes para shards grandes, siempre acompañados de manifiestos SHA-256. El estado de cada fuente, las licencias y las cifras verificadas se mantienen en [OPEN_FACTUAL_CORPORA.md](OPEN_FACTUAL_CORPORA.md).

**Incremento nuevo verificado en esta tanda:** PleIAs Spanish Public Domain Books, shards 1–8: **9.766 registros** y **1.441.007.073 bytes comprimidos (1,34 GiB)**. Los ocho jobs validaron cada registro como español, elegible y de dominio público, y compararon SHA-256 con el manifiesto; el rebuild unificado terminó correctamente en [run 42701981364](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42701981364).

No se atribuye a este incremento el tamaño acumulado de releases que contienen lotes anteriores. Las cifras de objetivos (por ejemplo, los 37.200 textos previstos de Wikisource o los 100 shards del Common Corpus) permanecen como objetivos hasta que los jobs publiquen sus propios manifiestos verificados. Los datos sintéticos siguen excluidos de la biblioteca factual real.
