#!/usr/bin/env python3
"""Self-gate for the portfolio-prompts library (PP-15).

The library previously had no real gate ("docs-only, link/grep"). This asserts the library's own
invariants so a broken registry, a dangling doc link, a stale README table, or a malformed worklist
example is caught before merge — the same discipline the library imposes on the projects it serves.

Checks:
  1. Registry folders   — every `project` in registry.yml maps to a real folder (../name; the meta
                          `portfolio-prompts` maps to the library itself).
  2. README generated   — the README registry table is up to date w.r.t. registry.yml
                          (delegates to `render-registry.py --check`).
  3. Internal links     — every relative Markdown link in the library's own docs resolves.
  4. Working norms      — the universal branch/PR policy is defined once in project-layout.md and
                          is not restated in operational prompts or skill bodies.
  5. Invocation paths   — active invocation examples use OS-neutral forward slashes.
  6. Worklist example   — the canonical example in project-layout.md parses as the documented format.

Usage (from the portfolio-prompts/ directory):
    python tools/check-library.py            # exit 0 if all checks pass, 1 otherwise

Requires PyYAML (`pip install pyyaml`). No other dependencies.
"""
from __future__ import annotations

import re
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

    # Drift watch: any sibling repo (has .git) that is neither a registry row nor acknowledged.
    known = set(present) | set(data.get("unregistered_candidates") or [])
    for child in sorted(PORTFOLIO_ROOT.iterdir()):
        if child.is_dir() and (child / ".git").exists() and child.name not in known:
            fails.append(
                f"[registry-folders] workspace repo '{child.name}' is neither a registry row nor in "
                f"unregistered_candidates — onboard it or acknowledge it in registry.yml"
            )


def check_readme_generated(fails: list[str]) -> None:
    r = subprocess.run(
        [sys.executable, str(HERE / "tools" / "render-registry.py"), "--check"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        fails.append("[readme-generated] " + (r.stdout.strip() or "README table is stale"))


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


def main() -> int:
    fails: list[str] = []
    for check in (
        check_registry_folders,
        check_readme_generated,
        check_internal_links,
        check_skills,
        check_working_norms,
        check_invocation_paths,
        check_worklist_example,
    ):
        check(fails)
    if fails:
        print("check-library: FAIL")
        for f in fails:
            print("  - " + f)
        return 1
    print("check-library: PASS (registry folders, README generated, internal links, skills, "
          "working norms, invocation paths, worklist example)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
