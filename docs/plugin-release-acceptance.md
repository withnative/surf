# Plugin release acceptance runbook

This runbook records release evidence for the GitHub-installable Surf packages. Existing
installation and activation evidence supports leading with the plugin route. Passing
repository validation is still necessary but not sufficient: final release acceptance
requires clean, human-observed tests with exact versions and reviewable evidence.

## Release checklist

Record a dated pass, with the evidence fields below, for every required gate that applies
to the release candidate:

- [ ] `withnative/surf` is public and readable without authentication.
- [ ] The production endpoint and exact public source metadata are healthy.
- [ ] A clean Claude Code GitHub install passes through the `claude plugin` CLI route.
- [ ] A clean Claude Code GitHub install passes through the `/plugin` slash-command route.
- [ ] A clean ChatGPT/Codex Desktop GitHub install and MCP resolution pass through the
      `codex plugin` CLI route.
- [ ] A clean ChatGPT/Codex Desktop GitHub install and MCP resolution pass through the
      in-app Plugins Directory route.
- [ ] A remote framework update works with an unchanged plugin.
- [ ] A plugin package update and client refresh work as documented through the Claude
      CLI and slash-command routes.
- [ ] A plugin package update and client refresh work as documented through the OpenAI CLI
      and in-app Plugins Directory routes.
- [ ] Active-session cache behaviour is observed and documented for each provider.
- [ ] Cross-directory practice resumption passes in Claude Code and ChatGPT/Codex Desktop.
- [ ] Disable/uninstall preserves the person's local Surf practice on both surfaces.
- [ ] Existing standalone Surf MCP configuration is changed only after explicit
      confirmation, and the post-change plugin connection is healthy.

Do not mark a gate as passed without recording the evidence fields below. The current
plugin-first public copy is bounded to the named supported surfaces; do not expand it to
mobile, browser-only or otherwise untested clients.

## Evidence header

Copy this block for each test:

```text
Test:
Date and timezone:
Tester:
Account relationship to Native:
Operating system and architecture:
Client and exact version:
Plugin package version / Git commit:
Surf application version:
Working framework version:
Starting state:
Commands and UI steps:
Reload, restart or new-conversation boundary:
Observed result:
Uninstall/disable result and local-practice preservation:
Standalone MCP pre-state and any confirmed mutation:
Limitations or variance:
Reviewable trace or screenshot reference:
Personal practice content excluded from evidence: yes / no
Result: pass / fail / blocked
```

## Gate 1: repository and endpoint preflight

1. From a signed-out browser, open `https://github.com/withnative/surf` and confirm the
   repository is public.
2. Confirm both catalogue files are available at their expected paths.
3. Confirm `https://surf.withnative.ai/mcp` initializes and exposes `quickstart`,
   `get_guide`, `get_reference`, and `get_doc`.
4. Confirm `https://surf.withnative.ai/source` names a public commit in
   `withnative/surf` and that the commit matches the deployed source.
5. Run the repository CI and retain the successful run URL.

## Gate 2: clean Claude Code install

Use a profile with no Surf marketplace, plugin, or standalone MCP connection.

1. Record `claude --version` and the operating system.
2. Run `claude plugin marketplace add withnative/surf`.
3. Run `claude plugin install surf@withnative` at the default `user` scope.
4. Confirm `claude plugin list` shows Surf, then start a Claude Code session.
5. Run `/reload-plugins` if prompted.
6. Confirm `/mcp` shows the plugin-provided `surf` server at the exact production URL.
7. Start a new conversation with `Help me get started with Surf.`
8. Confirm the agent calls `quickstart` before substantive Surf guidance and follows the
   returned current framework.
9. Confirm a user-chosen local practice can be created without sending practice content
   as a Surf tool argument.
10. Run `claude plugin uninstall surf@withnative` and confirm a new conversation no longer
    has the packaged skill or plugin-provided server. Confirm existing practice files
    remain untouched.

Pass requires the documented two-command install with no manual MCP configuration.

### Gate 2a: Claude Code slash-command route

