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
   and ref `main`.
7. [Verify production deployment](../.github/workflows/verify-production-deployment.yml)
   validates the event before using its values, proves the full SHA belongs to `main`,
   and verifies the exact source, MCP catalogue, compiled landing bytes, and legacy-host
   health. A deep-check failure is visible as a failed GitHub Actions run even though the
   platform health gate has completed.

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

The automatic verifier checks:

- `surf.withnative.ai/health` returns HTTP 200 and `ok`;
- `/source`, `surf://source`, and MCP initialization name the deployed full SHA and exact
  public commit URL;
- `tools/list` returns Surf's four expected tools;
- `resources/list` contains the complete working-framework and source catalogue;
- landing HTML and CSS are byte-for-byte identical to the deployed commit; and
- the two legacy hostnames still return a healthy response.

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
   SHA. From a current checkout of `main`, with the rollback commit checked out separately
   at `ROLLBACK_SOURCE`, the operator may run:

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
