# PleIAs Common Corpus — intake español

- Dataset: https://huggingface.co/datasets/PleIAs/common_corpus
- Tamaño global declarado: 2,27 billones de tokens; el castellano supera 10.000 millones de tokens entre los idiomas principales.
- El corpus conserva metadatos por documento: identificador, colección, tipo de apertura, licencia, fecha, título, creador, idioma y texto.
- Decisión de admisión: solo castellano y subcolecciones OpenScience, OpenGovernment y OpenSemantic.
- Derechos: filtro estricto por registro a dominio público, PDM, CC0 o CC BY de atribución únicamente. Excluye CC-BY-SA, NC, ND y licencias desconocidas.
- Primera tanda: 10 Parquet shards del directorio `common_corpus_1`, procesados en paralelo; los recuentos reales se publican por shard.
- Se excluyen OpenCulture y OpenWeb para evitar duplicación con PleIAs Spanish-PD-Books y Wikimedia ES; se excluye OpenSource por no ser prioritario para el modelo de lenguaje.
- Los JSONL se publican como assets versionados de release, nunca como ficheros gigantes en Git.
- La deduplicación exacta se aplica contra el corpus existente y dentro de cada shard; el builder registra los duplicados entre shards.
