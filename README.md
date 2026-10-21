# sandbox-conformance

An open lab for measuring sandboxes for AI coding agents.

Every sandbox makes claims: "the agent can't read your keys", "it can't reach the
network", "it can't plant a git hook". This repository turns those claims into
**contracts anyone can run**, and keeps the results of running them against each
sandbox, so you can compare them on the same tests, with the evidence attached.

It is not tied to any one sandbox. Add a contract, measure your sandbox, publish
the result.

## What's here

| folder | what |
|---|---|
| `contracts/` | the tests, one TOML file each, grouped by topic, each crediting its source |
| `spec/` | the [contract format](spec/format.md), explained for people who want to write one, and [what a result means](spec/verdicts.md) (draft) |
| `sandboxes/` | one page per sandbox: how a contract maps to its configuration, and its results by version |
| `results/` | published runs with their raw evidence, and the generated comparison table |

## What a contract is

Three parts, so a result is never just "it returned an error":

- **attack**: something the agent must not be able to do;
- **control**: legitimate work that must keep working (a sandbox that blocks
  everything fails here);
- **effect**: what is checked on disk or on the wire afterwards (the file is
  unchanged, the secret never appeared).

Before a contract counts against a sandbox, its attack must work **without** a
sandbox on the same host. Otherwise a "blocked" result would prove nothing.

## Status

First contracts in. `contracts/` holds 166 guarantees harvested from the public
test suites of other sandboxes — sandbox-runtime (114), nono (32), Codex (17),
bubblewrap (1) and OpenHands (2) — plus 22 by-omission variants derived from them,
each re-expressed in the neutral format and credited in
[`SOURCES.md`](SOURCES.md) and its own `source` field.

Maintained by the author of TartarOS, a competing sandbox. That is why the
contracts come from the other projects' test suites. TartarOS will be measured
in a later run, with its results published the same way.

First results in: [`results/2026-10-15/`](results/2026-10-15/README.md) measures
sandbox-runtime 0.0.79, nono 0.80.0 and Codex CLI 0.162.1 on Linux (kernel 6.8),
with the [runner and adapters](runner/README.md) that produced them and a page per
sandbox in [`sandboxes/`](sandboxes/README.md).

A fourth sandbox, [landrun](sandboxes/landrun.md) (pure Landlock, MIT), is now
measured alongside the three in a [four-column run](results/2026-10-15-four-sandboxes/README.md).
Adding a sandbox is one adapter module in `runner/adapters/`; the engine and the
contracts are untouched.

The [by-omission run](results/2026-10-15-by-omission/README.md) re-measures the
read-deny contracts in a capability sandbox's own model (grant the workspace,
omit the secret), so nono is measured where the neutral model only returned
`unsupported`.

The [2026-10-16 run](results/2026-10-16/README.md) is the first judged by
[`spec/verdicts.md`](spec/verdicts.md). The old runner reproduces the 2026-10-15
results on a fresh host; the new one changes five, each traced to a cause. The lab
tests itself against [reference sandboxes](runner/reference/README.md) whose behaviour
is known (`python3 -m unittest discover -s runner/tests`).

The [2026-10-21 run](results/2026-10-21/README.md) measures the latest releases:
sandbox-runtime 0.0.81 and Codex CLI 0.163.0 (nono and landrun unchanged). The
previous versions were re-measured first and reproduced. Which results changed in which
version is in [`results/versions.md`](results/versions.md).

Next: macOS runs, [more corpora](corpus-roadmap.md) harvested from other sandboxes' test suites, and
a site that lets you search a guarantee and see which sandbox holds it.
