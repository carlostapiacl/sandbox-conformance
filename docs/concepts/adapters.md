# Adapters and profiles

An adapter is one module in [repo:runner/adapters](repo:runner/adapters) that translates a
contract's neutral policy into one sandbox's configuration and command line. It never
reads the attack. It does three things:

- `identity()` records the sandbox's name, version, commit, license and the hash of the
  binary that ran.
- `check(contract)` names the policy fields the sandbox cannot express (`unsupported`) or
  the lab cannot provide (`needs-feature`).
- `wrap(...)` builds the command that runs a phase under the sandbox.

The engine, the contracts and the format do not change when a sandbox is added. Each
sandbox has a page saying how its adapter maps every field: [Sandboxes](../sandboxes/index.md).

## Profiles

The policy says what a contract asks for. A sandbox usually has options the policy does
not mention, and the profile says how the adapter sets them. `strict` sets each to the
most restrictive value the sandbox's own documentation supports that still lets the
control run. `default` leaves the sandbox's defaults. Every published run so far is
`strict`, and every row of [All runs](../results/index.md) names its profile.
