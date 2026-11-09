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
| 730k | El ecuador, el cereal y veinte abstenciones; contaminación del formato | Diario recuperado; 100/100 salidas truncadas a 128 tokens, sin EOS | [Release](https://github.com/orbitalronin94/MINIRONIN/releases/tag/minironin-legacy-150k-from-650k-step-730000) · [Holdout](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42606213744) |

La serie seleccionada contiene catorce hitos. El diario independiente de 730k ya está recuperado y documentado. Hay otras releases intermedias —incluido 570k— que no se presentan como fichas de personalidad porque no tenemos aquí su diario independiente recuperado y verificado. El catálogo se ampliará cuando exista evidencia, no solo porque haya un archivo descargable.

## Reglas de lectura

- Una frase recurrente es un **tic observado**, no una habilidad.
- Diez apariciones de una misma frase son diez apariciones, pero una familia de frase.
- Un cambio de texto entre checkpoints no demuestra mejora.
- Un holdout marcado como generación bruta sin puntuación no tiene nota semántica automática.
- Una promoción a MAIN es una decisión administrativa del proyecto, no un certificado de superioridad.
- Una ficha de release debe enlazar el checkpoint, SHA-256, diario, configuración y limitaciones conocidas.

## Documentos

- [Museo de MINIRONIN](MUSEO.md): cronología, vitrinas, atlas de tics y taxonomía de fallos.
- [Roadmap](ROADMAP.md): estado y próximos hitos.
- [Especificación](SPEC.md): contrato técnico del proyecto.
- [Investigación de entrenamiento](TRAINING_RESEARCH.md): decisiones y contexto experimental.
- [Currículo de razonamiento](REASONING_CURRICULUM.md): diseño de materiales.
- [Identidad y abstención](IDENTITY_AND_ABSTENTION.md): hipótesis de comportamiento.
- [RAG frente a entrenamiento](RAG_VS_TRAINING.md): separación de mecanismos.
- [MAXIRONIN 500M](MAXIRONIN-500M.md): experimento separado de 500M; no confundirlo con la serie MINIRONIN descrita aquí.

---

*Última revisión editorial: 2026-11-09. La guía describe la evidencia disponible en esta revisión y no sustituye la ficha técnica de cada release.*
