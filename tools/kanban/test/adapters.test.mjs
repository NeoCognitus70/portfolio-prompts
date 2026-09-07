import { test } from 'node:test';
import assert from 'node:assert/strict';
import { authTable, riskBlock, parseBacklog } from '../lib/adapters.mjs';

const AUTH_TABLE = `
## Ignore me

| Priority | Count | Done |
|---|---|---|
| P0 | 3 | 1 |

| ID | Ticket | Type | Priority | Tier | Blocked by | Status |
|---|---|---|---|---|---|---|
| \`A-001\` | First | Foundation | P0 | HIGH | — | ✅ **Done** 2026-09-01 |
| \`A-002\` | Second | Infrastructure | P0 | HIGH | \`A-001\` | Parked — out of scope under \`ADR-0005\` |
| \`A-003\` | Third | Feature | P1 | MEDIUM | \`A-001\`, \`A-002\` | Ready to start |
| \`A-004\` | Fourth | Test | P2 | LOW | \`A-003\` | Backlog |

| \`A-001\` | closure record has three cells | 2026-09-01 |
`;

test('authTable: reads only backticked-id, exactly-7-cell rows', () => {
  const t = authTable(AUTH_TABLE);
  assert.deepEqual(t.map((x) => x.id), ['A-001', 'A-002', 'A-003', 'A-004']);
});

test('authTable: status keyword classification, Parked tested before Done', () => {
  const t = Object.fromEntries(authTable(AUTH_TABLE).map((x) => [x.id, x.backlogStatus]));
  assert.equal(t['A-001'], 'Done');
  assert.equal(t['A-002'], 'Parked'); // "Parked ... ADR-0005" must not be misread
  assert.equal(t['A-003'], 'Ready');
  assert.equal(t['A-004'], 'Backlog');
});

test('authTable: Parked wins even if the cell also contains the word Done', () => {
  const rows = `| ID | Ticket | Type | Priority | Tier | Blocked by | Status |
|---|---|---|---|---|---|---|
| \`X-1\` | mixed | Feature | P0 | HIGH | — | Parked (was Done, now out of scope) |`;
  assert.equal(authTable(rows)[0].backlogStatus, 'Parked');
});

test('authTable: blockedBy is read from the Blocked-by cell (cell 6), multiple ids parsed in order', () => {
  const t = Object.fromEntries(authTable(AUTH_TABLE).map((x) => [x.id, x.blockedBy]));
  assert.deepEqual(t['A-001'], []); // em dash -> no blockers
  assert.deepEqual(t['A-003'], ['A-001', 'A-002']);
});

test('authTable: maps title/type/priority; omits empty type/priority', () => {
  const rows = `| ID | Ticket | Type | Priority | Tier | Blocked by | Status |
|---|---|---|---|---|---|---|
| \`X-1\` | Bare | — | — | — | — | Backlog |`;
  const [t] = authTable(rows);
  assert.equal(t.title, 'Bare');
  assert.ok(!('type' in t));
  assert.ok(!('priority' in t));
});

test('riskBlock: authored status maps straight to a final column (pre-classified)', () => {
  const text = `
#### Risk #1: Creds in plaintext — Score: 27
**Status:** COMPLETE

#### Risk #2: No rate limit — Score: 21
**Status:** IN PROGRESS

#### Risk #3: No restore drill — Score: 12
**Status:** READY START

#### Risk #4: Audit overdue — Score: 8
**Status:** BLOCKED
`;
  const t = Object.fromEntries(riskBlock(text).map((x) => [x.id, x.status]));
  assert.deepEqual(t, { 'RISK-1': 'Done', 'RISK-2': 'In Progress', 'RISK-3': 'Ready', 'RISK-4': 'Backlog' });
  assert.equal(riskBlock(text)[0].score, 27);
});

test('parseBacklog: reports graphDerived per dialect', () => {
  assert.equal(parseBacklog(AUTH_TABLE, 'auth-table').graphDerived, true);
  assert.equal(parseBacklog('#### Risk #1: x — Score: 1\n**Status:** BLOCKED', 'risk-block').graphDerived, false);
});

test('parseBacklog: fails loudly on an unknown dialect', () => {
  assert.throws(() => parseBacklog(AUTH_TABLE, 'nope'), /unknown backlog dialect/);
});

test('parseBacklog: fails loudly when the adapter parses zero tickets', () => {
  assert.throws(() => parseBacklog('# nothing here\n', 'auth-table'), /parsed zero tickets/);
});
