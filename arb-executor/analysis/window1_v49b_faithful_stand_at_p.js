"use strict";

// V49b is the faithful, narrow stand-AT-P test.  V47 remains the incumbent
// everywhere except a doctrine leg whose own tape has causally evidenced the
// frozen standable level P.  At such a receipt the post-only rest is P itself:
// no bid-minus-one transform and no synthetic-book substitution.

const v47 = require("./window1_v47_same_tick_arm.js");

function normalizedClauses(value = {}) {
  return {
    ...v47.normalizedClauses(value),
    trades_as_truth: Boolean(value.trades_as_truth),
    faithful_stand_at_p: Boolean(value.faithful_stand_at_p),
  };
}

function incumbentReceipt(inputs, clauses) {
  return v47.decideReceipt({ ...inputs, clauses });
}

function faithfulDecision(inputs, atomic, clauses) {
  const doctrine = inputs.doctrineStanding;
  const p = doctrine?.level_cents;
  if (!clauses.faithful_stand_at_p || !doctrine?.authorized || !v47.lawfulCent(p)) {
    return { ...atomic.decision, doctrine_standing: { enabled: clauses.faithful_stand_at_p, authorized: false, mechanism_code: "INCUMBENT_V47", doctrine: doctrine ?? null } };
  }

  const postOnly = v47.postOnlyBound(p, inputs.book, inputs.pairCap);
  const exact = postOnly === p && inputs.book?.ask > p;
  if (!exact) {
    const active = inputs.activeTarget;
    const action = v47.lawfulCent(active) ? "CANCEL_REST" : "HOLD_REST";
    return { action, target_cents: null, reason: "V49B_AT_P_CURRENTLY_UNLAWFUL_NO_OFFSET_FALLBACK", placement: { target_cents: null, unbounded_target_cents: p, authority: "V49B_FAITHFUL_STAND_AT_P_ABSTAIN", doctrine_level_cents: p, doctrine_mechanism_code: "AT_P_UNAVAILABLE" }, guard: null, unguarded_decision: { action, target_cents: null }, doctrine_standing: { enabled: true, authorized: true, mechanism_code: "AT_P_UNAVAILABLE", doctrine, bounded_level_cents: postOnly } };
  }

  // Preserve V43/V45 guard authority around the exact-P target.  The guard is
  // a feasibility check, not a placement transform.  Once the sibling is
  // credited, V45's authority-termination law applies unchanged.
  const guardAuthorityTerminated = clauses.release_guard_on_sibling_credit && inputs.siblingCredited;
  const guard = clauses.deep_gap_guard && !guardAuthorityTerminated
    ? v47.deepGapFeasibility(p, inputs.siblingBestAsk)
    : null;
  const placement = {
    target_cents: p,
    unbounded_target_cents: p,
    authority: "V49B_FAITHFUL_STAND_AT_P",
    doctrine_level_cents: p,
    doctrine_mechanism_code: "AT_P",
    causal_evidence: doctrine.causal_evidence,
  };
  if (guard?.withheld) {
    const active = inputs.activeTarget;
    const activeGuard = v47.deepGapFeasibility(active, inputs.siblingBestAsk);
    if (v47.lawfulCent(active) && !activeGuard.withheld) {
      return { action: "HOLD_REST", target_cents: active, reason: "V43_C2_WITHHOLD_REPRICE_KEEP_FEASIBLE_INCUMBENT_REST", placement, guard: { ...guard, active_target_guard: activeGuard }, unguarded_decision: { action: active === p ? "HOLD_REST" : "REPRICE_REST", target_cents: p }, doctrine_standing: { enabled: true, authorized: true, mechanism_code: "AT_P_GUARD_WITHHELD", doctrine } };
    }
    if (v47.lawfulCent(active)) {
      return { action: "CANCEL_REST", target_cents: null, reason: "V43_C2_WITHHOLD_CANCEL_INFEASIBLE_INCUMBENT_REST", placement, guard: { ...guard, active_target_guard: activeGuard }, unguarded_decision: { action: "REPRICE_REST", target_cents: p }, doctrine_standing: { enabled: true, authorized: true, mechanism_code: "AT_P_GUARD_WITHHELD", doctrine } };
    }
    return { action: "HOLD_REST", target_cents: null, reason: "V43_C2_WITHHOLD_NEW_REST", placement, guard, unguarded_decision: { action: "PLACE_REST", target_cents: p }, doctrine_standing: { enabled: true, authorized: true, mechanism_code: "AT_P_GUARD_WITHHELD", doctrine } };
  }

  const active = inputs.activeTarget;
  const action = !v47.lawfulCent(active) ? "PLACE_REST" : active === p ? "HOLD_REST" : "REPRICE_REST";
  return {
    action,
    target_cents: p,
    ...(action === "REPRICE_REST" ? { direction: p > active ? "UP" : "DOWN" } : {}),
    reason: action === "HOLD_REST" ? "V49B_FAITHFUL_STAND_AT_P_ALREADY_AT_TARGET" : "V49B_FAITHFUL_STAND_AT_P",
    placement,
    guard,
    unguarded_decision: { action, target_cents: p, placement },
    ...(guardAuthorityTerminated ? { guard_authority: "TERMINATED_AT_SIBLING_CREDIT", guard_authority_terminated: true } : {}),
    doctrine_standing: { enabled: true, authorized: true, mechanism_code: "AT_P", doctrine },
  };
}

function decideReceipt(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const atomic = incumbentReceipt(inputs, clauses);
  return { ...atomic, decision: faithfulDecision(inputs, atomic, clauses), faithful_stand_at_p_enabled: clauses.faithful_stand_at_p };
}

function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const atomic = incumbentReceipt({ ...inputs, currentJoinLevel: inputs.persistentJoinLevel, residencySeconds: inputs.residencySeconds ?? 0 }, clauses);
  return faithfulDecision(inputs, atomic, clauses);
}

function tradeTruthCredit(order, print) {
  return Boolean(order)
    && v47.lawfulCent(order.target_cents)
    && print?.kind === "PRINT"
    && Number.isFinite(print.ts)
    && print.ts > order.action_ts
    && typeof print.trade_id === "string"
    && print.trade_id.length > 0
    && Number.isInteger(print.price)
    && print.price <= order.target_cents;
}

module.exports = { ...v47, normalizedClauses, faithfulDecision, decideReceipt, decide, tradeTruthCredit };
