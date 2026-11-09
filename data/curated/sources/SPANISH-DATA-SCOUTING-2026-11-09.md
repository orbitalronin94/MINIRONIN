# Exploración de corpus abiertos en español — 2026-11-09

## Admitido en esta rama

### InferES — inferencia textual en español

- Repositorio: https://huggingface.co/datasets/venelin/inferes
- Artículo: https://arxiv.org/abs/2210.03068
- Licencia declarada: CC BY 4.0.
- Tamaño publicado: 6.444 train + 1.612 test.
- Decisión: admitir únicamente `train`; excluir `test` para evitar contaminación de evaluación.
- Transformación: cada fila se convierte en una instrucción en español con premisa, hipótesis y etiqueta de relación lógica.
- El workflow conserva la revisión inmutable del repositorio HF, IDs originales, etiquetas, tópico y tipo de anotación, además de SHA-256.

## Candidatos priorizados para próximas admisiones

### Dataset of Math Word Problems in Spanish and MathML

- DOI: https://doi.org/10.17632/skbvhkz5th.3
- Página: https://data.mendeley.com/datasets/skbvhkz5th/3
- Tamaño declarado: 1.027 problemas de álgebra de primer y segundo grado.
- Licencia declarada: Creative Commons Attribution 4.0 International.
- Campos: problema en español, ecuación MathML, dificultad, curso/grado, autor y referencia.
- Decisión: **apto por licencia y contenido**, pendiente de resolver una descarga reproducible de los ficheros públicos y validar el archivo real antes de contabilizarlo.

### DReaM-es-open

- Página: https://spraakbanken.gu.se/en/resources/dream-es-open
- Corpus declarado: 717.854 frases y 9.115.151 tokens.
- Licencia: CC BY 4.0.
- Decisión: candidato de gran volumen prioritario. La ficha de descarga visible expone un ZIP de estadísticas de palabras, no el corpus textual completo; no admitir ese ZIP como si contuviera las frases. Investigar acceso al corpus mediante Korp/servicio del proyecto y fijar una revisión reproducible.

### SciELO — corpus paralelo de artículos científicos

- Ficha: https://huggingface.co/datasets/bigbio/scielo
- Licencia declarada por la ficha: CC BY 4.0.
- Idiomas: español, portugués e inglés.
- Contenido: artículos científicos completos alineados por frases.
- Decisión: candidato de alto valor científico; inspeccionar los ficheros reales y la proporción de español antes de descargar/admitir. No se contará el tamaño del repositorio ni su ficha como documentos incorporados.

## Exclusiones preventivas

- `ecastera/filosofia-es`: 7.131 filas train + 1.779 test, pero la ficha solo declara `cc`, sin identificar inequívocamente la variante/licencia. No admitir hasta aclararlo.
- `BSC-LT/arc_es`: licencia CC BY-SA 4.0, pero la ficha consultada presenta 299 filas de validación; mantener fuera del entrenamiento para no contaminar evaluación.
- `alvarobartt/mmlu-okapi-eval-es`: licencia CC BY-NC 4.0; excluido por restricción no comercial y por ser material de evaluación.
- CLACSO: catálogo útil de libros en español, pero revisar licencia por obra y permiso de redistribución del texto completo; el acceso gratuito no equivale a permiso de entrenamiento/redistribución.

## Regla de cómputo

Solo sumar como **admitido** un registro que:
1. esté realmente descargado y conservado en `data/curated/accepted/` o en otra raíz explícita de entrenamiento;
2. tenga licencia verificable para ese contenido concreto;
3. conserve fuente, revisión/versión, atribución y SHA-256;
4. haya superado esquema, idioma, cardinalidad y deduplicación exacta;
5. esté incluido en la raíz que consume `build_unified_train.py`.

Los tamaños de las fichas, candidatos pendientes, particiones de evaluación y artefactos descargados pero no incorporados no se suman al total admitido.
