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
RAILWAY_HOST = "railway.com"


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
    repository_id: int,
    environment_label: str,
    environment_id: str,
    bot_id: int,
    bot_login: str,
    bot_node_id: str,
    service_name: str,
    project_id: str,
) -> dict[str, str]:
    if _require(event, "action", str) != "created":
        raise EventValidationError("deployment status action is not created")
    event_repository = _require(event, "repository", dict)
    if _require(event_repository, "full_name", str) != repository:
        raise EventValidationError("deployment event is for an unexpected repository")
    if _require(event_repository, "id", int) != repository_id:
        raise EventValidationError("deployment event has an unexpected repository id")
    if _require(event_repository, "default_branch", str) != "main":
        raise EventValidationError("deployment repository default branch is not main")
    _validate_bot(
        event.get("sender"),
        bot_id=bot_id,
        bot_login=bot_login,
        bot_node_id=bot_node_id,
    )

    deployment = _require(event, "deployment", dict)
    status = _require(event, "deployment_status", dict)
    _validate_bot(
        deployment.get("creator"),
        bot_id=bot_id,
        bot_login=bot_login,
        bot_node_id=bot_node_id,
    )
    _validate_bot(
        status.get("creator"),
        bot_id=bot_id,
        bot_login=bot_login,
        bot_node_id=bot_node_id,
    )
    if (
        "performed_via_github_app" not in deployment
        or deployment["performed_via_github_app"] is not None
    ):
        raise EventValidationError("Railway deployment App metadata changed from the reviewed shape")
    if (
        "performed_via_github_app" not in status
        or status["performed_via_github_app"] is not None
    ):
        raise EventValidationError("Railway status App metadata changed from the reviewed shape")
    if _require(status, "state", str) != "success":
        raise EventValidationError("deployment status is not success")
    if _require(deployment, "environment", str) != environment_label:
        raise EventValidationError("deployment environment label is not Surf production")
    if _require(status, "environment", str) != environment_label:
        raise EventValidationError("deployment status environment label is not Surf production")
    if _require(deployment, "original_environment", str) != environment_label:
        raise EventValidationError("deployment original environment label is not Surf production")
    if _require(deployment, "task", str) != "deploy":
        raise EventValidationError("deployment task is not deploy")
    # Railway's captured production event reports this flag as false even though
    # the exact service/environment label and UUID identify production. Treat
    # any shape change as review-required instead of silently changing trust.
    if _require(deployment, "production_environment", bool) is not False:
        raise EventValidationError("Railway production_environment metadata changed")
    if _require(deployment, "transient_environment", bool) is not False:
        raise EventValidationError("production deployment is marked transient")

    sha = _require(deployment, "sha", str)
    if FULL_SHA.fullmatch(sha) is None:
        raise EventValidationError(
            "deployment SHA must be 40 lowercase hexadecimal characters"
        )
    deployment_ref = _require(deployment, "ref", str)
    if deployment_ref != sha:
        raise EventValidationError("Railway deployment ref is not the exact deployed SHA")

    payload = _require(deployment, "payload", dict)
    if set(payload) != {"environmentId"}:
        raise EventValidationError("deployment payload fields changed from the reviewed shape")
    if _require(payload, "environmentId", str) != environment_id:
        raise EventValidationError("deployment payload is for an unexpected Railway environment")

    deployment_id = deployment.get("id")
    if (
        isinstance(deployment_id, bool)
        or not isinstance(deployment_id, int)
        or deployment_id < 1
    ):
        raise EventValidationError("deployment id must be a positive integer")

    status_id = status.get("id")
    if isinstance(status_id, bool) or not isinstance(status_id, int) or status_id < 1:
        raise EventValidationError("deployment status id must be a positive integer")

    repository_url = f"https://api.github.com/repos/{repository}"
    deployment_url = f"{repository_url}/deployments/{deployment_id}"
    status_url = f"{deployment_url}/statuses/{status_id}"
    expected_links = (
        (deployment, "repository_url", repository_url),
        (deployment, "url", deployment_url),
        (deployment, "statuses_url", f"{deployment_url}/statuses"),
        (status, "repository_url", repository_url),
        (status, "deployment_url", deployment_url),
        (status, "url", status_url),
    )
    for mapping, key, expected in expected_links:
        if _require(mapping, key, str) != expected:
            raise EventValidationError(f"deployment API link {key!r} is inconsistent")

    correlation_urls = [
        _validate_correlation_url(
            status.get(key), project_id=project_id, environment_id=environment_id
        )
        for key in ("target_url", "log_url", "environment_url")
    ]
    if len(set(correlation_urls)) != 1:
        raise EventValidationError("Railway target, log, and environment URLs disagree")
    correlation_url = correlation_urls[0]

    return {
        "sha": sha,
        "deployment_id": str(deployment_id),
        "environment": environment_label,
        "deployment_ref": deployment_ref,
        "app_identity": f"{bot_login} (bot {bot_id})",
        "service_name": service_name,
        "project_id": project_id,
        "environment_id": environment_id,
        "status_target_url": correlation_url,
    }


