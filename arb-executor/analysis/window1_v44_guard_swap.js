"use strict";

// V44 keeps V43's arm-at-first-evidence and +1c loosen clauses, removes the
// composition-stale T=10 guard, and adds a causal fill-time dry-sibling
// withhold.  The builder supplies explicit clause sets for the four-row
// attribution table.

const v43 = require("./window1_v43_composed_machine.js");

const DRY_SIBLING_NEAR_CENTS = 3;

function normalizedClauses(value = {}) {
  return {
    arm_at_first_evidence: value.arm_at_first_evidence !== false,
    deep_gap_guard: Boolean(value.deep_gap_guard),
    loosen_one_cent: value.loosen_one_cent !== false,
    dry_sibling_withhold: Boolean(value.dry_sibling_withhold),
  };
}

function drySiblingEvidence({ lawfulLevels = [], flowLevels = [] } = {}) {
  const lawful = [...new Set(lawfulLevels.filter(v43.lawfulCent))].sort((a, b) => a - b);
  const flow = [...new Set(flowLevels.filter(v43.lawfulCent))].sort((a, b) => a - b);
  let nearest_gap_cents = null;
  let nearest_lawful_level_cents = null;
  let nearest_flow_level_cents = null;
  for (const lawfulLevel of lawful) {
    for (const flowLevel of flow) {
      const gap = Math.abs(lawfulLevel - flowLevel);
      if (nearest_gap_cents === null || gap < nearest_gap_cents || (gap === nearest_gap_cents && (lawfulLevel < nearest_lawful_level_cents || (lawfulLevel === nearest_lawful_level_cents && flowLevel < nearest_flow_level_cents)))) {
        nearest_gap_cents = gap;
        nearest_lawful_level_cents = lawfulLevel;
        nearest_flow_level_cents = flowLevel;
      }
    }
  }
  const within = Number.isInteger(nearest_gap_cents) && nearest_gap_cents <= DRY_SIBLING_NEAR_CENTS;
  return {
    withheld: !within,
    reason: lawful.length === 0 ? "NO_LAWFUL_SIBLING_LEVEL_OBSERVED" : flow.length === 0 ? "NO_SIBLING_UNION_FLOW_OBSERVED" : within ? "SIBLING_FLOW_WITHIN_THREE_CENTS_OF_LAWFUL_LEVEL" : "SIBLING_FLOW_NEVER_WITHIN_THREE_CENTS_OF_LAWFUL_LEVEL",
    threshold_cents: DRY_SIBLING_NEAR_CENTS,
    lawful_level_count: lawful.length,
    flow_level_count: flow.length,
    nearest_gap_cents,
    nearest_lawful_level_cents,
    nearest_flow_level_cents,
  };
}

function persistenceJoinUpdate(inputs) {
  return v43.persistenceJoinUpdate({ ...inputs, clauses: normalizedClauses(inputs.clauses) });
}

function placementTarget(inputs) {
  return v43.placementTarget({ ...inputs, clauses: normalizedClauses(inputs.clauses) });
}

function decide(inputs) {
  return v43.decide({ ...inputs, clauses: normalizedClauses(inputs.clauses) });
}

module.exports = {
  ...v43,
  DRY_SIBLING_NEAR_CENTS,
  normalizedClauses,
  drySiblingEvidence,
  persistenceJoinUpdate,
  placementTarget,
  decide,
};
