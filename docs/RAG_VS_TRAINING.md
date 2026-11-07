# MINIRONIN — entrenamiento frente a recuperación semántica

## Hipótesis
Para información factual/documental que debe consultarse, recuperar fragmentos pertinentes durante la inferencia puede ser más eficaz que intentar memorizar todo el corpus en los pesos. No es universal: el entrenamiento puede ser mejor para patrones, procedimientos, estilo y capacidades generalizables.

## Comparación controlada
1. **Directo/entrenado:** checkpoint MINIRONIN sin contexto recuperado.
2. **RAG:** el mismo checkpoint y decodificador, con recuperación semántica del corpus.
3. **Híbrido:** fase posterior; deberá controlar qué documentos se vieron durante el entrenamiento.

La primera implementación automatiza directo vs RAG. No modifica ni detiene el entrenamiento evolutivo de 300k.

## Protocolo
- Mismo checkpoint, SHA-256, arquitectura 9.970.176 parámetros y vocabulario activo 257.
- Mismo holdout de inferencia, IDs y rúbricas.
- El índice se construye exclusivamente con el split de entrenamiento devuelto por el cargador de corpus. No se indexan validación ni holdout.
- Corpus: texto admitido por el cargador largo: HERETIC, PRODATPHIL v0.3 y ejemplos conductuales curados.
- Embeddings: sentence-transformers/all-MiniLM-L6-v2; coseno y búsqueda exacta por bloques.
- Fragmentos de 1.200 caracteres, solapamiento 180, top-3. Se registran procedencia y puntuaciones.
- Ambos brazos usan greedy argmax y el mismo límite de generación. RAG solo añade los fragmentos recuperados al prompt.
- Vectores float16 y búsqueda por bloques para reducir memoria.

## Ejecución
El primer benchmark se lanza automáticamente al fusionar el PR; las repeticiones pueden lanzarse manualmente desde `.github/workflows/semantic-rag-benchmark.yml`. Selecciona el mejor release de ciclo disponible; si no existe, usa el checkpoint bootstrap verificado de 130k. Descarga y verifica el corpus, crea el índice, evalúa el holdout y publica `minironin-direct-vs-rag`.

## Interpretación y límites
- Coseno no equivale a relevancia validada ni a respuesta correcta.
- El holdout contiene razonamiento e instrucciones además de conocimiento; RAG no debería mejorar todas las tareas.
- El modelo actual genera bytes y puede tener limitaciones fuertes al seguir instrucciones. No se presupone que aproveche el contexto.
- El informe conserva pares de respuestas, fuentes, scores, latencia y hashes. La calidad requiere revisión humana ciega A/B.
- Fase siguiente recomendada: retrieval holdout documental con consultas y documentos relevantes etiquetados por humanos.
- No se promociona ningún checkpoint ni se modifica el bucle de entrenamiento.

## Criterio de decisión
No declarar ganador por pérdida, similitud o tasa de cambios. Puntuar pares ciegos por exactitud, fidelidad documental, procedencia, abstención, razonamiento y seguimiento de instrucciones, por dominio y latencia.
