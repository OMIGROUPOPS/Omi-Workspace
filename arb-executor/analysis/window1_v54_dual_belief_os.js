"use strict";

// V54 layered dual-belief policy. The inherited V54 readers/retrieval remain the
// data plane. This module adds one joint, ordered derivation and never imports
// the ex-post DUAL_BELIEF_FORENSICS result.

const base = require("./window1_v54_functionable_os.js");
const survivorShapes = require("./window1_v54_survivor_shape_elimination.js");

const CONTRACT_SUM_CENTS = 100;
const SPREAD_SETTLE_COHERENCE_MAX_CENTS = 20;
const LAYER_PROVENANCE = Object.freeze({
  belief_format: "F-VS-101@0591792d",
  forensic_method_only: "F-VS-103@0591792d",
  layer_fit: "F-VS-060@521a1613",
  conditioning: "F-VS-066@521a1613",
  pair_coherence: "F-VS-053@31bce6d7",
  spread_settle: "L16@LAW_INDEX:0591792d",
  v3_map: "ac68e3bc:.claude/window1_second_seat/dives_t1_v3_20260823/TRUE_BELL_CELL_DEPTH_MAP.json",
  v3_source_key: "LIBRARY_CLOSE_CENTS",
  v3_runtime_rekey: "CURRENT_CAUSAL_BEST_BID_CENTS",
  micro_micro_store: "EXTERNAL_CUSTODY_DUAL_BOOK+EXTERNAL_CUSTODY_TRUE_PRINTS:SUBSECOND",
  phase_conditioning_fix: "F-VS-111@3be11997",
  live_deadline_fix: "F-VS-112@3be11997",
  remaining_dip_inversion_fix: "F-VS-114(b)@9ff83002",
  envelope_floor_side_fix: "F-VS-114(a)@9ff83002",
  envelope_migration_fix: "F-VS-114(c)@9ff83002",
  double_subtraction_fix: "F-VS-117b@c08ce381",
  coherence_placement_fix: "F-VS-118@c08ce381",
  atomic_cancel_replace_fix: "F-VS-118@c08ce381",
  own_low_return_fix: "F-VS-120@97411938",
  atomic_rearm_fix: "F-VS-120@97411938",
  phase_central_estimate_fix: "F-VS-124@48dbf36b",
  consume_live_touch_fix: "F-VS-125@48dbf36b",
  touch_subordination_fix: "F-VS-129@3e3d3548",
  disagrees_not_trading_state: "DISPATCH_TOUCH_SUBORDINATED@2026-08-24",
  inside_spread_reach_fix: "F-VS-130@3e3d3548",
  survivor_shape_restoration: "F-VS-133/F-VS-135@e7081336; structural source @189eaa20",
  carried_conviction: "F-VS-134@e7081336",
  continuous_belief_movement: "RIDER_BELIEF_EVOLVES@2026-08-24",
  own_evidence_sufficiency: "F-VS-068@521a1613",
});

const PHASE_CENTRAL_BANDS = Object.freeze([
  Object.freeze({ id: "P00_10", low: 0, high: 0.1 }),
  Object.freeze({ id: "P10_30", low: 0.1, high: 0.3 }),
  Object.freeze({ id: "P30_50", low: 0.3, high: 0.5 }),
  Object.freeze({ id: "P50_70", low: 0.5, high: 0.7 }),
  Object.freeze({ id: "P70_90", low: 0.7, high: 0.9 }),
  Object.freeze({ id: "P90_100", low: 0.9, high: 1 }),
]);
let phaseCentralSurface = null;

function configurePhaseCentralSurface(binding) {
  if (!binding || binding.kind !== "F_VS_124_PHASE_CATEGORY_CENTRAL_FUTURE_LOW_SURFACE") throw new Error("PHASE_CENTRAL_SURFACE_KIND_MISMATCH");
  if (!binding.sha256 || !binding.source_sha256 || !Array.isArray(binding.cells) || !binding.cells.length) throw new Error("PHASE_CENTRAL_SURFACE_INCOMPLETE");
  phaseCentralSurface = Object.freeze({ ...binding, cells: binding.cells.map((cell) => Object.freeze({ ...cell })) });
}

function phaseCentralCell(category, fraction) {
  if (!phaseCentralSurface || !Number.isFinite(fraction)) return null;
  const band = PHASE_CENTRAL_BANDS.find((row, index) => fraction >= row.low && (fraction < row.high || (index === PHASE_CENTRAL_BANDS.length - 1 && fraction <= row.high)));
  return band ? phaseCentralSurface.cells.find((cell) => cell.category === category && cell.phase_band === band.id) ?? null : null;
}

function finite(value) { return Number.isFinite(value) ? value : null; }
function cent(value) { return Number.isInteger(value) && value >= 1 && value <= 99 ? value : null; }
function clamp(value, low, high) { return Math.max(low, Math.min(high, value)); }
function sum(values) { return values.filter(Number.isFinite).reduce((a, b) => a + b, 0); }
function round2(value) { return Number.isFinite(value) ? Math.round(value * 100) / 100 : null; }

function weightedQuantile(rows, field, quantile) {
  const valid = rows
    .filter((row) => Number.isFinite(row[field]) && Number.isFinite(row.conditioning_weight) && row.conditioning_weight > 0)
    .sort((a, b) => a[field] - b[field] || String(a.event_id).localeCompare(String(b.event_id)));
  const total = sum(valid.map((row) => row.conditioning_weight));
  if (!valid.length || total <= 0) return null;
  const threshold = total * quantile;
  let running = 0;
  for (const row of valid) {
    running += row.conditioning_weight;
    if (running >= threshold) return row[field];
  }
  return valid.at(-1)[field];
}

function weightedMean(rows, field) {
  const valid = rows.filter((row) => Number.isFinite(row[field]) && Number.isFinite(row.conditioning_weight) && row.conditioning_weight > 0);
  const total = sum(valid.map((row) => row.conditioning_weight));
  return total > 0 ? sum(valid.map((row) => row[field] * row.conditioning_weight)) / total : null;
}

function memberFutureLowAtFraction(path, fraction) {
  if (!Array.isArray(path) || !path.length || !Number.isFinite(fraction)) return null;
  let selected = null;
  for (const row of path) {
    if (!Number.isFinite(row.window_fraction) || row.window_fraction > fraction) break;
    selected = row;
  }
  if (!selected) selected = path[0];
  return Number.isFinite(selected?.future_low_minus_seen_low_cents) ? selected : null;
}

