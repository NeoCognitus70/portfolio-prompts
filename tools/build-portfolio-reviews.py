#!/usr/bin/env python3
"""Generator script for portfolio-reviews (PP-33).

Discovers the latest code review bundle for each showcase project registered in registry.yml,
extracts metadata and executive summaries, and renders:
  1. portfolio-reviews/README.md  (Markdown summary with drill-down links)
  2. portfolio-reviews/index.html (HTML companion for browser viewing)

Usage:
    python tools/build-portfolio-reviews.py
"""
from __future__ import annotations

import html
import os
import re
import sys
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent.parent           # portfolio-prompts/
PORTFOLIO_ROOT = HERE.parent                             # test-automation-portfolio/
REGISTRY_PATH = HERE / "registry.yml"
OUTPUT_DIR = PORTFOLIO_ROOT / "portfolio-reviews"
OUTPUT_MD = OUTPUT_DIR / "README.md"
OUTPUT_HTML = OUTPUT_DIR / "index.html"


def extract_timestamp(folder_name: str) -> str:
    m = re.search(r"(\d{8}T\d{4}Z)", folder_name)
    return m.group(1) if m else folder_name


def parse_metadata(exec_text: str, index_text: str) -> dict[str, str]:
    meta = {"reviewer": "Unknown", "date": "Unknown", "grade": "N/A"}
    
    # Search for Reviewer
    m_rev = re.search(r"\*\*Reviewer:\*\*\s*([^\n\r]+)", exec_text + "\n" + index_text)
    if m_rev:
        meta["reviewer"] = m_rev.group(1).strip()
    else:
        m_rev2 = re.search(r"Reviewer \| ([^\n\r\|]+)", exec_text + "\n" + index_text)
        if m_rev2:
            meta["reviewer"] = m_rev2.group(1).strip()
            
    # Search for Date
    m_date = re.search(r"\*\*Date:\*\*\s*([^\n\r]+)", exec_text + "\n" + index_text)
    if m_date:
        meta["date"] = m_date.group(1).strip()
    else:
        m_date2 = re.search(r"(\d{4}-\d{2}-\d{2})", exec_text + "\n" + index_text)
        if m_date2:
            meta["date"] = m_date2.group(1).strip()

    # Search for Grade/Verdict
    m_grade = re.search(r"\| Grade \|\s*([^\n\r\|]+)", exec_text + "\n" + index_text)
    if m_grade:
        meta["grade"] = m_grade.group(1).strip()
    else:
        m_grade2 = re.search(r"Grade:\s*\*?([A-Za-z0-9+-]+)\*?", exec_text + "\n" + index_text)
        if m_grade2:
            meta["grade"] = m_grade2.group(1).strip()
            
    return meta


def clean_exec_summary(text: str, proj_name: str, review_rel: str) -> str:
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        # Skip title heading line or navigation backlink line
        if line.startswith("# Section 1: Executive Summary") or line.startswith("# Executive Summary") or line.startswith("# 01. Executive Summary"):
            continue
        if "[<- Back to Index]" in line or "[Next: Risks and Issues" in line or "[< Back to Index]" in line:
            continue
        if line.strip() == "---" and not cleaned:
            continue
        cleaned.append(line)
    
    result_text = "\n".join(cleaned).strip()
    
    # Adjust relative links inside executive summary to be relative to portfolio-reviews/
    def adjust_link(match):
        label = match.group(1)
        url = match.group(2)
        if url.startswith("http://") or url.startswith("https://") or url.startswith("#") or url.startswith("../"):
            return f"[{label}]({url})"
        # Prepend ../<proj_name>/
        target_relative = f"../{proj_name}/{url}"
        return f"[{label}]({target_relative})"

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", adjust_link, result_text)


