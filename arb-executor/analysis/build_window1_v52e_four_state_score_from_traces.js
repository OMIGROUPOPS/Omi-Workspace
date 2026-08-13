#!/usr/bin/env node
"use strict";

// Score-only adapter for the already-emitted V52e dev-804 decision diaries.
// It never imports or invokes a policy module.  The frozen receipt stream is
// merged with the same hash-bound true-print input used by d9f83b30.  This is
// deliberately narrower than a replay: decisions are immutable inputs.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");
const child = require("child_process");

const BLOCKED_COMMIT = "d9f83b30c44c3910f40d84b4b4f32daccabf3604";
const V52E_COMMIT = "b09aa22b301205d5d44d683497cf3edc5b177cf8";
const SPAN_COMMIT = "11f0fe0e04c315b555a0f02e4c8d44388328039e";
const OFFER_COMMIT = "22441e058f9efa7ea8c3065334a238ec8786416f";
const V52_COMMIT = "e20fbe6ce8bfe2619b6718e7554087fd9b900f0f";
const V52B_COMMIT = "98d07986fd916c1d75beb45095c75752bbc65102";
const V52C_COMMIT = "08ce27c0a297ed707cfd89aa29e60be223c9df7f";
const V52D_COMMIT = "893ee4c6860179a82c4b42439cf4a94cb2bcc97f";
const BLOCKED_REL = ".claude/window1_live_v4_replay/v52e_disposition_804_blocked_20260813";
const OUT_REL = ".claude/window1_live_v4_replay/v52e_disposition_804_four_state_20260813";
const SPAN_REL = ".claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806/WINDOW1_SPAN_804.json";
const OFFER_REL = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/POST_ONSET_OFFER_CENSUS.json";

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const repo = path.resolve(arg("--repo", "."));
const input = path.resolve(repo, arg("--input", BLOCKED_REL));
const output = path.resolve(repo, arg("--output", OUT_REL));
const compare = arg("--compare", null) ? path.resolve(repo, arg("--compare", null)) : null;
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));

function ensure(value, message) { if (!value) throw new Error(message); }
function shaBytes(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function fileHash(file) { return shaBytes(fs.readFileSync(file)); }
function gitShow(commit, relative) { return child.execFileSync("git", ["show", `${commit}:${relative}`], { cwd: repo, maxBuffer: 512 * 1024 * 1024 }); }
function canonicalValue(value) {
  if (Array.isArray(value)) return value.map(canonicalValue);
  if (value && typeof value === "object") return Object.fromEntries(Object.keys(value).sort().map((key) => [key, canonicalValue(value[key])]));
  return value;
}
function canonical(value) { return JSON.stringify(canonicalValue(value), null, 2) + "\n"; }
function write(name, value) { fs.writeFileSync(path.join(output, name), typeof value === "string" ? value : canonical(value)); }
function writeGzipRows(name, rows) {
  const body = rows.map((row) => JSON.stringify(canonicalValue(row))).join("\n") + (rows.length ? "\n" : "");
  fs.writeFileSync(path.join(output, name), zlib.gzipSync(Buffer.from(body), { level: 9, mtime: 0 }));
}
function quantile(sorted, p) { if (!sorted.length) return null; const i = (sorted.length - 1) * p, lo = Math.floor(i), hi = Math.ceil(i); return lo === hi ? sorted[lo] : sorted[lo] + (sorted[hi] - sorted[lo]) * (i - lo); }
function distribution(values) {
  const x = values.filter(Number.isFinite).sort((a, b) => a - b);
  return { n: x.length, min: x.length ? x[0] : null, p25: quantile(x, .25), median: quantile(x, .5), p75: quantile(x, .75), p90: quantile(x, .9), max: x.length ? x[x.length - 1] : null, sum: x.reduce((a, b) => a + b, 0) };
}
function countBy(rows, keyFn) { const out = {}; for (const row of rows) { const key = keyFn(row); out[key] = (out[key] || 0) + 1; } return Object.fromEntries(Object.entries(out).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function strictPrint(print) { return print.taker_side === "no" && Number.isFinite(print.size) && print.size >= 5; }
function eventCode(eventId) { const match = String(eventId).match(/-(26JUL[^-]+)$/); ensure(match, `cannot parse event code ${eventId}`); return match[1]; }
function legToken(legIdentity) { return String(legIdentity).split("|").pop(); }

function safeOutput(dir) {
  ensure(path.basename(dir).includes("v52e_disposition_804_four_state"), `unsafe output ${dir}`);
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
}

function manifest(dir) {
  const files = fs.readdirSync(dir).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  const rows = files.map((name) => ({ path: name, sha256: fileHash(path.join(dir, name)), bytes: fs.statSync(path.join(dir, name)).size }));
  fs.writeFileSync(path.join(dir, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: rows, aggregate_sha256: shaBytes(Buffer.from(rows.map((row) => `${row.sha256}  ${row.path}\n`).join(""))) }));
}

async function loadPrints(metaByTicker) {
  const file = path.join(privateRoot, "fit-local/prints.jsonl");
  ensure(fs.existsSync(file), `missing ${file}`);
  const hash = crypto.createHash("sha256");
  const byLeg = new Map([...metaByTicker.values()].map((meta) => [meta.leg_identity, []]));
  const seen = new Map([...metaByTicker.keys()].map((ticker) => [ticker, new Set()]));
  let raw = 0, admitted = 0, duplicate = 0;
  const source = fs.createReadStream(file, { highWaterMark: 1024 * 1024 });
  source.on("data", (chunk) => hash.update(chunk));
  const rows = readline.createInterface({ input: source, crlfDelay: Infinity });
  for await (const line of rows) {
    if (!line) continue;
    raw += 1;
    const row = JSON.parse(line), meta = metaByTicker.get(row.ticker);
    if (!meta || !row.true_print) continue;
    const ts = Date.parse(row.exchange_ts) / 1000;
    if (!Number.isFinite(ts) || ts < meta.left || ts > meta.right) continue;
    if (!row.trade_id || seen.get(row.ticker).has(row.trade_id)) { duplicate += 1; continue; }
    seen.get(row.ticker).add(row.trade_id);
    const price = Number(row.price_cents), size = Number(row.size);
    if (!Number.isInteger(price) || !Number.isFinite(size) || size <= 0) continue;
    admitted += 1;
    byLeg.get(meta.leg_identity).push({ kind: "PRINT", leg_identity: meta.leg_identity, timestamp_epoch: ts, sequence: admitted, receipt: row.receipt_id, trade_id: row.trade_id, price_cents: price, size, taker_side: row.taker_side, taker_book_side: row.taker_book_side });
  }
  for (const values of byLeg.values()) values.sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || a.sequence - b.sequence || a.leg_identity.localeCompare(b.leg_identity));
  return { byLeg, receipt: { path_class: "PRIVATE_FIT_DEVELOPMENT_PRINTS_HASH_ONLY", sha256: hash.digest("hex"), bytes: fs.statSync(file).size, raw_rows: raw, admitted_unique_window_prints: admitted, duplicate_trade_id_rows_rejected: duplicate } };
}

function rowObject(array, fields) { return Object.fromEntries(fields.map((field, index) => [field, array[index]])); }
function licenseEnvelope(row) {
  return {
    onset: { passed: row.onset_passed, selected_candidate: row.onset_candidate, timestamp_epoch: row.onset_timestamp_epoch },
    read: { passed: row.read_passed, state: row.read_state, quote_path_state: row.quote_path_state, pressure_state: row.pressure_state, evidence_class: row.read_evidence_class, span_seconds: row.read_span_seconds, evidence_receipts: row.read_evidence_receipts, book_receipts: row.read_book_receipts, print_receipts: row.read_print_receipts, comparable_book_transitions: row.read_comparable_book_transitions, comparable_print_transitions: row.read_comparable_print_transitions, rising_score: row.read_rising_score, falling_score: row.read_falling_score, last_directional_evidence_kind: row.last_directional_evidence_kind, last_directional_evidence_receipt: row.last_directional_evidence_receipt, last_directional_evidence_magnitude_cents: row.last_directional_evidence_magnitude_cents },
    diary: { own_post_onset_low_cents: row.own_post_onset_low_cents, own_low_receipt: row.own_low_receipt, sibling_post_onset_low_cents: row.sibling_post_onset_low_cents, sibling_low_receipt: row.sibling_low_receipt, lows_sum_cents: row.lows_sum_cents },
    coherence: { lows_under_par: row.lows_under_par, disagreement_firing: row.disagreement_firing, disagreement_clear: row.disagreement_clear, adjudication_status: row.adjudication_status, adjudication_winner: row.adjudication_winner, adjudication_loser: row.adjudication_loser },
    level: { passed: row.level_passed, target_cents: row.level_target_cents, authority: row.level_authority, machine_read_target_cents: row.machine_read_target_cents, machine_read_authority: row.machine_read_authority, palantir_rescue: row.palantir_rescue },
    palantir: { manifest_sha256: row.palantir_manifest_sha256, N2_cell_n: row.N2_cell_n, N2_cell_share: row.N2_cell_share, N4_grid_covered: row.N4_grid_covered, N4_grid_discount_cents: row.N4_grid_discount_cents, N4_zone_category_share: row.N4_zone_category_share, N5_mirror_rate: row.N5_mirror_rate, N5_vindication_rate: row.N5_vindication_rate, continuous: row.palantir_continuous, priors_gate: row.priors_gate },
    verdict: { gate_verdict: row.gate_verdict, blocked_clause: row.blocked_clause, incumbent_action: row.incumbent_action, incumbent_reason: row.incumbent_reason, order_before_cents: row.order_before_cents, final_action: row.final_action, final_target_cents: row.final_target_cents, reason: row.reason },
    observation: { timestamp_epoch: row.timestamp_epoch, t_minus_scheduled_seconds: row.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: row.t_minus_actual_bell_seconds, t_minus_pre_match_boundary_seconds: row.t_minus_pre_match_boundary_seconds, receipt: row.receipt, bid: row.bid, ask: row.ask, last_traded: row.last_traded, spread: row.spread, ask_dwell_seconds: row.ask_dwell_seconds, top_ask_size: row.top_ask_size, bid_depth_5: row.bid_depth_5, ask_depth_5: row.ask_depth_5 },
  };
}

function dominantBlock(leg) { return Object.entries(leg.block_counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))[0]?.[0] ?? "NO_GATE_BLOCK_RECORDED"; }

