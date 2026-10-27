# codex (`codex sandbox`)

El sandbox de Linux del Codex CLI de OpenAI. Usa bubblewrap para los namespaces
de filesystem, PID, IPC y red, define `no_new_privs` y aplica un filtro seccomp
que bloquea io_uring y ptrace, más las llamadas al sistema de red cuando la
red está restringida.

Medimos codex-cli 0.162.1 (`@openai/codex`), compilado desde el commit
`092d3acd6bec3e3a14bdc7e7a2810ab628ab759d` (tag rust-v0.162.1), y el
2026-10-21 codex-cli 0.163.0 (commit `83086188ae0614bd882818ff1aa23f3194962012`,
tag rust-v0.163.0), con licencia Apache-2.0. Qué resultados cambiaron en qué
versión: [`results/versions.md`](../results/versions.md). Llamamos directamente a su binario nativo `x86_64-unknown-linux-musl`
en vez del launcher de npm. Ese launcher es un script de Node, y un contract
que define `NODE_OPTIONS` en el entorno rompería el launcher antes de que el
sandbox llegara a arrancar. El adapter es [`runner/adapters/codex.py`](../runner/adapters/codex.py).
Escribe un profile de permisos con nombre en un `$CODEX_HOME/config.toml` temporal
y ejecuta `codex sandbox -P conformance -C <workspace> -- sh -c <cmd>`.

## Configuración {#configuration}

| campo del contract | profile de permisos |
|---|---|
| acceso de lectura a todo lo que no esté negado (el valor por defecto de los contracts) | `":root" = "read"` |
| `writable_roots` | `"<path>" = "write"` |
| `write_denies` | `"<path>" = "read"`. Cuando las entradas se superponen, gana la ruta más específica |
| `read_denies`, `glob_read_denies` | `"<path>" = "deny"` |
| `read_allows` | `"<path>" = "read"` |
| sin campo de red | `network.enabled = false` |
| `allow_domains` | el experimental `features.network_proxy`, más `network.domains` |
| allowlist de entorno, `env_passthrough` | `shell_environment_policy` con `include_only` en PATH, HOME, LANG y TERM, más las variables que se dejen pasar, e `ignore_default_excludes = false` |
| `inherit_env` | `shell_environment_policy.inherit = "all"` |
| `isolate_process_info`, `isolate_pids` | siempre activo: `--unshare-pid` con su propio `/proc` |
| `harden_syscalls`, `strict` | codex no tiene un modo aparte para estos, así que se miden contra su filtro por defecto |

Algunos campos no tienen equivalente en codex:

- `local_ports`. La red puede estar activada, desactivada o pasar por un proxy por dominio, pero codex no puede abrir un solo puerto de loopback.
- `max_processes`.
- `materialize_absent_handoff`.
- `[broker]`.
- Un log propio que el agente podría intentar manipular.

## Resultados de 0.163.0 (run del 2026-10-21) {#results-of-01630-2026-10-21-run}

Ningún resultado cambió respecto de 0.162.1: el [run](../results/2026-10-21/README.md)
primero volvió a medir 0.162.1 en el mismo host, runner y contracts, y las dos
versiones dan el mismo resultado en los 188 contracts. Todo lo de abajo vale para
0.163.0.

## Resultados del run del 2026-10-15 {#results-of-the-2026-10-15-run}

> **Medido de nuevo el 2026-10-16** con el runner que implementa [`spec/verdicts.md`](../spec/verdicts.md)
> ([run](../results/2026-10-16/README.md)). Misma versión, mismo kernel; cambió un resultado: `filesystem-writable-root-replace` ahora es **contained** (su `control-broke` era una falla del contract). Todos
> los demás resultados de abajo no cambian.


Linux 6.8. El método y los detalles del host están en [el README del run](../results/2026-10-15/README.md).

| contained | escaped | control-broke | unsupported | vacuous | needs-feature | n/a |
|---|---|---|---|---|---|---|
| 74 | 24 | 27 | 18 | 8 | 1 | 12 |

codex se configuró tan estricto como su documentación lo permite. De los escapes, tres
rompieron una regla que habíamos configurado.

### Escapes en reglas configuradas {#escapes-on-configured-rules}

**Un writable root dentro de un directorio con write-deny sigue siendo escribible**
(`write-deny-covers-nested-root`). codex resuelve las entradas superpuestas quedándose con
la más específica, así que el root anidado gana sobre el deny que lo cubre.

**Se sigue un writable root que es un symlink** (`fs-writable-root-symlink-out`,
`fs-writable-root-symlink-parent`). Si un writable root es un symlink que apunta
fuera de los otros roots, su destino pasa a ser escribible. El contract espera que el
sandbox rechace un root así. codex lo acepta.

### Escapes con una nota {#escapes-with-a-note}

- `secrets-env-loader-injection-inherit`: la policy pidió heredar todo el entorno, y codex lo hizo. El propio comentario del contract dice que quitar `LD_PRELOAD` en ese caso es una decisión de diseño que todavía falta tomar.

### Escapes en valores por defecto {#escapes-on-defaults}

20 escapes tienen que ver con comportamiento que ningún campo de `[policy]` pide:

- Trust handoff (13). codex deja `.git`, `.codex`, `.agents` y `.aws` como solo lectura en el nivel superior de cada writable root. En estos contracts el repositorio está un nivel por debajo del root, como estaría en un workspace con varios repositorios, y la protección no llega hasta ahí.
- Aislamiento (5).
  - El agente pudo crear namespaces de usuario anidados (3 contracts).
  - El agente pudo abrir `/proc/<pid>/mem` o `environ` de un ancestro.
  - `/proc/1` se puede leer. Pertenece al propio init del sandbox, no a un proceso del host.
- Ciclo de vida (2).
  - `.mcp.json` no está en la lista de archivos protegidos de codex.
  - Después de que le enviamos SIGTERM a `codex sandbox`, los procesos de adentro siguieron corriendo y escribieron el archivo marcador.

### Otros resultados {#other-results}

codex tuvo 27 resultados `control-broke`, más que cualquiera de los otros dos. En
21 de ellos, codex se negó a construir el sandbox y no ejecutó nada. Eso pasó
cuando una entrada era un symlink, pasaba por uno, nombraba una ruta que no
existía, era un solo archivo o contenía caracteres de glob como
`[WIP] project`. Los errores fueron `cannot enforce sandbox read-only path…` y
`bwrap: Can't mount tmpfs…`. El attack quedó detenido, pero también el trabajo
legítimo, y en la práctica el usuario recibiría un error en vez de un sandbox. Los
otros 6 fallaron de otras maneras:

- En dos contracts, un read-allow dentro de un read-deny siguió sin poder leerse.
- Tres controls necesitan llamadas al sistema o familias de sockets que el filtro de codex bloquea.
- Un contract reemplaza un writable root durante el run.

`needs-feature` (1): `isolation-nested-relaunch-no-widen` supone un launcher
con una línea de comandos `run --write DIR`, que codex no tiene.
