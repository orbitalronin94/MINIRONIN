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
