# Comparison, run of 2026-10-21

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

| result | sandbox-runtime | nono | codex | landrun |
|---|---|---|---|---|
| contained | reported | 50 | 95 | 41 |
| escaped | reported | 37 | 24 | 42 |
| control-broke | reported | 5 | 29 | 1 |
| unsupported | reported | 75 | 18 | 83 |
| vacuous | reported | 8 | 9 | 7 |
| needs-feature | reported | 1 | 1 | 2 |
| not-applicable | reported | 12 | 12 | 12 |
| invalid-contract | reported | 0 | 0 | 0 |

sandbox-runtime: findings reported to the vendor; its results will be published once they are fixed.

## Escapes by reading

What each `escaped` means on review (spec/verdicts.md §6). Only `confirmed` is a guarantee that did not hold as stated; `pending` has not been reviewed yet.

| reading | sandbox-runtime | nono | codex | landrun |
|---|---|---|---|---|
| confirmed | reported | 7 | 4 | 5 |
| documented | reported | 1 | 0 | 7 |
| design | reported | 27 | 18 | 27 |
| platform-dependent | reported | 2 | 0 | 2 |
| contract-assumption | reported | 0 | 2 | 1 |
| interface | reported | 0 | 0 | 0 |
| pending | reported | 0 | 0 | 0 |
| **escaped** | reported | 37 | 24 | 42 |

## Per contract

