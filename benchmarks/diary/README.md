# Diario de inferencia MINIRONIN

Este directorio conserva una ejecución independiente del mismo holdout contra cada estado del modelo.

## Orden de evaluación

1. **Base:** ganador del torneo de 30 semillas, seed 9519, checkpoint tras 100 pasos. Es la referencia anterior al entrenamiento largo; no es una inicialización aleatoria.
2. **Checkpoints:** releases `long-train-step-10000`, `long-train-step-20000`, etc., en orden ascendente.
3. Cada ejecución procesa un solo checkpoint nuevo. El workflow programado consulta releases cada 15 minutos. La base siempre se registra primero.

## Comparabilidad

- El conjunto fijo está en [inference-holdout-v1.jsonl](../inference-holdout-v1.jsonl): 40 preguntas de autoría propia, separadas del corpus de entrenamiento.
- Mismos IDs, texto de pregunta, sufijo de prompt, greedy argmax, temperatura 0 y máximo de 128 bytes generados.
- Modelo en modo evaluación, CPU y dos hilos.
- Se conserva la respuesta literal, los IDs de bytes generados, tiempo, SHA-256 del checkpoint y SHA-256 del holdout.
- La comparación automática solo mide cambios literales respecto a la base. **No** convierte cambios, longitud o pérdida de entrenamiento en una puntuación de calidad.

## Evaluación humana

Los JSON incluyen la rúbrica esperada de cada pregunta. Para decidir si una respuesta mejora, revisar las salidas con etiquetas ocultas (A/B) y puntuar exactitud, razonamiento, seguimiento de instrucciones, contradicciones, calibración y abstención. No promocionar checkpoints por este diario sin esa revisión.

## Archivos

- `base.json`: primera ejecución de referencia.
- `checkpoint-N.json`: respuestas del checkpoint con N pasos.
- `index.md`: índice generado automáticamente.

Los archivos de diario se versionan en Git para que sobrevivan a la retención limitada de artefactos de Actions.
