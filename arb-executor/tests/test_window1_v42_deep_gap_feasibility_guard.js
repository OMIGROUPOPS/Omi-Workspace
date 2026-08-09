#!/usr/bin/env node
"use strict";

const assert = require("assert");
const v41 = require("../analysis/window1_v41_maker_machine.js");
const policy = require("../analysis/window1_v42_deep_gap_feasibility_guard.js");

assert.equal(policy.DEEP_GAP_TOLERANCE_CENTS, 10);
let guard = policy.deepGapFeasibility(64, 93);
assert.equal(guard.implied_sibling_cap_cents, 35);
assert.equal(guard.deep_gap_cents, 58);
assert.equal(guard.withheld, true);
guard = policy.deepGapFeasibility(47, 53);
assert.equal(guard.implied_sibling_cap_cents, 52);
assert.equal(guard.deep_gap_cents, 1);
assert.equal(guard.withheld, false);
guard = policy.deepGapFeasibility(50, 59);
assert.equal(guard.implied_sibling_cap_cents, 49);
assert.equal(guard.deep_gap_cents, 10);
assert.equal(guard.withheld, false);
guard = policy.deepGapFeasibility(50, 60);
assert.equal(guard.deep_gap_cents, 11);
assert.equal(guard.withheld, true);
guard = policy.deepGapFeasibility(50, null);
assert.equal(guard.authority, false);
assert.equal(guard.withheld, false);

const base = { state: "SETTLED", book: { bid: 65, ask: 67 }, activeTarget: null, pairCap: null, persistentJoinLevel: null, wtaInverseFalling: false, pulseFloor: null, causalOwnReachLow: null };
const incumbent = v41.decide(base);
assert.equal(incumbent.action, "PLACE_REST");
assert.equal(incumbent.target_cents, 64);
let out = policy.decide({ ...base, siblingBestAsk: 93 });
assert.equal(out.action, "HOLD_REST");
assert.equal(out.guard.withheld, true);
out = policy.decide({ ...base, siblingBestAsk: 45 });
assert.equal(out.action, incumbent.action);
assert.equal(out.target_cents, incumbent.target_cents);
assert.equal(out.reason, incumbent.reason);
out = policy.decide({ ...base, activeTarget: 10, siblingBestAsk: 93 });
assert.equal(out.action, "HOLD_REST");
assert.equal(out.target_cents, 10);
out = policy.decide({ ...base, activeTarget: 64, siblingBestAsk: 93 });
assert.equal(out.action, "CANCEL_REST");
assert.equal(out.target_cents, null);
assert.equal(policy.combineState, v41.combineState);
assert.equal(policy.placementTarget, v41.placementTarget);
assert.equal(Object.keys(policy).some((name) => /take/i.test(name)), false);

process.stdout.write(`${JSON.stringify({ tests: 26, passed: 26 })}\n`);
