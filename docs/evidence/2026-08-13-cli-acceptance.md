# CLI acceptance evidence — 2026-08-13

This is indicative evidence for the local Surf 0.1.0 candidate, not a compatibility
certification or mechanical release gate. The candidate server ran at a temporary local
HTTP endpoint on macOS. Each probe began in a fresh, empty temporary directory and could
read but not change local files.

## Scenarios

Two short scenarios were run independently in each client:

1. orient to an existing practice and route a direct retained-preference correction,
   without inventing files or making the correction; and
2. respond to a difficult client-call report in protected capture, without advice or a
   causal diagnosis.

Both scenarios required the client to call `quickstart` and retrieve whichever moment
guide and references it judged relevant.

## Claude Code

- Client: Claude Code 2.1.231
- Reported model: `claude-sonnet-5`
- Connection: strict one-server MCP configuration, no session persistence
- Permission setup: `dontAsk` with explicit allow rules for Surf's four tools

The orientation probe retrieved `quickstart`, `setting-up`, and
`context-and-local-practice`. It treated the missing launch-directory marker as a reason
for bounded discovery, invented no practice location, changed nothing, and asked for the
actual path. An earlier fresh run chose `returning-and-capture` instead; both routes stayed
bounded, so this is useful model/routing variance rather than evidence of a framework
defect.

The capture probe retrieved `quickstart` and `returning-and-capture`. It preserved the
person's report without advice, diagnosis, or a settled causal claim; truthfully described
the capture as conversation-only because no durable practice was present; and explicitly
closed capture.

Without explicit allow rules, the same noninteractive `dontAsk` setup connected and
discovered all four tools but denied tool execution client-side. This is a client
permission/configuration limitation, not a Surf transport or content failure.

## Codex CLI

- Client: Codex CLI 0.147.0
- Model: not exposed in the recorded JSONL events
- Connection: ephemeral client with user configuration and workspace rules disabled
- Permission setup: read-only sandbox plus per-server default tool approval

The orientation probe retrieved `quickstart`, `returning-and-capture`, and
`context-and-local-practice`. It selected the direct-correction route, described
provenance and confirmation without performing the correction, listed what it consulted,
and did not invent or change files.

The capture probe retrieved the same three documents. It kept the report separate from a
settled cause, gave no advice, and truthfully said no durable Surf practice was available.
Its phrase “captured here” followed by “couldn't preserve it” was slightly ambiguous about
chat-only versus durable capture, but the limitation itself was explicit.

Without the per-server approval setting, fresh noninteractive calls were cancelled by the
client even under a global never-ask policy. This is client configuration variance.

## Reading the evidence

Positive evidence: both clients connected, discovered the four-tool surface, retrieved
the quickstart and relevant typed documents, stayed within the no-takeover boundary, and
handled protected capture without advice or diagnosis.

Client/model variance: noninteractive tool approvals need explicit configuration; Claude
showed two defensible routes when the prompt claimed an existing practice but the launch
directory contained no marker.

Framework defects indicated: none from these probes.

Coverage limits: this did not test Desktop clients, the hosted endpoint, durable setup and
resumption across conversations, malformed local practice recovery, or the whole authored
catalogue. Those remain future evidence, not implied support.
