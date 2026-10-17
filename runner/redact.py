#!/usr/bin/env python3
"""Hold contracts out of published results while a coordinated disclosure is open
(spec/verdicts.md §9, SECURITY.md).

  redact.py <held-list> <full-json>...

<held-list> names one contract id per line (# comments allowed). It is kept
outside the repository: the list itself says which results are under
disclosure. Every record of a listed contract is dropped from the given runner
outputs, for every sandbox, and the counts are recomputed, so neither a cell
nor a row points at the finding. Files are rewritten in place. The contract
files themselves are held out of contracts/ by the same rule.
"""
import json, sys


def load_list(path):
    return {line.split("#", 1)[0].strip() for line in open(path)} - {""}


def drop(path, held):
    d = json.load(open(path))
    before = len(d["contracts"])
    d["contracts"] = [r for r in d["contracts"] if r["id"] not in held]
    counts = {}
    for r in d["contracts"]:
        counts[r["result"]] = counts.get(r["result"], 0) + 1
    d["counts"] = counts
    with open(path, "w") as fh:
        json.dump(d, fh, indent=1)
    return before - len(d["contracts"])


def main(listfile, *files):
    held = load_list(listfile)
    for f in files:
        print(f"{drop(f, held):3} held out  {f}")


if __name__ == "__main__":
    main(*sys.argv[1:])