def _validate_bot(
    value: Any, *, bot_id: int, bot_login: str, bot_node_id: str
) -> None:
    if not isinstance(value, dict):
        raise EventValidationError("deployment metadata omits the Railway bot identity")
    if (
        value.get("id") != bot_id
        or value.get("login") != bot_login
        or value.get("node_id") != bot_node_id
        or value.get("type") != "Bot"
    ):
        raise EventValidationError("deployment metadata names an unexpected Railway bot")


def _validate_correlation_url(
    value: Any, *, project_id: str, environment_id: str
) -> str:
    if not isinstance(value, str):
        raise EventValidationError("Railway correlation URL must be present")
    if len(value) > 1000 or "`" in value or any(ord(char) < 0x20 for char in value):
        raise EventValidationError("deployment target URL contains unsafe summary text")
    parsed = urllib.parse.urlsplit(value)
    try:
        port = parsed.port
    except ValueError as error:
        raise EventValidationError("deployment target URL has an invalid port") from error
    if (
        parsed.scheme != "https"
        or parsed.hostname != RAILWAY_HOST
        or parsed.username
        or parsed.password
        or port is not None
        or parsed.fragment
    ):
        raise EventValidationError("deployment target URL is not a safe Railway HTTPS URL")
    if parsed.path != f"/project/{project_id}" or urllib.parse.parse_qsl(
        parsed.query, keep_blank_values=True
    ) != [("environmentId", environment_id)]:
        raise EventValidationError(
            "Railway correlation URL identifies an unexpected project or environment"
        )
    return value


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
        summary.write(f"- GitHub App: `{values['app_identity']}`\n")
        summary.write(f"- Railway project: `{values['project_id']}`\n")
        summary.write(f"- Railway service name: `{values['service_name']}`\n")
        summary.write(f"- Railway environment ID: `{values['environment_id']}`\n")
        summary.write(f"- Deployment status URL: `{values['status_target_url']}`\n")
        summary.write("\n")
        summary.write(
            "Use the status URL or the Railway dashboard to retrieve the Railway "
            "deployment ID, image digest, and runtime logs.\n"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--repository-id", type=int, required=True)
    parser.add_argument("--environment-label", required=True)
    parser.add_argument("--environment-id", required=True)
    parser.add_argument("--bot-id", type=int, required=True)
    parser.add_argument("--bot-login", required=True)
    parser.add_argument("--bot-node-id", required=True)
    parser.add_argument("--service-name", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--github-output", type=Path, required=True)
    parser.add_argument("--github-summary", type=Path, required=True)
    args = parser.parse_args()

    event = json.loads(args.event.read_text(encoding="utf-8"))
    if not isinstance(event, dict):
        raise EventValidationError("deployment event must be a JSON object")
    values = validate_event(
        event,
        repository=args.repository,
        repository_id=args.repository_id,
        environment_label=args.environment_label,
        environment_id=args.environment_id,
        bot_id=args.bot_id,
        bot_login=args.bot_login,
        bot_node_id=args.bot_node_id,
        service_name=args.service_name,
        project_id=args.project_id,
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
