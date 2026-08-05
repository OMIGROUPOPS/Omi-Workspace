"use strict";

const assert = require("assert");
const policy = require("../analysis/window1_v32_no_chase_state_machine.js");

assert.strictEqual(policy.LOOKBACK_SECONDS, 300);
assert.strictEqual(policy.PRESSURE_RISING_MIN, .60);
assert.strictEqual(policy.PRESSURE_FALLING_MAX, .40);
assert.strictEqual(policy.quotePathState([], 1000).state, "SETTLED");
assert.strictEqual(policy.quotePathState([{ ts: 800, ordinal: 1, direction: "FALLING", kind: "NEW_LOW_ASK", receipt: "a" }], 1000).state, "FALLING");
assert.strictEqual(policy.quotePathState([{ ts: 699, ordinal: 1, direction: "FALLING", kind: "NEW_LOW_ASK", receipt: "a" }], 1000).state, "SETTLED");
assert.strictEqual(policy.quotePathState([{ ts: 999, ordinal: 1, direction: "SETTLED", kind: "QUOTE_PATH_INTERNAL_CONFLICT_NEW_LOW_ASK_AND_NEW_HIGH_BID", receipt: "c" }], 1000).state, "SETTLED");
assert.strictEqual(policy.pressureState(.60), "RISING");
assert.strictEqual(policy.pressureState(.40), "FALLING");
assert.strictEqual(policy.pressureState(.50), "SETTLED");
const disagreement = policy.combineState({ state: "FALLING" }, "RISING");
assert.strictEqual(disagreement.state, "FALLING");
assert.strictEqual(disagreement.disagreement, true);
assert.strictEqual(policy.fallingRestTarget({ bid: 50 }), 49);
assert.strictEqual(policy.fallingRestTarget({ bid: 52, previousTarget: 49 }), 49);
assert.strictEqual(policy.fallingRestTarget({ bid: 48, previousTarget: 49 }), 47);
assert.strictEqual(policy.fallingRestTarget({ bid: 50, pairCap: 45 }), 45);
const book = { bid: 54, ask: 55, spread: 1, ask_dwell_seconds: 10, top_ask_size: 5 };
assert.strictEqual(policy.decide({ state: "SETTLED", book }).action, "TAKE");
assert.strictEqual(policy.decide({ state: "SETTLED", book: { ...book, ask_dwell_seconds: 9 } }).action, "HOLD");
assert.strictEqual(policy.decide({ state: "FALLING", book }).target_cents, 53);
assert.strictEqual(policy.decide({ state: "RISING", book }).action, "HOLD");
const order = { target_cents: 53, action_ts: 100 };
assert.strictEqual(policy.sellerPrintFills(order, { ts: 101, price: 53, size: 5, taker_side: "no" }), true);
assert.strictEqual(policy.sellerPrintFills(order, { ts: 101, price: 53, size: 4, taker_side: "no" }), false);
assert.strictEqual(policy.sellerPrintFills(order, { ts: 101, price: 53, size: 5, taker_side: "yes" }), false);
assert.strictEqual(policy.sellerPrintFills(order, { ts: 100, price: 53, size: 5, taker_side: "no" }), false);

process.stdout.write("window1 V32 no-chase state machine tests: PASS\n");
