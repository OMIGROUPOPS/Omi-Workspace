"use strict";

// V53-04b changes one behavioral surface on frozen V52l lineage: the causal
// receipt that arms a RISING leg.  The six selectable laws exist only for the
// engine-space pins sweep. Falling/settled/unclassified decisions and every
// target, guard, credit, and conservation input remain frozen lineage values.

const view = require("./window1_v53_understanding_organ.js");
const frozen = require("./window1_v52h_remove_pair_lows_precondition.js");

const REBASE_SOURCE = Object.freeze({ source_commit: "fe4c95de8c08a45081ef31e5fd24bb8da354a0cf", source_path: ".claude/window1_v53_04_riser_frontier_rebase_20260820/RISER_TRIGGER_FRONTIER_REBASED.json" });
const ARMING_LAWS = Object.freeze({
  A0_CONTROL_PROXY_SECOND_VISIT: Object.freeze({ id: "A0_CONTROL_PROXY_SECOND_VISIT", source_commit: "c1fd51ececb7de1885a88f8672b1e5ce7444e3a1", source_path: ".claude/window1_live_v4_replay/v53_04_riser_arming_law_pins_smoke_20260820/PINS_SMOKE_RECEIPT.json", engine_effect: "ARM_ON_SECOND_PROXY_ASK_LEVEL_VISIT_INSIDE_FROZEN_300S_HORIZON", horizon_seconds: frozen.LOOKBACK_SECONDS, horizon_source_commit: "d1ac94973252e2f8c28ba32374c29ff7bd605a7e", horizon_source_path: ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_DIVOT_CENSUS.json", proxy_instrument_consumed: true }),
  A1_PROXY_FIRST_VISIT: Object.freeze({ id: "A1_PROXY_FIRST_VISIT", ...REBASE_SOURCE, engine_effect: "ARM_ON_FIRST_CAUSAL_RISING_ASK_DESCENT", proxy_instrument_consumed: true }),
  A2_FIRST_TRUE_DIVOT_AND_RESUME: Object.freeze({ id: "A2_FIRST_TRUE_DIVOT_AND_RESUME", ...REBASE_SOURCE, engine_effect: "ARM_ON_FIRST_OPERATOR_DIVOT_LATER_RESUME", proxy_instrument_consumed: false }),
  A3_FIRST_SELLER_HIT: Object.freeze({ id: "A3_FIRST_SELLER_HIT", ...REBASE_SOURCE, engine_effect: "ARM_ON_FIRST_RISING_SIDE_SELLER_AGGRESSED_PRINT", proxy_instrument_consumed: false }),
  A4_BID_PERSISTENCE_300S: Object.freeze({ id: "A4_BID_PERSISTENCE_300S", ...REBASE_SOURCE, engine_effect: "ARM_ON_RISING_BID_PERSISTENCE_300S", persistence_seconds: 300, persistence_source_commit: "084df12553928677869bd2857516caa3f0490416", persistence_source_path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/RISER_TRIGGER_FRONTIER.json", proxy_instrument_consumed: false }),
  A5_FIRST_TWO_SIDED_BOOK: Object.freeze({ id: "A5_FIRST_TWO_SIDED_BOOK", ...REBASE_SOURCE, engine_effect: "ARM_ON_FIRST_TWO_SIDED_BOOK", proxy_instrument_consumed: false }),
});
let selectedArmingLaw = ARMING_LAWS.A2_FIRST_TRUE_DIVOT_AND_RESUME;

function withCommonProvenance(law) { return { ...law, method_revision: 3, shape_offset_aim_consumed: false, latchcal_consumed: false }; }
function configureArmingLaw(id) {
  if (!Object.hasOwn(ARMING_LAWS, id)) throw new Error(`unknown V53-04b arming law ${id}`);
  selectedArmingLaw = ARMING_LAWS[id];
  return withCommonProvenance(selectedArmingLaw);
}
function armingLaw() { return withCommonProvenance(selectedArmingLaw); }

function lawfulCent(value) { return Number.isInteger(value) && value >= 1 && value <= 99; }

function emptyLegState(onsetTimestampEpoch) {
  const law = armingLaw();
  return {
    ...view.emptyLegState(onsetTimestampEpoch),
    machine_state: null,
    machine_state_receipt: null,
    riser_arm: {
      law_id: law.id,
      prior_trade_high_cents: null,
      pending_trough: null,
      qualified_divots: [],
      armed: false,
      armed_receipt: null,
      armed_timestamp_epoch: null,
      arm_count: 0,
      arm_reason: null,
      prior_ask_cents: null,
      proxy_level_visits: [],
      current_bid_cents: null,
      current_bid_since_epoch: null,
    },
  };
}

function observePostOnset(state, row) { return view.observePostOnset(state, row); }

function observeMachineState(state, machineState, row) {
  state.machine_state = ["RISING", "FALLING", "SETTLED"].includes(machineState) ? machineState : null;
  state.machine_state_receipt = row?.receipt ?? null;
  return state;
}

function armAt(state, row, reason, evidence = null) {
  const arm = state.riser_arm;
  if (!arm.armed) {
    arm.armed = true;
    arm.armed_receipt = row.receipt;
    arm.armed_timestamp_epoch = row.ts;
    arm.arm_count += 1;
    arm.arm_reason = reason;
    arm.arm_evidence = evidence;
  }
  return state;
}

function observeRiserBook(state, row, priorBook, machineState) {
  observeMachineState(state, machineState, row);
  const arm = state.riser_arm, law = armingLaw();
  if (!arm || row?.kind !== "BOOK" || !lawfulCent(row.bid) || !lawfulCent(row.ask)) return state;
  if (law.id === "A5_FIRST_TWO_SIDED_BOOK") armAt(state, row, law.engine_effect, { bid_cents: row.bid, ask_cents: row.ask });
  if (!priorBook || row.ask !== priorBook.ask) {
    arm.proxy_level_visits.push({ timestamp_epoch: row.ts, receipt: row.receipt, ask_cents: row.ask });
    arm.proxy_level_visits = arm.proxy_level_visits.filter((visit) => visit.timestamp_epoch >= row.ts - frozen.LOOKBACK_SECONDS);
    const matching = arm.proxy_level_visits.filter((visit) => visit.ask_cents === row.ask);
    if (law.id === "A0_CONTROL_PROXY_SECOND_VISIT" && matching.length >= frozen.PULSE_REVISIT_MIN) armAt(state, row, law.engine_effect, { ask_cents: row.ask, visits: matching, horizon_seconds: frozen.LOOKBACK_SECONDS });
  }
  if (law.id === "A1_PROXY_FIRST_VISIT" && machineState === "RISING" && priorBook && lawfulCent(priorBook.ask) && row.ask < priorBook.ask) {
    armAt(state, row, law.engine_effect, { prior_ask_cents: priorBook.ask, ask_cents: row.ask, proxy_only: true });
  }
  if (law.id === "A4_BID_PERSISTENCE_300S") {
    if (arm.current_bid_cents !== row.bid) { arm.current_bid_cents = row.bid; arm.current_bid_since_epoch = row.ts; }
    if (machineState === "RISING" && Number.isFinite(arm.current_bid_since_epoch) && row.ts - arm.current_bid_since_epoch >= law.persistence_seconds) {
      armAt(state, row, law.engine_effect, { bid_cents: row.bid, persistence_seconds: row.ts - arm.current_bid_since_epoch, qualification_started_epoch: arm.current_bid_since_epoch });
    }
  }
  arm.prior_ask_cents = row.ask;
  return state;
}

function observeRiserPrint(state, row, ownBook, siblingBook, machineState) {
  const arm = state.riser_arm, law = armingLaw();
  if (!arm || row?.kind !== "PRINT" || !lawfulCent(row.price)) return state;
  if (law.id === "A3_FIRST_SELLER_HIT" && machineState === "RISING" && (row.taker_side === "no" || row.taker_book_side === "bid")) {
    armAt(state, row, law.engine_effect, { trade_id: row.trade_id, price_cents: row.price, size: row.size, taker_side: row.taker_side, taker_book_side: row.taker_book_side });
  }
  // A prior pending trough becomes a divot only on the later higher print.
  // That resume receipt is the causal arm receipt; no future row is read.
  if (arm.pending_trough && row.ts > arm.pending_trough.timestamp_epoch && row.price > arm.pending_trough.price_cents) {
    const qualified = { ...arm.pending_trough, resume_timestamp_epoch: row.ts, resume_receipt: row.receipt, resume_price_cents: row.price };
    arm.qualified_divots.push(qualified);
    arm.pending_trough = null;
    if (law.id === "A2_FIRST_TRUE_DIVOT_AND_RESUME" && arm.qualified_divots.length >= 1) armAt(state, row, law.engine_effect, qualified);
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
  const law = armingLaw();
  if (state.machine_state === "RISING") return { value: "EARLY_FLOOR_SIDE", classification: "RISING", arming_law: law, armed: state.riser_arm.armed, qualified_divots: state.riser_arm.qualified_divots.length, proxy_level_visits: state.riser_arm.proxy_level_visits.length, armed_receipt: state.riser_arm.armed_receipt, armed_timestamp_epoch: state.riser_arm.armed_timestamp_epoch, arm_count: state.riser_arm.arm_count, arm_reason: state.riser_arm.arm_reason };
  if (state.machine_state === "FALLING") return { value: "LATE_FLOOR_SIDE", classification: "FALLING", authority: "FROZEN_LINEAGE_TRACKING_CLAUSE" };
  return { value: "CLASSIFICATION_ABSENT", classification: state.machine_state, authority: "SILENCE_TO_FROZEN_LINEAGE" };
}

function buildGameView(states, context) {
  const base = view.buildGameView(states, context), ids = Object.keys(states).sort();
  return {
    ...base,
    legs: Object.fromEntries(ids.map((id) => [id, { ...base.legs[id], machine_state: { value: states[id].machine_state, producer_receipt: states[id].machine_state_receipt }, stance: stance(states[id]), riser_arm: { ...states[id].riser_arm, qualified_divots: [...states[id].riser_arm.qualified_divots], proxy_level_visits: [...states[id].riser_arm.proxy_level_visits] } }])),
    provenance: { ...base.provenance, v53_04_arming_law: armingLaw(), post_onset_only: true, no_span_fraction_consumed: true, no_static_depth_target_consumed: true },
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
    arming_law: armingLaw(),
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
    arming_law: armingLaw(),
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
    birth_license: license ? { ...license, game_view: inputs.v53GameView, plan, joint_license: joint, level: { ...(license.level ?? {}), v53_04_arming_law: armingLaw(), N9_role: "ADVISORY_ONLY_NOT_TARGET_AUTHORITY" } } : license,
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
  // A0 is the incumbent control. Its proxy receipt is measured, but it is not
  // permitted to become a new veto over the byte-frozen V52l decision path.
  if (armingLaw().id === "A0_CONTROL_PROXY_SECOND_VISIT") return annotate(inputs, inputs.v53Plan, lineage, lineage, "V53_04B_A0_PROXY_SECOND_VISIT_OBSERVED_FROZEN_V52L_CONTROL_BYTE_EQUAL");
  const plan = inputs.v53Plan;
  const ownStance = plan?.stances?.[inputs.legId];
  if (!ownStance || ownStance.value === "CLASSIFICATION_ABSENT") return annotate(inputs, plan, lineage, lineage, "V53_04_CLASSIFICATION_ABSENT_SILENCE_TO_LINEAGE");
  if (ownStance.value !== "EARLY_FLOOR_SIDE" || ownStance.armed) return annotate(inputs, plan, lineage, lineage, ownStance.value === "LATE_FLOOR_SIDE" ? "V53_04_LATE_FLOOR_FROZEN_TRACKING_BYTE_EQUAL" : `V53_04B_EARLY_FLOOR_ARMED_${armingLaw().id}_LINEAGE_RELEASED`);
  const active = lawfulCent(inputs.activeTarget) ? inputs.activeTarget : null;
  const blocked = active === null
    ? { action: "HOLD_REST", target_cents: null }
    : { action: "CANCEL_REST", target_cents: null, direction: undefined };
  return annotate(inputs, plan, lineage, { ...lineage, ...blocked, judgment_gate: { ...(lineage.judgment_gate ?? {}), verdict: "BLOCKED", failure: `RISER_ARMING_NOT_YET_QUALIFIED_${armingLaw().id}` } }, `V53_04B_RISER_ARMING_BLOCKED_${armingLaw().id}`);
}

function decideReceipt(inputs) { return { decision: decide(inputs), v53_riser_arming_law_enabled: true }; }

module.exports = { ...frozen, ARMING_LAWS, configureArmingLaw, armingLaw, emptyLegState, observePostOnset, observeMachineState, observeRiserBook, observeRiserPrint, stance, buildGameView, buildPlan, normalizedClauses, conservationInputs, jointLicense, decide, decideReceipt };
