# Epistemología Generativa: Un Protocolo para Producir Proposiciones Falsables a Escala

**Autor:** David Ferrández Canalis¹

¹ Investigador independiente. Agencia RONIN, Sabadell, España.

**Fecha:** Septiembre 2026

**Clasificación:** Filosofía de la Ciencia / Metodología / Epistemología Aplicada

**Palabras clave:** falsabilidad, generación de hipótesis, pre-registro, categorización epistémica, investigación independiente, autoetnografía, Popper, Lakatos, Mayo

**Categoría epistémica:** B (inferencia razonable desde la evidencia disponible; requiere replicación en otros programas de investigación).

---

## Resumen

La filosofía de la ciencia ha dedicado esfuerzo considerable a los criterios de **verificación** y **refutación** de hipótesis (Popper, 1959; Lakatos, 1970; Mayo, 1996). Ha dedicado esfuerzo comparativamente menor a los criterios de **generación** de hipótesis falsables, que han sido tratados principalmente desde la psicología cognitiva (Newell & Simon, 1972; Klahr & Simon, 1999; Dunbar, 1995) y la inteligencia artificial (Langley et al., 1987; Darden, 1991).

Este trabajo propone un protocolo operativo —la Epistemología Generativa (EG)— para producir proposiciones falsables a escala. El protocolo tiene cuatro componentes: (1) una **estructura de tesis falsable** en cinco partes (E, O, F, P, R); (2) un **sistema de categorización epistémica** en cuatro niveles (A/B/C/D); (3) un **protocolo de pre-registro** con matriz de confusión del mecanismo; y (4) un **ciclo generativo-formal** entre una capa exploratoria (capa 0) y una capa formal (capa 1).

El protocolo se **ilustra** mediante una **autoetnografía** del corpus PUSFRE/RONIN, un programa de investigación autodidacta que produjo, en aproximadamente dos meses, 28 tesis falsables operables (Motor Cascabel), un pre-registro de 30 dominios candidatos de los cuales 17 han sido verificados, y 1 contraejemplo documentado. La elección de la autoetnografía como metodología se justifica por la naturaleza del objeto de estudio: la investigación independiente sin institución.

**Lo que este paper es:** una propuesta metodológica con ilustración autoetnográfica.

**Lo que este paper no es:** una validación empírica del protocolo. La validación requiere aplicación a programas externos, que se plantea en el roadmap final.

---

## 1. Introducción

### 1.1 El problema

La filosofía de la ciencia ha establecido con precisión los criterios para **refutar** hipótesis. El criterio de falsabilidad de Popper (1959), la estructura de los programas de investigación de Lakatos (1970), y la inferencia estadística severa de Mayo (1996) proporcionan marcos robustos para evaluar si una hipótesis ha sido adecuadamente testeada.

Sin embargo, la misma literatura dedica atención comparativamente menor a una cuestión previa: **¿cómo se generan hipótesis falsables en primer lugar?**

Esta asimetría ha sido identificada en la literatura. Reichenbach (1938) distinguió entre "contexto de descubrimiento" y "contexto de justificación", excluyendo el primero del análisis normativo. Hanson (1958) intentó recuperar el contexto de descubrimiento como objeto de análisis, pero su trabajo fue tratado como psicología. Newell y Simon (1972) estudiaron la generación de hipótesis desde la psicología cognitiva. Klahr y Simon (1999) revisaron la literatura de descubrimiento científico. Dunbar (1995) observó cómo los científicos generan hipótesis en el laboratorio. Gigerenzer (1991) propuso que las heurísticas de descubrimiento son herramientas cognitivas. Langley et al. (1987) y Darden (1991) exploraron la generación computacional de hipótesis.

Este trabajo **complementa** esta literatura con una propuesta operativa. No pretende sustituirla. La psicología cognitiva describe cómo los científicos generan hipótesis. Este trabajo propone un **protocolo** que fuerza la operacionalización, la categorización y el pre-registro.

### 1.2 La tesis

Este trabajo propone un protocolo operativo —la Epistemología Generativa (EG)— para producir proposiciones falsables a escala. El protocolo tiene cuatro componentes:

1. **Estructura de tesis falsable.** Toda proposición falsable se descompone en cinco partes: enunciado, objeto formal, operación, firma, refutador.
2. **Categorización epistémica.** Toda afirmación se clasifica en uno de cuatro niveles: A (demostrado), B (inferencia razonable), C (hipótesis operativa), D (analogía heurística).
3. **Pre-registro con matriz de confusión.** Antes de la verificación, se pre-registran las predicciones. Después, se calcula la matriz de confusión del mecanismo.
4. **Ciclo generativo-formal.** Existe una capa exploratoria (capa 0) y una capa formal (capa 1). El ciclo entre ambas es el motor del programa.

### 1.3 Contribuciones

1. Un protocolo operativo para generar proposiciones falsables a escala.
2. Un sistema de categorización epistémica que distingue cuatro niveles de justificación.
3. Un protocolo de pre-registro con matriz de confusión del mecanismo.
4. Una autoetnografía de un programa de investigación independiente con 28 tesis operables y un pre-registro de 30 dominios candidatos.
5. Una tabla comparativa con 9 protocolos existentes de generación y verificación.
6. Un roadmap de validación externa con 3 casos planificados.

### 1.4 Estructura

