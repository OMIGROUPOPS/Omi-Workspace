"use strict";

const MIN_TRAINING_N = 30;
const MIN_DWELL_SECONDS = 10;
const SPREAD_CANDIDATES_CENTS = Object.freeze([1, 2, 3]);
const ASYMMETRIC_QUANTILE = 0.30;

function invariant(ok, message) {
  if (!ok) throw new Error(message);
}

function quantile(values, probability) {
  const ordered = values.filter(Number.isFinite).sort((a, b) => a - b);
  return ordered.length ? ordered[Math.floor((ordered.length - 1) * probability)] : null;
}

function asymmetricLoss(actualClose, estimate, q = ASYMMETRIC_QUANTILE) {
  invariant(Number.isFinite(actualClose) && Number.isFinite(estimate), "finite close and estimate required");
  invariant(q > 0 && q < 1, "lawful asymmetric quantile required");
  const residual = actualClose - estimate;
  return residual >= 0 ? q * residual : (1 - q) * -residual;
}

function fitCellCandidate(trainingRows, spreadCents) {
  invariant(SPREAD_CANDIDATES_CENTS.includes(spreadCents), "spread candidate must be 1/2/3 cents");
  const rows = trainingRows.filter((row) => row.reads?.[spreadCents]
    && Number.isInteger(row.audited_close_cents)
    && Number.isInteger(row.reads[spreadCents].bid));
  if (rows.length < MIN_TRAINING_N) return { state: "ABSTAIN", reason: "QUALIFIED_WALK_FORWARD_MIN_N_NOT_MET", spread_cents: spreadCents, n: rows.length };
  const deltas = rows.map((row) => row.audited_close_cents - row.reads[spreadCents].bid);
  const drift = quantile(deltas, ASYMMETRIC_QUANTILE);
  invariant(Number.isFinite(drift), "finite drift required");
  const estimatorLoss = rows.reduce((sum, row) => sum + asymmetricLoss(row.audited_close_cents, row.reads[spreadCents].bid + drift), 0) / rows.length;
  const naiveLoss = rows.reduce((sum, row) => sum + asymmetricLoss(row.audited_close_cents, row.reads[spreadCents].bid), 0) / rows.length;
  return {
    state: "BOUND",
    reason: "TRAINING_ONLY_QUALIFIED_BID_PLUS_CELL_DRIFT",
    spread_cents: spreadCents,
    cell_drift_cents: drift,
    n: rows.length,
    estimator_asymmetric_loss: estimatorLoss,
    naive_bid_asymmetric_loss: naiveLoss,
  };
}

function selectCellFit(trainingRows) {
  const candidates = SPREAD_CANDIDATES_CENTS.map((spread) => fitCellCandidate(trainingRows, spread));
  const bound = candidates.filter((candidate) => candidate.state === "BOUND")
    .sort((a, b) => a.estimator_asymmetric_loss - b.estimator_asymmetric_loss || a.spread_cents - b.spread_cents);
  if (!bound.length) return { state: "ABSTAIN", reason: "NO_SPREAD_CANDIDATE_MEETS_MIN_N", candidates };
  return { ...bound[0], candidates };
}

function estimateAtRead(fit, read) {
  if (!fit || fit.state !== "BOUND") return { state: "SILENT", reason: fit?.reason || "CELL_FIT_ABSENT" };
  const selected = read?.[fit.spread_cents];
  if (!selected) return { state: "SILENT", reason: "NO_QUALIFIED_READ_FOR_FITTED_SPREAD", spread_cents: fit.spread_cents };
  invariant(Number.isInteger(selected.bid), "qualified bid must be integer cents");
  const landing = selected.bid + fit.cell_drift_cents;
  invariant(Number.isFinite(landing), "finite landing estimate required");
  return {
    state: "BOUND",
    reason: "QUALIFIED_BID_PLUS_TRAINING_ONLY_CELL_DRIFT",
    landing_estimate_cents: landing,
    spread_cents: fit.spread_cents,
    cell_drift_cents: fit.cell_drift_cents,
    read: selected,
    training_n: fit.n,
  };
}

function authority(metrics, candidateCell) {
  if (!candidateCell) return { authorized: false, reasons: ["NOT_ANALYSIS_SEAT_CANDIDATE_CELL"] };
  const reasons = [];
  if (!(metrics.validation_n >= MIN_TRAINING_N)) reasons.push("VALIDATION_MIN_N_NOT_MET");
  if (!(metrics.non_overestimate_rate >= 0.70)) reasons.push("P_ESTIMATE_LE_CLOSE_BELOW_70_PERCENT");
  if (!(metrics.mean_overestimate_when_wrong_cents <= 2)) reasons.push("MEAN_SHORTFALL_WHEN_WRONG_ABOVE_2C");
  if (!(metrics.estimator_asymmetric_loss < metrics.naive_bid_asymmetric_loss)) reasons.push("DOES_NOT_BEAT_NAIVE_QUALIFIED_BID");
  if (!(metrics.qualified_read_coverage > 0)) reasons.push("ZERO_QUALIFIED_READ_COVERAGE");
  return { authorized: reasons.length === 0, reasons };
}

function overlayDecision({ cellAuthorized, incumbentAction, estimate, mirrorRelease }) {
  if (!cellAuthorized) return { state: "FALLBACK", reason: "CELL_AUTHORITY_BAR_NOT_PASSED", incumbent_byte_identity_required: true };
  if (!estimate || estimate.state !== "BOUND") return { state: "FALLBACK", reason: "QUALIFIED_DRIFT_READ_SILENT", incumbent_byte_identity_required: true };
  const clamp = Math.floor(estimate.landing_estimate_cents) - 1;
  if (!Number.isInteger(clamp) || clamp < 1 || clamp > 99) return { state: "FALLBACK", reason: "LANDING_MINUS_ONE_OUT_OF_RANGE", incumbent_byte_identity_required: true };
  if (incumbentAction) {
    invariant(Number.isInteger(incumbentAction.price_cents), "integer incumbent price required");
    return {
      state: "REFINE_EXISTING_AIM",
      reason: "AUTHORIZED_DRIFT_CLAMP_ON_EXISTING_V23_ACTION",
      price_cents: Math.min(incumbentAction.price_cents, clamp),
      incumbent_byte_identity_required: Math.min(incumbentAction.price_cents, clamp) === incumbentAction.price_cents,
    };
  }
  if (mirrorRelease?.state === "RELEASE") {
    return { state: "EARLY_MIRROR_RELEASE", reason: "AUTHORIZED_OWN_DECLINE_AND_COHERENT_ORDINAL", price_cents: clamp, incumbent_byte_identity_required: false };
  }
  return { state: "FALLBACK", reason: "NO_AUTHORIZED_OVERLAY_POWER_APPLIES", incumbent_byte_identity_required: true };
}

module.exports = {
  ASYMMETRIC_QUANTILE,
  MIN_DWELL_SECONDS,
  MIN_TRAINING_N,
  SPREAD_CANDIDATES_CENTS,
  asymmetricLoss,
  authority,
  estimateAtRead,
  fitCellCandidate,
  overlayDecision,
  quantile,
  selectCellFit,
};
