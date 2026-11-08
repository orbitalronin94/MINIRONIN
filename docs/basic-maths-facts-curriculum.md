# Currículo básico de matemáticas y hechos — 25 × 50k

Este currículo añade **1.250.000 ejemplos** en 25 datasets independientes:

- **12 de matemáticas (600.000 filas):** sumas, restas, multiplicaciones, divisiones exactas, restos, comparaciones, prioridad de operaciones, cuadrados, cubos, porcentajes, fracciones y operaciones mixtas.
- **13 de hechos cotidianos (650.000 filas):** animales, cuerpo humano, astronomía, geografía, ciencias, plantas, calendario, unidades, informática, alimentos, materiales, lengua y trivialidades generales.

## Generación y trazabilidad

El generador es `scripts/generate_basic_curricula.py`; el workflow `.github/workflows/generate-basic-curricula.yml` crea los ficheros en GitHub Actions y publica el artefacto `minironin-basic-maths-facts-25x50k`. Cada dataset se entrega como JSONL comprimido en gzip y con manifiesto SHA-256 de los bytes comprimidos y descomprimidos.

Las operaciones aritméticas se calculan mediante Python; no se copian respuestas escritas a mano. Las divisiones son exactas. Las fracciones se reducen. Los ejercicios de porcentajes incluyen resultados enteros y decimales.

## Límite importante de los hechos

Cada dataset factual contiene 50.000 filas construidas a partir de **10 hechos semilla revisados**, con variaciones de formulación y contexto. No son 50.000 hechos independientes ni sustituyen una fuente enciclopédica. Antes de entrenamiento conviene revisar una muestra y contrastar los hechos con referencias fiables.

El ejemplo del ciempiés está formulado deliberadamente sin cifra universal: el número de patas varía según la especie; los ciempiés tienen un par de patas por segmento corporal. No debe enseñarse una cantidad fija como respuesta general.

## Uso

La generación no modifica checkpoints, no cambia el tokenizador y no inicia entrenamiento. El artefacto debe inspeccionarse y aprobarse por separado antes de incorporarlo al corpus entrenable.
