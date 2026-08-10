#!/usr/bin/env node
"use strict";

const assert = require("assert");
const v45 = require("../analysis/window1_v45_guard_release_sibling_credit.js");
const policy = require("../analysis/window1_v46_pair_gated_gap_credit.js");

const clauses = { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, pair_gated_gap_credit: true };
const base = { state: "FALLING", book: { bid: 42, ask: 46 }, priorAsk: 50, askGapCents: 4, activeTarget: 54, pairCap: 52, persistentJoinLevel: null, wtaInverseFalling: false, pulseFloor: null, causalOwnReachLow: 45, siblingBestAsk: 47, siblingEntryCents: 47, siblingCredited: false };

assert.equal(policy.ASK_GAP_CREDIT_MIN_CENTS, 3);
assert.deepEqual(policy.normalizedClauses({}), { arm_at_first_evidence: false, deep_gap_guard: false, loosen_one_cent: false, release_guard_on_sibling_credit: false, pair_gated_gap_credit: false });

let out = policy.decide({ ...base, clauses });
assert.equal(out.gap_credit.eligible, true);
assert.equal(out.gap_credit.authorized, false);
assert.equal(out.gap_credit.reason, "V46_GAP_CREDIT_REFUSED_SIBLING_NOT_CREDITED");
assert.deepEqual({ ...out, gap_credit: undefined }, { ...v45.decide({ ...base, clauses }), gap_credit: undefined });

out = policy.decide({ ...base, siblingCredited: true, clauses });
assert.equal(out.action, "REPRICE_REST");
assert.equal(out.target_cents, 45);
assert.equal(out.direction, "DOWN");
assert.equal(out.gap_credit.authorized, true);
assert.equal(out.gap_credit.ask_gap_cents, 4);
assert.equal(out.gap_credit.sibling_entry_cents, 47);
assert(out.target_cents < base.book.ask);

out = policy.decide({ ...base, siblingCredited: true, pairCap: 43, clauses });
assert.equal(out.target_cents, 43);
assert.equal(out.gap_credit.pair_cap_cents, 43);

out = policy.decide({ ...base, askGapCents: 2, siblingCredited: true, clauses });
assert.equal(out.gap_credit, undefined);
assert.deepEqual(out, v45.decide({ ...base, askGapCents: 2, siblingCredited: true, clauses }));

out = policy.decide({ ...base, state: "RISING", siblingCredited: true, clauses });
assert.equal(out.gap_credit, undefined);

out = policy.decide({ ...base, activeTarget: 44, siblingCredited: true, clauses });
assert.equal(out.gap_credit.authorized, false);
assert.equal(out.gap_credit.reason, "V46_GAP_CREDIT_NO_LAWFUL_REPRICE_DOWN");

out = policy.decide({ ...base, siblingCredited: true, clauses: { ...clauses, pair_gated_gap_credit: false } });
assert.deepEqual(out, v45.decide({ ...base, siblingCredited: true, clauses: { ...clauses, pair_gated_gap_credit: false } }));
assert.equal(Object.keys(policy).some((name) => /take/i.test(name)), false);

process.stdout.write(`${JSON.stringify({ tests: 26, passed: 26 })}\n`);
