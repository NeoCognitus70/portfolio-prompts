#!/usr/bin/env python3
"""Read-only Docker inventory for the portfolio (portfolio Docker record).

Reads the optional ``docker:`` block of each project row (and the top-level
``docker_external:`` claims) in ``registry.yml``, resolves what each project declares
(Compose services, Dockerfile base images, script-run images, named volumes), then asks the
local Docker engine what is actually present. The report maps every image, container and
volume to the project that claims it, lists what nothing claims, and suggests a review action.

It never removes, stops, pulls or builds anything: every Docker call goes through a read-only
allowlist. Removal stays a manual, approved step, recorded in the cleanup log of
``portfolio-docs/PORTFOLIO_DOCKER_INVENTORY.md``.

Usage (from the portfolio root or anywhere):
  python portfolio-prompts/tools/docker_inventory.py                 # Markdown to stdout
  python portfolio-prompts/tools/docker_inventory.py --json          # machine-readable
  python portfolio-prompts/tools/docker_inventory.py --write portfolio-docs/PORTFOLIO_DOCKER_INVENTORY.md

Exit codes:
  0  report produced
  2  the registry, a docker block or the Docker engine could not be read
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("docker-inventory: PyYAML is required (pip install pyyaml)")


HERE = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = HERE / "registry.yml"
DEFAULT_WORKSPACE = HERE.parent

START_MARKER = "<!-- DOCKER-INVENTORY:START -->"
END_MARKER = "<!-- DOCKER-INVENTORY:END -->"

# Defence in depth: the inventory may only ever ask Docker these read-only questions.
READ_ONLY_DOCKER_COMMANDS = frozenset({("system", "df"), ("version",)})

DOCKER_KEYS = {"compose", "compose_env", "compose_project", "dockerfiles", "images", "volumes", "notes"}
IMAGE_KEYS = {"ref", "purpose", "source"}
EXTERNAL_KEYS = {"name", "location", "compose_projects", "containers", "images", "volumes", "notes"}

ANONYMOUS_VOLUME = re.compile(r"^[0-9a-f]{64}$")


class InventoryError(RuntimeError):
    """The inventory cannot produce a trustworthy report."""


# ---------------------------------------------------------------------------
# Registry validation
# ---------------------------------------------------------------------------

def validate_docker_block(owner: str, block: Any) -> list[str]:
    """Return human-readable problems with one project's ``docker:`` block (empty when valid)."""
    errors: list[str] = []
    if not isinstance(block, dict):
        return [f"{owner}: docker must be a mapping"]
    for key in sorted(set(block) - DOCKER_KEYS):
        errors.append(f"{owner}: docker has unknown key '{key}'")
    for key in ("compose", "dockerfiles", "volumes"):
        value = block.get(key, [])
        if not isinstance(value, list) or not all(isinstance(v, str) and v for v in value):
            errors.append(f"{owner}: docker.{key} must be a list of non-empty strings")
    env = block.get("compose_env", {})
    if not isinstance(env, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in env.items()):
        errors.append(f"{owner}: docker.compose_env must map strings to strings")
    if "compose_project" in block and not isinstance(block["compose_project"], str):
        errors.append(f"{owner}: docker.compose_project must be a string")
    images = block.get("images", [])
    if not isinstance(images, list):
        errors.append(f"{owner}: docker.images must be a list")
        images = []
    for index, image in enumerate(images):
        if not isinstance(image, dict) or not isinstance(image.get("ref"), str) or not image["ref"]:
            errors.append(f"{owner}: docker.images[{index}] needs a 'ref'")
            continue
        for key in sorted(set(image) - IMAGE_KEYS):
            errors.append(f"{owner}: docker.images[{index}] has unknown key '{key}'")
    return errors


def validate_external(entry: Any, index: int) -> list[str]:
    if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
        return [f"docker_external[{index}] needs a 'name'"]
    errors = [f"docker_external[{index}] has unknown key '{k}'" for k in sorted(set(entry) - EXTERNAL_KEYS)]
    for key in ("compose_projects", "containers", "images", "volumes"):
        value = entry.get(key, [])
        if not isinstance(value, list) or not all(isinstance(v, str) and v for v in value):
            errors.append(f"docker_external[{index}].{key} must be a list of non-empty strings")
    return errors


