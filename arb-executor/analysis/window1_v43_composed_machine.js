"use strict";

// V43 composes exactly three receipt-priced clauses on frozen V41.  The
// caller supplies an explicit clause set so the same executable policy
// produces the full 2^3 attribution table from identical inputs.

const v41 = require("./window1_v41_maker_machine.js");
const v42 = require("./window1_v42_deep_gap_feasibility_guard.js");

function normalizedClauses(value = {}) {
  return { arm_at_first_evidence: Boolean(value.arm_at_first_evidence), deep_gap_guard: Boolean(value.deep_gap_guard), loosen_one_cent: Boolean(value.loosen_one_cent) };
}

function persistenceJoinUpdate(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.arm_at_first_evidence) return v41.persistenceJoinUpdate(inputs);
  if (inputs.state !== "RISING" || !v41.lawfulCent(inputs.bid)) return { armed: false, changed: false, level_cents: inputs.currentJoinLevel };
  return { armed: true, changed: inputs.currentJoinLevel !== inputs.bid, level_cents: inputs.bid, authority: "V43_C1_FIRST_OBSERVATION_T5_ARM" };
}

function placementTarget(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const incumbent = v41.placementTarget(inputs);
  if (!clauses.loosen_one_cent) return incumbent;
  const nonTrackingAuthority = incumbent.authority === "V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1" || incumbent.authority === "V41_WTA_OTHER_EXPRESSION_FALLING_HOLD";
  if (nonTrackingAuthority) return incumbent;
  let target = Number.isInteger(inputs.book?.bid) ? inputs.book.bid : null;
  if (Number.isInteger(target) && Number.isInteger(inputs.pairCap)) target = Math.min(target, inputs.pairCap);
  if (Number.isInteger(target) && Number.isInteger(inputs.book?.ask)) target = Math.min(target, inputs.book.ask - 1);
  target = v41.lawfulCent(target) ? target : null;
  return { target_cents: target, unbounded_target_cents: inputs.book?.bid ?? null, authority: "V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY", sanity_bound_applied: Number.isInteger(inputs.book?.bid) && target !== inputs.book.bid, V41_placement: incumbent };
}

function unguardedDecision(inputs) {
  const placement = placementTarget(inputs), active = inputs.activeTarget, target = placement.target_cents;
  if (target === null) return { action: v41.lawfulCent(active) ? "CANCEL_REST" : "HOLD_REST", target_cents: null, reason: "V43_NO_LAWFUL_POST_ONLY_REST_TARGET", placement };
  if (!v41.lawfulCent(active)) return { action: "PLACE_REST", target_cents: target, reason: placement.authority, placement };
  if (target !== active) return { action: "REPRICE_REST", target_cents: target, direction: target > active ? "UP" : "DOWN", reason: placement.authority, placement };
  return { action: "HOLD_REST", target_cents: active, reason: `${placement.authority}_ALREADY_AT_TARGET`, placement };
}

function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses), incumbent = unguardedDecision(inputs);
  if (!clauses.deep_gap_guard || !v41.lawfulCent(incumbent.target_cents)) return { ...incumbent, guard: null, unguarded_decision: incumbent };
  const guard = v42.deepGapFeasibility(incumbent.target_cents, inputs.siblingBestAsk);
  if (!guard.withheld) return { ...incumbent, guard, unguarded_decision: incumbent };
  const active = inputs.activeTarget, activeGuard = v42.deepGapFeasibility(active, inputs.siblingBestAsk);
  if (v41.lawfulCent(active) && !activeGuard.withheld) return { action: "HOLD_REST", target_cents: active, reason: "V43_C2_WITHHOLD_REPRICE_KEEP_FEASIBLE_INCUMBENT_REST", placement: incumbent.placement, guard: { ...guard, active_target_guard: activeGuard }, unguarded_decision: incumbent };
  if (v41.lawfulCent(active)) return { action: "CANCEL_REST", target_cents: null, reason: "V43_C2_WITHHOLD_CANCEL_INFEASIBLE_INCUMBENT_REST", placement: incumbent.placement, guard: { ...guard, active_target_guard: activeGuard }, unguarded_decision: incumbent };
  return { action: "HOLD_REST", target_cents: null, reason: "V43_C2_WITHHOLD_NEW_REST", placement: incumbent.placement, guard, unguarded_decision: incumbent };
}

module.exports = {
  ...v41,
  DEEP_GAP_TOLERANCE_CENTS: v42.DEEP_GAP_TOLERANCE_CENTS,
  normalizedClauses,
  deepGapFeasibility: v42.deepGapFeasibility,
  persistenceJoinUpdate,
  placementTarget,
  decide,
};
