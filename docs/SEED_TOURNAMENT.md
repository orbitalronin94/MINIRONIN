# Torneo de semillas sobre corpus real

## Protocolo

El workflow `.github/workflows/seed-tournament.yml` descarga y vuelve a verificar el corpus HERETIC aprobado por el usuario y la biblioteca PRODATPHIL v0.3. Después ejecuta **30 inicializaciones independientes, 100 actualizaciones AdamW por inicialización** (3.000 pasos en total).

Todas las semillas reciben el mismo calendario determinista de minibatches. Se separan documentos completos para entrenamiento y validación antes de muestrear ventanas; ninguna ventana de un documento de validación entra en entrenamiento. El ganador es el checkpoint con menor pérdida media en la validación fija y se informa además la pérdida por dominio.

## Mezcla del piloto

| Dominio | Peso |
|---|---:|
| Matemáticas (OpenWebMath y Cosmopedia auto-math) | 40% |
| Ciencia/educación (arXiv, Cosmopedia y FineWeb-Edu) | 25% |
| Libros históricos PRODATPHIL | 20% |
| Ejemplos de comportamiento MINIRONIN | 10% |
| Aya multilingüe | 5% |

Para mantener el experimento acotado, se leen hasta 24 MiB y 350 documentos por fuente JSONL seleccionada. De PRODATPHIL se leen textos, XML/TEI y Markdown utilizables. El archivo HERETIC completo se descarga, reconstruye, verifica y extrae; el piloto no pretende consumir los 2,1 GB completos en solo 3.000 pasos. Se excluyen deliberadamente los conjuntos de audio/transcripción y Wikidata del muestreo inicial porque no son el mejor material para este objetivo.

## Limitación de tokenización

El tokenizador definitivo de MINIRONIN todavía no está congelado. Para que este primer torneo sea ejecutable y reproducible, usa UTF-8 byte-level: IDs 0–255 y EOS=256. El modelo mantiene la arquitectura configurada y sus **9.970.176 parámetros**, pero la cabeza de salida activa solo 257 símbolos mediante `vocab_limit`. No equivale a un modelo ya entrenado con un vocabulario semántico de 23.000 tokens. El checkpoint es una primera adaptación de corpus, no un modelo conversacional acabado.

## Selección y publicación

- Semillas: 9500–9529 por defecto.
- 100 pasos por semilla; batch 2; secuencia 128.
- AdamW, LR máximo 3e-4, warmup corto, decaimiento cosenoidal y clipping 1.0.
- Selección: menor pérdida en ventanas fijas de documentos no vistos durante el entrenamiento.
- Publicación: checkpoint ganador, informe ordenado, manifiesto de datos y SHA-256 en artefacto y release con tag `seed-tournament-RUN_ID`.
- El ganador queda como **candidato**, no se promociona automáticamente a main. Antes de promover hay que evaluar respuestas, lógica, matemáticas, abstención y regresiones con un holdout conductual independiente.

## Interpretación

Una diferencia pequeña de pérdida entre semillas puede ser ruido. El informe conserva las 30 métricas y el desglose por dominio para no vender una victoria marginal como mejora general. Cien pasos por semilla sirven para una criba de inicializaciones, no para afirmar que el modelo ha aprendido razonamiento profundo.
