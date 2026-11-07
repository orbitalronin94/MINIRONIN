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

El corpus scoped de **HERETIC-RONIN está preaprobado por el usuario para importación**, sin repetir la revisión manual de admisión. La copia física y deduplicación cruzada aún están pendientes. HERETIC declara 260.971 documentos / 703.593.871 bytes, incluidos 256.237 documentos derivados de RONIN-IA y 4.734 registros de Cosmopedia. RONIN-IA declara 286.468 documentos / 684.738.932 bytes. Los inventarios se solapan y nunca deben sumarse sin deduplicación. Consulta el [registro de herencia](data/INHERITANCE.md) y el [programa de 1.000 casos de ingeniería](docs/ENGINEERING_CASES_1000.md).

Además, ya hay **31 lecciones de ingeniería en castellano** curadas manualmente a partir de logs y artefactos de Actions de ambos repositorios. El lote de 31 pasó en [42379452577](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42379452577); SHA-256: `f96218280922a1a8cfe2ac9d7520b0c554b72e4aa600aae95a9581350a30e204`. Incluye HERETIC, RONIN-IA, cobol2py, ronin-lang, Sycophancy-audit y Agent-Eval. Objetivo de curación: 1.000 casos válidos; progreso 31/1.000.

## Exclusiones

- Reproducir el modelo de 95M/100M de RONIN-IA o el estudiante de 500M de HERETIC-RONIN.
- Reutilizar recetas de entrenamiento o YAML de workflows de los repositorios hermanos.
- Afirmar que el volumen del corpus produce capacidad por sí solo.
- Promocionar checkpoints sin evaluación independiente.
