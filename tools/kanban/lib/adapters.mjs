/**
 * Backlog adapters: turn a project's human-authored backlog into header tickets.
 *
 * An adapter is pluggable and MUST fail loudly on a backlog it cannot parse — a
 * silently-empty board is the failure mode this whole tool exists to prevent, so
 * "parsed zero tickets" is an error, never an empty success.
 *
 * A header ticket carries only what the backlog authors:
 *   { id, title, type?, priority?, score?, phase?, blockedBy[], backlogStatus,
 *     inFlight? }
 * Body fields (description, acceptance, spec, adr, assignee) come from the
 * optional content override, never from the backlog.
 *
 * `backlogStatus` is one of Done | Parked | Ready | Backlog.
 *
 * A dialect is either GRAPH-DERIVED or PRE-CLASSIFIED:
 *   - graph-derived (auth-table): the backlog authors Done/Parked but NOT
 *     Ready/Backlog; those are recomputed from the dependency graph by
 *     derive-status.mjs. This is the shipping path.
 *   - pre-classified (risk-block): the backlog authors the whole status directly
 *     (a risk has no dependency edges, so "BLOCKED" is a human decision, not a
 *     graph property). Such an adapter emits a final `status` and the generator
 *     passes it through without graph recomputation.
 */

/** Pull every backticked `TOKEN` out of a table cell, in order. */
function backtickedIds(cell) {
  return [...cell.matchAll(/`([^`]+)`/g)].map((m) => m[1]);
}

/**
 * auth-table (REQUIRED, the shipping dialect).
 *
 * Reads 7-column Markdown rows shaped exactly:
 *   | ID | Ticket | Type | Priority | Tier | Blocked by | Status |
 * A line is a ticket row iff its first cell is a single backticked id AND the row
 * has exactly seven cells — which keeps us clear of closure-record tables, prose
 * tables, and the summary tables that share the file.
 *
 * Status is keyword-classified, not matched exactly, because the Status cell
 * carries dates, ADR references and explanatory clauses alongside the word.
 * Parked is tested FIRST so "Parked (..., see ADR-0005)" cannot be misread as
 * anything else; then Done, then Ready, else Backlog. blockedBy is read from the
 * "Blocked by" cell (cell 6). Tier (cell 5) is informational and not carried:
 * it duplicates Priority and is not a canonical ticket field.
 *
 * `phase` (D7) is derived structurally, not from a cell: the backlog groups its
 * ticket tables under "Phase N" section headings (e.g. "### Phase 3 — Core
 * implementation"). Scanning top-to-bottom, the most recent such heading sets the
 * phase for every ticket row beneath it, until the next heading resets it. Rows
 * before any Phase heading get no phase. `phase` is a backlog-owned header field,
 * so it comes from here and never from the content override.
 */
export function authTable(text) {
  const tickets = [];
  let phase; // current phase from the most recent "Phase N" heading; unset before the first
  for (const line of text.split(/\r?\n/)) {
    const phaseHeading = line.match(/^#{1,4}\s+Phase\s+(\d+)\b/);
    if (phaseHeading) {
      phase = Number(phaseHeading[1]);
      continue;
    }
    // Fast reject: first cell must open with a backticked id.
    if (!/^\|\s*`[^`]+`\s*\|/.test(line)) continue;
    const cells = line.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim());
    if (cells.length !== 7) continue;

    const idMatch = cells[0].match(/^`([^`]+)`$/);
    if (!idMatch) continue; // first cell is more than a bare id -> not a ticket row
    const id = idMatch[1];

    const statusCell = cells[6];
    const backlogStatus = /\bParked\b/.test(statusCell)
      ? 'Parked'
      : /\bDone\b/.test(statusCell)
        ? 'Done'
        : /\bReady\b/.test(statusCell)
          ? 'Ready'
          : 'Backlog';

    const emptyish = (s) => s === '' || s === '-' || s === '—'; // '' | '-' | em dash
    tickets.push({
      id,
      title: cells[1],
      ...(emptyish(cells[2]) ? {} : { type: cells[2] }),
      ...(emptyish(cells[3]) ? {} : { priority: cells[3] }),
      ...(phase !== undefined ? { phase } : {}),
      blockedBy: emptyish(cells[5]) ? [] : backtickedIds(cells[5]),
      backlogStatus,
    });
  }
  return tickets;
}

/**
 * risk-block (SHIPPING, PRE-CLASSIFIED).
 *
 * Reads the portfolio's shared risk-scored backlog template. Unlike auth-table
 * this dialect is PRE-CLASSIFIED: a risk carries no dependency edges, so the
 * backlog author owns the whole status and derive-status never recomputes it.
 *
 * Item headings (`####`), all requiring an explicit `Score:` so prose headings
 * can never become cards:
 *   #### Risk #3: Title — Score: 21              -> RISK-3   (canonical template)
 *   #### Risk #2 (review #1): Title — Score: 12  -> RISK-2   (qualified variant)
 *   #### Risk PBR-07: Title — Score: 10          -> PBR-07   (explicit-id variant)
 * Inside a `Resolved Risks` section a scoreless closure heading is also an item:
 *   #### Title ✅ Resolved 2026-08-07            -> RES-<slug of title>
 * Every other `####` heading — "Problem", "Impact Analysis", "Out of scope",
 * "Implementation acceptance criteria" — matches neither form and is ignored.
 *
 * Priority band comes from the enclosing `### HIGH|MEDIUM|LOW Priority` heading,
 * falling back to the score (>=20 HIGH, >=10 MEDIUM, else LOW) so a band is
 * always present to group and badge by. The renderer has no phase concept for
 * this dialect; band + score take that role.
 *
 * Body content is read from the backlog itself — `**Problem:**` (plus any
 * `**Impact Analysis:**`) becomes the description and `**Success Criteria:**`
 * checkboxes become acceptance — so a risk-scored project needs no per-project
 * content override. An override, where supplied, still wins (see mergeContent).
 *
 * Status vocabulary -> column (pre-classified pass-through):
 *   COMPLETE -> Done | IN PROGRESS -> In Progress
 *   READY TO START (or READY START) -> Ready | BLOCKED -> Backlog
 * A resolved-section entry is Done. An item with no Status line is Backlog.
 */

