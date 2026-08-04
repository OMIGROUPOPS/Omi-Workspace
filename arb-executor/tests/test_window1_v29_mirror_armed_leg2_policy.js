"use strict";

const assert = require("assert");
const { mirrorArmDecision, mirrorReleaseDecision } = require("../analysis/window1_v29_mirror_armed_leg2_policy.js");

assert.strictEqual(mirrorArmDecision({ incumbentHandled: true, siblingDiscountAuthority: "BOUND", closeBar: 60, lawfulFloorBar: 55, firstFillCents: 40 }).reason, "V28_ALREADY_HANDLES_LEG_BYTE_IDENTICAL");
assert.strictEqual(mirrorArmDecision({ incumbentHandled: false, siblingDiscountAuthority: "NOT_BOUND", closeBar: 60, lawfulFloorBar: 55, firstFillCents: 40 }).reason, "SIBLING_CREDITED_DISCOUNT_AUTHORITY_NOT_BOUND");
assert.strictEqual(mirrorArmDecision({ incumbentHandled: false, siblingDiscountAuthority: "BOUND", closeBar: null, lawfulFloorBar: 55, firstFillCents: 40 }).reason, "DECISION_TIME_OWN_CLOSE_BAR_NOT_BOUND");
assert.strictEqual(mirrorArmDecision({ incumbentHandled: false, siblingDiscountAuthority: "BOUND", closeBar: 60, lawfulFloorBar: null, firstFillCents: 40 }).reason, "DECISION_TIME_OWN_LAWFUL_FLOOR_BAR_NOT_BOUND");
assert.deepStrictEqual(mirrorArmDecision({ incumbentHandled: false, siblingDiscountAuthority: "BOUND", closeBar: 60, lawfulFloorBar: 55, firstFillCents: 40 }), { state: "HOLD", reason: "MIRROR_ARMED_AWAITING_OWN_BOOK_DECLINE_COHERENT_ORDINAL", aim_cents: 55, no_clock_inputs: true });
assert.strictEqual(mirrorArmDecision({ incumbentHandled: false, siblingDiscountAuthority: "BOUND", closeBar: 50, lawfulFloorBar: 55, firstFillCents: 40 }).aim_cents, 49);
assert.strictEqual(mirrorArmDecision({ incumbentHandled: false, siblingDiscountAuthority: "BOUND", closeBar: 80, lawfulFloorBar: 70, firstFillCents: 35 }).aim_cents, 64);
assert.throws(() => mirrorArmDecision({ incumbentHandled: false, siblingDiscountAuthority: "BOUND", closeBar: 80, lawfulFloorBar: 70, firstFillCents: 35.5 }), /integer first fill/);

const armed = mirrorArmDecision({ incumbentHandled: false, siblingDiscountAuthority: "BOUND", closeBar: 60, lawfulFloorBar: 55, firstFillCents: 40 });
assert.strictEqual(mirrorReleaseDecision({ armed, bid: 54, ask: 55, spread: 1, askDwellSeconds: 10, displayedAskSize: 5, coherentOrdinalResolved: false }).reason, "OWN_DECLINE_COHERENT_ORDINAL_NOT_RESOLVED");
assert.strictEqual(mirrorReleaseDecision({ armed, bid: 55, ask: 56, spread: 1, askDwellSeconds: 20, displayedAskSize: 10, coherentOrdinalResolved: true }).reason, "OWN_BOOK_HAS_NOT_DECLINED_TO_AIM");
assert.strictEqual(mirrorReleaseDecision({ armed, bid: 54, ask: 55, spread: 1, askDwellSeconds: 9, displayedAskSize: 5, coherentOrdinalResolved: true }).reason, "SPREAD_DWELL_OR_CAPACITY_NOT_LAWFUL");
assert.deepStrictEqual(mirrorReleaseDecision({ armed, bid: 54, ask: 55, spread: 1, askDwellSeconds: 10, displayedAskSize: 5, coherentOrdinalResolved: true }), { state: "PLACE", reason: "OWN_BOOK_DECLINE_REACHED_AIM_WITH_COHERENT_ORDINAL_AND_LAWFUL_READ", price_cents: 55, pair_cap_preserved: true, no_clock_inputs: true });

process.stdout.write("window1 V29 mirror-armed leg-2 policy tests: PASS (12 assertions)\n");
