#!/usr/bin/env node
"use strict";

const assert = require("assert");
const policy = require("../analysis/window1_v52q_anchor_correction.js");

let assertions = 0;
const equal = (actual, expected, message) => { assertions += 1; assert.deepStrictEqual(actual, expected, message); };
const check = (value, message) => { assertions += 1; assert(value, message); };
const families = policy.FAMILY_ORDER;
const categories = ["ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL"];
const rows = families.flatMap((family) => categories.map((category) => ({ family, category, legs: family.endsWith("_DOWN") ? 10 : 30, depth_below_open_c: { med: family.endsWith("_DOWN") ? 8 : 2 }, floor_pos: { med: 0.5 }, early_call: { kind: family.endsWith("_DOWN") || family.endsWith("_UP") ? "DIRECTIONAL" : "STILL", median_declare_f: 0.25 } })));
policy.configureShapeLibrary({
  taxonomy: { LABEL: "SHAPE_TAXONOMY_BUILD1", families: Object.fromEntries(families.map((family) => [family, 1])), benchmark: { classifier: "early-window drift alone: last in-span print before the receipt minus post-formation open; >=+2c CLIMBER, <=-2c FALLER, else ABSTAIN", by_family_acc: Object.fromEntries(families.map((family) => [family, "95%"])) } },
  floor_tables: { LABEL: "PER_SHAPE_FLOOR_DEPTH_TABLES", rows },
  taxonomy_provenance: { commit: policy.BENCHMARK_ROLE_RULE_COMMIT, sha256: "a".repeat(64) },
  floor_table_provenance: { commit: "8ab4f2d9e8c831235dc7cb4570c88daa3caded50", sha256: "b".repeat(64) },
});
policy.configureRipeness({
  artifact: { LABEL: "RECOGNITION_OPERATING_POINT_RECONCILIATION", ripeness: [
    { class: "UP_SHAPES", ripe_f: 0.023 }, { class: "DOWN_SHAPES", ripe_f: 0.448 }, { class: "STILL_SHAPES", ripe_f: 0.650 },
    { class: "WTA_MAIN", ripe_f: 0.206 }, { class: "ATP_MAIN", ripe_f: 0.351 }, { class: "ATP_CHALL", ripe_f: 0.703 }, { class: "WTA_CHALL", ripe_f: 0.964 },
  ] },
  provenance: { commit: "41c1f7244af3afa4dade63bc9824808090ada41d", sha256: "c".repeat(64) },
});
const anchor = {
  method: { name: "SPREAD_SETTLE_MID_AT_FORMATION_END", commit: policy.ANCHOR_METHOD_COMMIT, path: "METHOD.json", sha256: "d".repeat(64), literal: "first mid with spread<=10c holding <=20c for 30min" },
  ground_truth: { commit: policy.GROUND_TRUTH_COMMIT, sha256: "e".repeat(64) },
  discrepancy: { commit: `${policy.ANCHOR_DISCREPANCY_COMMIT}abcdef`, sha256: "f".repeat(64) },
  series_floor: "FORMATION_END_INCLUSIVE",
};
equal(policy.configureAnchorCorrection(anchor).bound, true);
equal(policy.requiredAnchorCorrection().method.name, "SPREAD_SETTLE_MID_AT_FORMATION_END");
equal(policy.benchmarkRuleReceipt().threshold_cents, 2);
equal(policy.benchmarkRuleReceipt().series_floor, "FORMATION_END_INCLUSIVE");
equal(policy.benchmarkRuleReceipt().new_constants, 0);

const state = policy.emptyShapeState();
policy.observeTruePrint(state, { kind: "PRINT", ts: 90, ordinal: 1, price: 40, receipt: "PRE_FORMATION" });
policy.observeTruePrint(state, { kind: "PRINT", ts: 110, ordinal: 2, price: 60, receipt: "POST_FIRST" });
policy.observeTruePrint(state, { kind: "PRINT", ts: 120, ordinal: 3, price: 58, receipt: "POST_LAST" });
const evaluation = { timestamp_epoch: 160, receipt: "R160", category: "ATP_MAIN", anchor_correction_enabled: true, formation_end_epoch: 100, verified_span_end_epoch: 200, scheduled_span_end_epoch: 190, published_anchor_cents: 50, published_anchor_receipt: "GROUND#LEG" };
const result = policy.classifyShapeState(state, evaluation);
equal(result.post_formation_open_cents, 50);
equal(result.last_causal_print_cents, 58);
equal(result.drift_cents, 8);
equal(result.candidate_role, "ROLE_UP");
equal(result.bound_role, "ROLE_UP");
equal(result.role, "ROLE_UP");
equal(result.true_print_count, 2);
equal(result.maximum_consumed_timestamp_epoch, 120);
equal(result.formation_end_epoch, 100);
equal(result.anchor_correction.method.sha256, "d".repeat(64));
equal(result.anchor_correction.series_floor, "FORMATION_END_INCLUSIVE");
equal(result.ripeness.effective_gate_f, 0.351);
equal(result.ripeness.verified_binding, true);
equal(result.ripeness.source.sha256, "c".repeat(64));
equal(58 - 60 <= -2 ? "ROLE_DOWN" : "NOT_DOWN", "ROLE_DOWN", "the superseded first-print anchor would flip this call");

const beforePrint = policy.classifyShapeState(state, { ...evaluation, timestamp_epoch: 105, receipt: "R105" });
equal(beforePrint.status, "ABSTAIN_NO_POST_FORMATION_TRUE_PRINT");
equal(beforePrint.true_print_count, 0);
equal(beforePrint.anchor_correction.anchor_cents, 50);
const beforeFormation = policy.classifyShapeState(state, { ...evaluation, timestamp_epoch: 99, receipt: "R99" });
equal(beforeFormation.status, "ABSTAIN_FORMATION_NOT_COMPLETE");
const absent = policy.classifyShapeState(state, { ...evaluation, published_anchor_cents: null });
equal(absent.status, "ABSTAIN_PUBLISHED_ANCHOR_UNAVAILABLE");
equal(absent.signable, false);
equal(policy.normalizedClauses({ anchor_correction: true }).anchor_correction, true);
equal(policy.normalizedClauses({ anchor_correction: true }).ripeness_role_binding, undefined);
check(policy.classifyShapeState !== policy.familyFromSignature);

process.stdout.write(`${JSON.stringify({ assertions, failures: 0, omissions: 0, deselections: 0, new_constants: 0 })}\n`);
