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

## Discover the practice deterministically

The current working directory is launch context, not proof that it is the person's Surf
practice home. Being writable is not the same as being durable, private enough or likely
to be available in a later conversation.

Use this discovery order exactly:

1. Inspect only the launch directory, read-only. If its `AGENTS.md` marker, `README.md`
   semantic map and mapped working-framework record form one coherent Surf practice, use
   it and stop discovery. **A valid launch-directory practice wins; do not read the
   user-level locator.**
2. Otherwise, read only the canonical locator path for the platform:
   `$HOME/.surf/locator.json` on macOS/Linux or
   `%USERPROFILE%\.surf\locator.json` on Windows. Resolve `$HOME` or `%USERPROFILE%`
   from the client's current user environment only to construct that one path. Do not
   probe alternative home variables, XDG directories, application-support directories,
   parent folders or similarly named files.
3. Validate the locator before following it. Then inspect only its exact `surf_home`
   target and recognise a practice from the marker, map and working-framework record
   together. Pointer existence never proves that the target is a practice.
4. Only an absent locator permits the existing bounded-discovery conversation. An invalid
   locator remains read-only and requires the person's direction before a recovery search
   or mutation.

This order applies whether Surf was activated naturally or explicitly. Filesystem clients
and sandboxes differ: if the canonical locator or its exact target cannot be read because
access is denied, treat it as inaccessible. Explain the exact path and limitation and ask
for direction; do not reinterpret denial as absence or widen the search.

Use what the person has already told you. Before looking through parents, siblings, a home
folder or another root during bounded recovery, describe an exact bounded search and ask
for approval. State the root or roots, the depth or other limit and the identifying files
you will look for. An exact path supplied by the person permits inspection of that path;
it does not imply permission to search around it.

## Validate the user-level locator exactly

The locator is a small pointer, not part of the person's learning record. It has one
canonical location per platform and is UTF-8 JSON without a byte-order mark. Its top-level
value is an object containing exactly these two member names, each exactly once:

```json
{
  "schema_version": 1,
  "surf_home": "/absolute/path/to/the/confirmed/practice"
}
```

`schema_version` is the integer `1`. It versions only the locator structure and
interpretation, not the Surf application, plugin, working framework or practice.
`surf_home` is one non-empty, fully expanded, platform-absolute string. On macOS/Linux it
is rooted at `/`. On Windows it is a drive-rooted path such as `C:\Users\Ari\Surf` or a
complete UNC path such as `\\server\share\Surf`. A drive-relative path such as `C:Surf`
and a root-relative path such as `\Surf` are not absolute. JSON escaping does not change
the resulting filesystem path.

Do not accept `~`, environment-variable references, globs or a list of candidates. Do not
put learning content, participant identifiers, server-side identifiers or credentials in
the locator. JSON whitespace and object-member order are immaterial; every other
difference in structure is invalid. Invalid includes malformed JSON or UTF-8, a byte-order
mark, duplicate keys, a missing or additional key, a non-integer or unsupported
`schema_version`, and a non-string or non-absolute `surf_home`.

The filesystem shape is also exact. If the immediate `$HOME/.surf` or
`%USERPROFILE%\.surf` entry exists, it must be a real directory and must not be a
symlink. If `locator.json` exists, it must be a regular file and must not itself be a
symlink. Inspect these entries without following symlinks. A non-directory or symlinked
`.surf` entry, or a non-regular or symlinked `locator.json`, has the wrong filesystem
shape: stay read-only and ask for direction. Do not treat it as absent, follow it, search
elsewhere or replace it.

A locator is stale when its exact target is missing or no longer validates as one coherent
practice. A locator or target that the client cannot read is inaccessible.

Handle outcomes without ambiguity:

