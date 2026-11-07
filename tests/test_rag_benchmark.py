import importlib.util
from pathlib import Path
SCRIPT=Path(__file__).resolve().parents[1]/"scripts"/"benchmark_rag_vs_training.py"
SPEC=importlib.util.spec_from_file_location("rag_benchmark",SCRIPT)
RAG=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(RAG)

def test_chunking_overlap():
 chunks=RAG.split_chunks("a"*2600,size=1000,overlap=100)
 assert len(chunks)==3 and chunks[0][-100:]==chunks[1][:100] and chunks[1][-100:]==chunks[2][:100]

def test_short_chunk_is_ignored():
 assert RAG.split_chunks("short",size=1000,overlap=100)==[]

def test_duplicate_holdout_ids_rejected(tmp_path):
 p=tmp_path/"holdout.jsonl"; p.write_text('{"id":"x"}\n{"id":"x"}\n')
 try:RAG.load_questions(p)
 except ValueError as exc: assert "Duplicate" in str(exc)
 else:raise AssertionError("duplicate IDs must be rejected")

def test_rag_prompt_respects_model_context_budget():
 question="¿Qué explica el documento?"
 hits=[{"text":"Fragmento de evidencia. "*100},{"text":"Segundo fragmento. "*100}]
 prompt=RAG.make_rag_prompt(question,hits,512)
 assert len(prompt.encode("utf-8"))<=512
 assert question in prompt
