"use strict";

// Pair hypotheses are causal, synchronized two-book hypotheses.  Price regions
// are deliberately absent from their identity and runtime lookup.
const PAIR_ROLE_KEYS = [
  "ask_net", "ask_dip", "ask_peak", "ask_drawdown_from_peak",
  "mean_spread", "spread_range", "quote_rate", "ask_change_rate",
  "ask_dwell_fraction", "mean_log_top_ask_size", "mean_log_top5_ask_depth",
  "qualified_ask_descent_count", "qualified_ask_rise_count", "current_ask",
];
const PAIR_MACRO_KEYS = [
  "high_ask_net", "high_ask_dip", "high_ask_peak", "high_ask_drawdown_from_peak",
  "low_ask_net", "low_ask_dip", "low_ask_peak", "low_ask_drawdown_from_peak",
  "ask_sum", "ask_net_sum",
];

function pairFeatures(highRow, lowRow) {
  if (!highRow?.prefix || !lowRow?.prefix) return null;
  const out = {};
  for (const [role, row] of [["high", highRow], ["low", lowRow]]) {
    for (const key of PAIR_ROLE_KEYS) {
      const value = key === "current_ask" ? row.ask : row.prefix[key];
      out[`${role}_${key}`] = value;
    }
    out[`${role}_spread`] = row.spread;
    out[`${role}_top_ask_size`] = row.top_ask_size;
    out[`${role}_top5_ask_depth`] = row.top5_ask_depth;
    out[`${role}_ask_dwell_seconds`] = row.ask_dwell_seconds;
  }
  out.ask_sum = highRow.ask + lowRow.ask;
  out.ask_net_sum = highRow.prefix.ask_net + lowRow.prefix.ask_net;
  out.spread_sum = highRow.spread + lowRow.spread;
  return out;
}

function matchesPairEnvelope(hypothesis, highRow, lowRow, bin) {
  const features = pairFeatures(highRow, lowRow), envelope = hypothesis?.joint_interim_envelopes?.[bin];
  if (!features || !envelope) return false;
  return PAIR_MACRO_KEYS.every((key) => Array.isArray(envelope[key]) && Number.isFinite(features[key]) && features[key] >= envelope[key][0] && features[key] <= envelope[key][1]);
}

function pairTuples(hypotheses, highShapes, lowShapes) {
  const high = new Set(highShapes), low = new Set(lowShapes), rows = new Map();
  for (const hypothesis of hypotheses) for (const pair of hypothesis.member_single_shape_pairs || []) {
    if (!high.has(pair.high_shape_id) || !low.has(pair.low_shape_id)) continue;
    const key = `${pair.high_shape_id}|${pair.low_shape_id}`;
    const prior = rows.get(key) || { highShape: pair.high_shape_id, lowShape: pair.low_shape_id, n: 0, pair_hypothesis_ids: [], support_class: "SYNCHRONIZED_PAIR_INTERIM_HYPOTHESIS" };
    prior.n += pair.n;
    if (!prior.pair_hypothesis_ids.includes(hypothesis.pair_hypothesis_id)) prior.pair_hypothesis_ids.push(hypothesis.pair_hypothesis_id);
    rows.set(key, prior);
  }
  return [...rows.values()].map((row) => ({ ...row, pair_hypothesis_ids: row.pair_hypothesis_ids.sort() })).sort((a, b) => b.n - a.n || a.highShape.localeCompare(b.highShape) || a.lowShape.localeCompare(b.lowShape));
}

function mutuallyNarrowPairAndLegs({ group, priorPairIds, highShapes, lowShapes, highRow, lowRow, bin }) {
  if (!group || !highRow || !lowRow) return { status: "PAIR_SOURCE_PENDING", pair_survivor_ids: priorPairIds || [], signable_pair_survivor_ids: [], high_shapes: highShapes, low_shapes: lowShapes, tuples: [] };
  const byId = new Map(group.hypotheses.map((row) => [row.pair_hypothesis_id, row]));
  const starting = (priorPairIds?.length ? priorPairIds : group.hypotheses.map((row) => row.pair_hypothesis_id)).map((id) => byId.get(id)).filter(Boolean);
  let survivors = starting.filter((hypothesis) => matchesPairEnvelope(hypothesis, highRow, lowRow, bin));
  if (!survivors.length && priorPairIds?.length) survivors = group.hypotheses.filter((hypothesis) => matchesPairEnvelope(hypothesis, highRow, lowRow, bin));
  const signable = survivors.filter((hypothesis) => hypothesis.usable_for_signing);
  if (!signable.length) return { status: "PAIR_HYPOTHESIS_UNRESOLVED", pair_survivor_ids: survivors.map((x) => x.pair_hypothesis_id), signable_pair_survivor_ids: [], high_shapes: highShapes, low_shapes: lowShapes, tuples: [] };

  let narrowedHigh = [...highShapes], narrowedLow = [...lowShapes], active = signable;
  for (let pass = 0; pass < 4; pass += 1) {
    const tuples = pairTuples(active, narrowedHigh, narrowedLow);
    const allowedHigh = new Set(tuples.map((x) => x.highShape)), allowedLow = new Set(tuples.map((x) => x.lowShape));
    const nextHigh = narrowedHigh.filter((id) => allowedHigh.has(id)), nextLow = narrowedLow.filter((id) => allowedLow.has(id));
    const nextActive = active.filter((hypothesis) => (hypothesis.member_single_shape_pairs || []).some((pair) => nextHigh.includes(pair.high_shape_id) && nextLow.includes(pair.low_shape_id)));
    if (!nextHigh.length || !nextLow.length || !nextActive.length) return { status: "PAIR_SINGLE_LIBRARY_CONTRADICTION", pair_survivor_ids: survivors.map((x) => x.pair_hypothesis_id), signable_pair_survivor_ids: [], high_shapes: highShapes, low_shapes: lowShapes, tuples: [] };
    const stable = nextHigh.join("|") === narrowedHigh.join("|") && nextLow.join("|") === narrowedLow.join("|") && nextActive.length === active.length;
    narrowedHigh = nextHigh; narrowedLow = nextLow; active = nextActive;
    if (stable) break;
  }
  return { status: "PAIR_AND_SINGLE_LIBRARIES_MUTUALLY_NARROWED", pair_survivor_ids: survivors.map((x) => x.pair_hypothesis_id), signable_pair_survivor_ids: active.map((x) => x.pair_hypothesis_id), high_shapes: narrowedHigh, low_shapes: narrowedLow, tuples: pairTuples(active, narrowedHigh, narrowedLow) };
}

module.exports = { PAIR_ROLE_KEYS, PAIR_MACRO_KEYS, pairFeatures, matchesPairEnvelope, pairTuples, mutuallyNarrowPairAndLegs };
