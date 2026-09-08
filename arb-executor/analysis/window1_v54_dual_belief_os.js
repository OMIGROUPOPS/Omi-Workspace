"use strict";

// Pool cascade authorship. Legacy fixture helpers below never write an order.
const base = require("./window1_v54_functionable_os.js");
const survivorShapes = require("./window1_v54_survivor_shape_elimination.js");
const CONTRACT_SUM_CENTS = 100;
const SPREAD_SETTLE_COHERENCE_MAX_CENTS = 20;
const LAYER_PROVENANCE = Object.freeze({ pool_cascade: "CAUSAL_MEMBER_FLOORS_FIXED_ATLAS_RECEIPT_ROLES", floor_print_decision_instant: "INHERITED_TRUE_PRINT_DECISION_INSTANT", book_veto_only: "BOOK_VETO_ONLY_NOT_A_LEVEL_WRITER" });
const TECHNIQUE_CONTRACTS = Object.freeze([{ id: "C01_PRICING_AUTHORITY_OVER_LANE_LEVEL_SELECTION", state: "FIRED_OR_PRICED", method: "FIRST-TICK-ONLY then BASE; no lane substitutes a level" }, { id: "POOL_STEP_TELEMETRY", state: "LATENT_REGISTERED", method: "STEP-FORECAST never authors without receipt activation" }]);
const PHASE_CENTRAL_BANDS = Object.freeze([]);
function configurePhaseCentralSurface(binding) { if (!binding) throw new Error("MISSING_LEGACY_DIAGNOSTIC_BINDING"); }
const configureNeighborSpecialistBinding = base.configureNeighborSpecialistBinding;

function finite(value) { return Number.isFinite(value) ? value : null; }
function cent(value) { return Number.isInteger(value) && value >= 1 && value <= 99 ? value : null; }
function sum(values) { return values.filter(Number.isFinite).reduce((a, b) => a + b, 0); }
function predictionSeatImmunityDecision({ proposed_target_cents = null, mover = "NONE" }) {
  // Compatibility for the builder's retired-seat diagnostic fixture only.
  // A seat no longer chooses, changes, or freezes a level.
  return { disposition: "RETIRED_AS_LEVEL_WRITER", target_cents: proposed_target_cents, mover };
}

function predictionSeatEvidenceDelta(priorSnapshot, currentSnapshot) {
  if (!priorSnapshot) return { changed: true, named_non_book_sources: ["INITIAL_NON_BOOK_CONVICTION"] };
  const named = [];
  if (priorSnapshot.evidenced_floor_receipt !== currentSnapshot.evidenced_floor_receipt) named.push("TRUE_PRINT_FLOOR_RECEIPT");
  if (priorSnapshot.decisive_evidence_receipt !== currentSnapshot.decisive_evidence_receipt) named.push("DECISIVE_NON_BOOK_EVIDENCE_RECEIPT");
  if (priorSnapshot.non_book_evidence_signature !== currentSnapshot.non_book_evidence_signature) named.push("NON_BOOK_EVIDENCE_SET");
  if (priorSnapshot.panel_signature !== currentSnapshot.panel_signature) named.push("PANEL_CHANGE");
  if (priorSnapshot.credited_sibling_fill_receipt !== currentSnapshot.credited_sibling_fill_receipt) named.push("CREDITED_SIBLING_FILL");
  if (JSON.stringify(priorSnapshot.supporting_shape_ids ?? []) !== JSON.stringify(currentSnapshot.supporting_shape_ids ?? [])) named.push("SURVIVOR_OR_ELIMINATION_CHANGE");
  return {
    changed: named.length > 0,
    named_non_book_sources: named,
    book_cursor_considered: false,
    bid_or_ask_change_considered: false,
    book_may_license_level_change: false,
    provenance: LAYER_PROVENANCE.book_veto_only,
  };
}

