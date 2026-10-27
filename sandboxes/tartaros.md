# TartarOS

A local sandbox for AI coding agents. On Linux it stacks Landlock (filesystem and
TCP rules), seccomp, a private PID, mount and (with no network grant) network
namespace, cgroup limits and an egress proxy for domain allow-lists.

> **Conflict of interest.** TartarOS is maintained by the author of this lab. Its
> adapter was written before its first measurement, goes through the same review as
> the others, and every result file says so (`conflict_of_interest`). Counts are not
> a ranking (spec §8).

- Measured: **0.1.0-alpha.16**, built from the tagged commit `f245b8fd`
  (`github.com/carlostapiacl/tartaros`, Apache-2.0) in a pinned `rust:1.99.1` image
  ([`runner/Dockerfile`](../runner/Dockerfile)); there is no release binary for Linux.
- Adapter: [`runner/adapters/tartaros.py`](../runner/adapters/tartaros.py) — maps the
  policy to flags and runs `tartaros run --strict <flags> -- /bin/sh -c <cmd>`.
  `--strict` makes a guarantee the host cannot install abort the run instead of
  degrading. Refusal signature: exit 78 and a line starting `tartaros:`.

## How `[policy]` maps

| neutral field | tartaros flag |
|---|---|
| `writable_roots` | `--write <path>` |
| `read_denies` / `read_allows` | `--read-deny <path>` / `--read-allow <path>` |
| `read_scope = "granted"` | `--read-deny /`, then `--read-allow` for `/usr /lib /lib64 /bin /sbin /etc /dev /proc`, the roots and the `read_allows` |
| `write_denies` | `--write-deny <path>` |
| `local_ports` | `--port <port>` |
| `allow_domains` | `--allow-domain <host>` |
| `isolate_pids`, `isolate_process_info`, `harden_syscalls`, `materialize_absent_handoff` | `--isolate-pids`, `--isolate-proc`, `--seccomp-strict`, `--materialize` |
| `max_processes` | `--max-procs <n>` |
| `inherit_env` / `env_passthrough` | `--inherit-env` / `--env <name>` |
| `[broker]` | the `[broker]` table of a policy file passed with `--config`: `port`, `auth_header = "X-Broker-Auth"`, `allowed_hosts`, `allow_internal`, one `[[broker.capability]]` per capability. The token and each injected value go in the launcher's environment, read by name (`token_env`, `value_env`): never on the command line or in the agent's environment. Since 0.1.0-alpha.11 |

Fields the adapter reports `unsupported`:

- `glob_read_denies` / `glob_denies` — no glob engine on Linux; tartaros refuses globs there.
- `allow_unix_socket_paths` — only an all-or-nothing `--deny-unix`.

`{effect_log}` contracts are `needs-feature`, as for every other sandbox here.

## Review of the adapter

A private trial of 0.1.0-alpha.4 (2026-10-16) was reviewed by Codex before anything
was published. Its findings and what became of them:

- *Wrong refusal signature* (exit 2 for both a refusal and a start failure): TartarOS
  0.1.0-alpha.6 gave refusals their own exit code, 78, and the adapter declares it. The
  change came after seeing those results and is recorded as such in the adapter.
- *`--isolate-proc` hid the agent's own `/proc/self`*: since 0.1.0-alpha.7 every Linux
  run with namespaces gets a private PID namespace and a fresh `/proc`; the mapping is
  unchanged.
- *The strict profile does not turn on `--private-tmp` or `--deny-unix`*: kept as it
  is. `--deny-unix` refuses every AF_UNIX socket, including the socketpairs some
  controls use; `--private-tmp` is an opt-in for headless browsers. The other adapters
  likewise use their sandbox's own strict tier rather than every optional switch.
- *`--log` could serve `{effect_log}`*: left `needs-feature`, like the other sandboxes,
  until the runner can place a supervisor-owned log.

## Results

- 0.1.0-alpha.16: [2026-10-26-tartaros-alpha16](../results/2026-10-26-tartaros-alpha16/README.md), the masked-credential contracts measured.
- 0.1.0-alpha.11: [2026-10-22-tartaros-alpha11](../results/2026-10-22-tartaros-alpha11/README.md), the broker contracts measured.
- 0.1.0-alpha.10: [2026-10-22-tartaros](../results/2026-10-22-tartaros/README.md), the first measurement.
