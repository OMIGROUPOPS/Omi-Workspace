"use strict";

// V53-04 changes one behavioral surface on frozen V52l lineage: a leg whose
// receipt-causal machine state is RISING may not carry a rest until two
// operator-defined, joint-state-qualified, trade-backed divot episodes have
// each resumed.  Falling/settled/unclassified decisions and every target,
// guard, credit, and conservation input remain frozen lineage values.

const view = require("./window1_v53_understanding_organ.js");
const frozen = require("./window1_v52h_remove_pair_lows_precondition.js");

const ARMING_LAW = Object.freeze({
  id: "T1_SECOND_TRUE_DIVOT_VISIT",
  method_revision: 2,
  source_commit: "fe4c95de8c08a45081ef31e5fd24bb8da354a0cf",
  source_path: ".claude/window1_v53_04_riser_frontier_rebase_20260820/RISER_TRIGGER_FRONTIER_REBASED.json",
  proxy_instrument_consumed: false,
  shape_offset_aim_consumed: false,
  latchcal_consumed: false,
});

function lawfulCent(value) { return Number.isInteger(value) && value >= 1 && value <= 99; }

function emptyLegState(onsetTimestampEpoch) {
  return {
    ...view.emptyLegState(onsetTimestampEpoch),
    machine_state: null,
    machine_state_receipt: null,
    riser_arm: {
      prior_trade_high_cents: null,
      pending_trough: null,
      qualified_divots: [],
      armed: false,
      armed_receipt: null,
      armed_timestamp_epoch: null,
    },
  };
}

function observePostOnset(state, row) { return view.observePostOnset(state, row); }

function observeMachineState(state, machineState, row) {
  state.machine_state = ["RISING", "FALLING", "SETTLED"].includes(machineState) ? machineState : null;
  state.machine_state_receipt = row?.receipt ?? null;
  return state;
}

function observeRiserPrint(state, row, ownBook, siblingBook, machineState) {
  const arm = state.riser_arm;
  if (!arm || row?.kind !== "PRINT" || !lawfulCent(row.price)) return state;
  // A prior pending trough becomes a divot only on the later higher print.
  // That resume receipt is the causal arm receipt; no future row is read.
  if (arm.pending_trough && row.ts > arm.pending_trough.timestamp_epoch && row.price > arm.pending_trough.price_cents) {
    const qualified = { ...arm.pending_trough, resume_timestamp_epoch: row.ts, resume_receipt: row.receipt, resume_price_cents: row.price };
    arm.qualified_divots.push(qualified);
    arm.pending_trough = null;
    if (arm.qualified_divots.length >= 2 && !arm.armed) {
      arm.armed = true;
      arm.armed_receipt = row.receipt;
      arm.armed_timestamp_epoch = row.ts;
    }
  }
  const jointFormed = ownBook && siblingBook && lawfulCent(ownBook.bid) && lawfulCent(ownBook.ask) && lawfulCent(siblingBook.bid) && lawfulCent(siblingBook.ask);
  const strengthening = machineState === "RISING" && lawfulCent(arm.prior_trade_high_cents) && row.price < arm.prior_trade_high_cents;
  const tradeBackedAtTrough = jointFormed && row.price <= ownBook.bid;
  if (strengthening && tradeBackedAtTrough) {
    const candidate = {
      timestamp_epoch: row.ts,
      receipt: row.receipt,
      trade_id: row.trade_id,
      price_cents: row.price,
      size: row.size,
      own_joint_book: { bid_cents: ownBook.bid, ask_cents: ownBook.ask, receipt: ownBook.receipt },
      sibling_joint_book: { bid_cents: siblingBook.bid, ask_cents: siblingBook.ask, receipt: siblingBook.receipt },
      machine_state: machineState,
      definition: "OPERATOR_DIVOT_STRENGTHENING_SIDE_JOINT_STATE_TRADE_BACKED",
    };
    if (!arm.pending_trough || row.price < arm.pending_trough.price_cents) arm.pending_trough = candidate;
  }
  arm.prior_trade_high_cents = arm.prior_trade_high_cents === null ? row.price : Math.max(arm.prior_trade_high_cents, row.price);
  return state;
}

function stance(state) {
  if (state.machine_state === "RISING") return { value: "EARLY_FLOOR_SIDE", classification: "RISING", arming_law: ARMING_LAW, armed: state.riser_arm.armed, qualified_divots: state.riser_arm.qualified_divots.length, armed_receipt: state.riser_arm.armed_receipt };
  if (state.machine_state === "FALLING") return { value: "LATE_FLOOR_SIDE", classification: "FALLING", authority: "FROZEN_LINEAGE_TRACKING_CLAUSE" };
  return { value: "CLASSIFICATION_ABSENT", classification: state.machine_state, authority: "SILENCE_TO_FROZEN_LINEAGE" };
}

function buildGameView(states, context) {
  const base = view.buildGameView(states, context), ids = Object.keys(states).sort();
  return {
    ...base,
    legs: Object.fromEntries(ids.map((id) => [id, { ...base.legs[id], machine_state: { value: states[id].machine_state, producer_receipt: states[id].machine_state_receipt }, stance: stance(states[id]), riser_arm: { ...states[id].riser_arm, qualified_divots: [...states[id].riser_arm.qualified_divots] } }])),
    provenance: { ...base.provenance, v53_04_arming_law: ARMING_LAW, post_onset_only: true, no_span_fraction_consumed: true, no_static_depth_target_consumed: true },
  };
}

