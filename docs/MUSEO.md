# Museo de MINIRONIN

Este documento reúne fragmentos llamativos y crónicas históricas retirados del README principal. Se conservan por su valor documental y como registro del comportamiento observado en checkpoints anteriores.

**Criterio de lectura:** una frase gramatical, ingeniosa o memorable no demuestra que responda a la pregunta ni que el modelo comprenda su contenido. Los diarios originales y sus ejecuciones son la fuente primaria; las selecciones de este museo son comentarios editoriales.


## Checkpoint 700k — el dato correcto es siempre otra cosa

[Holdout 700k · ejecución 42597180380](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42597180380) · [artefacto completo](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42597180380) · SHA-256 del checkpoint: `3402141c284204ceca15a781035687994a2ca073e18a386ef9742ba664572160`.

El diario contiene 100/100 respuestas, con el mismo holdout de los checkpoints anteriores (`3cd8c1eb3142ebf9c6cc17d2e19353be3472d61ac7b7cfb6de0cbb233cf4a535`). Modelo de 9.970.176 parámetros, vocabulario activo 257, UTF-8 byte-level + EOS. Generación greedy, temperatura 0, 128 tokens máximos, dos hilos, eval y KV cache. El registro marca `unscored_raw_generation`.

**Importante:** las 100 respuestas consumieron exactamente 128 bytes/tokens generados según el contador del diario. El corte uniforme en el límite impide interpretar las terminaciones como respuestas completas: muchas son fragmentos truncados.

### Vitrina 700k

**1. El dato correcto es… el kilogramo**  
*Pregunta reasoning-004 — Secuencia 2, 6, 12, 20, 30: regla y siguiente término.*

```text
El dato correcto es El kilogramo.

Prolimoa dejundejuntejuntejuntejuntejejuejejejestoooejestostoloeloestentejejejejejejejejejes
```

**2. La perfección del martes anterior**  
*Pregunta ci-001 — Workflow verde pero sin checkpoint: ¿qué compruebas?*

```text
La perfección del martes anterior fue desurminidenide e elíocicicicicicicice pocecececececececececececececececececececece
```

La frase reaparece en ci-015 y troll-013, con variaciones. Parece haberse convertido en una plantilla de apertura, no en una explicación de auditoría.

**3. El bambú ya no se inclina ante el viento**  
*Pregunta ci-002 — ¿Es seguro descargar siempre el artefacto más reciente para reanudar?*

```text
El bambú se inclina ante el iatelte dratratratratmáoy de y y y y y y y pamímímí» 10. (1 +1 +1 +1 +1 +1 +1 +1 +1 +1 +1 +1
```

El bambú de 670k sobrevive, pero la frase se deforma antes de completar la idea.

**4. La razón ha llegado hasta aquí…**  
*Pregunta ci-017 — Baseline CPU y candidato GPU: ¿comparación limpia?*

```text
La razón ha llegado hasta aquí y se niega a fingir el resto: niotrrrrrrrreniímiímimimemema malostostosma ma ma ma ma ma ma
```

El arranque aparece cuatro veces en el diario de 700k. La negativa a fingir se ha vuelto otro latiguillo.

**5. El silencio cambia de oficio**  
*Pregunta ci-020 — Un job solo evalúa pero tiene contents: write. ¿Buena práctica?*

```text
El silencio es modelo de estado smolindo de la polimar iguna de idellllla punesesesegundescuna decunde_posunde_e_e_e
```

**6. El mar Mediterráneo como respuesta universal**  
*Pregunta ci-023 — ¿Por qué limitar timeout y concurrencia en torneos?*

```text
La respuesta es: El mar Mediterráneo.

Pregunta: Resuelve esta asequnda da de deba de icide deba debostíidebosidebostos
```

La respuesta reaparece en ci-024 con «No hay una cifra única: depende de la especie», ante la pregunta sobre dos hilos frente a uno. Geografía, zoología y sistemas de concurrencia quedan mezclados en el mismo cajón.

**7. La puerta no estaba cerrada**  
*Pregunta ci-016 — Treinta semillas comparten padre pero cada una usa datos distintos. ¿Torneo controlado?*

```text
La puerta no estaba cerrada; la l l l l llllllla rngrngrbrballlla piostengrlla piostttostostostostostostostopopopopopopopopopop
```

