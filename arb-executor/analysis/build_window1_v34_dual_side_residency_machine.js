#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const child = require("child_process");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const policy = require("./window1_v34_dual_side_residency_machine.js");

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const repo = path.resolve(arg("--repo", "."));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const output = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/v34_dual_side_residency_machine_20260805")));
const compare = arg("--compare", null);
const base = path.join(repo, ".claude/window1_live_v4_replay/v29r3_standing_floor_release_20260805");
const floorFile = path.join(repo, ".claude/window1_live_v4_replay/trade_floor_correction_v8_20260802/DUAL_FLOOR_LEG_LEDGER.jsonl.gz");
const baseTraceFile = path.join(base, "DECISION_TRACE_1608.json");
const quoteFile = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const bellFile = path.join(repo, ".claude/window1_live_v4_replay/actual_bell_refit_20260729/ACTUAL_BELL_REFIT.json");
const publicTapeManifest = path.join(privateRoot, "fit-local/PUBLIC_TAPE_MANIFEST.sanitized.json");
const spoolHelperFile = path.join(repo, "arb-executor/analysis/window1_v32_print_spool.ps1");
const spoolHelperSourceFile = path.join(repo, "arb-executor/analysis/window1_v32_print_spool.cs");
const builderFile = __filename;
const policyFile = path.join(repo, "arb-executor/analysis/window1_v34_dual_side_residency_machine.js");
const unitTestFile = path.join(repo, "arb-executor/tests/test_window1_v34_dual_side_residency_machine.js");
const packageTestFile = path.join(repo, "arb-executor/tests/test_window1_v34_dual_side_residency_package.js");
const V34_PARENT = "d5adc4ff080decef634309b7d1d022c2fd4b6841";
const V32_COMMIT = "a3429cad6719f96a25a900812e0f360b71a5607e";
const R3_COMMIT = "49f6501561c5d99a7f36c68ec41e0ea7250680e5";
const RECON_COMMIT = "938dca474e8bc4d96b17095e2aaa7cbb2fe97a87";
const NEARMISS_COMMIT = "65d49b5d623d99fb1d8ad3ef7eee6be9225c328e";
const RECON_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/RECONCILIATION_SEAL_804.json";
const NEARMISS_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/V32_NEARMISS_CENSUS.json";

function ensure(value, message) { if (!value) throw new Error(message); }
function sha(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function fileHash(file) { return sha(fs.readFileSync(file)); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function semantic(value) { return sha(JSON.stringify(value)); }
function write(name, bytes) { fs.writeFileSync(path.join(output, name), bytes); }
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function readRows(file) { const text = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse) : []; }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
function parseCsv(text) { const lines = text.trimEnd().split(/\r?\n/); const h = lines.shift().split(","); return lines.filter(Boolean).map((line) => Object.fromEntries(line.split(",").map((v, i) => [h[i], v]))); }
function parseEt(value) { const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/); if (!m) return null; let h = +m[4]; if (m[7] === "AM" && h === 12) h = 0; if (m[7] === "PM" && h !== 12) h += 12; return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(h).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000; }
function group(rows, fn) { const out = new Map(); for (const row of rows) { const key = fn(row); if (!out.has(key)) out.set(key, []); out.get(key).push(row); } return out; }
function countBy(rows, fn) { const out = {}; for (const row of rows) { const key = String(fn(row)); out[key] = (out[key] || 0) + 1; } return Object.fromEntries(Object.entries(out).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function quantile(values, p) { const x = values.filter(Number.isFinite).sort((a, b) => a - b); return x.length ? x[Math.floor((x.length - 1) * p)] : null; }
function distribution(values, unit = null) { const x = values.filter(Number.isFinite), total = x.reduce((a, b) => a + b, 0); const out = { denominator: values.length, numeric_n: x.length, null_n: values.length - x.length, min: x.length ? Math.min(...x) : null, p25: quantile(x, .25), median: quantile(x, .5), p75: quantile(x, .75), p90: quantile(x, .9), max: x.length ? Math.max(...x) : null, total }; if (unit) out[`total_${unit}`] = total; return out; }
function gitShow(commit, rel) { return child.execFileSync("git", ["show", `${commit}:${rel}`], { cwd: repo, maxBuffer: 128 * 1024 * 1024 }); }
function requireCommit(commit) { ensure(child.execFileSync("git", ["rev-parse", "--verify", `${commit}^{commit}`], { cwd: repo, encoding: "utf8" }).trim() === commit, `missing commit ${commit}`); child.execFileSync("git", ["cat-file", "-e", `${commit}^{commit}`], { cwd: repo }); }
function safeClean(dir) { const r = path.resolve(dir); ensure(path.basename(r).toLowerCase().includes("v34"), `unsafe output ${r}`); ensure(r !== repo && r !== path.parse(r).root, `unsafe output ${r}`); fs.rmSync(r, { recursive: true, force: true }); fs.mkdirSync(r, { recursive: true }); }

function loadBaseEvents() {
  const floors = readRows(floorFile);
  const traceRows = JSON.parse(fs.readFileSync(baseTraceFile)).rows;
  ensure(floors.length === 1608 && traceRows.length === 1608, "R3 leg denominator failed");
  const traceBy = new Map(traceRows.map((row) => [row.leg_identity, row]));
  const byEvent = new Map();
  for (const floor of floors) {
    const prior = traceBy.get(floor.leg_identity); ensure(prior, `missing R3 ${floor.leg_identity}`);
    const state = prior.leg_action_state;
    const leg = { leg_identity: floor.leg_identity, event_id: floor.event_id, category: floor.category, starting_price_split: prior.starting_price_split, price_region: floor.price_region, leg_id: floor.leg_id, ticker: floor.ticker, R3: { acted: state.acted, credited: state.credited, entry_cents: state.entry_cents } };
    if (!byEvent.has(floor.event_id)) byEvent.set(floor.event_id, { event_id: floor.event_id, category: floor.category, starting_price_split: prior.starting_price_split, legs: {} });
    byEvent.get(floor.event_id).legs[floor.leg_id] = leg;
  }
  return [...byEvent.values()].sort((a, b) => a.event_id.localeCompare(b.event_id));
}

function loadSources() {
  const map = new Map();
  for (const row of parseCsv(fs.readFileSync(quoteFile, "utf8"))) map.set(row.ticker, { event_id: row.event_id, ticker: row.ticker, scheduled: +row.scheduled_start_ts });
  return map;
}

function loadFullTape(ticker, hashes) {
  const file = path.join(privateRoot, "fit-local/ticks", `${ticker}.csv.gz`); ensure(fs.existsSync(file), `missing tape ${ticker}`);
  const bytes = fs.readFileSync(file); hashes[ticker] = { sha256: sha(bytes), bytes: bytes.length };
  const lines = zlib.gunzipSync(bytes).toString("utf8").trimEnd().split(/\r?\n/); const header = lines.shift().split(","); const ix = Object.fromEntries(header.map((v, i) => [v, i])); const out = [];
  for (let n = 0; n < lines.length; n += 1) {
    const v = lines[n].split(","), ts = parseEt(v[ix.ts_et]); if (!Number.isFinite(ts)) continue;
    const bids = [], asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bp = integer(v[ix[`bid_${level}`]]), bs = positive(v[ix[`bid_${level}_sz`]]), ap = integer(v[ix[`ask_${level}`]]), as = positive(v[ix[`ask_${level}_sz`]]);
      if (bp !== null && bs !== null) bids.push([bp, bs]); if (ap !== null && as !== null) asks.push([ap, as]);
    }
    if (!bids.length || !asks.length) continue;
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]);
    out.push({ kind: "BOOK", ticker, ts, ordinal: n + 2, receipt: `${ticker}.csv.gz#row-${n + 2}`, bid: bids[0][0], ask: asks[0][0], spread: asks[0][0] - bids[0][0], top_bid_size: bids[0][1], top_ask_size: asks[0][1], bid_depth_5: bids.reduce((s, x) => s + x[1], 0), ask_depth_5: asks.reduce((s, x) => s + x[1], 0), last_trade: integer(v[ix.last_trade]) });
  }
  out.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  let ask = null, since = null;
  for (const row of out) { if (row.ask !== ask) { ask = row.ask; since = row.ts; } row.ask_dwell_seconds = row.ts - since; row.depth_ratio = row.bid_depth_5 / (row.bid_depth_5 + row.ask_depth_5); }
  out.rawReceiptCount = out.length;
  return out;
}

