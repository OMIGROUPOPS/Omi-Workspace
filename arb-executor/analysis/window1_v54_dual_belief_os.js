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
  v3_runtime_rekey: "NONE_LIBRARY_MEMBER_BOUNDED_CLOSE_CENTS_PRESERVED",
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
  traded_low_axis_alignment: "F-VS-139/F-VS-143@f4752720",
  floor_rest_protection: "F-VS-138/F-VS-142@f4752720; lock retirement F-VS-148..152@d079687f",
  singleton_envelope_consumption: "F-VS-150@d079687f",
  proposal_supervisor: "F-VS-149@d079687f",
  disagrees_own_evidence_release: "F-VS-138/F-VS-142@f4752720; F-VS-068@521a1613",
  continuous_belief_movement: "RIDER_BELIEF_EVOLVES@2026-08-24",
  own_evidence_sufficiency: "F-VS-068@521a1613",
  definition_repair_floor: "F-VS-159@6093141b; F-VS-163..170@e65fe458/44559ebc",
  definition_repair_low: "F-VS-164/F-VS-168/F-VS-169@44559ebc",
  definition_repair_headroom: "F-VS-160/F-VS-169@a2a6a25d/44559ebc",
  definition_repair_tenure: "F-VS-154/F-VS-155@6093141b",
  honest_gate_contract: "F-VS-163/F-VS-165/F-VS-166/F-VS-167/F-VS-170@e65fe458/44559ebc",
  same_receipt_floor_hold: "F-VS-185@12f25f37; CC@601207d0/12f25f37",
  postable_floor_rest_hold: "F-VS-183@12f25f37; singleton adjudication CC@601207d0",
  honest_floor_tenure: "F-VS-184@12f25f37; CC@601207d0/12f25f37",
  post_only_own_target: "F-VS-191@2941cd15; CC@d945bcdd/2941cd15",
  floor_capable_lane: "F-VS-190@2941cd15; CC@d945bcdd/2941cd15",
  definition_lock_rest_claim: "F-VS-192@2941cd15; CC@d945bcdd/2941cd15",
  technique_frame: "THE_TECHNIQUE_FRAME@36f04e25; TECHNIQUE_REGISTER@9ef05314",
  pricing_authority_restored: "DISPATCH_CONTRACTS_BUILD@2026-08-25",
  own_evidence_inside_author: "F-VS-216/F-VS-218@a6e84246; F-VS-066/F-VS-068",
  evidence_only_level_movement: "F-VS-217/F-VS-218@a6e84246; F-VS-134",
  directional_floor_tenure: "F-VS-217/F-VS-218@a6e84246",
  continuous_post_only: "F-VS-217@a6e84246",
  technique_contracts: "F-VS-193..198@9ef05314; DISPATCH_CONTRACTS_BUILD@2026-08-25",
  spread_eye: "REGISTERED_TECHNIQUE_SPREAD_EYE@2026-08-25",
});

const TECHNIQUE_CONTRACTS = Object.freeze([
  Object.freeze({ id: "C01_PRICING_AUTHORITY_OVER_LANE_LEVEL_SELECTION", state: "FIRED_OR_PRICED", senior: "PANEL_PRIOR_CONDITIONED_BY_CURRENT_GAME_OWN_EVIDENCE", junior: "ALL_PLACEMENT_LANES", resolution: "THE_AUTHOR_CONDITIONS_PRIOR_ON_TRADED_LOW_LIVE_BOOK_AND_SPREAD_CLEARING; LANES_MAY_NOT_SUBSTITUTE_A_LEVEL" }),
  Object.freeze({ id: "C02_FLOOR_TENURE_OVER_BELIEF_DRIFT", state: "FIRED_OR_PRICED", senior: "EXACT_EVIDENCED_OWN_TAPE_LEVEL_TENURE", junior: "COHERENT_OR_CARRIED_REPRICE", resolution: "BLOCK_MOVES_AWAY_FROM_AN_EXACT_EVIDENCED_LEVEL; NEVER_BLOCK_A_RECOMPUTE_ONTO_IT" }),
  Object.freeze({ id: "C03_POST_ONLY_OVER_ALL_NEW_AND_STANDING_ORDERS", state: "FIRED_OR_PRICED", senior: "REST_TARGET_LT_CAUSAL_LIVE_ASK_CONTINUOUSLY", junior: "EVERY_LANE_WRITER_AND_ACTIVE_REST", resolution: "VETO_EMISSION_ONLY; A_STANDING_REST_AT_OR_ABOVE_ASK_IS_CANCELLED_OR_REPLACED_BY_A_LAWFUL_AUTHORITY_LEVEL" }),
  Object.freeze({ id: "C04_CANCEL_REARM_RESTORES_PRICE", state: "FIRED_OR_PRICED", senior: "CURRENT_RECOMPUTED_AUTHORITY_PRICE", junior: "GENERIC_REARM_OR_STALE_PRICE", resolution: "REARM_AT_THE_CURRENT_AUTHORITY_PRICE_WHEN_LICENSED_POSTABLE_AND_PAIR_LAWFUL" }),
  Object.freeze({ id: "C05_LOCKED_BOOK_IS_PLACEMENT_ONLY", state: "FIRED_OR_PRICED", senior: "EXISTING_LAWFUL_REST", junior: "LOCKED_OR_CROSSED_BOOK_NEW_PLACEMENT_VETO", resolution: "NO_NEW_ORDER; NEVER_CANCEL_AN_EXISTING_REST" }),
  Object.freeze({ id: "C06_LANE_LANE_LEVEL_SELECTION", state: "FIRED_OR_PRICED", senior: "PRICING_AUTHORITY", junior: "COHERENT_DISAGREES_TOUCH_CARRIED_WRITERS", resolution: "ONE_ELIGIBLE_WRITER_EMITS_THE_AUTHORITY_PRICE" }),
  Object.freeze({ id: "C07_SAME_RECEIPT_FLOOR_HANDOFF", state: "RETIRED_BY_ONE_AUTHOR", senior: "PRICING_AUTHORITY", junior: "TRADED_LOW_AS_DIRECT_TARGET", resolution: "THE_PRINT_IS CONDITIONING EVIDENCE; IT NEVER AUTHORS THE ORDER PRICE" }),
  Object.freeze({ id: "C08_DEFINITION_LOCK_FLOOR", state: "FIRED_OR_PRICED", senior: "OBSERVED_TRUE_TRADE_LOW_PRODUCER", junior: "REST_LICENSE_OR_BELIEF", resolution: "RESTS_AND_BELIEFS_NEVER_PRODUCE_THE_FLOOR_FIELD" }),
  Object.freeze({ id: "C09_PAR_CONSERVATION_OVER_PRICE", state: "FIRED_OR_PRICED", senior: "PAIR_SUM_AT_OR_BELOW_99", junior: "PRICING_AUTHORITY", resolution: "VETO_AN_INFEASIBLE PLAN; NEVER REWRITE THE AUTHORITY PRICE" }),
  Object.freeze({ id: "C10_FILL_HANDOFF_OVER_OPEN_SIDE_BUDGET", state: "FIRED_OR_PRICED", senior: "CREDITED_SIBLING_ENTRY_CAP", junior: "OPEN_SIDE_AUTHORITY_TARGET", resolution: "VETO_AN INFEASIBLE OPEN-SIDE ORDER; NEVER CAP OR RESNAP ITS PRICE" }),
  Object.freeze({ id: "C11_ENVELOPE_HIGH_PROVENANCE", state: "FIRED_OR_PRICED", senior: "TRUE_TRADE_OR_CAUSAL_BOOK_BID", junior: "MID_OR_REPORTED_LAST_REFERENCE", resolution: "NO_FLOORED_MID_MAY NAME_AN_ENVELOPE_HIGH" }),
  Object.freeze({ id: "C12_ONE_DECISION_PER_LEG_RECEIPT", state: "FIRED_OR_PRICED", senior: "CONTRACT_RESOLVED_WRITER", junior: "ALL_OTHER_ELIGIBLE_WRITERS", resolution: "ONE_EMISSION_WITH_ALL_LOSERS_RECORDED" }),
  Object.freeze({ id: "C13_SAME_RECEIPT_FLOOR_OVER_LANE_PROPOSAL", state: "FIRED_OR_PRICED", senior: "CURRENT_RECEIPT_TRADED_FLOOR", junior: "CURRENT_LANE_PROPOSAL", resolution: "FLOOR_GOVERNS_WHEN_POSTABLE; CONSERVATION_REMAINS_SENIOR" }),
  Object.freeze({ id: "C14_SINGLE_TENURE_INSTRUMENT", state: "FIRED_OR_PRICED", senior: "ORDER_TRANSITION_TENURE_PRODUCER", junior: "SAMPLED_ROW_TENURE", resolution: "ONLY_TRANSITION_INTERVALS_SERIALIZE_TENURE" }),
  Object.freeze({ id: "C15_SPREAD_EYE_IS_EVIDENCE_ONLY", state: "FIRED_OR_PRICED", senior: "FLOORS_TENURE_POST_ONLY_AND_CONSERVATION", junior: "SPREAD_EYE", resolution: "EYE_MAY_STRENGTHEN_PRICING_AUTHORITY_BUT_NEVER_COMMAND_A_LANE" }),
  Object.freeze({ id: "L01_CARRIED_CONVICTION_VS_CURRENT_COHERENCE", state: "LATENT_REGISTERED", senior: "CURRENT_COHERENT_AUTHORITY_WHEN_RESOLVED", junior: "CARRIED_CONVICTION", resolution: "CARRY_ACTS_ONLY_WHEN_CURRENT_CHAIN_IS_UNRESOLVED_AND_SUPPORT_SURVIVES" }),
  Object.freeze({ id: "L02_HOLD_VS_ALLOCATOR_AFTER_SIBLING_RISE", state: "LATENT_REGISTERED", senior: "PAIR_CONSERVATION", junior: "TENURE_HOLD", resolution: "YIELD_ONLY_THE_MINIMUM_NEEDED_THEN_RESNAP; OTHERWISE_ABSTAIN" }),
  Object.freeze({ id: "L03_GATE_PROBES_VS_PRODUCTION", state: "LATENT_REGISTERED", senior: "PRODUCTION_PREDICATE_REFERENCE", junior: "COUNTEREXAMPLE_FIXTURE", resolution: "PROBE_EXECUTES_THE_EXACT_PRODUCTION_FUNCTION" }),
  Object.freeze({ id: "L04_TOUCH_LANE_VS_CROSSED_BOOK_WITH_REST", state: "LATENT_REGISTERED", senior: "EXISTING_REST", junior: "TOUCH_OR_LOCKED_BOOK_PLACEMENT_VETO", resolution: "HOLD_EXISTING_REST; VETO_ONLY_ORIGINATION_OR_REPRICE" }),
  Object.freeze({ id: "L05_ALLOCATOR_OUTPUT_VS_TRADED_LOW_AXIS", state: "LATENT_REGISTERED", senior: "TRADED_LOW_SUPPORT_AXIS", junior: "RAW_ARITHMETIC_REDUCTION", resolution: "EVERY_REDUCED_OR_CAPPED_TARGET_RESNAPS_AT_OR_BELOW_TO_A_SUPPORTED_LEVEL" }),
  Object.freeze({ id: "L06_SAME_RECEIPT_FLOOR_VS_PAIR_BUDGET", state: "LATENT_REGISTERED", senior: "PAIR_CONSERVATION", junior: "SAME_RECEIPT_FLOOR_HANDOFF", resolution: "HANDOFF_ONLY_WHEN_THE_JOINT_PLAN_REMAINS_UNDER_PAR; OTHERWISE_LAWFUL_ABSTENTION" }),
]);

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

function supportedFloorLevel(criterion, referenceCents) {
  const levels = criterion?.candidate_final_floor_levels_cents ?? [];
  if (!Number.isInteger(referenceCents) || !levels.length) return null;
  return [...levels].sort((a, b) => Math.abs(a - referenceCents) - Math.abs(b - referenceCents) || a - b)[0] ?? null;
}

