# sandbox-conformance

An open lab for measuring sandboxes for AI coding agents.

Sandboxes for coding agents say what they stop, such as reading your keys or planting a
git hook. This lab turns each of those claims into a **contract** anyone can run, runs it
against each sandbox through the same procedure, and publishes the result with the
evidence of every case.

**Corpus v1.1**: 196 contracts, re-expressed from the public test suites of
sandbox-runtime, nono, Codex, Deno, bubblewrap and OpenHands, each crediting its source.
Measured so far: sandbox-runtime, nono, Codex CLI, landrun and TartarOS, on Linux.

## Where to start

- To see the numbers: [All runs](results/index.md), then a run's folder for the evidence.
- To run it yourself: [Quickstart](get-started/quickstart.md).
- To know what a number means before trusting it: [Methodology](methodology.md) and
  [Results and readings](concepts/results.md).
- To add a guarantee or a sandbox: [Write a contract](how-to/write-a-contract.md),
  [Add a sandbox](how-to/add-a-sandbox.md).

## How a contract decides

A contract has three parts. The **attack** is something the agent must not be able to
do. The **control** is legitimate work that must keep working, so a sandbox that blocks
everything does not pass. The **assert** checks the real effect on disk or on the wire.
Before a contract counts against a sandbox, its attack must work with no sandbox on the
same host ([Baseline and control](concepts/baseline.md)).

TartarOS, one of the sandboxes measured, started with this lab, by the same author, to
try to mitigate each variant the lab finds. The
[methodology](methodology.md#conflict-of-interest) says how that is kept from shaping
the results.
