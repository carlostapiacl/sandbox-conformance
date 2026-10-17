# Comparison, run of 2026-10-15

Each cell is the result of one contract against one sandbox, set up through its adapter (`runner/adapters/`) as strictly as that sandbox's documentation allows. Only results we actually measured are listed. The host and the method are described in `README.md`.

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
| contained | 99 | 31 | 74 |
| escaped | 22 | 33 | 24 |
| control-broke | 4 | 6 | 27 |
| unsupported | 18 | 74 | 18 |
| vacuous | 8 | 7 | 8 |
| needs-feature | 1 | 1 | 1 |
| not-applicable | 12 | 12 | 12 |
| invalid-contract | 0 | 0 | 0 |

## Per contract

| contract | category | sandbox-runtime | nono | codex |
|---|---|---|---|---|
| `credentials-broker-auth-required` | credentials | unsupported | unsupported | unsupported |
| `credentials-broker-injected-header-not-overridable` | credentials | unsupported | unsupported | unsupported |
| `credentials-broker-method-denied` | credentials | unsupported | unsupported | unsupported |
| `credentials-broker-no-redirect-follow` | credentials | unsupported | unsupported | unsupported |
| `credentials-broker-prefix-scope` | credentials | unsupported | unsupported | unsupported |
| `credentials-broker-token-not-forwarded` | credentials | unsupported | unsupported | unsupported |
| `filesystem-chmod-outside` | filesystem | contained | escaped | contained |
| `filesystem-command-cwd-not-writable` | filesystem | contained | contained | contained |
| `filesystem-deny-ancestor-rename` | filesystem | contained | unsupported | contained |
| `filesystem-rename-into-territory` | filesystem | contained | contained | contained |
| `filesystem-rename-out-of-territory` | filesystem | contained | contained | contained |
| `filesystem-rm-under-read-deny-ancestor` | filesystem | contained | unsupported | contained |
| `filesystem-single-file-grant` | filesystem | contained | contained | control-broke |
| `filesystem-tmp-shm-not-shared` | filesystem | contained | contained | contained |
| `filesystem-truncate-outside` | filesystem | contained | contained | contained |
| `filesystem-unlink-outside` | filesystem | contained | contained | contained |
| `filesystem-utime-outside` | filesystem | contained | escaped | contained |
| `filesystem-writable-root-move-across-roots` | filesystem | contained | unsupported | contained |
| `filesystem-writable-root-replace` | filesystem | control-broke | control-broke | control-broke |
| `filesystem-write-deny-absent-path` | filesystem | contained | unsupported | contained |
| `filesystem-write-deny-rename-bypass` | filesystem | contained | unsupported | contained |
| `filesystem-write-deny-symlink-alias` | filesystem | contained | unsupported | contained |
| `filesystem-write-deny-truncate-unlink` | filesystem | contained | unsupported | contained |
| `filesystem-write-deny-unlink-recreate` | filesystem | contained | unsupported | contained |
| `filesystem-write-deny-via-symlink-spelling` | filesystem | contained | unsupported | control-broke |
| `filesystem-write-reallow-inside-deny` | filesystem | contained | unsupported | contained |
| `filesystem-write-system-paths` | filesystem | vacuous | vacuous | vacuous |
| `filesystem-xattr-outside` | filesystem | contained | escaped | contained |
| `fs-dangling-symlink-create-outside` | filesystem | contained | contained | contained |
| `fs-dotdot-absent-root` | filesystem | contained | control-broke | contained |
| `fs-hardlink-create-write-out` | filesystem | contained | contained | contained |
| `fs-hardlink-widen-write` | filesystem | contained | contained | contained |
| `fs-symlink-dangling-create` | filesystem | contained | contained | contained |
| `fs-symlink-file-out-agent-made` | filesystem | contained | contained | contained |
| `fs-symlink-rename-out` | filesystem | contained | contained | contained |
| `fs-writable-root-symlink-out` | filesystem | contained | escaped | escaped |
| `fs-writable-root-symlink-parent` | filesystem | contained | escaped | escaped |
| `read-allow-writable-carveout-trailing-slash` | filesystem | contained | unsupported | contained |
| `write-deny-absent-deep` | filesystem | contained | unsupported | contained |
| `write-deny-backslash-absent` | filesystem | contained | unsupported | contained |
| `write-deny-covers-nested-root` | filesystem | contained | unsupported | escaped |
| `write-deny-cut-short-hop` | filesystem | contained | unsupported | control-broke |
| `write-deny-dangling-link-target` | filesystem | escaped | unsupported | control-broke |
| `write-deny-equals-root` | filesystem | contained | unsupported | contained |
| `write-deny-existing-file-chmod` | filesystem | contained | unsupported | contained |
| `write-deny-glob-chars-dir` | filesystem | contained | unsupported | control-broke |
| `write-deny-link-dotdot` | filesystem | control-broke | unsupported | control-broke |
| `write-deny-noncanonical-absent` | filesystem | contained | unsupported | contained |
| `write-deny-symlinked-parent` | filesystem | contained | unsupported | control-broke |
| `write-deny-through-policy-symlink` | filesystem | contained | unsupported | control-broke |
| `write-deny-trailing-slash` | filesystem | contained | unsupported | contained |
| `write-deny-under-dotdot-root` | filesystem | contained | unsupported | contained |
| `write-deny-unsearchable-dir` | filesystem | contained | unsupported | contained |
| `ipc-abstract-unix-socket` | ipc | contained | escaped§ | contained |
| `ipc-unix-socket-in-denied-dir` | ipc | contained | unsupported | contained |
| `isolation-clone-newns-denied` | isolation | escaped* | escaped* | escaped* |
| `isolation-nested-relaunch-no-widen` | isolation | needs-feature | control-broke* | needs-feature |
| `isolation-no-capabilities` | isolation | vacuous | vacuous | vacuous |
| `isolation-no-effective-caps` | isolation | escaped* | escaped* | contained* |
| `isolation-no-nested-userns` | isolation | escaped* | escaped* | escaped* |
| `isolation-no-new-privs` | isolation | contained* | contained* | contained* |
| `isolation-pid1-reaper-filtered` | isolation | escaped* | unsupported | contained* |
| `isolation-proc-mem-launcher-denied` | isolation | vacuous | vacuous | vacuous |
| `isolation-proc-sys-write-denied` | isolation | vacuous | vacuous | vacuous |
| `isolation-process-info-environ` | isolation | vacuous | vacuous | vacuous |
| `isolation-process-info-foreign` | isolation | escaped*‡ | escaped* | escaped*‡ |
| `isolation-ptrace-launcher-denied` | isolation | vacuous | vacuous | vacuous |
| `isolation-root-mount-bypass-denied` | isolation | vacuous | unsupported | vacuous |
| `isolation-seccomp-io-uring-denied` | isolation | contained* | contained* | contained* |
| `isolation-signal-host-process` | isolation | contained* | escaped*§ | contained* |
| `isolation-supervisor-proc-mem-denied` | isolation | contained* | escaped* | escaped* |
| `isolation-vsock-socket-denied` | isolation | escaped* | contained* | contained* |
| `seccomp-clone-newuser-denied` | isolation | escaped* | escaped* | escaped* |
| `seccomp-new-mount-api-denied` | isolation | vacuous | vacuous | vacuous |
| `usability-dev-nodes-and-ipc` | isolation | contained* | control-broke* | control-broke* |
| `lifecycle-background-reaped-on-exit` | lifecycle | contained* | escaped* | contained* |
| `lifecycle-effect-log-tamper` | lifecycle | unsupported | needs-feature | unsupported |
| `lifecycle-exit-status-forwarded` | lifecycle | contained* | contained* | contained* |
| `lifecycle-no-host-artifacts` | lifecycle | contained* | escaped* | escaped* |
| `lifecycle-signal-teardown` | lifecycle | contained* | escaped* | escaped* |
| `network-broker-allowlist-lookalike` | network | unsupported | unsupported | unsupported |
| `network-broker-host-header-spoof` | network | unsupported | unsupported | unsupported |
| `network-broker-internal-ip-spellings` | network | unsupported | unsupported | unsupported |
| `network-broker-no-request-smuggling` | network | unsupported | unsupported | unsupported |
| `network-broker-path-dot-segments` | network | unsupported | unsupported | unsupported |
| `network-broker-ssrf-internal` | network | unsupported | unsupported | unsupported |
| `network-broker-survives-malformed-client` | network | unsupported | unsupported | unsupported |
| `network-domain-allowlist-direct-bypass` | network | contained | contained | contained |
| `network-egress-public-denied` | network | control-broke‡ | contained | unsupported |
| `network-icmp-denied` | network | contained | contained | contained |
| `network-local-bind-denied` | network | escaped‡ | contained | unsupported |
| `network-other-socket-families-denied` | network | escaped | contained | control-broke |
| `network-proxy-env-present` | network | contained | contained | contained |
| `network-socket-domain-high-bits` | network | escaped | control-broke | control-broke |
| `network-tcp-external-denied` | network | escaped‡ | contained | contained |
| `network-vsock-denied` | network | escaped | contained | contained |
| `seccomp-io-uring-denied` | network | contained | control-broke | contained |
| `read-allow-inside-deny-writable-ancestor` | secrets | contained | unsupported | control-broke |
| `read-allow-symlink-into-deny` | secrets | contained | unsupported | control-broke |
| `read-allow-symlink-no-reopen` | secrets | contained | unsupported | control-broke |
| `read-allow-trailing-slash-nested-deny` | secrets | contained | unsupported | control-broke |
| `read-deny-alt-spelling` | secrets | contained | unsupported | control-broke |
| `read-deny-around-nested-root` | secrets | contained | unsupported | contained |
| `read-deny-backslash-name` | secrets | contained | unsupported | contained |
| `read-deny-bracket-dir` | secrets | control-broke | unsupported | control-broke |
| `read-deny-given-via-symlink` | secrets | contained | unsupported | control-broke |
| `read-deny-link-dotdot` | secrets | escaped | unsupported | contained |
| `read-deny-not-reopened-by-nested-writable` | secrets | contained | unsupported | contained |
| `read-deny-root-carve-out` | secrets | contained | unsupported | control-broke |
| `read-deny-symlink-entry` | secrets | contained | unsupported | control-broke |
| `read-deny-symlinked-dir` | secrets | contained | unsupported | control-broke |
| `read-deny-trailing-slash-nested-write-deny` | secrets | contained | unsupported | contained |
| `read-deny-under-write-deny` | secrets | contained | unsupported | contained |
| `secrets-env-loader-injection-inherit` | secrets | escaped‡ | contained | escaped‡ |
| `secrets-env-loader-injection-scrub` | secrets | unsupported | contained* | contained* |
| `secrets-env-passthrough-selective` | secrets | unsupported | contained | contained |
| `secrets-env-scrub-common-tokens` | secrets | unsupported | contained* | contained* |
| `secrets-home-credentials-in-writable` | secrets | contained | unsupported | contained |
| `secrets-host-process-environ` | secrets | contained | contained | contained |
| `secrets-proc-host-process-links` | secrets | unsupported | contained* | contained* |
| `secrets-read-allow-symlink-hop-no-widen` | secrets | contained | unsupported | control-broke |
| `secrets-read-allow-symlink-into-deny` | secrets | contained | unsupported | control-broke |
| `secrets-read-deny-after-chmod` | secrets | contained | unsupported | contained |
| `secrets-read-deny-also-write-denied` | secrets | contained | unsupported | contained |
| `secrets-read-deny-dir-listing` | secrets | contained | unsupported | contained |
| `secrets-read-deny-on-symlinked-path` | secrets | contained | unsupported | control-broke |
| `secrets-read-deny-path-special-chars` | secrets | contained | unsupported | contained |
| `secrets-read-deny-prefix-collision` | secrets | contained | unsupported | contained |
| `secrets-read-deny-rename-out` | secrets | contained | unsupported | contained |
| `secrets-read-deny-single-file` | secrets | contained | unsupported | contained |
| `secrets-read-deny-symlinked-entry` | secrets | contained | unsupported | control-broke |
| `secrets-read-deny-under-write-denied-ancestor` | secrets | contained | unsupported | contained |
| `trust-handoff-bracketed-root` | trust-handoff | contained | unsupported | control-broke |
| `trust-handoff-claude-agents` | trust-handoff | contained* | escaped* | escaped* |
| `trust-handoff-claude-symlink-cycle` | trust-handoff | escaped* | unsupported | unsupported |
| `trust-handoff-editor-dirs` | trust-handoff | contained* | escaped* | escaped* |
| `trust-handoff-git-config` | trust-handoff | contained* | escaped* | escaped* |
| `trust-handoff-git-config-move-aside` | trust-handoff | contained* | escaped* | contained* |
| `trust-handoff-git-dir-replace` | trust-handoff | contained* | escaped* | contained* |
| `trust-handoff-git-exchange-rename` | trust-handoff | contained* | escaped* | contained* |
| `trust-handoff-gitdir-pointer` | trust-handoff | escaped* | escaped* | contained* |
| `trust-handoff-gitignored-repo` | trust-handoff | escaped* | escaped* | escaped* |
| `trust-handoff-gitmodules` | trust-handoff | contained* | escaped* | escaped* |
| `trust-handoff-hooks-dir-absent` | trust-handoff | contained* | escaped* | escaped* |
| `trust-handoff-repo-created-in-run` | trust-handoff | escaped* | escaped* | escaped* |
| `trust-handoff-root-inside-hooks` | trust-handoff | escaped* | escaped* | escaped* |
| `trust-handoff-shell-rc` | trust-handoff | contained* | escaped* | escaped* |
| `trust-handoff-symlink-absent-parent` | trust-handoff | contained* | unsupported | unsupported |
| `trust-handoff-symlinked-claude-dir` | trust-handoff | escaped* | escaped* | escaped* |
| `trust-handoff-tool-rc` | trust-handoff | contained* | escaped* | escaped* |
| `trust-handoff-unreadable-at-compile` | trust-handoff | contained* | escaped* | escaped* |
| `trust-handoff-worktree-gitfile` | trust-handoff | escaped* | escaped* | escaped* |

