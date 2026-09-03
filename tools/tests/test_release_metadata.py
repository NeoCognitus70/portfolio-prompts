from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "check-library.py"
SPEC = importlib.util.spec_from_file_location("check_library", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECK_LIBRARY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_LIBRARY)


def backlog(outstanding_status: str = "IMPLEMENTED — owner refresh pending", total: int = 1) -> str:
    return f"""# Backlog

## Outstanding Items

### PP-01: Current release — Score: 10

**Status:** {outstanding_status}

## Risk Summary

| Priority | Count | Status Distribution |
|---|---|---|
| **Total Outstanding** | **{total}** | PP-01 |
| Resolved | 1 | PP-00 |

**Outstanding, by suggested order:** PP-01 (owner action required).

## Resolved Items

#### PP-00: Earlier release — Score: 10
"""


class BacklogConsistencyTests(unittest.TestCase):
    def test_accepts_matching_open_and_resolved_summaries(self) -> None:
        self.assertEqual(CHECK_LIBRARY.validate_backlog_consistency(backlog()), [])

    def test_rejects_terminal_status_in_outstanding(self) -> None:
        failures = CHECK_LIBRARY.validate_backlog_consistency(
            backlog(outstanding_status="RESOLVED 2026-09-03")
        )

        self.assertTrue(any("terminal status" in failure for failure in failures))

    def test_rejects_summary_count_drift(self) -> None:
        failures = CHECK_LIBRARY.validate_backlog_consistency(backlog(total=0))

        self.assertTrue(any("Total Outstanding is 0" in failure for failure in failures))

    def test_rejects_duplicate_item_ids(self) -> None:
        text = backlog() + "\n#### PP-01: Duplicate — Score: 1\n"

        failures = CHECK_LIBRARY.validate_backlog_consistency(text)

        self.assertTrue(any("must be unique: PP-01" in failure for failure in failures))


class ManifestVersionTests(unittest.TestCase):
    def test_accepts_shared_release_with_codex_cachebuster(self) -> None:
        failures = CHECK_LIBRARY.validate_plugin_manifest_versions(
            {"version": "0.4.0"},
            {"version": "0.4.0+codex.20260903120000"},
        )

        self.assertEqual(failures, [])

    def test_rejects_manifest_release_mismatch(self) -> None:
        failures = CHECK_LIBRARY.validate_plugin_manifest_versions(
            {"version": "0.4.0"},
            {"version": "0.3.0+codex.20260903120000"},
        )

        self.assertTrue(any("manifest release mismatch" in failure for failure in failures))

    def test_rejects_codex_version_without_cachebuster(self) -> None:
        failures = CHECK_LIBRARY.validate_plugin_manifest_versions(
            {"version": "0.4.0"},
            {"version": "0.4.0"},
        )

        self.assertTrue(any("<release>+codex.<cachebuster>" in failure for failure in failures))


class CodexDefaultPromptTests(unittest.TestCase):
    def test_accepts_three_suggested_prompts(self) -> None:
        failures = CHECK_LIBRARY.validate_codex_default_prompts(
            {"defaultPrompt": ["Status", "Resume", "Analyse"]}
        )

        self.assertEqual(failures, [])

    def test_rejects_more_than_three_suggested_prompts(self) -> None:
        failures = CHECK_LIBRARY.validate_codex_default_prompts(
            {"defaultPrompt": ["Status", "Resume", "Report", "Analyse"]}
        )

        self.assertTrue(any("maximum of 3" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
