# MINIRONIN — currículo de razonamiento escéptico

**Objetivo:** convertir un modelo causal de ~10M parámetros en un sistema compacto que priorice deducción válida, pruebas, evidencia contrastable, causalidad y calibración de incertidumbre. El tono puede ser seco e irónico; la personalidad no debe sustituir a la corrección.

## Regla de diseño

Los libros aportan lenguaje, conceptos e historia intelectual. No enseñan por sí solos a resolver tareas. El corpus debe combinar:
1. textos de referencia con procedencia y licencia;
2. problemas y demostraciones con soluciones verificables;
3. pares de contraste (argumento válido/inválido, correlación/causalidad, evidencia/afirmación);
4. pruebas de abstención y resistencia a presión retórica.

No se debe prometer que 5.000 libros convertirán un modelo de 10M en un razonador fuerte tras unos pocos pasos. En ese régimen, el objetivo realista es adaptar vocabulario, patrones de explicación y algunas competencias estrechas; el razonamiento general exige evaluación, ejemplos de alta calidad, destilación y más tokens de los que caben en unos pocos ciclos.

## Presupuesto de 5.000 obras/documentos

El objetivo cuenta documentos únicos con texto utilizable, no registros bibliográficos, ediciones duplicadas, páginas OCR vacías ni artículos repetidos. La asignación es un presupuesto de selección, no un recuento ya alcanzado.

| Área | Cuota | Porcentaje | Contenido |
|---|---:|---:|---|
| Lógica formal y fundamentos | 1.250 | 25% | Silogística, lógica proposicional y de predicados, validez, demostración, teoría de conjuntos |
| Matemáticas y pruebas | 1.250 | 25% | Aritmética, álgebra, geometría, combinatoria, teoría de números, análisis y demostraciones |
| Método científico y causalidad | 1.000 | 20% | Inducción, experimentación, falsabilidad, explicación, causalidad y diseño de estudios |
| Probabilidad y estadística | 600 | 12% | Bayes, incertidumbre, inferencia, sesgos de muestreo y correlación |
| Epistemología y filosofía de la ciencia | 500 | 10% | Evidencia, conocimiento, escepticismo, límites de inferencia y cambio científico |
| Retórica, falacias y argumentación | 250 | 5% | Falacias formales/informales, carga de prueba, contradicción y análisis de argumentos |
| Humanidades y ética como contraste | 150 | 3% | Historia de ideas, ética y humanismo; distinguir hechos, valores y premisas normativas |
| **Total** | **5.000** | **100%** | |

La proporción es deliberadamente poco humanista, pero no elimina las humanidades: las conserva como objeto de análisis y como contraste entre premisas descriptivas y normativas.

## Currículo de entrenamiento

No mezclar todo en un único saco ni presentar obras históricas como autoridad infalible.

- **Etapa A — adquisición documental:** textos originales, metadatos, fecha, idioma, licencia, fuente y SHA-256.
- **Etapa B — limpieza:** eliminar OCR roto, portadas, índices repetidos, duplicados exactos y casi duplicados; preservar fórmulas y estructura cuando sea posible.
- **Etapa C — segmentación:** conservar título/autor/capítulo y generar fragmentos con solapamiento controlado. No convertir cada fragmento en un supuesto libro.
- **Etapa D — tareas verificables:** generar problemas de lógica y matemáticas con solucionadores o pruebas independientes. Cada respuesta debe incluir evidencia o una derivación comprobable.
- **Etapa E — ajuste de comportamiento:** entrenar respuesta directa cuando hay base, respuesta parcial cuando la evidencia es parcial y abstención exacta `ni puta idea, la verdad` cuando no hay base.
- **Etapa F — evaluación:** holdout por obra/autor/familia de problema; medir exactitud, validez de pruebas, calibración, falsa abstención, alucinación y robustez a presión social.

## Proporción dentro de los lotes de ajuste

Como punto de partida experimental, no receta congelada:
- 45% problemas resueltos y demostraciones verificadas;
- 25% explicación de conceptos a partir de los textos;
- 15% análisis de argumentos y detección de falacias;
- 10% causalidad, probabilidad y lectura crítica de evidencia;
- 5% abstención, incertidumbre y límites de conocimiento.

El preentrenamiento documental puede usar otra mezcla. No confundir porcentaje de documentos con porcentaje de tokens: un tratado de 900 páginas no debe dominar el lote por longitud.

## Política epistemológica

1. La validez lógica no garantiza que las premisas sean verdaderas.
2. Una premisa popular, elegante, antigua o moralmente atractiva no obtiene privilegio probatorio.
3. Lo no falsable no queda automáticamente refutado: se etiqueta como no contrastable empíricamente.
4. Distinguir imposibilidad, improbabilidad, falta de evidencia y desconocimiento.
5. Un texto histórico es evidencia de lo que su autor sostuvo, no prueba de que la tesis sea correcta.
6. La ironía se dirige a la inferencia defectuosa, no a grupos humanos.
7. Si el sistema no puede justificar una respuesta, no improvisa.

## Criterio de admisión

Cada obra debe tener identificador, título, autor, fecha, idioma, dominio, URL estable, licencia y evidencia de licencia. Cada texto descargado añade formato, bytes, SHA-256, número de caracteres, calidad OCR, estado de deduplicación y partición. Los documentos sin licencia clara pueden quedar en cuarentena bibliográfica, nunca en entrenamiento.

## Límite de la meta

`5.000` es el objetivo de biblioteca, no una afirmación de 5.000 obras ya incorporadas. La primera admisión se cuenta solo cuando el texto completo se descarga, supera integridad, licencia, calidad y deduplicación, y queda registrado en el manifiesto.
