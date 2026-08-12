"use strict";

// V51 is one mechanism-bound time discipline over frozen V49b.  On a
// hash-bound doctrine leg, an exact-P rest which is already standing survives
// the two incumbent vacate paths (post-only walk-away and pre-credit S12/deep-
// gap withhold) only while the receipt carries the elevated-flow authority
// bound by AIM_ERROR_CENSUS @ 17664b3f.  It does not move the price, create a
// rest, waive pair-cap legality, or change crediting.

const v49b = require("./window1_v49b_faithful_stand_at_p.js");

const ELEVATED_FLOW_THRESHOLD_LOTS = 10000;
const ELEVATED_FLOW_PROVENANCE = "AIM_ERROR_CENSUS_17664B3F_VOLUME_TIER_GT_10K";

function normalizedClauses(value = {}) {
  return {
    ...v49b.normalizedClauses(value),
    continuity_of_standing: Boolean(value.continuity_of_standing),
  };
}

function elevatedFlow(inputs) {
  const lots = Number(inputs.cumulativeVolumeLots);
  return {
    qualified: Number.isFinite(lots) && lots > ELEVATED_FLOW_THRESHOLD_LOTS,
    cumulative_volume_lots: Number.isFinite(lots) ? lots : null,
    tier: !Number.isFinite(lots) || lots < 1 ? "NONE" : lots < 100 ? "1-99" : lots < 1000 ? "100-999" : lots <= 10000 ? "1k-10k" : ">10k",
    strict_threshold_lots: ELEVATED_FLOW_THRESHOLD_LOTS,
    provenance: ELEVATED_FLOW_PROVENANCE,
  };
}

function decideReceipt(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const incumbent = v49b.decideReceipt({ ...inputs, clauses });
  const decision = incumbent.decision;
  const doctrine = inputs.continuityDoctrine ?? inputs.doctrineStanding;
  const p = doctrine?.level_cents;
  const activeAtP = v49b.lawfulCent(p) && inputs.activeTarget === p;
  const flow = elevatedFlow(inputs);
  const pairCapLawful = !v49b.lawfulCent(inputs.pairCap) || p <= inputs.pairCap;
  const vacates = decision.target_cents !== p || ["CANCEL_REST", "REPRICE_REST"].includes(decision.action);

  if (!clauses.continuity_of_standing || !doctrine?.authorized || !activeAtP || !flow.qualified || !pairCapLawful || !vacates) {
    return {
      ...incumbent,
      continuity_of_standing: {
        enabled: clauses.continuity_of_standing,
        applied: false,
        flow,
        active_at_doctrine_P: activeAtP,
        pair_cap_lawful: pairCapLawful,
        incumbent_action: decision.action,
        incumbent_reason: decision.reason,
      },
    };
  }

  const reason = decision.guard?.withheld
    ? "V51_CONTINUITY_OVERRIDE_S12_WITHHOLD_ELEVATED_FLOW"
    : "V51_CONTINUITY_OVERRIDE_WALK_AWAY_ELEVATED_FLOW";
  const held = {
    action: "HOLD_REST",
    target_cents: p,
    reason,
    placement: {
      target_cents: p,
      unbounded_target_cents: p,
      authority: "V51_CONTINUITY_OF_STANDING",
      doctrine_level_cents: p,
      doctrine_mechanism_code: "AT_P_CONTINUITY_HOLD",
      causal_evidence: doctrine.causal_evidence,
    },
    guard: decision.guard ?? null,
    unguarded_decision: decision.unguarded_decision ?? decision,
    doctrine_standing: { enabled: true, authorized: true, mechanism_code: "AT_P_CONTINUITY_HOLD", doctrine },
    continuity_of_standing: {
      enabled: true,
      applied: true,
      time_discipline_only: true,
      price_changed: false,
      held_level_cents: p,
      flow,
      incumbent_action: decision.action,
      incumbent_reason: decision.reason,
      pair_cap_lawful: true,
    },
  };
  return { ...incumbent, decision: held, continuity_of_standing: held.continuity_of_standing };
}

function decide(inputs) {
  return decideReceipt({ ...inputs, currentJoinLevel: inputs.persistentJoinLevel, residencySeconds: inputs.residencySeconds ?? 0 }).decision;
}

module.exports = {
  ...v49b,
  ELEVATED_FLOW_THRESHOLD_LOTS,
  ELEVATED_FLOW_PROVENANCE,
  normalizedClauses,
  elevatedFlow,
  decideReceipt,
  decide,
};
