"use strict";

const v32 = require("./window1_v32_no_chase_state_machine.js");
const r3 = require("./window1_v29r3_standing_floor_release_policy.js");

function lawfulCent(value) {
  return Number.isInteger(value) && value >= 1 && value <= 99;
}

function discountEvidenceBound({ runningTradeLow = null, runningQualifyingAskLow = null }) {
  const values = [runningTradeLow, runningQualifyingAskLow].filter(lawfulCent);
  return values.length ? Math.min(...values) : null;
}

function walkingRestTarget({ bid, previousTarget = null, pairCap = null, runningTradeLow = null, runningQualifyingAskLow = null }) {
  if (!Number.isInteger(bid)) throw new Error("bid integer required");
  let target = bid - 1;
  const evidenceBound = discountEvidenceBound({ runningTradeLow, runningQualifyingAskLow });
  if (lawfulCent(evidenceBound)) target = Math.min(target, evidenceBound);
  if (lawfulCent(previousTarget)) target = Math.min(target, previousTarget);
  if (Number.isInteger(pairCap)) target = Math.min(target, pairCap);
  return lawfulCent(target) ? target : null;
}

function r3QualifiedTake(book) {
  if (!Number.isInteger(book?.bid) || !Number.isInteger(book?.ask) || !Number.isFinite(book.ask_dwell_seconds)) return false;
  if (book.ask_dwell_seconds < r3.DWELL_SECONDS) return false;
  if (book.bid >= book.ask) return true;
  return book.spread === book.ask - book.bid && book.spread <= r3.MAX_SPREAD_CENTS && book.top_ask_size >= r3.QUANTITY;
}

function decide({ state, book, activeTarget = null, pairCap = null, runningTradeLow = null, runningQualifyingAskLow = null }) {
  if (!["FALLING", "RISING", "SETTLED"].includes(state)) throw new Error("valid state required");
  const restTarget = walkingRestTarget({ bid: book.bid, previousTarget: activeTarget, pairCap, runningTradeLow, runningQualifyingAskLow });
  if (activeTarget === null && restTarget !== null) {
    return { action: "PLACE_REST", target_cents: restTarget, reason: "FORMATION_STANDING_REST_ONE_CENT_UNDER_BID_BOUNDED_BY_CAUSAL_DISCOUNT_EVIDENCE" };
  }
  if (state === "FALLING" && restTarget !== null && restTarget < activeTarget) {
    return { action: "REPRICE_REST_DOWN", target_cents: restTarget, reason: "FALLING_WALK_DOWN_NEVER_CHASE_UP" };
  }
  if (state === "SETTLED" && r3QualifiedTake(book)) {
    if (Number.isInteger(pairCap) && book.ask > pairCap) {
      return { action: "HOLD_REST", target_cents: activeTarget, reason: "SETTLED_ASK_ABOVE_PAIR_CAP" };
    }
    return { action: "TAKE", target_cents: book.ask, reason: "R3_QUALIFIED_SETTLED_FLOOR_TAKE_PATH" };
  }
  return {
    action: "HOLD_REST",
    target_cents: activeTarget,
    reason: state === "RISING" ? "RISING_HOLD_THROUGH_CLIMB" : state === "FALLING" ? "FALLING_REST_ALREADY_AT_CAUSAL_TARGET" : "SETTLED_FLOOR_NOT_TAKE_QUALIFIED",
  };
}

function strictMakerFill(order, print) {
  return Boolean(order) && lawfulCent(order.target_cents) && print.ts > order.action_ts &&
    print.taker_side === "no" && Number.isFinite(print.size) && print.size >= v32.QUALIFIED_SIZE_MIN &&
    Number.isInteger(print.price) && print.price <= order.target_cents;
}

function censusPricedFill(order, print) {
  if (!order || !lawfulCent(order.target_cents) || !(print.ts > order.action_ts) || print.taker_side !== "no" || !(print.size > 0) || !Number.isInteger(print.price)) return null;
  if (print.price <= order.target_cents && print.size >= v32.QUALIFIED_SIZE_MIN) return { fill: true, class: "PROVEN_MAKER_SELLER_AGGRESSED_PRINT_SIZE_FIVE_AT_OR_BELOW_REST", gap_cents: print.price - order.target_cents };
  if (print.price === order.target_cents + 1) return { fill: true, class: "CENSUS_PRICED_ONE_CENT_RESIDENCY_CONVERSION", gap_cents: 1 };
  return null;
}

module.exports = {
  ...v32,
  lawfulCent,
  discountEvidenceBound,
  walkingRestTarget,
  r3QualifiedTake,
  decide,
  strictMakerFill,
  censusPricedFill,
};
