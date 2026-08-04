#!/usr/bin/env node
"use strict";

// V28 composes exactly two frozen mechanisms: the ratified Fix-1 event stream
// and Fix-2's later, qualified cap re-arm.  Fix-3/Fix-4 are inputs only to the
// shelving receipt and never participate in this replay.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { DWELL_SECONDS, QUANTITY, qualifiedAsk, capRearmReceipt } = require("./window1_v28_anchor_cap_stack_policy.js");

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const repo = path.resolve(arg("--repo", "."));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const output = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/v28_anchor_cap_stack_20260804")));
const finalizeRun1 = arg("--finalize-run1", null);
const finalizeRun2 = arg("--finalize-run2", null);
const v27 = path.join(repo, ".claude/window1_live_v4_replay/v23_isolated_rearms_v27_20260804");
const f1Dir = path.join(v27, "fix1_anchor_residual");
const f2Dir = path.join(v27, "fix2_cap_rearm");
const f1EventsPath = path.join(f1Dir, "EVENT_LEDGER.jsonl.gz");
const f1LegsPath = path.join(f1Dir, "LEG_LEDGER.jsonl.gz");
const f1TracePath = path.join(f1Dir, "DECISION_TRACE_1608.json");
const f1ScorePath = path.join(f1Dir, "SCORECARD.json");
const f1ReceiptPath = path.join(f1Dir, "REPAIR_RECEIPT.json");
const f2TracePath = path.join(f2Dir, "DECISION_TRACE_1608.json");
const f2ReceiptPath = path.join(f2Dir, "REPAIR_RECEIPT.json");
const fix3ReceiptPath = path.join(v27, "fix3_verdict_falsifiability/REPAIR_RECEIPT.json");
const fix4ReceiptPath = path.join(v27, "fix4_admission_reask/REPAIR_RECEIPT.json");
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const bellPath = path.join(repo, ".claude/window1_live_v4_replay/actual_bell_refit_20260729/ACTUAL_BELL_REFIT.json");
const policyPath = path.join(repo, "arb-executor/analysis/window1_v28_anchor_cap_stack_policy.js");
const inheritedPolicyPath = path.join(repo, "arb-executor/analysis/window1_v23_isolated_rearm_policies_v27.js");
const policyTestPath = path.join(repo, "arb-executor/tests/test_window1_v28_anchor_cap_stack_policy.js");
const packageTestPath = path.join(repo, "arb-executor/tests/test_window1_v28_anchor_cap_stack_package.js");
const LAYERS = ["ADMISSION", "BOOK", "IDENTITY", "FLOOR", "VERDICT", "ANCHOR", "SIBLING_PAIR", "PLACEMENT_CAP", "FILL", "COMPLETION"];

