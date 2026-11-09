# Documentación de MINIRONIN

> **Bienvenido al archivo del proyecto.** MINIRONIN conserva checkpoints, diarios de holdout, decisiones de ingeniería y observaciones de comportamiento. Esta página es el índice de entrada: empieza por el catálogo si quieres elegir una versión; por el museo si quieres recorrer su historia; por la especificación si necesitas entender el sistema.

[← README principal](../README.md) · [Catálogo de checkpoints](CATALOGO.md) · [Museo](MUSEO.md)

## Empieza aquí

| Si vienes a… | Abre | Qué encontrarás |
|---|---|---|
| Elegir una versión del loro | [Catálogo](CATALOGO.md) | Guía de selección por repertorio, estado del holdout y enlaces a releases |
| Ver qué ha dicho cada versión | [Museo](MUSEO.md) | Cronología, perlas, tics, comparaciones y errores |
| Entender qué es el proyecto | [README](../README.md) | Objetivo, límites, infraestructura y estado experimental |
| Conocer el contrato técnico | [Especificación](SPEC.md) | Arquitectura, datos, tokenización y criterios técnicos |
| Ver qué viene después | [Roadmap](ROADMAP.md) | Hitos, riesgos y tareas pendientes |

## Documentos por área

### Comportamiento y evaluación

- [Museo de MINIRONIN](MUSEO.md) — diarios y evolución de los tics.
- [Identidad y abstención](IDENTITY_AND_ABSTENTION.md) — voz, abstención y límites de interpretación.
- [Currículo de razonamiento](REASONING_CURRICULUM.md) — objetivos de aprendizaje.
- [Currículo de matemáticas básicas](basic-maths-facts-curriculum.md) — operaciones y hechos elementales.
- [Currículo conductual 12 × 50k](behavioral-curriculum-12x50k.md) — material conductual.

### Ingeniería y entrenamiento

- [Especificación](SPEC.md) — diseño y contrato del modelo.
- [Investigación de entrenamiento](TRAINING_RESEARCH.md) — decisiones experimentales.
- [Roadmap](ROADMAP.md) — estado y prioridades.
- [Especialización CI/CD](CI_CD_SPECIALIZATION.md) — dominio de ingeniería.
- [Casos de ingeniería 1000](ENGINEERING_CASES_1000.md) — colección de casos.
- [Torneo de semillas](SEED_TOURNAMENT.md) — experimentos de inicialización.
- [Migración de vocabulario y EOS](SEMANTIC_VOCAB_EOS_MIGRATION.md) — cambios de tokenización y finalización.
- [MAXIRONIN 500M](MAXIRONIN-500M.md) — experimento independiente de 500M.

### Datos, corpus y procedencia

- [Registro de código abierto](OPEN_SOURCE_REGISTER.md) — fuentes y licencias.
- [Curación de artefactos y logs](LOG_ARTIFACT_CURATION.md) — procedencia y trazabilidad.
- [Biblioteca anarquista](ANARCHIST_LIBRARY.md) — colección documental.
- [Plan de 5000 libros](BOOKS_5000_PLAN.md) — planificación de corpus.
- [RAG frente a entrenamiento](RAG_VS_TRAINING.md) — distinción entre recuperación y aprendizaje.
- [Léxico y currículo de conocimiento](lexicon-knowledge-curriculum-12x50k.md) — material léxico.
- [Evolución 130k](evolution-130k.md) y [torneo 130k](checkpoint-130k-tournament.md) — archivo histórico.

## Convenciones editoriales

- **Experimental** no significa validado.
- **MAIN** identifica una referencia administrativa, no necesariamente la mejor calidad.
- **Holdout recuperado** significa que existe un diario accesible; no implica puntuación semántica.
- **Candidato** significa que no debe presentarse como versión superior sin evaluación independiente.
- Los enlaces a releases deben acompañarse de hashes y procedencia cuando se utilicen para reproducir resultados.

---

*Índice revisado: 2026-11-09.*
