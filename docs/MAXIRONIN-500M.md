# MAXIRONIN — experimento de 500M efectivos

MAXIRONIN es una rama experimental de modelo dentro del repositorio MINIRONIN. No sustituye ni modifica el checkpoint MAIN de MINIRONIN.

## Objetivo de la primera prueba

- Arquitectura: Transformer decoder-only, pre-LN.
- Parámetros entrenables auditados: **500.141.056**.
- Capas: 37; ancho: 1.024; cabezas: 16; FFN: 4.096.
- Contexto máximo: 512 tokens.
- Embeddings de entrada y salida compartidos (tied weights).
- Precisión de entrenamiento: FP32.
- Optimizador: Adafactor factorizado para evitar dos estados completos de Adam por parámetro.
- Gradient checkpointing activado.
- Primera ejecución: exactamente 1.000 pasos, batch 1, secuencia 128.

El recuento se comprueba sobre los parámetros reales del modelo y sobre los parámetros entrenables. No se congela ninguna capa ni se cuentan parámetros nominales.

## Tokenizador

BPE byte-level entrenado desde cero sobre todos los textos del artefacto inmutable del corpus unificado:

- Vocabulario: 32.768 tokens.
- ByteLevel pre-tokenizer y decoder.
- Normalización Unicode NFC.
- Dígitos aislados durante la pre-tokenización.
- Tokens especiales: `<PAD>`, `<UNK>`, `<BOS>`, `<EOS>`, `<DOC>`.
- Partición determinista 95/5 por documento para entrenamiento y validación.

La tokenización y el modelo MAXIRONIN son independientes del tokenizador byte-level de 257 símbolos de MINIRONIN.

## Corpus de la prueba inicial

Se reutiliza sin reconstruirlo el artefacto unificado publicado por el run `42523463620`:

- Artefacto: `minironin-unified-train-corpus-42523463620`.
- SHA-256 del artefacto: `e02fa1240a0457310cacf1406f641c720942a41abc48d83f3e4c730506b691fc`.
- Archivo principal: `train.jsonl.gz`; su integridad se verifica con `SHA256SUMS`.

No se incorporan fuentes nuevas ni se altera el corpus histórico.

## Interpretación

Los 1.000 pasos son una prueba de ingeniería: validan el entrenamiento, la memoria, la serialización del checkpoint y la caída de loss en una muestra fija. Con batch 1 y secuencia 128 se procesan aproximadamente 128.000 tokens de entrenamiento. No es entrenamiento suficiente para evaluar la capacidad lingüística de un modelo de 500M.

El checkpoint MAXIRONIN se publica como artefacto experimental. No se promociona a MAIN ni se mezcla con MINIRONIN.

## Paquete pretokenizado reutilizable

La preparación del corpus se separa del entrenamiento mediante
[prepare-maxironin-500m-data.yml](../.github/workflows/prepare-maxironin-500m-data.yml).
Ese workflow entrena el BPE una sola vez y publica el paquete
`maxironin-500m-pretokenized-corpus-v1`, que contiene:

- `tokenizer.json`
- `train.bin` y `validation.bin` (uint16 little-endian)
- `tokenizer-manifest.json` (SHA-256 del corpus, split y recuentos)
- `SHA256SUMS` para verificar todos los ficheros

Los workflows posteriores deben descargar este paquete por su run ID, ejecutar
`sha256sum -c SHA256SUMS` y usar directamente los binarios y el tokenizador.
No deben volver a ejecutar `prepare_maxironin_corpus.py` ni volver a entrenar el BPE.
El paquete de Actions tiene retención de 90 días; si se necesita conservarlo más
tiempo, habrá que republicarlo o trasladarlo a un release versionado. El run ID
de la primera preparación se añadirá aquí cuando termine y se verifique.
