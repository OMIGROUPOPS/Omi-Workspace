"use strict";

const assert = require("assert");
const v47 = require("../analysis/window1_v47_same_tick_arm.js");
const v50r = require("../analysis/window1_v50r_one_directional_price_discipline.js");

const common = {
  state: "SETTLED",
  book: { bid: 60, ask: 62, receipt: "synthetic.csv.gz#row-12" },
  activeTarget: null,
  pairCap: null,
  pulseFloor: null,
  persistentJoinLevel: null,
  currentJoinLevel: null,
  residencySeconds: 0,
  wtaInverseFalling: false,
  causalOwnReachLow: null,
  siblingBestAsk: 45,
  siblingObservedFlowFloor: 44,
  siblingCredited: false,
  clauses: {
    arm_at_first_evidence: true,
    deep_gap_guard: true,
    loosen_one_cent: true,
    release_guard_on_sibling_credit: true,
    same_tick_arm: true,
    first_fill_price_discipline: true,
  },
};

const unhedged = v50r.decideReceipt(common);
assert.equal(unhedged.decision.action, "PLACE_REST");
assert.equal(unhedged.decision.target_cents, 55);
assert.equal(unhedged.decision.first_fill_price_discipline.applied, true);
assert.equal(unhedged.decision.first_fill_price_discipline.scope, "UNHEDGED_FIRST_FILL_ONLY");

const hedgedInputs = { ...common, activeTarget: 55, pairCap: 57, siblingCredited: true };
const hedged = v50r.decideReceipt(hedgedInputs);
const incumbent = v47.decideReceipt(hedgedInputs);
assert.equal(hedged.decision.first_fill_price_discipline.authority, "LIFTED_AT_SIBLING_CREDIT_FIXED_PAIR_CAP_ONLY");
assert.equal(hedged.decision.first_fill_price_discipline.effective_cap_cents, null);
assert.equal(hedged.decision.target_cents, incumbent.decision.target_cents);
assert.equal(hedged.decision.action, incumbent.decision.action);

const noFlow = v50r.firstFillPriceBound({ pairCap: null, siblingObservedFlowFloor: null, siblingCredited: false });
assert.equal(noFlow.effective_cap_cents, null);
assert.equal(noFlow.authority, "UNBOUNDED_NO_SIBLING_FLOW");

const lifted = v50r.firstFillPriceBound({ pairCap: 35, siblingObservedFlowFloor: 44, siblingCredited: true });
assert.equal(lifted.fixed_pair_cap_cents, 35);
assert.equal(lifted.counterfactual_observed_flow_cap_cents, 55);
assert.equal(lifted.observed_flow_cap_cents, null);
assert.equal(lifted.effective_cap_cents, null);

console.log("PASS test_window1_v50r_one_directional_price_discipline");
