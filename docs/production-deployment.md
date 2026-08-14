# Production deployment and rollback

Surf's canonical production path is continuous deployment from the protected `main`
branch of `withnative/surf`. A reviewed merge is the production approval. Do not repeat
the historical local archive upload as a routine release process, and do not add a
GitHub-held Railway deployment token while the repository integration can perform the
deployment.

This runbook covers the repository-owned controls and the settings an authorised
operator must maintain in GitHub and Railway. It contains no credentials.

## Canonical deployment flow

1. A pull request passes CI, dependency-licence, source-provenance, and publication-guard
   checks and receives its required review.
2. The pull request is merged to protected `main`.
3. Railway's GitHub integration observes the commit and waits for all GitHub check suites
   for that commit to succeed. If a check fails, Railway must skip the deployment.
4. Railway builds the root `Dockerfile`. Its GitHub-provided
   `RAILWAY_GIT_COMMIT_SHA` is compiled as both the full source SHA and
   `https://github.com/withnative/surf/commit/{sha}`. A production build without exact
   provenance fails closed.
5. The committed [`railway.toml`](../railway.toml) overrides the Railway dashboard's
   builder, Dockerfile path, `/health` path, and 60-second health-check timeout. Railway
   must receive HTTP 200 before making the new deployment active; a failed health check
   leaves the prior healthy deployment active.
6. Railway publishes a successful GitHub deployment status for environment `production`
   and ref `main` (or an empty ref for a SHA-addressed deployment).
7. [Verify production deployment](../.github/workflows/verify-production-deployment.yml)
   validates the event before using its values, proves the full SHA belongs to `main`,
   and verifies the exact source, MCP catalogue, compiled landing bytes, and legacy-host
   health. A deep-check failure is visible as a failed GitHub Actions run even though the
   platform health gate has completed.

The event gate accepts only GitHub App installation `122756225`, the installation of the
Railway app (`railway-app`, app ID `73253`) on `withnative`. It also requires Railway
service `f73c4cbb-99a7-4716-a4a3-19bc91ca261a` and project
`f4d995a4-2c51-4860-8817-60f141b75b0c`. The validator requires the documented
`performed_via_github_app` ID and slug on both the deployment and status, the expected
top-level installation ID, and production/non-transient flags. It deliberately does not
infer app identity from an unrelated sender user ID. Confirm that GitHub Actions exposes
the installation object in Railway's first real event; if it does not, retain the failed
evidence and replace that assumption only with an equally strong documented identity.

Railway examples expose `deployment.payload.serviceId`; the validator requires it.
`payload.projectId` is accepted when present. If it is absent, the validator requires a
Railway HTTPS status URL whose `/project/{id}/service/{id}` path carries both exact IDs.
Any supplied target URL must be a safe `railway.com` or legacy `railway.app` HTTPS URL
with those IDs, and any supplied environment URL must be exactly
`https://surf.withnative.ai`. This is an explicit, tested assumption to confirm against
Railway's first real event. If Railway emits a different documented shape, keep the first
run failed, retain its event evidence, and review the validator before changing it.

The verification summary records the Git commit, GitHub deployment ID, and Railway
status URL. Use that status URL or Railway's deployment details to collect the Railway
deployment ID, image digest, build/runtime logs, and effective configuration when deeper
evidence is required.

## Required external settings

An authorised operator must confirm these settings before the first automatic rollout
and after any integration or ownership change.

### GitHub

- Protect `main`; require pull-request review and the existing CI and publication checks,
  disallow force pushes, and prevent unreviewed direct pushes.
- Allow GitHub Actions read-only repository contents for the verification workflow. The
  workflow declares no write permission and consumes no deployment secret.
- Install or retain the Railway GitHub app for `withnative/surf` with only the repository,
  checks, and deployment access required for the integration.
- Confirm the installation remains ID `122756225`; a reinstall normally changes that ID
  and must trigger a reviewed workflow update rather than silently broadening trust.

### Railway

- Connect the existing production service to `withnative/surf`, branch `main`, and use
  `/railway.toml` as its config-as-code file.
- Enable automatic deployment and **Wait for CI**.
- Keep the Railway environment name exactly `production`; the GitHub verification event
  gate deliberately rejects other names and refs.
