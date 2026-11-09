# Open collections intake — MINIRONIN

**Corte:** 2026-11-09  
**Rama de trabajo:** `prep/open-collections-curation-2026-11`  
**Estado:** lote piloto de síntesis originales; no incorporado al corpus congelado 800k→950k.

## Regla de admisión

No basta con que un recurso sea gratuito o accesible. Cada documento primario requiere licencia y edición concretas, autor, fecha, idioma, URL de origen, fecha de recuperación, SHA-256, transformación, deduplicación y comprobación de que no pertenece a un holdout. En España, la etiqueta de dominio público de Project Gutenberg para Estados Unidos no se toma como prueba suficiente de dominio público territorial.

Las fichas de este lote son **síntesis originales en castellano** y no reproducciones de las obras fuente. Sus enlaces sirven para localizar y revisar los textos primarios. No se debe inferir que el texto fuente completo ha sido importado.

## Colecciones y decisión

| Colección | Uso previsto | Licencia / control | Decisión |
|---|---|---|---|
| Project Gutenberg | Classics, Anarchists, PRODATPHIL | Revisar cada obra; la página de Gutenberg suele declarar dominio público en EE. UU.; comprobar España y separar material editorial moderno | Prioridad alta para obras históricas seleccionadas |
| Wikisource | Classics, Anarchists, PRODATPHIL | Cada página puede ser dominio público o CC BY-SA; comprobar la obra y la edición | Prioridad alta, por documento |
| DOAB / OAPEN | PRODATPHIL, ciencia, humanidades | Metadatos CC0; licencia del texto completo varía por libro | Prioridad alta para libros CC BY/CC0; excluir NC/ND |
| PubMed Central OA Subset | Ciencia / HERETIC | Solo artículos del subconjunto OA y respetando licencia individual | Prioridad alta, selección por CC BY/CC0 |
| Stack Exchange Data Dump | Ingeniería / conocimiento técnico | CC BY-SA según fecha/revisión; preservar atribución, URL y licencia exacta | Piloto separado, no mezclar sin atribución |
| Wikidata | Referencia estructurada | Datos estructurados CC0; no confundir con texto de otros namespaces o multimedia | Usar para metadatos, no como prosa principal |
| MIT OpenCourseWare | Ingeniería y ciencia | CC BY-NC-SA 4.0 | Excluido de admisión general por restricción NC |
| OpenStax | Ciencia y educación | CC BY-NC-SA | Excluido de admisión general por restricción NC |

## Documentos piloto creados

Los documentos de `data/inherited/*/curated/` son explicaciones originales, no textos copiados. Cada uno enlaza la fuente histórica y deja visibles las limitaciones de procedencia.

- Classics: Darwin, Smith, Mill, Wollstonecraft.
- Anarchists: Kropotkin, Proudhon, Bakunin.
- PRODATPHIL: Hume, Bacon, Bayes, Peirce.

**Nota de corrección:** el enlace Project Gutenberg eBook 23428 corresponde a *The Conquest of Bread*, no a *Mutual Aid*. La ficha de apoyo mutuo lo declara expresamente y no presenta ese enlace como evidencia de la edición de *Mutual Aid*.

## Siguiente paso de ingestión

1. Obtener el texto primario solo desde una fuente con derechos comprobados.
2. Guardar el original en su biblioteca correspondiente y mantener estas síntesis como documentos separados.
3. Extraer metadatos por obra; no heredar una licencia global de toda la colección.
4. Normalizar texto, retirar navegación/HTML/duplicados y detectar casi duplicados frente a HERETIC y RONIN-IA.
5. Calcular SHA-256 y añadir manifiesto de origen.
6. Ejecutar auditoría y preparar un nuevo corpus versionado. No alterar artefactos de entrenamiento ya iniciados.

## Evidencia de licencias consultada

- Project Gutenberg: https://www.gutenberg.org/policy/license
- Wikisource reuse: https://en.wikisource.org/wiki/Wikisource:Reusing_Wikisource_content
- DOAB FAQ y metadatos: https://www.doabooks.org/en/researchers/full-faq
- PubMed Central OA subset: https://support.nlm.nih.gov/knowledgebase/article/KA-03584/en-us
- Stack Exchange licensing: https://stackoverflow.com/help/licensing
- Wikidata licensing: https://www.wikidata.org/wiki/Wikidata:Licensing
- MIT OCW terms: https://ocw.mit.edu/pages/privacy-and-terms-of-use/
- OpenStax licensing: https://help.openstax.org/s/article/Openstax-textbook-licensing-and-customization
