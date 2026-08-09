"use strict";

// V42 is one receipt-causal feasibility clause on the frozen V41 maker
// machine.  It never changes V41's target arithmetic.  It temporarily
// withholds only a target whose resulting sibling cap is more than ten cents
// below the sibling's contemporaneous best ask.  Missing sibling evidence is
// not authority to gate V41.

const v41 = require("./window1_v41_maker_machine.js");

const DEEP_GAP_TOLERANCE_CENTS = 10;

function deepGapFeasibility(targetCents, siblingBestAsk) {
  if (!v41.lawfulCent(targetCents) || !v41.lawfulCent(siblingBestAsk)) {
    return {
      authority: false,
      withheld: false,
      reason: "V42_NO_CONTEMPORANEOUS_SIBLING_ASK_V41_UNCHANGED",
      target_cents: targetCents,
      sibling_best_ask_cents: siblingBestAsk ?? null,
      implied_sibling_cap_cents: v41.lawfulCent(targetCents) ? 99 - targetCents : null,
      deep_gap_cents: null,
      tolerance_cents: DEEP_GAP_TOLERANCE_CENTS,
    };
  }
  const impliedCap = 99 - targetCents;
  const deepGap = siblingBestAsk - impliedCap;
  const withheld = impliedCap < siblingBestAsk - DEEP_GAP_TOLERANCE_CENTS;
  return {
    authority: true,
    withheld,
    reason: withheld ? "V42_DEEP_GAP_FEASIBILITY_WITHHOLD" : "V42_DEEP_GAP_FEASIBILITY_PASS",
    target_cents: targetCents,
    sibling_best_ask_cents: siblingBestAsk,
    implied_sibling_cap_cents: impliedCap,
    deep_gap_cents: deepGap,
    tolerance_cents: DEEP_GAP_TOLERANCE_CENTS,
    comparison: `${impliedCap} ${withheld ? "<" : ">="} ${siblingBestAsk}-${DEEP_GAP_TOLERANCE_CENTS}`,
  };
}

function decide(inputs) {
  const incumbent = v41.decide(inputs);
  const proposed = v41.lawfulCent(incumbent.target_cents) ? incumbent.target_cents : null;
  if (proposed === null) return { ...incumbent, guard: deepGapFeasibility(null, inputs.siblingBestAsk), v41_decision: incumbent };

  const guard = deepGapFeasibility(proposed, inputs.siblingBestAsk);
  if (!guard.withheld) return { ...incumbent, guard, v41_decision: incumbent };

  // An already-resting V41 order is separately adjudicated at its own level.
  // Keep a feasible incumbent rest; cancel an incumbent rest that is itself
  // deep-gap infeasible.  A withheld new placement remains HOLD with no order.
  const active = inputs.activeTarget;
  const activeGuard = deepGapFeasibility(active, inputs.siblingBestAsk);
  if (v41.lawfulCent(active) && !activeGuard.withheld) {
    return {
      action: "HOLD_REST",
      target_cents: active,
      reason: "V42_DEEP_GAP_WITHHOLD_REPRICE_KEEP_FEASIBLE_INCUMBENT_REST",
      placement: incumbent.placement,
      guard: { ...guard, active_target_guard: activeGuard },
      v41_decision: incumbent,
    };
  }
  if (v41.lawfulCent(active)) {
    return {
      action: "CANCEL_REST",
      target_cents: null,
      reason: "V42_DEEP_GAP_WITHHOLD_CANCEL_INFEASIBLE_INCUMBENT_REST",
      placement: incumbent.placement,
      guard: { ...guard, active_target_guard: activeGuard },
      v41_decision: incumbent,
    };
  }
  return {
    action: "HOLD_REST",
    target_cents: null,
    reason: "V42_DEEP_GAP_WITHHOLD_NEW_REST",
    placement: incumbent.placement,
    guard,
    v41_decision: incumbent,
  };
}

module.exports = {
  ...v41,
  DEEP_GAP_TOLERANCE_CENTS,
  deepGapFeasibility,
  decide,
};
