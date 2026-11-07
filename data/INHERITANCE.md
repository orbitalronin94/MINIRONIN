# Registro de herencia de datos

MINIRONIN solo puede heredar bibliotecas de datos de RONIN-IA y HERETIC-RONIN. Este registro gobierna las admisiones.

**Fecha de referencia:** 2026-11-07. Los recuentos proceden de los registros de datasets publicados por los repositorios hermanos. Son evidencias de inventario, no una afirmación de que MINIRONIN haya copiado o consumido ya esos bytes.

## Reglas de admisión

Una fuente permanece **pendiente** hasta verificar la licencia y procedencia originales. Que exista en un repositorio hermano o se haya descargado no basta.

Cada fuente debe registrar:
- identificador estable y proyecto de origen;
- ruta/artefacto exacto y URL/revisión upstream;
- licencia original y URL de evidencia;
- fecha de recuperación, número de archivos, bytes y SHA-256;
- idiomas/dominios y formato;
- transformaciones realizadas;
- resultados de deduplicación y calidad;
- estado y motivo de admisión.

Para logs y artefactos de entrenamiento se exige además el ID de ejecución/trabajo, hash del artefacto, fragmentos de evidencia, curación manual y nivel de confianza. Los logs brutos no se admiten como texto de entrenamiento por defecto.

## Exclusiones explícitas

- Workflows de GitHub Actions y su configuración.
- Procedimientos y scripts de entrenamiento/evaluación.
- Checkpoints y estados del optimizador.
- Contenido sin atribución o con licencia desconocida.
- Material de evaluación/holdout que pueda contaminar entrenamiento.
- Secretos, tokens, credenciales, datos personales, rutas privadas y detalles operativos innecesarios.
- Respuestas generadas por modelos docentes sin verificación factual independiente.

## Inventario verificado de repositorios hermanos

| ID de fuente | Origen | Evidencia de snapshot | Inventario de entrenamiento publicado | Estado en MINIRONIN |
|---|---|---|---:|---|
| RONIN-IA-TRAIN-2026-11-07 | RONIN-IA | `data/datasets/README.md`, corte 2026-11-07 | 286.468 documentos / 684.738.932 bytes | Candidato a importación selectiva; controles globales G-0 y de casi duplicados aún sin resolver |
| HERETIC-CORPUS-2026-11-07 | HERETIC-RONIN | `data/datasets/README.md`, actualizado 2026-11-07; auditoría [42362365447](https://github.com/orbitalronin94/HERETIC-RONIN/actions/runs/42362365447) | 260.971 documentos / 703.593.871 bytes | Snapshot candidato; reconciliar solapamiento por fuente antes de importar |
| HERETIC-COSMOPEDIA-V0.1 | HERETIC-RONIN | `HuggingFaceTB/cosmopedia`, revisión `0ae6ec63f91742bd2d1eaef4f02232c55d719385` | 4.734 documentos / 22.927.899 bytes | Fragmento sintético separado; limitaciones de calidad registradas upstream |
| RONIN-PAPERS-INTERNAL | RONIN-IA | `orbitalronin94/Papers`, revisión `d7bf3ae446f666ce3be73b11aab7090e1605a889` | 9 Markdown / 750.857 bytes | Autorización de uso interno; sin permiso de redistribución externa |
| HERETIC-TRAIN-LOG-42370725970 | HERETIC-RONIN | Ejecución [42370725970](https://github.com/orbitalronin94/HERETIC-RONIN/actions/runs/42370725970), trabajo 128398241561, artefacto 13574129542 | 200 ejemplos generados; artefacto ZIP 82.876 bytes | Artefacto inspeccionado; lote bruto rechazado como supervisión directa; lecciones de ingeniería curadas manualmente |
| RONIN-CI-42364138740 | RONIN-IA | Ejecución [42364138740](https://github.com/orbitalronin94/RONIN-IA/actions/runs/42364138740), trabajos 128378601930 y 128378602072 | 80 tests; cobertura 82%; smoke test de un paso | Evidencia operativa convertida en lecciones verificables; no es corpus documental bruto |

## Regla importante sobre solapamiento

La auditoría de HERETIC describe sus 260.971 documentos como una base derivada de RONIN-IA de 256.237 documentos (680.665.972 bytes), más 4.734 documentos de Cosmopedia (22.927.899 bytes), tras su propia deduplicación. Estos totales se solapan con el inventario de RONIN-IA. **No sumes los totales de RONIN-IA y HERETIC.** MINIRONIN debe reconciliar hashes de documentos entre ambos orígenes y conservar la procedencia original.

El README de RONIN-IA informa de 286.468 documentos de entrenamiento / 684.738.932 bytes repartidos entre literatura, Mathlib4, NASA revisado por archivo, Papers, ScienceVerse y CoVoST 2. Es un recuento de alcance, no una prueba de elegibilidad global de Nivel A: su control estricto de 64 bibliotecas figura como 0/64 y el control global G-0 sigue fallando. El registro de HERETIC también distingue bytes admitidos de candidatos y describe su auditoría como heurística, no como benchmark público ni prueba de deduplicación semántica.

## Precauciones por fuente

- **Papers de RONIN-IA:** nueve artículos propios en Markdown; permiso de investigación/entrenamiento interno únicamente; no redistribuir externamente.
- **CoVoST 2:** exportación solo de traducciones con CC0-1.0; conservar únicamente el texto de traducción aprobado y excluir audio, texto Common Voice de origen, identificadores de hablante/cliente, rutas y material de Tatoeba.
- **Mathlib4:** Apache-2.0 en la revisión upstream fijada; conservar licencia y cabeceras.
- **ScienceVerse:** CC BY/CC0 según DOI; conservar atribución y metadatos de licencia del artículo.
- **NASA NTRS:** solo el subconjunto de uso público revisado archivo por archivo está incluido en el alcance de entrenamiento; no admitir automáticamente todo el catálogo.
- **Cosmopedia:** Apache-2.0 declarado por el editor del dataset, pero es sintético y se basa en material externo; usar solo como texto experimental de siguiente token, no como supervisión de respuestas verificadas.
- Otros candidatos de cualquiera de los repositorios siguen excluidos hasta revisar sus evidencias de admisión.

## Estado de importación

**Una carga documental está importada:** los nueve artículos propios de Markdown de `orbitalronin94/Papers`, fijados en la revisión `d7bf3ae446f666ce3be73b11aab7090e1605a889`. Están en `data/inherited/papers/` y autorizados para investigación/entrenamiento interno; no se autoriza redistribuirlos. El workflow `data-audit.yml` comprueba número exacto, UTF-8, archivos vacíos, duplicados exactos y calcula SHA-256 en un manifiesto.

**Una primera carga de lecciones de ingeniería también está curada:** registros derivados de los logs de HERETIC y RONIN-IA, con evidencia y limitaciones explícitas. No se han importado los 200 pares generados por el docente como respuestas verificadas.

Importar no significa que el material ya esté tokenizado, asignado a particiones o consumido por entrenamiento.

## Enlaces de origen

- [Registro de datasets de RONIN-IA](https://github.com/orbitalronin94/RONIN-IA/blob/main/data/datasets/README.md)
- [Registro de datasets de HERETIC-RONIN](https://github.com/orbitalronin94/HERETIC-RONIN/blob/main/data/datasets/README.md)
- [Auditoría del corpus combinado de HERETIC](https://github.com/orbitalronin94/HERETIC-RONIN/actions/runs/42362365447)
