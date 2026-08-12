#!/usr/bin/env node
"use strict";

const assert = require("assert");
const v47 = require("../analysis/window1_v47_same_tick_arm.js");
const v49b = require("../analysis/window1_v49b_faithful_stand_at_p.js");

const clauses = { arm_at_first_evidence: true, deep_gap_guard: false, loosen_one_cent: true, release_guard_on_sibling_credit: true, same_tick_arm: true, trades_as_truth: true, faithful_stand_at_p: true };
const base = { state: "SETTLED", book: { kind: "BOOK", bid: 46, ask: 49, receipt: "book-now" }, activeTarget: null, pairCap: null, pulseFloor: null, persistentJoinLevel: null, currentJoinLevel: null, residencySeconds: 0, wtaInverseFalling: false, siblingCredited: false, clauses };
const doctrine = { level_cents: 46, authorized: true, causal_evidence: [{ source: "OWN_BEST_BID_REACHED_P", receipt: "book-now" }] };

{
  const out = v49b.decideReceipt({ ...base, doctrineStanding: doctrine });
  assert.equal(out.decision.target_cents, 46);
  assert.equal(out.decision.placement.doctrine_mechanism_code, "AT_P");
  assert.equal(out.decision.doctrine_standing.mechanism_code, "AT_P");
  assert(!JSON.stringify(out.decision.doctrine_standing).includes("BID_MINUS_ONE"));
}
{
  const out = v49b.decideReceipt({ ...base, book: { ...base.book, bid: 40 }, doctrineStanding: doctrine });
  assert.equal(out.decision.target_cents, 46, "P must not be recomputed from the current bid");
}
{
  const out = v49b.decideReceipt({ ...base, doctrineStanding: { ...doctrine, authorized: false } });
  const incumbent = v47.decideReceipt(base);
  assert.deepEqual({ ...out.decision, doctrine_standing: undefined }, { ...incumbent.decision, doctrine_standing: undefined });
}
{
  const out = v49b.decideReceipt({ ...base, book: { ...base.book, ask: 46 }, doctrineStanding: doctrine });
  assert.equal(out.decision.action, "HOLD_REST");
  assert.equal(out.decision.target_cents, null);
  assert.equal(out.decision.doctrine_standing.mechanism_code, "AT_P_UNAVAILABLE", "post-only sanity must abstain instead of falling back to bid-minus-one");
}
{
  const out = v49b.decideReceipt({ ...base, pairCap: 45, doctrineStanding: doctrine });
  assert.equal(out.decision.action, "HOLD_REST");
  assert.equal(out.decision.target_cents, null);
  assert.equal(out.decision.doctrine_standing.mechanism_code, "AT_P_UNAVAILABLE", "pair cap must abstain instead of falling back to bid-minus-one");
}
{
  const order = { target_cents: 46, action_ts: 100 };
  assert.equal(v49b.tradeTruthCredit(order, { kind: "PRINT", ts: 101, trade_id: "t", price: 46 }), true);
  assert.equal(v49b.tradeTruthCredit(order, { kind: "PRINT", ts: 100, trade_id: "t", price: 46 }), false);
}

console.log("V49b faithful stand-at-P policy tests PASS");
