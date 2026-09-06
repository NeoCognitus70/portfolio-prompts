#!/usr/bin/env node
/**
 * generate-kanban.mjs — the shared per-project Kanban generator (T2) and its
 * per-repo drift-gate (T5).
 *
 * One generator, run inside each project repo. It builds a single self-contained
 * board from the project's backlog (via a pluggable adapter) and an optional
 * content override, deriving every ticket's status from the backlog + dependency
 * graph rather than trusting a hand-maintained column. The board is committed to
 * the repo and published to its Pages site; a CI drift-gate (`--check`) fails if a
 * commit lets the board diverge from a fresh generation — the same fourth-wall
 * guard the exemplar's `npm run verify` provides.
 *
 * USAGE
 *   node generate-kanban.mjs [options]           # write / refresh the board
 *   node generate-kanban.mjs --check [options]    # fail (exit 1) if the board is stale
 *
 * OPTIONS (all optional; sensible defaults for a standard project layout)
 *   --project <name>   project id (default: basename of --cwd)
 *   --backlog <path>   backlog file       (default: docs/backlog.md)
 *   --override <path>  content override   (default: docs/kanban-content.json)
 *   --adr <dir>        ADR directory      (default: docs/adr)
 *   --dialect <name>   backlog adapter    (default: auth-table; or risk-block)
 *   --board <path>     board file         (default: {project}_implementation-kanban_v1.html)
 *   --title <text>     board heading      (default: "{project} — Implementation Kanban v1")
 *   --cwd <dir>        base directory for all relative paths (default: process.cwd())
 *
 * A run FAILS (exit 1) in either mode on any of: an unparseable backlog (adapter
 * parsed zero tickets), an override id absent from the backlog, an override
 * carrying header fields, an unresolved ADR citation, or a non-deterministic
 * render. `--check` additionally fails on a missing or stale board.
 */
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { basename, resolve } from 'node:path';
import { parseBacklog } from './lib/adapters.mjs';
import { deriveAll, computeStats, IN_FLIGHT } from './lib/derive-status.mjs';
import { loadOverride, validateOverride, mergeContent, resolveAdrCitations } from './lib/override.mjs';
import { renderBoard, extractPayload } from './lib/render.mjs';

const FIXED = '1970-01-01 00:00:00Z'; // stand-in timestamp for the determinism self-check

export function parseArgs(argv) {
  const opts = { check: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--check') opts.check = true;
    else if (a.startsWith('--')) opts[a.slice(2)] = argv[++i];
  }
  return opts;
}

function stamp() {
  return new Date().toISOString().replace('T', ' ').replace(/\.\d+Z$/, 'Z');
}

/**
 * The board is always written with LF, but a committed board can arrive with CRLF
 * (a repo with core.autocrlf, or an editor). The drift-gate compares CONTENT, not
 * line-ending encoding, so both sides are normalised before comparison.
 */
function normalizeEol(s) {
  return s.replace(/\r\n/g, '\n');
}

/**
 * Build the derived tickets and stats from the current inputs. Returns everything
 * the caller needs to render, plus any validation problems (empty = clean).
 */
function build(paths) {
  const backlogText = readFileSync(paths.backlog, 'utf8');
  const { tickets: header, graphDerived } = parseBacklog(backlogText, paths.dialect); // throws (fail loud) on unparseable / empty

  const override = loadOverride(paths.override);
  const problems = validateOverride(override, header.map((t) => t.id));

  let derived;
  if (graphDerived) {
    // Graph-derived dialect: Ready/Backlog are recomputed. Preserve a human-set
    // In Progress / In Review sourced from the committed board.
    const prior = new Map();
    if (existsSync(paths.board)) {
      for (const t of extractPayload(readFileSync(paths.board, 'utf8'), 'payload-tickets')) {
        if (IN_FLIGHT.has(t.status)) prior.set(t.id, t.status);
      }
    }
    derived = deriveAll(header, prior);
  } else {
    // Pre-classified dialect: the adapter authored the final status; pass through.
    derived = header.map((t) => ({ ...t }));
  }
  const tickets = mergeContent(derived, override);
  const stats = computeStats(tickets);
  problems.push(...resolveAdrCitations(tickets, paths.adr));

  return { tickets, stats, problems };
}

function render(paths, tickets, stats, generatedAt) {
  return renderBoard({ project: paths.project, title: paths.title, tickets, stats, generatedAt });
}

