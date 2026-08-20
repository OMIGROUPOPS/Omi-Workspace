"use strict";

const assert = require("assert");
const policy = require("../analysis/window1_v53_understanding_bounds.js");

const makeState = (onset, prices) => {
  const state = policy.emptyLegState(onset);
  prices.forEach((price, index) => policy.observePostOnset(state, { ts: onset + index, receipt: `p-${price}-${index}`, kind: "PRINT", price }));
  return state;
};

const states = {
  A: makeState(100, [50, 49, 48, 47, 46]),
  B: makeState(100, [50, 51, 52, 53, 54]),
};
const context = { event_id: "TEST", category: "ATP_MAIN", row: { ts: 106, receipt: "eval", kind: "BOOK", bid: 45, ask: 47 }, states, shape_taxonomy_commit: "shape", shape_taxonomy_path: "path", trd5_commit: "trd5" };
const view = policy.buildGameView(states, context);
const plan = policy.buildPlan(view, context);
assert.equal(plan.licensed, true);
assert.equal(plan.owner_leg_id, "A");
assert.equal(plan.depth_bounds.B.bound_cents, 50);
assert.equal(plan.depth_bounds.A.bound_cents, 45);
assert.equal(view.provenance.post_onset_only, true);

const partialStates = { A: makeState(100, [50, 49, 48, 47, 46]), B: policy.emptyLegState(100) };
const partialView = policy.buildGameView(partialStates, { ...context, states: partialStates });
const partialPlan = policy.buildPlan(partialView, { ...context, states: partialStates });
assert.equal(partialPlan.licensed, true, "missing running low must abstain, never gate");
assert.equal(partialPlan.reason, "VIEW_BOUNDS_PARTIAL_NO_GATE");
assert(!JSON.stringify(partialPlan).includes("PAIR_RUNNING_SESSION_LOW_INCOMPLETE"));

const nonOwnerLift = policy.liftProposal(plan, { legId: "B", siblingCredited: false, siblingStandingTarget: 40 }, 45);
assert.equal(nonOwnerLift.allocation_priority, "NON_OWNER_FIRST");
assert.equal(nonOwnerLift.allocated_target_cents, 50);

const ownerLift = policy.liftProposal(plan, { legId: "A", siblingCredited: false, siblingStandingTarget: 54 }, 40);
assert.equal(ownerLift.allocation_priority, "NON_OWNER_ALREADY_STANDING_THEN_OWNER");
assert(ownerLift.allocated_target_cents >= 40);

const conflict = policy.liftProposal(plan, { legId: "A", siblingCredited: false, siblingStandingTarget: 55 }, 45);
assert.equal(conflict.allocated_target_cents, 45, "budget conflict must not move below lineage");

process.stdout.write("window1_v53_understanding_bounds: PASS\n");
