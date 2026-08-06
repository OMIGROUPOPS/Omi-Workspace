"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const ROOT = path.resolve(__dirname, "..", "..");
const OUT = path.join(ROOT, ".claude/window1_live_v4_replay/v37_floor_arithmetic_take_bound_20260806");
const read = (name) => JSON.parse(fs.readFileSync(path.join(OUT, name), "utf8"));
const rows = (name) => zlib.gunzipSync(fs.readFileSync(path.join(OUT, name))).toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
const sha = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

const control = read("CONTROL_BINDING.json");
const score = read("SCORECARD_TWO_COLUMN.json");
const hygiene = read("CLEAN_DEEP_HYGIENE_CENSUS.json");
const bound = read("FLOOR_ARITHMETIC_TAKE_BOUND_RECEIPT.json");
const differential = read("DIFFERENTIAL_VS_V36.json");
const rest = read("REST_SANITY.json");
const adverse = read("ADVERSE_TAIL_BY_FILL_STATE.json");
const named = read("NAMED_REGRESSION_RECEIPT.json");
const contradiction = read("CAUSAL_TRIPWIRE_CONTRADICTION_RECEIPT.json");
const acceptance = read("ACCEPTANCE_RECEIPT.json");
const forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
const determinism = read("DETERMINISM_RECEIPT.json");
const source = read("SOURCE_HASH_MANIFEST.json");

assert.strictEqual(control.machine.V36_baseline_commit, "bfde0d8d1135f5c5f48a5f3d619ab30050efab83");
assert.strictEqual(control.repair.fitted_parameters, 0);
assert.strictEqual(control.repair.formula, "other_under_par_budget = 100 - entry; TAKE iff other_under_par_budget > other_running_print_backed_floor");
assert.strictEqual(score.STRICT_LAW.aggregate.D, 804);
assert.strictEqual(score.CENSUS_PRICED.aggregate.D, 804);
assert.strictEqual(score.STRICT_LAW.aggregate.close_based_grade, null);
assert.strictEqual(score.CENSUS_PRICED.aggregate.close_based_grade, null);
assert.deepStrictEqual(score.comparison_floor.clean_deep_ruler, { definition: "EXACT_BELL_AND_COLLAPSE_CLEAN_COMPLETED_PAIR_LE95", V34: 9, V35: 5, V36: 7 });
assert.strictEqual(hygiene.source.commit, "03bac97b12777d751fbb334fa6ae0f605445498a");
assert.strictEqual(hygiene.baseline.V36.exact_and_clean, 7);
assert.strictEqual(bound.fitted_parameters, 0);
assert.strictEqual(bound.conservation.pass, true);
assert.strictEqual(rows("FLOOR_ARITHMETIC_TAKE_BOUND_LEDGER.jsonl.gz").length, bound.decisions);
assert.strictEqual(differential.conservation.pass, true);
assert.strictEqual(differential.conservation.strict_rows, 1608);
assert.strictEqual(differential.conservation.census_rows, 1608);
assert.strictEqual(rest.STRICT_LAW.aggregate.non_exact_target_receipts, 0);
assert.strictEqual(rest.STRICT_LAW.aggregate.max_abs_gap_cents, 0);
assert.strictEqual(adverse.STRICT_LAW.conservation.pass, true);
assert.strictEqual(named.checks.ARNROM_38_plus_56_equals_94, false);
assert.strictEqual(named.checks.KRALOR_LOR_keeps_5, true);
assert.strictEqual(named.checks.BOSCOP_BOS_keeps_32, true);
assert.strictEqual(acceptance.status, "REJECTED_V37_BAR_V36_REMAINS_OPERATIVE");
assert.strictEqual(acceptance.observed.strict_completed_pairs, 242);
assert.strictEqual(acceptance.observed.strict_exact_bell_collapse_clean_LE95, 5);
assert.strictEqual(contradiction.status, "SPECIFICATION_TRIPWIRE_CONFLICTS_WITH_DECISION_TIME_FLOOR_LAW");
assert.deepStrictEqual(contradiction.ARNROM.decision_time_ROM_floor_sequence_cents, [49, 45]);
assert.deepStrictEqual(contradiction.ARNROM.decision_time_comparisons, ["44 > 49", "44 > 45"]);
assert.strictEqual(contradiction.ARNROM.eventual_ROM_38_seconds_after_first_ARN_56_decision, 40304);
assert.strictEqual(contradiction.ARNROM.future_leakage_required_to_use_38_at_ARN_56, true);
assert.strictEqual(contradiction.GANJAN.decision_time_GAN_floor.cents, null);
assert.strictEqual(contradiction.GANJAN.future_leakage_required_to_use_18_at_JAN_79, true);
assert.strictEqual(acceptance.required_floor.strict_completed_pairs, 270);
assert.strictEqual(acceptance.required_floor.strict_exact_bell_collapse_clean_LE95, 7);
assert.strictEqual(forbidden.holdout_accesses, 0);
assert.strictEqual(forbidden.live_accesses, 0);
assert.strictEqual(forbidden.network_runtime_accesses, 0);
assert.strictEqual(rows("STRICT_EVENT_LEDGER.jsonl.gz").length, 804);
assert.strictEqual(rows("CENSUS_PRICED_EVENT_LEDGER.jsonl.gz").length, 804);
assert.strictEqual(determinism.builds, 2);
assert.strictEqual(determinism.byte_identical, true);

for (const rel of [
  "arb-executor/analysis/window1_v37_floor_arithmetic_take_bound.js",
  "arb-executor/analysis/build_window1_v37_floor_arithmetic_take_bound.js",
  "arb-executor/tests/test_window1_v37_floor_arithmetic_take_bound.js",
  "arb-executor/tests/test_window1_v37_floor_arithmetic_take_bound_package.js",
]) {
  assert.strictEqual(source.public_committed[rel].sha256, sha(path.join(ROOT, rel)), `source hash ${rel}`);
}

console.log("PASS test_window1_v37_floor_arithmetic_take_bound_package");
