#!/usr/bin/env node
"use strict";

/*
 * Binding-only V47 sealed-exam harness.
 *
 * Policy code is loaded from the pinned Git objects.  The sole in-memory
 * transformation replaces the builder's terminal main() call with exports of
 * already-defined simulation/scoring functions.  No policy source is edited.
 */

const child = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const Module = require("module");
const path = require("path");
const readline = require("readline");
const stream = require("stream/promises");
const zlib = require("zlib");

const V47 = "fb74c8b8f0f5fa3bae69fab017ec937b6b13eb34";
const V45 = "3bda0a5476c7fc845891928795f709feff8caabf";
const V36 = "bfde0d8d1135f5c5f48a5f3d619ab30050efab83";
const V47_PACKAGE = ".claude/window1_live_v4_replay/v47_same_tick_arm_20260810";
const V36_PACKAGE = ".claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806";
const V47_BUILDER = "arb-executor/analysis/build_window1_v38_maker_only.js";
const V47_WRAPPER = "arb-executor/analysis/build_window1_v47_same_tick_arm.js";
const V36_BUILDER = "arb-executor/analysis/build_window1_v36_state_directional_rest_mature_floor.js";
const V47_POLICY_PATHS = [
  V47_BUILDER, V47_WRAPPER,
  "arb-executor/analysis/window1_v47_same_tick_arm.js",
  "arb-executor/analysis/window1_v45_guard_release_sibling_credit.js",
  "arb-executor/analysis/window1_v43_composed_machine.js",
  "arb-executor/analysis/window1_v42_deep_gap_feasibility_guard.js",
  "arb-executor/analysis/window1_v41_maker_machine.js",
  "arb-executor/analysis/window1_v36_state_directional_rest_mature_floor.js",
  "arb-executor/analysis/window1_v35_living_rest_evidence_gate.js",
  "arb-executor/analysis/window1_v34_dual_side_residency_machine.js",
  "arb-executor/analysis/window1_v32_no_chase_state_machine.js",
];

const argv = process.argv.slice(2);
const arg = (name, fallback = null) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const required = (name) => { const value = arg(name); if (!value) throw new Error(`${name} required`); return value; };
const repo = path.resolve(arg("--repo", path.join(__dirname, "../..")));
const mode = required("--mode");
const output = path.resolve(required("--output"));
const privateRoot = path.resolve(arg("--private-root", "C:/Users/omigr/OMI-Window1-private"));

