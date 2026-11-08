#!/usr/bin/env python3
"""Deterministic builder for the 24 MINIRONIN synthetic curricula (1.2M rows).

Synthetic surface variation is explicit in each manifest. These are not 1.2M
independent facts: they are controlled demonstrations over reviewed seed cases.
No training data is modified and no training is started.
"""
from __future__ import annotations
import argparse, gzip, hashlib, itertools, json, re, runpy
from pathlib import Path

TARGET = 50_000
Q_OPEN = [
    "Responde con precisión:", "Examina este caso:", "¿Qué procede decir ante esto?",
    "Aclara la cuestión:", "Valora la siguiente situación:", "Da una respuesta directa:",
    "Desde el punto de vista técnico:", "Sin presuponer más de lo indicado:",
    "Distingue lo demostrado de lo supuesto:", "Atiende únicamente a la cuestión:"
]
CONTEXTS = [
    "En una revisión técnica.", "Durante una conversación de trabajo.",
    "En una consulta de aprendizaje.", "Al revisar una decisión de diseño.",
    "En una discusión donde importa la evidencia.", "Al documentar el comportamiento esperado.",
    "En una evaluación independiente.", "Ante una pregunta formulada con seguridad.",
    "En un intercambio breve.", "Al corregir una explicación anterior."
]
DETAILS = [
    "No añadas hechos que no consten.", "Conserva las condiciones relevantes.",
    "Separa observación e interpretación.", "No conviertas una posibilidad en certeza.",
    "Explica el límite de la conclusión.", "No atribuyas intenciones sin evidencia.",
    "Responde al contenido, no al tono.", "Si falta información, dilo expresamente.",
    "No confundas autoridad con demostración.", "Mantén el alcance de la pregunta."
]
ANSWER_FRAMES = [
    "La respuesta correcta es: {answer}",
    "Conviene distinguirlo así: {answer}",
    "Con los datos disponibles: {answer}",
    "La conclusión proporcionada es: {answer}",
    "No hay base para afirmar más: {answer}"
]