function condenseTape(rows, prints) {
  if (!rows.length) { const empty = []; empty.rawReceiptCount = 0; return empty; }
  const keep = new Set([0, rows.length - 1]);
  const firstAtOrAfter = (ts) => { let lo = 0, hi = rows.length; while (lo < hi) { const mid = (lo + hi) >> 1; if (rows[mid].ts < ts) lo = mid + 1; else hi = mid; } return lo < rows.length ? lo : null; };
  let prior = null;
  for (let i = 0; i < rows.length; i += 1) {
    const row = rows[i], pressure = policy.pressureState(row.depth_ratio), take = policy.r3QualifiedTake(row);
    if (!prior || row.bid !== prior.row.bid || row.ask !== prior.row.ask || pressure !== prior.pressure || take !== prior.take || (prior.row.ask_dwell_seconds < policy.QUALIFIED_DWELL_MIN_SECONDS && row.ask_dwell_seconds >= policy.QUALIFIED_DWELL_MIN_SECONDS)) keep.add(i);
    if (prior && (row.ask < prior.row.ask || row.bid > prior.row.bid)) { const expiry = firstAtOrAfter(row.ts + policy.LOOKBACK_SECONDS); if (expiry !== null) keep.add(expiry); }
    prior = { row, pressure, take };
  }
  for (const print of prints) { const next = firstAtOrAfter(print.ts), expiry = firstAtOrAfter(print.ts + policy.LOOKBACK_SECONDS); if (next !== null) keep.add(next); if (expiry !== null) keep.add(expiry); }
  const out = [...keep].sort((a, b) => a - b).map((i) => rows[i]); out.rawReceiptCount = rows.rawReceiptCount; out.condensedReceiptCount = out.length; return out;
}

function buildPrintSpool(tickers) {
  const spool = path.join(output, ".print-spool"), sourceContract = path.join(output, ".print-spool-sources.csv"), receiptFile = path.join(output, ".print-spool-receipt.json");
  fs.mkdirSync(spool, { recursive: true });
  fs.writeFileSync(sourceContract, `ticker,left,right\n${[...tickers].sort().map((ticker) => `${ticker},0,4102444800`).join("\n")}\n`);
  child.execFileSync("powershell.exe", ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", spoolHelperFile, "-Prints", path.join(privateRoot, "fit-local/prints.jsonl"), "-Sources", sourceContract, "-Spool", spool, "-Receipt", receiptFile, "-SourceCode", spoolHelperSourceFile], { cwd: repo, stdio: "inherit" });
  fs.rmSync(sourceContract); const rawReceipt = JSON.parse(fs.readFileSync(receiptFile)); fs.rmSync(receiptFile);
  return {
    load(ticker) { const file = path.join(spool, `${ticker}.jsonl`); if (!fs.existsSync(file)) return []; const text = fs.readFileSync(file, "utf8").trim(); const rows = text ? text.split(/\r?\n/).map(JSON.parse).map(([ts, ordinal, receipt, price, size, taker_side, trade_id]) => ({ kind: "PRINT", ticker, ts, ordinal, receipt, price, size, taker_side, trade_id })) : []; rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal); return rows; },
    cleanup() { fs.rmSync(spool, { recursive: true, force: true }); },
    receipt: { ...rawReceipt, legacy_helper_counter_name: "admitted_unique_window1_prints", admitted_unique_full_market_life_prints: rawReceipt.admitted_unique_window1_prints, bounds_supplied: "0_TO_4102444800_ALL_EXCHANGE_PRINTS" },
  };
}

function clock(ts, source, bell, marketClose) {
  return { timestamp_epoch: ts, t_minus_scheduled_seconds: Number.isFinite(source?.scheduled) ? source.scheduled - ts : null, t_minus_actual_bell_seconds: Number.isFinite(bell) ? bell - ts : null, seconds_to_market_close: Number.isFinite(marketClose) ? marketClose - ts : null };
}

