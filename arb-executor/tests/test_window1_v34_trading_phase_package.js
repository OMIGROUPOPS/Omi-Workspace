"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const out = path.join(ROOT, ".claude/window1_live_v4_replay/v34_dual_side_residency_machine_trading_phase_20260805");
const read = (name) => JSON.parse(fs.readFileSync(path.join(out, name), "utf8"));

const control = read("CONTROL_BINDING.json");
const binding = read("CANONICAL_CLOSE_BINDING.json");
const exclusion = read("SETTLEMENT_EVIDENCE_EXCLUSION_RECEIPT.json");
const score = read("SCORECARD_TWO_COLUMN.json");
const spans = read("TRADING_PHASE_SPAN_804.json");
const forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
const determinism = read("DETERMINISM_RECEIPT.json");

assert.strictEqual(control.canonical_close_binding.commit, "4f35ddea00a877c9b1129702a523abe2d689adb8");
assert.strictEqual(control.canonical_close_binding.sha256, "9188a771a9a8c6ec671485f8d4c1c61ffd60372b0df742cf4ab66ad1afa98c58");
assert.strictEqual(control.window_law.settlement_basis_role, "FORBIDDEN_NEGATIVE_CONTROL_ONLY");
assert.strictEqual(binding.map_events, 804);
assert.strictEqual(binding.map_T1_joint_comparison_universe, 750);
assert.strictEqual(binding.map_event_identity_mismatches, 0);
assert.strictEqual(binding.map_leg_close_mismatches, 0);
assert.strictEqual(binding.available_legs, 1606);
assert.strictEqual(binding.unavailable_legs, 2);
assert.strictEqual(binding.close_price_counts.UNAVAILABLE_CANONICAL_TRUE_CLOSE_NULL, 2);
assert.strictEqual(exclusion.settlement_basis_close_reads, 0);
assert.strictEqual(exclusion.settlement_basis_floor_reads, 0);
assert.strictEqual(exclusion.settlement_basis_fill_reads, 0);
assert.strictEqual(score.STRICT_LAW.canonical_T1_joint_comparison_universe, 750);
assert.strictEqual(score.CENSUS_PRICED.canonical_T1_joint_comparison_universe, 750);
assert.strictEqual(score.STRICT_LAW.aggregate.D, 804);
assert.strictEqual(score.CENSUS_PRICED.aggregate.D, 804);
assert.strictEqual(spans.events, 804);
assert.strictEqual(spans.exact_trading_phase_boundaries, 804);
assert.strictEqual(spans.actual_bell_metadata_available_events, 234);
assert.strictEqual(forbidden.settlement_basis_scoring_reads, 0);
assert.strictEqual(forbidden.live_accesses, 0);
assert.strictEqual(determinism.builds, 2);
assert.strictEqual(determinism.byte_identical, true);

console.log("PASS test_window1_v34_trading_phase_package");
