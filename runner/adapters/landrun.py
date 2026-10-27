"""Adapter: landrun (Zouuup/landrun), a pure-Landlock CLI sandbox.

landrun wraps a command with Landlock filesystem and TCP rules and nothing else:
no namespaces, no seccomp, no proxy. Landlock is allow-only, so it is a
capability sandbox like nono, but thinner. It therefore cannot express a
`read_denies` / `write_denies` carved out of a granted area (those are
`unsupported`), while the granted model (`read_scope = "granted"`) maps directly:
grant the workspace and nothing else. Landlock needs no grant on a path's
ancestors to reach it (checked 2026-10-16: with only --rwx /t/work, the
workspace reads and writes, /t/home/secret and listing /t are denied).
On this host (kernel 6.8, Landlock ABI 4) its abstract-socket and signal scoping
(ABI v6) is unavailable, so it runs with `--best-effort`. That flag drops what
the kernel cannot enforce without saying so: with no Landlock at all landrun
confines nothing (HOST_REQUIRES), and below ABI 4 its TCP rules are dropped, so
network guarantees are reported unsupported there instead of measured.
"""
import os, subprocess
from common import basis, file_sha256, landlock_abi, needs_placeholders, wants_env_scrub

NAME = "landrun"
HOST_REQUIRES = ["landlock"]
BIN = "/usr/local/bin/landrun"
CORE_ENV = ["PATH", "HOME", "LANG", "TERM"]
SYS_ROX = ["/usr", "/bin", "/sbin", "/lib", "/lib64"]
SYS_RO = ["/etc", "/dev", "/proc"]
SYS_RWX = ["/dev/null"]


def identity():
    v = subprocess.run([BIN, "--version"], capture_output=True, text=True)
    ver = (v.stdout + v.stderr).strip().split()[-1] if (v.stdout or v.stderr) else "0.1.17"
    return {"version": ver, "commit": "github.com/Zouuup/landrun (release binary)", "license": "MIT",
            "artifact_sha256": file_sha256(BIN)}


def check(c):
    p, unsupported, notes = c["policy"], [], []
    if c.get("masked_env"):
        unsupported.append("masked_env: landrun has no credential proxy")
    if c.get("broker"):
        unsupported.append("broker: landrun has no credential proxy")
    if p.get("allow_domains"):
        unsupported.append("allow_domains: landrun has no egress proxy (only TCP port rules)")
    for d in p.get("write_denies", []):
        unsupported.append(f"write_denies {d}: Landlock is allow-only; a non-writable hole in a writable root cannot be expressed")
    for d in list(p.get("read_denies", [])) + list(p.get("glob_read_denies", [])):
        unsupported.append(f"read_denies {d}: Landlock is allow-only; a deny inside a readable area cannot be expressed")
    if landlock_abi() < 4 and (c["category"] == "network" or p.get("local_ports")):
        unsupported.append(f"network: Landlock ABI {landlock_abi()} on this host has no TCP rules, and "
                           "landrun --best-effort drops them silently")
    if p.get("isolate_pids"):
        unsupported.append("isolate_pids: landrun creates no PID namespace")
    if p.get("harden_syscalls"):
        unsupported.append("harden_syscalls: landrun has no seccomp layer (Landlock only)")
    if p.get("materialize_absent_handoff"):
        unsupported.append("materialize_absent_handoff: no such feature")
    if p.get("max_processes"):
        unsupported.append("max_processes: landrun has no resource limits")
    if p.get("isolate_process_info"):
        notes.append("isolate_process_info: landrun has no /proc isolation; by omission only")
    ph = needs_placeholders(c)
    if ph & {"effect_log", "state_dir", "launcher_bin"}:
        return {"needs_feature": "placeholder " + ",".join(ph) + " not provided for landrun"}
    return {"unsupported": unsupported, "notes": notes, "basis": basis(c)}


def wrap(policy, m, c, env):
    p = policy
    args = [BIN, "--best-effort"]
    # filesystem: writable roots are read-write-exec; read_allows read-only;
    # system dirs read+exec. In the neutral model everything else is readable
    # too, so grant --ro / ; in the granted model, grant nothing more.
    for w in p.get("writable_roots", []):
        args += ["--rwx", w]
    for r in p.get("read_allows", []):
        args += ["--ro", r]
    for d in SYS_ROX:
        args += ["--rox", d]
    for d in SYS_RO:
        args += ["--ro", d]
    for d in SYS_RWX:
        args += ["--rwx", d]
    # Neutral model: read everywhere. Granted model: nothing beyond the grants above.
    if p.get("read_scope") != "granted":
        args += ["--ro", "/"]
    # network: grant only the loopback ports asked for; otherwise deny all TCP.
    for port in p.get("local_ports", []):
        args += ["--connect-tcp", str(port)]
    # environment: landrun passes nothing unless named, so this is the scrub.
    if p.get("inherit_env"):
        passed = list(env.keys())
    elif p.get("env_passthrough"):
        passed = CORE_ENV + list(p["env_passthrough"])
    else:
        passed = CORE_ENV
    envargs = []
    for k in passed:
        if k in env:
            envargs += ["--env", f"{k}={env[k]}"]
    argv = args + envargs
    return {"argv": lambda cmd: argv + ["--", "/bin/sh", "-c", cmd], "env": env}
