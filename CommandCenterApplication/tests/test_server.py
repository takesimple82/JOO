from __future__ import annotations

import json
import unittest
from io import BytesIO
from pathlib import Path
from types import MethodType

from CommandCenterApplication.fixture import build_fixture_dataset
from CommandCenterApplication.projection import build_command_center_view
from CommandCenterApplication.server import make_handler, serve


class ReadOnlyServerTests(unittest.TestCase):
    def setUp(self):
        view = build_command_center_view(build_fixture_dataset())
        self.handler_class = make_handler(view)

    def request(self, method, path):
        handler = self.handler_class.__new__(self.handler_class)
        handler.path = path
        handler.wfile = BytesIO()
        handler.status = None
        handler.headers_sent = {}

        def send_response(instance, status):
            instance.status = status

        def send_header(instance, key, value):
            instance.headers_sent[key] = value

        handler.send_response = MethodType(send_response, handler)
        handler.send_header = MethodType(send_header, handler)
        handler.end_headers = MethodType(lambda _instance: None, handler)
        getattr(handler, "do_" + method)()
        return handler.status, handler.headers_sent, handler.wfile.getvalue()

    def test_get_api_returns_deterministic_read_only_view(self):
        status, headers, body = self.request("GET", "/api/v1/command-center")
        payload = json.loads(body)
        self.assertEqual(status, 200)
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertIn("default-src 'self'", headers["Content-Security-Policy"])
        self.assertEqual(payload["execution"]["state"], "LIVE_BLOCKED")

    def test_mutating_methods_are_rejected(self):
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            with self.subTest(method=method):
                status, _headers, body = self.request(method, "/api/v1/command-center")
                self.assertEqual(status, 405)
                self.assertIn(b"Read-only", body)

    def test_unknown_route_is_not_found(self):
        status, _headers, _body = self.request("GET", "/approve")
        self.assertEqual(status, 404)

    def test_non_loopback_bind_is_rejected_before_server_creation(self):
        with self.assertRaisesRegex(ValueError, "loopback"):
            serve(view=build_command_center_view(build_fixture_dataset()), host="0.0.0.0")

    def test_static_ui_has_no_mutation_controls_and_preserves_decimal_text(self):
        root = Path(__file__).resolve().parents[1] / "assets"
        html = (root / "index.html").read_text()
        script = (root / "app.js").read_text()
        self.assertNotIn("<form", html.casefold())
        self.assertNotIn("<button", html.casefold())
        self.assertNotIn("Number(v)", script)
        self.assertIn("LIVE BLOCKED", html)
        self.assertIn("FIXTURE", script)
        self.assertIn('id="ev"', html)
        self.assertIn('id="allocation"', html)


if __name__ == "__main__":
    unittest.main()
