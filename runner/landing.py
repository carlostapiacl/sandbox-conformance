#!/usr/bin/env python3
"""Rebuild the data block of the landing page (index.html) from published runs.

  landing.py <results/RUN> [<results/RUN> ...] [index.html]

Each run adds the sandboxes it measured; a later run does not replace an
earlier one's columns (a sandbox measured in two of them takes the later).

The page shows the same results and the same marks as that run's comparison.md:
`*` built-in guarantee, and the review marks (‡, §) from its review.json. Review
notes travel with the cell. Nothing here is typed by hand, so the page cannot
drift from the run it shows.
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from report import DEFAULT_BASIS, MARK, ORDER

KIND = {"sandbox-runtime": "bubblewrap + seccomp + proxy", "nono": "Landlock + proxy + supervisor",
        "codex": "bubblewrap + seccomp", "landrun": "pure Landlock",
        "tartaros": "Landlock + seccomp + namespaces + proxy"}
BLOCK = re.compile(r'(<script id="data" type="application/json">)(.*?)(</script>)', re.S)


def build(*run_dirs):
    runs, review, where = {}, {}, {}
    for run_dir in run_dirs:
        present = [f[:-5] for f in os.listdir(run_dir) if f.endswith(".json") and f != "review.json"
                   and f != "upstream.json"]
        for n in present:
            runs[n] = json.load(open(os.path.join(run_dir, n + ".json")))
            where[n] = run_dir
        rv_path = os.path.join(run_dir, "review.json")
        for n, v in (json.load(open(rv_path)) if os.path.exists(rv_path) else {}).items():
            if not n.startswith("_") and n in present:
                review[n] = v
    names = [n for n in ORDER if n in runs] + sorted(n for n in runs if n not in ORDER)
    by = {n: {c["id"]: c for c in d["contracts"]} for n, d in runs.items()}
    first = {}
    for n in names:
        for c in runs[n]["contracts"]:
            first.setdefault(c["id"], c)
    rows, marked = [], {n: {} for n in names}
    for i in sorted(first, key=lambda i: (first[i]["category"], i)):
        row = {"id": i, "cat": first[i]["category"], "sev": first[i]["severity"], "r": {}}
        m, notes = {}, {}
        for n in names:
            c = by[n].get(i)
            if not c:
                continue
            row["r"][n] = c["result"]
            mark = ""
            if c.get("basis") in DEFAULT_BASIS and c["result"] in ("contained", "escaped", "control-broke"):
                mark += "*"
            rv = review.get(n, {}).get(i)
            if rv:
                mark += MARK.get(rv[0], "")
                notes[n] = f"{rv[0]}: {rv[1]}"
                if MARK.get(rv[0]) == "‡":
                    marked[n][c["result"]] = marked[n].get(c["result"], 0) + 1
            if mark:
                m[n] = mark
        if m:
            row["m"] = m
        if notes:
            row["n"] = notes
        rows.append(row)
    any_run = runs[names[0]]
    abi = any_run["host"]["landlock_abi"]
    kernel = ".".join(any_run["host"]["kernel"].split(".")[:2])
    return {
        "sandboxes": names,
        # the version number, out of a longer --version string ("tartaros 0.1.0-alpha.10 (linux/…)")
        "versions": {n: (re.search(r"\d+\.\d+[0-9A-Za-z.\-]*", runs[n]["version"]) or [runs[n]["version"]])[0]
                     for n in names},
        "kind": {n: KIND.get(n, "") for n in names},
        "counts": {n: runs[n]["counts"] for n in names},
        # results the review reads as "counted as an attack, not a breach" (‡), per sandbox
        "not_breach": {n: v for n, v in marked.items() if v},
        "categories": sorted({r["cat"] for r in rows}),
        "rows": rows,
        "meta": {"run": max(os.path.basename(os.path.normpath(where[n]))[:10] for n in names), "contracts": len(rows),
                 "kernel": f"Linux {kernel}, Landlock ABI {abi}"},
    }


def main(*args):
    page = args[-1] if args and args[-1].endswith(".html") else "index.html"
    run_dirs = [a for a in args if not a.endswith(".html")]
    data = json.dumps(build(*run_dirs), separators=(",", ":"), ensure_ascii=False)
    s = open(page).read()
    if not BLOCK.search(s):
        sys.exit(f"{page}: no data block")
    s = BLOCK.sub(lambda m: m.group(1) + data + m.group(3), s, count=1)
    with open(page, "w") as fh:
        fh.write(s)


if __name__ == "__main__":
    main(*sys.argv[1:])
