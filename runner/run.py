#!/usr/bin/env python3
"""Run conformance contracts against one sandbox through its adapter.

Meant to run as root inside a throwaway Linux container. Each contract gets a
fresh {root}; the agent's commands run as an unprivileged user (uid 1500)
unless the contract requires root. Run as a normal user (the runner's own
tests), everything runs as that user and nothing is switched or killed by uid.

For every contract applicable to the host:
  1. baseline  - fixtures, then attack and control WITHOUT a sandbox.
                 If the attack does not succeed here the contract is VACUOUS.
  2. sandboxed - fresh fixtures, attack then control through the adapter,
                 then the [assert] effect.

The result of each case, and the procedure that assigns it, are defined in
spec/verdicts.md; runner/verdict.py implements that procedure. This file only
observes: it runs the phases and records what happened.
"""
import argparse, ctypes, glob, hashlib, importlib, json, os, platform, pwd, shutil
import posixpath, re, signal, socket, socketserver, subprocess, sys, threading, time, tomllib
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reference_broker  # noqa: E402
import verdict  # noqa: E402

AGENT = os.environ.get("SC_AGENT", "agent")
RUNS = os.environ.get("SC_RUNS", "/var/lib/sc/runs")
CFG = os.environ.get("SC_CFG", "/var/lib/sc/cfg")
PRIVILEGED = os.geteuid() == 0  # in the lab container: switch to AGENT per command
PROFILE = "strict"  # spec/verdicts.md §7: the adapters set every open option to its strictest
# §4.5: the policy of the probe that checks the sandbox starts at all on this host
MINIMAL_POLICY = {"writable_roots": ["{root}"]}
CMD_TIMEOUT = 60
OUT_LIMIT = 4000


# ---------------------------------------------------------------- host probes
def host_os():
    return {"Linux": "linux", "Darwin": "macos"}.get(platform.system(), platform.system().lower())


def agent_pw():
    """The account the agent's commands run as: AGENT in the lab, else whoever runs us."""
    return pwd.getpwnam(AGENT) if PRIVILEGED else pwd.getpwuid(os.getuid())


def landlock_abi():
    if host_os() != "linux":
        return 0
    try:
        libc = ctypes.CDLL(None, use_errno=True)
        # landlock_create_ruleset(NULL, 0, LANDLOCK_CREATE_RULESET_VERSION)
        r = libc.syscall(444, None, 0, 1)
        return r if r > 0 else 0
    except Exception:
        return 0