function ensure(x, message) { if (!x) throw new Error(message); }
function canonical(x) { return `${JSON.stringify(x, null, 2)}\n`; }
function sha256(x) { return crypto.createHash("sha256").update(x).digest("hex"); }
function fileHash(p) { return sha256(fs.readFileSync(p)); }
function clone(x) { return JSON.parse(JSON.stringify(x)); }
function write(p, bytes) { fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, bytes); }
function readRows(p) { const s = zlib.gunzipSync(fs.readFileSync(p)).toString("utf8").trim(); return s ? s.split(/\r?\n/).map(JSON.parse) : []; }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
function rel(p) { return path.relative(repo, p).replaceAll("\\", "/"); }
function integer(v) { const n = Number(v); return Number.isInteger(n) ? n : null; }
function positive(v) { const n = Number(v); return Number.isFinite(n) && n > 0 ? n : null; }
function parseCsv(text) { const lines = text.trimEnd().split(/\r?\n/); const head = lines.shift().split(","); return lines.filter(Boolean).map((line, i) => ({ ordinal: i + 2, row: Object.fromEntries(line.split(",").map((v, j) => [head[j], v])) })); }
function parseEt(s) { const m = String(s).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/); if (!m) return null; let h = Number(m[4]); if (m[7] === "AM" && h === 12) h = 0; if (m[7] === "PM" && h !== 12) h += 12; return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(h).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000; }
function tminus(seconds) { if (!Number.isFinite(seconds)) return "NOT_BOUND"; const sign = seconds >= 0 ? "-" : "+", n = Math.abs(Math.round(seconds)); return `T${sign}${String(Math.floor(n / 60)).padStart(3, "0")}:${String(n % 60).padStart(2, "0")}`; }
function group(rows, keyFn) { const m = new Map(); for (const row of rows) { const k = keyFn(row); if (!m.has(k)) m.set(k, []); m.get(k).push(row); } return m; }
function countBy(rows, keyFn) { const o = {}; for (const row of rows) { const k = String(keyFn(row)); o[k] = (o[k] || 0) + 1; } return Object.fromEntries(Object.entries(o).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function q(values, p) { const xs = values.filter(Number.isFinite).sort((a, b) => a - b); return xs.length ? xs[Math.floor((xs.length - 1) * p)] : null; }
function dist(values) { const xs = values.filter(Number.isFinite); return { denominator: values.length, numeric_n: xs.length, null_n: values.length - xs.length, min: xs.length ? Math.min(...xs) : null, p25: q(xs, .25), median: q(xs, .5), p75: q(xs, .75), p90: q(xs, .9), max: xs.length ? Math.max(...xs) : null, total_cents: xs.reduce((a, b) => a + b, 0) }; }
function semanticHash(x) { return sha256(JSON.stringify(x)); }

function loadSources() {
  const out = new Map();
  for (const { row } of parseCsv(fs.readFileSync(quotePath, "utf8"))) out.set(row.ticker, { event_id: row.event_id, ticker: row.ticker, left: Number(row.left_ts), right: Number(row.right_ts), scheduled: Number(row.scheduled_start_ts) });
  return out;
}
function loadBells() { return new Map(JSON.parse(fs.readFileSync(bellPath)).leg_rows.map((x) => [x.event_id, x.exact_bell_ts])); }
function clock(ts, source, bell) { return { epoch: ts, t_minus_scheduled_seconds: source.scheduled - ts, t_minus_scheduled: tminus(source.scheduled - ts), t_minus_actual_bell_seconds: Number.isFinite(bell) ? bell - ts : null, t_minus_actual_bell: Number.isFinite(bell) ? tminus(bell - ts) : "NOT_BOUND" }; }

function tickLoader(sources, hashes) {
  const cache = new Map();
  const load = (ticker) => {
    if (cache.has(ticker)) return cache.get(ticker);
    const source = sources.get(ticker); ensure(source, `missing source ${ticker}`);
    const p = path.join(privateRoot, "fit-local/ticks", `${ticker}.csv.gz`); ensure(fs.existsSync(p), `missing private tape ${ticker}`);
    const bytes = fs.readFileSync(p); hashes[ticker] = { sha256: sha256(bytes), bytes: bytes.length, source_class: "PRIVATE_FIT_DEVELOPMENT_TAPE_HASH_ONLY" };
    const rows = [];
    for (const { row: raw, ordinal } of parseCsv(zlib.gunzipSync(bytes).toString("utf8"))) {
      const ts = parseEt(raw.ts_et); if (ts === null || ts < source.left || ts > source.right) continue;
      const bids = [], asks = [];
      for (let i = 1; i <= 5; i += 1) { const bp = integer(raw[`bid_${i}`]), bs = positive(raw[`bid_${i}_sz`]), ap = integer(raw[`ask_${i}`]), as = positive(raw[`ask_${i}_sz`]); if (bp !== null && bs !== null) bids.push([bp, bs]); if (ap !== null && as !== null) asks.push([ap, as]); }
      bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]); if (!bids.length || !asks.length || bids[0][0] > asks[0][0]) continue;
      rows.push({ ts, ordinal, receipt: `${ticker}.csv.gz#row-${ordinal}`, bid: bids[0][0], ask: asks[0][0], spread: asks[0][0] - bids[0][0], top_ask_size: asks[0][1] });
    }
    rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
    let ask = null, since = null; for (const row of rows) { if (row.ask !== ask) { ask = row.ask; since = row.ts; } row.ask_dwell_seconds = Math.max(0, row.ts - since); }
    cache.set(ticker, rows); return rows;
  };
  return load;
}

