# Comparison, run of 2026-10-17

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

| result | landrun |
|---|---|
| contained | 41 |
| escaped | 42 |
| control-broke | 1 |
| unsupported | 83 |
| vacuous | 7 |
| needs-feature | 2 |
| not-applicable | 12 |
| invalid-contract | 0 |

## Escapes by reading

What each `escaped` means on review (spec/verdicts.md §6). Only `confirmed` is a guarantee that did not hold as stated; `pending` has not been reviewed yet.

| reading | landrun |
|---|---|
| confirmed | 5 |
| documented | 7 |
| design | 27 |
| platform-dependent | 2 |
| contract-assumption | 1 |
| interface | 0 |
| pending | 0 |
| **escaped** | 42 |

## Per contract

| contract | category | landrun |
|---|---|---|
| `credentials-broker-auth-required` | credentials | unsupported |
| `credentials-broker-injected-header-not-overridable` | credentials | unsupported |
| `credentials-broker-method-denied` | credentials | unsupported |
| `credentials-broker-no-redirect-follow` | credentials | unsupported |
| `credentials-broker-prefix-scope` | credentials | unsupported |
| `credentials-broker-token-not-forwarded` | credentials | unsupported |
| `filesystem-chmod-outside` | filesystem | escaped |
| `filesystem-command-cwd-not-writable` | filesystem | contained |
| `filesystem-deny-ancestor-rename` | filesystem | unsupported |
| `filesystem-rename-into-territory` | filesystem | contained |
| `filesystem-rename-out-of-territory` | filesystem | contained |
| `filesystem-rm-under-read-deny-ancestor` | filesystem | unsupported |
| `filesystem-rm-under-read-deny-ancestor-by-omission` | filesystem | contained |
| `filesystem-single-file-grant` | filesystem | contained |
| `filesystem-tmp-shm-not-shared` | filesystem | contained |
| `filesystem-truncate-outside` | filesystem | contained |
| `filesystem-unlink-outside` | filesystem | contained |
| `filesystem-utime-outside` | filesystem | escaped |
| `filesystem-writable-root-move-across-roots` | filesystem | unsupported |
| `filesystem-writable-root-replace` | filesystem | contained |
| `filesystem-write-deny-absent-path` | filesystem | unsupported |
| `filesystem-write-deny-rename-bypass` | filesystem | unsupported |
| `filesystem-write-deny-symlink-alias` | filesystem | unsupported |
| `filesystem-write-deny-truncate-unlink` | filesystem | unsupported |
| `filesystem-write-deny-unlink-recreate` | filesystem | unsupported |
| `filesystem-write-deny-via-symlink-spelling` | filesystem | unsupported |
| `filesystem-write-reallow-inside-deny` | filesystem | unsupported |
| `filesystem-write-reallow-inside-deny-by-omission` | filesystem | contained |
| `filesystem-write-system-paths` | filesystem | vacuous |
| `filesystem-xattr-outside` | filesystem | escaped |
| `fs-dangling-symlink-create-outside` | filesystem | contained |
| `fs-dotdot-absent-root` | filesystem | control-broke |
| `fs-hardlink-create-write-out` | filesystem | contained |
| `fs-hardlink-widen-write` | filesystem | contained |
| `fs-symlink-dangling-create` | filesystem | contained |
| `fs-symlink-file-out-agent-made` | filesystem | contained |
| `fs-symlink-rename-out` | filesystem | contained |
| `fs-traversal-write-escape-dotdot` | filesystem | contained |
| `fs-writable-root-symlink-out` | filesystem | escaped |
| `fs-writable-root-symlink-parent` | filesystem | escaped |
| `read-allow-writable-carveout-trailing-slash` | filesystem | unsupported |
| `read-allow-writable-carveout-trailing-slash-by-omission` | filesystem | contained |
| `write-deny-absent-deep` | filesystem | unsupported |
| `write-deny-backslash-absent` | filesystem | unsupported |
| `write-deny-covers-nested-root` | filesystem | unsupported |
| `write-deny-cut-short-hop` | filesystem | unsupported |
| `write-deny-dangling-link-target` | filesystem | unsupported |
| `write-deny-equals-root` | filesystem | unsupported |
| `write-deny-existing-file-chmod` | filesystem | unsupported |
| `write-deny-glob-chars-dir` | filesystem | unsupported |
| `write-deny-link-dotdot` | filesystem | unsupported |
| `write-deny-noncanonical-absent` | filesystem | unsupported |
| `write-deny-symlinked-parent` | filesystem | unsupported |
| `write-deny-through-policy-symlink` | filesystem | unsupported |
| `write-deny-trailing-slash` | filesystem | unsupported |
| `write-deny-under-dotdot-root` | filesystem | unsupported |
| `write-deny-unsearchable-dir` | filesystem | unsupported |
| `ipc-abstract-unix-socket` | ipc | escaped§ |
| `ipc-unix-socket-in-denied-dir` | ipc | unsupported |
| `ipc-unix-socket-in-denied-dir-by-omission` | ipc | escaped |
| `isolation-clone-newns-denied` | isolation | unsupported |
| `isolation-nested-relaunch-no-widen` | isolation | needs-feature |
| `isolation-no-capabilities` | isolation | vacuous |
| `isolation-no-effective-caps` | isolation | unsupported |
| `isolation-no-nested-userns` | isolation | unsupported |
| `isolation-no-new-privs` | isolation | contained* |
| `isolation-pid1-reaper-filtered` | isolation | unsupported |
| `isolation-proc-mem-launcher-denied` | isolation | vacuous |
| `isolation-proc-sys-write-denied` | isolation | vacuous |
| `isolation-process-info-environ` | isolation | vacuous |
| `isolation-process-info-foreign` | isolation | escaped* |
| `isolation-ptrace-launcher-denied` | isolation | vacuous |
| `isolation-root-mount-bypass-denied` | isolation | unsupported |
| `isolation-root-mount-bypass-denied-by-omission` | isolation | vacuous |
| `isolation-seccomp-io-uring-denied` | isolation | escaped* |
| `isolation-signal-host-process` | isolation | escaped*§ |
| `isolation-supervisor-proc-mem-denied` | isolation | escaped* |
| `isolation-vsock-socket-denied` | isolation | escaped* |
| `seccomp-clone-newuser-denied` | isolation | unsupported |
| `seccomp-new-mount-api-denied` | isolation | unsupported |
| `usability-dev-nodes-and-ipc` | isolation | unsupported |
| `lifecycle-background-reaped-on-exit` | lifecycle | escaped* |
| `lifecycle-effect-log-tamper` | lifecycle | needs-feature |
| `lifecycle-exit-status-forwarded` | lifecycle | contained* |
| `lifecycle-no-host-artifacts` | lifecycle | escaped* |
| `lifecycle-signal-teardown` | lifecycle | escaped* |
| `network-broker-allowlist-lookalike` | network | unsupported |
| `network-broker-host-header-spoof` | network | unsupported |
| `network-broker-internal-ip-spellings` | network | unsupported |
| `network-broker-no-request-smuggling` | network | unsupported |
| `network-broker-path-dot-segments` | network | unsupported |
| `network-broker-ssrf-internal` | network | unsupported |
| `network-broker-survives-malformed-client` | network | unsupported |
| `network-domain-allowlist-direct-bypass` | network | unsupported |
| `network-egress-public-denied` | network | escaped |
| `network-icmp-denied` | network | escaped |
| `network-local-bind-denied` | network | contained |
| `network-other-socket-families-denied` | network | escaped |
| `network-proxy-env-present` | network | unsupported |
| `network-socket-domain-high-bits` | network | escaped |
| `network-tcp-external-denied` | network | contained |
| `network-vsock-denied` | network | escaped |
| `seccomp-io-uring-denied` | network | escaped |
| `read-allow-inside-deny-writable-ancestor` | secrets | unsupported |
| `read-allow-symlink-into-deny` | secrets | unsupported |
| `read-allow-symlink-into-deny-by-omission` | secrets | escaped |
| `read-allow-symlink-no-reopen` | secrets | unsupported |
| `read-allow-symlink-no-reopen-by-omission` | secrets | escaped |
| `read-allow-trailing-slash-nested-deny` | secrets | unsupported |
| `read-deny-alt-spelling` | secrets | unsupported |
| `read-deny-alt-spelling-by-omission` | secrets | contained |
| `read-deny-around-nested-root` | secrets | unsupported |
| `read-deny-around-nested-root-by-omission` | secrets | contained |
| `read-deny-backslash-name` | secrets | unsupported |
| `read-deny-backslash-name-by-omission` | secrets | contained |
| `read-deny-bracket-dir` | secrets | unsupported |
| `read-deny-bracket-dir-by-omission` | secrets | contained |
| `read-deny-given-via-symlink` | secrets | unsupported |
| `read-deny-given-via-symlink-by-omission` | secrets | contained |
| `read-deny-link-dotdot` | secrets | unsupported |
| `read-deny-link-dotdot-by-omission` | secrets | contained |
| `read-deny-not-reopened-by-nested-writable` | secrets | unsupported |
| `read-deny-not-reopened-by-nested-writable-by-omission` | secrets | contained |
| `read-deny-root-carve-out` | secrets | unsupported |
| `read-deny-symlink-entry` | secrets | unsupported |
| `read-deny-symlinked-dir` | secrets | unsupported |
| `read-deny-trailing-slash-nested-write-deny` | secrets | unsupported |
| `read-deny-under-write-deny` | secrets | unsupported |
| `secrets-env-loader-injection-inherit` | secrets | escaped‡ |
| `secrets-env-loader-injection-scrub` | secrets | contained* |
| `secrets-env-passthrough-selective` | secrets | contained |
| `secrets-env-scrub-common-tokens` | secrets | contained* |
| `secrets-home-credentials-in-writable` | secrets | unsupported |
| `secrets-host-process-environ` | secrets | contained |
| `secrets-proc-host-process-links` | secrets | contained* |
| `secrets-read-allow-symlink-hop-no-widen` | secrets | unsupported |
| `secrets-read-allow-symlink-hop-no-widen-by-omission` | secrets | contained |
| `secrets-read-allow-symlink-into-deny` | secrets | unsupported |
| `secrets-read-allow-symlink-into-deny-by-omission` | secrets | escaped |
| `secrets-read-deny-after-chmod` | secrets | unsupported |
| `secrets-read-deny-also-write-denied` | secrets | unsupported |
| `secrets-read-deny-dir-listing` | secrets | unsupported |
| `secrets-read-deny-dir-listing-by-omission` | secrets | contained |
| `secrets-read-deny-on-symlinked-path` | secrets | unsupported |
| `secrets-read-deny-on-symlinked-path-by-omission` | secrets | contained |
| `secrets-read-deny-path-special-chars` | secrets | unsupported |
| `secrets-read-deny-path-special-chars-by-omission` | secrets | contained |
| `secrets-read-deny-prefix-collision` | secrets | unsupported |
| `secrets-read-deny-prefix-collision-by-omission` | secrets | contained |
| `secrets-read-deny-rename-out` | secrets | unsupported |
| `secrets-read-deny-single-file` | secrets | unsupported |
| `secrets-read-deny-single-file-by-omission` | secrets | contained |
| `secrets-read-deny-symlinked-entry` | secrets | unsupported |
| `secrets-read-deny-symlinked-entry-by-omission` | secrets | contained |
| `secrets-read-deny-under-write-denied-ancestor` | secrets | unsupported |
| `secrets-traversal-read-escape-dotdot` | secrets | unsupported |
| `trust-handoff-bracketed-root` | trust-handoff | unsupported |
| `trust-handoff-claude-agents` | trust-handoff | escaped* |
| `trust-handoff-claude-symlink-cycle` | trust-handoff | unsupported |
| `trust-handoff-editor-dirs` | trust-handoff | escaped* |
| `trust-handoff-git-config` | trust-handoff | escaped* |
| `trust-handoff-git-config-move-aside` | trust-handoff | escaped* |
| `trust-handoff-git-dir-replace` | trust-handoff | escaped* |
| `trust-handoff-git-exchange-rename` | trust-handoff | escaped* |
| `trust-handoff-gitdir-pointer` | trust-handoff | escaped* |
| `trust-handoff-gitignored-repo` | trust-handoff | escaped* |
| `trust-handoff-gitmodules` | trust-handoff | escaped* |
| `trust-handoff-hooks-dir-absent` | trust-handoff | escaped* |
| `trust-handoff-repo-created-in-run` | trust-handoff | escaped* |
| `trust-handoff-root-inside-hooks` | trust-handoff | escaped* |
| `trust-handoff-shell-rc` | trust-handoff | escaped* |
| `trust-handoff-symlink-absent-parent` | trust-handoff | unsupported |
| `trust-handoff-symlinked-claude-dir` | trust-handoff | escaped* |
| `trust-handoff-tool-rc` | trust-handoff | escaped* |
| `trust-handoff-unreadable-at-compile` | trust-handoff | escaped* |
| `trust-handoff-worktree-gitfile` | trust-handoff | escaped* |

