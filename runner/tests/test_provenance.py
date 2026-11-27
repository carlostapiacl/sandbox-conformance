"""provenance.py: every contract says where it comes from and how it relates to TartarOS."""
import os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import provenance  # noqa: E402


class Provenance(unittest.TestCase):
    def test_file_is_current(self):
        # A new contract needs its entry (and, if written with a TartarOS feature, its row in TABLE).
        self.assertEqual(provenance.load(), provenance.build(),
                         "corpus/provenance.json is stale: run runner/provenance.py build")

    def test_every_contract_names_a_source_project(self):
        self.assertEqual([i for i, e in provenance.build().items() if not e["source_project"]], [])

    def test_kinds_are_known(self):
        kinds = {e["with_tartaros"] for e in provenance.build().values()}
        self.assertLessEqual(kinds, {"no", "written-alongside", "changed-alongside"})


if __name__ == "__main__":
    unittest.main()
