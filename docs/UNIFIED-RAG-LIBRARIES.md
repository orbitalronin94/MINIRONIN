# MINIRONIN — RAG unificado de bibliotecas

## Objetivo

Construir un índice documental externo que permita consultar **todas las bibliotecas admitidas** por MINIRONIN sin convertir cada documento en conocimiento paramétrico. El índice será independiente de Transformer, Mamba y futuras arquitecturas.

RAG no significa que el modelo lleve todos los documentos dentro de sus pesos. Significa que un recuperador busca fragmentos relevantes y los entrega al modelo como contexto en cada consulta. El modelo conserva en sus pesos las capacidades generales, el criterio, la personalidad y los procedimientos; el índice conserva el conocimiento documental actualizable y citable.

## Arquitectura objetivo

```text
Bibliotecas y fuentes admitidas
        |
        v
Registro de fuentes + manifiestos + hashes/licencias
        |
        v
Extracción de texto -> normalización -> deduplicación
        |
        v
Fragmentación con contexto y metadatos de procedencia
        |
        +--------------------------+
        |                          |
        v                          v
Embeddings multilingües       Índice léxico (BM25)
        |                          |
        +------------+-------------+
                     v
            Recuperación híbrida
                     |
              deduplicación/
              diversidad por fuente
                     |
              reranking opcional
                     |
              presupuesto de contexto
                     |
          Adaptador de prompt del modelo
                     |
       Transformer / Mamba / futura arquitectura
                     |
        respuesta + citas de fragmentos
```

El índice y el protocolo de recuperación no dependen del tipo de red. Cada arquitectura solo necesita un adaptador pequeño que convierta los fragmentos recuperados en contexto.

## Fuentes previstas

El índice se construirá desde el registro de herencia y los manifiestos reales, no desde una lista de directorios asumida. Familias iniciales:

- HERETIC-RONIN, conservando las etiquetas de corpus sintético, educativo, literatura, ciencia y demás procedencias.
- PRODATPHIL y otras obras/libros admitidos.
- Solo particiones train scoped dentro de `RONIN-IA/data/datasets/admitted/`, más `rights_registry/` para procedencia y licencias. Se excluyen expresamente `candidates/`, `quarantine/`, `reviews/` y `libraries/` (catálogo objetivo de 64 bibliotecas); G-0 global sigue FAIL y una admisión scoped no equivale a una aprobación global.
- Papers propios y documentos de investigación con permiso de uso interno.
- Fuentes factuales estructuradas, por ejemplo World Development Indicators, cuando sus shards/manifiestos estén materializados y auditados; conservar país, indicador, año, unidad y estado de estimación. Actualmente no se incluyen shards World Bank porque no están persistidos en esta rama.
- Datasets conductuales, abstención, personalidad, lexicón y casos de ingeniería de MINIRONIN.
- Documentación técnica y bibliotecas futuras que superen el registro de admisión.

No sumar recuentos de HERETIC y RONIN-IA: existe solapamiento documentado. La identidad del contenido se resuelve mediante hashes exactos y huellas de casi duplicados, manteniendo todas las procedencias asociadas a un mismo documento.

## Fuentes que nunca entran automáticamente

- Holdouts, validación reservada, rúbricas privadas o respuestas esperadas.
- Checkpoints, estados de optimizador, pesos, volcados binarios.
- Tokens, secretos, credenciales, datos personales o rutas privadas.
- Workflows, configuración CI y logs operativos brutos.
- Fuentes sin licencia/procedencia registrada o fuera del permiso de uso.
- Salidas de modelos no verificadas presentadas como hechos.

Los logs solo pueden entrar como lecciones de ingeniería curadas y con evidencia, no como logs brutos. El contenido sintético debe conservar una etiqueta explícita y no se debe mostrar como evidencia factual primaria.

## Esquema de documento y fragmento

Cada fragmento debe conservar como mínimo:

- `chunk_id` estable;
- `document_id` y SHA-256 del documento original;
- texto y hash del fragmento;
- proyecto/repositorio, fuente y ruta relativa;
- URL, revisión o ID de artefacto cuando exista;
- licencia y permiso de uso;
- dominio, idioma y tipo de contenido;
- autor/editor y fecha/periodo, cuando existan;
- número de página/sección/offset, cuando pueda determinarse;
- etiqueta epistemológica: primario, verificado, sintético, autoría propia, curado o estimado;
- versión del extractor, normalizador, fragmentador y modelo de embeddings.

Una misma obra puede tener varias procedencias; no perderlas al deduplicar. Los datos tabulares deben indexarse con sus unidades, etiquetas y claves de observación, no como números desnudos.

## Embeddings y recuperación

El benchmark inicial ya usa `sentence-transformers/all-MiniLM-L6-v2`, pero es un modelo centrado en inglés. Para el índice general multilingüe de MINIRONIN se evaluará `intfloat/multilingual-e5-small` como primera opción CPU (384 dimensiones), frente a un modelo multilingüe alternativo. La elección final se fija por revisión de licencia/revisión upstream, calidad por idioma y dominio, latencia y tamaño de índice.

No se debe confundir:
- vector de documento: representación usada por el buscador;
- embedding de token del LM: parámetro de la red;
- conocimiento paramétrico: información/capacidad aprendida durante entrenamiento.

Los vectores RAG no se copian directamente a la tabla de embeddings del modelo. Son un índice externo. Si más adelante queremos adaptación paramétrica, se hará mediante destilación separada, con objetivos y evaluación propios.

