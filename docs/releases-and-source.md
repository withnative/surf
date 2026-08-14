# Working framework and source

Surf currently has one freely revisable, pre-production working framework: **0.1.0**.
Separately, every deployed Surf build identifies the public source revision that produced
it. The first policy keeps early framework development lightweight; the second makes the
running network service inspectable.

The launch identities are:

- **Surf application version:** `0.1.0`
- **Working framework version:** `0.1.0`
- **Plugin package version:** `0.1.0`

The numbers match intentionally for this launch. These remain independent artifacts with
independent future release triggers; matching now does not establish a permanent lockstep
version policy.

The current plugin package is `0.1.2`; the Surf application and working framework remain
`0.1.0`. The locator and `next-step` activation releases use those independent package
triggers without changing the application or framework version.

The stable product-document slug for this page remains `releases-and-source`.

## The working framework

The framework is the operating guidance returned by `quickstart`, `get_guide`, and
`get_reference`. While nobody depends on it in production, Native improves the single
working version `0.1.0` directly.

That means Surf does not currently maintain:

- a public catalogue of historical framework drafts;
- installed, available, or acknowledged framework state;
- framework migration targets or migration flows;
- exact-version framework retrieval; or
- compatibility promises between successive `0.1.0` drafts.

The `0.1.0` stamp provides simple provenance for a local practice. It is not a claim that
the current bytes are immutable. Git history and Native's workspace decisions are the
development archive.

Strict semantic versioning begins when real production use creates a compatibility
obligation. At that point Native can define immutable releases, retention, migrations,
and support policy around evidence from actual dependent practices instead of simulating
those obligations during product development.

## Surf application builds

The Rust application has its own package version for build and deployment identity. A
hosted build reports:

- the Surf application version;
- the working framework version;
- the full Git commit SHA;
- a canonical URL for that exact public commit; and
- the build date where it is useful and reproducible.

The running service exposes this metadata in its landing-page footer, MCP initialization
metadata or instructions, `surf://source`, and `https://surf.withnative.ai/source`. The
source URL must resolve to the running revision, not merely to the repository homepage.

Production provenance is an explicit build input. `SURF_GIT_SHA` must be a full lowercase
40-character commit and `SURF_SOURCE_URL` must be the matching
`https://github.com/withnative/surf/commit/{sha}` URL. The build does not inspect `.git`
or derive a public URL from the repository that happens to be checked out. Ordinary local
and source-archive builds therefore expose a visible unavailable result instead of a
potentially false source offer. `/source` redirects with HTTP 307 only when the pair has
been verified; otherwise it returns HTTP 503 with the unavailable explanation.

For the canonical hosted deployment, Railway supplies `RAILWAY_GIT_COMMIT_SHA` from the
GitHub trigger and the Docker build derives the canonical URL from it. This removes a
mutable operator-supplied pair from the normal path while retaining the explicit
`SURF_GIT_SHA` and `SURF_SOURCE_URL` path for tests and deliberate exact-source builds.
See the [production deployment and rollback runbook](production-deployment.md).

The exact commit is immutable as a source revision even while the pre-production
framework evolves in later commits. Source identity therefore does not imply historical
framework support.

## Deployment evidence

Before deployment is declared complete, verify that:

1. the public commit contains the source and framework bytes used by the build;
2. the deployed metadata reports that full commit SHA;
3. `/source` and `surf://source` resolve to the same exact revision;
4. MCP initialization and the landing footer show consistent build information; and
5. the four tools and mirrored MCP resources return the catalogue compiled into that
   build.

## Forks and self-hosted deployments

The repository can be built, run, and forked, but the official managed endpoint is the
supported product. A fork does not automatically receive Native's deployments or
framework updates. Its operator owns build cadence, source disclosure, infrastructure,
compatibility testing, and support. Modified network services must follow the repository's
AGPL-3.0-only licence; consult qualified advice for legal questions about a specific
deployment.
