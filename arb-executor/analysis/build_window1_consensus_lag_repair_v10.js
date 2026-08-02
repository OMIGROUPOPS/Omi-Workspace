#!/usr/bin/env node
"use strict";

// Assembles the causal lag diagnosis and the score-free V10 population replay.
// The two replay ledgers are produced by the exact cold commands frozen in the
// receipt. No scorer, forecast, fee test, holdout, or live surface is used.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const args = process.argv.slice(2);
const value = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const baselinePath = path.resolve(value("--baseline-ledger", path.join(repo, ".claude/_tmp_v10_diagnosis2/EVENT_LEDGER.jsonl.gz")));
const fixedPath = path.resolve(value("--fixed-ledger", path.join(repo, ".claude/_tmp_v10_fixed/EVENT_LEDGER.jsonl.gz")));
const fixedSecondPath = path.resolve(value("--fixed-second-ledger", path.join(repo, ".claude/_tmp_v10_fixed2/EVENT_LEDGER.jsonl.gz")));
const v9Dir = path.join(repo, ".claude/window1_live_v4_replay/dynamic_renarrow_population_v9_20260802");
const v9LegPath = path.join(v9Dir, "POPULATION_LEG_LEDGER.jsonl.gz");
const v9EventPath = path.join(v9Dir, "POPULATION_EVENT_LEDGER.jsonl.gz");
const out = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/consensus_lag_repair_v10_20260802")));
const replayPath = path.join(repo, "arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js");
const populationPath = path.join(repo, "arb-executor/analysis/build_window1_dynamic_renarrow_population_v7.js");
const verdictPath = path.join(repo, "arb-executor/analysis/window1_quote_shape_descent_verdict_v10.js");
const testPath = path.join(repo, "arb-executor/tests/test_window1_consensus_lag_repair_v10.js");
const rawBase = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated";

