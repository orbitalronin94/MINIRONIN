# MINIRONIN — Investigación sobre entrenamiento eficiente

**Estado:** plan de investigación; todavía no hay una receta elegida.  
**Alcance:** entrenar de forma independiente la referencia de 9,97M de parámetros. No se reutilizan workflows, scripts, configuraciones de optimizador ni checkpoints de los repositorios hermanos.

## Decisión inicial

Empezar con una referencia reproducible: predicción causal del siguiente token, secuencias pretokenizadas y empaquetadas de longitud fija, AdamW, recorte de gradiente, calentamiento seguido de decaimiento cosenoidal y checkpoints de validación fijos. Optimizar solo después de perfilar el runner real. Muon será una alternativa experimental, no una mejora asumida.

En un modelo tan pequeño, el cuello de botella puede ser la utilización de CPU/GPU, el coste de Python/lanzamiento de kernels o la alimentación de datos, no la memoria de parámetros. El objetivo es **calidad ganada por hora de pared y por token procesado**, no maximizar tokens/s de forma aislada.

## Evidencia y límites

1. Hoffmann et al. (NeurIPS 2022), *Training Compute-Optimal Large Language Models*, estudió modelos desde 70M de parámetros y mostró que los presupuestos de tokens óptimos dependen del tamaño del modelo. La heurística popular de ~20 tokens de entrenamiento por parámetro es útil para modelos grandes, pero **no es una ley validada para un modelo de 10M**. Solo la usaremos para motivar pruebas escalonadas de presupuesto.
2. La [guía de optimización de rendimiento de PyTorch](https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html) recomienda perfilar, usar operaciones fusionadas cuando proceda, `zero_grad(set_to_none=True)`, una carga de datos adecuada, precisión mixta en aceleradores compatibles y `torch.compile` cuando se amortiza su coste de compilación. Cada opción debe medirse en nuestro runner.
3. La [guía de bloques Transformer de PyTorch](https://docs.pytorch.org/tutorials/intermediate/transformer_building_blocks.html) documenta la atención escalada producto-punto fusionada y su integración con `torch.compile`. MINIRONIN ya usa SDPA; hay que comprobar qué backend se ejecuta en cada dispositivo.
4. Comparaciones recientes en GPT pequeños indican que Muon puede ser competitivo, pero el resultado depende del modelo, hardware, partición de parámetros, planificador y presupuesto de tokens. Esto justifica una prueba controlada, no demuestra que Muon sea mejor para MINIRONIN. [Comparación experimental](https://ttlab.hopto.org/blog/llm-training-2026-02-muon-measured?lang=en).

## Diseño del sistema de entrenamiento

### Flujo de datos
- Convertir documentos admitidos en fragmentos deterministas de tokens una sola vez, cuando el tokenizador esté congelado.
- Guardar los identificadores en un formato entero compacto (`uint16` basta para un vocabulario de 23.000); validar rango y endianness al leer.
- Empaquetar documentos en ventanas de contexto fijas preservando EOS/límites de documento. Nunca concatenar a través de los límites entre particiones.
- Preferir lectura secuencial o memory-mapped frente a analizar JSONL en cada paso del optimizador.
- Registrar hash SHA-256 del tokenizador, manifiesto del corpus, identificadores de particiones, versión del empaquetado y número de tokens en cada ejecución.
- Empezar con contexto 256 para medir rendimiento; comparar con 512 después de medir calidad y memoria. La configuración de producción sigue en 512 salvo evidencia en contra.

### Referencia de optimización
- AdamW con grupos separados: decaimiento para pesos matriciales; sin decaimiento para sesgos y normalizaciones. Documentar el grupo de embeddings compartidos.
- Probar tasas máximas de aprendizaje 1e-3, 3e-4 y 1e-4; descartar ejecuciones inestables o claramente infraentrenadas.
- Calentamiento del 1–3% de los pasos y después decaimiento cosenoidal hasta el 10% de la tasa máxima.
- Recorte de norma global del gradiente a 1.0; registrar norma previa al recorte y valores no finitos.
- Usar `optimizer.zero_grad(set_to_none=True)`.
- Acumular gradientes para comparar lotes efectivos de 4k, 8k y 16k tokens por actualización sin exigir un lote físico grande.
- No activar dropout, weight decay, suavizado de etiquetas ni pérdidas auxiliares sin una ablación controlada.

### Ejecución según hardware
- **CPU:** referencia FP32 primero; fijar y medir hilos intra-op de PyTorch; comparar `num_workers` 0/1/2/4 en vez de asumir que más workers ayudan. Evitar sobresuscripción de núcleos. Registrar CPU, núcleos físicos/lógicos, RAM e hilos.
- **GPU CUDA:** probar BF16 si está soportado; si no, FP16 con GradScaler. Comparar con FP32 para verificar estabilidad. Usar memoria pinned y transferencias no bloqueantes solo si benefician al flujo de datos. Registrar GPU, memoria máxima y utilización.
- **Compilación:** comparar eager y `torch.compile` tras un calentamiento; informar del tiempo de compilación por separado e incluirlo en el coste total. Evitarla en trabajos cortos si el coste domina.
- **Atención:** conservar `scaled_dot_product_attention`; registrar dispositivo, tipo de dato y disponibilidad de backend fusionado. No crear kernels propios hasta que el perfil demuestre que la atención es el cuello de botella.
- **Checkpointing:** no es necesario por defecto a esta escala salvo que el perfil de memoria muestre una limitación real; recomputar puede reducir el rendimiento.

## Escalera de experimentos

| ID | Pregunta | Variantes controladas | Métrica principal |
|---|---|---|---|
| T0 | ¿El bucle es numéricamente correcto? | 200–500 pasos, semilla fija | pérdidas/gradientes finitos; paridad al guardar/cargar |
| T1 | ¿Qué longitud de secuencia es eficiente? | 256 frente a 512, mismos tokens procesados | pérdida de validación por hora |
| T2 | ¿Qué lote de tokens conviene al runner? | 4k / 8k / 16k tokens por actualización | rendimiento y estabilidad |
| T3 | ¿Qué tasa de aprendizaje es robusta? | 1e-3 / 3e-4 / 1e-4 | pérdida con mismos tokens |
| T4 | ¿Muon supera a AdamW? | misma inicialización/datos/tokens/semilla | pérdida emparejada y tokens/s |
| T5 | ¿Ayuda la compilación? | eager frente a compilado | tiempo total, compilación incluida |
| T6 | ¿Ayuda la precisión mixta? | FP32 frente a BF16/FP16 compatible | velocidad, memoria y estabilidad |
| T7 | ¿Qué presupuesto de datos es útil? | 5M / 20M / 50M / 100M tokens | curva de validación y métricas por dominio |

Al principio se cambia una variable cada vez. Las variantes prometedoras se repiten con al menos tres semillas antes de declarar un ganador. Nunca se comparan como controladas ejecuciones con distinto número de tokens o distintos conjuntos de validación.

## Contrato de medición

Cada ejecución registra:
- ID de ejecución, SHA de Git, SHA de configuración, semilla, dispositivo, versiones de software, CPU/GPU e hilos.
- Hashes del tokenizador y manifiesto del corpus, mezcla de fuentes/dominios y tokens consumidos.
- Optimizador, planificador, tokens efectivos por actualización, longitud de secuencia y precisión.
- Tiempo total, calentamiento, tokens/s estables, pasos/s y memoria máxima.
- Entropía cruzada de entrenamiento y validación en intervalos fijos, norma de gradiente y pasos omitidos/desbordamientos.
- Métricas de validación por idioma/dominio e identificadores fijos.
- SHA-256 del checkpoint y metadatos exactos para reanudar.

Informar tanto de **tokens/s** como de **pérdida de validación con igual número de tokens procesados**. Una ejecución más rápida que aprende peor no es una mejora de eficiencia. Informar también de la mejora de pérdida por hora de pared.

## Condiciones de rechazo

- Pérdida/gradientes NaN o Inf, truncamiento silencioso, discrepancia de hashes o solapamiento entre entrenamiento y validación.
- Ejecución que no pueda reanudarse con suficiente reproducibilidad.
- Ganador de optimizador basado en una sola semilla o exposición desigual a tokens.
- Optimización de velocidad que altere materialmente el comportamiento numérico o la calidad sin aceptar explícitamente el compromiso.
- Fuente sin licencia/procedencia auditable.

## Recomendación inicial

1. Mantener AdamW + eager + FP32 como referencia de corrección.
2. Implementar empaquetado de tokens y lotes de tokens fijos antes de optimizar kernels.
3. Medir el runner real con un piloto corto y número fijo de tokens.
4. Probar BF16/FP16 y compilación solo en runners GPU compatibles.
5. Probar Muon en paralelo después de estabilizar la referencia.
6. Aumentar gradualmente el presupuesto de tokens; no asumir que la heurística 20:1 se traslada exactamente a 10M de parámetros o a un corpus pequeño y heterogéneo.

## Referencias

- Hoffmann et al., 2022. [Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556).
- PyTorch. [Guía de optimización de rendimiento](https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html).
- PyTorch. [Bloques de construcción Transformer](https://docs.pytorch.org/tutorials/intermediate/transformer_building_blocks.html).
- TT Lab, 2026. [Comparación medida entre AdamW, Muon y MUON+ en un GPT pequeño](https://ttlab.hopto.org/blog/llm-training-2026-02-muon-measured?lang=en): informe experimental independiente, no resultado universal.
