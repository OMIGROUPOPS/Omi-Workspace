#!/usr/bin/env node
"use strict";

const assert = require("assert");
const v43 = require("../analysis/window1_v43_composed_machine.js");
const policy = require("../analysis/window1_v45_guard_release_sibling_credit.js");

const clauses = { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true };
const base = { state: "SETTLED", book: { bid: 65, ask: 67 }, activeTarget: null, pairCap: null, persistentJoinLevel: null, wtaInverseFalling: false, pulseFloor: null, causalOwnReachLow: null, siblingBestAsk: 93, siblingCredited: false };

assert.deepEqual(policy.normalizedClauses({}), { arm_at_first_evidence: false, deep_gap_guard: false, loosen_one_cent: false, release_guard_on_sibling_credit: false });
assert.deepEqual(policy.normalizedClauses(clauses), clauses);

let out = policy.decide({ ...base, clauses });
assert.equal(out.guard.withheld, true);
assert.equal(out.action, "HOLD_REST");
assert.notEqual(out.guard_authority_terminated, true);

out = policy.decide({ ...base, siblingCredited: true, pairCap: 56, clauses });
assert.equal(out.guard, null);
assert.equal(out.guard_authority_terminated, true);
assert.equal(out.guard_authority, "TERMINATED_AT_SIBLING_CREDIT");
assert.equal(out.action, "PLACE_REST");
assert.equal(out.target_cents, 56);
assert.equal(out.placement.sanity_bound_applied, true);

out = policy.decide({ ...base, siblingCredited: true, pairCap: 56, clauses: { ...clauses, release_guard_on_sibling_credit: false } });
assert.equal(out.guard.withheld, true);
assert.equal(out.action, "HOLD_REST");

const v43Input = { ...base, siblingCredited: true, clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true } };
assert.deepEqual(policy.decide(v43Input), v43.decide(v43Input));
assert.equal(policy.combineState, v43.combineState);
assert.equal(policy.DEEP_GAP_TOLERANCE_CENTS, 10);
assert.equal(Object.keys(policy).some((name) => /take/i.test(name)), false);

process.stdout.write(`${JSON.stringify({ tests: 20, passed: 20 })}\n`);
