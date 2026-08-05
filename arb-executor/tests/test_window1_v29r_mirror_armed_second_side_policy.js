"use strict";

const assert = require("assert");
const {
  DWELL_SECONDS, QUANTITY, MAX_SPREAD_CENTS, armOtherSide, releaseOtherSide,
} = require("../analysis/window1_v29r_mirror_armed_second_side_policy.js");

assert.strictEqual(DWELL_SECONDS, 10);
assert.strictEqual(QUANTITY, 5);
assert.strictEqual(MAX_SPREAD_CENTS, 1);
assert.strictEqual(armOtherSide({ incumbentActive: true, firstFillCents: 40, ownLiveAskCents: 55 }).state, "ABSTAIN");
assert.deepStrictEqual(
  armOtherSide({ incumbentActive: false, firstFillCents: 40, ownLiveAskCents: 65 }),
  {
    state: "HOLD",
    reason: "OTHER_SIDE_ARMED_AWAITING_OWN_LATER_COHERENT_DECLINE",
    aim_cents: 59,
    pair_cap_cents: 59,
    aim_formula: "min(99 - first_fill_cents, own_live_ask_cents_at_arm)",
    audited_close_policy_role: "NONE_GRADING_ONLY",
    elapsed_time_inputs: [],
  },
);
assert.strictEqual(armOtherSide({ incumbentActive: false, firstFillCents: 40, ownLiveAskCents: null }).reason, "OWN_LAWFUL_LIVE_BOOK_FLOOR_NOT_AVAILABLE_AT_ARM_TIME");
assert.throws(() => armOtherSide({ incumbentActive: false, firstFillCents: 40.5, ownLiveAskCents: 55 }), /integer first fill/);

const armed = armOtherSide({ incumbentActive: false, firstFillCents: 40, ownLiveAskCents: 55 });
const base = { armed, bid: 53, ask: 54, spread: 1, askDwellSeconds: 10, displayedAskSize: 5, strictlyLaterReceipt: true, ownLaterQualifiedDescent: true, coherentOrdinalResolved: true };
assert.strictEqual(releaseOtherSide({ ...base, strictlyLaterReceipt: false }).reason, "ARM_RECEIPT_CANNOT_RELEASE");
assert.strictEqual(releaseOtherSide({ ...base, ownLaterQualifiedDescent: false }).reason, "OWN_LATER_DECLINE_NOT_OBSERVED");
assert.strictEqual(releaseOtherSide({ ...base, coherentOrdinalResolved: false }).reason, "OWN_DECLINE_COHERENT_ORDINAL_NOT_RESOLVED");
assert.strictEqual(releaseOtherSide({ ...base, askDwellSeconds: 9 }).reason, "SPREAD_DWELL_OR_CAPACITY_NOT_LAWFUL");
assert.strictEqual(releaseOtherSide({ ...base, bid: 52, ask: 54, spread: 2 }).reason, "SPREAD_DWELL_OR_CAPACITY_NOT_LAWFUL");
assert.strictEqual(releaseOtherSide({ ...base, displayedAskSize: 4 }).reason, "SPREAD_DWELL_OR_CAPACITY_NOT_LAWFUL");
assert.strictEqual(releaseOtherSide({ ...base, bid: 55, ask: 56, spread: 1 }).reason, "OWN_BOOK_HAS_NOT_DECLINED_TO_AIM");
assert.deepStrictEqual(releaseOtherSide(base), {
  state: "PLACE",
  reason: "OWN_LATER_DECLINE_REACHED_AIM_WITH_COHERENT_ORDINAL_AND_LAWFUL_READ",
  price_cents: 54,
  fill_class: "PROVEN_TAKER_DISPLAYED_ASK_SIZE_AT_SUBMISSION",
  pair_cap_preserved: true,
  evaluation_cadence: "EVERY_CAUSAL_OWN_BOOK_RECEIPT_IN_EVENT_ORDER",
  elapsed_time_inputs: [],
});

process.stdout.write("window1 V29-R mirror-armed second-side policy tests: PASS (15 assertions)\n");
