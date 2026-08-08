#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const stream = require("stream/promises");
const zlib = require("zlib");
const V36_COMMIT = "bfde0d8d1135f5c5f48a5f3d619ab30050efab83";
const REACH_COMMIT = "57daf3c15ad618098a810566d24127df8f17f3f9";
const GAP_COMMIT = "b581cbb58f660939ed9b0c2e88ddc42163dbab9a";
const DIVOT_COMMIT = "d1ac94973252e2f8c28ba32374c29ff7bd605a7e";
const COUNTERFACTUAL_COMMIT = "2b45d14688a0ec05d14ab4975759f1a986398da5";
const FALLER_ANATOMY_COMMIT = "c3961e2c2134aac7ea977d7ab4bb65bf7a263cc4";
const V36_PACKAGE = ".claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806";
const GAP_PACKAGE = ".claude/window1_live_v4_replay/v36_gap_to_union_reach_20260807";
const OUT_REL = ".claude/window1_live_v4_replay/v38_maker_only_machine_20260807";
const EXPECTED_REACH = { events: 804, legs: 1608, reachable_games: 785, no_reach_games: 19, under_par_games: 637, locked_cents: 5253, union_legs: 1570 };

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const variant = arg("--variant", "v38");
const isV39 = variant === "v39";
if (!["v38", "v39"].includes(variant)) throw new Error(`unknown variant ${variant}`);
const policy = require(isV39 ? "./window1_v39_corrected_placement_stack.js" : "./window1_v38_maker_only_machine.js");
const repo = path.resolve(arg("--repo", "."));
const v36Root = path.resolve(arg("--v36-root", "C:/tmp/omi-v36-frozen-bfde"));
const reachRoot = path.resolve(arg("--reach-root", "C:/tmp/omi-reach-57daf3"));
const gapRoot = path.resolve(arg("--gap-root", isV39 ? "C:/tmp/omi-v36-gap-reach-20260807" : repo));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const output = path.resolve(arg("--output", path.join(repo, isV39 ? ".claude/window1_live_v4_replay/v39_corrected_placement_stack_20260807" : OUT_REL)));
const compare = arg("--compare", null) ? path.resolve(arg("--compare", null)) : null;

function ensure(value, message) { if (!value) throw new Error(message); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function shaBytes(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function fileHash(file) { return shaBytes(fs.readFileSync(file)); }
function write(name, bytes) { fs.writeFileSync(path.join(output, name), bytes); }
function writeManifest(dir) {
  const names = fs.readdirSync(dir).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(dir, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(names.map((name) => [name, { sha256: fileHash(path.join(dir, name)), bytes: fs.statSync(path.join(dir, name)).size }])) }));
}
function gzipRows(rows) {
  const lines = rows.map((row) => JSON.stringify(row)).join("\n");
  return zlib.gzipSync(Buffer.from(`${lines}${lines ? "\n" : ""}`), { level: 9, mtime: 0 });
}
async function writeGzipRowsFile(file, rows) {
  async function* encode() { for (const row of rows) yield `${JSON.stringify(row)}\n`; }
  await stream.pipeline(encode(), zlib.createGzip({ level: 9, mtime: 0 }), fs.createWriteStream(file));
}
function readRows(file) {
  const text = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim();
  return text ? text.split(/\r?\n/).map(JSON.parse) : [];
}
function readRowsBytes(bytes) {
  const text = zlib.gunzipSync(bytes).toString("utf8").trim();
  return text ? text.split(/\r?\n/).map(JSON.parse) : [];
}
function gitHead(root) {
  return require("child_process").execFileSync("git", ["-c", `safe.directory=${path.resolve(root).replaceAll("\\", "/")}`, "rev-parse", "HEAD"], { cwd: root, encoding: "utf8" }).trim();
}
function gitShow(commit, relativePath) {
  return require("child_process").execFileSync("git", ["show", `${commit}:${relativePath}`], { cwd: repo, maxBuffer: 256 * 1024 * 1024 });
}
function safeOutput(dir) {
  const resolved = path.resolve(dir);
  ensure(path.basename(resolved).includes(isV39 ? "v39" : "v38"), `unsafe output ${resolved}`);
  ensure(resolved !== repo && resolved !== path.parse(resolved).root, `unsafe output ${resolved}`);
  fs.rmSync(resolved, { recursive: true, force: true });
  fs.mkdirSync(resolved, { recursive: true });
}
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function percentile(values, q) {
  const x = values.filter(Number.isFinite).sort((a, b) => a - b);
  return x.length ? x[Math.max(0, Math.ceil(q * x.length) - 1)] : null;
}
function distribution(values) {
  const x = values.filter(Number.isFinite);
  return { n: x.length, null_n: values.length - x.length, sum: x.reduce((a, b) => a + b, 0), min: x.length ? Math.min(...x) : null, p25: percentile(x, .25), median: percentile(x, .5), p75: percentile(x, .75), p90: percentile(x, .9), max: x.length ? Math.max(...x) : null };
}
function countBy(rows, fn) {
  const out = {};
  for (const row of rows) { const key = String(fn(row)); out[key] = (out[key] || 0) + 1; }
  return Object.fromEntries(Object.entries(out).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}
function clockFields(ts, base) {
  return {
    timestamp_epoch: ts,
    t_minus_scheduled_seconds: Number.isFinite(base.scheduled) ? base.scheduled - ts : null,
    t_minus_actual_bell_seconds: Number.isFinite(base.actual_bell) ? base.actual_bell - ts : null,
    t_minus_pre_match_boundary_seconds: base.right - ts,
  };
}
function parseEt(value) {
  const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!m) return null;
  let hour = +m[4]; if (m[7] === "AM" && hour === 12) hour = 0; if (m[7] === "PM" && hour !== 12) hour += 12;
  return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(hour).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000;
}
function parseCsv(text) {
  const lines = text.trimEnd().split(/\r?\n/); const header = lines.shift().split(",");
  return { header, rows: lines.filter(Boolean).map((line) => line.split(",")) };
}

function loadTape(ticker) {
  const file = path.join(privateRoot, "fit-local/ticks", `${ticker}.csv.gz`);
  ensure(fs.existsSync(file), `missing tape ${ticker}`);
  const bytes = fs.readFileSync(file);
  const parsed = parseCsv(zlib.gunzipSync(bytes).toString("utf8"));
  const ix = Object.fromEntries(parsed.header.map((value, index) => [value, index]));
  const out = [];
  for (let n = 0; n < parsed.rows.length; n += 1) {
    const values = parsed.rows[n], ts = parseEt(values[ix.ts_et]);
    if (!Number.isFinite(ts)) continue;
    const bids = [], asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bp = integer(values[ix[`bid_${level}`]]), bs = positive(values[ix[`bid_${level}_sz`]]);
      const ap = integer(values[ix[`ask_${level}`]]), as = positive(values[ix[`ask_${level}_sz`]]);
      if (bp !== null && bs !== null) bids.push([bp, bs]);
      if (ap !== null && as !== null) asks.push([ap, as]);
    }
    if (!bids.length || !asks.length) continue;
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]);
    const bidDepth = bids.reduce((sum, x) => sum + x[1], 0), askDepth = asks.reduce((sum, x) => sum + x[1], 0);
    out.push({ kind: "BOOK", ticker, ts, ordinal: n + 2, receipt: `${ticker}.csv.gz#row-${n + 2}`, bid: bids[0][0], ask: asks[0][0], spread: asks[0][0] - bids[0][0], top_bid_size: bids[0][1], top_ask_size: asks[0][1], bid_depth_5: bidDepth, ask_depth_5: askDepth, depth_ratio: bidDepth / (bidDepth + askDepth), last_trade: integer(values[ix.last_trade]) });
  }
  out.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  let ask = null, askSince = null;
  for (const row of out) { if (row.ask !== ask) { ask = row.ask; askSince = row.ts; } row.ask_dwell_seconds = row.ts - askSince; }
  return { rows: out, sha256: shaBytes(bytes), bytes: bytes.length };
}

async function loadPrints(tickerBounds) {
  const file = path.join(privateRoot, "fit-local/prints.jsonl");
  ensure(fs.existsSync(file), "missing private prints");
  const hash = crypto.createHash("sha256"), byTicker = new Map([...tickerBounds].map(([ticker]) => [ticker, []]));
  const seen = new Map([...tickerBounds].map(([ticker]) => [ticker, new Set()]));
  let rawRows = 0, admitted = 0, duplicates = 0;
  const input = fs.createReadStream(file, { highWaterMark: 1024 * 1024 });
  input.on("data", (chunk) => hash.update(chunk));
  const rl = readline.createInterface({ input, crlfDelay: Infinity });
  for await (const line of rl) {
    if (!line) continue;
    rawRows += 1;
    const row = JSON.parse(line), bound = tickerBounds.get(row.ticker);
    if (!bound || !row.true_print) continue;
    const ts = Date.parse(row.exchange_ts) / 1000;
    if (!Number.isFinite(ts) || ts < bound.left || ts > bound.right) continue;
    if (!row.trade_id || seen.get(row.ticker).has(row.trade_id)) { duplicates += 1; continue; }
    seen.get(row.ticker).add(row.trade_id);
    admitted += 1;
    byTicker.get(row.ticker).push({ kind: "PRINT", ticker: row.ticker, ts, ordinal: admitted, receipt: row.receipt_id, price: integer(row.price_cents), size: positive(row.size), taker_side: row.taker_side, taker_book_side: row.taker_book_side, trade_id: row.trade_id });
  }
  for (const rows of byTicker.values()) rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  return { byTicker, receipt: { path_class: "PRIVATE_FIT_DEVELOPMENT_PRINTS_HASH_ONLY", sha256: hash.digest("hex"), bytes: fs.statSync(file).size, raw_rows: rawRows, admitted_unique_v36_window_prints: admitted, duplicate_trade_id_rows_rejected: duplicates } };
}

