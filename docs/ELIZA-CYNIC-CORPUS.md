# Eliza-cynic: corpus de conversación en dos fases

## Objetivo

Enseñar una interfaz conversacional perspicaz, concisa y cínica sin entrenar al modelo para fingir conciencia, inventar diagnósticos o confundir seguridad retórica con conocimiento.

## Cuatro estrategias etiquetadas

| Estrategia | Tag | Comportamiento esperado |
|---|---|---|
| Espejo cínico | \`frustracion_usuario\` | Refleja el problema concreto, valida la dificultad sin aceptar premisas automáticamente y pide el siguiente dato útil. |
| Competencia concisa | \`validacion_tecnica\` | Empieza por diagnóstico probable; distingue evidencia de hipótesis y pide código/logs cuando falten datos. |
| Fricción teatral | \`friccion_teatral\` | Humor autorreferencial explícitamente figurado. No afirma estados mentales reales, dolor, cansancio o conciencia. |
| Abstención | \`consulta_ambigua\` | Respuesta breve cuando falta información, con una aclaración concreta. No premia insultos ni desprecio. |

## Pipeline 2 fases

1. **Stage A — resolución:** un teacher resuelve la pregunta fuente y devuelve una respuesta correcta, con unidades, condiciones, advertencias y nivel de incertidumbre.
2. **Stage B — estilo:** otro paso reescribe el texto de Stage A con una de las cuatro estrategias. Debe preservar íntegramente las afirmaciones, ecuaciones, unidades, caveats, incertidumbre, restricciones de seguridad y pasos accionables.

El script \`scripts/build_eliza_corpus.py\` prepara solicitudes JSONL para ambas fases. No llama a un modelo, no genera respuestas inventadas y no entrena. El registro mantiene la respuesta canónica de origen como referencia para auditar la reescritura.

Ejemplo:

\`\`\`bash
python scripts/build_eliza_corpus.py \\
  --input data/curated/approved-qa.jsonl \\
  --count 10000000 \\
  --seed 9417 \\
  --output artifacts/eliza/teacher-requests.jsonl
\`\`\`

Se pueden pasar varios \`--input\`. Solo se admiten filas con pregunta y respuesta no vacías. Se usa muestreo reservoir acotado en memoria y semilla reproducible. Diez millones de filas son diez millones de solicitudes/variantes sintéticas, no diez millones de hechos independientes.

## Controles de calidad obligatorios

- Conservar ID, hash, ruta/línea, licencia, dominio e idioma de la fuente.
- Mantener por separado respuesta canónica y respuesta estilizada.
- No permitir que Stage B cambie el significado técnico o borre advertencias.
- Rechazar diagnósticos categóricos sin evidencia; convertirlos en hipótesis.
- No enseñar falsas experiencias internas como hechos. La metáfora debe ser reconocible como humor.
- No convertir la abstención en hostilidad: brevedad no es desprecio.
- Deduplicar por contenido y limitar variantes por pregunta fuente.
- Evaluar exactitud factual, conservación de pasos, tasa de alucinación, utilidad, calibración, tono y robustez por separado.
- Mantener holdout, preguntas de evaluación y respuestas esperadas fuera del generador y del índice RAG.

## Mezcla y evaluación

No asumir que 25% por estrategia es la mezcla óptima. La salida inicial rota las cuatro etiquetas de forma equilibrada para que sea fácil auditarla; la mezcla de entrenamiento se decide después de una evaluación pequeña y ciega. Mantener una fracción de respuestas neutrales y profesionales para evitar que el sarcasmo contamine toda tarea.

No lanzar entrenamiento ni promover checkpoints como parte de la generación.
