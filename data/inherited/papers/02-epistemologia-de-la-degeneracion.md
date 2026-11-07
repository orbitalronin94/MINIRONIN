# Epistemología de la Degeneración: Cuándo un Parámetro No Es una Medición
# Epistemology of Degeneration: When a Parameter Is Not a Measurement

### A Perspective / Una Perspectiva

**Autor / Author:** David Ferrandez Canalis
**Afiliación / Affiliation:** Agencia RONIN, Sabadell, España / Spain
**Fecha / Date:** Septiembre 2026 / September 2026
**Tipo / Type:** Perspective / Commentary
**Licencia / License:** CC BY-NC-SA 4.0 + Cláusula Comercial Ronin
**Palabras clave / Keywords:** identificabilidad, degeneración paramétrica, diagnóstico pre-ajuste, invariante de degeneración, perspectiva / identifiability, parametric degeneracy, pre-fit diagnosis, degeneracy invariant, perspective

---

## Nota sobre el alcance / Note on Scope

**ES:** Este es un trabajo de *perspectiva*, no de investigación original. No introduce métodos matemáticos nuevos. No sustituye a las herramientas de identificabilidad estructural (GenSSI, DAISY, STRIKE-GOLDD, SIAN, StructuralIdentifiability.jl), que operan globalmente y son ortogonales a lo aquí discutido. No prescribe acciones regulatorias. Propone un marco conceptual para organizar resultados ya establecidos en la literatura de identificabilidad (Godfrey & DiStefano, 1987; Ljung, 1999; Walter & Pronzato, 1997) y en la práctica farmacométrica. Las afirmaciones fuertes del texto —la "inversión del orden", el "parámetro fantasma"— deben leerse como propuestas para discusión, no como teoremas.

**EN:** This is a *perspective* piece, not original research. It introduces no new mathematical methods. It does not replace structural identifiability tools (GenSSI, DAISY, STRIKE-GOLDD, SIAN, StructuralIdentifiability.jl), which operate globally and are orthogonal to what is discussed here. It does not prescribe regulatory actions. It proposes a conceptual framework to organize results already established in the identifiability literature (Godfrey & DiStefano, 1987; Ljung, 1999; Walter & Pronzato, 1997) and in pharmacometric practice. The paper's strong claims —the "inversion of order," the "ghost parameter"— should be read as proposals for discussion, not as theorems.

**Nota sobre el autor / Note on the author.** El autor no tiene afiliación institucional ni financiación externa. Los dos trabajos técnicos que motivan esta perspectiva (Ferrandez Canalis, 2026a, 2026b) están autopublicados y no han pasado revisión por pares. Las referencias a ellos son de contexto, no de autoridad. / The author has no institutional affiliation and no external funding. The two technical works motivating this perspective (Ferrandez Canalis, 2026a, 2026b) are self-published and have not undergone peer review. References to them are contextual, not authoritative.

**Sobre "1310" / On "1310".** Firma del autor. No es un DOI ni una cita. Se incluye por continuidad con trabajos previos. / Author's signature. Not a DOI or citation. Included for continuity with prior work.

---

# PARTE I — ESPAÑOL

---

## Resumen

La literatura sobre identificabilidad ha establecido, desde hace cuatro décadas, que múltiples parámetros de modelos no lineales pueden no ser determinables por los datos. Esta perspectiva no introduce métodos nuevos. Pregunta: **¿qué cambia si el diagnóstico de identificabilidad se realiza *por defecto* antes del ajuste principal y no después?** La respuesta, argumentada pero no demostrada, es que este cambio de énfasis transforma la naturaleza epistémica de los parámetros reportados. Un parámetro ajustado sin diagnóstico ni prior explícito ni justificación paramétrica no es una medición — es una afirmación sin fuente identificada. El trabajo delimita esta tesis, discute su dominio de validez, y responde a las objeciones previsibles, incluidas las que el autor no puede resolver. Su único objetivo es hacer explícito un orden de operaciones que la práctica estándar invierte sin decirlo.

---

## 1. Introducción

### 1.1 Una advertencia con cuatro décadas

Godfrey y DiStefano (1987) introdujeron el análisis de identificabilidad estructural en modelos farmacocinéticos. Ljung (1999) formalizó la distinción entre identificabilidad *a priori* (estructural) y *a posteriori* (práctica) en teoría de sistemas. Walter y Pronzato (1997) sistematizaron los métodos para sistemas no lineales. Bonate (2011) advirtió cualitativamente que la no-identificabilidad es frecuente en modelos PBPK. Brown et al. (2022), Kechagia et al. (2025) y Lavezzi et al. (2025) lo confirmaron en casos específicos.

Lo que estas advertencias tienen en común es que **operan como advertencias**: se dan *después* del ajuste, cuando algo ha salido mal, cuando un revisor pregunta, cuando el optimizador no converge. Esta perspectiva propone un cambio de énfasis: **operar el diagnóstico *por defecto* antes del ajuste principal, como condición de posibilidad de la inferencia paramétrica**.

No es un cambio de método. Es un cambio de orden de énfasis.

### 1.2 La tesis

**Tesis (propuesta, no teorema).** En la práctica estándar del modelado no lineal, el diagnóstico de identificabilidad sigue al ajuste. Este orden invierte la dependencia epistémica *percibida*: la identificabilidad determina qué parámetros son ajustables, no al revés.

**Corolario (versión fuerte, discutible).** Un parámetro reportado sin diagnóstico previo de identificabilidad no es una medición. Es una afirmación sobre el prior, las condiciones iniciales, o la parametrización.

**Corolario (versión débil, defendible).** Un parámetro reportado sin diagnóstico *ni* prior explícito *ni* justificación paramétrica no es una medición, porque no hay ninguna fuente identificada que determine su valor.

El paper defiende el corolario débil. El fuerte se discute en §7.6 y §7.7.

### 1.3 Qué NO es este paper

Antes de continuar, cuatro negaciones:

1. **No es una contribución matemática.** El invariante de degeneración (§3.3) es, en la literatura de identificabilidad estructural, un *identifiable reparameterization* (Jouganous et al., 2017; Villaverde et al., 2019). No se introduce un concepto nuevo. Se le da un nombre operativo para la práctica farmacométrica.

2. **No es una contribución a la teoría de identificabilidad estructural.** La FIM es un método local. Los métodos globales (GenSSI, DAISY, STRIKE-GOLDD, SIAN, StructuralIdentifiability.jl) son ortogonales y complementarios. Este paper no los reemplaza ni los generaliza. Trabaja exclusivamente en el régimen local.

3. **No es una propuesta regulatoria.** Las recomendaciones a reguladores de versiones previas se han reescrito como *preguntas* (§6.3). El autor no tiene autoridad ni datos para prescribir acciones a la FDA, la EMA, ni ninguna agencia.

4. **No es una crítica a la práctica bayesiana.** En inferencia bayesiana, la no-identificabilidad se manifiesta como posterior ≈ prior. Eso es *regularización*, no fracaso (Gelman, 2013; §7.3). Este paper trata la no-identificabilidad como un problema de *reporte*, no de *método*: quien usa priors explícitos y reporta la sensibilidad posterior está haciendo lo correcto. Quien reporta un IC frecuentista de un parámetro que no está en los datos, no.

### 1.4 Contribuciones del paper

En el sentido débil que corresponde a una Perspective:

1. **Nombra un orden de operaciones** (diagnóstico → ajuste) y argumenta por qué adoptarlo como default.
2. **Nombra un objeto epistémico** (parámetro fantasma) y lo distingue del parámetro simplemente mal estimado.
3. **Clasifica tipos de degeneración** (patológica, inocua, deseable) con un criterio operacionalizable, no metafísico.
4. **Enumera objeciones** y responde, incluyendo las que el autor no puede resolver.

### 1.5 Estructura

