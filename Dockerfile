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

# Production builds pass an exact, mutually verified pair. Omitting every value
# deliberately produces a local image whose `/source` endpoint says unavailable;
# providing only one value or a mismatched URL fails the build.
ARG SURF_GIT_SHA
ARG SURF_SOURCE_URL
ARG SURF_BUILD_DATE
RUN if [ -z "$SURF_GIT_SHA" ] && [ -z "$SURF_SOURCE_URL" ] && [ -z "$SURF_BUILD_DATE" ]; then \
      env -u SURF_GIT_SHA -u SURF_SOURCE_URL -u SURF_BUILD_DATE cargo build --release --locked; \
    else \
      test -n "$SURF_GIT_SHA" && test -n "$SURF_SOURCE_URL" && \
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
