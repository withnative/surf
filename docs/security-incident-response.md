# Public-source incident response

This runbook covers suspected credentials, confidential material, personal
data, or private predecessor history exposed through a public Surf ref. It does
not replace the private vulnerability-reporting route in `SECURITY.md`.

## Contain first

1. Treat the material as compromised. Revoke or rotate credentials at their
   issuing system immediately; rewriting Git history is not revocation.
2. Pause releases, deployments, merges, Actions that can publish artifacts, and
   further public pushes. Preserve relevant audit logs and exact object IDs in a
   private incident record.
3. Tell the repository administrator and the owner of the affected system over
   a private channel. Do not paste the material into an issue, pull request,
   chat, CI log, or new evidence file.
4. Determine every public branch, tag, pull-request ref, release asset, Actions
   artifact, package, cache, fork, deployment, and service response that may
   contain or identify the object.

## Remove and verify

Use GitHub Support's current sensitive-data-removal process when an object must
be purged. Coordinate any exceptional history rewrite with the administrator;
do not improvise a mirror force-push. Remove affected releases and artifacts,
invalidate caches where possible, and replace deployments from a known-good
public commit. Assume clones and forks cannot be recalled.

From a signed-out session, enumerate every served ref and scan the exact objects
GitHub exposes. Confirm revoked credentials no longer work and the replacement
credential has the narrowest necessary scope. Restore publication only after
the incident owner records containment, exposure scope, remediation, residual
risk, and explicit approval.

## Learn without re-exposing

Record a sanitized timeline and root cause privately. Update the publication
manifest, readiness rules, dedicated scanner configuration, tests, GitHub
rulesets, or human checklist as appropriate. Canary tests must always use
synthetic nonfunctional values assembled so scanners test the candidate rather
than flagging their own source.
