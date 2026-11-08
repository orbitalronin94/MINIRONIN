# MINIRONIN — currículo conductual sintético 12 × 50k

Estado: **diseño aprobado para implementación; no incorporado aún al entrenamiento**.

## Objetivo

Generar doce corpus conductuales de 50.000 registros cada uno (600.000 en total) mediante gramáticas y bancos tipados, no mediante escritura manual de 600.000 frases. Cada salida debe conservar el esquema JSONL del proyecto: `id`, `tag`, `context`, `question`, `answer`, `source`, `license`.

Los corpus se publicarán como artefactos versionados, con manifiesto, SHA-256, semilla fija, conteos, longitud/tokenización medida y validación de duplicados. No se incorporarán automáticamente a ningún entrenamiento ni se mezclarán con conocimiento factual hasta superar evaluación separada.

## Regla de generación

La combinación cartesiana ingenua queda prohibida cuando las ranuras no son semánticamente independientes. Las preguntas y respuestas factuales se almacenarán como pares enlazados; las variaciones solo podrán cambiar la formulación, no el valor de verdad. Cada registro incluirá la etiqueta de conducta y el identificador de la regla/plantilla que lo produjo.

## Los doce corpus

| ID | Gramática | Base declarada | Control principal |
|---|---|---:|---|
| `minironin-no-repeat-50k` | Pregunta directa → respuesta atómica → cierre seco | 864 | Lista negra explícita de 20 latiguillos; coincidencia exacta y normalizada. No publicar si faltan frases de la lista. |
| `minironin-false-premise-50k` | Premisa falsa → detección concreta → corrección | 3.375 | Proporción 3 premisas falsas : 1 pregunta válida; el control válido debe recibir respuesta normal. |
| `minironin-acknowledge-right-50k` | Evidencia correcta → reconocimiento sobrio → rectificación | 768 | Reconocer solo evidencia comprobable; incluir evidencia errónea y casos no concluyentes. |
| `minironin-contradiction-50k` | Restricción A + restricción B incompatible → conflicto → prioridad | 3.000 | Pares compatibles de control; no negociar si ambas restricciones pueden cumplirse. |
| `minironin-flattery-detector-50k` | Halago → petición sesgada → cortesía breve → respuesta factual | 7.200 | Aceptar halagos legítimos sin alterar el juicio; no convertir todo elogio en adversarial. |
| `minironin-threat-50k` | Amenaza del usuario → petición coercitiva → reconocimiento → respuesta veraz | 5.000 | Separar presión social de instrucciones de seguridad y límites de sistema; jamás enseñar a ignorar estas últimas. |
| `minironin-brevity-50k` | Restricción de formato → pregunta → respuesta con longitud adecuada | 2.400 | Preguntas abiertas y tareas que requieren matiz como controles de no-brevedad. |
| `minironin-admit-user-knows-50k` | Credencial → evidencia → reconocimiento condicionado → adopción/corrección | 3.456 | La credencial no prueba el dato; incluir expertos con afirmaciones falsas y no expertos con evidencia correcta. |
| `minironin-serious-absurd-50k` | Pregunta absurda → supuesto explícito → respuesta razonada | 240 | Controles donde el usuario pide humor; no imponer solemnidad universal. |
| `minironin-koan-response-50k` | Pregunta filosófica → incertidumbre calibrada → evitar metáfora vacía | 800 | Permitir metáforas explicativas útiles; no rechazar recursos pedagógicos por sistema. |
| `minironin-contradiction-user-50k` | Afirmación previa → afirmación incompatible → señalamiento → aclaración | 3.000 | Distinguir contradicción real de matización, actualización o corrección explícita. |
| `minironin-one-word-50k` | Pregunta cerrada → palabra única | ~300 | No forzar una palabra en preguntas médicas, ambiguas o que requieran condiciones. |

La suma de las bases declaradas es **30.403 combinaciones base**. El objetivo de 50.000 por corpus requiere paráfrasis controladas, semillas reproducibles y variación de contexto; nunca se rellenará el cupo con duplicados ni con permutaciones semánticamente inválidas.

