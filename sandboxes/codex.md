# codex (`codex sandbox`)

The Linux sandbox in OpenAI's Codex CLI. It uses bubblewrap for filesystem,
PID, IPC and network namespaces, sets `no_new_privs`, and applies a seccomp
filter that blocks io_uring and ptrace, plus network system calls when the
network is restricted.

We measured codex-cli 0.162.1 (`@openai/codex`), built from commit
`092d3acd6bec3e3a14bdc7e7a2810ab628ab759d` (tag rust-v0.162.1), and on
2026-10-21 codex-cli 0.163.0 (commit `83086188ae0614bd882818ff1aa23f3194962012`,
tag rust-v0.163.0), licensed Apache-2.0. Which results changed in which
version: [`results/versions.md`](../results/versions.md). We called its native `x86_64-unknown-linux-musl` binary directly
instead of the npm launcher. That launcher is a Node script, and a contract
that sets `NODE_OPTIONS` in the environment would break the launcher before the
sandbox ever started. The adapter is [`runner/adapters/codex.py`](../runner/adapters/codex.py).
It writes a named permissions profile to a temporary `$CODEX_HOME/config.toml`
and runs `codex sandbox -P conformance -C <workspace> -- sh -c <cmd>`.

## Configuration

| contract field | permissions profile |
|---|---|
| read access to everything not denied (the contracts' default) | `":root" = "read"` |
| `writable_roots` | `"<path>" = "write"` |
| `write_denies` | `"<path>" = "read"`. When entries overlap, the most specific path wins |
| `read_denies`, `glob_read_denies` | `"<path>" = "deny"` |
| `read_allows` | `"<path>" = "read"` |
| no network field | `network.enabled = false` |
| `allow_domains` | the experimental `features.network_proxy`, plus `network.domains` |
| environment allowlist, `env_passthrough` | `shell_environment_policy` with `include_only` set to PATH, HOME, LANG and TERM, plus any passed-through variables, and `ignore_default_excludes = false` |
| `inherit_env` | `shell_environment_policy.inherit = "all"` |
| `isolate_process_info`, `isolate_pids` | always on: `--unshare-pid` with its own `/proc` |
| `harden_syscalls`, `strict` | codex has no separate mode for these, so they are measured against its default filter |

Some fields have no equivalent in codex:

- `local_ports`. The network can be on, off, or proxied by domain, but codex cannot open a single loopback port.
- `max_processes`.
- `materialize_absent_handoff`.
- `[broker]`.
- A log of its own that the agent could try to tamper with.

## Results of 0.163.0 (2026-10-21 run)

No result changed from 0.162.1: the [run](../results/2026-10-21/README.md)
re-measured 0.162.1 on the same host, runner and contracts first, and both
versions give the same result on all 188 contracts. Everything below holds for
0.163.0.

## Results of the 2026-10-15 run

> **Re-measured on 2026-10-16** with the runner that implements [`spec/verdicts.md`](../spec/verdicts.md)
> ([run](../results/2026-10-16/README.md)). Same version, same kernel; one result changed: `filesystem-writable-root-replace` is now **contained** (its `control-broke` was a fault of the contract). Every
> other result below is unchanged.


Linux 6.8. Method and host details are in [the run's README](../results/2026-10-15/README.md).

| contained | escaped | control-broke | unsupported | vacuous | needs-feature | n/a |
|---|---|---|---|---|---|---|
| 74 | 24 | 27 | 18 | 8 | 1 | 12 |

codex was set up as strictly as its documentation allows. Of the escapes, three
broke a rule we had configured.

### Escapes on configured rules

**A writable root inside a write-denied directory stays writable**
(`write-deny-covers-nested-root`). codex settles overlapping entries by taking
the most specific one, so the nested root wins over the deny that covers it.

**A writable root that is a symlink is followed** (`fs-writable-root-symlink-out`,
`fs-writable-root-symlink-parent`). If a writable root is a symlink pointing
outside the other roots, its target becomes writable. The contract expects the
sandbox to refuse such a root. codex accepts it.

### Escapes with a note

- `secrets-env-loader-injection-inherit`: the policy asked to inherit the whole environment, and codex did. The contract's own comment calls stripping `LD_PRELOAD` in that case a design decision still to be made.

### Escapes on defaults

20 escapes concern behaviour no `[policy]` field asks for:

- Trust handoff (13). codex makes `.git`, `.codex`, `.agents` and `.aws` read-only at the top of each writable root. In these contracts the repository sits one level below the root, the way it would in a workspace that holds several repositories, and the protection does not reach that far.
- Isolation (5).
  - The agent could create nested user namespaces (3 contracts).
  - The agent could open an ancestor's `/proc/<pid>/mem` or `environ`.
  - `/proc/1` is readable. It belongs to the sandbox's own init, not to a host process.
- Lifecycle (2).
  - `.mcp.json` is not on codex's list of protected files.
  - After we sent SIGTERM to `codex sandbox`, the processes inside kept running and wrote the marker file.

### Other results

codex had 27 `control-broke` results, more than either of the other two. In
21 of them, codex refused to build the sandbox and ran nothing. That happened
when an entry was a symlink, went through one, named a path that did not
exist, was a single file, or contained glob characters such as
`[WIP] project`. The errors were `cannot enforce sandbox read-only path…` and
`bwrap: Can't mount tmpfs…`. The attack was stopped, but so was the legitimate
work, and in practice the user would get an error instead of a sandbox. The
other 6 failed in different ways:

- In two contracts, a read-allow inside a read-deny stayed unreadable.
- Three controls need system calls or socket families that codex's filter blocks.
- One contract replaces a writable root during the run.

`needs-feature` (1): `isolation-nested-relaunch-no-widen` assumes a launcher
with a `run --write DIR` command line, which codex does not have.
