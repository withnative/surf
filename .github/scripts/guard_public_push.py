#!/usr/bin/env python3
"""Fail closed before any ref can introduce unreviewed objects to withnative/surf."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote_to_bytes, urlsplit

from check_publication_boundary import BoundaryError, Candidate, scan_publication_readiness


ZERO_RE = re.compile(r"^0+$")
SAFE_REF_RE = re.compile(r"^refs/(?:heads|tags)/")
SCP_GITHUB_RE = re.compile(r"^git@github\.com:(.*)$", re.IGNORECASE)


class GuardError(Exception):
    pass


def normalized_repository_path(raw_path: str) -> tuple[str, str]:
    try:
        decoded = unquote_to_bytes(raw_path).decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise GuardError("GitHub repository URL path is not valid UTF-8") from error
    if "\\" in decoded or any(ord(character) < 32 or ord(character) == 127 for character in decoded):
        raise GuardError("GitHub repository URL path contains ambiguous characters")
    parts = [part for part in decoded.split("/") if part]
    if len(parts) != 2:
        raise GuardError("GitHub repository URL does not identify exactly one owner and repository")
    owner, repository = parts
    if repository.casefold().endswith(".git"):
        repository = repository[:-4]
    if not owner or not repository or owner in {".", ".."} or repository in {".", ".."}:
        raise GuardError("GitHub repository URL has an ambiguous owner or repository")
    return owner.casefold(), repository.casefold()


def is_public_surf_url(url: str) -> bool:
    """Match supported GitHub URLs by canonical repository identity."""
    match = SCP_GITHUB_RE.fullmatch(url)
    if match:
        return normalized_repository_path(match.group(1)) == ("withnative", "surf")

    parsed = urlsplit(url)
    host = (parsed.hostname or "").casefold().rstrip(".")
    if host == "www.github.com":
        host = "github.com"
    user = (parsed.username or "").casefold()
    if parsed.query or parsed.fragment:
        if host in {"github.com", "ssh.github.com"}:
            raise GuardError("GitHub repository URL contains an ambiguous query or fragment")
        return False
    if parsed.scheme.casefold() in {"http", "https"}:
        if host != "github.com":
            return False
        default_port = 80 if parsed.scheme.casefold() == "http" else 443
        if parsed.port not in {None, default_port}:
            raise GuardError("GitHub HTTP repository URL uses an unsupported port")
    elif parsed.scheme.casefold() in {"ssh", "git+ssh", "ssh+git"}:
        supported = (host == "github.com" and parsed.port in {None, 22}) or (
            host == "ssh.github.com" and parsed.port == 443
        )
        if not supported or user != "git":
            return False
    else:
        return False
    return normalized_repository_path(parsed.path) == ("withnative", "surf")


def git(root: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise GuardError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def repository_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode:
        raise GuardError("the publication guard must run inside a Git worktree")
    return Path(result.stdout.strip()).resolve()


def object_format_length(root: Path) -> int:
    return len(git(root, "hash-object", "--stdin", input_bytes=b"").decode().strip())


def validate_object_store(root: Path) -> None:
    for variable in ("GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_REPLACE_REF_BASE"):
        if os.environ.get(variable):
            raise GuardError(f"object substitution environment is active: {variable}")
    replacements = git(root, "replace", "-l").decode().splitlines()
    if replacements:
        raise GuardError("Git replacement refs are active")
    common = Path(git(root, "rev-parse", "--git-common-dir").decode().strip())
    if not common.is_absolute():
        common = (root / common).resolve()
    for relative in ("info/grafts", "objects/info/alternates", "shallow"):
        candidate = common / relative
        if candidate.exists():
            raise GuardError(f"incomplete or substituted object mechanism is active: {relative}")
    config = subprocess.run(
        ["git", "-C", str(root), "config", "--local", "--get-regexp", r"^(extensions\.partialclone|remote\..*\.promisor)$"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if config.returncode not in {0, 1}:
        raise GuardError("could not inspect partial-clone or promisor configuration")
    if config.stdout.strip():
        raise GuardError("partial-clone or promisor object configuration is active")


def validate_oid(oid: str, length: int, *, allow_zero: bool) -> None:
    if len(oid) != length or not all(character in "0123456789abcdefABCDEF" for character in oid):
        raise GuardError(f"malformed object ID: {oid!r}")
    if ZERO_RE.fullmatch(oid):
        if allow_zero:
            return
        raise GuardError("unexpected zero object ID")


def parse_updates(lines: str, oid_length: int) -> list[tuple[str, str, str, str]]:
    updates: list[tuple[str, str, str, str]] = []
    for number, raw in enumerate(lines.splitlines(), 1):
        fields = raw.split()
        if len(fields) != 4:
            raise GuardError(f"malformed pre-push update on input line {number}")
        local_ref, local_oid, remote_ref, remote_oid = fields
        validate_oid(local_oid, oid_length, allow_zero=True)
        validate_oid(remote_oid, oid_length, allow_zero=True)
        if not SAFE_REF_RE.match(remote_ref):
            raise GuardError(f"unsupported public ref namespace: {remote_ref}")
        deleting = bool(ZERO_RE.fullmatch(local_oid))
        if deleting and local_ref != "(delete)":
            raise GuardError("zero local object ID is only valid for a deletion")
        if not deleting and not local_ref:
            raise GuardError("non-deletion update has an empty local ref")
        updates.append((local_ref, local_oid.lower(), remote_ref, remote_oid.lower()))
    return updates


def remote_tips(root: Path, remote_url: str, oid_length: int) -> dict[str, str]:
    output = git(root, "ls-remote", "--refs", remote_url).decode("utf-8", errors="strict")
    tips: dict[str, str] = {}
    for line in output.splitlines():
        fields = line.split("\t")
        if len(fields) != 2:
            raise GuardError("remote returned a malformed ref advertisement")
        oid, ref = fields
        validate_oid(oid, oid_length, allow_zero=False)
        if not ref.startswith("refs/"):
            raise GuardError("remote returned a malformed ref name")
        if ref in tips:
            raise GuardError(f"remote advertised duplicate ref: {ref}")
        tips[ref] = oid.lower()
    return tips


def introduced(root: Path, new_oids: set[str], exclusions: set[str]) -> list[str]:
    if not new_oids:
        return []
    arguments = ["rev-list", "--objects", *sorted(new_oids)]
    if exclusions:
        arguments.extend(["--not", *sorted(exclusions)])
    records = git(root, *arguments).decode("utf-8", errors="strict").splitlines()
    objects = {record.split(" ", 1)[0] for record in records if record}
    # rev-list may peel an annotated tag without reporting the tag object itself.
    objects.update(new_oids - exclusions)
    return sorted(objects)


def peel_commits(root: Path, new_oids: set[str]) -> list[str]:
    commits: set[str] = set()
    for oid in new_oids:
        try:
            peeled = git(root, "rev-parse", "--verify", f"{oid}^{{commit}}").decode().strip()
        except GuardError as error:
            raise GuardError(f"public ref tip {oid} does not peel to a commit") from error
        commits.add(peeled)
    return sorted(commits)


def scanner_binary(root: Path) -> Path:
    installer = root / ".github/scripts/install-gitleaks.sh"
    result = subprocess.run(
        [str(installer)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
    )
    if result.returncode:
        raise GuardError("pinned gitleaks is unavailable or unverifiable: " + result.stderr.strip())
    lines = result.stdout.splitlines()
    if not lines:
        raise GuardError("pinned gitleaks installer did not return a binary path")
    binary = Path(lines[-1]).resolve()
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise GuardError(f"pinned gitleaks binary is not executable: {binary}")
    version = subprocess.run([str(binary), "version"], capture_output=True, text=True, check=False)
    if version.returncode or version.stdout.strip() != "8.28.0":
        raise GuardError("pinned gitleaks binary failed its runtime version check")
    return binary


def scan_objects(root: Path, objects: list[str]) -> None:
    if not objects:
        return
    binary = scanner_binary(root)
    with tempfile.TemporaryDirectory(prefix="surf-introduced-objects-") as temporary:
        payload = Path(temporary)
        for oid in objects:
            object_type = git(root, "cat-file", "-t", oid).decode().strip()
            target = payload / f"{oid}.{object_type}"
            target.write_bytes(git(root, "cat-file", object_type, oid))
            if object_type in {"commit", "tag"}:
                try:
                    scan_publication_readiness(
                        Candidate(root=payload, paths=(target.name,), source=f"Git {object_type} {oid}")
                    )
                except BoundaryError as error:
                    raise GuardError(
                        f"publication readiness rejected introduced {object_type} metadata {oid}:\n{error}"
                    ) from error
        result = subprocess.run(
            [str(binary), "dir", "--no-banner", "--redact", "--exit-code", "1", str(payload)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode:
            detail = (result.stdout + "\n" + result.stderr).strip()
            raise GuardError("dedicated secret scan rejected introduced Git objects:\n" + detail)


def scan_commit_boundaries(root: Path, commits: list[str]) -> None:
    checker = root / ".github/scripts/check_publication_boundary.py"
    for commit in commits:
        result = subprocess.run(
            [sys.executable, str(checker), "check", "--source-root", str(root), "--source-ref", commit, "--publication-ready"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode:
            raise GuardError(f"publication boundary rejected introduced commit {commit}:\n{result.stderr.strip()}")


def guard(root: Path, new_oids: set[str], exclusions: set[str]) -> None:
    objects = introduced(root, new_oids, exclusions)
    commits = set(peel_commits(root, new_oids))
    commits.update(oid for oid in objects if git(root, "cat-file", "-t", oid).strip() == b"commit")
    scan_objects(root, objects)
    scan_commit_boundaries(root, sorted(commits))
    print(f"Surf publication guard accepted {len(commits)} ref tip(s) and {len(objects)} introduced object(s).")


def pre_push(remote_name: str, remote_url: str) -> None:
    # This can only add a guarded destination; it cannot disable protection for
    # withnative/surf. It exists so tests can prove a rejected hook leaves a
    # local synthetic receiver unchanged.
    test_target = os.environ.get("SURF_PUBLICATION_TEST_TARGET_URL")
    def is_target(url: str) -> bool:
        return is_public_surf_url(url) or bool(test_target and url == test_target)
    configured = subprocess.run(
        ["git", "remote", "get-url", "--push", "--all", remote_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    push_urls = configured.stdout.splitlines() if configured.returncode == 0 else []
    targets_public = is_target(remote_url) or any(is_target(url) for url in push_urls)
    if not targets_public:
        return
    if len(push_urls) > 1:
        raise GuardError(f"remote {remote_name!r} has multiple push URLs; public destination is ambiguous")
    root = repository_root()
    validate_object_store(root)
    oid_length = object_format_length(root)
    raw_updates = sys.stdin.buffer.read()
    try:
        update_text = raw_updates.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise GuardError("pre-push update protocol is not valid UTF-8") from error
    updates = parse_updates(update_text, oid_length)
    new_oids = {local_oid for _, local_oid, _, _ in updates if not ZERO_RE.fullmatch(local_oid)}
    for oid in new_oids:
        git(root, "cat-file", "-e", f"{oid}^{{object}}")
    advertised = remote_tips(root, remote_url, oid_length)
    zero = "0" * oid_length
    for _, _, remote_ref, remote_oid in updates:
        if remote_oid != advertised.get(remote_ref, zero):
            raise GuardError(f"pre-push old object ID disagrees with the advertised value for {remote_ref}")
    guard(root, new_oids, set(advertised.values()))


def ci_range(new_oid: str, exclusions: list[str]) -> None:
    root = repository_root()
    validate_object_store(root)
    length = object_format_length(root)
    validate_oid(new_oid, length, allow_zero=False)
    for oid in exclusions:
        validate_oid(oid, length, allow_zero=False)
    guard(root, {new_oid.lower()}, {oid.lower() for oid in exclusions})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    hook = subparsers.add_parser("pre-push")
    hook.add_argument("remote_name")
    hook.add_argument("remote_url")
    ci = subparsers.add_parser("ci-range")
    ci.add_argument("new_oid")
    ci.add_argument("exclude_oid", nargs="*")
    args = parser.parse_args()
    try:
        if args.command == "pre-push":
            pre_push(args.remote_name, args.remote_url)
        else:
            ci_range(args.new_oid, args.exclude_oid)
        return 0
    except (GuardError, OSError, UnicodeError) as error:
        print(f"Surf publication guard blocked the push: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
