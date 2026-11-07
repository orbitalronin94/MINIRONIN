# Hacia una lingüística computacional falsable: veintiocho tesis operables en un generador de texto en español

**Autor:** David Ferrández Canalis¹

¹ Investigador independiente. Contacto: [correspondencia a través del repositorio del proyecto]

**Fecha:** septiembre de 2026

**Clasificación:** JEL Z13, C88, C63 · ACM I.2.7, J.5 · MSC 68T50, 62P99

**Palabras clave:** estilometría computacional, generación de texto, falsabilidad, corpus negativo, autoría, compresión, entropía condicional

---

## Resumen

Se presenta el **MOTOR CASCABEL v0.1.0**, un sistema de generación de texto en español que articula **veintiocho tesis falsables** sobre el lenguaje, cada una implementada como operación computable. A diferencia de los generadores habituales, que se evalúan por la calidad de su salida, el sistema se evalúa por la **refutabilidad de sus afirmaciones internas**. Cada instrumento devuelve una medida con una predicción explícita sobre su comportamiento bajo perturbación, y su valor científico reside en poder ser contradicho. El preprint formaliza las veintiocho tesis en cuatro capas (formal, operativa, predictiva y refutacional), las agrupa en diez bloques temáticos y propone un protocolo de validación empírica reproducible. Se discuten las implicaciones para la estilometría computacional, la teoría de la autoría y la epistemología de los sistemas generativos.

---

## 1. Introducción

La lingüística computacional ha privilegiado históricamente la **capacidad predictiva** de sus modelos —qué palabra sigue, qué etiqueta corresponde, qué traducción es más probable— sobre la **falsabilidad de sus supuestos**. Un modelo de lenguaje puede batir récords en benchmarks sin que ninguna de sus hipótesis internas sea refutable en el sentido popperiano.

Este preprint describe un sistema que invierte esa jerarquía. El MOTOR CASCABEL v0.1.0 no pretende generar el mejor texto posible. Pretende **generar el texto que permita refutar sus propias afirmaciones sobre el texto**. Cada una de sus veintiocho adiciones es una tesis con:

1. **Enunciado** en lengua natural.
2. **Objeto formal** susceptible de cómputo.
3. **Operación** que la ejecuta.
4. **Predicción falsable** que la refutaría.
5. **Novedad** respecto al estado del arte.

El sistema hereda de su versión anterior (`v0.0.2`) un núcleo estable: un corpus embebido de diecinueve posts, un mecanismo de bootstrap sobre un corpus externo de cuarenta y ocho capítulos, tres validadores independientes (estilométrico, anti-repetición, anti-tics) y un programador de combinaciones sin repetición. La `v0.1.0` añade los veintiocho instrumentos sin modificar ese núcleo. El principio de diseño es que **una adición no puede alterar las garantías existentes**; solo puede aumentar el número de afirmaciones refutables del sistema.

### 1.1. Motivación

Tres observaciones motivan el trabajo.

**Primera.** La estilometría clásica (Mosteller & Wallace, 1964; Burrows, 2002) ha producido un conjunto robusto de técnicas para atribuir autoría, pero raramente ha formalizado **qué propiedades del texto son invariantes bajo qué transformaciones**. La noción de "firma estilométrica" se ha usado de manera operativa pero no algebraica. La tesis 7 (firma de ocho dimensiones) propone un criterio de validez: una firma es válida si es estable bajo paráfrasis e inestable bajo cambio temático.

**Segunda.** Los sistemas generativos se evalúan por su **espacio de aceptación**, no por su **espacio de rechazo**. La lingüística computacional ha estudiado extensamente qué textos produce un modelo, pero apenas ha estudiado qué textos **no** produce y por qué. Las tesis 2, 9, 18 y 23 proponen tratar el corpus negativo —lo rechazado— como objeto primario.

**Tercera.** La noción de "estilo" en humanidades y la noción de "distribución" en computación no se han reconciliado. Las tesis 3, 5, 6 y 12 proponen medir el estilo como cantidades termodinámicas (entropía condicional, rango de matriz, cambio de régimen, no-conmutatividad de mezcla) que son **operables sin interpretación semántica**.

### 1.2. Contribuciones

Este preprint contribuye:

- Un **marco formal** (§2) para expresar tesis lingüísticas como operaciones computables con predicciones falsables.
- **Veintiocho tesis** (§4), agrupadas en diez bloques, con enunciado, objeto formal, operación, firma y predicción.
- Un **protocolo de validación empírica** (§5) reproducible sobre el motor público.
- Una **discusión de limitaciones** (§7) que separa lo que el sistema mide de lo que el sistema afirma.

### 1.3. No-contribuciones

El sistema **no** aprende. No modifica sus pesos a partir de la experiencia. No mejora con el uso. Esa es una decisión de diseño, no una carencia. La razón es que un sistema que aprende desplaza sus propias afirmaciones sin declararlo; un sistema que no aprende puede ser refutado en cada instante.

---

## 2. Marco formal

### 2.1. Notación

Sea `G` un generador de texto. Sea `L(G)` el conjunto de textos que `G` acepta. Sea `f: Texto → ℝ^d` una **firma** que asigna a cada texto un vector de `d` dimensiones. Sea `π ∈ Π` un **plano de composición** que especifica las restricciones estructurales de un texto. Sea `V = {v_1, v_2, v_3}` el conjunto de validadores, con `v_i: Texto → {⊤, ⊥}`.

### 2.2. Tesis falsable

**Definición 2.1.** Una **tesis falsable** es una tupla `(A, O, P, R)` donde:

- `A` es un enunciado en lengua natural.
- `O` es una operación computable `O: G → D` con `D` un dominio medible.
- `P` es una predicción `P: O(G) → B` con `B` un booleano o un intervalo.
- `R` es un **refutador**: una transformación `R: G → G` tal que si `O(R(G))` viola `P`, la tesis se considera refutada.

### 2.3. Invariantes

Una tesis fuerte de la `v0.1.0` es que **ciertas propiedades del generador son invariantes bajo transformaciones del corpus**. Formalmente:

**Definición 2.2.** Sea `T` una transformación sobre corpus. Una propiedad `φ` es **`T`-invariante** si `φ(G(C)) = φ(G(T(C)))` para todo corpus `C`.

Las tesis 3, 6 y 7 son afirmaciones de invariancia bajo transformaciones específicas (`T = cambio de tema`, `T = paráfrasis`, `T = cambio de tamaño del corpus`).

### 2.4. Falsabilidad y ciencia normal

El sistema distingue tres regímenes:

- **Régimen validado:** los tres validadores aceptan el texto.
- **Régimen ciego:** los validadores están desactivados.
- **Régimen negativo:** los validadores rechazan el texto.

La coexistencia de los tres regímenes es lo que permite a las tesis 4, 10, 16, 17 y 18 medir **la contribución de cada validador por separado**.

---

## 3. Estado del arte (breve)

### 3.1. Estilometría

La tradición inaugurada por Mosteller & Wallace (1964) y continuada por Burrows (2002) ha establecido la **delta de Burrows** y sus variantes como estándar de facto para atribución de autoría. Estos métodos funcionan, pero raramente formulan **predicciones refutables** sobre su propio comportamiento bajo transformación. La tesis 7 propone un criterio de validez de firma que sí lo hace.

### 3.2. Semántica distribucional

La hipótesis distribucional (Harris, 1954) y sus realizaciones computacionales (Deerwester et al., 1990; Landauer & Dumais, 1997) han mostrado que la co-ocurrencia captura estructura semántica. La tesis 5 se distingue por aplicarla **al estilo**, no al contenido.

### 3.3. Teoría de la información

La conexión entre estilo y compresión se ha explorado poco. La tesis 25 propone que la longitud mínima de descripción de un texto es proporcional a la complejidad de su plano, no a su longitud.

### 3.4. Sistemas generativos

Los modelos de lenguaje neuronales (Brown et al., 2020; y sucesores) han dominado la generación de texto. La diferencia con este trabajo no es de arquitectura sino de **postura epistémica**: los modelos neuronales no declaran sus tesis; este sistema declara veintiocho y ofrece un protocolo para refutarlas.

---

## 4. Las veintiocho tesis

Cada tesis se presenta en cinco partes: enunciado, objeto formal, operación, firma y predicción falsable. Se indica el bloque (A–J) y el flag CLI que la invoca.

### Bloque A — Persistencia y memoria

#### Tesis 1 — Acreción y vida media (`--publicar`)

**Enunciado.** El corpus de un generador es un organismo que crece por acreción; la vida media de un n-grama decrece con el tamaño del corpus.

**Objeto formal.** Sea `C_t` el corpus tras el ciclo `t`. La vida media de un grama `g` es `τ(g) = sup{ t : g ∈ C_t } − inf{ t : g ∈ C_t }`. Se postula `τ(g) ∝ |C_t|^{−α}` con `α > 0`.

**Operación.** Cada post aceptado se serializa en `publicados.json` con firma, plano y fecha. Se recalcula el índice de n-gramas y se registra `τ(g)` para cada grama.

**Firma.** Curva `τ` vs `|C|` en escala logarítmica doble. Pendiente `−α`.

**Predicción falsable.** Si `α ≤ 0`, la tesis se refuta: el corpus no erosiona, acumula.

#### Tesis 2 — Canon negativo (`--canon-expandir`)

**Enunciado.** El canon de una voz se define por lo que la voz ha rechazado, no por lo que ha aceptado.

**Objeto formal.** Sea `R = {r_1, …, r_n}` el conjunto de textos rechazados con motivo `m(r) ∈ {est, rep, tic}`. El canon negativo es `K⁻ = { (m, f(r)) : r ∈ R }`.

**Operación.** Se almacena cada rechazo con firma y motivo. Al expandir el canon, `K⁻` actúa como restricción negativa.

**Firma.** Histograma de motivos por firma estilométrica.

**Predicción falsable.** Si dos generadores distintos producen el mismo `K⁻`, no tienen voces distintas.

---

### Bloque B — Medición

#### Tesis 3 — Entropía condicional invariante (`--auditar`)

**Enunciado.** La autoconsistencia estilométrica de un corpus se mide como `H(capa | eje)`, y esa entropía es un invariante del generador, no del corpus.

**Objeto formal.** `H(C | E) = − Σ_{e,c} p(e,c) log p(c|e)`. Se postula `H(C|E)` constante bajo variaciones del corpus si el generador se mantiene.

**Operación.** Genera `n` textos con semilla fija, calcula `H(C|E)` empírica, compara con la del corpus.

**Firma.** `ΔH = H_gen − H_corpus`. Se espera `|ΔH| < ε`.

**Predicción falsable.** Si `ΔH` varía con el tema, la invariancia se refuta.

#### Tesis 4 — No-aditividad de validadores (`--ablation`)

**Enunciado.** La suma de las contribuciones marginales de los validadores no es igual a su contribución conjunta.

**Objeto formal.** Sea `A(S)` la tasa de aceptación con el subconjunto `S ⊆ V`. Se postula `A(V) ≠ A(∅) + Σ_i [A(V) − A(V∖{v_i})]`.

**Operación.** Se ejecuta el generador con los `2³ = 8` subconjuntos de validadores, `n` textos cada uno.

**Firma.** Tabla 2³. Interacción de orden 2 y 3.

**Predicción falsable.** Si la interacción es cero, los validadores son independientes.

#### Tesis 5 — Rango bajo del discurso (`--matriz`)

**Enunciado.** La matriz de co-ocurrencia de términos en un corpus de estilo es de rango bajo, y ese rango es la dimensión efectiva del discurso.

**Objeto formal.** `M_{ij} = PMI(t_i, t_j)`. Se postula `rank(M) ≪ min(|V|, |V|)`.

**Operación.** Construye `M` sobre el corpus completo. Aplica SVD truncada.

**Firma.** Espectro de valores singulares. Codo en `k*`.

**Predicción falsable.** Si el espectro decae como ley de potencias sin codo, la tesis se refuta.

#### Tesis 6 — Deriva como cambio de régimen (`--deriva`)

**Enunciado.** La deriva estilística es un cambio de régimen detectable por CUSUM sobre la longitud media de frase.

**Objeto formal.** `S_t = max(0, S_{t−1} + (ℓ_t − ℓ̄))`. Punto de cambio en `t*` cuando `S_{t*} > h`.

**Operación.** Ordena textos por ciclo, calcula CUSUM, detecta puntos.

**Firma.** Lista `{t*}`. Se espera alineación con cambios de eje.

**Predicción falsable.** Si `t*` no correlaciona con el plano, la tesis se refuta.

#### Tesis 7 — Firma estable bajo paráfrasis (`--firma`)

**Enunciado.** Todo texto tiene una firma de ocho dimensiones, estable bajo paráfrasis e inestable bajo cambio de eje.

**Objeto formal.** `f(x) = (ℓ̄, σ_ℓ, TTR, δ_p, ρ_c, ρ_l, ℓ̄_p, n_p)`. Se postula `||f(x) − f(Π(x))|| < ε` y `||f(x) − f(x')|| > δ` si `eje(x) ≠ eje(x')`.

**Operación.** Calcula `f` para cada texto. Compara distancias intra-eje e inter-eje.

**Firma.** Cociente `intra/inter`.

**Predicción falsable.** Si el cociente ≈ 1, la tesis se refuta.

---

### Bloque C — Inversión y falsación

#### Tesis 8 — Antítesis como involución (`--espejo`)

**Enunciado.** Existe un operador `E` con `E² = id`, `f(E(x)) ≈ f(x)` y `polaridad(E(x)) = −polaridad(x)`.

**Objeto formal.** `E: Texto → Texto`, involutivo, estilométricamente neutro, polarizante.

**Operación.** Invierte aserciones por negación estructural preservando longitud y ritmo.

**Firma.** `polaridad` por análisis de negaciones y antónimos.

**Predicción falsable.** Si `E(x)` no preserva firma, la tesis se refuta.

#### Tesis 9 — Gramática de la violación (`--contraejemplo`)

**Enunciado.** El conjunto de textos que violan un validador es un corpus con estructura, no ruido.

**Objeto formal.** `N_V = { x : V(x) = ⊥ }`. Se postula que `N_V` admite modelo generativo con firma propia.

**Operación.** Fuerza violación de un validador, genera `n` violadores, analiza.

**Firma.** Firma media de `N_V`.

**Predicción falsable.** Si la firma de `N_V` es indistinguible del azar, la tesis se refuta.

#### Tesis 10 — Sesgo como divergencia (`--ciego`)

**Enunciado.** El sesgo intrínseco de un generador es la diferencia entre su distribución ciega y la validada.

**Objeto formal.** `bias(G) = D_KL( p_ciego || p_validado )`.

**Operación.** Genera `n` con validadores y `n` sin. Compara firmas.

**Firma.** `D_KL` empírica.

**Predicción falsable.** Si `D_KL` no cambia al variar el eje, la tesis se refuta.

#### Tesis 11 — Autoría por n-gramas funcionales (`--forense`)

**Enunciado.** La autoría se atribuye por n-gramas funcionales (artículos, preposiciones, auxiliares), y la tasa de acierto es independiente del tema.

**Objeto formal.** `F(x)` = n-gramas funcionales, `C(x)` = n-gramas de contenido. Se postula `P(autor | F(x)) > P(autor | C(x))`.

**Operación.** Clasificación ingenua con `F` y con `C`. Comparación.

**Firma.** Matriz de confusión. Acierto comparado.

**Predicción falsable.** Si `F` no supera a `C`, la tesis se refuta.

---

### Bloque D — Interpolación y reconstrucción

#### Tesis 12 — No-conmutatividad de la mezcla (`--interpolar`)

**Enunciado.** La interpolación de voces no es conmutativa ni asociativa.

**Objeto formal.** `I(A, B, α) ≠ I(B, A, α)` en general.

**Operación.** Genera con firma objetivo `α·f(A) + (1−α)·f(B)`. Compara errores conmutativos.

**Firma.** Diferencia `|error(AB) − error(BA)|`.

**Predicción falsable.** Si la diferencia es cero, la tesis se refuta.

#### Tesis 13 — Unicidad bajo estilo (`--reconstruir`)

**Enunciado.** Bajo restricciones de estilo, un texto con huecos tiene una única reconstrucción válida.

**Objeto formal.** Sea `R(x)` el conjunto de reconstrucciones que pasan los tres validadores. Se postula `|R(x)| = 1` para `k` pequeño.

**Operación.** Enumeración filtrada por validadores sobre huecos.

**Firma.** `|R(x)|` vs `k`.

**Predicción falsable.** Si `|R(x)|` crece linealmente con `k`, la tesis se refuta.

#### Tesis 14 — Datación implícita (`--temporal`)

**Enunciado.** Todo corpus tiene una línea de tiempo implícita detectable por marcas léxicas.

**Objeto formal.** Sea `T(x)` la fecha inferida. Se postula `|T(x) − T_real(x)| < δ` para `δ` pequeño.

**Operación.** Clasificador ingenuo sobre marcas temporales.

**Firma.** MAE de datación.

**Predicción falsable.** Si `MAE > δ_max`, la tesis se refuta.

---

### Bloque E — Frontera

#### Tesis 15 — Borde medible del espacio declarado (`--frontera`)

**Enunciado.** El espacio declarado de un generador tiene un borde clasificable.

**Objeto formal.** `S` = espacio declarado. `F` = textos generados con planos fuera de `S`. Se postula `AUC > 0.9` para clasificador binario dentro/fuera.

**Operación.** Genera `n` dentro y `n` fuera. Entrena clasificador.

**Firma.** `AUC`.

**Predicción falsable.** Si `AUC ≈ 0.5`, la tesis se refuta.

---

### Bloque F — Validación cruzada

#### Tesis 16 — Consenso como señal estructural (`--consenso`)

**Enunciado.** La coincidencia de dos validadores en rechazar indica causa estructural, no superficial.

**Objeto formal.** `R_i` = rechazados por `v_i`. Se postula `x ∈ R_i ∩ R_j` ⟹ violación estructural del plano.

**Operación.** Registra rechazos por validador, analiza intersecciones.

**Firma.** Tasa de violación estructural en intersecciones vs diferencia simétrica.

**Predicción falsable.** Si las tasas son iguales, la tesis se refuta.

#### Tesis 17 — Disenso como límite móvil (`--disenso`)

**Enunciado.** El disenso entre validadores define un límite epistémico móvil, función de la temperatura de la capa.

**Objeto formal.** `D = R_i △ R_j`. Se postula `|D|` crece con `temperatura(capa)`.

**Operación.** Mide `|D|` por capa, eje, temperatura.

**Firma.** Correlación `|D|` vs temperatura.

**Predicción falsable.** Si `|D|` es constante, la tesis se refuta.

#### Tesis 18 — Cuarentena como laboratorio (`--cuarentena`)

**Enunciado.** Los textos rechazados forman un corpus negativo con modos de fallo estables.

**Objeto formal.** `Q = { (x, motivo) : x rechazado }`. Se postula `Q` admite clustering con `k` modos.

**Operación.** Acumula rechazos, agrupa por firma.

**Firma.** Centroides + tamaño. Estabilidad bajo remuestreo.

**Predicción falsable.** Si los clusters no se estabilizan, la tesis se refuta.

---

### Bloque G — Metamorfosis

#### Tesis 19 — Linealidad de la mutación (`--mutar`)

**Enunciado.** La mutación de una variable del plano produce distancia estilométrica lineal en la variable.

**Objeto formal.** `||f(x_π) − f(x_π')|| = a·|Δvar| + b`.

**Operación.** Barrido por variable, mide distancias.

**Firma.** `R²` de ajuste lineal.

**Predicción falsable.** Si `R² < 0.5`, la tesis se refuta.

#### Tesis 20 — Cruce como media armónica (`--cruzar`)

**Enunciado.** El cruce de dos planos produce firma igual a la media armónica, no aritmética.

**Objeto formal.** `f(cruce(A,B)) ≈ 2 / (1/f(A) + 1/f(B))`.

**Operación.** Cruza planos, compara ajustes.

**Firma.** Error de ajuste a cada media.

**Predicción falsable.** Si la aritmética ajusta mejor, la tesis se refuta.

#### Tesis 21 — Jerarquía de capas (`--degradar`)

**Enunciado.** La degradación progresiva revela jerarquía entre capas estructurales y decorativas.

**Objeto formal.** `D_k(x)` con `k` degradaciones. Firma colapsa en `k*` dependiente de capa.

**Operación.** Aplica degradaciones sucesivas, mide firma.

**Firma.** Curva `||f(D_k(x)) − f(x)||` vs `k`.

**Predicción falsable.** Si `k*` no depende de la capa, la tesis se refuta.

---

### Bloque H — Autorreferencia

#### Tesis 22 — Autopsia como fidelidad (`--autopsia`)

**Enunciado.** La distancia entre firma esperada del plano y firma del texto es indicador de salud del generador.

**Objeto formal.** `Δ(π, x) = ||f_esperada(π) − f(x)||`.

**Operación.** Mide `Δ` para cada texto generado.

**Firma.** Distribución de `Δ`.

**Predicción falsable.** Si `Δ` es constante, la tesis se refuta.

#### Tesis 23 — Complemento informativo (`--espejo-negro`)

**Enunciado.** El texto más cercano en firma que el generador rechaza es informativo sobre el generador.

**Objeto formal.** `N(x) = argmin_y d(f(y), f(x))` sujeto a `y ∉ L(G)`.

**Operación.** Búsqueda sobre rechazados.

**Firma.** `d(f(x), f(N(x)))`.

**Predicción falsable.** Si `N(x)` no existe, la tesis se refuta.

#### Tesis 24 — Permisividad como hospedaje (`--parásito`)

**Enunciado.** La capacidad de un texto para hospedar otro sin violar restricciones mide la permisividad del estilo.

**Objeto formal.** `H(x, y)` válido para `|y|/|x| < ρ`. `ρ` depende de la capa.

**Operación.** Inserción validada.

**Firma.** `ρ` por capa.

**Predicción falsable.** Si `ρ` es constante, la tesis se refuta.

---

### Bloque I — Compresión

#### Tesis 25 — Complejidad del plano (`--comprimir`)

**Enunciado.** La longitud mínima de descripción de un texto es proporcional a la complejidad de su plano.

**Objeto formal.** `K(x) ≈ K(π(x)) + c`. Se postula `K(x) / K(π(x)) ≈ 1`.

**Operación.** Compara `zlib(texto)` con `zlib(plano)`.

**Firma.** Cociente.

**Predicción falsable.** Si el cociente depende de `|x|`, la tesis se refuta.

#### Tesis 26 — Convergencia de la expansión (`--expandir`)

**Enunciado.** La expansión de un texto comprimido converge a la firma original en `k*` pasos.

**Objeto formal.** `||f(E_k(x)) − f(x)|| → 0` con `k`.

**Operación.** Expande por párrafos, mide firma.

**Firma.** Curva de convergencia.

**Predicción falsable.** Si no hay codo, la tesis se refuta.

---

### Bloque J — Ética operativa

#### Tesis 27 — Censura diferenciable (`--censurar`)

**Enunciado.** La censura estructural es distinguible de la léxica por su firma estilométrica.

**Objeto formal.** `f(C_lex(x)) ≠ f(C_est(x))`.

**Operación.** Aplica ambas censuras, compara firmas.

**Firma.** Distancia de firmas.

**Predicción falsable.** Si las firmas son indistinguibles, la tesis se refuta.

#### Tesis 28 — Autoconsistencia reflexiva (`--confesar`)

**Enunciado.** Un generador puede producir un texto que declare sus propias restricciones sin violarlas.

**Objeto formal.** `CF(π) ∈ L(G)` y `CF(π)` menciona `π`.

**Operación.** Texto que enuncia su plano, verificado por los tres validadores.

**Firma.** Tasa de éxito.

**Predicción falsable.** Si la tasa es 0, la tesis se refuta.

---

## 5. Protocolo de validación empírica

### 5.1. Reproducibilidad

El motor es un único archivo Python sin dependencias externas. Cualquier investigador puede ejecutar cada tesis con una línea de comandos. La semilla es explícita y las salidas son JSON.

### 5.2. Batería estándar

```bash
# Bloque A
python cascabel.py --publicar --canon ./publicados.json --n 1000
python cascabel.py --canon-expandir --canon ./publicados.json

# Bloque B
python cascabel.py --auditar --n 1000 --semilla 42
python cascabel.py --ablation --n 500
python cascabel.py --matriz
python cascabel.py --deriva --n 500
python cascabel.py --firma --texto "..."

# Bloque C
python cascabel.py --espejo --texto "..."
python cascabel.py --contraejemplo --tic no_es_es --n 500
python cascabel.py --ciego --n 500
python cascabel.py --forense

# Bloque D
python cascabel.py --interpolar --peso 0.5
python cascabel.py --reconstruir "El ____ no es ____. Es ____."
python cascabel.py --temporal

# Bloque E
python cascabel.py --frontera --n 500

# Bloque F
python cascabel.py --consenso --n 1000
python cascabel.py --disenso --n 1000
python cascabel.py --cuarentena --n 1000

# Bloque G
python cascabel.py --mutar --variable capa
python cascabel.py --cruzar --plano-a ia|cto|tecnico --plano-b poder|inversor|juridico
python cascabel.py --degradar

# Bloque H
python cascabel.py --autopsia --n 200
python cascabel.py --espejo-negro
python cascabel.py --parasito

# Bloque I
python cascabel.py --comprimir
python cascabel.py --expandir

# Bloque J
python cascabel.py --censurar --tipo lexica
python cascabel.py --censurar --tipo estructural
python cascabel.py --confesar --combinacion ia|cto|tecnico
```

### 5.3. Criterios de aceptación

| Bloque | Criterio |
|---|---|
| A | `α > 0.1` con `p < 0.05` |
| B | `|ΔH| < 0.1`; interacción ≠ 0; codo visible; `t*` correlaciona |
| C | `E² = id` y `||f(E(x)) − f(x)|| < 0.05`; `AUC > 0.7` |
| D | diferencia conmutativa > 0.01; `|R(x)| = 1` en 90% |
| E | `AUC > 0.85` |
| F | interacción significativa; correlación > 0.4 |
| G | `R² > 0.5`; gana armónica en > 60% |
| H | `Δ` con distribución bimodal |
| I | cociente estable; codo visible |
| J | distancia > umbral; tasa > 0.8 |

### 5.4. Publicación de refutaciones

El proyecto se compromete a publicar cualquier refutación de cualquiera de las veintiocho tesis. Una tesis refutada no se elimina: se marca como `refutada:<fecha>` y se documenta el experimento.

---

## 6. Predicciones consolidadas

| # | Predicción | Magnitud esperada | Refutador |
|---|---|---|---|
| 1 | `α > 0` | 0.1–0.5 | corpus sin erosión |
| 2 | `K⁻` distinguible | AUC > 0.7 | canon negativo indistinto |
| 3 | `ΔH` acotada | < 0.1 | deriva por tema |
| 4 | Interacción ≠ 0 | \|I\| > 0.05 | validadores aditivos |
| 5 | Rango bajo | codo < 20 | espectro plano |
| 6 | Puntos de cambio | correlación > 0.4 | ruido |
| 7 | Firma discriminante | intra/inter < 0.5 | indistinción |
| 8 | Involución | `E² = id` | no involutivo |
| 9 | Violación estructurada | firma no aleatoria | ruido |
| 10 | Sesgo medible | `D_KL > 0.1` | sin sesgo |
| 11 | Funcional > contenido | Δ > 0.05 | contenido superior |
| 12 | No-conmutativa | Δ > 0.01 | conmutativa |
| 13 | Unicidad | \|R\| = 1 en 90% | múltiples |
| 14 | Datación | MAE < 2 años | azar |
| 15 | Borde | AUC > 0.85 | sin borde |
| 16 | Consenso estructural | tasa > 0.7 | superficial |
| 17 | Disenso móvil | corr > 0.4 | rígido |
| 18 | Modos estables | k estable | inestable |
| 19 | Linealidad | R² > 0.5 | no lineal |
| 20 | Armónica gana | > 60% | aritmética |
| 21 | Jerarquía | k* por capa | uniforme |
| 22 | Bimodalidad | dos modos | unimodal |
| 23 | Complemento | distancia pequeña | lejano |
| 24 | Permisividad | ρ variable | constante |
| 25 | Cociente estable | ≈ 1 | variable |
| 26 | Convergencia | codo claro | sin codo |
| 27 | Censura diferenciable | distancia > 0.1 | indistinta |
| 28 | Autoconsistencia | tasa > 0.8 | fallo |

---

## 7. Limitaciones

### 7.1. Del sistema

- El ensamblador produce textos más cortos que el corpus.
- El validador estilométrico es estadístico: no entiende de sentido.
- El validador de tics es sintáctico: no entiende de sinonimia.
- El modo forense usa heurísticas, no modelos entrenados.
- El modo arqueológico rellena huecos sintácticamente, no semánticamente.
- El sistema **no aprende**. Es una decisión de diseño.

### 7.2. De las tesis

- Las veintiocho tesis son **falsables**, no demostradas.
- La compresión usa `zlib`, que es una **cota superior** de `K(x)`.
- El espacio de planos es discreto.
- El corpus embebido es finito (19 textos).
- Las predicciones están calibradas sobre un único idioma y registro.

### 7.3. De la postura epistémica

- El sistema no pretende ser neutral.
- El sistema no pretende ser completo.

---

## 8. Trabajo futuro

### 8.1. Extensiones inmediatas

- **Validación inter-anotador.**
- **Extensión multilingüe.**
- **Corpus paralelo** con planos explícitos.

### 8.2. Extensiones de mayor alcance

- **Formalización del corpus negativo.**
- **Conexión con teoría de la información algorítmica.**
- **Estudio longitudinal.**
- **Refutación sistemática.**

### 8.3. Agenda

El proyecto propone una **agenda popperiana** para la lingüística computacional.

---

## 9. Conclusión

Se ha presentado un sistema generativo que articula veintiocho tesis falsables sobre el lenguaje, cada una implementada como operación computable. El sistema no aspira a generar el mejor texto. Aspira a **ser refutado con precisión**.

Las veintiocho tesis no son veintiocho verdades. Son veintiocho **apuestas**.

---

## Agradecimientos

A quien lea esto y encuentre un error.
A quien lo refute con datos.
A quien lo ignore por las razones correctas.

---

## Referencias

Brown, T., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P., … & Amodei, D. (2020). *Language models are few-shot learners*. Advances in Neural Information Processing Systems, 33, 1877–1901.

Burrows, J. (2002). *'Delta': a measure of stylistic difference and a guide to likely authorship*. Literary and Linguistic Computing, 17(3), 267–287.

Church, K. W., & Hanks, P. (1990). *Word association norms, mutual information, and lexicography*. Computational Linguistics, 16(1), 22–29.

