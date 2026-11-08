# Asociaciones Small-World para MINIRONIN

## Decisión

Empezar por generación de puentes conceptuales dispersos en los datos, no por máscaras neuronales dentro de Mamba. El generador elige tres conceptos pseudoaleatorios de registros del mismo dominio, crea un grafo de dos aristas y produce prompts para un docente. No inventa respuestas.

## Flujo

1. Extraer términos de registros estructurados admitidos.
2. Elegir tres registros del mismo dominio con semilla reproducible.
3. Construir un puente causal, funcional, analógico o de contraste.
4. Exigir definiciones y etiquetado explícito de analogías; no fabricar hechos.
5. Conservar las tres referencias de origen y la etiqueta teacher_generation_required.
6. Auditar coherencia, factualidad, diversidad y repetición antes de aceptar respuestas.

Comando:

    python scripts/build_smallworld_bridges.py --input data/curated/engineering-lessons-v1.jsonl --input data/curated/minironin-behavior-v1.jsonl --count 50000 --seed 9417 --output artifacts/smallworld/teacher-prompts.jsonl

No llama a la red, no requiere modelo docente y no entrena. Las respuestas se generan en una fase posterior explícita.

## Métricas

- diversidad de conceptos y grafos;
- coherencia del puente, con rúbrica humana ciega;
- factualidad de las definiciones;
- analogías correctamente etiquetadas;
- repetición de plantillas y respuestas;
- mejora en transferencia frente a ejemplos lineales equivalentes.

Millones de permutaciones no equivalen a millones de ideas independientes.

## Por qué no empezar con máscaras Mamba

La dispersión arbitraria de matrices de estado no garantiza una topología Small-World útil. Puede romper estabilidad, gradientes y selectividad del SSM. Antes de tocar la arquitectura hay que definir una topología estable y compararla con la matriz densa bajo idéntico presupuesto y evaluación.

## Siguiente fase

Memoria asociativa externa: recuperar fragmentos relevantes y, con baja probabilidad, añadir un salto lateral reproducible dentro del dominio, siempre con procedencia. Comparar contra BM25/vectorial estándar y contra recuperación sin saltos. La asociación aleatoria nunca sustituye a la relevancia principal.
