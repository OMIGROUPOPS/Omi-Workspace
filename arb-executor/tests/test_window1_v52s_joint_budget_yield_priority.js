"use strict";

const assert = require("assert");
const v52s = require("../analysis/window1_v52s_joint_budget_yield_priority.js");

const standing = (id, target, low, ask = 99) => ({ leg_identity: id, state: "STANDING_SIDE", default_target_cents: target, post_onset_session_low_cents: low, best_ask_cents: ask, pair_cap_cents: null });
const bought = (id, entry) => ({ leg_identity: id, state: "BOUGHT_SIDE", entry_cents: entry, post_onset_session_low_cents: null });

{
  const row = v52s.allocate([standing("B", 48, 49), standing("A", 49, 50)]);
  assert.equal(row.default_joint_sum_cents, 97);
  assert.equal(row.joint_target_sum_cents, 99);
  assert.deepEqual(row.allocations.map((x) => [x.leg_identity, x.allocated_target_cents]), [["A", 51], ["B", 48]]);
  assert.equal(row.invariant_pass, true);
}

{
  const row = v52s.allocate([bought("A", 60), standing("B", 37, 40)]);
  assert.equal(row.slack_before_lifts_cents, 2);
  assert.equal(row.allocations.find((x) => x.leg_identity === "B").allocated_target_cents, 39);
  assert.equal(row.joint_target_sum_cents, 99);
}

{
  const row = v52s.allocate([standing("A", 50, 55), standing("B", 49, 55)], { allow_lifts: false });
  assert.equal(row.allocations.some((x) => x.lift_active), false);
  assert.equal(row.joint_target_sum_cents, 99);
}

assert.throws(() => v52s.allocate([standing("A", 60, 60), standing("B", 40, 40)]), /senior target invariant/);
process.stdout.write("V52s joint-budget allocation tests PASS\n");
