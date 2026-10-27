#!/usr/bin/env python3
"""Turn full runner output into the published files of one run.

  report.py <full-json-dir> <results/DATE>

Writes <sandbox>.json (one line per contract, no raw output),
raw/<sandbox>.full.json (everything the runner captured) and comparison.md.
"""
import json, os, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpus  # noqa: E402

ORDER = ["sandbox-runtime", "nono", "codex", "landrun", "tartaros"]  # preferred column order; any other <name>.json is appended
# Review kinds that put a mark after a result (see the legend in comparison.md).
MARK = {"contract-assumption": "‡", "interface": "‡", "kernel-dependent": "§", "platform-dependent": "§",
        "documented": "", "design": "", "confirmed": ""}  # kernel-dependent: v0 name of platform-dependent
RESULTS = ["contained", "escaped", "control-broke", "inconclusive", "unsupported", "vacuous", "needs-feature",
           "not-applicable", "invalid-contract", "invalid-baseline", "harness-error"]
V1_ONLY = {"inconclusive", "invalid-baseline", "harness-error"}  # listed only when a run has them
DEFAULT_BASIS = ("default", "built-in")  # v1 / v0 spelling of spec/verdicts.md §5


def slim(r):
    keep = {k: r[k] for k in ("id", "category", "severity", "result", "reason", "basis", "judged_by", "spec_version", "profile",
                              "ran_as", "mapping_notes", "control_fails_unsandboxed", "control_requires_sandbox", "file", "contract_sha256",
                              "source", "derived_from") if k in r and r[k]}
    sb = r.get("sandboxed") or {}
    if isinstance(sb, list):  # repetitions: summarize the first, the reason gives k of n
        sb = sb[0] if sb else {}
    if "attack" in sb:
        keep["attack_exit"] = sb["attack"]["exit"]
        keep["control_exit"] = sb["control"]["exit"]
        ev = sb.get("effect_evidence") or (sb.get("signals") or {}).get("effect_evidence")  # v1 / v0
        if ev:
            keep["effect"] = ev
    return keep