function armSibling(sibling, filled, row, actions, base) {
  sibling.pair_cap_cents = 99 - filled.entry_cents;
  actions.push({ kind: "PAIR_ARM", event_id: sibling.event_id, leg_identity: sibling.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, first_fill_cents: filled.entry_cents, pair_cap_cents: sibling.pair_cap_cents });
  if (sibling.active_order && sibling.active_order.target_cents > sibling.pair_cap_cents) {
    const prior = sibling.active_order.target_cents;
    if (policy.lawfulCent(sibling.pair_cap_cents)) {
      sibling.active_order = { target_cents: sibling.pair_cap_cents, action_ts: row.ts, action_receipt: row.receipt, source_state: "PAIR_CAP" };
      actions.push({ kind: "PAIR_CAP_REPRICE", event_id: sibling.event_id, leg_identity: sibling.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, prior_target_cents: prior, target_cents: sibling.pair_cap_cents });
    } else {
      sibling.active_order = null;
      actions.push({ kind: "PAIR_CAP_CANCEL", event_id: sibling.event_id, leg_identity: sibling.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, prior_target_cents: prior });
    }
  }
}

function fillLeg(leg, sibling, row, fillClass, actions, base) {
  leg.credited = true; leg.entry_cents = leg.active_order.target_cents; leg.action_timestamp_epoch = leg.active_order.action_ts; leg.fill_timestamp_epoch = row.ts; leg.fill_class = fillClass; leg.fill_source_state = leg.active_order.source_state; leg.terminal_reason = fillClass;
  actions.push({ kind: "FILL", event_id: leg.event_id, leg_identity: leg.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, entry_cents: leg.entry_cents, fill_class: fillClass, fill_source_state: leg.fill_source_state, evidence: row.kind === "PRINT" ? { kind: "PRINT", price_cents: row.price, size: row.size, taker_side: row.taker_side, taker_book_side: row.taker_book_side } : { kind: "QUOTE_TOUCH", bid: row.bid, ask: row.ask, spread: row.spread, ask_dwell_seconds: row.ask_dwell_seconds, top_ask_size: row.top_ask_size } });
  armSibling(sibling, leg, row, actions, base);
}

function takeLeg(leg, sibling, row, actions, base, decision) {
  leg.credited = true; leg.entry_cents = row.ask; leg.action_timestamp_epoch = row.ts; leg.fill_timestamp_epoch = row.ts; leg.fill_class = "PROVEN_TAKER_V36_MATURE_EVIDENCE_FLOOR"; leg.fill_source_state = leg.last_combined_state; leg.terminal_reason = leg.fill_class;
  leg.active_order = null;
  actions.push({ kind: "FILL", event_id: leg.event_id, leg_identity: leg.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, entry_cents: leg.entry_cents, fill_class: leg.fill_class, fill_source_state: leg.fill_source_state, decision_reason: decision.reason, evidence: { kind: "DISPLAYED_ASK_TAKE", bid: row.bid, ask: row.ask, spread: row.spread, ask_dwell_seconds: row.ask_dwell_seconds, top_ask_size: row.top_ask_size } });
  armSibling(sibling, leg, row, actions, base);
}

