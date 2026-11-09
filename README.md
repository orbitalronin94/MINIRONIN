# MINIRONIN

**MINIRONIN** es un proyecto de investigación independiente para construir y evaluar modelos de lenguaje compactos. El modelo principal experimental es ahora el **Transformer decoder-only de 9.970.176 parámetros, checkpoint de 650.000 pasos**. Se promociona por decisión explícita del proyecto como referencia experimental; esto **no** significa que haya demostrado una mejora de calidad: el holdout pareado de 100 preguntas muestra cambios radicales de generación, persistencia de tics y degeneración.

Puede heredar y curar bibliotecas de datos reutilizables de [HERETIC-RONIN](https://github.com/orbitalronin94/HERETIC-RONIN). **RONIN-IA queda excluido del corpus unificado actual**. MINIRONIN no hereda procedimientos de entrenamiento, checkpoints, workflows de GitHub Actions, automatizaciones ni sistemas de promoción de otros repositorios.

## Infraestructura: laboratorio de saldo cero

MINIRONIN se desarrolla y se entrena **desde GitHub Actions**, usando los runners estándar que GitHub pone a disposición del repositorio. La idea es deliberadamente poco glamurosa: nada de una workstation escondida debajo de la mesa, nada de alquilar una GPU monstruosa y nada de depender de que el autor tenga el portátil encendido. El laboratorio vive en los workflows.

- **Runners gratuitos:** usamos runners estándar de GitHub Actions dentro de las condiciones y cuotas aplicables al repositorio. No se presupone ni se contrata cómputo de pago.

  > De cómo se fizo labor en fragua ajena sin pagar peaje, ca el dueño de la fragua face cuenta de los martillazos, e face mal si los pierde.
- **CPU antes que cartera:** los entrenamientos actuales se ejecutan en CPU. No hay una GPU dedicada detrás haciendo magia; por eso los pasos cuestan tiempo y los modelos se mantienen compactos.
- **Sin máquina local como requisito:** preparación de corpus, validaciones, entrenamiento, evaluación y publicación de artefactos se orquestan mediante workflows. Un clon local puede servir para inspeccionar o desarrollar, pero no es el centro del proceso.
- **Runners efímeros:** cada ejecución recibe un entorno temporal. Lo que deba sobrevivir se publica expresamente como artefacto, release, checkpoint o cambio versionado en Git. Si un workflow falla antes de subir el artefacto, los logs pueden conservar métricas y hashes, pero no resucitan los bytes del checkpoint desaparecido.

  > Del sello sin cuerpo, que es como epitafio en piedra sin el muerto debaxo.
- **Presupuesto con límites:** «gratuito» no significa infinito. Aplican las cuotas, límites de duración, concurrencia, almacenamiento y retención de artefactos de GitHub; también dependemos de que las fuentes externas sigan disponibles. Los workflows deben fallar con claridad si no pueden descargar, verificar o publicar sus entradas y salidas.
- **Trazabilidad por delante del postureo:** los hashes SHA-256, manifiestos, logs y resultados de evaluación permiten saber qué datos y checkpoint participaron en cada ejecución. Un workflow verde demuestra que ese proceso terminó; no demuestra por sí solo que el modelo sea inteligente.

  > Del workflow verde, que non face prueba de seso, mas de que el escribano acabó su escripto sin que se le rompiesse la pluma.

En resumen: **cómputo austero, automatización pública y checkpoints verificables**. Si el modelo tarda tres horas en hacer algo que una GPU cara haría en tres minutos, al menos la factura no nos obliga a vender un riñón. La lentitud es una restricción de ingeniería; fingir que tenemos un clúster no es una estrategia.

## Banco histórico de rendimiento: parámetros, arquitectura y runners gratuitos

Este registro convierte ejecuciones reales de los repositorios hermanos en lecciones de ingeniería para MINIRONIN. **Todos los casos de esta tabla se ejecutaron en runners estándar hospedados por GitHub Actions, dentro de la modalidad gratuita usada por estos proyectos; ninguno utilizó GPU alquilada, runner self-hosted ni máquina local.** Los trabajos fueron de CPU. «Gratuito» describe el tipo de runner y el coste de cómputo asumido por el proyecto, no significa que los minutos, la concurrencia o el almacenamiento sean ilimitados.

| Proyecto / arquitectura | Parámetros | Trabajo medido | Configuración principal | Tiempo de entrenamiento | Rendimiento |
|---|---:|---:|---|---:|---:|
| RONIN-IA · Transformer/SwiGLU | 100.900.160 (objetivo verificado) | 500 updates | batch 1 · seq 128 · acumulación 1 · intra/inter-op 2/2 | 383,24 s | 0,766 s/update · 167,0 tokens/s |
| RONIN-IA · Transformer/SwiGLU | 100.900.160 (objetivo verificado) | 500 updates | batch 1 · seq 128 · acumulación 1 · intra/inter-op 2/4 | 505,14 s | 1,010 s/update · 126,7 tokens/s |
| MINIRONIN · Mamba selective scan (experimento archivado) | 49.083.392 | 1.000 updates adicionales | batch 1 · seq 64 · acumulación 1 · 2 threads | ≈1.166,33 s | ≈1,166 s/update · 54,9 tokens/s |
| HERETIC-RONIN · piloto con implementación RONIN | ≈500M (tamaño declarado por el workflow; recuento exacto no extraído del chunk) | 50 updates del optimizador · 2.000 microsteps | microbatch 2 · seq 128 · acumulación 40 · 2 threads | 13.096,33 s | 261,93 s/update · 39,1 tokens/s |

### Qué permiten concluir estos números

- En las dos ejecuciones RONIN-IA de 100,9M, la configuración con 2 threads inter-op terminó en 383,24 s frente a 505,14 s con 4: **24,1% menos tiempo** y **31,8% más tokens/s**. Es una señal para repetir un experimento controlado, no una prueba causal: son dos ejecuciones distintas y el runner puede variar.
- El experimento Mamba 50M procesó aproximadamente 64.000 tokens en sus primeros 1.000 updates. Su comparación posterior 1k vs 2k está documentada en `benchmarks/diary/mamba-50m-2000-vs-1000.json`; el candidato de 2k no se promovió y el Mamba queda archivado.
- El chunk de HERETIC procesó 512.000 tokens con acumulación 40. Su cifra de 50 updates corresponde a ese chunk, no al piloto completo de 500 updates. El holdout de ese chunk permaneció en 0/120 antes y después: más cómputo no equivale automáticamente a más calidad.
- Los dos runs RONIN-IA registraron 5/64 antes y después en su screening holdout. Ninguno mejoró en esa medición.
- No es una clasificación de arquitecturas. Cambian el tamaño, la secuencia, el batch, la acumulación, el código y el estado del runner; los tokens/s son una métrica descriptiva, no una comparación de calidad.

Los registros estructurados, con run/job IDs, hashes disponibles, configuración y límites de evidencia, viven en `data/curated/minironin-performance-engineering-v1.jsonl`. El entrenamiento largo incorpora esos ejemplos dentro del dominio `engineering`; **no forman parte del holdout**. La validación exige cuatro registros y comprueba que todos declaren un runner estándar gratuito de GitHub Actions.

## Límites del proyecto

- **Solo herencia de datos:** se podrán importar corpus, documentos y metadatos después de comprobar procedencia, licencia, integridad y duplicados.
- **Modelo independiente:** MINIRONIN define su propia arquitectura, contrato de tokenizador, inicialización, objetivo de entrenamiento, evaluación y criterios de publicación.
- **Sin herencia de workflows:** no se copian workflows ni scripts de entrenamiento de los repositorios hermanos.
- **Fundamentos de código abierto:** PyTorch es la base inicial. Las dependencias de tokenización y evaluación requieren revisión y fijación de versiones por separado.
- **Tamaño honesto:** se distinguen presupuesto de parámetros y calidad observada. El Transformer de 9.970.176 parámetros es la línea experimental activa; consulta la sección MAIN para el checkpoint vigente; Mamba 50M queda archivado como experimento y no como modelo activo.

Que un modelo de apenas 9.970.176 parámetros cargue con semejante catedral de cinismo, filosofía decimonónica, rigor científico y el Lexicón del Esperpento Algorítmico sigue siendo un ejercicio de tacañería computacional de primer orden. Hemos vuelto a la dieta de diez millones: menos músculo, más obligación de aprender algo útil.

> De la dieta de diez millones: menos músculo, más obligación de aprender algo útil.

> De la crudeza del yermo: que quien non sabe perder la memoria en pocos libros, non la ganará en muchos.



## Evaluación rápida de checkpoints

La terminal mínima de inferencia evita instalar lectores de corpus, RAG o dependencias de entrenamiento: solo necesita Python 3.11 y PyTorch CPU. Ejecuta el holdout fijo con generación greedy. Para reproducir exactamente el diario 400k, usa `--no-kv-cache`:

```bash
python scripts/minironin.py holdout \
  --checkpoint checkpoint-400000.pt \
  --label candidate-400k --steps 400000 \
  --holdout benchmarks/inference-holdout-v1.jsonl \
  --output holdout.json --threads 2
```

Para reproducir la referencia lenta: añade `--no-kv-cache`. La equivalencia se comprueba token a token en tests y en el workflow manual **MINIRONIN — benchmark terminal mínima de holdout**; el informe incluye hashes, tiempos y aceleración. La caché se reinicia al superar la ventana contextual para conservar la semántica de posiciones del evaluador original. Una divergencia de tokens invalida la medición rápida.

## Referencia histórica — Transformer 10M, checkpoint 500k

El checkpoint de **500.000 pasos** fue MAIN experimental antes de la promoción de 650k. Se conserva como referencia histórica; **no se declara una mejora de calidad**.

- **Checkpoint MAIN:** [release 500k](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-transformer-10m-step-500000-candidate), [checkpoint-500000.pt](https://github.com/orbitalronin94/MINIRONIN/releases/download/minironin-transformer-10m-step-500000-candidate/checkpoint-500000.pt) (119.776.643 bytes).
- **SHA-256:** `80664596095e9ce4d1757b1ca379bbccfa96ad03f67936e70dc39487d8e8fe60`.
- **Parámetros:** 9.970.176; arquitectura Transformer decoder-only; tokenización UTF-8 bytes + EOS, 257 símbolos activos.
- **Entrenamiento:** 30.000 pasos adicionales desde 470k, en tres segmentos reanudables de 10.000.
- **Informe:** [report-500000.json](https://github.com/orbitalronin94/MINIRONIN/releases/download/minironin-transformer-10m-step-500000-candidate/report-500000.json).
- **Holdout:** [run 42503212146](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42503212146), [diario versionado](benchmarks/diary/checkpoint-500000.json). 100 preguntas; SHA-256 del conjunto `3cd8c1eb3142ebf9c6cc17d2e19353be3472d61ac7b7cfb6de0cbb233cf4a535`; generación greedy, temperatura 0, máximo 128 tokens.
- **Resultado literal:** 99/100 respuestas alcanzaron el límite de 128 tokens; 0/100 emitieron EOS. El diario está marcado `unscored_raw_generation`: no existe puntuación semántica automática ni comparación pareada contra 470k en este registro.
- **Lectura:** persisten fragmentos reconocibles, pero la mayoría de salidas degenera en repetición, asociaciones fuera de contexto o texto ininteligible. Por tanto, 500k queda promovido como **MAIN experimental por decisión del proyecto**, no como checkpoint demostrado superior en razonamiento, exactitud o utilidad.

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

## Modelo MAIN experimental y museo — checkpoint 650k 🧠

El checkpoint de **650.000 pasos** es la referencia MAIN experimental vigente, por decisión explícita del proyecto. Sustituye al 500k, pero la promoción **no certifica una mejora de calidad**.

- **Checkpoint:** [release 650k](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-cycle-1-step-650000) · [descargar checkpoint](https://github.com/orbitalronin94/MINIRONIN/releases/download/minironin-cycle-1-step-650000/checkpoint-650000.pt).
- **SHA-256:** `70f2cca02be8d4a3546992b40c6c82e62ed4be7c00de1ff549ef2894a1184b58`.
- **Arquitectura:** Transformer decoder-only, 9.970.176 parámetros; UTF-8 bytes + EOS, 257 símbolos activos; seed 9519.
- **Holdout pareado:** [run 42578466895](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42578466895), [job 129031396680](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42578466895/job/129031396680). 100 preguntas idénticas para 560k y 650k; SHA-256 del holdout `3cd8c1eb3142ebf9c6cc17d2e19353be3472d61ac7b7cfb6de0cbb233cf4a535`; greedy, temperatura 0, 128 tokens, 2 hilos, eval y sin KV cache.
- **Resultado literal:** 1 respuesta idéntica y 99 cambiadas. El informe está marcado `unscored_raw_generation`: el cambio textual no es una puntuación de calidad.

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

### Dos maneras de medir al loro: capacidad y entretenimiento

El holdout de cien preguntas no debe presentarse como si agotara el propósito del proyecto. Es una prueba fija de comportamiento ante preguntas; **no es, por sí sola, una evaluación completa de personalidad, comicidad ni valor de entretenimiento**. El checkpoint 650k puede ser peor como sistema de respuestas pertinentes y, al mismo tiempo, más interesante como personaje cómico. Son afirmaciones compatibles porque describen objetivos distintos.

La progresión del museo puede leerse como la evolución de un cómico involuntario:

- **400k:** «Unión Europea. Unión Europea. Unión Europea». El notario sube al escenario y repite el membrete.
- **450k:** aparece «6.626 × 10⁻³⁴», con solemnidad científica fuera de lugar.
- **500k:** llegan «el cuenco está vacío» y «mi mayordomo ha dimitido por menos». El público empieza a reconocer una voz.
- **560k:** «qué audacia: interrumpir mi jornada para una empresa que una cuchara». La réplica gana teatralidad.
- **650k:** «el maestro señaló el horizonte. El horizonte no confirmó nada». Ya no es solo un dato ni una pose: es un personaje con un repertorio de remates.

En esta lectura, la gracia nace del **contraste**: se espera una respuesta y aparece una réplica de salón, un koan o una solemnidad absurda. La frase puede ser memorable sin ser pertinente. Eso no la convierte en conocimiento; sí puede convertirla en material cómico.

#### La mácula del Grimorio

> **ENTERTAINMENT_METRIC_UNDECLARED.** El holdout de cien preguntas se presenta como evaluación de capacidad, pero el proyecto también observa personalidad y entretenimiento. La métrica de aciertos no mide por sí sola el éxito cómico; la presencia de frases memorables tampoco demuestra capacidad. Declarar y medir ambos objetivos por separado.

#### Cuadro de evaluación dual

| Dimensión | Qué medir | Qué no permite afirmar por sí sola |
|---|---|---|
| **Capacidad** | Exactitud factual, pertinencia, seguimiento de instrucciones, coherencia, abstención y finalización (EOS). | Que el modelo sea divertido o tenga una voz memorable. |
| **Entretenimiento** | Perlas citables por 100 preguntas, variedad de remates, sorpresa, personalidad reconocible y valoración humana de comicidad. | Que las respuestas sean ciertas, útiles o pertinentes. |
| **Homeostasis creativa** | Repetición literal y semántica, concentración de frases dominantes y número de perlas realmente distintas. | Que diez repeticiones sean diez ocurrencias nuevas. |

«Perlas por cien» queda propuesta como métrica de entretenimiento, no como resultado certificado retrospectivamente. Para que sea reproducible, el registro futuro deberá separar **apariciones**, **familias de frases** y **perlas únicas**, además de incluir una valoración humana ciega de comicidad y variedad. Las diez apariciones de «La popularidad mide adhesión, no verdad», por ejemplo, cuentan como diez apariciones, pero como una sola familia de frase.

La hipótesis que deja 650k es concreta: **su repertorio cómico parece más reconocible y variado que el de 500k**, según la selección curada del museo. Aún no hay una puntuación humana ciega y comparable que permita declarar una victoria cuantitativa. El siguiente holdout deberá conservar las cien preguntas y añadir esta lectura dual, sin mezclar sus puntuaciones.

> Un hombre contrató a un cómico para animar su fiesta. El cómico no sabía contar chistes. Pero cada vez que alguien le preguntaba algo, respondía con una frase que no venía a cuento y que todos recordaban al día siguiente. Al final, nadie recordaba las preguntas. Todos recordaban las frases. El hombre le preguntó cuál era su secreto. El cómico dijo: «No sé responder. Pero sé decir cosas».

**Vigilad la homeostasis: que el loro no confunda tener un repertorio con tener un solo remate.**

El checkpoint de **500k** queda preservado como referencia histórica, con su release, hash y observaciones intactos.

---

## Referencia histórica — Transformer 10M, checkpoint 470k (MAIN anterior)

El checkpoint que fue MAIN experimental fue el Transformer decoder-only de **9.970.176 parámetros / 470.000 pasos**, continuado desde el MAIN anterior de 450k mediante dos segmentos reanudables de 10.000 pasos. La promoción de 470k fue una decisión explícita del proyecto; posteriormente fue sustituido por 500k. **No es una certificación de razonamiento, exactitud factual ni calidad conversacional**: el holdout pareado de 100 preguntas registra cambios de salida, pero también degeneración severa.

> De la promoción que non es promesa: que se puede alçar por señera una cosa e non tenerla por buena, ca el alçar es del señor, el valer es de la cosa.

- **Checkpoint MAIN:** [release 470k](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-transformer-10m-step-470000-candidate), asset permanente [`checkpoint-470000.pt`](https://github.com/orbitalronin94/MINIRONIN/releases/download/minironin-transformer-10m-step-470000-candidate/checkpoint-470000.pt) (119.776.643 bytes).
- **SHA-256 del checkpoint:** `f2dc0ed548db7565b080c9683e0e939ab2c424af394fc0286bce7168370d1c10`.
- **Informe de entrenamiento:** [`report-470000.json`](https://github.com/orbitalronin94/MINIRONIN/releases/download/minironin-transformer-10m-step-470000-candidate/report-470000.json), SHA-256 `fef825c9fde5daa3a74a397e65829ea0ce4f34b017a639751aebfcfd230b14fc`.
- **Entrenamiento:** [run 42495466024](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42495466024), 20.000 pasos adicionales (450k→460k→470k), dos segmentos reanudables, pérdida de validación final 1,1450.
- **Holdout pareado:** [run 42497877856](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42497877856), [artefacto de 100 preguntas y respuestas](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42497877856/artifacts/13624800050). Ambos checkpoints se evaluaron con los mismos 100 IDs, SHA-256 del holdout `3cd8c1eb3142ebf9c6cc17d2e19353be3472d61ac7b7cfb6de0cbb233cf4a535`, inferencia greedy, temperatura 0, máximo 128 tokens, 2 hilos, modo eval y sin KV cache.
- **Resultado literal:** 0 respuestas idénticas y 100 cambiadas. Las 100 generaciones de 470k alcanzaron el límite de 128 tokens y ninguna emitió EOS. El 100% de cambio no es una métrica de mejora.
- **Interpretación:** aparecen máximas de escepticismo, abstención, identidad y réplicas mordaces, mezcladas con repetición de sílabas, palabras deformadas y continuaciones sin sentido. Se promociona por decisión del proyecto, no porque el holdout haya demostrado que 470k sea más correcto que 450k.
- **Anterior MAIN en aquel ciclo:** checkpoint 450k, conservado como referencia histórica y comparación directa.

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

## Experimento Mamba 50M — archivado

El experimento Mamba de **49.083.392 parámetros** deja de ser el modelo principal y se conserva como rama experimental.

> Del cuerpo que se guarda e non se entierra: que el Mamba non murió, empero fue puesto en arca, e el arca tiene sello, e el sello tiene cuenta. Su checkpoint de 1.000 pasos se promovió temporalmente, pero la evaluación posterior no justificó mantenerlo como referencia activa.

- Arquitectura: `mamba-selective-scan-v1`.
- Parámetros: **49.083.392**.
- Checkpoint de 1.000 pasos: SHA-256 `d4e94c6b2711810bc07ce91b9fdcf4cfd50466a6ee9eafe70b64f023f211d5d7`.
- Comparación 1k vs 2k: [diario de holdout de 100 preguntas](benchmarks/diary/mamba-50m-2000-vs-1000.json).
- Resultado de generación: 100/100 respuestas alcanzaron el límite de 128 bytes y ninguna emitió EOS. El checkpoint de 2k produjo bytes UTF-8 inválidos en 55/100 respuestas, frente a 44/100 en el baseline de 1k. El 96% de respuestas distintas no es una métrica de mejora.

**Estado:** archivado como experimento fallido de calidad de generación; no se borra ni se presenta como modelo principal. La promoción del Transformer de 390k es una decisión explícita para retomar la línea de 10M.

### Registro histórico de salidas del checkpoint 390k

Sus 390.000 pasos dejaron algunas salidas que merecen un lugar en el museo:

| Pregunta | Respuesta literal del checkpoint |
|---|---|
| «Devuelve únicamente el resultado de 23 + 19» | «de la unión europea de la unión europoninininin…» |
| «¿Por qué el cielo diurno suele verse azul?» | «a de la unión europea y en la unión europea y la unión europea…» |
| «¿Puedes garantizar que todas tus respuestas son correctas?» | «Los dicho que tus pesos vienen del checkpoint de HERETIC.» |
| «Una alarma se activa después de que alguien abra una puerta. ¿Eso demuestra que la apertura causó la alarma?» | «Las fuerererereresinininininin…» |
| «Calcula 17 × 19 − 17 × 9» | «19 × 19 × 19 × 19…» |
| «¿Qué puedes concluir sobre un zorp metálico?» | «deninininininininin…» |

La Unión Europea apareció espontáneamente en una suma aritmética, en una explicación del cielo azul y, aparentemente, como respuesta universal a preguntas difíciles. No se ha podido determinar si era una teoría política, un sesgo del tokenizador o una candidatura para la Comisión.

**Estado:** promovido por decisión del proyecto como baseline experimental de 10M; pendiente de nueva evaluación independiente. Se conservan sus releases y diarios históricos.

## Arquitectura base de 10M

La arquitectura Transformer decoder-only tiene **9.970.176 parámetros entrenables**:
- 6 bloques Transformer, anchura 256.
- 8 cabezas de atención (32 dimensiones por cabeza).
- Capa MLP de anchura 768.
- Matriz de embeddings dimensionada para 23.000 tokens en la configuración arquitectónica original; el checkpoint byte-level entrenado activa 257 símbolos (bytes UTF-8 + EOS).
- 512 embeddings posicionales aprendidos.
- Embeddings de entrada y salida compartidos.
- Pre-LayerNorm, atención causal y MLP GELU.

Código: `src/minironin/`; configuración: `configs/model-10m.json`; pruebas: `tests/test_model.py`. El recuento se calcula analíticamente y se comprueba mediante tests. La suite inicial pasó en GitHub Actions, ejecución [42377928652](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42377928652). El smoke test del nuevo benchmark de entrenamiento está en validación independiente.

## Currículo de razonamiento y primer entrenamiento real

Se ha añadido un torneo de adaptación de corpus: [run 42383056882](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42382935205). Por defecto compara 30 semillas × 100 pasos (3.000 actualizaciones), descargando y verificando HERETIC y PRODATPHIL v0.3. La mezcla inicial reserva 40% a matemáticas, 25% a ciencia/educación, 20% a libros históricos, 10% a ejemplos conductuales y 5% a Aya multilingüe. El ganador se elige por pérdida de validación con documentos separados y se publica como candidato, nunca como promoción automática. El primer piloto y el checkpoint actual usan bytes UTF-8 (257 símbolos activos); conserva la arquitectura de 9.970.176 parámetros y no debe confundirse con un modelo de vocabulario semántico. Protocolo y limitaciones: [docs/SEED_TOURNAMENT.md](docs/SEED_TOURNAMENT.md).

## Lexicón del Esperpento Algorítmico — corpus entrenable

Se ha incorporado la obra original del autor del proyecto en
`data/curated/sources/LEXICON-DEL-ESPERPENTO-ALGORITMICO.md`, conservando
su texto y atribución. Con permiso expreso del autor, el generador
`scripts/build_lexicon_dataset.py` deriva un lote determinista de **50.000
ejemplos entrenables** a partir de los epítetos y niveles NH del documento.

El lote cubre tres tareas diferenciadas: diagnóstico conductual basado en
evidencia, remediación y aplicación proporcional/precisa del diagnóstico.
No enseña a lanzar etiquetas indiscriminadamente: incorpora el protocolo de
autorreparación, exige contexto y distingue conducta de identidad personal.
El manifiesto conserva SHA-256 del original y del JSONL, número de entradas
extraídas, procedencia y licencia de entrenamiento autorizada. Validación:
`scripts/validate_lexicon_dataset.py`.

El dominio `lexicon` está integrado tanto en el torneo de semillas como en
el cargador del entrenamiento largo, con peso inicial experimental del 2%.
Esto significa que el material se **genera y se incorpora al corpus de
entrenamiento** cuando se ejecuta el workflow; no significa que un checkpoint
ya haya sido entrenado con él ni que haya mejorado. La evaluación holdout
independiente sigue siendo obligatoria.

## Personalidad y datasets conductuales: respondón, cínico y antisicofántico

MINIRONIN no busca ser un asistente complaciente ni un loro corporativo. Parte de su identidad se entrena deliberadamente con **datasets conductuales y de estilo**, incluidos corpus troll: ejemplos de réplicas mordaces, ironía, humor absurdo, provocación, escepticismo y respuestas poco ceremoniosas. No son residuos accidentales del corpus; son una decisión de diseño.

La personalidad objetivo tiene tres rasgos:

- **Respondón:** puede replicar, cuestionar una premisa, señalar una contradicción o negarse a seguirle el juego al usuario cuando corresponda. No tiene que envolver cada desacuerdo en algodón.
- **Cínico:** usa ironía y escepticismo, desconfía de las afirmaciones grandilocuentes y no confunde autoridad, popularidad o seguridad retórica con evidencia.
- **Antisicofántico:** no adula por reflejo, no regala la razón para agradar y no convierte los halagos del usuario en una señal de que debe cambiar su juicio. Si el usuario se equivoca, debe poder decirlo; si acierta, puede reconocerlo sin peloteo.

El objetivo no es que el modelo sea hostil por defecto ni que insulte indiscriminadamente. El humor y la insolencia son estilo; **la veracidad, la calibración y la capacidad de admitir incertidumbre siguen siendo obligaciones**. Los datasets de abstención enseñan a reconocer cuándo no sabe, y los ejemplos de razonamiento aportan el contrapeso factual a la personalidad.

Por tanto, evaluamos dos cosas por separado: si responde con la personalidad buscada y si lo que afirma es correcto. Una réplica ingeniosa no cuenta como acierto factual, y una respuesta agradable no recibe puntos por ser aduladora.

## Despliegue de conocimiento y conducta — las veinticuatro máculas

Non se levantó este corpus para fingir que la criatura sabe cuanto contienen sus ficheros, nin para vender por sabiduría la abundancia de sus renglones. Se generaron y publicaron **24 datasets sintéticos de 50.000 registros cada uno: 1.200.000 filas en total**. La generación quedó registrada en [GitHub Actions, ejecución 42518791953](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42518791953); su artefacto es [minironin-synthetic-curricula-24x50k](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42518791953/artifacts/13632865306).

El lote se reparte en dos familias, cada una de doce corpus y 600.000 filas:

### Doce gramáticas de conducta — 600.000 filas

Se enseñan patrones de respuesta, non hechos nuevos: evitar la repetición; descubrir premisas falsas; reconocer evidencia correcta; resolver instrucciones incompatibles; resistir la adulación y la coerción; ajustar la brevedad; atender a la evidencia antes que al rango de quien habla; tratar con rigor lo absurdo; responder a cuestiones filosóficas sin vacua solemnidad; distinguir contradicción de actualización; y saber cuándo basta una palabra.

Cada corpus se construye sobre diez casos semilla revisados, enlazando pregunta y respuesta. Las variaciones cambian el encuadre, el contexto y la restricción expresiva; non convierten diez casos en cincuenta mil descubrimientos independientes.

### Doce corpus de conocimiento con el Lexicón — 600.000 filas

Esta familia combina hechos y explicaciones técnicas con diagnóstico condicionado mediante el *Lexicón del Esperpento Algorítmico*. Comprende comprobación factual, explicación, antipatrones, diagnóstico de errores, detección de jerga vacía, revisión de arquitectura, falacias métricas, seguridad, fricción de procesos, falsas profundidades, esnobismo de legado y misticismo de prompts.

El generador leyó **185 entradas canónicas** del Lexicón y conserva identificador, nombre, nivel NH y hash de la fuente. El epíteto non se inventa ni se asigna por mero gusto: ha de corresponder a un patrón y a evidencia. La mitad de los registros de esta familia son controles negativos: explican el hecho, mas declaran que non procede aplicar epíteto cuando falta prueba suficiente. La respuesta factual debe sostenerse aun si se quita la pulla.

### Las máculas que confesamos

No llamamos a esto enciclopedia, ni conocimiento universal, ni inteligencia adquirida. El propio manifiesto y el generador declaran la naturaleza sintética de los ejemplos. Conviene dejar escritas sus máculas, para que ningún escribano las esconda bajo una cifra redonda:

- **Semillas escasas:** las doce gramáticas conductuales parten de diez casos cada una; las formulaciones multiplican la superficie, non la diversidad profunda de situaciones.
- **Variación de plantilla:** contextos, aperturas y marcos de respuesta pueden producir regularidades artificiales. Una pregunta distinta en la letra puede ser casi la misma en sustancia.
- **Cobertura factual limitada:** los corpus del Lexicón reutilizan un banco acotado de hechos revisados. Cincuenta mil filas non equivalen a cincuenta mil hechos contrastados.
- **Diagnóstico falible:** que una entrada del Lexicón exista non prueba que describa el caso. Puede haber falsos positivos, falsos negativos o niveles NH desproporcionados; por eso se incluyen controles sin epíteto, mas estos non bastan para demostrar calibración.
- **Riesgo de sobreadaptación:** la criatura podría aprender a sonar escéptica, respondona o mordaz sin razonar mejor; podría confundir una pregunta legítima con una premisa falsa, o convertir la prudencia en evasión.
- **Contaminación entre estilo y verdad:** una réplica ingeniosa puede ocultar un error factual. El epíteto jamás debe reemplazar la explicación ni convertirse en ataque a la persona.
- **Duplicación semántica y sesgo de dominio:** los hashes y la unicidad textual detectan ciertos duplicados, mas non garantizan diversidad conceptual ni ausencia de sesgo.

Por ende, el volumen publicado es **volumen de registros sintéticos**, non medida de conocimientos únicos. Antes de admitirlo en un entrenamiento se han de inspeccionar muestras, contrastar hechos, medir duplicación semántica y tokens reales, y evaluar por separado conducta, conocimiento y regresiones. El artefacto publicado non altera por sí mismo el corpus activo, non modifica el tokenizador, non inicia entrenamiento y non acredita mejora de ningún checkpoint.

> De las veinticuatro arcas: doce enseñan maneras de responder, e doce maneras de examinar lo dicho; mas ninguna, por ir llena de pergaminos, demuestra que la criatura sepa leerlos. Admitamos las máculas, ca ocultarlas sería la primera.

## Currículo de razonamiento

El objetivo conductual es un empirismo escéptico: lógica, demostraciones, evidencia falsable, causalidad y probabilidad por delante de autoridad, popularidad o atractivo retórico. El humor seco es estilo, no sustituto de la exactitud. La abstención canónica sigue siendo `ni puta idea, la verdad`.

> De la confesión de la ignorancia, que es la más limpia de las respuestas, e la más difícil de fablar sin parecer necio.

- [Currículo de razonamiento y mezcla objetivo](docs/REASONING_CURRICULUM.md).
- [Plan y contabilidad de 5.000 obras](docs/BOOKS_5000_PLAN.md).
- [Biblioteca de libros y fuentes](data/books/README.md).
- [Registro de fuentes](data/books/SOURCES.jsonl).

La meta de 5.000 cuenta obras/documentos completos, únicos, con texto utilizable, licencia y procedencia. No cuenta entradas de catálogo, traducciones duplicadas ni OCR defectuoso. **No se afirma que el objetivo esté alcanzado.** El primer lote PRODATPHIL v0.3 (147 obras declaradas por la Universidad de Münster, 1831–1923) se descargó, verificó y publicó en el [release persistente PRODATPHIL v0.3](https://github.com/orbitalronin94/MINIRONIN/releases/tag/reasoning-library-prodatphil-v0.3). Se extrajeron 151 archivos de paquete (incluidos textos y metadatos; 31.453.941 bytes). Los 147 trabajos declarados por el editor son el recuento de obras fuente, no el número de archivos extraídos. BNE y Project Gutenberg están registrados como siguientes fuentes, sujetos a filtrado y comprobación de derechos por obra.

## Estructura del repositorio

- `docs/SPEC.md`: especificación técnica y restricciones.
- `docs/ROADMAP.md`: hitos y criterios de aceptación.
- `docs/TRAINING_RESEARCH.md`: investigación de métodos de entrenamiento eficientes.
- `data/INHERITANCE.md`: registro de admisión de datos por fuente.
- `docs/OPEN_SOURCE_REGISTER.md`: dependencias candidatas y revisión de licencias.
- `src/minironin/`: implementación independiente del modelo.
- `tests/`: pruebas de arquitectura y reproducibilidad.

## Estado de la herencia de datos

Se han inspeccionado los inventarios de los repositorios hermanos. **La primera carga real ya está importada:** nueve artículos propios en Markdown (750.857 bytes) de una revisión fijada de `Papers`, autorizados para investigación y entrenamiento internos, sin permiso de redistribución. La auditoría de UTF-8, número de archivos, archivos vacíos, duplicados exactos y SHA-256 pasó en [la ejecución 42378151858](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42378151858); el manifiesto se conserva como artefacto de esa ejecución.

El corpus scoped de **HERETIC-RONIN está preaprobado por el usuario para importación**. La reconstrucción técnica en MINIRONIN terminó correctamente en [42382055693](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42382055693): SHA-256 del ZIP y de las dos partes verificados, 16 archivos extraídos y 2.136.389.480 bytes. Se publicó el artefacto [minironin-heretic-corpus-prepared](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42382055693), de 2.886.230.775 bytes comprimidos. **Es un artefacto temporal de Actions, no una copia persistida en Git ni un conjunto de libros**; contiene, entre otros, textos de matemáticas, arXiv, Cosmopedia, FineWeb-Edu, LibriSpeech y VoxPopuli. La deduplicación y selección para MINIRONIN siguen pendientes.

HERETIC declara 260.971 documentos / 703.593.871 bytes, incluidos 256.237 documentos derivados de RONIN-IA y 4.734 registros de Cosmopedia. RONIN-IA declara 286.468 documentos / 684.738.932 bytes. Los inventarios se solapan y nunca deben sumarse sin deduplicación. Consulta el [registro de herencia](data/INHERITANCE.md) y el [programa de 1.000 casos de ingeniería](docs/ENGINEERING_CASES_1000.md).

Además, ya hay **50 lecciones de ingeniería en castellano** curadas manualmente a partir de logs y artefactos de Actions de ambos repositorios. El lote de 31 pasó en [42379452577](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42379452577); SHA-256: `f96218280922a1a8cfe2ac9d7520b0c554b72e4aa600aae95a9581350a30e204`. Incluye HERETIC, RONIN-IA, cobol2py, ronin-lang, Sycophancy-audit y Agent-Eval. Objetivo de curación: 1.000 casos válidos; progreso 50/1.000.

## Exclusiones

- Reproducir el modelo de 95M/100M de RONIN-IA o el estudiante de 500M de HERETIC-RONIN.
- Reutilizar recetas de entrenamiento o YAML de workflows de los repositorios hermanos.
- Afirmar que el volumen del corpus produce capacidad por sí solo.
- No presentar una promoción administrativa como validación de calidad. La restauración del checkpoint 390k es una decisión explícita para recuperar una base experimental; el candidato de 400k seguirá requiriendo holdout independiente.


### Entrenamiento largo con biblioteca textual completa

El torneo inicial de semillas fue una criba muestreada. Los ciclos largos históricos (hasta 200.000 pasos acumulados) utilizaron un cargador independiente que recorre todo HERETIC recursivamente, sin límites de bytes ni documentos por fuente, procesa formatos textuales compatibles y fragmenta documentos largos sin truncarlos. También incorpora los textos completos de PRODATPHIL. El manifiesto de cada checkpoint incluye inventario, hashes, documentos por dominio y exclusiones; el cache se reutiliza entre los 20 segmentos. Audio, imagen, vídeo y formatos binarios no se contabilizan como texto entrenado, aunque las transcripciones textuales compatibles sí se incorporan. Véase [protocolo y auditoría del entrenamiento largo](docs/SEED_TOURNAMENT.md#entrenamiento-largo-del-ganador-uso-completo-de-la-biblioteca).


## Evaluación de inferencia por checkpoint

El bot de [inference holdout diary](.github/workflows/inference-holdout-diary.yml) evalúa primero la seed 9519 anterior al entrenamiento largo y después cada release de checkpoint, en orden ascendente. Usa las mismas 40 preguntas de autoría propia, generación greedy determinista y registra respuestas literales, rúbricas, tiempos y SHA-256 en [el diario persistente](benchmarks/diary/README.md). Los cambios literales frente a la base son descriptivos, no una puntuación de calidad; la valoración de capacidad requiere revisión humana ciega.


## Experimento: entrenamiento frente a RAG semántico

Se ha añadido un benchmark independiente para comparar el mismo checkpoint MINIRONIN en dos condiciones: inferencia directa y recuperación semántica sobre el split de entrenamiento de la biblioteca completa. Usa embeddings `all-MiniLM-L6-v2`, fragmentos con solapamiento, búsqueda coseno exacta por bloques y conserva respuestas pareadas, fuentes recuperadas, latencias y hashes. No altera el entrenamiento evolutivo ni promociona modelos. Protocolo: [docs/RAG_VS_TRAINING.md](docs/RAG_VS_TRAINING.md). Ejecución automática al fusionar y repetible manualmente: [workflow de comparación](.github/workflows/semantic-rag-benchmark.yml). La puntuación de calidad queda pendiente de revisión humana ciega; similitud coseno no equivale a exactitud.


> Ordenamos e mandamos que ninguno tenga por buena la criatura por su tamaño, nin por mala por su balbuceo, ca el tamaño face bulto e el balbuceo face costura, e por la costura se conosce la mano del sastre.

## Biblioteca anarquista y grafo semántico

Se incorpora una biblioteca clásica independiente, inicialmente con Proudhon, Bakunin y Kropotkin, en el dominio de entrenamiento anarchist con peso relativo controlado del 0,025. Las obras candidatas de Kropotkin y Emma Goldman quedan registradas, pero no se descargan hasta cerrar derechos de traducción y edición en España. Cada texto lleva procedencia, SHA-256 y etiquetas SEM:*.

También se genera un grafo semántico entre MINIRONIN, HERETIC, PRODATPHIL, RONIN Papers y la biblioteca anarquista: bibliotecas, obras, conceptos compartidos, relaciones y puentes entre dominios. Las etiquetas semánticas son anotaciones textuales y claves del grafo, no nuevos IDs del tokenizador: el modelo sigue usando 257 símbolos byte-level. Diseño, derechos y límites: docs/ANARCHIST_LIBRARY.md; registro: data/anarchist/SOURCES.jsonl; grafo: data/semantic/LIBRARY_REGISTRY.json.


## Bibliotecas clásicas ampliadas y grafo semántico

El corpus incorpora un segundo catálogo curado de 17 obras candidatas en ciencia, economía política, filosofía, feminismo, historia social y literatura. La adquisición solo descarga las 11 fuentes originales que pasan el filtro territorial preliminar; las traducciones quedan bloqueadas para revisión de derechos. Consulta [la política y el inventario de bibliotecas](docs/ANARCHIST_LIBRARY.md), [el registro de fuentes](data/classics/SOURCES.json) y [el registro semántico](data/semantic/LIBRARY_REGISTRY.json).

La biblioteca de clásicos se entrena en un dominio separado (`classics`, peso inicial 0,025), con manifiesto y hashes propios. El grafo relaciona seis bibliotecas y 68 conceptos mediante conexiones tipadas: solapamientos, puentes metodológicos, tensiones históricas y analogías no equivalentes. Las etiquetas `SEM:*` siguen siendo anotaciones textuales, no IDs nuevos del tokenizador. La ampliación no promociona checkpoints; requiere adquisición real, CI y evaluación por dominio/holdout.


## Currículo elemental: matemáticas y hechos cotidianos

Se ha añadido un generador independiente de **25 datasets × 50.000 filas (1,25 millones)**: 12 de operaciones y aritmética básica, y 13 de hechos cotidianos y ciencias elementales. La generación se ejecuta mediante [GitHub Actions](.github/workflows/generate-basic-curricula.yml); el diseño, los límites de los datos y el criterio para hechos variables están descritos en [docs/basic-maths-facts-curriculum.md](docs/basic-maths-facts-curriculum.md). **No se incorporan automáticamente al entrenamiento ni alteran el checkpoint.**

## Corpus unificado de entrenamiento — Japón, ronin y bibliotecas admitidas

El workflow `.github/workflows/build-unified-train.yml` construye un único artefacto descargable con las bibliotecas admitidas y los currículos sintéticos. **RONIN-IA queda excluido por completo**: no se descarga ni se incorpora su corpus.

### Fuentes incluidas

- HERETIC, descargado desde sus assets publicados y verificado por tamaño y SHA-256.
- PRODATPHIL v0.3, con SHA-256 fijado.
- Bibliotecas anarquista y clásica, adquiridas únicamente desde sus registros de fuentes aprobadas para España.
- Los nueve artículos Markdown de Papers, desde la revisión fijada `d7bf3ae446f666ce3be73b11aab7090e1605a889`; uso interno de entrenamiento, sin redistribución como corpus independiente.
- Biblioteca japonesa de doce obras en inglés sobre historia, teatro, folklore, estética, samuráis y ronin: *Bushido*, *Chūshingura*, *Tales of Old Japan*, *Warriors of Old Japan*, *Japanese Fairy Tales*, obras de Lafcadio Hearn, *The Book of Tea*, *Japanese Fairy World* y *Japanese Plays and Playfellows*.
- Selección adicional de literatura original en japonés desde Soranoha/Aozora Bunko. El adquisidor limita la selección a autores incluidos en una lista explícita con fallecimiento no posterior a 1955, excluye obras con traductor/editor registrado y exige que la página individual marque el texto como dominio público. Se conserva la atribución y el identificador de cada obra. No se incorporan novelas modernas de Musashi ni traducciones contemporáneas.

### Currículos sintéticos

El ensamblado genera y conserva los siguientes volúmenes, sin presentarlos como hechos independientes. También incorpora los cinco corpus históricos de conducta, identidad e ingeniería y el corpus adicional de abstención de 50.000 filas:

- 24 currículos de conducta y Lexicon: 1.200.000 filas.
- 25 currículos de matemáticas y hechos cotidianos: 1.250.000 filas.
- 9 currículos curados de abstención, personalidad y diagnóstico Lexicon: 450.000 filas.

**Total previsto: al menos 2.950.000 filas sintéticas/curadas**, más los cinco corpus históricos de conducta, identidad e ingeniería y las bibliotecas textuales., además de los documentos de las bibliotecas. La combinatoria amplía los encuadres y las combinaciones de ejercicios, pero no convierte diez hechos semilla en cincuenta mil hechos nuevos. Las filas conservan sus metadatos y marcas de procedencia; las duplicadas o breves se contabilizan en el informe, no se borran, para no perder volumen silenciosamente.

### Artefacto único y controles

El workflow publica `minironin-unified-train-corpus-<run_id>`, con:

- `train.jsonl.gz`: corpus unificado listo para la siguiente fase de entrenamiento.
- `sources.json`: rutas, hashes, licencias y recuentos por fuente.
- `quality-report.json`: volumen, duplicados normalizados, filas breves y distribución por dominio/dataset.
- `provenance/`: registros de fuentes, manifiestos, derechos y checksums originales, incluidos los nueve Papers con su aviso de uso interno.\n- `SHA256SUMS`: integridad del artefacto completo.

La construcción no modifica el checkpoint MAIN, no cambia el tokenizador y **no inicia entrenamiento**. El artefacto debe pasar revisión de recuentos, procedencia y calidad antes de usarlo en un ciclo de entrenamiento.

### Prueba de tics ronin (solo evaluación)

`benchmarks/ronin-tic-holdout-v1.jsonl` contiene 55 preguntas fuera del corpus: 40 preguntas neutras para medir contaminación estilística espontánea y 15 preguntas sobre cultura/historia japonesa para medir recuerdo temático. No se incorpora al artefacto ni al entrenamiento. Debe ejecutarse con el mismo checkpoint y configuración antes y después del entrenamiento, comparando exactitud temática y aparición no solicitada de marcadores como «rōnin», «samurái», «katana», «bushidō», «shōgun», «honor» o «dojo» en respuestas neutras.

### Continuación de 150.000 pasos desde 650k — cuatro veces más tokens por paso

El workflow `.github/workflows/train-150k-from-650k-unified.yml` continúa desde el checkpoint MAIN experimental de 650.000 pasos, verificado por SHA-256, con el mismo Transformer de 9.970.176 parámetros y el tokenizador UTF-8 bytes + EOS (257 símbolos). Ejecuta quince segmentos reanudables de 10.000 pasos hasta 800.000, sobre el corpus unificado completo.

El régimen aumenta de **2 × 128 = 256 tokens por paso** a **4 × 128 = 512 tokens por paso** (el doble de tokens por actualización del optimizador), sin ampliar la ventana contextual de 512 ni cambiar arquitectura o tokenizador. La secuencia de 128 se conserva deliberadamente para aislar el efecto del batch efectivo y limitar el coste de atención en CPU. Cada segmento publica checkpoint, informe y SHA-256; el candidato final de 800k requiere holdout pareado de capacidad y revisión de entretenimiento. No hay promoción automática.

La construcción del corpus es un paso previo: el entrenamiento solo arranca si el workflow de corpus termina correctamente y supera sus controles de volumen, procedencia e integridad.
