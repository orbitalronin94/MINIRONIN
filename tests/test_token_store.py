import tempfile
import unittest

from scripts.token_store import TokenStore, build_token_store


class TokenStoreTests(unittest.TestCase):
    def rows(self):
        return [
            {"id": "h1", "library_id": "heretic", "split": "train",
             "token_ids": [0, 1, 255, 256, 4095]},
            {"id": "a1", "library_id": "anarchist", "split": "train",
             "token_ids": [3, 4, 5, 6]},
        ]

    def test_round_trip_and_mmap_windows(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = build_token_store(self.rows(), tmp,
                tokenizer_sha256="tok-sha", corpus_signature="corpus-sha")
            self.assertEqual(manifest["total_tokens"], 9)
            with TokenStore(tmp, expected_tokenizer_sha256="tok-sha",
                            expected_corpus_signature="corpus-sha") as store:
                docs = list(store.documents())
                self.assertEqual(docs[0]["token_ids"][2], 255)
                self.assertEqual(docs[0]["token_ids"][1:5], [1, 255, 256, 4095])
                self.assertEqual(docs[1]["token_ids"][:], [3, 4, 5, 6])

    def test_validation_data_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = self.rows() + [{"id": "v1", "library_id": "heretic",
                "split": "validation", "token_ids": [1, 2, 3]}]
            with self.assertRaisesRegex(ValueError, "training-split"):
                build_token_store(rows, tmp, tokenizer_sha256="tok",
                                  corpus_signature="corpus")

    def test_tokenizer_signature_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            build_token_store(self.rows(), tmp, tokenizer_sha256="tok-sha",
                              corpus_signature="corpus-sha")
            with self.assertRaisesRegex(ValueError, "tokenizer SHA-256"):
                TokenStore(tmp, expected_tokenizer_sha256="wrong")

    def test_index_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            build_token_store(self.rows(), tmp, tokenizer_sha256="tok",
                              corpus_signature="corpus")
            index = __import__("pathlib").Path(tmp) / "index.json"
            index.write_text("[]", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "index SHA-256"):
                TokenStore(tmp)

    def test_duplicate_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = self.rows() + [dict(self.rows()[0])]
            with self.assertRaisesRegex(ValueError, "Duplicate document"):
                build_token_store(rows, tmp, tokenizer_sha256="tok",
                                  corpus_signature="corpus")


if __name__ == "__main__":
    unittest.main()
