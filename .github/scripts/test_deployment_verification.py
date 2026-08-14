#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SHA = "0123456789abcdef0123456789abcdef01234567"
SOURCE_URL = f"https://github.com/withnative/surf/commit/{SHA}"


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


event_validation = load_module("validate_deployment_event")
deployment_verification = load_module("verify_production_deployment")


def valid_event() -> dict:
    return {
        "repository": {"full_name": "withnative/surf"},
        "deployment": {
            "id": 42,
            "sha": SHA,
            "ref": "main",
            "environment": "production",
        },
        "deployment_status": {
            "state": "success",
            "target_url": "https://railway.example/deployment/42",
            "environment_url": "https://surf.withnative.ai",
        },
    }


class EventValidationTests(unittest.TestCase):
    def test_accepts_only_the_expected_production_shape(self):
        values = event_validation.validate_event(
            valid_event(),
            repository="withnative/surf",
            environment="production",
            ref="main",
        )
        self.assertEqual(values["sha"], SHA)
        self.assertEqual(values["deployment_id"], "42")

    def test_rejects_untrusted_routing_and_sha_fields(self):
        mutations = [
            ("repository", "full_name", "attacker/fork"),
            ("deployment", "environment", "preview"),
            ("deployment", "ref", "feature/unreviewed"),
            ("deployment", "sha", "$(touch /tmp/not-safe)"),
            ("deployment_status", "state", "failure"),
        ]
        for section, key, value in mutations:
            with self.subTest(section=section, key=key):
                event = valid_event()
                event[section][key] = value
                with self.assertRaises(event_validation.EventValidationError):
                    event_validation.validate_event(
                        event,
                        repository="withnative/surf",
                        environment="production",
                        ref="main",
                    )

    def test_summary_neutralizes_event_controlled_markdown(self):
        event = valid_event()
        event["deployment_status"]["target_url"] = "`\n## forged heading"
        values = event_validation.validate_event(
            event,
            repository="withnative/surf",
            environment="production",
            ref="main",
        )
        self.assertNotIn("`", values["status_target_url"])
        self.assertNotIn("\n", values["status_target_url"])


class SurfHandler(BaseHTTPRequestHandler):
    html = b""
    css = b""

    def log_message(self, format, *args):  # noqa: A002, ANN001
        return

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/health":
            self._send(200, b"ok")
        elif path == "/source":
            self.send_response(307)
            self.send_header("Location", SOURCE_URL)
            body = f"Source {SOURCE_URL}; full Git commit {SHA}.".encode()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/":
            self._send(200, self.html, "text/html")
        elif path == "/assets/landing.css":
            self._send(200, self.css, "text/css")
        else:
            self._send(404, b"missing")

    def do_POST(self):
        if self.path != "/mcp":
            self._send(404, b"missing")
            return
        length = int(self.headers.get("Content-Length", "0"))
        request = json.loads(self.rfile.read(length))
        method = request["method"]
        if method == "initialize":
            result = {
                "protocolVersion": "2025-06-18",
                "serverInfo": {"name": "surf", "version": "0.1.0"},
                "instructions": f"Source {SOURCE_URL}; full Git commit {SHA}.",
            }
        elif method == "tools/list":
            result = {
                "tools": [
                    {"name": name}
                    for name in deployment_verification.EXPECTED_TOOLS
                ]
            }
        elif method == "resources/list":
            result = {
                "resources": [
                    {"uri": uri}
                    for uri in sorted(
                        deployment_verification.EXPECTED_FRAMEWORK_RESOURCES
                    )
                ]
            }
        elif method == "resources/read":
            result = {
                "contents": [
                    {
                        "uri": "surf://source",
                        "text": f"Source {SOURCE_URL}; full Git commit {SHA}.",
                    }
                ]
            }
        else:
            raise AssertionError(method)
        self._send(
            200,
            json.dumps(
                {"jsonrpc": "2.0", "id": request["id"], "result": result}
            ).encode(),
            "application/json",
        )

    def _send(self, status: int, body: bytes, content_type: str = "text/plain"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class DeepVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        landing = self.repo / "web/landing"
        landing.mkdir(parents=True)
        (landing / "index.html").write_bytes(
            b'<html><footer><a href="/source">Source</a></footer></html>\n'
        )
        (landing / "_landing.css").write_bytes(b"body { color: black; }\n")
        SurfHandler.html = (landing / "index.html").read_bytes()
        SurfHandler.css = (landing / "_landing.css").read_bytes()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), SurfHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def verifier(self):
        return deployment_verification.Verifier(
            base_url=self.base_url,
            expected_sha=SHA,
            repo_root=self.repo,
            legacy_urls=[self.base_url, self.base_url],
            timeout=2,
            allow_http=True,
        )

    def test_complete_contract_passes(self):
        completed = self.verifier().run()
        self.assertIn("HTTP source provenance", completed)
        self.assertIn("MCP resources", completed)
        self.assertIn("compiled landing assets", completed)

    def test_landing_byte_mismatch_fails(self):
        SurfHandler.css = b"different"
        with self.assertRaises(deployment_verification.VerificationError):
            self.verifier().run()

    def test_production_urls_must_be_https(self):
        with self.assertRaises(deployment_verification.VerificationError):
            deployment_verification.validate_base_url(self.base_url)


if __name__ == "__main__":
    unittest.main()
