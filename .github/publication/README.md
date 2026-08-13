# Public repository boundary

Surf will be published from a single reviewed, history-free root commit in the
independent `withnative/surf` repository. The public repository becomes the
canonical source of truth from that commit onward. The private predecessor
remains an archive; it is not a fork, upstream, mirror, or release source.

`public-files.txt` is the exact path allowlist. The boundary check fails closed:
every candidate file must be listed, every listed file must exist, and private,
generated, unusual, or unreviewed paths are rejected. A publication candidate
must be an exact commit, not a mutable checkout.

## Prepare the reviewed candidate

1. Resolve all `--publication-ready` findings and the editorial decisions below.
2. Run CI and the publication boundary tests on the private candidate branch.
3. Commit the reviewed candidate, record its commit and tree IDs, and generate a
   JSON boundary report from that exact commit.
4. Have a second person review the file manifest, per-file digests and modes,
   publication-readiness result, secret-scanner result, build/test evidence, and
   the final author identity.
5. Export only from the pinned commit, supplying the reviewed tree digest with
   `--expect-tree-sha256`. Never copy a checkout or push predecessor refs.

Example, with an empty destination outside the private repository:

```console
python3 .github/scripts/check_publication_boundary.py check \
  --source-ref "$REVIEWED_PRIVATE_COMMIT" \
  --publication-ready \
  --report /tmp/surf-publication-report.json

python3 .github/scripts/check_publication_boundary.py export /tmp/surf-public-root \
  --source-ref "$REVIEWED_PRIVATE_COMMIT" \
  --publication-ready \
  --expect-tree-sha256 "$REVIEWED_TREE_SHA256"
```

The exported tree must then pass the full CI suite in a clean environment,
including formatting, locked builds and tests, plugin-package validation,
licence policy, Markdown links, container builds, and a dedicated secret scan.
Install and understand the tracked local push guard before adding the public
remote; see [`push-safety.md`](push-safety.md). Apply and test the GitHub
settings in [`github-ruleset-plan.md`](github-ruleset-plan.md) while the new
repository is private.

## Reviewed public-tree dispositions

The allowlist classifies files as public source; it does not approve prose by
itself. The initial public candidate applies these explicit dispositions:

- retain the dated CLI acceptance evidence as bounded public compatibility
  evidence;
- exclude the private plugin implementation audit from the history-free root;
- use public development language in the framework changelog;
- exclude the unreferenced landing-page prompt;
- keep plugin availability wording timeless and gate claims on dated acceptance
  evidence; and
- include the approved canonical Why Surf essay without its private verification
  and editorial notes.

Security reporting, copyright ownership, and publication copy are separately
approved launch inputs. Future allowlist changes still require explicit review.

## Create the public repository

Create `withnative/surf` as an empty independent private repository. Initialise
the exported tree as exactly one root commit using the approved public author
identity. Before any visibility change, verify that it has one root commit, no
other branches or tags, no replace refs, grafts or alternates, and only the Surf
remote. Push only `HEAD:refs/heads/main`; never use mirror, all-branch, or tag
pushes.

After the repository becomes public, inspect it signed out, enumerate every
public ref, and repeat the boundary, secret, build, plugin, licence and source
checks against what GitHub serves. Production releases must identify and build
the exact public Surf commit.

If anything sensitive is suspected after a push, follow
[`docs/security-incident-response.md`](../../docs/security-incident-response.md)
immediately. Rotation and containment come before history cleanup.