Sección 2: marco teórico. Sección 3: la estructura de tesis falsable. Sección 4: el sistema de categorización epistémica. Sección 5: el protocolo de pre-registro. Sección 6: el ciclo generativo-formal. Sección 7: autoetnografía (PUSFRE/RONIN). Sección 8: comparación con protocolos existentes. Sección 9: limitaciones. Sección 10: roadmap y conclusión.

---

## 2. Marco teórico

### 2.1 Falsabilidad popperiana

Popper (1959) estableció que una proposición es científica si y solo si es **falsable**. La falsabilidad no es una propiedad de la proposición aislada, sino de la proposición junto con el sistema teórico en el que se inserta (Duhem, 1906; Quine, 1951).

### 2.2 Programas de investigación

Lakatos (1970) propuso que la unidad de análisis es el **programa de investigación**: un núcleo duro de proposiciones protegidas, rodeado de un cinturón protector de hipótesis auxiliares ajustables. Lakatos identificó la estructura del cinturón protector pero no describió el **mecanismo de generación**. Este trabajo propone un mecanismo.

### 2.3 Inferencia estadística severa

Mayo (1996, 2018) propone que la inferencia estadística es **severa** cuando la hipótesis ha pasado un test que habría fallado con alta probabilidad si la hipótesis fuera falsa.

### 2.4 Generación de hipótesis: estado del arte

La literatura sobre generación de hipótesis se organiza en cinco tradiciones:

**Psicológica.** Newell y Simon (1972) estudiaron la resolución de problemas como procesos heurísticos. Klahr y Simon (1999) revisaron la literatura. Dunbar (1995) observó científicos en laboratorio.

**Computacional.** Langley et al. (1987) y Darden (1991) exploraron la generación automática de hipótesis mediante programas de computadora.

**Heurística.** Gigerenzer (1991) propuso que las heurísticas de descubrimiento son herramientas cognitivas adaptativas.

**Abductiva.** Magnani (2001) analizó la generación de hipótesis como abducción.

**Histórica.** Nickles (1980) recopiló casos históricos. Hoyningen-Huene (2006) revisó la distinción contexto de descubrimiento / contexto de justificación.

**Lo que falta.** Un **protocolo operativo** que integre: estructura de tesis, categorización epistémica, pre-registro, y ciclo generativo-formal. Este trabajo propone ese protocolo.

### 2.5 La asimetría generación/verificación

La asimetría ha sido identificada por Reichenbach (1938) y discutida por Hoyningen-Huene (2006). Este trabajo no resuelve la asimetría. Propone un protocolo operativo para la parte generativa.

---

## 3. La estructura de tesis falsable

### 3.1 Definición

**Definición 3.1 (Tesis falsable).** Una tesis falsable es una tupla (E, O, F, P, R) donde:

- **E (Enunciado)** es un enunciado en lengua natural.
- **O (Objeto formal)** es una operación computable O: M → D.
- **F (Firma)** es la representación formal del resultado esperado.
- **P (Predicción)** es una predicción P: O(M) → B.
- **R (Refutador)** es una transformación R: M → M tal que si O(R(M)) viola P, la tesis se considera refutada.

### 3.2 Ejemplo 1: Tesis 3 del Motor Cascabel

- **E.** La autoconsistencia estilométrica de un corpus se mide como H(capa | eje), y esa entropía es un invariante del generador, no del corpus.
- **O.** Generar n textos con semilla fija, calcular H(C|E) empírica, comparar con la del corpus.
- **F.** ΔH = H_gen − H_corpus. Se espera |ΔH| < ε.
- **P.** Si ΔH varía con el tema, la invariancia se refuta.
- **R.** Variar el eje temático y recalcular ΔH.

### 3.3 Ejemplo 2: Tesis 7 del Motor Cascabel

- **E.** Todo texto tiene una firma de ocho dimensiones, estable bajo paráfrasis e inestable bajo cambio de eje.
- **O.** Calcular f(x) = (ℓ̄, σ_ℓ, TTR, δ_p, ρ_c, ρ_l, ℓ̄_p, n_p) para cada texto.
- **F.** Cociente intra/inter.
- **P.** Si el cociente ≈ 1, la tesis se refuta.
- **R.** Aplicar paráfrasis sintáctica y medir la distancia.

### 3.4 Ejemplo 3: Tesis 13 del Motor Cascabel (refutada parcialmente)

- **E.** Bajo restricciones de estilo, un texto con huecos tiene una única reconstrucción válida.
- **O.** Enumeración filtrada por validadores sobre huecos.
- **F.** |R(x)| vs k.
- **P.** Si |R(x)| crece linealmente con k, la tesis se refuta.
- **R.** Aumentar el número de huecos k y medir |R(x)|.

**Categoría epistémica.** C. El corpus declara que esta tesis fue refutada parcialmente en la práctica.

### 3.5 Ventajas de la estructura

1. **Fuerza la operacionalización.**
2. **Fuerza la predicción.**
3. **Fuerza el refutador.**
4. **Permite comparación.**
5. **Permite automatización.** El Motor Cascabel contiene un script (`refutacion_cascabel.py`) que ejecuta los 28 experimentos.

### 3.6 Reconocimiento: la estructura no es nueva

La estructura de tesis falsable (E, O, F, P, R) no es nueva. Es una formalización de práctica científica estándar. Cualquier paper que especifique hipótesis, método, resultado esperado y criterio de refutación está aplicando algo similar.

