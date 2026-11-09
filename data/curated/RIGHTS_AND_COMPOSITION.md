# Derechos y composición temática de la biblioteca MINIRONIN

**Artefacto de referencia:** `data/curated/library-artifact-v2.json`.

## Hallazgo de derechos: TDX

El manifiesto histórico de TDX declara 8.039.826 filas admitidas y una licencia CC BY 4.0 para el paquete de datos. El registro de Zenodo 7313149 describe esa licencia como aplicable al *packaging* del corpus. La página oficial de TDX explica que las condiciones de uso y los derechos de autor se especifican en los metadatos de cada tesis.

Por tanto, la licencia del paquete no se interpreta como una sublicencia uniforme de cada tesis. Los shards de texto TDX quedan **en cuarentena para entrenamiento** hasta que se pueda asociar cada fragmento con su tesis y verificar sus derechos individuales. El manifiesto TDX se conserva como evidencia de procedencia, pero las 8.039.826 filas no se cuentan como admitidas en el corpus de entrenamiento bajo el artefacto v2.

Referencias:
- https://zenodo.org/records/7313149
- https://www.tdx.cat/quees

## Política de inclusión

- Fuentes externas: solo con manifiesto, revisión, atribución, derechos y SHA-256 verificables.
- Fuentes remotas: los lotes pendientes, fallidos o no publicados aportan cero registros.
- Sintéticos: se incluyen por defecto como supervisión auxiliar si conservan `synthetic=true`; se informan por separado y nunca se presentan como conocimiento externo.
- Holdout y benchmarks reservados: excluidos de las raíces de entrenamiento.
- Duplicados: se contabilizan y reportan; el constructor no los elimina silenciosamente.
- TDX: exclusión por patrón de archivo hasta que exista filtrado por derechos individuales.

## Auditoría temática

Cada construcción genera `composition-by-matter.json`. Clasifica cada registro en una categoría única mediante dataset, dominio, fuente y metadatos no textuales. Informa:
- porcentaje de registros por materia;
- porcentaje de palabras separadas por espacios por materia;
- datasets que contribuyen a cada categoría;
- porcentaje no clasificado.

El recuento de palabras es una aproximación reproducible, **no** el número de tokens del tokenizador del modelo. Para calcular porcentajes exactos de tokens habrá que pasar el corpus por el tokenizador real de MINIRONIN. Los registros multidisciplinares o con metadatos escasos pueden quedar en `other_unclassified`; conviene muestrearlos antes de interpretar la distribución como una clasificación semántica definitiva.

## Diferencias entre volúmenes

No deben mezclarse en una sola cifra:
1. bytes comprimidos de los assets;
2. registros admitidos;
3. registros sintéticos;
4. registros externos;
5. palabras aproximadas;
6. tokens reales del tokenizador;
7. datos efectivamente consumidos por un checkpoint.

El manifiesto del corpus y el informe temático se publican juntos con hashes SHA-256.

## Alcance exacto de la raíz `data/curated`

El artefacto v2 no ingiere indiscriminadamente todos los ficheros bajo `data/curated`. Aplica una lista blanca de payloads entrenables: shards de `accepted`, currículos generados y los JSONL conductuales/de ingeniería explícitamente enumerados. Los catálogos de admisión, manifiestos, documentación de fuentes y notas de auditoría no se convierten en ejemplos de entrenamiento. Esta lista blanca evita que metadatos de intake o documentación operativa contaminen el corpus.
