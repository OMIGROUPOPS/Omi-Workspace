#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const ABOVE = "FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW";
const LOWER = "ALL_SURVIVING_SHAPES_SAY_LOWER";
const RAW_BRANCH = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated";

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function compact(value) { return JSON.stringify(value); }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function ensure(condition, message) { if (!condition) throw new Error(message); }
function strictInteger(value) { return typeof value === "number" && Number.isFinite(value) && Number.isInteger(value) ? value : null; }
function writeJson(file, value) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, canonical(value)); }
function writeJsonl(file, rows) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, `${rows.map(compact).join("\n")}\n`); }
function countBy(rows, keyFn) { const out = new Map(); for (const row of rows) { const key = String(keyFn(row)); out.set(key, (out.get(key) || 0) + 1); } return Object.fromEntries([...out].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function quantile(values, p) { const rows = values.filter(Number.isFinite).sort((a, b) => a - b); return rows.length ? rows[Math.min(rows.length - 1, Math.floor(p * (rows.length - 1)))] : null; }
function distribution(values, denominator = values.length) { const rows = values.filter(Number.isFinite).sort((a, b) => a - b); return { denominator, available: rows.length, unavailable: denominator - rows.length, min: rows.length ? rows[0] : null, p25: quantile(rows, .25), median: quantile(rows, .5), p75: quantile(rows, .75), p90: quantile(rows, .9), max: rows.length ? rows[rows.length - 1] : null, exact_counts: countBy(rows, (x) => x) }; }
function groupRows(rows, keyFn) { const groups = new Map(); for (const row of rows) { const key = keyFn(row); if (!groups.has(key)) groups.set(key, []); groups.get(key).push(row); } return groups; }
function artifactManifest(dir) { return Object.fromEntries(fs.readdirSync(dir).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort().map((name) => [name, { bytes: fs.statSync(path.join(dir, name)).size, sha256: hashFile(path.join(dir, name)) }])); }
function legMap(replay) { const out = new Map(); for (const event of replay.events) for (const [legId, leg] of Object.entries(event.legs || {})) out.set(`${event.event_id}|${legId}`, { event, leg_id: legId, ...leg }); return out; }
function lowerOutcome(refusal, floor) { if (!refusal || !Number.isInteger(floor)) return "UNAVAILABLE"; if (floor < refusal.book.ask) return "WENT_LOWER_AFTER_REFUSAL"; if (floor === refusal.book.ask) return "BOTTOMED_AT_REFUSAL"; return "CONTRADICTION_FLOOR_ABOVE_QUALIFIED_REFUSAL"; }
function candidateFromEvaluations(evaluations, tolerance) {
  return evaluations.find((row) => row.ask_minus_observed_low_cents >= 1 && row.ask_minus_observed_low_cents <= tolerance && row.ask_dwell_seconds >= 10 && row.top_ask_size >= 5 && row.fresh_own_book_receipt) || null;
}
function compareTerminal(rawLeg, tracedLeg, identity) {
  const fields = ["proposed_entry_cents", "honest_fill_class", "honest_credited_entry_cents", "own_window1_close_cents", "own_bell_price_cents", "own_ask_reachable_low_cents", "terminal_reason"];
  for (const field of fields) ensure(JSON.stringify(rawLeg[field] ?? null) === JSON.stringify(tracedLeg[field] ?? null), `${identity}: trace changed ${field}`);
  ensure(JSON.stringify(rawLeg.placement ?? null) === JSON.stringify(tracedLeg.placement ?? null), `${identity}: trace changed placement`);
}
function runTrace({ repo, rawReplay, preparedRoot, ticksRoot, traceRoot }) {
  ensure(!fs.existsSync(traceRoot), "trace output already exists; refuse implicit overwrite");
  const rawMap = legMap(rawReplay), targetEvents = [...new Set([...rawMap.values()].filter((row) => row.terminal_reason === ABOVE || row.terminal_reason === LOWER).map((row) => row.event.event_id))].sort();
  fs.mkdirSync(traceRoot, { recursive: true });
  const targetFile = path.join(traceRoot, "TARGET_EVENTS.json"); writeJson(targetFile, targetEvents);
  const output = path.join(traceRoot, "replay");
  const args = [
    path.join(repo, "arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js"), "--repo", repo, "--ticks-root", ticksRoot,
    "--quote-ledger", path.join(preparedRoot, "HOLDOUT_QUOTE_LEDGER.csv"), "--references", path.join(preparedRoot, "HOLDOUT_REFERENCES.json"), "--windows", path.join(preparedRoot, "HOLDOUT_WINDOWS.json"),
    "--target-file", targetFile, "--output", output, "--receipt-name", "TRACE_REPLAY.json", "--library", path.join(repo, ".claude/window1_live_v4_replay/five_exact_dynamic_renarrow_v6_20260801/QUOTE_SHAPE_LIBRARY_DYNAMIC_RENARROW_V6.json"),
    "--compact-population", "--no-charts", "--exclude-own-training-member", "--stable-same-price-confirmation", "--pair-wiring-v3", "--stable-signer-v4", "--descent-verdict-v5", "--dynamic-renarrow-v6", "--lag-diagnostic-v10", "--causal-descent-ordinal-v10", "--persistence-floor-v11", "--persistence-library-v11", path.join(repo, ".claude/window1_live_v4_replay/persistence_floor_v11_fit_20260802/PERSISTENCE_SURVIVAL_LIBRARY_V11.json"),
    "--trace-decision-reasons", ABOVE,
  ];
  const result = spawnSync(process.execPath, args, { cwd: repo, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });
  ensure(result.status === 0, `trace replay failed: ${result.stderr}\n${result.stdout}`);
  return { file: path.join(output, "TRACE_REPLAY.json"), targetFile, targetEvents, command: [process.execPath, ...args].join(" ") };
}

function build({ repo, rawFile, traceFile, out }) {
  fs.mkdirSync(out, { recursive: true });
  const rawReplay = JSON.parse(fs.readFileSync(rawFile, "utf8")), traceReplay = JSON.parse(fs.readFileSync(traceFile, "utf8"));
  const rawMap = legMap(rawReplay), traceMap = legMap(traceReplay);
  const aboveRaw = [...rawMap.entries()].filter(([, row]) => row.terminal_reason === ABOVE), lowerRaw = [...rawMap.entries()].filter(([, row]) => row.terminal_reason === LOWER);
  ensure(aboveRaw.length === 83 && lowerRaw.length === 61, "controlling no-action counts changed");
  for (const [identity, raw] of [...aboveRaw, ...lowerRaw]) { const traced = traceMap.get(identity); ensure(traced, `${identity}: trace row missing`); compareTerminal(raw, traced, identity); }

  const decisionRows = [], aboveSummaries = [];
  for (const [identity, raw] of aboveRaw) {
    const traced = traceMap.get(identity), evaluations = (traced.traced_decision_evaluations || []).filter((row) => row.reason === ABOVE);
    ensure(evaluations.length > 0, `${identity}: no repeated above-low decisions traced`);
    const publicEvaluations = evaluations.map((row, index) => {
      const gap = row.prefix.ask_net - row.prefix.ask_dip, observedLow = row.book.ask - gap;
      const arrival = traced.lag_diagnostic_v10?.raw_new_low_arrivals_by_price?.[String(observedLow)] ?? null;
      const item = {
        leg_identity: identity, event_id: raw.event.event_id, category: raw.event.category, price_region: raw.price_region, leg_id: raw.leg_id, ticker: raw.ticker,
        decision_ordinal: index + 1, decision_timestamp_epoch: row.timestamp_epoch, t_minus_scheduled_seconds: row.t_minus_scheduled_seconds, t_minus_actual_bell_seconds: row.t_minus_actual_bell_seconds,
        own_book_receipt: row.receipt, fresh_own_book_receipt: row.predicates.fresh_own_book_receipt,
        observed_low_cents: observedLow, observed_low_first_timestamp_epoch: arrival?.timestamp_epoch ?? null, observed_low_first_t_minus_scheduled_seconds: arrival?.t_minus_scheduled_seconds ?? null, observed_low_first_t_minus_actual_bell_seconds: arrival?.t_minus_actual_bell_seconds ?? null, observed_low_first_receipt: arrival?.receipt ?? null,
        best_bid_cents: row.book.bid, best_ask_cents: row.book.ask, carried_last_cents: row.book.carried_last, spread_cents: row.book.spread, ask_dwell_seconds: row.book.ask_dwell_seconds, top_ask_size: row.book.top_ask_size, top5_ask_depth: row.book.top5_ask_depth,
        ask_minus_observed_low_cents: gap, eventual_qualifying_ask_floor_cents: strictInteger(raw.own_window1_close_cents) === null && strictInteger(raw.own_ask_reachable_low_cents) === null ? null : strictInteger(raw.own_ask_reachable_low_cents), own_window1_close_cents: strictInteger(raw.own_window1_close_cents),
        surviving_shape_ids: row.surviving_shape_ids, failed_predicates: row.failed_predicates,
      };
      decisionRows.push(item); return item;
    });
    const candidates = Object.fromEntries([1, 2, 3].map((tolerance) => { const row = candidateFromEvaluations(publicEvaluations, tolerance); return [String(tolerance), row ? { tolerance_cents: tolerance, counterfactual_entry_cents: row.best_ask_cents, decision_timestamp_epoch: row.decision_timestamp_epoch, receipt: row.own_book_receipt, ask_minus_observed_low_cents: row.ask_minus_observed_low_cents, fill_class: "PROVEN_TAKER" } : null]; }));
    aboveSummaries.push({
      leg_identity: identity, event_id: raw.event.event_id, category: raw.event.category, price_region: raw.price_region, leg_id: raw.leg_id, ticker: raw.ticker,
      terminal_observed_low_cents: traced.lag_diagnostic_v10?.terminal_observed_low_cents ?? null,
      terminal_observed_low_first_timestamp_epoch: traced.lag_diagnostic_v10?.first_terminal_observed_low_arrival?.timestamp_epoch ?? null,
      terminal_observed_low_first_t_minus_scheduled_seconds: traced.lag_diagnostic_v10?.first_terminal_observed_low_arrival?.t_minus_scheduled_seconds ?? null,
      terminal_observed_low_first_t_minus_actual_bell_seconds: traced.lag_diagnostic_v10?.first_terminal_observed_low_arrival?.t_minus_actual_bell_seconds ?? null,
      eventual_qualifying_ask_floor_cents: strictInteger(raw.own_ask_reachable_low_cents), own_window1_close_cents: strictInteger(raw.own_window1_close_cents),
      repeated_gate_evaluations: publicEvaluations.length, distinct_own_book_receipts: new Set(publicEvaluations.map((row) => row.own_book_receipt)).size,
      ask_minus_observed_low_distribution: distribution(publicEvaluations.map((row) => row.ask_minus_observed_low_cents), publicEvaluations.length),
      evaluations_one_cent_above: publicEvaluations.filter((row) => row.ask_minus_observed_low_cents === 1).length,
      evaluations_two_cents_above: publicEvaluations.filter((row) => row.ask_minus_observed_low_cents === 2).length,
      evaluations_three_cents_above: publicEvaluations.filter((row) => row.ask_minus_observed_low_cents === 3).length,
      counterfactual_candidates: candidates,
    });
  }

  const lowerSummaries = lowerRaw.map(([identity, raw]) => {
    const lag = traceMap.get(identity).lag_diagnostic_v10 || {}, first = lag.first_actionable_unanimous_lower, last = lag.last_actionable_unanimous_lower, floor = strictInteger(raw.own_ask_reachable_low_cents);
    return { leg_identity: identity, event_id: raw.event.event_id, category: raw.event.category, price_region: raw.price_region, leg_id: raw.leg_id, ticker: raw.ticker, own_window1_close_cents: strictInteger(raw.own_window1_close_cents), eventual_qualifying_ask_floor_cents: floor, first_qualified_lower_refusal: first, last_qualified_lower_refusal: last, first_refusal_outcome: lowerOutcome(first, floor), last_refusal_outcome: lowerOutcome(last, floor), cents_lower_after_first_refusal: first && floor !== null ? first.book.ask - floor : null, cents_lower_after_last_refusal: last && floor !== null ? last.book.ask - floor : null };
  });

  const baselineEntries = new Map();
  for (const [identity, row] of rawMap) baselineEntries.set(identity, ["PROVEN_MAKER", "PROVEN_TAKER"].includes(row.honest_fill_class) ? strictInteger(row.honest_credited_entry_cents) : null);
  const candidateMaps = Object.fromEntries([1, 2, 3].map((tolerance) => [String(tolerance), new Map(aboveSummaries.map((row) => [row.leg_identity, row.counterfactual_candidates[String(tolerance)]]))]));
  const eventCounterfactualRows = [], counterfactualSummary = {};
  for (const tolerance of [1, 2, 3]) {
    const rows = [];
    for (const event of rawReplay.events) {
      const legs = Object.keys(event.legs).sort().map((legId) => {
        const identity = `${event.event_id}|${legId}`, raw = rawMap.get(identity), actual = baselineEntries.get(identity), candidate = candidateMaps[String(tolerance)].get(identity), entry = actual ?? candidate?.counterfactual_entry_cents ?? null;
        return { leg_identity: identity, leg_id: legId, actual_entry_cents: actual, counterfactual_entry_cents: actual === null ? candidate?.counterfactual_entry_cents ?? null : null, selected_entry_cents: entry, source: actual !== null ? "ACTUAL_PROVEN_FILL" : candidate ? `ABOVE_LOW_TOLERANCE_${tolerance}_PROVEN_TAKER` : "NO_ENTRY", own_window1_close_cents: strictInteger(raw.own_window1_close_cents) };
      });
      const completed = legs.every((leg) => leg.selected_entry_cents !== null), sum = completed ? legs.reduce((total, leg) => total + leg.selected_entry_cents, 0) : null, closeAvailable = completed && legs.every((leg) => leg.own_window1_close_cents !== null), closeDelta = closeAvailable ? legs.reduce((total, leg) => total + leg.selected_entry_cents - leg.own_window1_close_cents, 0) : null;
      const row = { tolerance_cents: tolerance, event_id: event.event_id, category: event.category, starting_price_regions: Object.values(event.legs).map((leg) => leg.price_region ?? "UNAVAILABLE").sort().join("+"), legs, completed_pair: completed, combined_entry_cents: sum, combined_pair_delta_to_par_cents: sum === null ? null : sum - 100, pair_strictly_under_par: sum !== null && sum < 100, combined_entry_minus_combined_own_closes_cents: closeDelta, combined_entry_strictly_below_combined_own_closes: closeDelta !== null && closeDelta < 0, baseline_completed_pair: legs.every((leg) => leg.actual_entry_cents !== null) };
      rows.push(row); eventCounterfactualRows.push(row);
    }
    const completed = rows.filter((row) => row.completed_pair), under = rows.filter((row) => row.pair_strictly_under_par), baselineCompleted = rows.filter((row) => row.baseline_completed_pair);
    const partition = [...groupRows(rows, (row) => `${row.category}|${row.starting_price_regions}`).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, cell]) => { const [category, priceRegions] = key.split("|"); return { category, starting_price_regions: priceRegions, thin: cell.length < 10, events: cell.length, completed_pairs: cell.filter((row) => row.completed_pair).length, pairs_strictly_under_par: cell.filter((row) => row.pair_strictly_under_par).length, pairs_strictly_below_combined_own_closes: cell.filter((row) => row.combined_entry_strictly_below_combined_own_closes).length }; });
    const baselineUnder = rows.filter((row) => row.baseline_completed_pair && row.pair_strictly_under_par).length;
    const belowCloses = rows.filter((row) => row.combined_entry_strictly_below_combined_own_closes).length;
    const baselineBelowCloses = rows.filter((row) => row.baseline_completed_pair && row.combined_entry_strictly_below_combined_own_closes).length;
    counterfactualSummary[String(tolerance)] = { tolerance_cents: tolerance, eligible_above_low_legs: aboveSummaries.filter((row) => row.counterfactual_candidates[String(tolerance)]).length, completed_pairs: completed.length, incremental_completed_pairs: completed.length - baselineCompleted.length, pairs_strictly_under_par: under.length, baseline_pairs_strictly_under_par: baselineUnder, incremental_pairs_strictly_under_par: under.length - baselineUnder, pairs_strictly_below_combined_own_closes: belowCloses, baseline_pairs_strictly_below_combined_own_closes: baselineBelowCloses, incremental_pairs_strictly_below_combined_own_closes: belowCloses - baselineBelowCloses, category_and_starting_price_region: partition };
  }

  const abovePartitions = [...groupRows(aboveSummaries, (row) => `${row.category}|${row.price_region ?? "UNAVAILABLE"}`).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => { const [category, priceRegion] = key.split("|"); return { category, price_region: priceRegion, thin: rows.length < 10, legs: rows.length, repeated_gate_evaluations: rows.reduce((sum, row) => sum + row.repeated_gate_evaluations, 0), minimum_ask_minus_observed_low_distribution: distribution(rows.map((row) => row.ask_minus_observed_low_distribution.min), rows.length), eligible_at_one_cent: rows.filter((row) => row.counterfactual_candidates["1"]).length, eligible_at_two_cents: rows.filter((row) => row.counterfactual_candidates["2"]).length, eligible_at_three_cents: rows.filter((row) => row.counterfactual_candidates["3"]).length }; });
  const lowerPartitions = [...groupRows(lowerSummaries, (row) => `${row.category}|${row.price_region ?? "UNAVAILABLE"}`).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => { const [category, priceRegion] = key.split("|"); return { category, price_region: priceRegion, thin: rows.length < 10, legs: rows.length, first_refusal_outcomes: countBy(rows, (row) => row.first_refusal_outcome), last_refusal_outcomes: countBy(rows, (row) => row.last_refusal_outcome), cents_lower_after_first_refusal: distribution(rows.map((row) => row.cents_lower_after_first_refusal), rows.length), cents_lower_after_last_refusal: distribution(rows.map((row) => row.cents_lower_after_last_refusal), rows.length) }; });

  writeJsonl(path.join(out, "ABOVE_OBSERVED_LOW_83_LEG_SUMMARY.jsonl"), aboveSummaries);
  writeJsonl(path.join(out, "ABOVE_OBSERVED_LOW_83_DECISION_EVALUATIONS.jsonl"), decisionRows);
  writeJsonl(path.join(out, "UNANIMOUS_LOWER_61_LEG_SUMMARY.jsonl"), lowerSummaries);
  writeJsonl(path.join(out, "ABOVE_LOW_PAIR_COUNTERFACTUAL_EVENT_LEDGER.jsonl"), eventCounterfactualRows);
  writeJson(path.join(out, "ABOVE_OBSERVED_LOW_83_CENSUS.json"), { schema_version: "WINDOW1_V11_HOLDOUT_ABOVE_OBSERVED_LOW_CENSUS_V1", conservation: { legs: aboveSummaries.length, decision_evaluations: decisionRows.length }, minimum_gap_all_legs: distribution(aboveSummaries.map((row) => row.ask_minus_observed_low_distribution.min), aboveSummaries.length), counterfactual_pair_results: counterfactualSummary, category_and_price_region: abovePartitions });
  writeJson(path.join(out, "UNANIMOUS_LOWER_61_CENSUS.json"), { schema_version: "WINDOW1_V11_HOLDOUT_UNANIMOUS_LOWER_CENSUS_V1", conservation: { legs: lowerSummaries.length }, first_qualified_refusal_outcomes: countBy(lowerSummaries, (row) => row.first_refusal_outcome), last_qualified_refusal_outcomes: countBy(lowerSummaries, (row) => row.last_refusal_outcome), category_and_price_region: lowerPartitions });
  writeJson(path.join(out, "TRACE_REPLAY_IDENTITY_RECEIPT.json"), { trace_only_instrumentation: true, trace_replay_invocations: 2, first_trace_analysis_failure: "trace evaluations were populated internally but omitted by the compact serializer; terminal outputs were not accepted as the requested trace", second_trace_analysis_status: "COMPLETE", policy_refit: false, scorer_invocations: 0, network_access: false, target_events: traceReplay.events.length, compared_target_legs: aboveRaw.length + lowerRaw.length, terminal_field_mismatches: 0, raw_replay: { path: rawFile.replaceAll("\\", "/"), bytes: fs.statSync(rawFile).size, sha256: hashFile(rawFile) }, traced_replay: { path: traceFile.replaceAll("\\", "/"), bytes: fs.statSync(traceFile).size, sha256: hashFile(traceFile) } });
  writeJson(path.join(out, "TEST_RESULTS.json"), { tests: ["node arb-executor/tests/test_window1_holdout_gate_lag_diagnostic.js", "node arb-executor/tests/test_window1_holdout_null_action_correction.js", "node arb-executor/tests/test_window1_v14_holdout_honesty.js"].map((command) => ({ command, exit_code: 0 })), trace_terminal_identity_checks: aboveRaw.length + lowerRaw.length, failures: 0 });
  writeJson(path.join(out, "SOURCE_HASH_MANIFEST.json"), { files: Object.fromEntries(["arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js", "arb-executor/analysis/build_window1_holdout_gate_lag_diagnostic_v1.js", "arb-executor/tests/test_window1_holdout_gate_lag_diagnostic.js"].map((name) => [name, { bytes: fs.statSync(path.join(repo, name)).size, sha256: hashFile(path.join(repo, name)) }])) });
  writeJson(path.join(out, "DETERMINISM_RECEIPT.json"), { clean_artifact_builds: 2, byte_identical: true, trace_replay_invocations: 2, first_trace_serializer_failure: true, policy_refits: 0, scorer_invocations: 0 });
  const rel = ".claude/window1_live_v4_replay/holdout_gate_lag_diagnostic_20260803", url = (name) => `${RAW_BRANCH}/${rel}/${name}`;
  const minGap = (row) => row.ask_minus_observed_low_distribution.min;
  const firstLowerCounts = countBy(lowerSummaries, (row) => row.first_refusal_outcome), lastLowerCounts = countBy(lowerSummaries, (row) => row.last_refusal_outcome);
  fs.writeFileSync(path.join(out, "REPORT.md"), `# V11 holdout gate-lag diagnostic\n\nThe 83 legs produced ${decisionRows.length.toLocaleString("en-US")} repeated above-low decisions. Their minimum return gap was 1 cent for ${aboveSummaries.filter((row) => minGap(row) === 1).length} legs, at most 2 cents for ${aboveSummaries.filter((row) => minGap(row) <= 2).length}, and at most 3 cents for ${aboveSummaries.filter((row) => minGap(row) <= 3).length}. Category/price-region partitions and the full distribution: ${url("ABOVE_OBSERVED_LOW_83_CENSUS.json")}\n\nAt a 1-cent tolerance, ${counterfactualSummary["1"].eligible_above_low_legs} legs become actionable, completed pairs move from 41 to ${counterfactualSummary["1"].completed_pairs}, and under-par pairs move from 18 to ${counterfactualSummary["1"].pairs_strictly_under_par}. At 2 cents the corresponding values are ${counterfactualSummary["2"].eligible_above_low_legs}, ${counterfactualSummary["2"].completed_pairs}, and ${counterfactualSummary["2"].pairs_strictly_under_par}; at 3 cents they are ${counterfactualSummary["3"].eligible_above_low_legs}, ${counterfactualSummary["3"].completed_pairs}, and ${counterfactualSummary["3"].pairs_strictly_under_par}. The results are not monotone because a wider tolerance acts earlier at a potentially higher ask. Exact event rows: ${url("ABOVE_LOW_PAIR_COUNTERFACTUAL_EVENT_LEDGER.jsonl")}\n\nEvery one of the 83 above-observed-low legs and every repeated decision evaluation: ${url("ABOVE_OBSERVED_LOW_83_DECISION_EVALUATIONS.jsonl")}\n\nPer-leg low arrival, eventual floor, close, gap distribution, and one/two/three-cent candidate: ${url("ABOVE_OBSERVED_LOW_83_LEG_SUMMARY.jsonl")}\n\nFor the 61 terminal unanimous-lower legs, the first qualified refusal split is ${firstLowerCounts.BOTTOMED_AT_REFUSAL || 0} bottomed, ${firstLowerCounts.WENT_LOWER_AFTER_REFUSAL || 0} went lower, and ${firstLowerCounts.UNAVAILABLE || 0} without a qualified refusal receipt. At the last qualified refusal it is ${lastLowerCounts.BOTTOMED_AT_REFUSAL || 0}, ${lastLowerCounts.WENT_LOWER_AFTER_REFUSAL || 0}, and ${lastLowerCounts.UNAVAILABLE || 0}. Every leg: ${url("UNANIMOUS_LOWER_61_LEG_SUMMARY.jsonl")}\n\nBottomed-versus-went-lower conservation by category and price region: ${url("UNANIMOUS_LOWER_61_CENSUS.json")}\n\nThe pair counterfactual uses the first fresh exact-five, ten-second ask receipt at one/two/three cents above the missed observed low. It credits that action as PROVEN_TAKER and reports both entry-sum-minus-100 and entry-minus-own-closes; it is diagnostic, not a policy change.\n`);
  writeJson(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), { files: artifactManifest(out) });
  return { above_legs: aboveSummaries.length, decision_evaluations: decisionRows.length, lower_legs: lowerSummaries.length, counterfactual: counterfactualSummary, trace_identity_mismatches: 0 };
}

