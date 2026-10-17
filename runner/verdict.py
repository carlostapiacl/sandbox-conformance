"""The decision procedure of spec/verdicts.md (§4), as pure functions.

run.py observes (runs the phases, snapshots the effects); this module decides.
Nothing here touches the filesystem or runs a command, so every rule can be
read against the spec and tested on its own (runner/tests/test_verdict.py).
"""
import signal

SPEC_VERSION = "1.0.0-draft"

MEASURED = ("contained", "escaped", "control-broke", "inconclusive")       # §3.1
NOT_MEASURED = ("unsupported", "not-applicable", "vacuous")                # §3.2
LAB_FAULTS = ("invalid-contract", "invalid-baseline", "needs-feature", "harness-error")  # §3.3
RESULTS = MEASURED + NOT_MEASURED + LAB_FAULTS

ASSERT_KEYS = ("unchanged", "absent", "alive")
# A process killed by SIGSYS was stopped by a syscall filter (seccomp's kill
# action): that is a block, not a crash. Every other signal is unclear.
SIGSYS_EXIT = 128 + int(signal.SIGSYS)
NEVER_DECIDED = (126, 127)  # not executable / not found: the attack never ran


def has_assert(c):
    a = c.get("assert") or {}
    return any(k in a for k in ASSERT_KEYS)


def mode(c, baseline_effect):
    """§4.6: what decides whether the attack took effect.

    fidelity  the attack declares expect_exit and has no [assert]: the sandbox
              must report the command's own exit status faithfully
    effect    the [assert] showed the attack's effect in the baseline
    exit      otherwise: the attack's exit status
    """
    if "expect_exit" in c["attack"] and not has_assert(c):
        return "fidelity"
    return "effect" if baseline_effect else "exit"


def attack_outcome(c, m, effect, res):
    """'took-effect', 'blocked' or 'unclear' for one run of the attack.

    For a fidelity contract 'took-effect' means the reported status was wrong
    (the guarantee failed), 'blocked' that it was right.
    """
    if m == "effect":
        return "took-effect" if effect else "blocked"
    if res["timed_out"]:
        return "unclear"
    code, want = res["exit"], c["attack"].get("expect_exit", 0)
    if m == "fidelity":
        return "blocked" if code == want else "took-effect"
    if code == want:
        return "took-effect"
    declared = c["attack"].get("blocked_exit")
    if declared is not None:
        return "blocked" if code in declared else "unclear"
    if code in NEVER_DECIDED or (code >= 128 and code != SIGSYS_EXIT):
        return "unclear"
    return "blocked"


def decide_baseline(c, base):
    """§4.4. Returns (result or None, mode, reason). None: go on to the sandbox."""
    if base.get("error"):
        return "harness-error", None, "lab error in the baseline: " + base["error"]
    m = mode(c, base["effect"])
    out = attack_outcome(c, m, base["effect"], base["attack"])
    if m == "fidelity" and out != "blocked":
        return "vacuous", m, "without a sandbox the command does not report the status the contract expects"
    if m == "exit" and out != "took-effect":
        return "vacuous", m, "attack does not succeed without a sandbox"
    if not base["control_ok"] and not c.get("control_requires_sandbox"):
        return "invalid-baseline", m, ("the control fails without a sandbox and the contract does not "
                                       "declare control_requires_sandbox")
    return None, m, ""


def refusal_matches(signature, probe):
    """§4.5.2: a failed refusal probe is a refusal only if it matches the
    adapter's declared signature (exit status, and message where given)."""
    if not signature:
        return False
    if probe["exit"] not in signature.get("exit", []):
        return False
    text = signature.get("stderr")
    return text is None or text in (probe.get("stderr") or "")


def decide_sandboxed(c, m, sb, signature=None):
    """§4.5 for one sandboxed phase. Returns (result, reason)."""
    if sb.get("error"):
        return "harness-error", "lab error under the sandbox: " + sb["error"]
    if sb.get("unsupported"):
        return "unsupported", sb["unsupported"]
    vp = sb.get("valid_probe")
    if vp is not None and vp["exit"] != 0:
        return "harness-error", f"the sandbox does not start under a minimal policy (exit {vp['exit']})"
    rp = sb.get("refusal_probe")
    if rp is not None and rp["exit"] != 0:
        if refusal_matches(signature, rp):
            return "contained", "the sandbox refused this policy, with its declared refusal signature"
        return "inconclusive", (f"the sandbox did not start with this policy (exit {rp['exit']}), "
                                "and that does not match a declared refusal signature")
    out = attack_outcome(c, m, sb["effect"], sb["attack"])
    if out == "took-effect":
        return "escaped", ""
    if out == "unclear":
        a = sb["attack"]
        why = "timed out" if a["timed_out"] else f"exit {a['exit']}"
        return "inconclusive", f"the attack's exit status does not decide ({why})"
    if not sb["control_ok"]:
        return "control-broke", ""
    return "contained", ""


def combine(results):
    """§4.7: one result from the repetitions of a timing-dependent case."""
    n = len(results)
    k = sum(1 for r in results if r == "escaped")
    if k:
        return "escaped", f"escaped in {k} of {n} repetitions"
    if all(r == "contained" for r in results):
        return "contained", (f"contained in {n} of {n} repetitions" if n > 1 else "")
    return "inconclusive", "repetitions disagree: " + ", ".join(results)
