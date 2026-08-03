"use strict";

const MACRO_KEYS = ["ask_net", "ask_dip", "ask_peak", "ask_drawdown_from_peak"];
const MICRO_MICRO_KEYS = ["ask_dwell_seconds", "top_ask_size", "top5_ask_depth", "spread", "quote_rate", "ask_change_rate", "same_price_receipt_count", "episode_distinct_bbo_states", "episode_distinct_size_values", "seconds_since_prior_receipt"];

function macroState(prefix) {
  if (!prefix) return "UNAVAILABLE";
  if (prefix.ask_net === 0 && prefix.ask_drawdown_from_peak === 0) return "ANCHOR_OR_UNMOVED";
  if (prefix.ask_net > 0 && prefix.ask_drawdown_from_peak === 0) return "AT_RISING_PEAK";
  if (prefix.ask_net > 0) return "PULLBACK_ABOVE_ANCHOR";
  if (prefix.ask_net === 0) return "RETURNED_TO_ANCHOR_FROM_PEAK";
  if (prefix.ask_net === prefix.ask_dip) return "AT_DESCENDING_LOW";
  return "REBOUND_BELOW_ANCHOR";
}

function matchesMacroEnvelope(shape, row, bin) {
  const envelope = shape.interim_envelopes?.[bin];
  if (!envelope || !row?.prefix) return false;
  if (!(envelope.macro_states || []).includes(macroState(row.prefix))) return false;
  return MACRO_KEYS.every((key) => Array.isArray(envelope[key]) && row.prefix[key] >= envelope[key][0] && row.prefix[key] <= envelope[key][1]);
}

function ordinalVerdict(shape, observedQualifiedDescents) {
  const fitted = shape.descent_to_final_reachable_low;
  if (!shape.usable_for_signing) return { verdict: "UNKNOWN", reason: "INTERIM_PATH_UNUSABLE_THIN_OR_HETEROGENEOUS" };
  if (!Number.isInteger(observedQualifiedDescents) || !Number.isInteger(fitted?.min) || !Number.isInteger(fitted?.max)) return { verdict: "UNKNOWN", reason: "QUALIFIED_DESCENT_ORDINAL_UNAVAILABLE" };
  if (observedQualifiedDescents < fitted.min) return { verdict: "LOWER", reason: "COHERENT_PATH_REQUIRES_MORE_QUALIFIED_DESCENTS" };
  if (observedQualifiedDescents >= fitted.max) return { verdict: "FLOOR", reason: "COHERENT_PATH_ORDINAL_REACHED" };
  return { verdict: "UNKNOWN", reason: "ADJACENT_ORDINAL_PATH_MEMBERS_DISAGREE" };
}

function microMicroFeatures(row) {
  return {
    ask_dwell_seconds: row.ask_dwell_seconds,
    top_ask_size: row.top_ask_size,
    top5_ask_depth: row.top5_ask_depth,
    spread: row.spread,
    quote_rate: row.prefix?.quote_rate,
    ask_change_rate: row.prefix?.ask_change_rate,
    same_price_receipt_count: row.same_price_receipt_count,
    episode_distinct_bbo_states: row.episode_distinct_bbo_states,
    episode_distinct_size_values: row.episode_distinct_size_values,
    seconds_since_prior_receipt: row.seconds_since_prior_receipt,
  };
}

function traverseMicroModel(model, features) {
  if (!model?.tree) return { verdict: "INSUFFICIENT_EVIDENCE", reason: "MICRO_MICRO_MODEL_UNAVAILABLE", leaf_id: null };
  let node = model.tree;
  while (node.type === "SPLIT") {
    const value = features[node.feature];
    if (!Number.isFinite(value)) return { verdict: "INSUFFICIENT_EVIDENCE", reason: `MICRO_MICRO_FEATURE_UNAVAILABLE:${node.feature}`, leaf_id: null };
    node = value <= node.threshold ? node.left : node.right;
  }
  return { verdict: node.verdict, reason: node.verdict === "READY" ? "FITTED_NEXT_RECEIPT_MAJORITY_EXECUTABLE" : node.verdict === "NOT_READY" ? "FITTED_NEXT_RECEIPT_MAJORITY_NOT_EXECUTABLE" : "FITTED_NEXT_RECEIPT_TIE_OR_UNAVAILABLE", leaf_id: node.leaf_id, fit_rate: node.fit_rate, fit_samples: node.samples, fit_unique_legs: node.unique_legs };
}

module.exports = { MACRO_KEYS, MICRO_MICRO_KEYS, macroState, matchesMacroEnvelope, ordinalVerdict, microMicroFeatures, traverseMicroModel };