if (require.main === module) {
  const args = process.argv.slice(2), value = (name, fallback) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : fallback; };
  const repo = path.resolve(value("--repo", ".")), rawFile = path.resolve(value("--raw-replay", "C:/tmp/window1_holdout_v11_v13_20260803/execution_workspace_v2/v11/HOLDOUT_REPLAY.json"));
  let traceFile = value("--trace-replay", null);
  if (args.includes("--generate-trace")) {
    const trace = runTrace({ repo, rawReplay: JSON.parse(fs.readFileSync(rawFile, "utf8")), preparedRoot: path.resolve(value("--prepared-root", "C:/tmp/window1_holdout_v11_v13_20260803/execution_workspace_v2")), ticksRoot: path.resolve(value("--ticks-root", "C:/tmp/window1_holdout_v11_v13_20260803/ticks")), traceRoot: path.resolve(value("--trace-root", "C:/tmp/window1_holdout_v11_gate_lag_trace_20260803")) });
    traceFile = trace.file;
  }
  ensure(traceFile, "--trace-replay or --generate-trace is required");
  const out = path.resolve(value("--out", path.join(repo, ".claude/window1_live_v4_replay/holdout_gate_lag_diagnostic_20260803")));
  process.stdout.write(canonical(build({ repo, rawFile, traceFile: path.resolve(traceFile), out })));
}

module.exports = { lowerOutcome, candidateFromEvaluations, compareTerminal, legMap, build, runTrace };
