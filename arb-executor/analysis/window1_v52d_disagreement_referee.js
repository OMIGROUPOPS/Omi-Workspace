"use strict";

// V52d changes exactly clause 4. V52c's full post-onset read and V52b's
// level authority are inherited unchanged. The referee uses only causal,
// in-game evidence present at the evaluation receipt. No historical prior,
// post-bell evidence, or Palantir/N9 input is accepted.

const v52c = require("./window1_v52c_full_post_onset_read.js");

const EVIDENCE_CLASS_RANK = Object.freeze({ DEPTH_PRESSURE: 1, QUOTE_PATH: 2, PRINT_BACKED: 3 });

function normalizedClauses(value = {}) {
  const clauses = v52c.normalizedClauses(value);
  return value.disagreement_referee ? { ...clauses, disagreement_referee: true } : clauses;
}

function emptyReadState(onsetTimestampEpoch) {
  return { ...v52c.emptyReadState(onsetTimestampEpoch), referee_support_by_direction: { RISING: null, FALLING: null } };
}

function evidenceClass(kind) {
  if (typeof kind !== "string") return null;
  if (kind.includes("PRINT")) return "PRINT_BACKED";
  if (kind.includes("BID_") || kind.includes("ASK_")) return "QUOTE_PATH";
  return null;
}

function observePostOnsetEvidence(state, row) {
  v52c.observePostOnsetEvidence(state, row);
  const evidence = state.last_directional_evidence;
  if (evidence && ["RISING", "FALLING"].includes(evidence.direction)) {
    const klass = evidenceClass(evidence.kind);
    if (klass) state.referee_support_by_direction[evidence.direction] = { ...evidence, evidence_class: klass, evidence_class_rank: EVIDENCE_CLASS_RANK[klass] };
  }
  return state;
}

function pressureBacking(pressure, row) {
  if (!["RISING", "FALLING"].includes(pressure) || !Number.isFinite(row?.depth_ratio) || !Number.isFinite(row?.ts) || typeof row?.receipt !== "string") return null;
  return {
    reading: pressure,
    evidence_class: "DEPTH_PRESSURE",
    evidence_class_rank: EVIDENCE_CLASS_RANK.DEPTH_PRESSURE,
    timestamp_epoch: row.ts,
    receipt: row.receipt,
    magnitude: Math.abs(row.depth_ratio - 0.5),
    magnitude_unit: "ABS_DEPTH_RATIO_DISTANCE_FROM_BALANCE_0_5",
    depth_ratio: row.depth_ratio,
    source: "CURRENT_RECEIPT_JUL6_DEPTH_PRESSURE",
  };
}

function quoteBacking(quote, readState) {
  const evidence = ["RISING", "FALLING"].includes(quote?.state) ? readState?.referee_support_by_direction?.[quote.state] : null;
  if (!evidence || !["RISING", "FALLING"].includes(quote?.state)) return null;
  return {
    reading: quote.state,
    evidence_class: evidence.evidence_class,
    evidence_class_rank: evidence.evidence_class_rank,
    timestamp_epoch: evidence.timestamp_epoch,
    receipt: evidence.receipt,
    magnitude: evidence.magnitude_cents,
    magnitude_unit: "CENTS",
    causal_rank: evidence.causal_rank,
    kind: evidence.kind,
    source: "FULL_POST_ONSET_READ_SUPPORTING_RECEIPT",
  };
}

function compareBacking(left, right) {
  if (!left && !right) return { comparison_field: "NO_BACKING", result: 0 };
  if (left && !right) return { comparison_field: "BACKING_PRESENT", result: 1 };
  if (!left && right) return { comparison_field: "BACKING_PRESENT", result: -1 };
  for (const field of ["evidence_class_rank", "timestamp_epoch", "magnitude"]) {
    if (left[field] > right[field]) return { comparison_field: field, result: 1 };
    if (left[field] < right[field]) return { comparison_field: field, result: -1 };
  }
  return { comparison_field: "EXACT_TIE", result: 0 };
}

function adjudicateDisagreement({ quote, pressure, row, readState }) {
  const firing = ["RISING", "FALLING"].includes(quote?.state) && ["RISING", "FALLING"].includes(pressure) && quote.state !== pressure;
  if (!firing) return { enabled: true, firing: false, status: "NOT_FIRED", resolved: false, winner: null, loser: null, comparison: null, palantir_priors_consumed: false, historical_inputs_consumed: false };
  const quoteEvidence = quoteBacking(quote, readState);
  const pressureEvidence = pressureBacking(pressure, row);
  const comparison = compareBacking(quoteEvidence, pressureEvidence);
  const winner = comparison.result > 0 ? quoteEvidence : comparison.result < 0 ? pressureEvidence : null;
  const loser = comparison.result > 0 ? pressureEvidence : comparison.result < 0 ? quoteEvidence : null;
  return {
    enabled: true,
    firing: true,
    status: winner ? "ADJUDICATED_STRICTLY_STRONGER_BACKING" : "HONEST_TIE_FREEZE_STANDS",
    resolved: Boolean(winner),
    winner,
    loser,
    comparison: {
      ordering: ["EVIDENCE_CLASS_PRINT_GT_QUOTE_GT_DEPTH", "RECENCY_OF_BACKING_RECEIPT", "MAGNITUDE_OF_EVIDENCING_MOVE"],
      decisive_field: comparison.comparison_field,
      result: comparison.result,
      strict: comparison.result !== 0,
    },
    evaluation_receipt: row.receipt,
    evaluation_timestamp_epoch: row.ts,
    palantir_priors_consumed: false,
    N9_post_bell_consumed: false,
    historical_inputs_consumed: false,
  };
}

module.exports = { ...v52c, EVIDENCE_CLASS_RANK, normalizedClauses, emptyReadState, observePostOnsetEvidence, evidenceClass, compareBacking, adjudicateDisagreement };
