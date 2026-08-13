"use strict";

// V52g extends frozen V52f from the sequential settlement identity to a
// receipt-causal joint identity. Existing per-leg level authorities speak
// first; this clause only bounds the newly evaluated target when both sides
// have a decision-time-known standing or bought value.

const v52f = require("./window1_v52f_pair_entry_conservation.js");

function normalizedClauses(value = {}) {
  const clauses = v52f.normalizedClauses(value);
  return value.joint_target_conservation ? { ...clauses, pair_entry_conservation: true, joint_target_conservation: true } : clauses;
}

function jointTargetConservation(inputs, proposedTarget) {
  const counterpartKind = inputs.siblingCredited === true ? "BOUGHT_SIDE" : Number.isInteger(inputs.siblingStandingTarget) ? "STANDING_SIDE" : "UNSET_SIDE";
  const counterpartCents = inputs.siblingCredited === true ? inputs.siblingEntryCents : inputs.siblingStandingTarget;
  if (proposedTarget === null) return {
    clause: "CLAUSE_6_ORDER_FREE_JOINT_TARGET_CONSERVATION",
    reached: false,
    passed: null,
    reason: "NO_LICENSED_TARGET_TO_CHECK",
    proposed_target_cents: null,
    counterpart_kind: counterpartKind,
    counterpart_cents: Number.isInteger(counterpartCents) ? counterpartCents : null,
    licensed_target_cents: null,
  };
  if (!v52f.lawfulCent(proposedTarget)) throw new Error(`V52g proposed target unlawful ${proposedTarget}`);
  if (!Number.isInteger(counterpartCents)) return {
    clause: "CLAUSE_6_ORDER_FREE_JOINT_TARGET_CONSERVATION",
    reached: true,
    passed: true,
    reason: "COUNTERPART_TARGET_NOT_YET_LICENSED",
    proposed_target_cents: proposedTarget,
    counterpart_kind: counterpartKind,
    counterpart_cents: null,
    max_lawful_target_cents: null,
    licensed_target_cents: proposedTarget,
    target_changed: false,
  };
  if (!v52f.lawfulCent(counterpartCents)) throw new Error(`V52g counterpart cents unlawful ${counterpartCents}`);
  const cap = 99 - counterpartCents;
  if (!v52f.lawfulCent(cap)) throw new Error(`V52g joint target cap unlawful ${cap}`);
  const licensed = Math.min(proposedTarget, cap);
  return {
    clause: "CLAUSE_6_ORDER_FREE_JOINT_TARGET_CONSERVATION",
    reached: true,
    passed: licensed + counterpartCents <= 99,
    reason: proposedTarget <= cap ? "JOINT_TARGETS_ALREADY_AT_OR_BELOW_99" : "EVALUATED_TARGET_BOUNDED_BY_JOINT_IDENTITY",
    arithmetic: `${licensed}+${counterpartCents}=${licensed + counterpartCents}<=99`,
    operator: "target_A_cents + target_B_cents <= 99",
    proposed_target_cents: proposedTarget,
    counterpart_kind: counterpartKind,
    counterpart_cents: counterpartCents,
    max_lawful_target_cents: cap,
    licensed_target_cents: licensed,
    target_changed: licensed !== proposedTarget,
  };
}

function gateDecision(inputs, incumbent) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.joint_target_conservation) return v52f.gateDecision({ ...inputs, clauses }, incumbent);
  const frozen = v52f.gateDecision({ ...inputs, clauses: { ...clauses, joint_target_conservation: false } }, incumbent);
  const upperLayersLicensed = frozen.judgment_gate?.failure == null && ["PLACE_REST", "REPRICE_REST", "HOLD_REST"].includes(frozen.action);
  const proposed = upperLayersLicensed && v52f.lawfulCent(frozen.target_cents) ? frozen.target_cents : null;
  const conservation = jointTargetConservation(inputs, proposed);
  const license = frozen.birth_license ? { ...frozen.birth_license, joint_target_conservation: conservation } : null;
  if (proposed === null || !conservation.target_changed) return { ...frozen, birth_license: license, joint_target_conservation: conservation };
  if (!conservation.passed) throw new Error("V52g joint identity failed after target bound");
  const target = conservation.licensed_target_cents;
  const active = v52f.lawfulCent(inputs.activeTarget) ? inputs.activeTarget : null;
  const action = active === null ? "PLACE_REST" : active === target ? "HOLD_REST" : "REPRICE_REST";
  const boundedLicense = {
    ...license,
    level: {
      ...license.level,
      target_cents: target,
      pre_clause_6_target_cents: proposed,
      joint_identity_bound_cents: conservation.max_lawful_target_cents,
      authority: `${license.level.authority}+V52G_JOINT_TARGET_CONSERVATION`,
    },
  };
  return {
    ...frozen,
    action,
    target_cents: target,
    ...(action === "REPRICE_REST" ? { direction: target > active ? "UP" : "DOWN" } : { direction: undefined }),
    reason: action === "HOLD_REST" ? "V52G_JOINT_BOUND_ALREADY_STANDING" : "V52G_LICENSED_TARGET_JOINT_BOUND",
    placement: { ...(frozen.placement ?? {}), target_cents: target, pre_clause_6_target_cents: proposed, joint_target_conservation: conservation },
    birth_license: boundedLicense,
    joint_target_conservation: conservation,
    judgment_gate: { ...(frozen.judgment_gate ?? {}), verdict: action === "HOLD_REST" ? "LICENSED_HOLD" : "POST", failure: null, clause_6: "JOINT_TARGET_CONSERVATION_AT_OR_BELOW_99" },
    unguarded_decision: frozen,
  };
}

function decideReceipt(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const atomic = v52f.decideReceipt({ ...inputs, clauses: { ...clauses, joint_target_conservation: false } });
  return { ...atomic, decision: gateDecision({ ...inputs, clauses }, atomic.decision.unguarded_decision ?? atomic.decision), joint_target_conservation_enabled: Boolean(clauses.joint_target_conservation) };
}

function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const incumbent = v52f.decide({ ...inputs, clauses: { ...clauses, joint_target_conservation: false } });
  return gateDecision({ ...inputs, clauses }, incumbent.unguarded_decision ?? incumbent);
}

module.exports = { ...v52f, normalizedClauses, jointTargetConservation, gateDecision, decideReceipt, decide };
