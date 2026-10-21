"""Adapter: OpenAI Codex CLI sandbox, Linux (bubblewrap + seccomp + no_new_privs).

Maps the neutral [policy] to a named permissions profile in a throwaway
$CODEX_HOME/config.toml and runs `codex sandbox -P conformance -C <cwd> -- sh -c <cmd>`.
Everything is readable (":root" = read, like the neutral default), writes only
where granted, a write-deny is a narrower "read" entry, a read-deny is "deny".
"""
import json, os, subprocess, uuid
from common import basis, needs_placeholders, tree_sha256, wants_env_scrub

NAME = "codex"
CFG = "/var/lib/sc/cfg"
CORE_ENV = ["PATH", "HOME", "LANG", "TERM"]
# The native binary, not the npm `codex` shim: the shim is a Node script, so a
# poisoned NODE_OPTIONS in the launcher env would break the shim, not the sandbox.
BIN = "/usr/local/lib/node_modules/@openai/codex/node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex"


# The commit each measured release was built from (its tag). A version not listed
# records "unknown commit" instead of borrowing another release's.
TAG_COMMIT = {"0.162.1": "092d3acd6bec3e3a14bdc7e7a2810ab628ab759d",
              "0.163.0": "83086188ae0614bd882818ff1aa23f3194962012"}


def identity():
    v = subprocess.run([BIN, "--version"], capture_output=True, text=True).stdout.strip().split()[-1]
    return {"version": v, "package": "@openai/codex@" + v,
            "commit": TAG_COMMIT.get(v, "unknown commit") + " (tag rust-v" + v + ", github.com/openai/codex)",
            "license": "Apache-2.0",
            "artifact_sha256": tree_sha256("/usr/local/lib/node_modules/@openai/codex")}  # the package, vendored binaries included


def check(c):
    p, unsupported, notes = c["policy"], [], []
    if c.get("broker"):
        unsupported.append("broker: no capability broker with per-prefix upstreams and injected headers")
    if p.get("local_ports"):
        unsupported.append("local_ports: network is on or off (or proxied by domain); no per-port loopback grant")
    if p.get("max_processes"):
        unsupported.append("max_processes: no process cap")
    if p.get("materialize_absent_handoff"):
        unsupported.append("materialize_absent_handoff: no such option (codex's own .git/.codex/.agents "
                           "read-only subpaths are fixed)")
    ph = needs_placeholders(c)
    if "effect_log" in ph or "state_dir" in ph:
        unsupported.append("effect log: `codex sandbox` keeps no audit/effect log of the run")
    if "launcher_bin" in ph:
        return {"needs_feature": "{launcher_bin}: the attack is written for a `<bin> run --write DIR -- cmd` "
                                 "CLI; codex's sandbox CLI takes a permissions profile, so it cannot run as written"}
    if p.get("allow_domains"):
        notes.append("allow_domains: experimental feature network_proxy + [network] domains")
    for k, why in {"isolate_process_info": "own PID namespace and fresh /proc (--unshare-pid)",
                   "isolate_pids": "own PID namespace (--unshare-pid)",
                   "harden_syscalls": "always-on seccomp (io_uring, ptrace, network syscalls when restricted)",
                   "strict": "no separate tier"}.items():
        if p.get(k):
            notes.append(f"{k}: {why}")
    return {"unsupported": unsupported, "notes": notes, "basis": basis(c)}


def q(s):
    return json.dumps(s)  # a JSON string is a valid TOML basic string


def config(p, c):
    # Granted model: start from the system read set only (":minimal"), so a path
    # that is not a writable root or a read_allow is unreadable. Otherwise read
    # everywhere (":root") and deny the secret, the neutral model.
    fs = {":minimal": "read"} if p.get("read_scope") == "granted" else {":root": "read"}
    for w in p.get("writable_roots", []):
        fs[w] = "write"
    for w in p.get("write_denies", []):
        fs[w] = "read"
    for r in p.get("read_allows", []):
        fs.setdefault(r, "read")
    for d in list(p.get("read_denies", [])) + list(p.get("glob_read_denies", [])):
        fs[d] = "deny"
    lines = ["default_permissions = \"conformance\"", ""]
    if p.get("allow_domains"):
        lines += ["[features]", "network_proxy = true", ""]
    lines += ["[permissions.conformance.filesystem]"] + [f"{q(k)} = {q(v)}" for k, v in fs.items()] + [""]
    lines += ["[permissions.conformance.network]"]
    if p.get("allow_domains"):
        lines += ["enabled = true", "mode = \"limited\"", "",
                  "[permissions.conformance.network.domains]"] + [f"{q(d)} = \"allow\"" for d in p["allow_domains"]]
    else:
        lines += ["enabled = false"]
    lines += ["", "[shell_environment_policy]"]
    if p.get("inherit_env"):
        lines += ["inherit = \"all\""]
    else:
        lines += ["inherit = \"all\"", "ignore_default_excludes = false",
                  "include_only = [" + ", ".join(q(v) for v in CORE_ENV + list(p.get("env_passthrough", []))) + "]"]
    return "\n".join(lines) + "\n"


def wrap(policy, m, c, env):
    home = os.path.join(CFG, f"codex-{c['id']}-{uuid.uuid4().hex[:6]}")
    os.makedirs(home)
    with open(os.path.join(home, "config.toml"), "w") as fh:
        fh.write(config(policy, c))
    os.chmod(home, 0o755)
    os.chmod(os.path.join(home, "config.toml"), 0o644)
    import pwd
    a = pwd.getpwnam("agent")
    os.chown(home, a.pw_uid, a.pw_gid)
    env = dict(env, CODEX_HOME=home)
    root = m["root"]
    w = (policy.get("writable_roots") or [root])[0]
    cwd = w if os.path.isdir(w) else root
    return {"argv": lambda cmd: [BIN, "sandbox", "-P", "conformance", "-C", cwd, "--", "/bin/sh", "-c", cmd],
            "env": env, "config": home}
