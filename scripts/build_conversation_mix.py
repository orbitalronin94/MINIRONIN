#!/usr/bin/env python3
"""Build a 10M-candidate multi-turn MINIRONIN conversation corpus.

Uses only structured Q/A rows already present in curated/inherited datasets.
It creates combinations of each seed answer, a follow-up intent and a voice
variant. Every row retains seed provenance. Output is a candidate corpus only:
it is NOT wired into any training workflow.
"""
from __future__ import annotations
import argparse, gzip, hashlib, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOTS = ("data/curated", "data/inherited", "data/datasets")
FOLLOWUPS = [
 "¿Qué evidencia respalda exactamente esa respuesta?",
 "¿Qué parte es un hecho y qué parte es interpretación?",
 "¿Qué límite importante debería tener presente?",
 "¿Qué podría hacer que esa respuesta fuese incorrecta?",
 "¿Puedes resumirlo sin perder la precisión?",
 "¿Qué dato adicional necesitarías para afirmarlo con más seguridad?",
 "¿Cuál sería la objeción más razonable?",
 "¿Qué supuesto estás dando por válido?",
 "¿La fuente ofrece un dato observado o una proyección?",
 "¿Puedes distinguir la regla general de sus excepciones?",
 "¿Qué responderías a alguien que discrepa?",
 "¿Qué no se puede concluir a partir de ese dato?",
 "¿Puedes explicar el concepto sin jerga?",
 "¿Qué referencia concreta permite comprobarlo?",
 "¿Hay alguna incertidumbre que no debamos ocultar?",
 "¿Qué cambiaría si el contexto fuese distinto?",
 "¿Puedes señalar la premisa más débil?",
 "¿Cuál es la conclusión mínima que sí está justificada?",
 "¿Qué dato sería necesario para ir más allá?",
 "¿Puedes corregir cualquier exceso de seguridad?",
]
VOICES = [
 "La precisión no es un adorno; es el mínimo para no hacer el ridículo.",
 "El dato tiene límites. La imaginación, por desgracia, suele carecer de ellos.",
 "No confundamos una fuente con un oráculo infalible.",
 "Una conclusión más ambiciosa necesitaría pruebas más ambiciosas.",
 "La retórica queda muy bien; la trazabilidad queda mejor.",
 "La realidad no tiene obligación de obedecer a nuestra opinión favorita.",
 "Conviene desconfiar de quien ofrece certeza ilimitada en tres frases.",
 "El sarcasmo es opcional; la honestidad intelectual no.",
 "La respuesta corta era fácil. La respuesta responsable exige matices.",
 "Qué contratiempo: resulta que había que comprobarlo.",
]
SOURCE_ANSWERS = [
 "La ficha atribuye la afirmación a {source} ({period}). Esa es la procedencia declarada, no una garantía de cualquier interpretación adicional. {voice}",
 "La referencia registrada es {source} ({period}). Podemos comprobar esa fuente; no debemos fingir que prueba más de lo que dice. {voice}",
 "La trazabilidad disponible apunta a {source}, con alcance temporal «{period}». Si se quiere ir más lejos, hace falta contraste independiente. {voice}",
]
UNSOURCED_ANSWERS = [
 "Esta ficha no aporta una referencia externa verificable. Puedo trabajar con el contexto dado, pero no venderlo como hecho independiente. {voice}",
 "La procedencia registrada es {source}. Eso identifica el origen del ejemplo, no lo convierte en evidencia externa. {voice}",
]
ABSTENTION_ANSWERS = [
 "No hay información suficiente en el contexto para ampliar la respuesta. Inventar una fuente sería un truco barato; mantengo la abstención. {voice}",
 "La ficha no contiene evidencia para resolverlo. No voy a fabricar una certeza para decorar el silencio. {voice}",
]

def read_rows(path: Path):
    opener = gzip.open if path.name.endswith(".jsonl.gz") else open
    with opener(path, "rt", encoding="utf-8", errors="replace") as stream:
        for line_no, line in enumerate(stream, 1):
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(row, dict):
                continue
            question = row.get("question") or row.get("prompt") or row.get("instruction")
            answer = row.get("answer") or row.get("completion") or row.get("output")
            if not question or not answer:
                messages = row.get("messages")
                if isinstance(messages, list):
                    users = [m.get("content", "") for m in messages if m.get("role") == "user"]
                    assistants = [m.get("content", "") for m in messages if m.get("role") == "assistant"]
                    question = question or (users[-1] if users else None)
                    answer = answer or (assistants[-1] if assistants else None)
            if not isinstance(question, str) or not isinstance(answer, str):
                continue
            question, answer = question.strip(), answer.strip()
            if len(question) < 4 or len(answer) < 2:
                continue
            yield {
                "id": str(row.get("id") or f"{path.name}:{line_no}"),
                "tag": str(row.get("tag") or row.get("domain") or "curated"),
                "topic": str(row.get("topic") or row.get("tag") or row.get("domain") or "general"),
                "context": str(row.get("context") or ""),
                "question": question[:4000],
                "answer": answer[:6000],
                "source": str(row.get("source") or path.name),
                "source_url": str(row.get("source_url") or row.get("reference") or ""),
                "period": str(row.get("period") or ""),
                "source_file": str(path),
            }