const BAND_RE = /^#{2,3}\s+(HIGH|MEDIUM|LOW)\s+Priority\b/i;
const RESOLVED_SECTION_RE = /^#{2,3}\s+Resolved\s+Risks?\b/i;
/** `Risk <ref>: <title> — Score: <n>`; ref is `#N`, `#N (qualifier)` or an id. */
const ITEM_RE = /^####\s+Risk\s+(#\s*\d+(?:\s*\([^)]*\))?|[A-Za-z][\w.-]*)\s*:\s*(.+?)\s*[—–-]\s*Score:\s*(\d+)\s*$/;
/** Scoreless closure heading, only meaningful inside a Resolved Risks section. */
const RESOLVED_ITEM_RE = /^####\s+(.+?)\s*(?:✅\s*)?Resolved\b.*$/;

/** Stable, readable id for a resolved entry that carries no explicit risk ref. */
function slugId(title) {
  const slug = title
    .replace(/[`*_]/g, '')
    .replace(/[^A-Za-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .toUpperCase()
    .split('-')
    .filter(Boolean)
    .slice(0, 6)
    .join('-');
  return `RES-${slug || 'ITEM'}`;
}

/** Band for a score, used when no band heading encloses the item. */
function bandForScore(score) {
  if (score === undefined) return undefined;
  if (score >= 20) return 'HIGH';
  if (score >= 10) return 'MEDIUM';
  return 'LOW';
}

/** Collect the lines of a `**Label:**` block until the next label or heading. */
function labelBlock(lines, label) {
  const head = new RegExp(`^\\*\\*${label}:\\*\\*\\s*(.*)$`);
  const out = [];
  let active = false;
  for (const line of lines) {
    const m = line.match(head);
    if (m) {
      active = true;
      if (m[1].trim()) out.push(m[1].trim());
      continue;
    }
    if (!active) continue;
    if (/^#{1,6}\s/.test(line) || /^\*\*[^*]+:\*\*/.test(line)) break;
    out.push(line);
  }
  return out.join('\n').trim();
}

export function riskBlock(text) {
  const tickets = [];
  const seen = new Set();
  const lines = text.split(/\r?\n/);

  // Index every item heading first, so a body is exactly the lines up to the next heading.
  const marks = [];
  let band;
  let inResolved = false;
  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    const bandMatch = line.match(BAND_RE);
    if (bandMatch) {
      band = bandMatch[1].toUpperCase();
      inResolved = false;
      continue;
    }
    if (RESOLVED_SECTION_RE.test(line)) {
      inResolved = true;
      band = undefined;
      continue;
    }
    const item = line.match(ITEM_RE);
    if (item) {
      const ref = item[1].replace(/\s+/g, '');
      const id = ref.startsWith('#') ? `RISK-${ref.slice(1).replace(/\(.*\)$/, '')}` : ref.toUpperCase();
      marks.push({ i, id, title: item[2].trim(), score: Number(item[3]), band, resolved: inResolved });
      continue;
    }
    if (inResolved && line.startsWith('#### ')) {
      const res = line.match(RESOLVED_ITEM_RE);
      if (res) {
        const title = res[1].replace(/[—–-]\s*$/, '').trim();
        marks.push({ i, id: slugId(title), title, score: undefined, band: undefined, resolved: true });
      }
    }
  }

  for (let n = 0; n < marks.length; n += 1) {
    const m = marks[n];
    // Body runs to the next heading of any level, or the next item, whichever comes first.
    let stop = n + 1 < marks.length ? marks[n + 1].i : lines.length;
    for (let j = m.i + 1; j < stop; j += 1) {
      if (/^#{1,6}\s/.test(lines[j]) && !/^\*\*/.test(lines[j])) { stop = j; break; }
    }
    const body = lines.slice(m.i + 1, stop);

    const statusLine = body.find((l) => /^\*\*Status:\*\*/.test(l));
    const word = statusLine ? statusLine.replace(/^\*\*Status:\*\*\s*/, '').trim().toUpperCase() : '';
    let status = m.resolved ? 'Done' : 'Backlog';
    let backlogStatus = m.resolved ? 'Done' : 'Backlog';
    if (/\bCOMPLETE\b/.test(word)) (status = 'Done'), (backlogStatus = 'Done');
    else if (/\bIN\s+PROGRESS\b/.test(word)) (status = 'In Progress'), (backlogStatus = 'Ready');
    else if (/\bREADY(?:\s+TO)?\s+START\b/.test(word)) (status = 'Ready'), (backlogStatus = 'Ready');
    else if (/\bBLOCKED\b/.test(word)) (status = 'Backlog'), (backlogStatus = 'Backlog');

    // Score may also be authored as "**Priority Score:** ... = **21 points**".
    let score = m.score;
    if (score === undefined) {
      const ps = body.find((l) => /^\*\*Priority Score:\*\*/.test(l));
      const num = ps && ps.match(/=\s*\*\*(\d+)/);
      if (num) score = Number(num[1]);
    }

    const problem = labelBlock(body, 'Problem');
    const impact = labelBlock(body, 'Impact Analysis');
    const descriptionParts = [];
    if (problem) descriptionParts.push(problem);
    if (impact) descriptionParts.push(`Impact analysis:\n${impact}`);
    const description = descriptionParts.join('\n\n');

    const criteria = labelBlock(body, 'Success Criteria');
    const acceptance = criteria
      .split(/\r?\n/)
      .map((l) => l.match(/^\s*[-*]\s*\[[ xX]\]\s*(.+?)\s*$/))
      .filter(Boolean)
      .map((x) => x[1]);

    if (seen.has(m.id)) {
      throw new Error(
        `backlog dialect 'risk-block' produced a duplicate ticket id '${m.id}' — ids must be unique; ` +
          'give the risks distinct numbers or explicit ids.',
      );
    }
    seen.add(m.id);

    const priority = m.band ?? bandForScore(score);
    tickets.push({
      id: m.id,
      title: m.title,
      ...(score !== undefined ? { score } : {}),
      ...(priority !== undefined ? { priority } : {}),
      blockedBy: [],
      backlogStatus,
      status,
      ...(description ? { description } : {}),
      ...(acceptance.length ? { acceptance } : {}),
    });
  }
  return tickets;
}

/**
 * Adapter registry. `graphDerived` decides whether derive-status.mjs recomputes
 * Ready/Backlog from the dependency graph (true) or the adapter's authored
 * `status` is passed through unchanged (false).
 */
export const ADAPTERS = {
  'auth-table': { parse: authTable, graphDerived: true },
  'risk-block': { parse: riskBlock, graphDerived: false },
};

/**
 * Run the named adapter and enforce the fail-loudly contract.
 * @returns {{tickets:Array, graphDerived:boolean}}
 * @throws if the dialect is unknown or the adapter parses zero tickets.
 */
export function parseBacklog(text, dialect) {
  const adapter = ADAPTERS[dialect];
  if (!adapter) {
    throw new Error(
      `unknown backlog dialect '${dialect}' — expected one of: ${Object.keys(ADAPTERS).join(', ')}`,
    );
  }
  const tickets = adapter.parse(text);
  if (tickets.length === 0) {
    throw new Error(
      `backlog dialect '${dialect}' parsed zero tickets — the backlog is unparseable or empty; ` +
        'a silently-empty board is never an acceptable success.',
    );
  }
  return { tickets, graphDerived: adapter.graphDerived };
}
