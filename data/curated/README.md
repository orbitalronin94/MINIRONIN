# Lecciones de ingeniería extraídas de entrenamientos

**Versión:** 1.0  
**Idioma:** castellano  
**Registros:** 50  
**Método:** curación manual a partir de logs y metadatos de artefactos de GitHub Actions.

Este conjunto transforma evidencia operativa de RONIN-IA y HERETIC-RONIN en ejemplos explicativos. No contiene logs brutos ni respuestas automáticas del docente.

## Fuentes incluidas

- HERETIC-RONIN, ejecución [42370725970](https://github.com/orbitalronin94/HERETIC-RONIN/actions/runs/42370725970), trabajo 128398241561, artefacto 13574129542.
- RONIN-IA, ejecución [42364138740](https://github.com/orbitalronin94/RONIN-IA/actions/runs/42364138740), trabajos 128378601930 y 128378602072.
- HERETIC-RONIN, benchmark CPU [42355677701](https://github.com/orbitalronin94/HERETIC-RONIN/actions/runs/42355677701), referencia y variantes de hilos, mmap, BF16, compilación y afinidad.
- HERETIC-RONIN, bloque de entrenamiento [42355677713](https://github.com/orbitalronin94/HERETIC-RONIN/actions/runs/42355677713), pasos 600–2600 y curva de pérdida registrada en el log.

## Esquema

Cada línea JSONL contiene:
- identificador estable;
- tipo y dominio;
- instrucción y respuesta redactadas manualmente en castellano;
- evidencia concreta del log/manifiesto;
- repositorio, ejecución y trabajo de origen;
- nivel de confianza y método de curación;
- uso previsto.

## Criterios de calidad

- Se separan hechos observados e interpretación.
- No se confunde CI correcto con mejora del modelo.
- No se confunde smoke test con evaluación reservada.
- Un error anterior al primer paso del optimizador se clasifica como fallo de preparación, no como divergencia de entrenamiento.
- Las respuestas generadas por un docente no se consideran verdaderas sin verificación independiente.
- No se incluyen pesos, estados de optimizador, prompts/answers del holdout, secretos ni identificadores personales.

## Exclusión importante: lote docente de HERETIC

El artefacto de la ejecución 42370725970 contenía 200 ejemplos generados por SoAIHQ/Qwen3.5-4B-GGUF Q4_K_M. El propio manifiesto declara que solo se comprobaron formato, longitud y unicidad; no hubo verificación factual independiente. La muestra inspeccionada mostró preguntas redundantes y respuestas semánticamente dudosas. **No se incorpora ese JSONL bruto como supervisión aprobada.** Se conserva únicamente la lección sobre sus límites de calidad y la evidencia de la ejecución.

## Auditoría e integridad

El lote de 50 registros pasó la auditoría en [ejecución 42379452577](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42379452577). SHA-256: `f96218280922a1a8cfe2ac9d7520b0c554b72e4aa600aae95a9581350a30e204`. El manifiesto versionado recoge nueve repositorios de origen.

## Objetivo de expansión

El objetivo es llegar a 1.000 casos válidos. El progreso y los criterios de admisión están en [ENGINEERING_CASES_1000.md](../../docs/ENGINEERING_CASES_1000.md). Los logs repetidos de una misma suite no se cuentan como casos distintos.

## Uso

Estos registros pueden servir para entrenar al modelo a interpretar métricas, diagnosticar fallos y explicar controles de reproducibilidad. No sustituyen los corpus lingüísticos generales ni los benchmarks reservados. Antes de una mezcla de entrenamiento, deben pasar deduplicación global y revisión de contaminación del holdout.


## Dataset de abstención fuera de ámbito

**Versión:** 1.0  
**Registros:** 50.000 preguntas únicas generadas de forma determinista.  
**Respuesta objetivo:** `ni puta idea`.  
**Generador:** `scripts/generate_abstention_dataset.py` (semilla fija `20261108`).

El dataset cubre preguntas absurdas, premisas ficticias, sucesos imposibles, entidades inventadas y datos inaccesibles o no proporcionados. Cada registro incluye contexto explícito de ausencia de evidencia, pregunta y respuesta objetivo. El generador verifica unicidad, cardinalidad y uniformidad de la respuesta.

El conjunto se genera automáticamente en cada ejecución limpia del entrenamiento, se incorpora al dominio independiente `abstention` y queda reflejado en el manifiesto con tamaño y SHA-256. La mezcla reserva un 5% del muestreo para abstención y conserva un dominio `behavior` separado para no diluir los ejemplos de comportamiento ya curados.

**Límite de interpretación:** el corpus enseña una respuesta para preguntas sintéticas claramente fuera de ámbito; no demuestra por sí solo una capacidad general de calibración. La evaluación debe medir también abstenciones indebidas ante preguntas respondibles.

## Nuevos datasets de abstención (v1)

El workflow genera de forma determinista dos conjuntos independientes de **50.000 registros cada uno** (100.000 en total):

- `minironin-abstain-plain-50k-v1.jsonl`: preguntas deliberadamente fuera de alcance con respuesta canónica exacta `ni puta idea, la verdad`.
- `minironin-abstain-literary-50k-v1.jsonl`: las mismas clases de límites epistémicos expresadas mediante respuestas aforísticas originales, con ironía y gravedad filosófica. No son citas ni imitaciones textuales de Nietzsche, Cioran u otros autores.

Los prompts son sintéticos y tratan entidades y acontecimientos inventados; no se presentan como hechos. El generador `scripts/build_abstention_datasets.py` produce los JSONL y un manifiesto con número de registros, bytes y SHA-256. El workflow conserva los tres archivos junto a los artefactos del ciclo.

### Mezcla de entrenamiento

Los dos conjuntos se cargan en dominios separados (`abstain_plain` y `abstain_literary`) con un peso inicial de 0,05 cada uno. Esto reserva aproximadamente el 9,1 % de la mezcla normalizada para abstención, sin convertir todas las muestras del dominio de comportamiento en respuestas de desconocimiento. El conjunto original de comportamiento permanece separado.

La validación se separa por documento mediante el split determinista del entrenador. Antes de promover un checkpoint se debe medir abstención correcta, abstención indebida en preguntas respondibles y generalización a preguntas absurdas no vistas. Este entrenamiento enseña un patrón de calibración; no demuestra por sí solo que el modelo sepa reconocer todos los límites de su conocimiento.
