#!/usr/bin/env python3
"""Verify Surf's public HTTP, MCP, provenance, and compiled landing surfaces."""

from __future__ import annotations

import argparse
import json
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

FULL_SHA = re.compile(r"[0-9a-f]{40}")
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
PROTOCOL_VERSION = "2025-06-18"
EXPECTED_TOOLS = ["quickstart", "get_guide", "get_reference", "get_doc"]
EXPECTED_FRAMEWORK_RESOURCES = {
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
}


class VerificationError(RuntimeError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def validate_sha(value: str) -> str:
    if FULL_SHA.fullmatch(value) is None:
        raise VerificationError("expected SHA must be 40 lowercase hexadecimal characters")
    return value


def validate_base_url(value: str, *, allow_http: bool = False) -> str:
    parsed = urllib.parse.urlsplit(value)
    allowed_schemes = {"https", "http"} if allow_http else {"https"}
    if parsed.scheme not in allowed_schemes or not parsed.netloc:
        raise VerificationError("verification base URLs must be absolute HTTPS URLs")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise VerificationError("verification base URLs cannot contain credentials or suffixes")
    return value.rstrip("/")


class Verifier:
    def __init__(
        self,
        *,
        base_url: str,
        expected_sha: str,
        repo_root: Path,
        legacy_urls: list[str],
        timeout: float = 15,
        allow_http: bool = False,
    ) -> None:
        self.base_url = validate_base_url(base_url, allow_http=allow_http)
        self.sha = validate_sha(expected_sha)
        self.source_url = f"https://github.com/withnative/surf/commit/{self.sha}"
        self.repo_root = repo_root.resolve(strict=True)
        self.legacy_urls = [
            validate_base_url(url, allow_http=allow_http) for url in legacy_urls
        ]
        self.timeout = timeout
        context = ssl.create_default_context()
        self.opener = urllib.request.build_opener(
            NoRedirect(), urllib.request.HTTPSHandler(context=context)
        )
        self.completed: list[str] = []

    def _url(self, base: str, path: str) -> str:
        return f"{base}{path}"

    def _request(
        self,
        url: str,
        *,
        method: str = "GET",
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
        expected_status: int = 200,
    ) -> tuple[bytes, Any]:
        request_headers = {
            "Accept-Encoding": "identity",
            "User-Agent": "surf-production-verifier/1",
        }
        if headers:
            request_headers.update(headers)
        request = urllib.request.Request(
            url, data=body, headers=request_headers, method=method
        )
        try:
            response = self.opener.open(request, timeout=self.timeout)
        except urllib.error.HTTPError as error:
            response = error
        except (OSError, urllib.error.URLError) as error:
            raise VerificationError(f"request failed for {url}: {error}") from error

        with response:
            status = response.status
            response_body = response.read(MAX_RESPONSE_BYTES + 1)
            response_headers = response.headers
        if len(response_body) > MAX_RESPONSE_BYTES:
            raise VerificationError(f"response exceeded size limit for {url}")
        if status != expected_status:
            raise VerificationError(
                f"{url} returned HTTP {status}; expected {expected_status}"
            )
        return response_body, response_headers

    def _json_rpc(self, method: str, params: dict[str, Any], request_id: int) -> Any:
        body = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": method,
                "params": params,
            },
            separators=(",", ":"),
        ).encode()
        response_body, _ = self._request(
            self._url(self.base_url, "/mcp"),
            method="POST",
            body=body,
            headers={
                "Content-Type": "application/json",
                "MCP-Protocol-Version": PROTOCOL_VERSION,
            },
        )
        try:
            response = json.loads(response_body)
        except json.JSONDecodeError as error:
            raise VerificationError(f"{method} returned invalid JSON") from error
        if not isinstance(response, dict) or response.get("id") != request_id:
            raise VerificationError(f"{method} returned an invalid JSON-RPC envelope")
        if "error" in response or not isinstance(response.get("result"), dict):
            raise VerificationError(f"{method} returned a JSON-RPC error")
        return response["result"]

    def check_health(self, base: str, label: str) -> None:
        body, _ = self._request(self._url(base, "/health"))
        if body.strip() != b"ok":
            raise VerificationError(f"{label} /health body was not 'ok'")
        self.completed.append(f"{label} health")

    def check_source(self) -> None:
        body, headers = self._request(
            self._url(self.base_url, "/source"), expected_status=307
        )
        if headers.get("Location") != self.source_url:
            raise VerificationError("/source did not redirect to the deployed commit")
        text = body.decode("utf-8")
        for required in (self.sha, self.source_url):
            if required not in text:
                raise VerificationError(f"/source body omitted {required}")
        self.completed.append("HTTP source provenance")

    def check_mcp(self) -> None:
        initialized = self._json_rpc(
            "initialize",
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "surf-production-verifier", "version": "1"},
            },
            1,
        )
        if initialized.get("protocolVersion") != PROTOCOL_VERSION:
            raise VerificationError("MCP initialize negotiated an unexpected protocol")
        server_info = initialized.get("serverInfo")
        if not isinstance(server_info, dict) or server_info.get("name") != "surf":
            raise VerificationError("MCP initialize returned unexpected server metadata")
        instructions = initialized.get("instructions")
        if not isinstance(instructions, str):
            raise VerificationError("MCP initialize omitted instructions")
        for required in (self.sha, self.source_url):
            if required not in instructions:
                raise VerificationError(f"MCP initialize omitted {required}")

        tools = self._json_rpc("tools/list", {}, 2).get("tools")
        if not isinstance(tools, list):
            raise VerificationError("tools/list omitted its tool array")
        names = [tool.get("name") for tool in tools if isinstance(tool, dict)]
        if names != EXPECTED_TOOLS:
            raise VerificationError(f"tools/list returned unexpected tools: {names!r}")

        resources = self._json_rpc("resources/list", {}, 3).get("resources")
        if not isinstance(resources, list):
            raise VerificationError("resources/list omitted its resource array")
        uris = [
            resource.get("uri") for resource in resources if isinstance(resource, dict)
        ]
        if not all(isinstance(uri, str) for uri in uris):
            raise VerificationError("resources/list returned a non-string URI")
        missing = EXPECTED_FRAMEWORK_RESOURCES.difference(uris)
        if missing:
            raise VerificationError(
                f"resources/list omitted expected resources: {sorted(missing)!r}"
            )
        if len(uris) != len(set(uris)):
            raise VerificationError("resources/list returned duplicate URIs")

        source = self._json_rpc("resources/read", {"uri": "surf://source"}, 4)
        contents = source.get("contents")
        if not isinstance(contents, list) or len(contents) != 1:
            raise VerificationError("surf://source returned unexpected contents")
        source_text = contents[0].get("text") if isinstance(contents[0], dict) else None
        if not isinstance(source_text, str):
            raise VerificationError("surf://source omitted text")
        for required in (self.sha, self.source_url):
            if required not in source_text:
                raise VerificationError(f"surf://source omitted {required}")
        self.completed.extend(["MCP initialize", "MCP tools", "MCP resources"])

    def check_landing(self) -> None:
        expected_html = (self.repo_root / "web/landing/index.html").read_bytes()
        if b'href="/source"' not in expected_html:
            raise VerificationError("deployed commit's landing footer omits /source")
        actual_html, _ = self._request(self._url(self.base_url, "/"))
        if actual_html != expected_html:
            raise VerificationError("landing HTML differs from the deployed commit")

        expected_css = (self.repo_root / "web/landing/_landing.css").read_bytes()
        css_path = f"/assets/landing.css?commit={self.sha}"
        actual_css, _ = self._request(self._url(self.base_url, css_path))
        if actual_css != expected_css:
            raise VerificationError("landing stylesheet differs from the deployed commit")
        self.completed.append("compiled landing assets")

    def run(self) -> list[str]:
        self.check_health(self.base_url, "production")
        self.check_source()
        self.check_mcp()
        self.check_landing()
        for legacy_url in self.legacy_urls:
            self.check_health(legacy_url, urllib.parse.urlsplit(legacy_url).netloc)
        return self.completed


def write_summary(path: Path, completed: list[str], sha: str) -> None:
    with path.open("a", encoding="utf-8") as summary:
        summary.write("\n## Deep verification\n\n")
        summary.write(f"All checks passed for `{sha}`:\n\n")
        for check in completed:
            summary.write(f"- {check}\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--legacy-url", action="append", default=[])
    parser.add_argument("--github-summary", type=Path)
    parser.add_argument("--timeout", type=float, default=15)
    args = parser.parse_args()

    verifier = Verifier(
        base_url=args.base_url,
        expected_sha=args.expected_sha,
        repo_root=args.repo_root,
        legacy_urls=args.legacy_url,
        timeout=args.timeout,
    )
    completed = verifier.run()
    for check in completed:
        print(f"PASS: {check}")
    if args.github_summary:
        write_summary(args.github_summary, completed, verifier.sha)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
