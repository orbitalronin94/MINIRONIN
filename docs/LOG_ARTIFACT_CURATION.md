# Informe de curación manual — HERETIC-RONIN y RONIN-IA

**Fecha:** 2026-11-07  
**Destino:** MINIRONIN  
**Decisión:** admitir quince lecciones de ingeniería redactadas manualmente; rechazar el lote docente bruto de 200 ejemplos como supervisión directa.

## 1. HERETIC-RONIN — ejecución 42370725970

- Trabajo: 128398241561.
- Artefacto: 13574129542, ZIP de 82.876 bytes.
- Archivos: `teacher-dataset-manifest.json` y `teacher-multidomain-200.jsonl`.
- Modelo docente declarado: `SoAIHQ/Qwen3.5-4B-GGUF`, cuantización `Q4_K_M`.
- SHA-256 del docente declarado: `2ebe6eb67cb92adeffc7073c48dd4e3baf79465ac650793dc751cad2b29cf219`.
- Semilla: 20261106.
- 200 ejemplos: matemáticas 34, programación 34, lógica 33, ciencias naturales 33, lenguaje 33 e interdisciplinar 33.

### Resultado observado en los logs

- Corpus inspeccionado: 854 archivos, 34.922.543 bytes y 2.520 pasajes.
- Se aceptaron 200/200 filas generadas por el docente.
- El empaquetado SFT produjo 200 filas utilizables.
- El código exigía al menos 900 y lanzó `RuntimeError: too few usable SFT rows after context packing: 200`.
- El error ocurrió en `encode_sft_rows`, antes de entrar en los pasos del optimizador.

**Interpretación:** la extracción y generación llegaron a producir un lote; el entrenamiento no comenzó. No debe etiquetarse como entrenamiento completado ni como fallo de convergencia.

### Auditoría de calidad del lote docente

El manifiesto declara expresamente que solo se comprobaron formato, longitud y unicidad; las respuestas no se verificaron de forma independiente. La inspección manual de muestras de los seis dominios encontró señales de baja calidad:
- preguntas redundantes o casi equivalentes;
- preguntas sobre metadatos internos clasificadas como matemáticas;
- respuestas que no se desprenden de la evidencia citada;
- explicaciones que repiten la premisa sin demostrar la respuesta;
- errores semánticos o traducciones defectuosas.

**Decisión:** no importar el lote de 200 como respuestas supervisadas correctas. Se admiten únicamente lecciones sobre el proceso, su procedencia y sus límites de calidad. No se afirma que los 200 ejemplos hayan sido corregidos individualmente.

## 2. RONIN-IA — ejecución 42364138740

### Trabajo 128378601930 — calidad del núcleo

- Ruff: todos los controles pasaron.
- `pip check`: sin dependencias rotas.
- Checkpoint: SHA-256 comprobado contra el manifiesto.
- Carga estricta del estado del modelo.
- Paso del checkpoint y número de parámetros coherentes con el manifiesto.
- Suite: 80 tests superados en 5,50 segundos.
- Cobertura total registrada: 82%.

**Interpretación:** evidencia de integridad y calidad del software en esa revisión. No es prueba de mejora de calidad lingüística del modelo.

### Trabajo 128378602072 — prueba mínima de entrenamiento

- Se ejecutó un paso de entrenamiento en CPU.
- Pérdida final registrada: 5,44084.
- Se comprobó que el archivo de checkpoint de prueba no estaba vacío.
- El log advierte expresamente que no es una evaluación sobre holdout.

**Interpretación:** demuestra que el recorrido mínimo de entrenamiento pudo ejecutarse; no demuestra calidad ni mejora en evaluación.

## 3. Material admitido en MINIRONIN

Se han redactado manualmente quince ejemplos en castellano:
- diagnóstico de fallo de preparación de datos;
- identificación de la condición de 200 frente a 900 filas;
- límites de las respuestas generadas por docentes;
- trazabilidad de modelos docentes y artefactos;
- aislamiento declarado del holdout;
- interpretación de resultados de CI;
- verificación de integridad de checkpoints;
- diferencia entre prueba mínima y evaluación reservada.

Cada registro conserva repositorio, ejecución, trabajo, evidencia, nivel de confianza y método de curación.

