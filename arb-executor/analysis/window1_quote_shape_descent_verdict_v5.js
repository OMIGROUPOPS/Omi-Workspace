"use strict";

function evaluateDescentVerdict({ baseVerdict, observedNewLowDescents, fittedDistribution }) {
  if (!Number.isInteger(observedNewLowDescents) || observedNewLowDescents < 0) throw new Error("observed new-low descents must be an exact non-negative integer");
  if (baseVerdict !== "FLOOR" || observedNewLowDescents === 0) {
    return { verdict: baseVerdict, descent_adjustment: "NOT_APPLICABLE", observed_new_low_descents: observedNewLowDescents };
  }
  const signingOrdinal = fittedDistribution?.signing_ordinal_after_a_descent_is_observed;
  if (!Number.isInteger(signingOrdinal) || signingOrdinal <= 0) {
    return { verdict: "UNKNOWN", descent_adjustment: "OBSERVED_DESCENT_OUTSIDE_SHAPE_TRAINING_SUPPORT", observed_new_low_descents: observedNewLowDescents };
  }
  if (observedNewLowDescents < signingOrdinal) {
    return { verdict: "LOWER", descent_adjustment: "FITTED_DESCENT_ORDINAL_NOT_REACHED", observed_new_low_descents: observedNewLowDescents, required_new_low_descents: signingOrdinal };
  }
  return { verdict: "FLOOR", descent_adjustment: "FITTED_DESCENT_ORDINAL_REACHED", observed_new_low_descents: observedNewLowDescents, required_new_low_descents: signingOrdinal };
}

module.exports = { evaluateDescentVerdict };
