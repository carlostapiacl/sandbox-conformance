# Publish a run

A published run is a folder `results/<date>[-what]` with:

- `<sandbox>.json` per sandbox: one line per case, with its result, basis, reason, exit
  statuses, effect and the contract's hash, plus the run's sandbox identity, host stamp,
  profile, spec version and corpus version;
- `raw/<sandbox>.full.json`: everything the runner captured;
- `comparison.md`: the table, generated;
- `review.json`: the reading of every result other than `contained`, with who and why;
- `README.md`: what was measured, on what, and anything a reader needs to read it.

```sh
python3 runner/report.py /tmp/out results/2026-11-02-mysandbox
python3 runner/versions.py > results/versions.md
```

Before publishing, check every result that is not `contained` against its raw output and
give it a reading. State nothing that was not run. A published result is never edited: a
correction is a new run, or a new reading that keeps the old one.

To submit a run measured elsewhere, open a pull request with the folder and the commit of
the lab it ran. A finding about a sandbox follows the [disclosure rules](../methodology.md#disclosure).
