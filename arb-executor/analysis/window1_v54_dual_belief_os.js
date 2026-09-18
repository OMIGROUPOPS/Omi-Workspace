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
  if (base.directionHandoffEnabled()) {
    const handoff = pool.sides?.[legId]?.handoff, layer = handoff?.selected_layer;
    const view = layer ? handoff.layers[layer] : null;
    const target = view?.status === "OK" ? cent(view.destination_cents) : null;
    return { authority_source: layer ? `DIRECTION_HANDOFF:${layer}:${view.destination_kind}` : "INSUFFICIENT_EVIDENCE",
      target_cents: target, effective_target_cents: target, handoff,
      true_conditioning: { method: "DIRECTION_CONDITIONED_DESTINATION_SEPARATE_FROM_ENTRY", selected_layer: layer ?? null,
        conditioned: target !== null, posterior_q50_cents: target, member_count: view?.member_count ?? null,
        ess: view?.ess ?? null, weight_sum: view?.weight_sum ?? null, quantiles: null },
      base_target_lawful: target !== null, own_evidence_rows: [], panel_rows: [],
      conditioning_chain: { prior_cents: null, conditioned_cents: target, final_level_cents: target },
      book_role: "MAKER_ENTRY_ONLY_DESTINATION_FROM_MEMBERS" };
  }
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
  if (authority.handoff) {
    const layer = authority.handoff.selected_layer, view = layer ? authority.handoff.layers[layer] : null;
    return { deadline_epoch: view?.deadline_epoch ?? null, predicted_minutes_to_bell: view?.deadline_minutes_to_bell ?? null,
      emitted_at_epoch: state.current_epoch, emitted_at_receipt: state.receipt,
      source: view ? `HANDOFF_${view.destination_kind}` : "INSUFFICIENT_EVIDENCE", stale_modeled_deadline_clamped_to_emission: false };
  }
  const floor = authority.true_conditioning.quantiles?.q50;
  return { deadline_epoch: floor?.epoch ?? null, predicted_minutes_to_bell: floor?.minutes_to_bell ?? null,
    emitted_at_epoch: state.current_epoch, emitted_at_receipt: state.receipt,
    source: authority.true_conditioning.selected_layer ? `POOL_${authority.true_conditioning.selected_layer}_FLOOR_MTB` : "INSUFFICIENT_EVIDENCE",
    stale_modeled_deadline_clamped_to_emission: false };
}
// Immutable assumptions stay outside prices and the pool. Conduct consults them
// only to require a renewed exact-level promise or pull an unsupported rest.
function accountableBids(state) {
  return state.bid_accountability ??= { active: {}, monitors: new Map(), records: [], lines: [], last_renewal: {} };
}
function accountableLine(state, kind, payload) {
  const line = Object.freeze({ kind, event_id: state.event_id, receipt: state.receipt,
    timestamp_epoch: state.current_epoch, ...payload });
  accountableBids(state).lines.push(line);
  return line;
}
function expiredRestLegIds(state, atEpoch) {
  return state.leg_ids.filter(id => {
    const position = state.positions[id], ledger = state.bid_accountability;
    const assumption = ledger?.active[id], monitor = ledger?.monitors.get(assumption?.assumption_id);
    return !position.credited && Number.isInteger(position.standing_target_cents) && assumption
      && (monitor?.status === "MISSED_AT_DEADLINE"
        || (monitor?.status !== "FULFILLED" && Number.isFinite(assumption.X_epoch) && atEpoch > assumption.X_epoch));
  });
}
function restSupportDecision(state, id, belief, authority, target, blockedReason, reviewOnly) {
  const position = state.positions[id], active = cent(position.standing_target_cents);
  const ledger = state.bid_accountability, old = ledger?.active[id];
  if (position.credited || active === null || !old) return null;
  const priorStatus = ledger.monitors.get(old.assumption_id)?.status ?? null;
  const deadlinePassed = priorStatus === "MISSED_AT_DEADLINE"
    || (priorStatus !== "FULFILLED" && Number.isFinite(old.X_epoch) && state.current_epoch >= old.X_epoch);
  const superseded = old.Q !== belief.predicted_cents || old.X_epoch !== belief.deadline.deadline_epoch
    || old.q_author !== belief.q_author || old.x_author !== belief.x_author
    || old.authority_source !== authority.authority_source;
  const required = Boolean(reviewOnly || deadlinePassed || superseded);
  const fresh = belief.status === "RESOLVED" && belief.deadline.emitted_at_receipt === state.receipt
    && belief.deadline.emitted_at_epoch === state.current_epoch
    && Number.isFinite(belief.deadline.deadline_epoch) && belief.deadline.deadline_epoch > state.current_epoch;
  const supportLevel = authority.handoff ? belief.entry_license?.allowed ? belief.entry_license.entry_cents : null : belief.predicted_cents;
  const exactRestSupported = fresh && supportLevel === active && target === active;
  const replacementSupported = !reviewOnly && fresh && Number.isInteger(target)
    && target !== active && supportLevel === target;
  return { required, assumption_id: old.assumption_id, original_Q: old.Q, original_X_epoch: old.X_epoch,
    prior_status: priorStatus, deadline_passed: deadlinePassed, assumption_superseded: superseded,
    fresh_sentence_receipt: state.receipt, fresh_Q: belief.predicted_cents,
    fresh_X_epoch: belief.deadline.deadline_epoch, fresh_status: belief.status,
    active_rest_cents: active, proposed_target_cents: target, blocked_reason: blockedReason,
    review_only: Boolean(reviewOnly), exact_rest_supported: exactRestSupported,
    replacement_supported: replacementSupported, pull: required && !exactRestSupported && !replacementSupported,
    reason: !fresh ? "NO_FRESH_RESOLVED_SENTENCE_WITH_DEADLINE_AHEAD"
      : !exactRestSupported ? "FRESH_SENTENCE_DOES_NOT_SUPPORT_EXACT_REST" : "FRESH_SENTENCE_SUPPORTS_EXACT_REST" };
}
function accountableAssumption(state, derivation) {
  const id = derivation.leg_id, belief = derivation.layered_dual_belief.micro.beliefs[id];
  const side = belief.pool_cascade, selected = side?.layers?.[side.selected_layer];
  const snapshot = { leg_id: id, authoring_sentence_receipt: derivation.receipt,
    authoring_sentence: belief.plain_sentence, sentence_with_citations: derivation.sentence,
    created_at_epoch: state.current_epoch, Q: belief.predicted_cents, P: belief.belief_price_cents,
    X_epoch: belief.deadline.deadline_epoch, X_minutes_to_bell: belief.predicted_minutes_to_bell,
    layer: side?.selected_layer ?? null, ESS: selected?.ess ?? null,
    member_count: selected?.member_count ?? null, weight_sum: selected?.weight_sum ?? null,
    q_author: belief.q_author, x_author: belief.x_author,
    authority_source: derivation.derivation.pricing_authority.authority_source,
    role: side?.roles?.current_role ?? null, rest_cents: derivation.action.target_cents,
    action: derivation.action.action, action_reason: derivation.action.reason,
    own_print_receipt: state.legs[id].prints.findLast(Boolean)?.receipt ?? null,
    formation_end_epoch: state.legs[id].formation_end_epoch, bell_epoch: state.bell_epoch };
  if (belief.handoff) Object.assign(snapshot, { destination_kind: belief.handoff.destination_kind,
    destination_cents: belief.predicted_cents, entry_cents: derivation.action.target_cents,
    entry_license: belief.entry_license, layer: belief.handoff.layer, ESS: belief.handoff.ess,
    member_count: belief.handoff.member_count, weight_sum: belief.handoff.weight_sum });
  return Object.freeze({ assumption_id: base.sha256(JSON.stringify(snapshot)), ...snapshot });
}
function pairEntryArithmeticChanged(old, candidate) {
  return ["pair_destination_sum_cents", "destination_band_lower_cents", "chosen_expected_discount_cents", "chosen_probability"]
    .some(key => old?.entry_license?.pair_entry?.[key] !== candidate?.entry_license?.pair_entry?.[key]);
}
function accountableDecision(state, derivation) {
  const ledger = accountableBids(state), id = derivation.leg_id, position = state.positions[id];
  const old = ledger.active[id] ?? null, action = derivation.action;
  if (position.credited || !Number.isInteger(position.standing_target_cents)) {
    if (action.reason === "PULL_UNSUPPORTED" || (base.directionHandoffEnabled() && derivation.derivation.rest_support?.pull)) accountableLine(state, "PULL_UNSUPPORTED", {
      leg_id: id, assumption_id: old?.assumption_id ?? null,
      action: action.action, reason: derivation.derivation.rest_support?.reason ?? action.reason,
      support_review: derivation.derivation.rest_support });
    if (old) accountableLine(state, "ASSUMPTION_CLOSED", { leg_id: id, assumption_id: old.assumption_id,
      reason: position.credited ? "FILL" : action.action, hold_reason: action.reason });
    delete ledger.active[id];
    return { assumption: old, renewal: ledger.last_renewal[id] ?? null, supersession: null };
  }
  const candidate = accountableAssumption(state, derivation);
  const changed = old && (action.action === "REPRICE_REST" || old.Q !== candidate.Q
    || old.X_epoch !== candidate.X_epoch || old.q_author !== candidate.q_author
    || old.x_author !== candidate.x_author || old.authority_source !== candidate.authority_source
    || pairEntryArithmeticChanged(old, candidate)
    || (candidate.entry_license && (old.entry_license?.reserve_cents !== candidate.entry_license.reserve_cents
      || old.entry_license?.reserve_basis !== candidate.entry_license.reserve_basis)));
  let supersession = null;
  if (!old || changed) {
    ledger.records.push(candidate);
    ledger.active[id] = candidate;
    ledger.monitors.set(candidate.assumption_id, { record: candidate, status: "PENDING", witness: null,
      last_print_cents: state.legs[id].prints.findLast(Boolean)?.price_cents ?? null });
    accountableLine(state, "BID_ASSUMPTION", { leg_id: id, assumption: candidate });
    if (old) {
      const reasons = [];
      if (old.role !== candidate.role) reasons.push("ROLE_CHANGE");
      if (old.own_print_receipt !== candidate.own_print_receipt) reasons.push("NEW_OWN_PRINT");
      if (Number.isFinite(old.X_epoch) && state.current_epoch >= old.X_epoch) reasons.push("DEADLINE_PASSED");
      if (old.q_author !== candidate.q_author || old.x_author !== candidate.x_author
          || old.authority_source !== candidate.authority_source) reasons.push("AUTHORITY_CHANGE");
      // Same author can issue a different phase forecast without a role/print change.
      // Name that observed change; never fabricate a role or print explanation.
      if (old.Q !== candidate.Q) reasons.push("AUTHORITY_FORECAST_LEVEL_CHANGED");
      if (old.X_epoch !== candidate.X_epoch) reasons.push("AUTHORITY_FORECAST_DEADLINE_CHANGED");
      if (pairEntryArithmeticChanged(old, candidate)) reasons.push("PAIR_ENTRY_ARITHMETIC_CHANGED");
      if (candidate.entry_license && (old.entry_license?.reserve_cents !== candidate.entry_license.reserve_cents
          || old.entry_license?.reserve_basis !== candidate.entry_license.reserve_basis)) reasons.push("COUNTERPART_PURCHASE_PLAN_CHANGED");
      if (!reasons.length) reasons.push("AUTHORITY_TARGET_NOW_EXECUTED");
      supersession = accountableLine(state, "SUPERSESSION", { leg_id: id,
        old_assumption_id: old.assumption_id, new_assumption_id: candidate.assumption_id,
        old_status: ledger.monitors.get(old.assumption_id).status, reasons,
        reason: reasons.join(" + "), action: action.action, hold_reason: action.reason });
    }
  }
  ledger.active[id] = ledger.active[id] ?? old;
  // This reason is precisely the last executed decision, not newly inferred authority.
  ledger.active_hold_reasons ??= {};
  ledger.active_hold_reasons[id] = { reason: action.reason, receipt: derivation.receipt, action: action.action };
  const renewal = accountableRenewals(state, null, "DECISION").find(row => row.leg_id === id);
  return { assumption: ledger.active[id], renewal: renewal ?? ledger.last_renewal[id] ?? null, supersession };
}
function accountableRenewals(state, tick, phase = "TICK") {
  const ledger = accountableBids(state), rows = [];
  for (const monitor of ledger.monitors.values()) {
    const a = monitor.record, id = a.leg_id, active = ledger.active[id]?.assumption_id === a.assumption_id;
    let effect = "unresolved", evidence = "NO_NEW_ACCEPTED_OWN_PRINT";
    const ownPrint = tick?.kind === "PRINT" && tick.leg_id === id && Number.isFinite(tick.price_cents)
      && Number.isFinite(tick.size) && Math.sign(tick.size) === Math.sign(CONTRACT_SUM_CENTS);
    const later = ownPrint && tick.timestamp_epoch > a.created_at_epoch;
    const inSpan = later && tick.timestamp_epoch >= a.formation_end_epoch
      && Number.isFinite(a.bell_epoch) && tick.timestamp_epoch < a.bell_epoch;
    const onTime = inSpan && Number.isFinite(a.X_epoch) && tick.timestamp_epoch <= a.X_epoch;
    const wasPending = monitor.status === "PENDING";
    if (wasPending && a.destination_kind === "W1_CLOSE" && Number.isFinite(a.X_epoch) && state.current_epoch >= a.X_epoch) {
      const close = state.legs[id].prints.findLast(row => row.timestamp_epoch < a.bell_epoch && row.size > 0)?.price_cents;
      monitor.status = Number.isFinite(close) && close >= a.Q ? "FULFILLED" : "MISSED_AT_DEADLINE";
      monitor.witness = { price_cents: close ?? null, timestamp_epoch: a.bell_epoch, basis: "LAST_ACCEPTED_OWN_PRINT_BEFORE_BELL" };
      effect = monitor.status === "FULFILLED" ? "supports" : "contradicts";
      evidence = "CLOSE_DESTINATION_CHECKED_AT_BELL_NOT_A_FLOOR_TOUCH";
    } else if (wasPending && a.destination_kind === "W1_CLOSE") {
      if (onTime && Number.isFinite(monitor.last_print_cents) && Math.abs(tick.price_cents - a.Q) < Math.abs(monitor.last_print_cents - a.Q)) {
        effect = "supports"; evidence = "OWN_PRINT_APPROACHED_CLOSE_DESTINATION_STILL_PENDING";
      }
    } else if (wasPending && onTime && Number.isFinite(a.Q) && tick.price_cents <= a.Q) {
      monitor.status = "FULFILLED";
      monitor.witness = { receipt: tick.receipt, timestamp_epoch: tick.timestamp_epoch, price_cents: tick.price_cents, size: tick.size };
      effect = "supports"; evidence = "LATER_POSITIVE_TRUE_PRINT_REACHED_FROZEN_Q_BY_X";
    } else if (wasPending && Number.isFinite(a.X_epoch) && state.current_epoch >= a.X_epoch) {
      monitor.status = "MISSED_AT_DEADLINE";
      effect = "contradicts"; evidence = "FROZEN_DEADLINE_ELAPSED_WITHOUT_LATER_POSITIVE_PRINT_AT_Q";
    } else if (wasPending && onTime && Number.isFinite(a.Q) && Number.isFinite(monitor.last_print_cents)
        && Math.abs(tick.price_cents - a.Q) < Math.abs(monitor.last_print_cents - a.Q)) {
      effect = "supports"; evidence = "OWN_TRUE_PRINT_MOVED_TOWARD_Q_NOT_YET_FULFILLED";
    } else if (later) evidence = "OWN_TRUE_PRINT_DOES_NOT_RESOLVE_FROZEN_PROMISE";
    if (ownPrint) monitor.last_print_cents = tick.price_cents;
    if (wasPending && monitor.status !== "PENDING") accountableLine(state, "ASSUMPTION_OUTCOME", {
      leg_id: id, assumption_id: a.assumption_id, status: monitor.status, witness: monitor.witness,
      effect, evidence, superseded: !active });
    if (!active) continue;
    const book = state.legs[id].current_book, position = state.positions[id];
    const resting = Number.isInteger(position.standing_target_cents) && !position.credited;
    // The filling tick is observed after the unchanged credit path; it still renews the bid it ended.
    const filledHere = position.credited && position.fill_receipt === tick?.receipt;
    if (!resting && !filledHere) continue;
    const price = a.rest_cents, ask = cent(book?.ask_cents), bid = cent(book?.bid_cents);
    const knownBook = Number.isInteger(ask) && Number.isInteger(bid);
    const sibling = state.leg_ids.find(leg => leg !== id), other = state.positions[sibling];
    const commitment = other.credited ? other.entry_cents : other.standing_target_cents;
    const hold = ledger.active_hold_reasons?.[id] ?? { reason: a.action_reason, receipt: a.authoring_sentence_receipt, action: a.action };
    const renewal = accountableLine(state, "BID_RENEWAL", { leg_id: id, assumption_id: a.assumption_id,
      phase, tick_receipt: tick?.receipt ?? null, tick_kind: tick?.kind ?? null, tick_leg_id: tick?.leg_id ?? null,
      status: monitor.status, effect, evidence, witness: monitor.witness,
      tick: tick ? { price_cents: tick.price_cents ?? null, size: tick.size ?? null,
        bid_cents: tick.bid_cents ?? null, ask_cents: tick.ask_cents ?? null,
        last_trade_cents: tick.last_trade_cents ?? null } : null,
      book: book ? { receipt: book.receipt, bid_cents: bid, ask_cents: ask, last_trade_cents: book.last_trade_cents ?? null } : null,
      rest_cents: price, remains_postable: knownBook ? price < ask && bid < ask : null,
      existing_rest_at_or_below_ask: Number.isInteger(ask) ? price <= ask : null,
      pair_within_cap: Number.isInteger(commitment) ? price + commitment <= base.PAR_BUDGET_CENTS : null,
      hold_reason: hold.reason, hold_reason_receipt: hold.receipt, hold_action: hold.action,
      reason_scope: phase === "TICK" ? "CARRIED_EXECUTED_REASON_NO_NEW_PRICING_DECISION" : "EXECUTED_DECISION",
      disposition: filledHere ? "FILLED" : "RESTING", conduct_changed: false });
    ledger.last_renewal[id] = renewal; rows.push(renewal);
    if (filledHere) delete ledger.active[id];
  }
  return rows;
}
let handoffMarkets = new Map();
function configureDirectionHandoffMarkets(markets) {
  handoffMarkets = new Map(markets.map(row => {
    const ranges = row.record?.pricing?.price_ranges;
    if (ranges?.length !== 1 || !(Number(ranges[0].step) > 0) || !row.receipt?.sha256) throw new Error("HANDOFF_MARKET_INCREMENT_UNVERIFIED");
    return [row.record.ticker ?? row.record.market?.ticker ?? row.ticker, { increment_cents: Number(ranges[0].step) * CONTRACT_SUM_CENTS, source: row.receipt }];
  }));
}
function handoffEntryPlan(state, reads, beliefs, authorities, reviewOnly) {
  const ids = state.leg_ids, plans = {};
  // A not-yet-filled riser's permission must exist before the faller can use
  // its entry as a cost. This order does not change the riser's price rule.
  const ordered = [...ids.filter(id => authorities[id].handoff?.role !== "FALLER"),
    ...ids.filter(id => authorities[id].handoff?.role === "FALLER")];
  for (const id of ordered) {
    const a = authorities[id], h = a.handoff, view = h?.selected_layer ? h.layers[h.selected_layer] : null;
    const b = reads.books.value[id], bid = cent(b?.bid_cents), ask = cent(b?.ask_cents);
    const sibling = ids.find(other => other !== id), other = state.positions[sibling];
    const faller = h?.role === "FALLER", reach = h?.reach;
    const reserve = other.credited ? other.entry_cents : faller
      ? plans[sibling]?.allowed ? plans[sibling].entry_cents : null : beliefs[sibling].predicted_cents;
    const reserveBasis = other.credited ? "ACTUAL_FILL" : faller ? "LICENSED_RISER_ENTRY" : "ELIGIBLE_DESTINATION";
    const destinationSum = [a.target_cents, beliefs[sibling].predicted_cents].every(Number.isFinite)
      ? a.target_cents + beliefs[sibling].predicted_cents : null;
    const market = handoffMarkets.get(`${state.event_id}-${id}`);
    const levelTable = (reach?.levels ?? []).map(row => {
      const level = row.level_cents, discount = [destinationSum, reserve].every(Number.isFinite) ? destinationSum - reserve - level : null;
      const expected = Number.isFinite(discount) && Number.isFinite(row.probability) ? row.probability * discount : null;
      const blocked = !market || level % market.increment_cents !== 0 ? "INVALID_MARKET_INCREMENT"
        : !Number.isFinite(ask) || level >= ask ? "NOT_MAKER_POSTABLE"
        : !Number.isFinite(reserve) || level + reserve > base.PAR_BUDGET_CENTS ? "PAIR_CAP"
        : !(discount > 0) ? "NO_POSITIVE_PAIR_DISCOUNT" : !(expected > 0) ? "NO_POSITIVE_EXPECTED_DISCOUNT" : null;
      return { ...row, pair_discount_cents: discount, expected_pair_discount_cents: expected, eligible: blocked === null, blocked_reason: blocked };
    });
    const standing = state.positions[id].standing_target_cents;
    const best = levelTable.filter(row => row.eligible).sort((a, b) => b.expected_pair_discount_cents - a.expected_pair_discount_cents
      || Number(b.level_cents === standing) - Number(a.level_cents === standing) || a.level_cents - b.level_cents)[0] ?? null;
    const pairEntry = faller ? { riser: sibling, riser_cost_cents: reserve ?? null, riser_cost_basis: reserveBasis,
      riser_destination_cents: beliefs[sibling].predicted_cents, pair_destination_sum_cents: destinationSum,
      destination_band_lower_cents: view?.floor_band.q25 ?? null, current_cents: h.current_cents,
      reach: reach ? { ...reach, levels: undefined } : null, level_table: levelTable,
      chosen_probability: best?.probability ?? null, chosen_expected_discount_cents: best?.expected_pair_discount_cents ?? null,
      chosen_level_cents: best?.level_cents ?? null,
      formula: "MAX_CALIBRATED_REACH_TIMES_PAIR_DESTINATION_SUM_MINUS_RISER_COST_MINUS_LEVEL" } : null;
    let why = null, proposed = null;
    if (state.positions[id].credited) why = "already filled";
    else if (h?.role === "NOT_CALLABLE" || !h) why = "cannot yet tell which side rises";
    else if (beliefs[id].status !== "RESOLVED") why = "too few direction-matched past games";
    else if (!(beliefs[id].deadline.deadline_epoch > state.current_epoch)) why = "no destination deadline ahead";
    else if (bid === null || ask === null || bid >= ask) why = "missing or locked book";
    else if (!Number.isFinite(reserve)) why = "counterpart has no eligible purchase plan";
    else if (h.role === "CLIMBER") {
      if (!market) throw new Error(`HANDOFF_MARKET_INCREMENT_MISSING ${id}`);
      // Prefer the approved maker improvement, then join best bid; neither may
      // cross, exceed the destination, or consume the counterpart reservation.
      proposed = [cent(ask - market.increment_cents), bid].find(level => level !== null && level >= bid && level < ask
        && level < a.target_cents && level + reserve < CONTRACT_SUM_CENTS) ?? null;
      if (proposed === null) why = "no near-market maker entry below destination within the pair budget";
    } else if (h.role === "FALLER") {
      if (!view.window.open) why = "waiting for the learned faller window";
      else if (reach?.status !== "OK") why = "no earlier positive-print reach calibration";
      else if (!best) why = "no positive expected pair discount at a lawful maker level";
      else {
        proposed = cent(best.level_cents);
        if (proposed === null) why = "reach optimization gives no valid maker price";
      }
    } else why = "flat reference only; no side discount claimed";
    if (!why && proposed + reserve >= CONTRACT_SUM_CENTS) why = "entry plus counterpart reserve is not under par";
    if (!why && proposed >= ask) why = "licensed entry is not maker-postable";
    if (!why && reviewOnly?.includes(id) && proposed !== state.positions[id].standing_target_cents) why = "pre-print review may renew only the exact existing entry";
    plans[id] = { allowed: !why, entry_cents: proposed, destination_cents: a.target_cents,
      destination_kind: view?.destination_kind ?? null, role: h?.role ?? "NOT_CALLABLE",
      member_count: view?.member_count ?? null, ess: view?.ess ?? null, layer: h?.selected_layer ?? null,
      counterpart: sibling, reserve_cents: reserve ?? null, reserve_basis: reserveBasis,
      pair_cents: Number.isFinite(proposed) && Number.isFinite(reserve) ? proposed + reserve : null,
      ...(pairEntry ? { pair_entry: { ...pairEntry,
        discount_to_destinations_cents: [destinationSum, proposed, reserve].every(Number.isFinite) ? destinationSum - proposed - reserve : null } } : {}),
      price_increment: market ?? null, window: view?.window ?? null, waiting_reason: why };
  }
  return plans;
}
function handoffReason(id, plan) {
  if (plan.pair_entry) {
    const p = plan.pair_entry, value = cents => Number.isFinite(cents) ? `${cents}¢` : "unknown";
    const numbers = p.level_table.map(row => `${value(row.level_cents)} reaches ${Number.isFinite(row.probability) ? row.probability * CONTRACT_SUM_CENTS + "%" : "unknown"} for ${value(row.pair_discount_cents)} = ${value(row.expected_pair_discount_cents)}${row.blocked_reason ? ` (${row.blocked_reason})` : ""}`).join("; ");
    const arithmetic = `${p.riser} ${p.riser_cost_basis === "ACTUAL_FILL" ? "bought" : "licensed at"} ${value(p.riser_cost_cents)} → ${value(p.riser_destination_cents)}; ${id} → ${value(plan.destination_cents)} floor; pair destination sum ${value(p.pair_destination_sum_cents)}; ${numbers || "no calibrated levels"}`;
    return plan.allowed ? `${arithmetic}; entering ${value(plan.entry_cents)} maximizes expected pair discount; pair cost ${value(plan.pair_cents)}; maker-only in the learned window, under par.`
      : `${id}: waiting: ${plan.waiting_reason}; ${arithmetic}.`;
  }
  const destination = Number.isFinite(plan.destination_cents) ? `destination ${plan.destination_cents}¢ from ${plan.member_count} past ${plan.role === "CLIMBER" ? "risers" : "fallers"}` : "no licensed destination";
  const budget = `${plan.counterpart} ${plan.reserve_basis === "ACTUAL_FILL" ? "filled" : "reserved"} at ${plan.reserve_cents ?? "unknown"}¢; pair ${plan.pair_cents ?? "unknown"}¢`;
  return plan.allowed ? `${id}: ${destination}; entering at ${plan.entry_cents}¢ because ${plan.role === "CLIMBER" ? "maker entry is below the forecast close" : "the conditioned floor is postable in its learned window"}; ${budget}, under par.`
    : `${id}: waiting: ${plan.waiting_reason}; ${destination}; ${budget}.`;
}
function renewPairEntryDependencies(state, plans, targets) {
  for (const [id, plan] of Object.entries(plans)) {
    if (plan.allowed && plan.pair_entry && !state.positions[plan.counterpart].credited && !plans[plan.counterpart].allowed) {
      plan.allowed = false;
      plan.waiting_reason = "riser entry was withheld; no filled or licensed riser cost";
      targets[id] = null;
    }
  }
}
function deriveJointActions({ state, reads, resources, restReviewLegIds = null }) {
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
    if (authority.handoff) {
      const h = authority.handoff, v = h.selected_layer ? h.layers[h.selected_layer] : null;
      belief.status = formationComplete && authority.base_target_lawful ? "RESOLVED" : "INSUFFICIENT_EVIDENCE";
      belief.predicted_cents = belief.status === "RESOLVED" ? authority.target_cents : null;
      belief.predicted_minutes_to_bell = deadline.predicted_minutes_to_bell;
      belief.q_author = authority.authority_source; belief.x_author = deadline.source;
      belief.family = v?.family ?? null;
      belief.handoff = { flag: h.flag, role: h.role, destination_kind: v?.destination_kind ?? null,
        destination_cents: belief.predicted_cents, layer: h.selected_layer, member_count: v?.member_count ?? null,
        ess: v?.ess ?? null, weight_sum: v?.weight_sum ?? null, floor_band: v?.floor_band ?? null,
        close_band: v?.close_band ?? null, window: v?.window ?? null, reach: h.reach };
      belief.candidate_level_q25_cents = (h.role === "CLIMBER" ? v?.close_band : v?.floor_band)?.q25 ?? null;
      belief.candidate_level_q75_cents = (h.role === "CLIMBER" ? v?.close_band : v?.floor_band)?.q75 ?? null;
    }
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
  const microMicro = layerReceipt(state, "MICRO_MICRO", microMicroResolved ? "RESOLVED" : "INSUFFICIENT_EVIDENCE", [state.receipt, ...ids.map(id => reads.books.value[id]?.receipt)], { tick_state: reads.books.value });
  const targets = {}, modes = {}, postability = {};
  const handoffPlans = base.directionHandoffEnabled() ? handoffEntryPlan(state, reads, beliefs, authorities, restReviewLegIds) : null;
  for (const id of ids) {
    const position = state.positions[id], active = cent(position.standing_target_cents), q = handoffPlans ? handoffPlans[id].allowed ? handoffPlans[id].entry_cents : null : beliefs[id].predicted_cents;
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
    if (handoffPlans && !handoffPlans[id].allowed) targets[id] = null;
  }
  state.dual_belief.last_postability = postability;
  const planSum = sum(ids.map(id => state.positions[id].credited ? state.positions[id].entry_cents : targets[id]));
  const pairBlocked = planSum > base.PAR_BUDGET_CENTS;
  if (pairBlocked) for (const id of ids.filter(id => !state.positions[id].credited)) {
    targets[id] = cent(state.positions[id].standing_target_cents); modes[id] = "PAIR_CONSERVATION_SKIP_NEW_REST_HOLD_AND_CONTINUE";
  }
  if (handoffPlans) for (const id of ids) {
    const plan = handoffPlans[id];
    if (plan.allowed && targets[id] !== plan.entry_cents) {
      plan.allowed = false; plan.waiting_reason = `entry withheld by ${modes[id]}`;
    }
    if (!plan.allowed) targets[id] = null;
  }
  if (handoffPlans) renewPairEntryDependencies(state, handoffPlans, targets);
  if (handoffPlans) for (const id of ids) {
    const plan = handoffPlans[id];
    plan.written_reason = handoffReason(id, plan);
    beliefs[id].entry_license = plan;
    beliefs[id].plain_sentence = plan.written_reason;
  }
  // Post-only, book veto and pair cap above still select or block a new target.
  // None of those blocks, by itself, renews the old price's promise.
  const restSupport = {};
  for (const id of ids) {
    const reviewOnly = restReviewLegIds?.includes(id);
    const check = restSupportDecision(state, id, beliefs[id], authorities[id], targets[id], modes[id], reviewOnly);
    restSupport[id] = check;
    if (!check?.required) continue;
    if (check.pull) { targets[id] = null; modes[id] = "PULL_UNSUPPORTED"; }
    else if (reviewOnly || targets[id] === check.active_rest_cents) {
      targets[id] = check.active_rest_cents; modes[id] = "FRESH_SENTENCE_SUPPORTS_EXACT_REST";
    }
  }
  if (handoffPlans) for (const id of ids) {
    const plan = handoffPlans[id];
    if (plan.allowed && targets[id] !== plan.entry_cents) { plan.allowed = false; plan.waiting_reason = restSupport[id]?.reason ?? modes[id]; }
  }
  if (handoffPlans) renewPairEntryDependencies(state, handoffPlans, targets);
  if (handoffPlans) for (const id of ids) {
    const plan = handoffPlans[id];
    plan.written_reason = handoffReason(id, plan); beliefs[id].plain_sentence = plan.written_reason;
  }
  // Seal the citation only after the entry license is complete; destination
  // and licensing text must not mutate an already-hashed receipt context.
  const micro = layerReceipt(state, "MICRO", resolved ? "RESOLVED" : "INSUFFICIENT_EVIDENCE", references, { beliefs });
  const allocation = { targets, lawful: sum(ids.map(id => state.positions[id].credited ? state.positions[id].entry_cents : targets[id])) <= base.PAR_BUDGET_CENTS,
    reason: pairBlocked ? "PAIR_CONSERVATION_SKIP_NEW_REST_HOLD_AND_CONTINUE" : handoffPlans ? "DIRECTION_DESTINATION_LICENSES_SEPARATE_MAKER_ENTRY" : "POOL_Q_UNCHANGED_POST_ONLY_AND_PAIR_VETO", mode: "VETO_ONLY_NOT_PRICE_AUTHOR" };
  const derivations = ids.map(id => {
    const position = state.positions[id], active = cent(position.standing_target_cents), target = targets[id], mode = modes[id];
    const action = actionForTarget(active, target, mode);
    if (handoffPlans) action.reason = handoffPlans[id].written_reason;
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
    const side = pool.sides?.[id], selected = handoffPlans ? side?.handoff?.layers?.[side.handoff.selected_layer]
      : side?.selected_layer ? side.layers[side.selected_layer] : null;
    const lane = mode === "PRICING_AUTHORITY_TARGET_EXECUTED" ? "POOL_CASCADE_WRITER" : active !== null && target === active ? "ACTIVE_REST_HOLD" : "NO_ACTION";
    const arbitration = { decision_instant_epoch: state.current_epoch, source_receipt: state.receipt,
      winner: { lane, ...action }, losers: [{ lane: "STEP-FORECAST", eligible: false, disposition: "PILE_TELEMETRY_NOT_AN_AUTHOR" }],
      emitted_order_count: ["PLACE_REST", "REPRICE_REST", "CANCEL_REST"].includes(action.action) ? 1 : 0,
      pricing_authority_target_cents: authorities[id].target_cents, lane_may_replace_authority: false };
    if (handoffPlans) Object.assign(arbitration, { destination_cents: authorities[id].target_cents,
      licensed_entry_cents: handoffPlans[id].allowed ? handoffPlans[id].entry_cents : null,
      authority_contract: "DESTINATION_IS_NOT_ENTRY; ENTRY_REQUIRES_FRESH_LICENSE" });
    const placement = { mode, writer_lane: lane, active_target_before_cents: active, chosen_target_cents: target,
      post_only_test: { target_cents: handoffPlans ? handoffPlans[id].entry_cents : authorities[id].target_cents, live_ask_cents: reads.books.value[id]?.ask_cents ?? null, lawful: postability[id].postable },
      post_only_role: "VETO_ONLY_NOT_PRICE_AUTHOR", technique_contract: "C01_PRICING_AUTHORITY_OVER_LANE_LEVEL_SELECTION" };
    if (handoffPlans) Object.assign(placement, { destination_cents: authorities[id].target_cents,
      entry_license: handoffPlans[id], technique_contract: "FLAGGED_DESTINATION_ENTRY_HANDOFF" });
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
        ...(handoffPlans ? { entry_license: handoffPlans[id] } : {}),
        rest_support: restSupport[id],
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
Object.assign(module.exports, { accountableDecision, accountableRenewals, expiredRestLegIds, restSupportDecision });
Object.assign(module.exports, { configureDirectionHandoffMarkets, handoffEntryPlan, renewPairEntryDependencies });