function criterionSupportsLevel(criterion, targetCents) {
  return Number.isInteger(targetCents) && (criterion?.candidate_final_floor_levels_cents ?? []).includes(targetCents);
}

function criterionSupportsRangeLevel(criterion, targetCents) {
  if (!Number.isInteger(targetCents) || criterion?.signable !== true) return false;
  const deepest = cent(criterion.deepest_supported_floor_cents);
  const shallowest = cent(criterion.shallowest_supported_floor_cents);
  return Number.isInteger(deepest) && Number.isInteger(shallowest) && targetCents >= deepest && targetCents <= shallowest;
}

function currentReceiptIsAskOnlyBookTick(state) {
  for (const legId of state.leg_ids) {
    const rows = state.legs[legId]?.rows ?? [];
    const index = rows.findLastIndex((row) => row.receipt === state.receipt);
    if (index < 0 || rows[index]?.kind !== "BOOK") continue;
    let prior = null;
    for (let i = index - 1; i >= 0; i -= 1) {
      if (rows[i]?.kind === "BOOK") { prior = rows[i]; break; }
    }
    if (!prior) return false;
    const current = rows[index];
    return cent(current.ask_cents) !== cent(prior.ask_cents)
      && cent(current.bid_cents) === cent(prior.bid_cents)
      && cent(current.last_trade_cents) === cent(prior.last_trade_cents);
  }
  return false;
}

function chooseEnvelopePlacementTarget(envelope, quantileTarget, lawfulEnvelopeHigh) {
  const singleton = envelope?.low_cents === envelope?.high_cents ? envelope.low_cents : null;
  if (Number.isInteger(singleton) && Number.isInteger(lawfulEnvelopeHigh) && singleton <= lawfulEnvelopeHigh) {
    return { target_cents: singleton, singleton_level_cents: singleton, singleton_consumed: true };
  }
  return { target_cents: cent(quantileTarget), singleton_level_cents: singleton, singleton_consumed: false };
}

function supportingShapeIdsForLevel(criterion, targetCents) {
  if (!Number.isInteger(criterion?.anchor_cents) || !Number.isInteger(targetCents)) return [];
  const depth = criterion.anchor_cents - targetCents;
  return (criterion.shape_supports ?? [])
    .filter((row) => (row.remaining_depth_bins_cents ?? row.depth_bins_cents ?? []).includes(depth))
    .map((row) => row.shape_id);
}

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

function weightedMedianCents(rows) {
  const valid = rows
    .filter((row) => cent(row.price_cents) && Number.isFinite(row.weight) && row.weight > 0)
    .sort((a, b) => a.price_cents - b.price_cents || a.timestamp_epoch - b.timestamp_epoch || String(a.receipt).localeCompare(String(b.receipt)));
  const total = sum(valid.map((row) => row.weight));
  if (!valid.length || total <= 0) return null;
  let running = 0;
  for (const row of valid) {
    running += row.weight;
    if (running >= total / 2) return row.price_cents;
  }
  return valid.at(-1).price_cents;
}

function centralMedianCents(rows) {
  const values = rows.map((row) => cent(row.value_cents)).filter(Number.isInteger).sort((a, b) => a - b);
  if (!values.length) return null;
  const middle = Math.floor(values.length / 2);
  return values.length % 2 === 1 ? values[middle] : Math.round((values[middle - 1] + values[middle]) / 2);
}

function spreadEyeForLeg(state, legId) {
  const leg = state.legs[legId];
  const formationEnd = finite(leg?.formation_end_epoch);
  const currentBook = leg?.current_book ?? null;
  const currentBid = cent(currentBook?.bid_cents);
  const currentAsk = cent(currentBook?.ask_cents);
  let causalBook = null;
  const printRows = [];
  for (const row of leg?.rows ?? []) {
    if (Number.isFinite(formationEnd) && row.timestamp_epoch < formationEnd) continue;
    if (row.kind === "BOOK") {
      if (cent(row.bid_cents) && cent(row.ask_cents)) causalBook = row;
      continue;
    }
    if (row.kind !== "PRINT" || !cent(row.price_cents)) continue;
    const bid = cent(causalBook?.bid_cents);
    const ask = cent(causalBook?.ask_cents);
    const weight = Number.isFinite(row.size) && row.size > 0 ? row.size : 1;
    const relation = bid && ask
      ? row.price_cents < bid ? "BELOW_QUOTED_BID"
        : row.price_cents === bid ? "AT_QUOTED_BID"
          : row.price_cents < ask ? "INTERIOR_TO_QUOTES"
            : row.price_cents === ask ? "AT_QUOTED_ASK"
              : "ABOVE_QUOTED_ASK"
      : "NO_CAUSAL_TWO_SIDED_BOOK";
    printRows.push({ receipt: row.receipt, timestamp_epoch: row.timestamp_epoch, price_cents: row.price_cents, size: row.size ?? null, weight, bid_cents: bid, ask_cents: ask, relation });
  }
  const currentBidTrades = currentBid ? printRows.filter((row) => row.price_cents === currentBid) : [];
  const lastCurrentBidTrade = currentBidTrades.at(-1) ?? null;
  const sinceEpoch = lastCurrentBidTrade?.timestamp_epoch ?? formationEnd;
  const printsSinceBidTrade = Number.isFinite(sinceEpoch) ? printRows.filter((row) => row.timestamp_epoch > sinceEpoch) : printRows;
  const interior = printRows.filter((row) => row.relation === "INTERIOR_TO_QUOTES");
  const totalPrintWeight = sum(printRows.map((row) => row.weight));
  const interiorWeight = sum(interior.map((row) => row.weight));
  const effectiveClearingPrice = weightedMedianCents(interior);
  const effectiveRelation = !Number.isInteger(effectiveClearingPrice) || !currentBid || !currentAsk
    ? "NO_INTERIOR_CLEARING_PRICE"
    : effectiveClearingPrice < currentBid ? "BELOW_CURRENT_QUOTED_BID"
      : effectiveClearingPrice === currentBid ? "AT_CURRENT_QUOTED_BID"
        : effectiveClearingPrice < currentAsk ? "INTERIOR_TO_CURRENT_QUOTES"
          : effectiveClearingPrice === currentAsk ? "AT_CURRENT_QUOTED_ASK"
            : "ABOVE_CURRENT_QUOTED_ASK";
  return {
    technique: "SPREAD_EYE",
    timestamp_epoch: state.current_epoch,
    receipt: state.receipt,
    current_book_receipt: currentBook?.receipt ?? null,
    current_bid_cents: currentBid,
    current_ask_cents: currentAsk,
    current_bid_last_traded_receipt: lastCurrentBidTrade?.receipt ?? null,
    current_bid_last_traded_epoch: lastCurrentBidTrade?.timestamp_epoch ?? null,
    current_bid_staleness_seconds: lastCurrentBidTrade ? Math.max(0, state.current_epoch - lastCurrentBidTrade.timestamp_epoch) : null,
    current_bid_trade_status: lastCurrentBidTrade ? "TRADED_POST_ONSET" : "NEVER_TRADED_POST_ONSET",
    contracts_since_current_bid_last_traded: sum(printsSinceBidTrade.map((row) => row.weight)),
    print_count_post_onset: printRows.length,
    print_volume_post_onset: totalPrintWeight,
    interior_print_count: interior.length,
    interior_print_volume: interiorWeight,
    interior_print_share: totalPrintWeight > 0 ? interiorWeight / totalPrintWeight : null,
    effective_clearing_price_cents: effectiveClearingPrice,
    effective_clearing_relation_to_current_book: effectiveRelation,
    interior_receipts: interior.map((row) => ({ receipt: row.receipt, timestamp_epoch: row.timestamp_epoch, price_cents: row.price_cents, size: row.size, quoted_bid_cents: row.bid_cents, quoted_ask_cents: row.ask_cents })),
    feeds_pricing_authority_only: true,
    yields_to: ["OBSERVED_TRADED_FLOOR", "LICENSED_LEVEL_TENURE", "PAIR_CONSERVATION", "POST_ONLY"],
    provenance: LAYER_PROVENANCE.spread_eye,
  };
}

