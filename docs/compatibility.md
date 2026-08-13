# Compatibility

Surf's launch support target is deliberately narrow: Claude Desktop, ChatGPT Desktop,
Claude Code CLI, and Codex CLI. The landing page may describe this as “Claude or ChatGPT,”
but this matrix is the precise support record. Browser-only chat surfaces are not
supported.

Support requires both:

1. a connection to Surf's remote Streamable HTTP MCP endpoint; and
2. durable access to local files across conversations so the practice does not depend on
   chat memory.

## Indicative verification matrix

The four clients below are Surf's current focus. Fresh end-to-end checks provide indicative
evidence, not a mechanical release gate. Record exact versions, operating systems, dates,
results, and limitations so product judgement can distinguish framework defects from
client or model variance and evaluator ambiguity.

| Client | Surface | OS and client version | Verification date | Remote MCP | Durable local files | Status | Evidence / limitations |
|---|---|---|---|---|---|---|---|
| Claude Desktop | Desktop | Not yet recorded | Not yet recorded | Required | Required | Verification pending | Add a reviewable evidence reference |
| ChatGPT Desktop | Desktop | Not yet recorded | Not yet recorded | Required | Required | Verification pending | Add a reviewable evidence reference |
| Claude Code | CLI | macOS, 2.1.231 | 2026-08-13 | Candidate exercised | Native filesystem access | Positive candidate evidence | Local 0.1.0 probes; explicit MCP allow rules required in noninteractive `dontAsk` mode. See [CLI acceptance evidence](evidence/2026-08-13-cli-acceptance.md). |
| Codex | CLI | macOS, 0.147.0 | 2026-08-13 | Candidate exercised | Native filesystem access | Positive candidate evidence | Local 0.1.0 probes; per-server tool approval required in noninteractive mode. See [CLI acceptance evidence](evidence/2026-08-13-cli-acceptance.md). |

Do not expand this table by implication. A protocol-compatible client may work without
being a supported client; record it separately until the full verification standard has
been met.

## Plugin distribution release gates

The GitHub plugin packages have a stricter distribution gate than the indicative client
matrix above. A clean Claude Code install must work from `withnative/surf`, and an
unrelated OpenAI account with no pre-registered Native connection must install the
repository marketplace package and resolve its MCP tools. Until both pass, Surf must not
claim public GitHub plugin availability. The complete procedure and evidence template are
in the [plugin release acceptance runbook](plugin-release-acceptance.md).

## End-to-end verification standard

For each client, record evidence that a fresh installation can:

1. add `https://surf.withnative.ai/mcp` without a Surf account or credential;
2. initialize successfully and show the Surf identity;
3. discover `quickstart`, `get_guide`, `get_reference`, and `get_doc`;
4. call `quickstart` before a user-facing learning-loop reply;
5. choose and retrieve a primary moment guide that fits the interaction;
6. retrieve a relevant authored reference and product documentation;
7. create or resume a practice in a person-confirmed durable local folder;
8. preserve unrelated agent-instruction files and recover the same practice in a new
   conversation;
9. distinguish authored references from MCP resources; and
10. surface an honest limitation when remote MCP or durable file access is unavailable.

The evidence record should include the operating system, architecture where relevant,
client name and exact version, Surf application version, working framework, test date,
tester, setup path, observed result, limitations, and a reviewable trace or reference that
does not disclose personal practice content. Report positive evidence, likely framework
defects, client/model variance, and evaluator fragility separately; avoid frozen wording
matchers or a single aggregate pass rate.

## Capability notes

Desktop clients can change how connectors, local tools, projects, and filesystem access
are configured. CLI clients can change MCP configuration formats and permission prompts.
The matrix therefore records tested client versions instead of claiming that every past
or future client release works.

Some clients cache MCP server metadata or tool schemas. If a verification uses an existing
connection, remove and reconnect it before treating old names or missing tools as a Surf
failure. Record that step in the evidence rather than assuming a refresh occurred.

## Unsupported and unverified environments

- Browser-only chat cannot maintain the required local file practice.
- A client with remote MCP but no durable local files can read Surf documentation but
  cannot run the longitudinal practice as supported.
- A client with files but no remote MCP cannot retrieve the current managed framework.
- Self-hosted Surf forks are not covered by the official endpoint's compatibility claim.

For the architectural reason behind these requirements, see
[how Surf works](https://github.com/withnative/surf/blob/main/docs/how-surf-works.md).
