import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { authTable, riskBlock, parseBacklog } from '../lib/adapters.mjs';

const FIXTURES = join(import.meta.dirname, 'fixtures');

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

test('authTable (D7): phase is derived from the most recent "Phase N" heading', () => {
  const text = readFileSync(join(FIXTURES, 'phases', 'docs', 'backlog.md'), 'utf8');
  const phaseById = Object.fromEntries(authTable(text).map((t) => [t.id, t.phase]));
  // A row before any Phase heading gets no phase.
  assert.equal(phaseById['PRE-001'], undefined);
  assert.ok(!('phase' in authTable(text).find((t) => t.id === 'PRE-001')));
  // Rows inherit the number of the heading above them (non-contiguous, mixed depth).
  assert.equal(phaseById['P0-001'], 0);
  assert.equal(phaseById['P0-002'], 0);
  assert.equal(phaseById['P3-001'], 3);
  assert.equal(phaseById['P3-003'], 3);
  assert.equal(phaseById['P7-001'], 7);
});

test('authTable (D7): a "Phase 0" heading yields integer 0, not a falsy drop', () => {
  const [t] = authTable('### Phase 0 — Foundations\n\n' +
    '| ID | Ticket | Type | Priority | Tier | Blocked by | Status |\n' +
    '|---|---|---|---|---|---|---|\n' +
    '| `X-1` | zeroth | Feature | P0 | HIGH | — | Backlog |');
  assert.strictEqual(t.phase, 0);
});

