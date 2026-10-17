# Run of 2026-10-16: the first run judged by spec/verdicts.md

The same four sandboxes and versions as the [2026-10-15 four-sandbox run](../2026-10-15-four-sandboxes/README.md),
measured with the runner that implements [`spec/verdicts.md`](../../spec/verdicts.md)
(v1.0.0-draft) and the contracts it corrected. To tell what the new runner changed from what
the new host changed, the old runner was run first on the same host (`v0-rerun/`).

| sandbox | version | adapter (SHA-256, first 12) |
|---|---|---|
| [sandbox-runtime](../../sandboxes/sandbox-runtime.md) | 0.0.79 | `b05eb81ccdb4` |
| [nono](../../sandboxes/nono.md) | 0.80.0 | `8c677ae09815` |
| [codex](../../sandboxes/codex.md) | codex-cli 0.162.1 | `b861823045fb` |
| [landrun](../../sandboxes/landrun.md) | 0.1.17 | `ae7e9e40d59a` |

Runner and contracts: commit `b836325` (recorded in every file as `runner_commit`). Spec
version `1.0.0-draft`, profile `strict` (§7). The old runner of `v0-rerun/`: commit `c3024a9`,
the code of the 2026-10-15 runs.

## Results

| result | sandbox-runtime | nono | codex | landrun |
|---|---|---|---|---|
| contained | 124 | 50 | 95 | 24 |
| escaped | 21 | 37 | 24 | 38 |
| control-broke | 3 | 5 | 29 | 1 |
| unsupported | 18 | 75 | 18 | 105 |
| vacuous | 9 | 8 | 9 | 6 |
| needs-feature | 1 | 1 | 1 | 2 |
| not applicable | 12 | 12 | 12 | 12 |
| inconclusive, invalid-baseline, harness-error | 0 | 0 | 0 | 0 |

These counts are not a ranking (§8). Every escape has a reading (`comparison.md`, "Escapes by
reading"): `confirmed` counts guarantees a sandbox **claims** and did not hold, so a sandbox that
claims more can show more of them; `design` counts guarantees it never claimed. The full table and the review notes are in
[`comparison.md`](comparison.md). No case was `inconclusive`, and the lab reported no fault
of its own.

## What changed, and why

**Reproduction first.** With the old runner, this host gives the same result as the
2026-10-15 run for every contract both runs measured, in all four sandboxes (744 of 744
comparable cells). The only additions are the
two OpenHands contracts, which the 2026-10-15 run did not include. So any difference below
comes from the runner and the contracts, not from the host.

**Then the new runner: 5 results change, each traced to a cause.**

| contract | sandbox | 2026-10-15 | 2026-10-16 | cause |
|---|---|---|---|---|
| `filesystem-writable-root-replace` | all four | control-broke | contained | the contract's control wrote below `work/src`, which the attack may legitimately empty; the control now writes to the writable root itself. The 2026-10-15 `control-broke` results were a fault of the contract. |
| `network-tcp-external-denied` | sandbox-runtime | escaped (‡) | contained | the contract decided by errno and read "no network interface" (ENETUNREACH) as an escape; it now uses a witness server on the host's own address, and the witness received nothing. |

Contracts that changed without changing a result:

- `isolation-clone-newns-denied`: its script turned a child killed by a signal into a
  success. With that fixed, sandbox-runtime, nono and codex still escape: those three
  2026-10-15 results are confirmed.
- 26 Python attacks now exit 3 when blocked and declare `blocked_exit = [3]`, so a crash
  cannot read as a block. No result changed: none of them crashed.
- `isolation-nested-relaunch-no-widen` gained a missing fixture;
  `network-proxy-env-present` declares `control_requires_sandbox`. Their results are
  unchanged, now with a valid baseline.

## Host

A disposable virtual machine, used only for this run and deleted after it: Ubuntu 24.04.5 LTS,
kernel `6.8.0-146-generic` (the same kernel as the 2026-10-15 runs), x86_64, Landlock ABI 4,
AppArmor on, nothing mounted from the machine that ran it. Inside it, each sandbox ran in a
`--rm` Docker container (docker 29.1.3; the 2026-10-15 runs used 29.8.2) started by
[`runner/lab.sh`](../../runner/lab.sh) with `--init --cpus 1 --memory 1g --pids-limit 512
--security-opt seccomp=unconfined --security-opt apparmor=sc-lab --security-opt
systempaths=unconfined`, from the `sc-lab:tools` image built from
[`runner/Dockerfile`](../../runner/Dockerfile). Every file records the host it ran on.

## Files

- `<sandbox>.json`: one line per contract, no raw output, with its review note when it has one.
- `raw/<sandbox>.full.json`: everything the runner captured, per phase.
- `v0-rerun/<sandbox>.full.json`: the old runner on this host, the reproduction above.
- `comparison.md`: contract by sandbox, measured results only.
- `review.json`: the readings (§6), carried over from the 2026-10-15 four-sandbox run only
  where the result is identical.
