# sandbox-runtime (`srt`)

Anthropic's sandbox runtime. On Linux it relies on bubblewrap for filesystem,
PID and network namespaces. A seccomp filter blocks AF_UNIX socket creation
and io_uring, and HTTP and SOCKS proxies on the host decide which domains can
be reached.

I measured version 0.0.79 (`@anthropic-ai/sandbox-runtime`), built from
commit `d9aac2098351ca17f3743fbaf6ecbd0051b7e00e` (tag v0.0.79), and on
2026-10-21 version 0.0.81 (commit `c40cf14a65d025e3cd27f071f13a73c12b3b1f92`,
tag v0.0.81), licensed Apache-2.0. The adapter is
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

## Results

sandbox-runtime: findings reported to the vendor; its results will be published once they are fixed.
