#!/usr/bin/env node
"use strict";

const assert = require("assert");
const policy = require("../analysis/window1_v52p_ripeness_gated_role_binding.js");

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

equal(policy.CLASS_GATES, { ROLE_UP: 0.023, ROLE_DOWN: 0.448, ROLE_STILL: 0.65 });
equal(policy.CATEGORY_GATES.ATP_MAIN, 0.351);
equal(policy.CATEGORY_GATES.WTA_CHALL, 0.964);
equal(policy.fraction(50, 0, 100), 0.5);
const state = policy.emptyShapeState();
policy.observeTruePrint(state, { kind: "PRINT", ts: 10, ordinal: 1, price: 50, receipt: "P0" });
policy.observeTruePrint(state, { kind: "PRINT", ts: 20, ordinal: 2, price: 47, receipt: "P1" });
let role = policy.classifyShapeState(state, { timestamp_epoch: 30, receipt: "R1", category: "ATP_MAIN", role_instrument_enabled: true, ripeness_role_binding_enabled: true, formation_end_epoch: 0, verified_span_end_epoch: 100, scheduled_span_end_epoch: 80 });
equal(role.candidate_role, "ROLE_DOWN");
equal(role.bound_role, null);
equal(role.role, "ABSTAIN");
equal(role.ripeness.effective_gate_f, 0.448);
equal(role.ripeness.verified_binding, false);
equal(role.ripeness.scheduled_proxy_binding, false);
role = policy.classifyShapeState(state, { timestamp_epoch: 40, receipt: "R2", category: "ATP_MAIN", role_instrument_enabled: true, ripeness_role_binding_enabled: true, formation_end_epoch: 0, verified_span_end_epoch: 100, scheduled_span_end_epoch: 80 });
equal(role.bound_role, null);
equal(role.ripeness.verified_binding, false);
equal(role.ripeness.scheduled_proxy_binding, true);
equal(role.ripeness.binding_decision_diverges, true);
role = policy.classifyShapeState(state, { timestamp_epoch: 50, receipt: "R3", category: "ATP_MAIN", role_instrument_enabled: true, ripeness_role_binding_enabled: true, formation_end_epoch: 0, verified_span_end_epoch: 100, scheduled_span_end_epoch: 80 });
equal(role.bound_role, "ROLE_DOWN");
equal(role.role, "ROLE_DOWN");
equal(role.signable, true);
equal(role.ripeness.source.sha256, "c".repeat(64));

const stillState = policy.emptyShapeState();
policy.observeTruePrint(stillState, { kind: "PRINT", ts: 1, ordinal: 1, price: 50, receipt: "S0" });
let still = policy.classifyShapeState(stillState, { timestamp_epoch: 64, receipt: "S1", category: "ATP_MAIN", role_instrument_enabled: true, ripeness_role_binding_enabled: true, formation_end_epoch: 0, verified_span_end_epoch: 100, scheduled_span_end_epoch: 100 });
equal(still.candidate_role, "ROLE_STILL");
equal(still.bound_role, null);
still = policy.classifyShapeState(stillState, { timestamp_epoch: 66, receipt: "S2", category: "ATP_MAIN", role_instrument_enabled: true, ripeness_role_binding_enabled: true, formation_end_epoch: 0, verified_span_end_epoch: 100, scheduled_span_end_epoch: 100 });
equal(still.bound_role, "ROLE_STILL");
equal(still.role, "ABSTAIN");
equal(still.signable, true);
equal(policy.normalizedClauses({ ripeness_role_binding: true }).benchmarked_role_instrument, true);
equal(policy.normalizedClauses({ ripeness_role_binding: true }).ripeness_role_binding, true);
check(policy.classifyShapeState !== policy.familyFromSignature);

process.stdout.write(`${JSON.stringify({ assertions, failures: 0, omissions: 0, deselections: 0, new_constants: 0 })}\n`);
