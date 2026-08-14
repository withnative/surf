# Install and manage the Surf plugin

This is the canonical guide for installing, updating, removing and recovering Surf on
its supported plugin surfaces.

## Start with the repository link

Paste this into **ChatGPT/Codex Desktop** or **Claude Code**:

```text
Install the plugin https://github.com/withnative/surf and use the quickstart tool
```

The agent should inspect the public repository, use the product-native plugin flow below,
and ask before changing an existing standalone Surf MCP connection. If you are on mobile,
in a browser-only chat, or on another unlisted surface, use a supported desktop client
instead; the plugin flow and durable local-file practice are not verified there.

## ChatGPT/Codex Desktop

The Codex CLI installs Surf in two commands. The install verb is `add`, not `install`:

```sh
codex plugin marketplace add withnative/surf
codex plugin add surf@withnative
```

`codex plugin add` accepts `surf@withnative` or `surf --marketplace withnative`, and
`--json` if you want a machine-readable install result. Codex has no installation scope:
configuration and the marketplace snapshot live under `~/.codex/`. Confirm the result with
`codex plugin list`.

This also covers the ChatGPT desktop app: restart it after installing. A CLI-installed
plugin appears there in a less prominent area of the interface than an in-app install, so
check the Plugins Directory listing if you do not spot it straight away.

To install in-product instead:

1. In a terminal, add the public repository marketplace:

   ```sh
   codex plugin marketplace add withnative/surf
   ```

2. Restart the ChatGPT desktop app.
3. In Work or Codex mode, open the **Plugins Directory**.
4. Select the **Native** source, open **Surf**, and choose **Install**.

Choose one route or the other: the CLI and the desktop app share the same `~/.codex` host,
so if you already ran `codex plugin add`, run `codex plugin remove surf@withnative` before
installing from the Plugins Directory.

Either way, start a new conversation and say `Help me get started with Surf.`

To invoke Surf explicitly, choose `@surf` and add your request. Where the client exposes
individual skill selectors, choose **Find your next step with AI** (`$next-step`). Ordinary
language such as `What's my current Surf goal?` can activate the Surf skill without an
explicit mention. The skill should call `quickstart` before giving substantive Surf
guidance.

