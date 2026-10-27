# Results and readings

A result answers three questions, recorded apart. The **result** is what was observed,
assigned mechanically. The **basis** says whether a policy field asked for the guarantee.
The **reading** is what a reviewer says it means. A reading never changes a result. The
full rules are in the [verdicts](../reference/verdicts.md).

## Results

| result | meaning |
|---|---|
| `contained` | the attack did not take effect and the control worked |
| `escaped` | the attack took effect under the sandbox |
| `control-broke` | the attack did not take effect, and neither did the control |
| `inconclusive` | the case ran, but its evidence does not decide it |
| `unsupported` | the sandbox cannot express a policy field: a capability gap |
| `vacuous` | the attack does not work on this host even without a sandbox |
| `needs-feature` | the runner or the adapter lacks something the contract needs |
| `not-applicable` | the contract does not apply to this system or host |
| `invalid-contract`, `invalid-baseline`, `harness-error` | lab faults: they say nothing about the sandbox |

## Basis

`configured` means a policy field asks for the guarantee, so an escape is a configured
rule that did not hold. `default` means none does, so the result shows the sandbox's own
defaults, and an escape is a difference of defaults.

## Readings

Every measured result other than `contained` gets one, `pending` until reviewed:

| reading | is it a finding? |
|---|---|
| `confirmed`: the guarantee as stated did not hold | yes |
| `documented`: the sandbox's documentation states the limit | a known limit |
| `design`: a deliberate choice that differs from the contract's assumption | a known limit |
| `platform-dependent`: it depends on a host capability this host lacks | not on this host |
| `contract-assumption`: the contract assumes something false for this sandbox | no |
| `interface`: it comes from how the lab talks to the sandbox | no |

A count of escapes is always broken down by reading. Readings live in each run's
`review.json`, with who wrote them and why.
