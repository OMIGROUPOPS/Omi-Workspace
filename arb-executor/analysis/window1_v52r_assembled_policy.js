"use strict";

// V52r assembles two operator-selected, previously measured instruments over
// adopted V52l. Recognition is the TRD5 gate using V52q's corrected anchor;
// a directional call binds at the first receipt with five post-onset prints
// and is held until that same instrument flips. ROLE_DOWN alone consumes the
// LOW-1 target. ROLE_UP, ROLE_STILL and ABSTAIN retain V52l behavior.

const v52q = require("./window1_v52q_anchor_correction.js");
const v52h = require("./window1_v52h_remove_pair_lows_precondition.js");

const TRD5_COMMIT = "71de534a3f9e21faf569cd487d9aae735a084e7a";
const LOW1_COMMIT = "ab609761c5df44097f46ad2364f539bbd0751d54";
const TRD5_MIN_POST_ONSET_TRADES = 5;
const LOW1_DELTA_CENTS = 1;
let trd5Binding = null;
let low1Binding = null;

function ensure(value, message) { if (!value) throw new Error(message); }
function finite(value) { return Number.isFinite(value); }
function lawfulCent(value) { return Number.isInteger(value) && value >= 1 && value <= 99; }

function configureTRD5(value) {
  ensure(value?.provenance?.commit === TRD5_COMMIT, "V52r TRD5 commit mismatch");
  ensure(value?.artifact?.LABEL === "GATE_POLICY_EVALUATION_LIVE_COORDINATES", "V52r TRD5 label mismatch");
  ensure(value?.artifact?.grid?.TRD5?.cfg?.mt === TRD5_MIN_POST_ONSET_TRADES, "V52r TRD5 threshold mismatch");
  ensure(value.artifact.binding_rule.includes("bind at first gate crossing with a directional call"), "V52r TRD5 binding rule mismatch");
  ensure(value.artifact.binding_rule.includes("hold unless the instrument itself flips"), "V52r TRD5 hold rule mismatch");
  trd5Binding = value;
  return { bound: true, threshold: TRD5_MIN_POST_ONSET_TRADES, provenance: value.provenance };
}

function configureLOW1(value) {
  ensure(value?.provenance?.commit === LOW1_COMMIT, "V52r LOW-1 commit mismatch");
  ensure(value?.artifact?.LABEL === "DOWN_TARGET_FRONTIER", "V52r LOW-1 label mismatch");
  ensure(value.artifact.rules?.["LOW-1"] || value.artifact.grid?.["LOW-1"] || JSON.stringify(value.artifact).includes("LOW-1"), "V52r LOW-1 rule absent");
  low1Binding = value;
  return { bound: true, delta_cents: LOW1_DELTA_CENTS, provenance: value.provenance };
}

function requiredTRD5() { ensure(trd5Binding, "V52r TRD5 not configured"); return trd5Binding; }
function requiredLOW1() { ensure(low1Binding, "V52r LOW-1 not configured"); return low1Binding; }

function emptyShapeState() {
  return { ...v52q.emptyShapeState(), trd5_bound_role: null, trd5_first_bind: null, trd5_last_flip: null, trd5_flip_count: 0 };
}

function recognitionReceipt() {
  return {
    name: "TRD5_CORRECTED_ANCHOR_HELD_DIRECTIONAL_ROLE",
    expression: "after max(causal_onset,formation_end), first directional corrected-anchor call with post_onset_trade_count>=5 binds; hold through STILL; opposite directional call flips",
    threshold_post_onset_trades: TRD5_MIN_POST_ONSET_TRADES,
    corrected_anchor: v52q.requiredAnchorCorrection(),
    provenance: requiredTRD5().provenance,
    new_constants: 0,
  };
}

