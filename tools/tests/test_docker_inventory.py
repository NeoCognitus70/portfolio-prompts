"""Deterministic coverage for the read-only Docker inventory (no Docker engine needed)."""
from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import yaml

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import docker_inventory as inv  # noqa: E402

NOW = datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)
DIGEST = "sha256:" + "a" * 64
TOOL_DIGEST = "sha256:" + "d" * 64


def _image(repo: str, tag: str, image_id: str, size: str = "100MB", containers: str = "0") -> dict:
    return {"Repository": repo, "Tag": tag, "ID": image_id, "Size": size, "UniqueSize": size,
            "SharedSize": "0B", "Containers": containers, "CreatedSince": "1 day ago"}


class DockerInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self._temp.name)
        app = self.workspace / "shop"
        (app / "docker").mkdir(parents=True)
        (app / "docker" / "docker-compose.yml").write_text(
            yaml.safe_dump({
                "services": {
                    "web": {"image": "nginx:1.27"},
                    "worker": {"image": "nginx:1.27"},
                    "db": {"image": "${OWNER:?set OWNER}/db:1@" + DIGEST},
                    "tests": {"build": "."},
                },
                "volumes": {"data": {}},
            }),
            encoding="utf-8",
        )
        (app / "Dockerfile").write_text("FROM node:24-alpine AS build\nFROM build\n", encoding="utf-8")
        (app / "pins.psd1").write_text("Digest = '" + TOOL_DIGEST + "'\n", encoding="utf-8")
        self.registry = {
            "projects": [
                {
                    "project": "shop",
                    "docker": {
                        "compose": ["docker/docker-compose.yml"],
                        "compose_env": {"OWNER": "acme"},
                        "dockerfiles": ["Dockerfile"],
                        "images": [{"ref": "tool@" + TOOL_DIGEST, "purpose": "builder", "source": "pins.psd1"}],
                        "volumes": ["shop-cache"],
                    },
                },
                {"project": "no-docker"},
            ],
            "docker_external": [
                {"name": "rehearsal", "compose_projects": ["proj-08"], "images": ["nginx:1.27"]}
            ],
        }
        self.state = {
            "server_version": "29.0.1",
            "summary": [{"Type": "Images", "TotalCount": 5, "Active": 2, "Size": "1GB", "Reclaimable": "0B"}],
            "verbose": {
                "Images": [
                    _image("nginx", "1.27", "sha256:" + "1" * 64, containers="1"),
                    _image("acme/db", "<none>", DIGEST),
                    _image("docker-tests", "latest", "sha256:" + "2" * 64),
                    _image("node", "24-alpine", "sha256:" + "3" * 64),
                    _image("maven", "<none>", "sha256:" + "4" * 64, size="700MB"),
                    _image("leftover", "latest", "sha256:" + "5" * 64),
                ],
                "Containers": [
                    {"Names": "docker-web-1", "Image": "nginx:1.27", "State": "running", "Status": "Up 1 hour",
                     "Labels": "com.docker.compose.project=docker", "Mounts": "docker_data," + "b" * 64, "Size": "1kB"},
                    {"Names": "proj08", "Image": "nginx:1.27", "State": "exited", "Status": "Exited (0)",
                     "Labels": "com.docker.compose.project=proj-08", "Mounts": "", "Size": "0B"},
                    {"Names": "stray", "Image": "leftover", "State": "exited", "Status": "Exited (143)",
                     "Labels": "", "Mounts": "", "Size": "0B"},
                ],
                "Volumes": [
                    {"Name": "docker_data", "Labels": "com.docker.compose.project=docker", "Size": "10MB", "Links": "1"},
                    {"Name": "b" * 64, "Labels": "", "Size": "5MB", "Links": "1"},
                    {"Name": "shop-cache", "Labels": "", "Size": "20MB", "Links": "0"},
                    {"Name": "c" * 64, "Labels": "", "Size": "30MB", "Links": "0"},
                    {"Name": "mystery", "Labels": "", "Size": "40MB", "Links": "0"},
                ],
            },
        }

    def tearDown(self) -> None:
        self._temp.cleanup()

    def build(self) -> dict:
        return inv.build_inventory(self.registry, self.workspace, self.state, NOW)

    def owner(self, result: dict, name: str) -> dict:
        return next(o for o in result["owners"] if o["owner"] == name)

    def test_interpolates_compose_variables(self) -> None:
        self.assertEqual(inv.interpolate("${A:-x}/${B}/$$C", {"B": "b"}), "x/b/$C")
        with self.assertRaises(inv.InventoryError):
            inv.interpolate("${MISSING:?needed}", {})

    def test_parses_references(self) -> None:
        self.assertEqual(inv.parse_ref("docker.io/library/mysql:8.0@" + DIGEST), ("mysql", "8.0", DIGEST))
        self.assertEqual(inv.parse_ref("localhost:5000/app"), ("localhost:5000/app", "latest", None))
        self.assertEqual(inv.parse_ref("tool@" + DIGEST), ("tool", None, DIGEST))

    def test_parses_sizes(self) -> None:
        self.assertEqual(inv.parse_size("1.09GB"), 1_090_000_000)
        self.assertEqual(inv.parse_size("32.8kB"), 32_800)
        self.assertEqual(inv.parse_size("N/A"), 0)

    def test_dockerfile_skips_internal_stages(self) -> None:
        self.assertEqual(inv.dockerfile_bases(self.workspace / "shop" / "Dockerfile"), ["node:24-alpine"])

    def test_claims_project_objects(self) -> None:
        shop = self.owner(self.build(), "shop")
        self.assertEqual(shop["compose_project"], "docker")
        refs = {row["ref"]: row for row in shop["images"]}
        self.assertEqual(len([r for r in shop["images"] if r["ref"] == "nginx:1.27"]), 1, "duplicate refs merge")
        self.assertIn("worker", refs["nginx:1.27"]["purpose"])
        self.assertTrue(refs["acme/db:1@" + DIGEST]["present"], "digest pins match by image ID")
        self.assertTrue(refs["docker-tests"]["present"], "Compose-built images are named <project>-<service>")
        self.assertTrue(refs["node:24-alpine"]["present"])
        self.assertFalse(refs["tool@" + TOOL_DIGEST]["present"])
        self.assertEqual([c["name"] for c in shop["containers"]], ["docker-web-1"])
        volumes = {v["name"] for v in shop["volumes"]}
        self.assertEqual(volumes, {"docker_data", "b" * 64, "shop-cache"}, "label, mount and explicit claims")
        self.assertEqual(shop["warnings"], [])

    def test_external_claims_and_shared_images(self) -> None:
        result = self.build()
        rehearsal = self.owner(result, "rehearsal")
        self.assertEqual([c["name"] for c in rehearsal["containers"]], ["proj08"])
        self.assertEqual(result["shared"][0]["owners"], ["rehearsal", "shop"])

    def test_reports_unclaimed_with_actions(self) -> None:
        unclaimed = self.build()["unclaimed"]
        images = {row["image"]: row for row in unclaimed["images"]}
        self.assertEqual(set(images), {"maven (untagged)", "leftover:latest"})
        self.assertIn("superseded pin", images["maven (untagged)"]["action"])
        self.assertIn("Declared by no project", images["leftover:latest"]["action"])
        self.assertEqual([c["name"] for c in unclaimed["containers"]], ["stray"])
        volumes = {row["name"]: row["action"] for row in unclaimed["volumes"]}
        self.assertIn("Anonymous", volumes["c" * 64])
        self.assertIn("may hold data", volumes["mystery"])

    def test_warns_on_pin_drift_and_missing_files(self) -> None:
        self.registry["projects"][0]["docker"]["images"][0]["ref"] = "tool@sha256:" + "f" * 64
        self.registry["projects"][0]["docker"]["dockerfiles"].append("missing/Dockerfile")
        warnings = self.owner(self.build(), "shop")["warnings"]
        self.assertTrue(any("pin drift" in w for w in warnings))
        self.assertTrue(any("Dockerfile missing" in w for w in warnings))

    def test_rejects_invalid_blocks(self) -> None:
        self.registry["projects"][0]["docker"]["colour"] = "blue"
        self.registry["projects"][0]["docker"]["images"].append({"purpose": "no ref"})
        with self.assertRaises(inv.InventoryError) as raised:
            self.build()
        self.assertIn("unknown key 'colour'", str(raised.exception))
        self.assertIn("needs a 'ref'", str(raised.exception))

    def test_refuses_mutating_docker_commands(self) -> None:
        for command in (("rm", "x"), ("rmi", "x"), ("system", "prune"), ("volume", "rm", "x"), ("compose", "down")):
            with self.assertRaises(inv.InventoryError):
                inv.run_docker(*command)

    def test_renders_and_writes_between_markers(self) -> None:
        markdown = inv.render_markdown(self.build())
        self.assertIn("#### shop (project; Compose project `docker`)", markdown)
        self.assertIn("### Unclaimed (review before any removal)", markdown)
        self.assertNotIn("—", markdown)
        target = self.workspace / "record.md"
        target.write_text(f"intro\n{inv.START_MARKER}\nold\n{inv.END_MARKER}\nlog\n", encoding="utf-8")
        inv.write_between_markers(target, markdown)
        text = target.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("intro\n"))
        self.assertTrue(text.endswith(f"{inv.END_MARKER}\nlog\n"))
        self.assertNotIn("\nold\n", text)

    def test_live_registry_docker_blocks_are_valid(self) -> None:
        registry = yaml.safe_load((TOOLS.parent / "registry.yml").read_text(encoding="utf-8"))
        self.assertEqual(inv.validate_registry(registry), [])


if __name__ == "__main__":
    unittest.main()
