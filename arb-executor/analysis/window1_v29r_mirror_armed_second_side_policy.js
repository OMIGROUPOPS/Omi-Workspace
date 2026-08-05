"use strict";

const DWELL_SECONDS = 10;
const QUANTITY = 5;
const MAX_SPREAD_CENTS = 1;

function armOtherSide({ incumbentActive, firstFillCents, ownLiveAskCents }) {
  if (incumbentActive) return {
    state: "ABSTAIN",
    reason: "V28_ALREADY_HAS_ACTIVE_OR_CREDITED_SECOND_SIDE_AT_ARM_TIME",
    aim_cents: null,
  };
  if (!Number.isInteger(firstFillCents)) throw new Error("integer first fill required");
  if (!Number.isInteger(ownLiveAskCents)) return {
    state: "ABSTAIN",
    reason: "OWN_LAWFUL_LIVE_BOOK_FLOOR_NOT_AVAILABLE_AT_ARM_TIME",
    aim_cents: null,
  };
  const pairCap = 99 - firstFillCents;
  const aim = Math.min(pairCap, ownLiveAskCents);
  if (!Number.isInteger(aim) || aim < 1 || aim > 99) return {
    state: "ABSTAIN",
    reason: "PAIR_CAP_OR_LIVE_BOOK_AIM_OUT_OF_RANGE",
    aim_cents: null,
    pair_cap_cents: pairCap,
  };
  return {
    state: "HOLD",
    reason: "OTHER_SIDE_ARMED_AWAITING_OWN_LATER_COHERENT_DECLINE",
    aim_cents: aim,
    pair_cap_cents: pairCap,
    aim_formula: "min(99 - first_fill_cents, own_live_ask_cents_at_arm)",
    audited_close_policy_role: "NONE_GRADING_ONLY",
    elapsed_time_inputs: [],
  };
}

function releaseOtherSide({
  armed,
  bid,
  ask,
  spread,
  askDwellSeconds,
  displayedAskSize,
  strictlyLaterReceipt,
  ownLaterQualifiedDescent,
  coherentOrdinalResolved,
}) {
  if (armed?.state !== "HOLD") return {
    state: "ABSTAIN", reason: "OTHER_SIDE_NOT_ARMED", price_cents: null,
  };
  for (const [name, value] of Object.entries({
    bid, ask, spread, askDwellSeconds, displayedAskSize,
  })) if (!Number.isFinite(value)) throw new Error(`${name} finite required`);
  if (!(bid <= ask && spread === ask - bid)) return {
    state: "HOLD", reason: "OWN_BOOK_INVALID_OR_CROSSED", price_cents: null,
  };
  if (!strictlyLaterReceipt) return {
    state: "HOLD", reason: "ARM_RECEIPT_CANNOT_RELEASE", price_cents: null,
  };
  if (!ownLaterQualifiedDescent) return {
    state: "HOLD", reason: "OWN_LATER_DECLINE_NOT_OBSERVED", price_cents: null,
  };
  if (!coherentOrdinalResolved) return {
    state: "HOLD", reason: "OWN_DECLINE_COHERENT_ORDINAL_NOT_RESOLVED", price_cents: null,
  };
  if (spread > MAX_SPREAD_CENTS || askDwellSeconds < DWELL_SECONDS || displayedAskSize < QUANTITY) return {
    state: "HOLD", reason: "SPREAD_DWELL_OR_CAPACITY_NOT_LAWFUL", price_cents: null,
  };
  if (ask > armed.aim_cents) return {
    state: "HOLD", reason: "OWN_BOOK_HAS_NOT_DECLINED_TO_AIM", price_cents: null,
  };
  return {
    state: "PLACE",
    reason: "OWN_LATER_DECLINE_REACHED_AIM_WITH_COHERENT_ORDINAL_AND_LAWFUL_READ",
    price_cents: ask,
    fill_class: "PROVEN_TAKER_DISPLAYED_ASK_SIZE_AT_SUBMISSION",
    pair_cap_preserved: ask <= armed.pair_cap_cents,
    evaluation_cadence: "EVERY_CAUSAL_OWN_BOOK_RECEIPT_IN_EVENT_ORDER",
    elapsed_time_inputs: [],
  };
}

module.exports = {
  DWELL_SECONDS,
  QUANTITY,
  MAX_SPREAD_CENTS,
  armOtherSide,
  releaseOtherSide,
};