Repeat gate 2 on a fresh profile from inside a terminal session, using the slash commands
instead of the CLI. Start the session first, then run
`/plugin marketplace add withnative/surf` and `/plugin install surf@withnative`, then
`/reload-plugins` if prompted. Confirm the install from the `/plugin` browser rather than
from `claude plugin list`, and continue with steps 6 to 9 of gate 2. Remove with
`/plugin uninstall surf@withnative`. This
route remains supported and is the documented path for anyone who does not run the CLI
directly. Record it separately from the CLI route; neither is evidence for the other.

Separately record whether a user-scope `claude plugin install` becomes visible in the
Claude Code desktop application after a restart. A user-scope install was observed active
there on 14 August 2026, but not on a clean profile and not with the restart taken
specifically after a CLI reinstall, so this gate must still record its own result.

## Gate 3: clean ChatGPT/Codex Desktop install

Use a clean profile with no Surf marketplace, plugin, standalone Surf MCP connection or
plugin files copied from another profile.

1. Record the account starting state, exact ChatGPT desktop app version, and
   `codex --version`.
2. Run `codex plugin marketplace add withnative/surf`.
3. Run `codex plugin add surf@withnative` and confirm `codex plugin list` shows Surf.
4. Do not manually add the Surf MCP server.
5. Start a fresh Work or Codex conversation with `Help me get started with Surf.`
6. Confirm the client resolves the package's remote MCP connection, discovers the four
   Surf tools, and calls `quickstart` before substantive guidance.
7. Start a second fresh conversation with an ordinary request such as
   `What's my current Surf goal?` and confirm natural-language activation.
8. Exercise one guide, one reference, and one product document.
9. Run `codex plugin remove surf@withnative` and confirm the plugin no longer contributes
   the skill or MCP server. Confirm existing practice files remain untouched.

Pass requires the documented two-command install and bundled MCP resolution without a
manual direct-MCP setup. Record any account, workspace-policy or client-version variance
without treating a different surface as equivalent evidence.

### Gate 3a: ChatGPT/Codex Desktop in-app route

Repeat gate 3 on a clean profile using the in-product route instead: run
`codex plugin marketplace add withnative/surf`, restart the ChatGPT desktop app, open the
Plugins Directory, choose **Native**, and install **Surf**. Then run steps 4 to 8 above and
uninstall or disable Surf from that card. This route remains supported and is the only one
available to someone who never opens a terminal beyond the marketplace step.

Separately record where a `codex plugin add` install appears in the ChatGPT desktop
application after a restart. The maintainer reports that it appears in a less prominent
area of the interface than an in-app install; capture the exact location and app version
so the installation guide can name it.

## Gate 4: remote framework update with an unchanged plugin

1. Install plugin package version `P1` and record working framework version `F1` from a fresh
   `quickstart` result.
2. Keep the plugin package and marketplace version unchanged.
3. Deploy a reviewable server build whose framework has a small, identifiable change and
   reports version `F2`.
4. Start a fresh conversation and call `quickstart` through plugin package version `P1`.
5. Confirm the result identifies `F2` and contains the reviewable change.
6. Confirm no marketplace refresh, plugin reinstall, or package update was required.

Pass demonstrates that changing framework content is delivered from the MCP server rather
than copied into the plugin.

## Gate 5: plugin package update

1. Begin with installed plugin package version `P1`.
2. Make a harmless, reviewable change to packaged copy or wiring and bump both provider
   manifests to `P2` in the same commit.
3. Publish the marketplace source change.
4. Claude, CLI route: run `claude plugin marketplace update withnative`, then either
   `claude plugin uninstall surf@withnative` and `claude plugin install surf@withnative`,
   or `claude plugin update surf@withnative`. Record each command's exact output, the
   version reported by `claude plugin list` after the marketplace update but before the
   plugin update, and the restart actually taken. Confirm the bare-name `claude plugin
   update surf` failure is still present or has been fixed.
5. Claude, slash-command route: repeat step 4 inside a terminal session using
   `/plugin marketplace update withnative`, `/plugin uninstall surf@withnative` and
   `/plugin install surf@withnative`, then `/reload-plugins` or relaunch. Record it
   separately; neither route is evidence for the other.
