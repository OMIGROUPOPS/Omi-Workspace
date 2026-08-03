#!/usr/bin/env node
"use strict";

const assert = require("assert");
const { strictInteger, belowFloorBand, publicUnprovenRow, summarizeVersion } = require("../analysis/build_window1_holdout_null_action_correction_v1.js");
const { strictInteger: runnerStrictInteger } = require("../analysis/window1_v11_v13_v14_holdout_runner_v2.js");

for (const parse of [strictInteger, runnerStrictInteger]) {
  assert.strictEqual(parse(null), null);
  assert.strictEqual(parse(undefined), null);
  assert.strictEqual(parse(""), null);
  assert.strictEqual(parse("0"), null);
  assert.strictEqual(parse(false), null);
  assert.strictEqual(parse(true), null);
  assert.strictEqual(parse(NaN), null);
  assert.strictEqual(parse(Infinity), null);
  assert.strictEqual(parse(1.5), null);
  assert.strictEqual(parse(0), 0);
  assert.strictEqual(parse(55), 55);
}

const noAction = { event_id: "SYNTHETIC", category: "TEST", leg_id: "A", ticker: "SYNTHETIC-A", price_region: "26_50", honest_fill_class: "UNPROVEN", proposed_entry_cents: null, own_ask_reachable_low_cents: 55, placement: null, terminal_reason: "ALL_SURVIVING_SHAPES_SAY_LOWER", surviving_shapes_at_terminal: [] };
const corrected = publicUnprovenRow(noAction);
assert.strictEqual(corrected.corrected_execution_state, "NO_ORDER_WAS_PLACED");
assert.strictEqual(corrected.placed_price_cents, null);
assert.strictEqual(corrected.placed_minus_qualifying_ask_floor_cents, null);
assert.strictEqual(corrected.distance_below_floor_band, "NOT_APPLICABLE_NO_ORDER_OR_FLOOR");
assert.strictEqual(corrected.prior_invalid_adapter_projection.coerced_placed_price_cents, 0);
assert.strictEqual(corrected.prior_invalid_adapter_projection.coerced_gap_cents, -55);

const genuineUnproven = publicUnprovenRow({ ...noAction, proposed_entry_cents: 54, placement: { action_receipt: "synthetic#1", micro_position_evidence_type: "SYNTHETIC" } });
assert.strictEqual(genuineUnproven.corrected_execution_state, "ORDER_PLACED_EXECUTION_UNPROVEN");
assert.strictEqual(genuineUnproven.placed_minus_qualifying_ask_floor_cents, -1);
assert.strictEqual(genuineUnproven.distance_below_floor_band, "1_TO_4_CENTS_BELOW");

assert.strictEqual(belowFloorBand(-99), "50_PLUS_CENTS_BELOW");
assert.strictEqual(belowFloorBand(-50), "50_PLUS_CENTS_BELOW");
assert.strictEqual(belowFloorBand(-49), "25_TO_49_CENTS_BELOW");
assert.strictEqual(belowFloorBand(0), "AT_OR_ABOVE_FLOOR");

const summary = summarizeVersion([
  noAction,
  { ...noAction, proposed_entry_cents: 55, honest_fill_class: "PROVEN_TAKER", honest_credited_entry_cents: 55, action_book: { ask: 55 } },
]);
assert.strictEqual(summary.legs, 2);
assert.strictEqual(summary.acted_legs, 1);
assert.strictEqual(summary.no_action_legs, 1);
assert.strictEqual(summary.actual_orders_with_unproven_execution, 0);
assert.strictEqual(summary.raw_UNPROVEN_rows_with_no_order, 1);

process.stdout.write("window1 holdout null-action correction tests: PASS (strict null, 2 synthetic classifications, 4 gap bands)\n");
