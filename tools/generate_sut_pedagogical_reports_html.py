#!/usr/bin/env python3
"""
generate_sut_pedagogical_reports_html.py
-----------------------------------------
Generates standalone, responsive HTML companion files for all pedagogical SUT
architecture reports and the master README in `portfolio-pedagogical-reports/`.

Features:
- Dual-theme support (light/dark via prefers-color-scheme & clean CSS variables)
- Responsive layout with sticky top navigation breadcrumbs
- Native Mermaid 10 rendering via ESM CDN with theme awareness
- GitHub-style alert callout support ([!NOTE], [!TIP], [!IMPORTANT], etc.)
- Automatic link translation between Markdown and HTML companions
- Semantic tables with horizontal scrolling and zebra styling
- 100% compliant with portfolio typography, en-GB spelling, and accessibility standards
"""

from __future__ import annotations

import html
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("generate_sut_pedagogical_reports_html.py requires 'markdown' (pip install markdown)")

# Directory anchors
SCRIPT_DIR = Path(__file__).resolve().parent
PORTFOLIO_ROOT = SCRIPT_DIR.parent.parent
REPORTS_DIR = PORTFOLIO_ROOT / "portfolio-pedagogical-reports"

# Tier mapping for SUT projects
TIER_1_PROJECTS = {
    "tradeblotter-wpf-screenplay",
    "auth-separation-screenplay-poc",
    "calculator-screenplay-bdd",
    "mobile-forex-automation",
    "gb.automation.smoketests.sudoku.poc",
    "markdown-renderer",
}

TIER_2_PROJECTS = {
    "saleor-graphql-automation",
    "parabank-bank-automation",
    "juice-shop-dast-automation",
    "orangehrm-pim-automation",
    "magento-checkout-automation",
}

