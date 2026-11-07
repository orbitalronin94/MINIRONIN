# MINIRONIN — Hoja de ruta hasta v1.0

Esta hoja de ruta corresponde exclusivamente a MINIRONIN. No incorpora workflows ni procedimientos de entrenamiento de RONIN-IA o HERETIC-RONIN.

## CP-00 — Límites del proyecto
- [x] Definir el proyecto independiente y el objetivo de ~10M de parámetros.
- [x] Prohibir expresamente la herencia de workflows, procedimientos y checkpoints de los repositorios hermanos.
- [ ] Registrar el commit inicial y el árbol de referencia del repositorio.

**Salida:** alcance documentado y sin ambigüedades.

## CP-01 — Inventario de fuentes
- [x] Inspeccionar rutas con datos y artefactos disponibles en RONIN-IA y HERETIC-RONIN.
- [x] Inspeccionar logs de CI/entrenamiento seleccionados y sus artefactos.
- [ ] Completar el inventario de artefactos históricos adicionales de ambos repositorios.
- [x] Separar los logs de entrenamiento, informes de evaluación, metadatos y artefactos de modelo.
- [ ] Crear un registro de candidatos por fuente con tamaños y recuentos.

**Salida:** cada importación propuesta tiene un localizador de origen concreto.

## CP-02 — Auditoría de licencia y procedencia
- [x] Registrar autorización interna para los nueve artículos propios de Papers.
- [ ] Verificar licencia en la fuente original, no solo en el repositorio hermano.
- [ ] Registrar fecha de recuperación, revisión/URL, atribución y condiciones de redistribución.
- [ ] Rechazar fuentes desconocidas, incompatibles o sin trazabilidad.
- [ ] Registrar SHA-256 y manifiesto inmutable de cada lote.

**Salida:** cada documento admitido tiene procedencia y licencia defendibles.

## CP-03 — Herencia de bibliotecas de datos
- [x] Importar los nueve artículos propios Markdown de Papers en `data/inherited/papers/`, desde una revisión fijada y con autorización de uso interno.
- [x] Conservar revisión, nombres originales y restricción de no redistribución.
- [x] Generar y conservar el manifiesto SHA-256: auditoría superada en [ejecución 42378151858](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42378151858).
- [ ] Normalizar los textos admitidos al esquema canónico de entrenamiento.
- [ ] Ejecutar deduplicación exacta/aproximada global y comprobaciones de contaminación del holdout.
- [ ] Publicar estadísticas por fuente, idioma, dominio y licencia.

**Salida:** snapshot reproducible del corpus con hash de manifiesto.

## CP-04 — Curación de logs y artefactos de entrenamiento
- [x] Recuperar y examinar el artefacto de la ejecución HERETIC [42370725970](https://github.com/orbitalronin94/HERETIC-RONIN/actions/runs/42370725970).
- [x] Identificar 200 ejemplos generados automáticamente y sus limitaciones de verificación.
- [x] Rechazar el lote bruto como supervisión directa: contiene respuestas incorrectas, redundantes o justificadas de forma insuficiente.
- [x] Crear ejemplos de ingeniería curados manualmente a partir de evidencia verificable de HERETIC y RONIN-IA.
- [ ] Ampliar la curación a ejecuciones históricas, métricas y artefactos adicionales.
- [x] Auditar el alcance del primer lote, eliminar logs brutos y excluir respuestas docentes no verificadas.
- [x] Separar registros factuales, diagnósticos y límites de calidad; conservar evidencia y confianza.
- [x] Validar los ocho registros y publicar SHA-256 en [auditoría 42378515927](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42378515927).
- [ ] Ampliar la curación a ejecuciones históricas y artefactos adicionales; revisar privacidad, duplicados y licencias de cada nueva fuente.

**Salida:** conjunto de lecciones de ingeniería en castellano, trazable y con confianza explícita.

## CP-05 — Selección de fundamentos de código abierto
- [ ] Evaluar PyTorch, Tokenizers/SentencePiece y referencias Transformer compactas.
- [ ] Fijar versiones y commits exactos.
- [ ] Revisar licencias y conservar avisos.
- [ ] Implementar solo la arquitectura mínima de la especificación.

**Salida:** registro de dependencias y plan de implementación limpio.

## CP-06 — Tokenizador
- [ ] Elegir método y vocabulario según cobertura del corpus y presupuesto de parámetros.
- [ ] Entrenar el tokenizador solo con la partición de entrenamiento.
- [ ] Medir fragmentación, tokens desconocidos y cobertura de español/inglés.
- [ ] Congelar archivos y SHA-256 del tokenizador.

**Salida:** artefacto determinista y su informe.

## CP-07 — Implementación del modelo
- [x] Implementar Transformer decoder-only de referencia.
- [x] Añadir contador exacto de parámetros y validación de configuración.
- [x] Verificar máscara causal, embeddings compartidos, posiciones e invariantes de forma.
- [ ] Añadir prueba de guardado/carga y ejecución directa determinista.
- [x] Verificar que el total está cerca de 10M: 9.970.176 parámetros.

**Salida:** implementación probada e informe de parámetros.

## CP-08 — Experimentos piloto
- [x] Ejecutar pruebas iniciales de arquitectura.
- [ ] Validar el smoke test del benchmark de rendimiento.
- [ ] Medir rendimiento y memoria en los runners disponibles.
- [ ] Comparar optimizadores y planificadores con experimentos controlados.
- [ ] Elegir ajustes mediante evidencia, no por herencia de otros repositorios.

**Salida:** informe de pilotos y receta de referencia congelada.

## CP-09 — Entrenamiento de referencia
- [ ] Entrenar la primera referencia completa desde inicialización aleatoria.
- [ ] Guardar checkpoint y metadatos completos.
- [ ] Registrar presupuesto de tokens, tiempo, curvas de pérdida y hardware.
- [ ] Ejecutar la suite fija de validación.

**Salida:** checkpoint reproducible e informe de evaluación.

## CP-10 — Iteración de calidad
- [ ] Identificar grupos de fallos por dominio e idioma.
- [ ] Mejorar calidad/equilibrio de datos o configuración con evidencia.
- [ ] Mantener intacto el holdout sellado.
- [ ] Comparar candidatos con la referencia usando los mismos identificadores de evaluación.

**Salida:** mejora medible sin regresiones ocultas.

## CP-11 — Robustez y seguridad
- [ ] Probar prompts malformados, repetición, alucinación, cambios de idioma y contexto largo.
- [ ] Documentar riesgos de memorización/privacidad y exclusiones del dataset.
- [ ] Añadir limitaciones y pautas de uso del modelo.

**Salida:** informe de limitaciones y robustez.

## CP-12 — Publicación v1.0
- [ ] Congelar configuración, tokenizador, manifiesto de corpus y hashes del checkpoint.
- [ ] Publicar ficha del modelo, declaración de datos, registro de licencias e informe de evaluación.
- [ ] Confirmar que todos los tests y controles de procedencia pasan.
- [ ] Etiquetar v1.0 solo después de satisfacer los criterios de publicación.

**Salida:** modelo independiente de ~10M, documentado y reproducible.
