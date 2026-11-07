# MINIRONIN

**MINIRONIN** es un proyecto de investigación independiente cuyo objetivo es construir un modelo de lenguaje compacto de aproximadamente **10 millones de parámetros**.

Puede heredar y curar bibliotecas de datos reutilizables de [RONIN-IA](https://github.com/orbitalronin94/RONIN-IA) y [HERETIC-RONIN](https://github.com/orbitalronin94/HERETIC-RONIN). **No** heredará sus procedimientos de entrenamiento, checkpoints, workflows de GitHub Actions, automatizaciones ni sistemas de promoción.

## Límites del proyecto

- **Solo herencia de datos:** se podrán importar corpus, documentos y metadatos después de comprobar procedencia, licencia, integridad y duplicados.
- **Modelo independiente:** MINIRONIN define su propia arquitectura, contrato de tokenizador, inicialización, objetivo de entrenamiento, evaluación y criterios de publicación.
- **Sin herencia de workflows:** no se copian workflows ni scripts de entrenamiento de los repositorios hermanos.
- **Fundamentos de código abierto:** PyTorch es la base inicial. Las dependencias de tokenización y evaluación requieren revisión y fijación de versiones por separado.
- **Tamaño honesto:** el objetivo de 10M es un presupuesto de parámetros, no una afirmación de rendimiento.

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
