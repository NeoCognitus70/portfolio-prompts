"""Deterministic review discovery, provenance and public export."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

import markdown
import yaml

LIBRARY = Path(__file__).resolve().parent.parent
PUBLIC_ROLES = {"showcase", "methodology"}
STAMP = re.compile(r"\d{8}T\d{4}Z")
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise ValueError(f"Git source unavailable in {repo.name}: {' '.join(args)}")
    return result.stdout.strip()


def blob(repo: Path, ref: str, path: str) -> str | None:
    result = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{path}"], capture_output=True)
    return result.stdout.decode("utf-8-sig").replace("\r\n", "\n") if result.returncode == 0 else None


def published_ref(repo: Path) -> str | None:
    try:
        ref = git(repo, "symbolic-ref", "refs/remotes/origin/HEAD")
    except ValueError:
        ref = "refs/remotes/origin/main"
    try:
        return git(repo, "rev-parse", "--verify", ref)
    except ValueError:
        return None


def metadata(index: str, executive: str, timestamp: str) -> dict:
    text = index + "\n" + executive
    reviewer = re.search(r"\*\*Reviewer:\*\*\s*([^\r\n]+)", text)
    grade = re.search(r"(?:\*\*(?:Overall )?Grade:\*\*\s*|^## (?:Overall )?Grade:\s*|^\|\s*(?:Overall )?Grade\s*\|\s*)(?:\*\*)?([A-F][+-]?)(?=\s|\*|\|)", text, re.M)
    date = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]}T{timestamp[9:11]}:{timestamp[11:13]}Z"
    return {"reviewer": reviewer[1].rstrip(" \\") if reviewer else "Not recorded", "grade": grade[1] if grade else "Not assigned", "date": date}


def discover(workspace: Path, registry_path: Path) -> dict:
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    projects = []
    for row in registry["projects"]:
        name = row["project"]
        repo = workspace / name
        if not repo.is_dir():
            raise ValueError(f"Missing registered checkout: {name}")
        ref = published_ref(repo)
        rel = row.get("deviations", {}).get("reviews", ".review")
        directory = workspace / rel if rel.startswith(name + "/") else repo / rel
        project = {"project": name, "github": row["github"], "role": row["presentation_role"], "status": row["status"], "commit": ref, "reviews": [], "focused": []}
        for child in sorted(directory.iterdir()) if directory.is_dir() else []:
            if child.is_dir() and child.name.startswith("CODE_REVIEW_"):
                stamp = STAMP.search(child.name)
                indexes = sorted(child.glob("00_*.md"))
                executive = child / "01_EXECUTIVE_SUMMARY.md"
                if not stamp or len(indexes) != 1 or not executive.is_file():
                    raise ValueError(f"Incomplete or ambiguous review bundle: {name}/{child.name}")
                files = {"index": indexes[0], "executive": executive}
                contents = {key: path.read_text(encoding="utf-8-sig") for key, path in files.items()}
                paths = {key: path.relative_to(repo).as_posix() for key, path in files.items()}
                published = ref is not None and all(blob(repo, ref, paths[key]) == contents[key] for key in files)
                project["reviews"].append({"bundle": child.name, "timestamp": stamp[0], **paths, "published": published, **metadata(contents["index"], contents["executive"], stamp[0]), "summary": contents["executive"]})
            elif child.is_file() and re.match(r"\d{4}-\d{2}-\d{2}_.+\.md$", child.name):
                path = child.relative_to(repo).as_posix()
                project["focused"].append({"path": path, "date": child.name[:10], "published": ref is not None and blob(repo, ref, path) == child.read_text(encoding="utf-8-sig")})
        project["reviews"].sort(key=lambda r: (r["timestamp"], r["bundle"]), reverse=True)
        projects.append(project)
    return {"registryCommit": git(registry_path.parent, "rev-parse", "HEAD"), "projects": projects}


def source_link(project: dict, path: str, public: bool, fragment: str = "", directory: bool = False) -> str:
    if public:
        if not project["commit"]:
            raise ValueError("Unpublished source cannot enter public output")
        kind = "tree" if directory else "blob"
        target = f"https://github.com/{project['github']}/{kind}/{project['commit']}/{path.rstrip('/')}"
    else:
        target = f"../{project['project']}/{path}" + ("/" if directory else "")
    return target + ("#" + fragment if fragment else "")


def clean_summary(text: str, project: dict, review: dict, workspace: Path, projects: list[dict], public: bool) -> str:
    lines = [line for line in text.splitlines() if not re.match(r"^# (?:Section 1: |01\. )?Executive Summary", line) and not re.search(r"\[(?:[^\]]*Back to Index|<- Previous|Next[^\]]*)\]", line)]
    repo = workspace / project["project"]
    def link(match):
        label, url = match.groups()
        if url.startswith("https://"):
            return match[0]
        if url.startswith(("http://", "file:", "mailto:")):
            raise ValueError(f"Unsupported review URL: {url}")
        path, _, fragment = url.partition("#")
        candidates = [(repo / review["executive"]).parent / unquote(path), repo / unquote(path)] if path else [repo / review["executive"]]
        resolved = next((p.resolve() for p in candidates if p.exists() and p.resolve().is_relative_to(workspace)), None)
        if resolved is None:
            raise ValueError(f"Unresolved summary link in {project['project']}: {url}")
        owner = next((p for p in projects if resolved.is_relative_to(workspace / p["project"])), None)
        if owner is None:
            if public:
                raise ValueError(f"Internal workspace link cannot be published: {url}")
            target = "../" + resolved.relative_to(workspace).as_posix()
            if fragment:
                target += "#" + fragment
        else:
            relative = resolved.relative_to(workspace / owner["project"]).as_posix()
            if public:
                if owner["role"] not in PUBLIC_ROLES or not owner["commit"]:
                    raise ValueError("Hidden or unpublished source in public summary")
                try:
                    git(workspace / owner["project"], "cat-file", "-e", f"{owner['commit']}:{relative}")
                except ValueError as exc:
                    raise ValueError(f"Unpublished linked source: {owner['project']}/{relative}") from exc
            target = source_link(owner, relative, public, fragment, resolved.is_dir())
        return f"[{label}]({target})"
    return LINK.sub(link, "\n".join(lines).strip())


def rendered_markdown(text: str) -> str:
    # Reviews are data, never executable HTML. Tables and Markdown remain formatted.
    rendered = markdown.markdown(html.escape(text, quote=False), extensions=["tables", "fenced_code"])
    return re.sub(r"<(/?)h([1-6])>", lambda m: f"<{m[1]}h{min(6, max(4, int(m[2]) + 2))}>", rendered)


STYLE = """*{box-sizing:border-box}body{margin:0;padding:2rem;background:#0f172a;color:#f8fafc;font:16px/1.6 system-ui,sans-serif}.container{max-width:1200px;margin:auto;min-width:0}h1,h2{border-bottom:1px solid #334155;padding-bottom:.4rem}h2,a{color:#38bdf8}a:hover{color:#7dd3fc}p,li,td{color:#cbd5e1}a:focus-visible,summary:focus-visible,.table-scroll:focus-visible{outline:3px solid #fbbf24;outline-offset:3px}.table-scroll{overflow-x:auto;margin:1rem 0;max-width:100%}table{min-width:52rem;width:100%;border-collapse:collapse}th,td{padding:.75rem;text-align:left;border-bottom:1px solid #334155;vertical-align:top}th{color:#e2e8f0}.card{background:#1e293b;padding:1.5rem;border:1px solid #334155;border-radius:8px;margin:1rem 0}.card,p,li,td,code,a{overflow-wrap:anywhere}code{font-size:.9em}summary{cursor:pointer;font-weight:600;color:#38bdf8}details{padding:1rem;border:1px solid #334155;border-radius:6px;margin-top:1rem}nav{margin-bottom:1rem}@media(max-width:600px){body{padding:1rem}.card{padding:1rem}}"""


def render(catalog: dict, workspace: Path, since: str, public: bool) -> tuple[str, str, dict]:
    visible = [p for p in catalog["projects"] if not public or p["role"] in PUBLIC_ROLES]
    selected = []
    recent = []
    focused = []
    missing = []
    for p in visible:
        reviews = [r for r in p["reviews"] if not public or r["published"]]
        if reviews:
            selected.append((p, reviews[0]))
        else:
            missing.append(p)
        recent.extend((p, r) for r in reviews if r["date"][:10] >= since)
        focused.extend((p, r) for r in p["focused"] if r["date"] >= since and (not public or r["published"]))
    scope = "public" if public else "registered"
    lines = ["# Portfolio Code Reviews — Central Index & Latest Summaries", "", f"Latest summaries for **{len(selected)} {scope} projects**, with all {len(recent)} review bundles dated {since} or later and {len(focused)} focused records.", "", "Reviews are dated assessments, not current remediation status or new test executions. Lifecycle labels come from the captured registry. Letter grades are attributed reviewer judgements; Not assigned means no explicit overall grade was recorded.", "", "## Registered projects without a review in the matrix", ""]
    for p in missing:
        reason = "no published comprehensive review bundle" if public else "no comprehensive review bundle"
        if p["role"] == "hidden":
            reason += "; hidden/private registry member, internal coverage only"
        lines.append(f"- `{p['project']}`: {reason}.")
    if not missing:
        lines.append("All projects in this scope have a review bundle.")
    lines += ["", f"## Review bundles since {since}", "", "| Project | Review bundle | Publication | Links |", "|---|---|---|---|"]
    for p, r in recent:
        status = "Published" if r["published"] else "Local only — not published"
        lines.append(f"| `{p['project']}` | `{r['bundle']}` | {status} | [Full review]({source_link(p,r['index'],public)})<br>[Executive summary]({source_link(p,r['executive'],public)}) |")
    lines += ["", "## Focused review and confirmation records", "", "| Project | Record | Publication |", "|---|---|---|"]
    for p, r in focused:
        status = "Published" if r["published"] else "Local only — not published"
        lines.append(f"| `{p['project']}` | [{Path(r['path']).name}]({source_link(p,r['path'],public)}) | {status} |")
    if not public:
        structural = sorted((workspace / "portfolio-docs/structural-reviews").glob("*/PORTFOLIO_STRUCTURAL_REVIEW*.md"))
        if structural:
            path = structural[-1].relative_to(workspace).as_posix()
            lines += ["", "## Internal portfolio-level review", "", f"The [portfolio structural review](../{path}) is an internal support-repository assessment. It is excluded from the public export."]
    lines += ["", "## Latest Reviews Matrix", "", "| Project | Status | Latest Review | Date | Reviewer | Grade | Links |", "|---|---|---|---|---|---|---|"]
    for p, r in selected:
        reviewer = html.escape(r['reviewer']).replace('|', '\\|')
        lines.append(f"| `{p['project']}` | {p['status']} | `{r['bundle']}` | {r['date']} | {reviewer} | {r['grade']} | [Full Review]({source_link(p,r['index'],public)})<br>[Executive Summary]({source_link(p,r['executive'],public)}) |")
    intro = "\n".join(lines)
    # Metadata links are generated, never copied from untrusted HTML.
    rendered_intro = markdown.markdown(intro, extensions=["tables"])
    sections = []
    lines += ["", "## Detailed Executive Summaries per Project", ""]
    for p, r in selected:
        summary = clean_summary(r['summary'], p, r, workspace, catalog['projects'], public)
        links = f"[Full review]({source_link(p,r['index'],public)}) · [Executive summary]({source_link(p,r['executive'],public)})"
        lines += [f"### {p['project']}", "", f"**Review:** `{r['bundle']}` · **Date:** {r['date']} · **Grade:** {r['grade']}", "", links, "", "<details><summary>Executive summary</summary>", "", summary, "", "</details>", ""]
        sections.append(f'<div class="card" id="review-{html.escape(p["project"])}" data-review-project="{html.escape(p["project"])}"><h3>{html.escape(p["project"])}</h3><p><strong>Latest review:</strong> <code>{html.escape(r["bundle"])}</code><br><strong>Date:</strong> {r["date"]} · <strong>Grade:</strong> {r["grade"]}</p>{markdown.markdown(links)}<details><summary>Executive summary</summary>{rendered_markdown(summary)}</details></div>')
    document = f'<!DOCTYPE html>\n<html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Portfolio Code Reviews — Central Index</title><style>{STYLE}</style></head><body><main class="container">{rendered_intro}<h2>Detailed Executive Summaries per Project</h2>{"".join(sections)}</main></body></html>\n'
    document = document.replace('<table>', '<div class="table-scroll" tabindex="0" role="region" aria-label="Review table"><table>').replace('</table>', '</table></div>')
    unique = {(p['project'], r['bundle']): (p, r) for p, r in selected + recent}
    manifest = {"schemaVersion": 1, "registryCommit": catalog["registryCommit"], "recentSince": since, "repositories": {p['project']:p['github'] for p in visible}, "reviewProjects": [p['project'] for p, _ in selected], "reviewBundles": [{"project":p['project'], "bundle":r['bundle'], "commit":p['commit'], "index":source_link(p,r['index'],public), "executive":source_link(p,r['executive'],public)} for p, r in unique.values()], "focusedReviews": [{"project":p['project'], "url":source_link(p,r['path'],public)} for p,r in focused]}
    if public:
        for p in catalog['projects']:
            if p['role'] not in PUBLIC_ROLES and any(token in document for token in [p['project'], p['github']]):
                raise ValueError("Hidden project content found in public export")
        if re.search(r'(?:file://|(?<![A-Za-z])[A-Za-z]:[\\/]|href="\.\./)', document):
            raise ValueError("Local or workspace path in public export")
        manifest['htmlSha256'] = hashlib.sha256(document.encode()).hexdigest()
    return '\n'.join(lines).rstrip()+'\n', document, manifest


def build(workspace: Path, registry: Path, output: Path, since: str, check: bool = False) -> dict:
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', since):
        raise ValueError('since must be YYYY-MM-DD')
    catalog = discover(workspace.resolve(), registry.resolve())
    md, internal, _ = render(catalog, workspace.resolve(), since, False)
    _, public, manifest = render(catalog, workspace.resolve(), since, True)
    outputs = {'README.md':md, 'index.html':internal, 'public-index.html':public, 'public-manifest.json':json.dumps(manifest, indent=2, ensure_ascii=False)+'\n'}
    for name, text in outputs.items():
        path = output / name
        if check:
            if not path.is_file() or path.read_bytes() != text.encode('utf-8'):
                raise ValueError(f'Stale review output: {name}')
        else:
            output.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8', newline='\n')
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--portfolio-root', type=Path, default=LIBRARY.parent)
    parser.add_argument('--registry', type=Path, default=LIBRARY/'registry.yml')
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--since', default='1970-01-01', help='Inclusive date for the review archive and focused records')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args(argv)
    try:
        result = build(args.portfolio_root, args.registry, args.output_dir or args.portfolio_root/'portfolio-reviews', args.since, args.check)
    except (OSError, ValueError, KeyError) as exc:
        print(f'build-portfolio-reviews: ERROR — {exc}', file=sys.stderr)
        return 1
    print(f"build-portfolio-reviews: PASS — {len(result['reviewProjects'])} public project summaries, {len(result['reviewBundles'])} indexed bundles, {len(result['focusedReviews'])} focused records")
    return 0
