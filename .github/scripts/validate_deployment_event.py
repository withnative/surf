#!/usr/bin/env python3
"""Validate a deployment_status payload before using any of its values."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

FULL_SHA = re.compile(r"[0-9a-f]{40}")


class EventValidationError(ValueError):
    pass


def _require(mapping: dict[str, Any], key: str, kind: type) -> Any:
    value = mapping.get(key)
    if not isinstance(value, kind):
        raise EventValidationError(f"event field {key!r} must be {kind.__name__}")
    return value


def validate_event(
    event: dict[str, Any], *, repository: str, environment: str, ref: str
) -> dict[str, str]:
    event_repository = _require(event, "repository", dict)
    if _require(event_repository, "full_name", str) != repository:
        raise EventValidationError("deployment event is for an unexpected repository")

    deployment = _require(event, "deployment", dict)
    status = _require(event, "deployment_status", dict)
    if _require(status, "state", str) != "success":
        raise EventValidationError("deployment status is not success")
    if _require(deployment, "environment", str) != environment:
        raise EventValidationError("deployment environment is not production")
    if _require(deployment, "ref", str) != ref:
        raise EventValidationError("production deployment ref is not main")

    sha = _require(deployment, "sha", str)
    if FULL_SHA.fullmatch(sha) is None:
        raise EventValidationError(
            "deployment SHA must be 40 lowercase hexadecimal characters"
        )

    deployment_id = deployment.get("id")
    if not isinstance(deployment_id, int) or deployment_id < 1:
        raise EventValidationError("deployment id must be a positive integer")

    return {
        "sha": sha,
        "deployment_id": str(deployment_id),
        "environment": environment,
        "status_target_url": _safe_text(status.get("target_url")),
        "environment_url": _safe_text(status.get("environment_url")),
    }


def _safe_text(value: Any) -> str:
    if value is None:
        return "unavailable"
    if not isinstance(value, str):
        raise EventValidationError("deployment URL metadata must be a string or null")
    # GitHub renders the summary as Markdown. Keep event-controlled fields inert
    # inside a single-line code span and cap their log/summary footprint.
    return value.replace("`", "'").replace("\r", " ").replace("\n", " ")[:500]


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
