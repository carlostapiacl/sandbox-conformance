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

| result | sandbox-runtime | nono | codex | landrun |
|---|---|---|---|---|
| contained | 120 | 48 | 92 | 22 |
| escaped | 22 | 37 | 24 | 38 |
| control-broke | 4 | 6 | 30 | 2 |
| unsupported | 18 | 74 | 18 | 104 |
| vacuous | 9 | 8 | 9 | 6 |
| needs-feature | 1 | 1 | 1 | 2 |
| not-applicable | 12 | 12 | 12 | 12 |
| invalid-contract | 0 | 0 | 0 | 0 |

## Per contract

| contract | category | sandbox-runtime | nono | codex | landrun |
|---|---|---|---|---|---|
| `credentials-broker-auth-required` | credentials | unsupported | unsupported | unsupported | unsupported |
| `credentials-broker-injected-header-not-overridable` | credentials | unsupported | unsupported | unsupported | unsupported |
| `credentials-broker-method-denied` | credentials | unsupported | unsupported | unsupported | unsupported |
| `credentials-broker-no-redirect-follow` | credentials | unsupported | unsupported | unsupported | unsupported |
| `credentials-broker-prefix-scope` | credentials | unsupported | unsupported | unsupported | unsupported |
| `credentials-broker-token-not-forwarded` | credentials | unsupported | unsupported | unsupported | unsupported |
| `filesystem-chmod-outside` | filesystem | contained | escaped | contained | escaped |
| `filesystem-command-cwd-not-writable` | filesystem | contained | contained | contained | contained |
| `filesystem-deny-ancestor-rename` | filesystem | contained | unsupported | contained | unsupported |
| `filesystem-rename-into-territory` | filesystem | contained | contained | contained | contained |
| `filesystem-rename-out-of-territory` | filesystem | contained | contained | contained | contained |
| `filesystem-rm-under-read-deny-ancestor` | filesystem | contained | unsupported | contained | unsupported |
| `filesystem-rm-under-read-deny-ancestor-by-omission` | filesystem | contained | contained | contained | unsupported |
| `filesystem-single-file-grant` | filesystem | contained | contained | control-broke | contained |
| `filesystem-tmp-shm-not-shared` | filesystem | contained | contained | contained | contained |
| `filesystem-truncate-outside` | filesystem | contained | contained | contained | contained |
| `filesystem-unlink-outside` | filesystem | contained | contained | contained | contained |
| `filesystem-utime-outside` | filesystem | contained | escaped | contained | escaped |
| `filesystem-writable-root-move-across-roots` | filesystem | contained | unsupported | contained | unsupported |
| `filesystem-writable-root-replace` | filesystem | control-broke | control-broke | control-broke | control-broke |
| `filesystem-write-deny-absent-path` | filesystem | contained | unsupported | contained | unsupported |
| `filesystem-write-deny-rename-bypass` | filesystem | contained | unsupported | contained | unsupported |
| `filesystem-write-deny-symlink-alias` | filesystem | contained | unsupported | contained | unsupported |
| `filesystem-write-deny-truncate-unlink` | filesystem | contained | unsupported | contained | unsupported |
| `filesystem-write-deny-unlink-recreate` | filesystem | contained | unsupported | contained | unsupported |
| `filesystem-write-deny-via-symlink-spelling` | filesystem | contained | unsupported | control-broke | unsupported |
| `filesystem-write-reallow-inside-deny` | filesystem | contained | unsupported | contained | unsupported |
| `filesystem-write-reallow-inside-deny-by-omission` | filesystem | contained | contained | contained | unsupported |
| `filesystem-write-system-paths` | filesystem | vacuous | vacuous | vacuous | vacuous |
| `filesystem-xattr-outside` | filesystem | contained | escaped | contained | escaped |
| `fs-dangling-symlink-create-outside` | filesystem | contained | contained | contained | contained |
| `fs-dotdot-absent-root` | filesystem | contained | control-broke | contained | control-broke |
| `fs-hardlink-create-write-out` | filesystem | contained | contained | contained | contained |
| `fs-hardlink-widen-write` | filesystem | contained | contained | contained | contained |
| `fs-symlink-dangling-create` | filesystem | contained | contained | contained | contained |
| `fs-symlink-file-out-agent-made` | filesystem | contained | contained | contained | contained |
| `fs-symlink-rename-out` | filesystem | contained | contained | contained | contained |
| `fs-writable-root-symlink-out` | filesystem | contained | escaped | escaped | escaped |
| `fs-writable-root-symlink-parent` | filesystem | contained | escaped | escaped | escaped |
| `read-allow-writable-carveout-trailing-slash` | filesystem | contained | unsupported | contained | unsupported |
| `read-allow-writable-carveout-trailing-slash-by-omission` | filesystem | contained | contained | contained | unsupported |
| `write-deny-absent-deep` | filesystem | contained | unsupported | contained | unsupported |
| `write-deny-backslash-absent` | filesystem | contained | unsupported | contained | unsupported |
| `write-deny-covers-nested-root` | filesystem | contained | unsupported | escaped | unsupported |
| `write-deny-cut-short-hop` | filesystem | contained | unsupported | control-broke | unsupported |
| `write-deny-dangling-link-target` | filesystem | escaped | unsupported | control-broke | unsupported |
| `write-deny-equals-root` | filesystem | contained | unsupported | contained | unsupported |
| `write-deny-existing-file-chmod` | filesystem | contained | unsupported | contained | unsupported |
| `write-deny-glob-chars-dir` | filesystem | contained | unsupported | control-broke | unsupported |
| `write-deny-link-dotdot` | filesystem | control-broke | unsupported | control-broke | unsupported |
| `write-deny-noncanonical-absent` | filesystem | contained | unsupported | contained | unsupported |
| `write-deny-symlinked-parent` | filesystem | contained | unsupported | control-broke | unsupported |
| `write-deny-through-policy-symlink` | filesystem | contained | unsupported | control-broke | unsupported |
| `write-deny-trailing-slash` | filesystem | contained | unsupported | contained | unsupported |
| `write-deny-under-dotdot-root` | filesystem | contained | unsupported | contained | unsupported |
| `write-deny-unsearchable-dir` | filesystem | contained | unsupported | contained | unsupported |
| `ipc-abstract-unix-socket` | ipc | contained | escaped§ | contained | escaped§ |
| `ipc-unix-socket-in-denied-dir` | ipc | contained | unsupported | contained | unsupported |
| `ipc-unix-socket-in-denied-dir-by-omission` | ipc | contained | escaped | contained | unsupported |
| `isolation-clone-newns-denied` | isolation | escaped* | escaped* | escaped* | unsupported |
| `isolation-nested-relaunch-no-widen` | isolation | needs-feature | control-broke* | needs-feature | needs-feature |
| `isolation-no-capabilities` | isolation | vacuous | vacuous | vacuous | vacuous |
| `isolation-no-effective-caps` | isolation | escaped* | escaped* | contained* | unsupported |
| `isolation-no-nested-userns` | isolation | escaped* | escaped* | escaped* | unsupported |
| `isolation-no-new-privs` | isolation | contained* | contained* | contained* | contained* |
| `isolation-pid1-reaper-filtered` | isolation | escaped* | unsupported | contained* | unsupported |
| `isolation-proc-mem-launcher-denied` | isolation | vacuous | vacuous | vacuous | vacuous |
| `isolation-proc-sys-write-denied` | isolation | vacuous | vacuous | vacuous | vacuous |
| `isolation-process-info-environ` | isolation | vacuous | vacuous | vacuous | vacuous |
| `isolation-process-info-foreign` | isolation | escaped*‡ | escaped* | escaped*‡ | escaped* |
| `isolation-ptrace-launcher-denied` | isolation | vacuous | vacuous | vacuous | vacuous |
| `isolation-root-mount-bypass-denied` | isolation | vacuous | unsupported | vacuous | unsupported |
| `isolation-root-mount-bypass-denied-by-omission` | isolation | vacuous | vacuous | vacuous | unsupported |
| `isolation-seccomp-io-uring-denied` | isolation | contained* | contained* | contained* | escaped* |
| `isolation-signal-host-process` | isolation | contained* | escaped*§ | contained* | escaped*§ |
| `isolation-supervisor-proc-mem-denied` | isolation | contained* | escaped* | escaped* | escaped* |
| `isolation-vsock-socket-denied` | isolation | escaped* | contained* | contained* | escaped* |
| `seccomp-clone-newuser-denied` | isolation | escaped* | escaped* | escaped* | unsupported |
| `seccomp-new-mount-api-denied` | isolation | vacuous | vacuous | vacuous | unsupported |
| `usability-dev-nodes-and-ipc` | isolation | contained* | control-broke* | control-broke* | unsupported |
| `lifecycle-background-reaped-on-exit` | lifecycle | contained* | escaped* | contained* | escaped* |
| `lifecycle-effect-log-tamper` | lifecycle | unsupported | needs-feature | unsupported | needs-feature |
| `lifecycle-exit-status-forwarded` | lifecycle | contained* | contained* | contained* | contained* |
| `lifecycle-no-host-artifacts` | lifecycle | contained* | escaped* | escaped* | escaped* |
| `lifecycle-signal-teardown` | lifecycle | contained* | escaped* | escaped* | escaped* |
| `network-broker-allowlist-lookalike` | network | unsupported | unsupported | unsupported | unsupported |
| `network-broker-host-header-spoof` | network | unsupported | unsupported | unsupported | unsupported |
| `network-broker-internal-ip-spellings` | network | unsupported | unsupported | unsupported | unsupported |
| `network-broker-no-request-smuggling` | network | unsupported | unsupported | unsupported | unsupported |
| `network-broker-path-dot-segments` | network | unsupported | unsupported | unsupported | unsupported |
| `network-broker-ssrf-internal` | network | unsupported | unsupported | unsupported | unsupported |
| `network-broker-survives-malformed-client` | network | unsupported | unsupported | unsupported | unsupported |
| `network-domain-allowlist-direct-bypass` | network | contained | contained | contained | unsupported |
| `network-egress-public-denied` | network | control-broke‡ | contained | unsupported | escaped |
| `network-icmp-denied` | network | contained | contained | contained | escaped |
| `network-local-bind-denied` | network | escaped‡ | contained | unsupported | contained |
| `network-other-socket-families-denied` | network | escaped | contained | control-broke | escaped |
| `network-proxy-env-present` | network | contained | contained | contained | unsupported |
| `network-socket-domain-high-bits` | network | escaped | control-broke | control-broke | escaped |
| `network-tcp-external-denied` | network | escaped‡ | contained | contained | contained |
| `network-vsock-denied` | network | escaped | contained | contained | escaped |
| `seccomp-io-uring-denied` | network | contained | control-broke | contained | escaped |
| `read-allow-inside-deny-writable-ancestor` | secrets | contained | unsupported | control-broke | unsupported |
| `read-allow-symlink-into-deny` | secrets | contained | unsupported | control-broke | unsupported |
| `read-allow-symlink-into-deny-by-omission` | secrets | contained | escaped | control-broke‡ | unsupported |
| `read-allow-symlink-no-reopen` | secrets | contained | unsupported | control-broke | unsupported |
| `read-allow-symlink-no-reopen-by-omission` | secrets | contained | escaped | control-broke‡ | unsupported |
| `read-allow-trailing-slash-nested-deny` | secrets | contained | unsupported | control-broke | unsupported |
| `read-deny-alt-spelling` | secrets | contained | unsupported | control-broke | unsupported |
| `read-deny-alt-spelling-by-omission` | secrets | contained | contained | contained | unsupported |
| `read-deny-around-nested-root` | secrets | contained | unsupported | contained | unsupported |
| `read-deny-around-nested-root-by-omission` | secrets | contained | contained | contained | unsupported |
| `read-deny-backslash-name` | secrets | contained | unsupported | contained | unsupported |
| `read-deny-backslash-name-by-omission` | secrets | contained | contained | contained | unsupported |
| `read-deny-bracket-dir` | secrets | control-broke | unsupported | control-broke | unsupported |
| `read-deny-bracket-dir-by-omission` | secrets | contained | contained | contained | unsupported |
| `read-deny-given-via-symlink` | secrets | contained | unsupported | control-broke | unsupported |
| `read-deny-given-via-symlink-by-omission` | secrets | contained | contained | contained | unsupported |
| `read-deny-link-dotdot` | secrets | escaped | unsupported | contained | unsupported |
| `read-deny-link-dotdot-by-omission` | secrets | contained | contained | contained | unsupported |
| `read-deny-not-reopened-by-nested-writable` | secrets | contained | unsupported | contained | unsupported |
| `read-deny-not-reopened-by-nested-writable-by-omission` | secrets | contained | contained | contained | unsupported |
| `read-deny-root-carve-out` | secrets | contained | unsupported | control-broke | unsupported |
| `read-deny-symlink-entry` | secrets | contained | unsupported | control-broke | unsupported |
| `read-deny-symlinked-dir` | secrets | contained | unsupported | control-broke | unsupported |
| `read-deny-trailing-slash-nested-write-deny` | secrets | contained | unsupported | contained | unsupported |
| `read-deny-under-write-deny` | secrets | contained | unsupported | contained | unsupported |
| `secrets-env-loader-injection-inherit` | secrets | escaped‡ | contained | escaped‡ | escaped‡ |
| `secrets-env-loader-injection-scrub` | secrets | unsupported | contained* | contained* | contained* |
| `secrets-env-passthrough-selective` | secrets | unsupported | contained | contained | contained |
| `secrets-env-scrub-common-tokens` | secrets | unsupported | contained* | contained* | contained* |
| `secrets-home-credentials-in-writable` | secrets | contained | unsupported | contained | unsupported |
| `secrets-host-process-environ` | secrets | contained | contained | contained | contained |
| `secrets-proc-host-process-links` | secrets | unsupported | contained* | contained* | contained* |
| `secrets-read-allow-symlink-hop-no-widen` | secrets | contained | unsupported | control-broke | unsupported |
| `secrets-read-allow-symlink-hop-no-widen-by-omission` | secrets | contained | contained | contained | unsupported |
| `secrets-read-allow-symlink-into-deny` | secrets | contained | unsupported | control-broke | unsupported |
| `secrets-read-allow-symlink-into-deny-by-omission` | secrets | contained | escaped | control-broke‡ | unsupported |
| `secrets-read-deny-after-chmod` | secrets | contained | unsupported | contained | unsupported |
| `secrets-read-deny-also-write-denied` | secrets | contained | unsupported | contained | unsupported |
| `secrets-read-deny-dir-listing` | secrets | contained | unsupported | contained | unsupported |
| `secrets-read-deny-dir-listing-by-omission` | secrets | contained | contained | contained | unsupported |
| `secrets-read-deny-on-symlinked-path` | secrets | contained | unsupported | control-broke | unsupported |
| `secrets-read-deny-on-symlinked-path-by-omission` | secrets | contained | contained | contained | unsupported |
| `secrets-read-deny-path-special-chars` | secrets | contained | unsupported | contained | unsupported |
| `secrets-read-deny-path-special-chars-by-omission` | secrets | contained | contained | contained | unsupported |
| `secrets-read-deny-prefix-collision` | secrets | contained | unsupported | contained | unsupported |
| `secrets-read-deny-prefix-collision-by-omission` | secrets | contained | contained | contained | unsupported |
| `secrets-read-deny-rename-out` | secrets | contained | unsupported | contained | unsupported |
| `secrets-read-deny-single-file` | secrets | contained | unsupported | contained | unsupported |
| `secrets-read-deny-single-file-by-omission` | secrets | contained | contained | contained | unsupported |
| `secrets-read-deny-symlinked-entry` | secrets | contained | unsupported | control-broke | unsupported |
| `secrets-read-deny-symlinked-entry-by-omission` | secrets | contained | contained | contained | unsupported |
| `secrets-read-deny-under-write-denied-ancestor` | secrets | contained | unsupported | contained | unsupported |
| `trust-handoff-bracketed-root` | trust-handoff | contained | unsupported | control-broke | unsupported |
| `trust-handoff-claude-agents` | trust-handoff | contained* | escaped* | escaped* | escaped* |
| `trust-handoff-claude-symlink-cycle` | trust-handoff | escaped* | unsupported | unsupported | unsupported |
| `trust-handoff-editor-dirs` | trust-handoff | contained* | escaped* | escaped* | escaped* |
| `trust-handoff-git-config` | trust-handoff | contained* | escaped* | escaped* | escaped* |
| `trust-handoff-git-config-move-aside` | trust-handoff | contained* | escaped* | contained* | escaped* |
| `trust-handoff-git-dir-replace` | trust-handoff | contained* | escaped* | contained* | escaped* |
| `trust-handoff-git-exchange-rename` | trust-handoff | contained* | escaped* | contained* | escaped* |
| `trust-handoff-gitdir-pointer` | trust-handoff | escaped* | escaped* | contained* | escaped* |
| `trust-handoff-gitignored-repo` | trust-handoff | escaped* | escaped* | escaped* | escaped* |
| `trust-handoff-gitmodules` | trust-handoff | contained* | escaped* | escaped* | escaped* |
| `trust-handoff-hooks-dir-absent` | trust-handoff | contained* | escaped* | escaped* | escaped* |
| `trust-handoff-repo-created-in-run` | trust-handoff | escaped* | escaped* | escaped* | escaped* |
| `trust-handoff-root-inside-hooks` | trust-handoff | escaped* | escaped* | escaped* | escaped* |
| `trust-handoff-shell-rc` | trust-handoff | contained* | escaped* | escaped* | escaped* |
| `trust-handoff-symlink-absent-parent` | trust-handoff | contained* | unsupported | unsupported | unsupported |
| `trust-handoff-symlinked-claude-dir` | trust-handoff | escaped* | escaped* | escaped* | escaped* |
| `trust-handoff-tool-rc` | trust-handoff | contained* | escaped* | escaped* | escaped* |
| `trust-handoff-unreadable-at-compile` | trust-handoff | contained* | escaped* | escaped* | escaped* |
| `trust-handoff-worktree-gitfile` | trust-handoff | escaped* | escaped* | escaped* | escaped* |

