import unittest

from scripts.library_provenance import (
    infer_library_id,
    iter_tokenized_training_rows,
    training_corpus_signature,
)


class LibraryProvenanceTests(unittest.TestCase):
    def test_explicit_source_families(self):
        cases = {
            "HERETIC:dataset.jsonl": "heretic",
            "PRODATPHIL v0.3": "prodatphil",
            "MINIRONIN-ANARCHIST-LIBRARY-v1": "anarchist",
            "MINIRONIN-CLASSICS-LIBRARY-v1": "classics",
            "MINIRONIN-authored-behavior-v1": "minironin_behavior",
            "MINIRONIN-engineering-v1": "minironin_behavior",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(infer_library_id(source), expected)

    def test_unknown_source_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Unregistered"):
            infer_library_id("some-new-domain")

    def test_empty_source_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "required"):
            infer_library_id("")

    def test_tokenized_rows_are_train_only_and_deterministic(self):
        docs = {
            "books": [{"source": "PRODATPHIL v0.3", "sha256": "b" * 64, "text": "book"}],
            "science": [{"source": "HERETIC:science.jsonl", "sha256": "a" * 64, "text": "paper"}],
        }
        encode = lambda text: [len(text), 256]
        rows = list(iter_tokenized_training_rows(docs, encode))
        self.assertEqual([x["library_id"] for x in rows], ["heretic", "prodatphil"])
        self.assertTrue(all(x["split"] == "train" for x in rows))
        self.assertEqual(rows[0]["token_ids"], [5, 256])

    def test_corpus_signature_ignores_mapping_order(self):
        a = {"books": [{"source": "PRODATPHIL v0.3", "sha256": "b" * 64}]}
        b = {"books": list(reversed(a["books"]))}
        self.assertEqual(training_corpus_signature(a), training_corpus_signature(b))


if __name__ == "__main__":
    unittest.main()
