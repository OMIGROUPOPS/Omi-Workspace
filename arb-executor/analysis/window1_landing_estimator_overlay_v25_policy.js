"use strict";

function overlayDecision({ cellAuthorized, incumbentAction, estimate, phasedMirrorCandidate }) {
  if (!cellAuthorized) return { state: "FALLBACK", reason: "CELL_ERROR_BAR_NOT_BEATEN", incumbent_byte_identity_required: true };
  if (!estimate || estimate.state !== "BOUND") return { state: "FALLBACK", reason: "ESTIMATOR_AUTHORITY_ABSENT", incumbent_byte_identity_required: true };
  if (incumbentAction) {
    if (!Number.isInteger(incumbentAction.price_cents) || !Number.isFinite(estimate.q50)) throw new Error("invalid incumbent/estimate");
    return { state: "REFINE_EXISTING_AIM", reason: "AUTHORIZED_Q50_CLAMP_ON_EXISTING_V23_ACTION", price_cents: Math.min(incumbentAction.price_cents, Math.floor(estimate.q50)), incumbent_byte_identity_required: false };
  }
  if (phasedMirrorCandidate?.state === "PLACE") return { state: "EARLY_MIRROR_RELEASE", reason: "AUTHORIZED_PHASED_MIRROR_RELEASE", price_cents: phasedMirrorCandidate.price_cents, incumbent_byte_identity_required: false };
  return { state: "FALLBACK", reason: "NO_AUTHORIZED_OVERLAY_ACTION", incumbent_byte_identity_required: true };
}

module.exports = { overlayDecision };
