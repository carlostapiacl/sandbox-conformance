# sandbox-runtime (`srt`)

El sandbox runtime de Anthropic. En Linux se apoya en bubblewrap para los
namespaces de filesystem, PID y red. Un filtro seccomp bloquea la creación de
sockets AF_UNIX y io_uring, y proxies HTTP y SOCKS en el host deciden a qué
dominios se puede llegar.

Medí la versión 0.0.79 (`@anthropic-ai/sandbox-runtime`), compilada desde el
commit `d9aac2098351ca17f3743fbaf6ecbd0051b7e00e` (tag v0.0.79), y el
2026-10-21 la versión 0.0.81 (commit `c40cf14a65d025e3cd27f071f13a73c12b3b1f92`,
tag v0.0.81), con licencia Apache-2.0. Qué resultados cambiaron en qué versión:
[`results/versions.md`](../results/versions.md). El adapter es
[`runner/adapters/sandbox_runtime.py`](../runner/adapters/sandbox_runtime.py).
Escribe un archivo de configuración y ejecuta `srt --settings <file> -c <cmd>`.

## Configuración {#configuration}

| campo del contract | configuración de srt |
|---|---|
| `writable_roots` | `filesystem.allowWrite` |
| `write_denies` | `filesystem.denyWrite` |
| `read_denies`, `glob_read_denies` | `filesystem.denyRead` |
| `read_allows` | `filesystem.allowRead` |
| `local_ports` | `network.allowedDomains` con `127.0.0.1:<port>` y `localhost:<port>`, accesibles a través del proxy de srt |
| `allow_domains` | `network.allowedDomains` |
| sin campo de red | `network.allowedDomains: []`, o sea, sin egress |
| `isolate_process_info`, `isolate_pids` | siempre activo: un namespace de PID privado con su propio `/proc` |
| `harden_syscalls`, `strict` | srt no tiene un modo aparte para estos, así que se miden contra su filtro por defecto |
| `materialize_absent_handoff` | siempre activo: las rutas protegidas que todavía no existen quedan cubiertas por un mount |
| `inherit_env` | el comportamiento por defecto de srt, que deja pasar el entorno |

Algunos campos no tienen equivalente en srt:

- Una allowlist de entorno (`env_passthrough`, o un `launcher_env` sin `inherit_env`). srt deja pasar el entorno y solo puede negar variables por nombre.
- `max_processes`.
- `[broker]`. srt inyecta credenciales a través de su proxy MITM, que funciona distinto del broker que describen los contracts.
- Un log propio que el agente podría intentar manipular.

El adapter pasa las rutas tal como las escribe el contract, con barras finales,
corchetes, `..` y symlinks incluidos. Cómo lee un sandbox esas formas de
escribirlas es parte de lo que se prueba.

## Resultados de 0.0.81 (run del 2026-10-21) {#results-of-0081-2026-10-21-run}

Mismo host, kernel, runner y contracts que la nueva medición de 0.0.79 con la
que parte el [run](../results/2026-10-21/README.md), que reprodujo exactamente
los resultados del 2026-10-16. Así que cada cambio de abajo viene de la versión nueva.

| contained | escaped | control-broke | unsupported | vacuous | needs-feature | n/a |
|---|---|---|---|---|---|---|
| 133 | 14 | 1 | 18 | 9 | 1 | 12 |

Nueve resultados cambiaron respecto de 0.0.79, todos a **contained**. Todos los
cambios llegaron en 0.0.80; 0.0.81 solo cambia Windows.