function closeFromPrints(rows) {
  if (!rows.length) return { status: "UNAVAILABLE_NO_TRUE_EXCHANGE_PRINT", price_cents: null, timestamp_epoch: null, receipts: [] };
  // The sealed exchange archive preserves an authoritative ordinal inside each
  // second. "Final exchange print" is the final ordered row, not an unordered
  // same-second price set.
  const final = rows.at(-1);
  return { status: "AVAILABLE_FINAL_ORDERED_TRUE_EXCHANGE_PRINT", price_cents: final.price, timestamp_epoch: final.ts, ordinal: final.ordinal, receipts: [final.receipt], aggressor_sides: [final.taker_side], total_size: final.size };
}

function armSibling(sibling, fillLeg, row, mode, actions, eventClose) {
  sibling.pair_cap_cents = 99 - fillLeg.entry_cents;
  const source = sibling.source, bell = sibling.bell;
  actions.push({ mode, kind: "PAIR_ARM", event_id: sibling.event_id, leg_identity: sibling.leg_identity, sibling_fill_cents: fillLeg.entry_cents, pair_cap_cents: sibling.pair_cap_cents, receipt: row.receipt, ...clock(row.ts, source, bell, eventClose), same_receipt_fill_forbidden: true });
  if (sibling.active_order && sibling.active_order.target_cents > sibling.pair_cap_cents) {
    if (policy.lawfulCent(sibling.pair_cap_cents)) sibling.active_order = { target_cents: sibling.pair_cap_cents, action_ts: row.ts, action_receipt: row.receipt, action: "PAIR_CAP_REPRICE", source_state: "SIBLING_FILL" };
    else sibling.active_order = null;
  }
}