function pricingAuthorityForLeg({ state, legId, baseRow, spreadEye, criterion }) {
  const baseTarget = cent(baseRow?.derivation?.derived_target_cents) ?? cent(baseRow?.action?.target_cents);
  const liveBid = cent(baseRow?.derivation?.live_bid_cents);
  const liveAsk = cent(baseRow?.derivation?.live_ask_cents);
  const depthLicense = baseRow?.derivation?.joint_depth_license ?? null;
  const baseLawful = Number.isInteger(baseTarget)
    && baseRow?.derivation?.formation_complete === true
    && baseRow?.derivation?.formed_two_sided_book === true
    && baseRow?.derivation?.crossed_book !== true
    && depthLicense?.lawful === true;
  const clearingTarget = cent(spreadEye?.effective_clearing_price_cents);
  const recomputeInputs = baseRow?.derivation?.authority_recompute_inputs ?? {};
  const recomputeVotes = (recomputeInputs.specialist_map_votes ?? []).map((row) => ({
    event_id: row.event_id,
    conditioning_weight: row.weight,
    licensed_floor_cents: cent(row.value),
    source_receipt: row.source_receipt,
  })).filter((row) => Number.isInteger(row.licensed_floor_cents) && Number.isFinite(row.conditioning_weight) && row.conditioning_weight > 0);
  const independentlyRecomputedEngineTarget = cent(weightedQuantile(recomputeVotes, "licensed_floor_cents", 0.5));
  const observedOwnEvidenceLevel = cent(recomputeInputs.observed_traded_low_cents);
  const observedOwnEvidenceReceipt = recomputeInputs.observed_traded_low_receipt
    ?? [...(state.legs[legId]?.prints ?? [])].reverse().find((row) => cent(row.price_cents) === observedOwnEvidenceLevel)?.receipt
    ?? null;
  const liveBookReceipt = state.legs[legId]?.current_book?.receipt ?? null;
  const ownEvidenceRows = [
    Number.isInteger(observedOwnEvidenceLevel) ? { source: "OBSERVED_TRUE_TRADE_LOW", value_cents: observedOwnEvidenceLevel, receipt: observedOwnEvidenceReceipt } : null,
    Number.isInteger(liveBid) && Number.isInteger(liveAsk) && liveBid < liveAsk ? { source: "CAUSAL_LIVE_BOOK_BID", value_cents: liveBid, receipt: liveBookReceipt } : null,
    Number.isInteger(clearingTarget) ? {
      source: "SPREAD_EYE_EFFECTIVE_CLEARING_PRICE",
      value_cents: clearingTarget,
      receipt: [...(spreadEye?.interior_receipts ?? [])].reverse().find((row) => cent(row.price_cents) === clearingTarget)?.receipt ?? spreadEye?.receipt ?? null,
    } : null,
  ].filter(Boolean);
  const ownEvidenceCentral = cent(centralMedianCents(ownEvidenceRows));
  const formationComplete = baseRow?.derivation?.formation_complete === true;
  const independentlyRecomputedConditionedTarget = formationComplete
    ? ownEvidenceCentral ?? independentlyRecomputedEngineTarget
    : null;
  const ownEvidenceFallbackLawful = Boolean(
    !Number.isInteger(independentlyRecomputedEngineTarget)
    && Number.isInteger(observedOwnEvidenceLevel)
    && criterionSupportsRangeLevel(criterion, observedOwnEvidenceLevel)
  );
  const rawConditionedTarget = baseLawful && Number.isInteger(independentlyRecomputedConditionedTarget)
    ? independentlyRecomputedConditionedTarget
    : ownEvidenceFallbackLawful
      ? observedOwnEvidenceLevel
      : null;
  const authoritySource = Number.isInteger(ownEvidenceCentral) && baseLawful
    ? "PANEL_PRIOR_CONDITIONED_BY_CURRENT_GAME_OWN_EVIDENCE"
    : Number.isInteger(independentlyRecomputedEngineTarget)
      ? "ENGINE_VOTES_LICENSED_DEPTH_PRIOR_WITH_NO_OWN_EVIDENCE_YET"
    : ownEvidenceFallbackLawful
      ? "F_VS_068_OWN_EVIDENCE_VACUUM_FALLBACK"
      : "INSUFFICIENT_EVIDENCE";
  if (!state.dual_belief) state.dual_belief = {};
  if (!state.dual_belief.authority_memory_by_leg) state.dual_belief.authority_memory_by_leg = {};
  const siblingId = state.leg_ids.find((id) => id !== legId);
  const siblingPosition = state.positions[siblingId];
  const conditioningInputs = {
    own_last_market_receipt: state.legs[legId]?.rows?.at(-1)?.receipt ?? null,
    observed_traded_low_cents: observedOwnEvidenceLevel,
    observed_traded_low_receipt: observedOwnEvidenceReceipt,
    live_book_receipt: liveBookReceipt,
    live_bid_cents: liveBid,
    live_ask_cents: liveAsk,
    spread_eye_clearing_cents: clearingTarget,
    spread_eye_clearing_receipt: ownEvidenceRows.find((row) => row.source === "SPREAD_EYE_EFFECTIVE_CLEARING_PRICE")?.receipt ?? null,
    credited_sibling_entry_cents: siblingPosition?.credited ? cent(siblingPosition.entry_cents) : null,
    credited_sibling_fill_receipt: siblingPosition?.credited ? siblingPosition.fill_receipt ?? null : null,
  };
  const conditioningSignature = JSON.stringify(conditioningInputs);
  const priorMemory = state.dual_belief.authority_memory_by_leg[legId] ?? null;
  const conditioningChanged = !priorMemory || priorMemory.conditioning_signature !== conditioningSignature;
  const active = cent(state.positions[legId]?.standing_target_cents);
  let target = cent(rawConditionedTarget);
  let movementDisposition = !priorMemory
    ? "INITIAL_AUTHORITY_FORMATION"
    : target === active
      ? "CONFIRMED_ACTIVE_LEVEL"
      : conditioningChanged
        ? "MOVED_ON_NEW_MARKET_INPUT_OR_STATED_CONDITIONING_CHANGE"
        : "PURE_PANEL_RECOMPOSITION_SUPPRESSED";
  if (priorMemory && !conditioningChanged && target !== active) target = active;
  if (priorMemory && !conditioningChanged && !Number.isInteger(active)) target = null;
  const movementKind = !priorMemory
    ? "FORMED"
    : target === priorMemory.effective_target_cents
      ? "CONFIRMED"
      : Number.isInteger(target) && Number.isInteger(priorMemory.effective_target_cents)
        ? target > priorMemory.effective_target_cents ? "SHIFTED_UP" : "SHIFTED_DOWN"
        : Number.isInteger(target) ? "ORIGINATED" : "WITHHELD";
  state.dual_belief.authority_memory_by_leg[legId] = {
    conditioning_signature: conditioningSignature,
    conditioning_inputs: conditioningInputs,
    panel_prior_cents: independentlyRecomputedEngineTarget,
    raw_conditioned_target_cents: cent(rawConditionedTarget),
    effective_target_cents: target,
    evaluated_at_receipt: state.receipt,
  };
  const authorityRestored = Boolean(baseRow && baseRow.derivation && baseRow.derivation.neighbor_specialist_composition?.vote_count > 0);
  const targetFromLicensedRows = Boolean(
    Number.isInteger(target)
    && formationComplete
    && (ownEvidenceRows.some((row) => row.receipt)
      || (depthLicense?.lawful === true && baseRow.derivation.true_bell_cell_depth_map?.licensed === true))
  );
  return {
    authority: "BASE_V3_MAP_JOINT_DEPTH_MIND_WINDOW_VOTE",
    authority_restored_to_decision_path: authorityRestored,
    base_target_cents: baseTarget,
    target_cents: target,
    base_target_lawful: baseLawful,
    v3_map: baseRow?.derivation?.true_bell_cell_depth_map ?? null,
    joint_depth_license: depthLicense,
    mind_window: baseRow?.derivation?.mind_window ?? null,
    basis_weights: baseRow?.derivation?.basis_weights ?? [],
    authority_source: authoritySource,
    panel_prior_cents: independentlyRecomputedEngineTarget,
    own_evidence_rows: ownEvidenceRows,
    own_evidence_central_cents: ownEvidenceCentral,
    conditioning_chain: {
      prior_cents: independentlyRecomputedEngineTarget,
      own_evidence_rows: ownEvidenceRows,
      conditioned_cents: cent(rawConditionedTarget),
      final_level_cents: target,
      method: "CENTRAL_MEDIAN_OF_CURRENT_GAME_OWN_EVIDENCE_AFTER_FORMATION_ELSE_PANEL_PRIOR",
      prior_to_conditioned_to_level: `${independentlyRecomputedEngineTarget ?? "NONE"}->${cent(rawConditionedTarget) ?? "NONE"}->${target ?? "NONE"}`,
      provenance: LAYER_PROVENANCE.own_evidence_inside_author,
    },
    level_movement: {
      disposition: movementDisposition,
      movement_kind: movementKind,
      conditioning_changed: conditioningChanged,
      conditioning_inputs: conditioningInputs,
      prior_authority_memory: priorMemory,
      panel_recomposition_alone_may_move: false,
      provenance: LAYER_PROVENANCE.evidence_only_level_movement,
    },
    independently_recomputed_engine_target_cents: independentlyRecomputedEngineTarget,
    independently_recomputed_conditioned_target_cents: independentlyRecomputedConditionedTarget,
    independently_recomputed_authority_target_cents: target,
    production_target_matches_independent_recompute: target === cent(state.dual_belief.authority_memory_by_leg[legId].effective_target_cents),
    authority_recompute_inputs: recomputeInputs,
    spread_eye_consumed: ownEvidenceRows.some((row) => row.source === "SPREAD_EYE_EFFECTIVE_CLEARING_PRICE"),
    spread_eye_effective_clearing_price_cents: clearingTarget,
    spread_eye_reason: "SPREAD_EYE_CONDITIONS_THE_PANEL_PRIOR_INSIDE_THE_SINGLE_AUTHORITY_AND_NEVER_COMMANDS_A_LANE",
    live_bid_cents: liveBid,
    live_ask_cents: liveAsk,
    target_from_licensed_rows: targetFromLicensedRows,
    // The authority can lawfully be silent.  In that state lanes still may not
    // invent a price; they can only hold an already licensed rest.  Derive the
    // contract from the loaded specialist authority and either a licensed
    // target or explicit silence, rather than stamping a literal.
    no_lane_may_replace_target: Boolean(authorityRestored && (!Number.isInteger(target) || targetFromLicensedRows)),
    provenance: [LAYER_PROVENANCE.pricing_authority_restored, LAYER_PROVENANCE.spread_eye],
  };
}

