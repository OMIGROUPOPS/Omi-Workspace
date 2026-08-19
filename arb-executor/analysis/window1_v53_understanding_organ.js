"use strict";

// V53-01 is a hand-authored game-view/plan organ. It does not inherit V52's
// clause-3 level signer. The frozen V52h module remains the authority for the
// disagreement referee and the clause-5/clause-6 conservation functions.

const frozen = require("./window1_v52h_remove_pair_lows_precondition.js");

const PAR_CENTS = 100;
const TAPE_TICK_CENTS = 1;
const ROLE_DRIFT_CENTS = 2;
const TRD5_PRINT_COUNT = 5;

function lawfulCent(value) { return Number.isInteger(value) && value >= 1 && value <= 99; }
function receiptOf(row) { return { timestamp_epoch: row.ts, receipt: row.receipt, kind: row.kind }; }

function emptyLegState(onsetTimestampEpoch) {
  return {
    onset_timestamp_epoch: onsetTimestampEpoch,
    observations: [],
    prints: [],
    running_session_low_cents: null,
    running_session_low_receipt: null,
    anchor_cents: null,
    anchor_receipt: null,
    prior_reference_cents: null,
    prior_reference_receipt: null,
    last_step_cents: null,
    last_step_receipt: null,
    reversals: 0,
    prior_step_sign: 0,
  };
}

function referencePrice(row) {
  if (row.kind === "PRINT" && lawfulCent(row.price)) return { value: row.price, source: "TRUE_TRADE", receipt: receiptOf(row) };
  if (lawfulCent(row.last_trade)) return { value: row.last_trade, source: "BOOK_LAST_TRADED", receipt: receiptOf(row) };
  if (lawfulCent(row.bid) && lawfulCent(row.ask)) return { value: Math.floor((row.bid + row.ask) / 2), source: "JOINT_BBO_FLOORED_MID", receipt: receiptOf(row) };
  return null;
}

function observePostOnset(state, row) {
  if (!state || !Number.isFinite(state.onset_timestamp_epoch) || row.ts < state.onset_timestamp_epoch) return state;
  const ref = referencePrice(row);
  const executable = row.kind === "PRINT" ? row.price : row.ask;
  const observation = {
    timestamp_epoch: row.ts,
    receipt: row.receipt,
    kind: row.kind,
    bid_cents: row.kind === "BOOK" && lawfulCent(row.bid) ? row.bid : null,
    ask_cents: row.kind === "BOOK" && lawfulCent(row.ask) ? row.ask : null,
    last_traded_cents: row.kind === "BOOK" && lawfulCent(row.last_trade) ? row.last_trade : row.kind === "PRINT" ? row.price : null,
    spread_cents: row.kind === "BOOK" && lawfulCent(row.bid) && lawfulCent(row.ask) ? row.ask - row.bid : null,
    dwell_seconds: row.kind === "BOOK" && Number.isFinite(row.dwell_seconds) ? row.dwell_seconds : null,
    reference_cents: ref?.value ?? null,
    reference_source: ref?.source ?? null,
  };
  state.observations.push(observation);
  if (row.kind === "PRINT" && lawfulCent(row.price)) state.prints.push({ price_cents: row.price, ...receiptOf(row) });
  if (lawfulCent(executable) && (state.running_session_low_cents === null || executable < state.running_session_low_cents)) {
    state.running_session_low_cents = executable;
    state.running_session_low_receipt = receiptOf(row);
  }
  if (ref) {
    if (state.anchor_cents === null) {
      state.anchor_cents = ref.value;
      state.anchor_receipt = ref.receipt;
    }
    if (state.prior_reference_cents !== null && ref.value !== state.prior_reference_cents) {
      const step = ref.value - state.prior_reference_cents;
      const sign = Math.sign(step);
      if (state.prior_step_sign !== 0 && sign !== state.prior_step_sign) state.reversals += 1;
      state.prior_step_sign = sign;
      state.last_step_cents = step;
      state.last_step_receipt = ref.receipt;
    }
    state.prior_reference_cents = ref.value;
    state.prior_reference_receipt = ref.receipt;
  }
  return state;
}

