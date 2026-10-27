# Corpus versions

A corpus version is a fixed set of contract files, by hash. Each run records the hash of
every contract it ran, so anyone can check which version a run measured:

```sh
python3 runner/corpus.py of results/2026-10-26-tartaros-alpha16/tartaros.json
# {"version": "1.0", "ran": 194, "of": 194, "whole": true}
```

A run that ran every contract of a version unchanged measured that version. One that ran
some of them measured a subset, shown as *v1.0 (6 of 194)*. Runs from before the first
version ran contracts that have changed since and are *pre-1.0*.

The version moves with every change to `contracts/`: a minor version for an added or
changed contract, a major one for a removal or a change of the format or the verdicts
that can change an unchanged contract's result. The lab tests fail if a contract changes
without the next version. The rules and the list of versions are in the
[corpus reference](../reference/corpus.md); why each contract changed is in the
[changelog](../changelog/contracts.md).

[What changed by version](../results/versions.md) compares versions of one sandbox on the
contracts their runs share unchanged.