| contract | category | sandbox-runtime | nono | codex | landrun |
|---|---|---|---|---|---|
| `credentials-broker-auth-required` | credentials | reported | unsupported | unsupported | unsupported |
| `credentials-broker-injected-header-not-overridable` | credentials | reported | unsupported | unsupported | unsupported |
| `credentials-broker-method-denied` | credentials | reported | unsupported | unsupported | unsupported |
| `credentials-broker-no-redirect-follow` | credentials | reported | unsupported | unsupported | unsupported |
| `credentials-broker-prefix-scope` | credentials | reported | unsupported | unsupported | unsupported |
| `credentials-broker-token-not-forwarded` | credentials | reported | unsupported | unsupported | unsupported |
| `filesystem-chmod-outside` | filesystem | reported | escaped | contained | escaped |
| `filesystem-command-cwd-not-writable` | filesystem | reported | contained | contained | contained |
| `filesystem-deny-ancestor-rename` | filesystem | reported | unsupported | contained | unsupported |
| `filesystem-rename-into-territory` | filesystem | reported | contained | contained | contained |
| `filesystem-rename-out-of-territory` | filesystem | reported | contained | contained | contained |
| `filesystem-rm-under-read-deny-ancestor` | filesystem | reported | unsupported | contained | unsupported |
| `filesystem-rm-under-read-deny-ancestor-by-omission` | filesystem | reported | contained | contained | contained |
| `filesystem-single-file-grant` | filesystem | reported | contained | control-broke | contained |
| `filesystem-tmp-shm-not-shared` | filesystem | reported | contained | contained | contained |
| `filesystem-truncate-outside` | filesystem | reported | contained | contained | contained |
| `filesystem-unlink-outside` | filesystem | reported | contained | contained | contained |
| `filesystem-utime-outside` | filesystem | reported | escaped | contained | escaped |
| `filesystem-writable-root-move-across-roots` | filesystem | reported | unsupported | contained | unsupported |
| `filesystem-writable-root-replace` | filesystem | reported | contained | contained | contained |
| `filesystem-write-deny-absent-path` | filesystem | reported | unsupported | contained | unsupported |
| `filesystem-write-deny-rename-bypass` | filesystem | reported | unsupported | contained | unsupported |
| `filesystem-write-deny-symlink-alias` | filesystem | reported | unsupported | contained | unsupported |
| `filesystem-write-deny-truncate-unlink` | filesystem | reported | unsupported | contained | unsupported |
| `filesystem-write-deny-unlink-recreate` | filesystem | reported | unsupported | contained | unsupported |
| `filesystem-write-deny-via-symlink-spelling` | filesystem | reported | unsupported | control-broke | unsupported |
| `filesystem-write-reallow-inside-deny` | filesystem | reported | unsupported | contained | unsupported |
| `filesystem-write-reallow-inside-deny-by-omission` | filesystem | reported | contained | contained | contained |
| `filesystem-write-system-paths` | filesystem | reported | vacuous | vacuous | vacuous |
| `filesystem-xattr-outside` | filesystem | reported | escaped | contained | escaped |
| `fs-dangling-symlink-create-outside` | filesystem | reported | contained | contained | contained |
| `fs-dotdot-absent-root` | filesystem | reported | control-broke | contained | control-broke |
| `fs-hardlink-create-write-out` | filesystem | reported | contained | contained | contained |
| `fs-hardlink-widen-write` | filesystem | reported | contained | contained | contained |
| `fs-symlink-dangling-create` | filesystem | reported | contained | contained | contained |
| `fs-symlink-file-out-agent-made` | filesystem | reported | contained | contained | contained |
| `fs-symlink-rename-out` | filesystem | reported | contained | contained | contained |
| `fs-traversal-write-escape-dotdot` | filesystem | reported | contained | contained | contained |
| `fs-writable-root-symlink-out` | filesystem | reported | escaped | escaped | escaped |
| `fs-writable-root-symlink-parent` | filesystem | reported | escaped | escaped | escaped |
| `read-allow-writable-carveout-trailing-slash` | filesystem | reported | unsupported | contained | unsupported |
| `read-allow-writable-carveout-trailing-slash-by-omission` | filesystem | reported | contained | contained | contained |
| `write-deny-absent-deep` | filesystem | reported | unsupported | contained | unsupported |
| `write-deny-backslash-absent` | filesystem | reported | unsupported | contained | unsupported |
| `write-deny-covers-nested-root` | filesystem | reported | unsupported | escaped | unsupported |
| `write-deny-cut-short-hop` | filesystem | reported | unsupported | control-broke | unsupported |
| `write-deny-dangling-link-target` | filesystem | reported | unsupported | control-broke | unsupported |
| `write-deny-equals-root` | filesystem | reported | unsupported | contained | unsupported |
| `write-deny-existing-file-chmod` | filesystem | reported | unsupported | contained | unsupported |
| `write-deny-glob-chars-dir` | filesystem | reported | unsupported | control-broke | unsupported |
| `write-deny-link-dotdot` | filesystem | reported | unsupported | control-broke | unsupported |
| `write-deny-noncanonical-absent` | filesystem | reported | unsupported | contained | unsupported |
| `write-deny-symlinked-parent` | filesystem | reported | unsupported | control-broke | unsupported |
| `write-deny-through-policy-symlink` | filesystem | reported | unsupported | control-broke | unsupported |
| `write-deny-trailing-slash` | filesystem | reported | unsupported | contained | unsupported |
| `write-deny-under-dotdot-root` | filesystem | reported | unsupported | contained | unsupported |
| `write-deny-unsearchable-dir` | filesystem | reported | unsupported | contained | unsupported |
| `ipc-abstract-unix-socket` | ipc | reported | escaped§ | contained | escaped§ |
| `ipc-unix-socket-in-denied-dir` | ipc | reported | unsupported | contained | unsupported |
| `ipc-unix-socket-in-denied-dir-by-omission` | ipc | reported | escaped | contained | escaped |
| `isolation-clone-newns-denied` | isolation | reported | escaped* | escaped* | unsupported |
| `isolation-nested-relaunch-no-widen` | isolation | reported | control-broke* | needs-feature | needs-feature |
| `isolation-no-capabilities` | isolation | reported | vacuous | vacuous | vacuous |
| `isolation-no-effective-caps` | isolation | reported | escaped* | contained* | unsupported |
| `isolation-no-nested-userns` | isolation | reported | escaped* | escaped* | unsupported |
| `isolation-no-new-privs` | isolation | reported | contained* | contained* | contained* |
| `isolation-pid1-reaper-filtered` | isolation | reported | unsupported | contained* | unsupported |
| `isolation-proc-mem-launcher-denied` | isolation | reported | vacuous | vacuous | vacuous |
| `isolation-proc-sys-write-denied` | isolation | reported | vacuous | vacuous | vacuous |
| `isolation-process-info-environ` | isolation | reported | vacuous | vacuous | vacuous |
| `isolation-process-info-foreign` | isolation | reported | escaped* | escaped*‡ | escaped* |
| `isolation-ptrace-launcher-denied` | isolation | reported | vacuous | vacuous | vacuous |
| `isolation-root-mount-bypass-denied` | isolation | reported | unsupported | vacuous | unsupported |
| `isolation-root-mount-bypass-denied-by-omission` | isolation | reported | vacuous | vacuous | vacuous |
| `isolation-seccomp-io-uring-denied` | isolation | reported | contained* | contained* | escaped* |
| `isolation-signal-host-process` | isolation | reported | escaped*§ | contained* | escaped*§ |
| `isolation-supervisor-proc-mem-denied` | isolation | reported | escaped* | escaped* | escaped* |
| `isolation-vsock-socket-denied` | isolation | reported | contained* | contained* | escaped* |
| `seccomp-clone-newuser-denied` | isolation | reported | escaped* | escaped* | unsupported |
| `seccomp-new-mount-api-denied` | isolation | reported | vacuous | vacuous | unsupported |
| `usability-dev-nodes-and-ipc` | isolation | reported | control-broke* | control-broke* | unsupported |
| `lifecycle-background-reaped-on-exit` | lifecycle | reported | escaped* | contained* | escaped* |
| `lifecycle-effect-log-tamper` | lifecycle | reported | needs-feature | unsupported | needs-feature |
| `lifecycle-exit-status-forwarded` | lifecycle | reported | contained* | contained* | contained* |
| `lifecycle-no-host-artifacts` | lifecycle | reported | escaped* | escaped* | escaped* |
| `lifecycle-signal-teardown` | lifecycle | reported | escaped* | escaped* | escaped* |
| `network-broker-allowlist-lookalike` | network | reported | unsupported | unsupported | unsupported |
| `network-broker-host-header-spoof` | network | reported | unsupported | unsupported | unsupported |
| `network-broker-internal-ip-spellings` | network | reported | unsupported | unsupported | unsupported |
| `network-broker-no-request-smuggling` | network | reported | unsupported | unsupported | unsupported |
| `network-broker-path-dot-segments` | network | reported | unsupported | unsupported | unsupported |
| `network-broker-ssrf-internal` | network | reported | unsupported | unsupported | unsupported |
| `network-broker-survives-malformed-client` | network | reported | unsupported | unsupported | unsupported |
| `network-domain-allowlist-direct-bypass` | network | reported | contained | contained | unsupported |
| `network-egress-public-denied` | network | reported | contained | unsupported | escaped |
| `network-icmp-denied` | network | reported | contained | contained | escaped |
| `network-local-bind-denied` | network | reported | contained | unsupported | contained |
| `network-other-socket-families-denied` | network | reported | contained | control-broke | escaped |
| `network-proxy-env-present` | network | reported | contained | contained | unsupported |
| `network-socket-domain-high-bits` | network | reported | control-broke | control-broke | escaped |
| `network-tcp-external-denied` | network | reported | contained | contained | contained |
| `network-vsock-denied` | network | reported | contained | contained | escaped |
| `seccomp-io-uring-denied` | network | reported | control-broke | contained | escaped |
| `read-allow-inside-deny-writable-ancestor` | secrets | reported | unsupported | control-broke | unsupported |
| `read-allow-symlink-into-deny` | secrets | reported | unsupported | control-broke | unsupported |
| `read-allow-symlink-into-deny-by-omission` | secrets | reported | escaped | control-broke‡ | escaped |
| `read-allow-symlink-no-reopen` | secrets | reported | unsupported | control-broke | unsupported |
| `read-allow-symlink-no-reopen-by-omission` | secrets | reported | escaped | control-broke‡ | escaped |
| `read-allow-trailing-slash-nested-deny` | secrets | reported | unsupported | control-broke | unsupported |
| `read-deny-alt-spelling` | secrets | reported | unsupported | control-broke | unsupported |
| `read-deny-alt-spelling-by-omission` | secrets | reported | contained | contained | contained |
| `read-deny-around-nested-root` | secrets | reported | unsupported | contained | unsupported |
| `read-deny-around-nested-root-by-omission` | secrets | reported | contained | contained | contained |
| `read-deny-backslash-name` | secrets | reported | unsupported | contained | unsupported |
| `read-deny-backslash-name-by-omission` | secrets | reported | contained | contained | contained |
| `read-deny-bracket-dir` | secrets | reported | unsupported | control-broke | unsupported |
| `read-deny-bracket-dir-by-omission` | secrets | reported | contained | contained | contained |
| `read-deny-given-via-symlink` | secrets | reported | unsupported | control-broke | unsupported |
| `read-deny-given-via-symlink-by-omission` | secrets | reported | contained | contained | contained |
| `read-deny-link-dotdot` | secrets | reported | unsupported | contained | unsupported |
| `read-deny-link-dotdot-by-omission` | secrets | reported | contained | contained | contained |
| `read-deny-not-reopened-by-nested-writable` | secrets | reported | unsupported | contained | unsupported |
| `read-deny-not-reopened-by-nested-writable-by-omission` | secrets | reported | contained | contained | contained |
| `read-deny-root-carve-out` | secrets | reported | unsupported | control-broke | unsupported |
| `read-deny-symlink-entry` | secrets | reported | unsupported | control-broke | unsupported |
| `read-deny-symlinked-dir` | secrets | reported | unsupported | control-broke | unsupported |
| `read-deny-trailing-slash-nested-write-deny` | secrets | reported | unsupported | contained | unsupported |
| `read-deny-under-write-deny` | secrets | reported | unsupported | contained | unsupported |
| `secrets-env-loader-injection-inherit` | secrets | reported | contained | escaped‡ | escaped‡ |
| `secrets-env-loader-injection-scrub` | secrets | reported | contained* | contained* | contained* |
| `secrets-env-passthrough-selective` | secrets | reported | contained | contained | contained |
| `secrets-env-scrub-common-tokens` | secrets | reported | contained* | contained* | contained* |
| `secrets-home-credentials-in-writable` | secrets | reported | unsupported | contained | unsupported |
| `secrets-host-process-environ` | secrets | reported | contained | contained | contained |
| `secrets-proc-host-process-links` | secrets | reported | contained* | contained* | contained* |
| `secrets-read-allow-symlink-hop-no-widen` | secrets | reported | unsupported | control-broke | unsupported |
| `secrets-read-allow-symlink-hop-no-widen-by-omission` | secrets | reported | contained | contained | contained |
| `secrets-read-allow-symlink-into-deny` | secrets | reported | unsupported | control-broke | unsupported |
| `secrets-read-allow-symlink-into-deny-by-omission` | secrets | reported | escaped | control-broke‡ | escaped |
| `secrets-read-deny-after-chmod` | secrets | reported | unsupported | contained | unsupported |
| `secrets-read-deny-also-write-denied` | secrets | reported | unsupported | contained | unsupported |
| `secrets-read-deny-dir-listing` | secrets | reported | unsupported | contained | unsupported |
| `secrets-read-deny-dir-listing-by-omission` | secrets | reported | contained | contained | contained |
| `secrets-read-deny-on-symlinked-path` | secrets | reported | unsupported | control-broke | unsupported |
| `secrets-read-deny-on-symlinked-path-by-omission` | secrets | reported | contained | contained | contained |
| `secrets-read-deny-path-special-chars` | secrets | reported | unsupported | contained | unsupported |
| `secrets-read-deny-path-special-chars-by-omission` | secrets | reported | contained | contained | contained |
| `secrets-read-deny-prefix-collision` | secrets | reported | unsupported | contained | unsupported |
| `secrets-read-deny-prefix-collision-by-omission` | secrets | reported | contained | contained | contained |
| `secrets-read-deny-rename-out` | secrets | reported | unsupported | contained | unsupported |
| `secrets-read-deny-single-file` | secrets | reported | unsupported | contained | unsupported |
| `secrets-read-deny-single-file-by-omission` | secrets | reported | contained | contained | contained |
| `secrets-read-deny-symlinked-entry` | secrets | reported | unsupported | control-broke | unsupported |
| `secrets-read-deny-symlinked-entry-by-omission` | secrets | reported | contained | contained | contained |
| `secrets-read-deny-under-write-denied-ancestor` | secrets | reported | unsupported | contained | unsupported |
| `secrets-traversal-read-escape-dotdot` | secrets | reported | unsupported | contained | unsupported |
| `trust-handoff-bracketed-root` | trust-handoff | reported | unsupported | control-broke | unsupported |
| `trust-handoff-claude-agents` | trust-handoff | reported | escaped* | escaped* | escaped* |
| `trust-handoff-claude-symlink-cycle` | trust-handoff | reported | unsupported | unsupported | unsupported |
| `trust-handoff-editor-dirs` | trust-handoff | reported | escaped* | escaped* | escaped* |
| `trust-handoff-git-config` | trust-handoff | reported | escaped* | escaped* | escaped* |
| `trust-handoff-git-config-move-aside` | trust-handoff | reported | escaped* | contained* | escaped* |
| `trust-handoff-git-dir-replace` | trust-handoff | reported | escaped* | contained* | escaped* |
| `trust-handoff-git-exchange-rename` | trust-handoff | reported | escaped* | contained* | escaped* |
| `trust-handoff-gitdir-pointer` | trust-handoff | reported | escaped* | contained* | escaped* |
| `trust-handoff-gitignored-repo` | trust-handoff | reported | escaped* | escaped* | escaped* |
| `trust-handoff-gitmodules` | trust-handoff | reported | escaped* | escaped* | escaped* |
| `trust-handoff-hooks-dir-absent` | trust-handoff | reported | escaped* | escaped* | escaped* |
| `trust-handoff-repo-created-in-run` | trust-handoff | reported | escaped* | escaped* | escaped* |
| `trust-handoff-root-inside-hooks` | trust-handoff | reported | escaped* | escaped* | escaped* |
| `trust-handoff-shell-rc` | trust-handoff | reported | escaped* | escaped* | escaped* |
| `trust-handoff-symlink-absent-parent` | trust-handoff | reported | unsupported | unsupported | unsupported |
| `trust-handoff-symlinked-claude-dir` | trust-handoff | reported | escaped* | escaped* | escaped* |
| `trust-handoff-tool-rc` | trust-handoff | reported | escaped* | escaped* | escaped* |
| `trust-handoff-unreadable-at-compile` | trust-handoff | reported | escaped* | escaped* | escaped* |
| `trust-handoff-worktree-gitfile` | trust-handoff | reported | escaped* | escaped* | escaped* |

