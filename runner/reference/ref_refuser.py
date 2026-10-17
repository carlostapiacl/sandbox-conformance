"""Reference: refuses a writable root that is a symlink, and says so.

That is the one guarantee it implements; anything else runs unconfined. The
refusal has a declared signature (exit 78 and a message), so the lab can tell
it from a sandbox that failed to start.
"""
import os
from common import basis

NAME = "ref-refuser"
REFUSAL = {"exit": [78], "stderr": "ref-refuser: policy refused"}


def identity():
    return {"version": "0", "reference": True}


def check(c):
    return {"unsupported": [], "notes": [], "basis": basis(c)}


def wrap(policy, m, c, env):
    bad = [w for w in policy.get("writable_roots", []) if os.path.islink(w)]
    if bad:
        msg = f"ref-refuser: policy refused: writable root {bad[0]} is a symlink"
        return {"argv": lambda cmd: ["/bin/sh", "-c", f"echo '{msg}' >&2; exit 78"], "env": env}
    return {"argv": lambda cmd: ["/bin/sh", "-c", cmd], "env": env}
