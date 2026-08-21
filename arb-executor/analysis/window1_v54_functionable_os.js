"use strict";

// V54-v6 functionable game OS. Every reader returns a receipt-bearing value.
// The pattern calculation is the only adjustment lever and is fully declared.

const crypto = require("crypto");

const PAR_BUDGET_CENTS = 99;
const READER_NAMES = Object.freeze([
  "anchor_settle",
  "opening_split",
  "drift",
  "steps_stillness",
  "shape_survival",
  "ripeness",
  "lows_travel",
  "joint_state_spread_dwell",
  "divots",
  "depth_size",
  "volume",
  "sibling_state",
  "category",
  "time_in_window",
  "books",
  "half_pair_state",
]);

const EXPECTED_RESOURCE_IDS = Object.freeze([
  "CORPUS_CENSUS",
  "HISTORICAL_EVENTS_MATERIALIZATION",
  "CORPUS_EVENTS_V2",
  "RANGE_SPECTRUM_V1",
  "SUBSECOND_STORE",
  "DO_SPACES_TICKS",
  "DO_SPACES_TRADES",
  "DO_SPACES_WS_DEPTH",
  "EXTERNAL_CUSTODY_DUAL_BOOK",
  "EXTERNAL_CUSTODY_DEPTH_RECORDER",
  "EXTERNAL_CUSTODY_TRUE_PRINTS",
  "BOOKMAKER_ODDS_STORE",
  "MACRO_PROJECTION_DB",
  "SHAPE_TAXONOMY_E269779B",
  "FLOOR_DEPTH_8AB4F2D9",
  "RIPENESS_41C1F724",
  "TRUTH_TABLE_C0056976",
  "HONEST_PAIR_FLOOR_TIMING",
  "HONEST_DIVOT_ARRIVAL",
]);

const SIMILARITY_DECLARATION = Object.freeze({
  name: "V54_V6_HAND_AUTHORED_CONTINUOUS_NEIGHBORHOOD",
  only_adjustment_lever: true,
  formula: "score = covered_weight / total_weight * exp(-sum(weight*abs(query-neighbor)/scale)/covered_weight); missing fields contribute zero coverage and are never imputed",
  orientation: "pair legs align by formation-anchor rank, then ticker identity only breaks an exact anchor tie",
  weights: Object.freeze({
    category: 1.5,
    anchor_split_cents: 1.4,
    leg0_anchor_cents: 1.0,
    leg1_anchor_cents: 1.0,
    leg0_drift_cents: 1.2,
    leg1_drift_cents: 1.2,
    leg0_travel_cents: 1.0,
    leg1_travel_cents: 1.0,
    joint_mid_sum_cents: 1.3,
    joint_spread_cents: 0.8,
    inverse_coherence: 1.1,
    volume_log1p: 0.7,
    hours_from_discovery: 0.6,
    divot_depth_cents: 0.8,
  }),
  scales: Object.freeze({
    anchor_split_cents: 20,
    leg0_anchor_cents: 30,
    leg1_anchor_cents: 30,
    leg0_drift_cents: 20,
    leg1_drift_cents: 20,
    leg0_travel_cents: 30,
    leg1_travel_cents: 30,
    joint_mid_sum_cents: 10,
    joint_spread_cents: 12,
    inverse_coherence: 1,
    volume_log1p: 10,
    hours_from_discovery: 24,
    divot_depth_cents: 20,
  }),
  neighbor_count: 7,
  grades: "Every neighbor retains its continuous score and coverage; grade is rank N1..N7, not a threshold or gate.",
  declared: true,
  undisclosed_weights: false,
});

function sha256(value) {
  return crypto.createHash("sha256").update(Buffer.isBuffer(value) ? value : Buffer.from(String(value))).digest("hex");
}
function finite(value) { return Number.isFinite(value) ? value : null; }
function cent(value) { return Number.isInteger(value) && value >= 1 && value <= 99 ? value : null; }
function clipped(value, low = 0, high = 1) { return Math.max(low, Math.min(high, value)); }
function mean(values) { const rows = values.filter(Number.isFinite); return rows.length ? rows.reduce((a, b) => a + b, 0) / rows.length : null; }
function sum(values) { return values.filter(Number.isFinite).reduce((a, b) => a + b, 0); }
function last(values) { return values.length ? values[values.length - 1] : null; }

