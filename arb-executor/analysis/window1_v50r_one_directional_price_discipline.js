"use strict";

// V50-R applies the observed sibling-flow price bound only while this leg is
// still a prospective unhedged first fill.  Once the sibling is credited, V47
// owns the hedge-side decision with its fixed 99-minus-first-fill pair cap.
// The flow-floor overlay changes price only and never withholds or adds time.

const v47 = require("./window1_v47_same_tick_arm.js");

function normalizedClauses(value = {}) {
  return {
    ...v47.normalizedClauses(value),
    first_fill_price_discipline: Boolean(value.first_fill_price_discipline),
  };
}

function firstFillPriceBound({ pairCap, siblingObservedFlowFloor, siblingCredited }) {
  const fixedPairCap = Number.isInteger(pairCap) ? pairCap : null;
  const observedFloor = Number.isInteger(siblingObservedFlowFloor)
    ? siblingObservedFlowFloor
    : null;
  const siblingIsCredited = Boolean(siblingCredited);
  const counterfactualObservedFlowCap = observedFloor === null ? null : 99 - observedFloor;
  if (siblingIsCredited) {
    return {
      authority: "LIFTED_AT_SIBLING_CREDIT_FIXED_PAIR_CAP_ONLY",
      scope: "UNHEDGED_FIRST_FILL_ONLY",
      sibling_credited: true,
      sibling_observed_flow_floor_cents: observedFloor,
      counterfactual_observed_flow_cap_cents: counterfactualObservedFlowCap,
      observed_flow_cap_cents: null,
      fixed_pair_cap_cents: fixedPairCap,
      effective_cap_cents: null,
    };
  }
  return {
    authority: observedFloor === null ? "UNBOUNDED_NO_SIBLING_FLOW" : "UNHEDGED_SIBLING_LOWEST_CAUSAL_TRADE_SO_FAR",
    scope: "UNHEDGED_FIRST_FILL_ONLY",
    sibling_credited: false,
    sibling_observed_flow_floor_cents: observedFloor,
    counterfactual_observed_flow_cap_cents: counterfactualObservedFlowCap,
    observed_flow_cap_cents: counterfactualObservedFlowCap,
    fixed_pair_cap_cents: fixedPairCap,
    effective_cap_cents: counterfactualObservedFlowCap,
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
      reason: "V50R_UNHEDGED_PRICE_BOUND_NO_LAWFUL_CENT",
    };
  }
  return {
    ...result,
    target_cents: bound.effective_cap_cents,
    reason: `V50R_UNHEDGED_PRICE_BOUND__${decision.reason}`,
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
