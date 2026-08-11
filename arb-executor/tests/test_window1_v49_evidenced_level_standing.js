#!/usr/bin/env node
"use strict";

const assert = require("assert");
const v49 = require("../analysis/window1_v49_evidenced_level_standing.js");

const clauses = { arm_at_first_evidence: true, deep_gap_guard: false, release_guard_on_sibling_credit: true, same_tick_arm: true, evidenced_level_standing: true };
const base = {
  state: "SETTLED",
  book: { kind: "BOOK", bid: 46, ask: 48, receipt: "book-now" },
  activeTarget: null,
  pairCap: null,
  pulseFloor: null,
  persistentJoinLevel: null,
  currentJoinLevel: null,
  residencySeconds: 0,
  wtaInverseFalling: false,
  siblingCredited: false,
  clauses,
};

{
  const out = v49.decideReceipt(base);
  assert.equal(out.decision.target_cents, 45);
  assert.equal(out.raised_to_evidenced_level, false);
  assert.equal(out.universal_loosen_enabled, false);
}
{
  const out = v49.decideReceipt({ ...base, priorExactBidEvidence: { level_cents: 46, receipt: "book-earlier", timestamp_epoch: 10 } });
  assert.equal(out.decision.target_cents, 45, "a prior sighting is not standing evidence");
  assert.equal(out.raised_to_evidenced_level, false);
}
{
  const out = v49.decideReceipt({ ...base, residencySeconds: 301, priorExactBidEvidence: { level_cents: 46, receipt: "book-earlier", timestamp_epoch: 10 } });
  assert.equal(out.decision.target_cents, 46);
  assert.equal(out.raised_to_evidenced_level, true);
  assert.equal(out.evidence.sources[0].source, "OWN_BEST_BID_P_CONTINUOUSLY_STANDING");
  assert.equal(out.evidence.sources[0].inherited_persistence_seconds, 300);
}
{
  const out = v49.decideReceipt({ ...base, priorTrueTradeLow: 44, priorTrueTradeLowReceipt: "trade-earlier" });
  assert.equal(out.decision.target_cents, 46);
  assert.equal(out.raised_to_evidenced_level, true);
  assert.equal(out.evidence.sources[0].source, "PRIOR_TRUE_TRADE_AT_OR_BELOW_P");
}
{
  const out = v49.decideReceipt({ ...base, book: { ...base.book, bid: 45 }, evidencedStandingLevel: 46, evidencedStandingAuthority: { evidenced: true, level_cents: 46, sources: [{ source: "PRIOR_OWN_BOOK_EXACT_BID_P", receipt: "book-earlier" }] } });
  assert.equal(out.decision.target_cents, 46, "an evidenced standing level must not chase a later lower bid");
  assert.equal(out.next_evidenced_standing_level_cents, 46);
}
{
  const out = v49.decideReceipt({ ...base, book: { ...base.book, ask: 46 }, residencySeconds: 301, priorExactBidEvidence: { level_cents: 46, receipt: "book-earlier" } });
  assert.equal(out.decision.target_cents, 45, "post-only sanity must bind");
  assert.equal(out.raised_to_evidenced_level, false);
}
{
  const out = v49.decideReceipt({ ...base, clauses: { ...clauses, evidenced_level_standing: false, loosen_one_cent: true } });
  assert.equal(out.decision.target_cents, 46, "feature-off path must preserve V47 universal loosen");
  assert.equal(out.universal_loosen_enabled, true);
}
{
  const joined = v49.decideReceipt({ ...base, state: "RISING", persistentJoinLevel: 42, currentJoinLevel: 42, residencySeconds: 301, priorExactBidEvidence: { level_cents: 46, receipt: "book-earlier" } });
  assert.equal(joined.decision.placement.authority, "V41_RISING_PERSISTENCE_ONLY_JOIN_300S_P2_OVER_P1", "incumbent join authority must remain in control");
  assert.equal(joined.raised_to_evidenced_level, false);
}
{
  const order = { target_cents: 46, action_ts: 100 };
  assert.equal(v49.tradeTruthCredit(order, { kind: "PRINT", ts: 101, trade_id: "t", price: 46 }), true);
  assert.equal(v49.tradeTruthCredit(order, { kind: "PRINT", ts: 100, trade_id: "t", price: 46 }), false);
}

console.log("V49 evidenced-level standing policy tests PASS");
