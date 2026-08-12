"use strict";

const assert = require("assert");
const policy = require("../analysis/window1_v51_continuity_of_standing.js");

const doctrine = { authorized: true, level_cents: 50, causal_evidence: [{ source: "SYNTHETIC_TEST" }] };
const clauses = { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true, continuity_of_standing: true };
const base = { state: "SETTLED", book: { kind: "BOOK", bid: 48, ask: 49, ts: 2, receipt: "book-2" }, priorAsk: 51, activeTarget: 50, pairCap: 99, pulseFloor: null, persistentJoinLevel: null, wtaInverseFalling: false, causalOwnReachLow: null, activeEvidenceFloor: null, floorFirstFlickerLive: false, floorMature: false, recentTradeLow: null, priorTrueTradeLow: null, priorExactBidEvidence: null, evidencedStandingLevel: null, evidencedStandingAuthority: null, doctrineStanding: doctrine, continuityDoctrine: doctrine, siblingBestAsk: 60, siblingEntryCents: null, siblingCredited: false, clauses };

{
  const result = policy.decideReceipt({ ...base, cumulativeVolumeLots: 10000 });
  assert.strictEqual(result.continuity_of_standing.applied, false);
  assert.strictEqual(result.decision.action, "CANCEL_REST");
}

{
  const result = policy.decideReceipt({ ...base, cumulativeVolumeLots: 10001 });
  assert.strictEqual(result.continuity_of_standing.applied, true);
  assert.strictEqual(result.decision.action, "HOLD_REST");
  assert.strictEqual(result.decision.target_cents, 50);
  assert.strictEqual(result.decision.continuity_of_standing.price_changed, false);
}

{
  const result = policy.decideReceipt({ ...base, book: { kind: "BOOK", bid: 49, ask: 51, ts: 2, receipt: "s12" }, siblingBestAsk: 95, cumulativeVolumeLots: 10001 });
  assert.strictEqual(result.continuity_of_standing.applied, true);
  assert.strictEqual(result.decision.reason, "V51_CONTINUITY_OVERRIDE_S12_WITHHOLD_ELEVATED_FLOW");
  assert.strictEqual(result.decision.target_cents, 50);
}

{
  const result = policy.decideReceipt({ ...base, pairCap: 49, cumulativeVolumeLots: 10001 });
  assert.strictEqual(result.continuity_of_standing.applied, false);
  assert.strictEqual(result.continuity_of_standing.pair_cap_lawful, false);
}

{
  const result = policy.decideReceipt({ ...base, activeTarget: null, cumulativeVolumeLots: 10001 });
  assert.strictEqual(result.continuity_of_standing.applied, false);
  assert.strictEqual(result.continuity_of_standing.active_at_doctrine_P, false);
}

{
  const result = policy.decideReceipt({ ...base, clauses: { ...clauses, continuity_of_standing: false }, cumulativeVolumeLots: 10001 });
  assert.strictEqual(result.continuity_of_standing.applied, false);
}

{
  assert.strictEqual(policy.tradeTruthCredit({ target_cents: 50, action_ts: 10 }, { kind: "PRINT", ts: 11, receipt: "p", trade_id: "t", price: 50 }), true);
  assert.strictEqual(policy.tradeTruthCredit({ target_cents: 50, action_ts: 10 }, { kind: "PRINT", ts: 10, receipt: "p", trade_id: "t", price: 49 }), false);
}

console.log(JSON.stringify({ status: "PASS", tests: 7, threshold: { operator: ">", lots: policy.ELEVATED_FLOW_THRESHOLD_LOTS }, provenance: policy.ELEVATED_FLOW_PROVENANCE }));
