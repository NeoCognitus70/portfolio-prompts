#!/usr/bin/env python3
"""Self-gate for the portfolio-prompts library (PP-15).

The library previously had no real gate ("docs-only, link/grep"). This asserts the library's own
invariants so a broken registry, a dangling doc link, a stale README table, or a malformed worklist
example is caught before merge — the same discipline the library imposes on the projects it serves.

Checks:
  1. Registry folders   — every `project` maps to a real folder, and every sibling repository is
                          either a project or an explicitly classified support repository.
  2. Registry semantics — lifecycle labels and presentation roles are valid, resting projects
                          remain orchestration targets, and support repositories cannot enter
                          project fan-outs.
  3. README generated   — the README registry table is up to date w.r.t. registry.yml
                          (delegates to `render-registry.py --check`).
  4. CI workflow        — the self-gate runs on PRs/main pushes with read-only permissions.
  5. Internal links     — every relative Markdown link in the library's own docs resolves.
  6. Release metadata   — backlog state is internally consistent and Claude/Codex manifest
                          versions identify the same release.
  7. Codex plugin       — the Codex manifest and per-skill UI/invocation policies are complete,
                          including the runtime maximum of three suggested prompts.
  8. Working norms      — the universal branch/PR policy is defined once in project-layout.md and
                          is not restated in operational prompts or skill bodies.
  9. Invocation paths   — active invocation examples use OS-neutral forward slashes.
 10. Worklist example   — the canonical example in project-layout.md parses as the documented format.
 11. Workspace preflight — deterministic clean/dirty/behind/topic/missing-evidence scenarios pass.
 12. Handover pairs     — every root session-notes Markdown handover has its HTML companion
                          (P-09; skipped in a standalone clone with no sibling session-notes/).
 13. Kanban generator   — the shared tools/kanban generator's Node test suite passes: the
                          derive-status truth table, backlog adapters, override validation, and
                          the drift-gate over committed fixtures (skipped if Node is absent).

Usage (from the portfolio-prompts/ directory):
    python tools/check-library.py            # exit 0 if all checks pass, 1 otherwise

Requires PyYAML (`pip install pyyaml`). No other dependencies.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("check-library: PyYAML is required (pip install pyyaml)")

HERE = Path(__file__).resolve().parent.parent          # portfolio-prompts/
PORTFOLIO_ROOT = HERE.parent                            # test-automation-portfolio/
REGISTRY = HERE / "registry.yml"

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
ALLOWED_STATUSES = {"active", "resting", "meta"}
ALLOWED_PRESENTATION_ROLES = {"showcase", "methodology", "hidden"}
BACKLOG_ITEM_RE = re.compile(r"^#{3,4} (PP-\d+):", re.MULTILINE)
CODEX_VERSION_RE = re.compile(r"^(?P<base>[^+]+)\+codex\.(?P<cachebuster>[a-z0-9-]+)$")

# Markdown files that are the library's own docs (exclude node_modules and vendored trees).
def library_docs() -> list[Path]:
    docs: list[Path] = []
    for pattern in ("*.md", "*.prompt.md", "docs/*.md", "proposals/**/*.md", "tools/*.md",
                    "skills/**/*.md"):
        docs.extend(HERE.glob(pattern))
    seen, out = set(), []
    for p in docs:
        if "node_modules" in p.parts:
            continue
        if p not in seen:
            seen.add(p)
            out.append(p)
    return sorted(out)


def check_registry_folders(fails: list[str]) -> None:
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))

    def folder_for(name: str) -> Path:
        return HERE if name == "portfolio-prompts" else PORTFOLIO_ROOT / name

    present = {p["project"]: folder_for(p["project"]).is_dir() for p in data["projects"]}
    # Standalone clone of just the library (no sibling checkouts) — cross-repo checks don't apply.
    if not any(v for k, v in present.items() if k != "portfolio-prompts"):
        print("check-library: note — no sibling checkouts present; skipping cross-repo folder checks.")
        return

    for p in data["projects"]:
        if not present[p["project"]]:
            fails.append(f"[registry-folders] project '{p['project']}' has no folder at {folder_for(p['project'])}")

    # Drift watch: every sibling repo must be a project, a classified support repository, or an
    # explicitly acknowledged candidate awaiting a decision.
    support = {s["folder"] for s in data.get("support_repositories") or []}
    known = set(present) | support | set(data.get("unregistered_candidates") or [])
    for child in sorted(PORTFOLIO_ROOT.iterdir()):
        if child.is_dir() and (child / ".git").exists() and child.name not in known:
            fails.append(
                f"[registry-folders] workspace repo '{child.name}' is unclassified — register it "
                "as a project, support repository, or explicit candidate in registry.yml"
            )


def validate_project_registry_rows(projects: list[dict]) -> list[str]:
    """Return semantic failures for project rows without reading repository state."""
    fails: list[str] = []
    for project in projects:
        name = project["project"]
        status = project.get("status")
        if status not in ALLOWED_STATUSES:
            fails.append(
                f"[registry-semantics] project '{name}' has unsupported status '{status}'"
            )
        role = project.get("presentation_role")
        if not isinstance(role, str) or role not in ALLOWED_PRESENTATION_ROLES:
            allowed = ", ".join(sorted(ALLOWED_PRESENTATION_ROLES))
            fails.append(
                f"[registry-semantics] project '{name}' must declare presentation_role as one "
                f"of: {allowed}"
            )
        if not isinstance(project.get("orchestration_target"), bool):
            fails.append(
                f"[registry-semantics] project '{name}' must declare orchestration_target as boolean"
            )
        if status == "resting" and project.get("orchestration_target") is not True:
            fails.append(
                f"[registry-semantics] resting project '{name}' must remain an orchestration target"
            )
        if status == "meta" and project.get("orchestration_target") is not False:
            fails.append(
                f"[registry-semantics] meta project '{name}' cannot be an orchestration target"
            )
    return fails


def check_registry_semantics(fails: list[str]) -> None:
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    projects = data["projects"]
    project_names = {p["project"] for p in projects}
    fails.extend(validate_project_registry_rows(projects))

    readme = (HERE / "README.md").read_text(encoding="utf-8")
    support_folders: set[str] = set()
    for support in data.get("support_repositories") or []:
        missing = [key for key in ("folder", "github", "role", "status", "orchestration_target")
                   if key not in support]
        if missing:
            fails.append(
                "[registry-semantics] support repository is missing: " + ", ".join(missing)
            )
            continue
        folder = support["folder"]
        support_folders.add(folder)
        if folder in project_names:
            fails.append(
                f"[registry-semantics] support repository '{folder}' duplicates a PROJECT row"
            )
        if support["orchestration_target"] is not False:
            fails.append(
                f"[registry-semantics] support repository '{folder}' cannot be an orchestration target"
            )
        if support["status"] not in ALLOWED_STATUSES:
            fails.append(
                f"[registry-semantics] support repository '{folder}' has unsupported status "
                f"'{support['status']}'"
            )
        if f"`{folder}`" not in readme or support["github"] not in readme:
            fails.append(
                f"[registry-semantics] README does not expose support classification for '{folder}'"
            )

    if len(support_folders) != len(data.get("support_repositories") or []):
        fails.append("[registry-semantics] support repository folders must be unique")


def check_readme_generated(fails: list[str]) -> None:
    r = subprocess.run(
        [sys.executable, str(HERE / "tools" / "render-registry.py"), "--check"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        fails.append("[readme-generated] " + (r.stdout.strip() or "README table is stale"))


def check_ci_workflow(fails: list[str]) -> None:
    workflow_path = HERE / ".github" / "workflows" / "library-integrity.yml"
    if not workflow_path.is_file():
        fails.append("[ci-workflow] missing .github/workflows/library-integrity.yml")
        return

    try:
        workflow = yaml.load(
            workflow_path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader
        )
    except yaml.YAMLError as exc:
        fails.append(f"[ci-workflow] invalid YAML: {exc}")
        return
    if not isinstance(workflow, dict):
        fails.append("[ci-workflow] workflow root must be a mapping")
        return

    triggers = workflow.get("on") or {}
    if not isinstance(triggers, dict):
        fails.append("[ci-workflow] on must be a mapping")
        triggers = {}
    if set(triggers) != {"pull_request", "push"}:
        fails.append("[ci-workflow] triggers must be exactly pull_request and push")
    push = triggers.get("push") or {}
    if not isinstance(push, dict) or push.get("branches") != ["main"]:
        fails.append("[ci-workflow] push trigger must be limited to main")
    if workflow.get("permissions") != {"contents": "read"}:
        fails.append("[ci-workflow] permissions must be exactly contents: read")

    steps = (((workflow.get("jobs") or {}).get("verify") or {}).get("steps") or [])
    uses = {step.get("uses") for step in steps if step.get("uses")}
    runs = {step.get("run") for step in steps if step.get("run")}
    if "actions/checkout@v7" not in uses or "actions/setup-python@v6" not in uses:
        fails.append("[ci-workflow] workflow must use the approved checkout/setup-python majors")
    if "python tools/check-library.py" not in runs:
        fails.append("[ci-workflow] workflow does not run python tools/check-library.py")
    checkout = next((step for step in steps if step.get("uses") == "actions/checkout@v7"), {})
    if (checkout.get("with") or {}).get("persist-credentials") != "false":
        fails.append("[ci-workflow] checkout must disable persisted credentials")


def check_internal_links(fails: list[str]) -> None:
    for md in library_docs():
        text = md.read_text(encoding="utf-8")
        for target in LINK_RE.findall(text):
            t = target.strip()
            if t.startswith(("http://", "https://", "mailto:", "#")):
                continue
            t = t.split("#", 1)[0].split(" ", 1)[0].strip()   # drop anchor / title
            if not t:
                continue
            # Skip illustrative placeholders (e.g. `path/to/filename.ext`, `{PROJECT}`, `<repo>`).
            if any(c in t for c in "<>{}") or t.startswith("path/to") or "owner/repo" in t:
                continue
            if not (md.parent / t).exists():
                fails.append(f"[internal-links] {md.relative_to(HERE)} -> missing '{t}'")


def check_skills(fails: list[str]) -> None:
    skills_dir = HERE / "skills"
    if not skills_dir.is_dir():
        return
    for skill in sorted(skills_dir.glob("*/SKILL.md")):
        text = skill.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
        if not m:
            fails.append(f"[skills] {skill.relative_to(HERE)} has no YAML frontmatter block")
            continue
        front, body = m.group(1), m.group(2)
        try:
            front_data = yaml.safe_load(front) or {}
        except yaml.YAMLError as e:
            fails.append(f"[skills] {skill.relative_to(HERE)} frontmatter is not valid YAML: {e}")
            continue
        for key in ("name", "description"):
            if not front_data.get(key):
                fails.append(f"[skills] {skill.relative_to(HERE)} frontmatter missing '{key}'")
        unexpected = set(front_data) - {"name", "description"}
        if unexpected:
            fails.append(
                f"[skills] {skill.relative_to(HERE)} has non-portable frontmatter keys: "
                + ", ".join(sorted(unexpected))
            )
        description = front_data.get("description") or ""
        if "<" in description or ">" in description:
            fails.append(
                f"[skills] {skill.relative_to(HERE)} description contains angle brackets"
            )
        if front_data.get("name") and front_data["name"] != skill.parent.name:
            fails.append(
                f"[skills] {skill.relative_to(HERE)} name '{front_data['name']}' != folder "
                f"'{skill.parent.name}'"
            )
        # A thin-wrapper skill must delegate to a prompt file that exists at the repo root.
        for prompt in re.findall(r"([A-Za-z0-9_-]+(?:\.prompt)?\.md)", body):
            if prompt.endswith(".prompt.md") or prompt == "github-repo-analysis-prompt.md":
                if not (HERE / prompt).exists():
                    fails.append(f"[skills] {skill.relative_to(HERE)} delegates to missing '{prompt}'")


def validate_backlog_consistency(text: str) -> list[str]:
    """Return failures when backlog sections, statuses, and summary counts disagree."""
    fails: list[str] = []
    outstanding_marker = "## Outstanding Items"
    risk_marker = "## Risk Summary"
    resolved_marker = "## Resolved Items"
    if outstanding_marker not in text or risk_marker not in text or resolved_marker not in text:
        return ["[release-metadata] backlog must contain Outstanding, Risk Summary, and Resolved sections"]

    outstanding = text.split(outstanding_marker, 1)[1].split(risk_marker, 1)[0]
    risk = text.split(risk_marker, 1)[1].split(resolved_marker, 1)[0]
    resolved = text.split(resolved_marker, 1)[1]
    outstanding_ids = re.findall(r"^### (PP-\d+):", outstanding, re.MULTILINE)
    resolved_ids = re.findall(r"^#### (PP-\d+):", resolved, re.MULTILINE)

    all_ids = BACKLOG_ITEM_RE.findall(text)
    duplicates = sorted({item_id for item_id in all_ids if all_ids.count(item_id) > 1})
    if duplicates:
        fails.append(
            "[release-metadata] backlog item IDs must be unique: " + ", ".join(duplicates)
        )

    blocks = re.split(r"(?=^### PP-\d+:)", outstanding, flags=re.MULTILINE)[1:]
    for block in blocks:
        item_id = re.match(r"^### (PP-\d+):", block).group(1)
        status = re.search(r"^\*\*Status:\*\*\s*(.+)$", block, re.MULTILINE)
        if status is None:
            fails.append(f"[release-metadata] outstanding item {item_id} has no Status field")
        elif re.search(r"\b(resolved|complete|closed)\b", status.group(1), re.IGNORECASE):
            fails.append(
                f"[release-metadata] outstanding item {item_id} has terminal status "
                f"'{status.group(1).strip()}'"
            )

    total = re.search(
        r"^\| \*\*Total Outstanding\*\* \| \*\*(\d+)\*\* \|", risk, re.MULTILINE
    )
    if total is None or int(total.group(1)) != len(outstanding_ids):
        stated = total.group(1) if total else "missing"
        fails.append(
            f"[release-metadata] Total Outstanding is {stated}; found {len(outstanding_ids)} item(s)"
        )

    resolved_total = re.search(r"^\| Resolved \| (\d+) \|", risk, re.MULTILINE)
    if resolved_total is None or int(resolved_total.group(1)) != len(resolved_ids):
        stated = resolved_total.group(1) if resolved_total else "missing"
        fails.append(
            f"[release-metadata] Resolved is {stated}; found {len(resolved_ids)} resolved item(s)"
        )

    order = re.search(r"^\*\*Outstanding, by suggested order:\*\*\s*(.+)$", risk, re.MULTILINE)
    ordered_ids = re.findall(r"PP-\d+", order.group(1)) if order else []
    if ordered_ids != outstanding_ids:
        fails.append(
            "[release-metadata] suggested-order IDs must exactly match Outstanding Items"
        )
    return fails


def validate_plugin_manifest_versions(claude: dict, codex: dict) -> list[str]:
    """Return failures when the two plugin manifests identify different releases."""
    fails: list[str] = []
    claude_version = claude.get("version")
    codex_version = codex.get("version")
    if not isinstance(claude_version, str) or not claude_version:
        fails.append("[release-metadata] Claude plugin manifest has no version")
        return fails
    if not isinstance(codex_version, str) or not codex_version:
        fails.append("[release-metadata] Codex plugin manifest has no version")
        return fails
    match = CODEX_VERSION_RE.fullmatch(codex_version)
    if match is None:
        fails.append(
            "[release-metadata] Codex version must be '<release>+codex.<cachebuster>'"
        )
    elif match.group("base") != claude_version:
        fails.append(
            f"[release-metadata] manifest release mismatch: Claude {claude_version}, "
            f"Codex {match.group('base')}"
        )
    return fails


def validate_codex_default_prompts(interface: dict) -> list[str]:
    """Return failures when suggested prompts cannot be ingested by Codex."""
    prompts = interface.get("defaultPrompt")
    if not isinstance(prompts, list) or not prompts:
        return ["[codex-plugin] interface.defaultPrompt must be a non-empty list"]
    if len(prompts) > 3:
        return [
            "[codex-plugin] interface.defaultPrompt has "
            f"{len(prompts)} entries; Codex supports a maximum of 3"
        ]
    if any(not isinstance(prompt, str) or not prompt.strip() for prompt in prompts):
        return ["[codex-plugin] interface.defaultPrompt entries must be non-empty strings"]
    return []


# Prompts that deliberately ship without a skills/<name>/ wrapper, mapped to the reason.
# Record an exception here rather than letting a missing wrapper pass silently: a lifecycle
# prompt with no wrapper is *invisible* to a skill-driven agent, not merely undeclared, so the
# stage it documents gets skipped rather than declined (PP-39).
PROMPT_SKILL_EXCEPTIONS: dict[str, str] = {}


def prompt_skill_coverage_failures(
    prompt_stems: set[str], skill_names: set[str], exceptions: dict[str, str]
) -> list[str]:
    """Return a failure for every prompt with neither a skill wrapper nor a recorded exception.

    Also flags stale bookkeeping in the exception map, so it cannot quietly outlive the gap it
    was written for.
    """
    fails: list[str] = []
    for stem in sorted(prompt_stems):
        if stem in skill_names or stem in exceptions:
            continue
        fails.append(
            f"[skills] '{stem}.prompt.md' has no skills/{stem}/ wrapper, so a skill-driven agent "
            "cannot discover it; add the wrapper or record it in PROMPT_SKILL_EXCEPTIONS"
        )
    for stem in sorted(exceptions):
        if stem in skill_names:
            fails.append(
                f"[skills] '{stem}' is recorded in PROMPT_SKILL_EXCEPTIONS but now has a skill "
                "wrapper; remove the stale exception"
            )
        elif stem not in prompt_stems:
            fails.append(
                f"[skills] PROMPT_SKILL_EXCEPTIONS names '{stem}', which is not a prompt file"
            )
    return fails


def check_prompt_skill_coverage(fails: list[str]) -> None:
    """Every canonical prompt must be reachable as a skill (the reverse of check_skills)."""
    suffix = ".prompt.md"
    prompt_stems = {p.name[: -len(suffix)] for p in HERE.glob("*" + suffix)}
    skills_dir = HERE / "skills"
    skill_names = (
        {s.parent.name for s in skills_dir.glob("*/SKILL.md")} if skills_dir.is_dir() else set()
    )
    fails.extend(
        prompt_skill_coverage_failures(prompt_stems, skill_names, PROMPT_SKILL_EXCEPTIONS)
    )


def check_release_metadata(fails: list[str]) -> None:
    backlog = (HERE / "docs" / "backlog.md").read_text(encoding="utf-8")
    fails.extend(validate_backlog_consistency(backlog))
    try:
        claude = json.loads((HERE / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        codex = json.loads((HERE / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fails.append(f"[release-metadata] cannot read plugin manifests: {exc}")
        return
    fails.extend(validate_plugin_manifest_versions(claude, codex))


def check_codex_plugin(fails: list[str]) -> None:
    manifest_path = HERE / ".codex-plugin" / "plugin.json"
    if not manifest_path.is_file():
        fails.append("[codex-plugin] missing .codex-plugin/plugin.json")
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fails.append(f"[codex-plugin] invalid plugin manifest: {exc}")
        return

    for key in ("name", "version", "description", "author", "skills", "interface"):
        if not manifest.get(key):
            fails.append(f"[codex-plugin] plugin.json missing '{key}'")
    if manifest.get("name") != HERE.name:
        fails.append("[codex-plugin] plugin name must match the repository folder")
    if manifest.get("skills") != "./skills/":
        fails.append("[codex-plugin] plugin skills path must be './skills/'")

    interface = manifest.get("interface") or {}
    for key in (
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
        "capabilities",
        "defaultPrompt",
    ):
        if not interface.get(key):
            fails.append(f"[codex-plugin] plugin interface missing '{key}'")
    fails.extend(validate_codex_default_prompts(interface))

    marketplace_path = HERE / ".agents" / "plugins" / "marketplace.json"
    if not marketplace_path.is_file():
        fails.append("[codex-plugin] missing .agents/plugins/marketplace.json")
    else:
        try:
            marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            fails.append(f"[codex-plugin] invalid marketplace: {exc}")
        else:
            entries = marketplace.get("plugins") or []
            entry = next(
                (item for item in entries if item.get("name") == "portfolio-prompts"),
                None,
            )
            if entry is None:
                fails.append("[codex-plugin] marketplace has no portfolio-prompts entry")
            else:
                source = entry.get("source") or {}
                if source != {"source": "local", "path": "./"}:
                    fails.append("[codex-plugin] marketplace source must target the repository root")
                policy = entry.get("policy") or {}
                if policy.get("installation") != "AVAILABLE":
                    fails.append("[codex-plugin] marketplace installation policy must be AVAILABLE")
                if policy.get("authentication") != "ON_INSTALL":
                    fails.append("[codex-plugin] marketplace authentication policy must be ON_INSTALL")
                if not entry.get("category"):
                    fails.append("[codex-plugin] marketplace entry must declare a category")

    explicit_only = {
        "close-project",
        "loop-all-worklists",
        "loop-worklist",
        "onboard-project",
        "review-all-projects",
    }
    for skill_dir in sorted((HERE / "skills").iterdir()):
        if not skill_dir.is_dir():
            continue
        agent_path = skill_dir / "agents" / "openai.yaml"
        if not agent_path.is_file():
            fails.append(f"[codex-plugin] {skill_dir.name} missing agents/openai.yaml")
            continue
        try:
            agent = yaml.safe_load(agent_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            fails.append(f"[codex-plugin] {skill_dir.name} invalid agents/openai.yaml: {exc}")
            continue
        skill_interface = agent.get("interface") or {}
        for key in ("display_name", "short_description", "default_prompt"):
            if not skill_interface.get(key):
                fails.append(f"[codex-plugin] {skill_dir.name} interface missing '{key}'")
        invocation = f"$portfolio-prompts:{skill_dir.name}"
        if invocation not in str(skill_interface.get("default_prompt") or ""):
            fails.append(
                f"[codex-plugin] {skill_dir.name} default_prompt must mention '{invocation}'"
            )
        policy = agent.get("policy") or {}
        allow_implicit = policy.get("allow_implicit_invocation")
        if not isinstance(allow_implicit, bool):
            fails.append(
                f"[codex-plugin] {skill_dir.name} must declare boolean allow_implicit_invocation"
            )
        if skill_dir.name in explicit_only and allow_implicit is not False:
            fails.append(
                f"[codex-plugin] high-impact skill {skill_dir.name} must be explicit-only"
            )


def check_working_norms(fails: list[str]) -> None:
    contract = (HERE / "project-layout.md").read_text(encoding="utf-8")
    canonical = "All changes to a project's `main` go via branch + PR"
    if contract.count(canonical) != 1:
        fails.append(
            "[working-norms] project-layout.md must define the complete branch/PR norm exactly once"
        )

    operational = sorted(HERE.glob("*.prompt.md")) + sorted((HERE / "skills").glob("*/SKILL.md"))
    forbidden = (
        re.compile(r"all changes[^\n]*branch \+ PR", re.IGNORECASE),
        re.compile(r"direct pushes? to `main`", re.IGNORECASE),
        re.compile(r"harness blocks[^\n]*push", re.IGNORECASE),
    )
    for doc in operational:
        text = doc.read_text(encoding="utf-8")
        if any(pattern.search(text) for pattern in forbidden):
            fails.append(
                f"[working-norms] {doc.relative_to(HERE)} restates the universal policy; "
                "cite project-layout.md instead"
            )


def check_invocation_paths(fails: list[str]) -> None:
    operational = [HERE / "README.md", HERE / "skills" / "README.md"]
    operational += sorted(HERE.glob("*.prompt.md"))
    operational += sorted((HERE / "skills").glob("*/SKILL.md"))
    for doc in operational:
        if not doc.exists():
            continue
        if "portfolio-prompts\\" in doc.read_text(encoding="utf-8"):
            fails.append(
                f"[invocation-paths] {doc.relative_to(HERE)} uses a Windows-only "
                "'portfolio-prompts\\\\' invocation; use forward slashes"
            )


def check_worklist_example(fails: list[str]) -> None:
    text = (HERE / "project-layout.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```text\n(.*?)```", text, re.DOTALL)
    example = next((b for b in blocks if "# Worklist —" in b), None)
    if example is None:
        fails.append("[worklist-example] no '# Worklist —' example block in project-layout.md")
        return
    items = re.findall(r"^- \[[ x]\] \S+ — .+ — .+$", example, re.MULTILINE)
    if not items:
        fails.append("[worklist-example] example has no `- [ ] <id> — <desc> — <source>` item line")


def check_handover_pairs(fails: list[str]) -> None:
    """P-09: a Markdown handover without its HTML companion is a contract violation.

    Freshness (latest handover versus a project's default head) is deliberately NOT gated here —
    it is an advisory warning owned by workspace_preflight.py.
    """
    session_notes = PORTFOLIO_ROOT / "session-notes"
    if not session_notes.is_dir():
        # Standalone clone of just the library — the root session-notes archive is not present.
        print("check-library: note — no sibling session-notes/ present; skipping handover-pair check.")
        return
    name_re = re.compile(r"^.+_session-notes_v\d+_\d{8}T\d{4}Z\.md$")
    for md in sorted(session_notes.glob("*_session-notes_v*.md")):
        if name_re.match(md.name) and not md.with_suffix(".html").exists():
            fails.append(f"[handover-pairs] {md.name} has no HTML companion")


def check_workspace_preflight(fails: list[str]) -> None:
    command = "tools/workspace_preflight.py"
    for name in (
        "derive-all-worklists.prompt.md",
        "review-all-projects.prompt.md",
        "loop-all-worklists.prompt.md",
    ):
        text = (HERE / name).read_text(encoding="utf-8")
        step_one = re.search(r"^## Step 1\b.*?(?=^## Step 2\b)", text, re.MULTILINE | re.DOTALL)
        if not step_one or command not in step_one.group(0):
            fails.append(
                f"[workspace-preflight] {name} must run the canonical command in Step 1"
            )

    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tools/tests",
            "-p",
            "test_*.py",
        ],
        cwd=HERE,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stdout + "\n" + result.stderr).strip()
        fails.append("[workspace-preflight] deterministic tool tests failed:\n" + detail)


def check_kanban(fails: list[str]) -> None:
    """The shared Kanban generator (tools/kanban) carries its own Node test suite —
    the derive-status truth table, the backlog adapters, override validation, and
    the drift-gate over committed fixtures. Run it as part of the library self-gate
    so a regression in the generator is caught here, exactly as the derivation logic
    it carries over is gated in the auth-separation exemplar's `npm run verify`.

    Skipped with a note when Node is unavailable (a Python-only environment); the
    GitHub-hosted CI runners the library uses have Node preinstalled.
    """
    kanban_dir = HERE / "tools" / "kanban"
    if not kanban_dir.is_dir():
        return
    if shutil.which("node") is None:
        print("check-library: note — node not found; skipping tools/kanban Node test suite.")
        return
    # `node --test` auto-discovers test files under the working directory; a bare
    # directory argument is misread as a script path, so pass none.
    result = subprocess.run(
        ["node", "--test"],
        cwd=kanban_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stdout + "\n" + result.stderr).strip()
        fails.append("[kanban] tools/kanban Node test suite failed:\n" + detail)


def main() -> int:
    fails: list[str] = []
    for check in (
        check_registry_folders,
        check_registry_semantics,
        check_readme_generated,
        check_ci_workflow,
        check_internal_links,
        check_skills,
        check_prompt_skill_coverage,
        check_release_metadata,
        check_codex_plugin,
        check_working_norms,
        check_invocation_paths,
        check_worklist_example,
        check_workspace_preflight,
        check_handover_pairs,
        check_kanban,
    ):
        check(fails)
    if fails:
        print("check-library: FAIL")
        for f in fails:
            print("  - " + f)
        return 1
    print("check-library: PASS (registry classification, lifecycle/presentation semantics, README generated, "
          "least-privilege CI, internal links, skills, prompt-skill coverage, release metadata, Codex plugin, working norms, "
          "invocation paths, worklist example, workspace preflight scenarios, handover pairs, kanban generator)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
