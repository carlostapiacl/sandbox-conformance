# Run of 2026-11-08: all five sandboxes at their latest releases

The five sandboxes on the whole corpus (196 contracts, corpus v1.1), on one runner commit. Three
have new versions since they were last measured; sandbox-runtime and landrun are the same
releases, measured again so the five columns share one runner commit and the eight contracts
added since 2026-10-21 have a result for every sandbox.

> **Conflict of interest.** TartarOS is maintained by the author of this lab. Its adapter goes
> through the same review as the others, and every result file says so (`conflict_of_interest`).

| sandbox | version | since | adapter (SHA-256, first 12) |
|---|---|---|---|
| [sandbox-runtime](../../sandboxes/sandbox-runtime.md) | 0.0.81 | unchanged (latest on npm) | `42aabe8a1d41` |
| [nono](../../sandboxes/nono.md) | **0.81.0** | 0.80.0 | `f7653e7e3c7a` |
| [codex](../../sandboxes/codex.md) | **codex-cli 0.167.0** | 0.163.0 | `faf5ba529df0` |
| [landrun](../../sandboxes/landrun.md) | 0.1.17 | unchanged (latest release) | `a863856bc40f` |
| [tartaros](../../sandboxes/tartaros.md) | **0.1.0-alpha.24** (tag commit `060c3fc7`, built in the lab image) | 0.1.0-alpha.16 | `d561d1a16352` |

Runner and contracts: commit `dda0626` (recorded in every file as `runner_commit`). Against
`01fe653`, the commit of the earlier runs' runner, it changes only
[`runner/Dockerfile`](../../runner/Dockerfile) (the version pins, and the commit tartaros is built
from, now recorded) and the per-version tag-commit tables of the codex and nono adapters; no
mapping changes. A first pass on `8172948`, before those tables had the new versions, recorded
`unknown commit` for codex and nono; it was measured again on `dda0626` and gave the same result
on every contract of every sandbox, so only the second pass is published.
Spec version `1.0.0-draft`, profile `strict` (§7). 196 contracts.

## Results

| result | sandbox-runtime | nono | codex | landrun | tartaros |
|---|---|---|---|---|---|
| contained | 141 | 50 | 97 | 41 | 170 |
| escaped | 14 | 37 | 24 | 42 | 3 |
| control-broke | 1 | 5 | 29 | 1 | 0 |
| unsupported | 18 | 83 | 24 | 91 | 0 |
| vacuous | 9 | 8 | 9 | 7 | 10 |
| needs-feature | 1 | 1 | 1 | 2 | 1 |
| not applicable | 12 | 12 | 12 | 12 | 12 |
| inconclusive, invalid-baseline, harness-error | 0 | 0 | 0 | 0 | 0 |

These counts are not a ranking (§8). The full table, escapes by reading and the review notes are
in [`comparison.md`](comparison.md).

## What changed, and why

**Reproduction first.** On this host and runner commit, the previous versions were measured
again: tartaros 0.1.0-alpha.16, codex-cli 0.163.0 and nono 0.80.0 (`baseline/`, recorded as
runner commit `01fe653`: the same contracts and mappings). Each gives, on all 196 contracts, the same result as its new version.

**No new version changes a result.** For every contract whose file is byte-identical to the one
of the sandbox's previous run:

| sandbox | versions | compared | changed |
|---|---|---|---|
| tartaros | 0.1.0-alpha.16 → 0.1.0-alpha.24 | 194 | 0 |
| codex | 0.163.0 → 0.167.0 | 182 | 0 |
| nono | 0.80.0 → 0.81.0 | 182 | 0 |

tartaros alpha.17 to alpha.24 changed macOS, Windows, Linux without user namespaces, parallel
runs and paths that vanish during setup; none of that is what this host measures (Linux 6.8 with
user namespaces, one run at a time), so an unchanged column is the expected result.

**Where the counts move, it is the corpus.** Since 2026-10-21 the corpus gained eight contracts
and six broker contracts changed their file ([`contracts/CHANGES.md`](../../contracts/CHANGES.md)):

- the six `credentials-masked-env-*` contracts (2026-10-26): sandbox-runtime and tartaros hold all
  six; codex, nono and landrun have no masked credentials (`unsupported`);
- `secrets-read-deny-via-proc-self-root` and `filesystem-write-deny-survives-recursive-remove`,
  from Deno's permission tests (corpus v1.1): contained by sandbox-runtime, codex and tartaros;
  `unsupported` for nono and landrun, which cannot state a deny;
- the six broker contracts changed their file on 2026-10-22 and stay `unsupported` for the four
  sandboxes without a broker.

So sandbox-runtime goes from 133 to 141 contained (the eight new ones), codex from 95 to 97 (the
two Deno ones) and 18 to 24 unsupported (the six masked ones), nono and landrun gain eight
unsupported each, and tartaros goes from 168 to 170 contained (the two Deno ones).

**No escape is new**, so every escape keeps its reading ([`review.json`](review.json), carried
over only where the result and the contract file are identical). tartaros's three are the same
as in alpha.10: two contract assumptions (`/proc/1` and the parent are the run's own processes in
its private PID namespace; the supervisor has no `/proc` entry there) and one documented limit
(a repository created during the run, on Linux).

## A correction to an earlier run's metadata

The [2026-10-26 run](../2026-10-26-tartaros-alpha16/README.md) records tartaros 0.1.0-alpha.16 as
built from commit `f245b8fd`. After that run the tartaros history was rewritten to replace a
private hostname in a unit test's fixture strings, and the tag `v0.1.0-alpha.16` now points to
`481448e4`, which differs from `f245b8fd` only in those strings (`broker/src/lib.rs`, three lines
inside `mod tests`). `f245b8fd` can no longer be fetched from the public repository. The baseline
of this run was built from `481448e4`, and it reproduces the 2026-10-26 result on all 194 contracts
of that run, whose files are all unchanged.

## Host

The same disposable virtual machine recipe as the earlier runs
([`runner/lima/`](../../runner/lima/README.md)): Ubuntu 24.04.5 LTS, kernel `6.8.0-146-generic`,
x86_64, Landlock ABI 4, AppArmor on, nothing mounted from the machine that ran it. Its disk was
grown from 25 to 50 GB before the run; nothing else about it changed. Each sandbox ran in a `--rm`
Docker container (docker 29.1.3) started by [`runner/lab.sh`](../../runner/lab.sh) on the witness
network (`SC_WITNESS=1`, [`runner/lab-witness.sh`](../../runner/lab-witness.sh)), with the options
recorded in every file, from the `sc-lab:tools` image built from
[`runner/Dockerfile`](../../runner/Dockerfile).

## Files

- `<sandbox>.json`: one line per contract, no raw output, with its review note when it has one.
- `raw/<sandbox>.full.json`: everything the runner captured, per phase.
- `baseline/<sandbox>.full.json`: tartaros 0.1.0-alpha.16, codex-cli 0.163.0 and nono 0.80.0 on
  this host and runner commit, the reproduction above.
- `comparison.md`: contract by sandbox, measured results only.
- `review.json`: the readings (§6), carried over from the latest earlier run of each sandbox.
