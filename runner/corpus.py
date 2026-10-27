#!/usr/bin/env python3
"""The corpus versions: which contracts, byte for byte, a version is.

  corpus.py build <version>     write corpus/v<version>.json from contracts/
  corpus.py check               contracts/ must be exactly the latest version
  corpus.py of <result.json>    which corpus version a run measured

A version is a manifest of every contract's id, path and SHA-256. A run records
the hash of each contract it ran, so whether it measured a version is a matter
of comparing hashes: a run that ran every contract of v1.0 unchanged measured
v1.0; one that ran some of them unchanged measured a subset of it. The rules
for when the version moves are in corpus/README.md.
"""
import glob, hashlib, json, os, re, sys, tomllib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONTRACTS = os.path.join(ROOT, "contracts")
CORPUS = os.path.join(ROOT, "corpus")


def vkey(v):
    return [int(x) for x in v.split(".")]


def sha256_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def current(contracts=CONTRACTS):
    """{id: {path, sha256, category, severity, os}} for the contracts on disk."""
    out = {}
    for f in sorted(glob.glob(os.path.join(contracts, "*", "*.toml"))):
        with open(f, "rb") as fh:
            c = tomllib.load(fh)
        out[c["id"]] = {"path": os.path.relpath(f, os.path.dirname(contracts)).replace(os.sep, "/"),
                        "sha256": sha256_file(f), "category": c.get("category"),
                        "severity": c.get("severity"), "os": c.get("os", [])}
    return out


def versions(corpus=CORPUS):
    """[(version, manifest)] oldest first."""
    found = []
    for f in glob.glob(os.path.join(corpus, "v*.json")):
        m = re.fullmatch(r"v(\d+\.\d+(?:\.\d+)?)\.json", os.path.basename(f))
        if m:
            found.append((m.group(1), json.load(open(f))))
    return sorted(found, key=lambda x: vkey(x[0]))


def diff(old, new):
    """(added, removed, changed) contract ids between two {id: entry} maps."""
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(i for i in set(old) & set(new) if old[i]["sha256"] != new[i]["sha256"])
    return added, removed, changed


def corpus_of(run, corpus=CORPUS):
    """What a run measured: {"version", "ran", "of", "whole"} for the newest
    version whose contracts the run ran unchanged, or None if every contract it
    ran differs from every version (a run from before the versions)."""
    ran = {r["id"]: r.get("contract_sha256") for r in run.get("contracts", [])}
    for v, m in reversed(versions(corpus)):
        cs = m["contracts"]
        if any(i in cs and cs[i]["sha256"] != h for i, h in ran.items()):
            continue
        if not any(i in cs for i in ran):
            continue
        same = sum(1 for i in ran if i in cs)
        if same < len(ran):
            continue
        return {"version": v, "ran": same, "of": len(cs), "whole": same == len(cs)}
    return None


def build(version, date):
    vs = versions()
    if vs and vkey(version) <= vkey(vs[-1][0]):
        sys.exit(f"corpus: v{version} is not newer than v{vs[-1][0]}")
    cur = current()
    man = {"corpus_version": version, "date": date, "count": len(cur), "contracts": cur}
    if vs:
        a, r, c = diff(vs[-1][1]["contracts"], cur)
        man["since"] = {"version": vs[-1][0], "added": a, "removed": r, "changed": c}
    os.makedirs(CORPUS, exist_ok=True)
    with open(os.path.join(CORPUS, f"v{version}.json"), "w") as fh:
        json.dump(man, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(f"corpus v{version}: {len(cur)} contracts")


def check():
    vs = versions()
    if not vs:
        sys.exit("corpus: no version yet")
    v, m = vs[-1]
    a, r, c = diff(m["contracts"], current())
    if a or r or c:
        sys.exit(f"corpus: contracts/ is not v{v}: added {a}, removed {r}, changed {c}. "
                 "Write the next version (corpus/README.md says which).")
    print(f"corpus: contracts/ is v{v} ({len(m['contracts'])} contracts)")


if __name__ == "__main__":
    cmd = sys.argv[1:2]
    if cmd == ["build"] and len(sys.argv) == 4:
        build(sys.argv[2], sys.argv[3])
    elif cmd == ["build"] and len(sys.argv) == 3:
        import time
        build(sys.argv[2], time.strftime("%Y-%m-%d"))
    elif cmd == ["check"]:
        check()
    elif cmd == ["of"] and len(sys.argv) == 3:
        print(json.dumps(corpus_of(json.load(open(sys.argv[2])))))
    else:
        sys.exit(__doc__)