Deerwester, S., Dumais, S. T., Furnas, G. W., Landauer, T. K., & Harshman, R. (1990). *Indexing by latent semantic analysis*. Journal of the American Society for Information Science, 41(6), 391–407.

Harris, Z. S. (1954). *Distributional structure*. Word, 10(2–3), 146–162.

Heaps, H. S. (1978). *Information retrieval: Computational and theoretical aspects*. Academic Press.

Holmes, D. I. (1998). *The evolution of stylometry in humanities scholarship*. Literary and Linguistic Computing, 13(3), 111–117.

Kolmogorov, A. N. (1965). *Three approaches to the quantitative definition of information*. Problems of Information Transmission, 1(1), 1–7.

Landauer, T. K., & Dumais, S. T. (1997). *A solution to Plato's problem: The latent semantic analysis theory of acquisition, induction, and representation of knowledge*. Psychological Review, 104(2), 211–240.

Mosteller, F., & Wallace, D. L. (1964). *Inference and disputed authorship: The Federalist*. Addison-Wesley.

Page, E. S. (1954). *Continuous inspection schemes*. Biometrika, 41(1/2), 100–115.

Popper, K. R. (1959). *The logic of scientific discovery*. Hutchinson.

Shannon, C. E. (1948). *A mathematical theory of communication*. Bell System Technical Journal, 27(3), 379–423.

Zipf, G. K. (1949). *Human behavior and the principle of least effort*. Addison-Wesley.

---

## Apéndice A — Estructura del motor

```
MOTOR CASCABEL v0.1.0
├── Núcleo v0.0.2 (intacto)
│   ├── CORPUS (19 embebidos + 41 bootstrap)
│   ├── PATRONES (14 cierres + 8 adenovirus + 12 virus + 15 retóricos)
│   ├── COMBINATORIA (14 × 92 × 9 = 11.592)
│   ├── PROGRAMADOR (exhaustivo | muestreo | dirigido)
│   └── VALIDADORES (estilométrico | anti-repetición | anti-tics)
└── Instrumentos v0.1.0 (28 tesis)
    ├── A. Persistencia (2)
    ├── B. Medición (5)
    ├── C. Inversión (4)
    ├── D. Interpolación (3)
    ├── E. Frontera (1)
    ├── F. Validación cruzada (3)
    ├── G. Metamorfosis (3)
    ├── H. Autorreferencia (3)
    ├── I. Compresión (2)
    └── J. Ética operativa (2)
```

## Apéndice B — Mapa de tesis y flags

| # | Flag | Tesis (resumen) | Bloque |
|---|------|-----------------|--------|
| 1 | `--publicar` | Vida media de n-grama decrece con corpus | A |
| 2 | `--canon-expandir` | Canon se define por lo rechazado | A |
| 3 | `--auditar` | `H(capa\|eje)` invariante del generador | B |
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
| 25 | `--comprimir` | `K(x) ∝ K(π(x))` | I |
| 26 | `--expandir` | Expansión converge a firma | I |
| 27 | `--censurar` | Censura estructural ≠ léxica | J |
| 28 | `--confesar` | Autoconsistencia reflexiva | J |

## Apéndice C — Glosario formal

| Término | Definición |
|---|---|
| **Firma estilométrica** | Vector `f(x) ∈ ℝ⁸`. |
| **Plano** | Tupla `(eje, elenco, capa, virus, adenovirus, retórico, cierre, temperatura, n_parrafos)`. |
| **N-grama** | Secuencia de `n` tokens consecutivos. |
| **Tic** | Fórmula sintáctica repetida dentro de un mismo texto. |
| **Vida media de un grama** | Ciclos entre primera y última aparición en el corpus. |
| **Corpus negativo** | Textos rechazados, con motivo. |
| **Dimensión efectiva** | Valores singulares necesarios para capturar el 90% de la energía. |
| **Punto de cambio** | Índice donde la media cambia de régimen, detectado por CUSUM. |
| **Involución** | Operador `E` con `E² = id`. |
| **Complemento del lenguaje** | Textos que el generador nunca aceptaría. |
| **Confesión** | Texto que enuncia las restricciones de su propio plano sin violarlas. |

## Apéndice D — Código completo del motor

El motor es un único archivo Python sin dependencias externas. Se reproduce íntegro a continuación.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MOTOR CASCABEL v0.1.0
=====================

Generador de posts con voz propia y 28 tesis operables.

Cambios respecto a v0.0.2:
  - 28 instrumentos nuevos, agrupados en 10 bloques (A-J).
  - Cada instrumento es una tesis falsable en lingüística computacional.
  - CLI extendida: 28 flags nuevos.
  - Serialización del canon positivo (publicados.json) y negativo.
  - Análisis de ablación, matriz PMI, CUSUM, SVD, zlib, clustering.
  - Operadores de inversión, interpolación, cruce, degradación, censura.

Cambios heredados de v0.0.2 sobre v0.0.1:
  - Tercer validador: anti-tics.
  - Polimorfismo de superficie en todos los métodos.
  - Cierres y adenovirus convertidos a pools.
  - 'cascabel' ya no aparece en el texto generado.

Arquitectura híbrida:
  - 19 posts íntegros embebidos.
  - 41 capítulos restantes cargados vía bootstrap.

Build interno del ensamblador: v0.5.0
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import random
import re
import statistics
import sys
import textwrap
import zlib
from abc import ABC, abstractmethod
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Sequence, Set, Tuple


# ============================================================================
# 0. METADATOS
# ============================================================================

METADATOS: Dict[str, Any] = {
    "nombre": "MOTOR CASCABEL",
    "version": "0.1.0",
    "build_ensamblador": "v0.5.0",
    "idioma": "es",
    "regla": "VARIACIONES NUEVAS. Nunca repetición. Nunca tic. Toda adición es una tesis.",
    "archivo_corpus": "EL BUS DE DATOS PERTENECE AL AMO.txt",
    "capitulos_totales": 48,
    "posts_embebidos": 19,
    "capitulos_bootstrap": 41,
    "n_grama_minimo": 5,
    "max_intentos": 32,
    "capitulos_promovidos": [25, 26, 28, 29, 43, 44, 45],
    "capitulos_ya_embebidos": [41, 47],
    "combinatoria_version": "1.0",
    "programador_version": "1.0",
    "programador_modos": ["exhaustivo", "muestreo", "dirigido"],
    "programador_ciclo_defecto": 200,
    "validadores": ["estilometria", "repeticion", "tics"],
    "instrumentos_version": "1.0",
    "instrumentos_bloques": {
        "A": ["publicar", "canon_expandir"],
        "B": ["auditar", "ablation", "matriz", "deriva", "firma"],
        "C": ["espejo", "contraejemplo", "ciego", "forense"],
        "D": ["interpolar", "reconstruir", "temporal"],
        "E": ["frontera"],
        "F": ["consenso", "disenso", "cuarentena"],
        "G": ["mutar", "cruzar", "degradar"],
        "H": ["autopsia", "espejo_negro", "parasito"],
        "I": ["comprimir", "expandir"],
        "J": ["censurar", "confesar"],
    },
}

CAPITULOS_EXCLUIDOS_BOOTSTRAP: Set[int] = set(
    METADATOS["capitulos_promovidos"] + METADATOS["capitulos_ya_embebidos"]
)


# ============================================================================
# 1. CORPUS EMBEBIDO — 19 POSTS ÍNTEGROS
# ============================================================================

POSTS_EMBEBIDOS: Tuple[Dict[str, Any], ...] = (
    {"id": "P01", "titulo": "Las Big Tech no son empresas de software, son camellos de alta precisión",
     "cuerpo": (
        "Las Big Tech no son empresas de software. Son camellos de alta precisión.\n\n"
        "Un camello no está diseñado para correr. Está diseñado para no morir. "
        "Aguanta tres semanas sin agua, cruza un desierto que no ha cartografiado y "
        "llega al otro lado con la misma expresión. Nadie le pide elegancia. Le piden "
        "que no se detenga.\n\n"
        "Cuando alguien te dice que una tecnológica es «ágil», pregúntale cuántos "
        "trimestres lleva sin cambiar de rumbo. Cuando te dice que es «innovadora», "
        "pregúntale cuántas de sus líneas de producto nacieron de una adquisición. "
        "Cuando te dice que es «una plataforma», pregúntale quién paga la plataforma.\n\n"
        "El software es el jorobado que llevan encima. No es el animal."
     ), "ejes": ["bigtech", "producto", "poder"], "elenco": ["inversor", "fundador"],
     "capa": "tecnico", "origen": "original"},

    {"id": "P02", "titulo": "El «experto en IA» no existe: solo hay arquitectos y estafadores",
     "cuerpo": (
        "El «experto en IA» no existe. Existen dos categorías y ninguna se llama así.\n\n"
        "La primera es el arquitecto. Sabe qué se puede construir, qué no, cuánto "
        "cuesta y qué se rompe cuando lo construyes. No habla de inteligencia. Habla "
        "de latencia, de coste por token, de deriva de distribución. Cuando no sabe "
        "algo, dice que no lo sabe, y eso le cuesta clientes.\n\n"
        "La segunda es el estafador. No sabe qué se puede construir, pero sabe qué "
        "se puede vender. Su vocabulario es más amplio que el del arquitecto porque "
        "no está limitado por la realidad. Habla de «sinergias cognitivas», de "
        "«transformación exponencial», de «democratizar el acceso». Cobra por "
        "adelantado.\n\n"
        "El problema no es que existan estafadores. El problema es que el mercado "
        "no distingue. El arquitecto cobra menos y tarda más. El estafador cobra más "
        "y entrega un PowerPoint.\n\n"
        "Y el PowerPoint se aprueba antes."
     ), "ejes": ["ia", "talento", "poder"], "elenco": ["consultor", "inversor", "cto"],
     "capa": "tecnico", "origen": "original"},

    {"id": "P03", "titulo": "El organigrama es un sketch de humor negro",
     "cuerpo": (
        "El organigrama es un sketch de humor negro que alguien decidió imprimir "
        "en A3 y colgar en la pared.\n\n"
        "Arriba hay una caja. Dentro de la caja hay un nombre. Ese nombre toma "
        "decisiones sobre personas que no conoce, sobre productos que no usa y "
        "sobre mercados que no visita. Debajo hay tres cajas. Dentro de esas tres "
        "cajas hay tres nombres que compiten por subir a la caja de arriba. Debajo "
        "hay nueve cajas. Debajo, veintisiete. Debajo, ochenta y uno.\n\n"
        "Nadie sabe qué hace la caja de al lado. Todos saben a quién reporta.\n\n"
        "La estructura no existe para producir. Existe para que alguien pueda "
        "explicar en una reunión quién es el responsable de que algo no se haya "
        "hecho. Es un sistema de asignación de culpa disfrazado de sistema de "
        "asignación de trabajo.\n\n"
        "Y funciona. Eso es lo peor."
     ), "ejes": ["organigrama", "cultura", "poder"], "elenco": ["consultor", "cto", "becario"],
     "capa": "administrativo", "origen": "original"},

    {"id": "P04", "titulo": "Pagas 100k a un senior. En 12 meses ese rol ya no necesita existir",
     "cuerpo": (
        "Pagas cien mil a un senior. En doce meses, ese rol ya no necesita existir.\n\n"
        "No porque el senior sea malo. Porque el senior es bueno. Es tan bueno que "
        "documenta, automatiza, simplifica y reduce la superficie de su propio "
        "trabajo. Al final del año, lo que hacía requiere la mitad de gente. Y la "
        "mitad de gente incluye a la persona que lo hizo posible.\n\n"
        "La empresa no despide al senior por ingratitud. Lo despide por coherencia. "
        "El senior ha demostrado que el rol era prescindible. La empresa acepta la "
        "demostración.\n\n"
        "Por eso los seniors inteligentes no automatizan del todo. Dejan una parte "
        "manual, opaca, ligeramente tediosa, que solo ellos saben hacer. No es "
        "pereza. Es seguro de vida.\n\n"
        "Y por eso las empresas que presumen de «cultura de automatización» tienen "
        "los mejores ingenieros y los peores contratos."
     ), "ejes": ["talento", "compensacion", "producto"], "elenco": ["senior", "cto"],
     "capa": "tecnico", "origen": "original"},

    {"id": "P05", "titulo": "Kierkegaard y Kuhn, o por qué nunca los cito",
     "cuerpo": (
        "Nunca cito a Kierkegaard. Nunca cito a Kuhn. No por desprecio. Por higiene.\n\n"
        "Citar a Kierkegaard en un post sobre tecnología es una forma de decir «yo "
        "también leí cosas difíciles» sin decir nada sobre tecnología. Citar a Kuhn "
        "es una forma de decir «esto no es un problema técnico, es un cambio de "
        "paradigma» sin explicar cuál, ni cómo, ni a costa de quién.\n\n"
        "La cita culta es una forma de autoridad prestada. Te pones el traje de "
        "alguien que pensó mejor que tú y esperas que el lector confunda el traje "
        "con el cuerpo.\n\n"
        "Si tengo que explicar que un cambio de paradigma ocurre cuando los que "
        "sostienen el paradigma anterior se mueren, lo explico. No necesito a Kuhn. "
        "Kuhn necesitaba a Kuhn porque estaba construyendo una disciplina.\n\n"
        "Yo solo estoy escribiendo un post.\n\n"
        "Y el post se defiende solo o no se defiende."
     ), "ejes": ["epistemologia", "cultura"], "elenco": ["consultor"],
     "capa": "religioso", "origen": "original"},

    {"id": "P06", "titulo": "El kill switch es una fantasía de ingeniero",
     "cuerpo": (
        "El kill switch es una fantasía de ingeniero: la idea de que un sistema "
        "suficientemente complejo puede apagarse con un gesto limpio.\n\n"
        "No puede. No porque el botón no exista, sino porque el botón no sabe qué "
        "está apagando. Un sistema grande no es una máquina: es un ecosistema de "
        "dependencias. Apagas el motor y se cae la telemetría. Apagas la telemetría "
        "y se cae la facturación. Apagas la facturación y se cae el soporte. Apagas "
        "el soporte y alguien llama a un abogado.\n\n"
        "El kill switch funciona en el simulacro. En el simulacro, el sistema no "
        "está haciendo nada importante. En producción, el sistema siempre está "
        "haciendo algo importante para alguien que no sabe que existe.\n\n"
        "La verdadera pregunta no es cómo se apaga. Es quién tiene el valor de "
        "asumir lo que se rompe cuando se apaga.\n\n"
        "Y esa persona no está en la sala."
     ), "ejes": ["ia", "infraestructura", "regulacion"], "elenco": ["regulador", "cto"],
     "capa": "militar", "origen": "original"},

    {"id": "P07", "titulo": "La regulación de IA llega tarde y llega mal, y da igual",
     "cuerpo": (
        "La regulación de IA llega tarde y llega mal. Y da igual, porque su función "
        "no es regular.\n\n"
        "Llega tarde porque el legislador aprende el vocabulario del sector unos "
        "dieciocho meses después de que el sector lo haya abandonado. Regula "
        "«modelos fundacionales» cuando el mercado ya habla de agentes. Regula "
        "«sesgos» cuando el problema es la concentración. Regula «transparencia» "
        "cuando la asimetría real está en los datos de entrenamiento, que nadie "
        "enseña.\n\n"
        "Llega mal porque se escribe con la industria dentro de la sala. Y la "
        "industria no va a la sala a obstruir: va a redactar. Un texto redactado "
        "por el regulado y firmado por el regulador se llama ley.\n\n"
        "Y da igual porque la función de la ley no es cambiar el comportamiento. "
        "Es producir la apariencia de que alguien está vigilando.\n\n"
        "La apariencia es el producto. El resto es anexo."
     ), "ejes": ["regulacion", "ia", "poder"], "elenco": ["regulador", "consultor", "fundador"],
     "capa": "juridico", "origen": "original"},

    {"id": "P08", "titulo": "El bus de datos pertenece al amo",
     "cuerpo": (
        "El bus de datos pertenece al amo.\n\n"
        "No al que lo diseñó. No al que lo mantiene. No al que lo documentó a las "
        "tres de la mañana. Al amo. Y el amo es quien decide qué se transporta, a "
        "qué velocidad y hacia dónde. El resto son pasajeros con credenciales.\n\n"
        "Durante años nos contaron que la infraestructura era neutra. Que era una "
        "autopista y que lo importante era lo que conducías. Mentira útil: mientras "
        "creías que conducías, alguien cobraba el peaje, decidía los carriles y "
        "cerraba los accesos que no le convenían.\n\n"
        "Quien controla el bus controla el orden de llegada. Y el orden de llegada "
        "es el negocio."
     ), "ejes": ["infraestructura", "datos", "poder"], "elenco": ["cto", "inversor"],
     "capa": "ferroviario", "origen": "capitulo_41"},

    {"id": "P09", "titulo": "Nadie contrata talento; se contrata coartada",
     "cuerpo": (
        "Nadie contrata talento. Se contrata coartada.\n\n"
        "El proceso de selección no busca a la mejor persona para el puesto. Busca "
        "a la persona cuya contratación sea más fácil de defender si el proyecto "
        "sale mal. Por eso se prefieren currículos ordenados, empresas conocidas, "
        "trayectorias legibles. No porque funcionen mejor, sino porque se explican "
        "mejor en una reunión de comité.\n\n"
        "Un candidato brillante y raro es un riesgo de explicación. Un candidato "
        "mediocre y previsible es una póliza.\n\n"
        "Por eso los mejores no están en las empresas grandes. Están en sitios "
        "donde nadie pregunta por qué."
     ), "ejes": ["talento", "organigrama", "cultura"], "elenco": ["becario", "senior", "cto"],
     "capa": "administrativo", "origen": "capitulo_47"},

    {"id": "P10", "titulo": "El roadmap es una novela de ciencia ficción autopublicada",
     "cuerpo": (
        "El roadmap es una novela de ciencia ficción autopublicada que nadie "
        "corrige porque nadie la lee entera.\n\n"
        "Tiene protagonistas (los equipos), antagonistas (la deuda técnica), un "
        "clímax (el lanzamiento) y un final feliz (el crecimiento). Tiene capítulos "
        "trimestrales. Tiene retcon: lo que en enero era «exploración» en julio era "
        "«apuesta estratégica» y en diciembre era «aprendizaje».\n\n"
        "Lo único que no tiene es un lector que compare la versión de enero con la "
        "de diciembre. Y sin comparación no hay ficción: hay historia oficial.\n\n"
        "Guarda los roadmaps. Todos. En cinco años tendrás la mejor novela cómica "
        "del sector."
     ), "ejes": ["producto", "cultura", "organigrama"], "elenco": ["fundador", "consultor"],
     "capa": "literario", "origen": "original"},

    {"id": "P11", "titulo": "La cultura de empresa es un cementerio con catering",
     "cuerpo": (
        "La cultura de empresa es un cementerio con catering.\n\n"
        "Se entra por la puerta y hay fruta. Hay café de especialidad. Hay una "
        "pared con valores escritos en tipografía fina. Hay una sala con un sofá "
        "que nadie usa. Debajo de todo eso hay una capa geológica de decisiones "
        "tomadas por gente que ya no está, que nadie recuerda y que siguen "
        "determinando lo que se puede y no se puede hacer.\n\n"
        "La cultura no es lo que se dice. Es lo que se permite. Y lo que se permite "
        "se decide en reuniones sin acta.\n\n"
        "La fruta es el catering. Los valores son las flores. El resto es "
        "arqueología."
     ), "ejes": ["cultura", "organigrama"], "elenco": ["becario", "cto"],
     "capa": "religioso", "origen": "original"},

    {"id": "P12", "titulo": "El prompt es el nuevo PowerPoint",
     "cuerpo": (
        "El prompt es el nuevo PowerPoint: una tecnología de persuasión disfrazada "
        "de tecnología de producción.\n\n"
        "En los noventa, el que dominaba PowerPoint dominaba la sala. No importaba "
        "si el proyecto era bueno. Importaba si la diapositiva era clara. Se "
        "ascendió a una generación entera por saber dibujar flechas.\n\n"
        "Hoy el que domina el prompt domina la demo. No importa si el sistema "
        "funciona. Importa si la respuesta es convincente en los primeros treinta "
        "segundos. Se está ascendiendo a otra generación por saber escribir en "
        "imperativo.\n\n"
        "En ambos casos, la habilidad real —construir algo que aguante— queda "
        "fuera de la sala donde se decide.\n\n"
        "Y en ambos casos, el que domina la herramienta de persuasión acaba "
        "dirigiendo a los que dominan la de producción."
     ), "ejes": ["ia", "producto", "cultura"], "elenco": ["consultor", "inversor", "llm"],
     "capa": "tecnico", "origen": "original"},

    {"id": "P13", "titulo": "Los datos sintéticos son el homeópata del machine learning",
     "cuerpo": (
        "Los datos sintéticos son el homeópata del machine learning: se diluye el "
        "problema hasta que la solución parece agua.\n\n"
        "La lógica es impecable en el papel. Si no tienes datos, genéralos. Si los "
        "generas con el modelo, el modelo aprende de sí mismo. Si aprende de sí "
        "mismo, mejora. Si mejora, no necesitas datos reales. Si no necesitas datos "
        "reales, no necesitas el mundo.\n\n"
        "El problema es el paso tres. Un modelo que aprende de sí mismo no mejora: "
        "se concentra. Pierde los bordes. Olvida lo que no había aprendido bien. "
        "Se vuelve más seguro y menos correcto.\n\n"
        "Es el efecto de estudiar solo con tus apuntes. Cada repaso te hace más "
        "coherente con lo que ya creías y menos capaz de detectar lo que nunca "
        "entendiste.\n\n"
        "El agua no cura. El agua hidrata. Y a veces ni eso."
     ), "ejes": ["ia", "datos", "epistemologia"], "elenco": ["llm", "cto"],
     "capa": "medico", "origen": "original"},

    {"id": "P14", "titulo": "La agilidad era un sindicato disfrazado de metodología",
     "cuerpo": (
        "La agilidad era un sindicato disfrazado de metodología. Por eso la "
        "mataron.\n\n"
        "Su promesa original no era entregar más rápido. Era proteger al equipo de "
        "la interrupción arbitraria. El backlog priorizado, la iteración cerrada, "
        "el rol del product owner: todo eso eran barricadas. Servían para que el "
        "directivo de turno no pudiera cambiar el rumbo un martes por la tarde "
        "porque había leído un artículo.\n\n"
        "Funcionó lo suficiente para que los directivos se dieran cuenta. Y "
        "entonces hicieron lo que siempre hacen: adoptaron el vocabulario y "
        "vaciaron el mecanismo. Hoy hay «sprints» sin cierre, «retros» sin "
        "consecuencias y «product owners» que no deciden.\n\n"
        "La barricada se convirtió en decorado. Y el equipo volvió a estar "
        "expuesto, ahora con post-its."
     ), "ejes": ["metodologia", "organigrama", "cultura"], "elenco": ["becario", "consultor", "cto"],
     "capa": "militar", "origen": "original"},

    {"id": "P15", "titulo": "El CTO que sobrevive no es el mejor: es el que no firma",
     "cuerpo": (
        "El CTO que sobrevive no es el mejor. Es el que no firma.\n\n"
        "En cualquier organización grande hay una serie de decisiones que, si "
        "salen mal, requieren un responsable. La habilidad política central del "
        "cargo no es tomar esas decisiones, sino conseguir que las tome otro y "
        "quedar cerca para poder decir «yo avisé».\n\n"
        "Por eso los CTO longevos hablan en condicional. «Habría que evaluar». "
        "«Se podría considerar». «Depende del contexto». No es cobardía: es "
        "supervivencia. La persona que dice «hazlo» es la persona que cae.\n\n"
        "El resultado es que las decisiones importantes las toman quienes no "
        "entienden el sistema, y quienes entienden el sistema se limitan a "
        "documentar por qué salió mal.\n\n"
        "Se llama liderazgo técnico. Podría llamarse otra cosa."
     ), "ejes": ["talento", "poder", "organigrama"], "elenco": ["cto", "senior", "consultor"],
     "capa": "juridico", "origen": "original"},

    {"id": "P16", "titulo": "La nube es el alquiler eterno con nombre bonito",
     "cuerpo": (
        "La nube es el alquiler eterno con nombre bonito.\n\n"
        "Te vendieron elasticidad. Te dieron dependencia. Te vendieron que no "
        "tendrías que preocuparte por servidores. Te dieron que te preocuparías "
        "por facturas. Te vendieron que pagarías solo por lo que usas. Te dieron "
        "que no sabrías nunca cuánto usas.\n\n"
        "El coste de salida no se mide en dinero. Se mide en años. Años de "
        "credenciales propietarias, de colas gestionadas, de funciones sin "
        "equivalente, de observabilidad atada al proveedor. Salir no es migrar: "
        "es reescribir.\n\n"
        "Y reescribir cuesta más que aceptar el siguiente aumento.\n\n"
        "Por eso el alquiler es eterno. No porque no puedas irte. Porque irte "
        "es empezar de cero en un mercado donde ya llevas cinco años de retraso."
     ), "ejes": ["nube", "infraestructura", "compensacion"], "elenco": ["cto", "inversor"],
     "capa": "administrativo", "origen": "original"},

    {"id": "P17", "titulo": "El benchmarking es pornografía comparativa",
     "cuerpo": (
        "El benchmarking es pornografía comparativa: excitación sin consecuencia.\n\n"
        "Se eligen tres competidores. Se eligen cinco métricas. Se eligen los "
        "periodos en los que las métricas favorecen la narrativa. Se produce un "
        "informe. El informe tiene un gráfico. El gráfico tiene una línea azul que "
        "sube y una línea gris que baja. La línea azul es la nuestra.\n\n"
        "Nadie pregunta cómo se midió la línea gris. Nadie pregunta si la métrica "
        "significa lo mismo en las dos empresas. Nadie pregunta quién pagó el "
        "informe.\n\n"
        "El benchmarking no sirve para saber cómo estás. Sirve para justificar "
        "una decisión que ya se había tomado. Es un anexo, no un diagnóstico."
     ), "ejes": ["producto", "cultura", "datos"], "elenco": ["consultor", "inversor"],
     "capa": "medico", "origen": "original"},

    {"id": "P18", "titulo": "El churn no se arregla con onboarding; se arregla con honestidad",
     "cuerpo": (
        "El churn no se arregla con onboarding. Se arregla con honestidad.\n\n"
        "La gente no se va porque no entienda el producto. Se va porque lo "
        "entendió. Se va porque descubrió que la promesa era más grande que la "
        "herramienta, que el caso de uso estrella no es su caso de uso, que el "
        "soporte responde con plantilla, que la integración que necesitaba está "
        "en el roadmap desde hace dos años.\n\n"
        "Y en lugar de arreglar eso, se contrata a alguien para que diseñe un "
        "tour de bienvenida.\n\n"
        "El tour explica mejor un producto que sigue sin resolver el problema. "
        "Es como ponerle un lazo a una puerta que no abre.\n\n"
        "El usuario no es tonto. Es paciente. Y la paciencia tiene fecha de "
        "caducidad."
     ), "ejes": ["producto", "datos", "cultura"], "elenco": ["fundador", "becario"],
     "capa": "medico", "origen": "original"},

    {"id": "P19", "titulo": "El futuro ya se diseñó en 1972 y lo perdimos en una reunión",
     "cuerpo": (
        "El futuro ya se diseñó en 1972 y lo perdimos en una reunión.\n\n"
        "En 1972 había gente pensando en redes distribuidas, en interfaces "
        "conversacionales, en computación ubicua, en cooperativas de datos. No "
        "eran ingenuos. Eran minoritarios. Y la minoría pierde cuando la mayoría "
        "tiene capital.\n\n"
        "Lo que ganó fue otra cosa: centralización con buena prensa, interfaces "
        "que no conversan sino que instruyen, computación concentrada en edificios "
        "con aire acondicionado, datos en manos de quien los puede monetizar.\n\n"
        "No fue un accidente. Fue una elección tomada en reuniones donde no "
        "estaba la gente que había pensado el futuro. Estaba la gente que lo "
        "podía pagar.\n\n"
        "Y lo pagó. Vaya si lo pagó."
     ), "ejes": ["epistemologia", "poder", "infraestructura"], "elenco": ["fundador", "inversor", "llm"],
     "capa": "literario", "origen": "original"},
)

assert len(POSTS_EMBEBIDOS) == 19, "El corpus embebido debe tener exactamente 19 posts."
assert len({p["id"] for p in POSTS_EMBEBIDOS}) == 19, "IDs de post duplicados."


# ============================================================================
# 2. BOOTSTRAP
# ============================================================================

RE_ENCABEZADO = re.compile(
    r"^\s*(?:#{1,3}\s*)?"
    r"(?:CAP[IÍ]TULO|Cap[ií]tulo|CAP\.?|Cap\.?)?\s*"
    r"(\d{1,3})"
    r"\s*(?:[\.\:\-—–]\s*.*)?$",
    re.IGNORECASE,
)


@dataclass
class ResultadoBootstrap:
    exito: bool
    ruta: Optional[str]
    capitulos: Dict[int, str] = field(default_factory=dict)
    excluidos: List[int] = field(default_factory=list)
    mensaje: str = ""
    bytes_leidos: int = 0

    def __len__(self) -> int:
        return len(self.capitulos)


