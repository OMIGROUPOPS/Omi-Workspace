"use strict";

const assert = require("assert");
const {
  DWELL_SECONDS, QUANTITY, MAX_SPREAD_CENTS, armUncapturedSide, releaseOnQualifyingFloor,
} = require("../analysis/window1_v29r2_mirror_armed_uncaptured_side_policy.js");

assert.strictEqual(DWELL_SECONDS, 10);
assert.strictEqual(QUANTITY, 5);
assert.strictEqual(MAX_SPREAD_CENTS, 1);
assert.strictEqual(armUncapturedSide({ incumbentActive: true, firstFillCents: 40, ownLiveAskCents: 55 }).state, "STAND_DOWN");
assert.deepStrictEqual(
  armUncapturedSide({ incumbentActive: false, firstFillCents: 40, ownLiveAskCents: 65 }),
  {
    state: "HOLD",
    reason: "UNCAPTURED_SIBLING_ARMED_AWAITING_QUALIFYING_OWN_BOOK_FLOOR",
    aim_cents: 59,
    pair_cap_cents: 59,
    aim_formula: "min(99 - first_fill_cents, own_live_ask_cents_at_arm)",
    audited_close_policy_role: "NONE_GRADING_ONLY",
    elapsed_time_inputs: [],
  },
);
assert.strictEqual(armUncapturedSide({ incumbentActive: false, firstFillCents: 40, ownLiveAskCents: null }).reason, "OWN_LAWFUL_LIVE_BOOK_FLOOR_NOT_AVAILABLE_AT_ARM_TIME");
assert.throws(() => armUncapturedSide({ incumbentActive: false, firstFillCents: 40.5, ownLiveAskCents: 55 }), /integer first fill/);

const armed = armUncapturedSide({ incumbentActive: false, firstFillCents: 40, ownLiveAskCents: 55 });
const base = { armed, bid: 53, ask: 54, spread: 1, askDwellSeconds: 10, displayedAskSize: 5, strictlyLaterReceipt: true };
assert.strictEqual(releaseOnQualifyingFloor({ ...base, strictlyLaterReceipt: false }).reason, "ARM_RECEIPT_CANNOT_RELEASE");
assert.strictEqual(releaseOnQualifyingFloor({ ...base, ask: 56, bid: 55 }).reason, "OWN_ASK_ABOVE_ARMED_AIM");
assert.strictEqual(releaseOnQualifyingFloor({ ...base, bid: 52, spread: 2 }).reason, "SPREAD_ABOVE_ONE_CENT");
assert.strictEqual(releaseOnQualifyingFloor({ ...base, askDwellSeconds: 9 }).reason, "QUALIFYING_ASK_DWELL_BELOW_TEN_SECONDS");
assert.strictEqual(releaseOnQualifyingFloor({ ...base, displayedAskSize: 4 }).reason, "QUALIFYING_ASK_CAPACITY_BELOW_FIVE");
assert.deepStrictEqual(releaseOnQualifyingFloor(base), {
  state: "PLACE",
  reason: "QUALIFYING_OWN_BOOK_FLOOR_FORMED_AT_OR_BELOW_ARMED_AIM",
  price_cents: 54,
  fill_class: "PROVEN_TAKER_DISPLAYED_ASK_SIZE_AT_SUBMISSION",
  pair_cap_preserved: true,
  evaluation_cadence: "EVERY_CAUSAL_OWN_BOOK_RECEIPT_IN_EVENT_ORDER",
  elapsed_time_inputs: [],
  coherent_decline_ordinal_role: "LOGGED_CONFIRMATION_ONLY_NEVER_GATE",
});
assert.strictEqual(releaseOnQualifyingFloor({ ...base, ordinalConfirmation: "ALL_LOWER" }).state, "PLACE");

process.stdout.write("window1 V29-R2 uncaptured-side policy tests: PASS (17 assertions)\n");
