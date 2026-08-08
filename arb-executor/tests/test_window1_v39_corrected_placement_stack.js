#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const policy = require("../analysis/window1_v39_corrected_placement_stack.js");

const cases = [];
function test(name, fn) { fn(); cases.push(name); }

test("agreement resolves direction without ex-post input", () => {
  assert.equal(policy.agreementWeightedDirection({ state: "RISING" }, "RISING").state, "RISING");
  assert.equal(policy.agreementWeightedDirection({ state: "FALLING" }, "FALLING").state, "FALLING");
});

test("opposed causal reads settle rather than choosing a hindsight label", () => {
  const row = policy.agreementWeightedDirection({ state: "FALLING" }, "RISING");
  assert.equal(row.state, "SETTLED");
  assert.equal(row.disagreement, true);
  assert.match(row.authority, /NO_HINDSIGHT/);
});

test("persistent riser joins at the proven level", () => {
  const row = policy.placementTarget({ state: "RISING", book: { bid: 50, ask: 56 }, activeTarget: 49, persistentJoinLevel: 50 });
  assert.equal(row.target_cents, 50);
  assert.match(row.authority, /PERSISTENT_LEVEL_JOIN/);
});

test("WTA inverse falling uses the deeper causal floor", () => {
  const row = policy.placementTarget({ state: "RISING", book: { bid: 60, ask: 64 }, activeTarget: 59, wtaInverseFalling: true, pulseFloor: 58, causalOwnReachLow: 55 });
  assert.equal(row.target_cents, 55);
});

test("universal sanity bound stays strictly below ask", () => {
  const row = policy.placementTarget({ state: "RISING", book: { bid: 56, ask: 56 }, activeTarget: 55, persistentJoinLevel: 56 });
  assert.equal(row.target_cents, 55);
  assert.equal(row.sanity_bound_applied, true);
});

test("V36 mature-floor take remains callable", () => {
  const row = policy.decide({ state: "SETTLED", book: { bid: 55, ask: 56, spread: 1, ask_dwell_seconds: 20, top_ask_size: 5 }, activeTarget: 54, activeEvidenceFloor: 56, floorMature: true });
  assert.equal(row.action, "TAKE");
  assert.equal(row.target_cents, 56);
});

test("pair cap and sanity compose", () => {
  const row = policy.placementTarget({ state: "RISING", book: { bid: 70, ask: 71 }, persistentJoinLevel: 70, pairCap: 49 });
  assert.equal(row.target_cents, 49);
});

test("persistent seller-hit binding uses the contemporaneous book receipt", () => {
  const source = fs.readFileSync(path.join(__dirname, "../analysis/build_window1_v38_maker_only.js"), "utf8");
  assert.match(source, /row\.last_trade === row\.bid/);
  assert.match(source, /current_bid_last_trade_hit/);
});

test("sealed ex-post direction is absent from the receipt decision loop", () => {
  const source = fs.readFileSync(path.join(__dirname, "../analysis/build_window1_v38_maker_only.js"), "utf8");
  const simulation = source.slice(source.indexOf("function simulate"), source.indexOf("function score"));
  assert.doesNotMatch(simulation, /leg_direction/);
});

process.stdout.write(`${JSON.stringify({ tests: cases.length, passed: cases.length, names: cases }, null, 2)}\n`);
