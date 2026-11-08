# Mamba 50M: holdout con RAG y continuación de 1.000 pasos

## Punto de partida inmutable

El experimento consume exclusivamente el checkpoint del run 42465812618:

- Artefacto: `minironin-mamba-50m-from-390k`
- Archivo: `mamba-checkpoint-1000.pt`
- SHA-256: `d4e94c6b2711810bc07ce91b9fdcf4cfd50466a6ee9eafe70b64f023f211d5d7`
- Arquitectura: `mamba-selective-scan-v1`
- Parámetros: 49.083.392
- Pasos completados: 1.000

El workflow comprueba SHA-256, arquitectura, pasos, vocabulario activo y número de parámetros antes de inferir o entrenar. No reconstruye el modelo desde el Transformer ni inicializa bloques Mamba nuevos.

## Evaluación antes de entrenar

`scripts/run_mamba_rag_holdout.py` ejecuta las mismas 40 preguntas de `benchmarks/inference-holdout-v1.jsonl`, con SHA-256 `22dce842390cd2075a214cb01e69091baa82b990dfd8a9657c1f1b787d21b06d`.

Para cada pregunta genera dos respuestas con el mismo checkpoint:

1. Sin RAG: prompt original `pregunta + Respuesta:`.
2. Con RAG: recuperación híbrida BM25/E5, pasajes citados `[S1]...`, y la misma pregunta al final del prompt.

El prompt RAG se limita a la ventana real del modelo (512 bytes), reservando espacio para la pregunta. Se guardan las citas, fragmentos, procedencia, licencia, etiqueta epistemológica, advertencias y respuestas crudas. El rubric no entra en el prompt.

La evaluación comprueba la equivalencia del decodificador recurrente antes de generar. Si se pasa `--baseline-diary`, las 40 respuestas sin RAG deben coincidir exactamente con el diario histórico. No se calcula una supuesta precisión semántica automática: los rubrics quedan disponibles para revisión ciega. Las métricas de caracteres solo diagnostican corrupción y repetición.

## Corpus de la continuación

`scripts/continue_mamba_50m.py` carga los pesos del checkpoint anterior con `strict=True` y añade exactamente 1.000 pasos (pasos globales 1.001–2.000).

Incluye:

- El corpus completo que ya consumía el primer entrenamiento: HERETIC, PRODATPHIL v0.3 y los datasets conductuales/abstención/Lexicon materializados desde el repositorio.
- Los fragmentos de bibliotecas RAG `minironin-papers` y `RONIN_IA`, esta última únicamente desde `data/datasets/admitted` y con la procedencia/licencia conservadas en el índice.
- Partición determinista por documento de los fragmentos RAG: 90% entrenamiento y 10% validación, sin separar chunks del mismo documento entre ambos lados.
- Validación existente del corpus original más ventanas de validación de las bibliotecas añadidas.

No se vuelve a inyectar `minironin-curated` porque sus datasets canónicos ya se cargan desde los JSONL de entrenamiento. `RONIN_IA_RIGHTS` nunca es texto de entrenamiento. `minironin-books` queda fuera de esta ampliación mientras su raíz solo declare catálogo/fuentes y no obras adquiridas con permiso de entrenamiento verificado; PRODATPHIL v0.3 sí se carga desde su paquete público de dominio público.

La continuación usa batch 1, secuencia de 64 bytes, semilla fija y LR máximo `2e-5` con warmup/coseno. El checkpoint inicial no guardó el estado de AdamW: se conservan exactamente los pesos, pero el optimizador se reinicia y queda declarado en el manifiesto. Se escriben checkpoints intermedios cada 250 pasos y el final `mamba-checkpoint-2000.pt`.

## Automatización

`.github/workflows/mamba-rag-continuation.yml` se dispara cuando termina correctamente `Build complete MINIRONIN RAG index` en `main`. También admite ejecución manual indicando el run ID que publicó `minironin-complete-rag-index`.

Secuencia:

1. Descargar y verificar el checkpoint Mamba de 1.000 pasos.
2. Descargar y verificar el índice RAG y su manifiesto; exigir `holdout_read=false`.
3. Ejecutar holdout 40 antes de entrenar, con y sin RAG.
4. Descargar y verificar HERETIC y PRODATPHIL.
5. Entrenar exactamente 1.000 pasos adicionales desde los pesos de Mamba 1.000.
6. Repetir el holdout 40 con el checkpoint de 2.000 pasos y el mismo índice RAG.
7. Publicar el artefacto `minironin-mamba-50m-2000-rag-continuation` y registrar ambos diarios.

El workflow no promueve ni sustituye `main` por el checkpoint nuevo. La decisión queda pendiente de comparar las respuestas crudas y revisar el holdout.
