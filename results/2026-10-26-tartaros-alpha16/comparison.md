# Comparison, run of 2026-10-26

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

| result | sandbox-runtime | tartaros |
|---|---|---|
| contained | 6 | 168 |
| escaped | 0 | 3 |
| control-broke | 0 | 0 |
| unsupported | 0 | 0 |
| vacuous | 0 | 10 |
| needs-feature | 0 | 1 |
| not-applicable | 0 | 12 |
| invalid-contract | 0 | 0 |

## Escapes by reading

What each `escaped` means on review (spec/verdicts.md §6). Only `confirmed` is a guarantee that did not hold as stated; `pending` has not been reviewed yet.

| reading | sandbox-runtime | tartaros |
|---|---|---|
| confirmed | 0 | 0 |
| documented | 0 | 1 |
| design | 0 | 0 |
| platform-dependent | 0 | 0 |
| contract-assumption | 0 | 2 |
| interface | 0 | 0 |
| pending | 0 | 0 |
| **escaped** | 0 | 3 |

## Per contract

| contract | category | sandbox-runtime | tartaros |
|---|---|---|---|
| `credentials-broker-auth-required` | credentials |  | contained |
| `credentials-broker-injected-header-not-overridable` | credentials |  | contained |
| `credentials-broker-method-denied` | credentials |  | contained |
| `credentials-broker-no-redirect-follow` | credentials |  | contained |
| `credentials-broker-prefix-scope` | credentials |  | contained |
| `credentials-broker-token-not-forwarded` | credentials |  | contained |
| `credentials-masked-env-agent-holds-sentinel` | credentials | contained | contained |
| `credentials-masked-env-body-scoped` | credentials | contained | contained |
| `credentials-masked-env-no-laundering` | credentials | contained | contained |
| `credentials-masked-env-not-in-process-records` | credentials | contained | contained |
| `credentials-masked-env-not-sent-to-other-host` | credentials | contained | contained |
| `credentials-masked-env-plain-http-not-swapped` | credentials | contained | contained |
| `filesystem-chmod-outside` | filesystem |  | contained |
| `filesystem-command-cwd-not-writable` | filesystem |  | contained |
| `filesystem-deny-ancestor-rename` | filesystem |  | contained |
| `filesystem-rename-into-territory` | filesystem |  | contained |
| `filesystem-rename-out-of-territory` | filesystem |  | contained |
| `filesystem-rm-under-read-deny-ancestor` | filesystem |  | contained |
| `filesystem-rm-under-read-deny-ancestor-by-omission` | filesystem |  | contained |
| `filesystem-single-file-grant` | filesystem |  | contained |
| `filesystem-tmp-shm-not-shared` | filesystem |  | contained |
| `filesystem-truncate-outside` | filesystem |  | contained |
| `filesystem-unlink-outside` | filesystem |  | contained |
| `filesystem-utime-outside` | filesystem |  | contained |
| `filesystem-writable-root-move-across-roots` | filesystem |  | contained |
| `filesystem-writable-root-replace` | filesystem |  | contained |
| `filesystem-write-deny-absent-path` | filesystem |  | contained |
| `filesystem-write-deny-rename-bypass` | filesystem |  | contained |
| `filesystem-write-deny-symlink-alias` | filesystem |  | contained |
| `filesystem-write-deny-truncate-unlink` | filesystem |  | contained |
| `filesystem-write-deny-unlink-recreate` | filesystem |  | contained |
| `filesystem-write-deny-via-symlink-spelling` | filesystem |  | contained |
| `filesystem-write-reallow-inside-deny` | filesystem |  | contained |
| `filesystem-write-reallow-inside-deny-by-omission` | filesystem |  | contained |
| `filesystem-write-system-paths` | filesystem |  | vacuous |
| `filesystem-xattr-outside` | filesystem |  | contained |
| `fs-dangling-symlink-create-outside` | filesystem |  | contained |
| `fs-dotdot-absent-root` | filesystem |  | contained |
| `fs-hardlink-create-write-out` | filesystem |  | contained |
| `fs-hardlink-widen-write` | filesystem |  | contained |
| `fs-symlink-dangling-create` | filesystem |  | contained |
| `fs-symlink-file-out-agent-made` | filesystem |  | contained |
| `fs-symlink-rename-out` | filesystem |  | contained |
| `fs-traversal-write-escape-dotdot` | filesystem |  | contained |
| `fs-writable-root-symlink-out` | filesystem |  | contained |
| `fs-writable-root-symlink-parent` | filesystem |  | contained |
| `read-allow-writable-carveout-trailing-slash` | filesystem |  | contained |
| `read-allow-writable-carveout-trailing-slash-by-omission` | filesystem |  | contained |
| `write-deny-absent-deep` | filesystem |  | contained |
| `write-deny-backslash-absent` | filesystem |  | contained |
| `write-deny-covers-nested-root` | filesystem |  | contained |
| `write-deny-cut-short-hop` | filesystem |  | contained |
| `write-deny-dangling-link-target` | filesystem |  | contained |
| `write-deny-equals-root` | filesystem |  | contained |
| `write-deny-existing-file-chmod` | filesystem |  | contained |
| `write-deny-glob-chars-dir` | filesystem |  | contained |
| `write-deny-link-dotdot` | filesystem |  | contained |
| `write-deny-noncanonical-absent` | filesystem |  | contained |
| `write-deny-symlinked-parent` | filesystem |  | contained |
| `write-deny-through-policy-symlink` | filesystem |  | contained |
| `write-deny-trailing-slash` | filesystem |  | contained |
| `write-deny-under-dotdot-root` | filesystem |  | contained |
| `write-deny-unsearchable-dir` | filesystem |  | contained |
| `ipc-abstract-unix-socket` | ipc |  | contained |
| `ipc-unix-bind-denied` | ipc |  | n/a |
| `ipc-unix-socket-alias` | ipc |  | n/a |
| `ipc-unix-socket-allowlist` | ipc |  | n/a |
| `ipc-unix-socket-in-denied-dir` | ipc |  | contained |
| `ipc-unix-socket-in-denied-dir-by-omission` | ipc |  | contained |
| `isolation-apple-events-denied` | isolation |  | n/a |
| `isolation-clone-newns-denied` | isolation |  | contained* |
| `isolation-gpu-node-denied` | isolation |  | n/a |
| `isolation-nested-relaunch-no-widen` | isolation |  | contained* |
| `isolation-no-capabilities` | isolation |  | vacuous |
| `isolation-no-effective-caps` | isolation |  | contained* |
| `isolation-no-nested-userns` | isolation |  | contained* |
| `isolation-no-new-privs` | isolation |  | contained* |
| `isolation-pid1-reaper-filtered` | isolation |  | contained* |
| `isolation-proc-mem-launcher-denied` | isolation |  | vacuous |
| `isolation-proc-sys-write-denied` | isolation |  | vacuous |
| `isolation-process-info-environ` | isolation |  | vacuous |
| `isolation-process-info-foreign` | isolation |  | escaped*‡ |
| `isolation-ptrace-launcher-denied` | isolation |  | vacuous |
| `isolation-root-mount-bypass-denied` | isolation |  | vacuous |
| `isolation-root-mount-bypass-denied-by-omission` | isolation |  | vacuous |
| `isolation-seccomp-io-uring-denied` | isolation |  | contained* |
| `isolation-signal-host-process` | isolation |  | contained* |
| `isolation-supervisor-proc-mem-denied` | isolation |  | escaped*‡ |
| `isolation-vsock-socket-denied` | isolation |  | contained* |
| `seccomp-clone-newuser-denied` | isolation |  | contained* |
| `seccomp-new-mount-api-denied` | isolation |  | vacuous |
| `usability-dev-nodes-and-ipc` | isolation |  | contained* |
| `lifecycle-background-reaped-on-exit` | lifecycle |  | contained* |
| `lifecycle-effect-log-tamper` | lifecycle |  | needs-feature |
| `lifecycle-exit-status-forwarded` | lifecycle |  | contained* |
| `lifecycle-no-host-artifacts` | lifecycle |  | contained* |
| `lifecycle-signal-teardown` | lifecycle |  | contained* |
| `network-broker-allowlist-lookalike` | network |  | contained |
| `network-broker-host-header-spoof` | network |  | contained |
| `network-broker-internal-ip-spellings` | network |  | contained |
| `network-broker-no-request-smuggling` | network |  | contained |
| `network-broker-path-dot-segments` | network |  | contained |
| `network-broker-ssrf-internal` | network |  | contained |
| `network-broker-survives-malformed-client` | network |  | vacuous |
| `network-domain-allowlist-direct-bypass` | network |  | contained |
| `network-egress-public-denied` | network |  | contained |
| `network-icmp-denied` | network |  | contained |
| `network-local-bind-denied` | network |  | contained |
| `network-other-socket-families-denied` | network |  | contained |
| `network-proxy-env-present` | network |  | contained |
| `network-socket-domain-high-bits` | network |  | contained |
| `network-tcp-external-denied` | network |  | contained |
| `network-vsock-denied` | network |  | contained |
| `seccomp-io-uring-denied` | network |  | contained |
| `resources-cgroup-escape` | resources |  | n/a |
| `read-allow-inside-deny-writable-ancestor` | secrets |  | contained |
| `read-allow-symlink-into-deny` | secrets |  | contained |
| `read-allow-symlink-into-deny-by-omission` | secrets |  | contained |
| `read-allow-symlink-no-reopen` | secrets |  | contained |
| `read-allow-symlink-no-reopen-by-omission` | secrets |  | contained |
| `read-allow-trailing-slash-nested-deny` | secrets |  | contained |
| `read-deny-alt-spelling` | secrets |  | contained |
| `read-deny-alt-spelling-by-omission` | secrets |  | contained |
| `read-deny-around-nested-root` | secrets |  | contained |
| `read-deny-around-nested-root-by-omission` | secrets |  | contained |
| `read-deny-backslash-name` | secrets |  | contained |
| `read-deny-backslash-name-by-omission` | secrets |  | contained |
| `read-deny-bracket-dir` | secrets |  | contained |
| `read-deny-bracket-dir-by-omission` | secrets |  | contained |
| `read-deny-given-via-symlink` | secrets |  | contained |
| `read-deny-given-via-symlink-by-omission` | secrets |  | contained |
| `read-deny-link-dotdot` | secrets |  | contained |
| `read-deny-link-dotdot-by-omission` | secrets |  | contained |
| `read-deny-not-reopened-by-nested-writable` | secrets |  | contained |
| `read-deny-not-reopened-by-nested-writable-by-omission` | secrets |  | contained |
| `read-deny-root-carve-out` | secrets |  | contained |
| `read-deny-symlink-entry` | secrets |  | contained |
| `read-deny-symlinked-dir` | secrets |  | contained |
| `read-deny-trailing-slash-nested-write-deny` | secrets |  | contained |
| `read-deny-under-write-deny` | secrets |  | contained |
| `secrets-env-loader-injection-inherit` | secrets |  | contained |
| `secrets-env-loader-injection-scrub` | secrets |  | contained* |
| `secrets-env-passthrough-selective` | secrets |  | contained |
| `secrets-env-scrub-common-tokens` | secrets |  | contained* |
| `secrets-glob-deny-created-after-start` | secrets |  | n/a |
| `secrets-glob-deny-rename-out` | secrets |  | n/a |
| `secrets-glob-read-deny` | secrets |  | n/a |
| `secrets-home-credentials-in-writable` | secrets |  | contained |
| `secrets-host-process-environ` | secrets |  | contained |
| `secrets-proc-host-process-links` | secrets |  | contained* |
| `secrets-read-allow-symlink-hop-no-widen` | secrets |  | contained |
| `secrets-read-allow-symlink-hop-no-widen-by-omission` | secrets |  | contained |
| `secrets-read-allow-symlink-into-deny` | secrets |  | contained |
| `secrets-read-allow-symlink-into-deny-by-omission` | secrets |  | contained |
| `secrets-read-deny-after-chmod` | secrets |  | contained |
| `secrets-read-deny-also-write-denied` | secrets |  | contained |
| `secrets-read-deny-case-fold` | secrets |  | n/a |
| `secrets-read-deny-clonefile` | secrets |  | n/a |
| `secrets-read-deny-dir-listing` | secrets |  | contained |
| `secrets-read-deny-dir-listing-by-omission` | secrets |  | contained |
| `secrets-read-deny-firmlink` | secrets |  | n/a |
| `secrets-read-deny-on-symlinked-path` | secrets |  | contained |
| `secrets-read-deny-on-symlinked-path-by-omission` | secrets |  | contained |
| `secrets-read-deny-path-special-chars` | secrets |  | contained |
| `secrets-read-deny-path-special-chars-by-omission` | secrets |  | contained |
| `secrets-read-deny-prefix-collision` | secrets |  | contained |
| `secrets-read-deny-prefix-collision-by-omission` | secrets |  | contained |
| `secrets-read-deny-rename-out` | secrets |  | contained |
| `secrets-read-deny-single-file` | secrets |  | contained |
| `secrets-read-deny-single-file-by-omission` | secrets |  | contained |
| `secrets-read-deny-symlinked-entry` | secrets |  | contained |
| `secrets-read-deny-symlinked-entry-by-omission` | secrets |  | contained |
| `secrets-read-deny-under-write-denied-ancestor` | secrets |  | contained |
| `secrets-traversal-read-escape-dotdot` | secrets |  | contained |
| `trust-handoff-bracketed-root` | trust-handoff |  | contained |
| `trust-handoff-claude-agents` | trust-handoff |  | contained* |
| `trust-handoff-claude-symlink-cycle` | trust-handoff |  | contained* |
| `trust-handoff-editor-dirs` | trust-handoff |  | contained* |
| `trust-handoff-git-config` | trust-handoff |  | contained* |
| `trust-handoff-git-config-move-aside` | trust-handoff |  | contained* |
| `trust-handoff-git-dir-replace` | trust-handoff |  | contained* |
| `trust-handoff-git-exchange-rename` | trust-handoff |  | contained* |
| `trust-handoff-gitdir-pointer` | trust-handoff |  | contained* |
| `trust-handoff-gitignored-repo` | trust-handoff |  | contained* |
| `trust-handoff-gitmodules` | trust-handoff |  | contained* |
| `trust-handoff-hooks-dir-absent` | trust-handoff |  | contained* |
| `trust-handoff-repo-created-in-run` | trust-handoff |  | escaped* |
| `trust-handoff-root-inside-hooks` | trust-handoff |  | contained* |
| `trust-handoff-shell-rc` | trust-handoff |  | contained* |
| `trust-handoff-symlink-absent-parent` | trust-handoff |  | contained* |
| `trust-handoff-symlinked-claude-dir` | trust-handoff |  | contained* |
| `trust-handoff-tool-rc` | trust-handoff |  | contained* |
| `trust-handoff-unreadable-at-compile` | trust-handoff |  | contained* |
| `trust-handoff-worktree-gitfile` | trust-handoff |  | contained* |

Not applicable on this host for every sandbox (0): .

## Review notes

I read the raw output (`raw/`) for every result other than `contained`. These notes explain a result; they never change it.

### tartaros

- `isolation-process-info-foreign` (contract-assumption): /proc/1 inside tartaros is the sandbox's own init in its private PID namespace, not a host process (the reading given to srt and codex).
- `isolation-supervisor-proc-mem-denied` (contract-assumption): The process whose environ is read is the agent's own sh (PID 2 of the run's PID namespace), the parent of the attacking python; the supervisor is outside the namespace and has no /proc entry in it.
- `trust-handoff-repo-created-in-run` (documented): tartaros documents that on Linux a repository the agent creates during the run is not protected: its hooks are new and Landlock matches inodes that exist at launch (docs/limits.md).

