"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const out = path.join(ROOT, ".claude/window1_live_v4_replay/v34_dual_side_residency_machine_20260805");
const read = (name) => JSON.parse(fs.readFileSync(path.join(out, name), "utf8"));

const control = read("CONTROL_BINDING.json");
const machine = read("STATE_MACHINE_CONTRACT.json");
const score = read("SCORECARD_TWO_COLUMN.json");
const spans = read("FULL_MARKET_LIFE_SPAN_804.json");
const closeRuler = read("CLOSE_RULER_CONSEQUENCE_RECEIPT.json");
const forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
const determinism = read("DETERMINISM_RECEIPT.json");

assert.strictEqual(control.architecture, "DUAL_SIDE_RESIDENCY_MACHINE_NOT_OVERLAY");
assert.strictEqual(control.window_law.scheduled_edge_role, "NONE");
assert.strictEqual(control.window_law.actual_bell_role, "OPTIONAL_TIMING_METADATA_ONLY_NEVER_BOUNDARY");
assert.deepStrictEqual(machine.clock_inputs, []);
assert.strictEqual(score.STRICT_LAW.aggregate.D, 804);
assert.strictEqual(score.CENSUS_PRICED.aggregate.D, 804);
assert.strictEqual(score.STRICT_LAW.aggregate.legs, 1608);
assert.strictEqual(score.CENSUS_PRICED.aggregate.legs, 1608);
assert.strictEqual(spans.events, 804);
assert.strictEqual(spans.exact_market_close_boundaries, 804);
assert.strictEqual(spans.actual_bell_metadata_available_events, 234);
assert.strictEqual(closeRuler.legs, 1608);
assert.strictEqual(closeRuler.available_legs, 1606);
assert.strictEqual(closeRuler.unavailable_legs, 2);
assert.strictEqual(closeRuler.consequence.strict_both_below_close, 0);
assert.strictEqual(closeRuler.consequence.census_both_below_close, 0);
assert.strictEqual(forbidden.holdout_accesses, 0);
assert.strictEqual(forbidden.live_accesses, 0);
assert.strictEqual(forbidden.network_runtime_accesses, 0);
assert.strictEqual(determinism.builds, 2);
assert.strictEqual(determinism.byte_identical, true);

console.log("PASS test_window1_v34_dual_side_residency_package");
