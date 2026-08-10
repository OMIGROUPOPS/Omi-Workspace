"use strict";

const assert = require("assert");
const v45 = require("../analysis/window1_v45_guard_release_sibling_credit.js");
const v47 = require("../analysis/window1_v47_same_tick_arm.js");

const book = { bid: 47, ask: 49, receipt: "synthetic.csv.gz#row-173" };
const common = {
  state: "RISING",
  book,
  activeTarget: 46,
  pairCap: null,
  pulseFloor: null,
  currentJoinLevel: 46,
  residencySeconds: 300,
  wtaInverseFalling: false,
  causalOwnReachLow: null,
  siblingBestAsk: 55,
  siblingCredited: false,
  clauses: {
    arm_at_first_evidence: true,
    deep_gap_guard: true,
    loosen_one_cent: true,
    release_guard_on_sibling_credit: true,
    same_tick_arm: true,
  },
};

const atomic = v47.decideReceipt(common);
assert.equal(atomic.join.armed, true);
assert.equal(atomic.join.changed, true);
assert.equal(atomic.effective_join_level_cents, 47);
assert.equal(atomic.atomic_receipt, book.receipt);
assert.equal(atomic.decision.action, "REPRICE_REST");
assert.equal(atomic.decision.target_cents, 47);

const incumbentJoin = v45.persistenceJoinUpdate({
  state: common.state,
  bid: book.bid,
  residencySeconds: common.residencySeconds,
  currentJoinLevel: common.currentJoinLevel,
  clauses: common.clauses,
});
const incumbent = v45.decide({ ...common, persistentJoinLevel: incumbentJoin.level_cents });
assert.deepEqual(atomic.decision, incumbent);

const blocked = v47.decideReceipt({ ...common, siblingBestAsk: 93 });
assert.equal(blocked.join.changed, true);
assert.equal(blocked.decision.guard.withheld, true);
assert.notEqual(blocked.decision.action, "REPRICE_REST");

console.log("PASS test_window1_v47_same_tick_arm");