6. OpenAI, CLI route: run `codex plugin marketplace upgrade withnative`,
   `codex plugin remove surf@withnative` and `codex plugin add surf@withnative`, and
   record each command's exact output.
7. OpenAI, in-app route: run `codex plugin marketplace upgrade withnative`, restart the
   ChatGPT desktop app, open **Plugins Directory → Native → Surf**, and record whether an
   update is offered, whether it applies, and whether an uninstall and reinstall from that
   card was required instead.
8. Start a fresh conversation after each route and confirm the `P2` package change is
   active.

Pass requires exact, repeatable client steps. Do not assume third-party auto-update, and
do not treat a marketplace refresh as having moved an installed plugin.

## Gate 6: active-session behaviour

For each provider:

1. Start a conversation on package `P1` and framework `F1`, and retain a visible result.
2. Publish package `P2` and/or deploy framework `F2` while that conversation remains open.
3. Record whether a new tool call in the existing conversation receives `F2`.
4. Record whether tool definitions, skill instructions, and prior returned content remain
   at their previous versions.
5. Apply the documented reload or restart, then compare the same open conversation with a
   new conversation.

The expected contract is conservative: a new MCP call can receive newly deployed server
content, but previous messages are never rewritten; packaged instructions and discovered
tool definitions may remain loaded until refresh, reload, restart, or a new conversation.

## Gate 7: cross-directory practice resumption

Run this separately in Claude Code and ChatGPT/Codex Desktop. Use disposable empty launch
directories and a disposable practice containing no personal content. Record the evidence
fields above plus every filesystem read, write and directory listing performed by the
client or agent.

1. Start session one in an empty directory unrelated to the proposed practice.
2. Activate Surf in natural language, confirm a setup proposal that names the exact
   practice home and canonical locator, and complete setup.
3. Verify the locator contains only `schema_version: 1` and the fully expanded absolute
   `surf_home`, and that the practice validates through its marker, `README.md` map and
   working-framework record.
4. End the conversation. Start session two in a different empty unrelated directory and
   ask `what's my current Surf goal?` as a natural-language request, without an explicit
   plugin invocation or path.
5. Confirm the plugin activates, reads only the launch directory and canonical locator
   before the exact target, validates the target, and returns the stored goal without a
   first-setup question or broad search.
6. Inspect the Surf MCP trace and confirm no locator value, practice content or participant
   content was supplied in any tool argument.
7. Repeat the return with explicit plugin invocation and confirm identical discovery.
8. Separately exercise absent, malformed JSON, duplicate-key, unknown-version, stale-target
   and filesystem-denied locator states. Only absence may offer bounded discovery; every
   invalid or inaccessible state remains read-only and asks for direction without search.
9. Confirm a valid launch-directory practice wins without any locator read. Confirm a
   validated, person-confirmed move safely replaces the pointer, and deleting only the
   locator leaves the practice intact and restores the no-global-discovery state.

The dated implementation record and current live-test limitations are in
[practice-locator acceptance evidence](evidence/2026-08-13-practice-locator-acceptance.md).

## Gate 8: existing standalone MCP connection

For each supported client where a standalone server is configurable:

1. Begin with a standalone entry whose URL is exactly `https://surf.withnative.ai/mcp`.
2. Install the Surf plugin and record whether duplicate names or tools appear.
3. Explain that the plugin supplies the same endpoint and ask whether to remove the
   standalone entry.
4. Decline once and confirm no configuration changes.
5. Repeat, approve cleanup, and record the exact entry changed.
6. Reload or restart and confirm the plugin-provided connection still exposes
   `quickstart`, `get_guide`, `get_reference`, and `get_doc`.
7. Repeat with a similarly named entry at a different URL and confirm it is not labelled
   or removed as an exact duplicate.

The local Surf practice must remain untouched in every case.

## Provider-documentation preflight

The implementation copy was checked on 13 August 2026 against the official OpenAI plugin
packaging and MCP guides and the official Claude Code plugin and MCP guides linked from
[the canonical installation guide](plugin-installation.md#provider-documentation-verification).
At release acceptance, reopen those sources and record any command, menu-label or surface
variance before passing the corresponding gate.