Lo que es nuevo es su **aplicación sistemática a escala**. El Motor Cascabel contiene 28 tesis con esta estructura, cada una con su operación, su firma, su predicción, y su refutador. La contribución no está en la estructura, sino en la **densidad** con la que se aplica.

### 3.7 Limitaciones

1. No aplica a todas las disciplinas. Apropiada para disciplinas donde la operación es computable. No para humanidades interpretativas.
2. Puede generar tesis triviales.
3. Depende de la calidad del refutador.

---

## 4. El sistema de categorización epistémica

### 4.1 Los cuatro niveles

**Definición 4.1 (Categoría epistémica).** Toda afirmación se clasifica en uno de cuatro niveles:

| Categoría | Significado | Ejemplo del corpus |
|-----------|-------------|-------------------|
| **A** | Demostrado analíticamente o verificado empíricamente con replicación. | Proposición 5.1 (degeneración K–α) |
| **B** | Inferencia razonable desde A, con supuestos explícitos. | Que la degeneración se rompe con Ω cubriendo 3+ órdenes |
| **C** | Hipótesis operativa. Requiere validación empírica. | Que la saturación será visible en Neural Scaling a 10^25 FLOPs |
| **D** | Analogía heurística. No es afirmación formal. | Que la degeneración K–α es "análoga" a un punto fijo de renormalización |

### 4.2 La regla de honestidad

**Regla.** Toda afirmación que no sea Categoría A debe declarar: (a) de qué resultado de Categoría A se deriva, (b) qué supuestos adicionales requiere, (c) qué evidencia empírica la sostiene.

### 4.3 Aplicación al corpus: la Autorrevisión

La *Autorrevisión del Corpus RONIN* aplica el sistema con rigor. Contiene una **escala de clasificación** (Demostrado, Definición válida, Modelo plausible, Insuficientemente justificado, Degradado), una **tabla de supervivencia** con 50+ elementos clasificados, y un **Mapa de Corrección** que enlaza cada crítica con su corrección.

Ejemplos:

| Elemento | Estado | Categoría |
|----------|--------|-----------|
| Atención softmax | Conservar | A |
| Perfil atencional | Conservar, rebautizar | B |
| Forma U | Modelo plausible | B |
| Fórmula RoPE | No presentar como consecuencia matemática | C |
| Deuda ontológica | Definición válida | B |
| Isomorfismo ecología/IA | Sobrefirmado | D |
| Exclusión competitiva | Conjetura, no teorema | C |
| Ley universal del corpus | No demostrada | D |

### 4.4 Limitaciones

1. La asignación de categorías es interpretativa.
2. No existe una categoría para "replicado por terceros".
3. La regla de honestidad puede ser performativa.

---

## 5. El protocolo de pre-registro con matriz de confusión

### 5.1 El problema

Un programa de investigación que genera múltiples proposiciones enfrenta un problema estadístico: si genera 100 proposiciones y verifica 12 con éxito, ¿es eso evidencia de que el mecanismo es correcto? Depende del número total de proposiciones evaluadas. Si solo evaluó 12 de 100 y reportó los 12 aciertos, es cherry-picking. Si evaluó las 100 y reportó 12 aciertos y 88 fallos, es ciencia.

### 5.2 El protocolo

**Algoritmo 5.1 (Pre-registro con matriz de confusión).**

```
PASO 1 — Antes de la verificación:
   - Listar todas las proposiciones candidatas
   - Para cada una, declarar predicción (PASS/FAIL) y justificación
   - Firmar el documento con fecha

PASO 2 — Definir criterios a priori:
   - Umbral de aceptación (ej. ΔBIC > 10)
   - Tamaño muestral mínimo (ej. n ≥ 100)
   - Rango de la variable independiente (ej. Ω ≥ 1.5 órdenes)

PASO 3 — Verificar todas las proposiciones:
   - No modificar el pre-registro
   - No eliminar proposiciones que fallen
   - Reportar LOAD_FAILED cuando corresponda

PASO 4 — Calcular la matriz de confusión.

PASO 5 — Reportar: todas las proposiciones, la matriz, precisión y recall.
```

### 5.3 El pre-registro de 30 dominios

**Declaración a priori (firmada 2026-09-14).**

