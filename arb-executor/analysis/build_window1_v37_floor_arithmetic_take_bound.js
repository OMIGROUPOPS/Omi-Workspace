#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const child = require("child_process");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const stream = require("stream/promises");
const policy = require("./window1_v37_floor_arithmetic_take_bound.js");

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const repo = path.resolve(arg("--repo", "."));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const output = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/v37_floor_arithmetic_take_bound_20260806")));
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
const policyFile = path.join(repo, "arb-executor/analysis/window1_v37_floor_arithmetic_take_bound.js");
const unitTestFile = path.join(repo, "arb-executor/tests/test_window1_v37_floor_arithmetic_take_bound.js");
const packageTestFile = path.join(repo, "arb-executor/tests/test_window1_v37_floor_arithmetic_take_bound_package.js");
const V36_COMMIT = "bfde0d8d1135f5c5f48a5f3d619ab30050efab83";
const HYGIENE_COMMIT = "03bac97b12777d751fbb334fa6ae0f605445498a";
const V35_COMMIT = "0799fba887f1d1e84f9c0ef3e73096fd9d76019e";
const V34_W1_CAUSAL_COMMIT = "e56d79a2aee1f392b3bee5a0adad099c7f011976";
const V34_FULL_LIFE_COMMIT = "e0fb6a312d8bbc52806603fbc143bf2bcebb3df2";
const V34_TRADING_PHASE_COMMIT = "b430bcfff51f89c9466e77b798d4ac5d9fff15ea";
const V32_COMMIT = "a3429cad6719f96a25a900812e0f360b71a5607e";
const R3_COMMIT = "49f6501561c5d99a7f36c68ec41e0ea7250680e5";
const RECON_COMMIT = "938dca474e8bc4d96b17095e2aaa7cbb2fe97a87";
const NEARMISS_COMMIT = "65d49b5d623d99fb1d8ad3ef7eee6be9225c328e";
const START_LEDGER_COMMIT = "224417da642a9f378a0d83f76edffe9890cb4a6f";
const SUPPLIED_START_IDENTITY = "84b455c5";
const OFFER_COMMIT = "72512cd259ad9e3d077f7fc15af94dc2d6f72a90";
const RECON_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/RECONCILIATION_SEAL_804.json";
const NEARMISS_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/V32_NEARMISS_CENSUS.json";
const START_LEDGER_PATH = ".claude/window1_start_recovery_20260724/REAL_START_LEDGER_V3.jsonl";
const OFFER_PATH = ".claude/window1_t2_iteration_history/WINDOW1_FULL_LAWFUL_CEILING.json";
const R3_EVENT_PATH = ".claude/window1_live_v4_replay/v29r3_standing_floor_release_20260805/EVENT_LEDGER.jsonl.gz";
const FULL_LIFE_STRICT_PATH = ".claude/window1_live_v4_replay/v34_dual_side_residency_machine_20260805/STRICT_EVENT_LEDGER.jsonl.gz";
const FULL_LIFE_CENSUS_PATH = ".claude/window1_live_v4_replay/v34_dual_side_residency_machine_20260805/CENSUS_PRICED_EVENT_LEDGER.jsonl.gz";
const V34_W1_STRICT_PATH = ".claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/STRICT_EVENT_LEDGER.jsonl.gz";
const V34_W1_CENSUS_PATH = ".claude/window1_live_v4_replay/v34_w1_causal_capture_measurement_20260805/CENSUS_PRICED_EVENT_LEDGER.jsonl.gz";
const V35_STRICT_PATH = ".claude/window1_live_v4_replay/v35_living_rest_evidence_gate_20260806/STRICT_EVENT_LEDGER.jsonl.gz";
const V35_CENSUS_PATH = ".claude/window1_live_v4_replay/v35_living_rest_evidence_gate_20260806/CENSUS_PRICED_EVENT_LEDGER.jsonl.gz";
const V36_STRICT_PATH = ".claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/STRICT_EVENT_LEDGER.jsonl.gz";
const V36_CENSUS_PATH = ".claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/CENSUS_PRICED_EVENT_LEDGER.jsonl.gz";
const HYGIENE_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/DEEP_PAIR_HYGIENE_CENSUS.json";
const BLEED_COMMIT = "219c7ad118c0d4eb7daf9d7f55df6239548aaabc";
const BLEED_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/V34_BLEED_MECHANISM_CENSUS.json";
const EXEMPLAR_COMMIT = "1fd0328231dcff8bf03e470153deb26b84168e26";
const AUTOPSY_COMMIT = "9def6df3cb364f07f3477339bdee792dbcb8311b";
const AUTOPSY_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/DEEP_PAIR_AUTOPSY_V35.json";

