# Lecciones de ingeniería extraídas de entrenamientos

**Versión:** 1.0  
**Idioma:** castellano  
**Registros:** 15  
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

El lote de 14 registros pasó la auditoría en [ejecución 42378755692](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42378755692). Se ha añadido una lección más sobre un bloque de entrenamiento de 2.000 pasos; la nueva auditoría está en curso y actualizará el hash del manifiesto.

## Uso

Estos registros pueden servir para entrenar al modelo a interpretar métricas, diagnosticar fallos y explicar controles de reproducibilidad. No sustituyen los corpus lingüísticos generales ni los benchmarks reservados. Antes de una mezcla de entrenamiento, deben pasar deduplicación global y revisión de contaminación del holdout.
