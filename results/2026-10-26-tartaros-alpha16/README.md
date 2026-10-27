# Run of 2026-10-26: TartarOS 0.1.0-alpha.16, the masked-credential contracts

TartarOS on the whole corpus, and sandbox-runtime on the six new contracts only, on the host
of the [2026-10-21 run](../2026-10-21/README.md).

> **Conflict of interest.** TartarOS is maintained by the author of this lab, and the six
> `credentials-masked-env-*` contracts were written while masked credentials were being added
> to TartarOS ([`contracts/CHANGES.md`](../../contracts/CHANGES.md), 2026-10-26). They were
> derived from sandbox-runtime's own tests and frozen before either sandbox was measured. The
> result files record the conflict (`conflict_of_interest`).

| | |
|---|---|
| sandboxes | [tartaros](../../sandboxes/tartaros.md) **0.1.0-alpha.16**, tagged commit `f245b8fd`, built in the lab image; sandbox-runtime **0.0.81** |
| adapters | `runner/adapters/tartaros.py` SHA-256 `d561d1a16352…`, `runner/adapters/sandbox_runtime.py` `42aabe8a1d41…` (both map `[[masked_env]]` since this run) |
| runner and contracts | commit `0ee6c21` |
| host | Ubuntu 24.04.5, kernel 6.8.0-146-generic, Landlock ABI 4 ([`runner/lima/`](../../runner/lima/README.md)) |
| network | the witness network (`SC_WITNESS=1`, [`runner/lab-witness.sh`](../../runner/lab-witness.sh)): the runner's container on TEST-NET-2, the witness host beside it |
| profile | `strict` (spec §7) |

## Results

| result | tartaros 0.1.0-alpha.16 (whole corpus) | sandbox-runtime 0.0.81 (six contracts) |
|---|---|---|
| contained | 168 | 6 |
| escaped | 3 | 0 |
| control-broke | 0 | 0 |
| unsupported | 0 | 0 |
| vacuous | 10 | 0 |
| needs-feature | 1 | 0 |
| not applicable | 12 | 0 |

Full table in [`comparison.md`](comparison.md); raw evidence in `raw/`.

**What changed against 0.1.0-alpha.11.** Only the six new contracts, all **contained**:
the agent holds a sentinel, the real value reaches only the credential's own hosts, over TLS
and not plain HTTP, one credential's sentinel is not swapped on another's host, the body is
swapped only toward that host, and no process record the agent can read holds the value.
Every other result is the same as in alpha.11, contract by contract.

**sandbox-runtime holds the same six on Linux.** On this host the two are at parity for
masked credentials. Neither run measures macOS, where sandbox-runtime does not mask yet
([sandbox-runtime#593](https://github.com/anthropics/sandbox-runtime/pull/593)).

**How the baselines were checked.** Before counting, the six attacks were run with no
sandbox (all six got through) and under a sandbox that denies all network (all six controls
broke): the attacks and the controls both test something.

**The 3 escapes** are the same as in alpha.10 and alpha.11, with the same readings
([`review.json`](review.json)): two contract assumptions and one documented limit. No escape
is `confirmed`.
