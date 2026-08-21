"use strict";

// V54 is a game-level policy over the frozen V52l champion.  It changes only
// the strengthening-side entry stance after a causal pair polarity resolves.
// The fading side and every undecided game remain byte-equal to the champion.

const view = require("./window1_v53_understanding_organ.js");
const frozen = require("./window1_v52h_remove_pair_lows_precondition.js");

const PAR_BUDGET_CENTS = 99;
const POST_ONLY_TICK_CENTS = 1;
const TRD5_PRINT_COUNT = view.TRD5_PRINT_COUNT;
const ROLE_DRIFT_CENTS = view.ROLE_DRIFT_CENTS;
const PROVENANCE = Object.freeze({
  pair_model: Object.freeze({
    dispatch: "V54_THE_PAIR_MODEL",
    ruling_date: "2026-08-21",
    laws: ["L0", "L6", "L8", "L10", "L12", "L13", "L16", "L17", "L18", "L20", "L21", "L22", "L23"],
  }),
  formation_anchor: Object.freeze({
    law: "L16",
    method: "SPREAD_SETTLE_MID_AT_FORMATION_END_SERIES_FLOORED",
    source_commit: "c0056976",
    source_path: ".claude/window1_second_seat/w1_ground_truth_20260814/W1_GROUND_TRUTH_TABLE.json",
  }),
  role: Object.freeze({
    method: "TRD5_DRIFT_FROM_L16_FORMATION_ANCHOR",
    threshold_cents: ROLE_DRIFT_CENTS,
    threshold_provenance: view.V53_CONSTANT_PROVENANCE.ROLE_DRIFT_CENTS,
    minimum_true_prints: TRD5_PRINT_COUNT,
  }),
  conservation: Object.freeze({
    clause_5: "FROZEN_V52L_PAIR_ENTRY_CONSERVATION",
    clause_6: "FROZEN_V52L_JOINT_TARGET_CONSERVATION",
  }),
});

function lawfulCent(value) { return Number.isInteger(value) && value >= 1 && value <= 99; }
function direction(value) {
  if (value === "CLIMBER" || value === "RISING") return "STRENGTHENING";
  if (value === "FALLER" || value === "FALLING") return "FADING";
  return null;
}
function opposite(value) { return value === "STRENGTHENING" ? "FADING" : value === "FADING" ? "STRENGTHENING" : null; }

function emptyLegState(onsetTimestampEpoch) { return view.emptyLegState(onsetTimestampEpoch); }
function observePostOnset(state, row) { return view.observePostOnset(state, row); }

function compactRead(read) {
  return {
    state: read?.state ?? null,
    receipt: read?.receipt ?? null,
    quote_path_state: read?.quote_path_state ?? null,
    pressure_state: read?.pressure_state ?? null,
    directional_evidence_receipt: read?.directional_evidence_receipt ?? null,
    directional_evidence_kind: read?.directional_evidence_kind ?? null,
  };
}