function classifyShapeState(state, evaluation = {}) {
  if (evaluation.assembled_policy_enabled !== true) return v52q.classifyShapeState(state, evaluation);
  ensure(finite(evaluation.timestamp_epoch), "V52r evaluation timestamp absent");
  const coordinateZero = finite(evaluation.post_onset_epoch) && finite(evaluation.formation_end_epoch)
    ? Math.max(evaluation.post_onset_epoch, evaluation.formation_end_epoch) : null;
  const anchor = evaluation.published_anchor_cents;
  const causalPrints = finite(coordinateZero)
    ? state.prints.filter((row) => row.timestamp_epoch >= coordinateZero && row.timestamp_epoch <= evaluation.timestamp_epoch)
    : [];
  const last = causalPrints.at(-1) ?? null;
  const drift = last && lawfulCent(anchor) ? last.price_cents - anchor : null;
  const candidateRole = drift === null ? null
    : drift >= v52q.BENCHMARK_ROLE_THRESHOLD_CENTS ? "ROLE_UP"
      : drift <= -v52q.BENCHMARK_ROLE_THRESHOLD_CENTS ? "ROLE_DOWN" : "ROLE_STILL";
  const gatePassed = causalPrints.length >= TRD5_MIN_POST_ONSET_TRADES;
  let transition = "NO_BIND";
  if (gatePassed && (candidateRole === "ROLE_UP" || candidateRole === "ROLE_DOWN")) {
    if (state.trd5_bound_role === null) {
      state.trd5_bound_role = candidateRole;
      state.trd5_first_bind = { timestamp_epoch: evaluation.timestamp_epoch, receipt: evaluation.receipt ?? null, role: candidateRole, trade_count: causalPrints.length };
      transition = "FIRST_BIND";
    } else if (state.trd5_bound_role !== candidateRole) {
      const prior = state.trd5_bound_role;
      state.trd5_bound_role = candidateRole;
      state.trd5_flip_count += 1;
      state.trd5_last_flip = { timestamp_epoch: evaluation.timestamp_epoch, receipt: evaluation.receipt ?? null, from: prior, to: candidateRole, trade_count: causalPrints.length };
      transition = "INSTRUMENT_FLIP_REBIND";
    } else transition = "HELD_SAME_DIRECTION";
  } else if (state.trd5_bound_role !== null) transition = candidateRole === "ROLE_STILL" ? "HELD_THROUGH_STILL" : "HELD_NO_NEW_DIRECTIONAL_CALL";

  const bound = state.trd5_bound_role;
  return {
    status: bound ? `TRD5_BOUND_${bound}` : !finite(coordinateZero) ? "ABSTAIN_COORDINATE_ZERO_UNAVAILABLE" : !lawfulCent(anchor) ? "ABSTAIN_CORRECTED_ANCHOR_UNAVAILABLE" : !gatePassed ? "ABSTAIN_TRD5_NOT_MET" : "ABSTAIN_TRD5_DIRECTIONAL_CALL_ABSENT",
    role: bound ?? "ABSTAIN",
    bound_role: bound,
    candidate_role: candidateRole,
    signable: bound !== null,
    drift_cents: drift,
    post_formation_open_cents: lawfulCent(anchor) ? anchor : null,
    post_formation_open_receipt: evaluation.published_anchor_receipt ?? null,
    formation_end_epoch: evaluation.formation_end_epoch ?? null,
    post_onset_epoch: evaluation.post_onset_epoch ?? null,
    coordinate_zero_epoch: coordinateZero,
    last_causal_print_cents: last?.price_cents ?? null,
    last_causal_print_receipt: last?.receipt ?? null,
    true_print_count: causalPrints.length,
    evaluation_timestamp_epoch: evaluation.timestamp_epoch,
    evaluation_receipt: evaluation.receipt ?? null,
    maximum_consumed_timestamp_epoch: last?.timestamp_epoch ?? null,
    causal: true,
    right_edge_consumed: false,
    full_span_fit: false,
    anchor_correction: {
      anchor_cents: lawfulCent(anchor) ? anchor : null,
      anchor_receipt: evaluation.published_anchor_receipt ?? null,
      formation_end_epoch: evaluation.formation_end_epoch ?? null,
      method: v52q.requiredAnchorCorrection().method,
      series_floor: v52q.requiredAnchorCorrection().series_floor,
    },
    trd5: {
      post_onset_trade_count: causalPrints.length,
      threshold: TRD5_MIN_POST_ONSET_TRADES,
      gate_passed: gatePassed,
      transition,
      first_bind: state.trd5_first_bind,
      last_flip: state.trd5_last_flip,
      flip_count: state.trd5_flip_count,
      held_unless_instrument_flips: true,
      provenance: requiredTRD5().provenance,
    },
    rule: recognitionReceipt(),
  };
}

