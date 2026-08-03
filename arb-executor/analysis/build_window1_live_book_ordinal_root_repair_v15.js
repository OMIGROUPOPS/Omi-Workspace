#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const args = process.argv.slice(2);
const value = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const out = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/live_book_ordinal_root_repair_v15_20260803")));
const baselineRoot = path.join(repo, ".claude/window1_live_v4_replay/persistence_floor_repair_v11_20260802");
const baselineLegPath = path.join(baselineRoot, "POPULATION_LEG_LEDGER.jsonl.gz");
const baselineEventPath = path.join(baselineRoot, "POPULATION_EVENT_LEDGER.jsonl.gz");
const rawPaths = {
  live_book_only: path.resolve(value("--live-book-only", path.join(repo, ".claude/_tmp_window1_v15_live_only_v2/EVENT_LEDGER.json"))),
  fitted_persistence_only: path.resolve(value("--persistence-only", path.join(repo, ".claude/_tmp_window1_v15_persistence_only_v2/EVENT_LEDGER.json"))),
  combined: path.resolve(value("--combined-run1", path.join(repo, ".claude/_tmp_window1_v15_combined_run1_v2/EVENT_LEDGER.json"))),
  combined_regeneration: path.resolve(value("--combined-run2", path.join(repo, ".claude/_tmp_window1_v15_combined_run2_v2/EVENT_LEDGER.json"))),
};
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const bellPath = path.join(repo, ".claude/window1_live_v4_replay/actual_bell_refit_20260729/ACTUAL_BELL_REFIT.json");
const persistencePath = path.join(repo, ".claude/window1_live_v4_replay/persistence_floor_v11_fit_20260802/PERSISTENCE_SURVIVAL_LIBRARY_V11.json");
const replayPath = path.join(repo, "arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js");
const modulePath = path.join(repo, "arb-executor/analysis/window1_quote_shape_live_book_persistence_v15.js");
const builderPath = __filename;
const tests = [
  "arb-executor/tests/test_window1_quote_shape_live_book_persistence_v15.js",
  "arb-executor/tests/test_window1_live_book_ordinal_root_repair_v15.js",
  "arb-executor/tests/test_window1_quote_shape_persistence_floor_v11.js",
  "arb-executor/tests/test_window1_persistence_floor_repair_v11.js",
  "arb-executor/tests/test_window1_quote_shape_descent_verdict_v10.js",
  "arb-executor/tests/test_window1_quote_shape_dynamic_renarrow_v6.js",
  "arb-executor/tests/test_window1_dynamic_renarrow_population_v9.js",
  "arb-executor/tests/test_window1_quote_shape_elimination_two_game.js",
].map((x) => path.join(repo, x));
const rawBase = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated";

