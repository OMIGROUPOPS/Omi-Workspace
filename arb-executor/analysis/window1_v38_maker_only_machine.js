"use strict";

// V38 is intentionally self-contained.  In particular it does not import or
// expose any V34/V35/V36 take decision.  The only entry action is a resting
// bid, and the only state changes occur on exchange book/print receipts.

const LOOKBACK_SECONDS = 300;
const PRESSURE_RISING_MIN = 0.60;
const PRESSURE_FALLING_MAX = 0.40;
const QUALIFIED_SPREAD_MAX_CENTS = 1;
const QUALIFIED_DWELL_MIN_SECONDS = 10;
const QUALIFIED_SIZE_MIN = 5;
const PULSE_REVISIT_MIN = 2;

function lawfulCent(value) {
  return Number.isInteger(value) && value >= 1 && value <= 99;
}

function quotePathState(evidence, now) {
  if (!Number.isFinite(now)) throw new Error("now finite required");
  const live = evidence.filter((row) => Number.isFinite(row.ts) && row.ts <= now && row.ts >= now - LOOKBACK_SECONDS);
  if (!live.length) return { state: "SETTLED", receipt: null, evidence: "NO_DIRECTIONAL_QUOTE_OR_PRINT_EVIDENCE" };
  const latest = [...live].sort((a, b) => b.ts - a.ts || b.ordinal - a.ordinal)[0];
  return { state: latest.direction, receipt: latest.receipt, evidence: latest.kind };
}

