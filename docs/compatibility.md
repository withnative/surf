# Compatibility

Surf's public plugin-installation claim is deliberately narrow. The verified routes are
**ChatGPT/Codex Desktop** and **Claude Code**. Each needs the Surf remote MCP connection
and durable access to local files so the practice does not depend on chat memory.

## Current surface status

| Status | Surface | Installation route | Evidence and boundary |
|---|---|---|---|
| Verified | ChatGPT/Codex Desktop on macOS | `codex plugin marketplace add withnative/surf`, then `codex plugin add surf@withnative`; or, in the app, **Plugins Directory → Native → Surf → Install** after a restart | Human installation plus agent-led repository-link installation and activation on 13 August 2026 through the GUI route. The maintainer has run the CLI install himself; a CLI-installed plugin appears in the desktop app in a less prominent area than an in-app install. |
| Verified | Claude Code CLI on macOS | `claude plugin marketplace add withnative/surf`, then `claude plugin install surf@withnative`; the `/plugin` slash commands are equivalent inside a terminal session | Plugin installation and natural-language activation observed on Claude Code 2.1.222; direct-MCP baseline observed on 2.1.231. A full uninstall, install, marketplace-update and update cycle was executed on macOS on 14 August 2026 and recorded in [CLI install acceptance evidence](evidence/2026-08-14-cli-install-acceptance.md). |
| Expected, not claimed | Claude Code desktop app | Run `claude plugin marketplace add withnative/surf` and `claude plugin install surf@withnative` in a terminal, then restart the app. The `/plugin` slash command is terminal-only | A user-scope `claude plugin` install was observed active in the desktop application, with its skill and MCP server loaded, on 14 August 2026. Clean-install evidence for a public support claim has not been recorded. |
| Untested / unsupported | ChatGPT mobile, browser-only chats, Claude.ai, Claude mobile, other MCP clients | None promised | The repository marketplace flow and durable local-file practice have not passed Surf acceptance on these surfaces. |

“Verified” here means the route has positive installation and activation evidence strong
enough to be the public journey. It does not replace the dated human release checklist.
Do not expand support by implication: protocol compatibility alone is not a Surf support
claim.

See the [canonical installation guide](plugin-installation.md) for exact steps, updates,
uninstall, recovery and the direct MCP fallback.

## End-to-end verification standard

For each claimed surface, clean human acceptance must record evidence that it can:

1. install Surf from `https://github.com/withnative/surf` through the documented plugin
   route without a pre-existing standalone Surf MCP connection;
2. initialize the plugin-provided `https://surf.withnative.ai/mcp` connection;
3. discover `quickstart`, `get_guide`, `get_reference`, and `get_doc`;
4. activate through both the documented explicit invocation and an ordinary Surf request;
5. call `quickstart` before a user-facing learning-loop reply;
6. retrieve a relevant guide, reference and product document;
7. create or resume a practice in a person-confirmed durable local folder;
8. write the confirmed user-home locator and recover the same validated practice from an
   unrelated launch directory in a new conversation without broad filesystem search;
9. update or refresh the plugin using the documented client boundary;
10. uninstall or disable the plugin without deleting the local practice;
11. recover after a missing-tool or duplicate-connection condition without silently
    changing a standalone connection;
12. distinguish authored references from MCP resources; and
13. surface an honest limitation when remote MCP or durable file access is unavailable.

Record the operating system and architecture, exact client version, Surf application,
framework and plugin versions, date and timezone, tester, exact commands and UI paths,
reload/restart behaviour, observed result, limitations, and a reviewable trace or
screenshot reference that contains no personal practice content. The complete template is
in the [plugin release acceptance runbook](plugin-release-acceptance.md).

## Direct MCP compatibility

Direct MCP connection remains a supported fallback on the same file-capable surfaces. It
supplies Surf's live tools but not the plugin's trigger skill, so the person must ask the
agent to call `quickstart` at the beginning of a fresh Surf conversation.

A client with remote MCP but no durable local files can read Surf documentation but cannot
run the longitudinal practice as supported. A client with files but no remote MCP cannot
retrieve the current managed framework. Self-hosted Surf forks are not covered by the
official endpoint's compatibility claim.

Some clients cache installed packages, MCP metadata or tool schemas. After installation or
update, use the documented reload, restart and new-conversation boundary before reporting
a Surf failure. Client UI and configuration formats can change, so the acceptance record
must name the tested version rather than assuming every past or future release behaves the
same way.

For the architectural reason behind these requirements, see
[how Surf works](https://github.com/withnative/surf/blob/main/docs/how-surf-works.md).
