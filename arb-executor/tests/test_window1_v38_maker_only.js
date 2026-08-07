"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const policy = require("../analysis/window1_v38_maker_only_machine.js");

let tests = 0;
function test(name, fn) { fn(); tests += 1; process.stdout.write(`ok - ${name}\n`); }

test("take action is structurally absent from the policy", () => {
  const source = fs.readFileSync(path.join(__dirname, "../analysis/window1_v38_maker_only_machine.js"), "utf8");
  assert(!/action:\s*["']TAKE["']/.test(source));
  assert(!/function\s+\w*take\w*/i.test(source));
});

test("FALLING preserves V36 no-chase target", () => {
  assert.strictEqual(policy.fallingTarget({ bid: 50, activeTarget: 45, pairCap: 60 }), 45);
  assert.strictEqual(policy.fallingTarget({ bid: 40, activeTarget: 45, pairCap: 60 }), 39);
});

test("SETTLED tracks bid minus one and pair cap", () => {
  assert.strictEqual(policy.settledTarget({ bid: 61 }), 60);
  assert.strictEqual(policy.settledTarget({ bid: 61, pairCap: 57 }), 57);
});

test("unchanged recorder snapshots do not manufacture a revisit", () => {
  const one = policy.trailingPulseFloor([{ ts: 1, ordinal: 1, ask: 68 }, { ts: 2, ordinal: 2, ask: 68 }], 2);
  assert.strictEqual(one.floor_cents, 68, "tracker consumes visits, caller is responsible for transitions");
  const transitions = [{ ts: 1, ordinal: 1, ask: 68 }];
  assert.strictEqual(policy.trailingPulseFloor(transitions, 2).floor_cents, null);
});

test("second distinct visit makes the deepest pulse level signable", () => {
  const visits = [
    { ts: 1, ordinal: 1, ask: 70 },
    { ts: 10, ordinal: 2, ask: 68 },
    { ts: 20, ordinal: 3, ask: 70 },
    { ts: 30, ordinal: 4, ask: 68 },
  ];
  assert.strictEqual(policy.trailingPulseFloor(visits, 30).floor_cents, 68);
});

test("RISING pulse floor waits rather than crossing a standing ask", () => {
  const held = policy.decide({ state: "RISING", book: { bid: 67, ask: 68 }, pulseFloor: 68 });
  assert.deepStrictEqual(held, { action: "HOLD_REST", target_cents: null, reason: "POST_ONLY_REST_WOULD_CROSS_STANDING_ASK" });
  const placed = policy.decide({ state: "RISING", book: { bid: 69, ask: 70 }, pulseFloor: 68 });
  assert.strictEqual(placed.action, "PLACE_REST"); assert.strictEqual(placed.target_cents, 68);
});

test("RISING pair cap remains binding", () => {
  const placed = policy.decide({ state: "RISING", book: { bid: 60, ask: 61 }, pulseFloor: 58, pairCap: 55 });
  assert.strictEqual(placed.target_cents, 55);
});

test("market quote touch requires later qualified evidence", () => {
  const order = { target_cents: 68, action_ts: 100 };
  assert(!policy.quoteTouch(order, { ts: 100, bid: 67, ask: 68, spread: 1, ask_dwell_seconds: 10, top_ask_size: 5 }));
  assert(policy.quoteTouch(order, { ts: 101, bid: 67, ask: 68, spread: 1, ask_dwell_seconds: 10, top_ask_size: 5 }));
});

test("strict print crossing remains seller-side size-five verification", () => {
  const order = { target_cents: 40, action_ts: 100 };
  assert(policy.strictPrintCross(order, { ts: 101, price: 40, size: 5, taker_side: "no" }));
  assert(!policy.strictPrintCross(order, { ts: 101, price: 40, size: 4, taker_side: "no" }));
  assert(!policy.strictPrintCross(order, { ts: 101, price: 40, size: 5, taker_side: "yes" }));
});

test("traded-at-level is a distinct market ruler", () => {
  const order = { target_cents: 40, action_ts: 100 };
  assert(policy.tradedAtLevel(order, { ts: 101, price: 39, size: 1, taker_side: "yes" }));
});

process.stdout.write(`${tests} tests passed\n`);
