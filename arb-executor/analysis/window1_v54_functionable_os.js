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
  "FOUNDATION_PER_MINUTE_UNIVERSE",
  "SPIKE_ATLAS",
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
const CONDITIONAL_DIP_DECLARATION = Object.freeze({
  question: "Given this leg's own bounded evidence, its position in its own lawful window, the current live touch, and the pair state, how far below the touch does the continuously graded remaining-dip distribution license a rest?",
  distribution: "weighted q25/q50/q75 of integer-cent remaining dip; each member contributes its remaining dip only while its bell-bounded floor lies ahead of this leg's current window fraction, and contributes zero once that corresponding floor time has passed",
  signing_statistic: "the time-conditioned remaining-dip q50 is the derived depth below the live best bid; credited-sibling conservation can only deepen that distance",
  member_law: "Nearest usable members are never rejected by a binary dip/no-dip gate; similarity, coverage, and continuous evidence-distance jointly grade every member.",
  depth_inputs: ["CONDITIONED_REMAINING_DIP_DISTRIBUTION", "OWN_BELL_BOUNDED_WINDOW_POSITION", "OPEN_OR_HALF_PAIR_STATE"],
  authority_order: ["DERIVED-DEPTH", "DEPTH-UNAVAILABLE-CANCEL"],
  provenance: "OPERATOR_ORDERED_DERIVATION: no placement constant, threshold, or default appears in the depth path; q50 is the distribution's central order statistic, window position is continuous, and pair pressure is exact 99-cent conservation arithmetic",
  blanket_anchor_ratio: "DELETED",
  absolute_floor_target_path: "DELETED",
  lineage_depth_fallback: "DELETED",
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
    running_true_trade_low_cents: null, running_true_trade_high_cents: null,
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
    positions: Object.fromEntries(legIds.map((id) => [id, {
      credited: false,
      entry_cents: null,
      standing_target_cents: null,
      fill_receipt: null,
      fill_event_receipt: null,
      fill_timestamp_epoch: null,
    }])),
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
    if (cent(row.price_cents)) {
      leg.running_true_trade_low_cents = leg.running_true_trade_low_cents === null ? row.price_cents : Math.min(leg.running_true_trade_low_cents, row.price_cents);
      leg.running_true_trade_high_cents = leg.running_true_trade_high_cents === null ? row.price_cents : Math.max(leg.running_true_trade_high_cents, row.price_cents);
    }
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

function creditPosition(state, legId, row) {
  const position = state.positions[legId];
  if (!position) throw new Error(`UNKNOWN_POSITION ${state.event_id}|${legId}`);
  if (position.credited) throw new Error(`POSITION_ALREADY_CREDITED ${state.event_id}|${legId}`);
  if (row.kind !== "PRINT" || !cent(row.price_cents) || !row.receipt || !Number.isFinite(row.timestamp_epoch)) {
    throw new Error(`FILL_EVENT_REQUIRES_PRINT_RECEIPT ${state.event_id}|${legId}`);
  }
  const fillEventReceipt = captureReceipt({
    citationType: "FILL_EVENT",
    sourceId: `${state.event_id}|${legId}`,
    capturedAtReceipt: row.receipt,
    rowRefs: [String(row.receipt)],
    context: {
      event_id: state.event_id,
      leg_id: legId,
      entry_cents: row.price_cents,
      fill_timestamp_epoch: row.timestamp_epoch,
      prior_standing_target_cents: position.standing_target_cents,
      transition: "OPEN_REST_TO_CREDITED_HALF_PAIR",
    },
  });
  position.credited = true;
  position.entry_cents = row.price_cents;
  position.fill_receipt = row.receipt;
  position.fill_event_receipt = fillEventReceipt;
  position.fill_timestamp_epoch = row.timestamp_epoch;
  position.standing_target_cents = null;
  return fillEventReceipt;
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
    lows_travel: stamp(state, "lows_travel", Object.fromEntries(ids.map((id, i) => [id, { low_cents: legs[i].running_low_cents, high_cents: legs[i].running_high_cents, travel_cents: travels[i], true_trade_low_cents: legs[i].running_true_trade_low_cents, true_trade_high_cents: legs[i].running_true_trade_high_cents, true_trade_count: legs[i].prints.length }])), receipts),
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
  const positionByOrientedLeg = oriented.map((row) => reads.half_pair_state.value.legs[row.leg_id]);
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
    half_pair_credited_count: reads.half_pair_state.value.credited_count,
    half_pair_entry_sum_cents: reads.half_pair_state.value.entry_sum_cents,
    leg0_credited_entry_cents: cent(positionByOrientedLeg[0]?.entry_cents),
    leg1_credited_entry_cents: cent(positionByOrientedLeg[1]?.entry_cents),
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

function receiptId(receipt) {
  return `CR-${sha256(JSON.stringify(receipt))}`;
}

function captureReceipt({ citationType, sourceId, capturedAtReceipt, rowRefs, status = "RECEIPT", context = null }) {
  const receipt = {
    schema: "CITATION_RECEIPT_V1",
    kind: status === "RESOURCE-GAP" ? "RESOURCE_GAP" : "QUERY_RECEIPT",
    citation_type: citationType,
    source_id: sourceId,
    captured_at_receipt: capturedAtReceipt,
    row_refs: [...new Set((rowRefs ?? []).filter((value) => typeof value === "string" && value.length > 0))].sort(),
  };
  if (context && typeof context === "object") receipt.context = context;
  receipt.receipt_id = receiptId(receipt);
  return receipt;
}

function assertCaptureReceipt(receipt, capturedAtReceipt, citation) {
  const valid = Boolean(
    receipt
    && typeof receipt === "object"
    && receipt.schema === "CITATION_RECEIPT_V1"
    && ["QUERY_RECEIPT", "RESOURCE_GAP"].includes(receipt.kind)
    && receipt.captured_at_receipt === capturedAtReceipt
    && typeof receipt.receipt_id === "string"
    && receipt.receipt_id === receiptId(Object.fromEntries(Object.entries(receipt).filter(([key]) => key !== "receipt_id")))
    && (receipt.kind === "RESOURCE_GAP" || (Array.isArray(receipt.row_refs) && receipt.row_refs.length > 0))
  );
  if (!valid) throw new Error(`CITATION_RECEIPT_BUILD_VIOLATION ${citation}|${capturedAtReceipt}`);
  return receipt;
}

function retrieveNeighborhood(corpus, query, excludedEventId, count = SIMILARITY_DECLARATION.neighbor_count, capturedAtReceipt = null) {
  if (!capturedAtReceipt) throw new Error(`CITATION_RECEIPT_BUILD_VIOLATION NEIGHBORHOOD_QUERY|MISSING_CAPTURE_CLOCK`);
  const queryFingerprint = sha256(JSON.stringify(query));
  const rows = corpus
    .filter((row) => row.event_id !== excludedEventId)
    .filter((row) => Array.isArray(row.legs) && row.legs.length === 2 && row.legs.every((leg) => [leg.anchor_cents, leg.observed_low_cents, leg.low_cents].every(Number.isFinite)))
    .map((row) => ({ row, match: similarity(query, row.vector) }));
  rows.sort((a, b) => b.match.score - a.match.score || b.match.coverage - a.match.coverage || a.row.event_id.localeCompare(b.row.event_id));
  return rows.slice(0, count).map((entry, index) => {
    const rowRefs = (entry.row.source_receipts ?? []).map((sourceReceipt) => sourceReceipt?.row_ref).filter(Boolean);
    if (!rowRefs.length) throw new Error(`CITATION_RECEIPT_BUILD_VIOLATION NEIGHBOR_ROW_RECEIPT_MISSING:${entry.row.event_id}|${capturedAtReceipt}`);
    const citationReceipt = captureReceipt({
      citationType: "NAMED_NEIGHBOR",
      sourceId: entry.row.event_id,
      capturedAtReceipt,
      rowRefs,
      status: "RECEIPT",
      context: {
        query_fingerprint_sha256: queryFingerprint,
        half_pair_credited_count: query.half_pair_credited_count ?? 0,
        half_pair_entry_sum_cents: query.half_pair_entry_sum_cents ?? 0,
        leg0_credited_entry_cents: query.leg0_credited_entry_cents ?? null,
        leg1_credited_entry_cents: query.leg1_credited_entry_cents ?? null,
      },
    });
    assertCaptureReceipt(citationReceipt, capturedAtReceipt, `NEIGHBOR:${entry.row.event_id}`);
    return {
      grade: `N${index + 1}`,
      event_id: entry.row.event_id,
      event_date: entry.row.event_date,
      category: entry.row.category,
      score: entry.match.score,
      coverage: entry.match.coverage,
      normalized_distance: entry.match.normalized_distance,
      quality: entry.row.quality,
      grain: entry.row.grain ?? null,
      licensed_layers: entry.row.licensed_layers ?? null,
      micro_micro_licensed: entry.row.micro_micro_licensed ?? null,
      legs: entry.row.legs,
      source_receipts: entry.row.source_receipts,
      citation_receipt: citationReceipt,
      citation_receipt_id: citationReceipt.receipt_id,
      query_fingerprint_sha256: queryFingerprint,
    };
  });
}

function assertResources(resources) {
  const byId = new Map(resources.map((row) => [row.id, row]));
  const missing = EXPECTED_RESOURCE_IDS.filter((id) => !byId.has(id) || byId.get(id).status !== "CONNECTED");
  if (missing.length) throw new Error(`FUNCTIONAL_RESOURCES_NOT_CONNECTED ${missing.join(",")}`);
  return EXPECTED_RESOURCE_IDS.map((id) => byId.get(id));
}

function weightedQuantile(rows, quantile) {
  const ordered = rows.filter((row) => Number.isFinite(row.value) && row.weight > 0).sort((a, b) => a.value - b.value || a.event_id.localeCompare(b.event_id));
  const total = sum(ordered.map((row) => row.weight));
  if (!(total > 0)) return null;
  const threshold = total * quantile;
  let accumulated = 0;
  for (const row of ordered) {
    accumulated += row.weight;
    if (accumulated >= threshold) return row.value;
  }
  return ordered.at(-1).value;
}

function conditionalNeighborLeg(neighborhood, orientedIndex, ownEvidence) {
  const ownAnchor = ownEvidence.anchor_cents;
  const ownLow = ownEvidence.true_trade_low_cents ?? ownEvidence.book_path_low_cents;
  const ownBasis = Number.isFinite(ownEvidence.true_trade_low_cents) ? "TRUE_TRADE" : Number.isFinite(ownEvidence.book_path_low_cents) ? "BOOK_PATH" : "NO_OWN_LOW";
  const ownObservedDip = Number.isFinite(ownAnchor) && Number.isFinite(ownLow) ? Math.max(0, ownAnchor - ownLow) : null;
  const ownDipState = Number.isFinite(ownObservedDip) ? (ownObservedDip > 0 ? "DIP_OBSERVED" : "NO_DIP_OBSERVED") : "INSUFFICIENT_OWN_EVIDENCE";
  const rows = [], excluded = [];
  for (const neighbor of neighborhood) {
    const leg = neighbor.legs?.[orientedIndex];
    if (!leg || !Number.isFinite(leg.anchor_cents) || !Number.isFinite(leg.observed_low_cents) || !Number.isFinite(leg.low_cents)) {
      excluded.push({ event_id: neighbor.event_id, reason: "NO_INTERIM_BOUNDED_LOW" });
      continue;
    }
    const observedDip = Math.max(0, leg.anchor_cents - leg.observed_low_cents);
    const evidenceDistance = Math.abs(observedDip - ownObservedDip);
    const evidenceMatchGrade = 1 / (1 + evidenceDistance);
    const weight = neighbor.score * neighbor.coverage * evidenceMatchGrade;
    const remainingDip = Math.max(0, leg.observed_low_cents - leg.low_cents);
    const memberFloorFraction = Number.isFinite(leg.floor_fraction) ? clipped(leg.floor_fraction) : null;
    const ownWindowFraction = Number.isFinite(ownEvidence.window_fraction) ? clipped(ownEvidence.window_fraction) : null;
    const timeConditionedRemainingDip = Number.isFinite(memberFloorFraction) && Number.isFinite(ownWindowFraction)
      ? memberFloorFraction > ownWindowFraction ? remainingDip : 0
      : null;
    rows.push({ event_id: neighbor.event_id, quality: neighbor.quality, similarity_grade: neighbor.score, coverage_grade: neighbor.coverage, evidence_match_grade: evidenceMatchGrade, evidence_distance_cents: evidenceDistance, weight, observed_dip_cents: observedDip, dip_state: observedDip > 0 ? "DIP_OBSERVED" : "NO_DIP_OBSERVED", remaining_dip_cents: remainingDip, member_floor_fraction: memberFloorFraction, own_window_fraction: ownWindowFraction, time_conditioned_remaining_dip_cents: timeConditionedRemainingDip, observed_low_cents: leg.observed_low_cents, low_cents: leg.low_cents, low_basis: leg.low_basis ?? null, source_grain: neighbor.grain ?? leg.source_grain ?? null, licensed_layers: neighbor.licensed_layers ?? leg.licensed_layers ?? null });
  }
  const distributionRows = rows.map((row) => ({ event_id: row.event_id, weight: row.weight, value: row.remaining_dip_cents }));
  const timeConditionedRows = rows.filter((row) => Number.isFinite(row.time_conditioned_remaining_dip_cents)).map((row) => ({ event_id: row.event_id, weight: row.weight, value: row.time_conditioned_remaining_dip_cents }));
  const absoluteFloorRows = rows.map((row) => ({ event_id: row.event_id, weight: row.weight, value: row.low_cents }));
  const denominator = sum(rows.map((row) => row.weight));
  const q25 = weightedQuantile(distributionRows, 0.25), q50 = weightedQuantile(distributionRows, 0.50), q75 = weightedQuantile(distributionRows, 0.75);
  const timedQ25 = weightedQuantile(timeConditionedRows, 0.25), timedQ50 = weightedQuantile(timeConditionedRows, 0.50), timedQ75 = weightedQuantile(timeConditionedRows, 0.75);
  const floorQ25 = weightedQuantile(absoluteFloorRows, 0.25), floorQ50 = weightedQuantile(absoluteFloorRows, 0.50), floorQ75 = weightedQuantile(absoluteFloorRows, 0.75);
  return {
    rows, excluded, denominator,
    own_evidence: { basis: ownBasis, anchor_cents: ownAnchor, observed_low_cents: ownLow, observed_dip_cents: ownObservedDip, dip_state: ownDipState, true_trade_count: ownEvidence.true_trade_count, formation_end_epoch: ownEvidence.formation_end_epoch, window_end_epoch: ownEvidence.window_end_epoch, elapsed_window_seconds: ownEvidence.elapsed_window_seconds, remaining_window_seconds: ownEvidence.remaining_window_seconds, window_fraction: ownEvidence.window_fraction, window_source: ownEvidence.window_source },
    conditional_remaining_dip_distribution_cents: { q25, q50, q75 },
    time_conditioned_remaining_dip_distribution_cents: { q25: timedQ25, q50: timedQ50, q75: timedQ75 },
    time_conditioned_members: timeConditionedRows.length,
    conditional_absolute_floor_distribution_cents: { q25: floorQ25, q50: floorQ50, q75: floorQ75 },
    conditioned_floor_cents: floorQ50,
    derived_floor_cents: floorQ50,
    binary_state_gate_used: false,
    legacy_blanket_low_ratio_used: false,
    subtractive_remaining_dip_used: false,
    absolute_floor_target_used: false,
    lineage_depth_fallback_used: false,
  };
}

function deriveAction({ state, reads, neighborhood, legId, lineage, resources }) {
  assertResources(resources);
  const neighborReceipts = neighborhood.map((row) => assertCaptureReceipt(row.citation_receipt, state.receipt, `NEIGHBOR:${row.event_id}`));
  const readerRowRefs = [...new Set(Object.values(reads).flatMap((read) => read.receipts ?? []).filter(Boolean))];
  const readerReceipt = captureReceipt({ citationType: "SIXTEEN_READERS", sourceId: state.event_id, capturedAtReceipt: state.receipt, rowRefs: readerRowRefs, status: readerRowRefs.length ? "RECEIPT" : "RESOURCE-GAP" });
  assertCaptureReceipt(readerReceipt, state.receipt, `READERS:${state.event_id}`);
  const lineageRows = lineage?.receipt ? [String(lineage.receipt)] : [];
  const lineageReceipt = captureReceipt({ citationType: "LINEAGE", sourceId: `${state.event_id}|${legId}`, capturedAtReceipt: state.receipt, rowRefs: lineageRows, status: lineageRows.length ? "RECEIPT" : "RESOURCE-GAP" });
  assertCaptureReceipt(lineageReceipt, state.receipt, `LINEAGE:${state.event_id}|${legId}`);
  const neighborhoodGapReceipt = neighborhood.length ? null : captureReceipt({ citationType: "NAMED_NEIGHBOR", sourceId: state.event_id, capturedAtReceipt: state.receipt, rowRefs: [], status: "RESOURCE-GAP" });
  if (neighborhoodGapReceipt) assertCaptureReceipt(neighborhoodGapReceipt, state.receipt, `NEIGHBORHOOD_RESOURCE_GAP:${state.event_id}`);
  const citationReceipts = Object.fromEntries([...neighborReceipts, readerReceipt, lineageReceipt, ...(neighborhoodGapReceipt ? [neighborhoodGapReceipt] : [])].map((receipt) => [receipt.receipt_id, receipt]));
  const vector = vectorFromReads(state, reads);
  const orientedIndex = vector.oriented_leg_ids.indexOf(legId);
  if (orientedIndex < 0) throw new Error(`DERIVATION_LEG_NOT_ORIENTED ${legId}`);
  const anchor = reads.anchor_settle.value.anchors_cents[legId];
  const ownLowRead = reads.lows_travel.value[legId];
  const book = reads.books.value[legId];
  const position = reads.half_pair_state.value.legs[legId];
  const siblingId = state.leg_ids.find((id) => id !== legId);
  const sibling = reads.half_pair_state.value.legs[siblingId];
  const fillHandoffReceipt = sibling.credited ? captureReceipt({
    citationType: "FILL_HANDOFF",
    sourceId: `${state.event_id}|${siblingId}->${legId}`,
    capturedAtReceipt: state.receipt,
    rowRefs: [sibling.fill_receipt].filter(Boolean),
    status: sibling.fill_receipt && sibling.fill_event_receipt?.receipt_id ? "RECEIPT" : "RESOURCE-GAP",
    context: {
      credited_sibling_leg_id: siblingId,
      credited_sibling_entry_cents: sibling.entry_cents,
      original_fill_receipt: sibling.fill_receipt,
      original_fill_event_receipt_id: sibling.fill_event_receipt?.receipt_id ?? null,
      reposed_query_fingerprint_sha256: neighborhood[0]?.query_fingerprint_sha256 ?? sha256(JSON.stringify(vector)),
      transition: "HALF_PAIR_CREDIT_REPOSES_LIBRARY_AND_REDERIVES_OPEN_SIDE",
    },
  }) : null;
  if (fillHandoffReceipt) assertCaptureReceipt(fillHandoffReceipt, state.receipt, `FILL_HANDOFF:${state.event_id}|${legId}`);
  if (fillHandoffReceipt) citationReceipts[fillHandoffReceipt.receipt_id] = fillHandoffReceipt;
  const formationProgress = reads.anchor_settle.value.formation_progress[legId];
  const lineageTarget = cent(lineage?.target_cents);
  const neighborhoodMass = mean(neighborhood.map((row) => row.score * row.coverage)) ?? 0;
  const liveBid = cent(book?.bid_cents), liveAsk = cent(book?.ask_cents);
  const postOnlyCap = liveAsk ? liveAsk - 1 : 99;
  const formationEnd = finite(state.legs[legId].formation_end_epoch);
  const windowEnd = finite(state.bell_epoch);
  const windowDuration = Number.isFinite(formationEnd) && Number.isFinite(windowEnd) && windowEnd > formationEnd ? windowEnd - formationEnd : null;
  const elapsedWindowSeconds = Number.isFinite(windowDuration) ? Math.max(0, Math.min(windowDuration, state.current_epoch - formationEnd)) : null;
  const remainingWindowSeconds = Number.isFinite(windowDuration) ? Math.max(0, windowEnd - state.current_epoch) : null;
  const windowFraction = Number.isFinite(windowDuration) ? clipped(elapsedWindowSeconds / windowDuration) : null;
  const windowSource = Number.isFinite(windowDuration) ? `L11_VERIFIED_REPLAY_WINDOW:${state.bell_source ?? "UNKNOWN"}` : "WINDOW_RESOURCE_GAP";
  const timedNeighborLeg = conditionalNeighborLeg(neighborhood, orientedIndex, {
    anchor_cents: anchor,
    true_trade_low_cents: ownLowRead.true_trade_low_cents,
    book_path_low_cents: ownLowRead.low_cents,
    true_trade_count: ownLowRead.true_trade_count,
    formation_end_epoch: formationEnd,
    window_end_epoch: windowEnd,
    elapsed_window_seconds: elapsedWindowSeconds,
    remaining_window_seconds: remainingWindowSeconds,
    window_fraction: windowFraction,
    window_source: windowSource,
  });
  const depthDistribution = timedNeighborLeg.time_conditioned_remaining_dip_distribution_cents;
  const distributionDepth = Number.isFinite(depthDistribution.q50) ? Math.round(depthDistribution.q50) : null;
  const siblingCommitment = sibling.credited ? cent(sibling.entry_cents) : null;
  const pairCap = siblingCommitment ? PAR_BUDGET_CENTS - siblingCommitment : PAR_BUDGET_CENTS - 1;
  const pairRequiredDepth = liveBid && siblingCommitment ? Math.max(0, liveBid - pairCap) : 0;
  const chosenDepth = Number.isFinite(distributionDepth) && liveBid ? Math.max(distributionDepth, pairRequiredDepth) : null;
  const proposedTarget = liveBid && Number.isFinite(chosenDepth) ? Math.max(1, liveBid - chosenDepth) : null;
  const targetBasis = cent(proposedTarget) ? "DERIVED-DEPTH" : "DEPTH-UNAVAILABLE-CANCEL";
  const targetAuthority = targetBasis;
  const lawfulUnallocatedTarget = cent(proposedTarget) ? Math.max(1, Math.min(proposedTarget, postOnlyCap)) : null;
  const boundedTradeLow = cent(ownLowRead.true_trade_low_cents);
  const belowBoundedTradeLow = Boolean(boundedTradeLow && cent(lawfulUnallocatedTarget) && lawfulUnallocatedTarget < boundedTradeLow);
  const derivedJointEvidenceLicensesDepth = Boolean(belowBoundedTradeLow && liveBid && liveAsk && Number.isFinite(depthDistribution.q50) && timedNeighborLeg.time_conditioned_members > 0 && Number.isFinite(windowFraction));
  const jointDepthLicense = !belowBoundedTradeLow
    ? { required: false, lawful: true, basis: "NOT_BELOW_OWN_BOUNDED_TRADED_LOW", receipts: [] }
    : derivedJointEvidenceLicensesDepth
      ? { required: true, lawful: true, basis: "CONDITIONED_DIP_PLUS_OWN_WINDOW_PLUS_PAIR_STATE", receipts: [book.receipt, ...neighborReceipts.map((row) => row.receipt_id)] }
      : { required: true, lawful: false, basis: "DEPTH_DERIVATION_INCOMPLETE_BELOW_OWN_BOUNDED_TRADED_LOW", receipts: [] };
  const evidenceLawfulTarget = jointDepthLicense.lawful ? lawfulUnallocatedTarget : null;
  const derivedTarget = cent(evidenceLawfulTarget) ? Math.max(1, Math.min(evidenceLawfulTarget, pairCap)) : null;
  const touchRelation = liveBid && liveAsk && cent(evidenceLawfulTarget)
    ? evidenceLawfulTarget === liveBid ? "AT_BEST_BID" : evidenceLawfulTarget > liveBid ? `INSIDE_SPREAD_${evidenceLawfulTarget - liveBid}C_ABOVE_BID` : `BELOW_BEST_BID_${liveBid - evidenceLawfulTarget}C`
    : "NO_FORMED_TWO_SIDED_BOOK";
  const evidenceMass = reads.ripeness.value[legId].continuous_evidence_mass ?? 0;
  const touchDistance = liveBid && cent(evidenceLawfulTarget) ? Math.abs(evidenceLawfulTarget - liveBid) : 99;
  const allocationPriorityGrade = (timedNeighborLeg.denominator + evidenceMass) / (1 + touchDistance);
  const active = cent(position.standing_target_cents);
  let action;
  if (!Number.isFinite(formationProgress) || formationProgress < 1) action = { action: active ? "CANCEL_REST" : "HOLD_REST", target_cents: null, reason: "FORMATION_NOT_COMPLETE" };
  else if (!cent(derivedTarget)) action = { action: active ? "CANCEL_REST" : "HOLD_REST", target_cents: null, reason: "DEPTH_DERIVATION_UNAVAILABLE_NO_DEFAULT" };
  else action = { action: active === null ? "PLACE_REST" : active === derivedTarget ? "HOLD_REST" : "REPRICE_REST", target_cents: derivedTarget, reason: "DERIVED_DEPTH_CONDITIONED_DIP_WINDOW_PAIR_STATE" };
  const actionStatement = `ACTION=${action.action}; TARGET_CENTS=${cent(action.target_cents) ?? "NONE"}; ACTIVE_TARGET_BEFORE_CENTS=${active ?? "NONE"}.`;
  const namedNeighborhood = neighborhood.length
    ? neighborhood.map((row) => `${row.event_id}@${row.score.toFixed(6)}[${row.citation_receipt_id}]`).join(", ")
    : `RESOURCE-GAP[${neighborhoodGapReceipt.receipt_id}]`;
  const lineageStatement = lineageTarget === null ? `RESOURCE-GAP[${lineageReceipt.receipt_id}]` : `${lineageTarget}[${lineageReceipt.receipt_id}]`;
  const fillHandoffStatement = fillHandoffReceipt
    ? ` The sibling ${siblingId} is credited at ${sibling.entry_cents} from trade receipt ${sibling.fill_receipt ?? "RESOURCE-GAP"}; that half-pair transition re-posed query ${fillHandoffReceipt.context.reposed_query_fingerprint_sha256} and re-derived this open side [${fillHandoffReceipt.receipt_id}].`
    : "";
  const conditional = timedNeighborLeg.conditional_remaining_dip_distribution_cents;
  const conditionalStatement = `${legId} has anchor ${anchor ?? "UNKNOWN"}; its own ${timedNeighborLeg.own_evidence.basis} bounded evidence low is ${timedNeighborLeg.own_evidence.observed_low_cents ?? "UNKNOWN"}, so its observed state is ${timedNeighborLeg.own_evidence.dip_state} with ${timedNeighborLeg.own_evidence.observed_dip_cents ?? "UNKNOWN"} cents already dipped. The continuously graded, bell-bounded MINUTE-grain MACRO/MICRO neighbors imply raw remaining-dip q25/q50/q75 ${conditional.q25 ?? "UNKNOWN"}/${conditional.q50 ?? "UNKNOWN"}/${conditional.q75 ?? "UNKNOWN"} cents and time-conditioned remaining-dip q25/q50/q75 ${depthDistribution.q25 ?? "UNKNOWN"}/${depthDistribution.q50 ?? "UNKNOWN"}/${depthDistribution.q75 ?? "UNKNOWN"} cents from ${timedNeighborLeg.time_conditioned_members} members. TARGET_BASIS=${targetBasis}; LIVE_TOUCH_BID=${liveBid ?? "UNKNOWN"}; CHOSEN_DEPTH_CENTS=${chosenDepth ?? "UNKNOWN"}; PRE_ALLOCATION_DEPTH_TARGET_CENTS=${evidenceLawfulTarget ?? "UNKNOWN"}; no absolute-floor target, blanket ratio, binary same-state gate, stale-prior path, lineage depth fallback, placement constant, threshold, or default is consumed.`;
  const windowStatement = ` OWN_WINDOW=formation ${formationEnd ?? "UNKNOWN"} to ${windowEnd ?? "UNKNOWN"} [${windowSource}], elapsed ${elapsedWindowSeconds ?? "UNKNOWN"}s, remaining ${remainingWindowSeconds ?? "UNKNOWN"}s, continuous fraction ${Number.isFinite(windowFraction) ? windowFraction.toFixed(9) : "UNKNOWN"}; each neighbor's bell-bounded floor time decides whether its observed remaining dip still lies ahead at this receipt.`;
  const pairStateStatement = ` PAIR_STATE=${siblingCommitment ? "HALF_PAIR" : "OPEN"}; CREDITED_SIBLING=${siblingCommitment ? `${siblingId}@${siblingCommitment}` : "NONE"}; PAIR_REQUIRED_DEPTH_CENTS=${pairRequiredDepth}; PAIR_CAP_CENTS=${pairCap}.`;
  const presenceStatement = ` TOUCH_RELATION=${touchRelation}; LIVE_BID_ASK=${liveBid ?? "UNKNOWN"}/${liveAsk ?? "UNKNOWN"}; JOINT_DEPTH_LICENSE=${jointDepthLicense.basis}; DEPTH_LICENSE_RECEIPTS=${jointDepthLicense.receipts.join(",") || "NONE"}.`;
  const sentence = `At ${reads.time_in_window.value.hours_from_discovery.toFixed(6)} hours from discovery, all sixteen readers fired for ${state.event_id} [${readerReceipt.receipt_id}]. The named neighborhood is ${namedNeighborhood}. ${conditionalStatement}${windowStatement}${pairStateStatement}${presenceStatement} Lineage target ${lineageStatement} is context only and never a depth fallback; post-only cap is ${postOnlyCap}.${fillHandoffStatement} ALLOCATION=INCUMBENT-PENDING-JOINT-DERIVATION. ${actionStatement}`;
  if (!sentence.includes(actionStatement)) throw new Error(`SENTENCE_ACTION_MISMATCH ${state.event_id}|${legId}|${state.receipt}`);
  for (const row of neighborhood) if (!sentence.includes(`[${row.citation_receipt_id}]`)) throw new Error(`CITATION_RECEIPT_BUILD_VIOLATION NEIGHBOR_NOT_WELDED:${row.event_id}|${state.receipt}`);
  if (!sentence.includes(`[${readerReceipt.receipt_id}]`) || !sentence.includes(`[${lineageReceipt.receipt_id}]`)) throw new Error(`CITATION_RECEIPT_BUILD_VIOLATION SENTENCE_RECEIPT_NOT_WELDED|${state.receipt}`);
  if (fillHandoffReceipt && (!sentence.includes(`[${fillHandoffReceipt.receipt_id}]`) || !sentence.includes(String(sibling.fill_receipt)))) throw new Error(`FILL_HANDOFF_NOT_WELDED ${state.event_id}|${legId}|${state.receipt}`);
  return {
    event_id: state.event_id,
    leg_id: legId,
    timestamp_epoch: state.current_epoch,
    hours_from_discovery: reads.time_in_window.value.hours_from_discovery,
    receipt: state.receipt,
    vector,
    neighborhood,
    resources_consulted: [...new Set(neighborhood.filter((row) => row.quality === "FOUNDATION_MINUTE_BELL_BOUNDED").flatMap((row) => ["FOUNDATION_PER_MINUTE_UNIVERSE", ...(row.legs?.some((leg) => leg.spike_atlas) ? ["SPIKE_ATLAS"] : [])]))],
    citation_receipts: citationReceipts,
    derivation: { oriented_index: orientedIndex, neighbor_leg: timedNeighborLeg, neighborhood_mass: neighborhoodMass, anchor_cents: anchor, target_authority: targetAuthority, target_basis: targetBasis, depth_distribution_cents: depthDistribution, distribution_depth_cents: distributionDepth, chosen_depth_cents: chosenDepth, pair_required_depth_cents: pairRequiredDepth, window_timing: { source: windowSource, formation_end_epoch: formationEnd, window_end_epoch: windowEnd, elapsed_seconds: elapsedWindowSeconds, remaining_seconds: remainingWindowSeconds, fraction: windowFraction }, proposed_target_cents: cent(proposedTarget), lawful_unallocated_target_cents: cent(evidenceLawfulTarget), lineage_target_cents: lineageTarget, lineage_depth_fallback_used: false, sibling_commitment_cents: siblingCommitment, pair_state: siblingCommitment ? "HALF_PAIR" : "OPEN", pair_cap_cents: pairCap, post_only_cap_cents: postOnlyCap, derived_target_cents: cent(derivedTarget), touch_relation: touchRelation, live_bid_cents: liveBid, live_ask_cents: liveAsk, joint_depth_license: jointDepthLicense, allocation_priority_grade: allocationPriorityGrade, stale_prior_path_used: false, fill_handoff_receipt_id: fillHandoffReceipt?.receipt_id ?? null, reposed_query_fingerprint_sha256: fillHandoffReceipt?.context?.reposed_query_fingerprint_sha256 ?? null },
    action,
    sentence,
    sentence_action_assertion: { hard_assert: true, expected_statement: actionStatement, equal: true },
    citation_receipt_assertion: { hard_assert: true, receipt_count: Object.keys(citationReceipts).length, equal: true },
    pair_conservation: { sibling_leg_id: siblingId, sibling_commitment_cents: siblingCommitment, evaluated_target_cents: cent(action.target_cents), sum_cents: cent(action.target_cents) && siblingCommitment ? action.target_cents + siblingCommitment : null, at_or_below_99: !(cent(action.target_cents) && siblingCommitment) || action.target_cents + siblingCommitment <= PAR_BUDGET_CENTS },
  };
}

function rewriteAllocatedAction(row, action, allocation, reads) {
  const priorStatement = row.sentence_action_assertion.expected_statement;
  const active = cent(reads.half_pair_state.value.legs[row.leg_id].standing_target_cents);
  const actionStatement = `ACTION=${action.action}; TARGET_CENTS=${cent(action.target_cents) ?? "NONE"}; ACTIVE_TARGET_BEFORE_CENTS=${active ?? "NONE"}.`;
  const liveBid = cent(row.derivation.live_bid_cents);
  const finalDepth = liveBid && cent(action.target_cents) ? liveBid - action.target_cents : null;
  const allocationStatement = `ALLOCATION=${allocation.mode}; PRIORITY_GRADES=${allocation.priority_grades ?? "NONE"}; FROM_CENTS=${allocation.from_cents ?? "NONE"}; TO_CENTS=${allocation.to_cents ?? "NONE"}; EXCESS_CENTS=${allocation.excess_cents ?? 0}; FINAL_DEPTH_BELOW_TOUCH_CENTS=${finalDepth ?? "UNKNOWN"}; REASON=${allocation.reason}.`;
  row.sentence = row.sentence.replace("ALLOCATION=INCUMBENT-PENDING-JOINT-DERIVATION.", allocationStatement).replace(priorStatement, actionStatement);
  row.action = action;
  row.derivation.derived_target_cents = cent(action.target_cents);
  row.derivation.final_depth_below_touch_cents = finalDepth;
  row.derivation.allocation = allocation;
  row.sentence_action_assertion = { hard_assert: true, expected_statement: actionStatement, equal: row.sentence.includes(actionStatement) };
  return row;
}

function allocatePairActions({ state, reads, derivations }) {
  const rows = new Map(derivations.map((row) => [row.leg_id, row]));
  const openRows = derivations.filter((row) => !reads.half_pair_state.value.legs[row.leg_id].credited);
  const creditedRows = state.leg_ids.filter((id) => reads.half_pair_state.value.legs[id].credited);
  const allocated = new Map();

  if (creditedRows.length === 0 && openRows.length === 2 && openRows.every((row) => cent(row.derivation.lawful_unallocated_target_cents))) {
    const [left, right] = openRows;
    const leftFrom = left.derivation.lawful_unallocated_target_cents;
    const rightFrom = right.derivation.lawful_unallocated_target_cents;
    const excess = Math.max(0, leftFrom + rightFrom - PAR_BUDGET_CENTS);
    const leftGrade = Number.isFinite(left.derivation.allocation_priority_grade) ? left.derivation.allocation_priority_grade : 0;
    const rightGrade = Number.isFinite(right.derivation.allocation_priority_grade) ? right.derivation.allocation_priority_grade : 0;
    const gradeMass = leftGrade + rightGrade;
    const leftReduction = excess === 0 ? 0 : gradeMass > 0 ? Math.round(excess * rightGrade / gradeMass) : Math.floor(excess / 2);
    const rightReduction = excess - leftReduction;
    let leftTo = Math.max(1, leftFrom - leftReduction);
    let rightTo = Math.max(1, rightFrom - rightReduction);
    if (leftTo + rightTo > PAR_BUDGET_CENTS) {
      const residual = leftTo + rightTo - PAR_BUDGET_CENTS;
      if (leftGrade >= rightGrade) rightTo = Math.max(1, rightTo - residual);
      else leftTo = Math.max(1, leftTo - residual);
    }
    const changed = leftFrom !== leftTo || rightFrom !== rightTo;
    const common = {
      mode: changed ? "GRADED-CONTINUOUS-SPLIT" : "COMPOSED-PICTURE-NO-REALLOCATION",
      priority_grades: `${left.leg_id}:${leftGrade.toFixed(9)},${right.leg_id}:${rightGrade.toFixed(9)}`,
      from_cents: `${left.leg_id}:${leftFrom},${right.leg_id}:${rightFrom}`,
      to_cents: `${left.leg_id}:${leftTo},${right.leg_id}:${rightTo}`,
      excess_cents: excess,
      stale_prior_consumed: false,
      reason: changed
        ? `fresh per-receipt composition exceeded 99; each revisable standing plan yielded continuously in inverse proportion to its current evidence grade before market interaction`
        : "fresh per-receipt composed targets already fit the 99-cent conservation budget",
    };
    allocated.set(left.leg_id, { target: leftTo, allocation: common });
    allocated.set(right.leg_id, { target: rightTo, allocation: common });
  } else {
    for (const row of openRows) {
      allocated.set(row.leg_id, {
        target: cent(row.action.target_cents),
        allocation: {
          mode: "CURRENT-BEHAVIOR-BYTE-EQUAL",
          priority_grades: null,
          from_cents: null,
          to_cents: null,
          excess_cents: 0,
          stale_prior_consumed: false,
          reason: creditedRows.length ? "a credited fill is a commitment, so frozen pair-cap arithmetic applies" : "one or both fresh per-receipt composed targets are unavailable",
        },
      });
    }
  }

  for (const row of openRows) {
    const entry = allocated.get(row.leg_id);
    const target = cent(entry.target);
    const active = cent(reads.half_pair_state.value.legs[row.leg_id].standing_target_cents);
    let action;
    if (!target) action = { action: active ? "CANCEL_REST" : "HOLD_REST", target_cents: null, reason: "JOINT_DERIVATION_HAS_NO_LAWFUL_DERIVED_DEPTH" };
    else action = { action: active === null ? "PLACE_REST" : active === target ? "HOLD_REST" : "REPRICE_REST", target_cents: target, reason: entry.allocation.mode === "GRADED-CONTINUOUS-SPLIT" ? "DERIVED_GRADED_CONTINUOUS_SPLIT" : row.action.reason };
    rewriteAllocatedAction(row, action, entry.allocation, reads);
  }

  for (const row of derivations) {
    const siblingId = state.leg_ids.find((id) => id !== row.leg_id);
    const siblingRow = rows.get(siblingId);
    const siblingPosition = reads.half_pair_state.value.legs[siblingId];
    const siblingPlan = siblingPosition.credited ? cent(siblingPosition.entry_cents) : cent(siblingRow?.action?.target_cents);
    const target = cent(row.action.target_cents);
    row.pair_conservation = {
      sibling_leg_id: siblingId,
      sibling_commitment_cents: siblingPlan,
      evaluated_target_cents: target,
      sum_cents: target && siblingPlan ? target + siblingPlan : null,
      at_or_below_99: !(target && siblingPlan) || target + siblingPlan <= PAR_BUDGET_CENTS,
    };
  }
  return derivations;
}

module.exports = {
  PAR_BUDGET_CENTS,
  READER_NAMES,
  EXPECTED_RESOURCE_IDS,
  SIMILARITY_DECLARATION,
  CONDITIONAL_DIP_DECLARATION,
  sha256,
  createTapeState,
  observe,
  creditPosition,
  readAll,
  vectorFromReads,
  similarity,
  retrieveNeighborhood,
  assertResources,
  conditionalNeighborLeg,
  captureReceipt,
  assertCaptureReceipt,
  deriveAction,
  allocatePairActions,
};