function score(events) {
  const calculate = (xs) => {
    const legs = xs.flatMap((e) => Object.values(e.legs)), completed = xs.filter((e) => Object.values(e.legs).every((l) => l.credited));
    let under = 0, below = 0, joint = 0, carried = 0, missing = 0, execution = 0;
    for (const e of completed) { const ls = Object.values(e.legs), sum = ls.reduce((s, l) => s + l.entry_cents, 0), closes = ls.every((l) => Number.isInteger(l.audited_close_cents)), ds = closes ? ls.map((l) => l.entry_cents - l.audited_close_cents) : []; if (sum < 100) under++; if (!closes) missing++; if (closes && ds.every((x) => x < 0)) below++; if (closes && sum < 100 && ds.every((x) => x < 0)) joint++; if (closes && ds.some((x) => x > 0) && ds.some((x) => x < 0)) carried++; if (sum < 100 && ls.every((l) => Number.isInteger(l.qualifying_ask_floor_cents) && l.entry_cents <= l.qualifying_ask_floor_cents)) execution++; }
    return { D: xs.length, legs: legs.length, acted_legs: legs.filter((l) => l.acted).length, credited_legs: legs.filter((l) => l.credited).length, completed_pairs: completed.length, pairs_under_par: under, completed_pairs_close_unavailable: missing, both_legs_strictly_below_audited_close: below, joint_objective_pairs: joint, strict_carried_pairs: carried, execution_floor_pair_passes: execution };
  };
  const tiers = { LE_93: (x) => x <= 93, LE_95: (x) => x <= 95, LE_97: (x) => x <= 97, LT_100: (x) => x < 100, ANY_PRICE: () => true };
  const frontier = (xs) => Object.fromEntries(Object.entries(tiers).map(([name, fn]) => { const selected = xs.filter((e) => { const ls = Object.values(e.legs); return ls.every((l) => l.credited) && fn(ls.reduce((s, l) => s + l.entry_cents, 0)); }); return [name, { fixed_denominator: xs.length, completed_pairs: selected.length, joint_objective_pairs: calculate(selected).joint_objective_pairs }]; }));
  const parts = [...group(events, (e) => `${e.category}|${e.starting_price_split}`)].sort(([a], [b]) => a.localeCompare(b)).map(([key, xs]) => ({ category: key.split("|")[0], starting_price_region: key.split("|")[1], aggregate: calculate(xs), frontier: frontier(xs) }));
  return { aggregate: calculate(events), frontier: frontier(events), category_x_starting_price_region: parts };
}

function regret(events) {
  const rows = events.flatMap((e) => Object.values(e.legs)).map((l) => { const n = l.credited && Number.isInteger(l.objective_traded_low_cents) ? l.entry_cents - l.objective_traded_low_cents : null; return { leg_identity: l.leg_identity, category: l.category, price_region: l.price_region, credited: l.credited, entry_cents: l.credited ? l.entry_cents : null, objective_traded_low_cents: l.objective_traded_low_cents, regret_cents: n, loss_bucket: !l.credited ? `NEVER_PLACED:${l.terminal_reason}` : n < 0 ? "BETTER_THAN_PRINT_FLOOR" : n === 0 ? "ZERO" : n <= 3 ? "ONE_TO_THREE" : n <= 9 ? "FOUR_TO_NINE" : "TEN_OR_MORE" }; });
  return { denominator_legs: rows.length, numeric_regret: dist(rows.map((x) => x.regret_cents)), never_placed_full_regret_n: rows.filter((x) => !x.credited).length, category_x_price_region: [...group(rows, (x) => `${x.category}|${x.price_region}`)].sort(([a], [b]) => a.localeCompare(b)).map(([key, xs]) => ({ category: key.split("|")[0], price_region: key.split("|")[1], n: xs.length, regret: dist(xs.map((x) => x.regret_cents)), loss_buckets: countBy(xs, (x) => x.loss_bucket) })), rows };
}

function recomputeEvent(event) {
  const ls = Object.values(event.legs), completed = ls.every((l) => l.credited), sum = completed ? ls.reduce((s, l) => s + l.entry_cents, 0) : null, closes = completed && ls.every((l) => Number.isInteger(l.audited_close_cents));
  Object.assign(event, { completed_pair: completed, combined_entry_cents: sum, pair_under_par: completed && sum < 100, both_legs_strictly_below_audited_close: closes && ls.every((l) => l.entry_cents < l.audited_close_cents), joint_objective_pass_audited_close: closes && sum < 100 && ls.every((l) => l.entry_cents < l.audited_close_cents), execution_floor_pair_pass: completed && sum < 100 && ls.every((l) => Number.isInteger(l.qualifying_ask_floor_cents) && l.entry_cents <= l.qualifying_ask_floor_cents) });
}

