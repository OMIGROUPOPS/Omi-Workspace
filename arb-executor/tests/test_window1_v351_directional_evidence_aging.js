"use strict";

const assert = require("assert");
const policy = require("../analysis/window1_v351_directional_evidence_aging.js");

const book = (bid, ask, dwell = 10, size = 5) => ({ bid, ask, spread: ask - bid, ask_dwell_seconds: dwell, top_ask_size: size });

assert.strictEqual(policy.livingRestTarget({ bid: 50 }), 49);
assert.strictEqual(policy.livingRestTarget({ bid: 60, pairCap: 55 }), 55);
assert.strictEqual(policy.livingRestTarget({ bid: 1 }), null);

let decision = policy.decide({ state: "FALLING", book: book(50, 70, 0, 0), activeTarget: null });
assert.deepStrictEqual([decision.action, decision.target_cents], ["PLACE_REST", 49]);
decision = policy.decide({ state: "RISING", book: book(55, 80, 0, 0), activeTarget: 49 });
assert.deepStrictEqual([decision.action, decision.target_cents, decision.direction], ["REPRICE_REST", 54, "UP"]);
decision = policy.decide({ state: "SETTLED", book: book(45, 80, 0, 0), activeTarget: 54 });
assert.deepStrictEqual([decision.action, decision.target_cents, decision.direction], ["REPRICE_REST", 44, "DOWN"]);
decision = policy.decide({ state: "SETTLED", book: book(1, 2, 0, 0), activeTarget: 2 });
assert.deepStrictEqual([decision.action, decision.target_cents], ["CANCEL_REST", null]);

decision = policy.decide({ state: "FALLING", book: book(40, 41, 20, 20), activeTarget: 39, activeEvidenceFloor: 39 });
assert.strictEqual(decision.action, "HOLD_REST");
assert.strictEqual(decision.reason, "UNABSORBED_DOWNWARD_EVIDENCE_ASK_ABOVE_FLOOR");
decision = policy.decide({ state: "RISING", book: book(40, 41, 20, 20), activeTarget: 39, activeEvidenceFloor: 41 });
assert.strictEqual(decision.action, "TAKE");
assert.strictEqual(decision.reason, "EVIDENCE_FLOOR_TAKE_STATE_LABEL_IGNORED");
decision = policy.decide({ state: "FALLING", book: book(31, 32, 13, 27), activeTarget: 30, activeEvidenceFloor: 32, floorFirstFlickerLive: true });
assert.strictEqual(decision.action, "HOLD_REST");
assert.strictEqual(decision.reason, "CURRENT_ASK_CREATED_FLOOR_WHILE_DOWNWARD_SEQUENCE_UNABSORBED");
decision = policy.decide({ state: "SETTLED", book: book(31, 32, 400, 27), activeTarget: 30, activeEvidenceFloor: 32, floorFirstFlickerLive: false });
assert.strictEqual(decision.action, "TAKE");
decision = policy.decide({ state: "SETTLED", book: book(40, 41, 9, 20), activeTarget: 39, activeEvidenceFloor: 41 });
assert.notStrictEqual(decision.action, "TAKE");
decision = policy.decide({ state: "SETTLED", book: book(40, 41, 20, 4), activeTarget: 39, activeEvidenceFloor: 41 });
assert.notStrictEqual(decision.action, "TAKE");
decision = policy.decide({ state: "SETTLED", book: book(40, 41, 20, 20), activeTarget: 39, pairCap: 40, activeEvidenceFloor: 41 });
assert.notStrictEqual(decision.action, "TAKE");

assert.strictEqual(policy.qualifyingAskEvidence(book(40, 41, 10, 5)), true);
assert.strictEqual(policy.qualifyingAskEvidence(book(39, 42, 10, 5)), false);
assert.strictEqual(policy.strictMakerFill({ target_cents: 50, action_ts: 100 }, { ts: 101, taker_side: "no", size: 5, price: 50 }), true);
assert.strictEqual(policy.strictMakerFill({ target_cents: 50, action_ts: 100 }, { ts: 100, taker_side: "no", size: 5, price: 50 }), false);

assert.strictEqual(policy.directionallyAgedEvidenceFloor({ state: "FALLING", runningEvidenceFloor: 50, receiptLocalEvidenceFloor: 56, reformedQualifyingAskFloor: 56 }), 50);
assert.strictEqual(policy.directionallyAgedEvidenceFloor({ state: "RISING", runningEvidenceFloor: 50, receiptLocalEvidenceFloor: 52, reformedQualifyingAskFloor: 56 }), 52);
assert.strictEqual(policy.directionallyAgedEvidenceFloor({ state: "SETTLED", runningEvidenceFloor: 50, receiptLocalEvidenceFloor: null, reformedQualifyingAskFloor: 56, qualifyingAskFloorReformedNow: true }), 56);
assert.strictEqual(policy.directionallyAgedEvidenceFloor({ state: "RISING", runningEvidenceFloor: 50, receiptLocalEvidenceFloor: null, reformedQualifyingAskFloor: 56, qualifyingAskFloorReformedNow: true }), 56);
assert.strictEqual(policy.directionallyAgedEvidenceFloor({ state: "SETTLED", runningEvidenceFloor: 39, receiptLocalEvidenceFloor: null, reformedQualifyingAskFloor: 41, qualifyingAskFloorReformedNow: false }), 39);
assert.strictEqual(policy.directionallyAgedEvidenceFloor({ state: "RISING", runningEvidenceFloor: 50, receiptLocalEvidenceFloor: null, reformedQualifyingAskFloor: 56, qualifyingAskFloorReformedNow: true }), 56);
assert.strictEqual(policy.directionallyAgedEvidenceFloor({ state: "SETTLED", runningEvidenceFloor: 32, receiptLocalEvidenceFloor: null, reformedQualifyingAskFloor: 32, qualifyingAskFloorReformedNow: false }), 32);
assert.strictEqual(policy.directionallyAgedEvidenceFloor({ state: "SETTLED", runningEvidenceFloor: 50, receiptLocalEvidenceFloor: null, reformedQualifyingAskFloor: null }), null);

decision = policy.decide({ state: "RISING", book: book(55, 56, 600, 25), activeTarget: 54, activeEvidenceFloor: 56 });
assert.strictEqual(decision.action, "TAKE");
decision = policy.decide({ state: "RISING", book: book(55, 56, 20, 25), activeTarget: 54, activeEvidenceFloor: 50 });
assert.strictEqual(decision.action, "HOLD_REST");

console.log("PASS test_window1_v351_directional_evidence_aging");
