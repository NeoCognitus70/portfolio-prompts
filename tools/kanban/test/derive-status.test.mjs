import { test } from 'node:test';
import assert from 'node:assert/strict';
import { deriveStatus, deriveAll, computeStats, COLUMNS } from '../lib/derive-status.mjs';

/**
 * Truth table for the derive-status rule. Each row fixes the four inputs the rule
 * reads — is the id Done in the backlog, is it Parked, what was its prior board
 * status (in-flight preservation), and are all its blockedBy deps Done — and
 * asserts the single column it must land in. The rows are ordered to mirror the
 * rule's own precedence: Done > Parked > preserve-in-flight > graph(Ready|Backlog).
 */
const T = (name, { id = 'X', blockedBy = [], done = [], parked = [], prior }, expected) => ({
  name,
  ticket: { id, blockedBy },
  done: new Set(done),
  parked: new Set(parked),
  prior,
  expected,
});

const TRUTH_TABLE = [
  // Done is taken straight from the backlog and beats everything else.
  T('Done from backlog', { id: 'X', done: ['X'] }, 'Done'),
  T('Done beats an unmet blocker', { id: 'X', done: ['X'], blockedBy: ['Y'] }, 'Done'),
  T('Done beats Parked (Done checked first)', { id: 'X', done: ['X'], parked: ['X'] }, 'Done'),

  // Parked is scope, not progress: it beats dependency-readiness AND in-flight.
  T('Parked from backlog', { id: 'X', parked: ['X'] }, 'Parked'),
  T('Parked stays Parked though every blocker is Done (SCOPE BEATS READINESS)',
    { id: 'X', parked: ['X'], blockedBy: ['Y'], done: ['Y'] }, 'Parked'),
  T('Parked beats a human in-flight status', { id: 'X', parked: ['X'], prior: 'In Progress' }, 'Parked'),

  // A human-set in-flight status is preserved when not Done/Parked.
  T('preserve In Progress', { id: 'X', prior: 'In Progress' }, 'In Progress'),
  T('preserve In Review', { id: 'X', prior: 'In Review' }, 'In Review'),
  T('a non-in-flight prior is ignored and recomputed', { id: 'X', prior: 'Ready' }, 'Ready'),
  T('in-flight preservation still loses to Done', { id: 'X', done: ['X'], prior: 'In Progress' }, 'Done'),

  // Otherwise Ready iff every blockedBy is Done, else Backlog. Computed, never transcribed.
  T('no blockers -> Ready', { id: 'X', blockedBy: [] }, 'Ready'),
  T('all blockers Done -> Ready', { id: 'X', blockedBy: ['A', 'B'], done: ['A', 'B'] }, 'Ready'),
  T('one blocker unmet -> Backlog', { id: 'X', blockedBy: ['A', 'B'], done: ['A'] }, 'Backlog'),
  T('all blockers unmet -> Backlog', { id: 'X', blockedBy: ['A'], done: [] }, 'Backlog'),
];

for (const row of TRUTH_TABLE) {
  test(`deriveStatus: ${row.name}`, () => {
    assert.equal(deriveStatus(row.ticket, row.done, row.parked, row.prior), row.expected);
  });
}

test('readiness is never derived from `blocks` — a ticket that blocks others but has no unmet blockedBy is Ready', () => {
  const tickets = [
    { id: 'A', blockedBy: [], blocks: ['B', 'C'], backlogStatus: 'Backlog' },
    { id: 'B', blockedBy: ['A'], backlogStatus: 'Backlog' },
  ];
  const [a] = deriveAll(tickets);
  assert.equal(a.status, 'Ready');
});

test('deriveAll: Done/Parked sets are built from backlogStatus and applied across the list', () => {
  const tickets = [
    { id: 'A', blockedBy: [], backlogStatus: 'Done' },
    { id: 'B', blockedBy: ['A'], backlogStatus: 'Parked' },
    { id: 'C', blockedBy: ['A'], backlogStatus: 'Backlog' },
    { id: 'D', blockedBy: ['C'], backlogStatus: 'Ready' },
  ];
  const out = Object.fromEntries(deriveAll(tickets).map((t) => [t.id, t.status]));
  assert.deepEqual(out, { A: 'Done', B: 'Parked', C: 'Ready', D: 'Backlog' });
});

test('deriveAll: input order is preserved (determinism)', () => {
  const tickets = [
    { id: 'Z', blockedBy: [], backlogStatus: 'Backlog' },
    { id: 'A', blockedBy: [], backlogStatus: 'Backlog' },
    { id: 'M', blockedBy: [], backlogStatus: 'Backlog' },
  ];
  assert.deepEqual(deriveAll(tickets).map((t) => t.id), ['Z', 'A', 'M']);
});

test('computeStats: byStatus follows COLUMN order and omits empty columns', () => {
  const tickets = [
    { id: 'A', status: 'Done', priority: 'P0', type: 'Feature', phase: 0 },
    { id: 'B', status: 'Parked', priority: 'P1', type: 'Infrastructure', phase: 1 },
    { id: 'C', status: 'Ready', priority: 'P0', type: 'Feature', phase: 1 },
  ];
  const stats = computeStats(tickets);
  assert.equal(stats.total, 3);
  assert.deepEqual(Object.keys(stats.byStatus), ['Ready', 'Done', 'Parked']); // column order, In Progress/In Review/Backlog omitted
  assert.deepEqual(stats.byStatus, { Ready: 1, Done: 1, Parked: 1 });
  assert.deepEqual(stats.byPriority, { P0: 2, P1: 1 });
  assert.deepEqual(stats.byType, { Feature: 2, Infrastructure: 1 });
  assert.deepEqual(stats.byPhase, { 0: 1, 1: 2 });
});

test('computeStats: absent optional fields do not create an undefined bucket', () => {
  const stats = computeStats([
    { id: 'A', status: 'Ready' }, // no priority/type/phase
    { id: 'B', status: 'Ready', priority: 'P0' },
  ]);
  assert.deepEqual(stats.byPriority, { P0: 1 });
  assert.deepEqual(stats.byType, {});
  assert.deepEqual(stats.byPhase, {});
  assert.ok(!('undefined' in stats.byPriority));
});

test('COLUMNS is the canonical left-to-right order with Parked last', () => {
  assert.deepEqual(COLUMNS, ['Backlog', 'Ready', 'In Progress', 'In Review', 'Done', 'Parked']);
});
