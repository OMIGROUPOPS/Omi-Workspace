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

const SIMILARITY_DECLARATION = Object.freeze({ name: "POOL_CASCADE", neighbor_count: 0, formula: "FIRST-TICK-ONLY then BASE; STEP-FORECAST telemetry; likelihood and gates bound by bench receipt" });
const CONDITIONAL_DIP_DECLARATION = Object.freeze({ authority_order: ["POOL_CASCADE:FIRST-TICK-ONLY", "POOL_CASCADE:BASE", "INSUFFICIENT_EVIDENCE"] });
function configureNeighborSpecialistBinding(binding) { if (!binding) throw new Error("MISSING_LEGACY_DIAGNOSTIC_BINDING"); }
function configureTrueBellCellDepthMap(binding) { if (!binding) throw new Error("MISSING_LEGACY_DIAGNOSTIC_BINDING"); }

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
    running_book_path_low_cents: null, running_book_last_reference_low_cents: null,
    running_book_mid_low_cents: null, running_book_path_low_source: null,
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
      standing_license_basis: null,
      standing_license_receipt: null,
      standing_captured_rest_level_cents: null,
      standing_captured_rest_license_receipt: null,
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

function referenceBasisOf(row) {
  if (row.kind === "PRINT" && cent(row.price_cents)) return "TRUE_TRADE_PRINT";
  if (row.kind === "BOOK" && cent(row.last_trade_cents)) return "BOOK_REPORTED_LAST_REFERENCE_NON_TRADE";
  if (row.kind === "BOOK" && cent(row.bid_cents) && cent(row.ask_cents)) return "BOOK_BID_ASK_MID_SERIES_FLOORED_NON_TRADE";
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
  const referenceBasis = referenceBasisOf(row);
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
    leg.references.push({ timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, cents: reference, source: referenceBasis });
    if (row.kind === "BOOK") {
      if (leg.running_book_path_low_cents === null || reference < leg.running_book_path_low_cents) {
        leg.running_book_path_low_cents = reference;
        leg.running_book_path_low_source = { source: referenceBasis, receipt: row.receipt, timestamp_epoch: row.timestamp_epoch };
      }
      if (referenceBasis === "BOOK_REPORTED_LAST_REFERENCE_NON_TRADE") {
        leg.running_book_last_reference_low_cents = leg.running_book_last_reference_low_cents === null ? reference : Math.min(leg.running_book_last_reference_low_cents, reference);
      } else if (referenceBasis === "BOOK_BID_ASK_MID_SERIES_FLOORED_NON_TRADE") {
        leg.running_book_mid_low_cents = leg.running_book_mid_low_cents === null ? reference : Math.min(leg.running_book_mid_low_cents, reference);
      }
    }
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
  const restPrice = cent(position.standing_target_cents);
  if (!restPrice) throw new Error(`FILL_EVENT_REQUIRES_STANDING_REST ${state.event_id}|${legId}`);
  if (row.price_cents > restPrice) throw new Error(`PRINT_DID_NOT_KISS_STANDING_REST ${state.event_id}|${legId}`);
  const fillEventReceipt = captureReceipt({
    citationType: "FILL_EVENT",
    sourceId: `${state.event_id}|${legId}`,
    capturedAtReceipt: row.receipt,
    rowRefs: [String(row.receipt)],
    context: {
      event_id: state.event_id,
      leg_id: legId,
      entry_cents: restPrice,
      execution_price_basis: "STANDING_REST_LIMIT_CENTS",
      triggering_print_price_cents: row.price_cents,
      fill_timestamp_epoch: row.timestamp_epoch,
      prior_standing_target_cents: restPrice,
      standing_license_basis: position.standing_license_basis,
      standing_license_receipt: position.standing_license_receipt,
      print_at_or_below_rest: row.price_cents <= restPrice,
      transition: "OPEN_REST_TO_CREDITED_HALF_PAIR",
    },
  });
  position.credited = true;
  position.entry_cents = restPrice;
  position.fill_receipt = row.receipt;
  position.fill_event_receipt = fillEventReceipt;
  position.fill_timestamp_epoch = row.timestamp_epoch;
  position.standing_target_cents = null;
  position.standing_license_basis = null;
  position.standing_license_receipt = null;
  position.standing_captured_rest_level_cents = null;
  position.standing_captured_rest_license_receipt = null;
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
    lows_travel: stamp(state, "lows_travel", Object.fromEntries(ids.map((id, i) => [id, {
      reference_path_low_cents: legs[i].running_low_cents,
      book_path_low_cents: legs[i].running_book_path_low_cents,
      book_path_low_source: legs[i].running_book_path_low_source,
      book_reported_last_reference_low_cents: legs[i].running_book_last_reference_low_cents,
      book_mid_low_cents: legs[i].running_book_mid_low_cents,
      high_cents: legs[i].running_high_cents,
      travel_cents: travels[i],
      observed_traded_low_cents: legs[i].running_true_trade_low_cents,
      observed_traded_high_cents: legs[i].running_true_trade_high_cents,
      true_trade_low_cents: legs[i].running_true_trade_low_cents,
      true_trade_high_cents: legs[i].running_true_trade_high_cents,
      true_trade_count: legs[i].prints.length,
    }])), receipts),
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
    low_cents: reads.lows_travel.value[id].reference_path_low_cents,
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

function assertResources(resources) {
  const byId = new Map(resources.map((row) => [row.id, row]));
  const missing = EXPECTED_RESOURCE_IDS.filter((id) => !byId.has(id) || byId.get(id).status !== "CONNECTED");
  if (missing.length) throw new Error(`FUNCTIONAL_RESOURCES_NOT_CONNECTED ${missing.join(",")}`);
  return EXPECTED_RESOURCE_IDS.map((id) => byId.get(id));
}
// Pool mathematics are the causal bench contract, loaded with the library.
// Price coordinates and contract volume never share a distance sum.
let tickLibrary = null;
const PRICE_FIELDS = Object.freeze(["last", "bid", "ask"]);

function upperBound(values, value) {
  let low = 0, high = values.length;
  while (low < high) {
    const middle = low + Math.floor((high - low) / 2);
    if (values[middle] <= value) low = middle + 1; else high = middle;
  }
  return low;
}
function poolQuantile(values, weights, fraction) {
  const rows = values.map((value, index) => ({ value, weight: weights[index] }))
    .filter(row => Number.isFinite(row.value) && row.weight > 0)
    .sort((a, b) => a.value - b.value);
  const total = sum(rows.map(row => row.weight));
  if (!(total > 0)) return null;
  let running = 0;
  for (const row of rows) {
    running += row.weight;
    if (running >= total * fraction) return row.value;
  }
  return rows.at(-1).value;
}
function poolEss(weights) {
  const total = sum(weights), squares = sum(weights.map(weight => weight * weight));
  return squares > 0 ? total * total / squares : 0;
}
function poolSample(leg, epoch) {
  const index = upperBound(leg.epoch, epoch) - 1;
  return index < 0 ? { last: null, bid: null, ask: null, volume: null } : {
    last: leg.last[index], bid: leg.bid[index], ask: leg.ask[index], volume: leg.volume[index],
  };
}
function poolPair(legs, identity, contract) {
  if (legs.length !== 2 || legs.some(leg => !Number.isFinite(leg.first_epoch)) || legs[0].bell !== legs[1].bell) return null;
  const firstEpoch = Math.max(...legs.map(leg => leg.first_epoch));
  const prices = legs.map(leg => poolSample(leg, firstEpoch).last);
  if (!prices.every(Number.isFinite) || prices[0] === prices[1]) return null;
  legs.sort((a, b) => poolSample(b, firstEpoch).last - poolSample(a, firstEpoch).last);
  const pair = { ...identity, legs, first_epoch: firstEpoch, bell: legs[0].bell,
    formation: Math.max(...legs.map(leg => leg.formation)),
    first_mtb: (legs[0].bell - firstEpoch) / contract.minute_seconds,
    first_volume: sum(legs.map(leg => poolSample(leg, firstEpoch).volume)) };
  pair.first = poolLevels(pair, pair.first_mtb, contract);
  return pair;
}
function poolLevels(pair, mtb, contract) {
  const epoch = pair.bell - mtb * contract.minute_seconds;
  const sides = pair.legs.map(leg => poolSample(leg, epoch));
  return { sides, prices: [...sides.flatMap(side => PRICE_FIELDS.map(key => side[key])),
    sides.every(side => Number.isFinite(side.last)) ? sum(sides.map(side => side.last)) : null],
    volume: sides.every(side => Number.isFinite(side.volume)) ? sum(sides.map(side => side.volume)) - pair.first_volume : null };
}
function poolRole(value, open, contract) {
  if (!Number.isFinite(value) || !Number.isFinite(open)) return "NOT_CALLABLE";
  const drift = value - open;
  return drift >= contract.role_drift_cents ? "CLIMBER" : drift <= -contract.role_drift_cents ? "FALLER" : "NOT_CALLABLE";
}
function poolFamily(leg, threshold, contract) {
  const count = contract.taxonomy_samples, samples = [];
  for (let index = 0; index < count; index += 1) {
    const epoch = leg.formation + (leg.bell - leg.formation) * index / (count - 1);
    const value = epoch >= leg.first_epoch ? poolSample(leg, epoch).last : null;
    samples.push(index && Number.isFinite(value) ? value : leg.open);
  }
  if (!samples.every(Number.isFinite) || !Number.isFinite(threshold)) return null;
  if (leg.print_total < threshold) return "SLEEPER";
  const rules = contract.taxonomy_rules;
  const steps = samples.slice(1).map((value, index) => value - samples[index]);
  const moving = steps.filter(value => value !== 0).map(Math.sign);
  const net = samples.at(-1) - samples[0], magnitude = Math.abs(net);
  const travel = sum(steps.map(Math.abs));
  if (magnitude < rules.quiet_net_cents) return travel >= rules.round_trip_travel_cents ? "ROUND_TRIP" : "QUIET_WOBBLE";
  const quarter = (count - 1) * rules.quarter_fraction;
  const direction = net > 0 ? "UP" : "DOWN";
  if ((samples.at(-1) - samples[count - 1 - quarter]) / net >= rules.quarter_net_share) return `LATE_BREAK_${direction}`;
  if ((samples[quarter] - samples[0]) / net >= rules.quarter_net_share && Math.abs(samples.at(-1) - samples[quarter]) <= contract.flat_after_cents) return `EARLY_SET_${direction}`;
  if (Math.max(...steps.map(Math.abs)) >= rules.one_step_share * magnitude) return `ONE_STEP_${direction}`;
  const reversals = moving.slice(1).filter((value, index) => value !== moving[index]).length;
  if (reversals >= rules.grind_reversals && travel >= rules.grind_travel_multiple * magnitude) return `GRIND_WOBBLE_${direction}`;
  return `DRIFT_${direction}`;
}
function compactTickLeg(row, counts) {
  if (!counts?.seconds.length || counts.counts.at(-1) !== row.true_print_count_in_span) throw new Error(`POOL_SIDECAR_FINAL_COUNT_MISMATCH ${row.ticker}`);
  const leg = { id: row.leg_id, ticker: row.ticker, formation: row.formation_end_epoch, bell: row.bell_epoch,
    open: row.postformation_open_cents ?? row.anchor_cents, print_total: row.true_print_count_in_span,
    count_seconds: Float64Array.from(counts.seconds), count_cum: Float64Array.from(counts.counts) };
  for (const [key, source] of Object.entries({ epoch: "ts", last: "last_cents", bid: "bid_cents", ask: "ask_cents", volume: "volume_cum" })) {
    leg[key] = Float64Array.from(row.path, point => Number.isFinite(point[source]) ? point[source] : NaN);
  }
  if (leg.epoch.some((epoch, index) => index && epoch <= leg.epoch[index - 1])) throw new Error(`POOL_PATH_ORDER ${row.ticker}`);
  const index = leg.epoch.findIndex(epoch => Math.floor(epoch) >= counts.seconds[0]);
  leg.first_epoch = index < 0 ? null : leg.epoch[index];
  leg.suffix = new Int32Array(leg.epoch.length);
  let best = leg.epoch.length - 1;
  for (let cursor = best; cursor >= 0; cursor -= 1) {
    if (leg.last[cursor] <= leg.last[best]) best = cursor;
    leg.suffix[cursor] = best;
  }
  return leg;
}
function configureTickLibrary(binding) {
  if (!binding?.contract || !binding?.pairs || !binding?.receipt?.index?.sha256) throw new Error("POOL_TICK_LIBRARY_UNBOUND");
  const { contract } = binding;
  const totals = new Map();
  for (const pair of binding.pairs) {
    if (!totals.has(pair.category)) totals.set(pair.category, []);
    totals.get(pair.category).push(...pair.legs.map(leg => leg.print_total));
  }
  const thresholds = Object.fromEntries([...totals].map(([category, values]) => [category,
    poolQuantile(values, values.map(() => contract.likelihood_unit), contract.sleeper_category_quantile)]));
  for (const pair of binding.pairs) for (const leg of pair.legs) leg.family = poolFamily(leg, thresholds[pair.category], contract);
  binding.families = [...new Set(binding.pairs.flatMap(pair => pair.legs.map(leg => leg.family)).filter(Boolean))].sort();
  binding.thresholds = thresholds;
  tickLibrary = binding;
  return binding;
}
function atlasGateEpochs(meta) {
  if (!tickLibrary) throw new Error("POOL_TICK_LIBRARY_UNBOUND");
  return tickLibrary.contract.gates_minutes_to_bell.map(gate => meta.bell_epoch - gate * tickLibrary.contract.minute_seconds)
    .filter(epoch => epoch >= meta.discovery_epoch && epoch < meta.bell_epoch);
}
function retrieveNeighborhood(corpus) {
  if (!corpus.tick_library || corpus.tick_library !== tickLibrary) throw new Error("POOL_CORPUS_BINDING_MISMATCH");
  // No seven-neighbor or overlap retrieval remains in the author path.
  return [];
}
function ownPoolPair(state) {
  const contract = tickLibrary.contract;
  const legs = state.leg_ids.map(id => {
    const source = state.legs[id], formation = source.formation_end_epoch, bell = state.bell_epoch;
    const buckets = new Map(), seen = new Set();
    let lastPrice = null, bid = null, ask = null;
    const ordered = source.rows.filter(row => row.timestamp_epoch <= state.current_epoch && row.timestamp_epoch < bell);
    for (const row of ordered) {
      const epoch = row.source_timestamp_epoch ?? row.timestamp_epoch;
      if (row.kind === "PRINT") {
        if (seen.has(row.receipt)) continue;
        seen.add(row.receipt);
      }
      if (epoch < formation) {
        if (row.kind === "PRINT") lastPrice = row.price_cents;
        else if (row.kind === "BOOK") { bid = row.bid_cents; ask = row.ask_cents; }
        continue;
      }
      const second = Math.floor(epoch);
      if (!buckets.has(second)) buckets.set(second, []);
      buckets.get(second).push(row);
    }
    const leg = { id, formation, bell, open: source.anchor_cents, epoch: [], last: [], bid: [], ask: [], volume: [],
      first_epoch: null, print_total: 0, count_seconds: [], count_cum: [] };
    let volume = 0, low = null, high = null, previous = null;
    for (const [second, rows] of [...buckets].sort((a, b) => a[0] - b[0])) {
      const books = rows.filter(row => row.kind === "BOOK").sort((a, b) => a.source_row_index - b.source_row_index);
      if (books.length) { bid = books.at(-1).bid_cents; ask = books.at(-1).ask_cents; }
      const prints = rows.filter(row => row.kind === "PRINT").sort((a, b) => a.pool_source_row_index - b.pool_source_row_index);
      if (prints.some(row => !Number.isInteger(row.pool_source_row_index))) throw new Error("POOL_TRUE_PRINT_SOURCE_ORDER_MISSING");
      for (const print of prints) {
        lastPrice = print.price_cents;
        volume += print.size;
        leg.print_total += 1;
        low = low === null ? lastPrice : Math.min(low, lastPrice);
        high = high === null ? lastPrice : Math.max(high, lastPrice);
      }
      if (prints.length) { leg.count_seconds.push(second); leg.count_cum.push(leg.print_total); }
      const signature = JSON.stringify([lastPrice, bid, ask, volume, low, high]);
      if (signature === previous) continue;
      previous = signature;
      const epoch = Math.max(second, ...prints.map(row => row.source_timestamp_epoch ?? row.timestamp_epoch));
      leg.epoch.push(epoch); leg.last.push(lastPrice); leg.bid.push(bid); leg.ask.push(ask); leg.volume.push(volume);
      if (leg.first_epoch === null && leg.print_total && Math.floor(state.current_epoch) > second) leg.first_epoch = epoch;
    }
    return leg;
  });
  return poolPair(legs, { identity: state.event_id, category: state.category, date: state.event_id.split("-").at(-1).slice(0, 7) }, contract);
}
function poolRemaining(leg, gate, contract) {
  const epoch = leg.bell - gate * contract.minute_seconds;
  const current = poolSample(leg, epoch).last;
  const after = upperBound(leg.epoch, epoch);
  if (after === leg.epoch.length) return { level: current, mtb: gate };
  const index = leg.suffix[after];
  return current <= leg.last[index] ? { level: current, mtb: gate } :
    { level: leg.last[index], mtb: (leg.bell - leg.epoch[index]) / contract.minute_seconds };
}
function poolForecast(query, members, weights, gate, contract, families) {
  const current = poolLevels(query, gate, contract);
  const memberCurrent = members.map(member => poolLevels(member, gate, contract));
  const sides = query.legs.map((leg, side) => {
    const role = poolRole(current.sides[side].last, leg.open, contract);
    const sw = weights.map((weight, index) => {
      const member = members[index], observation = memberCurrent[index].sides[side];
      return member.first_mtb >= gate && PRICE_FIELDS.every(key => Number.isFinite(observation[key])) &&
        (role === "NOT_CALLABLE" || poolRole(observation.last, member.legs[side].open, contract) === role) ? weight : 0;
    });
    const effective = poolEss(sw), total = sum(sw);
    const remaining = members.map(member => poolRemaining(member.legs[side], gate, contract));
    const candidates = remaining.map((floor, index) => current.sides[side].last + floor.level - memberCurrent[index].sides[side].last);
    const familyMass = Object.fromEntries(families.map(name => [name, 0]));
    members.forEach((member, index) => { if (member.legs[side].family) familyMass[member.legs[side].family] += sw[index]; });
    const family = { probabilities: Object.fromEntries(Object.entries(familyMass).map(([name, mass]) => [name, total ? mass / total : null])),
      top: total ? Object.keys(familyMass).sort((a, b) => familyMass[b] - familyMass[a] || a.localeCompare(b))[0] : null };
    const floors = Object.fromEntries(contract.quantiles.map(fraction => [`q${fraction * (PAR_BUDGET_CENTS + contract.likelihood_unit)}`, {
      level_cents: poolQuantile(candidates, sw, fraction),
      minutes_to_bell: poolQuantile(remaining.map(floor => floor.mtb), sw, fraction),
    }]));
    for (const floor of Object.values(floors)) floor.epoch = Number.isFinite(floor.minutes_to_bell) ? query.bell - floor.minutes_to_bell * contract.minute_seconds : null;
    return { role, role_filter_bypassed: role === "NOT_CALLABLE", ess: effective, member_count: sw.filter(weight => weight > 0).length,
      weight_sum: total, status: effective >= contract.no_call_ess_floor ? "OK" : "NO-CALL: ESS < 10", family, floors,
      member_remaining_dip_zero_weighted_share: total ? sum(sw.filter((weight, index) => remaining[index].level === memberCurrent[index].sides[side].last)) / total : null };
  });
  return { member_count: weights.filter(weight => weight > 0).length, weight_sum: sum(weights), ess: poolEss(weights), sides };
}
function poolSnapshot(state) {
  if (!tickLibrary) throw new Error("POOL_TICK_LIBRARY_UNBOUND");
  const { contract, pairs, families } = tickLibrary;
  const query = ownPoolPair(state);
  if (!query) return { status: "INSUFFICIENT_EVIDENCE", reason: "FIRST_TRUE_TRADED_PAIR_NOT_BOUND", binding: tickLibrary.receipt };
  let memory = state.pool_cascade;
  if (!memory) {
    const members = pairs.filter(member => member.category === query.category && member.identity !== query.identity && member.date !== query.date && member.bell < query.formation);
    const unit = contract.likelihood_unit;
    const weights = members.map(member => unit / (unit + sum(member.first.sides.map((side, index) => Math.abs(side.last - query.first.sides[index].last)))) /
      (unit + Math.abs(member.first_mtb - query.first_mtb) / query.first_mtb));
    memory = { first_epoch: query.first_epoch, first: query.first, first_mtb: query.first_mtb, members, first_weights: weights,
      step_logs: weights.map(Math.log), last_gate: null, previous: null, validity: { status: "NO_PREVIOUS_GATE", weighted_share: null },
      roles: {}, volume_origin: query.first_mtb, volume_query: query.first.volume,
      volume_members: members.map(member => poolLevels(member, query.first_mtb, contract).volume), factors: null };
    state.pool_cascade = memory;
  }
  if (query.first_epoch !== memory.first_epoch || JSON.stringify(query.first) !== JSON.stringify(memory.first)) throw new Error("POOL_FIRST_BIND_CHANGED_AFTER_RECEIPT");
  const gate = (state.bell_epoch - state.current_epoch) / contract.minute_seconds;
  const due = contract.gates_minutes_to_bell.filter(value => value <= memory.first_mtb && value >= gate && (memory.last_gate === null || value < memory.last_gate));
  for (const at of due) {
    const current = poolLevels(query, at, contract), observed = memory.members.map(member => poolLevels(member, at, contract));
    const kVolume = observed.map((member, index) => Number.isFinite(member.volume) && Number.isFinite(memory.volume_members[index]) && memory.members[index].first_mtb >= memory.volume_origin ?
      contract.likelihood_unit / (contract.likelihood_unit + Math.abs(Math.log1p(member.volume - memory.volume_members[index]) - Math.log1p(current.volume - memory.volume_query))) : contract.likelihood_unit);
    const kPrice = observed.map(() => contract.likelihood_unit);
    if (memory.previous) {
      const prior = memory.previous;
      const errors = observed.map((member, index) => member.prices.map((value, coordinate) => Number.isFinite(value) && Number.isFinite(prior.members[index].prices[coordinate]) && Number.isFinite(current.prices[coordinate]) && Number.isFinite(prior.query.prices[coordinate]) ?
        Math.abs((value - prior.members[index].prices[coordinate]) - (current.prices[coordinate] - prior.query.prices[coordinate])) : null));
      const valid = errors.map((error, index) => error.every(Number.isFinite) && Number.isFinite(observed[index].volume) && prior.available[index]);
      const priorWeights = prior.weights.map((weight, index) => valid[index] ? weight : 0);
      const good = observed.map((member, index) => member.sides.every((side, sideIndex) =>
        Math.abs((side.last - prior.members[index].sides[sideIndex].last) - (current.sides[sideIndex].last - prior.query.sides[sideIndex].last)) <= contract.likelihood_unit));
      const total = sum(priorWeights), effective = poolEss(priorWeights);
      memory.validity = { status: effective >= contract.no_call_ess_floor ? "OK" : "INVALID: ESS < 10", previous_gate: prior.gate,
        weighted_share: total ? sum(priorWeights.filter((weight, index) => good[index])) / total : null, weight_sum: total, ess: effective };
      valid.forEach((usable, index) => { if (usable) kPrice[index] = contract.likelihood_unit / (contract.likelihood_unit + sum(errors[index])); });
    }
    memory.step_logs = memory.step_logs.map((value, index) => value + Math.log(kPrice[index]) + Math.log(kVolume[index]));
    const maxLog = Math.max(...memory.step_logs);
    const relative = memory.step_logs.map(value => Math.exp(value - maxLog));
    const pairAvailable = observed.map((member, index) => memory.members[index].first_mtb >= at && query.legs.every((leg, side) => {
      const role = poolRole(current.sides[side].last, leg.open, contract);
      return role === "NOT_CALLABLE" || poolRole(member.sides[side].last, memory.members[index].legs[side].open, contract) === role;
    }));
    memory.previous = { gate: at, query: current, members: observed, weights: relative.map((weight, index) => pairAvailable[index] ? weight : 0),
      available: pairAvailable.map((available, index) => available && observed[index].prices.every(Number.isFinite) && Number.isFinite(observed[index].volume)) };
    memory.factors = { gate_minutes_to_bell: at, volume_interval_from_mtb: memory.volume_origin,
      member_count: memory.members.length,
      k_price: Object.fromEntries(contract.quantiles.map(fraction => [fraction, poolQuantile(kPrice, kPrice.map(() => contract.likelihood_unit), fraction)])),
      k_volume: Object.fromEntries(contract.quantiles.map(fraction => [fraction, poolQuantile(kVolume, kVolume.map(() => contract.likelihood_unit), fraction)])) };
    memory.volume_origin = at; memory.volume_query = current.volume; memory.volume_members = observed.map(member => member.volume); memory.last_gate = at;
  }
  const stepMax = Math.max(...memory.step_logs);
  const stepWeights = memory.step_logs.map(value => Math.exp(value - stepMax));
  const baseWeights = memory.members.map(member => member.first.sides.every((side, index) =>
    (side.last >= contract.discovery_side_boundary_cents) === (memory.first.sides[index].last >= contract.discovery_side_boundary_cents)) ? contract.likelihood_unit : 0);
  const layers = { "FIRST-TICK-ONLY": poolForecast(query, memory.members, memory.first_weights, gate, contract, families),
    BASE: poolForecast(query, memory.members, baseWeights, gate, contract, families),
    "STEP-FORECAST": poolForecast(query, memory.members, stepWeights, gate, contract, families) };
  const roles = Object.fromEntries(query.legs.map(leg => {
    const prior = memory.roles[leg.id] ?? { first_bind: null, flip_count: 0, last_directional: null, as_of_epoch: null };
    const from = prior.as_of_epoch ?? query.first_epoch;
    // Only newly observed prefix points are processed. No full-path retrospective
    // classification can rewrite an earlier bind or erase an observed flip.
    const epochs = [...new Set([...leg.epoch.filter(epoch => epoch >= from && epoch <= state.current_epoch), state.current_epoch])].sort((a, b) => a - b);
    for (const epoch of epochs) {
      const call = poolRole(poolSample(leg, epoch).last, leg.open, contract);
      prior.current_role = call;
      if (call === "NOT_CALLABLE") continue;
      if (prior.first_bind === null) { prior.first_bind = call; prior.first_bind_receipt = state.receipt; prior.first_bind_epoch = epoch; }
      if (prior.last_directional !== null && prior.last_directional !== call) prior.flip_count += 1;
      prior.last_directional = call;
    }
    prior.as_of_epoch = state.current_epoch;
    memory.roles[leg.id] = prior;
    return [leg.id, { ...prior }];
  }));
  const sides = Object.fromEntries(query.legs.map((leg, index) => {
    const selected = ["FIRST-TICK-ONLY", "BASE"].find(layer => layers[layer].sides[index].status === "OK") ?? null;
    return [leg.id, { selected_layer: selected, status: selected ? "RESOLVED" : "INSUFFICIENT_EVIDENCE",
      current_last_cents: poolLevels(query, gate, contract).sides[index].last,
      roles: roles[leg.id], layers: Object.fromEntries(Object.entries(layers).map(([name, layer]) => [name, layer.sides[index]])) }];
  }));
  return { status: "BOUND", receipt: state.receipt, minutes_to_bell: gate, first_tick: { epoch: query.first_epoch, mtb: query.first_mtb,
    legs: query.legs.map(leg => leg.id), prices: memory.first.sides.map(side => side.last) },
    pool_member_count: memory.members.length, initial_ess: poolEss(memory.first_weights), layers: Object.fromEntries(Object.entries(layers).map(([name, layer]) => [name,
      { ess: layer.ess, member_count: layer.member_count, weight_sum: layer.weight_sum }])), sides,
    validity: memory.validity, likelihood_factors: memory.factors, binding: tickLibrary.receipt,
    author_order: ["FIRST-TICK-ONLY", "BASE"], step_author_role: "TELEMETRY_ONLY" };
}


module.exports = { PAR_BUDGET_CENTS, READER_NAMES, EXPECTED_RESOURCE_IDS, SIMILARITY_DECLARATION, CONDITIONAL_DIP_DECLARATION, sha256, createTapeState, observe, creditPosition, readAll, vectorFromReads, retrieveNeighborhood, assertResources, captureReceipt, assertCaptureReceipt, configureNeighborSpecialistBinding, configureTrueBellCellDepthMap, compactTickLeg, configureTickLibrary, poolPair, poolSnapshot, atlasGateEpochs };
