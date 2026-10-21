"""versions.py: which version changed which result."""
import io, json, os, sys, tempfile, unittest
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import versions  # noqa: E402


def run_file(parent, run, version, contracts):
    os.makedirs(os.path.join(parent, run), exist_ok=True)
    d = {"sandbox": "s", "version": version, "spec_version": "1.0.0-draft",
         "contracts": [{"id": i, "severity": "high", "result": r, "contract_sha256": h} for i, r, h in contracts]}
    json.dump(d, open(os.path.join(parent, run, "s.json"), "w"))


class Versions(unittest.TestCase):
    def test_version_order(self):
        vs = ["0.0.81", "0.0.9", "0.1.0-alpha.10", "0.1.0-alpha.6", "0.1.0", "0.163.0"]
        self.assertEqual(sorted(vs, key=versions.vkey),
                         ["0.0.9", "0.0.81", "0.1.0-alpha.6", "0.1.0-alpha.10", "0.1.0", "0.163.0"])

    def test_only_identical_contracts_are_compared(self):
        with tempfile.TemporaryDirectory() as root:
            run_file(root, "2026-01-01", "1.0", [("a", "escaped", "h1"), ("b", "escaped", "h2")])
            run_file(root, "2026-01-02", "1.1", [("a", "contained", "h1"), ("b", "contained", "CHANGED")])
            buf = io.StringIO()
            with redirect_stdout(buf):
                versions.main([root])
            out = buf.getvalue()
        self.assertIn("### 1.0 → 1.1", out)
        self.assertIn("| `a` | high | escaped | **contained** |", out)
        self.assertNotIn("`b`", out)
        self.assertIn("1 not compared", out)

    def test_latest_run_of_a_version_wins(self):
        with tempfile.TemporaryDirectory() as root:
            run_file(root, "2026-01-01", "1.0", [("a", "escaped", "h1")])
            run_file(root, "2026-01-05", "1.0", [("a", "contained", "h1")])
            self.assertEqual(versions.load([root])["s"]["1.0"][0], "2026-01-05")


if __name__ == "__main__":
    unittest.main()
