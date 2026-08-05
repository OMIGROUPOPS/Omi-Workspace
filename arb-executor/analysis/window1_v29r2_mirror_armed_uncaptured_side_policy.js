"use strict";

const DWELL_SECONDS = 10;
const QUANTITY = 5;
const MAX_SPREAD_CENTS = 1;

function armUncapturedSide({ incumbentActive, firstFillCents, ownLiveAskCents }) {
  if (incumbentActive) return {
    state: "STAND_DOWN",
    reason: "V28_INCUMBENT_ACTIVE_OR_CREDITED_FIRST",
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
    reason: "UNCAPTURED_SIBLING_ARMED_AWAITING_QUALIFYING_OWN_BOOK_FLOOR",
    aim_cents: aim,
    pair_cap_cents: pairCap,
    aim_formula: "min(99 - first_fill_cents, own_live_ask_cents_at_arm)",
    audited_close_policy_role: "NONE_GRADING_ONLY",
    elapsed_time_inputs: [],
  };
}

function releaseOnQualifyingFloor({
  armed,
  bid,
  ask,
  spread,
  askDwellSeconds,
  displayedAskSize,
  strictlyLaterReceipt,
}) {
  if (armed?.state !== "HOLD") return {
    state: "STAND_DOWN", reason: "UNCAPTURED_SIDE_NOT_ARMED", price_cents: null,
  };
  for (const [name, value] of Object.entries({ bid, ask, spread, askDwellSeconds, displayedAskSize })) {
    if (!Number.isFinite(value)) throw new Error(`${name} finite required`);
  }
  if (!(bid <= ask && spread === ask - bid)) return {
    state: "HOLD", reason: "OWN_BOOK_INVALID_OR_CROSSED", price_cents: null,
  };
  if (!strictlyLaterReceipt) return {
    state: "HOLD", reason: "ARM_RECEIPT_CANNOT_RELEASE", price_cents: null,
  };
  if (ask > armed.aim_cents) return {
    state: "HOLD", reason: "OWN_ASK_ABOVE_ARMED_AIM", price_cents: null,
  };
  if (spread > MAX_SPREAD_CENTS) return {
    state: "HOLD", reason: "SPREAD_ABOVE_ONE_CENT", price_cents: null,
  };
  if (askDwellSeconds < DWELL_SECONDS) return {
    state: "HOLD", reason: "QUALIFYING_ASK_DWELL_BELOW_TEN_SECONDS", price_cents: null,
  };
  if (displayedAskSize < QUANTITY) return {
    state: "HOLD", reason: "QUALIFYING_ASK_CAPACITY_BELOW_FIVE", price_cents: null,
  };
  return {
    state: "PLACE",
    reason: "QUALIFYING_OWN_BOOK_FLOOR_FORMED_AT_OR_BELOW_ARMED_AIM",
    price_cents: ask,
    fill_class: "PROVEN_TAKER_DISPLAYED_ASK_SIZE_AT_SUBMISSION",
    pair_cap_preserved: ask <= armed.pair_cap_cents,
    evaluation_cadence: "EVERY_CAUSAL_OWN_BOOK_RECEIPT_IN_EVENT_ORDER",
    elapsed_time_inputs: [],
    coherent_decline_ordinal_role: "LOGGED_CONFIRMATION_ONLY_NEVER_GATE",
  };
}

module.exports = {
  DWELL_SECONDS,
  QUANTITY,
  MAX_SPREAD_CENTS,
  armUncapturedSide,
  releaseOnQualifyingFloor,
};
