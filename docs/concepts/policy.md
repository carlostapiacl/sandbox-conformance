# Policy and read models

`[policy]` states the confinement in neutral fields: `writable_roots`, `read_denies`,
`read_allows`, `allow_domains`, `[broker]`, `[[masked_env]]` and the rest in the
[format reference](../reference/format.md). Each adapter maps them to its sandbox, and a
field a sandbox cannot express makes the case `unsupported`.

Sandboxes read the filesystem in one of two ways, and a contract says which it is
written in.

The **neutral model** is the default: everything is readable except `read_denies`. It is
how sandbox-runtime and Codex are usually configured.

The **granted model** (`read_scope = "granted"`) is how capability sandboxes such as nono
and landrun work: only `writable_roots`, `read_allows` and the system paths the runner
provides are readable, so a secret is protected by not being granted. A deny inside a
granted area has no meaning there.

The same attack can be written in both models, and the corpus has *by-omission* variants
of the read-deny contracts in the granted model, so a capability sandbox is measured on
the guarantee and not on a model it does not speak. A guarantee that only one model can
state, such as a secret file in the middle of a writable workspace, is a capability gap,
recorded as such.
