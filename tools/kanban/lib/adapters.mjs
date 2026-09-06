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
 */
export function authTable(text) {
  const tickets = [];
  for (const line of text.split(/\r?\n/)) {
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
      blockedBy: emptyish(cells[5]) ? [] : backtickedIds(cells[5]),
      backlogStatus,
    });
  }
  return tickets;
}

/**
 * risk-block (SCAFFOLD ONLY, PRE-CLASSIFIED — not the shipping path).
 *
 * Reads a templated risk backlog of the shape:
 *   #### Risk #3: Some risk title — Score: 21
 *   **Status:** IN PROGRESS
 * Ids are synthesised as RISK-<N>. The authored status maps straight to a final
 * column (no graph recomputation — a risk has no dependency edges):
 *   COMPLETE    -> Done
 *   IN PROGRESS -> In Progress
 *   READY START -> Ready
 *   BLOCKED     -> Backlog
 * `backlogStatus` (the canonical four-value field) is set to the nearest of
 * Done | Ready | Backlog for schema completeness.
 *
 * Scaffold status: parsing and mapping are implemented and unit-tested, but this
 * dialect carries no phase and no dependency edges, so its boards are header-only
 * queues. The drift-gate and every migrated repo use auth-table.
 */
export function riskBlock(text) {
  const tickets = [];
  const re = /^####\s+Risk\s+#(\d+):\s*(.+?)\s*[—-]\s*Score:\s*(\d+)\s*$/gm;
  let m;
  while ((m = re.exec(text)) !== null) {
    const [, n, title, score] = m;
    // The Status line is the first **Status:** after this heading.
    const statusLine = text.slice(re.lastIndex).match(/^\s*\*\*Status:\*\*\s*(.+)$/m);
    const word = statusLine ? statusLine[1].trim().toUpperCase() : '';
    let status = 'Backlog';
    let backlogStatus = 'Backlog';
    if (/\bCOMPLETE\b/.test(word)) (status = 'Done'), (backlogStatus = 'Done');
    else if (/\bIN\s+PROGRESS\b/.test(word)) (status = 'In Progress'), (backlogStatus = 'Ready');
    else if (/\bREADY\s+START\b/.test(word)) (status = 'Ready'), (backlogStatus = 'Ready');
    else if (/\bBLOCKED\b/.test(word)) (status = 'Backlog'), (backlogStatus = 'Backlog');
    tickets.push({ id: `RISK-${n}`, title, score: Number(score), blockedBy: [], backlogStatus, status });
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