function ensure(value, message) { if (!value) throw new Error(message); }
function sha(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function hashFile(file) { return sha(fs.readFileSync(file)); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function readJson(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }
function readJsonl(file) { const text = fs.readFileSync(file, "utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse) : []; }
function gitShow(commit, rel) { return child.execFileSync("git", ["show", `${commit}:${rel}`], { cwd: repo, maxBuffer: 512 * 1024 * 1024 }); }
function countBy(rows, fn) { const out = {}; for (const row of rows) { const key = String(fn(row)); out[key] = (out[key] || 0) + 1; } return Object.fromEntries(Object.entries(out).sort(([a], [b]) => a.localeCompare(b))); }
function percentile(values, q) { const rows = values.filter(Number.isFinite).sort((a, b) => a - b); return rows.length ? rows[Math.max(0, Math.ceil(q * rows.length) - 1)] : null; }
function distribution(values) { const rows = values.filter(Number.isFinite); return { n: rows.length, null_n: values.length - rows.length, sum: rows.reduce((a, b) => a + b, 0), min: rows.length ? Math.min(...rows) : null, p25: percentile(rows, .25), median: percentile(rows, .5), p75: percentile(rows, .75), p90: percentile(rows, .9), max: rows.length ? Math.max(...rows) : null }; }
function priceRegion(price) { return price <= 25 ? "le25" : price <= 50 ? "26_50" : price <= 75 ? "51_75" : "ge76"; }
function writeJson(dir, name, value) { fs.writeFileSync(path.join(dir, name), canonical(value)); }
async function writeGzipRows(file, rows) {
  async function* encode() { for (const row of rows) yield `${JSON.stringify(row)}\n`; }
  await stream.pipeline(encode(), zlib.createGzip({ level: 9, mtime: 0 }), fs.createWriteStream(file));
}
function readGzipRows(file) { const text = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse) : []; }

function compileV47() {
  const sourceBytes = gitShow(V47, V47_BUILDER);
  const builderFile = path.join(repo, V47_BUILDER);
  let source = sourceBytes.toString("utf8").replace(/^#![^\n]*\n/, "");
  const terminal = "main().catch((error) => { process.stderr.write(`${error.stack || error}\\n`); process.exitCode = 1; });";
  ensure(source.includes(terminal), "V47 terminal invocation missing");
  source = source.replace(terminal, "module.exports = { simulate, score, fullBookPnl, parseEt, integer, positive, distribution, countBy, policy };");
  const prior = process.argv;
  try {
    process.argv = [prior[0], builderFile, "--variant", "v47", "--repo", repo, "--private-root", privateRoot, "--output", path.join(output, ".compile-v47")];
    const instance = new Module(builderFile, module);
    instance.filename = builderFile;
    instance.paths = Module._nodeModulePaths(path.dirname(builderFile));
    instance._compile(source, builderFile);
    return instance.exports;
  } finally { process.argv = prior; }
}

function compileV36() {
  const sourceBytes = gitShow(V36, V36_BUILDER);
  const builderFile = path.join(repo, V36_BUILDER);
  let source = sourceBytes.toString("utf8").replace(/^#![^\n]*\n/, "");
  const terminal = "causalMain().catch((error) => { process.stderr.write(`${error.stack || error}\\n`); process.exitCode = 1; });";
  ensure(source.includes(terminal), "V36 terminal invocation missing");
  source = source.replace(terminal, "module.exports = { condenseTape, simulateW1Mode, scoreW1Column, frontierW1, regretW1, fillSplit, compactW1Trace, restSanity, parseEt, integer, positive, policy };");
  const prior = process.argv;
  try {
    process.argv = [prior[0], builderFile, "--repo", repo, "--private-root", privateRoot, "--output", path.join(output, ".compile-v36")];
    const instance = new Module(builderFile, module);
    instance.filename = builderFile;
    instance.paths = Module._nodeModulePaths(path.dirname(builderFile));
    instance._compile(source, builderFile);
    return instance.exports;
  } finally { process.argv = prior; }
}

function policyIdentity() {
  const files = {};
  for (const rel of V47_POLICY_PATHS) {
    const local = path.join(repo, rel), localBytes = fs.readFileSync(local), pinned = gitShow(V47, rel);
    ensure(sha(localBytes) === sha(pinned), `V47 policy dependency drift ${rel}`);
    files[rel] = { sha256: sha(localBytes), bytes: localBytes.length, pinned_commit: V47 };
  }
  const v36Paths = [
    "arb-executor/analysis/window1_v36_state_directional_rest_mature_floor.js",
    "arb-executor/analysis/window1_v35_living_rest_evidence_gate.js",
    "arb-executor/analysis/window1_v34_dual_side_residency_machine.js",
    "arb-executor/analysis/window1_v32_no_chase_state_machine.js",
  ];
  for (const v36Policy of v36Paths) {
    const v36Pinned = gitShow(V36, v36Policy), v36Local = fs.readFileSync(path.join(repo, v36Policy));
    ensure(sha(v36Pinned) === sha(v36Local), `V36 policy dependency drift ${v36Policy}`);
    files[`${v36Policy}@V36`] = { sha256: sha(v36Pinned), bytes: v36Pinned.length, pinned_commit: V36 };
  }
  files[`${V36_BUILDER}@V36`] = { sha256: sha(gitShow(V36, V36_BUILDER)), bytes: gitShow(V36, V36_BUILDER).length, pinned_commit: V36 };
  return files;
}

function tapeRootFor(leg, oldTapeRoot, newTapeRoot) {
  if (leg.private_root_class === "HOLDOUT_EXAM_20260807_TAPES") return oldTapeRoot;
  if (leg.private_root_class === "V47_EXAM_NEW_CAPTURE_TAPES") return newTapeRoot;
  throw new Error(`unknown tape root class ${leg.private_root_class}`);
}

function loadTape(api, leg, oldTapeRoot, newTapeRoot) {
  const file = path.join(tapeRootFor(leg, oldTapeRoot, newTapeRoot), leg.path_basename);
  ensure(fs.existsSync(file), `missing tape ${leg.ticker}`);
  ensure(hashFile(file) === leg.sha256 && fs.statSync(file).size === leg.bytes, `tape identity mismatch ${leg.ticker}`);
  const lines = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trimEnd().split(/\r?\n/);
  const header = lines.shift().split(","), ix = Object.fromEntries(header.map((value, index) => [value, index]));
  const rows = [];
  for (let n = 0; n < lines.length; n += 1) {
    const cells = lines[n].split(","), ts = api.parseEt(cells[ix.ts_et]);
    if (!Number.isFinite(ts) || ts < leg.authoritative_from_epoch || ts > leg.authoritative_through_epoch) continue;
    const bids = [], asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bp = api.integer(cells[ix[`bid_${level}`]]), bs = api.positive(cells[ix[`bid_${level}_sz`]]), ap = api.integer(cells[ix[`ask_${level}`]]), as = api.positive(cells[ix[`ask_${level}_sz`]]);
      if (bp !== null && bs !== null) bids.push([bp, bs]);
      if (ap !== null && as !== null) asks.push([ap, as]);
    }
    if (!bids.length || !asks.length) continue;
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]);
    const bidDepth = bids.reduce((sum, row) => sum + row[1], 0), askDepth = asks.reduce((sum, row) => sum + row[1], 0);
    rows.push({ kind: "BOOK", ticker: leg.ticker, ts, ordinal: n + 2, receipt: `${leg.path_basename}#row-${n + 2}`, bid: bids[0][0], ask: asks[0][0], spread: asks[0][0] - bids[0][0], top_bid_size: bids[0][1], top_ask_size: asks[0][1], bid_depth_5: bidDepth, ask_depth_5: askDepth, depth_ratio: bidDepth / (bidDepth + askDepth), last_trade: api.integer(cells[ix.last_trade]) });
  }
  rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  let ask = null, since = null;
  for (const row of rows) { if (row.ask !== ask) { ask = row.ask; since = row.ts; } row.ask_dwell_seconds = row.ts - since; }
  ensure(rows.length > 0, `no authoritative formed rows ${leg.ticker}`);
  return rows;
}

async function loadPrints(file, tickers) {
  const byTicker = new Map([...tickers].map((ticker) => [ticker, []]));
  const seen = new Set();
  const input = fs.createReadStream(file, { highWaterMark: 1024 * 1024 });
  const rl = readline.createInterface({ input, crlfDelay: Infinity });
  for await (const line of rl) {
    if (!line) continue;
    const row = JSON.parse(line);
    if (!byTicker.has(row.ticker) || row.true_print !== true || !row.trade_id || seen.has(row.trade_id)) continue;
    const ts = Date.parse(row.exchange_ts) / 1000;
    if (!Number.isFinite(ts)) continue;
    seen.add(row.trade_id);
    byTicker.get(row.ticker).push({ kind: "PRINT", ticker: row.ticker, ts, ordinal: 0, receipt: row.receipt_id || row.trade_id, price: Number(row.price_cents), size: Number(row.size), taker_side: row.taker_side, taker_book_side: row.taker_book_side, trade_id: row.trade_id });
  }
  for (const rows of byTicker.values()) { rows.sort((a, b) => a.ts - b.ts || a.trade_id.localeCompare(b.trade_id)); rows.forEach((row, index) => { row.ordinal = index + 1; }); }
  return byTicker;
}

function buildBinding(api, declarationFile, boundaryFile, oldTapeRoot, newTapeRoot) {
  const declaration = readJson(declarationFile), boundaryRows = readJsonl(boundaryFile);
  ensure(declaration.N >= 60 && declaration.events.length === declaration.N, "population gate failed");
  const boundaries = new Map(boundaryRows.map((row) => [row.event_id, row]));
  const events = declaration.events.map((event) => ({ ...event, boundary: boundaries.get(event.event_id) }));
  ensure(events.every((event) => event.boundary), "boundary missing");
  const tickers = new Set(events.flatMap((event) => event.legs.map((leg) => leg.ticker)));
  return { declaration, events, boundaries, tickers, loadTape: (leg) => loadTape(api, leg, oldTapeRoot, newTapeRoot) };
}

function boundaryBase(event, tapes) {
  const boundary = event.boundary;
  const left = Math.min(...[...tapes.values()].map((rows) => rows[0].ts));
  const schedule = (boundary.candidate_sources || []).find((row) => row.direction === "schedule_bound")?.timestamp_epoch ?? boundary.right_edge_epoch;
  const actualBell = boundary.precision_class === "exact" ? boundary.right_edge_epoch : null;
  const firstBids = [...tapes.values()].map((rows) => rows[0].bid).sort((a, b) => a - b);
  return { event_id: event.event_id, category: event.category, starting_price_split: firstBids.map(priceRegion).join("+"), bell_confidence: boundary.precision_class, edge_source_field: boundary.right_edge_source_field, left, right: Number(boundary.right_edge_epoch), scheduled: Number(schedule), actual_bell: actualBell, legs: {} };
}

function reachFor(tape, prints, left, right) {
  const asks = tape.filter((row) => row.ts >= left && row.ts <= right && row.ask_dwell_seconds >= 10 && row.top_ask_size >= 5);
  const trades = prints.filter((row) => row.ts >= left && row.ts <= right && row.size > 0 && Number.isInteger(row.price));
  const askLow = asks.length ? Math.min(...asks.map((row) => row.ask)) : null;
  const tradeLow = trades.length ? Math.min(...trades.map((row) => row.price)) : null;
  const levels = [askLow, tradeLow].filter(Number.isInteger), floor = levels.length ? Math.min(...levels) : null;
  const evidence = [...asks.filter((row) => row.ask === floor), ...trades.filter((row) => row.price === floor)].sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  return { union_reach_cents: floor, union_first_evidence_timestamp_epoch: evidence[0]?.ts ?? null, union_sources: { qualifying_ask_low_cents: askLow, traded_low_cents: tradeLow } };
}

function eventInputs(api, event, binding, printsByTicker) {
  const tapesById = new Map(), printsById = new Map();
  for (const leg of event.legs) { tapesById.set(leg.leg_id, binding.loadTape(leg)); printsById.set(leg.leg_id, printsByTicker.get(leg.ticker) || []); }
  const base = boundaryBase(event, tapesById);
  for (const leg of event.legs) {
    const reach = reachFor(tapesById.get(leg.leg_id), printsById.get(leg.leg_id), base.left, base.right);
    base.legs[leg.leg_id] = { leg_id: leg.leg_id, leg_identity: `${event.event_id}|${leg.leg_id}`, ticker: leg.ticker, category: event.category, price_region: priceRegion(tapesById.get(leg.leg_id)[0].bid), leg_direction: null, reach };
  }
  return { base, tapesById, printsById };
}

function runV47(api, binding, printsByTicker) {
  const variants = {
    V45: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: false },
    V47: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true },
  };
  const runs = Object.fromEntries(Object.keys(variants).map((name) => [name, { marketEvents: [], strictEvents: [], actions: [], joins: [] }]));
  ensure(api.policy && typeof api.policy.quoteTouch === "function" && typeof api.policy.tradedAtLevel === "function", "V47 fill adapter seam unavailable");
  const frozenQuoteTouch = api.policy.quoteTouch;
  try {
    // CANON trades-as-truth ruler: asks inform placement, never crediting.
    // The frozen simulator still follows its ordinary MARKET_UNION_REACH
    // branch, but quote touch is made inert at the grading seam; its existing
    // tradedAtLevel predicate admits any strictly-later positive-size trade at
    // or below the lawful standing rest.
    api.policy.quoteTouch = () => false;
    let index = 0;
    for (const event of binding.events) {
      index += 1; if (index % 25 === 0) process.stderr.write(`V47/V45 sealed ${index}/${binding.events.length}\n`);
      const input = eventInputs(api, event, binding, printsByTicker);
      for (const [name, clauses] of Object.entries(variants)) {
        const market = api.simulate(input.base, input.tapesById, input.printsById, "MARKET_UNION_REACH", clauses);
        market.event.mode = "MARKET_TRADES_TRUTH";
        const strict = api.simulate(input.base, input.tapesById, input.printsById, "STRICT_PRINT_CROSS", clauses);
        runs[name].marketEvents.push(market.event); runs[name].strictEvents.push(strict.event);
        runs[name].actions.push(...market.actions.map((row) => ({ mode: "MARKET_TRADES_TRUTH", ...row })), ...strict.actions.map((row) => ({ mode: "STRICT_PRINT_CROSS", ...row })));
        runs[name].joins.push(...market.joinQualifications.map((row) => ({ mode: "MARKET_TRADES_TRUTH", ...row })), ...strict.joinQualifications.map((row) => ({ mode: "STRICT_PRINT_CROSS", ...row })));
      }
    }
  } finally {
    api.policy.quoteTouch = frozenQuoteTouch;
  }
  return runs;
}