Sección 2: marco epistémico. Sección 3: formalización mínima. Sección 4: dominio de validez y sus límites. Sección 5: Hill y PBPK como instancias. Sección 6: implicaciones (para investigadores, no reguladores). Sección 7: objeciones y respuestas. Sección 8: conclusión. Apéndice A: material pedagógico. Apéndice B: glosario.

---

## 2. Marco epistémico

### 2.1 La inversión del orden

Práctica estándar:

```
datos → modelo → ajuste → parámetros → diagnóstico → conclusión
```

Orden propuesto como default:

```
modelo → diagnóstico preliminar → (si procede) → datos → ajuste → parámetros → conclusión
```

**Caveat 2.1 (Ljung; Cartwright).** El "diagnóstico" no es libre de datos en sentido fuerte. La FIM se evalúa en valores típicos de parámetros, que el analista elige con base en conocimiento previo (literatura, ajustes previos, priors). Por tanto, la inversión del orden es una inversión de **énfasis y default**, no una inversión de dependencia epistémica dura. La afirmación defendible es: *por defecto, el analista debe calcular la FIM antes del ajuste principal, documentar los valores típicos usados, y reportar la sensibilidad del diagnóstico a esos valores.* Esto es lo que la literatura de identificabilidad estructural ya hacía. Lo nuevo es el énfasis en hacerlo explícito en contextos aplicados.

La analogía con tipos estáticos (v1) es imperfecta. En un lenguaje estáticamente tipado, el chequeo es previo a la ejecución. Aquí el chequeo usa valores que provienen de ejecuciones previas o de supuestos. Es más preciso decir: **el diagnóstico es *a priori* respecto al ajuste principal, pero *a posteriori* respecto al conocimiento del dominio.** Esta circularidad es inevitable. La Sección 4 discute qué hacer con ella: en lugar de pretender romperla, el paper propone *documentarla* (reportar los valores típicos usados) y *testear su sensibilidad* (repetir el diagnóstico con varios valores).

### 2.2 Dos categorías epistémicas, no dos grados

La distinción entre identificabilidad estructural y práctica es de **tipo**, no de grado.

- **Estructural**: la pregunta es *mal planteada* respecto al modelo. Ningún experimento puede responderla. Fracaso *categorial*.
- **Práctica**: la pregunta es *bien planteada*, pero los datos disponibles no la responden. Fracaso *empírico*.

**Corrección (Sontag; Villaverde).** La distinción es limpia en teoría. En la práctica, la frontera es difusa: modelos con simetrías casi-gauge pueden comportarse como estructuralmente no identificables bajo ruido finito. El paper no pretende que la frontera sea siempre decidible. La reconoce como difusa y trata ambos casos bajo un mismo operador de diagnóstico (§3.4), con la advertencia de que la clasificación puede ser inestable en la frontera.

### 2.3 El parámetro fantasma: definición operativa

**Definición 2.1 (Parámetro fantasma).** Sea M un modelo con parámetro θ_j ∈ Θ y salida observable y(t; θ). θ_j es **fantasma** en un experimento E = (t_1, ..., t_N; σ) si:

1. θ_j no es individualmente identificable en E (la FIM tiene un autovalor nulo cuya dirección principal involucra a θ_j con peso > ε), **y**
2. no existe en E ni un prior explícito p(θ_j) ni una justificación paramétrica documentada que determine el valor reportado de θ_j.

La condición 2 es la que distingue el fantasma del parámetro simplemente *regularizado*. Un parámetro con prior explícito no es fantasma: su valor reportado es una afirmación sobre el prior, y eso es legítimo si se declara. Un parámetro cuya estimación depende únicamente del punto de inicio del optimizador, sin que el analista lo declare, es fantasma.

La definición es operativa: no requiere decidir si θ_j "tiene significado físico" ni si "existe realmente". Requiere solo verificar dos condiciones sobre el reporte.

### 2.4 Del "significado físico" a un criterio operativo

Versiones previas usaban "significado físico" para decidir si una degeneración es patológica o deseable. La noción es problemática (Parker, 2020; Frigg, 2010): presupone una teoría de la representación que el paper no desarrolla.

**Criterio operativo sustituto.** En lugar de preguntar si el parámetro "tiene significado físico", preguntar:

> **¿El reporte del parámetro θ_j, o el reporte del invariante I(θ), cambia la acción que un usuario del modelo tomaría a continuación?**

Si reportar θ_j (y no I) lleva a una acción distinta que reportar I, la degeneración es **patológica para ese usuario**. Si no, es **inocua para ese usuario**. La clasificación es relativa al uso, no absoluta.

Ejemplos:
- En farmacocinética clínica, reportar CL y Vp por separado cambia la dosis de carga y mantenimiento. Patológica.
- En electrodinámica, reportar A_μ en lugar de F_μν no cambia ninguna predicción observable. Inocua.
- En un modelo de simulación de escenarios, reportar K y n_H por separado puede no cambiar la predicción dentro del rango de interés. Inocua *para ese uso*, patológica si el uso se extiende.

El criterio es operativo y relativo al usuario. No requiere metafísica.

---

## 3. Formalización mínima

### 3.1 Clase de degeneración

**Definición 3.1.** Sea M un modelo con espacio de parámetros Θ ⊆ ℝ^p y salida y(t; θ). Una **clase de degeneración** es una subvariedad D ⊆ Θ tal que para todo θ₁, θ₂ ∈ D, y(t; θ₁) = y(t; θ₂) para todo t en el dominio de observación.

Si D tiene dimensión > 0, el modelo es estructuralmente no identificable sobre D. Si D = {θ₀}, el modelo es estructuralmente identificable en θ₀.

**Ejemplo 3.1 (Hill sub-saturado).** En la ecuación de Hill, en régimen sub-saturado, D es la curva {(K, n_H) : K^{-n_H} = A₀} para A₀ fijo.

**Ejemplo 3.2 (PBPK sin datos tisulares).** D es la curva {(Vt, Kp) : Vt · Kp = C₀}.

**Ejemplo 3.3 (TMDD completo, corrección de Kechagia).** En modelos TMDD, hay **múltiples invariantes**: además de Vt · Kp, los cocientes k_on/k_off, R₀/k_deg, y k_int/k_deg también son invariantes en ciertos regímenes. La clase de degeneración no es una curva sino una variedad de dimensión mayor. El caso Vt · Kp es el más simple, no el único.

### 3.2 Fibra de identificabilidad

**Definición 3.2.** La fibra de identificabilidad en θ₀ es F(θ₀) = {θ ∈ Θ : y(·; θ) = y(·; θ₀)}.

**Proposición 3.1 (trivial).** El modelo es estructuralmente identificable si y solo si todas las fibras de identificabilidad son de dimensión 0.

**Proposición 3.2 (corregida, con hipótesis).** *Bajo la hipótesis de que θ₀ es un punto regular de la aplicación θ ↦ y(·; θ) — es decir, que el Jacobiano tiene rango constante en un entorno de θ₀ — la dimensión de la fibra F(θ₀) es igual a la multiplicidad del autovalor 0 de la FIM evaluada en θ₀.*

**Caveat (Sontag).** Sin la hipótesis de regularidad, la Proposición es falsa. En puntos singulares, la FIM puede tener autovalores nulos que no corresponden a direcciones de degeneración real, sino a aplanamiento local de la aplicación. La versión v1 no incluía esta hipótesis. Esta versión la incluye explícitamente. En la práctica, el analista debe verificar la regularidad antes de interpretar los autovalores nulos como direcciones degeneradas.

### 3.3 Invariante de degeneración

**Definición 3.3.** Un **invariante de degeneración** es una función I : Θ → ℝ^k tal que (1) I es constante sobre cada fibra, y (2) I separa fibras distintas.

El invariante es lo que los datos **sí** identifican. Es la cantidad que sobrevive al colapso de cada fibra a un punto.