function pairCap(inputs) {
  const counterpart = inputs?.siblingCredited === true ? inputs.siblingEntryCents : inputs?.siblingStandingTarget;
  return Number.isInteger(counterpart) ? 99 - counterpart : null;
}

function low1Selection(license, incumbent, inputs = {}) {
  const recognition = license?.level?.macro_recognition ?? null;
  const frozen = v52h.machineReadLevel(license, incumbent);
  const base = {
    clause: "CLAUSE_3_V52R_ASSEMBLED_POLICY",
    recognition,
    frozen_v52l_machine_read: frozen,
    selected_target_cents: frozen.target_cents ?? null,
    target_changed: false,
    priors_gate: false,
  };
  if (recognition?.bound_role !== "ROLE_DOWN") return {
    ...base,
    applicable: false,
    reason: recognition?.bound_role === "ROLE_UP" ? "ROLE_UP_V52L_EARLY_CATCH_PRESERVED" : recognition?.candidate_role === "ROLE_STILL" ? "ROLE_STILL_V52L_DEFAULT_PRESERVED" : "TRD5_ABSTAIN_V52L_DEFAULT_PRESERVED",
    level_policy: "V52L_DEFAULT_EVIDENCE_BACKED_LEVEL",
  };
  const runningLow = license?.diary?.own_post_onset_true_trade_low_cents;
  const ask = inputs.book?.ask;
  const cap = pairCap(inputs);
  if (!lawfulCent(runningLow) || !lawfulCent(ask)) return {
    ...base,
    applicable: false,
    reason: "ROLE_DOWN_RUNNING_POST_ONSET_LOW_OR_TOUCH_ABSENT",
    level_policy: "V52L_DEFAULT_EVIDENCE_BACKED_LEVEL",
  };
  const raw = runningLow - LOW1_DELTA_CENTS;
  const bounded = Math.min(raw, ask - 1, Number.isInteger(cap) ? cap : 99);
  const applicable = lawfulCent(bounded);
  return {
    ...base,
    applicable,
    reason: applicable ? "ROLE_DOWN_LOW_MINUS_ONE_CONSUMED" : "ROLE_DOWN_LOW_MINUS_ONE_OUTSIDE_LAWFUL_CENT_RANGE",
    level_policy: applicable ? "ROLE_DOWN_RUNNING_POST_ONSET_SESSION_LOW_MINUS_ONE" : "V52L_DEFAULT_EVIDENCE_BACKED_LEVEL",
    session_low_cents: runningLow,
    session_low_receipt: license?.diary?.own_receipt ?? null,
    delta_cents: LOW1_DELTA_CENTS,
    arithmetic: `${runningLow}-${LOW1_DELTA_CENTS}=${raw};min(${raw},${ask}-1,${Number.isInteger(cap) ? cap : 99})=${bounded}`,
    current_touch_ask_cents: ask,
    clause_6_cap_cents: Number.isInteger(cap) ? cap : null,
    selected_target_cents: applicable ? bounded : frozen.target_cents ?? null,
    target_changed: applicable && bounded !== frozen.target_cents,
    current_touch_above_bound_applied: true,
    joint_law_bound_applied: Number.isInteger(cap),
    low1_identity: "TRAIL1_IDENTICAL_TO_LOW_1_ON_INTEGER_TAPE",
    provenance: requiredLOW1().provenance,
  };
}

function normalizedClauses(value = {}) {
  const clauses = v52q.normalizedClauses(value);
  return value.assembled_policy
    ? { ...clauses, benchmarked_role_instrument: true, anchor_correction: true, assembled_policy: true, ripeness_role_binding: false }
    : clauses;
}

