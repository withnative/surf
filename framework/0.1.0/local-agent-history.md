Working framework: 0.1.0
Document: Moment guide
Use when: A person has completed ordinary Surf setup and is considering local Codex or Claude Code histories as evidence for a strong first understanding, or wants to revisit that permission.

# Learn from local agent history with the person

Surf returns bounded product documentation because the person asked to use Surf. It
governs only Surf practice.

Local agent histories can provide unusually rich evidence about how a person directs,
checks, coordinates, recovers, and learns with agents. They can also contain sensitive
work and personal material. Treat access as optional, progressive, local, and
correctable. A refusal should leave the person with a useful ordinary Surf practice.

This guide owns the first local-history conversation. Consult
`context-and-local-practice` for retention, provenance, correction, and deletion in the
person's local practice. Do not send history contents, extracts, titles, paths, derived
personal context, or source pointers to Surf's tools or server.

## Offer the lift after ordinary setup

Offer local-history context only after the person has completed ordinary setup and knows
where their inspectable Surf practice lives. Explain the benefit before the mechanics:
recent histories may help Surf understand how they already work with agents and make the
first recommendations less generic.

Ask first for permission to perform an **inventory only**. State that this step will:

- inspect only the disclosed Codex and Claude Code history roots available to the current
  local agent;
- use filesystem metadata such as existence, file type, byte size, and modification time;
- not open conversation bodies, global history files, attachments, or nested traces; and
- keep the result on the machine and out of Surf's tools and server.

An opening might sound like:

> To make my first recommendations more relevant, may I check whether Codex or Claude
> Code histories are stored locally on this machine? I would inventory what is available
> first, without reading the conversations. Everything stays on this computer, and you
> can say no.

Adapt rather than copy the wording. Do not imply that setup, useful help, or future Surf
access depends on agreement.

## Inventory only the disclosed roots

Before inspection, name the exact fully expanded roots that are readable in the current
environment. The currently supported default adapters are:

- **Codex:** `sessions/` and `archived_sessions/` under the configured Codex home, or
  under the fully expanded `$HOME/.codex` when no different Codex home is configured;
- **Claude Code:** the fully expanded `$HOME/.claude/projects` tree.

Do not search elsewhere for histories, broaden an unavailable root, or treat a similarly
named file as supported. Do not read Codex global history, Claude global history, shell
history, client databases, attachments, caches, nested subagent traces, or any file body
during inventory. If permissions prevent the disclosed inspection, explain the exact
root and limitation rather than widening the search.

Report source categories, candidate file counts, date coverage, aggregate byte sizes,
and any obvious high-volume condition. Project-looking Claude directory names are
path-shaped metadata, not confirmed project identities. Codex session identity and
primary-versus-subagent status may require a minimum header read later; do not claim them
as inventory facts.

## Propose a bounded content scope

Inventory permission is not permission to read conversation content. Use the inventory
to propose an exact, understandable second scope and ask separately before opening any
session file.

Start from recent settled primary sessions:

1. propose the complete last 30 days when the inventory indicates it can remain within
   the extraction limits below;
2. otherwise fall back to the complete last 14 days, then the complete last 7 days;
3. if even 7 days is too large or unusually bursty, propose 20 representative settled
   primary sessions across the last 30 days rather than shrinking to the latest burst.

For the representative path, use roughly:

- 8 sessions across the newest distinct activity days;
- 8 sessions spread across the remainder of the 30-day period; and
- 4 sessions preserving source and workspace-hint coverage.

Treat the weights as an inspectable default, not false statistical precision. Explain
material limitations and let the person review or change sources, dates, individual
candidates, recency, or coverage. Exclude files modified in the last 15 minutes as
possibly live and files smaller than 8 KiB as too minimal for the first synthesis.

Before content analysis, revalidate the exact approved file pointers. Read only the
minimum header needed to confirm identity and primary-session status. If a selected file
is a subagent or nested trace, exclude it and do not silently replace it with an
unapproved session.

