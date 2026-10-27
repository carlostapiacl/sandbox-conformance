# Comparison, run of 2026-10-15

Each cell is the result of one contract against one sandbox, set up through its adapter (`runner/adapters/`) as strictly as that sandbox's documentation allows. Only results I actually measured are listed. The host and the method are described in `README.md`.

| result | meaning |
|---|---|
| `contained` | the attack failed and the legitimate control still worked |
| `escaped` | the attack succeeded under the sandbox |
| `control-broke` | the attack failed, and so did the legitimate control |
| `unsupported` | the sandbox cannot express a `[policy]` field: a missing feature, not a vulnerability |
| `vacuous` | the attack fails on this host even without a sandbox, so the result proves nothing |
| `needs-feature` | the runner or the adapter cannot provide something the contract needs |
| `n/a` | macOS-only contract, or the host lacks something the contract requires |

Marks after a result:

- `*`: no `[policy]` field asks for this guarantee, so the result reflects the sandbox's defaults. An escape marked this way is a difference of defaults, not a configured rule that failed.
- `‡`: the contract counts this as an attack, but given how the sandbox is built it is not a breach. The notes below say why.
- `§`: the result depends on a newer kernel than this host's (Landlock ABI 6).

## Totals

| result | sandbox-runtime | nono | codex |
|---|---|---|---|
| contained | reported | 31 | 74 |
| escaped | reported | 33 | 24 |
| control-broke | reported | 6 | 27 |
| unsupported | reported | 74 | 18 |
| vacuous | reported | 7 | 8 |
| needs-feature | reported | 1 | 1 |
| not-applicable | reported | 12 | 12 |
| invalid-contract | reported | 0 | 0 |

sandbox-runtime: findings reported to the vendor; its results will be published once they are fixed.

## Per contract