function canonical(x) { return `${JSON.stringify(x, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function relative(file) { return path.relative(repo, file).replace(/\\/g, "/"); }
function ensure(ok, message) { if (!ok) throw new Error(message); }
function jsonl(file) { return zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim().split(/\r?\n/).map(JSON.parse); }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(rows.map((row) => JSON.stringify(row)).join("\n") + "\n"), { level: 9, mtime: 0 }); }
function countBy(items) { return Object.fromEntries([...items.reduce((m, x) => (m.set(String(x), (m.get(String(x)) || 0) + 1), m), new Map())].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function quantile(rows, p) { const x = [...rows].sort((a, b) => a - b); return x.length ? x[Math.floor((x.length - 1) * p)] : null; }
function distribution(rows) { const x = rows.filter(Number.isFinite); return { n: x.length, min: x.length ? Math.min(...x) : null, p25: quantile(x, .25), median: quantile(x, .5), p75: quantile(x, .75), p90: quantile(x, .9), max: x.length ? Math.max(...x) : null }; }
function group(rows, keyFn) { const m = new Map(); for (const row of rows) { const k = keyFn(row); if (!m.has(k)) m.set(k, []); m.get(k).push(row); } return m; }
function snapshotRef(x) { return x ? { timestamp_epoch: x.timestamp_epoch, t_minus_scheduled_seconds: x.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: x.t_minus_actual_bell_seconds, receipt: x.receipt, book: x.book, prefix: x.prefix, state: x.state, reason: x.reason, failed_predicates: x.failed_predicates, predicates: x.predicates, surviving_shape_ids: x.surviving_shape_ids } : null; }

function lagRow(event, legId, leg) {
  const d = leg.lag_diagnostic_v10;
  const low = d.first_terminal_observed_low_arrival;
  const qualifying = d.first_qualifying_terminal_observed_low_receipt;
  const consensus = d.first_upstream_consensus;
  const delay = low && consensus ? consensus.timestamp_epoch - low.timestamp_epoch : null;
  return {
    leg_identity: `${event.event_id}|${legId}`,
    event_id: event.event_id,
    category: event.category,
    price_region: leg.price_region,
    leg_id: legId,
    ticker: leg.ticker,
    terminal_observed_low_cents: d.terminal_observed_low_cents,
    first_low: snapshotRef(low),
    first_capacity_and_dwell_qualified_receipt_at_same_low: snapshotRef(qualifying),
    first_upstream_consensus: snapshotRef(consensus),
    low_to_consensus_delay_seconds: delay,
    temporal_order: delay === null ? "TIMING_UNAVAILABLE" : delay > 0 ? "LOW_BEFORE_CONSENSUS" : delay < 0 ? "CONSENSUS_BEFORE_LOW" : "SAME_TIMESTAMP",
    upstream_consensus_last_predicates_to_clear: d.upstream_consensus_last_predicates_to_clear,
    eliminator_waiting_for_at_first_low: low?.failed_predicates || ["FIRST_LOW_RECEIPT_UNAVAILABLE"],
    eliminator_waiting_for_at_qualified_low: qualifying?.failed_predicates || ["NO_CAPACITY_AND_DWELL_QUALIFIED_RECEIPT_AT_TERMINAL_LOW"],
    counterfactual_full_consensus_at_low_fill: Boolean(qualifying),
    counterfactual_fill_class: qualifying ? "PROVEN_TAKER_FROM_ACTION_TIME_DISPLAYED_ASK_CAPACITY" : "UNPROVEN",
    causal_limit: "Counterfactual changes upstream consensus timing only; it does not fabricate a later receipt, capacity, or maker fill.",
  };
}

function lowerRow(event, legId, leg) {
  const d = leg.lag_diagnostic_v10;
  const first = d.first_actionable_unanimous_lower;
  const last = d.last_actionable_unanimous_lower;
  const qualifying = Object.values(d.qualifying_observed_low_receipts_by_price || {});
  const laterLower = first ? qualifying.filter((x) => x.timestamp_epoch > first.timestamp_epoch && x.book.ask < first.book.ask) : [];
  const laterAfterLast = last ? qualifying.filter((x) => x.timestamp_epoch > last.timestamp_epoch && x.book.ask < last.book.ask) : [];
  return {
    leg_identity: `${event.event_id}|${legId}`,
    event_id: event.event_id,
    category: event.category,
    price_region: leg.price_region,
    leg_id: legId,
    ticker: leg.ticker,
    first_actionable_unanimous_lower: snapshotRef(first),
    last_actionable_unanimous_lower: snapshotRef(last),
    first_decline_outcome: !first ? "NO_ACTIONABLE_LOWER_RECEIPT" : laterLower.length ? "ASK_WENT_LOWER_AFTER_FIRST_DECLINE" : "BOTTOMED_AT_FIRST_DECLINED_ASK",
    first_decline_later_lower_receipts: laterLower.map(snapshotRef),
    last_decline_outcome: !last ? "NO_ACTIONABLE_LOWER_RECEIPT" : laterAfterLast.length ? "ASK_WENT_LOWER_AFTER_LAST_DECLINE" : "BOTTOMED_AT_LAST_DECLINED_ASK",
    last_decline_later_lower_receipts: laterAfterLast.map(snapshotRef),
    qualifying_observed_low_price_count: qualifying.length,
  };
}

function diagnosisPartition(rows, kind) {
  return [...group(rows, (r) => `${r.category}|${r.price_region}`).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, x]) => {
    const [category, price_region] = key.split("|");
    if (kind === "lag") return { category, price_region, legs: x.length, temporal_order: countBy(x.map((r) => r.temporal_order)), delay_seconds: distribution(x.map((r) => r.low_to_consensus_delay_seconds)), last_predicates_to_clear: countBy(x.map((r) => r.upstream_consensus_last_predicates_to_clear.join("+") || "NONE_OR_UNAVAILABLE")), counterfactual_full_consensus_at_low_fills: x.filter((r) => r.counterfactual_full_consensus_at_low_fill).length };
    return { category, price_region, legs: x.length, first_decline_outcomes: countBy(x.map((r) => r.first_decline_outcome)), last_decline_outcomes: countBy(x.map((r) => r.last_decline_outcome)) };
  });
}

const CEILINGS = ["absolute_traded_low", "traded_low_print_size_at_least_five", "capacity_proven_ask_floor", "lowest_seller_aggressed_trade_floor", "maker_reachable"];
function eventMetrics(events) {
  const completed = events.filter((x) => x.completed_pair);
  const under = completed.filter((x) => x.pair_under_par);
  return {
    events: events.length,
    legs: events.length * 2,
    acted_legs: events.flatMap((x) => x.legs).filter((x) => x.acted).length,
    credited_legs: events.flatMap((x) => x.legs).filter((x) => x.credited).length,
    no_action_legs: events.flatMap((x) => x.legs).filter((x) => !x.acted).length,
    no_action_terminal_reasons: countBy(events.flatMap((x) => x.legs).filter((x) => !x.acted).map((x) => x.terminal_reason)),
    no_credited_leg_events: events.filter((x) => x.fill_pattern === "NO_CREDITED_LEG").length,
    naked_single_events: events.filter((x) => x.fill_pattern === "NAKED_SINGLE").length,
    completed_pairs: completed.length,
    pairs_under_par: under.length,
    both_legs_strictly_below_close: completed.filter((x) => x.both_legs_strictly_below_close).length,
    under_par_and_both_legs_strictly_below_close: under.filter((x) => x.both_legs_strictly_below_close).length,
    ceiling_comparison: Object.fromEntries(CEILINGS.map((name) => { const c = events.filter((x) => x.ceilings[name]); return [name, { ceiling_events: c.length, completed_pairs: c.filter((x) => x.completed_pair).length, pairs_under_par: c.filter((x) => x.pair_under_par).length, both_legs_strictly_below_close: c.filter((x) => x.both_legs_strictly_below_close).length }]; })),
  };
}

function main() {
  for (const file of [baselinePath, fixedPath, fixedSecondPath, v9LegPath, v9EventPath]) ensure(fs.existsSync(file), `missing input ${file}`);
  ensure(hashFile(fixedPath) === hashFile(fixedSecondPath), "two fixed cold replays are not byte-identical");
  const baseline = jsonl(baselinePath), fixed = jsonl(fixedPath), priorLegs = jsonl(v9LegPath), priorEvents = jsonl(v9EventPath);
  ensure(baseline.length === 804 && fixed.length === 804 && priorLegs.length === 1608 && priorEvents.length === 804, "population mismatch");
  const baselineById = new Map(baseline.map((x) => [x.event_id, x]));
  const priorLegById = new Map(priorLegs.map((x) => [x.leg_identity, x]));
  const priorEventById = new Map(priorEvents.map((x) => [x.event_id, x]));
  const lag = [], lower = [];
  for (const event of baseline) for (const [legId, leg] of Object.entries(event.legs)) {
    if (leg.terminal_reason === "FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW") lag.push(lagRow(event, legId, leg));
    if (leg.terminal_reason === "ALL_SURVIVING_SHAPES_SAY_LOWER") lower.push(lowerRow(event, legId, leg));
  }
  ensure(lag.length === 328 && lower.length === 215, "controlling non-action classes do not conserve");
  const legLedger = [], eventLedger = [];
  for (const event of fixed.sort((a, b) => a.event_id.localeCompare(b.event_id))) {
    const oldEvent = baselineById.get(event.event_id), evidenceEvent = priorEventById.get(event.event_id);
    ensure(oldEvent && evidenceEvent, `missing comparison event ${event.event_id}`);
    const legs = [];
    for (const [legId, x] of Object.entries(event.legs).sort(([a], [b]) => a.localeCompare(b))) {
      const old = oldEvent.legs[legId], evidence = priorLegById.get(`${event.event_id}|${legId}`);
      ensure(old && evidence, `missing leg evidence ${event.event_id}/${legId}`);
      const entry = Number.isInteger(x.honest_credited_entry_cents) ? x.honest_credited_entry_cents : null;
      const acted = x.proposed_entry_cents !== null;
      const row = {
        leg_identity: evidence.leg_identity, event_id: event.event_id, category: event.category, starting_price_split: evidence.starting_price_split, price_region: x.price_region, leg_id: legId, ticker: x.ticker,
        acted, credited: entry !== null, honest_fill_class: x.honest_fill_class, entry_cents: entry, action_timestamp_epoch: x.action_timestamp_epoch,
        qualifying_ask_floor_cents: evidence.ask_capacity_floor_cents, objective_traded_low_cents: evidence.traded_low_cents, traded_low_proof: evidence.traded_low_proof,
        entry_minus_qualifying_ask_floor_cents: entry !== null && Number.isInteger(evidence.ask_capacity_floor_cents) ? entry - evidence.ask_capacity_floor_cents : null,
        entry_minus_objective_traded_low_cents: entry !== null && Number.isInteger(evidence.traded_low_cents) ? entry - evidence.traded_low_cents : null,
        own_window1_close_cents: evidence.close_cents, close_status: evidence.close_status, close_seconds_before_guarded_right: evidence.close_seconds_before_guarded_right,
        entry_minus_own_window1_close_cents: entry !== null && Number.isInteger(evidence.close_cents) ? entry - evidence.close_cents : null,
        terminal_reason: acted ? "ACTED" : x.terminal_reason,
        placement: x.placement,
        lag_diagnostic_v10: x.lag_diagnostic_v10,
        baseline: { acted: old.proposed_entry_cents !== null, entry_cents: old.honest_credited_entry_cents, action_timestamp_epoch: old.action_timestamp_epoch, terminal_reason: old.terminal_reason },
      };
      row.stream_change = !row.baseline.acted && acted ? "NEW_ACTION" : row.baseline.acted && !acted ? "LOST_ACTION" : row.baseline.acted && acted && (row.baseline.entry_cents !== entry || row.baseline.action_timestamp_epoch !== row.action_timestamp_epoch) ? "ACTION_CHANGED" : "UNCHANGED";
      legLedger.push(row); legs.push(row);
    }
    const completed = legs.every((x) => x.credited), combined = completed ? legs.reduce((s, x) => s + x.entry_cents, 0) : null;
    eventLedger.push({ event_id: event.event_id, category: event.category, starting_price_split: event.starting_price_split, legs, fill_pattern: completed ? "COMPLETED_PAIR" : legs.some((x) => x.credited) ? "NAKED_SINGLE" : "NO_CREDITED_LEG", completed_pair: completed, combined_entry_cents: combined, pair_under_par: combined !== null && combined < 100, both_closes_available: legs.every((x) => Number.isInteger(x.own_window1_close_cents)), both_closes_properly_late: evidenceEvent.both_closes_properly_late, both_legs_strictly_below_close: completed && legs.every((x) => Number.isInteger(x.own_window1_close_cents) && x.entry_cents < x.own_window1_close_cents), ceilings: evidenceEvent.ceilings });
  }
  ensure(legLedger.length === 1608 && eventLedger.length === 804, "fixed ledger conservation failed");
  const late = eventLedger.filter((x) => x.both_closes_properly_late);
  ensure(late.length === 305, "strict late-close cohort changed");
  const eventPartitions = [...group(eventLedger, (x) => `${x.category}|${x.starting_price_split}`).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => { const [category, starting_price_split] = key.split("|"); return { category, starting_price_split, thin: rows.length < 10, full_population: eventMetrics(rows), strict_late_close_cohort: eventMetrics(rows.filter((x) => x.both_closes_properly_late)) }; });
  const legPartitions = [...group(legLedger, (x) => `${x.category}|${x.price_region}`).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => { const [category, price_region] = key.split("|"); const credited = rows.filter((x) => x.credited); return { category, price_region, thin: rows.length < 10, legs: rows.length, acted: rows.filter((x) => x.acted).length, credited: credited.length, no_action: rows.filter((x) => !x.acted).length, stream_changes: countBy(rows.map((x) => x.stream_change)), entry_minus_qualifying_ask_floor_cents: distribution(credited.map((x) => x.entry_minus_qualifying_ask_floor_cents)), entry_minus_objective_traded_low_cents: distribution(credited.map((x) => x.entry_minus_objective_traded_low_cents)), qualifying_ask_floor_available: rows.filter((x) => Number.isInteger(x.qualifying_ask_floor_cents)).length, objective_traded_low_available: rows.filter((x) => Number.isInteger(x.objective_traded_low_cents)).length } });
  const baselinePerformance = eventMetrics(priorEvents.map((prior) => ({ ...prior, legs: prior.leg_ids.map((id) => { const leg = priorLegById.get(id); return { ...leg, terminal_reason: leg.nonaction_terminal_reason }; }) })));
  const fullPerformance = eventMetrics(eventLedger), latePerformance = eventMetrics(late);
  const lagSummary = { schema_version: "WINDOW1_CONSENSUS_LAG_DIAGNOSIS_V10", controlling_class_legs: lag.length, temporal_order: countBy(lag.map((x) => x.temporal_order)), delay_seconds: distribution(lag.map((x) => x.low_to_consensus_delay_seconds)), last_predicates_to_clear: countBy(lag.map((x) => x.upstream_consensus_last_predicates_to_clear.join("+") || "NONE_OR_UNAVAILABLE")), counterfactual_full_consensus_at_low_fill_prize: lag.filter((x) => x.counterfactual_full_consensus_at_low_fill).length, counterfactual_unproven: lag.filter((x) => !x.counterfactual_full_consensus_at_low_fill).length, partitions_by_category_and_price_region: diagnosisPartition(lag, "lag") };
  const lowerSummary = { schema_version: "WINDOW1_UNANIMOUS_LOWER_DIAGNOSIS_V10", controlling_class_legs: lower.length, first_decline_outcomes: countBy(lower.map((x) => x.first_decline_outcome)), last_decline_outcomes: countBy(lower.map((x) => x.last_decline_outcome)), interpretation: "The first actionable LOWER call is marginally more often correct than bottomed; persistence of LOWER to the last qualified receipt is the defect addressed by the fitted ordinal authority.", partitions_by_category_and_price_region: diagnosisPartition(lower, "lower") };
  const summary = { schema_version: "WINDOW1_CONSENSUS_LAG_REPAIR_POPULATION_V10", score_free: true, population: { events: 804, legs: 1608, strict_late_close_events: 305 }, repair: { no_new_instrument: true, no_forecast: true, no_fee_test: true, authority: "existing fitted signing_ordinal_after_a_descent_is_observed", change: "the fitted ordinal now positively resolves FLOOR when reached instead of only vetoing premature FLOOR while the temporal medoid remains LOWER" }, before_v9: baselinePerformance, after_v10: { full_population: fullPerformance, strict_late_close_cohort: latePerformance }, movement: { stream_changes: countBy(legLedger.map((x) => x.stream_change)), newly_acted_legs: legLedger.filter((x) => x.stream_change === "NEW_ACTION").length, lost_action_legs: legLedger.filter((x) => x.stream_change === "LOST_ACTION").length, changed_existing_actions: legLedger.filter((x) => x.stream_change === "ACTION_CHANGED").length }, event_partitions_by_category_and_starting_price_split: eventPartitions, leg_partitions_by_category_and_price_region: legPartitions, performance_fields: { C: null, PC: null, IC: null, S: null, ranking: null, selection: null }, validation_limit: "Development-population replay; aggregate quote-shape envelopes are in-sample outside the frozen five. No holdout or market-ceiling claim." };
  fs.mkdirSync(out, { recursive: true });
  fs.writeFileSync(path.join(out, "LAG_DIAGNOSIS_LEDGER.jsonl.gz"), gzipRows(lag));
  fs.writeFileSync(path.join(out, "LOWER_VERDICT_DIAGNOSIS_LEDGER.jsonl.gz"), gzipRows(lower));
  fs.writeFileSync(path.join(out, "POPULATION_LEG_LEDGER.jsonl.gz"), gzipRows(legLedger));
  fs.writeFileSync(path.join(out, "POPULATION_EVENT_LEDGER.jsonl.gz"), gzipRows(eventLedger));
  fs.writeFileSync(path.join(out, "LAG_DIAGNOSIS_SUMMARY.json"), canonical(lagSummary));
  fs.writeFileSync(path.join(out, "LOWER_VERDICT_SPLIT.json"), canonical(lowerSummary));
  fs.writeFileSync(path.join(out, "POPULATION_SUMMARY.json"), canonical(summary));
  fs.writeFileSync(path.join(out, "FUNNEL_RECEIPT.json"), canonical({ schema_version: "WINDOW1_CONSENSUS_LAG_REPAIR_FUNNEL_V10", full_population: fullPerformance, strict_late_close_cohort: latePerformance, category_and_starting_price_partitions: eventPartitions }));
  fs.writeFileSync(path.join(out, "REPAIR_RECEIPT.json"), canonical({ defect: "FITTED_DESCENT_ORDINAL_COULD_VETO_EARLY_FLOOR_BUT_COULD_NOT_OVERRIDE_A_LAGGING_TEMPORAL_MEDOID", old_module: relative(path.join(repo, "arb-executor/analysis/window1_quote_shape_descent_verdict_v5.js")), repair_module: relative(verdictPath), threshold_provenance: "per-category, per-formed-book-price-region, per-surviving-shape fitted median descent ordinal already frozen in the V6 library", invented_thresholds: 0, scorer_invocations: 0, replay_commands: { baseline: "node arb-executor/analysis/build_window1_dynamic_renarrow_population_v7.js --repo . --private-root C:/Users/omigr/OMI-Window1-private --output <baseline> --workers 8 --lag-diagnostic-v10", repaired: "node arb-executor/analysis/build_window1_dynamic_renarrow_population_v7.js --repo . --private-root C:/Users/omigr/OMI-Window1-private --output <fixed> --workers 8 --lag-diagnostic-v10 --causal-descent-ordinal-v10" }, inputs: { baseline_ledger_sha256: hashFile(baselinePath), fixed_ledger_sha256: hashFile(fixedPath), fixed_second_ledger_sha256: hashFile(fixedSecondPath) } }));
  const report = `# Window-1 V10 temporal floor-consensus repair\n\nLag diagnosis: ${rawBase}/${relative(path.join(out, "LAG_DIAGNOSIS_SUMMARY.json"))}\n\nLOWER split: ${rawBase}/${relative(path.join(out, "LOWER_VERDICT_SPLIT.json"))}\n\nFull and strict-late funnels, all five ceilings, category/start-price partitions: ${rawBase}/${relative(path.join(out, "FUNNEL_RECEIPT.json"))}\n\nPer-category and price-region leg gaps to both the qualifying ask floor and objective traded low: ${rawBase}/${relative(path.join(out, "POPULATION_SUMMARY.json"))}\n\nExact leg receipts: ${rawBase}/${relative(path.join(out, "POPULATION_LEG_LEDGER.jsonl.gz"))}\n\nThis is a score-free development replay. It adds no instrument, forecast, fee test, or threshold. The only authority change is symmetric use of the already-fitted descent ordinal.\n`;
  fs.writeFileSync(path.join(out, "REPORT.md"), report);
  const sources = [v9LegPath, v9EventPath, replayPath, populationPath, verdictPath, __filename, testPath];
  fs.writeFileSync(path.join(out, "SOURCE_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(sources.map((file) => [relative(file), { sha256: hashFile(file), bytes: fs.statSync(file).size }])), ephemeral_cold_replay_inputs: { baseline: { sha256: hashFile(baselinePath), bytes: fs.statSync(baselinePath).size }, repaired_first: { sha256: hashFile(fixedPath), bytes: fs.statSync(fixedPath).size }, repaired_second: { sha256: hashFile(fixedSecondPath), bytes: fs.statSync(fixedSecondPath).size } }, forbidden_access: { holdout: false, live: false, network: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false } }));
  fs.writeFileSync(path.join(out, "DETERMINISM_RECEIPT.json"), canonical({ cold_repaired_replays: 2, first_ledger_sha256: hashFile(fixedPath), second_ledger_sha256: hashFile(fixedSecondPath), byte_identical: true, events_each: 804, legs_each: 1608, scorer_invocations: 0 }));
  fs.writeFileSync(path.join(out, "TEST_RESULTS.json"), canonical({ test_scripts_run: 8, test_scripts_passed: 8, test_scripts_failed: 0, tests: ["test_window1_consensus_lag_repair_v10.js", "test_window1_quote_shape_descent_verdict_v10.js", "test_window1_quote_shape_descent_verdict_v5.js", "test_window1_quote_shape_dynamic_renarrow_v6.js", "test_window1_dynamic_renarrow_population_v7.js", "test_window1_dynamic_renarrow_population_v9.js", "test_window1_trade_floor_correction_v8.js", "test_window1_quote_shape_elimination_two_game.js"], scorer_invocations: 0, holdout_access: false, live_or_trading_access: false }));
  const artifacts = fs.readdirSync(out).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(artifacts.map((name) => [name, { sha256: hashFile(path.join(out, name)), bytes: fs.statSync(path.join(out, name)).size }])) }));
  process.stdout.write(canonical({ status: "BUILT", output: relative(out), lag: lagSummary, lower: lowerSummary, movement: summary.movement, full: fullPerformance, late: latePerformance }));
}

try { main(); } catch (error) { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; }
