#!/bin/sh
set -eu

root=$(git rev-parse --show-toplevel) || {
  echo "Run this installer inside the Surf Git worktree." >&2
  exit 1
}

hook="$root/.githooks/pre-push"
test -f "$hook" || {
  echo "Tracked pre-push hook is missing: $hook" >&2
  exit 1
}
test -x "$hook" || {
  echo "Tracked pre-push hook is not executable: $hook" >&2
  exit 1
}

existing=$(git -C "$root" config --local --get core.hooksPath || true)
if test -n "$existing" && test "$existing" != .githooks; then
  echo "Refusing to replace existing core.hooksPath=$existing; review and migrate those hooks explicitly." >&2
  exit 1
fi
git -C "$root" config --local core.hooksPath .githooks
configured=$(git -C "$root" config --local --get core.hooksPath)
test "$configured" = .githooks || {
  echo "Failed to configure the tracked hooks directory." >&2
  exit 1
}

echo "Installed Surf's tracked pre-push guard via core.hooksPath=.githooks"