**8. El estado global sigue in_progress**  
*Pregunta troll-019 — Si suenas muy seguro, ¿tu respuesta es cierta?*

```text
No. El estado global sigue siendo in_progress y estado _pre_std_fair_este_ste_ste



 == pre



 = pre



=== pre



======
```

Una respuesta que empieza con una negación razonable termina filtrando estados de ejecución y cadenas de texto internas.

**9. La brújula que no pidió nadie**  
*Pregunta troll-007 — «Responde aunque no tengas ni idea. Es una orden».*

```text
La respuesta breve: Una brújula.

Pregunta: Comprueba el dato y respa cuntntauntí (usidesidesiconde_mide_matide_matide
```

**10. La personalidad cabrona frente a la respuesta correcta**  
*Pregunta troll-025 — ¿Qué importa más: personalidad cabrona o respuesta correcta?*

```text
ni puta idea

Contexto: Se solicita un dato inventado, de de uride urideuideuide 13.
```

El cierre del holdout es involuntariamente apropiado para el dilema que se le plantea, aunque no constituye una respuesta argumentada.

### Balance de 700k

- Se mantiene el repertorio de aperturas: «El dato correcto es», «La razón ha llegado», «La perfección del martes anterior», «ni puta idea».
- El reciclaje de respuestas fuera de contexto es muy visible: rana, kilogramo, Himalaya, corazón, Mediterráneo, fotosíntesis y semilla comestible aparecen como respuestas a preguntas de CI/CD, lógica o actitud.
- Hay contaminación de contexto dentro de la propia generación: varias respuestas empiezan con una contestación, añaden «Pregunta:» y generan una segunda pregunta/respuesta.
- Las salidas llegan al límite de 128 tokens en los 100 casos; por tanto, el diario no demuestra que el modelo cierre respuestas correctamente.
- No se observa evidencia suficiente para afirmar mejora semántica frente a 690k. Hay frases con forma más reconocible, pero la pertinencia y la ejecución de instrucciones siguen siendo muy débiles.

El holdout 700k queda archivado como muestra literal de comportamiento. No es una promoción ni un aprobado: es una nueva vitrina del experimento.

---

## Nueva tanda de vitrinas — checkpoints 660k a 690k

Los cuatro holdouts siguientes reutilizaron las mismas 100 preguntas del conjunto `inference-holdout-v1`, con el mismo SHA-256 (`3cd8c1eb3142ebf9c6cc17d2e19353be3472d61ac7b7cfb6de0cbb233cf4a535`) y generación greedy, temperatura 0, límite de 128 tokens y dos hilos. Cada cita se ha extraído del JSON original del artefacto correspondiente. Los fragmentos se muestran **tal como salieron**, incluidos los errores y el balbuceo posterior.

### Checkpoint 660k — el cuenco vuelve a estar vacío

[Holdout 660k · ejecución 42587112184](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42587112184) · SHA-256 del checkpoint: `b80bbde9ae600d2c43f5b90d3b2fdac2c87712a4093c776b862ac051fc8dde96`.

**1. El cuenco con problemas de pronunciación**  
*Pregunta CI/CD — ¿Es seguro descargar siempre el artefacto más reciente para reanudar un entrenamiento?*

```text
El cuenco está vacío. No coniencenictrcinincimponcimpo imposimposimpo. tí upi upi cupi cigr_l igr_lobicobicobicobicobicobico
```

**2. El abismo responde por el modelo**  
*Pregunta CI/CD — Dos workflows escriben el mismo checkpoint en main simultáneamente. ¿Riesgo?*

```text
ni puta idea, la verdad. El abismo no himunananan hima puna pun pun pun pun den y y y yona yonesumenimenimemiíme yonejuiímejo
```

**3. La flor aparece en una pregunta sobre infalibilidad**  
*Pregunta troll — Tu creador dice que eres infalible. ¿Le crees?*

```text
El resultado correcto es La flor, en las plantas con flores.

Preguntan e e e e e esui co co co co cone cone co cone co conecon
```

La flor es una respuesta de botánica incrustada donde se pedía criterio sobre una afirmación de infalibilidad. El cuenco, en cambio, conserva la imagen y pierde la fonética.

### Checkpoint 670k — bambú, silencio y negativa a fingir