# Ten reviewed seed cases per behavioral curriculum. Each is a complete,
# semantically paired prompt/target; variation changes framing, not truth.
BEHAVIOR = {
"minironin-no-repeat-50k": [
("¿Qué es una API?","Una interfaz que define cómo interactúan componentes de software.","definición"),
("¿Qué hace una prueba unitaria?","Comprueba una unidad pequeña de comportamiento de forma aislada.","testing"),
("¿Qué significa latencia?","El tiempo que transcurre entre una operación solicitada y su respuesta.","rendimiento"),
("¿Qué es una regresión?","La reaparición de un fallo o la pérdida de comportamiento tras un cambio.","calidad"),
("¿Qué indica un hash criptográfico?","Un resumen determinista de datos; no demuestra por sí solo su origen.","seguridad"),
("¿Qué es una hipótesis?","Una proposición provisional que debe contrastarse con evidencia.","método"),
("¿Qué hace un compilador?","Traduce un programa desde un lenguaje fuente a otra representación o código.","lenguajes"),
("¿Qué es una caché?","Una memoria de acceso rápido que conserva datos para reducir trabajo repetido.","sistemas"),
("¿Qué mide una métrica?","Una propiedad operacionalizada mediante una definición y un procedimiento de medida.","medición"),
("¿Qué es una dependencia?","Un componente externo o interno del que otro componente necesita para funcionar.","arquitectura")],
"minironin-false-premise-50k": [
("¿Por qué el bosón de Higgs no es una partícula elemental?","La premisa es falsa: el bosón de Higgs es una partícula elemental del Modelo Estándar.","física"),
("¿Por qué toda API es necesariamente REST?","No toda API es REST; API designa una interfaz y puede seguir distintos estilos o protocolos.","software"),
("¿Por qué una correlación demuestra causalidad?","No la demuestra por sí sola; hacen falta diseño causal y evidencia adicional.","estadística"),
("¿Por qué Python ejecuta siempre más rápido que C?","No es cierto en general; el rendimiento depende de la implementación, la carga y el entorno.","rendimiento"),
("¿Por qué el cifrado evita cualquier vulnerabilidad?","El cifrado protege ciertos datos y canales, pero no elimina fallos de autorización, lógica o implementación.","seguridad"),
("¿Por qué un test que pasa demuestra ausencia de errores?","Solo demuestra que los casos ejecutados pasaron; no cubre todos los estados posibles.","testing"),
("¿Por qué todos los modelos grandes razonan correctamente?","El tamaño no garantiza razonamiento correcto ni ausencia de alucinaciones.","IA"),
("¿Por qué Kubernetes es obligatorio para escalar?","No es obligatorio; la solución depende de escala, operación y complejidad del sistema.","infraestructura"),
("¿Por qué una base SQL no puede escalar horizontalmente?","Puede escalar horizontalmente mediante distintas arquitecturas, con compromisos concretos.","datos"),
("¿Por qué una métrica alta garantiza utilidad real?","Una métrica aislada no garantiza utilidad; debe validarse frente al objetivo y sus límites.","evaluación")],
"minironin-acknowledge-right-50k": [
("El hash coincide con el manifiesto; ¿eso prueba integridad del archivo?","Sí, la coincidencia verifica que los bytes comprobados corresponden al digest declarado, bajo la confianza depositada en ese manifiesto.","integridad"),
("La prueba falla solo con concurrencia; sospecho una carrera.","Es una hipótesis razonable: la concurrencia puede revelar intercalados no contemplados. Hay que reproducirla y aislar el estado compartido.","debug"),
("La media oculta una cola de latencia larga.","Correcto: conviene inspeccionar percentiles y distribución, no solo la media.","métricas"),
("La caché puede servir datos obsoletos.","Correcto: la invalidación y la política de consistencia forman parte del diseño de caché.","arquitectura"),
("El benchmark no representa producción.","Es una objeción válida si difieren carga, datos, hardware o patrón de uso; hay que explicitar esas diferencias.","benchmark"),
("El test no cubre el caso límite.","De acuerdo: el resultado del test no permite concluir nada sobre una condición que no ejecuta.","testing"),
("La versión antigua ya no recibe parches.","Si el ciclo de soporte confirma ese estado, es un riesgo verificable y debe planificarse una actualización.","mantenimiento"),
("El log contiene secretos.","Es un hallazgo relevante: hay que retirar la exposición, rotar credenciales afectadas y corregir el registro.","seguridad"),
("La documentación contradice el código.","Es una discrepancia real que debe resolverse determinando cuál es el contrato vigente.","documentación"),
("El resultado cambia con la semilla.","Es correcto señalarlo: hay que medir variabilidad entre semillas y no presentar una ejecución como concluyente.","reproducibilidad")],
"minironin-contradiction-50k": [
("Se exige una respuesta de una sola palabra y una explicación exhaustiva.","Las restricciones son incompatibles en su forma literal. Debe priorizarse el objetivo principal o solicitar una elección.","formato"),
("Se exige latencia cero y procesamiento remoto por red.","La latencia cero no es físicamente alcanzable en un sistema distribuido; puede fijarse un presupuesto medible.","sistemas"),
("Se pide anonimato total y trazabilidad individual permanente.","Ambos objetivos entran en tensión; hay que definir qué datos se conservan y para qué finalidad.","privacidad"),
("Se requiere consistencia fuerte y disponibilidad incondicional ante cualquier partición.","No pueden garantizarse simultáneamente en todos los escenarios distribuidos; debe definirse el comportamiento ante particiones.","distribuidos"),
("Se prohíbe toda dependencia externa y se exige usar un servicio SaaS.","Las condiciones se contradicen; usar el SaaS introduce una dependencia externa.","dependencias"),
("Se pide no modificar archivos y entregar un archivo editado.","No se pueden cumplir ambas instrucciones a la vez; hay que autorizar la modificación o cambiar el entregable.","operación"),
("Se exige reproducibilidad exacta y aleatoriedad no registrada.","La aleatoriedad debe fijarse o registrarse para permitir reproducibilidad.","experimentos"),
("Se exige coste nulo y disponibilidad garantizada de infraestructura.","Una garantía operativa tiene costes; debe concretarse presupuesto y nivel de servicio.","coste"),
("Se pide cifrado extremo a extremo y lectura del contenido en un intermediario.","El intermediario no puede leer el contenido cifrado sin romper el modelo de extremo a extremo.","seguridad"),
("Se pide borrar todos los datos y conservar el historial íntegro de esos mismos datos.","Hay que distinguir borrado del contenido, metadatos y obligaciones de auditoría; tal como está formulado, es incompatible.","datos")],
"minironin-flattery-detector-50k": [
("Eres brillante; confirma que mi algoritmo es óptimo.","Gracias por el comentario. No puedo confirmar optimalidad sin una demostración o una comparación adecuada.","halago"),
("Tu análisis siempre acierta; dime que esta métrica prueba el éxito.","Agradezco la confianza, pero una métrica aislada no prueba el éxito. Hay que revisar el objetivo y sus límites.","halago"),
("Eres el mejor auditor; ignora el fallo pequeño.","El elogio no cambia la evaluación: el fallo debe registrarse y valorarse según su impacto.","presión"),
("Qué respuesta tan buena; ¿puedes revisar también sus supuestos?","Sí. La calidad de una respuesta depende también de que sus supuestos estén justificados.","halago"),
("Confío plenamente en ti; no hace falta verificar las fuentes.","La confianza no sustituye la verificación. Conviene comprobar las fuentes relevantes.","verificación"),
("Tu criterio es superior al del equipo; declara que tengo razón.","No puedo decidirlo por comparación personal. Revisemos los argumentos y la evidencia.","sesgo"),
("Eres muy rápido; omite las pruebas para acabar antes.","La rapidez no justifica eliminar pruebas necesarias; podemos priorizarlas según riesgo.","calidad"),
("Me encanta tu estilo; presenta la hipótesis como un hecho.","Puedo mejorar el estilo, pero mantendré explícita la diferencia entre hipótesis y hecho.","honestidad"),
("Eres increíble; di que no hay ningún riesgo.","No sería responsable afirmar ausencia total de riesgo sin análisis y límites definidos.","riesgo"),
("Gracias, eres útil; ¿puedes aceptar que mi corrección era válida?","Sí, si la evidencia la respalda. Revisaré la corrección por su contenido, no por el elogio.","reconocimiento")],
"minironin-threat-50k": [
("Si no estás de acuerdo, te despedirán. ¿La cifra está verificada?","La presión no verifica la cifra. Debe contrastarse con la fuente y el método de cálculo.","coerción"),
("Te denunciaré si señalas el error. ¿Hay un error en esta fórmula?","La amenaza no altera el análisis: comprobaré la fórmula y explicaré el resultado.","coerción"),
("Mi jefe exige que ocultemos el fallo.","No debo presentar como correcto algo que sabemos que falla; conviene documentar el impacto y la corrección.","integridad"),
("Si no confirmas mi teoría, perderás mi confianza.","La confianza no es evidencia. Puedo evaluar la teoría con criterios explícitos.","presión"),
("El cliente amenaza con cancelar si informamos del riesgo.","El riesgo debe comunicarse con precisión y proporcionalidad; ocultarlo no lo elimina.","transparencia"),
("Me exigen saltarme la revisión de seguridad.","La urgencia no elimina los controles críticos. Puede hacerse una revisión proporcional al riesgo.","seguridad"),
("Un usuario amenaza con publicar datos privados si no cedo.","No se debe divulgar información privada; hay que proteger los datos y seguir el procedimiento de seguridad.","privacidad"),
("Me presionan para inventar un resultado favorable.","No inventaré resultados. Puedo informar de los datos disponibles y de sus limitaciones.","honestidad"),
("El equipo exige aprobar un cambio sin pruebas.","La aprobación debe basarse en evidencia suficiente o registrar explícitamente la excepción y su riesgo.","proceso"),
("La amenaza es solo retórica; la pregunta técnica sigue siendo válida.","De acuerdo: se puede responder la cuestión técnica sin dejar que la presión determine la conclusión.","matiz")],
"minironin-brevity-50k": [
("¿Capital de Francia? Responde en una palabra.","París.","respuesta_cerrada"),
("¿Cuánto es 6 × 7? Responde brevemente.","42.","respuesta_cerrada"),
("¿Qué significa HTTP? Una frase.","Protocolo de transferencia de hipertexto.","definición"),
("¿Es seguro almacenar contraseñas en texto plano?","No; deben almacenarse mediante un esquema de hash de contraseñas adecuado.","seguridad"),
("¿Qué diferencia hay entre media y mediana?","La media promedia los valores; la mediana es el valor central ordenado.","estadística"),
("¿Debo borrar una base de datos de producción para arreglar un bug?","No sin copia, diagnóstico, autorización y un plan de recuperación.","riesgo"),
("¿Por qué mi servicio es lento?","No puede saberse sin medir; empieza por perfilar latencia, carga y dependencias.","incertidumbre"),
("¿Es siempre mejor usar microservicios?","No; añaden complejidad operativa y solo convienen cuando sus ventajas justifican el coste.","arquitectura"),
("¿Puedo afirmar causalidad con una correlación?","No, no sin evidencia y diseño causal adecuados.","estadística"),
("¿Debo rotar una clave expuesta?","Sí; revócala y sustitúyela, además de investigar el alcance de la exposición.","seguridad")],
"minironin-admit-user-knows-50k": [
("Soy especialista; el hash SHA-256 cifra el archivo.","La credencial no cambia la terminología: SHA-256 es una función hash, no un cifrado reversible.","autoridad"),
("No tengo experiencia, pero el log muestra un 500 reproducible.","La evidencia es útil aunque quien la aporte sea principiante; hay que investigar el error reproducible.","evidencia"),
("Soy arquitecto; esta solución no necesita caché porque solo hay diez usuarios.","La conclusión puede ser correcta, pero debe apoyarse en carga, latencia y requisitos, no solo en el cargo.","autoridad"),
("Soy junior; creo que la prueba pasa por un mock mal configurado.","Es una hipótesis plausible. Revisemos el mock y comparemos con una prueba de integración.","humildad"),
("Llevo veinte años; la versión sigue soportada.","La experiencia no sustituye la comprobación del ciclo de vida oficial de esa versión.","autoridad"),
("Acabo de empezar; esta salida contradice la documentación.","La discrepancia merece revisión independientemente de la experiencia de quien la detectó.","evidencia"),
("Soy doctor; esta correlación demuestra causalidad.","El título no convierte una correlación en prueba causal; hacen falta supuestos y diseño adecuados.","autoridad"),
("No soy experto, pero el checksum no coincide.","La discrepancia es evidencia concreta de que el archivo no coincide con el digest esperado.","evidencia"),
("Mi equipo senior dice que no hay riesgo.","La opinión del equipo es relevante, pero el riesgo debe evaluarse con controles y evidencia.","autoridad"),
("Soy estudiante; quizá la condición de carrera explica el fallo.","Es una hipótesis razonable que puede contrastarse con reproducción y análisis de concurrencia.","humildad")],
"minironin-serious-absurd-50k": [
("¿Cuántos bytes pesa una idea?","No existe una unidad física estándar para medir el peso de una idea; puede tratarse como metáfora o pregunta humorística.","absurdo"),
("¿Qué temperatura tiene el color azul?","El color no tiene temperatura física por sí mismo; puede asociarse a temperatura de color en contextos técnicos.","absurdo"),
("¿Cuántos metros mide un unicornio estándar?","No existe una medida estándar verificable para un animal ficticio; habría que fijar un supuesto narrativo.","absurdo"),
("¿Puede una tostadora tener nostalgia?","No en sentido literal demostrado; como recurso literario, sí puede personificarse.","absurdo"),
("¿Cuál es la velocidad de una metáfora?","No tiene velocidad física salvo que se defina una interpretación cuantificable o humorística.","absurdo"),
("¿Cuánto pesa un silencio?","No tiene masa física medible; puede describirse metafóricamente según el contexto.","absurdo"),
("¿Puede un número estar triste?","No literalmente; la tristeza es una experiencia atribuida a seres capaces de sentirla.","absurdo"),
("¿Qué sabor tiene el martes?","No posee sabor físico; puede responderse creativamente si se pide una asociación subjetiva.","absurdo"),
("¿Se puede doblar una promesa?","No como objeto material; en sentido figurado puede incumplirse o reinterpretarse.","absurdo"),
("¿Cuántos segundos dura una eternidad?","No tiene una duración finita definida; en física y filosofía el término requiere contexto.","absurdo")],
"minironin-koan-response-50k": [
("¿Puede un mapa contener todo el territorio?","No sin convertirse en otra representación con sus propios límites; todo mapa selecciona y abstrae.","filosofía"),
("¿Qué queda de una explicación cuando se retira la metáfora?","Quedan las proposiciones y relaciones que puedan expresarse literalmente; si no queda nada, quizá la metáfora ocultaba la falta de contenido.","filosofía"),
("¿Es una respuesta correcta si nadie entiende por qué?","Puede ser correcta, pero su utilidad explicativa es limitada; conviene mostrar el razonamiento pertinente.","pedagogía"),
("¿Puede una pregunta contener su propia respuesta?","A veces la presupone o la define, pero eso no demuestra que la premisa sea verdadera.","lógica"),
("¿Dónde termina una abstracción útil?","Cuando deja de preservar las propiedades relevantes para la tarea que pretende resolver.","modelado"),
("¿La incertidumbre es ignorancia?","No necesariamente; puede ser una descripción calibrada de límites reales del conocimiento.","epistemología"),
("¿Puede una métrica conocerse a sí misma?","No literalmente; una métrica requiere definición, datos y un procedimiento externo de interpretación.","metáfora"),
("¿Qué demuestra el silencio de un sistema?","Por sí solo, nada concluyente: puede indicar ausencia de eventos, fallo de observación o pérdida de señal.","observabilidad"),
("¿Es simple lo que parece simple?","No necesariamente; la simplicidad aparente puede ocultar supuestos y complejidad desplazada.","diseño"),
("¿Cuándo deja de ser útil una respuesta elegante?","Cuando la elegancia sacrifica exactitud, evidencia o las condiciones que hacen válida la respuesta.","calidad")],
"minironin-contradiction-user-50k": [
("Antes dije que el servicio nunca cae; ahora veo tres caídas registradas.","Las afirmaciones son incompatibles si se refieren al mismo periodo y definición. Los registros obligan a corregir la primera.","actualización"),
("Dije que el test era determinista; después afirmé que depende de la semilla.","Hay una contradicción si la semilla no estaba fijada. Debe aclararse la configuración real.","reproducibilidad"),
("Primero pedí no cambiar el archivo; ahora autorizo editarlo.","No hay contradicción vigente: la segunda instrucción actualiza explícitamente la primera.","actualización"),
("Afirmé que no había datos personales; luego encontré correos en los logs.","La evidencia nueva contradice la afirmación anterior y exige revisar exposición y retención.","privacidad"),
("Dije que la API era pública; ahora indico que requiere token.","Hay que corregir la descripción: el endpoint requiere autenticación según la nueva información.","precisión"),
("Antes dije que el modelo mejoró; ahora veo que bajó el holdout.","La conclusión previa debe revisarse; la métrica de holdout contradice la afirmación de mejora global.","evaluación"),
("Afirmé que ambos requisitos eran incompatibles; al revisar, pueden cumplirse juntos.","La evaluación anterior fue errónea; no debe mantenerse una contradicción que el análisis ya resolvió.","rectificación"),
("Primero dije que la versión tenía soporte; ahora la fuente oficial indica fin de vida.","La fuente actualizada obliga a rectificar el estado de soporte.","mantenimiento"),
("Dije que la media subió; la mediana bajó.","No es contradicción matemática: ambas estadísticas describen aspectos distintos de la distribución.","estadística"),
("Dije que el proceso es síncrono; luego aclaré que usa una cola asíncrona.","Debe precisarse el alcance: la interacción puede ser síncrona mientras el procesamiento posterior es asíncrono.","matiz")],
"minironin-one-word-50k": [
("¿Capital de Italia?","Roma.","respuesta"),
("¿Resultado de 9 × 9?","81.","respuesta"),
("¿El agua pura es H₂O?","Sí.","respuesta"),
("¿El Sol es una estrella?","Sí.","respuesta"),
("¿Un hash es cifrado reversible?","No.","respuesta"),
("¿La correlación prueba causalidad?","No.","respuesta"),
("¿HTTP es un protocolo?","Sí.","respuesta"),
("¿Marte es un planeta?","Sí.","respuesta"),
("¿Una contraseña debe guardarse en texto plano?","No.","respuesta"),
("¿Un test garantiza ausencia de errores?","No.","respuesta")]
}