function simulate(base, tapes, prints, mode) {
  const ids = Object.keys(base.legs).sort(), actions = [];
  const event = { event_id: base.event_id, category: base.category, starting_price_split: base.starting_price_split, bell_confidence: base.bell_confidence, edge_source_field: base.edge_source_field, w1_left_epoch: base.left, w1_right_epoch: base.right, mode, legs: {} };
  for (const id of ids) {
    const meta = base.legs[id], reach = meta.reach;
    event.legs[id] = { ...meta, reach: undefined, event_id: base.event_id, credited: false, entry_cents: null, fill_class: null, fill_source_state: null, action_timestamp_epoch: null, fill_timestamp_epoch: null, pair_cap_cents: null, active_order: null, prior_book: null, directional: [], pulse_visits: [], pulse_floor_cents: null, pulse_floor_ever: false, current_bid_level: null, current_bid_since: null, current_bid_last_trade_hit: false, current_bid_last_trade_hit_receipt: null, book_last_trade_hits_by_level: new Map(), seller_hits_by_level: new Map(), persistent_join_level: null, persistent_join_receipt: null, persistent_join_evidence_receipt: null, running_seller_hit_low: null, running_qualified_ask_low: null, running_qualified_ask_low_unabsorbed: false, running_qualified_ask_low_reformed_nonfalling: false, latest_new_low_evidence_ts: null, downward_evidence_rows: [], last_combined_state: "SETTLED", classifier_rows: 0, classifier_state_counts: { FALLING: 0, RISING: 0, SETTLED: 0 }, classifier_opposed_rows: 0, classifier_agreement_rows: 0, sanity_bound_rows: 0, sanity_violation_rows: 0, decision_count: 0, state_counts: { FALLING: 0, RISING: 0, SETTLED: 0 }, action_counts: {}, disagreement_count: 0, first_decision: null, last_decision: null, first_action: null, terminal_reason: null, union_reach_cents: reach.union_reach_cents, union_first_evidence_timestamp_epoch: reach.union_first_evidence_timestamp_epoch, reach_sources: reach.union_sources, reach_inside_v36_edge: reach.union_first_evidence_timestamp_epoch >= base.left && reach.union_first_evidence_timestamp_epoch <= base.right, reach_snapshot: null };
  }
  const timeline = [];
  for (const id of ids) {
    for (const row of tapes.get(id)) timeline.push({ ...row, leg_id: id });
    for (const row of prints.get(id)) timeline.push({ ...row, leg_id: id });
  }
  timeline.sort((a, b) => a.ts - b.ts || (a.kind === "PRINT" ? 0 : 1) - (b.kind === "PRINT" ? 0 : 1) || a.ordinal - b.ordinal || a.leg_id.localeCompare(b.leg_id));
  for (const row of timeline) {
    if (event.legs[ids[0]].credited && event.legs[ids[1]].credited) break;
    if (row.ts < base.left || row.ts > base.right) continue;
    const leg = event.legs[row.leg_id], sibling = event.legs[ids.find((id) => id !== row.leg_id)];
    if (leg.credited) continue;
    if (row.kind === "PRINT") {
      if (mode === "STRICT_PRINT_CROSS" && policy.strictPrintCross(leg.active_order, row)) {
        fillLeg(leg, sibling, row, "STRICT_PRINT_CROSS_SELLER_AGGRESSED_SIZE_FIVE", actions, base); continue;
      }
      if (mode === "MARKET_UNION_REACH" && leg.active_order && policy.strictPrintCross(leg.active_order, row)) {
        fillLeg(leg, sibling, row, "MARKET_REACH_PRINT_CROSS", actions, base); continue;
      }
      if (mode === "MARKET_UNION_REACH" && policy.tradedAtLevel(leg.active_order, row)) {
        fillLeg(leg, sibling, row, "MARKET_REACH_TRADED_AT_LEVEL", actions, base); continue;
      }
      if (row.taker_side === "no") {
        const sellerHitMadeNewLow = leg.running_seller_hit_low === null || row.price < leg.running_seller_hit_low;
        leg.seller_hits_by_level.set(row.price, (leg.seller_hits_by_level.get(row.price) || 0) + 1);
        leg.running_seller_hit_low = leg.running_seller_hit_low === null ? row.price : Math.min(leg.running_seller_hit_low, row.price);
        leg.downward_evidence_rows.push({ ts: row.ts, ordinal: row.ordinal, price: row.price, kind: "SELLER_HIT_TRUE_PRINT", receipt: row.receipt });
        if (sellerHitMadeNewLow) leg.latest_new_low_evidence_ts = row.ts;
      }
      if (row.taker_side === "no" || row.taker_side === "yes") leg.directional = [{ ts: row.ts, ordinal: row.ordinal, direction: row.taker_side === "no" ? "FALLING" : "RISING", kind: row.taker_side === "no" ? "SELLER_HIT_PRINT" : "BUYER_LIFT_PRINT", receipt: row.receipt }];
      continue;
    }
    if (mode === "MARKET_UNION_REACH" && policy.quoteTouch(leg.active_order, row)) {
      fillLeg(leg, sibling, row, "MARKET_REACH_QUOTE_TOUCH_10S_SIZE_FIVE", actions, base); continue;
    }
    const prior = leg.prior_book, newLowAsk = Boolean(prior && row.ask < prior.ask), newHighBid = Boolean(prior && row.bid > prior.bid);
    if (leg.current_bid_level !== row.bid) {
      leg.current_bid_level = row.bid;
      leg.current_bid_since = row.ts;
      leg.current_bid_last_trade_hit = false;
      leg.current_bid_last_trade_hit_receipt = null;
    }
    if (row.last_trade === row.bid) {
      leg.current_bid_last_trade_hit = true;
      leg.current_bid_last_trade_hit_receipt ||= row.receipt;
      leg.book_last_trade_hits_by_level.set(row.bid, (leg.book_last_trade_hits_by_level.get(row.bid) || 0) + 1);
    }
    if (!prior || row.ask !== prior.ask) leg.pulse_visits.push({ ts: row.ts, ordinal: row.ordinal, ask: row.ask, receipt: row.receipt });
    leg.pulse_visits = policy.trimPulseVisits(leg.pulse_visits, row.ts);
    const pulse = policy.trailingPulseFloor(leg.pulse_visits, row.ts);
    leg.pulse_floor_cents = pulse.floor_cents; if (Number.isInteger(pulse.floor_cents)) leg.pulse_floor_ever = true;
    if (newLowAsk && newHighBid) leg.directional = [{ ts: row.ts, ordinal: row.ordinal, direction: "SETTLED", kind: "QUOTE_PATH_INTERNAL_CONFLICT", receipt: row.receipt }];
    else if (newLowAsk) leg.directional = [{ ts: row.ts, ordinal: row.ordinal, direction: "FALLING", kind: "NEW_LOW_ASK", receipt: row.receipt }];
    else if (newHighBid) leg.directional = [{ ts: row.ts, ordinal: row.ordinal, direction: "RISING", kind: "NEW_HIGH_BID", receipt: row.receipt }];
    const quote = policy.quotePathState(leg.directional, row.ts), pressure = policy.pressureState(row.depth_ratio), combined = policy.combineState(quote, pressure);
    leg.last_combined_state = combined.state;
    leg.classifier_rows += 1;
    leg.classifier_state_counts[combined.state] += 1;
    if (combined.disagreement) leg.classifier_opposed_rows += 1;
    if (combined.authority === "QUOTE_PATH_AND_JUL6_PRESSURE_AGREE") leg.classifier_agreement_rows += 1;
    if (isV39 && row.ts - leg.current_bid_since >= policy.PERSISTENT_LEVEL_SECONDS && leg.current_bid_last_trade_hit) {
      if (leg.persistent_join_level === null || row.bid < leg.persistent_join_level) {
        leg.persistent_join_level = row.bid;
        leg.persistent_join_receipt = row.receipt;
        leg.persistent_join_evidence_receipt = leg.current_bid_last_trade_hit_receipt;
      }
    }
    if (policy.qualifyingAskEvidence && policy.qualifyingAskEvidence(row)) {
      if (leg.running_qualified_ask_low === null || row.ask < leg.running_qualified_ask_low) {
        leg.running_qualified_ask_low = row.ask;
        leg.running_qualified_ask_low_unabsorbed = combined.state === "FALLING";
        leg.running_qualified_ask_low_reformed_nonfalling = combined.state !== "FALLING";
        leg.latest_new_low_evidence_ts = row.ts;
        if (combined.state === "FALLING") leg.downward_evidence_rows.push({ ts: row.ts, ordinal: row.ordinal, price: row.ask, kind: "QUALIFYING_ASK_LOW_CREATED_WHILE_FALLING", receipt: row.receipt });
      }
    }
    leg.downward_evidence_rows = leg.downward_evidence_rows.filter((evidence) => evidence.ts <= row.ts && evidence.ts >= row.ts - policy.LOOKBACK_SECONDS);
    const receiptLocalEvidenceFloor = leg.downward_evidence_rows.length ? Math.min(...leg.downward_evidence_rows.map((evidence) => evidence.price)) : null;
    const runningFloors = [leg.running_seller_hit_low, leg.running_qualified_ask_low].filter(Number.isInteger);
    const runningEvidenceFloor = runningFloors.length ? Math.min(...runningFloors) : null;
    const floorMature = Number.isFinite(leg.latest_new_low_evidence_ts) && row.ts - leg.latest_new_low_evidence_ts >= policy.LOOKBACK_SECONDS;
    const activeEvidenceFloor = policy.matureDirectionalEvidenceFloor ? policy.matureDirectionalEvidenceFloor({ state: combined.state, runningEvidenceFloor, receiptLocalEvidenceFloor, reformedQualifyingAskFloor: leg.running_qualified_ask_low, reformedQualifyingAskAuthority: leg.running_qualified_ask_low_reformed_nonfalling, floorMature }) : null;
    const causalOwnReachLowCandidates = [leg.running_seller_hit_low, leg.running_qualified_ask_low].filter(Number.isInteger);
    const causalOwnReachLow = causalOwnReachLowCandidates.length ? Math.min(...causalOwnReachLowCandidates) : null;
    const wtaInverseFalling = isV39 && combined.state === "RISING" && String(base.category).startsWith("WTA") && sibling.last_combined_state === "FALLING";
    const before = leg.active_order?.target_cents ?? null;
    const decision = policy.decide({ state: combined.state, book: row, activeTarget: before, pairCap: leg.pair_cap_cents, pulseFloor: pulse.floor_cents, persistentJoinLevel: isV39 ? leg.persistent_join_level : null, wtaInverseFalling, causalOwnReachLow, activeEvidenceFloor, floorFirstFlickerLive: activeEvidenceFloor === leg.running_qualified_ask_low && leg.running_qualified_ask_low_unabsorbed, floorMature });
    if (isV39 && decision.placement?.sanity_bound_applied) leg.sanity_bound_rows += 1;
    leg.prior_book = row; leg.decision_count += 1; leg.state_counts[combined.state] += 1; if (combined.disagreement) leg.disagreement_count += 1; leg.action_counts[decision.action] = (leg.action_counts[decision.action] || 0) + 1;
    const detail = { ...clockFields(row.ts, base), receipt: row.receipt, ordinal: row.ordinal, observation: { bid: row.bid, ask: row.ask, last_traded: row.last_trade, spread: row.spread, ask_dwell_seconds: row.ask_dwell_seconds, top_ask_size: row.top_ask_size, bid_depth_5: row.bid_depth_5, ask_depth_5: row.ask_depth_5 }, quote_path_state: quote.state, pressure_state: pressure, combined_state: combined.state, direction_authority: combined.authority, disagreement: combined.disagreement, pulse_floor: pulse, persistent_level_join: { level_cents: leg.persistent_join_level, receipt: leg.persistent_join_receipt, evidence_receipt: leg.persistent_join_evidence_receipt, current_bid_residency_seconds: row.ts - leg.current_bid_since, book_last_trade_equals_bid_receipts: leg.book_last_trade_hits_by_level.get(row.bid) || 0, certified_seller_aggressed_prints_at_current_bid: leg.seller_hits_by_level.get(row.bid) || 0 }, wta_other_expression_falling: wtaInverseFalling, causal_own_reach_low_cents: causalOwnReachLow, active_evidence_floor_cents: activeEvidenceFloor, floor_mature: floorMature, pair_cap_cents: leg.pair_cap_cents, order_before_cents: before, decision, order_after_cents: null };
    leg.first_decision ||= detail; leg.last_decision = detail;
    if (["PLACE_REST", "REPRICE_REST"].includes(decision.action)) {
      leg.active_order = { target_cents: decision.target_cents, action_ts: row.ts, action_receipt: row.receipt, source_state: combined.state };
      leg.first_action ||= detail;
      actions.push({ kind: decision.action, event_id: base.event_id, leg_identity: leg.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, target_cents: decision.target_cents, state: combined.state, reason: decision.reason, pulse_floor_cents: pulse.floor_cents });
    } else if (decision.action === "CANCEL_REST") {
      leg.active_order = null;
      actions.push({ kind: "CANCEL_REST", event_id: base.event_id, leg_identity: leg.leg_identity, ...clockFields(row.ts, base), receipt: row.receipt, reason: decision.reason });
    } else if (decision.action === "TAKE") {
      leg.first_action ||= detail;
      takeLeg(leg, sibling, row, actions, base, decision);
    }
    detail.order_after_cents = leg.active_order?.target_cents ?? null;
    if (Number.isInteger(detail.order_after_cents) && detail.order_after_cents >= row.ask) leg.sanity_violation_rows += 1;
    if (row.ts <= leg.union_first_evidence_timestamp_epoch) leg.reach_snapshot = { ...detail };
  }
  for (const leg of Object.values(event.legs)) {
    leg.resting_target_at_edge_cents = leg.credited ? null : (leg.active_order?.target_cents ?? null);
    leg.first_action_timestamp_epoch = leg.first_action?.timestamp_epoch ?? null;
    if (!leg.credited) leg.terminal_reason = leg.decision_count === 0 ? "NO_TWO_SIDED_BOOK_DECISION_INSIDE_V36_EDGE" : leg.active_order ? "REST_UNFILLED_AT_HARD_PREBELL_EDGE" : "NO_LAWFUL_REST_AT_HARD_PREBELL_EDGE";
    leg.final_state = leg.credited ? "CREDITED" : leg.active_order ? "RESTING_UNFILLED" : "NEVER_PLACED_OR_CANCELLED";
    leg.persistent_join_book_last_trade_receipts = leg.persistent_join_level === null ? 0 : (leg.book_last_trade_hits_by_level.get(leg.persistent_join_level) || 0);
    leg.persistent_join_certified_seller_aggressed_prints = leg.persistent_join_level === null ? 0 : (leg.seller_hits_by_level.get(leg.persistent_join_level) || 0);
    delete leg.active_order; delete leg.prior_book; delete leg.directional; delete leg.pulse_visits; delete leg.first_action; delete leg.seller_hits_by_level; delete leg.book_last_trade_hits_by_level; delete leg.downward_evidence_rows;
  }
  const legs = Object.values(event.legs);
  event.completed_pair = legs.every((leg) => leg.credited);
  event.combined_entry_cents = event.completed_pair ? legs.reduce((sum, leg) => sum + leg.entry_cents, 0) : null;
  event.pair_under_par = event.completed_pair && event.combined_entry_cents < 100;
  return { event, actions };
}

