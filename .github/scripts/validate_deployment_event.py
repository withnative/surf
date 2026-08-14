#!/usr/bin/env python3
"""Validate a deployment_status payload before using any of its values."""

from __future__ import annotations

import argparse
import json
import re
import urllib.parse
from pathlib import Path
from typing import Any

FULL_SHA = re.compile(r"[0-9a-f]{40}")
RAILWAY_HOSTS = {"railway.com", "railway.app"}


class EventValidationError(ValueError):
    pass


def _require(mapping: dict[str, Any], key: str, kind: type) -> Any:
    value = mapping.get(key)
    if not isinstance(value, kind):
        raise EventValidationError(f"event field {key!r} must be {kind.__name__}")
    return value


def validate_event(
    event: dict[str, Any],
    *,
    repository: str,
    environment: str,
    ref: str,
    installation_id: int,
    app_id: int,
    app_slug: str,
    service_id: str,
    project_id: str,
    allow_empty_ref: bool = False,
) -> dict[str, str]:
    if _require(event, "action", str) != "created":
        raise EventValidationError("deployment status action is not created")
    event_repository = _require(event, "repository", dict)
    if _require(event_repository, "full_name", str) != repository:
        raise EventValidationError("deployment event is for an unexpected repository")

    installation = _require(event, "installation", dict)
    if _require(installation, "id", int) != installation_id:
        raise EventValidationError("deployment event is from an unexpected GitHub App installation")

    deployment = _require(event, "deployment", dict)
    status = _require(event, "deployment_status", dict)
    _validate_app(
        deployment.get("performed_via_github_app"), app_id=app_id, app_slug=app_slug
    )
    _validate_app(
        status.get("performed_via_github_app"), app_id=app_id, app_slug=app_slug
    )
    if _require(status, "state", str) != "success":
        raise EventValidationError("deployment status is not success")
    if _require(deployment, "environment", str) != environment:
        raise EventValidationError("deployment environment is not production")
    if _require(status, "environment", str) != environment:
        raise EventValidationError("deployment status environment is not production")
    if _require(deployment, "production_environment", bool) is not True:
        raise EventValidationError("deployment is not marked as a production environment")
    if _require(deployment, "transient_environment", bool) is not False:
        raise EventValidationError("production deployment is marked transient")
    deployment_ref = _require(deployment, "ref", str)
    accepted_refs = {ref, ""} if allow_empty_ref else {ref}
    if deployment_ref not in accepted_refs:
        raise EventValidationError("production deployment ref is neither main nor an allowed empty SHA ref")

    payload = _require(deployment, "payload", dict)
    if _require(payload, "serviceId", str) != service_id:
        raise EventValidationError("deployment payload is for an unexpected Railway service")

    payload_project_id = payload.get("projectId")
    if payload_project_id is not None and payload_project_id != project_id:
        raise EventValidationError("deployment payload is for an unexpected Railway project")

    sha = _require(deployment, "sha", str)
    if FULL_SHA.fullmatch(sha) is None:
        raise EventValidationError(
            "deployment SHA must be 40 lowercase hexadecimal characters"
        )

    deployment_id = deployment.get("id")
    if (
        isinstance(deployment_id, bool)
        or not isinstance(deployment_id, int)
        or deployment_id < 1
    ):
        raise EventValidationError("deployment id must be a positive integer")

    target_url = _validate_correlation_url(
        status.get("target_url"), project_id=project_id, service_id=service_id
    )
    log_url = _validate_correlation_url(
        status.get("log_url"), project_id=project_id, service_id=service_id
    )
    if target_url and log_url and target_url != log_url:
        raise EventValidationError("deployment target and log URLs disagree")
    correlation_url = log_url or target_url
    # Railway examples consistently expose payload.serviceId. projectId is less
    # clearly documented, so accept either an exact payload value or an exact
    # project/service dashboard URL. The first live event confirms which shape
    # this installation emits without weakening the service boundary.
    if payload_project_id is None and correlation_url is None:
        raise EventValidationError(
            "Railway project identity is absent from both payload and correlation URL"
        )
    environment_url = _validate_environment_url(status.get("environment_url"))

    return {
        "sha": sha,
        "deployment_id": str(deployment_id),
        "environment": environment,
        "deployment_ref": deployment_ref or "(empty SHA ref)",
        "installation_id": str(installation_id),
        "app_identity": f"{app_slug} ({app_id})",
        "service_id": service_id,
        "project_id": project_id,
        "status_target_url": correlation_url or "unavailable",
        "environment_url": environment_url or "unavailable",
    }


