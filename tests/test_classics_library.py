import json
from pathlib import Path

from scripts.acquire_classics_library import clean_gutenberg

ROOT = Path(__file__).resolve().parents[1]


def test_classics_registry_has_broad_domains_and_rights_gates():
    registry = json.loads((ROOT / "data/classics/SOURCES.json").read_text(encoding="utf-8"))
    rows = registry["sources"]
    assert len(rows) >= 15
    assert {concept for row in rows for concept in row["concepts"]} >= {
        "science", "capitalism", "feminism", "literature", "biology", "political_theory"
    }
    assert all(row["rights_status"] == "rights_review_required" for row in rows if row.get("translator"))
    assert sum(row["rights_status"] == "approved_for_spain_training" for row in rows) >= 8


def test_classics_cleaner_extracts_only_gutenberg_body():
    raw = (
        "header\n*** START OF THE PROJECT GUTENBERG EBOOK TEST ***\n"
        + ("A sufficiently long body. " * 500)
        + "\n*** END OF THE PROJECT GUTENBERG EBOOK TEST ***\nfooter"
    ).encode("utf-8")
    body = clean_gutenberg(raw)
    assert body.startswith("A sufficiently long body.")
    assert "header" not in body and "footer" not in body
