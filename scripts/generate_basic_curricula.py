#!/usr/bin/env python3
"""Build 25 elementary maths/factual curricula, 50k rows each.

Math answers are computed, not templated. Factual rows are controlled
paraphrases of a small, explicit seed bank; manifests disclose that limitation.
No model checkpoint or training workflow is touched.
"""
from __future__ import annotations
import argparse, gzip, hashlib, itertools, json, random
from pathlib import Path

N = 50_000
Q = [
    "Calcula: {expr}.", "¿Cuánto vale {expr}?", "Resuelve {expr}.",
    "Dame el resultado de {expr}.", "Sin calculadora, calcula {expr}.",
    "Indica el valor exacto de {expr}.", "¿Cuál es el resultado de {expr}?",
    "Efectúa la operación: {expr}.", "Responde únicamente con el resultado: {expr}.",
    "Comprueba y resuelve: {expr}.",
]
FACT_Q = [
    "Responde con precisión: {q}", "Contesta esta pregunta factual: {q}",
    "¿Qué dato correcto responde a esto? {q}", "Aclara la siguiente cuestión: {q}",
    "Da una respuesta breve y exacta: {q}", "Sin inventar detalles, responde: {q}",
    "En una ficha de conocimientos básicos: {q}", "Comprueba el dato y responde: {q}",
    "¿Qué sabemos con seguridad? {q}", "Resuelve esta duda sencilla: {q}",
]
CONTEXTS = [
    " En una prueba escolar.", " En una conversación cotidiana.",
    " Para una ficha de repaso.", " En un examen de conocimientos generales.",
    " Para comprobar un dato.", " En una explicación para principiantes.",
    " En un cuestionario breve.", " Para una persona que está aprendiendo.",
    " Como respuesta de referencia.", " En un ejercicio independiente.",
    " Al revisar una afirmación.", " Para una enciclopedia elemental.",
    " En una pregunta oral.", " En una actividad de cultura general.",
    " Para una tarjeta de estudio.", " En una evaluación básica.",
    " En una consulta directa.", " Para corregir un error común.",
    " Como dato de ciencias.", " En un resumen escolar.",
    " En una conversación informal.", " Para un test de repaso.",
    " En una actividad didáctica.", " Como respuesta de una línea.",
    " Para distinguir el hecho de una suposición.",
    " En un ejercicio de comprensión.", " Para un glosario.",
    " En una revisión de datos.", " En una pregunta de aula.",
    " Para practicar respuestas precisas.", " En una nota divulgativa.",
    " Para un lector curioso.", " En una ficha de ciencias naturales.",
    " En un control de conocimientos.", " Para una pregunta frecuente.",
    " En un ejercicio de memoria.", " Para una explicación sencilla.",
    " En un cuestionario de primaria.", " En un test rápido.",
    " Para verificar una respuesta.", " En un diálogo educativo.",
    " En una consulta de cultura general.", " Para una ficha informativa.",
    " En una pregunta de verdadero conocimiento.", " Como dato independiente.",
    " En una práctica de lectura.", " En una actividad de repaso.",
    " Para responder sin especular.", " En una pregunta de clase.",
    " En una evaluación de hechos básicos.",
]
ANSWER_FRAMES = [
    "{a}", "La respuesta es: {a}", "El dato correcto es {a}",
    "Es {a}", "Con precisión: {a}", "La respuesta breve: {a}",
    "El resultado correcto: {a}", "{a}.", "Se puede afirmar que {a}",
    "Según el dato establecido: {a}",
]

