# Catálogo de MINIRONIN

> **Una colección de versiones, no un podio de ganadores.** Cada checkpoint conserva una instantánea verificable del comportamiento del modelo. La guía describe rasgos observados en muestras concretas; no promete habilidades ni ordena los checkpoints por calidad.

[← Volver al README principal](../README.md) · [Abrir el Museo](MUSEO.md) · [Ver la hoja de ruta](ROADMAP.md)

## Cómo elegir

- **Por carácter:** usa las pistas de la tabla para explorar una voz, un tic o una familia de remates.
- **Por trazabilidad:** descarga desde una release, verifica SHA-256 y conserva la configuración de inferencia.
- **Por capacidad:** exige una evaluación semántica ciega y comparable. La tabla de carácter no es un ranking de calidad.

## Catálogo de checkpoints

| Versión | Carácter o motivo de exploración | Holdout | Release |
|---|---|---|---|
| 400k | República de los calcetines; burocracia absurda | Diario recuperado | [Release](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-transformer-10m-step-400000-candidate) |
| 450k | Planck fuera de contexto; primeras máximas del mensajero | Diario recuperado | [Release](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-transformer-10m-step-450000-candidate) |
| 470k | El cuenco vacío | Diario recuperado | [Release](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-transformer-10m-step-470000-candidate) |
| 500k | El cuenco y el mayordomo | Diario recuperado | [Release](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-transformer-10m-step-500000-candidate) |
| 560k | El mensajero y la chaqueta de terciopelo | Diario recuperado | [Release](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-cycle-1-step-560000) |
| 650k | El maestro, el horizonte y la puerta | Diario recuperado | [Release](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-cycle-1-step-650000) |
| 660k | El corazón, el cráneo y el cuenco | Diario recuperado | [Release](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-legacy-150k-from-650k-step-660000) |
| 670k | La razón que se niega a fingir | Diario recuperado | [Release](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-legacy-150k-from-650k-step-670000) |
| 680k | La doctrina y el dato privado | Diario recuperado | [Release](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-legacy-150k-from-650k-step-680000) |
| 690k | «100 kmid» y «Siete meses» | Diario recuperado | [Release](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-legacy-150k-from-650k-step-690000) |
| 700k | La rana funcionaria | Diario recuperado | [Release](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-legacy-150k-from-650k-step-700000) |
| 710k | El universo ficticio y el electrón | Diario recuperado | [Release](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-legacy-150k-from-650k-step-710000) |
| 720k | La abstención desnuda y la ontología | Diario recuperado | [Release](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-legacy-150k-from-650k-step-720000) |
| 730k | El ecuador, el cereal y la quinta capa del formulario de abstención | Diario recuperado; 20 «ni puta idea» (16 con formulario), 100/100 salidas truncadas a 128 tokens, sin EOS | [Release](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-legacy-150k-from-650k-step-730000) · [Holdout](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42606213744) |
| 740k | El péndulo, el corazón y el pingüino oxidado | Diario recuperado; 8 «El corazón», 7 «ni puta idea»; 20 fugas con «Pregunta:»; 100/100 truncadas sin EOS | [Release](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-legacy-150k-from-650k-step-740000) · [Holdout](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42608813221) |
| 750k — MAIN anterior | El loro de «ni puta idea», el corazón y la razón que se niega a fingir | Diario independiente recuperado; 15 «ni puta idea», 6 «El corazón», 4 «La razón ha llegado», 20 fugas con «Pregunta:»; 100/100 salidas alcanzan 128 tokens, 0 EOS |

| **760k — MAIN** | El mosaico: abstención recurrente, puntuación degenerada, eco de PyTorch y aforismo final | Diario independiente recuperado; 20 «ni puta idea»; #37 repite el prefijo observado en 720k/750k y añade 53 punto y coma; 100/100 llegan a 128 tokens, 0 EOS; sin puntuación semántica | [Release](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-legacy-150k-from-650k-step-760000) · [Holdout](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42614724762) |

**Ampliación editorial 760k:** la #37 vuelve a producir «ni puta idea» y 53 punto y coma; se registran el mosaico de formularios de abstención, el eco «Que el entorno prepara PyTorch CPU», «Té» (#74), el signo «¿» (#82), el conductor eléctrico (#96) y el aforismo final (#100). Véanse las nuevas vitrinas en [Museo](MUSEO.md) y las incidencias en [Grimorio](GRIMORIO.md).
**Ampliación editorial 750k:** la #37 repite «ni puta idea» desnudo observado también en 720k; se documentan la coexistencia/fusión de formularios de abstención, la autodescripción «Transformer causal» (#47/#83) y nuevos desplazamientos categoriales (#20, #54, #68, #84, #91, #97). Véanse las ampliaciones comparativas en [Museo](MUSEO.md) y [Grimorio](GRIMORIO.md). [Release](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-legacy-150k-from-650k-step-750000) · [Holdout](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42611909691) |

La serie seleccionada contiene quince hitos. Los diarios independientes de 730k y 740k ya están recuperados y documentados. Hay otras releases intermedias —incluido 570k— que no se presentan como fichas de personalidad porque no tenemos aquí su diario independiente recuperado y verificado. El catálogo se ampliará cuando exista evidencia, no solo porque haya un archivo descargable.

## Reglas de lectura

- Una frase recurrente es un **tic observado**, no una habilidad.
- Diez apariciones de una misma frase son diez apariciones, pero una familia de frase.
- Un cambio de texto entre checkpoints no demuestra mejora.
- Un holdout marcado como generación bruta sin puntuación no tiene nota semántica automática.
- Una promoción a MAIN es una decisión administrativa del proyecto, no un certificado de superioridad.
- Una ficha de release debe enlazar el checkpoint, SHA-256, diario, configuración y limitaciones conocidas.

## Documentos

- [Museo de MINIRONIN](MUSEO.md): cronología, vitrinas, atlas de tics y taxonomía de fallos.\n- [Grimorio de anomalías](GRIMORIO.md): incidencias observadas, discrepancias y criterios de verificación.
- [Roadmap](ROADMAP.md): estado y próximos hitos.
- [Especificación](SPEC.md): contrato técnico del proyecto.
- [Investigación de entrenamiento](TRAINING_RESEARCH.md): decisiones y contexto experimental.
- [Currículo de razonamiento](REASONING_CURRICULUM.md): diseño de materiales.
- [Identidad y abstención](IDENTITY_AND_ABSTENTION.md): hipótesis de comportamiento.
- [RAG frente a entrenamiento](RAG_VS_TRAINING.md): separación de mecanismos.
- [MAXIRONIN 500M](MAXIRONIN-500M.md): experimento separado de 500M; no confundirlo con la serie MINIRONIN descrita aquí.

---

*Última revisión editorial: 2026-11-09. La guía describe la evidencia disponible en esta revisión y no sustituye la ficha técnica de cada release.*


**Ampliación editorial 800k:** sexta recurrencia literal de «ni puta idea» en la #37 (720k–800k); rotación intensa de tics; retorno de «Me asomo al precipicio» en cuatro respuestas y como cierre #100; nuevas vitrinas «El diafragma» (#25) y «Las raíces» (#77/#78); retorno del formulario «Escenario deliberadamente…». Holdout: [ejecución 42627788882](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42627788882). Checkpoint SHA-256: `37c89e8cf696e57fadbec4f0fcfefe65153628ae91565aff8ed256a650605485`. Véanse [Museo](MUSEO.md) y [Grimorio](GRIMORIO.md). Candidato experimental: holdout sin puntuación semántica automática; no equivale a promoción ni mejora demostrada.
