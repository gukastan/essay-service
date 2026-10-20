"""Owned local GET server for the safe-reader connection seam scenario."""

from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from queue import Queue
from threading import Thread
from typing import override


@dataclass(frozen=True, slots=True)
class PageWire:
    port: int
    requests: Queue[tuple[str, str]]


@contextmanager
def serve_page() -> Generator[PageWire]:
    requests: Queue[tuple[str, str]] = Queue()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            requests.put((self.path, self.headers["Host"]))
            body = b"<h1>Acme Engineer</h1><p>Build reliable systems.</p>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            _ = self.wfile.write(body)

        @override
        def log_message(self, format: str, *args: str | int) -> None:
            """Synthetic GET fixture never writes operation logs."""

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield PageWire(server.server_port, requests)
        finally:
            server.shutdown()
            thread.join(timeout=3)
            assert not thread.is_alive()