function buildGameView(states, context) {
  const base = view.buildGameView(states, context);
  const ids = Object.keys(states).sort();
  const legs = {};
  for (const id of ids) {
    const baseLeg = base.legs[id];
    const anchor = context.formation_anchors?.[id] ?? null;
    const current = baseLeg.current_observation?.value ?? null;
    const currentReference = current?.reference_cents ?? null;
    const drift = lawfulCent(anchor?.value_cents) && lawfulCent(currentReference) ? currentReference - anchor.value_cents : null;
    const prints = states[id].prints.length;
    let role = "UNRIPE";
    let roleReason = "TRD5_OR_L16_ANCHOR_NOT_YET_AVAILABLE";
    if (!String(context.category).startsWith("WTA_CHALL") && lawfulCent(anchor?.value_cents) && Number.isFinite(anchor?.formation_end_epoch) && context.row.ts >= anchor.formation_end_epoch && prints >= TRD5_PRINT_COUNT && Number.isInteger(drift)) {
      if (drift >= ROLE_DRIFT_CENTS) { role = "CLIMBER"; roleReason = "TRD5_DRIFT_AT_OR_ABOVE_POSITIVE_ROLE_THRESHOLD"; }
      else if (drift <= -ROLE_DRIFT_CENTS) { role = "FALLER"; roleReason = "TRD5_DRIFT_AT_OR_BELOW_NEGATIVE_ROLE_THRESHOLD"; }
      else roleReason = "TRD5_DRIFT_INSIDE_ROLE_DEADBAND";
    }
    legs[id] = {
      identity: id,
      current_observation: baseLeg.current_observation,
      l16_formation_anchor: {
        value_cents: lawfulCent(anchor?.value_cents) ? anchor.value_cents : null,
        formation_end_epoch: Number.isFinite(anchor?.formation_end_epoch) ? anchor.formation_end_epoch : null,
        source_receipt: anchor?.source_receipt ?? null,
        provenance: PROVENANCE.formation_anchor,
      },
      travel_from_l16_anchor: { value_cents: drift, current_reference_cents: currentReference, producer_receipt: current?.receipt ?? null },
      role: { value: role, reason: roleReason, print_count: prints, producer_receipt: current?.receipt ?? null, provenance: PROVENANCE.role },
      machine_read: compactRead(context.joint_reads?.[id]),
      champion_state: context.machine_states?.[id] ?? null,
      bought_entry_cents: lawfulCent(context.positions?.[id]?.entry_cents) ? context.positions[id].entry_cents : null,
      standing_target_cents: lawfulCent(context.positions?.[id]?.standing_target_cents) ? context.positions[id].standing_target_cents : null,
    };
  }
  return {
    event_id: context.event_id,
    evaluation: { timestamp_epoch: context.row.ts, receipt: context.row.receipt },
    legs,
    provenance: { ...PROVENANCE, causal_prefix_only: true, post_onset_only: true, endpoint_labels_consumed: false, span_fraction_consumed: false, no_span_fraction_consumed: true, no_static_depth_target_consumed: true },
  };
}

function undecided(ids, evidence, reason) {
  return {
    tag: "UNDECIDED",
    strengthening_leg_id: null,
    fading_leg_id: null,
    reason,
    evidence,
    evidence_needed: "OPPOSITE_TRD5_ROLES_WITH_NO_CONTRADICTION_FROM_PRESSURE_JOINT_STATE_OR_L16_TRAVEL",
    type_invariant: ids.length === 2,
  };
}

function polarity(gameView) {
  const ids = Object.keys(gameView.legs).sort();
  const evidence = Object.fromEntries(ids.map((id) => {
    const leg = gameView.legs[id];
    return [id, {
      role: leg.role,
      pressure_direction: direction(leg.machine_read.pressure_state),
      joint_state_direction: direction(leg.machine_read.state),
      travel_direction: Number.isInteger(leg.travel_from_l16_anchor.value_cents) && Math.abs(leg.travel_from_l16_anchor.value_cents) >= ROLE_DRIFT_CENTS
        ? (leg.travel_from_l16_anchor.value_cents > 0 ? "STRENGTHENING" : "FADING") : null,
      read_receipt: leg.machine_read.receipt,
    }];
  }));
  if (ids.length !== 2) return undecided(ids, evidence, "PAIR_REQUIRES_EXACTLY_TWO_EXPRESSIONS");
  const roleDirections = ids.map((id) => direction(gameView.legs[id].role.value));
  if (!roleDirections[0] || !roleDirections[1]) return undecided(ids, evidence, "ROLE_INSTRUMENT_NOT_RESOLVED_ON_BOTH_EXPRESSIONS");
  if (roleDirections[0] === roleDirections[1]) return undecided(ids, evidence, "ROLE_INSTRUMENT_DID_NOT_PRODUCE_OPPOSITE_PAIR");
  for (const [index, id] of ids.entries()) {
    const required = roleDirections[index];
    for (const field of ["pressure_direction", "joint_state_direction", "travel_direction"]) {
      const observed = evidence[id][field];
      if (observed && observed !== required) return undecided(ids, evidence, `ROLE_DISAGREES_WITH_${field.toUpperCase()}_${id}`);
    }
  }
  const strengthening = ids[roleDirections.indexOf("STRENGTHENING")];
  const fading = ids.find((id) => id !== strengthening);
  return {
    tag: "DECIDED",
    strengthening_leg_id: strengthening,
    fading_leg_id: fading,
    reason: "OPPOSITE_TRD5_ROLES_COHERENT_WITH_PRESSURE_JOINT_STATE_AND_L16_TRAVEL",
    evidence,
    type_invariant: strengthening !== fading && ids.includes(strengthening) && ids.includes(fading),
  };
}