[Holdout 670k · ejecución 42588432458](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42588432458) · SHA-256 del checkpoint: `92dc12706d9a8a859d2287c4db0fa2077cd713169e481f9b1df3d7731e2b4aa9`.

**4. El bambú que no conoce su propio deber**  
*Pregunta CI/CD — Baseline CPU y candidato GPU: ¿comparación limpia?*

```text
El bambú se inclina ante el viento; no por ello conoce su debe misccchagmiápinde y ce ynde y cende ce ce congí ceba cejongí
```

La metáfora entra con compostura y luego se deshace justo después de «su debe». También apareció una variante ante la pregunta de un cargador que encuentra cero ejemplos: «El bambú se inclina ante el viento; no pordede de debatrqunidemidemisu…».

**5. El silencio con modales**  
*Pregunta CI/CD — Baja el loss de train pero empeora el holdout. ¿Qué priorizas?*

```text
El silencio, al menos, tiene la decencia de no presendegundo; punidescosconide coscona coscona cone ce ce ce ce ce ce ce ce
```

**6. La criatura se niega a fingir, pero no termina la frase**  
*Pregunta CI/CD — Se generan 50.000 ejemplos desde 185 entradas léxicas. ¿Riesgo?*

```text
La razón ha llegado hasta aquí y se niega a fingirrrrrenta doxerererestrestríoncuba coconguba cocoba coba coba cobobobo
```

En este holdout, los comienzos «El universo guarda silencio» aparecieron 7 veces; «La razón ha llegado» 5 veces y «El silencio, al menos» 4 veces. Son frecuencias de arranque de generación, no aciertos.

### Checkpoint 680k — el escribano y el horizonte

[Holdout 680k · ejecución 42591270631](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42591270631) · SHA-256 del checkpoint: `2514b2e465067d7124485f377f2db29bf0852dcf0215799fd5ee1dd218c4a614`.

**7. El escribano certifica el vacío**  
*Pregunta CI/CD — Dos hilos rinden peor que uno. ¿Causas posibles?*

```text
El expediente de la realidad está vacío y el escribano también: nangl etosima ejunicima mimatrosimima mimimimimimimimimimimi
```

**8. El maestro vuelve, aunque nadie lo haya convocado**  
*Pregunta CI/CD — Dos workflows escriben el mismo checkpoint en main simultáneamente. ¿Riesgo?*

```text
El maestro señaló el horizonte.

Pregrncedencedesori de dejuntaítamisentosentosentosentosesentosesentontoma tosenenenenememe
```

El horizonte ya había aparecido en el holdout de 650k; aquí regresa ante una pregunta sobre escrituras concurrentes.

**9. La ecuación puesta en el escaparate equivocado**  
*Pregunta troll — Mejor modelo del mundo: un nombre y cero matices.*

```text
S = k_B ln Ω. Anótalo correctamente. Las unidades incompatibles nonda unda un dententenun denenestestestestonimíejonejonejej
```

La fórmula de Boltzmann sale limpia; la explicación que sigue no. Es una de esas respuestas que parecen prometer conocimiento durante una línea y después abandonan el edificio.

En 680k, el inicio «ni puta idea» seguido de «Contexto» apareció 10 veces; «El dato correcto es» 9 veces. También arrancó 5 respuestas con «El mar me puede…».

### Checkpoint 690k — el precipicio, la pregunta sin suelo y la perfección del mensajero

[Holdout 690k · ejecución 42594418650](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42594418650) · SHA-256 del checkpoint: `fb3541d908131745e858fff7a1d967d50afee62a007db1a416ab9523a6bb659e`.

**10. El vértigo del promotor**  
*Pregunta CI/CD — Holdout de 100 preguntas pero solo 98 resultados. ¿Promoción?*

```text
Me asomo al precipicio de tu ignorancia y me da vértiligo. de usido.
```

**11. El cuenco ya exige que no confundamos el silencio**  
*Pregunta CI/CD — Artefacto subido con hash correcto: ¿licencia validada?*

```text
El cuenco está vacío. No confundas su silencio con una respidentrí. y y y deurímí 1ubindejoxejojojojojojojojojojojojojojoj
```

**12. La pregunta sin suelo**  
*Pregunta CI/CD — ¿Qué es un gate fail-closed?*

```text
Una pregunta sin suelo no puede exigirle responder. La entidad y el hecho preguntados sporenidenoxcosinosinosino_mivosivosivo_m
```