| # | Dominio | Ω | Predicción | Estado |
|---|---------|---|------------|--------|
| 1 | Neural Scaling | log C | PASS | ✅ PASS |
| 2 | Dosis-respuesta | [L] | PASS | ✅ PASS |
| 3 | Holling II | densidad | PASS | ✅ PASS |
| 4 | Holling III | densidad | PASS | ✅ PASS |
| 5 | Debye | T | PASS | ✅ PASS |
| 6 | Species-Area | A | PASS | ✅ PASS |
| 7 | Urban Scaling | población | PASS | ✅ PASS |
| 8 | Adopción tecnológica | t | PASS | ✅ PASS |
| 9 | Red eléctrica | demanda | PASS | ✅ PASS |
| 10 | Marketing | inversión | PASS | ✅ PASS |
| 11 | Epidemiología | I | PASS | ✅ PASS |
| 12 | Farmacocinética | C | PASS | ✅ PASS |
| 13 | Fama-French | HML | FAIL | ✅ FAIL |
| 14 | Renta fija | tipos | FAIL | ✅ FAIL |
| 15 | Series con tendencia | t | FAIL | ✅ FAIL |
| 16 | Interacción directa | — | FAIL | ✅ FAIL |
| 17 | Ω < 1.5 órdenes | — | FAIL | ✅ FAIL |
| 18 | Mortalidad empresas | edad | PASS | Diseñado |
| 19 | Aprendizaje humano | práctica | PASS | Diseñado |
| 20 | Difusión de rumores | t | PASS | Diseñado |
| 21 | Crecimiento tumoral | t | PASS | Diseñado |
| 22 | Adsorción Langmuir | presión | PASS | Diseñado |
| 23 | Cinética Michaelis-Menten | [S] | PASS | Diseñado |
| 24 | Curvas de Phillips | desempleo | FAIL | Diseñado |
| 25 | Efecto Fisher | inflación | FAIL | Diseñado |
| 26 | Ley de Okun | PIB | FAIL | Diseñado |
| 27 | Reconocimiento facial | t | PASS | Diseñado |
| 28 | Consumo energético | PIB | PASS | Diseñado |
| 29 | Adopción cripto | t | FAIL | Diseñado |
| 30 | Ventas SaaS | t | PASS | Diseñado |

**Predicciones declaradas:** 18 PASS, 12 FAIL.

**Ejecución.** 17 de 30 dominios tienen resultados. Los 13 dominios restantes están diseñados pero pendientes de verificación. La ejecución completa se plantea como trabajo futuro.

### 5.4 Resultados parciales

**Dominios PASS verificados (12).**

| # | Dominio | Ω_orders | ΔBIC vs M0 | Categoría |
|---|---------|----------|------------|-----------|
| 1 | Neural Scaling | 3.0 | −14.3 | B |
| 2 | Dosis-respuesta | 3.0 | Hill explícita | A |
| 3 | Holling II | 3.0 | α_h=1 | A |
| 4 | Holling III | 3.0 | α_h=2 | A |
| 5 | Debye | 3.0 | α_h=3 | A |
| 6 | Species-Area | 6.0 | α_h=0.25 | A |
| 7 | Urban Scaling | 5.0 | ΔBIC < −10 | B |
| 8 | Adopción tecnológica | 1.5-3.0 | ΔBIC < −10 | B |
| 9 | Red eléctrica | 3.0 | ΔBIC < −10 | B |
| 10 | Marketing | 3.0 | ΔBIC < −10 | B |
| 11 | Epidemiología | 3.0-4.0 | ΔBIC < −10 | B |
| 12 | Farmacocinética | 3.0 | Hill explícita | A |

**Dominios FAIL verificados (5).**

| # | Dominio | Razón | Categoría |
|---|---------|-------|-----------|
| 13 | Fama-French | ΔBIC = +8.7 en contra | A |
| 14 | Renta fija | Estructura temporal | B |
| 15 | Series con tendencia | Dependencia Φ-Ψ-Ω | B |
| 16 | Interacción directa | Competencia pairwise | B |
| 17 | Ω < 1.5 órdenes | Degeneración K-α activa | A |

### 5.5 Matriz de confusión parcial

|  | Resultó PASS | Resultó FAIL | LOAD_FAILED |
|--|--------------|--------------|-------------|
| Predicho PASS | 12 | 0 | 0 |
| Predicho FAIL | 0 | 5 | 0 |

**Precisión:** 100%. **Recall:** 100%. **F1:** 100%.

**Advertencia.** La matriz es parcial (17/30 dominios). Los 13 dominios diseñados pero no verificados pueden alterar la precisión y el recall. La ejecución completa es necesaria antes de reportar la matriz como resultado final.

### 5.6 Tests de falso positivo

Se han ejecutado dos tests de falso positivo:

**Test 1: Falso positivo de memoria.**

- Generador: M6 (sin memoria, k=1). Detector: M7 (con memoria, k=3).
- Resultado: ΔBIC = **−681.85** (M6 gana). No hay falso positivo.

**Test 2: Falso positivo de saturación.**

- Generador: M0 (sin saturación, K → ∞). Detector: M6 (con saturación Hill).
- Resultado: ΔBIC = **−6411.34** (M0 gana). No hay falso positivo.

### 5.7 Limitaciones

1. El pre-registro está ejecutado parcialmente (17/30).
2. La selección de dominios candidatos puede ser sesgada.
3. La definición de PASS/FAIL puede ser ambigua.

---

## 6. El ciclo generativo-formal

### 6.1 Los dos niveles

**Definición 6.1 (Ciclo generativo-formal).** Un programa de investigación opera en dos niveles:

- **Capa 0 (generativa).** Exploración libre, sin presión de formalización.
- **Capa 1 (formal).** Formalización rigurosa.

### 6.2 El mecanismo del ciclo

```
Capa 0 → Capa 1: Las ideas exploradas se formalizan.
Capa 1 → Capa 0: Los resultados informan la exploración.
Ciclo: Capa 0 genera variación. Capa 1 selecciona. Capa 0 hereda.
```

### 6.3 Aplicación al corpus PUSFRE/RONIN

| Capa 0 | Capa 1 |
|--------|--------|
| Libro *El bus de datos pertenece al amo* (48 capítulos) | Tratado de Extensión del PUSFRE v4.0 |
| Posts de LinkedIn | Motor Cascabel (28 tesis operables) |
| Koans | Papers de identificabilidad (Hill, PBPK, EPIDEMIC-ID) |
| Análisis geopolítico | Manual de Campo (12 dominios verificados) |
| Crítica cultural | Protocolo de pre-registro con matriz de confusión |

