#!/usr/bin/env node
"use strict";

const assert = require("assert");
const v41 = require("../analysis/window1_v41_maker_machine.js");
const policy = require("../analysis/window1_v43_composed_machine.js");

const base = { state: "SETTLED", book: { bid: 65, ask: 67 }, activeTarget: null, pairCap: null, persistentJoinLevel: null, wtaInverseFalling: false, pulseFloor: null, causalOwnReachLow: null, siblingBestAsk: null };
assert.deepEqual(policy.normalizedClauses({}), { arm_at_first_evidence: false, deep_gap_guard: false, loosen_one_cent: false });
assert.deepEqual(policy.decide({ ...base, clauses: {} }), { ...v41.decide(base), guard: null, unguarded_decision: v41.decide(base) });

let join = v41.persistenceJoinUpdate({ state: "RISING", bid: 50, residencySeconds: 0, currentJoinLevel: null });
assert.equal(join.armed, false);
join = policy.persistenceJoinUpdate({ state: "RISING", bid: 50, residencySeconds: 0, currentJoinLevel: null, clauses: { arm_at_first_evidence: true } });
assert.equal(join.armed, true);
assert.equal(join.level_cents, 50);
assert.equal(join.authority, "V43_C1_FIRST_OBSERVATION_T5_ARM");
join = policy.persistenceJoinUpdate({ state: "FALLING", bid: 50, residencySeconds: 0, currentJoinLevel: null, clauses: { arm_at_first_evidence: true } });
assert.equal(join.armed, false);

let out = policy.decide({ ...base, clauses: { loosen_one_cent: true } });
assert.equal(v41.decide(base).target_cents, 64);
assert.equal(out.target_cents, 65);
assert.equal(out.placement.authority, "V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY");
out = policy.decide({ ...base, book: { bid: 65, ask: 65 }, clauses: { loosen_one_cent: true } });
assert.equal(out.target_cents, 64);
out = policy.decide({ ...base, pairCap: 62, clauses: { loosen_one_cent: true } });
assert.equal(out.target_cents, 62);

const joined = { ...base, state: "RISING", persistentJoinLevel: 50, book: { bid: 65, ask: 67 }, clauses: { loosen_one_cent: true } };
out = policy.decide(joined);
assert.equal(out.target_cents, 50);
assert.equal(out.placement.authority, "V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1");

out = policy.decide({ ...base, siblingBestAsk: 93, clauses: { deep_gap_guard: true } });
assert.equal(out.action, "HOLD_REST");
assert.equal(out.guard.withheld, true);
assert.equal(out.guard.implied_sibling_cap_cents, 35);
out = policy.decide({ ...base, siblingBestAsk: 45, clauses: { deep_gap_guard: true } });
assert.equal(out.action, "PLACE_REST");
assert.equal(out.target_cents, 64);
out = policy.decide({ ...base, siblingBestAsk: 93, clauses: { deep_gap_guard: true, loosen_one_cent: true } });
assert.equal(out.guard.target_cents, 65);
assert.equal(out.guard.implied_sibling_cap_cents, 34);
assert.equal(out.action, "HOLD_REST");

for (let mask = 0; mask < 8; mask += 1) {
  const clauses = { arm_at_first_evidence: Boolean(mask & 1), deep_gap_guard: Boolean(mask & 2), loosen_one_cent: Boolean(mask & 4) };
  const normalized = policy.normalizedClauses(clauses);
  assert.deepEqual(normalized, clauses);
  const decision = policy.decide({ ...base, siblingBestAsk: 45, clauses });
  assert(["PLACE_REST", "REPRICE_REST", "HOLD_REST", "CANCEL_REST"].includes(decision.action));
}

assert.equal(policy.DEEP_GAP_TOLERANCE_CENTS, 10);
assert.equal(policy.combineState, v41.combineState);
assert.equal(Object.keys(policy).some((name) => /take/i.test(name)), false);
process.stdout.write(`${JSON.stringify({ tests: 40, passed: 40 })}\n`);
