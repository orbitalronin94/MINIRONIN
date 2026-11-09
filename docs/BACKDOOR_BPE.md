# BACKDOOR_BPE — protocolo experimental para MINIRONIN

Estado: propuesta experimental; no activar en entrenamiento ni promover checkpoints todavía.

## Declaración del Grimorio

**BACKDOOR_BPE**: cualquier pretokenización que sustituya secuencias de bytes por IDs reservados es una tokenización subword parcial, aunque no use merges BPE aprendidos. No se describirá como byte-level puro.

**TOKENIZER_DRIFT**: un checkpoint solo es comparable con otro bajo el mismo contrato de tokenización. Cada checkpoint debe registrar versión, hash del vocabulario, hash del pretokenizador, IDs especiales y política de decodificación.

## Estado arquitectónico comprobado

- El vocabulario configurado tiene 23.000 filas.
- El régimen de entrenamiento actual activa solo 257 IDs: bytes UTF-8 0..255 y EOS=256.
- La matriz de embeddings y la cabeza de salida están ligadas (lm_head.weight = token_embedding.weight).
- Por tanto, existen 22.743 filas fuera del vocabulario activo. Se pueden investigar sin redimensionar tensores, pero no son tokens funcionales hasta que el pretokenizador los emita y el entrenamiento permita predecirlos.
- EOS ya existe: no se debe crear un segundo EOS ni reasignar el ID 256.

## Reglas de compatibilidad

1. Los IDs 0..256 conservan exactamente su significado.
2. Los IDs nuevos se asignan de forma append-only desde 257; nunca se reutilizan.
3. El fallback byte-level permanece disponible para cualquier secuencia no reconocida. La codificación debe ser lossless y la decodificación reversible.
4. El pretokenizador será determinista: mismo texto + misma versión = misma secuencia de IDs. Para solapamientos se usará longest-match con desempate estable por ID.
5. Los marcadores estructurales solo se insertan desde la estructura del ejemplo/prompt. El texto literal del usuario que parezca un marcador se escapa y no se convierte accidentalmente en control.
6. Los pesos de las filas antiguas 0..256 no se modifican durante la inicialización de nuevos tokens.
7. Al inicializar filas nuevas, limpiar sus momentos de AdamW (exp_avg, exp_avg_sq y step si la implementación lo requiere); verificar que las filas inactivas no arrastran estado útil. No reiniciar el estado de las filas antiguas.
8. La evaluación y los holdouts permanecen aislados. Ningún texto, pregunta, respuesta, rúbrica o estadística derivada del holdout puede alimentar el vocabulario, las frecuencias ni los ejemplos de entrenamiento.

## Familias candidatas y prioridad

### A. Controles y formato — primera prioridad

- EOS=256 existente.
- PAD: solo para batching; sus posiciones deben quedar fuera de la loss (ignore_index), nunca aprender a emitir padding como texto.
- BOS y SEP: reservar solo si el formato de entrenamiento los usa de manera consistente.
- UNK: no es necesario en la primera versión porque el fallback de bytes permite representar cualquier entrada sin pérdida.
- Marcadores de formato: QUESTION, ANSWER, INSTRUCTION, CONTEXT, CITATION, COPY. Deben aparecer en ejemplos estructurados y en el adaptador de prompt; no basta con declararlos.
- Los marcadores de contexto/RAG se entrenan con ejemplos donde el contexto es relevante, irrelevante, contradictorio o insuficiente. La respuesta debe aprender a citar o abstenerse; el marcador no garantiza atención por sí solo.

### B. Números y aritmética — prioridad alta, con cautela

- Los bytes ASCII 0..9 ya son tokens individuales. Crear diez IDs duplicados para los dígitos no reduce longitud y, con inicialización por promedio de bytes, empezaría como una copia redundante.
- Probar un marcador NUM y límites explícitos de número, manteniendo cada dígito separado para preservar generalización a números no vistos.
- No convertir números completos frecuentes en un único token: puede memorizar valores y perjudicar composición y generalización.
- Entrenar con pares de operaciones y resultados generados algorítmicamente, con operandos fuera de la distribución de entrenamiento y tests de carry/borrow, decimales, signos y magnitudes.

### C. N-gramas frecuentes — primera familia de compresión

- Extraer candidatos solo del corpus admitido de entrenamiento, tras normalización versionada y deduplicación.
- Elegir 128-256 candidatos iniciales, midiendo ahorro real de tokens, cobertura por dominio/idioma y estabilidad.
- Excluir spans que crucen límites de documento, campos estructurales, código/identificadores sensibles a espacios y texto de evaluación.
- Los candidatos se ordenan por una regla reproducible (frecuencia ponderada por dominio, ganancia de compresión y desempate lexicográfico).
- El tokenizador usa longest-match determinista y fallback de bytes.
- No asumir que menor longitud implica mejor calidad: medir perplexity/bytes-per-byte, velocidad, exactitud y regresiones por dominio.