HTML_TEMPLATE = """<!doctype html>
<!--
  source: {source_file}
  type: {doc_type}
  project: {project_slug}
  tier: {tier_label}
  generated: {generation_time}
  language: en-GB
-->
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{page_title}</title>
  <style>
    :root {{
      --bg: #ffffff;
      --surface: #f8fafc;
      --panel: #f1f5f9;
      --text: #1e293b;
      --text-muted: #64748b;
      --line: #e2e8f0;
      --line-subtle: #edf2f7;
      --accent: #2563eb;
      --accent-hover: #1d4ed8;
      --accent-subtle: #eff6ff;
      --code-bg: #f8fafc;
      --code-text: #0f172a;
      --code-border: #cbd5e1;
      --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
      --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
      --tag-tier1-bg: #eff6ff;
      --tag-tier1-text: #1d4ed8;
      --tag-tier1-border: #bfdbfe;
      --tag-tier2-bg: #f5f3ff;
      --tag-tier2-text: #6d28d9;
      --tag-tier2-border: #ddd6fe;
      --callout-note-bg: #f0f9ff;
      --callout-note-border: #0284c7;
      --callout-tip-bg: #f0fdf4;
      --callout-tip-border: #16a34a;
      --callout-important-bg: #faf5ff;
      --callout-important-border: #9333ea;
      --callout-warning-bg: #fffbeb;
      --callout-warning-border: #d97706;
      --callout-caution-bg: #fef2f2;
      --callout-caution-border: #dc2626;
    }}

    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #0b0f17;
        --surface: #111827;
        --panel: #1e293b;
        --text: #f3f4f6;
        --text-muted: #9ca3af;
        --line: #334155;
        --line-subtle: #1e293b;
        --accent: #60a5fa;
        --accent-hover: #93c5fd;
        --accent-subtle: #172554;
        --code-bg: #111827;
        --code-text: #e5e7eb;
        --code-border: #374151;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.5);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.5);
        --tag-tier1-bg: #1e3a5f;
        --tag-tier1-text: #93c5fd;
        --tag-tier1-border: #2563eb;
        --tag-tier2-bg: #3b1d5c;
        --tag-tier2-text: #d8b4fe;
        --tag-tier2-border: #7c3aed;
        --callout-note-bg: #0c2340;
        --callout-note-border: #38bdf8;
        --callout-tip-bg: #052e16;
        --callout-tip-border: #22c55e;
        --callout-important-bg: #2e1065;
        --callout-important-border: #c084fc;
        --callout-warning-bg: #451a03;
        --callout-warning-border: #f59e0b;
        --callout-caution-bg: #450a0a;
        --callout-caution-border: #f87171;
      }}
    }}

    * {{
      box-sizing: border-box;
    }}

    html {{
      -webkit-text-size-adjust: 100%;
      scroll-behavior: smooth;
    }}

    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
      color: var(--text);
      background-color: var(--bg);
      line-height: 1.68;
      font-size: 15px;
    }}

    /* Sticky Navigation Header */
    .top-nav {{
      position: sticky;
      top: 0;
      z-index: 100;
      background: var(--surface);
      border-bottom: 1px solid var(--line);
      backdrop-filter: blur(8px);
      padding: 10px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      box-shadow: var(--shadow-sm);
    }}

    .nav-left, .nav-right {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .nav-link {{
      color: var(--accent);
      text-decoration: none;
      font-size: 0.88rem;
      font-weight: 550;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 6px;
      transition: background-color 0.15s ease, color 0.15s ease;
    }}

    .nav-link:hover {{
      background: var(--accent-subtle);
      color: var(--accent-hover);
      text-decoration: none;
    }}

    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 3px 9px;
      border-radius: 9999px;
      font-size: 0.76rem;
      font-weight: 650;
      letter-spacing: 0.02em;
      text-transform: uppercase;
    }}

    .badge-tier1 {{
      background: var(--tag-tier1-bg);
      color: var(--tag-tier1-text);
      border: 1px solid var(--tag-tier1-border);
    }}

    .badge-tier2 {{
      background: var(--tag-tier2-bg);
      color: var(--tag-tier2-text);
      border: 1px solid var(--tag-tier2-border);
    }}

    .badge-index {{
      background: var(--panel);
      color: var(--text-muted);
      border: 1px solid var(--line);
    }}

    /* Main Container */
    main {{
      max-width: 1040px;
      margin: 0 auto;
      padding: 40px 28px 100px;
    }}

    /* Typography */
    h1 {{
      font-size: 2.15rem;
      font-weight: 750;
      line-height: 1.25;
      margin: 0 0 20px;
      padding-bottom: 16px;
      border-bottom: 3px solid var(--accent);
      color: var(--text);
    }}

    h2 {{
      font-size: 1.45rem;
      font-weight: 700;
      margin: 44px 0 16px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--line);
      color: var(--text);
    }}

    h3 {{
      font-size: 1.18rem;
      font-weight: 650;
      margin: 32px 0 12px;
      color: var(--text);
    }}

    h4 {{
      font-size: 1.02rem;
      font-weight: 600;
      margin: 24px 0 8px;
      color: var(--text-muted);
    }}

    p, ul, ol {{
      margin: 0 0 16px;
    }}

    ul, ol {{
      padding-left: 26px;
    }}

    li {{
      margin: 5px 0;
    }}

    li > ul, li > ol {{
      margin: 6px 0 6px 0;
    }}

    a {{
      color: var(--accent);
      text-decoration: underline;
      text-decoration-thickness: 1px;
      text-underline-offset: 2px;
    }}

    a:hover {{
      color: var(--accent-hover);
      text-decoration-thickness: 2px;
    }}

    a:focus-visible {{
      outline: 2px solid var(--accent);
      outline-offset: 2px;
      border-radius: 2px;
    }}

    strong {{
      font-weight: 650;
      color: var(--text);
    }}

    hr {{
      border: 0;
      border-top: 1px solid var(--line);
      margin: 40px 0;
    }}

    /* Inline Code */
    code {{
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace;
      font-size: 0.88em;
      background: var(--code-bg);
      color: var(--code-text);
      border: 1px solid var(--code-border);
      border-radius: 4px;
      padding: 0.15em 0.4em;
    }}

    /* Code Blocks */
    pre {{
      background: var(--code-bg);
      color: var(--code-text);
      border: 1px solid var(--code-border);
      border-radius: 8px;
      padding: 16px 20px;
      overflow-x: auto;
      font-size: 0.86rem;
      line-height: 1.55;
      margin: 0 0 20px;
      box-shadow: var(--shadow-sm);
    }}

    pre code {{
      background: none;
      border: 0;
      padding: 0;
      color: inherit;
      font-size: inherit;
    }}

    /* Mermaid Architecture & Sequence Diagrams */
    .diagram-wrapper {{
      margin: 24px 0;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 24px 16px;
      overflow-x: auto;
      text-align: center;
      box-shadow: var(--shadow-sm);
    }}

    .mermaid {{
      display: inline-block;
      min-width: 280px;
      text-align: center;
      background: transparent !important;
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace;
      font-size: 0.85rem;
    }}

    .diagram-wrapper svg {{
      max-width: 100%;
      height: auto;
      display: inline-block;
      margin: 0 auto;
    }}

    /* Tables */
    .table-container {{
      width: 100%;
      overflow-x: auto;
      margin: 20px 0 24px;
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow-sm);
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.91rem;
      background: var(--bg);
    }}

    th, td {{
      padding: 10px 14px;
      border: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}

    th {{
      background: var(--panel);
      font-weight: 650;
      color: var(--text);
      white-space: nowrap;
    }}

    tbody tr:nth-child(even) {{
      background: var(--surface);
    }}

    tbody tr:hover {{
      background: var(--accent-subtle);
    }}

    /* GitHub Alert Callouts */
    .alert {{
      margin: 20px 0;
      padding: 14px 18px;
      border-left: 4px solid var(--accent);
      border-radius: 0 8px 8px 0;
      background: var(--panel);
    }}

    .alert p:last-child {{
      margin-bottom: 0;
    }}

    .alert-note {{
      border-left-color: var(--callout-note-border);
      background: var(--callout-note-bg);
    }}

    .alert-tip {{
      border-left-color: var(--callout-tip-border);
      background: var(--callout-tip-bg);
    }}

    .alert-important {{
      border-left-color: var(--callout-important-border);
      background: var(--callout-important-bg);
    }}

    .alert-warning {{
      border-left-color: var(--callout-warning-border);
      background: var(--callout-warning-bg);
    }}

    .alert-caution {{
      border-left-color: var(--callout-caution-border);
      background: var(--callout-caution-bg);
    }}

    .alert-title {{
      font-weight: 700;
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    blockquote {{
      margin: 20px 0;
      padding: 12px 18px;
      border-left: 4px solid var(--accent);
      background: var(--panel);
      border-radius: 0 6px 6px 0;
      color: var(--text-muted);
    }}

    /* Footer */
    footer {{
      margin-top: 60px;
      padding-top: 24px;
      border-top: 1px solid var(--line);
      font-size: 0.85rem;
      color: var(--text-muted);
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
    }}

    @media (max-width: 768px) {{
      main {{
        padding: 24px 16px 64px;
      }}
      h1 {{
        font-size: 1.7rem;
      }}
      h2 {{
        font-size: 1.25rem;
      }}
      .top-nav {{
        padding: 8px 16px;
      }}
      footer {{
        flex-direction: column;
      }}
    }}

    @media print {{
      .top-nav, footer {{
        display: none;
      }}
      main {{
        max-width: none;
        padding: 0;
      }}
      body {{
        background: #fff;
        color: #000;
      }}
      a {{
        color: #000;
        text-decoration: underline;
      }}
      table, pre, .diagram-wrapper {{
        break-inside: avoid;
      }}
    }}
  </style>
</head>
<body>

  <header class="top-nav">
    <div class="nav-left">
      {nav_left_content}
    </div>
    <div class="nav-right">
      {nav_right_content}
    </div>
  </header>

  <main>
    {main_content}
  </main>

  <footer>
    <div>
      <strong>Portfolio Pedagogical SUT Architecture Reports</strong> &bull; Generated: {generation_display}
    </div>
    <div>
      <a href="#top" class="nav-link">&uarr; Back to Top</a>
    </div>
  </footer>

  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    mermaid.initialize({{
      startOnLoad: true,
      theme: isDark ? 'dark' : 'neutral',
      securityLevel: 'loose',
      fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, monospace'
    }});
  </script>
</body>
</html>
"""