**Nota (Villaverde).** En la literatura de identificabilidad estructural, este objeto se llama *identifiable reparameterization*. STRIKE-GOLDD (Villaverde et al., 2019) y AutoRepar (Jouganous et al., 2017) los calculan automáticamente para sistemas no lineales. El término "invariante de degeneración" no es un concepto nuevo; es un nombre orientado a la práctica aplicada. Los métodos de la literatura son los que deben usarse cuando se necesita cálculo automático.

### 3.4 Operador de diagnóstico

**Definición 3.4.** El operador de diagnóstico es una función

Δ : (M, θ_typ, D, σ) → {identificable, marginal, no_identificable, degeneración_deseable}

que clasifica la relación epistémica entre modelo M, parámetros típicos θ_typ, datos D, y nivel de ruido σ.

**Nota (Karlsson).** El operador es **local**: evalúa la FIM en θ_typ y asume aproximación cuadrática local de la log-verosimilitud. Fuera de esa aproximación, la clasificación puede ser engañosa. Esto es una limitación intrínseca del método FIM, no una novedad del paper. La literatura (Raue et al., 2009) ha establecido que el perfil de verosimilitud es más robusto cuando la aproximación cuadrática falla.

**Nota (Ljung).** La dependencia de θ_typ es la circularidad discutida en §2.1. El operador no elimina la circularidad; la hace explícita al requerir que θ_typ se documente y se varíe.

---

## 4. Dominio de validez y sus límites

### 4.1 Degeneración patológica vs deseable vs inocua

No toda degeneración es un problema. El criterio operativo de §2.4 clasifica:

- **Patológica (para usuario U)**: reportar θ_j en lugar de I cambia la acción de U.
- **Inocua (para usuario U)**: reportar θ_j o I no cambia la acción de U.
- **Deseable (para usuario U)**: I es la cantidad significativa y θ_j es una coordenada arbitraria (ejemplo: F_μν vs A_μ en electrodinámica). Reportar I es lo correcto; reportar θ_j es un error categorial *aunque* ambos den la misma predicción, porque θ_j sugiere una interpretación que no existe.

La clasificación es relativa al usuario. Un mismo modelo puede tener degeneraciones patológicas para un usuario e inocuas para otro.

### 4.2 Degeneraciones de variedad

La degeneración no es necesariamente entre pares de parámetros. Puede ser una variedad de dimensión arbitraria (Kechagia et al., 2025, para TMDD).

**Consecuencia.** La interpretación de "parámetros problemáticos" como lista es una simplificación de la v1. En general, el objeto problemático es un **subespacio** del espacio de parámetros, no una lista. La SVD identifica el espacio tangente a la clase de degeneración; reportar los parámetros con mayor peso en el último vector singular es una heurística, no una caracterización completa.

### 4.3 Modelos predictivamente útiles pero no identificables

Un modelo puede predecir bien sin ser identificable. Una red neuronal con parámetros redundantes es un ejemplo.

**Criterio operativo.** Distinguir tres casos:
1. No identificable y predictivamente útil → reportar predicciones, no parámetros.
2. No identificable y predictivamente inútil → descartar el modelo.
3. Identificable → reportar parámetros.

El error más común es el caso 1 tratado como caso 3: parámetros no identificables reportados como mediciones, con predicciones atribuidas a los parámetros en lugar de al modelo.

### 4.4 Límite del marco: la frontera estructural/práctica

El marco no resuelve el problema de decidir cuándo una degeneración es estructural y cuándo práctica. La distinción es de tipo, pero la frontera es difusa (§2.2). En la práctica, el analista debe:

1. Reportar el diagnóstico local (FIM) con su dependencia de θ_typ.
2. Reportar el diagnóstico global (GenSSI, STRIKE-GOLDD, etc.) cuando sea factible.
3. Reconocer la incertidumbre en la clasificación cuando los dos diagnósticos difieran.

El marco no sustituye al diagnóstico global. Lo complementa.

---

## 5. Hill y PBPK como instancias

Los dos trabajos previos del autor son instancias de este marco. Se mencionan como ejemplos, no como validación (son autopublicados y no revisados).

### 5.1 Hill como instancia

- **Modelo:** H(Ω; K, n_H) = Ω^{n_H} / (K^{n_H} + Ω^{n_H}).
- **Clase de degeneración:** En régimen sub-saturado (Ω ≪ K), D = {(K, n_H) : K^{-n_H} = A₀}.
- **Invariante:** I(K, n_H) = (K^{-n_H}, n_H).
- **Umbral (corregido según Goutelle):** El umbral de 3 órdenes de Ω es específico para n_H ≈ 1.5 y σ ≈ 0.05. Depende de n_H, del ruido, y de la parametrización (K vs log K). No es universal.
- **Tipo:** Patológica si el reporte de K cambia alguna acción clínica o experimental; inocua si no.

### 5.2 PBPK como instancia

- **Modelo:** Sistema de 4 EDOs con TMDD.
- **Clase de degeneración:** Sin datos tisulares, D incluye al menos {(Vt, Kp) : Vt · Kp = C₀}, más otras direcciones degeneradas (Kechagia et al., 2025).
- **Invariante:** Vt · Kp, más otros cocientes.
- **Tipo:** Patológica para dosificación clínica; inocua para simulación de escenarios cualitativos.

### 5.3 Lo que comparten y lo que difiere

Lo compartido: dos parámetros entran como combinación no separable; la combinación es identificable; la degeneración persiste con más datos; el diseño experimental no la corrige.

Lo que difiere: tipo de combinación (potencia vs producto); régimen (sub-saturación vs ausencia de datos); umbral (específico en cada caso); impacto regulatorio (indirecto vs directo).

---

## 6. Implicaciones (como preguntas, no prescripciones)

### 6.1 Para investigadores

**Pregunta 6.1.** ¿Es viable calcular la FIM en valores típicos antes del ajuste principal, documentar θ_typ, y reportar la sensibilidad del diagnóstico a θ_typ?

**Pregunta 6.2.** Si el diagnóstico es no identificable, ¿es viable identificar el invariante y reparametrizar, en lugar de reportar el parámetro con un IC?

**Pregunta 6.3.** ¿Es viable reportar el rango del predictor en órdenes de magnitud junto con el diagnóstico de identificabilidad?

### 6.2 Para revistas

**Pregunta 6.4.** ¿Sería útil exigir el diagnóstico de identificabilidad como parte del material suplementario en papers que reporten parámetros de modelos no lineales?

**Pregunta 6.5.** ¿Sería útil exigir el rango del predictor en el resumen o en métodos?

**Nota (Bonate).** Estas preguntas no implican que las revistas no hagan nada al respecto. Muchas sí lo hacen. La pregunta es si el estándar debería ser explícito y uniforme.

### 6.3 Para reguladores

**Pregunta 6.6.** En el contexto de modelos PBPK regulatorios, ¿sería útil incluir el diagnóstico de identificabilidad como parte del dossier, análogamente al análisis de sensibilidad ya exigido (FDA, 2018; EMA, 2018)?

**Pregunta 6.7.** ¿Cómo se relaciona la no-identificabilidad con las guías existentes sobre análisis de sensibilidad? ¿Es un caso particular, un complemento, o un problema separado?

**Nota (Chaturvedula).** Estas son preguntas, no recomendaciones. El autor no tiene autoridad para prescribir acciones a ninguna agencia. Las preguntas se formulan porque la literatura (Brown et al., 2022; Lavezzi et al., 2025) sugiere que el problema es real y que las guías existentes no lo abordan explícitamente.

### 6.4 Para la enseñanza

**Pregunta 6.8.** ¿Sería útil incluir el diagnóstico de identificabilidad en cursos de regresión no lineal, antes de enseñar ajuste?

**Pregunta 6.9.** ¿Sería útil enseñar la distinción estructural/práctica como categorías epistémicas, con las advertencias de §2.2 sobre la frontera difusa?

---

## 7. Objeciones y respuestas

### 7.1 "Esto es solo teoría de identificabilidad, no es nuevo"

