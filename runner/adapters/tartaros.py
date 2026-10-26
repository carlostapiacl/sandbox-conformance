"""Adapter: TartarOS (`tartaros run`), Linux backend (Landlock + seccomp).

Maps the neutral [policy] to `tartaros run` flags. TartarOS is maintained by
the author of this lab: its adapter goes through the same review as the others
(a first review of a private trial is recorded in sandboxes/tartaros.md), and its
results carry that conflict of interest.

Strict profile (spec/verdicts.md §7): `--strict` always, so a guarantee the host
cannot install aborts the run instead of degrading. Refusals print a line
starting `tartaros:` and exit 78 (EX_CONFIG); that is the declared refusal signature.
It was exit 2 until 0.1.0-alpha.6; the change was made after seeing the
2026-10-16 trial results (two contracts were inconclusive because tartaros used
the same code for a refusal and a start failure), and is recorded as such.
"""
import json, os, subprocess, tempfile
from common import basis, masked_settings, needs_placeholders

NAME = "tartaros"
BIN = "/usr/local/bin/tartaros"
HOST_REQUIRES = ["landlock"]  # the base sandbox on Linux is Landlock (+ seccomp)
REFUSAL = {"exit": [78], "stderr": "tartaros:"}  # 0.1.0-alpha.6+; was [2]
SYS_READ = ["/usr", "/lib", "/lib64", "/bin", "/sbin", "/etc", "/dev", "/proc"]


def identity():
    v = subprocess.run([BIN, "version"], capture_output=True, text=True)
    return {"version": (v.stdout or v.stderr).strip(), "license": "Apache-2.0",
            "commit": os.environ.get("SC_TARTAROS_COMMIT", "") + " (github.com/carlostapiacl/tartaros)",
            "conflict_of_interest": "maintained by the author of this lab"}


def check(c):
    p, unsupported, notes = c["policy"], [], []
    for k in ("glob_read_denies", "glob_denies"):
        for g in p.get(k, []):
            unsupported.append(f"{k} {g}: no glob engine on Linux (Landlock matches by inode); "
                               "tartaros refuses globs there")
    if p.get("allow_unix_socket_paths"):
        unsupported.append("allow_unix_socket_paths: only all-or-nothing --deny-unix")
    ph = needs_placeholders(c)
    if ph & {"effect_log", "state_dir"}:
        return {"needs_feature": "{effect_log}: the contract needs the log inside the agent's writable root; "
                                 "the runner cannot place it there yet"}
    return {"unsupported": unsupported, "notes": notes, "basis": basis(c)}


def flags(p):
    a = ["--strict"]
    granted = p.get("read_scope") == "granted"
    for w in p.get("writable_roots", []):
        a += ["--write", w]
    if granted:
        # Granted model: deny everything, re-open the system dirs, the roots and the
        # read_allows; the most specific rule wins.
        a += ["--read-deny", "/"]
        for r in SYS_READ + list(p.get("writable_roots", [])) + list(p.get("read_allows", [])):
            a += ["--read-allow", r]
    else:
        for d in p.get("read_denies", []):
            a += ["--read-deny", d]
        for r in p.get("read_allows", []):
            a += ["--read-allow", r]
    for d in p.get("write_denies", []):
        a += ["--write-deny", d]
    for port in p.get("local_ports", []):
        a += ["--port", str(port)]
    for d in p.get("allow_domains", []):
        a += ["--allow-domain", d]
    for k, flag in (("isolate_pids", "--isolate-pids"), ("isolate_process_info", "--isolate-proc"),
                    ("harden_syscalls", "--seccomp-strict"), ("materialize_absent_handoff", "--materialize")):
        if p.get(k):
            a.append(flag)
    if p.get("max_processes"):
        a += ["--max-procs", str(p["max_processes"])]
    if p.get("inherit_env"):
        a.append("--inherit-env")
    for k in p.get("env_passthrough", []):
        a += ["--env", k]
    return a


def broker_config(b, env):
    """A contract's [broker] as the [broker] table of a tartaros policy file. The
    token and the injected values go to the launcher's environment, where tartaros
    reads them by name (they never reach the agent); the token travels in the
    contract's header, X-Broker-Auth."""
    env["SC_BROKER_TOKEN"] = b["token"]
    q = json.dumps
    lines = ["[broker]", f"port = {int(b['port'])}", 'token_env = "SC_BROKER_TOKEN"',
             'auth_header = "X-Broker-Auth"',
             "allowed_hosts = [" + ", ".join(q(h) for h in b.get("allowed_hosts", [])) + "]",
             f"allow_internal = {'true' if b.get('allow_internal') else 'false'}"]
    for i, cap in enumerate(b.get("capability", [])):
        lines += ["[[broker.capability]]", f"prefix = {q(cap['prefix'])}", f"upstream = {q(cap['upstream_base'])}"]
        if cap.get("inject_header"):
            env[f"SC_BROKER_SECRET_{i}"] = cap.get("inject_value", "")
            lines += ["[[broker.capability.inject]]", f"header = {q(cap['inject_header'])}",
                      f'value_env = "SC_BROKER_SECRET_{i}"']
    return "\n".join(lines) + "\n"


def wrap(policy, m, c, env):
    base = [BIN, "run"] + flags(policy)
    if c.get("broker"):
        env = dict(env)
        b = json.loads(json.dumps(c["broker"]).replace("{root}", m.get("root", "{root}")))
        fd, path = tempfile.mkstemp(prefix="sc-tartaros-", suffix=".toml")
        with os.fdopen(fd, "w") as fh:
            fh.write(broker_config(b, env))
        os.chmod(path, 0o644)
        base += ["--config", path]
    masked = {}
    if c.get("masked_env"):
        # Masked credentials exist only in tartaros's sandbox-runtime schema
        # (`--settings`), next to the flags above; the network list goes with them,
        # since tartaros checks each credential's hosts against it.
        allow = list(policy.get("allow_domains", []))
        masked = masked_settings(c, allow)
    if masked:
        doc = {"network": {"allowedDomains": allow, "tlsTerminate": masked["tlsTerminate"]},
               "credentials": masked["credentials"]}
        fd, path = tempfile.mkstemp(prefix="sc-tartaros-", suffix=".json")
        with os.fdopen(fd, "w") as fh:
            json.dump(doc, fh, indent=1)
        os.chmod(path, 0o644)
        base += ["--settings", path]
    return {"argv": lambda cmd: base + ["--", "/bin/sh", "-c", cmd], "env": env}


def placeholders(c):
    return {"launcher_bin": BIN}
