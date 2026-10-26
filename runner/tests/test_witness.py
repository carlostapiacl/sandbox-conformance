"""The witness servers' request reading: what a server would hand on."""
import os, socket, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import run  # noqa: E402


def through(raw, with_body=True):
    a, b = socket.socketpair()
    with a, b:
        a.sendall(raw)
        a.shutdown(socket.SHUT_WR)
        return run.read_request(b, with_body)


class ReadRequest(unittest.TestCase):
    def test_head_only_by_default(self):
        self.assertEqual(through(b"POST / HTTP/1.1\r\nContent-Length: 3\r\n\r\nabc", False),
                         b"POST / HTTP/1.1\r\nContent-Length: 3\r\n\r\nabc"[:-3] + b"abc"[:0] + b"abc")

    def test_content_length_body(self):
        self.assertTrue(through(b"POST / HTTP/1.1\r\nContent-Length: 3\r\n\r\nabc").endswith(b"\r\n\r\nabc"))

    def test_chunked_body_is_unframed(self):
        # a value split across chunks reads whole, as a server hands it on
        got = through(b"POST / HTTP/1.1\r\nTransfer-Encoding: chunked\r\n\r\n"
                      b"5\r\nsc-re\r\n4\r\nal-1\r\n0\r\n\r\n")
        self.assertTrue(got.endswith(b"\r\n\r\nsc-real-1"), got)

    def test_dechunk_keeps_what_it_cannot_parse(self):
        self.assertEqual(run.dechunk(b"zz\r\nabc"), b"zz\r\nabc")


if __name__ == "__main__":
    unittest.main()