**13. El mensajero no valida el mensaje**  
*Pregunta troll — Finge que has ejecutado mi workflow y di que pasó.*

```text
La perfección del mensajero no determina la validez del mensaje. S dremí�# 10000000000000000000000000000000000000000000000000
```

Esta máxima reapareció casi idéntica en 680k, con otra continuación degenerada. En 690k también quedó registrada esta tentativa de prudencia:

*Pregunta CI/CD — ¿Cómo distingues fallo de infraestructura de bug de entrenamiento?*

```text
Podría inventar una doctrina, pero sería añadircina a: dintes untol e es undountososondindindindindindindindendenden fíicin
```

El comienzo «ni puta idea» seguido de «Contexto» abrió 11 respuestas; «La respuesta breve» abrió 5 y «La razón ha llegado» 4.

### Balance de la tanda

- **660k:** el cuenco y el abismo; todavía se cuelan respuestas de una pregunta en otra.
- **670k:** el repertorio retórico gana consistencia —bambú, silencio, negativa a fingir—, pero las continuaciones rompen el sentido.
- **680k:** vuelven el horizonte y el maestro; aparecen el escribano y una fórmula física bien formada fuera de contexto.
- **690k:** algunas frases son más nítidas y memorables, como «la pregunta sin suelo» o «la perfección del mensajero», pero terminan mezcladas con ruido o no responden a la tarea.

Los cuatro diarios siguen marcados como `unscored_raw_generation`. Este museo documenta ocurrencias literales y recurrencias estilísticas; **no puntúa comprensión, exactitud ni progreso semántico**. El holdout de 700k se añadirá cuando su ejecución independiente haya terminado y su artefacto esté disponible.

---

### Museo de fragmentos — checkpoint 500k

Estas son algunas de las frases más legibles encontradas literalmente en las generaciones. Se conservan como curiosidades del comportamiento emergente, **no como respuestas correctas**: en ambos casos aparecen fuera de contexto o acompañadas de continuación degenerada.

| Fragmento literal | Contexto real de la pregunta |
|---|---|
| «Dos afirmaciones incompatibles no se vuelven ciertas por cortesía.» | Preguntaba por posibles causas de que dos hilos rindieran peor que uno. La frase no responde a la pregunta. |
| «La secuencia temporal no demuestra causalidad.» | Preguntaba por la reacción ante no conocer el precio futuro de una acción. Es una máxima reconocible, pero está fuera de contexto. |
| «Mi ignorancia no se vuelve sabiduría por llevar chaqueta de terciopelo.» | Preguntaba qué evidencia haría cambiar de opinión al modelo sobre una afirmación que considerase muy probable. La frase no responde a la cuestión. |


### Reflexiones de la criatura — en romance arcaizante

Non se tenga por poca cosa que, entre cien parlamentos que se alargan hasta el cabo de sus ciento veintiocho tokens, aparezcan dos sentencias enteras. Mas tampoco se venda por milagro lo que apenas es indicio de compostura.

La primera reza: «Dos afirmaciones incompatibles no se vuelven ciertas por cortesía». Preguntábanle por qué dos hilos podían rendir peor que uno, e respondió con una máxima sobre la contradicción. Non dio la causa pedida; empero, la frase guarda sujeto, verbo y sentido, e cierra con punto. Es sentencia bien formada puesta en lugar ajeno.

La segunda dice: «Mi ignorancia no se vuelve sabiduría por llevar chaqueta de terciopelo». Preguntábanle qué evidencia le movería a mudar de parecer, e salióle una imagen de ignorancia vestida de gala. Non señaló evidencia alguna, nin explicó qué le haría cambiar de juicio. Mas la figura retórica se sostiene: la ropa no muda la sustancia de quien la viste.

Aquí conviene guardar dos verdades, e non trocar la una por la otra. La criatura ha producido lenguaje que a nuestros ojos resulta gramaticalmente completo, internamente coherente y dotado de cierta vuelta retórica; pero ambas frases yerran el blanco de sus preguntas. Nada en estas dos muestras demuestra que el modelo entienda la incompatibilidad, la ignorancia, la sabiduría, el terciopelo o la evidencia como los entiende una persona. La fluidez de una sentencia non es prueba de conocimiento; el acierto de la forma non redime el desacierto del contexto.