- Keep `surf.withnative.ai`, `learn.withnative.ai`, and `agility.withnative.ai` attached
  while they share this service.
- Do not define `SURF_GIT_SHA` or `SURF_SOURCE_URL` for normal GitHub builds. Railway's
  Git variables are the source of truth, and the Docker build rejects an override.
- Retain at least one project member who can inspect deployments, logs, variables, and
  rollback actions. Keep credentials and mutable service variables in Railway, not in
  this repository.

Repository config overrides the matching build/deploy fields shown in the Railway
dashboard without rewriting those dashboard values. Domains, the GitHub connection,
autodeploy/Wait for CI, access control, environment identity, regions, and non-build
runtime variables remain Railway-managed.

## Verification and recovery

The automatic verifier checks the contract in the deployed commit's
`.github/deployment-contract.json`:

- `surf.withnative.ai/health` returns HTTP 200 and `ok`;
- `/source`, `surf://source`, and MCP initialization name the deployed full SHA and exact
  public commit URL;
- `tools/list` returns Surf's four expected tools;
- `resources/list` contains the complete working-framework and source catalogue;
- landing HTML and CSS are byte-for-byte identical to the deployed commit; and
- the two legacy hostnames still return a healthy response.

The mutable production hostname can briefly serve the previous healthy deployment after
GitHub receives Railway's success status. The verifier therefore retries the complete
contract with bounded exponential backoff (six attempts over at most 60 seconds of
backoff). A newer successful deployment cancels an older in-progress verification run.
Transient network errors and temporarily stale source or landing bytes can settle; a
real mismatch still fails after the final attempt.

If the GitHub verification fails but Railway is healthy, inspect the failing assertion
before deciding whether to fix forward or roll back. Do not treat Railway's one-time
health gate as ongoing application monitoring.

## Deterministic rollback

1. In Railway's production service, choose a named previously successful deployment.
   Record its Railway deployment ID and its exact full Git commit before acting.
2. Confirm the commit is the intended known-good public revision and that its source URL
   is still available.
3. Use **Rollback** on that specific Railway deployment. Railway restores the selected
   deployment's image and configuration. Never use **Deploy Latest Commit** or an
   ambiguous “redeploy latest” operation as rollback.
4. Wait for `/health` to pass, then re-run the same deep verification against the restored
   SHA. The current verifier loads tool, resource, protocol, and landing expectations
   from the rollback commit's `.github/deployment-contract.json`, rather than comparing
   an older deployment to the current `main` catalogue. From a current checkout of
   `main`, with the rollback commit checked out separately at `ROLLBACK_SOURCE`, run:

   ```sh
   python3 .github/scripts/verify_production_deployment.py \
     --base-url https://surf.withnative.ai \
     --expected-sha FULL_40_CHARACTER_SHA \
     --repo-root "$ROLLBACK_SOURCE" \
     --legacy-url https://learn.withnative.ai \
     --legacy-url https://agility.withnative.ai
   ```

5. Preserve the Railway deployment result and verification output with the incident or
   release evidence.

Commit `f1f914857d99594ce8590a25fb495481b778aa4e` predates the contract manifest and the
post-deployment verifier, but it is the specifically reviewed known-good production
promotion. The current verifier contains an exact-SHA compatibility contract for that
commit so it can be assessed without borrowing today's catalogue. Any other pre-manifest
commit must be checked with its own reviewed verifier/acceptance evidence or gain an
explicit reviewed compatibility contract; do not silently fall back to current-main
expectations.

Dry-run this procedure by selecting (but not confirming) a known-good deployment,
recording its ID and SHA, preparing the exact verifier command, and confirming the image
is still inside Railway's rollback retention window. If the image is no longer retained,
explicitly deploy that known-good public commit with matching exact-source provenance;
do not substitute the current head of `main`.

## Pull-request previews

Preview environments are optional and are not part of the production gate. If enabled,
use Railway's isolated, ephemeral PR environments and Railway-provided preview domains.
Do not attach production hostnames, credentials, or mutable production state. Because
the landing HTML and CSS are compiled into the Rust binary, a faithful landing preview
deploys the whole service. Watch paths may initially limit previews to
`web/landing/**`, `src/landing.rs`, and directly related build inputs.
