"use strict";

// V11 does not add a time, size, or price threshold. It makes the already-bound
// stable same-price ask proof causal authority when the fitted descent ordinal
// is absent or remains unreached: a fresh later receipt at the current observed
// low, after ten seconds and with exact-five displayed capacity, can rebut a
// stale unanimous LOWER only when own micro position, inverse sibling, and the
// existing stable-signing proof are all present.

function evaluatePersistenceFloorOverride({
  unanimousLower,
  currentAskAtObservedLow,
  freshOwnReceipt,
  strictlyLaterSamePriceAskReceipt,
  askDwellSeconds,
  dwellSeconds,
  topAskSize,
  quantity,
  ownMicroPositionObserved,
  inverseSiblingResolved,
  stableSigningSupported,
  fittedPersistenceExhausted,
  fittedOrdinalUnavailable,
  zeroFutureQualifiedLowerSupport,
}) {
  for (const [name, value] of [["askDwellSeconds", askDwellSeconds], ["dwellSeconds", dwellSeconds], ["topAskSize", topAskSize], ["quantity", quantity]]) {
    if (!Number.isFinite(value) || value < 0) throw new Error(`${name} must be finite and non-negative`);
  }
  const predicates = {
    unanimous_lower_before_override: Boolean(unanimousLower),
    current_ask_at_observed_low: Boolean(currentAskAtObservedLow),
    fresh_own_receipt: Boolean(freshOwnReceipt),
    strictly_later_same_price_ask_receipt: Boolean(strictlyLaterSamePriceAskReceipt),
    ask_dwell_at_least_existing_threshold: askDwellSeconds >= dwellSeconds,
    top_ask_capacity_at_least_exact_quantity: topAskSize >= quantity,
    own_micro_position_observed: Boolean(ownMicroPositionObserved),
    inverse_sibling_resolved: Boolean(inverseSiblingResolved),
    stable_signing_supported: Boolean(stableSigningSupported),
    fitted_leave_one_leg_out_persistence_exhausted: Boolean(fittedPersistenceExhausted),
    fitted_descent_ordinal_unavailable: Boolean(fittedOrdinalUnavailable),
    zero_leave_one_leg_out_future_qualified_lower_support: Boolean(zeroFutureQualifiedLowerSupport),
  };
  const supported = Object.values(predicates).every(Boolean);
  return {
    supported,
    verdict: supported ? "FLOOR" : "LOWER",
    authority: supported ? "EXISTING_STABLE_QUALIFIED_ASK_PERSISTENCE" : null,
    predicates,
    invented_thresholds: 0,
  };
}

module.exports = { evaluatePersistenceFloorOverride };
