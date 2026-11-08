import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("rag_builder",ROOT/"scripts/build_rag_index.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def test_chunking():
 xs=m.chunk("Alpha paragraph. "*60,240,40,80);assert len(xs)>1 and all(len(x)>=80 for x in xs)
def test_jsonl_fields():
 x=m.extract({"id":"a","question":"What is entropy?","answer":"A state function."});assert "entropy" in x and "state function" in x
def test_registry_excludes_holdout():
 r=json.loads((ROOT/"data/rag/sources.json").read_text());assert m.excluded(Path("benchmarks/holdout/a.jsonl"),r)
def test_hash_stable():assert m.sha(b"abc")==m.sha(b"abc")
