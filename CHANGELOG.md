# Surf changelog

Surf releases and framework releases have separate version numbers. Framework changes
are recorded in [`framework/CHANGELOG.md`](framework/CHANGELOG.md).

## Unreleased

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

- First Surf service release, with the public stateless MCP endpoint, versioned framework
  catalogue, generic container build, and landing page.
