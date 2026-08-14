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
6. Railway publishes a successful GitHub deployment status with environment label
   `native-learn / production` and the full deployed SHA in both `sha` and `ref`.
7. [Verify production deployment](../.github/workflows/verify-production-deployment.yml)
   validates the event before using its values, proves the full SHA belongs to `main`,
   and verifies the exact source, MCP catalogue, compiled landing bytes, and legacy-host
   health. A deep-check failure is visible as a failed GitHub Actions run even though the
   platform health gate has completed.

The event gate is based on the first captured production event, rather than Railway's
generic example payload. GitHub did not expose usable installation metadata in that
event, so the validator uses the exact Railway identity that was present: repository ID
`1333433853` and `railway-app[bot]` (bot ID `68434857`, including its immutable node ID)
as sender, deployment creator, and status creator. Railway emitted
`performed_via_github_app: null`; the validator requires that reviewed value, the exact
`native-learn / production` label, a non-transient `deploy` task, and the full deployed
SHA as its ref. Railway also emitted
`production_environment: false`; that counterintuitive but observed value is pinned so
any platform shape change fails closed for review.

The captured event does not expose Railway service ID
`f73c4cbb-99a7-4716-a4a3-19bc91ca261a`. Its strongest available service boundary is the
exact `native-learn` service name embedded in the environment label, inside project
`f4d995a4-2c51-4860-8817-60f141b75b0c` and production environment
`2255334a-771c-4024-a5b8-f7760f8d0144`. The payload must contain that environment UUID,
and `target_url`, `log_url`, and `environment_url` must all be present, identical, and
equal the exact Railway HTTPS project/environment URL. The later ancestry, live `/source`,
landing-byte, and MCP checks still prove that this production hostname serves the same
protected-main SHA. If Railway changes any event field, retain the failed run as evidence
and review the new shape rather than weakening the gate speculatively.

The GitHub event cannot prove the Railway service UUID, Railway deployment UUID, image
digest, Wait-for-CI setting, or health-gate behavior by itself. Those remain deployment
configuration/evidence checks in Railway. The automatic claim is deliberately narrower:
the authenticated Railway bot reported success for this exact protected-main SHA in the
expected project/environment, and the public Surf endpoint served that exact commit and
contract.

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
- Confirm the Railway App remains installed only for the intended repositories. A
  reinstall or permission change must trigger an integration review; the event gate
  authenticates the captured Railway bot identity because the event does not expose a
  usable installation ID.

### Railway

- Connect the existing production service to `withnative/surf`, branch `main`, and use
  `/railway.toml` as its config-as-code file.
- Enable automatic deployment and **Wait for CI**.
- Keep the Railway service and environment names exactly `native-learn` and `production`;
  the event gate deliberately rejects any other combined label or non-SHA ref.
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
