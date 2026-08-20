"use strict";

// V53-02 is a lift-only overlay on the frozen V52l-lineage current-level
// machinery.  The lineage decision is always computed first.  Missing view
// inputs abstain, never gate.  Clause 5/6 conservation remains authoritative;
// if clause 6 blocks a proposed lift, the lineage behavior is returned.

const viewOrgan = require("./window1_v53_understanding_organ.js");
const frozen = require("./window1_v52h_remove_pair_lows_precondition.js");

const PAR_CENTS = 100;
const TAPE_TICK_CENTS = 1;

function lawfulCent(value) { return Number.isInteger(value) && value >= 1 && value <= 99; }

function buildGameView(states, context) {
  const view = viewOrgan.buildGameView(states, context);
  return {
    ...view,
    provenance: {
      ...view.provenance,
      post_onset_only: true,
      v53_02_plan_v2: "LINEAGE_CURRENT_LEVEL_PLUS_LIFT_ONLY_VIEW_BOUNDS",
    },
  };
}

function buildPlan(gameView, context) {
  const ids = Object.keys(gameView.legs).sort();
  const lows = Object.fromEntries(ids.map((id) => [id, gameView.legs[id].reach.running_session_low_cents]));
  const lowsComplete = ids.every((id) => lawfulCent(lows[id]));
  const lowSum = lowsComplete ? lows[ids[0]] + lows[ids[1]] : null;
  const deltaGoal = lowsComplete ? Math.max(TAPE_TICK_CENTS, PAR_CENTS - lowSum) : null;
  const pairBudget = Number.isInteger(deltaGoal) ? PAR_CENTS - deltaGoal : null;
  const ownerCandidates = ids.filter((id) => {
    const role = gameView.legs[id].role;
    return role.value === "FALLER"
      && gameView.legs[id].leg_state.value === "STEPPING"
      && Number.isInteger(role.TRD5_print_count)
      && role.TRD5_print_count >= role.TRD5_gate;
  });
  const owner = ownerCandidates.length === 1 ? ownerCandidates[0] : null;
  const depthBounds = Object.fromEntries(ids.map((id) => {
    if (!lawfulCent(lows[id])) return [id, { status: "UNBOUND_INPUT_ABSENT", bound_cents: null, source: "RUNNING_SESSION_LOW" }];
    if (id !== owner) return [id, { status: "BOUND", bound_cents: lows[id], source: "MAX_LINEAGE_TARGET_RUNNING_SESSION_LOW" }];
    const signedStep = context.states[id].last_step_cents;
    const observedStep = Number.isInteger(signedStep) && signedStep !== 0 ? Math.abs(signedStep) : null;
    if (!Number.isInteger(observedStep)) return [id, { status: "UNBOUND_INPUT_ABSENT", bound_cents: null, source: "RUNNING_SESSION_LOW_MINUS_LAST_OBSERVED_STEP", last_observed_step_cents: null }];
    return [id, {
      status: "BOUND",
      bound_cents: Math.max(TAPE_TICK_CENTS, lows[id] - observedStep),
      source: "MAX_LINEAGE_TARGET_RUNNING_SESSION_LOW_MINUS_LAST_OBSERVED_STEP",
      last_observed_step_cents: observedStep,
      last_observed_step_receipt: context.states[id].last_step_receipt,
    }];
  }));
  return {
    licensed: true,
    reason: lowsComplete ? "VIEW_BOUNDS_AVAILABLE_NO_GATE" : "VIEW_BOUNDS_PARTIAL_NO_GATE",
    inputs_complete: lowsComplete,
    missing_input_leg_ids: ids.filter((id) => !lawfulCent(lows[id])),
    delta_goal_cents: deltaGoal,
    delta_goal_formula: lowsComplete ? `max(${TAPE_TICK_CENTS},${PAR_CENTS}-${lowSum})=${deltaGoal}` : null,
    pair_budget_cents: pairBudget,
    running_low_sum_cents: lowSum,
    running_session_lows_cents: lows,
    owner_leg_id: owner,
    owner_candidates: ownerCandidates,
    owner_rule: "EXACTLY_ONE_FALLER_AND_STEPPING_AFTER_TRD5_RIPENESS",
    depth_bounds: depthBounds,
    pair_running_session_low_incomplete_gate_removed: true,
    evidence_receipt: context.row.receipt,
  };
}

function normalizedClauses(value = {}) {
  return {
    ...frozen.normalizedClauses(value),
    v53_understanding_bounds: Boolean(value.v53_understanding_bounds),
    pair_entry_conservation: true,
    joint_target_conservation: true,
    remove_pair_lows_precondition: true,
    scavenger: false,
  };
}

