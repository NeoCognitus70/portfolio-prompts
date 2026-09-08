"""Cross-language guard for the shared Kanban generator (tools/kanban).

check-library.py's `check_kanban` runs the generator's own Node suite. This Python
test is discovered by the existing `unittest discover -s tools/tests` harness (via
check_workspace_preflight) and adds a complementary, language-boundary guard:

  1. the committed fixture boards are in sync with their backlogs (the drift-gate,
     `--check`, exits 0), and
  2. the generated board is genuinely self-contained — no external script/style,
     no CDN URL, no vendored files (the D6 render-stack contract).

It is skipped when Node is unavailable, matching check_kanban's own behaviour.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import unittest
from pathlib import Path

KANBAN = Path(__file__).resolve().parents[1] / "kanban"
GENERATOR = KANBAN / "generate-kanban.mjs"
NODE = shutil.which("node")

FIXTURES = [
    # (fixture folder, project, extra args)
    ("auth-table", "demo", []),
    ("risk-block", "riskdemo", ["--dialect", "risk-block"]),
    ("risk-template", "templatedemo", ["--dialect", "risk-block"]),
]


@unittest.skipUnless(NODE, "node not found; skipping kanban generator guard")
class KanbanGeneratorTests(unittest.TestCase):
    def _check(self, folder: str, project: str, extra: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            [NODE, str(GENERATOR), "--check", "--project", project, "--cwd",
             str(KANBAN / "test" / "fixtures" / folder), *extra],
            capture_output=True, text=True,
        )

    def test_committed_fixture_boards_are_in_sync(self) -> None:
        for folder, project, extra in FIXTURES:
            with self.subTest(fixture=folder):
                result = self._check(folder, project, extra)
                self.assertEqual(
                    result.returncode, 0,
                    f"{folder} board is out of step:\n{result.stdout}\n{result.stderr}",
                )

    def test_generated_board_is_self_contained(self) -> None:
        for folder, project, _extra in FIXTURES:
            with self.subTest(fixture=folder):
                board = KANBAN / "test" / "fixtures" / folder / f"{project}_implementation-kanban_v1.html"
                html = board.read_text(encoding="utf-8")
                self.assertNotRegex(html, r"<script[^>]+\bsrc=", "board must not load external scripts")
                self.assertNotRegex(html, r"<link[^>]+stylesheet", "board must not load external stylesheets")
                self.assertNotRegex(html, r"https?://", "board must not reference any CDN/URL")
                self.assertNotIn("vendor/", html, "board must not reference vendored files")
                self.assertIn('id="payload-tickets"', html)
                self.assertIn('id="payload-stats"', html)


if __name__ == "__main__":
    unittest.main()
