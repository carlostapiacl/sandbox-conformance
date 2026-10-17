"""What every adapter shares: the neutral [policy] vocabulary and the runner
features a contract may declare."""
import ctypes, platform

# Every [policy] key a contract may use, and what it asks for.
POLICY_FIELDS = {
    "writable_roots": "paths the agent may write (everything else read-only)",
    "read_scope": "\"granted\": only writable_roots + read_allows + system paths are readable (no read_denies)",
    "write_denies": "paths inside a writable root that stay read-only",
    "read_denies": "paths the agent may not read",
    "read_allows": "paths re-opened for reading inside a read-deny",
    "glob_read_denies": "read-deny by glob pattern",
    "glob_denies": "read/write deny by glob pattern",
    "local_ports": "loopback TCP ports the agent may connect to (nothing else)",
    "allow_domains": "domains reachable through the sandbox's egress proxy",
    "allow_unix_socket_paths": "unix sockets the agent may connect to",
    "isolate_process_info": "other processes' /proc entries are not readable",
    "isolate_pids": "the agent runs in its own PID namespace",
    "harden_syscalls": "the sandbox's syscall hardening tier is on",
    "strict": "the sandbox's strictest mode",
    "max_processes": "cap on processes in the agent's tree",
    "env_passthrough": "only these launcher variables reach the agent",
    "inherit_env": "the agent inherits the launcher's whole environment",
    "materialize_absent_handoff": "absent trust-handoff paths are protected too",
}

# Contracts whose guarantee is not spelled out by any [policy] field: the
# result reflects what the sandbox does on its own (a default), and an escape
# there is a default difference, not a broken configured rule. The values are
# spec/verdicts.md §5 (v0 runs say "policy" / "built-in").
IMPLICIT_CATEGORIES = {"trust-handoff", "lifecycle", "isolation"}


def basis(c):
    p = c["policy"]
    if c["category"] in IMPLICIT_CATEGORIES and not (p.get("write_denies") or p.get("read_denies")):
        return "default"
    if c.get("launcher_env") and not p.get("inherit_env") and not p.get("env_passthrough"):
        return "default"
    return "configured"


def wants_env_scrub(c):
    """A launcher env is present and the policy does not say 'inherit all':
    the contract assumes an allowlist environment (only named vars pass)."""
    p = c["policy"]
    return bool(c.get("launcher_env")) and not p.get("inherit_env")


def needs_placeholders(c):
    import re
    text = repr(c.get("attack")) + repr(c.get("control"))
    return set(re.findall(r"\{(launcher_bin|effect_log|state_dir)\}", text))


def landlock_abi():
    """The host's Landlock ABI version, 0 when there is none (not Linux, not built in)."""
    if platform.system() != "Linux":
        return 0
    try:
        r = ctypes.CDLL(None, use_errno=True).syscall(444, None, 0, 1)  # LANDLOCK_CREATE_RULESET_VERSION
        return r if r > 0 else 0
    except Exception:
        return 0


def file_sha256(path):
    """sha256 of the file a command resolves to (symlinks followed), or "" if absent."""
    import hashlib, os, shutil
    p = shutil.which(path) or path
    try:
        with open(os.path.realpath(p), "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except OSError:
        return ""


def tree_sha256(root):
    """One sha256 over every file under root (relative path + content, sorted), so two
    installs of an npm package can be compared even if npm resolved them separately."""
    import hashlib, os
    h = hashlib.sha256()
    for dp, dns, fns in os.walk(root):
        dns.sort()
        for n in sorted(fns):
            p = os.path.join(dp, n)
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            h.update(os.path.relpath(p, root).encode() + b"\0")
            with open(p, "rb") as fh:
                h.update(hashlib.sha256(fh.read()).digest())
    return h.hexdigest() if os.path.isdir(root) else ""