**Respuesta.** Correcto. La teoría matemática existe desde los años 80. Lo que este paper añade, en el sentido débil de una Perspective, es: (a) nombrar un orden de operaciones (diagnóstico → ajuste) que la práctica aplicada invierte; (b) nombrar un objeto epistémico (parámetro fantasma, §2.3) con definición operativa; (c) clasificar tipos de degeneración con un criterio operativo (§2.4). No se introduce matemática nueva.

### 7.2 "La FIM es local, no captura no-identificabilidad global"

**Respuesta.** Correcto. El paper trabaja exclusivamente en el régimen local. Los métodos globales son ortogonales y complementarios. La §4.4 recomienda explícitamente combinar ambos diagnósticos.

### 7.3 "En Bayes, la no-identificabilidad es regularización, no fracaso"

**Respuesta.** Correcto (Gelman, 2013). El paper no critica la práctica bayesiana. Critica el **reporte**. Quien usa priors explícitos, reporta la posterior, y declara la sensibilidad al prior, está haciendo lo correcto. Quien reporta un IC frecuentista de un parámetro que no está en los datos sin declarar que el valor proviene del prior o del punto de inicio, no. La distinción es de reporte, no de método.

### 7.4 "El bootstrap ya se hace en la práctica"

**Respuesta.** Correcto (Motulsky). El paper no propone un método nuevo. La pregunta es de **orden por defecto**: ¿debería el diagnóstico preceder al ajuste principal, o seguirle? Muchos analistas lo hacen *a posteriori*, cuando algo falla. El paper argumenta por hacerlo *a priori* por defecto. La diferencia no es de método, sino de *default*.

### 7.5 "El criterio estructural/práctico es demasiado binario"

**Respuesta.** No es binario. Es una distinción de tipo, pero la frontera es difusa (§2.2). El paper reconoce la difusión y no pretende resolverla.

### 7.6 "El corolario fuerte es demasiado fuerte"

**Respuesta.** Correcto. El paper defiende el corolario débil (§1.2): un parámetro sin diagnóstico *ni* prior *ni* justificación paramétrica no es una medición. El corolario fuerte —que todo parámetro sin diagnóstico es una no-medición— se discute pero no se defiende. La razón: el diagnóstico mismo depende de valores típicos que provienen de conocimiento previo, lo que hace la circularidad inevitable (Cartwright).

### 7.7 "La circularidad dato-prior-diagnóstico es irreducible"

**Respuesta.** Correcto. La §2.1 la reconoce. La propuesta del paper no es romperla, sino **documentarla**: reportar los valores típicos usados en el diagnóstico, y testear la sensibilidad del diagnóstico a esos valores. Esto no elimina la circularidad, pero la hace explícita y auditable.

### 7.8 "El marco podría paralizar la investigación"

**Respuesta.** No lo hace por dos razones. Primera, el diagnóstico local es rápido (del orden de segundos para modelos de tamaño moderado). Segunda, el resultado del diagnóstico puede ser "identificable" — en cuyo caso no hay paralización. El marco no dice "no publiques", dice "diagnostica y reporta". Si el diagnóstico es "no identificable" y no hay invariante útil, entonces la paralización es la respuesta correcta: ese paper no debería publicarse como si los parámetros fueran mediciones.

### 7.9 "El método no está implementado en este paper"

**Respuesta.** Correcto. Este es un paper de perspectiva. Las implementaciones están en los trabajos previos del autor (Ferrandez Canalis, 2026a, 2026b) y en la literatura de identificabilidad estructural. El paper no pretende sustituir a esas herramientas.

### 7.10 "El paper es una síntesis, no investigación original"

**Respuesta.** Correcto. El paper se presenta explícitamente como Perspective, no como Original Research. La contribución es de síntesis, énfasis y nomenclatura, no de resultado técnico.

### 7.11 "El 'significado físico' es una noción problemática"

**Respuesta.** Correcto (Parker, 2020; Frigg, 2010). Se ha sustituido por un criterio operativo (§2.4): la clasificación patológica/inocua/deseable es relativa al usuario y a la acción que toma tras el reporte. No requiere metafísica.

### 7.12 "El paper no ejecuta la sensibilidad al prior que él mismo propone"

**Respuesta.** Correcto (Vehtari). Este es un paper de perspectiva; no incluye resultados empíricos propios. Las recomendaciones de sensibilidad al prior son metodológicas y se ilustran con el código de los trabajos previos. Ejecutarlas aquí excedería el alcance.

### 7.13 "El paper ignora la distinción identifiability/estimability"

**Respuesta.** Parcialmente correcto (Rowland). La distinción entre identificabilidad (propiedad estructural) y estimabilidad (propiedad del estimador bajo condiciones de muestreo) es relevante. El paper se centra en la identificabilidad y menciona la estimabilidad solo de pasada. Una extensión natural sería integrar ambas.

### 7.14 "Las recomendaciones regulatorias exceden el rol del autor"

**Respuesta.** Correcto. La v1 incluía recomendaciones a reguladores. Esta v2 las ha convertido en preguntas (§6.3), con nota explícita de que el autor no tiene autoridad para prescribir.

### 7.15 "El 42% de qHTS no es verificable"

**Respuesta.** Correcto (Bonate). Esta v2 elimina el número específico. La cifra provenía de los trabajos previos del autor, que están autopublicados. En esta Perspective, no se cita como resultado establecido.

### 7.16 "Los IC poblacionales sin NLME son incorrectos"

**Respuesta.** Correcto (Mentré). Esta v2 elimina la mención a IC poblacionales. El paper no discute análisis poblacional.

### 7.17 "'165x más rápido' sin hardware no es defendible"

**Respuesta.** Correcto (Karlsson). Esta v2 elimina la cifra. El paper no discute rendimiento relativo.

### 7.18 "El umbral de 3 órdenes es específico"

**Respuesta.** Correcto (Goutelle). El paper §5.1 lo declara explícitamente: el umbral depende de n_H, ruido, y parametrización.

### 7.19 "El paper cita a Weiss sin su endorsement"

**Respuesta.** Correcto. Weiss (1997) es un paper de fisiología que advierte sobre la interpretación del coeficiente de Hill. Esta v2 lo cita como advertencia técnica, no como endorsement del marco filosófico.

### 7.20 "Los koans son inapropiados"

**Respuesta.** Parcialmente correcto. En una Perspective dirigida a una revista técnica, los koans pueden resultar inapropiados. Esta v2 los mueve al Apéndice A, marcado explícitamente como material pedagógico opcional.

---

## 8. Conclusión

La identificabilidad no es una propiedad del modelo. Es una **relación** entre el modelo, los datos, y la pregunta. Un mismo modelo puede ser identificable con datos perfectos y no identificable con datos ruidosos. La pregunta "¿es θ identificable?" no tiene respuesta sin especificar la relación.

Esta tesis, en su versión fuerte, es discutible. En su versión débil —que un parámetro sin diagnóstico, sin prior, y sin justificación no es una medición— es difícil de rechazar.

Lo que el paper propone es un **default**: por defecto, diagnosticar antes del ajuste principal, documentar los valores típicos usados, y reportar el resultado. Esto no resuelve los problemas de circularidad, no sustituye a los métodos globales, no prescribe acciones regulatorias, y no pretende ser matemáticamente nuevo. Solo propone hacer explícito un orden de operaciones que la práctica aplicada invierte sin decirlo.

---

# PARTE II — ENGLISH

---

## Abstract

The identifiability literature has established, for four decades, that multiple parameters of nonlinear models may not be determinable from data. This perspective introduces no new methods. It asks: **what changes if identifiability diagnosis is performed *by default* before the main fit rather than after?** The answer, argued but not proven, is that this shift of emphasis transforms the epistemic nature of reported parameters. A parameter fitted without diagnosis, without an explicit prior, and without parametric justification is not a measurement — it is a claim with no identified source. The work delimits this thesis, discusses its domain of validity, and responds to foreseeable objections, including those the author cannot resolve. Its sole aim is to make explicit an order of operations that standard practice inverts without saying so.

