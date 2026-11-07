# MINIRONIN — estrategia evolutiva permanente

## Ciclo de selección natural

Este es el protocolo estándar de entrenamiento de MINIRONIN. Se repite generación tras generación; no se vuelve a entrenar desde cero mientras exista un checkpoint padre válido.

1. **Padre:** usar el mejor checkpoint seleccionado de la generación anterior. El checkpoint es inmutable y se registra su SHA-256.
2. **Torneo:** crear exactamente 30 descendientes desde el mismo padre. Cada descendiente recibe una semilla independiente y ejecuta 1.000 pasos adicionales.
3. **Selección de semilla:** evaluar los 30 descendientes con la misma validación fija, sin contaminación del holdout. Clasificar por pérdida de validación y desglose por dominio. Guardar métricas y hashes de los 30.
4. **Crecimiento:** el descendiente ganador recibe 200.000 pasos adicionales. Guardar checkpoints intermedios cada 10.000 pasos.
5. **Selección de checkpoint:** al acabar esos 200.000 pasos, comparar todos los checkpoints intermedios y el checkpoint final con la misma validación. Elegir el checkpoint con menor pérdida de validación como padre de la siguiente generación. No asumir que el último es el mejor.
6. **Siguiente generación:** lanzar otras 30 semillas de 1.000 pasos desde ese checkpoint seleccionado. Repetir indefinidamente el ciclo.
7. **Control independiente:** antes de promover una generación o sustituir el padre operativo, ejecutar el holdout inmutable de 40 preguntas y revisar las salidas. La pérdida de validación no demuestra por sí sola razonamiento ni comprensión.

## Primera generación: padre de 130.000 pasos

- Padre inicial: release `long-train-step-130000`.
- SHA-256: `4eea4efe7e1c65da0ee7985ae3c09a7f69eab3cce90e2cabaa8694b6857cc986`.
- Torneo inicial: 30 semillas × 1.000 pasos.
- Ganador: 200.000 pasos adicionales.
- Alcance global esperado del ganador: 331.000 pasos (131.000 tras el torneo + 200.000).
- Checkpoints de la fase larga: cada 10.000 pasos.

## Reglas de reproducibilidad y seguridad

- Los 30 descendientes de una generación parten exactamente del mismo estado de pesos y optimizador.
- Corpus, mezcla de dominios, tokenizer, configuración del modelo y validación deben ser idénticos dentro de una generación.
- Las semillas modifican la secuencia reproducible de minibatches y la aleatoriedad del entrenamiento.
- Nunca sobrescribir el padre ni borrar descendientes perdedores: conservar informes, hashes y manifiestos.
- No seleccionar por pérdida de entrenamiento.
- No introducir preguntas ni respuestas del holdout en el corpus.
- La selección automática por validación produce un **candidato**, no una promoción automática.
- Registrar para cada candidato: padre y hash, semilla, pasos, pérdida global y por dominio, manifiesto de corpus, configuración y SHA-256.
- Si una generación falla, se conserva el último padre válido y se reanuda desde ahí; no se inicia una generación con un checkpoint incompleto.

## Métrica de selección

La pérdida de validación común es el criterio mecánico para ordenar candidatos y checkpoints. Se inspeccionarán también los resultados por dominio para detectar regresiones concentradas. El holdout semántico permanece separado y actúa como control de calidad independiente.