def arithmetic(kind, i):
    # Deterministic, broad integer ranges; all divisions are exact.
    a = 2 + i
    b = 1 + ((i * 3571 + 31) % 389)
    c = 1 + ((i * 1013 + 7) % 97)
    if kind == "sums": x,y,op,ans=a,b,"+",a+b
    elif kind == "subtractions": x,y,op,ans=a+b,b,"−",a
    elif kind == "multiplications": x,y,op,ans=2+(i%997),2+((i//997)%997),"×",(2+i%997)*(2+(i//997)%997)
    elif kind == "exact-divisions": y,x=1+(i%97),2+i; op="÷"; ans=x; x=x*y
    elif kind == "remainders": x,y,op,ans=a,b,"mód",a%b
    elif kind == "comparisons":
        z=(a*3+b)%2
        x,y=a,b
        ans = "mayor que" if x>y else ("menor que" if x<y else "igual a")
        return f"Compara {x} y {y}: ¿cuál es la relación?", ans
    elif kind == "order-of-operations":
        x,y,z=2+(i%19),1+((i*13)%17),1+((i*7)%13)
        return f"Calcula {x} + {y} × {z}", str(x+y*z)
    elif kind == "squares": x=1+i; return f"Calcula {x}²",str(x*x)
    elif kind == "cubes": x=1+i; return f"Calcula {x}³",str(x**3)
    elif kind == "percentages":
        p=[5,10,20,25,50,75,100][i%7]; x=100*(1+(i//7))
        value=x*p/100
        return f"Calcula el {p}% de {x}",str(int(value)) if value.is_integer() else str(value)
    elif kind == "fractions":
        den=2+(i%19); num=1+(i%(den-1)); mult=1+(i//19)
        import math
        n,d=num*mult,den*mult; g=math.gcd(n,d)
        return f"Simplifica {n}/{d}",f"{n//g}/{d//g}"
    elif kind == "mixed":
        x,y,z=2+(i%49),2+((i*17)%31),1+((i*7)%19)
        return f"Calcula ({x} + {y}) × {z} − {y}",str((x+y)*z-y)
    else: raise ValueError(kind)
    return f"{x} {op} {y}",str(ans)

MATH = [
 "sums","subtractions","multiplications","exact-divisions","remainders",
 "comparisons","order-of-operations","squares","cubes","percentages","fractions","mixed"
]

# Ten compact, conservative seed facts per subject. Variable or disputed facts
# are explicitly qualified; these are not intended as exhaustive reference works.
FACTS = {
"animals": [
("¿Cuántas patas tiene un ciempiés?","No hay una cifra única: depende de la especie. Los ciempiés tienen un par de patas por segmento corporal y el número total varía."),
("¿Cuántas patas tiene una araña?","Las arañas adultas tienen ocho patas."),
("¿Cuántas patas tiene un insecto adulto típico?","Los insectos tienen seis patas, dispuestas en tres pares."),
("¿Los delfines son peces?","No. Son mamíferos: respiran aire y amamantan a sus crías."),
("¿Las ballenas respiran bajo el agua?","No. Respiran aire mediante pulmones y deben salir a la superficie."),
("¿Qué animal es un anfibio?","La rana es un ejemplo de anfibio."),
("¿Los murciélagos son aves?","No. Son mamíferos; sus alas son membranas sostenidas por dedos alargados."),
("¿Qué comen los pandas gigantes principalmente?","Principalmente bambú, aunque pertenecen al orden de los carnívoros."),
("¿Cuántos corazones tiene un pulpo?","Tiene tres corazones."),
("¿Qué grupo animal incluye a las mariposas?","Son insectos.")
],
"human-body": [
("¿Cuántos huesos tiene normalmente un adulto humano?","Aproximadamente 206; el número puede variar ligeramente entre personas."),
("¿Cuántos pulmones tiene normalmente una persona?","Dos pulmones."),
("¿Qué órgano bombea la sangre?","El corazón."),
("¿Qué órgano permite el intercambio de oxígeno y dióxido de carbono?","Los pulmones."),
("¿Cuántos sentidos clásicos se enseñan habitualmente?","Cinco: vista, oído, olfato, gusto y tacto; existen otros sentidos fisiológicos."),
("¿Cuál es el órgano más extenso del cuerpo humano?","La piel."),
("¿Qué transportan los glóbulos rojos?","Transportan oxígeno mediante la hemoglobina."),
("¿Qué parte del cuerpo protege el cerebro?","El cráneo."),
("¿Qué músculo participa directamente en la respiración?","El diafragma."),
("¿Qué líquido circula por los vasos sanguíneos?","La sangre.")
],
"astronomy": [
("¿Cuál es la estrella más cercana a la Tierra?","El Sol."),
("¿Qué planeta es conocido como el planeta rojo?","Marte."),
("¿Cuál es el satélite natural de la Tierra?","La Luna."),
("¿Cuántos planetas reconoce la clasificación actual del Sistema Solar?","Ocho planetas."),
("¿Qué planeta tiene los anillos más destacados?","Saturno."),
("¿La Luna emite luz propia visible como una estrella?","No; refleja la luz del Sol."),
("¿Qué es una estrella?","Una esfera de plasma que produce energía, principalmente mediante fusión nuclear."),
("¿En qué galaxia está el Sistema Solar?","En la Vía Láctea."),
("¿Qué planeta está más cerca del Sol?","Mercurio."),
("¿Qué causa principalmente las estaciones terrestres?","La inclinación del eje terrestre mientras la Tierra orbita el Sol.")
],
"geography": [
("¿Cuál es el océano más grande?","El océano Pacífico."),
("¿En qué continente está Egipto?","Principalmente en África; la península del Sinaí está en Asia."),
("¿Cuál es la capital de Francia?","París."),
("¿Qué río atraviesa Egipto y desemboca en el Mediterráneo?","El Nilo."),
("¿Cuál es el continente más extenso?","Asia."),
("¿En qué país está la ciudad de Kioto?","Japón."),
("¿Qué línea imaginaria divide la Tierra en hemisferios norte y sur?","El ecuador."),
("¿Cuál es la capital de Japón?","Tokio."),
("¿Qué cordillera incluye el Everest?","El Himalaya."),
("¿Qué mar separa en parte Europa y África?","El mar Mediterráneo.")
],
"science": [
("¿A qué temperatura se congela el agua pura a presión atmosférica estándar?","A 0 °C."),
("¿Qué gas absorben las plantas durante la fotosíntesis?","Dióxido de carbono."),
("¿Qué gas es necesario para la respiración humana?","Oxígeno."),
("¿Cuál es el símbolo químico del oro?","Au."),
("¿Cuál es la fórmula química del agua?","H₂O."),
("¿Qué fuerza atrae los cuerpos con masa?","La gravedad."),
("¿La luz viaja más rápido que el sonido en el aire?","Sí, mucho más rápido."),
("¿Qué unidad mide la corriente eléctrica en el SI?","El amperio."),
("¿Qué partícula tiene carga eléctrica negativa?","El electrón."),
("¿Qué estado de la materia tiene volumen definido pero adopta la forma del recipiente?","El líquido.")
],
"plants": [
("¿Qué proceso usan las plantas para convertir luz en energía química?","La fotosíntesis."),
("¿Qué parte de muchas plantas absorbe agua del suelo?","Las raíces."),
("¿Qué gas liberan muchas plantas durante la fotosíntesis?","Oxígeno."),
("¿Qué estructura de la planta suele producir semillas?","La flor, en las plantas con flores."),
("¿Cómo se llama el pigmento verde principal de las plantas?","Clorofila."),
("¿Qué necesitan las plantas para realizar la fotosíntesis?","Luz, agua y dióxido de carbono."),
("¿Qué parte sostiene hojas y flores en muchas plantas?","El tallo."),
("¿Las setas son plantas?","No; los hongos forman un reino distinto."),
("¿Qué es la polinización?","La transferencia de polen a la parte receptora de una flor."),
("¿Qué función cumplen las hojas principalmente?","Captan luz y realizan gran parte de la fotosíntesis.")
],
"time-calendar": [
("¿Cuántos minutos tiene una hora?","60 minutos."),
("¿Cuántos segundos tiene un minuto?","60 segundos."),
("¿Cuántas horas tiene un día convencional?","24 horas."),
("¿Cuántos días tiene una semana?","7 días."),
("¿Cuántos meses tiene un año?","12 meses."),
("¿Cuántos días tiene un año común?","365 días."),
("¿Cuántos días tiene un año bisiesto?","366 días."),
("¿Cuántos meses tienen 31 días?","Siete meses."),
("¿Qué mes viene después de septiembre?","Octubre."),
("¿Cuántos minutos hay en dos horas?","120 minutos.")
],
"units": [
("¿Cuántos centímetros tiene un metro?","100 centímetros."),
("¿Cuántos milímetros tiene un centímetro?","10 milímetros."),
("¿Cuántos gramos tiene un kilogramo?","1.000 gramos."),
("¿Cuántos mililitros tiene un litro?","1.000 mililitros."),
("¿Cuántos metros tiene un kilómetro?","1.000 metros."),
("¿Qué unidad del SI mide la masa?","El kilogramo."),
("¿Qué unidad del SI mide la longitud?","El metro."),
("¿Cuántos centímetros hay en medio metro?","50 centímetros."),
("¿Cuántos gramos hay en medio kilogramo?","500 gramos."),
("¿Cuántos litros son 500 mililitros?","0,5 litros.")
],
"computing": [
("¿Qué significa CPU?","Unidad central de procesamiento."),
("¿Qué significa RAM?","Memoria de acceso aleatorio."),
("¿Qué es un bit?","La unidad básica de información binaria, con valor 0 o 1."),
("¿Cuántos bits forman un byte?","Ocho bits."),
("¿Qué es una URL?","Una dirección que identifica un recurso en la web u otro sistema."),
("¿Qué hace un sistema operativo?","Gestiona recursos del dispositivo y ofrece servicios a los programas."),
("¿Qué es un archivo?","Una unidad de información almacenada con un nombre y un formato o estructura."),
("¿Qué es una contraseña?","Un secreto de autenticación que debe mantenerse protegido."),
("¿Qué significa HTTP?","Protocolo de transferencia de hipertexto."),
("¿Qué es una copia de seguridad?","Una copia de datos destinada a poder recuperarlos.")
],
"food": [
("¿De qué fruta se obtiene tradicionalmente el aceite de oliva?","De la aceituna, fruto del olivo."),
("¿Qué ingrediente principal se usa para hacer pan común?","Harina, normalmente de trigo, junto con agua y otros ingredientes."),
("¿El arroz es un cereal?","Sí, es un cereal."),
("¿De qué animal procede la leche de vaca?","De la vaca."),
("¿Qué vitamina se asocia especialmente a los cítricos como la naranja?","Vitamina C."),
("¿El tomate es botánicamente un fruto?","Sí, botánicamente es un fruto; en cocina suele tratarse como hortaliza."),
("¿Qué alimento se obtiene al cuajar leche?","El queso."),
("¿Qué legumbre se usa para hacer hummus tradicional?","El garbanzo."),
("¿Qué bebida se obtiene al infusionar hojas de Camellia sinensis?","Té."),
("¿Qué fruto seco es la almendra?","La semilla comestible del fruto del almendro.")
],
"materials": [
("¿Qué material atrae un imán común con fuerza?","Materiales ferromagnéticos como el hierro, el níquel y el cobalto."),
("¿El vidrio común es transparente?","Generalmente sí, aunque puede ser coloreado, translúcido u opaco."),
("¿De qué material se fabrica principalmente el papel?","De fibras vegetales, normalmente celulosa de madera u otras fuentes."),
("¿El cobre conduce la electricidad?","Sí, es un buen conductor eléctrico."),
("¿Qué metal es líquido cerca de la temperatura ambiente?","El mercurio."),
("¿Qué material se obtiene del látex natural?","Caucho natural."),
("¿El hielo es agua en estado sólido?","Sí."),
("¿Qué material se usa habitualmente en lápices para escribir?","Grafito, no plomo."),
("¿El acero es una aleación?","Sí, principalmente de hierro y carbono."),
("¿Qué material se obtiene de la arena rica en sílice al fabricar vidrio común?","Vidrio basado principalmente en sílice.")
],
"language": [
("¿Cuántas letras tiene el alfabeto español actual?","27 letras."),
("¿Qué signo se coloca al inicio de una pregunta en español?","El signo de interrogación de apertura: ¿."),
("¿Qué es un sinónimo?","Una palabra o expresión de significado igual o parecido a otra en un contexto."),
("¿Qué es un antónimo?","Una palabra de significado opuesto a otra."),
("¿Qué clase de palabra nombra personas, lugares, objetos o ideas?","El sustantivo."),
("¿Qué signo suele cerrar una oración enunciativa?","El punto."),
("¿Cuál es el plural habitual de «luz»?","«Luces»."),
("¿Qué es un verbo?","Una palabra que expresa acción, estado o proceso."),
("¿Qué idioma se habla principalmente en Brasil?","Portugués."),
("¿Qué lengua tiene más hablantes nativos según las estimaciones habituales?","El chino mandarín suele encabezar las estimaciones; el resultado depende de cómo se agrupen las variedades.")
],
"everyday": [
("¿Cuántos lados tiene un triángulo?","Tres lados."),
("¿Cuántos lados tiene un cuadrado?","Cuatro lados iguales."),
("¿Cuántos grados tiene un ángulo recto?","90 grados."),
("¿Cuántos días tiene febrero en un año común?","28 días."),
("¿Qué color resulta de mezclar luz roja y luz verde?","Amarillo, en mezcla aditiva de luz."),
("¿Cuántas ruedas tiene normalmente una bicicleta?","Dos ruedas."),
("¿Qué instrumento mide la temperatura?","Un termómetro."),
("¿Qué instrumento indica la dirección del norte magnético?","Una brújula."),
("¿Cuántos jugadores de un equipo de fútbol asociación están normalmente en el campo al comenzar?","Once jugadores por equipo."),
("¿Qué forma geométrica tiene una pelota perfectamente esférica?","Una esfera.")
]
}

def sha(data): return hashlib.sha256(data).hexdigest()

def write_dataset(out, name, rows, meta):
    path=out/(name+".jsonl.gz")
    h=hashlib.sha256(); count=0
    with path.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, compresslevel=6) as gz:
            for row in rows:
                b=(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n").encode()
                gz.write(b); h.update(b); count+=1
    compressed=path.read_bytes()
    manifest={**meta,"dataset":name,"rows":count,"sha256_uncompressed":h.hexdigest(),
              "sha256_compressed":sha(compressed),"bytes_compressed":len(compressed)}
    (out/(name+".manifest.json")).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    if count != N: raise RuntimeError(f"{name}: {count} != {N}")
    return manifest

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",default="generated-basic-curricula")
    ap.add_argument("--seed",type=int,default=20261108); args=ap.parse_args()
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    manifests=[]
    for kind in MATH:
        def math_rows(kind=kind):
            for i in range(N):
                expr,answer=arithmetic(kind,i)
                yield {"id":f"{kind}-{i:05d}","domain":"mathematics-basic",
                       "question":Q[i%len(Q)].format(expr=expr),"answer":answer,
                       "operation":kind,"answer_type":"computed"}
        manifests.append(write_dataset(out,"math-"+kind,math_rows(),{
            "type":"computed_arithmetic","curriculum_version":"v1","generator_seed":args.seed,
            "method":"deterministic integer arithmetic; answers computed by Python",
            "limitations":"Elementary exercises; not a proof of broad mathematical reasoning."}))
    for subject, facts in FACTS.items():
        if len(facts)!=10: raise RuntimeError(f"{subject}: expected 10 reviewed seed facts")
        def fact_rows(subject=subject,facts=facts):
            # 10 facts x 10 question frames x 50 contexts x 10 answer frames = 50,000.
            for fi,(q,a) in enumerate(facts):
                for qi,qf in enumerate(FACT_Q):
                    for ci,ctx in enumerate(CONTEXTS):
                        for ai,af in enumerate(ANSWER_FRAMES):
                            idx=(((fi*10+qi)*50+ci)*10+ai)
                            yield {"id":f"{subject}-{idx:05d}","domain":"factual-basic",
                                   "question":qf.format(q=q)+ctx,
                                   "answer":af.format(a=a),"subject":subject,
                                   "seed_fact_id":f"{subject}-seed-{fi:02d}",
                                   "variation":{"question_frame":qi,"context_frame":ci,"answer_frame":ai},
                                   "answer_type":"curated_fact"}
        manifests.append(write_dataset(out,"facts-"+subject,fact_rows(),{
            "type":"curated_factual_qa","generator_seed":args.seed,
            "seed_fact_count":len(facts),"method":"10 reviewed facts x 10 question frames x 50 contexts x 10 answer frames",
            "limitations":"50k rows are controlled paraphrases of 10 seed facts, not 50k independent facts; verify against an authoritative reference before high-stakes use."}))
    summary={"dataset_count":len(manifests),"rows_total":sum(m["rows"] for m in manifests),
             "math_rows":sum(m["rows"] for m in manifests if m["type"]=="computed_arithmetic"),
             "factual_rows":sum(m["rows"] for m in manifests if m["type"]=="curated_factual_qa"),
             "datasets":manifests}
    (out/"SUMMARY.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    assert len(manifests)==25 and summary["rows_total"]==1_250_000
    print(json.dumps({k:v for k,v in summary.items() if k!="datasets"},ensure_ascii=False))

if __name__=="__main__": main()
