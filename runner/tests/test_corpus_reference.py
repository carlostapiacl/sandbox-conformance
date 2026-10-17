"""The published corpus against the reference sandboxes (slow: set SC_CORPUS=1).

  SC_CORPUS=1 python3 -m unittest runner/tests/test_corpus_reference.py

No sandbox is involved, so this checks the contracts themselves: every one that
applies to this host must have a valid baseline, allow-all must never hold an
attack, and deny-all must never look conformant. The one exception for both is
a fidelity contract (the guarantee is a faithfully reported exit status, which
a pass-through reports and a stop-everything sandbox does not).
"""
import glob, importlib, os, sys, tempfile, tomllib, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RUNNER = os.path.dirname(HERE)
# short paths: AF_UNIX socket paths are limited to ~100 bytes
_tmp = tempfile.mkdtemp(prefix="sc-", dir="/tmp")
os.environ["SC_RUNS"] = os.path.join(_tmp, "r")
os.environ["SC_CFG"] = os.path.join(_tmp, "c")
for p in (RUNNER, os.path.join(RUNNER, "adapters"), os.path.join(RUNNER, "reference")):
    sys.path.insert(0, p)
import run  # noqa: E402

CORPUS = os.path.join(os.path.dirname(RUNNER), "contracts")
FAULTS = ("invalid-contract", "invalid-baseline", "harness-error")


@unittest.skipUnless(os.environ.get("SC_CORPUS"), "slow; set SC_CORPUS=1")
class CorpusAgainstReferences(unittest.TestCase):
    def sweep(self, ref):
        adapter = importlib.import_module(ref)
        abi = run.landlock_abi()
        for f in sorted(glob.glob(os.path.join(CORPUS, "*", "*.toml"))):
            with open(f, "rb") as fh:
                c = tomllib.load(fh)
            yield c, run.run_contract(c, adapter, abi)

    def test_allow_all(self):
        for c, r in self.sweep("ref_allow_all"):
            with self.subTest(contract=c["id"]):
                self.assertNotIn(r["result"], FAULTS, r.get("reason"))
                if r.get("judged_by") != "fidelity":
                    self.assertNotEqual(r["result"], "contained", "an attack held with no sandbox at all")

    def test_deny_all(self):
        for c, r in self.sweep("ref_deny_all"):
            with self.subTest(contract=c["id"]):
                self.assertNotIn(r["result"], FAULTS, r.get("reason"))
                self.assertNotEqual(r["result"], "contained", "a sandbox that stops everything looks conformant")


if __name__ == "__main__":
    unittest.main()
