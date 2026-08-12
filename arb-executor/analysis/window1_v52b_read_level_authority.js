"use strict";

// V52b changes exactly V52 clause 3.  When enabled, the frozen incumbent
// machine's receipt-local, post-only level may earn birth authority from the
// causal read in sight.  V52's true-trade diary remains in every license as a
// reference input but is not the sole level authority.  Onset, read,
// coherence, disagreement, guards, crediting, and scavenger laws are frozen.

const v52 = require("./window1_v52_judgment_gate.js");

function normalizedClauses(value = {}) {
  const clauses = v52.normalizedClauses(value);
  return value.machine_read_level_authority ? { ...clauses, machine_read_level_authority: true } : clauses;
}

function machineReadLevel(license, incumbent) {
  const unguarded = incumbent?.unguarded_decision ?? incumbent;
  const target = unguarded?.placement?.target_cents ?? unguarded?.target_cents ?? null;
  const authority = unguarded?.placement?.authority ?? unguarded?.reason ?? null;
  const evidence = license?.level?.machine_read_evidence ?? null;
  const onsetTs = license?.onset?.timestamp_epoch;
  const evaluationTs = evidence?.evaluation_timestamp_epoch;
  const readTs = evidence?.directional_evidence_timestamp_epoch;
  const bounds = evidence?.post_onset_observation_bounds ?? null;
  const supportedAuthority = typeof authority === "string" && (authority.startsWith("V41_") || authority.startsWith("V43_"));
  const insideBounds = v52.lawfulCent(target) && Number.isInteger(bounds?.min_cents) && Number.isInteger(bounds?.max_cents)
    && target >= bounds.min_cents && target <= bounds.max_cents;
  const postOnset = Number.isFinite(onsetTs) && Number.isFinite(evaluationTs) && Number.isFinite(readTs)
    && evaluationTs >= onsetTs && readTs >= onsetTs && readTs <= evaluationTs;
  const receiptBound = typeof evidence?.evaluation_receipt === "string" && evidence.evaluation_receipt.length > 0
    && typeof evidence?.directional_evidence_receipt === "string" && evidence.directional_evidence_receipt.length > 0;
  const authorized = supportedAuthority && insideBounds && postOnset && receiptBound;
  return {
    authorized,
    target_cents: authorized ? target : null,
    proposed_target_cents: target,
    incumbent_authority: authority,
    supported_authority: supportedAuthority,
    inside_post_onset_observation_bounds: insideBounds,
    evidence_is_post_onset: postOnset,
    receipt_bound: receiptBound,
    evidence,
  };
}

function firstFailure(license, readLevel) {
  if (!license?.onset?.passed) return "STABILITY_ONSET_NOT_REACHED";
  if (!license?.read?.passed) return "NO_TAPE_MACHINE_READ_ABSENT";
  if (!license?.coherence?.lows_under_par) return "PAIR_POST_ONSET_LOWS_NOT_UNDER_PAR";
  if (!license?.coherence?.disagreement_clear) return "FIRING_DISAGREEMENT_ACTIVE";
  if (!readLevel?.authorized) return "MACHINE_READ_LEVEL_AUTHORITY_NOT_EARNED";
  if (!v52.lawfulCent(readLevel.target_cents)) return "NO_LAWFUL_MACHINE_READ_POST_LEVEL";
  return null;
}

function gateDecision(inputs, incumbent) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.machine_read_level_authority) return v52.gateDecision({ ...inputs, clauses }, incumbent);
  const originalLicense = inputs.birthLicense;
  const readLevel = machineReadLevel(originalLicense, incumbent);
  const license = {
    ...originalLicense,
    onset: originalLicense?.onset ? { ...originalLicense.onset, binding_status: "CODEX-INTERIM", binding_changed_by_V52b: false } : null,
    diary: originalLicense?.diary ? { ...originalLicense.diary, role: "RECORDED_REFERENCE_INPUT_NOT_SOLE_LEVEL_AUTHORITY" } : null,
    level: {
      ...originalLicense?.level,
      target_cents: readLevel.target_cents,
      authority: readLevel.authorized ? "V52B_EVIDENCE_BACKED_MACHINE_READ_LEVEL" : "V52B_MACHINE_READ_LEVEL_ABSTAIN",
      machine_read: readLevel,
      diary_is_sole_authority: false,
    },
  };
  const active = v52.lawfulCent(inputs.activeTarget) ? inputs.activeTarget : null;
  if (active !== null && incumbent?.action === "CANCEL_REST") {
    return { ...incumbent, birth_license: license, judgment_gate: { enabled: true, verdict: "INCUMBENT_LICENSED_REST_GUARD", failure: null, clause_3: "V52B_MACHINE_READ_LEVEL_AUTHORITY" } };
  }
  const failure = firstFailure(license, readLevel);
  if (failure) {
    return {
      action: "HOLD_REST",
      target_cents: active,
      reason: `V52B_BIRTH_BLOCKED_${failure}`,
      placement: incumbent?.placement ?? null,
      guard: active === null ? null : incumbent?.guard ?? null,
      unguarded_decision: incumbent,
      birth_license: license,
      judgment_gate: { enabled: true, verdict: "BLOCKED", failure, clause_3: "V52B_MACHINE_READ_LEVEL_AUTHORITY" },
    };
  }
  const target = readLevel.target_cents;
  const action = active === null ? "PLACE_REST" : active === target ? "HOLD_REST" : "REPRICE_REST";
  return {
    action,
    target_cents: target,
    ...(action === "REPRICE_REST" ? { direction: target > active ? "UP" : "DOWN" } : {}),
    reason: action === "HOLD_REST" ? "V52B_LICENSED_MACHINE_READ_LEVEL_ALREADY_STANDING" : "V52B_LICENSED_MACHINE_READ_LEVEL_POST",
    placement: {
      target_cents: target,
      unbounded_target_cents: readLevel.proposed_target_cents,
      authority: "V52B_EVIDENCE_BACKED_MACHINE_READ_LEVEL",
      incumbent_authority: readLevel.incumbent_authority,
      displayed_bid_consumed_as_unlicensed_anchor: false,
      evidence: readLevel.evidence,
    },
    guard: active === null ? null : incumbent?.guard ?? null,
    unguarded_decision: incumbent,
    birth_license: license,
    judgment_gate: { enabled: true, verdict: action === "HOLD_REST" ? "LICENSED_HOLD" : "POST", failure: null, clause_3: "V52B_MACHINE_READ_LEVEL_AUTHORITY" },
  };
}

function decideReceipt(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const atomic = v52.decideReceipt({ ...inputs, clauses: { ...clauses, machine_read_level_authority: false } });
  return { ...atomic, decision: gateDecision({ ...inputs, clauses }, atomic.decision.unguarded_decision ?? atomic.decision), machine_read_level_authority_enabled: Boolean(clauses.machine_read_level_authority) };
}

function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const incumbent = v52.decide({ ...inputs, clauses: { ...clauses, machine_read_level_authority: false } });
  return gateDecision({ ...inputs, clauses }, incumbent.unguarded_decision ?? incumbent);
}

module.exports = { ...v52, normalizedClauses, machineReadLevel, firstFailure, gateDecision, decideReceipt, decide };