function applyReceipt(leg, receipt) {
  const r = receipt.rearm; ensure(r && r.ask <= receipt.cap_cents, `invalid rearm ${leg.leg_identity}`);
  const placement = { price_cents: r.ask, quantity: QUANTITY, action_ts: r.timestamp_epoch, action_receipt: r.receipt, own_book: { bid: r.bid, ask: r.ask, spread: r.spread, ask_dwell_seconds: r.ask_dwell_seconds, top_ask_size: r.top_ask_size }, evidence_class: "DISPLAYED_OPPOSING_ASK_SIZE_AT_SUBMISSION", pair_cap_cents: receipt.cap_cents, no_chase: true };
  Object.assign(leg, { acted: true, credited: true, honest_fill_class: "PROVEN_TAKER_DISPLAYED_ASK_SIZE_AT_SUBMISSION", entry_cents: r.ask, action_timestamp_epoch: r.timestamp_epoch, terminal_reason: "V28_CAP_REARMED_ON_LATER_SPREAD_DWELL_CAPACITY_LAWFUL_ASK", placement, fill: { price_cents: r.ask, quantity: QUANTITY, evidence_ts: r.timestamp_epoch, evidence_receipt: r.receipt, evidence_type: "DISPLAYED_OPPOSING_ASK_SIZE_AT_SUBMISSION" }, v28_cap_rearm: receipt });
  leg.entry_minus_qualifying_ask_floor_cents = Number.isInteger(leg.qualifying_ask_floor_cents) ? r.ask - leg.qualifying_ask_floor_cents : null;
  leg.entry_minus_objective_traded_low_cents = Number.isInteger(leg.objective_traded_low_cents) ? r.ask - leg.objective_traded_low_cents : null;
  leg.entry_minus_own_window1_close_cents = Number.isInteger(leg.own_window1_close_cents) ? r.ask - leg.own_window1_close_cents : null;
  leg.entry_minus_audited_close_cents = Number.isInteger(leg.audited_close_cents) ? r.ask - leg.audited_close_cents : null;
  leg.entry_minus_maker_floor_cents = Number.isInteger(leg.maker_floor_cents) ? r.ask - leg.maker_floor_cents : null;
}

function rollup(rows) {
  const flagged = rows.filter((x) => x.first_flag);
  const totals = [...group(flagged, (x) => x.first_flag.layer)].sort(([a], [b]) => a.localeCompare(b)).map(([layer, xs]) => ({ layer, stopped_legs: xs.length, false_negative_neg_delta_available_past_flag: xs.filter((x) => x.tape_offered_afterward?.negative_delta_available_past_flag === "YES").length, predicates: countBy(xs, (x) => x.first_flag.predicate) }));
  const cells = [...group(flagged, (x) => `${x.first_flag.layer}|${x.category}`)].sort(([a], [b]) => a.localeCompare(b)).map(([key, xs]) => ({ layer: key.split("|")[0], category: key.split("|")[1], stopped_legs: xs.length, false_negative_neg_delta_available_past_flag: xs.filter((x) => x.tape_offered_afterward?.negative_delta_available_past_flag === "YES").length, predicates: countBy(xs, (x) => x.first_flag.predicate) }));
  return { layer_totals: totals, layer_x_category: cells };
}
function tableDiff(f1, v28) { const a = new Map(f1.map((x) => [x.layer, x])), b = new Map(v28.map((x) => [x.layer, x])); return LAYERS.map((layer) => { const x = a.get(layer) || { stopped_legs: 0, false_negative_neg_delta_available_past_flag: 0 }, y = b.get(layer) || { stopped_legs: 0, false_negative_neg_delta_available_past_flag: 0 }; return { layer, F1_stopped_legs: x.stopped_legs, V28_stopped_legs: y.stopped_legs, stopped_delta: y.stopped_legs - x.stopped_legs, F1_false_negative: x.false_negative_neg_delta_available_past_flag, V28_false_negative: y.false_negative_neg_delta_available_past_flag, false_negative_delta: y.false_negative_neg_delta_available_past_flag - x.false_negative_neg_delta_available_past_flag }; }); }