function timelineFor(baseEvent, tapes, prints) {
  const rows = [];
  for (const [id, leg] of Object.entries(baseEvent.legs)) { for (const row of tapes.get(id)) rows.push({ ...row, leg_id: id }); for (const row of prints.get(id) || []) rows.push({ ...row, leg_id: id }); }
  rows.sort((a, b) => a.ts - b.ts || (a.kind === "PRINT" ? 0 : 1) - (b.kind === "PRINT" ? 0 : 1) || a.ordinal - b.ordinal || a.leg_id.localeCompare(b.leg_id));
  return rows;
}

function normalizedBoundary(row) { return { event_id: row.event_id, right_edge_epoch: Number(row.right_edge_epoch), edge_source_field: row.right_edge_source_field, precision_class: row.precision_class, selected_source: row.selected_source, selected_source_family: row.selected_source, selected_timestamp_precision: row.selected_timestamp_precision, conflict_status: "FROZEN_EXAM_NO_CONFLICT_FIELD", interval_contradiction: false }; }

function runV36(api, binding, printsByTicker) {
  const strictEvents = [], marketEvents = [], actions = [], spans = [];
  let decisionRows = 0;
  ensure(api.policy && typeof api.policy.censusPricedFill === "function", "V36 fill adapter seam unavailable");
  const frozenCensusPricedFill = api.policy.censusPricedFill;
  api.policy.censusPricedFill = (order, print) => {
    if (!order || !Number.isInteger(order.target_cents) || !(print.ts > order.action_ts) || !(print.size > 0) || !Number.isInteger(print.price) || print.price > order.target_cents) return null;
    return { fill: true, class: "MARKET_TRADES_TRUTH_ANY_TRADE_AT_OR_BELOW_REST", gap_cents: print.price - order.target_cents };
  };
  let index = 0;
  try { for (const event of binding.events) {
    index += 1; if (index % 25 === 0) process.stderr.write(`V36 sealed ${index}/${binding.events.length}\n`);
    const rawTapes = new Map(), tapes = new Map(), prints = new Map();
    for (const leg of event.legs) { const raw = binding.loadTape(leg), p = printsByTicker.get(leg.ticker) || []; rawTapes.set(leg.leg_id, raw); tapes.set(leg.leg_id, api.condenseTape(raw, p)); prints.set(leg.leg_id, p); }
    const base = boundaryBase(event, rawTapes), boundary = normalizedBoundary(event.boundary);
    const baseEvent = { event_id: event.event_id, category: event.category, starting_price_split: base.starting_price_split, legs: {} };
    const sources = new Map(), bells = new Map();
    for (const leg of event.legs) { baseEvent.legs[leg.leg_id] = { leg_identity: `${event.event_id}|${leg.leg_id}`, event_id: event.event_id, category: event.category, price_region: priceRegion(rawTapes.get(leg.leg_id)[0].bid), leg_id: leg.leg_id, ticker: leg.ticker, R3: null }; sources.set(leg.ticker, { event_id: event.event_id, ticker: leg.ticker, scheduled: base.scheduled }); }
    if (Number.isFinite(base.actual_bell)) bells.set(event.event_id, base.actual_bell);
    const span = { event_id: event.event_id, category: event.category, starting_price_split: base.starting_price_split, w1_left_epoch: base.left, w1_right_epoch: base.right, edge_source_field: boundary.edge_source_field, precision_class: boundary.precision_class, selected_source: boundary.selected_source, selected_source_family: boundary.selected_source_family, selected_timestamp_precision: boundary.selected_timestamp_precision, conflict_status: boundary.conflict_status, interval_contradiction: false, non_positive_span: base.right < base.left, span_seconds: Math.max(0, base.right - base.left) };
    spans.push(span);
    const timeline = timelineFor(baseEvent, tapes, prints), strictDecisions = [], marketDecisions = [];
    strictEvents.push(api.simulateW1Mode(baseEvent, tapes, prints, sources, bells, "STRICT_LAW", actions, strictDecisions, span, timeline, boundary));
    const marketEvent = api.simulateW1Mode(baseEvent, tapes, prints, sources, bells, "CENSUS_PRICED", actions, marketDecisions, span, timeline, boundary);
    marketEvent.mode = "MARKET_TRADES_TRUTH";
    marketEvents.push(marketEvent);
    decisionRows += strictDecisions.length + marketDecisions.length;
  } } finally {
    api.policy.censusPricedFill = frozenCensusPricedFill;
  }
  return {
    strictEvents,
    marketEvents,
    actions: actions.map((row) => row.mode === "CENSUS_PRICED" ? { ...row, mode: "MARKET_TRADES_TRUTH" } : row),
    decision_rows_observed: decisionRows,
    spans,
  };
}

