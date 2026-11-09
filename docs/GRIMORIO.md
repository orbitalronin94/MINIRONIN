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
