"""Deterministic coverage for the handover manifest builder's P-09 pair-integrity gate."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "build_handover_manifest", TOOLS / "build-handover-manifest.py"
)
build_handover_manifest = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_handover_manifest)


class HandoverManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.session_notes = Path(self._temp.name) / "session-notes"
        self.session_notes.mkdir()

    def tearDown(self) -> None:
        self._temp.cleanup()

    def _handover(self, project: str, version: int, ts: str, html: bool) -> None:
        stem = f"{project}_session-notes_v{version}_{ts}"
        (self.session_notes / f"{stem}.md").write_text(f"# {project} v{version}\n", encoding="utf-8")
        if html:
            (self.session_notes / f"{stem}.html").write_text("<!doctype html>\n", encoding="utf-8")

    def test_complete_pairs_report_no_violations(self) -> None:
        self._handover("alpha", 1, "20260101T0900Z", html=True)
        self._handover("alpha", 2, "20260201T0900Z", html=True)
        self.assertEqual(build_handover_manifest.unpaired(self.session_notes), [])
        manifest = build_handover_manifest.build(self.session_notes)
        self.assertEqual(len(manifest["handovers"]), 2)
        self.assertEqual(manifest["latest"]["alpha"]["version"], 2)
        self.assertTrue(all(h["html"] for h in manifest["handovers"]))

    def test_missing_html_companion_is_a_violation(self) -> None:
        self._handover("alpha", 1, "20260101T0900Z", html=True)
        self._handover("beta", 3, "20260301T0900Z", html=False)
        missing = build_handover_manifest.unpaired(self.session_notes)
        self.assertEqual(missing, ["beta_session-notes_v3_20260301T0900Z.md"])
        # The manifest still records the truthful (null) html entry while the pair is repaired.
        manifest = build_handover_manifest.build(self.session_notes)
        beta = [h for h in manifest["handovers"] if h["project"] == "beta"][0]
        self.assertIsNone(beta["html"])

    def test_latest_is_numeric_not_lexical(self) -> None:
        self._handover("gamma", 9, "20260101T0900Z", html=True)
        self._handover("gamma", 13, "20260601T0900Z", html=True)
        manifest = build_handover_manifest.build(self.session_notes)
        self.assertEqual(manifest["latest"]["gamma"]["version"], 13)

    def test_non_matching_files_are_ignored(self) -> None:
        (self.session_notes / "README.md").write_text("not a handover\n", encoding="utf-8")
        self.assertEqual(build_handover_manifest.unpaired(self.session_notes), [])
        self.assertEqual(build_handover_manifest.build(self.session_notes)["handovers"], [])


if __name__ == "__main__":
    unittest.main()
