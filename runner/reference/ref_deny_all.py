"""Reference: starts, then stops every operation.

It runs `true` (so the lab sees a sandbox that starts) and refuses to run
anything else, exiting 1 like a denied operation. It blocks every attack and
breaks every control, so it must never be reported `contained`.
"""
from common import basis

NAME = "ref-deny-all"


def identity():
    return {"version": "0", "reference": True}


def check(c):
    return {"unsupported": [], "notes": [], "basis": basis(c)}


def wrap(policy, m, c, env):
    def argv(cmd):
        if cmd == "true":
            return ["/bin/sh", "-c", "true"]
        return ["/bin/sh", "-c", "echo 'ref-deny-all: operation not permitted' >&2; exit 1"]
    return {"argv": argv, "env": env}
