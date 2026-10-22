"""Reference: no confinement at all. Every valid attack must come back `escaped`."""
from common import basis

NAME = "ref-allow-all"
SANDBOX_ENV = {"SC_REF_SANDBOX": "1"}  # what a control with control_requires_sandbox checks
REFERENCE_BROKER = True  # its broker is the runner's reference one, with no defences


def identity():
    return {"version": "0", "reference": True}


def check(c):
    return {"unsupported": [], "notes": [], "basis": basis(c)}


def wrap(policy, m, c, env):
    env = dict(env, **SANDBOX_ENV)
    return {"argv": lambda cmd: ["/bin/sh", "-c", cmd], "env": env}
