# Security and disclosure

This lab measures sandboxes. A measured result can amount to a vulnerability
report about the sandbox under test, so disclosure is handled with care.

## Findings about a measured sandbox

When a run shows a sandbox failing a contract in a way that is a real security
weakness, the finding goes to **that sandbox's own project first**, through its
published security channel, not into this repository. Until the vendor has had a
chance to respond and authorizes disclosure, nothing about it is published here:
not the result, and not that a result exists. Marking a cell "withheld" would
point at the sandbox and the contract, and since contracts are runnable, anyone
could reproduce the finding from that pointer. So while a disclosure is open, the
contracts involved are held out of the published corpus and out of every
published run, for every sandbox. They are published, with their results, once
the vendor authorizes it.

A result is *not* held back when it reflects documented behaviour, a difference of
defaults, a capability a sandbox does not claim, or a weakness the vendor has
already made public. Those are published in full with a link to the public
record.

## Reporting a problem with the lab itself

For a problem with the lab — a contract that is wrong or unfair, a runner or
adapter bug, a mis-attributed `source`, or a result you cannot reproduce — open
a GitHub issue. If the problem is that a published result discloses something it
should not, please report it privately to the maintainer rather than opening a
public issue, so it can be taken down before it spreads.

## Running the contracts

The contracts are attacks. Run them only in a disposable environment (a
throwaway container or VM), never on a workstation or a host you care about.
See `runner/README.md`.
