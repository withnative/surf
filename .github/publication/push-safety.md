# Public and private Git workflow

The private predecessor is a preparation workspace. It must never gain a remote
whose URL is, aliases, or pushes to `withnative/surf`. The public repository is
an independent history created only by the separately authorized publication
task. Do not add the private predecessor as an upstream, mirror, alternate, or
object source.

## Install and verify the local guard

Run this once in every clone of the public repository:

```console
.github/scripts/install-publication-hooks.sh
test "$(git config --local core.hooksPath)" = .githooks
python3 .github/scripts/test_public_push_guard.py
```

The hook activates only when Git identifies the destination as the GitHub
repository `withnative/surf`, parsing supported HTTP(S), SSH, `git+ssh`,
`ssh+git`, SCP-style SSH, and GitHub SSH-over-443 URLs by their decoded,
case-insensitive owner/repository identity. Harmless GitHub aliases such as
userinfo, the default port, repeated or trailing slashes, and an optional
`.git` suffix normalize to that identity; an ambiguous GitHub-host URL fails
closed. A remote merely named `surf`, a local path, or a private-lab/lookalike
URL containing those words does not match. Before Git updates a ref, the guard
reads every proposed update, obtains the target's
current refs, computes the objects newly reachable through all proposed branch
and tag updates, and scans those objects with checksum-pinned gitleaks. It also
runs the strict public manifest and publication-readiness check on every newly
introduced commit tree. Deletions introduce no content. Unsupported ref
namespaces, malformed input, an inconsistent remote advertisement, and a
missing or unverifiable scanner all stop the push.

An arbitrary personal SSH-config hostname cannot be resolved to a GitHub
repository identity from the hook arguments alone. Maintainers must use a
documented GitHub URL form for the public remote; setup and phase-2 verification
must reject an opaque host alias rather than claiming it is guarded.

Normal work uses a feature branch and pull request. Never bypass the hook with
`--no-verify`. Local hooks are advisory because a user can disable them; the
public repository's `publication guard / introduced objects and refs` check
repeats the same object and tree checks from the pull-request base in CI. Branch
protection must require that check before merge. GitHub Actions cannot retract a
leak after a feature-branch push, so it is not a substitute for the hook at that
boundary. Public feature branches are permitted only when every commit and
object is already safe to publish before its first push.

Tags are immutable release pointers. Create and push a tag only after the exact
commit is public, reviewed, green, and approved for release. Never force a tag.
Do not use `--mirror`, `--all`, `--tags`, broad wildcard refspecs, or a force push
to the public remote. The guard understands force pushes and multiple updates,
but understanding them is not authorization to use them.

## Before every public push

Review `git remote -v`, the explicit refspec, and `git log --stat` for every
commit being introduced. Run the full CI suite and the publication-ready check
against the exact commit. Push one named branch or tag. Confirm the resulting
GitHub ref and CI result signed out when the change affects publication or
release integrity.
