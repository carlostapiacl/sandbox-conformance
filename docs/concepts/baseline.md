# Baseline and control

A case runs twice from a fresh state. The **baseline** runs the attack and the control
with no sandbox. The **sandboxed** phase runs them under the sandbox.

The baseline is what makes a `contained` mean something. If the attack does not work on
this host without a sandbox, blocking it proves nothing, and the case is `vacuous`. If
the control fails without a sandbox, the contract is at fault and the case is
`invalid-baseline`, unless the contract declares why the control needs the sandbox
(`control_requires_sandbox`, for a control that talks to the sandbox's proxy).

The control is what stops a sandbox that blocks everything from passing. A sandbox that
stops the attack by breaking the control gets `control-broke`, not `contained`. It runs
after the attack in the same phase, so it must not depend on anything a working attack
may change.

When the guarantee needs a counterpart that only exists inside a sandbox, such as a
credential broker, the baseline runs against a reference one written with none of the
defences under test. An attack that does not get through the reference is `vacuous`
too ([Witnesses](witnesses.md#the-reference-broker)).

The lab checks its own baselines against [reference sandboxes](repo:runner/reference):
an allow-all one under which every attack must escape and a deny-all one under which
every control must break.
