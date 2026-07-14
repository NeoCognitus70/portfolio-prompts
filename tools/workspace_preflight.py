#!/usr/bin/env python3
"""Read-only safety preflight for portfolio orchestration (PP-25 / portfolio P-06).

The command loads orchestration targets from ``registry.yml`` and inspects only local filesystem
state plus already-fetched Git references. It deliberately never contacts a remote or changes a
checkout. Run it from the portfolio root before any ``*-all-*`` fan-out.

Exit codes:
  0  all selected targets are READY or WARN only
  1  one or more selected targets are BLOCKED
  2  the registry or invocation could not be evaluated
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("workspace-preflight: PyYAML is required (pip install pyyaml)")


HERE = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = HERE / "registry.yml"
DEFAULT_WORKSPACE = HERE.parent

# Defence in depth: every Git call made by the inspector must use one of these read-only commands.
READ_ONLY_GIT_COMMANDS = frozenset(
    {"rev-parse", "rev-list", "show", "status", "symbolic-ref"}
)


class PreflightError(RuntimeError):
    """The preflight itself cannot produce a trustworthy target report."""


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    if not args or args[0] not in READ_ONLY_GIT_COMMANDS:
        raise PreflightError(f"refusing non-read-only Git command: {' '.join(args)}")
    env = os.environ.copy()
    env["GIT_OPTIONAL_LOCKS"] = "0"
    try:
        return subprocess.run(
            ["git", "--no-optional-locks", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            check=False,
        )
    except OSError as exc:
        raise PreflightError(f"Git could not be executed: {exc}") from exc


def _iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _handover_datetime(value: str) -> datetime:
    return datetime.strptime(value, "%Y%m%dT%H%MZ").replace(tzinfo=timezone.utc)


def _load_registry(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise PreflightError(f"registry is missing: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise PreflightError(f"registry is unreadable: {path}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("projects"), list):
        raise PreflightError("registry must contain a projects list")
    if not isinstance(data.get("defaults"), dict):
        raise PreflightError("registry must contain a defaults mapping")
    return data


def _select_targets(data: dict[str, Any], selected: list[str] | None) -> list[dict[str, Any]]:
    projects = data["projects"]
    if any(not isinstance(project, dict) for project in projects):
        raise PreflightError("every registry project row must be a mapping")
    targets = [p for p in projects if p.get("orchestration_target") is True]
    by_name = {p.get("project"): p for p in targets if isinstance(p.get("project"), str)}
    if not selected:
        return targets

    requested = list(dict.fromkeys(selected))
    invalid = [name for name in requested if name not in by_name]
    if invalid:
        raise PreflightError(
            "unknown or non-orchestration PROJECTS: " + ", ".join(invalid)
        )
    wanted = set(requested)
    return [p for p in targets if p["project"] in wanted]


def _parse_contract_gates(contract: Path) -> list[str]:
    commands: list[str] = []
    in_gates = False
    for raw in contract.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if re.match(r"^##\s+Gates\s*$", stripped, re.IGNORECASE):
            in_gates = True
            continue
        if in_gates and stripped.startswith("## "):
            break
        if not in_gates:
            continue
        if stripped.startswith("```"):
            continue
        if not stripped or stripped.startswith("#"):
            continue
        command = re.sub(r"^(?:[-*]|\d+[.)])\s+", "", stripped)
        if command:
            commands.append(command)
    return commands


def _registry_gate_steps(gates: Any) -> list[str]:
    if isinstance(gates, list):
        return [str(command) for command in gates if str(command).strip()]
    if not isinstance(gates, dict):
        return []

    gate_type = gates.get("type")
    if gate_type == "docs_only":
        return ["docs-only validation (link/grep checks; no build)"]
    if gate_type == "ci_jobs":
        steps = [
            f"CI job {stack.get('name')}: {stack.get('tool')}/{stack.get('language')}"
            for stack in gates.get("stacks", [])
        ]
        if gates.get("parity_scripts"):
            steps.append(f"parity scripts matching {gates['parity_scripts']}")
        return steps
    if gate_type == "ci":
        steps = [str(command) for command in gates.get("static", [])]
        e2e = gates.get("e2e") or {}
        for key in ("bring_up", "run"):
            if e2e.get(key):
                steps.append(str(e2e[key]))
        return steps
    return [json.dumps(gates, sort_keys=True)]


def _resolve_gates(
    repo: Path, project: dict[str, Any], defaults: dict[str, Any]
) -> tuple[str, list[str]]:
    deviations = project.get("deviations") or {}
    if not isinstance(deviations, dict):
        raise PreflightError(
            f"registry deviations for '{project.get('project')}' must be a mapping"
        )
    contract_rel = deviations.get("project_contract", defaults.get("project_contract"))
    if contract_rel:
        contract = repo / str(contract_rel)
        if contract.is_file():
            commands = _parse_contract_gates(contract)
            if commands:
                return f"project contract ({contract_rel})", commands

    commands = _registry_gate_steps(project.get("gates"))
    if commands:
        return "registry.yml project gates", commands

    package_json = repo / "package.json"
    if package_json.is_file():
        try:
            package = json.loads(package_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            package = {}
        if isinstance(package.get("scripts"), dict) and package["scripts"].get("verify"):
            return "package.json verify script", ["npm run verify"]

    defaults_found: list[str] = []
    if (repo / "tsconfig.json").is_file():
        defaults_found.append("npx tsc --noEmit")
    cucumber_configs = ("cucumber.js", "cucumber.json", "cucumber.yaml", "cucumber.yml")
    if any((repo / name).is_file() for name in cucumber_configs):
        defaults_found.append("npx cucumber-js --profile default --dry-run")
    if defaults_found:
        return "stack defaults", defaults_found
    return "unresolved", ["ASK: no validation gate is recorded"]


def _find_default_ref(repo: Path, upstream: str | None) -> str | None:
    remote = upstream.split("/", 1)[0] if upstream and "/" in upstream else "origin"
    symbolic = _git(
        repo, "symbolic-ref", "--quiet", "--short", f"refs/remotes/{remote}/HEAD"
    )
    if symbolic.returncode == 0 and symbolic.stdout.strip():
        return symbolic.stdout.strip()

    candidates = [f"{remote}/main", f"{remote}/master"]
    if upstream and upstream.rsplit("/", 1)[-1] in {"main", "master"}:
        candidates.insert(0, upstream)
    for candidate in dict.fromkeys(candidates):
        result = _git(repo, "rev-parse", "--verify", "--quiet", f"{candidate}^{{commit}}")
        if result.returncode == 0:
            return candidate
    return None


def _inspect_handover(
    session_notes: Path,
    project_name: str,
    default_head_time: str | None,
    warnings: list[str],
) -> dict[str, Any]:
    pattern = re.compile(
        rf"^{re.escape(project_name)}_session-notes_v(?P<version>\d+)_"
        rf"(?P<created>\d{{8}}T\d{{4}}Z)\.md$"
    )
    candidates: list[tuple[int, datetime, Path]] = []
    if session_notes.is_dir():
        for path in session_notes.iterdir():
            match = pattern.match(path.name)
            if match and path.is_file():
                try:
                    created = _handover_datetime(match["created"])
                except ValueError:
                    warnings.append(f"ignored handover with invalid timestamp: {path.name}")
                    continue
                candidates.append(
                    (
                        int(match["version"]),
                        created,
                        path,
                    )
                )

    if not candidates:
        warnings.append("latest handover is missing")
        return {
            "version": None,
            "markdown": None,
            "html": None,
            "paired": False,
            "created": None,
            "freshness": "missing",
        }

    version, created, markdown = max(candidates, key=lambda item: (item[0], item[1]))
    html = markdown.with_suffix(".html")
    paired = html.is_file()
    if not paired:
        warnings.append(f"latest handover v{version} has no HTML companion")

    freshness = "unknown"
    if default_head_time:
        if created < _iso_datetime(default_head_time):
            freshness = "stale"
            warnings.append(
                f"latest handover v{version} predates fetched default head"
            )
        else:
            freshness = "current"
    else:
        warnings.append("handover freshness is unknown because no fetched default head is available")

    return {
        "version": version,
        "markdown": f"session-notes/{markdown.name}",
        "html": f"session-notes/{html.name}" if paired else None,
        "paired": paired,
        "created": created.isoformat().replace("+00:00", "Z"),
        "freshness": freshness,
    }


def _inspect_project(
    workspace: Path,
    session_notes: Path,
    defaults: dict[str, Any],
    project: dict[str, Any],
) -> dict[str, Any]:
    name = project.get("project")
    if not isinstance(name, str) or not name:
        raise PreflightError("every orchestration target must have a project name")

    repo = workspace / name
    blockers: list[str] = []
    warnings: list[str] = []
    folder_present = repo.is_dir()
    git_info: dict[str, Any] = {
        "readable": False,
        "branch": None,
        "dirty": None,
        "upstream": None,
        "ahead": None,
        "behind": None,
        "fetched_default_ref": None,
        "fetched_default_head": None,
        "fetched_default_head_time": None,
    }

    if not folder_present:
        blockers.append("repository folder is missing")
    elif not (repo / ".git").exists():
        blockers.append("folder is not an independent Git checkout")
    else:
        inside = _git(repo, "rev-parse", "--is-inside-work-tree")
        if inside.returncode != 0 or inside.stdout.strip() != "true":
            blockers.append("Git state is unreadable")
        else:
            git_info["readable"] = True

            branch = _git(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
            if branch.returncode == 0:
                git_info["branch"] = branch.stdout.strip()
            else:
                detached = _git(repo, "rev-parse", "--short", "HEAD")
                if detached.returncode == 0:
                    git_info["branch"] = f"<detached@{detached.stdout.strip()}>"
                    warnings.append("checkout is at a detached HEAD")
                else:
                    blockers.append("current branch/HEAD is unreadable")

            dirty = _git(repo, "status", "--porcelain=v1", "--untracked-files=normal")
            if dirty.returncode != 0:
                blockers.append("dirty state is unreadable")
            else:
                git_info["dirty"] = bool(dirty.stdout.strip())
                if git_info["dirty"]:
                    blockers.append("working tree has uncommitted or untracked changes")

            upstream = _git(
                repo,
                "rev-parse",
                "--abbrev-ref",
                "--symbolic-full-name",
                "@{upstream}",
            )
            if upstream.returncode == 0:
                git_info["upstream"] = upstream.stdout.strip()
                counts = _git(repo, "rev-list", "--left-right", "--count", "HEAD...@{upstream}")
                if counts.returncode == 0:
                    try:
                        ahead, behind = (int(value) for value in counts.stdout.split())
                    except (TypeError, ValueError):
                        blockers.append("ahead/behind counts are unreadable")
                    else:
                        git_info["ahead"] = ahead
                        git_info["behind"] = behind
                        if ahead:
                            warnings.append(f"checkout is {ahead} commit(s) ahead of upstream")
                        if behind:
                            warnings.append(f"checkout is {behind} commit(s) behind upstream")
                else:
                    blockers.append("ahead/behind counts are unreadable")
            else:
                warnings.append("current branch has no upstream")

            default_ref = _find_default_ref(repo, git_info["upstream"])
            git_info["fetched_default_ref"] = default_ref
            if default_ref:
                head = _git(repo, "rev-parse", "--verify", f"{default_ref}^{{commit}}")
                head_time = _git(repo, "show", "-s", "--format=%cI", default_ref)
                if head.returncode == 0 and head_time.returncode == 0:
                    git_info["fetched_default_head"] = head.stdout.strip()
                    git_info["fetched_default_head_time"] = head_time.stdout.strip()
                else:
                    warnings.append("fetched default head metadata is unreadable")
                default_branch = default_ref.split("/", 1)[-1]
                branch_name = git_info["branch"]
                if branch_name and not branch_name.startswith("<detached"):
                    if branch_name != default_branch:
                        warnings.append(
                            f"checkout is on topic branch '{branch_name}' (default: '{default_branch}')"
                        )
            else:
                warnings.append("no fetched default-branch reference is available")

    deviations = project.get("deviations") or {}
    if not isinstance(deviations, dict):
        raise PreflightError(f"registry deviations for '{name}' must be a mapping")
    backlog_rel = deviations.get("backlog", defaults.get("backlog"))
    backlog_path = repo / str(backlog_rel) if backlog_rel else None
    backlog_present = bool(backlog_path and backlog_path.is_file())
    if not backlog_rel:
        blockers.append("registry has no authoritative backlog path")
    elif not backlog_present:
        blockers.append(f"authoritative backlog is missing: {backlog_rel}")

    try:
        gate_source, gate_commands = _resolve_gates(repo, project, defaults)
    except OSError as exc:
        gate_source, gate_commands = "unreadable", []
        blockers.append(f"validation gate source is unreadable: {exc}")
    if gate_source == "unresolved":
        warnings.append("validation gate source is unresolved")

    handover = _inspect_handover(
        session_notes,
        name,
        git_info["fetched_default_head_time"],
        warnings,
    )

    return {
        "project": name,
        "folder": str(repo),
        "folder_present": folder_present,
        "git": git_info,
        "backlog": {"path": str(backlog_rel) if backlog_rel else None, "present": backlog_present},
        "gates": {"source": gate_source, "commands": gate_commands},
        "handover": handover,
        "blockers": blockers,
        "warnings": warnings,
        "status": "BLOCKED" if blockers else ("WARN" if warnings else "READY"),
    }


def inspect_workspace(
    registry_path: Path = DEFAULT_REGISTRY,
    workspace: Path = DEFAULT_WORKSPACE,
    selected: list[str] | None = None,
) -> dict[str, Any]:
    registry_path = registry_path.resolve()
    workspace = workspace.resolve()
    data = _load_registry(registry_path)
    targets = _select_targets(data, selected)
    reports = [
        _inspect_project(workspace, workspace / "session-notes", data["defaults"], project)
        for project in targets
    ]
    return {
        "registry": str(registry_path),
        "workspace": str(workspace),
        "read_only": True,
        "target_count": len(reports),
        "blocker_count": sum(len(report["blockers"]) for report in reports),
        "warning_count": sum(len(report["warnings"]) for report in reports),
        "targets": reports,
    }


def _show(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    return str(value)


def print_report(report: dict[str, Any]) -> None:
    overall = "BLOCKED" if report["blocker_count"] else (
        "WARN" if report["warning_count"] else "READY"
    )
    print(
        f"Workspace preflight: {overall} ({report['target_count']} target(s), "
        f"{report['blocker_count']} blocker(s), {report['warning_count']} warning(s))"
    )
    print("Policy: read-only; local files and already-fetched Git refs only; no network refresh")
    for target in report["targets"]:
        git = target["git"]
        handover = target["handover"]
        print(f"\n[{target['status']}] {target['project']}")
        print(f"  folder: {_show(target['folder_present'])} | {target['folder']}")
        print(
            "  git: "
            f"branch={_show(git['branch'])}; dirty={_show(git['dirty'])}; "
            f"upstream={_show(git['upstream'])}; ahead={_show(git['ahead'])}; "
            f"behind={_show(git['behind'])}"
        )
        print(
            "  fetched default: "
            f"ref={_show(git['fetched_default_ref'])}; "
            f"head={_show(git['fetched_default_head'])}; "
            f"time={_show(git['fetched_default_head_time'])}"
        )
        backlog = target["backlog"]
        print(f"  backlog: {_show(backlog['present'])} | {_show(backlog['path'])}")
        print(
            f"  gates: {target['gates']['source']} | "
            + "; ".join(target["gates"]["commands"])
        )
        print(
            "  handover: "
            f"v{_show(handover['version'])}; paired={_show(handover['paired'])}; "
            f"freshness={handover['freshness']}; md={_show(handover['markdown'])}; "
            f"html={_show(handover['html'])}"
        )
        for blocker in target["blockers"]:
            print(f"  BLOCKER: {blocker}")
        for warning in target["warnings"]:
            print(f"  WARNING: {warning}")


def _parse_projects(value: str | None) -> list[str] | None:
    if value is None:
        return None
    projects = [item.strip() for item in value.split(",") if item.strip()]
    if not projects:
        raise argparse.ArgumentTypeError("--projects must contain at least one folder name")
    return projects


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--projects",
        help="comma-separated orchestration-target subset; default is every registry target",
    )
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--workspace", type=Path, default=DEFAULT_WORKSPACE)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)
    try:
        selected = _parse_projects(args.projects)
        report = inspect_workspace(args.registry, args.workspace, selected)
    except (PreflightError, argparse.ArgumentTypeError) as exc:
        print(f"workspace-preflight: BLOCKED — {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_report(report)
    return 1 if report["blocker_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