function processEvent(eventId, traceRows, base, printsByLeg, reconstruction) {
  const ids = base.per_leg.map((row) => row.leg_identity).sort();
  const legs = Object.fromEntries(ids.map((id) => [id, {
    leg_identity: id, ticker: base.per_leg.find((row) => row.leg_identity === id).ticker,
    credited: false, entry_cents: null, fill_timestamp_epoch: null, fill_receipt: null, fill_print: null, fill_class: null, strict_credit: false,
    active: null, first_action_timestamp_epoch: null, terminal_reason: null, final_state: null, last_trace: null, action_transitions: [], block_counts: {}, decision_rows: 0,
  }]));
  const timeline = [];
  for (const row of traceRows) timeline.push({ kind: "BOOK_DECISION", ...row });
  for (const id of ids) for (const print of printsByLeg.get(id) || []) timeline.push(print);
  timeline.sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || (a.kind === "PRINT" ? 0 : 1) - (b.kind === "PRINT" ? 0 : 1) || a.sequence - b.sequence || a.leg_identity.localeCompare(b.leg_identity));

  const fill = (leg, print, active, source) => {
    leg.credited = true; leg.entry_cents = active.target_cents; leg.fill_timestamp_epoch = print.timestamp_epoch; leg.fill_receipt = print.receipt; leg.fill_print = print; leg.fill_class = "MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST"; leg.strict_credit = strictPrint(print); leg.terminal_reason = leg.fill_class;
    leg.fill_license = active.license; leg.fill_action = { timestamp_epoch: active.action_ts, receipt: active.action_receipt, source, target_cents: active.target_cents };
    const sibling = legs[ids.find((id) => id !== leg.leg_identity)];
    sibling.pair_cap_cents = 99 - leg.entry_cents;
    sibling.last_sibling_fill = { timestamp_epoch: print.timestamp_epoch, receipt: print.receipt, entry_cents: leg.entry_cents, pair_cap_cents: sibling.pair_cap_cents };
    if (sibling.active && sibling.active.target_cents > sibling.pair_cap_cents) {
      sibling.action_transitions.push({ action: "PAIR_CAP_REPRICE", timestamp_epoch: print.timestamp_epoch, receipt: print.receipt, before_cents: sibling.active.target_cents, after_cents: sibling.pair_cap_cents, triggering_fill_leg: leg.leg_identity, triggering_fill_cents: leg.entry_cents });
      sibling.active = { ...sibling.active, target_cents: sibling.pair_cap_cents, action_ts: print.timestamp_epoch, action_receipt: print.receipt, source: "PAIR_CAP_REPRICE", cap_origin: sibling.last_sibling_fill };
    }
  };

  for (const item of timeline) {
    const leg = legs[item.leg_identity];
    if (leg.credited) continue;
    if (item.kind === "PRINT") {
      if (leg.active && item.timestamp_epoch > leg.active.action_ts && item.price_cents <= leg.active.target_cents) fill(leg, item, leg.active, leg.active.source);
      continue;
    }
    leg.decision_rows += 1; leg.last_trace = item;
    if (item.blocked_clause) leg.block_counts[item.blocked_clause] = (leg.block_counts[item.blocked_clause] || 0) + 1;
    const before = Number.isInteger(item.order_before_cents) ? item.order_before_cents : null;
    const current = leg.active?.target_cents ?? null;
    if (before !== current) {
      reconstruction.order_before_resynchronizations += 1;
      reconstruction.resynchronization_classes[`${current === null ? "NULL" : "REST"}_TO_${before === null ? "NULL" : "REST"}`] = (reconstruction.resynchronization_classes[`${current === null ? "NULL" : "REST"}_TO_${before === null ? "NULL" : "REST"}`] || 0) + 1;
      if (before === null) leg.active = null;
      else {
        const sideEffect = leg.last_sibling_fill;
        ensure(sideEffect && sideEffect.timestamp_epoch <= item.timestamp_epoch, `unbound implicit rest ${eventId} ${leg.leg_identity} ${item.receipt}`);
        leg.active = { target_cents: before, action_ts: sideEffect.timestamp_epoch, action_receipt: sideEffect.receipt, source: "FILL_TIME_SIDE_EFFECT_RECONCILED_BY_NEXT_ORDER_BEFORE", license: leg.active?.license ?? licenseEnvelope(item), cap_origin: sideEffect };
        leg.first_action_timestamp_epoch ??= sideEffect.timestamp_epoch;
      }
    }
    const action = item.final_action;
    if (action === "PLACE_REST" || action === "REPRICE_REST") {
      ensure(Number.isInteger(item.final_target_cents), `missing target ${eventId} ${item.receipt}`);
      const transition = { action, timestamp_epoch: item.timestamp_epoch, receipt: item.receipt, before_cents: before, after_cents: item.final_target_cents, license: licenseEnvelope(item) };
      leg.action_transitions.push(transition);
      leg.active = { target_cents: item.final_target_cents, action_ts: item.timestamp_epoch, action_receipt: item.receipt, source: action, license: transition.license };
      leg.first_action_timestamp_epoch ??= item.timestamp_epoch;
    } else if (action === "CANCEL_REST") {
      leg.action_transitions.push({ action, timestamp_epoch: item.timestamp_epoch, receipt: item.receipt, before_cents: before, after_cents: null, license: licenseEnvelope(item) });
      leg.active = null;
    } else ensure(action === "HOLD_REST", `unknown frozen action ${action}`);
  }

  for (const leg of Object.values(legs)) {
    leg.resting_target_at_edge_cents = leg.credited ? null : leg.active?.target_cents ?? null;
    if (!leg.credited) leg.terminal_reason = leg.decision_rows === 0 ? "NO_TWO_SIDED_BOOK_DECISION_INSIDE_EDGE" : leg.active ? "REST_UNFILLED_AT_HARD_PREBELL_EDGE" : "NO_LAWFUL_REST_AT_HARD_PREBELL_EDGE";
    leg.final_state = leg.credited ? "CREDITED" : leg.active ? "RESTING_UNFILLED" : "NEVER_PLACED_OR_CANCELLED";
    delete leg.active; delete leg.last_trace; delete leg.last_sibling_fill;
  }
  const values = Object.values(legs), completed = values.every((leg) => leg.credited), combined = completed ? values.reduce((sum, leg) => sum + leg.entry_cents, 0) : null;
  return { event_id: eventId, category: base.category, starting_price_split: base.starting_price_split, bell_confidence: base.precision_class, w1_left_epoch: base.w1_left_epoch, w1_right_epoch: base.w1_right_epoch, completed_pair: completed, combined_entry_cents: combined, pair_under_par: completed && combined < 100, legs };
}