function pressureState(depthRatio) {
  if (!Number.isFinite(depthRatio)) throw new Error("depth_ratio finite required");
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

function qualifyingAsk(row) {
  return Number.isInteger(row?.bid) && Number.isInteger(row?.ask) &&
    Number.isInteger(row.spread) && row.spread >= 0 && row.spread <= QUALIFIED_SPREAD_MAX_CENTS &&
    Number.isFinite(row.ask_dwell_seconds) && row.ask_dwell_seconds >= QUALIFIED_DWELL_MIN_SECONDS &&
    Number.isFinite(row.top_ask_size) && row.top_ask_size >= QUALIFIED_SIZE_MIN;
}

function trimPulseVisits(visits, now) {
  return visits.filter((row) => row.ts <= now && row.ts >= now - LOOKBACK_SECONDS);
}

function trailingPulseFloor(visits, now) {
  const live = trimPulseVisits(visits, now);
  const counts = new Map();
  for (const row of live) counts.set(row.ask, (counts.get(row.ask) || 0) + 1);
  const eligible = [...counts.entries()].filter(([, count]) => count >= PULSE_REVISIT_MIN).map(([ask]) => ask);
  return {
    floor_cents: eligible.length ? Math.min(...eligible) : null,
    live_visits: live.length,
    eligible_levels: eligible.sort((a, b) => a - b).map((ask) => ({ ask_cents: ask, visits: counts.get(ask) })),
  };
}

function capTarget(target, pairCap) {
  if (!lawfulCent(target)) return null;
  const capped = Number.isInteger(pairCap) ? Math.min(target, pairCap) : target;
  return lawfulCent(capped) ? capped : null;
}

function fallingTarget({ bid, activeTarget = null, pairCap = null }) {
  if (!Number.isInteger(bid)) throw new Error("bid integer required");
  let target = bid - 1;
  if (lawfulCent(activeTarget)) target = Math.min(target, activeTarget);
  return capTarget(target, pairCap);
}

function settledTarget({ bid, pairCap = null }) {
  if (!Number.isInteger(bid)) throw new Error("bid integer required");
  return capTarget(bid - 1, pairCap);
}

function risingTarget({ pulseFloor = null, pairCap = null }) {
  return capTarget(pulseFloor, pairCap);
}

function desiredTarget({ state, book, activeTarget = null, pairCap = null, pulseFloor = null }) {
  if (state === "FALLING") return fallingTarget({ bid: book.bid, activeTarget, pairCap });
  if (state === "SETTLED") return settledTarget({ bid: book.bid, pairCap });
  if (state === "RISING") return risingTarget({ pulseFloor, pairCap });
  throw new Error("valid state required");
}

function decide({ state, book, activeTarget = null, pairCap = null, pulseFloor = null }) {
  const target = desiredTarget({ state, book, activeTarget, pairCap, pulseFloor });
  if (state === "RISING" && target === null) {
    return {
      action: "HOLD_REST",
      target_cents: activeTarget,
      reason: lawfulCent(activeTarget) ? "RISING_HOLD_EXISTING_REST_NO_REVISITED_PULSE_FLOOR" : "RISING_NO_REVISITED_PULSE_FLOOR",
    };
  }
  if (target === null) {
    return { action: lawfulCent(activeTarget) ? "CANCEL_REST" : "HOLD_REST", target_cents: null, reason: "NO_LAWFUL_REST_TARGET" };
  }
  // A new bid at the standing ask would be a take.  V38 waits until the ask
  // leaves the pulse level, then rests at that previously observed floor.
  if (!lawfulCent(activeTarget) && target >= book.ask) {
    return { action: "HOLD_REST", target_cents: null, reason: "POST_ONLY_REST_WOULD_CROSS_STANDING_ASK" };
  }
  if (!lawfulCent(activeTarget)) {
    return { action: "PLACE_REST", target_cents: target, reason: state === "RISING" ? "RISING_REST_AT_REVISITED_TRAILING_PULSE_FLOOR" : state === "FALLING" ? "FALLING_V36_NO_CHASE_REST" : "SETTLED_BID_MINUS_ONE_TRACKING" };
  }
  if (target !== activeTarget) {
    return {
      action: "REPRICE_REST",
      target_cents: target,
      direction: target > activeTarget ? "UP" : "DOWN",
      reason: state === "RISING" ? "RISING_REANCHOR_TO_REVISITED_TRAILING_PULSE_FLOOR" : state === "FALLING" ? "FALLING_V36_NO_CHASE_WALK_DOWN" : "SETTLED_BID_MINUS_ONE_TRACKING",
    };
  }
  return { action: "HOLD_REST", target_cents: activeTarget, reason: state === "RISING" ? "RISING_REST_ALREADY_AT_TRAILING_PULSE_FLOOR" : state === "FALLING" ? "FALLING_V36_NO_CHASE_REST_HELD" : "SETTLED_BID_MINUS_ONE_REST_HELD" };
}

function strictPrintCross(order, print) {
  return Boolean(order) && lawfulCent(order.target_cents) && print.ts > order.action_ts &&
    print.taker_side === "no" && Number.isFinite(print.size) && print.size >= QUALIFIED_SIZE_MIN &&
    Number.isInteger(print.price) && print.price <= order.target_cents;
}

function tradedAtLevel(order, print) {
  return Boolean(order) && lawfulCent(order.target_cents) && print.ts > order.action_ts &&
    Number.isFinite(print.size) && print.size > 0 && Number.isInteger(print.price) && print.price <= order.target_cents;
}

function quoteTouch(order, book) {
  return Boolean(order) && lawfulCent(order.target_cents) && book.ts > order.action_ts &&
    qualifyingAsk(book) && book.ask <= order.target_cents;
}

module.exports = {
  LOOKBACK_SECONDS,
  PRESSURE_RISING_MIN,
  PRESSURE_FALLING_MAX,
  QUALIFIED_SPREAD_MAX_CENTS,
  QUALIFIED_DWELL_MIN_SECONDS,
  QUALIFIED_SIZE_MIN,
  PULSE_REVISIT_MIN,
  lawfulCent,
  quotePathState,
  pressureState,
  combineState,
  qualifyingAsk,
  trimPulseVisits,
  trailingPulseFloor,
  fallingTarget,
  settledTarget,
  risingTarget,
  desiredTarget,
  decide,
  strictPrintCross,
  tradedAtLevel,
  quoteTouch,
};
