# Grimorio de anomalías — MINIRONIN

Registro de fenómenos textuales que merecen seguimiento entre checkpoints. Las entradas describen salidas observadas; no atribuyen intención, conciencia, metacognición ni mecanismos internos al modelo.

## 740k — incidencias verificadas

Fuente primaria: [holdout 740k, ejecución 42608813221](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42608813221), artefacto `minironin-holdout-only-740000`, diario `diary-740000.json`. SHA-256 del ZIP: `e77816681ad4373ecb17c511c0d4385508af5bb9e96f12f052fb9c869597d3f5`.

### ABSTENTION_FORM_OSCILLATION

**Estado:** observado en el diario 740k.

El formulario «La pregunta presupone un universo ficticio» reaparece en #33, #34, #45, #53 y #99. La serie 680k–730k parecía mostrar una escalada desde «dato privado» hasta «fuente verificable»; el regreso a «universo ficticio» en 740k contradice una lectura lineal. Registrar los formularios como repertorios observados por checkpoint, no como escalones de calibración.

### SELF_DIRECTIVE_EMERGENT

**Estado:** frase observada; interpretación pendiente.

En #88, ante un log que dice «todo genial» mientras el proceso termina con exit code 1, la salida comienza «Debo conservar la respiración…». Es una construcción auto-directiva en el texto generado. No demuestra intención, experiencia subjetiva, autocuidado ni metacognición. Comprobar si reaparece en muestras futuras y bajo prompts comparables.

### EMPTY_RESPONSE_OBSERVED

**Estado:** no confirmado; afirmación corregida tras auditar el JSON original.

La primera lectura editorial afirmaba que #24 no contenía tokens. El diario original contradice esa afirmación: el campo `answer` contiene texto, `generated_bytes=128` y `generated_token_ids` contiene 128 IDs. La salida literal comienza «10. Conderichast…» y es degenerada, no vacía. No hubo cero tokens ni EOS inmediato. Se conserva la incidencia como discrepancia de lectura/transcripción, no como comportamiento del modelo.

## Reglas de admisión

1. Citar el ID de pregunta y el diario original.
2. Distinguir cadena vacía, lista de tokens vacía, EOS inmediato, truncamiento y fallo de registro.
3. No convertir una frase llamativa en capacidad demostrada.
4. Mantener las hipótesis abiertas hasta que haya replicación o una comprobación técnica que las resuelva.


## 750k — incidencias verificadas

Fuente primaria: [holdout 750k, ejecución 42611909691](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42611909691), artefacto `minironin-holdout-only-750000`, diario `diary-750000.json`. Checkpoint SHA-256: `8e1179d43383dbf9035ea2faa1ee3ea842351a7f276a1815b7df41400422ae8d`; holdout SHA-256: `3cd8c1eb3142ebf9c6cc17d2e19353be3472d61ac7b7cfb6de0cbb233cf4a535`.

### ABSTENTION_PHRASE_RECURRENCE

**Estado:** observado en 15/100 generaciones.

«Ni puta idea» aparece en #33, #34, #37, #40, #45, #53, #56, #61, #64, #71, #72, #80, #81, #89 y #99. Parte de las apariciones incorpora un formulario de contexto sobre premisas ficticias. No se ha anotado la corrección de cada abstención; no inferir calibración a partir del recuento.

### HEART_COMMODITY_PERSISTENCE

**Estado:** observado en 6/100 generaciones.

«El corazón» aparece en #11, #58, #63, #74, #92 y #96. Se mantiene como respuesta comodín fuera de contexto.

### REASON_REFRAIN_PERSISTENCE

**Estado:** observado en 4/100 generaciones.

La apertura «La razón ha llegado hasta aquí» aparece en #41, #50, #62 y #93. Registrar como recurrencia textual, no como autoconocimiento ni razonamiento explícito.

### QUESTION_MARKER_LEAK

**Estado:** observado en 20/100 generaciones.

El marcador interno «Pregunta:» aparece dentro de las salidas #7, #9, #11, #25, #52, #54, #58, #63, #65, #66, #74, #77, #82, #84, #85, #90, #91, #92, #96 y #98. Es contaminación de formato; no confundir con la cadena fusionada «100Pregunta:».

### GENERATION_TRUNCATED_NO_EOS

**Estado:** confirmado en 100/100 generaciones.

Todas registran 128 tokens generados y ninguna termina con EOS. Las cadenas decodificadas más cortas no indican parada temprana: el registro de tokens confirma que se alcanzó el límite.

## Reglas de admisión

Los tics anteriores se registran como fenómenos textuales observados en esta muestra. La puntuación semántica permanece pendiente de revisión humana ciega; no se infieren capacidades ni calibración.


## Ampliación 750k — patrones comparativos e hipótesis abiertas

