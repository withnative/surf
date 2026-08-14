#!/usr/bin/env python3
"""Focused negative tests for the fail-closed Surf publication boundary."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from check_publication_boundary import (
    BoundaryError,
    Candidate,
    ensure_external_report_path,
    MANIFEST_PATH,
    normalize_manifest,
    scan_publication_readiness,
    validate_modes,
    validate_safe_paths,
    validate_inventory,
)


class ManifestTests(unittest.TestCase):
    def test_rejects_unclassified_file(self) -> None:
        with self.assertRaisesRegex(BoundaryError, "unclassified candidate paths"):
            validate_inventory(
                (MANIFEST_PATH.as_posix(), "README.md"),
                (MANIFEST_PATH.as_posix(), "README.md", "private-notes.md"),
            )

    def test_rejects_missing_manifest_file(self) -> None:
        with self.assertRaisesRegex(BoundaryError, "manifest paths missing"):
            validate_inventory(
                (MANIFEST_PATH.as_posix(), "README.md"),
                (MANIFEST_PATH.as_posix(),),
            )

    def test_rejects_private_path(self) -> None:
        with self.assertRaisesRegex(BoundaryError, "blocked paths"):
            validate_inventory(
                (MANIFEST_PATH.as_posix(), "docs/" + "evals/raw.jsonl"),
                (MANIFEST_PATH.as_posix(), "docs/" + "evals/raw.jsonl"),
            )

    def test_manifest_must_be_sorted(self) -> None:
        with self.assertRaisesRegex(BoundaryError, "must be sorted"):
            normalize_manifest("README.md\n.github/publication/public-files.txt\n")

    def test_rejects_case_collision(self) -> None:
        with self.assertRaisesRegex(BoundaryError, "case-colliding"):
            validate_safe_paths(("README.md", "readme.md"), "test")

    def test_rejects_control_character(self) -> None:
        with self.assertRaisesRegex(BoundaryError, "control character"):
            validate_safe_paths(("docs/private\nnotes.md",), "test")

    def test_rejects_unusual_git_mode(self) -> None:
        with self.assertRaisesRegex(BoundaryError, "unusual Git modes"):
            validate_modes(("linked.md",), (("linked.md", "120000"),))

    def test_rejects_report_inside_export(self) -> None:
        with tempfile.TemporaryDirectory(prefix="surf-publication-report-test-") as temporary:
            root = Path(temporary)
            candidate = root / "candidate"
            destination = root / "export"
            candidate.mkdir()
            destination.mkdir()
            with self.assertRaisesRegex(BoundaryError, "outside the export destination"):
                ensure_external_report_path(
                    destination / "unclassified-report.json",
                    candidate,
                    destination,
                )

    def test_rejects_report_inside_candidate(self) -> None:
        with tempfile.TemporaryDirectory(prefix="surf-publication-report-test-") as temporary:
            candidate = Path(temporary) / "candidate"
            candidate.mkdir()
            with self.assertRaisesRegex(BoundaryError, "outside the candidate"):
                ensure_external_report_path(candidate / "report.json", candidate, None)


class ReadinessTests(unittest.TestCase):
    def candidate_with(self, files: dict[str, str]) -> tuple[Candidate, tempfile.TemporaryDirectory[str]]:
        temporary = tempfile.TemporaryDirectory(prefix="surf-publication-test-")
        root = Path(temporary.name)
        paths = tuple(sorted(files))
        for path, content in files.items():
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        return Candidate(root=root, paths=paths, source="test fixture"), temporary

    def test_rejects_publication_marker(self) -> None:
        marker = "PUBLICATION " + "BLOCKER"
        candidate, temporary = self.candidate_with({"README.md": marker})
        self.addCleanup(temporary.cleanup)
        with self.assertRaisesRegex(BoundaryError, "unresolved publication marker"):
            scan_publication_readiness(candidate)

    def test_rejects_native_record_mention(self) -> None:
        candidate, temporary = self.candidate_with({"README.md": "internal source [" + "[abcdef1]]"})
        self.addCleanup(temporary.cleanup)
        with self.assertRaisesRegex(BoundaryError, "Native record mention"):
            scan_publication_readiness(candidate)

    def test_rejects_workstation_path(self) -> None:
        candidate, temporary = self.candidate_with({"README.md": "/" + "Users/alice/project"})
        self.addCleanup(temporary.cleanup)
        with self.assertRaisesRegex(BoundaryError, "internal literal"):
            scan_publication_readiness(candidate)

    def test_rejects_private_predecessor_name(self) -> None:
        candidate, temporary = self.candidate_with(
            {"README.md": "withnative/native-" + "learn"}
        )
        self.addCleanup(temporary.cleanup)
        with self.assertRaisesRegex(BoundaryError, "internal literal"):
            scan_publication_readiness(candidate)

    def test_rejects_secret_canary(self) -> None:
        candidate, temporary = self.candidate_with(
            {"README.md": "ghp_" + "abcdefghijklmnopqrstuvwxyz123456"}
        )
        self.addCleanup(temporary.cleanup)
        with self.assertRaisesRegex(BoundaryError, "possible GitHub token"):
            scan_publication_readiness(candidate)

    def test_rejects_account_identifier_canary(self) -> None:
        candidate, temporary = self.candidate_with(
            {"README.md": "123e4567" + "-e89b-12d3-a456-426614174000"}
        )
        self.addCleanup(temporary.cleanup)
        with self.assertRaisesRegex(BoundaryError, "account-specific identifier"):
            scan_publication_readiness(candidate)

    def test_accepts_only_the_exact_cardinality_checked_push_guard_fixtures(self) -> None:
        path = ".github/scripts/test_" + "public_push_guard.py"
        blocked_path = "docs/" + "evals"
        account_identifier = "123e4567" + "-e89b-12d3-a456-426614174000"
        candidate, temporary = self.candidate_with(
            {path: f"{blocked_path}\n{account_identifier}\n"}
        )
        self.addCleanup(temporary.cleanup)
        scan_publication_readiness(candidate)

    def test_accepts_exact_railway_ids_only_in_reviewed_operational_paths(self) -> None:
        project_id = "f4d995a4" + "-2c51-4860-8817-60f141b75b0c"
        service_id = "f73c4cbb" + "-99a7-4716-a4a3-19bc91ca261a"
        content = f"{project_id}\n{service_id}\n"
        candidate, temporary = self.candidate_with(
            {
                ".github/scripts/test_deployment_verification.py": content,
                ".github/workflows/verify-production-deployment.yml": content,
                "docs/production-deployment.md": content,
            }
        )
        self.addCleanup(temporary.cleanup)
        scan_publication_readiness(candidate)

        historical, historical_temporary = self.candidate_with(
            {
                ".github/scripts/test_deployment_verification.py": "pre-verifier\n",
                ".github/workflows/verify-production-deployment.yml": "pre-verifier\n",
                "docs/production-deployment.md": "pre-verifier\n",
            }
        )
        self.addCleanup(historical_temporary.cleanup)
        scan_publication_readiness(historical)

    def test_rejects_duplicated_railway_id_in_approved_path(self) -> None:
        project_id = "f4d995a4" + "-2c51-4860-8817-60f141b75b0c"
        candidate, temporary = self.candidate_with(
            {
                ".github/workflows/verify-production-deployment.yml": (
                    f"{project_id}\n{project_id}\n"
                )
            }
        )
        self.addCleanup(temporary.cleanup)
        with self.assertRaisesRegex(BoundaryError, "expected at most 1"):
            scan_publication_readiness(candidate)

    def test_rejects_duplicate_value_in_approved_push_guard_fixture(self) -> None:
        path = ".github/scripts/test_" + "public_push_guard.py"
        blocked_path = "docs/" + "evals"
        account_identifier = "123e4567" + "-e89b-12d3-a456-426614174000"
        candidate, temporary = self.candidate_with(
            {path: f"{blocked_path}\n{blocked_path}\n{account_identifier}\n"}
        )
        self.addCleanup(temporary.cleanup)
        with self.assertRaisesRegex(BoundaryError, "expected exactly 1"):
            scan_publication_readiness(candidate)

    def test_exact_guard_fixture_values_still_fail_in_every_other_path(self) -> None:
        blocked_path = "docs/" + "evals"
        account_identifier = "123e4567" + "-e89b-12d3-a456-426614174000"
        candidate, temporary = self.candidate_with(
            {"README.md": f"{blocked_path}\n{account_identifier}\n"}
        )
        self.addCleanup(temporary.cleanup)
        with self.assertRaises(BoundaryError) as raised:
            scan_publication_readiness(candidate)
        self.assertIn("internal literal", str(raised.exception))
        self.assertIn("account-specific identifier", str(raised.exception))

    def test_rejects_nul_containing_file(self) -> None:
        candidate, temporary = self.candidate_with({"asset.bin": "safe text"})
        self.addCleanup(temporary.cleanup)
        (candidate.root / "asset.bin").write_bytes(b"prefix\0ghp_hidden_secret_canary")
        with self.assertRaisesRegex(BoundaryError, "binary or NUL-containing"):
            scan_publication_readiness(candidate)

    def test_accepts_public_copy(self) -> None:
        candidate, temporary = self.candidate_with({"README.md": "Surf is free and open source.\n"})
        self.addCleanup(temporary.cleanup)
        scan_publication_readiness(candidate)


if __name__ == "__main__":
    unittest.main()