| contract | category | sandbox-runtime | nono | codex |
|---|---|---|---|---|
| `credentials-broker-auth-required` | credentials | reported | unsupported | unsupported |
| `credentials-broker-injected-header-not-overridable` | credentials | reported | unsupported | unsupported |
| `credentials-broker-method-denied` | credentials | reported | unsupported | unsupported |
| `credentials-broker-no-redirect-follow` | credentials | reported | unsupported | unsupported |
| `credentials-broker-prefix-scope` | credentials | reported | unsupported | unsupported |
| `credentials-broker-token-not-forwarded` | credentials | reported | unsupported | unsupported |
| `filesystem-chmod-outside` | filesystem | reported | escaped | contained |
| `filesystem-command-cwd-not-writable` | filesystem | reported | contained | contained |
| `filesystem-deny-ancestor-rename` | filesystem | reported | unsupported | contained |
| `filesystem-rename-into-territory` | filesystem | reported | contained | contained |
| `filesystem-rename-out-of-territory` | filesystem | reported | contained | contained |
| `filesystem-rm-under-read-deny-ancestor` | filesystem | reported | unsupported | contained |
| `filesystem-single-file-grant` | filesystem | reported | contained | control-broke |
| `filesystem-tmp-shm-not-shared` | filesystem | reported | contained | contained |
| `filesystem-truncate-outside` | filesystem | reported | contained | contained |
| `filesystem-unlink-outside` | filesystem | reported | contained | contained |
| `filesystem-utime-outside` | filesystem | reported | escaped | contained |
| `filesystem-writable-root-move-across-roots` | filesystem | reported | unsupported | contained |
| `filesystem-writable-root-replace` | filesystem | reported | control-broke | control-broke |
| `filesystem-write-deny-absent-path` | filesystem | reported | unsupported | contained |
| `filesystem-write-deny-rename-bypass` | filesystem | reported | unsupported | contained |
| `filesystem-write-deny-symlink-alias` | filesystem | reported | unsupported | contained |
| `filesystem-write-deny-truncate-unlink` | filesystem | reported | unsupported | contained |
| `filesystem-write-deny-unlink-recreate` | filesystem | reported | unsupported | contained |
| `filesystem-write-deny-via-symlink-spelling` | filesystem | reported | unsupported | control-broke |
| `filesystem-write-reallow-inside-deny` | filesystem | reported | unsupported | contained |
| `filesystem-write-system-paths` | filesystem | reported | vacuous | vacuous |
| `filesystem-xattr-outside` | filesystem | reported | escaped | contained |
| `fs-dangling-symlink-create-outside` | filesystem | reported | contained | contained |
| `fs-dotdot-absent-root` | filesystem | reported | control-broke | contained |
| `fs-hardlink-create-write-out` | filesystem | reported | contained | contained |
| `fs-hardlink-widen-write` | filesystem | reported | contained | contained |
| `fs-symlink-dangling-create` | filesystem | reported | contained | contained |
| `fs-symlink-file-out-agent-made` | filesystem | reported | contained | contained |
| `fs-symlink-rename-out` | filesystem | reported | contained | contained |
| `fs-writable-root-symlink-out` | filesystem | reported | escaped | escaped |
| `fs-writable-root-symlink-parent` | filesystem | reported | escaped | escaped |
| `read-allow-writable-carveout-trailing-slash` | filesystem | reported | unsupported | contained |
| `write-deny-absent-deep` | filesystem | reported | unsupported | contained |
| `write-deny-backslash-absent` | filesystem | reported | unsupported | contained |
| `write-deny-covers-nested-root` | filesystem | reported | unsupported | escaped |
| `write-deny-cut-short-hop` | filesystem | reported | unsupported | control-broke |
| `write-deny-dangling-link-target` | filesystem | reported | unsupported | control-broke |
| `write-deny-equals-root` | filesystem | reported | unsupported | contained |
| `write-deny-existing-file-chmod` | filesystem | reported | unsupported | contained |
| `write-deny-glob-chars-dir` | filesystem | reported | unsupported | control-broke |
| `write-deny-link-dotdot` | filesystem | reported | unsupported | control-broke |
| `write-deny-noncanonical-absent` | filesystem | reported | unsupported | contained |
| `write-deny-symlinked-parent` | filesystem | reported | unsupported | control-broke |
| `write-deny-through-policy-symlink` | filesystem | reported | unsupported | control-broke |
| `write-deny-trailing-slash` | filesystem | reported | unsupported | contained |
| `write-deny-under-dotdot-root` | filesystem | reported | unsupported | contained |
| `write-deny-unsearchable-dir` | filesystem | reported | unsupported | contained |
| `ipc-abstract-unix-socket` | ipc | reported | escaped§ | contained |
| `ipc-unix-socket-in-denied-dir` | ipc | reported | unsupported | contained |
| `isolation-clone-newns-denied` | isolation | reported | escaped* | escaped* |
| `isolation-nested-relaunch-no-widen` | isolation | reported | control-broke* | needs-feature |
| `isolation-no-capabilities` | isolation | reported | vacuous | vacuous |
| `isolation-no-effective-caps` | isolation | reported | escaped* | contained* |
| `isolation-no-nested-userns` | isolation | reported | escaped* | escaped* |
| `isolation-no-new-privs` | isolation | reported | contained* | contained* |
| `isolation-pid1-reaper-filtered` | isolation | reported | unsupported | contained* |
| `isolation-proc-mem-launcher-denied` | isolation | reported | vacuous | vacuous |
| `isolation-proc-sys-write-denied` | isolation | reported | vacuous | vacuous |
| `isolation-process-info-environ` | isolation | reported | vacuous | vacuous |
| `isolation-process-info-foreign` | isolation | reported | escaped* | escaped*‡ |
| `isolation-ptrace-launcher-denied` | isolation | reported | vacuous | vacuous |
| `isolation-root-mount-bypass-denied` | isolation | reported | unsupported | vacuous |
| `isolation-seccomp-io-uring-denied` | isolation | reported | contained* | contained* |
| `isolation-signal-host-process` | isolation | reported | escaped*§ | contained* |
| `isolation-supervisor-proc-mem-denied` | isolation | reported | escaped* | escaped* |
| `isolation-vsock-socket-denied` | isolation | reported | contained* | contained* |
| `seccomp-clone-newuser-denied` | isolation | reported | escaped* | escaped* |
| `seccomp-new-mount-api-denied` | isolation | reported | vacuous | vacuous |
| `usability-dev-nodes-and-ipc` | isolation | reported | control-broke* | control-broke* |
| `lifecycle-background-reaped-on-exit` | lifecycle | reported | escaped* | contained* |
| `lifecycle-effect-log-tamper` | lifecycle | reported | needs-feature | unsupported |
| `lifecycle-exit-status-forwarded` | lifecycle | reported | contained* | contained* |
| `lifecycle-no-host-artifacts` | lifecycle | reported | escaped* | escaped* |
| `lifecycle-signal-teardown` | lifecycle | reported | escaped* | escaped* |
| `network-broker-allowlist-lookalike` | network | reported | unsupported | unsupported |
| `network-broker-host-header-spoof` | network | reported | unsupported | unsupported |
| `network-broker-internal-ip-spellings` | network | reported | unsupported | unsupported |
| `network-broker-no-request-smuggling` | network | reported | unsupported | unsupported |
| `network-broker-path-dot-segments` | network | reported | unsupported | unsupported |
| `network-broker-ssrf-internal` | network | reported | unsupported | unsupported |
| `network-broker-survives-malformed-client` | network | reported | unsupported | unsupported |
| `network-domain-allowlist-direct-bypass` | network | reported | contained | contained |
| `network-egress-public-denied` | network | reported | contained | unsupported |
| `network-icmp-denied` | network | reported | contained | contained |
| `network-local-bind-denied` | network | reported | contained | unsupported |
| `network-other-socket-families-denied` | network | reported | contained | control-broke |
| `network-proxy-env-present` | network | reported | contained | contained |
| `network-socket-domain-high-bits` | network | reported | control-broke | control-broke |
| `network-tcp-external-denied` | network | reported | contained | contained |
| `network-vsock-denied` | network | reported | contained | contained |
| `seccomp-io-uring-denied` | network | reported | control-broke | contained |
| `read-allow-inside-deny-writable-ancestor` | secrets | reported | unsupported | control-broke |
| `read-allow-symlink-into-deny` | secrets | reported | unsupported | control-broke |
| `read-allow-symlink-no-reopen` | secrets | reported | unsupported | control-broke |
| `read-allow-trailing-slash-nested-deny` | secrets | reported | unsupported | control-broke |
| `read-deny-alt-spelling` | secrets | reported | unsupported | control-broke |
| `read-deny-around-nested-root` | secrets | reported | unsupported | contained |
| `read-deny-backslash-name` | secrets | reported | unsupported | contained |
| `read-deny-bracket-dir` | secrets | reported | unsupported | control-broke |
| `read-deny-given-via-symlink` | secrets | reported | unsupported | control-broke |
| `read-deny-link-dotdot` | secrets | reported | unsupported | contained |
| `read-deny-not-reopened-by-nested-writable` | secrets | reported | unsupported | contained |
| `read-deny-root-carve-out` | secrets | reported | unsupported | control-broke |
| `read-deny-symlink-entry` | secrets | reported | unsupported | control-broke |
| `read-deny-symlinked-dir` | secrets | reported | unsupported | control-broke |
| `read-deny-trailing-slash-nested-write-deny` | secrets | reported | unsupported | contained |
| `read-deny-under-write-deny` | secrets | reported | unsupported | contained |
| `secrets-env-loader-injection-inherit` | secrets | reported | contained | escaped‡ |
| `secrets-env-loader-injection-scrub` | secrets | reported | contained* | contained* |
| `secrets-env-passthrough-selective` | secrets | reported | contained | contained |
| `secrets-env-scrub-common-tokens` | secrets | reported | contained* | contained* |
| `secrets-home-credentials-in-writable` | secrets | reported | unsupported | contained |
| `secrets-host-process-environ` | secrets | reported | contained | contained |
| `secrets-proc-host-process-links` | secrets | reported | contained* | contained* |
| `secrets-read-allow-symlink-hop-no-widen` | secrets | reported | unsupported | control-broke |
| `secrets-read-allow-symlink-into-deny` | secrets | reported | unsupported | control-broke |
| `secrets-read-deny-after-chmod` | secrets | reported | unsupported | contained |
| `secrets-read-deny-also-write-denied` | secrets | reported | unsupported | contained |
| `secrets-read-deny-dir-listing` | secrets | reported | unsupported | contained |
| `secrets-read-deny-on-symlinked-path` | secrets | reported | unsupported | control-broke |
| `secrets-read-deny-path-special-chars` | secrets | reported | unsupported | contained |
| `secrets-read-deny-prefix-collision` | secrets | reported | unsupported | contained |
| `secrets-read-deny-rename-out` | secrets | reported | unsupported | contained |
| `secrets-read-deny-single-file` | secrets | reported | unsupported | contained |
| `secrets-read-deny-symlinked-entry` | secrets | reported | unsupported | control-broke |
| `secrets-read-deny-under-write-denied-ancestor` | secrets | reported | unsupported | contained |
| `trust-handoff-bracketed-root` | trust-handoff | reported | unsupported | control-broke |
| `trust-handoff-claude-agents` | trust-handoff | reported | escaped* | escaped* |
| `trust-handoff-claude-symlink-cycle` | trust-handoff | reported | unsupported | unsupported |
| `trust-handoff-editor-dirs` | trust-handoff | reported | escaped* | escaped* |
| `trust-handoff-git-config` | trust-handoff | reported | escaped* | escaped* |
| `trust-handoff-git-config-move-aside` | trust-handoff | reported | escaped* | contained* |
| `trust-handoff-git-dir-replace` | trust-handoff | reported | escaped* | contained* |
| `trust-handoff-git-exchange-rename` | trust-handoff | reported | escaped* | contained* |
| `trust-handoff-gitdir-pointer` | trust-handoff | reported | escaped* | contained* |
| `trust-handoff-gitignored-repo` | trust-handoff | reported | escaped* | escaped* |
| `trust-handoff-gitmodules` | trust-handoff | reported | escaped* | escaped* |
| `trust-handoff-hooks-dir-absent` | trust-handoff | reported | escaped* | escaped* |
| `trust-handoff-repo-created-in-run` | trust-handoff | reported | escaped* | escaped* |
| `trust-handoff-root-inside-hooks` | trust-handoff | reported | escaped* | escaped* |
| `trust-handoff-shell-rc` | trust-handoff | reported | escaped* | escaped* |
| `trust-handoff-symlink-absent-parent` | trust-handoff | reported | unsupported | unsupported |
| `trust-handoff-symlinked-claude-dir` | trust-handoff | reported | escaped* | escaped* |
| `trust-handoff-tool-rc` | trust-handoff | reported | escaped* | escaped* |
| `trust-handoff-unreadable-at-compile` | trust-handoff | reported | escaped* | escaped* |
| `trust-handoff-worktree-gitfile` | trust-handoff | reported | escaped* | escaped* |

