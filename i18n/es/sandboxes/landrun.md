# landrun

Un sandbox CLI delgado, puro Landlock: envuelve un comando con reglas de filesystem
y TCP de Landlock y nada más (sin namespaces, sin seccomp, sin proxy). Landlock
es allow-only, así que landrun es un sandbox de capacidades como nono, pero mucho más chico.

- Medido: **0.1.17** (binario de release `landrun-linux-amd64`), `github.com/Zouuup/landrun`, MIT.
- Adapter: [`runner/adapters/landrun.py`](../runner/adapters/landrun.py), arma las
  concesiones de Landlock y corre `landrun --best-effort <grants> -- /bin/sh -c <cmd>`.
  `--best-effort` hace falta porque landrun apunta por defecto a la ABI v9 de Landlock y
  este host es ABI 4 (kernel 6.8).

## Cómo se mapea `[policy]` {#how-policy-maps}

| campo neutral | flag de landrun |
|---|---|
| `writable_roots` | `--rwx <path>` (lectura, escritura, ejecución) |
| `read_allows` | `--ro <path>` |
| (paths del sistema, para que corran `sh`/`python3`/`curl`) | `--rox /usr /bin /sbin /lib /lib64`, `--ro /etc /dev /proc`, `--rwx /dev/null` |
| leer en todas partes (el default neutral) | `--ro /` |
| `local_ports` | `--connect-tcp <port>` |
| ningún campo de red | ninguna regla TCP → se deniegan todos los connect/bind TCP (Landlock net, ABI 4) |
| entorno | landrun no pasa nada que no se nombre, así que `--env` es el scrub: se pasan las variables básicas (y `env_passthrough`); `inherit_env` las pasa todas |

Campos que landrun no puede expresar (reportados `unsupported`):

- `read_denies` / `write_denies`: Landlock es allow-only; no se puede declarar un deny recortado de un área que se puede leer o escribir (la misma brecha que nono).
- `read_scope = "granted"`: se puede expresar desde el 2026-10-17 (SC-003): concedes el workspace y nada más; Landlock no necesita concesiones sobre los ancestros de un path. Hasta entonces el adapter lo reportaba `unsupported` por error.
- `allow_domains` (sin egress proxy), `isolate_pids` / `harden_syscalls` (sin namespaces ni seccomp), `materialize_absent_handoff`, `max_processes`, `[broker]`.

En este host (Landlock ABI 4) el scoping de abstract sockets y de señales de landrun (ABI
v6) no está disponible, así que esas garantías no se aplican; sus reglas de red cubren
solo TCP, así que UDP, netlink y las demás familias de sockets no se bloquean.

## Resultados (2026-10-15, Linux 6.8, [run de cuatro sandboxes](../results/2026-10-15-four-sandboxes/README.md)) {#results-2026-10-15-linux-68-four-sandbox-run}

> **Medido de nuevo el 2026-10-17** en el read model granted ([run](../results/2026-10-17-landrun/README.md)): 22 contracts que estaban en `unsupported` ahora se miden (17 contained, 4 escaped, 1 vacuous).
>
> **Medido de nuevo el 2026-10-16** con el runner que implementa [`spec/verdicts.md`](../spec/verdicts.md)
> ([run](../results/2026-10-16/README.md)). Misma versión, mismo kernel; cambió un resultado: `filesystem-writable-root-replace` ahora es **contained** (su `control-broke` era una falla del contract). Todos
> los demás resultados de abajo no cambiaron.


| contained | escaped | control-broke | unsupported | vacuous | needs-feature | n/a |
|---|---|---|---|---|---|---|
| 22 | 38 | 2 | 104 | 6 | 2 | 12 |

landrun cumple el confinamiento de paths del filesystem (write/symlink/hardlink/rename/unlink
fuera del workspace), la denegación de egress y bind TCP, `no_new_privs` y el
scrub del entorno (no pasa ninguna variable que no se nombre con `--env`). De los 38
escapes, **25 son garantías incorporadas que no provee** (sin protección de
trust-handoff basada en nombres, sin namespaces ni seccomp para el aislamiento y el ciclo de vida
de los procesos), **8 son límites de Landlock** (red solo TCP; el scoping de abstract sockets y de
señales necesita ABI 6, no la ABI 4 de este host), y **5 están confirmados**:
`chmod`/`utime`/`xattr` sobre un archivo que se puede leer fuera de los roots, y un writable root
que es un symlink que apunta hacia afuera, las mismas dos brechas que tiene nono. Los 104 unsupported
son el costo de ser allow-only: todos los contracts de read/write-deny y las
variantes por omisión. Las notas completas están en el `review.json` del run.