function legView(state, context) {
  const current = state.observations[state.observations.length - 1] ?? null;
  const refs = state.observations.map((row) => row.reference_cents).filter(Number.isInteger);
  const min = refs.length ? Math.min(...refs) : null;
  const max = refs.length ? Math.max(...refs) : null;
  const currentRef = current?.reference_cents ?? null;
  const net = Number.isInteger(currentRef) && Number.isInteger(state.anchor_cents) ? currentRef - state.anchor_cents : null;
  const travel = Number.isInteger(min) && Number.isInteger(max) ? max - min : null;
  const nonzeroStep = Number.isInteger(state.last_step_cents) && state.last_step_cents !== 0;
  const legState = nonzeroStep && state.last_step_receipt?.receipt === current?.receipt
    ? "STEPPING"
    : state.last_step_receipt && current?.receipt !== state.last_step_receipt.receipt ? "SETTLED" : "STILL";
  let family = { status: "PENDING", value: null, reason: "ENDPOINT_DEPENDENT_FAMILIES_NOT_LIVE_CALLABLE", producer_receipt: current?.receipt ?? null };
  if (state.prints.length >= TRD5_PRINT_COUNT && Number.isInteger(net) && Number.isInteger(travel)) {
    const maxStep = Math.max(0, ...state.observations.slice(1).map((row, i) => {
      const previous = state.observations[i].reference_cents;
      return Number.isInteger(row.reference_cents) && Number.isInteger(previous) ? Math.abs(row.reference_cents - previous) : 0;
    }));
    const absNet = Math.abs(net);
    let value;
    if (travel >= 10 && absNet < 5 && state.reversals > 0) value = "ROUND_TRIP";
    else if (absNet > 0 && maxStep / absNet >= 0.60) value = net < 0 ? "ONE_STEP_DOWN" : "ONE_STEP_UP";
    else if (state.reversals >= 4 && travel >= 2 * absNet) value = net < 0 ? "GRIND_WOBBLE_DOWN" : "GRIND_WOBBLE_UP";
    else if (net <= -ROLE_DRIFT_CENTS) value = "DRIFT_DOWN";
    else if (net >= ROLE_DRIFT_CENTS) value = "DRIFT_UP";
    if (value) family = { status: "DECLARED", value, reason: "LIVE_RESTATEMENT_FROM_CAUSAL_PREFIX_ONLY", producer_receipt: current?.receipt ?? null };
  }
  let role = "UNRIPE";
  if (!String(context.category).startsWith("WTA_CHALL") && state.prints.length >= TRD5_PRINT_COUNT && Number.isInteger(net)) {
    if (net >= ROLE_DRIFT_CENTS) role = "CLIMBER";
    else if (net <= -ROLE_DRIFT_CENTS) role = "FALLER";
  }
  return {
    current_observation: { value: current, producer_receipt: current?.receipt ?? null },
    belief_anchor: { value_cents: state.anchor_cents, producer_receipt: state.anchor_receipt },
    travel: { value_cents: travel, net_cents: net, min_cents: min, max_cents: max, producer_receipt: current?.receipt ?? null },
    leg_state: { value: legState, producer_receipt: current?.receipt ?? null },
    family,
    role: {
      value: role,
      drift_cents: net,
      drift_anchor_cents: state.anchor_cents,
      drift_anchor_receipt: state.anchor_receipt,
      TRD5_print_count: state.prints.length,
      TRD5_gate: TRD5_PRINT_COUNT,
      TRV6: { travel_cents: travel, reversals: state.reversals },
      WTA_CHALL_role_disabled: String(context.category).startsWith("WTA_CHALL"),
      producer_receipt: current?.receipt ?? null,
    },
    reach: {
      running_session_low_cents: state.running_session_low_cents,
      producer_receipt: state.running_session_low_receipt,
      authority: "RECORDER_DUAL_BOOK_TRUE_TRADE_SESSION_LOW_ONLY",
    },
  };
}