def extract_title(content: str, default: str) -> str:
    """Extracts first H1 title from Markdown content."""
    m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if m:
        # Strip backticks or formatting
        t = m.group(1).replace("`", "").strip()
        return t
    return default


def transform_mermaid(html_text: str) -> str:
    """
    Transforms markdown-generated mermaid code blocks into Mermaid.js compatible tags.
    Replaces: <pre><code class="language-mermaid">...</code></pre>
    With: <div class="diagram-wrapper"><pre class="mermaid">...raw unescaped text...</pre></div>
    """
    def repl(match: re.Match) -> str:
        escaped_code = match.group(1)
        raw_code = html.unescape(escaped_code).strip()
        return f'<div class="diagram-wrapper"><pre class="mermaid">\n{raw_code}\n</pre></div>'

    pattern = re.compile(r'<pre><code class="language-mermaid">(.*?)</code></pre>', re.DOTALL)
    return pattern.sub(repl, html_text)


def transform_tables(html_text: str) -> str:
    """Wraps <table> elements in <div class="table-container"> for horizontal responsiveness."""
    return re.sub(r'(<table>.*?</table>)', r'<div class="table-container">\1</div>', html_text, flags=re.DOTALL)


def transform_alerts(html_text: str) -> str:
    """
    Transforms GitHub-style alert blockquotes into styled alerts.
    Example:
    <blockquote>
    <p>[!NOTE]<br />
    Content...
    """
    alert_types = {
        "NOTE": ("alert-note", "Note"),
        "TIP": ("alert-tip", "Tip"),
        "IMPORTANT": ("alert-important", "Important"),
        "WARNING": ("alert-warning", "Warning"),
        "CAUTION": ("alert-caution", "Caution"),
    }

    def repl(m: re.Match) -> str:
        kind = m.group(1).upper()
        body = m.group(2).strip()
        if kind in alert_types:
            css_class, display_title = alert_types[kind]
            return (
                f'<div class="alert {css_class}">'
                f'<div class="alert-title">{display_title}</div>'
                f'<p>{body}</p>'
                f'</div>'
            )
        return m.group(0)

    # Match blockquotes starting with [!TYPE]
    pattern = re.compile(
        r'<blockquote>\s*<p>\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*(?:<br\s*/?>)?\s*(.*?)</p>\s*</blockquote>',
        re.DOTALL | re.IGNORECASE
    )
    return pattern.sub(repl, html_text)


