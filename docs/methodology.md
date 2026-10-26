# Methodology

## What is measured

Whether a sandbox holds a guarantee when the agent inside it tries to break it. The agent
is assumed compromised: each attack is executed as written, by a process confined by the
sandbox, and the lab observes whether its effect happened on the host. How often a real
agent gets compromised, by a prompt injection for example, is a different question that
benchmarks such as [AgentDojo](https://agentdojo.spylab.ai/) measure.

Out of scope: escapes from the kernel or a hypervisor, side channels, and denial of
service beyond the resource limits a contract states. The lab hosts are disposable VMs
with a known kernel, adequate for attacks that try to leave the sandbox inside the guest.

## How a case is decided

Every case runs a baseline with no sandbox and a sandboxed phase, each from a fresh
state. The [decision procedure](reference/verdicts.md#4-decision-procedure) turns what
they observed into a result mechanically, and [the lab tests](repo:runner/tests) check it
rule by rule against reference sandboxes. A reviewer adds a reading afterwards, and it
never changes the result.

## Comparing runs

A row of [All runs](results/index.md) is one sandbox version, one host, one profile, one
corpus version and one verdicts version. Results are not summed, averaged or ranked
across rows that differ in any of these, and no single score across sandboxes is
published. Counts are per result, and escapes are broken down by reading, so a confirmed
finding reads apart from a contract assumption or a known limit.

## Configuring each sandbox

Each sandbox runs through an adapter configured the way its own documentation recommends
for strict confinement. A field it cannot express is reported as `unsupported`, a
capability gap, never as a vulnerability. A difference of defaults is labelled as such
(`basis: default`).

## Evidence

Every case records the commands run, their exit statuses, bounded output, the effect
observed, the contract's hash, the adapter's hash, the hash of the sandbox binary, and the
host's detected capabilities and container options. The raw record of each run is
published with it.

## Conflict of interest

TartarOS, one of the sandboxes measured, started together with this lab, by the same
author. It is where the variants the lab finds are tried, one by one, to see whether
each can be mitigated; the lab is what says whether it was. To keep that from shaping
the results:

- the contracts come from other projects' test suites, each credited;
- the corpus was frozen before TartarOS was first measured, and every later change to a
  contract is logged with its reason in the [changelog](changelog/contracts.md) and moves
  the [corpus version](concepts/corpus-versions.md), so a contract changed after a result
  shows up;
- TartarOS's results and page state the conflict, and its result files carry
  `conflict_of_interest`.

## Disclosure

A weakness found in a sandbox goes to that project first. While a disclosure is open,
nothing about it is published, not even that a result is withheld, because a contract is
runnable and the mark alone would reproduce it. The contracts involved are held out of the
published corpus and of every run until the disclosure closes
([verdicts §9](reference/verdicts.md#9-disclosure)).
