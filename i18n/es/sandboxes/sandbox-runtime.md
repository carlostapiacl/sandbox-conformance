# sandbox-runtime (`srt`)

El sandbox runtime de Anthropic. En Linux se apoya en bubblewrap para los
namespaces de filesystem, PID y red. Un filtro seccomp bloquea la creación de
sockets AF_UNIX y io_uring, y proxies HTTP y SOCKS en el host deciden a qué
dominios se puede llegar.

Medí la versión 0.0.79 (`@anthropic-ai/sandbox-runtime`), compilada desde el
commit `d9aac2098351ca17f3743fbaf6ecbd0051b7e00e` (tag v0.0.79), y el
2026-10-21 la versión 0.0.81 (commit `c40cf14a65d025e3cd27f071f13a73c12b3b1f92`,
tag v0.0.81), con licencia Apache-2.0. El adapter es
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

## Resultados {#results}

sandbox-runtime: hallazgos reportados al vendor; sus resultados se publican cuando estén corregidos.
