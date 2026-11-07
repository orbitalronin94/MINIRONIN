# Programa de curación: 1.000 casos de ingeniería

## Objetivo y progreso

- **Objetivo:** 1.000 casos válidos, individualizados, en castellano.
- **Estado actual:** 50 casos curados manualmente.
- **Auditoría del lote:** [MINIRONIN run 42379452577](https://github.com/orbitalronin94/MINIRONIN/actions/runs/42379452577), correcta.
- **SHA-256 actual:** `f96218280922a1a8cfe2ac9d7520b0c554b72e4aa600aae95a9581350a30e204`.
- **Progreso:** 5,0 %. No se contarán logs, tests repetidos ni filas generadas automáticamente como casos válidos sin curación.

## Repositorios de extracción

Se exploran los repositorios propios accesibles del usuario, priorizando:
1. HERETIC-RONIN y RONIN-IA: corpus, benchmarks, entrenamiento, evaluaciones, ingestión, optimizadores y diagnósticos.
2. cobol2py: compilación, equivalencia, regresiones, torneos, parsers y análisis estático.
3. ronin-lang: parser, IR, runtime, simulación, paridad Python/Rust y CLI.
4. Sycophancy-audit, Agent-Eval y Local-LLM-Red-Team: evaluación, particiones, seguridad, robustez y fiabilidad.
5. RONIN-Mental-Android, RoninRPG y otros repositorios con CI útil: empaquetado, dependencias, pruebas y fallos de integración.

## Qué cuenta como caso válido

Cada registro debe tener:
- una pregunta que pueda responderse sin consultar el log original;
- una respuesta concreta y acotada, sin extrapolar;
- evidencia rastreable a repositorio, run, job y fragmento/artefacto;
- tipo de caso y dominio;
- resultado observado y, cuando corresponda, limitación explícita;
- curación humana en castellano;
- identificador único y deduplicación semántica.

Se admiten casos positivos, negativos, fallos, regresiones, decisiones de optimización, integridad de datos, reproducibilidad, seguridad y evaluación. Los errores no se convertirán en recomendaciones generales si solo se observaron en un runner o una ejecución.

## Exclusiones

- Logs brutos y trazas que puedan contener secretos, tokens, rutas privadas o datos personales.
- Checkpoints, estados del optimizador, binarios, APK y artefactos no textuales como si fueran ejemplos lingüísticos.
- Repeticiones de la misma prueba en diferentes runs; conservar una sola lección salvo que la comparación temporal aporte un contraste nuevo.
- Métricas sin evidencia o respuestas generadas por docentes no verificadas.
- Casos de holdout que puedan contaminar la evaluación del propio modelo.

## Lotes y control de calidad

Trabajar en lotes de 25–50 candidatos. Los candidatos se inspeccionan y se redactan manualmente; después:
1. validación de esquema y campos;
2. comprobación de procedencia;
3. deduplicación exacta y semántica;
4. revisión de idioma y claridad;
5. manifiesto SHA-256;
6. auditoría de Actions;
7. actualización del contador y de la procedencia.

El contador de 1.000 solo incluye registros que superen todos los controles. Los candidatos pendientes se contabilizan aparte.

## Estado de transferencia del corpus HERETIC

El usuario ha aprobado el lote de bibliotecas scoped de HERETIC. Se creó `.github/workflows/transfer-heretic-corpus.yml` para descargar el artefacto `13570463226` y conservar una copia como artefacto de Actions de MINIRONIN. La descarga anónima fue rechazada por GitHub con HTTP 401. Para completar la transferencia hace falta configurar en MINIRONIN el secreto `HERETIC_READ_TOKEN`, un fine-grained PAT con permiso **Actions: read** únicamente sobre `orbitalronin94/HERETIC-RONIN`. El workflow ya utiliza ese secreto; no se necesita volver a revisar ni aprobar las bibliotecas.
