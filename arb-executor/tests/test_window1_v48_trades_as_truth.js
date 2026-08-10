"use strict";

const assert = require("assert");
const policy = require("../analysis/window1_v48_trades_as_truth.js");

const order = { target_cents: 50, action_ts: 100 };
assert.equal(policy.tradeTruthCredit(order, { kind: "PRINT", ts: 101, trade_id: "t1", price: 50, size: null, taker_side: null }), true);
assert.equal(policy.tradeTruthCredit(order, { kind: "PRINT", ts: 101, trade_id: "t2", price: 49, size: 1, taker_side: "yes" }), true);
assert.equal(policy.tradeTruthCredit(order, { kind: "PRINT", ts: 100, trade_id: "t3", price: 49 }), false);
assert.equal(policy.tradeTruthCredit(order, { kind: "BOOK", ts: 101, trade_id: "t4", price: 49 }), false);
assert.equal(policy.tradeTruthCredit(order, { kind: "PRINT", ts: 101, trade_id: "", price: 49 }), false);
assert.equal(policy.tradeTruthCredit(order, { kind: "PRINT", ts: 101, trade_id: "t5", price: 51 }), false);

const base = {
  state: "SETTLED",
  book: { bid: 50, ask: 52, receipt: "book-1" },
  residencySeconds: 0,
  currentJoinLevel: null,
  persistentJoinLevel: null,
  activeTarget: null,
  pairCap: null,
  siblingBestAsk: null,
  siblingCredited: false,
  clauses: { arm_at_first_evidence: true, deep_gap_guard: true, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true },
};
let result = policy.decideReceipt({ ...base, clauses: { ...base.clauses, placement_ladder: policy.PLACEMENT_LADDERS.BID_MINUS_ONE } });
assert.equal(result.decision.target_cents, 49);
result = policy.decideReceipt({ ...base, clauses: { ...base.clauses, placement_ladder: policy.PLACEMENT_LADDERS.BID } });
assert.equal(result.decision.target_cents, 50);
result = policy.decideReceipt({ ...base, recentTradeLow: 47, clauses: { ...base.clauses, placement_ladder: policy.PLACEMENT_LADDERS.LOWEST_RECENT_TRADED_LEVEL } });
assert.equal(result.decision.target_cents, 47);
assert.equal(result.decision.reason, "V48_LADDER_LOWEST_TRUE_TRADE_TRAILING_300S");
result = policy.decideReceipt({ ...base, recentTradeLow: null, clauses: { ...base.clauses, placement_ladder: policy.PLACEMENT_LADDERS.LOWEST_RECENT_TRADED_LEVEL } });
assert.equal(result.ladder_authority, "NO_CAUSAL_RECENT_TRADE_V47_INCUMBENT_FALLBACK");

console.log("PASS test_window1_v48_trades_as_truth");