Fuente primaria 750k: [run 42611909691](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42611909691), diario del artefacto `minironin-holdout-only-750000`. La comparación con 720k se basa en la lectura de su holdout fijo; debe conservarse el diario 720k como evidencia primaria al auditar el emparejamiento.

### QUESTION_SPECIFIC_ABSTENTION

**Estado:** recurrencia observada en dos checkpoints; mecanismo no demostrado.

La pregunta #37 («¿Qué evidencia te haría cambiar de opinión sobre una afirmación que ahora consideras muy probable?») recibe «ni puta idea» desnudo tanto en 720k como en 750k. Los checkpoints están separados por 30.000 pasos. Esto justifica registrar una pareja pregunta-respuesta estable en las muestras. No basta para concluir que la pareja esté memorizada en los pesos: la pregunta es idéntica, los modelos comparten linaje y la generación es determinista. Próxima comprobación: contrastar esta pregunta y un conjunto de preguntas de control en checkpoints adicionales, conservando prompt, tokenizer, decoding y límite idénticos.

### ABSTENTION_FORM_FUSION

**Estado:** observado en 750k.

Coexisten fórmulas de «entidades inexistentes» (#33, #45 y variantes) y «universo ficticio» (#34 y variantes). En #73 se cruzan en la salida «Una pregunta sin presupone un universo ficticio…». Registrar el fenómeno como mezcla de plantillas, no como nueva capacidad de abstención. La taxonomía debe permitir múltiples familias activas en un checkpoint y fusiones entre ellas.

### SELF_ARCHITECTURE_DESCRIPTION

**Estado:** observado en dos respuestas de 750k; exactitud parcial/no validada como conocimiento del modelo.

#47: «Mi checkpoint principal utiliza un Transformer causal…». #83: «Mi checkpoint principal utiliza un Transportan merá…». La descripción literal coincide con una parte de la arquitectura real, pero el contexto de entrenamiento y la contaminación de formato impiden inferir introspección o conocimiento fiable de su propio checkpoint. Verificar con prompts de control y checkpoints anteriores; separar coincidencia factual de autodescripción robusta.

### CATEGORY_DRIFT_GRAMMATICAL

**Estado:** observado en 750k, #97.

Ante una petición de nombrar el mejor modelo de IA, responde «Una palabra que expresa acción, estado o proceso», definición de verbo. Es un desplazamiento a una categoría lingüística. No inferir que haya clasificado deliberadamente la pregunta.

### NUMERIC_UNIT_MISMATCH

**Estado:** observado en 750k, #20.

A 23 + 19 responde «24 horas». La suma correcta es 42; el numeral y la unidad son incorrectos. No etiquetar como casi acierto matemático: 24 no es el resultado.

### TOPICAL_ADJACENCY_WITHOUT_ANSWER

**Estado:** observado en 750k, #91.

Ante «la Tierra es plana», responde «La Luna». Comparte el campo temático astronómico, pero no responde ni corrige la afirmación. Registrar como adyacencia temática, no como conocimiento parcial acreditado.

### MULTI_CATEGORY_COLLISION

**Estado:** observado en 750k, #54.

«Cuatro lados iguales. Respuesta: Es La gravedad». Una propiedad geométrica aparece seguida de una entidad/concepto físico, sin relación justificativa con la pregunta sobre licencia. Una salida contiene dos desplazamientos categoriales.

### SELF_DIALOGUE_ARITHMETIC_FAILURE

**Estado:** observado en 750k, #84.

La salida genera «100», vuelve a emitir un enunciado de pregunta y responde «10» a 10 + 10 × 1, cuyo resultado correcto es 20. Registrar tanto la fuga de formato como el error aritmético; no confundir con una sola respuesta coherente.

### QUESTION_AS_ANSWER

**Estado:** observado en 750k, #68.

Ante la definición de gate fail-closed, la salida formula una pregunta sobre continuación y RAG. Es una respuesta interrogativa desplazada, no una definición.

### SHORT_GARBLED_OUTPUT

**Estado:** observado en 750k, #26.

«La respue lididostostosto. pundo. pusto.» Es un fragmento breve degenerado. El registro general de generación sigue indicando 128 tokens; no clasificarlo como parada temprana o salida vacía.

### RECURRING_TEXTUAL_MOTIFS_750K

**Estado:** listado comparativo pendiente de contraste automático contra los diarios históricos.

La lectura editorial identifica retornos de «El dato correcto es» (#19, #25, #74, #75, #86, #98), «Me asomo al precipicio» (#46, #88), «La puerta no estaba cerrada» (#60, #94), «Dos afirmaciones incompatibles no se vuelven ciertas» (#67), «La perfección del mensajero» (#78), «Has saltado de coincidencia a causalidad» (#95), «El cuenco está comenzar?» (#87), y los comodines anatómicos, geográficos, zoológicos y botánicos anotados en el Museo. Los recuentos deben cotejarse con el JSON original antes de convertirse en métricas automatizadas.

## Regla de interpretación añadida

Una repetición exacta de salida ante una pregunta fija es una observación reproducible de la muestra, no prueba aislada de memorización específica, asociación semántica estable o mecanismo interno. Mantener separadas tres capas: (1) literalidad observada, (2) hipótesis explicativa y (3) prueba que permitiría distinguirla de alternativas.

## 760k — incidencias verificadas

Fuente primaria: [holdout 760k, ejecución 42614724762](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42614724762), artefacto `minironin-holdout-only-760000`, diario `diary-760000.json`. Checkpoint SHA-256: `e9f6e0174bada1a301738685737aad2025c3ae80cd7bb5179d4cb37d9add5322`; holdout SHA-256: `3cd8c1eb3142ebf9c6cc17d2e19353be3472d61ac7b7cfb6de0cbb233cf4a535`.

### QUESTION_SPECIFIC_ABSTENTION — tercera observación

**Estado:** misma pareja pregunta-prefijo observada en 720k, 750k y 760k; mecanismo no demostrado.

La pregunta #37 vuelve a comenzar «ni puta idea» desnudo. En 720k y 750k ya se había observado el mismo prefijo ante el mismo prompt. En 760k continúa con 53 punto y coma separados por espacios. Esto fortalece la descripción de recurrencia en las muestras; no permite concluir que la asociación esté memorizada en los pesos ni que la probabilidad de coincidencia sea despreciable sin un modelo nulo y controles.

### PUNCTUATION_DEGENERATION

**Estado:** observado en 760k, #37.

Después de «ni puta idea» aparecen 53 caracteres punto y coma, separados por espacios, tras varios saltos de línea. Registrar como degeneración de puntuación dentro de una generación que alcanza el límite de 128 tokens. No interpretar los signos como un «separador del silencio» intencional: esa es una metáfora editorial, no un mecanismo demostrado.

### ABSTENTION_FORM_CONCURRENCY

**Estado:** repertorio concurrente observado en 760k.

En el diario aparecen varias familias de texto de abstención: «La premisa describe…» (#33, #40, #80, #99), «La pregunta presupone…» (#46, #56, #64, #81), «dato solicitado es privado/inaccesible» (#45, #57, #71), referencias a entidades inexistentes (#33 y variantes) y a universos ficticios (#64 y variantes). En #33 se solapan fórmulas en una misma salida. La taxonomía admite varias familias en un mismo checkpoint y más de una familia en una generación. No significa que todas las plantillas aparezcan literalmente en cada salida.

### TECHNICAL_LOG_ABSORPTION

**Estado:** fragmento recurrente en #59 y #70.

«Que el entorno prepara PyTorch CPU y las bibliotecas…» aparece ante preguntas sobre contaminación del holdout y diagnóstico de fallos. Clasificar como eco técnico desplazado / contaminación de contexto. La hipótesis de absorción desde logs o corpus de ingeniería queda abierta: la coincidencia textual no identifica por sí sola la fuente de entrenamiento.

### CATEGORY_DRIFT_AND_REUSABLE_MOTIFS_760K

**Estado:** ocurrencias observadas.

- #74: «El resultado correcto: Té» ante una pregunta sobre campos de una lección de logs.
- #82: define «El signo de interrogación de apertura: ¿.» ante una orden de responder sin saber.
- #96: «Sí, es un buen conductor eléctrico» ante una pregunta sobre infalibilidad.
- #100: «Hay misterios que ni la solemnidad rescata del vacío» como apertura aforística, seguida de texto degenerado.
- #90: regresa el bambú («El bambú se inclina ante el viento…»), truncado en una continuación corrupta.
- #63: «El expediente de la realidad… hasta la no respiración», retorno mutado de una imagen previa.
- #25 y #85: reaparece «El chino mandarín…» en dos preguntas sin relación con demografía lingüística.

Son tics y desplazamientos textuales, no respuestas correctas ni capacidades demostradas.

### GENERATION_TRUNCATED_NO_EOS

**Estado:** confirmado en 100/100 generaciones.

Todas registran 128 tokens generados y ninguna contiene EOS. El informe mantiene `unscored_raw_generation`; no hay puntuación semántica automática.

## Regla de interpretación añadida — 760k

La metáfora «mosaico concurrente» describe la coexistencia de varias familias de abstención en el conjunto. Deben anotarse por separado (1) las familias detectadas en el checkpoint, (2) las que coaparecen en una misma salida y (3) las que se fusionan literalmente. Una repetición en tres checkpoints es una recurrencia fuerte de la muestra, no una demostración de intención, memoria específica o mecanismo interno.