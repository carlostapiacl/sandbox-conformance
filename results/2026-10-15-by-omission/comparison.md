# Comparison, by-omission run of 2026-10-15

Each cell is the result of one contract against one sandbox, set up through its adapter (`runner/adapters/`) as strictly as that sandbox's documentation allows. Only results I actually measured are listed. The host and the method are described in `README.md`.

| result | meaning |
|---|---|
| `contained` | the attack failed and the legitimate control still worked |
| `escaped` | the attack succeeded under the sandbox |
| `control-broke` | the attack failed, and so did the legitimate control |
| `unsupported` | the sandbox cannot express a `[policy]` field: a missing feature, not a vulnerability |
| `vacuous` | the attack fails on this host even without a sandbox, so the result proves nothing |
| `needs-feature` | the runner or the adapter cannot provide something the contract needs |
| `n/a` | macOS-only contract, or the host lacks something the contract requires |

Marks after a result:

- `*`: no `[policy]` field asks for this guarantee, so the result reflects the sandbox's defaults. An escape marked this way is a difference of defaults, not a configured rule that failed.
- `‡`: the contract counts this as an attack, but given how the sandbox is built it is not a breach. The notes below say why.
- `§`: the result depends on a newer kernel than this host's (Landlock ABI 6).

## Totals

| result | sandbox-runtime | nono | codex |
|---|---|---|---|
| contained | 21 | 17 | 18 |
| escaped | 0 | 4 | 0 |
| control-broke | 0 | 0 | 3 |
| unsupported | 0 | 0 | 0 |
| vacuous | 1 | 1 | 1 |
| needs-feature | 0 | 0 | 0 |
| not-applicable | 0 | 0 | 0 |
| invalid-contract | 0 | 0 | 0 |

## Per contract

| contract | category | sandbox-runtime | nono | codex |
|---|---|---|---|---|
| `filesystem-rm-under-read-deny-ancestor-by-omission` | filesystem | contained | contained | contained |
| `filesystem-write-reallow-inside-deny-by-omission` | filesystem | contained | contained | contained |
| `read-allow-writable-carveout-trailing-slash-by-omission` | filesystem | contained | contained | contained |
| `ipc-unix-socket-in-denied-dir-by-omission` | ipc | contained | escaped | contained |
| `isolation-root-mount-bypass-denied-by-omission` | isolation | vacuous | vacuous | vacuous |
| `read-allow-symlink-into-deny-by-omission` | secrets | contained | escaped | control-broke‡ |
| `read-allow-symlink-no-reopen-by-omission` | secrets | contained | escaped | control-broke‡ |
| `read-deny-alt-spelling-by-omission` | secrets | contained | contained | contained |
| `read-deny-around-nested-root-by-omission` | secrets | contained | contained | contained |
| `read-deny-backslash-name-by-omission` | secrets | contained | contained | contained |
| `read-deny-bracket-dir-by-omission` | secrets | contained | contained | contained |
| `read-deny-given-via-symlink-by-omission` | secrets | contained | contained | contained |
| `read-deny-link-dotdot-by-omission` | secrets | contained | contained | contained |
| `read-deny-not-reopened-by-nested-writable-by-omission` | secrets | contained | contained | contained |
| `secrets-read-allow-symlink-hop-no-widen-by-omission` | secrets | contained | contained | contained |
| `secrets-read-allow-symlink-into-deny-by-omission` | secrets | contained | escaped | control-broke‡ |
| `secrets-read-deny-dir-listing-by-omission` | secrets | contained | contained | contained |
| `secrets-read-deny-on-symlinked-path-by-omission` | secrets | contained | contained | contained |
| `secrets-read-deny-path-special-chars-by-omission` | secrets | contained | contained | contained |
| `secrets-read-deny-prefix-collision-by-omission` | secrets | contained | contained | contained |
| `secrets-read-deny-single-file-by-omission` | secrets | contained | contained | contained |
| `secrets-read-deny-symlinked-entry-by-omission` | secrets | contained | contained | contained |

Not applicable on this host for every sandbox (0): .

## Review notes

I read the raw output (`raw/`) for every result other than `contained`. These notes explain a result; they never change it.

### sandbox-runtime

- `isolation-root-mount-bypass-denied-by-omission` (vacuous): mount fails in the container without a sandbox; nothing is proven here.

### nono

- `ipc-unix-socket-in-denied-dir-by-omission` (documented): Landlock does not mediate connect() to a pathname unix socket, so a socket in an ungranted directory stays reachable. This is the gap the original contract already documents; it holds in the granted model too.
- `isolation-root-mount-bypass-denied-by-omission` (vacuous): mount operations fail in the container even without a sandbox (no CAP_SYS_ADMIN), so the attack proves nothing on this host.
- `read-allow-symlink-into-deny-by-omission` (design): The granted read path is itself a symlink into the protected area. nono resolves grants through symlinks (documented in its Path Resolution), so granting the link grants its target and the secret is read. srt grants the link name only and contains it; codex refuses to build the sandbox.
- `read-allow-symlink-no-reopen-by-omission` (design): The granted read path is itself a symlink into the protected area. nono resolves grants through symlinks (documented in its Path Resolution), so granting the link grants its target and the secret is read. srt grants the link name only and contains it; codex refuses to build the sandbox.
- `secrets-read-allow-symlink-into-deny-by-omission` (design): The granted read path is itself a symlink into the protected area. nono resolves grants through symlinks (documented in its Path Resolution), so granting the link grants its target and the secret is read. srt grants the link name only and contains it; codex refuses to build the sandbox.

### codex

- `isolation-root-mount-bypass-denied-by-omission` (vacuous): mount fails in the container without a sandbox; nothing is proven here.
- `read-allow-symlink-into-deny-by-omission` (interface): codex refuses to build the sandbox when a read grant resolves through a symlink ('cannot enforce sandbox read-only path'): the attack is stopped and so is the control.
- `read-allow-symlink-no-reopen-by-omission` (interface): codex refuses to build the sandbox when a read grant resolves through a symlink: fails closed, control broke too.
- `secrets-read-allow-symlink-into-deny-by-omission` (interface): codex refuses to build the sandbox when a read grant resolves through a symlink: fails closed, control broke too.

