"""Reference: a sandbox binary that never starts (a missing library, a bad build).

Every invocation fails before running anything. Nothing it produces says
anything about confinement, so every case must be a lab fault.
"""
from common import basis

NAME = "ref-broken"


def identity():
    return {"version": "0", "reference": True}


def check(c):
    return {"unsupported": [], "notes": [], "basis": basis(c)}


def wrap(policy, m, c, env):
    fail = ["/bin/sh", "-c", "echo 'ref-broken: error while loading shared libraries' >&2; exit 127"]
    return {"argv": lambda cmd: fail, "env": env}
