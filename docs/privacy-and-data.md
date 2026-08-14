# Privacy and data

This document describes Surf's technical data boundary. It avoids the broader and usually
misleading claim that a workflow is simply “private.” Surf is one component in a path that
also includes an AI client and provider, a network and hosting stack, a local machine, and
any backups or sharing systems attached to that machine.

## What reaches the Surf application

The MCP endpoint receives the JSON-RPC request needed to call a Surf method. The public
tools accept no participant content. Their inputs are:

- `quickstart`: no arguments;
- `get_guide`: a moment-guide slug;
- `get_reference`: a reference slug;
- `get_doc`: a product-document topic.

MCP initialization also includes normal protocol and client metadata such as the requested
protocol version and client name/version. Plain HTTP requests contain the route being
requested. The application uses these values to return compiled framework or
documentation text.

The Surf application has no participant account, authentication, database, participant
identifier, or participant session. It receives zero participant content through its
defined tool schemas and retains zero participant state. Responses are functions of the
document choice and the content compiled into the running build.

## What does not reach Surf through its tools

Surf's tool schemas do not accept:

- the local locator path or its contents;
- the contents of the local practice folder;
- the person's reports, working agreement, profile, plan, or reviews;
- a participant identity or practice identifier;
- source code or documents from the person's work;
- conversation transcripts;
- model-provider credentials.

The connected agent reads and writes local practice material through the client's local
capabilities, not through Surf. Do not paste sensitive content into a Surf tool argument
or an unrelated request merely because the defined tools do not ask for it.

## Infrastructure metadata

The no-participant-state design describes the Surf application. Network, CDN, platform,
and host infrastructure may process operational metadata such as IP addresses, request
times, routes, user-agent strings, response status, and abuse or security signals. Their
retention and access controls are separate from the application's source-level data
model.

Surf documentation should not turn “no application database” into a claim that no
infrastructure log can exist. Security and reliability investigations may require limited
operational records at those adjacent layers.

## Local files

The practice persists in ordinary files at a location the person confirms. The agent uses
them for continuity across conversations and should keep them readable, provenance-aware,
and correctable. A person can inspect, edit, exclude, move, back up, share, or delete those
files using the controls available on their machine.

Cross-directory continuity uses a separate two-field pointer at
`$HOME/.surf/locator.json` on macOS/Linux or
`%USERPROFILE%\.surf\locator.json` on Windows. It contains a schema version and the
fully expanded absolute path of the confirmed practice, not learning content or a Surf
account identifier. A valid practice in the launch directory takes precedence, so the
agent does not read this user-level pointer in that case. Otherwise the agent reads only
this exact path before asking permission for any bounded recovery search.

The dot-prefixed `.surf` directory is hidden by default in ordinary macOS and Linux file
browsing. That location is reserved for the small continuity pointer; it is not the
default home for the person's learning record. Surf setup normally recommends a visible,
user-findable practice folder and discloses hidden alternatives before confirmation.

The locator is inspectable and independently removable. Deleting it leaves the practice
untouched and returns Surf to the no-global-discovery state. Moving or restoring a
practice requires validating the destination and confirming the pointer update; backing
up the locator alone does not back up the learning record. The path itself can reveal
information such as a local account name or folder choice to the AI client and provider,
but it is not an input to Surf's MCP tools.

Those choices have consequences outside Surf. Device accounts, filesystem permissions,
cloud sync, backups, repositories, collaboration tools, and workplace administration may
make local files available to other people or systems. Surf cannot inspect or enforce
those settings.

The Surf plugin does not own, copy or manage the practice folder. It supplies a trigger
skill and the managed MCP connection; the agent continues to use ordinary local files at
the location the person confirms. Disabling, uninstalling, updating or reinstalling the
plugin does not delete those files. Deleting the plugin cache or marketplace is therefore
not a practice-deletion mechanism.

## The AI client and provider

The AI provider processes the conversation, the request to call Surf, and Surf's returned
guidance. When the agent reads a local practice file, that content may enter the model
context so the agent can use it. The provider's retention, training, regional processing,
enterprise controls, and access policies are governed by the person's provider and client
configuration—not by Surf.

Use the controls appropriate to that provider and environment. Do not place material in a
practice folder that the connected agent is not permitted to process.

## Threat boundaries and non-claims

Surf's small, stateless application surface reduces what the service needs to receive and
retain. It does not establish that:

- the AI conversation is confidential under every client plan;
- local files are encrypted, access-controlled, backed up, or deleted everywhere;
- hosting and network infrastructure produce no logs;
- a compromised client, machine, provider, dependency, or network cannot expose data;
- a fork preserves the official service's architecture or operational controls;
- open source alone makes a deployment secure.

The repository and exact deployed-source link make these claims inspectable. Security
reports should use the private route in
[SECURITY.md](https://github.com/withnative/surf/blob/main/SECURITY.md), not a public issue.

## Practical choices

Before activating a practice:

1. choose a durable location with suitable access and sharing settings;
2. understand which AI provider and account will process the files;
3. keep the practice scoped to information appropriate for that environment;
4. inspect and correct the local record as it develops;
5. inspect, move, back up or remove the separate locator as their continuity needs change;
6. use the person's explicit correction, exclusion, and deletion choices as controlling
   instructions.

For the component roles and request flow, see
[how Surf works](https://github.com/withnative/surf/blob/main/docs/how-surf-works.md).
