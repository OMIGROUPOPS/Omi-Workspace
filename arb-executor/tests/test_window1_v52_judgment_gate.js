#!/usr/bin/env node
"use strict";

const assert = require("assert");
const gate = require("../analysis/window1_v52_judgment_gate.js");
const onset = require("../analysis/window1_v52_stability_onset.js");

function license(overrides = {}) {
  return {
    onset: { passed: true, selected_candidate: "A_SPREAD_COLLAPSE_PLUS_CROSS_LEG_MIDSUM_SETTLE" },
    read: { passed: true, state: "SETTLED", receipt: "book#9" },
    diary: { passed: true, own_post_onset_true_trade_low_cents: 37, sibling_post_onset_true_trade_low_cents: 55, displayed_bid_consumed: false },
    coherence: { lows_under_par: true, disagreement_clear: true, sibling_credited: false },
    level: { target_cents: 37, authority: "POST_ONSET_RUNNING_TRUE_TRADE_LOW_DIARY", displayed_bid_consumed: false },
    scavenger: { enabled: false },
    ...overrides,
  };
}

const incumbent = { action: "PLACE_REST", target_cents: 81, reason: "INCUMBENT_DISPLAYED_BID_PATH" };
const placed = gate.gateDecision({ clauses: { judgment_gate: true }, activeTarget: null, birthLicense: license() }, incumbent);
assert.equal(placed.action, "PLACE_REST");
assert.equal(placed.target_cents, 37);
assert.equal(placed.placement.authority, "V52_POST_ONSET_TRUE_TRADE_LOW_DIARY");
assert.equal(placed.placement.displayed_bid_consumed, false);

for (const [field, value, reason] of [
  ["onset", { passed: false }, "STABILITY_ONSET_NOT_REACHED"],
  ["read", { passed: false }, "NO_TAPE_MACHINE_READ_ABSENT"],
  ["diary", { passed: false }, "POST_ONSET_TRUE_TRADE_LOW_ABSENT"],
  ["coherence", { lows_under_par: false, disagreement_clear: true }, "PAIR_POST_ONSET_LOWS_NOT_UNDER_PAR"],
  ["coherence", { lows_under_par: true, disagreement_clear: false }, "FIRING_DISAGREEMENT_ACTIVE"],
]) {
  const blocked = gate.gateDecision({ clauses: { judgment_gate: true }, activeTarget: null, birthLicense: license({ [field]: value }) }, incumbent);
  assert.equal(blocked.action, "HOLD_REST");
  assert.equal(blocked.target_cents, null);
  assert.equal(blocked.judgment_gate.failure, reason);
}

const siblingCleared = gate.gateDecision({ clauses: { judgment_gate: true }, activeTarget: null, birthLicense: license({ coherence: { lows_under_par: true, disagreement_clear: true, sibling_credited: true, disagreement_firing: true } }) }, incumbent);
assert.equal(siblingCleared.action, "PLACE_REST");

const holdExisting = gate.gateDecision({ clauses: { judgment_gate: true }, activeTarget: 37, birthLicense: license({ read: { passed: false } }) }, incumbent);
assert.equal(holdExisting.action, "HOLD_REST");
assert.equal(holdExisting.target_cents, 37);

const cancelExisting = gate.gateDecision({ clauses: { judgment_gate: true }, activeTarget: 37, birthLicense: license({ read: { passed: false } }) }, { action: "CANCEL_REST", target_cents: null, reason: "INCUMBENT_GUARD" });
assert.equal(cancelExisting.action, "CANCEL_REST");

const rows = [
  { timestamp_epoch: 0, spread: 8, midsum_abs_dev: 7, trades_60min: 0 },
  { timestamp_epoch: 60, spread: 8, midsum_abs_dev: 7, trades_60min: 0 },
  { timestamp_epoch: 120, spread: 1, midsum_abs_dev: 1, trades_60min: 2 },
  { timestamp_epoch: 180, spread: 1, midsum_abs_dev: 1, trades_60min: 3 },
];
const computed = onset.computeLegOnset(rows);
assert.equal(computed.candidates.A.timestamp_epoch, 120);
assert.equal(computed.selected.timestamp_epoch, 120);
assert.equal(onset.neutralTwoSegmentSplit(rows, "spread").after_mean, 1);

assert.equal(gate.normalizedClauses({ judgment_gate: true, scavenger: true }).scavenger, false);
console.log(JSON.stringify({ tests: 14, pass: true }));
