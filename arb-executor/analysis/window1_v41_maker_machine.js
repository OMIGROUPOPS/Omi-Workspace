"use strict";

// V41 is a maker-only placement machine. It consumes V36 only for the
// incumbent receipt-causal state/read laws; no take function is exported or
// called. One post-only rest exists per leg from its first two-sided book.

const v36 = require("./window1_v36_state_directional_rest_mature_floor.js");

const LOOKBACK_SECONDS = 300;
const PERSISTENT_LEVEL_SECONDS = 300;
const PULSE_REVISIT_MIN = 2;
const QUALIFIED_SIZE_MIN = v36.QUALIFIED_SIZE_MIN;

function lawfulCent(value) {
  return Number.isInteger(value) && value >= 1 && value <= 99;
}

function trimPulseVisits(visits, now) {
  return visits.filter((row) => row.ts <= now && row.ts >= now - LOOKBACK_SECONDS);
}

function trailingPulseFloor(visits, now) {
  const live = trimPulseVisits(visits, now), counts = new Map();
  for (const row of live) counts.set(row.ask, (counts.get(row.ask) || 0) + 1);
  const eligible = [...counts].filter(([, count]) => count >= PULSE_REVISIT_MIN).map(([ask]) => ask).sort((a, b) => a - b);
  return { floor_cents: eligible[0] ?? null, live_visits: live.length, eligible_levels: eligible.map((ask) => ({ ask_cents: ask, visits: counts.get(ask) })) };
}

function postOnlyBound(target, book, pairCap = null) {
  if (!lawfulCent(target) || !Number.isInteger(book?.ask)) return null;
  let bounded = Math.min(target, book.ask - 1);
  if (Number.isInteger(pairCap)) bounded = Math.min(bounded, pairCap);
  return lawfulCent(bounded) ? bounded : null;
}

function persistenceJoinUpdate({ state, bid, residencySeconds, currentJoinLevel = null }) {
  if (state !== "RISING" || !lawfulCent(bid) || !Number.isFinite(residencySeconds) || residencySeconds < PERSISTENT_LEVEL_SECONDS) {
    return { armed: false, changed: false, level_cents: currentJoinLevel };
  }
  return { armed: true, changed: currentJoinLevel !== bid, level_cents: bid };
}

function placementTarget({ state, book, activeTarget = null, pairCap = null, persistentJoinLevel = null, wtaInverseFalling = false, pulseFloor = null, causalOwnReachLow = null }) {
  let target;
  let authority;
  if (state === "RISING" && lawfulCent(persistentJoinLevel)) {
    target = persistentJoinLevel;
    authority = "V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1";
  } else if (wtaInverseFalling) {
    const candidates = [pulseFloor, causalOwnReachLow].filter(lawfulCent);
    target = candidates.length ? Math.min(...candidates) : v36.stateDirectionalRestTarget({ state, bid: book.bid, activeTarget, pairCap });
    authority = candidates.length ? "V41_WTA_OTHER_EXPRESSION_FALLING_HOLD" : "V41_WTA_HOLD_ABSTAINS_TO_INCUMBENT_TRACKER";
  } else {
    target = v36.stateDirectionalRestTarget({ state, bid: book.bid, activeTarget, pairCap });
    authority = state === "FALLING" ? "V41_V36_FALLING_NO_CHASE" : state === "SETTLED" ? "V41_V36_SETTLED_BID_MINUS_ONE_TRACKER" : "V41_RISING_TRACKER_UNTIL_PERSISTENT_JOIN_ARMS";
  }
  const bounded = postOnlyBound(target, book, pairCap);
  return { target_cents: bounded, unbounded_target_cents: target, authority, sanity_bound_applied: Number.isInteger(target) && bounded !== target };
}

function decide(inputs) {
  const placement = placementTarget(inputs);
  const activeTarget = inputs.activeTarget;
  const target = placement.target_cents;
  if (target === null) return { action: lawfulCent(activeTarget) ? "CANCEL_REST" : "HOLD_REST", target_cents: null, reason: "V41_NO_LAWFUL_POST_ONLY_REST_TARGET", placement };
  if (!lawfulCent(activeTarget)) return { action: "PLACE_REST", target_cents: target, reason: placement.authority, placement };
  if (target !== activeTarget) return { action: "REPRICE_REST", target_cents: target, direction: target > activeTarget ? "UP" : "DOWN", reason: placement.authority, placement };
  return { action: "HOLD_REST", target_cents: activeTarget, reason: `${placement.authority}_ALREADY_AT_TARGET`, placement };
}

function strictPrintCross(order, print) {
  return Boolean(order) && lawfulCent(order.target_cents) && print.ts > order.action_ts && print.taker_side === "no" && Number.isFinite(print.size) && print.size >= QUALIFIED_SIZE_MIN && Number.isInteger(print.price) && print.price <= order.target_cents;
}

function tradedAtLevel(order, print) {
  return Boolean(order) && lawfulCent(order.target_cents) && print.ts > order.action_ts && Number.isFinite(print.size) && print.size > 0 && Number.isInteger(print.price) && print.price <= order.target_cents;
}

function quoteTouch(order, book) {
  return Boolean(order) && lawfulCent(order.target_cents) && book.ts > order.action_ts && v36.qualifyingAskEvidence(book) && book.ask <= order.target_cents;
}

module.exports = {
  LOOKBACK_SECONDS,
  PERSISTENT_LEVEL_SECONDS,
  PULSE_REVISIT_MIN,
  QUALIFIED_SIZE_MIN,
  lawfulCent,
  quotePathState: v36.quotePathState,
  pressureState: v36.pressureState,
  combineState: v36.combineState,
  qualifyingAskEvidence: v36.qualifyingAskEvidence,
  trimPulseVisits,
  trailingPulseFloor,
  postOnlyBound,
  persistenceJoinUpdate,
  placementTarget,
  decide,
  strictPrintCross,
  tradedAtLevel,
  quoteTouch,
};