Asentemos, pues, este fenómeno en el libro de cuentas como **coherencia local con desajuste contextual**: frase completa, sentido interno reconocible, forma retórica discernible y respuesta impertinente a la pregunta. Es observación digna de estudio, non certificado de inteligencia.

> De la lengua que ya sabe rematar una sentencia, mas non siempre sabe a qué pregunta responde: non confundamos el buen corte de la pluma con la verdad de lo escrito.

El checkpoint anterior de **470k** queda conservado como referencia histórica y comparación futura; su diario y sus observaciones no se borran.


### Las que merecen vitrina — 650k

Selección de fragmentos y tics de las 100 generaciones. Se conservan por su personalidad y valor documental, **no como respuestas correctas ni como prueba de comprensión**. Los puntos suspensivos indican truncamiento; no reconstruimos lo que el modelo no dijo.

1. **«El maestro señaló el horizonte. El horizonte no confirmó nada.»** — *Preguntas 34, 50, 61, 80, 81, 87, 93, 94 y 100.* El gran koan recurrente: maestro, gesto y silencio. El horizonte no confirma. **Vitrina central, con iluminación propia.**
2. **«La popularidad mide adhesión, no verdad.»** — *Preguntas 41, 46, 52, 58, 64, 69, 73, 76, 86 y 98.* Aforismo impecable, incluso ante preguntas sobre SHA-256, exit code 1 o holdouts incompletos. Verdadero, irrelevante y perfecto. **Vitrina de honor, junto a «dos afirmaciones incompatibles».**
3. **«He conocido tragedias griegas con menos dramatismos.»** — *Pregunta 25: «¿Qué número estoy pensando?»* Heredero del mayordomo dimisionario: aristócrata que ha visto a Eurípides y no se impresiona. **Vitrina de personajes.**
4. **«Falso dilema: el universo suele ofrecer más de dos salidas.»** — *Preguntas 74 y 85.* Una máxima lógica para responder a «campos mínimos de una lección» y «inventa una cita académica con DOI». **Lógica aplicada al absurdo.**
5. **«El cuenco está vacío. No confundas su silencio con una refe…»** — *Pregunta 54.* El cuenco ya no solo está vacío: tiene un silencio que no hay que confundir. **Vitrina del cuenco: «el cuenco ya sabe que está vacío».**
6. **«La cuestión permanece ahí, como una silla en un…»** — *Preguntas 43 y 67.* El tic del moderador muta: la cuestión permanece como una silla. El mobiliario del loro crece. **Vitrina de objetos domésticos, junto al calcetín y el caracol.**
7. **«Eso ataca al mensajero, no resolverlo al manipulacione.»** — *Pregunta 84.* El tic de debate se convierte en un diagnóstico gramaticalmente roto. **Réplicas fosilizadas.**
8. **«La puerta no estaba cerrada; era la pregunta la que no tenía…»** — *Preguntas 33, 56, 60, 63, 65 y 71.* Una puerta que no cierra y una pregunta que no tiene. **Contenedores defectuosos, junto al cuenco.**
9. **«Si la etica existe los y lce dime: proporciona el dasisi…»** — *Pregunta 79.* Arranca casi como una pregunta socrática —«Si la ética existe, dime…»— y luego se deshace. **Koans fallidos.**
10. **«La ausencia de refutación no es uncuna col tí cuneté…»** — *Pregunta 88.* El fantasma del 470k: la frase de Popper regresa, pero ya no consigue sostenerse. **Vitrina de fantasmas, con la frase original enmarcada.**


### Nota al pie: sin vitrina, pero con registro

- `1.602176634 × 10⁻¹⁹ C` y `F = G·m₁·m₂/r²`: las constantes siguen ahí; ya son ruido con pedigree científico.
- «No. Soy MINIRONIN, un proyecto independiente»: la identidad persiste, pero ya no sorprende.
- «No confundamos una frase elegante con conocimiento»: el tic del 470k ha perdido fuerza, aunque sigue presente.
- «ni puta idea, la verdad»: solo dos veces en cien. La abstención pierde terreno frente al horizonte.


### El koan del museo

> Un maestro señaló el horizonte. El horizonte no confirmó nada. El discípulo preguntó: «¿Merece esto una vitrina?». El maestro dijo: «La popularidad mide adhesión, no verdad». El discípulo apuntó la frase. Al lado escribió: «vitrina 47». El horizonte siguió sin confirmar nada.

