# MINIRONIN

**MINIRONIN** es un proyecto de investigación independiente para construir y evaluar modelos de lenguaje compactos. El modelo principal experimental es ahora el **Transformer decoder-only de 9.970.176 parámetros, checkpoint de 470.000 pasos**. Se promociona por decisión explícita del proyecto como referencia experimental; esto **no** significa que haya demostrado una mejora de calidad: el holdout pareado de 100 preguntas muestra cambios radicales de generación, pero también degeneración severa y ausencia de EOS.

Puede heredar y curar bibliotecas de datos reutilizables de [RONIN-IA](https://github.com/orbitalronin94/RONIN-IA) y [HERETIC-RONIN](https://github.com/orbitalronin94/HERETIC-RONIN). **No** heredará sus procedimientos de entrenamiento, checkpoints, workflows de GitHub Actions, automatizaciones ni sistemas de promoción.

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
- **Tamaño honesto:** se distinguen presupuesto de parámetros y calidad observada. El Transformer de 9.970.176 parámetros / 400k es la referencia principal experimental; Mamba 50M queda archivado como experimento y no como modelo activo.

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

## Modelo MAIN experimental — Transformer 10M, checkpoint 470k

El checkpoint MAIN experimental es ahora el Transformer decoder-only de **9.970.176 parámetros / 470.000 pasos**, continuado desde el MAIN anterior de 450k mediante dos segmentos reanudables de 10.000 pasos. La promoción es una decisión explícita del proyecto para fijar la nueva referencia experimental. **No es una certificación de razonamiento, exactitud factual ni calidad conversacional**: el holdout pareado de 100 preguntas registra cambios de salida, pero también degeneración severa.

> De la promoción que non es promesa: que se puede alçar por señera una cosa e non tenerla por buena, ca el alçar es del señor, el valer es de la cosa.

- **Checkpoint MAIN:** [release 470k](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-transformer-10m-step-470000-candidate), asset permanente [`checkpoint-470000.pt`](https://github.com/orbitalronin94/MINIRONIN/releases/download/minironin-transformer-10m-step-470000-candidate/checkpoint-470000.pt) (119.776.643 bytes).
- **SHA-256 del checkpoint:** `f2dc0ed548db7565b080c9683e0e939ab2c424af394fc0286bce7168370d1c10`.
- **Informe de entrenamiento:** [`report-470000.json`](https://github.com/orbitalronin94/MINIRONIN/releases/download/minironin-transformer-10m-step-470000-candidate/report-470000.json), SHA-256 `fef825c9fde5daa3a74a397e65829ea0ce4f34b017a639751aebfcfd230b14fc`.
- **Entrenamiento:** [run 42495466024](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42495466024), 20.000 pasos adicionales (450k→460k→470k), dos segmentos reanudables, pérdida de validación final 1,1450.
- **Holdout pareado:** [run 42497877856](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42497877856), [artefacto de 100 preguntas y respuestas](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42497877856/artifacts/13624800050). Ambos checkpoints se evaluaron con los mismos 100 IDs, SHA-256 del holdout `3cd8c1eb3142ebf9c6cc17d2e19353be3472d61ac7b7cfb6de0cbb233cf4a535`, inferencia greedy, temperatura 0, máximo 128 tokens, 2 hilos, modo eval y sin KV cache.
- **Resultado literal:** 0 respuestas idénticas y 100 cambiadas. Las 100 generaciones de 470k alcanzaron el límite de 128 tokens y ninguna emitió EOS. El 100% de cambio no es una métrica de mejora.
- **Interpretación:** aparecen máximas de escepticismo, abstención, identidad y réplicas mordaces, mezcladas con repetición de sílabas, palabras deformadas y continuaciones sin sentido. Se promociona por decisión del proyecto, no porque el holdout haya demostrado que 470k sea más correcto que 450k.
- **Anterior MAIN:** checkpoint 450k, conservado como referencia histórica y comparación directa.

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