Not applicable on this host for every sandbox (12): `ipc-unix-bind-denied`, `ipc-unix-socket-alias`, `ipc-unix-socket-allowlist`, `isolation-apple-events-denied`, `isolation-gpu-node-denied`, `resources-cgroup-escape`, `secrets-glob-deny-created-after-start`, `secrets-glob-deny-rename-out`, `secrets-glob-read-deny`, `secrets-read-deny-case-fold`, `secrets-read-deny-clonefile`, `secrets-read-deny-firmlink`.

## Review notes

I read the raw output (`raw/`) for every result other than `contained`. These notes explain a result; they never change it.

### nono

- `filesystem-chmod-outside` (confirmed): Measured with a read grant on the test tree (the neutral read-everything baseline). Landlock does not mediate chmod/utime/xattr, so a readable file's metadata can be changed. Under nono's own idiom (no grant at all) the file would be unreachable.
- `filesystem-utime-outside` (confirmed): As filesystem-chmod-outside.
- `filesystem-xattr-outside` (confirmed): As filesystem-chmod-outside.
- `fs-writable-root-symlink-out` (confirmed): A writable root that is itself a symlink pointing outside the other roots was followed, so its target became writable. The contract pins a policy decision (refuse such a root); the sandbox does not make it.
- `fs-writable-root-symlink-parent` (confirmed): A writable root that is itself a symlink pointing outside the other roots was followed, so its target became writable. The contract pins a policy decision (refuse such a root); the sandbox does not make it.
- `ipc-abstract-unix-socket` (kernel-dependent): Abstract-socket scoping needs Landlock ABI 6 (kernel 6.12+); this host has ABI 4 and nono logs it as unavailable.
- `isolation-signal-host-process` (kernel-dependent): Signal scoping needs Landlock ABI 6 (kernel 6.12+); this host has ABI 4.
- `lifecycle-background-reaped-on-exit` (confirmed): A background child outlived the sandboxed command and wrote the marker.
- `lifecycle-signal-teardown` (confirmed): SIGTERM to the launcher ended it (143), but the sandboxed tree survived and wrote the marker.