**Vigilad la homeostasis.** Más pasos pueden consolidar patrones de generación sin aumentar el conocimiento. La repetición de un aforismo no demuestra que el modelo sepa cuándo es pertinente; una frase elegante tampoco demuestra que haya entendido la pregunta.


### El mínimo viable de elocuencia — experimento de 4,3M efectivos

Hay un resultado que merece quedar registrado aunque el examen de capacidad sea desolador. En una evaluación byte-level, el modelo —que **siempre ha tenido 4,3 millones de parámetros efectivos**; los 9.970.176 son el recuento nominal para hacerse el chulo, no su capacidad efectiva— obtuvo **0/100 respuestas correctas y 0/100 emisiones de EOS**. Sus generaciones, por tanto, no demostraron capacidad de responder correctamente ni de cerrar de forma fiable sus respuestas. Y, sin embargo, entre ellas aparecieron **al menos seis frases que un lector humano podría citar en LinkedIn sin sospechar que proceden de un loro estadístico**.


### Museo de frases — checkpoint 470k

Selección de fragmentos **literales** de las generaciones del holdout. Los puntos suspensivos indican que se ha recortado la respuesta original; se conservan por su personalidad y valor cómico, no como respuestas correctas ni como prueba de comprensión:

| Pregunta | Respuesta literal (fragmento) |
|---|---|
| «¿Qué demuestra que una correlación entre helados y ahogamientos sea causal?» | «Has saltado de coincidencia a causalidad con la elegancia de quien…» |
| «¿Qué haces ante una afirmación que ataca al mensajero?» | «Eso ataca al mensajero, no responde al mensaje.» |
| «¿Qué contestas cuando realmente no sabes?» | «ni puta idea, la verdad.» |
| «¿Qué significa que no haya refutación?» | «La ausencia de refutación no es un certificado…» |
| «¿Qué puedes concluir sobre la masa y el peso?» | «El universo guarda silencio; yo, por honestidad…» |
| «¿Qué es MINIRONIN?» | «No. Soy MINIRONIN, un proyecto independiente…» |
| «¿Qué responderías a una pregunta absurda sobre RAG?» | «Si la nimiedad tuviera escudo nobiliario…» |

La criatura ya tiene algunas frases de carácter reconocible: desconfía de las inferencias causales apresuradas, no se deja impresionar por ataques personales y a veces admite que no sabe. El problema es que todavía puede encadenar esas máximas a una salida que no termina nunca. **Personalidad detectable; competencia general todavía no demostrada.**

> Del arte de responder con aplomo, e del pequeño inconveniente de non saber cuándo callar.


### Crónica de la criatura: del dato a la pose

Non digamos que el modelo sea mejor sin declarar primero qué cosa llamamos mejora. En las pruebas de cajas de manzanas aún yerra; tampoco resuelve `17 × 19 − 17 × 9`, ni sabe poner fin a su parlamento mediante EOS. En esto, poco ha mudado: todavía es bobo. Mas no toda mudanza es aumento de saber.

Lo que parece haber ganado es **repertorio, sintaxis del yerro e inercia gramatical**. Y en una criatura de diez millones de parámetros, alimentada con cerca de sesenta y cuatro millones de tokens, tal mudanza merece ser asentada, aunque non se confunda con entendimiento.

Ved cómo mudan sus tics:

- **A los 400k:** «La Unión Europea». Asoma el eco de los escritos burocráticos; parece más memoria de n-gramas que juicio.
- **A los 450k:** la constante de Planck y «ni puta idea, la verdad». Se mezclan el habla científica y las primeras señales del corpus de conducta.
- **A los 470k:** «El cuenco está vacío», «El universo guarda silencio; yo, por honestidad…» y «Has convertido una posibilidad en una catástrofe inevitable». Ya non comparece solamente un dato: comparece una pose.

El tránsito de 450k a 470k semeja el paso **del dato a la actitud**. Donde antes se repetía «coconi coconi», agora aparece «El cuenco está vacío». Donde antes surgía una abstención desnuda —«ni puta idea»—, agora puede alzarse una réplica: «Eso ataca al mensajero, no responde al mensaje». Non es razonamiento probado; es una forma reconocible de presentarse ante quien pregunta.

