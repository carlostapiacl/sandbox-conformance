# Four-sandbox run of 2026-10-15

This run adds a fourth sandbox, **landrun** (pure Landlock), alongside the three
from the [2026-10-15 run](../2026-10-15/README.md), and measures all four against
the current full contract set: the 166 harvested guarantees plus the 22
by-omission variants. It is the same host, image and container options as the
2026-10-15 run; the three earlier sandboxes are re-measured here so the four
columns come from one run.

| sandbox | version | source commit | license |
|---|---|---|---|
| [sandbox-runtime](../../sandboxes/sandbox-runtime.md) | 0.0.79 | `d9aac20` (tag v0.0.79) | Apache-2.0 |
| [nono](../../sandboxes/nono.md) | 0.80.0 | `8bb0413` (tag v0.80.0) | Apache-2.0 |
| [codex](../../sandboxes/codex.md) | codex-cli 0.162.1 | `092d3ac` (tag rust-v0.162.1) | Apache-2.0 |
| [landrun](../../sandboxes/landrun.md) | 0.1.17 | `github.com/Zouuup/landrun` (release binary) | MIT |

## Results

| result | sandbox-runtime | nono | codex | landrun |
|---|---|---|---|---|
| contained | reported | 48 | 92 | 22 |
| escaped | reported | 37 | 24 | 38 |
| control-broke | reported | 6 | 30 | 2 |
| unsupported | reported | 74 | 18 | 104 |
| vacuous | reported | 8 | 9 | 6 |
| needs-feature | reported | 1 | 1 | 2 |
| not applicable | reported | 12 | 12 | 12 |

sandbox-runtime: findings reported to the vendor; its results will be published once they are fixed.

These counts are not a ranking. The full table is in [`comparison.md`](comparison.md);
every non-contained result was checked against the raw output and the notes are
in `review.json`.

## landrun — the pure-Landlock floor

landrun is the thinnest of the four: it wraps a command with Landlock filesystem
and TCP rules and nothing else. That shape shows clearly.

What it **holds** (22 contained): path confinement (write outside the workspace,
symlinks and hardlinks out, rename, unlink, truncate, `/dev/shm`), TCP egress and
bind denial, `no_new_privs`, and — notably — the **environment scrub** contracts.
Because landrun passes no environment variable unless named (`--env`), a launcher
secret never reaches the command, so it contains `secrets-env-scrub-common-tokens`,
`secrets-env-passthrough-selective` and `secrets-env-loader-injection-scrub` where
a read-everything-then-deny sandbox has to work harder.

Its **109 unsupported** are the honest cost of being allow-only: every
`read_denies` / `write_denies` contract (Landlock cannot carve a deny out of a
granted area, the same gap as nono) and the 22 by-omission variants (landrun's
grants are recursive and it needs an ancestor of the workspace granted to reach
it, which would expose the omitted secret — see its page).

Its **38 escapes** split into:

- **25 on built-in guarantees landrun does not provide.** It has no name-based protection, so all 17 trust-handoff contracts (planting `.git/config`, `.claude`, hooks, rc files inside the writable workspace) escape; and with no namespaces or seccomp, the 5 isolation and 3 lifecycle guarantees (process info, io_uring, signals, vsock, proc-mem, process teardown) are not enforced. These are differences of defaults — landrun is a filesystem/network tool, not a process isolator.
- **8 annotated**: Landlock mediates TCP only, so UDP / ICMP / netlink / AF_VSOCK / high-bit socket domains and io_uring are not blocked (6 network contracts); abstract-socket and signal scoping need Landlock ABI 6, not this host's ABI 4 (1 ipc); and one contract asked to inherit the whole environment.
- **5 confirmed on configured rules**: Landlock does not mediate `chmod` / `utime` / `xattr` on a readable file outside the roots (3), and a writable root that is a symlink pointing out is followed (2) — the same two gaps nono has.

`control-broke` (2): a writable root replaced during the run, and a writable root
spelled with `..` that landrun refuses to turn into a Landlock ruleset.

## Reading the four together

- **codex** fails closed (30 control-broke): it refuses to build the sandbox for symlinked / absent / glob deny paths rather than enforce them loosely.
- **nono** and **landrun** are both allow-only (Landlock), so they show many `unsupported` in the neutral read model; nono adds a credential proxy, process and network machinery on top, so it holds more than bare landrun. The [by-omission run](../2026-10-15-by-omission/README.md) measures nono's read model where this neutral model only returns `unsupported`.

## Limits of this run

- One OS, one kernel: Linux 6.8, Landlock ABI 4. landrun ran with `--best-effort` (it targets ABI v9 by default).
- A `vacuous` result proves nothing in either direction.
- The by-omission variants are mixed into this set; landrun reports them `unsupported`. Their fair measurement is the separate by-omission run.