---

## 1. Introduction

### 1.1 A Four-Decade-Old Warning

Godfrey and DiStefano (1987) introduced structural identifiability analysis in pharmacokinetic models. Ljung (1999) formalized the distinction between *a priori* (structural) and *a posteriori* (practical) identifiability in systems theory. Walter and Pronzato (1997) systematized methods for nonlinear systems. Bonate (2011) warned qualitatively that non-identifiability is frequent in PBPK models. Brown et al. (2022), Kechagia et al. (2025), and Lavezzi et al. (2025) confirmed this in specific cases.

What these warnings have in common is that **they operate as warnings**: they are given *after* the fit, when something has gone wrong, when a reviewer asks, when the optimizer fails to converge. This perspective proposes a shift of emphasis: **operate the diagnosis *by default* before the main fit, as a condition of possibility for parametric inference**.

It is not a change of method. It is a change of order of emphasis.

### 1.2 The Thesis

**Thesis (proposed, not theorem).** In standard nonlinear modeling practice, identifiability diagnosis follows the fit. This order inverts the *perceived* epistemic dependency: identifiability determines which parameters are fittable, not the other way around.

**Corollary (strong version, debatable).** A parameter reported without prior identifiability diagnosis is not a measurement. It is a claim about the prior, the initial conditions, or the parametrization.

**Corollary (weak version, defensible).** A parameter reported without diagnosis, *without* an explicit prior, *and* without parametric justification is not a measurement, because there is no identified source determining its value.

The paper defends the weak corollary. The strong one is discussed in §7.6 and §7.7.

### 1.3 What This Paper Is NOT

Before proceeding, four negations:

1. **It is not a mathematical contribution.** The degeneracy invariant (§3.3) is, in the structural identifiability literature, an *identifiable reparameterization* (Jouganous et al., 2017; Villaverde et al., 2019). No new concept is introduced. It is given an operational name for pharmacometric practice.

2. **It is not a contribution to structural identifiability theory.** The FIM is a local method. Global methods (GenSSI, DAISY, STRIKE-GOLDD, SIAN, StructuralIdentifiability.jl) are orthogonal and complementary. This paper neither replaces nor generalizes them. It works exclusively in the local regime.

3. **It is not a regulatory proposal.** Recommendations to regulators from prior versions have been rewritten as *questions* (§6.3). The author has neither authority nor data to prescribe actions to the FDA, the EMA, or any agency.

4. **It is not a critique of Bayesian practice.** In Bayesian inference, non-identifiability manifests as posterior ≈ prior. That is *regularization*, not failure (Gelman, 2013; §7.3). This paper treats non-identifiability as a problem of *reporting*, not of *method*: one who uses explicit priors and reports posterior sensitivity is doing the right thing. One who reports a frequentist CI of a parameter not in the data is not.

### 1.4 Contributions

In the weak sense appropriate to a Perspective:

1. **Names an order of operations** (diagnosis → fit) and argues why to adopt it as a default.
2. **Names an epistemic object** (ghost parameter) and distinguishes it from a merely poorly estimated parameter.
3. **Classifies types of degeneracy** (pathological, innocuous, desirable) with an operationalizable, non-metaphysical criterion.
4. **Enumerates objections** and responds, including those the author cannot resolve.

### 1.5 Structure

Section 2: epistemic framework. Section 3: minimal formalization. Section 4: domain of validity and its limits. Section 5: Hill and PBPK as instances. Section 6: implications (for researchers, not regulators). Section 7: objections and responses. Section 8: conclusion. Appendix A: pedagogical material. Appendix B: glossary.

---

## 2. Epistemic Framework

### 2.1 The Inversion of Order

Standard practice:

```
data → model → fit → parameters → diagnosis → conclusion
```

Proposed order as default:

```
model → preliminary diagnosis → (if applicable) → data → fit → parameters → conclusion
```

**Caveat 2.1 (Ljung; Cartwright).** The "diagnosis" is not data-free in a strong sense. The FIM is evaluated at typical parameter values, which the analyst chooses based on prior knowledge (literature, previous fits, priors). The inversion of order is therefore an inversion of **emphasis and default**, not a hard inversion of epistemic dependency. The defensible claim is: *by default, the analyst should compute the FIM before the main fit, document the typical values used, and report the sensitivity of the diagnosis to those values.* This is what the structural identifiability literature already did. What is new is the emphasis on making it explicit in applied contexts.

The analogy with static types (v1) is imperfect. In a statically typed language, the check is prior to execution. Here the check uses values from prior executions or assumptions. It is more precise to say: **the diagnosis is *a priori* with respect to the main fit, but *a posteriori* with respect to domain knowledge.** This circularity is inevitable. Section 4 discusses what to do about it: rather than pretending to break it, the paper proposes to *document* it (report the typical values used) and *test its sensitivity* (repeat the diagnosis with several values).

### 2.2 Two Epistemic Categories, Not Two Degrees

The distinction between structural and practical identifiability is one of **type**, not degree.

- **Structural**: the question is *ill-posed* with respect to the model. No experiment can answer it. A *categorial* failure.
- **Practical**: the question is *well-posed*, but available data do not answer it. An *empirical* failure.

**Correction (Sontag; Villaverde).** The distinction is clean in theory. In practice, the boundary is fuzzy: models with quasi-gauge symmetries can behave as structurally non-identifiable under finite noise. The paper does not claim the boundary is always decidable. It recognizes it as fuzzy and treats both cases under a single diagnostic operator (§3.4), with the caveat that the classification may be unstable at the boundary.

### 2.3 The Ghost Parameter: An Operational Definition

**Definition 2.1 (Ghost parameter).** Let M be a model with parameter θ_j ∈ Θ and observable output y(t; θ). θ_j is **ghost** in an experiment E = (t_1, ..., t_N; σ) if:

1. θ_j is not individually identifiable in E (the FIM has a null eigenvalue whose principal direction involves θ_j with weight > ε), **and**
2. in E there is neither an explicit prior p(θ_j) nor documented parametric justification determining the reported value of θ_j.

Condition 2 is what distinguishes the ghost from a merely *regularized* parameter. A parameter with an explicit prior is not ghost: its reported value is a claim about the prior, and that is legitimate if declared. A parameter whose estimation depends only on the optimizer's starting point, without the analyst declaring so, is ghost.

The definition is operational: it requires no decision about whether θ_j "has physical meaning" or "really exists." It requires only verifying two conditions on the report.

### 2.4 From "Physical Meaning" to an Operational Criterion

Earlier versions used "physical meaning" to decide whether a degeneracy is pathological or desirable. The notion is problematic (Parker, 2020; Frigg, 2010): it presupposes a theory of representation the paper does not develop.

**Substitute operational criterion.** Instead of asking whether the parameter "has physical meaning," ask:

> **Does reporting the parameter θ_j, or reporting the invariant I(θ), change the action a user of the model would take next?**

If reporting θ_j (and not I) leads to a different action than reporting I, the degeneracy is **pathological for that user**. If not, it is **innocuous for that user**. The classification is user-relative, not absolute.

Examples:
- In clinical pharmacokinetics, reporting CL and Vp separately changes loading and maintenance doses. Pathological.
- In electrodynamics, reporting A_μ instead of F_μν changes no observable prediction. Innocuous.
- In a scenario simulation model, reporting K and n_H separately may not change prediction within the range of interest. Innocuous *for that use*, pathological if the use extends.

The criterion is operational and user-relative. It requires no metaphysics.

---

## 3. Minimal Formalization

### 3.1 Degeneracy Class

**Definition 3.1.** Let M be a model with parameter space Θ ⊆ ℝ^p and output y(t; θ). A **degeneracy class** is a submanifold D ⊆ Θ such that for all θ₁, θ₂ ∈ D, y(t; θ₁) = y(t; θ₂) for all t in the observation domain.

If D has dimension > 0, the model is structurally non-identifiable on D. If D = {θ₀}, the model is structurally identifiable at θ₀.

