"use strict";

// V53-03 is a single lift-only bound on the frozen V52l-lineage target.
// The frozen lineage decision speaks first.  A leg may lift only to its own
// running post-onset session low, and only when both frozen read classes say
// SETTLED with their own causal support present.  There is no pair budget,
// delta goal, owner allowance, or allocation overlay here.

const viewOrgan = require("./window1_v53_understanding_organ.js");
const frozen = require("./window1_v52h_remove_pair_lows_precondition.js");

function lawfulCent(value) { return Number.isInteger(value) && value >= 1 && value <= 99; }

function buildGameView(states, context) {
  const view = viewOrgan.buildGameView(states, context);
  return {
    ...view,
    provenance: {
      ...view.provenance,
      post_onset_only: true,
      no_span_fraction_consumed: true,
      v53_03_plan_v3: "FROZEN_LINEAGE_TARGET_PLUS_SETTLED_READ_RUNNING_LOW_BOUND",
    },
  };
}

function buildPlan(gameView, context) {
  const ids = Object.keys(gameView.legs).sort();
  return {
    licensed: true,
    reason: "PER_LEG_READ_LICENSED_BOUND_NEVER_PAIR_GATE",
    bounds: Object.fromEntries(ids.map((id) => [id, {
      running_session_low_cents: gameView.legs[id].reach.running_session_low_cents,
      running_session_low_receipt: gameView.legs[id].reach.producer_receipt,
      source: "OWN_POST_ONSET_RUNNING_SESSION_LOW",
    }])),
    delta_goal_deleted: true,
    pair_budget_derivation_deleted: true,
    owner_allowance_deleted: true,
    allocation_overlay_deleted: true,
    evidence_receipt: context.row.receipt,
  };
}

function normalizedClauses(value = {}) {
  return {
    ...frozen.normalizedClauses(value),
    v53_read_licensed_bound: Boolean(value.v53_read_licensed_bound),
    pair_entry_conservation: true,
    joint_target_conservation: true,
    remove_pair_lows_precondition: true,
    scavenger: false,
  };
}

function readLicensedBound(inputs, plan) {
  const read = inputs.birthLicense?.read ?? null;
  const full = read?.full_post_onset_evidence ?? null;
  const quoteRipe = read?.passed === true && full?.sufficient === true;
  const pressureRipe = Number.isFinite(inputs.book?.depth_ratio) && ["RISING", "FALLING", "SETTLED"].includes(read?.pressure_state);
  const quoteSettled = read?.quote_path_state === "SETTLED";
  const pressureSettled = read?.pressure_state === "SETTLED";
  const bound = plan?.bounds?.[inputs.legId] ?? null;
  const low = lawfulCent(bound?.running_session_low_cents) ? bound.running_session_low_cents : null;
  return {
    authorized: quoteRipe && pressureRipe && quoteSettled && pressureSettled && lawfulCent(low),
    reason: !quoteRipe ? "QUOTE_PATH_CLASS_UNRIPE"
      : !pressureRipe ? "PRESSURE_CLASS_UNRIPE"
        : !quoteSettled ? "QUOTE_PATH_NOT_SETTLED"
          : !pressureSettled ? "PRESSURE_NOT_SETTLED"
            : !lawfulCent(low) ? "RUNNING_SESSION_LOW_INPUT_ABSENT"
              : "BOTH_READ_CLASSES_SETTLED_AND_RIPE",
    quote_path: {
      state: read?.quote_path_state ?? null,
      ripe: quoteRipe,
      evidence: full,
      ripeness_law: "FROZEN_FULL_POST_ONSET_READ_SUFFICIENCY",
    },
    pressure: {
      state: read?.pressure_state ?? null,
      ripe: pressureRipe,
      depth_ratio: Number.isFinite(inputs.book?.depth_ratio) ? inputs.book.depth_ratio : null,
      evaluation_receipt: inputs.book?.receipt ?? null,
      ripeness_law: "FROZEN_JUL6_PRESSURE_CLASS_PRESENT_AT_RECEIPT",
    },
    running_session_low_cents: low,
    running_session_low_receipt: bound?.running_session_low_receipt ?? null,
    evaluation_receipt: inputs.book?.receipt ?? null,
    no_span_fraction_consumed: true,
  };
}

function conservationInputs(inputs) {
  return {
    sibling_credited: inputs.siblingCredited === true,
    sibling_entry_cents: Number.isInteger(inputs.siblingEntryCents) ? inputs.siblingEntryCents : null,
    sibling_standing_target_cents: Number.isInteger(inputs.siblingStandingTarget) ? inputs.siblingStandingTarget : null,
    pair_cap_cents: Number.isInteger(inputs.pairCap) ? inputs.pairCap : null,
  };
}

function lineageSummary(decision) {
  return {
    action: decision?.action ?? null,
    target_cents: lawfulCent(decision?.target_cents) ? decision.target_cents : null,
    reason: decision?.reason ?? null,
    pair_entry_conservation: decision?.pair_entry_conservation ?? decision?.birth_license?.pair_entry_conservation ?? null,
    joint_target_conservation: decision?.joint_target_conservation ?? decision?.birth_license?.joint_target_conservation ?? null,
  };
}

