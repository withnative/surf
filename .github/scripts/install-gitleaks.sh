#!/bin/sh
set -eu

version=8.28.0
base_url="https://github.com/gitleaks/gitleaks/releases/download/v${version}"
cache_root=${XDG_CACHE_HOME:-"$HOME/.cache"}/surf-publication/gitleaks/${version}
destination="$cache_root/gitleaks"

case "$(uname -s):$(uname -m)" in
  Linux:x86_64|Linux:amd64)
    asset="gitleaks_${version}_linux_x64.tar.gz"
    expected=a65b5253807a68ac0cafa4414031fd740aeb55f54fb7e55f386acb52e6a840eb
    binary_expected=5fd1b3b0073269484d40078662e921d07427340ab9e6ed526ccd215a565b3298
    ;;
  Linux:aarch64|Linux:arm64)
    asset="gitleaks_${version}_linux_arm64.tar.gz"
    expected=eff65261156100e5d94a6b3dec313d532fddfe19ae1590bf7a2b4f2699128356
    binary_expected=3770c7ebeb625e3e96c183525ca18285a01aedef2d75a2c41ceb3e141af2e8b7
    ;;
  Darwin:arm64)
    asset="gitleaks_${version}_darwin_arm64.tar.gz"
    expected=d942f3ad147250c9edbaab3fed9e482f98d3b59ba10ae97b8d75647e3ade492c
    binary_expected=5588b5d942dffa048720f7e6e1d274283219fb5722a2c7564d22e83ba39087d7
    ;;
  Darwin:x86_64)
    asset="gitleaks_${version}_darwin_x64.tar.gz"
    expected=edf5a507008b0d2ef4959575772772770586409c1f6f74dabf19cbe7ec341ced
    binary_expected=cf09ad7a85683d90221db8324f036f23c8c29107145e1fc4a0dffbfa9e89c09a
    ;;
  *)
    echo "No pinned gitleaks ${version} build for $(uname -s) $(uname -m)." >&2
    exit 1
    ;;
esac

case "$expected" in
  *[!0-9a-f]*|'') echo "Pinned checksum is malformed." >&2; exit 1 ;;
esac
test "${#expected}" -eq 64 || { echo "Pinned checksum must contain 64 hexadecimal characters." >&2; exit 1; }

if test -x "$destination"; then
  cached=$(shasum -a 256 "$destination" | awk '{print $1}')
  if test "$cached" = "$binary_expected" && test "$("$destination" version)" = "$version"; then
    printf '%s\n' "$destination"
    exit 0
  fi
  rm -f "$destination"
fi

command -v curl >/dev/null 2>&1 || { echo "curl is required to acquire pinned gitleaks." >&2; exit 1; }
command -v tar >/dev/null 2>&1 || { echo "tar is required to acquire pinned gitleaks." >&2; exit 1; }
command -v shasum >/dev/null 2>&1 || { echo "shasum is required to verify pinned gitleaks." >&2; exit 1; }

mkdir -p "$cache_root"
archive="$cache_root/$asset"
temporary="$archive.tmp.$$"
trap 'rm -f "$temporary"' EXIT HUP INT TERM
curl --fail --location --proto '=https' --tlsv1.2 --output "$temporary" "$base_url/$asset"
actual=$(shasum -a 256 "$temporary" | awk '{print $1}')
test "$actual" = "$expected" || {
  echo "Pinned gitleaks archive checksum mismatch: expected $expected, got $actual" >&2
  exit 1
}
mv "$temporary" "$archive"
tar -xzf "$archive" -C "$cache_root" gitleaks
chmod 0755 "$destination"
binary_actual=$(shasum -a 256 "$destination" | awk '{print $1}')
test "$binary_actual" = "$binary_expected" || {
  rm -f "$destination"
  echo "Extracted gitleaks binary checksum mismatch: expected $binary_expected, got $binary_actual" >&2
  exit 1
}
test "$("$destination" version)" = "$version" || {
  echo "Acquired binary did not report pinned gitleaks version $version." >&2
  exit 1
}
printf '%s\n' "$destination"