// F-VS-114(b): remaining dip is conditioned total travel minus the travel that
// has already arrived at this receipt.  The old implementation subtracted the
// arrived share and therefore made the claimed remaining dip grow toward the
// bell.  Only members with a lawful floor-time observation can participate in
// this arithmetic.  All quantiles below use that one row universe so the raw
// summary and placement input cannot silently disagree (F-VS-114(c)).
function conditionTravelPrior(baseRow, category) {
  const neighborLeg = baseRow?.derivation?.neighbor_leg ?? {};
  const own = neighborLeg.own_evidence ?? {};
  const ownFraction = finite(own.window_fraction);
  const rows = (neighborLeg.rows ?? []).flatMap((row) => {
    const fullTravel = finite(row.remaining_dip_cents);
    const memberFloorFraction = finite(row.member_floor_fraction);
    const conditioningWeight = finite(row.weight);
    const futureLowRow = memberFutureLowAtFraction(row.future_low_return_path, ownFraction);
    if (!(Number.isFinite(ownFraction) && Number.isFinite(fullTravel) && Number.isFinite(memberFloorFraction) && memberFloorFraction > 0 && Number.isFinite(conditioningWeight) && conditioningWeight > 0 && futureLowRow)) return [];
    const phaseScale = clamp(ownFraction / memberFloorFraction, 0, 1);
    const arrivedDip = fullTravel * phaseScale;
    return [{
      event_id: row.event_id,
      source_receipt: row.citation_receipt_id ?? null,
      full_travel_cents: fullTravel,
      member_floor_fraction: memberFloorFraction,
      own_window_fraction: ownFraction,
      phase_scale: round2(phaseScale),
      conditioned_total_dip_cents: fullTravel,
      arrived_dip_cents: arrivedDip,
      remaining_dip_cents: Math.max(0, fullTravel - arrivedDip),
      member_seen_true_trade_low_cents: futureLowRow.seen_true_trade_low_cents,
      member_strict_future_true_trade_low_cents: futureLowRow.strict_future_true_trade_low_cents,
      future_low_minus_seen_low_cents: futureLowRow.future_low_minus_seen_low_cents,
      future_low_source_row_ref: futureLowRow.source_row_ref,
      future_low_return_source: row.future_low_return_source ?? null,
      conditioning_weight: conditioningWeight,
      own_evidence_match_grade: row.evidence_match_grade ?? null,
    }];
  });
  const q = (field, p) => {
    const value = weightedQuantile(rows, field, p);
    return Number.isFinite(value) ? Math.max(0, Math.round(value)) : null;
  };
  const distribution = (field) => ({ q25: q(field, 0.25), q50: q(field, 0.5), q75: q(field, 0.75) });
  const targetFloorFraction = weightedQuantile(rows, "member_floor_fraction", 0.5);
  const sourceRows = neighborLeg.rows ?? [];
  const excludedUntimedRows = sourceRows.filter((row) => !Number.isFinite(row.member_floor_fraction) || row.member_floor_fraction <= 0).map((row) => ({ event_id: row.event_id, member_floor_fraction: row.member_floor_fraction ?? null, reason: "NO_POSITIVE_MEMBER_FLOOR_FRACTION" }));
  const excludedFutureLowRows = sourceRows.filter((row) => !memberFutureLowAtFraction(row.future_low_return_path, ownFraction)).map((row) => ({ event_id: row.event_id, leg_id: row.leg_id ?? null, reason: "NO_BELL_BOUNDED_STRICT_FUTURE_LOW_AT_CAUSAL_MEMBER_PHASE" }));
  const neighborTailEstimate = weightedMean(rows, "future_low_minus_seen_low_cents");
  const centralCell = phaseCentralCell(category, ownFraction);
  const expectedOffset = finite(centralCell?.q50_cents);
  return {
    status: rows.length && centralCell ? "RESOLVED" : "INSUFFICIENT_EVIDENCE",
    method: "EXPECTED_FUTURE_LOW_EQUALS_CAUSAL_OWN_SEEN_LOW_PLUS_PHASE_CATEGORY_POPULATION_Q50; TERMINAL_PATH_POINT_EXCLUDED; F_VS_124_PHASE_BANDS; SEVEN_NEIGHBOR_TAIL_RETAINED_AS_TELEMETRY_NOT_CENTRAL",
    upstream_all_member_distribution_reference_cents: neighborLeg.conditional_remaining_dip_distribution_cents ?? {},
    conditioned_total_dip_distribution_cents: distribution("conditioned_total_dip_cents"),
    arrived_dip_distribution_cents: distribution("arrived_dip_cents"),
    remaining_dip_distribution_cents: distribution("remaining_dip_cents"),
    future_low_minus_seen_low_distribution_cents: distribution("future_low_minus_seen_low_cents"),
    expected_future_low_minus_seen_low_cents: Number.isFinite(expectedOffset) ? expectedOffset : null,
    phase_central_estimate: centralCell ? {
      category,
      phase_band: centralCell.phase_band,
      phase_low_inclusive: centralCell.phase_low_inclusive,
      phase_high_exclusive: centralCell.phase_high_exclusive,
      members: centralCell.members,
      q25_cents: centralCell.q25_cents,
      q50_cents: centralCell.q50_cents,
      q75_cents: centralCell.q75_cents,
      q50_midrank: centralCell.q50_midrank,
      estimate_rank_in_population: centralCell.q50_midrank,
      source_sha256: phaseCentralSurface?.source_sha256 ?? null,
      surface_sha256: phaseCentralSurface?.sha256 ?? null,
      provenance: LAYER_PROVENANCE.phase_central_estimate_fix,
    } : null,
    displaced_seven_neighbor_tail_estimate_cents: Number.isFinite(neighborTailEstimate) ? neighborTailEstimate : null,
    row_universe: {
      source_rows: sourceRows.length,
      floor_timed_rows: rows.length,
      excluded_untimed_rows: excludedUntimedRows,
      excluded_future_low_rows: excludedFutureLowRows,
      one_universe_for_total_arrived_and_remaining_quantiles: true,
    },
    own_evidence: own,
    target_floor_fraction: Number.isFinite(targetFloorFraction) ? targetFloorFraction : null,
    rows,
    provenance: [LAYER_PROVENANCE.phase_central_estimate_fix, LAYER_PROVENANCE.own_low_return_fix, LAYER_PROVENANCE.conditioning],
  };
}

function actionForTarget(active, target, reason) {
  if (!cent(target)) return { action: active ? "CANCEL_REST" : "HOLD_REST", target_cents: null, reason };
  if (!active) return { action: "PLACE_REST", target_cents: target, reason };
  if (active === target) return { action: "HOLD_REST", target_cents: target, reason };
  return { action: "REPRICE_REST", target_cents: target, reason };
}

function interimFamily(reads, legId) {
  const drift = finite(reads.drift.value[legId]?.drift_cents);
  const shape = reads.shape_survival.value[legId] ?? {};
  if (!Number.isFinite(drift)) return { family: "INSUFFICIENT_EVIDENCE", drift_cents: null, directional_step_share: shape.directional_step_share ?? null, observed_steps: shape.observed_steps ?? 0 };
  if (drift < 0) return { family: "INTERIM_DOWN_TRAVEL", drift_cents: drift, directional_step_share: shape.directional_step_share ?? null, observed_steps: shape.observed_steps ?? 0 };
  if (drift > 0) return { family: "INTERIM_UP_TRAVEL", drift_cents: drift, directional_step_share: shape.directional_step_share ?? null, observed_steps: shape.observed_steps ?? 0 };
  return { family: "INTERIM_STILL", drift_cents: drift, directional_step_share: shape.directional_step_share ?? null, observed_steps: shape.observed_steps ?? 0 };
}

function layerReceipt(state, layer, status, rowRefs, context) {
  return base.captureReceipt({
    citationType: `DUAL_BELIEF_${layer}`,
    sourceId: state.event_id,
    capturedAtReceipt: state.receipt,
    rowRefs: [...new Set((rowRefs ?? []).filter(Boolean).map(String))],
    status: status === "RESOLVED" ? "RECEIPT" : "RESOURCE-GAP",
    context: { layer, status, ...context },
  });
}

function freshDeadline(state, legId, conditionedPrior) {
  const formation = finite(state.legs[legId].formation_end_epoch);
  const bell = finite(state.bell_epoch);
  const now = finite(state.current_epoch);
  const fraction = finite(conditionedPrior?.target_floor_fraction);
  if (!(Number.isFinite(formation) && Number.isFinite(bell) && bell > formation && Number.isFinite(now) && Number.isFinite(fraction))) return null;
  const modeledEpoch = formation + clamp(fraction, 0, 1) * (bell - formation);
  const deadlineEpoch = clamp(Math.max(now, modeledEpoch), now, bell);
  return {
    emitted_at_epoch: now,
    emitted_at_receipt: state.receipt,
    deadline_epoch: deadlineEpoch,
    minutes_to_bell_at_emission: Math.max(0, Math.round((bell - now) / 60)),
    deadline_minutes_to_bell: Math.max(0, Math.round((bell - deadlineEpoch) / 60)),
    target_floor_fraction: fraction,
    modeled_floor_epoch: modeledEpoch,
    stale_modeled_deadline_clamped_to_emission: modeledEpoch < now,
    derives_fresh_at_each_emission: true,
    provenance: LAYER_PROVENANCE.live_deadline_fix,
  };
}

