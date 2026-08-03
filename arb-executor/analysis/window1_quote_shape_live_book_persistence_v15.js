"use strict";

// V15 removes two obsolete vetoes without adding a price, time, or size
// constant.  A unanimous FLOOR is priced from the current lawful book rather
// than equality with a historical low.  A unanimous LOWER may be overturned
// only when the already-fitted, leave-one-leg-out persistence wait has expired.

function evaluateLiveBookFloorAuthority({
  unanimousFloor,
  ownMicroPositionObserved,
  inverseSiblingResolved,
  stableSigningSupported,
  freshOwnReceipt,
  askDwellSeconds,
  dwellSeconds,
  topAskSize,
  quantity,
}) {
  for (const [name, value] of [["askDwellSeconds", askDwellSeconds], ["dwellSeconds", dwellSeconds], ["topAskSize", topAskSize], ["quantity", quantity]]) {
    if (!Number.isFinite(value) || value < 0) throw new Error(`${name} must be finite and non-negative`);
  }
  const predicates = {
    unanimous_surviving_shape_floor: Boolean(unanimousFloor),
    own_micro_position_observed: Boolean(ownMicroPositionObserved),
    inverse_sibling_resolved: Boolean(inverseSiblingResolved),
    stable_signing_supported: Boolean(stableSigningSupported),
    fresh_own_receipt: Boolean(freshOwnReceipt),
    ask_dwell_at_least_inherited_threshold: askDwellSeconds >= dwellSeconds,
    top_ask_capacity_at_least_exact_quantity: topAskSize >= quantity,
  };
  return {
    supported: Object.values(predicates).every(Boolean),
    authority: "CURRENT_LAWFUL_BOOK_PLUS_SURVIVING_SHAPE_SET",
    predicates,
    historical_low_equality_consulted: false,
    invented_thresholds: 0,
  };
}

function evaluateFittedPersistenceFloorAuthority({
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
  persistenceProofs,
}) {
  for (const [name, value] of [["askDwellSeconds", askDwellSeconds], ["dwellSeconds", dwellSeconds], ["topAskSize", topAskSize], ["quantity", quantity]]) {
    if (!Number.isFinite(value) || value < 0) throw new Error(`${name} must be finite and non-negative`);
  }
  if (!Array.isArray(persistenceProofs)) throw new Error("persistenceProofs must be an array");
  const fittedCellsAvailable = persistenceProofs.length > 0 && persistenceProofs.every((proof) => proof && proof.available === true);
  const fittedWaitExhausted = fittedCellsAvailable && persistenceProofs.every((proof) => proof.exhausted === true);
  const predicates = {
    unanimous_lower_before_override: Boolean(unanimousLower),
    current_ask_at_observed_low: Boolean(currentAskAtObservedLow),
    fresh_own_receipt: Boolean(freshOwnReceipt),
    strictly_later_same_price_ask_receipt: Boolean(strictlyLaterSamePriceAskReceipt),
    ask_dwell_at_least_inherited_threshold: askDwellSeconds >= dwellSeconds,
    top_ask_capacity_at_least_exact_quantity: topAskSize >= quantity,
    own_micro_position_observed: Boolean(ownMicroPositionObserved),
    inverse_sibling_resolved: Boolean(inverseSiblingResolved),
    stable_signing_supported: Boolean(stableSigningSupported),
    leave_one_leg_out_persistence_cells_available: fittedCellsAvailable,
    leave_one_leg_out_fitted_wait_exhausted: fittedWaitExhausted,
  };
  const supported = Object.values(predicates).every(Boolean);
  return {
    supported,
    verdict: supported ? "FLOOR" : "LOWER",
    authority: supported ? "LEAVE_ONE_LEG_OUT_FITTED_SAME_PRICE_PERSISTENCE" : null,
    predicates,
    persistence_proofs: persistenceProofs,
    descent_ordinal_availability_is_not_a_veto: true,
    invented_thresholds: 0,
  };
}

module.exports = { evaluateLiveBookFloorAuthority, evaluateFittedPersistenceFloorAuthority };