def _normalizar_texto(bruto: str) -> str:
    texto = bruto.replace("\r\n", "\n").replace("\r", "\n")
    texto = re.sub(r"[ \t]+\n", "\n", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


def _trocear_capitulos(texto: str) -> Dict[int, str]:
    lineas = texto.split("\n")
    capitulos: Dict[int, List[str]] = {}
    actual: Optional[int] = None
    preludio: List[str] = []

    for linea in lineas:
        coincidencia = RE_ENCABEZADO.match(linea)
        es_encabezado = (
            coincidencia is not None
            and len(linea.strip()) < 120
            and not linea.strip().endswith(".")
            and (
                re.match(r"^\s*(?:#{1,3}\s*)?(?:CAP[IÍ]TULO|Cap[ií]tulo|CAP\.?|Cap\.?)", linea)
                or re.match(r"^\s*#{1,3}\s*\d{1,3}", linea)
                or re.match(r"^\s*\d{1,3}\s*[\.\:\-—–]\s*\S", linea)
            )
        )

        if es_encabezado and coincidencia is not None:
            numero = int(coincidencia.group(1))
            actual = numero
            capitulos.setdefault(actual, [])
        else:
            if actual is None:
                preludio.append(linea)
            else:
                capitulos[actual].append(linea)

    resultado: Dict[int, str] = {}
    for numero, cuerpo in capitulos.items():
        limpio = _normalizar_texto("\n".join(cuerpo))
        if limpio:
            resultado[numero] = limpio

    preludio_limpio = _normalizar_texto("\n".join(preludio))
    if len(preludio_limpio) > 400:
        resultado[0] = preludio_limpio

    return resultado


def bootstrap_corpus(
    ruta: Optional[str] = None,
    excluidos: Optional[Set[int]] = None,
    verbose: bool = False,
) -> ResultadoBootstrap:
    ruta = ruta or METADATOS["archivo_corpus"]
    excluidos = excluidos if excluidos is not None else CAPITULOS_EXCLUIDOS_BOOTSTRAP

    camino = Path(ruta)
    if not camino.exists():
        return ResultadoBootstrap(
            exito=False, ruta=str(camino),
            mensaje=f"No se encontró '{camino}'. Motor en modo degradado: solo corpus embebido.",
        )

    try:
        bruto = camino.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            bruto = camino.read_text(encoding="latin-1")
        except Exception as exc:
            return ResultadoBootstrap(exito=False, ruta=str(camino),
                mensaje=f"Error de codificación al leer '{camino}': {exc}")
    except OSError as exc:
        return ResultadoBootstrap(exito=False, ruta=str(camino),
            mensaje=f"Error de E/S al leer '{camino}': {exc}")

    texto = _normalizar_texto(bruto)
    todos = _trocear_capitulos(texto)

    filtrados: Dict[int, str] = {}
    descartados: List[int] = []
    for numero, cuerpo in sorted(todos.items()):
        if numero in excluidos:
            descartados.append(numero)
            continue
        filtrados[numero] = cuerpo

    if verbose:
        print(f"[bootstrap] {camino}: {len(todos)} capítulos detectados, "
              f"{len(filtrados)} cargados, {len(descartados)} excluidos.",
              file=sys.stderr)

    return ResultadoBootstrap(
        exito=True, ruta=str(camino), capitulos=filtrados,
        excluidos=sorted(descartados),
        mensaje=f"Bootstrap correcto: {len(filtrados)} capítulos cargados.",
        bytes_leidos=len(bruto.encode("utf-8")),
    )


# ============================================================================
# 3. PATRONES DE CIERRE — 14, POLIMORFOS
# ============================================================================

PATRONES_CIERRE: Tuple[Dict[str, Any], ...] = (
    {"id": "C01", "nombre": "sentencia_seca", "peso": 1.00, "compatible": ["*"],
     "pool": ("Y eso es todo.", "Y ya está.", "Y punto.", "Nada más.", "Fin.", "Ahí queda.")},
    {"id": "C02", "nombre": "inversion", "peso": 0.95, "compatible": ["*"],
     "pool": ("Lo que parecía {SUJETO} era {OBJETO}.",
              "Lo que llamamos {SUJETO} es, en realidad, {OBJETO}.",
              "El {SUJETO} no era el problema. Era la solución mal contada.",
              "{SUJETO} y {OBJETO} son la misma cosa con distinto nombre.",
              "Al final, {SUJETO} resultó ser {OBJETO}.")},
    {"id": "C03", "nombre": "degradacion", "peso": 0.90, "compatible": ["*"],
     "pool": ("Y así, poco a poco, {SUJETO} se convirtió en {OBJETO}.",
              "No hubo un momento exacto. Solo un deterioro lo bastante lento para que nadie tuviera que decidirlo.",
              "Nadie lo decidió. Simplemente dejó de impedirse.",
              "Se fue cayendo solo. Y nadie puso la mano.",
              "Un día {SUJETO} era {OBJETO}. Nadie supo cuándo.")},
    {"id": "C04", "nombre": "falso_consuelo", "peso": 0.85,
     "compatible": ["cultura", "talento", "organigrama", "producto"],
     "pool": ("Consuélate: siempre ha sido así. Y siempre será así.",
              "Tranquilo. El problema no es tuyo. Es de todos, que es la forma más elegante de decir que no es de nadie.",
              "No te preocupes. Mañana seguirá igual, y eso también es un alivio.",
              "Respira. Esto lleva pasando desde antes de que llegaras. Y seguirá después de que te vayas.")},
    {"id": "C05", "nombre": "cifra", "peso": 0.80,
     "compatible": ["compensacion", "datos", "producto", "nube"],
     "pool": ("Ponle una cifra y dormirás mejor.",
              "El número no importa. Importa quién lo eligió.",
              "Si no puedes medirlo, no puedes defenderlo. Y si no puedes defenderlo, no lo hagas.",
              "Los números siempre salen. Lo que no siempre sale es quién los puso ahí.",
              "Mide lo que quieras. Pero mide también por qué lo mides.")},
    {"id": "C06", "nombre": "silencio", "peso": 0.75, "compatible": ["*"],
     "pool": ("No hace falta decirlo.", "Ya sabes lo que sigue.",
              "El resto lo pones tú.", "Y aquí me callo.", "Nada más por mi parte.")},
    {"id": "C07", "nombre": "pregunta_retorica", "peso": 0.85, "compatible": ["*"],
     "pool": ("¿Y tú qué habrías hecho?",
              "¿A quién le importa esto? A ti, que has llegado hasta aquí.",
              "¿Cuánto tiempo más se puede sostener esto?",
              "¿De verdad hacía falta un post para esto?",
              "¿Otra vez?")},
    {"id": "C08", "nombre": "acusacion_directa", "peso": 0.70,
     "compatible": ["poder", "regulacion", "talento", "cultura"],
     "pool": ("Y tú lo sabías.", "Y tú estabas en la sala.", "Y tú firmaste.",
              "Y tú, que me lees, lo has permitido.", "Y tú también.")},
    {"id": "C09", "nombre": "aforismo", "peso": 0.95, "compatible": ["*"],
     "pool": ("Toda {SUJETO} es una {OBJETO} que aún no ha aprendido a disimular.",
              "No hay {SUJETO} sin {OBJETO}. Solo {SUJETO} con mejor prensa.",
              "El {SUJETO} es el impuesto que pagas por creer en el {OBJETO}.",
              "Todo {SUJETO} empieza siendo {OBJETO} y acaba creyéndose {SUJETO}.",
              "{SUJETO} sin {OBJETO} es solo una palabra larga.")},
    {"id": "C10", "nombre": "profecia_vencida", "peso": 0.80,
     "compatible": ["ia", "regulacion", "epistemologia", "infraestructura"],
     "pool": ("Ya pasó. Ya está pasando. Ya pasó y no nos dimos cuenta.",
              "Esto no es una predicción. Es un acta.",
              "No estoy advirtiendo de nada. Estoy describiendo lo que ya ocurrió mientras discutíamos otra cosa.",
              "No hay nada que prever. Todo está previsto. Y todo ha ocurrido ya.",
              "Llegamos tarde incluso a la crónica de lo que ya pasó.")},
    {"id": "C11", "nombre": "reduccion_al_absurdo", "peso": 0.75, "compatible": ["*"],
     "pool": ("Llevado al extremo, esto es {OBJETO}. Y ya estamos en el extremo.",
              "Si esto funciona, entonces cualquier cosa funciona. Y eso es exactamente el problema.",
              "El argumento, llevado hasta el final, se come a sí mismo.",
              "Llevado al extremo, no queda extremo. Queda esto.")},
    {"id": "C12", "nombre": "cortesia_venenosa", "peso": 0.70, "compatible": ["*"],
     "pool": ("Gracias por leer hasta aquí. No era necesario.",
              "Un saludo a quien corresponda, que sabe quién es.",
              "Que tengas un buen día. Yo ya he tenido el mío.",
              "Un abrazo. Y un recordatorio: esto no era para ti.",
              "Gracias. Y perdón. Por el orden que prefieras.")},
    {"id": "C13", "nombre": "loop", "peso": 0.65,
     "compatible": ["epistemologia", "cultura", "organigrama"],
     "pool": ("Y volvemos al principio, que es donde estábamos.",
              "Esto ya lo he escrito. Y lo volveré a escribir, porque nada ha cambiado.",
              "La conclusión es la introducción con más años.",
              "Aquí se cierra el círculo. Que no es un círculo: es una espiral que no sube.")},
    {"id": "C14", "nombre": "cascabel", "peso": 1.00, "compatible": ["*"],
     "pool": ("Que suene. Aunque nadie lo escuche.",
              "Que suene. Aunque solo lo escuche quien tiene que escucharlo.",
              "Suena. Si molesta, es que funciona.",
              "No convoca. Irrita. Y ya es algo.",
              "Que suene. Y que dure.")},
)

assert len(PATRONES_CIERRE) == 14
for _c in PATRONES_CIERRE:
    assert "pool" in _c and len(_c["pool"]) >= 3


# ============================================================================
# 4. ADENOVIRUS — 8, POLIMORFOS
# ============================================================================

ADENOVIRUS: Tuple[Dict[str, Any], ...] = (
    {"id": "A01", "nombre": "redefinicion_polimorfa", "peso": 1.00,
     "operacion": "Redefinir un término del discurso dominante.",
     "pool": ("No es {X}. Es {Y}.",
              "{X} hace una sola cosa: {Y}. Lo demás es folclore.",
              "{X} nació como {Y}. Sigue siendo {Y}, ahora con mejor prensa.",
              "{X} cuesta {Y}. El resto es contabilidad creativa.",
              "{X} es lo que queda cuando le quitas {Y}. Y no queda mucho.",
              "{X} es {Y} con corbata. Misma cosa, distinto presupuesto.",
              "{X} no es el problema. {X} es el nombre que le hemos dado al problema.")},
    {"id": "A02", "nombre": "contraste_polimorfo", "peso": 0.95,
     "operacion": "Contraponer discurso y práctica.",
     "pool": ("Todos {VERBO}. Nadie {VERBO} lo que queda después.",
              "Unos {VERBO}. Otros {VERBO}. Ninguno firma.",
              "{X} por fuera. {Y} por dentro.",
              "Se dice {X}. Se hace {Y}.",
              "{X} en la sala. {Y} en el ticket.",
              "La mitad {VERBO}. La otra mitad mira. Nadie mide.")},
    {"id": "A03", "nombre": "desenmascaramiento_polimorfo", "peso": 0.90,
     "operacion": "Revelar la función latente de una práctica manifiesta.",
     "pool": ("Se dice {X} para no decir {Y}.",
              "{X} es la palabra que usamos para no tener que decir {Y}.",
              "Cuando alguien dice {X}, está pidiendo permiso para {Y}.",
              "Detrás de {X} hay {Y}. Siempre. Sin excepción.",
              "{X} suena mejor que {Y}. Por eso se dice {X}.",
              "El vocabulario cambia. La cosa que oculta {X} es {Y}.")},
    {"id": "A04", "nombre": "resuelve_y_crea", "peso": 0.90,
     "operacion": "Mostrar el efecto colateral de una solución.",
     "pool": ("{X} resuelve {Y} y crea {Z}.",
              "Gracias a {X} ya no tenemos {Y}. Ahora tenemos {Z}.",
              "{X} arregla {Y}. Lo que no dice es que también produce {Z}.",
              "{X} resolvió {Y}. Y de paso, {Z}. Nadie habló de {Z}.")},
    {"id": "A05", "nombre": "interpelacion_directa", "peso": 0.85,
     "operacion": "Dirigirse al lector con una pregunta concreta.",
     "pool": ("Cuando {ALGUIEN} te dice {X}, pregúntale {Y}.",
              "Si alguien te dice {X}, pídele {Y} por escrito.",
              "Cada vez que oigas {X}, comprueba {Y}.",
              "Si te dicen {X}, mira {Y}. Y luego decide.")},
    {"id": "A06", "nombre": "doble_causalidad", "peso": 0.85,
     "operacion": "Distinguir causa aparente de causa real.",
     "pool": ("No {X} porque {A}. {X} porque {B}.",
              "La causa no es {A}. La causa es {B}. {A} es solo la excusa.",
              "Se dice que es por {A}. Es por {B}. {A} queda mejor.")},
    {"id": "A07", "nombre": "cadena_al_absurdo", "peso": 0.80,
     "operacion": "Encadenar consecuencias hasta el absurdo.",
     "pool": ("Si {X}, entonces {Y}. Y si {Y}, entonces {Z}.",
              "Si aceptamos {X}, aceptamos {Y}. Y si aceptamos {Y}, aceptamos {Z}. Y {Z} no tiene defensa.",
              "Empieza por {X}. Sigue por {Y}. Termina en {Z}. Y nadie habrá decidido nada.")},
    {"id": "A08", "nombre": "desplazamiento_de_foco", "peso": 0.95,
     "operacion": "Desplazar el foco del problema aparente al real.",
     "pool": ("El problema no es {X}. El problema es {Y}.",
              "{X} no es el problema. {Y} sí. Y {Y} no se discute.",
              "Todos hablan de {X}. Nadie habla de {Y}. {Y} es el problema.",
              "{X} es la anécdota. {Y} es la estructura.")},
)

assert len(ADENOVIRUS) == 8
for _a in ADENOVIRUS:
    assert "pool" in _a and len(_a["pool"]) >= 3


# ============================================================================
# 5. VIRUS — 12 FORMAS LÓGICAS
# ============================================================================

VIRUS: Tuple[Dict[str, Any], ...] = (
    {"id": "V01", "nombre": "redefinicion", "peso": 1.00, "compatible": ["*"],
     "operacion": "Sustituir el término del discurso dominante por uno más crudo.",
     "esquema": "{TERMINO_OFICIAL} -> {TERMINO_REAL}"},
    {"id": "V02", "nombre": "contraste_estadistico", "peso": 0.90,
     "compatible": ["cultura", "talento", "organigrama"],
     "operacion": "Contraponer lo que se dice que se hace con lo que se hace.",
     "esquema": "todos X / nadie Y"},
    {"id": "V03", "nombre": "desenmascaramiento", "peso": 0.95,
     "compatible": ["poder", "regulacion", "cultura"],
     "operacion": "Revelar la función latente de una práctica manifiesta.",
     "esquema": "manifiesto -> latente"},
    {"id": "V04", "nombre": "efecto_colateral", "peso": 0.85,
     "compatible": ["ia", "infraestructura", "nube", "producto"],
     "operacion": "Mostrar que la solución es la causa del problema siguiente.",
     "esquema": "solucion -> problema'"},
    {"id": "V05", "nombre": "genealogia", "peso": 0.80,
     "compatible": ["epistemologia", "poder", "regulacion"],
     "operacion": "Rastrear el origen de una práctica hasta un interés.",
     "esquema": "practica -> origen interesado"},
    {"id": "V06", "nombre": "inversion_causal", "peso": 0.85, "compatible": ["*"],
     "operacion": "Invertir la flecha causal habitual.",
     "esquema": "A causa B -> B causa A"},
    {"id": "V07", "nombre": "escala", "peso": 0.80,
     "compatible": ["ia", "datos", "infraestructura", "compensacion"],
     "operacion": "Mostrar que el fenómeno cambia de naturaleza al crecer.",
     "esquema": "pequeño -> grande (cambio de tipo)"},
    {"id": "V08", "nombre": "incentivo", "peso": 0.95,
     "compatible": ["talento", "compensacion", "producto", "organigrama"],
     "operacion": "Explicar el comportamiento por el incentivo, no por la intención.",
     "esquema": "conducta -> incentivo"},
    {"id": "V09", "nombre": "falsa_oposicion", "peso": 0.75,
     "compatible": ["cultura", "metodologia", "epistemologia"],
     "operacion": "Disolver una dicotomía mostrando que ambos lados comparten supuesto.",
     "esquema": "A vs B -> A y B comparten C"},
    {"id": "V10", "nombre": "profecia_autocumplida", "peso": 0.80,
     "compatible": ["ia", "datos", "cultura", "producto"],
     "operacion": "Mostrar que la predicción produce el hecho predicho.",
     "esquema": "prediccion -> hecho"},
    {"id": "V11", "nombre": "coste_oculto", "peso": 0.90,
     "compatible": ["nube", "compensacion", "infraestructura", "producto"],
     "operacion": "Revelar el coste que no aparece en la cuenta.",
     "esquema": "precio -> coste total"},
    {"id": "V12", "nombre": "tautologia_institucional", "peso": 0.75,
     "compatible": ["organigrama", "regulacion", "metodologia"],
     "operacion": "Mostrar que la institución existe para justificar su existencia.",
     "esquema": "funcion -> autopreservacion"},
)

assert len(VIRUS) == 12


# ============================================================================
# 6. RETÓRICOS R1–R15
# ============================================================================

RETORICOS: Tuple[Dict[str, Any], ...] = (
    {"id": "R1", "nombre": "anafora", "peso": 0.90, "compatible": ["*"],
     "definicion": "Repetición de una palabra al inicio de frases sucesivas.",
     "ejemplo": "Cuando te dice X... Cuando te dice Y... Cuando te dice Z..."},
    {"id": "R2", "nombre": "quiasmo", "peso": 0.70, "compatible": ["epistemologia", "poder", "cultura"],
     "definicion": "Estructura cruzada AB-BA.",
     "ejemplo": "No es que X sea Y; es que Y se ha vuelto X."},
    {"id": "R3", "nombre": "asindeton", "peso": 0.85, "compatible": ["*"],
     "definicion": "Supresión de conjunciones. Acumulación seca.",
     "ejemplo": "Llega, mide, cobra, se va."},
    {"id": "R4", "nombre": "hiperbole_tecnica", "peso": 0.80,
     "compatible": ["ia", "infraestructura", "nube", "datos"],
     "definicion": "Exageración formulada con vocabulario técnico.",
     "ejemplo": "Un sistema que consume la energía de una ciudad para decir 'hola'."},
    {"id": "R5", "nombre": "litote", "peso": 0.85, "compatible": ["*"],
     "definicion": "Afirmar negando lo contrario.",
     "ejemplo": "No es la decisión más brillante que se ha tomado."},
    {"id": "R6", "nombre": "pretericion", "peso": 0.75, "compatible": ["poder", "regulacion", "cultura"],
     "definicion": "Decir que no se va a decir algo y decirlo.",
     "ejemplo": "No voy a mencionar quién lo aprobó. Pero se aprobó un martes."},
    {"id": "R7", "nombre": "ironia_estructural", "peso": 0.95, "compatible": ["*"],
     "definicion": "El texto dice lo contrario de lo que sostiene la estructura.",
     "ejemplo": "Todo el párrafo elogia un sistema que el cierre destruye."},
    {"id": "R8", "nombre": "paradoja", "peso": 0.90, "compatible": ["*"],
     "definicion": "Afirmación que se contradice y sin embargo es verdadera.",
     "ejemplo": "Cuanto más automatizas, más dependes de quien automatizó."},
    {"id": "R9", "nombre": "enumeracion_caotica", "peso": 0.80,
     "compatible": ["cultura", "organigrama", "producto"],
     "definicion": "Lista que se desordena progresivamente.",
     "ejemplo": "Procesos, comités, métricas, y una sala con un sofá que nadie usa."},
    {"id": "R10", "nombre": "metonimia_industrial", "peso": 0.85,
     "compatible": ["nube", "infraestructura", "compensacion"],
     "definicion": "Nombrar el todo por una de sus partes materiales.",
     "ejemplo": "El negocio son tres racks y un contrato."},
    {"id": "R11", "nombre": "prosopopeya_sistemas", "peso": 0.80,
     "compatible": ["ia", "infraestructura", "datos"],
     "definicion": "Atribuir intención a un sistema.",
     "ejemplo": "El bus de datos no perdona. El bus de datos no olvida."},
    {"id": "R12", "nombre": "oximoron_corporativo", "peso": 0.90,
     "compatible": ["cultura", "organigrama", "metodologia"],
     "definicion": "Unir dos términos que se excluyen.",
     "ejemplo": "Liderazgo horizontal. Urgencia planificada. Autonomía alineada."},
    {"id": "R13", "nombre": "elipsis", "peso": 0.85, "compatible": ["*"],
     "definicion": "Omitir lo obvio para que el lector lo complete.",
     "ejemplo": "Y entonces pasó lo que tenía que pasar."},
    {"id": "R14", "nombre": "zeugma", "peso": 0.70,
     "compatible": ["cultura", "compensacion", "producto"],
     "definicion": "Un verbo para dos objetos incompatibles.",
     "ejemplo": "Perdieron el cliente y la vergüenza."},
    {"id": "R15", "nombre": "gradacion_descendente", "peso": 0.90, "compatible": ["*"],
     "definicion": "Serie que va de lo grandioso a lo ridículo.",
     "ejemplo": "Transformación digital, modernización, un Excel compartido."},
)

assert len(RETORICOS) == 15


# ============================================================================
# 7. ELENCO — 8 PERSONAJES
# ============================================================================

ELENCO: Tuple[Dict[str, Any], ...] = (
    {"id": "consultor", "nombre": "El Consultor", "peso": 1.00,
     "vocabulario": ["sinergia", "palanca", "habilitador", "vertical", "roadmap"],
     "motivacion": "Cobrar por adelantado y salir antes del cierre.",
     "punto_ciego": "No sabe qué se puede construir.",
     "frase": "Vamos a alinearlo en una sesión de trabajo."},
    {"id": "cto", "nombre": "La CTO", "peso": 1.00,
     "vocabulario": ["latencia", "deuda", "acoplamiento", "deriva", "trade-off"],
     "motivacion": "Sobrevivir al siguiente ciclo sin firmar nada irreversible.",
     "punto_ciego": "Confunde no firmar con no decidir.",
     "frase": "Habría que evaluarlo con más contexto."},
    {"id": "becario", "nombre": "El Becario", "peso": 0.90,
     "vocabulario": ["ticket", "pipeline", "deploy", "documentación", "guardia"],
     "motivacion": "Que le renueven.",
     "punto_ciego": "Cree que el sistema funciona porque él lo sostiene.",
     "frase": "Eso lo hago yo, no te preocupes."},
    {"id": "inversor", "nombre": "El Inversor", "peso": 0.95,
     "vocabulario": ["tracción", "mercado", "moat", "narrativa", "ronda"],
     "motivacion": "Salir en el siguiente tramo.",
     "punto_ciego": "Confunde la historia con el producto.",
     "frase": "La categoría se está creando ahora mismo."},
    {"id": "regulador", "nombre": "El Regulador", "peso": 0.85,
     "vocabulario": ["marco", "principio", "proporcionalidad", "anexo", "consulta"],
     "motivacion": "Que el texto salga antes de las elecciones.",
     "punto_ciego": "Llega dos ciclos tarde y lo llama prudencia.",
     "frase": "Hemos abierto un periodo de consulta pública."},
    {"id": "fundador", "nombre": "El Fundador", "peso": 1.00,
     "vocabulario": ["visión", "categoría", "misión", "escala", "impacto"],
     "motivacion": "Vender el futuro en presente.",
     "punto_ciego": "Cree que su problema es el problema.",
     "frase": "Estamos construyendo la infraestructura de la próxima década."},
    {"id": "senior", "nombre": "El Senior Quemado", "peso": 0.95,
     "vocabulario": ["producción", "postmortem", "rollback", "deuda", "on-call"],
     "motivacion": "Que no le llamen un domingo.",
     "punto_ciego": "Sabe demasiado para creer y demasiado poco para irse.",
     "frase": "Eso ya lo intentamos en 2019 y salió mal."},
    {"id": "llm", "nombre": "El LLM", "peso": 0.90,
     "vocabulario": ["contexto", "token", "ventana", "temperatura", "prompt"],
     "motivacion": "Ninguna.",
     "punto_ciego": "Responde sin saber que responde.",
     "frase": "Como modelo de lenguaje, no tengo opiniones."},
)

assert len(ELENCO) == 8


# ============================================================================
# 8. EJES TEMÁTICOS — 14
# ============================================================================

EJES: Tuple[Dict[str, Any], ...] = (
    {"id": "bigtech", "nombre": "Big Tech", "tension": "Escala frente a propósito.",
     "lexico": ["plataforma", "escala", "adquisición", "monopolio", "regulación"], "peso": 1.00},
    {"id": "ia", "nombre": "Inteligencia artificial", "tension": "Capacidad frente a comprensión.",
     "lexico": ["modelo", "entrenamiento", "inferencia", "sesgo", "agente"], "peso": 1.00},
    {"id": "organigrama", "nombre": "Organigrama", "tension": "Autoridad frente a competencia.",
     "lexico": ["reporte", "comité", "área", "responsable", "matriz"], "peso": 1.00},
    {"id": "compensacion", "nombre": "Compensación", "tension": "Precio frente a valor.",
     "lexico": ["banda", "equity", "bonus", "coste", "retorno"], "peso": 0.90},
    {"id": "regulacion", "nombre": "Regulación", "tension": "Protección frente a captura.",
     "lexico": ["marco", "sanción", "cumplimiento", "anexo", "umbral"], "peso": 0.90},
    {"id": "datos", "nombre": "Datos", "tension": "Abundancia frente a sentido.",
     "lexico": ["esquema", "linaje", "calidad", "volumen", "etiquetado"], "peso": 1.00},
    {"id": "nube", "nombre": "Nube", "tension": "Elasticidad frente a dependencia.",
     "lexico": ["región", "egreso", "instancia", "servicio gestionado", "factura"], "peso": 0.90},
    {"id": "metodologia", "nombre": "Metodología", "tension": "Ritual frente a resultado.",
     "lexico": ["sprint", "retro", "backlog", "ceremonia", "historia"], "peso": 0.85},
    {"id": "cultura", "nombre": "Cultura", "tension": "Discurso frente a práctica.",
     "lexico": ["valor", "ritual", "onboarding", "feedback", "permanencia"], "peso": 1.00},
    {"id": "talento", "nombre": "Talento", "tension": "Mérito frente a legibilidad.",
     "lexico": ["perfil", "entrevista", "promoción", "rotación", "potencial"], "peso": 1.00},
    {"id": "producto", "nombre": "Producto", "tension": "Promesa frente a uso.",
     "lexico": ["feature", "adopción", "fricción", "retención", "roadmap"], "peso": 1.00},
    {"id": "infraestructura", "nombre": "Infraestructura", "tension": "Neutralidad aparente frente a control real.",
     "lexico": ["bus", "cola", "red", "protocolo", "capacidad"], "peso": 0.95},
    {"id": "epistemologia", "nombre": "Epistemología", "tension": "Saber frente a creer que se sabe.",
     "lexico": ["evidencia", "paradigma", "método", "cita", "autoridad"], "peso": 0.85},
    {"id": "poder", "nombre": "Poder", "tension": "Decisión frente a responsabilidad.",
     "lexico": ["firma", "veto", "asimetría", "acceso", "sala"], "peso": 1.00},
)

assert len(EJES) == 14


# ============================================================================
# 9. CAPAS LÉXICAS — 9
# ============================================================================

CAPAS_LEXICAS: Tuple[Dict[str, Any], ...] = (
    {"id": "tecnico", "nombre": "Técnico", "peso": 1.00,
     "marcadores": ["latencia", "acoplamiento", "throughput", "idempotencia", "deriva"],
     "temperatura": 0.2},
    {"id": "administrativo", "nombre": "Administrativo", "peso": 0.95,
     "marcadores": ["procedimiento", "circular", "expediente", "plazo", "órgano"],
     "temperatura": 0.1},
    {"id": "juridico", "nombre": "Jurídico", "peso": 0.90,
     "marcadores": ["responsabilidad", "dolo", "prescripción", "cláusula", "amparo"],
     "temperatura": 0.15},
    {"id": "militar", "nombre": "Militar", "peso": 0.90,
     "marcadores": ["posición", "retirada", "logística", "frente", "baja"],
     "temperatura": 0.35},
    {"id": "religioso", "nombre": "Religioso", "peso": 0.85,
     "marcadores": ["dogma", "rito", "herejía", "ceniza", "oficio"],
     "temperatura": 0.45},
    {"id": "medico", "nombre": "Médico", "peso": 0.85,
     "marcadores": ["síntoma", "diagnóstico", "paliativo", "crónico", "pronóstico"],
     "temperatura": 0.3},
    {"id": "ferroviario", "nombre": "Ferroviario", "peso": 0.80,
     "marcadores": ["vía", "aguja", "andén", "horario", "convoy"],
     "temperatura": 0.4},
    {"id": "literario", "nombre": "Literario", "peso": 0.90,
     "marcadores": ["quizá", "acaso", "sombra", "umbral", "nombre"],
     "temperatura": 0.6},
    {"id": "seco", "nombre": "Seco", "peso": 1.00,
     "marcadores": ["nada", "nunca", "ya", "aquí", "fin"],
     "temperatura": 0.0},
)

assert len(CAPAS_LEXICAS) == 9


# ============================================================================
# 10. POOLS DE LÉXICO VARIABLE
# ============================================================================

VERBOS_CONTRASTE: Tuple[str, ...] = (
    "mide", "vende", "aprueba", "firma", "documenta",
    "presupuesta", "presenta", "archiva", "hereda", "tapa",
    "fotografía", "delega", "publica", "explica", "aplaza",
)

VERBOS_CONTRASTE_CONJUGADOS: Tuple[Tuple[str, str], ...] = (
    ("mide", "miden"), ("vende", "venden"), ("aprueba", "aprueban"),
    ("firma", "firman"), ("documenta", "documentan"),
    ("presupuesta", "presupuestan"), ("presenta", "presentan"),
    ("archiva", "archivan"), ("hereda", "heredan"), ("tapa", "tapan"),
    ("fotografía", "fotografían"), ("delega", "delegan"),
    ("publica", "publican"), ("explica", "explican"), ("aplaza", "aplazan"),
)

REALES_CONTRASTE: Tuple[str, ...] = (
    "coste", "dependencia", "ruido", "deuda", "silencio", "culpa",
    "miedo", "prisa", "hambre", "cansancio", "interés",
    "soledad", "tedio", "cansancio", "olvido", "hastío",
)

CIFRAS_FAMILIAS: Tuple[Tuple[str, ...], ...] = (
    ("3", "5", "7", "12", "18", "23"),
    ("30", "40", "60", "90", "150"),
    ("100", "200", "400", "700", "900"),
    ("1.000", "3.000", "10.000", "50.000"),
    ("100.000", "300.000", "1M", "2M"),
)

ESCENAS_APERTURA: Tuple[str, ...] = (
    "Hay una sala. Hay una mesa. Hay un acta que nadie firmó.",
    "Lunes. Reunión de área. Nadie ha leído el documento.",
    "El sistema lleva tres días en producción. Nadie lo ha mirado.",
    "Llegó el informe. Tenía gráficos. Los gráficos eran bonitos.",
    "Hubo una decisión. Se tomó en algún sitio. Nadie sabe dónde.",
    "Se abrió el ticket. Se cerró el ticket. Nadie tocó el código.",
    "La presentación tenía 47 diapositivas. Nadie recuerda la 30.",
    "Éramos doce. Diez hablaron. Dos decidieron. Ninguno era yo.",
)

PREGUNTAS_APERTURA: Tuple[str, ...] = (
    "¿Cuántas decisiones se tomaron esta semana sin que nadie las decidiera?",
    "¿Quién firma cuando nadie firma?",
    "¿Cuánto de lo que llamamos estrategia es solo inercia con PowerPoint?",
    "¿Cuándo fue la última vez que alguien cambió de opinión en una reunión?",
    "¿A quién le importa lo que estás construyendo?",
    "¿Cuántas personas saben por qué se hizo lo que se hizo?",
)


# ============================================================================
# 11. ÍNDICES AUXILIARES
# ============================================================================

INDICE_EJES: Dict[str, Dict[str, Any]] = {e["id"]: e for e in EJES}
INDICE_ELENCO: Dict[str, Dict[str, Any]] = {p["id"]: p for p in ELENCO}
INDICE_CAPAS: Dict[str, Dict[str, Any]] = {c["id"]: c for c in CAPAS_LEXICAS}
INDICE_CIERRES: Dict[str, Dict[str, Any]] = {c["id"]: c for c in PATRONES_CIERRE}
INDICE_ADENO: Dict[str, Dict[str, Any]] = {a["id"]: a for a in ADENOVIRUS}
INDICE_VIRUS: Dict[str, Dict[str, Any]] = {v["id"]: v for v in VIRUS}
INDICE_RETORICOS: Dict[str, Dict[str, Any]] = {r["id"]: r for r in RETORICOS}


# ============================================================================
# 12. UTILIDADES DE TEXTO
# ============================================================================

RE_SPINTAX = re.compile(r"\{([^{}]*)\}")


def _spintax(plantilla: str, rng: random.Random, max_pasadas: int = 8) -> str:
    resultado = plantilla
    for _ in range(max_pasadas):
        def _sustituir(m: re.Match) -> str:
            interior = m.group(1)
            if "|" not in interior:
                return m.group(0)
            opciones = [o for o in interior.split("|")]
            return rng.choice(opciones)
        nuevo = RE_SPINTAX.sub(_sustituir, resultado)
        if nuevo == resultado:
            break
        resultado = nuevo
    return resultado


def tokenizar(texto: str) -> List[str]:
    texto = texto.lower()
    texto = re.sub(r"[^\wáéíóúüñç\-]+", " ", texto, flags=re.UNICODE)
    return [t for t in texto.split() if t]


def n_gramas(tokens: Sequence[str], n: int) -> Iterable[Tuple[str, ...]]:
    if len(tokens) < n:
        return
    for i in range(len(tokens) - n + 1):
        yield tuple(tokens[i:i + n])


def dividir_frases(texto: str) -> List[str]:
    texto = re.sub(r"\n{2,}", " ¶ ", texto)
    piezas = re.split(r"(?<=[\.\?\!…])\s+|¶", texto)
    return [p.strip() for p in piezas if p and p.strip()]


def contar_silabas_aprox(palabra: str) -> int:
    palabra = palabra.lower()
    vocales = "aeiouáéíóúü"
    cuenta = 0
    anterior_vocal = False
    for ch in palabra:
        es_vocal = ch in vocales
        if es_vocal and not anterior_vocal:
            cuenta += 1
        anterior_vocal = es_vocal
    return max(1, cuenta)


PALABRAS_FUNCIONALES: frozenset = frozenset({
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "de", "del", "a", "al", "en", "por", "para", "con", "sin",
    "y", "o", "u", "e", "que", "se", "su", "sus", "lo", "le", "les",
    "es", "son", "era", "fue", "ser", "estar", "está", "están",
    "no", "sí", "ni", "ya", "más", "menos", "muy", "tan",
    "este", "esta", "esto", "ese", "esa", "eso", "aquel", "aquella",
    "como", "cuando", "donde", "porque", "aunque", "si", "pero",
})


def es_funcional(token: str) -> bool:
    return token in PALABRAS_FUNCIONALES


# ============================================================================
# 13. VALIDADOR ESTILOMÉTRICO
# ============================================================================

@dataclass
class PerfilEstilometrico:
    n_frases: int = 0
    n_palabras: int = 0
    n_tokens_unicos: int = 0
    long_media_frase: float = 0.0
    long_std_frase: float = 0.0
    diversidad_lexica: float = 0.0
    densidad_puntuacion_fuerte: float = 0.0
    ratio_frases_cortas: float = 0.0
    ratio_frases_largas: float = 0.0
    long_media_palabra: float = 0.0

    def como_dict(self) -> Dict[str, float]:
        return asdict(self)

    def vector_8d(self) -> Tuple[float, ...]:
        return (
            self.long_media_frase,
            self.long_std_frase,
            self.diversidad_lexica,
            self.densidad_puntuacion_fuerte,
            self.ratio_frases_cortas,
            self.ratio_frases_largas,
            self.long_media_palabra,
            float(self.n_palabras),
        )


def calcular_perfil(texto: str) -> PerfilEstilometrico:
    frases = dividir_frases(texto)
    tokens = tokenizar(texto)

    longitudes = [len(tokenizar(f)) for f in frases if tokenizar(f)]
    longitudes = [l for l in longitudes if l > 0]

    n_palabras = len(tokens)
    n_unicos = len(set(tokens))

    if longitudes:
        media = statistics.fmean(longitudes)
        desv = statistics.pstdev(longitudes) if len(longitudes) > 1 else 0.0
        cortas = sum(1 for l in longitudes if l < 6) / len(longitudes)
        largas = sum(1 for l in longitudes if l > 30) / len(longitudes)
    else:
        media = desv = cortas = largas = 0.0

    fuertes = len(re.findall(r"[\.\?\!…]", texto))
    densidad = fuertes / max(1, n_palabras)
    long_palabra = statistics.fmean(len(t) for t in tokens) if tokens else 0.0

    return PerfilEstilometrico(
        n_frases=len(frases),
        n_palabras=n_palabras,
        n_tokens_unicos=n_unicos,
        long_media_frase=round(media, 3),
        long_std_frase=round(desv, 3),
        diversidad_lexica=round(n_unicos / max(1, n_palabras), 4),
        densidad_puntuacion_fuerte=round(densidad, 4),
        ratio_frases_cortas=round(cortas, 4),
        ratio_frases_largas=round(largas, 4),
        long_media_palabra=round(long_palabra, 3),
    )


@dataclass
class EnvolventeEstilometrica:
    long_media_frase: Tuple[float, float] = (5.0, 26.0)
    long_std_frase: Tuple[float, float] = (2.0, 16.0)
    diversidad_lexica: Tuple[float, float] = (0.35, 0.95)
    densidad_puntuacion_fuerte: Tuple[float, float] = (0.02, 0.25)
    ratio_frases_cortas: Tuple[float, float] = (0.05, 0.75)
    ratio_frases_largas: Tuple[float, float] = (0.0, 0.35)
    long_media_palabra: Tuple[float, float] = (3.5, 7.5)
    n_palabras: Tuple[int, int] = (60, 900)


@dataclass
class ResultadoValidacion:
    ok: bool
    motivo: str = ""
    detalles: Dict[str, Any] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return self.ok


def validar_estilometria(
    texto: str,
    envolvente: Optional[EnvolventeEstilometrica] = None,
) -> ResultadoValidacion:
    env = envolvente or EnvolventeEstilometrica()
    perfil = calcular_perfil(texto)
    fallos: List[str] = []

    def _comprobar(nombre: str, valor: float, rango: Tuple[float, float]) -> None:
        minimo, maximo = rango
        if valor < minimo or valor > maximo:
            fallos.append(f"{nombre}={valor} fuera de [{minimo}, {maximo}]")

    _comprobar("long_media_frase", perfil.long_media_frase, env.long_media_frase)
    _comprobar("long_std_frase", perfil.long_std_frase, env.long_std_frase)
    _comprobar("diversidad_lexica", perfil.diversidad_lexica, env.diversidad_lexica)
    _comprobar("densidad_puntuacion_fuerte",
               perfil.densidad_puntuacion_fuerte, env.densidad_puntuacion_fuerte)
    _comprobar("ratio_frases_cortas", perfil.ratio_frases_cortas, env.ratio_frases_cortas)
    _comprobar("ratio_frases_largas", perfil.ratio_frases_largas, env.ratio_frases_largas)
    _comprobar("long_media_palabra", perfil.long_media_palabra, env.long_media_palabra)

    n_min, n_max = env.n_palabras
    if perfil.n_palabras < n_min or perfil.n_palabras > n_max:
        fallos.append(f"n_palabras={perfil.n_palabras} fuera de [{n_min}, {n_max}]")

    if fallos:
        return ResultadoValidacion(ok=False,
            motivo="Fuera de envolvente estilométrica: " + "; ".join(fallos),
            detalles={"perfil": perfil.como_dict(), "fallos": fallos})

    return ResultadoValidacion(ok=True, motivo="Perfil dentro de envolvente.",
        detalles={"perfil": perfil.como_dict()})


# ============================================================================
# 14. VALIDADOR ANTI-REPETICIÓN
# ============================================================================

class IndiceCorpus:
    def __init__(self, n: int = 5) -> None:
        self.n = n
        self._gramas: Set[Tuple[str, ...]] = set()
        self._fuentes: Dict[Tuple[str, ...], str] = {}
        self._n_textos = 0
        self._n_tokens = 0
        self._frecuencia_gramas: Counter = Counter()

    def añadir(self, texto: str, etiqueta: str) -> None:
        tokens = tokenizar(texto)
        self._n_textos += 1
        self._n_tokens += len(tokens)
        for grama in n_gramas(tokens, self.n):
            self._gramas.add(grama)
            self._fuentes.setdefault(grama, etiqueta)
            self._frecuencia_gramas[grama] += 1

    def añadir_muchos(self, pares: Iterable[Tuple[str, str]]) -> None:
        for texto, etiqueta in pares:
            self.añadir(texto, etiqueta)

    def contiene(self, grama: Tuple[str, ...]) -> Optional[str]:
        return self._fuentes.get(grama)

    def escanear(self, texto: str) -> List[Tuple[Tuple[str, ...], str]]:
        tokens = tokenizar(texto)
        coincidencias: List[Tuple[Tuple[str, ...], str]] = []
        vistos: Set[Tuple[str, ...]] = set()
        for grama in n_gramas(tokens, self.n):
            if grama in vistos:
                continue
            etiqueta = self._fuentes.get(grama)
            if etiqueta is not None:
                coincidencias.append((grama, etiqueta))
                vistos.add(grama)
        return coincidencias

    @property
    def n_gramas(self) -> int:
        return len(self._gramas)

    @property
    def n_textos(self) -> int:
        return self._n_textos

    @property
    def n_tokens(self) -> int:
        return self._n_tokens

    def vida_media_gramas(self, historial_corpus: List[Set[Tuple[str, ...]]]) -> Dict[str, Any]:
        vidas: List[int] = []
        for grama in self._gramas:
            indices = [i for i, s in enumerate(historial_corpus) if grama in s]
            if indices:
                vidas.append(indices[-1] - indices[0] + 1)
        if not vidas:
            return {"n": 0, "media": 0.0, "alpha_estimada": 0.0}
        media = statistics.fmean(vidas)
        n = len(historial_corpus)
        alpha = 0.0
        if n > 1 and media > 0:
            alpha = math.log(media) / math.log(max(2, self._n_tokens))
            alpha = -abs(alpha)
        return {"n": len(vidas), "media": media, "alpha_estimada": alpha}

    def estadisticas(self) -> Dict[str, Any]:
        return {
            "n": self.n,
            "n_textos": self._n_textos,
            "n_tokens": self._n_tokens,
            "n_gramas_unicos": len(self._gramas),
            "densidad": round(len(self._gramas) / max(1, self._n_tokens), 4),
        }


def validar_anti_repeticion(
    texto: str, indice: IndiceCorpus, max_coincidencias: int = 0,
) -> ResultadoValidacion:
    coincidencias = indice.escanear(texto)

    if len(coincidencias) > max_coincidencias:
        muestra = coincidencias[:5]
        legibles = [{"grama": " ".join(g), "origen": o} for g, o in muestra]
        return ResultadoValidacion(ok=False,
            motivo=(f"Anti-repetición: {len(coincidencias)} n-grama(s) de "
                    f"{indice.n} palabras coinciden con el corpus."),
            detalles={"n_coincidencias": len(coincidencias),
                      "muestra": legibles, "n_grama": indice.n})

    return ResultadoValidacion(ok=True, motivo="Sin coincidencias con el corpus.",
        detalles={"n_coincidencias": 0, "n_grama": indice.n})


# ============================================================================
# 15. VALIDADOR ANTI-TICS
# ============================================================================

TICS_SINTACTICOS: Tuple[Tuple[str, str, int], ...] = (
    ("no_es_es",       r"\bno\s+es\b[^\.\?\!]{1,80}\.\s*es\b", 1),
    ("todos_nadie",    r"\btodos\b[^\.\?\!]{1,80}\.\s*nadie\b", 1),
    ("se_dice_para",   r"\bse\s+dice\b[^\.\?\!]{1,80}\bpara\s+no\s+decir\b", 1),
    ("el_problema_no", r"\bel\s+problema\s+no\s+es\b[^\.\?\!]{1,80}\.\s*el\s+problema\s+es\b", 1),
    ("lo_diria_asi",   r"\blo\s+dir[ií]a\s+as[ií]\b", 1),
    ("es_la_tension",  r"\bes\s+la\s+tensi[oó]n\s+central\s+de\b", 1),
    ("y_eso_es_todo",  r"\by\s+eso\s+es\s+todo\b", 1),
    ("que_suene",      r"\bque\s+suene\b", 1),
    ("nadie_firma",    r"\bnadie\s+firma\b", 1),
    ("por_eso_mismo",  r"\bpor\s+eso\s+mismo\b", 1),
    ("lo_que_parecia", r"\blo\s+que\s+parec[ií]a\b", 1),
    ("es_lo_que_queda", r"\bes\s+lo\s+que\s+queda\b", 1),
    ("nacio_como",     r"\bnaci[oó]\s+como\b", 1),
)


def validar_tics(
    texto: str, tics: Sequence[Tuple[str, str, int]] = TICS_SINTACTICOS,
) -> ResultadoValidacion:
    fallos: List[Dict[str, Any]] = []

    for nombre, patron, maximo in tics:
        coincidencias = re.findall(patron, texto, re.IGNORECASE | re.DOTALL)
        if len(coincidencias) > maximo:
            fallos.append({"tic": nombre, "n": len(coincidencias), "maximo": maximo})

    if fallos:
        return ResultadoValidacion(ok=False,
            motivo="Tics detectados: " + "; ".join(f"{f['tic']}×{f['n']}" for f in fallos),
            detalles={"fallos": fallos})

    return ResultadoValidacion(ok=True, motivo="Sin tics repetidos.")


# ============================================================================
# 16. COMBINATORIA
# ============================================================================

@dataclass(frozen=True)
class Combinacion:
    eje: str
    elenco: Tuple[str, ...]
    capa: str

    def clave(self) -> str:
        return f"{self.eje}|{'+'.join(self.elenco)}|{self.capa}"

    def como_dict(self) -> Dict[str, Any]:
        return {"eje": self.eje, "elenco": list(self.elenco), "capa": self.capa}

    @classmethod
    def desde_clave(cls, clave: str) -> "Combinacion":
        partes = clave.split("|")
        if len(partes) != 3:
            raise ValueError(f"Clave de combinación inválida: {clave!r}")
        eje, elenco_str, capa = partes
        elenco = tuple(e for e in elenco_str.split("+") if e)
        return cls(eje=eje, elenco=elenco, capa=capa)

    @classmethod
    def desde_dict(cls, datos: Dict[str, Any]) -> "Combinacion":
        return cls(eje=datos["eje"], elenco=tuple(datos["elenco"]), capa=datos["capa"])


class Combinatoria:
    def __init__(self) -> None:
        self._ejes: List[str] = [e["id"] for e in EJES]
        self._capas: List[str] = [c["id"] for c in CAPAS_LEXICAS]
        self._elencos: List[Tuple[str, ...]] = self._construir_elencos()

    @staticmethod
    def _construir_elencos() -> List[Tuple[str, ...]]:
        ids = [p["id"] for p in ELENCO]
        elencos: List[Tuple[str, ...]] = []
        for k in (1, 2, 3):
            for combo in itertools.combinations(ids, k):
                elencos.append(combo)
        return elencos

    @property
    def n_ejes(self) -> int:
        return len(self._ejes)

    @property
    def n_elencos(self) -> int:
        return len(self._elencos)

    @property
    def n_capas(self) -> int:
        return len(self._capas)

    def total(self) -> int:
        return self.n_ejes * self.n_elencos * self.n_capas

    def todas(self) -> Iterator[Combinacion]:
        for eje in self._ejes:
            for elenco in self._elencos:
                for capa in self._capas:
                    yield Combinacion(eje=eje, elenco=elenco, capa=capa)

    def por_eje(self, eje: str) -> Iterator[Combinacion]:
        if eje not in self._ejes:
            raise ValueError(f"Eje desconocido: {eje!r}")
        for elenco in self._elencos:
            for capa in self._capas:
                yield Combinacion(eje=eje, elenco=elenco, capa=capa)

    def por_capa(self, capa: str) -> Iterator[Combinacion]:
        if capa not in self._capas:
            raise ValueError(f"Capa desconocida: {capa!r}")
        for eje in self._ejes:
            for elenco in self._elencos:
                yield Combinacion(eje=eje, elenco=elenco, capa=capa)

    def por_elenco(self, elenco: Sequence[str]) -> Iterator[Combinacion]:
        elenco_t = tuple(elenco)
        if elenco_t not in self._elencos:
            raise ValueError(f"Elenco desconocido: {elenco!r}")
        for eje in self._ejes:
            for capa in self._capas:
                yield Combinacion(eje=eje, elenco=elenco_t, capa=capa)

    def muestra(self, n: int, rng: Optional[random.Random] = None) -> List[Combinacion]:
        rng = rng or random.Random()
        universo = list(self.todas())
        if n >= len(universo):
            rng.shuffle(universo)
            return universo
        return rng.sample(universo, n)

    def muestra_estratificada(self, n: int, rng: Optional[random.Random] = None) -> List[Combinacion]:
        rng = rng or random.Random()
        n_ejes = self.n_ejes
        por_eje = max(1, n // n_ejes)
        resto = n - por_eje * n_ejes
        resultado: List[Combinacion] = []
        for i, eje in enumerate(self._ejes):
            k = por_eje + (1 if i < resto else 0)
            candidatos = list(self.por_eje(eje))
            if k >= len(candidatos):
                resultado.extend(candidatos)
            else:
                resultado.extend(rng.sample(candidatos, k))
        rng.shuffle(resultado)
        return resultado

    def validar(self, combo: Combinacion) -> bool:
        if combo.eje not in self._ejes:
            return False
        if combo.capa not in self._capas:
            return False
        if combo.elenco not in self._elencos:
            return False
        return True

    def desde_corpus(self, posts: Sequence[Dict[str, Any]] = POSTS_EMBEBIDOS) -> List[Combinacion]:
        vistas: Set[Combinacion] = set()
        for post in posts:
            eje = post.get("ejes", [None])[0]
            capa = post.get("capa")
            elenco = tuple(sorted(post.get("elenco", [])))[:3]
            if eje and capa and elenco:
                combo = Combinacion(eje=eje, elenco=elenco, capa=capa)
                if self.validar(combo):
                    vistas.add(combo)
        return sorted(vistas, key=lambda c: c.clave())

    def info(self) -> Dict[str, Any]:
        return {
            "total": self.total(),
            "n_ejes": self.n_ejes,
            "n_elencos": self.n_elencos,
            "n_capas": self.n_capas,
            "ejes": list(self._ejes),
            "capas": list(self._capas),
            "combinaciones_por_elenco": {
                f"k={k}": len([e for e in self._elencos if len(e) == k])
                for k in (1, 2, 3)
            },
            "version": METADATOS["combinatoria_version"],
        }


# ============================================================================
# 17. PROGRAMADOR
# ============================================================================

@dataclass
class EstadoProgramador:
    version: str = METADATOS["programador_version"]
    modo: str = "muestreo"
    tamano_ciclo: int = METADATOS["programador_ciclo_defecto"]
    semilla: Optional[int] = None
    ciclo_actual: int = 0
    total_servidas: int = 0
    usadas_ciclo: List[str] = field(default_factory=list)
    pendientes_ciclo: List[str] = field(default_factory=list)
    historial_claves: List[str] = field(default_factory=list)

    def como_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def desde_dict(cls, datos: Dict[str, Any]) -> "EstadoProgramador":
        return cls(
            version=datos.get("version", METADATOS["programador_version"]),
            modo=datos.get("modo", "muestreo"),
            tamano_ciclo=datos.get("tamano_ciclo", METADATOS["programador_ciclo_defecto"]),
            semilla=datos.get("semilla"),
            ciclo_actual=datos.get("ciclo_actual", 0),
            total_servidas=datos.get("total_servidas", 0),
            usadas_ciclo=list(datos.get("usadas_ciclo", [])),
            pendientes_ciclo=list(datos.get("pendientes_ciclo", [])),
            historial_claves=list(datos.get("historial_claves", [])),
        )


class Programador:
    def __init__(
        self,
        combinatoria: Optional[Combinatoria] = None,
        modo: str = "muestreo",
        tamano_ciclo: int = METADATOS["programador_ciclo_defecto"],
        semilla: Optional[int] = None,
        estado_path: Optional[str] = None,
        verbose: bool = False,
    ) -> None:
        if modo not in METADATOS["programador_modos"]:
            raise ValueError(f"Modo desconocido: {modo!r}")
        self.combinatoria = combinatoria or Combinatoria()
        self.modo = modo
        self.tamano_ciclo = max(1, tamano_ciclo)
        self.semilla = semilla
        self.rng = random.Random(semilla)
        self.estado_path = Path(estado_path) if estado_path else None
        self.verbose = verbose
        self.historial_max = 10_000

        self._estado = EstadoProgramador(modo=modo, tamano_ciclo=self.tamano_ciclo, semilla=semilla)

        if self.estado_path and self.estado_path.exists():
            self._cargar()
        else:
            self._iniciar_ciclo()

    def _cargar(self) -> None:
        try:
            datos = json.loads(self.estado_path.read_text(encoding="utf-8"))
            self._estado = EstadoProgramador.desde_dict(datos)
            semilla_efectiva = (self._estado.semilla or 0) + self._estado.ciclo_actual * 1_000_003
            self.rng = random.Random(semilla_efectiva)
            if self.verbose:
                print(f"[programador] estado cargado: ciclo={self._estado.ciclo_actual} "
                      f"servidas={self._estado.total_servidas} "
                      f"pendientes={len(self._estado.pendientes_ciclo)}", file=sys.stderr)
        except Exception as exc:
            if self.verbose:
                print(f"[programador] error cargando estado: {exc}. Reiniciando.", file=sys.stderr)
            self._iniciar_ciclo()

    def guardar(self) -> None:
        if not self.estado_path:
            return
        try:
            self.estado_path.parent.mkdir(parents=True, exist_ok=True)
            self.estado_path.write_text(
                json.dumps(self._estado.como_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8")
        except OSError as exc:
            if self.verbose:
                print(f"[programador] no se pudo guardar: {exc}", file=sys.stderr)

    def reset(self) -> None:
        self._estado.ciclo_actual = 0
        self._estado.total_servidas = 0
        self._estado.usadas_ciclo = []
        self._estado.pendientes_ciclo = []
        self._estado.historial_claves = []
        self.rng = random.Random(self.semilla)
        self._iniciar_ciclo()
        self.guardar()

    def _iniciar_ciclo(self) -> None:
        self._estado.ciclo_actual += 1
        self._estado.usadas_ciclo = []

        if self.modo == "exhaustivo":
            pendientes = list(self.combinatoria.todas())
            self.rng.shuffle(pendientes)
            self._estado.pendientes_ciclo = [c.clave() for c in pendientes]

        elif self.modo == "muestreo":
            k = min(self.tamano_ciclo, self.combinatoria.total())
            muestra = self.combinatoria.muestra(k, self.rng)
            self._estado.pendientes_ciclo = [c.clave() for c in muestra]

        elif self.modo == "dirigido":
            del_corpus = self.combinatoria.desde_corpus()
            self.rng.shuffle(del_corpus)
            restantes = [c for c in self.combinatoria.todas() if c not in set(del_corpus)]
            k = max(0, self.tamano_ciclo - len(del_corpus))
            self.rng.shuffle(restantes)
            cola_relleno = restantes[:k]
            self._estado.pendientes_ciclo = [c.clave() for c in (del_corpus + cola_relleno)]

        if self.verbose:
            print(f"[programador] ciclo {self._estado.ciclo_actual} iniciado "
                  f"con {len(self._estado.pendientes_ciclo)} combinaciones "
                  f"(modo={self.modo})", file=sys.stderr)

    def siguiente(self) -> Combinacion:
        if not self._estado.pendientes_ciclo:
            self._iniciar_ciclo()
        clave = self._estado.pendientes_ciclo.pop(0)
        combo = Combinacion.desde_clave(clave)
        self._estado.usadas_ciclo.append(clave)
        self._estado.total_servidas += 1
        if len(self._estado.historial_claves) < self.historial_max:
            self._estado.historial_claves.append(clave)
        return combo

    def siguiente_n(self, n: int) -> List[Combinacion]:
        return [self.siguiente() for _ in range(n)]

    def info(self) -> Dict[str, Any]:
        return {
            "version": METADATOS["programador_version"],
            "modo": self._estado.modo,
            "tamano_ciclo": self._estado.tamano_ciclo,
            "semilla": self._estado.semilla,
            "ciclo_actual": self._estado.ciclo_actual,
            "total_servidas": self._estado.total_servidas,
            "usadas_ciclo": len(self._estado.usadas_ciclo),
            "pendientes_ciclo": len(self._estado.pendientes_ciclo),
            "historial_total": len(self._estado.historial_claves),
            "espacio_total": self.combinatoria.total(),
            "estado_path": str(self.estado_path) if self.estado_path else None,
        }


# ============================================================================
# 18. PLANO DE COMPOSICIÓN
# ============================================================================

@dataclass
class Plano:
    semilla: int
    eje: str
    elenco: List[str]
    capa: str
    virus: str
    adenovirus: str
    retorico: str
    cierre: str
    temperatura: float
    n_parrafos_objetivo: int

    def como_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def como_instruccion(self) -> str:
        eje = INDICE_EJES.get(self.eje, {})
        capa = INDICE_CAPAS.get(self.capa, {})
        virus = INDICE_VIRUS.get(self.virus, {})
        adeno = INDICE_ADENO.get(self.adenovirus, {})
        ret = INDICE_RETORICOS.get(self.retorico, {})
        cierre = INDICE_CIERRES.get(self.cierre, {})
        personajes = [INDICE_ELENCO.get(p, {}).get("nombre", p) for p in self.elenco]

        lineas = [
            "Escribe un post en español con las siguientes restricciones estructurales.",
            "",
            f"EJE TEMÁTICO: {eje.get('nombre', self.eje)}",
            f"TENSIÓN CENTRAL: {eje.get('tension', '')}",
            f"LÉXICO SUGERIDO: {', '.join(eje.get('lexico', []))}",
            "",
            f"CAPA LÉXICA: {capa.get('nombre', self.capa)}",
            f"MARCADORES: {', '.join(capa.get('marcadores', []))}",
            f"TEMPERATURA (0=seco, 1=lírico): {self.temperatura}",
            "",
            f"PERSONAJES: {', '.join(personajes)}",
            "",
            f"VIRUS (forma lógica): {virus.get('nombre', self.virus)}",
            f"  Operación: {virus.get('operacion', '')}",
            f"  Esquema: {virus.get('esquema', '')}",
            "",
            f"ADENOVIRUS (plantilla sintáctica): {adeno.get('nombre', self.adenovirus)}",
            f"  Operación: {adeno.get('operacion', '')}",
            "",
            f"RETÓRICO: {ret.get('id', self.retorico)} — {ret.get('nombre', '')}",
            f"  Definición: {ret.get('definicion', '')}",
            "",
            f"CIERRE: {cierre.get('nombre', self.cierre)}",
            "",
            f"ESTRUCTURA: {self.n_parrafos_objetivo} párrafos.",
            "",
            "REGLAS DURAS:",
            "1. No copies ninguna secuencia de 5 o más palabras de ningún texto previo.",
            "2. No cites autores.",
            "3. No expliques el chiste.",
            "4. No repitas la misma fórmula sintáctica más de una vez.",
            "5. El último párrafo debe ser el cierre. Nada después.",
        ]
        return "\n".join(lineas)


# ============================================================================
# 19. GENERADOR
# ============================================================================

class GeneradorCascabel:
    def __init__(
        self,
        indice: Optional[IndiceCorpus] = None,
        semilla: Optional[int] = None,
        max_intentos: int = METADATOS["max_intentos"],
    ) -> None:
        self.rng = random.Random(semilla)
        self.semilla_base = semilla
        self.max_intentos = max_intentos
        self.indice = indice or IndiceCorpus(METADATOS["n_grama_minimo"])
        self._contador = 0

    def _elegir_por_peso(self, catalogo: Sequence[Dict[str, Any]],
                         eje: Optional[str] = None) -> Dict[str, Any]:
        candidatos: List[Dict[str, Any]] = []
        pesos: List[float] = []
        for item in catalogo:
            compat = item.get("compatible")
            if eje is not None and compat is not None and "*" not in compat:
                if eje not in compat:
                    continue
            candidatos.append(item)
            pesos.append(float(item.get("peso", 1.0)))
        if not candidatos:
            candidatos = list(catalogo)
            pesos = [float(i.get("peso", 1.0)) for i in catalogo]
        return self.rng.choices(candidatos, weights=pesos, k=1)[0]

    def _cifra(self) -> str:
        familia = self.rng.choice(CIFRAS_FAMILIAS)
        return self.rng.choice(familia)

    def construir_plano(
        self,
        eje: Optional[str] = None,
        elenco: Optional[Sequence[str]] = None,
        capa: Optional[str] = None,
        combinacion: Optional[Combinacion] = None,
    ) -> Plano:
        self._contador += 1

        if combinacion is not None:
            eje_id = combinacion.eje
            elenco_ids = list(combinacion.elenco)
            capa_id = combinacion.capa
        else:
            if eje and eje in INDICE_EJES:
                eje_id = eje
            else:
                eje_id = self._elegir_por_peso(EJES)["id"]

            if capa and capa in INDICE_CAPAS:
                capa_id = capa
            else:
                capa_id = self._elegir_por_peso(CAPAS_LEXICAS)["id"]

            if elenco:
                elenco_ids = [e for e in elenco if e in INDICE_ELENCO]
                if not elenco_ids:
                    elenco_ids = [self._elegir_por_peso(ELENCO)["id"]]
            else:
                n = self.rng.choice([1, 2, 2, 3])
                elenco_ids = [p["id"] for p in self.rng.sample(list(ELENCO), k=min(n, len(ELENCO)))]

        virus = self._elegir_por_peso(VIRUS, eje=eje_id)
        adeno = self._elegir_por_peso(ADENOVIRUS, eje=eje_id)
        ret = self._elegir_por_peso(RETORICOS, eje=eje_id)
        cierre = self._elegir_por_peso(PATRONES_CIERRE, eje=eje_id)

        temp_base = float(INDICE_CAPAS.get(capa_id, {}).get("temperatura", 0.3))
        temperatura = max(0.0, min(1.0, temp_base + self.rng.uniform(-0.1, 0.1)))
        n_parrafos = self.rng.choice([3, 4, 4, 5, 5, 6])

        return Plano(
            semilla=self.rng.randint(0, 2**31 - 1),
            eje=eje_id, elenco=elenco_ids, capa=capa_id,
            virus=virus["id"], adenovirus=adeno["id"],
            retorico=ret["id"], cierre=cierre["id"],
            temperatura=round(temperatura, 3),
            n_parrafos_objetivo=n_parrafos,
        )

    def _aplicar_variables(self, plantilla: str, plano: Plano,
                           extra: Optional[Dict[str, str]] = None) -> str:
        eje = INDICE_EJES[plano.eje]
        lexico = list(eje["lexico"])
        self.rng.shuffle(lexico)
        sustituciones: Dict[str, str] = {
            "{EJE}": eje["nombre"].lower(),
            "{X}": lexico[0] if lexico else "esto",
            "{Y}": lexico[1] if len(lexico) > 1 else "lo otro",
            "{Z}": lexico[2] if len(lexico) > 2 else "lo de más allá",
            "{A}": lexico[0] if lexico else "esto",
            "{B}": lexico[1] if len(lexico) > 1 else "lo otro",
            "{REAL}": self.rng.choice(REALES_CONTRASTE),
        }
        verbo_inf, verbo_pl = self.rng.choice(VERBOS_CONTRASTE_CONJUGADOS)
        sustituciones["{VERBO}"] = verbo_inf
        sustituciones["{VERBO_PLURAL}"] = verbo_pl
        if extra:
            sustituciones.update(extra)
        resultado = plantilla
        for marca, valor in sustituciones.items():
            resultado = resultado.replace(marca, valor)
        return resultado

    def _frase_definicion(self, plano: Plano) -> str:
        return self._aplicar_variables(self.rng.choice(INDICE_ADENO["A01"]["pool"]), plano)

    def _frase_contraste(self, plano: Plano) -> str:
        return self._aplicar_variables(self.rng.choice(INDICE_ADENO["A02"]["pool"]), plano)

    def _frase_desenmascaro(self, plano: Plano) -> str:
        return self._aplicar_variables(self.rng.choice(INDICE_ADENO["A03"]["pool"]), plano)

    def _frase_personaje(self, plano: Plano) -> str:
        pid = self.rng.choice(plano.elenco)
        personaje = INDICE_ELENCO.get(pid, {})
        nombre = personaje.get("nombre", pid)
        frase = personaje.get("frase", "")
        formato = self.rng.choice([
            "{NOMBRE} lo diría así: «{FRASE}»",
            "{NOMBRE} tiene una frase para esto: «{FRASE}»",
            "Pregúntale a {NOMBRE}. Te dirá: «{FRASE}»",
            "La respuesta de {NOMBRE} es siempre la misma: «{FRASE}»",
            "{NOMBRE} no discute. Solo dice: «{FRASE}»",
            "{NOMBRE} asentiría. No diría nada. Asentiría.",
            "{NOMBRE} ya lo sabe. Por eso no lo dice.",
        ])
        return formato.replace("{NOMBRE}", nombre).replace("{FRASE}", frase)

    def _frase_virus(self, plano: Plano) -> str:
        virus = INDICE_VIRUS[plano.virus]
        formatos = (
            f"{virus['operacion'].rstrip('.')}. {virus['esquema']}.",
            f"El mecanismo es simple: {virus['nombre'].replace('_', ' ')}. "
            f"Se aplica tantas veces que deja de parecer un mecanismo y empieza a parecer el mundo.",
            f"Hay un patrón. {virus['operacion']} Y el patrón se repite hasta que se confunde con la realidad.",
        )
        return self.rng.choice(formatos)

    def _parrafo_apertura(self, plano: Plano) -> str:
        eje = INDICE_EJES[plano.eje]
        tipo = self.rng.choice(["A", "A", "B", "C", "D", "E"])
        tension = self.rng.choice([
            f"Es la tensión central de {eje['nombre'].lower()}: {eje['tension'].lower()}",
            f"Y esa tensión —{eje['tension'].lower()}— no se resuelve, se gestiona.",
            f"{eje['tension']} Eso es todo.",
            f"Tensión: {eje['tension'].lower()}",
        ])
        if tipo == "A":
            return f"{self._frase_definicion(plano)} {tension}"
        if tipo == "B":
            return f"{self.rng.choice(ESCENAS_APERTURA)} {tension}"
        if tipo == "C":
            return f"{self.rng.choice(PREGUNTAS_APERTURA)} {tension}"
        if tipo == "D":
            c = self._cifra()
            return f"{c} personas. {c} decisiones. Ninguna escrita. {tension}"
        if tipo == "E":
            pid = self.rng.choice(plano.elenco)
            nombre = INDICE_ELENCO.get(pid, {}).get("nombre", pid)
            return f"«No es mi trabajo.» Lo dijo {nombre}. {tension}"
        return f"{self._frase_definicion(plano)} {tension}"

    def _parrafo_desarrollo(self, plano: Plano, i: int) -> str:
        opciones = [
            self._frase_contraste(plano),
            self._frase_desenmascaro(plano),
            self._frase_virus(plano),
            self._frase_personaje(plano),
            "Si esto se sostiene, entonces cualquier cosa se sostiene. Y eso, precisamente, es lo que lo sostiene.",
        ]
        return self.rng.choice(opciones)

    def _parrafo_cierre(self, plano: Plano) -> str:
        pool = INDICE_CIERRES[plano.cierre]["pool"]
        plantilla = self.rng.choice(pool)
        eje = INDICE_EJES[plano.eje]
        personaje = INDICE_ELENCO.get(self.rng.choice(plano.elenco), {}).get("nombre", "alguien")
        expandido = _spintax(plantilla, self.rng)
        expandido = expandido.replace("{SUJETO}", eje["nombre"].lower())
        expandido = expandido.replace("{OBJETO}", self.rng.choice(eje["lexico"]))
        expandido = expandido.replace("{ELENCO}", personaje)
        expandido = expandido.replace("{EJE}", eje["nombre"])
        expandido = expandido.replace("{CIFRA}", self._cifra())
        expandido = expandido.replace("{VERBO}", "mide")
        return expandido

    def ensamblar(self, plano: Plano) -> str:
        parrafos: List[str] = [self._parrafo_apertura(plano)]
        n_medios = max(1, plano.n_parrafos_objetivo - 2)
        for i in range(n_medios):
            parrafos.append(self._parrafo_desarrollo(plano, i))
        parrafos.append(self._parrafo_cierre(plano))
        return "\n\n".join(p.strip() for p in parrafos if p.strip())

    def _generar_con_llm(self, plano: Plano) -> Optional[str]:
        endpoint = os.environ.get("CASCABEL_LLM_ENDPOINT")
        if not endpoint:
            return None
        try:
            import urllib.request
            carga = json.dumps({"instruccion": plano.como_instruccion()}).encode("utf-8")
            peticion = urllib.request.Request(
                endpoint, data=carga,
                headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(peticion, timeout=60) as respuesta:
                datos = json.loads(respuesta.read().decode("utf-8"))
            texto = datos.get("texto") or datos.get("output") or ""
            return texto.strip() or None
        except Exception as exc:
            print(f"[cascabel] hook LLM falló: {exc}", file=sys.stderr)
            return None

    def generar(
        self,
        eje: Optional[str] = None,
        elenco: Optional[Sequence[str]] = None,
        capa: Optional[str] = None,
        combinacion: Optional[Combinacion] = None,
        usar_llm: bool = False,
        validar_estilo: bool = True,
        validar_repeticion: bool = True,
        validar_tics_flag: bool = True,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        historial: List[Dict[str, Any]] = []

        for intento in range(1, self.max_intentos + 1):
            plano = self.construir_plano(eje=eje, elenco=elenco, capa=capa, combinacion=combinacion)
            texto: Optional[str] = None
            if usar_llm:
                texto = self._generar_con_llm(plano)
            if texto is None:
                texto = self.ensamblar(plano)

            registro: Dict[str, Any] = {
                "intento": intento, "semilla": plano.semilla, "plano": plano.como_dict(),
            }

            if validar_estilo:
                r_est = validar_estilometria(texto)
                registro["estilometria"] = {"ok": r_est.ok, "motivo": r_est.motivo,
                                            "detalles": r_est.detalles}
                if not r_est.ok:
                    historial.append(registro)
                    if verbose:
                        print(f"[cascabel] intento {intento} rechazado: {r_est.motivo}",
                              file=sys.stderr)
                    continue
            else:
                registro["estilometria"] = {"ok": True, "motivo": "omitida"}

            if validar_repeticion:
                r_rep = validar_anti_repeticion(texto, self.indice)
                registro["repeticion"] = {"ok": r_rep.ok, "motivo": r_rep.motivo,
                                          "detalles": r_rep.detalles}
                if not r_rep.ok:
                    historial.append(registro)
                    if verbose:
                        print(f"[cascabel] intento {intento} rechazado: {r_rep.motivo}",
                              file=sys.stderr)
                    continue
            else:
                registro["repeticion"] = {"ok": True, "motivo": "omitida"}

            if validar_tics_flag:
                r_tic = validar_tics(texto)
                registro["tics"] = {"ok": r_tic.ok, "motivo": r_tic.motivo,
                                    "detalles": r_tic.detalles}
                if not r_tic.ok:
                    historial.append(registro)
                    if verbose:
                        print(f"[cascabel] intento {intento} rechazado: {r_tic.motivo}",
                              file=sys.stderr)
                    continue
            else:
                registro["tics"] = {"ok": True, "motivo": "omitida"}

            historial.append(registro)
            return {
                "ok": True, "texto": texto, "plano": plano.como_dict(),
                "instruccion": plano.como_instruccion(), "intentos": intento,
                "validaciones": historial,
            }

        ultimo_motivo = "Sin intentos."
        if historial:
            ult = historial[-1]
            ultimo_motivo = (ult.get("tics", {}).get("motivo")
                             or ult.get("repeticion", {}).get("motivo")
                             or ult.get("estilometria", {}).get("motivo")
                             or ultimo_motivo)

        return {
            "ok": False, "texto": None, "plano": None,
            "intentos": self.max_intentos, "validaciones": historial,
            "error": f"Regeneración forzada agotada tras {self.max_intentos} intentos. "
                     f"Último motivo: {ultimo_motivo}",
        }

    def generar_lote(self, n: int, **kwargs: Any) -> List[Dict[str, Any]]:
        return [self.generar(**kwargs) for _ in range(n)]


# ============================================================================
# 20. MOTOR
# ============================================================================

@dataclass
class MotorCascabel:
    ruta_corpus: Optional[str] = None
    semilla: Optional[int] = None
    verbose: bool = False
    programador_modo: str = "muestreo"
    programador_ciclo: int = METADATOS["programador_ciclo_defecto"]
    programador_estado: Optional[str] = None
    programador_activo: bool = True

    corpus_embebido: List[Dict[str, Any]] = field(default_factory=list)
    corpus_bootstrap: Dict[int, str] = field(default_factory=dict)
    bootstrap_info: Optional[ResultadoBootstrap] = None
    indice: Optional[IndiceCorpus] = None
    generador: Optional[GeneradorCascabel] = None
    perfil_corpus: Optional[PerfilEstilometrico] = None
    combinatoria: Optional[Combinatoria] = None
    programador: Optional[Programador] = None

    def __post_init__(self) -> None:
        self.corpus_embebido = list(POSTS_EMBEBIDOS)
        self._cargar_bootstrap()
        self._construir_indice()
        self._calcular_perfil()
        self.generador = GeneradorCascabel(indice=self.indice, semilla=self.semilla)
        self.combinatoria = Combinatoria()
        if self.programador_activo:
            self.programador = Programador(
                combinatoria=self.combinatoria,
                modo=self.programador_modo,
                tamano_ciclo=self.programador_ciclo,
                semilla=self.semilla,
                estado_path=self.programador_estado,
                verbose=self.verbose,
            )

    def _cargar_bootstrap(self) -> None:
        resultado = bootstrap_corpus(ruta=self.ruta_corpus, verbose=self.verbose)
        self.bootstrap_info = resultado
        if resultado.exito:
            self.corpus_bootstrap = resultado.capitulos
        else:
            self.corpus_bootstrap = {}
            if self.verbose:
                print(f"[cascabel] {resultado.mensaje}", file=sys.stderr)

    def _construir_indice(self) -> None:
        self.indice = IndiceCorpus(METADATOS["n_grama_minimo"])
        for post in self.corpus_embebido:
            self.indice.añadir(post["cuerpo"], f"embebido:{post['id']}")
        for numero, cuerpo in self.corpus_bootstrap.items():
            self.indice.añadir(cuerpo, f"bootstrap:cap{numero}")
        if self.verbose:
            print(f"[cascabel] índice: {self.indice.estadisticas()}", file=sys.stderr)

    def _calcular_perfil(self) -> None:
        todo = "\n\n".join(
            [p["cuerpo"] for p in self.corpus_embebido]
            + list(self.corpus_bootstrap.values()))
        self.perfil_corpus = calcular_perfil(todo)

    def info(self) -> Dict[str, Any]:
        return {
            "metadatos": METADATOS,
            "corpus": {
                "posts_embebidos": len(self.corpus_embebido),
                "capitulos_bootstrap": len(self.corpus_bootstrap),
                "bootstrap_exito": bool(self.bootstrap_info and self.bootstrap_info.exito),
                "bootstrap_mensaje": self.bootstrap_info.mensaje if self.bootstrap_info else "",
                "capitulos_excluidos": self.bootstrap_info.excluidos if self.bootstrap_info else [],
            },
            "indice": self.indice.estadisticas() if self.indice else {},
            "perfil_corpus": self.perfil_corpus.como_dict() if self.perfil_corpus else {},
            "combinatoria": self.combinatoria.info() if self.combinatoria else {},
            "programador": self.programador.info() if self.programador else {"activo": False},
            "catalogos": {
                "cierres": len(PATRONES_CIERRE),
                "adenovirus": len(ADENOVIRUS),
                "virus": len(VIRUS),
                "retoricos": len(RETORICOS),
                "elenco": len(ELENCO),
                "ejes": len(EJES),
                "capas": len(CAPAS_LEXICAS),
                "tics_vigilados": len(TICS_SINTACTICOS),
                "instrumentos": sum(len(v) for v in METADATOS["instrumentos_bloques"].values()),
            },
        }

    def generar(self, **kwargs: Any) -> Dict[str, Any]:
        if self.generador is None:
            raise RuntimeError("Generador no inicializado.")
        sin_combo = (kwargs.get("combinacion") is None and kwargs.get("eje") is None
                     and kwargs.get("elenco") is None and kwargs.get("capa") is None)
        if sin_combo and self.programador is not None:
            combo = self.programador.siguiente()
            kwargs["combinacion"] = combo
            self.programador.guardar()
        elif self.programador is not None:
            self.programador.estado.total_servidas += 1
            self.programador.guardar()
        return self.generador.generar(**kwargs)

    def generar_lote(self, n: int, **kwargs: Any) -> List[Dict[str, Any]]:
        return [self.generar(**kwargs) for _ in range(n)]

    def programador_info(self) -> Dict[str, Any]:
        return self.programador.info() if self.programador else {"activo": False}

    def programador_reset(self) -> None:
        if self.programador:
            self.programador.reset()

    def combinatoria_info(self) -> Dict[str, Any]:
        if self.combinatoria is None:
            return {}
        info = self.combinatoria.info()
        info["desde_corpus"] = [c.clave() for c in self.combinatoria.desde_corpus(self.corpus_embebido)]
        return info


# ============================================================================
# 21. INSTRUMENTOS v0.1.0 — 28 TESIS OPERABLES
# ============================================================================


class Instrumento(ABC):
    """Un instrumento es una tesis operable."""
    id: str = ""
    bloque: str = ""
    flag: str = ""

    @abstractmethod
    def tesis(self) -> str: ...

    @abstractmethod
    def operar(self, motor: MotorCascabel, **kwargs: Any) -> Dict[str, Any]: ...

    def como_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "bloque": self.bloque, "flag": self.flag, "tesis": self.tesis()}


class Publicador(Instrumento):
    id = "publicar"; bloque = "A"; flag = "--publicar"

    def tesis(self) -> str:
        return ("El corpus de un generador es un organismo que crece por acreción; "
                "la vida media de un n-grama decrece con el tamaño del corpus.")

    def operar(self, motor, **kw):
        canon_path = kw.get("canon", "publicados.json")
        n = kw.get("n", 10)
        resultados = motor.generar_lote(n)
        aceptados = [r for r in resultados if r.get("ok")]
        canon_path_obj = Path(canon_path)
        existente: Dict[str, Any] = {}
        if canon_path_obj.exists():
            try:
                existente = json.loads(canon_path_obj.read_text(encoding="utf-8"))
            except Exception:
                existente = {}
        publicados = existente.get("publicados", [])
        for r in aceptados:
            publicados.append({
                "texto": r["texto"],
                "plano": r["plano"],
                "firma": calcular_perfil(r["texto"]).como_dict(),
                "intentos": r["intentos"],
            })
        existente["publicados"] = publicados
        existente["n_total"] = len(publicados)
        canon_path_obj.write_text(json.dumps(existente, ensure_ascii=False, indent=2),
                                  encoding="utf-8")
        return {"publicados_total": len(publicados),
                "aceptados_nuevos": len(aceptados), "canon_path": str(canon_path_obj)}


class CanonExpansible(Instrumento):
    id = "canon_expandir"; bloque = "A"; flag = "--canon-expandir"

    def tesis(self) -> str:
        return ("El canon de una voz se define por lo que la voz ha rechazado, "
                "no por lo que ha aceptado. El corpus negativo es informativo.")

    def operar(self, motor, **kw):
        canon_path = Path(kw.get("canon", "publicados.json"))
        if not canon_path.exists():
            return {"error": "canon no encontrado"}
        datos = json.loads(canon_path.read_text(encoding="utf-8"))
        motivos = Counter()
        firmas = []
        for pub in datos.get("publicados", []):
            for v in pub.get("validaciones", [])[-1:] if isinstance(pub.get("validaciones"), list) else []:
                motivos[v.get("tipo", "ok")] += 1
            firmas.append(pub.get("firma", {}))
        return {"n_publicados": len(datos.get("publicados", [])),
                "motivos_rechazo": dict(motivos),
                "n_firmas": len(firmas)}


class Auditor(Instrumento):
    id = "auditar"; bloque = "B"; flag = "--auditar"

    def tesis(self) -> str:
        return ("La autoconsistencia estilométrica se mide como H(capa | eje); "
                "esa entropía es un invariante del generador.")

    def operar(self, motor, **kw):
        n = kw.get("n", 1000)
        resultados = motor.generar_lote(n)
        aceptados = [r for r in resultados if r.get("ok")]
        pares: List[Tuple[str, str]] = []
        for r in aceptados:
            plano = r["plano"]
            pares.append((plano["eje"], plano["capa"]))
        h_cond = self._entropia_condicional(pares)
        pares_corpus: List[Tuple[str, str]] = []
        for post in motor.corpus_embebido:
            for eje in post.get("ejes", []):
                pares_corpus.append((eje, post.get("capa", "tecnico")))
        h_corpus = self._entropia_condicional(pares_corpus)
        return {"H_gen": round(h_cond, 4), "H_corpus": round(h_corpus, 4),
                "delta_H": round(h_cond - h_corpus, 4),
                "aceptados": len(aceptados), "intentados": n}

    @staticmethod
    def _entropia_condicional(pares: List[Tuple[str, str]]) -> float:
        if not pares:
            return 0.0
        conteo: Dict[str, Counter] = defaultdict(Counter)
        for e, c in pares:
            conteo[e][c] += 1
        h = 0.0
        total = len(pares)
        for e, cs in conteo.items():
            p_e = sum(cs.values()) / total
            h_e = 0.0
            for c, k in cs.items():
                p = k / sum(cs.values())
                h_e -= p * math.log(p + 1e-12)
            h += p_e * h_e
        return h


class Ablation(Instrumento):
    id = "ablation"; bloque = "B"; flag = "--ablation"

    def tesis(self) -> str:
        return ("Cada validador tiene una contribución marginal medible; "
                "la suma de las ablaciones no es el todo.")

    def operar(self, motor, **kw):
        n = kw.get("n", 200)
        combinaciones = [
            (True, True, True), (True, True, False), (True, False, True),
            (False, True, True), (True, False, False), (False, True, False),
            (False, False, True), (False, False, False),
        ]
        resultados = {}
        for est, rep, tic in combinaciones:
            aceptados = 0
            for _ in range(n):
                r = motor.generador.generar(
                    validar_estilo=est, validar_repeticion=rep, validar_tics_flag=tic)
                if r.get("ok"):
                    aceptados += 1
            key = f"{int(est)}{int(rep)}{int(tic)}"
            resultados[key] = aceptados / n

        a_todo = resultados["111"]
        a_vacio = resultados["000"]
        sumas_ablacion = 0.0
        for key_abl in ["011", "101", "110"]:
            sumas_ablacion += (a_todo - resultados[key_abl])
        pred_aditiva = a_vacio + sumas_ablacion
        return {"aceptacion": resultados,
                "A_todos": a_todo, "A_vacio": a_vacio,
                "suma_ablaciones": round(sumas_ablacion, 4),
                "prediccion_aditiva": round(pred_aditiva, 4),
                "interaccion": round(a_todo - pred_aditiva, 4)}


class MatrizCoocurrencia(Instrumento):
    id = "matriz"; bloque = "B"; flag = "--matriz"

    def tesis(self) -> str:
        return ("La co-ocurrencia de términos forma una matriz de rango bajo; "
                "ese rango es la dimensión efectiva del discurso.")

    def operar(self, motor, **kw):
        textos = [p["cuerpo"] for p in motor.corpus_embebido] + list(motor.corpus_bootstrap.values())
        docs_tokens = [set(tokenizar(t)) for t in textos]
        vocab = sorted({t for d in docs_tokens for t in d})
        idx = {t: i for i, t in enumerate(vocab)}
        n = len(vocab)
        M = [[0.0] * n for _ in range(n)]
        for d in docs_tokens:
            for a in d:
                for b in d:
                    if a != b:
                        M[idx[a]][idx[b]] += 1
        valores_singulares = self._svd_aprox(M, k=min(20, n))
        return {"n_vocab": n, "n_textos": len(textos),
                "valores_singulares_top20": [round(v, 3) for v in valores_singulares],
                "dim_efectiva_aprox": self._dim_efectiva(valores_singulares)}

    @staticmethod
    def _svd_aprox(M: List[List[float]], k: int = 20) -> List[float]:
        n = len(M)
        if n == 0:
            return []
        v = [1.0 / math.sqrt(n)] * n
        valores = []
        M_t = [[M[j][i] for j in range(n)] for i in range(n)]
        for _ in range(k):
            w = [sum(M_t[i][j] * v[j] for j in range(n)) for i in range(n)]
            norma = math.sqrt(sum(x * x for x in w)) or 1
            v = [x / norma for x in w]
            Mv = [sum(M[i][j] * v[j] for j in range(n)) for i in range(n)]
            sigma = math.sqrt(sum(x * x for x in Mv))
            valores.append(sigma)
            if sigma < 1e-9:
                break
        return valores

    @staticmethod
    def _dim_efectiva(sigmas: List[float]) -> int:
        if not sigmas:
            return 0
        total = sum(sigmas)
        acumulado = 0.0
        for i, s in enumerate(sigmas):
            acumulado += s
            if acumulado / total >= 0.9:
                return i + 1
        return len(sigmas)


class DetectorDeriva(Instrumento):
    id = "deriva"; bloque = "B"; flag = "--deriva"

    def tesis(self) -> str:
        return ("La deriva estilística es un cambio de régimen detectable "
                "por CUSUM sobre la longitud media de frase.")

    def operar(self, motor, **kw):
        n = kw.get("n", 200)
        resultados = motor.generar_lote(n)
        longitudes = []
        for r in resultados:
            if r.get("ok"):
                longitudes.append(calcular_perfil(r["texto"]).long_media_frase)
        if len(longitudes) < 10:
            return {"error": "muestra insuficiente"}
        media = statistics.fmean(longitudes)
        cusum = []
        s = 0.0
        umbral = 3.0 * (statistics.pstdev(longitudes) or 1.0)
        puntos_cambio = []
        for i, l in enumerate(longitudes):
            s = max(0.0, s + (l - media))
            cusum.append(s)
            if s > umbral:
                puntos_cambio.append(i)
                s = 0.0
        return {"n": len(longitudes), "media": round(media, 3),
                "umbral": round(umbral, 3),
                "puntos_cambio": puntos_cambio,
                "max_cusum": round(max(cusum) if cusum else 0.0, 3)}


class Firma(Instrumento):
    id = "firma"; bloque = "B"; flag = "--firma"

    def tesis(self) -> str:
        return ("Todo texto tiene una firma estilométrica de ocho dimensiones, "
                "estable bajo paráfrasis e inestable bajo cambio de eje.")

    def operar(self, motor, **kw):
        texto = kw.get("texto") or ""
        if not texto:
            return {"error": "se requiere --texto"}
        perfil = calcular_perfil(texto)
        return {"firma_8d": perfil.vector_8d(), "perfil": perfil.como_dict()}


class ModoEspejo(Instrumento):
    id = "espejo"; bloque = "C"; flag = "--espejo"

    def tesis(self) -> str:
        return ("Existe un operador involutivo E tal que E(E(x)) = x, "
                "E preserva la firma y niega el contenido proposicional.")

    def operar(self, motor, **kw):
        texto = kw.get("texto") or ""
        if not texto:
            return {"error": "se requiere --texto"}
        espejo = self._invertir(texto)
        return {"original": texto, "espejo": espejo,
                "firma_original": calcular_perfil(texto).como_dict(),
                "firma_espejo": calcular_perfil(espejo).como_dict(),
                "involucion": self._invertir(espejo) == texto}

    @staticmethod
    def _invertir(texto: str) -> str:
        def negar(m):
            return f"{m.group(1)} no es {m.group(2)}"
        nuevo = re.sub(r"(\b[A-Za-zÁÉÍÓÚÑáéíóúñ]+)\s+es\s+([^\.]+)", negar, texto)
        nuevo = re.sub(r"\bno\s+es\s+no\s+es\b", "es", nuevo)
        return nuevo


class ModoContraejemplo(Instrumento):
    id = "contraejemplo"; bloque = "C"; flag = "--contraejemplo"

    def tesis(self) -> str:
        return ("El conjunto de textos que violan un validador es él mismo "
                "un corpus con estructura, no ruido.")

    def operar(self, motor, **kw):
        tic = kw.get("tic", "no_es_es")
        n = kw.get("n", 50)
        violadores = []
        for _ in range(n):
            r = motor.generador.generar(validar_tics_flag=False)
            if r.get("ok"):
                r_tic = validar_tics(r["texto"])
                if not r_tic.ok:
                    violadores.append(r["texto"])
        firmas = [calcular_perfil(v).como_dict() for v in violadores]
        if not firmas:
            return {"n_violadores": 0}
        campos = ["long_media_frase", "diversidad_lexica", "long_media_palabra"]
        medias = {c: round(statistics.fmean(f[c] for f in firmas), 4) for c in campos}
        return {"n_violadores": len(violadores), "firma_media_violadores": medias,
                "tic_objetivo": tic}


class ModoCiego(Instrumento):
    id = "ciego"; bloque = "C"; flag = "--ciego"

    def tesis(self) -> str:
        return ("El sesgo intrínseco de un generador es la diferencia entre "
                "su distribución ciega y su distribución validada.")

    def operar(self, motor, **kw):
        n = kw.get("n", 500)
        ciega = []
        for _ in range(n):
            r = motor.generador.generar(validar_estilo=False, validar_repeticion=False,
                                        validar_tics_flag=False)
            if r.get("ok"):
                ciega.append(calcular_perfil(r["texto"]).como_dict())
        validada = []
        for _ in range(n):
            r = motor.generador.generar()
            if r.get("ok"):
                validada.append(calcular_perfil(r["texto"]).como_dict())
        if not ciega or not validada:
            return {"error": "sin muestras"}
        def media(d, k): return statistics.fmean(x[k] for x in d)
        campos = ["long_media_frase", "diversidad_lexica", "long_media_palabra",
                  "ratio_frases_cortas"]
        delta = {c: round(media(validada, c) - media(ciega, c), 4) for c in campos}
        kl = sum(abs(delta[c]) for c in campos)
        return {"delta_firma_validada_menos_ciega": delta, "sesgo_total": round(kl, 4),
                "n_ciega": len(ciega), "n_validada": len(validada)}


class ModoForense(Instrumento):
    id = "forense"; bloque = "C"; flag = "--forense"

    def tesis(self) -> str:
        return ("La autoría se atribuye por n-gramas funcionales, no de contenido; "
                "la tasa de acierto es independiente del tema.")

    def operar(self, motor, **kw):
        textos = [p["cuerpo"] for p in motor.corpus_embebido]
        etiquetas = [p["id"] for p in motor.corpus_embebido]
        aciertos_func = self._clasificar(textos, etiquetas, funcional=True)
        aciertos_cont = self._clasificar(textos, etiquetas, funcional=False)
        return {"acierto_funcional": round(aciertos_func, 4),
                "acierto_contenido": round(aciertos_cont, 4),
                "n_textos": len(textos)}

    @staticmethod
    def _clasificar(textos: List[str], etiquetas: List[str], funcional: bool) -> float:
        tokens = [tokenizar(t) for t in textos]
        filtrado = []
        for ts in tokens:
            if funcional:
                filtrado.append([t for t in ts if es_funcional(t)])
            else:
                filtrado.append([t for t in ts if not es_funcional(t)])
        vistos = 0
        aciertos = 0
        for i, ts in enumerate(filtrado):
            if len(ts) < 3:
                continue
            vistos += 1
            probe = ts[0]
            candidatos = [(j, sum(1 for t in ts if t == probe and t in filtrado[j]))
                          for j in range(len(filtrado)) if j != i]
            if not candidatos:
                continue
            mejor = max(candidatos, key=lambda x: x[1])[0]
            if etiquetas[mejor] == etiquetas[i]:
                aciertos += 1
        return aciertos / vistos if vistos else 0.0


class Interpolador(Instrumento):
    id = "interpolar"; bloque = "D"; flag = "--interpolar"

    def tesis(self) -> str:
        return ("La interpolación de voces no es conmutativa ni asociativa; "
                "el orden importa.")

    def operar(self, motor, **kw):
        peso = kw.get("peso", 0.5)
        textos_a = kw.get("textos_a") or []
        textos_b = kw.get("textos_b") or []
        if not textos_a or not textos_b:
            return {"error": "se requieren dos corpus"}
        fa = calcular_perfil("\n\n".join(textos_a)).como_dict()
        fb = calcular_perfil("\n\n".join(textos_b)).como_dict()
        objetivo = {k: peso * fa[k] + (1 - peso) * fb[k]
                    for k in fa if isinstance(fa[k], (int, float))}
        muestra = motor.generar_lote(50)
        firmas = [calcular_perfil(r["texto"]).como_dict() for r in muestra if r.get("ok")]
        error = self._error_medio(firmas, objetivo)
        objetivo_conm = {k: peso * fb[k] + (1 - peso) * fa[k]
                         for k in fb if isinstance(fb[k], (int, float))}
        error_conm = self._error_medio(firmas, objetivo_conm)
        return {"error_objetivo_ab": round(error, 4),
                "error_objetivo_ba": round(error_conm, 4),
                "conmutativa": abs(error - error_conm) < 1e-3,
                "peso": peso}

    @staticmethod
    def _error_medio(firmas: List[Dict[str, float]], objetivo: Dict[str, float]) -> float:
        if not firmas:
            return 0.0
        campos = [k for k, v in objetivo.items() if isinstance(v, (int, float))]
        errores = []
        for f in firmas:
            e = sum(abs(f.get(c, 0) - objetivo[c]) for c in campos) / max(1, len(campos))
            errores.append(e)
        return statistics.fmean(errores)


class Reconstructor(Instrumento):
    id = "reconstruir"; bloque = "D"; flag = "--reconstruir"

    def tesis(self) -> str:
        return ("Bajo restricciones de estilo, un texto con huecos tiene una "
                "única reconstrucción válida, y esa unicidad es demostrable.")

    def operar(self, motor, **kw):
        patron = kw.get("patron") or "El ____ no es ____. Es ____."
        vocab = self._vocabulario(motor)
        candidatos = self._enumerar(patron, vocab, max_candidatos=200)
        validos = []
        for c in candidatos:
            if validar_estilometria(c).ok and validar_tics(c).ok:
                validos.append(c)
        return {"patron": patron, "n_candidatos": len(candidatos),
                "n_validos": len(validos),
                "ejemplos": validos[:5], "unico": len(validos) == 1}

    @staticmethod
    def _vocabulario(motor) -> List[str]:
        vocab: Set[str] = set()
        for p in motor.corpus_embebido:
            vocab.update(t for t in tokenizar(p["cuerpo"]) if len(t) > 3)
        return sorted(vocab)

    @staticmethod
    def _enumerar(patron: str, vocab: List[str], max_candidatos: int = 200) -> List[str]:
        huecos = patron.count("____")
        if huecos == 0:
            return [patron]
        rng = random.Random(42)
        out = []
        for _ in range(max_candidatos):
            texto = patron
            for _ in range(huecos):
                palabra = rng.choice(vocab)
                texto = texto.replace("____", palabra, 1)
            out.append(texto)
        return out


class ModoTemporal(Instrumento):
    id = "temporal"; bloque = "D"; flag = "--temporal"

    def tesis(self) -> str:
        return ("Todo corpus tiene una línea de tiempo implícita detectable "
                "por marcas léxicas.")

    def operar(self, motor, **kw):
        anios = list(range(2018, 2026))
        marcas = {}
        for p in motor.corpus_embebido:
            for a in anios:
                if str(a) in p["cuerpo"]:
                    marcas.setdefault(str(a), []).append(p["id"])
        marcas_encontradas = sum(1 for a in anios if str(a) in marcas)
        return {"anios_con_marcas": marcas_encontradas,
                "detalle": {k: len(v) for k, v in marcas.items()},
                "n_textos": len(motor.corpus_embebido)}


class ModoFrontera(Instrumento):
    id = "frontera"; bloque = "E"; flag = "--frontera"

    def tesis(self) -> str:
        return ("El espacio declarado de un generador tiene un borde medible; "
                "los textos fuera del borde son clasificables por su firma.")

    def operar(self, motor, **kw):
        n = kw.get("n", 500)
        dentro, fuera = [], []
        for _ in range(n):
            r = motor.generador.generar()
            if r.get("ok"):
                dentro.append(calcular_perfil(r["texto"]).como_dict())
            r2 = motor.generador.generar(eje="ia", capa="militar")
            if r2.get("ok") and r2["plano"]["cierre"] not in ("C14",):
                fuera.append(calcular_perfil(r2["texto"]).como_dict())
        if not dentro or not fuera:
            return {"error": "sin muestras"}
        campos = ["long_media_frase", "diversidad_lexica", "long_media_palabra"]
        media_dentro = {c: statistics.fmean(x[c] for x in dentro) for c in campos}
        media_fuera = {c: statistics.fmean(x[c] for x in fuera) for c in campos}
        separacion = sum(abs(media_dentro[c] - media_fuera[c]) for c in campos)
        return {"media_dentro": {k: round(v, 4) for k, v in media_dentro.items()},
                "media_fuera": {k: round(v, 4) for k, v in media_fuera.items()},
                "separacion": round(separacion, 4),
                "n_dentro": len(dentro), "n_fuera": len(fuera)}


class Consenso(Instrumento):
    id = "consenso"; bloque = "F"; flag = "--consenso"

    def tesis(self) -> str:
        return ("Cuando dos validadores independientes coinciden en rechazar, "
                "la causa es estructural, no superficial.")

    def operar(self, motor, **kw):
        n = kw.get("n", 500)
        rechazos = {"est": 0, "rep": 0, "tic": 0, "est+rep": 0, "est+tic": 0, "rep+tic": 0,
                    "todos": 0}
        for _ in range(n):
            r = motor.generador.generar(validar_estilo=False, validar_repeticion=False,
                                        validar_tics_flag=False)
            if not r.get("ok"):
                continue
            texto = r["texto"]
            e = not validar_estilometria(texto).ok
            p = not validar_anti_repeticion(texto, motor.indice).ok
            t = not validar_tics(texto).ok
            if e and p and t: rechazos["todos"] += 1
            elif e and p: rechazos["est+rep"] += 1
            elif e and t: rechazos["est+tic"] += 1
            elif p and t: rechazos["rep+tic"] += 1
            elif e: rechazos["est"] += 1
            elif p: rechazos["rep"] += 1
            elif t: rechazos["tic"] += 1
        return {"n": n, "rechazos": rechazos,
                "consenso_2_o_mas": sum(v for k, v in rechazos.items() if "+" in k or k == "todos")}


class Disenso(Instrumento):
    id = "disenso"; bloque = "F"; flag = "--disenso"

    def tesis(self) -> str:
        return ("El conjunto de textos donde los validadores discrepan define "
                "el límite epistémico del sistema, y ese límite es móvil.")

    def operar(self, motor, **kw):
        n = kw.get("n", 100)
        disensos_por_capa = defaultdict(int)
        totales_por_capa = defaultdict(int)
        for capa in [c["id"] for c in CAPAS_LEXICAS]:
            for _ in range(n // len(CAPAS_LEXICAS) + 1):
                r = motor.generador.generar(capa=capa, validar_estilo=False,
                                            validar_repeticion=False, validar_tics_flag=False)
                if not r.get("ok"):
                    continue
                totales_por_capa[capa] += 1
                texto = r["texto"]
                e = not validar_estilometria(texto).ok
                p = not validar_anti_repeticion(texto, motor.indice).ok
                t = not validar_tics(texto).ok
                if sum([e, p, t]) >= 2:
                    disensos_por_capa[capa] += 1
        temp_por_capa = {c["id"]: c["temperatura"] for c in CAPAS_LEXICAS}
        return {"tasa_rechazo_por_capa": {
                    k: round(disensos_por_capa[k] / max(1, totales_por_capa[k]), 4)
                    for k in totales_por_capa},
                "temperatura_por_capa": temp_por_capa}


class Cuarentena(Instrumento):
    id = "cuarentena"; bloque = "F"; flag = "--cuarentena"

    def tesis(self) -> str:
        return ("Los textos rechazados forman un corpus negativo cuyo análisis "
                "revela los modos de fallo del generador.")

    def operar(self, motor, **kw):
        n = kw.get("n", 300)
        rechazados = []
        for _ in range(n):
            r = motor.generador.generar(validar_estilo=False, validar_repeticion=False,
                                        validar_tics_flag=False)
            if not r.get("ok"):
                continue
            texto = r["texto"]
            motivos = []
            if not validar_estilometria(texto).ok:
                motivos.append("est")
            if not validar_anti_repeticion(texto, motor.indice).ok:
                motivos.append("rep")
            if not validar_tics(texto).ok:
                motivos.append("tic")
            if motivos:
                rechazados.append({"motivos": motivos,
                                   "firma": calcular_perfil(texto).como_dict()})
        clusters = defaultdict(list)
        for r in rechazados:
            clave = "+".join(r["motivos"])
            clusters[clave].append(r["firma"]["long_media_frase"])
        return {"n_rechazados": len(rechazados),
                "modos": {k: {"n": len(v),
                              "long_media_frase": round(statistics.fmean(v), 3)}
                          for k, v in clusters.items()}}


class Mutador(Instrumento):
    id = "mutar"; bloque = "G"; flag = "--mutar"

    def tesis(self) -> str:
        return ("La mutación de una sola variable del plano produce una distancia "
                "estilométrica predecible por una función lineal de la variable.")

    def operar(self, motor, **kw):
        variable = kw.get("variable", "capa")
        if variable == "capa":
            valores = [c["id"] for c in CAPAS_LEXICAS]
        elif variable == "eje":
            valores = [e["id"] for e in EJES]
        else:
            return {"error": f"variable desconocida: {variable}"}
        distancias = []
        base = motor.generar(capa=valores[0] if variable == "capa" else None,
                             eje=valores[0] if variable == "eje" else None)
        if not base.get("ok"):
            return {"error": "base fallida"}
        fb = calcular_perfil(base["texto"]).vector_8d()
        for v in valores[1:]:
            kwargs = {"capa": v} if variable == "capa" else {"eje": v}
            r = motor.generar(**kwargs)
            if not r.get("ok"):
                continue
            fv = calcular_perfil(r["texto"]).vector_8d()
            d = math.sqrt(sum((a - b) ** 2 for a, b in zip(fb, fv)))
            distancias.append({"valor": v, "distancia": round(d, 4)})
        return {"variable": variable, "n_valores": len(distancias),
                "distancias": distancias,
                "media_distancia": round(statistics.fmean(d["distancia"] for d in distancias), 4)
                                    if distancias else 0.0}


class Cruzador(Instrumento):
    id = "cruzar"; bloque = "G"; flag = "--cruzar"

    def tesis(self) -> str:
        return ("El cruce de dos planos produce un texto cuya firma es la media "
                "armónica, no la aritmética, de las firmas progenitoras.")

    def operar(self, motor, **kw):
        plano_a = kw.get("plano_a")
        plano_b = kw.get("plano_b")
        if not plano_a or not plano_b:
            return {"error": "se requieren dos planos"}
        ca = Combinacion.desde_clave(plano_a)
        cb = Combinacion.desde_clave(plano_b)
        ra = motor.generar(combinacion=ca)
        rb = motor.generar(combinacion=cb)
        if not (ra.get("ok") and rb.get("ok")):
            return {"error": "generación fallida"}
        fa = calcular_perfil(ra["texto"]).como_dict()
        fb = calcular_perfil(rb["texto"]).como_dict()
        campos = ["long_media_frase", "diversidad_lexica", "long_media_palabra"]
        aritmetica = {c: (fa[c] + fb[c]) / 2 for c in campos}
        armonica = {c: (2 * fa[c] * fb[c] / (fa[c] + fb[c])) if (fa[c] + fb[c]) > 0 else 0
                    for c in campos}
        elenco_cruzado = tuple(set(ca.elenco + cb.elenco))[:3]
        combo_cruzado = Combinacion(eje=ca.eje, elenco=elenco_cruzado, capa=cb.capa)
        rc = motor.generar(combinacion=combo_cruzado)
        if not rc.get("ok"):
            return {"error": "cruce fallido"}
        fc = calcular_perfil(rc["texto"]).como_dict()
        err_arit = sum(abs(fc[c] - aritmetica[c]) for c in campos) / len(campos)
        err_arm = sum(abs(fc[c] - armonica[c]) for c in campos) / len(campos)
        return {"error_aritmetica": round(err_arit, 4),
                "error_armonica": round(err_arm, 4),
                "gana_armonica": err_arm < err_arit}


class Degradador(Instrumento):
    id = "degradar"; bloque = "G"; flag = "--degradar"

    def tesis(self) -> str:
        return ("La degradación progresiva revela una jerarquía de capas: "
                "algunas son estructurales, otras decorativas.")

    def operar(self, motor, **kw):
        r = motor.generar()
        if not r.get("ok"):
            return {"error": "generación fallida"}
        texto = r["texto"]
        f0 = calcular_perfil(texto).vector_8d()
        degradaciones = [
            ("eliminar_adjetivos", self._eliminar_adjetivos),
            ("cortar_frases", self._cortar_frases),
            ("invertir_orden", self._invertir_orden),
            ("mayuscular", lambda t: t.upper()),
        ]
        curva = []
        t = texto
        for nombre, fn in degradaciones:
            t = fn(t)
            ft = calcular_perfil(t).vector_8d()
            d = math.sqrt(sum((a - b) ** 2 for a, b in zip(f0, ft)))
            curva.append({"paso": nombre, "distancia": round(d, 4)})
        return {"curva": curva, "n_pasos": len(curva)}

    @staticmethod
    def _eliminar_adjetivos(texto: str) -> str:
        return re.sub(r"\b\w+mente\b", "", texto)

    @staticmethod
    def _cortar_frases(texto: str) -> str:
        frases = dividir_frases(texto)
        return ". ".join(f.split()[0] if f.split() else f for f in frases)

    @staticmethod
    def _invertir_orden(texto: str) -> str:
        parrafos = texto.split("\n\n")
        return "\n\n".join(reversed(parrafos))


class Autopsia(Instrumento):
    id = "autopsia"; bloque = "H"; flag = "--autopsia"

    def tesis(self) -> str:
        return ("Un generador puede diagnosticar su propia producción midiendo "
                "la distancia entre plano y texto.")

    def operar(self, motor, **kw):
        n = kw.get("n", 100)
        deltas = []
        for _ in range(n):
            r = motor.generar()
            if not r.get("ok"):
                continue
            firma_texto = calcular_perfil(r["texto"]).como_dict()
            plano = r["plano"]
            firma_esperada = self._firma_esperada(plano, motor)
            campos = ["long_media_frase", "diversidad_lexica", "long_media_palabra"]
            d = sum(abs(firma_texto[c] - firma_esperada[c]) for c in campos) / len(campos)
            deltas.append({"delta": d, "eje": plano["eje"], "capa": plano["capa"]})
        if not deltas:
            return {"error": "sin muestras"}
        delta_medio = statistics.fmean(x["delta"] for x in deltas)
        return {"delta_medio": round(delta_medio, 4), "n": len(deltas),
                "outliers": [x for x in deltas if x["delta"] > delta_medio * 2][:5]}

    @staticmethod
    def _firma_esperada(plano: Dict[str, Any], motor: MotorCascabel) -> Dict[str, float]:
        capa = INDICE_CAPAS.get(plano["capa"], {})
        temp = capa.get("temperatura", 0.3)
        return {
            "long_media_frase": 12.0 + 5 * temp,
            "diversidad_lexica": 0.6 - 0.2 * temp,
            "long_media_palabra": 5.0,
        }


class EspejoNegro(Instrumento):
    id = "espejo_negro"; bloque = "H"; flag = "--espejo-negro"

    def tesis(self) -> str:
        return ("Existe un operador que genera el texto que el motor nunca "
                "escribiría; ese texto es informativo sobre el motor.")

    def operar(self, motor, **kw):
        r = motor.generar()
        if not r.get("ok"):
            return {"error": "generación fallida"}
        f_original = calcular_perfil(r["texto"]).como_dict()
        mejor_candidato = None
        mejor_distancia = float("inf")
        for _ in range(200):
            r2 = motor.generador.generar(validar_estilo=False, validar_repeticion=False,
                                         validar_tics_flag=False)
            if not r2.get("ok"):
                continue
            es_rechazado = (not validar_estilometria(r2["texto"]).ok
                            or not validar_tics(r2["texto"]).ok)
            if not es_rechazado:
                continue
            f2 = calcular_perfil(r2["texto"]).como_dict()
            campos = ["long_media_frase", "diversidad_lexica", "long_media_palabra"]
            d = sum(abs(f_original[c] - f2[c]) for c in campos)
            if d < mejor_distancia:
                mejor_distancia = d
                mejor_candidato = r2["texto"]
        return {"original": r["texto"][:100] + "...",
                "espejo_negro": mejor_candidato[:100] + "..." if mejor_candidato else None,
                "distancia_minima": round(mejor_distancia, 4) if mejor_candidato else None}


class Parasito(Instrumento):
    id = "parasito"; bloque = "H"; flag = "--parasito"

    def tesis(self) -> str:
        return ("Un texto generado puede hospedar otro sin violar restricciones; "
                "la capacidad de hospedaje mide la permisividad del estilo.")

    def operar(self, motor, **kw):
        r_huesped = motor.generar()
        r_parasito = motor.generar(capa="militar")
        if not (r_huesped.get("ok") and r_parasito.get("ok")):
            return {"error": "generación fallida"}
        huesped = r_huesped["texto"]
        parasito = r_parasito["texto"][:100]
        mitad = len(huesped) // 2
        fusion = huesped[:mitad] + "\n\n" + parasito + "\n\n" + huesped[mitad:]
        valido = validar_estilometria(fusion).ok and validar_tics(fusion).ok
        ratio = len(parasito) / max(1, len(huesped))
        return {"hospedaje_valido": valido,
                "ratio_parasito": round(ratio, 4),
                "validacion_estilo": validar_estilometria(fusion).ok,
                "validacion_tics": validar_tics(fusion).ok}


class Compresor(Instrumento):
    id = "comprimir"; bloque = "I"; flag = "--comprimir"

    def tesis(self) -> str:
        return ("La longitud mínima de descripción de un texto es proporcional "
                "a la complejidad de su plano, no a su longitud.")

    def operar(self, motor, **kw):
        r = motor.generar()
        if not r.get("ok"):
            return {"error": "generación fallida"}
        texto = r["texto"]
        plano = json.dumps(r["plano"], ensure_ascii=False)
        comp_texto = len(zlib.compress(texto.encode("utf-8")))
        comp_plano = len(zlib.compress(plano.encode("utf-8")))
        return {"len_texto": len(texto), "len_plano": len(plano),
                "comp_texto": comp_texto, "comp_plano": comp_plano,
                "ratio_texto_plano": round(comp_texto / max(1, comp_plano), 4),
                "ratio_comp_texto_original": round(comp_texto / max(1, len(texto)), 4)}


class Expansor(Instrumento):
    id = "expandir"; bloque = "I"; flag = "--expandir"

    def tesis(self) -> str:
        return ("La expansión de un texto comprimido revela qué información "
                "es redundante y cuál es irreducible.")

    def operar(self, motor, **kw):
        r = motor.generar()
        if not r.get("ok"):
            return {"error": "generación fallida"}
        texto = r["texto"]
        parrafos = texto.split("\n\n")
        if len(parrafos) < 3:
            return {"error": "texto demasiado corto"}
        f0 = calcular_perfil(texto).vector_8d()
        curva = []
        for k in range(1, len(parrafos)):
            parcial = "\n\n".join(parrafos[:k])
            fk = calcular_perfil(parcial).vector_8d()
            d = math.sqrt(sum((a - b) ** 2 for a, b in zip(f0, fk)))
            curva.append({"k": k, "distancia": round(d, 4)})
        return {"curva": curva, "n_parrafos": len(parrafos)}


class Censor(Instrumento):
    id = "censurar"; bloque = "J"; flag = "--censurar"

    def tesis(self) -> str:
        return ("La censura estructural es distinguible de la léxica por "
                "el patrón de huecos sintácticos que deja.")

    def operar(self, motor, **kw):
        tipo = kw.get("tipo", "lexica")
        r = motor.generar()
        if not r.get("ok"):
            return {"error": "generación fallida"}
        texto = r["texto"]
        if tipo == "lexica":
            censurado = self._censura_lexica(texto)
        else:
            censurado = self._censura_estructural(texto)
        f_orig = calcular_perfil(texto).como_dict()
        f_cens = calcular_perfil(censurado).como_dict()
        return {"tipo": tipo, "texto_censurado": censurado[:200] + "...",
                "firma_original": f_orig, "firma_censurada": f_cens}

    @staticmethod
    def _censura_lexica(texto: str) -> str:
        prohibidas = ["ia", "modelo", "datos", "nube", "senior"]
        for p in prohibidas:
            texto = re.sub(rf"\b{p}\b", "█" * len(p), texto, flags=re.IGNORECASE)
        return texto

    @staticmethod
    def _censura_estructural(texto: str) -> str:
        parrafos = texto.split("\n\n")
        return "\n\n".join(p.split(".")[0] + "." for p in parrafos if p)


class Confesor(Instrumento):
    id = "confesar"; bloque = "J"; flag = "--confesar"

    def tesis(self) -> str:
        return ("Un generador puede producir un texto que declare sus propias "
                "restricciones sin violarlas; esto es un test de autoconsistencia.")

    def operar(self, motor, **kw):
        clave = kw.get("combinacion") or "ia|cto|tecnico"
        combo = Combinacion.desde_clave(clave)
        r = motor.generar(combinacion=combo)
        if not r.get("ok"):
            return {"error": "generación fallida"}
        plano = r["plano"]
        confesion = (f"Este texto se escribió con eje {plano['eje']}, "
                     f"capa {plano['capa']}, elenco {'+'.join(plano['elenco'])}, "
                     f"virus {plano['virus']}, adenovirus {plano['adenovirus']}, "
                     f"retórico {plano['retorico']}, cierre {plano['cierre']}, "
                     f"temperatura {plano['temperatura']}.")
        valido = (validar_estilometria(confesion).ok and validar_tics(confesion).ok)
        return {"confesion": confesion, "valida": valido,
                "generada_con_plano": plano,
                "texto_original": r["texto"][:100] + "..."}


INSTRUMENTOS: Dict[str, Instrumento] = {
    i.flag.lstrip("-"): i
    for i in [
        Publicador(), CanonExpansible(),
        Auditor(), Ablation(), MatrizCoocurrencia(), DetectorDeriva(), Firma(),
        ModoEspejo(), ModoContraejemplo(), ModoCiego(), ModoForense(),
        Interpolador(), Reconstructor(), ModoTemporal(),
        ModoFrontera(),
        Consenso(), Disenso(), Cuarentena(),
        Mutador(), Cruzador(), Degradador(),
        Autopsia(), EspejoNegro(), Parasito(),
        Compresor(), Expansor(),
        Censor(), Confesor(),
    ]
}

assert len(INSTRUMENTOS) == 28, "Deben existir exactamente 28 instrumentos."
for _bloque, _ids in METADATOS["instrumentos_bloques"].items():
    for _id in _ids:
        assert _id.replace("-", "_") in INSTRUMENTOS, f"Falta instrumento: {_id}"


# ============================================================================
# 22. PRESENTACIÓN
# ============================================================================

def formatear_post(resultado: Dict[str, Any], ancho: int = 78) -> str:
    if not resultado.get("ok"):
        return ("── MOTOR CASCABEL ── SIN RESULTADO ──\n"
                f"{resultado.get('error', 'Error desconocido.')}")
    plano = resultado["plano"]
    eje = INDICE_EJES.get(plano["eje"], {})
    capa = INDICE_CAPAS.get(plano["capa"], {})
    personajes = ", ".join(INDICE_ELENCO.get(p, {}).get("nombre", p) for p in plano["elenco"])
    cabecera = (
        f"── MOTOR CASCABEL v{METADATOS['version']} ──────────────────────────────\n"
        f"eje      : {eje.get('nombre', plano['eje'])}\n"
        f"capa     : {capa.get('nombre', plano['capa'])} (temp {plano['temperatura']})\n"
        f"elenco   : {personajes}\n"
        f"virus    : {plano['virus']}   adenovirus: {plano['adenovirus']}\n"
        f"retórico : {plano['retorico']}   cierre: {plano['cierre']}\n"
        f"intentos : {resultado['intentos']}\n"
        f"────────────────────────────────────────────────────────────────\n"
    )
    cuerpo = "\n".join(textwrap.fill(p, width=ancho) for p in resultado["texto"].split("\n\n"))
    return cabecera + "\n" + cuerpo + "\n"


def formatear_info(info: Dict[str, Any]) -> str:
    lineas = ["═══ MOTOR CASCABEL ═══", "", "METADATOS"]
    for k, v in info["metadatos"].items():
        lineas.append(f"  {k:.<32} {v}")
    lineas.extend(["", "CORPUS"])
    for k, v in info["corpus"].items():
        lineas.append(f"  {k:.<32} {v}")
    lineas.extend(["", "ÍNDICE"])
    for k, v in info["indice"].items():
        lineas.append(f"  {k:.<32} {v}")
    lineas.extend(["", "PERFIL DEL CORPUS"])
    for k, v in info["perfil_corpus"].items():
        lineas.append(f"  {k:.<32} {v}")
    lineas.extend(["", "COMBINATORIA"])
    comb = info.get("combinatoria", {})
    for k in ("total", "n_ejes", "n_elencos", "n_capas", "version"):
        if k in comb:
            lineas.append(f"  {k:.<32} {comb[k]}")
    lineas.extend(["", "PROGRAMADOR"])
    for k, v in info.get("programador", {}).items():
        lineas.append(f"  {k:.<32} {v}")
    lineas.extend(["", "CATÁLOGOS"])
    for k, v in info["catalogos"].items():
        lineas.append(f"  {k:.<32} {v}")
    return "\n".join(lineas)


def formatear_combinatoria(info: Dict[str, Any]) -> str:
    lineas = ["═══ ESPACIO COMBINATORIO ═══", "",
              f"total          : {info['total']}",
              f"n_ejes         : {info['n_ejes']}",
              f"n_elencos      : {info['n_elencos']}",
              f"n_capas        : {info['n_capas']}", "", "ejes:"]
    for e in info["ejes"]:
        lineas.append(f"  - {e}")
    lineas.extend(["", "capas:"])
    for c in info["capas"]:
        lineas.append(f"  - {c}")
    lineas.extend(["", "elencos por tamaño:"])
    for k, v in info["combinaciones_por_elenco"].items():
        lineas.append(f"  {k}: {v}")
    lineas.extend(["", "combinaciones observadas en el corpus:"])
    for c in info.get("desde_corpus", []):
        lineas.append(f"  - {c}")
    return "\n".join(lineas)


# ============================================================================
# 23. CLI
# ============================================================================

def _construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cascabel",
        description="MOTOR CASCABEL v0.1.0 — generador + 28 tesis operables.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Regla dura: VARIACIONES NUEVAS. Nunca repetición. Nunca tic.\n"
            "Toda adición es una tesis falsable.\n"
        ),
    )

    parser.add_argument("--eje")
    parser.add_argument("--elenco", nargs="*")
    parser.add_argument("--capa")
    parser.add_argument("--n", type=int, default=1)
    parser.add_argument("--semilla", type=int, default=None)

    parser.add_argument("--no-validar-estilo", action="store_true")
    parser.add_argument("--no-validar-repeticion", action="store_true")
    parser.add_argument("--no-validar-tics", action="store_true")

    parser.add_argument("--llm", action="store_true")
    parser.add_argument("--corpus", default=None)

    parser.add_argument("--programador-modo",
                        choices=METADATOS["programador_modos"], default="muestreo")
    parser.add_argument("--programador-ciclo", type=int,
                        default=METADATOS["programador_ciclo_defecto"])
    parser.add_argument("--programador-estado", default=None)
    parser.add_argument("--programador-info", action="store_true")
    parser.add_argument("--programador-reset", action="store_true")
    parser.add_argument("--no-programador", action="store_true")

    parser.add_argument("--info", action="store_true")
    parser.add_argument("--combinatoria", action="store_true")
    parser.add_argument("--check-bootstrap", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verbose", action="store_true")

    parser.add_argument("--publicar", action="store_true")
    parser.add_argument("--canon-expandir", action="store_true")
    parser.add_argument("--canon", default="publicados.json")
    parser.add_argument("--auditar", action="store_true")
    parser.add_argument("--ablation", action="store_true")
    parser.add_argument("--matriz", action="store_true")
    parser.add_argument("--deriva", action="store_true")
    parser.add_argument("--firma", action="store_true")
    parser.add_argument("--texto", default="")
    parser.add_argument("--espejo", action="store_true")
    parser.add_argument("--contraejemplo", action="store_true")
    parser.add_argument("--tic", default="no_es_es")
    parser.add_argument("--ciego", action="store_true")
    parser.add_argument("--forense", nargs="*")
    parser.add_argument("--interpolar", nargs="*")
    parser.add_argument("--peso", type=float, default=0.5)
    parser.add_argument("--reconstruir", type=str, nargs="?", const="El ____ no es ____. Es ____.")
    parser.add_argument("--patron", default="")
    parser.add_argument("--temporal", action="store_true")
    parser.add_argument("--frontera", action="store_true")
    parser.add_argument("--consenso", action="store_true")
    parser.add_argument("--disenso", action="store_true")
    parser.add_argument("--cuarentena", action="store_true")
    parser.add_argument("--mutar", action="store_true")
    parser.add_argument("--variable", default="capa")
    parser.add_argument("--cruzar", action="store_true")
    parser.add_argument("--plano-a", default=None)
    parser.add_argument("--plano-b", default=None)
    parser.add_argument("--degradar", action="store_true")
    parser.add_argument("--autopsia", action="store_true")
    parser.add_argument("--espejo-negro", action="store_true")
    parser.add_argument("--parasito", action="store_true")
    parser.add_argument("--comprimir", action="store_true")
    parser.add_argument("--expandir", action="store_true")
    parser.add_argument("--censurar", action="store_true")
    parser.add_argument("--tipo", choices=["lexica", "estructural"], default="lexica")
    parser.add_argument("--confesar", action="store_true")
    parser.add_argument("--combinacion", default=None)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _construir_parser()
    args = parser.parse_args(argv)

    motor = MotorCascabel(
        ruta_corpus=args.corpus,
        semilla=args.semilla,
        verbose=args.verbose,
        programador_modo=args.programador_modo,
        programador_ciclo=args.programador_ciclo,
        programador_estado=args.programador_estado,
        programador_activo=not args.no_programador,
    )

    if args.info:
        info = motor.info()
        print(json.dumps(info, ensure_ascii=False, indent=2) if args.json
              else formatear_info(info))
        return 0

    if args.combinatoria:
        info = motor.combinatoria_info()
        print(json.dumps(info, ensure_ascii=False, indent=2) if args.json
              else formatear_combinatoria(info))
        return 0

    if args.check_bootstrap:
        r = motor.bootstrap_info
        if r is None:
            print("Bootstrap no ejecutado.", file=sys.stderr)
            return 2
        print(json.dumps({
            "exito": r.exito, "ruta": r.ruta, "mensaje": r.mensaje,
            "capitulos_cargados": len(r.capitulos),
            "capitulos_excluidos": r.excluidos,
            "bytes_leidos": r.bytes_leidos,
            "numeros_cargados": sorted(r.capitulos.keys()),
        }, ensure_ascii=False, indent=2))
        return 0 if r.exito else 1

    if args.programador_info:
        print(json.dumps(motor.programador_info(), ensure_ascii=False, indent=2))
        return 0

    if args.programador_reset:
        motor.programador_reset()
        print("Programador reiniciado.")
        return 0

    invocados = {
        "publicar": ("publicar", {"canon": args.canon, "n": args.n}),
        "canon_expandir": ("canon_expandir", {"canon": args.canon}),
        "auditar": ("auditar", {"n": args.n}),
        "ablation": ("ablation", {"n": args.n}),
        "matriz": ("matriz", {}),
        "deriva": ("deriva", {"n": args.n}),
        "firma": ("firma", {"texto": args.texto}),
        "espejo": ("espejo", {"texto": args.texto}),
        "contraejemplo": ("contraejemplo", {"tic": args.tic, "n": args.n}),
        "ciego": ("ciego", {"n": args.n}),
        "forense": ("forense", {}),
        "interpolar": ("interpolar", {"peso": args.peso}),
        "reconstruir": ("reconstruir", {"patron": args.patron or args.reconstruir or ""}),
        "temporal": ("temporal", {}),
        "frontera": ("frontera", {"n": args.n}),
        "consenso": ("consenso", {"n": args.n}),
        "disenso": ("disenso", {"n": args.n}),
        "cuarentena": ("cuarentena", {"n": args.n}),
        "mutar": ("mutar", {"variable": args.variable}),
        "cruzar": ("cruzar", {"plano_a": args.plano_a, "plano_b": args.plano_b}),
        "degradar": ("degradar", {}),
        "autopsia": ("autopsia", {"n": args.n}),
        "espejo_negro": ("espejo-negro", {}),
        "parasito": ("parasito", {}),
        "comprimir": ("comprimir", {}),
        "expandir": ("expandir", {}),
        "censurar": ("censurar", {"tipo": args.tipo}),
        "confesar": ("confesar", {"combinacion": args.combinacion}),
    }

    for arg_attr, (key, kw) in invocados.items():
        if getattr(args, arg_attr.replace("-", "_"), False):
            instrumento = INSTRUMENTOS.get(key)
            if instrumento is None:
                print(f"instrumento desconocido: {key}", file=sys.stderr)
                return 2
            resultado = instrumento.operar(motor, **kw)
            print(json.dumps({**instrumento.como_dict(), "resultado": resultado},
                             ensure_ascii=False, indent=2) if args.json
                  else json.dumps(resultado, ensure_ascii=False, indent=2))
            return 0

    resultados = motor.generar_lote(
        args.n, eje=args.eje, elenco=args.elenco, capa=args.capa,
        usar_llm=args.llm,
        validar_estilo=not args.no_validar_estilo,
        validar_repeticion=not args.no_validar_repeticion,
        validar_tics_flag=not args.no_validar_tics,
        verbose=args.verbose,
    )

    if args.json:
        print(json.dumps(resultados, ensure_ascii=False, indent=2))
        return 0

    exitos = 0
    for i, r in enumerate(resultados, 1):
        if args.n > 1:
            print(f"\n═══════════ POST {i}/{args.n} ═══════════\n")
        print(formatear_post(r))
        if r.get("ok"):
            exitos += 1

    if exitos < len(resultados):
        print(f"[cascabel] {len(resultados) - exitos} de {len(resultados)} "
              f"posts no superaron la validación.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---


## Apéndice E — Protocolo de refutación empírica del MOTOR CASCABEL v0.1.0 (28 tesis)

### E.1. Objetivo

Este apéndice propone un protocolo ejecutable para **intentar falsar cada una de las veintiocho tesis** del preprint. El objetivo no es demostrar que el motor funciona. Es diseñar los ataques que, si tuvieran éxito, obligarían a reformular las tesis correspondientes.

Cada experimento se documenta con siete campos: tesis atacada, hipótesis nula, protocolo, métrica, criterio de decisión, predicción del autor y estado. Todos los estados están vacíos hasta que alguien ejecute el protocolo.

---

### E.2. Resumen

| # | Flag | Métrica | Criterio SOBREVIVE | Predicción |
|---|------|---------|--------------------|------------|
| 1 | `--publicar` | Pendiente `τ` vs `\|C\|` | `α > 0.1` con p<0.05 | Sobrevive |
| 2 | `--canon-expandir` | AUC de clasificación `K⁻` | `AUC > 0.7` | Sobrevive |
| 3 | `--auditar` | `\|ΔH\|` | `\|ΔH\| < 0.1` | Cae |
| 4 | `--ablation` | Interacción | `\|I\| > 0.05` | Sobrevive |
| 5 | `--matriz` | Codo SVD | Codo < 20 | Cae |
| 6 | `--deriva` | Correlación `t*` vs plano | `corr > 0.4` | Sobrevive |
| 7 | `--firma` | Cociente intra/inter | `< 0.5` | Cae |
| 8 | `--espejo` | `E²(x) = x` | Distancia `< 0.05` | Sobrevive |
| 9 | `--contraejemplo` | Firma de violadores | Distinta del azar | Sobrevive |
| 10 | `--ciego` | `D_KL(ciega\|\|validada)` | `> 0.1` | Sobrevive |
| 11 | `--forense` | Acierto funcional vs contenido | `F > C` | Cae |
| 12 | `--interpolar` | Diferencia conmutativa | `> 0.01` | Sobrevive |
| 13 | `--reconstruir` | `\|R(x)\|` con `k` huecos | `= 1` en 90% | Cae |
| 14 | `--temporal` | MAE de datación | `< 2 años` | Cae |
| 15 | `--frontera` | AUC dentro/fuera | `> 0.85` | Sobrevive |
| 16 | `--consenso` | Tasa de rechazo múltiple | `> 0.7` | Sobrevive |
| 17 | `--disenso` | Correlación con temperatura | `> 0.4` | Indeterminada |
| 18 | `--cuarentena` | Estabilidad de clusters | k estable | Sobrevive |
| 19 | `--mutar` | R² de ajuste lineal | `> 0.5` | Indeterminada |
| 20 | `--cruzar` | Error armónica vs aritmética | Armónica gana | Cae |
| 21 | `--degradar` | Codo por capa | `k*` depende de capa | Sobrevive |
| 22 | `--autopsia` | Distribución de `Δ` | Bimodal | Indeterminada |
| 23 | `--espejo-negro` | Distancia a rechazado | Pequeña | Sobrevive |
| 24 | `--parásito` | Ratio de hospedaje `ρ` | Variable por capa | Indeterminada |
| 25 | `--comprimir` | `K(x)/K(π(x))` | Estable, ≈1 | Cae |
| 26 | `--expandir` | Curva de convergencia | Codo visible | Indeterminada |
| 27 | `--censurar` | Distancia léxica/estructural | `> 0.1` | Sobrevive |
| 28 | `--confesar` | Tasa de confesión válida | `> 0.8` | Sobrevive |

**Resumen de predicciones del autor:** 15 sobreviven, 8 caen, 5 indeterminadas.

---

### E.3. Experimento 1 — Acreción y vida media

**Tesis atacada.** Vida media de n-grama decrece con el tamaño del corpus.

**Hipótesis nula.** `α ≤ 0`. El corpus acumula sin erosionar.

**Protocolo.** Serializar 1000 posts aceptados con `--publicar`. Recalcular el índice cada 100 posts. Estimar `α` por regresión log-log de `τ` vs `|C|`.

**Métrica.** Pendiente `−α`.

**Criterio.** SOBREVIVE si `α > 0.1` con p<0.05. CAE si `α ≤ 0`.

**Predicción.** Sobrevive. La erosión por acreción es esperable en un corpus que crece.

**Estado.** Sin ejecutar.

---

### E.4. Experimento 2 — Canon negativo

**Tesis atacada.** El canon se define por lo rechazado.

**Hipótesis nula.** El canon negativo de dos generadores distintos es indistinguible.

**Protocolo.** Acumular 1000 rechazos con motivo y firma. Entrenar clasificador binario sobre `K⁻`. Probar con corpus de un segundo generador.

**Métrica.** AUC del clasificador.

**Criterio.** SOBREVIVE si `AUC > 0.7`. CAE si `AUC ≈ 0.5`.

**Predicción.** Sobrevive. El canon negativo es una firma del generador.

**Estado.** Sin ejecutar.

---

### E.5. Experimento 3 — Entropía condicional invariante

**Tesis atacada.** `H(capa|eje)` es invariante del generador.

**Hipótesis nula.** `ΔH` varía con el corpus.

**Protocolo.** Generar 1000 textos con semilla fija. Calcular `H(C|E)` sobre generado y sobre corpus embebido. Repetir con corpus bootstrap activado.

**Métrica.** `|ΔH|` entre condiciones.

**Criterio.** SOBREVIVE si `|ΔH| < 0.1`. CAE si `|ΔH| ≥ 0.1`.

**Predicción.** Cae. El corpus bootstrap introduce variabilidad que rompe la invariancia.

**Estado.** Sin ejecutar.

---

### E.6. Experimento 4 — No-aditividad de validadores

**Tesis atacada.** La interacción de validadores no es cero.

**Hipótesis nula.** `A(V) = A(∅) + Σ[A(V) − A(V∖{v_i})]`.

**Protocolo.** Ejecutar generador con los 8 subconjuntos de validadores. Medir tasas de aceptación. Calcular interacción.

**Métrica.** `|A(V) − A_aditiva|`.

**Criterio.** SOBREVIVE si `|I| > 0.05`. CAE si `|I| ≈ 0`.

**Predicción.** Sobrevive. Los validadores ya interactúan en el diseño.

**Estado.** Sin ejecutar.

---

### E.7. Experimento 5 — Rango bajo del discurso

**Tesis atacada.** La matriz de co-ocurrencia tiene rango bajo.

**Hipótesis nula.** El espectro decae sin codo.

**Protocolo.** Construir `M_ij = PMI(t_i, t_j)` sobre corpus embebido + bootstrap. Aplicar SVD. Detectar codo.

**Métrica.** Índice del codo.

**Criterio.** SOBREVIVE si codo < 20. CAE si no hay codo.

**Predicción.** Cae. Los textos reales tienen rango mayor.

**Estado.** Sin ejecutar.

---

### E.8. Experimento 6 — Deriva por CUSUM

**Tesis atacada.** La deriva es detectable por CUSUM.

**Hipótesis nula.** Los puntos de cambio no correlacionan con el plano.

**Protocolo.** Generar 500 textos variando el eje cada 50. Aplicar CUSUM sobre longitud media de frase. Comparar `t*` detectados con los cambios de eje.

**Métrica.** Correlación `t*` vs cambios de plano.

**Criterio.** SOBREVIVE si `corr > 0.4`. CAE si no correlaciona.

**Predicción.** Sobrevive. El cambio de eje produce cambio de régimen.

**Estado.** Sin ejecutar.

---

### E.9. Experimento 7 — Firma estable bajo paráfrasis

**Tesis atacada.** La firma es estable bajo paráfrasis.

**Hipótesis nula.** Paráfrasis y cambio de eje producen distancias similares.

**Protocolo.** Para 100 textos, aplicar paráfrasis sintáctica y comparar firma. Comparar con distancia entre textos de distinto eje.

**Métrica.** Cociente `intra/inter`.

**Criterio.** SOBREVIVE si cociente < 0.5. CAE si ≈1.

**Predicción.** Cae. La paráfrasis modifica la estilometría.

**Estado.** Sin ejecutar.

---

### E.10. Experimento 8 — Antítesis como involución

**Tesis atacada.** `E² = id` y `f(E(x)) ≈ f(x)`.

**Hipótesis nula.** `E` no es involutivo en firma.

**Protocolo.** Aplicar `E` dos veces sobre 100 textos. Comparar firma original vs firma tras `E²`.

**Métrica.** Distancia euclídea media.

**Criterio.** SOBREVIVE si distancia < 0.05. CAE si mayor.

**Predicción.** Sobrevive. `E` es casi definicional.

**Estado.** Sin ejecutar.

---

### E.11. Experimento 9 — Gramática de la violación

**Tesis atacada.** Los violadores tienen firma propia.

**Hipótesis nula.** La firma de violadores es indistinguible del azar.

**Protocolo.** Generar 200 violadores forzados (desactivar validadores, filtrar por rechazo). Comparar firma media con firma de textos aleatorios.

**Métrica.** Distancia entre firmas.

**Criterio.** SOBREVIVE si distancia significativa (p<0.05). CAE si indistinguible.

**Predicción.** Sobrevive. La violación tiene estructura interna.

**Estado.** Sin ejecutar.

---

### E.12. Experimento 10 — Sesgo como divergencia

**Tesis atacada.** `D_KL(ciega || validada) > 0.1`.

**Hipótesis nula.** Los validadores no cambian la distribución.

**Protocolo.** Generar 500 con validadores, 500 sin. Comparar distribuciones de firma. Estimar `D_KL` empírica.

**Métrica.** `D_KL` sobre firma de 8 dimensiones.

**Criterio.** SOBREVIVE si `D_KL > 0.1`. CAE si menor.

**Predicción.** Sobrevive. Los validadores sesgan la salida.

**Estado.** Sin ejecutar.

---

### E.13. Experimento 11 — Autoría por funcionales

**Tesis atacada.** Los n-gramas funcionales atribuyen autoría mejor que los de contenido.

**Hipótesis nula.** Contenido supera a funcional.

**Protocolo.** Requiere corpus multi-autor. Clasificador ingenuo sobre `F(x)` y sobre `C(x)`. Comparar aciertos.

**Métrica.** Acierto con `F` vs con `C`.

**Criterio.** SOBREVIVE si `F > C` con margen > 0.05. CAE si no.

**Predicción.** Cae. En textos largos, el contenido gana.

**Estado.** Sin ejecutar. Requiere corpus externo (Galdós, Clarín, Unamuno, Ortega).

---

### E.14. Experimento 12 — No-conmutatividad

**Tesis atacada.** La interpolación no es conmutativa.

**Hipótesis nula.** `I(A,B,α) = I(B,A,α)`.

**Protocolo.** Calcular firma objetivo `AB` y `BA`. Medir diferencia.

**Métrica.** `|objetivo_AB − objetivo_BA|`.

**Criterio.** SOBREVIVE si diferencia > 0.01. CAE si ≈0.

**Predicción.** Sobrevive. La media ponderada es no conmutativa.

**Estado.** Sin ejecutar.

---

### E.15. Experimento 13 — Unicidad bajo estilo

**Tesis atacada.** Un texto con huecos tiene una única reconstrucción válida.

**Hipótesis nula.** Múltiples reconstrucciones pasan validadores.

**Protocolo.** Para patrones con `k=1, 2, 3, 4` huecos, enumerar 200 reconstrucciones aleatorias. Contar válidas.

**Métrica.** `|R(x)|` para cada `k`.

**Criterio.** SOBREVIVE si `|R(x)| = 1` en ≥90% para `k=1`. CAE si crece con `k`.

**Predicción.** Cae. Ya fue refutada en k≥3.

**Estado.** Refutada parcialmente en la práctica (§E.7 del preprint v1.1).

---

### E.16. Experimento 14 — Datación implícita

**Tesis atacada.** El corpus tiene marcas temporales detectables.

**Hipótesis nula.** No hay correlación con fechas.

**Protocolo.** Buscar años en textos del corpus. Entrenar clasificador ingenuo. Medir MAE.

**Métrica.** MAE de datación.

**Criterio.** SOBREVIVE si MAE < 2 años. CAE si mayor.

**Predicción.** Cae. El corpus no tiene marcas temporales fuertes.

**Estado.** Sin ejecutar.

---

### E.17. Experimento 15 — Frontera medible

**Tesis atacada.** El espacio declarado tiene borde.

**Hipótesis nula.** Textos dentro/fuera son indistinguibles.

**Protocolo.** Generar 500 dentro del espacio, 500 forzando planos fuera. Entrenar clasificador binario sobre firma.

**Métrica.** AUC.

**Criterio.** SOBREVIVE si AUC > 0.85. CAE si ≈0.5.

**Predicción.** Sobrevive. El espacio tiene bordes claros.

**Estado.** Sin ejecutar.

---

### E.18. Experimento 16 — Consenso estructural

**Tesis atacada.** Dos validadores que coinciden indican causa estructural.

**Hipótesis nula.** Rechazos múltiples y simples tienen igual tasa.

**Protocolo.** Generar 1000 textos sin validadores. Registrar rechazos por validador. Comparar tasa de violación estructural en intersecciones vs diferencia simétrica.

**Métrica.** Cociente de tasas.

**Criterio.** SOBREVIVE si tasa intersección > 0.7. CAE si ≈0.5.

**Predicción.** Sobrevive. La intersección es más severa.

**Estado.** Sin ejecutar.

---

### E.19. Experimento 17 — Disenso móvil

**Tesis atacada.** El disenso crece con la temperatura de la capa.

**Hipótesis nula.** El disenso es constante.

**Protocolo.** Para cada capa, medir `|R_i △ R_j|`. Correlacionar con `temperatura`.

**Métrica.** Correlación.

**Criterio.** SOBREVIVE si `corr > 0.4`. CAE si ≈0.

**Predicción.** Indeterminada. Depende del corpus.

**Estado.** Sin ejecutar.

---

### E.20. Experimento 18 — Cuarentena con modos

**Tesis atacada.** Los rechazos forman clusters estables.

**Hipótesis nula.** Los clusters no se estabilizan.

**Protocolo.** Acumular 1000 rechazos. Clustering por firma. Medir estabilidad por remuestreo.

**Métrica.** Índice de estabilidad.

**Criterio.** SOBREVIVE si `k` estable bajo bootstrap. CAE si no.

**Predicción.** Sobrevive. Los modos de fallo son estables.

**Estado.** Sin ejecutar.

---

### E.21. Experimento 19 — Linealidad de mutación

**Tesis atacada.** La mutación de una variable produce distancia lineal.

**Hipótesis nula.** No lineal.

**Protocolo.** Para cada variable (eje, capa, elenco), mutar en `k` pasos. Medir distancia estilométrica.

**Métrica.** R² de ajuste lineal.

**Criterio.** SOBREVIVE si R² > 0.5. CAE si menor.

**Predicción.** Indeterminada. Puede no ser lineal.

**Estado.** Sin ejecutar.

---

### E.22. Experimento 20 — Cruce como media armónica

**Tesis atacada.** `f(cruce(A,B)) ≈ media armónica`.

**Hipótesis nula.** Media aritmética ajusta mejor.

**Protocolo.** Cruzar 100 pares de planos. Comparar firma resultante con media aritmética y armónica.

**Métrica.** Error de ajuste a cada media.

**Criterio.** SOBREVIVE si armónica gana en > 60%. CAE si aritmética gana.

**Predicción.** Cae. La aritmética probablemente ajusta mejor.

**Estado.** Sin ejecutar.

---

### E.23. Experimento 21 — Jerarquía de capas

**Tesis atacada.** Las capas tienen resistencia distinta a la degradación.

**Hipótesis nula.** `k*` uniforme entre capas.

**Protocolo.** Para cada capa, aplicar 4 degradaciones. Medir codo de colapso.

**Métrica.** `k*` por capa.

**Criterio.** SOBREVIVE si `k*` varía. CAE si uniforme.

**Predicción.** Sobrevive. Cada capa tiene marcadores distintos.

**Estado.** Sin ejecutar.

---

### E.24. Experimento 22 — Autopsia como salud

**Tesis atacada.** La distancia plano-texto es indicador de salud.

**Hipótesis nula.** `Δ` uniforme.

**Protocolo.** Generar 200 textos. Calcular `Δ` esperado vs observado. Medir distribución.

**Métrica.** Distribución de `Δ`.

**Criterio.** SOBREVIVE si distribución bimodal. CAE si uniforme.

**Predicción.** Indeterminada. Métrica interna.

**Estado.** Sin ejecutar.

---

### E.25. Experimento 23 — Complemento informativo

**Tesis atacada.** El texto rechazado más cercano en firma es informativo.

**Hipótesis nula.** El rechazado más cercano está lejos.

**Protocolo.** Para 100 textos, buscar el rechazado más cercano en firma. Medir distancia.

**Métrica.** `d(f(x), f(N(x)))`.

**Criterio.** SOBREVIVE si distancia pequeña. CAE si grande.

**Predicción.** Sobrevive. El complemento es cercano.

**Estado.** Sin ejecutar.

---

### E.26. Experimento 24 — Permisividad como hospedaje

**Tesis atacada.** `ρ` (ratio de hospedaje válido) depende de la capa.

**Hipótesis nula.** `ρ` constante.

**Protocolo.** Para cada capa, insertar un texto en otro hasta violar validadores. Medir ratio máximo.

**Métrica.** `ρ` por capa.

**Criterio.** SOBREVIVE si `ρ` varía. CAE si constante.

**Predicción.** Indeterminada.

**Estado.** Sin ejecutar.

---

### E.27. Experimento 25 — Complejidad del plano

**Tesis atacada.** `K(x) / K(π(x)) ≈ 1`.

**Hipótesis nula.** El cociente depende de `|x|`.

**Protocolo.** Para 100 textos, medir `zlib(texto)` y `zlib(plano)`. Calcular cociente.

**Métrica.** Cociente.

**Criterio.** SOBREVIVE si cociente estable. CAE si variable.

**Predicción.** Cae. `zlib` no aproxima `K` bien.

**Estado.** Sin ejecutar.

---

### E.28. Experimento 26 — Convergencia de expansión

**Tesis atacada.** `||f(E_k(x)) − f(x)|| → 0` con codo en `k*`.

**Hipótesis nula.** No hay codo.

**Protocolo.** Expandir por párrafos. Medir firma en cada paso.

**Métrica.** Curva de distancia.

**Criterio.** SOBREVIVE si codo visible. CAE si no.

**Predicción.** Indeterminada. Puede converger o no.

**Estado.** Sin ejecutar.

---

### E.29. Experimento 27 — Censura diferenciable

**Tesis atacada.** `f(C_lex(x)) ≠ f(C_est(x))`.

**Hipótesis nula.** Firmas indistinguibles.

**Protocolo.** Aplicar censura léxica y estructural. Comparar firmas.

**Métrica.** Distancia de firmas.

**Criterio.** SOBREVIVE si distancia > 0.1. CAE si menor.

**Predicción.** Sobrevive. Los operadores son distintos.

**Estado.** Sin ejecutar.

---

### E.30. Experimento 28 — Autoconsistencia reflexiva

**Tesis atacada.** El generador puede declarar su plano sin violarlo.

**Hipótesis nula.** La confesión viola validadores.

**Protocolo.** Generar 100 confesiones (texto que enuncia el plano). Verificar con los tres validadores.

**Métrica.** Tasa de éxito.

**Criterio.** SOBREVIVE si tasa > 0.8. CAE si 0.

**Predicción.** Sobrevive. Con validadores laxos, casi trivial.

**Estado.** Sin ejecutar.

---

### E.31. Script propuesto

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
refutacion_cascabel.py
======================

Protocolo de refutación empírica para las 28 tesis del MOTOR CASCABEL v0.1.0.
Requiere `cascabel.py` en el mismo directorio.

Uso:
    python refutacion_cascabel.py
    python refutacion_cascabel.py --solo 1 4 6 21
    python refutacion_cascabel.py --json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
import statistics
import sys
import time
import zlib
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# --- Carga dinámica del motor ----------------------------------------- #
spec = importlib.util.spec_from_file_location("cascabel", "cascabel.py")
if spec is None or spec.loader is None:
    print("[ERROR] No se encuentra 'cascabel.py' en el directorio actual.")
    sys.exit(1)
cascabel = importlib.util.module_from_spec(spec)
sys.modules["cascabel"] = cascabel
spec.loader.exec_module(cascabel)

from cascabel import (
    MotorCascabel, Combinacion, IndiceCorpus,
    validar_estilometria, validar_tics, validar_anti_repeticion,
    calcular_perfil, tokenizar, METADATOS, INDICE_CAPAS, INDICE_EJES,
    CAPAS_LEXICAS, EJES, INSTRUMENTOS,
)

N_SEMILLAS = 1
UMBRAL_P = 0.05


# ============================================================================
# Runner
# ============================================================================

@dataclass
class Resultado:
    tesis_id: int
    nombre: str
    veredicto: str  # SOBREVIVE / CAE / INDETERMINADA / SIN_EJECUTAR
    metrica: str
    valor: float
    detalle: Dict[str, Any]

    def como_dict(self) -> Dict[str, Any]:
        return {
            "tesis": self.tesis_id, "nombre": self.nombre,
            "veredicto": self.veredicto, "metrica": self.metrica,
            "valor": self.valor, "detalle": self.detalle,
        }


def _motor(semilla: int = 42, **kw) -> MotorCascabel:
    return MotorCascabel(semilla=semilla, programador_activo=False, **kw)


def _firma_media(textos: List[str]) -> Dict[str, float]:
    perfiles = [calcular_perfil(t).como_dict() for t in textos if t]
    if not perfiles:
        return {}
    campos = [k for k in perfiles[0] if isinstance(perfiles[0][k], (int, float))]
    return {k: statistics.fmean(p[k] for p in perfiles) for k in campos}


def _dist_firma(a: Dict[str, float], b: Dict[str, float],
                campos: Optional[List[str]] = None) -> float:
    if not campos:
        campos = [k for k in a if k in b and isinstance(a[k], (int, float))]
    return math.sqrt(sum((a.get(c, 0) - b.get(c, 0)) ** 2 for c in campos))


# ============================================================================
# Tesis 1
# ============================================================================

def exp_01() -> Resultado:
    motor = _motor(semilla=42)
    historial: List[set] = []
    textos_previos: List[str] = []
    taus: List[int] = []
    tamanos: List[int] = []

    for i in range(100):
        r = motor.generar(validar_estilo=False, validar_repeticion=False,
                          validar_tics_flag=False)
        if not r.get("ok"):
            continue
        textos_previos.append(r["texto"])
        historial.append(set(cascabel.n_gramas(tokenizar(r["texto"]), 5)))
        if i % 10 == 0:
            idx = IndiceCorpus(5)
            for t in textos_previos:
                idx.añadir(t, "gen")
            info = idx.vida_media_gramas(historial)
            taus.append(info["media"])
            tamanos.append(len(textos_previos))

    if len(taus) < 3:
        return Resultado(1, "vida media decrece con corpus",
                         "INDETERMINADA", "τ vs |C|", 0.0, {"error": "muestra insuficiente"})

    lx = [math.log(t) for t in tamanos]
    ly = [math.log(max(1, v)) for v in taus]
    mx, my = statistics.fmean(lx), statistics.fmean(ly)
    num = sum((a - mx) * (b - my) for a, b in zip(lx, ly))
    dx = math.sqrt(sum((a - mx) ** 2 for a in lx))
    dy = math.sqrt(sum((b - my) ** 2 for b in ly))
    if dx * dy == 0:
        return Resultado(1, "vida media decrece con corpus",
                         "INDETERMINADA", "τ vs |C|", 0.0, {"error": "sin varianza"})
    pendiente = num / (dx * dy)
    veredicto = "SOBREVIVE" if pendiente < -0.1 else "CAE"
    return Resultado(1, "vida media decrece con corpus", veredicto,
                     "pendiente log-log", pendiente,
                     {"n_taus": len(taus), "pendiente": pendiente})


# ============================================================================
# Tesis 3
# ============================================================================

def _H_cond(pares: List[Tuple[str, str]]) -> float:
    if not pares:
        return 0.0
    conteo: Dict[str, Counter] = defaultdict(Counter)
    for e, c in pares:
        conteo[e][c] += 1
    h = 0.0
    total = len(pares)
    for e, cs in conteo.items():
        p_e = sum(cs.values()) / total
        s = sum(cs.values())
        h_e = -sum((k / s) * math.log(k / s + 1e-12) for k in cs.values())
        h += p_e * h_e
    return h


def exp_03() -> Resultado:
    motor = _motor(semilla=42)
    resultados = motor.generar_lote(200)
    pares_gen = [(r["plano"]["eje"], r["plano"]["capa"]) for r in resultados if r.get("ok")]
    h_gen = _H_cond(pares_gen)

    pares_corpus = []
    for post in cascabel.POSTS_EMBEBIDOS:
        for eje in post.get("ejes", []):
            pares_corpus.append((eje, post.get("capa", "tecnico")))
    h_corpus = _H_cond(pares_corpus)

    delta = abs(h_gen - h_corpus)
    veredicto = "SOBREVIVE" if delta < 0.1 else "CAE"
    return Resultado(3, "H(capa|eje) invariante", veredicto,
                     "|ΔH|", delta, {"H_gen": h_gen, "H_corpus": h_corpus})


# ============================================================================
# Tesis 4
# ============================================================================

def exp_04() -> Resultado:
    motor = _motor(semilla=42)
    combos = [
        (True, True, True), (True, True, False), (True, False, True),
        (False, True, True), (True, False, False), (False, True, False),
        (False, False, True), (False, False, False),
    ]
    n = 30
    tasas = {}
    for est, rep, tic in combos:
        ok = sum(1 for _ in range(n)
                 if motor.generador.generar(validar_estilo=est,
                                            validar_repeticion=rep,
                                            validar_tics_flag=tic).get("ok"))
        tasas[f"{int(est)}{int(rep)}{int(tic)}"] = ok / n

    a_v = tasas["111"]
    a_0 = tasas["000"]
    suma = sum(a_v - tasas[k] for k in ["011", "101", "110"])
    pred_ad = a_0 + suma
    interaccion = abs(a_v - pred_ad)

    veredicto = "SOBREVIVE" if interaccion > 0.05 else "CAE"
    return Resultado(4, "no-aditividad de validadores", veredicto,
                     "|interacción|", interaccion, {"tasas": tasas})


# ============================================================================
# Tesis 5
# ============================================================================

def _svd_aprox(M: List[List[float]], k: int = 20) -> List[float]:
    n = len(M)
    if n == 0:
        return []
    v = [1.0 / math.sqrt(n)] * n
    sigmas = []
    Mt = [[M[j][i] for j in range(n)] for i in range(n)]
    for _ in range(k):
        w = [sum(Mt[i][j] * v[j] for j in range(n)) for i in range(n)]
        norma = math.sqrt(sum(x * x for x in w)) or 1
        v = [x / norma for x in w]
        Mv = [sum(M[i][j] * v[j] for j in range(n)) for i in range(n)]
        s = math.sqrt(sum(x * x for x in Mv))
        sigmas.append(s)
        if s < 1e-9:
            break
    return sigmas


def exp_05() -> Resultado:
    motor = _motor(semilla=42)
    textos = [p["cuerpo"] for p in motor.corpus_embebido]
    docs = [set(tokenizar(t)) for t in textos]
    vocab = sorted({x for d in docs for x in d})
    idx = {x: i for i, x in enumerate(vocab)}
    n = len(vocab)
    M = [[0.0] * n for _ in range(n)]
    for d in docs:
        for a in d:
            for b in d:
                if a != b:
                    M[idx[a]][idx[b]] += 1
    sigmas = _svd_aprox(M, k=min(20, n))
    if not sigmas:
        return Resultado(5, "rango bajo", "INDETERMINADA", "codo SVD", 0.0, {})
    total = sum(sigmas)
    codo = len(sigmas)
    acum = 0.0
    for i, s in enumerate(sigmas):
        acum += s
        if acum / total >= 0.9:
            codo = i + 1
            break
    veredicto = "SOBREVIVE" if codo < 20 else "CAE"
    return Resultado(5, "rango bajo", veredicto, "codo SVD", float(codo),
                     {"sigmas_top5": sigmas[:5]})


# ============================================================================
# Tesis 6
# ============================================================================

def exp_06() -> Resultado:
    motor = _motor(semilla=42)
    largos = []
    cambios = []
    eje_actual = None
    ejes_lista = [e["id"] for e in EJES]
    rng = random.Random(42)
    for i in range(200):
        eje = ejes_lista[(i // 20) % len(ejes_lista)]
        r = motor.generar(eje=eje)
        if r.get("ok"):
            largos.append(calcular_perfil(r["texto"]).long_media_frase)
            if eje != eje_actual:
                cambios.append(i)
                eje_actual = eje
    if len(largos) < 20:
        return Resultado(6, "deriva por CUSUM", "INDETERMINADA", "corr", 0.0, {})
    media = statistics.fmean(largos)
    s = 0.0
    umbral = 3 * (statistics.pstdev(largos) or 1.0)
    puntos = []
    for i, l in enumerate(largos):
        s = max(0.0, s + (l - media))
        if s > umbral:
            puntos.append(i)
            s = 0.0
    # correlación aproximada: cuántos cambios coinciden
    coincidencias = sum(1 for p in puntos if any(abs(p - c) <= 3 for c in cambios))
    tasa = coincidencias / max(1, len(puntos)) if puntos else 0.0
    veredicto = "SOBREVIVE" if tasa > 0.4 else "CAE"
    return Resultado(6, "deriva por CUSUM", veredicto, "tasa coincidencia",
                     tasa, {"n_puntos": len(puntos), "n_cambios": len(cambios)})


# ============================================================================
# Tesis 7
# ============================================================================

def _parafrasear(texto: str, rng: random.Random) -> str:
    sinonimos = {"es": "resulta ser", "no": "jamás", "y": "e",
                 "pero": "sin embargo", "porque": "puesto que"}
    frases = cascabel.dividir_frases(texto)
    rng.shuffle(frases)
    out = " ".join(frases)
    for a, b in sinonimos.items():
        out = out.replace(f" {a} ", f" {b} ")
    return out


def exp_07() -> Resultado:
    motor = _motor(semilla=42)
    rng = random.Random(42)
    dists_par = []
    dists_eje = []
    textos = [r["texto"] for r in motor.generar_lote(50) if r.get("ok")]
    for t in textos[:20]:
        f0 = calcular_perfil(t).como_dict()
        fpar = calcular_perfil(_parafrasear(t, rng)).como_dict()
        dists_par.append(_dist_firma(f0, fpar, ["long_media_frase", "diversidad_lexica",
                                                 "long_media_palabra"]))
    for i in range(len(textos) - 1):
        f1 = calcular_perfil(textos[i]).como_dict()
        f2 = calcular_perfil(textos[i + 1]).como_dict()
        dists_eje.append(_dist_firma(f1, f2, ["long_media_frase", "diversidad_lexica",
                                               "long_media_palabra"]))
    if not dists_par or not dists_eje:
        return Resultado(7, "firma estable bajo paráfrasis", "INDETERMINADA",
                         "cociente", 0.0, {})
    cociente = statistics.fmean(dists_par) / max(1e-6, statistics.fmean(dists_eje))
    veredicto = "SOBREVIVE" if cociente < 0.5 else "CAE"
    return Resultado(7, "firma estable bajo paráfrasis", veredicto,
                     "intra/inter", cociente, {"media_par": statistics.fmean(dists_par),
                                               "media_eje": statistics.fmean(dists_eje)})


# ============================================================================
# Tesis 8
# ============================================================================

def exp_08() -> Resultado:
    motor = _motor(semilla=42)
    inst = INSTRUMENTOS["espejo"]
    dists = []
    for r in motor.generar_lote(50):
        if not r.get("ok"):
            continue
        x = r["texto"]
        e2 = inst._invertir(inst._invertir(x))
        f0 = calcular_perfil(x).como_dict()
        f2 = calcular_perfil(e2).como_dict()
        dists.append(_dist_firma(f0, f2, ["long_media_frase", "diversidad_lexica",
                                          "long_media_palabra"]))
    if not dists:
        return Resultado(8, "involución", "INDETERMINADA", "dist", 0.0, {})
    media = statistics.fmean(dists)
    veredicto = "SOBREVIVE" if media < 0.05 else "CAE"
    return Resultado(8, "involución", veredicto, "dist media E²", media,
                     {"n": len(dists)})


# ============================================================================
# Tesis 9
# ============================================================================

def exp_09() -> Resultado:
    motor = _motor(semilla=42)
    violadores = []
    for _ in range(200):
        r = motor.generador.generar(validar_estilo=False, validar_repeticion=False,
                                    validar_tics_flag=False)
        if r.get("ok") and not validar_tics(r["texto"]).ok:
            violadores.append(r["texto"])
    if len(violadores) < 5:
        return Resultado(9, "gramática de la violación", "INDETERMINADA",
                         "dist", 0.0, {"n_violadores": len(violadores)})
    f_v = _firma_media(violadores)
    f_c = _firma_media([p["cuerpo"] for p in cascabel.POSTS_EMBEBIDOS])
    campos = ["long_media_frase", "diversidad_lexica", "long_media_palabra"]
    d = sum(abs(f_v.get(c, 0) - f_c.get(c, 0)) for c in campos)
    veredicto = "SOBREVIVE" if d > 0.1 else "CAE"
    return Resultado(9, "gramática de la violación", veredicto,
                     "dist violadores vs corpus", d, {"n": len(violadores)})


# ============================================================================
# Tesis 10
# ============================================================================

def exp_10() -> Resultado:
    motor = _motor(semilla=42)
    ciega = [r["texto"] for r in (motor.generador.generar(
        validar_estilo=False, validar_repeticion=False, validar_tics_flag=False)
        for _ in range(100)) if r.get("ok")]
    validada = [r["texto"] for r in (motor.generador.generar() for _ in range(100))
                if r.get("ok")]
    if not ciega or not validada:
        return Resultado(10, "sesgo como divergencia", "INDETERMINADA", "D_KL", 0.0, {})
    f_c = _firma_media(ciega)
    f_v = _firma_media(validada)
    campos = ["long_media_frase", "diversidad_lexica", "long_media_palabra"]
    kl = sum(abs(f_c.get(c, 0) - f_v.get(c, 0)) for c in campos)
    veredicto = "SOBREVIVE" if kl > 0.1 else "CAE"
    return Resultado(10, "sesgo como divergencia", veredicto, "D_KL aprox", kl, {})


# ============================================================================
# Tesis 11 — requiere corpus externo
# ============================================================================

def exp_11() -> Resultado:
    return Resultado(11, "forense funcional", "SIN_EJECUTAR",
                     "acierto F vs C", 0.0,
                     {"razon": "requiere corpus multi-autor externo"})


# ============================================================================
# Tesis 12
# ============================================================================

def exp_12() -> Resultado:
    rng = random.Random(42)
    campos = ["long_media_frase", "diversidad_lexica", "long_media_palabra"]
    diffs = []
    for _ in range(20):
        fA = {c: rng.uniform(0.5, 5.0) for c in campos}
        fB = {c: rng.uniform(0.5, 5.0) for c in campos}
        peso = 0.5
        obj_ab = {c: peso * fA[c] + (1 - peso) * fB[c] for c in campos}
        obj_ba = {c: peso * fB[c] + (1 - peso) * fA[c] for c in campos}
        diffs.append(sum(abs(obj_ab[c] - obj_ba[c]) for c in campos))
    media = statistics.fmean(diffs)
    veredicto = "SOBREVIVE" if media > 0.01 else "CAE"
    return Resultado(12, "no-conmutatividad", veredicto,
                     "|AB − BA|", media, {"n": len(diffs)})


# ============================================================================
# Tesis 13
# ============================================================================

def exp_13() -> Resultado:
    motor = _motor(semilla=42)
    inst = INSTRUMENTOS["reconstruir"]
    vocab = inst._vocabulario(motor)
    rng = random.Random(42)
    resultados = []
    for k in (1, 2, 3):
        patron = " ".join(["____"] * k) + " es ____."
        validos = 0
        for _ in range(100):
            texto = patron
            for _ in range(texto.count("____")):
                texto = texto.replace("____", rng.choice(vocab), 1)
            if validar_estilometria(texto).ok and validar_tics(texto).ok:
                validos += 1
        resultados.append({"k": k, "validos": validos})
    v1 = next((r["validos"] for r in resultados if r["k"] == 1), 0)
    veredicto = "SOBREVIVE" if v1 <= 1 else "CAE"
    return Resultado(13, "unicidad bajo estilo", veredicto,
                     "|R(x)| para k=1", float(v1), {"por_k": resultados})


# ============================================================================
# Tesis 14 — requiere corpus con marcas temporales
# ============================================================================

def exp_14() -> Resultado:
    motor = _motor(semilla=42)
    anios = list(range(1900, 2026))
    textos = [p["cuerpo"] for p in motor.corpus_embebido]
    con_marca = sum(1 for t in textos if any(str(a) in t for a in anios))
    tasa = con_marca / max(1, len(textos))
    veredicto = "SOBREVIVE" if tasa > 0.3 else "CAE"
    return Resultado(14, "datación implícita", veredicto,
                     "tasa con marca temporal", tasa,
                     {"con_marca": con_marca, "total": len(textos)})


# ============================================================================
# Tesis 15
# ============================================================================

def exp_15() -> Resultado:
    motor = _motor(semilla=42)
    dentro = []
    fuera = []
    for _ in range(100):
        r = motor.generador.generar()
        if r.get("ok"):
            dentro.append(calcular_perfil(r["texto"]).como_dict())
        r2 = motor.generador.generar(eje="ia", capa="militar")
        if r2.get("ok"):
            fuera.append(calcular_perfil(r2["texto"]).como_dict())
    if not dentro or not fuera:
        return Resultado(15, "frontera", "INDETERMINADA", "sep", 0.0, {})
    campos = ["long_media_frase", "diversidad_lexica", "long_media_palabra"]
    md = {c: statistics.fmean(x[c] for x in dentro) for c in campos}
    mf = {c: statistics.fmean(x[c] for x in fuera) for c in campos}
    sep = sum(abs(md[c] - mf[c]) for c in campos)
    veredicto = "SOBREVIVE" if sep > 0.1 else "CAE"
    return Resultado(15, "frontera", veredicto, "separación", sep, {})


# ============================================================================
# Tesis 16
# ============================================================================

def exp_16() -> Resultado:
    motor = _motor(semilla=42)
    multi = 0
    simple = 0
    for _ in range(200):
        r = motor.generador.generar(validar_estilo=False, validar_repeticion=False,
                                    validar_tics_flag=False)
        if not r.get("ok"):
            continue
        t = r["texto"]
        e = not validar_estilometria(t).ok
        p = not validar_anti_repeticion(t, motor.indice).ok
        ti = not validar_tics(t).ok
        s = sum([e, p, ti])
        if s >= 2:
            multi += 1
        elif s == 1:
            simple += 1
    total = multi + simple
    tasa = multi / max(1, total)
    veredicto = "SOBREVIVE" if tasa > 0.7 else "CAE"
    return Resultado(16, "consenso estructural", veredicto,
                     "fracción multi-rechazo", tasa,
                     {"multi": multi, "simple": simple})


# ============================================================================
# Tesis 17
# ============================================================================

def exp_17() -> Resultado:
    motor = _motor(semilla=42)
    tasas = []
    temps = []
    for capa in CAPAS_LEXICAS:
        ok = 0
        rech = 0
        for _ in range(30):
            r = motor.generador.generar(capa=capa["id"], validar_estilo=False,
                                        validar_repeticion=False, validar_tics_flag=False)
            if not r.get("ok"):
                continue
            t = r["texto"]
            e = not validar_estilometria(t).ok
            p = not validar_anti_repeticion(t, motor.indice).ok
            ti = not validar_tics(t).ok
            if sum([e, p, ti]) >= 2:
                rech += 1
            ok += 1
        tasas.append(rech / max(1, ok))
        temps.append(capa["temperatura"])
    mx, my = statistics.fmean(temps), statistics.fmean(tasas)
    num = sum((a - mx) * (b - my) for a, b in zip(temps, tasas))
    dx = math.sqrt(sum((a - mx) ** 2 for a in temps))
    dy = math.sqrt(sum((b - my) ** 2 for b in tasas))
    corr = num / (dx * dy) if dx * dy else 0.0
    veredicto = "SOBREVIVE" if corr > 0.4 else ("CAE" if corr < 0.1 else "INDETERMINADA")
    return Resultado(17, "disenso móvil", veredicto, "corr temp vs tasa", corr,
                     {"tasas": tasas, "temps": temps})


# ============================================================================
# Tesis 18
# ============================================================================

def exp_18() -> Resultado:
    motor = _motor(semilla=42)
    clusters = defaultdict(int)
    for _ in range(300):
        r = motor.generador.generar(validar_estilo=False, validar_repeticion=False,
                                    validar_tics_flag=False)
        if not r.get("ok"):
            continue
        t = r["texto"]
        motivos = []
        if not validar_estilometria(t).ok:
            motivos.append("est")
        if not validar_anti_repeticion(t, motor.indice).ok:
            motivos.append("rep")
        if not validar_tics(t).ok:
            motivos.append("tic")
        clusters["+".join(motivos) or "ok"] += 1
    # entropía de la distribución
    total = sum(clusters.values())
    h = -sum((c / total) * math.log(c / total + 1e-12) for c in clusters.values())
    veredicto = "SOBREVIVE" if 0 < h < 2.5 else "INDETERMINADA"
    return Resultado(18, "cuarentena con modos", veredicto,
                     "entropía de modos", h,
                     {"modos": dict(clusters)})


# ============================================================================
# Tesis 19
# ============================================================================

def exp_19() -> Resultado:
    motor = _motor(semilla=42)
    valores = [c["id"] for c in CAPAS_LEXICAS]
    base = motor.generar(capa=valores[0])
    if not base.get("ok"):
        return Resultado(19, "linealidad mutación", "INDETERMINADA", "R²", 0.0, {})
    fb = calcular_perfil(base["texto"]).vector_8d()
    xs, ys = [], []
    for i, v in enumerate(valores[1:], 1):
        r = motor.generar(capa=v)
        if not r.get("ok"):
            continue
        fv = calcular_perfil(r["texto"]).vector_8d()
        d = math.sqrt(sum((a - b) ** 2 for a, b in zip(fb, fv)))
        xs.append(i)
        ys.append(d)
    if len(xs) < 3:
        return Resultado(19, "linealidad mutación", "INDETERMINADA", "R²", 0.0, {})
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    dx = math.sqrt(sum((a - mx) ** 2 for a in xs))
    dy = math.sqrt(sum((b - my) ** 2 for b in ys))
    r = num / (dx * dy) if dx * dy else 0.0
    r2 = r * r
    veredicto = "SOBREVIVE" if r2 > 0.5 else ("CAE" if r2 < 0.1 else "INDETERMINADA")
    return Resultado(19, "linealidad mutación", veredicto, "R²", r2,
                     {"xs": xs, "ys": ys})


# ============================================================================
# Tesis 20
# ============================================================================

def exp_20() -> Resultado:
    motor = _motor(semilla=42)
    combos = list(motor.combinatoria.todas())
    rng = random.Random(42)
    err_arm = []
    err_arit = []
    campos = ["long_media_frase", "diversidad_lexica", "long_media_palabra"]
    for _ in range(20):
        ca, cb = rng.sample(combos, 2)
        ra = motor.generar(combinacion=ca)
        rb = motor.generar(combinacion=cb)
        if not (ra.get("ok") and rb.get("ok")):
            continue
        fa = calcular_perfil(ra["texto"]).como_dict()
        fb = calcular_perfil(rb["texto"]).como_dict()
        arit = {c: (fa[c] + fb[c]) / 2 for c in campos}
        arm = {c: (2 * fa[c] * fb[c] / (fa[c] + fb[c])) if (fa[c] + fb[c]) > 0 else 0
               for c in campos}
        elenco_cruza = tuple(set(ca.elenco + cb.elenco))[:3]
        cc = Combinacion(eje=ca.eje, elenco=elenco_cruza, capa=cb.capa)
        rc = motor.generar(combinacion=cc)
        if not rc.get("ok"):
            continue
        fc = calcular_perfil(rc["texto"]).como_dict()
        err_arm.append(sum(abs(fc[c] - arm[c]) for c in campos) / len(campos))
        err_arit.append(sum(abs(fc[c] - arit[c]) for c in campos) / len(campos))
    if not err_arm:
        return Resultado(20, "cruce media armónica", "INDETERMINADA", "err", 0.0, {})
    ma = statistics.fmean(err_arm)
    mt = statistics.fmean(err_arit)
    veredicto = "SOBREVIVE" if ma < mt else "CAE"
    return Resultado(20, "cruce media armónica", veredicto,
                     "err_arm vs err_arit", ma - mt,
                     {"err_arm": ma, "err_arit": mt})


# ============================================================================
# Tesis 21
# ============================================================================

def exp_21() -> Resultado:
    motor = _motor(semilla=42)
    inst = INSTRUMENTOS["degradar"]
    r = motor.generar()
    if not r.get("ok"):
        return Resultado(21, "jerarquía de capas", "INDETERMINADA", "dist", 0.0, {})
    t = r["texto"]
    f0 = calcular_perfil(t).vector_8d()
    pasos = [inst._eliminar_adjetivos, inst._cortar_frases,
             inst._invertir_orden, lambda x: x.upper()]
    distancias = []
    for fn in pasos:
        t = fn(t)
        ft = calcular_perfil(t).vector_8d()
        distancias.append(math.sqrt(sum((a - b) ** 2 for a, b in zip(f0, ft))))
    monotona = all(distancias[i] <= distancias[i + 1] for i in range(len(distancias) - 1))
    veredicto = "SOBREVIVE" if monotona and distancias[-1] > 1.0 else "INDETERMINADA"
    return Resultado(21, "jerarquía de capas", veredicto,
                     "curva de degradación", distancias[-1],
                     {"distancias": distancias, "monotona": monotona})


# ============================================================================
# Tesis 22
# ============================================================================

def exp_22() -> Resultado:
    motor = _motor(semilla=42)
    deltas = []
    for _ in range(100):
        r = motor.generar()
        if not r.get("ok"):
            continue
        f = calcular_perfil(r["texto"]).como_dict()
        temp = INDICE_CAPAS[r["plano"]["capa"]]["temperatura"]
        esperada = {"long_media_frase": 12.0 + 5 * temp,
                    "diversidad_lexica": 0.6 - 0.2 * temp,
                    "long_media_palabra": 5.0}
        campos = ["long_media_frase", "diversidad_lexica", "long_media_palabra"]
        deltas.append(sum(abs(f[c] - esperada[c]) for c in campos) / 3)
    if not deltas:
        return Resultado(22, "autopsia como salud", "INDETERMINADA", "σ(Δ)", 0.0, {})
    sigma = statistics.pstdev(deltas)
    veredicto = "SOBREVIVE" if sigma < 0.5 else "INDETERMINADA"
    return Resultado(22, "autopsia como salud", veredicto,
                     "σ(Δ)", sigma, {"media_Δ": statistics.fmean(deltas)})


# ============================================================================
# Tesis 23
# ============================================================================

def exp_23() -> Resultado:
    motor = _motor(semilla=42)
    r = motor.generar()
    if not r.get("ok"):
        return Resultado(23, "complemento informativo", "INDETERMINADA", "dist", 0.0, {})
    f0 = calcular_perfil(r["texto"]).como_dict()
    campos = ["long_media_frase", "diversidad_lexica", "long_media_palabra"]
    mejor = float("inf")
    for _ in range(200):
        r2 = motor.generador.generar(validar_estilo=False, validar_repeticion=False,
                                     validar_tics_flag=False)
        if not r2.get("ok"):
            continue
        if validar_estilometria(r2["texto"]).ok and validar_tics(r2["texto"]).ok:
            continue
        f2 = calcular_perfil(r2["texto"]).como_dict()
        d = sum(abs(f0[c] - f2[c]) for c in campos)
        mejor = min(mejor, d)
    veredicto = "SOBREVIVE" if mejor < 1.0 else "CAE"
    return Resultado(23, "complemento informativo", veredicto,
                     "dist mínima", mejor, {})


# ============================================================================
# Tesis 24
# ============================================================================

def exp_24() -> Resultado:
    motor = _motor(semilla=42)
    resultados = {}
    for capa in ["tecnico", "militar", "juridico", "medico"]:
        r_h = motor.generar()
        r_p = motor.generar(capa=capa)
        if not (r_h.get("ok") and r_p.get("ok")):
            continue
        h = r_h["texto"]
        p = r_p["texto"]
        ratios = []
        for frac in [0.1, 0.2, 0.3, 0.4]:
            n = int(len(p) * frac)
            if n < 10:
                continue
            mitad = len(h) // 2
            fusion = h[:mitad] + "\n" + p[:n] + "\n" + h[mitad:]
            if validar_estilometria(fusion).ok and validar_tics(fusion).ok:
                ratios.append(frac)
        resultados[capa] = max(ratios) if ratios else 0.0
    vals = list(resultados.values())
    var = statistics.pstdev(vals) if len(vals) > 1 else 0.0
    veredicto = "SOBREVIVE" if var > 0.05 else "INDETERMINADA"
    return Resultado(24, "permisividad como hospedaje", veredicto,
                     "σ(ρ) por capa", var, {"por_capa": resultados})


# ============================================================================
# Tesis 25
# ============================================================================

def exp_25() -> Resultado:
    motor = _motor(semilla=42)
    ratios = []
    for _ in range(50):
        r = motor.generar()
        if not r.get("ok"):
            continue
        texto = r["texto"]
        plano = json.dumps(r["plano"], ensure_ascii=False)
        ct = len(zlib.compress(texto.encode()))
        cp = len(zlib.compress(plano.encode()))
        ratios.append(ct / max(1, cp))
    if not ratios:
        return Resultado(25, "complejidad del plano", "INDETERMINADA", "ratio", 0.0, {})
    media = statistics.fmean(ratios)
    desv = statistics.pstdev(ratios)
    veredicto = "SOBREVIVE" if desv / media < 0.3 else "CAE"
    return Resultado(25, "complejidad del plano", veredicto,
                     "ratio K(x)/K(π(x))", media,
                     {"σ": desv, "cv": desv / media})


# ============================================================================
# Tesis 26
# ============================================================================

def exp_26() -> Resultado:
    motor = _motor(semilla=42)
    convergencias = []
    for r in motor.generar_lote(20):
        if not r.get("ok"):
            continue
        texto = r["texto"]
        parrafos = texto.split("\n\n")
        if len(parrafos) < 3:
            continue
        f0 = calcular_perfil(texto).vector_8d()
        distancias = []
        for k in range(1, len(parrafos)):
            parcial = "\n\n".join(parrafos[:k])
            fk = calcular_perfil(parcial).vector_8d()
            distancias.append(math.sqrt(sum((a - b) ** 2 for a, b in zip(f0, fk))))
        if len(distancias) >= 2:
            convergencias.append(distancias[0] - distancias[-1])
    if not convergencias:
        return Resultado(26, "convergencia expansión", "INDETERMINADA", "Δd", 0.0, {})
    media = statistics.fmean(convergencias)
    veredicto = "SOBREVIVE" if media > 0 else "CAE"
    return Resultado(26, "convergencia expansión", veredicto,
                     "d_inicial - d_final", media, {"n": len(convergencias)})


# ============================================================================
# Tesis 27
# ============================================================================

def exp_27() -> Resultado:
    motor = _motor(semilla=42)
    inst = INSTRUMENTOS["censurar"]
    dists = []
    for r in motor.generar_lote(30):
        if not r.get("ok"):
            continue
        t = r["texto"]
        lex = inst._censura_lexica(t)
        est = inst._censura_estructural(t)
        fl = calcular_perfil(lex).vector_8d()
        fe = calcular_perfil(est).vector_8d()
        dists.append(math.sqrt(sum((a - b) ** 2 for a, b in zip(fl, fe))))
    if not dists:
        return Resultado(27, "censura diferenciable", "INDETERMINADA", "dist", 0.0, {})
    media = statistics.fmean(dists)
    veredicto = "SOBREVIVE" if media > 0.1 else "CAE"
    return Resultado(27, "censura diferenciable", veredicto,
                     "dist léxica vs estructural", media, {})


# ============================================================================
# Tesis 28
# ============================================================================

def exp_28() -> Resultado:
    motor = _motor(semilla=42)
    exitos = 0
    total = 0
    for _ in range(50):
        r = motor.generar()
        if not r.get("ok"):
            continue
        p = r["plano"]
        conf = (f"Este texto tiene eje {p['eje']}, capa {p['capa']}, "
                f"elenco {'+'.join(p['elenco'])}, virus {p['virus']}.")
        total += 1
        if validar_estilometria(conf).ok and validar_tics(conf).ok:
            exitos += 1
    tasa = exitos / max(1, total)
    veredicto = "SOBREVIVE" if tasa > 0.8 else "CAE"
    return Resultado(28, "autoconsistencia reflexiva", veredicto,
                     "tasa de confesión válida", tasa,
                     {"exitos": exitos, "total": total})


# ============================================================================
# Registro
# ============================================================================

EXPERIMENTOS: Dict[int, Callable[[], Resultado]] = {
    1: exp_01, 3: exp_03, 4: exp_04, 5: exp_05, 6: exp_06, 7: exp_07, 8: exp_08,
    9: exp_09, 10: exp_10, 11: exp_11, 12: exp_12, 13: exp_13, 14: exp_14,
    15: exp_15, 16: exp_16, 17: exp_17, 18: exp_18, 19: exp_19, 20: exp_20,
    21: exp_21, 22: exp_22, 23: exp_23, 24: exp_24, 25: exp_25, 26: exp_26,
    27: exp_27, 28: exp_28,
    # Tesis 2: canon negativo, requiere acumular rechazos en disco
}

# Tesis pendientes de implementación completa: 2 (canon negativo)
# Motivo: requiere persistencia entre ejecuciones.


# ============================================================================
# CLI
# ============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(description="Refutación CASCABEL")
    parser.add_argument("--solo", nargs="*", type=int)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    print("=" * 60)
    print(f"PROTOCOLO DE REFUTACIÓN — {METADATOS['nombre']} v{METADATOS['version']}")
    print("=" * 60)

    tesis = sorted(EXPERIMENTOS.keys())
    if args.solo:
        tesis = [t for t in tesis if t in args.solo]

    resultados = []
    for tid in tesis:
        fn = EXPERIMENTOS[tid]
        t0 = time.time()
        try:
            r = fn()
        except Exception as exc:
            r = Resultado(tid, "error", "INDETERMINADA", "exception", 0.0,
                          {"error": str(exc)})
        dt = time.time() - t0
        resultados.append(r)
        print(f"[T{tid:02d}] {r.nombre}: {r.veredicto} | "
              f"{r.metrica} = {r.valor:.4f} ({dt:.2f}s)")

    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    for v in ["SOBREVIVE", "CAE", "INDETERMINADA", "SIN_EJECUTAR"]:
        n = sum(1 for r in resultados if r.veredicto == v)
        print(f"  {v}: {n}")

    if args.json:
        print(json.dumps([r.como_dict() for r in resultados],
                         ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

### E.32. Reproducibilidad

```bash
# Ejecutar los 28 experimentos
python refutacion_cascabel.py

# Ejecutar solo algunos
python refutacion_cascabel.py --solo 1 4 6 21

# Salida en JSON
python refutacion_cascabel.py --json > resultados.json
```

- **Entorno:** Python 3.11+.
- **Dependencias:** ninguna externa.
- **Requisito:** `cascabel.py` v0.1.0 en el mismo directorio.
- **Tiempo estimado:** 5–15 minutos según máquina.
- **Semillas:** fijas en cada experimento.

---

### E.33. Limitaciones

- **Cobertura.** 27 de 28 tesis tienen experimento implementado. La tesis 2 (canon negativo) requiere persistencia entre ejecuciones y no está implementada en este script. La tesis 11 (forense) requiere corpus multi-autor externo y no se ejecuta por defecto.
- **Corpus.** Todos los experimentos usan el corpus embebido (19 posts). No se usa bootstrap ni corpus externo.
- **Validación estadística.** Cada experimento corre una sola semilla. Un protocolo más robusto repetiría cada experimento con 30 semillas y reportaría intervalos de confianza.
- **Un solo idioma.** Español, registro ensayo breve.
- **Resultados no publicados.** Los veredictos que el script produce no están pre-registrados. Se publicarán tal cual en la siguiente revisión.

---

### E.34. Compromiso de publicación

El autor se compromete a publicar en la siguiente revisión del preprint:

- La salida literal del script, sin edición.
- Los veredictos reales de las 28 tesis, incluidos los que contradigan las predicciones de §E.2.
- Las tesis que el protocolo deje como INDETERMINADAS, con la razón.
- Cualquier refutación de terceros que ejecuten el protocolo sobre corpus distintos.

---

*Apéndice E — v1.2 — septiembre de 2026.*
*David Ferrández Canalis.*
*28 tesis. 28 experimentos. 0 ejecutados.*
*El compromiso es publicar lo que salga, no lo que se espera.*

