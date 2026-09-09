# Surf

**Learn to surf the waves of AI.**

Surf is a free, open-source plugin and learning framework that helps you get better at
working with AI agents through your real work. It helps your agent establish a lightweight
local practice, retain useful evidence and choose grounded ways to improve how you work
together.

## Start here

- **Setting up Surf?** [Follow the setup guide](docs/plugin-installation.md).
- **Understanding the project?** Read [how Surf works](docs/how-surf-works.md) and
  [why Surf exists](docs/why-surf.md).
- **Inspecting or contributing to the source?** See
  [build and test](docs/development.md) and
  [the hosted-service source contract](docs/releases-and-source.md).

## Quickstart for humans

Give this instruction to Claude or ChatGPT/Codex, on desktop or CLI:

```text
Use the setup guide at https://github.com/withnative/surf to install Surf.
```

The agent should identify the client it is running in, install Surf using that client's
plugin tools and explain any required restart or reload.

Known file-capable clients described by this guide are the ChatGPT desktop app in Work or
Codex mode, Codex CLI, Claude Code CLI, and the Claude Code desktop app. This list is not
exhaustive. Other clients may connect to Surf over MCP, but their packaged-plugin and
durable-local-file behaviour is not implied by this list; use the direct fallback in the
[setup guide](docs/plugin-installation.md) when appropriate.

If you begin in a browser-only or mobile chat, that agent cannot complete Surf's local
installation or durable file setup. It should send you to a file-capable client—ChatGPT
desktop in Work or Codex mode (or Codex CLI) for ChatGPT, and Claude Code for Claude—and
ask you to paste the same instruction there.

If installation requires a reload or restart, continue in a fresh conversation with:

```text
Use Surf's quickstart tool to help me finish setting up Surf.
```

For manual installation, supported surfaces, updates, troubleshooting and removal, use
the [setup guide](docs/plugin-installation.md).

## What Surf does

Surf supplies an agent with a current working learning framework. The agent uses that
framework to help you:

- establish an explicit learning aim and working agreement;
- keep lightweight evidence from real successes, failures and surprises;
- maintain a correctable understanding of what is useful for you; and
- review the evidence and choose one grounded next experiment.

Your agent performs the local work. The Surf server returns the rulebook; it does not read
your practice folder, keep a participant profile or take over the immediate task you are
trying to complete.

## Quickstart for agents

If a user asks you to set up Surf from this repository, identify the local client and
inspect its existing marketplace, plugin and MCP/connection state before changing
anything. If shell access and a direct installation capability are available, perform
the setup yourself with the client's non-interactive plugin CLI, then verify the
marketplace, plugin, version and connection. If the host offers a plugin suggestion,
approval or enable action instead, use that host flow and ask for approval where the
host requires it.

Use an in-product Plugins Directory only when the current host exposes it and Surf is
already visible under one of its configured sources. If Surf or its source is absent,
do not imply that the directory can add an arbitrary Git marketplace. Give the person
the shortest CLI route below, or ask a workspace administrator to import and enable the
public marketplace for the workspace. The product repository owns these detailed setup
instructions; the shared marketplace is only the discovery/catalogue signpost.

If the current chat cannot act on the user's machine because it has no durable filesystem
or local client shell, do not install into an isolated sandbox and do not stop at a list
of commands. Explain the boundary, then give the user a provider-matched handoff:

- from ChatGPT browser or mobile, open ChatGPT desktop in Work or Codex mode, or Codex CLI;
- from Claude.ai or Claude mobile, open Claude Code.

Ask them to paste this human-readable setup prompt into that client:

```text
Use the setup guide at https://github.com/withnative/surf to install Surf.
```

The receiving desktop or CLI agent should inspect its own client state and complete the
installation. Offer the manual commands below only as a fallback if the user prefers to
run them personally.

**Claude Code and its desktop application:**

```sh
claude plugin marketplace add withnative/plugins
claude plugin install surf@withnative
```

**ChatGPT/Codex Desktop and Codex CLI:**

```sh
codex plugin marketplace add withnative/plugins
codex plugin add surf@withnative
```

