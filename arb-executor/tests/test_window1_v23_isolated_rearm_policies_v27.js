"use strict";

const assert = require("assert");
const {
  qualifiedAsk, findAnchorRearm, findCapRearm,
  unfalsifiableLowerReceipt, findAdmissionReask,
} = require("../analysis/window1_v23_isolated_rearm_policies_v27.js");

const row = (ts, ask, bid = ask - 1, dwell = 10, size = 5) => ({
  ts, receipt: `r${ts}`, bid, ask, spread: ask - bid,
  ask_dwell_seconds: dwell, top_ask_size: size,
});

assert.equal(qualifiedAsk(row(1, 50)), true);
assert.equal(qualifiedAsk(row(1, 50, 49, 9, 5)), false);
assert.equal(qualifiedAsk(row(1, 50, 49, 10, 4)), false);
assert.equal(findAnchorRearm([row(1, 50), row(2, 52)], { afterTs: 1, afterReceipt: "r1" }).ask, 52);
assert.equal(findAnchorRearm([row(1, 50), row(2, 52, 51, 9)], { afterTs: 1, afterReceipt: "r1" }), null);
assert.equal(findCapRearm([row(2, 50), row(3, 49)], { afterTs: 1, capCents: 49 }).ask, 49);
assert.equal(findCapRearm([row(2, 49, 47)], { afterTs: 1, capCents: 49 }), null, "spread must be one cent");

const snapshot = (counts, inverse = true) => ({
  reason: "ALL_SURVIVING_SHAPES_SAY_LOWER",
  shape_verdicts: [{ verdict: "LOWER", fitted_descent_distribution: { counts } }],
  predicates: {
    current_ask_at_observed_low: true,
    ask_dwell_at_least_10_seconds: true,
    top_ask_capacity_at_least_five: true,
    fresh_own_book_receipt: true,
    own_micro_position_observed: true,
    inverse_sibling_resolved: inverse,
  },
});
assert.deepEqual(unfalsifiableLowerReceipt(snapshot({ 0: 30 })), {
  touched: true,
  placeable: true,
  reason: "UNFALSIFIABLE_LOWER_SETTLED_BY_SUSTAINED_QUALIFIED_DWELL_AT_OBSERVED_LOW",
});
assert.equal(unfalsifiableLowerReceipt(snapshot({ 0: 30 }, false)).reason, "INVERSE_SIBLING_UNRESOLVED");
assert.equal(unfalsifiableLowerReceipt(snapshot({ 0: 10, 1: 20 })).touched, false);
assert.equal(findAdmissionReask([row(5, 51, 49), row(6, 50, 49)], { leftTs: 1, rightTs: 10 }).ts, 6);
assert.equal(findAdmissionReask([row(11, 50, 49)], { leftTs: 1, rightTs: 10 }), null);

process.stdout.write("test_window1_v23_isolated_rearm_policies_v27: PASS (13 assertions)\n");
