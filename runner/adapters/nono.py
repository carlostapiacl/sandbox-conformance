"""Adapter: nono (nolabs-ai/nono), Linux (Landlock + seccomp).

Maps the neutral [policy] to a nono profile (JSON, `--profile <file>`) and runs
`nono -s run --no-diagnostics --no-rollback --no-audit --profile <file> -- sh -c <cmd>`.

nono is allow-only (Landlock). The neutral baseline reads everything that is
not denied, so the adapter grants read on the whole test tree ({root}) plus
nono's system read set; writes only where granted. A read- or write-deny
INSIDE a grant is something Landlock cannot express (nono refuses to start
rather than ignore it), so such fields are recorded as capability gaps. nono's
own idiom (deny by omission: grant only the workspace) is not what the
neutral policy describes and was not measured here.
"""
import json, os, subprocess, uuid, platform
from common import basis, file_sha256, needs_placeholders, wants_env_scrub

NAME = "nono"
# On Linux its confinement is Landlock; without it there is nothing to measure.
HOST_REQUIRES = ["landlock"] if platform.system() == "Linux" else []
CFG = "/var/lib/sc/cfg"
BIN = "/usr/local/bin/nono"
CORE_ENV = ["PATH", "HOME", "LANG", "TERM"]


# The commit each measured release was built from (its tag). A version not listed
# records "unknown commit" instead of borrowing another release's.
TAG_COMMIT = {"0.80.0": "8bb041356d48f771a221e58c98d9b1ff442e76fe"}


def identity():
    v = subprocess.run([BIN, "--version"], capture_output=True, text=True).stdout.strip().split()[-1]
    return {"version": v, "commit": TAG_COMMIT.get(v, "unknown commit") + " (tag v" + v + ", github.com/nolabs-ai/nono)",
            "license": "Apache-2.0", "binary": f"nono-v{v}-x86_64-unknown-linux-gnu.tar.gz (release asset, SHA256SUMS verified)",
            "artifact_sha256": file_sha256(BIN)}


def check(c):
    p, unsupported, notes = c["policy"], [], []
    if c.get("masked_env"):
        unsupported.append("masked_env: not mapped; nono's credential proxy (--credential/--allow-endpoint) is a reverse proxy the tool is pointed at, not a sentinel swapped on egress to the real host")
    if c.get("broker"):
        unsupported.append("broker: nono's credential proxy (--credential/--allow-endpoint) is a reverse proxy "
                           "with its own routes and phantom tokens, not the contract's port/token/prefix interface")
    for d in p.get("write_denies", []):
        unsupported.append(f"write_denies {d}: nono has no write-only deny; a deny inside a writable grant "
                           "is refused on Linux (Landlock is allow-only)")
    for d in p.get("read_denies", []) + p.get("glob_read_denies", []):
        # The neutral baseline reads everything not denied; for nono that is a
        # read grant on the whole test tree, so every deny lies inside a grant.
        unsupported.append(f"read_denies {d}: a deny inside a readable grant; Landlock is allow-only and "
                           "nono refuses to start on such an overlap (its model is deny-by-omission)")
    if p.get("isolate_pids"):
        unsupported.append("isolate_pids: nono uses no PID namespace on Linux")
    if p.get("harden_syscalls"):
        notes.append("harden_syscalls: no separate tier; measured against nono's built-in filter "
                     "(no_new_privs, Landlock, a network seccomp filter)")
    if p.get("materialize_absent_handoff"):
        unsupported.append("materialize_absent_handoff: no such protection")
    if p.get("isolate_process_info"):
        notes.append("isolate_process_info: by omission — only /proc/self (and a few /proc files) are granted; "
                     "nono's process_info_mode itself is macOS-only")
    if p.get("strict"):
        notes.append("strict: no separate tier; the minimal profile below is the strictest")
    if p.get("max_processes"):
        notes.append("max_processes: --max-processes (cgroup v2 pids.max, supervised run)")
    ph = needs_placeholders(c)
    if "effect_log" in ph or "state_dir" in ph:
        return {"needs_feature": "{effect_log}: nono keeps an audit trail, but where a run's log lands "
                                 "was not wired into this adapter (por confirmar)"}
    return {"unsupported": unsupported, "notes": notes, "basis": basis(c)}


def profile(p, c):
    prof = {
        "meta": {"name": "conformance-" + c["id"]},
        # Drop the default profile's writable /tmp and the user tool dirs: only
        # the system read set plus explicit grants remain.
        "groups": {"exclude": ["system_write_linux", "user_tools", "homebrew_linux",
                               "dangerous_commands", "dangerous_commands_linux"]},
        "filesystem": {
            "allow": [x for x in p.get("writable_roots", [])],
            # Granted model (read_scope): only the workspace, the read_allows and
            # the system read set -- nono's own idiom. Otherwise the neutral model
            # grants read over the whole test tree.
            "read": ["/usr/local/bin"] + [x for x in p.get("read_allows", [])]
                    + ([] if p.get("read_scope") == "granted" else [c["_root"]]),
            "write_file": ["/dev/null"],
        },
        "workdir": {"access": "none"},
    }
    net = {}
    if p.get("allow_domains"):
        net["allow_domain"] = list(p["allow_domains"])
    elif p.get("local_ports"):
        net["block"] = True
        net["connect_port"] = list(p["local_ports"])
    else:
        net["block"] = True
    prof["network"] = net
    if p.get("env_passthrough"):
        prof["environment"] = {"allow_vars": CORE_ENV + list(p["env_passthrough"])}
    elif wants_env_scrub(c) or not p.get("inherit_env"):
        prof["environment"] = {"allow_vars": CORE_ENV}
    return prof


def wrap(policy, m, c, env):
    cfg = os.path.join(CFG, f"nono-{c['id']}-{uuid.uuid4().hex[:6]}.json")
    prof = profile(policy, dict(c, _root=m["root"]))
    # Files and directories are granted with different keys; nono fails hard
    # on a grant that does not exist, which is part of what gets measured.
    fs = prof["filesystem"]
    for key, fkey in (("allow", "allow_file"), ("read", "read_file")):
        keep = []
        for x in fs[key]:
            (fs.setdefault(fkey, []) if os.path.isfile(x) else keep).append(x)
        fs[key] = keep
    with open(cfg, "w") as fh:
        json.dump(prof, fh, indent=1)
    os.chmod(cfg, 0o644)
    extra = []
    if policy.get("max_processes"):
        extra += ["--max-processes", str(policy["max_processes"])]
    base = [BIN, "-s", "run", "--no-diagnostics", "--no-rollback", "--no-audit", "--profile", cfg] + extra
    return {"argv": lambda cmd: base + ["--", "/bin/sh", "-c", cmd], "env": env, "config": cfg}


def placeholders(c):
    return {"launcher_bin": BIN}