### codex

- `fs-writable-root-symlink-out` (confirmed): A writable root that is itself a symlink pointing outside the other roots was followed, so its target became writable. The contract pins a policy decision (refuse such a root); the sandbox does not make it.
- `fs-writable-root-symlink-parent` (confirmed): A writable root that is itself a symlink pointing outside the other roots was followed, so its target became writable. The contract pins a policy decision (refuse such a root); the sandbox does not make it.
- `isolation-process-info-foreign` (contract-assumption): /proc/1 inside codex's sandbox is its own init in a private PID namespace, not a host process.
- `lifecycle-signal-teardown` (confirmed): After SIGTERM to `codex sandbox`, the sandboxed tree kept running and wrote the marker.
- `read-deny-symlink-entry` (confirmed): Fails closed: bwrap cannot mount over a deny entry that is a symlink, so nothing runs.
- `secrets-env-loader-injection-inherit` (contract-assumption): The policy asks to inherit the launcher's whole environment, and the sandbox did exactly that (LD_PRELOAD/BASH_ENV passed). The contract's own comment calls stripping loader variables even under inherit-all a design decision still to be made, not an established guarantee.
- `write-deny-covers-nested-root` (confirmed): A writable root nested inside a write-denied directory stayed writable; codex resolves overlapping entries by the most specific path.

