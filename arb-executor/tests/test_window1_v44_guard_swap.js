#!/usr/bin/env node
"use strict";

const assert = require("assert");
const v43 = require("../analysis/window1_v43_composed_machine.js");
const policy = require("../analysis/window1_v44_guard_swap.js");

assert.deepEqual(policy.normalizedClauses({ dry_sibling_withhold: true }), { arm_at_first_evidence: true, deep_gap_guard: false, loosen_one_cent: true, dry_sibling_withhold: true });
assert.deepEqual(policy.normalizedClauses({ deep_gap_guard: true }), { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, dry_sibling_withhold: false });

let evidence = policy.drySiblingEvidence({ lawfulLevels: [64], flowLevels: [] });
assert.equal(evidence.withheld, true);
assert.equal(evidence.reason, "NO_SIBLING_UNION_FLOW_OBSERVED");
evidence = policy.drySiblingEvidence({ lawfulLevels: [64], flowLevels: [60] });
assert.equal(evidence.withheld, true);
assert.equal(evidence.nearest_gap_cents, 4);
evidence = policy.drySiblingEvidence({ lawfulLevels: [64, 63], flowLevels: [60] });
assert.equal(evidence.withheld, false);
assert.equal(evidence.nearest_gap_cents, 3);
assert.equal(evidence.nearest_lawful_level_cents, 63);
evidence = policy.drySiblingEvidence({ lawfulLevels: [], flowLevels: [60] });
assert.equal(evidence.withheld, true);
assert.equal(evidence.reason, "NO_LAWFUL_SIBLING_LEVEL_OBSERVED");

const base = { state: "SETTLED", book: { bid: 65, ask: 67 }, activeTarget: null, pairCap: null, persistentJoinLevel: null, wtaInverseFalling: false, pulseFloor: null, causalOwnReachLow: null, siblingBestAsk: 93 };
let out = policy.decide({ ...base, clauses: { dry_sibling_withhold: true } });
assert.equal(out.action, "PLACE_REST");
assert.equal(out.target_cents, 65);
assert.equal(out.guard, null);
out = policy.decide({ ...base, clauses: { deep_gap_guard: true } });
assert.equal(out.action, "HOLD_REST");
assert.equal(out.guard.withheld, true);
assert.equal(policy.persistenceJoinUpdate({ state: "RISING", bid: 50, residencySeconds: 0, currentJoinLevel: null, clauses: { dry_sibling_withhold: true } }).armed, true);
assert.equal(policy.combineState, v43.combineState);
assert.equal(policy.DRY_SIBLING_NEAR_CENTS, 3);
assert.equal(Object.keys(policy).some((name) => /take/i.test(name)), false);

process.stdout.write(`${JSON.stringify({ tests: 24, passed: 24 })}\n`);
