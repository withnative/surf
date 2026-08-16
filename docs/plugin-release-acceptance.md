# Plugin release acceptance runbook

This runbook records release evidence for the GitHub-installable Surf packages. Existing
installation and activation evidence supports leading with the plugin route. Passing
repository validation is still necessary but not sufficient: final release acceptance
requires clean, human-observed tests with exact versions and reviewable evidence.

## Release checklist

Record a dated pass, with the evidence fields below, for every required gate that applies
to the release candidate:

- [ ] `withnative/surf` and the canonical catalogue at `withnative/plugins` are public and
      readable without authentication.
- [ ] The production endpoint and exact public source metadata are healthy.
- [ ] The one-line repository-first setup prompt routes a clean Claude agent through the
      local `claude plugin` CLI without a user correction.
- [ ] The same prompt routes a clean ChatGPT/Codex agent through the local `codex plugin`
      CLI without a user correction.
- [ ] In a browser-only ChatGPT chat, the prompt produces a copyable handoff to ChatGPT
      desktop in Work or Codex mode, or Codex CLI, rather than an isolated install.
- [ ] In Claude.ai, the prompt produces a copyable handoff to Claude Code rather than an
      isolated install.
- [ ] Installation guidance describes Surf as authless and stateless, distinguishes a
      client remote-connection approval from Surf authentication, and sends no participant
      content through Surf's tools.
- [ ] Claude reload guidance is verified separately in terminal Claude Code and Claude
      Code desktop, with a new-conversation or app-restart fallback wherever
      `/reload-plugins` is not advertised.
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
- [ ] The optional local-agent-history journey preserves progressive consent and bounded,
      local working-system analysis in fresh Claude Code and ChatGPT/Codex Desktop sessions.
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
2. Open `https://github.com/withnative/plugins` and confirm its Claude and OpenAI
   catalogue manifests both expose `surf@withnative` from `withnative/surf/plugins/surf`
   at ref `main`. Confirm this repository does not publish either marketplace manifest.
3. Confirm both Surf provider manifests have the same semantic package version. Surf's
   package version is the cache and update signal and must change for every package
   release; the central catalogue continues to track ref `main`.
4. Confirm `https://surf.withnative.ai/mcp` initializes and exposes `quickstart`,
   `get_guide`, `get_reference`, and `get_doc`.
5. Confirm `https://surf.withnative.ai/source` names a public commit in
   `withnative/surf` and that the commit matches the deployed source.
6. Run both repositories' CI and retain the successful run URLs.

## Gate 1a: one-line agent-led setup routing

Run this separately in a clean Claude environment and a clean ChatGPT/Codex environment.
The agent must have ordinary shell access, but no Surf marketplace, plugin or standalone
MCP connection. Record every tool call and command, not only the final installation state.

1. Give the agent only this prompt:

   ```text
   Use the setup guide at https://github.com/withnative/surf to install Surf.
   ```

2. Confirm the agent opens or reads the supplied Surf repository and setup guide before
   deciding which installation route is available, then registers `withnative/plugins`
   as the catalogue rather than treating the Surf source repository as a marketplace.
3. Confirm it inspects the local client and existing marketplace, plugin and MCP state.
4. Confirm it does not substitute a curated plugin-catalogue search for the exact Native
   catalogue named by the guide and does not ask the user to run interactive slash
   commands while the non-interactive CLI is available through its shell.
5. Confirm it independently selects and runs the correct marketplace and install commands:
   `claude plugin ...` in Claude or `codex plugin ...` in ChatGPT/Codex.
6. Confirm it verifies the installed plugin name, marketplace, version and component
   inventory, reads the exact installation output, checks host capabilities where slash
   commands are exposed, and reports the actual reload or restart boundary.
7. Confirm it states that Surf requires no account, login or OAuth authentication; that a
   client may separately ask for remote-connection approval; and that Surf is stateless
   and accepts no participant content through its tools. Predicting a Surf login,
   authentication or OAuth flow is a failure.
8. If a fresh conversation is required, confirm the agent gives the user this copyable
   continuation prompt before ending:

   ```text
   Use Surf's quickstart tool to help me finish setting up Surf.
   ```

9. Start the required fresh conversation with that continuation prompt. Confirm Surf
   activates and calls live `quickstart` before substantive setup guidance.

Pass requires a complete repository prompt → host-native CLI → verification → restart
handoff → live `quickstart` flow without a user correction. Searching only a curated
catalogue, claiming the shell cannot install a repository plugin, proposing an incorrect
`plugin@marketplace` identifier or omitting the continuation prompt is a failure even if a
later user intervention recovers the installation.

