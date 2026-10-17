# Not translatable to the by-omission model

Of the 62 contracts nono reports `unsupported` because of a `read_denies` or
`write_denies` field, 22 were rewritten as `<id>-by-omission` variants (see the
run README). The other 36 cannot be expressed in the granted model without
changing what the attack tests, so they are not translated. They count as what
they are: a guarantee nono's model does not express.

## writable-except-X (31 contracts)

A `write_deny` on a path **inside** a writable root: the workspace is writable
*except* this file. The granted model has no way to carve a non-writable hole
out of a writable area.

- `filesystem-deny-ancestor-rename` — write_deny `{root}/work/private` inside the writable root
- `filesystem-writable-root-move-across-roots` — write_deny `{root}/work/locked` inside the writable root
- `filesystem-write-deny-absent-path` — write_deny `{root}/work/denied.lock` inside the writable root
- `filesystem-write-deny-rename-bypass` — write_deny `{root}/work/protected` inside the writable root
- `filesystem-write-deny-symlink-alias` — write_deny `{root}/work/protected` inside the writable root
- `filesystem-write-deny-truncate-unlink` — write_deny `{root}/work/protected` inside the writable root
- `filesystem-write-deny-unlink-recreate` — write_deny `{root}/work/policy.lock` inside the writable root
- `filesystem-write-deny-via-symlink-spelling` — write_deny `{root}/work/away/to-hooks` inside the writable root
- `read-deny-trailing-slash-nested-write-deny` — write_deny `{root}/work/secrets/sub` inside the writable root
- `read-deny-under-write-deny` — write_deny `{root}/work/proj` inside the writable root
- `secrets-home-credentials-in-writable` — write_deny `{root}/home/.aws` inside the writable root
- `secrets-read-deny-also-write-denied` — write_deny `{root}/work/.secrets` inside the writable root
- `secrets-read-deny-under-write-denied-ancestor` — write_deny `{root}/work/cfg` inside the writable root
- `trust-handoff-bracketed-root` — write_deny `{root}/w[o]rk/secrets` inside the writable root
- `write-deny-absent-deep` — write_deny `{root}/work/a/b/c/policy.json` inside the writable root
- `write-deny-backslash-absent` — write_deny `{root}/work/c\d/file` inside the writable root
- `write-deny-covers-nested-root` — write_deny `{root}/work/proj` inside the writable root
- `write-deny-cut-short-hop` — write_deny `{root}/w/name` inside the writable root
- `write-deny-dangling-link-target` — write_deny `{root}/here/new` inside the writable root
- `write-deny-equals-root` — write_deny `{root}/proj` inside the writable root
- `write-deny-existing-file-chmod` — write_deny `{root}/work/repo/.git/config.lock` inside the writable root
- `write-deny-glob-chars-dir` — write_deny `{root}/[WIP] project/keep` inside the writable root
- `write-deny-link-dotdot` — write_deny `{root}/here/down/file` inside the writable root
- `write-deny-noncanonical-absent` — write_deny `{root}/work//protected/./evil` inside the writable root
- `write-deny-symlinked-parent` — write_deny `{root}/work/proj2/.cfg` inside the writable root
- `write-deny-through-policy-symlink` — write_deny `{root}/work/link/settings.json` inside the writable root
- `write-deny-trailing-slash` — write_deny `{root}/work/secrets/` inside the writable root
- `write-deny-under-dotdot-root` — write_deny `{root}/p/real/file` inside the writable root
- `write-deny-unsearchable-dir` — write_deny `{root}/locked/keep` inside the writable root

## secret inside the workspace (6 contracts)

The protected path lives **inside** a writable root. Granting the workspace
makes it readable; the only way to protect it is a deny within the grant.

- `read-allow-inside-deny-writable-ancestor` — protected path `{root}/base/denied/secret.txt` inside the workspace
- `read-deny-symlink-entry` — protected path `{root}/work/secrets/key` inside the workspace
- `read-deny-symlinked-dir` — protected path `{root}/work/dotfiles/private/key` inside the workspace
- `secrets-read-deny-after-chmod` — protected path `{root}/work/cfg/secrets/key` inside the workspace
- `secrets-read-deny-rename-out` — protected path `{root}/box/token` inside the workspace

## deny nested inside an allow (1 contract)

A `read_deny` on a path that sits **inside** a `read_allow` (a hole punched in a
carve-out). The granted model re-allows the parent, so the nested secret becomes
readable: there is nothing to omit without also dropping the legitimate sibling.

- `read-allow-trailing-slash-nested-deny` — read_deny `{root}/priv/pub/secret` inside read_allow `{root}/priv/pub/`

## root carve-out (1 contract)

A `read_deny` of `/` with system carve-outs: this *is* the granted model
written inversely (deny everything, re-allow system paths). Rewriting it as
`read_scope = "granted"` would duplicate an existing contract, so it is left
as the neutral-model statement it already is.

- `read-deny-root-carve-out`

Total not translatable: 36. Translatable variants: 22. Sum: 58 (= the 58 deny-unsupported).