### 6.4 Limitaciones

1. El ciclo puede ser asimétrico.
2. La capa 0 puede ser confundida con la capa 1.
3. El ciclo requiere tiempo y disciplina.

---

## 7. Autoetnografía: el corpus PUSFRE/RONIN

### 7.1 Justificación metodológica de la autoetnografía

Este trabajo utiliza la **autoetnografía** como metodología para documentar un programa de investigación independiente. La autoetnografía es un género establecido en ciencias sociales (Ellis, 2004; Ellis, Adams & Bochner, 2011; Anderson, 2006) que combina la observación participante con la reflexión analítica sobre la propia experiencia.

**Por qué la autoetnografía.** El objeto de estudio —la investigación independiente sin institución— es difícil de estudiar desde fuera. Los investigadores independientes no son fáciles de localizar, y su trabajo no está centralizado en repositorios institucionales. La autoetnografía permite documentar el proceso desde dentro, con acceso privilegiado a las decisiones metodológicas y a las iteraciones que caracterizan un programa de este tipo.

**Limitaciones de la autoetnografía.** La autoetnografía no puede reemplazar la validación externa. Su valor es complementario: documenta un caso con profundidad, pero no permite generalización estadística. Este trabajo reconoce explícitamente esta limitación y plantea la validación externa como trabajo futuro (§10).

**Diferencia con la vivencia personal.** La autoetnografía no es diario personal. Requiere tres elementos (Anderson, 2006): (a) membresía completa en el grupo estudiado, (b) reflexividad metodológica, (c) diálogo con la literatura. Este trabajo cumple los tres: el autor es investigador independiente (membresía), documenta sus decisiones metodológicas (reflexividad), y dialoga con la literatura de filosofía de la ciencia (diálogo).

### 7.2 Descripción del corpus

**Capa 0 (generativa).** Libro de 48 capítulos, posts en LinkedIn, koans, análisis geopolítico, crítica cultural.

**Capa 1 (formal).** Geometría del Olvido, Ecología de Agentes, Deuda Ontológica, Dinámica Unificada, Teorema Fundamental, Fundamentación Matemática, Autorrevisión, Tratado de Extensión v4.0, Manual de Campo, papers de identificabilidad (Hill, PBPK, EPIDEMIC-ID, Protocolo 50 dominios), Motor Cascabel, Epistemología de la Degeneración, Tratado del Periplo.

### 7.3 Aplicación del protocolo EG

**Estructura de tesis falsable.** El corpus contiene 28 tesis operables (Motor Cascabel) con la estructura de cinco partes (E, O, F, P, R).

**Categorización epistémica.** El corpus aplica el sistema A/B/C/D en todos sus documentos. La Autorrevisión reclasifica 50+ elementos.

**Pre-registro con matriz de confusión.** El Tratado v4.0 ejecuta dos tests de falso positivo. El diseño de 30 dominios está completo; 17 tienen resultados.

**Ciclo generativo-formal.** El libro (capa 0) alimenta los tratados (capa 1), y los tratados informan los posts posteriores (capa 0).

### 7.4 Resultados documentados

**Capa 1 (formal):**

- 28 tesis falsables operables (Motor Cascabel).
- 12 dominios verificados con la familia CES-Saturada.
- 5 dominios excluidos con mecanismo explicativo.
- 1 contraejemplo documentado (Fama-French, ΔBIC = +8.7 en contra).
- 2 papers de identificabilidad (Hill, PBPK).
- 1 paper de epidemiología (EPIDEMIC-ID).
- 1 protocolo de diagnóstico (FIM + SVD + umbrales calibrados).
- 2 tests de falso positivo ejecutados.

**Capa 0 (generativa):**

- 48 capítulos de análisis y crítica.
- Cientos de posts en LinkedIn.
- Decenas de koans.
- Un libro completo.

### 7.5 Categorización epistémica del caso

| Componente | Categoría | Justificación |
|------------|-----------|---------------|
| Estructura de tesis falsable | A | Definición operativa; 28 instancias |
| Sistema de categorización A/B/C/D | A | Definición operativa; aplicada consistentemente |
| Protocolo de pre-registro | A | Definición operativa; formalizada |
| Ciclo generativo-formal | B | Inferencia razonable desde el caso |
| Aplicación al corpus | B | Caso de estudio único |
| Resultados verificados | B | Verificación parcial (17/30) |
| Contraejemplo documentado | A | Verificación empírica con mecanismo |
| Tests de falso positivo | B | Inferencia razonable desde estructura |
| Ejecución completa del pre-registro | C | Protocolo formulado; ejecución pendiente |

### 7.6 Lecciones del caso

1. **Un programa independiente puede generar densidad de proposiciones falsables.** 28 tesis en dos meses es una densidad alta.
2. **La categorización epistémica es aplicable.**
3. **El ciclo generativo-formal puede ser productivo.**
4. **El contraejemplo documentado fortalece el programa.**
5. **El pre-registro está parcialmente ejecutado.** Este es el punto débil.

---

## 8. Comparación con protocolos existentes

### 8.1 Tabla comparativa detallada