function beliefForLeg({ state, reads, neighborhood, baseRow, conditionedPrior, legId, macroStatus, macroFamily }) {
  const vector = baseRow.vector;
  const orientedIndex = vector.oriented_leg_ids.indexOf(legId);
  const topNeighbor = neighborhood[0] ?? null;
  const topNeighborLeg = topNeighbor?.legs?.[orientedIndex] ?? null;
  const raw = baseRow.derivation.neighbor_leg?.conditional_remaining_dip_distribution_cents ?? {};
  const conditioned = conditionedPrior?.remaining_dip_distribution_cents ?? {};
  const own = baseRow.derivation.neighbor_leg?.own_evidence ?? {};
  const readerLevel = cent(reads.drift.value[legId]?.current_cents);
  const liveBid = cent(reads.books.value[legId]?.bid_cents);
  const liveAsk = cent(reads.books.value[legId]?.ask_cents);
  const mapCell = baseRow.derivation.true_bell_cell_depth_map?.cell ?? null;
  // F-VS-120: the seen low is state, not the answer.  Members supply the
  // bell-bounded strict-future low relative to the low they had seen at the
  // same phase.  The existing own-evidence conditioning weights form the
  // expectation; no return-to-low assumption or numerical offset survives.
  const expectedFutureLowOffset = conditionedPrior?.expected_future_low_minus_seen_low_cents;
  const predictedRaw = cent(own.observed_low_cents) && Number.isFinite(expectedFutureLowOffset)
    ? own.observed_low_cents + Math.round(expectedFutureLowOffset)
    : null;
  const predicted = cent(predictedRaw);
  const minutesToBell = Number.isFinite(state.bell_epoch) ? Math.max(0, Math.round((state.bell_epoch - state.current_epoch) / 60)) : null;
  const deadline = freshDeadline(state, legId, conditionedPrior);
  const byMinutes = deadline?.deadline_minutes_to_bell ?? null;
  const volume = round2(Math.log1p(sum(Object.values(reads.volume.value).map((row) => row.contracts))));
  const formationComplete = Number.isFinite(reads.anchor_settle.value.formation_progress[legId]) && reads.anchor_settle.value.formation_progress[legId] >= 1;
  const beliefPrice = formationComplete && liveBid && liveAsk && liveBid < liveAsk ? Math.floor((liveBid + liveAsk) / 2) : null;
  const beliefPriceBasis = beliefPrice ? "SETTLED_BOOK_MID_SERIES_FLOORED_FROM_BID_ASK" : null;
  const bookReceipt = reads.books.value[legId]?.receipt ?? null;
  const microResolved = macroStatus === "RESOLVED"
    && formationComplete
    && Number.isInteger(predicted)
    && Number.isInteger(readerLevel)
    && Number.isInteger(beliefPrice)
    && Number.isInteger(liveBid)
    && Number.isInteger(liveAsk)
    && liveBid < liveAsk
    && Boolean(bookReceipt)
    && Boolean(topNeighbor?.citation_receipt_id);
  const store = mapCell
    ? `${state.category}|${mapCell.price_cell} (V3 map @ac68e3bc; SOURCE_KEY=LIBRARY_CLOSE_CENTS; CAUSAL_REKEY=CURRENT_BEST_BID_CENTS)`
    : `UNMAPPED (V3 map @ac68e3bc; SOURCE_KEY=LIBRARY_CLOSE_CENTS; CAUSAL_REKEY=CURRENT_BEST_BID_CENTS)`;
  const neighborName = topNeighbor
    ? `${topNeighbor.event_id}@${round2(topNeighbor.score)} [${topNeighbor.quality}/${topNeighbor.grain ?? "UNKNOWN"}; MACRO/MICRO; ${topNeighbor.citation_receipt_id}]`
    : "NO_GRADED_NEIGHBOR";
  const plain = microResolved
    ? `believes ${legId} at ${beliefPrice}¢ [${beliefPriceBasis}; bid=${liveBid}¢; ask=${liveAsk}¢; book-receipt=${bookReceipt}] at ${minutesToBell ?? "UNKNOWN"}min-to-bell with ${volume ?? "UNKNOWN"} vol_log1p in ${state.category}, using ${store} + ${neighborName}, SHOULD drift to ${predicted}¢ by ${byMinutes ?? "UNKNOWN"}min-to-bell [PHASE_CENTRAL_ESTIMATE=${conditionedPrior?.phase_central_estimate?.q50_cents ?? "UNKNOWN"}¢; CENTRAL_ESTIMATE_RANK=${conditionedPrior?.phase_central_estimate?.estimate_rank_in_population ?? "UNKNOWN"}; CENTRAL_MEMBERS=${conditionedPrior?.phase_central_estimate?.members ?? "UNKNOWN"}; CENTRAL_CELL=${conditionedPrior?.phase_central_estimate?.phase_band ?? "UNKNOWN"}; deadline-epoch=${deadline?.deadline_epoch ?? "UNKNOWN"}; deadline-emitted-now=${deadline?.emitted_at_epoch ?? "UNKNOWN"}; deadline-receipt=${deadline?.emitted_at_receipt ?? "UNKNOWN"}]`
    : null;
  return {
    leg_id: legId,
    status: microResolved ? "RESOLVED" : "INSUFFICIENT_EVIDENCE",
    family: macroFamily.family,
    current_cents: beliefPrice,
    belief_price_cents: beliefPrice,
    belief_price_basis: beliefPriceBasis,
    belief_price_book_receipt: bookReceipt,
    reader_level_cents: readerLevel,
    envelope_high_cents: readerLevel,
    live_bid_cents: liveBid,
    live_ask_cents: liveAsk,
    predicted_cents: predicted,
    minutes_to_bell: minutesToBell,
    predicted_minutes_to_bell: byMinutes,
    deadline,
    volume_log1p: volume,
    store,
    v3_map_semantics: {
      source_key: LAYER_PROVENANCE.v3_source_key,
      runtime_rekey: LAYER_PROVENANCE.v3_runtime_rekey,
      stated_verbatim: true,
      cell: mapCell,
    },
    top_neighbor: topNeighbor ? { event_id: topNeighbor.event_id, score: topNeighbor.score, coverage: topNeighbor.coverage, quality: topNeighbor.quality, grain: topNeighbor.grain, licensed_layers: topNeighbor.licensed_layers, citation_receipt_id: topNeighbor.citation_receipt_id } : null,
    own_evidence: own,
    raw_remaining_dip_cents: raw,
    remaining_dip_cents: conditioned,
    remaining_dip_consumption: {
      role: "LEGACY_TRAVEL_TELEMETRY_NOT_BELIEF_TARGET",
      own_low_return_assumption_removed: true,
      expected_future_low_minus_seen_low_cents: expectedFutureLowOffset ?? null,
      future_low_minus_seen_low_distribution_cents: conditionedPrior?.future_low_minus_seen_low_distribution_cents ?? {},
      provenance: LAYER_PROVENANCE.own_low_return_fix,
    },
    conditioned_total_dip_cents: conditionedPrior?.conditioned_total_dip_distribution_cents ?? {},
    arrived_dip_cents: conditionedPrior?.arrived_dip_distribution_cents ?? {},
    phase_conditioning: conditionedPrior,
    book_receipt: bookReceipt,
    plain_sentence: plain,
  };
}

function lineageTarget(lineage, liveAsk) {
  const target = cent(lineage?.target_cents);
  // The lineage row is already an independently licensed placement. Re-applying
  // the contemporary ask here changed its byte-frozen action stream; the dual
  // layer may not silently re-adjudicate that upstream license.
  if (!target) return null;
  return target;
}

function allocateUnderPar(targets, lowerBounds) {
  const ids = Object.keys(targets);
  if (ids.length !== 2 || ids.some((id) => !cent(targets[id]))) return { lawful: false, targets, reason: "PAIR_TARGET_INCOMPLETE" };
  let excess = targets[ids[0]] + targets[ids[1]] - base.PAR_BUDGET_CENTS;
  if (excess <= 0) return { lawful: true, targets: { ...targets }, reason: "JOINT_TARGET_ALREADY_UNDER_PAR", excess_cents: 0 };
  const out = { ...targets };
  const headroom = Object.fromEntries(ids.map((id) => [id, Math.max(0, out[id] - lowerBounds[id])]));
  for (const id of [...ids].sort((a, b) => headroom[b] - headroom[a] || a.localeCompare(b))) {
    const reduction = Math.min(excess, headroom[id]);
    out[id] -= reduction;
    excess -= reduction;
  }
  return excess === 0
    ? { lawful: true, targets: out, reason: "JOINT_TARGET_RECONCILED_INSIDE_COHERENT_ENVELOPES", excess_cents: targets[ids[0]] + targets[ids[1]] - base.PAR_BUDGET_CENTS }
    : { lawful: false, targets, reason: "COHERENT_ENVELOPES_CANNOT_SATISFY_PAR", excess_cents: excess };
}