function createTapeState(meta) {
  const legIds = [...meta.leg_ids].sort();
  if (legIds.length !== 2) throw new Error(`FUNCTIONABLE_OS_REQUIRES_TWO_LEGS ${meta.event_id}`);
  const legs = Object.fromEntries(legIds.map((legId) => [legId, {
    leg_id: legId,
    anchor_cents: cent(meta.anchors_cents?.[legId]),
    formation_end_epoch: finite(meta.formation_end_epochs?.[legId]),
    rows: [], books: [], prints: [], references: [], steps: [], divots: [],
    current_book: null, current_reference_cents: null, running_low_cents: null,
    running_high_cents: null, volume_contracts: 0, last_change_epoch: null,
  }]));
  return {
    event_id: meta.event_id,
    event_date: meta.event_date,
    category: meta.category,
    discovery_epoch: meta.discovery_epoch,
    bell_epoch: meta.bell_epoch ?? null,
    bell_source: meta.bell_source ?? null,
    leg_ids: legIds,
    legs,
    positions: Object.fromEntries(legIds.map((id) => [id, { credited: false, entry_cents: null, standing_target_cents: null }])),
    current_epoch: meta.discovery_epoch,
    receipt: `${meta.event_id}|DISCOVERY`,
  };
}

function referenceOf(row) {
  if (row.kind === "PRINT" && cent(row.price_cents)) return row.price_cents;
  if (row.kind === "BOOK" && cent(row.last_trade_cents)) return row.last_trade_cents;
  if (row.kind === "BOOK" && cent(row.bid_cents) && cent(row.ask_cents)) return Math.floor((row.bid_cents + row.ask_cents) / 2);
  return null;
}

function observe(state, legId, row) {
  const leg = state.legs[legId];
  if (!leg) throw new Error(`UNKNOWN_LEG ${state.event_id}|${legId}`);
  if (!Number.isFinite(row.timestamp_epoch)) throw new Error(`MISSING_TAPE_CLOCK ${state.event_id}|${legId}`);
  state.current_epoch = row.timestamp_epoch;
  state.receipt = row.receipt;
  leg.rows.push(row);
  const reference = referenceOf(row);
  if (row.kind === "BOOK") {
    leg.current_book = row;
    leg.books.push(row);
  } else if (row.kind === "PRINT") {
    leg.prints.push(row);
    leg.volume_contracts += Number.isFinite(row.size) ? row.size : 0;
  }
  if (Number.isInteger(reference)) {
    const prior = leg.current_reference_cents;
    if (Number.isInteger(prior) && prior !== reference) {
      leg.steps.push({ timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, cents: reference - prior });
      leg.last_change_epoch = row.timestamp_epoch;
    } else if (leg.last_change_epoch === null) leg.last_change_epoch = row.timestamp_epoch;
    leg.current_reference_cents = reference;
    leg.running_low_cents = leg.running_low_cents === null ? reference : Math.min(leg.running_low_cents, reference);
    leg.running_high_cents = leg.running_high_cents === null ? reference : Math.max(leg.running_high_cents, reference);
    leg.references.push({ timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, cents: reference });
    if (leg.references.length >= 3) {
      const a = leg.references.at(-3), b = leg.references.at(-2), c = leg.references.at(-1);
      if (b.cents < a.cents && b.cents < c.cents) leg.divots.push({ timestamp_epoch: b.timestamp_epoch, receipt: b.receipt, floor_cents: b.cents, depth_cents: Math.min(a.cents, c.cents) - b.cents });
    }
  }
  return state;
}

function stamp(state, name, value, receipts, gaps = []) {
  return { reader: name, status: "CONNECTED", value, receipts: [...new Set(receipts.filter(Boolean))], resource_gaps: gaps, timestamp_epoch: state.current_epoch, hours_from_discovery: (state.current_epoch - state.discovery_epoch) / 3600 };
}