def build_reviews_summary() -> tuple[list[dict], str]:
    if not REGISTRY_PATH.exists():
        sys.exit(f"build-portfolio-reviews: registry not found at {REGISTRY_PATH}")

    registry_data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    projects_info = []

    for p in registry_data["projects"]:
        proj_name = p["project"]
        status = p.get("status", "unknown")
        
        # Skip meta prompt library itself if no reviews directory exists
        deviations = p.get("deviations", {})
        review_rel = deviations.get("reviews", f"{proj_name}/.review/")
        
        if review_rel.startswith(proj_name):
            review_dir = PORTFOLIO_ROOT / review_rel
        else:
            review_dir = PORTFOLIO_ROOT / proj_name / review_rel

        if not review_dir.exists():
            continue

        subdirs = [d for d in os.listdir(review_dir) if (review_dir / d).is_dir() and d.startswith("CODE_REVIEW_")]
        if not subdirs:
            continue

        subdirs.sort(key=extract_timestamp, reverse=True)
        latest_folder = subdirs[0]
        latest_path = review_dir / latest_folder

        exec_file = latest_path / "01_EXECUTIVE_SUMMARY.md"
        index_files = [f for f in os.listdir(latest_path) if f.startswith("00_") and f.endswith(".md")]
        index_file = latest_path / index_files[0] if index_files else latest_path / f"00_{latest_folder}.md"

        exec_content = exec_file.read_text(encoding="utf-8") if exec_file.exists() else ""
        index_content = index_file.read_text(encoding="utf-8") if index_file.exists() else ""

        meta = parse_metadata(exec_content, index_content)
        cleaned_summary = clean_exec_summary(exec_content, proj_name, review_rel)

        # Build relative paths from portfolio-reviews/
        rel_index = os.path.relpath(index_file, OUTPUT_DIR).replace("\\", "/")
        rel_exec = os.path.relpath(exec_file, OUTPUT_DIR).replace("\\", "/")
        rel_folder = os.path.relpath(latest_path, OUTPUT_DIR).replace("\\", "/")

        projects_info.append({
            "project": proj_name,
            "status": status,
            "latest_folder": latest_folder,
            "timestamp": extract_timestamp(latest_folder),
            "reviewer": meta["reviewer"],
            "date": meta["date"],
            "grade": meta["grade"],
            "rel_index": rel_index,
            "rel_exec": rel_exec,
            "rel_folder": rel_folder,
            "exec_summary": cleaned_summary
        })

    # Render Markdown
    md_lines = [
        "# Portfolio Code Reviews — Central Index & Latest Summaries",
        "",
        "> **Single Point of Reference:** Authoritative summary of the latest code review findings across all showcase projects in the test-automation portfolio.",
        "",
        "## Latest Reviews Matrix",
        "",
        "| Project | Status | Latest Review | Date | Reviewer | Grade | Links |",
        "|---|---|---|---|---|---|---|",
    ]

    for p in projects_info:
        links_cell = f"[Full Review]({p['rel_index']}) | [Executive Summary]({p['rel_exec']})"
        md_lines.append(
            f"| `{p['project']}` | {p['status']} | `{p['latest_folder']}` | {p['date']} | {p['reviewer']} | {p['grade']} | {links_cell} |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "## Detailed Executive Summaries per Project",
        "",
    ])

    for p in projects_info:
        md_lines.extend([
            f"### {p['project']}",
            "",
            f"- **Registry Lifecycle Status:** `{p['status']}`",
            f"- **Latest Review Bundle:** [`{p['latest_folder']}`]({p['rel_folder']}/)",
            f"- **Reviewer / Model:** {p['reviewer']}",
            f"- **Date / Timestamp:** {p['date']}",
            f"- **Overall Grade / Rating:** `{p['grade']}`",
            f"- **Drill-Down Links:** [Full Review Index]({p['rel_index']}) | [Executive Summary Document]({p['rel_exec']})",
            "",
            "<details><summary><strong>Click to expand Executive Summary for " + p['project'] + "</strong></summary>",
            "",
            p['exec_summary'],
            "",
            "</details>",
            "",
            "---",
            "",
        ])

    markdown_output = "\n".join(md_lines)
    return projects_info, markdown_output


