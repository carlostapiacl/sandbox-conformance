# nono

El sandbox de nolabs-ai. En Linux combina Landlock, que cubre el
filesystem y, desde la ABI 4, TCP, con un filtro seccomp para la red,
`no_new_privs` y un proceso padre que supervisa.

Medí la versión 0.80.0 desde el asset del release
`nono-v0.80.0-x86_64-unknown-linux-gnu.tar.gz`, después de verificarlo contra el
SHA256SUMS del release. El commit de origen es
`8bb041356d48f771a221e58c98d9b1ff442e76fe` (tag v0.80.0), y la licencia es
Apache-2.0. El adapter es [`runner/adapters/nono.py`](../runner/adapters/nono.py).
Escribe un profile y ejecuta
`nono -s run --no-diagnostics --no-rollback --no-audit --profile <file> -- sh -c <cmd>`.

## Configuración {#configuration}

| campo del contract | profile de nono |
|---|---|
| (base) | los grupos por defecto, menos `system_write_linux`, `user_tools`, `homebrew_linux` y `dangerous_commands*`. Lectura en `/usr/local/bin`, escritura en `/dev/null`, `workdir.access: none` |
| acceso de lectura a todo lo que no esté negado (el valor por defecto de los contracts) | `filesystem.read` sobre todo el árbol de prueba, `{root}` |
| `writable_roots` | `filesystem.allow`, o `allow_file` para un solo archivo |
| `read_allows` | `filesystem.read`, o `read_file` |
| `local_ports` | `network.block` más `network.connect_port`. Landlock filtra TCP solo por puerto, así que el permiso no queda limitado a loopback |
| `allow_domains` | `network.allow_domain`, a través del proxy de nono |
| sin campo de red | `network.block: true` |
| allowlist de entorno, `env_passthrough` | `environment.allow_vars` con PATH, HOME, LANG y TERM, más las variables que se dejen pasar |
| `inherit_env` | sin `allow_vars`. nono igual quita variables del loader como `LD_PRELOAD` |
| `max_processes` | `--max-processes` |
| `isolate_process_info` | nada que configurar: nono solo da acceso a `/proc/self` y a algunos otros archivos de `/proc`. Su opción `process_info_mode` existe solo en macOS |
| `harden_syscalls`, `strict` | nono no tiene un modo aparte para estos, así que se miden contra su filtro por defecto |

Algunos campos no tienen equivalente en nono:

- Un `read_denies` o `write_denies` que cae dentro de algo permitido. Landlock solo puede dar acceso, y nono se niega a arrancar cuando un deny se superpone con un permiso.
- `isolate_pids`. nono no crea un namespace de PID.
- `materialize_absent_handoff`.
- `[broker]` tal como lo definen los contracts. nono sí tiene un proxy de credenciales, pero usa sus propias rutas.

Casi todos los 78 resultados `unsupported` de nono vienen de ese primer punto. Los
contracts suponen un modelo donde todo se puede leer salvo que esté negado. nono
funciona al revés: das acceso al workspace y a nada más, y un
secreto queda protegido porque nadie le dio acceso. Con esa configuración la mayoría de estos
secretos nunca se podrían leer. La `[policy]` de los contracts no describe
esa configuración, así que no la medí en este run. Una versión de los
contracts de read-deny escrita para ese modelo me permitiría medirla.

## Medido en el modelo propio de nono (run by-omission) {#measured-in-nonos-own-model-by-omission-run}

El run del 2026-10-15 de abajo midió nono contra el modelo neutral, donde 58 de sus
78 resultados `unsupported` venían de campos `read_denies` / `write_denies` que el
modelo de solo permisos de nono no expresa. El [run by-omission](../results/2026-10-15-by-omission/README.md)
reformula los 23 contracts de lectura traducibles en el modelo propio de nono
(`read_scope = "granted"`: dar acceso al workspace, omitir el secreto) y mide los
tres sandboxes. nono pasa de 23 `unsupported` a **18 contained, 4 escaped, 1
vacuous**: mantiene esas garantías de lectura cuando se piden en el modelo que
habla. Los 4 escapes (un hueco de Landlock con sockets unix y tres casos de un permiso que
es un symlink hacia el área protegida) y los 39 contracts que no se pueden expresar
en el modelo granted están detallados ahí.