def _validate_app(value: Any, *, app_id: int, app_slug: str) -> None:
    if not isinstance(value, dict):
        raise EventValidationError("deployment metadata omits the performing GitHub App")
    if value.get("id") != app_id or value.get("slug") != app_slug:
        raise EventValidationError("deployment metadata names an unexpected GitHub App")


def _validate_correlation_url(
    value: Any, *, project_id: str, service_id: str
) -> str | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise EventValidationError("deployment target URL must be a string or null")
    if len(value) > 1000 or "`" in value or any(ord(char) < 0x20 for char in value):
        raise EventValidationError("deployment target URL contains unsafe summary text")
    parsed = urllib.parse.urlsplit(value)
    try:
        port = parsed.port
    except ValueError as error:
        raise EventValidationError("deployment target URL has an invalid port") from error
    if (
        parsed.scheme != "https"
        or parsed.hostname not in RAILWAY_HOSTS
        or parsed.username
        or parsed.password
        or port is not None
        or parsed.fragment
    ):
        raise EventValidationError("deployment target URL is not a safe Railway HTTPS URL")
    segments = [urllib.parse.unquote(segment) for segment in parsed.path.split("/") if segment]
    try:
        project_index = segments.index("project")
        service_index = segments.index("service")
    except ValueError as error:
        raise EventValidationError(
            "deployment target URL does not identify a Railway project and service"
        ) from error
    if (
        project_index + 1 >= len(segments)
        or service_index + 1 >= len(segments)
        or segments[project_index + 1] != project_id
        or segments[service_index + 1] != service_id
    ):
        raise EventValidationError(
            "deployment target URL identifies an unexpected Railway project or service"
        )
    return value


def _validate_environment_url(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise EventValidationError("deployment environment URL must be a string or null")
    parsed = urllib.parse.urlsplit(value)
    try:
        port = parsed.port
    except ValueError as error:
        raise EventValidationError("deployment environment URL has an invalid port") from error
    if (
        parsed.scheme != "https"
        or parsed.hostname != "surf.withnative.ai"
        or parsed.username
        or parsed.password
        or port is not None
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise EventValidationError("deployment environment URL is not Surf production")
    return "https://surf.withnative.ai"


def write_github_output(path: Path, values: dict[str, str]) -> None:
    with path.open("a", encoding="utf-8") as output:
        for key in ("sha", "deployment_id"):
            output.write(f"{key}={values[key]}\n")


def write_summary(path: Path, values: dict[str, str]) -> None:
    with path.open("a", encoding="utf-8") as summary:
        summary.write("## Railway production deployment\n\n")
        summary.write(f"- Git commit: `{values['sha']}`\n")
        summary.write(f"- GitHub deployment ID: `{values['deployment_id']}`\n")
        summary.write(f"- Environment: `{values['environment']}`\n")
        summary.write(f"- Deployment ref: `{values['deployment_ref']}`\n")
        summary.write(f"- GitHub App installation: `{values['installation_id']}`\n")
        summary.write(f"- GitHub App: `{values['app_identity']}`\n")
        summary.write(f"- Railway project: `{values['project_id']}`\n")
        summary.write(f"- Railway service: `{values['service_id']}`\n")
        summary.write(f"- Deployment status URL: `{values['status_target_url']}`\n")
        summary.write(f"- Environment URL: `{values['environment_url']}`\n\n")
        summary.write(
            "Use the status URL or the Railway dashboard to retrieve the Railway "
            "deployment ID, image digest, and runtime logs.\n"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--installation-id", type=int, required=True)
    parser.add_argument("--app-id", type=int, required=True)
    parser.add_argument("--app-slug", required=True)
    parser.add_argument("--service-id", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--allow-empty-ref", action="store_true")
    parser.add_argument("--github-output", type=Path, required=True)
    parser.add_argument("--github-summary", type=Path, required=True)
    args = parser.parse_args()

    event = json.loads(args.event.read_text(encoding="utf-8"))
    if not isinstance(event, dict):
        raise EventValidationError("deployment event must be a JSON object")
    values = validate_event(
        event,
        repository=args.repository,
        environment=args.environment,
        ref=args.ref,
        installation_id=args.installation_id,
        app_id=args.app_id,
        app_slug=args.app_slug,
        service_id=args.service_id,
        project_id=args.project_id,
        allow_empty_ref=args.allow_empty_ref,
    )
    write_github_output(args.github_output, values)
    write_summary(args.github_summary, values)
    print(
        f"Validated production deployment {values['deployment_id']} "
        f"for commit {values['sha']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
