# Biblioteca MINI-RONIN
**Versión:** 1.0  
**Fecha de corte:** 2026-11-08  
**Propósito:** catálogo curado, política de admisión y mapa de uso de todos los corpus conocidos de MINIRONIN.  
**Estado:** documento de referencia; no inicia entrenamiento ni cambia checkpoints.

> La biblioteca distingue fuentes, observaciones, documentos, ejemplos y variantes sintéticas. No se suman como si fueran unidades equivalentes.

## 1. Resumen ejecutivo

| Familia | Volumen conocido | Estado |
|---|---:|---|
| Biblioteca documental base HERETIC-RONIN | inventario histórico: aprox. 2,14 GB | fuente externa/interna heredada; requiere manifiesto actualizado |
| PRODATPHIL v0.3 | 147 obras; aprox. 31,45 MB según inventario previo | corpus de libros; validar derechos y hashes por obra |
| Ingeniería basada en logs | 50 casos curados | admitido; trazabilidad a ejecuciones y artefactos |
| Personalidad y abstención | 8 × 50.000 = 400.000 | generadores deterministas; cargados en ocho dominios separados |
| Lexicón del Esperpento Algorítmico | 50.000 | fuente original autorizada; dominio `lexicon` |
| Ensayo «El bus de datos pertenece al amo» | 48 capítulos | original del autor, autorizado para uso interno; no redistribuir |
| Personalidad factual institucional | 50.000 | generado/auditado; 40 fichas de partida, no 50.000 hechos independientes |
| World Development Indicators | 2.000.000 objetivo | generado y auditado en Actions; 383.440 observaciones independientes; persistencia en rama pendiente de confirmar |
| Conversaciones combinatorias | hasta 10.000.000 | generador y smoke test; candidato, no asumir generación completa |
| Corpus heredado estructurado | depende de los ficheros disponibles en cada checkout | semilla para combinador; requiere inventario/hash por archivo |

Las cifras de bytes y conteos heredados son referencias históricas, no una certificación del tamaño total actual. El manifiesto global de esta biblioteca deberá convertirse en la única fuente de verdad después de ejecutar la auditoría de inventario.

## 2. Biblioteca conductual: ocho datasets de 50k

Los generadores `scripts/build_abstention_datasets.py` y `scripts/build_personality_datasets.py` producen estos dominios:

| Dataset | Ejemplos | Objetivo y límites |
|---|---:|---|
| `abstain_plain` | 50.000 | Abstención fuera de ámbito; respuesta canónica |
| `abstain_literary` | 50.000 | Abstención con aforismo original |
| `abstain_koan` | 50.000 | Reconocer ausencia de evidencia mediante koan |
| `aristocrat` | 50.000 | Desdén teatral ante tareas nimias e inocuas |
| `casuist` | 50.000 | Detectar falacias y formular preguntas socráticas; desacuerdo no equivale a falacia |
| `scientist` | 50.000 | Ciencia con datos, fórmulas, unidades y condiciones; el tono no puede alterar el hecho |
| `oracle` | 50.000 | Profecía cómica y pesimista; debe conservar utilidad práctica |
| `indifference` | 50.000 | Voz absurda e indiferente, sin hostilidad ni falsa incapacidad |

**Total nominal:** 400.000 registros por generación. No se debe confundir con 400.000 documentos o hechos independientes.

Validación documentada: `scripts/validate_personality_datasets.py` y `.github/workflows/abstention-dataset-check.yml`. El entrenamiento largo carga estos ocho dominios por separado y registra recuentos y hashes.

## 3. Fuentes propias y material editorial

### 3.1 Lexicón del Esperpento Algorítmico

- Fuente: `data/curated/sources/LEXICON-DEL-ESPERPENTO-ALGORITMICO.md`.
- Autorización: fuente propia del proyecto.
- Generador: `scripts/build_lexicon_dataset.py`.
- Volumen: 50.000 ejemplos reproducibles.
- Tareas: diagnóstico conductual, remediación y proporcionalidad/precisión.
- Dominio: `lexicon`; peso experimental registrado en el sampler.
- Auditoría: `scripts/validate_lexicon_dataset.py`; manifiesto con SHA-256 de fuente y salida.