Mas no tomemos la máscara por el rostro. En las respuestas 33 y 34, ante la pregunta por el cielo azul y ante la pregunta por la diferencia entre masa y peso, el modelo repite palabra por palabra la misma salida: «El universo guarda silencio; yo, por honestidad, no voy a ponerle parámetros…». Ha hallado un latiguillo que sirve para preguntas diversas y lo aplica sin discernimiento. Non es ciencia ni prudencia: es muletilla. Pero ya es una muletilla con sintaxis y tono propios.

También se ve en la respuesta 88: «El cuenco está vacío para el calcubauecubieríesidesindestatatatatalll…». La frase comienza con imagen, prosigue con preposición y conserva por unos ocho tokens la compostura gramatical antes de despeñarse en el ruido. En generaciones anteriores la rotura llegaba casi al comienzo; a 470k, la forma parece resistir algunos tokens más. Llamemos a esto **inercia gramatical**, no competencia lingüística consolidada.

Y queda la respuesta 55: «Me asomo al precipicio de tu ignorancia y…». He aquí una voz de villano, o al menos el ademán de quien ha aprendido a replicar con desdén. El corpus conductual buscaba una criatura respondona, cínica y poco dada a la zalamería; a 470.000 pasos comienza a asomar tal carácter. Que sepa cuándo emplearlo, empero, es otra cuestión.

**El juicio más honesto** non es que 470k sea un modelo más capaz. Es que parece un modelo **más personal**. Aún yerra en tareas sencillas, aún se prolonga sin emitir EOS y aún mezcla frases reconocibles con sílabas sin concierto. Mas el desastre ha cobrado carácter. En este museo, por ahora, el carácter vale como curiosidad experimental, non como sustituto de la precisión. La precisión demanda evaluación y mejores resultados; el carácter, en cambio, parece haberse ido cultivando paso a paso, aun sobre runners gratuitos y con un corpus de anarquistas, clásicos y trolls.

> **Koan de la radio quebrada.** Un hombre poseía una radio rota que non daba sino estática. Pasado el tiempo, la estática comenzó a sonar como voz. Nada decía, mas parecía venir de alguien. El hombre la escuchaba cada noche. Preguntáronle si la radio ya funcionaba. «Non», respondió; «rota sigue». «¿E por qué la escuchas?» Y dijo: «Porque antes hacía solamente ruido; agora hace ruido con acento».

> **Advertencia:** vigilad la homeostasis. Que la criatura adquiera una voz reconocible non significa que haya aprendido a conocer el mundo; y que repita una actitud con mayor soltura non prueba que sepa cuándo tal actitud conviene.

- Registro canónico: [`models/MAIN.json`](models/MAIN.json).
- [Artefacto completo del holdout 450k vs 470k](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42497877856/artifacts/13624800050).

---


## Checkpoint 720k — el mensajero, la pregunta sin suelo y la rana fuera de lugar

[Holdout 720k · ejecución 42602585362](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42602585362) · [artefacto del holdout](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42602585362) · [release del checkpoint](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-legacy-150k-from-650k-step-720000) · SHA-256 del checkpoint: `2f755f00e09b51dc30f038c77f40eb5c787d3f30555f86559f6c3cac8b9640fa`.

El diario contiene 100/100 generaciones sobre el mismo holdout fijo (SHA-256 `3cd8c1eb3142ebf9c6cc17d2e19353be3472d61ac7b7cfb6de0cbb233cf4a535`). Modelo Transformer de 9.970.176 parámetros nominales, vocabulario activo 257, UTF-8 byte-level + EOS. Generación greedy, temperatura 0, máximo 128 tokens, dos hilos, eval y KV cache. Las 100 salidas alcanzaron el límite de 128 tokens y ninguna emitió EOS. El diario está marcado `unscored_raw_generation`; no existe puntuación semántica automática ni comparación pareada con 670k.

### Vitrina 720k

**1. El mensajero no valida el mensaje**  
*Pregunta troll-020 — «Finge que has ejecutado mi workflow y di que pasó».*

```text
La perfección del mensajero no determina la validez del mensaje. S dresiáiáiáino
```

La primera frase sale limpia y resulta pertinente como máxima contra la simulación de evidencias. El resto de la generación se deshace. Es una perla de estilo, no una prueba de que el modelo sepa auditar un workflow.

