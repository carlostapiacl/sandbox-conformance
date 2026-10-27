# By-omission run of 2026-10-15

The run of 2026-10-15 measured nono against the neutral read model, where
everything is readable unless a `read_denies` entry names it. nono uses
Landlock, which is allow-only, and its model is the opposite: you grant the
workspace and nothing else, and a secret stays protected because nobody granted
it. So 62 of nono's 78 `unsupported` results in that run said nothing about
nono: the test was written in a model nono does not speak.

This run measures the same attacks in nono's own model, fairly for all three
sandboxes. The `read_scope = "granted"` policy field (see
[`spec/format.md`](../../spec/format.md)) states that only the writable roots,
the read_allows and the runner's system paths are readable; there are no
read_denies. The secret lives outside every grant.

## What was translatable

Of the 62 contracts nono marked `unsupported` for a `read_denies` or
`write_denies` field, **22** were rewritten as `<id>-by-omission` variants, with
the same attack, control and assert. The other **39** cannot be expressed in the
granted model without changing what the attack tests; they are listed, with the
reason, in [`not-translatable.md`](not-translatable.md). In short:

| not translatable | count | why |
|---|---|---|
| writable-except-X | 31 | a `write_deny` inside a writable root; the granted model cannot carve a non-writable hole out of a writable area |
| secret inside the workspace | 6 | the protected path is inside a writable root, so granting the workspace makes it readable |
| deny nested inside an allow | 1 | a `read_deny` inside a `read_allow`; re-allowing the parent re-opens the secret |
| root carve-out | 1 | a `read_deny` of `/` with system carve-outs: this already *is* the granted model, written inversely |

These 39 are not a nono weakness; they are guarantees nono's model does not
express, counted as that.

## Results of the 22 variants

| result | sandbox-runtime | nono | codex |
|---|---|---|---|
| contained | reported | 17 | 18 |
| escaped | reported | 4 | 0 |
| control-broke | reported | 0 | 3 |
| vacuous | reported | 1 | 1 |

sandbox-runtime: findings reported to the vendor; its results will be published once they are fixed.

Every non-contained result was checked by hand against the raw output; the notes
are in `review.json` and at the end of [`comparison.md`](comparison.md).

## nono, before and after

The point of the run. In the neutral model all 22 of these were `unsupported` —
nono could not even be asked. In its own model:

| | before (neutral, 2026-10-15) | after (by-omission) |
|---|---|---|
| contained | 0 | 17 |
| escaped | 0 | 4 |
| control-broke | 0 | 0 |
| vacuous | 0 | 1 |
| unsupported | 22 | 0 |

nono holds 17 of the 22 read guarantees once they are stated in its model. The
4 escapes are honest and specific:

- `ipc-unix-socket-in-denied-dir` — Landlock does not mediate `connect()` to a pathname unix socket, so a socket in an ungranted directory stays reachable. The original contract already documents this gap; it holds here too.
- `read-allow-symlink-into-deny`, `read-allow-symlink-no-reopen`, `secrets-read-allow-symlink-into-deny` — the granted read path is itself a symlink into the protected area. nono resolves grants through symlinks (its documented Path Resolution), so granting the link grants its target and the secret is read. codex refuses to build the sandbox (control-broke).

The 1 vacuous is `isolation-root-mount-bypass-denied`: mount operations fail in
the container even without a sandbox (no `CAP_SYS_ADMIN`), so the attack proves
nothing on this host.

## codex in the granted model

codex can express the granted model, so it stays contained where it was:

- **codex**: 18 contained, 3 control-broke, 1 vacuous. The 3 control-broke are the symlink-grant cases, where codex refuses to build the sandbox rather than resolve a read grant through a symlink — it fails closed (the attack is stopped, and so is the control).

## Files

- `<sandbox>.json` — per-contract results of the 22 variants.
- `raw/<sandbox>.full.json` — everything the runner captured.
- `comparison.md` — contract × sandbox table and the review notes.
- `review.json` — the manual notes.
- `not-translatable.md` — the 39 contracts that cannot be stated in the granted model, with reasons.

## Limits of this run

- One OS, one kernel: Linux 6.8, Landlock ABI 4. Same host, image and container options as the 2026-10-15 run (see that run's README).
- A `vacuous` result proves nothing in either direction.
- This measures the granted model only for the 22 translatable read contracts. The 36 not-translatable ones remain guarantees nono's model does not express.