function lineageSummary(decision) {
  return {
    action: decision?.action ?? null,
    target_cents: lawfulCent(decision?.target_cents) ? decision.target_cents : null,
    reason: decision?.reason ?? null,
    gate_verdict: decision?.judgment_gate?.verdict ?? null,
    gate_failure: decision?.judgment_gate?.failure ?? null,
    level_authority: decision?.birth_license?.level?.authority ?? decision?.placement?.authority ?? null,
  };
}

function liftProposal(plan, inputs, lineageTarget) {
  const bound = plan?.depth_bounds?.[inputs.legId] ?? null;
  const counterpart = inputs.siblingCredited === true ? inputs.siblingEntryCents : inputs.siblingStandingTarget;
  const base = {
    applicable: false,
    reason: null,
    lineage_target_cents: lineageTarget,
    depth_bound_cents: lawfulCent(bound?.bound_cents) ? bound.bound_cents : null,
    desired_target_cents: lineageTarget,
    allocated_target_cents: lineageTarget,
    pair_budget_cents: Number.isInteger(plan?.pair_budget_cents) ? plan.pair_budget_cents : null,
    counterpart_cents: lawfulCent(counterpart) ? counterpart : null,
    owner_leg_id: plan?.owner_leg_id ?? null,
    allocation_priority: inputs.legId === plan?.owner_leg_id ? "NON_OWNER_ALREADY_STANDING_THEN_OWNER" : "NON_OWNER_FIRST",
  };
  if (!lawfulCent(lineageTarget)) return { ...base, reason: "LINEAGE_TARGET_NOT_LICENSED" };
  if (!lawfulCent(bound?.bound_cents)) return { ...base, reason: "VIEW_BOUND_INPUT_ABSENT_LINEAGE_UNCHANGED" };
  if (!Number.isInteger(plan?.pair_budget_cents) || !lawfulCent(counterpart)) return { ...base, reason: "PAIR_ALLOCATION_INPUT_ABSENT_LINEAGE_UNCHANGED" };
  const desired = Math.max(lineageTarget, bound.bound_cents);
  const allocationCap = plan.pair_budget_cents - counterpart;
  if (!lawfulCent(allocationCap) || allocationCap < lineageTarget) return {
    ...base,
    applicable: true,
    reason: "PAIR_BUDGET_CONFLICT_LINEAGE_UNCHANGED",
    desired_target_cents: desired,
    allocation_cap_cents: Number.isInteger(allocationCap) ? allocationCap : null,
  };
  return {
    ...base,
    applicable: true,
    reason: desired > lineageTarget ? "LIFT_PROPOSED" : "DEPTH_BOUND_ALREADY_SATISFIED",
    desired_target_cents: desired,
    allocation_cap_cents: allocationCap,
    allocated_target_cents: Math.max(lineageTarget, Math.min(desired, allocationCap)),
  };
}

function annotateLineage(decision, inputs, plan, proposal, monotone) {
  const license = decision.birth_license ?? inputs.birthLicense ?? {};
  return {
    ...decision,
    birth_license: {
      ...license,
      game_view: inputs.v53GameView,
      plan,
      level: {
        ...(license.level ?? {}),
        lineage_target_cents: lawfulCent(decision.target_cents) ? decision.target_cents : null,
        v53_02_lift_only: proposal,
        N9_role: "ADVISORY_ONLY_NOT_TARGET_AUTHORITY",
      },
    },
    lineage_decision: lineageSummary(decision),
    lineage_target_cents: lawfulCent(decision.target_cents) ? decision.target_cents : null,
    v53_monotone_lift: monotone,
    v53_understanding_bounds_enabled: true,
  };
}