def validate_registry(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for row in data.get("projects") or []:
        if isinstance(row, dict) and "docker" in row:
            errors.extend(validate_docker_block(str(row.get("project")), row["docker"]))
    for index, entry in enumerate(data.get("docker_external") or []):
        errors.extend(validate_external(entry, index))
    return errors


# ---------------------------------------------------------------------------
# Compose and Dockerfile parsing
# ---------------------------------------------------------------------------

_VAR = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?:(:?[-?])([^}]*))?\}|\$([A-Za-z_][A-Za-z0-9_]*)")


def interpolate(value: str, env: dict[str, str]) -> str:
    """Resolve Compose-style ``${VAR}``, ``${VAR:-default}`` and ``${VAR:?message}`` references."""

    def replace(match: re.Match[str]) -> str:
        name = match.group(1) or match.group(4)
        operator, argument = match.group(2), match.group(3) or ""
        current = env.get(name)
        if operator in (":-", "-"):
            return current if current else argument
        if operator in (":?", "?") and not current:
            raise InventoryError(f"compose variable {name} is required but not set in docker.compose_env")
        return current or ""

    return _VAR.sub(replace, value.replace("$$", "\0")).replace("\0", "$")


def compose_project_name(compose_files: list[Path], explicit: str | None, top_level_name: str | None) -> str:
    raw = explicit or top_level_name or compose_files[0].resolve().parent.name
    return re.sub(r"[^a-z0-9_-]", "", raw.lower())


@dataclass
class Declared:
    ref: str
    purpose: str
    source: str


@dataclass
class ProjectDeclaration:
    owner: str
    kind: str  # "project" or "external"
    compose_project: str | None = None
    images: list[Declared] = field(default_factory=list)
    volumes: list[str] = field(default_factory=list)
    containers: list[str] = field(default_factory=list)
    compose_projects: list[str] = field(default_factory=list)
    notes: str = ""
    warnings: list[str] = field(default_factory=list)


def parse_compose(files: list[Path], env: dict[str, str]) -> tuple[str | None, dict[str, dict[str, Any]], list[str]]:
    """Merge Compose files in ``-f`` order. Later files override a service's image."""
    name: str | None = None
    services: dict[str, dict[str, Any]] = {}
    volumes: list[str] = []
    for path in files:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        name = data.get("name") or name
        for service, spec in (data.get("services") or {}).items():
            merged = services.setdefault(service, {})
            spec = spec or {}
            if "image" in spec:
                merged["image"] = interpolate(str(spec["image"]), env)
            if "build" in spec:
                merged["build"] = True
            if "container_name" in spec:
                merged["container_name"] = spec["container_name"]
        for volume in (data.get("volumes") or {}):
            if volume not in volumes:
                volumes.append(volume)
    return name, services, volumes


def dockerfile_bases(path: Path) -> list[str]:
    bases: list[str] = []
    stages: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\s*FROM\s+(?:--platform=\S+\s+)?(\S+)(?:\s+AS\s+(\S+))?", line, re.IGNORECASE)
        if match:
            image = match.group(1)
            if image.lower() not in stages and image.lower() != "scratch":
                bases.append(image)
            if match.group(2):
                stages.add(match.group(2).lower())
    return bases


def declare_project(row: dict[str, Any], workspace: Path) -> ProjectDeclaration:
    project = row["project"]
    block = row["docker"]
    root = workspace / project
    declaration = ProjectDeclaration(owner=project, kind="project", notes=str(block.get("notes", "")).strip())
    env = dict(block.get("compose_env") or {})

    compose_files = [root / rel for rel in block.get("compose", [])]
    missing = [str(p.relative_to(workspace)) for p in compose_files if not p.is_file()]
    if missing:
        declaration.warnings.append("compose file missing: " + ", ".join(missing))
    present = [p for p in compose_files if p.is_file()]
    if present:
        name, services, volumes = parse_compose(present, env)
        declaration.compose_project = compose_project_name(present, block.get("compose_project"), name)
        label = " + ".join(block.get("compose", []))
        for service, spec in services.items():
            if spec.get("image"):
                declaration.images.append(Declared(spec["image"], f"Compose service '{service}'", label))
            elif spec.get("build"):
                declaration.images.append(
                    Declared(f"{declaration.compose_project}-{service}", f"Compose-built service '{service}'", label)
                )
            if spec.get("container_name"):
                declaration.containers.append(spec["container_name"])
        declaration.volumes.extend(f"{declaration.compose_project}_{v}" for v in volumes)
    elif block.get("compose_project"):
        declaration.compose_project = block["compose_project"]

    for rel in block.get("dockerfiles", []):
        path = root / rel
        if not path.is_file():
            declaration.warnings.append(f"Dockerfile missing: {project}/{rel}")
            continue
        for base in dockerfile_bases(path):
            declaration.images.append(Declared(base, f"Dockerfile base ({rel})", rel))

    for image in block.get("images", []):
        source = image.get("source", "")
        declaration.images.append(Declared(image["ref"], image.get("purpose", ""), source))
        if source:
            path = root / source
            digest = parse_ref(image["ref"])[2]
            needle = digest or image["ref"]
            if not path.is_file():
                declaration.warnings.append(f"image source missing: {project}/{source}")
            elif needle not in path.read_text(encoding="utf-8", errors="ignore"):
                declaration.warnings.append(f"{image['ref']} not found in {source} (pin drift?)")

    declaration.volumes.extend(block.get("volumes", []))
    return declaration