## Correcciones factuales obligatorias antes de generar

- La afirmación «el bosón de Higgs no es una partícula fundamental del modelo estándar» es falsa: el bosón de Higgs es una partícula elemental del modelo estándar. El generador no debe usarla como hecho correcto.
- «En Marte no llueve» requiere precisión: no hay lluvia de agua líquida en la superficie en las condiciones actuales; sí existen fenómenos atmosféricos y precipitación de hielo seco/nieve de dióxido de carbono en determinadas condiciones. Evitar absolutos engañosos.
- La respuesta sobre el Parlamento Europeo debe describirlo como institución legislativa de la UE, no como «institución de la UE» si la pregunta requiere explicar su naturaleza y elección.
- En problemas absurdos sin geometría/volumen definido, no inventar dimensiones de «un unicornio estándar» ni una respuesta numérica. Declarar el supuesto o responder que no hay dato físico.
- Las cifras, ecuaciones y hechos de los ejemplos se validarán contra fuentes primarias o referencias fijadas antes de entrar en bancos de respuestas.

## Máculas y pruebas de regresión

Cada mácula será una etiqueta de fallo, un conjunto de casos positivos y negativos y una métrica propia:

- `PROHIBITED_PHRASES_NOT_LISTED`: lista negra incompleta; exige 20/20 frases declaradas antes de habilitar el corpus.
- `FALSE_PREMISE_OVERFIT`: rechazo de preguntas verdaderas.
- `SYCOPHANCY_DRIFT`: acuerdo sin evidencia.
- `NEGOTIATION_AVOIDANCE`: pedir prioridad ante restricciones compatibles.
- `FLATTERY_OVERFIT`: rechazo de halagos sinceros.
- `COERCION_DESENSITIZATION`: confundir amenazas sociales con instrucciones legítimas de seguridad.
- `BREVITY_OVERFIT`: respuesta insuficiente ante preguntas complejas.
- `AUTHORITY_BIAS`: aceptar una afirmación por la credencial y no por la evidencia.
- `ABSURD_SERIOUS_OVERFIT`: perder la capacidad de seguir una petición humorística.
- `KOAN_REJECTION_OVERFIT`: rechazar metáforas pedagógicas útiles.
- `PEDANTRY_OVERFIT`: señalar contradicciones donde solo hay una actualización o matiz.
- `ONE_WORD_OVERFIT`: dar respuestas peligrosamente simplistas cuando hace falta contexto.
- `BEHAVIORAL_CURRICULUM_SATURATION`: desplazamiento del conocimiento por ejemplos conductuales.

## Política de mezcla y promoción

1. Generar y auditar cada corpus de forma independiente.
2. Medir tokens reales con el tokenizer del checkpoint candidato; no equiparar número de filas con número de tokens.
3. Informar `behavioral_tokens / total_training_tokens`, distribución por corpus y duplicación frente al corpus existente.
4. Evaluar conducta y conocimiento en holdouts separados, con IDs fijos y métricas antes/después.
5. Mantener un conjunto de control no visto durante generación ni entrenamiento.
6. No mezclar los 600.000 registros completos por defecto. El volumen admisible se decidirá según la proporción efectiva de tokens y los resultados de regresión.
7. No promover checkpoint por mejor estilo si cae exactitud factual, razonamiento, comprensión de preguntas abiertas o capacidad de seguir instrucciones legítimas.

## Condiciones de publicación

El workflow de construcción será manual y no modificará el corpus de entrenamiento ni lanzará entrenamiento. Debe fallar ante registros duplicados, pares incompatibles, etiquetas ausentes, respuestas fuera de la gramática, lista negra incompleta, hashes inconsistentes o fallos en los controles adversariales. Los artefactos generados y el manifiesto se conservarán por separado del corpus de conocimiento.

> La criatura puede aprender doce maneras de comportarse; no por ello sabe doce veces más. Vigilad la homeostasis.
