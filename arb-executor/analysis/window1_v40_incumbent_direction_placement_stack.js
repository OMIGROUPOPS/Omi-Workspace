"use strict";

// V40 preserves V36's incumbent state machine and TAKE path.  It adds only
// persistent-level JOIN, the WTA inverse-FALLING deeper hold, and the
// universal post-only sanity bound.

const v36 = require("./window1_v36_state_directional_rest_mature_floor.js");

const LOOKBACK_SECONDS = 300;
const PERSISTENT_LEVEL_SECONDS = 300;
const PULSE_REVISIT_MIN = 2;

function lawfulCent(value) {
  return Number.isInteger(value) && value >= 1 && value <= 99;
}

function trimPulseVisits(visits, now) {
  return visits.filter((row) => row.ts <= now && row.ts >= now - LOOKBACK_SECONDS);
}

function trailingPulseFloor(visits, now) {
  const live = trimPulseVisits(visits, now), counts = new Map();
  for (const row of live) counts.set(row.ask, (counts.get(row.ask) || 0) + 1);
  const eligible = [...counts]
    .filter(([, count]) => count >= PULSE_REVISIT_MIN)
    .map(([ask]) => ask)
    .sort((a, b) => a - b);
  return { floor_cents: eligible[0] ?? null, live_visits: live.length, eligible_levels: eligible.map((ask) => ({ ask_cents: ask, visits: counts.get(ask) })) };
}

function postOnlyBound(target, book, pairCap = null) {
  if (!lawfulCent(target) || !Number.isInteger(book?.ask)) return null;
  let bounded = Math.min(target, book.ask - 1);
  if (Number.isInteger(pairCap)) bounded = Math.min(bounded, pairCap);
  return lawfulCent(bounded) ? bounded : null;
}

function placementTarget({ state, book, activeTarget = null, pairCap = null, persistentJoinLevel = null, wtaInverseFalling = false, pulseFloor = null, causalOwnReachLow = null }) {
  let target;
  let authority;
  if (state === "RISING" && lawfulCent(persistentJoinLevel)) {
    target = persistentJoinLevel;
    authority = "INCUMBENT_RISING_PERSISTENT_LEVEL_JOIN_300S_AND_LAST_TRADED_AT_LEVEL";
  } else if (wtaInverseFalling) {
    const candidates = [pulseFloor, causalOwnReachLow].filter(lawfulCent);
    target = candidates.length ? Math.min(...candidates) : v36.stateDirectionalRestTarget({ state, bid: book.bid, activeTarget, pairCap });
    authority = candidates.length ? "WTA_INCUMBENT_OTHER_EXPRESSION_FALLING_DEEPER_OF_PULSE_AND_CAUSAL_OWN_REACH" : "WTA_OTHER_EXPRESSION_FALLING_ABSTAINS_TO_V36_NO_CAUSAL_FLOOR";
  } else {
    target = v36.stateDirectionalRestTarget({ state, bid: book.bid, activeTarget, pairCap });
    authority = state === "FALLING" ? "V36_FALLING_NO_CHASE" : "V36_RISING_OR_SETTLED_LIVING_REST";
  }
  const bounded = postOnlyBound(target, book, pairCap);
  return { target_cents: bounded, unbounded_target_cents: target, authority, sanity_bound_applied: Number.isInteger(target) && bounded !== target };
}

function decide({ state, book, activeTarget = null, pairCap = null, activeEvidenceFloor = null, floorFirstFlickerLive = false, floorMature = false, persistentJoinLevel = null, wtaInverseFalling = false, pulseFloor = null, causalOwnReachLow = null }) {
  const placement = placementTarget({ state, book, activeTarget, pairCap, persistentJoinLevel, wtaInverseFalling, pulseFloor, causalOwnReachLow });
  if (activeTarget !== null) {
    const take = v36.matureFloorTakePermission({ book, pairCap, activeEvidenceFloor, floorFirstFlickerLive, floorMature });
    if (take.permitted) return { action: "TAKE", target_cents: book.ask, reason: "MATURE_EVIDENCE_FLOOR_TAKE", take_permission: take, placement };
  }
  const target = placement.target_cents;
  if (target === null) return { action: lawfulCent(activeTarget) ? "CANCEL_REST" : "HOLD_REST", target_cents: null, reason: "NO_LAWFUL_POST_ONLY_REST_TARGET", take_permission: null, placement };
  if (!lawfulCent(activeTarget)) return { action: "PLACE_REST", target_cents: target, reason: placement.authority, take_permission: null, placement };
  if (target !== activeTarget) return { action: "REPRICE_REST", target_cents: target, direction: target > activeTarget ? "UP" : "DOWN", reason: placement.authority, take_permission: null, placement };
  return { action: "HOLD_REST", target_cents: activeTarget, reason: `${placement.authority}_ALREADY_AT_TARGET`, take_permission: null, placement };
}

function strictPrintCross(order, print) {
  return Boolean(order) && lawfulCent(order.target_cents) && print.ts > order.action_ts && print.taker_side === "no" && Number.isFinite(print.size) && print.size >= v36.QUALIFIED_SIZE_MIN && Number.isInteger(print.price) && print.price <= order.target_cents;
}

function tradedAtLevel(order, print) {
  return Boolean(order) && lawfulCent(order.target_cents) && print.ts > order.action_ts && Number.isFinite(print.size) && print.size > 0 && Number.isInteger(print.price) && print.price <= order.target_cents;
}

function quoteTouch(order, book) {
  return Boolean(order) && lawfulCent(order.target_cents) && book.ts > order.action_ts && v36.qualifyingAskEvidence(book) && book.ask <= order.target_cents;
}

module.exports = {
  ...v36,
  LOOKBACK_SECONDS,
  PERSISTENT_LEVEL_SECONDS,
  PULSE_REVISIT_MIN,
  lawfulCent,
  trimPulseVisits,
  trailingPulseFloor,
  postOnlyBound,
  placementTarget,
  decide,
  strictPrintCross,
  tradedAtLevel,
  quoteTouch,
};
