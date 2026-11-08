import unittest

from scripts.library_sampler import LibrarySampler


def docs():
    return [
        {"id": "h1", "library_id": "heretic", "split": "train", "token_ids": list(range(100))},
        {"id": "h2", "library_id": "heretic", "split": "train", "token_ids": list(range(100, 200))},
        {"id": "a1", "library_id": "anarchist", "split": "train", "token_ids": list(range(200))},
    ]


class LibrarySamplerTests(unittest.TestCase):
    def test_deterministic_with_same_seed(self):
        a = LibrarySampler(docs(), {"heretic": 0.8, "anarchist": 0.2}, seed=7)
        b = LibrarySampler(docs(), {"heretic": 0.8, "anarchist": 0.2}, seed=7)
        self.assertEqual([a.sample_window(8) for _ in range(20)],
                         [b.sample_window(8) for _ in range(20)])

    def test_only_train_split_is_accepted(self):
        bad = docs() + [{"id": "v1", "library_id": "heretic",
                         "split": "validation", "token_ids": list(range(100))}]
        with self.assertRaisesRegex(ValueError, "training-split"):
            LibrarySampler(bad, {"heretic": 1.0})

    def test_missing_library_is_renormalized_away(self):
        sampler = LibrarySampler(docs(), {"heretic": 0.5, "anarchist": 0.25,
                                           "classics": 0.25}, seed=3)
        self.assertEqual(set(sampler.available), {"heretic", "anarchist"})
        self.assertAlmostEqual(sum(sampler.probabilities.values()), 1.0)

    def test_batch_shape_and_accounting(self):
        sampler = LibrarySampler(docs(), {"heretic": 0.5, "anarchist": 0.5}, seed=2)
        rows, provenance = sampler.make_batch(4, 16)
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(len(row) == 17 for row in rows))
        self.assertEqual(len(provenance), 4)
        report = sampler.report()
        self.assertEqual(report["total_sampled_target_tokens"], 64)
        self.assertGreaterEqual(sum(x["unique_documents"] for x in report["libraries"].values()), 1)

    def test_document_cycle_covers_every_document_before_repeating(self):
        sampler = LibrarySampler(docs(), {"heretic": 1.0}, seed=11)
        ids = [sampler.sample_window(8)[1]["document_id"] for _ in range(2)]
        self.assertEqual(set(ids), {"h1", "h2"})

    def test_stable_document_identity_is_required(self):
        row = {"library_id": "heretic", "split": "train", "token_ids": [1, 2, 3]}
        with self.assertRaisesRegex(ValueError, "id/sha256"):
            LibrarySampler([row], {"heretic": 1.0})

    def test_duplicate_document_identity_is_rejected(self):
        rows = docs() + [dict(docs()[0])]
        with self.assertRaisesRegex(ValueError, "Duplicate document"):
            LibrarySampler(rows, {"heretic": 1.0, "anarchist": 1.0})


if __name__ == "__main__":
    unittest.main()
