# Run of 2026-11-08: nono 0.81.0 with its namespaces

nono 0.81.0 added opt-in Linux namespaces ([NEP-0004](https://github.com/nolabs-ai/nono/pull/2145),
`--isolate net,ipc,uts`). The [2026-11-08 run](../2026-11-08/README.md) measured 0.81.0 without
them. The adapter now asks for as many as each policy allows, as it does with the rest of nono's
configuration: net, ipc and uts, or ipc and uts when the policy grants local ports (`net` cannot
be combined with a direct port grant). nono has no PID or mount namespace.

Same host, image and witness network as the 2026-11-08 run; runner commit `43effe3`, which
changes only [`runner/adapters/nono.py`](../../runner/adapters/nono.py). 196 contracts.

| result | nono 0.81.0 without namespaces | with |
|---|---|---|
| contained | 50 | 51 |
| escaped | 37 | 36 |
| control-broke | 5 | 5 |
| unsupported | 83 | 83 |
| vacuous | 8 | 8 |

One result changes: `ipc-abstract-unix-socket` (critical) goes from escaped to **contained**. An
abstract unix socket belongs to a network namespace, so with `net` the agent can no longer reach
one the host listens on. Every other contract gives the same result, and every other escape keeps
its reading ([`review.json`](review.json)).

In [`../versions.md`](../versions.md) this shows as a change from 0.80.0 to 0.81.0: the namespaces
exist only from 0.81.0.