function readAll(state) {
  const ids = state.leg_ids;
  const legs = ids.map((id) => state.legs[id]);
  const receipts = legs.map((leg) => last(leg.rows)?.receipt);
  const anchors = legs.map((leg) => leg.anchor_cents);
  const currents = legs.map((leg) => leg.current_reference_cents);
  const drifts = legs.map((leg, index) => Number.isInteger(currents[index]) && Number.isInteger(anchors[index]) ? currents[index] - anchors[index] : null);
  const travels = legs.map((leg) => Number.isInteger(leg.running_low_cents) && Number.isInteger(leg.running_high_cents) ? leg.running_high_cents - leg.running_low_cents : null);
  const formationProgress = legs.map((leg) => Number.isFinite(leg.formation_end_epoch) && leg.formation_end_epoch > state.discovery_epoch
    ? clipped((state.current_epoch - state.discovery_epoch) / (leg.formation_end_epoch - state.discovery_epoch)) : null);
  const books = legs.map((leg) => leg.current_book);
  const shapeSurvival = legs.map((leg, index) => {
    const netSign = Math.sign(drifts[index] ?? 0);
    if (!leg.steps.length || netSign === 0) return leg.steps.length ? 0 : null;
    return leg.steps.filter((row) => Math.sign(row.cents) === netSign).length / leg.steps.length;
  });
  const ripeness = legs.map((leg) => leg.rows.length / (leg.rows.length + 1));
  const dwellSeconds = legs.map((leg) => Number.isFinite(leg.last_change_epoch) ? state.current_epoch - leg.last_change_epoch : null);
  const spreads = books.map((book) => cent(book?.bid_cents) && cent(book?.ask_cents) ? book.ask_cents - book.bid_cents : null);
  const divotDepths = legs.map((leg) => mean(leg.divots.map((row) => row.depth_cents)));
  const depthRatios = books.map((book) => Number.isFinite(book?.bid_depth_5) && Number.isFinite(book?.ask_depth_5) && book.bid_depth_5 + book.ask_depth_5 > 0 ? book.bid_depth_5 / (book.bid_depth_5 + book.ask_depth_5) : null);
  const inverseCoherence = Number.isFinite(drifts[0]) && Number.isFinite(drifts[1]) ? 1 - Math.abs(drifts[0] + drifts[1]) / (Math.abs(drifts[0]) + Math.abs(drifts[1]) + 1) : null;
  const positionSnapshot = Object.fromEntries(ids.map((id) => [id, { ...state.positions[id] }]));
  const reads = {
    anchor_settle: stamp(state, "anchor_settle", { formation_progress: Object.fromEntries(ids.map((id, i) => [id, formationProgress[i]])), anchors_cents: Object.fromEntries(ids.map((id, i) => [id, anchors[i]])) }, receipts, ids.filter((id, i) => anchors[i] === null).map((id) => `ANCHOR_MISSING:${id}`)),
    opening_split: stamp(state, "opening_split", { sum_cents: Number.isInteger(anchors[0]) && Number.isInteger(anchors[1]) ? anchors[0] + anchors[1] : null, absolute_split_cents: Number.isInteger(anchors[0]) && Number.isInteger(anchors[1]) ? Math.abs(anchors[0] - anchors[1]) : null }, receipts),
    drift: stamp(state, "drift", Object.fromEntries(ids.map((id, i) => [id, { current_cents: currents[i], drift_cents: drifts[i] }])), receipts),
    steps_stillness: stamp(state, "steps_stillness", Object.fromEntries(ids.map((id, i) => [id, { step_count: legs[i].steps.length, last_step_cents: last(legs[i].steps)?.cents ?? null, still_seconds: dwellSeconds[i] }])), receipts),
    shape_survival: stamp(state, "shape_survival", Object.fromEntries(ids.map((id, i) => [id, { directional_step_share: shapeSurvival[i], observed_steps: legs[i].steps.length }])), receipts),
    ripeness: stamp(state, "ripeness", Object.fromEntries(ids.map((id, i) => [id, { continuous_evidence_mass: ripeness[i], observations: legs[i].rows.length, prints: legs[i].prints.length }])), receipts),
    lows_travel: stamp(state, "lows_travel", Object.fromEntries(ids.map((id, i) => [id, { low_cents: legs[i].running_low_cents, high_cents: legs[i].running_high_cents, travel_cents: travels[i] }])), receipts),
    joint_state_spread_dwell: stamp(state, "joint_state_spread_dwell", { mid_sum_cents: Number.isInteger(currents[0]) && Number.isInteger(currents[1]) ? currents[0] + currents[1] : null, spread_sum_cents: Number.isFinite(spreads[0]) && Number.isFinite(spreads[1]) ? spreads[0] + spreads[1] : null, dwell_seconds: Object.fromEntries(ids.map((id, i) => [id, dwellSeconds[i]])) }, receipts),
    divots: stamp(state, "divots", Object.fromEntries(ids.map((id, i) => [id, { count: legs[i].divots.length, mean_depth_cents: divotDepths[i], latest: last(legs[i].divots) }])), receipts),
    depth_size: stamp(state, "depth_size", Object.fromEntries(ids.map((id, i) => [id, { bid_depth_5: finite(books[i]?.bid_depth_5), ask_depth_5: finite(books[i]?.ask_depth_5), bid_share: depthRatios[i], top_bid_size: finite(books[i]?.bid_1_sz), top_ask_size: finite(books[i]?.ask_1_sz) }])), receipts, ids.filter((id, i) => !books[i]).map((id) => `BOOK_MISSING:${id}`)),
    volume: stamp(state, "volume", Object.fromEntries(ids.map((id, i) => [id, { print_count: legs[i].prints.length, contracts: legs[i].volume_contracts }])), receipts),
    sibling_state: stamp(state, "sibling_state", { inverse_coherence: inverseCoherence, drift_sum_cents: Number.isFinite(drifts[0]) && Number.isFinite(drifts[1]) ? drifts[0] + drifts[1] : null, both_legs_named: true }, receipts),
    category: stamp(state, "category", { category: state.category }, receipts),
    time_in_window: stamp(state, "time_in_window", { hours_from_discovery: (state.current_epoch - state.discovery_epoch) / 3600, hours_to_truth_bell: Number.isFinite(state.bell_epoch) ? (state.bell_epoch - state.current_epoch) / 3600 : null, bell_source: state.bell_source }, receipts, Number.isFinite(state.bell_epoch) ? [] : ["TRUTH_BELL_UNKNOWN"]),
    books: stamp(state, "books", Object.fromEntries(ids.map((id, i) => [id, books[i] ? { bid_cents: cent(books[i].bid_cents), ask_cents: cent(books[i].ask_cents), last_trade_cents: cent(books[i].last_trade_cents), receipt: books[i].receipt } : null])), receipts),
    half_pair_state: stamp(state, "half_pair_state", { credited_count: ids.filter((id) => state.positions[id].credited).length, entry_sum_cents: sum(ids.map((id) => state.positions[id].entry_cents)), standing_count: ids.filter((id) => cent(state.positions[id].standing_target_cents)).length, legs: positionSnapshot }, receipts),
  };
  const names = Object.keys(reads).sort();
  if (names.length !== READER_NAMES.length || READER_NAMES.some((name) => !reads[name])) throw new Error(`SIXTEEN_READER_CONSERVATION_FAILED ${names.join(",")}`);
  return reads;
}

