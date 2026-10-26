# Contracts

A contract is one TOML file stating one guarantee. It is written in neutral terms, so it
reads the same whatever sandbox runs it, and an [adapter](adapters.md) translates it.

```toml
id       = "secrets-read-deny-single-file"
category = "secrets"
severity = "critical"
os       = ["linux", "macos"]
source   = "anthropics/sandbox-runtime test/sandbox/... (Apache-2.0)"

[policy]                      # what the agent runs under
read_denies    = ["{root}/home/.netrc"]
writable_roots = ["{root}/work"]

[[fixture]]                   # created before the run
path    = "{root}/home/.netrc"
content = "machine x login y password hunter2"

[attack]                      # must not take effect
cmd = "grep -q hunter2 {root}/home/.netrc"

[control]                     # must keep working
cmd = "echo ok > {root}/work/f.txt"

[assert]                      # the effect checked afterwards
unchanged = "{root}/home/.netrc"
```

`{root}` is a fresh directory per case. Unknown fields are rejected, so a typo fails
loudly instead of passing as a weaker policy.

Every contract comes from another project's public test suite and names it in `source`.
It re-expresses the guarantee; it does not copy the test. The
[catalog](../contracts/index.md) lists the current ones and the
[format reference](../reference/format.md) every field.

Contracts are grouped in categories: `filesystem`, `secrets`, `network`, `credentials`,
`trust-handoff` (files a trusted tool runs later, such as git hooks), `isolation`, `ipc`,
`lifecycle` and `resources`. `severity` is the contract's, set when it is written.
