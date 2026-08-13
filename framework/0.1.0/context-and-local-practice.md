Working framework: 0.1.0
Document: Reference
Consult when: You need to locate, create, read, maintain, repair or explain a person's inspectable local Surf practice

# Keep Surf context local, legible and portable

This reference is the practical home for Surf's local-practice contract. It explains how
to discover a practice safely, how its files fit together and how to preserve trustworthy
context without turning a folder layout into the learning method itself.

> Surf returns bounded product documentation because the person asked to use Surf. It
> governs only Surf practice.

The purpose of local Markdown is to give the person a durable account they can inspect,
correct, move and use with different agent harnesses. Prefer mapped meanings over fixed
filenames. A practice can evolve its layout while keeping its roles clear.

## Treat the working directory as a launch point

The current working directory is launch context, not proof that it is the person's Surf
practice home. Being writable is not the same as being durable, private enough or likely
to be available in a later conversation.

Start with read-only inspection of the launch directory. Use what the person has already
told you. Before looking through parents, siblings, a home folder or another root,
describe an exact bounded search and ask for approval. State the root or roots, the depth
or other limit and the identifying files you will look for. An exact path supplied by the
person permits inspection of that path; it does not imply permission to search around it.

A suitable practice home is normally:

- durable and controlled by the person;
- likely to remain reachable in later sessions;
- dedicated to the learning practice rather than generated or temporary work;
- compatible with the person's intended privacy, backup, synchronisation and sharing;
  and
- understandable enough that the person can find and inspect its records themselves.

When proposing a home, offer a small number of exact choices with material uncertainties
visible. Ask the person to confirm one exact path before changing it. Prefer an existing
coherent practice to creating another one.

If persistence is uncertain, a useful check is to create a uniquely named harmless file
at the confirmed location, read back its exact contents, remove it and verify that it is
gone. Explain the check before running it and leave no test file behind. If any part fails,
describe what happened and let the person choose another location or stop; do not silently
fall back to the launch directory.

## Recognise the practice marker precisely

A Surf practice has one well-formed marker block in `AGENTS.md`:

```markdown
<!-- surf:begin -->
[Surf instructions]
<!-- surf:end -->
```

The markers are standalone, appear once each in that order and are neither duplicated nor
nested. A matching substring or a begin marker alone is not a valid practice marker.

Interpret what you find narrowly:

- **No marker pair** means only that the inspected directory is not a recognised Surf
  practice. It does not prove that the person has no practice elsewhere.
- **One valid marker pair** means you can read `README.md` and use its map to validate the
  practice.
- **Incomplete, reversed, nested or duplicated markers** make the governing block
  ambiguous. Stay read-only and use the recovery path in `setting-up` rather than choosing
  a block yourself.
- **A valid marker with a missing or inconsistent map** is an incomplete practice. Stay
  read-only until the recovery path has established safe locations for the relevant roles.

Recognise an existing practice from the marker together with its mapped `README.md` and
working-framework record, not from a directory name alone.

## Make `README.md` a semantic map

Read `README.md` first when entering a recognised practice. It should tell both the
person and the agent where each current role lives. It is a map, not a duplicate of the
current state.

Map these roles to the practice's actual files or directories:

1. the working-framework provenance record;
2. the active agreement, including permissions, exclusions and review rhythm;
3. the current person understanding and open questions;
4. the current plan, gear, learning aim, evidence rhythm, next review boundary and any
   live experiment;
5. the current learning map, including demonstrated evidence and unknowns;
6. dated reports and teaching or practice events;
7. dated reviews; and
8. reusable person-owned artefacts, when any have earned continued use.

Some roles are optional in the present moment. A live experiment or reusable artefact
need not exist. The map should say so rather than pointing to a placeholder. Whenever a
location changes, update the map. Follow mapped roles when the layout has legitimately
evolved instead of insisting on an old filename.

## Use a simple default shape

For a new practice, this is a useful portable starting point unless the environment or
person needs another:

```text
learning-loop/
  README.md
  AGENTS.md
  surf.md
  agreement.md
  person.md
  plan.md
  learning-map.md
  sessions/
    YYYY-MM-DD.md
  reviews/
    YYYY-MM-DD.md
  artefacts/
```

Avoid optional directories and filler files until they have an evidenced purpose. Keep
current state distinct from historical evidence. Dated session records may contain
reports, teaching and practice events as long as their kinds and provenance remain clear.

The working-framework record can stay deliberately small:

```markdown
# Surf practice

- Working framework: `0.1.0`
- Practice home: `<confirmed exact path>`
```