function supportedFloorAtOrBelow(criterion, targetCents, lowerBoundCents = null) {
  if (!Number.isInteger(targetCents)) return null;
  const levels = [...new Set((criterion?.candidate_final_floor_levels_cents ?? []).filter(Number.isInteger))]
    .filter((level) => level <= targetCents && (!Number.isInteger(lowerBoundCents) || level >= lowerBoundCents))
    .sort((a, b) => b - a);
  return levels[0] ?? null;
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
  const observedTradeLow = cent(own.observed_traded_low_cents);
  const observedTradeLowReceipt = observedTradeLow === null
    ? null
    : [...state.legs[legId].prints].reverse().find((row) => cent(row.price_cents) === observedTradeLow)?.receipt ?? null;
  const envelopeHigh = observedTradeLow ?? liveBid;
  const envelopeHighBasis = observedTradeLow ? "OBSERVED_TRUE_TRADE_LOW" : liveBid ? "CAUSAL_DISPLAYED_BID" : null;
  const envelopeHighReceipt = observedTradeLow ? observedTradeLowReceipt : reads.books.value[legId]?.receipt ?? null;
  const mapVotes = baseRow.derivation.true_bell_cell_depth_map?.map_votes ?? [];
  // F-VS-120: the seen low is state, not the answer.  Members supply the
  // bell-bounded strict-future low relative to the low they had seen at the
  // same phase.  The existing own-evidence conditioning weights form the
  // expectation; no return-to-low assumption or numerical offset survives.
  const expectedFutureLowOffset = conditionedPrior?.expected_future_low_minus_seen_low_cents;
  const predictedRaw = cent(own.conditioning_low_cents) && Number.isFinite(expectedFutureLowOffset)
    ? own.conditioning_low_cents + Math.round(expectedFutureLowOffset)
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
  const store = mapVotes.length
    ? `${mapVotes.length} specialist member cells (V3 map @ac68e3bc; SOURCE_KEY=LIBRARY_CLOSE_CENTS; RUNTIME_REKEY=NONE)`
    : `UNMAPPED (V3 map @ac68e3bc; SOURCE_KEY=LIBRARY_CLOSE_CENTS; RUNTIME_REKEY=NONE)`;
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
    envelope_high_cents: envelopeHigh,
    envelope_high_basis: envelopeHighBasis,
    envelope_high_receipt: envelopeHighReceipt,
    envelope_high_is_floored_mid: false,
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
      cells: mapVotes.map((row) => ({ event_id: row.event_id, category: row.category, price_cell: row.v3_price_cell, edge_p50_cents: row.map_cell?.edge_p50_cents ?? null })),
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

function allocateUnderPar(targets, parAllocationFloorBounds, criteriaByLeg) {
  const ids = Object.keys(targets);
  if (ids.length !== 2 || ids.some((id) => !cent(targets[id]))) return { lawful: false, targets, reason: "PAIR_TARGET_INCOMPLETE" };
  const excess = targets[ids[0]] + targets[ids[1]] - base.PAR_BUDGET_CENTS;
  if (excess <= 0) return { lawful: true, targets: { ...targets }, reason: "JOINT_TARGET_ALREADY_UNDER_PAR", excess_cents: 0, par_allocation_floor_bounds: parAllocationFloorBounds, headroom_cents: Object.fromEntries(ids.map((id) => [id, Math.max(0, targets[id] - (parAllocationFloorBounds[id]?.value_cents ?? targets[id]))])) };
  return {
    lawful: false,
    targets: { ...targets },
    reason: "PAIR_CONSERVATION_VETO_AUTHORITY_LEVELS_NOT_REWRITTEN",
    excess_cents: excess,
    par_allocation_floor_bounds: parAllocationFloorBounds,
    price_rewrites: 0,
  };
}

function deriveJointActions({ state, reads, neighborhood, lineageByLeg, resources }) {
  if (!state.dual_belief) state.dual_belief = { first_coherence: null, current_envelopes: null, carried_convictions: {}, coherence_history: [], envelope_history: [], conviction_history: [], first_lawful_coherence_by_leg: {}, rearm_by_leg: {} };
  if (!state.dual_belief.first_lawful_coherence_by_leg) state.dual_belief.first_lawful_coherence_by_leg = {};
  if (!state.dual_belief.rearm_by_leg) state.dual_belief.rearm_by_leg = {};
  if (!state.dual_belief.carried_convictions) state.dual_belief.carried_convictions = {};
  if (!state.dual_belief.conviction_history) state.dual_belief.conviction_history = [];
  delete state.dual_belief.floor_rest_tenure_by_leg;
  delete state.dual_belief.floor_rest_tenure_history;
  // F-VS-148..152: the persistent first-guess floor_rest_locks state is retired.
  // Floor protection is evaluated from the current active rest, current traded
  // floor, and current survivor support on every receipt.
  delete state.dual_belief.floor_rest_locks;
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
  const spreadEyes = Object.fromEntries(openIds.map((id) => [id, spreadEyeForLeg(state, id)]));
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
  const pricingAuthorities = Object.fromEntries(openIds.map((id) => [id, pricingAuthorityForLeg({ state, legId: id, baseRow: baseRows.get(id), spreadEye: spreadEyes[id], criterion: survivorUpdate.legs[id]?.target_criterion ?? null })]));
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
    ? Object.fromEntries(openIds.flatMap((id) => {
      const criterion = survivorUpdate.legs[id]?.target_criterion;
      const supported = supportedFloorLevel(criterion, beliefs[id].predicted_cents);
      const high = beliefs[id].envelope_high_cents;
      if (!Number.isInteger(supported) || !Number.isInteger(high) || supported > high) return [];
      return [[id, {
        low_cents: supported,
        high_cents: high,
        belief_receipt: state.receipt,
        target_axis: survivorShapes.TRADED_LOW_AXIS,
        target_criterion: criterion,
        belief_prediction_reference_cents: beliefs[id].predicted_cents,
      }]];
    }))
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
    const eliminationsStillHold = !priorConviction || (priorSupport.length > 0 && supportIntersection.length > 0);
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
      const supportForNext = proposed
        ? priorConviction && ["CONFIRMED_CARRIED_CONVICTION", "TIGHTENED_CARRIED_CONVICTION"].includes(update) && supportIntersection.length
          ? supportIntersection
          : [...survivorIds]
        : supportIntersection;
      nextEnvelopes[id] = effective;
      nextConvictions[id] = {
        envelope: effective,
        belief_receipt: proposed ? state.receipt : priorConviction.belief_receipt,
        latest_basis_restatement_receipt: state.receipt,
        supporting_shape_ids: [...supportForNext],
        movement_statement: convictionEvolution[id].movement_statement,
        provenance: LAYER_PROVENANCE.carried_conviction,
      };
    }
    if (migrated) state.dual_belief.envelope_history.push({ leg_id: id, ...envelopeMigrations[id] });
  }
  if (coherentNow && !state.dual_belief.first_coherence) state.dual_belief.first_coherence = { ...coherence, envelopes: proposedEnvelopes, beliefs: JSON.parse(JSON.stringify(beliefs)) };

  const beliefMode = openIds.some((id) => Boolean(decisionEnvelopes[id]));
  const targets = {};
  const parAllocationFloorBounds = {};
  const envelopePlacement = {};
  for (const legId of openIds) {
    const book = reads.books.value[legId];
    const liveBid = cent(book?.bid_cents), liveAsk = cent(book?.ask_cents);
    const active = cent(reads.half_pair_state.value.legs[legId].standing_target_cents);
    const survivor = survivorUpdate.legs[legId];
    const criterion = survivor?.target_criterion ?? null;
    if (decisionEnvelopes[legId] && coherentNow) {
      const envelope = decisionEnvelopes[legId];
      if (envelope && microMicroResolved && liveBid && liveAsk && liveBid < liveAsk) {
        const conditionedExpectedFutureLow = cent(beliefs[legId]?.predicted_cents);
        const phaseCentralEstimate = beliefs[legId]?.phase_conditioning?.phase_central_estimate ?? null;
        const causalSeenLow = cent(beliefs[legId]?.own_evidence?.conditioning_low_cents);
        const upperQuantileOffset = finite(phaseCentralEstimate?.q75_cents);
        const upperQuantileRaw = Number.isInteger(causalSeenLow) && Number.isFinite(upperQuantileOffset)
          ? causalSeenLow + Math.round(upperQuantileOffset)
          : null;
        const lawfulEnvelopeHigh = envelope.high_cents;
        const lawfulEnvelopeExists = envelope.low_cents <= lawfulEnvelopeHigh;
        const upperQuantileTarget = Number.isInteger(upperQuantileRaw) && lawfulEnvelopeExists
          ? clamp(upperQuantileRaw, envelope.low_cents, lawfulEnvelopeHigh)
          : null;
        const supportedQuantileTarget = supportedFloorLevel(criterion, upperQuantileTarget);
        const axisAlignedQuantileTarget = Number.isInteger(supportedQuantileTarget)
          && lawfulEnvelopeExists
          && supportedQuantileTarget >= envelope.low_cents
          && supportedQuantileTarget <= lawfulEnvelopeHigh
          ? supportedQuantileTarget
          : null;
        // F-VS-130: coherent belief pricing must account for executable prints
        // inside the displayed spread. The already-built conditioned population's
        // upper quantile names that cent. The live bid remains evidence in the
        // sentence, but it never anchors a coherent-envelope placement.
        const envelopeTargetDecision = chooseEnvelopePlacementTarget(envelope, axisAlignedQuantileTarget, lawfulEnvelopeHigh);
        const singletonEnvelopeLevel = envelopeTargetDecision.singleton_level_cents;
        const distributionPricedTarget = envelopeTargetDecision.target_cents;
        // F-VS-114(c): a newly migrated envelope re-derives the standing rest
        // on this same receipt, in either direction.  A stale active target may
        // never veto the current belief-priced target.
        targets[legId] = Number.isInteger(distributionPricedTarget) ? distributionPricedTarget : null;
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
          selected_quantile_inside_envelope_cents: axisAlignedQuantileTarget,
          pre_axis_quantile_inside_envelope_cents: upperQuantileTarget,
          traded_low_target_criterion: criterion,
          conditioned_q50_reference_cents: conditionedExpectedFutureLow,
          live_bid_reference_only_cents: liveBid,
          touch_anchored_inside_coherent_envelope: false,
          singleton_survivor_envelope_level_cents: singletonEnvelopeLevel,
          singleton_envelope_consumed: envelopeTargetDecision.singleton_consumed,
          chosen_candidate_rule: envelopeTargetDecision.singleton_consumed
            ? "SINGLETON_SURVIVOR_ENVELOPE_CONSUMED_AT_EXACT_LEVEL"
            : Number.isInteger(axisAlignedQuantileTarget)
              ? "CONDITIONED_Q75_RECONCILED_TO_EXACT_SURVIVOR_TRADED_LOW_DEPTH_BIN"
              : "NO_LAWFUL_TRADED_LOW_SUPPORTED_Q75_INSIDE_ENVELOPE",
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
        envelopePlacement[legId] = { mode: "HOLD_PREVIOUSLY_LICENSED_ENVELOPE_TARGET", coherence_exists_at_receipt: true, chosen_target_cents: active, numeric_constant_added: false };
      }
    } else if (coherence.status === "DISAGREES") {
      // F-VS-138/142: disagreement blocks belief-priced origination, but it
      // cannot veto independent own-tape evidence that the surviving traded-low
      // hypotheses support.  Only the leg's receipt-pinned traded evidence may
      // name a new level here.  The displayed bid is context, never the default
      // price of a DISAGREES rest (F-VS-177).
      const runningTradeLow = cent(state.legs[legId].running_true_trade_low_cents);
      const ownEvidenceTarget = runningTradeLow;
      const belowPriorLowTarget = Number.isInteger(liveBid) && Number.isInteger(runningTradeLow) && liveBid < runningTradeLow
        ? liveBid
        : null;
      const floorCapableSupported = Boolean(
        Number.isInteger(belowPriorLowTarget)
        && Number.isInteger(liveAsk)
        && belowPriorLowTarget < liveAsk
        && book?.receipt
        && criterionSupportsRangeLevel(criterion, belowPriorLowTarget)
      );
      const ownEvidenceComplete = Boolean(ownEvidenceTarget && liveAsk && ownEvidenceTarget < liveAsk && book?.receipt);
      const survivorSupported = ownEvidenceComplete && criterionSupportsLevel(criterion, ownEvidenceTarget);
      targets[legId] = floorCapableSupported ? belowPriorLowTarget : survivorSupported ? ownEvidenceTarget : active;
      envelopePlacement[legId] = {
        mode: floorCapableSupported
          ? "FLOOR_CAPABLE_OWN_BOOK_LEVEL_BELOW_PRIOR_TRADE_LOW"
          : survivorSupported
            ? "OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED"
            : "DISAGREES_HOLD_OR_REDERIVE_NO_PLACEMENT",
        coherence_exists_at_receipt: false,
        coherence_status_at_receipt: coherence.status,
        live_bid_cents: liveBid,
        live_ask_cents: liveAsk,
        book_receipt: book?.receipt ?? null,
        live_bid_consumed_as_price: floorCapableSupported,
        live_bid_relation: floorCapableSupported
          ? "OWN_BOOK_LEVEL_BELOW_PRIOR_TRADE_LOW_LICENSED_BY_SIGNABLE_SURVIVOR_RANGE"
          : survivorSupported && ownEvidenceTarget === liveBid
            ? "EVIDENCED_TRADE_LOW_HAPPENS_TO_EQUAL_LIVE_BID"
            : "REFERENCE_ONLY_NOT_LEVEL_AUTHORITY",
        running_true_trade_low_cents: runningTradeLow,
        own_evidence_target_cents: ownEvidenceTarget,
        below_prior_low_target_cents: belowPriorLowTarget,
        lower_lawful_level_existed: floorCapableSupported,
        pricing_lane: floorCapableSupported ? "FLOOR_CAPABLE_OWN_BOOK_LEVEL" : survivorSupported ? "DISAGREES_PRIOR_TRADE_LOW" : "NO_NEW_LEVEL",
        floor_capable_survivor_range_supported: floorCapableSupported,
        own_evidence_complete: ownEvidenceComplete,
        survivor_target_supported: floorCapableSupported || survivorSupported,
        traded_low_target_criterion: criterion,
        chosen_target_cents: targets[legId],
        may_originate_rest: floorCapableSupported || survivorSupported,
        may_reprice_rest: floorCapableSupported || survivorSupported,
        disagreement_stated: true,
        data_consumed_for_placement: floorCapableSupported || survivorSupported,
        provenance: [LAYER_PROVENANCE.floor_capable_lane, LAYER_PROVENANCE.disagrees_own_evidence_release, LAYER_PROVENANCE.traded_low_axis_alignment, LAYER_PROVENANCE.pair_coherence],
        numeric_constant_added: false,
      };
    } else if (decisionEnvelopes[legId]) {
      // F-VS-134/135: an examined carried conviction may originate or reprice.
      // It is read from a prior receipt, its eliminations are rechecked, and its
      // book basis is re-stated now. The same conditioned Q75 geometry remains
      // authoritative; touch is still subordinate.
      const envelope = decisionEnvelopes[legId];
      const phaseCentralEstimate = beliefs[legId]?.phase_conditioning?.phase_central_estimate ?? null;
      const causalSeenLow = cent(beliefs[legId]?.own_evidence?.conditioning_low_cents);
      const upperQuantileOffset = finite(phaseCentralEstimate?.q75_cents);
      const upperQuantileRaw = Number.isInteger(causalSeenLow) && Number.isFinite(upperQuantileOffset) ? causalSeenLow + Math.round(upperQuantileOffset) : null;
      const lawfulEnvelopeHigh = envelope.high_cents;
      const lawfulEnvelopeExists = Number.isInteger(lawfulEnvelopeHigh) && envelope.low_cents <= lawfulEnvelopeHigh;
      const preAxisCarriedTarget = Number.isInteger(upperQuantileRaw) && lawfulEnvelopeExists ? clamp(upperQuantileRaw, envelope.low_cents, lawfulEnvelopeHigh) : active;
      const supportedCarriedTarget = supportedFloorLevel(criterion, preAxisCarriedTarget);
      const quantileCarriedTarget = Number.isInteger(supportedCarriedTarget) && lawfulEnvelopeExists && supportedCarriedTarget >= envelope.low_cents && supportedCarriedTarget <= lawfulEnvelopeHigh ? supportedCarriedTarget : active;
      const envelopeTargetDecision = chooseEnvelopePlacementTarget(envelope, quantileCarriedTarget, lawfulEnvelopeHigh);
      const singletonEnvelopeLevel = envelopeTargetDecision.singleton_level_cents;
      const carriedTarget = envelopeTargetDecision.target_cents;
      targets[legId] = carriedTarget;
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
        singleton_survivor_envelope_level_cents: singletonEnvelopeLevel,
        singleton_envelope_consumed: envelopeTargetDecision.singleton_consumed,
        placement_quantile: "Q75",
        selected_quantile_offset_cents: upperQuantileOffset,
        selected_quantile_raw_cents: upperQuantileRaw,
        pre_axis_target_cents: preAxisCarriedTarget,
        traded_low_target_criterion: criterion,
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
      envelopePlacement[legId] = { mode: "CONSUME_OWN_EVIDENCED_LIVE_TOUCH_WHILE_ENVELOPE_NULL", live_bid_cents: liveBid, live_ask_cents: liveAsk, book_receipt: book?.receipt ?? null, chosen_target_cents: targets[legId], may_originate_rest: true, data_consumed: Boolean(liveBid && liveAsk && liveBid < liveAsk && book?.receipt), provenance: [LAYER_PROVENANCE.consume_live_touch_fix, LAYER_PROVENANCE.own_evidence_sufficiency], numeric_constant_added: false };
    }
    const laneProposalBeforeAuthority = cent(targets[legId]);
    const laneModeBeforeAuthority = envelopePlacement[legId]?.mode ?? null;
    const pricingAuthority = pricingAuthorities[legId];
    const authorityTarget = cent(pricingAuthority?.target_cents);
    const writerLane = coherentNow && decisionEnvelopes[legId]
      ? "COHERENT_ENVELOPE_WRITER"
      : coherence.status === "DISAGREES"
        ? "FLOOR_CAPABLE_WRITER"
        : decisionEnvelopes[legId]
          ? "CARRIED_CONVICTION_WRITER"
          : "OWN_TOUCH_WRITER";
    targets[legId] = authorityTarget ?? active;
    const laneLevelReplacedAuthority = Number.isInteger(authorityTarget)
      && cent(targets[legId]) !== authorityTarget;
    envelopePlacement[legId] = {
      ...envelopePlacement[legId],
      mode: authorityTarget ? "PRICING_AUTHORITY_TARGET_EXECUTED" : active ? "PRICING_AUTHORITY_SILENT_HOLD_EXISTING_REST" : "PRICING_AUTHORITY_SILENT_NO_PLACEMENT",
      prior_lane_mode: laneModeBeforeAuthority,
      lane_proposal_before_authority_cents: laneProposalBeforeAuthority,
      pricing_authority: pricingAuthority,
      writer_lane: writerLane,
      lane_level_replaced_authority: laneLevelReplacedAuthority,
      live_bid_relation: authorityTarget === liveBid
        ? "PRICING_AUTHORITY_OUTPUT_EQUALS_LIVE_BID_NOT_LANE_DEFAULT"
        : "REFERENCE_EVIDENCE_NOT_FINAL_LEVEL",
      chosen_target_cents: targets[legId],
      technique_contract: "C01_PRICING_AUTHORITY_OVER_LANE_LEVEL_SELECTION",
    };
    const formationComplete = Number.isFinite(reads.anchor_settle.value.formation_progress[legId]) && reads.anchor_settle.value.formation_progress[legId] >= 1;
    const lockedOrCrossedBook = Boolean(liveBid && liveAsk && liveBid >= liveAsk);
    if (!formationComplete) {
      targets[legId] = null;
      envelopePlacement[legId] = { ...envelopePlacement[legId], mode: "FORMATION_NOT_COMPLETE_NO_PLACEMENT", chosen_target_cents: null };
    } else if (lockedOrCrossedBook) {
      targets[legId] = active;
      envelopePlacement[legId] = {
        ...envelopePlacement[legId],
        mode: active ? "LOCKED_BOOK_PLACEMENT_VETO_EXISTING_REST_HELD" : "LOCKED_BOOK_PLACEMENT_VETO_NO_REST",
        locked_book_is_placement_law_only: true,
        existing_rest_cancelled_by_locked_book: false,
        chosen_target_cents: active,
        technique_contract: "C05_LOCKED_BOOK_IS_PLACEMENT_ONLY",
      };
    }
    const evidencedFloor = cent(state.legs[legId].running_true_trade_low_cents);
    const evidencedFloorPrint = evidencedFloor === null
      ? null
      : [...state.legs[legId].prints].reverse().find((row) => cent(row.price_cents) === evidencedFloor) ?? null;
    const evidencedFloorReceipt = evidencedFloorPrint?.receipt ?? null;
    const floorEstablishedOnCurrentReceipt = Boolean(evidencedFloorPrint && evidencedFloorPrint.timestamp_epoch === state.current_epoch);
    const sameReceiptFloorPostable = Boolean(floorEstablishedOnCurrentReceipt && Number.isInteger(liveAsk) && evidencedFloor < liveAsk);
    const targetBeforeSameReceiptFloorLaw = cent(targets[legId]);
    // The new trade is evidence for the authority's next derivation, never a
    // second price writer.  A rest already on protected ground can hold; no
    // same-receipt handoff is allowed to substitute the raw print as target.
    if (floorEstablishedOnCurrentReceipt) {
      envelopePlacement[legId] = {
        ...envelopePlacement[legId],
        floor_evidence_update: "CURRENT_RECEIPT_TRADE_LOW_CONSUMED_AS_CONDITIONING_NOT_TARGET",
        prior_mode: envelopePlacement[legId]?.mode ?? null,
        prior_target_cents: targetBeforeSameReceiptFloorLaw,
        evidenced_floor_cents: evidencedFloor,
        evidenced_floor_receipt: evidencedFloorReceipt,
        evidenced_floor_timestamp_epoch: evidencedFloorPrint.timestamp_epoch,
        floor_established_on_current_receipt: floorEstablishedOnCurrentReceipt,
        floor_postable_below_live_ask: sameReceiptFloorPostable,
        chosen_target_cents: targets[legId],
        writer_lane: envelopePlacement[legId]?.writer_lane ?? null,
        floor_handoff_same_receipt: false,
        raw_trade_low_authored_target: false,
        disposition: "EVIDENCE_UPDATED_AUTHORITY_REMAINS_SOLE_PRICE_AUTHOR",
        provenance: LAYER_PROVENANCE.same_receipt_floor_hold,
      };
    }
    const targetBeforeAllocation = cent(targets[legId]);
    const boundValue = evidencedFloor && targetBeforeAllocation ? Math.min(evidencedFloor, targetBeforeAllocation) : targetBeforeAllocation;
    parAllocationFloorBounds[legId] = {
      name: "PAR_ALLOCATION_OBSERVED_TRADED_FLOOR_BOUND",
      value_cents: boundValue,
      evidenced_floor_cents: evidencedFloor,
      source: evidencedFloor ? "OBSERVED_TRUE_TRADE_PRINT" : "NO_TRADED_FLOOR_NO_REDUCTION_AUTHORITY",
      source_receipt: evidencedFloorReceipt,
      never_above_evidenced_floor: !evidencedFloor || !boundValue || boundValue <= evidencedFloor,
      role: "MAXIMUM_LAWFUL_REDUCTION_FLOOR_FOR_PAIR_PAR_ALLOCATION",
      provenance: LAYER_PROVENANCE.definition_repair_headroom,
    };
    const floorSupportingShapes = Number.isInteger(active) && criterionSupportsRangeLevel(criterion, active) ? (survivor?.survivor_shapes ?? []) : [];
    // F-VS-217/F-VS-218: tenure has direction. It protects a rest standing
    // exactly on the evidenced own-tape level from a move away, but never
    // protects a different rest from a recompute onto that evidenced level.
    const activeAtSupportedEvidencedFloor = Boolean(Number.isInteger(active) && Number.isInteger(evidencedFloor) && active === evidencedFloor && evidencedFloorReceipt);
    const proposalBeforeFloorProtection = cent(targets[legId]);
    // The lawful protection is symmetric and exact: only a rest already standing
    // at the current evidenced traded floor may hold against a conflicting belief,
    // and only while the current survivor set continues to support that cent.
    if (activeAtSupportedEvidencedFloor && proposalBeforeFloorProtection !== active) {
      targets[legId] = active;
      parAllocationFloorBounds[legId] = { ...parAllocationFloorBounds[legId], value_cents: active, protected_active_floor_rest: true };
      envelopePlacement[legId] = {
        mode: "EXACT_EVIDENCED_FLOOR_REST_HELD_AGAINST_MOVE_AWAY",
        writer_lane: "LICENSED_FLOOR_TENURE",
        active_floor_rest_cents: active,
        evidenced_floor_cents: evidencedFloor,
        evidenced_floor_source: "OBSERVED_TRUE_TRADE_PRINT_ONLY_NOT_DERIVED_FROM_REST",
        evidenced_floor_receipt: evidencedFloorReceipt,
        licensed_floor_level_cents: active,
        licensed_floor_level_receipt: evidencedFloorReceipt,
        proposed_conflicting_target_cents: proposalBeforeFloorProtection,
        supporting_shapes_still_alive: floorSupportingShapes,
        supporting_eliminations_overturned: false,
        chosen_target_cents: active,
        may_cancel_or_reprice_off_floor: false,
        tenure_direction: "BLOCK_AWAY_NEVER_BLOCK_ONTO",
        technique_contract: "C02_FLOOR_TENURE_OVER_BELIEF_DRIFT",
        provenance: [LAYER_PROVENANCE.floor_rest_protection, LAYER_PROVENANCE.technique_contracts],
        numeric_constant_added: false,
      };
    }
  }
  let allocation = { lawful: true, targets: { ...targets }, reason: beliefMode ? "ONE_OPEN_SIDE_OR_LIVE_TOUCH" : "OWN_EVIDENCED_LIVE_TOUCH_MIND_ONLY", excess_cents: 0 };
  if (openIds.length === 2 && openIds.every((id) => cent(targets[id]))) allocation = allocateUnderPar(targets, parAllocationFloorBounds, Object.fromEntries(openIds.map((id) => [id, survivorUpdate.legs[id]?.target_criterion ?? null])));
  const creditedId = state.leg_ids.find((id) => reads.half_pair_state.value.legs[id].credited);
  if (creditedId && openIds.length === 1) {
    const openId = openIds[0], cap = base.PAR_BUDGET_CENTS - reads.half_pair_state.value.legs[creditedId].entry_cents;
    const beforeCap = cent(allocation.targets[openId]);
    allocation.fill_handoff_veto = {
      authority_target_cents: beforeCap,
      cap_cents: cap,
      lawful: !Number.isInteger(beforeCap) || beforeCap <= cap,
      price_rewritten: false,
    };
    if (Number.isInteger(beforeCap) && beforeCap > cap) {
      allocation.lawful = false;
      allocation.reason = "FILL_HANDOFF_PAIR_CAP_VETO_AUTHORITY_LEVEL_NOT_REWRITTEN";
      allocation.excess_cents = beforeCap - cap;
    }
  }
  // F-VS-191/F-VS-192: post-only is a predicate on OUR candidate target, not
  // merely on whether the displayed book is uncrossed. It applies to every
  // candidate row. A rejected new target cannot cancel a lawful, already
  // postable rest; the held level is a captured rest claim, never a floor
  // producer. Only the observed true-trade low owns the word "floor".
  for (const legId of openIds) {
    if (!allocation.lawful) continue;
    const candidate = cent(allocation.targets[legId]);
    const active = cent(reads.half_pair_state.value.legs[legId].standing_target_cents);
    const floor = cent(state.legs[legId].running_true_trade_low_cents);
    const ask = cent(reads.books.value[legId]?.ask_cents);
    const placement = envelopePlacement[legId] ?? {};
    const capturedRestLevel = cent(reads.half_pair_state.value.legs[legId].standing_captured_rest_level_cents) ?? active;
    const candidateIsNewOrder = Number.isInteger(candidate) && candidate !== active;
    const candidateCrossesAsk = Boolean(candidateIsNewOrder && Number.isInteger(ask) && candidate >= ask);
    const candidateMissing = !Number.isInteger(candidate);
    const candidateAskMissing = Boolean(candidateIsNewOrder && !Number.isInteger(ask));
    const candidateUnpostable = candidateCrossesAsk || candidateAskMissing;
    const askOnlyBookTick = currentReceiptIsAskOnlyBookTick(state);
    const activeIsPostable = Boolean(active && Number.isInteger(ask) && active < ask);
    const activeCrossesAsk = Boolean(Number.isInteger(active) && Number.isInteger(ask) && active >= ask);
    const siblingId = state.leg_ids.find((id) => id !== legId);
    const siblingPlan = reads.half_pair_state.value.legs[siblingId].credited
      ? cent(reads.half_pair_state.value.legs[siblingId].entry_cents)
      : cent(allocation.targets[siblingId]) ?? cent(reads.half_pair_state.value.legs[siblingId].standing_target_cents);
    const pairPlanLawful = !Number.isInteger(siblingPlan) || active + siblingPlan <= base.PAR_BUDGET_CENTS;
    if (activeCrossesAsk && (!Number.isInteger(candidate) || candidate >= ask || candidate === active)) {
      allocation.targets[legId] = null;
      allocation.reason = `${allocation.reason}+CONTINUOUS_POST_ONLY_CANCEL_CROSSED_STANDING_REST`;
      envelopePlacement[legId] = {
        ...placement,
        mode: "CONTINUOUS_POST_ONLY_CANCEL_CROSSED_STANDING_REST",
        writer_lane: "POST_ONLY_CONTINUOUS_VETO",
        active_target_before_cents: active,
        live_ask_cents: ask,
        active_target_crossed_live_ask: true,
        authority_candidate_cents: candidate,
        post_only_test: { target_cents: active, live_ask_cents: ask, lawful: false, predicate: "STANDING_TARGET_CENTS_LT_LIVE_ASK_CENTS" },
        post_only_disposition: "ACTIVE_REST_UNLAWFUL_TO_HOLD_CANCEL_AND_REDERIVE",
        chosen_target_cents: null,
        technique_contract: "C03_POST_ONLY_OVER_ALL_NEW_AND_STANDING_ORDERS",
        provenance: [LAYER_PROVENANCE.post_only_own_target, LAYER_PROVENANCE.continuous_post_only],
      };
    } else if (candidateIsNewOrder && askOnlyBookTick) {
      allocation.targets[legId] = active;
      envelopePlacement[legId] = {
        ...placement,
        mode: active ? "ASK_ONLY_TICK_VETO_HOLD_STANDING_LAWFUL_REST" : "ASK_ONLY_TICK_VETO_STAND_DOWN",
        ask_only_tick: true,
        post_only_role: "VETO_ONLY_NOT_PRICE_AUTHOR",
        chosen_target_cents: active,
        resolution: active ? "HOLD_STANDING_LAWFUL_REST" : "STAND_DOWN_REDERIVE_NEXT_NON_ASK_RECEIPT",
      };
    } else if (candidateMissing) {
      allocation.targets[legId] = active;
      envelopePlacement[legId] = {
        ...placement,
        mode: active ? "INSUFFICIENT_AUTHORITY_HOLD_STANDING_LAWFUL_REST" : "INSUFFICIENT_AUTHORITY_STAND_DOWN",
        authority_vacuum: true,
        resolution: active ? "HOLD_STANDING_LAWFUL_REST" : "NO_F_VS_068_LEVEL_STAND_DOWN",
        post_only_evaluated: false,
        chosen_target_cents: active,
      };
    } else if (candidateUnpostable && activeIsPostable && pairPlanLawful) {
      allocation.targets[legId] = active;
      allocation.reason = `${allocation.reason}+POST_ONLY_BLOCKED_NEW_TARGET_HOLD_EXISTING_POSTABLE_REST`;
      envelopePlacement[legId] = {
        ...placement,
        mode: "POST_ONLY_BLOCKED_NEW_TARGET_HOLD_EXISTING_POSTABLE_REST",
        prior_mode: placement.mode ?? null,
        active_captured_rest_level_cents: active,
        evidenced_floor_cents: floor,
        evidenced_floor_source: Number.isInteger(floor) ? "OBSERVED_TRUE_TRADE_PRINT" : "NO_OBSERVED_TRADED_FLOOR",
        captured_rest_level_cents: capturedRestLevel,
        captured_rest_claim_source: "STANDING_REST_LICENSE_NOT_A_FLOOR_PRODUCER",
        captured_rest_license_receipt: reads.half_pair_state.value.legs[legId].standing_captured_rest_license_receipt ?? null,
        live_ask_cents: ask,
        blocked_candidate_cents: candidate,
        active_target_before_cents: active,
        active_target_crossed_live_ask: Number.isInteger(active) && Number.isInteger(ask) && active >= ask,
        post_only_test: { target_cents: candidate, live_ask_cents: ask, lawful: false, predicate: "TARGET_CENTS_LT_LIVE_ASK_CENTS" },
        post_only_disposition: "VETO_ONLY_NEW_TARGET_UNPOSTABLE_EXISTING_LAWFUL_REST_HELD",
        pair_plan_sibling_cents: siblingPlan,
        pair_plan_at_or_below_99: pairPlanLawful,
        chosen_target_cents: active,
        provenance: [LAYER_PROVENANCE.post_only_own_target, LAYER_PROVENANCE.definition_lock_rest_claim],
      };
    } else if (candidateUnpostable) {
      allocation.targets[legId] = null;
      allocation.reason = `${allocation.reason}+POST_ONLY_BLOCKED_NO_EXISTING_POSTABLE_REST`;
      envelopePlacement[legId] = {
        ...placement,
        mode: "POST_ONLY_BLOCKED_NO_EXISTING_POSTABLE_REST",
        prior_mode: placement.mode ?? null,
        evidenced_floor_cents: floor,
        evidenced_floor_source: Number.isInteger(floor) ? "OBSERVED_TRUE_TRADE_PRINT" : "NO_OBSERVED_TRADED_FLOOR",
        blocked_candidate_cents: candidate,
        active_target_before_cents: active,
        active_target_crossed_live_ask: Number.isInteger(active) && Number.isInteger(ask) && active >= ask,
        live_ask_cents: ask,
        post_only_test: { target_cents: candidate, live_ask_cents: ask, lawful: false, predicate: "TARGET_CENTS_LT_LIVE_ASK_CENTS" },
        post_only_disposition: "VETO_ONLY_WITHHOLD_UNPOSTABLE_NEW_TARGET",
        chosen_target_cents: null,
        provenance: [LAYER_PROVENANCE.post_only_own_target, LAYER_PROVENANCE.definition_lock_rest_claim],
      };
    } else if (Number.isInteger(candidate) && Number.isInteger(ask)) {
      envelopePlacement[legId] = {
        ...placement,
        active_target_before_cents: active,
        active_target_crossed_live_ask: Number.isInteger(active) && Number.isInteger(ask) && active >= ask,
        post_only_test: { target_cents: candidate, live_ask_cents: ask, lawful: candidate < ask, predicate: "TARGET_CENTS_LT_LIVE_ASK_CENTS" },
        post_only_disposition: candidate === active ? "NO_NEW_ORDER_EXISTING_REST" : "NEW_ORDER_POSTABLE",
        provenance: [...(Array.isArray(placement.provenance) ? placement.provenance : placement.provenance ? [placement.provenance] : []), LAYER_PROVENANCE.post_only_own_target],
      };
    }
  }
  if (!allocation.lawful) {
    const failedAllocation = allocation;
    const atomicTargets = {};
    const noLawfulReplacementLegs = [];
    const existingStandingPlan = openIds.map((legId) => cent(reads.half_pair_state.value.legs[legId].standing_target_cents));
    const existingStandingPlanLawful = sum(existingStandingPlan) <= base.PAR_BUDGET_CENTS;
    for (const legId of openIds) {
      const active = cent(reads.half_pair_state.value.legs[legId].standing_target_cents);
      const envelope = decisionEnvelopes[legId] ?? null;
      const ask = cent(reads.books.value[legId]?.ask_cents);
      const activeLicenseReceipt = reads.half_pair_state.value.legs[legId].standing_license_receipt;
      const activeStillLawful = Number.isInteger(active)
        && Boolean(activeLicenseReceipt)
        && existingStandingPlanLawful
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
    let target = cent(allocation.targets[legId]);
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
    if (pendingRearmBefore
      && !Number.isInteger(active)
      && Number.isInteger(pricingAuthorities[legId]?.target_cents)
      && !currentReceiptIsAskOnlyBookTick(state)) {
      const restorePrice = pricingAuthorities[legId].target_cents;
      const ask = cent(reads.books.value[legId]?.ask_cents);
      const criterion = survivorUpdate.legs[legId]?.target_criterion ?? null;
      const siblingId = state.leg_ids.find((id) => id !== legId);
      const siblingPlan = reads.half_pair_state.value.legs[siblingId].credited
        ? cent(reads.half_pair_state.value.legs[siblingId].entry_cents)
        : cent(allocation.targets[siblingId]);
      const restoreLawful = Number.isInteger(ask)
        && restorePrice < ask
        && criterionSupportsRangeLevel(criterion, restorePrice)
        && (!Number.isInteger(siblingPlan) || restorePrice + siblingPlan <= base.PAR_BUDGET_CENTS);
      if (restoreLawful) {
        target = restorePrice;
        allocation.targets[legId] = restorePrice;
        envelopePlacement[legId] = {
          ...envelopePlacement[legId],
          mode: "CANCEL_REARM_RESTORES_CURRENT_AUTHORITY_PRICE",
          writer_lane: "REARM_PRICE_RESTORATION_WRITER",
          restored_price_cents: restorePrice,
          stale_price_ignored_cents: pendingRearmBefore.last_cancelled_price_reference_cents ?? pendingRearmBefore.price_to_restore_cents ?? null,
          restored_price_license_receipt: state.receipt,
          chosen_target_cents: restorePrice,
          technique_contract: "C04_CANCEL_REARM_RESTORES_CURRENT_AUTHORITY_PRICE",
        };
      }
    }
    const placementMode = envelopePlacement[legId]?.mode;
    const reason = placementMode === "PRICING_AUTHORITY_TARGET_EXECUTED"
        ? "BASE_PRICING_AUTHORITY_EXECUTED_BY_LANE"
      : placementMode === "PRICING_AUTHORITY_SILENT_HOLD_EXISTING_REST"
        ? "PRICING_AUTHORITY_SILENT_EXISTING_REST_HELD"
      : placementMode === "PRICING_AUTHORITY_SILENT_NO_PLACEMENT"
        ? "PRICING_AUTHORITY_SILENT_NO_PLACEMENT"
      : placementMode === "LOCKED_BOOK_PLACEMENT_VETO_EXISTING_REST_HELD"
        ? "LOCKED_BOOK_PLACEMENT_ONLY_EXISTING_REST_HELD"
      : placementMode === "LOCKED_BOOK_PLACEMENT_VETO_NO_REST"
        ? "LOCKED_BOOK_PLACEMENT_ONLY_NO_REST"
      : placementMode === "CANCEL_REARM_RESTORES_CURRENT_AUTHORITY_PRICE"
        ? "CANCEL_REARM_RESTORES_CURRENT_AUTHORITY_PRICE"
      : placementMode === "POST_ONLY_BLOCKED_NEW_TARGET_HOLD_EXISTING_POSTABLE_REST"
        ? "POST_ONLY_BLOCKED_NEW_TARGET_HOLD_EXISTING_POSTABLE_REST"
      : placementMode === "CONTINUOUS_POST_ONLY_CANCEL_CROSSED_STANDING_REST"
        ? "CONTINUOUS_POST_ONLY_CANCEL_CROSSED_STANDING_REST"
      : placementMode === "EXACT_EVIDENCED_FLOOR_REST_HELD_AGAINST_MOVE_AWAY"
      ? "EXACT_EVIDENCED_FLOOR_REST_HELD_AGAINST_MOVE_AWAY"
      : placementMode === "FLOOR_CAPABLE_OWN_BOOK_LEVEL_BELOW_PRIOR_TRADE_LOW"
        ? "FLOOR_CAPABLE_OWN_BOOK_LEVEL_BELOW_PRIOR_TRADE_LOW"
      : placementMode === "OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED"
        ? "DISAGREES_STATED_OWN_EVIDENCE_SURVIVOR_SUPPORTED"
        : noLawfulReplacement
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
    const explicitWriter = envelopePlacement[legId]?.writer_lane ?? null;
    const derivedWinner = !Number.isInteger(target) && !Number.isInteger(active)
      ? "NO_ACTION"
      : placementMode === "EXACT_EVIDENCED_FLOOR_REST_HELD_AGAINST_MOVE_AWAY"
        ? "LICENSED_FLOOR_TENURE"
      : placementMode === "POST_ONLY_BLOCKED_NEW_TARGET_HOLD_EXISTING_POSTABLE_REST"
        ? "ACTIVE_REST_HOLD"
        : placementMode === "CANCEL_REARM_RESTORES_CURRENT_AUTHORITY_PRICE"
          ? "REARM_PRICE_RESTORATION_WRITER"
          : explicitWriter
            ?? (Number.isInteger(active) && target === active ? "ACTIVE_REST_HOLD" : "NO_ACTION");
    const laneEligibility = {
      COHERENT_ENVELOPE_WRITER: Boolean(coherentNow && decisionEnvelopes[legId] && pricingAuthorities[legId]?.base_target_lawful),
      FLOOR_CAPABLE_WRITER: Boolean(coherence.status === "DISAGREES" || envelopePlacement[legId]?.floor_handoff_same_receipt),
      CARRIED_CONVICTION_WRITER: Boolean(decisionEnvelopes[legId] && !coherentNow && coherence.status !== "DISAGREES"),
      OWN_TOUCH_WRITER: Boolean(!decisionEnvelopes[legId] && coherence.status !== "DISAGREES" && pricingAuthorities[legId]?.base_target_lawful),
      LICENSED_FLOOR_TENURE: placementMode === "EXACT_EVIDENCED_FLOOR_REST_HELD_AGAINST_MOVE_AWAY",
      REARM_PRICE_RESTORATION_WRITER: placementMode === "CANCEL_REARM_RESTORES_CURRENT_AUTHORITY_PRICE",
      ACTIVE_REST_HOLD: Number.isInteger(active) && target === active,
      POST_ONLY_CONTINUOUS_VETO: placementMode === "CONTINUOUS_POST_ONLY_CANCEL_CROSSED_STANDING_REST",
      NO_ACTION: !Number.isInteger(target) && !Number.isInteger(active),
    };
    laneEligibility[derivedWinner] = true;
    const winningLane = derivedWinner;
    const decisionArbitration = {
      decision_instant_epoch: state.current_epoch,
      source_receipt: state.receipt,
      winner: { lane: winningLane, action: action.action, target_cents: action.target_cents, reason: action.reason },
      losers: Object.entries(laneEligibility).filter(([lane]) => lane !== winningLane).map(([lane, eligible]) => ({ lane, eligible, disposition: eligible ? "LOST_PRECEDENCE_TO_WINNER" : "INELIGIBLE_AT_RECEIPT" })),
      emitted_order_count: ["PLACE_REST", "REPRICE_REST", "CANCEL_REST"].includes(action.action) ? 1 : 0,
      winner_regenerated_from_lane_eligibility: laneEligibility[winningLane] === true,
      pricing_authority_target_cents: pricingAuthorities[legId]?.target_cents ?? null,
      lane_may_replace_authority: false,
    };
    const survivor = survivorUpdate.legs[legId];
    const evidencedFloor = cent(state.legs[legId].running_true_trade_low_cents);
    const evidencedFloorReceipt = evidencedFloor === null
      ? null
      : [...state.legs[legId].prints].reverse().find((print) => cent(print.price_cents) === evidencedFloor)?.receipt ?? null;
    const standingLicensedLevel = evidencedFloor;
    const standingLicensedReceipt = evidencedFloorReceipt;
    const floorSupportAlive = Number.isInteger(active) && criterionSupportsRangeLevel(survivor?.target_criterion, active) ? (survivor?.survivor_shapes ?? []) : [];
    const activeAtSupportedFloor = Boolean(Number.isInteger(active) && Number.isInteger(evidencedFloor) && active === evidencedFloor && evidencedFloorReceipt);
    const floorPrint = evidencedFloor === null
      ? null
      : [...state.legs[legId].prints].reverse().find((print) => cent(print.price_cents) === evidencedFloor) ?? null;
    const floorEstablishedOnCurrentReceipt = Boolean(floorPrint && floorPrint.timestamp_epoch === state.current_epoch);
    const continuousPostOnlyCancel = envelopePlacement[legId]?.mode === "CONTINUOUS_POST_ONLY_CANCEL_CROSSED_STANDING_REST";
    const sameReceiptFloorDeparture = Boolean(floorEstablishedOnCurrentReceipt
      && activeAtSupportedFloor
      && target !== active
      && !continuousPostOnlyCancel);
    // Continuous post-only is senior because a crossed maker rest is unlawful
    // to keep standing. Cancelling that rest does not falsify directional floor
    // tenure; it is the mandatory disposition of an unpostable order.
    const floorRestProtectionViolation = activeAtSupportedFloor && target !== active && !continuousPostOnlyCancel;
    const targetInsideCurrentEnvelope = Number.isInteger(target) && currentEnvelope && target >= currentEnvelope.low_cents && target <= currentEnvelope.high_cents;
    if (coherentNow && Number.isInteger(target) && !state.dual_belief.first_lawful_coherence_by_leg[legId]) {
      state.dual_belief.first_lawful_coherence_by_leg[legId] = { epoch: state.current_epoch, receipt: state.receipt };
    }
    const firstLawfulCoherence = state.dual_belief.first_lawful_coherence_by_leg[legId] ?? null;
    const placementAtCurrentCoherence = coherentNow && Number.isInteger(target) && ["PLACE_REST", "REPRICE_REST", "HOLD_REST"].includes(action.action);
    const carriedPlacement = envelopePlacement[legId]?.mode === "CARRIED_PRIOR_RECEIPT_CONVICTION_Q75_BASIS_RESTATED" && ["PLACE_REST", "REPRICE_REST"].includes(action.action);
    const disagreesOwnEvidencePlacement = ["OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED", "FLOOR_CAPABLE_OWN_BOOK_LEVEL_BELOW_PRIOR_TRADE_LOW"].includes(envelopePlacement[legId]?.mode) && ["PLACE_REST", "REPRICE_REST"].includes(action.action);
    const observedFloorPlacement = ["SAME_RECEIPT_ESTABLISHED_FLOOR_GOVERNS", "POST_ONLY_BLOCKED_NEW_TARGET_HOLD_EXISTING_POSTABLE_REST"].includes(envelopePlacement[legId]?.mode)
      && ["PLACE_REST", "REPRICE_REST", "HOLD_REST"].includes(action.action);
    const envelopeConsistency = {
      active_inconsistent_before_action: Boolean(activeInconsistent),
      resolution: !activeInconsistent ? "ACTIVE_CONSISTENT_OR_NO_CURRENT_ENVELOPE" : targetInsideCurrentEnvelope ? "CANCEL_AND_REPLACE_ATOMIC_SAME_RECEIPT" : action.action === "CANCEL_REST" ? "FAIL_LOUD_NO_LAWFUL_REPLACEMENT" : "VIOLATION_STALE_REST_SURVIVED",
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
      disagrees_own_evidence_originated_or_repriced_rest: disagreesOwnEvidencePlacement,
      observed_floor_originated_repriced_or_held_rest: observedFloorPlacement,
      live_touch_originated_new_rest: !coherentNow && !Number.isInteger(active) && action.action === "PLACE_REST" && String(envelopePlacement[legId]?.mode ?? "").startsWith("CONSUME_OWN_EVIDENCED_LIVE_TOUCH"),
      provenance: [LAYER_PROVENANCE.coherence_placement_fix, LAYER_PROVENANCE.carried_conviction],
    };
    let rearmReceipt;
    if (action.action === "CANCEL_REST" && Number.isInteger(active)) {
      const prior = pendingRearmBefore;
      rearmReceipt = {
        status: "REARM_PENDING",
        armed_at_epoch: prior?.armed_at_epoch ?? state.current_epoch,
        armed_at_receipt: prior?.armed_at_receipt ?? state.receipt,
        latest_attempt_epoch: state.current_epoch,
        latest_attempt_receipt: state.receipt,
        attempts: (prior?.attempts ?? 0) + 1,
        trigger: noLawfulReplacement ? envelopeConsistency.no_lawful_replacement_reason : "ORDINARY_BOOK_CANCEL_WITHOUT_SAME_RECEIPT_REPLACEMENT",
        last_cancelled_price_reference_cents: prior?.last_cancelled_price_reference_cents ?? active,
        price_license_receipt: prior?.price_license_receipt ?? reads.half_pair_state.value.legs[legId].standing_license_receipt ?? null,
        restores_price_not_merely_rest: true,
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
      rearmReceipt = { status: "NO_REARM_PENDING_OR_TRIGGERED", attempts: 0, permanent_silence_allowed: false, provenance: LAYER_PROVENANCE.atomic_rearm_fix };
    }
    const floorRestProtection = {
      floor_rest_lock_state: Object.prototype.hasOwnProperty.call(state.dual_belief, "floor_rest_locks") ? "PRESENT_DEFECT" : "ABSENT_RETIRED",
      evidenced_floor_cents: evidencedFloor,
      evidenced_floor_source: evidencedFloor ? "OBSERVED_TRUE_TRADE_PRINT" : null,
      evidenced_floor_receipt: evidencedFloorReceipt,
      active_target_before_cents: active,
      active_was_at_evidenced_floor: Boolean(Number.isInteger(active) && Number.isInteger(evidencedFloor) && active === evidencedFloor && evidencedFloorReceipt),
      active_was_at_licensed_floor_level: activeAtSupportedFloor,
      licensed_floor_level_cents: standingLicensedLevel,
      licensed_floor_level_receipt: standingLicensedReceipt,
      supporting_shapes_still_alive: floorSupportAlive,
      proposed_target_before_protection_cents: envelopePlacement[legId]?.proposed_conflicting_target_cents ?? envelopePlacement[legId]?.chosen_target_cents ?? null,
      protected_from_conflicting_belief_or_cancel: envelopePlacement[legId]?.mode === "EXACT_EVIDENCED_FLOOR_REST_HELD_AGAINST_MOVE_AWAY",
      floor_established_on_current_receipt: floorEstablishedOnCurrentReceipt,
      same_receipt_floor_departure: sameReceiptFloorDeparture,
      same_receipt_floor_law_applied: false,
      postable_floor_rest_held_against_crossing_singleton: envelopePlacement[legId]?.mode === "POST_ONLY_BLOCKED_NEW_TARGET_HOLD_EXISTING_POSTABLE_REST",
      violation: floorRestProtectionViolation,
      tenure_instrument: "ORDER_TRANSITION_TENURE_SINGLE_PRODUCER",
      sampled_row_tenure_serialized: false,
      tenure_direction: "BLOCK_AWAY_NEVER_BLOCK_ONTO",
      continuous_post_only_seniority_applied: continuousPostOnlyCancel,
      provenance: [LAYER_PROVENANCE.floor_rest_protection, LAYER_PROVENANCE.directional_floor_tenure],
    };
    const proposalBeforeAllocation = cent(envelopePlacement[legId]?.proposed_conflicting_target_cents ?? envelopePlacement[legId]?.chosen_target_cents);
    const proposalAtOrBelowFloor = Number.isInteger(proposalBeforeAllocation) && Number.isInteger(evidencedFloor) && proposalBeforeAllocation <= evidencedFloor;
    const proposalAdmitted = proposalAtOrBelowFloor && Number.isInteger(target) && target <= evidencedFloor;
    const proposalSupervisor = {
      proposal_cents: proposalBeforeAllocation,
      evidenced_floor_cents: evidencedFloor,
      proposal_at_or_below_evidenced_floor: proposalAtOrBelowFloor,
      final_target_cents: target,
      status: !proposalAtOrBelowFloor
        ? "NO_AT_OR_BELOW_FLOOR_PROPOSAL"
        : proposalAdmitted
          ? "ADMITTED_AT_OR_BELOW_EVIDENCED_FLOOR"
          : activeAtSupportedFloor && target === active
            ? "HELD_EXISTING_EVIDENCED_FLOOR_REST"
            : "BLOCKED_OR_REFUSED_WITH_REASON",
      reason: !proposalAtOrBelowFloor
        ? "PROPOSAL_NOT_AT_OR_BELOW_CURRENT_EVIDENCED_FLOOR"
        : proposalAdmitted
          ? action.reason
          : activeAtSupportedFloor && target === active
            ? "CURRENT_EVIDENCED_FLOOR_REST_HAS_LIVE_SURVIVOR_SUPPORT"
            : `${allocation.reason}:${action.reason}`,
      supervisor_required: proposalAtOrBelowFloor,
      independent_check: {
        producer_store: "DERIVED_ACTION_AND_PAIR_ALLOCATION",
        check_store: evidencedFloorReceipt ? "OBSERVED_TRUE_TRADE_PRINT_RECEIPT" : "NO_OBSERVED_TRADE_FLOOR",
        check_receipt: evidencedFloorReceipt,
        can_fail: true,
        passed: !proposalAtOrBelowFloor || Boolean(action.reason && allocation.reason && evidencedFloorReceipt),
      },
      provenance: LAYER_PROVENANCE.proposal_supervisor,
    };
    const actionStatement = `ACTION=${action.action}; TARGET_CENTS=${action.target_cents ?? "NONE"}; ACTIVE_TARGET_BEFORE_CENTS=${active ?? "NONE"}.`;
    const upstream = `MACRO=${macroStatus}[${macroReceipt.receipt_id}] · MICRO=${microStatus}[${microReceipt.receipt_id}] · MICRO_MICRO=${microMicroStatus}[${microMicroReceipt.receipt_id}]`;
    const beliefText = dualPlain.length ? `${dualPlain[0]} || SIBLING-INVERSE: ${dualPlain[1]}` : "DUAL_BELIEF=INSUFFICIENT_EVIDENCE";
    const fillHandoffId = baseRows.get(legId).derivation.fill_handoff_receipt_id;
    const fillHandoff = fillHandoffId ? baseRows.get(legId).citation_receipts[fillHandoffId] : null;
    const fillHandoffText = fillHandoff
      ? ` FILL_HANDOFF=${fillHandoff.context.original_fill_receipt}[${fillHandoff.receipt_id}]; CREDITED_SIBLING_ENTRY=${fillHandoff.context.credited_sibling_entry_cents}; REPOSED_QUERY=${fillHandoff.context.reposed_query_fingerprint_sha256}.`
      : "";
    const floorCriterion = survivor?.target_criterion ?? null;
    const allocationBound = allocation.par_allocation_floor_bounds?.[legId] ?? parAllocationFloorBounds[legId] ?? null;
    const authorChainText = `PRIOR_${pricingAuthorities[legId]?.conditioning_chain?.prior_cents ?? "NONE"}_TO_CONDITIONED_${pricingAuthorities[legId]?.conditioning_chain?.conditioned_cents ?? "NONE"}_TO_LEVEL_${pricingAuthorities[legId]?.conditioning_chain?.final_level_cents ?? "NONE"}`;
    const sentence = `${beliefText}. MACRO: family=${macroFamilies[legId].family}, SURVIVOR_SHAPES=${JSON.stringify(survivorUpdate.legs[legId])}, conditioned-total-dip=${JSON.stringify(conditionedPriors[legId]?.conditioned_total_dip_distribution_cents ?? null)}, arrived-dip=${JSON.stringify(conditionedPriors[legId]?.arrived_dip_distribution_cents ?? null)}, remaining-dip=total-minus-arrived=${JSON.stringify(conditionedPriors[legId]?.remaining_dip_distribution_cents ?? null)}, conditioning-method=${conditionedPriors[legId]?.method ?? "NONE"}, stores=${coarseNeighbors.map((neighbor) => `${neighbor.quality}/${neighbor.grain ?? "UNKNOWN"}@${neighbor.citation_receipt_id}`).join(",") || "NONE"} [${macroReceipt.receipt_id}]. MICRO: own-window=${JSON.stringify(beliefs[legId]?.own_evidence ?? null)}, rows=${[beliefs[legId]?.book_receipt, beliefs[legId]?.top_neighbor?.citation_receipt_id].filter(Boolean).join(",") || "NONE"}, V3_KEY=${LAYER_PROVENANCE.v3_source_key}->${LAYER_PROVENANCE.v3_runtime_rekey}, ENVELOPE_HIGH=${beliefs[legId]?.envelope_high_cents ?? "NONE"}@${beliefs[legId]?.envelope_high_basis ?? "NONE"}:${beliefs[legId]?.envelope_high_receipt ?? "NONE"} [${microReceipt.receipt_id}]. MICRO-MICRO: tick=${state.receipt}, book=${beliefs[legId]?.book_receipt ?? "NONE"}, store=${LAYER_PROVENANCE.micro_micro_store} [${microMicroReceipt.receipt_id}]. ORDER=${upstream}. COHERENCE=${coherence.status}; MIRROR_GAP=${coherence.absolute_mirror_gap_cents ?? "UNKNOWN"}; SPREAD_BOUND=${spread ?? "UNKNOWN"}/${SPREAD_SETTLE_COHERENCE_MAX_CENTS}; OBSERVED_TRADED_FLOOR=${evidencedFloor ?? "NONE"}@${evidencedFloorReceipt ?? "NONE"}; AUTHOR_CHAIN=${authorChainText}; PRICING_AUTHORITY=${JSON.stringify(pricingAuthorities[legId])}; WRITER_LANE=${decisionArbitration.winner.lane}; SENIORITY_CONTRACT=${envelopePlacement[legId]?.technique_contract ?? "C01_PRICING_AUTHORITY_OVER_LANE_LEVEL_SELECTION"}; SPREAD_EYE=${JSON.stringify(spreadEyes[legId])}; TRADED_LOW_TARGET_CRITERION=${JSON.stringify(floorCriterion)}; NON_TRADED_LOW_DISCLOSURE=${beliefs[legId]?.own_evidence?.non_traded_low_disclosure ?? "NOT_CONSUMED"}; CONVICTION_EVOLUTION=${JSON.stringify(convictionEvolution[legId])}; FLOOR_REST_PROTECTION=${JSON.stringify(floorRestProtection)}; PROPOSAL_SUPERVISOR=${JSON.stringify(proposalSupervisor)}; DECISION_ARBITRATION=${JSON.stringify(decisionArbitration)}; PAR_ALLOCATION_FLOOR_BOUND=${JSON.stringify(allocationBound)}; PAR_ALLOCATION_HEADROOM_CENTS=${allocation.headroom_cents?.[legId] ?? "NONE"}; ENVELOPE=${JSON.stringify(currentEnvelope)}; ENVELOPE_PLACEMENT=${JSON.stringify(envelopePlacement[legId])}; ALLOCATION=${allocation.reason}.${fillHandoffText} ${actionStatement}`;
    row.citation_receipts[macroReceipt.receipt_id] = macroReceipt;
    row.citation_receipts[microReceipt.receipt_id] = microReceipt;
    row.citation_receipts[microMicroReceipt.receipt_id] = microMicroReceipt;
    row.action = action;
    row.sentence = sentence;
    row.sentence_action_assertion = { hard_assert: true, expected_statement: actionStatement, equal: sentence.includes(actionStatement) };
    row.citation_receipt_assertion = { hard_assert: true, receipt_count: Object.keys(row.citation_receipts).length, equal: [macroReceipt, microReceipt, microMicroReceipt].every((receipt) => sentence.includes(receipt.receipt_id)) };
    row.layered_dual_belief = { macro: { status: macroStatus, families: macroFamilies, survivor_shapes: survivorUpdate, conditioned_priors: conditionedPriors, receipt_id: macroReceipt.receipt_id }, micro: { status: microStatus, beliefs, receipt_id: microReceipt.receipt_id }, micro_micro: { status: microMicroStatus, receipt_id: microMicroReceipt.receipt_id }, coherence, belief_mode: beliefMode, conviction_evolution: convictionEvolution[legId], carried_conviction_consumed_for_action: carriedPlacement, independent_lane_license: [LAYER_PROVENANCE.consume_live_touch_fix, LAYER_PROVENANCE.own_evidence_sufficiency, LAYER_PROVENANCE.disagrees_own_evidence_release], pricing_authority: pricingAuthorities[legId], spread_eye: spreadEyes[legId], technique_contracts: TECHNIQUE_CONTRACTS, decision_arbitration: decisionArbitration, atomic_rearm: rearmReceipt, first_coherence: state.dual_belief.first_coherence, envelope_history_count: state.dual_belief.envelope_history.length, envelope_migration_at_receipt: envelopeMigrations[legId] ?? null, envelope_consistency: envelopeConsistency, coherence_placement: coherencePlacement, floor_rest_protection: floorRestProtection, proposal_supervisor: proposalSupervisor, par_allocation_floor_bound: allocationBound, envelope: currentEnvelope, envelope_placement: envelopePlacement[legId], v3_keying_fix: beliefs[legId]?.v3_map_semantics ?? null };
    delete row.derivation.stale_prior_path_used;
    row.derivation.carried_conviction = convictionEvolution[legId];
    row.derivation.target_basis = reason;
    row.derivation.target_authority = placementMode === "POST_ONLY_BLOCKED_NEW_TARGET_HOLD_EXISTING_POSTABLE_REST"
        ? "CAPTURED_REST_LEVEL_HELD_POST_ONLY_NOT_A_FLOOR_PRODUCER"
      : placementMode === "EXACT_EVIDENCED_FLOOR_REST_HELD_AGAINST_MOVE_AWAY"
        ? "OBSERVED_TRUE_TRADE_FLOOR_TENURE"
        : placementMode === "CANCEL_REARM_RESTORES_CURRENT_AUTHORITY_PRICE"
          ? "CURRENT_AUTHORITY_PRICE_RESTORED"
          : "BASE_V3_MAP_JOINT_DEPTH_MIND_WINDOW_PRICING_AUTHORITY";
    row.derivation.pricing_authority = pricingAuthorities[legId];
    row.derivation.spread_eye = spreadEyes[legId];
    row.derivation.derived_target_cents = target;
    row.derivation.allocation = allocation;
    const authorityTargetAtReceipt = cent(pricingAuthorities[legId]?.target_cents);
    const authorityDiverged = Number.isInteger(authorityTargetAtReceipt) && target !== authorityTargetAtReceipt;
    const seniorAuthorityReason = authorityDiverged
      ? rearmReceipt?.status === "REARM_PENDING"
        ? "C04_PAIR_CONSERVATION_CANCEL_REARM_PENDING"
        : rearmReceipt?.status === "REARM_RESOLVED_WITH_LAWFUL_REST"
          ? "C04_CANCEL_REARM_RESTORES_PRICE"
          : envelopePlacement[legId]?.technique_contract !== "C01_PRICING_AUTHORITY_OVER_LANE_LEVEL_SELECTION"
            ? envelopePlacement[legId]?.technique_contract
            : allocation.fill_handoff_veto
              ? "PAIR_CAP_FILL_HANDOFF_VETO"
              : Number.isInteger(allocation.excess_cents)
                && allocation.excess_cents > 0
                && cent(allocation.rejected_candidate_targets?.[legId]) === authorityTargetAtReceipt
                && cent(allocation.targets?.[legId]) === target
                ? "PAIR_CONSERVATION_ALLOCATION"
              : allocation.reason?.includes("JOINT_TARGET") || allocation.reason?.includes("PAIR_ALLOCATION")
                ? "PAIR_CONSERVATION_ALLOCATION"
                : null
      : null;
    row.derivation.authority_target_divergence = {
      authority_target_cents: authorityTargetAtReceipt,
      final_target_cents: target,
      diverged: authorityDiverged,
      licensed_senior: !authorityDiverged || Boolean(seniorAuthorityReason),
      senior_authority_reason: seniorAuthorityReason,
    };
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
  TECHNIQUE_CONTRACTS,
  PHASE_CENTRAL_BANDS,
  configurePhaseCentralSurface,
  configureSurvivorShapeLibraries: survivorShapes.configureSurvivorShapeLibraries,
  chooseEnvelopePlacementTarget,
  spreadEyeForLeg,
  pricingAuthorityForLeg,
  deriveJointActions,
};
