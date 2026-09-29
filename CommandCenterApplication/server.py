"""GET-only local HTTP surface. No approval, TEA, or mutation routes."""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from CommandCenterApplication.models import CommandCenterView
from CommandCenterApplication.presentation import public_json


ASSET_ROOT = Path(__file__).resolve().parent / "assets"
ROUTES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/assets/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/assets/app.js": ("app.js", "text/javascript; charset=utf-8"),
}


def make_handler(view: CommandCenterView):
    payload = public_json(view)

    class ReadOnlyHandler(BaseHTTPRequestHandler):
        server_version = "JOOCommandCenter/1"

        def _headers(self, status, content_type, length):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(length))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'self'; style-src 'self'; "
                "img-src 'self'; connect-src 'self'; frame-ancestors 'none'",
            )
            self.end_headers()

        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/api/v1/command-center":
                self._headers(200, "application/json; charset=utf-8", len(payload))
                self.wfile.write(payload)
                return
            route = ROUTES.get(path)
            if route is None:
                body = b"Not Found"
                self._headers(404, "text/plain; charset=utf-8", len(body))
                self.wfile.write(body)
                return
            body = (ASSET_ROOT / route[0]).read_bytes()
            self._headers(200, route[1], len(body))
            self.wfile.write(body)

        def do_HEAD(self):
            path = urlsplit(self.path).path
            if path == "/api/v1/command-center":
                self._headers(200, "application/json; charset=utf-8", len(payload))
                return
            route = ROUTES.get(path)
            if route is None:
                self._headers(404, "text/plain; charset=utf-8", 0)
                return
            body = (ASSET_ROOT / route[0]).read_bytes()
            self._headers(200, route[1], len(body))

        def _read_only(self):
            body = b"Read-only application: method not allowed"
            self._headers(405, "text/plain; charset=utf-8", len(body))
            self.wfile.write(body)

        do_POST = _read_only
        do_PUT = _read_only
        do_PATCH = _read_only
        do_DELETE = _read_only

        def log_message(self, _format, *_args):
            return

    return ReadOnlyHandler


def serve(*, view: CommandCenterView, host: str = "127.0.0.1", port: int = 8765):
    if host not in {"127.0.0.1", "::1", "localhost"}:
        raise ValueError("Command Center binds to loopback only")
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("port must be 1..65535")
    server = ThreadingHTTPServer((host, port), make_handler(view))
    try:
        server.serve_forever()
    finally:
        server.server_close()