/** Concise human diff between a committed board and a freshly derived one. */
function describeDrift(committedHtml, tickets, stats) {
  const lines = [];
  try {
    const wasTickets = extractPayload(committedHtml, 'payload-tickets');
    const wasById = new Map(wasTickets.map((t) => [t.id, t]));
    const nowIds = new Set(tickets.map((t) => t.id));
    for (const t of tickets) {
      const was = wasById.get(t.id);
      if (!was) lines.push(`[ticket] ${t.id} is new in the backlog and absent from the board`);
      else if (was.status !== t.status) lines.push(`[status] ${t.id}: ${was.status} -> ${t.status}`);
    }
    for (const t of wasTickets) if (!nowIds.has(t.id)) lines.push(`[ticket] ${t.id} is on the board but gone from the backlog`);
    const wasStats = extractPayload(committedHtml, 'payload-stats');
    if (JSON.stringify(wasStats.byStatus) !== JSON.stringify(stats.byStatus)) {
      lines.push(`[stats] byStatus ${JSON.stringify(wasStats.byStatus)} -> ${JSON.stringify(stats.byStatus)}`);
    }
  } catch {
    lines.push('[board] committed board payloads could not be read for a detailed diff');
  }
  return lines;
}

export function run(argv, env = {}) {
  const log = env.log || ((s) => console.log(s));
  const err = env.err || ((s) => console.error(s));
  const opts = parseArgs(argv);
  const cwd = resolve(opts.cwd || env.cwd || process.cwd());
  const project = opts.project || basename(cwd);
  const paths = {
    project,
    title: opts.title,
    dialect: opts.dialect || 'auth-table',
    backlog: resolve(cwd, opts.backlog || 'docs/backlog.md'),
    override: resolve(cwd, opts.override || 'docs/kanban-content.json'),
    adr: resolve(cwd, opts.adr || 'docs/adr'),
    board: resolve(cwd, opts.board || `${project}_implementation-kanban_v1.html`),
  };

  let result;
  try {
    result = build(paths);
  } catch (e) {
    err(`kanban: FAILED — ${e.message}`);
    return 1;
  }
  const { tickets, stats, problems } = result;

  // Determinism self-check: identical inputs must render byte-identical output
  // (generatedAt excluded by holding it fixed). Guards against accidental
  // nondeterministic ordering before anything is written or gated.
  if (render(paths, tickets, stats, FIXED) !== render(paths, tickets, stats, FIXED)) {
    err('kanban: FAILED — render is non-deterministic on unchanged inputs');
    return 1;
  }

  for (const p of problems) log(`  [content] ${p}`);
  if (problems.length) {
    err(`\nkanban: FAILED — ${problems.length} content problem(s); the board was not ${opts.check ? 'gated' : 'written'}.`);
    return 1;
  }

  const committed = existsSync(paths.board) ? readFileSync(paths.board, 'utf8') : null;

  if (opts.check) {
    if (committed === null) {
      err(`kanban: FAILED — no committed board at ${paths.board}; run the generator and commit it.`);
      return 1;
    }
    const committedAt = extractPayload(committed, 'payload-stats').generatedAt;
    const fresh = render(paths, tickets, stats, committedAt); // reuse timestamp -> excluded from diff
    if (normalizeEol(fresh) !== normalizeEol(committed)) {
      for (const line of describeDrift(committed, tickets, stats)) log(`  ${line}`);
      err(`\nkanban: FAILED — ${basename(paths.board)} is out of step with the backlog. Regenerate and commit.`);
      return 1;
    }
    log(`kanban: in sync — ${tickets.length} ticket(s), ${statusSummary(stats)}.`);
    return 0;
  }

  // Write mode: idempotent. If the only thing that would change is the timestamp,
  // leave the board untouched so re-running never churns the diff.
  if (committed !== null) {
    const committedAt = extractPayload(committed, 'payload-stats').generatedAt;
    if (normalizeEol(render(paths, tickets, stats, committedAt)) === normalizeEol(committed)) {
      log(`kanban: already in sync — nothing to write (${tickets.length} ticket(s)).`);
      return 0;
    }
  }
  const drift = committed ? describeDrift(committed, tickets, stats) : [];
  writeFileSync(paths.board, render(paths, tickets, stats, stamp()));
  for (const line of drift) log(`  ${line}`);
  log(`kanban: ${committed ? 'updated' : 'created'} ${basename(paths.board)} — ${tickets.length} ticket(s), ${statusSummary(stats)}.`);
  return 0;
}

function statusSummary(stats) {
  return Object.entries(stats.byStatus).map(([k, v]) => `${v} ${k}`).join(' / ');
}

// CLI entry (only when run directly, not when imported by tests).
if (import.meta.url === `file://${process.argv[1]}` || process.argv[1]?.endsWith('generate-kanban.mjs')) {
  process.exit(run(process.argv.slice(2)));
}