def render_html(projects_info: list[dict], for_landing: bool = False) -> str:
    html_lines = [
        "<!DOCTYPE html>",
        "<html lang=\"en-GB\">",
        "<head>",
        "  <meta charset=\"utf-8\">",
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
        "  <title>Portfolio Code Reviews — Central Index</title>",
        "  <style>",
        "    :root {",
        "      --bg: #0f172a;",
        "      --panel: #1e293b;",
        "      --border: #334155;",
        "      --text: #f8fafc;",
        "      --muted: #94a3b8;",
        "      --accent: #38bdf8;",
        "      --accent-hover: #0284c7;",
        "      --green: #22c55e;",
        "      --yellow: #eab308;",
        "    }",
        "    body { font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 2rem; line-height: 1.6; }",
        "    .container { max-width: 1200px; margin: 0 auto; }",
        "    .nav-header { margin-bottom: 1.5rem; }",
        "    .nav-header a { font-weight: 600; text-decoration: none; color: var(--accent); }",
        "    h1 { color: #fff; border-bottom: 2px solid var(--border); padding-bottom: 0.5rem; margin-top: 0; }",
        "    h2 { color: var(--accent); margin-top: 2rem; border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }",
        "    h3 { color: #e2e8f0; margin-top: 1.5rem; }",
        "    p, li { color: #cbd5e1; }",
        "    a { color: var(--accent); text-decoration: none; font-weight: 500; }",
        "    a:hover { text-decoration: underline; color: var(--accent-hover); }",
        "    .badge { display: inline-block; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; }",
        "    .badge-active { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.4); }",
        "    .badge-resting { background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.4); }",
        "    table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; background: var(--panel); border-radius: 8px; overflow: hidden; border: 1px solid var(--border); }",
        "    th, td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid var(--border); }",
        "    th { background: #0f172a; color: var(--muted); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }",
        "    tr:last-child td { border-bottom: none; }",
        "    tr:hover td { background: rgba(255,255,255,0.02); }",
        "    .card { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }",
        "    details { background: #0f172a; border: 1px solid var(--border); border-radius: 6px; padding: 1rem; margin-top: 1rem; }",
        "    summary { font-weight: 600; cursor: pointer; color: var(--accent); }",
        "    summary:hover { color: #fff; }",
        "    code { font-family: ui-monospace, SFMono-Regular, Consolas, monospace; background: rgba(255,255,255,0.1); padding: 0.15rem 0.35rem; border-radius: 4px; font-size: 0.9em; }",
        "  </style>",
        "</head>",
        "<body>",
        "  <div class=\"container\">",
    ]

    if for_landing:
        html_lines.append("    <div class=\"nav-header\"><a href=\"index.html\">&larr; Back to Portfolio Showcase</a></div>")

    html_lines.extend([
        "    <h1>Portfolio Code Reviews — Central Index</h1>",
        "    <p>Authoritative summary of the latest code review findings across all showcase projects in the test-automation portfolio.</p>",
        "    ",
        "    <h2>Latest Reviews Matrix</h2>",
        "    <table>",
        "      <thead>",
        "        <tr>",
        "          <th>Project</th>",
        "          <th>Status</th>",
        "          <th>Latest Review</th>",
        "          <th>Date</th>",
        "          <th>Reviewer</th>",
        "          <th>Grade</th>",
        "          <th>Drill-Down Links</th>",
        "        </tr>",
        "      </thead>",
        "      <tbody>",
    ])

    for p in projects_info:
        badge_cls = "badge-active" if p['status'] == 'active' else "badge-resting"
        
        if for_landing:
            # Map relative paths to public GitHub URLs
            owner = "NeoCognitus70" if p['project'] in ["hand-baked-screenplay-pattern", "calculator-screenplay-bdd", "portfolio-prompts"] else "GBrooks1970"
            clean_rel = p['rel_index'].replace('../', '')
            clean_exec_rel = p['rel_exec'].replace('../', '')
            idx_url = f"https://github.com/{owner}/{clean_rel.split('/', 1)[0]}/blob/main/{clean_rel.split('/', 1)[1]}"
            exec_url = f"https://github.com/{owner}/{clean_exec_rel.split('/', 1)[0]}/blob/main/{clean_exec_rel.split('/', 1)[1]}"
        else:
            idx_url = p['rel_index']
            exec_url = p['rel_exec']

        html_lines.append(f"        <tr>")
        html_lines.append(f"          <td><code>{html.escape(p['project'])}</code></td>")
        html_lines.append(f"          <td><span class=\"badge {badge_cls}\">{html.escape(p['status'])}</span></td>")
        html_lines.append(f"          <td><code>{html.escape(p['latest_folder'])}</code></td>")
        html_lines.append(f"          <td>{html.escape(p['date'])}</td>")
        html_lines.append(f"          <td>{html.escape(p['reviewer'])}</td>")
        html_lines.append(f"          <td><code>{html.escape(p['grade'])}</code></td>")
        html_lines.append(f"          <td><a href=\"{idx_url}\">Full Review</a> &bull; <a href=\"{exec_url}\">Executive Summary</a></td>")
        html_lines.append(f"        </tr>")

    html_lines.extend([
        "      </tbody>",
        "    </table>",
        "    ",
        "    <h2>Detailed Executive Summaries per Project</h2>",
    ])

    for p in projects_info:
        badge_cls = "badge-active" if p['status'] == 'active' else "badge-resting"
        
        if for_landing:
            owner = "NeoCognitus70" if p['project'] in ["hand-baked-screenplay-pattern", "calculator-screenplay-bdd", "portfolio-prompts"] else "GBrooks1970"
            clean_rel = p['rel_index'].replace('../', '')
            clean_exec_rel = p['rel_exec'].replace('../', '')
            clean_folder_rel = p['rel_folder'].replace('../', '')
            idx_url = f"https://github.com/{owner}/{clean_rel.split('/', 1)[0]}/blob/main/{clean_rel.split('/', 1)[1]}"
            exec_url = f"https://github.com/{owner}/{clean_exec_rel.split('/', 1)[0]}/blob/main/{clean_exec_rel.split('/', 1)[1]}"
            folder_url = f"https://github.com/{owner}/{clean_folder_rel.split('/', 1)[0]}/tree/main/{clean_folder_rel.split('/', 1)[1]}"
        else:
            idx_url = p['rel_index']
            exec_url = p['rel_exec']
            folder_url = f"{p['rel_folder']}/"

        html_lines.append(f"    <div class=\"card\">")
        html_lines.append(f"      <h3>{html.escape(p['project'])} <span class=\"badge {badge_cls}\">{html.escape(p['status'])}</span></h3>")
        html_lines.append(f"      <p>")
        html_lines.append(f"        <strong>Latest Review:</strong> <code>{html.escape(p['latest_folder'])}</code> | ")
        html_lines.append(f"        <strong>Reviewer:</strong> {html.escape(p['reviewer'])} | ")
        html_lines.append(f"        <strong>Date:</strong> {html.escape(p['date'])} | ")
        html_lines.append(f"        <strong>Grade:</strong> <code>{html.escape(p['grade'])}</code>")
        html_lines.append(f"      </p>")
        html_lines.append(f"      <p>")
        html_lines.append(f"        <a href=\"{idx_url}\">Open Full Review Index</a> &bull; ")
        html_lines.append(f"        <a href=\"{exec_url}\">Open Executive Summary Document</a> &bull; ")
        html_lines.append(f"        <a href=\"{folder_url}\">Browse Review Folder</a>")
        html_lines.append(f"      </p>")
        
        # Simple HTML conversion for executive summary text
        html_lines.append(f"      <details>")
        html_lines.append(f"        <summary>Click to view Executive Summary text</summary>")
        html_lines.append(f"        <div style=\"margin-top: 1rem; color: #cbd5e1; font-size: 0.95rem; white-space: pre-wrap;\">{html.escape(p['exec_summary'])}</div>")
        html_lines.append(f"      </details>")
        html_lines.append(f"    </div>")

    html_lines.extend([
        "  </div>",
        "</body>",
        "</html>",
    ])

    return "\n".join(html_lines)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    projects_info, markdown_output = build_reviews_summary()
    
    OUTPUT_MD.write_text(markdown_output, encoding="utf-8")
    print(f"build-portfolio-reviews: wrote {OUTPUT_MD.relative_to(PORTFOLIO_ROOT)}")

    html_output = render_html(projects_info, for_landing=False)
    OUTPUT_HTML.write_text(html_output, encoding="utf-8")
    print(f"build-portfolio-reviews: wrote {OUTPUT_HTML.relative_to(PORTFOLIO_ROOT)}")

    landing_dir = PORTFOLIO_ROOT / "portfolio-landing"
    if landing_dir.exists():
        landing_reviews_html = landing_dir / "reviews.html"
        landing_html_output = render_html(projects_info, for_landing=True)
        landing_reviews_html.write_text(landing_html_output, encoding="utf-8")
        print(f"build-portfolio-reviews: wrote {landing_reviews_html.relative_to(PORTFOLIO_ROOT)}")

    print(f"build-portfolio-reviews: SUCCESS ({len(projects_info)} project review summaries generated)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
