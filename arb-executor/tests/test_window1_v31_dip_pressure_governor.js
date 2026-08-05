"use strict";

const assert = require("assert");
const {
  HALFLIFE_SECONDS,
  TRAINING_DIP_HORIZON_SECONDS,
  MIN_AUTHORITY_PRECISION_LIFT,
  MIN_TRAIN_ROWS,
  FEATURE_NAMES,
  rawBands,
  updateEwma,
  featureVector,
  predict,
  onlineUpdate,
  fitThreshold,
  authorityVerdict,
  governBuy,
} = require("../analysis/window1_v31_dip_pressure_governor.js");

assert.strictEqual(HALFLIFE_SECONDS, 120);
assert.strictEqual(TRAINING_DIP_HORIZON_SECONDS, 600);
assert.strictEqual(MIN_AUTHORITY_PRECISION_LIFT, .05);
assert.strictEqual(MIN_TRAIN_ROWS, 40);
assert.deepStrictEqual(FEATURE_NAMES, ["cross", "lock", "bid_dom", "ask_dom", "ask_stair", "bid_stair"]);
const first = { ts: 100, bid: 50, ask: 51, top_bid_depth: 90, top_ask_depth: 10 };
const raw = rawBands(null, first);
assert.strictEqual(raw.cross, 0);
assert.strictEqual(raw.lock, 0);
assert.strictEqual(raw.bid_dom, .9);
const state1 = updateEwma(null, null, first);
const state2 = updateEwma(state1, 100, { ts: 220, bid: 51, ask: 50, top_bid_depth: 50, top_ask_depth: 50 });
assert(Math.abs(state2.cross - .5) < 1e-12);
assert(Math.abs(state2.ask_stair - .5) < 1e-12);
assert(Math.abs(state2.bid_stair - .5) < 1e-12);
assert.strictEqual(featureVector(state2).length, 7);
const weights = Array(7).fill(0);
assert.strictEqual(predict(weights, featureVector(state2)), .5);
assert(onlineUpdate(weights, featureVector(state2), 1, 0)[0] > 0);
const history = [];
for (let i = 0; i < 50; i += 1) history.push({ probability: i / 50, label: i >= 30 ? 1 : 0, deeper_floor_drop_cents: i >= 30 ? 3 : 0 });
const threshold = fitThreshold(history);
assert(threshold);
assert.strictEqual(threshold.pressure_implied_drop_cents, 3);
const earned = authorityVerdict(Array.from({ length: 40 }, (_, i) => ({ walkforward_scored: true, pressure_state: i >= 20 ? "HIGH" : "LOW", label: i >= 20 ? 1 : 0 })));
assert.strictEqual(earned.earned, true);
assert.strictEqual(governBuy({ authority: earned, pressureState: "LOW", currentPriceCents: 42, impliedDropCents: 4 }).decision, "UNCHANGED");
const demoted = governBuy({ authority: earned, pressureState: "HIGH", currentPriceCents: 42, impliedDropCents: 4 });
assert.strictEqual(demoted.decision, "DEMOTE");
assert.strictEqual(demoted.target_cents, 38);
assert.deepStrictEqual(demoted.clock_inputs, []);
assert.strictEqual(governBuy({ authority: { earned: false }, pressureState: "HIGH", currentPriceCents: 42, impliedDropCents: 4 }).decision, "UNCHANGED");

process.stdout.write("window1 V31 dip-pressure governor policy tests: PASS (causal EWMA, walk-forward authority, demotion, fallback)\n");