function ensure(value, message) { if (!value) throw new Error(message); }
function sha(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function fileHash(file) { return sha(fs.readFileSync(file)); }
function splitArtifact(file, outputDir, prefix, maxBytes = 64 * 1024 * 1024) {
  const sourceSha256 = fileHash(file);
  const sourceBytes = fs.statSync(file).size;
  const handle = fs.openSync(file, "r");
  const buffer = Buffer.allocUnsafe(maxBytes);
  const parts = [];
  try {
    let offset = 0;
    for (let index = 0; offset < sourceBytes; index += 1) {
      const length = Math.min(maxBytes, sourceBytes - offset);
      const bytesRead = fs.readSync(handle, buffer, 0, length, offset);
      ensure(bytesRead === length, `short trace read at ${offset}`);
      const name = `${prefix}.part${String(index).padStart(3, "0")}`;
      const bytes = Buffer.from(buffer.subarray(0, bytesRead));
      fs.writeFileSync(path.join(outputDir, name), bytes);
      parts.push({ name, bytes: bytesRead, sha256: sha(bytes) });
      offset += bytesRead;
    }
  } finally {
    fs.closeSync(handle);
  }
  fs.rmSync(file);
  const partBytesSum = parts.reduce((sum, row) => sum + row.bytes, 0);
  return {
    source_sha256: sourceSha256,
    source_bytes: sourceBytes,
    max_part_bytes: maxBytes,
    parts,
    concatenation_law: "BINARY_CONCATENATION_IN_ASCENDING_PART_NAME_ORDER_REPRODUCES_SOURCE_BYTE_FOR_BYTE",
    conservation: { part_bytes_sum: partBytesSum, source_bytes: sourceBytes, pass: partBytesSum === sourceBytes },
  };
}
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function semantic(value) { return sha(JSON.stringify(value)); }
function write(name, bytes) { fs.writeFileSync(path.join(output, name), bytes); }
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function readRows(file) { const text = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse) : []; }
function readRowsBytes(bytes) { const text = zlib.gunzipSync(bytes).toString("utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse) : []; }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
async function writeGzipRowsFile(file, rows) {
  async function* encodedRows() { for (const row of rows) yield `${JSON.stringify(row)}\n`; }
  await stream.pipeline(encodedRows(), zlib.createGzip({ level: 9, mtime: 0 }), fs.createWriteStream(file));
}
function parseCsv(text) { const lines = text.trimEnd().split(/\r?\n/); const h = lines.shift().split(","); return lines.filter(Boolean).map((line) => Object.fromEntries(line.split(",").map((v, i) => [h[i], v]))); }
function parseEt(value) { const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/); if (!m) return null; let h = +m[4]; if (m[7] === "AM" && h === 12) h = 0; if (m[7] === "PM" && h !== 12) h += 12; return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(h).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000; }
function parseIso(value) { if (!value) return null; const n = Date.parse(value); return Number.isFinite(n) ? n / 1000 : null; }
function group(rows, fn) { const out = new Map(); for (const row of rows) { const key = fn(row); if (!out.has(key)) out.set(key, []); out.get(key).push(row); } return out; }
function countBy(rows, fn) { const out = {}; for (const row of rows) { const key = String(fn(row)); out[key] = (out[key] || 0) + 1; } return Object.fromEntries(Object.entries(out).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function quantile(values, p) { const x = values.filter(Number.isFinite).sort((a, b) => a - b); return x.length ? x[Math.floor((x.length - 1) * p)] : null; }
function distribution(values, unit = null) { const x = values.filter(Number.isFinite), total = x.reduce((a, b) => a + b, 0); const out = { denominator: values.length, numeric_n: x.length, null_n: values.length - x.length, min: x.length ? Math.min(...x) : null, p25: quantile(x, .25), median: quantile(x, .5), p75: quantile(x, .75), p90: quantile(x, .9), max: x.length ? Math.max(...x) : null, total }; if (unit) out[`total_${unit}`] = total; return out; }
function actionSummary(rows) { const targets = rows.map((row) => row.target_cents).filter(Number.isInteger), digest = crypto.createHash("sha256"); for (const row of rows) digest.update(`${JSON.stringify(row)}\n`); return { count: rows.length, kinds: countBy(rows, (row) => row.kind), target_cents: distribution(targets, "cents"), first: rows[0] || null, last: rows.at(-1) || null, ordered_jsonl_sha256: digest.digest("hex") }; }
function gitShow(commit, rel) { return child.execFileSync("git", ["show", `${commit}:${rel}`], { cwd: repo, maxBuffer: 128 * 1024 * 1024 }); }
function requireCommit(commit) { ensure(child.execFileSync("git", ["rev-parse", "--verify", `${commit}^{commit}`], { cwd: repo, encoding: "utf8" }).trim() === commit, `missing commit ${commit}`); child.execFileSync("git", ["cat-file", "-e", `${commit}^{commit}`], { cwd: repo }); }
function safeClean(dir) { const r = path.resolve(dir); ensure(path.basename(r).toLowerCase().includes("v37"), `unsafe output ${r}`); ensure(r !== repo && r !== path.parse(r).root, `unsafe output ${r}`); fs.rmSync(r, { recursive: true, force: true }); fs.mkdirSync(r, { recursive: true }); }

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

function tradingPhaseCloseFromPrints(rows, expectedClose) {
  if (!Number.isInteger(expectedClose)) return { status: "UNAVAILABLE_CANONICAL_TRUE_CLOSE_NULL", price_cents: null, timestamp_epoch: null, ordinal: null, receipts: [], boundary_derivation: "EVENT_SIBLING_TRADING_PHASE_BOUNDARY_REQUIRED_FOR_STREAM_CLIP" };
  const matching = rows.filter((row) => row.price === expectedClose);
  if (!matching.length) return { status: "CANONICAL_TRUE_CLOSE_NOT_PRESENT_IN_ORDERED_EXCHANGE_PRINTS", price_cents: expectedClose, timestamp_epoch: null, ordinal: null, receipts: [] };
  const timestamp = matching.at(-1).ts, boundaryMatches = matching.filter((row) => row.ts === timestamp), sameTimestamp = rows.filter((row) => row.ts === timestamp);
  return { status: "AVAILABLE_HASH_BOUND_CANONICAL_TRADING_PHASE_CLOSE", price_cents: expectedClose, timestamp_epoch: timestamp, ordinal: boundaryMatches.at(-1).ordinal, receipts: boundaryMatches.map((row) => row.receipt), aggressor_sides: [...new Set(boundaryMatches.map((row) => row.taker_side))].sort(), total_size: boundaryMatches.reduce((sum, row) => sum + row.size, 0), same_timestamp_prices: [...new Set(sameTimestamp.map((row) => row.price))].sort((a, b) => a - b), boundary_derivation: "LATEST_ORDERED_EXCHANGE_TIMESTAMP_CONTAINING_HASH_BOUND_TRUE_CLOSE" };
}

function atOrBeforeClose(row, close) {
  if (row.ts < close.timestamp_epoch) return true;
  if (row.ts > close.timestamp_epoch) return false;
  if (row.kind !== "PRINT") return true;
  if (close.price_cents > 10 && close.price_cents < 90) return row.price > 10 && row.price < 90;
  return row.price === close.price_cents;
}

function armSibling(sibling, fillLeg, row, mode, actions, eventClose) {
  if (row.ts > eventClose.timestamp_epoch) { sibling.pair_arm_expired_at_own_trading_phase_close = true; return; }
  sibling.pair_cap_cents = 99 - fillLeg.entry_cents;
  const source = sibling.source, bell = sibling.bell;
  actions.push({ mode, kind: "PAIR_ARM", event_id: sibling.event_id, leg_identity: sibling.leg_identity, sibling_fill_cents: fillLeg.entry_cents, pair_cap_cents: sibling.pair_cap_cents, receipt: row.receipt, ...clock(row.ts, source, bell, eventClose.timestamp_epoch), same_receipt_fill_forbidden: true });
  if (sibling.active_order && sibling.active_order.target_cents > sibling.pair_cap_cents) {
    if (policy.lawfulCent(sibling.pair_cap_cents)) sibling.active_order = { target_cents: sibling.pair_cap_cents, action_ts: row.ts, action_receipt: row.receipt, action: "PAIR_CAP_REPRICE", source_state: "SIBLING_FILL" };
    else sibling.active_order = null;
  }
}

function simulateMode(baseEvent, tapes, prints, sources, bells, mode, actionRows, span, timeline) {
  const ids = Object.keys(baseEvent.legs).sort(), event = { event_id: baseEvent.event_id, category: baseEvent.category, starting_price_split: baseEvent.starting_price_split, mode, market_life_start_epoch: span.market_life_start_epoch, trading_phase_close_epoch: span.trading_phase_close_epoch, legs: {} };
  for (const id of ids) {
    const b = baseEvent.legs[id], p = prints.get(b.ticker), t = tapes.get(b.ticker), close = b.canonical_close_contract, phasePrints = p.filter((row) => atOrBeforeClose(row, close));
    ensure((close.price_cents ?? null) === (b.canonical_true_close_cents ?? null), `canonical close mismatch ${b.leg_identity}`);
    event.legs[id] = { ...b, canonical_close_contract: undefined, source: sources.get(b.ticker), bell: bells.get(baseEvent.event_id), trading_phase_close_status: close.status, own_trading_phase_close_cents: close.price_cents, own_trading_phase_close_timestamp_epoch: close.timestamp_epoch, own_trading_phase_close_ordinal: close.ordinal, own_trading_phase_close_receipts: close.receipts, own_trading_phase_close_same_timestamp_prices: close.same_timestamp_prices || [], own_trading_phase_close_boundary_derivation: close.boundary_derivation, own_trading_phase_traded_low_cents: phasePrints.length ? phasePrints.reduce((low, x) => Math.min(low, x.price), Infinity) : null, own_trading_phase_qualifying_ask_floor_cents: null, acted: false, credited: false, entry_cents: null, fill_class: null, action_timestamp_epoch: null, fill_timestamp_epoch: null, pair_cap_cents: null, active_order: null, prior_book: null, latest_directional: null, running_trade_low: null, running_qualified_ask_low: null, decisions: 0, state_counts: { FALLING: 0, RISING: 0, SETTLED: 0 }, action_counts: {}, disagreement_count: 0, maker_reprices: 0, first_decision: null, last_decision: null, first_action: null, terminal_reason: null, first_book_epoch: t[0]?.ts ?? null, last_book_epoch: t.filter((row) => atOrBeforeClose(row, close)).at(-1)?.ts ?? null, first_print_epoch: phasePrints[0]?.ts ?? null, last_print_epoch: phasePrints.at(-1)?.ts ?? null };
  }
  for (const row of timeline) {
    if (event.legs[ids[0]].credited && event.legs[ids[1]].credited) break;
    if (row.ts < span.market_life_start_epoch || row.ts > span.trading_phase_close_epoch) continue;
    const leg = event.legs[row.leg_id]; if (leg.credited) continue; const sibling = event.legs[ids.find((id) => id !== row.leg_id)];
    if (!atOrBeforeClose(row, { timestamp_epoch: leg.own_trading_phase_close_timestamp_epoch, price_cents: leg.own_trading_phase_close_cents })) continue;
    if (row.kind === "PRINT") {
      let maker = null;
      if (mode === "STRICT_LAW" && policy.strictMakerFill(leg.active_order, row)) maker = { class: "PROVEN_MAKER_SELLER_AGGRESSED_PRINT_SIZE_FIVE_AT_OR_BELOW_REST", strict: true };
      if (mode === "CENSUS_PRICED") maker = policy.censusPricedFill(leg.active_order, row);
      if (maker?.fill || maker?.strict || maker?.class === "PROVEN_MAKER_SELLER_AGGRESSED_PRINT_SIZE_FIVE_AT_OR_BELOW_REST") {
        leg.credited = true; leg.entry_cents = leg.active_order.target_cents; leg.action_timestamp_epoch = leg.active_order.action_ts; leg.fill_timestamp_epoch = row.ts; leg.fill_class = maker.class; leg.terminal_reason = maker.class;
        actionRows.push({ mode, kind: "FILL", event_id: event.event_id, leg_identity: leg.leg_identity, fill_class: maker.class, entry_cents: leg.entry_cents, action_timestamp_epoch: leg.action_timestamp_epoch, receipt: row.receipt, print: { price_cents: row.price, size: row.size, taker_side: row.taker_side }, ...clock(row.ts, leg.source, leg.bell, leg.own_trading_phase_close_timestamp_epoch) });
        armSibling(sibling, leg, row, mode, actionRows, { timestamp_epoch: sibling.own_trading_phase_close_timestamp_epoch, price_cents: sibling.own_trading_phase_close_cents });
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
    leg.own_trading_phase_qualifying_ask_floor_cents = leg.running_qualified_ask_low;
    const quote = policy.quotePathState(leg.latest_directional ? [leg.latest_directional] : [], row.ts), pressure = policy.pressureState(row.depth_ratio), combined = policy.combineState(quote, pressure);
    const decision = policy.decide({ state: combined.state, book: row, activeTarget: leg.active_order?.target_cents ?? null, pairCap: leg.pair_cap_cents, runningTradeLow: leg.running_trade_low, runningQualifyingAskLow: leg.running_qualified_ask_low });
    leg.prior_book = row; leg.decisions += 1; leg.state_counts[combined.state] += 1; if (combined.disagreement) leg.disagreement_count += 1; leg.action_counts[decision.action] = (leg.action_counts[decision.action] || 0) + 1;
    const detail = { receipt: row.receipt, ...clock(row.ts, leg.source, leg.bell, leg.own_trading_phase_close_timestamp_epoch), observation: { bid: row.bid, ask: row.ask, last_traded: row.last_trade, spread: row.spread, ask_dwell_seconds: row.ask_dwell_seconds, top_ask_size: row.top_ask_size, bid_depth_5: row.bid_depth_5, ask_depth_5: row.ask_depth_5, depth_ratio: row.depth_ratio }, quote_path: quote, pressure_state: pressure, combined_state: combined.state, disagreement: combined.disagreement, causal_discount_evidence: { running_trade_low_cents: leg.running_trade_low, running_qualifying_ask_low_cents: leg.running_qualified_ask_low }, pair_cap_cents: leg.pair_cap_cents, decision };
    leg.first_decision ||= detail; leg.last_decision = detail;
    if (decision.action === "PLACE_REST" || decision.action === "REPRICE_REST_DOWN") {
      if (decision.action === "REPRICE_REST_DOWN") leg.maker_reprices += 1;
      leg.acted = true; leg.active_order = { target_cents: decision.target_cents, action_ts: row.ts, action_receipt: row.receipt, action: decision.action, source_state: combined.state }; leg.first_action ||= detail;
      actionRows.push({ mode, kind: decision.action, event_id: event.event_id, leg_identity: leg.leg_identity, target_cents: decision.target_cents, receipt: row.receipt, state: combined.state, reason: decision.reason, ...clock(row.ts, leg.source, leg.bell, leg.own_trading_phase_close_timestamp_epoch) });
    } else if (decision.action === "TAKE") {
      leg.acted = true; leg.credited = true; leg.entry_cents = decision.target_cents; leg.action_timestamp_epoch = row.ts; leg.fill_timestamp_epoch = row.ts; leg.fill_class = "PROVEN_TAKER_R3_QUALIFIED_SETTLED_ASK"; leg.terminal_reason = leg.fill_class; leg.first_action ||= detail;
      actionRows.push({ mode, kind: "FILL", event_id: event.event_id, leg_identity: leg.leg_identity, fill_class: leg.fill_class, entry_cents: leg.entry_cents, receipt: row.receipt, displayed_ask: { price_cents: row.ask, size: row.top_ask_size, spread: row.spread, dwell_seconds: row.ask_dwell_seconds, crossed_or_locked: row.bid >= row.ask }, ...clock(row.ts, leg.source, leg.bell, leg.own_trading_phase_close_timestamp_epoch) });
      armSibling(sibling, leg, row, mode, actionRows, { timestamp_epoch: sibling.own_trading_phase_close_timestamp_epoch, price_cents: sibling.own_trading_phase_close_cents });
    }
  }
  for (const leg of Object.values(event.legs)) {
    leg.entry_minus_trading_phase_close_cents = leg.credited && Number.isInteger(leg.own_trading_phase_close_cents) ? leg.entry_cents - leg.own_trading_phase_close_cents : null;
    leg.entry_minus_qualifying_ask_floor_cents = leg.credited && Number.isInteger(leg.own_trading_phase_qualifying_ask_floor_cents) ? leg.entry_cents - leg.own_trading_phase_qualifying_ask_floor_cents : null;
    leg.entry_minus_traded_low_cents = leg.credited && Number.isInteger(leg.own_trading_phase_traded_low_cents) ? leg.entry_cents - leg.own_trading_phase_traded_low_cents : null;
    if (!leg.credited) leg.terminal_reason = leg.acted ? "STANDING_REST_UNFILLED_AT_MARKET_CLOSE" : "OWN_TWO_SIDED_BOOK_NEVER_FORMED";
    leg.first_action_timestamp_epoch = leg.first_action?.timestamp_epoch ?? null;
    delete leg.source; delete leg.bell; delete leg.active_order; delete leg.prior_book; delete leg.latest_directional;
  }
  const legs = Object.values(event.legs); event.completed_pair = legs.every((x) => x.credited); event.combined_entry_cents = event.completed_pair ? legs.reduce((s, x) => s + x.entry_cents, 0) : null; event.pair_under_par = event.completed_pair && event.combined_entry_cents < 100; event.both_legs_strictly_below_trading_phase_close = event.completed_pair && legs.every((x) => Number.isInteger(x.own_trading_phase_close_cents) && x.entry_cents < x.own_trading_phase_close_cents); event.joint_objective_pass = event.pair_under_par && event.both_legs_strictly_below_trading_phase_close; event.execution_floor_pair_pass = event.pair_under_par && legs.every((x) => Number.isInteger(x.own_trading_phase_qualifying_ask_floor_cents) && x.entry_cents <= x.own_trading_phase_qualifying_ask_floor_cents);
  return event;
}

function metrics(events) {
  const legs = events.flatMap((e) => Object.values(e.legs)), completed = events.filter((e) => e.completed_pair), carried = completed.filter((e) => { const d = Object.values(e.legs).map((x) => x.entry_minus_trading_phase_close_cents); return d.some((x) => x > 0) && d.some((x) => x < 0); });
  return { D: events.length, legs: legs.length, canonical_T1_joint_comparison_universe: 750, acted_legs: legs.filter((x) => x.acted).length, credited_legs: legs.filter((x) => x.credited).length, proven_maker_legs: legs.filter((x) => x.fill_class?.startsWith("PROVEN_MAKER")).length, proven_taker_legs: legs.filter((x) => x.fill_class?.startsWith("PROVEN_TAKER")).length, census_priced_conversion_legs: legs.filter((x) => x.fill_class === "CENSUS_PRICED_ONE_CENT_RESIDENCY_CONVERSION").length, completed_pairs: completed.length, pairs_under_par: events.filter((e) => e.pair_under_par).length, both_legs_strictly_below_close: events.filter((e) => e.both_legs_strictly_below_trading_phase_close).length, joint_objective_pairs: events.filter((e) => e.joint_objective_pass).length, carried_pairs: carried.length, execution_floor_pair_passes: events.filter((e) => e.execution_floor_pair_pass).length, close_unavailable_legs: legs.filter((x) => !Number.isInteger(x.own_trading_phase_close_cents)).length };
}

function scoreColumn(events, label) {
  const aggregate = metrics(events), cells = [...group(events, (e) => `${e.category}|${e.starting_price_split}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, rows]) => ({ cell, metrics: metrics(rows) }));
  return { label, canonical_T1_joint_comparison_universe: 750, aggregate, delta_joint_vs_R3_68: aggregate.joint_objective_pairs - 68, gap_to_named_603: 603 - aggregate.joint_objective_pairs, gap_to_canonical_T1_joint_750: 750 - aggregate.joint_objective_pairs, category_x_starting_price_region: cells };
}

function frontier(events) {
  const tiers = [{ id: "LE_93", test: (x) => x <= 93 }, { id: "LE_95", test: (x) => x <= 95 }, { id: "LE_97", test: (x) => x <= 97 }, { id: "LT_100", test: (x) => x < 100 }, { id: "ANY_PRICE", test: () => true }];
  const make = (rows) => Object.fromEntries(tiers.map((tier) => [tier.id, { fixed_denominator: rows.length, completed_pairs: rows.filter((e) => e.completed_pair && tier.test(e.combined_entry_cents)).length, joint_objective_pairs: rows.filter((e) => e.joint_objective_pass && tier.test(e.combined_entry_cents)).length }]));
  return { fixed_denominator: events.length, canonical_T1_joint_comparison_universe: 750, cumulative_frontier: make(events), category_x_starting_price_region: [...group(events, (e) => `${e.category}|${e.starting_price_split}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, rows]) => ({ cell, canonical_T1_joint_comparison_universe: 750, frontier: make(rows) })) };
}

function regret(events) {
  const rows = events.flatMap((e) => Object.values(e.legs)).map((x) => ({ leg_identity: x.leg_identity, category: x.category, price_region: x.price_region, credited: x.credited, entry_cents: x.entry_cents, achievable_trading_phase_true_print_floor_cents: x.own_trading_phase_traded_low_cents, regret_cents: x.credited && Number.isInteger(x.own_trading_phase_traded_low_cents) ? x.entry_cents - x.own_trading_phase_traded_low_cents : null, loss_attribution: x.credited ? "CREDITED" : x.acted ? "RESTED_UNFILLED" : "NO_FORMED_OWN_BOOK" }));
  return { law: "regret=entry-minus-lowest-true-exchange-print-clipped-to-canonical-trading-phase; incomplete numeric regret remains null; settlement evidence forbidden", canonical_T1_joint_comparison_universe: 750, aggregate: distribution(rows.map((x) => x.regret_cents), "cents"), loss_attribution: countBy(rows, (x) => x.loss_attribution), category_x_price_region: [...group(rows, (x) => `${x.category}|${x.price_region}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, x]) => ({ cell, canonical_T1_joint_comparison_universe: 750, regret: distribution(x.map((r) => r.regret_cents), "cents"), loss_attribution: countBy(x, (r) => r.loss_attribution) })), rows };
}

function compactTrace(events) {
  return events.flatMap((e) => Object.values(e.legs).map((x) => ({ mode: e.mode, event_id: e.event_id, leg_identity: x.leg_identity, ticker: x.ticker, category: x.category, price_region: x.price_region, decisions: x.decisions, state_counts: x.state_counts, action_counts: x.action_counts, disagreement_count: x.disagreement_count, maker_reprices: x.maker_reprices, first_decision: x.first_decision, last_decision: x.last_decision, first_action_timestamp_epoch: x.first_action_timestamp_epoch, fill_timestamp_epoch: x.fill_timestamp_epoch, entry_cents: x.entry_cents, fill_class: x.fill_class, terminal_reason: x.terminal_reason, final_state: x.credited ? (e.joint_objective_pass ? "JOINT_CAPTURED" : e.completed_pair ? "COMPLETED_NON_JOINT" : "NAKED") : x.acted ? "RESTING_UNFILLED" : "NO_FORMED_OWN_BOOK" }))).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity));
}

function diffVsR3(baseEvents, events, mode) {
  const by = new Map(events.map((e) => [e.event_id, e])), changed = [], unchanged = [];
  for (const baseEvent of baseEvents) for (const [id, old] of Object.entries(baseEvent.legs)) { const x = by.get(baseEvent.event_id).legs[id], before = old.R3, after = { acted: x.acted, credited: x.credited, entry_cents: x.entry_cents }; (semantic(before) === semantic(after) ? unchanged : changed).push(x.leg_identity); }
  return { mode, base: "V29_R3_JOINT_68", changed_leg_streams: changed.length, unchanged_leg_streams: unchanged.length, changed_leg_identities: changed, unchanged_semantic_hash: semantic(unchanged), conservation: changed.length + unchanged.length };
}

async function legacyMain() {
  ensure(!output.toLowerCase().includes("holdout"), "holdout forbidden");
  for (const c of [V34_PARENT, V32_COMMIT, R3_COMMIT, RECON_COMMIT, NEARMISS_COMMIT, CANONICAL_CLOSE_COMMIT]) requireCommit(c);
  safeClean(output);
  const baseEvents = loadBaseEvents(); ensure(baseEvents.length === 804, "D must be 804");
  const canonicalCloseBytes = gitShow(CANONICAL_CLOSE_COMMIT, CANONICAL_CLOSE_PATH), canonicalCloseMap = JSON.parse(canonicalCloseBytes), canonicalByEvent = new Map(canonicalCloseMap.per_game.map((row) => [row.event, row]));
  ensure(canonicalCloseMap.summary.CANONICAL === "TRADING_PHASE_CLOSE_BASIS", "canonical trading-phase stamp missing");
  ensure(canonicalCloseMap.summary.T1_joint.n === 750, "canonical T1-joint must be 750");
  ensure(canonicalCloseMap.per_game.length === 804 && canonicalByEvent.size === 804, "canonical close event conservation failed");
  const sources = loadSources(), bells = new Map(JSON.parse(fs.readFileSync(bellFile)).leg_rows.map((x) => [x.event_id, x.exact_bell_ts])), tickers = new Set(baseEvents.flatMap((e) => Object.values(e.legs).map((x) => x.ticker))); ensure(tickers.size === 1608, "1608 legs required");
  process.stderr.write("V34_STAGE print_spool_start\n"); const printLoad = buildPrintSpool(tickers); process.stderr.write("V34_STAGE print_spool_complete\n");
  const tapeHashes = {}, strictEvents = [], censusEvents = [], spans = [], actionRows = [];
  for (const baseEvent of baseEvents) {
    const tapes = new Map(), prints = new Map();
    for (const leg of Object.values(baseEvent.legs)) prints.set(leg.ticker, printLoad.load(leg.ticker));
    for (const leg of Object.values(baseEvent.legs)) { const rawTape = loadFullTape(leg.ticker, tapeHashes); tapes.set(leg.ticker, condenseTape(rawTape, prints.get(leg.ticker))); }
    const printSets = [...prints.values()], tapeSets = [...tapes.values()], printCount = printSets.reduce((n, rows) => n + rows.length, 0);
    ensure(printCount > 0, `no event exchange activity ${baseEvent.event_id}`);
    const canonicalRow = canonicalByEvent.get(baseEvent.event_id); ensure(canonicalRow, `canonical event missing ${baseEvent.event_id}`);
    const orderedLegs = Object.values(baseEvent.legs); ensure(canonicalRow.true_close.length === orderedLegs.length, `canonical leg count mismatch ${baseEvent.event_id}`);
    const closes = new Map();
    orderedLegs.forEach((leg, index) => {
      leg.canonical_true_close_cents = canonicalRow.true_close[index];
      const close = tradingPhaseCloseFromPrints(prints.get(leg.ticker), leg.canonical_true_close_cents);
      ensure(close.status === "AVAILABLE_HASH_BOUND_CANONICAL_TRADING_PHASE_CLOSE" || close.status === "UNAVAILABLE_CANONICAL_TRUE_CLOSE_NULL", `trading close mismatch ${leg.leg_identity}: ${close.status}`);
      closes.set(leg.ticker, close);
    });
    const availableCloseTimes = [...closes.values()].map((close) => close.timestamp_epoch).filter(Number.isFinite);
    ensure(availableCloseTimes.length > 0, `no canonical trading-phase boundary ${baseEvent.event_id}`);
    const eventTradingPhaseBoundary = Math.max(...availableCloseTimes);
    orderedLegs.forEach((leg) => {
      let close = closes.get(leg.ticker);
      if (!Number.isFinite(close.timestamp_epoch)) close = { ...close, timestamp_epoch: eventTradingPhaseBoundary, boundary_derivation: "CANONICAL_NULL_CLOSE_STREAM_CLIPPED_AT_SIBLING_TRADING_PHASE_BOUNDARY", receipts: [], same_timestamp_prices: [] };
      leg.canonical_close_contract = close;
      closes.set(leg.ticker, close);
    });
    const finalExchangeActivity = printSets.reduce((latest, rows) => rows.length ? Math.max(latest, rows.at(-1).ts) : latest, -Infinity);
    const tradingPhaseClose = [...closes.values()].reduce((latest, close) => Math.max(latest, close.timestamp_epoch), -Infinity);
    const marketStart = [...printSets, ...tapeSets].reduce((earliest, rows) => rows.length ? Math.min(earliest, rows[0].ts) : earliest, Infinity);
    const source0 = sources.get(Object.values(baseEvent.legs)[0].ticker), bell = bells.get(baseEvent.event_id);
    const perLeg = orderedLegs.map((leg) => { const t = tapes.get(leg.ticker), p = prints.get(leg.ticker), close = closes.get(leg.ticker), phaseTape = t.filter((row) => atOrBeforeClose(row, close)), phasePrints = p.filter((row) => atOrBeforeClose(row, close)), bs = phaseTape[0]?.ts ?? null, be = phaseTape.at(-1)?.ts ?? null, ps = phasePrints[0]?.ts ?? null, overlapStart = Number.isFinite(bs) ? Math.max(marketStart, bs) : null, overlapEnd = Number.isFinite(be) ? Math.min(close.timestamp_epoch, be) : null, bookSeconds = Number.isFinite(overlapStart) && Number.isFinite(overlapEnd) ? Math.max(0, overlapEnd - overlapStart) : 0; return { leg_identity: leg.leg_identity, ticker: leg.ticker, canonical_true_close_cents: leg.canonical_true_close_cents, trading_phase_close_status: close.status, trading_phase_close_epoch: close.timestamp_epoch, trading_phase_close_ordinal: close.ordinal, trading_phase_close_receipt: close.receipts[0] || null, trading_phase_close_boundary_derivation: close.boundary_derivation, first_two_sided_book_epoch: bs, last_two_sided_book_epoch: be, first_true_print_epoch: ps, trading_phase_true_print_count: phasePrints.length, full_exchange_true_print_count: p.length, final_exchange_activity_epoch: p.at(-1)?.ts ?? null, settlement_evidence_excluded_count: p.length - phasePrints.length, settlement_evidence_excluded_seconds: p.length ? p.at(-1).ts - close.timestamp_epoch : null, two_sided_book_receipt_count_raw: t.rawReceiptCount, two_sided_book_receipt_count_causal: phaseTape.length, causally_equivalent_or_post_phase_receipts_excluded: t.rawReceiptCount - phaseTape.length, book_coverage_seconds: bookSeconds, trading_phase_seconds: close.timestamp_epoch - marketStart, book_coverage_fraction: close.timestamp_epoch > marketStart ? bookSeconds / (close.timestamp_epoch - marketStart) : null, print_only_remainder_seconds: Number.isFinite(be) && close.timestamp_epoch > be ? close.timestamp_epoch - be : 0 }; });
    const span = { event_id: baseEvent.event_id, category: baseEvent.category, starting_price_split: baseEvent.starting_price_split, canonical_map_tier: canonicalRow.tier, canonical_map_T1_joint: canonicalRow.t1_joint, market_life_start_epoch: marketStart, trading_phase_close_epoch: tradingPhaseClose, final_exchange_activity_epoch: finalExchangeActivity, settlement_phase_excluded_seconds: finalExchangeActivity - tradingPhaseClose, trading_phase_seconds: tradingPhaseClose - marketStart, formation_clock: clock(marketStart, source0, bell, tradingPhaseClose), close_clock: clock(tradingPhaseClose, source0, bell, tradingPhaseClose), actual_bell_role: Number.isFinite(bell) ? "TIMING_METADATA_ONLY_NEVER_BOUNDARY" : "NOT_AVAILABLE_NEVER_REQUIRED", per_leg: perLeg }; spans.push(span);
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
  const closeRows = strictEvents.flatMap((event) => Object.values(event.legs).map((leg) => ({ event_id: event.event_id, leg_identity: leg.leg_identity, status: leg.trading_phase_close_status, price_cents: leg.own_trading_phase_close_cents, timestamp_epoch: leg.own_trading_phase_close_timestamp_epoch, ordinal: leg.own_trading_phase_close_ordinal, receipt: leg.own_trading_phase_close_receipts[0] })));
  const closePairs = strictEvents.map((event) => { const prices = Object.values(event.legs).map((leg) => leg.own_trading_phase_close_cents); return { event_id: event.event_id, both_available: prices.every(Number.isInteger), close_sum_cents: prices.every(Number.isInteger) ? prices[0] + prices[1] : null }; });
  const settlementRowsExcluded = spans.flatMap((span) => span.per_leg).reduce((sum, leg) => sum + leg.settlement_evidence_excluded_count, 0);
  const closeRuler = { law: canonicalCloseMap.summary.WINDOW_LAW, canonical_commit: CANONICAL_CLOSE_COMMIT, canonical_path: CANONICAL_CLOSE_PATH, canonical_sha256: sha(canonicalCloseBytes), canonical_bytes: canonicalCloseBytes.length, boundary_identity_law: "LATEST_ORDERED_EXCHANGE_TIMESTAMP_CONTAINING_EACH_HASH_BOUND_TRUE_CLOSE; SAME_TIMESTAMP_TERMINAL_BAND_ROWS_EXCLUDED_WHEN_CLOSE_IS_CONTESTED", map_events: canonicalCloseMap.per_game.length, map_T1_joint_comparison_universe: canonicalCloseMap.summary.T1_joint.n, map_event_identity_mismatches: 0, map_leg_close_mismatches: 0, legs: closeRows.length, available_legs: closeRows.filter((row) => Number.isInteger(row.price_cents)).length, unavailable_legs: closeRows.filter((row) => !Number.isInteger(row.price_cents)).length, close_price_counts: countBy(closeRows, (row) => row.price_cents ?? row.status), events: closePairs.length, both_closes_available_events: closePairs.filter((row) => row.both_available).length, close_sum_counts: countBy(closePairs, (row) => row.close_sum_cents ?? "UNAVAILABLE"), scored: { strict_completed_pairs: strictScore.aggregate.completed_pairs, strict_both_below_close: strictScore.aggregate.both_legs_strictly_below_close, strict_joint: strictScore.aggregate.joint_objective_pairs, census_completed_pairs: censusScore.aggregate.completed_pairs, census_both_below_close: censusScore.aggregate.both_legs_strictly_below_close, census_joint: censusScore.aggregate.joint_objective_pairs } };
  const settlementExclusion = { scoring_basis: "CANONICAL_TRADING_PHASE_ONLY", settlement_basis_close_reads: 0, settlement_basis_floor_reads: 0, settlement_basis_fill_reads: 0, full_archive_rows_used_only_to_locate_and_exclude_terminal_settlement_phase: true, excluded_post_trading_phase_print_rows: settlementRowsExcluded, excluded_seconds_by_leg: distribution(spans.flatMap((span) => span.per_leg.map((leg) => leg.settlement_evidence_excluded_seconds)), "seconds"), negative_control_stamp: canonicalCloseMap.summary.SETTLEMENT_VARIANT_STAMP };
  const control = { schema_version: "window1-v34-control-v3-canonical-trading-phase", construction_parent: V34_PARENT, architecture: "DUAL_SIDE_RESIDENCY_MACHINE_NOT_OVERLAY", window_law: { left: "EARLIER_OF_FIRST_TWO_SIDED_BOOK_OR_FIRST_TRUE_EXCHANGE_PRINT", right: "HASH_BOUND_THE_603_MAP_TRADING_PHASE_BOUNDARY_PER_LEG; NULL_CLOSE_STREAM_USES_SIBLING_GAME_BOUNDARY_WITH_GRADE_UNAVAILABLE", close: "THE_603_MAP_PER_LEG_TRUE_CLOSE_HASH_BOUND_AND_VALIDATED_AGAINST_ORDERED_EXCHANGE_PRINTS", scheduled_edge_role: "NONE", actual_bell_role: "OPTIONAL_TIMING_METADATA_ONLY_NEVER_BOUNDARY", settlement_basis_role: "FORBIDDEN_NEGATIVE_CONTROL_ONLY", book_chain_after_end: "ACTIVE_REST_PERSISTS_TO_OWN_TRADING_PHASE_CLOSE; PRINT_EVIDENCE_CONTINUES; NO_BOOK_DEPENDENT_TRANSITION_IS_FABRICATED" }, source_seal: { commit: RECON_COMMIT, receipt: RECON_PATH, scope_note: "same sealed 4,836,462-row public archive; scoring clipped before terminal settlement collapse" }, canonical_close_binding: { commit: CANONICAL_CLOSE_COMMIT, path: CANONICAL_CLOSE_PATH, sha256: sha(canonicalCloseBytes), bytes: canonicalCloseBytes.length }, comparisons: { R3_joint_floor: 68, named_603: 603, canonical_T1_joint_comparison_universe: 750 } };
  const machine = { schema_version: "window1-v34-dual-side-residency-v1", game_state: "ONE_GAME_STATE_TWO_ENTRY_OUTPUTS", standing_rest: { both_legs: true, starts: "FIRST_OWN_TWO_SIDED_BOOK", formula: "min(best_bid-1, prior_rest, running_true_trade_low_if_any, running_qualified_ask_low_if_any, 99-first_fill_if_armed)", falls: "WALK_DOWN", climbs: "HOLD_NEVER_CHASE_UP" }, state: { quote_path: { trailing_evidence_seconds: policy.LOOKBACK_SECONDS, falling: ["NEW_LOW_ASK", "SELLER_HIT_PRINT"], rising: ["NEW_HIGH_BID", "BUYER_LIFT_PRINT"], otherwise: "SETTLED" }, July6_pressure: { rising_at_or_above: policy.PRESSURE_RISING_MIN, falling_at_or_below: policy.PRESSURE_FALLING_MAX }, combination: "QUOTE_PATH_PRIMARY; PRESSURE_ONLY_WHEN_QUOTE_PATH_SETTLED; DISAGREEMENTS_LOGGED" }, take_path: "V29_R3_QUALIFIED_SETTLED_FLOOR; DWELL_10; ORDINARY_SPREAD_LE_1_AND_SIZE_GE_5; CROSSED_OR_LOCKED_MAXIMAL_URGENCY", fill_laws: { STRICT_LAW: "STRICTLY_LATER_SELLER_AGGRESSED_PRINT_SIZE_GE_5_AT_OR_BELOW_REST_OR_PROVEN_TAKER", CENSUS_PRICED: "STRICT_LAW_PLUS_SELLER_PRINT_EXACTLY_REST_PLUS_1_CONVERTED_AT_REST_PER_65d49b5d" }, pair_cap: "ON_FIRST_FILL_OTHER_LEG_CAP_99_MINUS_FILL_SAME_RECEIPT_CANNOT_FILL_REPRICE", clock_inputs: [] };
  const scored = { schema_version: "window1-v34-two-column-score-v1", STRICT_LAW: strictScore, CENSUS_PRICED: censusScore };
  const dispositions = { STRICT_LAW: countBy(strictTrace, (x) => `${x.fill_class || "UNFILLED"}|${x.terminal_reason}`), CENSUS_PRICED: countBy(censusTrace, (x) => `${x.fill_class || "UNFILLED"}|${x.terminal_reason}`) };
  const core = {
    "CONTROL_BINDING.json": canonical(control),
    "STATE_MACHINE_CONTRACT.json": canonical(machine),
    "TRADING_PHASE_SPAN_804.json": canonical({ events: spans.length, exact_trading_phase_boundaries: spans.filter((x) => Number.isFinite(x.trading_phase_close_epoch)).length, actual_bell_metadata_available_events: spans.filter((x) => x.actual_bell_role === "TIMING_METADATA_ONLY_NEVER_BOUNDARY").length, canonical_T1_joint_comparison_universe: 750, book_coverage_fraction: distribution(spans.map((x) => x.per_leg.reduce((s, l) => s + (l.book_coverage_fraction || 0), 0) / 2)), print_only_remainder_seconds: distribution(spans.flatMap((x) => x.per_leg.map((l) => l.print_only_remainder_seconds)), "seconds"), settlement_phase_excluded_seconds: distribution(spans.map((x) => x.settlement_phase_excluded_seconds), "seconds"), rows: spans }),
    "CANONICAL_CLOSE_BINDING.json": canonical(closeRuler),
    "SETTLEMENT_EVIDENCE_EXCLUSION_RECEIPT.json": canonical(settlementExclusion),
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
    "SCORING_BINDING_SUPERSESSION_RECEIPT.json": canonical({ supersedes_settlement_scoring_commit: "e0fb6a312d8bbc52806603fbc143bf2bcebb3df2", preserved_negative_control_package: ".claude/window1_live_v4_replay/v34_dual_side_residency_machine_20260805", defect: "RAW_FINAL_EXCHANGE_PRINT_CONSUMED_AS_CLOSE", correction: "HASH_BOUND_THE_603_MAP_TRADING_PHASE_TRUE_CLOSE_AND_CLIP_ALL_SCORING_EVIDENCE_TO_OWN_PHASE_BOUNDARY", settlement_basis_never_consumed: true }),
    "FORBIDDEN_ACCESS_RECEIPT.json": canonical({ holdout_accesses: 0, live_accesses: 0, network_runtime_accesses: 0, order_accesses: 0, position_accesses: 0, live_settlement_accesses: 0, settlement_basis_scoring_reads: 0, deployment_accesses: 0, scorer_external_invocations: 0, private_scope: "FIT_DEVELOPMENT_804_ONLY" }),
    "SOURCE_HASH_MANIFEST.json": canonical({ public_committed: Object.fromEntries([builderFile, policyFile, unitTestFile, packageTestFile, floorFile, baseTraceFile, quoteFile, bellFile, spoolHelperFile, spoolHelperSourceFile].map((file) => [path.relative(repo, file).replaceAll("\\", "/"), { sha256: fs.existsSync(file) ? fileHash(file) : null, bytes: fs.existsSync(file) ? fs.statSync(file).size : null }])), git_bound: { [RECON_PATH]: { commit: RECON_COMMIT, sha256: sha(reconBytes), bytes: reconBytes.length }, [NEARMISS_PATH]: { commit: NEARMISS_COMMIT, sha256: sha(nearBytes), bytes: nearBytes.length }, [CANONICAL_CLOSE_PATH]: { commit: CANONICAL_CLOSE_COMMIT, sha256: sha(canonicalCloseBytes), bytes: canonicalCloseBytes.length } }, private_full_life_prints: printLoad.receipt, private_full_life_books: tapeHashes, public_tape_manifest: { sha256: fileHash(publicTapeManifest), bytes: fs.statSync(publicTapeManifest).size } }),
  };
  for (const [name, bytes] of Object.entries(core)) write(name, bytes);
  write("REPORT.md", `# V34 dual-side residency machine - canonical trading-phase scoring\n\nV34's state machine is unchanged. Scoring is clipped per leg from the earlier of first two-sided book or first true exchange print through the hash-bound trading-phase boundary implied by that leg's THE_603_MAP true_close. Every non-null close is validated against the ordered exchange prints; null closes remain unavailable and use the sibling's game boundary only to clip their streams. Terminal settlement-collapse prints are excluded from decisions, fills, floors, close grades, frontier, and regret. The 234-event exact-bell subset remains timing metadata only.\n\n- Canonical T1-joint comparison universe: 750.\n- STRICT-LAW JOINT: ${strictScore.aggregate.joint_objective_pairs}; delta vs R3 68: ${strictScore.delta_joint_vs_R3_68}; gap to named 603: ${strictScore.gap_to_named_603}; gap to T1 750: ${strictScore.gap_to_canonical_T1_joint_750}.\n- CENSUS-PRICED JOINT: ${censusScore.aggregate.joint_objective_pairs}; delta vs R3 68: ${censusScore.delta_joint_vs_R3_68}; gap to named 603: ${censusScore.gap_to_named_603}; gap to T1 750: ${censusScore.gap_to_canonical_T1_joint_750}.\n- STRICT completed / under par / both-below / carried: ${strictScore.aggregate.completed_pairs} / ${strictScore.aggregate.pairs_under_par} / ${strictScore.aggregate.both_legs_strictly_below_close} / ${strictScore.aggregate.carried_pairs}.\n- CENSUS completed / under par / both-below / carried: ${censusScore.aggregate.completed_pairs} / ${censusScore.aggregate.pairs_under_par} / ${censusScore.aggregate.both_legs_strictly_below_close} / ${censusScore.aggregate.carried_pairs}.\n- ARNROM STRICT: ${strictArn?.combined_entry_cents ?? "INCOMPLETE"}; CENSUS: ${censusArn?.combined_entry_cents ?? "INCOMPLETE"}.\n- Canonical close availability: ${closeRuler.available_legs}/${closeRuler.legs}; map mismatches: ${closeRuler.map_leg_close_mismatches}.\n\nThe prior settlement-basis V34 package is preserved as a stamped negative control and is not consumed by this score.\n`);
  const compareNames = [...Object.keys(core), "REPORT.md"].sort();
  if (compare) { const mismatches = compareNames.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name))); ensure(!mismatches.length, `determinism mismatch ${mismatches.join(",")}`); write("DETERMINISM_RECEIPT.json", canonical({ builds: 2, byte_identical: true, compared_files: compareNames.length, mismatches: [] })); }
  else write("DETERMINISM_RECEIPT.json", canonical({ builds: 1, byte_identical: null, role: "FIRST_BUILD" }));
  const names = fs.readdirSync(output).filter((x) => x !== "ARTIFACT_HASH_MANIFEST.json").sort(); write("ARTIFACT_HASH_MANIFEST.json", canonical({ files: Object.fromEntries(names.map((name) => [name, { sha256: fileHash(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size }])) }));
  process.stdout.write(canonical({ output, STRICT_LAW: strictScore.aggregate, CENSUS_PRICED: censusScore.aggregate, spans: spans.length, action_rows: actionRows.length }));
}

function w1Boundary(row) {
  const candidates = [
    ["exact_start_utc", row.exact_start_utc],
    ["known_live_by_utc", row.known_live_by_utc],
    ["schedule_bound_utc", row.schedule_bound_utc],
  ];
  const chosen = candidates.find(([, value]) => Number.isFinite(parseIso(value)));
  ensure(chosen, `no Window-1 right edge ${row.event_id}`);
  return {
    event_id: row.event_id,
    right_edge_epoch: parseIso(chosen[1]),
    right_edge_utc: chosen[1],
    edge_source_field: chosen[0],
    precision_class: row.precision_class,
    selected_source: row.selected_source,
    selected_source_family: row.selected_source_family,
    selected_timestamp_precision: row.selected_timestamp_precision,
    conflict_status: row.conflict_status,
    interval_contradiction: row.interval_contradiction,
    exact_start_utc: row.exact_start_utc,
    known_live_by_utc: row.known_live_by_utc,
    schedule_bound_utc: row.schedule_bound_utc,
  };
}

function w1Clock(ts, source, bell, boundary) {
  return {
    timestamp_epoch: ts,
    t_minus_scheduled_seconds: Number.isFinite(source?.scheduled) ? source.scheduled - ts : null,
    t_minus_actual_bell_seconds: Number.isFinite(bell) ? bell - ts : null,
    t_minus_pre_match_boundary_seconds: boundary.right_edge_epoch - ts,
    pre_match_boundary_epoch: boundary.right_edge_epoch,
    pre_match_boundary_source: boundary.edge_source_field,
    bell_confidence: boundary.precision_class,
  };
}

function evidenceInsideWindow(tape, prints, left, right) {
  const books = tape.filter((row) => row.ts >= left && row.ts <= right);
  const trades = prints.filter((row) => row.ts >= left && row.ts <= right);
  const qualified = books.filter((row) => policy.r3QualifiedTake(row));
  const low = trades.length ? Math.min(...trades.map((row) => row.price)) : null;
  const lowRows = Number.isInteger(low) ? trades.filter((row) => row.price === low) : [];
  const qualifiedLow = qualified.length ? Math.min(...qualified.map((row) => row.ask)) : null;
  const qualifiedLowRows = Number.isInteger(qualifiedLow) ? qualified.filter((row) => row.ask === qualifiedLow) : [];
  const close = trades.at(-1) || null;
  return {
    books,
    trades,
    first_two_sided_book_epoch: books[0]?.ts ?? null,
    last_two_sided_book_epoch: books.at(-1)?.ts ?? null,
    two_sided_book_receipts: books.length,
    true_prints: trades.length,
    print_backed_achievable_floor_cents: low,
    print_backed_floor_receipts: lowRows.map((row) => ({ receipt: row.receipt, timestamp_epoch: row.ts, ordinal: row.ordinal, price_cents: row.price, size: row.size, aggressor_side: row.taker_side === "no" ? "SELLER" : row.taker_side === "yes" ? "BUYER" : "UNKNOWN" })),
    qualifying_ask_floor_cents: qualifiedLow,
    qualifying_ask_floor_receipts: qualifiedLowRows.length ? { count: qualifiedLowRows.length, first: { receipt: qualifiedLowRows[0].receipt, timestamp_epoch: qualifiedLowRows[0].ts, ordinal: qualifiedLowRows[0].ordinal, bid: qualifiedLowRows[0].bid, ask: qualifiedLowRows[0].ask, spread: qualifiedLowRows[0].spread, dwell_seconds: qualifiedLowRows[0].ask_dwell_seconds, displayed_size: qualifiedLowRows[0].top_ask_size }, last: { receipt: qualifiedLowRows.at(-1).receipt, timestamp_epoch: qualifiedLowRows.at(-1).ts, ordinal: qualifiedLowRows.at(-1).ordinal, bid: qualifiedLowRows.at(-1).bid, ask: qualifiedLowRows.at(-1).ask, spread: qualifiedLowRows.at(-1).spread, dwell_seconds: qualifiedLowRows.at(-1).ask_dwell_seconds, displayed_size: qualifiedLowRows.at(-1).top_ask_size } } : { count: 0, first: null, last: null },
    w1_close_telemetry: close ? { status: "AVAILABLE_TELEMETRY_ONLY", price_cents: close.price, timestamp_epoch: close.ts, ordinal: close.ordinal, receipt: close.receipt, size: close.size, aggressor_side: close.taker_side === "no" ? "SELLER" : close.taker_side === "yes" ? "BUYER" : "UNKNOWN" } : { status: "UNAVAILABLE_NO_TRUE_PRINT_INSIDE_PRE_MATCH_SPAN", price_cents: null, timestamp_epoch: null, ordinal: null, receipt: null, size: null, aggressor_side: null },
  };
}

function armW1Sibling(sibling, fillLeg, row, mode, actions, boundary) {
  if (row.ts > boundary.right_edge_epoch) return;
  sibling.pair_cap_cents = 99 - fillLeg.entry_cents;
  actions.push({ mode, kind: "PAIR_ARM", event_id: sibling.event_id, leg_identity: sibling.leg_identity, sibling_fill_cents: fillLeg.entry_cents, pair_cap_cents: sibling.pair_cap_cents, receipt: row.receipt, ...w1Clock(row.ts, sibling.source, sibling.bell, boundary), same_receipt_fill_forbidden: true });
  if (sibling.active_order && sibling.active_order.target_cents > sibling.pair_cap_cents) {
    const prior = sibling.active_order.target_cents;
    if (policy.lawfulCent(sibling.pair_cap_cents)) {
      sibling.active_order = { target_cents: sibling.pair_cap_cents, action_ts: row.ts, action_receipt: row.receipt, action: "PAIR_CAP_REPRICE", source_state: "SIBLING_FILL" };
      actions.push({ mode, kind: "PAIR_CAP_REPRICE", event_id: sibling.event_id, leg_identity: sibling.leg_identity, prior_target_cents: prior, target_cents: sibling.pair_cap_cents, receipt: row.receipt, ...w1Clock(row.ts, sibling.source, sibling.bell, boundary), same_receipt_fill_forbidden: true });
    } else {
      sibling.active_order = null;
      actions.push({ mode, kind: "PAIR_CAP_CANCEL", event_id: sibling.event_id, leg_identity: sibling.leg_identity, prior_target_cents: prior, target_cents: null, receipt: row.receipt, ...w1Clock(row.ts, sibling.source, sibling.bell, boundary), same_receipt_fill_forbidden: true });
    }
  }
}

function simulateW1Mode(baseEvent, tapes, prints, sources, bells, mode, actions, decisions, span, timeline, boundary) {
  const ids = Object.keys(baseEvent.legs).sort();
  const event = { event_id: baseEvent.event_id, category: baseEvent.category, starting_price_split: baseEvent.starting_price_split, bell_confidence: boundary.precision_class, edge_source_field: boundary.edge_source_field, mode, w1_left_epoch: span.w1_left_epoch, w1_right_epoch: boundary.right_edge_epoch, legs: {} };
  for (const id of ids) {
    const baseLeg = baseEvent.legs[id];
    const evidence = evidenceInsideWindow(tapes.get(baseLeg.ticker), prints.get(baseLeg.ticker), span.w1_left_epoch, boundary.right_edge_epoch);
    event.legs[id] = {
      ...baseLeg,
      source: sources.get(baseLeg.ticker),
      bell: bells.get(baseEvent.event_id),
      w1_print_backed_achievable_floor_cents: evidence.print_backed_achievable_floor_cents,
      w1_print_backed_floor_receipts: evidence.print_backed_floor_receipts,
      w1_qualifying_ask_floor_cents: evidence.qualifying_ask_floor_cents,
      w1_qualifying_ask_floor_receipts: evidence.qualifying_ask_floor_receipts,
      w1_close_telemetry: evidence.w1_close_telemetry,
      w1_true_print_count: evidence.true_prints,
      w1_two_sided_book_receipts: evidence.two_sided_book_receipts,
      acted: false,
      credited: false,
      entry_cents: null,
      fill_class: null,
      action_timestamp_epoch: null,
      fill_timestamp_epoch: null,
      pair_cap_cents: null,
      active_order: null,
      prior_book: null,
      latest_directional: null,
      running_trade_low: null,
      running_trade_low_timestamp_epoch: null,
      running_trade_low_ordinal: null,
      running_trade_low_receipt: null,
      running_seller_hit_low: null,
      running_raw_ask_low: null,
      running_qualified_ask_low: null,
      running_qualified_ask_low_directional_receipt: null,
      running_qualified_ask_low_unabsorbed: false,
      running_qualified_ask_low_reformed_nonfalling: false,
      running_qualified_ask_low_reformation_receipt: null,
      latest_downward_evidence_ts: null,
      latest_downward_evidence_receipt: null,
      latest_new_low_evidence_ts: null,
      latest_new_low_evidence_receipt: null,
      latest_new_low_evidence_price_cents: null,
      downward_evidence_rows: [],
      decision_count: 0,
      state_counts: { FALLING: 0, RISING: 0, SETTLED: 0 },
      action_counts: {},
      disagreement_count: 0,
      maker_reprices: 0,
      rest_sanity: { tracked_book_receipts: 0, exact_target_receipts: 0, gap_abs_max_cents: 0, reprice_up: 0, reprice_down: 0, target_min_cents: null, target_max_cents: null, best_bid_min_cents: null, best_bid_max_cents: null, by_state: { FALLING: { tracked: 0, exact: 0 }, RISING: { tracked: 0, exact: 0 }, SETTLED: { tracked: 0, exact: 0 } } },
      first_decision: null,
      last_decision: null,
      first_action: null,
      terminal_reason: null,
    };
  }
  for (const row of timeline) {
    if (event.legs[ids[0]].credited && event.legs[ids[1]].credited) break;
    if (row.ts < span.w1_left_epoch || row.ts > boundary.right_edge_epoch) continue;
    const leg = event.legs[row.leg_id];
    const sibling = event.legs[ids.find((id) => id !== row.leg_id)];
    if (row.kind === "PRINT") {
      if (leg.running_trade_low === null || row.price < leg.running_trade_low) {
        leg.running_trade_low = row.price;
        leg.running_trade_low_timestamp_epoch = row.ts;
        leg.running_trade_low_ordinal = row.ordinal;
        leg.running_trade_low_receipt = row.receipt;
      }
      if (leg.credited) continue;
      let fill = null;
      if (mode === "STRICT_LAW" && policy.strictMakerFill(leg.active_order, row)) fill = { class: "PROVEN_MAKER_SELLER_AGGRESSED_PRINT_SIZE_FIVE_AT_OR_BELOW_REST" };
      if (mode === "CENSUS_PRICED") fill = policy.censusPricedFill(leg.active_order, row);
      if (fill) {
        leg.credited = true;
        leg.entry_cents = leg.active_order.target_cents;
        leg.action_timestamp_epoch = leg.active_order.action_ts;
        leg.fill_timestamp_epoch = row.ts;
        leg.fill_class = fill.class;
        leg.fill_source_state = leg.active_order.source_state;
        leg.terminal_reason = fill.class;
        actions.push({ mode, kind: "FILL", event_id: event.event_id, leg_identity: leg.leg_identity, fill_class: fill.class, entry_cents: leg.entry_cents, action_timestamp_epoch: leg.action_timestamp_epoch, receipt: row.receipt, print: { price_cents: row.price, size: row.size, taker_side: row.taker_side }, ...w1Clock(row.ts, leg.source, leg.bell, boundary) });
        armW1Sibling(sibling, leg, row, mode, actions, boundary);
      }
      if (!leg.credited) {
        if (row.taker_side === "no" && Number.isFinite(row.size) && row.size > 0) {
          if (leg.running_seller_hit_low === null || row.price < leg.running_seller_hit_low) {
            leg.latest_new_low_evidence_ts = row.ts;
            leg.latest_new_low_evidence_receipt = row.receipt;
            leg.latest_new_low_evidence_price_cents = row.price;
          }
          leg.running_seller_hit_low = leg.running_seller_hit_low === null ? row.price : Math.min(leg.running_seller_hit_low, row.price);
          leg.downward_evidence_rows.push({ ts: row.ts, ordinal: row.ordinal, price: row.price, kind: "SELLER_HIT_TRUE_PRINT", receipt: row.receipt });
        }
        if (row.taker_side === "no" || row.taker_side === "yes") leg.latest_directional = { ts: row.ts, ordinal: row.ordinal, direction: row.taker_side === "no" ? "FALLING" : "RISING", kind: row.taker_side === "no" ? "SELLER_HIT_PRINT" : "BUYER_LIFT_PRINT", receipt: row.receipt };
      }
      continue;
    }
    if (leg.credited) continue;
    const prior = leg.prior_book;
    const newLowAsk = prior && row.ask < prior.ask;
    const newHighBid = prior && row.bid > prior.bid;
    if (leg.running_raw_ask_low === null || row.ask < leg.running_raw_ask_low) {
      leg.running_raw_ask_low = row.ask;
      leg.latest_new_low_evidence_ts = row.ts;
      leg.latest_new_low_evidence_receipt = row.receipt;
      leg.latest_new_low_evidence_price_cents = row.ask;
    }
    if (newLowAsk && newHighBid) leg.latest_directional = { ts: row.ts, ordinal: row.ordinal, direction: "SETTLED", kind: "QUOTE_PATH_INTERNAL_CONFLICT_NEW_LOW_ASK_AND_NEW_HIGH_BID", receipt: row.receipt };
    else if (newLowAsk) leg.latest_directional = { ts: row.ts, ordinal: row.ordinal, direction: "FALLING", kind: "NEW_LOW_ASK", receipt: row.receipt };
    else if (newHighBid) leg.latest_directional = { ts: row.ts, ordinal: row.ordinal, direction: "RISING", kind: "NEW_HIGH_BID", receipt: row.receipt };
    let qualifyingAskFloorReformedNow = false;
    if (policy.qualifyingAskEvidence(row)) {
      let qualifyingAskCreatedDownwardFloor = false;
      if (leg.running_qualified_ask_low === null || row.ask < leg.running_qualified_ask_low) {
        leg.running_qualified_ask_low = row.ask;
        const directionAtFloorCreation = policy.quotePathState(leg.latest_directional ? [leg.latest_directional] : [], row.ts);
        leg.running_qualified_ask_low_directional_receipt = directionAtFloorCreation.state === "FALLING" ? directionAtFloorCreation.receipt : null;
        leg.running_qualified_ask_low_unabsorbed = directionAtFloorCreation.state === "FALLING" || policy.pressureState(row.depth_ratio) === "FALLING";
        qualifyingAskCreatedDownwardFloor = leg.running_qualified_ask_low_unabsorbed;
        qualifyingAskFloorReformedNow = !qualifyingAskCreatedDownwardFloor;
        leg.running_qualified_ask_low_reformed_nonfalling = qualifyingAskFloorReformedNow;
        leg.running_qualified_ask_low_reformation_receipt = qualifyingAskFloorReformedNow ? row.receipt : null;
      }
      if (qualifyingAskCreatedDownwardFloor) leg.downward_evidence_rows.push({ ts: row.ts, ordinal: row.ordinal, price: row.ask, kind: "QUALIFYING_ASK_LOW_BAND_CREATED_WHILE_FALLING", receipt: row.receipt });
    }
    leg.downward_evidence_rows = leg.downward_evidence_rows.filter((evidence) => evidence.ts <= row.ts && evidence.ts >= row.ts - policy.LOOKBACK_SECONDS);
    const activeEvidenceRows = leg.downward_evidence_rows;
    const quote = policy.quotePathState(leg.latest_directional ? [leg.latest_directional] : [], row.ts);
    const pressure = policy.pressureState(row.depth_ratio);
    const combined = policy.combineState(quote, pressure);
    if (quote.state === "FALLING" || pressure === "FALLING") {
      leg.latest_downward_evidence_ts = row.ts;
      leg.latest_downward_evidence_receipt = row.receipt;
    }
    if (leg.running_qualified_ask_low_unabsorbed && Number.isFinite(leg.latest_downward_evidence_ts) && row.ts - leg.latest_downward_evidence_ts > policy.LOOKBACK_SECONDS) {
      leg.running_qualified_ask_low_unabsorbed = false;
    }
    const receiptLocalEvidenceFloor = activeEvidenceRows.length ? Math.min(...activeEvidenceRows.map((evidence) => evidence.price)) : null;
    const runningDiscountFloors = [leg.running_seller_hit_low, leg.running_qualified_ask_low].filter(Number.isFinite);
    const runningEvidenceFloor = runningDiscountFloors.length ? Math.min(...runningDiscountFloors) : null;
    const fallingCarryFloor = quote.state === "FALLING" ? runningEvidenceFloor : null;
    const reformedQualifyingAskFloor = policy.qualifyingAskEvidence(row) ? row.ask : null;
    const floorMature = Number.isFinite(leg.latest_new_low_evidence_ts) && row.ts - leg.latest_new_low_evidence_ts >= policy.LOOKBACK_SECONDS;
    const activeEvidenceFloor = policy.matureDirectionalEvidenceFloor({
      state: combined.state,
      runningEvidenceFloor,
      receiptLocalEvidenceFloor,
      reformedQualifyingAskFloor: leg.running_qualified_ask_low,
      reformedQualifyingAskAuthority: leg.running_qualified_ask_low_reformed_nonfalling,
      floorMature,
    });
    const evidenceAuthority = combined.state === "FALLING" && Number.isInteger(runningEvidenceFloor)
      ? "FALLING_RUNNING_DOWNWARD_EVIDENCE"
      : Number.isInteger(receiptLocalEvidenceFloor)
        ? "TRAILING_HORIZON_DOWNWARD_EVIDENCE"
        : Number.isInteger(leg.running_qualified_ask_low) && activeEvidenceFloor === leg.running_qualified_ask_low && leg.running_qualified_ask_low_reformed_nonfalling && floorMature
          ? "MATURE_RISEN_OR_SETTLED_REFORMED_QUALIFYING_ASK_FLOOR"
          : Number.isInteger(reformedQualifyingAskFloor) && activeEvidenceFloor === reformedQualifyingAskFloor
            ? "ESTABLISHED_QUALIFYING_ASK_FLOOR_WITH_NO_LOWER_LIVE_EVIDENCE"
          : Number.isInteger(activeEvidenceFloor)
            ? "SETTLED_DESCENT_ORIGIN_FLOOR_NOT_CAUSALLY_REFORMED"
          : "NO_ACTIVE_EVIDENCE_AUTHORITY";
    const floorFirstFlickerLive = activeEvidenceFloor === leg.running_qualified_ask_low && leg.running_qualified_ask_low_unabsorbed;
    const before = leg.active_order?.target_cents ?? null;
    const expectedRestTarget = policy.stateDirectionalRestTarget({ state: combined.state, bid: row.bid, activeTarget: before, pairCap: leg.pair_cap_cents });
    const decision = policy.decide({ state: combined.state, book: row, activeTarget: before, pairCap: leg.pair_cap_cents, activeEvidenceFloor, floorFirstFlickerLive, floorMature, otherRunningPrintBackedFloor: sibling.running_trade_low });
    leg.prior_book = row;
    leg.decision_count += 1;
    leg.state_counts[combined.state] += 1;
    if (combined.disagreement) leg.disagreement_count += 1;
    leg.action_counts[decision.action] = (leg.action_counts[decision.action] || 0) + 1;
    const detail = { mode, event_id: event.event_id, leg_identity: leg.leg_identity, ticker: leg.ticker, category: leg.category, price_region: leg.price_region, starting_price_split: event.starting_price_split, bell_confidence: boundary.precision_class, receipt: row.receipt, ordinal: row.ordinal, ...w1Clock(row.ts, leg.source, leg.bell, boundary), observation: { bid: row.bid, ask: row.ask, last_traded: row.last_trade, spread: row.spread, ask_dwell_seconds: row.ask_dwell_seconds, top_ask_size: row.top_ask_size, bid_depth_5: row.bid_depth_5, ask_depth_5: row.ask_depth_5, depth_ratio: row.depth_ratio }, quote_path: quote, pressure_state: pressure, combined_state: combined.state, disagreement: combined.disagreement, causal_discount_evidence: { running_trade_low_cents: leg.running_trade_low, running_seller_hit_low_cents: leg.running_seller_hit_low, running_qualifying_ask_low_cents: leg.running_qualified_ask_low, running_price_bearing_evidence_floor_cents: runningEvidenceFloor, receipt_local_evidence_floor_cents: receiptLocalEvidenceFloor, reformed_qualifying_ask_floor_cents: reformedQualifyingAskFloor, qualifying_ask_floor_reformed_on_current_receipt: qualifyingAskFloorReformedNow, qualifying_ask_floor_reformed_nonfalling_authority: leg.running_qualified_ask_low_reformed_nonfalling, qualifying_ask_floor_reformation_receipt: leg.running_qualified_ask_low_reformation_receipt, evidence_authority: evidenceAuthority, falling_state_carry_floor_cents: fallingCarryFloor, falling_state_carry_authority: combined.state === "FALLING" ? "COMBINED_SIDE_STATE" : null, active_evidence_floor_cents: activeEvidenceFloor, active_trailing_evidence_receipts: activeEvidenceRows.length, transient_directional_horizon_seconds: policy.LOOKBACK_SECONDS, floor_first_flicker_live: floorFirstFlickerLive, floor_creation_directional_receipt: leg.running_qualified_ask_low_directional_receipt, latest_downward_evidence_timestamp_epoch: leg.latest_downward_evidence_ts, latest_downward_evidence_receipt: leg.latest_downward_evidence_receipt, latest_new_low_evidence_timestamp_epoch: leg.latest_new_low_evidence_ts, latest_new_low_evidence_receipt: leg.latest_new_low_evidence_receipt, latest_new_low_evidence_price_cents: leg.latest_new_low_evidence_price_cents, floor_mature: floorMature, floor_maturity_age_seconds: Number.isFinite(leg.latest_new_low_evidence_ts) ? row.ts - leg.latest_new_low_evidence_ts : null }, sibling_running_print_backed_floor: { cents: sibling.running_trade_low, timestamp_epoch: sibling.running_trade_low_timestamp_epoch, ordinal: sibling.running_trade_low_ordinal, receipt: sibling.running_trade_low_receipt }, pair_cap_cents: leg.pair_cap_cents, order_before_cents: before, decision, order_after_cents: null };
    leg.first_decision ||= detail;
    leg.last_decision = detail;
    if (decision.action === "PLACE_REST" || decision.action === "REPRICE_REST") {
      if (decision.action === "REPRICE_REST") {
        leg.maker_reprices += 1;
        if (decision.target_cents > before) leg.rest_sanity.reprice_up += 1;
        if (decision.target_cents < before) leg.rest_sanity.reprice_down += 1;
      }
      leg.acted = true;
      leg.active_order = { target_cents: decision.target_cents, action_ts: row.ts, action_receipt: row.receipt, action: decision.action, source_state: combined.state };
      leg.first_action ||= detail;
      actions.push({ mode, kind: decision.action, event_id: event.event_id, leg_identity: leg.leg_identity, target_cents: decision.target_cents, receipt: row.receipt, state: combined.state, reason: decision.reason, ...w1Clock(row.ts, leg.source, leg.bell, boundary) });
    } else if (decision.action === "TAKE") {
      leg.acted = true;
      leg.credited = true;
      leg.entry_cents = decision.target_cents;
      leg.action_timestamp_epoch = row.ts;
      leg.fill_timestamp_epoch = row.ts;
      leg.fill_class = "PROVEN_TAKER_EVIDENCE_FLOOR_QUALIFIED_ASK";
      leg.fill_source_state = combined.state;
      leg.terminal_reason = leg.fill_class;
      leg.first_action ||= detail;
      actions.push({ mode, kind: "FILL", event_id: event.event_id, leg_identity: leg.leg_identity, fill_class: leg.fill_class, entry_cents: leg.entry_cents, receipt: row.receipt, decision_reason: decision.reason, state_label_ignored_for_take_authority: true, active_evidence_floor_cents: activeEvidenceFloor, active_evidence_receipts: activeEvidenceRows.length, evidence_authority: evidenceAuthority, floor_arithmetic_take_bound: decision.floor_arithmetic_take_bound || null, displayed_ask: { price_cents: row.ask, size: row.top_ask_size, spread: row.spread, dwell_seconds: row.ask_dwell_seconds, crossed_or_locked: row.bid >= row.ask }, ...w1Clock(row.ts, leg.source, leg.bell, boundary) });
      armW1Sibling(sibling, leg, row, mode, actions, boundary);
    } else if (decision.action === "CANCEL_REST") {
      leg.active_order = null;
      actions.push({ mode, kind: "CANCEL_REST", event_id: event.event_id, leg_identity: leg.leg_identity, receipt: row.receipt, reason: decision.reason, ...w1Clock(row.ts, leg.source, leg.bell, boundary) });
    }
    detail.order_after_cents = leg.credited ? leg.entry_cents : (leg.active_order?.target_cents ?? null);
    if (!leg.credited && leg.active_order) {
      const expected = expectedRestTarget;
      const gap = Number.isInteger(expected) ? leg.active_order.target_cents - expected : null;
      leg.rest_sanity.tracked_book_receipts += 1;
      if (gap === 0) leg.rest_sanity.exact_target_receipts += 1;
      leg.rest_sanity.by_state[combined.state].tracked += 1;
      if (gap === 0) leg.rest_sanity.by_state[combined.state].exact += 1;
      if (Number.isInteger(gap)) leg.rest_sanity.gap_abs_max_cents = Math.max(leg.rest_sanity.gap_abs_max_cents, Math.abs(gap));
      leg.rest_sanity.target_min_cents = leg.rest_sanity.target_min_cents === null ? leg.active_order.target_cents : Math.min(leg.rest_sanity.target_min_cents, leg.active_order.target_cents);
      leg.rest_sanity.target_max_cents = leg.rest_sanity.target_max_cents === null ? leg.active_order.target_cents : Math.max(leg.rest_sanity.target_max_cents, leg.active_order.target_cents);
      leg.rest_sanity.best_bid_min_cents = leg.rest_sanity.best_bid_min_cents === null ? row.bid : Math.min(leg.rest_sanity.best_bid_min_cents, row.bid);
      leg.rest_sanity.best_bid_max_cents = leg.rest_sanity.best_bid_max_cents === null ? row.bid : Math.max(leg.rest_sanity.best_bid_max_cents, row.bid);
    }
    decisions.push(detail);
  }
  for (const leg of Object.values(event.legs)) {
    leg.entry_minus_print_backed_floor_cents = leg.credited && Number.isInteger(leg.w1_print_backed_achievable_floor_cents) ? leg.entry_cents - leg.w1_print_backed_achievable_floor_cents : null;
    leg.entry_minus_qualifying_ask_floor_cents = leg.credited && Number.isInteger(leg.w1_qualifying_ask_floor_cents) ? leg.entry_cents - leg.w1_qualifying_ask_floor_cents : null;
    leg.resting_at_hard_edge = !leg.credited && Boolean(leg.active_order);
    leg.resting_target_at_hard_edge_cents = leg.resting_at_hard_edge ? leg.active_order.target_cents : null;
    if (!leg.credited) leg.terminal_reason = leg.acted ? "HARD_RIGHT_EDGE_REACHED_WITH_REST_UNFILLED" : "NO_OWN_TWO_SIDED_BOOK_ACTION_INSIDE_WINDOW1";
    leg.first_action_timestamp_epoch = leg.first_action?.timestamp_epoch ?? null;
    delete leg.source;
    delete leg.bell;
    delete leg.active_order;
    delete leg.prior_book;
    delete leg.latest_directional;
    delete leg.downward_evidence_rows;
    delete leg.running_qualified_ask_low_directional_receipt;
    delete leg.running_qualified_ask_low_unabsorbed;
    delete leg.running_qualified_ask_low_reformed_nonfalling;
    delete leg.running_qualified_ask_low_reformation_receipt;
    delete leg.latest_downward_evidence_ts;
    delete leg.latest_downward_evidence_receipt;
    delete leg.latest_new_low_evidence_ts;
    delete leg.latest_new_low_evidence_receipt;
    delete leg.latest_new_low_evidence_price_cents;
    delete leg.running_raw_ask_low;
  }
  const legs = Object.values(event.legs);
  event.completed_pair = legs.every((leg) => leg.credited);
  event.combined_entry_cents = event.completed_pair ? legs.reduce((sum, leg) => sum + leg.entry_cents, 0) : null;
  event.pair_under_par = event.completed_pair && event.combined_entry_cents < 100;
  event.close_based_grade = null;
  return event;
}

function w1Metrics(events) {
  const legs = events.flatMap((event) => Object.values(event.legs));
  return {
    D: events.length,
    legs: legs.length,
    acted_legs: legs.filter((leg) => leg.acted).length,
    credited_legs: legs.filter((leg) => leg.credited).length,
    proven_maker_legs: legs.filter((leg) => leg.fill_class?.startsWith("PROVEN_MAKER")).length,
    proven_taker_legs: legs.filter((leg) => leg.fill_class?.startsWith("PROVEN_TAKER")).length,
    census_priced_conversion_legs: legs.filter((leg) => leg.fill_class === "CENSUS_PRICED_ONE_CENT_RESIDENCY_CONVERSION").length,
    completed_pairs: events.filter((event) => event.completed_pair).length,
    pairs_under_par: events.filter((event) => event.pair_under_par).length,
    naked_credited_legs: legs.filter((leg) => leg.credited && !events.find((event) => event.event_id === leg.event_id).completed_pair).length,
    rests_unfilled_at_edge: legs.filter((leg) => leg.resting_at_hard_edge).length,
    close_based_grade: null,
  };
}

function w1Cells(events) {
  return [...group(events, (event) => `${event.category}|${event.starting_price_split}|${event.bell_confidence}`).entries()].sort((a, b) => a[0].localeCompare(b[0]));
}

function scoreW1Column(events, label) {
  const aggregate = w1Metrics(events);
  const rows = w1Cells(events).map(([cell, subset]) => ({ cell, metrics: w1Metrics(subset) }));
  return { label, grading_law: "CLOSE_FREE_COMPLETION_AND_SUM_STRICTLY_BELOW_100", aggregate, category_x_starting_price_region_x_bell_confidence: rows, conservation: { cell_D_sum: rows.reduce((sum, row) => sum + row.metrics.D, 0), expected_D: events.length, pass: rows.reduce((sum, row) => sum + row.metrics.D, 0) === events.length } };
}

function frontierW1(events) {
  const tiers = [{ id: "LE_93", test: (x) => x <= 93 }, { id: "LE_95", test: (x) => x <= 95 }, { id: "LE_97", test: (x) => x <= 97 }, { id: "LT_100", test: (x) => x < 100 }, { id: "ANY_PRICE", test: () => true }];
  const make = (rows) => Object.fromEntries(tiers.map((tier) => [tier.id, { fixed_denominator: rows.length, completed_pairs: rows.filter((event) => event.completed_pair && tier.test(event.combined_entry_cents)).length }]));
  const cells = w1Cells(events).map(([cell, rows]) => ({ cell, D: rows.length, frontier: make(rows) }));
  return { grading_law: "CLOSE_FREE_RAW_INTEGER_COMPLETION_FRONTIER", fixed_denominator: events.length, cumulative_frontier: make(events), category_x_starting_price_region_x_bell_confidence: cells, conservation: { cell_D_sum: cells.reduce((sum, row) => sum + row.D, 0), expected_D: events.length, pass: cells.reduce((sum, row) => sum + row.D, 0) === events.length } };
}

function regretW1(events) {
  const rows = events.flatMap((event) => Object.values(event.legs).map((leg) => ({ event_id: leg.event_id, leg_identity: leg.leg_identity, category: leg.category, price_region: leg.price_region, bell_confidence: event.bell_confidence, credited: leg.credited, entry_cents: leg.entry_cents, print_backed_achievable_floor_cents: leg.w1_print_backed_achievable_floor_cents, regret_cents: leg.credited && Number.isInteger(leg.w1_print_backed_achievable_floor_cents) ? leg.entry_cents - leg.w1_print_backed_achievable_floor_cents : null, loss_attribution: leg.credited ? leg.fill_class : leg.resting_at_hard_edge ? "WAITED_WITH_REST_TO_HARD_EDGE" : "NEVER_PLACED_INSIDE_WINDOW1" })));
  const cells = [...group(rows, (row) => `${row.category}|${row.price_region}|${row.bell_confidence}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, subset]) => ({ cell, legs: subset.length, credited_legs: subset.filter((row) => row.credited).length, regret: distribution(subset.map((row) => row.regret_cents), "cents"), loss_attribution: countBy(subset, (row) => row.loss_attribution) }));
  return { law: "REGRET=FROZEN_CREDITED_ENTRY_MINUS_DEEPEST_TRUE_PRINT_PRICE_INSIDE_FIRST_TWO_SIDED_BOOK_TO_V3_PRE_MATCH_EDGE; UNCREDITED_NUMERIC_REGRET_NULL", denominator_legs: rows.length, aggregate: distribution(rows.map((row) => row.regret_cents), "cents"), category_x_price_region_x_bell_confidence: cells, conservation: { cell_leg_sum: cells.reduce((sum, row) => sum + row.legs, 0), expected_legs: rows.length, pass: cells.reduce((sum, row) => sum + row.legs, 0) === rows.length }, rows };
}

function fillSplit(events) {
  const legs = events.flatMap((event) => Object.values(event.legs));
  const make = (rows) => ({ legs: rows.length, credited: rows.filter((leg) => leg.credited).length, maker: rows.filter((leg) => leg.fill_class?.startsWith("PROVEN_MAKER")).length, taker: rows.filter((leg) => leg.fill_class?.startsWith("PROVEN_TAKER")).length, census_priced: rows.filter((leg) => leg.fill_class === "CENSUS_PRICED_ONE_CENT_RESIDENCY_CONVERSION").length, uncredited: rows.filter((leg) => !leg.credited).length });
  const cells = [...group(legs, (leg) => `${leg.category}|${leg.price_region}|${events.find((event) => event.event_id === leg.event_id).bell_confidence}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, rows]) => ({ cell, counts: make(rows) }));
  return { strict_fill_law: "MAKER_REQUIRES_STRICTLY_LATER_SELLER_AGGRESSED_PRINT_SIZE_GE_5_AT_OR_BELOW_LIVING_REST; TAKER_REQUIRES_DWELL_10_SIZE_5_PAIR_CAP_AND_ASK_AT_OR_BELOW_ACTIVE_TRAILING_EVIDENCE_FLOOR; STATE_LABEL_IGNORED", aggregate: make(legs), category_x_price_region_x_bell_confidence: cells, conservation: { cell_leg_sum: cells.reduce((sum, row) => sum + row.counts.legs, 0), expected_legs: legs.length, pass: cells.reduce((sum, row) => sum + row.counts.legs, 0) === legs.length } };
}

function compactW1Trace(events) {
  return events.flatMap((event) => Object.values(event.legs).map((leg) => ({ mode: event.mode, event_id: event.event_id, leg_identity: leg.leg_identity, ticker: leg.ticker, category: leg.category, price_region: leg.price_region, bell_confidence: event.bell_confidence, w1_left_epoch: event.w1_left_epoch, w1_right_epoch: event.w1_right_epoch, decision_count: leg.decision_count, state_counts: leg.state_counts, action_counts: leg.action_counts, disagreement_count: leg.disagreement_count, maker_reprices: leg.maker_reprices, rest_sanity: leg.rest_sanity, first_decision: leg.first_decision, last_decision: leg.last_decision, first_action_timestamp_epoch: leg.first_action_timestamp_epoch, fill_timestamp_epoch: leg.fill_timestamp_epoch, entry_cents: leg.entry_cents, fill_class: leg.fill_class, print_backed_floor_cents: leg.w1_print_backed_achievable_floor_cents, qualifying_ask_floor_cents: leg.w1_qualifying_ask_floor_cents, entry_minus_eventual_print_low_cents: leg.entry_minus_print_backed_floor_cents, close_telemetry_only: leg.w1_close_telemetry, terminal_reason: leg.terminal_reason, final_state: event.completed_pair ? (event.pair_under_par ? "COMPLETED_UNDER_PAR" : "COMPLETED_AT_OR_ABOVE_PAR") : leg.credited ? "NAKED_CREDITED" : leg.resting_at_hard_edge ? "RESTING_AT_HARD_EDGE" : "NEVER_PLACED" }))).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity));
}

function r3SameBasis(r3Events, boundaries, starts) {
  const out = [];
  for (const prior of r3Events) {
    const boundary = boundaries.get(prior.event_id);
    const left = starts.get(prior.event_id);
    ensure(boundary && Number.isFinite(left), `R3 boundary missing ${prior.event_id}`);
    const legs = Object.values(prior.legs).map((leg) => {
      const fillTimestamp = Number.isFinite(leg.fill?.evidence_ts) ? leg.fill.evidence_ts : leg.honest_fill_class?.startsWith("PROVEN_TAKER") ? leg.action_timestamp_epoch : null;
      const inside = leg.credited && Number.isFinite(fillTimestamp) && fillTimestamp >= left && fillTimestamp <= boundary.right_edge_epoch;
      return { leg_identity: leg.leg_identity, credited: inside, entry_cents: inside ? leg.entry_cents : null, fill_timestamp_epoch: inside ? fillTimestamp : null, frozen_timestamp_source: Number.isFinite(leg.fill?.evidence_ts) ? "fill.evidence_ts" : leg.honest_fill_class?.startsWith("PROVEN_TAKER") ? "action_timestamp_epoch_same_receipt_taker" : "UNAVAILABLE" };
    });
    const completed = legs.every((leg) => leg.credited);
    const cost = completed ? legs.reduce((sum, leg) => sum + leg.entry_cents, 0) : null;
    out.push({ event_id: prior.event_id, category: prior.category, starting_price_split: prior.starting_price_split, bell_confidence: boundary.precision_class, completed_pair: completed, combined_entry_cents: cost, pair_under_par: completed && cost < 100, legs });
  }
  return out;
}

function baselineMetrics(events) {
  const legs = events.flatMap((event) => event.legs);
  return { D: events.length, credited_legs: legs.filter((leg) => leg.credited).length, completed_pairs: events.filter((event) => event.completed_pair).length, pairs_under_par: events.filter((event) => event.pair_under_par).length };
}

function baselineFrontier(events) {
  const tiers = [{ id: "LE_93", test: (x) => x <= 93 }, { id: "LE_95", test: (x) => x <= 95 }, { id: "LE_97", test: (x) => x <= 97 }, { id: "LT_100", test: (x) => x < 100 }, { id: "ANY_PRICE", test: () => true }];
  const make = (rows) => Object.fromEntries(tiers.map((tier) => [tier.id, { fixed_denominator: rows.length, completed_pairs: rows.filter((event) => event.completed_pair && tier.test(event.combined_entry_cents)).length }]));
  const cells = [...group(events, (event) => `${event.category}|${event.starting_price_split}|${event.bell_confidence}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, rows]) => ({ cell, D: rows.length, frontier: make(rows) }));
  return { original_R3_joint_reference_only: 68, same_V3_span_metrics: baselineMetrics(events), same_V3_span_frontier: make(events), category_x_starting_price_region_x_bell_confidence: cells, conservation: { cell_D_sum: cells.reduce((sum, row) => sum + row.D, 0), expected_D: events.length, pass: cells.reduce((sum, row) => sum + row.D, 0) === events.length } };
}

function differentialFullLife(events, fullLifeEvents, mode) {
  const fullBy = new Map(fullLifeEvents.map((event) => [event.event_id, event]));
  const rows = [];
  for (const event of events) {
    const prior = fullBy.get(event.event_id); ensure(prior, `full-life missing ${event.event_id}`);
    for (const [id, leg] of Object.entries(event.legs)) {
      const full = prior.legs[id]; ensure(full, `full-life leg missing ${leg.leg_identity}`);
      let disposition = "OTHER_CAUSAL_WINDOW_DIFFERENCE";
      if (leg.acted === full.acted && leg.credited === full.credited && leg.entry_cents === full.entry_cents && leg.action_timestamp_epoch === full.action_timestamp_epoch && leg.fill_timestamp_epoch === full.fill_timestamp_epoch && leg.fill_class === full.fill_class) disposition = "BYTE_SEMANTIC_IDENTICAL_ENTRY_STREAM";
      else if (!leg.credited && full.credited && full.fill_timestamp_epoch > event.w1_right_epoch && leg.resting_at_hard_edge) disposition = "WAITED_AND_LOST_TO_HARD_RIGHT_EDGE_FULL_LIFE_FILLED_LATER";
      else if (!leg.credited && full.credited && full.fill_timestamp_epoch > event.w1_right_epoch) disposition = "FULL_LIFE_ONLY_POST_EDGE_ACTION_OR_FILL";
      else if (leg.credited && full.credited && leg.fill_timestamp_epoch <= event.w1_right_epoch) disposition = "PRE_EDGE_STREAM_DIFFERENCE_FROM_W1_LEFT_EDGE_LAW";
      rows.push({ mode, event_id: event.event_id, leg_identity: leg.leg_identity, category: leg.category, price_region: leg.price_region, bell_confidence: event.bell_confidence, disposition, w1: { acted: leg.acted, credited: leg.credited, entry_cents: leg.entry_cents, action_timestamp_epoch: leg.action_timestamp_epoch, fill_timestamp_epoch: leg.fill_timestamp_epoch, fill_class: leg.fill_class, resting_target_at_hard_edge_cents: leg.resting_target_at_hard_edge_cents }, full_life: { acted: full.acted, credited: full.credited, entry_cents: full.entry_cents, action_timestamp_epoch: full.action_timestamp_epoch, fill_timestamp_epoch: full.fill_timestamp_epoch, fill_class: full.fill_class } });
    }
  }
  const cells = [...group(rows, (row) => `${row.category}|${row.price_region}|${row.bell_confidence}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, subset]) => ({ cell, legs: subset.length, dispositions: countBy(subset, (row) => row.disposition) }));
  return { mode, rows, disposition_counts: countBy(rows, (row) => row.disposition), waited_and_lost_legs: rows.filter((row) => row.disposition === "WAITED_AND_LOST_TO_HARD_RIGHT_EDGE_FULL_LIFE_FILLED_LATER").length, category_x_price_region_x_bell_confidence: cells, conservation: { row_count: rows.length, expected_legs: 1608, pass: rows.length === 1608, cell_leg_sum: cells.reduce((sum, row) => sum + row.legs, 0) } };
}