## 4. Próximas auditorías

- Revisar más ejecuciones de entrenamiento, incluidas las finalizadas y sus artefactos disponibles.
- Extraer curvas de pérdida, tokens/s, tokens consumidos, configuración y métricas por dominio solo cuando haya evidencia explícita.
- Comparar ejecuciones únicamente con configuración, datos y evaluación compatibles.
- Excluir checkpoints y estados del optimizador del dataset.
- No introducir datos del holdout ni respuestas de evaluación.
- Ejecutar deduplicación global contra documentos ya admitidos.

## 5. HERETIC-RONIN — benchmark CPU 42355677701

Se descargaron y examinaron los 13 artefactos pequeños de referencia/variantes (no los checkpoints de varios GB). Todos comparan 10.240 tokens y una sola actualización del optimizador; por ello sus tokens/s son datos de microbenchmark, no rendimiento garantizado de entrenamiento largo.

| Variante | Tokens/s | Cambio frente a referencia | Control numérico | Decisión |
|---|---:|---:|---|---|
| Referencia, 4 hilos | 38,18 | — | referencia | base |
| 2 hilos | 53,12 | +28,12 % | superado | candidata a repetir |
| mmap-batches | 52,62 | +27,44 % | superado | candidata a repetir |
| sharded-prefetch | 46,54 | +17,95 % | superado | candidata secundaria |
| 8 hilos | 45,80 | +16,64 % | superado | candidata secundaria |
| mkldnn desactivado | 44,82 | +14,81 % | superado | candidata secundaria |
| packed-window-cache | 40,74 | +6,28 % | superado | ganancia pequeña |
| AdamW foreach | 38,96 | +2,01 % | superado | ganancia marginal |
| BF16 autocast | 100,37 | +61,96 % | **fallido** | rechazada |
| torch.compile | 30,69 | -24,42 % | **fallido** | rechazada |
| 1 hilo | 24,76 | -54,20 % | superado | no competitiva |
| afinidad CPU | 6,07 | -528,76 % | superado | rechazada |

La variante de evaluación con `inference_mode` también quedó excluida: el artefacto informa control numérico fallido y accuracy de holdout 0,0; no se incorpora ese resultado como señal de calidad.

### Lectura correcta

- Dos hilos y mmap-batches son las dos variantes más interesantes para repetir en MINIRONIN, pero todavía no son ajustes elegidos.
- BF16 fue la más rápida en bruto, pero falló el control numérico. Se rechaza aunque su velocidad parezca atractiva.
- `torch.compile` fue más lento que la referencia y falló el control numérico en ese entorno.
- La afinidad de CPU perjudicó gravemente el rendimiento de esa ejecución.
- Todos los candidatos ejecutaron una sola actualización del optimizador. La pérdida media casi idéntica no demuestra equivalencia de calidad a largo plazo.

Los seis ejemplos del benchmark y una lección adicional sobre el bloque de 2.000 pasos se redactaron manualmente. El lote completo de 15 registros pasó la auditoría de procedencia y estructura en [ejecución 42378954458](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42378954458). SHA-256: `d0d4b618783b7533c823d4bf10cad5ae666cf73841267e37c47e046c6d60b21a`.

## 6. HERETIC-RONIN — bloque de entrenamiento 42355677713

El trabajo 128353150091 registró un bloque de continuación desde el paso 600 hasta el 2600, con objetivo global declarado de 250.000 pasos:
- 2.000 pasos en el bloque.
- 15.382,33 segundos de entrenamiento.
- Pérdida inicial: 2,7662957.
- Pérdida final: 2,5199592.
- Pérdida media: 2,5911295.
- Corpus auditado declarado: 256.237 documentos y 680.665.972 bytes, después de excluir 68 registros duplicados.

**Interpretación:** la pérdida de entrenamiento bajó durante ese bloque. No se puede inferir una mejora del holdout a partir de ese dato. El artefacto de 6.001.698.610 bytes incluye archivos `holdout-before.json` y `holdout-after.json`, pero no se descargó el checkpoint completo y el fragmento de log consultado no expone las métricas de esos informes. Por eso el ejemplo curado enseña a separar pérdida de entrenamiento y generalización, sin inventar un resultado de evaluación.
