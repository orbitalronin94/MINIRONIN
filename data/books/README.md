# Biblioteca de lógica, ciencia y razonamiento

Esta carpeta separa la biblioteca documental del corpus general heredado. Objetivo: **5.000 obras/documentos únicos con texto utilizable**, seleccionados por contenido y no por el mero número de registros de catálogo.

## Prioridad lingüística y factual

La adquisición nueva prioriza **castellano**: fuentes oficiales españolas, bibliotecas nacionales, universidades, repositorios científicos y colecciones educativas abiertas. Después se incorporan fuentes de cualquier idioma cuando aporten hechos, ciencia, matemáticas, documentación técnica o datos con procedencia verificable. Se conserva siempre el idioma original; las traducciones son derivadas enlazadas con su fuente, nunca documentos independientes para inflar el recuento.

El mapa ampliado de adquisición está en `data/curated/OPEN_FACTUAL_CORPORA.md`. Incluye BOE, INE, AEMET, IGN/CNIG, Banco de España, BNE, OpenStax, Wikidata, Eurostat, World Bank, OpenAlex, PubMed Central OA, PleIAs Common Corpus y Common Pile, con controles de licencia y factualidad por componente.

## Fuentes iniciales aprobadas para adquisición técnica

| Fuente | Alcance conocido | Derechos declarados | Uso |
|---|---:|---|---|
| PRODATPHIL v0.3 — Science and Logic | 147 obras: 44 libros y 103 artículos; 74 autores; 1831–1923 | Dominio público según Universidad de Münster | Primera adquisición directa; fuente especialmente alineada con lógica y filosofía de la ciencia |
| BNE — documentos en dominio público | Catálogo de obras digitalizadas en español; incluye metadatos y enlaces OCR | CC BY 4.0 según datos.gob.es/BNE | Selección por materias; conservar atribución |
| Project Gutenberg | Catálogo público de libros y ficheros descargables | Derechos dependen del país y de cada registro; la situación en EE. UU. no garantiza dominio público en España | Descarga selectiva, comprobar derechos obra por obra |
| Open Logic Project | Material moderno de lógica formal y demostración | CC BY 4.0 según el proyecto | Texto didáctico de referencia, separado de los clásicos |

## Registros de fuente

Los registros de fuente se mantienen en `SOURCES.jsonl`. No son libros descargados ni cuentan para el objetivo de 5.000.

## Primera importación

El workflow `.github/workflows/acquire-reasoning-books.yml` descarga PRODATPHIL v0.3, comprueba el ZIP, extrae el corpus y publica un artefacto de Actions con los textos y el manifiesto. Esto evita meter cientos de megabytes o gigabytes de OCR sin filtrar en el historial Git. Un artefacto de Actions es una copia preparada y temporal; no equivale a un corpus persistido en `main`.

## Reglas

- No duplicar la misma obra por idioma, edición, espejo o formato.
- Mantener originales y traducciones como relaciones, no como obras nuevas automáticamente.
- No usar el OCR de la BNE sin revisar idioma, longitud, ruido y atribución.
- No mezclar obras históricas con respuestas modernas verificadas sin etiquetas.
- No inferir que un autor antiguo es correcto por ser canónico.
- Mantener holdout por obra y autor para evitar contaminación por capítulos o ediciones paralelas.
- El recuento oficial solo aumenta tras descargar y auditar el texto completo.
- Para datos factuales, preservar unidad, periodo, jurisdicción, fuente y fecha de revisión; nunca entrenar cifras sin su contexto.

## Estado inicial

- Objetivo: 5.000 obras/documentos únicos.
- Obras completas adquiridas: 147 (PRODATPHIL v0.3; release persistente). No están versionadas dentro del árbol Git: se distribuyen como asset de release para no inflar el historial.
- Lote PRODATPHIL v0.3: 147 obras declaradas por el editor; ZIP descargado, comprobado, extraído (151 archivos de paquete, 31.453.941 bytes extraídos) y publicado como release asset.
- Biblioteca HERETIC heredada: 16 archivos / 2.136.389.480 bytes extraídos en Actions, publicados en el artefacto `minironin-heretic-corpus-prepared`; aún no está persistida en el árbol Git de `main`.
