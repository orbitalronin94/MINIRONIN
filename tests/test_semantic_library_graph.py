import json
import sys

from scripts.build_semantic_library_graph import main


def test_semantic_graph_connects_libraries_and_exposes_stable_tokens(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["build_semantic_library_graph.py", "--output-dir", str(tmp_path)])
    main()
    graph = json.loads((tmp_path / "semantic-library-graph.json").read_text(encoding="utf-8"))
    tokens = json.loads((tmp_path / "semantic-tokens.json").read_text(encoding="utf-8"))
    assert graph["counts"]["libraries"] >= 4
    assert graph["counts"]["concepts"] >= 20
    assert "SEM:mutual_aid" in tokens["tokens"]
    assert any(edge["type"] == "cross_library_semantic_overlap" for edge in graph["edges"])
    assert any(edge["type"] == "cross_library_analogy_not_equivalence" for edge in graph["edges"])
    assert "NOT atomic tokenizer IDs" in graph["token_semantics"]
