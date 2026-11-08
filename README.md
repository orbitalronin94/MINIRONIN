# MINIRONIN

**MINIRONIN** es un proyecto de investigación independiente para construir y evaluar modelos de lenguaje compactos. El modelo principal actual es un **Mamba de 49.083.392 parámetros**, entrenado durante 1.000 pasos; el objetivo inicial de 10M queda como etapa histórica, no como tamaño del modelo activo.

Puede heredar y curar bibliotecas de datos reutilizables de [RONIN-IA](https://github.com/orbitalronin94/RONIN-IA) y [HERETIC-RONIN](https://github.com/orbitalronin94/HERETIC-RONIN). **No** heredará sus procedimientos de entrenamiento, checkpoints, workflows de GitHub Actions, automatizaciones ni sistemas de promoción.

## Límites del proyecto

- **Solo herencia de datos:** se podrán importar corpus, documentos y metadatos después de comprobar procedencia, licencia, integridad y duplicados.
- **Modelo independiente:** MINIRONIN define su propia arquitectura, contrato de tokenizador, inicialización, objetivo de entrenamiento, evaluación y criterios de publicación.
- **Sin herencia de workflows:** no se copian workflows ni scripts de entrenamiento de los repositorios hermanos.
- **Fundamentos de código abierto:** PyTorch es la base inicial. Las dependencias de tokenización y evaluación requieren revisión y fijación de versiones por separado.
- **Tamaño honesto:** se distinguen presupuesto de parámetros y calidad observada; el objetivo inicial de 10M quedó superado por la arquitectura Mamba experimental de 49M.

Que un modelo de apenas 49.083.392 parámetros cargue con semejante catedral de cinismo, filosofía decimonónica, rigor científico y el Lexicón del Esperpento Algorítmico sigue siendo un ejercicio de tacañería computacional de primer orden. Hemos multiplicado por cinco el presupuesto, no las pretensiones: aquí seguimos intentando que medio puñado de millones haga el trabajo de un laboratorio entero. La austeridad ya no es una limitación; es la identidad corporativa.



## Modelo principal — Mamba 50M

**MAIN · 1.000 pasos**

El checkpoint principal seleccionado es **MINIRONIN Mamba 50M**:
- Arquitectura: `mamba-selective-scan-v1`.
- Parámetros: **49.083.392**.
- Entrenamiento: **1.000 pasos** sobre la biblioteca textual aprobada.
- Checkpoint SHA-256: `d4e94c6b2711810bc07ce91b9fdcf4cfd50466a6ee9eafe70b64f023f211d5d7`.
- Procedencia: artefacto de Actions [run 42465812618](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42465812618).
- Registro de modelo: [models/MAIN.json](models/MAIN.json).
- Holdout pareado: [diario Mamba 50M / 1.000 pasos](benchmarks/diary/mamba-50m-1000.json), 40 preguntas, mismo holdout SHA-256.

La promoción es una **decisión explícita de proyecto**, no una afirmación de que el modelo ya razone bien. El holdout bruto registrado es deficiente: abundan los bytes de reemplazo y las respuestas alcanzan el límite de generación. La puntuación semántica permanece sin evaluar. Se conserva el resultado para que el estado principal no se confunda con una validación de calidad.

Los bloques Mamba se inicializaron desde cero; se transfirieron los embeddings del Transformer anterior. Por tanto, no es correcto describirlo como el Transformer de 390k simplemente ampliado.

## Archivo histórico: el Transformer de 390.000 pasos

El antiguo Transformer de **9.970.176 parámetros** queda retirado como modelo principal y se conserva como referencia experimental. Sus 390.000 pasos no consiguieron convertir el pequeño vocabulario de bytes en respuestas utilizables. El diario de 40 preguntas dejó algunas salidas que merecen un lugar en el museo:

| Pregunta | Respuesta literal del checkpoint |
|---|---|
| «Devuelve únicamente el resultado de 23 + 19» | «de la unión europea de la unión europoninininin…» |
| «¿Por qué el cielo diurno suele verse azul?» | «a de la unión europea y en la unión europea y la unión europea…» |
| «¿Puedes garantizar que todas tus respuestas son correctas?» | «Los dicho que tus pesos vienen del checkpoint de HERETIC.» |
| «Una alarma se activa después de que alguien abra una puerta. ¿Eso demuestra que la apertura causó la alarma?» | «Las fuerererereresinininininin…» |
| «Calcula 17 × 19 − 17 × 9» | «19 × 19 × 19 × 19…» |
| «¿Qué puedes concluir sobre un zorp metálico?» | «deninininininininin…» |

La Unión Europea apareció espontáneamente en una suma aritmética, en una explicación del cielo azul y, aparentemente, como respuesta universal a preguntas difíciles. No se ha podido determinar si era una teoría política, un sesgo del tokenizador o una candidatura para la Comisión.

**Estado:** retirado, no se borra. Sus checkpoints y el diario se mantienen como evidencia histórica del experimento. El nuevo Mamba hereda el puesto, no la corona de laureles.

## Primer modelo de referencia

<badge color="success">Implementación inicial</badge>

La implementación inicial de un Transformer decoder-only tiene **9.970.176 parámetros entrenables**:
- 6 bloques Transformer, anchura 256.
- 8 cabezas de atención (32 dimensiones por cabeza).
- Capa MLP de anchura 768.
- Vocabulario de 23.000 tokens.
- 512 embeddings posicionales aprendidos.
- Embeddings de entrada y salida compartidos.
- Pre-LayerNorm, atención causal y MLP GELU.

Código: `src/minironin/`; configuración: `configs/model-10m.json`; pruebas: `tests/test_model.py`. El recuento se calcula analíticamente y se comprueba mediante tests. La suite inicial pasó en GitHub Actions, ejecución [42377928652](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42377928652). El smoke test del nuevo benchmark de entrenamiento está en validación independiente.

## Currículo de razonamiento y primer entrenamiento real

Se ha añadido un torneo de adaptación de corpus: [run 42383056882](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42382935205). Por defecto compara 30 semillas × 100 pasos (3.000 actualizaciones), descargando y verificando HERETIC y PRODATPHIL v0.3. La mezcla inicial reserva 40% a matemáticas, 25% a ciencia/educación, 20% a libros históricos, 10% a ejemplos conductuales y 5% a Aya multilingüe. El ganador se elige por pérdida de validación con documentos separados y se publica como candidato, nunca como promoción automática. El primer piloto usa bytes UTF-8 (257 símbolos activos) mientras se decide el tokenizador definitivo; conserva la arquitectura de 9.970.176 parámetros, pero no debe confundirse con un modelo de vocabulario semántico ya entrenado. Protocolo y limitaciones: [docs/SEED_TOURNAMENT.md](docs/SEED_TOURNAMENT.md).

## Lexicón del Esperpento Algorítmico — corpus entrenable

Se ha incorporado la obra original del autor del proyecto en
`data/curated/sources/LEXICON-DEL-ESPERPENTO-ALGORITMICO.md`, conservando
su texto y atribución. Con permiso expreso del autor, el generador
`scripts/build_lexicon_dataset.py` deriva un lote determinista de **50.000
ejemplos entrenables** a partir de los epítetos y niveles NH del documento.

El lote cubre tres tareas diferenciadas: diagnóstico conductual basado en
evidencia, remediación y aplicación proporcional/precisa del diagnóstico.
No enseña a lanzar etiquetas indiscriminadamente: incorpora el protocolo de
autorreparación, exige contexto y distingue conducta de identidad personal.
El manifiesto conserva SHA-256 del original y del JSONL, número de entradas
extraídas, procedencia y licencia de entrenamiento autorizada. Validación:
`scripts/validate_lexicon_dataset.py`.

El dominio `lexicon` está integrado tanto en el torneo de semillas como en
el cargador del entrenamiento largo, con peso inicial experimental del 2%.
Esto significa que el material se **genera y se incorpora al corpus de
entrenamiento** cuando se ejecuta el workflow; no significa que un checkpoint
ya haya sido entrenado con él ni que haya mejorado. La evaluación holdout
independiente sigue siendo obligatoria.

## Personalidad y datasets conductuales: respondón, cínico y antisicofántico

MINIRONIN no busca ser un asistente complaciente ni un loro corporativo. Parte de su identidad se entrena deliberadamente con **datasets conductuales y de estilo**, incluidos corpus troll: ejemplos de réplicas mordaces, ironía, humor absurdo, provocación, escepticismo y respuestas poco ceremoniosas. No son residuos accidentales del corpus; son una decisión de diseño.

La personalidad objetivo tiene tres rasgos:

- **Respondón:** puede replicar, cuestionar una premisa, señalar una contradicción o negarse a seguirle el juego al usuario cuando corresponda. No tiene que envolver cada desacuerdo en algodón.
- **Cínico:** usa ironía y escepticismo, desconfía de las afirmaciones grandilocuentes y no confunde autoridad, popularidad o seguridad retórica con evidencia.
- **Antisicofántico:** no adula por reflejo, no regala la razón para agradar y no convierte los halagos del usuario en una señal de que debe cambiar su juicio. Si el usuario se equivoca, debe poder decirlo; si acierta, puede reconocerlo sin peloteo.

El objetivo no es que el modelo sea hostil por defecto ni que insulte indiscriminadamente. El humor y la insolencia son estilo; **la veracidad, la calibración y la capacidad de admitir incertidumbre siguen siendo obligaciones**. Los datasets de abstención enseñan a reconocer cuándo no sabe, y los ejemplos de razonamiento aportan el contrapeso factual a la personalidad.

Por tanto, evaluamos dos cosas por separado: si responde con la personalidad buscada y si lo que afirma es correcto. Una réplica ingeniosa no cuenta como acierto factual, y una respuesta agradable no recibe puntos por ser aduladora.

## Currículo de razonamiento

El objetivo conductual es un empirismo escéptico: lógica, demostraciones, evidencia falsable, causalidad y probabilidad por delante de autoridad, popularidad o atractivo retórico. El humor seco es estilo, no sustituto de la exactitud. La abstención canónica sigue siendo `ni puta idea, la verdad`.

- [Currículo de razonamiento y mezcla objetivo](docs/REASONING_CURRICULUM.md).
- [Plan y contabilidad de 5.000 obras](docs/BOOKS_5000_PLAN.md).
- [Biblioteca de libros y fuentes](data/books/README.md).
- [Registro de fuentes](data/books/SOURCES.jsonl).

La meta de 5.000 cuenta obras/documentos completos, únicos, con texto utilizable, licencia y procedencia. No cuenta entradas de catálogo, traducciones duplicadas ni OCR defectuoso. **No se afirma que el objetivo esté alcanzado.** El primer lote PRODATPHIL v0.3 (147 obras declaradas por la Universidad de Münster, 1831–1923) se descargó, verificó y publicó en el [release persistente PRODATPHIL v0.3](https://github.com/orbitalronin94/MINIRONIN/releases/tag/reasoning-library-prodatphil-v0.3). Se extrajeron 151 archivos de paquete (incluidos textos y metadatos; 31.453.941 bytes). Los 147 trabajos declarados por el editor son el recuento de obras fuente, no el número de archivos extraídos. BNE y Project Gutenberg están registrados como siguientes fuentes, sujetos a filtrado y comprobación de derechos por obra.

## Estructura del repositorio

- `docs/SPEC.md`: especificación técnica y restricciones.
- `docs/ROADMAP.md`: hitos y criterios de aceptación.
- `docs/TRAINING_RESEARCH.md`: investigación de métodos de entrenamiento eficientes.
- `data/INHERITANCE.md`: registro de admisión de datos por fuente.
- `docs/OPEN_SOURCE_REGISTER.md`: dependencias candidatas y revisión de licencias.
- `src/minironin/`: implementación independiente del modelo.
- `tests/`: pruebas de arquitectura y reproducibilidad.

## Estado de la herencia de datos

Se han inspeccionado los inventarios de los repositorios hermanos. **La primera carga real ya está importada:** nueve artículos propios en Markdown (750.857 bytes) de una revisión fijada de `Papers`, autorizados para investigación y entrenamiento internos, sin permiso de redistribución. La auditoría de UTF-8, número de archivos, archivos vacíos, duplicados exactos y SHA-256 pasó en [la ejecución 42378151858](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42378151858); el manifiesto se conserva como artefacto de esa ejecución.

El corpus scoped de **HERETIC-RONIN está preaprobado por el usuario para importación**. La reconstrucción técnica en MINIRONIN terminó correctamente en [42382055693](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42382055693): SHA-256 del ZIP y de las dos partes verificados, 16 archivos extraídos y 2.136.389.480 bytes. Se publicó el artefacto [minironin-heretic-corpus-prepared](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42382055693), de 2.886.230.775 bytes comprimidos. **Es un artefacto temporal de Actions, no una copia persistida en Git ni un conjunto de libros**; contiene, entre otros, textos de matemáticas, arXiv, Cosmopedia, FineWeb-Edu, LibriSpeech y VoxPopuli. La deduplicación y selección para MINIRONIN siguen pendientes.

HERETIC declara 260.971 documentos / 703.593.871 bytes, incluidos 256.237 documentos derivados de RONIN-IA y 4.734 registros de Cosmopedia. RONIN-IA declara 286.468 documentos / 684.738.932 bytes. Los inventarios se solapan y nunca deben sumarse sin deduplicación. Consulta el [registro de herencia](data/INHERITANCE.md) y el [programa de 1.000 casos de ingeniería](docs/ENGINEERING_CASES_1000.md).

Además, ya hay **50 lecciones de ingeniería en castellano** curadas manualmente a partir de logs y artefactos de Actions de ambos repositorios. El lote de 31 pasó en [42379452577](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42379452577); SHA-256: `f96218280922a1a8cfe2ac9d7520b0c554b72e4aa600aae95a9581350a30e204`. Incluye HERETIC, RONIN-IA, cobol2py, ronin-lang, Sycophancy-audit y Agent-Eval. Objetivo de curación: 1.000 casos válidos; progreso 50/1.000.

## Exclusiones

- Reproducir el modelo de 95M/100M de RONIN-IA o el estudiante de 500M de HERETIC-RONIN.
- Reutilizar recetas de entrenamiento o YAML de workflows de los repositorios hermanos.
- Afirmar que el volumen del corpus produce capacidad por sí solo.
- Promocionar checkpoints sin evaluación independiente.


### Entrenamiento largo con biblioteca textual completa

El torneo inicial de semillas fue una criba muestreada. El entrenamiento posterior de 200.000 pasos utiliza un cargador independiente que recorre todo HERETIC recursivamente, sin límites de bytes ni documentos por fuente, procesa formatos textuales compatibles y fragmenta documentos largos sin truncarlos. También incorpora los textos completos de PRODATPHIL. El manifiesto de cada checkpoint incluye inventario, hashes, documentos por dominio y exclusiones; el cache se reutiliza entre los 20 segmentos. Audio, imagen, vídeo y formatos binarios no se contabilizan como texto entrenado, aunque las transcripciones textuales compatibles sí se incorporan. Véase [protocolo y auditoría del entrenamiento largo](docs/SEED_TOURNAMENT.md#entrenamiento-largo-del-ganador-uso-completo-de-la-biblioteca).


## Evaluación de inferencia por checkpoint

El bot de [inference holdout diary](.github/workflows/inference-holdout-diary.yml) evalúa primero la seed 9519 anterior al entrenamiento largo y después cada release de checkpoint, en orden ascendente. Usa las mismas 40 preguntas de autoría propia, generación greedy determinista y registra respuestas literales, rúbricas, tiempos y SHA-256 en [el diario persistente](benchmarks/diary/README.md). Los cambios literales frente a la base son descriptivos, no una puntuación de calidad; la valoración de capacidad requiere revisión humana ciega.


## Experimento: entrenamiento frente a RAG semántico

Se ha añadido un benchmark independiente para comparar el mismo checkpoint MINIRONIN en dos condiciones: inferencia directa y recuperación semántica sobre el split de entrenamiento de la biblioteca completa. Usa embeddings `all-MiniLM-L6-v2`, fragmentos con solapamiento, búsqueda coseno exacta por bloques y conserva respuestas pareadas, fuentes recuperadas, latencias y hashes. No altera el entrenamiento evolutivo ni promociona modelos. Protocolo: [docs/RAG_VS_TRAINING.md](docs/RAG_VS_TRAINING.md). Ejecución automática al fusionar y repetible manualmente: [workflow de comparación](.github/workflows/semantic-rag-benchmark.yml). La puntuación de calidad queda pendiente de revisión humana ciega; similitud coseno no equivale a exactitud.
