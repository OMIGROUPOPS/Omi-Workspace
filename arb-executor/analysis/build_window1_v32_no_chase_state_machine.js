#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const child = require("child_process");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");
const policy = require("./window1_v32_no_chase_state_machine.js");

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const repo = path.resolve(arg("--repo", "."));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const output = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/v32_no_chase_state_machine_20260805")));
const compare = arg("--compare", null);
const base = path.join(repo, ".claude/window1_live_v4_replay/v29r3_standing_floor_release_20260805");
const specCommit = "6f2c3f822b85cb4e4a22001cdfe14ef2af8384fc";
const specDoc = "arb-executor/docs/research/window1/second_seat/NOCHASE_CEILING_MODELFREE.md";
const specJson = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/NOCHASE_CEILING_MODELFREE.json";
const quoteFile = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const bellFile = path.join(repo, ".claude/window1_live_v4_replay/actual_bell_refit_20260729/ACTUAL_BELL_REFIT.json");
const floorFile = path.join(repo, ".claude/window1_live_v4_replay/trade_floor_correction_v8_20260802/DUAL_FLOOR_LEG_LEDGER.jsonl.gz");
const baseTraceFile = path.join(base, "DECISION_TRACE_1608.json");
const policyFile = path.join(repo, "arb-executor/analysis/window1_v32_no_chase_state_machine.js");
const builderFile = __filename;
const unitTestFile = path.join(repo, "arb-executor/tests/test_window1_v32_no_chase_state_machine.js");
const packageTestFile = path.join(repo, "arb-executor/tests/test_window1_v32_no_chase_state_machine_package.js");
const spoolHelperFile = path.join(repo, "arb-executor/analysis/window1_v32_print_spool.ps1");
const spoolHelperSourceFile = path.join(repo, "arb-executor/analysis/window1_v32_print_spool.cs");

