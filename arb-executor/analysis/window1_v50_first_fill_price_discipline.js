"use strict";

// V50 adds one causal price discipline to frozen V47.  It never withholds a
// receipt or creates a timer: when the sibling has printed, the incumbent V47
// rest target is bounded by 99 minus the sibling's lowest true trade observed
// so far.  Before sibling flow exists, V47 is returned byte-for-decision.

const v47 = require("./window1_v47_same_tick_arm.js");

function normalizedClauses(value = {}) {
  return {
    ...v47.normalizedClauses(value),
    first_fill_price_discipline: Boolean(value.first_fill_price_discipline),
  };
}

function firstFillPriceBound({ pairCap, siblingObservedFlowFloor }) {
  const fixedPairCap = Number.isInteger(pairCap) ? pairCap : null;
  const observedFloor = Number.isInteger(siblingObservedFlowFloor)
    ? siblingObservedFlowFloor
    : null;
  const observedFlowCap = observedFloor === null ? null : 99 - observedFloor;
  const caps = [fixedPairCap, observedFlowCap].filter(Number.isInteger);
  return {
    authority: observedFloor === null ? "UNBOUNDED_NO_SIBLING_FLOW" : "SIBLING_LOWEST_CAUSAL_TRADE_SO_FAR",
    sibling_observed_flow_floor_cents: observedFloor,
    observed_flow_cap_cents: observedFlowCap,
    fixed_pair_cap_cents: fixedPairCap,
    effective_cap_cents: caps.length ? Math.min(...caps) : null,
  };
}

function applyPriceBound(decision, inputs, clauses) {
  if (!clauses.first_fill_price_discipline) return decision;
  const bound = firstFillPriceBound(inputs);
  const target = decision?.target_cents;
  const result = {
    ...decision,
    first_fill_price_discipline: {
      ...bound,
      incumbent_target_cents: Number.isInteger(target) ? target : null,
      applied: false,
    },
  };
  if (!Number.isInteger(target) || !["PLACE_REST", "REPRICE_REST"].includes(decision.action)) return result;
  if (!Number.isInteger(bound.effective_cap_cents) || target <= bound.effective_cap_cents) return result;
  result.first_fill_price_discipline.applied = true;
  result.first_fill_price_discipline.reduction_cents = target - bound.effective_cap_cents;
  if (!v47.lawfulCent(bound.effective_cap_cents)) {
    return {
      ...result,
      action: Number.isInteger(inputs.activeTarget) ? "CANCEL_REST" : "HOLD_REST",
      target_cents: null,
      reason: "V50_FIRST_FILL_PRICE_BOUND_NO_LAWFUL_CENT",
    };
  }
  return {
    ...result,
    target_cents: bound.effective_cap_cents,
    reason: `V50_FIRST_FILL_PRICE_BOUND__${decision.reason}`,
  };
}

function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.first_fill_price_discipline) return v47.decide(inputs);
  const decision = v47.decide({ ...inputs, clauses });
  return applyPriceBound(decision, inputs, clauses);
}

function decideReceipt(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.first_fill_price_discipline) return v47.decideReceipt(inputs);
  const bound = firstFillPriceBound(inputs);
  const atomic = v47.decideReceipt({ ...inputs, clauses });
  return {
    ...atomic,
    decision: applyPriceBound(atomic.decision, inputs, clauses),
    first_fill_price_discipline: bound,
  };
}

module.exports = {
  ...v47,
  normalizedClauses,
  firstFillPriceBound,
  applyPriceBound,
  decide,
  decideReceipt,
};
