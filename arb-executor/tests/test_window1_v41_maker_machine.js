#!/usr/bin/env node
"use strict";

const assert = require("assert");
const policy = require("../analysis/window1_v41_maker_machine.js");

const book = { bid: 60, ask: 62 };
let out = policy.placementTarget({ state: "RISING", book, activeTarget: null, pairCap: null, persistentJoinLevel: null, wtaInverseFalling: false, pulseFloor: null, causalOwnReachLow: null });
assert.equal(out.target_cents, 59);
assert.equal(out.authority, "V41_RISING_TRACKER_UNTIL_PERSISTENT_JOIN_ARMS");
out = policy.placementTarget({ state: "RISING", book, activeTarget: 59, pairCap: null, persistentJoinLevel: 50, wtaInverseFalling: false, pulseFloor: null, causalOwnReachLow: null });
assert.equal(out.target_cents, 50);
assert.equal(out.authority, "V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1");
out = policy.placementTarget({ state: "FALLING", book: { bid: 55, ask: 56 }, activeTarget: 50, pairCap: null, persistentJoinLevel: null, wtaInverseFalling: false, pulseFloor: null, causalOwnReachLow: null });
assert.equal(out.target_cents, 50);
out = policy.placementTarget({ state: "SETTLED", book, activeTarget: 40, pairCap: null, persistentJoinLevel: null, wtaInverseFalling: false, pulseFloor: null, causalOwnReachLow: null });
assert.equal(out.target_cents, 59);
out = policy.placementTarget({ state: "RISING", book, activeTarget: 59, pairCap: null, persistentJoinLevel: null, wtaInverseFalling: true, pulseFloor: 55, causalOwnReachLow: 52 });
assert.equal(out.target_cents, 52);
assert.equal(out.authority, "V41_WTA_OTHER_EXPRESSION_FALLING_HOLD");
out = policy.placementTarget({ state: "RISING", book: { bid: 60, ask: 50 }, activeTarget: 49, pairCap: null, persistentJoinLevel: 55, wtaInverseFalling: false, pulseFloor: null, causalOwnReachLow: null });
assert.equal(out.target_cents, 49);
assert.equal(out.sanity_bound_applied, true);
out = policy.placementTarget({ state: "RISING", book, activeTarget: 59, pairCap: 47, persistentJoinLevel: 50, wtaInverseFalling: false, pulseFloor: null, causalOwnReachLow: null });
assert.equal(out.target_cents, 47);
assert.equal(policy.decide({ state: "RISING", book, activeTarget: null, pairCap: null, persistentJoinLevel: null, wtaInverseFalling: false, pulseFloor: null, causalOwnReachLow: null }).action, "PLACE_REST");
assert.equal(policy.decide({ state: "RISING", book, activeTarget: 59, pairCap: null, persistentJoinLevel: 50, wtaInverseFalling: false, pulseFloor: null, causalOwnReachLow: null }).action, "REPRICE_REST");
assert.equal(policy.decide({ state: "RISING", book, activeTarget: 50, pairCap: null, persistentJoinLevel: 50, wtaInverseFalling: false, pulseFloor: null, causalOwnReachLow: null }).action, "HOLD_REST");
assert.equal(policy.strictPrintCross({ target_cents: 50, action_ts: 10 }, { ts: 11, taker_side: "no", size: 5, price: 50 }), true);
assert.equal(policy.strictPrintCross({ target_cents: 50, action_ts: 10 }, { ts: 11, taker_side: "yes", size: 5, price: 50 }), false);
assert.equal(policy.tradedAtLevel({ target_cents: 50, action_ts: 10 }, { ts: 11, size: 1, price: 50 }), true);
assert.equal(policy.quoteTouch({ target_cents: 50, action_ts: 10 }, { ts: 21, bid: 49, ask: 50, spread: 1, ask_dwell_seconds: 10, top_ask_size: 5 }), true);
assert.deepStrictEqual(policy.persistenceJoinUpdate({ state: "RISING", bid: 4, residencySeconds: 299, currentJoinLevel: null }), { armed: false, changed: false, level_cents: null });
assert.deepStrictEqual(policy.persistenceJoinUpdate({ state: "FALLING", bid: 50, residencySeconds: 300, currentJoinLevel: 4 }), { armed: false, changed: false, level_cents: 4 });
assert.deepStrictEqual(policy.persistenceJoinUpdate({ state: "RISING", bid: 50, residencySeconds: 300, currentJoinLevel: 4 }), { armed: true, changed: true, level_cents: 50 });
assert.deepStrictEqual(policy.persistenceJoinUpdate({ state: "RISING", bid: 50, residencySeconds: 301, currentJoinLevel: 50 }), { armed: true, changed: false, level_cents: 50 });
assert.equal(Object.keys(policy).some((name) => /take/i.test(name)), false);

process.stdout.write(`${JSON.stringify({ tests: 24, passed: 24 })}\n`);