function ensure(value, message) { if (!value) throw new Error(message); }
function sha(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function fileHash(file) { return sha(fs.readFileSync(file)); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function write(name, bytes) { const file = path.join(output, name); fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, bytes); }
function readRows(file) { const text = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse) : []; }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
function semantic(value) { return sha(JSON.stringify(value)); }
function integer(value) { const number = Number(value); return Number.isInteger(number) ? number : null; }
function positive(value) { const number = Number(value); return Number.isFinite(number) && number > 0 ? number : null; }
function quantile(values, p) { const sorted = values.filter(Number.isFinite).sort((a, b) => a - b); return sorted.length ? sorted[Math.floor((sorted.length - 1) * p)] : null; }
function distribution(values) { const x = values.filter(Number.isFinite); return { denominator: values.length, numeric_n: x.length, null_n: values.length - x.length, min: x.length ? Math.min(...x) : null, p25: quantile(x, .25), median: quantile(x, .5), p75: quantile(x, .75), p90: quantile(x, .9), max: x.length ? Math.max(...x) : null, total_cents: x.reduce((a, b) => a + b, 0) }; }
function parseCsv(text) { const lines = text.trimEnd().split(/\r?\n/); const h = lines.shift().split(","); return lines.filter(Boolean).map((line) => Object.fromEntries(line.split(",").map((v, i) => [h[i], v]))); }
function parseEt(value) { const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/); if (!m) return null; let h = +m[4]; if (m[7] === "AM" && h === 12) h = 0; if (m[7] === "PM" && h !== 12) h += 12; return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(h).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000; }
function group(rows, fn) { const out = new Map(); for (const row of rows) { const key = fn(row); if (!out.has(key)) out.set(key, []); out.get(key).push(row); } return out; }
function countBy(rows, fn) { const out = {}; for (const row of rows) { const key = String(fn(row)); out[key] = (out[key] || 0) + 1; } return Object.fromEntries(Object.entries(out).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function clocks(ts, source, bell) { return { timestamp_epoch: ts, t_minus_scheduled_seconds: source.scheduled - ts, t_minus_actual_bell_seconds: Number.isFinite(bell) ? bell - ts : null }; }

async function readSlimBaseEvents(file) {
  const input = readline.createInterface({ input: fs.createReadStream(file).pipe(zlib.createGunzip()), crlfDelay: Infinity }); const events = [];
  for await (const line of input) {
    if (!line) continue; const row = JSON.parse(line); const legs = {};
    for (const [id, leg] of Object.entries(row.legs)) legs[id] = { leg_identity: leg.leg_identity, event_id: leg.event_id, category: leg.category, starting_price_split: leg.starting_price_split, price_region: leg.price_region, leg_id: leg.leg_id, ticker: leg.ticker, qualifying_ask_floor_cents: leg.qualifying_ask_floor_cents, objective_traded_low_cents: leg.objective_traded_low_cents, own_window1_close_cents: leg.own_window1_close_cents, close_status: leg.close_status, acted: leg.acted, credited: leg.credited, entry_cents: leg.entry_cents };
    events.push({ event_id: row.event_id, category: row.category, starting_price_split: row.starting_price_split, legs }); if (global.gc && events.length % 50 === 0) global.gc();
  }
  return events;
}

function loadCompactBaseEvents() {
  const floors = readRows(floorFile); const traceRows = JSON.parse(fs.readFileSync(baseTraceFile)).rows; ensure(floors.length === 1608 && traceRows.length === 1608, "compact base leg conservation failed"); const traceBy = new Map(traceRows.map((row) => [row.leg_identity, row])); const byEvent = new Map();
  for (const floor of floors) {
    const prior = traceBy.get(floor.leg_identity); ensure(prior, `missing R3 trace ${floor.leg_identity}`); const state = prior.leg_action_state; const leg = { leg_identity: floor.leg_identity, event_id: floor.event_id, category: floor.category, starting_price_split: prior.starting_price_split, price_region: floor.price_region, leg_id: floor.leg_id, ticker: floor.ticker, qualifying_ask_floor_cents: floor.ask_capacity_floor_cents, objective_traded_low_cents: floor.lowest_traded_price_cents, own_window1_close_cents: floor.own_window1_close_cents, close_status: Number.isInteger(floor.own_window1_close_cents) ? (floor.v7_close_binding_defect || "AVAILABLE") : "UNAVAILABLE", acted: state.acted, credited: state.credited, entry_cents: state.entry_cents };
    if (!byEvent.has(floor.event_id)) byEvent.set(floor.event_id, { event_id: floor.event_id, category: floor.category, starting_price_split: prior.starting_price_split, legs: {} }); byEvent.get(floor.event_id).legs[floor.leg_id] = leg;
  }
  return [...byEvent.values()].sort((a, b) => a.event_id.localeCompare(b.event_id));
}

function createTraceCollector(file) {
  const gzip = zlib.createGzip({ level: 9, mtime: 0 }); const stream = fs.createWriteStream(file); gzip.pipe(stream);
  const perLeg = new Map(), byCategory = new Map(); let total = 0, decisions = 0, disagreements = 0;
  function summary(legIdentity) { if (!perLeg.has(legIdentity)) perLeg.set(legIdentity, { decisions: 0, state_counts: {}, action_counts: {}, disagreements: 0, first: null, last: null, fill: null }); return perLeg.get(legIdentity); }
  return {
    push(row) {
      gzip.write(`${JSON.stringify(row)}\n`); total += 1; if (!row.leg_identity) return; const s = summary(row.leg_identity);
      if (row.kind === "DECISION") { decisions += 1; s.decisions += 1; s.state_counts[row.combined_state] = (s.state_counts[row.combined_state] || 0) + 1; s.action_counts[row.decision.action] = (s.action_counts[row.decision.action] || 0) + 1; if (!s.first) s.first = row; s.last = row; if (row.disagreement) { disagreements += 1; s.disagreements += 1; } const c = byCategory.get(row.category) || { receipts: 0, disagreements: 0 }; c.receipts += 1; if (row.disagreement) c.disagreements += 1; byCategory.set(row.category, c); }
      if (row.kind === "FILL") s.fill = row;
    },
    async end() { gzip.end(); await new Promise((resolve, reject) => { stream.on("finish", resolve); stream.on("error", reject); gzip.on("error", reject); }); },
    total: () => total, decisions: () => decisions, disagreements: () => disagreements, perLeg, byCategory,
  };
}

function loadSources() {
  const map = new Map();
  for (const row of parseCsv(fs.readFileSync(quoteFile, "utf8"))) map.set(row.ticker, { event_id: row.event_id, ticker: row.ticker, left: +row.left_ts, right: +row.right_ts, scheduled: +row.scheduled_start_ts });
  return map;
}

function loadTape(ticker, source, hashes) {
  const file = path.join(privateRoot, "fit-local/ticks", `${ticker}.csv.gz`);
  ensure(fs.existsSync(file), `missing development tape ${ticker}`);
  const bytes = fs.readFileSync(file); hashes[ticker] = { sha256: sha(bytes), bytes: bytes.length };
  const lines = zlib.gunzipSync(bytes).toString("utf8").trimEnd().split(/\r?\n/); const header = lines.shift().split(","); const ix = Object.fromEntries(header.map((v, i) => [v, i]));
  const out = [];
  for (let n = 0; n < lines.length; n += 1) {
    const v = lines[n].split(","); const ts = parseEt(v[ix.ts_et]); if (ts === null || ts < source.left || ts > source.right) continue;
    const bids = [], asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bp = integer(v[ix[`bid_${level}`]]), bs = positive(v[ix[`bid_${level}_sz`]]), ap = integer(v[ix[`ask_${level}`]]), as = positive(v[ix[`ask_${level}_sz`]]);
      if (bp !== null && bs !== null) bids.push([bp, bs]); if (ap !== null && as !== null) asks.push([ap, as]);
    }
    if (!bids.length || !asks.length) continue; bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]);
    out.push({ kind: "BOOK", ticker, ts, ordinal: n + 2, receipt: `${ticker}.csv.gz#row-${n + 2}`, bid: bids[0][0], ask: asks[0][0], spread: asks[0][0] - bids[0][0], top_bid_size: bids[0][1], top_ask_size: asks[0][1], bid_depth_5: bids.reduce((s, x) => s + x[1], 0), ask_depth_5: asks.reduce((s, x) => s + x[1], 0), last_trade: integer(v[ix.last_trade]) });
  }
  out.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  let ask = null, since = null;
  for (const row of out) { if (row.ask !== ask) { ask = row.ask; since = row.ts; } row.ask_dwell_seconds = row.ts - since; row.depth_ratio = row.bid_depth_5 / (row.bid_depth_5 + row.ask_depth_5); }
  return out;
}

