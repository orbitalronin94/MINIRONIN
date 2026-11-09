# MINIRONIN Integrated Evidence Stack (MIES)

**Estado:** integración experimental en PR #35; CI de integración verde (15 pruebas). La preparación del artefacto y el holdout emparejado siguen pendientes. No se ha entrenado ni promovido ningún checkpoint.

## Componentes

1. **Inventario canónico:** `scripts/import_admitted_sources.py` importa exclusivamente particiones train con manifiestos y hashes verificables de RONIN-IA, documentos propios de Papers y datasets curados internos. `scripts/build_library_manifest.py` valida derechos, admisión, hashes, rutas y exclusiones, y genera `documents.jsonl` como snapshot común.
2. **RAG literal:** `scripts/build_rag_index.py` crea SQLite + FTS5/BM25 y embeddings multilingües opcionales. `scripts/rag_retrieve.py` ofrece recuperación híbrida, fusión RRF y contexto con citas.
3. **Filas despiertas:** `scripts/build_awake_rows.py` genera ejemplos extractivos/citados y QA curado a partir del mismo inventario, manteniendo documento de origen y hashes.
4. **BACKDOOR_BPE:** `scripts/build_backdoor_bpe.py` aprende n-gramas de bytes únicamente del split train; `src/minironin/tokenizer.py` conserva fallback de bytes, longest-match determinista y EOS=256.
5. **Entrenamiento compatible:** `scripts/train_backdoor_bpe_continuation.py` puede continuar un checkpoint byte-level, inicializar filas nuevas desde sus bytes constituyentes, preservar filas antiguas y limpiar momentos del optimizador solo para filas nuevas.
6. **Inferencia compatible:** `scripts/run_inference_holdout.py --tokenizer` requiere el mismo hash de tokenizador que declara el checkpoint y limita logits al vocabulario activo. Con `--rag-index`, recupera evidencia, ajusta el contexto al límite real de bytes del modelo, incluye marcadores [S#] y registra qué fragmentos llegaron al prompt, hits, hashes y advertencias.

## Flujo reproducible

El workflow `.github/workflows/prepare-integrated-evidence-stack.yml` prepara el inventario, filas despiertas, candidato BACKDOOR_BPE e índice RAG, valida sus contratos y publica `minironin-integrated-evidence-stack`. La CI específica valida los componentes en la rama de integración. El workflow de preparación se ejecuta en `main` tras cambios en sus componentes o por lanzamiento manual.

Si la preparación en `main` termina correctamente, `.github/workflows/holdout-integrated-810k.yml` descarga el artefacto exacto y ejecuta dos inferencias emparejadas sobre el mismo checkpoint 810k: baseline sin RAG y 810k + RAG. Comprueba SHA-256 del checkpoint, `completed_steps=810000`, los 100 IDs del holdout, SHA-256 del holdout y configuración de generación idéntica. Publica ambas respuestas y el diario comparativo. **No entrena ni cambia pesos.**

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

El corpus HERETIC entra únicamente mediante su importador específico, con manifiesto de curación, revisión fijada, SHA-256 y auditoría global de autorización. La cobertura efectiva se determina por el informe de importación y el manifiesto final del workflow.

La generación de filas despiertas actual es conservadora: aprovecha QA marcado como verificado/curado y, en ausencia de QA, genera ejercicios de copia literal. No inventa respuestas factuales a partir de similitud semántica.

## Validación pendiente

- Completar el workflow de preparación y revisar el artefacto real, las fuentes, las exclusiones y la distribución por dominio.
- Medir ahorro real de BACKDOOR_BPE, BPB, EOS y regresiones antes de cualquier continuación.
- Ejecutar el holdout emparejado 810k byte-level sin RAG / con RAG; el candidato BACKDOOR_BPE no se conecta al checkpoint 810k porque sus pesos no contienen esas filas.
- Si BACKDOOR_BPE demuestra utilidad, entrenar una continuación separada, guardar el nuevo checkpoint y hash de tokenizador y evaluarla con su propio holdout emparejado.
- Solo después del holdout completo y revisión ciega se decidirá cualquier promoción.

La nota de investigación y SOTA está en el repositorio Papers: `MINIRONIN-enano-arquitectura-integrada-BACKDOOR-BPE-RAG.md`.
