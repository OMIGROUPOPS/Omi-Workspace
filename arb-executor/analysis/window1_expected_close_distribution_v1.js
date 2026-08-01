"use strict";

// Score-free empirical Window-1-close distribution. The estimator consumes
// only causal, decision-time features. Every historical leg contributes at
// most one (closest) residual to a query distribution.

const FEATURE_NAMES = [
  "bid", "ask", "spread", "log_ask_size", "log_top5_ask_depth",
  "log_ask_dwell", "log_quote_rate", "log_ask_change_rate",
  "last_missing", "last_minus_mid", "last_at_or_below_bid", "last_at_or_above_ask",
  "log_executed_volume", "log_print_rate", "time_to_scheduled_hours",
  "sibling_missing", "sibling_bid", "sibling_ask", "sibling_spread",
  "sibling_log_ask_size", "sibling_log_top5_ask_depth", "sibling_log_ask_dwell",
  "sibling_log_quote_rate", "sibling_last_missing", "sibling_last_minus_mid",
  "sibling_log_executed_volume", "pair_ask_sum"
];

function finite(value, label) {
  const n = Number(value);
  if (!Number.isFinite(n)) throw new Error(`non-finite ${label}`);
  return n;
}
function median(values) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b), middle = (sorted.length - 1) / 2;
  const lo = Math.floor(middle), hi = Math.ceil(middle);
  return (sorted[lo] + sorted[hi]) / 2;
}
function weightedQuantile(rows, q) {
  if (!rows.length) return null;
  const sorted = [...rows].sort((a, b) => a.value - b.value || a.identity.localeCompare(b.identity));
  const total = sorted.reduce((sum, row) => sum + row.weight, 0);
  let running = 0;
  for (const row of sorted) { running += row.weight; if (running >= total * q) return row.value; }
  return sorted[sorted.length - 1].value;
}
function region(price) {
  const p = Number(price);
  if (!Number.isInteger(p) || p < 1 || p > 99) return "UNKNOWN";
  return p <= 25 ? "LE25" : p <= 50 ? "26_50" : p <= 75 ? "51_75" : "GE76";
}
function jaccardDistance(left, right) {
  const a = new Set(left || []), b = new Set(right || []), union = new Set([...a, ...b]);
  if (!union.size) return 0;
  let intersection = 0; for (const value of a) if (b.has(value)) intersection += 1;
  return 1 - intersection / union.size;
}
function vector(row) {
  return FEATURE_NAMES.map((name) => finite(row.features[name], `feature ${name}`));
}
function fitExpectedCloseModel(rows) {
  const groups = {};
  for (const row of rows) {
    if (!Number.isInteger(row.close_cents) || !Number.isInteger(row.ask_cents)) throw new Error("training row lacks exact close/ask");
    const key = `${row.category}|${row.price_region}`;
    if (!groups[key]) groups[key] = { rows: [] };
    groups[key].rows.push({ ...row, feature_vector: vector(row), close_delta_cents: row.close_cents - row.ask_cents });
  }
  for (const [key, group] of Object.entries(groups)) {
    const centers = FEATURE_NAMES.map((_, index) => median(group.rows.map((row) => row.feature_vector[index])));
    const scales = FEATURE_NAMES.map((_, index) => {
      const mad = median(group.rows.map((row) => Math.abs(row.feature_vector[index] - centers[index])));
      return Math.max(1, mad * 1.4826);
    });
    group.centers = centers; group.scales = scales;
    group.training_legs = new Set(group.rows.map((row) => row.leg_identity)).size;
    group.training_events = new Set(group.rows.map((row) => row.event_id)).size;
    group.rows.sort((a, b) => a.leg_identity.localeCompare(b.leg_identity) || a.ts - b.ts);
  }
  return { schema_version: "WINDOW1_EXPECTED_CLOSE_EMPIRICAL_MODEL_V1", feature_names: FEATURE_NAMES, groups };
}
function predictExpectedClose(model, query) {
  const key = `${query.category}|${query.price_region}`, group = model.groups[key];
  if (!group) return { status: "NO_CALL_NO_CATEGORY_PRICE_REGION_SUPPORT", key };
  const qv = vector(query), bestByLeg = new Map();
  for (const row of group.rows) {
    let distance2 = 0;
    for (let index = 0; index < qv.length; index += 1) {
      const z = (qv[index] - row.feature_vector[index]) / group.scales[index]; distance2 += z * z;
    }
    const shapeDistance = jaccardDistance(query.surviving_shapes, row.surviving_shapes);
    distance2 += shapeDistance * shapeDistance;
    const distance = Math.sqrt(distance2), prior = bestByLeg.get(row.leg_identity);
    if (!prior || distance < prior.distance || (distance === prior.distance && row.ts < prior.row.ts)) bestByLeg.set(row.leg_identity, { row, distance });
  }
  const support = [...bestByLeg.values()].map(({ row, distance }) => ({
    identity: row.leg_identity,
    value: row.close_delta_cents,
    weight: 1 / (1 + distance),
    distance,
    source_ts: row.ts,
  }));
  if (!support.length) return { status: "NO_CALL_NO_INDEPENDENT_LEG_SUPPORT", key };
  const sumWeight = support.reduce((sum, row) => sum + row.weight, 0), sumSquared = support.reduce((sum, row) => sum + row.weight ** 2, 0);
  const deltas = Object.fromEntries([0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95].map((q) => [String(q), weightedQuantile(support, q)]));
  const meanDelta = support.reduce((sum, row) => sum + row.value * row.weight, 0) / sumWeight;
  return {
    status: "DISTRIBUTION_AVAILABLE_UNVALIDATED",
    key,
    ask_cents: query.ask_cents,
    independent_training_legs: support.length,
    effective_sample_size: sumWeight * sumWeight / sumSquared,
    close_delta_quantiles_cents: deltas,
    close_quantiles_cents: Object.fromEntries(Object.entries(deltas).map(([q, delta]) => [q, query.ask_cents + delta])),
    weighted_mean_close_delta_cents: meanDelta,
    weighted_mean_close_cents: query.ask_cents + meanDelta,
  };
}

module.exports = { FEATURE_NAMES, fitExpectedCloseModel, predictExpectedClose, region, weightedQuantile };