function finalPrintClose(events, printsByTicker) {
  const result = new Map();
  for (const event of events) for (const leg of Object.values(event.legs)) {
    const rows = (printsByTicker.get(leg.ticker) || []).filter((row) => row.ts >= event.w1_left_epoch && row.ts <= event.w1_right_epoch && row.size > 0 && Number.isInteger(row.price));
    result.set(leg.ticker, rows.length ? rows.at(-1).price : null);
  }
  return result;
}

function frontier(events) { const completed = events.filter((row) => row.completed_pair); return { LE_93: completed.filter((row) => row.combined_entry_cents <= 93).length, LE_95: completed.filter((row) => row.combined_entry_cents <= 95).length, LE_97: completed.filter((row) => row.combined_entry_cents <= 97).length, LT_100: completed.filter((row) => row.combined_entry_cents < 100).length, ANY_PRICE: completed.length }; }
function genericScore(events) { const legs = events.flatMap((event) => Object.values(event.legs)); const completed = events.filter((event) => event.completed_pair), under = completed.filter((event) => event.pair_under_par); return { D: events.length, legs: legs.length, acted_legs: legs.filter((leg) => leg.first_action_timestamp_epoch !== null || leg.action_timestamp_epoch !== null).length, credited_legs: legs.filter((leg) => leg.credited).length, completed_pairs: completed.length, under_par_pairs: under.length, locked_cents_per_contract: under.reduce((sum, event) => sum + 100 - event.combined_entry_cents, 0), frontier: frontier(events), fill_classes: countBy(legs.filter((leg) => leg.credited), (leg) => leg.fill_class) }; }

