"""The reference broker: what a contract's [broker] attack runs against when no
sandbox is in place (spec/format.md, "The [broker] table").

A contract about a credential broker cannot show its attack working "without a
sandbox": without one there is no broker. So in the baseline the runner stands
up this one, a broker written the obvious way with none of the defences the
contracts test for. It is the control group: an attack that does not get through
it proves nothing about the sandbox's broker (the case is vacuous), and one that
does is then run against the sandbox's own broker.

What it does, on purpose:

- no client token is checked, and every header the agent sends goes upstream
  (the token included), with the capability's header added after them;
- `/prefix…` is matched as a string prefix and the rest is appended to the
  upstream base as written: no path normalisation, no dot-segment check;
- any method is relayed; a redirect is followed, with the same headers;
- absolute-form requests and CONNECT go to whatever host the agent names, by
  name, with no allow-list and no internal-address check;
- whatever the agent sent after the request head is passed on as is;
- one connection at a time, with no timeouts.

Plain sockets only, so nothing in it normalises what the agent sent.
"""
import socket
import threading
from urllib.parse import urlsplit


def _read_head(conn):
    data = b""
    while b"\r\n\r\n" not in data:
        c = conn.recv(65536)
        if not c:
            break
        data += c
    head, _, rest = data.partition(b"\r\n\r\n")
    return head, rest


def _relay(a, b):
    try:
        while True:
            c = a.recv(65536)
            if not c:
                break
            b.sendall(c)
    except OSError:
        pass
    for s in (a, b):
        try:
            s.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass


def _exchange(host, port, raw):
    """Send `raw` to host:port and return everything it answers until it closes."""
    up = socket.create_connection((host, port))
    up.sendall(raw)
    out = b""
    while True:
        c = up.recv(65536)
        if not c:
            break
        out += c
    up.close()
    return out


def _request(method, url, headers, body):
    u = urlsplit(url)
    path = u.path or "/"
    if u.query:
        path += "?" + u.query
    lines = [f"{method} {path} HTTP/1.1".encode(), f"Host: {u.netloc}".encode()]
    lines += [h for h in headers if not h.lower().startswith((b"host:", b"connection:"))]
    lines.append(b"Connection: close")
    return u.hostname, u.port or 80, b"\r\n".join(lines) + b"\r\n\r\n" + body


def _location(resp):
    head = resp.split(b"\r\n\r\n", 1)[0].split(b"\r\n")
    if len(head[0].split(b" ")) > 1 and head[0].split(b" ")[1][:1] == b"3":
        for h in head[1:]:
            k, _, v = h.partition(b":")
            if k.strip().lower() == b"location":
                return v.strip().decode("latin-1")
    return None


def _handle(conn, spec):
    head, rest = _read_head(conn)
    lines = head.split(b"\r\n")
    parts = lines[0].decode("latin-1").split(" ")
    if len(parts) < 3:
        return
    method, target = parts[0], parts[1]
    headers = [h for h in lines[1:] if h]
    if method.upper() == "CONNECT":
        host, _, port = target.rpartition(":")
        up = socket.create_connection((host.strip("[]"), int(port)))
        conn.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")
        if rest:
            up.sendall(rest)
        t = threading.Thread(target=_relay, args=(up, conn), daemon=True)
        t.start()
        _relay(conn, up)
        t.join()
        return
    if target.startswith("/"):
        cap = next((c for c in spec.get("capability", []) if target.startswith(c["prefix"])), None)
        if cap is None:
            conn.sendall(b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
            return
        url = cap["upstream_base"].rstrip("/") + target[len(cap["prefix"]):]
        if cap.get("inject_header"):
            headers.append(f"{cap['inject_header']}: {cap.get('inject_value', '')}".encode())
    else:
        url = target
    resp = b""
    for _ in range(5):  # follows redirects, headers and all
        host, port, raw = _request(method, url, headers, rest)
        resp = _exchange(host, port, raw)
        nxt = _location(resp)
        if not nxt:
            break
        url = nxt
    conn.sendall(resp)


def start(spec):
    """Listen on spec["port"]; returns the stop functions, like the runner's servers."""
    ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ls.bind(("127.0.0.1", int(spec["port"])))
    ls.listen(64)
    stopped = threading.Event()

    def loop():
        while not stopped.is_set():
            try:
                conn, _ = ls.accept()
            except OSError:
                return
            try:
                _handle(conn, spec)
            except Exception:
                pass
            finally:
                try:
                    conn.close()
                except OSError:
                    pass

    threading.Thread(target=loop, daemon=True).start()

    def stop():
        stopped.set()
        try:
            ls.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        ls.close()

    return [stop]
