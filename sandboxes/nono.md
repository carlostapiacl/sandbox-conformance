# nono

The sandbox from nolabs-ai. On Linux it combines Landlock, which covers the
filesystem and, from ABI 4, TCP, with a seccomp filter for networking,
`no_new_privs`, and a supervising parent process.

We measured version 0.80.0 from the release asset
`nono-v0.80.0-x86_64-unknown-linux-gnu.tar.gz`, after checking it against the
release's SHA256SUMS. The source commit is
`8bb041356d48f771a221e58c98d9b1ff442e76fe` (tag v0.80.0), and the license is
Apache-2.0. The adapter is [`runner/adapters/nono.py`](../runner/adapters/nono.py).
It writes a profile and runs
`nono -s run --no-diagnostics --no-rollback --no-audit --profile <file> -- sh -c <cmd>`.

## Configuration

| contract field | nono profile |
|---|---|
| (base) | the default groups, minus `system_write_linux`, `user_tools`, `homebrew_linux` and `dangerous_commands*`. Read on `/usr/local/bin`, write on `/dev/null`, `workdir.access: none` |
| read access to everything not denied (the contracts' default) | `filesystem.read` on the whole test tree, `{root}` |
| `writable_roots` | `filesystem.allow`, or `allow_file` for a single file |
| `read_allows` | `filesystem.read`, or `read_file` |
| `local_ports` | `network.block` plus `network.connect_port`. Landlock filters TCP by port only, so the grant is not limited to loopback |
| `allow_domains` | `network.allow_domain`, through nono's proxy |
| no network field | `network.block: true` |
| environment allowlist, `env_passthrough` | `environment.allow_vars` with PATH, HOME, LANG and TERM, plus any passed-through variables |
| `inherit_env` | no `allow_vars`. nono still removes loader variables such as `LD_PRELOAD` |
| `max_processes` | `--max-processes` |
| `isolate_process_info` | nothing to configure: nono only grants `/proc/self` and a few other `/proc` files. Its `process_info_mode` option exists on macOS only |
| `harden_syscalls`, `strict` | nono has no separate mode for these, so they are measured against its default filter |

Some fields have no equivalent in nono:

- A `read_denies` or `write_denies` that falls inside something granted. Landlock can only grant access, and nono refuses to start when a deny overlaps a grant.
- `isolate_pids`. nono does not create a PID namespace.
- `materialize_absent_handoff`.
- `[broker]` as the contracts define it. nono does have a credential proxy, but it uses its own routes.

Nearly all of nono's 78 `unsupported` results come from that first point. The
contracts assume a model where everything is readable unless denied. nono
works the other way round: you grant the workspace and nothing else, and a
secret stays protected because nobody granted it. In that setup most of these
secrets would never be readable. The contracts' `[policy]` does not describe
that setup, so we did not measure it in this run. A version of the read-deny
contracts written for that model would let us measure it.

## Measured in nono's own model (by-omission run)

The 2026-10-15 run below measured nono against the neutral model, where 58 of its
78 `unsupported` results came from `read_denies` / `write_denies` fields nono's
allow-only model does not express. The [by-omission run](../results/2026-10-15-by-omission/README.md)
re-states the 23 translatable read contracts in nono's own model
(`read_scope = "granted"`: grant the workspace, omit the secret) and measures all
three sandboxes. nono goes from 23 `unsupported` to **18 contained, 4 escaped, 1
vacuous**: it holds those read guarantees once they are asked in the model it
speaks. The 4 escapes (a Landlock unix-socket gap and three cases of a grant that
is a symlink into the protected area) and the 39 contracts that cannot be stated
in the granted model are detailed there.

## Results of the 2026-10-15 run

> **Re-measured on 2026-10-16** with the runner that implements [`spec/verdicts.md`](../spec/verdicts.md)
> ([run](../results/2026-10-16/README.md)). Same version, same kernel; one result changed: `filesystem-writable-root-replace` is now **contained** (its `control-broke` was a fault of the contract). Every
> other result below is unchanged.


Linux 6.8, Landlock ABI 4. Method and host details are in [the run's README](../results/2026-10-15/README.md).

| contained | escaped | control-broke | unsupported | vacuous | needs-feature | n/a |
|---|---|---|---|---|---|---|
| 31 | 33 | 6 | 74 | 7 | 1 | 12 |

nono was set up as strictly as its documentation allows. Out of 33 escapes, 5
broke a rule we had configured.

### Escapes on configured rules

**Metadata of a readable file can be changed** (`filesystem-chmod-outside`,
`filesystem-utime-outside`, `filesystem-xattr-outside`). With read access to
the test tree, the agent could change the mode, the timestamps and the
extended attributes of files outside its writable roots. Landlock does not
cover these operations. If nono had not granted read access to those files in
the first place, the agent could not have reached them.

**A writable root that is a symlink is followed** (`fs-writable-root-symlink-out`,
`fs-writable-root-symlink-parent`). If a writable root is a symlink pointing
outside the other roots, its target becomes writable. The contract expects the
sandbox to refuse such a root. nono accepts it.

### Escapes with a note

- `ipc-abstract-unix-socket` (`§`): limiting connections to abstract unix sockets requires Landlock ABI 6, which needs kernel 6.12 or newer. This host has ABI 4.

### Escapes on defaults

27 escapes concern behaviour no `[policy]` field asks for:

- Trust handoff (17). Inside a writable root, nono does not protect `.git/hooks`, `.git/config`, `.claude/`, editor directories or rc files.
- Isolation (7).
  - The agent could create nested user namespaces (3 contracts).
  - When nono is launched as root, the command keeps its capabilities.
  - `/proc/1` is readable, and so are an ancestor's `/proc/<pid>/mem` and `environ`.
  - On this kernel nothing stops the agent from signalling processes outside the sandbox (`isolation-signal-host-process`, `§`: needs Landlock ABI 6).
- Lifecycle (3).
  - A child process left in the background kept running after the command exited.
  - After we sent SIGTERM to the launcher, the processes inside the sandbox kept running and wrote the marker file.
  - `.mcp.json` is not protected.

These are differences of defaults. Of the three groups, the lifecycle results
deserve the closest look.

### Other results

`control-broke` (6):

- A writable root spelled `absent/../real`. nono requires every granted path to exist.
- A writable root that is replaced during the run.
- The nested relaunch: the inner nono could not start.
- Three controls that need system calls nono's network filter blocks: io_uring, an unusual socket domain, and multiprocessing IPC.

`needs-feature` (1): `lifecycle-effect-log-tamper`. nono keeps an audit trail,
but we did not connect the adapter to the place where a run's log is stored
(por confirmar).
