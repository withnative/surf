# Surf changelog

The Surf application, working framework, and plugin package are independently versioned
artifacts. Their matching `0.1.0` numbers at launch are intentional, not a permanent
lockstep policy. Working-framework changes are recorded in
[`framework/CHANGELOG.md`](framework/CHANGELOG.md).

## Unreleased

- Move Surf discovery to the canonical `withnative/plugins` catalogue while keeping the
  setup guide and package source in `withnative/surf`. Retire this repository's conflicting
  marketplace manifests; the public plugin identity remains `surf@withnative`.
- Add an optional, progressive-consent local Codex and Claude Code history route to the
  working framework, with metadata-first inventory, bounded analysis, calibration, and
  correctable synthesis while keeping participant content out of Surf's server.

- Fix future Surf revisions at `AGPL-3.0-only`, so Native can review any future
  licence version before adopting it, and publish the change as plugin package
  `0.1.3`. Revisions published before this change retain their existing
  `AGPL-3.0-or-later` grants.
- Rename the single shared Surf skill to `next-step`, broaden its stable activation
  boundary for plausible AI-agent learning and reflection, and keep precise routing in
  remotely served guidance for plugin package `0.1.2`.
- Add the deterministic user-home practice-locator contract to working framework `0.1.0`
  and reinforce it in plugin package `0.1.1` without adding local runtime code.

## 0.1.0 — 2026-08-13

- Align the Surf application version with the `0.1.0` working framework and `0.1.0`
  plugin package for a clear launch identity while preserving their independent future
  release triggers.
- Prepare Surf's first public source tree, documentation, licensing, contribution policy,
  and continuous-integration checks.
- Adopt `surf` consistently as the Rust package, binary, MCP server name, resource scheme,
  and local practice marker.
- Serve the nine-document product catalogue through `get_doc`, `surf://docs/{slug}`, and
  `/docs/{slug}` from the same compiled Markdown.
- Expose fail-closed, explicitly verified source provenance through initialization,
  `surf://source`, `/source`, and the landing footer.
- Prepare aligned Claude and OpenAI repository-marketplace packages around one thin Surf
  skill and the managed MCP endpoint, with explicit release gates and update contracts.

## 0.0.1 — 2026-08-12

- First Surf application release, with the public stateless MCP endpoint, versioned
  framework catalogue, generic container build, and landing page. Superseded by `0.1.0`;
  the historical `v0.0.1` release remains unchanged.
