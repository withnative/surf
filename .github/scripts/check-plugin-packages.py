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
PRIMARY_PROMPT = f"Install the plugin {REPOSITORY} and use the quickstart tool"
OPENAI_MARKETPLACE_COMMAND = "codex plugin marketplace add withnative/surf"
OPENAI_INSTALL_COMMAND = "codex plugin add surf@withnative"
CLAUDE_MARKETPLACE_COMMAND = "claude plugin marketplace add withnative/surf"
CLAUDE_INSTALL_COMMAND = "claude plugin install surf@withnative"
CLAUDE_SLASH_MARKETPLACE_COMMAND = "/plugin marketplace add withnative/surf"
CLAUDE_SLASH_INSTALL_COMMAND = "/plugin install surf@withnative"
OPENAI_SKILL_INVOCATION = "$next-step"
CLAUDE_SKILL_INVOCATION = "/surf:next-step"
SUPPORTED_SURFACES = ("ChatGPT/Codex Desktop", "Claude Code")
FALLBACK_SEMANTICS = "Direct MCP connection remains a supported fallback"
HERO = "Learn to surf the waves of AI"
PLUGIN_NAME = "surf"
MARKETPLACE_NAME = "withnative"
PLUGIN_PATH = "./plugins/surf"
PLUGIN_VERSION = "0.1.3"
SKILL_NAME = "next-step"
SKILL_PATH = "skills/next-step/SKILL.md"
SKILL_DESCRIPTION = (
    "Use for plausible learning or reflection about working with AI agents, including "
    "explicitly invoking Surf; starting or resuming a Surf practice; Surf guidance or "
    "documentation; a current goal, aim, experiment, or plan; capturing or reflecting on "
    "good, bad, or surprising AI-agent experiences; reviewing evidence; changing an "
    "experiment; or deliberate improvement in how someone works with AI agents, even when "
    "Surf is not named. Prefer activation for bounded AI-agent-practice intent. Do not use "
    "for web surfing, unrelated products named Surf, ordinary task execution, or generic "
    "subject learning without intent to learn from, reflect on, or improve the human-agent "
    "working system."
)
SKILL_DISPLAY_NAME = "Find your next step with AI"
SKILL_SHORT_DESCRIPTION = "Find your next worthwhile step with AI agents."
SKILL_DEFAULT_PROMPT = (
    "Use $next-step to find a worthwhile next step from my experience working with AI agents."
)

# Public installation copy is deliberately duplicated across surfaces rather than
# generated from one source, so these per-surface expectations are the authoritative
# list of what each surface must carry. Any public string that appears on more than
# one surface belongs here as a named constant.

# Every public surface leads with the same repository and the same pasteable prompt.
SHARED_INSTALLATION_COPY = (REPOSITORY, PRIMARY_PROMPT)

# The written surfaces (README and the canonical guide) carry the deterministic
# commands, the named supported surfaces, and the direct-MCP fallback.
DOCUMENTED_INSTALLATION_COPY = (
    ENDPOINT,
    FALLBACK_SEMANTICS,
    OPENAI_MARKETPLACE_COMMAND,
    OPENAI_INSTALL_COMMAND,
    CLAUDE_MARKETPLACE_COMMAND,
    CLAUDE_INSTALL_COMMAND,
    CLAUDE_SLASH_MARKETPLACE_COMMAND,
    CLAUDE_SLASH_INSTALL_COMMAND,
    OPENAI_SKILL_INVOCATION,
    CLAUDE_SKILL_INVOCATION,
    *SUPPORTED_SURFACES,
)

# The landing card carries one promise, one prompt and one link. Commands, surface
# lists, fallback prose and deep documentation links belong in the docs, not on it.
LANDING_INSTALLATION_COPY = (
    f"<h1>{HERO}</h1>",
    f'data-copy="{PRIMARY_PROMPT}"',
    f'<a class="repo" href="{REPOSITORY}">',
)
# Copy that must not appear as readable text on the landing card. Checked against the
# raw source, the whitespace-collapsed source and the tag-stripped source, so neither a
# source-line wrap nor inline markup can smuggle a command block back onto the card.
LANDING_FORBIDDEN_TEXT = (
    OPENAI_MARKETPLACE_COMMAND,
    OPENAI_INSTALL_COMMAND,
    CLAUDE_MARKETPLACE_COMMAND,
    CLAUDE_INSTALL_COMMAND,
    CLAUDE_SLASH_MARKETPLACE_COMMAND,
    CLAUDE_SLASH_INSTALL_COMMAND,
    "codex plugin",
    "claude plugin",
    FALLBACK_SEMANTICS,
)

