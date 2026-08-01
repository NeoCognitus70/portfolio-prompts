from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "check-library.py"
SPEC = importlib.util.spec_from_file_location("check_library", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECK_LIBRARY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_LIBRARY)


def project_row(
    name: str,
    *,
    status: str = "active",
    presentation_role: object = "showcase",
    orchestration_target: bool = True,
) -> dict:
    return {
        "project": name,
        "status": status,
        "presentation_role": presentation_role,
        "orchestration_target": orchestration_target,
    }


class RegistryPresentationRoleTests(unittest.TestCase):
    def test_accepts_all_roles_independently_of_lifecycle(self) -> None:
        projects = [
            project_row("showcase-active", presentation_role="showcase"),
            project_row(
                "methodology-meta",
                status="meta",
                presentation_role="methodology",
                orchestration_target=False,
            ),
            project_row("hidden-resting", status="resting", presentation_role="hidden"),
        ]

        self.assertEqual(CHECK_LIBRARY.validate_project_registry_rows(projects), [])

    def test_rejects_missing_role(self) -> None:
        project = project_row("missing")
        del project["presentation_role"]

        failures = CHECK_LIBRARY.validate_project_registry_rows([project])

        self.assertEqual(len(failures), 1)
        self.assertIn("must declare presentation_role", failures[0])

    def test_rejects_unsupported_role(self) -> None:
        failures = CHECK_LIBRARY.validate_project_registry_rows(
            [project_row("unsupported", presentation_role="featured")]
        )

        self.assertEqual(len(failures), 1)
        self.assertIn("hidden, methodology, showcase", failures[0])

    def test_rejects_multiple_roles_instead_of_crashing(self) -> None:
        failures = CHECK_LIBRARY.validate_project_registry_rows(
            [project_row("multiple", presentation_role=["showcase", "hidden"])]
        )

        self.assertEqual(len(failures), 1)
        self.assertIn("must declare presentation_role", failures[0])

    def test_preserves_existing_meta_orchestration_rule(self) -> None:
        failures = CHECK_LIBRARY.validate_project_registry_rows(
            [
                project_row(
                    "meta-target",
                    status="meta",
                    presentation_role="methodology",
                    orchestration_target=True,
                )
            ]
        )

        self.assertEqual(len(failures), 1)
        self.assertIn("cannot be an orchestration target", failures[0])


if __name__ == "__main__":
    unittest.main()