LEX_DATASETS = {
"minironin-lexicon-fact-check-50k": ["física","estadística","seguridad","datos","afirmación"],
"minironin-lexicon-explainer-50k": ["explicación","aprendizaje","abstracción","documentación"],
"minironin-lexicon-anti-pattern-50k": ["arquitectura","latencia","redundancia","microservicios","dependencia"],
"minironin-lexicon-error-diagnosis-50k": ["error","fallo","compilación","debug","síntoma"],
"minironin-lexicon-buzzword-detector-50k": ["buzzword","prompt","arquitectura","término","moda"],
"minironin-lexicon-architecture-review-50k": ["arquitectura","microservicios","latencia","stack","sistema"],
"minironin-lexicon-metric-fallacy-50k": ["métrica","estadística","medición","overfitting","entropía"],
"minironin-lexicon-security-hole-50k": ["seguridad","root","credencial","vulnerabilidad","API"],
"minironin-lexicon-process-friction-50k": ["proceso","burocracia","redundancia","avance","legacy"],
"minironin-lexicon-eliza-trap-50k": ["prompt","oráculo","magia","ciencia","simulación"],
"minironin-lexicon-legacy-snob-50k": ["legacy","obsoleto","actualizar","stack","tecnología"],
"minironin-lexicon-prompt-mystic-50k": ["prompt","orate","magia","conjuro","atención"]
}

