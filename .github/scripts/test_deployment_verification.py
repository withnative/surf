#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SHA = "0123456789abcdef0123456789abcdef01234567"
SOURCE_URL = f"https://github.com/withnative/surf/commit/{SHA}"
OLD_SHA = "ffffffffffffffffffffffffffffffffffffffff"
INSTALLATION_ID = 122756225
APP_ID = 73253
APP_SLUG = "railway-app"
SERVICE_ID = "f73c4cbb-99a7-4716-a4a3-19bc91ca261a"
PROJECT_ID = "f4d995a4-2c51-4860-8817-60f141b75b0c"
TARGET_URL = (
    f"https://railway.com/project/{PROJECT_ID}/service/{SERVICE_ID}"
    "?environmentId=production"
)
TOOLS = ["quickstart", "get_guide", "get_reference", "get_doc"]
RESOURCES = [
    "surf://framework/quickstart",
    "surf://framework/manifest",
    "surf://guide/setting-up",
    "surf://guide/returning-and-capture",
    "surf://guide/evidence-review",
    "surf://guide/intensive-foundation",
    "surf://guide/teaching-and-practice",
    "surf://reference/shared-map-of-development",
    "surf://reference/context-and-local-practice",
    "surf://reference/capabilities",
    "surf://reference/supporting-literacies",
    "surf://reference/builds",
    "surf://changelog",
    "surf://source",
]


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


event_validation = load_module("validate_deployment_event")
deployment_verification = load_module("verify_production_deployment")


def valid_event() -> dict:
    return {
        "action": "created",
        "installation": {"id": INSTALLATION_ID},
        "repository": {"full_name": "withnative/surf"},
        "deployment": {
            "id": 42,
            "sha": SHA,
            "ref": "main",
            "environment": "production",
            "production_environment": True,
            "transient_environment": False,
            "performed_via_github_app": {"id": APP_ID, "slug": APP_SLUG},
            "payload": {"serviceId": SERVICE_ID, "projectId": PROJECT_ID},
        },
        "deployment_status": {
            "state": "success",
            "environment": "production",
            "performed_via_github_app": {"id": APP_ID, "slug": APP_SLUG},
            "target_url": TARGET_URL,
            "environment_url": "https://surf.withnative.ai",
        },
    }


def validate(event: dict) -> dict[str, str]:
    return event_validation.validate_event(
        event,
        repository="withnative/surf",
        environment="production",
        ref="main",
        installation_id=INSTALLATION_ID,
        app_id=APP_ID,
        app_slug=APP_SLUG,
        service_id=SERVICE_ID,
        project_id=PROJECT_ID,
        allow_empty_ref=True,
    )


class EventValidationTests(unittest.TestCase):
    def test_accepts_only_the_expected_production_shape(self):
        values = validate(valid_event())
        self.assertEqual(values["sha"], SHA)
        self.assertEqual(values["deployment_id"], "42")

    def test_rejects_untrusted_routing_and_sha_fields(self):
        mutations = [
            (None, "action", "edited"),
            ("installation", "id", 1),
            ("repository", "full_name", "attacker/fork"),
            ("deployment", "environment", "preview"),
            ("deployment", "ref", "feature/unreviewed"),
            ("deployment", "sha", "$(touch /tmp/not-safe)"),
            ("deployment_status", "state", "failure"),
            ("deployment_status", "environment", "preview"),
            ("deployment_status", "environment_url", "https://attacker.example"),
            ("deployment", "production_environment", False),
            ("deployment", "transient_environment", True),
            ("deployment", "id", True),
            ("deployment", "performed_via_github_app", None),
            ("deployment", "performed_via_github_app", {"id": 1, "slug": APP_SLUG}),
            ("deployment_status", "performed_via_github_app", {"id": APP_ID, "slug": "wrong"}),
            ("deployment", "payload", {"serviceId": "wrong", "projectId": PROJECT_ID}),
            ("deployment", "payload", {"serviceId": SERVICE_ID, "projectId": "wrong"}),
        ]
        for section, key, value in mutations:
            with self.subTest(section=section, key=key):
                event = valid_event()
                if section is None:
                    event[key] = value
                else:
                    event[section][key] = value
                with self.assertRaises(event_validation.EventValidationError):
                    validate(event)

    def test_rejects_unsafe_or_wrong_correlation_urls(self):
        for target_url in [
            "http://railway.com/project/x/service/y",
            f"https://attacker.example/project/{PROJECT_ID}/service/{SERVICE_ID}",
            f"https://railway.com/project/wrong/service/{SERVICE_ID}",
            f"https://railway.com/project/{PROJECT_ID}/service/wrong",
            TARGET_URL + "`\n## forged heading",
        ]:
            with self.subTest(target_url=target_url):
                event = valid_event()
                event["deployment_status"]["target_url"] = target_url
                with self.assertRaises(event_validation.EventValidationError):
                    validate(event)

    def test_project_identity_can_come_from_payload_or_correlation_url(self):
        event = valid_event()
        del event["deployment"]["payload"]["projectId"]
        self.assertEqual(validate(event)["status_target_url"], TARGET_URL)

        event = valid_event()
        event["deployment_status"]["target_url"] = None
        self.assertEqual(validate(event)["status_target_url"], "unavailable")

        event = valid_event()
        del event["deployment"]["payload"]["projectId"]
        event["deployment_status"]["target_url"] = None
        with self.assertRaises(event_validation.EventValidationError):
            validate(event)

        event = valid_event()
        event["deployment_status"]["target_url"] = ""
        event["deployment_status"]["log_url"] = TARGET_URL
        self.assertEqual(validate(event)["status_target_url"], TARGET_URL)

        event["deployment_status"]["target_url"] = TARGET_URL.replace(
            SERVICE_ID, "wrong"
        )
        with self.assertRaises(event_validation.EventValidationError):
            validate(event)

    def test_empty_sha_ref_is_allowed_but_other_branches_are_not(self):
        event = valid_event()
        event["deployment"]["ref"] = ""
        self.assertEqual(validate(event)["deployment_ref"], "(empty SHA ref)")

        event["deployment"]["ref"] = "feature/unreviewed"
        with self.assertRaises(event_validation.EventValidationError):
            validate(event)