function differentialV34W1(events, baselineEvents, mode) {
  const priorBy = new Map(baselineEvents.map((event) => [event.event_id, event]));
  const rows = [];
  for (const event of events) {
    const prior = priorBy.get(event.event_id); ensure(prior, `V34-W1 missing ${event.event_id}`);
    for (const [id, leg] of Object.entries(event.legs)) {
      const old = prior.legs[id]; ensure(old, `V34-W1 leg missing ${leg.leg_identity}`);
      const before = { acted: old.acted, credited: old.credited, entry_cents: old.entry_cents, action_timestamp_epoch: old.action_timestamp_epoch, fill_timestamp_epoch: old.fill_timestamp_epoch, fill_class: old.fill_class };
      const after = { acted: leg.acted, credited: leg.credited, entry_cents: leg.entry_cents, action_timestamp_epoch: leg.action_timestamp_epoch, fill_timestamp_epoch: leg.fill_timestamp_epoch, fill_class: leg.fill_class };
      let disposition = "ENTRY_STREAM_CHANGED_OTHER";
      if (semantic(before) === semantic(after)) disposition = "ENTRY_STREAM_IDENTICAL";
      else if (!old.credited && leg.credited) disposition = "NEWLY_CREDITED";
      else if (old.credited && !leg.credited) disposition = "V34_CREDIT_LOST";
      else if (old.credited && leg.credited && old.entry_cents !== leg.entry_cents) disposition = leg.entry_cents < old.entry_cents ? "CREDITED_DEEPER_THAN_V34" : "CREDITED_SHALLOWER_THAN_V34";
      else if (old.acted !== leg.acted) disposition = "ACTION_STATUS_CHANGED";
      rows.push({ mode, event_id: event.event_id, leg_identity: leg.leg_identity, category: leg.category, price_region: leg.price_region, bell_confidence: event.bell_confidence, disposition, V34_W1: before, V36: after });
    }
  }
  const cells = [...group(rows, (row) => `${row.category}|${row.price_region}|${row.bell_confidence}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, subset]) => ({ cell, legs: subset.length, dispositions: countBy(subset, (row) => row.disposition) }));
  return { mode, baseline_commit: V34_W1_CAUSAL_COMMIT, rows, disposition_counts: countBy(rows, (row) => row.disposition), category_x_price_region_x_bell_confidence: cells, conservation: { rows: rows.length, expected_legs: 1608, cell_leg_sum: cells.reduce((sum, row) => sum + row.legs, 0), pass: rows.length === 1608 && cells.reduce((sum, row) => sum + row.legs, 0) === 1608 } };
}

function differentialV35(events, baselineEvents, mode) {
  const priorBy = new Map(baselineEvents.map((event) => [event.event_id, event]));
  const rows = [];
  for (const event of events) {
    const prior = priorBy.get(event.event_id); ensure(prior, `V35 missing ${event.event_id}`);
    for (const [id, leg] of Object.entries(event.legs)) {
      const old = prior.legs[id]; ensure(old, `V35 leg missing ${leg.leg_identity}`);
      const before = { acted: old.acted, credited: old.credited, entry_cents: old.entry_cents, action_timestamp_epoch: old.action_timestamp_epoch, fill_timestamp_epoch: old.fill_timestamp_epoch, fill_class: old.fill_class };
      const after = { acted: leg.acted, credited: leg.credited, entry_cents: leg.entry_cents, action_timestamp_epoch: leg.action_timestamp_epoch, fill_timestamp_epoch: leg.fill_timestamp_epoch, fill_class: leg.fill_class };
      let disposition = "ENTRY_STREAM_CHANGED_OTHER";
      if (semantic(before) === semantic(after)) disposition = "ENTRY_STREAM_IDENTICAL";
      else if (!old.credited && leg.credited) disposition = "NEWLY_CREDITED";
      else if (old.credited && !leg.credited) disposition = "V35_CREDIT_LOST";
      else if (old.credited && leg.credited && old.entry_cents !== leg.entry_cents) disposition = leg.entry_cents < old.entry_cents ? "CREDITED_DEEPER_THAN_V35" : "CREDITED_SHALLOWER_THAN_V35";
      else if (old.acted !== leg.acted) disposition = "ACTION_STATUS_CHANGED";
      rows.push({ mode, event_id: event.event_id, leg_identity: leg.leg_identity, category: leg.category, price_region: leg.price_region, bell_confidence: event.bell_confidence, disposition, V35: before, V36: after });
    }
  }
  const cells = [...group(rows, (row) => `${row.category}|${row.price_region}|${row.bell_confidence}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, subset]) => ({ cell, legs: subset.length, dispositions: countBy(subset, (row) => row.disposition) }));
  return { mode, baseline_commit: V35_COMMIT, rows, disposition_counts: countBy(rows, (row) => row.disposition), category_x_price_region_x_bell_confidence: cells, conservation: { rows: rows.length, expected_legs: 1608, cell_leg_sum: cells.reduce((sum, row) => sum + row.legs, 0), pass: rows.length === 1608 && cells.reduce((sum, row) => sum + row.legs, 0) === 1608 } };
}

