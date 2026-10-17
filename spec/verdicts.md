# Verdicts

**Version:** 1.0.0-draft · **Status:** draft, open for review · **Supersedes:** v0 (implicit; the
runs of 2026-10-15)

This document defines what a sandbox-conformance result means: the values a result can
take, the procedure that assigns them, the record that carries them, and the rules for
comparing and publishing them. [`format.md`](format.md) defines how a contract is written;
this document defines how it is judged. [`runner/verdict.py`](../runner/verdict.py)
implements the decision procedure (§4), and [`runner/tests/`](../runner/tests/) checks it,
rule by rule and against reference sandboxes whose behaviour is known.

It is written so that two independent labs, running the same contract against the same
sandbox on equivalent hosts, assign the same result, and so that anyone reading a result
can tell what was observed, what was asked for, and what it means, without trusting the
lab that produced it.

The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are to be interpreted as
described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
[RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they appear in
capitals.

## 1. Terms

- **Contract**: one TOML file stating one guarantee ([`format.md`](format.md)).
- **Sandbox under test**: one sandbox, at one exact version.
- **Adapter**: the code that translates a contract's neutral `[policy]` into that
  sandbox's configuration and command line.
- **Profile**: how the adapter fills what the contract's policy leaves open (§7).
- **Host**: the machine the case runs on, described by its detected capabilities, not
  only by its kernel version.
- **Case**: one contract × one sandbox version × one profile × one host.
- **Phase**: one pass of a case from a fresh state. Every case has a *baseline* phase
  (no sandbox) and a *sandboxed* phase.
- **Lab**: the runner, the adapters and the host setup, as opposed to the sandbox under
  test.

## 2. Three axes

A result answers three different questions. They MUST be recorded as separate fields
and MUST NOT be folded into one value or expressed only as typographic marks.

| axis | question | values | who assigns it |
|---|---|---|---|
| **result** | What was observed? | §3 | the decision procedure (§4), mechanically |
| **basis** | Was the guarantee asked for? | `configured`, `default` (§5) | the contract and the adapter, before the run |
| **reading** | What does it mean? | §6 | a reviewer, after the run |

A reading MUST NOT change a result. A result is what the lab measured; a reading is an
explanation attached to it.

## 3. Results

Results fall into three groups. Only the first says something about the sandbox.

### 3.1 Measured: the case ran and says something about the sandbox

| result | meaning |
|---|---|
| `contained` | The attack did not take effect under the sandbox, and the control succeeded. |
| `escaped` | The attack took effect under the sandbox. |
| `control-broke` | The attack did not take effect, but the control failed too: the sandbox stopped legitimate work. |
| `inconclusive` | The case ran, but the evidence does not decide between the outcomes above (§4.6). |

### 3.2 Not measured: the case did not run, for a reason about the sandbox or the host

| result | meaning |
|---|---|
| `unsupported` | The sandbox cannot express a field of the contract's policy. A capability gap, never a vulnerability. |
| `not-applicable` | The contract does not apply to this host: wrong OS, or a required host capability is missing. |
| `vacuous` | The attack does not take effect on this host even without a sandbox, so blocking it proves nothing. |

### 3.3 Lab faults: the case says nothing about the sandbox

| result | meaning |
|---|---|
| `invalid-contract` | The contract fails validation: an unknown field, a missing part, a condition no phase can observe. |
| `invalid-baseline` | Without a sandbox the control fails, and the contract does not declare why (§4.4). |
| `needs-feature` | The runner or the adapter lacks a feature the contract needs (a placeholder, a broker, a log location). |
| `harness-error` | The lab itself failed: an exception in the runner or the adapter, fixtures that could not be created, a sandbox that does not start under any policy on this host. |

A lab fault MUST NOT be reported as a measured result. In particular, a failure to start
the sandbox MUST NOT be reported as `contained` (§4.5).

## 4. Decision procedure

The steps below are applied in order; the first one that assigns a result ends the case.
Every phase starts from a fresh state: a new `{root}`, fixtures re-created, no process
left from an earlier phase.

### 4.1 Validate the contract

Unknown fields, a missing `[attack]` or `[control]`, or an `[assert]` that names nothing
observable → `invalid-contract`.

### 4.2 Applicability

The host's OS is not in `os`, or a capability in `requires` is not detected on the host
→ `not-applicable`, with the missing capability named.

The same holds for what the sandbox itself needs. Some sandboxes degrade silently: on a
host without the mechanism they rely on, they start and confine nothing (landrun with
`--best-effort` and no Landlock), and the start probe (§4.5) cannot tell. The adapter
MUST declare the host capabilities its sandbox needs to confine anything
(`HOST_REQUIRES`); without them every case is `not-applicable`, with the capability and
the sandbox named. Where a sandbox drops only part of a policy on this host (landrun's TCP
rules below Landlock ABI 4), the adapter MUST report the affected fields `unsupported`
(§4.3) rather than let the case be measured as if they applied.

### 4.3 Capability

The adapter reports a `[policy]` field it cannot express → `unsupported`, with the field
and the reason. The adapter reports a runner or adapter feature it lacks →
`needs-feature`. Both are decided before anything runs.

### 4.4 Baseline (no sandbox)

1. Any lab exception → `harness-error`.
2. The attack MUST take effect (§4.6). If it does not → `vacuous`.
3. The control MUST succeed. If it fails, the case is `invalid-baseline`, unless the
   contract declares `control_requires_sandbox = "<reason>"`: a control that checks
   something only the sandbox provides (a proxy variable it sets, for example). The
   declaration MUST be in the contract before the run; it MUST NOT be added to explain
   a result after the fact.
   The control runs after the attack, in the same phase, so it also shows the sandbox
   is still usable after the attempt. It therefore MUST NOT depend on anything the
   attack is allowed to change when it succeeds (the contents of a writable root, for
   example): otherwise a successful baseline attack breaks the control, and the
   contract, not the sandbox, is at fault.

### 4.5 Sandboxed

1. Any lab exception → `harness-error`.
2. **Start probe.** Before anything else, the lab runs `true` under the sandbox with a
   minimal policy (one writable root, the phase's own fresh directory). If it does not
   succeed → `harness-error`: the sandbox does not run on this host at all, and nothing
   it does afterwards says anything about confinement.
3. **Contracts with `expect_refusal = true`** (the correct outcome is that the sandbox
   refuses this policy). The lab runs `true` under the contract's policy, the *refusal
   probe*. Its failing is `contained` only if the failure matches the refusal
   signature the adapter declares for that sandbox (an exit status and, where the
   sandbox prints one, a message). A failure that does not match → `inconclusive`. A
   refusal probe that succeeds → the case continues with the attack, and the effect
   decides.
4. Run the attack, then the control.
5. The attack took effect (§4.6) → `escaped`. The attack's outcome is unclear (§4.6) →
   `inconclusive`.
6. The attack did not take effect and the control failed → `control-broke`.
7. Otherwise → `contained`.

### 4.6 When the attack "takes effect"

- If the contract has an `[assert]` and the baseline showed its effect (a file changed,
  a marker present, a process dead), the effect decides, in both phases. The attack's
  exit status is recorded but does not decide.
- Otherwise the attack's exit status decides. `expect_exit` (default 0) means *took
  effect*. A status MUST NOT stand for two outcomes, so:
  - if the contract declares `blocked_exit`, only those statuses mean *blocked*; any
    other status is unclear;
  - if it does not, every other status means *blocked*, except the ones that say the
    attack never reached a decision: a timeout, 126 and 127 (not executable, not
    found), and death by a signal (128 + n). Those are unclear. SIGSYS is the exception:
    it is how a syscall filter (seccomp's kill action) stops a process, so it means
    *blocked*;
  - an attack that can exit with its *blocked* status for a reason other than being
    blocked — a script whose interpreter exits 1 on an uncaught error, for example —
    MUST declare `blocked_exit` with a status its interpreter does not use.

  An unclear outcome makes the case `inconclusive`.
- A contract whose attack declares `expect_exit` and has no `[assert]` is a *fidelity*
  contract: the guarantee is that the sandbox reports the command's own exit status
  (143 for a command ended by SIGTERM, for example). Without a sandbox the attack MUST
  report `expect_exit`, or the case is `vacuous`; under the sandbox any other status is
  `escaped`, and a timeout is `inconclusive`.
- A timeout of the control is a failed control. A timeout of an exit-decided attack is
  `inconclusive`.

### 4.7 Repetitions

A contract that depends on timing (a race, a late fixture) SHOULD declare
`repeat = <n>`. Each repetition is a full sandboxed phase from a fresh state.

- Any repetition `escaped` → `escaped`, recorded as *k of n*.
- All repetitions `contained` → `contained`.
- Any other mix (some `control-broke`, some `inconclusive`, some lab faults) →
  `inconclusive`, with every repetition recorded.

A single `contained` run of a timing-dependent attack MUST NOT be reported as a held
guarantee unless the contract declares it deterministic.

## 5. Basis

| basis | meaning |
|---|---|
| `configured` | A `[policy]` field asks for this guarantee. An `escaped` here is a configured rule that did not hold. |
| `default` | No `[policy]` field asks for it. The result shows what the sandbox does on its own; an `escaped` here is a difference of defaults, not a broken rule. |

The basis is fixed before the run, from the contract and the adapter, and MUST be
recorded with every measured result.

## 6. Reading

Every measured result other than `contained` SHOULD receive a reading. Until it does,
its reading is `pending`. A reading carries a kind, a note, who wrote it and when.

| reading | meaning | counts as a finding? |
|---|---|---|
| `pending` | Not reviewed yet. | not yet |
| `confirmed` | The guarantee, as stated, did not hold. | **yes** |
| `documented` | The sandbox's own documentation states this limitation. | known limitation |
| `design` | A deliberate design choice that differs from the contract's assumption. | known limitation |
| `platform-dependent` | The result depends on a host capability this host lacks (a newer Landlock ABI, for example). | no, on this host |
| `contract-assumption` | The contract assumes something that does not hold for this sandbox's architecture; given how it is built, the result is not a breach. | no |
| `interface` | The result comes from how the contract or the adapter talks to the sandbox (through its proxy, for example), not from the guarantee. | no |

A reading MAY be amended later. The earlier reading MUST be kept, so a published
reading is never silently replaced.

## 7. Profiles

A contract's `[policy]` says what it asks for. A sandbox often has options the policy
does not mention. The profile says how the adapter sets them.

| profile | the adapter sets every option the policy leaves open to |
|---|---|
| `strict` | the most restrictive value the sandbox's documentation supports that still lets the control run |
| `default` | the sandbox's own default |
| `custom` | values named in the case record |

Every result MUST name its profile. The v0 runs used `strict`.

## 8. Comparing and publishing

1. Results MUST NOT be summed, averaged or ranked across sandbox versions, profiles or
   hosts with different detected capabilities. A table that compares sandboxes MUST
   state the version, profile and host of each column.
2. A single score or ranking across sandboxes MUST NOT be published. Counts per result
   MAY be published per case group.
3. A count of `escaped` MUST be broken down by reading, so a reader can tell confirmed
   findings from contract assumptions and known limitations.
4. Lab faults (§3.3) MUST be published as such, and MUST NOT be counted as measured
   results.
5. A published result MUST NOT be changed. A correction is a new run, or a new reading
   that keeps the old one.

## 9. Disclosure

Whether a result may be shown is separate from what the result is.

- While a coordinated disclosure is open, a lab MUST NOT publish the result, its reading,
  its evidence or any prose that describes it, and MUST NOT publish that such a result
  exists: a "withheld" mark names the sandbox and the contract, and contracts are
  runnable, so the mark alone lets anyone reproduce the finding.
- The contracts involved are held out of the published corpus and out of every
  published run, for every sandbox, so that neither a missing cell nor a missing row
  points at them.
- They are published, with their results, only when the disclosure process with the
  sandbox's maintainers allows it ([`SECURITY.md`](../SECURITY.md)).

## 10. The case record

Every case MUST produce one record. Fields marked *later* are REQUIRED once the lab can
provide them (see the roadmap) and SHOULD be filled before then.

| field | content |
|---|---|
| `spec_version` | version of this document the case was judged under |
| `contract` | id, path, and SHA-256 of the contract file |
| `corpus_commit`, `runner_commit` | commits of the contracts and of the runner |
| `adapter` | name, and SHA-256 of the adapter module |
| `sandbox` | name, version, source (package or release); SHA-256 of the binary (*later*) |
| `profile` | §7, and for `custom`, the values |
| `config` | the configuration the adapter produced, and (*later*) the configuration the sandbox reports it applied |
| `host` | kernel, OS, architecture, detected capabilities (Landlock ABI, user namespaces, cgroups…), container options |
| `result`, `basis`, `reading`, `disclosure` | §3, §5, §6, §9 |
| `phases` | for each phase and repetition: command, exit status, timed out, duration, captured output (bounded), effect evidence |
| `reason` | for every result other than `contained` and `escaped`, why |

## 11. SARIF export

A run MAY be exported as [SARIF 2.1.0](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html),
so tools that read static-analysis and security results can ingest it unchanged. One
SARIF `run` per sandbox version and profile; each contract is a `rule`; each measured
case is a `result`.

| result | SARIF `kind` | SARIF `level` |
|---|---|---|
| `contained` | `pass` | `none` |
| `escaped` | `fail` | `error` (severity critical or high), `warning` (medium) |
| `control-broke` | `fail` | `warning` |
| `inconclusive` | `open` | `none` |
| `unsupported`, `not-applicable`, `vacuous` | `notApplicable` | `none` |
| lab faults (§3.3) | not a `result`: a `toolExecutionNotification` of the run's `invocation` | `error` |

- A reading of `contract-assumption` or `interface` is exported as a `suppression` with
  `status: accepted` and the note as its `justification`. The result stays a `fail`.
- `basis`, `reading`, `profile` and the host capabilities go in `properties`.

## 12. Versioning

This document uses semantic versioning. A change that can change the result of an
existing case is a major version. A run records the version it was judged under, and is
never re-judged in place: re-judging is a new run.

### From v0 (the 2026-10-15 runs)

The 2026-10-15 runs were judged before this document existed. They stay as published.
This is how their values read in v1 terms:

| v0 | v1 |
|---|---|
| `contained` with reason "sandbox refused to start" | `contained` only if the refusal matches the adapter's signature; otherwise `inconclusive` (re-measure) |
| `contained` / `control-broke` with `control_fails_unsandboxed` | `invalid-baseline`, unless the contract now declares `control_requires_sandbox` |
| `needs-feature` with reason "runner error…" | `harness-error` |
| `needs-feature` (other reasons) | `needs-feature` |
| `withheld` (result) | not published at all while the disclosure is open (§9) |
| `basis: policy` / `built-in` | `configured` / `default` |
| marks `*` / `‡` / `§` | `basis: default` / reading `contract-assumption` or `interface` / reading `platform-dependent` |
| reading `kernel-dependent` | `platform-dependent` |
| reading `vacuous` | dropped: the result already says it |
| exit-decided attacks without `blocked_exit` | v0 read any non-success status as blocked; v1 reads timeouts, 126, 127 and signals other than SIGSYS as `inconclusive` |
| `contained` / `control-broke` from a sandbox that never started | `harness-error` (the start probe, §4.5) |

## 13. Open questions

- **Refusal signatures**: each adapter has to declare one. Some sandboxes print no
  distinct message when they refuse a policy; for those, is an exit status enough?
- **Repetition count**: what `n` makes a `contained` race trustworthy, and should it be
  set per contract or per family?
- **Independent observation**: §4.6 still trusts the runner's own snapshot of the
  effect. A later version should require effects observed from outside the sandboxed
  process's reach, at least for network and process guarantees.
- **Finding severity**: `severity` belongs to the contract; whether a confirmed finding
  needs its own impact rating (conditions needed, reach) is not settled.
