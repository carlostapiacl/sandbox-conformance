# landrun re-run of 2026-10-17: the granted read model (SC-003)

landrun 0.1.17 only, on the host of the [2026-10-16 run](../2026-10-16/README.md) (Ubuntu
24.04, kernel 6.8.0-146-generic, Landlock ABI 4; [`runner/lima/`](../../runner/lima/README.md)).
The other three sandboxes are not re-measured: their 2026-10-16 results stand.

**Why.** The adapter used to report `read_scope = "granted"` unsupported, claiming landrun
needs a grant on an ancestor of the workspace to reach it. Measured: it does not (Landlock
checks no ancestor on path walk). The adapter now expresses the granted model.

**What changed against 2026-10-16** (landrun column; full table in [`comparison.md`](comparison.md)):

| | 2026-10-16 | 2026-10-17 |
|---|---|---|
| contained | 24 | 41 |
| escaped | 38 | 42 |
| unsupported | 105 | 83 |
| vacuous | 6 | 7 |
| control-broke | 1 | 1 |

All 22 changes are contracts that were `unsupported` and are now measured: 17 contained,
4 escaped, 1 vacuous. The 4 escapes are the same as nono's in this model: a granted path
that is a symlink into the protected area (3, reading `design`) and a unix socket in an
ungranted directory (1, `documented`).

**Contracts.** Measuring this surfaced nine contracts that named `{root}/work` as a writable
root without creating it; landrun refuses a grant on a missing path. They were fixed after the
`corpus-2026-10-16` freeze and the change is logged in
[`contracts/CHANGES.md`](../../contracts/CHANGES.md). Re-measured with the fix, nono and
codex give the same result on those nine as on 2026-10-16.

Runner and contracts: the commit recorded in `raw/landrun.full.json` as `runner_commit`.
