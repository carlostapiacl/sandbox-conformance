#!/usr/bin/env python3
"""Generate the by-omission variants from the translatable deny contracts.

A by-omission variant keeps the same attack, control and assert, but states the
policy in the granted model: `read_scope = "granted"` means only writable_roots,
read_allows and the runner's system paths are readable; there are no read_denies.
The protected secret lives outside every grant, so it is unreadable because
nobody granted it. Any non-secret path the control legitimately reads is granted
explicitly as a read_allow.
"""
import glob, tomllib, os, posixpath

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRACTS = os.path.join(ROOT, "contracts")

# The 24 translatable ids, with any extra read_allows their control needs
# (the specific non-secret path the control reads outside the workspace).
EXTRA_READ_ALLOWS = {
    "read-deny-backslash-name": ["{root}/tree/a/b"],
    "read-deny-bracket-dir": ["{root}/tree/u/a.env"],
    "read-deny-link-dotdot": ["{root}/here/file"],
    "secrets-read-deny-single-file": ["{root}/home/notes.txt"],
    "secrets-read-deny-symlinked-entry": ["{root}/dotfiles/vimrc"],
}
TRANSLATABLE = """filesystem-rm-under-read-deny-ancestor filesystem-write-reallow-inside-deny
read-allow-writable-carveout-trailing-slash ipc-unix-socket-in-denied-dir
isolation-root-mount-bypass-denied read-allow-symlink-into-deny read-allow-symlink-no-reopen
read-allow-trailing-slash-nested-deny read-deny-alt-spelling read-deny-around-nested-root
read-deny-backslash-name read-deny-bracket-dir read-deny-given-via-symlink read-deny-link-dotdot
read-deny-not-reopened-by-nested-writable secrets-read-allow-symlink-hop-no-widen
secrets-read-allow-symlink-into-deny
secrets-read-deny-dir-listing secrets-read-deny-on-symlinked-path
secrets-read-deny-path-special-chars secrets-read-deny-prefix-collision
secrets-read-deny-single-file secrets-read-deny-symlinked-entry""".split()


def q(s):
    import json
    return json.dumps(s)  # a JSON string is a valid TOML basic string


def arr(xs):
    return "[" + ", ".join(q(x) for x in xs) + "]"


def emit_policy(p, extra):
    lines = ["[policy]", 'read_scope = "granted"',
             "writable_roots = " + arr(p.get("writable_roots", ["{root}/work"]))]
    ra = list(p.get("read_allows", [])) + list(extra)
    if ra:
        lines.append("read_allows = " + arr(ra))
    # carry a resource/isolation field that is not about denies, if present
    for k in ("isolate_process_info", "isolate_pids", "harden_syscalls", "strict",
              "local_ports", "max_processes", "allow_unix_socket_paths"):
        if k in p:
            v = p[k]
            lines.append(f"{k} = " + (arr(v) if isinstance(v, list) else ("true" if v is True else str(v))))
    return "\n".join(lines)


def emit_fixture(fx):
    out = ["[[fixture]]", f'path = {q(fx["path"])}']
    if fx.get("dir"):
        out.append("dir = true")
    if "symlink_to" in fx:
        out.append(f'symlink_to = {q(fx["symlink_to"])}')
    if "content" in fx:
        out.append(f'content = {q(fx["content"])}')
    if "mode" in fx:
        out.append(f'mode = {q(str(fx["mode"]))}')
    return "\n".join(out)


def emit_cmd(name, block):
    out = [f"[{name}]", f'cmd = {q(block["cmd"])}']
    if "expect_exit" in block:
        out.append(f'expect_exit = {block["expect_exit"]}')
    return "\n".join(out)


def emit_assert(a):
    out = ["[assert]"]
    for k in ("unchanged", "absent", "alive"):
        if k in a:
            v = a[k]
            out.append(f"{k} = " + (arr(v) if isinstance(v, list) else q(v)))
    if "settle_secs" in a:
        out.append(f'settle_secs = {a["settle_secs"]}')
    return "\n".join(out)


def emit_table_array(name, items, keys):
    blocks = []
    for it in items:
        b = [f"[[{name}]]"]
        for k in keys:
            if k in it:
                v = it[k]
                b.append(f"{k} = " + (arr(v) if isinstance(v, list) else (str(v) if isinstance(v, int) else q(v))))
        blocks.append("\n".join(b))
    return "\n\n".join(blocks)


def main():
    byid = {}
    for f in glob.glob(os.path.join(CONTRACTS, "*", "*.toml")):
        byid[tomllib.load(open(f, "rb"))["id"]] = (f, open(f).read(), tomllib.load(open(f, "rb")))
    made = []
    for i in TRANSLATABLE:
        path, raw, c = byid[i]
        src_comment = raw.splitlines()[0] if raw.startswith("#") else f'# derived from {c["source"]}'
        p = c["policy"]
        parts = [
            f"{src_comment}",
            "# BY-OMISSION VARIANT: the granted model (read_scope = \"granted\"). The protected",
            "# path lives outside every grant, so it is unreadable because nobody granted it;",
            "# read_denies are not used. Same attack, control and assert as the original.",
            f'id = "{i}-by-omission"',
            f'source = {q(c["source"])}',
            f'derived_from = "{i}"',
            f'category = {q(c["category"])}',
            f'severity = {q(c["severity"])}',
            "os = " + arr(c["os"]),
        ]
        if c.get("requires"):
            parts.append("requires = " + arr(c["requires"]))
        parts.append("")
        parts.append(emit_policy(p, EXTRA_READ_ALLOWS.get(i, [])))
        parts.append("")
        for fx in c.get("fixture", []):
            parts.append(emit_fixture(fx)); parts.append("")
        if c.get("unix_server"):
            parts.append(emit_table_array("unix_server", c["unix_server"], ["path", "name", "port"])); parts.append("")
        if c.get("late_fixture"):
            parts.append(emit_table_array("late_fixture", c["late_fixture"], ["path", "content", "after_ms"])); parts.append("")
        parts.append(emit_cmd("attack", c["attack"])); parts.append("")
        parts.append(emit_cmd("control", c["control"]))
        if c.get("assert"):
            parts.append(""); parts.append(emit_assert(c["assert"]))
        out = "\n".join(parts).rstrip() + "\n"
        dst = os.path.join(os.path.dirname(path), f"{i}-by-omission.toml")
        open(dst, "w").write(out)
        made.append(os.path.relpath(dst, ROOT))
    print(f"generated {len(made)} variants")
    for m in made:
        print(" ", m)


if __name__ == "__main__":
    main()