function bookVetoOnlyDecision({ prior_snapshot, current_snapshot, standing_target_cents, proposed_target_cents, live_ask_cents }) {
  const evidence = predictionSeatEvidenceDelta(prior_snapshot, current_snapshot);
  const proposed = cent(proposed_target_cents);
  const standing = cent(standing_target_cents);
  const ask = cent(live_ask_cents);
  const updateLicensed = evidence.changed && Number.isInteger(proposed);
  const candidate = updateLicensed ? proposed : standing;
  const postable = Number.isInteger(candidate) && Number.isInteger(ask) && candidate < ask;
  return {
    update_licensed: updateLicensed,
    named_non_book_evidence_sources: evidence.named_non_book_sources,
    candidate_level_cents: candidate,
    standing_level_cents: standing,
    proposed_non_book_level_cents: proposed,
    live_ask_cents: ask,
    book_disposition: postable ? "POSTABLE" : "VETO",
    book_transformed_level: false,
    book_licensed_change: false,
    book_cursor_considered: false,
    provenance: LAYER_PROVENANCE.book_veto_only,
  };
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

function weightedModeFloorSideCents(rows) {
  const massByCent = new Map();
  for (const row of rows) {
    const level = cent(row.licensed_floor_cents);
    const weight = finite(row.conditioning_weight);
    if (!Number.isInteger(level) || !Number.isFinite(weight) || weight <= 0) continue;
    massByCent.set(level, (massByCent.get(level) ?? 0) + weight);
  }
  return [...massByCent.entries()]
    .sort((a, b) => b[1] - a[1] || a[0] - b[0])[0]?.[0] ?? null;
}

function actionForTarget(active, target, reason) {
  if (!cent(target)) return { action: active ? "CANCEL_REST" : "HOLD_REST", target_cents: null, reason };
  if (!active) return { action: "PLACE_REST", target_cents: target, reason };
  if (active === target) return { action: "HOLD_REST", target_cents: target, reason };
  return { action: "REPRICE_REST", target_cents: target, reason };
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
function conditionPriorDistribution({ side, layer }) {
  const selected = layer ? side?.layers?.[layer] : null;
  return { method: "MEMBER_REMAINING_MINIMUM_WEIGHTED_QUANTILES", selected_layer: layer,
    conditioned: selected?.status === "OK", quantiles: selected?.floors ?? null,
    posterior_q50_cents: selected?.floors?.q50?.level_cents ?? null,
    member_count: selected?.member_count ?? null, ess: selected?.ess ?? null,
    weight_sum: selected?.weight_sum ?? null, family_distribution: selected?.family ?? null };
}
function pricingAuthorityForLeg({ pool, legId }) {
  const side = pool.sides?.[legId], layer = side?.selected_layer ?? null;
  const conditioning = conditionPriorDistribution({ side, layer });
  const target = conditioning.conditioned ? cent(conditioning.quantiles?.q50?.level_cents) : null;
  return { authority_source: layer ? `POOL_CASCADE:${layer}` : "INSUFFICIENT_EVIDENCE",
    target_cents: target, effective_target_cents: target, true_conditioning: conditioning,
    base_target_lawful: Number.isInteger(target), own_evidence_rows: [], panel_rows: [],
    conditioning_chain: { prior_cents: null, conditioned_cents: target, final_level_cents: target },
    book_role: "VETO_ONLY_NOT_PRICE_AUTHOR" };
}
function freshDeadline(state, authority) {
  const floor = authority.true_conditioning.quantiles?.q50;
  return { deadline_epoch: floor?.epoch ?? null, predicted_minutes_to_bell: floor?.minutes_to_bell ?? null,
    emitted_at_epoch: state.current_epoch, emitted_at_receipt: state.receipt,
    source: authority.true_conditioning.selected_layer ? `POOL_${authority.true_conditioning.selected_layer}_FLOOR_MTB` : "INSUFFICIENT_EVIDENCE",
    stale_modeled_deadline_clamped_to_emission: false };
}
function deriveJointActions({ state, reads, resources }) {
  base.assertResources(resources);
  state.dual_belief ??= { first_coherence: null, rearm_by_leg: {}, coherence_history: [] };
  const ids = state.leg_ids, pool = base.poolSnapshot(state);
  const formationComplete = ids.every(id => Number.isFinite(state.legs[id].formation_end_epoch) && state.current_epoch >= state.legs[id].formation_end_epoch);
  const authorities = Object.fromEntries(ids.map(legId => [legId, pricingAuthorityForLeg({ pool, legId })]));
  const beliefs = Object.fromEntries(ids.map(id => {
    const authority = authorities[id], side = pool.sides?.[id], layer = side?.selected_layer;
    const selected = layer ? side.layers[layer] : null;
    const resolved = formationComplete && selected?.status === "OK" && Number.isInteger(authority.target_cents);
    const deadline = freshDeadline(state, authority);
    const belief = { status: resolved ? "RESOLVED" : "INSUFFICIENT_EVIDENCE", belief_price_cents: side?.current_last_cents ?? null,
      current_cents: side?.current_last_cents ?? null,
      predicted_cents: resolved ? authority.target_cents : null,
      predicted_minutes_to_bell: resolved ? deadline.predicted_minutes_to_bell : null,
      q_author: resolved ? `POOL_${layer}` : "INSUFFICIENT_EVIDENCE",
      x_author: resolved ? `POOL_${layer}_FLOOR_MTB` : "INSUFFICIENT_EVIDENCE",
      family: selected?.family?.top ?? null, family_distribution: selected?.family ?? null,
      pool_cascade: side ?? null, deadline, book_receipt: reads.books.value[id]?.receipt ?? null,
      own_evidence: { formation_end_epoch: state.legs[id].formation_end_epoch, observed_traded_low_cents: state.legs[id].running_true_trade_low_cents,
        observed_traded_high_cents: state.legs[id].running_true_trade_high_cents, basis: "TRUE_TRADE_RECEIPTS", non_traded_low_consumed: false },
      candidate_level_q25_cents: selected?.floors?.q25?.level_cents ?? null,
      candidate_level_q75_cents: selected?.floors?.q75?.level_cents ?? null };
    belief.plain_sentence = resolved
      ? `${id} is ${belief.belief_price_cents}¢ now; ${layer} writes Q ${belief.predicted_cents}¢ by ${belief.predicted_minutes_to_bell} minutes to bell. ${selected.member_count} members, weight ${selected.weight_sum}, ESS ${selected.ess}. STEP-FORECAST is pile telemetry only.`
      : `${id}: INSUFFICIENT_EVIDENCE; no pool layer may write a new bid.`;
    return [id, belief];
  }));
  const resolved = ids.every(id => beliefs[id].status === "RESOLVED");
  const spread = finite(reads.joint_state_spread_dwell.value.spread_sum_cents);
  const predictedSum = resolved ? sum(ids.map(id => beliefs[id].predicted_cents)) : null;
  const hasBooks = ids.every(id => Boolean(reads.books.value[id]?.receipt));
  const microMicroResolved = resolved && hasBooks;
  const coherent = microMicroResolved && Number.isInteger(predictedSum) && Number.isFinite(spread) && spread <= SPREAD_SETTLE_COHERENCE_MAX_CENTS && Math.abs(predictedSum - CONTRACT_SUM_CENTS) <= spread;
  const coherence = { timestamp_epoch: state.current_epoch, receipt: state.receipt,
    status: coherent ? "COHERENT" : microMicroResolved ? "DISAGREES" : "INSUFFICIENT_EVIDENCE",
    predicted_sum_cents: predictedSum, contract_sum_cents: CONTRACT_SUM_CENTS,
    absolute_mirror_gap_cents: predictedSum === null ? null : Math.abs(predictedSum - CONTRACT_SUM_CENTS),
    spread_settle_bound_cents: spread, spread_settle_max_cents: SPREAD_SETTLE_COHERENCE_MAX_CENTS };
  if (coherent && !state.dual_belief.first_coherence) state.dual_belief.first_coherence = { epoch: state.current_epoch, receipt: state.receipt };
  state.dual_belief.coherence_history.push(coherence);
  const references = Object.values(pool.binding ?? {}).flatMap(value => value?.sha256 ? [`${value.path}@sha256:${value.sha256}`] : []);
  const macro = layerReceipt(state, "MACRO", pool.status === "BOUND" ? "RESOLVED" : "INSUFFICIENT_EVIDENCE", references, {
    pool_cascade: pool, families: Object.fromEntries(ids.map(id => [id, { family: beliefs[id].family }])),
    survivor_shapes: null, step_author_role: pool.step_author_role });
  const micro = layerReceipt(state, "MICRO", resolved ? "RESOLVED" : "INSUFFICIENT_EVIDENCE", references, { beliefs });
  const microMicro = layerReceipt(state, "MICRO_MICRO", microMicroResolved ? "RESOLVED" : "INSUFFICIENT_EVIDENCE", [state.receipt, ...ids.map(id => reads.books.value[id]?.receipt)], { tick_state: reads.books.value });
  const targets = {}, modes = {}, postability = {};
  for (const id of ids) {
    const position = state.positions[id], active = cent(position.standing_target_cents), q = beliefs[id].predicted_cents;
    const book = reads.books.value[id], ask = cent(book?.ask_cents), bid = cent(book?.bid_cents);
    const formed = Number.isFinite(state.legs[id].formation_end_epoch) && state.current_epoch >= state.legs[id].formation_end_epoch;
    const locked = Number.isInteger(bid) && Number.isInteger(ask) && bid >= ask;
    const prior = state.dual_belief.last_postability?.[id];
    const becamePostable = Number.isInteger(q) && Number.isInteger(ask) && q < ask && prior?.target_cents === q && prior?.postable === false;
    postability[id] = { target_cents: q, postable: Number.isInteger(q) && Number.isInteger(ask) && q < ask };
    let target = q, mode = "PRICING_AUTHORITY_TARGET_EXECUTED";
    if (position.credited) { target = null; mode = "CREDITED_LEG_READ_ONLY"; }
    else if (!formed) { target = null; mode = "FORMATION_NOT_COMPLETE_NO_PLACEMENT"; }
    else if (locked) { target = active; mode = "LOCKED_BOOK_PLACEMENT_ONLY_EXISTING_REST_HELD"; }
    else if (!Number.isInteger(q)) { target = active; mode = "INSUFFICIENT_AUTHORITY_HOLD_STANDING_LAWFUL_REST"; }
    else if (currentReceiptIsAskOnlyBookTick(state) && !becamePostable) { target = active; mode = "ASK_ONLY_TICK_VETO_HOLD_STANDING_LAWFUL_REST"; }
    else if (!Number.isInteger(ask) || q >= ask) {
      const standingPostable = Number.isInteger(active) && Number.isInteger(ask) && active <= ask;
      target = standingPostable ? active : null;
      mode = standingPostable ? "POST_ONLY_BLOCKED_NEW_TARGET_HOLD_EXISTING_POSTABLE_REST" : "POST_ONLY_BLOCKED_NO_EXISTING_POSTABLE_REST";
    }
    targets[id] = target; modes[id] = mode;
  }
  state.dual_belief.last_postability = postability;
  const planSum = sum(ids.map(id => state.positions[id].credited ? state.positions[id].entry_cents : targets[id]));
  const pairBlocked = planSum > base.PAR_BUDGET_CENTS;
  if (pairBlocked) for (const id of ids.filter(id => !state.positions[id].credited)) {
    targets[id] = cent(state.positions[id].standing_target_cents); modes[id] = "PAIR_CONSERVATION_SKIP_NEW_REST_HOLD_AND_CONTINUE";
  }
  const allocation = { targets, lawful: sum(ids.map(id => state.positions[id].credited ? state.positions[id].entry_cents : targets[id])) <= base.PAR_BUDGET_CENTS,
    reason: pairBlocked ? "PAIR_CONSERVATION_SKIP_NEW_REST_HOLD_AND_CONTINUE" : "POOL_Q_UNCHANGED_POST_ONLY_AND_PAIR_VETO", mode: "VETO_ONLY_NOT_PRICE_AUTHOR" };
  const derivations = ids.map(id => {
    const position = state.positions[id], active = cent(position.standing_target_cents), target = targets[id], mode = modes[id];
    const action = actionForTarget(active, target, mode);
    const pending = state.dual_belief.rearm_by_leg[id];
    let rearm;
    if (action.action === "CANCEL_REST" && active !== null) {
      rearm = { status: "REARM_PENDING", armed_at_epoch: pending?.armed_at_epoch ?? state.current_epoch,
        armed_at_receipt: pending?.armed_at_receipt ?? state.receipt, attempts: (pending?.attempts ?? 0) + 1,
        last_cancelled_price_reference_cents: active, latest_attempt_epoch: state.current_epoch, latest_attempt_receipt: state.receipt };
      state.dual_belief.rearm_by_leg[id] = rearm;
    } else if (pending && target !== null) {
      rearm = { ...pending, status: "REARM_RESOLVED_WITH_LAWFUL_REST", resolved_at_epoch: state.current_epoch,
        resolved_at_receipt: state.receipt, replacement_target_cents: target, attempts: pending.attempts + 1 };
      delete state.dual_belief.rearm_by_leg[id];
    } else if (pending) {
      rearm = { ...pending, latest_attempt_epoch: state.current_epoch, latest_attempt_receipt: state.receipt, attempts: pending.attempts + 1 };
      state.dual_belief.rearm_by_leg[id] = rearm;
    } else rearm = { status: "NO_REARM_PENDING_OR_TRIGGERED", attempts: 0 };
    const side = pool.sides?.[id], selected = side?.selected_layer ? side.layers[side.selected_layer] : null;
    const lane = mode === "PRICING_AUTHORITY_TARGET_EXECUTED" ? "POOL_CASCADE_WRITER" : active !== null && target === active ? "ACTIVE_REST_HOLD" : "NO_ACTION";
    const arbitration = { decision_instant_epoch: state.current_epoch, source_receipt: state.receipt,
      winner: { lane, ...action }, losers: [{ lane: "STEP-FORECAST", eligible: false, disposition: "PILE_TELEMETRY_NOT_AN_AUTHOR" }],
      emitted_order_count: ["PLACE_REST", "REPRICE_REST", "CANCEL_REST"].includes(action.action) ? 1 : 0,
      pricing_authority_target_cents: authorities[id].target_cents, lane_may_replace_authority: false };
    const placement = { mode, writer_lane: lane, active_target_before_cents: active, chosen_target_cents: target,
      post_only_test: { target_cents: authorities[id].target_cents, live_ask_cents: reads.books.value[id]?.ask_cents ?? null, lawful: postability[id].postable },
      post_only_role: "VETO_ONLY_NOT_PRICE_AUTHOR", technique_contract: "C01_PRICING_AUTHORITY_OVER_LANE_LEVEL_SELECTION" };
    const citations = Object.fromEntries([macro, micro, microMicro].map(receipt => [receipt.receipt_id, receipt]));
    const actionStatement = `ACTION=${action.action}; TARGET_CENTS=${target ?? "NONE"}; ACTIVE_TARGET_BEFORE_CENTS=${active ?? "NONE"}.`;
    const sentence = `${ids.map(leg => beliefs[leg].plain_sentence).join(" || ")} [${macro.receipt_id}] [${micro.receipt_id}] [${microMicro.receipt_id}]. ${actionStatement}`;
    const sibling = ids.find(leg => leg !== id), siblingCommitment = state.positions[sibling].credited ? state.positions[sibling].entry_cents : targets[sibling];
    const pairSum = target !== null && siblingCommitment !== null ? target + siblingCommitment : null;
    return { event_id: state.event_id, leg_id: id, timestamp_epoch: state.current_epoch,
      hours_from_discovery: reads.time_in_window.value.hours_from_discovery, receipt: state.receipt,
      vector: base.vectorFromReads(state, reads), neighborhood: [], resources_consulted: references,
      citation_receipts: citations, pool_cascade: pool, membership_count: selected?.member_count ?? null,
      membership_weight_sum: selected?.weight_sum ?? null, survivor_count: pool.pool_member_count ?? null,
      action, sentence,
      sentence_action_assertion: { hard_assert: true, expected_statement: actionStatement, equal: sentence.includes(actionStatement) },
      citation_receipt_assertion: { hard_assert: true, receipt_count: Object.keys(citations).length,
        equal: Object.keys(citations).every(receipt => sentence.includes(receipt)) },
      pair_conservation: { sibling_leg_id: sibling, sibling_commitment_cents: siblingCommitment, evaluated_target_cents: target, sum_cents: pairSum,
        at_or_below_99: pairSum === null || pairSum <= base.PAR_BUDGET_CENTS },
      derivation: { formation_end_epoch: state.legs[id].formation_end_epoch, target_basis: authorities[id].authority_source,
        target_authority: authorities[id].authority_source, derived_target_cents: target,
        lawful_unallocated_target_cents: authorities[id].target_cents, pricing_authority: authorities[id], allocation,
        live_bid_cents: reads.books.value[id]?.bid_cents ?? null, live_ask_cents: reads.books.value[id]?.ask_cents ?? null,
        formation_complete: formationComplete, pool_cascade: side ?? null,
        neighbor_leg: { status: "RETIRED_COMPATIBILITY_PROJECTION_ONLY", own_evidence: beliefs[id].own_evidence,
          conditional_remaining_dip_distribution_cents: {}, rows: [], excluded: [] },
        authority_target_divergence: { authority_target_cents: authorities[id].target_cents, final_target_cents: target,
          diverged: authorities[id].target_cents !== target, senior_authority_reason: authorities[id].target_cents !== target ? mode : null } },
      layered_dual_belief: { macro: { status: macro.context.status, pool_cascade: pool },
        micro: { status: micro.context.status, beliefs }, micro_micro: { status: microMicro.context.status }, coherence,
        pricing_authority: authorities[id], pool_cascade: side ?? null,
        prediction_seat: { disposition: "RETIRED_AS_LEVEL_WRITER", seat: null },
        envelope: null, envelope_placement: placement, technique_contracts: TECHNIQUE_CONTRACTS,
        decision_arbitration: arbitration, atomic_rearm: rearm, first_coherence: state.dual_belief.first_coherence }
    };
  });
  const creditedLegStreams = Object.fromEntries(ids.filter(id => state.positions[id].credited).map(id => [id, {
    credited_entry_cents: state.positions[id].entry_cents, fill_receipt: state.positions[id].fill_receipt,
    belief: beliefs[id], pricing_authority: authorities[id], current_receipt: state.receipt, action_emission_allowed: false }]));
  return { derivations, layers: { macro, micro, micro_micro: microMicro }, coherence, credited_leg_streams: creditedLegStreams };
}


module.exports = { ...base, CONTRACT_SUM_CENTS, SPREAD_SETTLE_COHERENCE_MAX_CENTS, LAYER_PROVENANCE, TECHNIQUE_CONTRACTS, PHASE_CENTRAL_BANDS, configurePhaseCentralSurface, configureNeighborSpecialistBinding, configureSurvivorShapeLibraries: survivorShapes.configureSurvivorShapeLibraries, weightedModeFloorSideCents, predictionSeatImmunityDecision, bookVetoOnlyDecision, pricingAuthorityForLeg, conditionPriorDistribution, deriveJointActions };