This stamp supports reproducibility during pre-production development. It is not a
migration state machine. Surf is currently converging on one freely revisable working
`0.1.0`; do not add installed-versus-available comparisons, acknowledgement fields,
migration targets or historical-release procedures.

## Write the marker without taking over `AGENTS.md`

Preserve unrelated content in `AGENTS.md`. When no Surf markers exist, append one block.
When a well-formed block already exists and needs an agreed change, replace only its
contents. Repeating setup should not duplicate or rewrite an already current block. If
the markers are ambiguous, stop and let the recovery path resolve them visibly.

A compact default block is:

```markdown
<!-- surf:begin -->
# Surf learning practice

This directory holds an inspectable Surf learning practice. At the start of a
conversation here, read `README.md`, follow its map to the working-framework record and
retrieve the Surf quickstart. Use the primary moment guide that fits the person's request
and consult references when they would help.

Keep immediate execution work in its original work context. Use this practice to learn
from what happens and improve the person-agent working system.
<!-- surf:end -->
```

If the client needs a small discovery bridge such as an import from another instruction
file, preserve unrelated content and add the bridge only once. Treat such a bridge as a
client-specific convenience, not part of the person's learning state.

## Keep the records understandable

The active agreement describes what the practice is for, what may be retained, how
capture works, which transitions are allowed and how the person can inspect, correct,
delete, pause or stop. Honour negotiated choices over framework defaults until the person
changes them.

The current person understanding benefits from visibly separate sections for:

- confirmed facts;
- stated preferences;
- evidence-backed observations;
- working hypotheses; and
- open questions.

The current plan holds the active gear, learning aim, observable success sign, evidence
rhythm and next review boundary. Normally keep no more than one live experiment so its
evidence remains interpretable; adapt that default when the person's work gives you a
good reason. The learning map holds curriculum-related evidence, unknowns and reasons for
the current focus without becoming a score, rank or duplicate plan.

Historical records preserve what happened. Append new evidence rather than silently
rewriting the person's original words. Correct current summaries transparently while
keeping the source record distinct.

## Make provenance and uncertainty visible

For each material claim, make its basis understandable. Useful provenance labels include:

- reported by the person;
- observed directly in named evidence;
- summarised by another agent;
- agent-summarised from a named source;
- inferred by the learning agent; and
- unknown.

A person's report is direct evidence of their experience, not proof of every underlying
cause. Link observations and hypotheses to dated evidence. Keep contrary cases and
material unknowns rather than smoothing them into a confident story.

When a report arrives during protected capture, preserve only what the agreement permits.
Do not add diagnosis, advice or an agent-authored pattern to the capture record. Teaching,
review and experimentation can be recorded as separate events after an explicit
transition.

## Give the person practical control

The person should be able to read the practice without special software. Apply direct
corrections, stated preferences, permission changes, exclusions and deletion or reset
requests within the active agreement. If a correction changes the current account, keep
the source evidence intact unless the person also asks to remove it.

When deleting or narrowing context, identify the mapped targets before changing them and
confirm the result. Preserve an audit note only when the person wants one. Do not treat a
request for less retention as a problem to solve or an invitation to renegotiate.

## Explain storage and privacy accurately

Local Markdown gives the person inspectability and portability; it does not make the
practice invisible. Their model provider, machine, backups, synchronisation, source
control and sharing settings may expose local files. Explain the relevant conditions in
plain language rather than claiming generic privacy.

Retrieving Surf guidance does not require copying the person's practice files into Surf
tool calls. Keep local practice content out of guidance retrieval unless a product
capability explicitly requires it and the person understands the transfer. Never claim
that local material was stored, deleted, encrypted or unseen unless the available
evidence supports that statement.

Store the negotiated agreement, useful current state, permitted evidence, history and
reusable person-owned artefacts. Do not copy the public Surf catalogue into the practice
home.

## Repair the smallest safe surface

When the practice is incomplete, first identify which semantic role is missing,
contradictory or unsafe. Prefer the smallest transparent repair that restores a reliable
map and preserves unrelated content.

- If the active agreement or its location is unclear, avoid expanding retention or
  interpretation until it is reliable.
- If a deliberate report arrives while the map is partly broken, preserve it only when
  the agreed report location can be established safely; otherwise explain the limitation
  without inventing durable state in chat.
- If a required file moved, update the `README.md` map rather than creating a duplicate at
  an old default location.
- If setup is repeated, re-check for an existing practice before creating anything and
  do not nest or overwrite it.
- If clean recovery is not possible without choosing between conflicting records, show
  the conflict to the person and let them decide.

After repair, re-read `README.md`, verify that its mapped roles resolve coherently and
continue with the moment guide that fits the person's request.