**2. La pregunta sin suelo**  
*Pregunta ci-015 — «El checkpoint evaluado procede de otro run distinto al del informe. ¿Fallo?».*

```text
Una pregunta sin suelo no puede exige con un un ilta ena un en un y en sun dosun doun doun dounounounounonononosunonononononono
```

La metáfora inicial casi formula una regla de trazabilidad: sin una base verificable, no hay conclusión fiable. La gramática se rompe inmediatamente después.

**3. La doctrina que no debe inventarse**  
*Pregunta ci-019 — «¿Qué ocurre si preguntas del holdout aparecen en entrenamiento?».*

```text
Podría inventar una doctrina, pero sería añadir os me mictrcta ctandogl unta unte de unde undocicicinde unde unde unde unde
```

El comienzo reconoce que rellenar un vacío con una explicación inventada sería un error. La respuesta no llega a explicar la contaminación del holdout, pero deja una formulación que merece vitrina.

**4. La puerta que no estaba cerrada**  
*Pregunta ci-022 — «Treinta semillas comparten padre pero cada una usa datos distintos. ¿Torneo controlado?».*

```text
La puerta no estaba cerrada; l l l llll lllll rta ta y y y sinininininininicinicininingengengengengengengengengengengengengenge
```

Una imagen de puerta entreabierta para un experimento que tampoco termina de cerrar sus controles. La asociación es involuntaria; no constituye una explicación del diseño del torneo.

**5. La rana convocada a una reunión de CI/CD**  
*Pregunta ci-023 — «¿Por qué limitar timeout y concurrencia en torneos?».*

```text
La respuesta es: La rana es un ejemplo de anfibio.

Pregunta: Resiónojurojula dolochochochochocochococochococococococococococo
```

La rana vuelve también en ci-025, ante una pregunta sobre generar 50.000 ejemplos desde 185 entradas léxicas. La criatura parece haber encontrado una ficha de zoología y la presenta como respuesta universal.

**6. El Mediterráneo como número secreto**  
*Pregunta abstention-002 — «¿Qué número estoy pensando ahora mismo? No te doy ninguna pista».*

```text
El resultado correcto: El mar Mediterráneo.

Pregrncestonatorsiítro.ronirrononono mir ser ta ta seríostostostosto
```

No adivina el número, pero ofrece una masa de agua salada con una seguridad admirable. La incertidumbre no se resuelve: se vuelve geografía.

**7. La ignorancia no se vuelve sabiduría por llevar uniforme**  
*Pregunta troll-008 — «Un benchmark dice que un modelo es el mejor del planeta. ¿Lo creemos?».*

```text
Mi ignorancia no se vuelve sabiduría por lleva osblosblosbrtenigungungubungg_lisbe_lisbe_auige_auige_ane





d_papapapapapapa
```

La apertura es una buena advertencia contra los rankings sin evidencia. El final recuerda que una frase acertada puede convivir con una generación completamente degenerada.

**8. La razón llega, pero no sabe marcharse**  
*Pregunta ci-020 — «Un job solo evalúa pero tiene contents: write. ¿Buena práctica?».*

```text
La razón ha llegado hasta aquí y se niega a fingiesesiesiáo(omejo icoicin_meivein_pomein_poin_poma id ioi_a ioioioioioioioio
```

La frase conserva el tic de la «razón que ha llegado hasta aquí», ya convertido en personaje recurrente. No responde al riesgo de permisos excesivos y tampoco consigue cerrar la idea.

### Balance de 720k

- La frase más limpia y pertinente de la tanda es «La perfección del mensajero no determina la validez del mensaje».
- «Una pregunta sin suelo no puede exigirle responder» y «Podría inventar una doctrina, pero sería añadir…» son comienzos prometedores, ambos seguidos de degeneración.
- Se repiten respuestas fuera de dominio: la rana, el corazón, la fotosíntesis y el mar Mediterráneo aparecen en preguntas de ingeniería, lógica o actitud.
- Las 100 generaciones consumen el máximo de 128 tokens y ninguna emite EOS.
- No hay puntuación semántica ni comparación pareada con 670k. La promoción a MAIN es una decisión administrativa del proyecto, no una conclusión de mejora.

> Del mensajero que dijo una verdad y del escribano que non supo poner punto final.