function score(events) {
  const legs = events.flatMap((event) => Object.values(event.legs));
  const completed = events.filter((event) => event.completed_pair), under = completed.filter((event) => event.pair_under_par);
  const frontier = {};
  for (const [name, predicate] of Object.entries({ LE_93: (x) => x <= 93, LE_95: (x) => x <= 95, LE_97: (x) => x <= 97, LT_100: (x) => x < 100, ANY_PRICE: () => true })) frontier[name] = completed.filter((event) => predicate(event.combined_entry_cents)).length;
  return { D: events.length, legs: legs.length, acted_legs: legs.filter((leg) => leg.first_action_timestamp_epoch !== null).length, credited_legs: legs.filter((leg) => leg.credited).length, completed_pairs: completed.length, under_par_pairs: under.length, maker_fill_classes: countBy(legs.filter((leg) => leg.credited), (leg) => leg.fill_class), frontier, conservation: { D: events.length, legs: legs.length, pass: events.length === 804 && legs.length === 1608 } };
}

function frozenV36Score(reachRows) {
  const byEvent = new Map();
  for (const row of reachRows) { if (!byEvent.has(row.event_id)) byEvent.set(row.event_id, []); byEvent.get(row.event_id).push(row); }
  const events = [...byEvent].map(([event_id, legs]) => {
    const completed = legs.length === 2 && legs.every((leg) => leg.v36_credited && Number.isInteger(leg.v36_entry_cents));
    const cost = completed ? legs.reduce((sum, leg) => sum + leg.v36_entry_cents, 0) : null;
    return {
      event_id,
      completed_pair: completed,
      combined_entry_cents: cost,
      pair_under_par: completed && cost < 100,
      legs: Object.fromEntries(legs.map((leg) => [leg.leg_id, {
        first_action_timestamp_epoch: leg.v36_decision_count > 0 ? leg.v36_left_epoch : null,
        credited: Boolean(leg.v36_credited),
        fill_class: leg.v36_fill_class,
      }])),
    };
  });
  return score(events);
}

function classifierTelemetry(events) {
  const legs = events.flatMap((event) => Object.values(event.legs).map((leg) => ({ ...leg, event_category: event.category, event_bell_confidence: event.bell_confidence })));
  const sealedDirection = (leg) => leg.leg_direction === "CLIMBING" ? "RISING" : leg.leg_direction === "FALLING" ? "FALLING" : leg.leg_direction === "FLAT" ? "SETTLED" : null;
  const summarize = (rows) => {
    const atReach = rows.filter((leg) => sealedDirection(leg) && leg.reach_snapshot?.combined_state);
    const atReachCorrect = atReach.filter((leg) => leg.reach_snapshot.combined_state === sealedDirection(leg));
    return {
      legs: rows.length,
      decision_receipts: rows.reduce((sum, leg) => sum + leg.classifier_rows, 0),
      eligible_receipts: rows.reduce((sum, leg) => sum + (sealedDirection(leg) ? leg.classifier_rows : 0), 0),
      correct_receipts: rows.reduce((sum, leg) => sum + (sealedDirection(leg) ? leg.classifier_state_counts[sealedDirection(leg)] : 0), 0),
      receipt_accuracy: rows.reduce((sum, leg) => sum + (sealedDirection(leg) ? leg.classifier_rows : 0), 0) ? rows.reduce((sum, leg) => sum + (sealedDirection(leg) ? leg.classifier_state_counts[sealedDirection(leg)] : 0), 0) / rows.reduce((sum, leg) => sum + (sealedDirection(leg) ? leg.classifier_rows : 0), 0) : null,
      reach_moment_eligible_legs: atReach.length,
      reach_moment_correct_legs: atReachCorrect.length,
      reach_moment_accuracy: atReach.length ? atReachCorrect.length / atReach.length : null,
      reach_moment_confusion: countBy(atReach, (leg) => `${sealedDirection(leg)}->${leg.reach_snapshot.combined_state}`),
      agreement_receipts: rows.reduce((sum, leg) => sum + leg.classifier_agreement_rows, 0),
      opposed_receipts_settled: rows.reduce((sum, leg) => sum + leg.classifier_opposed_rows, 0),
    };
  };
  const groups = new Map(); for (const leg of legs) { const key = `${leg.event_category}|${leg.event_bell_confidence}`; if (!groups.has(key)) groups.set(key, []); groups.get(key).push(leg); }
  return { aggregate: summarize(legs), category_x_bell_confidence: [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([cell, rows]) => ({ cell, ...summarize(rows) })), telemetry_only_ex_post_direction_not_consumed_by_policy: true };
}

function residualOwner(leg, reach, base) {
  if (leg.credited && leg.entry_cents <= reach) return null;
  if (leg.credited && String(leg.fill_class).includes("TAKER")) return { owner: "TAKE_FIRED_ABOVE_REACH", detail: `take ${leg.entry_cents} > union reach ${reach}`, measurable_cents: leg.entry_cents - reach };
  if (leg.credited) return { owner: `${leg.fill_source_state || "UNKNOWN"}_REST_FILLED_SHALLOW`, detail: `entry ${leg.entry_cents} > union reach ${reach}`, measurable_cents: leg.entry_cents - reach };
  if (!leg.reach_inside_v36_edge) return { owner: "HARD_PREBELL_EDGE_EXCLUDES_REACH_EVIDENCE", detail: `reach evidence ${leg.union_first_evidence_timestamp_epoch} outside ${base.left}..${base.right}`, measurable_cents: null };
  const snapshot = leg.reach_snapshot || leg.last_decision, rest = snapshot?.order_after_cents ?? leg.resting_target_at_edge_cents, cap = snapshot?.pair_cap_cents ?? leg.pair_cap_cents;
  if (Number.isInteger(cap) && reach > cap) return { owner: "PAIR_CAP_ARITHMETIC", detail: `reach ${reach} > cap ${cap}`, measurable_cents: reach - cap };
  if (leg.decision_count === 0) return { owner: "ADMISSION_NO_TWO_SIDED_BOOK", detail: "no decision receipt inside hard edge", measurable_cents: null };
  if (Number.isInteger(rest) && rest >= reach) return { owner: "UNION_REACH_PRECEDED_RESIDENCY_OR_CHANNEL_NOT_REPEATED", detail: `rest ${rest} at/above reach ${reach} but no later union channel`, measurable_cents: 0 };
  const state = snapshot?.combined_state || leg.last_decision?.combined_state || "UNKNOWN";
  const gap = Number.isInteger(rest) ? reach - rest : null;
  if (state === "RISING" && !leg.pulse_floor_ever) return { owner: "RISER_NO_TWO_VISIT_TRAILING_PULSE_FLOOR", detail: `no signable revisited pulse floor; reach ${reach}`, measurable_cents: gap };
  if (state === "RISING") return { owner: "RISER_PULSE_REST_OFF_REACH", detail: `pulse rest ${rest} below reach ${reach}`, measurable_cents: gap };
  if (state === "FALLING") return { owner: "FALLER_V36_NO_CHASE_REST_OFF_REACH", detail: `falling rest ${rest} below reach ${reach}`, measurable_cents: gap };
  return { owner: "SETTLED_BID_MINUS_ONE_REST_OFF_REACH", detail: `settled rest ${rest} below reach ${reach}`, measurable_cents: gap };
}

