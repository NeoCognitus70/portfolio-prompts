"""Deterministic integration coverage for the read-only workspace preflight."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

import yaml

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import workspace_preflight  # noqa: E402


class WorkspacePreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self._temp.name)
        self.session_notes = self.workspace / "session-notes"
        self.session_notes.mkdir()
        self.projects: dict[str, Path] = {}

        self._make_project("clean", handover="fresh")
        self._make_project("dirty", handover="fresh", dirty=True)
        self._make_project("behind", handover="stale", behind=True)
        self._make_project("topic", handover="fresh", topic=True)
        self._make_project("missing-backlog", handover="fresh", backlog=False)
        self._make_project("missing-handover", handover=None)

        registry = {
            "version": 1,
            "defaults": {
                "backlog": "docs/backlog.md",
                "project_contract": "docs/project-contract.md",
            },
            "projects": [
                {
                    "project": name,
                    "status": "active",
                    "orchestration_target": True,
                    "gates": ["npm run verify"],
                }
                for name in self.projects
            ]
            + [
                {
                    "project": "meta-control",
                    "status": "meta",
                    "orchestration_target": False,
                    "gates": ["python tools/check.py"],
                }
            ],
        }
        self.registry = self.workspace / "registry.yml"
        self.registry.write_text(yaml.safe_dump(registry, sort_keys=False), encoding="utf-8")

    def tearDown(self) -> None:
        self._temp.cleanup()

    def _git(
        self,
        repo: Path,
        *args: str,
        commit_date: str | None = None,
    ) -> str:
        env = os.environ.copy()
        if commit_date:
            env["GIT_AUTHOR_DATE"] = commit_date
            env["GIT_COMMITTER_DATE"] = commit_date
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            check=False,
        )
        if result.returncode != 0:
            self.fail(f"git {' '.join(args)} failed: {result.stderr}")
        return result.stdout.strip()

    def _make_project(
        self,
        name: str,
        *,
        handover: str | None,
        backlog: bool = True,
        dirty: bool = False,
        behind: bool = False,
        topic: bool = False,
    ) -> None:
        repo = self.workspace / name
        repo.mkdir()
        self.projects[name] = repo
        self._git(repo, "init", "-b", "main")
        self._git(repo, "config", "user.name", "Preflight Test")
        self._git(repo, "config", "user.email", "preflight@example.invalid")
        (repo / "README.md").write_text(f"# {name}\n", encoding="utf-8")
        if backlog:
            (repo / "docs").mkdir()
            (repo / "docs" / "backlog.md").write_text("# Backlog\n", encoding="utf-8")
        self._git(repo, "add", ".")
        self._git(
            repo,
            "commit",
            "-m",
            "fixture: initial",
            commit_date="2026-01-01T00:00:00Z",
        )
        initial = self._git(repo, "rev-parse", "HEAD")
        self._git(repo, "remote", "add", "origin", f"https://example.invalid/{name}.git")
        self._git(repo, "update-ref", "refs/remotes/origin/main", initial)
        self._git(
            repo,
            "symbolic-ref",
            "refs/remotes/origin/HEAD",
            "refs/remotes/origin/main",
        )
        self._git(repo, "branch", "--set-upstream-to=origin/main", "main")

        if behind:
            (repo / "README.md").write_text(f"# {name}\nremote change\n", encoding="utf-8")
            self._git(repo, "add", "README.md")
            self._git(
                repo,
                "commit",
                "-m",
                "fixture: fetched remote commit",
                commit_date="2026-01-02T00:00:00Z",
            )
            fetched_head = self._git(repo, "rev-parse", "HEAD")
            self._git(repo, "update-ref", "refs/remotes/origin/main", fetched_head)
            self._git(repo, "reset", "--hard", initial)

        if topic:
            self._git(repo, "switch", "-c", "feature/preflight-fixture")
            topic_head = self._git(repo, "rev-parse", "HEAD")
            self._git(repo, "update-ref", "refs/remotes/origin/feature/preflight-fixture", topic_head)
            self._git(
                repo,
                "branch",
                "--set-upstream-to=origin/feature/preflight-fixture",
                "feature/preflight-fixture",
            )

        if dirty:
            (repo / "untracked.txt").write_text("dirty fixture\n", encoding="utf-8")

        if handover:
            timestamp = "20990101T0000Z" if handover == "fresh" else "20000101T0000Z"
            stem = f"{name}_session-notes_v1_{timestamp}"
            (self.session_notes / f"{stem}.md").write_text("# Handover\n", encoding="utf-8")
            (self.session_notes / f"{stem}.html").write_text("<h1>Handover</h1>\n", encoding="utf-8")

    def _snapshot(self, repo: Path) -> tuple[str, str, str, str]:
        return (
            self._git(repo, "rev-parse", "HEAD"),
            self._git(repo, "branch", "--show-current"),
            self._git(repo, "status", "--porcelain"),
            self._git(repo, "for-each-ref", "--format=%(refname) %(objectname)"),
        )

    def _reports(self) -> tuple[dict, dict[str, dict]]:
        before = {name: self._snapshot(repo) for name, repo in self.projects.items()}
        result = workspace_preflight.inspect_workspace(self.registry, self.workspace)
        after = {name: self._snapshot(repo) for name, repo in self.projects.items()}
        self.assertEqual(before, after, "preflight changed checkout-visible Git state")
        for repo in self.projects.values():
            self.assertFalse((repo / ".git" / "index.lock").exists())
        return result, {target["project"]: target for target in result["targets"]}

    def test_registry_driven_scenario_matrix(self) -> None:
        result, reports = self._reports()

        self.assertTrue(result["read_only"])
        self.assertEqual(result["target_count"], 6)
        self.assertNotIn("meta-control", reports)

        self.assertEqual(reports["clean"]["status"], "READY")
        self.assertFalse(reports["clean"]["git"]["dirty"])
        self.assertEqual(reports["clean"]["gates"]["source"], "registry.yml project gates")
        self.assertEqual(reports["clean"]["handover"]["freshness"], "current")

        self.assertEqual(reports["dirty"]["status"], "BLOCKED")
        self.assertTrue(reports["dirty"]["git"]["dirty"])
        self.assertTrue(any("uncommitted" in item for item in reports["dirty"]["blockers"]))

        self.assertEqual(reports["behind"]["status"], "WARN")
        self.assertEqual(reports["behind"]["git"]["ahead"], 0)
        self.assertEqual(reports["behind"]["git"]["behind"], 1)
        self.assertEqual(reports["behind"]["handover"]["freshness"], "stale")

        self.assertEqual(reports["topic"]["status"], "WARN")
        self.assertEqual(reports["topic"]["git"]["branch"], "feature/preflight-fixture")
        self.assertTrue(any("topic branch" in item for item in reports["topic"]["warnings"]))

        self.assertEqual(reports["missing-backlog"]["status"], "BLOCKED")
        self.assertFalse(reports["missing-backlog"]["backlog"]["present"])
        self.assertTrue(
            any("backlog is missing" in item for item in reports["missing-backlog"]["blockers"])
        )

        self.assertEqual(reports["missing-handover"]["status"], "WARN")
        self.assertEqual(reports["missing-handover"]["handover"]["freshness"], "missing")
        self.assertTrue(
            any("handover is missing" in item for item in reports["missing-handover"]["warnings"])
        )

    def test_subset_uses_registry_order_and_rejects_non_targets(self) -> None:
        selected = workspace_preflight.inspect_workspace(
            self.registry, self.workspace, ["topic", "clean"]
        )
        self.assertEqual(
            [target["project"] for target in selected["targets"]], ["clean", "topic"]
        )
        with self.assertRaises(workspace_preflight.PreflightError):
            workspace_preflight.inspect_workspace(
                self.registry, self.workspace, ["meta-control"]
            )

    def test_git_command_allowlist_rejects_mutation(self) -> None:
        with self.assertRaises(workspace_preflight.PreflightError):
            workspace_preflight._git(self.projects["clean"], "fetch")

    def test_cli_exit_codes_distinguish_ready_blocked_and_invalid(self) -> None:
        common = ["--registry", str(self.registry), "--workspace", str(self.workspace)]
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            self.assertEqual(
                workspace_preflight.main([*common, "--projects", "clean"]), 0
            )
            self.assertEqual(
                workspace_preflight.main([*common, "--projects", "dirty"]), 1
            )
            self.assertEqual(
                workspace_preflight.main([*common, "--projects", "meta-control"]), 2
            )


if __name__ == "__main__":
    unittest.main()