function buildPlan(gameView, context) {
  const ids = Object.keys(gameView.legs).sort();
  const pairPolarity = polarity(gameView);
  const windows = pairPolarity.tag === "DECIDED"
    ? { [pairPolarity.strengthening_leg_id]: "EARLY", [pairPolarity.fading_leg_id]: "LATE" }
    : Object.fromEntries(ids.map((id) => [id, "LATE"]));
  const anchorTargets = Object.fromEntries(ids.map((id) => [id, gameView.legs[id].l16_formation_anchor.value_cents]));
  return {
    model: "V54_PAIR_MODEL",
    licensed: true,
    evaluation_receipt: context.row.receipt,
    evaluation_timestamp_epoch: context.row.ts,
    polarity: pairPolarity,
    windows,
    l16_anchor_targets_cents: anchorTargets,
    undecided_fallback: pairPolarity.tag === "UNDECIDED" ? "FROZEN_CHAMPION_BYTE_EQUAL" : null,
    fading_path: "FROZEN_CHAMPION_TRACKING_BYTE_EQUAL",
    strengthening_path: "STAND_EARLY_AT_OWN_L16_FORMATION_ANCHOR_CANCEL_ON_OWN_DOWN_PRESSURE",
    provenance: PROVENANCE,
  };
}

function normalizedClauses(value = {}) {
  return { ...frozen.normalizedClauses(value), v54_pair_model: Boolean(value.v54_pair_model), pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true, scavenger: false };
}

function conservationInputs(inputs) {
  return {
    sibling_credited: inputs.siblingCredited === true,
    sibling_entry_cents: lawfulCent(inputs.siblingEntryCents) ? inputs.siblingEntryCents : null,
    sibling_standing_target_cents: lawfulCent(inputs.siblingStandingTarget) ? inputs.siblingStandingTarget : null,
    pair_cap_cents: lawfulCent(inputs.pairCap) ? inputs.pairCap : null,
  };
}

function plannedSplit(inputs, plan, target) {
  const ids = Object.keys(plan?.windows ?? {}).sort();
  const siblingId = ids.find((id) => id !== inputs.legId) ?? null;
  const knownSibling = inputs.siblingCredited && lawfulCent(inputs.siblingEntryCents) ? inputs.siblingEntryCents
    : lawfulCent(inputs.siblingStandingTarget) ? inputs.siblingStandingTarget : null;
  const evaluated = lawfulCent(target) ? target : null;
  const sibling = lawfulCent(knownSibling) ? knownSibling : lawfulCent(evaluated) ? PAR_BUDGET_CENTS - evaluated : null;
  return {
    pair_budget_cents: PAR_BUDGET_CENTS,
    evaluated_leg_id: inputs.legId,
    evaluated_target_cents: evaluated,
    sibling_leg_id: siblingId,
    sibling_kind: inputs.siblingCredited ? "BOUGHT_SIDE" : lawfulCent(inputs.siblingStandingTarget) ? "STANDING_SIDE" : "RESERVED_SIDE",
    sibling_cents: sibling,
    sum_cents: lawfulCent(evaluated) && Number.isInteger(sibling) ? evaluated + sibling : null,
  };
}

function sentence(inputs, plan, target, adjustments, split) {
  const p = plan.polarity;
  if (p.tag === "UNDECIDED") {
    return `At receipt ${plan.evaluation_receipt}, pair polarity is UNDECIDED because ${p.reason}. Both expressions therefore remain in LATE windows and the frozen champion owns both levels. ${inputs.legId} evaluates ${target ?? "no lawful"} cents while ${split.sibling_kind.toLowerCase()} ${split.sibling_leg_id ?? "the sibling"} carries ${split.sibling_cents ?? "no"} cents; the joint budget is ${PAR_BUDGET_CENTS} cents. ${adjustments.join(" ") || "No pair-model price adjustment was made."}`;
  }
  return `At receipt ${plan.evaluation_receipt}, ${p.strengthening_leg_id} is STRENGTHENING and has the EARLY cheap window; ${p.fading_leg_id} is FADING and has the LATE tracked-floor window because ${p.reason}. ${p.strengthening_leg_id} stands from its own L16 formation anchor while ${p.fading_leg_id} remains on the byte-frozen tracking engine. This receipt evaluates ${inputs.legId} at ${target ?? "no lawful"} cents and reserves or fixes ${split.sibling_cents ?? "no"} cents for ${split.sibling_leg_id}; together they use ${split.sum_cents ?? "an unresolved"} of ${PAR_BUDGET_CENTS} cents. ${adjustments.join(" ") || "No pair-model price adjustment was made."}`;
}

