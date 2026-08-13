# Why Surf uses MCP

Surf's learning framework should move with the AI frontier without taking your learning
history out of your hands. That combination is why Surf uses MCP.

The official Surf service provides the current shared learning framework. Your AI agent
uses that framework to help you run experiments, reflect on evidence and maintain your
practice locally.

Surf's server does not need an account or a server-side profile of you, and it does not
store your learning history. Your practice stays in ordinary files under your control,
subject to the normal boundaries of your machine, backups, sharing settings and AI
provider.

A cloned curriculum or standalone CLI would make each person responsible for installing
and updating another local package. Copies would drift, leaving people to work out whether
their guidance was still current before they could even begin learning.

The managed service avoids that drift without silently changing the local record of an
established practice. During pre-production, Surf has one freely revisable working
framework, labelled `0.1.0`; it does not promise exact historical framework retrieval or
migrations between drafts. Git history preserves the development record, while the
managed service returns the current framework.

MCP also lets your agent retrieve the guidance it needs progressively instead of loading
the entire framework into every conversation.

The plugin makes Surf easy to install. The managed service keeps the shared framework
current. Your local files keep the continuing practice in your hands.
