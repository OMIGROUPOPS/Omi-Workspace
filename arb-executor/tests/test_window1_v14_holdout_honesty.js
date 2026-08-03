#!/usr/bin/env node
"use strict";

const assert = require("assert");
const {
  distribution,
  honestFillCredited,
  metrics,
} = require("../analysis/window1_v11_v13_v14_holdout_runner_v2.js");

const d = distribution([4, -2, 1, null, 9], 5);
assert.strictEqual(d.min, -2);
assert.strictEqual(d.max, 9);
assert.strictEqual(d.available, 4);
assert.strictEqual(d.unavailable, 1);

assert.strictEqual(honestFillCredited("PROVEN_MAKER", 55), true);
assert.strictEqual(honestFillCredited("PROVEN_TAKER", 55), true);
assert.strictEqual(honestFillCredited("UNPROVEN", 55), false);
assert.strictEqual(honestFillCredited("PROVEN_TAKER", 55.5), false);
assert.strictEqual(honestFillCredited("PROVEN_TAKER", null), false);

const legs = [
  { acted: true, credited: true, entry_cents: 40, entry_minus_qualifying_ask_floor_cents: 0, entry_minus_objective_traded_low_cents: 1 },
  { acted: true, credited: false, entry_cents: null, entry_minus_qualifying_ask_floor_cents: null, entry_minus_objective_traded_low_cents: null },
];
const event = { completed_pair: false, pair_under_par: false, both_legs_strictly_below_close: false, legs, ceilings: {} };
const m = metrics([event]);
assert.strictEqual(m.acted_legs, 2);
assert.strictEqual(m.credited_legs, 1);
assert.strictEqual(m.completed_pairs, 0);

console.log(JSON.stringify({ status: "PASS", assertions: 12, development_scorer_calls: 0, holdout_policy_calls: 0, network_access: false }));
