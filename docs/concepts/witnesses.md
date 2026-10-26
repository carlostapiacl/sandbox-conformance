# Witnesses

Some effects happen on the wire, not on disk. The runner starts witness servers for a
contract (`[[server]]`) and the assert reads what they received.

- A witness can log each request head, the paths asked for (normalised as a server would
  route them) or the whole request with its body, and answer with what it received, so
  the agent sees what reached the upstream.
- `bind = "{host_ip}"` puts a witness on the host's own address, one a sandboxed process
  must not reach.
- `[[host_alias]]` resolves a name to an address for one case, in `/etc/hosts`.

## TLS witnesses

A witness with `tls = true` and a `name` speaks TLS for that host, with a certificate
signed by a CA the runner makes for the run. Several share one address and each
connection is served by the one its server name asks for. The launcher trusts that CA, as
it would trust a site-local one.

## The witness host

A sandbox's egress proxy may refuse names that resolve to the sandbox's own host, or to
internal addresses, which is a defence of its own and not what a contract about
credentials tests. So those contracts reach their witness through a second container on a
lab network in TEST-NET-2 (`198.51.100.0/24`), an address range no such guard treats as
internal, which forwards to the runner. They declare `requires = ["witness-host"]` and are
`not-applicable` on a host without it ([Quickstart](../get-started/quickstart.md#3-the-contracts-that-need-a-witness-host)).

## The reference broker

With no sandbox there is no credential broker, so the baseline of a `[broker]` contract
runs against [a reference one](repo:runner/reference_broker.py) written the obvious way:
no token check, every agent header forwarded, the prefix matched as a string, redirects
followed. It is the same for every sandbox. An attack that does not get through it is
`vacuous`.
