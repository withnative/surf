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
- **Inspecting or contributing to the source?** See [build and test](#build-and-test) and
  [the hosted-service source contract](#source-for-the-hosted-service).

## Quickstart for humans

Give this instruction to Claude or ChatGPT/Codex, on desktop or CLI:

```text
Open https://github.com/withnative/surf and follow the setup guide.
```

The agent should identify the client it is running in, install Surf using that client's
plugin tools and explain any required restart or reload.

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

If a user asks you to set up Surf from this repository, inspect the local client before
deciding installation is unavailable. If shell access is available, perform the setup
yourself using the client's non-interactive plugin CLI.

If the current chat cannot act on the user's machine because it has no durable filesystem
or local client shell, do not install into an isolated sandbox and do not stop at a list
of commands. Explain the boundary, then give the user a provider-matched handoff:

- from ChatGPT browser or mobile, open ChatGPT desktop in Work or Codex mode, or Codex CLI;
- from Claude.ai or Claude mobile, open Claude Code.

Ask them to paste this human-readable setup prompt into that client:

```text
Open https://github.com/withnative/surf and follow the setup guide.
```

The receiving desktop or CLI agent should inspect its own client state and complete the
installation. Offer the manual commands below only as a fallback if the user prefers to
run them personally.

**Claude Code and its desktop application:**

```sh
claude plugin marketplace add withnative/surf
claude plugin install surf@withnative
```

**ChatGPT/Codex Desktop and Codex CLI:**

```sh
codex plugin marketplace add withnative/surf
codex plugin add surf@withnative
```

Check existing marketplace, plugin and MCP state before adding anything. Verify the
installed plugin afterwards and follow any restart or reload instruction reported by the
client.

Do not substitute a curated plugin-catalogue search for the repository the user supplied.
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

Product documentation and framework guidance are separate. Product documentation
explains Surf and is returned by `get_doc`, `/docs/{slug}`, and `surf://docs/{slug}` from
the same compiled Markdown. The working framework is returned by `quickstart`,
`get_guide`, and `get_reference`: moment guides help with a particular Surf interaction,
while references provide cross-cutting knowledge when it is useful. MCP resources are a
protocol-level delivery mirror, not another authored content kind.

## Source for the hosted service

The hosted service identifies its Surf application version, working framework, Git commit,
and exact source URL at [surf.withnative.ai/source](https://surf.withnative.ai/source).
That exact revision—not merely the repository homepage—is the source corresponding to the
running build. See [working framework and source](docs/releases-and-source.md).

## Build and test

Surf requires Rust 1.85 or later.

```sh
cargo build --locked
cargo test --locked
cargo run --locked
```

The server listens on port `8080` by default. Set `PORT` to use another port. A generic
container build is also available:

```sh
docker build -t surf .
docker run --rm -p 8080:8080 surf
```

Ordinary local and archive builds deliberately report source metadata as unavailable;
they never combine the current checkout's commit with Surf's public repository URL. A
production build must explicitly provide a matching full public commit and URL:

```sh
SURF_GIT_SHA=$(git rev-parse HEAD)
docker build \
  --build-arg SURF_GIT_SHA="$SURF_GIT_SHA" \
  --build-arg SURF_SOURCE_URL="https://github.com/withnative/surf/commit/$SURF_GIT_SHA" \
  -t surf .
```

The build stops if either value is missing, the SHA is not full lowercase hexadecimal,
or the URL does not identify that exact commit in `withnative/surf`. Deployment must
still verify that the commit is public and is the source actually being built.

The hosted service follows the repository's documented
[merge-to-`main` production and rollback flow](docs/production-deployment.md). Railway's
GitHub build supplies the exact triggering SHA and derives the matching URL during the
same container build; operators do not maintain those two values separately.

The official hosted endpoint is the supported product. The source is intentionally
inspectable, runnable, and forkable, but Native does not promise operational support or
automatic framework updates for self-hosted deployments. Fork operators own their
deployment and update policy.

## Contributing and security

Issues, questions, design discussion, and forks are genuinely welcome. Pull requests are
closed by default unless invited: open an issue first and describe the problem or idea
before writing a patch. Read [CONTRIBUTING.md](CONTRIBUTING.md) for the complete policy.

Please do not disclose suspected vulnerabilities in a public issue. Follow the private
reporting route in [SECURITY.md](SECURITY.md).

## Created by Richard Ng

Surf was created by Richard Ng, a founder and educator who has worked with over 1,000
learners across AI and software engineering. Across a decade in education and edtech,
Richard has built global training programmes delivered across four continents, including
programmes used by Starling Bank, Beamery and Ocado, as well as startups backed by
Sequoia, Index Ventures and Y Combinator. Richard graduated from the University of Oxford
and is CEO of [Native](https://withnative.ai).
