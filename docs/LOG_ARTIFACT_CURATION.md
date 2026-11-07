# Informe de curación manual — HERETIC-RONIN y RONIN-IA

**Fecha:** 2026-11-07  
**Destino:** MINIRONIN  
**Decisión:** admitir ocho lecciones de ingeniería redactadas manualmente; rechazar el lote docente bruto de 200 ejemplos como supervisión directa.

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

Se han redactado manualmente ocho ejemplos en castellano:
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
