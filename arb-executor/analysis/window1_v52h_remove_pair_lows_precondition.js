"use strict";

// V52h removes exactly the market-proof portion of clause 4.  The frozen
// V52g stack still computes and records post-onset traded lows, but their
// sum no longer gates birth.  The disagreement referee remains operative;
// clauses 1/2/3/5/6, N9, crediting, and scavenger remain frozen.

const v52g = require("./window1_v52g_joint_target_conservation.js");

function normalizedClauses(value = {}) {
  const clauses = v52g.normalizedClauses(value);
  return value.remove_pair_lows_precondition
    ? { ...clauses, joint_target_conservation: true, pair_entry_conservation: true, remove_pair_lows_precondition: true }
    : clauses;
}

function marketProofReceipt(coherence) {
  return {
    clause: "CLAUSE_4_MARKET_PROOF_PRECONDITION_REMOVAL",
    removed_from_licensing: true,
    recorded_as_telemetry: true,
    original_lows_under_par: coherence?.lows_under_par ?? null,
    original_lows_sum_cents: coherence?.lows_sum_cents ?? null,
    disagreement_referee_untouched: true,
    disagreement_firing: coherence?.disagreement_firing ?? null,
    disagreement_clear: coherence?.disagreement_clear ?? null,
  };
}

function restoreLicense(license, originalCoherence) {
  if (!license) return license;
  return {
    ...license,
    coherence: originalCoherence ? { ...originalCoherence } : originalCoherence,
    clause_4_market_proof_precondition: marketProofReceipt(originalCoherence),
  };
}

function restoreDecision(decision, originalCoherence) {
  if (!decision || typeof decision !== "object") return decision;
  return {
    ...decision,
    birth_license: restoreLicense(decision.birth_license, originalCoherence),
    clause_4_market_proof_precondition: marketProofReceipt(originalCoherence),
  };
}

function gateDecision(inputs, incumbent) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.remove_pair_lows_precondition) return v52g.gateDecision({ ...inputs, clauses }, incumbent);
  const originalCoherence = inputs.birthLicense?.coherence ?? null;
  const licensingCoherence = originalCoherence ? { ...originalCoherence, lows_under_par: true } : originalCoherence;
  const decision = v52g.gateDecision({
    ...inputs,
    clauses: { ...clauses, remove_pair_lows_precondition: false },
    birthLicense: inputs.birthLicense ? { ...inputs.birthLicense, coherence: licensingCoherence } : inputs.birthLicense,
  }, incumbent);
  return restoreDecision(decision, originalCoherence);
}

function decideReceipt(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const atomic = v52g.decideReceipt({ ...inputs, clauses: { ...clauses, remove_pair_lows_precondition: false } });
  return {
    ...atomic,
    decision: gateDecision({ ...inputs, clauses }, atomic.decision.unguarded_decision ?? atomic.decision),
    remove_pair_lows_precondition_enabled: Boolean(clauses.remove_pair_lows_precondition),
  };
}

function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const incumbent = v52g.decide({ ...inputs, clauses: { ...clauses, remove_pair_lows_precondition: false } });
  return gateDecision({ ...inputs, clauses }, incumbent.unguarded_decision ?? incumbent);
}

module.exports = { ...v52g, normalizedClauses, marketProofReceipt, restoreLicense, gateDecision, decideReceipt, decide };
