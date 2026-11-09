# Nueva línea de expansión — corpus español factual, filosófico y matemático

**Inicio:** 2026-11-09  
**Línea anterior:** `OPEN_COLLECTIONS_INTAKE_2026-11.md` se conserva intacta.  
**Destino:** `data/datasets` mediante ingestión reproducible en GitHub Actions.  
**Estado de este registro:** fuentes localizadas; no confundir catálogo con documentos ya descargados/admitidos.

## Prioridad por volumen y castellano

| Prioridad | Fuente | Tamaño declarado | Contenido | Decisión de ingestión |
|---|---|---:|---|---|
| P0 | TDX Thesis Spanish Corpus (Zenodo 7313149) | 1,6 GB; 246,7 M tokens; 9.790 tesis | Ciencia, ingeniería, humanidades y conocimiento académico en español | **No admitir en entrenamiento comercial/general por ahora.** El README especifica CC BY-NC-SA 4.0 (no CC BY 4.0) y declara que no hubo anonimización. Mantener en cuarentena de investigación; revisar privacidad y compatibilidad antes de cualquier uso. |
| P0 | CSIC Spanish Corpus (Zenodo 7313126) | 146,8 M tokens; 30.929 documentos | Revistas científicas españolas | **No admitir en entrenamiento comercial/general por ahora.** El README especifica CC BY-NC-SA 4.0. Mantener fuera de la mezcla general; solo reconsiderar en una línea no comercial con revisión de derechos y trazabilidad. |
| P1 | Wikimedia Spanish / Wikipedia | Corpus grande; ya existe intake reproducible de 100.000 documentos en el proyecto | Hechos generales, biografías, geografía, historia, ciencia | Reutilizar el adquiridor existente; CC BY-SA/GFDL exige atribución y compartir adaptaciones bajo términos compatibles. No contar como fuente editorialmente verificada. |
| P1 | Common Corpus (PleIAs) — subconjunto español | Multilingüe, escala de billones de tokens global | Libros, prensa, ciencia, gobierno y patrimonio | Filtrar estrictamente `language=es` y licencia por documento; no descargar el corpus global ni asumir que todo es castellano. |
| P1 | FineWeb-2 — `spa_Latn` | 441.287.261 documentos; 1,32 TB UTF-8 según tabla publicada | Web española global deduplicada y filtrada | Fuente masiva de segundo nivel. Usar solo shards españoles y aplicar filtro propio de calidad, licencias/procedencia y deduplicación. |
| P1 | Spanish 3 Billion Words Corpora (josecannete/spanish-corpora) | 300,9 M líneas; 2,996 B palabras | Wikipedia, ParaCrawl, EUBookshop, MultiUN | No admitir el paquete entero a ciegas: licencias heterogéneas por subcorpus. Separar fuentes y conservar atribución. |
| P2 | Clásicos de Filosofía en Español (ecastera/filosofia-es) | 7.130 filas | Platón, Aristóteles y clásicos filosóficos en español | Importar como lote pequeño y enfocado tras verificar obras, traducciones y licencia concreta de cada texto. |
| P2 | Wikisource en español | Variable; catálogo extenso | Filosofía, política, historia, ciencia y literatura primaria | Selección por obra/edición; dominio público o CC BY-SA según ficha. Priorizar traducciones españolas de clásicos y textos filosóficos. |
| P2 | Gutenberg en español | Variable; catálogo extenso | Filosofía, economía política, historia y ciencia histórica | Selección individual. No inferir dominio público en España por la etiqueta estadounidense de Gutenberg. |
| P2 | DOAB / OAPEN | Miles de libros académicos | Filosofía, humanidades y ciencia | Filtrar libros en español con licencia CC BY/CC0; excluir NC/ND para la línea general de entrenamiento. |
| P3 | OpenBookQA-ES (BSC-LT) | 500 validación + 500 test | Ciencia escolar factual, opción múltiple | **No entrenar** esos splits: reservarlos para evaluación externa. Buscar train original u otras fuentes con permiso. |

