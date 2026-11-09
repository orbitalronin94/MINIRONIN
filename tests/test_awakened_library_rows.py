import json
from pathlib import Path

from scripts.build_awakened_library_rows import has_alias, normalize, split_sentences


def test_alias_matching_uses_word_boundaries():
    assert has_alias("The theory of natural selection is important.", "natural selection")
    assert not has_alias("A naturalist selected the sample.", "natural selection")


def test_sentence_split_preserves_sentence_content():
    rows = split_sentences("Natural selection changes populations over time. Mutual aid can shape social life.")
    assert len(rows) == 2
    assert rows[0].startswith("Natural selection")
    assert rows[1].startswith("Mutual aid")


def test_normalization_is_deterministic():
    assert normalize("  Mutual-aid, and COOPERATION! ") == "mutual aid and cooperation"


def test_awakened_builder_emits_only_extractive_grounded_rows(tmp_path, monkeypatch):
    from scripts import build_awakened_library_rows as builder

    root = tmp_path
    source = root / "library" / "darwin.md"
    source.parent.mkdir(parents=True)
    source.write_text(
        "# Natural selection\n\nNatural selection changes populations over generations. "
        "The evidence comes from inherited variation and differential reproduction.\n",
        encoding="utf-8",
    )
    registry = {
        "concepts": [{"id": "natural_selection", "label": "Selección natural",
                      "aliases": ["natural selection"]}],
        "libraries": [{"id": "classics-library", "name": "Classics",
                       "source_paths": ["library"], "concepts": ["natural_selection"]}],
    }
    registry_path = root / "registry.json"
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    monkeypatch.setattr(builder, "ROOT", root)
    monkeypatch.setattr(builder, "DOMAIN_BY_LIBRARY", {"classics-library": "classics"})
    monkeypatch.setattr("sys.argv", [
        "build_awakened_library_rows.py", "--registry", str(registry_path),
        "--output", str(root / "rows.jsonl"), "--manifest", str(root / "manifest.json"),
    ])
    builder.main()
    rows = [json.loads(line) for line in (root / "rows.jsonl").read_text().splitlines()]
    manifest = json.loads((root / "manifest.json").read_text())
    assert rows
    assert all(row["synthetic"] is True for row in rows)
    assert all(row["answer"] in row["context"] for row in rows)
    assert all(row["document_sha256"] for row in rows)
    assert manifest["training_authorized"] is True
