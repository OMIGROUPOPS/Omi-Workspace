"use strict";

// V54 layered dual-belief policy. The inherited V54 readers/retrieval remain the
// data plane. This module adds one joint, ordered derivation and never imports
// the ex-post DUAL_BELIEF_FORENSICS result.

const base = require("./window1_v54_functionable_os.js");

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
});

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

// F-VS-114(b): remaining dip is conditioned total travel minus the travel that
// has already arrived at this receipt.  The old implementation subtracted the
// arrived share and therefore made the claimed remaining dip grow toward the
// bell.  Only members with a lawful floor-time observation can participate in
// this arithmetic.  All quantiles below use that one row universe so the raw
// summary and placement input cannot silently disagree (F-VS-114(c)).
function conditionTravelPrior(baseRow) {
  const neighborLeg = baseRow?.derivation?.neighbor_leg ?? {};
  const own = neighborLeg.own_evidence ?? {};
  const ownFraction = finite(own.window_fraction);
  const rows = (neighborLeg.rows ?? []).flatMap((row) => {
    const fullTravel = finite(row.remaining_dip_cents);
    const memberFloorFraction = finite(row.member_floor_fraction);
    const conditioningWeight = finite(row.weight);
    if (!(Number.isFinite(ownFraction) && Number.isFinite(fullTravel) && Number.isFinite(memberFloorFraction) && memberFloorFraction > 0 && Number.isFinite(conditioningWeight) && conditioningWeight > 0)) return [];
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
  return {
    status: rows.length ? "RESOLVED" : "INSUFFICIENT_EVIDENCE",
    method: "REMAINING_DIP_EQUALS_CONDITIONED_TOTAL_MINUS_ARRIVED; ARRIVED_EQUALS_TOTAL_X_CLAMP(OWN_WINDOW_FRACTION_DIV_MEMBER_FLOOR_FRACTION,0,1); OWN_TAPE_CONDITIONED_MEMBER_WEIGHTS",
    upstream_all_member_distribution_reference_cents: neighborLeg.conditional_remaining_dip_distribution_cents ?? {},
    conditioned_total_dip_distribution_cents: distribution("conditioned_total_dip_cents"),
    arrived_dip_distribution_cents: distribution("arrived_dip_cents"),
    remaining_dip_distribution_cents: distribution("remaining_dip_cents"),
    row_universe: {
      source_rows: sourceRows.length,
      floor_timed_rows: rows.length,
      excluded_untimed_rows: excludedUntimedRows,
      one_universe_for_total_arrived_and_remaining_quantiles: true,
    },
    own_evidence: own,
    target_floor_fraction: Number.isFinite(targetFloorFraction) ? targetFloorFraction : null,
    rows,
    provenance: [LAYER_PROVENANCE.remaining_dip_inversion_fix, LAYER_PROVENANCE.phase_conditioning_fix, LAYER_PROVENANCE.conditioning],
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
  const predicted = cent(own.observed_low_cents) && Number.isInteger(conditioned.q50)
    ? Math.max(1, own.observed_low_cents - conditioned.q50)
    : null;
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
    ? `believes ${legId} at ${beliefPrice}¢ [${beliefPriceBasis}; bid=${liveBid}¢; ask=${liveAsk}¢; book-receipt=${bookReceipt}] at ${minutesToBell ?? "UNKNOWN"}min-to-bell with ${volume ?? "UNKNOWN"} vol_log1p in ${state.category}, using ${store} + ${neighborName}, SHOULD drift to ${predicted}¢ by ${byMinutes ?? "UNKNOWN"}min-to-bell [deadline-epoch=${deadline?.deadline_epoch ?? "UNKNOWN"}; deadline-emitted-now=${deadline?.emitted_at_epoch ?? "UNKNOWN"}; deadline-receipt=${deadline?.emitted_at_receipt ?? "UNKNOWN"}]`
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
  if (!state.dual_belief) state.dual_belief = { first_coherence: null, current_envelopes: null, coherence_history: [], envelope_history: [] };
  const openIds = state.leg_ids.filter((id) => !reads.half_pair_state.value.legs[id].credited);
  const baseRows = new Map();
  for (const legId of openIds) {
    baseRows.set(legId, base.deriveAction({ state, reads, neighborhood, legId, lineage: lineageByLeg[legId], resources }));
  }
  const allFormationComplete = state.leg_ids.every((id) => Number.isFinite(reads.anchor_settle.value.formation_progress[id]) && reads.anchor_settle.value.formation_progress[id] >= 1);
  const coarseNeighbors = neighborhood.filter((row) => ["FOUNDATION_MINUTE_BELL_BOUNDED", "RANGE_BELL_BOUNDED", "HISTORICAL_BELL_BOUNDED"].includes(row.quality));
  const macroFamilies = Object.fromEntries(state.leg_ids.map((id) => [id, interimFamily(reads, id)]));
  const conditionedPriors = Object.fromEntries(openIds.map((id) => [id, conditionTravelPrior(baseRows.get(id))]));
  const macroResolved = allFormationComplete && coarseNeighbors.length > 0 && openIds.every((id) => {
    const q50 = conditionedPriors[id]?.remaining_dip_distribution_cents?.q50;
    return Number.isInteger(q50);
  });
  const macroStatus = macroResolved ? "RESOLVED" : "INSUFFICIENT_EVIDENCE";
  const macroReceipt = layerReceipt(state, "MACRO", macroStatus, coarseNeighbors.flatMap((row) => [row.citation_receipt_id, ...(row.source_receipts ?? []).map((source) => source.row_ref)]), {
    families: macroFamilies,
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
  state.dual_belief.coherence_history.push(coherence);
  const envelopeMigrations = {};
  if (coherentNow) {
    const envelopes = Object.fromEntries(openIds.map((id) => [id, { low_cents: beliefs[id].predicted_cents, high_cents: beliefs[id].envelope_high_cents, belief_receipt: state.receipt }]));
    for (const id of openIds) {
      const prior = state.dual_belief.current_envelopes?.[id] ?? null;
      const current = envelopes[id];
      const migrated = Boolean(prior && (prior.low_cents !== current.low_cents || prior.high_cents !== current.high_cents));
      envelopeMigrations[id] = { migrated, from: prior, to: current, receipt: state.receipt, provenance: LAYER_PROVENANCE.envelope_migration_fix };
      if (migrated) state.dual_belief.envelope_history.push({ leg_id: id, ...envelopeMigrations[id] });
    }
    state.dual_belief.current_envelopes = envelopes;
    if (!state.dual_belief.first_coherence) state.dual_belief.first_coherence = { ...coherence, envelopes, beliefs: JSON.parse(JSON.stringify(beliefs)) };
  }

  const beliefMode = Boolean(state.dual_belief.current_envelopes);
  const targets = {};
  const lowerBounds = {};
  const envelopePlacement = {};
  for (const legId of openIds) {
    const book = reads.books.value[legId];
    const liveBid = cent(book?.bid_cents), liveAsk = cent(book?.ask_cents);
    const active = cent(reads.half_pair_state.value.legs[legId].standing_target_cents);
    if (beliefMode) {
      const envelope = state.dual_belief.current_envelopes[legId];
      if (envelope && microMicroResolved && liveBid && liveAsk && liveBid < liveAsk) {
        const conditionedQ50 = beliefs[legId]?.remaining_dip_cents?.q50;
        const floorSideRaw = Number.isInteger(conditionedQ50) ? liveAsk - conditionedQ50 : null;
        const floorSideTarget = Number.isInteger(floorSideRaw) ? clamp(floorSideRaw, envelope.low_cents, envelope.high_cents) : null;
        const bookGeometryTarget = clamp(liveBid, envelope.low_cents, envelope.high_cents);
        // F-VS-114(a): q50 names the floor-side point inside the containing
        // envelope.  The envelope's deep edge and the projected bid are audit
        // geometry, not alternative defaults.  With zero remaining dip the
        // evidenced bid is the lawful floor-side point.
        const distributionPricedTarget = Number.isInteger(conditionedQ50) && conditionedQ50 > 0 && Number.isInteger(floorSideTarget) && floorSideTarget < liveAsk
          ? floorSideTarget
          : (bookGeometryTarget < liveAsk ? bookGeometryTarget : null);
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
          conditioned_remaining_dip_q50_cents: conditionedQ50,
          floor_side_formula: "LIVE_ASK_CENTS_MINUS_CONDITIONED_REMAINING_DIP_Q50_CENTS",
          floor_side_raw_cents: floorSideRaw,
          floor_side_inside_envelope_cents: floorSideTarget,
          live_bid_projected_inside_envelope_cents: bookGeometryTarget,
          chosen_candidate_rule: conditionedQ50 > 0 ? "CONDITIONED_REMAINING_DIP_Q50_FLOOR_SIDE_ONLY" : "ZERO_REMAINING_DIP_USES_EVIDENCED_BID_INSIDE_ENVELOPE",
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
          numeric_constant_added: false,
        };
      } else {
        targets[legId] = active;
        lowerBounds[legId] = envelope?.low_cents ?? 1;
        envelopePlacement[legId] = { mode: "HOLD_PREVIOUSLY_LICENSED_ENVELOPE_TARGET", chosen_target_cents: active, numeric_constant_added: false };
      }
    } else {
      // F-VS-108 bed rule: an independent/no-opinion lane may hold an already
      // licensed coherent rest or abstain, but may not originate a completion.
      targets[legId] = active;
      lowerBounds[legId] = 1;
      envelopePlacement[legId] = { mode: "INDEPENDENT_LANE_HOLD_OR_ABSTAIN_BED", chosen_target_cents: targets[legId], may_originate_rest: false, numeric_constant_added: false };
    }
    const formationComplete = Number.isFinite(reads.anchor_settle.value.formation_progress[legId]) && reads.anchor_settle.value.formation_progress[legId] >= 1;
    if (!formationComplete || (liveBid && liveAsk && liveBid >= liveAsk)) targets[legId] = null;
  }
  let allocation = { lawful: true, targets: { ...targets }, reason: beliefMode ? "ONE_OPEN_SIDE_OR_LATCH_HOLD" : "INDEPENDENT_LANE_HOLD_OR_ABSTAIN_BED", excess_cents: 0 };
  if (openIds.length === 2 && openIds.every((id) => cent(targets[id]))) allocation = allocateUnderPar(targets, lowerBounds);
  const creditedId = state.leg_ids.find((id) => reads.half_pair_state.value.legs[id].credited);
  if (creditedId && openIds.length === 1) {
    const openId = openIds[0], cap = base.PAR_BUDGET_CENTS - reads.half_pair_state.value.legs[creditedId].entry_cents;
    allocation.targets[openId] = cent(allocation.targets[openId]) ? Math.min(allocation.targets[openId], cap) : null;
    allocation.reason = `${allocation.reason}+FILL_HANDOFF_PAIR_CAP`;
  }
  if (!allocation.lawful) {
    for (const legId of openIds) allocation.targets[legId] = null;
    allocation.reason = `${allocation.reason}+FAIL_LOUD_CANCEL_INCONSISTENT_RESTS`;
  }

  const dualPlain = openIds.length === 2 && openIds.every((id) => beliefs[id]?.plain_sentence)
    ? openIds.map((id) => beliefs[id].plain_sentence)
    : [];
  const results = [];
  for (const legId of openIds) {
    const row = baseRows.get(legId);
    const active = cent(reads.half_pair_state.value.legs[legId].standing_target_cents);
    const target = cent(allocation.targets[legId]);
    const reason = !allocation.lawful
      ? "FAIL_LOUD_COHERENT_ENVELOPES_CANNOT_SATISFY_PAR"
      : beliefMode ? (microMicroResolved ? "LAYERED_COHERENT_ENVELOPE" : "HOLD_LAST_LICENSED_COHERENT_ENVELOPE") : "INDEPENDENT_LANE_HOLD_OR_ABSTAIN_BED";
    const action = actionForTarget(active, target, reason);
    const currentEnvelope = state.dual_belief.current_envelopes?.[legId] ?? null;
    const activeInconsistent = Number.isInteger(active) && currentEnvelope && (active < currentEnvelope.low_cents || active > currentEnvelope.high_cents);
    const targetInsideCurrentEnvelope = Number.isInteger(target) && currentEnvelope && target >= currentEnvelope.low_cents && target <= currentEnvelope.high_cents;
    const envelopeConsistency = {
      active_inconsistent_before_action: Boolean(activeInconsistent),
      resolution: !activeInconsistent ? "NOT_REQUIRED" : targetInsideCurrentEnvelope ? "REDERIVED_INSIDE_CURRENT_ENVELOPE" : action.action === "CANCEL_REST" ? "CANCELLED_FAIL_LOUD_SAME_RECEIPT" : "VIOLATION_STALE_REST_SURVIVED",
      resolved_same_receipt: !activeInconsistent || targetInsideCurrentEnvelope || action.action === "CANCEL_REST",
      current_envelope: currentEnvelope,
      provenance: LAYER_PROVENANCE.envelope_migration_fix,
    };
    const actionStatement = `ACTION=${action.action}; TARGET_CENTS=${action.target_cents ?? "NONE"}; ACTIVE_TARGET_BEFORE_CENTS=${active ?? "NONE"}.`;
    const upstream = `MACRO=${macroStatus}[${macroReceipt.receipt_id}] · MICRO=${microStatus}[${microReceipt.receipt_id}] · MICRO_MICRO=${microMicroStatus}[${microMicroReceipt.receipt_id}]`;
    const beliefText = dualPlain.length ? `${dualPlain[0]} || SIBLING-INVERSE: ${dualPlain[1]}` : "DUAL_BELIEF=INSUFFICIENT_EVIDENCE";
    const fillHandoffId = baseRows.get(legId).derivation.fill_handoff_receipt_id;
    const fillHandoff = fillHandoffId ? baseRows.get(legId).citation_receipts[fillHandoffId] : null;
    const fillHandoffText = fillHandoff
      ? ` FILL_HANDOFF=${fillHandoff.context.original_fill_receipt}[${fillHandoff.receipt_id}]; CREDITED_SIBLING_ENTRY=${fillHandoff.context.credited_sibling_entry_cents}; REPOSED_QUERY=${fillHandoff.context.reposed_query_fingerprint_sha256}.`
      : "";
    const sentence = `${beliefText}. MACRO: family=${macroFamilies[legId].family}, conditioned-total-dip=${JSON.stringify(conditionedPriors[legId]?.conditioned_total_dip_distribution_cents ?? null)}, arrived-dip=${JSON.stringify(conditionedPriors[legId]?.arrived_dip_distribution_cents ?? null)}, remaining-dip=total-minus-arrived=${JSON.stringify(conditionedPriors[legId]?.remaining_dip_distribution_cents ?? null)}, conditioning-method=${conditionedPriors[legId]?.method ?? "NONE"}, stores=${coarseNeighbors.map((neighbor) => `${neighbor.quality}/${neighbor.grain ?? "UNKNOWN"}@${neighbor.citation_receipt_id}`).join(",") || "NONE"} [${macroReceipt.receipt_id}]. MICRO: own-window=${JSON.stringify(beliefs[legId]?.own_evidence ?? null)}, rows=${[beliefs[legId]?.book_receipt, beliefs[legId]?.top_neighbor?.citation_receipt_id].filter(Boolean).join(",") || "NONE"}, V3_KEY=${LAYER_PROVENANCE.v3_source_key}->${LAYER_PROVENANCE.v3_runtime_rekey} [${microReceipt.receipt_id}]. MICRO-MICRO: tick=${state.receipt}, book=${beliefs[legId]?.book_receipt ?? "NONE"}, store=${LAYER_PROVENANCE.micro_micro_store} [${microMicroReceipt.receipt_id}]. ORDER=${upstream}. COHERENCE=${coherence.status}; MIRROR_GAP=${coherence.absolute_mirror_gap_cents ?? "UNKNOWN"}; SPREAD_BOUND=${spread ?? "UNKNOWN"}/${SPREAD_SETTLE_COHERENCE_MAX_CENTS}; ENVELOPE=${JSON.stringify(state.dual_belief.current_envelopes?.[legId] ?? null)}; ENVELOPE_PLACEMENT=${JSON.stringify(envelopePlacement[legId])}; ALLOCATION=${allocation.reason}.${fillHandoffText} ${actionStatement}`;
    row.citation_receipts[macroReceipt.receipt_id] = macroReceipt;
    row.citation_receipts[microReceipt.receipt_id] = microReceipt;
    row.citation_receipts[microMicroReceipt.receipt_id] = microMicroReceipt;
    row.action = action;
    row.sentence = sentence;
    row.sentence_action_assertion = { hard_assert: true, expected_statement: actionStatement, equal: sentence.includes(actionStatement) };
    row.citation_receipt_assertion = { hard_assert: true, receipt_count: Object.keys(row.citation_receipts).length, equal: [macroReceipt, microReceipt, microMicroReceipt].every((receipt) => sentence.includes(receipt.receipt_id)) };
    row.layered_dual_belief = { macro: { status: macroStatus, families: macroFamilies, conditioned_priors: conditionedPriors, receipt_id: macroReceipt.receipt_id }, micro: { status: microStatus, beliefs, receipt_id: microReceipt.receipt_id }, micro_micro: { status: microMicroStatus, receipt_id: microMicroReceipt.receipt_id }, coherence, belief_mode: beliefMode, independent_lane_may_complete: false, first_coherence: state.dual_belief.first_coherence, envelope_history_count: state.dual_belief.envelope_history.length, envelope_migration_at_receipt: envelopeMigrations[legId] ?? null, envelope_consistency: envelopeConsistency, envelope: currentEnvelope, envelope_placement: envelopePlacement[legId], v3_keying_fix: beliefs[legId]?.v3_map_semantics ?? null };
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
  return { derivations: results, layers: { macro: macroReceipt, micro: microReceipt, micro_micro: microMicroReceipt }, coherence };
}

module.exports = {
  ...base,
  CONTRACT_SUM_CENTS,
  SPREAD_SETTLE_COHERENCE_MAX_CENTS,
  LAYER_PROVENANCE,
  deriveJointActions,
};
