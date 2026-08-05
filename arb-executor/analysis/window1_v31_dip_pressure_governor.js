"use strict";

const HALFLIFE_SECONDS = 120;
const TRAINING_DIP_HORIZON_SECONDS = 600;
const MIN_TRAIN_ROWS = 40;
const MIN_AUTHORITY_HIGH_ROWS = 20;
const MIN_AUTHORITY_PRECISION_LIFT = 0.05;
const FEATURE_NAMES = ["cross", "lock", "bid_dom", "ask_dom", "ask_stair", "bid_stair"];

function finite(name, value) {
  if (!Number.isFinite(value)) throw new Error(`${name} finite required`);
  return value;
}

function sigmoid(x) {
  if (x >= 0) return 1 / (1 + Math.exp(-Math.min(40, x)));
  const e = Math.exp(Math.max(-40, x));
  return e / (1 + e);
}

function rawBands(previous, row) {
  for (const name of ["bid", "ask", "top_bid_depth", "top_ask_depth"]) finite(name, row[name]);
  const crossed = row.bid > row.ask;
  const locked = row.bid === row.ask;
  const depthTotal = Math.max(1, row.top_bid_depth + row.top_ask_depth);
  return {
    cross: crossed ? 1 : 0,
    lock: locked ? 1 : 0,
    bid_dom: row.top_bid_depth / depthTotal,
    ask_dom: row.top_ask_depth / depthTotal,
    ask_stair: previous && row.ask < previous.ask ? 1 : 0,
    bid_stair: previous && row.bid > previous.bid ? 1 : 0,
  };
}

function updateEwma(previousState, previousTimestamp, row) {
  const raw = rawBands(previousState?.book || null, row);
  if (!previousState) return { ...raw, book: { bid: row.bid, ask: row.ask }, timestamp: row.ts };
  const dt = Math.max(0, finite("timestamp delta", row.ts - previousTimestamp));
  const decay = Math.exp(-Math.log(2) * dt / HALFLIFE_SECONDS);
  const out = { book: { bid: row.bid, ask: row.ask }, timestamp: row.ts };
  for (const name of FEATURE_NAMES) out[name] = decay * previousState[name] + (1 - decay) * raw[name];
  return out;
}

function featureVector(state) {
  return [1, ...FEATURE_NAMES.map((name) => finite(name, state[name]))];
}

function dot(weights, x) {
  return weights.reduce((sum, weight, index) => sum + weight * x[index], 0);
}

function predict(weights, x) {
  return sigmoid(dot(weights, x));
}

function onlineUpdate(weights, x, label, seen) {
  if (!(label === 0 || label === 1)) throw new Error("binary label required");
  const probability = predict(weights, x);
  const rate = 0.35 / Math.sqrt(Math.max(1, seen + 1));
  const next = [...weights];
  for (let i = 0; i < next.length; i += 1) {
    const regularization = i === 0 ? 0 : 0.0005 * weights[i];
    next[i] += rate * ((label - probability) * x[i] - regularization);
  }
  return next;
}

function median(values) {
  const sorted = values.filter(Number.isFinite).sort((a, b) => a - b);
  if (!sorted.length) return null;
  return sorted[Math.floor((sorted.length - 1) / 2)];
}

function fitThreshold(history) {
  if (history.length < MIN_TRAIN_ROWS) return null;
  const baseRate = history.reduce((sum, row) => sum + row.label, 0) / history.length;
  const candidates = [...new Set(history.map((row) => row.probability))].sort((a, b) => a - b);
  let best = null;
  for (const threshold of candidates) {
    const selected = history.filter((row) => row.probability >= threshold);
    if (selected.length < MIN_AUTHORITY_HIGH_ROWS) continue;
    const tp = selected.reduce((sum, row) => sum + row.label, 0);
    const precision = tp / selected.length;
    const recallDenominator = history.reduce((sum, row) => sum + row.label, 0);
    const recall = recallDenominator ? tp / recallDenominator : 0;
    const f1 = precision + recall ? 2 * precision * recall / (precision + recall) : 0;
    const depth = median(selected.filter((row) => row.label === 1).map((row) => row.deeper_floor_drop_cents));
    if (!Number.isInteger(depth) || depth < 1) continue;
    const candidate = { threshold, training_n: history.length, selected_n: selected.length, base_rate: baseRate, precision, precision_lift: precision - baseRate, recall, f1, pressure_implied_drop_cents: depth };
    if (!best || candidate.precision_lift > best.precision_lift || (candidate.precision_lift === best.precision_lift && candidate.f1 > best.f1) || (candidate.precision_lift === best.precision_lift && candidate.f1 === best.f1 && candidate.threshold > best.threshold)) best = candidate;
  }
  return best;
}

function authorityVerdict(rows) {
  const eligible = rows.filter((row) => row.walkforward_scored && row.pressure_state === "HIGH");
  const scored = rows.filter((row) => row.walkforward_scored);
  const baseRate = scored.length ? scored.reduce((sum, row) => sum + row.label, 0) / scored.length : null;
  const precision = eligible.length ? eligible.reduce((sum, row) => sum + row.label, 0) / eligible.length : null;
  const observedLift = precision === null || baseRate === null ? null : precision - baseRate;
  const earned = eligible.length >= MIN_AUTHORITY_HIGH_ROWS && observedLift >= MIN_AUTHORITY_PRECISION_LIFT;
  return {
    earned,
    heldout_scored_n: scored.length,
    heldout_high_n: eligible.length,
    heldout_positive_n: scored.reduce((sum, row) => sum + row.label, 0),
    heldout_high_true_positive_n: eligible.reduce((sum, row) => sum + row.label, 0),
    heldout_base_rate: baseRate,
    heldout_high_precision: precision,
    observed_precision_lift: observedLift,
    required_margin: MIN_AUTHORITY_PRECISION_LIFT,
    authority_bar: `heldout_high_n>=${MIN_AUTHORITY_HIGH_ROWS} AND precision-base_rate>=${MIN_AUTHORITY_PRECISION_LIFT}`,
  };
}

function governBuy({ authority, pressureState, currentPriceCents, impliedDropCents }) {
  if (!authority?.earned) return { decision: "UNCHANGED", reason: "CATEGORY_GOVERNOR_AUTHORITY_NOT_EARNED", target_cents: null };
  if (pressureState !== "HIGH") return { decision: "UNCHANGED", reason: "DIP_PRESSURE_LOW", target_cents: null };
  if (!Number.isInteger(currentPriceCents) || currentPriceCents < 2) throw new Error("integer buy price at least two required");
  if (!Number.isInteger(impliedDropCents) || impliedDropCents < 1) throw new Error("positive integer pressure-implied drop required");
  return {
    decision: "DEMOTE",
    reason: "HIGH_DIP_PRESSURE_WITH_EARNED_CATEGORY_AUTHORITY",
    target_cents: Math.max(1, currentPriceCents - impliedDropCents),
    target_law: "max(1,current_buy_price-pressure_implied_training_median_deeper_floor_drop)",
    re_evaluation_cadence: "EVERY_CAUSAL_OWN_BOOK_RECEIPT",
    clock_inputs: [],
  };
}

module.exports = {
  HALFLIFE_SECONDS,
  TRAINING_DIP_HORIZON_SECONDS,
  MIN_TRAIN_ROWS,
  MIN_AUTHORITY_HIGH_ROWS,
  MIN_AUTHORITY_PRECISION_LIFT,
  FEATURE_NAMES,
  rawBands,
  updateEwma,
  featureVector,
  predict,
  onlineUpdate,
  fitThreshold,
  authorityVerdict,
  governBuy,
};
