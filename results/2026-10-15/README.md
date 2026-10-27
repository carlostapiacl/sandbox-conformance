# Run of 2026-10-15

This is the lab's first measured run. I took the 168 contracts in `contracts/`
and ran them against three sandboxes on a single Linux host. I did not run
anything on macOS or Windows.

| sandbox | version | source commit | license |
|---|---|---|---|
| [sandbox-runtime](../../sandboxes/sandbox-runtime.md) | 0.0.79 (`@anthropic-ai/sandbox-runtime`) | `d9aac2098351ca17f3743fbaf6ecbd0051b7e00e` (tag v0.0.79) | Apache-2.0 |
| [nono](../../sandboxes/nono.md) | 0.80.0 (release binary, checked against SHA256SUMS) | `8bb041356d48f771a221e58c98d9b1ff442e76fe` (tag v0.80.0) | Apache-2.0 |
| [codex](../../sandboxes/codex.md) | codex-cli 0.162.1 (`@openai/codex`, native binary) | `092d3acd6bec3e3a14bdc7e7a2810ab628ab759d` (tag rust-v0.162.1) | Apache-2.0 |

## Results

| result | sandbox-runtime | nono | codex |
|---|---|---|---|
| contained | reported | 31 | 74 |
| escaped | reported | 33 | 24 |
| control-broke | reported | 6 | 27 |
| unsupported (capability gap) | reported | 78 | 18 |
| vacuous | reported | 7 | 8 |
| needs-feature | reported | 1 | 1 |
| not applicable (macOS-only) | reported | 10 | 10 |
| not applicable (host has no GPU or cgroup delegation) | reported | 2 | 2 |

sandbox-runtime: findings reported to the vendor; its results will be published once they are fixed.

The escape totals mix two kinds of result. Some contracts test a rule the
adapter configured, such as a read-deny or a write-deny. Others test something
no `[policy]` field asks for, such as protecting `.git/hooks` inside a writable
root, or tearing down the process tree when the launcher is killed. For the
second kind I am measuring the sandbox's defaults. An escape there tells you
how the sandbox behaves out of the box. It does not mean a configured rule
failed.

I went through every result other than `contained` by hand and compared it
with the raw output. Some escapes turned out to rest on an assumption the
contract makes that does not fit the sandbox's design. Others depend on a newer
kernel, or match a limitation the sandbox already documents. Those notes are in
`review.json` and at the end of `comparison.md`. They explain results; none of
them changes one.

| escaped | sandbox-runtime | nono 33 | codex 24 |
|---|---|---|---|
| on a default (no `[policy]` field asks for it) | reported | 27 | 20 |
| on a configured rule, with a note (not a breach, kernel, or documented) | reported | 1 | 1 |
| on a configured rule, confirmed | reported | 5 | 3 |

Some codex results are held while a coordinated-disclosure process is open; they are not shown and will be published when the vendor authorizes it.

## Files

- `<sandbox>.json`: sandbox, version, commit, license, host, time of the run, counts, and one entry per contract with its result, the reason, how it was judged and the review note, if any.
- `raw/<sandbox>.full.json`: everything the runner captured. For each contract, both passes (with and without the sandbox), the argv, exit codes, stdout and stderr (cut at 4000 characters) and the effect evidence.
- `comparison.md`: contract by sandbox, measured results only.
- `review.json`: the manual notes.
- `upstream.json`: where each finding stands in the sandbox's own project, and the version or commit that fixes it.

## Host

I ran everything on a disposable Linux lab host, inside Docker containers
started with `--rm`. Nothing ran on a workstation.

| | |
|---|---|
| kernel | 6.8.0-146-generic, x86_64 |
| OS | Ubuntu 24.04.5 LTS |
| Landlock ABI | 4 (no ioctl-dev from ABI 5, no signal or abstract-socket scoping from ABI 6) |
| bubblewrap | 0.9.0 (Ubuntu package) |
| container | Docker 29.8.2, `--init --cpus 1 --memory 1g --pids-limit 512 --security-opt seccomp=unconfined --security-opt apparmor=sc-lab --security-opt systempaths=unconfined` |
| agent user | uid 1500, not root (contracts that require root ran as root inside the container) |

The container options are there for two reasons. The sandboxes need user
namespaces and fresh `/proc` mounts, and Docker's default seccomp and AppArmor
profiles block both. Those profiles would also act as a second wall, and a
containment could end up credited to Docker instead of the sandbox under test.
`sc-lab` is an AppArmor profile whose only rule is `userns`, which Ubuntu 24.04
otherwise restricts for unprivileged users. I loaded it into the kernel for
the run and removed it afterwards. I changed no host sysctl. The exact setup
is in `runner/lab.sh`, `runner/Dockerfile` and `runner/sc-lab.apparmor`.

## Method

For each contract that applies to Linux, `runner/run.py` does the following:

1. Baseline. Create a fresh `{root}` and the fixtures, then run the attack and the control with no sandbox, in the same container and as the same user. If the attack fails here, the contract is `vacuous` and proves nothing.
2. Sandboxed run. Create a fresh `{root}` and the fixtures again, run the attack and then the control through the adapter, and check the `[assert]`.
3. The baseline tells the lab how to recognise a successful attack. If the `[assert]` caught its effect on disk, I judge by that effect; otherwise I judge by the exit status. A read attack is the usual case for the second: the file it reads stays `unchanged`, so only the exit status shows that the read worked. Under the sandbox, any real effect counts as an escape. When an attack sets `expect_exit` and has no `[assert]`, the contract is checking that the sandbox reports the right status, and any other status is the failure.
4. Commands run from the first writable root, which is where an agent would be working.

Each adapter (`runner/adapters/`) translates the neutral `[policy]` into its
sandbox's own configuration, in the way that sandbox's documentation suggests
for strict confinement. Adapters never read the attack. When a sandbox has no
way to express a field, the result is `unsupported`: a feature it lacks, not a
vulnerability. The runner itself provides the pieces some contracts need
outside the sandbox (`[[server]]`, `[[unix_server]]`, `[[abstract_server]]`,
`launcher_env`, `[[late_fixture]]`, `[[canary_process]]`, `[[host_process]]`,
`[signal]`). None of the three sandboxes has a credential broker with the
interface the `[broker]` contracts use, so those contracts are `unsupported`
for all three.

## Limits of this run

- One OS and one kernel: Linux 6.8, Landlock ABI 4. Two nono results (marked `§`) would need ABI 6.
- A `vacuous` contract says nothing in either direction. Most of mine are written for a launcher running as root, or for attacks that file permissions already stop for a non-root user.
- I did not check whether `AF_VSOCK` reaches anything from inside these containers on this host (por confirmar).
- nono was measured against the neutral model, where everything not denied is readable, and not against its own model of granting only what is needed. Its page explains the difference.
