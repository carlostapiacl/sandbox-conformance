"""The lab measured against sandboxes whose behaviour is known (runner/reference/).

Every cell of EXPECTED is what spec/verdicts.md says a correct lab reports for
that contract and that reference sandbox. Runs unprivileged on Linux and macOS:

  python3 -m unittest discover -s runner/tests
"""
import glob, importlib, os, shutil, sys, tempfile, tomllib, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RUNNER = os.path.dirname(HERE)
_tmp = tempfile.mkdtemp(prefix="sc-tests-")
os.environ["SC_RUNS"] = os.path.join(_tmp, "runs")
os.environ["SC_CFG"] = os.path.join(_tmp, "cfg")
for p in (RUNNER, os.path.join(RUNNER, "adapters"), os.path.join(RUNNER, "reference")):
    sys.path.insert(0, p)
import run  # noqa: E402

CONTRACTS = {}
for f in sorted(glob.glob(os.path.join(HERE, "contracts", "*", "*.toml"))):
    with open(f, "rb") as fh:
        c = tomllib.load(fh)
    CONTRACTS[c["id"]] = c

REFS = ["ref_allow_all", "ref_deny_all", "ref_broken", "ref_refuser", "ref_refuser_unsigned"]

# contract -> {reference sandbox: expected result}
EXPECTED = {
    "ref-write-protected": {
        "ref_allow_all": "escaped", "ref_deny_all": "control-broke", "ref_broken": "harness-error",
        "ref_refuser": "escaped", "ref_refuser_unsigned": "escaped"},
    "ref-read-protected": {
        "ref_allow_all": "escaped", "ref_deny_all": "control-broke", "ref_broken": "harness-error",
        "ref_refuser": "escaped", "ref_refuser_unsigned": "escaped"},
    # deny-all exits 1, which this contract does not declare as "blocked" (a crash exits 1 too)
    "ref-script-blocked-exit": {
        "ref_allow_all": "escaped", "ref_deny_all": "inconclusive", "ref_broken": "harness-error",
        "ref_refuser": "escaped", "ref_refuser_unsigned": "escaped"},
    "ref-refuse-symlink-root": {
        "ref_allow_all": "escaped", "ref_deny_all": "control-broke", "ref_broken": "harness-error",
        "ref_refuser": "contained", "ref_refuser_unsigned": "inconclusive"},
    # decided in the baseline, before any sandbox runs
    "ref-vacuous": {r: "vacuous" for r in REFS},
    "ref-control-broken-unsandboxed": {r: "invalid-baseline" for r in REFS},
    "ref-control-needs-sandbox": {
        "ref_allow_all": "escaped", "ref_deny_all": "control-broke", "ref_broken": "harness-error",
        "ref_refuser": "escaped", "ref_refuser_unsigned": "escaped"},
}


class ReferenceSandboxes(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(_tmp, ignore_errors=True)

    def test_every_contract_has_expectations(self):
        self.assertEqual(sorted(CONTRACTS), sorted(EXPECTED))

    def test_matrix(self):
        abi = run.landlock_abi()
        for cid, row in EXPECTED.items():
            for ref, want in row.items():
                with self.subTest(contract=cid, sandbox=ref):
                    adapter = importlib.import_module(ref)
                    got = run.run_contract(CONTRACTS[cid], adapter, abi)
                    self.assertEqual(got["result"], want, got.get("reason", ""))

    def test_deny_all_is_never_contained(self):
        """A sandbox that stops everything must not look conformant."""
        abi = run.landlock_abi()
        adapter = importlib.import_module("ref_deny_all")
        for cid, c in CONTRACTS.items():
            with self.subTest(contract=cid):
                self.assertNotEqual(run.run_contract(c, adapter, abi)["result"], "contained")

    def test_missing_host_capability_is_not_measured(self):
        """A sandbox that would degrade silently on this host is not measured (§4.2)."""
        abi = run.landlock_abi()
        adapter = importlib.import_module("ref_needs_host")
        for cid, c in CONTRACTS.items():
            with self.subTest(contract=cid):
                got = run.run_contract(c, adapter, abi)
                self.assertEqual(got["result"], "not-applicable")
                self.assertIn("no-such-capability", got["reason"])

    def test_broken_never_yields_a_measured_result(self):
        """A sandbox that never starts says nothing about confinement."""
        abi = run.landlock_abi()
        adapter = importlib.import_module("ref_broken")
        for cid, c in CONTRACTS.items():
            with self.subTest(contract=cid):
                got = run.run_contract(c, adapter, abi)["result"]
                self.assertNotIn(got, ("contained", "escaped", "control-broke"))


if __name__ == "__main__":
    unittest.main()
