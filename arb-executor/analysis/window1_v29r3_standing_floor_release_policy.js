"use strict";

const DWELL_SECONDS = 10;
const QUANTITY = 5;
const MAX_SPREAD_CENTS = 1;

function armUncapturedSide({ incumbentActive, firstFillCents, ownLiveAskCents }) {
  if (incumbentActive) return {
    state: "STAND_DOWN",
    reason: "R2_INCUMBENT_ACTIVE_OR_CREDITED_FIRST",
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
    reason: "UNCAPTURED_SIBLING_ARMED_EVALUATE_STANDING_THEN_FUTURE_FLOORS",
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
  standingAtArm,
  strictlyLaterReceipt,
}) {
  if (armed?.state !== "HOLD") return {
    state: "STAND_DOWN", reason: "UNCAPTURED_SIDE_NOT_ARMED", price_cents: null,
  };
  for (const [name, value] of Object.entries({ bid, ask, spread, askDwellSeconds, displayedAskSize })) {
    if (!Number.isFinite(value)) throw new Error(`${name} finite required`);
  }
  if (!(standingAtArm || strictlyLaterReceipt)) return {
    state: "HOLD", reason: "NEITHER_ARM_SNAPSHOT_NOR_STRICTLY_LATER_RECEIPT", price_cents: null,
  };
  if (ask > armed.aim_cents) return {
    state: "HOLD", reason: "OWN_ASK_ABOVE_ARMED_AIM", price_cents: null,
  };
  const crossedOrLocked = bid >= ask;
  if (!crossedOrLocked && spread !== ask - bid) return {
    state: "HOLD", reason: "OWN_BOOK_SPREAD_IDENTITY_INVALID", price_cents: null,
  };
  if (!crossedOrLocked && spread > MAX_SPREAD_CENTS) return {
    state: "HOLD", reason: "SPREAD_ABOVE_ONE_CENT", price_cents: null,
  };
  if (askDwellSeconds < DWELL_SECONDS) return {
    state: "HOLD", reason: "QUALIFYING_ASK_DWELL_BELOW_TEN_SECONDS", price_cents: null,
  };
  if (!crossedOrLocked && displayedAskSize < QUANTITY) return {
    state: "HOLD", reason: "QUALIFYING_ASK_CAPACITY_BELOW_FIVE", price_cents: null,
  };
  return {
    state: "PLACE",
    reason: standingAtArm ? "STANDING_QUALIFYING_FLOOR_RELEASED_AT_ARM" : "POST_ARM_QUALIFYING_FLOOR_RELEASED",
    release_origin: standingAtArm ? "STANDING_AT_ARM" : "POST_ARM_FORMATION",
    price_cents: ask,
    fill_class: "PROVEN_TAKER_DISPLAYED_ASK_SIZE_AT_SUBMISSION",
    pair_cap_preserved: ask <= armed.pair_cap_cents,
    crossed_or_locked_maximal_urgency: crossedOrLocked,
    ordinary_five_contract_displayed_ask_gate_bypassed_by_crossed_urgency: crossedOrLocked && displayedAskSize < QUANTITY,
    evaluation_cadence: "ARM_SNAPSHOT_THEN_EVERY_CAUSAL_OWN_BOOK_RECEIPT",
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
