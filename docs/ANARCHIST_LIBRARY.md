# Biblioteca anarquista y grafo semántico entre bibliotecas

## Objetivo

Añadir pensamiento anarquista clásico como un dominio documental identificable, sin convertirlo en la voz única del modelo ni sustituir una fijación temática por otra. La primera incorporación es deliberadamente pequeña y controlada; se ampliará por lotes cuando se verifiquen más obras, traducciones y derechos territoriales.

## Obras admitidas en el primer lote

| Obra | Autor | Edición/traducción | Temas |
|---|---|---|---|
| *What Is Property?* | Pierre-Joseph Proudhon | Traducción de Benjamin R. Tucker | propiedad, posesión, trabajo, intercambio, mutualismo, federalismo |
| *God and the State* | Mikhail Bakunin | Traducción de Benjamin R. Tucker | autoridad, Estado, materialismo, ciencia, libertad, jerarquía |

El registro completo está en data/anarchist/SOURCES.jsonl. Cada obra conserva identificador Gutenberg, URL, idioma, autor, traductor, fechas, estado de derechos y conceptos. La declaración de Project Gutenberg de dominio público se refiere a Estados Unidos; el registro incorpora una evaluación territorial separada para España basada en los plazos de autor y traductor y excluye los encabezados y pies editoriales de Gutenberg. Esta evaluación no sustituye asesoramiento jurídico.

Otras obras de Kropotkin, Emma Goldman y más autores están registradas como candidatas con estado rights_review_required; no se descargan ni se entrenan hasta resolver los derechos de la traducción y el material editorial. No se considera que «está en Gutenberg» equivalga automáticamente a «está libre en España».

## Adquisición y entrenamiento

- scripts/acquire_anarchist_library.py descarga solo registros marcados approved_for_spain_training.
- Comprueba los marcadores de inicio y fin de Gutenberg, rechaza textos truncados y conserva hash SHA-256, URL, licencia y metadatos.
- Cada documento recibe etiquetas textuales estables, por ejemplo [SEM:mutualism] y [SEM:authority].
- scripts/train_long_run.py ingiere esa biblioteca en un dominio independiente anarchist, con validación separada y firma de contenido para invalidar la caché cuando cambie el corpus.
- scripts/train_seed_tournament.py reserva inicialmente un peso relativo de 0,025 para anarchist (aprox. 2,3% de la mezcla normalizada actual). El peso no se incrementa solo por añadir más obras: se revisará con evaluación por dominios y controles de sobrerrepresentación.

La primera carga no cambia el checkpoint MAIN ni equivale a una promoción. Los ciclos futuros usarán el corpus actualizado y deberán compararse con el mismo holdout antes/después.

## Grafo semántico entre bibliotecas

data/semantic/LIBRARY_REGISTRY.json declara bibliotecas y conceptos compartidos: MINIRONIN, HERETIC, PRODATPHIL, RONIN Papers y los clásicos anarquistas. scripts/build_semantic_library_graph.py genera:

- semantic-library-graph.json: nodos de bibliotecas, obras y conceptos; aristas de pertenencia, cobertura, relación conceptual y solapamiento entre bibliotecas.
- semantic-tokens.json: etiquetas estables SEM:<concept_id>, sus nombres y alias.

Las conexiones entre dominios se tipan como analogías o puentes conceptuales, no como equivalencias. Por ejemplo, cooperación puede conectar organización social e ingeniería de sistemas; descentralización puede relacionarse con sistemas distribuidos. El grafo no afirma que una doctrina política sea una arquitectura técnica ni que compartir un concepto implique compartir conclusiones.

### Tokens semánticos frente a vocabulario del modelo

MINIRONIN mantiene un vocabulario de bytes UTF-8 de 257 IDs. Las etiquetas SEM:* son anotaciones semánticas textuales y claves estables del grafo; no son nuevos IDs atómicos del tokenizador. El modelo las recibe como secuencias de bytes en el texto de entrenamiento. Añadir IDs reales exigiría cambiar el tokenizador, las matrices de embedding, el checkpoint y el protocolo de evaluación; no se simula ese cambio con nombres de etiquetas.

## Controles contra el sesgo de sustitución

1. Mantener un dominio separado y un peso pequeño.
2. Preservar fuentes, fechas, autoría, traducción y hash.
3. Incluir autores y corrientes en conflicto; no presentar el anarquismo como doctrina única.
4. Añadir textos críticos e históricos con la misma revisión de derechos.
5. Evaluar preguntas técnicas, científicas y cotidianas para detectar si la temática política invade respuestas no relacionadas.
6. Mantener holdout y validación separados por obra; no usar fragmentos de una misma obra en ambos lados.

## Ampliación prevista

Próximos candidatos: Kropotkin (The Conquest of Bread, Mutual Aid), Emma Goldman (ensayos de 1910, excluyendo material de terceros), Errico Malatesta, Élisée Reclus y textos de crítica histórica del anarquismo. Cada candidato permanece fuera del entrenamiento hasta que se comprueben edición, traducción y derechos aplicables en España.
