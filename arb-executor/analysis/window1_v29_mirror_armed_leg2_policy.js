"use strict";

function mirrorArmDecision({ incumbentHandled, siblingDiscountAuthority, closeBar, lawfulFloorBar, firstFillCents }) {
  if (incumbentHandled) return { state: "ABSTAIN", reason: "V28_ALREADY_HANDLES_LEG_BYTE_IDENTICAL", aim_cents: null };
  if (siblingDiscountAuthority !== "BOUND") return { state: "ABSTAIN", reason: "SIBLING_CREDITED_DISCOUNT_AUTHORITY_NOT_BOUND", aim_cents: null };
  if (!Number.isInteger(closeBar)) return { state: "ABSTAIN", reason: "DECISION_TIME_OWN_CLOSE_BAR_NOT_BOUND", aim_cents: null };
  if (!Number.isInteger(lawfulFloorBar)) return { state: "ABSTAIN", reason: "DECISION_TIME_OWN_LAWFUL_FLOOR_BAR_NOT_BOUND", aim_cents: null };
  if (!Number.isInteger(firstFillCents)) throw new Error("integer first fill required");
  const aim = Math.min(99 - firstFillCents, lawfulFloorBar, closeBar - 1);
  if (aim < 1 || aim > 99) return { state: "ABSTAIN", reason: "STRICT_JOINT_AIM_OUT_OF_RANGE", aim_cents: null };
  return { state: "HOLD", reason: "MIRROR_ARMED_AWAITING_OWN_BOOK_DECLINE_COHERENT_ORDINAL", aim_cents: aim, no_clock_inputs: true };
}

function mirrorReleaseDecision({ armed, bid, ask, spread, askDwellSeconds, displayedAskSize, coherentOrdinalResolved }) {
  if (armed?.state !== "HOLD") return { state: "ABSTAIN", reason: "MIRROR_NOT_ARMED", price_cents: null };
  for (const [name, value] of Object.entries({ bid, ask, spread, askDwellSeconds, displayedAskSize })) if (!Number.isFinite(value)) throw new Error(`${name} finite required`);
  if (!(bid <= ask && spread === ask - bid)) return { state: "HOLD", reason: "OWN_BOOK_INVALID_OR_CROSSED", price_cents: null };
  if (!coherentOrdinalResolved) return { state: "HOLD", reason: "OWN_DECLINE_COHERENT_ORDINAL_NOT_RESOLVED", price_cents: null };
  if (spread !== 1 || askDwellSeconds < 10 || displayedAskSize < 5) return { state: "HOLD", reason: "SPREAD_DWELL_OR_CAPACITY_NOT_LAWFUL", price_cents: null };
  if (ask > armed.aim_cents) return { state: "HOLD", reason: "OWN_BOOK_HAS_NOT_DECLINED_TO_AIM", price_cents: null };
  return { state: "PLACE", reason: "OWN_BOOK_DECLINE_REACHED_AIM_WITH_COHERENT_ORDINAL_AND_LAWFUL_READ", price_cents: ask, pair_cap_preserved: ask <= armed.aim_cents, no_clock_inputs: true };
}

module.exports = { mirrorArmDecision, mirrorReleaseDecision };