function simulateMode(baseEvent, tapes, prints, sources, bells, mode, actionRows, span, timeline) {
  const ids = Object.keys(baseEvent.legs).sort(), event = { event_id: baseEvent.event_id, category: baseEvent.category, starting_price_split: baseEvent.starting_price_split, mode, market_life_start_epoch: span.market_life_start_epoch, market_close_epoch: span.market_close_epoch, legs: {} };
  for (const id of ids) {
    const b = baseEvent.legs[id], p = prints.get(b.ticker), t = tapes.get(b.ticker), close = closeFromPrints(p);
    event.legs[id] = { ...b, source: sources.get(b.ticker), bell: bells.get(baseEvent.event_id), market_life_close_status: close.status, own_market_life_close_cents: close.price_cents, own_market_life_close_timestamp_epoch: close.timestamp_epoch, own_market_life_close_receipts: close.receipts, own_market_life_traded_low_cents: p.length ? p.reduce((low, x) => Math.min(low, x.price), Infinity) : null, own_full_life_qualifying_ask_floor_cents: null, acted: false, credited: false, entry_cents: null, fill_class: null, action_timestamp_epoch: null, fill_timestamp_epoch: null, pair_cap_cents: null, active_order: null, prior_book: null, latest_directional: null, running_trade_low: null, running_qualified_ask_low: null, decisions: 0, state_counts: { FALLING: 0, RISING: 0, SETTLED: 0 }, action_counts: {}, disagreement_count: 0, maker_reprices: 0, first_decision: null, last_decision: null, first_action: null, terminal_reason: null, first_book_epoch: t[0]?.ts ?? null, last_book_epoch: t.at(-1)?.ts ?? null, first_print_epoch: p[0]?.ts ?? null, last_print_epoch: p.at(-1)?.ts ?? null };
  }
  for (const row of timeline) {
    if (event.legs[ids[0]].credited && event.legs[ids[1]].credited) break;
    if (row.ts < span.market_life_start_epoch || row.ts > span.market_close_epoch) continue;
    const leg = event.legs[row.leg_id]; if (leg.credited) continue; const sibling = event.legs[ids.find((id) => id !== row.leg_id)];
    if (row.kind === "PRINT") {
      let maker = null;
      if (mode === "STRICT_LAW" && policy.strictMakerFill(leg.active_order, row)) maker = { class: "PROVEN_MAKER_SELLER_AGGRESSED_PRINT_SIZE_FIVE_AT_OR_BELOW_REST", strict: true };
      if (mode === "CENSUS_PRICED") maker = policy.censusPricedFill(leg.active_order, row);
      if (maker?.fill || maker?.strict || maker?.class === "PROVEN_MAKER_SELLER_AGGRESSED_PRINT_SIZE_FIVE_AT_OR_BELOW_REST") {
        leg.credited = true; leg.entry_cents = leg.active_order.target_cents; leg.action_timestamp_epoch = leg.active_order.action_ts; leg.fill_timestamp_epoch = row.ts; leg.fill_class = maker.class; leg.terminal_reason = maker.class;
        actionRows.push({ mode, kind: "FILL", event_id: event.event_id, leg_identity: leg.leg_identity, fill_class: maker.class, entry_cents: leg.entry_cents, action_timestamp_epoch: leg.action_timestamp_epoch, receipt: row.receipt, print: { price_cents: row.price, size: row.size, taker_side: row.taker_side }, ...clock(row.ts, leg.source, leg.bell, span.market_close_epoch) });
        armSibling(sibling, leg, row, mode, actionRows, span.market_close_epoch);
      }
      if (!leg.credited) {
        leg.running_trade_low = leg.running_trade_low === null ? row.price : Math.min(leg.running_trade_low, row.price);
        if (row.taker_side === "no" || row.taker_side === "yes") leg.latest_directional = { ts: row.ts, ordinal: row.ordinal, direction: row.taker_side === "no" ? "FALLING" : "RISING", kind: row.taker_side === "no" ? "SELLER_HIT_PRINT" : "BUYER_LIFT_PRINT", receipt: row.receipt };
      }
      continue;
    }
    const prior = leg.prior_book, newLowAsk = prior && row.ask < prior.ask, newHighBid = prior && row.bid > prior.bid;
    if (newLowAsk && newHighBid) leg.latest_directional = { ts: row.ts, ordinal: row.ordinal, direction: "SETTLED", kind: "QUOTE_PATH_INTERNAL_CONFLICT_NEW_LOW_ASK_AND_NEW_HIGH_BID", receipt: row.receipt };
    else if (newLowAsk) leg.latest_directional = { ts: row.ts, ordinal: row.ordinal, direction: "FALLING", kind: "NEW_LOW_ASK", receipt: row.receipt };
    else if (newHighBid) leg.latest_directional = { ts: row.ts, ordinal: row.ordinal, direction: "RISING", kind: "NEW_HIGH_BID", receipt: row.receipt };
    if (policy.r3QualifiedTake(row)) leg.running_qualified_ask_low = leg.running_qualified_ask_low === null ? row.ask : Math.min(leg.running_qualified_ask_low, row.ask);
    leg.own_full_life_qualifying_ask_floor_cents = leg.running_qualified_ask_low;
    const quote = policy.quotePathState(leg.latest_directional ? [leg.latest_directional] : [], row.ts), pressure = policy.pressureState(row.depth_ratio), combined = policy.combineState(quote, pressure);
    const decision = policy.decide({ state: combined.state, book: row, activeTarget: leg.active_order?.target_cents ?? null, pairCap: leg.pair_cap_cents, runningTradeLow: leg.running_trade_low, runningQualifyingAskLow: leg.running_qualified_ask_low });
    leg.prior_book = row; leg.decisions += 1; leg.state_counts[combined.state] += 1; if (combined.disagreement) leg.disagreement_count += 1; leg.action_counts[decision.action] = (leg.action_counts[decision.action] || 0) + 1;
    const detail = { receipt: row.receipt, ...clock(row.ts, leg.source, leg.bell, span.market_close_epoch), observation: { bid: row.bid, ask: row.ask, last_traded: row.last_trade, spread: row.spread, ask_dwell_seconds: row.ask_dwell_seconds, top_ask_size: row.top_ask_size, bid_depth_5: row.bid_depth_5, ask_depth_5: row.ask_depth_5, depth_ratio: row.depth_ratio }, quote_path: quote, pressure_state: pressure, combined_state: combined.state, disagreement: combined.disagreement, causal_discount_evidence: { running_trade_low_cents: leg.running_trade_low, running_qualifying_ask_low_cents: leg.running_qualified_ask_low }, pair_cap_cents: leg.pair_cap_cents, decision };
    leg.first_decision ||= detail; leg.last_decision = detail;
    if (decision.action === "PLACE_REST" || decision.action === "REPRICE_REST_DOWN") {
      if (decision.action === "REPRICE_REST_DOWN") leg.maker_reprices += 1;
      leg.acted = true; leg.active_order = { target_cents: decision.target_cents, action_ts: row.ts, action_receipt: row.receipt, action: decision.action, source_state: combined.state }; leg.first_action ||= detail;
      actionRows.push({ mode, kind: decision.action, event_id: event.event_id, leg_identity: leg.leg_identity, target_cents: decision.target_cents, receipt: row.receipt, state: combined.state, reason: decision.reason, ...clock(row.ts, leg.source, leg.bell, span.market_close_epoch) });
    } else if (decision.action === "TAKE") {
      leg.acted = true; leg.credited = true; leg.entry_cents = decision.target_cents; leg.action_timestamp_epoch = row.ts; leg.fill_timestamp_epoch = row.ts; leg.fill_class = "PROVEN_TAKER_R3_QUALIFIED_SETTLED_ASK"; leg.terminal_reason = leg.fill_class; leg.first_action ||= detail;
      actionRows.push({ mode, kind: "FILL", event_id: event.event_id, leg_identity: leg.leg_identity, fill_class: leg.fill_class, entry_cents: leg.entry_cents, receipt: row.receipt, displayed_ask: { price_cents: row.ask, size: row.top_ask_size, spread: row.spread, dwell_seconds: row.ask_dwell_seconds, crossed_or_locked: row.bid >= row.ask }, ...clock(row.ts, leg.source, leg.bell, span.market_close_epoch) });
      armSibling(sibling, leg, row, mode, actionRows, span.market_close_epoch);
    }
  }
  for (const leg of Object.values(event.legs)) {
    leg.entry_minus_market_life_close_cents = leg.credited && Number.isInteger(leg.own_market_life_close_cents) ? leg.entry_cents - leg.own_market_life_close_cents : null;
    leg.entry_minus_qualifying_ask_floor_cents = leg.credited && Number.isInteger(leg.own_full_life_qualifying_ask_floor_cents) ? leg.entry_cents - leg.own_full_life_qualifying_ask_floor_cents : null;
    leg.entry_minus_traded_low_cents = leg.credited && Number.isInteger(leg.own_market_life_traded_low_cents) ? leg.entry_cents - leg.own_market_life_traded_low_cents : null;
    if (!leg.credited) leg.terminal_reason = leg.acted ? "STANDING_REST_UNFILLED_AT_MARKET_CLOSE" : "OWN_TWO_SIDED_BOOK_NEVER_FORMED";
    leg.first_action_timestamp_epoch = leg.first_action?.timestamp_epoch ?? null;
    delete leg.source; delete leg.bell; delete leg.active_order; delete leg.prior_book; delete leg.latest_directional;
  }
  const legs = Object.values(event.legs); event.completed_pair = legs.every((x) => x.credited); event.combined_entry_cents = event.completed_pair ? legs.reduce((s, x) => s + x.entry_cents, 0) : null; event.pair_under_par = event.completed_pair && event.combined_entry_cents < 100; event.both_legs_strictly_below_market_life_close = event.completed_pair && legs.every((x) => Number.isInteger(x.own_market_life_close_cents) && x.entry_cents < x.own_market_life_close_cents); event.joint_objective_pass = event.pair_under_par && event.both_legs_strictly_below_market_life_close; event.execution_floor_pair_pass = event.pair_under_par && legs.every((x) => Number.isInteger(x.own_full_life_qualifying_ask_floor_cents) && x.entry_cents <= x.own_full_life_qualifying_ask_floor_cents);
  return event;
}

function metrics(events) {
  const legs = events.flatMap((e) => Object.values(e.legs)), completed = events.filter((e) => e.completed_pair), carried = completed.filter((e) => { const d = Object.values(e.legs).map((x) => x.entry_minus_market_life_close_cents); return d.some((x) => x > 0) && d.some((x) => x < 0); });
  return { D: events.length, legs: legs.length, acted_legs: legs.filter((x) => x.acted).length, credited_legs: legs.filter((x) => x.credited).length, proven_maker_legs: legs.filter((x) => x.fill_class?.startsWith("PROVEN_MAKER")).length, proven_taker_legs: legs.filter((x) => x.fill_class?.startsWith("PROVEN_TAKER")).length, census_priced_conversion_legs: legs.filter((x) => x.fill_class === "CENSUS_PRICED_ONE_CENT_RESIDENCY_CONVERSION").length, completed_pairs: completed.length, pairs_under_par: events.filter((e) => e.pair_under_par).length, both_legs_strictly_below_close: events.filter((e) => e.both_legs_strictly_below_market_life_close).length, joint_objective_pairs: events.filter((e) => e.joint_objective_pass).length, carried_pairs: carried.length, execution_floor_pair_passes: events.filter((e) => e.execution_floor_pair_pass).length, close_unavailable_legs: legs.filter((x) => !Number.isInteger(x.own_market_life_close_cents)).length };
}

