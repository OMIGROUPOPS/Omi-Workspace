"use strict";

const assert = require("assert");
const v47 = require("../analysis/window1_v47_same_tick_arm.js");
const v50 = require("../analysis/window1_v50_first_fill_price_discipline.js");

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
  siblingCredited: false,
  clauses: {
    arm_at_first_evidence: true,
    deep_gap_guard: true,
    loosen_one_cent: true,
    release_guard_on_sibling_credit: true,
    same_tick_arm: true,
  },
};

assert.deepEqual(v50.decideReceipt(common), v47.decideReceipt(common));

const capped = v50.decideReceipt({
  ...common,
  siblingObservedFlowFloor: 44,
  clauses: { ...common.clauses, first_fill_price_discipline: true },
});
assert.equal(capped.decision.action, "PLACE_REST");
assert.equal(capped.decision.target_cents, 55);
assert.equal(capped.decision.first_fill_price_discipline.incumbent_target_cents, 60);
assert.equal(capped.decision.first_fill_price_discipline.observed_flow_cap_cents, 55);
assert.equal(capped.decision.first_fill_price_discipline.applied, true);

const fixedCapWins = v50.firstFillPriceBound({ pairCap: 35, siblingObservedFlowFloor: 44 });
assert.equal(fixedCapWins.effective_cap_cents, 35);

const noFlow = v50.firstFillPriceBound({ pairCap: null, siblingObservedFlowFloor: null });
assert.equal(noFlow.effective_cap_cents, null);
assert.equal(noFlow.authority, "UNBOUNDED_NO_SIBLING_FLOW");

const impossible = v50.decideReceipt({
  ...common,
  activeTarget: 20,
  siblingObservedFlowFloor: 99,
  clauses: { ...common.clauses, first_fill_price_discipline: true },
});
assert.equal(impossible.decision.action, "CANCEL_REST");
assert.equal(impossible.decision.reason, "V50_FIRST_FILL_PRICE_BOUND_NO_LAWFUL_CENT");

console.log("PASS test_window1_v50_first_fill_price_discipline");
