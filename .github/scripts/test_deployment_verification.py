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
BOT_ID = 68434857
BOT_LOGIN = "railway-app[bot]"
BOT_NODE_ID = "MDM6Qm90Njg0MzQ4NTc="
SERVICE_NAME = "native-learn"
PROJECT_ID = "f4d995a4-2c51-4860-8817-60f141b75b0c"
ENVIRONMENT_ID = "2255334a-771c-4024-a5b8-f7760f8d0144"
ENVIRONMENT_LABEL = "native-learn / production"
TARGET_URL = f"https://railway.com/project/{PROJECT_ID}?environmentId={ENVIRONMENT_ID}"
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
    bot = {
        "id": BOT_ID,
        "login": BOT_LOGIN,
        "node_id": BOT_NODE_ID,
        "type": "Bot",
    }
    repository_url = "https://api.github.com/repos/withnative/surf"
    deployment_url = f"{repository_url}/deployments/42"
    return {
        "action": "created",
        "sender": bot.copy(),
        "repository": {
            "id": 1333433853,
            "full_name": "withnative/surf",
            "default_branch": "main",
        },
        "deployment": {
            "id": 42,
            "url": deployment_url,
            "statuses_url": f"{deployment_url}/statuses",
            "repository_url": repository_url,
            "sha": SHA,
            "ref": SHA,
            "environment": ENVIRONMENT_LABEL,
            "original_environment": ENVIRONMENT_LABEL,
            "task": "deploy",
            "production_environment": False,
            "transient_environment": False,
            "creator": bot.copy(),
            "performed_via_github_app": None,
            "payload": {"environmentId": ENVIRONMENT_ID},
        },
        "deployment_status": {
            "id": 84,
            "url": f"{deployment_url}/statuses/84",
            "deployment_url": deployment_url,
            "repository_url": repository_url,
            "state": "success",
            "environment": ENVIRONMENT_LABEL,
            "creator": bot.copy(),
            "performed_via_github_app": None,
            "target_url": TARGET_URL,
            "log_url": TARGET_URL,
            "environment_url": TARGET_URL,
        },
    }


def validate(event: dict) -> dict[str, str]:
    return event_validation.validate_event(
        event,
        repository="withnative/surf",
        repository_id=1333433853,
        environment_label=ENVIRONMENT_LABEL,
        environment_id=ENVIRONMENT_ID,
        bot_id=BOT_ID,
        bot_login=BOT_LOGIN,
        bot_node_id=BOT_NODE_ID,
        service_name=SERVICE_NAME,
        project_id=PROJECT_ID,
    )


class EventValidationTests(unittest.TestCase):
    def test_accepts_only_the_expected_production_shape(self):
        values = validate(valid_event())
        self.assertEqual(values["sha"], SHA)
        self.assertEqual(values["deployment_id"], "42")

    def test_rejects_untrusted_routing_and_sha_fields(self):
        mutations = [
            (None, "action", "edited"),
            ("sender", "id", 1),
            ("repository", "id", 1),
            ("repository", "full_name", "attacker/fork"),
            ("repository", "default_branch", "trunk"),
            ("deployment", "environment", "preview"),
            ("deployment", "original_environment", "preview"),
            ("deployment", "task", "other"),
            ("deployment", "ref", OLD_SHA),
            ("deployment", "sha", "$(touch /tmp/not-safe)"),
            ("deployment_status", "state", "failure"),
            ("deployment_status", "environment", "preview"),
            ("deployment_status", "environment_url", "https://attacker.example"),
            ("deployment", "production_environment", True),
            ("deployment", "transient_environment", True),
            ("deployment", "id", True),
            ("deployment_status", "id", True),
            ("deployment", "creator", {"id": 1, "login": BOT_LOGIN, "node_id": BOT_NODE_ID, "type": "Bot"}),
            ("deployment_status", "creator", {"id": BOT_ID, "login": "wrong", "node_id": BOT_NODE_ID, "type": "Bot"}),
            ("deployment", "performed_via_github_app", {"id": 73253, "slug": "railway-app"}),
            ("deployment_status", "performed_via_github_app", {}),
            ("deployment", "payload", {"environmentId": "wrong"}),
            ("deployment", "payload", {"environmentId": ENVIRONMENT_ID, "extra": "wrong"}),
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
            f"http://railway.com/project/{PROJECT_ID}?environmentId={ENVIRONMENT_ID}",
            f"https://attacker.example/project/{PROJECT_ID}?environmentId={ENVIRONMENT_ID}",
            TARGET_URL.replace(PROJECT_ID, "wrong"),
            TARGET_URL.replace(ENVIRONMENT_ID, "wrong"),
            TARGET_URL + "&serviceId=unexpected",
            TARGET_URL + "`\n## forged heading",
        ]:
            with self.subTest(target_url=target_url):
                event = valid_event()
                event["deployment_status"]["target_url"] = target_url
                with self.assertRaises(event_validation.EventValidationError):
                    validate(event)

    def test_github_deployment_and_status_links_must_be_self_consistent(self):
        mutations = [
            ("deployment", "repository_url", "https://api.github.com/repos/attacker/fork"),
            ("deployment", "url", "https://api.github.com/repos/withnative/surf/deployments/1"),
            ("deployment", "statuses_url", "https://api.github.com/repos/withnative/surf/deployments/1/statuses"),
            ("deployment_status", "repository_url", "https://api.github.com/repos/attacker/fork"),
            ("deployment_status", "deployment_url", "https://api.github.com/repos/withnative/surf/deployments/1"),
            ("deployment_status", "url", "https://api.github.com/repos/withnative/surf/deployments/42/statuses/1"),
        ]
        for section, key, value in mutations:
            with self.subTest(section=section, key=key):
                event = valid_event()
                event[section][key] = value
                with self.assertRaises(event_validation.EventValidationError):
                    validate(event)

    def test_requires_the_captured_explicit_null_app_metadata(self):
        for section in ("deployment", "deployment_status"):
            with self.subTest(section=section):
                event = valid_event()
                del event[section]["performed_via_github_app"]
                with self.assertRaises(event_validation.EventValidationError):
                    validate(event)

    def test_all_three_railway_correlation_urls_are_required_and_must_agree(self):
        self.assertEqual(validate(valid_event())["status_target_url"], TARGET_URL)

        for key in ("target_url", "log_url", "environment_url"):
            with self.subTest(key=key):
                event = valid_event()
                event["deployment_status"][key] = None
                with self.assertRaises(event_validation.EventValidationError):
                    validate(event)

        event = valid_event()
        event["deployment_status"]["log_url"] = TARGET_URL.replace(
            ENVIRONMENT_ID, "wrong"
        )
        with self.assertRaises(event_validation.EventValidationError):
            validate(event)

    def test_deployment_ref_must_equal_the_validated_sha(self):
        event = valid_event()
        self.assertEqual(validate(event)["deployment_ref"], SHA)

        event["deployment"]["ref"] = "main"
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