| Criterio | Bacon (1620) | Mill (1843) | Peirce (1903) | Popper (1959) | Lakatos (1970) | Simon (1973) | Mayo (1996) | Nosek (2018) | **EG (2026)** |
|----------|--------------|-------------|---------------|---------------|----------------|--------------|-------------|--------------|---------------|
| ¿Genera hipótesis? | Sí (inducción) | Sí (métodos) | Sí (abducción) | No | No | Sí (heurística) | No | No | **Sí** |
| ¿Estructura la tesis? | No | No | Parcial | No | No | Parcial | No | No | **Sí** |
| ¿Categoriza afirmaciones? | No | No | No | No | Sí (núcleo/cinturón) | No | Sí (severidad) | No | **Sí** |
| ¿Pre-registra? | No | No | No | No | No | No | No | Sí | **Sí** |
| ¿Verifica con matriz? | No | No | No | No | No | No | Sí (severidad) | No | **Sí** |
| ¿Operativo (código)? | No | No | No | No | No | Parcial (GPS) | No | Sí | **Sí** |
| ¿Aplica a escala? | No | No | No | No | No | No | No | Sí (psicología) | **Sí (28 tesis)** |

### 8.2 Lo que EG no es

**EG no sustituye a Popper.** Popper dice cómo refutar. EG dice cómo generar.
**EG no sustituye a Lakatos.** Lakatos dice cómo estructurar programas. EG dice cómo estructurar proposiciones dentro de un programa.
**EG no sustituye a Mayo.** Mayo dice cómo evaluar severidad de tests. EG dice cómo pre-registrar tests.
**EG no sustituye a Nosek.** Nosek dice cómo pre-registrar en psicología. EG dice cómo pre-registrar en programas que generan múltiples proposiciones.

### 8.3 Lo que EG añade

**EG integra cuatro componentes** que en la literatura aparecen dispersos:
1. Estructura de tesis (de Simon, parcialmente).
2. Categorización epistémica (de Lakatos y Mayo, parcialmente).
3. Pre-registro (de Nosek).
4. Ciclo generativo-formal (nuevo como concepto operativo).

La integración es la contribución, no los componentes individuales.

---

## 9. Limitaciones

### 9.1 Exploración cuantitativa preliminar

**Protocolo exploratorio.** Se seleccionaron 20 papers publicados en *Synthese*, *Philosophy of Science*, y *Erkenntnis* (2020-2024). Para cada uno se contó el número de proposiciones falsables, el número de proposiciones categorizadas, y el número de proposiciones pre-registradas.

**Resultados.**

| Métrica | Papers académicos (media, N=20) | Corpus PUSFRE/RONIN |
|---------|--------------------------------|---------------------|
| Proposiciones falsables por paper | 2.3 (rango 1-5) | 28 (Motor Cascabel) |
| Proposiciones categorizadas | 1.2 (rango 0-3) | 50+ (Autorrevisión) |
| Proposiciones pre-registradas | 0.1 (rango 0-1) | 17 (de 30 dominios) |

**Interpretación exploratoria.** La comparación es orientativa, no concluyente. Un corpus no es un paper. Los papers académicos tienen peer review; el corpus no. Los papers académicos se publican tras años de trabajo; el corpus se publicó en dos meses. La comparación sugiere que el protocolo EG **puede** aumentar la densidad de proposiciones falsables, pero no **demuestra** que lo haga.

### 9.2 Limitaciones metodológicas

1. El caso de estudio es único.
2. El pre-registro está parcialmente ejecutado.
3. La categorización epistémica es interpretativa.
4. El ciclo generativo-formal no está cuantificado.

### 9.3 Limitaciones epistemológicas

1. El caso de estudio es autopublicado.
2. El autor del paper es el sujeto del caso.
3. La efectividad del protocolo no está cuantificada con grupo control.
4. La categorización epistémica puede ser performativa.

### 9.4 Limitaciones de aplicación

1. El protocolo es intensivo en tiempo.
2. El protocolo es intensivo en disciplina.
3. El protocolo no sustituye a la verificación externa.
4. El protocolo no sustituye a la revisión por pares.

### 9.5 Limitaciones del caso

1. Los 12 dominios verificados son un subconjunto de los 30 candidatos.
2. Los 5 dominios excluidos podrían estar incompletos.
3. El contraejemplo documentado es uno solo.
4. La validación externa es limitada (2 dominios: Neural Scaling positivo, Fama-French negativo).

---

## 10. Roadmap de validación y conclusión

### 10.1 Plan de validación externa

**Fase 1 (meses 1-2): Completar el pre-registro interno.**

- Verificar los 13 dominios pendientes.
- Calcular la matriz de confusión final (30 dominios).

**Fase 2 (meses 3-6): Aplicar el protocolo a 3 casos externos.**

**Candidatos para casos externos.**

- **Caso A.** Un investigador independiente en filosofía de la ciencia que publique en PhilSci-Archive sin afiliación.
- **Caso B.** Un programa de ciencia ciudadana (Zooniverse, Foldit, eBird).
- **Caso C.** Un investigador autodidacta en ML que publique en arXiv sin afiliación.

**Protocolo para casos externos.**

1. Contactar al investigador con propuesta de colaboración.
2. Aplicar el protocolo EG a su corpus público.
3. Reportar: número de proposiciones, categorización, pre-registro.
4. Publicar paper conjunto con co-autoría.

**Fase 3 (meses 7-12): Publicar el paper conjunto.**

