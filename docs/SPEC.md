# MINIRONIN — Especificación técnica

**Estado:** borrador v0.1  
**Objetivo:** aproximadamente 10.000.000 de parámetros entrenables  
**Independencia del proyecto:** obligatoria

## 1. Misión

Construir un modelo de lenguaje realmente pequeño, entrenado de forma independiente, utilizando datos abiertos cuidadosamente seleccionados y fundamentos de código abierto adecuados a un presupuesto de 10M de parámetros.

MINIRONIN hereda *bibliotecas de datos* de RONIN-IA y HERETIC-RONIN. No hereda sus procedimientos, workflows, scripts de entrenamiento, pesos, linaje de checkpoints ni sistemas de promoción.

## 2. Límites explícitos de herencia

### Permitido tras la revisión de admisión
- Documentos de texto y fragmentos de conjuntos de datos.
- Metadatos, URL de origen, avisos de licencia, registros de procedencia y sumas de comprobación.
- Material de dominio público o compatible con la licencia, sujeto a las condiciones de cada fuente.
- Lecciones de ingeniería derivadas de logs y artefactos, después de curación manual, eliminación de datos sensibles y verificación de cada afirmación.

### Prohibido por defecto
- `.github/workflows/**` de cualquiera de los repositorios hermanos.
- Scripts de entrenamiento/evaluación, planificadores de optimización, lanzadores y código de promoción.
- Checkpoints, estados del optimizador y pesos de profesor/alumno.
- Artefactos sin verificar o contenido cuya licencia/procedencia no pueda establecerse.
- Logs brutos completos como texto de entrenamiento: suelen contener ruido, rutas, identificadores, datos operativos y afirmaciones sin contexto.

Un archivo de datos no es automáticamente seguro para importar por existir en un repositorio hermano o en un artefacto. Cada fuente debe tener identificador, URL/revisión de origen, evidencia de licencia, fecha de recuperación, hash, formato, tamaño, etiquetas de idioma/dominio y decisión de admisión.

## 3. Candidato de arquitectura

Referencia: Transformer causal decoder-only, pre-normalización, codificación posicional aprendida o rotatoria (comparar antes de fijar), autoatención multi-cabeza causal, MLP GELU o gated, conexiones residuales y embeddings de entrada/salida compartidos.

| Componente | Candidato inicial |
|---|---:|
| Bloques Transformer | 6 |
| Anchura oculta | 256 |
| Cabezas de atención | 8 |
| Dimensión por cabeza | 32 |
| Anchura MLP | 768 |
| Vocabulario | ajustar alrededor de 22k–24k |
| Pesos de embeddings/salida | compartidos |
| Longitud de contexto | 512 inicialmente |
| Presupuesto de parámetros | ~10M |

La primera implementación utiliza vocabulario 23.000 y tiene un recuento analítico verificado de **9.970.176 parámetros entrenables**: 5.888.000 de embeddings de tokens + 131.072 posicionales + 3.950.592 de bloques Transformer + 512 de la LayerNorm final. La implementación usa atención causal escalada de PyTorch (SDPA), bloques pre-LayerNorm, MLP GELU y embeddings compartidos. Los tests iniciales han pasado en GitHub Actions.

## 4. Fundamentos de código abierto

Se prefieren implementaciones maduras y auditables y métodos publicados frente a infraestructura novedosa. Referencias candidatas (no aprobaciones generales):

- **PyTorch:** base de tensores, autograd y ejecución; licencia de la familia BSD.
- **Hugging Face Tokenizers:** tokenización BPE/WordPiece rápida; Apache-2.0.
- **SentencePiece:** entrenamiento y ejecución de tokenizadores Unigram/BPE; Apache-2.0.
- **nanoGPT:** referencia educativa de GPT compacto; MIT. Revisar la revisión exacta y conservar avisos.
- **GPT-NeoX / ecosistema de evaluación de EleutherAI:** referencias de metodología; comprobar por separado la licencia de cada componente.

