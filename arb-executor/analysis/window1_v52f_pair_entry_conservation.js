"use strict";

// V52f adds one settlement-identity clause to frozen V52e. Once the sibling
// is credited, any newly licensed rest target is bounded so the pair cost is
// strictly below 100 cents. Clauses 1-4, N9, and crediting remain V52e.

const v52e = require("./window1_v52e_palantir_wiring.js");

function normalizedClauses(value = {}) {
  const clauses = v52e.normalizedClauses(value);
  return value.pair_entry_conservation ? { ...clauses, pair_entry_conservation: true } : clauses;
}

function settlementIdentity(inputs, proposedTarget) {
  const applicable = inputs.siblingCredited === true;
  if (proposedTarget === null) return {
    clause: "CLAUSE_5_PAIR_ENTRY_CONSERVATION",
    applicable,
    reached: false,
    passed: null,
    reason: "NO_LICENSED_REST_TARGET_TO_CHECK",
    proposed_target_cents: null,
    credited_sibling_entry_cents: applicable ? inputs.siblingEntryCents : null,
    max_lawful_target_cents: applicable && v52e.lawfulCent(inputs.siblingEntryCents) ? 99 - inputs.siblingEntryCents : null,
    licensed_target_cents: null,
  };
  if (!applicable) return {
    clause: "CLAUSE_5_PAIR_ENTRY_CONSERVATION",
    applicable: false,
    reached: true,
    passed: true,
    reason: "NO_CREDITED_SIBLING_YET",
    proposed_target_cents: proposedTarget,
    credited_sibling_entry_cents: null,
    max_lawful_target_cents: null,
    licensed_target_cents: proposedTarget,
  };
  if (!v52e.lawfulCent(inputs.siblingEntryCents)) throw new Error("V52f credited sibling entry missing or non-integer");
  const cap = 99 - inputs.siblingEntryCents;
  if (!v52e.lawfulCent(cap)) throw new Error(`V52f settlement cap unlawful ${cap}`);
  if (!Number.isInteger(inputs.pairCap) || inputs.pairCap !== cap) throw new Error(`V52f pair-cap mismatch ${inputs.pairCap} != ${cap}`);
  if (!v52e.lawfulCent(proposedTarget)) throw new Error(`V52f proposed licensed target unlawful ${proposedTarget}`);
  const licensed = Math.min(proposedTarget, cap);
  return {
    clause: "CLAUSE_5_PAIR_ENTRY_CONSERVATION",
    applicable: true,
    reached: true,
    passed: licensed + inputs.siblingEntryCents < 100,
    reason: proposedTarget <= cap ? "PROPOSED_TARGET_ALREADY_STRICTLY_UNDER_PAR" : "TARGET_BOUNDED_BY_SETTLEMENT_IDENTITY",
    arithmetic: `${licensed}+${inputs.siblingEntryCents}=${licensed + inputs.siblingEntryCents}<100`,
    operator: "target_cents <= 99 - credited_sibling_entry_cents",
    proposed_target_cents: proposedTarget,
    credited_sibling_entry_cents: inputs.siblingEntryCents,
    max_lawful_target_cents: cap,
    licensed_target_cents: licensed,
    target_changed: licensed !== proposedTarget,
  };
}

function gateDecision(inputs, incumbent) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.pair_entry_conservation) return v52e.gateDecision({ ...inputs, clauses }, incumbent);
  const frozen = v52e.gateDecision({ ...inputs, clauses: { ...clauses, pair_entry_conservation: false } }, incumbent);
  const upperLayersLicensed = frozen.judgment_gate?.failure == null && ["PLACE_REST", "REPRICE_REST", "HOLD_REST"].includes(frozen.action);
  const proposed = upperLayersLicensed && v52e.lawfulCent(frozen.target_cents) ? frozen.target_cents : null;
  const conservation = settlementIdentity(inputs, proposed);
  const license = frozen.birth_license ? { ...frozen.birth_license, pair_entry_conservation: conservation } : null;
  if (proposed === null || !conservation.applicable || !conservation.target_changed) {
    return { ...frozen, birth_license: license, pair_entry_conservation: conservation };
  }
  if (!conservation.passed) throw new Error("V52f settlement identity failed after target bound");
  const target = conservation.licensed_target_cents;
  const active = v52e.lawfulCent(inputs.activeTarget) ? inputs.activeTarget : null;
  const action = active === null ? "PLACE_REST" : active === target ? "HOLD_REST" : "REPRICE_REST";
  const boundedLicense = {
    ...license,
    level: {
      ...license.level,
      target_cents: target,
      pre_clause_5_target_cents: proposed,
      settlement_identity_bound_cents: conservation.max_lawful_target_cents,
      authority: `${license.level.authority}+V52F_PAIR_ENTRY_CONSERVATION`,
    },
  };
  return {
    ...frozen,
    action,
    target_cents: target,
    ...(action === "REPRICE_REST" ? { direction: target > active ? "UP" : "DOWN" } : { direction: undefined }),
    reason: action === "HOLD_REST" ? "V52F_SETTLEMENT_BOUND_ALREADY_STANDING" : "V52F_LICENSED_TARGET_SETTLEMENT_BOUND",
    placement: {
      ...(frozen.placement ?? {}),
      target_cents: target,
      pre_clause_5_target_cents: proposed,
      pair_entry_conservation: conservation,
    },
    birth_license: boundedLicense,
    pair_entry_conservation: conservation,
    judgment_gate: { ...(frozen.judgment_gate ?? {}), verdict: action === "HOLD_REST" ? "LICENSED_HOLD" : "POST", failure: null, clause_5: "PAIR_ENTRY_CONSERVATION_STRICTLY_UNDER_100" },
    unguarded_decision: frozen,
  };
}

function decideReceipt(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const atomic = v52e.decideReceipt({ ...inputs, clauses: { ...clauses, pair_entry_conservation: false } });
  return { ...atomic, decision: gateDecision({ ...inputs, clauses }, atomic.decision.unguarded_decision ?? atomic.decision), pair_entry_conservation_enabled: Boolean(clauses.pair_entry_conservation) };
}

function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const incumbent = v52e.decide({ ...inputs, clauses: { ...clauses, pair_entry_conservation: false } });
  return gateDecision({ ...inputs, clauses }, incumbent.unguarded_decision ?? incumbent);
}

module.exports = { ...v52e, normalizedClauses, settlementIdentity, gateDecision, decideReceipt, decide };
