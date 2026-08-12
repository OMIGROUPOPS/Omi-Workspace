#!/usr/bin/env node
"use strict";

const assert = require("assert");
const v52 = require("../analysis/window1_v52_judgment_gate.js");
const v52b = require("../analysis/window1_v52b_read_level_authority.js");

function license(overrides = {}) {
  const base = {
    onset: { passed: true, selected_candidate: "A_SPREAD_COLLAPSE_PLUS_CROSS_LEG_MIDSUM_SETTLE", timestamp_epoch: 100 },
    read: { passed: true, state: "FALLING", receipt: "quote#8" },
    diary: { passed: true, own_post_onset_true_trade_low_cents: 37, sibling_post_onset_true_trade_low_cents: 55, displayed_bid_consumed: false },
    coherence: { lows_under_par: true, disagreement_clear: true, sibling_credited: false },
    level: {
      target_cents: 37,
      authority: "POST_ONSET_RUNNING_TRUE_TRADE_LOW_DIARY",
      displayed_bid_consumed: false,
      machine_read_evidence: {
        evaluation_timestamp_epoch: 130,
        evaluation_receipt: "book#10",
        directional_evidence_timestamp_epoch: 125,
        directional_evidence_receipt: "quote#8",
        directional_evidence_kind: "NEW_LOW_ASK",
        post_onset_observation_bounds: { min_cents: 30, max_cents: 70 },
      },
    },
    scavenger: { enabled: false },
  };
  return { ...base, ...overrides };
}

const incumbent = { action: "PLACE_REST", target_cents: 42, reason: "V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY", placement: { target_cents: 42, authority: "V43_C3_TRACKING_REST_BEST_BID_ONE_CENT_LESS_GREEDY" } };

const frozen = v52.gateDecision({ clauses: { judgment_gate: true }, activeTarget: null, birthLicense: license() }, incumbent);
const delegated = v52b.gateDecision({ clauses: { judgment_gate: true, machine_read_level_authority: false }, activeTarget: null, birthLicense: license() }, incumbent);
assert.deepStrictEqual(delegated, frozen);

const placed = v52b.gateDecision({ clauses: { judgment_gate: true, machine_read_level_authority: true }, activeTarget: null, birthLicense: license() }, incumbent);
assert.equal(placed.action, "PLACE_REST");
assert.equal(placed.target_cents, 42);
assert.equal(placed.birth_license.onset.binding_status, "CODEX-INTERIM");
assert.equal(placed.birth_license.onset.binding_changed_by_V52b, false);
assert.equal(placed.birth_license.diary.role, "RECORDED_REFERENCE_INPUT_NOT_SOLE_LEVEL_AUTHORITY");
assert.equal(placed.birth_license.level.authority, "V52B_EVIDENCE_BACKED_MACHINE_READ_LEVEL");
assert.equal(placed.birth_license.level.machine_read.authorized, true);

const diaryNotSole = v52b.gateDecision({ clauses: { judgment_gate: true, machine_read_level_authority: true }, activeTarget: null, birthLicense: license({ diary: { passed: false, displayed_bid_consumed: false } }) }, incumbent);
assert.equal(diaryNotSole.action, "PLACE_REST");

for (const [changed, failure] of [
  [{ level: { ...license().level, machine_read_evidence: { ...license().level.machine_read_evidence, directional_evidence_receipt: null } } }, "MACHINE_READ_LEVEL_AUTHORITY_NOT_EARNED"],
  [{ level: { ...license().level, machine_read_evidence: { ...license().level.machine_read_evidence, post_onset_observation_bounds: { min_cents: 43, max_cents: 70 } } } }, "MACHINE_READ_LEVEL_AUTHORITY_NOT_EARNED"],
  [{ coherence: { lows_under_par: false, disagreement_clear: true } }, "PAIR_POST_ONSET_LOWS_NOT_UNDER_PAR"],
  [{ coherence: { lows_under_par: true, disagreement_clear: false } }, "FIRING_DISAGREEMENT_ACTIVE"],
]) {
  const blocked = v52b.gateDecision({ clauses: { judgment_gate: true, machine_read_level_authority: true }, activeTarget: null, birthLicense: license(changed) }, incumbent);
  assert.equal(blocked.action, "HOLD_REST");
  assert.equal(blocked.judgment_gate.failure, failure);
}

const unsupported = { ...incumbent, reason: "V49B_FAITHFUL_STAND_AT_P", placement: { target_cents: 42, authority: "V49B_FAITHFUL_STAND_AT_P" } };
assert.equal(v52b.gateDecision({ clauses: { judgment_gate: true, machine_read_level_authority: true }, activeTarget: null, birthLicense: license() }, unsupported).judgment_gate.failure, "MACHINE_READ_LEVEL_AUTHORITY_NOT_EARNED");

const cancel = v52b.gateDecision({ clauses: { judgment_gate: true, machine_read_level_authority: true }, activeTarget: 42, birthLicense: license() }, { ...incumbent, action: "CANCEL_REST" });
assert.equal(cancel.action, "CANCEL_REST");
assert.equal(v52b.normalizedClauses({ judgment_gate: true, machine_read_level_authority: true, scavenger: true }).scavenger, false);

console.log(JSON.stringify({ tests: 17, pass: true }));
