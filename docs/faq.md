# Frequently asked questions

## What is Surf?

Surf is a public MCP server and open-source learning framework. It gives a supported AI
agent a current method for helping you learn from your real work with agents.
The practice itself is kept in ordinary files controlled through your local environment.
See [how Surf works](https://github.com/withnative/surf/blob/main/docs/how-surf-works.md).

## Who is Surf for?

Surf is for people who want to become more capable with AI agents through evidence from
their own work. It starts without assuming technical expertise and can adapt its language
and depth as evidence accumulates.

## What does Surf do that a normal AI assistant does not?

A normal assistant is usually optimised to complete the task in front of it. Surf gives an
agent a protected learning role: agree a learning aim, capture selected experiences,
maintain a correctable model, review evidence, and propose bounded experiments. This
creates continuity without requiring Surf to keep a server-side profile.

## Why does the learning-loop agent avoid solving my immediate task?

Doing the task and learning from the task are different roles. If the learning agent takes
over whenever work becomes difficult, it changes the experience it is meant to observe and
weakens the evidence. It can preserve the report and offer a neutral handoff to the work
context or a doing-agent; it does not quietly become that doing-agent.

## Why MCP rather than a CLI, application, or cloned repository?

MCP lets an agent retrieve the current framework at the moment it needs it, without each
person installing or upgrading a separate program. Local files retain the person's
evidence and control. Read [why MCP](https://github.com/withnative/surf/blob/main/docs/why-mcp.md).

## How do I install Surf?

Paste `Install the plugin https://github.com/withnative/surf and use the quickstart tool`
into ChatGPT/Codex Desktop or Claude Code. The agent can follow the product-native plugin
flow. If you prefer to do it yourself, each surface installs with two shell commands from
its own CLI, and both also offer an in-product route. For the exact commands, updates,
uninstall and recovery, use the
[canonical installation guide](https://github.com/withnative/surf/blob/main/docs/plugin-installation.md).
Direct MCP connection remains a supported fallback at `https://surf.withnative.ai/mcp`.

## What lives in the plugin?

The installed plugin supplies Surf's trigger skill and MCP connection. The managed MCP
service supplies current Surf guidance. Your practice remains in ordinary local files you
control; it is not stored in the plugin or the Surf application.

## Will uninstalling Surf delete my practice?

No. Disabling or uninstalling the plugin removes its packaged skill and connection, not
the local practice files you chose to keep. You can inspect, move, back up or delete those
files yourself. See [privacy and data](https://github.com/withnative/surf/blob/main/docs/privacy-and-data.md).

## Why is Surf open source?

Inspectability is part of Surf's trust claim. Anyone can examine the server, framework,
tests, and data boundary; run or fork the source; and criticise the educational method
independently of Native. Read [why open source](https://github.com/withnative/surf/blob/main/docs/why-open-source.md).

## Is Surf really free?

The official Surf service is available without an account, authentication, or billing
surface. Its source is licensed under AGPL-3.0-or-later. Running a fork can still involve
infrastructure and AI-provider costs for its operator or users.

## Which Claude and ChatGPT clients work?

Surf's verified plugin routes are ChatGPT/Codex Desktop and Claude Code. Other desktop,
browser and mobile surfaces are expected, untested or unsupported as labelled in the
[compatibility matrix](https://github.com/withnative/surf/blob/main/docs/compatibility.md).
Do not infer support for an unlisted client.

## Does Surf read or store my files?

No local practice file is an input to a Surf tool. The application has no participant
database, authentication, account, or session state. Your agent may read and write local
files in order to run the practice, and your AI provider may process that content. Hosting
and network infrastructure may also process request metadata. Read
[privacy and data](https://github.com/withnative/surf/blob/main/docs/privacy-and-data.md)
for the exact boundary.

## Where does my practice state live?

It lives in a dedicated local folder that you confirm and that your agent can access. A
readable map records where the working agreement, current understanding, plan, dated
evidence, reviews, and working-framework provenance live. The framework avoids relying on
conversation memory when that local source exists. A separate user-home locator contains
only the confirmed folder's absolute path so a new conversation can find it without
searching your home directory. You can inspect or delete that pointer independently;
deleting it never deletes the practice.

## What does my AI provider still see?

Your provider processes the conversation and Surf's tool calls and responses. If your
agent reads local practice files, their contents may also enter the provider's context.
Provider retention, training, privacy, and enterprise controls are governed by your
provider relationship, not by Surf.

## How does Surf adapt around me without a server-side profile?

The agent maintains an inspectable, correctable understanding in your local practice. It
distinguishes stated preferences, observed or reported evidence, inference, and unknowns.
You can correct, exclude, or delete local material. Surf only supplies the framework that
tells the agent how to do this.

## How does the framework change?

During pre-production, Native improves one freely revisable working framework, `0.1.0`.
Surf does not yet promise compatibility with earlier drafts or keep them available through
the service. Git history preserves the development record. Strict versioning, migrations,
and historical retrieval begin when a real production practice depends on a particular
version. See [working framework and source](https://github.com/withnative/surf/blob/main/docs/releases-and-source.md).

## Can I run or fork Surf myself?

Yes. The repository contains the service, working framework, tests, and generic container
packaging needed to build and run it. The official managed endpoint is the supported
product. Native does not promise support or automatic framework updates for forks; their
operators own deployment and update responsibility.

## Who built Surf and why?

Surf was created by Richard Ng and is managed by Native. The final public creator story
and motivation are deliberate launch-gate copy and remain pending Richard's approval. See
[about Richard](https://github.com/withnative/surf/blob/main/docs/about-richard.md).

## How do I report a problem or security issue?

Use a public GitHub issue for reproducible product or documentation problems that contain
no sensitive information. Do not disclose a suspected vulnerability publicly; use the
private route in [SECURITY.md](https://github.com/withnative/surf/blob/main/SECURITY.md).