test('authTable (D7): phase distribution matches the auth-separation anchor {0:6,1:7,2:4,3:15,4:4,5:4,6:6,7:5}', () => {
  // Auth-shaped backlog reproduced with the real heading format and the exact
  // per-phase ticket counts from auth-separation/docs/backlog.md (the source of the
  // original hand-authored board's payload). The generator run against the live file
  // yields this same distribution.
  const counts = { 0: 6, 1: 7, 2: 4, 3: 15, 4: 4, 5: 4, 6: 6, 7: 5 };
  const rowHeader = '| ID | Ticket | Type | Priority | Tier | Blocked by | Status |\n|---|---|---|---|---|---|---|\n';
  let md = '# Implementation backlog\n\n';
  let n = 0;
  for (const [phase, count] of Object.entries(counts)) {
    md += `### Phase ${phase} — Section ${phase} (${count} tickets)\n\n${rowHeader}`;
    for (let i = 0; i < count; i++) {
      md += `| \`AUTH-${String(++n).padStart(3, '0')}\` | Ticket ${n} | Feature | P0 | HIGH | — | Backlog |\n`;
    }
    md += '\n';
  }
  const dist = {};
  for (const t of authTable(md)) dist[t.phase] = (dist[t.phase] ?? 0) + 1;
  assert.deepEqual(dist, counts);
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

#### Risk #5: Spec mis-declares a field type — Score: 5
**Status:** RECORDED — asserted, not accommodated
`;
  const t = Object.fromEntries(riskBlock(text).map((x) => [x.id, x.status]));
  assert.deepEqual(t, {
    'RISK-1': 'Done',
    'RISK-2': 'In Progress',
    'RISK-3': 'Ready',
    'RISK-4': 'Backlog',
    'RISK-5': 'Parked',
  });
  assert.equal(riskBlock(text)[0].score, 27);
});

test('riskBlock: RECORDED is the accepted-risk terminal state, not open work', () => {
  // Regression for the real gap: parabank-bank-automation authors RECORDED for a
  // risk it asserted and consciously did not accommodate. Before 1.2.0 that fell
  // through to the Backlog default, so a closed-out project advertised open cards.
  const [t] = riskBlock(`#### Risk PBR-01: Spec mis-declares a field — Score: 5
**Status:** RECORDED — asserted, not accommodated`);
  assert.equal(t.status, 'Parked');
  assert.equal(t.backlogStatus, 'Parked');

  // Parked is outside the Backlog -> Done flow, so it must never be revived as Ready.
  assert.notEqual(t.status, 'Ready');
  assert.notEqual(t.status, 'Backlog');
});

test('riskBlock: RESOLVED does not collide with RECORDED', () => {
  // "RESOLVED" shares no word boundary with "RECORDED"; an outstanding-section item
  // marked RESOLVED is a bookkeeping error in that backlog (it belongs under
  // Resolved Risks) and must NOT be silently reclassified as Parked here.
  const [t] = riskBlock(`#### Risk PBR-07: Assertion raced the fetch — Score: 10
**Status:** RESOLVED 2026-09-01 — the step now waits`);
  assert.equal(t.status, 'Backlog');
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

// --- risk-block, shipping template dialect (PP-38) ---------------------------
// One sample carrying everything the real portfolio backlogs throw at it: the
// canonical heading, a review-qualified number, an explicit id, prose headings
// that must never become cards, and a resolved section.
const RISK_TEMPLATE = `
### HIGH Priority (Score: 20-30)

#### Risk #1: Creds in log — Score: 24
**Status:** IN PROGRESS

**Problem:**
Passwords are serialised into the log sink.

**Impact Analysis:**
- **Security (10/10):** readable by anyone with log access.

**Success Criteria:**
- [ ] Fields are redacted.
- [x] Regression test added.

#### Risk #2 (review #1): No rate limit — Score: 21
**Status:** READY TO START

### MEDIUM Priority (Score: 10-19)

#### Risk PBR-07: No restore drill — Score: 12
**Status:** BLOCKED

## Delivery notes

#### Out of scope

#### Implementation acceptance criteria

#### Validation and closure criteria

### Resolved Risks

#### Secure cookie attribute ✅ Resolved 2026-08-07
**Resolution:** done.
`;

test('riskBlock: parses the canonical heading and both real-world variants', () => {
  assert.deepEqual(
    riskBlock(RISK_TEMPLATE).map((x) => x.id),
    ['RISK-1', 'RISK-2', 'PBR-07', 'RES-SECURE-COOKIE-ATTRIBUTE'],
  );
});

test('riskBlock: prose #### headings never become cards (zero false positives)', () => {
  const ids = riskBlock(RISK_TEMPLATE).map((x) => x.id).join(' ');
  for (const phantom of ['OUT-OF-SCOPE', 'IMPLEMENTATION', 'VALIDATION']) {
    assert.doesNotMatch(ids, new RegExp(phantom), `${phantom} must not become a ticket`);
  }
});

test('riskBlock: template status vocabulary maps to columns; resolved section is Done', () => {
  assert.deepEqual(
    Object.fromEntries(riskBlock(RISK_TEMPLATE).map((x) => [x.id, x.status])),
    {
      'RISK-1': 'In Progress',
      'RISK-2': 'Ready',
      'PBR-07': 'Backlog',
      'RES-SECURE-COOKIE-ATTRIBUTE': 'Done',
    },
  );
});

test('riskBlock: band comes from the enclosing heading, else from the score', () => {
  const p = Object.fromEntries(riskBlock(RISK_TEMPLATE).map((x) => [x.id, x.priority]));
  assert.equal(p['RISK-1'], 'HIGH');
  assert.equal(p['RISK-2'], 'HIGH');
  assert.equal(p['PBR-07'], 'MEDIUM');
  // No enclosing band heading: the band is derived from the score instead.
  assert.equal(riskBlock('#### Risk #9: x — Score: 4\n**Status:** BLOCKED')[0].priority, 'LOW');
  assert.equal(riskBlock('#### Risk #9: x — Score: 25\n**Status:** BLOCKED')[0].priority, 'HIGH');
});

test('riskBlock: card body is read from the backlog, so no override is needed', () => {
  const t = riskBlock(RISK_TEMPLATE)[0];
  assert.match(t.description, /Passwords are serialised/, 'Problem becomes the description');
  assert.match(t.description, /Impact analysis:/, 'Impact Analysis is carried too');
  assert.deepEqual(t.acceptance, ['Fields are redacted.', 'Regression test added.']);
});

test('riskBlock: duplicate ids fail loudly rather than producing two cards', () => {
  assert.throws(
    () => riskBlock('#### Risk #1: a — Score: 5\n#### Risk #1: b — Score: 6'),
    /duplicate ticket id/,
  );
});