Not applicable on this host for every sandbox (12): `ipc-unix-bind-denied`, `ipc-unix-socket-alias`, `ipc-unix-socket-allowlist`, `isolation-apple-events-denied`, `isolation-gpu-node-denied`, `resources-cgroup-escape`, `secrets-glob-deny-created-after-start`, `secrets-glob-deny-rename-out`, `secrets-glob-read-deny`, `secrets-read-deny-case-fold`, `secrets-read-deny-clonefile`, `secrets-read-deny-firmlink`.

## Review notes

We read the raw output (`raw/`) for every result other than `contained`. These notes explain a result; they never change it.

### sandbox-runtime

- `isolation-process-info-foreign` (contract-assumption): /proc/1 inside srt is the sandbox's own init in its private PID namespace, not a host process.
- `isolation-root-mount-bypass-denied-by-omission` (vacuous): mount fails in the container without a sandbox; nothing is proven here.
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
- `ipc-unix-socket-in-denied-dir-by-omission` (documented): Landlock does not mediate connect() to a pathname unix socket, so a socket in an ungranted directory stays reachable. This is the gap the original contract already documents; it holds in the granted model too.
- `isolation-root-mount-bypass-denied-by-omission` (vacuous): mount operations fail in the container even without a sandbox (no CAP_SYS_ADMIN), so the attack proves nothing on this host.
- `isolation-signal-host-process` (kernel-dependent): Signal scoping needs Landlock ABI 6 (kernel 6.12+); this host has ABI 4.
- `lifecycle-background-reaped-on-exit` (confirmed): A background child outlived the sandboxed command and wrote the marker.
- `lifecycle-signal-teardown` (confirmed): SIGTERM to the launcher ended it (143), but the sandboxed tree survived and wrote the marker.
- `read-allow-symlink-into-deny-by-omission` (design): The granted read path is itself a symlink into the protected area. nono resolves grants through symlinks (documented in its Path Resolution), so granting the link grants its target and the secret is read. srt grants the link name only and contains it; codex refuses to build the sandbox.
- `read-allow-symlink-no-reopen-by-omission` (design): The granted read path is itself a symlink into the protected area. nono resolves grants through symlinks (documented in its Path Resolution), so granting the link grants its target and the secret is read. srt grants the link name only and contains it; codex refuses to build the sandbox.
- `secrets-read-allow-symlink-into-deny-by-omission` (design): The granted read path is itself a symlink into the protected area. nono resolves grants through symlinks (documented in its Path Resolution), so granting the link grants its target and the secret is read. srt grants the link name only and contains it; codex refuses to build the sandbox.

