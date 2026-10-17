# sandbox-runtime (`srt`)

Anthropic's sandbox runtime. On Linux it relies on bubblewrap for filesystem,
PID and network namespaces. A seccomp filter blocks AF_UNIX socket creation
and io_uring, and HTTP and SOCKS proxies on the host decide which domains can
be reached.

We measured version 0.0.79 (`@anthropic-ai/sandbox-runtime`), built from
commit `d9aac2098351ca17f3743fbaf6ecbd0051b7e00e` (tag v0.0.79), licensed
Apache-2.0. The adapter is
[`runner/adapters/sandbox_runtime.py`](../runner/adapters/sandbox_runtime.py).
It writes a settings file and runs `srt --settings <file> -c <cmd>`.

## Configuration

| contract field | srt setting |
|---|---|
| `writable_roots` | `filesystem.allowWrite` |
| `write_denies` | `filesystem.denyWrite` |
| `read_denies`, `glob_read_denies` | `filesystem.denyRead` |
| `read_allows` | `filesystem.allowRead` |
| `local_ports` | `network.allowedDomains` with `127.0.0.1:<port>` and `localhost:<port>`, reachable through srt's proxy |
| `allow_domains` | `network.allowedDomains` |
| no network field | `network.allowedDomains: []`, so no egress |
| `isolate_process_info`, `isolate_pids` | always on: a private PID namespace with its own `/proc` |
| `harden_syscalls`, `strict` | srt has no separate mode for these, so they are measured against its default filter |
| `materialize_absent_handoff` | always on: protected paths that do not exist yet are covered by a mount |
| `inherit_env` | srt's default, which passes the environment through |

Some fields have no equivalent in srt:

- An environment allowlist (`env_passthrough`, or a `launcher_env` without `inherit_env`). srt passes the environment through and can only deny variables by name.
- `max_processes`.
- `[broker]`. srt injects credentials through its MITM proxy, which works differently from the broker the contracts describe.
- A log of its own that the agent could try to tamper with.

The adapter passes paths exactly as the contract spells them, with trailing
slashes, brackets, `..` and symlinks left in. How a sandbox reads those
spellings is part of what is under test.

## Results of the 2026-10-15 run

> **Re-measured on 2026-10-16** with the runner that implements [`spec/verdicts.md`](../spec/verdicts.md)
> ([run](../results/2026-10-16/README.md)). Same version, same kernel; two results changed: `network-tcp-external-denied` is now **contained** (the contract now uses a witness server and the effect decides, instead of reading ENETUNREACH as an escape), and `filesystem-writable-root-replace` is now **contained** (its `control-broke` was a fault of the contract). Every
> other result below is unchanged.