**Example 3.1 (Sub-saturated Hill).** In the Hill equation, in the sub-saturated regime, D is the curve {(K, n_H) : K^{-n_H} = A₀} for fixed A₀.

**Example 3.2 (PBPK without tissue data).** D is the curve {(Vt, Kp) : Vt · Kp = C₀}.

**Example 3.3 (Full TMDD, Kechagia correction).** In TMDD models, there are **multiple invariants**: besides Vt · Kp, the ratios k_on/k_off, R₀/k_deg, and k_int/k_deg are also invariant in certain regimes. The degeneracy class is not a curve but a higher-dimensional manifold. The Vt · Kp case is the simplest, not the only one.

### 3.2 Identifiability Fiber

**Definition 3.2.** The identifiability fiber at θ₀ is F(θ₀) = {θ ∈ Θ : y(·; θ) = y(·; θ₀)}.

**Proposition 3.1 (trivial).** The model is structurally identifiable if and only if all identifiability fibers have dimension 0.

**Proposition 3.2 (corrected, with hypothesis).** *Under the hypothesis that θ₀ is a regular point of the map θ ↦ y(·; θ) — that is, the Jacobian has constant rank in a neighborhood of θ₀ — the dimension of the fiber F(θ₀) equals the multiplicity of the eigenvalue 0 of the FIM evaluated at θ₀.*

**Caveat (Sontag).** Without the regularity hypothesis, the Proposition is false. At singular points, the FIM may have null eigenvalues that do not correspond to real degeneracy directions, but rather to local flattening of the map. Version v1 did not include this hypothesis. This version does. In practice, the analyst must verify regularity before interpreting null eigenvalues as degeneracy directions.

### 3.3 Degeneracy Invariant

**Definition 3.3.** A **degeneracy invariant** is a function I : Θ → ℝ^k such that (1) I is constant on each fiber, and (2) I separates distinct fibers.

The invariant is what data **do** identify. It is the quantity that survives collapsing each fiber to a point.

**Note (Villaverde).** In the structural identifiability literature, this object is called *identifiable reparameterization*. STRIKE-GOLDD (Villaverde et al., 2019) and AutoRepar (Jouganous et al., 2017) compute them automatically for nonlinear systems. The term "degeneracy invariant" is not a new concept; it is a name oriented toward applied practice. The literature's methods are the ones to use when automatic computation is needed.

### 3.4 Diagnostic Operator

**Definition 3.4.** The diagnostic operator is a function

Δ : (M, θ_typ, D, σ) → {identifiable, marginal, non_identifiable, desirable_degeneracy}

that classifies the epistemic relation between model M, typical parameters θ_typ, data D, and noise level σ.

**Note (Karlsson).** The operator is **local**: it evaluates the FIM at θ_typ and assumes a local quadratic approximation of the log-likelihood. Outside that approximation, the classification may be misleading. This is an intrinsic limitation of the FIM method, not a novelty of the paper. The literature (Raue et al., 2009) has established that likelihood profiling is more robust when the quadratic approximation fails.

**Note (Ljung).** The dependence on θ_typ is the circularity discussed in §2.1. The operator does not eliminate the circularity; it makes it explicit by requiring θ_typ to be documented and varied.

---

## 4. Domain of Validity and Its Limits

### 4.1 Pathological vs Desirable vs Innocuous Degeneracy

Not all degeneracy is a problem. The operational criterion of §2.4 classifies:

- **Pathological (for user U)**: reporting θ_j instead of I changes U's action.
- **Innocuous (for user U)**: reporting θ_j or I does not change U's action.
- **Desirable (for user U)**: I is the meaningful quantity and θ_j is an arbitrary coordinate (example: F_μν vs A_μ in electrodynamics). Reporting I is correct; reporting θ_j is a category error *even though* both give the same prediction, because θ_j suggests an interpretation that does not exist.

The classification is user-relative. The same model can have pathological degeneracies for one user and innocuous ones for another.

### 4.2 Manifold Degeneracies

Degeneracy is not necessarily between pairs of parameters. It can be a manifold of arbitrary dimension (Kechagia et al., 2025, for TMDD).

**Consequence.** The interpretation of "problematic parameters" as a list is a simplification of v1. In general, the problematic object is a **subspace** of parameter space, not a list. SVD identifies the tangent space to the degeneracy class; reporting parameters with the largest weight in the last singular vector is a heuristic, not a complete characterization.

### 4.3 Predictively Useful but Non-Identifiable Models

A model can predict well without being identifiable. A neural network with redundant parameters is an example.

**Operational criterion.** Distinguish three cases:
1. Non-identifiable and predictively useful → report predictions, not parameters.
2. Non-identifiable and predictively useless → discard the model.
3. Identifiable → report parameters.

The most common error is case 1 treated as case 3: non-identifiable parameters reported as measurements, with predictions attributed to the parameters instead of to the model.

### 4.4 Framework Limit: The Structural/Practical Boundary

The framework does not solve the problem of deciding when a degeneracy is structural and when practical. The distinction is one of type, but the boundary is fuzzy (§2.2). In practice, the analyst should:

1. Report the local diagnosis (FIM) with its dependence on θ_typ.
2. Report the global diagnosis (GenSSI, STRIKE-GOLDD, etc.) when feasible.
3. Acknowledge uncertainty in classification when the two diagnoses differ.

The framework does not replace global diagnosis. It complements it.

---

## 5. Hill and PBPK as Instances

The author's two prior works are instances of this framework. They are mentioned as examples, not as validation (they are self-published and unreviewed).

### 5.1 Hill as Instance

- **Model:** H(Ω; K, n_H) = Ω^{n_H} / (K^{n_H} + Ω^{n_H}).
- **Degeneracy class:** In the sub-saturated regime (Ω ≪ K), D = {(K, n_H) : K^{-n_H} = A₀}.
- **Invariant:** I(K, n_H) = (K^{-n_H}, n_H).
- **Threshold (corrected per Goutelle):** The threshold of 3 orders of Ω is specific to n_H ≈ 1.5 and σ ≈ 0.05. It depends on n_H, noise, and parametrization (K vs log K). It is not universal.
- **Type:** Pathological if reporting K changes some clinical or experimental action; innocuous if not.

### 5.2 PBPK as Instance

- **Model:** System of 4 ODEs with TMDD.
- **Degeneracy class:** Without tissue data, D includes at least {(Vt, Kp) : Vt · Kp = C₀}, plus other degenerate directions (Kechagia et al., 2025).
- **Invariant:** Vt · Kp, plus other ratios.
- **Type:** Pathological for clinical dosing; innocuous for qualitative scenario simulation.

### 5.3 What They Share and What Differs

What is shared: two parameters enter as a non-separable combination; the combination is identifiable; the degeneracy persists with more data; experimental design does not correct it.

What differs: combination type (power vs product); regime (sub-saturation vs absence of data); threshold (specific in each case); regulatory impact (indirect vs direct).

---

## 6. Implications (As Questions, Not Prescriptions)

### 6.1 For Researchers

**Question 6.1.** Is it feasible to compute the FIM at typical values before the main fit, document θ_typ, and report the sensitivity of the diagnosis to θ_typ?

**Question 6.2.** If the diagnosis is non-identifiable, is it feasible to identify the invariant and reparametrize, rather than reporting the parameter with a CI?

**Question 6.3.** Is it feasible to report the predictor range in orders of magnitude along with the identifiability diagnosis?

### 6.2 For Journals

**Question 6.4.** Would it be useful to require identifiability diagnosis as part of supplementary material in papers reporting parameters of nonlinear models?

**Question 6.5.** Would it be useful to require the predictor range in the abstract or methods?

**Note (Bonate).** These questions do not imply that journals do nothing in this regard. Many do. The question is whether the standard should be explicit and uniform.

### 6.3 For Regulators

