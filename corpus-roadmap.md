# Corpus roadmap

Where the contracts come from now, and the sandboxes whose public test suites I
could harvest next. A contract is never a copy of upstream test code: it
re-expresses the guarantee under test in the neutral format and credits its
`source`. Licenses are listed for attribution, not because code is copied.

Status: **harvested** = contracts are in `contracts/`; **candidate** = a public
test suite I have assessed but not yet harvested.

Model fit: **fits** = process / filesystem / network policy with a real on-disk
or on-the-wire effect to assert (the lab's model); **cap** = a capability /
WASM runtime whose test asserts an error code or exit status, not a host effect;
**vm** = a micro-VM / VM where only a sub-layer (jailer, seccomp) fits; **ast** =
an in-process language restriction with no disk/wire effect.

## Harvested (corpus v1.1: 196 contracts)

Counts include the by-omission variants, under the source of the contract they vary.
[`SOURCES.md`](SOURCES.md) lists every contract.

| source | license | contracts | notes |
|---|---|---|---|
| [anthropics/sandbox-runtime](https://github.com/anthropics/sandbox-runtime) | Apache-2.0 | 135 | `test/sandbox/*` |
| [nolabs-ai/nono](https://github.com/nolabs-ai/nono) | Apache-2.0 | 38 | Rust tests + integration shell |
| [openai/codex](https://github.com/openai/codex) | Apache-2.0 | 18 | `codex-rs/linux-sandbox`, sandboxing tests |
| [denoland/deno](https://github.com/denoland/deno) | MIT | 2 | `tests/specs/permission/`; the rest test Deno's own runtime APIs (imports, Node compatibility, prompts), not a guarantee an OS sandbox gives |
| [OpenHands/software-agent-sdk](https://github.com/OpenHands/software-agent-sdk) | MIT | 2 | path traversal |
| [containers/bubblewrap](https://github.com/containers/bubblewrap) | LGPL-2.1+ | 1 | one guarantee so far; `tests/` has more |

## Candidates (assessed 2026-10-15, read-only)

Ranked by harvestable count × agent-relevance × permissive license.

### Tier 1 — harvest first

| project | license | test suite | ~count | fit | fills |
|---|---|---|---|---|---|
| [OpenHands/software-agent-sdk](https://github.com/OpenHands/software-agent-sdk) | MIT | `tests/agent_server/`, `tests/sdk/`, `tests/cross/` | many | fits | **partially harvested** (2: path traversal). Remaining agent-specific tests — credential broker, secret masking/scope, `.mcp.json` planting, approval — are agent-framework controls, not sandbox FS/net policy, so they are out of scope for a sandbox-conformance contract (noted here, not harvested) |
| [superradcompany/microsandbox](https://github.com/superradcompany/microsandbox) | Apache-2.0 | `crates/filesystem/.../tests/`, `crates/network/` | ~60 | vm (tests fit) | FS confinement (symlink-root escape refused), **egress with a real exfil assert**, port allowlist, readonly, quota |
| [vndee/llm-sandbox](https://github.com/vndee/llm-sandbox) | MIT | `tests/` | ~several | fits | agent-domain: reverse-shell / `/etc/passwd` reads flagged, tar-traversal (symlink/device members), install-arg allowlist, MCP |

### Tier 2 — strong, or capability-model asserts

| project | license | test suite | ~count | fit | fills |
|---|---|---|---|---|---|
| [torvalds/linux landlock selftests](https://github.com/torvalds/linux/tree/master/tools/testing/selftests/landlock) | GPL-2.0 | `tools/testing/selftests/landlock/` | ~10 files | fits | the primitive codex/srt use. Abstract unix sockets, signals and ptrace are covered already (2026-10-26); left: rename/link across domains, net ports |
| [opencontainers/runc](https://github.com/opencontainers/runc) | Apache-2.0 | `tests/integration/` | 61 `.bats` | fits | masked/readonly paths, seccomp errno, capabilities bounding, userns, rlimits — asserts on real effect |
| [youki-dev/youki](https://github.com/youki-dev/youki) | Apache-2.0 | `tests/contest/.../tests/` | 59 | fits | `prohibit_symlink`, masked/readonly paths, capabilities, seccomp-notify, hooks lifecycle |
| [google/gvisor](https://github.com/google/gvisor) | Apache-2.0 | `test/syscalls/linux/` | ~290–338 | fits | deepest syscall corpus: chroot, capabilities, bind/connect, iptables egress, rename; framed as POSIX parity, no agent cases |
| [bytecodealliance/wasmtime](https://github.com/bytecodealliance/wasmtime) + [WebAssembly/wasi-testsuite](https://github.com/WebAssembly/wasi-testsuite) | Apache-2.0 | `crates/test-programs/`, wasi-testsuite `tests/` | 300+ / ~200 | cap | capability FS (preopens) + net; `..` escapes, nofollow, no-TCP-without-capability; assert is a WASI error code |
| [landlock-lsm/go-landlock](https://github.com/landlock-lsm/go-landlock) | MIT | `landlock/*_test.go` | ~6 files | fits | clean kernel FS r/w + net port allow/deny |
| [google/minijail](https://github.com/google/minijail) | BSD-3-Clause | `*_unittest.cc` | small | fits | seccomp filter generation/application, cap drop, mounts |
| [google/nsjail](https://github.com/google/nsjail) | Apache-2.0 | `tests/` | small | fits | network drop/NAT, path containment, seccomp |

### Tier 3 — partial / different model / niche

| project | license | why it is lower | fit |
|---|---|---|---|
| [containers/crun](https://github.com/containers/crun) | GPL-2.0 | same guarantees as runc; use as cross-check | fits |
| [netblue30/firejail](https://github.com/netblue30/firejail) | GPL-2.0 | huge (`test/` ~387) but Expect-script asserts, copyleft | fits |
| [systemd/systemd](https://github.com/systemd/systemd) | GPL-2.0 | `test/test-execute/` catalogs what to isolate; asserts are internal | fits (catalog) |
| [bytecodealliance] libseccomp | LGPL-2.1 | validates generated BPF, not runtime "agent must not X" | — |
| [cloudflare/workerd](https://github.com/cloudflare/workerd) | Apache-2.0 | isolate bindings; tests are functional, not attack/deny | vm/isolate |
| [zopefoundation/RestrictedPython](https://github.com/zopefoundation/RestrictedPython) | ZPL | forbidden imports/builtins; no disk/wire assert | ast |
| [pyodide/pyodide](https://github.com/pyodide/pyodide) | MPL-2.0 | FS mount confinement; tests assert function, not denial | cap/wasm |
| [firecracker-microvm/firecracker](https://github.com/firecracker-microvm/firecracker) | Apache-2.0 | only the jailer + seccomp subset fits; a different isolation tier | vm |

### No usable corpus (verified)

- **e2b-dev** (Apache-2.0): tests are control-plane only (secrets volume, auth, lifecycle); no in-guest confinement tests (Firecracker VM).
- **daytonaio/daytona**: archived 2026-07-24; core went closed-source; no security tests.
- **modal-labs**, **Morph**, **Northflank**: client SDKs only; the real sandbox is closed-source.

## Priorities

1. **OpenHands** — the only source of agent-specific guarantees (`.mcp.json` / git-hook / shell-rc planting, credential broker handoff, approval/trust, secret masking). This dimension is essentially uncovered everywhere else; systematizing it is what would make the lab distinctive. Verified test files include `tests/agent_server/test_credential_binding.py`, `tests/cross/test_secret_masking_tool_payloads.py`, `tests/agent_server/test_mcp_router.py`, the planting fixture `tests/fixtures/plugins/agent_plugins/wrong-locations/.mcp.json`, and `tests/sdk/io/test_local_filestore_security.py`.
2. **microsandbox + llm-sandbox** — FS confinement, egress with real exfil asserts, and more agent-domain attacks.
3. **runc + youki + landlock selftests**: near 1:1 mapping and permissive licenses, but most of what they add (abstract sockets, signals, ptrace, masked `/proc` paths) is covered already; what is left is rename/link across domains, net ports and rlimits.
4. **gVisor + wasi-testsuite** — deep veins to mine later; gVisor is heavy (C++ syscall conformance), WASI asserts are capability error codes.

## A note on assert fidelity

For **cap** and **vm** corpora, anchor the `assert` to what that suite actually
observes — a WASI error code, an exit status, a policy-denied result — not to a
host disk/wire state the runtime never exposes. Mixing the two would overstate
what was measured.
