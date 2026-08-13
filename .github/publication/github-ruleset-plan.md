# Private-repository safeguard plan

This file records the settings to apply and verify in phase 2, after the empty
private `withnative/surf` repository exists. It is a plan, not evidence that a
GitHub setting is active. Local tooling must never claim that it configured a
remote repository.

## Verified owner state

`@richardcrng` was verified on 2026-08-13 as a `withnative` organization member
with write/admin access to the private predecessor. It is therefore the only
owner currently named in `CODEOWNERS`. `@nbogie` was verified as an organization
member but has read-only repository access, so it is deliberately not named as
a code owner.

Before rules require independent human approval, grant a real second reviewer
write access and add that verified person or team to `CODEOWNERS`. Agent review
and an authorized admin merge can support the pre-publication implementation
workflow, but must not be represented as independent human CODEOWNERS approval.

## Repository ruleset

Create rulesets targeting the default branch, every public branch, and all
tags, active rather than evaluate-only, with repository administrators
included. Verify the exact new-branch behavior with a safe canary rather than
assuming a required check can run before the branch exists. Configure them to:

- block deletion and non-fast-forward updates to `main`;
- require pull requests and dismiss stale approvals when the diff changes;
- require approval from a code owner for protected-file changes after an
  eligible independent owner exists;
- require conversation resolution;
- require the exact status checks `ci`, `dependency licences`, `source
  provenance`, and `publication guard / introduced objects and refs`;
- require branches to be current before merge;
- block force pushes, branch/tag creation that bypasses checks, and tag updates;
- allow bypass only to the smallest named administrator set, using pull
  requests except for a documented incident; and
- restrict direct creation/update/deletion of public refs to maintainers.

Enable GitHub secret scanning, push protection, private vulnerability reporting,
and dependency/security alerts. Test each setting with a safe synthetic branch
or token canary and record dated evidence outside the candidate tree. Never use
a real credential as a test value.

Protected paths are `.github/CODEOWNERS`, `.github/publication/**`,
`.github/scripts/**`, `.github/workflows/**`, `.githooks/**`, `SECURITY.md`,
the dependency lockfile, and build/release definitions. Confirm that a change to
each category requests the expected owner and cannot merge without the required
checks.

## Visibility checkpoint

Before making the repository public, verify signed in that there is one approved
root history, only `main`, no tags or hidden replacement mechanisms, all rules
above are active, push protection rejects a synthetic canary, the private
security-reporting URL works, and an administrator bypass is visible in the
audit trail. Stop for Richard's explicit approval before changing visibility.