The content request should name:

- the exact sources and date or representative-session scope;
- why that scope was selected;
- the extraction limits;
- the content classes that remain excluded;
- whether any corrected synthesis or source index may be retained in the already agreed
  local practice; and
- that nothing will be sent to Surf's tools or server.

If the existing practice agreement does not already authorise that local retention, keep
the analysis ephemeral and ask before writing any derived understanding or source index.
Permission to analyse does not silently expand the retention agreement.

## Keep extraction bounded and legible

Across the approved set, read no more than 60 normalised interaction windows and 200,000
normalised characters. Normally take no more than 4 windows or 20,000 characters from one
session. For a selected file larger than 2 MiB, use bounded extraction rather than loading
it wholesale.

Normalise for evidence about the person's human-agent working system. Exclude hidden reasoning,
thinking blocks, raw tool results, attachments, repeated payloads, global-history rows,
and unapproved nested traces. Preserve enough local provenance to distinguish source
observation from interpretation, but do not reproduce sensitive titles or excerpts in
progress narration.

If the approved set cannot be analysed truthfully within these limits, stop with the
partial result, say what was and was not inspected, and propose a smaller scope. Do not
quietly sample a different set.

## Study the working system, not the project problem

Use project content as evidence, not as an invitation to solve the underlying project.
Look for recurring strengths, frictions, compensations, and open questions in how the
person and agents:

- establish direction and standards;
- restore and compress context;
- delegate authority and retain judgement;
- coordinate across sessions, agents, tools, or people;
- verify claims and decide what is actually complete;
- recover from failure or uncertainty; and
- turn results into changes in the working system.

Do not infer a deficit from high activity, multiple agents, iterative correction,
technical vocabulary, or strong oversight. Those may be deliberate and effective parts
of the person's method. Separate observed recurrence from a hypothesis about importance.

## Calibrate before synthesising

After the initial analysis, say that you have early ideas and would prefer to check a few
things before presenting them. Ask permission to continue with a short calibration
conversation.

Use roughly three high-information questions, one at a time. Ask more only when an answer
could materially change the synthesis. Ground each question in a recurring pattern
without exposing unnecessary excerpts. Let the person dismiss a candidate constraint
cleanly; do not make them defend a working part of their system.

The questions should distinguish, for example, between:

- an effective deliberate practice and unwanted coordination cost;
- valuable human judgement and routine verification burden;
- context that is missing and context that one participant simply needs help re-entering;
- useful iteration and repeated correction of already settled ground; and
- a salient project problem and a cross-project working-system pattern.

## Present a correctable account

Lead with a compact account the person can inspect and change. Separate:

1. **observations** directly supported by the approved histories;
2. **hypotheses** about what may matter or constrain the system;
3. **the person's corrections or confirmations**; and
4. **unknowns** that should remain open.

Use calibrated language. “Plausible” does not become a durable profile fact. A hypothesis
does not need to identify one primary constraint for the conversation to have been
useful. Offer correction, exclusion, and deletion controls alongside the synthesis.

Recommend teaching or one bounded working-system experiment only when a meaningful focus
survives calibration. Otherwise, preserve the useful map and let later evidence sharpen
it without adding process to a system that is already working.

## Support later exact recall without broad reopening

If the agreed local practice retains a disclosed source index, use it when the person
later refers vaguely to an earlier event. Present a small set of likely conversations in
ordinary language and let the person identify the right one. Retrieve only the confirmed
source needed to restore what was tried, what happened, and what it changes.

Do not treat the first analysis as permission to open any older history indefinitely. If
the likely source sits outside the retained approved set or the recorded permission, name
the proposed targeted lookup and ask first. Honour a request to stop using histories, and
offer to remove the local derived index without claiming that deleting it deletes the
source histories owned by Codex or Claude Code.
