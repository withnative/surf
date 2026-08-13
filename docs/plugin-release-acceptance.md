# Plugin release acceptance runbook

This runbook records release evidence for the GitHub-installable Surf packages. Passing
repository validation is necessary but not sufficient: public installation and client
behaviour require clean, human-observed tests.

## Release checklist

Record a dated pass, with the evidence fields below, for every required gate that applies
to the release candidate:

- [ ] `withnative/surf` is public and readable without authentication.
- [ ] The production endpoint and exact public source metadata are healthy.
- [ ] A clean Claude Code GitHub install passes.
- [ ] An unrelated-account OpenAI GitHub install and MCP resolution pass; this is a
      go/no-go gate for that route.
- [ ] A remote framework update works with an unchanged plugin.
- [ ] A plugin package update and client refresh work as documented.
- [ ] Active-session cache behaviour is observed and documented for each provider.
- [ ] Cross-directory practice resumption passes in Claude Code and ChatGPT/Codex Desktop.

Do not mark a gate as passed without recording the evidence fields below. Do not claim
public GitHub availability until every required gate passes.

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
Observed result:
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
2. Run `/plugin marketplace add withnative/surf`.
3. Run `/plugin install surf@withnative` at user scope.
4. Run `/reload-plugins` if prompted.
5. Confirm `/mcp` shows the plugin-provided `surf` server at the exact production URL.
6. Start a new conversation with `Help me get started with Surf.`
7. Confirm the agent calls `quickstart` before substantive Surf guidance and follows the
   returned current framework.
8. Confirm a user-chosen local practice can be created without sending practice content
   as a Surf tool argument.
9. Uninstall Surf and confirm a new conversation no longer has the packaged skill or
   plugin-provided server. Confirm existing practice files remain untouched.

Pass requires the documented two-command install with no manual MCP configuration.

## Gate 3: unrelated-account OpenAI portability

This is a go/no-go gate. Use an account that has no Native membership, no Surf connection,
no pre-registered Native MCP app, and no plugin files copied from a Native account.

1. Record the relationship of the account to Native and the exact client version.
2. Run `codex plugin marketplace add withnative/surf`.
3. Restart the ChatGPT desktop app.
4. Open the Plugins Directory, choose **Native**, and install **Surf**.
5. Do not manually add the Surf MCP server and do not create an account-specific
   `plugin_asdk_app...` mapping.
6. Start a fresh Work or Codex conversation with `Help me get started with Surf.`
7. Confirm the client resolves the package's remote MCP connection, discovers the four
   Surf tools, and calls `quickstart` before substantive guidance.
8. Exercise one guide, one reference, and one product document.
9. Uninstall or disable Surf and confirm the plugin no longer contributes the skill or
   MCP server. Confirm existing practice files remain untouched.

Pass requires repository installation and MCP resolution without account pre-registration.
If it fails because ChatGPT requires a registered `plugin_asdk_app...` connection:

- record the exact UI, error, and surface;
- do not add an ID to the shared manifest;
- do not claim the repository route is portable;
- verify the documented direct-MCP or Developer-mode fallback separately; and
- make a product decision between a two-step skill-plus-connection flow and an official
  directory submission.

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
4. Claude: record the outcome of marketplace update, plugin update, and
   `/reload-plugins` or relaunch.
5. OpenAI: record the outcome of marketplace upgrade, desktop restart, and any required
   refresh or reinstall in the Plugins Directory.
6. Start a fresh conversation and confirm the `P2` package change is active.

Pass requires exact, repeatable client steps. Do not assume third-party auto-update.

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
