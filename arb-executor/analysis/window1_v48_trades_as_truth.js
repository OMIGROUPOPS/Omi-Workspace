"use strict";

// V48 preserves V47's receipt-local arming and placement machinery, but gives
// market credit to one source only: a true trade printed at or below a lawful
// rest after that rest existed.  Quote observations remain placement inputs;
// they are never fill evidence.  The explicit ladder rungs are executable
// attribution variants, not hidden aliases for V47's mixed placement stack.

const v47 = require("./window1_v47_same_tick_arm.js");

const PLACEMENT_LADDERS = Object.freeze({
  V47_INCUMBENT: "V47_INCUMBENT",
  BID_MINUS_ONE: "BID_MINUS_ONE",
  BID: "BID",
  LOWEST_RECENT_TRADED_LEVEL: "LOWEST_RECENT_TRADED_LEVEL",
});

function normalizedClauses(value = {}) {
  const ladder = Object.values(PLACEMENT_LADDERS).includes(value.placement_ladder)
    ? value.placement_ladder
    : PLACEMENT_LADDERS.V47_INCUMBENT;
  return {
    ...v47.normalizedClauses(value),
    trades_as_truth: Boolean(value.trades_as_truth),
    placement_ladder: ladder,
  };
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

function unguardedTargetDecision(inputs, target, authority) {
  const active = inputs.activeTarget;
  const placement = {
    target_cents: target,
    unbounded_target_cents: inputs.ladder_unbounded_target_cents ?? null,
    authority,
    sanity_bound_applied: Number.isInteger(inputs.ladder_unbounded_target_cents)
      && target !== inputs.ladder_unbounded_target_cents,
  };
  if (!v47.lawfulCent(target)) {
    return {
      action: v47.lawfulCent(active) ? "CANCEL_REST" : "HOLD_REST",
      target_cents: null,
      reason: "V48_LADDER_NO_LAWFUL_POST_ONLY_TARGET",
      placement,
    };
  }
  if (!v47.lawfulCent(active)) return { action: "PLACE_REST", target_cents: target, reason: authority, placement };
  if (target !== active) return { action: "REPRICE_REST", target_cents: target, direction: target > active ? "UP" : "DOWN", reason: authority, placement };
  return { action: "HOLD_REST", target_cents: active, reason: `${authority}_ALREADY_AT_TARGET`, placement };
}

function guardedTargetDecision(inputs, target, authority, clauses) {
  const incumbent = unguardedTargetDecision(inputs, target, authority);
  if (clauses.release_guard_on_sibling_credit && inputs.siblingCredited) {
    return { ...incumbent, guard: null, guard_authority: "TERMINATED_AT_SIBLING_CREDIT", guard_authority_terminated: true };
  }
  if (!clauses.deep_gap_guard || !v47.lawfulCent(incumbent.target_cents)) {
    return { ...incumbent, guard: null, unguarded_decision: incumbent };
  }
  const guard = v47.deepGapFeasibility(incumbent.target_cents, inputs.siblingBestAsk);
  if (!guard.withheld) return { ...incumbent, guard, unguarded_decision: incumbent };
  const active = inputs.activeTarget;
  const activeGuard = v47.deepGapFeasibility(active, inputs.siblingBestAsk);
  if (v47.lawfulCent(active) && !activeGuard.withheld) {
    return { action: "HOLD_REST", target_cents: active, reason: "V48_LADDER_WITHHOLD_REPRICE_KEEP_FEASIBLE_INCUMBENT_REST", placement: incumbent.placement, guard: { ...guard, active_target_guard: activeGuard }, unguarded_decision: incumbent };
  }
  if (v47.lawfulCent(active)) {
    return { action: "CANCEL_REST", target_cents: null, reason: "V48_LADDER_WITHHOLD_CANCEL_INFEASIBLE_INCUMBENT_REST", placement: incumbent.placement, guard: { ...guard, active_target_guard: activeGuard }, unguarded_decision: incumbent };
  }
  return { action: "HOLD_REST", target_cents: null, reason: "V48_LADDER_WITHHOLD_NEW_REST", placement: incumbent.placement, guard, unguarded_decision: incumbent };
}

function ladderTarget(inputs, ladder) {
  if (ladder === PLACEMENT_LADDERS.BID_MINUS_ONE) {
    const raw = Number.isInteger(inputs.book?.bid) ? inputs.book.bid - 1 : null;
    return { raw, bounded: v47.postOnlyBound(raw, inputs.book, inputs.pairCap), authority: "V48_LADDER_BID_MINUS_ONE" };
  }
  if (ladder === PLACEMENT_LADDERS.BID) {
    const raw = Number.isInteger(inputs.book?.bid) ? inputs.book.bid : null;
    return { raw, bounded: v47.postOnlyBound(raw, inputs.book, inputs.pairCap), authority: "V48_LADDER_BEST_BID" };
  }
  if (ladder === PLACEMENT_LADDERS.LOWEST_RECENT_TRADED_LEVEL && v47.lawfulCent(inputs.recentTradeLow)) {
    const raw = inputs.recentTradeLow;
    return { raw, bounded: v47.postOnlyBound(raw, inputs.book, inputs.pairCap), authority: "V48_LADDER_LOWEST_TRUE_TRADE_TRAILING_300S" };
  }
  return null;
}

function decideReceipt(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const incumbent = v47.decideReceipt({ ...inputs, clauses });
  if (clauses.placement_ladder === PLACEMENT_LADDERS.V47_INCUMBENT) {
    return { ...incumbent, placement_ladder: clauses.placement_ladder, ladder_authority: "V47_INCUMBENT_BYTE_IDENTICAL" };
  }
  const rung = ladderTarget(inputs, clauses.placement_ladder);
  if (!rung) {
    return { ...incumbent, placement_ladder: clauses.placement_ladder, ladder_authority: "NO_CAUSAL_RECENT_TRADE_V47_INCUMBENT_FALLBACK" };
  }
  const decision = guardedTargetDecision({ ...inputs, ladder_unbounded_target_cents: rung.raw }, rung.bounded, rung.authority, clauses);
  return {
    ...incumbent,
    decision,
    placement_ladder: clauses.placement_ladder,
    ladder_authority: rung.authority,
    ladder_raw_target_cents: rung.raw,
    ladder_target_cents: rung.bounded,
  };
}

module.exports = {
  ...v47,
  PLACEMENT_LADDERS,
  normalizedClauses,
  tradeTruthCredit,
  ladderTarget,
  decideReceipt,
};
