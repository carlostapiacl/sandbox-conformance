# Run of 2026-10-22: TartarOS 0.1.0-alpha.10

TartarOS only, on the host of the [2026-10-21 run](../2026-10-21/README.md). The other four
sandboxes are not re-measured: their 2026-10-21 results stand.

> **Conflict of interest.** TartarOS is maintained by the author of this lab. Its adapter
> was written before its first measurement and reviewed (see
> [`sandboxes/tartaros.md`](../../sandboxes/tartaros.md)); the result file records the
> conflict (`conflict_of_interest`). These counts are not a ranking (spec §8).

| | |
|---|---|
| sandbox | [tartaros](../../sandboxes/tartaros.md) **0.1.0-alpha.10**, tagged commit `8f2ba053`, built in the lab image |
| adapter | [`runner/adapters/tartaros.py`](../../runner/adapters/tartaros.py), SHA-256 `f19159ee14a1…` |
| runner and contracts | commit `393f538` (`runner_commit` in the result file); the contracts are the 188 of the 2026-10-21 run, byte for byte |
| host | Ubuntu 24.04.5, kernel 6.8.0-146-generic, Landlock ABI 4 ([`runner/lima/`](../../runner/lima/README.md)) |
| image | the 2026-10-21 lab image plus one layer, the `tartaros` binary: every other layer is identical, so the other sandboxes' tools are the same |
| profile | `strict` (spec §7): `--strict` always |

## Results

| result | tartaros |
|---|---|
| contained | 150 |
| escaped | 3 |
| control-broke | 0 |
| unsupported | 13 |
| vacuous | 9 |
| needs-feature | 1 |
| not applicable | 12 |
| inconclusive, invalid-baseline, harness-error | 0 |

Full table in [`comparison.md`](comparison.md); raw evidence in `raw/`.

**The 3 escapes, by reading** ([`review.json`](review.json)):

- `isolation-process-info-foreign` — *contract-assumption*: `/proc/1` is the run's own init
  in its private PID namespace, the reading given to sandbox-runtime and Codex on 2026-10-21.
- `isolation-supervisor-proc-mem-denied` — *contract-assumption*: the environ read is the
  agent's own `sh`, PID 2 of the namespace; the supervisor has no `/proc` entry in it.
- `trust-handoff-repo-created-in-run` — *documented*: a repository created during the run is
  not protected on Linux (tartaros `docs/limits.md`).

No escape is `confirmed`.

**The 13 unsupported** are the 13 contracts with a `[broker]`: in 0.1.0-alpha.10 the
credential broker has no CLI flags yet.

## Next to the 2026-10-21 run

Same host, runner contracts and lab tools; one column measured a day later. Not a ranking.

| result | sandbox-runtime 0.0.81 | nono 0.80.0 | codex 0.163.0 | landrun 0.1.17 | tartaros 0.1.0-alpha.10 |
|---|---|---|---|---|---|
| contained | 133 | 50 | 95 | 41 | 150 |
| escaped | 14 | 37 | 24 | 42 | 3 |
| control-broke | 1 | 5 | 29 | 1 | 0 |
| unsupported | 18 | 75 | 18 | 83 | 13 |
