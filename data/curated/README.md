# Lecciones de ingeniería extraídas de entrenamientos

**Versión:** 1.0  
**Idioma:** castellano  
**Registros:** 8  
**Método:** curación manual a partir de logs y metadatos de artefactos de GitHub Actions.

Este conjunto transforma evidencia operativa de RONIN-IA y HERETIC-RONIN en ejemplos explicativos. No contiene logs brutos ni respuestas automáticas del docente.

## Fuentes incluidas

- HERETIC-RONIN, ejecución [42370725970](https://github.com/orbitalronin94/HERETIC-RONIN/actions/runs/42370725970), trabajo 128398241561, artefacto 13574129542.
- RONIN-IA, ejecución [42364138740](https://github.com/orbitalronin94/RONIN-IA/actions/runs/42364138740), trabajos 128378601930 y 128378602072.

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

La auditoría automática pasó en [ejecución 42378515927](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42378515927). SHA-256 del JSONL: `013155e7b94ed4278ffb31e21970c1db895f17336f5c7a59c5deba0b7d7d3faa`. El manifiesto está versionado en `data/manifests/engineering-lessons-v1.sha256.json` y también se publicó como artefacto de Actions.

## Uso

Estos registros pueden servir para entrenar al modelo a interpretar métricas, diagnosticar fallos y explicar controles de reproducibilidad. No sustituyen los corpus lingüísticos generales ni los benchmarks reservados. Antes de una mezcla de entrenamiento, deben pasar deduplicación global y revisión de contaminación del holdout.
