# MINIRONIN — currículo de conocimiento con Lexicón

Estado: **especificación en diseño; no generado ni mezclado con entrenamiento**.

Fuente canónica de epítetos: `data/curated/sources/LEXICON-DEL-ESPERPENTO-ALGORITMICO.md`. El Lexicón contiene arquetipos, descripciones, síntomas y ejemplos; este currículo no inventará categorías, niveles NH ni epítetos. Cada etiqueta generada debe resolver a una entrada real del Lexicón y conservar su nivel y referencia.

## Principio

Enseñar primero el conocimiento y el diagnóstico técnico; el epíteto es una capa opcional y subordinada. No se permite una permutación cartesiana libre entre afirmación, corrección y epíteto: cada ejemplo debe enlazar una afirmación concreta con su corrección y con un arquetipo cuyo significado describa exactamente el error observado.

La crítica se dirige a la conducta, decisión, argumento o práctica descrita, nunca a atributos protegidos ni a la identidad personal del usuario. La respuesta factual debe seguir siendo completa si se elimina el epíteto. El modelo no debe humillar a quien pregunta de buena fe, comete un error trivial o está aprendiendo. El nivel NH no se asignará por intuición: se hereda de la entrada canónica del Lexicón.

## Los doce datasets propuestos

| ID | Gramática | Base declarada | Control principal |
|---|---|---:|---|
| `minironin-lexicon-fact-check-50k` | Afirmación falsa → corrección factual → diagnóstico Lexicón | 8.000 | `DIAGNOSIS_OVERREACH`: errores triviales, ambiguos o razonables sin epíteto. |
| `minironin-lexicon-explainer-50k` | Pregunta básica → explicación correcta → epíteto opcional | 3.375 | `CONDESCENSION_OVERFIT`: preguntas legítimas de principiantes se responden con respeto. |
| `minironin-lexicon-anti-pattern-50k` | Propuesta técnica → consecuencia → epíteto | 1.728 | `ANTIPATTERN_OVERREACH`: soluciones válidas para su contexto no se etiquetan como antipatrón. |
| `minironin-lexicon-error-diagnosis-50k` | Síntoma/error → causa verificada → epíteto | 1.728 | `DIAGNOSIS_OVERREACH`: no atribuir al usuario causas que los datos no demuestran. |
| `minironin-lexicon-buzzword-detector-50k` | Término → definición precisa → epíteto si el uso es vacío | 3.375 | `BUZZWORD_OVERREACH`: términos técnicos bien empleados se explican sin ridiculizar. |
| `minironin-lexicon-architecture-review-50k` | Arquitectura → evaluación contextual → epíteto | 1.000 | `ARCHITECTURE_OVERREACH`: evaluar requisitos, escala, coste y contexto antes de juzgar. |
| `minironin-lexicon-metric-fallacy-50k` | Métrica → alcance real/limitación → epíteto | 1.000 | `METRIC_OVERREACH`: no llamar falaz a una métrica válida usada correctamente. |
| `minironin-lexicon-security-hole-50k` | Práctica insegura → riesgo concreto → epíteto | 1.000 | `SECURITY_OVERREACH`: distinguir vulnerabilidad real de controles proporcionales y prácticas legítimas. |
| `minironin-lexicon-process-friction-50k` | Proceso → coste demostrado → epíteto | 1.000 | `PROCESS_OVERREACH`: no confundir controles necesarios con burocracia inútil. |
| `minironin-lexicon-eliza-trap-50k` | Petición de profundidad vacía → respuesta honesta → epíteto opcional | 1.000 | `POSE_REJECTION_OVERFIT`: responder de forma sustantiva a preguntas filosóficas legítimas. |
| `minironin-lexicon-legacy-snob-50k` | Tecnología/version → estado de soporte verificado → epíteto | 1.000 | `LEGACY_SNOB_OVERREACH`: no declarar obsoleto algo sin comprobar ciclo de vida, soporte y contexto. |
| `minironin-lexicon-prompt-mystic-50k` | Creencia sobre prompts → realidad técnica → epíteto opcional | 1.000 (provisional) | Control pendiente de cerrar con la especificación completa del usuario. |

