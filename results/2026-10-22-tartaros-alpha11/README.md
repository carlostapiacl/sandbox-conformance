# Run of 2026-10-22: TartarOS 0.1.0-alpha.11, the broker contracts measured

TartarOS only, on the host of the [2026-10-21 run](../2026-10-21/README.md), a few hours
after its [first measurement](../2026-10-22-tartaros/README.md) (0.1.0-alpha.10).

> **Conflict of interest.** TartarOS is maintained by the author of this lab, and the change
> to the lab that made these contracts measurable was prompted by adding a broker to
> TartarOS's CLI ([`contracts/CHANGES.md`](../../contracts/CHANGES.md)). The result file
> records the conflict (`conflict_of_interest`). These counts are not a ranking (spec §8).

| | |
|---|---|
| sandbox | [tartaros](../../sandboxes/tartaros.md) **0.1.0-alpha.11**, tagged commit `57ceab2f`, built in the lab image |
| adapter | [`runner/adapters/tartaros.py`](../../runner/adapters/tartaros.py), SHA-256 `0b0ed2579a28…` (maps `[broker]` since this run) |
| runner and contracts | commit `49ab364`: the [reference broker](../../spec/format.md#the-broker-table) in the baseline of the `[broker]` contracts, and four of them completed (logged in `contracts/CHANGES.md`) |
| host | Ubuntu 24.04.5, kernel 6.8.0-146-generic, Landlock ABI 4 ([`runner/lima/`](../../runner/lima/README.md)) |
| image | the 2026-10-21 lab image plus one layer, the `tartaros` binary |
| profile | `strict` (spec §7): `--strict` always |

## Results

| result | tartaros |
|---|---|
| contained | 162 |
| escaped | 3 |
| control-broke | 0 |
| unsupported | 0 |
| vacuous | 10 |
| needs-feature | 1 |
| not applicable | 12 |
| inconclusive, invalid-baseline, harness-error | 0 |

Full table in [`comparison.md`](comparison.md); raw evidence in `raw/`.

**What changed against 0.1.0-alpha.10.** Only the 13 `[broker]` contracts, all of them
`unsupported` before: 12 are now **contained** and 1 is **vacuous**
(`network-broker-survives-malformed-client`: even the reference broker survives that
abuse, so the attack proves nothing as written). Six of the 13 contract files changed
with the lab change above; the others are byte-identical. Every other result is the same.

**The 3 escapes** are the same as in alpha.10, with the same readings
([`review.json`](review.json)): two contract assumptions (`/proc/1` and the agent's own
`sh` inside the run's PID namespace) and one documented limit (a repository created
during the run, tartaros `docs/limits.md`). No escape is `confirmed`.

**What the reference broker showed.** Before counting, each broker contract's attack was
run against the reference broker (no token check, agent headers forwarded, prefix matched
as a string, redirects followed, any host by name). Twelve attacks got through it; that is
what makes TartarOS's twelve `contained` mean something. One of them,
`network-broker-path-dot-segments`, also caught a real bug in TartarOS while the broker was
being added to its CLI: a capability path with percent-encoded dot segments left its
upstream base. It was fixed in 0.1.0-alpha.11, before this run.

## Next to the 2026-10-21 run

Same host and lab tools; the other columns are the 2026-10-21 results, where the
`[broker]` contracts were `unsupported` for every sandbox (their adapters have no broker
mapping). Not a ranking.

| result | sandbox-runtime 0.0.81 | nono 0.80.0 | codex 0.163.0 | landrun 0.1.17 | tartaros 0.1.0-alpha.11 |
|---|---|---|---|---|---|
| contained | reported | 50 | 95 | 41 | 162 |
| escaped | reported | 37 | 24 | 42 | 3 |
| control-broke | reported | 5 | 29 | 1 | 0 |
| unsupported | reported | 75 | 18 | 83 | 0 |

sandbox-runtime: findings reported to the vendor; its results will be published once they are fixed.