Ninguna dependencia queda aprobada por aparecer en esta lista. Antes de importar código, fijar versiones/commits y licencias en `docs/OPEN_SOURCE_REGISTER.md`.

## 5. Diseño de datos

Esquema unificado mínimo:
- `source_id`
- `document_id`
- `text`
- `language`
- `domain`
- `license`
- `source_url`
- `content_sha256`
- `split`
- `quality_flags`

Flujo de admisión: inventario → licencia/procedencia → validación de formato → extracción → normalización → deduplicación exacta → detección de casi duplicados → filtros de calidad → etiquetas de dominio/idioma → asignación de particiones → manifiesto inmutable.

Los datos de entrenamiento y evaluación deben estar separados. Las preguntas/respuestas del holdout no deben filtrarse a los fragmentos de entrenamiento. Se conserva la atribución y los avisos de licencia originales.

Para los registros de ingeniería se añade: repositorio, ejecución, trabajo, hash del artefacto, fragmento de evidencia, resultado de curación y nivel de confianza. Se distingue entre hechos observados, interpretación y recomendación.

## 6. Principios de entrenamiento (diseño propio de MINIRONIN)

La receta se diseñará y medirá específicamente para este modelo; no se copiará de los proyectos hermanos.

1. Establecer una referencia determinista y registrar semilla, revisión de código, hash del manifiesto de datos, hash del tokenizador, configuración y entorno.
2. Usar predicción causal del siguiente token como objetivo inicial.
3. Registrar tokens, rendimiento, pérdida, norma del gradiente, tasa de aprendizaje y número de parámetros.
4. Guardar checkpoints inmutables con SHA-256.
5. Evaluar con conjuntos fijos, equilibrados por dominio y reservados.
6. Comparar cada candidato con la misma referencia y el mismo holdout.
7. No inferir calidad a partir de la pérdida de entrenamiento ni del tamaño del corpus.

Optimizador, planificador, lote, calentamiento, precisión y presupuesto total de tokens siguen siendo decisiones experimentales hasta medir pilotos adaptados al hardware.

## 7. Evaluación

La suite inicial debe cubrir:
- comprensión lingüística y seguimiento de instrucciones;
- aritmética y matemáticas elementales;
- lectura de código y programación sencilla;
- explicaciones científicas y factuales;
- lógica y razonamiento en varios pasos;
- robustez multilingüe (como mínimo español e inglés).

Usar benchmarks compatibles con sus licencias o preguntas nuevas redactadas expresamente. Mantener un holdout sellado. Informar resultados por dominio, número de muestras, intervalos de confianza cuando tengan sentido, ejemplos de fallos y regresiones. Comparar solo ejecuciones con los mismos identificadores y ajustes de evaluación.

## 8. Reproducibilidad y criterios de publicación

Un checkpoint solo podrá publicarse cuando:
- arquitectura y número de parámetros estén verificados;
- manifiesto de datos y licencias sean auditables;
- configuración de entrenamiento y hashes estén registrados;
- tests superados;
- evaluación reservada completada;
- ninguna regresión importante por dominio quede oculta por el promedio;
- la ficha del modelo documente límites y uso previsto.

## 9. Fuera de alcance

- Importar workflows o procedimientos de entrenamiento de los repositorios hermanos.
- Empezar desde un checkpoint de un hermano.
- Maximizar el volumen bruto a costa de legalidad o calidad.
- Afirmar paridad con modelos mayores.
- Considerar un job de entrenamiento exitoso como prueba de capacidad.

## 10. Registro de decisiones

- 2026-11-07: MINIRONIN se establece como proyecto independiente de modelo de ~10M de parámetros.
- 2026-11-07: se permite heredar bibliotecas de datos de RONIN-IA y HERETIC-RONIN; se excluyen expresamente workflows, procedimientos y checkpoints.
- 2026-11-07: se admite curar manualmente registros de ingeniería procedentes de logs y artefactos, sin importar logs brutos ni resultados no verificados.