function jointLicense(inputs, plan, lineage, decision, adjustments = []) {
  const split = plannedSplit(inputs, plan, decision.target_cents);
  const polarityInvariant = plan?.polarity?.tag === "UNDECIDED"
    ? plan.polarity.strengthening_leg_id === null && plan.polarity.fading_leg_id === null
    : plan?.polarity?.tag === "DECIDED" && plan.polarity.strengthening_leg_id !== plan.polarity.fading_leg_id;
  const text = plan ? sentence(inputs, plan, decision.target_cents, adjustments, split) : null;
  return {
    law: "L23_PAIR_UNIT_PROOF",
    model: "V54_PAIR_MODEL",
    complete: Boolean(plan && polarityInvariant && Object.keys(plan.windows ?? {}).length === 2 && split.sum_cents !== null && split.sum_cents <= PAR_BUDGET_CENTS && typeof text === "string" && text.trim().length > 0),
    polarity: plan?.polarity ?? null,
    windows: plan?.windows ?? null,
    both_levels: {
      strengthening_anchor_cents: plan?.polarity?.tag === "DECIDED" ? plan.l16_anchor_targets_cents[plan.polarity.strengthening_leg_id] : null,
      fading_tracking_authority: plan?.polarity?.tag === "DECIDED" ? "FROZEN_CHAMPION_TRACKING_ENGINE" : "FROZEN_CHAMPION_BOTH_LEGS",
      evaluated_target_cents: lawfulCent(decision.target_cents) ? decision.target_cents : null,
    },
    budget_split: split,
    sentence: text,
    sentence_machine_written_at_decision_time: true,
    evaluation_receipt: plan?.evaluation_receipt ?? inputs.book?.receipt ?? null,
    lineage_action: lineage.action,
    lineage_target_cents: lawfulCent(lineage.target_cents) ? lineage.target_cents : null,
    adjustments,
    provenance: PROVENANCE,
  };
}

function annotate(inputs, plan, lineage, decision, reason, adjustments = []) {
  const joint = jointLicense(inputs, plan, lineage, decision, adjustments);
  const license = decision.birth_license ?? lineage.birth_license ?? inputs.birthLicense ?? null;
  return {
    ...decision,
    reason,
    birth_license: license ? {
      ...license,
      game_view: inputs.v53GameView,
      plan,
      joint_license: joint,
      pair_entry_conservation: decision.pair_entry_conservation ?? license.pair_entry_conservation ?? null,
      joint_target_conservation: decision.joint_target_conservation ?? license.joint_target_conservation ?? null,
      level: { ...(license.level ?? {}), N9_role: "ADVISORY_ONLY_NOT_TARGET_AUTHORITY", v54_pair_model: { applied: reason.startsWith("V54_STRENGTHENING"), adjustments, provenance: PROVENANCE } },
    } : license,
    lineage_decision: { action: lineage.action, target_cents: lineage.target_cents, reason: lineage.reason },
    lineage_target_cents: lawfulCent(lineage.target_cents) ? lineage.target_cents : null,
    v54_pair_model: { enabled: true, polarity: plan?.polarity ?? null, window: plan?.windows?.[inputs.legId] ?? null, applied: reason.startsWith("V54_STRENGTHENING"), reason },
    conservation_input_identity: { lineage_inputs: conservationInputs(inputs), candidate_inputs: conservationInputs(inputs), byte_equal: true },
    joint_license: joint,
  };
}

