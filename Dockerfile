# Surf ships as a single binary with the framework text compiled in, so a
# deployed image is a fixed artefact — a version stamp on someone's experiment
# record refers to bytes that cannot drift underneath them.
#
# Pinned to the toolchain CI verifies against, not to `latest`.
FROM rust:1.85-slim-bookworm AS build

WORKDIR /src

# framework/ and web/ are build inputs, not runtime assets: src/framework.rs and
# src/landing.rs pull them in with include_str! at compile time.
COPY Cargo.toml Cargo.lock ./
COPY build.rs ./
COPY src ./src
COPY docs ./docs
COPY framework ./framework
COPY web ./web

# Railway's GitHub integration supplies the triggering commit and repository
# identity as build variables. The Docker build turns that commit into the only
# acceptable public source URL; operators cannot override one half of the pair.
# Explicit SURF_* inputs remain available for local tests and deliberate
# exact-source builds. An ordinary local image still reports source unavailable.
ARG RAILWAY_GIT_COMMIT_SHA
ARG RAILWAY_GIT_BRANCH
ARG RAILWAY_GIT_REPO_NAME
ARG RAILWAY_GIT_REPO_OWNER
ARG RAILWAY_ENVIRONMENT_NAME
ARG SURF_GIT_SHA
ARG SURF_SOURCE_URL
ARG SURF_BUILD_DATE
RUN set -eu; \
    if [ -n "${RAILWAY_GIT_COMMIT_SHA:-}" ]; then \
      if [ -n "${SURF_GIT_SHA:-}" ] || [ -n "${SURF_SOURCE_URL:-}" ]; then \
        echo "Railway Git provenance cannot be overridden with SURF_GIT_SHA or SURF_SOURCE_URL" >&2; \
        exit 1; \
      fi; \
      if [ "${RAILWAY_GIT_REPO_OWNER:-}" != "withnative" ] || [ "${RAILWAY_GIT_REPO_NAME:-}" != "surf" ]; then \
        echo "Railway Git builds must originate from withnative/surf" >&2; \
        exit 1; \
      fi; \
      if [ "${RAILWAY_ENVIRONMENT_NAME:-}" = "production" ] && [ "${RAILWAY_GIT_BRANCH:-}" != "main" ]; then \
        echo "Railway production Git builds must originate from main" >&2; \
        exit 1; \
      fi; \
      SURF_GIT_SHA="$RAILWAY_GIT_COMMIT_SHA" \
      SURF_SOURCE_URL="https://github.com/withnative/surf/commit/$RAILWAY_GIT_COMMIT_SHA" \
      cargo build --release --locked; \
    elif [ "${RAILWAY_ENVIRONMENT_NAME:-}" = "production" ]; then \
      if [ -z "${SURF_GIT_SHA:-}" ] || [ -z "${SURF_SOURCE_URL:-}" ]; then \
        echo "Railway production builds require Git-triggered or explicit exact-source provenance" >&2; \
        exit 1; \
      fi; \
      cargo build --release --locked; \
    elif [ -z "${SURF_GIT_SHA:-}" ] && [ -z "${SURF_SOURCE_URL:-}" ] && [ -z "${SURF_BUILD_DATE:-}" ]; then \
      env -u SURF_GIT_SHA -u SURF_SOURCE_URL -u SURF_BUILD_DATE cargo build --release --locked; \
    else \
      test -n "${SURF_GIT_SHA:-}" && test -n "${SURF_SOURCE_URL:-}"; \
      cargo build --release --locked; \
    fi


# No ca-certificates: the server makes no outbound requests. There is no
# database, no auth, no HTTP client — the dependency set in Cargo.toml is the
# whole runtime surface.
FROM debian:bookworm-slim AS runtime

RUN useradd --system --create-home --uid 10001 app

COPY --from=build /src/target/release/surf /usr/local/bin/surf

USER app
ENV PORT=8080
EXPOSE 8080

CMD ["surf"]
