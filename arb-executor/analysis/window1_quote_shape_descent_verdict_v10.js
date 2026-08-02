"use strict";

// V10 closes the temporal-lag hole left by V5. The already-fitted descent
// ordinal is symmetric causal authority: below it the shape says LOWER; at or
// beyond it the shape says FLOOR. No new threshold or future target-row fact is
// introduced.

function evaluateCausalDescentOrdinalVerdict({ baseVerdict, observedNewLowDescents, fittedDistribution }) {
  if (!Number.isInteger(observedNewLowDescents) || observedNewLowDescents < 0) throw new Error("observed new-low descents must be an exact non-negative integer");
  if (observedNewLowDescents === 0) {
    return { verdict: baseVerdict, descent_adjustment: "NOT_APPLICABLE", observed_new_low_descents: observedNewLowDescents };
  }
  const signingOrdinal = fittedDistribution?.signing_ordinal_after_a_descent_is_observed;
  if (!Number.isInteger(signingOrdinal) || signingOrdinal <= 0) {
    return { verdict: "UNKNOWN", descent_adjustment: "OBSERVED_DESCENT_OUTSIDE_SHAPE_TRAINING_SUPPORT", observed_new_low_descents: observedNewLowDescents };
  }
  if (observedNewLowDescents < signingOrdinal) {
    return { verdict: "LOWER", descent_adjustment: "FITTED_DESCENT_ORDINAL_NOT_REACHED", observed_new_low_descents: observedNewLowDescents, required_new_low_descents: signingOrdinal };
  }
  return {
    verdict: "FLOOR",
    descent_adjustment: baseVerdict === "FLOOR" ? "FITTED_DESCENT_ORDINAL_REACHED" : "FITTED_DESCENT_ORDINAL_OVERRIDES_LAGGING_TEMPORAL_MEDOID",
    observed_new_low_descents: observedNewLowDescents,
    required_new_low_descents: signingOrdinal,
    prior_base_verdict: baseVerdict,
  };
}

module.exports = { evaluateCausalDescentOrdinalVerdict };