async function loadPrints(tickers, sources) {
  const file = path.join(privateRoot, "fit-local/prints.jsonl"); ensure(fs.existsSync(file), "missing development prints");
  const spool = path.join(output, ".print-spool"); fs.mkdirSync(spool, { recursive: true });
  const hash = crypto.createHash("sha256"); let carry = "", rows = 0, admitted = 0, duplicates = 0, currentTicker = null, currentSelected = false, currentBuffer = [], seen = new Set(); const closed = new Set();
  const spoolFile = (ticker) => path.join(spool, `${ticker}.jsonl`);
  const flushBuffer = () => { if (currentSelected && currentBuffer.length) { fs.appendFileSync(spoolFile(currentTicker), `${currentBuffer.join("\n")}\n`); currentBuffer = []; } };
  const finishTicker = () => { if (currentTicker !== null && currentSelected) { flushBuffer(); closed.add(currentTicker); } currentBuffer = []; seen = new Set(); };
  const startTicker = (ticker) => { currentTicker = ticker; currentSelected = tickers.has(ticker); if (currentSelected) { ensure(!closed.has(ticker), `non-contiguous print ticker ${ticker}`); fs.writeFileSync(spoolFile(ticker), ""); } };
  const admit = (row) => {
    if (row.ticker !== currentTicker) { finishTicker(); startTicker(row.ticker); }
    if (!tickers.has(row.ticker) || row.true_print !== true) return;
    const source = sources.get(row.ticker); const ts = Date.parse(row.exchange_ts) / 1000; if (!Number.isFinite(ts) || ts < source.left || ts > source.right) return;
    const identity = row.trade_id; if (seen.has(identity)) { duplicates += 1; return; } seen.add(identity); admitted += 1;
    currentBuffer.push(JSON.stringify([ts, admitted, row.receipt_id, integer(row.price_cents), +row.size, row.taker_side, row.trade_id])); if (currentBuffer.length >= 10000) flushBuffer();
  };
  for await (const chunk of fs.createReadStream(file)) {
    hash.update(chunk); const pieces = (carry + chunk.toString("utf8")).split(/\r?\n/); carry = pieces.pop();
    for (const line of pieces) { if (!line) continue; rows += 1; admit(JSON.parse(line)); }
  }
  if (carry.trim()) { rows += 1; admit(JSON.parse(carry)); } finishTicker();
  return {
    load(ticker) { const target = spoolFile(ticker); if (!fs.existsSync(target)) return []; const text = fs.readFileSync(target, "utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse).map(([ts, ordinal, receipt, price, size, taker_side, trade_id]) => ({ kind: "PRINT", ticker, ts, ordinal, receipt, price, size, taker_side, trade_id })) : []; },
    cleanup() { const resolved = path.resolve(spool); ensure(resolved.startsWith(`${path.resolve(output)}${path.sep}`), "unsafe spool cleanup target"); fs.rmSync(resolved, { recursive: true, force: true }); },
    receipt: { path_class: "PRIVATE_FIT_DEVELOPMENT_PRINTS_HASH_ONLY", sha256: hash.digest("hex"), bytes: fs.statSync(file).size, raw_rows: rows, admitted_unique_window1_prints: admitted, duplicate_trade_id_rows_rejected: duplicates, contiguous_ticker_spool_count: closed.size },
  };
}

function buildPrintSpool(tickers, sources) {
  const spool = path.join(output, ".print-spool"), sourceContract = path.join(output, ".print-spool-sources.csv"), receiptFile = path.join(output, ".print-spool-receipt.json");
  const resolved = path.resolve(spool); ensure(resolved.startsWith(`${path.resolve(output)}${path.sep}`), "unsafe spool target"); if (fs.existsSync(resolved)) fs.rmSync(resolved, { recursive: true, force: true });
  fs.mkdirSync(resolved, { recursive: true }); const contract = ["ticker,left,right"]; for (const ticker of [...tickers].sort()) { const source = sources.get(ticker); contract.push(`${ticker},${source.left},${source.right}`); } fs.writeFileSync(sourceContract, `${contract.join("\n")}\n`);
  child.execFileSync("powershell.exe", ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", spoolHelperFile, "-Prints", path.join(privateRoot, "fit-local/prints.jsonl"), "-Sources", sourceContract, "-Spool", spool, "-Receipt", receiptFile, "-SourceCode", spoolHelperSourceFile], { cwd: repo, stdio: "inherit" });
  fs.rmSync(sourceContract); const receipt = JSON.parse(fs.readFileSync(receiptFile)); fs.rmSync(receiptFile);
  const spoolFile = (ticker) => path.join(spool, `${ticker}.jsonl`);
  return {
    load(ticker) { const target = spoolFile(ticker); if (!fs.existsSync(target)) return []; const text = fs.readFileSync(target, "utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse).map(([ts, ordinal, receiptId, price, size, taker_side, trade_id]) => ({ kind: "PRINT", ticker, ts, ordinal, receipt: receiptId, price, size, taker_side, trade_id })) : []; },
    cleanup() { const target = path.resolve(spool); ensure(target.startsWith(`${path.resolve(output)}${path.sep}`), "unsafe spool cleanup target"); fs.rmSync(target, { recursive: true, force: true }); },
    receipt,
  };
}

function stateRow(leg, row, state, quote, pressure, decision, source, bell) {
  return { leg_identity: leg.leg_identity, event_id: leg.event_id, leg_id: leg.leg_id, ticker: leg.ticker, category: leg.category, price_region: leg.price_region, ...clocks(row.ts, source, bell), receipt: row.receipt, observation: { bid: row.bid, ask: row.ask, last_traded: row.last_trade, spread: row.spread, ask_dwell_seconds: row.ask_dwell_seconds, top_ask_size: row.top_ask_size, bid_depth_5: row.bid_depth_5, ask_depth_5: row.ask_depth_5, depth_ratio: row.depth_ratio }, quote_path: quote, pressure_state: pressure, combined_state: state.state, authority: state.authority, disagreement: state.disagreement, decision };
}

function simulateEvent(baseEvent, tapes, prints, sources, bells, trace) {
  const event = { event_id: baseEvent.event_id, category: baseEvent.category, starting_price_split: baseEvent.starting_price_split, legs: {} };
  const ids = Object.keys(baseEvent.legs).sort();
  for (const id of ids) {
    const b = baseEvent.legs[id]; event.legs[id] = { leg_identity: b.leg_identity, event_id: b.event_id, category: b.category, starting_price_split: b.starting_price_split, price_region: b.price_region, leg_id: b.leg_id, ticker: b.ticker, qualifying_ask_floor_cents: b.qualifying_ask_floor_cents, objective_traded_low_cents: b.objective_traded_low_cents, own_window1_close_cents: b.own_window1_close_cents, close_status: b.close_status, acted: false, credited: false, entry_cents: null, honest_fill_class: null, action_timestamp_epoch: null, fill_timestamp_epoch: null, terminal_reason: null, pair_cap_cents: null, active_order: null, quote_evidence: [], decisions: 0, state_counts: { FALLING: 0, RISING: 0, SETTLED: 0 }, disagreement_count: 0, maker_reprices: 0, first_decision: null, last_decision: null, first_action: null };
  }
  const timeline = [];
  for (const id of ids) { const ticker = event.legs[id].ticker; for (const row of tapes.get(ticker)) timeline.push({ ...row, leg_id: id }); for (const row of prints.get(ticker)) timeline.push({ ...row, leg_id: id }); }
  timeline.sort((a, b) => a.ts - b.ts || (a.kind === "PRINT" ? 0 : 1) - (b.kind === "PRINT" ? 0 : 1) || a.ordinal - b.ordinal || a.leg_id.localeCompare(b.leg_id));
  for (const row of timeline) {
    const leg = event.legs[row.leg_id]; if (leg.credited) continue; const sibling = event.legs[ids.find((id) => id !== row.leg_id)]; const source = sources.get(leg.ticker); const bell = bells.get(event.event_id);
    if (row.kind === "PRINT") {
      if (policy.sellerPrintFills(leg.active_order, row)) {
        leg.credited = true; leg.entry_cents = leg.active_order.target_cents; leg.action_timestamp_epoch = leg.active_order.action_ts; leg.fill_timestamp_epoch = row.ts; leg.honest_fill_class = "PROVEN_MAKER_SELLER_AGGRESSED_PRINT_AT_OR_BELOW_RESTING_LIMIT"; leg.terminal_reason = "STRICTLY_LATER_SELLER_AGGRESSED_PRINT_AT_OR_BELOW_RESTING_LIMIT";
        trace.push({ kind: "FILL", leg_identity: leg.leg_identity, ...clocks(row.ts, source, bell), receipt: row.receipt, print: { price_cents: row.price, size: row.size, taker_side: row.taker_side }, resting_order: leg.active_order, credited_price_cents: leg.entry_cents });
        sibling.pair_cap_cents = 99 - leg.entry_cents;
        if (sibling.active_order && sibling.active_order.target_cents > sibling.pair_cap_cents) { sibling.active_order = { target_cents: sibling.pair_cap_cents, action_ts: row.ts, action_receipt: row.receipt, action: "PAIR_CAP_REPRICE", source_state: "SIBLING_FILL" }; trace.push({ kind: "PAIR_ARM", leg_identity: sibling.leg_identity, sibling_fill_cents: leg.entry_cents, pair_cap_cents: sibling.pair_cap_cents, ...clocks(row.ts, sources.get(sibling.ticker), bell), receipt: row.receipt, same_receipt_fill_forbidden: true }); }
      }
      if (!leg.credited && (row.taker_side === "no" || row.taker_side === "yes")) leg.quote_evidence.push({ ts: row.ts, ordinal: row.ordinal, direction: row.taker_side === "no" ? "FALLING" : "RISING", kind: row.taker_side === "no" ? "SELLER_HIT_PRINT" : "BUYER_LIFT_PRINT", receipt: row.receipt });
      continue;
    }
    const prior = leg.prior_book;
    const newLowAsk = prior && row.ask < prior.ask, newHighBid = prior && row.bid > prior.bid;
    if (newLowAsk && newHighBid) leg.quote_evidence.push({ ts: row.ts, ordinal: row.ordinal, direction: "SETTLED", kind: "QUOTE_PATH_INTERNAL_CONFLICT_NEW_LOW_ASK_AND_NEW_HIGH_BID", receipt: row.receipt });
    else if (newLowAsk) leg.quote_evidence.push({ ts: row.ts, ordinal: row.ordinal, direction: "FALLING", kind: "NEW_LOW_ASK", receipt: row.receipt });
    else if (newHighBid) leg.quote_evidence.push({ ts: row.ts, ordinal: row.ordinal, direction: "RISING", kind: "NEW_HIGH_BID", receipt: row.receipt });
    const quote = policy.quotePathState(leg.quote_evidence, row.ts); const pressure = policy.pressureState(row.depth_ratio); const combined = policy.combineState(quote, pressure); const decision = policy.decide({ state: combined.state, book: row, activeTarget: leg.active_order?.target_cents ?? null, pairCap: leg.pair_cap_cents });
    leg.prior_book = row;
    leg.decisions += 1; leg.state_counts[combined.state] += 1; if (combined.disagreement) leg.disagreement_count += 1;
    const detail = stateRow(leg, row, combined, quote, pressure, decision, source, bell); trace.push({ kind: "DECISION", ...detail }); if (!leg.first_decision) leg.first_decision = detail; leg.last_decision = detail;
    if (decision.action === "PLACE" || decision.action === "REPRICE") {
      if (decision.action === "REPRICE") leg.maker_reprices += 1; leg.acted = true; leg.active_order = { target_cents: decision.target_cents, action_ts: row.ts, action_receipt: row.receipt, action: decision.action, source_state: combined.state }; leg.first_action ??= detail;
    } else if (decision.action === "TAKE") {
      leg.acted = true; leg.credited = true; leg.action_timestamp_epoch = row.ts; leg.fill_timestamp_epoch = row.ts; leg.entry_cents = decision.target_cents; leg.honest_fill_class = "PROVEN_TAKER_DISPLAYED_ASK_SIZE_AT_SUBMISSION"; leg.terminal_reason = "SETTLED_QUALIFIED_STANDING_ASK_TAKEN"; leg.first_action ??= detail;
      trace.push({ kind: "FILL", leg_identity: leg.leg_identity, ...clocks(row.ts, source, bell), receipt: row.receipt, displayed_ask: { price_cents: row.ask, size: row.top_ask_size, spread: row.spread, dwell_seconds: row.ask_dwell_seconds }, credited_price_cents: leg.entry_cents });
      sibling.pair_cap_cents = 99 - leg.entry_cents;
      if (sibling.active_order && sibling.active_order.target_cents > sibling.pair_cap_cents) { sibling.active_order = { target_cents: sibling.pair_cap_cents, action_ts: row.ts, action_receipt: row.receipt, action: "PAIR_CAP_REPRICE", source_state: "SIBLING_FILL" }; trace.push({ kind: "PAIR_ARM", leg_identity: sibling.leg_identity, sibling_fill_cents: leg.entry_cents, pair_cap_cents: sibling.pair_cap_cents, ...clocks(row.ts, sources.get(sibling.ticker), bell), receipt: row.receipt, same_receipt_fill_forbidden: true }); }
    }
  }
  for (const leg of Object.values(event.legs)) {
    leg.entry_minus_qualifying_ask_floor_cents = leg.credited && Number.isInteger(leg.qualifying_ask_floor_cents) ? leg.entry_cents - leg.qualifying_ask_floor_cents : null;
    leg.entry_minus_objective_traded_low_cents = leg.credited && Number.isInteger(leg.objective_traded_low_cents) ? leg.entry_cents - leg.objective_traded_low_cents : null;
    leg.entry_minus_own_window1_close_cents = leg.credited && Number.isInteger(leg.own_window1_close_cents) ? leg.entry_cents - leg.own_window1_close_cents : null;
    if (!leg.credited) leg.terminal_reason = leg.acted ? "RESTING_ORDER_NEVER_RECEIVED_LATER_SELLER_AGGRESSED_PRINT" : "NO_EXECUTABLE_ACTION_BEFORE_GUARDED_RIGHT_EDGE";
    leg.first_action_timestamp_epoch = leg.first_action?.timestamp_epoch ?? null;
    delete leg.quote_evidence; delete leg.active_order; delete leg.prior_book;
  }
  const legs = Object.values(event.legs); event.completed_pair = legs.every((x) => x.credited); event.combined_entry_cents = event.completed_pair ? legs.reduce((s, x) => s + x.entry_cents, 0) : null; event.pair_under_par = event.completed_pair && event.combined_entry_cents < 100; event.both_legs_strictly_below_audited_close = event.completed_pair && legs.every((x) => Number.isInteger(x.own_window1_close_cents) && x.entry_cents < x.own_window1_close_cents); event.joint_objective_pass_audited_close = event.pair_under_par && event.both_legs_strictly_below_audited_close; event.execution_floor_pair_pass = event.pair_under_par && legs.every((x) => Number.isInteger(x.qualifying_ask_floor_cents) && x.entry_cents <= x.qualifying_ask_floor_cents);
  return event;
}

function metrics(events) {
  const legs = events.flatMap((e) => Object.values(e.legs)); const completed = events.filter((e) => e.completed_pair); const carried = completed.filter((e) => { const d = Object.values(e.legs).map((x) => x.entry_minus_own_window1_close_cents); return d.some((x) => x > 0) && d.some((x) => x < 0); });
  return { D: events.length, legs: legs.length, acted_legs: legs.filter((x) => x.acted).length, credited_legs: legs.filter((x) => x.credited).length, proven_maker_legs: legs.filter((x) => x.honest_fill_class?.startsWith("PROVEN_MAKER")).length, proven_taker_legs: legs.filter((x) => x.honest_fill_class?.startsWith("PROVEN_TAKER")).length, completed_pairs: completed.length, pairs_under_par: events.filter((e) => e.pair_under_par).length, both_legs_strictly_below_audited_close: events.filter((e) => e.both_legs_strictly_below_audited_close).length, joint_objective_pairs: events.filter((e) => e.joint_objective_pass_audited_close).length, strict_carried_pairs: carried.length, execution_floor_pair_passes: events.filter((e) => e.execution_floor_pair_pass).length };
}

function score(events) {
  const aggregate = metrics(events); const baseScore = JSON.parse(fs.readFileSync(path.join(base, "SCORECARD.json"))).V29R3_score; const spec = JSON.parse(require("child_process").execFileSync("git", ["show", `${specCommit}:${specJson}`], { cwd: repo, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 }));
  const cells = [...group(events, (e) => `${e.category}|${e.starting_price_split}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([key, rows]) => ({ category: key.split("|")[0], starting_price_region: key.split("|")[1], aggregate: metrics(rows) }));
  return { variant: "V32_NO_CHASE_STATE_MACHINE_EXECUTABLE", law: "QUOTE_PATH_PRIMARY_PLUS_JUL6_PRESSURE_SECONDARY_CONSERVATIVE_SELLER_PRINT_MAKER_FILL", R3_floor: baseScore, V32_score: aggregate, delta_vs_R3: Object.fromEntries(Object.keys(aggregate).map((k) => [k, typeof baseScore[k] === "number" ? aggregate[k] - baseScore[k] : null])), model_free_comparison_ceiling: { label: "MODEL_FREE_CEILING_NOT_EXECUTABLE_RESULT", joint_pairs: spec.summary.nochase_joint.n, denominator: 804, executable_gap_is_execution_price: spec.summary.nochase_joint.n - aggregate.joint_objective_pairs }, category_x_starting_price_region: cells };
}

function frontier(events) { const tiers = [{ id: "LE_93", test: (x) => x <= 93 }, { id: "LE_95", test: (x) => x <= 95 }, { id: "LE_97", test: (x) => x <= 97 }, { id: "LT_100", test: (x) => x < 100 }, { id: "ANY_PRICE", test: () => true }]; const make = (rows) => Object.fromEntries(tiers.map((tier) => [tier.id, { fixed_denominator: rows.length, completed_pairs: rows.filter((e) => e.completed_pair && tier.test(e.combined_entry_cents)).length, joint_objective_pairs: rows.filter((e) => e.joint_objective_pass_audited_close && tier.test(e.combined_entry_cents)).length }])); return { fixed_denominator: events.length, cumulative_frontier: make(events), category_x_starting_price_region: [...group(events, (e) => `${e.category}|${e.starting_price_split}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, rows]) => ({ cell, frontier: make(rows) })) }; }

function regret(events) { const legs = events.flatMap((e) => Object.values(e.legs)); const rows = legs.map((x) => ({ leg_identity: x.leg_identity, category: x.category, price_region: x.price_region, credited: x.credited, entry_cents: x.entry_cents, achievable_print_backed_floor_cents: x.objective_traded_low_cents, regret_cents: x.credited && Number.isInteger(x.objective_traded_low_cents) ? x.entry_cents - x.objective_traded_low_cents : null, loss_attribution: x.credited ? "CREDITED" : x.acted ? "RESTED_NOT_SELLER_HIT" : "NEVER_PLACED" })); return { law: "regret=credited_fill_minus_achievable_print_backed_floor; never-placed legs retain null numeric regret and explicit loss attribution", aggregate: distribution(rows.map((x) => x.regret_cents)), loss_attribution: countBy(rows, (x) => x.loss_attribution), category_x_price_region: [...group(rows, (x) => `${x.category}|${x.price_region}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, x]) => ({ cell, regret: distribution(x.map((r) => r.regret_cents)), loss_attribution: countBy(x, (r) => r.loss_attribution) })), rows } }

function traceSummary(events, trace) { const byEvent = new Map(events.map((e) => [e.event_id, e])); return events.flatMap((e) => Object.values(e.legs)).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)).map((leg) => { const s = trace.perLeg.get(leg.leg_identity) || { decisions: 0, state_counts: {}, action_counts: {}, disagreements: 0, first: null, last: null, fill: null }; const event = byEvent.get(leg.event_id); return { leg_identity: leg.leg_identity, ticker: leg.ticker, category: leg.category, price_region: leg.price_region, decision_receipts: s.decisions, state_counts: s.state_counts, action_counts: s.action_counts, disagreement_receipts: s.disagreements, first_decision: s.first, last_decision: s.last, fill: s.fill, final_state: leg.credited ? (event.joint_objective_pass_audited_close ? "JOINT_CAPTURED" : event.completed_pair ? "COMPLETED_NON_JOINT" : "NAKED") : leg.acted ? "RESTING_UNFILLED" : "NEVER_PLACED", terminal_reason: leg.terminal_reason }; }); }

async function main() {
  ensure(!output.includes("holdout"), "holdout forbidden"); ensure(fs.existsSync(base), "R3 base absent"); fs.mkdirSync(output, { recursive: true });
  process.stderr.write("V32_STAGE compact_base_start\n");
  const baseEvents = loadCompactBaseEvents(); ensure(baseEvents.length === 804, "D must be 804"); const sources = loadSources(); const bells = new Map(JSON.parse(fs.readFileSync(bellFile)).leg_rows.map((x) => [x.event_id, x.exact_bell_ts])); const tickers = new Set(baseEvents.flatMap((e) => Object.values(e.legs).map((x) => x.ticker))); ensure(tickers.size === 1608, "1608 unique legs required");
  process.stderr.write("V32_STAGE compact_base_complete\nV32_STAGE print_spool_start\n");
  const printLoad = buildPrintSpool(tickers, sources); const privateHashes = {}; const tracePath = path.join(output, "FULL_DECISION_TRACE.jsonl.gz"); const trace = createTraceCollector(tracePath); const events = [];
  process.stderr.write("V32_STAGE print_spool_complete\nV32_STAGE replay_start\n");
  for (const baseEvent of baseEvents) { const tapes = new Map(), eventPrints = new Map(); for (const leg of Object.values(baseEvent.legs)) { tapes.set(leg.ticker, loadTape(leg.ticker, sources.get(leg.ticker), privateHashes)); eventPrints.set(leg.ticker, printLoad.load(leg.ticker)); } events.push(simulateEvent(baseEvent, tapes, eventPrints, sources, bells, trace)); if (events.length % 100 === 0) process.stderr.write(`V32_STAGE replay_events_${events.length}\n`); }
  await trace.end(); printLoad.cleanup(); const legs = events.flatMap((e) => Object.values(e.legs)).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)); const scored = score(events); const frontierResult = frontier(events); const regretResult = regret(events); const summaries = traceSummary(events, trace);
  const spec = JSON.parse(require("child_process").execFileSync("git", ["show", `${specCommit}:${specJson}`], { cwd: repo, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 })); const costRows = spec.per_game.filter((x) => x.nochase_joint).map((x) => ({ event: x.event, model_free_ceiling_joint: true, V32_executable_joint: Boolean(events.find((e) => e.event_id === x.event)?.joint_objective_pass_audited_close), execution_cost: events.find((e) => e.event_id === x.event)?.joint_objective_pass_audited_close ? "EXECUTED" : "WAITED_AND_LOST_OR_NO_CONSERVATIVE_FILL" }));
  const baseEventsBy = new Map(baseEvents.map((e) => [e.event_id, e])); const changed = [], unchanged = []; for (const event of events) { const old = baseEventsBy.get(event.event_id); const before = Object.fromEntries(Object.entries(old.legs).map(([id, x]) => [id, { acted: x.acted, credited: x.credited, entry: x.entry_cents }])); const after = Object.fromEntries(Object.entries(event.legs).map(([id, x]) => [id, { acted: x.acted, credited: x.credited, entry: x.entry_cents }])); (semantic(before) === semantic(after) ? unchanged : changed).push(event.event_id); }
  const arn = events.find((e) => e.event_id.includes("ARNROM"));
  const core = {
    "SPEC_BINDING.json": canonical({ spec_commit: specCommit, spec_document: specDoc, spec_json: specJson, source_label: "MODEL_FREE_CEILING", executable_correction: "maker residency convention replaced by strictly later seller-aggressed print at/below resting limit", ceiling_joint: 201 }),
    "STATE_MACHINE_CONTRACT.json": canonical({ state_scope: "ONE_STATE_PER_LEG_FROM_BOTH_EVIDENCE_TYPES", quote_path: { authority: "PRIMARY", trailing_receipt_lookback_seconds: 300, falling: ["NEW_LOW_ASK", "SELLER_HIT_PRINT"], rising: ["NEW_HIGH_BID", "BUYER_LIFT_PRINT"], otherwise: "SETTLED" }, pressure: { authority: "SECONDARY_WHEN_QUOTE_PATH_SETTLED", depth_ratio_rising_at_or_above: .60, depth_ratio_falling_at_or_below: .40 }, discipline: { FALLING: "REST_ONE_CENT_UNDER_BEST_BID_AND_ONLY_REPRICE_DOWN", RISING: "NO_CHASE_HOLD", SETTLED: "QUALIFIED_STANDING_ASK_TAKEABLE" }, read_law: { spread_max_cents: 1, dwell_min_seconds: 10, displayed_size_min_contracts: 5 }, maker_fill_law: "STRICTLY_LATER_SELLER_AGGRESSED_TRUE_PRINT_SIZE_AT_LEAST_FIVE_AT_OR_BELOW_RESTING_LIMIT", pair_cap: "99_MINUS_FIRST_CREDITED_FILL", clock_law: "NO_ELAPSED_TIME_ACTION_TRIGGER; 300S_ONLY_CAUSAL_EVIDENCE_LOOKBACK; ORDERS_CARRY_TO_GUARDED_RIGHT_EDGE" }),
    "EVENT_LEDGER.jsonl.gz": gzipRows(events), "LEG_LEDGER.jsonl.gz": gzipRows(legs), "DECISION_TRACE_1608.json": canonical({ rows: summaries, conservation: { expected: 1608, actual: summaries.length } }), "SCORECARD.json": canonical(scored), "FRONTIER.json": canonical(frontierResult), "REGRET_GAUGE.json": canonical({ ...regretResult, rows: undefined }), "REGRET_LEDGER.jsonl.gz": gzipRows(regretResult.rows), "CARRIED_PAIR_CENSUS.json": canonical({ strict_carried_pairs: scored.V32_score.strict_carried_pairs, rows: events.filter((e) => e.completed_pair && Object.values(e.legs).some((x) => x.entry_minus_own_window1_close_cents > 0) && Object.values(e.legs).some((x) => x.entry_minus_own_window1_close_cents < 0)).map((e) => ({ event_id: e.event_id, combined_entry_cents: e.combined_entry_cents, legs: Object.values(e.legs).map((x) => ({ leg_id: x.leg_id, entry: x.entry_cents, own_close: x.own_window1_close_cents, delta: x.entry_minus_own_window1_close_cents })) })) }), "WAITED_AND_LOST_COST.json": canonical({ comparison_ceiling_joint: 201, V32_executable_joint: scored.V32_score.joint_objective_pairs, executable_gap_is_execution_price: 201 - scored.V32_score.joint_objective_pairs, rows: costRows, disposition: countBy(costRows, (x) => x.execution_cost) }), "STATE_DISAGREEMENT_RECEIPT.json": canonical({ receipts: trace.decisions(), disagreements: trace.disagreements(), by_category: Object.fromEntries([...trace.byCategory.entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([k, value]) => [k, { ...value, rate: value.receipts ? value.disagreements / value.receipts : null }])) }), "DIFFERENTIAL_RECEIPT.json": canonical({ base_variant: "V29R3_STANDING_FLOOR_RELEASE", changed_event_streams: changed.length, unchanged_event_streams: unchanged.length, changed_event_ids: changed, unchanged_semantic_hash: semantic(unchanged), conservation: changed.length + unchanged.length }), "ARNROM_REGRESSION_RECEIPT.json": canonical({ named_event: "ARNROM", event_id: arn?.event_id || null, result: arn || null }), "SOURCE_HASH_MANIFEST.json": canonical({ public_committed: Object.fromEntries([builderFile, policyFile, spoolHelperFile, spoolHelperSourceFile, unitTestFile, packageTestFile, floorFile, baseTraceFile, quoteFile, bellFile].map((file) => [path.relative(repo, file).replaceAll("\\", "/"), { sha256: fs.existsSync(file) ? fileHash(file) : null, bytes: fs.existsSync(file) ? fs.statSync(file).size : null }])), private_development_tapes: privateHashes, private_development_prints: printLoad.receipt }), "FORBIDDEN_ACCESS_RECEIPT.json": canonical({ holdout_accesses: 0, live_accesses: 0, network_accesses: 0, order_accesses: 0, position_accesses: 0, settlement_accesses: 0, window2_accesses: 0, deployment_accesses: 0, private_scope: "FIT_DEVELOPMENT_ONLY_20260712_20260720", assertions: ["No live engine import or invocation", "No holdout path", "No network API", "No order or position mutation"] })
  };
  for (const [name, bytes] of Object.entries(core)) write(name, bytes);
  write("REPORT.md", `# V32 no-chase state machine — executable replay\n\nV32 is an executable causal replay of the model-free discipline at ${specCommit}. Its conservative maker law credits only a strictly later seller-aggressed print of at least five contracts at or below a prior resting limit. The spec's 201 is retained only as a comparison ceiling.\n\n- R3 floor: 68 JOINT.\n- V32 executable JOINT: ${scored.V32_score.joint_objective_pairs}.\n- Gap to 201 comparison ceiling: ${201 - scored.V32_score.joint_objective_pairs}; this is the execution price.\n- Completed pairs: ${scored.V32_score.completed_pairs}; under par: ${scored.V32_score.pairs_under_par}; carried: ${scored.V32_score.strict_carried_pairs}.\n- Proven maker legs: ${scored.V32_score.proven_maker_legs}; proven taker legs: ${scored.V32_score.proven_taker_legs}.\n- ARNROM: ${arn ? `${arn.combined_entry_cents ?? "incomplete"} cents, JOINT=${arn.joint_objective_pass_audited_close}` : "not found"}.\n\nThe 300-second quantity is a trailing evidence window evaluated only on book/print receipts. It is not an elapsed-time placement, cancellation, or pair-lifecycle trigger.\n`);
  const names = [...Object.keys(core), "REPORT.md", "FULL_DECISION_TRACE.jsonl.gz"].sort();
  if (compare) { const mismatches = names.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name))); ensure(!mismatches.length, `determinism mismatch: ${mismatches.join(",")}`); write("DETERMINISM_RECEIPT.json", canonical({ builds: 2, byte_identical_core_artifacts: true, compared_against: path.basename(compare), compared_files: names, mismatches: [] })); } else write("DETERMINISM_RECEIPT.json", canonical({ builds: 1, byte_identical_core_artifacts: null, role: "FIRST_CLEAN_BUILD_PENDING_SECOND" }));
  const manifestNames = fs.readdirSync(output).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort(); write("ARTIFACT_HASH_MANIFEST.json", canonical({ files: Object.fromEntries(manifestNames.map((name) => [name, { sha256: fileHash(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size }])) }));
  process.stdout.write(`${canonical({ output, score: scored.V32_score, gap_to_201: 201 - scored.V32_score.joint_objective_pairs, trace_rows: trace.total() })}`);
}

main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