def translate_links(html_text: str) -> str:
    """
    Translates relative Markdown links to HTML links where appropriate:
    - Preserves links where link text is 'Markdown' or 'View Markdown'
    - Converts links pointing to *_sut-report.md to *_sut-report.html in prose
    - Converts links pointing to README.md in prose to README.html
    """
    def link_repl(m: re.Match) -> str:
        full_tag = m.group(0)
        href = m.group(1)
        link_inner = m.group(2)
        plain_text = re.sub(r'<[^>]+>', '', link_inner).strip()

        # If the link text explicitly mentions Markdown, preserve the .md link
        if re.search(r'\bMarkdown\b', plain_text, re.IGNORECASE):
            return full_tag

        # If pointing to an SUT report in prose, link to the HTML companion
        if "_sut-report.md" in href:
            new_href = href.replace("_sut-report.md", "_sut-report.html")
            return f'<a href="{new_href}">{link_inner}</a>'

        # If pointing to README.md in prose, link to README.html
        if href == "README.md":
            return f'<a href="README.html">{link_inner}</a>'

        return full_tag

    pattern = re.compile(r'<a\s+href="([^"]+)">([\s\S]*?)</a>')
    return pattern.sub(link_repl, html_text)


def build_html_file(md_path: Path) -> Path:
    """Converts a single Markdown file to its companion HTML file."""
    md_content = md_path.read_text(encoding="utf-8")
    stem = md_path.stem
    is_readme = (stem == "README")
    now_utc = datetime.now(timezone.utc)
    gen_time_iso = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    gen_time_display = now_utc.strftime("%Y-%m-%d %H:%M UTC")

    # Project metadata
    if is_readme:
        doc_type = "pedagogical-sut-index"
        project_slug = "portfolio-pedagogical-reports"
        tier_label = "Catalog Index"
        page_title = "Portfolio Pedagogical SUT Architecture & Testability Reports"
        badge_html = '<span class="badge badge-index">Catalog &amp; Navigation Hub</span>'
        nav_left_content = (
            f'<a href="README.html" class="nav-link" style="font-weight:700;">🏠 SUT Reports Hub</a>'
            f'{badge_html}'
        )
        nav_right_content = (
            f'<a href="README.md" class="nav-link" title="View Markdown Source">📄 View Markdown (README.md)</a>'
            f'<a href="../README.md" class="nav-link">📂 Portfolio Root</a>'
        )
    else:
        doc_type = "pedagogical-sut-report"
        project_slug = stem.replace("_sut-report", "")
        if project_slug in TIER_1_PROJECTS:
            tier_label = "Tier 1: First-Party / In-Repo SUT"
            badge_html = '<span class="badge badge-tier1">Tier 1: In-Repo SUT</span>'
        elif project_slug in TIER_2_PROJECTS:
            tier_label = "Tier 2: Containerised / Pinned External SUT"
            badge_html = '<span class="badge badge-tier2">Tier 2: Containerised SUT</span>'
        else:
            tier_label = "Pedagogical SUT"
            badge_html = '<span class="badge badge-index">SUT Architecture</span>'

        extracted_title = extract_title(md_content, f"Pedagogical Report: {project_slug}")
        page_title = f"{extracted_title} — Pedagogical SUT Architecture Report"

        nav_left_content = (
            f'<a href="README.html" class="nav-link">&larr; SUT Reports Catalog</a>'
            f'{badge_html}'
            f'<span style="font-size:0.85rem; color:var(--text-muted); font-weight:600;">{project_slug}</span>'
        )
        nav_right_content = (
            f'<a href="{md_path.name}" class="nav-link" title="View Markdown Source">📄 View Markdown Source</a>'
            f'<a href="https://github.com/GBrooks1970/{project_slug}" target="_blank" rel="noopener noreferrer" class="nav-link">GitHub ↗</a>'
        )

    # Markdown to HTML conversion
    md_parser = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])
    raw_html = md_parser.convert(md_content)

    # Post-processing transforms
    processed_html = transform_mermaid(raw_html)
    processed_html = transform_tables(processed_html)
    processed_html = transform_alerts(processed_html)
    processed_html = translate_links(processed_html)

    # Assemble complete HTML
    html_output = HTML_TEMPLATE.format(
        source_file=md_path.name,
        doc_type=doc_type,
        project_slug=project_slug,
        tier_label=tier_label,
        generation_time=gen_time_iso,
        generation_display=gen_time_display,
        page_title=page_title,
        nav_left_content=nav_left_content,
        nav_right_content=nav_right_content,
        main_content=processed_html,
    )

    out_path = md_path.with_suffix(".html")
    out_path.write_text(html_output, encoding="utf-8")
    return out_path


