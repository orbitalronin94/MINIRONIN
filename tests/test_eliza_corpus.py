import json,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def test_eliza_requests_keep_canonical_answers_and_tags(tmp_path):
 source=tmp_path/"source.jsonl"
 source.write_text(
  json.dumps({"id":"q1","question":"Why does this pointer crash?","answer":"The pointer may be dangling; inspect its lifetime.","domain":"systems","license":"CC0-1.0"},ensure_ascii=False)+"\n"+
  json.dumps({"id":"q2","question":"What is entropy?","answer":"A thermodynamic state function.","domain":"science","license":"CC0-1.0"},ensure_ascii=False)+"\n",
  encoding="utf-8")
 output=tmp_path/"out.jsonl"
 subprocess.run([sys.executable,str(ROOT/"scripts/build_eliza_corpus.py"),
  "--input",str(source),"--count","8","--seed","7","--max-pool","10",
  "--output",str(output)],check=True,capture_output=True,text=True)
 rows=[json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
 assert len(rows)==8
 assert {r["strategy"] for r in rows}=={"mirror","expert","friction","abstain"}
 assert all(r["stage_a"]["canonical_reference"] in {
  "The pointer may be dangling; inspect its lifetime.","A thermodynamic state function."} for r in rows)
 assert all(r["source"]["license"]=="CC0-1.0" for r in rows)
 assert all(r["synthetic_status"]=="teacher_request_only" for r in rows)
 assert all(r["stage_b"]["must_preserve"] for r in rows)