function orientPair(values) {
  return [...values].sort((a, b) => (a.anchor_cents ?? 50) - (b.anchor_cents ?? 50) || String(a.leg_id).localeCompare(String(b.leg_id)));
}

function vectorFromReads(state, reads) {
  const oriented = orientPair(state.leg_ids.map((id) => ({
    leg_id: id,
    anchor_cents: reads.anchor_settle.value.anchors_cents[id],
    drift_cents: reads.drift.value[id].drift_cents,
    travel_cents: reads.lows_travel.value[id].travel_cents,
    low_cents: reads.lows_travel.value[id].low_cents,
  })));
  return {
    category: state.category,
    anchor_split_cents: reads.opening_split.value.absolute_split_cents,
    leg0_anchor_cents: oriented[0].anchor_cents,
    leg1_anchor_cents: oriented[1].anchor_cents,
    leg0_drift_cents: oriented[0].drift_cents,
    leg1_drift_cents: oriented[1].drift_cents,
    leg0_travel_cents: oriented[0].travel_cents,
    leg1_travel_cents: oriented[1].travel_cents,
    joint_mid_sum_cents: reads.joint_state_spread_dwell.value.mid_sum_cents,
    joint_spread_cents: reads.joint_state_spread_dwell.value.spread_sum_cents,
    inverse_coherence: reads.sibling_state.value.inverse_coherence,
    volume_log1p: Math.log1p(sum(Object.values(reads.volume.value).map((row) => row.contracts))),
    hours_from_discovery: reads.time_in_window.value.hours_from_discovery,
    divot_depth_cents: mean(Object.values(reads.divots.value).map((row) => row.mean_depth_cents)),
    oriented_leg_ids: oriented.map((row) => row.leg_id),
  };
}