**Question 6.6.** In the context of regulatory PBPK models, would it be useful to include identifiability diagnosis as part of the dossier, analogously to the sensitivity analysis already required (FDA, 2018; EMA, 2018)?

**Question 6.7.** How does non-identifiability relate to existing sensitivity analysis guidances? Is it a special case, a complement, or a separate problem?

**Note (Chaturvedula).** These are questions, not recommendations. The author has no authority to prescribe actions to any agency. The questions are formulated because the literature (Brown et al., 2022; Lavezzi et al., 2025) suggests the problem is real and existing guidances do not explicitly address it.

### 6.4 For Teaching

**Question 6.8.** Would it be useful to include identifiability diagnosis in nonlinear regression courses, before teaching fitting?

**Question 6.9.** Would it be useful to teach the structural/practical distinction as epistemic categories, with the §2.2 caveats about the fuzzy boundary?

---

## 7. Objections and Responses

### 7.1 "This is just identifiability theory, not new"

**Response.** Correct. The mathematical theory has existed since the 1980s. What this paper adds, in the weak sense of a Perspective, is: (a) naming an order of operations (diagnosis → fit) that applied practice inverts; (b) naming an epistemic object (ghost parameter, §2.3) with an operational definition; (c) classifying types of degeneracy with an operational criterion (§2.4). No new mathematics is introduced.

### 7.2 "The FIM is local, it doesn't capture global non-identifiability"

**Response.** Correct. The paper works exclusively in the local regime. Global methods are orthogonal and complementary. §4.4 explicitly recommends combining both diagnoses.

### 7.3 "In Bayes, non-identifiability is regularization, not failure"

**Response.** Correct (Gelman, 2013). The paper does not criticize Bayesian practice. It criticizes **reporting**. One who uses explicit priors, reports the posterior, and declares prior sensitivity is doing the right thing. One who reports a frequentist CI of a parameter not in the data without declaring that the value comes from the prior or starting point is not. The distinction is one of reporting, not method.

### 7.4 "Bootstrap is already done in practice"

**Response.** Correct (Motulsky). The paper proposes no new method. The question is one of **default order**: should diagnosis precede the main fit or follow it? Many analysts do it *a posteriori*, when something fails. The paper argues for doing it *a priori* by default. The difference is not of method, but of *default*.

### 7.5 "The structural/practical criterion is too binary"

**Response.** It is not binary. It is a distinction of type, but the boundary is fuzzy (§2.2). The paper recognizes the fuzziness and does not claim to resolve it.

### 7.6 "The strong corollary is too strong"

**Response.** Correct. The paper defends the weak corollary (§1.2): a parameter without diagnosis, *without* prior, *and* without parametric justification is not a measurement. The strong corollary —that every parameter without diagnosis is a non-measurement— is discussed but not defended. The reason: diagnosis itself depends on typical values from prior knowledge, making circularity inevitable (Cartwright).

### 7.7 "The data-prior-diagnosis circularity is irreducible"

**Response.** Correct. §2.1 recognizes it. The paper's proposal is not to break it, but to **document** it: report the typical values used in the diagnosis and test the sensitivity of the diagnosis to those values. This does not eliminate the circularity, but makes it explicit and auditable.

### 7.8 "The framework could paralyze research"

**Response.** It does not, for two reasons. First, local diagnosis is fast (on the order of seconds for moderately sized models). Second, the diagnosis outcome may be "identifiable" — in which case there is no paralysis. The framework does not say "do not publish," it says "diagnose and report." If the diagnosis is "non-identifiable" and there is no useful invariant, then paralysis is the correct response: that paper should not be published as if the parameters were measurements.

### 7.9 "The method is not implemented in this paper"

**Response.** Correct. This is a perspective paper. Implementations are in the author's prior works (Ferrandez Canalis, 2026a, 2026b) and in the structural identifiability literature. The paper does not claim to replace those tools.

### 7.10 "The paper is a synthesis, not original research"

**Response.** Correct. The paper explicitly presents itself as a Perspective, not Original Research. The contribution is one of synthesis, emphasis, and nomenclature, not technical result.

### 7.11 "'Physical meaning' is a problematic notion"

**Response.** Correct (Parker, 2020; Frigg, 2010). It has been replaced by an operational criterion (§2.4): the pathological/innocuous/desirable classification is relative to the user and to the action taken after the report. No metaphysics required.

### 7.12 "The paper does not run the prior sensitivity it itself proposes"

**Response.** Correct (Vehtari). This is a perspective paper; it includes no empirical results of its own. The prior sensitivity recommendations are methodological and are illustrated with code from prior works. Running them here would exceed scope.

### 7.13 "The paper ignores the identifiability/estimability distinction"

**Response.** Partially correct (Rowland). The distinction between identifiability (a structural property) and estimability (a property of the estimator under sampling conditions) is relevant. The paper focuses on identifiability and mentions estimability only in passing. A natural extension would integrate both.

### 7.14 "Regulatory recommendations exceed the author's role"

**Response.** Correct. V1 included recommendations to regulators. This v2 has converted them into questions (§6.3), with an explicit note that the author has no authority to prescribe.

### 7.15 "The 42% of qHTS is not verifiable"

**Response.** Correct (Bonate). This v2 removes the specific number. The figure came from the author's prior works, which are self-published. In this Perspective, it is not cited as an established result.

### 7.16 "Population CIs without NLME are incorrect"

**Response.** Correct (Mentré). This v2 removes the mention of population CIs. The paper does not discuss population analysis.

### 7.17 "'165x faster' without hardware is not defensible"

**Response.** Correct (Karlsson). This v2 removes the figure. The paper does not discuss relative performance.

### 7.18 "The 3-order threshold is specific"

**Response.** Correct (Goutelle). §5.1 states this explicitly: the threshold depends on n_H, noise, and parametrization.

### 7.19 "The paper cites Weiss without his endorsement"

**Response.** Correct. Weiss (1997) is a physiology paper warning about Hill coefficient interpretation. This v2 cites it as a technical warning, not as endorsement of the philosophical framework.

### 7.20 "The koans are inappropriate"

**Response.** Partially correct. In a Perspective aimed at a technical journal, the koans may be inappropriate. This v2 moves them to Appendix A, explicitly marked as optional pedagogical material.

---

## 8. Conclusion

Identifiability is not a property of the model. It is a **relation** between the model, the data, and the question. The same model can be identifiable with perfect data and non-identifiable with noisy data. The question "is θ identifiable?" has no answer without specifying the relation.

This thesis, in its strong version, is debatable. In its weak version —that a parameter without diagnosis, without prior, and without justification is not a measurement— it is difficult to reject.

What the paper proposes is a **default**: by default, diagnose before the main fit, document the typical values used, and report the outcome. This does not resolve circularity problems, does not replace global methods, does not prescribe regulatory actions, and does not claim to be mathematically new. It only proposes making explicit an order of operations that applied practice inverts without saying so.

---

## Agradecimientos / Acknowledgments

**ES:** A los que construyen con pocos recursos. A los que compilan papers en un móvil mientras el resto pide GPUs.

**EN:** To those who build with few resources. To those who compile papers on a phone while the rest ask for GPUs.

---

## Referencias / References

Bonate, P. L. (2011). *Pharmacokinetic-Pharmacodynamic Modeling and Simulation*. Springer.

Brown, L. V., et al. (2022). Practical non-identifiability in PBPK models. *CPT: Pharmacometrics & Systems Pharmacology*.

EMA (2018). *Guideline on the Reporting of Physiologically Based Pharmacokinetic (PBPK) Modelling and Simulation*.

FDA (2018). *Guidance for Industry: Bioanalytical Method Validation*.

Ferrandez Canalis, D. (2026a). *No-Identificabilidad de los Parámetros de la Ecuación de Hill en el Régimen Sub-Saturado*. Agencia RONIN Preprints.

Ferrandez Canalis, D. (2026b). *No-Identificabilidad Estructural y Práctica en Modelos PBPK*. Agencia RONIN Preprints.