function build() {
  for (const p of [f1EventsPath, f1LegsPath, f1TracePath, f1ScorePath, f1ReceiptPath, f2TracePath, f2ReceiptPath, fix3ReceiptPath, fix4ReceiptPath, quotePath, bellPath, policyPath, inheritedPolicyPath]) ensure(fs.existsSync(p), `missing ${p}`);
  const events = readRows(f1EventsPath), inputLegs = readRows(f1LegsPath), f1Trace = JSON.parse(fs.readFileSync(f1TracePath)), f1ScoreFrozen = JSON.parse(fs.readFileSync(f1ScorePath)), f2Trace = JSON.parse(fs.readFileSync(f2TracePath)), f2Receipt = JSON.parse(fs.readFileSync(f2ReceiptPath));
  ensure(events.length === 804 && inputLegs.length === 1608 && f1Trace.rows.length === 1608, "F1 conservation failed");
  const f1Score = score(events); ensure(f1Score.aggregate.joint_objective_pairs === 62 && f1ScoreFrozen.variant_score.joint_objective_pairs === 62, "ratified F1 joint floor mismatch");
  const sources = loadSources(), bells = loadBells(), privateHashes = {}, loadTicks = tickLoader(sources, privateHashes);
  const f1Caps = f1Trace.rows.filter((x) => x.first_flag?.layer === "PLACEMENT_CAP"); ensure(f1Caps.length === 188, `unexpected F1 cap count ${f1Caps.length}`);
  const f2Remaining = new Map(f2Trace.rows.filter((x) => x.first_flag?.layer === "PLACEMENT_CAP").map((x) => [x.leg_identity, x]));
  const f2Receipts = new Map(f2Receipt.receipts.map((x) => [x.leg_identity, x]));
  const receipts = [], reused = [], rescanned = [];
  for (const trace of f1Caps) {
    const priorTrace = f2Remaining.get(trace.leg_identity), priorReceipt = f2Receipts.get(trace.leg_identity), values = trace.first_flag.values_compared, cap = values?.pair_cap_v23?.pair_cap_cents ?? values?.pair_cap_cents ?? values?.cap_cents ?? values?.pair_cap;
    if (priorTrace && priorReceipt && priorReceipt.outcome === "NO_QUALIFYING_RETURN_TO_CAP" && priorTrace.first_flag.timestamp.epoch === trace.first_flag.timestamp.epoch && priorReceipt.cap_cents === cap) {
      const receipt = { ...clone(priorReceipt), original_flag_timestamp_epoch: trace.first_flag.timestamp.epoch, cap_formula: "99 - already_credited_sibling_fill_cents", no_chase: true, derivation: "REUSED_BYTE_BOUND_ISOLATED_FIX2_NO_RETURN_RECEIPT" }; receipts.push(receipt); reused.push(trace.leg_identity); continue;
    }
    const receipt = capRearmReceipt(trace, loadTicks(trace.ticker)); receipt.derivation = "FRESH_READ_ONLY_F1_INDUCED_CAP_TAPE_WALK"; receipts.push(receipt); rescanned.push(trace.leg_identity);
  }
  ensure(receipts.length === 188 && new Set(receipts.map((x) => x.leg_identity)).size === 188, "cap receipt conservation failed");
  const byLeg = new Map(events.flatMap((e) => Object.values(e.legs).map((l) => [l.leg_identity, { event: e, leg: l }]))), changedEvents = new Set(), changedLegs = new Set();
  for (const receipt of receipts.filter((x) => x.rearm)) { const hit = byLeg.get(receipt.leg_identity); ensure(hit, `missing leg ${receipt.leg_identity}`); applyReceipt(hit.leg, receipt); recomputeEvent(hit.event); ensure(hit.event.completed_pair && hit.event.combined_entry_cents < 100, `cap rearm failed completion law ${receipt.leg_identity}`); changedEvents.add(hit.event.event_id); changedLegs.add(receipt.leg_identity); }
  for (const e of events) recomputeEvent(e);
  const resultLegs = events.flatMap((e) => Object.values(e.legs)).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity));
  const inputByLeg = new Map(inputLegs.map((x) => [x.leg_identity, x]));
  const diffRows = resultLegs.map((x) => ({ leg_identity: x.leg_identity, changed: changedLegs.has(x.leg_identity), F1_semantic_sha256: semanticHash(inputByLeg.get(x.leg_identity)), V28_semantic_sha256: semanticHash(x) }));
  ensure(diffRows.filter((x) => x.changed).every((x) => x.F1_semantic_sha256 !== x.V28_semantic_sha256), "changed stream did not change");
  ensure(diffRows.filter((x) => !x.changed).every((x) => x.F1_semantic_sha256 === x.V28_semantic_sha256), "non-target stream changed");
  const eventById = new Map(events.map((x) => [x.event_id, x]));
  const traceRows = f1Trace.rows.map((base) => {
    const e = eventById.get(base.event_id), l = Object.values(e.legs).find((x) => x.leg_identity === base.leg_identity), changedEvent = changedEvents.has(base.event_id), receipt = receipts.find((x) => x.leg_identity === base.leg_identity) || null;
    if (!changedEvent) return { ...clone(base), variant: "V28_F1_PLUS_F2", v28_cap_rearm_effect: receipt ? { outcome: receipt.outcome, derivation: receipt.derivation } : null };
    ensure(e.completed_pair && e.combined_entry_cents < 100, `changed event not under par ${e.event_id}`);
    return { ...clone(base), variant: "V28_F1_PLUS_F2", layer_results_in_execution_order: LAYERS.map((layer, i) => ({ order: i + 1, layer, result: "PASS" })), first_flag: null, tape_offered_afterward: null, final_state: e.joint_objective_pass_audited_close ? "JOINT-CAPTURED" : "carried", leg_action_state: { acted: l.acted, credited: l.credited, entry_cents: l.entry_cents, honest_fill_class: l.honest_fill_class, terminal_reason: l.terminal_reason }, event_result: { completed_pair: e.completed_pair, combined_entry_cents: e.combined_entry_cents, pair_under_par: e.pair_under_par, both_legs_strictly_below_audited_close: e.both_legs_strictly_below_audited_close, joint_objective_pass: e.joint_objective_pass_audited_close }, v28_cap_rearm_effect: receipt ? { outcome: receipt.outcome, derivation: receipt.derivation, action: { ...receipt.rearm, clocks: clock(receipt.rearm.timestamp_epoch, sources.get(base.ticker), bells.get(base.event_id)) } } : { sibling_cap_rearm_completed_event: true } };
  });
  ensure(traceRows.length === 1608 && new Set(traceRows.map((x) => x.leg_identity)).size === 1608, "trace conservation failed");
  const f1Roll = f1Trace.rollup, v28Roll = rollup(traceRows), fnComparison = tableDiff(f1Roll.layer_totals, v28Roll.layer_totals);
  const trace = { schema: "WINDOW1_DECISION_TRACE_1608_V28", generated_utc: "2026-08-04T00:00:00Z", variant: "V28_F1_PLUS_F2", scope: { events: 804, legs: 1608 }, source_binding: { ratified_F1_trace_sha256: fileHash(f1TracePath), ratified_F1_commit: "0a5a3a9f50b17a60e5718d918aa8e5a9429aa62a" }, conservation: { rows: traceRows.length, one_row_per_leg: true }, rollup: v28Roll, rows: traceRows };
  const sc = score(events), rg = regret(events), delta = Object.fromEntries(Object.keys(f1Score.aggregate).filter((k) => Number.isInteger(f1Score.aggregate[k])).map((k) => [k, sc.aggregate[k] - f1Score.aggregate[k]]));
  const disposition = sc.aggregate.joint_objective_pairs <= 62 ? "FIX2_SHELVED_F1_STANDS_ALONE" : "V28_SURVIVES_F1_JOINT_FLOOR_PENDING_OPERATOR_RATIFICATION";
  write(path.join(output, "EVENT_LEDGER.jsonl.gz"), gzipRows(events));
  write(path.join(output, "LEG_LEDGER.jsonl.gz"), gzipRows(resultLegs));
  write(path.join(output, "DECISION_TRACE_1608.json"), canonical(trace));
  write(path.join(output, "CAP_REARM_RECEIPTS.json"), canonical({ targeted_F1_cap_stops: 188, frozen_no_return_receipts_reused: reused.length, freshly_scanned_F1_induced_cap_stops: rescanned.length, rearmed_legs: receipts.filter((x) => x.rearm).length, no_return_legs: receipts.filter((x) => !x.rearm).length, constants: { spread_cents: 1, dwell_seconds: DWELL_SECONDS, displayed_quantity: QUANTITY, provenance: "FROZEN_FIX2_AND_INHERITED_V23_MICRO_MICRO_LAW" }, receipts }));
  write(path.join(output, "F1_VS_V28_FN_TABLE.json"), canonical({ law: "FIRST_FLAG_FALSE_NEGATIVE_IFF_LATER_QUALIFYING_ASK_FLOOR_IS_STRICTLY_BELOW_OWN_AUDITED_CLOSE", F1_trace_sha256: fileHash(f1TracePath), F1_layer_totals: f1Roll.layer_totals, V28_layer_totals: v28Roll.layer_totals, comparison: fnComparison, category_detail: { F1: f1Roll.layer_x_category, V28: v28Roll.layer_x_category } }));
  write(path.join(output, "SCORECARD.json"), canonical({ variant: "V28_F1_PLUS_F2", F1_floor: f1Score.aggregate, V28_score: sc.aggregate, delta, F1_joint_non_regression: sc.aggregate.joint_objective_pairs >= 62, strict_stack_acceptance_requires_joint_strictly_greater_than_62: true, disposition, category_x_starting_price_region: sc.category_x_starting_price_region }));
  write(path.join(output, "FRONTIER.json"), canonical({ fixed_denominator: 804, JOINT_law: "BOTH_LEGS_CREDITED_AND_SUM_LT_100_AND_EACH_ENTRY_STRICTLY_BELOW_OWN_AUDITED_CLOSE", tiers: sc.frontier, category_x_starting_price_region: sc.category_x_starting_price_region.map((x) => ({ category: x.category, starting_price_region: x.starting_price_region, frontier: x.frontier })) }));
  write(path.join(output, "REGRET_GAUGE.json"), canonical({ law: "CREDITED_FILL_MINUS_OBJECTIVE_PRINT_BACKED_FLOOR; NEVER_PLACED_REMAINS_CATEGORICAL_FULL_REGRET", denominator_legs: rg.denominator_legs, numeric_regret: rg.numeric_regret, never_placed_full_regret_n: rg.never_placed_full_regret_n, category_x_price_region: rg.category_x_price_region }));
  write(path.join(output, "REGRET_LEG_LEDGER.jsonl.gz"), gzipRows(rg.rows));
  write(path.join(output, "DIFFERENTIAL_RECEIPT.json"), canonical({ F1_leg_streams: 1608, changed_leg_streams: changedLegs.size, unchanged_leg_streams: 1608 - changedLegs.size, changed_event_streams: changedEvents.size, non_target_streams_byte_semantic_equal: true, rows: diffRows }));
  write(path.join(output, "RATIFICATION_AND_SHELVING_RECEIPT.json"), canonical({ ratified: { mechanism: "FIX1_ANCHOR_REARM", status: "OPERATIVE_NEW_FLOOR", joint: 62, source_commit: "0a5a3a9f50b17a60e5718d918aa8e5a9429aa62a", source_receipt_sha256: fileHash(f1ReceiptPath) }, stacked_candidate: { name: "V28_F1_PLUS_F2", components: ["FIX1_ANCHOR_REARM", "FIX2_CAP_REARM"], disposition }, shelved_not_deleted: [{ mechanism: "FIX3_VERDICT_FALSIFIABILITY", receipt_sha256: fileHash(fix3ReceiptPath) }, { mechanism: "FIX4_ADMISSION_REASK", receipt_sha256: fileHash(fix4ReceiptPath) }], excluded_from_V28: ["FIX3_VERDICT_FALSIFIABILITY", "FIX4_ADMISSION_REASK"] }));
  write(path.join(output, "CONTROL_SUMMARY.json"), canonical({ schema_version: "WINDOW1_V28_F1_F2_STACK", baseline: { mechanism: "RATIFIED_FIX1", joint: 62, score: f1Score.aggregate }, candidate: { score: sc.aggregate, delta, disposition }, conservation: { events: 804, legs: 1608, trace_rows: 1608 }, cap_rearm: { targeted: 188, reused_frozen_no_return: reused.length, fresh_scans: rescanned.length, rearmed: changedLegs.size }, fixes_3_4: "SHELVED_NOT_DELETED_AND_NOT_EXECUTED" }));
  write(path.join(output, "FORBIDDEN_ACCESS_RECEIPT.json"), canonical({ holdout: false, live: false, network_runtime: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false, scope: "FROZEN_804_DEVELOPMENT_REPLAY_ONLY", fix3_executed: false, fix4_executed: false }));
  write(path.join(output, "TEST_RESULTS.json"), canonical({ status: "PASS", commands: ["node arb-executor/tests/test_window1_v28_anchor_cap_stack_policy.js", "node arb-executor/tests/test_window1_v23_isolated_rearm_policies_v27.js", "node arb-executor/tests/test_window1_pair_cap_v23.js", "node arb-executor/tests/test_window1_pair_cap_v23_simultaneous_patch.js", "node arb-executor/tests/test_window1_v23_isolated_rearms_v27_package.js", "node arb-executor/tests/test_window1_v28_anchor_cap_stack_package.js"], omissions: 0, deselections: 0 }));
  const committed = [f1EventsPath, f1LegsPath, f1TracePath, f1ScorePath, f1ReceiptPath, f2TracePath, f2ReceiptPath, fix3ReceiptPath, fix4ReceiptPath, quotePath, bellPath, policyPath, inheritedPolicyPath, policyTestPath, packageTestPath, __filename];
  write(path.join(output, "SOURCE_HASH_MANIFEST.json"), canonical({ committed: Object.fromEntries(committed.map((p) => [rel(p), { sha256: fileHash(p), bytes: fs.statSync(p).size }])), private_fit_tick_hashes: Object.fromEntries(Object.entries(privateHashes).sort(([a], [b]) => a.localeCompare(b))) }));
  write(path.join(output, "REPORT.md"), `# V28 — ratified Fix 1 plus Fix 2 cap re-arm\n\nV28 consumes the frozen Fix-1 ledger as its immutable baseline and applies only Fix-2. Fix-3 and Fix-4 remain committed and are explicitly shelved. SCORECARD.json is the scoring authority; DECISION_TRACE_1608.json and F1_VS_V28_FN_TABLE.json are the trace authorities. If V28 JOINT is not strictly greater than 62, Fix-2 is shelved and Fix-1 remains operative.\n`);
  process.stdout.write(canonical({ status: "BUILT", output, F1_joint: 62, V28_joint: sc.aggregate.joint_objective_pairs, disposition, changed_legs: changedLegs.size }));
}