## Cuarentena por licencia y privacidad\n\nLa ficha de Zenodo muestra CC BY 4.0 para el empaquetado de TDX y CSIC, pero sus README de distribución concretan **CC BY-NC-SA 4.0**. Prevalece la condición más restrictiva hasta aclaración formal del distribuidor. TDX indica además que no se realizó anonimización. Por tanto, ninguno de los dos se descarga a `data/datasets` ni se marca `train_eligible=true` en esta línea.\n\n## Matemáticas: corpus factual generado por código

Además de las colecciones externas, se incorpora un generador determinista del proyecto:
`scripts/generate_math_es.py`.

- Produce ejercicios en castellano de suma, resta, multiplicación, división exacta, resto, potencias pequeñas, MCD, MCM, porcentajes exactos y fracciones reducibles.
- Las respuestas se calculan con aritmética entera/racional de Python; no hay docente generativo.
- Semilla, versión, ID, operación y SHA-256 quedan registrados.
- Permite generar millones de filas bajo demanda en Actions; no se versionan millones de líneas en Git.
- Dominio separado `math_synthetic`; no mezclar sin límite de proporción ni evaluar con los mismos ejemplos generados.
- La salida se marca como sintética y con licencia propia del código/datos generados por MINIRONIN.

## Reglas de admisión (obligatorias)

1. Castellano real: clasificador de idioma más muestreo humano; no basta con el campo de metadatos.
2. Licencia: guardar licencia/URL/revisión por documento. Excluir NC, ND, desconocida o incompatible de la línea general hasta revisión jurídica/documental.
3. Calidad: retirar navegación, boilerplate, OCR corrupto, páginas vacías, listas de enlaces y contenido repetido.
4. Deduplicación: exacta y casi duplicados frente a todo `data/datasets`; no mezclar splits.
5. Factualidad: distinguir fuente primaria, artículo revisado, tesis, enciclopedia y web general; no convertir afirmaciones no verificadas en verdad de referencia.
6. Holdout: comprobar IDs, hashes, URL, título y similitud contra los holdouts reservados; cualquier coincidencia bloquea la admisión.
7. Trazabilidad: SHA-256 de archivo y documento, procedencia, licencia, fecha, transformación y conteos por idioma/dominio.
8. Entrenamiento: añadir primero como corpus candidato, auditar y medir proporciones; no promover checkpoint por volumen añadido.

## Fuentes

- TDX Thesis Spanish Corpus: https://zenodo.org/records/7313149
- CSIC Spanish Corpus: https://zenodo.org/records/7313126
- Filosofía en español: https://huggingface.co/datasets/ecastera/filosofia-es
- Common Corpus: https://huggingface.co/datasets/PleIAs/common_corpus
- FineWeb-2: https://huggingface.co/datasets/HuggingFaceFW/fineweb-2
- Spanish 3 Billion Words: https://github.com/josecannete/spanish-corpora
- Wikisource: https://es.wikisource.org/
- Project Gutenberg: https://www.gutenberg.org/
- DOAB: https://www.doabooks.org/
- ALIA Cultural Heritage: https://huggingface.co/datasets/SINAI/ALIA-es-cultural-heritage\n- ESQAD: https://zenodo.org/records/16351733\n- Wikidata Label Maps: https://huggingface.co/datasets/yashkumaratri/wikidata-label-maps-2025-all-languages\n- OpenAlex Philosophy: https://huggingface.co/datasets/CristianPelayo/openalex-philosophy\n- OpenBookQA-ES (solo referencia de evaluación): https://huggingface.co/datasets/BSC-LT/openbookqa-es

## Estado de ejecución

Este fichero registra fuentes y política de admisión. Los tamaños son los declarados por sus páginas de origen y no equivalen a bytes descargados en MINIRONIN. Cada lote deberá publicar manifiesto, SHA-256, conteo de filas/documentos, idioma, licencia y resultado de auditoría antes de marcarse como `admitted`.