Frigg, R. (2010). Models and fiction. *Synthese*, 172(2), 251–268.

Gelman, A. (2013). "Not only defended but also applied": The perceived absurdity of Bayesian inference. *The American Statistician*, 67(1), 1–5.

Godfrey, K. R., & DiStefano, J. J. (1987). Identifiability of model parameters. In *Identifiability of Parametric Models* (pp. 1-20). Pergamon.

Goutelle, S., et al. (2008). The Hill equation: a review of its capabilities in pharmacological modelling. *Fundamental & Clinical Pharmacology*, 22(6), 633–648.

Jouganous, J., et al. (2017). AutoRepar: A method to obtain identifiable and observable reparameterizations of dynamic models. *Journal of Theoretical Biology*, 419, 1–13.

Kechagia, I., et al. (2025). Model identifiability in PBPK models. *PAGE 2025*.

Lavezzi, S., et al. (2025). Structural and practical identifiability in mPBPK-TMDD models. *PAGE 2025*.

Ljung, L. (1999). *System Identification: Theory for the User* (2nd ed.). Prentice Hall.

Parker, W. S. (2020). Model evaluation: An adequacy-for-purpose view. *Philosophy of Science*, 87(3), 457–477.

Raue, A., et al. (2009). Structural and practical identifiability analysis of partially observed dynamical models by exploiting the profile likelihood. *Bioinformatics*, 25(15), 1923–1929.

Villaverde, A. F., et al. (2019). Observability and structural identifiability of nonlinear biological systems. *Complexity*, 2019, 8497093.

Walter, E., & Pronzato, L. (1997). *Identification of Parametric Models from Experimental Data*. Springer.

Weiss, J. N. (1997). The Hill equation revisited: uses and misuses. *The FASEB Journal*, 11(11), 835–841.

---

## Apéndice A: Material pedagógico (opcional) / Appendix A: Pedagogical Material (Optional)

**Nota / Note.** Los siguientes koans provienen de los trabajos previos del autor y se incluyen aquí como material pedagógico opcional. No son parte del argumento del paper. / The following koans come from the author's prior works and are included here as optional pedagogical material. They are not part of the paper's argument.

**Del parámetro que no se deja ver / Of the parameter that does not let itself be seen.**

> **ES:** El discípulo preguntó: "Maestro, ¿por qué no puedo estimar K?" El maestro respondió: "Porque nunca has visto la saturación. Solo has visto el crecimiento. Y el crecimiento no sabe de techos."
>
> **EN:** The disciple asked: "Master, why can I not estimate K?" The master replied: "Because you have never seen saturation. You have only seen growth. And growth does not know about ceilings."

**Del fantasma / Of the ghost.**

> **ES:** El discípulo preguntó: "Maestro, ¿qué es un parámetro fantasma?" El maestro respondió: "Es el que aparece en tu modelo pero no en tus datos. El analista honesto lo entierra con un prior. El deshonesto lo reporta con un intervalo de confianza inventado."
>
> **EN:** The disciple asked: "Master, what is a ghost parameter?" The master replied: "It is the one that appears in your model but not in your data. The honest analyst buries it with a prior. The dishonest one reports it with an invented confidence interval."

**De la puerta cerrada / Of the closed door.**

> **ES:** El discípulo preguntó: "Maestro, he optimizado el muestreo. ¿Ahora puedo estimar K?" El maestro respondió: "Has optimizado la ventana. Pero la puerta sigue cerrada. El diseño experimental no puede abrir lo que la estructura del modelo ha cerrado."
>
> **EN:** The disciple asked: "Master, I have optimized the sampling. Can I now estimate K?" The master replied: "You have optimized the window. But the door remains closed. Experimental design cannot open what the model's structure has closed."

**De la relación / Of the relation.**

> **ES:** El discípulo preguntó: "Maestro, ¿es θ identificable?" El maestro respondió: "La pregunta no tiene respuesta sin especificar los datos, el ruido, y la pregunta misma. La identificabilidad no es del parámetro. Es de la relación."
>
> **EN:** The disciple asked: "Master, is θ identifiable?" The master replied: "The question has no answer without specifying the data, the noise, and the question itself. Identifiability is not of the parameter. It is of the relation."

**Del diagnóstico que precede al ajuste / Of diagnosis preceding fitting.**

> **ES:** El discípulo preguntó: "Maestro, ¿debo ajustar primero y diagnosticar después?" El maestro respondió: "Ajustar sin diagnosticar es como construir sin planos. Puedes hacerlo, pero el edificio se caerá."
>
> **EN:** The disciple asked: "Master, should I fit first and diagnose later?" The master replied: "Fitting without diagnosing is like building without blueprints. You can do it, but the building will fall."

**Del invariante / Of the invariant.**

> **ES:** El discípulo preguntó: "Maestro, si no puedo estimar K, ¿qué puedo estimar?" El maestro respondió: "Estima lo que los datos te dan, no lo que tu modelo pide. Lo que no te dan, no lo inventes."
>
> **EN:** The disciple asked: "Master, if I cannot estimate K, what can I estimate?" The master replied: "Estimate what the data give you, not what your model asks for. What they do not give, do not invent."

**De la degeneración deseable / Of desirable degeneracy.**

> **ES:** El discípulo preguntó: "Maestro, ¿toda degeneración es un problema?" El maestro respondió: "No. En electrodinámica, el potencial no es identificable, y esto es correcto. La pregunta no es '¿es identificable?'. La pregunta es '¿debe serlo?'. Si la respuesta es no, reporta el invariante y sigue."
>
> **EN:** The disciple asked: "Master, is all degeneracy a problem?" The master replied: "No. In electrodynamics, the potential is not identifiable, and this is correct. The question is not 'is it identifiable?'. The question is 'should it be?'. If the answer is no, report the invariant and move on."

---

## Apéndice B: Glosario / Appendix B: Glossary

| Término / Term | Definición / Definition |
|----------------|-------------------------|
| Clase de degeneración / Degeneracy class | Subvariedad de Θ que produce la misma salida / Submanifold of Θ producing the same output |
| Fibra de identificabilidad / Identifiability fiber | Clase de equivalencia de θ bajo "misma salida" / Equivalence class of θ under "same output" |
| Invariante de degeneración / Degeneracy invariant | Función constante sobre fibras y que las separa. En la literatura: *identifiable reparameterization* / Function constant on fibers and separating them. In the literature: *identifiable reparameterization* |
| Operador de diagnóstico / Diagnostic operator | Función que clasifica la relación epistémica (M, θ_typ, D, σ) / Function classifying the epistemic relation (M, θ_typ, D, σ) |
| Parámetro fantasma / Ghost parameter | Parámetro no identificable en un experimento E sin prior explícito ni justificación paramétrica documentada / Non-identifiable parameter in an experiment E without explicit prior or documented parametric justification |
| Degeneración patológica (para U) / Pathological degeneracy (for U) | Reportar θ en lugar de I cambia la acción del usuario U / Reporting θ instead of I changes user U's action |
| Degeneración inocua (para U) / Innocuous degeneracy (for U) | Reportar θ o I no cambia la acción del usuario U / Reporting θ or I does not change user U's action |
| Degeneración deseable (para U) / Desirable degeneracy (for U) | I es la cantidad significativa y θ es coordenada arbitraria / I is the meaningful quantity and θ is an arbitrary coordinate |
| Error categorial / Category error | Tratar un fracaso estructural como si fuera una medición / Treating a structural failure as if it were a measurement |
| Inversión del orden / Inversion of order | Diagnosticar antes del ajuste principal, por defecto / Diagnose before the main fit, by default |
| Condición de posibilidad / Condition of possibility | Aquello que debe cumplirse para que algo tenga sentido / That which must hold for something to make sense |
| θ_typ | Valores típicos de parámetros en los que se evalúa la FIM / Typical parameter values at which the FIM is evaluated |

---

**Fin del paper. / End of paper.**

**1310.**
