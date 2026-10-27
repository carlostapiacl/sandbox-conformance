# Corpus versions

A corpus version is a fixed set of contracts, byte for byte: `v<version>.json` lists
every contract's id, path and SHA-256. A run records the hash of every contract it
ran, so anyone can check which version it measured
(`python3 runner/corpus.py of <result.json>`).

Two results are comparable contract by contract only when the contract is the same
file in both. Results across sandboxes or versions of one sandbox are compared on
the same corpus version, or on the contracts the two runs share unchanged
([`results/versions.md`](../results/versions.md) does the latter).

## When the version moves

The version is `MAJOR.MINOR`. Every change to `contracts/` comes with the next
version in the same pull request; the lab tests fail otherwise
(`runner/corpus.py check`).

| change | version | why |
|---|---|---|
| a contract added | minor | earlier results stay valid; the new one has none yet |
| a contract's file changed (attack, control, assert, policy, fixtures, `os`, `requires`, even a comment) | minor | its hash changes, so its earlier results are no longer for this contract; the others stay comparable |
| a contract removed, or a change to the contract format or to [`spec/verdicts.md`](../spec/verdicts.md) that can change the result of an unchanged contract | major | results before and after are not comparable without re-running |

Each manifest after the first lists what it changed (`since`: added, removed,
changed). [`contracts/CHANGES.md`](../contracts/CHANGES.md) says why.

A published run is never re-labelled: it measured the version whose hashes it
recorded. Re-measuring on a newer version is a new run.

## Versions

| version | date | contracts | what |
|---|---|---|---|
| [1.0](v1.0.json) | 2026-10-26 | 194 | the first version: the contracts of every run up to 2026-10-26, with the six masked-credential contracts. The runs before it ran contracts that have changed since and are listed as *pre-1.0* |
| [1.1](v1.1.json) | 2026-10-26 | 196 | two contracts from Deno's permission tests: a read-deny reached through `/proc/self/root`, and a write-denied directory that must survive `rm -rf` of its parent |
