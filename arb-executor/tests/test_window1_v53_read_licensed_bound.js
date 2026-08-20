"use strict";

const assert = require("assert");
const policy = require("../analysis/window1_v53_read_licensed_bound.js");

const makeState = (onset, prices) => {
  const state = policy.emptyLegState(onset);
  prices.forEach((price, index) => policy.observePostOnset(state, { ts: onset + index, receipt: `p-${price}-${index}`, kind: "PRINT", price }));
  return state;
};

const states = {
  A: makeState(100, [50, 49, 48, 47, 46]),
  B: makeState(100, [50, 51, 52, 53, 54]),
};
const context = { event_id: "TEST", category: "ATP_MAIN", row: { ts: 106, receipt: "eval", kind: "BOOK", bid: 45, ask: 47, depth_ratio: 0.5 }, states, shape_taxonomy_commit: "shape", shape_taxonomy_path: "path", trd5_commit: "trd5" };
const view = policy.buildGameView(states, context);
const plan = policy.buildPlan(view, context);
assert.equal(plan.licensed, true);
assert.equal(plan.bounds.A.running_session_low_cents, 46);
assert.equal(plan.bounds.B.running_session_low_cents, 50);
assert.equal(plan.delta_goal_deleted, true);
assert.equal(plan.pair_budget_derivation_deleted, true);
assert.equal(plan.owner_allowance_deleted, true);
assert.equal(plan.allocation_overlay_deleted, true);
assert.equal(Object.hasOwn(plan, "delta_goal_cents"), false);
assert.equal(Object.hasOwn(plan, "pair_budget_cents"), false);
assert.equal(Object.hasOwn(plan, "owner_leg_id"), false);

const fullEvidence = { sufficient: true, consulted: { comparable_book_transitions: 1 } };
const settled = policy.readLicensedBound({
  legId: "A",
  book: { receipt: "eval", depth_ratio: 0.5 },
  birthLicense: { read: { passed: true, quote_path_state: "SETTLED", pressure_state: "SETTLED", full_post_onset_evidence: fullEvidence } },
}, plan);
assert.equal(settled.authorized, true);
assert.equal(settled.running_session_low_cents, 46);
assert.equal(settled.no_span_fraction_consumed, true);

const directional = policy.readLicensedBound({
  legId: "A",
  book: { receipt: "eval", depth_ratio: 0.5 },
  birthLicense: { read: { passed: true, quote_path_state: "FALLING", pressure_state: "SETTLED", full_post_onset_evidence: fullEvidence } },
}, plan);
assert.equal(directional.authorized, false);
assert.equal(directional.reason, "QUOTE_PATH_NOT_SETTLED");

const unripe = policy.readLicensedBound({
  legId: "A",
  book: { receipt: "eval", depth_ratio: 0.5 },
  birthLicense: { read: { passed: false, quote_path_state: "SETTLED", pressure_state: "SETTLED", full_post_onset_evidence: { sufficient: false } } },
}, plan);
assert.equal(unripe.authorized, false);
assert.equal(unripe.reason, "QUOTE_PATH_CLASS_UNRIPE");

const conservation = policy.conservationInputs({ siblingCredited: true, siblingEntryCents: 54, siblingStandingTarget: 53, pairCap: 45 });
assert.deepEqual(conservation, { sibling_credited: true, sibling_entry_cents: 54, sibling_standing_target_cents: 53, pair_cap_cents: 45 });

process.stdout.write("window1_v53_read_licensed_bound: PASS\n");