function buildGameView(states, context) {
  const ids = Object.keys(states).sort();
  const legs = Object.fromEntries(ids.map((id) => [id, legView(states[id], context)]));
  return {
    event_id: context.event_id,
    evaluation: { timestamp_epoch: context.row.ts, receipt: context.row.receipt },
    joint_observation: Object.fromEntries(ids.map((id) => [id, legs[id].current_observation])),
    belief_anchor_pair: Object.fromEntries(ids.map((id) => [id, legs[id].belief_anchor])),
    legs,
    provenance: {
      shape_taxonomy_commit: context.shape_taxonomy_commit,
      shape_taxonomy_path: context.shape_taxonomy_path,
      TRD5_commit: context.trd5_commit,
      no_endpoint_labels_consumed: true,
      no_span_fraction_consumed: true,
      no_static_depth_target_consumed: true,
    },
  };
}

function buildPlan(gameView, context) {
  const ids = Object.keys(gameView.legs).sort();
  const lows = Object.fromEntries(ids.map((id) => [id, gameView.legs[id].reach.running_session_low_cents]));
  if (!ids.every((id) => lawfulCent(lows[id]))) return { licensed: false, reason: "PAIR_RUNNING_SESSION_LOW_INCOMPLETE", delta_goal_cents: null, targets: {}, owner_leg_id: null, evidence_receipt: context.row.receipt };
  const lowSum = lows[ids[0]] + lows[ids[1]];
  const deltaGoal = Math.max(TAPE_TICK_CENTS, PAR_CENTS - lowSum);
  const budget = PAR_CENTS - deltaGoal;
  const ownerCandidates = ids.filter((id) => gameView.legs[id].role.value === "FALLER" && gameView.legs[id].leg_state.value === "STEPPING");
  const owner = ownerCandidates.length === 1 ? ownerCandidates[0] : null;
  const targets = { ...lows };
  let expectedRemainingStep = null;
  if (owner) {
    const state = context.states[owner];
    expectedRemainingStep = Math.abs(Math.min(-TAPE_TICK_CENTS, state.last_step_cents ?? -TAPE_TICK_CENTS));
    targets[owner] = Math.max(TAPE_TICK_CENTS, lows[owner] - expectedRemainingStep);
  }
  const targetSum = targets[ids[0]] + targets[ids[1]];
  if (targetSum > budget) return {
    licensed: false,
    reason: "PAIR_PLAN_CANNOT_HONOR_AT_LOW_FOR_NON_OWNER_WITHOUT_INVENTED_DEPTH",
    delta_goal_cents: deltaGoal,
    pair_budget_cents: budget,
    running_low_sum_cents: lowSum,
    targets,
    target_sum_cents: targetSum,
    owner_leg_id: owner,
    expected_remaining_step_cents: expectedRemainingStep,
    evidence_receipt: context.row.receipt,
  };
  return {
    licensed: true,
    reason: owner ? "OWNER_STANDS_ONE_OBSERVED_REMAINING_STEP_DEEPER" : "BOTH_LEGS_STAND_AT_RUNNING_SESSION_LOW",
    delta_goal_cents: deltaGoal,
    delta_goal_formula: `max(${TAPE_TICK_CENTS},${PAR_CENTS}-${lowSum})=${deltaGoal}`,
    pair_budget_cents: budget,
    running_low_sum_cents: lowSum,
    targets,
    target_sum_cents: targetSum,
    owner_leg_id: owner,
    expected_remaining_step_cents: expectedRemainingStep,
    evidence_receipt: context.row.receipt,
  };
}

function normalizedClauses(value = {}) {
  return {
    ...frozen.normalizedClauses(value),
    v53_understanding_organ: Boolean(value.v53_understanding_organ),
    pair_entry_conservation: true,
    joint_target_conservation: true,
    remove_pair_lows_precondition: true,
    scavenger: false,
  };
}

