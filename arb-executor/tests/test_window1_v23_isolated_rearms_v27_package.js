"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const root = path.resolve(__dirname, "../../.claude/window1_live_v4_replay/v23_isolated_rearms_v27_20260804");
const read = (name) => JSON.parse(fs.readFileSync(path.join(root, name)));
const sha = (p) => crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex");
const control = read("CONTROL_SUMMARY.json");

assert.equal(control.baseline.score.D, 804);
assert.equal(control.baseline.score.legs, 1608);
assert.equal(control.baseline.score.joint_objective_pairs, 45);
assert.equal(control.stacking, false);
assert.deepEqual(control.fix1_binding_predicate_distribution, {
  FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW: 143,
  FLOOR_CONSENSUS_BUT_MICRO_MICRO_NOT_READY: 5,
  FLOOR_CONSENSUS_AWAITING_FRESH_OWN_BOOK_RECEIPT: 1,
});
assert.equal(control.fix1_anchor_stopped_legs, 149);
assert.equal(control.fix1_anchor_false_negative_legs, 131);

for (const [name, item] of Object.entries(control.variants)) {
  assert.equal(item.score.D, 804, name);
  assert.equal(item.score.legs, 1608, name);
  assert.ok(item.score.joint_objective_pairs >= 45, name);
  const trace = read(`${item.directory}/DECISION_TRACE_1608.json`);
  assert.equal(trace.rows.length, 1608, name);
  assert.equal(new Set(trace.rows.map((x) => x.leg_identity)).size, 1608, name);
  assert.equal(trace.variant, name, name);
  assert.equal(trace.conservation.one_row_per_leg, true, name);
  assert.equal(trace.rollup.layer_totals.reduce((sum, x) => sum + x.stopped_legs, 0), trace.rows.filter((x) => x.first_flag).length, name);
}

assert.equal(control.variants.FIX1_ANCHOR_RESIDUAL.score.joint_objective_pairs, 62);
assert.equal(control.variants.FIX2_CAP_REARM.score.joint_objective_pairs, 46);
assert.equal(control.variants.FIX3_VERDICT_FALSIFIABILITY.touched_legs, 145);
assert.equal(control.variants.FIX3_VERDICT_FALSIFIABILITY.score.joint_objective_pairs, 45);
assert.equal(control.variants.FIX4_ADMISSION_REASK.changed_leg_streams, 20);
assert.equal(control.variants.FIX4_ADMISSION_REASK.score.joint_objective_pairs, 45);

const verdict = read("fix3_verdict_falsifiability/REPAIR_RECEIPT.json");
const arn = verdict.receipts.filter((x) => x.source_csv_row === "NAMED_ARN_EXEMPLAR");
assert.equal(arn.length, 1);
assert.equal(arn[0].source_receipt, "KXATPCHALLENGERMATCH-26JUL12ARNROM-ARN.csv.gz#row-35593");
assert.equal(arn[0].verdict.reason, "INVERSE_SIBLING_UNRESOLVED");

const admission = read("fix4_admission_reask/REPAIR_RECEIPT.json");
const bal = admission.receipts.find((x) => x.leg_identity === "KXATPCHALLENGERMATCH-26JUL12BALPET|BAL");
assert.equal(bal.outcome, "ADMISSION_REASK_PASSED_ON_LATER_FORMED_BOOK");
assert.equal(bal.formed_book.spread, 1);

const determinism = read("DETERMINISM_RECEIPT.json");
assert.equal(determinism.clean_builds, 2);
assert.equal(determinism.byte_identical_payloads, true);
const manifest = read("ARTIFACT_HASH_MANIFEST.json");
for (const [name, expected] of Object.entries(manifest.files)) {
  const p = path.join(root, name);
  assert.equal(fs.statSync(p).size, expected.bytes, name);
  assert.equal(sha(p), expected.sha256, name);
}

process.stdout.write("test_window1_v23_isolated_rearms_v27_package: PASS\n");
