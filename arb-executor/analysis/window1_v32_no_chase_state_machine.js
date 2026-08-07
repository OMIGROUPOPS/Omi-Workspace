"use strict";

const LOOKBACK_SECONDS = 300;
const PRESSURE_RISING_MIN = 0.60;
const PRESSURE_FALLING_MAX = 0.40;
const QUALIFIED_SPREAD_MAX_CENTS = 1;
const QUALIFIED_DWELL_MIN_SECONDS = 10;
const QUALIFIED_SIZE_MIN = 5;

function finite(name, value) {
  if (!Number.isFinite(value)) throw new Error(`${name} finite required`);
  return value;
}

function integer(name, value) {
  if (!Number.isInteger(value)) throw new Error(`${name} integer required`);
  return value;
}

function quotePathState(evidence, now) {
  finite("now", now);
  const live = evidence.filter((row) => Number.isFinite(row.ts) && row.ts <= now && row.ts >= now - LOOKBACK_SECONDS);
  if (!live.length) return { state: "SETTLED", receipt: null, evidence: "NO_DIRECTIONAL_QUOTE_OR_PRINT_EVIDENCE" };
  const latest = [...live].sort((a, b) => b.ts - a.ts || b.ordinal - a.ordinal)[0];
  return { state: latest.direction, receipt: latest.receipt, evidence: latest.kind };
}

function pressureState(depthRatio) {
  finite("depth_ratio", depthRatio);
  if (depthRatio >= PRESSURE_RISING_MIN) return "RISING";
  if (depthRatio <= PRESSURE_FALLING_MAX) return "FALLING";
  return "SETTLED";
}

function combineState(quote, pressure) {
  if (!quote || !["FALLING", "RISING", "SETTLED"].includes(quote.state)) throw new Error("valid quote state required");
  if (!["FALLING", "RISING", "SETTLED"].includes(pressure)) throw new Error("valid pressure state required");
  const disagreement = quote.state !== "SETTLED" && pressure !== "SETTLED" && quote.state !== pressure;
  return {
    state: quote.state === "SETTLED" ? pressure : quote.state,
    quote_state: quote.state,
    pressure_state: pressure,
    disagreement,
    authority: quote.state === "SETTLED" ? "JUL6_DEPTH_PRESSURE" : "TRAILING_300S_QUOTE_PATH_PRIMARY",
  };
}

function qualifiedBook(row) {
  return Number.isInteger(row?.bid) && Number.isInteger(row?.ask) &&
    row.spread >= 0 && row.spread <= QUALIFIED_SPREAD_MAX_CENTS &&
    row.ask_dwell_seconds >= QUALIFIED_DWELL_MIN_SECONDS &&
    row.top_ask_size >= QUALIFIED_SIZE_MIN;
}

function fallingRestTarget({ bid, previousTarget = null, pairCap = null }) {
  integer("bid", bid);
  let target = bid - 1;
  if (Number.isInteger(previousTarget)) target = Math.min(target, previousTarget);
  if (Number.isInteger(pairCap)) target = Math.min(target, pairCap);
  return target >= 1 && target <= 99 ? target : null;
}

function decide({ state, book, activeTarget = null, pairCap = null }) {
  if (!["FALLING", "RISING", "SETTLED"].includes(state)) throw new Error("valid state required");
  if (state === "FALLING") {
    const target = fallingRestTarget({ bid: book.bid, previousTarget: activeTarget, pairCap });
    if (target === null) return { action: "HOLD", target_cents: null, reason: "NO_LAWFUL_ONE_CENT_UNDER_BID_TARGET" };
    if (target === activeTarget) return { action: "HOLD", target_cents: target, reason: "FALLING_REST_ALREADY_AT_OR_BELOW_LIVE_TARGET" };
    return { action: activeTarget === null ? "PLACE" : "REPRICE", target_cents: target, reason: "FALLING_REST_ONE_CENT_UNDER_BEST_BID_NO_UPWARD_CHASE" };
  }
  if (state === "SETTLED") {
    if (!qualifiedBook(book)) return { action: "HOLD", target_cents: activeTarget, reason: "SETTLED_BOOK_NOT_SPREAD_DWELL_SIZE_QUALIFIED" };
    if (Number.isInteger(pairCap) && book.ask > pairCap) return { action: "HOLD", target_cents: activeTarget, reason: "SETTLED_ASK_ABOVE_PAIR_CAP" };
    return { action: "TAKE", target_cents: book.ask, reason: "SETTLED_STANDING_ASK_TAKEABLE" };
  }
  return { action: "HOLD", target_cents: activeTarget, reason: "RISING_NO_CHASE_WAIT_FOR_SETTLEMENT" };
}

function sellerPrintFills(order, print) {
  if (!order || !Number.isInteger(order.target_cents)) return false;
  return print.taker_side === "no" && print.size >= QUALIFIED_SIZE_MIN && print.ts > order.action_ts && print.price <= order.target_cents;
}

module.exports = {
  LOOKBACK_SECONDS,
  PRESSURE_RISING_MIN,
  PRESSURE_FALLING_MAX,
  QUALIFIED_SPREAD_MAX_CENTS,
  QUALIFIED_DWELL_MIN_SECONDS,
  QUALIFIED_SIZE_MIN,
  quotePathState,
  pressureState,
  combineState,
  qualifiedBook,
  fallingRestTarget,
  decide,
  sellerPrintFills,
};