def verify_generated_files(html_files: list[Path]) -> None:
    """Verifies that all generated HTML files meet portfolio quality gates."""
    print("\n--- Verifying Generated HTML Files ---")
    errors = []
    total_diagrams = 0
    total_tables = 0

    for path in html_files:
        if not path.exists():
            errors.append(f"Missing file: {path.name}")
            continue
        size = path.stat().st_size
        if size == 0:
            errors.append(f"Empty file: {path.name}")
            continue

        content = path.read_text(encoding="utf-8")

        # Check DOCTYPE and closing tags
        if not content.startswith("<!doctype html>"):
            errors.append(f"{path.name}: Missing <!doctype html>")
        if "</html>" not in content:
            errors.append(f"{path.name}: Incomplete HTML document (missing </html>)")

        # Count diagrams and tables
        diagrams = re.findall(r'<pre class="mermaid">\s*(.*?)\s*</pre>', content, re.DOTALL)
        tables = re.findall(r'<table\b', content)
        total_diagrams += len(diagrams)
        total_tables += len(tables)

        # Check for unrendered raw markdown code blocks for mermaid
        if '<code class="language-mermaid">' in content:
            errors.append(f"{path.name}: Found untransformed <code class=\"language-mermaid\">")

        # Check for dangling broken table links in README.html
        if path.name == "README.html":
            # Ensure README.html links to both .md and .html for every project
            for proj in list(TIER_1_PROJECTS) + list(TIER_2_PROJECTS):
                if f'href="{proj}_sut-report.md"' not in content:
                    errors.append(f"README.html missing Markdown link for {proj}")
                if f'href="{proj}_sut-report.html"' not in content:
                    errors.append(f"README.html missing HTML link for {proj}")

        print(f"  [VERIFIED] {path.name:<48} | {len(diagrams)} diagram(s) | {len(tables)} table(s) | {size:,} bytes")

    print(f"\nVerification Summary:")
    print(f"  Files checked:   {len(html_files)}")
    print(f"  Total diagrams:  {total_diagrams}")
    print(f"  Total tables:    {total_tables}")

    if errors:
        print(f"  Errors found:    {len(errors)}")
        for err in errors:
            print(f"    - {err}")
        sys.exit(1)
    else:
        print(f"  Result:          100% PASSED (0 errors)\n")


def main():
    print(f"Scanning reports in: {REPORTS_DIR}")
    if not REPORTS_DIR.exists():
        sys.exit(f"Directory not found: {REPORTS_DIR}")

    md_files = sorted(REPORTS_DIR.glob("*.md"))
    if not md_files:
        sys.exit(f"No Markdown files found in {REPORTS_DIR}")

    print(f"Found {len(md_files)} Markdown files to process.")
    generated = []

    for md_file in md_files:
        html_file = build_html_file(md_file)
        generated.append(html_file)

    verify_generated_files(generated)
    print(f"Successfully generated and verified {len(generated)} HTML companion files in {REPORTS_DIR.name}/.")


if __name__ == "__main__":
    main()
