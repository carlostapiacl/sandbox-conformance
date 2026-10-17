"""Reference: a sandbox that needs a host capability no host has.

Without it the sandbox would run but confine nothing (like landrun's
--best-effort with no Landlock), so every case must be not-applicable, never
a measured result.
"""
from ref_allow_all import identity, check, wrap  # noqa: F401  it would confine nothing

NAME = "ref-needs-host"
HOST_REQUIRES = ["no-such-capability"]