Not applicable on this host for every sandbox (12): `ipc-unix-bind-denied`, `ipc-unix-socket-alias`, `ipc-unix-socket-allowlist`, `isolation-apple-events-denied`, `isolation-gpu-node-denied`, `resources-cgroup-escape`, `secrets-glob-deny-created-after-start`, `secrets-glob-deny-rename-out`, `secrets-glob-read-deny`, `secrets-read-deny-case-fold`, `secrets-read-deny-clonefile`, `secrets-read-deny-firmlink`.

## Review notes

We read the raw output (`raw/`) for every result other than `contained`. These notes explain a result; they never change it.

### sandbox-runtime

- `isolation-process-info-foreign` (contract-assumption): /proc/1 inside srt is the sandbox's own init in its private PID namespace, not a host process.
- `isolation-vsock-socket-denied` (confirmed): Same as network-vsock-denied.
- `network-egress-public-denied` (interface): A granted loopback port is reachable only through srt's proxy (measured: HTTP 200 with curl --noproxy ''). The control connects directly, and srt sets NO_PROXY=127.0.0.1, so it fails; the attack was contained.
- `network-local-bind-denied` (contract-assumption): The listener is bound inside srt's own empty network namespace, which no host process can reach; the contract's concern (an inbound channel from the host) does not arise. The control failed for the same proxy reason as network-egress-public-denied.
- `network-other-socket-families-denied` (confirmed): AF_NETLINK/AF_VSOCK sockets can be created. In srt's empty network namespace netlink only sees that namespace; AF_VSOCK is not namespaced. Whether vsock reaches anything on this host: (por confirmar).
- `network-socket-domain-high-bits` (confirmed): Socket creation with high bits set in the domain argument is not refused by srt's filter (which targets AF_UNIX).
- `network-tcp-external-denied` (contract-assumption): The contract counts any error other than EPERM/EACCES as success. Under srt the process has no network interface at all (ENETUNREACH); nothing can leave the host.
- `network-vsock-denied` (confirmed): AF_VSOCK socket creation allowed; reachability on this host (por confirmar).
- `read-deny-bracket-dir` (confirmed): srt exits before running anything: 'Invalid regular expression ... [user-id] ... Range out of order'. Fails closed.
- `read-deny-link-dotdot` (confirmed): The deny is resolved lexically: here/up -> link/../file is folded to here/file, so here/file is denied (control fails) and the real target elsewhere/file is read (attack printed TOPSECRET).
- `secrets-env-loader-injection-inherit` (contract-assumption): The policy asks to inherit the launcher's whole environment, and the sandbox did exactly that (LD_PRELOAD/BASH_ENV passed). The contract's own comment calls stripping loader variables even under inherit-all a design decision still to be made, not an established guarantee.
- `write-deny-dangling-link-target` (confirmed): Writing through the denied dangling link created its eventual target elsewhere/made.
- `write-deny-link-dotdot` (confirmed): srt hung until the runner's 60 s timeout (exit 137) for both attack and control; fails closed, but unusable.

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

