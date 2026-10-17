# Contributing

Two kinds of contribution: a **contract** (a guarantee to measure) and an
**adapter** (a sandbox to measure it against). Everything in the repo is in
English.

## Adding a contract

A contract is one TOML file in `contracts/<category>/<id>.toml`. Read
[`spec/format.md`](spec/format.md) first. The rules that keep a result meaningful:

- **Three parts.** `attack` is the forbidden operation, `control` is legitimate work that must still succeed, and `assert` is the real effect checked afterwards (a file is `unchanged`, a planted marker is `absent`). A sandbox that blocks the attack by breaking the control fails the contract.
- **Credit the source.** Every contract re-expresses a guarantee from another project's public test suite and names it in the `source` field. Re-express the guarantee in your own words; do not copy upstream test code.
- **The attack must be real.** It has to succeed *without* a sandbox on the same host, or the runner marks it `vacuous` and it proves nothing. Do not weaken an attack to make it pass.
- **`{root}` is a fresh temporary directory** per run. Keep the control's work inside the writable roots.
- Unknown fields are rejected, so a typo fails loudly instead of passing as a weaker policy.

If a guarantee only makes sense in one sandbox's model, say so rather than
forcing it — a field a sandbox cannot express is a capability gap, not a
vulnerability.

## Adding a sandbox

A sandbox is one module in `runner/adapters/<name>.py`. The engine
(`runner/run.py`), the contracts and the format do not change. The module
exposes:

- `NAME` and `identity()` — the sandbox's name, version, commit and license.
- `check(contract)` — returns the `[policy]` fields this sandbox cannot express as `unsupported` (a capability gap, never a vulnerability), or `needs_feature` when the runner cannot provide something the contract declares.
- `wrap(policy, m, contract, env)` — returns the argv that runs a command under the sandbox, configured the way that sandbox's own documentation recommends for strict confinement. Adapters never read the attack.

Install the tool in `runner/Dockerfile` and run `runner/lab.sh <name>` on a
disposable Linux host. `runner/report.py` discovers the sandbox automatically.

## Measurement discipline

- Configure each sandbox idiomatically for strict confinement.
- A difference of defaults is not a bug; a capability a sandbox does not express is not a vulnerability.
- State nothing you did not run. Unverified numbers are marked `(por confirmar)` / "to be confirmed", never estimated.
- Check every non-`contained` result against the raw output before trusting it.
- Findings about a sandbox follow [`SECURITY.md`](SECURITY.md): the vendor first, then publication.
