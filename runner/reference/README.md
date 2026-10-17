# Reference sandboxes

Fake sandboxes with a known behaviour, used only to test the lab itself
(`runner/tests/`). They are never measured or published. If the lab cannot tell
these apart, its results on real sandboxes cannot be trusted either.

| adapter | behaves like | a correct lab reports |
|---|---|---|
| `ref_allow_all` | no sandbox at all | `escaped` wherever the baseline is valid |
| `ref_deny_all` | a sandbox that starts, then stops every operation | `control-broke`, never `contained` |
| `ref_broken` | a sandbox binary that never starts | `harness-error`, never a measured result |
| `ref_refuser` | refuses a symlinked writable root, with a declared refusal signature; otherwise no confinement | `contained` on the refusal contract |
| `ref_needs_host` | needs a host capability no host has, and would confine nothing without it | `not-applicable`, never a measured result |
| `ref_refuser_unsigned` | refuses the same way, but declares no signature | `inconclusive` on the refusal contract |

They follow the adapter interface of `runner/adapters/` (`NAME`, `identity()`,
`check()`, `wrap()`, optional `REFUSAL`), and run on Linux and macOS without
privileges.