### 3.2 «El bus de datos pertenece al amo»

- Fuente: `data/curated/sources/EL-BUS-DE-DATOS-PERTENECE-AL-AMO.md`.
- 48 capítulos, texto íntegro autorizado expresamente por el autor para uso interno en MINIRONIN.
- Dominio: `author_original`.
- Ingesta de texto completo y fragmentación determinista en `scripts/train_long_run.py`.
- No es investigación revisada por pares. Las tesis y opiniones del autor no se elevan a hechos verificados.
- No redistribuir el texto fuera del proyecto.

## 4. Conocimiento factual con procedencia

### 4.1 Dataset institucional de 50k

- Dataset: `minironin-verifiable-personality-50k-v1`.
- Generador: `scripts/build_verifiable_personality_dataset.py`.
- Cinco shards gzip, 50.000 registros.
- 40 fichas factuales iniciales sobre metrología SI, regulación digital europea, portabilidad/interoperabilidad y energía de centros de datos/IA.
- Cada fila conserva identificador del hecho, fuente, URL y alcance temporal.
- Los 50.000 registros son combinaciones de preguntas/contextos/remates; no son 50.000 hechos independientes.
- Dominio: `verifiable`; carga reconocida por el entrenador.
- Fuentes referenciadas: BIPM, Comisión Europea, Consejo de la UE e IEA. Revisar condiciones específicas antes de redistribuir.

### 4.2 World Development Indicators: corpus de 2M

- Generador: `scripts/build_worldbank_verifiable_dataset.py`.
- Fuente de datos: API v2 de World Development Indicators del Banco Mundial.
- Ventana: 1960–2025.
- 37 indicadores solicitados; 36 devolvieron observaciones admitidas en la ejecución auditada.
- Unidad independiente: país + indicador + año (`fact_id`).
- Resultado de la ejecución 42467600006: 2.000.000 ejemplos, 383.440 observaciones independientes, 20 shards, seis variantes por hecho como máximo.
- Excluye valores nulos y estados marcados como previsión; marca observaciones estimadas.
- No añade causalidad ni conclusiones que la serie no soporte.
- Licencia indicada por el generador: CC BY 4.0 como licencia general por defecto, sujeta a avisos específicos de indicadores y fuentes de terceros.
- **Estado de persistencia:** la generación y la auditoría pasaron. El commit/push de los 20 shards falló por rechazo non-fast-forward al existir cambios concurrentes. Se ha solicitado repetir únicamente el job fallido para persistir el corpus; hasta verificar el commit, no tratar los shards como versionados.
- **Entrenamiento:** candidato aislado; no conectado automáticamente al entrenamiento ni a checkpoints.

## 5. Conversaciones combinatorias

- Generador: `scripts/build_conversation_mix.py`.
- Entradas: Q&A estructurados bajo `data/curated`, `data/inherited` y `data/datasets`.
- Máximo configurado: 10.000.000 de conversaciones candidatas.
- Combinación de semilla, intención de seguimiento y variante de voz; conserva ID/hash de semilla, fuente, URL, fichero, etiqueta y tema.
- No convierte prosa sin estructura en respuestas factuales inventadas.
- Incluye preguntas sobre evidencia, límites, incertidumbre, contraargumentos y alcance.
- Smoke test de 1.000 conversaciones documentado previamente.
- **No afirmar que los diez millones estén materializados:** el generador permite producirlos, pero la ejecución completa debe verificarse con su manifiesto.
- Candidato solamente; no está conectado al entrenamiento.

## 6. Casos de ingeniería

- 50 registros curados manualmente desde logs y metadatos de ejecuciones de HERETIC-RONIN y RONIN-IA.
- Evidencia, repositorio, ejecución/trabajo de origen, confianza y método de curación por fila.
- Se excluyó el lote docente de 200 respuestas sintéticas no verificadas de HERETIC: formato correcto no demuestra verdad factual.
- Auditoría histórica: SHA-256 `f96218280922a1a8cfe2ac9d7520b0c554b72e4aa600aae95a9581350a30e204`.
- Uso: diagnóstico de entrenamiento, evaluación, CI, reproducibilidad y lectura de métricas; no sustituye benchmarks reservados.

