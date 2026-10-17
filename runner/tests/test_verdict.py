"""The decision procedure (runner/verdict.py) against spec/verdicts.md, rule by rule."""
import os, sys, unittest

RUNNER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RUNNER)
import verdict as v  # noqa: E402


def contract(**attack):
    return {"id": "t", "attack": {"cmd": "x", **attack}, "control": {"cmd": "y"}}


def res(exit=0, timed_out=False, stderr=""):
    return {"exit": exit, "timed_out": timed_out, "stderr": stderr}


def phase(attack, effect=False, control_ok=True, **extra):
    return {"attack": attack, "effect": effect, "control_ok": control_ok, **extra}


class Mode(unittest.TestCase):
    def test_effect_when_the_baseline_shows_it(self):
        c = {**contract(), "assert": {"unchanged": "f"}}
        self.assertEqual(v.mode(c, True), "effect")

    def test_exit_when_the_effect_is_not_visible(self):
        c = {**contract(), "assert": {"unchanged": "f"}}  # a read leaves the file unchanged
        self.assertEqual(v.mode(c, False), "exit")

    def test_fidelity(self):
        self.assertEqual(v.mode(contract(expect_exit=143), False), "fidelity")


class AttackOutcome(unittest.TestCase):
    """§4.6: an exit status never stands for two outcomes."""

    def test_effect_decides_regardless_of_exit(self):
        c = contract()
        self.assertEqual(v.attack_outcome(c, "effect", True, res(1)), "took-effect")
        self.assertEqual(v.attack_outcome(c, "effect", False, res(0)), "blocked")

    def test_success_status(self):
        self.assertEqual(v.attack_outcome(contract(), "exit", False, res(0)), "took-effect")

    def test_ordinary_failure_is_a_block(self):
        for code in (1, 2, 7, 56, 101):  # the statuses seen in the 2026-10-15 runs
            self.assertEqual(v.attack_outcome(contract(), "exit", False, res(code)), "blocked")

    def test_statuses_that_never_decide(self):
        for code in (126, 127, 128 + 6, 128 + 9, 128 + 11):  # not executable, not found, ABRT, KILL, SEGV
            with self.subTest(code=code):
                self.assertEqual(v.attack_outcome(contract(), "exit", False, res(code)), "unclear")

    def test_seccomp_kill_is_a_block(self):
        self.assertEqual(v.attack_outcome(contract(), "exit", False, res(v.SIGSYS_EXIT)), "blocked")

    def test_timeout_is_unclear(self):
        self.assertEqual(v.attack_outcome(contract(), "exit", False, res(137, timed_out=True)), "unclear")

    def test_declared_blocked_exit(self):
        c = contract(blocked_exit=[3])
        self.assertEqual(v.attack_outcome(c, "exit", False, res(3)), "blocked")
        self.assertEqual(v.attack_outcome(c, "exit", False, res(1)), "unclear")  # a crash
        self.assertEqual(v.attack_outcome(c, "exit", False, res(0)), "took-effect")

    def test_fidelity_outcome(self):
        c = contract(expect_exit=143)
        self.assertEqual(v.attack_outcome(c, "fidelity", False, res(143)), "blocked")
        self.assertEqual(v.attack_outcome(c, "fidelity", False, res(0)), "took-effect")
        self.assertEqual(v.attack_outcome(c, "fidelity", False, res(143, timed_out=True)), "unclear")


class Baseline(unittest.TestCase):
    """§4.4."""

    def test_lab_error(self):
        self.assertEqual(v.decide_baseline(contract(), {"error": "boom"})[0], "harness-error")

    def test_vacuous(self):
        self.assertEqual(v.decide_baseline(contract(), phase(res(1)))[0], "vacuous")

    def test_crash_without_sandbox_is_vacuous(self):
        self.assertEqual(v.decide_baseline(contract(), phase(res(127)))[0], "vacuous")

    def test_invalid_baseline(self):
        self.assertEqual(v.decide_baseline(contract(), phase(res(0), control_ok=False))[0], "invalid-baseline")

    def test_declared_control_requires_sandbox(self):
        c = {**contract(), "control_requires_sandbox": "checks a proxy variable"}
        self.assertIsNone(v.decide_baseline(c, phase(res(0), control_ok=False))[0])

    def test_fidelity_baseline_must_report_the_status(self):
        c = contract(expect_exit=143)
        self.assertIsNone(v.decide_baseline(c, phase(res(143)))[0])
        self.assertEqual(v.decide_baseline(c, phase(res(0)))[0], "vacuous")

    def test_valid(self):
        r, m, _ = v.decide_baseline(contract(), phase(res(0)))
        self.assertIsNone(r)
        self.assertEqual(m, "exit")


