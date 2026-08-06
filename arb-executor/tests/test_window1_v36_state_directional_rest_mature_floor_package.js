"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const ROOT = path.resolve(__dirname, "..", "..");
const OUT = path.join(ROOT, ".claude/window1_live_v4_replay/v36_state_directional_rest_mature_floor_20260806");
const read = (name) => JSON.parse(fs.readFileSync(path.join(OUT, name), "utf8"));
const rows = (name) => zlib.gunzipSync(fs.readFileSync(path.join(OUT, name))).toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
const sha = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

const control = read("CONTROL_BINDING.json");
const score = read("SCORECARD_TWO_COLUMN.json");
const edge = read("HARD_RIGHT_EDGE_RECEIPT.json");
const rest = read("REST_SANITY.json");
const adverse = read("ADVERSE_TAIL_BY_FILL_STATE.json");
const bleed = read("BLEED_CENSUS_DELTA.json");
const named = read("NAMED_REGRESSION_RECEIPT.json");
const acceptance = read("ACCEPTANCE_RECEIPT.json");
const close = read("CLOSE_TELEMETRY_ISOLATION_RECEIPT.json");
const forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
const determinism = read("DETERMINISM_RECEIPT.json");
const source = read("SOURCE_HASH_MANIFEST.json");

assert.strictEqual(control.machine.V35_baseline_commit, "0799fba887f1d1e84f9c0ef3e73096fd9d76019e");
assert.strictEqual(control.machine.V32_lineage_commit, "a3429cad6719f96a25a900812e0f360b71a5607e");
assert.deepStrictEqual(control.machine.clock_decision_inputs, []);
assert.strictEqual(score.STRICT_LAW.aggregate.D, 804);
assert.strictEqual(score.CENSUS_PRICED.aggregate.D, 804);
assert.strictEqual(score.STRICT_LAW.aggregate.close_based_grade, null);
assert.strictEqual(score.CENSUS_PRICED.aggregate.close_based_grade, null);
assert.strictEqual(edge.post_edge_action_or_fill_or_cap_arm_rows, 0);
assert.strictEqual(edge.post_edge_state_update_rows, 0);
assert.strictEqual(rest.STRICT_LAW.aggregate.non_exact_target_receipts, 0);
assert.strictEqual(rest.CENSUS_PRICED.aggregate.non_exact_target_receipts, 0);
assert.strictEqual(rest.STRICT_LAW.aggregate.max_abs_gap_cents, 0);
assert.strictEqual(adverse.STRICT_LAW.conservation.pass, true);
assert.strictEqual(adverse.CENSUS_PRICED.conservation.pass, true);
assert.strictEqual(bleed.STRICT_LAW.conservation.pass, true);
assert.strictEqual(bleed.CENSUS_PRICED.conservation.pass, true);
assert.strictEqual(Object.keys(named.checks).length, 7);
assert.strictEqual(typeof acceptance.status, "string");
assert.strictEqual(acceptance.required_floor.strict_completed_pairs, 264);
assert.deepStrictEqual(acceptance.required_floor.strict_frontier, { LE_93: 23, LE_95: 34, LE_97: 68 });
assert.strictEqual(close.strict_invariant, true);
assert.strictEqual(close.census_invariant, true);
assert.strictEqual(forbidden.holdout_accesses, 0);
assert.strictEqual(forbidden.live_accesses, 0);
assert.strictEqual(forbidden.network_runtime_accesses, 0);
assert.strictEqual(rows("STRICT_EVENT_LEDGER.jsonl.gz").length, 804);
assert.strictEqual(rows("CENSUS_PRICED_EVENT_LEDGER.jsonl.gz").length, 804);
assert.strictEqual(determinism.builds, 2);
assert.strictEqual(determinism.byte_identical, true);

for (const rel of [
  "arb-executor/analysis/window1_v36_state_directional_rest_mature_floor.js",
  "arb-executor/analysis/build_window1_v36_state_directional_rest_mature_floor.js",
  "arb-executor/tests/test_window1_v36_state_directional_rest_mature_floor.js",
  "arb-executor/tests/test_window1_v36_state_directional_rest_mature_floor_package.js",
]) {
  assert.strictEqual(source.public_committed[rel].sha256, sha(path.join(ROOT, rel)), `source hash ${rel}`);
}

console.log("PASS test_window1_v36_state_directional_rest_mature_floor_package");
