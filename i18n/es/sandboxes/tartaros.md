# TartarOS

Un sandbox local para agentes de programación con IA. En Linux apila Landlock (reglas de
filesystem y TCP), seccomp, un namespace privado de PID, de mount y (sin permiso de red) de
red, límites de cgroup y un proxy de egress para allow-lists de dominios.

> **Conflicto de interés.** TartarOS y este lab partieron juntos, en octubre de 2026,
> del mismo autor: TartarOS es donde se prueban las variantes que encuentra el lab, una por
> una, para ver si cada una se puede mitigar, y el lab mide si se mitigó. Su
> adapter se escribió antes de su primera medición, pasa por la misma revisión que
> los demás, y cada archivo de resultados lo dice (`conflict_of_interest`).

- Medido: **0.1.0-alpha.16**, compilado desde el commit con tag `f245b8fd`
  (`github.com/carlostapiacl/tartaros`, Apache-2.0) en una imagen fijada `rust:1.99.1`
  ([`runner/Dockerfile`](../runner/Dockerfile)); no hay binario de release para Linux.
- Adapter: [`runner/adapters/tartaros.py`](../runner/adapters/tartaros.py). Traduce la
  policy a flags y ejecuta `tartaros run --strict <flags> -- /bin/sh -c <cmd>`.
  `--strict` hace que una garantía que el host no puede instalar aborte el run en vez de
  degradarse. Firma de rechazo: exit 78 y una línea que empieza con `tartaros:`.

## Cómo se traduce `[policy]` {#how-policy-maps}

| campo neutral | flag de tartaros |
|---|---|
| `writable_roots` | `--write <path>` |
| `read_denies` / `read_allows` | `--read-deny <path>` / `--read-allow <path>` |
| `read_scope = "granted"` | `--read-deny /`, después `--read-allow` para `/usr /lib /lib64 /bin /sbin /etc /dev /proc`, los roots y los `read_allows` |
| `write_denies` | `--write-deny <path>` |
| `local_ports` | `--port <port>` |
| `allow_domains` | `--allow-domain <host>` |
| `isolate_pids`, `isolate_process_info`, `harden_syscalls`, `materialize_absent_handoff` | `--isolate-pids`, `--isolate-proc`, `--seccomp-strict`, `--materialize` |
| `max_processes` | `--max-procs <n>` |
| `inherit_env` / `env_passthrough` | `--inherit-env` / `--env <name>` |
| `[broker]` | la tabla `[broker]` de un archivo de policy pasado con `--config`: `port`, `auth_header = "X-Broker-Auth"`, `allowed_hosts`, `allow_internal`, un `[[broker.capability]]` por capability. El token y cada valor inyectado van en el entorno del launcher, leídos por nombre (`token_env`, `value_env`): nunca en la línea de comandos ni en el entorno del agente. Desde 0.1.0-alpha.11 |

Campos que el adapter reporta como `unsupported`:

- `glob_read_denies` / `glob_denies`: no hay motor de glob en Linux; tartaros rechaza los globs ahí.
- `allow_unix_socket_paths`: solo hay un `--deny-unix` de todo o nada.

Los contracts `{effect_log}` son `needs-feature`, igual que para todos los demás sandboxes de aquí.

## Revisión del adapter {#review-of-the-adapter}

Codex revisó una prueba privada de 0.1.0-alpha.4 (2026-10-16) antes de que se
publicara nada. Sus hallazgos y lo que pasó con ellos:

- *Firma de rechazo equivocada* (exit 2 tanto para un rechazo como para una falla al arrancar): TartarOS
  0.1.0-alpha.6 les dio a los rechazos su propio código de salida, 78, y el adapter lo declara. El
  cambio vino después de ver esos resultados y queda registrado como tal en el adapter.
- *`--isolate-proc` escondía el propio `/proc/self` del agente*: desde 0.1.0-alpha.7 cada run
  de Linux con namespaces recibe un namespace de PID privado y un `/proc` nuevo; la traducción
  no cambia.
- *El profile estricto no activa `--private-tmp` ni `--deny-unix`*: se deja tal
  cual. `--deny-unix` rechaza todo socket AF_UNIX, incluidos los socketpairs que usan algunos
  controls; `--private-tmp` es opcional, para navegadores headless. Los otros adapters
  también usan el nivel estricto propio de su sandbox en vez de cada switch opcional.
- *`--log` podría servir para `{effect_log}`*: queda como `needs-feature`, igual que los otros sandboxes,
  hasta que el runner pueda poner un log del que sea dueño el supervisor.

## Resultados {#resultados}

- 0.1.0-alpha.16: [2026-10-26-tartaros-alpha16](../results/2026-10-26-tartaros-alpha16/README.md), con los contracts de credenciales enmascaradas medidos.
- 0.1.0-alpha.11: [2026-10-22-tartaros-alpha11](../results/2026-10-22-tartaros-alpha11/README.md), con los contracts del broker medidos.
- 0.1.0-alpha.10: [2026-10-22-tartaros](../results/2026-10-22-tartaros/README.md), la primera medición.