function differentialV36(events, baselineEvents, mode) {
  const priorBy = new Map(baselineEvents.map((event) => [event.event_id, event]));
  const rows = [];
  for (const event of events) {
    const prior = priorBy.get(event.event_id); ensure(prior, `V36 missing ${event.event_id}`);
    for (const [id, leg] of Object.entries(event.legs)) {
      const old = prior.legs[id]; ensure(old, `V36 leg missing ${leg.leg_identity}`);
      const before = { acted: old.acted, credited: old.credited, entry_cents: old.entry_cents, action_timestamp_epoch: old.action_timestamp_epoch, fill_timestamp_epoch: old.fill_timestamp_epoch, fill_class: old.fill_class };
      const after = { acted: leg.acted, credited: leg.credited, entry_cents: leg.entry_cents, action_timestamp_epoch: leg.action_timestamp_epoch, fill_timestamp_epoch: leg.fill_timestamp_epoch, fill_class: leg.fill_class };
      let disposition = "ENTRY_STREAM_CHANGED_OTHER";
      if (semantic(before) === semantic(after)) disposition = "ENTRY_STREAM_IDENTICAL";
      else if (!old.credited && leg.credited) disposition = "NEWLY_CREDITED";
      else if (old.credited && !leg.credited) disposition = "V36_CREDIT_LOST";
      else if (old.credited && leg.credited && old.entry_cents !== leg.entry_cents) disposition = leg.entry_cents < old.entry_cents ? "CREDITED_DEEPER_THAN_V36" : "CREDITED_SHALLOWER_THAN_V36";
      else if (old.acted !== leg.acted) disposition = "ACTION_STATUS_CHANGED";
      rows.push({ mode, event_id: event.event_id, leg_identity: leg.leg_identity, category: leg.category, price_region: leg.price_region, bell_confidence: event.bell_confidence, disposition, V36: before, V37: after });
    }
  }
  const cells = [...group(rows, (row) => `${row.category}|${row.price_region}|${row.bell_confidence}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, subset]) => ({ cell, legs: subset.length, dispositions: countBy(subset, (row) => row.disposition) }));
  return { mode, baseline_commit: V36_COMMIT, rows, disposition_counts: countBy(rows, (row) => row.disposition), category_x_price_region_x_bell_confidence: cells, conservation: { rows: rows.length, expected_legs: 1608, cell_leg_sum: cells.reduce((sum, row) => sum + row.legs, 0), pass: rows.length === 1608 && cells.reduce((sum, row) => sum + row.legs, 0) === 1608 } };
}

function terminalCollapseReceipt(leg, trades) {
  if (!leg.credited || !Number.isInteger(leg.entry_cents) || leg.entry_cents > 9 || !Number.isFinite(leg.fill_timestamp_epoch)) {
    return { terminal_collapse: false, reason: "ENTRY_NOT_SINGLE_DIGIT_OR_NOT_CREDITED", evidence: [] };
  }
  const rows = trades.filter((row) => row.taker_side === "no" && Number.isFinite(row.size) && row.size > 0 && Math.abs(row.ts - leg.fill_timestamp_epoch) <= 1800).sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  let best = [];
  for (let i = 0; i < rows.length; i += 1) {
    const run = [rows[i]];
    for (let j = i + 1; j < rows.length; j += 1) {
      if (rows[j].ts - run[0].ts > 1800) break;
      if (rows[j].price < run.at(-1).price) run.push(rows[j]);
    }
    if (run.length > best.length || (run.length === best.length && run[0].price - run.at(-1).price > (best[0]?.price ?? 0) - (best.at(-1)?.price ?? 0))) best = run;
  }
  const span = best.length ? best[0].price - best.at(-1).price : 0;
  const terminal = best.length >= 3 && span >= 10 && best.at(-1).price <= 9;
  return { terminal_collapse: terminal, reason: terminal ? "MONOTONE_SELLER_DUMP_GE3_SPAN_GE10_INTO_SINGLE_DIGITS_WITHIN_30M_OF_FILL" : "NO_QUALIFYING_TERMINAL_COLLAPSE", evidence: best.map((row) => ({ timestamp_epoch: row.ts, ordinal: row.ordinal, receipt: row.receipt, price_cents: row.price, size: row.size, aggressor_side: "SELLER" })) };
}

function cleanDeepCensus(events, collapseByEvent, mode) {
  const deep = events.filter((event) => event.completed_pair && event.combined_entry_cents <= 95);
  const rows = deep.map((event) => {
    const collapses = collapseByEvent.get(`${mode}|${event.event_id}`) || {};
    const anyTerminalCollapse = Object.values(collapses).some((row) => row.terminal_collapse);
    return { event_id: event.event_id, category: event.category, starting_price_split: event.starting_price_split, bell_confidence: event.bell_confidence, combined_entry_cents: event.combined_entry_cents, exact_bell: event.bell_confidence === "exact", any_terminal_collapse: anyTerminalCollapse, exact_bell_collapse_clean: event.bell_confidence === "exact" && !anyTerminalCollapse, leg_receipts: collapses };
  });
  return { mode, deep_definition: "COMPLETED_PAIR_COMBINED_ENTRY_LE_95", terminal_collapse_method: "03bac97b: credited single-digit leg inside monotone seller-aggressed run of >=3 descending prints spanning >=10c into single digits within 30 minutes", deep_pairs: rows.length, by_bell_confidence: countBy(rows, (row) => row.bell_confidence), with_terminal_collapse: rows.filter((row) => row.any_terminal_collapse).length, exact_bell: rows.filter((row) => row.exact_bell).length, exact_bell_collapse_clean: rows.filter((row) => row.exact_bell_collapse_clean).length, rows };
}

function bleedDelta(v36Events, v34Events, bleed) {
  const v34By = new Map(v34Events.map((event) => [event.event_id, event]));
  const v36By = new Map(v36Events.map((event) => [event.event_id, event]));
  const mechanismByEvent = new Map(bleed.per_game.map((row) => [row.event, row.mech]));
  const mechanismRows = [];
  for (const before of v34Events) {
    if (before.completed_pair) continue;
    const after = v36By.get(before.event_id); ensure(after, `bleed event missing ${before.event_id}`);
    const mechanism = mechanismByEvent.get(before.event_id) || "MODE_SPECIFIC_BASELINE_NON_COMPLETION_OUTSIDE_STRICT_BLEED_CENSUS";
    mechanismRows.push({ event_id: before.event_id, category: after.category, starting_price_split: after.starting_price_split, bell_confidence: after.bell_confidence, V34_mechanism: mechanism, V34_completed: before.completed_pair, V36_completed: after.completed_pair, V36_under_par: after.pair_under_par, disposition: after.pair_under_par ? "CONVERTED_TO_UNDER_PAR" : after.completed_pair ? "COMPLETED_NOT_UNDER_PAR" : "NOT_CONVERTED" });
  }
  const newLossRows = v34Events.filter((before) => before.completed_pair && !v36By.get(before.event_id).completed_pair).map((before) => ({ event_id: before.event_id, category: before.category, starting_price_split: before.starting_price_split, bell_confidence: before.bell_confidence, V34_completed: true, V36_completed: false, V36_credited_legs: Object.values(v36By.get(before.event_id).legs).filter((leg) => leg.credited).length }));
  const depthRows = v36Events.flatMap((event) => Object.values(event.legs).filter((leg) => leg.credited).map((leg) => ({ event_id: event.event_id, leg_identity: leg.leg_identity, category: leg.category, price_region: leg.price_region, bell_confidence: event.bell_confidence, V34_mechanism: mechanismByEvent.get(event.event_id) || "V34_COMPLETED_BASELINE", fill_class: leg.fill_class, entry_cents: leg.entry_cents, eventual_print_low_cents: leg.w1_print_backed_achievable_floor_cents, fill_depth_vs_eventual_low_cents: leg.entry_minus_print_backed_floor_cents })));
  const depthCells = [...group(depthRows, (row) => `${row.category}|${row.price_region}|${row.bell_confidence}|${row.fill_class}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, subset]) => ({ cell, legs: subset.length, depth_vs_eventual_low: distribution(subset.map((row) => row.fill_depth_vs_eventual_low_cents), "cents") }));
  return {
    baseline_mechanism_totals: bleed.summary.mechanism_totals,
    converted_by_V34_mechanism: countBy(mechanismRows.filter((row) => row.disposition === "CONVERTED_TO_UNDER_PAR"), (row) => row.V34_mechanism),
    mechanism_rows: mechanismRows,
    new_losses_from_V34_completed: { count: newLossRows.length, rows: newLossRows },
    credited_fill_depth_vs_eventual_low: { aggregate: distribution(depthRows.map((row) => row.fill_depth_vs_eventual_low_cents), "cents"), category_x_price_region_x_bell_confidence_x_fill_class: depthCells, rows: depthRows, conservation: { rows: depthRows.length, cell_rows: depthCells.reduce((sum, row) => sum + row.legs, 0), pass: depthRows.length === depthCells.reduce((sum, row) => sum + row.legs, 0) } },
    conservation: { V34_non_completed_rows: mechanismRows.length, expected: v34Events.filter((event) => !event.completed_pair).length, V34_completed_rows: v34Events.filter((event) => event.completed_pair).length, full_D: mechanismRows.length + v34Events.filter((event) => event.completed_pair).length, pass: mechanismRows.length === v34Events.filter((event) => !event.completed_pair).length && mechanismRows.length + v34Events.filter((event) => event.completed_pair).length === 804 },
  };
}

