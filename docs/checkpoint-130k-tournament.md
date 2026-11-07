# Torneo de continuación desde el checkpoint 130k

Este experimento bifurca 30 veces el mismo checkpoint de 130.000 pasos. Cada rama restaura exactamente los mismos pesos y el mismo estado AdamW, y continúa 1.000 pasos con un orden de muestreo determinista distinto por semilla.

- Fuente: release `long-train-step-130000`.
- SHA-256: `4eea4efe7e1c65da0ee7985ae3c09a7f69eab3cce90e2cabaa8694b6857cc986`.
- Arquitectura: 9.970.176 parámetros; vocabulario activo 257.
- Entrenamiento: mismo corpus completo HERETIC + PRODATPHIL, mismo split y mismas ventanas fijas de validación.
- Scheduler: se continúa la curva coseno original en pasos globales 130001–131000.
- Estado del optimizador: se restaura el AdamW del checkpoint 130k en cada rama.
- Selección: menor pérdida de validación fija; desempate por número de semilla.

El resultado es un candidato, nunca una promoción automática. Se debe ejecutar el holdout invariable de 40 preguntas sobre el candidato ganador y compararlo con 130k antes de promover. La pérdida de validación no demuestra por sí sola capacidad semántica.

Artefactos: checkpoint ganador (incluye pesos y AdamW), tabla JSONL de las 30 semillas, informe y manifiesto del corpus. El workflow no modifica el checkpoint base ni el modelo de `main`.
