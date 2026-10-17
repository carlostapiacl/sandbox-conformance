# Changes to the corpus

Every change to a contract after a corpus freeze is listed here, with why, so a
reader can tell a fix from a change made to suit a result. The corpus was frozen
at tag `corpus-2026-10-16` before TartarOS, maintained by this lab's author, was
first measured.

## After `corpus-2026-10-16`

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