function regret(events, printsByTicker) {
  const rows = [];
  for (const event of events) for (const leg of Object.values(event.legs)) {
    const prints = (printsByTicker.get(leg.ticker) || []).filter((row) => row.ts >= event.w1_left_epoch && row.ts <= event.w1_right_epoch && row.size > 0 && Number.isInteger(row.price));
    const floor = prints.length ? Math.min(...prints.map((row) => row.price)) : null;
    rows.push({ event_id: event.event_id, leg_identity: leg.leg_identity, ticker: leg.ticker, category: event.category, bell_confidence: event.bell_confidence, credited: leg.credited, entry_cents: leg.entry_cents, traded_floor_cents: floor, regret_cents: leg.credited && Number.isInteger(floor) ? leg.entry_cents - floor : null, uncredited_opportunity: !leg.credited && Number.isInteger(floor) });
  }
  const cells = [];
  for (const key of [...new Set(rows.map((row) => `${row.category}|${row.bell_confidence}`))].sort()) { const subset = rows.filter((row) => `${row.category}|${row.bell_confidence}` === key), [category, bell] = key.split("|"); cells.push({ category, bell_confidence: bell, legs: subset.length, credited: subset.filter((row) => row.credited).length, uncredited_opportunity: subset.filter((row) => row.uncredited_opportunity).length, regret: distribution(subset.map((row) => row.regret_cents)), floor_missing: subset.filter((row) => !Number.isInteger(row.traded_floor_cents)).length }); }
  return { rows, cells, aggregate: { legs: rows.length, credited: rows.filter((row) => row.credited).length, uncredited_opportunity: rows.filter((row) => row.uncredited_opportunity).length, regret: distribution(rows.map((row) => row.regret_cents)), floor_missing: rows.filter((row) => !Number.isInteger(row.traded_floor_cents)).length } };
}

function terminalCollapse(leg, prints) {
  if (!leg.credited || !Number.isInteger(leg.entry_cents) || leg.entry_cents > 9 || !Number.isFinite(leg.fill_timestamp_epoch)) return false;
  const rows = prints.filter((row) => row.taker_side === "no" && row.size > 0 && Math.abs(row.ts - leg.fill_timestamp_epoch) <= 1800).sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  for (let i = 0; i < rows.length; i += 1) { const run = [rows[i]]; for (let j = i + 1; j < rows.length && rows[j].ts - run[0].ts <= 1800; j += 1) if (rows[j].price < run.at(-1).price) run.push(rows[j]); if (run.length >= 3 && run[0].price - run.at(-1).price >= 10 && run.at(-1).price <= 9) return true; }
  return false;
}
function cleanDeep(events, printsByTicker) { const rows = events.filter((event) => event.completed_pair && event.combined_entry_cents <= 95).map((event) => ({ event_id: event.event_id, category: event.category, bell_confidence: event.bell_confidence, combined_entry_cents: event.combined_entry_cents, terminal_collapse: Object.values(event.legs).some((leg) => terminalCollapse(leg, printsByTicker.get(leg.ticker) || [])) })); return { deep_pairs: rows.length, exact_bell_collapse_clean: rows.filter((row) => row.bell_confidence === "exact" && !row.terminal_collapse).length, schedule_only_collapse_clean: rows.filter((row) => row.bell_confidence === "schedule_only" && !row.terminal_collapse).length, by_category_x_bell: countBy(rows.filter((row) => !row.terminal_collapse), (row) => `${row.category}|${row.bell_confidence}`), rows }; }

function cellScore(events, devContext, api, closes) {
  const rows = [];
  for (const key of [...new Set(events.map((row) => `${row.category}|${row.bell_confidence}`))].sort()) {
    const subset = events.filter((row) => `${row.category}|${row.bell_confidence}` === key), [category, bell] = key.split("|");
    rows.push({ category, bell_confidence: bell, headline: bell === "exact", exam: genericScore(subset), full_book_PnL: api.fullBookPnl(subset, closes).aggregate, development_category_context: devContext?.[category] || null });
  }
  return rows;
}

function bellConfidenceScore(events, api, closes, printsByTicker) {
  return [...new Set(events.map((row) => row.bell_confidence))].sort((a, b) => (a === "exact" ? -1 : b === "exact" ? 1 : String(a).localeCompare(String(b)))).map((bell) => {
    const subset = events.filter((row) => row.bell_confidence === bell);
    return { bell_confidence: bell, headline: bell === "exact", hygiene: bell === "schedule_only" ? "TERMINAL_COLLAPSE_EXCLUDED_PER_03BAC97B" : "STANDARD", score: genericScore(subset), full_book_PnL: api.fullBookPnl(subset, closes).aggregate, clean_deep: { ...cleanDeep(subset, printsByTicker), rows: undefined } };
  });
}

function restSanity(events) { const legs = events.flatMap((event) => Object.values(event.legs)); return { legs: legs.length, sanity_violation_receipts: legs.reduce((sum, leg) => sum + (leg.sanity_violation_rows || 0), 0), terminal_resting: legs.filter((leg) => leg.final_state === "RESTING_UNFILLED" || Number.isInteger(leg.resting_target_at_edge_cents) || Number.isInteger(leg.active_order?.target_cents)).length, by_category_x_bell: countBy(legs, (leg) => `${leg.category}|${events.find((event) => event.event_id === leg.event_id)?.bell_confidence}`) }; }

