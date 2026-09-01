#!/usr/bin/env python3
"""
generate_in_depth_reports_index.py
----------------------------------
Scans `portfolio-in-depth-reports/` for all generated in-depth project reports
and generates a master index file `portfolio-in-depth-reports/index.html`
(along with `portfolio-in-depth-reports/index.json`).

The resulting HTML index features:
- Responsive, premium modern design (dark/light mode, custom fonts, glassmorphism)
- Live client-side search, filtering by stack / discipline / status, and sorting
- Grid card view and structured table view toggle
- Rich KPI summary statistics
- Direct relative links to HTML reports, Markdown sources, and GitHub repositories.
"""

import json
import os
import re
import sys
from pathlib import Path

# Paths
PORTFOLIO_ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = PORTFOLIO_ROOT / "portfolio-in-depth-reports"
PRESENTATION_PATH = PORTFOLIO_ROOT / "portfolio-landing" / "data" / "presentation.json"


def load_presentation_data():
    if PRESENTATION_PATH.exists():
        try:
            with open(PRESENTATION_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning loading presentation.json: {e}", file=sys.stderr)
    return {}


def parse_report_file(html_file: Path, md_file: Path, project_dir_name: str, presentation_data: dict):
    project_slug = project_dir_name
    
    # Defaults
    meta = {
        "project": project_slug,
        "title": project_slug.replace("-", " ").replace(".", " ").title(),
        "version": "v1",
        "created": "",
        "created_display": "",
        "source_revision": "",
        "evidence_cutoff": "",
        "html_file": html_file.name if html_file else "",
        "html_path": f"./{project_dir_name}/{html_file.name}" if html_file else "",
        "md_file": md_file.name if md_file else "",
        "md_path": f"./{project_dir_name}/{md_file.name}" if md_file else "",
        "discipline": "Test Automation",
        "status": "Resting",
        "presentation_role": "Showcase",
        "tags": [],
        "github": f"https://github.com/GBrooks1970/{project_slug}",
        "summary": "In-depth architectural analysis and project verification report.",
        "highlights": []
    }

    # Match with presentation.json projects dictionary
    pres_projects = presentation_data.get("projects", {})
    if isinstance(pres_projects, dict) and project_slug in pres_projects:
        p = pres_projects[project_slug]
        meta["title"] = p.get("title", meta["title"])
        meta["discipline"] = p.get("discipline", meta["discipline"])
        meta["summary"] = p.get("summary", meta["summary"])
        meta["tags"] = p.get("tags", meta["tags"])
        if p.get("github"):
            meta["github"] = p.get("github")
    elif isinstance(pres_projects, list):
        for p in pres_projects:
            if isinstance(p, dict) and (p.get("project") == project_slug or p.get("id") == project_slug):
                meta["title"] = p.get("title", meta["title"])
                meta["discipline"] = p.get("discipline", meta["discipline"])
                meta["summary"] = p.get("summary", meta["summary"])
                meta["tags"] = p.get("tags", meta["tags"])
                if p.get("github"):
                    meta["github"] = p.get("github")
                break

    # Parse Markdown if present
    if md_file and md_file.exists():
        content = md_file.read_text(encoding="utf-8")
        
        # Frontmatter
        fm_match = re.search(r"^---\r?\n(.*?)\r?\n---", content, re.DOTALL)
        if fm_match:
            fm = fm_match.group(1)
            for line in fm.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k == "version":
                        meta["version"] = f"v{v}" if not v.startswith("v") else v
                    elif k == "created":
                        meta["created"] = v
                        meta["created_display"] = v.replace("T", " ").replace("Z", " UTC")
                    elif k == "source-revision":
                        meta["source_revision"] = v[:7] if len(v) >= 7 else v
                    elif k == "evidence-cut-off":
                        meta["evidence_cutoff"] = v

        # Title from first H1
        h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if h1_match:
            raw_h1 = h1_match.group(1).strip()
            # Clean off trailing in-depth report suffix
            cleaned = re.sub(r"\s*[—–-]\s*In-Depth Project Report.*$", "", raw_h1, flags=re.IGNORECASE).strip()
            if cleaned:
                meta["title"] = cleaned

        # Metadata table overrides
        meta_table_match = re.search(r"## Report metadata\s*\n\s*\|.*?\n\|.*?\n((?:\|.*?\n)+)", content)
        if meta_table_match:
            table_rows = meta_table_match.group(1).strip().splitlines()
            for row in table_rows:
                parts = [p.strip() for p in row.strip("|").split("|")]
                if len(parts) >= 2:
                    k, val = parts[0], parts[1]
                    if "Repository" in k:
                        gh_url_match = re.search(r"https://github\.com/[a-zA-Z0-9_\-\./]+", val)
                        if gh_url_match:
                            clean_url = gh_url_match.group(0).rstrip(")>].")
                            meta["github"] = clean_url
                    elif "Presentation Role" in k:
                        meta["presentation_role"] = val.split("(")[0].strip()
                    elif "Operating Status" in k:
                        meta["status"] = val.split("(")[0].strip()

        # Extract Summary from Executive summary
        exec_match = re.search(r"## 1\. Executive summary\s*\n+(?:###.*?\n+)?(.*?)(?=\n###|\n##|\n---|\Z)", content, re.DOTALL)
        if exec_match:
            summary_text = exec_match.group(1).strip()
            paragraphs = [p.strip().replace("\n", " ") for p in summary_text.split("\n\n") if p.strip() and not p.strip().startswith("-") and not p.strip().startswith("1.")]
            if paragraphs:
                meta["summary"] = paragraphs[0]

        # Extract Key accomplishments / highlights
        acc_match = re.search(r"### Key accomplishments\s*\n\s*(.*?)(?=\n###|\n##|\Z)", content, re.DOTALL)
        if acc_match:
            bullets = re.findall(r"-\s+\*\*(.*?)\*\*:?\s*(.*?)(?=\n-|\Z)", acc_match.group(1), re.DOTALL)
            meta["highlights"] = [{"title": b[0].strip(), "text": b[1].strip().replace("\n", " ")} for b in bullets[:4]]

    # Specific custom enrichments if tags are empty or need refinement
    if "sudoku" in project_slug:
        meta["tags"] = ["Multi-Stack", "TypeScript", "Python", "C# .NET 10", "Serenity/JS", "pytest-bdd", "Reqnroll", "Playwright", "Parity Gates"]
        meta["discipline"] = "Multi-Stack Parity"
    elif "hand-baked" in project_slug:
        meta["tags"] = ["TypeScript", "Zero-Dependency", "Screenplay Engine", "Architecture Reference", "ESM/CommonJS", "Teaching Reference"]
        meta["discipline"] = "Architecture Reference"
    elif "auth-separation" in project_slug:
        meta["tags"] = ["TypeScript", "Serenity/JS", "Playwright", "Cucumber", "WireMock", "Docker Compose", "Multi-Service"]
        meta["discipline"] = "Multi-Service Web E2E"
    elif "calculator" in project_slug:
        meta["tags"] = ["TypeScript", "Serenity/JS", "Cucumber", "Hand-Baked Provider", "Dual-Provider", "Zero-Browser"]
        meta["discipline"] = "Domain BDD Screenplay"
    elif "orangehrm" in project_slug:
        meta["tags"] = ["TypeScript", "Serenity/JS", "Playwright", "Cucumber", "Docker Compose", "MySQL", "Web UI E2E"]
        meta["discipline"] = "End-to-End Web UI"

    # Set GitHub properly for NeoCognitus70 projects if needed
    if "hand-baked" in project_slug or "calculator" in project_slug:
        meta["github"] = f"https://github.com/NeoCognitus70/{project_slug}"

    return meta


def collect_reports():
    presentation_data = load_presentation_data()
    reports = []
    
    if not REPORTS_DIR.exists():
        return reports

    for item in sorted(REPORTS_DIR.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            # Find latest html and md files
            html_files = sorted(item.glob("*_in-depth-report_*.html"), reverse=True)
            md_files = sorted(item.glob("*_in-depth-report_*.md"), reverse=True)
            
            if html_files or md_files:
                html_file = html_files[0] if html_files else None
                md_file = md_files[0] if md_files else None
                meta = parse_report_file(html_file, md_file, item.name, presentation_data)
                reports.append(meta)

    # Sort reports by title
    reports.sort(key=lambda r: r.get("title", ""))
    return reports


def generate_html(reports):
    reports_json = json.dumps(reports, indent=2)
    total_reports = len(reports)
    total_showcases = sum(1 for r in reports if "showcase" in r.get("presentation_role", "").lower())
    
    # Collect all unique tags and disciplines
    all_tags = sorted(list({tag for r in reports for tag in r.get("tags", [])}))
    all_disciplines = sorted(list({r.get("discipline", "") for r in reports if r.get("discipline")}))

    html = f"""<!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Portfolio In-Depth Project Reports — Master Index</title>
  <meta name="description" content="Master index and interactive catalogue of in-depth architectural and quality assurance reports across the test automation portfolio.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #0f172a;
      --bg-card: #1e293b;
      --bg-card-hover: #273549;
      --bg-panel: #141f32;
      --border: #334155;
      --border-accent: #38bdf8;
      --ink: #f8fafc;
      --ink-muted: #94a3b8;
      --ink-dim: #64748b;
      --primary: #38bdf8;
      --primary-hover: #0ea5e9;
      --accent: #6366f1;
      --success: #10b981;
      --success-bg: rgba(16, 185, 129, 0.12);
      --badge-bg: #334155;
      --tag-bg: rgba(56, 189, 248, 0.1);
      --tag-ink: #38bdf8;
      --shadow-sm: 0 2px 4px rgba(0,0,0,0.3);
      --shadow-md: 0 8px 24px rgba(0,0,0,0.4);
      --shadow-glow: 0 0 20px rgba(56, 189, 248, 0.15);
      --radius: 12px;
      --radius-sm: 6px;
      --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    [data-theme="light"] {{
      --bg: #f8fafc;
      --bg-card: #ffffff;
      --bg-card-hover: #f1f5f9;
      --bg-panel: #edf2f7;
      --border: #e2e8f0;
      --border-accent: #0284c7;
      --ink: #0f172a;
      --ink-muted: #475569;
      --ink-dim: #94a3b8;
      --primary: #0284c7;
      --primary-hover: #0369a1;
      --accent: #4f46e5;
      --success: #059669;
      --success-bg: rgba(5, 150, 105, 0.1);
      --badge-bg: #e2e8f0;
      --tag-bg: rgba(2, 132, 199, 0.08);
      --tag-ink: #0369a1;
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
      --shadow-md: 0 6px 18px rgba(0,0,0,0.08);
      --shadow-glow: 0 0 16px rgba(2, 132, 199, 0.12);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background-color: var(--bg);
      color: var(--ink);
      line-height: 1.6;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      transition: background-color 0.3s ease, color 0.3s ease;
    }}

    /* Container */
    .container {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 0 24px;
      width: 100%;
    }}

    /* Header */
    header {{
      background: linear-gradient(180deg, var(--bg-panel) 0%, var(--bg) 100%);
      border-bottom: 1px solid var(--border);
      padding: 44px 0 32px;
      position: relative;
      overflow: hidden;
    }}

    header::before {{
      content: '';
      position: absolute;
      top: -100px;
      left: 50%;
      transform: translateX(-50%);
      width: 800px;
      height: 250px;
      background: radial-gradient(circle, rgba(56, 189, 248, 0.15) 0%, rgba(99, 102, 241, 0.05) 50%, transparent 70%);
      pointer-events: none;
    }}

    .header-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 18px;
    }}

    .badge-hub {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--tag-bg);
      color: var(--tag-ink);
      font-size: 0.8rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      padding: 4px 12px;
      border-radius: 999px;
      border: 1px solid rgba(56, 189, 248, 0.25);
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .theme-toggle {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--ink);
      padding: 8px 14px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      font-size: 0.9rem;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: var(--transition);
    }}

    .theme-toggle:hover {{
      background: var(--bg-card-hover);
      border-color: var(--border-accent);
    }}

    .header-title {{
      font-size: 2.25rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      margin-bottom: 10px;
      background: linear-gradient(135deg, var(--ink) 0%, var(--primary) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .header-subtitle {{
      color: var(--ink-muted);
      font-size: 1.08rem;
      max-width: 860px;
      line-height: 1.6;
      margin-bottom: 24px;
    }}

    /* KPI Stats Ribbon */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-top: 20px;
    }}

    .kpi-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      padding: 16px 20px;
      border-radius: var(--radius);
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
    }}

    .kpi-value {{
      font-size: 1.8rem;
      font-weight: 800;
      color: var(--primary);
      line-height: 1.2;
    }}

    .kpi-label {{
      font-size: 0.8rem;
      color: var(--ink-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-weight: 600;
      margin-top: 4px;
    }}

    /* Controls Bar */
    .controls-section {{
      background: var(--bg-card);
      border-bottom: 1px solid var(--border);
      padding: 18px 0;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: var(--shadow-sm);
      backdrop-filter: blur(10px);
    }}

    .controls-wrapper {{
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      justify-content: space-between;
      align-items: center;
    }}

    .search-box {{
      position: relative;
      flex: 1;
      min-width: 260px;
      max-width: 480px;
    }}

    .search-input {{
      width: 100%;
      background: var(--bg-panel);
      border: 1px solid var(--border);
      color: var(--ink);
      font-size: 0.95rem;
      padding: 10px 16px 10px 40px;
      border-radius: var(--radius-sm);
      outline: none;
      transition: var(--transition);
      font-family: inherit;
    }}

    .search-input:focus {{
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);
    }}

    .search-icon {{
      position: absolute;
      left: 14px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--ink-dim);
      pointer-events: none;
      font-size: 0.9rem;
    }}

    .filters-group {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }}

    .select-dropdown {{
      background: var(--bg-panel);
      border: 1px solid var(--border);
      color: var(--ink);
      padding: 9px 14px;
      border-radius: var(--radius-sm);
      font-size: 0.88rem;
      font-family: inherit;
      cursor: pointer;
      outline: none;
      transition: var(--transition);
    }}

    .select-dropdown:focus {{
      border-color: var(--primary);
    }}

    .view-toggle-group {{
      display: flex;
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      overflow: hidden;
    }}

    .view-btn {{
      background: transparent;
      border: none;
      color: var(--ink-muted);
      padding: 8px 12px;
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: 500;
      transition: var(--transition);
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .view-btn.active {{
      background: var(--primary);
      color: #0f172a;
      font-weight: 600;
    }}

    /* Main Content Area */
    main {{
      flex: 1;
      padding: 32px 0 64px;
    }}

    .results-count {{
      font-size: 0.88rem;
      color: var(--ink-dim);
      margin-bottom: 20px;
    }}

    /* Grid Layout */
    .reports-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 24px;
    }}

    .report-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 24px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: var(--shadow-sm);
      transition: var(--transition);
      position: relative;
    }}

    .report-card:hover {{
      transform: translateY(-3px);
      box-shadow: var(--shadow-md), var(--shadow-glow);
      border-color: var(--border-accent);
    }}

    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
      margin-bottom: 12px;
    }}

    .card-discipline {{
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--primary);
    }}

    .card-version-pill {{
      background: var(--badge-bg);
      color: var(--ink-muted);
      font-size: 0.72rem;
      font-family: 'JetBrains Mono', monospace;
      padding: 3px 8px;
      border-radius: 4px;
      font-weight: 600;
      border: 1px solid var(--border);
    }}

    .card-title {{
      font-size: 1.28rem;
      font-weight: 700;
      line-height: 1.35;
      margin-bottom: 8px;
      color: var(--ink);
    }}

    .card-meta-line {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 0.8rem;
      color: var(--ink-dim);
      margin-bottom: 14px;
    }}

    .card-summary {{
      font-size: 0.92rem;
      color: var(--ink-muted);
      line-height: 1.55;
      margin-bottom: 18px;
      flex-grow: 1;
    }}

    .card-tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 20px;
    }}

    .tag-pill {{
      background: var(--tag-bg);
      color: var(--tag-ink);
      font-size: 0.75rem;
      font-weight: 500;
      padding: 3px 9px;
      border-radius: 999px;
      border: 1px solid rgba(56, 189, 248, 0.15);
    }}

    .card-actions {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding-top: 16px;
      border-top: 1px solid var(--border);
    }}

    .btn-primary {{
      flex: 1;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      background: var(--primary);
      color: #0f172a;
      padding: 9px 16px;
      border-radius: var(--radius-sm);
      font-size: 0.88rem;
      font-weight: 600;
      text-decoration: none;
      transition: var(--transition);
    }}

    .btn-primary:hover {{
      background: var(--primary-hover);
      box-shadow: 0 4px 12px rgba(56, 189, 248, 0.35);
    }}

    .btn-secondary {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      background: var(--bg-panel);
      color: var(--ink-muted);
      border: 1px solid var(--border);
      padding: 9px 12px;
      border-radius: var(--radius-sm);
      font-size: 0.88rem;
      font-weight: 500;
      text-decoration: none;
      transition: var(--transition);
    }}

    .btn-secondary:hover {{
      color: var(--ink);
      border-color: var(--border-accent);
      background: var(--bg-card-hover);
    }}

    /* Table View Layout */
    .table-container {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow-x: auto;
      box-shadow: var(--shadow-sm);
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.9rem;
    }}

    th {{
      background: var(--bg-panel);
      padding: 14px 18px;
      font-weight: 650;
      color: var(--ink-muted);
      text-transform: uppercase;
      font-size: 0.75rem;
      letter-spacing: 0.05em;
      border-bottom: 1px solid var(--border);
    }}

    td {{
      padding: 16px 18px;
      border-bottom: 1px solid var(--border);
      vertical-align: middle;
    }}

    tr:last-child td {{
      border-bottom: none;
    }}

    tr:hover td {{
      background: var(--bg-card-hover);
    }}

    .table-title-cell {{
      font-weight: 600;
      color: var(--ink);
    }}

    .table-title-cell a {{
      color: var(--ink);
      text-decoration: none;
      font-weight: 650;
    }}

    .table-title-cell a:hover {{
      color: var(--primary);
    }}

    .table-slug {{
      font-size: 0.78rem;
      font-family: 'JetBrains Mono', monospace;
      color: var(--ink-dim);
      margin-top: 2px;
    }}

    /* Empty State */
    .empty-state {{
      text-align: center;
      padding: 64px 20px;
      color: var(--ink-muted);
    }}

    .empty-icon {{
      font-size: 2.4rem;
      margin-bottom: 12px;
      color: var(--ink-dim);
    }}

    /* Footer */
    footer {{
      background: var(--bg-panel);
      border-top: 1px solid var(--border);
      padding: 28px 0;
      text-align: center;
      color: var(--ink-dim);
      font-size: 0.85rem;
    }}

    footer a {{
      color: var(--primary);
      text-decoration: none;
    }}

    footer a:hover {{
      text-decoration: underline;
    }}

    @media (max-width: 768px) {{
      .header-title {{ font-size: 1.8rem; }}
      .reports-grid {{ grid-template-columns: 1fr; }}
      .controls-wrapper {{ flex-direction: column; align-items: stretch; }}
      .search-box {{ max-width: none; }}
    }}
  </style>
</head>
<body data-theme="dark">

  <header>
    <div class="container">
      <div class="header-top">
        <span class="badge-hub">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
          Portfolio Documentation Hub
        </span>
        <div class="header-actions">
          <button class="theme-toggle" id="themeToggle" title="Toggle Dark/Light Mode">
            <span id="themeIcon">☀️</span> <span id="themeText">Light</span>
          </button>
        </div>
      </div>
      <h1 class="header-title">In-Depth Project Reports</h1>
      <p class="header-subtitle">
        Authoritative, evidence-based project reports detailing technical architecture, test pyramid design, historical evolution milestones, decision registers, and governance verification across the portfolio.
      </p>

      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-value" id="kpiTotalReports">{total_reports}</div>
          <div class="kpi-label">Reports Generated</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-value" id="kpiShowcases">{total_showcases}</div>
          <div class="kpi-label">Showcase Projects</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-value" id="kpiParity">100%</div>
          <div class="kpi-label">Backlog Resolution</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-value" id="kpiFormats">HTML + MD</div>
          <div class="kpi-label">Bilingual Formats</div>
        </div>
      </div>
    </div>
  </header>

  <section class="controls-section">
    <div class="container">
      <div class="controls-wrapper">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input type="text" id="searchInput" class="search-input" placeholder="Search by title, stack, discipline, or keywords...">
        </div>

        <div class="filters-group">
          <select id="disciplineFilter" class="select-dropdown">
            <option value="">All Disciplines</option>
            {''.join(f'<option value="{d}">{d}</option>' for d in all_disciplines)}
          </select>

          <select id="sortFilter" class="select-dropdown">
            <option value="title-asc">Sort by Name (A-Z)</option>
            <option value="title-desc">Sort by Name (Z-A)</option>
            <option value="date-desc">Sort by Newest Date</option>
            <option value="date-asc">Sort by Oldest Date</option>
          </select>

          <div class="view-toggle-group">
            <button class="view-btn active" id="btnGridView" title="Grid Card View">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
              Grid
            </button>
            <button class="view-btn" id="btnTableView" title="Table View">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
              Table
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>

  <main>
    <div class="container">
      <div class="results-count" id="resultsCount">Showing {total_reports} reports</div>

      <div id="gridContainer" class="reports-grid">
        <!-- Rendered dynamically by JavaScript -->
      </div>

      <div id="tableContainer" class="table-container" style="display: none;">
        <table>
          <thead>
            <tr>
              <th>Project</th>
              <th>Discipline</th>
              <th>Version & Date</th>
              <th>Stack Tags</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody id="tableBody">
            <!-- Rendered dynamically by JavaScript -->
          </tbody>
        </table>
      </div>

      <div id="emptyState" class="empty-state" style="display: none;">
        <div class="empty-icon">🔎</div>
        <h3>No matching project reports found</h3>
        <p>Try clearing your search query or selecting a different discipline filter.</p>
      </div>
    </div>
  </main>

  <footer>
    <div class="container">
      <p>© 2026 Test Automation Portfolio · Built with Spec-Driven Development and strict quality governance.</p>
    </div>
  </footer>

  <script>
    const reportsData = {reports_json};

    let currentView = 'grid';
    let searchQuery = '';
    let selectedDiscipline = '';
    let currentSort = 'title-asc';

    const searchInput = document.getElementById('searchInput');
    const disciplineFilter = document.getElementById('disciplineFilter');
    const sortFilter = document.getElementById('sortFilter');
    const btnGridView = document.getElementById('btnGridView');
    const btnTableView = document.getElementById('btnTableView');
    const gridContainer = document.getElementById('gridContainer');
    const tableContainer = document.getElementById('tableContainer');
    const tableBody = document.getElementById('tableBody');
    const emptyState = document.getElementById('emptyState');
    const resultsCount = document.getElementById('resultsCount');
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');

    // Theme handling
    function setTheme(theme) {{
      document.body.setAttribute('data-theme', theme);
      if (theme === 'dark') {{
        themeIcon.textContent = '☀️';
        themeText.textContent = 'Light';
      }} else {{
        themeIcon.textContent = '🌙';
        themeText.textContent = 'Dark';
      }}
      localStorage.setItem('portfolio-reports-theme', theme);
    }}

    themeToggle.addEventListener('click', () => {{
      const current = document.body.getAttribute('data-theme') || 'dark';
      setTheme(current === 'dark' ? 'light' : 'dark');
    }});

    const savedTheme = localStorage.getItem('portfolio-reports-theme') || 'dark';
    setTheme(savedTheme);

    // View toggling
    btnGridView.addEventListener('click', () => {{
      currentView = 'grid';
      btnGridView.classList.add('active');
      btnTableView.classList.remove('active');
      gridContainer.style.display = 'grid';
      tableContainer.style.display = 'none';
      render();
    }});

    btnTableView.addEventListener('click', () => {{
      currentView = 'table';
      btnTableView.classList.add('active');
      btnGridView.classList.remove('active');
      gridContainer.style.display = 'none';
      tableContainer.style.display = 'block';
      render();
    }});

    // Filtering & Sorting
    searchInput.addEventListener('input', (e) => {{
      searchQuery = e.target.value.toLowerCase().trim();
      render();
    }});

    disciplineFilter.addEventListener('change', (e) => {{
      selectedDiscipline = e.target.value;
      render();
    }});

    sortFilter.addEventListener('change', (e) => {{
      currentSort = e.target.value;
      render();
    }});

    function filterAndSortReports() {{
      return reportsData.filter(report => {{
        const matchesQuery = !searchQuery || 
          report.title.toLowerCase().includes(searchQuery) ||
          report.project.toLowerCase().includes(searchQuery) ||
          report.discipline.toLowerCase().includes(searchQuery) ||
          report.summary.toLowerCase().includes(searchQuery) ||
          (report.tags && report.tags.some(t => t.toLowerCase().includes(searchQuery)));
        
        const matchesDiscipline = !selectedDiscipline || report.discipline === selectedDiscipline;

        return matchesQuery && matchesDiscipline;
      }}).sort((a, b) => {{
        if (currentSort === 'title-asc') return a.title.localeCompare(b.title);
        if (currentSort === 'title-desc') return b.title.localeCompare(a.title);
        if (currentSort === 'date-desc') return (b.created || '').localeCompare(a.created || '');
        if (currentSort === 'date-asc') return (a.created || '').localeCompare(b.created || '');
        return 0;
      }});
    }}

    function render() {{
      const filtered = filterAndSortReports();
      resultsCount.textContent = `Showing ${{filtered.length}} of ${{reportsData.length}} reports`;

      if (filtered.length === 0) {{
        gridContainer.style.display = 'none';
        tableContainer.style.display = 'none';
        emptyState.style.display = 'block';
        return;
      }}

      emptyState.style.display = 'none';
      if (currentView === 'grid') {{
        gridContainer.style.display = 'grid';
        tableContainer.style.display = 'none';
        renderGrid(filtered);
      }} else {{
        gridContainer.style.display = 'none';
        tableContainer.style.display = 'block';
        renderTable(filtered);
      }}
    }}

    function renderGrid(items) {{
      gridContainer.innerHTML = items.map(report => `
        <div class="report-card">
          <div>
            <div class="card-top">
              <span class="card-discipline">${{report.discipline}}</span>
              <span class="card-version-pill">${{report.version}} · ${{report.created_display || report.created || '2026'}}</span>
            </div>
            <h3 class="card-title">${{report.title}}</h3>
            <div class="card-meta-line">
              <span>📂 <code>${{report.project}}</code></span>
              ${{report.source_revision ? `<span>🏷️ <code>${{report.source_revision}}</code></span>` : ''}}
            </div>
            <p class="card-summary">${{report.summary}}</p>
            <div class="card-tags">
              ${{(report.tags || []).map(t => `<span class="tag-pill">${{t}}</span>`).join('')}}
            </div>
          </div>
          <div class="card-actions">
            <a href="${{report.html_path}}" class="btn-primary">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
              View HTML Report
            </a>
            ${{report.md_path ? `
            <a href="${{report.md_path}}" class="btn-secondary" title="View Markdown Source">
              📄 MD
            </a>` : ''}}
            ${{report.github ? `
            <a href="${{report.github}}" class="btn-secondary" target="_blank" rel="noopener" title="Open GitHub Repository">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>
            </a>` : ''}}
          </div>
        </div>
      `).join('');
    }}

    function renderTable(items) {{
      tableBody.innerHTML = items.map(report => `
        <tr>
          <td>
            <div class="table-title-cell">
              <a href="${{report.html_path}}">${{report.title}}</a>
            </div>
            <div class="table-slug">${{report.project}}</div>
          </td>
          <td><span class="card-discipline">${{report.discipline}}</span></td>
          <td>
            <span class="card-version-pill">${{report.version}}</span>
            <div style="font-size: 0.78rem; color: var(--ink-dim); margin-top: 3px;">${{report.created_display || report.created || '2026'}}</div>
          </td>
          <td>
            <div class="card-tags" style="margin-bottom: 0;">
              ${{(report.tags || []).slice(0, 3).map(t => `<span class="tag-pill">${{t}}</span>`).join('')}}
              ${{report.tags && report.tags.length > 3 ? `<span class="tag-pill">+${{report.tags.length - 3}}</span>` : ''}}
            </div>
          </td>
          <td>
            <div style="display: flex; gap: 8px;">
              <a href="${{report.html_path}}" class="btn-primary" style="padding: 6px 12px; font-size: 0.8rem;">HTML</a>
              ${{report.md_path ? `<a href="${{report.md_path}}" class="btn-secondary" style="padding: 6px 10px; font-size: 0.8rem;">MD</a>` : ''}}
            </div>
          </td>
        </tr>
      `).join('');
    }}

    // Initial render
    render();
  </script>
</body>
</html>
"""
    return html


def main():
    print(f"Scanning reports in: {REPORTS_DIR}")
    reports = collect_reports()
    print(f"Found {len(reports)} generated in-depth report(s):")
    for r in reports:
        print(f" - [{r['version']}] {r['title']} ({r['project']}) -> {r['html_file']}")

    # Write index.json
    json_path = REPORTS_DIR / "index.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2)
    print(f"Wrote {json_path}")

    # Write index.html
    html_content = generate_html(reports)
    html_path = REPORTS_DIR / "index.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Wrote {html_path}")


if __name__ == "__main__":
    main()
