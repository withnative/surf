# Plugin package 0.1.3 update acceptance — 14 August 2026

> Historical route: these tests used the former Surf-owned `withnative` marketplace. Surf
> no longer publishes that marketplace; current clean installs register the canonical
> `withnative/plugins` catalogue. The package and client observations remain useful, but
> this evidence does not verify the new catalogue route.

This evidence covers the CLI routes that could be exercised truthfully from the
maintainer's existing local client states after plugin package `0.1.3` was published on
`withnative/surf` `main`. It does not stand in for the Claude slash-command or Codex
in-app routes, and it does not claim a Codex `0.1.2` to `0.1.3` update where no `0.1.2`
installation existed.

## Claude Code qualified update

- **Date and timezone:** 14 August 2026, 11:14–11:15 BST
- **Tester:** Codex, acting at the Native maintainer's direction
- **Account relationship to Native:** maintainer-owned local client profile
- **Operating system and architecture:** macOS 26.3, arm64
- **Client and exact version:** Claude Code 2.1.231
- **Plugin package version / Git commit:** `0.1.2` to `0.1.3` /
  `e5184809aec0683599b225927ffc8002d15542ea`
- **Surf application version:** `0.1.0`
- **Working framework version:** `0.1.0`
- **Starting state:** the `withnative` GitHub marketplace was configured and
  `surf@withnative` `0.1.2` was installed and enabled at user scope.
- **Commands and UI steps:** `claude plugin marketplace update withnative`; `claude
  plugin list`; `claude plugin update surf`; `claude plugin update surf@withnative`;
  `claude plugin list`; `claude plugin details surf@withnative`.
- **Observed update behaviour:** refreshing the marketplace did not silently move the
  installed plugin: `claude plugin list` still reported `0.1.2`. The bare-name update
  failed with `Plugin "surf" not found`. The qualified update reported `Plugin "surf"
  updated from 0.1.2 to 0.1.3 for scope user. Restart to apply changes.` The subsequent
  list and details commands reported `0.1.3`, one `next-step` skill and one `surf` MCP
  server.
- **Reload, restart or new-conversation boundary:** a fresh non-persistent `claude -p`
  process was started after the update. Its permission policy allowed only
  `mcp__plugin_surf_surf__quickstart` for the acceptance call.
- **Observed result:** the new process resolved MCP server `plugin:surf:surf`, called
  `quickstart` successfully and received the `Quickstart` document for working framework
  `0.1.0`.
- **Uninstall/disable result and local-practice preservation:** not exercised in this
  update test. The user-scope plugin remains installed and enabled at `0.1.3`. No practice
  was located, read, created, changed or removed.
- **Standalone MCP pre-state and any confirmed mutation:** not inspected or mutated.
- **Limitations or variance:** the Claude `/plugin` slash-command route and desktop
  visibility after restart were not exercised.
- **Reviewable trace or screenshot reference:** command output retained in the executing
  Codex task; repository commit and production provenance are public.
- **Personal practice content excluded from evidence:** yes
- **Result:** pass for the qualified Claude CLI update and fresh-process MCP call.

## ChatGPT/Codex clean install at 0.1.3

- **Date and timezone:** 14 August 2026, 11:15–11:17 BST
- **Tester:** Codex, acting at the Native maintainer's direction
- **Account relationship to Native:** maintainer-owned local client profile
- **Operating system and architecture:** macOS 26.3, arm64
- **Client and exact version:** Codex CLI 0.147.0
- **Plugin package version / Git commit:** `0.1.3` /
  `e5184809aec0683599b225927ffc8002d15542ea`
- **Surf application version:** `0.1.0`
- **Working framework version:** `0.1.0`
- **Starting state:** no `withnative` marketplace and no Surf plugin were configured in
  Codex. This was therefore a clean install, not a package-update test.
- **Commands and UI steps:** `codex plugin marketplace add withnative/surf --ref main
  --json`; `codex plugin add surf@withnative --json`; `codex plugin list`; a fresh
  `codex exec --ephemeral --approve-for-me` session; `codex plugin remove
  surf@withnative --json`; `codex plugin marketplace remove withnative`.
- **Observed install behaviour:** the marketplace resolved as `withnative`; installation
  reported plugin `surf@withnative`, version `0.1.3`, and the expected installed cache
  path.
- **Reload, restart or new-conversation boundary:** a fresh ephemeral Codex process was
  started from a disposable empty directory. Automatic approval review was enabled for
  the read-only MCP call; the prompt prohibited shell, filesystem and practice changes.
- **Observed result:** the process resolved MCP server `surf`, called `quickstart`
  successfully and received the `Quickstart` document for working framework `0.1.0`.
- **Uninstall/disable result and local-practice preservation:** the plugin and marketplace
  were removed after the test, restoring the original Codex configuration. No practice
  was located, read, created, changed or removed.
- **Standalone MCP pre-state and any confirmed mutation:** not inspected or mutated.
- **Limitations or variance:** an installed `0.1.2` package was absent, so the Codex
  marketplace-upgrade and `0.1.2` to `0.1.3` package-update path could not be observed.
  The in-app Plugins Directory route was not exercised.
- **Reviewable trace or screenshot reference:** command output retained in the executing
  Codex task; repository commit and production provenance are public.
- **Personal practice content excluded from evidence:** yes
- **Result:** pass for clean Codex CLI install, fresh-process MCP resolution and cleanup;
  not run for the Codex installed-package update route.

## Production evidence

At 11:13 BST, `https://surf.withnative.ai/source` returned HTTP 307 to the exact public
commit `e5184809aec0683599b225927ffc8002d15542ea`. The main CI run and the dedicated
production-deployment verification for that commit both passed.