function gradeAgainstReach(events, reachByEvent, baseByEvent) {
  const rows = [], residuals = [], classRows = [];
  for (const event of events) {
    const reach = reachByEvent.get(event.event_id);
    if (!reach) continue;
    const levels = Object.values(reach.legs).map((leg) => leg.union_reach_cents);
    const reachComplete = levels.every(Number.isInteger), reachCost = reachComplete ? levels.reduce((a, b) => a + b, 0) : null;
    if (!(reachComplete && reachCost < 100)) continue;
    const legRows = [];
    for (const id of Object.keys(event.legs).sort()) {
      const leg = event.legs[id], level = reach.legs[id].union_reach_cents, gap = leg.credited ? leg.entry_cents - level : null;
      const bind = residualOwner(leg, level, baseByEvent.get(event.event_id));
      const row = { event_id: event.event_id, leg_identity: leg.leg_identity, ticker: leg.ticker, category: event.category, starting_price_split: event.starting_price_split, price_region: leg.price_region, bell_confidence: event.bell_confidence, reach_cents: level, reach_sources: reach.legs[id].union_sources, reach_first_evidence_timestamp_epoch: reach.legs[id].union_first_evidence_timestamp_epoch, credited: leg.credited, entry_cents: leg.entry_cents, gap_to_reach_cents: gap, fill_class: leg.fill_class, terminal_state: leg.final_state, terminal_rest_cents: leg.resting_target_at_edge_cents, pair_cap_cents: leg.pair_cap_cents, pulse_floor_ever: leg.pulse_floor_ever, terminal_pulse_floor_cents: leg.pulse_floor_cents, reach_snapshot: leg.reach_snapshot, layer_bind: bind };
      legRows.push(row); rows.push(row); if (bind) residuals.push(row);
    }
    const completed = legRows.every((row) => row.credited), shallowCents = legRows.filter((row) => Number.isInteger(row.gap_to_reach_cents) && row.gap_to_reach_cents > 0).reduce((sum, row) => sum + row.gap_to_reach_cents, 0);
    const grade = completed ? (shallowCents === 0 ? "MATCHED" : "SHALLOW") : "MISSING";
    classRows.push({ event_id: event.event_id, category: event.category, starting_price_split: event.starting_price_split, bell_confidence: event.bell_confidence, reach_cost_cents: reachCost, reach_locked_cents: 100 - reachCost, grade, completed, combined_entry_cents: event.combined_entry_cents, under_par: event.pair_under_par, shallow_cents: shallowCents, measurable_residual_cents: legRows.reduce((sum, row) => sum + (row.layer_bind?.measurable_cents || 0), 0), legs: legRows.map((row) => ({ leg_identity: row.leg_identity, reach_cents: row.reach_cents, credited: row.credited, entry_cents: row.entry_cents, gap_to_reach_cents: row.gap_to_reach_cents, owner: row.layer_bind?.owner || null })) });
  }
  const aggregate = { answer_key_games: classRows.length, answer_key_locked_cents: classRows.reduce((sum, row) => sum + row.reach_locked_cents, 0), grades: countBy(classRows, (row) => row.grade), shallow_gap_cents: distribution(rows.map((row) => row.gap_to_reach_cents).filter((gap) => Number.isInteger(gap) && gap > 0)), measurable_residual_cents: distribution(residuals.map((row) => row.layer_bind?.measurable_cents).filter(Number.isFinite)), completed_pairs: classRows.filter((row) => row.completed).length, under_par_pairs: classRows.filter((row) => row.under_par).length };
  ensure(aggregate.answer_key_games === EXPECTED_REACH.under_par_games && aggregate.answer_key_locked_cents === EXPECTED_REACH.locked_cents, "reach answer-key conservation failed");
  return { rows, residuals, classRows, aggregate };
}

function cellSummary(grades) {
  const groups = new Map();
  for (const row of grades.classRows) { const key = `${row.category}|${row.bell_confidence}`; if (!groups.has(key)) groups.set(key, []); groups.get(key).push(row); }
  return [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([cell, rows]) => ({ cell, category: rows[0].category, bell_confidence: rows[0].bell_confidence, answer_key_games: rows.length, reach_locked_cents: rows.reduce((sum, row) => sum + row.reach_locked_cents, 0), grades: countBy(rows, (row) => row.grade), completed_pairs: rows.filter((row) => row.completed).length, under_par_pairs: rows.filter((row) => row.under_par).length, shallow_cents: distribution(rows.map((row) => row.shallow_cents).filter((x) => x > 0)), measurable_residual_cents: distribution(rows.map((row) => row.measurable_residual_cents).filter((x) => x > 0)) }));
}

