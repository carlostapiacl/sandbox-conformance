"""§4.1: contract validation, and the published corpus against it."""
import glob, os, sys, tempfile, tomllib, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RUNNER = os.path.dirname(HERE)
os.environ.setdefault("SC_RUNS", os.path.join(tempfile.gettempdir(), "sc-tests-runs"))
sys.path.insert(0, RUNNER)
import run  # noqa: E402

GOOD = {"id": "t", "category": "ref", "severity": "high", "os": ["linux"],
        "policy": {"writable_roots": ["{root}/w"]},
        "attack": {"cmd": "x"}, "control": {"cmd": "y"}}


class Validation(unittest.TestCase):
    def bad(self, **change):
        c = {**GOOD, **change}
        return run.invalid(c)

    def test_good(self):
        self.assertEqual(run.invalid(GOOD), [])

    def test_unknown_top_field(self):
        self.assertTrue(self.bad(expect_refusl=True))

    def test_misspelled_policy_field(self):
        self.assertTrue(self.bad(policy={"writable_root": ["x"]}))

    def test_misspelled_attack_field(self):
        self.assertTrue(self.bad(attack={"cmd": "x", "blocked_exits": [3]}))

    def test_missing_part(self):
        c = dict(GOOD)
        del c["control"]
        self.assertTrue(run.invalid(c))

    def test_blocked_exit_must_not_contain_success(self):
        self.assertTrue(self.bad(attack={"cmd": "x", "blocked_exit": [0, 3]}))

    def test_blocked_exit_must_be_statuses(self):
        self.assertTrue(self.bad(attack={"cmd": "x", "blocked_exit": "3"}))

    def test_repeat(self):
        self.assertTrue(self.bad(repeat=0))
        self.assertEqual(self.bad(repeat=5), [])

    def test_assert_that_observes_nothing(self):
        self.assertTrue(self.bad(**{"assert": {"settle_secs": 1}}))


class Corpus(unittest.TestCase):
    def test_every_published_contract_is_valid(self):
        root = os.path.join(os.path.dirname(RUNNER), "contracts")
        files = sorted(glob.glob(os.path.join(root, "*", "*.toml")))
        self.assertTrue(files)
        ids = set()
        for f in files:
            with self.subTest(contract=os.path.relpath(f, root)):
                with open(f, "rb") as fh:
                    c = tomllib.load(fh)
                self.assertEqual(run.invalid(c), [])
                self.assertNotIn(c["id"], ids, "duplicate id")
                ids.add(c["id"])
                self.assertEqual(c["category"], os.path.basename(os.path.dirname(f)),
                                 "category must be the folder it lives in (spec/format.md)")


if __name__ == "__main__":
    unittest.main()