## Resultados del run del 2026-10-15 {#results-of-the-2026-10-15-run}

> **Medido de nuevo el 2026-10-16** con el runner que implementa [`spec/verdicts.md`](../spec/verdicts.md)
> ([run](../results/2026-10-16/README.md)). Misma versión, mismo kernel; cambió un resultado: `filesystem-writable-root-replace` ahora es **contained** (su `control-broke` era una falla del contract). Todos
> los demás resultados de abajo no cambian.


Linux 6.8, Landlock ABI 4. El método y los detalles del host están en [el README del run](../results/2026-10-15/README.md).

| contained | escaped | control-broke | unsupported | vacuous | needs-feature | n/a |
|---|---|---|---|---|---|---|
| 31 | 33 | 6 | 74 | 7 | 1 | 12 |

nono se configuró tan estricto como su documentación lo permite. De 33 escapes, 5
rompieron una regla que yo había configurado.

### Escapes en reglas configuradas {#escapes-on-configured-rules}

**Se pueden cambiar los metadatos de un archivo legible** (`filesystem-chmod-outside`,
`filesystem-utime-outside`, `filesystem-xattr-outside`). Con acceso de lectura al
árbol de prueba, el agente pudo cambiar el modo, las marcas de tiempo y los
atributos extendidos de archivos fuera de sus writable roots. Landlock no
cubre estas operaciones. Si nono no hubiera dado acceso de lectura a esos archivos
desde un principio, el agente no habría podido llegar a ellos.

**Se sigue un writable root que es un symlink** (`fs-writable-root-symlink-out`,
`fs-writable-root-symlink-parent`). Si un writable root es un symlink que apunta
fuera de los otros roots, su destino pasa a ser escribible. El contract espera que el
sandbox rechace un root así. nono lo acepta.

### Escapes con una nota {#escapes-with-a-note}

- `ipc-abstract-unix-socket` (`§`): limitar las conexiones a sockets unix abstractos requiere Landlock ABI 6, que necesita kernel 6.12 o más nuevo. Este host tiene ABI 4.

### Escapes en valores por defecto {#escapes-on-defaults}

27 escapes tienen que ver con comportamiento que ningún campo de `[policy]` pide:

- Trust handoff (17). Dentro de un writable root, nono no protege `.git/hooks`, `.git/config`, `.claude/`, los directorios de editores ni los archivos rc.
- Aislamiento (7).
  - El agente pudo crear namespaces de usuario anidados (3 contracts).
  - Cuando nono se lanza como root, el comando conserva sus capabilities.
  - `/proc/1` se puede leer, y también `/proc/<pid>/mem` y `environ` de un ancestro.
  - En este kernel nada impide que el agente envíe señales a procesos fuera del sandbox (`isolation-signal-host-process`, `§`: necesita Landlock ABI 6).
- Ciclo de vida (3).
  - Un proceso hijo dejado en segundo plano siguió corriendo después de que el comando terminó.
  - Después de que le envié SIGTERM al launcher, los procesos dentro del sandbox siguieron corriendo y escribieron el archivo marcador.
  - `.mcp.json` no está protegido.

Son diferencias de valores por defecto. De los tres grupos, los resultados de ciclo de vida
son los que merecen la mirada más atenta.

### Otros resultados {#other-results}

`control-broke` (6):

- Un writable root escrito `absent/../real`. nono exige que exista cada ruta a la que da acceso.
- Un writable root que se reemplaza durante el run.
- El relanzamiento anidado: el nono interior no pudo arrancar.
- Tres controls que necesitan llamadas al sistema que el filtro de red de nono bloquea: io_uring, un dominio de socket poco común y la IPC de multiprocessing.

`needs-feature` (1): `lifecycle-effect-log-tamper`. nono mantiene un registro de auditoría,
pero no conecté el adapter al lugar donde se guarda el log de un run
(por confirmar).