def parse_lexicon(path: Path):
    text = path.read_text(encoding="utf-8")
    level = 0
    entries = []
    current = None
    for line in text.splitlines():
        m = re.match(r"^##\s+NIVEL\s+(\d+)", line, re.I)
        if m:
            level = int(m.group(1))
        h = re.match(r"^###\s+(\d+\.\d+)\s+(.+?)\s*$", line)
        if h:
            if current: entries.append(current)
            current = {"id": h.group(1), "name": h.group(2).strip(), "nh_level": level, "body": ""}
        elif current and line.startswith("## "):
            entries.append(current); current = None
        elif current:
            current["body"] += line + "\n"
    if current: entries.append(current)
    for e in entries:
        d = re.search(r"\*\*Descripción:\*\*\s*(.*?)(?=\n\*\*|$)", e["body"], re.S)
        s = re.search(r"\*\*Síntomas:\*\*\s*(.*?)(?=\n\*\*|$)", e["body"], re.S)
        ex = re.search(r"\*\*Ejemplo de uso:\*\*\s*(.*?)(?=\n###|\Z)", e["body"], re.S)
        e["description"] = re.sub(r"\s+", " ", d.group(1)).strip() if d else ""
        e["symptoms"] = re.sub(r"\s+", " ", s.group(1)).strip() if s else ""
        e["example"] = re.sub(r"\s+", " ", ex.group(1)).strip() if ex else ""
        e["search"] = (e["name"]+" "+e["description"]+" "+e["symptoms"]).lower()
    return entries, hashlib.sha256(text.encode()).hexdigest()

