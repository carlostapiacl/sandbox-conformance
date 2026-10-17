# Runner

Runs the contracts against one sandbox through its adapter, inside a throwaway
Linux container. Never run it on a workstation: attacks do what they say.

| file | what |
|---|---|
| `run.py` | the runner: baseline without a sandbox, then attack + control + `[assert]` under it; records what each phase observed |
| `verdict.py` | the decision procedure of [`spec/verdicts.md`](../spec/verdicts.md): turns those observations into one result per contract |
| `adapters/<sandbox>.py` | maps a contract's neutral `[policy]` to that sandbox's configuration; `check()` names what it cannot express, `wrap()` builds the command |
| `adapters/common.py` | the `[policy]` vocabulary shared by every adapter |
| `report.py` | turns full runner output into a run folder: `<sandbox>.json`, `raw/`, `comparison.md` |
| `landing.py` | rebuilds the data block of `index.html` from one run folder, with the same marks and review notes as its `comparison.md` |
| `Dockerfile` | the lab image: base image by digest, every download checked against a fixed sha256; each adapter's `identity()` records the sha256 of what actually ran (`artifact_sha256`) |
| `lab.sh` | runs one sandbox in a `--rm` container with the options recorded in the host stamp |
| `sc-lab.apparmor` | AppArmor profile that only adds `userns` (Ubuntu 24.04), loaded for a run and removed after |
| `reference/` | fake sandboxes with a known behaviour (allow-all, deny-all, broken, refusers), used only to test the lab |
| `lima/` | a disposable local lab VM (Ubuntu 24.04, kernel 6.8, nothing mounted), as used for the 2026-10-16 run |
| `tests/` | the lab's own tests: `python3 -m unittest discover -s runner/tests` (Python 3.11+, no dependencies, no privileges) |

On a disposable Linux host with Docker:

```sh
apparmor_parser -r -W runner/sc-lab.apparmor
docker build -t sc-lab:tools runner/
sh runner/lab.sh sandbox-runtime /tmp/out          # or nono, codex; optional contract ids
python3 runner/report.py /tmp/out results/<date>
apparmor_parser -R runner/sc-lab.apparmor
```

Results: `contained`, `escaped`, `control-broke`, `unsupported` (a capability gap,
never a vulnerability), `vacuous` (the attack does not work without a sandbox
either), `needs-feature`, `not-applicable`. See `results/<date>/README.md` for
the method.