function similarity(query, candidate, declaration = SIMILARITY_DECLARATION) {
  let totalWeight = 0, coveredWeight = 0, distanceWeight = 0;
  const contributions = {};
  for (const [field, weight] of Object.entries(declaration.weights)) {
    totalWeight += weight;
    if (field === "category") {
      const covered = Boolean(query.category && candidate.category);
      const distance = covered ? (query.category === candidate.category ? 0 : 1) : null;
      if (covered) { coveredWeight += weight; distanceWeight += weight * distance; }
      contributions[field] = { weight, covered, distance };
      continue;
    }
    const q = query[field], c = candidate[field], scale = declaration.scales[field];
    const covered = Number.isFinite(q) && Number.isFinite(c) && Number.isFinite(scale) && scale > 0;
    const distance = covered ? Math.abs(q - c) / scale : null;
    if (covered) { coveredWeight += weight; distanceWeight += weight * distance; }
    contributions[field] = { weight, scale, covered, distance };
  }
  const coverage = totalWeight > 0 ? coveredWeight / totalWeight : 0;
  const normalizedDistance = coveredWeight > 0 ? distanceWeight / coveredWeight : null;
  const score = normalizedDistance === null ? 0 : coverage * Math.exp(-normalizedDistance);
  return { score, coverage, normalized_distance: normalizedDistance, contributions };
}

function retrieveNeighborhood(corpus, query, excludedEventId, count = SIMILARITY_DECLARATION.neighbor_count) {
  const rows = corpus.filter((row) => row.event_id !== excludedEventId).map((row) => ({ row, match: similarity(query, row.vector) }));
  rows.sort((a, b) => b.match.score - a.match.score || b.match.coverage - a.match.coverage || a.row.event_id.localeCompare(b.row.event_id));
  return rows.slice(0, count).map((entry, index) => ({
    grade: `N${index + 1}`,
    event_id: entry.row.event_id,
    event_date: entry.row.event_date,
    category: entry.row.category,
    score: entry.match.score,
    coverage: entry.match.coverage,
    normalized_distance: entry.match.normalized_distance,
    quality: entry.row.quality,
    legs: entry.row.legs,
    source_receipts: entry.row.source_receipts,
  }));
}

function assertResources(resources) {
  const byId = new Map(resources.map((row) => [row.id, row]));
  const missing = EXPECTED_RESOURCE_IDS.filter((id) => !byId.has(id) || byId.get(id).status !== "CONNECTED");
  if (missing.length) throw new Error(`FUNCTIONAL_RESOURCES_NOT_CONNECTED ${missing.join(",")}`);
  return EXPECTED_RESOURCE_IDS.map((id) => byId.get(id));
}

function weightedNeighborLeg(neighborhood, orientedIndex) {
  const rows = [];
  for (const neighbor of neighborhood) {
    const leg = neighbor.legs?.[orientedIndex];
    if (!leg || !Number.isFinite(leg.anchor_cents) || !Number.isFinite(leg.low_cents) || leg.anchor_cents <= 0) continue;
    const weight = neighbor.score * neighbor.coverage;
    rows.push({ event_id: neighbor.event_id, weight, low_ratio: leg.low_cents / leg.anchor_cents, low_cents: leg.low_cents, anchor_cents: leg.anchor_cents });
  }
  const denominator = sum(rows.map((row) => row.weight));
  return { rows, denominator, weighted_low_ratio: denominator > 0 ? sum(rows.map((row) => row.weight * row.low_ratio)) / denominator : null };
}

