"""Deterministic coverage tests for the prompt->skill wrapper gate (PP-39).

A canonical prompt with no `skills/<name>/` wrapper is invisible to a skill-driven agent — the
lifecycle stage it documents is skipped rather than declined. `check_skills` validates the
skill->prompt direction; these tests pin the reverse.
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "check-library.py"
SPEC = importlib.util.spec_from_file_location("check_library", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECK_LIBRARY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_LIBRARY)

failures = CHECK_LIBRARY.prompt_skill_coverage_failures


class PromptSkillCoverageTests(unittest.TestCase):
    def test_every_prompt_wrapped_passes(self) -> None:
        self.assertEqual(
            failures({"write-handover", "loop-worklist"}, {"write-handover", "loop-worklist"}, {}),
            [],
        )

    def test_prompt_without_wrapper_fails(self) -> None:
        fails = failures({"write-handover", "write-walkthrough"}, {"write-handover"}, {})
        self.assertEqual(len(fails), 1)
        self.assertIn("write-walkthrough.prompt.md", fails[0])
        self.assertIn("skills/write-walkthrough/", fails[0])

    def test_recorded_exception_passes(self) -> None:
        self.assertEqual(
            failures(
                {"write-handover", "experimental-thing"},
                {"write-handover"},
                {"experimental-thing": "deliberately prompt-only while it is being trialled"},
            ),
            [],
        )

    def test_stale_exception_for_a_now_wrapped_prompt_fails(self) -> None:
        fails = failures({"write-handover"}, {"write-handover"}, {"write-handover": "old reason"})
        self.assertEqual(len(fails), 1)
        self.assertIn("stale exception", fails[0])

    def test_exception_naming_a_nonexistent_prompt_fails(self) -> None:
        fails = failures({"write-handover"}, {"write-handover"}, {"ghost": "no such prompt"})
        self.assertEqual(len(fails), 1)
        self.assertIn("not a prompt file", fails[0])

    def test_live_library_has_full_coverage(self) -> None:
        """The real repository must satisfy the gate — this is what PP-39 fixes."""
        fails: list[str] = []
        CHECK_LIBRARY.check_prompt_skill_coverage(fails)
        self.assertEqual(fails, [], "every canonical prompt should have a skill wrapper")


if __name__ == "__main__":
    unittest.main()
