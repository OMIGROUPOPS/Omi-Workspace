#!/usr/bin/env node
"use strict";

const assert = require("assert");
const policy = require("../analysis/window1_v52o_benchmarked_role_instrument.js");

let assertions = 0;
const equal = (actual, expected, message) => { assertions += 1; assert.deepStrictEqual(actual, expected, message); };
const check = (value, message) => { assertions += 1; assert(value, message); };
const families = policy.FAMILY_ORDER;
const categories = ["ATP_MAIN", "ATP_CHALL", "WTA_MAIN", "WTA_CHALL"];
const downDepth = { DRIFT_DOWN: 8, EARLY_SET_DOWN: 10, ONE_STEP_DOWN: 6, LATE_BREAK_DOWN: 12, GRIND_WOBBLE_DOWN: 14 };
const rows = families.flatMap((family) => categories.map((category, index) => ({
  family, category, legs: family.endsWith("_DOWN") ? index + 1 : 30,
  depth_below_open_c: { med: downDepth[family] ?? 2 }, floor_pos: { med: 0.5 },
  early_call: family.endsWith("_DOWN") || family.endsWith("_UP") ? { kind: "DIRECTIONAL", median_declare_f: 0.25 } : { kind: "STILL" },
})));
equal(rows.length, 52);
policy.configureShapeLibrary({
  taxonomy: { LABEL: "SHAPE_TAXONOMY_BUILD1", families: Object.fromEntries(families.map((family) => [family, 1])), benchmark: { classifier: "early-window drift alone: last in-span print before the receipt minus post-formation open; >=+2c CLIMBER, <=-2c FALLER, else ABSTAIN", by_family_acc: Object.fromEntries(families.map((family) => [family, "95%"])) } },
  floor_tables: { LABEL: "PER_SHAPE_FLOOR_DEPTH_TABLES", rows },
  taxonomy_provenance: { commit: policy.BENCHMARK_ROLE_RULE_COMMIT, sha256: "a".repeat(64) },
  floor_table_provenance: { commit: "8ab4f2d9e8c831235dc7cb4570c88daa3caded50", sha256: "b".repeat(64) },
});

const state = policy.emptyShapeState();
let role = policy.classifyShapeState(state, { timestamp_epoch: 0, receipt: "E0", category: "ATP_MAIN", role_instrument_enabled: true });
equal(role.role, "ABSTAIN");
equal(role.status, "ABSTAIN_NO_POST_FORMATION_TRUE_PRINT");
policy.observeTruePrint(state, { kind: "PRINT", ts: 10, ordinal: 1, price: 50, receipt: "P0" });
role = policy.classifyShapeState(state, { timestamp_epoch: 10, receipt: "E1", category: "ATP_MAIN", role_instrument_enabled: true });
equal(role.post_formation_open_cents, 50);
equal(role.drift_cents, 0);
equal(role.role, "ABSTAIN");
policy.observeTruePrint(state, { kind: "PRINT", ts: 20, ordinal: 2, price: 52, receipt: "P1" });
role = policy.classifyShapeState(state, { timestamp_epoch: 20, receipt: "E2", category: "ATP_MAIN", role_instrument_enabled: true });
equal(role.drift_cents, 2);
equal(role.role, "ROLE_UP");
equal(role.rule.threshold_cents, 2);
equal(role.rule.new_constants, 0);
equal(role.maximum_consumed_timestamp_epoch, 20);
policy.observeTruePrint(state, { kind: "PRINT", ts: 30, ordinal: 3, price: 47, receipt: "P2" });
role = policy.classifyShapeState(state, { timestamp_epoch: 30, receipt: "E3", category: "ATP_MAIN", role_instrument_enabled: true });
equal(role.drift_cents, -3);
equal(role.role, "ROLE_DOWN");
equal(role.causal, true);
equal(role.right_edge_consumed, false);
equal(role.full_span_fit, false);

const aggregate = policy.downDepthAggregate("ATP_MAIN");
equal(aggregate.row_identity, "ROLE_DOWN_AGGREGATE|ATP_MAIN");
equal(aggregate.component_rows.length, 5);
equal(aggregate.total_frequency_weight, 5);
equal(aggregate.depth_below_open_cents, 10);
equal(aggregate.borrowed_from, null);
equal(aggregate.interpolation, false);
equal(aggregate.provenance.sha256, "b".repeat(64));

const incumbent = { action: "PLACE_REST", target_cents: 49, reason: "V43_TRACKER", placement: { target_cents: 49, authority: "V43_TRACKER" } };
const machineReadEvidence = { evaluation_timestamp_epoch: 30, directional_evidence_timestamp_epoch: 30, evaluation_receipt: "E3", directional_evidence_receipt: "P2", post_onset_observation_bounds: { min_cents: 40, max_cents: 60 } };
const downLicense = { onset: { timestamp_epoch: 10 }, level: { macro_recognition: role, machine_read_evidence: machineReadEvidence } };
const selected = policy.roleDepthSelection(downLicense, incumbent, { category: "ATP_MAIN", book: { ask: 60 }, siblingCredited: true, siblingEntryCents: 45 });
equal(selected.applicable, true);
equal(selected.selected_target_cents, 40);
equal(selected.clause_6_cap_cents, 54);
equal(selected.current_touch_ask_cents, 60);
equal(selected.down_depth_row_consumed.row_identity, "ROLE_DOWN_AGGREGATE|ATP_MAIN");
equal(selected.priors_gate, false);

const up = { ...role, role: "ROLE_UP", drift_cents: 3 };
const upSelection = policy.roleDepthSelection({ onset: { timestamp_epoch: 10 }, level: { macro_recognition: up, machine_read_evidence: machineReadEvidence } }, incumbent, { category: "ATP_MAIN", book: { ask: 60 } });
equal(upSelection.applicable, false);
equal(upSelection.selected_target_cents, 49);
equal(upSelection.level_policy, "V52L_DEFAULT_EVIDENCE_BACKED_LEVEL_CATCH_EARLY");
const abstainSelection = policy.roleDepthSelection({ onset: { timestamp_epoch: 10 }, level: { macro_recognition: { ...up, role: "ABSTAIN", signable: false }, machine_read_evidence: machineReadEvidence } }, incumbent, { category: "ATP_MAIN", book: { ask: 60 } });
equal(abstainSelection.applicable, false);
equal(abstainSelection.selected_target_cents, 49);
equal(policy.normalizedClauses({ benchmarked_role_instrument: true }).benchmarked_role_instrument, true);
check(policy.classifyShapeState !== policy.familyFromSignature, "role instrument must not reuse family classifier");

process.stdout.write(`${JSON.stringify({ assertions, failures: 0, omissions: 0, deselections: 0, exact_published_rule: true, new_constants: 0 })}\n`);