function buildPlan(gameView, context) {
  const ids = Object.keys(gameView.legs).sort();
  return {
    licensed: true,
    reason: "L23_ONE_GAME_ONE_JOINT_LICENSE",
    stances: Object.fromEntries(ids.map((id) => [id, gameView.legs[id].stance])),
    both_states: Object.fromEntries(ids.map((id) => [id, gameView.legs[id].machine_state])),
    split_authority: "FROZEN_CLAUSE_5_AND_CLAUSE_6_INPUTS_BYTE_EQUAL",
    arming_law: ARMING_LAW,
    evidence_receipt: context.row.receipt,
  };
}

function normalizedClauses(value = {}) {
  return { ...frozen.normalizedClauses(value), v53_riser_arming_law: Boolean(value.v53_riser_arming_law), pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true, scavenger: false };
}

function conservationInputs(inputs) {
  return { sibling_credited: inputs.siblingCredited === true, sibling_entry_cents: Number.isInteger(inputs.siblingEntryCents) ? inputs.siblingEntryCents : null, sibling_standing_target_cents: Number.isInteger(inputs.siblingStandingTarget) ? inputs.siblingStandingTarget : null, pair_cap_cents: Number.isInteger(inputs.pairCap) ? inputs.pairCap : null };
}

function jointLicense(inputs, plan, lineage, decision) {
  const counterpartKind = inputs.siblingCredited ? "BOUGHT_SIDE" : Number.isInteger(inputs.siblingStandingTarget) ? "STANDING_SIDE" : "UNSET_SIDE";
  return {
    law: "L23_PAIR_UNIT_PROOF",
    complete: Boolean(plan && plan.stances && Object.keys(plan.stances).length === 2),
    both_states: plan?.both_states ?? null,
    both_stances: plan?.stances ?? null,
    budget_split: { evaluated_side_target_cents: lawfulCent(decision.target_cents) ? decision.target_cents : null, counterpart_kind: counterpartKind, counterpart_cents: inputs.siblingCredited ? inputs.siblingEntryCents : inputs.siblingStandingTarget, pair_cap_cents: inputs.pairCap },
    split_authority: "FROZEN_CLAUSE_5_AND_CLAUSE_6_INPUTS_BYTE_EQUAL",
    evaluation_receipt: inputs.book?.receipt ?? null,
    arming_law: ARMING_LAW,
    lineage_action: lineage.action,
    lineage_target_cents: lawfulCent(lineage.target_cents) ? lineage.target_cents : null,
  };
}

function annotate(inputs, plan, lineage, decision, reason) {
  const license = decision.birth_license ?? lineage.birth_license ?? inputs.birthLicense ?? null;
  const joint = jointLicense(inputs, plan, lineage, decision);
  return {
    ...decision,
    reason,
    birth_license: license ? { ...license, game_view: inputs.v53GameView, plan, joint_license: joint, level: { ...(license.level ?? {}), v53_04_arming_law: ARMING_LAW, N9_role: "ADVISORY_ONLY_NOT_TARGET_AUTHORITY" } } : license,
    lineage_decision: { action: lineage.action, target_cents: lineage.target_cents, reason: lineage.reason },
    lineage_target_cents: lawfulCent(lineage.target_cents) ? lineage.target_cents : null,
    v53_riser_arming: { enabled: true, stance: plan?.stances?.[inputs.legId] ?? null, applied: inputs.state === "RISING", armed: plan?.stances?.[inputs.legId]?.armed ?? null, reason },
    conservation_input_identity: { lineage_inputs: conservationInputs(inputs), candidate_inputs: conservationInputs(inputs), byte_equal: true },
    joint_license: joint,
  };
}

function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses), lineage = frozen.decide({ ...inputs, clauses });
  if (!clauses.v53_riser_arming_law) return lineage;
  const plan = inputs.v53Plan;
  const ownStance = plan?.stances?.[inputs.legId];
  if (!ownStance || ownStance.value === "CLASSIFICATION_ABSENT") return annotate(inputs, plan, lineage, lineage, "V53_04_CLASSIFICATION_ABSENT_SILENCE_TO_LINEAGE");
  if (ownStance.value !== "EARLY_FLOOR_SIDE" || ownStance.armed) return annotate(inputs, plan, lineage, lineage, ownStance.value === "LATE_FLOOR_SIDE" ? "V53_04_LATE_FLOOR_FROZEN_TRACKING_BYTE_EQUAL" : "V53_04_EARLY_FLOOR_SECOND_TRUE_DIVOT_ARMED_LINEAGE_RELEASED");
  const active = lawfulCent(inputs.activeTarget) ? inputs.activeTarget : null;
  const blocked = active === null
    ? { action: "HOLD_REST", target_cents: null }
    : { action: "CANCEL_REST", target_cents: null, direction: undefined };
  return annotate(inputs, plan, lineage, { ...lineage, ...blocked, judgment_gate: { ...(lineage.judgment_gate ?? {}), verdict: "BLOCKED", failure: "RISER_T1_SECOND_TRUE_DIVOT_NOT_ARMED" } }, "V53_04_RISER_ARMING_BLOCKED_PENDING_SECOND_TRUE_DIVOT_RESUME");
}

function decideReceipt(inputs) { return { decision: decide(inputs), v53_riser_arming_law_enabled: true }; }

module.exports = { ...frozen, ARMING_LAW, emptyLegState, observePostOnset, observeMachineState, observeRiserPrint, stance, buildGameView, buildPlan, normalizedClauses, conservationInputs, jointLicense, decide, decideReceipt };