function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const lineage = frozen.decide({ ...inputs, clauses });
  if (!clauses.v54_pair_model) return lineage;
  const plan = inputs.v53Plan;
  if (!plan || plan.polarity.tag === "UNDECIDED") return annotate(inputs, plan, lineage, lineage, "V54_UNDECIDED_CHAMPION_BYTE_EQUAL");
  if (inputs.legId === plan.polarity.fading_leg_id) return annotate(inputs, plan, lineage, lineage, "V54_FADING_TRACKING_ENGINE_BYTE_EQUAL");
  if (inputs.legId !== plan.polarity.strengthening_leg_id) throw new Error(`V54 pair polarity omitted evaluated leg ${inputs.legId}`);

  const ownRead = inputs.v53GameView?.legs?.[inputs.legId]?.machine_read ?? null;
  const downPressure = ownRead?.pressure_state === "FALLING" || ownRead?.state === "FALLING";
  const activeFromV54Early = inputs.activeOrderBirthLicense?.joint_license?.model === "V54_PAIR_MODEL"
    && inputs.activeOrderBirthLicense.joint_license.windows?.[inputs.legId] === "EARLY";
  if (downPressure) {
    const decision = activeFromV54Early
      ? { ...lineage, action: "CANCEL_REST", target_cents: null, judgment_gate: { ...(lineage.judgment_gate ?? {}), verdict: "BLOCKED", failure: "STRENGTHENING_OWN_DOWN_PRESSURE_REVERSED_EARLY_CALL" } }
      : lineage;
    return annotate(inputs, plan, lineage, decision, activeFromV54Early ? "V54_STRENGTHENING_EARLY_BID_CANCELLED_ON_OWN_DOWN_PRESSURE" : "V54_STRENGTHENING_DOWN_PRESSURE_CHAMPION_FALLBACK", ["Own down-pressure evidence reversed the early call; the pair model did not retain an early bid."]);
  }

  const anchor = plan.l16_anchor_targets_cents[inputs.legId];
  if (!lawfulCent(anchor) || !inputs.birthLicense?.onset?.passed || !inputs.birthLicense?.read?.passed) {
    return annotate(inputs, plan, lineage, lineage, "V54_STRENGTHENING_AUTHORITY_INCOMPLETE_CHAMPION_BYTE_EQUAL");
  }
  const adjustments = [];
  let target = anchor;
  if (lawfulCent(inputs.book?.ask) && target >= inputs.book.ask) {
    const postOnly = inputs.book.ask - POST_ONLY_TICK_CENTS;
    adjustments.push(`The L16 anchor ${target} was reduced to ${postOnly} because the current ask ${inputs.book.ask} requires a post-only rest below the offer.`);
    target = postOnly;
  }
  const preConservation = target;
  const settlement = frozen.settlementIdentity(inputs, target);
  target = settlement.licensed_target_cents;
  const joint = frozen.jointTargetConservation(inputs, target);
  target = joint.licensed_target_cents;
  if (target !== preConservation) adjustments.push(`Frozen clauses 5 and 6 reduced the early target from ${preConservation} to ${target}.`);
  if (!lawfulCent(target)) return annotate(inputs, plan, lineage, lineage, "V54_STRENGTHENING_CONSERVATION_UNLAWFUL_CHAMPION_BYTE_EQUAL", adjustments);
  const active = lawfulCent(inputs.activeTarget) ? inputs.activeTarget : null;
  const action = active === null ? "PLACE_REST" : active === target ? "HOLD_REST" : "REPRICE_REST";
  const decision = {
    ...lineage,
    action,
    target_cents: target,
    ...(action === "REPRICE_REST" ? { direction: target > active ? "UP" : "DOWN" } : {}),
    placement: { target_cents: target, authority: "V54_STRENGTHENING_L16_FORMATION_ANCHOR+FROZEN_CLAUSE_5+FROZEN_CLAUSE_6", evidence_receipt: plan.evaluation_receipt },
    pair_entry_conservation: settlement,
    joint_target_conservation: joint,
    judgment_gate: { enabled: true, verdict: action === "HOLD_REST" ? "LICENSED_HOLD" : "POST", failure: null, clause_3: "V54_PAIR_MODEL_STRENGTHENING_L16_ANCHOR", clause_5: "FROZEN", clause_6: "FROZEN" },
  };
  return annotate(inputs, plan, lineage, decision, "V54_STRENGTHENING_EARLY_ANCHOR_BID", adjustments);
}

function decideReceipt(inputs) { return { decision: decide(inputs), v54_pair_model_enabled: true }; }

module.exports = {
  ...frozen,
  PAR_BUDGET_CENTS,
  POST_ONLY_TICK_CENTS,
  PROVENANCE,
  emptyLegState,
  observePostOnset,
  buildGameView,
  polarity,
  buildPlan,
  normalizedClauses,
  conservationInputs,
  jointLicense,
  decide,
  decideReceipt,
};