function adjustedIncumbent(incumbent, selection) {
  const result = { ...incumbent, target_cents: selection.selected_target_cents, placement: { ...(incumbent?.placement ?? {}), target_cents: selection.selected_target_cents, macro_recognition_target_source: "V52R_ROLE_DOWN_LOW_MINUS_ONE" } };
  delete result.unguarded_decision;
  return result;
}

function assembledGateDecision(inputs, incumbent) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.assembled_policy) return v52q.decide({ ...inputs, clauses });
  const selection = low1Selection(inputs.birthLicense, incumbent, inputs);
  const adjustedLicense = { ...inputs.birthLicense, level: { ...inputs.birthLicense?.level, proposed_target_cents: selection.selected_target_cents, macro_recognition: selection.recognition, assembled_policy: selection } };
  const frozenClauses = { ...clauses, macro_recognition: false, recognition_confidence_gate: false, benchmarked_role_instrument: false, ripeness_role_binding: false, anchor_correction: false, assembled_policy: false };
  const decision = selection.applicable
    ? v52h.gateDecision({ ...inputs, clauses: frozenClauses, birthLicense: adjustedLicense }, adjustedIncumbent(incumbent, selection))
    : v52h.gateDecision({ ...inputs, clauses: frozenClauses, birthLicense: adjustedLicense }, incumbent);
  const licensed = decision.judgment_gate?.failure == null && ["PLACE_REST", "REPRICE_REST", "HOLD_REST"].includes(decision.action);
  const consumed = selection.applicable && licensed && decision.target_cents === selection.selected_target_cents;
  const stamped = { ...selection, candidate_target_differs_from_v52l: selection.target_changed, target_changed: consumed && selection.selected_target_cents !== selection.frozen_v52l_machine_read?.target_cents, level_policy_consumed: consumed, final_licensed_target_cents: decision.target_cents ?? null };
  return v52q.restoreGuardTerminationReceipt({
    ...decision,
    birth_license: decision.birth_license ? { ...decision.birth_license, level: { ...decision.birth_license.level, macro_recognition: selection.recognition, assembled_policy: stamped } } : null,
    macro_recognition: selection.recognition,
    assembled_policy: stamped,
  }, inputs);
}

function decideReceipt(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.assembled_policy) return v52q.decideReceipt({ ...inputs, clauses });
  const frozenClauses = { ...clauses, assembled_policy: false, benchmarked_role_instrument: false, ripeness_role_binding: false, anchor_correction: false, macro_recognition: false, recognition_confidence_gate: false };
  const atomic = v52h.decideReceipt({ ...inputs, clauses: frozenClauses });
  return { ...atomic, decision: assembledGateDecision({ ...inputs, clauses }, atomic.decision.unguarded_decision ?? atomic.decision), assembled_policy_enabled: true };
}

function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.assembled_policy) return v52q.decide({ ...inputs, clauses });
  const frozenClauses = { ...clauses, assembled_policy: false, benchmarked_role_instrument: false, ripeness_role_binding: false, anchor_correction: false, macro_recognition: false, recognition_confidence_gate: false };
  const incumbent = v52h.decide({ ...inputs, clauses: frozenClauses });
  return assembledGateDecision({ ...inputs, clauses }, incumbent.unguarded_decision ?? incumbent);
}

module.exports = {
  ...v52q,
  TRD5_COMMIT,
  LOW1_COMMIT,
  TRD5_MIN_POST_ONSET_TRADES,
  LOW1_DELTA_CENTS,
  configureTRD5,
  configureLOW1,
  requiredTRD5,
  requiredLOW1,
  emptyShapeState,
  recognitionReceipt,
  classifyShapeState,
  low1Selection,
  floorDepthSelection: low1Selection,
  incumbentWithSelectedTarget: adjustedIncumbent,
  normalizedClauses,
  assembledGateDecision,
  decideReceipt,
  decide,
};