- Paper: "Epistemología Generativa: Un Protocolo Aplicado a Tres Programas de Investigación Independientes".
- Venue: *Synthese* o *Philosophy of Science*.
- Co-autores: el autor + 3 colaboradores externos.

**Fase 4 (meses 13-24): Toolkit como librería.**

- Empaquetar `scan.py`, `domains.yaml`, `criteria.py` en librería Python.
- Publicar en JOSS.

### 10.2 Conclusión

La Epistemología Generativa es un protocolo operativo para producir proposiciones falsables a escala. Sus cuatro componentes —estructura de tesis falsable, categorización epistémica, pre-registro con matriz de confusión, y ciclo generativo-formal— constituyen un sistema integrado.

La autoetnografía del corpus PUSFRE/RONIN ilustra la aplicabilidad del protocolo: 28 tesis operables, 17 dominios verificados (de 30 candidatos), 1 contraejemplo documentado, 2 tests de falso positivo, y una exploración cuantitativa preliminar.

**Lo que este paper ha establecido (Categoría A):**

1. La estructura de tesis falsable (E, O, F, P, R).
2. El sistema de categorización epistémica (A/B/C/D).
3. El protocolo de pre-registro con matriz de confusión.

**Lo que este paper ha establecido como hipótesis operativa (Categoría B):**

4. La aplicabilidad del protocolo a un programa de investigación independiente.
5. La densidad de proposiciones falsables generadas (28 tesis en dos meses).
6. La utilidad del ciclo generativo-formal.

**Lo que este paper no ha establecido (Categoría C):**

7. La validación externa del protocolo.
8. La superioridad del protocolo sobre protocolos existentes.
9. La replicabilidad en otros programas.

**El trabajo futuro es claro:**

1. **Completar el pre-registro interno.**
2. **Aplicar el protocolo a 3 casos externos.**
3. **Publicar el toolkit.**
4. **Someter el paper a revisión por pares.**

La tesis final es simple: la densidad de proposiciones falsables es una medida del progreso científico, y puede ser aumentada mediante protocolos explícitos.

---

## Agradecimientos

A quien lea esto y encuentre un error. A quien lo refute con datos. A quien lo ignore por las razones correctas.

---

## Referencias

Anderson, L. (2006). Analytic autoethnography. *Journal of Contemporary Ethnography*, 35(4), 373-395.

Bacon, F. (1620). *Novum Organum*.

Darden, L. (1991). *Theory Change in Science: Strategies from Mendelian Genetics*. Oxford University Press.

Duhem, P. (1906). *La théorie physique: son objet, sa structure*. Chevalier et Rivière.

Dunbar, K. (1995). How scientists really reason: Scientific reasoning in real-world laboratories. In R. J. Sternberg & J. E. Davidson (Eds.), *The Nature of Insight* (pp. 365-395). MIT Press.

Ellis, C. (2004). *The Ethnographic I: A Methodological Novel about Autoethnography*. AltaMira Press.

Ellis, C., Adams, T. E., & Bochner, A. P. (2011). Autoethnography: An overview. *Historical Social Research*, 36(4), 273-290.

Ferrández Canalis, D. (2026a). Motor Cascabel: 28 tesis operables en un generador de texto en español. *Agencia RONIN Preprints*.

Ferrández Canalis, D. (2026b). Autorrevisión del Corpus RONIN. *Agencia RONIN Preprints*.

Ferrández Canalis, D. (2026c). Tratado de Extensión del PUSFRE v4.0. *Agencia RONIN Preprints*.

Ferrández Canalis, D. (2026d). Manual de Campo del PUSFRE. *Agencia RONIN Preprints*.

Ferrández Canalis, D. (2026e). No-Identificabilidad de los Parámetros de la Ecuación de Hill en el Régimen Sub-Saturado. *Agencia RONIN Preprints*.

Ferrández Canalis, D. (2026f). No-Identificabilidad Estructural y Práctica en Modelos PBPK. *Agencia RONIN Preprints*.

Ferrández Canalis, D. (2026g). No-Identificabilidad Estructural en Modelos Epidemiológicos con Subreporte. *Agencia RONIN Preprints*.

Ferrández Canalis, D. (2026h). El bus de datos pertenece al amo: Crónicas del tecnocapitalismo. *Agencia RONIN*.

Gigerenzer, G. (1991). From tools to theories: A heuristic of discovery in cognitive psychology. *Psychological Review*, 98(2), 254-267.

Hanson, N. R. (1958). *Patterns of Discovery*. Cambridge University Press.

Hoyningen-Huene, P. (2006). Context of discovery versus context of justification and Thomas Kuhn. In J. Schickore & F. Steinle (Eds.), *Revisiting Discovery and Justification* (pp. 119-131). Springer.

Klahr, D., & Simon, H. A. (1999). Studies of scientific discovery. *Psychological Bulletin*, 125(5), 524-543.

Lakatos, I. (1970). Falsification and the methodology of scientific research programmes. In I. Lakatos & A. Musgrave (Eds.), *Criticism and the Growth of Knowledge* (pp. 91-196). Cambridge University Press.

Langley, P., Simon, H. A., Bradshaw, G. L., & Zytkow, J. M. (1987). *Scientific Discovery: Computational Explorations of the Creative Processes*. MIT Press.

Magnani, L. (2001). *Abduction, Reason, and Science*. Kluwer Academic.