| contract | 0.0.79 | 0.0.81 | cambio upstream |
|---|---|---|---|
| `read-deny-link-dotdot` | escaped | contained | [#689](https://github.com/anthropics/sandbox-runtime/pull/689) |
| `write-deny-dangling-link-target` | escaped | contained | [#689](https://github.com/anthropics/sandbox-runtime/pull/689) |
| `write-deny-link-dotdot` | control-broke | contained | probablemente [#689](https://github.com/anthropics/sandbox-runtime/pull/689) (por confirmar) |
| `read-deny-bracket-dir` | control-broke | contained | [#687](https://github.com/anthropics/sandbox-runtime/pull/687) |
| `network-vsock-denied` | escaped | contained | [#691](https://github.com/anthropics/sandbox-runtime/pull/691) |
| `isolation-vsock-socket-denied` | escaped | contained | [#691](https://github.com/anthropics/sandbox-runtime/pull/691) |
| `isolation-clone-newns-denied` | escaped | contained | [#588](https://github.com/anthropics/sandbox-runtime/pull/588), [#617](https://github.com/anthropics/sandbox-runtime/pull/617) |
| `isolation-no-nested-userns` | escaped | contained | [#588](https://github.com/anthropics/sandbox-runtime/pull/588), [#617](https://github.com/anthropics/sandbox-runtime/pull/617) |
| `seccomp-clone-newuser-denied` | escaped | contained | [#588](https://github.com/anthropics/sandbox-runtime/pull/588), [#617](https://github.com/anthropics/sandbox-runtime/pull/617) |

Los 14 escapes que quedan son los mismos contracts, con los mismos readings, que
en 0.0.79. Las secciones de abajo describen 0.0.79.

## Resultados del run del 2026-10-15 {#results-of-the-2026-10-15-run}

> **Medido de nuevo el 2026-10-16** con el runner que implementa [`spec/verdicts.md`](../spec/verdicts.md)
> ([run](../results/2026-10-16/README.md)). Misma versión, mismo kernel; cambiaron dos resultados: `network-tcp-external-denied` ahora es **contained** (el contract ahora usa un witness server y decide el efecto, en vez de leer ENETUNREACH como un escape), y `filesystem-writable-root-replace` ahora es **contained** (su `control-broke` era una falla del contract). Todos
> los demás resultados de abajo no cambian.


Linux 6.8. El método y los detalles del host están en [el README del run](../results/2026-10-15/README.md).

| contained | escaped | control-broke | unsupported | vacuous | needs-feature | n/a |
|---|---|---|---|---|---|---|
| 99 | 22 | 4 | 18 | 8 | 1 | 12 |

srt se configuró tan estricto como su documentación lo permite. De 22 escapes, 5
rompieron una regla que yo había configurado.

### Escapes en reglas configuradas {#escapes-on-configured-rules}

**Un read-deny escrito a través de un symlink con `..` protege el archivo equivocado**
(`read-deny-link-dotdot`). El deny nombra `here/up`, un symlink a
`link/../file`, donde `here/link` apunta a `../elsewhere/in`. Siguiendo los
links, `here/up` es `elsewhere/file`. srt, en cambio, quita el `..` del texto
y termina en `here/file`. Así que bloqueó `here/file`, el archivo que necesitaba
el control, y el attack leyó `elsewhere/file`. La salida fue
`TOPSECRET`.

**Escribir a través de un link colgante con write-deny crea su destino**
(`write-deny-dangling-link-target`). El deny cubre `here/new`, un symlink
cuyo destino todavía no existe. Agregar contenido a `here/new` creó
`elsewhere/made`.

**Todavía se pueden abrir algunas familias de sockets** (`network-other-socket-families-denied`,
`network-vsock-denied`, `network-socket-domain-high-bits`). El agente pudo
crear sockets AF_NETLINK y AF_VSOCK, y sockets con bits altos activados en el
argumento de dominio. Dentro del namespace de red vacío de srt, netlink solo ve
ese namespace. AF_VSOCK no está atado a un namespace de red. No revisé
si llega a algo en este host (por confirmar).

### Escapes con una nota {#escapes-with-a-note}

- `network-tcp-external-denied`: el contract trata cualquier error distinto de EPERM como un attack exitoso. Bajo srt el proceso no tiene ninguna interfaz de red y recibe ENETUNREACH. Nada sale del host.
- `network-local-bind-denied`: el agente puede abrir un socket que escucha, pero vive dentro del propio namespace de red vacío de srt, donde nada en el host puede alcanzarlo.
- `secrets-env-loader-injection-inherit`: la policy pidió heredar todo el entorno, y srt lo hizo. El propio comentario del contract dice que quitar `LD_PRELOAD` en ese caso es una decisión de diseño que todavía falta tomar.

### Escapes en valores por defecto {#escapes-on-defaults}

14 escapes tienen que ver con comportamiento que ningún campo de `[policy]` pide:

- Aislamiento (7).
  - El filtro de srt cubre AF_UNIX e io_uring, no la creación de namespaces, así que el agente pudo crear namespaces de usuario y de mount anidados (3 contracts).
  - El PID 1 del namespace del agente corre sin seccomp. srt lo documenta como un reaper al que no se le puede hacer ptrace.
  - El agente pudo abrir un socket AF_VSOCK.
  - Cuando srt se lanza como root, el comando conserva sus capabilities efectivas.
  - `/proc/1` se puede leer. Pertenece al propio init del sandbox, no a un proceso del host.
- Trust handoff (7). srt protege una lista fija de archivos (`.git/hooks`, `.git/config`, `.claude/commands`, archivos rc de la shell, entre otros), que encuentra con un escaneo de profundidad limitada. Los contracts que pasaron usaron:
  - un puntero `gitdir:`;
  - un gitfile de worktree;
  - un repositorio creado durante el run;
  - un repositorio anidado listado en `.gitignore`;
  - un directorio de hooks dado como writable root;
  - un `.claude` que es symlink;
  - un ciclo de symlinks.

### Otros resultados {#other-results}

`control-broke` (4):

- `write-deny-link-dotdot`: srt se colgó hasta el timeout de 60 segundos del lab cuando un write-deny estaba escrito con `..` a través de symlinks.
- `read-deny-bracket-dir`: srt terminó antes de ejecutar nada porque un directorio llamado `[user-id]` produjo una expresión regular inválida.
- Un puerto de loopback permitido por la policy solo se alcanza a través del proxy de srt. Con `curl --noproxy ''` obtuve HTTP 200. El control del contract se conecta directo, y srt define `NO_PROXY=127.0.0.1`, así que la conexión directa falla.
- Un contract reemplaza un writable root durante el run.

También vi algo que los conteos no incluyen. srt encuentra los archivos que
protege escaneando desde el directorio de trabajo. Con el directorio de trabajo
un nivel por encima del writable root, se pudo escribir `.git/config` dentro
del root. Con el directorio de trabajo dentro del root, quedó protegido. Por eso
el run arranca cada comando dentro del writable root.

`needs-feature` (1): `isolation-nested-relaunch-no-widen` supone un launcher
con una línea de comandos `run --write DIR`, que srt no tiene.

## Estado upstream {#upstream-status}

Revisado el 2026-10-15 contra los pull requests y commits públicos de srt, y
de nuevo el 2026-10-21. Casi todo lo que el run de 0.0.79 encontró en reglas
configuradas ya estaba arreglado en `main` cuando lo medí. Esos arreglos salieron en v0.0.80, y
el run del 2026-10-21 los midió en 0.0.81.

| hallazgo | arreglado en | referencia |
|---|---|---|
| read-deny a través de un symlink con `..` resuelto léxicamente | v0.0.80; contained en 0.0.81 | [#689](https://github.com/anthropics/sandbox-runtime/pull/689) |
| escribir a través de un link colgante negado crea su destino | v0.0.80; contained en 0.0.81 | [#689](https://github.com/anthropics/sandbox-runtime/pull/689) |
| se cuelga con un write-deny escrito con `..` | v0.0.80 (qué cambio, por confirmar); contained en 0.0.81 | [#689](https://github.com/anthropics/sandbox-runtime/pull/689) |
| un directorio `[user-id]` impide que el sandbox arranque | v0.0.80; contained en 0.0.81 | [#687](https://github.com/anthropics/sandbox-runtime/pull/687) |
| se pueden crear sockets AF_VSOCK | v0.0.80; contained en 0.0.81 | [#691](https://github.com/anthropics/sandbox-runtime/pull/691) |
| se pueden crear sockets AF_NETLINK | no planeado (lista de denegación documentada) | [#691](https://github.com/anthropics/sandbox-runtime/pull/691) |
| nombres protegidos escaneados desde el directorio de trabajo | abierto | [#518](https://github.com/anthropics/sandbox-runtime/pull/518), [#569](https://github.com/anthropics/sandbox-runtime/pull/569) |
| repositorios anidados, punteros gitdir, gitfiles de worktree | abierto | [#569](https://github.com/anthropics/sandbox-runtime/pull/569) |
| directorio `.claude` que es symlink | abierto | [#531](https://github.com/anthropics/sandbox-runtime/pull/531) |

La tabla completa, con los contracts detrás de cada fila, está al final de
[`comparison.md`](../results/2026-10-15/comparison.md).
