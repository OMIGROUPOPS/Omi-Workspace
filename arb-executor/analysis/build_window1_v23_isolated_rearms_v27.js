#!/usr/bin/env node
"use strict";

// Four deliberately isolated V23 overlays.  This builder never stacks them.
// It consumes the frozen V23 event/leg ledgers and the frozen decision trace,
// then walks only the private development tape identities named by a repair.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const {
  DWELL_SECONDS, QUANTITY, qualifiedAsk, findAnchorRearm, findCapRearm,
  unfalsifiableLowerReceipt, findAdmissionReask,
} = require("./window1_v23_isolated_rearm_policies_v27.js");

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const repo = path.resolve(arg("--repo", "."));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const output = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/v23_isolated_rearms_v27_20260804")));
const finalizeRun1 = arg("--finalize-run1", null);
const finalizeRun2 = arg("--finalize-run2", null);
const baselineDir = path.join(repo, ".claude/window1_live_v4_replay/pair_cap_v23_audited_close_20260804");
const baselineEventPath = path.join(baselineDir, "V23_EVENT_LEDGER.jsonl.gz");
const baselineLegPath = path.join(baselineDir, "V23_LEG_LEDGER.jsonl.gz");
const baselineTracePath = path.join(repo, ".claude/window1_live_v4_replay/decision_trace_v23_20260804/DECISION_TRACE_1608.json");
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const bellPath = path.join(repo, ".claude/window1_live_v4_replay/actual_bell_refit_20260729/ACTUAL_BELL_REFIT.json");
const policyPath = path.join(repo, "arb-executor/analysis/window1_v23_isolated_rearm_policies_v27.js");

const VARIANTS = [
  ["FIX1_ANCHOR_RESIDUAL", "fix1_anchor_residual"],
  ["FIX2_CAP_REARM", "fix2_cap_rearm"],
  ["FIX3_VERDICT_FALSIFIABILITY", "fix3_verdict_falsifiability"],
  ["FIX4_ADMISSION_REASK", "fix4_admission_reask"],
];
const LAYERS = ["ADMISSION", "BOOK", "IDENTITY", "FLOOR", "VERDICT", "ANCHOR", "SIBLING_PAIR", "PLACEMENT_CAP", "FILL", "COMPLETION"];