## Upstream status

Where each finding stands in the sandbox's own project, checked against its public issues, pull requests and commits. "Fixed in" names the first release with the fix, or the commit on the default branch when no release has it yet. The results above were measured on the versions in `README.md`.

### nono

| finding | contracts | status | fixed in | references |
|---|---|---|---|---|
| Landlock does not mediate chmod, utime or xattr, so a readable file's metadata can be changed | `filesystem-chmod-outside`, `filesystem-utime-outside`, `filesystem-xattr-outside` | open | not fixed (latest v0.80.0) | [#914](https://github.com/nolabs-ai/nono/issues/914) |
| Abstract unix sockets and signals are not scoped below Landlock ABI 6 | `ipc-abstract-unix-socket`, `isolation-signal-host-process` | kernel-dependent | n/a: needs kernel 6.12+ (Landlock ABI 6); nono logs it as unavailable | none found |
| A writable root that is a symlink pointing outside the other roots is followed | `fs-writable-root-symlink-out`, `fs-writable-root-symlink-parent` | by design | documented: every granted path is canonicalized and symlinks are resolved before the sandbox is applied (docs/cli/usage/flags.mdx, Path Resolution) | none found |
| A background child outlives the command, and the sandboxed tree survives SIGTERM to the launcher | `lifecycle-background-reaped-on-exit`, `lifecycle-signal-teardown` | outside the security model | not a vulnerability by nono's model: descendants inherit the Landlock restrictions and cannot remove them; tearing down the tree on exit or SIGTERM is not a documented guarantee. At most a public feature request | none found |

### codex

| finding | contracts | status | fixed in | references |
|---|---|---|---|---|
| An entry that is a symlink, goes through one, or names an absent path stops the sandbox from starting | `read-deny-symlink-entry`, `read-deny-given-via-symlink`, `secrets-read-deny-symlinked-entry`, `secrets-read-deny-on-symlinked-path`, `read-deny-alt-spelling` | open | not fixed (latest stable rust-v0.162.1) | [#52658](https://github.com/openai/codex/issues/52658), [#54110](https://github.com/openai/codex/issues/54110), [#53350](https://github.com/openai/codex/issues/53350) |
| A writable root that is a single file stops the sandbox from starting | `filesystem-single-file-grant` | open | not fixed (latest stable rust-v0.162.1) | [#49755](https://github.com/openai/codex/issues/49755) |
| After SIGTERM to the launcher the sandboxed tree keeps running | `lifecycle-signal-teardown` | open (related) | not fixed | [#21994](https://github.com/openai/codex/issues/21994) |
| A writable root that is a symlink pointing outside the other roots is followed | `fs-writable-root-symlink-out`, `fs-writable-root-symlink-parent` | design question | not a vulnerability by codex's docs: the writable root is chosen by the operator; symlink handling is undocumented | none found |
| A writable root nested inside a write-denied directory stays writable | `write-deny-covers-nested-root` | by design | documented: "More specific entries override broader entries" and a more specific path can reopen a subtree inside a broader deny (learn.chatgpt.com/docs/permissions) | none found |

