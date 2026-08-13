# Corresponding-source deployment checklist

This checklist is the operational control behind Surf's “source for this
running version” assurance. It is a practical deployment aid, not a legal opinion about the
scope of Corresponding Source under the AGPL.

## Repository contents

- [ ] The public commit contains the exact Rust source used for the build.
- [ ] The working framework and every landing asset compiled into the binary are
      present at the same commit.
- [ ] `Cargo.toml`, `Cargo.lock`, the container recipe, CI workflows, tests and
      scripts needed to generate and run the deployed object code are present.
- [ ] Build-time configuration that controls the compiled program is documented
      or included, excluding only secrets and generally available tools or system
      libraries after appropriate review.
- [ ] The clean public repository contains no credentials, personal data,
      private operational configuration, raw internal transcripts or local paths.

## Build identity

- [ ] The build starts from a clean, reviewed public commit.
- [ ] The full commit SHA, Surf application version, working framework and canonical source
      URL are embedded by the build.
- [ ] The source URL resolves without authentication to that commit or a release
      whose tag resolves to it.
- [ ] `cargo build --release --locked` and the documented container build work
      from the public checkout.
- [ ] Tests and `cargo deny check licenses` pass against the committed lockfile.

## Hosted-service verification

- [ ] The landing-page footer prominently exposes the exact source URL.
- [ ] MCP initialization metadata or instructions expose the same URL.
- [ ] `surf://source` and the HTTP `/source` surface resolve to the same commit.
- [ ] A check against the deployed service confirms its reported full SHA equals
      the commit used for the deployment.
- [ ] The source remains available for as long as the licence requires.

## Changes after deployment

- [ ] A code, framework or compiled-asset change is deployed as a new source-identified
      build, even while the pre-production framework keeps its `0.1.0` working label.
- [ ] The public repository is the production source of truth. Any retained
      private predecessor is historical material, not a divergent build source.
- [ ] Dependency and licence changes are reviewed and the evidence in
      [the dependency audit](dependency-licenses.md) is refreshed.
- [ ] Legal counsel reviews any disputed source-boundary judgement before a
      deployment relies on excluding that material.