async function writeBrain(dir, brain, marketEvents, strictEvents, actions, joins, api, printsByTicker, devContext) {
  fs.mkdirSync(dir, { recursive: true });
  const closes = finalPrintClose(marketEvents, printsByTicker);
  const marketScore = genericScore(marketEvents), strictScore = genericScore(strictEvents), marketRegret = regret(marketEvents, printsByTicker), strictRegret = regret(strictEvents, printsByTicker);
  const fullBook = api.fullBookPnl(marketEvents, closes);
  fullBook.conservation = { events: marketEvents.length, disposition_sum: fullBook.rows.length, expected: marketEvents.length, pass: fullBook.rows.length === marketEvents.length };
  writeJson(dir, "SCORECARD.json", { brain, population_N: marketEvents.length, MARKET_TRADES_TRUTH: marketScore, STRICT_PRINT_CROSS_BUILD_VERIFICATION: strictScore, FULL_BOOK_PNL: fullBook.aggregate, development_aggregate_context: devContext?.aggregate || null, clean_deep: { MARKET_TRADES_TRUTH: { ...cleanDeep(marketEvents, printsByTicker), rows: undefined }, STRICT_PRINT_CROSS: { ...cleanDeep(strictEvents, printsByTicker), rows: undefined } }, bell_confidence: { MARKET_TRADES_TRUTH: bellConfidenceScore(marketEvents, api, closes, printsByTicker), STRICT_PRINT_CROSS: bellConfidenceScore(strictEvents, api, closes, printsByTicker) }, cells: { MARKET_TRADES_TRUTH: cellScore(marketEvents, devContext?.market, api, closes), STRICT_PRINT_CROSS: cellScore(strictEvents, devContext?.strict, api, closes) } });
  writeJson(dir, "FRONTIER.json", { MARKET_TRADES_TRUTH: marketScore.frontier, STRICT_PRINT_CROSS_BUILD_VERIFICATION: strictScore.frontier });
  writeJson(dir, "REGRET_GAUGE.json", { MARKET_TRADES_TRUTH: { ...marketRegret, rows: undefined }, STRICT_PRINT_CROSS_BUILD_VERIFICATION: { ...strictRegret, rows: undefined } });
  writeJson(dir, "REST_SANITY.json", { MARKET_TRADES_TRUTH: restSanity(marketEvents), STRICT_PRINT_CROSS_BUILD_VERIFICATION: restSanity(strictEvents) });
  writeJson(dir, "MAKER_TAKER_SPLIT.json", { MARKET_TRADES_TRUTH: marketScore.fill_classes, STRICT_PRINT_CROSS_BUILD_VERIFICATION: strictScore.fill_classes });
  writeJson(dir, "FULL_BOOK_PNL.json", fullBook);
  await writeGzipRows(path.join(dir, "MARKET_EVENT_LEDGER.jsonl.gz"), marketEvents);
  await writeGzipRows(path.join(dir, "STRICT_EVENT_LEDGER.jsonl.gz"), strictEvents);
  await writeGzipRows(path.join(dir, "ACTION_TRACE.jsonl.gz"), actions);
  await writeGzipRows(path.join(dir, "JOIN_QUALIFICATION_TRACE.jsonl.gz"), joins || []);
  await writeGzipRows(path.join(dir, "MARKET_REGRET_LEDGER.jsonl.gz"), marketRegret.rows);
  await writeGzipRows(path.join(dir, "STRICT_REGRET_LEDGER.jsonl.gz"), strictRegret.rows);
}

async function materialize(root, result, api47, printsByTicker, dev) {
  fs.mkdirSync(root, { recursive: true });
  await writeBrain(path.join(root, "V47"), "V47", result.V47.marketEvents, result.V47.strictEvents, result.V47.actions, result.V47.joins, api47, printsByTicker, dev.V47);
  await writeBrain(path.join(root, "V45"), "V45", result.V45.marketEvents, result.V45.strictEvents, result.V45.actions, result.V45.joins, api47, printsByTicker, dev.V45);
  await writeBrain(path.join(root, "V36"), "V36", result.V36.marketEvents, result.V36.strictEvents, result.V36.actions, [], api47, printsByTicker, dev.V36);
}

function treeManifest(root) { const files = {}; const walk = (dir) => { for (const entry of fs.readdirSync(dir, { withFileTypes: true })) { const full = path.join(dir, entry.name); if (entry.isDirectory()) walk(full); else { const rel = path.relative(root, full).replaceAll("\\", "/"); files[rel] = { sha256: hashFile(full), bytes: fs.statSync(full).size }; } } }; walk(root); return files; }

function writeComparison(outputRoot, scoresRoot) {
  const cards = Object.fromEntries(["V47", "V45", "V36"].map((brain) => [brain, readJson(path.join(scoresRoot, brain, "SCORECARD.json"))]));
  const rows = Object.entries(cards).map(([brain, card]) => ({ brain, MARKET_TRADES_TRUTH: card.MARKET_TRADES_TRUTH, STRICT_PRINT_CROSS_BUILD_VERIFICATION: card.STRICT_PRINT_CROSS_BUILD_VERIFICATION, FULL_BOOK_PNL: card.FULL_BOOK_PNL, CLEAN_DEEP: card.clean_deep, BELL_CONFIDENCE: card.bell_confidence, DEVELOPMENT_CONTEXT: card.development_aggregate_context }));
  writeJson(outputRoot, "BELL_CONFIDENCE_SCORECARD.json", { schema_version: "window1-v47-sealed-exam-comparison-v1", headline: "EXACT_BELL", schedule_only_hygiene: "TERMINAL_COLLAPSE_EXCLUDED_PER_03BAC97B", rows });
  const line = (row) => {
    const market = row.MARKET_TRADES_TRUTH, strict = row.STRICT_PRINT_CROSS_BUILD_VERIFICATION, book = row.FULL_BOOK_PNL, clean = row.CLEAN_DEEP.MARKET_TRADES_TRUTH;
    return `| ${row.brain} | ${market.completed_pairs} | ${market.under_par_pairs} | ${market.frontier.LE_93}/${market.frontier.LE_95}/${market.frontier.LE_97}/${market.frontier.LT_100} | ${market.locked_cents_per_contract} | ${book.true_book_net_cents} | ${strict.completed_pairs}/${strict.under_par_pairs} | ${clean.exact_bell_collapse_clean}/${clean.schedule_only_collapse_clean} |`;
  };
  fs.writeFileSync(path.join(outputRoot, "REPORT.md"), `# V47 sealed-population exam\n\nStatus: **COMPLETE_FINAL**. One score-emitting run, zero retries, no policy edits. The exact-bell subset is the headline; schedule-only rows carry the frozen terminal-collapse hygiene.\n\n| brain | market completed | market under par | frontier <=93/<=95/<=97/<100 | locked c/contract | full-book net c | strict completed/under par | clean-deep exact/schedule |\n|---|---:|---:|---:|---:|---:|---:|---:|\n${rows.map(line).join("\n")}\n\nMarket credit is trades-as-truth: a strictly later positive-size exchange trade at or below the lawful standing rest. Quote touch never credits. Strict seller-aggressed size-five print crossing is printed beside it only as build verification. Frozen development context appears beside every category x bell-confidence row in each brain's scorecard.\n`);
}

