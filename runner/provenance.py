#!/usr/bin/env python3
"""Where each contract comes from, and whether it was written alongside TartarOS.

  provenance.py build    write corpus/provenance.json from contracts/ and the table below
  provenance.py check    fail if a contract has no entry, or an entry has no contract

The lab is maintained by TartarOS's author. Every contract re-expresses a guarantee
from another project's public test suite (its `source` field); `with_tartaros` says
how its writing relates to TartarOS:

  no                  in the corpus frozen at corpus-2026-10-16, before TartarOS was
                      first measured (2026-10-22), or added later with no TartarOS
                      feature behind it
  written-alongside   written by the lab's author at the same time as the TartarOS
                      feature it tests, so TartarOS was built to pass it
  changed-alongside   in the frozen corpus, but its assert was changed when the same
                      feature was added to TartarOS (the attack and control were not)

This file lives outside contracts/, so it does not change a contract's hash or the
corpus version. contracts/CHANGES.md has the full story of each change.
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus  # noqa: E402

OUT = os.path.join(corpus.CORPUS, "provenance.json")

MASKED = "Written the same day as TartarOS's masked credentials (0.1.0-alpha.16, 2026-10-26)."
BROKER = ("Its assert was added on 2026-10-22, when TartarOS got its broker; the attack and control are "
          "the frozen ones.")
TABLE = {
    **{f"credentials-masked-env-{s}": ("written-alongside", MASKED) for s in (
        "agent-holds-sentinel", "body-scoped", "no-laundering", "not-in-process-records",
        "not-sent-to-other-host", "plain-http-not-swapped")},
    "lifecycle-protected-path-not-in-git": ("written-alongside",
        "TartarOS 0.1.0-alpha.25 makes its placeholders directories git does not list, and was designed "
        "to pass it (corpus v1.2, 2026-11-20)."),
    "lifecycle-no-host-artifacts-after-sigterm": ("written-alongside",
        "Written with the one above, while working on TartarOS's placeholders; 0.1.0-alpha.24 already "
        "passed it (corpus v1.2, 2026-11-20)."),
    **{i: ("changed-alongside", BROKER) for i in (
        "network-broker-no-request-smuggling", "network-broker-path-dot-segments",
        "credentials-broker-injected-header-not-overridable", "network-broker-allowlist-lookalike")},
}


def project(source):
    m = re.match(r"\s*([\w.-]+/[\w.-]+)", source or "")
    return m.group(1) if m else None


def build():
    import tomllib, glob
    out = {}
    for f in sorted(glob.glob(os.path.join(corpus.CONTRACTS, "*", "*.toml"))):
        c = tomllib.load(open(f, "rb"))
        parent = c.get("derived_from")
        src = c.get("source")
        if not src and parent:  # a by-omission variant: same source as its contract
            pf = glob.glob(os.path.join(corpus.CONTRACTS, "*", parent + ".toml"))
            src = tomllib.load(open(pf[0], "rb")).get("source") if pf else None
        kind, why = TABLE.get(c["id"], TABLE.get(parent, ("no", None)))
        e = {"source_project": project(src), "with_tartaros": kind}
        if why:
            e["why"] = why
        if parent:
            e["by_omission_of"] = parent
        out[c["id"]] = e
    missing = [i for i in TABLE if i not in out]
    if missing:
        raise SystemExit(f"table names contracts that do not exist: {missing}")
    return out


def main(cmd):
    if cmd == "build":
        with open(OUT, "w") as fh:
            json.dump(build(), fh, indent=1, sort_keys=True)
            fh.write("\n")
    elif cmd == "check":
        if json.load(open(OUT)) != build():
            raise SystemExit("corpus/provenance.json is stale: run runner/provenance.py build")
    else:
        raise SystemExit(__doc__)


def load():
    return json.load(open(OUT)) if os.path.exists(OUT) else {}


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