function strictProjection(events) {
  return events.map((event) => {
    const legs = Object.fromEntries(Object.entries(event.legs).map(([id, leg]) => [id, { ...leg, credited: leg.credited && leg.strict_credit }]));
    const values = Object.values(legs), completed = values.every((leg) => leg.credited), combined = completed ? values.reduce((sum, leg) => sum + leg.entry_cents, 0) : null;
    return { ...event, legs, completed_pair: completed, combined_entry_cents: combined, pair_under_par: completed && combined < 100, strict_role: "FROZEN_OUTPUT_BUILD_VERIFICATION_RECLASSIFICATION" };
  });
}
function score(events, strict = false) {
  const eligible = strict ? strictProjection(events) : events;
  const legs = eligible.flatMap((event) => Object.values(event.legs)), completed = eligible.filter((event) => event.completed_pair), under = completed.filter((event) => event.pair_under_par);
  const frontier = Object.fromEntries(Object.entries({ LE_93: (x) => x <= 93, LE_95: (x) => x <= 95, LE_97: (x) => x <= 97, LT_100: (x) => x < 100, ANY_PRICE: () => true }).map(([name, predicate]) => [name, completed.filter((event) => predicate(event.combined_entry_cents)).length]));
  return { D: eligible.length, legs: legs.length, acted_legs: legs.filter((leg) => leg.first_action_timestamp_epoch !== null).length, credited_legs: legs.filter((leg) => leg.credited).length, completed_pairs: completed.length, under_par_pairs: under.length, complete_at_loss_pairs: completed.length - under.length, locked_cents_per_contract: under.reduce((sum, event) => sum + 100 - event.combined_entry_cents, 0), locked_cents_five_lot: under.reduce((sum, event) => sum + (100 - event.combined_entry_cents) * 5, 0), maker_fill_classes: countBy(legs.filter((leg) => leg.credited), (leg) => leg.fill_class), frontier, conservation: { D: eligible.length, legs: legs.length, pass: eligible.length === 804 && legs.length === 1608 } };
}

function partitionScores(events, strict) {
  const groups = new Map();
  for (const event of events) { const key = `${event.category}|${event.starting_price_split}`; if (!groups.has(key)) groups.set(key, []); groups.get(key).push(event); }
  return [...groups].sort(([a], [b]) => a.localeCompare(b)).map(([cell, rows]) => ({ cell, denominator: rows.length, ...score(rows, strict), conservation: undefined }));
}