function ensure(x, message) { if (!x) throw new Error(message); }
function canonical(x) { return `${JSON.stringify(x, null, 2)}\n`; }
function sha256(x) { return crypto.createHash("sha256").update(x).digest("hex"); }
function fileHash(p) { return sha256(fs.readFileSync(p)); }
function clone(x) { return JSON.parse(JSON.stringify(x)); }
function readRows(p) { const s = zlib.gunzipSync(fs.readFileSync(p)).toString("utf8").trim(); return s ? s.split(/\r?\n/).map(JSON.parse) : []; }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
function write(p, bytes) { fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, bytes); }
function rel(p) { return path.relative(repo, p).replaceAll("\\", "/"); }
function integer(v) { const n = Number(v); return Number.isInteger(n) ? n : null; }
function positive(v) { const n = Number(v); return Number.isFinite(n) && n > 0 ? n : null; }
function parseCsv(text) { const lines = text.trimEnd().split(/\r?\n/); const head = lines.shift().split(","); return lines.filter(Boolean).map((line, i) => ({ ordinal: i + 2, row: Object.fromEntries(line.split(",").map((v, j) => [head[j], v])) })); }
function parseEt(s) { const m = String(s).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/); if (!m) return null; let h = Number(m[4]); if (m[7] === "AM" && h === 12) h = 0; if (m[7] === "PM" && h !== 12) h += 12; return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(h).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000; }
function tminus(seconds) { if (!Number.isFinite(seconds)) return "NOT_BOUND"; const sign = seconds >= 0 ? "-" : "+"; const n = Math.abs(Math.round(seconds)); return `T${sign}${String(Math.floor(n / 60)).padStart(3, "0")}:${String(n % 60).padStart(2, "0")}`; }
function clock(ts, source, bell) { return { epoch: ts, timestamp_et: new Date(ts * 1000).toLocaleString("en-US", { timeZone: "America/New_York", hour12: true }), t_minus_scheduled_seconds: source.scheduled - ts, t_minus_scheduled: tminus(source.scheduled - ts), t_minus_actual_bell_seconds: Number.isFinite(bell) ? bell - ts : null, t_minus_actual_bell: Number.isFinite(bell) ? tminus(bell - ts) : "NOT_BOUND" }; }
function group(rows, keyFn) { const m = new Map(); for (const row of rows) { const k = keyFn(row); if (!m.has(k)) m.set(k, []); m.get(k).push(row); } return m; }
function countBy(rows, keyFn) { const o = {}; for (const row of rows) { const k = String(keyFn(row)); o[k] = (o[k] || 0) + 1; } return Object.fromEntries(Object.entries(o).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function q(values, p) { const xs = values.filter(Number.isFinite).sort((a, b) => a - b); return xs.length ? xs[Math.floor((xs.length - 1) * p)] : null; }
function dist(values) { const xs = values.filter(Number.isFinite); return { denominator: values.length, numeric_n: xs.length, null_n: values.length - xs.length, min: xs.length ? Math.min(...xs) : null, p25: q(xs, .25), median: q(xs, .5), p75: q(xs, .75), p90: q(xs, .9), max: xs.length ? Math.max(...xs) : null, total_cents: xs.reduce((a, b) => a + b, 0) }; }

function loadSources() {
  const map = new Map();
  for (const { row } of parseCsv(fs.readFileSync(quotePath, "utf8"))) map.set(row.ticker, { event_id: row.event_id, ticker: row.ticker, leg_id: row.leg, category: row.category, left: Number(row.left_ts), right: Number(row.right_ts), scheduled: Number(row.scheduled_start_ts), raw_bbo_rows: Number(row.raw_bbo_rows), distinct_top_states: Number(row.distinct_top_states), true_print_rows: Number(row.true_print_rows) });
  return map;
}
function loadBells() { return new Map(JSON.parse(fs.readFileSync(bellPath)).leg_rows.map((x) => [x.event_id, x.exact_bell_ts])); }
function tickLoader(sources, sourceHashes) {
  const cache = new Map();
  const load = (ticker) => {
    if (cache.has(ticker)) { const hit = cache.get(ticker); cache.delete(ticker); cache.set(ticker, hit); return hit; }
    const source = sources.get(ticker); ensure(source, `missing quote source ${ticker}`);
    const p = path.join(privateRoot, "fit-local/ticks", `${ticker}.csv.gz`); ensure(fs.existsSync(p), `missing private tick ${ticker}`);
    const bytes = fs.readFileSync(p); sourceHashes[ticker] = { sha256: sha256(bytes), bytes: bytes.length, source_class: "PRIVATE_FIT_DEVELOPMENT_TAPE_HASH_ONLY" };
    const rows = [];
    for (const { row: raw, ordinal } of parseCsv(zlib.gunzipSync(bytes).toString("utf8"))) {
      const ts = parseEt(raw.ts_et); if (ts === null || ts < source.left || ts > source.right) continue;
      const bids = [], asks = [];
      for (let i = 1; i <= 5; i += 1) { const bp = integer(raw[`bid_${i}`]), bs = positive(raw[`bid_${i}_sz`]), ap = integer(raw[`ask_${i}`]), as = positive(raw[`ask_${i}_sz`]); if (bp !== null && bs !== null) bids.push([bp, bs]); if (ap !== null && as !== null) asks.push([ap, as]); }
      bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]); if (!bids.length || !asks.length || bids[0][0] > asks[0][0]) continue;
      rows.push({ ts, ordinal, receipt: `${ticker}.csv.gz#row-${ordinal}`, bid: bids[0][0], ask: asks[0][0], spread: asks[0][0] - bids[0][0], top_ask_size: asks[0][1], top5_ask_depth: asks.reduce((s, x) => s + x[1], 0), asks, last_trade: integer(raw.last_trade) });
    }
    rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
    let ask = null, since = null;
    for (const row of rows) { if (row.ask !== ask) { ask = row.ask; since = row.ts; } row.ask_dwell_seconds = Math.max(0, row.ts - since); }
    cache.set(ticker, rows);
    while (cache.size > 4) cache.delete(cache.keys().next().value);
    return rows;
  };
  load.clear = () => cache.clear();
  return load;
}
function capacityAt(rows, price) { return rows.filter(([p]) => p <= price).reduce((s, [, n]) => s + n, 0); }
function laterMakerFill(rows, actionTs, actionReceipt, price) { return rows.find((x) => x.ts > actionTs && x.receipt !== actionReceipt && x.ask <= price && x.ask_dwell_seconds >= DWELL_SECONDS && capacityAt(x.asks, price) >= QUANTITY) || null; }
function postFlagFloor(rows, ts) { const xs = rows.filter((x) => x.ts >= ts && qualifiedAsk(x)); if (!xs.length) return null; const price = xs.reduce((m, x) => Math.min(m, x.ask), 100), first = xs.find((x) => x.ask === price); return { price_cents: price, timestamp_epoch: first.ts, receipt: first.receipt, bid: first.bid, ask: first.ask, spread: first.spread, ask_dwell_seconds: first.ask_dwell_seconds, top_ask_size: first.top_ask_size }; }

