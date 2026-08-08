#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const v36 = require("../analysis/window1_v36_state_directional_rest_mature_floor.js");
const policy = require("../analysis/window1_v40_incumbent_direction_placement_stack.js");

const cases = [];
function test(name, fn) { fn(); cases.push(name); }

test("incumbent state combiner is inherited byte-for-function", () => {
  assert.strictEqual(policy.combineState, v36.combineState);
});

test("V39 classifier is structurally severed", () => {
  const source = fs.readFileSync(path.join(__dirname, "../analysis/window1_v40_incumbent_direction_placement_stack.js"), "utf8");
  assert.doesNotMatch(source, /window1_v39|agreementWeightedDirection|NO_HINDSIGHT/);
});

test("incumbent RISING state authorizes persistent join", () => {
  const row = policy.placementTarget({ state: "RISING", book: { bid: 50, ask: 56 }, activeTarget: 49, persistentJoinLevel: 50 });
  assert.equal(row.target_cents, 50);
  assert.match(row.authority, /INCUMBENT_RISING_PERSISTENT_LEVEL_JOIN/);
});

test("incumbent FALLING does not consume persistent join", () => {
  const row = policy.placementTarget({ state: "FALLING", book: { bid: 50, ask: 56 }, activeTarget: 49, persistentJoinLevel: 50 });
  assert.doesNotMatch(row.authority, /PERSISTENT_LEVEL_JOIN/);
});

test("WTA inverse falling holds deeper", () => {
  const row = policy.placementTarget({ state: "RISING", book: { bid: 60, ask: 64 }, activeTarget: 59, wtaInverseFalling: true, pulseFloor: 58, causalOwnReachLow: 55 });
  assert.equal(row.target_cents, 55);
});

test("sanity bound enforces rest below ask", () => {
  const row = policy.placementTarget({ state: "RISING", book: { bid: 56, ask: 56 }, activeTarget: 55, persistentJoinLevel: 56 });
  assert.equal(row.target_cents, 55);
  assert.equal(row.sanity_bound_applied, true);
});

test("V36 take behavior remains callable", () => {
  const row = policy.decide({ state: "SETTLED", book: { bid: 55, ask: 56, spread: 1, ask_dwell_seconds: 20, top_ask_size: 5 }, activeTarget: 54, activeEvidenceFloor: 56, floorMature: true });
  assert.equal(row.action, "TAKE");
  assert.equal(row.reason, "MATURE_EVIDENCE_FLOOR_TAKE");
});

process.stdout.write(`${JSON.stringify({ tests: cases.length, passed: cases.length, names: cases }, null, 2)}\n`);

