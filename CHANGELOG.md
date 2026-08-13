# Surf changelog

The Surf application, working framework, and plugin package are independently versioned
artifacts. Their matching `0.1.0` numbers at launch are intentional, not a permanent
lockstep policy. Working-framework changes are recorded in
[`framework/CHANGELOG.md`](framework/CHANGELOG.md).

## Unreleased

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
