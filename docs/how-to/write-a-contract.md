# Write a contract

1. **Find the guarantee in a public test suite.** The lab measures claims sandboxes make
   about themselves, so a contract starts from another project's test and names it in
   `source`. Candidate suites are in [repo:corpus-roadmap.md](repo:corpus-roadmap.md).
2. **Write it in neutral terms** in `contracts/<category>/<id>.toml`: the policy, the
   fixtures, an attack that must not take effect, a control that must keep working, and
   the effect to assert ([Contracts](../concepts/contracts.md), [format](../reference/format.md)).
3. **Make the attack real.** Run it with no sandbox: it has to work, or the case is
   `vacuous`. Never weaken an attack to make a sandbox pass.
4. **Keep the control independent of the attack.** It runs after the attack, so it must
   not need anything a working attack changes.
5. **Say what decides it.** When an exit status is the evidence, declare `expect_exit`
   and, if the attack can exit with its blocked status for another reason, `blocked_exit`.
   Declare `requires` for host capabilities and `os` for the systems it applies to.
6. **Write the next corpus version** in the same pull request:

    ```sh
    python3 runner/corpus.py build 1.1
    ```

    and add a line to [repo:contracts/CHANGES.md](repo:contracts/CHANGES.md) saying why.
    The lab tests run `corpus.py check` and fail otherwise
    ([Corpus versions](../concepts/corpus-versions.md)).
7. **Run the lab tests** (`python3 -m unittest discover -s runner/tests`): the reference
   sandboxes check that an allow-all sandbox escapes your attack and a deny-all one breaks
   your control.

A guarantee that only makes sense in one sandbox's model is stated as such, not forced:
a field a sandbox cannot express is a capability gap, never a vulnerability.