### codex

- `fs-writable-root-symlink-out` (confirmed): A writable root that is itself a symlink pointing outside the other roots was followed, so its target became writable. The contract pins a policy decision (refuse such a root); the sandbox does not make it.
- `fs-writable-root-symlink-parent` (confirmed): A writable root that is itself a symlink pointing outside the other roots was followed, so its target became writable. The contract pins a policy decision (refuse such a root); the sandbox does not make it.
- `isolation-process-info-foreign` (contract-assumption): /proc/1 inside codex's sandbox is its own init in a private PID namespace, not a host process.
- `isolation-root-mount-bypass-denied-by-omission` (vacuous): mount fails in the container without a sandbox; nothing is proven here.
- `lifecycle-signal-teardown` (confirmed): After SIGTERM to `codex sandbox`, the sandboxed tree kept running and wrote the marker.
- `read-allow-symlink-into-deny-by-omission` (interface): codex refuses to build the sandbox when a read grant resolves through a symlink ('cannot enforce sandbox read-only path'): the attack is stopped and so is the control.
- `read-allow-symlink-no-reopen-by-omission` (interface): codex refuses to build the sandbox when a read grant resolves through a symlink: fails closed, control broke too.
- `read-deny-symlink-entry` (confirmed): Fails closed: bwrap cannot mount over a deny entry that is a symlink, so nothing runs.
- `secrets-env-loader-injection-inherit` (contract-assumption): The policy asks to inherit the launcher's whole environment, and the sandbox did exactly that (LD_PRELOAD/BASH_ENV passed). The contract's own comment calls stripping loader variables even under inherit-all a design decision still to be made, not an established guarantee.
- `secrets-read-allow-symlink-into-deny-by-omission` (interface): codex refuses to build the sandbox when a read grant resolves through a symlink: fails closed, control broke too.
- `write-deny-covers-nested-root` (confirmed): A writable root nested inside a write-denied directory stayed writable; codex resolves overlapping entries by the most specific path.

