#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { FEATURE_NAMES, fitExpectedCloseModel, predictExpectedClose } = require("../analysis/window1_expected_close_distribution_v1.js");

const repo = path.resolve(__dirname, "../.."), out = path.join(repo, ".claude/window1_live_v4_replay/expected_close_binding_20260801");
const read = (name) => JSON.parse(fs.readFileSync(path.join(out, name), "utf8"));
let assertions = 0; function check(value, message) { assertions += 1; assert.ok(value, message); }

function synthetic(identity, ts, ask, close, shift = 0) {
  const features = Object.fromEntries(FEATURE_NAMES.map((name, index) => [name, index + shift]));
  return { event_id: identity.split("|")[0], leg_identity: identity, category: "ATP_CHALL", price_region: "26_50", ts, ask_cents: ask, close_cents: close, surviving_shapes: ["QUOTE_DOWN"], features };
}

const training = [synthetic("A|L", 1, 40, 45), synthetic("A|L", 2, 41, 46, 0.1), synthetic("B|L", 1, 40, 38, 2)];
const model = fitExpectedCloseModel(training), query = synthetic("Q|L", 3, 42, 44, 0.05), prediction = predictExpectedClose(model, query);
check(prediction.status === "DISTRIBUTION_AVAILABLE_UNVALIDATED", "synthetic distribution unavailable");
check(prediction.independent_training_legs === 2, "repeated ticks inflated independent support");
check(prediction.close_quantiles_cents["0.5"] !== null, "median missing");
assert.throws(() => fitExpectedCloseModel([{ ...synthetic("C|L", 1, 40, 42), features: { ...synthetic("C|L", 1, 40, 42).features, bid: NaN } }]), /non-finite/); assertions += 1;

const binding = read("CONTROL_BINDING.json"), calibration = read("POSTFIT_CALIBRATION.json"), external = read("EXTERNAL_BOOK_COVERAGE.json"), decisions = read("DECISION_UNLOCK_RECEIPT.json"), sources = read("SOURCE_HASH_MANIFEST.json"), artifacts = read("ARTIFACT_HASH_MANIFEST.json");
check(binding.status === "NOT_BOUND", "model was improperly bound");
check(binding.permitted_use === "DESCRIPTIVE_POSTFIT_CALIBRATION_ONLY", "permitted use widened");
check(binding.comparison_to_current_ask_baseline.cells_better === 0, "unexpected hidden improvement claim");
check(binding.comparison_to_current_ask_baseline.cells_total === 16, "cell conservation failed");
check(binding.comparison_to_current_ask_baseline.predicted_edge_ge15_rows === 0, "GE15 claim mismatch");
check(calibration.fit.events === 525 && calibration.fit.legs === 1050, "fit split mismatch");
check(calibration.postfit.events === 279 && calibration.postfit.legs === 558, "post-fit split mismatch");
check(calibration.fit.labeled_legs === 854 && calibration.postfit.labeled_legs === 449, "labeled-leg conservation mismatch");
check(calibration.conservation.close_unavailable_legs === 301, "missing-close count mismatch");
check(calibration.conservation.predictions === 2902, "prediction count mismatch");
check(calibration.by_category_and_price_region.length === 16, "category/region cells missing");
check(calibration.thin_cells.length === 10, "thin-cell census mismatch");
check(calibration.comparison_to_current_ask_baseline.cells_equal === 16, "baseline comparison mismatch");
check(!Object.prototype.hasOwnProperty.call(calibration, "pooled_performance"), "flattened performance emitted");
check(external.summary.fresh_legs === 0 && external.summary.population_legs === 1608, "external coverage mismatch");
check(external.summary.predictive_comparison === "NOT_MEASURABLE_ZERO_FRESH_EXTERNAL_READS", "external comparison fabricated");
check(external.by_category_and_starting_price_region.every((row) => row.fresh_external_read_legs === 0), "fresh external row fabricated");
check(decisions.fee_aware_take.causal_516_clear_count === null, "unbound fee count populated");
check(decisions.commitment.threshold === null, "commitment threshold invented");
check(decisions.policy_runs.five_games === false && decisions.policy_runs.population_804 === false && decisions.policy_runs.scorer_invocations === 0, "policy/scorer run occurred");
check(decisions.policy_runs.performance_metrics === null, "performance field populated");
check(Object.keys(sources.private_tick_files).length === 1608, "tick source census mismatch");
check(Object.keys(sources.private_guarded_cache_v3).length === 804, "cache source census mismatch");
const predictions = zlib.gunzipSync(fs.readFileSync(path.join(out, "POSTFIT_PREDICTIONS.jsonl.gz"))).toString("utf8").trim().split(/\r?\n/).map(JSON.parse);
check(predictions.length === 2902, "prediction ledger mismatch");
check(predictions.every((row) => row.scheduled_t_minus_seconds !== null && row.own_book_receipt && Array.isArray(row.surviving_shapes)), "causal provenance incomplete");
for (const [name, receipt] of Object.entries(artifacts.artifacts)) { const file = path.join(out, name); check(fs.existsSync(file), `missing artifact ${name}`); check(fs.statSync(file).size === receipt.bytes, `artifact size mismatch ${name}`); }
const builder = fs.readFileSync(path.join(repo, "arb-executor/analysis/build_window1_expected_close_binding_v1.js"), "utf8");
check(!/require\([^)]*(scorer|scoring_runner)|from\s+["'][^"']*(scorer|scoring_runner)/i.test(builder), "scorer imported");
check(!/execute mode|--mode execute/i.test(builder), "execute path referenced");
check(!fs.existsSync(path.join(out, "RESULTS.json")), "results artifact exists");

process.stdout.write(`${JSON.stringify({ status: "PASS", assertions, fit_labeled_legs: 854, postfit_labeled_legs: 449, thin_cells: 10, external_fresh_legs: 0 })}\n`);
