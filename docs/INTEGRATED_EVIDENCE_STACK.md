# MINIRONIN Integrated Evidence Stack (MIES)

**Estado:** implementación experimental en rama; no activada en un checkpoint y sin holdout ejecutado.

## Componentes

1. **Inventario canónico:** `scripts/import_admitted_sources.py` importa exclusivamente particiones train con manifiestos y hashes verificables de RONIN-IA, documentos propios de Papers y datasets curados internos. `scripts/build_library_manifest.py` valida derechos, admisión, hashes, rutas y exclusiones, y genera `documents.jsonl` como snapshot común.
2. **RAG literal:** `scripts/build_rag_index.py` crea SQLite + FTS5/BM25 y embeddings multilingües opcionales. `scripts/rag_retrieve.py` ofrece recuperación híbrida, fusión RRF y contexto con citas.
3. **Filas despiertas:** `scripts/build_awake_rows.py` genera ejemplos extractivos/citados y QA curado a partir del mismo inventario, manteniendo documento de origen y hashes.
4. **BACKDOOR_BPE:** `scripts/build_backdoor_bpe.py` aprende n-gramas de bytes únicamente del split train; `src/minironin/tokenizer.py` conserva fallback de bytes, longest-match determinista y EOS=256.
5. **Entrenamiento compatible:** `scripts/train_backdoor_bpe_continuation.py` puede continuar un checkpoint byte-level, inicializar filas nuevas desde sus bytes constituyentes, preservar filas antiguas y limpiar momentos del optimizador solo para filas nuevas.
6. **Inferencia compatible:** `scripts/run_inference_holdout.py --tokenizer` requiere el mismo hash de tokenizador que declara el checkpoint y limita logits al vocabulario activo.

## Flujo reproducible

El workflow manual `.github/workflows/prepare-integrated-evidence-stack.yml` prepara el inventario, filas despiertas, tokenizador e índice RAG y publica el artefacto `minironin-integrated-evidence-stack`.

**Este workflow no entrena ni ejecuta holdout.** No hay disparadores automáticos de continuación o evaluación. La activación de un entrenamiento y el holdout real son fases posteriores que requieren que el artefacto esté verificado y que todas las piezas estén conectadas al checkpoint elegido.

## Contratos y protecciones

- IDs byte 0–255 y EOS 256 no se reasignan.
- IDs nuevos se añaden desde 257; tokenizador versionado y hash por checkpoint.
- Tokenización lossless y fallback byte universal.
- Embeddings de entrada/salida siguen atados.
- RAG y entrenamiento derivan del mismo snapshot documental; train/validation son particiones por documento.
- Solo se admiten documentos con estado explícito admitted, rights_status permitido y SHA-256 verificado.
- Holdout, validación reservada, benchmarks, cuarentena, candidatos, checkpoints y logs quedan excluidos.
- Los documentos sin licencia o manifiesto de admisión verificable no entran silenciosamente.
- Los resultados sintéticos se etiquetan; las filas QA solo se generan desde registros curados/verificados. El resto se limita a tareas de copia extractiva.
- Ningún cambio de tokenizer se compara contra el régimen anterior sin BPB y métricas de tarea emparejadas.

## Alcance actual y límites

El importador incorpora los payloads de RONIN-IA solo cuando encuentra un archivo de partición train cuyo SHA-256 coincide exactamente con el manifiesto scoped-admitted. También incorpora los documentos Markdown propios de Papers y una allow-list de JSONL curados de MINIRONIN.

El corpus HERETIC externo todavía requiere un importador específico de su manifiesto de corpus y verificación de artefacto. No se afirma que esté incluido por el mero hecho de que exista una carpeta o un artefacto histórico. La cobertura efectiva se determina por el informe de importación y el manifiesto final del workflow.

La generación de filas despiertas actual es conservadora: aprovecha QA marcado como verificado/curado y, en ausencia de QA, genera ejercicios de copia literal. No inventa respuestas factuales a partir de similitud semántica.

## Validación pendiente

- Ejecutar el workflow manual y revisar el informe de fuentes admitidas/omitidas.
- Confirmar que el índice incluye cada biblioteca esperada y ninguna partición reservada.
- Inspeccionar distribución de filas despiertas por dominio, tarea y procedencia.
- Medir ahorro real de BACKDOOR_BPE, BPB, EOS y regresiones.
- Validar el adaptador RAG en preguntas sintéticas separadas del holdout.
- Solo entonces conectar el artefacto a la continuación del checkpoint y, después de activarlo todo, ejecutar el holdout emparejado.

La nota de investigación y SOTA está en el repositorio Papers: `MINIRONIN-enano-arquitectura-integrada-BACKDOOR-BPE-RAG.md`.
