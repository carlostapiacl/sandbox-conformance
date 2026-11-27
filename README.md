# sandbox-conformance

An open lab for measuring sandboxes for AI coding agents.

Every sandbox for coding agents makes claims: the agent can't read your keys, can't reach the
network, can't plant a git hook. I turn each claim into a **contract** anyone can run, run every
contract against every sandbox through the same procedure, and publish the result with the
evidence of each case.

**Documentation:** [carlostapiacl.github.io/sandbox-conformance/docs](https://carlostapiacl.github.io/sandbox-conformance/docs/)
(quickstart, concepts, how-to guides, methodology, every run and the contract catalog), also
[in Spanish](https://carlostapiacl.github.io/sandbox-conformance/docs/es/).

## How a contract works

A contract is a TOML file with three parts:

- **attack**: something the agent must not be able to do;
- **control**: legitimate work that must keep working, so a sandbox that blocks everything
  does not pass;
- **effect**: what is checked on disk or on the wire afterwards (the file is unchanged, the
  secret never left).

Each contract runs twice on the same host: first without a sandbox, where the attack must
work, then inside the sandbox. An attack that fails even without a sandbox proves nothing and is
reported as `vacuous`. What each result means is defined in [`spec/verdicts.md`](spec/verdicts.md),
and the file format in [`spec/format.md`](spec/format.md).

The contracts are re-expressed from the public test suites of the sandboxes themselves
(sandbox-runtime, nono, Codex, Deno, bubblewrap, OpenHands), so each one tests a guarantee some
project already claims. Every file credits its source ([`SOURCES.md`](SOURCES.md)).

## Latest results

Run of [2026-11-20](results/2026-11-20/README.md), corpus v1.2 (198 contracts), Linux 6.8:

| sandbox | version | contained | escaped | unsupported |
|---|---|---:|---:|---:|
| [sandbox-runtime](sandboxes/sandbox-runtime.md) | 0.0.83 | 142 | 15 | 18 |
| [nono](sandboxes/nono.md) | 0.82.0 | 51 | 38 | 83 |
| [Codex CLI](sandboxes/codex.md) | 0.171.0 | 97 | 26 | 24 |
| [landrun](sandboxes/landrun.md) | 0.1.17 | 41 | 44 | 91 |
| [TartarOS](sandboxes/tartaros.md) | 0.1.0-alpha.25 | 172 | 3 | 0 |

`unsupported` means the sandbox has no way to express that rule: a missing feature, not an
escape. Every escape has a reading (a confirmed breach, documented, a design choice, or an
assumption of the contract that doesn't hold for that sandbox) in the run's
[`comparison.md`](results/2026-11-20/comparison.md). Every run is in [`results/`](results/README.md),
and what changed from one version of a sandbox to the next in
[`results/versions.md`](results/versions.md).

## What's here

| folder | what |
|---|---|
| `contracts/` | the contracts, one TOML file each, grouped by topic |
| `corpus/` | the corpus versions: the exact contract files of each, by hash |
| `spec/` | the contract format and the meaning of each result |
| `runner/` | the engine, one adapter per sandbox, the lab image and the reference sandboxes |
| `sandboxes/` | one page per sandbox: how a contract maps to its configuration, and its results by version |
| `results/` | the published runs, with the raw evidence of every case |

## Running it

```sh
python3 -m unittest discover -s runner/tests   # the lab against its reference sandboxes, any machine
python3 runner/corpus.py check                 # contracts/ is exactly the latest corpus version
```

Measuring a sandbox needs Docker on a disposable Linux host with Landlock; the
[quickstart](https://carlostapiacl.github.io/sandbox-conformance/docs/get-started/quickstart/) has
the steps. Adding a sandbox is one adapter module in `runner/adapters/`.

## How the lab has changed

- **2026-10-15.** First runs: sandbox-runtime, nono and Codex CLI, then landrun as a fourth
  column, and a by-omission run that measures capability sandboxes in their own model.
- **2026-10-16.** Results judged by a written spec. The lab tests itself against reference
  sandboxes whose behaviour is known (one allows everything, one denies everything), so a bug
  in the lab shows up before it reaches a result.
- **2026-10-21.** Before a new release is measured, the one it replaces is measured again on the
  same host and has to reproduce its published result (also on 2026-11-08 and 2026-11-20).
- **2026-10-22.** TartarOS added. Contracts on credential brokers run their baseline against a
  reference broker with no defences, the same for every sandbox.
- **2026-10-26.** The corpus is versioned (v1.0, v1.1) and every result records the version it
  ran on. A witness host lets contracts check that a masked credential never reaches the wire.
- **2026-11-08.** All five sandboxes on one runner commit, at their latest releases.
- **2026-11-20.** Corpus v1.2: two contracts on what a sandbox leaves at a protected path that
  doesn't exist yet, after SIGTERM and as seen by git.

Every change to a published contract is recorded with its reason in
[`contracts/CHANGES.md`](contracts/CHANGES.md), so a fix can be told from a change made to suit a
result.

## Conflict of interest

I maintain TartarOS, one of the sandboxes measured. It is where I try to mitigate each escape the
lab finds, so it is built against these contracts and its column should be read that way. That is
also why the contracts come from the other projects' test suites, and why its adapter goes through
the same review as the others. Every TartarOS result file records the conflict. The contracts written or changed at the same time as a TartarOS feature are marked in every
comparison (° and †) and listed in [`SOURCES.md`](SOURCES.md#written-alongside-tartaros).

## Contributing

Contracts and adapters are welcome: see [`CONTRIBUTING.md`](CONTRIBUTING.md). How a finding
about a measured sandbox is disclosed: [`SECURITY.md`](SECURITY.md).

The results and what they mean are written up at
[carlostapia.cl](https://carlostapia.cl/notes/sandbox-escapes-no-rule-broken/).

Apache-2.0.