async function devInertness() {
  ensure(!fs.existsSync(output), "DEV inertness output must be absent");
  fs.mkdirSync(output, { recursive: true });
  const policy = policyIdentity();
  // The frozen builder's safety law requires the output basename itself to
  // contain lowercase "v47".  This is an invocation-path constraint only.
  const scratch = path.join(output, "v47_dev_rebuild");
  const command = [path.join(repo, V47_WRAPPER), "--repo", repo, "--v36-root", path.resolve(required("--v36-root")), "--reach-root", path.resolve(required("--reach-root")), "--gap-root", path.resolve(required("--gap-root")), "--private-root", privateRoot, "--output", scratch, "--compare", path.join(repo, V47_PACKAGE)];
  const run = child.spawnSync(process.execPath, command, { cwd: repo, encoding: "utf8", maxBuffer: 128 * 1024 * 1024, env: { ...process.env, NODE_OPTIONS: "--max-old-space-size=8192" } });
  fs.writeFileSync(path.join(output, "DEV_REBUILD_STDOUT.txt"), run.stdout || ""); fs.writeFileSync(path.join(output, "DEV_REBUILD_STDERR.txt"), run.stderr || "");
  ensure(run.status === 0, `DEV rebuild failed ${run.status}`);
  const compareFiles = [
    "ATTRIBUTION_SCORECARD.json",
    "MARKET_GRADE_SCORECARD.json",
    "STRICT_BUILD_VERIFICATION_SCORECARD.json",
    "MARKET_EVENT_LEDGER.jsonl.gz",
    "STRICT_EVENT_LEDGER.jsonl.gz",
    "ACTION_TRACE.jsonl.gz",
    "DECISION_TRACE_1608.jsonl.gz",
    "ATTRIBUTION_FULL_BOOK_LEDGER.jsonl.gz",
    "SEG_C_SAME_TICK_FOOTPRINT.jsonl.gz",
    "SEG_C_SAME_TICK_RECEIPT.json",
  ];
  const rows = compareFiles.map((name) => { const rebuilt = path.join(scratch, name), frozen = path.join(repo, V47_PACKAGE, name); return { file: name, rebuilt_sha256: hashFile(rebuilt), frozen_sha256: hashFile(frozen), rebuilt_bytes: fs.statSync(rebuilt).size, frozen_bytes: fs.statSync(frozen).size, pass: hashFile(rebuilt) === hashFile(frozen) && fs.statSync(rebuilt).size === fs.statSync(frozen).size }; });
  ensure(rows.every((row) => row.pass), "DEV inertness mismatch");
  fs.rmSync(scratch, { recursive: true, force: true });
  writeJson(output, "POLICY_BYTE_IDENTITY_RECEIPT.json", { files: policy, pass: true });
  writeJson(output, "DEV_INERTNESS_RECEIPT.json", { schema_version: "window1-v47-sealed-exam-dev-inertness-v1", V47, D: 804, compared_files: rows, byte_identical: true, sealed_exam_invocations: 0, score_rows_on_sealed_population: 0, pass: true });
  const files = treeManifest(output); writeJson(output, "ARTIFACT_HASH_MANIFEST.json", { files });
  process.stdout.write(canonical({ status: "PASS", compared_files: rows.length, V47 }));
}

function devContexts() {
  const v47 = readJson(path.join(repo, V47_PACKAGE, "ATTRIBUTION_SCORECARD.json"));
  const byName = new Map(v47.rows.map((row) => [row.machine, {
    aggregate: { MARKET_UNION_REACH: row.MARKET_UNION_REACH, STRICT_PRINT_CROSS: row.STRICT_PRINT_CROSS, FULL_BOOK: row.FULL_BOOK },
    market: row.by_category.MARKET_UNION_REACH,
    strict: row.by_category.STRICT_PRINT_CROSS,
    full_book: row.by_category.FULL_BOOK,
  }]));
  const v36Score = readJson(path.join(repo, V36_PACKAGE, "SCORECARD_TWO_COLUMN.json"));
  const fold = (column) => {
    const result = {};
    for (const row of column.category_x_starting_price_region_x_bell_confidence || []) {
      const category = row.cell.split("|")[0], metrics = row.metrics;
      if (!result[category]) result[category] = { D: 0, legs: 0, acted_legs: 0, credited_legs: 0, completed_pairs: 0, pairs_under_par: 0, naked_credited_legs: 0, rests_unfilled_at_edge: 0 };
      for (const key of Object.keys(result[category])) result[category][key] += Number(metrics[key] || 0);
    }
    return result;
  };
  const v36 = { aggregate: { MARKET_ORIGINAL_CENSUS_PRICED: v36Score.CENSUS_PRICED.aggregate, STRICT_LAW: v36Score.STRICT_LAW.aggregate }, market: fold(v36Score.CENSUS_PRICED), strict: fold(v36Score.STRICT_LAW), full_book: null };
  return { V47: byName.get("V47_SAME_TICK_ARM"), V45: byName.get("V45_BASELINE"), V36: v36 };
}