The installed plugin connects to Surf's official public MCP endpoint. Surf requires no
account, login or OAuth authentication, although the client may separately ask the user
to approve enabling a remote connection. The Surf application is stateless: its tools
accept only a document choice—or no arguments—and do not accept local practice files,
histories, transcripts or other participant content. Surf retains no participant state.
See the [privacy and data statement](https://github.com/withnative/surf/blob/main/docs/privacy-and-data.md)
for the separate AI-provider and infrastructure-metadata boundaries.

Check existing marketplace, plugin and MCP state before adding anything. Verify the
installed plugin afterwards and read the exact restart or reload instruction reported by
the client. `/reload-plugins` is a Claude Code host command, not a Surf skill. Recommend it
only when the current host advertises it and it applies; otherwise tell the user to start
a new conversation or restart the app.

The Surf repository is the setup guide and source repository. The separate
[withnative/plugins](https://github.com/withnative/plugins) repository is the canonical
Native plugin catalogue; adding it makes Surf and the other catalogue entries available
but installs none of them. The separate install command selects only Surf.

Do not substitute a curated plugin-catalogue search for the exact Native catalogue named
by this guide.
Do not send the user to interactive slash commands when you have shell access to the
non-interactive CLI.

If installation requires a restart or reload, give the user this copyable continuation
prompt before ending the conversation:

```text
Use Surf's quickstart tool to help me finish setting up Surf.
```

For existing installations, duplicate MCP connections, GUI alternatives, updates,
troubleshooting and removal, follow the
[complete setup guide](docs/plugin-installation.md).

### If plugin installation is unavailable: direct MCP

Surf also accepts a direct connection with these exact values:

| Field | Value |
| --- | --- |
| URL | `https://surf.withnative.ai/mcp` |
| Transport | Streamable HTTP (`http`) |
| Authorization | None; Surf has no account, login or OAuth requirement |

In ChatGPT desktop, add a server named `surf` under **Settings → MCP servers**, choose
**Streamable HTTP**, enter the URL, save, and restart. In Claude Code, run:

```sh
claude mcp add --transport http surf --scope user https://surf.withnative.ai/mcp
```

For local Codex clients, the same host configuration can contain:

```toml
[mcp_servers.surf]
url = "https://surf.withnative.ai/mcp"
```

Then use the host's MCP list/status view to verify the connection and start a fresh
conversation by explicitly asking the agent to call `quickstart`. Direct MCP exposes
Surf's live tools, but it does not install Surf's packaged `next-step` skill: ordinary
Surf requests therefore do not get the skill's trigger or proactive fresh-conversation
`quickstart` behaviour. This is a capability difference, not an authentication step.

## How Surf is delivered

This repository contains thin Claude and OpenAI plugin packages. The installed plugin
supplies Surf's trigger skill and MCP connection. The managed MCP service supplies current
Surf guidance. Your practice remains in ordinary local files you control.

[Read more about how Surf works →](docs/how-surf-works.md)

## Why Surf?

AI is a kind of magic — and everyone should get to wield it.

Surf is a free, open-source plugin that helps you learn to do remarkable things with AI.
It meets you wherever you are, uses experiments grounded in your real work, and keeps
adapting as the technology changes.

People working most deeply with AI are having enormous fun learning to ride a fast,
powerful and unpredictable wave. Surf exists to make that experience available to anyone.

[Read why Surf exists →](docs/why-surf.md)

## Trust and data boundaries

The Surf application has no account system, authentication, database, or participant
state. Its MCP tools accept no participant content: they receive only the document choice
needed to return framework or product documentation. They do not accept the contents of
your local practice files.

That is a boundary around Surf, not a promise that the whole workflow is private. Your AI
provider processes the conversation, tool calls, tool results, and any local files your
agent reads. Your machine, backups, sharing settings, network, and Surf's hosting
infrastructure have their own data boundaries. Read the precise
[privacy and data statement](docs/privacy-and-data.md).

## Documentation

- [Documentation index](docs/index.md)
- [Frequently asked questions](docs/faq.md)
- [How Surf works](docs/how-surf-works.md)
- [Privacy and data](docs/privacy-and-data.md)
- [Compatibility](docs/compatibility.md)
- [Plugin installation and management](docs/plugin-installation.md)
- [Plugin release acceptance runbook](docs/plugin-release-acceptance.md)
- [Working framework and source](docs/releases-and-source.md)
- [Production deployment and rollback](docs/production-deployment.md)
- [Development, building and self-hosting](docs/development.md)
- [Contributing](CONTRIBUTING.md)
- [Security reporting](SECURITY.md)
- [About Richard](docs/about-richard.md)

Product documentation and framework guidance are separate. Product documentation
explains Surf and is returned by `get_doc`, `/docs/{slug}`, and `surf://docs/{slug}` from
the same compiled Markdown. The working framework is returned by `quickstart`,
`get_guide`, and `get_reference`: moment guides help with a particular Surf interaction,
while references provide cross-cutting knowledge when it is useful. MCP resources are a
protocol-level delivery mirror, not another authored content kind.
