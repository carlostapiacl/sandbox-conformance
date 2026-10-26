# Quickstart

The attacks do what they say: they try to read secrets, write outside the workspace and
reach the network. Run them only on a disposable host, never on your workstation.

## 1. The lab's own tests (any machine, no privileges)

```sh
git clone https://github.com/carlostapiacl/sandbox-conformance
cd sandbox-conformance
python3 -m unittest discover -s runner/tests     # Python 3.11+, no dependencies
python3 runner/corpus.py check                   # contracts/ is exactly the latest corpus version
```

The tests run the decision procedure against [reference sandboxes](repo:runner/reference)
whose behaviour is known: one that allows everything (every attack escapes), one that
denies everything (every control breaks), and refusers. If they pass, the lab judges a
case the way the [verdicts](../reference/verdicts.md) say.

## 2. One sandbox, on a disposable Linux host

You need Docker and a kernel with Landlock (Docker Desktop's kernel has none). The
published runs used Ubuntu 24.04 with kernel 6.8 in a [Lima VM](../how-to/run-on-linux.md).

```sh
sudo apparmor_parser -r -W runner/sc-lab.apparmor      # adds userns for the container only
sudo docker build -t sc-lab:tools runner/              # every download checked by hash
sudo sh runner/lab.sh sandbox-runtime /tmp/out          # or nono, codex, landrun, tartaros
python3 runner/report.py /tmp/out results/$(date +%F)-mine
```

`lab.sh` takes contract ids after the output folder to run only those. `/tmp/out/<sandbox>.json`
holds every case: what each phase ran, its exit status, its output and the effect observed.
`report.py` turns it into a run folder like the published ones.

## 3. The contracts that need a witness host

Masked-credential contracts reach a witness by name through the sandbox's proxy, on a
second host of the lab network ([Witnesses](../concepts/witnesses.md)):

```sh
sudo sh runner/lab-witness.sh up
sudo SC_WITNESS=1 sh runner/lab.sh tartaros /tmp/out
sudo sh runner/lab-witness.sh down
```

Without it those contracts are `not-applicable`.
