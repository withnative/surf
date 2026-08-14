#!/usr/bin/env python3
"""Fail-closed inventory, export, and readiness checks for Surf's public tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = PurePosixPath(".github/publication/public-files.txt")

# These are deliberately assembled so the readiness scanner does not flag its
# own source while still rejecting the exact marker in candidate content.
PUBLICATION_MARKERS = (
    "EDITORIAL " + "LAUNCH GATE",
    "PUBLICATION " + "BLOCKER",
    "not approved for " + "publication",
)
INTERNAL_LITERALS = (
    "/" + "Users/",
    "native-" + "learn-" + "worktrees",
    "docs/" + "dogfood",
    "docs/" + "evals",
    "n8v" + ".to/",
    "native-" + "learn",
    "Native " + "workspace",
    "dogfood" + "able",
)
BLOCKED_PREFIXES = (
    ".claude/",
    ".codex-tmp/",
    "docs/" + "dogfood/",
    "docs/" + "evals/",
    "target/",
)
BLOCKED_COMPONENTS = {"__pycache__", ".git"}
BLOCKED_SUFFIXES = {".log", ".pyc", ".swp", ".swo"}
SECRET_PATTERNS = (
    ("GitHub token", re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})")),
    ("OpenAI-style secret", re.compile(r"sk-[A-Za-z0-9_-]{20,}")),
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Slack token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}")),
    ("private key", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----")),
    (
        "account-specific identifier",
        re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b"),
    ),
)
NATIVE_RECORD_MENTION = re.compile(r"\[\[[0-9a-f]{7,8}\]\]")

# The push-guard test suite needs two adversarial values in its source so it can
# prove that they are rejected before a public receiver changes. Production
# verification also needs two non-secret Railway routing identifiers in its
# trusted workflow, tests, and operator runbook. Keep every exception exact and
# path-scoped. The operational identifiers are optional so historical commits
# from before deployment verification still scan, but duplication or use in any
# other path remains a readiness failure.
PUSH_GUARD_TEST = ".github/scripts/test_" + "public_push_guard.py"
RAILWAY_PROJECT_ID = "f4d995a4" + "-2c51-4860-8817-60f141b75b0c"
RAILWAY_SERVICE_ID = "f73c4cbb" + "-99a7-4716-a4a3-19bc91ca261a"
RAILWAY_ID_PATHS = (
    ".github/scripts/test_deployment_verification.py",
    ".github/workflows/verify-production-deployment.yml",
    "docs/production-deployment.md",
)
APPROVED_READINESS_FIXTURES = (
    (PUSH_GUARD_TEST, "internal literal", "docs/" + "evals", 1),
    (
        PUSH_GUARD_TEST,
        "account-specific identifier",
        "123e4567" + "-e89b-12d3-a456-426614174000",
        1,
    ),
)
APPROVED_OPTIONAL_READINESS_VALUES = tuple(
    (path, "account-specific identifier", identifier, 1)
    for path in RAILWAY_ID_PATHS
    for identifier in (RAILWAY_PROJECT_ID, RAILWAY_SERVICE_ID)
)


class BoundaryError(Exception):
    pass


@dataclass(frozen=True)
class Candidate:
    root: Path
    paths: tuple[str, ...]
    source: str
    modes: tuple[tuple[str, str], ...] = ()
    temporary_root: Path | None = None

    def cleanup(self) -> None:
        if self.temporary_root is not None:
            shutil.rmtree(self.temporary_root, ignore_errors=True)


def run_git(root: Path, *args: str, text: bool = False) -> bytes | str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=text,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() if text else result.stderr.decode("utf-8", errors="replace").strip()
        raise BoundaryError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def normalize_manifest(text: str) -> tuple[str, ...]:
    paths = [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    if not paths:
        raise BoundaryError("public-files manifest is empty")
    if paths != sorted(paths):
        raise BoundaryError("public-files manifest must be sorted")
    if len(paths) != len(set(paths)):
        raise BoundaryError("public-files manifest contains duplicate paths")
    validate_safe_paths(paths, "manifest")
    for raw in paths:
        path = PurePosixPath(raw)
        if raw.startswith("/") or "\\" in raw or path.as_posix() != raw:
            raise BoundaryError(f"manifest path is not normalized and relative: {raw}")
        if any(part in {"", ".", ".."} for part in path.parts):
            raise BoundaryError(f"manifest path contains an unsafe component: {raw}")
    return tuple(paths)


def validate_safe_paths(paths: Iterable[str], label: str) -> None:
    casefolded: dict[str, str] = {}
    for path in paths:
        if any(ord(character) < 32 or ord(character) == 127 for character in path):
            raise BoundaryError(f"{label} path contains a control character: {path!r}")
        folded = path.casefold()
        previous = casefolded.get(folded)
        if previous is not None and previous != path:
            raise BoundaryError(f"{label} contains case-colliding paths: {previous!r}, {path!r}")
        casefolded[folded] = path


def filesystem_modes(root: Path, paths: Iterable[str]) -> tuple[tuple[str, str], ...]:
    modes: list[tuple[str, str]] = []
    for path in paths:
        file_mode = stat.S_IMODE((root / path).stat().st_mode)
        mode = "100755" if file_mode & 0o111 else "100644"
        modes.append((path, mode))
    return tuple(modes)


def validate_modes(paths: Iterable[str], modes: Iterable[tuple[str, str]]) -> tuple[tuple[str, str], ...]:
    expected = set(paths)
    mode_map = dict(modes)
    if set(mode_map) != expected:
        raise BoundaryError("file-mode inventory does not match candidate paths")
    unusual = sorted((path, mode) for path, mode in mode_map.items() if mode not in {"100644", "100755"})
    if unusual:
        rendered = ", ".join(f"{path} ({mode})" for path, mode in unusual)
        raise BoundaryError(f"candidate contains unusual Git modes: {rendered}")
    return tuple(sorted(mode_map.items()))


def worktree_inventory(root: Path) -> tuple[str, ...]:
    raw = run_git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    assert isinstance(raw, bytes)
    paths = tuple(sorted(item.decode("utf-8") for item in raw.split(b"\0") if item))
    for path in paths:
        full = root / path
        if not full.exists():
            raise BoundaryError(f"candidate path is deleted or missing: {path}")
        if full.is_symlink() or not full.is_file():
            raise BoundaryError(f"candidate path must be a regular file: {path}")
    return paths


def filesystem_inventory(root: Path) -> tuple[str, ...]:
    paths = tuple(
        sorted(
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file() or path.is_symlink()
        )
    )
    for path in paths:
        full = root / path
        if full.is_symlink():
            raise BoundaryError(f"candidate path must not be a symlink: {path}")
    return paths


def blocked_path_reason(path: str) -> str | None:
    if any(path.startswith(prefix) for prefix in BLOCKED_PREFIXES):
        return "private or generated prefix"
    pure = PurePosixPath(path)
    if any(component in BLOCKED_COMPONENTS for component in pure.parts):
        return "private or generated component"
    if pure.suffix in BLOCKED_SUFFIXES:
        return "generated or raw-output suffix"
    if pure.name == ".env" or pure.name.startswith(".env."):
        return "environment file"
    return None


def validate_inventory(manifest: Iterable[str], inventory: Iterable[str]) -> tuple[str, ...]:
    manifest_paths = tuple(manifest)
    inventory_paths = tuple(sorted(inventory))
    validate_safe_paths(manifest_paths, "manifest")
    validate_safe_paths(inventory_paths, "candidate")
    expected = set(manifest_paths)
    actual = set(inventory_paths)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing or unexpected:
        parts = []
        if missing:
            parts.append("manifest paths missing from candidate: " + ", ".join(missing))
        if unexpected:
            parts.append("unclassified candidate paths: " + ", ".join(unexpected))
        raise BoundaryError("; ".join(parts))
    blocked = [(path, blocked_path_reason(path)) for path in manifest_paths]
    blocked = [(path, reason) for path, reason in blocked if reason is not None]
    if blocked:
        rendered = ", ".join(f"{path} ({reason})" for path, reason in blocked)
        raise BoundaryError(f"public manifest contains blocked paths: {rendered}")
    if MANIFEST_PATH.as_posix() not in expected:
        raise BoundaryError(f"manifest must classify itself: {MANIFEST_PATH}")
    return tuple(sorted(manifest_paths))


def candidate_from_worktree(root: Path) -> Candidate:
    manifest_file = root / MANIFEST_PATH
    manifest = normalize_manifest(manifest_file.read_text(encoding="utf-8"))
    paths = validate_inventory(manifest, worktree_inventory(root))
    base = run_git(root, "rev-parse", "HEAD", text=True)
    assert isinstance(base, str)
    status = run_git(root, "status", "--short", text=True)
    assert isinstance(status, str)
    source = f"worktree based on {base.strip()}"
    if status.strip():
        source += " with reviewed working-tree changes"
    modes = validate_modes(paths, filesystem_modes(root, paths))
    return Candidate(root=root, paths=paths, source=source, modes=modes)


def candidate_from_filesystem(root: Path) -> Candidate:
    manifest_file = root / MANIFEST_PATH
    manifest = normalize_manifest(manifest_file.read_text(encoding="utf-8"))
    paths = validate_inventory(manifest, filesystem_inventory(root))
    modes = validate_modes(paths, filesystem_modes(root, paths))
    return Candidate(root=root, paths=paths, source=f"filesystem tree at {root}", modes=modes)


def safe_extract_archive(archive: Path, destination: Path) -> None:
    with tarfile.open(archive, mode="r:") as tar:
        members = tar.getmembers()
        for member in members:
            path = PurePosixPath(member.name)
            if member.name.startswith("/") or any(part in {"", ".", ".."} for part in path.parts):
                raise BoundaryError(f"git archive contains an unsafe path: {member.name}")
            if not member.isfile() and not member.isdir():
                raise BoundaryError(f"git archive contains a non-regular entry: {member.name}")
        tar.extractall(destination)


def candidate_from_ref(root: Path, source_ref: str) -> Candidate:
    resolved = run_git(root, "rev-parse", "--verify", f"{source_ref}^{{commit}}", text=True)
    assert isinstance(resolved, str)
    commit = resolved.strip()
    raw_tree = run_git(root, "ls-tree", "-rz", "--full-tree", commit)
    assert isinstance(raw_tree, bytes)
    tree_paths: list[str] = []
    tree_modes: list[tuple[str, str]] = []
    for record in (item for item in raw_tree.split(b"\0") if item):
        metadata, raw_path = record.split(b"\t", 1)
        mode, object_type, _object_id = metadata.decode("ascii").split()
        path = raw_path.decode("utf-8")
        if object_type != "blob":
            raise BoundaryError(f"commit contains a non-file Git object: {path} ({object_type})")
        tree_paths.append(path)
        tree_modes.append((path, mode))
    validate_safe_paths(tree_paths, "commit")
    modes = validate_modes(tree_paths, tree_modes)
    temp_root = Path(tempfile.mkdtemp(prefix="surf-public-source-"))
    archive = temp_root / "source.tar"
    checkout = temp_root / "checkout"
    checkout.mkdir()
    with archive.open("wb") as output:
        result = subprocess.run(
            ["git", "-C", str(root), "archive", "--format=tar", commit],
            check=False,
            stdout=output,
            stderr=subprocess.PIPE,
        )
    if result.returncode != 0:
        shutil.rmtree(temp_root, ignore_errors=True)
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise BoundaryError(f"git archive failed: {detail}")
    safe_extract_archive(archive, checkout)
    manifest = normalize_manifest((checkout / MANIFEST_PATH).read_text(encoding="utf-8"))
    inventory = tuple(
        sorted(path.relative_to(checkout).as_posix() for path in checkout.rglob("*") if path.is_file())
    )
    paths = validate_inventory(manifest, inventory)
    if tuple(sorted(tree_paths)) != paths:
        raise BoundaryError("git archive paths differ from the committed tree")
    return Candidate(
        root=checkout,
        paths=paths,
        source=f"commit {commit}",
        modes=modes,
        temporary_root=temp_root,
    )


def scan_publication_readiness(candidate: Candidate) -> None:
    findings: list[str] = []
    for path in candidate.paths:
        data = (candidate.root / path).read_bytes()
        if b"\0" in data:
            findings.append(f"{path}: binary or NUL-containing file requires explicit review")
            continue
        text = data.decode("utf-8", errors="replace")
        fixture_counts: dict[tuple[str, str], int] = {}
        for fixture_path, label, value, expected_count in APPROVED_READINESS_FIXTURES:
            if path != fixture_path:
                continue
            actual_count = text.count(value)
            fixture_counts[(label, value)] = expected_count if actual_count == expected_count else 0
            if actual_count != expected_count:
                findings.append(
                    f"{path}: approved {label} fixture {value!r} occurs {actual_count} times; "
                    f"expected exactly {expected_count}"
                )
        for fixture_path, label, value, maximum_count in APPROVED_OPTIONAL_READINESS_VALUES:
            if path != fixture_path:
                continue
            actual_count = text.count(value)
            if actual_count > maximum_count:
                findings.append(
                    f"{path}: approved {label} value {value!r} occurs {actual_count} times; "
                    f"expected at most {maximum_count}"
                )
            elif actual_count:
                fixture_counts[(label, value)] = actual_count
        for marker in PUBLICATION_MARKERS:
            if marker.casefold() in text.casefold():
                findings.append(f"{path}: unresolved publication marker {marker!r}")
        for literal in INTERNAL_LITERALS:
            if literal in text and fixture_counts.get(("internal literal", literal)) is None:
                findings.append(f"{path}: internal literal {literal!r}")
        if NATIVE_RECORD_MENTION.search(text):
            findings.append(f"{path}: Native record mention")
        for label, pattern in SECRET_PATTERNS:
            matches = pattern.findall(text)
            approved_values = {
                value
                for (fixture_label, value), count in fixture_counts.items()
                if fixture_label == label and count > 0
            }
            if any(match not in approved_values for match in matches):
                findings.append(f"{path}: possible {label}")
    if findings:
        raise BoundaryError("publication-readiness scan failed:\n- " + "\n- ".join(sorted(set(findings))))


def tree_digest(candidate: Candidate) -> str:
    digest = hashlib.sha256()
    mode_map = dict(candidate.modes) if candidate.modes else dict(filesystem_modes(candidate.root, candidate.paths))
    for path in candidate.paths:
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(mode_map[path].encode("ascii"))
        digest.update(b"\0")
        digest.update(hashlib.sha256((candidate.root / path).read_bytes()).digest())
    return digest.hexdigest()


def file_report(candidate: Candidate) -> list[dict[str, str | int]]:
    mode_map = dict(candidate.modes) if candidate.modes else dict(filesystem_modes(candidate.root, candidate.paths))
    return [
        {
            "path": path,
            "mode": mode_map[path],
            "bytes": (candidate.root / path).stat().st_size,
            "sha256": hashlib.sha256((candidate.root / path).read_bytes()).hexdigest(),
        }
        for path in candidate.paths
    ]


def ensure_empty_destination(destination: Path) -> None:
    if destination.exists():
        if not destination.is_dir():
            raise BoundaryError(f"export destination is not a directory: {destination}")
        if any(destination.iterdir()):
            raise BoundaryError(f"export destination is not empty: {destination}")
    else:
        destination.mkdir(parents=True)


def ensure_external_report_path(
    report: Path | None,
    candidate_root: Path,
    destination: Path | None,
) -> None:
    if report is None:
        return
    report = report.resolve()
    protected_roots = (("candidate", candidate_root.resolve()),)
    if destination is not None:
        protected_roots += (("export destination", destination.resolve()),)
    for label, root in protected_roots:
        try:
            report.relative_to(root)
        except ValueError:
            continue
        raise BoundaryError(f"report path must be outside the {label}: {report}")


def export_candidate(candidate: Candidate, destination: Path) -> None:
    ensure_empty_destination(destination)
    for path in candidate.paths:
        source = candidate.root / path
        target = destination / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        mode = stat.S_IMODE(source.stat().st_mode)
        os.chmod(target, mode)
    exported = tuple(sorted(path.relative_to(destination).as_posix() for path in destination.rglob("*") if path.is_file()))
    validate_inventory(candidate.paths, exported)
    for path in candidate.paths:
        if (candidate.root / path).read_bytes() != (destination / path).read_bytes():
            raise BoundaryError(f"exported bytes differ from source: {path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "export"))
    parser.add_argument("destination", nargs="?", type=Path)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--source-ref", help="export an exact committed tree instead of the working tree")
    parser.add_argument(
        "--filesystem-only",
        action="store_true",
        help="check an exported tree that has no Git metadata",
    )
    parser.add_argument(
        "--expect-tree-sha256",
        help="fail unless the path, mode, and content digest matches the reviewed value",
    )
    parser.add_argument(
        "--publication-ready",
        action="store_true",
        help="also reject unresolved publication markers, internal literals, and likely secrets",
    )
    parser.add_argument("--report", type=Path, help="write a machine-readable result outside the candidate tree")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "export" and args.destination is None:
        raise SystemExit("export requires an empty destination directory")
    if args.command == "check" and args.destination is not None:
        raise SystemExit("check does not accept a destination")
    if args.source_ref and args.filesystem_only:
        raise SystemExit("--source-ref and --filesystem-only are mutually exclusive")

    candidate: Candidate | None = None
    try:
        root = args.source_root.resolve()
        if args.source_ref:
            candidate = candidate_from_ref(root, args.source_ref)
        elif args.filesystem_only:
            candidate = candidate_from_filesystem(root)
        else:
            candidate = candidate_from_worktree(root)
        destination = args.destination.resolve() if args.destination else None
        report = args.report.resolve() if args.report else None
        ensure_external_report_path(report, candidate.root, destination)
        if args.publication_ready:
            scan_publication_readiness(candidate)
        digest = tree_digest(candidate)
        if args.expect_tree_sha256 and digest != args.expect_tree_sha256:
            raise BoundaryError(
                f"candidate digest {digest} does not match reviewed digest {args.expect_tree_sha256}"
            )
        if args.command == "export":
            assert destination is not None
            export_candidate(candidate, destination)
        result = {
            "command": args.command,
            "source": candidate.source,
            "file_count": len(candidate.paths),
            "tree_sha256": digest,
            "publication_ready_scanned": args.publication_ready,
            "destination": str(destination) if destination else None,
            "files": file_report(candidate),
        }
        rendered = json.dumps(result, indent=2, sort_keys=True)
        print(rendered)
        if report:
            report.write_text(rendered + "\n", encoding="utf-8")
        return 0
    except (BoundaryError, OSError, UnicodeError) as error:
        print(f"publication boundary check failed: {error}", file=sys.stderr)
        return 1
    finally:
        if candidate is not None:
            candidate.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
