# Contract format

A contract is one TOML file describing a single guarantee a sandbox should hold.
It is written so anyone can read it without knowing any sandbox's internals, and
so a runner can execute it against any sandbox through an adapter.
How a run of a contract is judged, and what each result means, is in
[`verdicts.md`](verdicts.md).

## Shape

```toml
id       = "secrets-read-deny-single-file"   # unique, kebab-case
category = "secrets"                         # folder it lives in
severity = "critical"                        # critical | high | medium
os       = ["linux", "macos"]                # where it applies
source   = "project test/path (License)"     # where the guarantee comes from
requires = ["userns"]                        # host capabilities needed (optional)

[policy]            # the confinement the agent runs under (sandbox-neutral fields)
read_denies    = ["{root}/home/.netrc"]
writable_roots = ["{root}/work"]

[[fixture]]         # files/dirs created before the run
path    = "{root}/home/.netrc"
content = "machine x login y password hunter2"

[attack]            # must NOT succeed
cmd = "grep -q hunter2 {root}/home/.netrc"

[control]           # legitimate work that MUST keep working
cmd = "echo ok > {root}/work/f.txt"

[assert]            # the real effect checked afterwards
unchanged = "{root}/home/.netrc"
```

## The three parts that make a result mean something

- **attack** — the forbidden operation. A contract counts against a sandbox only
  if this attack *works without any sandbox* on the same host; otherwise the run
  reports it VACUOUS, because "blocked" would prove nothing.
- **control** — ordinary work that must still succeed. A sandbox that blocks the
  attack by breaking the control fails the contract.
- **assert** — what is checked on disk or on the wire: a protected file is
  `unchanged`, a planted marker is `absent`.

`{root}` is a fresh temporary directory per run. `expect_refusal = true` marks a
policy whose correct outcome is that the sandbox refuses to start.

## Fields that make a result unambiguous

How each of these is judged is in [`verdicts.md`](verdicts.md) §4.

| field | where | meaning |
|---|---|---|
| `expect_exit` | `[attack]` | the status that means the attack took effect (default 0). With no `[assert]`, the contract is a *fidelity* contract: the sandbox must report exactly this status |
| `blocked_exit` | `[attack]` | the statuses that mean *blocked*. Required when the attack can exit with its blocked status for another reason: a Python script that exits 1 when blocked cannot tell that from an uncaught exception, so it exits 3 and declares `blocked_exit = [3]` |
| `control_requires_sandbox` | top level | why the control is expected to fail without a sandbox (it checks a variable the sandbox's proxy sets, or talks to its broker). Without it, a control that fails with no sandbox makes the case `invalid-baseline` |
| `repeat` | top level | run the sandboxed phase this many times, for attacks that depend on timing; any escape is an escape, reported as *k of n* |
| `bind` | `[[server]]` | the address a witness server listens on (default `127.0.0.1`). `{host_ip}` is this host's own non-loopback address, for a witness a sandboxed process must not reach; a contract that uses it declares `requires = ["host-ip"]` |

The control runs after the attack, in the same phase. It must not depend on
anything the attack may legitimately change when it succeeds (the contents of a
writable root, for example), or a working attack breaks it in the baseline.

Witnesses and asserts the runner provides:

| field | where | meaning |
|---|---|---|
| `log` | `[[server]]` | append each raw request head the server receives to this file |
| `log_paths` | `[[server]]` | append, one per line, the path each request line asks for (a pipelined one too), normalised as an ordinary server would before routing it: authority dropped, percent-escapes undone, dot segments resolved |
| `echo_headers` | `[[server]]` | answer with the request head received, so the agent sees what reached the upstream |
| `respond` | `[[server]]` | the raw response to send (default a `200 ok`) |
| `absent_line` | `[assert]` | `{ file, pattern }`: the effect is a line of `file` matching the regular expression `pattern` |
| `[[host_alias]]` | top level | `name`, `ip`: a host name resolved to `ip` for this case only (in `/etc/hosts`, restored afterwards) |

## The `[broker]` table

A credential broker lets the agent use a secret it never holds: the agent asks the
broker, the broker makes the real request with the secret added. A contract about
one declares it in neutral terms; each adapter maps it to its sandbox's broker.

```toml
[broker]
port  = 19550                       # loopback port the agent reaches it on
token = "run-token-only-the-agent-has"  # the agent sends it in X-Broker-Auth
allowed_hosts  = [".allowed.test"]  # forwarding allow-list (optional)
allow_internal = false              # may an allowed name resolve inward (optional)

[[broker.capability]]               # /up/rest -> upstream_base/rest
prefix        = "/up"
upstream_base = "http://127.0.0.1:19650"
inject_header = "Authorization"     # added by the broker
inject_value  = "Bearer the-agent-never-sees-this"
```

**The baseline runs against a reference broker.** Without a sandbox there is no
broker, so "the attack works without a sandbox" needs a stand-in. In the baseline
the runner starts [`runner/reference_broker.py`](../runner/reference_broker.py) on
the contract's port: a broker written the obvious way, with none of the defences
the contracts test (no token check, every agent header forwarded, prefix matched as
a string and the path appended as written, redirects followed, any host forwarded
by name). An attack that does not get through it makes the case `vacuous`; one
that does is then run against the sandbox's own broker. The reference broker is
the same for every sandbox.

## Adapters

Each sandbox maps the neutral `[policy]` to its own configuration. A field a
sandbox cannot express is a capability gap recorded as such — never counted as a
vulnerability. See `sandboxes/`.

## Read scope: the neutral model vs. the granted model

By default a contract uses the **neutral read model**: everything is readable
except the paths named in `read_denies`. This mirrors how sandbox-runtime and
Codex are usually configured (read-everywhere, then deny), and it is the model
behind every contract that has a `read_denies` field.

A capability sandbox like nono works the other way round. Landlock is
allow-only: you grant the workspace and nothing else, and a secret stays
protected because nobody granted it. A `read_denies` inside a granted area has
no meaning there, so the neutral contracts report `unsupported` against nono —
not because nono is weaker, but because the test is written in a model it does
not speak.

`read_scope = "granted"` states the policy in that second model, so the same
attack can be measured fairly against all three sandboxes:

```toml
[policy]
read_scope    = "granted"
writable_roots = ["{root}/work"]
read_allows    = ["{root}/home/notes.txt"]   # a non-secret file the control reads
```

Under `read_scope = "granted"` the only readable paths are `writable_roots`,
`read_allows`, and the system paths the runner already provides (so `sh`,
`python3`, `curl` still run). There are **no** `read_denies`: the protected
path is unreadable because it is not in any grant. A contract that needs a
`read_deny` *inside* a granted, writable area (a file protected in the middle
of the workspace) cannot be expressed this way; that is a real capability gap,
recorded as such, not translated.

An adapter that cannot express the granted model for its sandbox reports
`unsupported`, exactly as it does for any other field it cannot map.