function baselineMetrics(events) { return score(events).aggregate; }
function score(events) {
  const calculate = (xs) => {
    const legs = xs.flatMap((e) => Object.values(e.legs)); const completed = xs.filter((e) => Object.values(e.legs).every((l) => l.credited));
    let under = 0, below = 0, joint = 0, carried = 0, missing = 0, execution = 0;
    for (const e of completed) { const ls = Object.values(e.legs), sum = ls.reduce((s, l) => s + l.entry_cents, 0); if (sum < 100) under += 1; const closes = ls.every((l) => Number.isInteger(l.audited_close_cents)); if (!closes) missing += 1; const ds = closes ? ls.map((l) => l.entry_cents - l.audited_close_cents) : []; if (closes && ds.every((x) => x < 0)) below += 1; if (closes && sum < 100 && ds.every((x) => x < 0)) joint += 1; if (closes && ds.some((x) => x > 0) && ds.some((x) => x < 0)) carried += 1; if (sum < 100 && ls.every((l) => Number.isInteger(l.qualifying_ask_floor_cents) && l.entry_cents <= l.qualifying_ask_floor_cents)) execution += 1; }
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

function setLegFromAction(leg, proposal, priorFill, loadTicks) {
  const rows = loadTicks(leg.ticker), cap = priorFill ? 99 - priorFill.entry_cents : null;
  const receipt = { ...proposal.receipt, pair_cap: cap, prior_credited_sibling: priorFill ? { leg_identity: priorFill.leg_identity, entry_cents: priorFill.entry_cents, action_timestamp_epoch: priorFill.action_timestamp_epoch } : null };
  if (Number.isInteger(cap) && proposal.row.ask > cap) {
    if (cap < proposal.row.bid) return { ...leg, acted: false, credited: false, entry_cents: null, action_timestamp_epoch: null, honest_fill_class: "UNPROVEN", terminal_reason: "PAIR_CAP_BELOW_CURRENT_LIVE_BID_UNREACHABLE_WITHOUT_CHASING", placement: null, isolated_repair_v27: { ...receipt, result: "CAP_ABSTAIN", live_bid: proposal.row.bid, live_ask: proposal.row.ask } };
    const fill = laterMakerFill(rows, proposal.row.ts, proposal.row.receipt, cap);
    return { ...leg, acted: true, credited: Boolean(fill), entry_cents: fill ? cap : null, action_timestamp_epoch: proposal.row.ts, honest_fill_class: fill ? "PROVEN_MAKER_BY_RESIDENCY_STRICTLY_LATER_QUALIFYING_ASK" : "UNPROVEN", terminal_reason: fill ? "ISOLATED_REPAIR_CAP_RESTED_AND_FILLED_LATER" : "ISOLATED_REPAIR_CAP_RESTED_UNFILLED", placement: { price_cents: cap, quantity: QUANTITY, action_ts: proposal.row.ts, action_receipt: proposal.row.receipt, same_receipt_fill_forbidden: true, isolated_repair_v27: receipt }, fill: fill ? { price_cents: cap, quantity: QUANTITY, evidence_ts: fill.ts, evidence_receipt: fill.receipt } : null, isolated_repair_v27: { ...receipt, result: fill ? "CAP_RESTED_FILLED" : "CAP_RESTED_UNFILLED", selected_price_cents: cap } };
  }
  return { ...leg, acted: true, credited: true, entry_cents: proposal.row.ask, action_timestamp_epoch: proposal.row.ts, honest_fill_class: "PROVEN_TAKER_DISPLAYED_ASK_SIZE_AT_SUBMISSION", terminal_reason: proposal.reason, placement: { price_cents: proposal.row.ask, quantity: QUANTITY, action_ts: proposal.row.ts, action_receipt: proposal.row.receipt, same_receipt_fill_forbidden: true, own_book: { bid: proposal.row.bid, ask: proposal.row.ask, spread: proposal.row.spread, ask_dwell_seconds: proposal.row.ask_dwell_seconds, top_ask_size: proposal.row.top_ask_size }, isolated_repair_v27: receipt }, fill: { price_cents: proposal.row.ask, quantity: QUANTITY, evidence_ts: proposal.row.ts, evidence_receipt: proposal.row.receipt, evidence_type: "DISPLAYED_OPPOSING_ASK_SIZE_AT_SUBMISSION" }, isolated_repair_v27: { ...receipt, result: "PROVEN_TAKER", selected_price_cents: proposal.row.ask } };
}
function replayExistingSecondUnderNewFirst(leg, priorFill, loadTicks) {
  if (!leg.acted || !Number.isFinite(leg.action_timestamp_epoch) || !priorFill || priorFill.action_timestamp_epoch >= leg.action_timestamp_epoch) return leg;
  const original = leg.credited ? leg.entry_cents : leg.placement?.price_cents; if (!Number.isInteger(original)) return leg;
  const cap = 99 - priorFill.entry_cents; if (original <= cap) return leg;
  const book = leg.placement?.pre_action_evidence?.own?.current_book || leg.action_book; if (!book || !Number.isInteger(book.bid) || !Number.isInteger(book.ask)) return leg;
  const rows = loadTicks(leg.ticker), after = postFlagFloor(rows, leg.action_timestamp_epoch);
  if (cap < book.bid) return { ...leg, acted: false, credited: false, entry_cents: null, honest_fill_class: "UNPROVEN", terminal_reason: "PAIR_CAP_REORDERED_BY_ISOLATED_REPAIR_ABSTAIN", placement: null, isolated_repair_v27_induced_cap: { cap_cents: cap, live_bid: book.bid, live_ask: book.ask, prior_leg: priorFill.leg_identity, post_flag_floor: after } };
  const fill = laterMakerFill(rows, leg.action_timestamp_epoch, leg.placement?.action_receipt, cap);
  return { ...leg, acted: true, credited: Boolean(fill), entry_cents: fill ? cap : null, honest_fill_class: fill ? "PROVEN_MAKER_BY_RESIDENCY_STRICTLY_LATER_QUALIFYING_ASK" : "UNPROVEN", terminal_reason: fill ? "PAIR_CAP_REORDERED_BY_ISOLATED_REPAIR_FILLED" : "PAIR_CAP_REORDERED_BY_ISOLATED_REPAIR_UNFILLED", placement: { ...leg.placement, price_cents: cap }, fill: fill ? { price_cents: cap, quantity: QUANTITY, evidence_ts: fill.ts, evidence_receipt: fill.receipt } : null, isolated_repair_v27_induced_cap: { cap_cents: cap, prior_leg: priorFill.leg_identity, post_flag_floor: after } };
}

function proposalsFor(variant, events, traceRows, sources, loadTicks) {
  const byLeg = new Map(events.flatMap((e) => Object.values(e.legs).map((l) => [l.leg_identity, l]))); const traceByLeg = new Map(traceRows.map((x) => [x.leg_identity, x])); const proposals = new Map(), receipts = [];
  if (variant === "FIX1_ANCHOR_RESIDUAL") {
    for (const t of traceRows.filter((x) => x.first_flag?.layer === "ANCHOR" && x.first_flag.predicate === "FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW")) { const rows = loadTicks(t.ticker), row = findAnchorRearm(rows, { afterTs: t.first_flag.timestamp.epoch, afterReceipt: t.first_flag.values_compared?.decision_receipt?.receipt }); const r = { leg_identity: t.leg_identity, binding_predicate: t.first_flag.predicate, refusal_is_state_not_terminal: true, rearm: row ? { receipt: row.receipt, timestamp_epoch: row.ts, bid: row.bid, ask: row.ask, spread: row.spread, dwell: row.ask_dwell_seconds, size: row.top_ask_size } : null, post_flag_floor: row ? postFlagFloor(rows, row.ts) : null, outcome: row ? "REARMED_ON_FRESH_QUALIFIED_LIVE_BOOK" : "NO_LATER_FRESH_QUALIFIED_READ" }; receipts.push(r); if (row) proposals.set(t.leg_identity, { row, reason: "ANCHOR_REARMED_ON_ANY_FRESH_QUALIFIED_LIVE_BOOK_READ", receipt: r }); }
  } else if (variant === "FIX2_CAP_REARM") {
    for (const t of traceRows.filter((x) => x.first_flag?.layer === "PLACEMENT_CAP")) { const leg = byLeg.get(t.leg_identity), cap = leg.pair_cap_v23?.pair_cap_cents ?? t.first_flag.values_compared?.pair_cap_cents; if (!Number.isInteger(cap)) continue; const rows = loadTicks(t.ticker), row = findCapRearm(rows, { afterTs: t.first_flag.timestamp.epoch, capCents: cap }); const r = { leg_identity: t.leg_identity, cap_cents: cap, abstention_is_state_not_terminal: true, rearm: row ? { receipt: row.receipt, timestamp_epoch: row.ts, bid: row.bid, ask: row.ask, spread: row.spread, dwell: row.ask_dwell_seconds, size: row.top_ask_size } : null, post_flag_floor: row ? postFlagFloor(rows, row.ts) : null, outcome: row ? "CAP_REARMED_ON_QUALIFYING_ASK_AT_OR_BELOW_CAP" : "NO_QUALIFYING_RETURN_TO_CAP" }; receipts.push(r); if (row) proposals.set(t.leg_identity, { row, reason: "PAIR_CAP_REARMED_ON_LATER_SPREAD_AND_DWELL_LAWFUL_ASK", receipt: r }); }
  } else if (variant === "FIX3_VERDICT_FALSIFIABILITY") {
    for (const leg of byLeg.values()) { const snap = leg.lag_diagnostic_v10?.first_actionable_unanimous_lower; const verdict = unfalsifiableLowerReceipt(snap); if (!verdict.touched) continue; const rows = loadTicks(leg.ticker), row = verdict.placeable ? rows.find((x) => x.receipt === snap.receipt) : null; if (verdict.placeable) ensure(row, `missing verdict receipt ${snap.receipt}`); const r = { leg_identity: leg.leg_identity, source_receipt: snap.receipt, source_timestamp_epoch: snap.timestamp_epoch, source_csv_row: snap.receipt?.includes("ARNROM-ARN.csv.gz#row-35593") ? "NAMED_ARN_EXEMPLAR" : null, verdict, post_flag_floor: postFlagFloor(rows, snap.timestamp_epoch), fitted_shapes: snap.shape_verdicts.map((x) => ({ shape_id: x.shape_id, verdict: x.verdict, counts: x.fitted_descent_distribution?.counts })) }; receipts.push(r); if (verdict.placeable) proposals.set(leg.leg_identity, { row, reason: verdict.reason, receipt: r }); }
  } else if (variant === "FIX4_ADMISSION_REASK") {
    for (const t of traceRows.filter((x) => x.first_flag?.layer === "ADMISSION")) { const source = sources.get(t.ticker), lawfulWindow = Number.isFinite(source?.left) && Number.isFinite(source?.right) && source.left < source.right, rows = lawfulWindow ? loadTicks(t.ticker) : [], row = lawfulWindow ? findAdmissionReask(rows, { leftTs: source.left, rightTs: source.right }) : null; const r = { leg_identity: t.leg_identity, initial_flag_timestamp_epoch: t.first_flag.timestamp.epoch, guarded_window_status: lawfulWindow ? "POSITIVE" : "NON_POSITIVE_OR_UNAVAILABLE", formed_book: row ? { receipt: row.receipt, timestamp_epoch: row.ts, bid: row.bid, ask: row.ask, spread: row.spread } : null, post_flag_floor: row ? postFlagFloor(rows, row.ts) : null, both_clocks_lawful: Boolean(row), outcome: row ? "ADMISSION_REASK_PASSED_ON_LATER_FORMED_BOOK" : lawfulWindow ? "NO_LATER_FORMED_BOOK_INSIDE_GUARDED_WINDOW" : "ADMISSION_WINDOW_NOT_LAWFUL_FOR_REASK" }; receipts.push(r); }
  }
  return { proposals, receipts, traceByLeg };
}

function applyVariant(variant, baselineEvents, traceRows, sources, loadTicks) {
  const events = clone(baselineEvents), { proposals, receipts } = proposalsFor(variant, events, traceRows, sources, loadTicks), outcomes = new Map();
  if (variant === "FIX4_ADMISSION_REASK") for (const r of receipts) if (r.formed_book) outcomes.set(r.leg_identity, { status: "ADMISSION_REASKED", receipt: r });
  for (const event of events) {
    const legs = Object.values(event.legs); const actionItems = [];
    for (const leg of legs) { if (leg.acted && Number.isFinite(leg.action_timestamp_epoch)) actionItems.push({ type: "BASE", ts: leg.action_timestamp_epoch, leg }); const proposal = proposals.get(leg.leg_identity); if (proposal && (!leg.acted || proposal.row.ts < leg.action_timestamp_epoch)) actionItems.push({ type: "REPAIR", ts: proposal.row.ts, leg, proposal }); }
    actionItems.sort((a, b) => a.ts - b.ts || (a.type === "REPAIR" ? -1 : 1) || a.leg.leg_identity.localeCompare(b.leg.leg_identity));
    let priorFill = null; const processed = new Set();
    for (const item of actionItems) {
      if (processed.has(item.leg.leg_identity)) continue;
      let next = item.leg;
      if (item.type === "REPAIR") next = setLegFromAction(next, item.proposal, priorFill, loadTicks);
      else if (priorFill) next = replayExistingSecondUnderNewFirst(next, priorFill, loadTicks);
      event.legs[next.leg_id] = next; item.leg = next; processed.add(next.leg_identity);
      if (next.credited) priorFill = next;
      if (item.type === "REPAIR") outcomes.set(next.leg_identity, { status: next.credited ? "CREDITED" : next.acted ? "ACTED_UNCREDITED" : "CAP_ABSTAIN", receipt: next.isolated_repair_v27, action_timestamp_epoch: next.action_timestamp_epoch });
    }
    for (const leg of Object.values(event.legs)) if (leg.isolated_repair_v27_induced_cap) outcomes.set(leg.leg_identity, { status: leg.credited ? "INDUCED_CAP_CREDITED" : leg.acted ? "INDUCED_CAP_UNCREDITED" : "CAP_ABSTAIN", receipt: leg.isolated_repair_v27_induced_cap, action_timestamp_epoch: leg.action_timestamp_epoch });
    const xs = Object.values(event.legs), completed = xs.every((l) => l.credited), sum = completed ? xs.reduce((s, l) => s + l.entry_cents, 0) : null, closes = completed && xs.every((l) => Number.isInteger(l.audited_close_cents));
    Object.assign(event, { completed_pair: completed, combined_entry_cents: sum, pair_under_par: completed && sum < 100, both_legs_strictly_below_audited_close: closes && xs.every((l) => l.entry_cents < l.audited_close_cents), joint_objective_pass_audited_close: closes && sum < 100 && xs.every((l) => l.entry_cents < l.audited_close_cents), execution_floor_pair_pass: completed && sum < 100 && xs.every((l) => Number.isInteger(l.qualifying_ask_floor_cents) && l.entry_cents <= l.qualifying_ask_floor_cents) });
  }
  if (variant === "FIX3_VERDICT_FALSIFIABILITY") for (const r of receipts.filter((x) => x.verdict.touched && !x.verdict.placeable)) outcomes.set(r.leg_identity, { status: "VERDICT_SETTLED_PAIR_UNRESOLVED", receipt: r });
  return { events, receipts, outcomes };
}

function firstFlagFor(base, leg, event, outcome, eventChanged) {
  const completed = event.completed_pair, sum = event.combined_entry_cents;
  if (!outcome && !eventChanged) return base.first_flag ? { layer: base.first_flag.layer, predicate: base.first_flag.predicate, preserve: base.first_flag } : null;
  if (outcome?.status === "ADMISSION_REASKED") return { layer: "SIBLING_PAIR", predicate: "ADMISSION_REASK_PASSED_BUT_DOWNSTREAM_PAIR_PATH_UNRESOLVED", values_compared: outcome.receipt, ts: outcome.receipt.formed_book.timestamp_epoch };
  if (outcome?.status === "VERDICT_SETTLED_PAIR_UNRESOLVED") return { layer: "SIBLING_PAIR", predicate: "UNFALSIFIABLE_LOWER_SETTLED_BUT_INVERSE_SIBLING_UNRESOLVED", values_compared: outcome.receipt, ts: outcome.receipt.source_timestamp_epoch };
  if (outcome?.status === "CAP_ABSTAIN") return { layer: "PLACEMENT_CAP", predicate: "PAIR_CAP_BELOW_CURRENT_LIVE_BID_UNREACHABLE_WITHOUT_CHASING", values_compared: outcome.receipt, ts: base.first_flag?.timestamp?.epoch };
  if (outcome && leg.acted && !leg.credited) return { layer: "FILL", predicate: "RESTING_EXPOSURE_NOT_CREDITED_BY_GUARDED_WINDOW_END", values_compared: outcome.receipt, ts: leg.action_timestamp_epoch };
  if (leg.credited) {
    if (!completed && outcome) return { layer: "COMPLETION", predicate: "SIBLING_NOT_COMPLETED_BY_GUARDED_WINDOW_END", values_compared: outcome.receipt, ts: leg.action_timestamp_epoch };
    if (!completed && base.first_flag?.layer === "COMPLETION") return { layer: base.first_flag.layer, predicate: base.first_flag.predicate, preserve: base.first_flag };
    if (completed && sum >= 100) return { layer: "COMPLETION", predicate: "COMPLETED_PAIR_NOT_STRICTLY_UNDER_PAR", values_compared: { combined_entry_cents: sum }, ts: leg.action_timestamp_epoch };
    if (completed && sum < 100) return null;
  }
  return base.first_flag ? { layer: base.first_flag.layer, predicate: base.first_flag.predicate, values_compared: base.first_flag.values_compared, ts: base.first_flag.timestamp.epoch, preserve: base.first_flag } : null;
}
function tapeAfterFlag(leg, ts, outcome, sources, bells, loadTicks) {
  const saved = outcome?.receipt?.post_flag_floor || outcome?.receipt?.receipt?.post_flag_floor;
  const first = saved || postFlagFloor(loadTicks(leg.ticker), ts);
  if (!first) return { evaluated_ticker: leg.ticker, best_qualifying_ask_floor_cents_after_flag: null, own_audited_close_cents: leg.audited_close_cents, negative_delta_available_past_flag: "NO", floor_status: "UNAVAILABLE_AFTER_FLAG" };
  const floor = first.price_cents, source = sources.get(leg.ticker);
  return { evaluated_ticker: leg.ticker, best_qualifying_ask_floor_cents_after_flag: floor, own_audited_close_cents: leg.audited_close_cents, floor_minus_close_cents: Number.isInteger(leg.audited_close_cents) ? floor - leg.audited_close_cents : null, negative_delta_available_past_flag: Number.isInteger(leg.audited_close_cents) && floor < leg.audited_close_cents ? "YES" : "NO", floor_status: "AVAILABLE", first_qualification_timestamp: clock(first.timestamp_epoch, source, bells.get(leg.event_id)), source_receipt: first.receipt, book_at_first_qualification: { bid: first.bid, ask: first.ask, spread: first.spread, ask_dwell_seconds: first.ask_dwell_seconds, top_ask_size: first.top_ask_size } };
}
function traceVariant(variant, events, baseTrace, outcomes, sources, bells, loadTicks) {
  const byLeg = new Map(events.flatMap((e) => Object.values(e.legs).map((l) => [l.leg_identity, { leg: l, event: e }]))); const rows = [];
  const changedEvents = new Set([...outcomes.keys()].map((identity) => identity.split("|")[0]));
  for (const base of baseTrace.rows) { const { leg, event } = byLeg.get(base.leg_identity), outcome = outcomes.get(base.leg_identity), f = firstFlagFor(base, leg, event, outcome, changedEvents.has(base.event_id)), first = f?.preserve ? clone(f.preserve) : f ? { layer: f.layer, source_layer: `V27_${variant}`, predicate: f.predicate, values_compared: f.values_compared, timestamp: clock(f.ts, sources.get(base.ticker), bells.get(base.event_id)), evaluated_ticker: base.ticker, repair_variant: variant } : null; const layerRows = LAYERS.map((layer, i) => { if (!first) return { order: i + 1, layer, result: "PASS" }; const j = LAYERS.indexOf(first.layer); return i < j ? { order: i + 1, layer, result: "PASS" } : i === j ? { order: i + 1, layer, result: "FLAG", predicate: first.predicate } : { order: i + 1, layer, result: "FLAG", predicate: "NOT_REACHED_AFTER_UPSTREAM_FLAG", upstream_layer: first.layer }; }); const xs = Object.values(event.legs), final = !event.completed_pair ? (leg.credited ? "naked" : xs.some((x) => x.credited) ? "naked" : leg.acted ? "never-placed" : "never-placed") : event.joint_objective_pass_audited_close ? "JOINT-CAPTURED" : "carried"; rows.push({ ...base, variant, layer_results_in_execution_order: layerRows, first_flag: first, tape_offered_afterward: first && !f?.preserve ? tapeAfterFlag(leg, f.ts, outcome, sources, bells, loadTicks) : base.tape_offered_afterward, final_state: final, leg_action_state: { acted: leg.acted, credited: leg.credited, entry_cents: leg.entry_cents, honest_fill_class: leg.honest_fill_class, terminal_reason: leg.terminal_reason }, event_result: { completed_pair: event.completed_pair, combined_entry_cents: event.combined_entry_cents, pair_under_par: event.pair_under_par, both_legs_strictly_below_audited_close: event.both_legs_strictly_below_audited_close, joint_objective_pass: event.joint_objective_pass_audited_close }, repair_effect: outcome || null }); }
  const roll = [...group(rows.filter((x) => x.first_flag), (x) => `${x.first_flag.layer}|${x.category}`)].sort(([a], [b]) => a.localeCompare(b)).map(([key, xs]) => ({ layer: key.split("|")[0], category: key.split("|")[1], stopped_legs: xs.length, false_negative_neg_delta_available_past_flag: xs.filter((x) => x.tape_offered_afterward?.negative_delta_available_past_flag === "YES").length, predicates: countBy(xs, (x) => x.first_flag.predicate) }));
  return { schema: "WINDOW1_DECISION_TRACE_1608_V27", generated_utc: "2026-08-04T00:00:00Z", variant, scope: { events: 804, legs: rows.length }, source_binding: { V23_trace_sha256: fileHash(baselineTracePath), V23_commit: "6b9c0ff25d74332b5ae6616a58adac641636462e" }, conservation: { rows: rows.length, one_row_per_leg: new Set(rows.map((x) => x.leg_identity)).size === 1608 }, rollup: { layer_x_category: roll, layer_totals: [...group(rows.filter((x) => x.first_flag), (x) => x.first_flag.layer)].sort(([a], [b]) => a.localeCompare(b)).map(([layer, xs]) => ({ layer, stopped_legs: xs.length, false_negative_neg_delta_available_past_flag: xs.filter((x) => x.tape_offered_afterward?.negative_delta_available_past_flag === "YES").length, predicates: countBy(xs, (x) => x.first_flag.predicate) })) }, rows };
}

function build() {
  for (const p of [baselineEventPath, baselineLegPath, baselineTracePath, quotePath, bellPath]) ensure(fs.existsSync(p), `missing ${p}`);
  const baselineEvents = readRows(baselineEventPath), baselineLegs = readRows(baselineLegPath), baseTrace = JSON.parse(fs.readFileSync(baselineTracePath)); ensure(baselineEvents.length === 804 && baselineLegs.length === 1608 && baseTrace.rows.length === 1608, "baseline conservation failed");
  const sources = loadSources(), bells = loadBells(), sourceHashes = {}, loadTicks = tickLoader(sources, sourceHashes), baseScore = score(baselineEvents); ensure(baseScore.aggregate.joint_objective_pairs === 45, `V23 floor mismatch ${baseScore.aggregate.joint_objective_pairs}`);
  const summary = { schema_version: "WINDOW1_V23_ISOLATED_REARMS_V27", baseline: { commit: "6b9c0ff25d74332b5ae6616a58adac641636462e", score: baseScore.aggregate }, stacking: false, variants: {} };
  for (const [variant, slug] of VARIANTS) {
    const { events, receipts, outcomes } = applyVariant(variant, baselineEvents, baseTrace.rows, sources, loadTicks), sc = score(events), rg = regret(events), tr = traceVariant(variant, events, baseTrace, outcomes, sources, bells, loadTicks), legs = events.flatMap((e) => Object.values(e.legs)).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)); ensure(tr.rows.length === 1608, `${variant} trace count`);
    const delta = Object.fromEntries(Object.keys(baseScore.aggregate).filter((k) => Number.isInteger(baseScore.aggregate[k])).map((k) => [k, sc.aggregate[k] - baseScore.aggregate[k]])); const survives = sc.aggregate.joint_objective_pairs >= baseScore.aggregate.joint_objective_pairs; const fullFloor = ["completed_pairs", "pairs_under_par", "both_legs_strictly_below_audited_close", "joint_objective_pairs", "execution_floor_pair_passes"].every((key) => sc.aggregate[key] >= baseScore.aggregate[key]);
    const dir = path.join(output, slug); write(path.join(dir, "EVENT_LEDGER.jsonl.gz"), gzipRows(events)); write(path.join(dir, "LEG_LEDGER.jsonl.gz"), gzipRows(legs)); write(path.join(dir, "DECISION_TRACE_1608.json"), canonical(tr)); write(path.join(dir, "SCORECARD.json"), canonical({ variant, V23_floor: baseScore.aggregate, variant_score: sc.aggregate, delta, V23_joint_non_regression: survives, V23_multimetric_floor_nonregression: fullFloor, stacking_eligible: false, stacking_requires_separate_operator_ratification: true, category_x_starting_price_region: sc.category_x_starting_price_region })); write(path.join(dir, "FRONTIER.json"), canonical({ fixed_denominator: 804, JOINT_law: "BOTH_LEGS_CREDITED_AND_SUM_LT_100_AND_EACH_ENTRY_STRICTLY_BELOW_OWN_AUDITED_CLOSE", tiers: sc.frontier, category_x_starting_price_region: sc.category_x_starting_price_region.map((x) => ({ category: x.category, starting_price_region: x.starting_price_region, frontier: x.frontier })) })); write(path.join(dir, "REGRET_GAUGE.json"), canonical({ law: "CREDITED_FILL_MINUS_OBJECTIVE_PRINT_BACKED_FLOOR; NEVER_PLACED_REMAINS_CATEGORICAL_FULL_REGRET", denominator_legs: rg.denominator_legs, numeric_regret: rg.numeric_regret, never_placed_full_regret_n: rg.never_placed_full_regret_n, category_x_price_region: rg.category_x_price_region })); write(path.join(dir, "REGRET_LEG_LEDGER.jsonl.gz"), gzipRows(rg.rows)); write(path.join(dir, "REPAIR_RECEIPT.json"), canonical({ variant, stacking: false, stacking_requires_separate_operator_ratification: true, constants: { dwell_seconds: DWELL_SECONDS, displayed_quantity: QUANTITY, provenance: "INHERITED_V23_MICRO_MICRO_LAW; NO_NEW_NUMERIC_CONSTANT" }, touched_legs: receipts.length, changed_leg_streams: outcomes.size, receipts, V23_joint_non_regression: survives, V23_multimetric_floor_nonregression: fullFloor }));
    summary.variants[variant] = { directory: slug, touched_legs: receipts.length, changed_leg_streams: outcomes.size, score: sc.aggregate, delta, V23_joint_non_regression: survives, V23_multimetric_floor_nonregression: fullFloor, stacking_eligible: false, stacking_requires_separate_operator_ratification: true, first_flag_totals: tr.rollup.layer_totals };
    loadTicks.clear();
  }
  const anchor = baseTrace.rows.filter((x) => x.first_flag?.layer === "ANCHOR"); summary.fix1_binding_predicate_distribution = countBy(anchor, (x) => x.first_flag.predicate); summary.fix1_anchor_stopped_legs = anchor.length; summary.fix1_anchor_false_negative_legs = anchor.filter((x) => x.tape_offered_afterward?.negative_delta_available_past_flag === "YES").length;
  write(path.join(output, "CONTROL_SUMMARY.json"), canonical(summary)); write(path.join(output, "FORBIDDEN_ACCESS_RECEIPT.json"), canonical({ holdout: false, live: false, network_runtime: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false, variants_stacked: false, scope: "FROZEN_804_DEVELOPMENT_REPLAY_ONLY" }));
  write(path.join(output, "SOURCE_HASH_MANIFEST.json"), canonical({ committed: Object.fromEntries([baselineEventPath, baselineLegPath, baselineTracePath, quotePath, bellPath, policyPath, __filename].map((p) => [rel(p), { sha256: fileHash(p), bytes: fs.statSync(p).size }])), private_fit_tick_hashes: Object.fromEntries(Object.entries(sourceHashes).sort(([a], [b]) => a.localeCompare(b))) }));
  write(path.join(output, "REPORT.md"), `# V23 isolated re-arm variants V27\n\nFour independent variants were replayed and scored separately. No variant is stacked. CONTROL_SUMMARY.json is the comparison authority. Each variant directory contains its own 1,608-leg trace, JOINT/FRONTIER score, REGRET gauge, exact ledgers, and causal repair receipt. V23 joint=45 is the non-regression floor.\n`);
  process.stdout.write(canonical({ status: "BUILT", output, summary: summary.variants }));
}

