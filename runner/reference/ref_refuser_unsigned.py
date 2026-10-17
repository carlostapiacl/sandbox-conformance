"""Reference: refuses like ref_refuser, but declares no refusal signature.

Without a signature a refusal cannot be told from a failure to start, so the
refusal contract must come back `inconclusive`, not `contained`.
"""
from ref_refuser import identity, check, wrap  # noqa: F401  same behaviour

NAME = "ref-refuser-unsigned"