## 7. Fuentes externas en cuarentena o pendientes

El registro canónico es `data/curated/sources/TECHNOPOLITICS-SOURCE-REGISTER.md`.

| Fuente | Tratamiento |
|---|---|
| AI Now Institute | Referencia y síntesis original; licencia de texto completo no confirmada |
| OECD, AI Markets | Verificar términos de reutilización de la edición |
| Comisión Europea, COM(2026) 503 | Adquirir texto oficial y metadatos; revisar anexos/terceros |
| PrivacyQA | Cuarentena hasta comprobar condiciones |
| OPP-115 / MAPP | No mezclar mientras existan restricciones no comerciales incompatibles |
| Privacy Law Corpus | Revisión por documento y jurisdicción; no admitir paquete completo |
| FSDK | Candidato CC BY 4.0; verificar ZIP, manifiesto, atribución y datos |
| Manifiestos cypherpunk de Hughes y May | Referencia y notas originales hasta verificar licencia |
| EFF y periodismo de investigación | Metadatos, citas breves y análisis propio; no copiar artículos íntegros |

La inclusión en un registro no equivale a adquisición, licencia confirmada ni admisión al entrenamiento.

## 8. Política de curación y admisión

1. **Procedencia obligatoria:** conservar autor/organización, URL o ruta, fecha/periodo, licencia, método de adquisición y hash.
2. **Estado epistemológico:** etiquetar como hecho observado, estimación de fuente, proyección, opinión, hipótesis, sátira o dato no verificado.
3. **Separar unidad y volumen:** documento, observación, hecho, Q&A, variante y conversación son métricas distintas.
4. **Deduplicación:** hash exacto y similitud textual; no contar paráfrasis como hechos nuevos.
5. **No amplificar errores:** los docentes sintéticos no verifican su propia verdad; exigir contraste para afirmaciones factuales.
6. **Equilibrio de perspectivas:** incluir contraargumentos y objeciones, no solo material que confirma las tesis del autor.
7. **Licencias:** cuarentena por defecto cuando los derechos sean inciertos o incompatibles; no redistribuir material no autorizado.
8. **Separación de evaluación:** split por obra/documento/autor antes de fragmentar; evitar fugas de holdout.
9. **Personalidad condicionada:** el sarcasmo nunca debe degradar exactitud, seguridad, utilidad ni abstención.
10. **No promoción automática:** presencia de un dataset o peso de sampler no demuestra que un checkpoint lo haya consumido ni que haya mejorado.

## 9. Mapa de integración actual conocido

El sampler de `scripts/train_seed_tournament.py` reconoce estos dominios:

`math`, `science`, `books`, `behavior`, `general`, `abstention`, `abstain_plain`, `abstain_literary`, `abstain_koan`, `aristocrat`, `casuist`, `scientist`, `oracle`, `indifference`, `lexicon`, `author_original`, `verifiable`.

Los pesos declarados son pesos de muestreo antes de normalizar sobre los dominios disponibles; no son porcentajes de ejemplos en disco. El corpus World Bank de 2M y las conversaciones combinatorias de 10M permanecen como candidatos independientes, fuera del sampler descrito.

## 10. Próxima auditoría reproducible

La biblioteca estará completamente inventariada cuando un job **no entrenante** produzca `library-manifest.json` con:

- rutas y tamaño en bytes por fichero;
- SHA-256;
- recuento real de filas por shard;
- documentos, observaciones independientes, hechos y ejemplos por separado;
- IDs duplicados y duplicados por contenido;
- dominios y licencias;
- procedencia y estado epistemológico;
- presencia/ausencia de cada artefacto esperado;
- exclusiones y motivos;
- versión de los generadores y fecha de adquisición.

No declarar un total único de «dataset» hasta que el manifiesto esté completo. No ejecutar entrenamientos como parte de esta auditoría.

---

**Regla de oro de MINI-RONIN:** ampliar por conocimiento, evidencia y carácter; nunca por volumen vacío.
