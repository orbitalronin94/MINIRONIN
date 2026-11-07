# Plan de admisión — 5.000 obras de razonamiento

El objetivo es 5.000 obras/documentos completos, únicos y utilizables. La cuota por dominio está definida en `docs/REASONING_CURRICULUM.md`.

## Contabilidad

| Indicador | Valor |
|---|---:|
| Objetivo | 5.000 |
| Obras completas admitidas en Git | 0 |
| Obras en artefactos de adquisición confirmados | 0 |
| Lote PRODATPHIL v0.3 | 147 obras declaradas por el editor; workflow de adquisición pendiente |
| HERETIC corpus preparado | 16 archivos / 2.136.389.480 bytes; no son libros y no cuentan para este objetivo |

## Fases de expansión

1. PRODATPHIL v0.3: importar los 147 textos, extraer metadatos y contar libros/artículos por separado.
2. BNE: descargar el catálogo CC BY 4.0 y seleccionar títulos en español relacionados con lógica, matemáticas, filosofía natural, método científico, estadística y argumentación. Solo contar los registros cuyo texto OCR se haya descargado y supere controles.
3. Project Gutenberg: extraer selectivamente obras clásicas y comprobar derechos para España por obra; no hacer mirror completo.
4. Colecciones abiertas modernas: lógica formal, teoría de la demostración, matemáticas y estadística, respetando licencias y atribución.
5. Expandir por lotes de 250–500, deduplicar por hash y similitud, y recalcular cuotas.

## No hacer

- No sumar libros, artículos, capítulos, traducciones y versiones como si fueran obras independientes.
- No contar metadatos de catálogo como documentos entrenables.
- No usar una obra como train y otra edición del mismo texto como holdout.
- No entrenar directamente sobre textos OCR con calidad baja.
- No usar solo preentrenamiento causal para enseñar demostraciones: crear después tareas con soluciones verificadas.
