/**
 * Content override: the optional, per-project body of each ticket.
 *
 * The backlog owns a ticket's header (id, title, type, priority, score, phase,
 * dependency edges, status). The override — docs/kanban-content.json by default —
 * owns only its BODY: the prose a card expands to. Keeping them apart is decision
 * D5: one shared generator, plus an optional per-project content file, so a board
 * can carry rich acceptance criteria without forking the generator.
 *
 * The split is enforced, not merely documented:
 *   - an override entry for an id the backlog does not list is a HARD ERROR (a
 *     card body with no card is always a mistake — a typo'd id, or content left
 *     behind when a ticket was renamed);
 *   - a backlog id with no override entry is FINE (a header-only card);
 *   - an override entry may carry ONLY body fields. Any header field
 *     (status, backlogStatus, blockedBy, title, type, priority, score, phase,
 *     blocks, id) in the override is a hard error: it would let content quietly
 *     contradict the backlog, which is exactly the drift this tool prevents.
 */
import { readFileSync, existsSync, readdirSync } from 'node:fs';

/** The only keys an override entry may carry. */
export const BODY_FIELDS = ['description', 'acceptance', 'spec', 'adr', 'assignee'];
const BODY_SET = new Set(BODY_FIELDS);
const ADR_ID_RE = /^ADR-\d{4}$/;

/** Load and JSON-parse the override file. Absent file -> {} (overrides optional). */
export function loadOverride(path) {
  if (!existsSync(path)) return {};
  let raw;
  try {
    raw = readFileSync(path, 'utf8');
  } catch (e) {
    throw new Error(`override: cannot read ${path}: ${e.message}`);
  }
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (e) {
    throw new Error(`override: ${path} is not valid JSON: ${e.message}`);
  }
  if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
    throw new Error(`override: ${path} must be a JSON object keyed by ticket id`);
  }
  return parsed;
}

/**
 * Validate the override against the set of backlog ids. Returns a list of problem
 * strings (empty = clean); the caller decides that any problem fails the run.
 */
export function validateOverride(override, backlogIds) {
  const ids = new Set(backlogIds);
  const problems = [];
  for (const [id, body] of Object.entries(override)) {
    if (!ids.has(id)) {
      problems.push(`override names ${id}, which is not a ticket in the backlog`);
      continue;
    }
    if (body === null || typeof body !== 'object' || Array.isArray(body)) {
      problems.push(`override entry ${id} must be an object of body fields`);
      continue;
    }
    for (const key of Object.keys(body)) {
      if (!BODY_SET.has(key)) {
        problems.push(
          `override entry ${id} carries non-body field '${key}' — the override may hold only ` +
            `${BODY_FIELDS.join(', ')} (header fields are owned by the backlog)`,
        );
      }
    }
    if ('acceptance' in body && !(Array.isArray(body.acceptance) && body.acceptance.every((a) => typeof a === 'string'))) {
      problems.push(`override entry ${id}: acceptance must be an array of strings`);
    }
    if ('adr' in body) {
      if (!Array.isArray(body.adr)) {
        problems.push(`override entry ${id}: adr must be an array of ADR-nnnn ids`);
      } else {
        for (const ref of body.adr) {
          if (typeof ref !== 'string' || !ADR_ID_RE.test(ref)) {
            problems.push(`override entry ${id}: adr entry '${ref}' must match ADR-nnnn (four digits)`);
          }
        }
      }
    }
  }
  return problems;
}

/**
 * Merge body fields onto header tickets, and compute `blocks` as the reverse of
 * the blockedBy graph. `blocks` is DISPLAY-ONLY: derive-status.mjs never reads it,
 * so populating it cannot affect readiness. Output field order is fixed for
 * deterministic serialisation.
 */
export function mergeContent(headerTickets, override) {
  // Reverse edges: b in blocks[a] iff a in blockedBy[b].
  const blocks = new Map(headerTickets.map((t) => [t.id, []]));
  for (const t of headerTickets) {
    for (const dep of t.blockedBy) {
      if (blocks.has(dep)) blocks.get(dep).push(t.id);
    }
  }
  return headerTickets.map((t) => {
    const body = override[t.id] ?? {};
    const out = {
      id: t.id,
      title: t.title,
      ...(t.type !== undefined ? { type: t.type } : {}),
      ...(t.priority !== undefined ? { priority: t.priority } : {}),
      ...(t.score !== undefined ? { score: t.score } : {}),
      ...(t.phase !== undefined ? { phase: t.phase } : {}),
      blockedBy: t.blockedBy,
      blocks: blocks.get(t.id),
      backlogStatus: t.backlogStatus,
      status: t.status,
      ...(body.description !== undefined ? { description: body.description } : {}),
      ...(body.acceptance !== undefined ? { acceptance: body.acceptance } : {}),
      ...(body.spec !== undefined ? { spec: body.spec } : {}),
      ...(body.adr !== undefined ? { adr: body.adr } : {}),
      ...(body.assignee !== undefined ? { assignee: body.assignee } : {}),
    };
    return out;
  });
}

/**
 * Resolve every ADR citation to a file in the ADR directory. A citation is any
 * `ADR-nnnn` appearing anywhere in a ticket (adr[] list, spec note, description).
 * Ported from the exemplar's validate-kanban-content.mjs check 2: it catches
 * typos, renumbering, and deletions.
 *
 * Returns a list of problem strings. If the ADR directory is absent, citations
 * are a problem (they point nowhere); no citations and no directory is clean.
 */
export function resolveAdrCitations(tickets, adrDir) {
  const cited = new Map(); // ADR-nnnn -> [ticket ids]
  for (const t of tickets) {
    for (const ref of new Set(JSON.stringify(t).match(/ADR-\d{4}/g) ?? [])) {
      if (!cited.has(ref)) cited.set(ref, []);
      cited.get(ref).push(t.id);
    }
  }
  if (cited.size === 0) return [];

  const adrFiles = existsSync(adrDir)
    ? readdirSync(adrDir).filter((f) => /^\d{4}-.*\.md$/.test(f))
    : null;
  const problems = [];
  for (const [ref, ids] of cited) {
    const number = ref.slice(4); // strip "ADR-"
    const exists = adrFiles && adrFiles.some((f) => f.startsWith(number));
    if (!exists) {
      problems.push(
        adrFiles === null
          ? `${ids.join(', ')} cite ${ref}, but no ADR directory exists at ${adrDir}/`
          : `${ids.join(', ')} cite ${ref}, which has no file in ${adrDir}/`,
      );
    }
  }
  return problems;
}
