---
name: surf
description: Use when someone asks to start, continue, capture, or review a Surf learning practice; asks for Surf guidance or documentation; or names Surf as the AI-agent learning framework. Do not use for web surfing or unrelated products named Surf.
---

# Surf

Use the Surf MCP server at `https://surf.withnative.ai/mcp` as the source of current
Surf guidance. Do not rely on remembered or packaged curriculum.

At the beginning of a fresh Surf conversation, call the Surf MCP tool named
`quickstart` once, before giving substantive Surf guidance. Follow the returned
orientation and use `get_guide`, `get_reference`, or `get_doc` only as the current
quickstart and the person's request require.

Keep the person's practice in ordinary local files at a location they confirm. Do not
send practice-file contents to Surf: its public tools retrieve guidance and do not store
participant state.

If the Surf tools are unavailable, say that the MCP connection is unavailable and point
the person to the direct-connection fallback in
`https://github.com/withnative/surf/blob/main/docs/plugin-installation.md`. Do not invent
guidance or imply that the current framework was retrieved.
