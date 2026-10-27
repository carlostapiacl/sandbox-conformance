# sandbox-conformance

An open lab for measuring sandboxes for AI coding agents.

Every sandbox makes claims: "the agent can't read your keys", "it can't reach the
network", "it can't plant a git hook". This repository turns those claims into
**contracts anyone can run**, and keeps the results of running them against each
sandbox, so you can compare them on the same tests, with the evidence attached.

It is not tied to any one sandbox. Add a contract, measure your sandbox, publish
the result.

**Documentation:** [carlostapiacl.github.io/sandbox-conformance/docs](https://carlostapiacl.github.io/sandbox-conformance/docs/):
quickstart, concepts, how-to guides, methodology, every run and the contract catalog.
In Spanish at [/docs/es](https://carlostapiacl.github.io/sandbox-conformance/docs/es/): the
translations are in `docs-es/` and `i18n/es/` (glossary in `i18n/es/GLOSARIO.md`), and a page
whose English original changed since it was translated says so until it is re-translated and
stamped (`python3 i18n/es/stamp.py`).

## What's here

| folder | what |
|---|---|
| `contracts/` | the tests, one TOML file each, grouped by topic, each crediting its source |
| `corpus/` | the corpus versions: the exact contract files of each, by hash |
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

The corpus is versioned: **v1.1** (2026-10-26) is 196 contracts, harvested from the
public test suites of sandbox-runtime, nono, Codex, Deno, bubblewrap and OpenHands, with
by-omission variants and six masked-credential contracts, each re-expressed in the
neutral format and credited in [`SOURCES.md`](SOURCES.md) and its own `source` field.
Which contracts a version is, and when it moves, is in [`corpus/`](corpus/README.md).

Maintained by the author of TartarOS. TartarOS is where I try each escape the lab
finds, to see whether it can be mitigated, so it is built against these contracts and
its column should be read that way. That is also why the contracts come from the other
projects' test suites. TartarOS is measured like the others since the
[2026-10-22 run](results/2026-10-22-tartaros/README.md), and its
[page](sandboxes/tartaros.md) and result file record the conflict of interest.

Contracts and adapters are welcome: see [`CONTRIBUTING.md`](CONTRIBUTING.md).

Reports I sent to each vendor's security program, as of 2026-10-27:

| sandbox | reported | still open |
|---|---:|---:|
| sandbox-runtime | 4 | 1 |
| codex | 2 | 1 |
| nono | 0 | 0 |
| landrun | 0 | 0 |

The details of an open report are not published until the vendor fixes it
([`SECURITY.md`](SECURITY.md)).

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

The [2026-10-22 run](results/2026-10-22-tartaros/README.md) adds TartarOS 0.1.0-alpha.10,
on the same host, contracts and lab tools as the 2026-10-21 run. The
[alpha.11 run](results/2026-10-22-tartaros-alpha11/README.md) the same day measures the
`[broker]` contracts for the first time: their baseline now runs against a
[reference broker](spec/format.md#the-broker-table) with no defences, the same for every
sandbox.
The [2026-10-26 run](results/2026-10-26-tartaros-alpha16/README.md) measures TartarOS
0.1.0-alpha.16 and sandbox-runtime 0.0.81 on six new masked-credential contracts: both
contain all six on Linux.

Next: macOS runs and [more corpora](corpus-roadmap.md) harvested from other sandboxes' test suites.

The results and what they mean are written up at [carlostapia.cl](https://carlostapia.cl/notes/sandbox-escapes-no-rule-broken/).