| Outcome | Behaviour |
| --- | --- |
| Valid launch-directory practice | Use it; do not read the locator. |
| Locator absent | Offer the existing person-approved bounded discovery or first setup. |
| Locator valid and target valid | Use the target after read-only marker, map and framework validation. |
| Locator malformed | Stay read-only, describe the problem and ask for direction; no search. |
| Locator stale | Stay read-only, describe the missing or invalid target and ask for direction; no search. |
| Locator duplicated | Stay read-only, describe the duplicate keys and ask for direction; no search. |
| Locator unsupported | Stay read-only, describe the unknown schema version and ask for direction; no search. |
| Locator has the wrong filesystem shape | Stay read-only, describe the non-directory or symlinked `.surf` entry or the non-regular or symlinked `locator.json` and ask for direction; no search or write. |
| Locator inaccessible | Stay read-only, describe the denied locator or target and ask for direction; no search. |

A suitable practice home is normally:

- durable and controlled by the person;
- likely to remain reachable in later sessions;
- dedicated to the learning practice rather than generated or temporary work;
- compatible with the person's intended privacy, backup, synchronisation and sharing;
- normally visible in their ordinary file browser without enabling hidden-file
  visibility; and
- understandable enough that the person can find and inspect its records themselves.

When proposing a home, offer a small number of exact choices with material uncertainties
visible. Prefer a suitable existing notes or documents location, then the platform's
visible Documents folder, then a clearly named visible folder directly under the person's
home. These are defaults rather than a fixed path: account for sandbox access, durability,
backup, synchronisation, workplace administration, sharing, source control and the
person's existing organisation. Do not default to a dot-prefixed, configuration, cache,
temporary, generated or application-support directory. If a hidden home is appropriate,
say that it is hidden before the person confirms it.

Name the exact proposed `surf_home` and canonical locator path together, and explain that
confirming the proposal authorises both writes. The hidden canonical locator is a small
operational pointer, not the learning record or a default home for it. Prefer an existing
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

Retrieving Surf guidance does not require copying the person's locator or practice files
into Surf MCP calls. Keep the locator path and local practice content out of guidance
retrieval. Never claim that local material was stored, deleted, encrypted or unseen unless
the available evidence supports that statement.

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

## Create, replace, move and remove the locator safely

Create or update the locator only after the person has confirmed the exact practice home
and that practice passes marker, map and working-framework validation. Confirmation of a
setup proposal naming both paths covers both the practice and locator writes. A later move
requires a new confirmation naming the validated destination and locator update.

Before writing, inspect the immediate `.surf` entry and exact `locator.json` entry without
following symlinks. If `.surf` is absent, create it as a real directory; if it exists, it
must already be a real directory and not a symlink. If `locator.json` exists, it must be a
regular file and not a symlink. A wrong-shape entry fails closed under the table above. If
the locator is already valid and names the confirmed home, leave it unchanged: repeated
setup is idempotent. If it is valid but names another practice, show the difference and
update it only as part of a confirmed setup or move. Never silently overwrite an invalid
locator.

Use the client's safest supported replacement: create a new regular sibling temporary file
without following or reusing an existing entry, write the complete UTF-8 JSON, verify the
bytes and parsed value, then atomically replace `locator.json` without exposing a partial
file. Restrict permissions where the client and platform support that, while avoiding
stronger privacy claims than were verified. After replacement, read the canonical locator
back, validate it again and validate its exact target. Remove a leftover temporary file if
replacement fails. If safe replacement is not available, explain the limitation and do
not claim that continuity was established.

The locator is operational continuity state, not learning content:

- **Inspect:** the person can open the canonical JSON file with ordinary tools and compare
  `surf_home` with the practice's working-framework record.
- **Move:** validate and confirm the new home before replacing the locator. Updating the
  pointer does not move or delete either directory by itself.
- **Delete:** deleting only the locator restores the no-global-discovery state and leaves
  the practice untouched. Deleting a practice does not remove its locator; remove or
  redirect the locator as a separate confirmed action so it does not become stale.
- **Back up:** back up the practice according to the person's choices. The locator can be
  recreated after restoring and validating the practice; restoring the pointer alone does
  not restore learning state.

If the locator write or read-back fails after practice setup, say exactly that the local
practice exists but cross-directory continuity is incomplete. Do not present setup as
fully complete and do not fall back to a broad search.
