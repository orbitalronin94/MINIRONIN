import unittest

from scripts.library_provenance import infer_library_id


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


if __name__ == "__main__":
    unittest.main()