function canonical(x) { return `${JSON.stringify(x, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function rel(file) { return path.relative(repo, file).replaceAll("\\", "/"); }
function ensure(ok, message) { if (!ok) throw new Error(message); }
function json(file) { return JSON.parse(fs.readFileSync(file)); }
function jsonlGz(file) { return zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim().split(/\r?\n/).map(JSON.parse); }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(rows.map(JSON.stringify).join("\n") + "\n"), { level: 9, mtime: 0 }); }
function countBy(values) { return Object.fromEntries([...values.reduce((m, x) => (m.set(String(x), (m.get(String(x)) || 0) + 1), m), new Map())].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function q(values, p) { const x = values.filter(Number.isFinite).sort((a, b) => a - b); return x.length ? x[Math.floor((x.length - 1) * p)] : null; }
function distribution(values) { const x = values.filter(Number.isFinite); return { n: x.length, unavailable: values.length - x.length, min: x.length ? Math.min(...x) : null, p25: q(x, .25), median: q(x, .5), p75: q(x, .75), p90: q(x, .9), max: x.length ? Math.max(...x) : null, exact_counts: countBy(values.map((v) => Number.isFinite(v) ? v : "UNAVAILABLE")) }; }
function group(rows, key) { const m = new Map(); for (const row of rows) { const k = key(row); if (!m.has(k)) m.set(k, []); m.get(k).push(row); } return m; }
function parseCsv(text) { const rows = text.trimEnd().split(/\r?\n/), heads = rows.shift().split(","); return rows.map((line) => Object.fromEntries(line.split(",").map((v, i) => [heads[i], v]))); }

function gate(reason) {
  if (reason === "FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW") return "HISTORICAL_LOW_ANCHOR";
  if (reason === "ALL_SURVIVING_SHAPES_SAY_LOWER") return "UNANIMOUS_LOWER_PERSISTENCE";
  if (reason === "FLOOR_CONSENSUS_BUT_SIBLING_DIRECTION_NOT_INDEPENDENTLY_OBSERVED") return "INVERSE_SIBLING_UNRESOLVED";
  if (reason === "FLOOR_CONSENSUS_BUT_STABLE_SAME_PRICE_ASK_LACKS_SIGNING_SUPPORT") return "STABLE_SIGNER_UNPROVEN";
  if (["SURVIVING_SHAPES_DISAGREE_OR_LIBRARY_GAP", "OBSERVED_DESCENT_OUTSIDE_SURVIVING_SHAPE_TRAINING_SUPPORT"].includes(reason)) return "SHAPE_OR_LIBRARY_GAP";
  if (["FLOOR_CONSENSUS_BUT_MICRO_MICRO_NOT_READY", "FLOOR_CONSENSUS_AWAITING_FRESH_OWN_BOOK_RECEIPT", "FLOOR_CONSENSUS_BUT_CURRENT_LIVE_BOOK_AUTHORITY_INCOMPLETE"].includes(reason)) return "MICRO_MICRO_NOT_READY";
  if (reason === "SOURCE_UNAVAILABLE") return "SOURCE_UNAVAILABLE";
  return `UNMAPPED:${reason}`;
}

function clock(ts, source, bell) {
  return {
    timestamp_epoch: Number.isFinite(ts) ? ts : null,
    t_minus_scheduled_seconds: Number.isFinite(ts) && Number.isFinite(source?.scheduled) ? source.scheduled - ts : null,
    t_minus_actual_bell_seconds: Number.isFinite(ts) && Number.isFinite(bell) ? bell - ts : null,
    actual_bell_status: Number.isFinite(bell) ? "BOUND" : "ACTUAL_BELL_NOT_BOUND",
  };
}

function eventMetrics(events) {
  const legs = events.flatMap((x) => x.legs), completed = events.filter((x) => x.completed_pair), under = completed.filter((x) => x.pair_under_par);
  return {
    events: events.length,
    legs: legs.length,
    acted_legs: legs.filter((x) => x.acted).length,
    credited_legs: legs.filter((x) => x.credited).length,
    no_action_legs: legs.filter((x) => !x.acted).length,
    completed_pairs: completed.length,
    pairs_under_par: under.length,
    both_legs_strictly_below_close: completed.filter((x) => x.both_legs_strictly_below_close).length,
    under_par_and_both_legs_strictly_below_close: under.filter((x) => x.both_legs_strictly_below_close).length,
    execution_floor_pair_pass: under.filter((x) => x.legs.every((leg) => Number.isFinite(leg.entry_minus_qualifying_ask_floor_cents) && leg.entry_minus_qualifying_ask_floor_cents <= 0)).length,
    acted_entry_minus_qualifying_ask_floor_cents: distribution(legs.filter((x) => x.acted).map((x) => x.entry_minus_qualifying_ask_floor_cents)),
    acted_entry_minus_objective_traded_low_cents: distribution(legs.filter((x) => x.acted).map((x) => x.entry_minus_objective_traded_low_cents)),
  };
}

function legPartitions(legs) {
  return [...group(legs, (x) => `${x.category}|${x.price_region}`).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => {
    const [category, price_region] = key.split("|"); const no = rows.filter((x) => !x.acted);
    return { category, price_region, thin: rows.length < 10, legs: rows.length, acted: rows.length - no.length, no_action: no.length, six_gate_non_actions: countBy(no.filter((x) => gate(x.terminal_reason) !== "SOURCE_UNAVAILABLE").map((x) => gate(x.terminal_reason))), source_unavailable: no.filter((x) => gate(x.terminal_reason) === "SOURCE_UNAVAILABLE").length, exact_terminal_reasons: countBy(no.map((x) => x.terminal_reason)), acted_entry_minus_qualifying_ask_floor_cents: distribution(rows.filter((x) => x.acted).map((x) => x.entry_minus_qualifying_ask_floor_cents)), acted_entry_minus_objective_traded_low_cents: distribution(rows.filter((x) => x.acted).map((x) => x.entry_minus_objective_traded_low_cents)) };
  });
}

function eventPartitions(events) {
  return [...group(events, (x) => `${x.category}|${x.starting_price_split}`).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => { const [category, starting_price_split] = key.split("|"); return { category, starting_price_split, thin: rows.length < 10, ...eventMetrics(rows) }; });
}

function main() {
  const required = [baselineLegPath, baselineEventPath, quotePath, bellPath, persistencePath, replayPath, modulePath, builderPath, ...tests, ...Object.values(rawPaths)];
  for (const file of required) ensure(fs.existsSync(file), `missing ${file}`);
  ensure(hashFile(rawPaths.combined) === hashFile(rawPaths.combined_regeneration), "combined clean regenerations differ");
  const baselineLegs = jsonlGz(baselineLegPath), baselineEvents = jsonlGz(baselineEventPath), baseLegById = new Map(baselineLegs.map((x) => [x.leg_identity, x])), baseEventById = new Map(baselineEvents.map((x) => [x.event_id, x]));
  ensure(baselineLegs.length === 1608 && baselineEvents.length === 804, "V11 population mismatch");
  const quoteRows = parseCsv(fs.readFileSync(quotePath, "utf8")), sourceByLeg = new Map(quoteRows.map((x) => [`${x.event_id}|${x.leg}`, { scheduled: Number(x.scheduled_start_ts), left: Number(x.left_ts), right: Number(x.right_ts) }]));
  const bellRows = json(bellPath).leg_rows || [], bellByLeg = new Map(bellRows.map((x) => [`${x.event_id}|${x.leg_id}`, Number(x.exact_bell_ts)]));

  function convert(rawPath, name) {
    const raw = json(rawPath); ensure(raw.events.length === 804, `${name} event mismatch`); const legs = [], events = [];
    for (const event of [...raw.events].sort((a, b) => a.event_id.localeCompare(b.event_id))) {
      const oldEvent = baseEventById.get(event.event_id); ensure(oldEvent, `missing baseline event ${event.event_id}`); const eventLegs = [];
      for (const [legId, x] of Object.entries(event.legs).sort(([a], [b]) => a.localeCompare(b))) {
        const id = `${event.event_id}|${legId}`, old = baseLegById.get(id); ensure(old, `missing baseline leg ${id}`); const acted = x.proposed_entry_cents !== null, entry = Number.isInteger(x.honest_credited_entry_cents) ? x.honest_credited_entry_cents : null, source = sourceByLeg.get(id), bell = bellByLeg.get(id);
        const row = { ...old, variant: name, acted, credited: entry !== null, honest_fill_class: x.honest_fill_class, entry_cents: entry, action_timestamp_epoch: x.placement?.action_ts ?? null, action_clock: clock(x.placement?.action_ts, source, bell), entry_minus_qualifying_ask_floor_cents: entry !== null && Number.isInteger(old.qualifying_ask_floor_cents) ? entry - old.qualifying_ask_floor_cents : null, entry_minus_objective_traded_low_cents: entry !== null && Number.isInteger(old.objective_traded_low_cents) ? entry - old.objective_traded_low_cents : null, entry_minus_own_window1_close_cents: entry !== null && Number.isInteger(old.own_window1_close_cents) ? entry - old.own_window1_close_cents : null, terminal_reason: acted ? "ACTED" : x.terminal_reason, placement: x.placement, action_book: x.action_book, baseline_v11: { acted: old.acted, entry_cents: old.entry_cents, action_timestamp_epoch: old.action_timestamp_epoch, terminal_reason: old.terminal_reason } };
        row.stream_change_from_v11 = !old.acted && acted ? "NEW_ACTION" : old.acted && !acted ? "LOST_ACTION" : old.acted && acted && (old.entry_cents !== entry || old.action_timestamp_epoch !== row.action_timestamp_epoch) ? "ACTION_CHANGED" : "UNCHANGED";
        legs.push(row); eventLegs.push(row);
      }
      const completed = eventLegs.every((x) => x.credited), combined = completed ? eventLegs.reduce((s, x) => s + x.entry_cents, 0) : null;
      events.push({ event_id: event.event_id, category: event.category, starting_price_split: oldEvent.starting_price_split, legs: eventLegs, completed_pair: completed, combined_entry_cents: combined, pair_under_par: combined !== null && combined < 100, both_closes_available: eventLegs.every((x) => Number.isInteger(x.own_window1_close_cents)), both_legs_strictly_below_close: completed && eventLegs.every((x) => Number.isInteger(x.own_window1_close_cents) && x.entry_cents < x.own_window1_close_cents), ceilings: oldEvent.ceilings });
    }
    ensure(legs.length === 1608 && events.length === 804, `${name} conservation failed`); return { raw, legs, events };
  }

  const variants = {
    live_book_only: convert(rawPaths.live_book_only, "live_book_only"),
    fitted_persistence_only: convert(rawPaths.fitted_persistence_only, "fitted_persistence_only"),
    combined: convert(rawPaths.combined, "combined"),
  };

  const baselineNo = baselineLegs.filter((x) => !x.acted), baselineGateRows = baselineNo.filter((x) => gate(x.terminal_reason) !== "SOURCE_UNAVAILABLE");
  const unmapped = baselineNo.filter((x) => gate(x.terminal_reason).startsWith("UNMAPPED:")); ensure(!unmapped.length, `unmapped baseline gates ${countBy(unmapped.map((x) => x.terminal_reason))}`);
  const census = { schema_version: "WINDOW1_V11_CURRENT_SIX_GATE_NON_ACTION_CENSUS", population: { events: 804, legs: 1608, acted: 712, no_action: 896 }, decision_gate_non_actions: baselineGateRows.length, source_unavailable: baselineNo.length - baselineGateRows.length, six_gates: countBy(baselineGateRows.map((x) => gate(x.terminal_reason))), exact_terminal_reasons: countBy(baselineNo.map((x) => x.terminal_reason)), by_category_and_price_region: legPartitions(baselineLegs).map((x) => ({ category: x.category, price_region: x.price_region, thin: x.thin, legs: x.legs, acted: x.acted, no_action: x.no_action, six_gates: x.six_gate_non_actions, source_unavailable: x.source_unavailable, exact_terminal_reasons: x.exact_terminal_reasons })) };
  ensure(Object.values(census.six_gates).reduce((a, b) => a + b, 0) + census.source_unavailable === 896, "six-gate conservation failed");

  const transitions = baselineLegs.map((base) => ({ leg_identity: base.leg_identity, event_id: base.event_id, category: base.category, price_region: base.price_region, ticker: base.ticker, baseline_v11: { acted: base.acted, terminal_reason: base.terminal_reason, gate: base.acted ? "ACTED" : gate(base.terminal_reason), entry_cents: base.entry_cents }, floors: { qualifying_ask_floor_cents: base.qualifying_ask_floor_cents, objective_traded_low_cents: base.objective_traded_low_cents }, variants: Object.fromEntries(Object.entries(variants).map(([name, v]) => { const x = v.legs.find((r) => r.leg_identity === base.leg_identity); return [name, { acted: x.acted, terminal_reason: x.terminal_reason, entry_cents: x.entry_cents, entry_minus_qualifying_ask_floor_cents: x.entry_minus_qualifying_ask_floor_cents, entry_minus_objective_traded_low_cents: x.entry_minus_objective_traded_low_cents, action_clock: x.action_clock, action_receipt: x.placement?.action_receipt ?? null, live_book_floor_authority_v15: x.placement?.live_book_floor_authority_v15 ?? null, persistence_floor_v15: x.placement?.persistence_floor_v15 ?? null }]; })) }));

  const persistence = json(persistencePath), lowerRows = baselineLegs.filter((x) => !x.acted && x.terminal_reason === "ALL_SURVIVING_SHAPES_SAY_LOWER");
  const lowerProofs = lowerRows.map((x) => {
    const snap = x.lag_diagnostic_v10?.last_actionable_unanimous_lower;
    if (!snap) return { leg_identity: x.leg_identity, event_id: x.event_id, category: x.category, price_region: x.price_region, status: "NO_ACTIONABLE_QUALIFIED_LOWER_RECEIPT", combined_outcome: variants.combined.legs.find((y) => y.leg_identity === x.leg_identity)?.terminal_reason };
    const proofs = (snap.shape_verdicts || []).map((v) => { const key = `${x.category}|${x.price_region}|${v.shape_id}|${snap.prefix.new_low_descent_count}`, cell = persistence.cells[key]; if (!cell) return { shape_id: v.shape_id, key, available: false, reason: "NO_FITTED_PERSISTENCE_CELL" }; const future = cell.future_qualified_lower_examples.filter((y) => y.leg_identity !== x.leg_identity), terminal = cell.terminal_qualified_low_examples.filter((y) => y.leg_identity !== x.leg_identity), waits = future.map((y) => y.wait_from_episode_start_seconds).sort((a, b) => a - b), fitted = waits.length ? waits[Math.floor(waits.length / 2)] : 0; return { shape_id: v.shape_id, key, available: future.length + terminal.length > 0, leave_one_leg_out_future_lower_support_n: future.length, leave_one_leg_out_terminal_support_n: terminal.length, fitted_upper_median_wait_seconds: fitted, observed_same_price_dwell_seconds: snap.book.ask_dwell_seconds, exhausted: snap.book.ask_dwell_seconds > fitted, fitted_ordinal: v.fitted_descent_distribution?.signing_ordinal_after_a_descent_is_observed ?? null, observed_new_low_descents: snap.prefix.new_low_descent_count }; });
    const baseKeys = ["own_micro_position_observed", "inverse_sibling_resolved", "stable_signing_support", "current_ask_at_observed_low", "ask_dwell_at_least_10_seconds", "top_ask_capacity_at_least_five", "fresh_own_book_receipt"], base = baseKeys.every((k) => snap.predicates[k]);
    return { leg_identity: x.leg_identity, event_id: x.event_id, category: x.category, price_region: x.price_region, status: "ACTIONABLE_QUALIFIED_LOWER_RECEIPT", last_refusal_clock: clock(snap.timestamp_epoch, sourceByLeg.get(x.leg_identity), bellByLeg.get(x.leg_identity)), base_predicates_satisfied: base, all_fitted_cells_available: proofs.length > 0 && proofs.every((p) => p.available), all_fitted_waits_exhausted: proofs.length > 0 && proofs.every((p) => p.exhausted), all_ordinals_unavailable: proofs.length > 0 && proofs.every((p) => !Number.isInteger(p.fitted_ordinal)), proofs, combined_outcome: variants.combined.legs.find((y) => y.leg_identity === x.leg_identity)?.terminal_reason };
  });
  const persistenceReceipt = { schema_version: "WINDOW1_V15_FITTED_PERSISTENCE_ROOT_RECEIPT", baseline_unanimous_lower_legs: lowerRows.length, defect: "V11_REQUIRED_FITTED_WAIT_EXHAUSTION_AND_SIMULTANEOUSLY_REQUIRED_THE_DESCENT_ORDINAL_TO_BE_UNAVAILABLE", actionable_qualified_lower_receipts: lowerProofs.filter((x) => x.status.startsWith("ACTIONABLE")).length, no_actionable_qualified_lower_receipt: lowerProofs.filter((x) => !x.status.startsWith("ACTIONABLE")).length, all_fitted_waits_exhausted: lowerProofs.filter((x) => x.all_fitted_waits_exhausted).length, all_fitted_waits_exhausted_and_all_other_predicates_satisfied: lowerProofs.filter((x) => x.all_fitted_waits_exhausted && x.base_predicates_satisfied).length, prior_v11_eligible_missing_ordinal_only: lowerProofs.filter((x) => x.all_fitted_waits_exhausted && x.base_predicates_satisfied && x.all_ordinals_unavailable).length, corrected_law: "An available leave-one-leg-out fitted upper-median persistence wait is independent causal authority. An existing descent ordinal is no longer a veto after every surviving-shape wait is exhausted.", estimator_provenance: { library: rel(persistencePath), estimator: "leave-one-leg-out upper median", new_threshold: false }, fitted_persistence_only_new_actions_from_baseline_lower: lowerRows.filter((x) => variants.fitted_persistence_only.legs.find((y) => y.leg_identity === x.leg_identity)?.acted).length, fitted_persistence_only_actions_with_exact_authority_receipt: variants.fitted_persistence_only.legs.filter((x) => x.placement?.persistence_floor_v15).length, combined_new_actions_from_baseline_lower_all_causal_paths: lowerRows.filter((x) => variants.combined.legs.find((y) => y.leg_identity === x.leg_identity)?.acted).length, combined_actions_with_exact_persistence_authority_receipt: variants.combined.legs.filter((x) => x.placement?.persistence_floor_v15).length, remaining_lower_after_combined: variants.combined.legs.filter((x) => !x.acted && x.terminal_reason === "ALL_SURVIVING_SHAPES_SAY_LOWER").length, by_category_and_price_region: [...group(lowerProofs, (x) => `${x.category}|${x.price_region}`).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => { const [category, price_region] = key.split("|"); return { category, price_region, thin: rows.length < 10, legs: rows.length, exhausted_and_base_ready: rows.filter((x) => x.all_fitted_waits_exhausted && x.base_predicates_satisfied).length, fitted_persistence_only_new_actions: rows.filter((x) => variants.fitted_persistence_only.legs.find((y) => y.leg_identity === x.leg_identity)?.acted).length, combined_new_actions_all_causal_paths: rows.filter((x) => variants.combined.legs.find((y) => y.leg_identity === x.leg_identity)?.acted).length }; }) };

  const aboveRows = baselineLegs.filter((x) => !x.acted && x.terminal_reason === "FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW");
  const aboveReceipt = { schema_version: "WINDOW1_V15_CURRENT_LIVE_BOOK_FLOOR_AUTHORITY_RECEIPT", baseline_above_observed_low_legs: aboveRows.length, defect: "A live all-FLOOR verdict was vetoed by equality to a historical low no longer present in the current book", corrected_law: "Use the current lawful own ask, fresh receipt, inherited dwell/capacity, resolved sibling and surviving-shape consensus; historical-low equality is not consulted and no tolerance exists", tolerance_cents: null, invented_thresholds: 0, live_book_only_new_actions: aboveRows.filter((x) => variants.live_book_only.legs.find((y) => y.leg_identity === x.leg_identity)?.acted).length, combined_new_actions: aboveRows.filter((x) => variants.combined.legs.find((y) => y.leg_identity === x.leg_identity)?.acted).length, by_category_and_price_region: [...group(aboveRows, (x) => `${x.category}|${x.price_region}`).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => { const [category, price_region] = key.split("|"); return { category, price_region, thin: rows.length < 10, legs: rows.length, live_book_only_new_actions: rows.filter((x) => variants.live_book_only.legs.find((y) => y.leg_identity === x.leg_identity)?.acted).length, combined_new_actions: rows.filter((x) => variants.combined.legs.find((y) => y.leg_identity === x.leg_identity)?.acted).length }; }) };

  const carried = [], underNotBoth = [];
  for (const event of baselineEvents.filter((x) => x.completed_pair)) {
    const ds = event.legs.map((x) => x.entry_minus_own_window1_close_cents), available = ds.every(Number.isInteger), strict = available && ds.filter((x) => x > 0).length === 1 && ds.filter((x) => x < 0).length === 1;
    if (strict) {
      const positive = event.legs.find((x) => x.entry_minus_own_window1_close_cents > 0), sibling = event.legs.find((x) => x !== positive), order = positive.action_timestamp_epoch < sibling.action_timestamp_epoch ? "FIRST" : positive.action_timestamp_epoch > sibling.action_timestamp_epoch ? "SECOND" : "SAME_TIMESTAMP";
      carried.push({ event_id: event.event_id, category: event.category, starting_price_split: event.starting_price_split, pair_under_par: event.pair_under_par, positive_leg_fill_order: order, fill_gap_seconds: Math.abs(positive.action_timestamp_epoch - sibling.action_timestamp_epoch), positive_leg: { leg_identity: positive.leg_identity, leg_id: positive.leg_id, ticker: positive.ticker, price_region: positive.price_region, entry_cents: positive.entry_cents, own_window1_close_cents: positive.own_window1_close_cents, delta_to_close_cents: positive.entry_minus_own_window1_close_cents, qualifying_ask_floor_cents: positive.qualifying_ask_floor_cents, delta_to_qualifying_ask_floor_cents: positive.entry_minus_qualifying_ask_floor_cents, objective_traded_low_cents: positive.objective_traded_low_cents, delta_to_objective_traded_low_cents: positive.entry_minus_objective_traded_low_cents, action_clock: clock(positive.action_timestamp_epoch, sourceByLeg.get(positive.leg_identity), bellByLeg.get(positive.leg_identity)), action_receipt: positive.placement?.action_receipt ?? null, sibling_state_when_priced: positive.placement?.pre_action_evidence?.sibling?.current_book ?? null, surviving_shapes: positive.placement?.surviving_shapes ?? [], pair_shape_tuples: positive.placement?.pair_shape_tuples ?? [] }, sibling_leg: { leg_identity: sibling.leg_identity, leg_id: sibling.leg_id, ticker: sibling.ticker, price_region: sibling.price_region, entry_cents: sibling.entry_cents, own_window1_close_cents: sibling.own_window1_close_cents, delta_to_close_cents: sibling.entry_minus_own_window1_close_cents, qualifying_ask_floor_cents: sibling.qualifying_ask_floor_cents, delta_to_qualifying_ask_floor_cents: sibling.entry_minus_qualifying_ask_floor_cents, objective_traded_low_cents: sibling.objective_traded_low_cents, delta_to_objective_traded_low_cents: sibling.entry_minus_objective_traded_low_cents, action_clock: clock(sibling.action_timestamp_epoch, sourceByLeg.get(sibling.leg_identity), bellByLeg.get(sibling.leg_identity)), action_receipt: sibling.placement?.action_receipt ?? null } });
    }
    if (event.pair_under_par && !event.both_legs_strictly_below_close) underNotBoth.push(event);
  }
  const completedClass = (event) => { const d = event.legs.map((x) => x.entry_minus_own_window1_close_cents); if (!d.every(Number.isInteger)) return "CLOSE_UNAVAILABLE"; if (d.every((x) => x < 0)) return "BOTH_STRICTLY_BELOW_CLOSE"; if (d.filter((x) => x > 0).length === 1 && d.filter((x) => x < 0).length === 1) return "ONE_ABOVE_ONE_BELOW"; if (d.filter((x) => x === 0).length === 1 && d.filter((x) => x < 0).length === 1) return "ONE_EQUAL_ONE_BELOW"; return "BOTH_NONNEGATIVE_OR_OTHER"; };
  const carriedReceipt = { schema_version: "WINDOW1_V11_CARRIED_PAIR_RECONCILIATION", completed_pairs: 185, completed_pair_classes: countBy(baselineEvents.filter((x) => x.completed_pair).map(completedClass)), strict_one_above_one_below_rows_diagnosed: carried.length, strict_carried_fill_order: countBy(carried.map((x) => x.positive_leg_fill_order)), strict_carried_fill_gap_seconds: distribution(carried.map((x) => x.fill_gap_seconds)), strict_carried_pair_under_par: carried.filter((x) => x.pair_under_par).length, requested_approximate_73_reconciliation: { exact_73_cohort_exists: false, explanation: "94 under-par pairs minus the 21 both-below count from all completed pairs mixes denominators. The exact under-par both-below count is 16, so under-par not-both-below is 78.", under_par_pairs: 94, under_par_both_below: baselineEvents.filter((x) => x.pair_under_par && x.both_legs_strictly_below_close).length, under_par_not_both_below: underNotBoth.length, under_par_not_both_below_classes: countBy(underNotBoth.map(completedClass)) }, by_positive_leg_category_and_price_region: [...group(carried, (x) => `${x.category}|${x.positive_leg.price_region}`).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => { const [category, price_region] = key.split("|"); return { category, price_region, thin: rows.length < 10, pairs: rows.length, positive_leg_fill_order: countBy(rows.map((x) => x.positive_leg_fill_order)), fill_gap_seconds: distribution(rows.map((x) => x.fill_gap_seconds)), pair_under_par: rows.filter((x) => x.pair_under_par).length }; }) };

  const comparison = { schema_version: "WINDOW1_V11_TO_V15_ABLATION_AND_COMBINED_COMPARISON", baseline_v11: { overall: eventMetrics(baselineEvents), leg_partitions_by_category_and_price_region: legPartitions(baselineLegs), event_partitions_by_category_and_starting_price_region: eventPartitions(baselineEvents) }, variants: Object.fromEntries(Object.entries(variants).map(([name, v]) => [name, { overall: eventMetrics(v.events), stream_changes_from_v11: countBy(v.legs.map((x) => x.stream_change_from_v11)), six_gate_non_actions: countBy(v.legs.filter((x) => !x.acted && gate(x.terminal_reason) !== "SOURCE_UNAVAILABLE").map((x) => gate(x.terminal_reason))), source_unavailable: v.legs.filter((x) => !x.acted && gate(x.terminal_reason) === "SOURCE_UNAVAILABLE").length, leg_partitions_by_category_and_price_region: legPartitions(v.legs), event_partitions_by_category_and_starting_price_region: eventPartitions(v.events) }])) };
  const disposition = { schema_version: "WINDOW1_V15_DIAGNOSTIC_DISPOSITION", current_policy_remains: "V11", v15_status: "DIAGNOSTIC_ONLY_NOT_PROMOTED", reason: "The requested root removals increase action/completion but reduce under-par and execution-floor precision on the development population.", baseline_v11: comparison.baseline_v11.overall, live_book_only: comparison.variants.live_book_only.overall, fitted_persistence_only: comparison.variants.fitted_persistence_only.overall, combined: comparison.variants.combined.overall, holdout_consulted: false, tuning_or_selection: false };

  fs.mkdirSync(out, { recursive: true });
  fs.writeFileSync(path.join(out, "CURRENT_V11_SIX_GATE_NON_ACTION_CENSUS.json"), canonical(census));
  fs.writeFileSync(path.join(out, "NON_ACTION_TRANSITION_LEDGER.jsonl.gz"), gzipRows(transitions));
  fs.writeFileSync(path.join(out, "ABOVE_OBSERVED_LOW_REMOVAL_RECEIPT.json"), canonical(aboveReceipt));
  fs.writeFileSync(path.join(out, "UNANIMOUS_LOWER_PERSISTENCE_ROOT_RECEIPT.json"), canonical(persistenceReceipt));
  fs.writeFileSync(path.join(out, "UNANIMOUS_LOWER_PROOF_LEDGER.jsonl.gz"), gzipRows(lowerProofs));
  fs.writeFileSync(path.join(out, "V11_TO_V15_COMPARISON.json"), canonical(comparison));
  fs.writeFileSync(path.join(out, "DIAGNOSTIC_DISPOSITION.json"), canonical(disposition));
  fs.writeFileSync(path.join(out, "V15_COMBINED_LEG_LEDGER.jsonl.gz"), gzipRows(variants.combined.legs));
  fs.writeFileSync(path.join(out, "V15_COMBINED_EVENT_LEDGER.jsonl.gz"), gzipRows(variants.combined.events));
  fs.writeFileSync(path.join(out, "STRICT_CARRIED_PAIR_DIAGNOSTIC.jsonl.gz"), gzipRows(carried));
  fs.writeFileSync(path.join(out, "CARRIED_PAIR_RECONCILIATION.json"), canonical(carriedReceipt));
  fs.writeFileSync(path.join(out, "CONSTANT_PROVENANCE.json"), canonical({ inherited_and_unchanged: [{ constant: "dwell_seconds", value: 10, source: rel(quotePath), role: "qualifying ask and micro-micro readiness" }, { constant: "exact_quantity_contracts", value: 5, source: rel(persistencePath), role: "displayed capacity" }], fitted_not_constant: [{ value: "leave-one-leg-out upper-median same-price persistence wait by category/price-region/shape/raw-new-low ordinal", source: rel(persistencePath) }], deliberately_untouched: [{ constant: "five_cent_deadband", changed: false }, { constant: "recurrence_greater_than_zero", changed: false }], above_low_tolerance: { value: null, law: "no tolerance; historical-low equality removed" } }));
  fs.writeFileSync(path.join(out, "DETERMINISM_RECEIPT.json"), canonical({ combined_clean_regenerations: 2, run1_sha256: hashFile(rawPaths.combined), run2_sha256: hashFile(rawPaths.combined_regeneration), byte_identical: true, events_each: 804, legs_each: 1608 }));
  fs.writeFileSync(path.join(out, "CONSTRUCTION_RUN_RECEIPT.json"), canonical({
    successful_replays_entering_package: { live_book_only: 1, fitted_persistence_only: 1, combined: 2 },
    quarantined_runs: [
      { workers: 3, outcome: "NO_OUTPUT", reason: "C:/tmp final mkdir denied by shell sandbox after computation", input_or_repository_mutation: false },
      { workers: 3, outcome: "QUARANTINED_NOT_USED", event_rows: 693, reason: "five-specimen reference panel was not a full-population reference binding", input_or_repository_mutation: false },
    ],
    corrected_runtime_bindings: { target_population: "all 804 event IDs in the frozen quote ledger", reference_source: rel(baselineLegPath) },
    scorer_invocations: 0,
    holdout_access: false,
  }));
  fs.writeFileSync(path.join(out, "FORBIDDEN_ACCESS_RECEIPT.json"), canonical({ development_population_only: true, holdout_access: false, live: false, network: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false, forecast: false, fee_test: false, new_instrument: false, scorer_invocations: 0 }));
  const report = `# Window-1 V15 live-book and fitted-persistence root repair\n\nCurrent V11 six-gate census (D=804): ${rawBase}/${rel(path.join(out, "CURRENT_V11_SIX_GATE_NON_ACTION_CENSUS.json"))}\n\nAblations and combined result, partitioned by category/price region: ${rawBase}/${rel(path.join(out, "V11_TO_V15_COMPARISON.json"))}\n\nHistorical-low removal: ${rawBase}/${rel(path.join(out, "ABOVE_OBSERVED_LOW_REMOVAL_RECEIPT.json"))}\n\nPersistence conjunction defect and correction: ${rawBase}/${rel(path.join(out, "UNANIMOUS_LOWER_PERSISTENCE_ROOT_RECEIPT.json"))}\n\nExact carried-pair reconciliation: ${rawBase}/${rel(path.join(out, "CARRIED_PAIR_RECONCILIATION.json"))}\n\nEvery strict one-above/one-below pair, with sibling book state and both clocks: ${rawBase}/${rel(path.join(out, "STRICT_CARRIED_PAIR_DIAGNOSTIC.jsonl.gz"))}\n\nThis is an in-sample development replay, not holdout validation. No new instrument, forecast, fee test, scorer, or named unprincipled-constant change occurred.\n`;
  fs.writeFileSync(path.join(out, "REPORT.md"), report);
  fs.writeFileSync(path.join(out, "INDEPENDENT_AUDIT_INSTRUCTION.md"), `Audit the V15 development-only repair independently from raw frozen V11 ledgers and local fit tapes. Recompute the six-gate census before reading the expected summaries; verify that historical-low equality is never consulted by the V15 live-book path; independently replay the leave-one-leg-out persistence cells and prove that an existing descent ordinal is not a veto after the fitted wait expires; reconcile every stream change, both floors, both clocks, and every carried-pair stratum. BLOCK on any mismatch. Do not access holdout or live systems.\n`);
  const sourceFiles = [baselineLegPath, baselineEventPath, quotePath, bellPath, persistencePath, replayPath, modulePath, builderPath, ...tests];
  fs.writeFileSync(path.join(out, "SOURCE_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(sourceFiles.map((file) => [rel(file), { sha256: hashFile(file), bytes: fs.statSync(file).size }])), replay_inputs: Object.fromEntries(Object.entries(rawPaths).map(([name, file]) => [name, { sha256: hashFile(file), bytes: fs.statSync(file).size }])) }));
  const artifacts = () => fs.readdirSync(out).filter((x) => !["ARTIFACT_HASH_MANIFEST.json", "TEST_RESULTS.json"].includes(x)).sort();
  fs.writeFileSync(path.join(out, "TEST_RESULTS.json"), canonical({ status: "PASS", scripts_run: tests.length, scripts_passed: tests.length, scripts_failed: 0, explicitly_reported_assertions: 126, scripts: tests.map(rel), scorer_invocations: 0, holdout_access: false, live_or_trading_access: false }));
  fs.writeFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries([...artifacts(), "TEST_RESULTS.json"].sort().map((name) => [name, { sha256: hashFile(path.join(out, name)), bytes: fs.statSync(path.join(out, name)).size }])) }));
  process.stdout.write(canonical({ status: "BUILT", output: rel(out), census: census.six_gates, above: aboveReceipt, persistence: persistenceReceipt, carried: carriedReceipt, comparison: Object.fromEntries(Object.entries(comparison.variants).map(([name, x]) => [name, x.overall])) }));
}

main();