function deriveJointActions({ state, reads, neighborhood, lineageByLeg, resources }) {
  if (!state.dual_belief) state.dual_belief = { first_coherence: null, current_envelopes: null, carried_convictions: {}, coherence_history: [], envelope_history: [], conviction_history: [], first_lawful_coherence_by_leg: {}, rearm_by_leg: {} };
  if (!state.dual_belief.first_lawful_coherence_by_leg) state.dual_belief.first_lawful_coherence_by_leg = {};
  if (!state.dual_belief.rearm_by_leg) state.dual_belief.rearm_by_leg = {};
  if (!state.dual_belief.carried_convictions) state.dual_belief.carried_convictions = {};
  if (!state.dual_belief.conviction_history) state.dual_belief.conviction_history = [];
  const openIds = state.leg_ids.filter((id) => !reads.half_pair_state.value.legs[id].credited);
  const baseRows = new Map();
  for (const legId of openIds) {
    baseRows.set(legId, base.deriveAction({ state, reads, neighborhood, legId, lineage: lineageByLeg[legId], resources }));
  }
  const allFormationComplete = state.leg_ids.every((id) => Number.isFinite(reads.anchor_settle.value.formation_progress[id]) && reads.anchor_settle.value.formation_progress[id] >= 1);
  const coarseNeighbors = neighborhood.filter((row) => ["FOUNDATION_MINUTE_BELL_BOUNDED", "RANGE_BELL_BOUNDED", "HISTORICAL_BELL_BOUNDED"].includes(row.quality));
  const survivorUpdate = survivorShapes.advanceSurvivorShapes({ state, reads });
  const macroFamilies = Object.fromEntries(state.leg_ids.map((id) => [id, interimFamily(reads, id)]));
  const conditionedPriors = Object.fromEntries(openIds.map((id) => [id, conditionTravelPrior(baseRows.get(id), state.category)]));
  const macroResolved = allFormationComplete && coarseNeighbors.length > 0 && openIds.every((id) => {
    return Number.isFinite(conditionedPriors[id]?.expected_future_low_minus_seen_low_cents);
  });
  const macroStatus = macroResolved ? "RESOLVED" : "INSUFFICIENT_EVIDENCE";
  const macroReceipt = layerReceipt(state, "MACRO", macroStatus, coarseNeighbors.flatMap((row) => [row.citation_receipt_id, ...(row.source_receipts ?? []).map((source) => source.row_ref)]), {
    families: macroFamilies,
    survivor_shapes: survivorUpdate,
    travel_priors: Object.fromEntries(openIds.map((id) => [id, conditionedPriors[id] ?? null])),
    sources: coarseNeighbors.map((row) => ({ event_id: row.event_id, store: row.quality, grain: row.grain, licensed_layers: row.licensed_layers, citation_receipt_id: row.citation_receipt_id })),
    provenance: LAYER_PROVENANCE.layer_fit,
  });
  const beliefs = {};
  for (const legId of openIds) beliefs[legId] = beliefForLeg({ state, reads, neighborhood, baseRow: baseRows.get(legId), conditionedPrior: conditionedPriors[legId], legId, macroStatus, macroFamily: macroFamilies[legId] });
  const microResolved = macroResolved && openIds.every((id) => beliefs[id].status === "RESOLVED");
  const microStatus = microResolved ? "RESOLVED" : "INSUFFICIENT_EVIDENCE";
  const microReceipt = layerReceipt(state, "MICRO", microStatus, openIds.flatMap((id) => [beliefs[id].book_receipt, beliefs[id].top_neighbor?.citation_receipt_id]), {
    beliefs,
    conditioning: LAYER_PROVENANCE.conditioning,
    v3_map_keying: { source: LAYER_PROVENANCE.v3_source_key, runtime: LAYER_PROVENANCE.v3_runtime_rekey, stated_verbatim: true },
  });
  const subsecondRow = state.leg_ids.some((id) => state.legs[id].rows.at(-1)?.receipt === state.receipt);
  const microMicroResolved = microResolved && subsecondRow && state.leg_ids.every((id) => Boolean(reads.books.value[id]?.receipt));
  const microMicroStatus = microMicroResolved ? "RESOLVED" : "INSUFFICIENT_EVIDENCE";
  const microMicroReceipt = layerReceipt(state, "MICRO_MICRO", microMicroStatus, [state.receipt, ...state.leg_ids.map((id) => reads.books.value[id]?.receipt)], {
    tick_state: Object.fromEntries(state.leg_ids.map((id) => [id, reads.books.value[id]])),
    store: LAYER_PROVENANCE.micro_micro_store,
    coarse_number_timed_action: false,
  });
  const predicted = openIds.map((id) => beliefs[id].predicted_cents);
  const predictedSum = predicted.length === 2 && predicted.every(Number.isInteger) ? predicted[0] + predicted[1] : null;
  const spread = finite(reads.joint_state_spread_dwell.value.spread_sum_cents);
  const coherentNow = microMicroResolved
    && openIds.length === 2
    && Number.isInteger(predictedSum)
    && Number.isFinite(spread)
    && spread <= SPREAD_SETTLE_COHERENCE_MAX_CENTS
    && Math.abs(predictedSum - CONTRACT_SUM_CENTS) <= spread;
  const coherence = {
    timestamp_epoch: state.current_epoch,
    receipt: state.receipt,
    status: coherentNow ? "COHERENT" : microMicroResolved ? "DISAGREES" : "INSUFFICIENT_EVIDENCE",
    predicted_sum_cents: predictedSum,
    contract_sum_cents: CONTRACT_SUM_CENTS,
    absolute_mirror_gap_cents: Number.isInteger(predictedSum) ? Math.abs(predictedSum - CONTRACT_SUM_CENTS) : null,
    spread_settle_bound_cents: spread,
    spread_settle_max_cents: SPREAD_SETTLE_COHERENCE_MAX_CENTS,
    provenance: [LAYER_PROVENANCE.pair_coherence, LAYER_PROVENANCE.spread_settle],
  };
  const priorCoherence = state.dual_belief.coherence_history.at(-1);
  const coherenceSignature = `${coherence.status}|${coherence.predicted_sum_cents ?? "NONE"}|${coherence.spread_settle_bound_cents ?? "NONE"}`;
  const priorCoherenceSignature = priorCoherence ? `${priorCoherence.status}|${priorCoherence.predicted_sum_cents ?? "NONE"}|${priorCoherence.spread_settle_bound_cents ?? "NONE"}` : null;
  if (coherenceSignature !== priorCoherenceSignature) state.dual_belief.coherence_history.push(coherence);
  // F-VS-134/135: the decision reads the conviction that existed before this
  // receipt. The current receipt proposes an update; it is committed only after
  // placement has consumed and re-stated the carried basis.
  const priorEnvelopes = state.dual_belief.current_envelopes
    ? JSON.parse(JSON.stringify(state.dual_belief.current_envelopes))
    : {};
  const proposedEnvelopes = coherentNow
    ? Object.fromEntries(openIds.map((id) => [id, { low_cents: beliefs[id].predicted_cents, high_cents: beliefs[id].envelope_high_cents, belief_receipt: state.receipt }]))
    : {};
  const decisionEnvelopes = {};
  const nextEnvelopes = { ...priorEnvelopes };
  const convictionEvolution = {};
  const nextConvictions = { ...state.dual_belief.carried_convictions };
  const envelopeMigrations = {};
  for (const id of openIds) {
    const prior = priorEnvelopes[id] ?? null;
    const proposed = proposedEnvelopes[id] ?? null;
    const priorConviction = state.dual_belief.carried_convictions[id] ?? null;
    const survivor = survivorUpdate.legs[id];
    const survivorIds = survivor?.survivor_shapes ?? [];
    const priorSupport = priorConviction?.supporting_shape_ids ?? [];
    const supportIntersection = priorSupport.filter((shapeId) => survivorIds.includes(shapeId));
    const eliminationsStillHold = !priorConviction || supportIntersection.length > 0;
    const book = reads.books.value[id];
    const basisRestated = Boolean(book?.receipt && cent(book.bid_cents) && cent(book.ask_cents) && book.bid_cents < book.ask_cents && survivorIds.length);
    const priorReceiptReadable = Boolean(priorConviction?.belief_receipt && priorConviction.belief_receipt !== state.receipt);
    let effective = null;
    let update = "NO_LAWFUL_ENVELOPE";
    if (proposed) {
      effective = proposed;
      if (!prior) update = "FORMED_NEW_CONVICTION";
      else if (prior.low_cents === proposed.low_cents && prior.high_cents === proposed.high_cents) update = "CONFIRMED_CARRIED_CONVICTION";
      else if (proposed.low_cents >= prior.low_cents && proposed.high_cents <= prior.high_cents) update = "TIGHTENED_CARRIED_CONVICTION";
      else update = "SHIFTED_CARRIED_CONVICTION";
    } else if (coherence.status !== "DISAGREES" && prior && priorConviction && eliminationsStillHold && basisRestated && priorReceiptReadable) {
      effective = prior;
      update = "CARRIED_PRIOR_RECEIPT_CONVICTION_WITH_CURRENT_BASIS_RESTATEMENT";
    } else if (priorConviction && !eliminationsStillHold) {
      update = "DROPPED_CONVICTION_SUPPORTING_ELIMINATIONS_OVERTURNED";
      delete nextEnvelopes[id];
      delete nextConvictions[id];
    } else if (coherence.status === "DISAGREES") update = "DISAGREES_HOLDS_OR_REDERIVES_NO_PLACEMENT";
    decisionEnvelopes[id] = effective;
    const migrated = Boolean(prior && effective && (prior.low_cents !== effective.low_cents || prior.high_cents !== effective.high_cents));
    envelopeMigrations[id] = { migrated, from: prior, to: effective, receipt: state.receipt, provenance: LAYER_PROVENANCE.envelope_migration_fix };
    convictionEvolution[id] = {
      update,
      prior_envelope: prior,
      proposed_envelope: proposed,
      effective_envelope: effective,
      prior_conviction_receipt: priorConviction?.belief_receipt ?? null,
      prior_receipt_genuinely_readable: priorReceiptReadable,
      basis_re_stated_at_current_receipt: basisRestated,
      basis_book_receipt: book?.receipt ?? null,
      supporting_shape_ids_before: priorSupport,
      surviving_shape_ids_now: survivorIds,
      supporting_shape_ids_still_alive: supportIntersection,
      eliminations_still_hold: eliminationsStillHold,
      movement_evidence: survivor?.movement ?? null,
      movement_statement: `${survivor?.movement?.effect ?? "NO_MOVEMENT_EVIDENCE"}: move=${survivor?.movement?.move_cents ?? "UNKNOWN"}c; eliminated=${(survivor?.eliminated_now ?? []).join("|") || "NONE"}; reinstated=${(survivor?.reinstated_now ?? []).join("|") || "NONE"}`,
      carried_conviction_law: LAYER_PROVENANCE.carried_conviction,
    };
    if (effective) {
      nextEnvelopes[id] = effective;
      nextConvictions[id] = {
        envelope: effective,
        belief_receipt: proposed ? state.receipt : priorConviction.belief_receipt,
        latest_basis_restatement_receipt: state.receipt,
        supporting_shape_ids: [...survivorIds],
        movement_statement: convictionEvolution[id].movement_statement,
        provenance: LAYER_PROVENANCE.carried_conviction,
      };
    }
    if (migrated) state.dual_belief.envelope_history.push({ leg_id: id, ...envelopeMigrations[id] });
  }
  if (coherentNow && !state.dual_belief.first_coherence) state.dual_belief.first_coherence = { ...coherence, envelopes: proposedEnvelopes, beliefs: JSON.parse(JSON.stringify(beliefs)) };

  const beliefMode = openIds.some((id) => Boolean(decisionEnvelopes[id]));
  const targets = {};
  const lowerBounds = {};
  const envelopePlacement = {};
  for (const legId of openIds) {
    const book = reads.books.value[legId];
    const liveBid = cent(book?.bid_cents), liveAsk = cent(book?.ask_cents);
    const active = cent(reads.half_pair_state.value.legs[legId].standing_target_cents);
    if (decisionEnvelopes[legId] && coherentNow) {
      const envelope = decisionEnvelopes[legId];
      if (envelope && microMicroResolved && liveBid && liveAsk && liveBid < liveAsk) {
        const conditionedExpectedFutureLow = cent(beliefs[legId]?.predicted_cents);
        const phaseCentralEstimate = beliefs[legId]?.phase_conditioning?.phase_central_estimate ?? null;
        const causalSeenLow = cent(beliefs[legId]?.own_evidence?.observed_low_cents);
        const upperQuantileOffset = finite(phaseCentralEstimate?.q75_cents);
        const upperQuantileRaw = Number.isInteger(causalSeenLow) && Number.isFinite(upperQuantileOffset)
          ? causalSeenLow + Math.round(upperQuantileOffset)
          : null;
        const lawfulEnvelopeHigh = Math.min(envelope.high_cents, liveAsk - 1);
        const lawfulEnvelopeExists = envelope.low_cents <= lawfulEnvelopeHigh;
        const upperQuantileTarget = Number.isInteger(upperQuantileRaw) && lawfulEnvelopeExists
          ? clamp(upperQuantileRaw, envelope.low_cents, lawfulEnvelopeHigh)
          : null;
        // F-VS-130: coherent belief pricing must account for executable prints
        // inside the displayed spread. The already-built conditioned population's
        // upper quantile names that cent. The live bid remains evidence in the
        // sentence, but it never anchors a coherent-envelope placement.
        const distributionPricedTarget = upperQuantileTarget;
        // F-VS-114(c): a newly migrated envelope re-derives the standing rest
        // on this same receipt, in either direction.  A stale active target may
        // never veto the current belief-priced target.
        targets[legId] = Number.isInteger(distributionPricedTarget) ? distributionPricedTarget : null;
        lowerBounds[legId] = envelope.low_cents;
        const activeInconsistent = Number.isInteger(active) && (active < envelope.low_cents || active > envelope.high_cents);
        envelopePlacement[legId] = {
          mode: "CONDITIONED_DISTRIBUTION_FLOOR_SIDE_INSIDE_COHERENT_ENVELOPE",
          live_bid_cents: liveBid,
          live_ask_cents: liveAsk,
          coherence_exists_at_receipt: true,
          lawful_envelope_high_cents: lawfulEnvelopeHigh,
          lawful_envelope_exists: lawfulEnvelopeExists,
          conditioned_expected_future_low_cents: conditionedExpectedFutureLow,
          future_low_minus_seen_low_distribution_cents: beliefs[legId]?.phase_conditioning?.future_low_minus_seen_low_distribution_cents ?? null,
          expected_future_low_minus_seen_low_cents: beliefs[legId]?.phase_conditioning?.expected_future_low_minus_seen_low_cents ?? null,
          placement_quantile: "Q75",
          placement_quantile_reason: "UPPER_CONDITIONED_FUTURE_LOW_QUANTILE_CAPTURES_INSIDE_SPREAD_REACH_WITHOUT_TOUCH_ANCHORING",
          placement_population_members: phaseCentralEstimate?.members ?? null,
          placement_population_cell: phaseCentralEstimate?.phase_band ?? null,
          placement_population_source_sha256: phaseCentralEstimate?.surface_sha256 ?? null,
          causal_seen_low_cents: causalSeenLow,
          selected_quantile_offset_cents: upperQuantileOffset,
          selected_quantile_raw_cents: upperQuantileRaw,
          selected_quantile_inside_envelope_cents: upperQuantileTarget,
          conditioned_q50_reference_cents: conditionedExpectedFutureLow,
          live_bid_reference_only_cents: liveBid,
          touch_anchored_inside_coherent_envelope: false,
          chosen_candidate_rule: Number.isInteger(upperQuantileTarget) ? "CONDITIONED_POPULATION_Q75_INSIDE_COHERENT_ENVELOPE" : "NO_LAWFUL_CONDITIONED_Q75_INSIDE_ENVELOPE",
          chosen_before_migration_discipline_cents: distributionPricedTarget,
          active_target_before_cents: active,
          chosen_target_cents: targets[legId],
          envelope_migration: envelopeMigrations[legId] ?? { migrated: false, from: envelope, to: envelope, receipt: state.receipt, provenance: LAYER_PROVENANCE.envelope_migration_fix },
          active_inconsistent_with_current_envelope: activeInconsistent,
          inconsistent_active_preallocation_resolution: !activeInconsistent
            ? "NOT_INCONSISTENT"
            : Number.isInteger(targets[legId]) && targets[legId] >= envelope.low_cents && targets[legId] <= envelope.high_cents
              ? "REDERIVED_INSIDE_CURRENT_ENVELOPE"
              : "CANCEL_REQUIRED_FAIL_LOUD",
          placement_provenance: LAYER_PROVENANCE.envelope_floor_side_fix,
          coherence_placement_provenance: LAYER_PROVENANCE.coherence_placement_fix,
          numeric_constant_added: false,
        };
      } else {
        targets[legId] = active;
        lowerBounds[legId] = envelope?.low_cents ?? 1;
        envelopePlacement[legId] = { mode: "HOLD_PREVIOUSLY_LICENSED_ENVELOPE_TARGET", coherence_exists_at_receipt: true, chosen_target_cents: active, numeric_constant_added: false };
      }
    } else if (coherence.status === "DISAGREES") {
      // A disagreement is evidence that the pair read has not resolved, not a
      // separate trading state. No lane may originate or reprice a rest here.
      // A previously licensed rest may hold while the pair re-derives.
      targets[legId] = active;
      lowerBounds[legId] = active ?? 1;
      envelopePlacement[legId] = {
        mode: "DISAGREES_HOLD_OR_REDERIVE_NO_PLACEMENT",
        coherence_exists_at_receipt: false,
        coherence_status_at_receipt: coherence.status,
        live_bid_cents: liveBid,
        live_ask_cents: liveAsk,
        book_receipt: book?.receipt ?? null,
        chosen_target_cents: targets[legId],
        may_originate_rest: false,
        may_reprice_rest: false,
        data_consumed_for_placement: false,
        provenance: [LAYER_PROVENANCE.disagrees_not_trading_state, LAYER_PROVENANCE.pair_coherence],
        numeric_constant_added: false,
      };
    } else if (decisionEnvelopes[legId]) {
      // F-VS-134/135: an examined carried conviction may originate or reprice.
      // It is read from a prior receipt, its eliminations are rechecked, and its
      // book basis is re-stated now. The same conditioned Q75 geometry remains
      // authoritative; touch is still subordinate.
      const envelope = decisionEnvelopes[legId];
      const phaseCentralEstimate = beliefs[legId]?.phase_conditioning?.phase_central_estimate ?? null;
      const causalSeenLow = cent(beliefs[legId]?.own_evidence?.observed_low_cents);
      const upperQuantileOffset = finite(phaseCentralEstimate?.q75_cents);
      const upperQuantileRaw = Number.isInteger(causalSeenLow) && Number.isFinite(upperQuantileOffset) ? causalSeenLow + Math.round(upperQuantileOffset) : null;
      const lawfulEnvelopeHigh = liveAsk ? Math.min(envelope.high_cents, liveAsk - 1) : null;
      const lawfulEnvelopeExists = Number.isInteger(lawfulEnvelopeHigh) && envelope.low_cents <= lawfulEnvelopeHigh;
      const carriedTarget = Number.isInteger(upperQuantileRaw) && lawfulEnvelopeExists ? clamp(upperQuantileRaw, envelope.low_cents, lawfulEnvelopeHigh) : active;
      targets[legId] = carriedTarget;
      lowerBounds[legId] = envelope.low_cents;
      envelopePlacement[legId] = {
        mode: "CARRIED_PRIOR_RECEIPT_CONVICTION_Q75_BASIS_RESTATED",
        coherence_exists_at_receipt: false,
        coherence_status_at_receipt: coherence.status,
        prior_envelope: priorEnvelopes[legId] ?? null,
        effective_envelope: envelope,
        live_bid_cents: liveBid,
        live_ask_cents: liveAsk,
        book_receipt: book?.receipt ?? null,
        chosen_target_cents: targets[legId],
        placement_quantile: "Q75",
        selected_quantile_offset_cents: upperQuantileOffset,
        selected_quantile_raw_cents: upperQuantileRaw,
        lawful_envelope_high_cents: lawfulEnvelopeHigh,
        lawful_envelope_exists: lawfulEnvelopeExists,
        may_originate_rest: true,
        may_reprice_rest: true,
        touch_lane_subordinated: true,
        prior_receipt_genuinely_readable: convictionEvolution[legId].prior_receipt_genuinely_readable,
        basis_re_stated_at_current_receipt: convictionEvolution[legId].basis_re_stated_at_current_receipt,
        eliminations_still_hold: convictionEvolution[legId].eliminations_still_hold,
        movement_statement: convictionEvolution[legId].movement_statement,
        provenance: [LAYER_PROVENANCE.carried_conviction, LAYER_PROVENANCE.touch_subordination_fix, LAYER_PROVENANCE.inside_spread_reach_fix],
        numeric_constant_added: false,
      };
    } else {
      // F-VS-068/F-VS-125 remains lawful only when no belief envelope exists and
      // the pair is not in DISAGREES. The current live book is evidence in sight,
      // subject to the unchanged pair-conservation allocator.
      targets[legId] = liveBid && liveAsk && liveBid < liveAsk ? liveBid : active;
      lowerBounds[legId] = targets[legId] ?? 1;
      envelopePlacement[legId] = { mode: "CONSUME_OWN_EVIDENCED_LIVE_TOUCH_WHILE_ENVELOPE_NULL", live_bid_cents: liveBid, live_ask_cents: liveAsk, book_receipt: book?.receipt ?? null, chosen_target_cents: targets[legId], may_originate_rest: true, data_consumed: Boolean(liveBid && liveAsk && liveBid < liveAsk && book?.receipt), provenance: [LAYER_PROVENANCE.consume_live_touch_fix, LAYER_PROVENANCE.own_evidence_sufficiency], numeric_constant_added: false };
    }
    const formationComplete = Number.isFinite(reads.anchor_settle.value.formation_progress[legId]) && reads.anchor_settle.value.formation_progress[legId] >= 1;
    if (!formationComplete || (liveBid && liveAsk && liveBid >= liveAsk)) targets[legId] = null;
  }
  let allocation = { lawful: true, targets: { ...targets }, reason: beliefMode ? "ONE_OPEN_SIDE_OR_LIVE_TOUCH" : "OWN_EVIDENCED_LIVE_TOUCH_MIND_ONLY", excess_cents: 0 };
  if (openIds.length === 2 && openIds.every((id) => cent(targets[id]))) allocation = allocateUnderPar(targets, lowerBounds);
  const creditedId = state.leg_ids.find((id) => reads.half_pair_state.value.legs[id].credited);
  if (creditedId && openIds.length === 1) {
    const openId = openIds[0], cap = base.PAR_BUDGET_CENTS - reads.half_pair_state.value.legs[creditedId].entry_cents;
    allocation.targets[openId] = cent(allocation.targets[openId]) ? Math.min(allocation.targets[openId], cap) : null;
    allocation.reason = `${allocation.reason}+FILL_HANDOFF_PAIR_CAP`;
  }
  if (!allocation.lawful) {
    const failedAllocation = allocation;
    const atomicTargets = {};
    const noLawfulReplacementLegs = [];
    for (const legId of openIds) {
      const active = cent(reads.half_pair_state.value.legs[legId].standing_target_cents);
      const envelope = decisionEnvelopes[legId] ?? null;
      const ask = cent(reads.books.value[legId]?.ask_cents);
      const activeStillLawful = Number.isInteger(active)
        && envelope
        && active >= envelope.low_cents
        && active <= envelope.high_cents
        && Number.isInteger(ask)
        && active < ask;
      atomicTargets[legId] = activeStillLawful ? active : null;
      if (Number.isInteger(active) && !activeStillLawful) noLawfulReplacementLegs.push(legId);
    }
    const held = Object.values(atomicTargets).filter(Number.isInteger);
    if (held.length === 2 && sum(held) > base.PAR_BUDGET_CENTS) {
      for (const legId of openIds) atomicTargets[legId] = null;
      noLawfulReplacementLegs.splice(0, noLawfulReplacementLegs.length, ...openIds);
    }
    allocation = {
      lawful: true,
      targets: atomicTargets,
      reason: "ATOMIC_REPLACEMENT_UNAVAILABLE_FAIL_LOUD_INCONSISTENT_ONLY",
      excess_cents: failedAllocation.excess_cents,
      replacement_unavailable: true,
      rejected_candidate_targets: failedAllocation.targets,
      rejected_reason: failedAllocation.reason,
      no_lawful_replacement_legs: [...new Set(noLawfulReplacementLegs)],
      provenance: LAYER_PROVENANCE.atomic_cancel_replace_fix,
    };
  }

  const dualPlain = openIds.length === 2 && openIds.every((id) => beliefs[id]?.plain_sentence)
    ? openIds.map((id) => beliefs[id].plain_sentence)
    : [];
  const results = [];
  for (const legId of openIds) {
    const row = baseRows.get(legId);
    const active = cent(reads.half_pair_state.value.legs[legId].standing_target_cents);
    const target = cent(allocation.targets[legId]);
    const currentEnvelope = decisionEnvelopes[legId] ?? null;
    const envelopeAuthoritativeAtReceipt = [
      "CONDITIONED_DISTRIBUTION_FLOOR_SIDE_INSIDE_COHERENT_ENVELOPE",
      "CARRIED_PRIOR_RECEIPT_CONVICTION_Q75_BASIS_RESTATED",
    ].includes(envelopePlacement[legId]?.mode);
    const activeInconsistent = envelopeAuthoritativeAtReceipt && Number.isInteger(active) && currentEnvelope && (active < currentEnvelope.low_cents || active > currentEnvelope.high_cents);
    const atomicNoReplacement = allocation.replacement_unavailable === true && allocation.no_lawful_replacement_legs?.includes(legId);
    const envelopeNoReplacement = Boolean(activeInconsistent && envelopePlacement[legId]?.lawful_envelope_exists === false);
    const noLawfulReplacement = atomicNoReplacement || envelopeNoReplacement;
    const pendingRearmBefore = state.dual_belief.rearm_by_leg[legId] ?? null;
    const reason = noLawfulReplacement
      ? "FAIL_LOUD_NO_LAWFUL_ATOMIC_REPLACEMENT"
      : pendingRearmBefore && Number.isInteger(target)
        ? "ATOMIC_REARM_LAWFUL_REPLACEMENT"
        : coherentNow
          ? "LAYERED_COHERENT_ENVELOPE_Q75_INSIDE_SPREAD_REACH"
          : coherence.status === "DISAGREES"
            ? "DISAGREES_HOLD_OR_REDERIVE_NO_PLACEMENT"
            : decisionEnvelopes[legId]
              ? "CARRIED_CONVICTION_Q75_BASIS_RESTATED_SURVIVORS_HOLD"
              : "OWN_EVIDENCED_LIVE_TOUCH_ENVELOPE_NULL";
    const action = actionForTarget(active, target, reason);
    const targetInsideCurrentEnvelope = Number.isInteger(target) && currentEnvelope && target >= currentEnvelope.low_cents && target <= currentEnvelope.high_cents;
    if (coherentNow && Number.isInteger(target) && !state.dual_belief.first_lawful_coherence_by_leg[legId]) {
      state.dual_belief.first_lawful_coherence_by_leg[legId] = { epoch: state.current_epoch, receipt: state.receipt };
    }
    const firstLawfulCoherence = state.dual_belief.first_lawful_coherence_by_leg[legId] ?? null;
    const placementAtCurrentCoherence = coherentNow && Number.isInteger(target) && ["PLACE_REST", "REPRICE_REST", "HOLD_REST"].includes(action.action);
    const carriedPlacement = envelopePlacement[legId]?.mode === "CARRIED_PRIOR_RECEIPT_CONVICTION_Q75_BASIS_RESTATED" && ["PLACE_REST", "REPRICE_REST"].includes(action.action);
    const envelopeConsistency = {
      active_inconsistent_before_action: Boolean(activeInconsistent),
      resolution: !activeInconsistent ? "NOT_REQUIRED" : targetInsideCurrentEnvelope ? "CANCEL_AND_REPLACE_ATOMIC_SAME_RECEIPT" : action.action === "CANCEL_REST" ? "FAIL_LOUD_NO_LAWFUL_REPLACEMENT" : "VIOLATION_STALE_REST_SURVIVED",
      resolved_same_receipt: !activeInconsistent || targetInsideCurrentEnvelope || action.action === "CANCEL_REST",
      cancel_and_replace_atomic: Boolean(activeInconsistent && targetInsideCurrentEnvelope && action.action === "REPRICE_REST"),
      fail_loud_only_without_lawful_replacement: !activeInconsistent || targetInsideCurrentEnvelope || (action.action === "CANCEL_REST" && noLawfulReplacement),
      no_lawful_replacement_reason: atomicNoReplacement ? "PAIR_ALLOCATION_INFEASIBLE_INSIDE_ENVELOPES" : envelopeNoReplacement ? "ENVELOPE_POINT_AT_OR_ABOVE_LIVE_ASK" : null,
      current_envelope: currentEnvelope,
      envelope_authoritative_at_receipt: envelopeAuthoritativeAtReceipt,
      provenance: [LAYER_PROVENANCE.envelope_migration_fix, LAYER_PROVENANCE.atomic_cancel_replace_fix],
    };
    const coherencePlacement = {
      current_coherence: coherentNow,
      lawful_target_after_pair_allocation_cents: target,
      first_lawful_coherence_epoch: firstLawfulCoherence?.epoch ?? null,
      first_lawful_coherence_receipt: firstLawfulCoherence?.receipt ?? null,
      action_at_receipt: action.action,
      placement_or_replacement_same_receipt: !coherentNow || !Number.isInteger(target) || placementAtCurrentCoherence,
      qualification_to_action_latency_seconds: placementAtCurrentCoherence ? state.current_epoch - (firstLawfulCoherence?.epoch ?? state.current_epoch) : null,
      stale_envelope_originated_new_rest: false,
      carried_conviction_originated_or_repriced_rest: carriedPlacement,
      carried_conviction_basis_re_stated: carriedPlacement ? convictionEvolution[legId].basis_re_stated_at_current_receipt : null,
      carried_conviction_prior_receipt: carriedPlacement ? convictionEvolution[legId].prior_conviction_receipt : null,
      live_touch_originated_new_rest: !coherentNow && !Number.isInteger(active) && action.action === "PLACE_REST" && String(envelopePlacement[legId]?.mode ?? "").startsWith("CONSUME_OWN_EVIDENCED_LIVE_TOUCH"),
      provenance: [LAYER_PROVENANCE.coherence_placement_fix, LAYER_PROVENANCE.carried_conviction],
    };
    let rearmReceipt;
    if (action.action === "CANCEL_REST" && noLawfulReplacement) {
      const prior = pendingRearmBefore;
      rearmReceipt = {
        status: "REARM_PENDING",
        armed_at_epoch: prior?.armed_at_epoch ?? state.current_epoch,
        armed_at_receipt: prior?.armed_at_receipt ?? state.receipt,
        latest_attempt_epoch: state.current_epoch,
        latest_attempt_receipt: state.receipt,
        attempts: (prior?.attempts ?? 0) + 1,
        trigger: noLawfulReplacement ? envelopeConsistency.no_lawful_replacement_reason : "NO_LAWFUL_REPLACEMENT",
        permanent_silence_allowed: false,
        provenance: LAYER_PROVENANCE.atomic_rearm_fix,
      };
      state.dual_belief.rearm_by_leg[legId] = rearmReceipt;
    } else if (pendingRearmBefore && Number.isInteger(target) && ["PLACE_REST", "REPRICE_REST", "HOLD_REST"].includes(action.action)) {
      rearmReceipt = {
        ...pendingRearmBefore,
        status: "REARM_RESOLVED_WITH_LAWFUL_REST",
        resolved_at_epoch: state.current_epoch,
        resolved_at_receipt: state.receipt,
        replacement_target_cents: target,
        attempts: (pendingRearmBefore.attempts ?? 0) + 1,
        permanent_silence_allowed: false,
        provenance: LAYER_PROVENANCE.atomic_rearm_fix,
      };
      delete state.dual_belief.rearm_by_leg[legId];
    } else if (pendingRearmBefore) {
      rearmReceipt = {
        ...pendingRearmBefore,
        status: "REARM_PENDING",
        latest_attempt_epoch: state.current_epoch,
        latest_attempt_receipt: state.receipt,
        attempts: (pendingRearmBefore.attempts ?? 0) + 1,
        permanent_silence_allowed: false,
        provenance: LAYER_PROVENANCE.atomic_rearm_fix,
      };
      state.dual_belief.rearm_by_leg[legId] = rearmReceipt;
    } else {
      rearmReceipt = { status: "NOT_REQUIRED", attempts: 0, permanent_silence_allowed: false, provenance: LAYER_PROVENANCE.atomic_rearm_fix };
    }
    const actionStatement = `ACTION=${action.action}; TARGET_CENTS=${action.target_cents ?? "NONE"}; ACTIVE_TARGET_BEFORE_CENTS=${active ?? "NONE"}.`;
    const upstream = `MACRO=${macroStatus}[${macroReceipt.receipt_id}] · MICRO=${microStatus}[${microReceipt.receipt_id}] · MICRO_MICRO=${microMicroStatus}[${microMicroReceipt.receipt_id}]`;
    const beliefText = dualPlain.length ? `${dualPlain[0]} || SIBLING-INVERSE: ${dualPlain[1]}` : "DUAL_BELIEF=INSUFFICIENT_EVIDENCE";
    const fillHandoffId = baseRows.get(legId).derivation.fill_handoff_receipt_id;
    const fillHandoff = fillHandoffId ? baseRows.get(legId).citation_receipts[fillHandoffId] : null;
    const fillHandoffText = fillHandoff
      ? ` FILL_HANDOFF=${fillHandoff.context.original_fill_receipt}[${fillHandoff.receipt_id}]; CREDITED_SIBLING_ENTRY=${fillHandoff.context.credited_sibling_entry_cents}; REPOSED_QUERY=${fillHandoff.context.reposed_query_fingerprint_sha256}.`
      : "";
    const sentence = `${beliefText}. MACRO: family=${macroFamilies[legId].family}, SURVIVOR_SHAPES=${JSON.stringify(survivorUpdate.legs[legId])}, conditioned-total-dip=${JSON.stringify(conditionedPriors[legId]?.conditioned_total_dip_distribution_cents ?? null)}, arrived-dip=${JSON.stringify(conditionedPriors[legId]?.arrived_dip_distribution_cents ?? null)}, remaining-dip=total-minus-arrived=${JSON.stringify(conditionedPriors[legId]?.remaining_dip_distribution_cents ?? null)}, conditioning-method=${conditionedPriors[legId]?.method ?? "NONE"}, stores=${coarseNeighbors.map((neighbor) => `${neighbor.quality}/${neighbor.grain ?? "UNKNOWN"}@${neighbor.citation_receipt_id}`).join(",") || "NONE"} [${macroReceipt.receipt_id}]. MICRO: own-window=${JSON.stringify(beliefs[legId]?.own_evidence ?? null)}, rows=${[beliefs[legId]?.book_receipt, beliefs[legId]?.top_neighbor?.citation_receipt_id].filter(Boolean).join(",") || "NONE"}, V3_KEY=${LAYER_PROVENANCE.v3_source_key}->${LAYER_PROVENANCE.v3_runtime_rekey} [${microReceipt.receipt_id}]. MICRO-MICRO: tick=${state.receipt}, book=${beliefs[legId]?.book_receipt ?? "NONE"}, store=${LAYER_PROVENANCE.micro_micro_store} [${microMicroReceipt.receipt_id}]. ORDER=${upstream}. COHERENCE=${coherence.status}; MIRROR_GAP=${coherence.absolute_mirror_gap_cents ?? "UNKNOWN"}; SPREAD_BOUND=${spread ?? "UNKNOWN"}/${SPREAD_SETTLE_COHERENCE_MAX_CENTS}; CONVICTION_EVOLUTION=${JSON.stringify(convictionEvolution[legId])}; ENVELOPE=${JSON.stringify(currentEnvelope)}; ENVELOPE_PLACEMENT=${JSON.stringify(envelopePlacement[legId])}; ALLOCATION=${allocation.reason}.${fillHandoffText} ${actionStatement}`;
    row.citation_receipts[macroReceipt.receipt_id] = macroReceipt;
    row.citation_receipts[microReceipt.receipt_id] = microReceipt;
    row.citation_receipts[microMicroReceipt.receipt_id] = microMicroReceipt;
    row.action = action;
    row.sentence = sentence;
    row.sentence_action_assertion = { hard_assert: true, expected_statement: actionStatement, equal: sentence.includes(actionStatement) };
    row.citation_receipt_assertion = { hard_assert: true, receipt_count: Object.keys(row.citation_receipts).length, equal: [macroReceipt, microReceipt, microMicroReceipt].every((receipt) => sentence.includes(receipt.receipt_id)) };
    row.layered_dual_belief = { macro: { status: macroStatus, families: macroFamilies, survivor_shapes: survivorUpdate, conditioned_priors: conditionedPriors, receipt_id: macroReceipt.receipt_id }, micro: { status: microStatus, beliefs, receipt_id: microReceipt.receipt_id }, micro_micro: { status: microMicroStatus, receipt_id: microMicroReceipt.receipt_id }, coherence, belief_mode: beliefMode, conviction_evolution: convictionEvolution[legId], carried_conviction_consumed_for_action: ["PLACE_REST", "REPRICE_REST"].includes(action.action) && convictionEvolution[legId].prior_receipt_genuinely_readable, independent_lane_may_complete: true, independent_lane_license: [LAYER_PROVENANCE.consume_live_touch_fix, LAYER_PROVENANCE.own_evidence_sufficiency], first_coherence: state.dual_belief.first_coherence, envelope_history_count: state.dual_belief.envelope_history.length, envelope_migration_at_receipt: envelopeMigrations[legId] ?? null, envelope_consistency: envelopeConsistency, coherence_placement: coherencePlacement, atomic_rearm: rearmReceipt, envelope: currentEnvelope, envelope_placement: envelopePlacement[legId], v3_keying_fix: beliefs[legId]?.v3_map_semantics ?? null };
    delete row.derivation.stale_prior_path_used;
    row.derivation.carried_conviction = convictionEvolution[legId];
    row.derivation.target_basis = reason;
    row.derivation.derived_target_cents = target;
    row.derivation.allocation = allocation;
    const siblingLegId = state.leg_ids.find((id) => id !== legId);
    const siblingPlan = creditedId
      ? cent(reads.half_pair_state.value.legs[creditedId].entry_cents)
      : cent(allocation.targets[siblingLegId]);
    const jointSum = target && siblingPlan ? target + siblingPlan : null;
    row.pair_conservation = { sibling_leg_id: siblingLegId, sibling_commitment_cents: siblingPlan, evaluated_target_cents: target, sum_cents: jointSum, at_or_below_99: !Number.isInteger(jointSum) || jointSum <= base.PAR_BUDGET_CENTS };
    results.push(row);
  }
  for (const id of state.leg_ids.filter((legId) => !openIds.includes(legId))) {
    delete nextEnvelopes[id];
    delete nextConvictions[id];
  }
  state.dual_belief.current_envelopes = Object.keys(nextEnvelopes).length ? nextEnvelopes : null;
  state.dual_belief.carried_convictions = nextConvictions;
  const evolutionSignature = JSON.stringify(Object.fromEntries(openIds.map((id) => [id, { update: convictionEvolution[id].update, effective: convictionEvolution[id].effective_envelope, survivors: convictionEvolution[id].surviving_shape_ids_now }])));
  if (state.dual_belief.conviction_history.at(-1)?.signature !== evolutionSignature) state.dual_belief.conviction_history.push({ timestamp_epoch: state.current_epoch, receipt: state.receipt, signature: evolutionSignature, evolution: convictionEvolution });
  return { derivations: results, layers: { macro: macroReceipt, micro: microReceipt, micro_micro: microMicroReceipt }, coherence, survivor_shapes: survivorUpdate, conviction_evolution: convictionEvolution };
}

module.exports = {
  ...base,
  CONTRACT_SUM_CENTS,
  SPREAD_SETTLE_COHERENCE_MAX_CENTS,
  LAYER_PROVENANCE,
  PHASE_CENTRAL_BANDS,
  configurePhaseCentralSurface,
  configureSurvivorShapeLibraries: survivorShapes.configureSurvivorShapeLibraries,
  deriveJointActions,
};