function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.v53_understanding_bounds) return frozen.decide({ ...inputs, clauses });
  const lineage = frozen.decide({ ...inputs, clauses });
  const lineageTarget = lawfulCent(lineage.target_cents) ? lineage.target_cents : null;
  const lineageLicensed = lineage.judgment_gate?.failure == null
    && ["PLACE_REST", "REPRICE_REST", "HOLD_REST"].includes(lineage.action)
    && lawfulCent(lineageTarget);
  const plan = inputs.v53Plan ?? { licensed: true, reason: "VIEW_PLAN_ABSENT_NO_GATE", depth_bounds: {} };
  const proposal = liftProposal(plan, inputs, lineageTarget);
  const noLift = (reason, extra = {}) => annotateLineage(lineage, inputs, { ...plan, allocation: proposal }, proposal, {
    applicable: lineageLicensed,
    checked: lineageLicensed,
    passed: true,
    lineage_target_cents: lineageTarget,
    final_target_cents: lineageTarget,
    lift_applied: false,
    fallback_to_lineage: true,
    reason,
    ...extra,
  });
  if (!lineageLicensed) return noLift("LINEAGE_NOT_LICENSED_OVERLAY_ABSTAINS");
  if (!proposal.applicable || proposal.allocated_target_cents === lineageTarget) return noLift(proposal.reason ?? "NO_LIFT_AVAILABLE");
  if (!lawfulCent(inputs.book?.ask) || proposal.desired_target_cents >= inputs.book.ask) return noLift("LINEAGE_CURRENT_LEVEL_TOUCH_LIMIT_BLOCKED_LIFT");

  const desiredSettlement = frozen.settlementIdentity(inputs, proposal.desired_target_cents);
  const desiredJoint = frozen.jointTargetConservation(inputs, desiredSettlement.licensed_target_cents);
  if (desiredJoint.target_changed) return noLift("CLAUSE_6_BLOCKED_LIFT_LINEAGE_UNCHANGED", { clause_6_probe: desiredJoint });

  let target = proposal.allocated_target_cents;
  if (target >= inputs.book.ask) return noLift("ALLOCATION_TOUCH_LIMIT_BLOCKED_LIFT");
  const settlement = frozen.settlementIdentity(inputs, target);
  target = settlement.licensed_target_cents;
  const joint = frozen.jointTargetConservation(inputs, target);
  target = joint.licensed_target_cents;
  if (!lawfulCent(target) || target < lineageTarget) return noLift("MONOTONE_LIFT_GUARD_HELD_LINEAGE_TARGET", { attempted_target_cents: target });
  if (joint.target_changed) return noLift("CLAUSE_6_BLOCKED_LIFT_LINEAGE_UNCHANGED", { clause_6_probe: joint });
  if (target === lineageTarget) return noLift("CONSERVATION_REMOVED_LIFT_LINEAGE_UNCHANGED");

  const active = lawfulCent(inputs.activeTarget) ? inputs.activeTarget : null;
  const action = active === null ? "PLACE_REST" : active === target ? "HOLD_REST" : "REPRICE_REST";
  const allocation = { ...proposal, allocated_target_cents: target, target_sum_cents: target + proposal.counterpart_cents };
  const finalPlan = { ...plan, allocation };
  const baseLicense = lineage.birth_license ?? inputs.birthLicense ?? {};
  const license = {
    ...baseLicense,
    game_view: inputs.v53GameView,
    plan: finalPlan,
    level: {
      ...(baseLicense.level ?? {}),
      target_cents: target,
      lineage_target_cents: lineageTarget,
      v53_02_lift_only: allocation,
      N9_role: "ADVISORY_ONLY_NOT_TARGET_AUTHORITY",
      authority: `${baseLicense.level?.authority ?? lineage.placement?.authority ?? "FROZEN_LINEAGE_CURRENT_LEVEL"}+V53_02_LIFT_ONLY_VIEW_BOUND`,
    },
    pair_entry_conservation: settlement,
    joint_target_conservation: joint,
  };
  const monotone = {
    applicable: true,
    checked: true,
    passed: target >= lineageTarget,
    lineage_target_cents: lineageTarget,
    final_target_cents: target,
    lift_applied: true,
    fallback_to_lineage: false,
    reason: "MONOTONE_LIFT_APPLIED",
  };
  return {
    ...lineage,
    action,
    target_cents: target,
    ...(action === "REPRICE_REST" ? { direction: target > active ? "UP" : "DOWN" } : { direction: undefined }),
    reason: action === "HOLD_REST" ? "V53_02_LIFT_TARGET_ALREADY_STANDING" : "V53_02_LINEAGE_TARGET_LIFTED_BY_VIEW_BOUND",
    placement: { ...(lineage.placement ?? {}), target_cents: target, lineage_target_cents: lineageTarget, authority: license.level.authority },
    birth_license: license,
    pair_entry_conservation: settlement,
    joint_target_conservation: joint,
    lineage_decision: lineageSummary(lineage),
    lineage_target_cents: lineageTarget,
    v53_monotone_lift: monotone,
    v53_understanding_bounds_enabled: true,
    judgment_gate: { ...(lineage.judgment_gate ?? {}), verdict: action === "HOLD_REST" ? "LICENSED_HOLD" : "POST", failure: null, clause_3: "FROZEN_LINEAGE_PLUS_V53_02_LIFT_ONLY_BOUND", clause_5: "FROZEN", clause_6: "FROZEN" },
  };
}

function decideReceipt(inputs) { return { decision: decide(inputs), v53_understanding_bounds_enabled: true }; }

module.exports = {
  ...viewOrgan,
  buildGameView,
  buildPlan,
  normalizedClauses,
  liftProposal,
  decide,
  decideReceipt,
};
