# landrun

A thin, pure-Landlock CLI sandbox: it wraps a command with Landlock filesystem
and TCP rules and nothing else — no namespaces, no seccomp, no proxy. Landlock
is allow-only, so landrun is a capability sandbox like nono, but much smaller.

- Measured: **0.1.17** (release binary `landrun-linux-amd64`), `github.com/Zouuup/landrun`, MIT.
- Adapter: [`runner/adapters/landrun.py`](../runner/adapters/landrun.py) — builds the
  Landlock grants and runs `landrun --best-effort <grants> -- /bin/sh -c <cmd>`.
  `--best-effort` is needed because landrun targets Landlock ABI v9 by default and
  this host is ABI 4 (kernel 6.8).

## How `[policy]` maps

| neutral field | landrun flag |
|---|---|
| `writable_roots` | `--rwx <path>` (read, write, execute) |
| `read_allows` | `--ro <path>` |
| (system paths, so `sh`/`python3`/`curl` run) | `--rox /usr /bin /sbin /lib /lib64`, `--ro /etc /dev /proc`, `--rwx /dev/null` |
| read everywhere (the neutral default) | `--ro /` |
| `local_ports` | `--connect-tcp <port>` |
| no network field | no TCP rule → all TCP connect/bind denied (Landlock net, ABI 4) |
| environment | landrun passes nothing unless named, so `--env` is the scrub: core vars (and `env_passthrough`) are passed; `inherit_env` passes them all |

Fields landrun cannot express (reported `unsupported`):

- `read_denies` / `write_denies` — Landlock is allow-only; a deny carved out of a readable or writable area cannot be stated (same gap as nono).
- `read_scope = "granted"` — expressible since 2026-10-17 (SC-003): grant the workspace and nothing else; Landlock needs no grant on a path's ancestors. Until then the adapter wrongly reported it `unsupported`.
- `allow_domains` (no egress proxy), `isolate_pids` / `harden_syscalls` (no namespaces or seccomp), `materialize_absent_handoff`, `max_processes`, `[broker]`.

On this host (Landlock ABI 4) landrun's abstract-socket and signal scoping (ABI
v6) is unavailable, so those guarantees are not enforced; its network rules cover
TCP only, so UDP, netlink and other socket families are not blocked.

## Results (2026-10-15, Linux 6.8, [four-sandbox run](../results/2026-10-15-four-sandboxes/README.md))

> **Re-measured on 2026-10-17** in the granted read model ([run](../results/2026-10-17-landrun/README.md)): 22 contracts that were `unsupported` are now measured (17 contained, 4 escaped, 1 vacuous).
>
> **Re-measured on 2026-10-16** with the runner that implements [`spec/verdicts.md`](../spec/verdicts.md)
> ([run](../results/2026-10-16/README.md)). Same version, same kernel; one result changed: `filesystem-writable-root-replace` is now **contained** (its `control-broke` was a fault of the contract). Every
> other result below is unchanged.


| contained | escaped | control-broke | unsupported | vacuous | needs-feature | n/a |
|---|---|---|---|---|---|---|
| 22 | 38 | 2 | 104 | 6 | 2 | 12 |

landrun holds filesystem path confinement (write/symlink/hardlink/rename/unlink
outside the workspace), TCP egress and bind denial, `no_new_privs`, and the
environment scrub (it passes no variable unless named with `--env`). Of 38
escapes, **25 are built-in guarantees it does not provide** (no name-based
trust-handoff protection, no namespaces or seccomp for process isolation and
lifecycle), **8 are Landlock limits** (TCP-only network; abstract-socket and
signal scoping need ABI 6, not this host's ABI 4), and **5 are confirmed**:
`chmod`/`utime`/`xattr` on a readable file outside the roots, and a writable root
that is a symlink pointing out — the same two gaps nono has. The 109 unsupported
are the cost of being allow-only: every read/write-deny contract and the
by-omission variants. Full notes in the run's `review.json`.