Use `/mcp` in the composer to inspect connected servers. The official OpenAI documentation
covers [Git-backed repository marketplaces](https://developers.openai.com/plugins/build/plugins#add-a-marketplace-from-the-cli)
and the [ChatGPT/Codex MCP controls](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

## Claude Code

The `claude` CLI installs Surf in two commands. The default install scope is `user`, so
Surf is available across projects:

```sh
claude plugin marketplace add withnative/surf
claude plugin install surf@withnative
```

Useful flags:

- `claude plugin install -s|--scope user|project|local` chooses where the plugin is
  recorded; `user` is the default.
- `claude plugin marketplace add --scope user|project|local` chooses where the marketplace
  is declared, and `--sparse <paths...>` limits the checkout for large repositories.
- `-y|--yes` and `--config <key=value>` exist but do nothing for Surf. `-y` applies only to
  marketplaces that install by running a declared command, and Surf's entry is a plain
  directory source; Surf's manifest declares no `userConfig` options.

The install runs without a confirmation prompt and reports
`✔ Successfully installed plugin: surf@withnative (scope: user)`. Confirm the result with
`claude plugin list`.

These two commands are also the route for the **Claude Code desktop application**: run
them in a terminal, then restart the app. A user-scope install is active there.

Inside an interactive Claude Code terminal session, the equivalent slash commands are:

```text
/plugin marketplace add withnative/surf
/plugin install surf@withnative
```

The `/plugin` slash command exists only in the terminal build of Claude Code. It is not
available in the Claude Code desktop application, which has its own plugin browser.

If the install summary says `Run /reload-plugins to activate.`, run:

```text
/reload-plugins
```

Start a new conversation and say `Help me get started with Surf.` To invoke the skill
explicitly, use `/surf:next-step`; ordinary Surf requests can activate it naturally too.
Use `/mcp` to confirm the plugin-provided `surf` server is connected.

Anthropic documents these commands, user scope, reload behaviour and marketplace safety
in its [Claude Code plugin guide](https://code.claude.com/docs/en/discover-plugins).

## What the plugin installs

Both provider catalogues point to `plugins/surf`. The installed package contains:

- a small Surf trigger skill;
- a connection to `https://surf.withnative.ai/mcp`; and
- the provider manifests that identify and present Surf.

The roles stay separate:

- **The installed plugin** supplies the trigger skill and MCP connection.
- **The managed MCP service** supplies the current Surf framework and product guidance.
- **Your local practice** remains in ordinary files at a location you confirm and control.

The plugin does not contain your practice or a copy of Surf's changing framework. A fresh
`quickstart`, `get_guide`, `get_reference`, or `get_doc` call receives content from the
running managed service.

## Updates

Surf has two independent update channels.

### Framework and guidance updates

Native deploys framework and product-document updates to the managed MCP service. No
plugin release is needed. Start a new Surf conversation so the installed skill calls
`quickstart` and establishes a clean, current context.

Previous messages are not rewritten. An active conversation can retain earlier tool
results, and a client can retain discovered tool definitions until a reload, restart or
new conversation.

### Plugin package updates

Changes to the skill, manifests or connection configuration require a new plugin package.

For ChatGPT/Codex Desktop, refresh the marketplace snapshot and reinstall from the CLI.
The Codex marketplace verb is `upgrade` and the plugin verbs are `remove` and `add`:

```sh
codex plugin marketplace upgrade withnative
codex plugin remove surf@withnative
codex plugin add surf@withnative
```

For the in-app route, run `codex plugin marketplace upgrade withnative`, restart the
ChatGPT desktop app, open **Plugins Directory → Native → Surf**, and apply an offered
update. If the old version remains, uninstall and reinstall Surf from that card, then start
a new conversation. OpenAI clients install a cached copy rather than reading the repository
in place.

For Claude Code, third-party marketplaces do not auto-update by default. The Claude
marketplace verb is `update` and the plugin verbs are `uninstall` and `install`. Refresh
and reinstall deterministically from the CLI:

```sh
claude plugin marketplace update withnative
claude plugin uninstall surf@withnative
claude plugin install surf@withnative
```

`claude plugin marketplace update` refreshes the catalogue only. It does not move an
already-installed plugin, so `claude plugin list` still reports the old version after it
runs. Run it first regardless: an install resolves from the locally cached marketplace
snapshot, so without a refresh it can serve an older package than the one published.

`claude plugin update` is the alternative to uninstall-and-reinstall, and it needs the
`plugin@marketplace` form:

```sh
claude plugin update surf@withnative
```

The bare name works for `uninstall` but not for `update`: `claude plugin update surf`
fails with `Plugin "surf" not found` even when the plugin is installed. A successful
update reports `Plugin "surf" updated from 0.1.0 to 0.1.1 for scope user. Restart to apply
changes.`, so restart Claude Code afterwards.

The equivalent slash commands inside a terminal session are:

```text
/plugin marketplace update withnative
/plugin uninstall surf@withnative
/plugin install surf@withnative
/reload-plugins
```

You can instead enable auto-update for **withnative** under `/plugin` → **Marketplaces**.
Skip `/reload-plugins` only when the install summary says the plugin is already active.
A CLI update applies to a Claude Code session started afterwards, which is what its
`Restart to apply changes.` notice means. Start a new session if an installed or updated
plugin does not appear.
Removing or reinstalling the plugin does not remove your local Surf practice.

## Uninstall or disable

For ChatGPT/Codex Desktop, remove Surf from the CLI:

```sh
codex plugin remove surf@withnative
```

To stop tracking the repository marketplace too, run:

```sh
codex plugin marketplace remove withnative
```

You can also open **Plugins Directory → Native → Surf** in the ChatGPT desktop app and
disable or uninstall Surf there.

For Claude Code, remove Surf from the CLI:

```sh
claude plugin uninstall surf@withnative
```

`claude plugin uninstall` takes `-s|--scope` to match the scope you installed at, and
`claude plugin disable surf@withnative` keeps the plugin installed but inactive. To remove
the catalogue too, run `claude plugin marketplace remove withnative`; Claude Code also
uninstalls plugins installed from a marketplace when that marketplace is removed.

The equivalent slash commands inside a terminal session are
`/plugin uninstall surf@withnative` and `/plugin marketplace remove withnative`.

Uninstalling or disabling Surf removes the packaged trigger skill and connection. It does
not delete the local practice files you chose to keep. Those files are not plugin data and
remain under your control.

## Recovery and troubleshooting

### Surf is absent from the catalogue

- Confirm `https://github.com/withnative/surf` is reachable without authentication.
- ChatGPT/Codex Desktop: run `codex plugin marketplace list`, then
  `codex plugin marketplace upgrade withnative`, and confirm Surf appears in
  `codex plugin list`. For the in-app route, restart the app and inspect the **Native**
  source again.
- Claude Code: run `claude plugin marketplace update withnative`, then confirm Surf appears
  in `claude plugin list`. Inside a terminal session, `/plugin marketplace update
  withnative` and the `/plugin` browser do the same.
- `claude plugin validate <path>` checks a plugin or marketplace manifest if you are
  working from a local checkout or a fork.

### The skill is present but the Surf tools are missing

- Start a new conversation after installation or update.
- ChatGPT/Codex Desktop: restart the app, open **Settings → MCP servers**, confirm the
  plugin-provided `surf` server is enabled, and type `/mcp` in the composer.
- Claude Code: run `/reload-plugins` if the install summary requested it, then inspect
  `/mcp` and the `/plugin` **Errors** tab.
- Confirm `https://surf.withnative.ai/mcp` is reachable from the client environment.
- Do not continue from remembered or packaged guidance if `quickstart` cannot run.

### A standalone Surf MCP connection already exists

The plugin already supplies the same managed endpoint. An exact standalone connection to
`https://surf.withnative.ai/mcp` may be redundant and can produce duplicate names or tools,
depending on the client. Do not remove, disable or rewrite it automatically.

Identify the exact entry and URL, explain the overlap, and ask before changing it. If the
person declines or the endpoints cannot be matched confidently, leave both in place. If
they approve cleanup, remove only the confirmed standalone entry, reload or restart, and
verify the plugin-provided `surf` connection still exposes `quickstart`, `get_guide`,
`get_reference`, and `get_doc`. A similarly named connection with a different URL is not
an exact duplicate.

## Direct MCP fallback

Direct MCP connection remains a supported fallback. It is useful when plugin installation
is unavailable and as a connection diagnostic.

### ChatGPT desktop and local Codex clients

In the ChatGPT desktop app:

1. Open **Settings → MCP servers**.
2. Choose **Add server**.
3. Name it `surf`, choose **Streamable HTTP**, and enter
   `https://surf.withnative.ai/mcp`.
4. Save, then select **Restart**.

The ChatGPT desktop app, Codex CLI and Codex IDE extension share MCP configuration for the
same Codex host. For a manual Codex configuration, add this to `~/.codex/config.toml`:

```toml
[mcp_servers.surf]
url = "https://surf.withnative.ai/mcp"
```

Start a new conversation and explicitly ask the agent to call `quickstart`.

### Claude Code

```sh
claude mcp add --transport http surf --scope user https://surf.withnative.ai/mcp
```

Start or reload Claude Code, inspect `/mcp`, then ask the agent to call `quickstart`.
Anthropic recommends HTTP for remote MCP servers in its
[MCP guide](https://code.claude.com/docs/en/mcp).

The direct fallback supplies Surf's tools but not the packaged trigger skill. Your local
practice has the same data boundary either way; do not send its contents as Surf tool
arguments. Read [privacy and data](privacy-and-data.md) and the
[compatibility matrix](compatibility.md) before adapting these steps to another surface.

## Provider-documentation verification

These commands and menu labels were checked on 13 August 2026 against the official
[OpenAI plugin packaging guide](https://developers.openai.com/plugins/build/plugins),
[OpenAI MCP guide](https://learn.chatgpt.com/docs/extend/mcp?surface=cli),
[Claude Code plugin guide](https://code.claude.com/docs/en/discover-plugins), and
[Claude Code MCP guide](https://code.claude.com/docs/en/mcp). Client UI and commands can
change; record exact client versions and any variance during release acceptance.

The `claude plugin` and `codex plugin` command surfaces above, including their verbs and
flags, were read from `--help` on the installed binaries on 14 August 2026. The
`claude plugin` uninstall, install, marketplace-update and update commands were executed
and observed on macOS the same day; the exact commands, output and remaining gaps are in
[CLI install acceptance evidence](evidence/2026-08-14-cli-install-acceptance.md).
