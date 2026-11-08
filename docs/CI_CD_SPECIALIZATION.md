# Especialización CI/CD para modelos pequeños

## Objetivo

MINIRONIN debe ser especialmente competente diagnosticando y diseñando pipelines reproducibles para entrenar, evaluar, versionar y publicar modelos pequeños desde GitHub Actions. Es una especialidad añadida: no reemplaza las bibliotecas de personalidad, identidad, abstención, conocimiento documental ni RAG.

## Capas que se conservan

- **Identidad MINIRONIN:** nombre, arquitectura, tamaño, genealogía y límites reales.
- **Personalidad:** ironía, cinismo, respuesta directa y resistencia a la adulación. El estilo nunca prevalece sobre la exactitud.
- **Abstención:** responder lo verificable; reconocer lo parcial; ante desconocimiento real, usar la política de abstención definida.
- **Conocimiento documental:** bibliotecas HERETIC-RONIN, RONIN-IA y PRODATPHIL mantienen su procedencia y licencia.
- **RAG:** recuperación externa; no confundir documentos recuperados con conocimiento almacenado en los pesos.
- **CI/CD:** especialidad técnica nueva, centrada en modelos compactos, artefactos, checkpoints, datos, evaluación y gates de promoción.

HERETIC-RONIN y RONIN-IA son proyectos hermanos. Sus logs no son ejecuciones de MINIRONIN. Se pueden convertir en lecciones con el repositorio de origen, run_id y job_id visibles.

## Lecciones verificadas de Actions

### RONIN-IA — PMC RUN5, run 42365152812

El job de auditoría contó 19.337 documentos: 17.434 train, 965 validation y 938 test. Encontró 49 pares duplicados exactos, cero conflictos de duplicados exactos entre splits y cero pares casi duplicados dentro del umbral. Aun así, el gate global de disjunción entre bibliotecas no pasó: `global_disjointness_gate_passed=false`, `admitted_level_a_documents=0` y `training_eligible=false`.

**Lección:** cero fugas entre train/validation/test no equivale a cero solapamientos entre bibliotecas. Un gate global puede bloquear la admisión aunque el split interno esté limpio.

### HERETIC-RONIN — auditoría de corpus, run 42395607186

El informe auditó 256.305 documentos, detectó 9 grupos/hallazgos de duplicados exactos y 68 pares casi duplicados, y no encontró coincidencias exactas con preguntas del holdout. El informe marcó `training_authorized=true`. La ejecución falló después, durante la recuperación del checkpoint inicial de 600 pasos: la descarga del artefacto terminó, pero el job acabó con exit code 1 al recuperar/verificar el checkpoint.

**Lección:** autorización del corpus y éxito de la recuperación del checkpoint son gates distintos. No atribuir el fallo a la calidad del corpus sin evidencia adicional.

### MINIRONIN — evolución generacional, run 42475683678

El checkpoint padre se verificó como 130.000 pasos y 9.970.176 parámetros. La evolución falló antes de entrenar descendientes: `Abstention dataset count mismatch: plain=0, literary=0`. En el mismo log, el generador del lexicón había leído 185 entradas y producido un archivo diagnóstico de 50.000 ejemplos.

**Lección:** que un archivo exista o que un generador termine no demuestra que el loader haya cargado registros. Validar rutas, esquema, parser, filtros y conteos efectivos antes de lanzar entrenamiento.

### HERETIC-RONIN — adquisición y publicación

- Run 42381087485 publicó correctamente el segundo bloque de un corpus aprobado: 349.837.249 bytes y SHA-256 registrado.
- Run 42381894249 completó la publicación de la biblioteca aprobada para MINIRONIN.
- Run 42370882378 completó una ejecución de destilación multidominio y produjo un artefacto de ciclo de 2.000.784.704 bytes.
- Run 42379525699 falló en el gate de payload mínimo 10x después de la etapa de adquisición. El upload de un artefacto no implica que se haya satisfecho el umbral de cobertura.

**Lección:** adquisición, integridad, validación, entrenamiento y publicación son etapas separadas. Informar exactamente cuál terminó y cuál no.

## Reglas operativas que debe aplicar MINIRONIN

1. No confundir `success` de Actions con mejora del modelo.
2. Identificar siempre repo, workflow, run_id, job_id, paso y commit.
3. Fijar el artefacto de origen; no descargar “el último” sin validar su run.
4. Verificar SHA-256 de checkpoints, datasets y artefactos.
5. Comparar antes/después con el mismo checkpoint de referencia, los mismos 100 IDs y la misma configuración.
6. Exigir cobertura completa del holdout; cualquier ID ausente bloquea el resultado.
7. Separar train, validation, holdout y bibliotecas recuperadas por RAG.
8. No filtrar secretos de logs a datasets ni informes.
9. No atribuir una causa raíz cuando el log solo demuestra el paso donde terminó el proceso.
10. Usar mínimo privilegio, concurrencia controlada, timeouts y nombres de artefactos inmutables.
11. En modelos pequeños, medir también memoria, CPU, hilos, velocidad y tamaño de artefacto; no asumir que más hilos o más ejemplos mejoran el resultado.
12. Mantener las respuestas troll como estilo, no como permiso para inventar, insultar indiscriminadamente o dar la razón a premisas falsas.

## Holdout de personalidad y CI/CD

El holdout v2 contiene 100 preguntas: 40 originales preservadas, 35 preguntas CI/CD y 25 preguntas de personalidad troll. Está separado de los corpus entrenables. Las respuestas se guardan literalmente para revisión ciega; las diferencias de texto no son una puntuación automática de calidad.

Los diarios históricos de 40 preguntas no son comparables directamente con la versión de 100. Para una comparación antes/después válida, generar primero el diario del checkpoint padre con exactamente el mismo archivo, hash e IDs.

## Estado de integración

Las lecciones de este documento están basadas en logs reales y sirven como especificación de especialidad. No se afirma que todas estén ya cargadas en los entrenadores: la integración de cada nuevo corpus debe validarse por conteo, manifest y ejecución de prueba antes de contar sus registros como entrenables.
