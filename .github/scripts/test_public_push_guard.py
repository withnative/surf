#!/usr/bin/env python3
"""Synthetic tests for exact-ref publication push protection."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from guard_public_push import GuardError, is_public_surf_url, parse_updates, validate_object_store


HERE = Path(__file__).resolve().parent
BOUNDARY = HERE / "check_publication_boundary.py"
GUARD = HERE / "guard_public_push.py"
INSTALLER = HERE / "install-gitleaks.sh"
HOOK_INSTALLER = HERE / "install-publication-hooks.sh"
HOOK = HERE.parents[1] / ".githooks/pre-push"
WORKFLOW = HERE.parents[1] / ".github/workflows/publication-guard.yml"
BLOCKED_EVALUATION_PATH = "docs/evals/raw.txt"


def run(*args: str, cwd: Path, env: dict[str, str] | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and result.returncode:
        raise AssertionError(f"{' '.join(args)} failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")
    return result


class ParsingTests(unittest.TestCase):
    def test_accepts_branch_tag_force_multiple_deletion_and_zero_sha_forms(self) -> None:
        one = "1" * 40
        two = "2" * 40
        zero = "0" * 40
        updates = parse_updates(
            "\n".join(
                (
                    f"refs/heads/main {one} refs/heads/main {two}",
                    f"refs/tags/v1 {two} refs/tags/v1 {zero}",
                    f"(delete) {zero} refs/heads/old {one}",
                )
            ),
            40,
        )
        self.assertEqual(len(updates), 3)

    def test_rejects_unsupported_public_ref_namespace(self) -> None:
        with self.assertRaisesRegex(GuardError, "unsupported public ref namespace"):
            parse_updates(f"refs/notes/x {'1' * 40} refs/notes/x {'0' * 40}\n", 40)

    def test_rejects_impossible_local_zero(self) -> None:
        with self.assertRaisesRegex(GuardError, "only valid for a deletion"):
            parse_updates(f"refs/heads/main {'0' * 40} refs/heads/main {'1' * 40}\n", 40)

    def test_rejects_malformed_or_wrong_width_protocol(self) -> None:
        with self.assertRaisesRegex(GuardError, "malformed pre-push update"):
            parse_updates("only three fields\n", 40)
        with self.assertRaisesRegex(GuardError, "malformed object ID"):
            parse_updates(f"refs/heads/main {'1' * 39} refs/heads/main {'0' * 40}\n", 40)

    def test_only_exact_surf_urls_are_protected(self) -> None:
        for url in (
            "git@github.com:withnative/surf.git",
            "git@GitHub.com:WithNative/Surf.git",
            "https://github.com/WITHNATIVE/SURF",
            "https://github.com/withnative/surf.git/",
            "https://github.com./withnative/surf.git",
            "https://www.github.com/withnative/surf.git",
            "http://github.com:80/withnative/surf.git",
            "https://richardcrng@github.com:443//withnative/surf.git",
            "https://github.com/withnative/s%75rf.git",
            "git@github.com:/withnative//surf.git/",
            "ssh://git@github.com:22/WithNative/Surf.git",
            "git+ssh://git@github.com/withnative/surf.git",
            "ssh+git://git@github.com/withnative/surf.git",
            "ssh://git@github.com/withnative/surf.git/",
            "ssh://git@ssh.github.com:443/withnative/surf.git",
        ):
            with self.subTest(url=url):
                self.assertTrue(is_public_surf_url(url))
        for url in (
            "git@github.com:example/surf.git",
            "git@github.com:someone/surf.git",
            "https://github.example/withnative/surf.git",
            "/tmp/private-withnative/surf.git",
            "ssh://git@ssh.github.com:22/withnative/surf.git",
        ):
            with self.subTest(url=url):
                self.assertFalse(is_public_surf_url(url))
        for url in (
            "https://github.com/withnative/surf/extra",
            "https://github.com/withnative/surf.git?ambiguous=1",
            "https://github.com/withnative/%FF",
        ):
            with self.subTest(url=url):
                with self.assertRaises(GuardError):
                    is_public_surf_url(url)

    def test_publication_workflow_detects_every_branch_and_tag_push(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("branches: ['**']", workflow)
        self.assertIn("tags: ['**']", workflow)
        self.assertIn("AFTER: ${{ github.event.after }}", workflow)
        self.assertIn("REF: ${{ github.ref }}", workflow)
        self.assertIn('git rev-parse --verify "${REF}^{object}"', workflow)

    def test_annotated_tag_object_differs_from_the_event_style_peeled_commit(self) -> None:
        with tempfile.TemporaryDirectory(prefix="surf-tag-event-test-") as temporary:
            repo = Path(temporary)
            run("git", "init", str(repo), cwd=repo.parent)
            run("git", "config", "user.name", "Test", cwd=repo)
            run("git", "config", "user.email", "test@example.invalid", cwd=repo)
            run("git", "commit", "--allow-empty", "-m", "safe commit", cwd=repo)
            run("git", "tag", "-a", "v1", "-m", "annotated metadata", cwd=repo)
            tag_object = run("git", "rev-parse", "refs/tags/v1^{object}", cwd=repo).stdout.strip()
            peeled_commit = run("git", "rev-parse", "refs/tags/v1^{commit}", cwd=repo).stdout.strip()
            self.assertNotEqual(tag_object, peeled_commit)

    def test_pinned_checksums_are_full_sha256_values(self) -> None:
        text = INSTALLER.read_text(encoding="utf-8")
        checksums = [line.split("=", 1)[1].strip() for line in text.splitlines() if line.strip().startswith(("expected=", "binary_expected="))]
        checksums = [value.split()[0] for value in checksums]
        self.assertEqual(len(checksums), 8)
        self.assertTrue(all(len(value) == 64 and set(value) <= set("0123456789abcdef") for value in checksums))

    def test_hook_installer_is_idempotent_and_refuses_a_conflict(self) -> None:
        with tempfile.TemporaryDirectory(prefix="surf-hook-installer-test-") as temporary:
            repo = Path(temporary)
            run("git", "init", str(repo), cwd=repo.parent)
            (repo / ".github/scripts").mkdir(parents=True)
            (repo / ".githooks").mkdir()
            shutil.copy2(HOOK_INSTALLER, repo / ".github/scripts/install-publication-hooks.sh")
            shutil.copy2(HOOK, repo / ".githooks/pre-push")
            (repo / ".github/scripts/install-publication-hooks.sh").chmod(0o755)
            (repo / ".githooks/pre-push").chmod(0o755)
            installer = str(repo / ".github/scripts/install-publication-hooks.sh")
            run(installer, cwd=repo)
            run(installer, cwd=repo)
            self.assertEqual(run("git", "config", "--local", "--get", "core.hooksPath", cwd=repo).stdout.strip(), ".githooks")
            run("git", "config", "--local", "core.hooksPath", ".other-hooks", cwd=repo)
            conflict = run(installer, cwd=repo, check=False)
            self.assertNotEqual(conflict.returncode, 0)
            self.assertIn("Refusing to replace", conflict.stderr)

    def test_rejects_replacement_graft_alternate_and_shallow_mechanisms(self) -> None:
        for relative in ("objects/info/alternates", "info/grafts", "shallow"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory(prefix="surf-object-store-test-") as temporary:
                repo = Path(temporary)
                run("git", "init", str(repo), cwd=repo.parent)
                target = repo / ".git" / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("synthetic\n", encoding="utf-8")
                with self.assertRaisesRegex(GuardError, "incomplete or substituted"):
                    validate_object_store(repo)
        with tempfile.TemporaryDirectory(prefix="surf-replace-test-") as temporary:
            repo = Path(temporary)
            run("git", "init", str(repo), cwd=repo.parent)
            run("git", "config", "user.name", "Test", cwd=repo)
            run("git", "config", "user.email", "test@example.invalid", cwd=repo)
            (repo / "x").write_text("one", encoding="utf-8")
            run("git", "add", "x", cwd=repo)
            run("git", "commit", "-m", "one", cwd=repo)
            first = run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()
            (repo / "x").write_text("two", encoding="utf-8")
            run("git", "commit", "-am", "two", cwd=repo)
            second = run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()
            run("git", "replace", first, second, cwd=repo)
            with self.assertRaisesRegex(GuardError, "replacement refs"):
                validate_object_store(repo)

    def test_rejects_object_substitution_environment(self) -> None:
        with tempfile.TemporaryDirectory(prefix="surf-object-env-test-") as temporary:
            repo = Path(temporary)
            run("git", "init", str(repo), cwd=repo.parent)
            previous = os.environ.get("GIT_ALTERNATE_OBJECT_DIRECTORIES")
            try:
                os.environ["GIT_ALTERNATE_OBJECT_DIRECTORIES"] = "/synthetic/alternate"
                with self.assertRaisesRegex(GuardError, "object substitution environment"):
                    validate_object_store(repo)
            finally:
                if previous is None:
                    os.environ.pop("GIT_ALTERNATE_OBJECT_DIRECTORIES", None)
                else:
                    os.environ["GIT_ALTERNATE_OBJECT_DIRECTORIES"] = previous

    def test_rejects_partial_clone_and_promisor_configuration(self) -> None:
        for key, value in (("extensions.partialClone", "origin"), ("remote.origin.promisor", "true")):
            with self.subTest(key=key), tempfile.TemporaryDirectory(prefix="surf-promisor-test-") as temporary:
                repo = Path(temporary)
                run("git", "init", str(repo), cwd=repo.parent)
                run("git", "config", "--local", key, value, cwd=repo)
                with self.assertRaisesRegex(GuardError, "partial-clone or promisor"):
                    validate_object_store(repo)


class PushIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="surf-public-push-test-")
        base = Path(self.temporary.name)
        self.repo = base / "candidate"
        self.remote = base / "receiver.git"
        self.cache = Path(tempfile.gettempdir()) / "surf-publication-test-gitleaks-cache"
        run("git", "init", "--bare", str(self.remote), cwd=base)
        run("git", "init", "-b", "main", str(self.repo), cwd=base)
        run("git", "config", "user.name", "Surf Guard Test", cwd=self.repo)
        run("git", "config", "user.email", "guard-test@example.invalid", cwd=self.repo)
        (self.repo / ".github/scripts").mkdir(parents=True)
        (self.repo / ".github/publication").mkdir(parents=True)
        (self.repo / ".githooks").mkdir()
        for source, target in (
            (BOUNDARY, self.repo / ".github/scripts/check_publication_boundary.py"),
            (GUARD, self.repo / ".github/scripts/guard_public_push.py"),
            (INSTALLER, self.repo / ".github/scripts/install-gitleaks.sh"),
            (HOOK, self.repo / ".githooks/pre-push"),
        ):
            shutil.copy2(source, target)
            if source.stat().st_mode & 0o111:
                target.chmod(0o755)
        manifest = self.repo / ".github/publication/public-files.txt"
        manifest.write_text(".github/publication/public-files.txt\nREADME.md\n", encoding="utf-8")
        (self.repo / "README.md").write_text("Safe synthetic Surf candidate.\n", encoding="utf-8")
        (self.repo / ".git/info/exclude").write_text(".github/scripts/\n.githooks/\n", encoding="utf-8")
        # Guard machinery is tracked in production but intentionally untracked
        # here so the tiny candidate manifest exercises only the fixture.
        run("git", "add", "-f", ".github/publication/public-files.txt", "README.md", cwd=self.repo)
        run("git", "commit", "-m", "safe root", cwd=self.repo)
        run("git", "config", "core.hooksPath", ".githooks", cwd=self.repo)
        run("git", "remote", "add", "public", str(self.remote), cwd=self.repo)
        self.env = os.environ.copy()
        self.env["SURF_PUBLICATION_TEST_TARGET_URL"] = str(self.remote)
        self.env["XDG_CACHE_HOME"] = str(self.cache)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def push(self, *refspecs: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return run("git", "push", "public", *refspecs, cwd=self.repo, env=self.env, check=check)

    def remote_oid(self, ref: str) -> str | None:
        result = run("git", "--git-dir", str(self.remote), "rev-parse", "--verify", ref, cwd=self.repo, check=False)
        return result.stdout.strip() if result.returncode == 0 else None

    def safe_commit(self, message: str) -> str:
        with (self.repo / "README.md").open("a", encoding="utf-8") as output:
            output.write(message + "\n")
        run("git", "add", "README.md", cwd=self.repo)
        run("git", "commit", "-m", message, cwd=self.repo)
        return run("git", "rev-parse", "HEAD", cwd=self.repo).stdout.strip()

    def reset_to(self, oid: str) -> None:
        run("git", "reset", "--hard", oid, cwd=self.repo)
        run("git", "clean", "-fd", cwd=self.repo)

    def test_safe_branches_tags_force_multiple_updates_and_deletion(self) -> None:
        self.push("HEAD:refs/heads/main")
        first = self.remote_oid("refs/heads/main")
        self.assertIsNotNone(first)

        run("git", "tag", "safe-tag", cwd=self.repo)
        self.push("refs/tags/safe-tag")
        self.assertIsNotNone(self.remote_oid("refs/tags/safe-tag"))

        run("git", "checkout", "--orphan", "replacement", cwd=self.repo)
        # The tracked candidate files remain in the worktree for the new root.
        run("git", "add", "-f", ".github/publication/public-files.txt", "README.md", cwd=self.repo)
        run("git", "commit", "-m", "safe force replacement", cwd=self.repo)
        replacement = run("git", "rev-parse", "HEAD", cwd=self.repo).stdout.strip()
        self.push("--force", "HEAD:refs/heads/main")
        self.assertEqual(self.remote_oid("refs/heads/main"), replacement)

        run("git", "branch", "safe-one", cwd=self.repo)
        run("git", "branch", "safe-two", cwd=self.repo)
        self.push("refs/heads/safe-one", "refs/heads/safe-two")
        self.assertIsNotNone(self.remote_oid("refs/heads/safe-one"))
        self.assertIsNotNone(self.remote_oid("refs/heads/safe-two"))
        self.push(":refs/heads/safe-one")
        self.assertIsNone(self.remote_oid("refs/heads/safe-one"))

        run("git", "tag", "-a", "safe-annotated", "-m", "safe annotated release", cwd=self.repo)
        self.push("refs/tags/safe-annotated")
        self.assertIsNotNone(self.remote_oid("refs/tags/safe-annotated"))

    def test_each_leakage_canary_is_rejected_before_receiver_changes(self) -> None:
        self.push("HEAD:refs/heads/main")
        accepted = self.remote_oid("refs/heads/main")
        canaries = (
            "PUBLICATION " + "BLOCKER",
            "/" + "Users/private/worktree",
            "internal [" + "[abcdef1]] record",
            "ghp_" + "abcdefghijklmnopqrstuvwxyz123456",
            "AKIA" + "ABCDEFGHIJKLMNOP",
            # A gitleaks generic-api-key canary that is not one of the
            # publication-readiness regexes. It is long but nonfunctional.
            "api_key = " + "ZXCVBNMASDFGHJKLQWERTYUIOP1234567890",
        )
        for index, canary in enumerate(canaries):
            (self.repo / "README.md").write_text(f"canary {index}: {canary}\n", encoding="utf-8")
            run("git", "add", "README.md", cwd=self.repo)
            run("git", "commit", "-m", f"unsafe canary {index}", cwd=self.repo)
            if index == len(canaries) - 1:
                boundary = run(
                    "python3",
                    str(self.repo / ".github/scripts/check_publication_boundary.py"),
                    "check",
                    "--source-ref",
                    "HEAD",
                    "--publication-ready",
                    cwd=self.repo,
                    check=False,
                )
                self.assertEqual(boundary.returncode, 0, boundary.stderr)
            result = self.push("HEAD:refs/heads/main", check=False)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(self.remote_oid("refs/heads/main"), accepted)
            self.reset_to(accepted)

    def test_boundary_inventory_path_identifier_and_binary_canaries_never_reach_receiver(self) -> None:
        self.push("HEAD:refs/heads/main")
        accepted = self.remote_oid("refs/heads/main")

        cases = (
            ("blocked private path", {BLOCKED_EVALUATION_PATH: b"synthetic private evaluation\n"}, (".github/publication/public-files.txt", "README.md", BLOCKED_EVALUATION_PATH)),
            ("unexpected file", {"private-notes.md": b"synthetic unclassified content\n"}, None),
            ("account identifier", {"README.md": b"123e4567-e89b-12d3-a456-426614174000\n"}, None),
            ("binary NUL", {"asset.bin": b"synthetic\x00binary\n"}, (".github/publication/public-files.txt", "README.md", "asset.bin")),
        )
        for index, (label, files, manifest_paths) in enumerate(cases):
            with self.subTest(label=label):
                for relative, data in files.items():
                    target = self.repo / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
                if manifest_paths is not None:
                    (self.repo / ".github/publication/public-files.txt").write_text(
                        "\n".join(sorted(manifest_paths)) + "\n", encoding="utf-8"
                    )
                run("git", "add", "-A", cwd=self.repo)
                run("git", "commit", "-m", f"unsafe boundary canary {index}", cwd=self.repo)
                result = self.push("HEAD:refs/heads/main", check=False)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(self.remote_oid("refs/heads/main"), accepted)
                self.reset_to(accepted)

    def test_unsafe_extra_refs_block_safe_main_in_one_atomic_hook_decision(self) -> None:
        self.push("HEAD:refs/heads/main")
        accepted = self.remote_oid("refs/heads/main")
        safe = self.safe_commit("safe proposed main")
        run("git", "branch", "safe-proposed-main", safe, cwd=self.repo)
        canary = "ghp_" + "abcdefghijklmnopqrstuvwxyz1234567890ABCD"
        (self.repo / "README.md").write_text(canary + "\n", encoding="utf-8")
        run("git", "add", "README.md", cwd=self.repo)
        run("git", "commit", "-m", "unsafe extra ref", cwd=self.repo)
        run("git", "branch", "unsafe-extra", cwd=self.repo)
        run("git", "tag", "unsafe-extra-tag", cwd=self.repo)
        result = self.push(
            "refs/heads/safe-proposed-main:refs/heads/main",
            "refs/heads/unsafe-extra:refs/heads/unsafe-extra",
            "refs/tags/unsafe-extra-tag:refs/tags/unsafe-extra-tag",
            check=False,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.remote_oid("refs/heads/main"), accepted)
        self.assertIsNone(self.remote_oid("refs/heads/unsafe-extra"))
        self.assertIsNone(self.remote_oid("refs/tags/unsafe-extra-tag"))

    def test_annotated_tag_message_canary_is_rejected_before_receiver_changes(self) -> None:
        self.push("HEAD:refs/heads/main")
        canaries = (
            "ghp_" + "abcdefghijklmnopqrstuvwxyz1234567890ABCD",
            "PUBLICATION " + "BLOCKER",
            "/" + "Users/private/tag-message",
        )
        for index, canary in enumerate(canaries):
            tag = f"unsafe-tag-{index}"
            run("git", "tag", "-a", tag, "-m", canary, cwd=self.repo)
            result = self.push(f"refs/tags/{tag}", check=False)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIsNone(self.remote_oid(f"refs/tags/{tag}"))

    def test_commit_message_canary_is_rejected_with_safe_tree(self) -> None:
        self.push("HEAD:refs/heads/main")
        accepted = self.remote_oid("refs/heads/main")
        run("git", "commit", "--allow-empty", "-m", "/" + "Users/private/commit-message", cwd=self.repo)
        result = self.push("HEAD:refs/heads/main", check=False)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.remote_oid("refs/heads/main"), accepted)

    def test_unsafe_intermediate_commit_is_rejected_even_when_tip_tree_is_clean(self) -> None:
        self.push("HEAD:refs/heads/main")
        accepted = self.remote_oid("refs/heads/main")
        canary = "ghp_" + "abcdefghijklmnopqrstuvwxyz123456"
        (self.repo / "README.md").write_text(canary + "\n", encoding="utf-8")
        run("git", "add", "README.md", cwd=self.repo)
        run("git", "commit", "-m", "unsafe intermediate", cwd=self.repo)
        (self.repo / "README.md").write_text("Safe synthetic Surf candidate again.\n", encoding="utf-8")
        run("git", "add", "README.md", cwd=self.repo)
        run("git", "commit", "-m", "clean tip", cwd=self.repo)
        result = self.push("HEAD:refs/heads/main", check=False)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.remote_oid("refs/heads/main"), accepted)

    def test_blob_ref_tip_is_rejected(self) -> None:
        blob = run("git", "hash-object", "README.md", cwd=self.repo).stdout.strip()
        run("git", "update-ref", "refs/tags/blob-tip", blob, cwd=self.repo)
        result = self.push("refs/tags/blob-tip", check=False)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIsNone(self.remote_oid("refs/tags/blob-tip"))

    def test_unavailable_scanner_fails_closed(self) -> None:
        self.push("HEAD:refs/heads/main")
        accepted = self.remote_oid("refs/heads/main")
        self.safe_commit("safe update blocked without scanner")
        (self.repo / ".github/scripts/install-gitleaks.sh").chmod(0o644)
        result = self.push("HEAD:refs/heads/main", check=False)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.remote_oid("refs/heads/main"), accepted)

    def test_similarly_named_private_remote_is_not_classified_as_public(self) -> None:
        private = Path(self.temporary.name) / "private-withnative-surf-lab.git"
        run("git", "init", "--bare", str(private), cwd=self.repo)
        run("git", "remote", "add", "private-surf-lab", str(private), cwd=self.repo)
        canary = "ghp_" + "abcdefghijklmnopqrstuvwxyz1234567890ABCD"
        (self.repo / "README.md").write_text(canary + "\n", encoding="utf-8")
        run("git", "add", "README.md", cwd=self.repo)
        run("git", "commit", "-m", "private lab fixture", cwd=self.repo)
        result = run("git", "push", "private-surf-lab", "HEAD:refs/heads/main", cwd=self.repo, env=self.env, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        remote = run("git", "--git-dir", str(private), "rev-parse", "refs/heads/main", cwd=self.repo).stdout.strip()
        self.assertEqual(remote, run("git", "rev-parse", "HEAD", cwd=self.repo).stdout.strip())


if __name__ == "__main__":
    unittest.main()
