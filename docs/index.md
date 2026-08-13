# Surf documentation

This is the catalogue of Surf's public product documentation. The Markdown files in this
directory are canonical: the same content is available in GitHub, over plain HTTP, as MCP
resources, and through Surf's `get_doc` tool.

Product documentation explains Surf itself. It is separate from the working framework
returned by `quickstart`, `get_guide`, and `get_reference`, which guides a person's Surf
practice.

| Topic | Slug | What it covers |
|---|---|---|
| [Documentation index](https://github.com/withnative/surf/blob/main/docs/index.md) | `index` | This catalogue and the distinction between product docs and framework guidance |
| [Frequently asked questions](https://github.com/withnative/surf/blob/main/docs/faq.md) | `faq` | Short answers and routes to deeper material |
| [Why Surf](https://github.com/withnative/surf/blob/main/docs/why-surf.md) | `why-surf` | Richard Ng's canonical account of why Surf exists |
| [Why MCP](https://github.com/withnative/surf/blob/main/docs/why-mcp.md) | `why-mcp` | Managed framework, local control, and the delivery choice |
| [Why Surf is free and open source](https://github.com/withnative/surf/blob/main/docs/why-open-source.md) | `why-open-source` | Why free access and open source follow from Surf's mission and agency |
| [How Surf works](https://github.com/withnative/surf/blob/main/docs/how-surf-works.md) | `how-surf-works` | Architecture, roles, tools, files, and framework model |
| [Privacy and data](https://github.com/withnative/surf/blob/main/docs/privacy-and-data.md) | `privacy-and-data` | What reaches Surf, what does not, and adjacent boundaries |
| [Compatibility](https://github.com/withnative/surf/blob/main/docs/compatibility.md) | `compatibility` | Supported clients, required capabilities, and evidence |
| [About Richard](https://github.com/withnative/surf/blob/main/docs/about-richard.md) | `about-richard` | Richard Ng's creator story, biography, and relationship to Native |
| [Working framework and source](https://github.com/withnative/surf/blob/main/docs/releases-and-source.md) | `releases-and-source` | Pre-production framework policy and exact running source |

Repository-maintainer documents that are not served as product-document topics:

- [Plugin installation and management](plugin-installation.md)
- [Plugin release acceptance runbook](plugin-release-acceptance.md)

Use `get_doc(topic)` with one of the slugs above. Where a client supports MCP resources,
the equivalent URI is `surf://docs/{slug}`. Plain Markdown is available at
`https://surf.withnative.ai/docs/{slug}`.

For framework material, call `quickstart` first. It normally routes to one primary moment
guide; the agent may consult whichever references are useful. **References** are an
authored content kind. **MCP resources** are the protocol primitive that mirrors authored
content for clients that support it. Do not use product documentation as a substitute for
the framework's operating guidance.
