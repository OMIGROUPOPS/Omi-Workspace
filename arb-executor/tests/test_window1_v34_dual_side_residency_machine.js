"use strict";

const assert = require("assert");
const p = require("../analysis/window1_v34_dual_side_residency_machine.js");

assert.strictEqual(p.walkingRestTarget({ bid: 50 }), 49);
assert.strictEqual(p.walkingRestTarget({ bid: 50, runningTradeLow: 45 }), 45);
assert.strictEqual(p.walkingRestTarget({ bid: 50, runningQualifyingAskLow: 46 }), 46);
assert.strictEqual(p.walkingRestTarget({ bid: 55, previousTarget: 49 }), 49);
assert.strictEqual(p.walkingRestTarget({ bid: 40, previousTarget: 49 }), 39);
assert.strictEqual(p.walkingRestTarget({ bid: 50, pairCap: 44 }), 44);
assert.strictEqual(p.walkingRestTarget({ bid: 1 }), null);

const fresh = { bid: 54, ask: 55, spread: 1, ask_dwell_seconds: 0, top_ask_size: 5 };
assert.strictEqual(p.decide({ state: "SETTLED", book: fresh }).action, "PLACE_REST");
const qualified = { ...fresh, ask_dwell_seconds: 10 };
assert.strictEqual(p.decide({ state: "SETTLED", book: qualified, activeTarget: 53 }).action, "TAKE");
assert.strictEqual(p.decide({ state: "SETTLED", book: qualified, activeTarget: 53, pairCap: 54 }).action, "HOLD_REST");
assert.strictEqual(p.r3QualifiedTake({ ...qualified, bid: 55, top_ask_size: 0 }), true);
assert.strictEqual(p.decide({ state: "FALLING", book: { ...qualified, bid: 50 }, activeTarget: 53 }).target_cents, 49);
assert.strictEqual(p.decide({ state: "RISING", book: { ...qualified, bid: 60 }, activeTarget: 53 }).target_cents, 53);

const order = { target_cents: 50, action_ts: 100 };
assert.strictEqual(p.strictMakerFill(order, { ts: 101, taker_side: "no", size: 5, price: 50 }), true);
assert.strictEqual(p.strictMakerFill(order, { ts: 101, taker_side: "no", size: 4, price: 50 }), false);
assert.strictEqual(p.strictMakerFill(order, { ts: 100, taker_side: "no", size: 5, price: 50 }), false);
assert.strictEqual(p.censusPricedFill(order, { ts: 101, taker_side: "no", size: 5, price: 50 }).class, "PROVEN_MAKER_SELLER_AGGRESSED_PRINT_SIZE_FIVE_AT_OR_BELOW_REST");
assert.strictEqual(p.censusPricedFill(order, { ts: 101, taker_side: "no", size: 1, price: 51 }).class, "CENSUS_PRICED_ONE_CENT_RESIDENCY_CONVERSION");
assert.strictEqual(p.censusPricedFill(order, { ts: 101, taker_side: "no", size: 1, price: 52 }), null);

console.log("PASS test_window1_v34_dual_side_residency_machine");
