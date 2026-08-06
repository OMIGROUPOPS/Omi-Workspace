"use strict";

const assert = require("assert");
const v36 = require("../analysis/window1_v36_state_directional_rest_mature_floor.js");
const policy = require("../analysis/window1_v37_floor_arithmetic_take_bound.js");

const book = (bid, ask, dwell = 10, size = 5) => ({ bid, ask, spread: ask - bid, ask_dwell_seconds: dwell, top_ask_size: size });
const takeArgs = (ask, otherFloor) => ({
  state: "SETTLED",
  book: book(ask - 1, ask, 20, 20),
  activeTarget: ask - 2,
  activeEvidenceFloor: ask,
  floorMature: true,
  otherRunningPrintBackedFloor: otherFloor,
});

let bound = policy.floorArithmeticTakeBound({ entryCents: 56, otherRunningPrintBackedFloor: 38 });
assert.deepStrictEqual([bound.permitted, bound.comparison], [true, "44 > 38"]); // ARNROM
bound = policy.floorArithmeticTakeBound({ entryCents: 93, otherRunningPrintBackedFloor: 8 });
assert.deepStrictEqual([bound.permitted, bound.comparison], [false, "7 > 8"]); // JACDA
bound = policy.floorArithmeticTakeBound({ entryCents: 79, otherRunningPrintBackedFloor: 18 });
assert.deepStrictEqual([bound.permitted, bound.comparison], [true, "21 > 18"]); // GANJAN
bound = policy.floorArithmeticTakeBound({ entryCents: 62, otherRunningPrintBackedFloor: 38 });
assert.strictEqual(bound.permitted, false); // equality is not strictly under par

let decision = policy.decide(takeArgs(93, 8));
assert.deepStrictEqual([decision.action, decision.target_cents], ["HOLD_REST", 91]);
assert.strictEqual(decision.floor_arithmetic_take_bound.authority, true);
decision = policy.decide(takeArgs(56, 38));
assert.deepStrictEqual([decision.action, decision.target_cents], ["TAKE", 56]);
decision = policy.decide(takeArgs(5, 32));
assert.deepStrictEqual([decision.action, decision.target_cents], ["TAKE", 5]); // KRALOR
decision = policy.decide(takeArgs(32, 60));
assert.deepStrictEqual([decision.action, decision.target_cents], ["TAKE", 32]); // BOSCOP

const noAuthority = takeArgs(56, null);
assert.deepStrictEqual(
  Object.fromEntries(Object.entries(policy.decide(noAuthority)).filter(([key]) => key !== "floor_arithmetic_take_bound")),
  v36.decide(noAuthority),
);
assert.strictEqual(policy.decide(noAuthority).floor_arithmetic_take_bound.authority, false);

const restArgs = { state: "FALLING", book: book(40, 41, 20, 20), activeTarget: 44, activeEvidenceFloor: 39, floorMature: true, otherRunningPrintBackedFloor: 90 };
assert.deepStrictEqual(policy.decide(restArgs), v36.decide(restArgs));

assert.throws(() => policy.floorArithmeticTakeBound({ entryCents: 50.5, otherRunningPrintBackedFloor: 40 }), /integer/);
assert.throws(() => policy.floorArithmeticTakeBound({ entryCents: 50, otherRunningPrintBackedFloor: 40.5 }), /integer or null/);

console.log("PASS test_window1_v37_floor_arithmetic_take_bound");