class SurfHandler(BaseHTTPRequestHandler):
    html = b""
    css = b""
    health_failures = 0
    source_failures = 0
    css_requests = 0

    def log_message(self, format, *args):  # noqa: A002, ANN001
        return

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/health":
            if self.health_failures:
                type(self).health_failures -= 1
                self._send(503, b"starting")
            else:
                self._send(200, b"ok")
        elif path == "/source":
            self.send_response(307)
            stale = self.source_failures > 0
            if stale:
                type(self).source_failures -= 1
            source_url = (
                f"https://github.com/withnative/surf/commit/{OLD_SHA}"
                if stale
                else SOURCE_URL
            )
            source_sha = OLD_SHA if stale else SHA
            self.send_header("Location", source_url)
            body = f"Source {source_url}; full Git commit {source_sha}.".encode()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/":
            self._send(200, self.html, "text/html")
        elif path == "/assets/landing.css":
            type(self).css_requests += 1
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
                    for name in TOOLS
                ]
            }
        elif method == "resources/list":
            result = {
                "resources": [
                    {"uri": uri}
                    for uri in sorted(
                        RESOURCES
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
        contract_dir = self.repo / ".github"
        contract_dir.mkdir()
        (contract_dir / "deployment-contract.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "protocolVersion": "2025-06-18",
                    "serverName": "surf",
                    "tools": TOOLS,
                    "requiredResources": RESOURCES,
                    "landing": {
                        "html": "web/landing/index.html",
                        "css": "web/landing/_landing.css",
                        "sourceLink": 'href="/source"',
                    },
                }
            ),
            encoding="utf-8",
        )
        SurfHandler.html = (landing / "index.html").read_bytes()
        SurfHandler.css = (landing / "_landing.css").read_bytes()
        SurfHandler.health_failures = 0
        SurfHandler.source_failures = 0
        SurfHandler.css_requests = 0
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), SurfHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def verifier(self, *, retry_delays=(), sleep=lambda _: None):
        return deployment_verification.Verifier(
            base_url=self.base_url,
            expected_sha=SHA,
            repo_root=self.repo,
            legacy_urls=[self.base_url, self.base_url],
            timeout=2,
            allow_http=True,
            retry_delays=retry_delays,
            sleep=sleep,
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

    def test_transient_health_and_stale_source_retry_without_real_sleep(self):
        SurfHandler.health_failures = 1
        SurfHandler.source_failures = 1
        sleeps = []
        completed = self.verifier(
            retry_delays=(0, 0), sleep=sleeps.append
        ).run()
        self.assertIn("HTTP source provenance", completed)
        self.assertEqual(sleeps, [0, 0])

    def test_persistent_mismatch_fails_after_bounded_retry_window(self):
        SurfHandler.css = b"different"
        with self.assertRaisesRegex(
            deployment_verification.VerificationError,
            "verification failed after 3 attempts",
        ):
            self.verifier(retry_delays=(0, 0)).run()
        self.assertEqual(SurfHandler.css_requests, 3)

    def test_contract_is_commit_scoped_with_explicit_f1_fallback(self):
        contract = deployment_verification.load_contract(
            self.repo, deployment_verification.KNOWN_PRE_VERIFIER_SHA
        )
        self.assertEqual(contract.tools, tuple(TOOLS))

        (self.repo / ".github/deployment-contract.json").unlink()
        legacy = deployment_verification.load_contract(
            self.repo, deployment_verification.KNOWN_PRE_VERIFIER_SHA
        )
        self.assertEqual(legacy.tools, tuple(TOOLS))
        with self.assertRaises(deployment_verification.VerificationError):
            deployment_verification.load_contract(self.repo, SHA)

    def test_production_urls_must_be_https(self):
        with self.assertRaises(deployment_verification.VerificationError):
            deployment_verification.validate_base_url(self.base_url)


if __name__ == "__main__":
    unittest.main()