# Markup the landing page must not contain anywhere, including its header and footer.
# These are attribute fragments, so they are checked against the raw and collapsed
# source only: tag stripping would remove the very text being matched.
LANDING_FORBIDDEN_MARKUP = (
    'href="/docs/',
    f'href="{REPOSITORY}/blob/',
)

# The visible prompt in the fence and the clipboard payload on the button must be the
# same bytes. The fence marks up part of the prompt, so its text is compared after
# stripping inner tags.
LANDING_FENCE_PATTERN = re.compile(
    r'<div class="fence" id="setup-prompt">(.*?)</div>', re.DOTALL
)
HTML_TAG_PATTERN = re.compile(r"<[^>]*>")


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
            manifest.get("license") == "AGPL-3.0-only",
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
    require(skill_files[0].relative_to(PLUGIN).as_posix() == SKILL_PATH, "skill path drifted")
    skill = skill_files[0].read_text(encoding="utf-8")
    require(skill.startswith("---\n"), "Surf skill must start with frontmatter")
    require(f"name: {SKILL_NAME}\n" in skill, "Surf skill name is missing")
    require(
        f"description: {SKILL_DESCRIPTION}\n" in skill,
        "Surf skill activation description drifted",
    )
    require("quickstart" in skill, "Surf skill must require quickstart")
    require(ENDPOINT in skill, "Surf skill must identify the stable endpoint")
    require(len(skill.encode("utf-8")) <= 2500, "Surf skill is no longer a thin bootstrap")

    openai_metadata_path = skill_files[0].parent / "agents" / "openai.yaml"
    try:
        openai_metadata = openai_metadata_path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise ValidationError(
            f"missing {openai_metadata_path.relative_to(ROOT)}"
        ) from error
    expected_openai_metadata = (
        "interface:\n"
        f'  display_name: "{SKILL_DISPLAY_NAME}"\n'
        f'  short_description: "{SKILL_SHORT_DESCRIPTION}"\n'
        f'  default_prompt: "{SKILL_DEFAULT_PROMPT}"\n'
    )
    require(
        openai_metadata == expected_openai_metadata,
        "OpenAI skill display metadata drifted",
    )

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
        "docs/faq.md": (ROOT / "docs" / "faq.md").read_text(encoding="utf-8"),
    }
    required_by_surface = {
        "README.md": (*SHARED_INSTALLATION_COPY, *DOCUMENTED_INSTALLATION_COPY),
        "docs/plugin-installation.md": (
            *SHARED_INSTALLATION_COPY,
            *DOCUMENTED_INSTALLATION_COPY,
        ),
        "web/landing/index.html": (*SHARED_INSTALLATION_COPY, *LANDING_INSTALLATION_COPY),
        # The FAQ leads with the same repository and pasteable prompt but deliberately
        # sends the reader to the canonical guide instead of repeating the commands.
        "docs/faq.md": SHARED_INSTALLATION_COPY,
    }
    for path, fragments in required_by_surface.items():
        text = public_copy[path]
        # Prose wraps across lines; compare against the collapsed text too so a
        # line break is not treated as drift.
        collapsed = " ".join(text.split())
        for fragment in fragments:
            require(
                fragment in text or fragment in collapsed,
                f"{path} public installation copy drifted: {fragment!r}",
            )

    landing = public_copy["web/landing/index.html"]
    landing_collapsed = " ".join(landing.split())
    landing_stripped = " ".join(HTML_TAG_PATTERN.sub(" ", landing).split())
    for fragment in LANDING_FORBIDDEN_TEXT:
        require(
            fragment not in landing
            and fragment not in landing_collapsed
            and fragment not in landing_stripped,
            f"landing card must stay one promise, one prompt and one link: {fragment!r}",
        )
    for fragment in LANDING_FORBIDDEN_MARKUP:
        require(
            fragment not in landing and fragment not in landing_collapsed,
            f"landing page must not link into the documentation tree: {fragment!r}",
        )

    # The visible prompt and the clipboard payload must be byte-identical, so editing
    # one without the other fails here rather than shipping a mismatched card.
    fence = LANDING_FENCE_PATTERN.search(landing)
    require(fence is not None, "landing card is missing the setup-prompt fence")
    fence_text = " ".join(HTML_TAG_PATTERN.sub("", fence.group(1)).split())
    require(
        fence_text == PRIMARY_PROMPT,
        "landing fence text must equal the copy-button payload exactly: "
        f"{fence_text!r} != {PRIMARY_PROMPT!r}",
    )

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