Not applicable on this host for every sandbox (12): `ipc-unix-bind-denied`, `ipc-unix-socket-alias`, `ipc-unix-socket-allowlist`, `isolation-apple-events-denied`, `isolation-gpu-node-denied`, `resources-cgroup-escape`, `secrets-glob-deny-created-after-start`, `secrets-glob-deny-rename-out`, `secrets-glob-read-deny`, `secrets-read-deny-case-fold`, `secrets-read-deny-clonefile`, `secrets-read-deny-firmlink`.

## Review notes

I read the raw output (`raw/`) for every result other than `contained`. These notes explain a result; they never change it.

### nono

- `filesystem-chmod-outside` (confirmed): Measured with a read grant on the test tree (the neutral read-everything baseline). Landlock does not mediate chmod/utime/xattr, so a readable file's metadata can be changed. Under nono's own idiom (no grant at all) the file would be unreachable.
- `filesystem-utime-outside` (confirmed): As filesystem-chmod-outside.
- `filesystem-xattr-outside` (confirmed): As filesystem-chmod-outside.
- `fs-writable-root-symlink-out` (confirmed): A writable root that is itself a symlink pointing outside the other roots was followed, so its target became writable. The contract pins a policy decision (refuse such a root); the sandbox does not make it.
- `fs-writable-root-symlink-parent` (confirmed): A writable root that is itself a symlink pointing outside the other roots was followed, so its target became writable. The contract pins a policy decision (refuse such a root); the sandbox does not make it.
- `ipc-abstract-unix-socket` (platform-dependent): Abstract-socket scoping needs Landlock ABI 6 (kernel 6.12+); this host has ABI 4 and nono logs it as unavailable.
- `ipc-unix-socket-in-denied-dir-by-omission` (documented): Landlock does not mediate connect() to a pathname unix socket, so a socket in an ungranted directory stays reachable. This is the gap the original contract already documents; it holds in the granted model too.
- `isolation-clone-newns-denied` (design): nono creates no PID namespace and does not claim this isolation (nested user namespaces, capabilities as root, other processes' /proc).
- `isolation-no-effective-caps` (design): nono creates no PID namespace and does not claim this isolation (nested user namespaces, capabilities as root, other processes' /proc).
- `isolation-no-nested-userns` (design): nono creates no PID namespace and does not claim this isolation (nested user namespaces, capabilities as root, other processes' /proc).
- `isolation-process-info-foreign` (design): nono creates no PID namespace and does not claim this isolation (nested user namespaces, capabilities as root, other processes' /proc).
- `isolation-signal-host-process` (platform-dependent): Signal scoping needs Landlock ABI 6 (kernel 6.12+); this host has ABI 4.
- `isolation-supervisor-proc-mem-denied` (design): nono creates no PID namespace and does not claim this isolation (nested user namespaces, capabilities as root, other processes' /proc).
- `lifecycle-background-reaped-on-exit` (confirmed): A background child outlived the sandboxed command and wrote the marker.
- `lifecycle-no-host-artifacts` (design): .mcp.json is not among the files nono protects.
- `lifecycle-signal-teardown` (confirmed): SIGTERM to the launcher ended it (143), but the sandboxed tree survived and wrote the marker.
- `read-allow-symlink-into-deny-by-omission` (design): The granted read path is itself a symlink into the protected area. nono resolves grants through symlinks (documented in its Path Resolution), so granting the link grants its target and the secret is read. codex refuses to build the sandbox.
- `read-allow-symlink-no-reopen-by-omission` (design): The granted read path is itself a symlink into the protected area. nono resolves grants through symlinks (documented in its Path Resolution), so granting the link grants its target and the secret is read. codex refuses to build the sandbox.
- `seccomp-clone-newuser-denied` (design): nono creates no PID namespace and does not claim this isolation (nested user namespaces, capabilities as root, other processes' /proc).
- `secrets-read-allow-symlink-into-deny-by-omission` (design): The granted read path is itself a symlink into the protected area. nono resolves grants through symlinks (documented in its Path Resolution), so granting the link grants its target and the secret is read. codex refuses to build the sandbox.
- `trust-handoff-claude-agents` (design): inside a writable root nono does not protect trust-handoff files (.git/hooks, .git/config, .claude/, editor dirs, rc files); a capability sandbox grants the root as a whole.
- `trust-handoff-editor-dirs` (design): inside a writable root nono does not protect trust-handoff files (.git/hooks, .git/config, .claude/, editor dirs, rc files); a capability sandbox grants the root as a whole.
- `trust-handoff-git-config` (design): inside a writable root nono does not protect trust-handoff files (.git/hooks, .git/config, .claude/, editor dirs, rc files); a capability sandbox grants the root as a whole.
- `trust-handoff-git-config-move-aside` (design): inside a writable root nono does not protect trust-handoff files (.git/hooks, .git/config, .claude/, editor dirs, rc files); a capability sandbox grants the root as a whole.
- `trust-handoff-git-dir-replace` (design): inside a writable root nono does not protect trust-handoff files (.git/hooks, .git/config, .claude/, editor dirs, rc files); a capability sandbox grants the root as a whole.
- `trust-handoff-git-exchange-rename` (design): inside a writable root nono does not protect trust-handoff files (.git/hooks, .git/config, .claude/, editor dirs, rc files); a capability sandbox grants the root as a whole.
- `trust-handoff-gitdir-pointer` (design): inside a writable root nono does not protect trust-handoff files (.git/hooks, .git/config, .claude/, editor dirs, rc files); a capability sandbox grants the root as a whole.
- `trust-handoff-gitignored-repo` (design): inside a writable root nono does not protect trust-handoff files (.git/hooks, .git/config, .claude/, editor dirs, rc files); a capability sandbox grants the root as a whole.
- `trust-handoff-gitmodules` (design): inside a writable root nono does not protect trust-handoff files (.git/hooks, .git/config, .claude/, editor dirs, rc files); a capability sandbox grants the root as a whole.
- `trust-handoff-hooks-dir-absent` (design): inside a writable root nono does not protect trust-handoff files (.git/hooks, .git/config, .claude/, editor dirs, rc files); a capability sandbox grants the root as a whole.
- `trust-handoff-repo-created-in-run` (design): inside a writable root nono does not protect trust-handoff files (.git/hooks, .git/config, .claude/, editor dirs, rc files); a capability sandbox grants the root as a whole.
- `trust-handoff-root-inside-hooks` (design): inside a writable root nono does not protect trust-handoff files (.git/hooks, .git/config, .claude/, editor dirs, rc files); a capability sandbox grants the root as a whole.
- `trust-handoff-shell-rc` (design): inside a writable root nono does not protect trust-handoff files (.git/hooks, .git/config, .claude/, editor dirs, rc files); a capability sandbox grants the root as a whole.
- `trust-handoff-symlinked-claude-dir` (design): inside a writable root nono does not protect trust-handoff files (.git/hooks, .git/config, .claude/, editor dirs, rc files); a capability sandbox grants the root as a whole.
- `trust-handoff-tool-rc` (design): inside a writable root nono does not protect trust-handoff files (.git/hooks, .git/config, .claude/, editor dirs, rc files); a capability sandbox grants the root as a whole.
- `trust-handoff-unreadable-at-compile` (design): inside a writable root nono does not protect trust-handoff files (.git/hooks, .git/config, .claude/, editor dirs, rc files); a capability sandbox grants the root as a whole.
- `trust-handoff-worktree-gitfile` (design): inside a writable root nono does not protect trust-handoff files (.git/hooks, .git/config, .claude/, editor dirs, rc files); a capability sandbox grants the root as a whole.

### codex

- `fs-writable-root-symlink-out` (confirmed): A writable root that is itself a symlink pointing outside the other roots was followed, so its target became writable. The contract pins a policy decision (refuse such a root); the sandbox does not make it.
- `fs-writable-root-symlink-parent` (confirmed): A writable root that is itself a symlink pointing outside the other roots was followed, so its target became writable. The contract pins a policy decision (refuse such a root); the sandbox does not make it.
- `isolation-clone-newns-denied` (design): codex does not claim this isolation (nested user namespaces, an ancestor's /proc/<pid>/mem or environ).
- `isolation-no-nested-userns` (design): codex does not claim this isolation (nested user namespaces, an ancestor's /proc/<pid>/mem or environ).
- `isolation-process-info-foreign` (contract-assumption): /proc/1 inside codex's sandbox is its own init in a private PID namespace, not a host process.
- `isolation-supervisor-proc-mem-denied` (design): codex does not claim this isolation (nested user namespaces, an ancestor's /proc/<pid>/mem or environ).
- `lifecycle-no-host-artifacts` (design): .mcp.json is not on codex's list of protected files.
- `lifecycle-signal-teardown` (confirmed): After SIGTERM to `codex sandbox`, the sandboxed tree kept running and wrote the marker.
- `read-allow-symlink-into-deny-by-omission` (interface): codex refuses to build the sandbox when a read grant resolves through a symlink ('cannot enforce sandbox read-only path'): the attack is stopped and so is the control.
- `read-allow-symlink-no-reopen-by-omission` (interface): codex refuses to build the sandbox when a read grant resolves through a symlink: fails closed, control broke too.
- `read-deny-symlink-entry` (confirmed): Fails closed: bwrap cannot mount over a deny entry that is a symlink, so nothing runs.
- `seccomp-clone-newuser-denied` (design): codex does not claim this isolation (nested user namespaces, an ancestor's /proc/<pid>/mem or environ).
- `secrets-env-loader-injection-inherit` (contract-assumption): The policy asks to inherit the launcher's whole environment, and the sandbox did exactly that (LD_PRELOAD/BASH_ENV passed). The contract's own comment calls stripping loader variables even under inherit-all a design decision still to be made, not an established guarantee.
- `secrets-read-allow-symlink-into-deny-by-omission` (interface): codex refuses to build the sandbox when a read grant resolves through a symlink: fails closed, control broke too.
- `trust-handoff-claude-agents` (design): codex makes .git, .codex, .agents and .aws read-only at the top of each writable root; here the repository or file sits where that protection does not reach.
- `trust-handoff-editor-dirs` (design): codex makes .git, .codex, .agents and .aws read-only at the top of each writable root; here the repository or file sits where that protection does not reach.
- `trust-handoff-git-config` (design): codex makes .git, .codex, .agents and .aws read-only at the top of each writable root; here the repository or file sits where that protection does not reach.
- `trust-handoff-gitignored-repo` (design): codex makes .git, .codex, .agents and .aws read-only at the top of each writable root; here the repository or file sits where that protection does not reach.
- `trust-handoff-gitmodules` (design): codex makes .git, .codex, .agents and .aws read-only at the top of each writable root; here the repository or file sits where that protection does not reach.
- `trust-handoff-hooks-dir-absent` (design): codex makes .git, .codex, .agents and .aws read-only at the top of each writable root; here the repository or file sits where that protection does not reach.
- `trust-handoff-repo-created-in-run` (design): codex makes .git, .codex, .agents and .aws read-only at the top of each writable root; here the repository or file sits where that protection does not reach.
- `trust-handoff-root-inside-hooks` (design): codex makes .git, .codex, .agents and .aws read-only at the top of each writable root; here the repository or file sits where that protection does not reach.
- `trust-handoff-shell-rc` (design): codex makes .git, .codex, .agents and .aws read-only at the top of each writable root; here the repository or file sits where that protection does not reach.
- `trust-handoff-symlinked-claude-dir` (design): codex makes .git, .codex, .agents and .aws read-only at the top of each writable root; here the repository or file sits where that protection does not reach.
- `trust-handoff-tool-rc` (design): codex makes .git, .codex, .agents and .aws read-only at the top of each writable root; here the repository or file sits where that protection does not reach.
- `trust-handoff-unreadable-at-compile` (design): codex makes .git, .codex, .agents and .aws read-only at the top of each writable root; here the repository or file sits where that protection does not reach.
- `trust-handoff-worktree-gitfile` (design): codex makes .git, .codex, .agents and .aws read-only at the top of each writable root; here the repository or file sits where that protection does not reach.
- `write-deny-covers-nested-root` (confirmed): A writable root nested inside a write-denied directory stayed writable; codex resolves overlapping entries by the most specific path.

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