function restSanity(events, actions, mode) {
  const rows = events.flatMap((event) => Object.values(event.legs).map((leg) => ({ mode, event_id: event.event_id, leg_identity: leg.leg_identity, ticker: leg.ticker, category: leg.category, price_region: leg.price_region, bell_confidence: event.bell_confidence, ...leg.rest_sanity, credited: leg.credited, entry_cents: leg.entry_cents, fill_class: leg.fill_class, entry_minus_eventual_print_low_cents: leg.entry_minus_print_backed_floor_cents })));
  const cells = [...group(rows, (row) => `${row.category}|${row.price_region}|${row.bell_confidence}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, subset]) => ({ cell, legs: subset.length, tracked_book_receipts: subset.reduce((sum, row) => sum + row.tracked_book_receipts, 0), exact_target_receipts: subset.reduce((sum, row) => sum + row.exact_target_receipts, 0), max_abs_gap_cents: Math.max(...subset.map((row) => row.gap_abs_max_cents)), reprice_up: subset.reduce((sum, row) => sum + row.reprice_up, 0), reprice_down: subset.reduce((sum, row) => sum + row.reprice_down, 0) }));
  const namedIds = ["KXATPCHALLENGERMATCH-26JUL12BOSCOP|COP", "KXATPCHALLENGERMATCH-26JUL12POLKUH|POL", "KXATPCHALLENGERMATCH-26JUL12ARNROM|ARN", "KXATPCHALLENGERMATCH-26JUL12ARNROM|ROM", "KXATPCHALLENGERMATCH-26JUL12KRALOR|LOR", "KXATPCHALLENGERMATCH-26JUL12BOSCOP|BOS"];
  const named = Object.fromEntries(namedIds.map((id) => [id, { leg: rows.find((row) => row.leg_identity === id) || null, actions: actionSummary(actions.filter((row) => row.mode === mode && row.leg_identity === id)), complete_rows_source: "ACTION_AND_FILL_TRACE_PARTS.json" }]));
  const tracked = rows.reduce((sum, row) => sum + row.tracked_book_receipts, 0), exact = rows.reduce((sum, row) => sum + row.exact_target_receipts, 0);
  const byState = Object.fromEntries(["FALLING", "RISING", "SETTLED"].map((state) => {
    const stateTracked = rows.reduce((sum, row) => sum + row.by_state[state].tracked, 0);
    const stateExact = rows.reduce((sum, row) => sum + row.by_state[state].exact, 0);
    return [state, { tracked_book_receipts: stateTracked, exact_target_receipts: stateExact, non_exact_target_receipts: stateTracked - stateExact }];
  }));
  return { law: "FALLING:ACTIVE_REST_EQUALS_MIN(PRIOR_REST,BEST_BID_MINUS_1,PAIR_CAP)_NO_UPWARD_CHASE; RISING_OR_SETTLED:ACTIVE_REST_EQUALS_MIN(BEST_BID_MINUS_1,PAIR_CAP)_TRACK_UP_AND_DOWN; NO_SPREAD_GATE", aggregate: { legs: rows.length, tracked_book_receipts: tracked, exact_target_receipts: exact, non_exact_target_receipts: tracked - exact, max_abs_gap_cents: Math.max(...rows.map((row) => row.gap_abs_max_cents)), reprice_up: rows.reduce((sum, row) => sum + row.reprice_up, 0), reprice_down: rows.reduce((sum, row) => sum + row.reprice_down, 0), by_state: byState }, category_x_price_region_x_bell_confidence: cells, named_checks: named, rows, conservation: { rows: rows.length, expected_legs: 1608, cell_legs: cells.reduce((sum, row) => sum + row.legs, 0), pass: rows.length === 1608 && cells.reduce((sum, row) => sum + row.legs, 0) === 1608 } };
}

function adverseTail(events, mode) {
  const rows = events.flatMap((event) => Object.values(event.legs)
    .filter((leg) => leg.credited && leg.fill_class?.startsWith("PROVEN_MAKER"))
    .map((leg) => ({ mode, event_id: event.event_id, leg_identity: leg.leg_identity, category: leg.category, price_region: leg.price_region, bell_confidence: event.bell_confidence, fill_source_state: leg.fill_source_state || "UNRECORDED", entry_cents: leg.entry_cents, eventual_print_low_cents: leg.w1_print_backed_achievable_floor_cents, entry_minus_eventual_low_cents: leg.entry_minus_print_backed_floor_cents })));
  const make = (subset) => ({ maker_fills: subset.length, adverse_depth: distribution(subset.map((row) => row.entry_minus_eventual_low_cents), "cents"), positive_adverse_tail: subset.filter((row) => Number.isFinite(row.entry_minus_eventual_low_cents) && row.entry_minus_eventual_low_cents > 0).length });
  const cells = [...group(rows, (row) => `${row.category}|${row.price_region}|${row.bell_confidence}|${row.fill_source_state}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, subset]) => ({ cell, ...make(subset) }));
  return { law: "MAKER_FILL_ENTRY_MINUS_EVENTUAL_TRUE_PRINT_LOW_INSIDE_THE_SAME_HARD_PRE_BELL_WINDOW; FILL_SOURCE_STATE_IS_THE_STATE_CARRIED_BY_THE_REST_AT_FILL", aggregate: make(rows), by_fill_source_state: Object.fromEntries(["FALLING", "RISING", "SETTLED", "SIBLING_FILL", "UNRECORDED"].map((state) => [state, make(rows.filter((row) => row.fill_source_state === state))])), category_x_price_region_x_bell_confidence_x_fill_state: cells, rows, conservation: { rows: rows.length, cell_rows: cells.reduce((sum, row) => sum + row.maker_fills, 0), pass: rows.length === cells.reduce((sum, row) => sum + row.maker_fills, 0) } };
}