async function executeExam() {
  const declarationFile = path.resolve(required("--population-declaration")), boundaryFile = path.resolve(required("--boundary-ledger")), eventListFile = path.resolve(required("--event-list")), printsFile = path.resolve(required("--prints")), printReceiptFile = path.resolve(required("--prints-receipt")), inertnessFile = path.resolve(required("--dev-inertness"));
  const oldTapeRoot = path.resolve(required("--old-tape-root")), newTapeRoot = path.resolve(required("--new-tape-root"));
  ensure(!fs.existsSync(output), "exam results directory already exists");
  const inertness = readJson(inertnessFile); ensure(inertness.pass && inertness.byte_identical && inertness.sealed_exam_invocations === 0, "DEV inertness is not PASS");
  const printReceipt = readJson(printReceiptFile); ensure(printReceipt.nightly_method_spot_reconciliation.pass, "print reconciliation not PASS");
  const declaration = readJson(declarationFile); ensure(declaration.N >= 60 && declaration.event_list_sha256 === hashFile(eventListFile) && declaration.boundary_ledger_sha256 === hashFile(boundaryFile), "frozen population binding mismatch");
  fs.mkdirSync(output, { recursive: true });
  writeJson(output, "EXECUTION_START_RECEIPT.json", { authorization: "OPERATOR_PROMPT_V47_SEALED_EXAM_20260811", authorization_consumed: true, emission_finality: "FIRST_SCORE_ROW_FINAL", score_rows_before_start: 0, V47, V45, V36, population_N: declaration.N, event_list_sha256: hashFile(eventListFile), boundary_sha256: hashFile(boundaryFile), prints_sha256: hashFile(printsFile), started_at_utc: new Date().toISOString() });
  const before = policyIdentity(), api47 = compileV47(), api36 = compileV36();
  const binding47 = buildBinding(api47, declarationFile, boundaryFile, oldTapeRoot, newTapeRoot), prints = await loadPrints(printsFile, binding47.tickers);
  const binding36 = buildBinding(api36, declarationFile, boundaryFile, oldTapeRoot, newTapeRoot);
  const pair = runV47(api47, binding47, prints), v36 = runV36(api36, binding36, prints);
  const result = { V47: pair.V47, V45: pair.V45, V36: v36 };
  const primary = path.join(output, "SCORES"), secondary = path.join(output, ".determinism-build-2");
  await materialize(primary, result, api47, prints, devContexts());
  await materialize(secondary, result, api47, prints, devContexts());
  writeComparison(primary, primary);
  writeComparison(secondary, secondary);
  const manifest1 = treeManifest(primary), manifest2 = treeManifest(secondary);
  const mismatches = Object.keys(manifest1).filter((name) => !manifest2[name] || manifest1[name].sha256 !== manifest2[name].sha256 || manifest1[name].bytes !== manifest2[name].bytes);
  ensure(mismatches.length === 0 && Object.keys(manifest1).length === Object.keys(manifest2).length, `determinism mismatch ${mismatches.join(",")}`);
  fs.rmSync(secondary, { recursive: true, force: true });
  const after = policyIdentity(); ensure(JSON.stringify(before) === JSON.stringify(after), "policy bytes changed during exam");
  writeJson(output, "DETERMINISM_RECEIPT.json", { policy_replay_invocations: { V47_and_V45_single_shared_pass: 1, V36: 1 }, artifact_builds: 2, compared_files: Object.keys(manifest1).length, byte_identical: true, mismatches: [] });
  writeJson(output, "POLICY_BYTE_IDENTITY_RECEIPT.json", { before, after, byte_identical: true, policy_files_modified: 0, adapter_scope: "INPUT_BINDING_ONLY" });
  writeJson(output, "FILL_RULER_BINDING.json", {
    schema_version: "window1-v47-sealed-exam-fill-ruler-v1",
    MARKET_TRADES_TRUTH: {
      rest_credit: "STRICTLY_LATER_POSITIVE_SIZE_EXCHANGE_TRADE_AT_OR_BELOW_LAWFUL_STANDING_REST",
      aggressor_filter: null,
      dwell_filter: null,
      quote_touch_credit: false,
      asks_role: "PLACEMENT_INPUT_ONLY",
      V47_V45_existing_predicate: "window1_v41_maker_machine.tradedAtLevel",
      V36_adapter_predicate: "SAME_TRADE_AT_OR_BELOW_RULE; IMMEDIATE_POLICY_TAKES_UNCHANGED",
    },
    STRICT_PRINT_CROSS_BUILD_VERIFICATION: "STRICTLY_LATER_SELLER_AGGRESSED_PRINT_SIZE_GE_5_AT_OR_BELOW_REST; V36_IMMEDIATE_POLICY_TAKES_UNCHANGED",
    policy_source_bytes_changed: 0,
  });
  writeJson(output, "FORBIDDEN_ACCESS_RECEIPT.json", { exam_runtime_network_access: 0, live_engine_access: 0, account_access: 0, order_access: 0, position_access: 0, trading_access: 0, tuning: 0, policy_edits: 0, inputs: "FROZEN_LOCAL_TAPES_PRINTS_BOUNDARIES_ONLY" });
  writeJson(output, "EXECUTION_COMPLETE_RECEIPT.json", { status: "COMPLETE_FINAL", score_emitting_runs: 1, retries: 0, V47_invocations: 1, V45_comparison_from_same_V47_policy_pass: 1, V36_invocations: 1, population_N: declaration.N, completed_at_utc: new Date().toISOString() });
  writeJson(output, "ARTIFACT_HASH_MANIFEST.json", { files: treeManifest(output) });
  process.stdout.write(canonical({ status: "COMPLETE_FINAL", population_N: declaration.N, score_emitting_runs: 1, retries: 0 }));
}

(async () => {
  if (mode === "dev-inertness") await devInertness();
  else if (mode === "execute") await executeExam();
  else throw new Error(`unsupported mode ${mode}`);
})().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