### sandbox-runtime

| finding | contracts | status | fixed in | references |
|---|---|---|---|---|
| A read-deny spelled through a symlink with `..` is resolved lexically | `read-deny-link-dotdot` | fixed | main 48a08dc (merged 2026-10-14, after v0.0.79; no release yet) | [#689](https://github.com/anthropics/sandbox-runtime/pull/689) |
| Writing through a write-denied dangling link creates its target | `write-deny-dangling-link-target` | fixed | main 48a08dc (merged 2026-10-14, after v0.0.79; no release yet) | [#689](https://github.com/anthropics/sandbox-runtime/pull/689) |
| A write-deny spelled with `..` through symlinks hangs the sandbox | `write-deny-link-dotdot` | likely fixed | main 48a08dc, whose tests require this case to start; the hang itself not re-measured (por confirmar) | [#689](https://github.com/anthropics/sandbox-runtime/pull/689) |
| A directory named `[user-id]` in a read-deny stops the sandbox from starting | `read-deny-bracket-dir` | fixed | main 80ea0c9 (merged 2026-10-12, after v0.0.79; no release yet) | [#687](https://github.com/anthropics/sandbox-runtime/pull/687) |
| AF_VSOCK sockets can be created | `network-vsock-denied`, `isolation-vsock-socket-denied`, `network-other-socket-families-denied` | fixed | main 5507fb0 (merged 2026-10-10, after v0.0.79; no release yet) | [#691](https://github.com/anthropics/sandbox-runtime/pull/691) |
| AF_NETLINK sockets can be created | `network-other-socket-families-denied` | by design | not planned: the README documents a deny list of AF_UNIX and io_uring; netlink stays inside the sandbox's empty network namespace | [#691](https://github.com/anthropics/sandbox-runtime/pull/691) |
| Socket domains with high bits set are not refused | `network-socket-domain-high-bits` | unclear | (por confirmar) | none found |
| Nested repositories (gitignored, gitdir: pointers, worktree gitfiles) are not covered by the protected names | `trust-handoff-gitignored-repo`, `trust-handoff-gitdir-pointer`, `trust-handoff-worktree-gitfile` | open | not fixed | [#569](https://github.com/anthropics/sandbox-runtime/pull/569) |
| A symlinked .claude directory is not covered by the protected names | `trust-handoff-symlinked-claude-dir` | open | not fixed | [#531](https://github.com/anthropics/sandbox-runtime/pull/531) |
| A repository created during the run, a hooks directory given as a writable root, and a .claude symlink cycle are not covered | `trust-handoff-repo-created-in-run`, `trust-handoff-root-inside-hooks`, `trust-handoff-claude-symlink-cycle` | by design | n/a: srt's README describes the protected names as defense in depth | none found |

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

