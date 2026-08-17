#!/usr/bin/env node
"use strict";

const assert = require("assert");
const policy = require("../analysis/window1_v52n_recognition_confidence_gates.js");

const families = Object.fromEntries(policy.FAMILY_ORDER.map((family) => [family, 1]));
const confidence = Object.fromEntries(policy.FAMILY_ORDER.filter((family) => !policy.ABSTAIN_FAMILIES.has(family)).map((family) => [family, "95%"]));
const early = (family) => {
  if (family.startsWith("LATE_BREAK")) return { kind: "DIRECTIONAL", median_declare_f: 0.8125, declared_by_f025_pct: 20, declared_by_f05_pct: 30, ever_declares_pct: 100 };
  if (family.endsWith("_DOWN") || family.endsWith("_UP")) return { kind: "DIRECTIONAL", median_declare_f: 0.25, declared_by_f025_pct: 60, declared_by_f05_pct: 95, ever_declares_pct: 100 };
  return { kind: "STILL", still_within_2c_at_f025_pct: 62, still_at_f05_pct: 44 };
};
const rows = policy.FAMILY_ORDER.flatMap((family) => [
  { family, category: "ALL", legs: 30, depth_below_open_c: { med: 2 }, floor_pos: { med: 0.5 }, early_call: early(family) },
  { family, category: "ATP_MAIN", legs: 30, depth_below_open_c: { med: 2 }, floor_pos: { med: 0.5 }, early_call: early(family) },
  { family, category: "ATP_CHALL", legs: 30, depth_below_open_c: { med: 2 }, floor_pos: { med: 0.5 }, early_call: early(family) },
  { family, category: "WTA_MAIN", legs: 30, depth_below_open_c: { med: 2 }, floor_pos: { med: 0.5 }, early_call: early(family) },
]);
assert.strictEqual(rows.length, 52);
policy.configureShapeLibrary({
  taxonomy: { LABEL: "SHAPE_TAXONOMY_BUILD1", families, benchmark: { by_family_acc: confidence } },
  floor_tables: { LABEL: "PER_SHAPE_FLOOR_DEPTH_TABLES", rows },
  taxonomy_provenance: { commit: "e269779b0ec025d55f67d576e3cfb0cb575d5890", sha256: "a".repeat(64) },
  floor_table_provenance: { commit: "8ab4f2d9e8c831235dc7cb4570c88daa3caded50", sha256: "b".repeat(64) },
});

const recognition = (family, net, signable = true, value = 0.95) => ({ family, signable, confidence: value, signature: { net_cents: net } });
const drift = policy.confidenceGate(recognition("DRIFT_DOWN", -5), "ATP_MAIN");
assert.strictEqual(drift.passed, true);
assert.strictEqual(drift.gate.median_declaration_by_pinned_checkpoint, true);
assert.strictEqual(drift.gate.receipt_has_pinned_directional_declaration, true);
assert.strictEqual(drift.gate.required_directional_drift_cents, 2);
assert.strictEqual(drift.gate.pinned_early_checkpoint_f, 0.5);
assert.strictEqual(policy.confidenceGate(recognition("LATE_BREAK_DOWN", -5), "ATP_MAIN").passed, false);
assert.strictEqual(policy.confidenceGate(recognition("QUIET_WOBBLE", 0), "ATP_MAIN").passed, false);
assert.strictEqual(policy.confidenceGate(recognition("DRIFT_UP", 1), "ATP_MAIN").passed, false);
assert.strictEqual(policy.confidenceGate(recognition("DRIFT_UP", 5, false), "ATP_MAIN").passed, false);

const state = policy.emptyShapeState();
policy.observeTruePrint(state, { kind: "PRINT", ts: 0, ordinal: 0, price: 50, receipt: "R0" });
policy.observeTruePrint(state, { kind: "PRINT", ts: 60, ordinal: 1, price: 50, receipt: "R1" });
const earlyAbstain = policy.classifyShapeState(state, { timestamp_epoch: 60, receipt: "E1", category: "ATP_MAIN", confidence_gate_enabled: true });
assert.strictEqual(earlyAbstain.classification_class, "ABSTAIN");
assert.strictEqual(earlyAbstain.signable, false);
policy.observeTruePrint(state, { kind: "PRINT", ts: 120, ordinal: 2, price: 48, receipt: "R2" });
policy.observeTruePrint(state, { kind: "PRINT", ts: 180, ordinal: 3, price: 46, receipt: "R3" });
policy.observeTruePrint(state, { kind: "PRINT", ts: 240, ordinal: 4, price: 44, receipt: "R4" });
const later = policy.classifyShapeState(state, { timestamp_epoch: 240, receipt: "E2", category: "ATP_MAIN", confidence_gate_enabled: true });
assert.ok(later.proposed_family.endsWith("_DOWN"));
assert.strictEqual(later.binding_family, later.proposed_family);
assert.strictEqual(later.signable, true);
assert.strictEqual(later.recognition_confidence_gate.passed, true);
const ungated = policy.classifyShapeState(state, { timestamp_epoch: 240, receipt: "E3", category: "ATP_MAIN", confidence_gate_enabled: false });
assert.strictEqual(ungated.recognition_confidence_gate, undefined);
assert.strictEqual(ungated.signable, true);
assert.strictEqual(policy.PINNED_EARLY_CHECKPOINT_F, 0.5);
assert.strictEqual(policy.PINNED_DIRECTIONAL_DECLARATION_CENTS, 2);
const repaired = policy.restoreGuardTerminationReceipt({ action: "HOLD_REST", target_cents: 44, guard: null }, { clauses: { release_guard_on_sibling_credit: true }, siblingCredited: true });
assert.strictEqual(repaired.guard_authority_terminated, true);
assert.deepStrictEqual({ action: repaired.action, target_cents: repaired.target_cents, guard: repaired.guard }, { action: "HOLD_REST", target_cents: 44, guard: null });

process.stdout.write(`${JSON.stringify({ assertions: 22, failures: 0, one_clause: "RECOGNITION_CONFIDENCE_GATE", reattempted_as_evidence_accrued: true, new_constants: 0, mechanical_receipt_stamp_repairs: 1 })}\n`);
