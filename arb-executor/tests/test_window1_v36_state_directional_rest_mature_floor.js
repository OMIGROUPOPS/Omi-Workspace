"use strict";

const assert = require("assert");
const policy = require("../analysis/window1_v36_state_directional_rest_mature_floor.js");

const book = (bid, ask, dwell = 10, size = 5) => ({ bid, ask, spread: ask - bid, ask_dwell_seconds: dwell, top_ask_size: size });

assert.strictEqual(policy.stateDirectionalRestTarget({ state: "FALLING", bid: 50, activeTarget: 44 }), 44);
assert.strictEqual(policy.stateDirectionalRestTarget({ state: "FALLING", bid: 40, activeTarget: 44 }), 39);
assert.strictEqual(policy.stateDirectionalRestTarget({ state: "RISING", bid: 50, activeTarget: 44 }), 49);
assert.strictEqual(policy.stateDirectionalRestTarget({ state: "SETTLED", bid: 50, activeTarget: 44, pairCap: 46 }), 46);

let decision = policy.decide({ state: "FALLING", book: book(50, 51, 20, 20), activeTarget: 44, activeEvidenceFloor: 51, floorMature: true });
assert.deepStrictEqual([decision.action, decision.target_cents], ["TAKE", 51]);
decision = policy.decide({ state: "FALLING", book: book(50, 51, 20, 20), activeTarget: 44, activeEvidenceFloor: 51, floorMature: false });
assert.deepStrictEqual([decision.action, decision.target_cents], ["HOLD_REST", 44]);
assert.strictEqual(decision.reason, "ACTIVE_EVIDENCE_FLOOR_NOT_MATURE_NEW_LOW_INSIDE_TRAILING_HORIZON");
decision = policy.decide({ state: "FALLING", book: book(40, 41, 20, 20), activeTarget: 44, activeEvidenceFloor: 39, floorMature: true });
assert.deepStrictEqual([decision.action, decision.target_cents, decision.direction], ["REPRICE_REST", 39, "DOWN"]);
decision = policy.decide({ state: "RISING", book: book(50, 60, 20, 20), activeTarget: 44, activeEvidenceFloor: 39, floorMature: true });
assert.deepStrictEqual([decision.action, decision.target_cents, decision.direction], ["REPRICE_REST", 49, "UP"]);

assert.strictEqual(policy.matureDirectionalEvidenceFloor({ state: "FALLING", runningEvidenceFloor: 50, receiptLocalEvidenceFloor: null, reformedQualifyingAskFloor: 56, reformedQualifyingAskAuthority: true, floorMature: true }), 50);
assert.strictEqual(policy.matureDirectionalEvidenceFloor({ state: "RISING", runningEvidenceFloor: 50, receiptLocalEvidenceFloor: 52, reformedQualifyingAskFloor: 56, reformedQualifyingAskAuthority: true, floorMature: true }), 52);
assert.strictEqual(policy.matureDirectionalEvidenceFloor({ state: "RISING", runningEvidenceFloor: 50, receiptLocalEvidenceFloor: null, reformedQualifyingAskFloor: 56, reformedQualifyingAskAuthority: true, floorMature: false }), 50);
assert.strictEqual(policy.matureDirectionalEvidenceFloor({ state: "RISING", runningEvidenceFloor: 50, receiptLocalEvidenceFloor: null, reformedQualifyingAskFloor: 56, reformedQualifyingAskAuthority: true, floorMature: true }), 56);
assert.strictEqual(policy.matureDirectionalEvidenceFloor({ state: "SETTLED", runningEvidenceFloor: 39, receiptLocalEvidenceFloor: null, reformedQualifyingAskFloor: 41, reformedQualifyingAskAuthority: false, floorMature: true }), 39);

assert.strictEqual(policy.strictMakerFill({ target_cents: 50, action_ts: 100 }, { ts: 101, taker_side: "no", size: 5, price: 50 }), true);
assert.strictEqual(policy.strictMakerFill({ target_cents: 50, action_ts: 100 }, { ts: 100, taker_side: "no", size: 5, price: 50 }), false);

console.log("PASS test_window1_v36_state_directional_rest_mature_floor");