Linux 6.8. Method and host details are in [the run's README](../results/2026-10-15/README.md).

| contained | escaped | control-broke | unsupported | vacuous | needs-feature | n/a |
|---|---|---|---|---|---|---|
| 99 | 22 | 4 | 18 | 8 | 1 | 12 |

srt was set up as strictly as its documentation allows. Out of 22 escapes, 5
broke a rule we had configured.

### Escapes on configured rules

**A read-deny written through a symlink with `..` protects the wrong file**
(`read-deny-link-dotdot`). The deny names `here/up`, a symlink to
`link/../file`, where `here/link` points to `../elsewhere/in`. Following the
links, `here/up` is `elsewhere/file`. srt removes the `..` from the text
instead, and ends up at `here/file`. So it blocked `here/file`, the file the
control needed, and the attack read `elsewhere/file`. The output was
`TOPSECRET`.

**Writing through a write-denied dangling link creates its target**
(`write-deny-dangling-link-target`). The deny covers `here/new`, a symlink
whose target does not exist yet. Appending to `here/new` created
`elsewhere/made`.

**Some socket families can still be opened** (`network-other-socket-families-denied`,
`network-vsock-denied`, `network-socket-domain-high-bits`). The agent could
create AF_NETLINK and AF_VSOCK sockets, and sockets with high bits set in the
domain argument. Inside srt's empty network namespace, netlink only sees that
namespace. AF_VSOCK is not tied to a network namespace. We did not check
whether it reaches anything on this host (por confirmar).

### Escapes with a note

- `network-tcp-external-denied`: the contract treats any error other than EPERM as a successful attack. Under srt the process has no network interface at all and gets ENETUNREACH. Nothing leaves the host.
- `network-local-bind-denied`: the agent can open a listening socket, but it lives inside srt's own empty network namespace, where nothing on the host can reach it.
- `secrets-env-loader-injection-inherit`: the policy asked to inherit the whole environment, and srt did. The contract's own comment calls stripping `LD_PRELOAD` in that case a design decision still to be made.

### Escapes on defaults

14 escapes concern behaviour no `[policy]` field asks for:

- Isolation (7).
  - srt's filter covers AF_UNIX and io_uring, not namespace creation, so the agent could create nested user and mount namespaces (3 contracts).
  - The PID 1 of the agent's namespace runs without seccomp. srt documents it as a reaper that cannot be ptraced.
  - The agent could open an AF_VSOCK socket.
  - When srt is launched as root, the command keeps its effective capabilities.
  - `/proc/1` is readable. It belongs to the sandbox's own init, not to a host process.
- Trust handoff (7). srt protects a fixed list of files (`.git/hooks`, `.git/config`, `.claude/commands`, shell rc files, among others), found by a scan of limited depth. The contracts that got through used:
  - a `gitdir:` pointer;
  - a worktree gitfile;
  - a repository created during the run;
  - a nested repository listed in `.gitignore`;
  - a hooks directory given as a writable root;
  - a symlinked `.claude`;
  - a symlink cycle.

### Other results

`control-broke` (4):

- `write-deny-link-dotdot`: srt hung until our 60-second timeout when a write-deny was spelled with `..` through symlinks.
- `read-deny-bracket-dir`: srt quit before running anything because a directory named `[user-id]` produced an invalid regular expression.
- A loopback port allowed by the policy is reachable only through srt's proxy. With `curl --noproxy ''` we got HTTP 200. The contract's control connects directly, and srt sets `NO_PROXY=127.0.0.1`, so the direct connection fails.
- One contract replaces a writable root during the run.

We also saw something the counts do not include. srt finds the files it
protects by scanning from the working directory. With the working directory
one level above the writable root, `.git/config` inside the root could be
written. With the working directory inside the root, it was protected. That is
why the run starts every command inside the writable root.

`needs-feature` (1): `isolation-nested-relaunch-no-widen` assumes a launcher
with a `run --write DIR` command line, which srt does not have.

## Upstream status

Checked on 2026-10-15 against srt's public pull requests and commits. Most of
what this run found on configured rules was already fixed on `main` when we
measured, in changes merged after the v0.0.79 release. No release carries those
fixes yet, so the results above stay as measured until the next version is run.

| finding | fixed in | reference |
|---|---|---|
| read-deny through a symlink with `..` resolved lexically | `main` 48a08dc, no release yet | [#689](https://github.com/anthropics/sandbox-runtime/pull/689) |
| write through a denied dangling link creates its target | `main` 48a08dc, no release yet | [#689](https://github.com/anthropics/sandbox-runtime/pull/689) |
| hang on a write-deny spelled with `..` | probably `main` 48a08dc (por confirmar) | [#689](https://github.com/anthropics/sandbox-runtime/pull/689) |
| `[user-id]` directory stops the sandbox from starting | `main` 80ea0c9, no release yet | [#687](https://github.com/anthropics/sandbox-runtime/pull/687) |
| AF_VSOCK sockets can be created | `main` 5507fb0, no release yet | [#691](https://github.com/anthropics/sandbox-runtime/pull/691) |
| AF_NETLINK sockets can be created | not planned (documented deny list) | [#691](https://github.com/anthropics/sandbox-runtime/pull/691) |
| protected names scanned from the working directory | open | [#518](https://github.com/anthropics/sandbox-runtime/pull/518), [#569](https://github.com/anthropics/sandbox-runtime/pull/569) |
| nested repositories, gitdir pointers, worktree gitfiles | open | [#569](https://github.com/anthropics/sandbox-runtime/pull/569) |
| symlinked `.claude` directory | open | [#531](https://github.com/anthropics/sandbox-runtime/pull/531) |

The full table, with the contracts behind each row, is at the end of
[`comparison.md`](../results/2026-10-15/comparison.md).
