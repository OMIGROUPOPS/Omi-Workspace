"use strict";

const MIN_TRAINING_N = 30;
const QUANTITY = 5;
const DWELL_SECONDS = 10;

function invariant(ok, message) {
  if (!ok) throw new Error(message);
}

function quantile(values, probability) {
  const ordered = values.filter(Number.isFinite).sort((a, b) => a - b);
  return ordered.length ? ordered[Math.floor((ordered.length - 1) * probability)] : null;
}

function pathFamily(shapeIds) {
  const families = [...new Set((shapeIds || []).map((id) => {
    const match = String(id).match(/_(INTERIM_PATH_\d+)_ORD_/);
    return match ? match[1] : null;
  }).filter(Boolean))].sort();
  if (!families.length) return null;
  return families.length === 1 ? families[0] : `MIXED:${families.join("+")}`;
}

function estimateLanding(samples, decision) {
  invariant(Number.isFinite(decision.decision_ts), "decision timestamp required");
  invariant(Number.isInteger(decision.current_ask_cents), "integer current ask required");
  if (decision.identity_unresolved) return { state: "ABSTAIN", reason: "LANDING_IDENTITY_UNRESOLVED_339", q25: null, q50: null, q75: null, n: 0, borrowed_from: null };
  if (!decision.path_family) return { state: "ABSTAIN", reason: "LANDING_PATH_FAMILY_UNAVAILABLE", q25: null, q50: null, q75: null, n: 0, borrowed_from: null };
  const lawful = samples.filter((row) => row.event_id !== decision.event_id && row.close_ts < decision.decision_ts);
  const tiers = [
    { name: `${decision.category}|${decision.path_family}`, rows: lawful.filter((r) => r.category === decision.category && r.path_family === decision.path_family) },
    { name: `${decision.category}|ALL_PATH_FAMILIES`, rows: lawful.filter((r) => r.category === decision.category) },
    { name: `ALL_CATEGORIES|${decision.path_family}`, rows: lawful.filter((r) => r.path_family === decision.path_family) },
    { name: "GLOBAL_WALK_FORWARD_PARENT", rows: lawful },
  ];
  const selected = tiers.find((tier) => tier.rows.length >= MIN_TRAINING_N);
  if (!selected) return { state: "ABSTAIN", reason: "LANDING_WALK_FORWARD_MIN_N_NOT_MET", q25: null, q50: null, q75: null, n: lawful.length, borrowed_from: null };
  const deltas = selected.rows.map((row) => row.close_minus_live_ask_cents);
  const q25Delta = quantile(deltas, .25), q50Delta = quantile(deltas, .5), q75Delta = quantile(deltas, .75);
  return {
    state: "BOUND",
    reason: "CAUSAL_WALK_FORWARD_QUANTILE_SET",
    q25: decision.current_ask_cents + q25Delta,
    q50: decision.current_ask_cents + q50Delta,
    q75: decision.current_ask_cents + q75Delta,
    delta_quantiles: { q25: q25Delta, q50: q50Delta, q75: q75Delta },
    n: selected.rows.length,
    borrowed_from: selected.name,
    max_training_close_ts: Math.max(...selected.rows.map((row) => row.close_ts)),
    walk_forward_proof: Math.max(...selected.rows.map((row) => row.close_ts)) < decision.decision_ts,
  };
}

function readSideDecision({ liveBid, liveAsk, displayedAskSize, estimate }) {
  if (estimate.state !== "BOUND") return { state: "ABSTAIN", reason: estimate.reason, price_cents: null };
  invariant(Number.isInteger(liveBid) && Number.isInteger(liveAsk) && liveBid <= liveAsk, "lawful book required");
  if (!(liveAsk < estimate.q50)) return { state: "ABSTAIN", reason: "LIVE_ASK_NOT_STRICTLY_BELOW_Q50_LANDING", price_cents: null };
  if (!(displayedAskSize >= QUANTITY)) return { state: "REST", reason: "LIVE_ASK_BELOW_Q50_BUT_CAPACITY_NOT_PROVEN_AT_ACTION", price_cents: liveAsk };
  return { state: "PLACE", reason: "PRE_DECLINE_SIDE_CURRENT_ASK_STRICTLY_BELOW_Q50_LANDING", price_cents: liveAsk };
}

function mirrorAim(estimate) {
  if (estimate.state !== "BOUND") return { state: "ABSTAIN", reason: estimate.reason, aim_cents: null };
  const aim = Math.ceil(estimate.q50) - 1;
  if (!Number.isInteger(aim) || aim < 1 || aim > 99) return { state: "ABSTAIN", reason: "STRICT_BELOW_Q50_AIM_OUT_OF_RANGE", aim_cents: null };
  return { state: "HOLD", reason: "MIRROR_AIM_ARMED_AWAITING_OWN_DECLINE_ORDINAL", aim_cents: aim };
}

function pairCap({ aimCents, firstFillCents, liveBid, liveAsk }) {
  for (const [name, value] of Object.entries({ aimCents, firstFillCents, liveBid, liveAsk })) invariant(Number.isInteger(value), `${name} integer required`);
  invariant(liveBid <= liveAsk, "crossed live book");
  const cap = 99 - firstFillCents;
  const selected = Math.min(aimCents, cap);
  if (selected < liveBid) return { state: "ABSTAIN", reason: "PAIR_CAP_OR_AIM_BELOW_LIVE_BID_UNREACHABLE_NO_CHASE", cap_cents: cap, selected_cents: null };
  return { state: "PLACE", reason: "OWN_DECLINE_RELEASE_AND_PAIR_CAP_REACHABLE", cap_cents: cap, selected_cents: selected };
}

function displayedCapacityAtOrBelow(asks, target) {
  return Array.isArray(asks) ? asks.filter(([price]) => price <= target).reduce((sum, [, size]) => sum + size, 0) : 0;
}

function findLaterFill(rows, actionTs, actionReceipt, target) {
  let ask = null, episodeStart = null;
  for (const row of rows) {
    if (row.ask !== ask) { ask = row.ask; episodeStart = row.ts; }
    const capacity = displayedCapacityAtOrBelow(row.asks, target);
    if (row.ts > actionTs && row.receipt !== actionReceipt && row.ask <= target && row.ts - episodeStart >= DWELL_SECONDS && capacity >= QUANTITY) {
      return { timestamp_epoch: row.ts, receipt: row.receipt, ask_cents: row.ask, ask_dwell_seconds: row.ts - episodeStart, displayed_capacity: capacity };
    }
  }
  return null;
}

module.exports = {
  DWELL_SECONDS,
  MIN_TRAINING_N,
  QUANTITY,
  estimateLanding,
  findLaterFill,
  mirrorAim,
  pairCap,
  pathFamily,
  quantile,
  readSideDecision,
};
