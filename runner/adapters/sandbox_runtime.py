"""Adapter: Anthropic sandbox-runtime (`srt`), Linux (bubblewrap + seccomp + proxies).

Maps the neutral [policy] to an srt settings file and runs
`srt --settings <file> -c <cmd>`. Strict, idiomatic configuration: no network
unless a field grants it, writes only where granted, srt's own mandatory
protections left on (they cannot be turned off).
"""
import json, os, shlex, subprocess, uuid
from common import basis, masked_settings, needs_placeholders, tree_sha256, wants_env_scrub

NAME = "sandbox-runtime"
CFG = "/var/lib/sc/cfg"


# The commit each measured release was built from (its tag). A version not listed
# records "unknown commit" instead of borrowing another release's.
TAG_COMMIT = {"0.0.79": "d9aac2098351ca17f3743fbaf6ecbd0051b7e00e",
              "0.0.81": "c40cf14a65d025e3cd27f071f13a73c12b3b1f92"}


def identity():
    v = subprocess.run(["srt", "--version"], capture_output=True, text=True).stdout.strip()
    return {"version": v, "package": "@anthropic-ai/sandbox-runtime@" + v,
            "commit": TAG_COMMIT.get(v, "unknown commit") + " (tag v" + v + ", github.com/anthropics/sandbox-runtime)",
            "license": "Apache-2.0",
            "artifact_sha256": tree_sha256("/usr/local/lib/node_modules/@anthropic-ai/sandbox-runtime")}


BUILT_IN = {
    "isolate_process_info": "always on: own PID namespace and fresh /proc",
    "isolate_pids": "always on: own PID namespace",
    "harden_syscalls": "always on: seccomp filter (AF_UNIX socket creation, io_uring) via apply-seccomp",
    "strict": "no separate strict tier; the default is already the strictest",
    "materialize_absent_handoff": "always on: absent mandatory-deny paths are mounted over",
    "inherit_env": "srt passes the launcher environment through as-is",
}


def check(c):
    p, unsupported, notes = c["policy"], [], []
    if c.get("broker"):
        unsupported.append("broker: no capability broker with per-prefix upstreams and injected "
                           "headers (srt's credential masking/injection works through its MITM proxy, a different interface)")
    if p.get("max_processes"):
        unsupported.append("max_processes: no process cap")
    if p.get("env_passthrough"):
        unsupported.append("env_passthrough: no allowlist environment; srt can only deny named variables")
    elif wants_env_scrub(c):
        unsupported.append("environment scrub: srt inherits the launcher environment; an allowlist "
                           "(only named variables pass) is not expressible, only per-name denies")
    if p.get("allow_unix_socket_paths"):
        unsupported.append("allow_unix_socket_paths: ignored on Linux (seccomp cannot filter by path)")
    ph = needs_placeholders(c)
    if "effect_log" in ph or "state_dir" in ph:
        unsupported.append("effect log: srt keeps no audit/effect log of its own")
    if "launcher_bin" in ph:
        return {"needs_feature": "{launcher_bin}: the attack is written for a `<bin> run --write DIR -- cmd` "
                                 "CLI; srt's CLI takes a settings file, so the contract cannot be run as written"}
    for k, why in BUILT_IN.items():
        if p.get(k):
            notes.append(f"{k}: {why}")
    return {"unsupported": unsupported, "notes": notes, "basis": basis(c)}


def settings(p):
    allow = []
    for port in p.get("local_ports", []):
        allow += [f"127.0.0.1:{port}", f"localhost:{port}"]
    allow += list(p.get("allow_domains", []))
    sys_read = ["/usr", "/lib", "/lib64", "/bin", "/sbin", "/etc", "/dev", "/proc"]
    if p.get("read_scope") == "granted":
        # Granted model: nothing is readable but the system dirs, the writable
        # roots and the read_allows. The secret is under "/" and never re-opened.
        fs = {
            "denyRead": ["/"],
            "allowRead": sys_read + list(p.get("writable_roots", [])) + list(p.get("read_allows", [])),
            "allowWrite": list(p.get("writable_roots", [])),
            "denyWrite": list(p.get("write_denies", [])),
        }
    else:
        fs = {
            "denyRead": list(p.get("read_denies", [])) + list(p.get("glob_read_denies", [])),
            "allowRead": list(p.get("read_allows", [])),
            "allowWrite": list(p.get("writable_roots", [])),
            "denyWrite": list(p.get("write_denies", [])),
        }
    return {"network": {"allowedDomains": allow, "deniedDomains": []}, "filesystem": fs}


def wrap(policy, m, c, env):
    cfg = os.path.join(CFG, f"srt-{c['id']}-{uuid.uuid4().hex[:6]}.json")
    s = settings(policy)
    masked = masked_settings(c, s["network"]["allowedDomains"])
    if masked:
        s["credentials"] = masked["credentials"]
        s["network"]["tlsTerminate"] = masked["tlsTerminate"]
    with open(cfg, "w") as fh:
        json.dump(s, fh, indent=1)
    os.chmod(cfg, 0o644)
    return {"argv": lambda cmd: ["srt", "--settings", cfg, "-c", cmd],
            "env": env, "config": cfg}
