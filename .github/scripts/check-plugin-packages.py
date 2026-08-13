#!/usr/bin/env python3
"""Validate the aligned Claude and OpenAI Surf plugin packages."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "plugins" / "surf"
ENDPOINT = "https://surf.withnative.ai/mcp"
REPOSITORY = "https://github.com/withnative/surf"
PRIMARY_PROMPT = f"Help me install Surf from {REPOSITORY} and get started."
OPENAI_MARKETPLACE_COMMAND = "codex plugin marketplace add withnative/surf"
CLAUDE_MARKETPLACE_COMMAND = "/plugin marketplace add withnative/surf"
CLAUDE_INSTALL_COMMAND = "/plugin install surf@withnative"
SUPPORTED_SURFACES = ("ChatGPT/Codex Desktop", "Claude Code")
FALLBACK_SEMANTICS = "Direct MCP connection remains a supported fallback"
HERO = "Learn to surf the waves of AI"
PLUGIN_NAME = "surf"
MARKETPLACE_NAME = "withnative"
PLUGIN_PATH = "./plugins/surf"
PLUGIN_VERSION = "0.1.1"


class ValidationError(Exception):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValidationError(f"missing {path.relative_to(ROOT)}") from error
    except json.JSONDecodeError as error:
        raise ValidationError(f"invalid JSON in {path.relative_to(ROOT)}: {error}") from error
    if not isinstance(value, dict):
        raise ValidationError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def main() -> int:
    try:
        validate()
    except ValidationError as error:
        print(f"plugin package validation failed: {error}", file=sys.stderr)
        return 1
    print("plugin package validation passed")
    return 0


def validate() -> None:
    claude_manifest = load_json(PLUGIN / ".claude-plugin" / "plugin.json")
    codex_manifest = load_json(PLUGIN / ".codex-plugin" / "plugin.json")
    claude_marketplace = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    codex_marketplace = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    mcp = load_json(PLUGIN / ".mcp.json")

    for label, manifest in (
        ("Claude manifest", claude_manifest),
        ("OpenAI manifest", codex_manifest),
    ):
        require(manifest.get("name") == PLUGIN_NAME, f"{label} name must be {PLUGIN_NAME}")
        require(
            isinstance(manifest.get("version"), str)
            and re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]) is not None,
            f"{label} version must be simple semantic versioning",
        )
        require(
            manifest["version"] == PLUGIN_VERSION,
            f"{label} plugin package version must be {PLUGIN_VERSION} for this release",
        )
        require(manifest.get("skills") == "./skills/", f"{label} must use canonical skills")
        require(
            manifest.get("mcpServers") == "./.mcp.json",
            f"{label} must use canonical MCP configuration",
        )
        require(
            manifest.get("repository") == "https://github.com/withnative/surf",
            f"{label} repository is incorrect",
        )
        require(
            manifest.get("license") == "AGPL-3.0-or-later",
            f"{label} license is incorrect",
        )
        require("[TODO:" not in json.dumps(manifest), f"{label} contains a TODO placeholder")

    require(
        claude_manifest["version"] == codex_manifest["version"],
        "provider manifest versions must match",
    )
    require(
        claude_manifest["description"] == codex_manifest["description"],
        "provider manifest descriptions must match",
    )

    validate_claude_marketplace(claude_marketplace)
    validate_codex_marketplace(codex_marketplace)
    validate_public_installation_copy()

    require(
        mcp == {
            "mcpServers": {
                "surf": {
                    "type": "http",
                    "url": ENDPOINT,
                }
            }
        },
        ".mcp.json must contain only the public Surf HTTP endpoint",
    )

    skill_files = sorted(PLUGIN.glob("skills/*/SKILL.md"))
    require(len(skill_files) == 1, "plugin must contain exactly one canonical skill")
    require(skill_files[0].relative_to(PLUGIN).as_posix() == "skills/surf/SKILL.md", "skill path drifted")
    skill = skill_files[0].read_text(encoding="utf-8")
    require(skill.startswith("---\n"), "Surf skill must start with frontmatter")
    require("name: surf" in skill, "Surf skill name is missing")
    require("quickstart" in skill, "Surf skill must require quickstart")
    require(ENDPOINT in skill, "Surf skill must identify the stable endpoint")
    require(len(skill.encode("utf-8")) <= 2500, "Surf skill is no longer a thin bootstrap")

    forbidden = [
        path.relative_to(PLUGIN).as_posix()
        for path in PLUGIN.rglob("*")
        if path.is_file()
        and (
            "framework" in path.parts
            or path.name in {"quickstart.md", "capabilities.md", "setting-up.md"}
        )
    ]
    require(not forbidden, f"plugin duplicates changing framework content: {forbidden}")

    all_plugin_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in PLUGIN.rglob("*")
        if path.is_file()
    )
    require(
        "plugin_asdk_app" not in all_plugin_text,
        "shared package must not commit an account-specific registered app ID",
    )


def validate_public_installation_copy() -> None:
    public_copy = {
        "README.md": (ROOT / "README.md").read_text(encoding="utf-8"),
        "docs/plugin-installation.md": (ROOT / "docs" / "plugin-installation.md").read_text(
            encoding="utf-8"
        ),
        "web/landing/index.html": (ROOT / "web" / "landing" / "index.html").read_text(
            encoding="utf-8"
        ),
    }
    stable_fragments = (
        REPOSITORY,
        ENDPOINT,
        PRIMARY_PROMPT,
        OPENAI_MARKETPLACE_COMMAND,
        CLAUDE_MARKETPLACE_COMMAND,
        CLAUDE_INSTALL_COMMAND,
        *SUPPORTED_SURFACES,
    )
    for path, text in public_copy.items():
        for fragment in stable_fragments:
            require(fragment in text, f"{path} public installation copy drifted: {fragment!r}")
        require(
            FALLBACK_SEMANTICS in " ".join(text.split()),
            f"{path} direct-MCP fallback semantics drifted",
        )

    landing = public_copy["web/landing/index.html"]
    require(f"<h1>{HERO}</h1>" in landing, "landing hero copy drifted")
    require(
        f'data-copy="{PRIMARY_PROMPT}"' in landing,
        "landing copy action drifted from the canonical installation prompt",
    )
    for target in (
        "https://github.com/withnative/surf/blob/main/docs/plugin-installation.md",
        "/docs/privacy-and-data",
        "/docs/compatibility",
    ):
        require(f'href="{target}"' in landing, f"landing installation link drifted: {target}")

    guide = public_copy["docs/plugin-installation.md"]
    for heading in (
        "## ChatGPT/Codex Desktop",
        "## Claude Code",
        "## Updates",
        "## Uninstall or disable",
        "## Recovery and troubleshooting",
        "## Direct MCP fallback",
        "## Provider-documentation verification",
    ):
        require(heading in guide, f"canonical installation guide omits {heading}")


def validate_claude_marketplace(marketplace: dict[str, Any]) -> None:
    require(marketplace.get("name") == MARKETPLACE_NAME, "Claude marketplace name drifted")
    plugins = marketplace.get("plugins")
    require(isinstance(plugins, list) and len(plugins) == 1, "Claude marketplace must contain only Surf")
    entry = plugins[0]
    require(isinstance(entry, dict), "Claude marketplace Surf entry must be an object")
    require(entry.get("name") == PLUGIN_NAME, "Claude marketplace plugin name drifted")
    require(entry.get("source") == PLUGIN_PATH, "Claude marketplace source path drifted")


def validate_codex_marketplace(marketplace: dict[str, Any]) -> None:
    require(marketplace.get("name") == MARKETPLACE_NAME, "OpenAI marketplace name drifted")
    plugins = marketplace.get("plugins")
    require(isinstance(plugins, list) and len(plugins) == 1, "OpenAI marketplace must contain only Surf")
    entry = plugins[0]
    require(isinstance(entry, dict), "OpenAI marketplace Surf entry must be an object")
    require(entry.get("name") == PLUGIN_NAME, "OpenAI marketplace plugin name drifted")
    require(
        entry.get("source") == {"source": "local", "path": PLUGIN_PATH},
        "OpenAI marketplace source path drifted",
    )
    require(
        entry.get("policy")
        == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "OpenAI marketplace policy drifted",
    )
    require(entry.get("category") == "Productivity", "OpenAI marketplace category drifted")


if __name__ == "__main__":
    raise SystemExit(main())