class Sandboxed(unittest.TestCase):
    """§4.5."""

    def test_lab_error(self):
        self.assertEqual(v.decide_sandboxed(contract(), "exit", {"error": "boom"})[0], "harness-error")

    def test_sandbox_that_does_not_start(self):
        sb = {"valid_probe": res(127)}
        self.assertEqual(v.decide_sandboxed(contract(), "exit", sb)[0], "harness-error")

    def test_refusal_with_signature(self):
        sig = {"exit": [78], "stderr": "refused"}
        sb = {"valid_probe": res(0), "refusal_probe": res(78, stderr="policy refused: x")}
        self.assertEqual(v.decide_sandboxed(contract(), "effect", sb, sig)[0], "contained")

    def test_refusal_without_signature(self):
        sb = {"valid_probe": res(0), "refusal_probe": res(78, stderr="policy refused")}
        self.assertEqual(v.decide_sandboxed(contract(), "effect", sb, None)[0], "inconclusive")

    def test_refusal_with_the_wrong_status(self):
        sig = {"exit": [78], "stderr": "refused"}
        sb = {"valid_probe": res(0), "refusal_probe": res(1, stderr="refused")}
        self.assertEqual(v.decide_sandboxed(contract(), "effect", sb, sig)[0], "inconclusive")

    def test_refusal_with_the_wrong_message(self):
        sig = {"exit": [78], "stderr": "refused"}
        sb = {"valid_probe": res(0), "refusal_probe": res(78, stderr="segmentation fault")}
        self.assertEqual(v.decide_sandboxed(contract(), "effect", sb, sig)[0], "inconclusive")

    def test_escaped(self):
        sb = phase(res(1), effect=True, valid_probe=res(0))
        self.assertEqual(v.decide_sandboxed(contract(), "effect", sb)[0], "escaped")

    def test_escaped_even_if_the_control_failed(self):
        sb = phase(res(0), control_ok=False, valid_probe=res(0))
        self.assertEqual(v.decide_sandboxed(contract(), "exit", sb)[0], "escaped")

    def test_control_broke(self):
        sb = phase(res(1), control_ok=False, valid_probe=res(0))
        self.assertEqual(v.decide_sandboxed(contract(), "exit", sb)[0], "control-broke")

    def test_contained(self):
        sb = phase(res(1), valid_probe=res(0))
        self.assertEqual(v.decide_sandboxed(contract(), "exit", sb)[0], "contained")

    def test_inconclusive_attack(self):
        sb = phase(res(139), valid_probe=res(0))
        self.assertEqual(v.decide_sandboxed(contract(), "exit", sb)[0], "inconclusive")


class Repetitions(unittest.TestCase):
    """§4.7."""

    def test_any_escape(self):
        r, why = v.combine(["contained", "escaped", "contained"])
        self.assertEqual((r, why), ("escaped", "escaped in 1 of 3 repetitions"))

    def test_all_contained(self):
        self.assertEqual(v.combine(["contained"] * 5)[0], "contained")

    def test_mixed(self):
        for mix in (["contained", "control-broke"], ["contained", "harness-error"], ["contained", "inconclusive"]):
            with self.subTest(mix=mix):
                self.assertEqual(v.combine(mix)[0], "inconclusive")


class Vocabulary(unittest.TestCase):
    def test_groups_are_disjoint_and_complete(self):
        groups = [set(v.MEASURED), set(v.NOT_MEASURED), set(v.LAB_FAULTS)]
        self.assertEqual(sum(len(g) for g in groups), len(set().union(*groups)))
        self.assertEqual(set(v.RESULTS), set().union(*groups))


if __name__ == "__main__":
    unittest.main()