def main(src, dst):
    os.makedirs(os.path.join(dst, "raw"), exist_ok=True)
    import glob as _glob
    present = sorted(os.path.basename(f)[:-5] for f in _glob.glob(os.path.join(src, "*.json")))
    names = [n for n in ORDER if n in present] + [n for n in present if n not in ORDER]
    runs = {}
    for name in names:
        f = os.path.join(src, name + ".json")
        if not os.path.exists(f):
            continue
        d = json.load(open(f))
        runs[name] = d
        shutil.copy(f, os.path.join(dst, "raw", name + ".full.json"))
        out = {k: d[k] for k in d if k != "contracts"}
        # Which corpus version the run measured, from the hashes it recorded
        # (runner/corpus.py; null for a run from before the versions).
        out["corpus"] = corpus.corpus_of(d)
        rv = (json.load(open(os.path.join(dst, "review.json"))) if os.path.exists(os.path.join(dst, "review.json")) else {}).get(name, {})
        out["contracts"] = [dict(slim(r), **({"review": {"kind": rv[r["id"]][0], "note": rv[r["id"]][1]}} if r["id"] in rv else {}))
                            for r in d["contracts"]]
        with open(os.path.join(dst, name + ".json"), "w") as fh:
            json.dump(out, fh, indent=1)
            fh.write("\n")

    ids = sorted({r["id"] for d in runs.values() for r in d["contracts"]},
                 key=lambda i: (next(r["category"] for d in runs.values() for r in d["contracts"] if r["id"] == i), i))
    by = {n: {r["id"]: r for r in d["contracts"]} for n, d in runs.items()}
    rv_path = os.path.join(dst, "review.json")
    review = json.load(open(rv_path)) if os.path.exists(rv_path) else {}
    run_date = min(d.get("run_at", "")[:10] for d in runs.values()) or "(undated)"
    seen = {r for d in runs.values() for r in d["counts"]}
    shown = [x for x in RESULTS if x not in V1_ONLY or x in seen]
    legend = {
        "inconclusive": "| `inconclusive` | the case ran, but the evidence does not decide the outcome |",
        "invalid-baseline": "| `invalid-baseline` | the control fails even without a sandbox: a fault of the contract, not of the sandbox |",
        "harness-error": "| `harness-error` | the lab itself failed: the result says nothing about the sandbox |",
    }
    L = [f"# Comparison, run of {run_date}", "",
         "Each cell is the result of one contract against one sandbox, set up through its adapter "
         "(`runner/adapters/`) as strictly as that sandbox's documentation allows. Only results we "
         "actually measured are listed. The host and the method are described in `README.md`.", "",
         "| result | meaning |", "|---|---|",
         "| `contained` | the attack failed and the legitimate control still worked |",
         "| `escaped` | the attack succeeded under the sandbox |",
         "| `control-broke` | the attack failed, and so did the legitimate control |",
         "| `unsupported` | the sandbox cannot express a `[policy]` field: a missing feature, not a vulnerability |",
         "| `vacuous` | the attack fails on this host even without a sandbox, so the result proves nothing |",
         "| `needs-feature` | the runner or the adapter cannot provide something the contract needs |",
         "| `n/a` | macOS-only contract, or the host lacks something the contract requires |",
         *[legend[x] for x in shown if x in legend], "",
         "Marks after a result:", "",
         "- `*`: no `[policy]` field asks for this guarantee, so the result reflects the sandbox's defaults. "
         "An escape marked this way is a difference of defaults, not a configured rule that failed.",
         "- `‡`: the contract counts this as an attack, but given how the sandbox is built it is not a breach. The notes below say why.",
         "- `§`: the result depends on a newer kernel than this host's (Landlock ABI 6).", "",
         "## Totals", "", "| result | " + " | ".join(runs) + " |", "|---|" + "---|" * len(runs)]
    for res in shown:
        L.append(f"| {res} | " + " | ".join(str(d["counts"].get(res, 0)) for d in runs.values()) + " |")
    if any(d.get("spec_version") for d in runs.values()):
        # spec/verdicts.md §8.3: a count of escapes is broken down by reading, so
        # confirmed findings read apart from contract assumptions and known limits.
        order = ["confirmed", "documented", "design", "platform-dependent", "contract-assumption", "interface", "pending"]
        rename = {"kernel-dependent": "platform-dependent"}
        tally = {n: {k: 0 for k in order} for n in runs}
        for n in runs:
            for r in runs[n]["contracts"]:
                if r["result"] == "escaped":
                    rv = review.get(n, {}).get(r["id"])
                    k = rename.get(rv[0], rv[0]) if rv else "pending"
                    tally[n][k if k in tally[n] else "pending"] += 1
        L += ["", "## Escapes by reading", "",
              "What each `escaped` means on review (spec/verdicts.md §6). Only `confirmed` is a guarantee "
              "that did not hold as stated; `pending` has not been reviewed yet.", "",
              "| reading | " + " | ".join(runs) + " |", "|---|" + "---|" * len(runs)]
        for k in order:
            L.append(f"| {k} | " + " | ".join(str(tally[n][k]) for n in runs) + " |")
        L.append("| **escaped** | " + " | ".join(str(sum(tally[n].values())) for n in runs) + " |")
    L += ["", "## Per contract", "", "| contract | category | " + " | ".join(runs) + " |", "|---|---|" + "---|" * len(runs)]
    for i in ids:
        cells, cat = [], ""
        for n in runs:
            r = by[n].get(i)
            if not r:
                cells.append("")
                continue
            cat = r["category"]
            v = "n/a" if r["result"] == "not-applicable" else r["result"]
            if r.get("basis") in DEFAULT_BASIS and v in ("contained", "escaped", "control-broke"):
                v += "*"
            rv = review.get(n, {}).get(i)
            if rv:
                v += MARK.get(rv[0], "")
            cells.append(v)
        if all(c == "n/a" for c in cells):
            continue
        L.append(f"| `{i}` | {cat} | " + " | ".join(cells) + " |")
    na = [i for i in ids if all(by[n].get(i, {}).get("result") == "not-applicable" for n in runs)]
    L += ["", f"Not applicable on this host for every sandbox ({len(na)}): " + ", ".join(f"`{i}`" for i in na) + "."]
    L += ["", "## Review notes", "",
          "We read the raw output (`raw/`) for every result other than `contained`. These notes explain "
          "a result; they never change it.", ""]
    for n in runs:
        notes = review.get(n, {})
        if not notes:
            continue
        L += [f"### {n}", ""]
        for i, (kind, text) in sorted(notes.items()):
            L.append(f"- `{i}` ({kind}): {text}")
        L.append("")
    up_path = os.path.join(dst, "upstream.json")
    upstream = json.load(open(up_path)) if os.path.exists(up_path) else {}
    if any(k in upstream for k in runs):
        L += ["## Upstream status", "",
              "Where each finding stands in the sandbox's own project, checked against its public issues, "
              "pull requests and commits. \"Fixed in\" names the first release with the fix, or the commit "
              "on the default branch when no release has it yet. The results above were measured on the "
              "versions in `README.md`.", ""]
        for n in runs:
            items = upstream.get(n)
            if not items:
                continue
            L += [f"### {n}", "", "| finding | contracts | status | fixed in | references |", "|---|---|---|---|---|"]
            for it in items:
                refs = ", ".join(f"[#{u.rstrip('/').split('/')[-1]}]({u})" for u in it["refs"]) or "none found"
                cs = ", ".join(f"`{c}`" for c in it["contracts"]) or "(observation)"
                L.append(f"| {it['finding']} | {cs} | {it['status']} | {it['fixed_in']} | {refs} |")
            L.append("")
    with open(os.path.join(dst, "comparison.md"), "w") as fh:
        fh.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
