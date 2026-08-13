# Surf

**Surf the AI frontier.**

Surf is a free, open-source learning framework that helps you get better at working with
AI agents through your real work. Connect its public MCP server to a supported agent and
the agent can establish a lightweight local practice, notice useful evidence over time,
and help you review what is actually changing.

Surf is managed by [Native](https://www.withnative.ai/) and licensed under
[AGPL-3.0-or-later](LICENSE). See [licensing and notices](docs/licensing.md) for
the copyright holder and a plain-language licence summary.

## Plugin packages

This repository contains thin Claude and OpenAI plugin packages. Treat an installation
route as supported only after its clean-client checks in the
[plugin release acceptance runbook](docs/plugin-release-acceptance.md) have dated,
reviewable pass evidence. See [install and manage the Surf plugin](docs/plugin-installation.md)
for the GitHub flows, direct MCP fallback, updates, privacy, and troubleshooting.

Surf launches with three intentionally matching but independently versioned identities:
the **Surf application version**, **working framework version**, and **plugin package
version** are each `0.1.0`. Their future releases do not need to remain in lockstep.

## Start in one line

Paste this into a supported, file-capable agent:

```text
Help me add https://surf.withnative.ai/mcp as an MCP server, then use its quickstart tool
```

Surf focuses on Claude Desktop, ChatGPT Desktop, Claude Code CLI, and Codex CLI. See the
[compatibility matrix](docs/compatibility.md) for the capabilities each client needs and
the latest recorded verification evidence. Browser-only chat surfaces are not supported.

## What Surf does

Surf supplies an agent with a current working learning framework. The agent uses that
framework to help you:

- establish an explicit learning aim and working agreement;
- keep lightweight evidence from real successes, failures, and surprises;
- maintain a correctable understanding of what is useful for you;
- review the evidence and choose one grounded next experiment.

Your agent performs the local work. The Surf server returns the rulebook; it does not read
your practice folder, keep a participant profile, or take over the immediate task you are
trying to complete. See [how Surf works](docs/how-surf-works.md).

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
