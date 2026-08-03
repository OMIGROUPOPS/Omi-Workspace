#!/usr/bin/env node
"use strict";

const assert = require("assert");
const { pairFeatures, matchesPairEnvelope, mutuallyNarrowPairAndLegs } = require("../analysis/window1_pair_interim_elimination_v18.js");

function row(ask, net, dip, peak, drawdown) {
  return { ask, bid: ask - 1, spread: 1, top_ask_size: 8, top5_ask_depth: 20, ask_dwell_seconds: 12, prefix: { ask_net: net, ask_dip: dip, ask_peak: peak, ask_drawdown_from_peak: drawdown, mean_spread: 1, spread_range: 0, quote_rate: 4, ask_change_rate: 1, ask_dwell_fraction: .5, mean_log_top_ask_size: 2, mean_log_top5_ask_depth: 3, qualified_ask_descent_count: 1, qualified_ask_rise_count: 0 } };
}
const high = row(68, -2, -2, 0, 2), low = row(31, 1, 0, 1, 0), features = pairFeatures(high, low);
assert.strictEqual(features.ask_sum, 99);
assert.strictEqual(features.high_ask_net, -2);
assert.strictEqual(features.low_top5_ask_depth, 20);

const keys = ["high_ask_net", "high_ask_dip", "high_ask_peak", "high_ask_drawdown_from_peak", "low_ask_net", "low_ask_dip", "low_ask_peak", "low_ask_drawdown_from_peak", "ask_sum", "ask_net_sum"];
const envelope = Object.fromEntries(keys.map((key) => [key, [features[key], features[key]]]));
const hypotheses = [
  { pair_hypothesis_id: "PAIR_A", usable_for_signing: true, joint_interim_envelopes: [envelope], member_single_shape_pairs: [{ high_shape_id: "H_A", low_shape_id: "L_A", n: 25 }] },
  { pair_hypothesis_id: "PAIR_B", usable_for_signing: true, joint_interim_envelopes: [Object.fromEntries(keys.map((key) => [key, [features[key] + 1, features[key] + 1]]))], member_single_shape_pairs: [{ high_shape_id: "H_B", low_shape_id: "L_B", n: 22 }] },
  { pair_hypothesis_id: "PAIR_THIN", usable_for_signing: false, joint_interim_envelopes: [envelope], member_single_shape_pairs: [{ high_shape_id: "H_X", low_shape_id: "L_X", n: 3 }] },
];
assert.strictEqual(matchesPairEnvelope(hypotheses[0], high, low, 0), true);
assert.strictEqual(matchesPairEnvelope(hypotheses[1], high, low, 0), false);
const narrowed = mutuallyNarrowPairAndLegs({ group: { hypotheses }, priorPairIds: hypotheses.map((x) => x.pair_hypothesis_id), highShapes: ["H_A", "H_B", "H_X"], lowShapes: ["L_A", "L_B", "L_X"], highRow: high, lowRow: low, bin: 0 });
assert.strictEqual(narrowed.status, "PAIR_AND_SINGLE_LIBRARIES_MUTUALLY_NARROWED");
assert.deepStrictEqual(narrowed.high_shapes, ["H_A"]);
assert.deepStrictEqual(narrowed.low_shapes, ["L_A"]);
assert.deepStrictEqual(narrowed.signable_pair_survivor_ids, ["PAIR_A"]);
assert.strictEqual(narrowed.tuples.length, 1);
assert.strictEqual(narrowed.tuples[0].support_class, "SYNCHRONIZED_PAIR_INTERIM_HYPOTHESIS");

const unresolved = mutuallyNarrowPairAndLegs({ group: { hypotheses: [hypotheses[2]] }, priorPairIds: ["PAIR_THIN"], highShapes: ["H_X"], lowShapes: ["L_X"], highRow: high, lowRow: low, bin: 0 });
assert.strictEqual(unresolved.status, "PAIR_HYPOTHESIS_UNRESOLVED");
assert.deepStrictEqual(unresolved.tuples, []);

console.log("test_window1_pair_interim_elimination_v18: PASS");