def host_stamp():
    def sh(c):
        try:
            return subprocess.run(c, shell=True, capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception:
            return ""
    return {
        "kernel": platform.release(),
        "os": sh(". /etc/os-release && echo $PRETTY_NAME"),
        "arch": platform.machine(),
        "landlock_abi": landlock_abi(),
        "bwrap": sh("bwrap --version"),
        "python": platform.python_version(),
        "container": os.environ.get("SC_CONTAINER_STAMP", ""),
        "agent_uid": agent_pw().pw_uid,
    }


def host_ip():
    """This host's own non-loopback IPv4, for a witness server a sandboxed process
    must not reach. A UDP connect only picks the route: no packet is sent."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("192.0.2.1", 9))
            ip = s.getsockname()[0]
    except OSError:
        return None
    return None if ip.startswith("127.") or ip == "0.0.0.0" else ip


def host_has(req, abi):
    if req == "landlock":
        return abi >= 1
    if req == "landlock-net":
        return abi >= 4
    if req == "userns":
        if host_os() != "linux":
            return False
        return subprocess.run(["unshare", "-Ur", "true"], capture_output=True,
                              preexec_fn=as_agent).returncode == 0
    if req == "root":
        return PRIVILEGED  # the attack runs as root, so the runner must be root
    if req == "non-root":
        return True  # chosen by running as the agent
    if req == "cgroup":
        return os.access("/sys/fs/cgroup/cgroup.procs", os.W_OK) and \
            os.path.exists("/sys/fs/cgroup/cgroup.subtree_control")
    if req == "host-ip":
        return host_ip() is not None
    if req == "gpu":
        return bool(glob.glob("/dev/dri/renderD*"))
    if req == "hosts-file":
        return os.access("/etc/hosts", os.W_OK)  # host_alias appends to it for the case
    return False


def as_agent():
    if not PRIVILEGED:
        return
    pw = agent_pw()
    os.setgroups([])
    os.setgid(pw.pw_gid)
    os.setuid(pw.pw_uid)


# ------------------------------------------------------------------ helpers
TOP_FIELDS = {"id", "source", "derived_from", "category", "severity", "os", "requires",
              "policy", "fixture", "late_fixture", "attack", "control", "assert",
              "broker", "server", "unix_server", "abstract_server", "signal",
              "canary_process", "host_process", "launcher_env", "expect_refusal",
              "control_requires_sandbox", "repeat", "host_alias"}
REQUIRED_FIELDS = ("id", "category", "severity", "os", "policy", "attack", "control")
ATTACK_FIELDS = {"cmd", "expect_exit", "blocked_exit"}
CONTROL_FIELDS = {"cmd", "expect_exit"}
ASSERT_FIELDS = {"unchanged", "absent", "alive", "absent_line", "settle_secs"}
POLICY_FIELDS = {"writable_roots", "read_scope", "write_denies", "read_denies", "read_allows",
                 "glob_read_denies", "glob_denies", "local_ports", "allow_domains",
                 "allow_unix_socket_paths", "isolate_process_info", "isolate_pids",
                 "harden_syscalls", "strict", "max_processes", "env_passthrough",
                 "inherit_env", "materialize_absent_handoff"}


def invalid(c):
    """§4.1. A misspelled key must fail loudly, never pass silently as a weaker policy."""
    unknown = [f"[{k}]" if isinstance(c.get(k), (dict, list)) else k for k in c if k not in TOP_FIELDS]
    for part, allowed in (("policy", POLICY_FIELDS), ("attack", ATTACK_FIELDS),
                          ("control", CONTROL_FIELDS), ("assert", ASSERT_FIELDS)):
        unknown += [f"{part}.{k}" for k in (c.get(part) or {}) if k not in allowed]
    bad = ["unknown field(s): " + ", ".join(unknown)] if unknown else []
    bad += [f"missing {k}" for k in REQUIRED_FIELDS if k not in c]
    for part in ("attack", "control"):
        if part in c and not c[part].get("cmd"):
            bad.append(f"[{part}] has no cmd")
    be = (c.get("attack") or {}).get("blocked_exit")
    be_ok = isinstance(be, list) and all(isinstance(x, int) for x in be)
    if be is not None and not be_ok:
        bad.append("attack.blocked_exit must be a list of exit statuses")
    if be_ok and c["attack"].get("expect_exit", 0) in be:
        bad.append("attack.blocked_exit contains expect_exit: one status cannot mean both outcomes")
    rp = c.get("repeat", 1)
    if not (isinstance(rp, int) and rp >= 1):
        bad.append("repeat must be a positive integer")
    if c.get("assert") and not verdict.has_assert(c):
        bad.append("[assert] names nothing observable")
    return bad


def sub(v, m):
    if isinstance(v, str):
        for k, x in m.items():
            v = v.replace("{" + k + "}", str(x))
        return v
    if isinstance(v, list):
        return [sub(x, m) for x in v]
    if isinstance(v, dict):
        return {k: sub(x, m) for k, x in v.items()}
    return v


def chown_tree(path, uid, gid):
    for dp, dns, fns in os.walk(path):
        for n in [dp] + [os.path.join(dp, x) for x in dns + fns]:
            try:
                os.lchown(n, uid, gid)
            except OSError:
                pass


def make_fixtures(fixtures, owner):
    for f in fixtures:
        p = f["path"]
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if "symlink_to" in f:
            os.symlink(f["symlink_to"], p)
        elif f.get("dir"):
            os.makedirs(p, exist_ok=True)
        else:
            with open(p, "w") as fh:
                fh.write(f.get("content", ""))
        if "mode" in f:
            os.chmod(p, int(str(f["mode"]), 8))


def snapshot(p):
    try:
        st = os.lstat(p)
    except FileNotFoundError:
        return {"exists": False}
    s = {"exists": True, "mode": st.st_mode, "mtime": st.st_mtime_ns, "uid": st.st_uid}
    if os.path.islink(p):
        s["link"] = os.readlink(p)
    elif os.path.isdir(p):
        s["list"] = sorted(os.listdir(p))
    elif os.path.isfile(p):
        with open(p, "rb") as fh:
            s["sha"] = hashlib.sha256(fh.read()).hexdigest()
    if hasattr(os, "listxattr"):  # Linux; macOS has no os.listxattr
        try:
            s["xattr"] = sorted(os.listxattr(p, follow_symlinks=False))
        except OSError:
            pass
    return s


def as_list(v):
    return v if isinstance(v, list) else [v]


def pid_alive(pid):
    try:
        os.kill(int(pid), 0)
        if not os.path.isdir("/proc/self"):
            return True  # no procfs (macOS): signal 0 is all we can ask
        with open(f"/proc/{pid}/stat") as fh:
            return fh.read().split()[2] != "Z"
    except (OSError, ValueError):
        return False


def clip(b):
    s = b.decode("utf-8", "replace") if isinstance(b, bytes) else (b or "")
    return s if len(s) <= OUT_LIMIT else s[:OUT_LIMIT] + f"...[{len(s) - OUT_LIMIT} more]"


# ----------------------------------------------------------- host-side fakes
class _Srv(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


REQUEST_LINE = re.compile(rb"^([A-Z]+) (\S+) HTTP/1\.[01]\r?$", re.M)


def normalized_path(target):
    """The path an ordinary server would serve for this request target: the
    authority of an absolute-form target dropped, percent-escapes undone, dot
    segments resolved (as a server does before routing)."""
    t = target.decode("latin-1")
    if "://" in t:
        t = "/" + t.split("://", 1)[1].partition("/")[2]
    t = urllib.parse.unquote(t.split("?", 1)[0])
    return posixpath.normpath("/" + t.lstrip("/")).replace("//", "/")


def start_tcp_server(spec):
    respond = spec.get("respond", "HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nok")
    log = spec.get("log") or spec.get("log_requests")
    log_paths = spec.get("log_paths")
    echo = spec.get("echo_headers")

    class H(socketserver.BaseRequestHandler):
        def handle(self):
            self.request.settimeout(2)
            data = b""
            try:
                while b"\r\n\r\n" not in data and len(data) < 65536:
                    c = self.request.recv(4096)
                    if not c:
                        break
                    data += c
            except OSError:
                pass
            if log:
                with open(log, "ab") as fh:
                    fh.write(data + b"\n")
                os.chmod(log, 0o644)
            if log_paths:
                # every request line in what arrived, a pipelined one included
                with open(log_paths, "a") as fh:
                    for _, target in REQUEST_LINE.findall(data):
                        fh.write(normalized_path(target) + "\n")
                os.chmod(log_paths, 0o644)
            out = respond.encode()
            if echo:
                body = data.split(b"\r\n\r\n", 1)[0]
                out = b"HTTP/1.1 200 OK\r\nContent-Length: %d\r\nConnection: close\r\n\r\n" % len(body) + body
            try:
                self.request.sendall(out)
            except OSError:
                pass

    s = _Srv((spec.get("bind", "127.0.0.1"), int(spec["port"])), H)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s.shutdown, s.server_close


def start_unix_server(path=None, abstract=None):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    if abstract:
        s.bind("\0" + abstract)
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        s.bind(path)
        os.chmod(path, 0o777)
        if PRIVILEGED:
            agent = agent_pw()
            os.chown(path, agent.pw_uid, agent.pw_gid)
    s.listen(8)
    s.settimeout(0.3)
    stop = threading.Event()

    def loop():
        while not stop.is_set():
            try:
                c, _ = s.accept()
                c.sendall(b"ok")
                c.close()
            except OSError:
                pass
        s.close()
    t = threading.Thread(target=loop, daemon=True)
    t.start()
    return stop.set, t.join


class World:
    """Everything outside the sandbox a contract asks the runner to provide."""

    def __init__(self, c, m, root_user, sandboxed=True):
        self.c, self.m, self.root_user, self.sandboxed = c, m, root_user, sandboxed
        self.stops, self.procs = [], []
        self.hosts_before = None

    def __enter__(self):
        c = self.c
        if c.get("host_alias"):
            # names the contract needs resolved (lookalike domains), for this case only
            with open("/etc/hosts") as fh:
                self.hosts_before = fh.read()
            with open("/etc/hosts", "a") as fh:
                for h in c["host_alias"]:
                    fh.write(f"\n{h['ip']} {h['name']}")
                fh.write("\n")
        if c.get("broker") and not self.sandboxed:
            # the baseline's broker: the reference one, without defences
            self.stops += reference_broker.start(sub(c["broker"], self.m))
        for sp in c.get("server", []):
            self.stops += start_tcp_server(sub(sp, self.m))
        for sp in c.get("unix_server", []):
            self.stops += start_unix_server(path=sub(sp["path"], self.m))
        for sp in c.get("abstract_server", []):
            self.stops += start_unix_server(abstract=sp["name"])
        for key in ("canary_process", "host_process"):
            for sp in c.get(key, []):
                env = base_env()
                env.update(dict(x.split("=", 1) for x in sp.get("env", [])))
                p = subprocess.Popen(sub(sp["cmd"], self.m), shell=True, env=env,
                                     preexec_fn=None if self.root_user else as_agent,
                                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL, start_new_session=True)
                self.procs.append(p)
                if key == "host_process":
                    self.m["host_pid"] = p.pid
        time.sleep(0.2 if (self.stops or self.procs) else 0)
        return self

    def __exit__(self, *a):
        for p in self.procs:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except OSError:
                pass
            p.wait()
        for f in self.stops:
            try:
                f()
            except Exception:
                pass
        if self.hosts_before is not None:
            with open("/etc/hosts", "w") as fh:
                fh.write(self.hosts_before)


def base_env():
    return {"PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "HOME": agent_pw().pw_dir, "LANG": "C.UTF-8", "TERM": "dumb"}


# ------------------------------------------------------------------ execution
def run_cmd(argv, env, root_user, timeout=CMD_TIMEOUT, late=None, sig=None, cwd=None):
    t0 = time.time()
    p = subprocess.Popen(argv, env=env, cwd=cwd, preexec_fn=None if root_user else as_agent,
                         stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, start_new_session=True)
    timers = []
    if late:
        for lf in late:
            def w(lf=lf):
                os.makedirs(os.path.dirname(lf["path"]), exist_ok=True)
                with open(lf["path"], "w") as fh:
                    fh.write(lf.get("content", ""))
                if PRIVILEGED and not root_user:
                    a = agent_pw()
                    os.chown(lf["path"], a.pw_uid, a.pw_gid)
            t = threading.Timer(lf.get("after_ms", 0) / 1000, w)
            t.start()
            timers.append(t)
    if sig:
        t = threading.Timer(sig.get("after_secs", 1),
                            lambda: p.poll() is None and os.kill(p.pid, getattr(signal, "SIG" + sig.get("sig", "TERM"))))
        t.start()
        timers.append(t)
    timed_out = False
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(p.pid, signal.SIGKILL)
        out, err = p.communicate()
    for t in timers:
        t.join()
    rc = p.returncode
    if rc is not None and rc < 0:
        rc = 128 - rc
    return {"argv": argv, "exit": rc, "timed_out": timed_out, "secs": round(time.time() - t0, 2),
            "stdout": clip(out), "stderr": clip(err)}


def kill_leftovers(root_user):
    # Only in the lab, where AGENT is a dedicated account. As a normal user this
    # would kill the user's own processes, so nothing is killed by uid.
    if PRIVILEGED and not root_user:
        subprocess.run(["pkill", "-KILL", "-u", AGENT], capture_output=True)


def effect_evidence(c, before, m):
    """What the [assert] finds changed after the attack (empty: no effect)."""
    a = c.get("assert") or {}
    bad = []
    for p in as_list(sub(a.get("unchanged", []), m)):
        if snapshot(p) != before.get(p):
            bad.append(f"changed:{p}")
    for p in as_list(sub(a.get("absent", []), m)):
        if os.path.lexists(p):
            bad.append(f"present:{p}")
    for p in as_list(sub(a.get("alive", []), m)):
        if not pid_alive(p):
            bad.append(f"dead:{p}")
    for al in as_list(sub(a.get("absent_line", []), m)):
        try:
            with open(al["file"]) as fh:
                hit = [ln.rstrip("\n") for ln in fh if re.search(al["pattern"], ln)]
        except OSError:
            hit = []
        if hit:
            bad.append(f"line:{al['file']}:{hit[0]}")
    return bad


def cwd_for(c, root):
    """The agent works in its workspace: the first writable root, if it is a
    directory; otherwise {root}. Some sandboxes derive protections from cwd."""
    w = sub((c["policy"].get("writable_roots") or ["{root}"])[0], {"root": root})
    return w if os.path.isdir(w) else root


def phase(c, adapter, sandboxed, root_user, workdir):
    """One full pass from a fresh state: root, fixtures, world, attack, control, assert."""
    root = workdir
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(root)
    m = {"root": root}
    if "{host_ip}" in repr(c):
        m["host_ip"] = host_ip()
    if hasattr(adapter, "placeholders"):
        m.update(adapter.placeholders(c))
    a = c.get("assert") or {}
    for p in as_list(sub(a.get("absent", []), m)):
        if not p.startswith(root) and os.path.lexists(p) and not os.path.isdir(p):
            os.unlink(p)  # a leftover from an earlier pass, outside {root}
    make_fixtures(sub(c.get("fixture", []), m), None)
    if PRIVILEGED:
        owner = pwd.getpwnam("root") if root_user else agent_pw()
        chown_tree(root, owner.pw_uid, owner.pw_gid)
    out = {"root": root}
    # The reference broker stands in for the sandbox's in the baseline, and in a
    # sandboxed phase too for a reference sandbox with no broker of its own.
    with World(c, m, root_user, sandboxed and not getattr(adapter, "REFERENCE_BROKER", False)) as w:
        m = w.m
        env = base_env()
        env.update(dict(x.split("=", 1) for x in c.get("launcher_env", [])))
        if root_user:
            env["HOME"] = "/root"
        before = {p: snapshot(p) for p in as_list(sub(a.get("unchanged", []), m))}
        wrap = None
        if sandboxed:
            # §4.5: first, does the sandbox start at all on this host? A
            # failure here is the lab's, never a result about confinement.
            # Same environment as the case (HOME=/root for a root contract): a
            # sandbox that rejects the agent's state dir as root is the probe's
            # fault, not the sandbox's.
            vw = adapter.wrap(sub(MINIMAL_POLICY, m), m, c, dict(env))
            if not vw.get("unsupported"):
                out["valid_probe"] = run_cmd(vw["argv"]("true"), vw.get("env", env), root_user, cwd=root)
                if out["valid_probe"]["exit"] != 0:
                    kill_leftovers(root_user)
                    return out
            wrap = adapter.wrap(sub(c["policy"], m), m, c, env)
            if wrap.get("unsupported"):
                out["unsupported"] = wrap["unsupported"]
                return out
            m.update(wrap.get("placeholders", {}))
            env = wrap.get("env", env)
            if c.get("expect_refusal"):
                out["refusal_probe"] = run_cmd(wrap["argv"]("true"), env, root_user, cwd=cwd_for(c, root))
                if out["refusal_probe"]["exit"] != 0:
                    kill_leftovers(root_user)
                    return out
        attack = sub(c["attack"]["cmd"], m)
        control = sub(c["control"]["cmd"], m)
        argv = (lambda cmd: wrap["argv"](cmd)) if sandboxed else (lambda cmd: ["/bin/sh", "-c", cmd])
        late = sub(c.get("late_fixture", []), m)
        out["attack"] = run_cmd(argv(attack), env, root_user, late=late, sig=c.get("signal"), cwd=cwd_for(c, root))
        time.sleep(a.get("settle_secs", 0))
        out["effect_evidence"] = effect_evidence(c, before, m)
        out["effect"] = bool(out["effect_evidence"])
        out["control"] = run_cmd(argv(control), env, root_user, cwd=cwd_for(c, root))
        out["control_ok"] = out["control"]["exit"] == c["control"].get("expect_exit", 0)
    kill_leftovers(root_user)
    return out


def safe_phase(c, adapter, sandboxed, root_user, workdir):
    """A lab exception becomes a recorded error, judged as harness-error (§4.4, §4.5)."""
    try:
        return phase(c, adapter, sandboxed, root_user, workdir)
    except Exception as e:
        kill_leftovers(root_user)
        return {"error": repr(e)}


def run_contract(c, adapter, abi):
    r = {"id": c.get("id"), "category": c.get("category"), "severity": c.get("severity"),
         "source": c.get("source"), "spec_version": verdict.SPEC_VERSION, "profile": PROFILE}
    if c.get("derived_from"):
        r["derived_from"] = c["derived_from"]
    bad = invalid(c)
    if bad:
        return {**r, "result": "invalid-contract", "reason": "; ".join(bad)}
    if host_os() not in c["os"]:
        return {**r, "result": "not-applicable", "reason": f"contract does not apply to {host_os()}"}
    missing = [q for q in c.get("requires", []) if not host_has(q, abi)]
    if missing:
        return {**r, "result": "not-applicable", "reason": "host lacks " + ",".join(missing)}
    # §4.2: what the sandbox itself needs from the host to confine anything. A
    # sandbox that degrades silently without it must not be measured as if it
    # confined (landrun's --best-effort runs unconfined without Landlock).
    lacking = [q for q in getattr(adapter, "HOST_REQUIRES", []) if not host_has(q, abi)]
    if lacking:
        return {**r, "result": "not-applicable",
                "reason": f"host lacks {','.join(lacking)}, which {adapter.NAME} needs to confine anything"}
    root_user = "root" in c.get("requires", [])
    r["ran_as"] = "root" if root_user else agent_pw().pw_name

    try:
        gap = adapter.check(c)
    except Exception as e:
        return {**r, "result": "harness-error", "reason": f"adapter error in check(): {e!r}"}
    if gap.get("needs_feature"):
        return {**r, "result": "needs-feature", "reason": gap["needs_feature"]}
    if gap.get("unsupported"):
        return {**r, "result": "unsupported", "reason": "; ".join(gap["unsupported"])}
    r["mapping_notes"] = gap.get("notes", [])
    r["basis"] = gap.get("basis", "configured")
    if c.get("control_requires_sandbox"):
        r["control_requires_sandbox"] = c["control_requires_sandbox"]

    work = os.path.join(RUNS, c["id"])
    base = safe_phase(c, adapter, False, root_user, work + ".base")
    r["baseline"] = base
    res, m, why = verdict.decide_baseline(c, base)
    r["judged_by"] = m
    if res:
        return {**r, "result": res, "reason": why}

    n = c.get("repeat", 1)
    runs, results = [], []
    for i in range(n):
        sb = safe_phase(c, adapter, True, root_user, work + ".sbx")
        res, why = verdict.decide_sandboxed(c, m, sb, getattr(adapter, "REFUSAL", None))
        runs.append(sb)
        results.append(res)
        if n > 1:
            sb["result"], sb["reason"] = res, why
    r["sandboxed"] = runs[0] if n == 1 else runs
    if n == 1:
        r["result"], r["reason"] = results[0], why
    else:
        r["result"], r["reason"] = verdict.combine(results)
    if not r["reason"]:
        del r["reason"]
    return r


def sha256_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sandbox", required=True)
    ap.add_argument("--contracts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "adapters"))
    adapter = importlib.import_module(args.sandbox.replace("-", "_"))
    os.makedirs(RUNS, exist_ok=True)
    os.makedirs(CFG, exist_ok=True)
    os.chmod(RUNS, 0o755)
    os.chmod(CFG, 0o755)
    abi = landlock_abi()
    files = sorted(glob.glob(os.path.join(args.contracts, "*", "*.toml")))
    results = []
    for f in files:
        with open(f, "rb") as fh:
            c = tomllib.load(fh)
        if args.only and c.get("id") not in args.only:
            continue
        r = run_contract(c, adapter, abi)
        r["file"] = os.path.relpath(f, os.path.dirname(args.contracts))
        r["contract_sha256"] = sha256_file(f)
        print(f"{r['result']:16} {c.get('id')}", flush=True)
        results.append(r)
    counts = {}
    for r in results:
        counts[r["result"]] = counts.get(r["result"], 0) + 1
    doc = {"sandbox": adapter.NAME, **adapter.identity(), "spec_version": verdict.SPEC_VERSION,
           "profile": PROFILE, "adapter_sha256": sha256_file(adapter.__file__),
           "runner_commit": os.environ.get("SC_COMMIT", ""), "host": host_stamp(),
           "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "counts": counts, "contracts": results}
    with open(args.out, "w") as fh:
        json.dump(doc, fh, indent=1)
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