La recuperación prevista es híbrida:
1. búsqueda vectorial semántica;
2. búsqueda léxica BM25 para nombres, fórmulas, identificadores, fechas y términos exactos;
3. fusión de rankings (RRF u otro método validado);
4. diversidad por documento/fuente;
5. reranking opcional, solo si la mejora justifica coste;
6. selección bajo presupuesto de tokens/contexto.

Se evaluará por separado español, inglés y otros idiomas presentes. No se confiará en la similitud coseno como medida de verdad o relevancia suficiente.

## Integración con MINIRONIN

El contrato de recuperación debe ser independiente de la arquitectura:

```python
result = search(index_path, question, k=5)
prompt_context = format_context(result, max_chars=12000)
answer = model_adapter.generate(question, context=prompt_context)
```

El contrato Python actual es `search(index_path, query, k=5, model=None, use_vectors=True)`, que devuelve `hits`, `warnings` y el manifiesto del índice; `format_context(result, max_chars=12000)` crea bloques citables `[S#]` respetando el presupuesto de caracteres. La CLI permite `--format context` y `--no-vector`. El prefijo de consulta E5 se lee del manifiesto del índice, no se vuelve a asumir en el runtime. Los adaptadores de Transformer y Mamba reciben el mismo contexto para que la comparación sea justa. Si el contexto supera la ventana, se seleccionan fragmentos por relevancia y diversidad; no se trunca a ciegas la pregunta ni las citas.

La respuesta debe distinguir:
- afirmaciones apoyadas por los fragmentos;
- inferencias del modelo;
- información no encontrada;
- contradicciones entre fuentes.

Cada afirmación factual recuperada debe poder remitir a una fuente, documento y fragmento. Si no hay evidencia suficiente, se activa la política de abstención de MINIRONIN.

## Evaluación antes de darlo por bueno

Crear un benchmark documental independiente, con preguntas redactadas sin consultar el índice final y relevancia etiquetada por humanos. Separar:
- Recall@k / MRR / nDCG de recuperación;
- exactitud y fidelidad de la respuesta;
- atribución correcta y citas verificables;
- abstención cuando no hay evidencia;
- robustez ante documentos contradictorios o sintéticos;
- contaminación entre índice, entrenamiento y holdout;
- latencia, RAM y tamaño del índice.

Comparar, con el mismo checkpoint y decodificador:
1. sin RAG;
2. RAG vectorial;
3. RAG híbrido;
4. RAG híbrido + reranker, si procede.

La calidad se puntúa a ciegas. Ni el score coseno ni una respuesta distinta cuentan como mejora por sí solos.

## Fases de implementación

1. **Inventario:** reconciliar el registro de herencia, manifests y fuentes reales; identificar formatos y permisos.
2. **Ingesta reproducible:** extracción, normalización, deduplicación, chunking, procedencia y hashes.
3. **Índice vectorial:** embeddings multilingües versionados, almacenamiento compacto y búsqueda por bloques.
4. **Recuperación híbrida:** BM25 + vectores, fusión, diversidad y citas.
5. **Adaptadores de arquitectura:** mismo contrato para Transformer y Mamba.
6. **Benchmark documental:** conjunto de consultas y relevancia independiente, A/B ciego y métricas.
7. **Runtime:** empaquetado descargable/versionado del índice; actualizar bibliotecas sin tocar los pesos.

No lanzar entrenamientos como parte de estas fases. La construcción del índice tampoco debe fusionar automáticamente ningún checkpoint ni modificar el holdout.

## Implementación disponible en la rama feat/checkpoint-bridge

- Registro de fuentes: `data/rag/sources.json`.
- Ingesta SQLite: `scripts/build_rag_index.py`; FTS5/BM25 + embeddings E5 multilingües opcionales.
- Recuperación: `scripts/rag_retrieve.py`; RRF y búsqueda vectorial por lotes con memoria acotada.
- Workflow: `.github/workflows/build-rag-index.yml`; artefacto `minironin-complete-rag-index` con SQLite y manifiesto SHA-256.
- Formatos: Markdown, TXT, RST, JSON/JSONL, JSONL.GZ, CSV/TSV, HTML/XML, PDF y DOCX.
- Metadatos: SHA-256, ruta, línea/página, dominio, idioma, etiqueta epistemológica, licencia y procedencias alternativas; los registros duplicados conservan todas sus ubicaciones.
- Exclusiones: particiones de evaluación, benchmarks, candidatos, cuarentena, checkpoints, secretos y logs brutos.

El workflow incorpora el artefacto HERETIC preaprobado de run 42382055693 y solo las carpetas admitidas/rights_registry de RONIN-IA. Materializa los ocho datasets conductuales y el lexicón antes de indexar. Los datos World Bank y el generador de 10M conversaciones siguen pendientes de materialización; no se simula su presencia.

## Relación con el benchmark existente

`scripts/benchmark_rag_vs_training.py` ya demuestra una comparación directa vs RAG sobre el split de entrenamiento que devuelve `load_training_data`. Es una prueba de concepto útil, pero no es todavía el RAG unificado de todas las bibliotecas: usa el cargador del entrenamiento, un embedding inglés y no cubre por sí sola todo el registro documental ni el contrato de recuperación compartido entre arquitecturas. Se conservará como baseline y se ampliará sin contaminar el holdout.