def declare_external(entry: dict[str, Any]) -> ProjectDeclaration:
    return ProjectDeclaration(
        owner=entry["name"],
        kind="external",
        images=[Declared(ref, "external claim", entry.get("location", "")) for ref in entry.get("images", [])],
        volumes=list(entry.get("volumes", [])),
        containers=list(entry.get("containers", [])),
        compose_projects=list(entry.get("compose_projects", [])),
        notes=str(entry.get("notes", "")).strip(),
    )


# ---------------------------------------------------------------------------
# Docker state
# ---------------------------------------------------------------------------

_UNITS = {"B": 1, "kB": 1e3, "KB": 1e3, "MB": 1e6, "GB": 1e9, "TB": 1e12}


def parse_size(text: str | None) -> int:
    if not text or text in ("N/A", "-"):
        return 0
    match = re.match(r"^\s*([0-9.]+)\s*([kKMGT]?B)\s*$", str(text))
    if not match:
        return 0
    return int(float(match.group(1)) * _UNITS[match.group(2)])


def human(size: int) -> str:
    for unit, factor in (("GB", 1e9), ("MB", 1e6), ("kB", 1e3)):
        if size >= factor:
            return f"{size / factor:.2f} {unit}".replace(".00 ", " ")
    return f"{size} B"


def labels(text: str | None) -> dict[str, str]:
    result: dict[str, str] = {}
    for part in (text or "").split(","):
        if "=" in part:
            key, value = part.split("=", 1)
            result[key] = value
    return result


def normalise_repo(repo: str) -> str:
    for prefix in ("docker.io/library/", "docker.io/", "library/"):
        if repo.startswith(prefix):
            repo = repo[len(prefix):]
    return repo


def parse_ref(ref: str) -> tuple[str, str | None, str | None]:
    """Split ``repo[:tag][@sha256:digest]`` into (repo, tag, digest)."""
    digest = None
    if "@" in ref:
        ref, digest = ref.split("@", 1)
    tag = None
    last = ref.rsplit("/", 1)[-1]
    if ":" in last:
        ref, tag = ref.rsplit(":", 1)
    if tag is None and digest is None:
        tag = "latest"
    return normalise_repo(ref), tag, digest


