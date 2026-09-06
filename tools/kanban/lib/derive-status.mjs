/**
 * Status derivation and stats recomputation for the shared Kanban generator.
 *
 * This is the load-bearing rule, carried over VERBATIM from the auth-separation
 * exemplar's scripts/sync-kanban-status.mjs (see that file's header for the full
 * rationale and the two hand-closure traps that produced it). The single change
 * here is generalisation: the exemplar hard-codes `AUTH-` ids and reads a board
 * payload; this module takes plain data so any project's backlog can drive it.
 *
 * WHERE AUTHORITY LIVES — unchanged from the exemplar:
 *   the backlog       owns which tickets are Done and which are Parked (human
 *                     decisions, classified by the adapter).
 *   the content graph owns each ticket's dependency edges (blockedBy).
 *   Ready vs Backlog  is authored by NEITHER — it is derived from the two above.
 *
 * PARKED is scope, not progress. A parked ticket never derives to Ready however
 * its dependencies resolve, because dependency-readiness and being-in-scope are
 * different questions. SCOPE BEATS DEPENDENCY-READINESS.
 *
 * Readiness is a property of the whole graph and must be computed, never
 * transcribed, and it is NEVER derived from `blocks` — only from `blockedBy`.
 */

/**
 * Column order, left to right. Parked sits after Done, outside the
 * Backlog -> Done flow, because it is not a stage of that flow: parked tickets
 * are out of scope, not queued. This order is mirrored by the board renderer.
 */
export const COLUMNS = ['Backlog', 'Ready', 'In Progress', 'In Review', 'Done', 'Parked'];

/** Statuses a human sets deliberately (on the board, or in an in-flight-aware
 *  backlog dialect); derivation preserves them rather than overwriting them. */
export const IN_FLIGHT = new Set(['In Progress', 'In Review']);

/**
 * Derive one ticket's column.
 *
 * @param {{id:string, blockedBy:string[]}} ticket
 * @param {Set<string>} done    ids the backlog marks Done
 * @param {Set<string>} parked  ids the backlog marks Parked
 * @param {string|undefined} prior  the ticket's previous board status, used only
 *   to preserve a human-set In Progress / In Review; anything else is ignored.
 * @returns {string} one of COLUMNS
 */
export function deriveStatus(ticket, done, parked, prior) {
  if (done.has(ticket.id)) return 'Done';
  // Scope beats dependency-readiness: an out-of-scope ticket is not startable
  // no matter what its blockers have done.
  if (parked.has(ticket.id)) return 'Parked';
  // A human moved this card into an in-flight lane; never clobber that.
  if (IN_FLIGHT.has(prior)) return prior;
  // Readiness is computed from the graph, never transcribed, and only from
  // blockedBy — never from `blocks`.
  return ticket.blockedBy.every((d) => done.has(d)) ? 'Ready' : 'Backlog';
}

/**
 * Apply {@link deriveStatus} across a ticket list, returning a new list with each
 * ticket's `status` set. Input order is preserved (determinism).
 *
 * @param {Array} tickets  header tickets carrying id, blockedBy, backlogStatus
 * @param {Map<string,string>} [prior]  id -> previous board status (in-flight preservation)
 */
export function deriveAll(tickets, prior = new Map()) {
  const done = new Set(tickets.filter((t) => t.backlogStatus === 'Done').map((t) => t.id));
  const parked = new Set(tickets.filter((t) => t.backlogStatus === 'Parked').map((t) => t.id));
  return tickets.map((t) => ({ ...t, status: deriveStatus(t, done, parked, prior.get(t.id)) }));
}

/**
 * Recompute the stats payload from derived tickets. Field order is fixed so the
 * serialised JSON is deterministic. `generatedAt` is intentionally excluded here
 * and stamped by the caller — it is the one field excluded from the drift diff.
 *
 * byStatus follows COLUMN order and omits empty columns. byPhase / byPriority /
 * byType tally only tickets that carry that field (no `undefined` bucket).
 */
export function computeStats(tickets) {
  const tally = (key) => {
    const acc = {};
    for (const t of tickets) {
      const v = t[key];
      if (v === undefined || v === null) continue;
      acc[v] = (acc[v] ?? 0) + 1;
    }
    return acc;
  };
  const statusCounts = tally('status');
  return {
    total: tickets.length,
    byStatus: Object.fromEntries(COLUMNS.filter((c) => statusCounts[c]).map((c) => [c, statusCounts[c]])),
    byPhase: tally('phase'),
    byPriority: tally('priority'),
    byType: tally('type'),
  };
}
