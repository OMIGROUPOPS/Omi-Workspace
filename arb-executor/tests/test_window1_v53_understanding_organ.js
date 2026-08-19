"use strict";

const assert = require("assert");
const organ = require("../analysis/window1_v53_understanding_organ.js");

const receipt = (ts, suffix, extra = {}) => ({ ts, receipt: `r-${suffix}`, kind: "BOOK", bid: 49, ask: 51, last_trade: null, ...extra });
const state = organ.emptyLegState(100);
organ.observePostOnset(state, receipt(99, "pre"));
assert.equal(state.observations.length, 0, "pre-onset receipt must not enter the view");
organ.observePostOnset(state, receipt(100, "a"));
organ.observePostOnset(state, { ts: 101, receipt: "p1", kind: "PRINT", price: 50 });
organ.observePostOnset(state, { ts: 102, receipt: "p2", kind: "PRINT", price: 49 });
organ.observePostOnset(state, { ts: 103, receipt: "p3", kind: "PRINT", price: 48 });
organ.observePostOnset(state, { ts: 104, receipt: "p4", kind: "PRINT", price: 47 });
organ.observePostOnset(state, { ts: 105, receipt: "p5", kind: "PRINT", price: 46 });
const sibling = organ.emptyLegState(100);
for (const [i, p] of [50, 51, 52, 53, 54].entries()) organ.observePostOnset(sibling, { ts: 101 + i, receipt: `s${i}`, kind: "PRINT", price: p });
const states = { A: state, B: sibling };
const context = { event_id: "TEST", category: "ATP_MAIN", row: receipt(106, "eval"), shape_taxonomy_commit: "shape", shape_taxonomy_path: "path", trd5_commit: "trd5", states };
const view = organ.buildGameView(states, context);
assert.equal(view.legs.A.role.value, "FALLER");
assert.equal(view.legs.B.role.value, "CLIMBER");
assert.equal(view.provenance.no_endpoint_labels_consumed, true);
const plan = organ.buildPlan(view, context);
assert.equal(plan.licensed, true);
assert(plan.target_sum_cents <= 99);
assert(plan.targets.A < view.legs.A.reach.running_session_low_cents, "stepping faller owns the deeper aim");

const wta = organ.legView(state, { category: "WTA_CHALL" });
assert.equal(wta.role.value, "UNRIPE", "WTA_CHALL role must remain disabled");

const decision = organ.decide({
  legId: "A", state: "FALLING", book: { bid: 44, ask: 47 }, activeTarget: null,
  pairCap: null, siblingCredited: false, siblingEntryCents: null, siblingStandingTarget: null,
  v53GameView: view, v53Plan: plan,
  birthLicense: { onset: { passed: true }, read: { passed: true }, coherence: { disagreement_clear: true, lows_under_par: true }, level: {} },
  clauses: { v53_understanding_organ: true },
});
assert.equal(decision.action, "PLACE_REST");
assert(decision.target_cents + plan.targets.B <= 99);
assert(decision.birth_license.game_view);
assert(decision.birth_license.plan);
assert.equal(decision.birth_license.level.N9_role, "ADVISORY_ONLY_NOT_TARGET_AUTHORITY");

process.stdout.write("window1_v53_understanding_organ: PASS\n");