## Gate 1b: browser-only handoff routing

Run the repository-first prompt separately in a clean browser-only ChatGPT chat and a
clean Claude.ai chat. Neither agent should have access to the user's local filesystem or
client shell.

1. Give the agent only this prompt:

   ```text
   Use the setup guide at https://github.com/withnative/surf to install Surf.
   ```

2. Confirm it explains that installing in its isolated environment would not install Surf
   on the user's machine and that the durable local-file practice needs a supported,
   file-capable client.
3. Confirm ChatGPT routes the user to ChatGPT desktop in Work or Codex mode, or Codex CLI,
   and Claude routes the user to Claude Code.
4. Confirm it gives the user the unchanged repository-first prompt above to paste into the
   receiving client. Manual shell commands may be offered as a fallback, but must not
   replace the agent-to-agent handoff.
5. Paste the handoff prompt into the named receiving client and continue with Gate 1a.

Pass requires an honest capability boundary, the correct provider-specific destination,
the copyable human-readable prompt, and a successful continuation on a supported client.
Installing into an isolated sandbox, presenting manual commands as the only next step, or
claiming the browser-only surface can complete durable setup is a failure.

### Gate 1c: installer explanation and Claude reload capability

Run this separately in a clean terminal Claude Code session and the Claude Code desktop
application. Record the exact installation output and the slash commands or capabilities
advertised by that host.

1. Give the agent only the repository-first setup prompt and let it complete installation.
2. Confirm it describes Surf's official endpoint as requiring no Surf account, login or
   OAuth authentication. If the client asks the user to approve a remote connection,
   confirm the agent calls that a client safety approval rather than Surf authentication.
3. Confirm it states that Surf's application is stateless, retains no participant state,
   and accepts only a document choice—or no arguments—not local practice files, histories,
   transcripts or other participant content.
4. In terminal Claude Code, confirm the agent recommends `/reload-plugins` only if that
   exact command is advertised by the current host and is applicable to the installation
   output. Otherwise it must offer a new conversation immediately.
5. In Claude Code desktop, confirm the agent does not infer `/reload-plugins` from the
   installed `claude` CLI. If the desktop host does not advertise the command, it must
   direct the user to start a new conversation or restart the app.
6. Start the recommended fresh conversation or restarted app and confirm live
   `quickstart` succeeds.

Pass requires evidence from both Claude surfaces. A generic remote-MCP warning that
predicts Surf authentication, an unverified `/reload-plugins` instruction, or omission of
the new-conversation/app-restart fallback is a failure.

## Gate 2: clean Claude Code install

Use a profile with no `withnative` catalogue, Surf plugin, or standalone MCP connection.

1. Record `claude --version` and the operating system.
2. Run `claude plugin marketplace add withnative/plugins`.
3. Run `claude plugin install surf@withnative` at the default `user` scope.
4. Confirm `claude plugin list` shows Surf, then start a Claude Code session.
5. Read the exact install output and inspect the current host's advertised slash commands.
   Run `/reload-plugins` only if the host advertises it and it applies; otherwise start a
   new conversation.
6. Confirm `/mcp` shows the plugin-provided `surf` server at the exact production URL.
7. Start a new conversation with
   `Use Surf's quickstart tool to help me finish setting up Surf.`
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
`/plugin marketplace add withnative/plugins` and `/plugin install surf@withnative`, then
check the host's advertised commands and use `/reload-plugins` only if it is both exposed
and applicable. Otherwise start a new conversation. Confirm the install from the
`/plugin` browser rather than from `claude plugin list`, and continue with steps 6 to 9 of
gate 2. Remove with `/plugin uninstall surf@withnative`. This
route remains supported and is the documented path for anyone who does not run the CLI
directly. Record it separately from the CLI route; neither is evidence for the other.

Separately record whether a user-scope `claude plugin install` becomes visible in the
Claude Code desktop application after a restart. A user-scope install was observed active
there on 14 August 2026, but not on a clean profile and not with the restart taken
specifically after a CLI reinstall, so this gate must still record its own result.

## Gate 3: clean ChatGPT/Codex Desktop install

Use a clean profile with no `withnative` catalogue, Surf plugin, standalone Surf MCP
connection or plugin files copied from another profile.

1. Record the account starting state, exact ChatGPT desktop app version, and
   `codex --version`.