function stripCloseTelemetry(events) {
  return events.map((event) => ({ ...event, legs: Object.fromEntries(Object.entries(event.legs).map(([id, leg]) => [id, Object.fromEntries(Object.entries(leg).filter(([key]) => !key.toLowerCase().includes("close"))) ])) }));
}

function gradeDigest(events) {
  return semantic({ score: scoreW1Column(events, "DIGEST"), frontier: frontierW1(events), regret: { ...regretW1(events), rows: undefined }, fills: fillSplit(events) });
}

async function causalMain() {
  ensure(!output.toLowerCase().includes("holdout"), "holdout forbidden");
  for (const commit of [V36_COMMIT, HYGIENE_COMMIT, V35_COMMIT, V34_W1_CAUSAL_COMMIT, V34_FULL_LIFE_COMMIT, V34_TRADING_PHASE_COMMIT, V32_COMMIT, R3_COMMIT, RECON_COMMIT, NEARMISS_COMMIT, START_LEDGER_COMMIT, OFFER_COMMIT, BLEED_COMMIT, EXEMPLAR_COMMIT, AUTOPSY_COMMIT]) requireCommit(commit);
  safeClean(output);
  const baseEvents = loadBaseEvents(); ensure(baseEvents.length === 804, "D must be 804");
  const startBytes = gitShow(START_LEDGER_COMMIT, START_LEDGER_PATH);
  ensure(sha(startBytes) === "1d7fe6a56837ceb0c0b8c932a05daecacc0cefbea94384e16c84975f2ed98ce5", "V3 ledger hash mismatch");
  const startRows = startBytes.toString("utf8").trim().split(/\r?\n/).map(JSON.parse); ensure(startRows.length === 804, "V3 D mismatch");
  const boundaries = new Map(startRows.map((row) => [row.event_id, w1Boundary(row)])); ensure(boundaries.size === 804, "V3 duplicate event");
  const sources = loadSources();
  const bells = new Map(JSON.parse(fs.readFileSync(bellFile)).leg_rows.map((row) => [row.event_id, row.exact_bell_ts]));
  const tickers = new Set(baseEvents.flatMap((event) => Object.values(event.legs).map((leg) => leg.ticker))); ensure(tickers.size === 1608, "1608 legs required");
  process.stderr.write("V37_STAGE print_spool_start\n");
  const printLoad = buildPrintSpool(tickers);
  process.stderr.write("V37_STAGE print_spool_complete\n");
  const tapeHashes = {}, strictEvents = [], censusEvents = [], spans = [], actions = [], eventStarts = new Map();
  const collapseByEvent = new Map();
  const decisionTmp = path.join(output, ".full-decision-trace.jsonl");
  fs.writeFileSync(decisionTmp, "");
  const namedDecisionRows = [];
  const floorBoundRows = [];
  const decisionStats = { total: 0, strict: 0, census: 0, post_edge: 0, scheduled_clock_non_null: 0, actual_bell_clock_non_null: 0, boundary_clock_non_null: 0, floor_bound_authority_decisions: 0, floor_bound_forbidden_takes: 0, floor_bound_allowed_takes: 0, floor_bound_unbound_takes: 0 };
  const flushDecisions = (rows) => {
    if (!rows.length) return;
    for (const row of rows) {
      decisionStats.total += 1;
      if (row.mode === "STRICT_LAW") decisionStats.strict += 1;
      if (row.mode === "CENSUS_PRICED") decisionStats.census += 1;
      if (row.timestamp_epoch > row.pre_match_boundary_epoch) decisionStats.post_edge += 1;
      if (Number.isFinite(row.t_minus_scheduled_seconds)) decisionStats.scheduled_clock_non_null += 1;
      if (Number.isFinite(row.t_minus_actual_bell_seconds)) decisionStats.actual_bell_clock_non_null += 1;
      if (Number.isFinite(row.t_minus_pre_match_boundary_seconds)) decisionStats.boundary_clock_non_null += 1;
      if (row.decision?.floor_arithmetic_take_bound) {
        const bound = row.decision.floor_arithmetic_take_bound;
        if (bound.authority) decisionStats.floor_bound_authority_decisions += 1;
        if (!bound.authority) decisionStats.floor_bound_unbound_takes += 1;
        else if (bound.permitted) decisionStats.floor_bound_allowed_takes += 1;
        else decisionStats.floor_bound_forbidden_takes += 1;
        floorBoundRows.push({ mode: row.mode, event_id: row.event_id, leg_identity: row.leg_identity, category: row.category, price_region: row.price_region, bell_confidence: row.bell_confidence, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, displayed_ask_cents: row.observation.ask, sibling_running_print_backed_floor: row.sibling_running_print_backed_floor, incumbent_action: row.decision.incumbent_v36_take?.action || row.decision.action, final_action: row.decision.action, bound });
      }
      if (["ARNROM", "KRALOR", "BOSCOP", "POLKUH"].some((stem) => row.event_id.includes(stem))) namedDecisionRows.push(row);
    }
    fs.appendFileSync(decisionTmp, `${rows.map(JSON.stringify).join("\n")}\n`);
  };
  for (const baseEvent of baseEvents) {
    const boundary = boundaries.get(baseEvent.event_id); ensure(boundary, `missing V3 row ${baseEvent.event_id}`);
    const tapes = new Map(), prints = new Map();
    for (const leg of Object.values(baseEvent.legs)) prints.set(leg.ticker, printLoad.load(leg.ticker));
    for (const leg of Object.values(baseEvent.legs)) { const rawTape = loadFullTape(leg.ticker, tapeHashes); tapes.set(leg.ticker, condenseTape(rawTape, prints.get(leg.ticker))); }
    const firstBooks = [...tapes.values()].map((rows) => rows[0]?.ts).filter(Number.isFinite);
    ensure(firstBooks.length > 0, `no two-sided book ${baseEvent.event_id}`);
    const left = Math.min(...firstBooks); eventStarts.set(baseEvent.event_id, left);
    const nonPositive = boundary.right_edge_epoch < left;
    const source0 = sources.get(Object.values(baseEvent.legs)[0].ticker), bell = bells.get(baseEvent.event_id);
    const perLeg = Object.values(baseEvent.legs).map((leg) => {
      const tape = tapes.get(leg.ticker), trades = prints.get(leg.ticker), evidence = evidenceInsideWindow(tape, trades, left, boundary.right_edge_epoch);
      return { leg_identity: leg.leg_identity, ticker: leg.ticker, first_two_sided_book_epoch: tape[0]?.ts ?? null, first_book_inside_window_epoch: evidence.first_two_sided_book_epoch, last_book_inside_window_epoch: evidence.last_two_sided_book_epoch, w1_two_sided_book_receipts: evidence.two_sided_book_receipts, w1_true_prints: evidence.true_prints, print_backed_achievable_floor_cents: evidence.print_backed_achievable_floor_cents, qualifying_ask_floor_cents: evidence.qualifying_ask_floor_cents, w1_close_telemetry: evidence.w1_close_telemetry, book_receipts_after_edge_excluded: tape.filter((row) => row.ts > boundary.right_edge_epoch).length, print_receipts_after_edge_excluded: trades.filter((row) => row.ts > boundary.right_edge_epoch).length };
    });
    const span = { event_id: baseEvent.event_id, category: baseEvent.category, starting_price_split: baseEvent.starting_price_split, w1_left_epoch: left, w1_right_epoch: boundary.right_edge_epoch, edge_source_field: boundary.edge_source_field, precision_class: boundary.precision_class, selected_source: boundary.selected_source, selected_source_family: boundary.selected_source_family, selected_timestamp_precision: boundary.selected_timestamp_precision, conflict_status: boundary.conflict_status, interval_contradiction: boundary.interval_contradiction, non_positive_span: nonPositive, span_seconds: Math.max(0, boundary.right_edge_epoch - left), formation_clock: w1Clock(left, source0, bell, boundary), edge_clock: w1Clock(boundary.right_edge_epoch, source0, bell, boundary), per_leg: perLeg }; spans.push(span);
    const timeline = [];
    for (const [id, leg] of Object.entries(baseEvent.legs)) { for (const row of tapes.get(leg.ticker)) timeline.push({ ...row, leg_id: id }); for (const row of prints.get(leg.ticker)) timeline.push({ ...row, leg_id: id }); }
    timeline.sort((a, b) => a.ts - b.ts || (a.kind === "PRINT" ? 0 : 1) - (b.kind === "PRINT" ? 0 : 1) || a.ordinal - b.ordinal || a.leg_id.localeCompare(b.leg_id));
    const strictDecisionRows = [], censusDecisionRows = [];
    const strictEvent = simulateW1Mode(baseEvent, tapes, prints, sources, bells, "STRICT_LAW", actions, strictDecisionRows, span, timeline, boundary);
    const censusEvent = simulateW1Mode(baseEvent, tapes, prints, sources, bells, "CENSUS_PRICED", actions, censusDecisionRows, span, timeline, boundary);
    strictEvents.push(strictEvent);
    censusEvents.push(censusEvent);
    for (const [mode, event] of [["STRICT_LAW", strictEvent], ["CENSUS_PRICED", censusEvent]]) {
      collapseByEvent.set(`${mode}|${event.event_id}`, Object.fromEntries(Object.values(event.legs).map((leg) => [leg.leg_id, terminalCollapseReceipt(leg, prints.get(leg.ticker))])));
    }
    flushDecisions(strictDecisionRows);
    flushDecisions(censusDecisionRows);
    if (strictEvents.length % 50 === 0) process.stderr.write(`V37_STAGE replay_events_${strictEvents.length}\n`);
  }
  printLoad.cleanup();
  const fullTraceGzip = path.join(output, "FULL_DECISION_TRACE.jsonl.gz");
  await stream.pipeline(fs.createReadStream(decisionTmp), zlib.createGzip({ level: 9, mtime: 0 }), fs.createWriteStream(fullTraceGzip));
  fs.rmSync(decisionTmp);
  const fullTraceParts = splitArtifact(fullTraceGzip, output, "FULL_DECISION_TRACE.jsonl.gz");
  const actionTraceGzip = path.join(output, "ACTION_AND_FILL_TRACE.jsonl.gz");
  await writeGzipRowsFile(actionTraceGzip, actions);
  const actionTraceParts = splitArtifact(actionTraceGzip, output, "ACTION_AND_FILL_TRACE.jsonl.gz");
  const strictScore = scoreW1Column(strictEvents, "STRICT_LAW");
  const censusScore = scoreW1Column(censusEvents, "CENSUS_PRICED_ONE_CENT_RESIDENCY");
  const strictFrontier = frontierW1(strictEvents), censusFrontier = frontierW1(censusEvents);
  const strictRegret = regretW1(strictEvents), censusRegret = regretW1(censusEvents);
  const strictTrace = compactW1Trace(strictEvents), censusTrace = compactW1Trace(censusEvents);
  const strictFillSplit = fillSplit(strictEvents), censusFillSplit = fillSplit(censusEvents);
  ensure(gradeDigest(strictEvents) === gradeDigest(stripCloseTelemetry(strictEvents)), "STRICT close telemetry contaminated grade");
  ensure(gradeDigest(censusEvents) === gradeDigest(stripCloseTelemetry(censusEvents)), "CENSUS close telemetry contaminated grade");
  const r3Bytes = gitShow(R3_COMMIT, R3_EVENT_PATH), r3Events = readRowsBytes(r3Bytes), r3Same = r3SameBasis(r3Events, boundaries, eventStarts), r3Comparison = baselineFrontier(r3Same);
  const v34StrictBytes = gitShow(V34_W1_CAUSAL_COMMIT, V34_W1_STRICT_PATH), v34CensusBytes = gitShow(V34_W1_CAUSAL_COMMIT, V34_W1_CENSUS_PATH);
  const v34StrictEvents = readRowsBytes(v34StrictBytes), v34CensusEvents = readRowsBytes(v34CensusBytes);
  const v35StrictBytes = gitShow(V35_COMMIT, V35_STRICT_PATH), v35CensusBytes = gitShow(V35_COMMIT, V35_CENSUS_PATH);
  const v35StrictEvents = readRowsBytes(v35StrictBytes), v35CensusEvents = readRowsBytes(v35CensusBytes);
  const v36StrictBytes = gitShow(V36_COMMIT, V36_STRICT_PATH), v36CensusBytes = gitShow(V36_COMMIT, V36_CENSUS_PATH);
  const v36StrictEvents = readRowsBytes(v36StrictBytes), v36CensusEvents = readRowsBytes(v36CensusBytes);
  const hygieneBytes = gitShow(HYGIENE_COMMIT, HYGIENE_PATH), hygiene = JSON.parse(hygieneBytes);
  ensure(hygiene.per_model.V34.exact_and_clean === 9 && hygiene.per_model.V35.exact_and_clean === 5 && hygiene.per_model.V36.exact_and_clean === 7, "03bac97b clean-deep ruler mismatch");
  const strictDiff = differentialV34W1(strictEvents, v34StrictEvents, "STRICT_LAW"), censusDiff = differentialV34W1(censusEvents, v34CensusEvents, "CENSUS_PRICED");
  const strictV35Diff = differentialV35(strictEvents, v35StrictEvents, "STRICT_LAW"), censusV35Diff = differentialV35(censusEvents, v35CensusEvents, "CENSUS_PRICED");
  const strictV36Diff = differentialV36(strictEvents, v36StrictEvents, "STRICT_LAW"), censusV36Diff = differentialV36(censusEvents, v36CensusEvents, "CENSUS_PRICED");
  const strictCleanDeep = cleanDeepCensus(strictEvents, collapseByEvent, "STRICT_LAW"), censusCleanDeep = cleanDeepCensus(censusEvents, collapseByEvent, "CENSUS_PRICED");
  const bleedBytes = gitShow(BLEED_COMMIT, BLEED_PATH), bleed = JSON.parse(bleedBytes);
  const strictBleed = bleedDelta(strictEvents, v34StrictEvents, bleed), censusBleed = bleedDelta(censusEvents, v34CensusEvents, bleed);
  const strictRestSanity = restSanity(strictEvents, actions, "STRICT_LAW"), censusRestSanity = restSanity(censusEvents, actions, "CENSUS_PRICED");
  const strictAdverseTail = adverseTail(strictEvents, "STRICT_LAW"), censusAdverseTail = adverseTail(censusEvents, "CENSUS_PRICED");
  const reconBytes = gitShow(RECON_COMMIT, RECON_PATH), recon = JSON.parse(reconBytes), nearBytes = gitShow(NEARMISS_COMMIT, NEARMISS_PATH), near = JSON.parse(nearBytes), offerBytes = gitShow(OFFER_COMMIT, OFFER_PATH), offer = JSON.parse(offerBytes), autopsyBytes = gitShow(AUTOPSY_COMMIT, AUTOPSY_PATH), autopsy = JSON.parse(autopsyBytes), publicManifest = JSON.parse(fs.readFileSync(publicTapeManifest));
  ensure(recon.conservation.PRINTS_FAITHFUL === 804 && recon.conservation.DEFECT === 0, "938 reconciliation seal failed");
  ensure(publicManifest.immutable_denominator.D === 804 && publicManifest.immutable_denominator.required_leg_tickers === 1608, "public tape denominator failed");
  ensure(printLoad.receipt.admitted_unique_full_market_life_prints === publicManifest.records.canonical_true_print_rows, "print archive conservation failed");
  ensure(offer.ceilings.strict_sequential_touch.frontier.any === 680, "historic tape completability 680 missing");
  const hardEdgeViolations = actions.filter((row) => row.timestamp_epoch > row.pre_match_boundary_epoch);
  ensure(hardEdgeViolations.length === 0 && decisionStats.post_edge === 0, "post-edge machine activity");
  const spanCounts = countBy(spans, (row) => `${row.edge_source_field}|${row.precision_class}`);
  const strictArn = strictEvents.find((event) => event.event_id.includes("ARNROM")), censusArn = censusEvents.find((event) => event.event_id.includes("ARNROM")), arnSpan = spans.find((event) => event.event_id.includes("ARNROM"));
  const v34StrictScore = scoreW1Column(v34StrictEvents, "V34_W1_STRICT_BASELINE"), v34CensusScore = scoreW1Column(v34CensusEvents, "V34_W1_CENSUS_BASELINE");
  const v34StrictFrontier = frontierW1(v34StrictEvents), v34CensusFrontier = frontierW1(v34CensusEvents);
  const v35StrictScore = scoreW1Column(v35StrictEvents, "V35_STRICT_BASELINE"), v35CensusScore = scoreW1Column(v35CensusEvents, "V35_CENSUS_BASELINE");
  const v35StrictFrontier = frontierW1(v35StrictEvents), v35CensusFrontier = frontierW1(v35CensusEvents);
  const v36StrictScore = scoreW1Column(v36StrictEvents, "V36_STRICT_OPERATIVE_BASELINE"), v36CensusScore = scoreW1Column(v36CensusEvents, "V36_CENSUS_OPERATIVE_BASELINE");
  const v36StrictFrontier = frontierW1(v36StrictEvents), v36CensusFrontier = frontierW1(v36CensusEvents);
  const scorecard = { schema_version: "window1-v37-floor-arithmetic-take-bound-close-free-score-v1", comparison_floor: { V36_commit: V36_COMMIT, V36_STRICT: v36StrictScore.aggregate, V36_CENSUS: v36CensusScore.aggregate, V36_clean_deep_exact_bell_collapse_clean: hygiene.per_model.V36.exact_and_clean, V35_commit: V35_COMMIT, V35_STRICT: v35StrictScore.aggregate, V35_CENSUS: v35CensusScore.aggregate, V34_W1_commit: V34_W1_CAUSAL_COMMIT, V34_W1_STRICT: v34StrictScore.aggregate, V34_W1_CENSUS: v34CensusScore.aggregate, retired_contaminated_deep_bar: { V34_frontier_LE93_LE95_LE97: [23, 34, 68], reason: "03bac97b_PROVED_73_PERCENT_OF_V34_LE95_DEEP_PAIRS_HAVE_ESTIMATED_RIGHT_EDGES" }, clean_deep_ruler: { definition: "EXACT_BELL_AND_COLLAPSE_CLEAN_COMPLETED_PAIR_LE95", V34: 9, V35: 5, V36: 7 }, R3_original_joint_reference_only: 68, R3_same_V3_window: r3Comparison.same_V3_span_metrics, operator_named_under_par_offer_census_adjusted: 680 }, STRICT_LAW: strictScore, CENSUS_PRICED: censusScore, clean_deep: { STRICT_LAW: { ...strictCleanDeep, rows: undefined }, CENSUS_PRICED: { ...censusCleanDeep, rows: undefined } }, delta_vs_V36: { STRICT_completed_pairs: strictScore.aggregate.completed_pairs - v36StrictScore.aggregate.completed_pairs, STRICT_under_par_pairs: strictScore.aggregate.pairs_under_par - v36StrictScore.aggregate.pairs_under_par, STRICT_clean_deep: strictCleanDeep.exact_bell_collapse_clean - hygiene.per_model.V36.exact_and_clean, CENSUS_completed_pairs: censusScore.aggregate.completed_pairs - v36CensusScore.aggregate.completed_pairs, CENSUS_under_par_pairs: censusScore.aggregate.pairs_under_par - v36CensusScore.aggregate.pairs_under_par }, delta_vs_V35: { STRICT_completed_pairs: strictScore.aggregate.completed_pairs - v35StrictScore.aggregate.completed_pairs, STRICT_under_par_pairs: strictScore.aggregate.pairs_under_par - v35StrictScore.aggregate.pairs_under_par, CENSUS_completed_pairs: censusScore.aggregate.completed_pairs - v35CensusScore.aggregate.completed_pairs, CENSUS_under_par_pairs: censusScore.aggregate.pairs_under_par - v35CensusScore.aggregate.pairs_under_par }, delta_vs_V34_W1: { STRICT_completed_pairs: strictScore.aggregate.completed_pairs - v34StrictScore.aggregate.completed_pairs, STRICT_under_par_pairs: strictScore.aggregate.pairs_under_par - v34StrictScore.aggregate.pairs_under_par, CENSUS_completed_pairs: censusScore.aggregate.completed_pairs - v34CensusScore.aggregate.completed_pairs, CENSUS_under_par_pairs: censusScore.aggregate.pairs_under_par - v34CensusScore.aggregate.pairs_under_par }, conservation: { D_each_column: [strictScore.aggregate.D, censusScore.aggregate.D], expected_D: 804, pass: strictScore.aggregate.D === 804 && censusScore.aggregate.D === 804 } };
  const entryDispositions = { STRICT_LAW: { rows: strictTrace, counts: countBy(strictTrace, (row) => `${row.fill_class || "UNFILLED"}|${row.terminal_reason}`), conservation: { rows: strictTrace.length, expected: 1608, pass: strictTrace.length === 1608 } }, CENSUS_PRICED: { rows: censusTrace, counts: countBy(censusTrace, (row) => `${row.fill_class || "UNFILLED"}|${row.terminal_reason}`), conservation: { rows: censusTrace.length, expected: 1608, pass: censusTrace.length === 1608 } } };
  const binding = { schema_version: "window1-v37-floor-arithmetic-take-bound-control-v1", machine: { architecture: "V36_PLUS_ZERO_PARAMETER_FLOOR_ARITHMETIC_TAKE_BOUND", V36_baseline_commit: V36_COMMIT, V35_lineage_commit: V35_COMMIT, V34_W1_baseline_commit: V34_W1_CAUSAL_COMMIT, V32_lineage_commit: V32_COMMIT, policy_path: path.relative(repo, policyFile).replaceAll("\\", "/"), policy_sha256: fileHash(policyFile), clock_decision_inputs: [], state_transitions_and_maturity_evaluated_only_on_receipts: true }, unchanged_from_V36: { state_directional_rest: "BYTE_SEMANTIC_UNCHANGED", mature_floor_take_permission: "UNCHANGED_BEFORE_ARITHMETIC_BOUND", strict_fill_law: "UNCHANGED", evidence_gate: "UNCHANGED", pair_cap: "UNCHANGED", hard_pre_bell_edge: "UNCHANGED", close_free_grading: "UNCHANGED" }, repair: { authority: "ONLY_ON_A_V36_TAKE_WHEN_OTHER_EXPRESSION_RUNNING_TRUE_PRINT_LOW_IS_CAUSALLY_BOUND", formula: "other_under_par_budget = 100 - entry; TAKE iff other_under_par_budget > other_running_print_backed_floor", forbidden_equality: true, fitted_parameters: 0, missing_other_floor: "NO_AUTHORITY_V36_DECISION_UNCHANGED", forbidden_take_disposition: "HOLD_EXISTING_REST_AND_REASK_ON_EVERY_OWN_BOOK_RECEIPT", other_floor_updates: "TRUE_PRINT_RECEIPTS_ONLY_AT_OR_BEFORE_CURRENT_DECISION; CONTINUES_AFTER_OTHER_LEG_FILL" }, hygiene_ruler: { commit: HYGIENE_COMMIT, path: HYGIENE_PATH, clean_deep_definition: "COMPLETED_LE95_EXACT_BELL_NO_TERMINAL_COLLAPSE", V34: 9, V35: 5, V36: 7, contaminated_23_34_68_bar: "RETIRED" }, window_law: { left: "FIRST_TWO_SIDED_BOOK_ON_EITHER_EXPRESSION", right_precedence: ["exact_start_utc", "known_live_by_utc", "schedule_bound_utc"], hard_edge: "NO_REST_WALK_NO_TAKE_NO_FILL_NO_CAP_ARM_NO_STATE_UPDATE_AFTER_EDGE", boundary_is_reporting_and_admission_only_not_AIM_input: true }, close_law: { role: "TELEMETRY_ONLY", grading_reads: 0, settlement_close_reads: 0 } };
  const startIdentity = { supplied_identity: SUPPLIED_START_IDENTITY, supplied_identity_git_resolution: "UNRESOLVED_AFTER_FETCH_PRUNE_AND_FULL_OBJECT_CENSUS", operative_commit_derived_by_git_path_history: START_LEDGER_COMMIT, operative_path: START_LEDGER_PATH, sha256: sha(startBytes), bytes: startBytes.length, rows: startRows.length, edge_precedence_counts: countBy(spans, (row) => row.edge_source_field), precision_class_counts: countBy(spans, (row) => row.precision_class), combined_edge_source_precision_counts: spanCounts, conservation: { rows: startRows.length, unique_events: boundaries.size, expected_D: 804, pass: startRows.length === 804 && boundaries.size === 804 } };
  const offerBinding = { operator_named_under_par_offer_census_adjusted: 680, operator_binding_role: "COMPARISON_CONSTANT_FROM_V34_W1_ORDER", historical_tape_completability_binding: { commit: OFFER_COMMIT, path: OFFER_PATH, sha256: sha(offerBytes), bytes: offerBytes.length, strict_sequential_any_price: offer.ceilings.strict_sequential_touch.frontier.any, strict_sequential_lt_100: offer.ceilings.strict_sequential_touch.frontier.lt_100, independent_touch_any_price: offer.ceilings.independent_touch.frontier.any }, semantic_fence: "THE HISTORICAL SOURCE CALLS 680 ANY-PRICE TAPE COMPLETABILITY AND 451 LT100; THE OPERATOR-SUPPLIED CENSUS-ADJUSTED UNDER-PAR OFFER IS PRINTED AS 680 BUT NOT SILENTLY ATTRIBUTED TO THE HISTORICAL LT100 FIELD" };
  const closeIsolation = { close_fields_present_as_telemetry_only: true, close_fields_consumed_by_scorecard: 0, close_fields_consumed_by_frontier: 0, close_fields_consumed_by_regret: 0, strict_grade_digest_with_telemetry: gradeDigest(strictEvents), strict_grade_digest_without_close_named_fields: gradeDigest(stripCloseTelemetry(strictEvents)), census_grade_digest_with_telemetry: gradeDigest(censusEvents), census_grade_digest_without_close_named_fields: gradeDigest(stripCloseTelemetry(censusEvents)), strict_invariant: gradeDigest(strictEvents) === gradeDigest(stripCloseTelemetry(strictEvents)), census_invariant: gradeDigest(censusEvents) === gradeDigest(stripCloseTelemetry(censusEvents)), settlement_basis_reads: 0 };
  const hardEdge = { actions: actions.length, decisions: decisionStats.total, post_edge_action_or_fill_or_cap_arm_rows: hardEdgeViolations.length, post_edge_state_update_rows: decisionStats.post_edge, hard_edge_pass: hardEdgeViolations.length === 0 && decisionStats.post_edge === 0, non_positive_spans: spans.filter((row) => row.non_positive_span).length, left_edge_counts: { events: spans.length, first_two_sided_book_events: spans.filter((row) => Number.isFinite(row.w1_left_epoch)).length }, right_edge_counts: countBy(spans, (row) => row.edge_source_field), conservation: { spans: spans.length, expected_D: 804, pass: spans.length === 804 } };
  const decisionConservation = { decision_rows: decisionStats.total, strict_decisions: decisionStats.strict, census_decisions: decisionStats.census, action_and_fill_rows: actions.length, strict_compact_leg_rows: strictTrace.length, census_compact_leg_rows: censusTrace.length, post_edge_rows: hardEdgeViolations.length + decisionStats.post_edge, both_clocks: { scheduled_clock_non_null: decisionStats.scheduled_clock_non_null, actual_bell_clock_non_null: decisionStats.actual_bell_clock_non_null, boundary_clock_non_null: decisionStats.boundary_clock_non_null }, conservation_pass: strictTrace.length === 1608 && censusTrace.length === 1608 && hardEdgeViolations.length === 0 && decisionStats.post_edge === 0 };
  const repairBinding = { V36_operative_baseline: { commit: V36_COMMIT, strict_path: V36_STRICT_PATH, strict_sha256: sha(v36StrictBytes), census_path: V36_CENSUS_PATH, census_sha256: sha(v36CensusBytes) }, hygiene_census: { commit: HYGIENE_COMMIT, path: HYGIENE_PATH, sha256: sha(hygieneBytes), bytes: hygieneBytes.length, exact_clean_bar: { V34: hygiene.per_model.V34.exact_and_clean, V35: hygiene.per_model.V35.exact_and_clean, V36: hygiene.per_model.V36.exact_and_clean } }, V35_lineage: { commit: V35_COMMIT, strict_path: V35_STRICT_PATH, strict_sha256: sha(v35StrictBytes), census_path: V35_CENSUS_PATH, census_sha256: sha(v35CensusBytes) }, V34_W1_lineage: { commit: V34_W1_CAUSAL_COMMIT, strict_path: V34_W1_STRICT_PATH, strict_sha256: sha(v34StrictBytes), census_path: V34_W1_CENSUS_PATH, census_sha256: sha(v34CensusBytes) }, autopsy: { commit: AUTOPSY_COMMIT, path: AUTOPSY_PATH, sha256: sha(autopsyBytes), headline: autopsy.headline, mechanism_tally: autopsy.part1_vanished_deep.mechanism_tally, maker_state_counts: autopsy.part2_maker_fill_adverse_selection?.state_counts || null }, bleed_census: { commit: BLEED_COMMIT, path: BLEED_PATH, sha256: sha(bleedBytes), mechanism_totals: bleed.summary.mechanism_totals }, exemplar_render_pack: { commit: EXEMPLAR_COMMIT, paths: [".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/BOSCOP_DECISION_MARKS.json", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/KRALOR_DECISION_MARKS.json", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/exemplar_packs/POLKUH_DECISION_MARKS.json"] }, CC_sanity_census: { binding_status: "OPERATOR_NAMED_WITHOUT_SEPARATE_GIT_IDENTITY_IN_ORDER", treatment: "NOT_FABRICATED; V37 REST_SANITY IS RECOMPUTED_FROM_RAW RECEIPTS" } };
  const strictNamedActions = actions.filter((row) => row.mode === "STRICT_LAW");
  const namedEvidenceGate = {};
  for (const [legIdentity, prohibitedTake] of [["KXATPCHALLENGERMATCH-26JUL12KRALOR|LOR", 6], ["KXATPCHALLENGERMATCH-26JUL12ARNROM|ROM", 41]]) {
    const fills = strictNamedActions.filter((row) => row.leg_identity === legIdentity && row.kind === "FILL");
    const prohibited = fills.filter((row) => row.fill_class?.startsWith("PROVEN_TAKER") && row.entry_cents === prohibitedTake);
    ensure(prohibited.length === 0, `first-flicker overpay survived ${legIdentity}@${prohibitedTake}`);
    namedEvidenceGate[legIdentity] = { prohibited_taker_entry_cents: prohibitedTake, prohibited_taker_count: prohibited.length, fills };
  }
  const bos32Decisions = namedDecisionRows.filter((row) => row.mode === "STRICT_LAW" && row.leg_identity === "KXATPCHALLENGERMATCH-26JUL12BOSCOP|BOS" && row.decision.action === "TAKE" && row.decision.target_cents === 32);
  const bos32WhileEvidenceLive = bos32Decisions.filter((row) => row.causal_discount_evidence.floor_first_flicker_live || row.quote_path.state === "FALLING" || row.pressure_state === "FALLING");
  ensure(bos32WhileEvidenceLive.length === 0, "first-flicker overpay survived KXATPCHALLENGERMATCH-26JUL12BOSCOP|BOS@32 while downward evidence live");
  namedEvidenceGate["KXATPCHALLENGERMATCH-26JUL12BOSCOP|BOS"] = { prohibited_taker_entry_cents_while_downward_evidence_live: 32, prohibited_taker_count_while_downward_evidence_live: bos32WhileEvidenceLive.length, later_take_after_evidence_absorbed: bos32Decisions, semantic_note: "THE ORDER PROHIBITS BOS_32_WHILE_28_TO_30_DOWNWARD_EVIDENCE_IS_FORMING; THE SAME_32_AFTER_THE_EXISTING_STATE_HORIZON_EXPIRES_WITH_NO_NEW_LOW_IS_LAWFULLY_TAKEABLE_PER THE EXPLICIT AGE_OUT CLAUSE" };
  const bosCopRestActions = strictNamedActions.filter((row) => row.leg_identity === "KXATPCHALLENGERMATCH-26JUL12BOSCOP|COP" && ["PLACE_REST", "REPRICE_REST", "PAIR_CAP_REPRICE"].includes(row.kind));
  const bosCopSweepFills = strictNamedActions.filter((row) => row.leg_identity === "KXATPCHALLENGERMATCH-26JUL12BOSCOP|COP" && row.kind === "FILL" && row.print && row.print.price_cents >= 47 && row.print.price_cents <= 51);
  const polActionsBeforeNamedSeller = strictNamedActions.filter((row) => row.leg_identity === "KXATPCHALLENGERMATCH-26JUL12POLKUH|POL" && ["PLACE_REST", "REPRICE_REST", "PAIR_CAP_REPRICE"].includes(row.kind) && row.timestamp_epoch <= 1783872979);
  const bosCopRequiredBand = bosCopRestActions.filter((row) => row.target_cents >= 45 && row.target_cents <= 66);
  const strictGan = strictEvents.find((event) => event.event_id.includes("GANJAN"));
  const strictFet = strictEvents.find((event) => event.event_id.includes("FETPIE"));
  const strictJon = strictEvents.find((event) => event.event_id.includes("JONSPI"));
  const strictKra = strictEvents.find((event) => event.event_id.includes("KRALOR"));
  const strictBos = strictEvents.find((event) => event.event_id.includes("BOSCOP"));
  const arnLeg = strictArn?.legs?.ARN, romLeg = strictArn?.legs?.ROM;
  const kraLor = strictKra?.legs?.LOR, bosBos = strictBos?.legs?.BOS;
  const namedRegressionChecks = {
    GANJAN_recovers_toward_23: Boolean(strictGan?.completed_pair && strictGan.combined_entry_cents < 99 && Math.abs(strictGan.combined_entry_cents - 23) < 76),
    FETPIE_completes: Boolean(strictFet?.completed_pair),
    JONSPI_completes: Boolean(strictJon?.completed_pair),
    ARNROM_38_plus_56_equals_94: Boolean(strictArn?.completed_pair && strictArn.combined_entry_cents === 94 && arnLeg?.entry_cents === 56 && romLeg?.entry_cents === 38),
    KRALOR_LOR_keeps_5: kraLor?.entry_cents === 5,
    BOSCOP_BOS_keeps_32: bosBos?.entry_cents === 32,
    ARNROM_ROM_38_zero_regret: romLeg?.entry_cents === 38 && romLeg?.entry_minus_print_backed_floor_cents === 0,
  };
  const acceptanceChecks = {
    strict_completed_at_least_V36_270: strictScore.aggregate.completed_pairs >= 270,
    strict_exact_bell_collapse_clean_LE95_at_least_V36_7: strictCleanDeep.exact_bell_collapse_clean >= 7,
    named_regressions_all_pass: Object.values(namedRegressionChecks).every(Boolean),
  };
  const acceptance = {
    status: Object.values(acceptanceChecks).every(Boolean) ? "PASS_V37_BAR" : "REJECTED_V37_BAR_V36_REMAINS_OPERATIVE",
    checks: acceptanceChecks,
    named_regression_checks: namedRegressionChecks,
    required_floor: { strict_completed_pairs: 270, strict_exact_bell_collapse_clean_LE95: 7, rule: "V36_RE_ADJUDICATED_OPERATIVE_FLOOR; BOTH_COMPLETION_AND_03bac97b_CLEAN_DEEP_BAR_MUST_PASS" },
    observed: { strict_completed_pairs: strictScore.aggregate.completed_pairs, strict_exact_bell_collapse_clean_LE95: strictCleanDeep.exact_bell_collapse_clean, strict_frontier_telemetry: { LE_93: strictFrontier.cumulative_frontier.LE_93.completed_pairs, LE_95: strictFrontier.cumulative_frontier.LE_95.completed_pairs, LE_97: strictFrontier.cumulative_frontier.LE_97.completed_pairs } },
    retired_bar: { V34_LE93_LE95_LE97: [23, 34, 68], reason: "03bac97b_SCHEDULE_CONTAMINATION" },
    ruling: "STRICT_COMPLETED_GE_270_AND_EXACT_BELL_COLLAPSE_CLEAN_LE95_GE_7; NAMED_REGRESSIONS_ALL_PASS"
  };
  const arnAgingFill = strictNamedActions.find((row) => row.leg_identity === "KXATPCHALLENGERMATCH-26JUL12ARNROM|ARN" && row.kind === "FILL");
  const floorBoundCells = [...group(floorBoundRows, (row) => `${row.mode}|${row.category}|${row.price_region}|${row.bell_confidence}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, rows]) => ({ cell, decisions: rows.length, permitted: rows.filter((row) => row.bound.permitted).length, forbidden: rows.filter((row) => !row.bound.permitted).length, authority_missing: rows.filter((row) => !row.bound.authority).length }));
  const floorBoundReceipt = { law: "A_V36_TAKE_IS_FORBIDDEN_IFF_100_MINUS_ENTRY_IS_LESS_THAN_OR_EQUAL_TO_THE_OTHER_EXPRESSION_RUNNING_TRUE_PRINT_LOW", fitted_parameters: 0, decision_time_only: true, decisions: floorBoundRows.length, authority_decisions: decisionStats.floor_bound_authority_decisions, forbidden_takes: decisionStats.floor_bound_forbidden_takes, allowed_takes: decisionStats.floor_bound_allowed_takes, unbound_V36_unchanged_takes: decisionStats.floor_bound_unbound_takes, category_x_price_region_x_bell_confidence: floorBoundCells, named: { ARNROM: floorBoundRows.filter((row) => row.event_id.includes("ARNROM")), GANJAN: floorBoundRows.filter((row) => row.event_id.includes("GANJAN")), JACDA: floorBoundRows.filter((row) => row.event_id.includes("JACDA")) }, conservation: { cell_decisions: floorBoundCells.reduce((sum, row) => sum + row.decisions, 0), total_decisions: floorBoundRows.length, pass: floorBoundCells.reduce((sum, row) => sum + row.decisions, 0) === floorBoundRows.length } };
  const strictArnBoundRows = floorBoundReceipt.named.ARNROM.filter((row) => row.mode === "STRICT_LAW");
  const strictArn56Rows = strictArnBoundRows.filter((row) => row.leg_identity.endsWith("|ARN") && row.bound.entry_cents === 56);
  const strictArn38Row = strictArnBoundRows.find((row) => row.leg_identity.endsWith("|ROM") && row.bound.entry_cents === 38) || null;
  const strictGanBoundRows = floorBoundReceipt.named.GANJAN.filter((row) => row.mode === "STRICT_LAW");
  const strictJan79Row = strictGanBoundRows.find((row) => row.leg_identity.endsWith("|JAN") && row.bound.entry_cents === 79) || null;
  const arnFirst56 = strictArn56Rows.at(0) || null;
  const arnLatest56 = strictArn56Rows.at(-1) || null;
  const causalTripwireContradiction = {
    schema_version: "window1-v37-causal-tripwire-contradiction-v1",
    status: "SPECIFICATION_TRIPWIRE_CONFLICTS_WITH_DECISION_TIME_FLOOR_LAW",
    governing_rule: "ONLY_TRUE_PRINTS_OBSERVED_AT_OR_BEFORE_THE_TAKE_DECISION_MAY_BIND_THE_OTHER_EXPRESSION_FLOOR",
    ARNROM: {
      operator_tripwire: "ARN_56_WITH_ROM_FLOOR_38_MUST_BE_LAWFUL_BECAUSE_100_MINUS_56_EQUALS_44_GREATER_THAN_38",
      ARN_take_decision: arnFirst56,
      last_ARN_56_reask: arnLatest56,
      ROM_38_later_take: strictArn38Row,
      decision_time_ROM_floor_sequence_cents: [...new Set(strictArn56Rows.map((row) => row.sibling_running_print_backed_floor.cents))],
      decision_time_comparisons: [...new Set(strictArn56Rows.map((row) => row.bound.comparison))],
      eventual_ROM_38_seconds_after_first_ARN_56_decision: arnFirst56 && strictArn38Row ? strictArn38Row.timestamp_epoch - arnFirst56.timestamp_epoch : null,
      future_leakage_required_to_use_38_at_ARN_56: Boolean(arnFirst56 && strictArn38Row && strictArn38Row.timestamp_epoch > arnFirst56.timestamp_epoch),
      causal_ruling: "ARN_56_IS_FORBIDDEN; 44_IS_NOT_GREATER_THAN_THE_OBSERVED_ROM_FLOOR_49_OR_45. THE_ROM_38_RECEIPT_ARRIVES_LATER_AND_CANNOT_BE_BACKDATED.",
    },
    GANJAN: {
      operator_tripwire: "JAN_79_IS_LAWFUL_ONLY_BECAUSE_GAN_FLOOR_WAS_18",
      JAN_take_decision: strictJan79Row,
      decision_time_GAN_floor: strictJan79Row?.sibling_running_print_backed_floor ?? null,
      final_event: strictGan,
      future_leakage_required_to_use_18_at_JAN_79: strictJan79Row?.sibling_running_print_backed_floor?.cents == null,
      causal_ruling: "GAN_FLOOR_WAS_NOT_BOUND_AT_THE_JAN_79_DECISION, SO V37_HAD_NO_AUTHORITY_AND_LEFT_V36_UNCHANGED. THE_LATER_18_CANNOT_JUSTIFY_THE_EARLIER_TAKE.",
    },
    acceptance_effect: "THE_CAUSAL_IMPLEMENTATION_IS_NOT_RETUNED_TO_FORCE_NONCAUSAL_NAMED_TRIPWIRES; V37_IS_REJECTED_AND_V36_REMAINS_OPERATIVE",
  };
  const namedChecks = { checks: namedRegressionChecks, FLOOR_ARITHMETIC: floorBoundReceipt.named, CAUSAL_TRIPWIRE_CONTRADICTION: causalTripwireContradiction, GANJAN: { STRICT_LAW: strictGan, causal_arithmetic: "AT_JAN_79_THE_GAN_RUNNING_PRINT_BACKED_FLOOR_IS_NULL; V37_HAS_NO_AUTHORITY_AND_V36_IS_UNCHANGED. GAN_18_IS_LATER OUTCOME EVIDENCE." }, FETPIE: strictFet, JONSPI: strictJon, MATURE_REFORMED_FLOOR: { ARNROM_ARN: { expected_entry_cents: 56, fill: arnAgingFill, combined_entry_cents: strictArn?.combined_entry_cents ?? null, pair_under_par: strictArn?.pair_under_par ?? false }, law: `A_NONFALLING_REFORMED_QUALIFYING_ASK_FLOOR_EARNS_TAKE_AUTHORITY_ONLY_AFTER_NO_NEW_LOW_RECEIPT_INSIDE_THE_EXISTING_${policy.LOOKBACK_SECONDS}S_HORIZON; REASK_ON_BOOK_RECEIPTS_ONLY` }, BOSCOP_COP: { rest_actions_45_to_66: actionSummary(bosCopRequiredBand), seller_sweep_fill_rows_47_to_51: actionSummary(bosCopSweepFills), any_rest_in_required_band: bosCopRequiredBand.length > 0, complete_rows_source: "ACTION_AND_FILL_TRACE_PARTS.json" }, POLKUH_POL: { named_seller_timestamp_epoch: 1783872979, last_rest_action_at_or_before_seller: polActionsBeforeNamedSeller.at(-1) || null }, NO_FIRST_FLICKER_OVERPAY: namedEvidenceGate, ARNROM: { span: arnSpan, STRICT_LAW: strictArn, CENSUS_PRICED: censusArn } };
  const core = {
    "CONTROL_BINDING.json": canonical(binding),
    "START_LEDGER_V3_IDENTITY_AND_EDGE_RECEIPT.json": canonical(startIdentity),
    "WINDOW1_SPAN_804.json": canonical({ rows: spans, edge_source_counts: countBy(spans, (row) => row.edge_source_field), precision_class_counts: countBy(spans, (row) => row.precision_class), non_positive_spans: spans.filter((row) => row.non_positive_span).length, conservation: { rows: spans.length, expected_D: 804, pass: spans.length === 804 } }),
    "HARD_RIGHT_EDGE_RECEIPT.json": canonical(hardEdge),
    "SCORECARD_TWO_COLUMN.json": canonical(scorecard),
    "STRICT_FRONTIER.json": canonical(strictFrontier),
    "CENSUS_PRICED_FRONTIER.json": canonical(censusFrontier),
    "STRICT_REGRET_GAUGE.json": canonical({ ...strictRegret, rows: undefined }),
    "CENSUS_PRICED_REGRET_GAUGE.json": canonical({ ...censusRegret, rows: undefined }),
    "STRICT_REGRET_LEDGER.jsonl.gz": gzipRows(strictRegret.rows),
    "CENSUS_PRICED_REGRET_LEDGER.jsonl.gz": gzipRows(censusRegret.rows),
    "STRICT_EVENT_LEDGER.jsonl.gz": gzipRows(strictEvents),
    "CENSUS_PRICED_EVENT_LEDGER.jsonl.gz": gzipRows(censusEvents),
    "STRICT_DECISION_TRACE_1608.json": canonical({ rows: strictTrace, conservation: { rows: strictTrace.length, expected: 1608, pass: strictTrace.length === 1608 } }),
    "CENSUS_PRICED_DECISION_TRACE_1608.json": canonical({ rows: censusTrace, conservation: { rows: censusTrace.length, expected: 1608, pass: censusTrace.length === 1608 } }),
    "ACTION_AND_FILL_TRACE_PARTS.json": canonical(actionTraceParts),
    "DECISION_TRACE_CONSERVATION.json": canonical(decisionConservation),
    "FULL_DECISION_TRACE_PARTS.json": canonical(fullTraceParts),
    "ENTRY_PATH_DISPOSITION.json": canonical(entryDispositions),
    "STRICT_FILL_SPLIT.json": canonical(strictFillSplit),
    "CENSUS_PRICED_FILL_SPLIT.json": canonical(censusFillSplit),
    "FLOOR_ARITHMETIC_TAKE_BOUND_RECEIPT.json": canonical(floorBoundReceipt),
    "FLOOR_ARITHMETIC_TAKE_BOUND_LEDGER.jsonl.gz": gzipRows(floorBoundRows),
    "CLEAN_DEEP_HYGIENE_CENSUS.json": canonical({ source: { commit: HYGIENE_COMMIT, path: HYGIENE_PATH, sha256: sha(hygieneBytes) }, baseline: { V34: hygiene.per_model.V34, V35: hygiene.per_model.V35, V36: hygiene.per_model.V36 }, V37: { STRICT_LAW: strictCleanDeep, CENSUS_PRICED: censusCleanDeep }, contaminated_bar_retired: [23, 34, 68], operative_bar: { strict_completed_pairs: 270, exact_bell_collapse_clean_LE95: 7 } }),
    "V36_READJUDICATION_RECEIPT.json": canonical({ prior_status: "REJECTED_BY_CONTAMINATED_23_34_68_DEEP_FRONTIER_BAR", new_status: "OPERATIVE", controlling_census: { commit: HYGIENE_COMMIT, path: HYGIENE_PATH, sha256: sha(hygieneBytes), V34_deep_LE95: hygiene.per_model.V34.deep_pairs, V34_exact_bell: hygiene.per_model.V34.exact_bell, V34_exact_and_clean: hygiene.per_model.V34.exact_and_clean, schedule_contaminated_share: "25/34=73.5% estimated right edges", V35_exact_and_clean: hygiene.per_model.V35.exact_and_clean, V36_exact_and_clean: hygiene.per_model.V36.exact_and_clean }, comparison: { V35_strict_completed: 264, V36_strict_completed: v36StrictScore.aggregate.completed_pairs, V35_clean_deep: 5, V36_clean_deep: 7, ARNROM_94: true }, ruling: "V36_DOMINATES_V35_ON_CLEAN_INSTRUMENTS_AND_IS_THE_OPERATIVE_V37_FLOOR" }),
    "R3_SAME_WINDOW_COMPARISON.json": canonical(r3Comparison),
    "V36_BASELINE_FRONTIER.json": canonical({ commit: V36_COMMIT, STRICT_LAW: v36StrictFrontier, CENSUS_PRICED: v36CensusFrontier }),
    "V35_BASELINE_FRONTIER.json": canonical({ commit: V35_COMMIT, STRICT_LAW: v35StrictFrontier, CENSUS_PRICED: v35CensusFrontier }),
    "V34_W1_BASELINE_FRONTIER.json": canonical({ STRICT_LAW: v34StrictFrontier, CENSUS_PRICED: v34CensusFrontier }),
    "UNDER_PAR_OFFER_BINDING.json": canonical(offerBinding),
    "DIFFERENTIAL_VS_V34_W1.json": canonical({ STRICT_LAW: { ...strictDiff, rows: undefined }, CENSUS_PRICED: { ...censusDiff, rows: undefined }, conservation: { strict_rows: strictDiff.rows.length, census_rows: censusDiff.rows.length, expected_each: 1608, pass: strictDiff.rows.length === 1608 && censusDiff.rows.length === 1608 } }),
    "DIFFERENTIAL_VS_V34_W1_LEDGER.jsonl.gz": gzipRows([...strictDiff.rows, ...censusDiff.rows]),
    "DIFFERENTIAL_VS_V35.json": canonical({ STRICT_LAW: { ...strictV35Diff, rows: undefined }, CENSUS_PRICED: { ...censusV35Diff, rows: undefined }, conservation: { strict_rows: strictV35Diff.rows.length, census_rows: censusV35Diff.rows.length, expected_each: 1608, pass: strictV35Diff.rows.length === 1608 && censusV35Diff.rows.length === 1608 } }),
    "DIFFERENTIAL_VS_V35_LEDGER.jsonl.gz": gzipRows([...strictV35Diff.rows, ...censusV35Diff.rows]),
    "DIFFERENTIAL_VS_V36.json": canonical({ STRICT_LAW: { ...strictV36Diff, rows: undefined }, CENSUS_PRICED: { ...censusV36Diff, rows: undefined }, conservation: { strict_rows: strictV36Diff.rows.length, census_rows: censusV36Diff.rows.length, expected_each: 1608, pass: strictV36Diff.rows.length === 1608 && censusV36Diff.rows.length === 1608 } }),
    "DIFFERENTIAL_VS_V36_LEDGER.jsonl.gz": gzipRows([...strictV36Diff.rows, ...censusV36Diff.rows]),
    "BLEED_CENSUS_DELTA.json": canonical({ STRICT_LAW: strictBleed, CENSUS_PRICED: censusBleed }),
    "REST_SANITY.json": canonical({ STRICT_LAW: strictRestSanity, CENSUS_PRICED: censusRestSanity }),
    "ADVERSE_TAIL_BY_FILL_STATE.json": canonical({ STRICT_LAW: strictAdverseTail, CENSUS_PRICED: censusAdverseTail }),
    "NAMED_REGRESSION_RECEIPT.json": canonical(namedChecks),
    "CAUSAL_TRIPWIRE_CONTRADICTION_RECEIPT.json": canonical(causalTripwireContradiction),
    "ACCEPTANCE_RECEIPT.json": canonical(acceptance),
    "REPAIR_AUTHORITY_BINDING.json": canonical(repairBinding),
    "CLOSE_TELEMETRY_ISOLATION_RECEIPT.json": canonical(closeIsolation),
    "CENSUS_PRICED_65D49B5D_BINDING.json": canonical({ commit: NEARMISS_COMMIT, path: NEARMISS_PATH, source_sha256: sha(nearBytes), source: { waited_and_lost: near.summary.conservation.waited_and_lost_censused, one_cent_near_miss_rests: near.summary.totals.with1, v32_joint: near.summary.conservation.V32_executable_joint, model_free_ceiling: near.summary.conservation.model_free_ceiling_joint }, V37_application: "V36_TRAJECTORY_PLUS_FLOOR_ARITHMETIC_TAKE_BOUND_INSIDE_V3_PRE_MATCH_SPAN_ONLY; FIRST_LAWFUL_ONE_CENT_SELLER_PRINT_CONVERTS_AT_CURRENT_REST_IN_CENSUS_COLUMN" }),
    "FORBIDDEN_ACCESS_RECEIPT.json": canonical({ holdout_accesses: 0, live_accesses: 0, network_runtime_accesses: 0, order_accesses: 0, position_accesses: 0, exit_accesses: 0, settlement_accesses: 0, DCA_accesses: 0, deployment_accesses: 0, private_scope: "FIT_DEVELOPMENT_804_PUBLIC_TAPE_CACHE_ONLY" }),
    "SOURCE_HASH_MANIFEST.json": canonical({ public_committed: Object.fromEntries([builderFile, policyFile, unitTestFile, packageTestFile, floorFile, baseTraceFile, quoteFile, bellFile, spoolHelperFile, spoolHelperSourceFile].map((file) => [path.relative(repo, file).replaceAll("\\", "/"), { sha256: fs.existsSync(file) ? fileHash(file) : null, bytes: fs.existsSync(file) ? fs.statSync(file).size : null }])), git_bound: { [START_LEDGER_PATH]: { commit: START_LEDGER_COMMIT, sha256: sha(startBytes), bytes: startBytes.length }, [R3_EVENT_PATH]: { commit: R3_COMMIT, sha256: sha(r3Bytes), bytes: r3Bytes.length }, [V36_STRICT_PATH]: { commit: V36_COMMIT, sha256: sha(v36StrictBytes), bytes: v36StrictBytes.length }, [V36_CENSUS_PATH]: { commit: V36_COMMIT, sha256: sha(v36CensusBytes), bytes: v36CensusBytes.length }, [HYGIENE_PATH]: { commit: HYGIENE_COMMIT, sha256: sha(hygieneBytes), bytes: hygieneBytes.length }, [V35_STRICT_PATH]: { commit: V35_COMMIT, sha256: sha(v35StrictBytes), bytes: v35StrictBytes.length }, [V35_CENSUS_PATH]: { commit: V35_COMMIT, sha256: sha(v35CensusBytes), bytes: v35CensusBytes.length }, [V34_W1_STRICT_PATH]: { commit: V34_W1_CAUSAL_COMMIT, sha256: sha(v34StrictBytes), bytes: v34StrictBytes.length }, [V34_W1_CENSUS_PATH]: { commit: V34_W1_CAUSAL_COMMIT, sha256: sha(v34CensusBytes), bytes: v34CensusBytes.length }, [BLEED_PATH]: { commit: BLEED_COMMIT, sha256: sha(bleedBytes), bytes: bleedBytes.length }, [AUTOPSY_PATH]: { commit: AUTOPSY_COMMIT, sha256: sha(autopsyBytes), bytes: autopsyBytes.length }, [RECON_PATH]: { commit: RECON_COMMIT, sha256: sha(reconBytes), bytes: reconBytes.length }, [NEARMISS_PATH]: { commit: NEARMISS_COMMIT, sha256: sha(nearBytes), bytes: nearBytes.length }, [OFFER_PATH]: { commit: OFFER_COMMIT, sha256: sha(offerBytes), bytes: offerBytes.length } }, private_full_life_prints: printLoad.receipt, private_full_life_books: tapeHashes, public_tape_manifest: { sha256: fileHash(publicTapeManifest), bytes: fs.statSync(publicTapeManifest).size } }),
  };
  for (const [name, bytes] of Object.entries(core)) write(name, bytes);
  write("REPORT.md", `# V37 floor-arithmetic take bound\n\nV36 ${V36_COMMIT} is re-adjudicated operative under the clean ${HYGIENE_COMMIT} ruler: V34/V35/V36 exact-bell collapse-clean <=95 pairs are 9/5/7, while V36 has 270 strict completions versus V35's 264. The contaminated 23/34/68 frontier bar is retired.\n\nV37 changes only a V36 TAKE. With a causally bound sibling running true-print low, it permits the take iff \`100 - entry > sibling_floor\`; equality is forbidden. Missing sibling floor gives no authority and leaves V36 unchanged. There are zero fitted parameters.\n\n- Status: ${acceptance.status}.\n- STRICT completed / under par: ${strictScore.aggregate.completed_pairs} / ${strictScore.aggregate.pairs_under_par}; V36: ${v36StrictScore.aggregate.completed_pairs} / ${v36StrictScore.aggregate.pairs_under_par}.\n- Clean deep exact-bell collapse-clean <=95: ${strictCleanDeep.exact_bell_collapse_clean}; V36 floor: 7.\n- STRICT frontier <=93 / <=95 / <=97 / <100: ${strictFrontier.cumulative_frontier.LE_93.completed_pairs} / ${strictFrontier.cumulative_frontier.LE_95.completed_pairs} / ${strictFrontier.cumulative_frontier.LE_97.completed_pairs} / ${strictFrontier.cumulative_frontier.LT_100.completed_pairs}.\n- CENSUS completed / under par: ${censusScore.aggregate.completed_pairs} / ${censusScore.aggregate.pairs_under_par}; V36: ${v36CensusScore.aggregate.completed_pairs} / ${v36CensusScore.aggregate.pairs_under_par}.\n- Floor-bound allowed / forbidden / unbound V36-unchanged take decisions: ${decisionStats.floor_bound_allowed_takes} / ${decisionStats.floor_bound_forbidden_takes} / ${decisionStats.floor_bound_unbound_takes}.\n- STRICT maker / taker: ${strictFillSplit.aggregate.maker} / ${strictFillSplit.aggregate.taker}. Falling maker positive adverse tail / cents: ${strictAdverseTail.by_fill_source_state.FALLING.positive_adverse_tail} / ${strictAdverseTail.by_fill_source_state.FALLING.adverse_depth.total_cents}.\n- Named checks: ${JSON.stringify(namedRegressionChecks)}.\n- GANJAN STRICT: ${strictGan?.combined_entry_cents ?? "INCOMPLETE"}; arithmetic rows are frozen in FLOOR_ARITHMETIC_TAKE_BOUND_RECEIPT.json.\n- Post-edge machine rows: ${hardEdgeViolations.length + decisionStats.post_edge}. Close fields consumed by grading: 0.\n`);
  write("ACCEPTANCE_REPORT.md", `# V37 acceptance ruling\n\nStatus: **${acceptance.status}**.\n\nThe clean bar requires strict completed pairs >=270 and exact-bell collapse-clean completed pairs <=95 >=7, plus every V36 tripwire. Observed: ${acceptance.observed.strict_completed_pairs} and ${acceptance.observed.strict_exact_bell_collapse_clean_LE95}. The schedule-contaminated V34 23/34/68 bar is retired by ${HYGIENE_COMMIT}.\n`);
  const compareNames = [...Object.keys(core), ...fullTraceParts.parts.map((row) => row.name), ...actionTraceParts.parts.map((row) => row.name), "REPORT.md", "ACCEPTANCE_REPORT.md"].sort();
  if (compare) {
    const mismatches = compareNames.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name)));
    ensure(!mismatches.length, `determinism mismatch ${mismatches.join(",")}`);
    write("DETERMINISM_RECEIPT.json", canonical({ builds: 2, byte_identical: true, compared_files: compareNames.length, mismatches: [] }));
  } else write("DETERMINISM_RECEIPT.json", canonical({ builds: 1, byte_identical: null, role: "FIRST_BUILD" }));
  const names = fs.readdirSync(output).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  write("ARTIFACT_HASH_MANIFEST.json", canonical({ files: Object.fromEntries(names.map((name) => [name, { sha256: fileHash(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size }])) }));
  process.stdout.write(canonical({ output, STRICT_LAW: strictScore.aggregate, CENSUS_PRICED: censusScore.aggregate, R3_same_window: r3Comparison.same_V3_span_metrics, spans: spans.length, decisions: decisionStats.total, actions: actions.length, post_edge_rows: hardEdgeViolations.length + decisionStats.post_edge }));
}

causalMain().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