function scoreColumn(events, label) {
  const aggregate = metrics(events), cells = [...group(events, (e) => `${e.category}|${e.starting_price_split}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, rows]) => ({ cell, metrics: metrics(rows) }));
  return { label, aggregate, delta_joint_vs_R3_68: aggregate.joint_objective_pairs - 68, gap_to_operator_bound_603: 603 - aggregate.joint_objective_pairs, category_x_starting_price_region: cells };
}

function frontier(events) {
  const tiers = [{ id: "LE_93", test: (x) => x <= 93 }, { id: "LE_95", test: (x) => x <= 95 }, { id: "LE_97", test: (x) => x <= 97 }, { id: "LT_100", test: (x) => x < 100 }, { id: "ANY_PRICE", test: () => true }];
  const make = (rows) => Object.fromEntries(tiers.map((tier) => [tier.id, { fixed_denominator: rows.length, completed_pairs: rows.filter((e) => e.completed_pair && tier.test(e.combined_entry_cents)).length, joint_objective_pairs: rows.filter((e) => e.joint_objective_pass && tier.test(e.combined_entry_cents)).length }]));
  return { fixed_denominator: events.length, cumulative_frontier: make(events), category_x_starting_price_region: [...group(events, (e) => `${e.category}|${e.starting_price_split}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, rows]) => ({ cell, frontier: make(rows) })) };
}