function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.v53_understanding_organ) return frozen.decide({ ...inputs, clauses });
  const active = lawfulCent(inputs.activeTarget) ? inputs.activeTarget : null;
  const gameView = inputs.v53GameView;
  const plan = inputs.v53Plan;
  const ownPlan = plan?.targets?.[inputs.legId];
  const upperFailure = !inputs.birthLicense?.onset?.passed ? "STABILITY_ONSET_NOT_REACHED"
    : !inputs.birthLicense?.read?.passed ? "NO_TAPE_MACHINE_READ_ABSENT"
      : !inputs.birthLicense?.coherence?.disagreement_clear ? "FIRING_DISAGREEMENT_ACTIVE"
        : !plan?.licensed ? plan?.reason ?? "PAIR_PLAN_ABSENT"
          : !lawfulCent(ownPlan) ? "NO_LAWFUL_PLAN_TARGET" : null;
  const licenseBase = {
    ...inputs.birthLicense,
    game_view: gameView,
    plan,
    level: {
      ...(inputs.birthLicense?.level ?? {}),
      target_cents: lawfulCent(ownPlan) ? ownPlan : null,
      authority: "V53_HAND_AUTHORED_GAME_VIEW_PLAN",
      clause_3_replaced: true,
      N9_role: "ADVISORY_ONLY_NOT_TARGET_AUTHORITY",
    },
  };
  if (upperFailure) return {
    action: active === null ? "HOLD_REST" : "CANCEL_REST",
    target_cents: active === null ? null : active,
    reason: `V53_LICENSE_BLOCKED_${upperFailure}`,
    birth_license: licenseBase,
    judgment_gate: { enabled: true, verdict: "BLOCKED", failure: upperFailure, clause_3: "V53_GAME_VIEW_PLAN" },
  };
  let target = ownPlan;
  if (lawfulCent(inputs.book?.ask)) target = Math.min(target, inputs.book.ask - TAPE_TICK_CENTS);
  if (!lawfulCent(target)) return { action: active === null ? "HOLD_REST" : "CANCEL_REST", target_cents: active, reason: "V53_POST_ONLY_BOUND_UNLAWFUL", birth_license: licenseBase, judgment_gate: { enabled: true, verdict: "BLOCKED", failure: "NO_LAWFUL_POST_ONLY_TARGET", clause_3: "V53_GAME_VIEW_PLAN" } };
  const settlement = frozen.settlementIdentity(inputs, target);
  target = settlement.licensed_target_cents;
  const joint = frozen.jointTargetConservation(inputs, target);
  target = joint.licensed_target_cents;
  if (!lawfulCent(target)) throw new Error("V53 conservation returned unlawful target");
  const action = active === null ? "PLACE_REST" : active === target ? "HOLD_REST" : "REPRICE_REST";
  const license = {
    ...licenseBase,
    level: { ...licenseBase.level, target_cents: target, pre_clause_5_target_cents: ownPlan, post_only_target_cents: Math.min(ownPlan, inputs.book.ask - TAPE_TICK_CENTS), authority: "V53_HAND_AUTHORED_GAME_VIEW_PLAN+FROZEN_CLAUSE_5+FROZEN_CLAUSE_6" },
    pair_entry_conservation: settlement,
    joint_target_conservation: joint,
    clause_4_market_proof_precondition: frozen.marketProofReceipt(inputs.birthLicense?.coherence),
  };
  return {
    action,
    target_cents: target,
    ...(action === "REPRICE_REST" ? { direction: target > active ? "UP" : "DOWN" } : {}),
    reason: action === "HOLD_REST" ? "V53_PLAN_TARGET_ALREADY_STANDING" : "V53_PLAN_LICENSED_POST",
    placement: { target_cents: target, authority: license.level.authority, game_view_receipt: gameView.evaluation.receipt, plan_receipt: plan.evidence_receipt },
    birth_license: license,
    pair_entry_conservation: settlement,
    joint_target_conservation: joint,
    clause_4_market_proof_precondition: license.clause_4_market_proof_precondition,
    judgment_gate: { enabled: true, verdict: action === "HOLD_REST" ? "LICENSED_HOLD" : "POST", failure: null, clause_3: "V53_GAME_VIEW_PLAN", clause_5: "FROZEN", clause_6: "FROZEN" },
  };
}

function decideReceipt(inputs) { return { decision: decide(inputs), v53_understanding_organ_enabled: true }; }

module.exports = {
  ...frozen,
  PAR_CENTS,
  TAPE_TICK_CENTS,
  ROLE_DRIFT_CENTS,
  TRD5_PRINT_COUNT,
  emptyLegState,
  observePostOnset,
  legView,
  buildGameView,
  buildPlan,
  normalizedClauses,
  decide,
  decideReceipt,
};