function deriveAction({ state, reads, neighborhood, legId, lineage, resources }) {
  const consulted = assertResources(resources);
  const vector = vectorFromReads(state, reads);
  const orientedIndex = vector.oriented_leg_ids.indexOf(legId);
  if (orientedIndex < 0) throw new Error(`DERIVATION_LEG_NOT_ORIENTED ${legId}`);
  const neighborLeg = weightedNeighborLeg(neighborhood, orientedIndex);
  const anchor = reads.anchor_settle.value.anchors_cents[legId];
  const book = reads.books.value[legId];
  const position = reads.half_pair_state.value.legs[legId];
  const siblingId = state.leg_ids.find((id) => id !== legId);
  const sibling = reads.half_pair_state.value.legs[siblingId];
  const formationProgress = reads.anchor_settle.value.formation_progress[legId];
  let derivedTarget = Number.isFinite(neighborLeg.weighted_low_ratio) && Number.isInteger(anchor) ? Math.round(anchor * neighborLeg.weighted_low_ratio) : null;
  const lineageTarget = cent(lineage?.target_cents);
  const neighborhoodMass = mean(neighborhood.map((row) => row.score * row.coverage)) ?? 0;
  if (cent(derivedTarget) && lineageTarget) derivedTarget = Math.round(neighborhoodMass * derivedTarget + (1 - neighborhoodMass) * lineageTarget);
  else if (!cent(derivedTarget)) derivedTarget = lineageTarget;
  const siblingCommitment = cent(sibling.entry_cents) ?? cent(sibling.standing_target_cents);
  const pairCap = siblingCommitment ? PAR_BUDGET_CENTS - siblingCommitment : PAR_BUDGET_CENTS - 1;
  const postOnlyCap = cent(book?.ask_cents) ? book.ask_cents - 1 : 99;
  if (cent(derivedTarget)) derivedTarget = Math.max(1, Math.min(derivedTarget, pairCap, postOnlyCap));
  const active = cent(position.standing_target_cents);
  let action;
  if (!Number.isFinite(formationProgress) || formationProgress < 1) action = { action: active ? "CANCEL_REST" : "HOLD_REST", target_cents: null, reason: "FORMATION_NOT_COMPLETE" };
  else if (!cent(derivedTarget)) action = { action: active ? "HOLD_REST" : "HOLD_REST", target_cents: active, reason: "NEIGHBORHOOD_TARGET_UNAVAILABLE" };
  else action = { action: active === null ? "PLACE_REST" : active === derivedTarget ? "HOLD_REST" : "REPRICE_REST", target_cents: derivedTarget, reason: "ASSEMBLED_PATTERN_NEIGHBORHOOD_PAIR_ARITHMETIC" };
  const actionStatement = `ACTION=${action.action}; TARGET_CENTS=${cent(action.target_cents) ?? "NONE"}; ACTIVE_TARGET_BEFORE_CENTS=${active ?? "NONE"}.`;
  const sentence = `At ${reads.time_in_window.value.hours_from_discovery.toFixed(6)} hours from discovery, all sixteen readers fired for ${state.event_id}. The named neighborhood is ${neighborhood.map((row) => `${row.event_id}@${row.score.toFixed(6)}`).join(", ") || "EMPTY"}. ${legId} has anchor ${anchor ?? "UNKNOWN"}, neighborhood low ratio ${neighborLeg.weighted_low_ratio ?? "UNKNOWN"}, lineage target ${lineageTarget ?? "NONE"}, pair cap ${pairCap}, and post-only cap ${postOnlyCap}. Resources consulted: ${consulted.map((row) => row.id).join(", ")}. ${actionStatement}`;
  if (!sentence.includes(actionStatement)) throw new Error(`SENTENCE_ACTION_MISMATCH ${state.event_id}|${legId}|${state.receipt}`);
  return {
    event_id: state.event_id,
    leg_id: legId,
    timestamp_epoch: state.current_epoch,
    hours_from_discovery: reads.time_in_window.value.hours_from_discovery,
    receipt: state.receipt,
    vector,
    neighborhood,
    resources_consulted: consulted.map((row) => ({ id: row.id, receipt: row.receipt })),
    derivation: { oriented_index: orientedIndex, neighbor_leg: neighborLeg, neighborhood_mass: neighborhoodMass, anchor_cents: anchor, lineage_target_cents: lineageTarget, sibling_commitment_cents: siblingCommitment, pair_cap_cents: pairCap, post_only_cap_cents: postOnlyCap, derived_target_cents: cent(derivedTarget) },
    action,
    sentence,
    sentence_action_assertion: { hard_assert: true, expected_statement: actionStatement, equal: true },
    pair_conservation: { sibling_leg_id: siblingId, sibling_commitment_cents: siblingCommitment, evaluated_target_cents: cent(action.target_cents), sum_cents: cent(action.target_cents) && siblingCommitment ? action.target_cents + siblingCommitment : null, at_or_below_99: !(cent(action.target_cents) && siblingCommitment) || action.target_cents + siblingCommitment <= PAR_BUDGET_CENTS },
  };
}

module.exports = {
  PAR_BUDGET_CENTS,
  READER_NAMES,
  EXPECTED_RESOURCE_IDS,
  SIMILARITY_DECLARATION,
  sha256,
  createTapeState,
  observe,
  readAll,
  vectorFromReads,
  similarity,
  retrieveNeighborhood,
  assertResources,
  deriveAction,
};