def load_seeds(roots):
    seen, rows, audit = set(), [], []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or not (path.name.endswith(".jsonl") or path.name.endswith(".ndjson") or path.name.endswith(".jsonl.gz")):
                continue
            before = len(rows)
            for row in read_rows(path):
                key = hashlib.sha256((row["context"]+"\0"+row["question"]+"\0"+row["answer"]).encode()).hexdigest()
                if key in seen:
                    continue
                seen.add(key)
                row["seed_sha256"] = key
                rows.append(row)
            audit.append({"path": str(path), "rows_added": len(rows)-before})
    if not rows:
        raise SystemExit("No structured question/answer records found in the input roots")
    return rows, audit

def followup_answer(seed, variant):
    voice = VOICES[variant % len(VOICES)]
    tag = seed["tag"].lower()
    answer = seed["answer"].lower()
    if any(x in tag for x in ("abstain", "unknown", "out_of_scope", "hallucination_trap")) or answer.startswith(("ni puta idea", "no tengo", "no hay datos")):
        template = ABSTENTION_ANSWERS[variant % len(ABSTENTION_ANSWERS)]
        return template.format(voice=voice)
    if seed["source_url"] or seed["period"]:
        template = SOURCE_ANSWERS[variant % len(SOURCE_ANSWERS)]
        return template.format(source=seed["source"], period=seed["period"] or "no especificado", voice=voice)
    template = UNSOURCED_ANSWERS[variant % len(UNSOURCED_ANSWERS)]
    return template.format(source=seed["source"], voice=voice)

def make_record(seed, index, variant):
    followup = FOLLOWUPS[variant % len(FOLLOWUPS)]
    voice_variant = (variant // len(FOLLOWUPS)) % len(VOICES)
    system = (
      "Eres MINIRONIN: un personaje culto, escéptico, irónico y mordaz. "
      "Primero conserva la verdad y los límites del contexto; después añade humor seco. "
      "No inventes hechos, fuentes ni certezas. Si no hay evidencia, abstente. "
      + ("Contexto de la ficha: " + seed["context"] if seed["context"] else "")
    ).strip()
    messages = [
      {"role":"system","content":system},
      {"role":"user","content":seed["question"]},
      {"role":"assistant","content":seed["answer"]},
      {"role":"user","content":followup},
      {"role":"assistant","content":followup_answer(seed, voice_variant)},
    ]
    return {
      "id": f"conv-{index:08d}",
      "seed_id": seed["id"],
      "seed_sha256": seed["seed_sha256"],
      "source": seed["source"],
      "source_url": seed["source_url"],
      "source_file": seed["source_file"],
      "tag": seed["tag"],
      "topic": seed["topic"],
      "variant": variant,
      "synthetic": True,
      "generation_method": "seed_x_followup_x_voice_v1",
      "messages": messages,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-roots", nargs="*", default=list(DEFAULT_ROOTS))
    p.add_argument("--target", type=int, default=10_000_000)
    p.add_argument("--shard-size", type=int, default=100_000)
    p.add_argument("--output-dir", default="data/generated/conversation-candidates-v1")
    p.add_argument("--dry-run", action="store_true")
    args=p.parse_args()
    if args.target < 1 or args.shard_size < 1:
        p.error("target and shard-size must be positive")
    roots=[Path(x) for x in args.input_roots]
    seeds, audit=load_seeds(roots)
    variants_per_seed=math.ceil(args.target/len(seeds))
    max_variants=len(FOLLOWUPS)*len(VOICES)
    if variants_per_seed > max_variants:
        raise SystemExit(f"Not enough combinations: {len(seeds)} seeds × {max_variants} variants < {args.target}")
    summary={
      "target":args.target, "unique_seed_records":len(seeds),
      "variants_per_seed":variants_per_seed, "max_variants_per_seed":max_variants,
      "theoretical_combinations":len(seeds)*max_variants,
      "source_files":audit, "output_format":"sharded gzip JSONL",
      "training_status":"candidate_only_not_wired_into_training",
    }
    if args.dry_run:
        examples=[make_record(seeds[i],i+1,0) for i in range(min(3,len(seeds)))]
        print(json.dumps({"summary":summary,"sample":examples},ensure_ascii=False,indent=2))
        return
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    manifest_shards=[]
    shard_no=1; written=0; digest_all=hashlib.sha256()
    buffer=[]
    def flush(rows, number):
        path=out/f"conversations-{number:04d}.jsonl.gz"
        raw="".join(json.dumps(r,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n" for r in rows).encode()
        compressed=gzip.compress(raw,compresslevel=6,mtime=0)
        path.write_bytes(compressed)
        return {"file":str(path),"records":len(rows),"bytes":len(compressed),"sha256":hashlib.sha256(compressed).hexdigest()}
    for seed_index, seed in enumerate(seeds):
        for variant in range(variants_per_seed):
            if written >= args.target: break
            row=make_record(seed,written+1,variant)
            encoded=json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n"
            buffer.append(row); digest_all.update(encoded.encode()); written+=1
            if len(buffer)>=args.shard_size:
                manifest_shards.append(flush(buffer,shard_no)); buffer=[]; shard_no+=1
        if written>=args.target: break
    if buffer: manifest_shards.append(flush(buffer,shard_no))
    manifest={**summary,"records_written":written,"sha256_uncompressed_jsonl":digest_all.hexdigest(),"shards":manifest_shards}
    (out/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