async function main() {
  ensure(fs.existsSync(input), `missing blocked package ${input}`);
  const sourceManifest = JSON.parse(fs.readFileSync(path.join(input, "ARTIFACT_HASH_MANIFEST.json")));
  for (const [name, row] of Object.entries(sourceManifest.files)) ensure(fs.existsSync(path.join(input, name)) && fileHash(path.join(input, name)) === row.sha256, `blocked artifact changed ${name}`);
  const schema = JSON.parse(fs.readFileSync(path.join(input, "TRACE_SCHEMA.json"))), fields = schema.fields;
  const span = JSON.parse(fs.readFileSync(path.join(repo, SPAN_REL)));
  ensure(span.rows.length === 804 && span.rows.reduce((sum, row) => sum + row.per_leg.length, 0) === 1608, "span population changed");
  const baseByEvent = new Map(span.rows.map((row) => [row.event_id, row]));
  const metaByTicker = new Map(span.rows.flatMap((event) => event.per_leg.map((leg) => [leg.ticker, { ...leg, category: event.category, left: event.w1_left_epoch, right: event.w1_right_epoch }])));
  const printLoad = await loadPrints(metaByTicker);
  const chunks = fs.readdirSync(input).filter((name) => /^V52E_FULL_DECISION_TRACE_804_CHUNK_\d+\.jsonl\.gz$/.test(name)).sort();
  ensure(chunks.length === 101, `trace chunk count changed ${chunks.length}`);
  const events = [], reconstruction = { adapter: "FROZEN_DIARY_PLUS_HASH_BOUND_PRINTS_V1", policy_modules_imported: 0, policy_invocations: 0, trace_rows: 0, trace_chunks: chunks.length, order_before_resynchronizations: 0, resynchronization_classes: {}, source_event_boundaries: 0 };
  const palSummary = { decision_rows: 0, manifest_sha256_counts: {}, N2_rows: 0, N4_rows: 0, N5_rows: 0, continuous_rows: 0, priors_gate_true_rows: 0 };
  for (const name of chunks) {
    const rows = readline.createInterface({ input: fs.createReadStream(path.join(input, name)).pipe(zlib.createGunzip()), crlfDelay: Infinity });
    let eventId = null, eventRows = [];
    const flush = () => {
      if (!eventId) return;
      const base = baseByEvent.get(eventId); ensure(base, `trace event absent from span ${eventId}`);
      events.push(processEvent(eventId, eventRows, base, printLoad.byLeg, reconstruction));
      reconstruction.source_event_boundaries += 1; eventRows = [];
    };
    for await (const line of rows) {
      if (!line) continue;
      reconstruction.trace_rows += 1;
      const row = rowObject(JSON.parse(line), fields);
      palSummary.decision_rows += 1;
      palSummary.manifest_sha256_counts[row.palantir_manifest_sha256 ?? "NULL"] = (palSummary.manifest_sha256_counts[row.palantir_manifest_sha256 ?? "NULL"] || 0) + 1;
      if (row.N2_cell_n !== undefined) palSummary.N2_rows += 1;
      if (row.N4_grid_covered !== undefined) palSummary.N4_rows += 1;
      if (row.N5_mirror_rate !== undefined) palSummary.N5_rows += 1;
      if (row.palantir_continuous === true) palSummary.continuous_rows += 1;
      if (row.priors_gate === true) palSummary.priors_gate_true_rows += 1;
      if (eventId !== null && row.event_id !== eventId) flush();
      eventId = row.event_id; eventRows.push(row);
    }
    flush();
  }
  const reconstructedIds = new Set(events.map((row) => row.event_id));
  const emptyTraceEvents = span.rows.filter((row) => !reconstructedIds.has(row.event_id));
  reconstruction.trace_empty_events = emptyTraceEvents.length;
  reconstruction.trace_empty_event_ids = emptyTraceEvents.map((row) => row.event_id).sort();
  for (const base of emptyTraceEvents) events.push(processEvent(base.event_id, [], base, printLoad.byLeg, reconstruction));
  events.sort((a, b) => a.event_id.localeCompare(b.event_id));
  ensure(events.length === 804 && new Set(events.map((row) => row.event_id)).size === 804, `event reconstruction conservation ${events.length}`);
  const strictEvents = strictProjection(events);
  const market = score(events, false), strict = score(events, true);
  ensure(market.complete_at_loss_pairs === 4, `operator fourth-state fingerprint changed: ${market.complete_at_loss_pairs}`);

  const stateRows = events.map((event) => {
    const legs = Object.values(event.legs), credited = legs.filter((leg) => leg.credited), missing = legs.filter((leg) => !leg.credited);
    const state = credited.length === 2 ? (event.pair_under_par ? "COMPLETE_AT_DELTA" : "COMPLETE_AT_LOSS") : credited.length === 1 ? "PARTIAL_FOR_REASON" : "NEITHER_FOR_REASON";
    return { event_id: event.event_id, category: event.category, price_region: event.starting_price_split, bell_confidence: event.bell_confidence, state, combined_entry_cents: event.combined_entry_cents, credited_legs: credited.map((leg) => leg.leg_identity).sort(), missing: missing.map((leg) => ({ leg_identity: leg.leg_identity, terminal_reason: leg.terminal_reason, dominant_block_reason: dominantBlock(leg), reason: `${leg.terminal_reason}|${dominantBlock(leg)}` })).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)) };
  });
  const states = countBy(stateRows, (row) => row.state);
  const stateCensus = { D: 804, states, named_reasons: countBy(stateRows.flatMap((row) => row.missing.map((leg) => `${row.state}|${leg.reason}`)), (row) => row), by_category_x_price_region: countBy(stateRows, (row) => `${row.category}|${row.price_region}|${row.state}`), conservation: { rows: stateRows.length, state_sum: Object.values(states).reduce((a, b) => a + b, 0), only_four_states: stateRows.every((row) => ["COMPLETE_AT_DELTA", "COMPLETE_AT_LOSS", "PARTIAL_FOR_REASON", "NEITHER_FOR_REASON"].includes(row.state)), pass: stateRows.length === 804 && Object.values(states).reduce((a, b) => a + b, 0) === 804 } };

  const twoRulers = { CANON_MARKET_GRADE: { ...market, role: "PRIMARY_MARKET_RULER_TRADES_AS_TRUTH", category_x_price_region: partitionScores(events, false) }, STRICT_PRINT_CROSS: { ...strict, role: "BUILD_VERIFICATION_RECLASSIFICATION_OF_FROZEN_MARKET_OUTPUT_ONLY", category_x_price_region: partitionScores(events, true), caveat: "No counterfactual policy replay; strict eligibility is applied to each frozen market fill receipt." } };

  const offerBytes = gitShow(OFFER_COMMIT, OFFER_REL), offer = JSON.parse(offerBytes);
  ensure(offer.conservation.games === 804 && offer.rows.length === 804 && offer.conservation.counts.OFFERED_POST_ONSET === 612, "offer denominator changed");
  const eventByCode = new Map(events.map((event) => [eventCode(event.event_id), event]));
  const offerRows = offer.rows.map((row) => {
    const event = eventByCode.get(row.code); ensure(event, `offer event missing ${row.code}`);
    const strictComplete = event.completed_pair && Object.values(event.legs).every((leg) => leg.strict_credit);
    return { code: row.code, event_id: event.event_id, category: row.cat, price_region: event.starting_price_split, offer_class: row.cls, offer_margin_cents: row.margin, pair_post_onset_floor_cents: row.pair_floor_sel, market_complete_at_delta: event.completed_pair && event.pair_under_par, market_complete_at_loss: event.completed_pair && !event.pair_under_par, market_combined_entry_cents: event.combined_entry_cents, strict_complete_at_delta: strictComplete && event.combined_entry_cents < 100, strict_combined_entry_cents: strictComplete ? event.combined_entry_cents : null, legs: row.legs };
  });
  const capture = (rows, field) => ({ denominator: rows.length, captured: rows.filter((row) => row[field]).length, rate: rows.length ? rows.filter((row) => row[field]).length / rows.length : null });
  const offered = offerRows.filter((row) => row.offer_class === "OFFERED_POST_ONSET");
  const ladder = [["GE_10_CENTS", (row) => row.offer_margin_cents >= 10], ["GE_5_CENTS", (row) => row.offer_margin_cents >= 5], ["GE_3_CENTS", (row) => row.offer_margin_cents >= 3], ["THIN_1_TO_2_CENTS", (row) => row.offer_margin_cents >= 1 && row.offer_margin_cents <= 2], ["ALL_OFFERED_POST_ONSET", () => true]];
  const offerCapture = { source: { commit: OFFER_COMMIT, path: OFFER_REL, sha256: shaBytes(offerBytes) }, fixed_denominator: { D: 804, OFFERED_POST_ONSET: 612, margin_ladder: { GE_10_CENTS: 90, GE_5_CENTS: 236, GE_3_CENTS: 384, THIN_1_TO_2_CENTS: 228 }, other_classes: offer.conservation.counts }, market_ladder: Object.fromEntries(ladder.map(([name, predicate]) => [name, capture(offered.filter(predicate), "market_complete_at_delta")])), strict_ladder: Object.fromEntries(ladder.map(([name, predicate]) => [name, capture(offered.filter(predicate), "strict_complete_at_delta")])), classes_market: Object.fromEntries([...new Set(offerRows.map((row) => row.offer_class))].sort().map((cls) => [cls, capture(offerRows.filter((row) => row.offer_class === cls), "market_complete_at_delta")])), by_category_x_price_region: [...new Set(offerRows.map((row) => `${row.category}|${row.price_region}`))].sort().map((cell) => { const rows = offerRows.filter((row) => `${row.category}|${row.price_region}` === cell); return { cell, denominator: rows.length, offer_classes: countBy(rows, (row) => row.offer_class), market: capture(rows, "market_complete_at_delta"), strict: capture(rows, "strict_complete_at_delta") }; }), formation_only_and_not_offered_never_folded: true };

  const offerLegByTicker = new Map(offer.rows.flatMap((row) => {
    if (row.legs) return Object.values(row.legs).map((leg) => [leg.ticker, { code: row.code, category: row.cat, offer_class: row.cls, pair_margin_cents: row.margin, floor_cents: leg.floor_sel, onset_timestamp_epoch: leg.onset_sel }]);
    ensure(row.cls === "NO_TAPE", `offer row lacks legs outside NO_TAPE ${row.code}`);
    const event = eventByCode.get(row.code); ensure(event, `NO_TAPE event missing ${row.code}`);
    return Object.values(event.legs).map((leg) => [leg.ticker, { code: row.code, category: row.cat, offer_class: row.cls, pair_margin_cents: null, floor_cents: null, onset_timestamp_epoch: null }]);
  }));
  ensure(offerLegByTicker.size === 1608, "offer leg conservation changed");
  const regretRows = events.flatMap((event) => Object.values(event.legs).map((leg) => { const source = offerLegByTicker.get(leg.ticker); ensure(source, `missing floor ${leg.ticker}`); return { event_id: event.event_id, leg_identity: leg.leg_identity, ticker: leg.ticker, category: event.category, price_region: event.starting_price_split, offer_class: source.offer_class, post_onset_floor_cents: source.floor_cents, onset_timestamp_epoch: source.onset_timestamp_epoch, credited: leg.credited, entry_cents: leg.entry_cents, regret_cents: leg.credited && Number.isInteger(source.floor_cents) ? leg.entry_cents - source.floor_cents : null, uncredited_opportunity: !leg.credited && Number.isInteger(source.floor_cents), terminal_reason: leg.terminal_reason, dominant_block_reason: dominantBlock(leg) }; }));
  const regretSummary = (rows) => { const credited = rows.filter((row) => Number.isInteger(row.regret_cents)); return { legs: rows.length, floor_available: rows.filter((row) => Number.isInteger(row.post_onset_floor_cents)).length, credited_with_floor: credited.length, uncredited_with_floor: rows.filter((row) => row.uncredited_opportunity).length, regret_cents: distribution(credited.map((row) => row.regret_cents)), no_fabricated_incomplete_penalty: true }; };
  const regretGauge = { ruler: "ENTRY_MINUS_OFFER_CENSUS_PER_LEG_POST_ONSET_FLOOR", aggregate: regretSummary(regretRows), by_category_x_price_region: [...new Set(regretRows.map((row) => `${row.category}|${row.price_region}`))].sort().map((cell) => ({ cell, ...regretSummary(regretRows.filter((row) => `${row.category}|${row.price_region}` === cell)) })), by_offer_class: Object.fromEntries([...new Set(regretRows.map((row) => row.offer_class))].sort().map((cls) => [cls, regretSummary(regretRows.filter((row) => row.offer_class === cls))])) };

  const firstPosts = events.flatMap((event) => Object.values(event.legs).flatMap((leg) => leg.action_transitions.filter((row) => ["PLACE_REST", "FILL_TIME_SIDE_EFFECT_RECONCILED_BY_NEXT_ORDER_BEFORE"].includes(row.action)).slice(0, 1).map((row) => ({ event_id: event.event_id, category: event.category, leg_identity: leg.leg_identity, ...row }))));
  const restMutations = events.flatMap((event) => Object.values(event.legs).flatMap((leg) => leg.action_transitions.filter((row) => ["PLACE_REST", "REPRICE_REST", "PAIR_CAP_REPRICE"].includes(row.action)).map((row) => ({ event_id: event.event_id, category: event.category, leg_identity: leg.leg_identity, ...row }))));
  const reflex = restMutations.filter((row) => row.license && !row.license.read.passed);
  ensure(reflex.length === 0, `REFLEX_POST=${reflex.length}`);
  const posting = { first_placements: firstPosts.length, rest_mutations: restMutations.length, REFLEX_POST: reflex.length, first_post_seconds_after_window_open: distribution(firstPosts.map((row) => row.timestamp_epoch - baseByEvent.get(row.event_id).w1_left_epoch)), first_post_t_minus_scheduled_seconds: distribution(firstPosts.map((row) => row.license?.observation?.t_minus_scheduled_seconds).filter(Number.isFinite)), first_post_t_minus_actual_bell_seconds: distribution(firstPosts.map((row) => row.license?.observation?.t_minus_actual_bell_seconds).filter(Number.isFinite)), read_at_first_post: countBy(firstPosts, (row) => `${row.license?.read?.state ?? "READ_ABSENT"}|${row.license?.read?.evidence_class ?? "NO_EVIDENCE_CLASS"}`), onset_candidate_at_first_post: countBy(firstPosts, (row) => row.license?.onset?.selected_candidate ?? "NO_ONSET") };

  const palRows = reconstruction.trace_rows;
  palSummary.clean_store_assertion = JSON.parse(gitShow(V52E_COMMIT, ".claude/window1_live_v4_replay/v52e_palantir_wiring_20260812/CLEAN_STORE_BOOT_ASSERTION.json"));
  palSummary.all_decision_rows_consumed_N2_N4_N5 = [palSummary.N2_rows, palSummary.N4_rows, palSummary.N5_rows, palSummary.continuous_rows].every((value) => value === palRows);
  palSummary.priors_never_gate = palSummary.priors_gate_true_rows === 0;
  ensure(palSummary.clean_store_assertion.passed && palSummary.all_decision_rows_consumed_N2_N4_N5 && palSummary.priors_never_gate, "Palantir scale binding failed");

  const namedChecks = { role: "CURRENT_BINDINGS_REPORTED_NOT_TUNED", rows: Object.fromEntries(["ARSMAR", "SANDAN", "PUTJEA", "POLKUH", "MERDRO"].map((label) => { const event = events.find((row) => row.event_id.includes(label)); ensure(event, `missing named ${label}`); return [label, { event_id: event.event_id, completed: event.completed_pair, combined_entry_cents: event.combined_entry_cents, under_par: event.pair_under_par, legs: Object.fromEntries(Object.entries(event.legs).map(([id, leg]) => [id, { credited: leg.credited, entry_cents: leg.entry_cents, final_state: leg.final_state, terminal_reason: leg.terminal_reason, gate_blocks: leg.block_counts }])) }]; })) };

  const priorObservationPath = ".claude/window1_live_v4_replay/v52e_palantir_wiring_20260812/V52E_FLOW_OUTCOMES_OBSERVATION_ONLY.json";
  const priorObservationBytes = gitShow(V52E_COMMIT, priorObservationPath), priorObservations = JSON.parse(priorObservationBytes), parityDiffs = [];
  const eventsById = new Map(events.map((event) => [event.event_id, event]));
  for (const prior of priorObservations) {
    const event = eventsById.get(prior.event_id); ensure(event, `parity event missing ${prior.event_id}`);
    for (const priorLeg of prior.legs) {
      const leg = event.legs[priorLeg.leg_identity], expectedCredited = priorLeg.final_state === "CREDITED";
      const fillDelta = Number.isFinite(leg?.fill_timestamp_epoch) && Number.isFinite(priorLeg.fill_timestamp_epoch) ? Math.abs(leg.fill_timestamp_epoch - priorLeg.fill_timestamp_epoch) : leg?.fill_timestamp_epoch === priorLeg.fill_timestamp_epoch ? 0 : null;
      if (!leg || leg.credited !== expectedCredited || leg.entry_cents !== priorLeg.entry_cents_observation || fillDelta !== 0) parityDiffs.push({ event_id: prior.event_id, leg_identity: priorLeg.leg_identity, frozen: { credited: expectedCredited, entry_cents: priorLeg.entry_cents_observation, fill_timestamp_epoch: priorLeg.fill_timestamp_epoch }, reconstructed: leg ? { credited: leg.credited, entry_cents: leg.entry_cents, fill_timestamp_epoch: leg.fill_timestamp_epoch } : null });
    }
  }
  const traceParity = { source: { commit: V52E_COMMIT, path: priorObservationPath, sha256: shaBytes(priorObservationBytes) }, events: priorObservations.length, legs: priorObservations.length * 2, differences: parityDiffs, byte_value_parity: parityDiffs.length === 0, role: "INDEPENDENT_EVENT_LEVEL_FILL_PARITY_FOR_FROZEN_30_GAME_V52E_OBSERVATION" };
  ensure(traceParity.byte_value_parity, `trace reconstruction parity failed ${parityDiffs.length}`);

  const lineageArtifact = (commit, relative) => JSON.parse(gitShow(commit, relative));
  const v52Score = lineageArtifact(V52_COMMIT, ".claude/window1_live_v4_replay/v52_judgment_gate_20260812/MARKET_GRADE_SCORECARD.json");
  ensure(v52Score.score.completed_pairs === 176, "honest V52 lineage changed");
  const lineage = { warning: "V52_IS_FULL_804; V52B_TO_V52E_PRIOR_ROWS_ARE_DISTINCT_30_GAME_OBSERVATION_COHORTS_NOT_A_SCORE_SERIES", rows: [
    { version: "V52", commit: V52_COMMIT, scope: "DEV_804_DISPOSITION", completed_pairs: v52Score.score.completed_pairs },
    { version: "V52B", commit: V52B_COMMIT, scope: "PINS_PLUS_FRESH25_OBSERVATION", completed_pairs: lineageArtifact(V52B_COMMIT, ".claude/window1_live_v4_replay/v52b_read_level_authority_20260812/OUTCOME_OBSERVATIONS_30.json").candidate.completed_pairs },
    { version: "V52C", commit: V52C_COMMIT, scope: "PINS_PLUS_FRESH25_OBSERVATION", completed_pairs: lineageArtifact(V52C_COMMIT, ".claude/window1_live_v4_replay/v52c_full_post_onset_read_20260812/OUTCOME_OBSERVATIONS_30.json").candidate.completed_pairs },
    { version: "V52D", commit: V52D_COMMIT, scope: "PINS_PLUS_FRESH25_OBSERVATION", completed_pairs: lineageArtifact(V52D_COMMIT, ".claude/window1_live_v4_replay/v52d_disagreement_referee_20260812/OUTCOME_OBSERVATIONS_30.json").candidate.completed_pairs },
    { version: "V52E", commit: V52E_COMMIT, scope: "PINS_PLUS_FRESH25_OBSERVATION", completed_pairs: lineageArtifact(V52E_COMMIT, ".claude/window1_live_v4_replay/v52e_palantir_wiring_20260812/OUTCOME_OBSERVATIONS_30.json").candidate.completed_pairs },
    { version: "V52E", commit: BLOCKED_COMMIT, scope: "DEV_804_FOUR_STATE_EXAM", completed_pairs: market.completed_pairs, complete_at_delta: market.under_par_pairs, complete_at_loss: market.complete_at_loss_pairs },
  ] };

  const lossEvents = events.filter((event) => event.completed_pair && !event.pair_under_par);
  ensure(lossEvents.length === 4, "loss autopsy population changed");
  const autopsy = [];
  for (const event of lossEvents) {
    const fillOrder = Object.values(event.legs).sort((a, b) => a.fill_timestamp_epoch - b.fill_timestamp_epoch || a.fill_receipt.localeCompare(b.fill_receipt));
    const first = fillOrder[0], second = fillOrder[1];
    const breachRows = second.action_transitions.filter((row) => row.timestamp_epoch >= first.fill_timestamp_epoch && Number.isInteger(row.after_cents) && row.after_cents + first.entry_cents >= 100);
    const licensing = breachRows[0] ?? second.action_transitions.filter((row) => Number.isInteger(row.after_cents) && row.after_cents === second.entry_cents).slice(-1)[0];
    ensure(licensing, `missing loss licensing row ${event.event_id}`);
    for (const [ordinal, leg] of fillOrder.entries()) autopsy.push({ row_type: "LEG_LICENSE_AND_FILL", event_id: event.event_id, category: event.category, price_region: event.starting_price_split, combined_entry_cents: event.combined_entry_cents, fill_sequence: ordinal + 1, leg_identity: leg.leg_identity, entry_cents: leg.entry_cents, post: leg.fill_action, full_retained_license_fields: leg.fill_license, fill: { timestamp_epoch: leg.fill_timestamp_epoch, receipt: leg.fill_receipt, print: leg.fill_print, strict_build_verification_credit: leg.strict_credit } });
    autopsy.push({ row_type: "SECOND_SIDE_BREACH_EVALUATION", event_id: event.event_id, category: event.category, price_region: event.starting_price_split, combined_entry_cents: event.combined_entry_cents, first_entry: { leg_identity: first.leg_identity, entry_cents: first.entry_cents, fill_timestamp_epoch: first.fill_timestamp_epoch, fill_receipt: first.fill_receipt }, second_entry: { leg_identity: second.leg_identity, entry_cents: second.entry_cents, fill_timestamp_epoch: second.fill_timestamp_epoch, fill_receipt: second.fill_receipt }, licensing_evaluation: licensing, arithmetic: { standing_first_entry_cents: first.entry_cents, licensed_second_level_cents: licensing.after_cents, sum_cents: first.entry_cents + licensing.after_cents, pair_cap_required_cents: 99 - first.entry_cents, breach_cents: licensing.after_cents - (99 - first.entry_cents) }, missing_check_precise: "V52E_MACHINE_READ_LICENSE_TARGET_MUST_BE_BOUNDED_BY_ACTIVE_PAIR_CAP: target_cents <= 99 - credited_sibling_entry_cents", repair_status: "FUTURE_ITERATION_NOT_APPLIED" });
  }

  const sumBlocks = (eventRows) => {
    const out = {};
    for (const event of eventRows) for (const leg of Object.values(event.legs)) for (const [reason, n] of Object.entries(leg.block_counts)) out[reason] = (out[reason] || 0) + n;
    return Object.fromEntries(Object.entries(out).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
  };
  const blockRollup = { decision_receipts: { aggregate: sumBlocks(events), by_category: Object.fromEntries([...new Set(events.map((event) => event.category))].sort().map((category) => [category, sumBlocks(events.filter((event) => event.category === category))])) }, terminal_missing_legs: countBy(stateRows.flatMap((row) => row.missing), (row) => row.reason) };

  const policyReceipt = JSON.parse(fs.readFileSync(path.join(input, "POLICY_BYTE_IDENTITY.json")));
  ensure(policyReceipt.all_byte_identical, "blocked policy identity changed");
  safeOutput(output);
  writeGzipRows("MARKET_EVENT_LEDGER_804.jsonl.gz", events);
  writeGzipRows("STRICT_EVENT_LEDGER_804.jsonl.gz", strictEvents);
  writeGzipRows("FOUR_STATE_EVENT_LEDGER_804.jsonl.gz", stateRows);
  writeGzipRows("POST_ONSET_OFFER_CAPTURE_LEDGER_804.jsonl.gz", offerRows);
  writeGzipRows("REGRET_LEDGER_1608.jsonl.gz", regretRows);
  writeGzipRows("FIRST_POST_LEDGER.jsonl.gz", firstPosts);
  writeGzipRows("COMPLETE_AT_LOSS_LICENSE_AUTOPSY.jsonl.gz", autopsy);
  write("TWO_RULER_SCORECARD.json", twoRulers);
  write("FOUR_STATE_CENSUS.json", stateCensus);
  write("FRONTIER.json", { market: market.frontier, strict: strict.frontier, denominator: 804, per_category_x_price_region: { market: twoRulers.CANON_MARKET_GRADE.category_x_price_region, strict: twoRulers.STRICT_PRINT_CROSS.category_x_price_region } });
  write("REGRET_GAUGE.json", regretGauge);
  write("OFFER_DENOMINATOR_CAPTURE.json", offerCapture);
  write("POSTING_TIME_AND_READ_AT_POST.json", posting);
  write("REFLEX_POST_ATTESTATION.json", { REFLEX_POST: posting.REFLEX_POST, pass: posting.REFLEX_POST === 0, scope: "ALL_FROZEN_REST_MUTATIONS_RECONSTRUCTED_FROM_D9_DIARIES" });
  write("PALANTIR_CONSUMPTION_SCALE_RECEIPT.json", palSummary);
  write("NAMED_CHECKS.json", namedChecks);
  write("LINEAGE_RECEIPT.json", lineage);
  write("PER_BLOCK_REASON_ROLLUP.json", blockRollup);
  write("COMPLETE_AT_LOSS_AUTOPSY_SUMMARY.json", { events: lossEvents.length, event_ids: lossEvents.map((row) => row.event_id), rows: autopsy.length, missing_check_precise: "V52E_MACHINE_READ_LICENSE_TARGET_MUST_BE_BOUNDED_BY_ACTIVE_PAIR_CAP", repair_applied: false });
  write("TRACE_SCORE_ADAPTER_RECEIPT.json", { ...reconstruction, input_commit: BLOCKED_COMMIT, input_path: BLOCKED_REL, input_manifest_sha256: fileHash(path.join(input, "ARTIFACT_HASH_MANIFEST.json")), print_source: printLoad.receipt, reconstructed_events: events.length, reconstructed_loss_events: lossEvents.length, fourth_state_operator_ruling_consumed: true, policy_replay: false, policy_invocations: 0, behavior_edits: false, pass: events.length === 804 && lossEvents.length === 4 && reconstruction.policy_invocations === 0 });
  write("TRACE_RECONSTRUCTION_PARITY_30.json", traceParity);
  write("POLICY_BYTE_IDENTITY.json", policyReceipt);
  write("CONTROL_BINDING.json", { variant: "V52E_DISPOSITION_804_FOUR_STATE_SCORE_FROM_D9_TRACES", frozen_policy_commit: V52E_COMMIT, already_run_trace_commit: BLOCKED_COMMIT, trace_parent: SPAN_COMMIT, scope: "DEV_804_ONLY", policy_edits: false, policy_replay: false, score_only_adapter: true, sealed_access: false, deployment: false, live: false });
  write("SOURCE_HASH_MANIFEST.json", { sources: { blocked_trace_manifest: { commit: BLOCKED_COMMIT, path: `${BLOCKED_REL}/ARTIFACT_HASH_MANIFEST.json`, sha256: fileHash(path.join(input, "ARTIFACT_HASH_MANIFEST.json")) }, trace_chunks: chunks.map((name) => ({ path: `${BLOCKED_REL}/${name}`, sha256: fileHash(path.join(input, name)), bytes: fs.statSync(path.join(input, name)).size })), trace_schema: { path: `${BLOCKED_REL}/TRACE_SCHEMA.json`, sha256: fileHash(path.join(input, "TRACE_SCHEMA.json")) }, prints: printLoad.receipt, stability_spans: { path: SPAN_REL, sha256: fileHash(path.join(repo, SPAN_REL)) }, offer_denominator: offerCapture.source, policy_files: policyReceipt.files } });
  write("FORBIDDEN_ACCESS_RECEIPT.json", { sealed: false, holdout: false, deployment: false, live: false, network: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, policy_edits: false, policy_replay: false });
  const report = `# V52e full-804 disposition exam — four-state score\n\nThe operator-ratified fourth state closes the d9f83b30 pre-score specification block without another policy replay. The score-only adapter consumes the already-run 101 decision-diary shards and their hash-bound true prints; policy invocations: 0.\n\n- Four states: ${JSON.stringify(states)}; conservation ${Object.values(states).reduce((a, b) => a + b, 0)}/804.\n- CANON market ruler: completed ${market.completed_pairs}; at delta ${market.under_par_pairs}; at loss ${market.complete_at_loss_pairs}; frontier <=93/<=95/<=97/<100/any ${market.frontier.LE_93}/${market.frontier.LE_95}/${market.frontier.LE_97}/${market.frontier.LT_100}/${market.frontier.ANY_PRICE}.\n- Strict build-verification reclassification: completed ${strict.completed_pairs}; at delta ${strict.under_par_pairs}; at loss ${strict.complete_at_loss_pairs}; frontier ${strict.frontier.LE_93}/${strict.frontier.LE_95}/${strict.frontier.LE_97}/${strict.frontier.LT_100}/${strict.frontier.ANY_PRICE}.\n- Offered-post-onset capture: ${offerCapture.market_ladder.ALL_OFFERED_POST_ONSET.captured}/612; >=10c ${offerCapture.market_ladder.GE_10_CENTS.captured}/90; >=5c ${offerCapture.market_ladder.GE_5_CENTS.captured}/236; >=3c ${offerCapture.market_ladder.GE_3_CENTS.captured}/384; thin 1–2c ${offerCapture.market_ladder.THIN_1_TO_2_CENTS.captured}/228. Formation-only and not-offered remain separate.\n- REFLEX_POST ${posting.REFLEX_POST}. Palantir continuous consumption ${palSummary.continuous_rows}/${palSummary.decision_rows}; priors gated ${palSummary.priors_gate_true_rows}.\n- COMPLETE_AT_LOSS autopsy: ${lossEvents.map((event) => `${eventCode(event.event_id)}=${event.combined_entry_cents}`).join(", ")}. Each row freezes the retained full license envelope at post/fill and the breaching second-side evaluation. The missing check is pair-cap bounding inside V52e machine-read level licensing. No repair is included.\n- Lineage starts at honest V52 176 completed pairs; prior b/c/d/e rows are explicitly separate 30-game observation cohorts.\n- No sealed, holdout, deployment, live, network, order, position, exit, settlement, or DCA access.\n`;
  write("REPORT.md", report);

  const names = fs.readdirSync(output).sort();
  let determinism;
  if (compare) {
    const mismatches = names.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name)));
    const extra = fs.readdirSync(compare).filter((name) => ![...names, "DETERMINISM_RECEIPT.json", "ARTIFACT_HASH_MANIFEST.json"].includes(name));
    ensure(!mismatches.length && !extra.length, `score build mismatch ${[...mismatches, ...extra].join(",")}`);
    determinism = { clean_score_builds: 2, compared_files: names.length, byte_identical: true, mismatches: [], policy_replays: 0 };
  } else determinism = { clean_score_builds: 1, byte_identical: null, role: "FIRST_SCORE_BUILD", policy_replays: 0 };
  write("DETERMINISM_RECEIPT.json", determinism);
  manifest(output);
  if (compare) { fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism)); manifest(compare); ensure(fileHash(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(output, "ARTIFACT_HASH_MANIFEST.json")), "final manifests differ"); }
  process.stdout.write(canonical({ output, states, market, strict, offer_capture: offerCapture.market_ladder, REFLEX_POST: posting.REFLEX_POST, loss_events: lossEvents.map((row) => ({ event_id: row.event_id, combined_entry_cents: row.combined_entry_cents })), determinism }));
}

main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