function regret(events) {
  const rows = events.flatMap((e) => Object.values(e.legs)).map((x) => ({ leg_identity: x.leg_identity, category: x.category, price_region: x.price_region, credited: x.credited, entry_cents: x.entry_cents, achievable_full_life_true_print_floor_cents: x.own_market_life_traded_low_cents, regret_cents: x.credited && Number.isInteger(x.own_market_life_traded_low_cents) ? x.entry_cents - x.own_market_life_traded_low_cents : null, loss_attribution: x.credited ? "CREDITED" : x.acted ? "RESTED_UNFILLED" : "NO_FORMED_OWN_BOOK" }));
  return { law: "regret=entry-minus-lowest-true-exchange-print-over-full-market-life; incomplete numeric regret remains null", aggregate: distribution(rows.map((x) => x.regret_cents), "cents"), loss_attribution: countBy(rows, (x) => x.loss_attribution), category_x_price_region: [...group(rows, (x) => `${x.category}|${x.price_region}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, x]) => ({ cell, regret: distribution(x.map((r) => r.regret_cents), "cents"), loss_attribution: countBy(x, (r) => r.loss_attribution) })), rows };
}

function compactTrace(events) {
  return events.flatMap((e) => Object.values(e.legs).map((x) => ({ mode: e.mode, event_id: e.event_id, leg_identity: x.leg_identity, ticker: x.ticker, category: x.category, price_region: x.price_region, decisions: x.decisions, state_counts: x.state_counts, action_counts: x.action_counts, disagreement_count: x.disagreement_count, maker_reprices: x.maker_reprices, first_decision: x.first_decision, last_decision: x.last_decision, first_action_timestamp_epoch: x.first_action_timestamp_epoch, fill_timestamp_epoch: x.fill_timestamp_epoch, entry_cents: x.entry_cents, fill_class: x.fill_class, terminal_reason: x.terminal_reason, final_state: x.credited ? (e.joint_objective_pass ? "JOINT_CAPTURED" : e.completed_pair ? "COMPLETED_NON_JOINT" : "NAKED") : x.acted ? "RESTING_UNFILLED" : "NO_FORMED_OWN_BOOK" }))).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity));
}

function diffVsR3(baseEvents, events, mode) {
  const by = new Map(events.map((e) => [e.event_id, e])), changed = [], unchanged = [];
  for (const baseEvent of baseEvents) for (const [id, old] of Object.entries(baseEvent.legs)) { const x = by.get(baseEvent.event_id).legs[id], before = old.R3, after = { acted: x.acted, credited: x.credited, entry_cents: x.entry_cents }; (semantic(before) === semantic(after) ? unchanged : changed).push(x.leg_identity); }
  return { mode, base: "V29_R3_JOINT_68", changed_leg_streams: changed.length, unchanged_leg_streams: unchanged.length, changed_leg_identities: changed, unchanged_semantic_hash: semantic(unchanged), conservation: changed.length + unchanged.length };
}

async function main() {
  ensure(!output.toLowerCase().includes("holdout"), "holdout forbidden");
  for (const c of [V34_PARENT, V32_COMMIT, R3_COMMIT, RECON_COMMIT, NEARMISS_COMMIT]) requireCommit(c);
  safeClean(output);
  const baseEvents = loadBaseEvents(); ensure(baseEvents.length === 804, "D must be 804");
  const sources = loadSources(), bells = new Map(JSON.parse(fs.readFileSync(bellFile)).leg_rows.map((x) => [x.event_id, x.exact_bell_ts])), tickers = new Set(baseEvents.flatMap((e) => Object.values(e.legs).map((x) => x.ticker))); ensure(tickers.size === 1608, "1608 legs required");
  process.stderr.write("V34_STAGE print_spool_start\n"); const printLoad = buildPrintSpool(tickers); process.stderr.write("V34_STAGE print_spool_complete\n");
  const tapeHashes = {}, strictEvents = [], censusEvents = [], spans = [], actionRows = [];
  for (const baseEvent of baseEvents) {
    const tapes = new Map(), prints = new Map();
    for (const leg of Object.values(baseEvent.legs)) prints.set(leg.ticker, printLoad.load(leg.ticker));
    for (const leg of Object.values(baseEvent.legs)) { const rawTape = loadFullTape(leg.ticker, tapeHashes); tapes.set(leg.ticker, condenseTape(rawTape, prints.get(leg.ticker))); }
    const printSets = [...prints.values()], tapeSets = [...tapes.values()], printCount = printSets.reduce((n, rows) => n + rows.length, 0);
    ensure(printCount > 0, `no event exchange activity ${baseEvent.event_id}`);
    const marketClose = printSets.reduce((latest, rows) => rows.length ? Math.max(latest, rows.at(-1).ts) : latest, -Infinity);
    const marketStart = [...printSets, ...tapeSets].reduce((earliest, rows) => rows.length ? Math.min(earliest, rows[0].ts) : earliest, Infinity);
    const source0 = sources.get(Object.values(baseEvent.legs)[0].ticker), bell = bells.get(baseEvent.event_id);
    const perLeg = Object.values(baseEvent.legs).map((leg) => { const t = tapes.get(leg.ticker), p = prints.get(leg.ticker), bs = t[0]?.ts ?? null, be = t.at(-1)?.ts ?? null, ps = p[0]?.ts ?? null, pe = p.at(-1)?.ts ?? null, overlapStart = Number.isFinite(bs) ? Math.max(marketStart, bs) : null, overlapEnd = Number.isFinite(be) ? Math.min(marketClose, be) : null, bookSeconds = Number.isFinite(overlapStart) && Number.isFinite(overlapEnd) ? Math.max(0, overlapEnd - overlapStart) : 0; return { leg_identity: leg.leg_identity, ticker: leg.ticker, first_two_sided_book_epoch: bs, last_two_sided_book_epoch: be, first_true_print_epoch: ps, final_true_print_epoch: pe, true_print_count: p.length, two_sided_book_receipt_count_raw: t.rawReceiptCount, two_sided_book_receipt_count_causal: t.length, causally_equivalent_receipts_collapsed: t.rawReceiptCount - t.length, book_coverage_seconds: bookSeconds, market_life_seconds: marketClose - marketStart, book_coverage_fraction: marketClose > marketStart ? bookSeconds / (marketClose - marketStart) : null, print_only_remainder_seconds: Number.isFinite(be) && marketClose > be ? marketClose - be : 0 }; });
    const span = { event_id: baseEvent.event_id, category: baseEvent.category, starting_price_split: baseEvent.starting_price_split, market_life_start_epoch: marketStart, market_close_epoch: marketClose, market_life_seconds: marketClose - marketStart, formation_clock: clock(marketStart, source0, bell, marketClose), close_clock: clock(marketClose, source0, bell, marketClose), actual_bell_role: Number.isFinite(bell) ? "TIMING_METADATA_ONLY_NEVER_BOUNDARY" : "NOT_AVAILABLE_NEVER_REQUIRED", per_leg: perLeg }; spans.push(span);
    const timeline = [];
    for (const [id, leg] of Object.entries(baseEvent.legs)) { for (const row of tapes.get(leg.ticker)) timeline.push({ ...row, leg_id: id }); for (const row of prints.get(leg.ticker)) timeline.push({ ...row, leg_id: id }); }
    timeline.sort((a, b) => a.ts - b.ts || (a.kind === "PRINT" ? 0 : 1) - (b.kind === "PRINT" ? 0 : 1) || a.ordinal - b.ordinal || a.leg_id.localeCompare(b.leg_id));
    strictEvents.push(simulateMode(baseEvent, tapes, prints, sources, bells, "STRICT_LAW", actionRows, span, timeline));
    censusEvents.push(simulateMode(baseEvent, tapes, prints, sources, bells, "CENSUS_PRICED", actionRows, span, timeline));
    if (strictEvents.length % 50 === 0) process.stderr.write(`V34_STAGE replay_events_${strictEvents.length}\n`);
  }
  printLoad.cleanup();
  const strictScore = scoreColumn(strictEvents, "STRICT_LAW"), censusScore = scoreColumn(censusEvents, "CENSUS_PRICED_ONE_CENT_RESIDENCY");
  const strictRegret = regret(strictEvents), censusRegret = regret(censusEvents), strictTrace = compactTrace(strictEvents), censusTrace = compactTrace(censusEvents);
  const reconBytes = gitShow(RECON_COMMIT, RECON_PATH), recon = JSON.parse(reconBytes), nearBytes = gitShow(NEARMISS_COMMIT, NEARMISS_PATH), near = JSON.parse(nearBytes), publicManifest = JSON.parse(fs.readFileSync(publicTapeManifest));
  ensure(recon.conservation.PRINTS_FAITHFUL === 804 && recon.conservation.DEFECT === 0, "938 reconciliation seal failed"); ensure(publicManifest.immutable_denominator.D === 804 && publicManifest.immutable_denominator.required_leg_tickers === 1608, "public tape manifest denominator failed"); ensure(printLoad.receipt.admitted_unique_full_market_life_prints === publicManifest.records.canonical_true_print_rows, "full-life print count failed");
  const strictArn = strictEvents.find((e) => e.event_id.includes("ARNROM")), censusArn = censusEvents.find((e) => e.event_id.includes("ARNROM"));
  const closeRows = strictEvents.flatMap((event) => Object.values(event.legs).map((leg) => ({ event_id: event.event_id, leg_identity: leg.leg_identity, status: leg.market_life_close_status, price_cents: leg.own_market_life_close_cents, timestamp_epoch: leg.own_market_life_close_timestamp_epoch })));
  const closePairs = strictEvents.map((event) => { const prices = Object.values(event.legs).map((leg) => leg.own_market_life_close_cents); return { event_id: event.event_id, both_available: prices.every(Number.isInteger), close_sum_cents: prices.every(Number.isInteger) ? prices[0] + prices[1] : null }; });
  const closeRuler = { law: "TRUE_CLOSE_IS_EACH_LEGS_FINAL_ORDERED_EXCHANGE_PRINT_OF_FULL_MARKET_LIFE", authoritative_within_second_ordering: "EXCHANGE_ARCHIVE_ORDINAL", legs: closeRows.length, available_legs: closeRows.filter((row) => Number.isInteger(row.price_cents)).length, unavailable_legs: closeRows.filter((row) => !Number.isInteger(row.price_cents)).length, close_price_counts: countBy(closeRows, (row) => row.price_cents ?? row.status), events: closePairs.length, both_closes_available_events: closePairs.filter((row) => row.both_available).length, close_sum_counts: countBy(closePairs, (row) => row.close_sum_cents ?? "UNAVAILABLE"), consequence: { strict_completed_pairs: strictScore.aggregate.completed_pairs, strict_both_below_close: strictScore.aggregate.both_legs_strictly_below_close, census_completed_pairs: censusScore.aggregate.completed_pairs, census_both_below_close: censusScore.aggregate.both_legs_strictly_below_close, explanation: "THE_FINAL_EXCHANGE_PRINTS_ARE_TERMINAL_1_OR_99_PRICES_FOR_THE_GREAT_MAJORITY_OF_LEGS; A_POSITIVE_CENT_ENTRY_CANNOT_BE_STRICTLY_BELOW_A_TERMINAL_1_CLOSE" } };
  const control = { schema_version: "window1-v34-control-v2-unblocked", construction_parent: V34_PARENT, architecture: "DUAL_SIDE_RESIDENCY_MACHINE_NOT_OVERLAY", window_law: { left: "EARLIER_OF_FIRST_TWO_SIDED_BOOK_OR_FIRST_TRUE_EXCHANGE_PRINT", right: "EVENT_FINAL_TRUE_EXCHANGE_PRINT_TIMESTAMP_FROM_MARKET_OWN_EXCHANGE_RECORD", close: "EACH_LEG_FINAL_TRUE_EXCHANGE_PRINT_AT_ITS_LATEST_TIMESTAMP", scheduled_edge_role: "NONE", actual_bell_role: "OPTIONAL_TIMING_METADATA_ONLY_NEVER_BOUNDARY", book_chain_after_end: "ACTIVE_REST_PERSISTS; PRINT_EVIDENCE_CONTINUES; NO_BOOK_DEPENDENT_TRANSITION_IS_FABRICATED" }, source_seal: { commit: RECON_COMMIT, receipt: RECON_PATH, scope_note: "938dca47 reconciled the guarded subset; the same sealed 4,836,462-row public archive supplies the full-life extension" }, comparisons: { R3_joint_floor: 68, operator_bound_CC_map_joint: 603, CC_event_map_status: "NOT_PRESENT_IN_FETCHED_GIT_REFS_AGGREGATE_603_BOUND_FROM_OPERATOR_ORDER" } };
  const machine = { schema_version: "window1-v34-dual-side-residency-v1", game_state: "ONE_GAME_STATE_TWO_ENTRY_OUTPUTS", standing_rest: { both_legs: true, starts: "FIRST_OWN_TWO_SIDED_BOOK", formula: "min(best_bid-1, prior_rest, running_true_trade_low_if_any, running_qualified_ask_low_if_any, 99-first_fill_if_armed)", falls: "WALK_DOWN", climbs: "HOLD_NEVER_CHASE_UP" }, state: { quote_path: { trailing_evidence_seconds: policy.LOOKBACK_SECONDS, falling: ["NEW_LOW_ASK", "SELLER_HIT_PRINT"], rising: ["NEW_HIGH_BID", "BUYER_LIFT_PRINT"], otherwise: "SETTLED" }, July6_pressure: { rising_at_or_above: policy.PRESSURE_RISING_MIN, falling_at_or_below: policy.PRESSURE_FALLING_MAX }, combination: "QUOTE_PATH_PRIMARY; PRESSURE_ONLY_WHEN_QUOTE_PATH_SETTLED; DISAGREEMENTS_LOGGED" }, take_path: "V29_R3_QUALIFIED_SETTLED_FLOOR; DWELL_10; ORDINARY_SPREAD_LE_1_AND_SIZE_GE_5; CROSSED_OR_LOCKED_MAXIMAL_URGENCY", fill_laws: { STRICT_LAW: "STRICTLY_LATER_SELLER_AGGRESSED_PRINT_SIZE_GE_5_AT_OR_BELOW_REST_OR_PROVEN_TAKER", CENSUS_PRICED: "STRICT_LAW_PLUS_SELLER_PRINT_EXACTLY_REST_PLUS_1_CONVERTED_AT_REST_PER_65d49b5d" }, pair_cap: "ON_FIRST_FILL_OTHER_LEG_CAP_99_MINUS_FILL_SAME_RECEIPT_CANNOT_FILL_REPRICE", clock_inputs: [] };
  const scored = { schema_version: "window1-v34-two-column-score-v1", STRICT_LAW: strictScore, CENSUS_PRICED: censusScore };
  const dispositions = { STRICT_LAW: countBy(strictTrace, (x) => `${x.fill_class || "UNFILLED"}|${x.terminal_reason}`), CENSUS_PRICED: countBy(censusTrace, (x) => `${x.fill_class || "UNFILLED"}|${x.terminal_reason}`) };
  const core = {
    "CONTROL_BINDING.json": canonical(control),
    "STATE_MACHINE_CONTRACT.json": canonical(machine),
    "FULL_MARKET_LIFE_SPAN_804.json": canonical({ events: spans.length, exact_market_close_boundaries: spans.filter((x) => Number.isFinite(x.market_close_epoch)).length, actual_bell_metadata_available_events: spans.filter((x) => x.actual_bell_role === "TIMING_METADATA_ONLY_NEVER_BOUNDARY").length, book_coverage_fraction: distribution(spans.map((x) => x.per_leg.reduce((s, l) => s + (l.book_coverage_fraction || 0), 0) / 2)), print_only_remainder_seconds: distribution(spans.flatMap((x) => x.per_leg.map((l) => l.print_only_remainder_seconds)), "seconds"), rows: spans }),
    "CLOSE_RULER_CONSEQUENCE_RECEIPT.json": canonical(closeRuler),
    "SCORECARD_TWO_COLUMN.json": canonical(scored),
    "STRICT_FRONTIER.json": canonical(frontier(strictEvents)),
    "CENSUS_PRICED_FRONTIER.json": canonical(frontier(censusEvents)),
    "STRICT_REGRET_GAUGE.json": canonical({ ...strictRegret, rows: undefined }),
    "CENSUS_PRICED_REGRET_GAUGE.json": canonical({ ...censusRegret, rows: undefined }),
    "STRICT_REGRET_LEDGER.jsonl.gz": gzipRows(strictRegret.rows),
    "CENSUS_PRICED_REGRET_LEDGER.jsonl.gz": gzipRows(censusRegret.rows),
    "STRICT_EVENT_LEDGER.jsonl.gz": gzipRows(strictEvents),
    "CENSUS_PRICED_EVENT_LEDGER.jsonl.gz": gzipRows(censusEvents),
    "STRICT_DECISION_TRACE_1608.json": canonical({ rows: strictTrace, conservation: strictTrace.length }),
    "CENSUS_PRICED_DECISION_TRACE_1608.json": canonical({ rows: censusTrace, conservation: censusTrace.length }),
    "ACTION_AND_FILL_TRACE.jsonl.gz": gzipRows(actionRows),
    "ENTRY_PATH_DISPOSITION.json": canonical(dispositions),
    "DIFFERENTIAL_VS_R3.json": canonical({ STRICT_LAW: diffVsR3(baseEvents, strictEvents, "STRICT_LAW"), CENSUS_PRICED: diffVsR3(baseEvents, censusEvents, "CENSUS_PRICED") }),
    "ARNROM_REGRESSION_RECEIPT.json": canonical({ STRICT_LAW: strictArn, CENSUS_PRICED: censusArn }),
    "CENSUS_PRICED_65D49B5D_BINDING.json": canonical({ commit: NEARMISS_COMMIT, path: NEARMISS_PATH, source_sha256: sha(nearBytes), source: { waited_and_lost: near.summary.conservation.waited_and_lost_censused, one_cent_near_miss_rests: near.summary.totals.with1, v32_joint: near.summary.conservation.V32_executable_joint, model_free_ceiling: near.summary.conservation.model_free_ceiling_joint }, V34_application: "DYNAMIC_ACTIVE_V34_REST_TRAJECTORY; FIRST_LAWFUL_ONE_CENT_SELLER_PRINT_CONVERTS_AT_REST_IN_CENSUS_COLUMN" }),
    "UNBLOCK_SUPERSESSION_RECEIPT.json": canonical({ supersedes_commit: "4450de974d855605f51816049bcc5b693502c6d4", prior_block: "EXACT_EXTERNAL_ACTUAL_BELL_REQUIRED", corrected_law: "MARKET_OWN_FINAL_EXCHANGE_ACTIVITY_BOUNDARY", external_actual_bell_required: false, actual_bell_timing_metadata_only: true, scheduled_edge_used: false }),
    "FORBIDDEN_ACCESS_RECEIPT.json": canonical({ holdout_accesses: 0, live_accesses: 0, network_runtime_accesses: 0, order_accesses: 0, position_accesses: 0, settlement_accesses: 0, deployment_accesses: 0, scorer_external_invocations: 0, private_scope: "FIT_DEVELOPMENT_804_ONLY" }),
    "SOURCE_HASH_MANIFEST.json": canonical({ public_committed: Object.fromEntries([builderFile, policyFile, unitTestFile, packageTestFile, floorFile, baseTraceFile, quoteFile, bellFile, spoolHelperFile, spoolHelperSourceFile].map((file) => [path.relative(repo, file).replaceAll("\\", "/"), { sha256: fs.existsSync(file) ? fileHash(file) : null, bytes: fs.existsSync(file) ? fs.statSync(file).size : null }])), git_bound: { [RECON_PATH]: { commit: RECON_COMMIT, sha256: sha(reconBytes), bytes: reconBytes.length }, [NEARMISS_PATH]: { commit: NEARMISS_COMMIT, sha256: sha(nearBytes), bytes: nearBytes.length } }, private_full_life_prints: printLoad.receipt, private_full_life_books: tapeHashes, public_tape_manifest: { sha256: fileHash(publicTapeManifest), bytes: fs.statSync(publicTapeManifest).size } }),
  };
  for (const [name, bytes] of Object.entries(core)) write(name, bytes);
  write("REPORT.md", `# V34 dual-side residency machine - full market life\n\nV34 is a new game-level architecture with both entries as outputs. It runs from the earlier of the first two-sided book or first true exchange print through the event's final ordered exchange print. Scheduled edges are not boundaries. The 234-event exact-bell subset is timing metadata only.\n\n- STRICT-LAW JOINT: ${strictScore.aggregate.joint_objective_pairs}; delta vs R3 68: ${strictScore.delta_joint_vs_R3_68}; gap to operator-bound 603: ${strictScore.gap_to_operator_bound_603}.\n- CENSUS-PRICED JOINT: ${censusScore.aggregate.joint_objective_pairs}; delta vs R3 68: ${censusScore.delta_joint_vs_R3_68}; gap to operator-bound 603: ${censusScore.gap_to_operator_bound_603}.\n- STRICT completed / under par / carried: ${strictScore.aggregate.completed_pairs} / ${strictScore.aggregate.pairs_under_par} / ${strictScore.aggregate.carried_pairs}.\n- CENSUS completed / under par / carried: ${censusScore.aggregate.completed_pairs} / ${censusScore.aggregate.pairs_under_par} / ${censusScore.aggregate.carried_pairs}.\n- ARNROM STRICT: ${strictArn?.combined_entry_cents ?? "INCOMPLETE"}; CENSUS: ${censusArn?.combined_entry_cents ?? "INCOMPLETE"}.\n- Ordered close availability: ${closeRuler.available_legs}/${closeRuler.legs}; close-price counts are frozen in CLOSE_RULER_CONSEQUENCE_RECEIPT.json.\n\nThe restated final-exchange-print close is terminal 1/99 pricing for the great majority of legs, so neither column can satisfy both-legs-below-close. This is a ruler consequence, not a hidden replay exclusion. The CC per-event 603 map is not present in fetched Git refs. The operator-bound aggregate 603 comparison is reported; no event identities were fabricated.\n`);
  const compareNames = [...Object.keys(core), "REPORT.md"].sort();
  if (compare) { const mismatches = compareNames.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name))); ensure(!mismatches.length, `determinism mismatch ${mismatches.join(",")}`); write("DETERMINISM_RECEIPT.json", canonical({ builds: 2, byte_identical: true, compared_files: compareNames.length, mismatches: [] })); }
  else write("DETERMINISM_RECEIPT.json", canonical({ builds: 1, byte_identical: null, role: "FIRST_BUILD" }));
  const names = fs.readdirSync(output).filter((x) => x !== "ARTIFACT_HASH_MANIFEST.json").sort(); write("ARTIFACT_HASH_MANIFEST.json", canonical({ files: Object.fromEntries(names.map((name) => [name, { sha256: fileHash(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size }])) }));
  process.stdout.write(canonical({ output, STRICT_LAW: strictScore.aggregate, CENSUS_PRICED: censusScore.aggregate, spans: spans.length, action_rows: actionRows.length }));
}

main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
