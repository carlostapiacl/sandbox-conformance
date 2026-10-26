"""corpus.py: a version is the exact set of contract files, by hash."""
import json, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import corpus  # noqa: E402


def manifest(root, version, entries):
    os.makedirs(root, exist_ok=True)
    m = {"corpus_version": version, "contracts": {i: {"sha256": h} for i, h in entries.items()}}
    json.dump(m, open(os.path.join(root, f"v{version}.json"), "w"))


def run(entries):
    return {"contracts": [{"id": i, "contract_sha256": h} for i, h in entries.items()]}


class Corpus(unittest.TestCase):
    def test_contracts_are_the_latest_version(self):
        # Every change to contracts/ comes with the next version (corpus/README.md).
        vs = corpus.versions()
        self.assertTrue(vs, "no corpus version")
        a, r, c = corpus.diff(vs[-1][1]["contracts"], corpus.current())
        self.assertEqual((a, r, c), ([], [], []),
                         f"contracts/ is not v{vs[-1][0]}: write the next version (runner/corpus.py build)")

    def test_versions_sort_numerically(self):
        with tempfile.TemporaryDirectory() as d:
            for v in ["1.10", "1.2", "2.0"]:
                manifest(d, v, {"a": "h"})
            self.assertEqual([v for v, _ in corpus.versions(d)], ["1.2", "1.10", "2.0"])

    def test_a_run_measures_the_newest_version_it_ran_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            manifest(d, "1.0", {"a": "h1", "b": "h2"})
            manifest(d, "1.1", {"a": "h1", "b": "CHANGED", "c": "h3"})
            self.assertEqual(corpus.corpus_of(run({"a": "h1", "b": "h2"}), d),
                             {"version": "1.0", "ran": 2, "of": 2, "whole": True})
            self.assertEqual(corpus.corpus_of(run({"a": "h1", "b": "CHANGED", "c": "h3"}), d),
                             {"version": "1.1", "ran": 3, "of": 3, "whole": True})
            # a subset of the newest version: not the whole of it
            self.assertEqual(corpus.corpus_of(run({"c": "h3"}), d),
                             {"version": "1.1", "ran": 1, "of": 3, "whole": False})

    def test_a_whole_older_version_wins_over_part_of_a_newer_one(self):
        with tempfile.TemporaryDirectory() as d:
            manifest(d, "1.0", {"a": "h1", "b": "h2"})
            manifest(d, "1.1", {"a": "h1", "b": "h2", "c": "h3"})
            self.assertEqual(corpus.corpus_of(run({"a": "h1", "b": "h2"}), d),
                             {"version": "1.0", "ran": 2, "of": 2, "whole": True})

    def test_a_run_with_any_contract_of_no_version_measured_none(self):
        with tempfile.TemporaryDirectory() as d:
            manifest(d, "1.0", {"a": "h1", "b": "h2"})
            self.assertIsNone(corpus.corpus_of(run({"a": "h1", "b": "OLD"}), d))
            self.assertIsNone(corpus.corpus_of(run({"z": "h9"}), d))

    def test_diff_names_added_removed_changed(self):
        old = {"a": {"sha256": "1"}, "b": {"sha256": "2"}}
        new = {"b": {"sha256": "3"}, "c": {"sha256": "4"}}
        self.assertEqual(corpus.diff(old, new), (["c"], ["a"], ["b"]))


if __name__ == "__main__":
    unittest.main()