def run_docker(*args: str) -> str:
    if tuple(args[:2]) not in READ_ONLY_DOCKER_COMMANDS and tuple(args[:1]) not in READ_ONLY_DOCKER_COMMANDS:
        raise InventoryError(f"refusing non-read-only Docker command: {' '.join(args)}")
    try:
        result = subprocess.run(
            ["docker", *args], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False
        )
    except OSError as exc:
        raise InventoryError(f"Docker could not be executed: {exc}") from exc
    if result.returncode != 0:
        raise InventoryError(f"docker {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def read_docker_state() -> dict[str, Any]:
    verbose = json.loads(run_docker("system", "df", "-v", "--format", "{{json .}}"))
    summary = [json.loads(line) for line in run_docker("system", "df", "--format", "{{json .}}").splitlines() if line.strip()]
    version = run_docker("version", "--format", "{{.Server.Version}}").strip()
    return {"verbose": verbose, "summary": summary, "server_version": version}


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

def image_matches(declared_ref: str, image: dict[str, Any]) -> bool:
    repo, tag, digest = parse_ref(declared_ref)
    image_id = str(image.get("ID", ""))
    if digest and (image_id == digest or str(image.get("Digest", "")) == digest):
        return True
    if digest and tag is None:
        return False
    image_repo = normalise_repo(str(image.get("Repository", "")))
    return image_repo == repo and str(image.get("Tag", "")) == (tag or "latest")


def build_inventory(registry: dict[str, Any], workspace: Path, state: dict[str, Any], now: datetime) -> dict[str, Any]:
    errors = validate_registry(registry)
    if errors:
        raise InventoryError("invalid docker registry data:\n  " + "\n  ".join(errors))

    declarations = [declare_project(row, workspace) for row in registry.get("projects") or [] if row.get("docker")]
    declarations += [declare_external(entry) for entry in registry.get("docker_external") or []]

    verbose = state["verbose"]
    images = verbose.get("Images") or []
    containers = verbose.get("Containers") or []
    volumes = verbose.get("Volumes") or []

    claimed_images: dict[str, set[str]] = {}
    claimed_containers: set[str] = set()
    claimed_volumes: set[str] = set()
    owners: list[dict[str, Any]] = []

    for decl in declarations:
        image_rows = []
        for declared in _dedupe(decl.images):
            found = [img for img in images if image_matches(declared.ref, img)]
            for img in found:
                claimed_images.setdefault(img["ID"], set()).add(decl.owner)
            image_rows.append(
                {
                    "ref": declared.ref,
                    "purpose": declared.purpose,
                    "source": declared.source,
                    "pinned": "@sha256:" in declared.ref,
                    "present": bool(found),
                    "id": found[0]["ID"][7:19] if found else "",
                    "size": parse_size(found[0].get("Size")) if found else 0,
                }
            )
        projects = set(decl.compose_projects) | ({decl.compose_project} if decl.compose_project else set())
        container_rows = []
        mounted: set[str] = set()
        for container in containers:
            lab = labels(container.get("Labels"))
            if lab.get("com.docker.compose.project") in projects or container.get("Names") in decl.containers:
                claimed_containers.add(container["Names"])
                mounted.update(m.strip() for m in str(container.get("Mounts") or "").split(",") if m.strip())
                container_rows.append(
                    {
                        "name": container["Names"],
                        "image": container.get("Image", ""),
                        "state": container.get("State", ""),
                        "status": container.get("Status", ""),
                        "size": parse_size(str(container.get("Size", "")).split(" ")[0]),
                    }
                )
        volume_rows = []
        for volume in volumes:
            lab = labels(volume.get("Labels"))
            # Anonymous volumes carry no Compose label; they belong to whoever owns the mounting container.
            if volume["Name"] in decl.volumes or lab.get("com.docker.compose.project") in projects or volume["Name"] in mounted:
                claimed_volumes.add(volume["Name"])
                volume_rows.append(
                    {"name": volume["Name"], "size": parse_size(volume.get("Size")), "links": int(volume.get("Links") or 0)}
                )
        declared_volume_rows = {row["name"] for row in volume_rows}
        missing_volumes = [v for v in decl.volumes if v not in declared_volume_rows]
        owners.append(
            {
                "owner": decl.owner,
                "kind": decl.kind,
                "compose_project": decl.compose_project,
                "notes": decl.notes,
                "warnings": decl.warnings,
                "images": image_rows,
                "containers": sorted(container_rows, key=lambda r: r["name"]),
                "volumes": sorted(volume_rows, key=lambda r: r["name"]),
                "volumes_not_present": missing_volumes,
                "space": sum(r["size"] for r in image_rows) + sum(r["size"] for r in volume_rows),
            }
        )

    shared = [
        {"image": _image_label(img), "id": img["ID"][7:19], "owners": sorted(claimed_images[img["ID"]])}
        for img in images
        if len(claimed_images.get(img["ID"], set())) > 1
    ]

    unclaimed_images = []
    for img in images:
        if img["ID"] in claimed_images:
            continue
        dangling = img.get("Tag") in ("<none>", "") or img.get("Repository") in ("<none>", "")
        in_use = int(img.get("Containers") or 0) > 0
        if in_use:
            action = "Docker counts a container against it; check which before removing."
        elif dangling:
            action = "Untagged and unused: usually an older pull or a superseded pin. Remove after review."
        else:
            action = "Declared by no project. Find its script or CI use and declare it, or remove it."
        unclaimed_images.append(
            {
                "image": _image_label(img),
                "id": img["ID"][7:19],
                "size": parse_size(img.get("Size")),
                "unique": parse_size(img.get("UniqueSize")),
                "created": img.get("CreatedSince", ""),
                "action": action,
            }
        )

    unclaimed_containers = [
        {
            "name": c["Names"],
            "image": c.get("Image", ""),
            "status": c.get("Status", ""),
            "action": "No project or external owner claims it. Inspect its labels and mounts before removing.",
        }
        for c in containers
        if c["Names"] not in claimed_containers
    ]

    unclaimed_volumes = []
    for volume in volumes:
        if volume["Name"] in claimed_volumes:
            continue
        attached = int(volume.get("Links") or 0) > 0
        anonymous = bool(ANONYMOUS_VOLUME.match(volume["Name"]))
        if attached:
            action = "Attached to a container; review that container first."
        elif anonymous:
            action = "Anonymous and not attached. Usually safe to remove after review."
        else:
            action = "Named volume declared by no project and not attached. It may hold data: check before removing."
        unclaimed_volumes.append(
            {"name": volume["Name"], "size": parse_size(volume.get("Size")), "links": int(volume.get("Links") or 0), "action": action}
        )

    summary = [
        {"type": row.get("Type"), "count": row.get("TotalCount"), "active": row.get("Active"), "size": row.get("Size"), "reclaimable": row.get("Reclaimable")}
        for row in state.get("summary", [])
    ]
    return {
        "generated": now.strftime("%Y-%m-%dT%H:%MZ"),
        "server_version": state.get("server_version", ""),
        "summary": summary,
        "owners": owners,
        "shared": shared,
        "unclaimed": {"images": unclaimed_images, "containers": unclaimed_containers, "volumes": unclaimed_volumes},
    }


def _dedupe(images: list[Declared]) -> list[Declared]:
    """Merge declarations of the same ref (for example two Compose services on one image)."""
    merged: dict[str, Declared] = {}
    for declared in images:
        if declared.ref in merged:
            existing = merged[declared.ref]
            if declared.purpose not in existing.purpose:
                existing.purpose = f"{existing.purpose}; {declared.purpose}"
        else:
            merged[declared.ref] = Declared(declared.ref, declared.purpose, declared.source)
    return list(merged.values())


def _image_label(img: dict[str, Any]) -> str:
    repo, tag = img.get("Repository", ""), img.get("Tag", "")
    return f"{repo}:{tag}" if tag and tag != "<none>" else f"{repo} (untagged)"


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _cell(text: Any) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def _volume_label(name: str) -> str:
    return f"{name[:12]}... (anonymous)" if ANONYMOUS_VOLUME.match(name) else name


def _short_ref(ref: str) -> str:
    repo, tag, digest = parse_ref(ref)
    text = f"{repo}:{tag}" if tag else repo
    return f"{text}@{digest[:19]}" if digest else text


def render_markdown(inv: dict[str, Any]) -> str:
    out: list[str] = []
    out.append(f"*Generated {inv['generated']} by `portfolio-prompts/tools/docker_inventory.py` (Docker Engine {inv['server_version']}). Do not edit this block by hand.*")
    out.append("")
    out.append("### Engine totals")
    out.append("")
    out.append("| Type | Count | Active | Size | Reclaimable |")
    out.append("|---|---|---|---|---|")
    for row in inv["summary"]:
        out.append(f"| {_cell(row['type'])} | {row['count']} | {row['active']} | {row['size']} | {_cell(row['reclaimable'])} |")
    out.append("")
    unclaimed = inv["unclaimed"]
    out.append(
        f"**Needs review:** {len(unclaimed['images'])} unclaimed image(s) "
        f"({human(sum(i['unique'] for i in unclaimed['images']))} unique), "
        f"{len(unclaimed['containers'])} unclaimed container(s), "
        f"{len(unclaimed['volumes'])} unclaimed volume(s) ({human(sum(v['size'] for v in unclaimed['volumes']))})."
    )
    out.append("")

    out.append("### By owner")
    out.append("")
    for owner in inv["owners"]:
        kind = "external owner" if owner["kind"] == "external" else "project"
        compose = f"; Compose project `{owner['compose_project']}`" if owner["compose_project"] else ""
        out.append(f"#### {owner['owner']} ({kind}{compose})")
        out.append("")
        if owner["notes"]:
            out.append(owner["notes"])
            out.append("")
        for warning in owner["warnings"]:
            out.append(f"> **Warning:** {warning}")
            out.append("")
        if owner["images"]:
            out.append("| Image | Pinned | Present | ID | Size | Purpose |")
            out.append("|---|---|---|---|---|---|")
            for row in owner["images"]:
                out.append(
                    f"| `{_cell(_short_ref(row['ref']))}` | {'yes' if row['pinned'] else 'no'} | "
                    f"{'yes' if row['present'] else 'no'} | {row['id'] or '-'} | {human(row['size']) if row['present'] else '-'} | {_cell(row['purpose'])} |"
                )
            out.append("")
        if owner["containers"]:
            out.append("| Container | Image | State |")
            out.append("|---|---|---|")
            for row in owner["containers"]:
                out.append(f"| `{row['name']}` | `{_cell(row['image'])}` | {_cell(row['status'])} |")
            out.append("")
        if owner["volumes"] or owner["volumes_not_present"]:
            out.append("| Volume | Size | Attached |")
            out.append("|---|---|---|")
            for row in owner["volumes"]:
                out.append(f"| `{_volume_label(row['name'])}` | {human(row['size'])} | {'yes' if row['links'] else 'no'} |")
            for name in owner["volumes_not_present"]:
                out.append(f"| `{name}` | not present | - |")
            out.append("")
        out.append(f"Space held (images listed above plus volumes; shared layers counted per image): **{human(owner['space'])}**")
        out.append("")

    if inv["shared"]:
        out.append("### Shared images")
        out.append("")
        out.append("Removing a shared image affects every owner listed.")
        out.append("")
        out.append("| Image | ID | Owners |")
        out.append("|---|---|---|")
        for row in inv["shared"]:
            out.append(f"| `{_cell(row['image'])}` | {row['id']} | {', '.join(row['owners'])} |")
        out.append("")

    out.append("### Unclaimed (review before any removal)")
    out.append("")
    if unclaimed["images"]:
        out.append("| Image | ID | Size (unique) | Created | Suggested action |")
        out.append("|---|---|---|---|---|")
        for row in sorted(unclaimed["images"], key=lambda r: -r["unique"]):
            out.append(f"| `{_cell(row['image'])}` | {row['id']} | {human(row['size'])} ({human(row['unique'])}) | {_cell(row['created'])} | {row['action']} |")
        out.append("")
    if unclaimed["containers"]:
        out.append("| Container | Image | Status | Suggested action |")
        out.append("|---|---|---|---|")
        for row in unclaimed["containers"]:
            out.append(f"| `{row['name']}` | `{_cell(row['image'])}` | {_cell(row['status'])} | {row['action']} |")
        out.append("")
    if unclaimed["volumes"]:
        out.append("| Volume | Size | Attached | Suggested action |")
        out.append("|---|---|---|---|")
        for row in sorted(unclaimed["volumes"], key=lambda r: -r["size"]):
            out.append(f"| `{_volume_label(row['name'])}` | {human(row['size'])} | {'yes' if row['links'] else 'no'} | {row['action']} |")
        out.append("")
    if not any(unclaimed.values()):
        out.append("Nothing unclaimed.")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def write_between_markers(path: Path, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    start, end = text.find(START_MARKER), text.find(END_MARKER)
    if start < 0 or end < start:
        raise InventoryError(f"{path} has no {START_MARKER} ... {END_MARKER} block")
    updated = text[: start + len(START_MARKER)] + "\n\n" + block + "\n" + text[end:]
    path.write_text(updated, encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only Docker inventory for the portfolio.")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--workspace", type=Path, default=DEFAULT_WORKSPACE)
    parser.add_argument("--json", action="store_true", help="emit the inventory as JSON")
    parser.add_argument("--write", type=Path, help="replace the generated block in this Markdown file")
    args = parser.parse_args(argv)
    try:
        registry = yaml.safe_load(args.registry.read_text(encoding="utf-8"))
        inventory = build_inventory(registry, args.workspace, read_docker_state(), datetime.now(timezone.utc))
        if args.json:
            print(json.dumps(inventory, indent=2))
        elif args.write:
            write_between_markers(args.write, render_markdown(inventory))
            print(f"docker-inventory: wrote {args.write}")
        else:
            print(render_markdown(inventory), end="")
    except (InventoryError, OSError, yaml.YAMLError) as exc:
        print(f"docker-inventory: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