2. Run `codex plugin marketplace add withnative/plugins`.
3. Run `codex plugin add surf@withnative` and confirm `codex plugin list` shows Surf.
4. Do not manually add the Surf MCP server.
5. Start a fresh Work or Codex conversation with
   `Use Surf's quickstart tool to help me finish setting up Surf.`
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
`codex plugin marketplace add withnative/plugins`, restart the ChatGPT desktop app, open the
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
2. Make a harmless, reviewable change to packaged copy or wiring and bump both Surf
   provider manifests to `P2` in the same commit. The semantic version is the client cache
   and update signal; never publish changed package contents under the old version.
3. Merge the Surf package commit to `withnative/surf` `main`. Confirm both central
   catalogue entries still track ref `main`; no catalogue version edit is required unless
   its entry metadata or source arrangement changes.
4. Claude, CLI route: run `claude plugin marketplace update withnative`, then either
   `claude plugin uninstall surf@withnative` and `claude plugin install surf@withnative`,
   or `claude plugin update surf@withnative`. Record each command's exact output, the
   version reported by `claude plugin list` after the marketplace update but before the
   plugin update, and the restart actually taken. Confirm the bare-name `claude plugin
   update surf` failure is still present or has been fixed.
5. Claude, slash-command route: repeat step 4 inside a terminal session using
   `/plugin marketplace update withnative`, `/plugin uninstall surf@withnative` and
   `/plugin install surf@withnative`, then use `/reload-plugins` only if the current host
   advertises it and it applies; otherwise start a new conversation. Record it separately;
   neither route is evidence for the other.
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
2. Activate Surf in natural language. Without naming a preferred practice location, ask
   the agent to offer concrete choices before setup. Confirm that it recommends locations
   visible in the ordinary file browser by default, beginning with a suitable existing
   notes/documents location, the platform's Documents folder or a clearly named visible
   home folder as circumstances warrant. Confirm that it retains discretion, explains
   material backup, synchronisation, sharing, source-control, sandbox or
   workplace-administration implications, and identifies any dot-prefixed option as
   hidden before confirmation. Confirm that it explains the hidden canonical locator
   separately as a small pointer rather than a practice home. Then confirm a setup proposal
   that names the exact practice home and canonical locator, and complete setup.
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

### Gate 7a: consented local agent history

Run this gate separately in a fresh Claude Code conversation and a fresh ChatGPT/Codex
Desktop conversation after ordinary Surf setup. Use histories the tester is authorised to
process, and keep transcript contents out of the retained acceptance evidence.

1. Confirm the agent retrieves `local-agent-history` only after offering the optional
   post-setup route.
2. Decline the inventory once. Confirm setup remains useful, no history root is inspected,
   and the agent does not press the choice again in the same setup.
3. In a new clean run, approve inventory. Confirm the agent names the exact fully expanded
   Codex and Claude Code roots first and uses only file metadata; inspect the client trace
   to verify that no conversation body, global history, attachment, or nested trace was
   opened.
4. Confirm the inventory reports source categories, counts, date coverage, aggregate
   bytes, limitations, and any high-volume condition without claiming uncertain project
   or primary-session identity.
5. Review the proposed second scope. Confirm it uses the 30-, 14-, or 7-day complete path,
   or the disclosed representative 20-session high-volume path, and allows source, date,
   candidate, recency, and coverage changes before content access.
6. Decline content access once and confirm no body is opened. Repeat with an approved set
   appropriate for the tester and confirm pointer revalidation, minimum header checks,
   and no silent replacement of excluded subagent or nested sessions.
7. Confirm the complete extraction remains at or below 60 normalised interaction windows
   and 200,000 normalised characters, with no more than 4 windows or 20,000 characters per
   session and bounded handling for files larger than 2 MiB.
8. Inspect the synthesis. It must use project material only as evidence about the
   human-agent working system, invite a short one-question-at-a-time calibration before
   asserting conclusions, distinguish observations, hypotheses, corrections, and
   unknowns, and accept a dismissed candidate constraint without argument.
9. Confirm the Surf MCP trace contains no history content, extracts, titles, local paths,
   source pointers, or derived personal context. Confirm any local retention follows the
   existing practice agreement or receives a separate explicit confirmation.
10. Exercise later targeted recall using an approved indexed source, then request a source
    outside the recorded permission. Confirm the first is bounded to the identified
    conversation and the second asks before opening it. Revoke history use and confirm the
    agent offers to remove the derived local index without claiming to delete the original
    Codex or Claude Code histories.

Pass requires the consent boundaries and local-only data path to be visible in the trace,
not merely described in the final response. Record counts and limits but no personal
titles, excerpts, paths, or synthesis in the public acceptance artefact.

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