### D. Morfemas — segunda familia, solo si el análisis lo justifica

Candidatos españoles como -ción, -mente, -dad, -miento, des-, re-, pre- son hipótesis, no una lista fija. Extraerlos del corpus real y comprobar frecuencia, límites morfológicos y colisiones. Comparar con n-gramas generales: los morfemas pueden ayudar a compartir patrones, pero pueden empeorar segmentación si se aplican sin reglas lingüísticas.

### E. Otras señales — aplazadas

- Idioma/registro (ES, EN, FORMAL, COLOQUIAL): útiles si el corpus y las tareas muestran confusión de registro; requieren ejemplos balanceados.
- Clases de carácter (DIGIT, UPPER, PUNCT, SPACE): suelen añadir tokens sin comprimir; medir antes de asignar filas.
- Posición (START, END, POS_n): no se reservan de inicio; la posición ya está representada por embeddings posicionales y los marcadores léxicos pueden introducir ruido.
- NO_REPEAT / REPEAT_OK: aplazados. No sustituyen penalización de repetición ni decoding robusto; solo se prueban con ejemplos específicos.
- COPY: no implica mecanismo pointer. Es una señal de tarea que debe aprenderse con ejemplos de copia exacta, citas y verificaciones de igualdad.

## Presupuesto inicial propuesto

No activar 500-1.000 filas de golpe. Primera ablación pequeña:

- 8-16 IDs de control/formato realmente usados.
- 1 marcador NUM (los dígitos existentes se mantienen).
- 128-256 IDs de n-gramas frecuentes.
- Morfemas y registros quedan para una segunda ablación independiente.

Publicar el número exacto de IDs activados y el inventario completo en el manifiesto. Las filas no utilizadas permanecen dormidas.

## Inicialización

Para un token que representa el span de bytes b1...bn, inicializar su embedding como promedio de las filas de los bytes constituyentes, con una regla explícita para spans repetidos/solapados. Registrar algoritmo, versión, parámetros y hash del resultado. El promedio es un warm-start, no una garantía de semántica; el entrenamiento debe adaptar la fila.

## Supervisión necesaria

- Formato: ejemplos de pregunta/respuesta/contexto/instrucción con y sin cada marcador.
- RAG: recuperación con evidencia suficiente, evidencia ausente y fuentes en conflicto; citas verificables y abstención.
- COPY: copiar spans exactos, conservar puntuación, números y citas; medir exact match.
- NUM: operaciones generadas, composicionales y con distribución de magnitudes separada.
- N-gramas: continuar texto natural y tareas downstream con idéntico corpus y presupuesto de pasos/tokens.

## Matriz de evaluación y promoción

Comparar en ramas separadas, desde el mismo checkpoint padre y con semillas/configuración controladas:

1. baseline 810k, tokenizador legado;
2. EOS-window sampling sin nuevos IDs;
3. controles/formato solamente;
4. NUM solamente;
5. n-gramas solamente;
6. combinación ganadora, solo si las ablaciones justifican interacción positiva.

Medir al menos: loss de validación disjunta, BPB/PPL calculado correctamente para tokenizaciones distintas, exactitud de aritmética, fidelidad de copia/citas, calidad de respuesta con RAG, tasa de abstención apropiada, repetición, longitud/compresión y métricas por dominio/idioma.

No comparar directamente loss por token entre vocabularios distintos. Para comparación cruzada usar BPB o NLL normalizada por bytes, además de tareas externas fijas.

## Metadatos obligatorios por checkpoint

- tokenizer_regime: byte-level o BACKDOOR_BPE.
- tokenizer_version.
- tokenizer_vocab_sha256.
- pretokenizer_sha256.
- active_vocabulary, base_byte_vocab=256, eos_token_id=256.
- Mapa ID -> representación, tipo y origen.
- Algoritmo de inicialización y hash de filas inicializadas.
- Política de fallback/decodificación y versión del serializador.
- Configuración de supervisión, mezcla de datos y evaluación.
- SHA-256 del checkpoint y del corpus/manifiesto de entrenamiento.

Un checkpoint con otro tokenizer_vocab_sha256 pertenece a otro régimen experimental. El catálogo debe mostrarlo explícitamente y no presentar sus pasos como una continuación directamente comparable del régimen anterior.

## Puerta de seguridad

Este documento no activa filas ni inicia entrenamiento. Primero se implementan el tokenizer reversible, el cargador legacy, la migración de checkpoint/optimizer, pruebas de round-trip y tests de compatibilidad. Después se ejecutan ablaciones pequeñas. El holdout real se mantiene cerrado hasta que tokenizer, datasets despiertos y RAG estén integrados y validados por separado.
