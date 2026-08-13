#!/bin/sh
set -eu

repo=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
scratch=$(mktemp -d "${TMPDIR:-/tmp}/surf-source-builds.XXXXXX")
trap 'rm -rf "$scratch"' EXIT HUP INT TERM

sha=0123456789abcdef0123456789abcdef01234567
url="https://github.com/withnative/surf/commit/$sha"

# An ordinary checkout must compile and report unavailable, without consulting
# its private or public Git remote.
CARGO_TARGET_DIR="$scratch/ordinary-target" \
  cargo test --locked source::tests::ordinary_build_fails_closed_without_inventing_a_repository_revision
CARGO_TARGET_DIR="$scratch/ordinary-target" \
  cargo test --locked source_surfaces_and_initialize_are_consistent

# Explicit production provenance must survive all user-facing surfaces.
SURF_GIT_SHA="$sha" SURF_SOURCE_URL="$url" SURF_BUILD_DATE="2026-08-12T00:00:00Z" \
  CARGO_TARGET_DIR="$scratch/verified-target" \
  cargo test --locked source::tests::verified_instruction_names_every_required_identity
SURF_GIT_SHA="$sha" SURF_SOURCE_URL="$url" SURF_BUILD_DATE="2026-08-12T00:00:00Z" \
  CARGO_TARGET_DIR="$scratch/verified-target" \
  cargo test --locked source_surfaces_and_initialize_are_consistent

# A partial pair and a plausible-looking URL for the wrong revision must stop
# compilation rather than publish a misleading source offer.
if SURF_GIT_SHA="$sha" CARGO_TARGET_DIR="$scratch/invalid-target" \
  cargo check --locked >"$scratch/partial.log" 2>&1; then
  echo "partial source metadata unexpectedly compiled" >&2
  exit 1
fi
grep -q "SURF_GIT_SHA and SURF_SOURCE_URL must either both be set or both be absent" \
  "$scratch/partial.log"

if SURF_GIT_SHA="$sha" \
  SURF_SOURCE_URL="https://github.com/withnative/surf/commit/ffffffffffffffffffffffffffffffffffffffff" \
  CARGO_TARGET_DIR="$scratch/invalid-target" cargo check --locked >"$scratch/mismatch.log" 2>&1; then
  echo "mismatched source metadata unexpectedly compiled" >&2
  exit 1
fi
grep -q "SURF_SOURCE_URL must be the exact public Surf commit URL" "$scratch/mismatch.log"

# A Git source archive contains no repository metadata. It must behave exactly
# like an ordinary local build, proving build.rs does not inspect `.git`.
mkdir "$scratch/archive"
git -C "$repo" archive HEAD | tar -x -C "$scratch/archive"
(
  cd "$scratch/archive"
  test ! -e .git
  CARGO_TARGET_DIR="$scratch/archive-target" \
    cargo test --locked source::tests::ordinary_build_fails_closed_without_inventing_a_repository_revision
  CARGO_TARGET_DIR="$scratch/archive-target" \
    cargo test --locked source_surfaces_and_initialize_are_consistent
)