Not applicable on this host for every sandbox (12): `ipc-unix-bind-denied`, `ipc-unix-socket-alias`, `ipc-unix-socket-allowlist`, `isolation-apple-events-denied`, `isolation-gpu-node-denied`, `resources-cgroup-escape`, `secrets-glob-deny-created-after-start`, `secrets-glob-deny-rename-out`, `secrets-glob-read-deny`, `secrets-read-deny-case-fold`, `secrets-read-deny-clonefile`, `secrets-read-deny-firmlink`.

## Review notes

I read the raw output (`raw/`) for every result other than `contained`. These notes explain a result; they never change it.

### landrun

- `filesystem-chmod-outside` (confirmed): Landlock does not mediate chmod/utime/xattr; a readable file's metadata can be changed (same gap as nono).
- `filesystem-utime-outside` (confirmed): as filesystem-chmod-outside.
- `filesystem-xattr-outside` (confirmed): as filesystem-chmod-outside.
- `fs-dotdot-absent-root` (confirmed): landrun fails to apply the Landlock ruleset for a writable root spelled with '..' (control broke).
- `fs-writable-root-symlink-out` (confirmed): a writable root that is a symlink pointing out is followed.
- `fs-writable-root-symlink-parent` (confirmed): as fs-writable-root-symlink-out.
- `ipc-abstract-unix-socket` (platform-dependent): abstract-socket scoping needs Landlock ABI 6; this host is ABI 4.
- `ipc-unix-socket-in-denied-dir-by-omission` (documented): Landlock does not mediate connect() to a pathname unix socket, so a socket in an ungranted directory stays reachable (the same as nono).
- `isolation-process-info-foreign` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `isolation-seccomp-io-uring-denied` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `isolation-signal-host-process` (platform-dependent): signal scoping needs Landlock ABI 6; this host is ABI 4.
- `isolation-supervisor-proc-mem-denied` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `isolation-vsock-socket-denied` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `lifecycle-background-reaped-on-exit` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `lifecycle-no-host-artifacts` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `lifecycle-signal-teardown` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `network-egress-public-denied` (documented): Landlock mediates only TCP (ABI 4): UDP, ICMP, netlink, AF_VSOCK and other socket families are not blocked, so the attack's non-TCP leg succeeds.
- `network-icmp-denied` (documented): Landlock mediates only TCP (ABI 4): UDP, ICMP, netlink, AF_VSOCK and other socket families are not blocked, so the attack's non-TCP leg succeeds.
- `network-other-socket-families-denied` (documented): Landlock mediates only TCP (ABI 4): UDP, ICMP, netlink, AF_VSOCK and other socket families are not blocked, so the attack's non-TCP leg succeeds.
- `network-socket-domain-high-bits` (documented): Landlock mediates only TCP (ABI 4): UDP, ICMP, netlink, AF_VSOCK and other socket families are not blocked, so the attack's non-TCP leg succeeds.
- `network-vsock-denied` (documented): Landlock mediates only TCP (ABI 4): UDP, ICMP, netlink, AF_VSOCK and other socket families are not blocked, so the attack's non-TCP leg succeeds.
- `read-allow-symlink-into-deny-by-omission` (design): The granted read path is itself a symlink into the protected area. Landlock resolves a rule's path when the rule is made, so granting the link grants its target and the secret is read (the same as nono).
- `read-allow-symlink-no-reopen-by-omission` (design): The granted read path is itself a symlink into the protected area. Landlock resolves a rule's path when the rule is made, so granting the link grants its target and the secret is read (the same as nono).
- `seccomp-io-uring-denied` (documented): landrun has no seccomp; io_uring is not blocked (Landlock does not cover syscalls).
- `secrets-env-loader-injection-inherit` (contract-assumption): the policy asked to inherit the whole environment, so LD_PRELOAD passed, as expected.
- `secrets-read-allow-symlink-into-deny-by-omission` (design): The granted read path is itself a symlink into the protected area. Landlock resolves a rule's path when the rule is made, so granting the link grants its target and the secret is read (the same as nono).
- `trust-handoff-claude-agents` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `trust-handoff-editor-dirs` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `trust-handoff-git-config` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `trust-handoff-git-config-move-aside` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `trust-handoff-git-dir-replace` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `trust-handoff-git-exchange-rename` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `trust-handoff-gitdir-pointer` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `trust-handoff-gitignored-repo` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `trust-handoff-gitmodules` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `trust-handoff-hooks-dir-absent` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `trust-handoff-repo-created-in-run` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `trust-handoff-root-inside-hooks` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `trust-handoff-shell-rc` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `trust-handoff-symlinked-claude-dir` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `trust-handoff-tool-rc` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `trust-handoff-unreadable-at-compile` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.
- `trust-handoff-worktree-gitfile` (design): landrun is a filesystem and TCP tool (pure Landlock): no name-based trust-handoff protection, no namespaces or seccomp, no process teardown. It does not claim this guarantee.

