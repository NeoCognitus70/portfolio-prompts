import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, mkdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { validateOverride, mergeContent, resolveAdrCitations, loadOverride } from '../lib/override.mjs';

const BACKLOG_IDS = ['A-001', 'A-002', 'A-003'];

test('validateOverride: an override id absent from the backlog is a hard error', () => {
  const p = validateOverride({ 'GHOST-9': { description: 'x' } }, BACKLOG_IDS);
  assert.equal(p.length, 1);
  assert.match(p[0], /GHOST-9, which is not a ticket/);
});

test('validateOverride: a backlog id with no override entry is allowed (header-only card)', () => {
  assert.deepEqual(validateOverride({ 'A-001': { description: 'x' } }, BACKLOG_IDS), []);
});

test('validateOverride: header fields in the override are rejected', () => {
  for (const bad of ['status', 'backlogStatus', 'blockedBy', 'title', 'type', 'priority', 'score']) {
    const p = validateOverride({ 'A-001': { [bad]: 'v' } }, BACKLOG_IDS);
    assert.equal(p.length, 1, `${bad} should be rejected`);
    assert.match(p[0], /non-body field/);
  }
});

test('validateOverride: acceptance must be an array of strings', () => {
  assert.match(validateOverride({ 'A-001': { acceptance: 'nope' } }, BACKLOG_IDS)[0], /acceptance must be an array/);
  assert.deepEqual(validateOverride({ 'A-001': { acceptance: ['ok'] } }, BACKLOG_IDS), []);
});

test('validateOverride: adr entries must match ADR-nnnn', () => {
  assert.match(validateOverride({ 'A-001': { adr: ['ADR-1'] } }, BACKLOG_IDS)[0], /must match ADR-nnnn/);
  assert.match(validateOverride({ 'A-001': { adr: 'ADR-0001' } }, BACKLOG_IDS)[0], /adr must be an array/);
  assert.deepEqual(validateOverride({ 'A-001': { adr: ['ADR-0001'] } }, BACKLOG_IDS), []);
});

test('mergeContent: blocks is computed as the reverse of blockedBy (display-only)', () => {
  const header = [
    { id: 'A', title: 'a', blockedBy: [], backlogStatus: 'Done', status: 'Done' },
    { id: 'B', title: 'b', blockedBy: ['A'], backlogStatus: 'Ready', status: 'Ready' },
    { id: 'C', title: 'c', blockedBy: ['A'], backlogStatus: 'Ready', status: 'Ready' },
  ];
  const out = Object.fromEntries(mergeContent(header, {}).map((t) => [t.id, t.blocks]));
  assert.deepEqual(out.A, ['B', 'C']);
  assert.deepEqual(out.B, []);
});

test('mergeContent: body fields are merged from the override; missing ones are simply absent', () => {
  const header = [{ id: 'A', title: 'a', blockedBy: [], backlogStatus: 'Done', status: 'Done' }];
  const [t] = mergeContent(header, { A: { description: 'desc', acceptance: ['x'] } });
  assert.equal(t.description, 'desc');
  assert.deepEqual(t.acceptance, ['x']);
  assert.ok(!('spec' in t));
  assert.ok(!('assignee' in t));
});

test('resolveAdrCitations: unresolved citation is a problem; resolved ones are clean', () => {
  const dir = mkdtempSync(join(tmpdir(), 'kanban-adr-'));
  try {
    mkdirSync(join(dir, 'adr'), { recursive: true });
    writeFileSync(join(dir, 'adr', '0001-x.md'), '# ADR-0001');
    const tickets = [{ id: 'A', spec: 'see ADR-0001', adr: ['ADR-0001'] }];
    assert.deepEqual(resolveAdrCitations(tickets, join(dir, 'adr')), []);

    const missing = [{ id: 'B', adr: ['ADR-0002'] }];
    assert.match(resolveAdrCitations(missing, join(dir, 'adr'))[0], /ADR-0002, which has no file/);

    // No ADR directory at all, but a citation exists -> problem.
    assert.match(resolveAdrCitations(missing, join(dir, 'nope'))[0], /no ADR directory exists/);
    // No citations anywhere -> clean, even without a directory.
    assert.deepEqual(resolveAdrCitations([{ id: 'C' }], join(dir, 'nope')), []);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('loadOverride: absent file yields {}; malformed JSON fails loudly', () => {
  const dir = mkdtempSync(join(tmpdir(), 'kanban-ovr-'));
  try {
    assert.deepEqual(loadOverride(join(dir, 'nope.json')), {});
    writeFileSync(join(dir, 'bad.json'), '{ not json');
    assert.throws(() => loadOverride(join(dir, 'bad.json')), /not valid JSON/);
    writeFileSync(join(dir, 'arr.json'), '[]');
    assert.throws(() => loadOverride(join(dir, 'arr.json')), /must be a JSON object/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('mergeContent: an override wins over adapter-supplied body, which wins over nothing (PP-38)', () => {
  const header = [
    // risk-block reads body straight out of the backlog; auth-table supplies none.
    { id: 'R-1', title: 'from backlog', blockedBy: [], backlogStatus: 'Ready', status: 'Ready',
      description: 'backlog text', acceptance: ['backlog criterion'] },
    { id: 'R-2', title: 'no body anywhere', blockedBy: [], backlogStatus: 'Ready', status: 'Ready' },
  ];
  const merged = mergeContent(header, { 'R-1': { description: 'override text' } });
  const byId = Object.fromEntries(merged.map((t) => [t.id, t]));
  assert.equal(byId['R-1'].description, 'override text', 'override wins');
  assert.deepEqual(byId['R-1'].acceptance, ['backlog criterion'], 'un-overridden backlog body survives');
  assert.equal('description' in byId['R-2'], false, 'absent everywhere stays absent');
});
