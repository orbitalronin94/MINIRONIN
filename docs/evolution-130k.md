# MINIRONIN — evolución desde el checkpoint 130k

## Protocolo fijado
1. Padre inmutable: release `long-train-step-130000`, checkpoint SHA-256 `4eea4efe7e1c65da0ee7985ae3c09a7f69eab3cce90e2cabaa8694b6857cc986`.
2. Crear 30 descendientes restaurando exactamente pesos y estado AdamW del padre.
3. Cada descendiente entrena 1.000 pasos (30.000 pasos de optimizador agregados). Se mantienen corpus, mezcla de dominios, validación y configuración. Las semillas alteran el orden reproducible de minibatches y el dropout.
4. Clasificar por pérdida de validación común, con desglose por dominio. Conservar todos los resultados y hashes.
5. El ganador continúa 200.000 pasos adicionales: global step 131.001 a 331.000, checkpoints cada 10.000.
6. No promocionar automáticamente. Ejecutar el holdout inmutable de 40 preguntas y revisar las salidas antes de cualquier promoción.

## Salvaguardas
- No modificar ni sobrescribir el padre.
- No mezclar el holdout en el corpus de entrenamiento.
- No seleccionar por pérdida de entrenamiento.
- La pérdida de validación es una métrica de selección, no una prueba de razonamiento.
- Guardar manifiesto del corpus, métricas por dominio, SHA-256 de checkpoints y reportes.