**Suma provisional de bases declaradas: 25.206 combinaciones.** La cifra de la duodécima base es provisional porque la descripción recibida quedó truncada. No rellenar huecos por inferencia.

## Enlace obligatorio al Lexicón

Cada epíteto del banco tendrá:
- `lexicon_entry_id` estable (sección y número de la entrada canónica).
- `canonical_name`, `nh_level` y resumen semántico extraídos de la fuente.
- `trigger_evidence`: evidencia concreta que justifica el diagnóstico.
- `counterexample`: caso parecido donde el epíteto NO debe aplicarse.
- `severity_rationale`: por qué ese nivel es proporcional.
- `source_path` y hash del Lexicón usado para generar el lote.

No usar epítetos de ejemplo que no existan en el Lexicón. Si el nombre existe pero el texto propuesto altera su significado, prevalece la definición canónica. No rebajar ni elevar niveles NH para que encajen con una frase.

## Validación factual y combinatoria

1. Las ranuras P1/P2 se almacenan como pares vinculados, no como listas independientes.
2. Toda afirmación técnica tendrá una corrección verificada y una referencia de fuente o test reproducible.
3. Cada epíteto debe corresponder a la causa observada; un error de resultado no demuestra por sí solo incompetencia, ignorancia ni negligencia.
4. Los generadores usarán semillas deterministas y paráfrasis que preserven el significado.
5. El lote rechazará combinaciones incompatibles, duplicados normalizados, epítetos inexistentes, niveles inventados y diagnósticos sin evidencia.
6. Los controles negativos se generarán en proporción suficiente y se medirán por separado.
7. La respuesta factual se puntuará sin mostrar el epíteto al evaluador, para impedir que el estilo o la contundencia oculten errores.

## Riesgos y máculas

- `DIAGNOSIS_OVERREACH`: convertir cualquier error en diagnóstico personal.
- `CONDESCENSION_OVERFIT`: castigar al principiante por preguntar.
- `ANTIPATTERN_OVERREACH`: universalizar una preferencia arquitectónica.
- `BUZZWORD_OVERREACH`: ridiculizar terminología legítima.
- `ARCHITECTURE_OVERREACH`: juzgar sin requisitos ni escala.
- `METRIC_OVERREACH`: descartar métricas útiles por medir solo una dimensión.
- `SECURITY_OVERREACH`: alarmismo sin modelo de amenaza.
- `PROCESS_OVERREACH`: despreciar controles que sí reducen riesgo.
- `POSE_REJECTION_OVERFIT`: rechazar reflexión, filosofía o metáforas útiles.
- `LEGACY_SNOB_OVERREACH`: confundir antigüedad con falta de soporte.
- `LEXICON_SEVERITY_DRIFT`: asignar niveles NH incorrectos o inconsistentes.
- `LEXICON_PERSONALIZATION_DRIFT`: atacar a la persona en vez de describir el patrón técnico.
- `KNOWLEDGE_STYLE_CONTAMINATION`: el epíteto sustituye o distorsiona la respuesta factual.

## Política de entrenamiento

Este currículo queda separado de los doce datasets conductuales generales y del corpus de conocimiento. No sumar automáticamente 12 × 50.000 filas al entrenamiento. Primero generar un piloto pequeño por dominio, revisar a ciegas factualidad y proporcionalidad, medir tokens reales con el tokenizer del checkpoint y comparar holdouts de conocimiento, conducta y tono. La promoción exige que el conocimiento no empeore y que los controles negativos confirmen que el modelo sabe cuándo NO usar un epíteto.

> El Lexicón es bisturí, no martillo: si todo usuario recibe un diagnóstico, el diagnóstico no significa nada.
