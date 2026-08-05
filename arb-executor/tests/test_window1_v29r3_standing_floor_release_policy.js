"use strict";

const assert = require("assert");
const {
  DWELL_SECONDS, QUANTITY, MAX_SPREAD_CENTS, armUncapturedSide, releaseOnQualifyingFloor,
} = require("../analysis/window1_v29r3_standing_floor_release_policy.js");

assert.strictEqual(DWELL_SECONDS, 10);
assert.strictEqual(QUANTITY, 5);
assert.strictEqual(MAX_SPREAD_CENTS, 1);
const armed = armUncapturedSide({ incumbentActive: false, firstFillCents: 42, ownLiveAskCents: 56 });
assert.strictEqual(armed.aim_cents, 56);
assert.strictEqual(armed.pair_cap_cents, 57);
assert.strictEqual(armUncapturedSide({ incumbentActive: true, firstFillCents: 42, ownLiveAskCents: 56 }).state, "STAND_DOWN");
const base = { armed, bid: 55, ask: 56, spread: 1, askDwellSeconds: 14400, displayedAskSize: 5, standingAtArm: true, strictlyLaterReceipt: false };
assert.strictEqual(releaseOnQualifyingFloor(base).state, "PLACE");
assert.strictEqual(releaseOnQualifyingFloor(base).release_origin, "STANDING_AT_ARM");
assert.strictEqual(releaseOnQualifyingFloor({ ...base, standingAtArm: false, strictlyLaterReceipt: true }).release_origin, "POST_ARM_FORMATION");
assert.strictEqual(releaseOnQualifyingFloor({ ...base, bid: 57, spread: -1 }).state, "PLACE");
assert.strictEqual(releaseOnQualifyingFloor({ ...base, bid: 57, spread: -1 }).crossed_or_locked_maximal_urgency, true);
assert.strictEqual(releaseOnQualifyingFloor({ ...base, bid: 57, spread: -1, displayedAskSize: 2 }).state, "PLACE");
assert.strictEqual(releaseOnQualifyingFloor({ ...base, bid: 57, spread: -1, displayedAskSize: 2 }).ordinary_five_contract_displayed_ask_gate_bypassed_by_crossed_urgency, true);
assert.strictEqual(releaseOnQualifyingFloor({ ...base, bid: 54, spread: 2 }).reason, "SPREAD_ABOVE_ONE_CENT");
assert.strictEqual(releaseOnQualifyingFloor({ ...base, askDwellSeconds: 9 }).reason, "QUALIFYING_ASK_DWELL_BELOW_TEN_SECONDS");
assert.strictEqual(releaseOnQualifyingFloor({ ...base, displayedAskSize: 4 }).reason, "QUALIFYING_ASK_CAPACITY_BELOW_FIVE");
assert.strictEqual(releaseOnQualifyingFloor({ ...base, bid: 56, spread: 0 }).state, "PLACE");
assert.strictEqual(releaseOnQualifyingFloor({ ...base, standingAtArm: false, strictlyLaterReceipt: false }).reason, "NEITHER_ARM_SNAPSHOT_NOR_STRICTLY_LATER_RECEIPT");

process.stdout.write("window1 V29-R3 standing-floor policy tests: PASS (18 assertions)\n");
