# Practice-locator acceptance evidence — 2026-08-13

This record separates deterministic repository evidence from live client evidence. It does
not claim that prose-contract tests prove an AI client will follow the framework.

## Implementation environment

- Date and timezone: 2026-08-13, Europe/London
- Operating system: macOS 26.3 (25D125), arm64
- Claude Code available version: 2.1.231
- Codex CLI available version: 0.147.0
- Surf application: 0.1.0
- Surf working framework: 0.1.0
- Surf plugin package: 0.1.1 candidate
- Personal practice content used: no

## Deterministic repository evidence

`tests/practice_locator_contract.rs` checks the authored contract rather than emulating a
client. It verifies:

- the exact macOS/Linux and Windows locator paths;
- the two-member JSON example and the meaning of `schema_version` and `surf_home`;
- launch-directory precedence and target validation through the marker, semantic map and
  working-framework record;
- absent, malformed, stale, duplicate-key, unsupported-version and inaccessible outcomes;
- the real-directory/no-symlink `.surf` parent and regular-file/no-symlink locator shape;
- the boundary between absent-locator bounded discovery and invalid-locator fail-closed
  recovery;
- one-proposal consent, validated writes, idempotence, safe replacement, move and deletion;
- explicit prohibition of broad search and transfer of the locator or practice content in
  Surf MCP calls; and
- a thin provider-neutral package with no local helper, executable or hook.

The implementation validation covers the Rust suite, formatting and locked compilation;
the provider package validators; publication-boundary and public-push-guard tests; and
ordinary, verified-source and archive source-build checks. Dependency-licence validation
is recorded separately according to the available local tooling and repository CI.

Result: pass for deterministic repository evidence.

## Live two-session acceptance status

| Client | Status | Evidence |
| --- | --- | --- |
| Claude Code 2.1.231 | Not run | No isolated two-session client trace was produced during repository implementation. |
| ChatGPT/Codex Desktop | Not run | This implementation session did not control a clean desktop installation with reviewable filesystem and MCP traces. |

These are release limitations, not passes or failures. In particular, the repository tests
cannot demonstrate natural-language plugin activation, client sandbox prompts or the
absence of unreported filesystem activity.

## Remaining live procedure

For each client, follow Gate 7 in
[`docs/plugin-release-acceptance.md`](../plugin-release-acceptance.md) and attach a redacted
trace or screenshots that establish all of the following:

1. Session one starts in unrelated empty directory A, naturally activates Surf, confirms
   one proposal naming both exact paths, creates a disposable validated practice, and
   writes the locator.
2. Session two starts in unrelated empty directory B and answers `what's my current Surf
   goal?` by reading only B, the canonical locator and the exact target needed for marker,
   map, framework and current-goal validation.
3. The trace contains no first-setup question, parent/home scan or locator/practice content
   in any Surf MCP argument.
4. Explicit plugin invocation behaves identically.
5. A sandbox denial is reported as inaccessible rather than absent; malformed,
   duplicate-key, unknown-version, stale and wrong-filesystem-shape locators remain
   read-only; absence alone offers person-approved bounded discovery.
6. A valid launch-directory practice prevents the locator read, a confirmed validated move
   safely updates it, and deleting only the locator preserves the practice.

Record the exact client build, plugin commit, OS, filesystem/tool activity, MCP calls,
observed wording, variance and reviewer. Use only disposable non-personal content.