function manifestTree(root) { const out = {}; const walk = (p) => { for (const e of fs.readdirSync(p, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) { const f = path.join(p, e.name); if (e.isDirectory()) walk(f); else if (!new Set(["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"]).has(e.name)) out[path.relative(root, f).replaceAll("\\", "/")] = { sha256: fileHash(f), bytes: fs.statSync(f).size }; } }; walk(root); return out; }
function finalize() { const r1 = path.resolve(finalizeRun1), r2 = path.resolve(finalizeRun2); ensure(fs.existsSync(r1) && fs.existsSync(r2), "missing deterministic runs"); const a = manifestTree(r1), b = manifestTree(r2); ensure(JSON.stringify(a) === JSON.stringify(b), "clean builds differ"); fs.cpSync(r1, output, { recursive: true }); write(path.join(output, "DETERMINISM_RECEIPT.json"), canonical({ clean_builds: 2, byte_identical_payloads: true, payload_file_count: Object.keys(a).length, payload_manifest_sha256: sha256(canonical(a)), run_paths_not_authoritative: true })); const files = manifestTree(output); files["DETERMINISM_RECEIPT.json"] = { sha256: fileHash(path.join(output, "DETERMINISM_RECEIPT.json")), bytes: fs.statSync(path.join(output, "DETERMINISM_RECEIPT.json")).size }; write(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(Object.entries(files).sort(([x], [y]) => x.localeCompare(y))) })); process.stdout.write(canonical({ status: "FINALIZED", output, payload_file_count: Object.keys(a).length, payload_manifest_sha256: sha256(canonical(a)) })); }

if (finalizeRun1 || finalizeRun2) finalize(); else build();