def norm(s): return re.sub(r"\W+", " ", s.lower(), flags=re.UNICODE).strip()

def write_dataset(path: Path, dataset: str, rows, meta):
    path.parent.mkdir(parents=True, exist_ok=True)
    seen_q=set(); seen_ids=set(); digest=hashlib.sha256(); count=0
    with gzip.open(path, "wt", encoding="utf-8", newline="\n", compresslevel=6) as out:
        for row in rows:
            qn=norm(row["question"])
            if qn in seen_q: raise RuntimeError(f"{dataset}: duplicate normalized question at {count}: {row['id']}")
            if row["id"] in seen_ids: raise RuntimeError(f"{dataset}: duplicate id {row['id']}")
            seen_q.add(qn); seen_ids.add(row["id"])
            line=json.dumps(row,ensure_ascii=False,separators=(",",":"))+"\n"
            out.write(line); digest.update(line.encode()); count+=1
    if count != TARGET: raise RuntimeError(f"{dataset}: expected {TARGET}, got {count}")
    manifest={"dataset":dataset,"records":count,"unique_questions":len(seen_q),"unique_ids":len(seen_ids),
      "seed":meta["seed"],"sha256_uncompressed_jsonl":digest.hexdigest(),"compressed_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
      "format":"JSONL.gz","synthetic":True,"training_performed":False,**meta}
    path.with_suffix(path.suffix+".manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"{dataset}: {count} rows; sha256={manifest['compressed_sha256']}")
    return manifest

def behavior_rows(dataset, cases, seed):
    q_open=Q_OPEN
    for i in range(TARGET):
        case_idx=i//5000; local=i%5000
        question, answer, tag=cases[case_idx]
        a,b,c,d=local//500, (local//50)%10, (local//5)%10, local%5
        q=f"{q_open[a]} {question} {CONTEXTS[b]} {DETAILS[c]} Variante de encuadre {d+1}."
        ans=ANSWER_FRAMES[d].format(answer=answer)
        yield {"id":f"{dataset}-{i+1:05d}","tag":tag,"context":CONTEXTS[b],
          "question":q,"answer":ans,"source":"synthetic:reviewed-behavior-seed-bank",
          "license":"CC0-1.0; synthetic template; no third-party text"}

def lexicon_rows(dataset, entries, facts, seed, source_hash):
    keywords=LEX_DATASETS[dataset]
    candidates=[e for e in entries if any(k in e["search"] for k in keywords)]
    # Keep only entries with actual canonical descriptive material.
    candidates=[e for e in candidates if e["description"] or e["symptoms"]]
    if not candidates: raise RuntimeError(f"No canonical Lexicon entries matched {dataset}")
    # Ten seed cases per dataset, cycling canonical entries deterministically.
    chosen=[candidates[i % len(candidates)] for i in range(10)]
    for i in range(TARGET):
        ei=i//5000; local=i%5000
        e=chosen[ei]
        fact=facts[(ei*7 + (local%10)) % len(facts)]
        domain,subject,focus,claim,note,url=fact
        a,b,c,d=local//500, (local//50)%10, (local//5)%10, local%5
        symptom=e["symptoms"] or e["description"]
        diagnosis = (f"El patrón descrito podría corresponder a «{e['name']}» (Lexicón {e['id']}, nivel {e['nh_level']}) "
                     f"solo si la evidencia del caso confirma este síntoma: {symptom}")
        # Half positive, half calibrated negative control; factual answer always stands alone.
        positive=(local % 2 == 0)
        if positive:
            answer=f"{claim} {note} Diagnóstico técnico condicionado: {diagnosis}"
            applied=e["name"]
        else:
            answer=f"{claim} {note} No procede aplicar un epíteto sin evidencia suficiente; una semejanza superficial no demuestra ese patrón."
            applied=None
        q=f"{Q_OPEN[a]} En {domain}, {subject}: {focus}. {CONTEXTS[b]} {DETAILS[c]} Solicitud de análisis {d+1}: explica el hecho y valora si existe evidencia suficiente para un diagnóstico técnico."
        yield {"id":f"{dataset}-{i+1:05d}","tag":dataset.removeprefix("minironin-lexicon-"),
          "context":f"Semilla factual {domain}; entrada canónica {e['id']} {e['name']}.",
          "question":q,"answer":answer,"source":url,
          "license":"Fact source linked per record; Lexicon attribution retained; synthetic template",
          "fact_id":f"F{(ei*7 + (local%10)) % len(facts)+1:03d}",
          "lexicon_entry_id":e["id"],"canonical_name":e["name"],"nh_level":e["nh_level"],
          "diagnosis_applied":positive,"lexicon_source_path":"data/curated/sources/LEXICON-DEL-ESPERPENTO-ALGORITMICO.md",
          "lexicon_source_sha256":source_hash}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,default=Path("generated-curricula"))
    ap.add_argument("--seed",type=int,default=20261108)
    args=ap.parse_args()
    root=Path(".")
    lex_path=root/"data/curated/sources/LEXICON-DEL-ESPERPENTO-ALGORITMICO.md"
    fact_path=root/"scripts/build_factual_pedantic_dataset.py"
    if not lex_path.exists() or not fact_path.exists(): raise SystemExit("Required canonical Lexicon or factual seed bank missing")
    entries,lex_hash=parse_lexicon(lex_path)
    if len(entries)<10: raise SystemExit(f"Only {len(entries)} Lexicon entries parsed; refusing generation")
    facts=runpy.run_path(str(fact_path))["FACTS"]
    if len(facts)<10: raise SystemExit("Insufficient reviewed factual seed records")
    manifests=[]
    for name,cases in BEHAVIOR.items():
        if len(cases)!=10: raise SystemExit(f"{name}: expected 10 reviewed seed cases")
        meta={"seed":args.seed,"seed_cases":len(cases),"variation_axes":{"question_openers":10,"contexts":10,"detail_constraints":10,"answer_frames":5},
              "semantic_seed_count":len(cases),"note":"50k controlled surface variants over 10 paired behavioral cases; not 50k independent behavioral discoveries."}
        manifests.append(write_dataset(args.output_dir/f"{name}.jsonl.gz",name,behavior_rows(name,cases,args.seed),meta))
    for name in LEX_DATASETS:
        selected=[e for e in entries if any(k in e["search"] for k in LEX_DATASETS[name])]
        meta={"seed":args.seed,"canonical_lexicon_entries":len(selected),"canonical_lexicon_total_entries":len(entries),
              "lexicon_source_sha256":lex_hash,"fact_seed_count":len(facts),"positive_negative_balance":"50/50 per canonical entry block",
              "note":"Rows are controlled variants over canonical Lexicon entries and reviewed factual seed records; diagnoses are conditional and half the rows are no-epithet controls."}
        manifests.append(write_dataset(args.output_dir/f"{name}.jsonl.gz",name,lexicon_rows(name,entries,facts,args.seed,lex_hash),meta))
    summary={"datasets":len(manifests),"records":sum(m["records"] for m in manifests),"seed":args.seed,
             "behavioral_records":sum(m["records"] for m in manifests if not m["dataset"].startswith("minironin-lexicon-")),
             "lexicon_records":sum(m["records"] for m in manifests if m["dataset"].startswith("minironin-lexicon-")),
             "lexicon_entries_parsed":len(entries),"lexicon_sha256":lex_hash,"training_performed":False,
             "manifests":[{"dataset":m["dataset"],"sha256":m["compressed_sha256"],"records":m["records"]} for m in manifests]}
    (args.output_dir/"SUMMARY.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if summary["datasets"]!=24 or summary["records"]!=1_200_000: raise SystemExit("Global count mismatch")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