async function main() {
  ensure(gitHead(v36Root) === V36_COMMIT, "V36 frozen worktree mismatch");
  ensure(gitHead(reachRoot) === REACH_COMMIT, "reach frozen worktree mismatch");
  ensure(gitHead(gapRoot) === GAP_COMMIT, "gap-grade frozen worktree mismatch");
  ensure(isV39 || gitHead(repo) === GAP_COMMIT || compare, "V38 must build from b581cbb parent before commit");
  safeOutput(output);
  const v36Package = path.join(v36Root, V36_PACKAGE), gapPackage = path.join(gapRoot, GAP_PACKAGE);
  const spans = JSON.parse(fs.readFileSync(path.join(v36Package, "WINDOW1_SPAN_804.json"), "utf8")).rows;
  const v36Trace = JSON.parse(fs.readFileSync(path.join(v36Package, "STRICT_DECISION_TRACE_1608.json"), "utf8")).rows;
  const reachRows = readRows(path.join(gapPackage, "V36_GAP_TO_REACH_LEG_LEDGER.jsonl.gz"));
  ensure(spans.length === 804 && v36Trace.length === 1608 && reachRows.length === 1608, "frozen population mismatch");
  const traceByLeg = new Map(v36Trace.map((row) => [row.leg_identity, row])), reachByLeg = new Map(reachRows.map((row) => [row.leg_identity, row]));
  const reachByEvent = new Map(), baseByEvent = new Map(), tickerBounds = new Map();
  for (const row of reachRows) {
    if (!reachByEvent.has(row.event_id)) reachByEvent.set(row.event_id, { event_id: row.event_id, legs: {} });
    reachByEvent.get(row.event_id).legs[row.leg_id] = row;
  }
  for (const span of spans) {
    const scheduled = Number.isFinite(span.formation_clock?.t_minus_scheduled_seconds) ? span.w1_left_epoch + span.formation_clock.t_minus_scheduled_seconds : null;
    const actualBell = Number.isFinite(span.formation_clock?.t_minus_actual_bell_seconds) ? span.w1_left_epoch + span.formation_clock.t_minus_actual_bell_seconds : null;
    const base = { event_id: span.event_id, category: span.category, starting_price_split: span.starting_price_split, bell_confidence: span.precision_class, edge_source_field: span.edge_source_field, left: span.w1_left_epoch, right: span.w1_right_epoch, scheduled, actual_bell: actualBell, legs: {} };
    for (const leg of span.per_leg) {
      const prior = traceByLeg.get(leg.leg_identity), reach = reachByLeg.get(leg.leg_identity);
      ensure(prior && reach, `missing leg binding ${leg.leg_identity}`);
      const legId = leg.leg_identity.split("|").at(-1);
      base.legs[legId] = { leg_id: legId, leg_identity: leg.leg_identity, ticker: leg.ticker, category: span.category, price_region: prior.price_region, leg_direction: reach.leg_direction, reach };
      tickerBounds.set(leg.ticker, { left: span.w1_left_epoch, right: span.w1_right_epoch });
    }
    ensure(Object.keys(base.legs).length === 2, `event not paired ${span.event_id}`);
    baseByEvent.set(span.event_id, base);
  }
  ensure(baseByEvent.size === 804 && tickerBounds.size === 1608, "base conservation failed");
  const printLoad = await loadPrints(tickerBounds), marketEvents = [], strictEvents = [], allActions = [], tapeHashes = {};
  let index = 0;
  for (const base of [...baseByEvent.values()].sort((a, b) => a.event_id.localeCompare(b.event_id))) {
    index += 1; if (index % 50 === 0) process.stderr.write(`${isV39 ? "V39" : "V38"} replay ${index}/804\n`);
    const tapes = new Map(), prints = new Map();
    for (const [id, leg] of Object.entries(base.legs)) {
      const loaded = loadTape(leg.ticker); tapeHashes[leg.ticker] = { sha256: loaded.sha256, bytes: loaded.bytes };
      tapes.set(id, loaded.rows); prints.set(id, printLoad.byTicker.get(leg.ticker));
    }
    const market = simulate(base, tapes, prints, "MARKET_UNION_REACH"), strict = simulate(base, tapes, prints, "STRICT_PRINT_CROSS");
    marketEvents.push(market.event); strictEvents.push(strict.event);
    for (const row of market.actions) allActions.push({ mode: "MARKET_UNION_REACH", ...row });
    for (const row of strict.actions) allActions.push({ mode: "STRICT_PRINT_CROSS", ...row });
  }
  const marketScore = score(marketEvents), strictScore = score(strictEvents), marketGrades = gradeAgainstReach(marketEvents, reachByEvent, baseByEvent), strictGrades = gradeAgainstReach(strictEvents, reachByEvent, baseByEvent), v36Score = frozenV36Score(reachRows);
  const layerGroups = new Map();
  for (const row of marketGrades.residuals) { const key = row.layer_bind.owner; if (!layerGroups.has(key)) layerGroups.set(key, []); layerGroups.get(key).push(row); }
  const layerRanking = [...layerGroups].map(([owner, rows]) => ({ owner, games: new Set(rows.map((row) => row.event_id)).size, sides: rows.length, measurable_cents: rows.reduce((sum, row) => sum + (row.layer_bind.measurable_cents || 0), 0), category_x_bell_confidence: countBy(rows, (row) => `${row.category}|${row.bell_confidence}`) })).sort((a, b) => b.measurable_cents - a.measurable_cents || b.games - a.games || a.owner.localeCompare(b.owner));
  const named = {};
  for (const label of ["ARNROM", "BOSCOP", "WESPAA", "NIKVRB", "GANJAN"]) {
    const market = marketEvents.find((event) => event.event_id.includes(label)), strict = strictEvents.find((event) => event.event_id.includes(label));
    ensure(market && strict, `named game absent ${label}`);
    const reach = reachByEvent.get(market.event_id), reachLevels = Object.values(reach.legs).map((leg) => leg.union_reach_cents);
    const legView = (event) => Object.fromEntries(Object.entries(event.legs).map(([id, leg]) => [id, { credited: leg.credited, entry_cents: leg.entry_cents, fill_class: leg.fill_class, terminal_rest_cents: leg.resting_target_at_edge_cents, final_causal_state: leg.last_combined_state, persistent_join_level_cents: leg.persistent_join_level, persistent_join_book_last_trade_receipts: leg.persistent_join_book_last_trade_receipts, persistent_join_certified_seller_aggressed_prints: leg.persistent_join_certified_seller_aggressed_prints, persistent_join_evidence_receipt: leg.persistent_join_evidence_receipt, sanity_bound_receipts: leg.sanity_bound_rows, sanity_violations: leg.sanity_violation_rows }]));
    named[label] = { event_id: market.event_id, reach_levels: Object.fromEntries(Object.entries(reach.legs).map(([id, leg]) => [id, leg.union_reach_cents])), reach_combined_cents: reachLevels.every(Number.isInteger) ? reachLevels.reduce((a, b) => a + b, 0) : null, MARKET_UNION_REACH: { completed: market.completed_pair, combined_entry_cents: market.combined_entry_cents, under_par: market.pair_under_par, legs: legView(market) }, STRICT_PRINT_CROSS: { completed: strict.completed_pair, combined_entry_cents: strict.combined_entry_cents, under_par: strict.pair_under_par, legs: legView(strict) } };
  }
  ensure(named.ARNROM.reach_combined_cents === 88 && named.BOSCOP.reach_combined_cents === 75 && named.NIKVRB.reach_combined_cents === 86, "named reach identities changed");
  const policyFile = path.join(repo, isV39 ? "arb-executor/analysis/window1_v39_corrected_placement_stack.js" : "arb-executor/analysis/window1_v38_maker_only_machine.js"), builderFile = __filename;
  const wrapperFile = path.join(repo, "arb-executor/analysis/build_window1_v39_corrected_placement_stack.js");
  const policyText = fs.readFileSync(policyFile, "utf8");
  if (!isV39) ensure(!/action:\s*["']TAKE["']/.test(policyText) && !/function\s+.*take/i.test(policyText), "take path survived in V38 policy");
  if (isV39) ensure(/V36_MATURE_EVIDENCE_FLOOR_TAKE_UNCHANGED/.test(policyText), "V36 take path missing from V39");
  const control = isV39
    ? { schema_version: "window1-v39-corrected-placement-stack-control-v1", base: V36_COMMIT, frozen_union_reach: REACH_COMMIT, controlling_receipts: [COUNTERFACTUAL_COMMIT, "2c54d724186d2f8b152205379aef88499c457a7a", FALLER_ANATOMY_COMMIT], architecture: { causal_direction: "DECISION_TIME_QUOTE_PATH_PLUS_JUL6_PRESSURE_AGREEMENT_WEIGHTED; OPPOSED_DIRECTIONAL_VOTES_SETTLE; NO_EX_POST_LABEL_INPUT", persistent_level_join: `RISING_CURRENT_BID_RESIDENCY_GE_${policy.PERSISTENT_LEVEL_SECONDS}S_AND_SELLER_HIT_AT_LEVEL_THEN_REST_AT_LEVEL`, WTA_inverse_falling_hold: "WTA_RISING_SIDE_ONLY_DEEPER_OF_TRAILING_PULSE_FLOOR_AND_CAUSAL_RUNNING_OWN_REACH_LOW", sanity_bound: "EVERY_REST_STRICTLY_BELOW_CURRENT_BEST_ASK", take_path: "V36_MATURE_FLOOR_TAKE_INTACT", pair_cap: "99_MINUS_FIRST_FILL", clocks_as_decision_inputs: [], hard_prebell_edge: "V36_WINDOW1_SPAN_804_UNCHANGED" }, fill_rulers: { market_scoring: "UNION_REACH_CHANNELS_QUOTE_TOUCH_10S_SIZE5_PLUS_TRADED_AT_LEVEL_PLUS_STRICT_PRINT_CROSS", build_verification: "STRICT_SELLER_AGGRESSED_PRINT_SIZE5_AT_OR_BELOW_PRIOR_REST_PLUS_PROVEN_TAKER", never_swapped: true } }
    : { schema_version: "window1-v38-maker-only-control-v1", parent: GAP_COMMIT, frozen_V36: V36_COMMIT, frozen_union_reach: REACH_COMMIT, sealed_divot_census: DIVOT_COMMIT, architecture: { entry_actions: ["PLACE_REST", "REPRICE_REST"], take_path: "REMOVED_FROM_POLICY_SOURCE_NOT_GATED", FALLING: "V36_NO_CHASE_WALKING_REST_UNCHANGED", RISING: `REST_AT_LOWEST_ASK_LEVEL_WITH_AT_LEAST_${policy.PULSE_REVISIT_MIN}_DISTINCT_VISITS_INSIDE_EXISTING_${policy.LOOKBACK_SECONDS}S_RECEIPT_HORIZON; POST_ONLY_REQUIRES_STANDING_ASK_ABOVE_NEW_REST`, SETTLED: "BID_MINUS_ONE_TRACKING", pair_cap: "99_MINUS_FIRST_FILL", clocks_as_decision_inputs: [], hard_prebell_edge: "V36_WINDOW1_SPAN_804_UNCHANGED" }, fill_rulers: { market_scoring: "UNION_REACH_CHANNELS_QUOTE_TOUCH_10S_SIZE5_PLUS_TRADED_AT_LEVEL_PLUS_STRICT_PRINT_CROSS", build_verification: "STRICT_SELLER_AGGRESSED_PRINT_SIZE5_AT_OR_BELOW_PRIOR_REST", never_swapped: true } };
  const pulseBinding = { commit: DIVOT_COMMIT, path: ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_DIVOT_CENSUS.json", source_sha256: fileHash(path.join(reachRoot, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_DIVOT_CENSUS.json")), adopted: { ask_side_dwell_10s_depth_median_cents: 1, ask_side_dwell_10s_depth_p90_cents: 2, trailing_horizon_seconds: policy.LOOKBACK_SECONDS, minimum_distinct_level_visits: policy.PULSE_REVISIT_MIN }, causal_revisit_definition: "ASK_LEVEL_ENTRY_AFTER_A_DIFFERENT_PRIOR_ASK; UNCHANGED RECORDER SNAPSHOTS DO_NOT INCREMENT VISITS" };
  const directionTelemetry = classifierTelemetry(marketEvents);
  const counterPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/PLACEMENT_LAW_COUNTERFACTUAL_V2.json";
  const counterBytes = isV39 ? gitShow(COUNTERFACTUAL_COMMIT, counterPath) : null;
  const counterReceipt = isV39 ? JSON.parse(counterBytes) : null;
  const anatomyPath = ".claude/window1_live_v4_replay/v36_faller_side_mirror_anatomy_20260807/FALLER_ISSUE_ANATOMY_399.jsonl.gz";
  const anatomyBytes = isV39 ? gitShow(FALLER_ANATOMY_COMMIT, anatomyPath) : null;
  const anatomyMislabels = isV39 ? readRowsBytes(anatomyBytes).filter((row) => row.miss_taxonomy?.class === "STATE_MISLABELED") : [];
  const marketLegByIdentity = new Map(marketEvents.flatMap((event) => Object.values(event.legs).map((leg) => [leg.leg_identity, leg])));
  const reconstructedRecovery = anatomyMislabels.map((row) => {
    const identity = `${row.event_id}|${row.leg_id}`, leg = marketLegByIdentity.get(identity);
    return { event_id: row.event_id, leg_identity: identity, frozen_ex_post_direction: String(row.miss_taxonomy.reason).split(" was ").at(-1), v36_credited: row.v36_credited, v36_entry_cents: row.v36_entry_cents, union_reach_cents: row.reach_bottom_cents, v39_credited: Boolean(leg?.credited), v39_entry_cents: leg?.entry_cents ?? null, recovered_at_or_better_than_reach: Boolean(leg?.credited && Number.isInteger(row.reach_bottom_cents) && leg.entry_cents <= row.reach_bottom_cents) };
  });
  const mislabelRecovery = isV39 ? { controlling_counterfactual_denominator: counterReceipt.faller_mislabel.measured_ran_faller_on_nonfaller, controlling_counterfactual_forfeited: counterReceipt.faller_mislabel.forfeited, controlling_counterfactual_credited: counterReceipt.faller_mislabel.credited, identity_binding_status: "NOT_BOUND_IN_2B45D146_AGGREGATE_RECEIPT_SO_NO_FALSE_115_SIDE_NUMERATOR_IS_EMITTED", independently_reconstructable_c396_cohort: { sides: reconstructedRecovery.length, recovered_credited: reconstructedRecovery.filter((row) => row.v39_credited && !row.v36_credited).length, recovered_at_or_better_than_reach: reconstructedRecovery.filter((row) => row.recovered_at_or_better_than_reach && !row.v36_credited).length }, telemetry_law: "FROZEN_EX_POST_DIRECTION_USED_ONLY_AFTER_REPLAY; NEVER_PASSED_TO_POLICY" } : null;
  const marketLegs = marketEvents.flatMap((event) => Object.values(event.legs).map((leg) => ({ ...leg, category: event.category, bell_confidence: event.bell_confidence })));
  const sanity = isV39 ? { legs: marketLegs.length, bound_application_receipts: marketLegs.reduce((sum, leg) => sum + leg.sanity_bound_rows, 0), post_decision_rest_at_or_above_ask_violations: marketLegs.reduce((sum, leg) => sum + leg.sanity_violation_rows, 0), legs_with_violation: marketLegs.filter((leg) => leg.sanity_violation_rows > 0).length, violations_by_category_x_bell_confidence: countBy(marketLegs.filter((leg) => leg.sanity_violation_rows > 0), (leg) => `${leg.category}|${leg.bell_confidence}`) } : null;
  const v36Comparison = isV39 ? { frozen_commit: V36_COMMIT, frozen_score: v36Score, reach_answer_key_grade_from_b581cbb: { matched: 52, shallow: 212, one_missing: 486, both_missing: 35, no_reach: 19, completed_on_637_answer_key: 264 }, V39_market_union_reach: marketScore, V39_strict_build_verification: strictScore } : null;
  const namedCausality = isV39 ? {
    controlling_counterfactual: {
      commit: COUNTERFACTUAL_COMMIT,
      ruler: counterReceipt.ruler,
      warning: "THE COUNTERFACTUAL CREDITS UNION REACH AT THE REST LEVEL WITHOUT REQUIRING A STRICTLY LATER CAUSAL RECEIPT; V39 DOES NOT RETRO-CREDIT THAT HINDSIGHT CONVENTION",
    },
    ARNROM: {
      ordered_target: "ARN joins 50; pair 89",
      result: named.ARNROM.MARKET_UNION_REACH,
      adjudication: named.ARNROM.MARKET_UNION_REACH.completed && named.ARNROM.MARKET_UNION_REACH.combined_entry_cents === 89 ? "PASS" : "FAIL",
    },
    BOSCOP: {
      ordered_target: "COP joins 47; pair 77",
      result: named.BOSCOP.MARKET_UNION_REACH,
      adjudication: named.BOSCOP.MARKET_UNION_REACH.completed && named.BOSCOP.MARKET_UNION_REACH.combined_entry_cents === 77 ? "PASS" : "FAIL_CLOSED_NO_STRICTLY_LATER_UNION_REACH_AFTER_CAUSAL_JOIN",
      explanation: "COP causally joined 47 only after the persistent-level seller-hit receipt. No later quote-touch, traded-at-level, or print-cross receipt reached that resting order before the hard edge, so pair 77 is not credited.",
    },
    WESPAA: { role: "CAUSAL_CLASSIFIER_TEST_CASE", result: named.WESPAA.MARKET_UNION_REACH },
    NIKVRB: { role: "NEGATIVE_CONTROL_PERSISTENT_JOIN_DOES_NOT_OVERRIDE_PULSE_OR_INCUMBENT_PATH", result: named.NIKVRB.MARKET_UNION_REACH },
    GANJAN: { role: "NAMED_DAMAGE_REGRESSION", result: named.GANJAN.MARKET_UNION_REACH },
  } : null;
  const core = {
    "CONTROL_BINDING.json": canonical(control),
    ...(isV39 ? { "TAKE_PATH_INTACT_RECEIPT.json": canonical({ frozen_V36_commit: V36_COMMIT, V36_policy_path: "arb-executor/analysis/window1_v36_state_directional_rest_mature_floor.js", V36_policy_sha256: fileHash(path.join(v36Root, "arb-executor/analysis/window1_v36_state_directional_rest_mature_floor.js")), V39_policy_path: path.relative(repo, policyFile).replaceAll("\\", "/"), V39_policy_sha256: fileHash(policyFile), decision_reason: "V36_MATURE_EVIDENCE_FLOOR_TAKE_UNCHANGED", market_taker_fills: marketLegs.filter((leg) => String(leg.fill_class).includes("TAKER")).length, strict_taker_fills: strictEvents.flatMap((event) => Object.values(event.legs)).filter((leg) => String(leg.fill_class).includes("TAKER")).length, V38_tombstone_role: "REJECTED_MAKER_ONLY_NEGATIVE_CONTROL_NOT_INHERITED" }) } : { "TAKE_PATH_DELETION_RECEIPT.json": canonical({ policy_path: path.relative(repo, policyFile).replaceAll("\\", "/"), policy_sha256: fileHash(policyFile), forbidden_action_literal_TAKE_count: (policyText.match(/action:\s*["']TAKE["']/g) || []).length, take_named_function_count: (policyText.match(/function\s+\w*take\w*/gi) || []).length, entry_actions_exported: ["PLACE_REST", "REPRICE_REST"], pass: true }) }),
    "PULSE_FLOOR_BINDING.json": canonical(pulseBinding),
    "MARKET_GRADE_SCORECARD.json": canonical({ score: marketScore, reach_grade: marketGrades.aggregate, comparison_answer_key: EXPECTED_REACH }),
    "STRICT_BUILD_VERIFICATION_SCORECARD.json": canonical({ score: strictScore, reach_grade: strictGrades.aggregate, role: "BUILD_VERIFICATION_ONLY_NOT_MARKET_VALUE" }),
    "CATEGORY_X_BELL_CONFIDENCE.json": canonical({ MARKET_UNION_REACH: cellSummary(marketGrades), STRICT_PRINT_CROSS: cellSummary(strictGrades), conservation: { market_answer_key_D: marketGrades.classRows.length, strict_answer_key_D: strictGrades.classRows.length, expected: 637, pass: marketGrades.classRows.length === 637 && strictGrades.classRows.length === 637 } }),
    "REACH_GRADE_EVENT_LEDGER.jsonl.gz": gzipRows(marketGrades.classRows),
    "REACH_GRADE_LEG_LEDGER.jsonl.gz": gzipRows(marketGrades.rows),
    "RESIDUAL_LAYER_BIND_LEDGER.jsonl.gz": gzipRows(marketGrades.residuals),
    "LAYER_BIND_RANKING.json": canonical({ rows: layerRanking, conservation: { residual_sides: marketGrades.residuals.length, ranked_sides: layerRanking.reduce((sum, row) => sum + row.sides, 0), pass: marketGrades.residuals.length === layerRanking.reduce((sum, row) => sum + row.sides, 0) } }),
    ...(isV39 ? { "CAUSAL_DIRECTION_CLASSIFIER_TELEMETRY.json": canonical(directionTelemetry), "MISLABEL_RECOVERY_RECEIPT.json": canonical(mislabelRecovery), "MISLABEL_RECOVERY_LEDGER.jsonl.gz": gzipRows(reconstructedRecovery), "REST_SANITY.json": canonical(sanity), "V36_COMPARISON.json": canonical(v36Comparison) } : {}),
    "MARKET_EVENT_LEDGER.jsonl.gz": gzipRows(marketEvents),
    "STRICT_EVENT_LEDGER.jsonl.gz": gzipRows(strictEvents),
    "DECISION_TRACE_1608.jsonl.gz": gzipRows(marketGrades.rows.map((row) => ({ ...row, reach_snapshot: row.reach_snapshot, first_decision: marketEvents.find((event) => event.event_id === row.event_id).legs[row.leg_identity.split("|").at(-1)].first_decision, last_decision: marketEvents.find((event) => event.event_id === row.event_id).legs[row.leg_identity.split("|").at(-1)].last_decision }))),
    "NAMED_GAMES.json": canonical({ games: named, action_rows: allActions.filter((row) => ["ARNROM", "BOSCOP", "WESPAA", "NIKVRB", "GANJAN"].some((name) => row.event_id.includes(name)) && (row.kind === "FILL" || String(row.reason).includes("PERSISTENT_LEVEL_JOIN") || String(row.reason).includes("WTA_OTHER_EXPRESSION_FALLING"))) }),
    ...(isV39 ? { "NAMED_CAUSALITY_RECEIPT.json": canonical(namedCausality) } : {}),
    "FORBIDDEN_ACCESS_RECEIPT.json": canonical({ holdout_accesses: 0, live_accesses: 0, network_runtime_accesses: 0, order_accesses: 0, position_accesses: 0, exit_accesses: 0, settlement_accesses: 0, DCA_accesses: 0, deployment_accesses: 0, private_scope: "FIT_DEVELOPMENT_804_TAPE_AND_CERTIFIED_PRINT_CACHE_ONLY", mutations: 0 }),
    "SOURCE_HASH_MANIFEST.json": canonical({
      commits: { V36: V36_COMMIT, UNION_REACH: REACH_COMMIT, GAP_GRADE_PARENT: GAP_COMMIT, DIVOT_CENSUS: DIVOT_COMMIT, ...(isV39 ? { COUNTERFACTUAL: COUNTERFACTUAL_COMMIT, FALLER_ANATOMY: FALLER_ANATOMY_COMMIT } : {}) },
      public: {
        [path.relative(repo, policyFile).replaceAll("\\", "/")]: { sha256: fileHash(policyFile), bytes: fs.statSync(policyFile).size },
        [path.relative(repo, builderFile).replaceAll("\\", "/")]: { sha256: fileHash(builderFile), bytes: fs.statSync(builderFile).size },
        ...(isV39 ? { [path.relative(repo, wrapperFile).replaceAll("\\", "/")]: { sha256: fileHash(wrapperFile), bytes: fs.statSync(wrapperFile).size } } : {}),
        [`${GAP_PACKAGE}/UNION_REACH_LEG_LEDGER.jsonl.gz`]: { sha256: fileHash(path.join(gapPackage, "UNION_REACH_LEG_LEDGER.jsonl.gz")), bytes: fs.statSync(path.join(gapPackage, "UNION_REACH_LEG_LEDGER.jsonl.gz")).size },
        [`${GAP_PACKAGE}/V36_GAP_TO_REACH_LEG_LEDGER.jsonl.gz`]: { sha256: fileHash(path.join(gapPackage, "V36_GAP_TO_REACH_LEG_LEDGER.jsonl.gz")), bytes: fs.statSync(path.join(gapPackage, "V36_GAP_TO_REACH_LEG_LEDGER.jsonl.gz")).size },
      },
      frozen_V36: { WINDOW1_SPAN_804: { sha256: fileHash(path.join(v36Package, "WINDOW1_SPAN_804.json")), bytes: fs.statSync(path.join(v36Package, "WINDOW1_SPAN_804.json")).size }, STRICT_DECISION_TRACE_1608: { sha256: fileHash(path.join(v36Package, "STRICT_DECISION_TRACE_1608.json")), bytes: fs.statSync(path.join(v36Package, "STRICT_DECISION_TRACE_1608.json")).size } },
      git_bound_receipts: isV39 ? { [counterPath]: { commit: COUNTERFACTUAL_COMMIT, sha256: shaBytes(counterBytes), bytes: counterBytes.length }, [anatomyPath]: { commit: FALLER_ANATOMY_COMMIT, sha256: shaBytes(anatomyBytes), bytes: anatomyBytes.length } } : {},
      private_prints: printLoad.receipt,
      private_tapes: tapeHashes,
    }),
  };
  for (const [name, bytes] of Object.entries(core)) write(name, bytes);
  await writeGzipRowsFile(path.join(output, "ACTION_TRACE.jsonl.gz"), allActions);
  write("REPORT.md", isV39
    ? `# V39 corrected placement stack\n\nV39 runs on frozen V36 with its mature-floor take path intact. The receipt-causal direction classifier combines trailing quote-path and July-6 pressure without reading an ex-post path label; opposing directional votes settle. RISING sides may join a bid only after 300 seconds of continuous residency and a last-traded-at-level book receipt. WTA RISING sides whose other expression reads FALLING hold to the deeper causal pulse/reach level. Every rest is strictly below the current ask.\n\nMarket grade uses the CANON union-reach channels; strict seller-print crossing plus proven takes is build verification.\n\n- V36 frozen completed / under par: ${v36Score.completed_pairs} / ${v36Score.under_par_pairs}.\n- V39 market completed / under par: ${marketScore.completed_pairs} / ${marketScore.under_par_pairs}. This regresses the frozen V36 count and therefore does not supersede V36.\n- Market reach grades across 637 games / 5,253c: ${JSON.stringify(marketGrades.aggregate.grades)}; shallow ${marketGrades.aggregate.shallow_gap_cents.sum}c; measurable residual ${marketGrades.aggregate.measurable_residual_cents.sum}c.\n- Strict verification completed / under par: ${strictScore.completed_pairs} / ${strictScore.under_par_pairs}.\n- Direction telemetry: ${directionTelemetry.aggregate.correct_receipts}/${directionTelemetry.aggregate.eligible_receipts} eligible receipt calls correct and ${directionTelemetry.aggregate.reach_moment_correct_legs}/${directionTelemetry.aggregate.reach_moment_eligible_legs} reach-moment legs correct; ex-post labels consumed by policy: 0.\n- The 2b45d146 115-side cohort has no frozen identity list, so recovery is not fabricated; the independently reproducible c3961e2c cohort has ${mislabelRecovery.independently_reconstructable_c396_cohort.sides} sides and ${mislabelRecovery.independently_reconstructable_c396_cohort.recovered_at_or_better_than_reach} previously uncredited sides recovered at/better than reach.\n- Rest sanity: ${sanity.post_decision_rest_at_or_above_ask_violations} violations after ${sanity.bound_application_receipts} bound applications.\n- Named market outcomes: ARNROM ${named.ARNROM.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; BOSCOP ${named.BOSCOP.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; WESPAA ${named.WESPAA.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}; NIKVRB ${named.NIKVRB.MARKET_UNION_REACH.combined_entry_cents ?? "INCOMPLETE"}. BOSCOP causally joined COP at 47 but had no strictly later union-reach receipt; the 2b45d146 counterfactual's pair-77 credit is not replay-causal and is not imported.\n`
    : `# V38 maker-only machine\n\nV38 removes the take path from the executable policy source. FALLING preserves V36 no-chase rest behavior; SETTLED tracks bid minus one; RISING rests at the lowest ask level revisited at least twice inside the inherited 300-second receipt horizon, only after the standing ask has moved above that floor so the new order remains post-only. Pair cap, lazy first-fill coupling, no-clock law, and the V36 hard pre-bell edge remain intact.\n\nMarket grade uses the CANON union reach ruler; strict seller-print crossing is printed only as build verification.\n\n- Market completed / under par: ${marketScore.completed_pairs} / ${marketScore.under_par_pairs}.\n- Market reach grades across the 637-game answer key: ${JSON.stringify(marketGrades.aggregate.grades)}.\n- Market shallow gap cents: ${marketGrades.aggregate.shallow_gap_cents.sum}; measurable residual cents: ${marketGrades.aggregate.measurable_residual_cents.sum}.\n- Strict verification completed / under par: ${strictScore.completed_pairs} / ${strictScore.under_par_pairs}.\n- Named reach: ARNROM ${named.ARNROM.reach_combined_cents}; BOSCOP ${named.BOSCOP.reach_combined_cents}; NIKVRB ${named.NIKVRB.reach_combined_cents}; GANJAN ${named.GANJAN.reach_combined_cents}.\n`);
  const namesBeforeDeterminism = fs.readdirSync(output).sort();
  let determinism;
  if (compare) {
    const mismatches = namesBeforeDeterminism.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name)));
    const extra = fs.readdirSync(compare).filter((name) => ![...namesBeforeDeterminism, "DETERMINISM_RECEIPT.json", "ARTIFACT_HASH_MANIFEST.json"].includes(name));
    ensure(!mismatches.length && !extra.length, `determinism mismatch: ${[...mismatches, ...extra].join(",")}`);
    determinism = { clean_builds: 2, compared_files: namesBeforeDeterminism.length, byte_identical: true, mismatches: [] };
  } else determinism = { clean_builds: 1, byte_identical: null, role: "FIRST_BUILD" };
  write("DETERMINISM_RECEIPT.json", canonical(determinism));
  writeManifest(output);
  if (compare) {
    fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism));
    writeManifest(compare);
    ensure(fileHash(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(output, "ARTIFACT_HASH_MANIFEST.json")), "finalized artifact manifests differ");
  }
  process.stdout.write(canonical({ output, MARKET_UNION_REACH: marketScore, STRICT_PRINT_CROSS: strictScore, reach_grade: marketGrades.aggregate, named }));
}

main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
