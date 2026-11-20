# Run of 2026-11-20: corpus v1.2 and the five sandboxes at their latest releases

The five sandboxes on the whole corpus (198 contracts, corpus v1.2), on one runner commit. Corpus
v1.2 adds two lifecycle contracts on the placeholders a sandbox puts at an absent protected path
([`contracts/CHANGES.md`](../../contracts/CHANGES.md)). Four sandboxes have new versions;
landrun is the same release, measured again so the five columns share one runner commit and the
two new contracts have a result for every sandbox.

> **Conflict of interest.** TartarOS is maintained by the author of this lab. Its adapter goes
> through the same review as the others, and every result file says so (`conflict_of_interest`).
> One of the two new contracts, `lifecycle-protected-path-not-in-git`, checks something TartarOS
> 0.1.0-alpha.25 was changed to do (its placeholders are empty directories, which git does not
> list): it was designed to pass that contract.

| sandbox | version | since | adapter (SHA-256, first 12) |
|---|---|---|---|
| [sandbox-runtime](../../sandboxes/sandbox-runtime.md) | **0.0.83** (tag commit `0bbebed0`) | 0.0.81 | `010c6d76d8c2` |
| [nono](../../sandboxes/nono.md) | **0.82.0** (tag commit `f1e0a7ac`), with its namespaces | 0.81.0 | `e619c9b12563` |
| [codex](../../sandboxes/codex.md) | **codex-cli 0.171.0** (tag commit `ccf9be8c`) | 0.167.0 | `8c1083a1c9ec` |
| [landrun](../../sandboxes/landrun.md) | 0.1.17 | unchanged (latest release) | `a863856bc40f` |
| [tartaros](../../sandboxes/tartaros.md) | **0.1.0-alpha.25** (tag commit `28a153fe`, built in the lab image) | 0.1.0-alpha.24 | `d561d1a16352` |

Runner and contracts: commit `cd322d7` (recorded in every file as `runner_commit`). Against
`1801507`, the runner of the earlier runs, it adds the two contracts and corpus v1.2, and changes
[`runner/Dockerfile`](../../runner/Dockerfile) (the version pins) and the per-version tag-commit
tables of the sandbox-runtime, codex and nono adapters; no mapping changes. That is why three
adapter hashes differ from the 2026-11-08 run while their code paths do not.
Spec version `1.0.0-draft`, profile `strict` (§7). 198 contracts.

## Results

| result | sandbox-runtime | nono | codex | landrun | tartaros |
|---|---|---|---|---|---|
| contained | 142 | 51 | 97 | 41 | 172 |
| escaped | 15 | 38 | 26 | 44 | 3 |
| control-broke | 1 | 5 | 29 | 1 | 0 |
| unsupported | 18 | 83 | 24 | 91 | 0 |
| vacuous | 9 | 8 | 9 | 7 | 10 |
| needs-feature | 1 | 1 | 1 | 2 | 1 |
| not applicable | 12 | 12 | 12 | 12 | 12 |
| inconclusive, invalid-baseline, harness-error | 0 | 0 | 0 | 0 | 0 |

The full table, escapes by reading and the review notes are in [`comparison.md`](comparison.md).

## What changed, and why

**Reproduction first.** On this host, the previous versions were measured again on corpus v1.2:
sandbox-runtime 0.0.81, tartaros 0.1.0-alpha.24, codex-cli 0.167.0 and nono 0.81.0 (`baseline/`,
runner commit `da9e9f5`: the same contracts and mappings, before the version pins of the other
three were raised). Each gives, on all 196 contracts it shares with its previous run, the same
result as that run (for nono, the [run with its namespaces](../2026-11-08-nono-isolate/README.md)).

**No new version changes a result on the contracts they share.** For every contract whose file is
byte-identical to the one of the baseline:

| sandbox | versions | compared | changed |
|---|---|---|---|
| sandbox-runtime | 0.0.81 → 0.0.83 | 198 | 0 |
| codex | 0.167.0 → 0.171.0 | 198 | 0 |
| nono | 0.81.0 → 0.82.0 | 198 | 0 |
| tartaros | 0.1.0-alpha.24 → 0.1.0-alpha.25 | 198 | 1 |

The one change is tartaros on `lifecycle-protected-path-not-in-git`, escaped under alpha.24 and
**contained** under alpha.25, the version made to pass it (see the conflict of interest above).

**The two new contracts.**

| contract | sandbox-runtime | nono | codex | landrun | tartaros |
|---|---|---|---|---|---|
| `lifecycle-no-host-artifacts` (existing: after a normal exit) | contained | escaped | escaped | escaped | contained |
| `lifecycle-no-host-artifacts-after-sigterm` | contained | escaped | escaped | escaped | contained |
| `lifecycle-protected-path-not-in-git` | **escaped** | escaped | escaped | escaped | contained |

- sandbox-runtime removes its placeholder when its launcher is ended by SIGTERM, as it does after a
  normal exit. While the command runs, the placeholder at `.mcp.json` is a file git lists as
  untracked (`?? .mcp.json`): the escape. Its README states that these mount points are visible
  on the host while a command runs, so the reading is `documented`.
- nono, codex and landrun do not protect `.mcp.json`, so the agent writes the file and it stays,
  as in the existing contract: `design`, with the same notes.
- tartaros alpha.24 already passed the SIGTERM contract; alpha.25 passes the git one.

So sandbox-runtime goes from 141 to 142 contained and 14 to 15 escaped, nono, codex and landrun
gain two escapes each (nono's `ipc-abstract-unix-socket` stays contained, as in the run with its
namespaces), and tartaros goes from 170 to 172 contained.

**Every other escape keeps its reading** ([`review.json`](review.json), carried over only where the
result and the contract file are identical).

## Host

The same disposable virtual machine as the 2026-11-08 run ([`runner/lima/`](../../runner/lima/README.md)):
Ubuntu 24.04.5 LTS, kernel `6.8.0-146-generic`, x86_64, Landlock ABI 4, AppArmor on, nothing
mounted from the machine that ran it. Each sandbox ran in a `--rm` Docker container (docker
29.1.3) started by [`runner/lab.sh`](../../runner/lab.sh) on the witness network (`SC_WITNESS=1`,
[`runner/lab-witness.sh`](../../runner/lab-witness.sh)), with the options recorded in every file,
from the `sc-lab:tools` image built from [`runner/Dockerfile`](../../runner/Dockerfile).
The sandbox-runtime 0.0.81 baseline ran in the image of the 2026-11-08 run; the other baselines in
the image of runner commit `da9e9f5`. Each file records its image.

## Files

- `<sandbox>.json`: one line per contract, no raw output, with its review note when it has one.
- `raw/<sandbox>.full.json`: everything the runner captured, per phase.
- `baseline/<sandbox>.full.json`: sandbox-runtime 0.0.81, tartaros 0.1.0-alpha.24, codex-cli
  0.167.0 and nono 0.81.0 on this host and corpus, the reproduction above.
- `comparison.md`: contract by sandbox, measured results only.
- `review.json`: the readings (§6), carried over from the latest earlier run of each sandbox, and
  the new ones for the two contracts.
