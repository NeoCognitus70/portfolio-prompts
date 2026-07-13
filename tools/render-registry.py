#!/usr/bin/env python3
"""Render the README project-registry table from registry.yml (PP-23).

registry.yml is the source of truth; the README table is a generated view. This script rewrites
the block between the `<!-- REGISTRY:START ... -->` and `<!-- REGISTRY:END -->` markers in
README.md so the two can never drift.

Usage (run from the portfolio-prompts/ directory):
    python tools/render-registry.py            # rewrite README.md in place
    python tools/render-registry.py --check     # exit 1 if README is out of date (for a gate)

Requires PyYAML (`pip install pyyaml`). No other dependencies.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("render-registry: PyYAML is required (pip install pyyaml)")

HERE = Path(__file__).resolve().parent.parent      # portfolio-prompts/
REGISTRY = HERE / "registry.yml"
README = HERE / "README.md"

MARKERS = re.compile(
    r"(<!-- REGISTRY:START.*?-->\n).*?(\n<!-- REGISTRY:END -->)", re.DOTALL
)


def render_gates(g) -> str:
    if not g:
        return ""
    if isinstance(g, list):
        return "Gates: " + ", ".join(f"`{c}`" for c in g) + "."
    if isinstance(g, dict):
        t = g.get("type")
        if t == "docs_only":
            return "Gates: docs-only (link/grep checks, no build)."
        if t == "ci_jobs":
            stacks = "; ".join(
                f"{s['name']} {s['tool']}/{s['language']}" for s in g.get("stacks", [])
            )
            parity = g.get("parity_scripts")
            extra = f" + `{parity}` parity" if parity else ""
            return (
                f"Gates: per `ci.yml` — stack jobs ({stacks}){extra}; "
                "run the job(s) for the stack(s) touched."
            )
        if t == "ci":
            parts = []
            if g.get("static"):
                parts.append("static " + ", ".join(f"`{c}`" for c in g["static"]))
            e = g.get("e2e")
            if e:
                parts.append(f"E2E `{e['bring_up']}` then `{e['run']}`")
            out = "Gates: per `ci.yml` — " + "; ".join(parts) + "."
            if g.get("notes"):
                out += f" {g['notes']}."
            return out
    return ""


def render_deviations(dev: dict) -> str:
    label = {
        "backlog": "backlog",
        "reviews": "reviews",
        "implementation_logs": "implementation-logs",
        "shared_templates": "templates",
        "adr": "adr",
        "project_contract": "project-contract",
    }
    parts = [f"{label.get(k, k)} `{v}`" for k, v in dev.items()]
    return "Deviations: " + ", ".join(parts) + "."


def render_couples(c: dict) -> str:
    order = f" ({c['order']})" if c.get("order") else ""
    return f"Depends on `{c['project']}` — {c['reason']}{order}."


def status_label(p: dict) -> str:
    if p.get("status_label"):
        return p["status_label"]
    s = p.get("status", "")
    if s == "meta":
        return "Meta (self-onboarded)"
    if s == "active":
        return "Active (product)" if p.get("product") else "Active"
    return s.capitalize()


def notes_cell(p: dict) -> str:
    parts = []
    if p.get("notes"):
        parts.append(p["notes"].strip())
    for clause in (
        render_gates(p.get("gates")),
        render_deviations(p["deviations"]) if p.get("deviations") else "",
        render_couples(p["couples_with"]) if p.get("couples_with") else "",
    ):
        if clause:
            parts.append(clause)
    return " ".join(parts)


def render_table(data: dict) -> str:
    rows = [
        f"| `{p['project']}` | {p['github']} | {status_label(p)} | {notes_cell(p)} |"
        for p in data["projects"]
    ]
    header = "| `PROJECT` | GitHub | Status | Notes |\n|---|---|---|---|"
    return header + "\n" + "\n".join(rows)


def main() -> int:
    check = "--check" in sys.argv[1:]
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    readme = README.read_text(encoding="utf-8")
    if not MARKERS.search(readme):
        sys.exit("render-registry: REGISTRY:START/END markers not found in README.md")
    table = render_table(data)
    updated = MARKERS.sub(lambda m: m.group(1) + table + m.group(2), readme)
    if updated == readme:
        print("render-registry: README table already up to date.")
        return 0
    if check:
        print("render-registry: README table is OUT OF DATE — run `python tools/render-registry.py`.")
        return 1
    README.write_text(updated, encoding="utf-8", newline="\n")
    print(f"render-registry: rewrote README table ({len(data['projects'])} projects).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