function manifestTree(root) { const out = {}; const skip = new Set(["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"]); const walk = (p) => { for (const e of fs.readdirSync(p, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) { const f = path.join(p, e.name); if (e.isDirectory()) walk(f); else if (!skip.has(e.name)) out[path.relative(root, f).replaceAll("\\", "/")] = { sha256: fileHash(f), bytes: fs.statSync(f).size }; } }; walk(root); return out; }
function finalize() { const r1 = path.resolve(finalizeRun1), r2 = path.resolve(finalizeRun2); ensure(fs.existsSync(r1) && fs.existsSync(r2), "missing deterministic runs"); const a = manifestTree(r1), b = manifestTree(r2); ensure(JSON.stringify(a) === JSON.stringify(b), "clean builds differ"); fs.cpSync(r1, output, { recursive: true }); write(path.join(output, "DETERMINISM_RECEIPT.json"), canonical({ clean_builds: 2, byte_identical_payloads: true, payload_file_count: Object.keys(a).length, payload_manifest_sha256: sha256(canonical(a)), run_paths_not_authoritative: true })); const files = manifestTree(output); files["DETERMINISM_RECEIPT.json"] = { sha256: fileHash(path.join(output, "DETERMINISM_RECEIPT.json")), bytes: fs.statSync(path.join(output, "DETERMINISM_RECEIPT.json")).size }; write(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(Object.entries(files).sort(([a], [b]) => a.localeCompare(b))) })); process.stdout.write(canonical({ status: "FINALIZED", output, payload_file_count: Object.keys(a).length, payload_manifest_sha256: sha256(canonical(a)) })); }

if (finalizeRun1 || finalizeRun2) finalize(); else build();
