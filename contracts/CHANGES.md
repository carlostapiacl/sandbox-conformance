# Changes to the corpus

Every change to a contract after a corpus freeze is listed here, with why, so a
reader can tell a fix from a change made to suit a result. The corpus was frozen
at tag `corpus-2026-10-16` before TartarOS, maintained by this lab's author, was
first measured.

## After `corpus-2026-10-16`

- **2026-10-26. Six masked-credential contracts are added** (`credentials-masked-env-*`),
  from sandbox-runtime's `credential-mask*.test.ts`, with the runner features they
  need: `[[masked_env]]`, TLS witnesses (`tls`, `name`) signed by a CA made per run,
  `read_body` / `echo_request`, and the `witness-host` requirement (a forwarding host on a TEST-NET network). They are
  frozen before any sandbox is measured on them, and the attacks are not changed to
  suit a result: a fix goes here. Written by this lab's author, who also wrote
  TartarOS's masked credentials (released in 0.1.0-alpha.16, the same day); that is
  the conflict of interest, and why each contract states the source test it
  re-expresses.

- **2026-10-22. The broker contracts become measurable.** The 13 contracts with a
  `[broker]` were `unsupported` for every sandbox: their attack could not be shown
  to work without a sandbox. The baseline now runs them against a reference broker
  with no defences ([`spec/format.md`](../spec/format.md), "The `[broker]` table").
  Four of them carried their assert or witness only as a comment, waiting for a
  runner feature; with `log_paths`, `echo_headers`, `absent_line` and
  `[[host_alias]]` in the runner they now state it:
  `network-broker-no-request-smuggling` and `network-broker-path-dot-segments`
  (no request outside the capability reaches the upstream),
  `credentials-broker-injected-header-not-overridable` (the upstream echoes what it
  got) and `network-broker-allowlist-lookalike` (the allow-list and the names it
  needs). The attacks and controls are unchanged. Prompted by adding a broker to
  TartarOS's CLI, maintained by this lab's author; no result existed for any
  sandbox on these contracts. `credentials-broker-no-redirect-follow` and
  `credentials-broker-token-not-forwarded` changed only by losing a stale comment.

- **2026-10-17. Nine contracts gain a `{root}/work` fixture**:
  `filesystem-write-reallow-inside-deny` (and `-by-omission`),
  `ipc-unix-socket-allowlist`, `read-deny-around-nested-root` (and `-by-omission`),
  `secrets-read-allow-symlink-hop-no-widen` (and `-by-omission`),
  `secrets-read-deny-prefix-collision` (and `-by-omission`). They named
  `{root}/work` as a writable root without creating it. landrun refuses a grant on
  a path that does not exist, which is how this surfaced when landrun was first
  measured in the granted model (SC-003); sandboxes that ignore a missing grant
  were unaffected. Not prompted by any TartarOS result.
- **2026-10-17. Coordinated disclosure.** Contracts involved in an open
  coordinated disclosure are held out of the published corpus and of every
  published run (`SECURITY.md`, spec/verdicts.md §9). Holds are not itemized
  here; the contracts return, with their results, when the disclosure closes.
