# Install and manage the Surf plugin

## Availability and acceptance

The packages in this repository are distributed from `withnative/surf`. Before promoting
an installation route as supported, maintainers must record a clean pass in
[the plugin release runbook](plugin-release-acceptance.md). In particular, the OpenAI
route must work from an unrelated account with no pre-existing Native connection.

If the repository is unavailable or a client route has not passed its current acceptance
check, use the direct MCP connection described under
[Fallback: connect Surf without the plugin](#fallback-connect-surf-without-the-plugin).

## What the plugin installs

The Claude and OpenAI catalogues both point to `plugins/surf`. The package contains:

- one concise, provider-neutral Surf skill;
- a connection to `https://surf.withnative.ai/mcp`; and
- provider manifests that identify and present the package.

It does not contain a copy of Surf's changing framework or curriculum. The client caches
the small package locally; the MCP server returns the current framework when the agent
calls `quickstart`, `get_guide`, or `get_reference`.

## Claude Code

These commands use Claude Code's user scope, so Surf is available across projects:

```text
/plugin marketplace add withnative/surf
/plugin install surf@withnative
```

If the install summary asks for it, run:

```text
/reload-plugins
```

Start a new conversation and say, for example, `Help me get started with Surf.` The Surf
skill should call `quickstart` before providing substantive Surf guidance. Use `/mcp` if
you want to confirm that the plugin-provided `surf` server is connected.

Claude's marketplace and install flow is documented in the
[official Claude Code plugin guide](https://code.claude.com/docs/en/discover-plugins).

## ChatGPT desktop and Codex

The candidate repository-marketplace flow is:

1. Run `codex plugin marketplace add withnative/surf` in a terminal.
2. Restart the ChatGPT desktop app.
3. Open the Plugins Directory and select the **Native** source.
4. Find **Surf** and choose **Install**.
5. Start a new Work or Codex conversation and say, for example,
   `Help me get started with Surf.`

The package includes a standard remote HTTP entry in `.mcp.json`. However, OpenAI's
official packaging documentation also describes ChatGPT connections registered in
Developer mode and referenced through account-created `plugin_asdk_app...` identifiers.
No such identifier is committed here because the documentation does not establish that
one account's identifier is portable to unrelated accounts.

Therefore the five-step route above remains gated by the unrelated-account acceptance
test. Do not present it as the normal installation route unless the runbook contains a
dated pass for the current package and client version. OpenAI also notes that repository
marketplaces are authoring, testing, and team-distribution sources whose availability can
vary by surface. See the [official OpenAI packaging documentation](https://developers.openai.com/plugins/build/plugins).

## Updates

Surf has two independent update channels:

### Framework and curriculum updates

Native deploys these to the managed MCP server. A fresh tool call receives the content in
the running server build; no plugin release or client pull is required. Begin a new Surf
conversation and let the skill call `quickstart` to establish a clean current context.

An already-running conversation is not rewritten retroactively. It can retain previous
tool results, and a client may retain discovered tool definitions until the connection or
session is refreshed.

### Plugin package updates

Changes to the skill, manifests, connection configuration, assets, hooks, or scripts need
a new plugin package version and a client refresh.

For Claude Code:

```text
/plugin marketplace update withnative
/plugin update surf@withnative
/reload-plugins
```

Third-party Claude marketplaces have auto-update disabled by default. Users can enable it
in `/plugin` under **Marketplaces**. Even when an update downloads in the background, the
running session continues with the version it loaded until `/reload-plugins` or the next
launch.

For ChatGPT desktop and Codex:

```text
codex plugin marketplace upgrade withnative
```

Then restart the ChatGPT desktop app, refresh or reinstall Surf from the Plugins
Directory if the updated version is not shown, and use a new conversation. OpenAI's
repository marketplace documentation describes the local client as loading a cached
installed copy rather than reading the source in place.

## Uninstall

In Claude Code:

```text
/plugin uninstall surf@withnative
```

To remove the catalogue too, run `/plugin marketplace remove withnative`. Removing the
marketplace also uninstalls plugins installed from it.

In ChatGPT desktop, uninstall or disable Surf in the Plugins Directory. Alternatively,
remove the installed plugin from the CLI:

```text
codex plugin remove surf@withnative
```

To stop tracking the repository marketplace too, run:

```text
codex plugin marketplace remove withnative
```

Uninstalling the plugin does not delete any Surf practice files you chose to keep on your
machine. Those files are not plugin data and remain under your control.

## Privacy and trust

Installing a plugin gives the client instructions and an MCP connection from code in a
GitHub repository. Review the source and install only from a repository you trust.

The Surf application's tools accept a document choice, not participant content, and the
application stores no participant state. The AI client and provider still process the
conversation, Surf's returned guidance, and local files the agent reads. Hosting and
network infrastructure can process operational metadata. Read the complete
[privacy and data statement](privacy-and-data.md).

## Troubleshooting

### Surf is absent from the catalogue

- Confirm that the repository is public and reachable without authentication.
- Claude: run `/plugin marketplace update withnative`, then inspect `/plugin`.
- OpenAI: run `codex plugin marketplace list`, upgrade `withnative`, restart the desktop
  app, and inspect the **Native** source again.

### The skill is present but Surf tools are missing

- Start a new conversation after installation or update.
- Claude: run `/reload-plugins`, then inspect `/mcp`.
- ChatGPT desktop: open **Settings → MCP servers**, confirm `surf` is enabled, then
  restart the app.
- Confirm that `https://surf.withnative.ai/mcp` is reachable from the client environment.
- Do not continue from packaged or remembered curriculum if `quickstart` cannot run.

### OpenAI asks for a registered connection

This is the portability gate described above. Do not reuse or publish someone else's
`plugin_asdk_app...` value. Either use the direct desktop/Codex connection below, or in
ChatGPT Developer mode register `https://surf.withnative.ai/mcp` for that account and use
the account-specific connection as a local test. Record the result in the release runbook;
do not describe the repository package as portable until a clean unrelated account passes.

## Fallback: connect Surf without the plugin

The direct connection remains a supported fallback and a useful diagnostic.

### Claude Code

```sh
claude mcp add --transport http --scope user surf https://surf.withnative.ai/mcp
```

Start a new conversation and ask the agent to use Surf's `quickstart` tool. Claude
documents remote HTTP as its recommended transport for cloud MCP servers in the
[official MCP guide](https://code.claude.com/docs/en/mcp).

### ChatGPT desktop and Codex

In the ChatGPT desktop app:

1. Open **Settings → MCP servers**.
2. Choose **Add server**.
3. Name it `surf`, choose **Streamable HTTP**, and enter
   `https://surf.withnative.ai/mcp`.
4. Save and restart the app.

For Codex CLI, add this to `~/.codex/config.toml`, then start a new session:

```toml
[mcp_servers.surf]
url = "https://surf.withnative.ai/mcp"
```

The ChatGPT desktop app, Codex CLI, and Codex IDE extension share this local MCP
configuration for the same Codex host. See the
[official OpenAI MCP documentation](https://developers.openai.com/codex/mcp).

The fallback supplies Surf's live tools but not the packaged bootstrap skill. Explicitly
ask the agent to call `quickstart` at the beginning of a fresh Surf conversation.