function annotateLineage(decision, inputs, plan, bound, reason) {
  const target = lawfulCent(decision?.target_cents) ? decision.target_cents : null;
  const snapshot = conservationInputs(inputs);
  const license = decision.birth_license ?? inputs.birthLicense ?? null;
  return {
    ...decision,
    ...(license ? {
      birth_license: {
        ...license,
        game_view: inputs.v53GameView,
        plan,
        level: {
          ...(license.level ?? {}),
          lineage_target_cents: target,
          v53_03_read_licensed_bound: { ...bound, applied: false, final_target_cents: target, reason },
          N9_role: "ADVISORY_ONLY_NOT_TARGET_AUTHORITY",
        },
      },
    } : {}),
    lineage_decision: lineageSummary(decision),
    lineage_target_cents: target,
    v53_read_licensed_bound: { ...bound, applied: false, lineage_target_cents: target, final_target_cents: target, reason },
    conservation_input_identity: { lineage_inputs: snapshot, candidate_inputs: { ...snapshot }, byte_equal: true },
    v53_read_licensed_bound_enabled: true,
  };
}

function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.v53_read_licensed_bound) return frozen.decide({ ...inputs, clauses });
  const lineage = frozen.decide({ ...inputs, clauses });
  const lineageTarget = lawfulCent(lineage.target_cents) ? lineage.target_cents : null;
  const lineageLicensed = lineage.judgment_gate?.failure == null
    && ["PLACE_REST", "REPRICE_REST", "HOLD_REST"].includes(lineage.action)
    && lawfulCent(lineageTarget);
  const plan = inputs.v53Plan ?? { licensed: true, reason: "PLAN_ABSENT_OVERLAY_ABSTAINS", bounds: {} };
  const bound = readLicensedBound(inputs, plan);
  if (!lineageLicensed) return annotateLineage(lineage, inputs, plan, bound, "LINEAGE_NOT_LICENSED_OVERLAY_ABSTAINS");
  if (!bound.authorized) return annotateLineage(lineage, inputs, plan, bound, bound.reason);

  const desired = Math.max(lineageTarget, bound.running_session_low_cents);
  if (desired === lineageTarget) return annotateLineage(lineage, inputs, plan, bound, "LINEAGE_ALREADY_AT_OR_ABOVE_BOUND");
  if (!lawfulCent(inputs.book?.ask) || desired >= inputs.book.ask) return annotateLineage(lineage, inputs, plan, bound, "FROZEN_POST_ONLY_TOUCH_BOUND_BLOCKED_LIFT");

  const snapshot = conservationInputs(inputs);
  const settlement = frozen.settlementIdentity(inputs, desired);
  const joint = frozen.jointTargetConservation(inputs, settlement.licensed_target_cents);
  const target = joint.licensed_target_cents;
  if (!lawfulCent(target) || target < lineageTarget) return annotateLineage(lineage, inputs, plan, bound, "FROZEN_CONSERVATION_BLOCKED_LIFT_LINEAGE_UNCHANGED");
  if (target === lineageTarget) return annotateLineage(lineage, inputs, plan, bound, "FROZEN_CONSERVATION_REMOVED_LIFT_LINEAGE_UNCHANGED");

  const active = lawfulCent(inputs.activeTarget) ? inputs.activeTarget : null;
  const action = active === null ? "PLACE_REST" : active === target ? "HOLD_REST" : "REPRICE_REST";
  const baseLicense = lineage.birth_license ?? inputs.birthLicense ?? {};
  const applied = {
    ...bound,
    applied: true,
    lineage_target_cents: lineageTarget,
    proposed_target_cents: desired,
    final_target_cents: target,
    lift_cents: target - lineageTarget,
    license_complete: Boolean(bound.running_session_low_receipt && bound.quote_path.evidence && bound.evaluation_receipt),
  };
  const license = {
    ...baseLicense,
    game_view: inputs.v53GameView,
    plan,
    level: {
      ...(baseLicense.level ?? {}),
      target_cents: target,
      lineage_target_cents: lineageTarget,
      v53_03_read_licensed_bound: applied,
      N9_role: "ADVISORY_ONLY_NOT_TARGET_AUTHORITY",
      authority: `${baseLicense.level?.authority ?? lineage.placement?.authority ?? "FROZEN_LINEAGE_CURRENT_LEVEL"}+V53_03_SETTLED_READ_RUNNING_LOW_BOUND`,
    },
    pair_entry_conservation: settlement,
    joint_target_conservation: joint,
  };
  return {
    ...lineage,
    action,
    target_cents: target,
    ...(action === "REPRICE_REST" ? { direction: target > active ? "UP" : "DOWN" } : { direction: undefined }),
    reason: action === "HOLD_REST" ? "V53_03_READ_LICENSED_BOUND_ALREADY_STANDING" : "V53_03_SETTLED_READ_LICENSED_LIFT",
    placement: { ...(lineage.placement ?? {}), target_cents: target, lineage_target_cents: lineageTarget, authority: license.level.authority },
    birth_license: license,
    pair_entry_conservation: settlement,
    joint_target_conservation: joint,
    lineage_decision: lineageSummary(lineage),
    lineage_target_cents: lineageTarget,
    v53_read_licensed_bound: applied,
    conservation_input_identity: { lineage_inputs: snapshot, candidate_inputs: { ...snapshot }, byte_equal: true },
    v53_read_licensed_bound_enabled: true,
    judgment_gate: { ...(lineage.judgment_gate ?? {}), verdict: action === "HOLD_REST" ? "LICENSED_HOLD" : "POST", failure: null, clause_3: "FROZEN_LINEAGE_PLUS_V53_03_SETTLED_READ_BOUND", clause_5: "FROZEN_BYTE_EQUAL_INPUTS", clause_6: "FROZEN_BYTE_EQUAL_INPUTS" },
  };
}

function decideReceipt(inputs) { return { decision: decide(inputs), v53_read_licensed_bound_enabled: true }; }

module.exports = {
  ...viewOrgan,
  buildGameView,
  buildPlan,
  normalizedClauses,
  readLicensedBound,
  conservationInputs,
  decide,
  decideReceipt,
};
