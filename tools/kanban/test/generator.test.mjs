import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, cpSync, rmSync, readFileSync, writeFileSync, appendFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { run } from '../generate-kanban.mjs';
import { extractPayload } from '../lib/render.mjs';

const FIXTURES = join(import.meta.dirname, 'fixtures');

/** Copy a fixture project into a fresh temp dir and return its path + a runner. */
function stage(name) {
  const dir = mkdtempSync(join(tmpdir(), `kanban-${name}-`));
  cpSync(join(FIXTURES, name), dir, { recursive: true });
  const lines = [];
  const sink = { log: (s) => lines.push(s), err: (s) => lines.push(s) };
  return {
    dir,
    lines,
    run: (args) => run(args, { cwd: dir, ...sink }),
    board: (project) => join(dir, `${project}_implementation-kanban_v1.html`),
    cleanup: () => rmSync(dir, { recursive: true, force: true }),
  };
}

test('generate produces a single self-contained board (no framework, CDN, or vendored files)', () => {
  const s = stage('auth-table');
  try {
    assert.equal(s.run(['--project', 'demo']), 0);
    const html = readFileSync(s.board('demo'), 'utf8');
    assert.doesNotMatch(html, /<script[^>]+\bsrc=/i, 'no external script src');
    assert.doesNotMatch(html, /<link[^>]+stylesheet/i, 'no external stylesheet');
    assert.doesNotMatch(html, /https?:\/\//, 'no absolute URLs (no CDN)');
    assert.doesNotMatch(html, /vendor\//, 'no vendored files');
    assert.doesNotMatch(html, /babel|react/i, 'no React/babel');
    // Both payloads present and parseable.
    assert.equal(extractPayload(html, 'payload-tickets').length, 6);
    assert.ok(extractPayload(html, 'payload-stats').total === 6);
  } finally {
    s.cleanup();
  }
});

test('--check passes on a freshly generated board and fails when the backlog drifts', () => {
  const s = stage('auth-table');
  try {
    assert.equal(s.run(['--project', 'demo']), 0);
    assert.equal(s.run(['--check', '--project', 'demo']), 0);

    // Add a ticket to the backlog: the committed board is now stale.
    appendFileSync(
      join(s.dir, 'docs', 'backlog.md'),
      '\n| `DEMO-007` | Late addition | Feature | P0 | HIGH | — | Backlog |\n',
    );
    assert.equal(s.run(['--check', '--project', 'demo']), 1);
    assert.ok(s.lines.some((l) => /out of step/.test(l)));
  } finally {
    s.cleanup();
  }
});

test('--check fails when no board has been committed', () => {
  const s = stage('auth-table');
  try {
    rmSync(s.board('demo'), { force: true }); // ensure no committed board
    assert.equal(s.run(['--check', '--project', 'demo']), 1);
    assert.ok(s.lines.some((l) => /no committed board/.test(l)));
  } finally {
    s.cleanup();
  }
});

test('generation is deterministic and idempotent (re-running writes nothing)', () => {
  const s = stage('auth-table');
  try {
    assert.equal(s.run(['--project', 'demo']), 0);
    const first = readFileSync(s.board('demo'), 'utf8');
    assert.equal(s.run(['--project', 'demo']), 0);
    const second = readFileSync(s.board('demo'), 'utf8');
    assert.equal(first, second, 'byte-identical board on unchanged inputs (generatedAt included, since nothing was rewritten)');
    assert.ok(s.lines.some((l) => /already in sync/.test(l)));
  } finally {
    s.cleanup();
  }
});

test('a status change regenerates the board and --check then agrees', () => {
  const s = stage('auth-table');
  try {
    assert.equal(s.run(['--project', 'demo']), 0);
    // Close DEMO-003 in the backlog.
    const bl = join(s.dir, 'docs', 'backlog.md');
    writeFileSync(bl, readFileSync(bl, 'utf8').replace(
      '| `DEMO-003` | Build on the thing | Feature | P0 | HIGH | `DEMO-001` | Backlog |',
      '| `DEMO-003` | Build on the thing | Feature | P0 | HIGH | `DEMO-001` | ✅ **Done** 2026-09-07 |',
    ));
    assert.equal(s.run(['--check', '--project', 'demo']), 1); // stale
    assert.equal(s.run(['--project', 'demo']), 0); // regenerate
    const html = readFileSync(s.board('demo'), 'utf8');
    const byId = Object.fromEntries(extractPayload(html, 'payload-tickets').map((t) => [t.id, t.status]));
    assert.equal(byId['DEMO-003'], 'Done');
    assert.equal(byId['DEMO-004'], 'Ready'); // its only blocker is now Done
    assert.equal(s.run(['--check', '--project', 'demo']), 0);
  } finally {
    s.cleanup();
  }
});

test('--check is EOL-tolerant: a CRLF committed board is still in sync (no false drift)', () => {
  const s = stage('auth-table');
  try {
    assert.equal(s.run(['--project', 'demo']), 0);
    const board = s.board('demo');
    writeFileSync(board, readFileSync(board, 'utf8').replace(/\n/g, '\r\n')); // simulate autocrlf checkout
    assert.equal(s.run(['--check', '--project', 'demo']), 0);
  } finally {
    s.cleanup();
  }
});

test('an override naming an unknown id fails the run (exit 1, nothing written)', () => {
  const s = stage('auth-table');
  try {
    const ovr = join(s.dir, 'docs', 'kanban-content.json');
    const j = JSON.parse(readFileSync(ovr, 'utf8'));
    j['GHOST-1'] = { description: 'orphan' };
    writeFileSync(ovr, JSON.stringify(j));
    assert.equal(s.run(['--project', 'demo']), 1);
    assert.ok(s.lines.some((l) => /GHOST-1, which is not a ticket/.test(l)));
  } finally {
    s.cleanup();
  }
});

test('risk-block scaffold: pre-classified statuses pass through and round-trip through --check', () => {
  const s = stage('risk-block');
  try {
    assert.equal(s.run(['--project', 'riskdemo', '--dialect', 'risk-block']), 0);
    const html = readFileSync(s.board('riskdemo'), 'utf8');
    const byId = Object.fromEntries(extractPayload(html, 'payload-tickets').map((t) => [t.id, t.status]));
    assert.deepEqual(byId, { 'RISK-1': 'Done', 'RISK-2': 'In Progress', 'RISK-3': 'Ready', 'RISK-4': 'Backlog' });
    assert.equal(s.run(['--check', '--project', 'riskdemo', '--dialect', 'risk-block']), 0);
  } finally {
    s.cleanup();
  }
});

test('board layout stays viewport-bounded so every column is reachable (PP-37)', () => {
  const s = stage('auth-table');
  try {
    assert.equal(s.run(['--project', 'demo']), 0);
    const html = readFileSync(s.board('demo'), 'utf8');

    // The page is a full-height app shell: the board occupies the space the chrome leaves
    // rather than growing to its tallest column. Without this, the board's own overflow-x
    // scrollbar renders at its bottom edge, thousands of pixels below the fold.
    const body = html.match(/\bbody\s*\{([^}]*)\}/);
    assert.ok(body, 'body rule present');
    assert.match(body[1], /height:100vh/, 'body is viewport-height');
    assert.match(body[1], /flex-direction:column/, 'body is a column flex shell');

    const board = html.match(/\.board\s*\{([^}]*)\}/);
    assert.ok(board, '.board rule present');
    assert.match(board[1], /overflow-x:auto/, 'board scrolls horizontally');
    assert.match(board[1], /flex:1/, 'board fills the remaining height');
    assert.match(board[1], /min-height:0/, 'board may shrink below its content height');
    assert.doesNotMatch(
      board[1],
      /min-height:calc\(100vh/,
      'board must not be forced taller than the viewport (PP-37 regression)',
    );

    // A height-capped column is what lets its body scroll vertically instead of stretching
    // the column - and with it the board - to fit every card.
    const colBody = html.match(/\.column-body\s*\{([^}]*)\}/);
    assert.ok(colBody, '.column-body rule present');
    assert.match(colBody[1], /overflow-y:auto/, 'column body scrolls vertically');
    assert.match(colBody[1], /min-height:0/, 'column body may shrink below its content height');
  } finally {
    s.cleanup();
  }
});