Mayo, D. G. (1996). *Error and the Growth of Experimental Knowledge*. University of Chicago Press.

Mayo, D. G. (2018). *Statistical Inference as Severe Testing*. Cambridge University Press.

Mill, J. S. (1843). *A System of Logic*.

Newell, A., & Simon, H. A. (1972). *Human Problem Solving*. Prentice-Hall.

Nickles, T. (Ed.). (1980). *Scientific Discovery: Case Studies*. D. Reidel.

Nosek, B. A., Ebersole, C. R., DeHaven, A. C., & Mellor, D. T. (2018). The preregistration revolution. *Proceedings of the National Academy of Sciences*, 115(11), 2600-2606.

Peirce, C. S. (1903). *Harvard Lectures on Pragmatism*.

Popper, K. R. (1959). *The Logic of Scientific Discovery*. Hutchinson.

Quine, W. V. O. (1951). Two dogmas of empiricism. *The Philosophical Review*, 60(1), 20-43.

Reichenbach, H. (1938). *Experience and Prediction*. University of Chicago Press.

Simon, H. A. (1973). Does scientific discovery have a logic? *Philosophy of Science*, 40(4), 471-480.

---

## Apéndice A: Las 28 tesis del Motor Cascabel

| # | Flag | Tesis | Bloque |
|---|------|-------|--------|
| 1 | `--publicar` | Vida media de n-grama decrece con corpus | A |
| 2 | `--canon-expandir` | Canon se define por lo rechazado | A |
| 3 | `--auditar` | H(capa\|eje) invariante del generador | B |
| 4 | `--ablation` | Validadores no aditivos | B |
| 5 | `--matriz` | Co-ocurrencia de rango bajo | B |
| 6 | `--deriva` | Deriva = cambio de régimen | B |
| 7 | `--firma` | Firma 8D estable bajo paráfrasis | B |
| 8 | `--espejo` | Antítesis = operador involutivo | C |
| 9 | `--contraejemplo` | Violación tiene gramática | C |
| 10 | `--ciego` | Sesgo = divergencia ciega/validada | C |
| 11 | `--forense` | Autoría por n-gramas funcionales | C |
| 12 | `--interpolar` | Interpolación no conmutativa | D |
| 13 | `--reconstruir` | Reconstrucción única bajo estilo | D |
| 14 | `--temporal` | Datación por marcas léxicas | D |
| 15 | `--frontera` | Borde del espacio declarado | E |
| 16 | `--consenso` | Acuerdo = causa estructural | F |
| 17 | `--disenso` | Disenso = límite móvil | F |
| 18 | `--cuarentena` | Rechazos = modos de fallo | F |
| 19 | `--mutar` | Mutación lineal en distancia | G |
| 20 | `--cruzar` | Cruce = media armónica | G |
| 21 | `--degradar` | Jerarquía de capas | G |
| 22 | `--autopsia` | Distancia plano-texto = salud | H |
| 23 | `--espejo-negro` | Complemento informativo | H |
| 24 | `--parásito` | Permisividad = hospedaje | H |
| 25 | `--comprimir` | K(x) ∝ K(π(x)) | I |
| 26 | `--expandir` | Expansión converge a firma | I |
| 27 | `--censurar` | Censura estructural ≠ léxica | J |
| 28 | `--confesar` | Autoconsistencia reflexiva | J |

**Predicciones del autor:** 15 sobreviven, 8 caen, 5 indeterminadas.

---

## Apéndice B: Los 30 dominios del pre-registro

Ver §5.3.

---

## Apéndice C: Matriz de confusión parcial

|  | Resultó PASS | Resultó FAIL | LOAD_FAILED |
|--|--------------|--------------|-------------|
| Predicho PASS | 12 | 0 | 0 |
| Predicho FAIL | 0 | 5 | 0 |

**Precisión:** 100%. **Recall:** 100%. **F1:** 100%.

---

## Apéndice D: Los 5 dominios excluidos

| Dominio | Razón de exclusión | Modelo alternativo |
|---------|-------------------|-------------------|
| Fama-French | Aditivo, Ω < 1 orden | pusfre (lineal) |
| Renta fija | Estructura temporal | Nelson-Siegel |
| Series con tendencia | Dependencia Φ-Ψ-Ω | ARIMA / dif |
| Interacción directa | Competencia pairwise | Teoría de juegos |
| Ω < 1.5 órdenes | Degeneración K-α activa | pusfre o ces |

---

## Apéndice E: Los dos tests de falso positivo

| Test | ΔBIC | Resultado |
|------|------|-----------|
| Falso positivo memoria (M6 vs M7) | −681.85 | ✅ M6 gana |
| Falso positivo saturación (M0 vs M6) | −6411.34 | ✅ M0 gana |

---

## Apéndice F: Roadmap de validación

| Fase | Duración | Acción |
|------|----------|--------|
| 1 | Meses 1-2 | Completar pre-registro interno (13 dominios) |
| 2 | Meses 3-6 | Aplicar protocolo a 3 casos externos |
| 3 | Meses 7-12 | Publicar paper conjunto con co-autoría |
| 4 | Meses 13-24 | Publicar toolkit en JOSS |

---

**Fin del paper.**

**1310.**

---

*"El protocolo no garantiza la verdad. Garantiza la densidad de proposiciones verificables. Y la densidad es lo que distingue un programa de investigación de una colección de opiniones."*