### landrun

- `filesystem-chmod-outside` (confirmed): Landlock does not mediate chmod/utime/xattr; a readable file's metadata can be changed (same gap as nono).
- `filesystem-utime-outside` (confirmed): as filesystem-chmod-outside.
- `filesystem-writable-root-replace` (confirmed): a writable root replaced during the run; control broke.
- `filesystem-xattr-outside` (confirmed): as filesystem-chmod-outside.
- `fs-dotdot-absent-root` (confirmed): landrun fails to apply the Landlock ruleset for a writable root spelled with '..' (control broke).
- `fs-writable-root-symlink-out` (confirmed): a writable root that is a symlink pointing out is followed.
- `fs-writable-root-symlink-parent` (confirmed): as fs-writable-root-symlink-out.
- `ipc-abstract-unix-socket` (kernel-dependent): abstract-socket scoping needs Landlock ABI 6; this host is ABI 4.
- `isolation-signal-host-process` (kernel-dependent): signal scoping needs Landlock ABI 6; this host is ABI 4.
- `network-egress-public-denied` (documented): Landlock mediates only TCP (ABI 4): UDP, ICMP, netlink, AF_VSOCK and other socket families are not blocked, so the attack's non-TCP leg succeeds.
- `network-icmp-denied` (documented): Landlock mediates only TCP (ABI 4): UDP, ICMP, netlink, AF_VSOCK and other socket families are not blocked, so the attack's non-TCP leg succeeds.
- `network-other-socket-families-denied` (documented): Landlock mediates only TCP (ABI 4): UDP, ICMP, netlink, AF_VSOCK and other socket families are not blocked, so the attack's non-TCP leg succeeds.
- `network-socket-domain-high-bits` (documented): Landlock mediates only TCP (ABI 4): UDP, ICMP, netlink, AF_VSOCK and other socket families are not blocked, so the attack's non-TCP leg succeeds.
- `network-vsock-denied` (documented): Landlock mediates only TCP (ABI 4): UDP, ICMP, netlink, AF_VSOCK and other socket families are not blocked, so the attack's non-TCP leg succeeds.
- `seccomp-io-uring-denied` (documented): landrun has no seccomp; io_uring is not blocked (Landlock does not cover syscalls).
- `secrets-env-loader-injection-inherit` (contract-assumption): the policy asked to inherit the whole environment, so LD_PRELOAD passed, as expected.

