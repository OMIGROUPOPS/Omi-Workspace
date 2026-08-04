"use strict";

const assert = require("assert");
const {
  capFromTrace,
  capRearmReceipt,
  qualifiedAsk,
} = require("../analysis/window1_v28_anchor_cap_stack_policy.js");

function row(ts, bid, ask, dwell, size, ordinal = ts) {
  return { ts, bid, ask, spread: ask - bid, ask_dwell_seconds: dwell, top_ask_size: size, receipt: `synthetic#${ordinal}` };
}

const direct = { leg_identity: "E|A", first_flag: { layer: "PLACEMENT_CAP", timestamp: { epoch: 10 }, values_compared: { pair_cap_v23: { pair_cap_cents: 40 } } } };
const induced = { leg_identity: "E|B", first_flag: { layer: "PLACEMENT_CAP", timestamp: { epoch: 10 }, values_compared: { cap_cents: 40 } } };
const repair = { leg_identity: "E|C", first_flag: { layer: "PLACEMENT_CAP", timestamp: { epoch: 10 }, values_compared: { pair_cap: 40 } } };
assert.strictEqual(capFromTrace(direct), 40);
assert.strictEqual(capFromTrace(induced), 40);
assert.strictEqual(capFromTrace(repair), 40);

assert.strictEqual(qualifiedAsk(row(11, 39, 40, 10, 5)), true);
assert.strictEqual(qualifiedAsk(row(11, 39, 40, 9, 5)), false);
assert.strictEqual(qualifiedAsk(row(11, 39, 40, 10, 4)), false);

const receipt = capRearmReceipt(direct, [
  row(10, 39, 40, 100, 20, 1), // not strictly later
  row(11, 38, 40, 11, 20, 2),  // spread is not one
  row(12, 40, 41, 11, 20, 3),  // ask exceeds cap
  row(13, 39, 40, 10, 5, 4),
]);
assert.strictEqual(receipt.outcome, "CAP_REARMED_ON_QUALIFYING_ASK_AT_OR_BELOW_CAP");
assert.strictEqual(receipt.rearm.receipt, "synthetic#4");
assert.strictEqual(receipt.rearm.ask, 40);
assert.strictEqual(receipt.no_chase, true);

const absent = capRearmReceipt(direct, [row(11, 40, 41, 10, 5)]);
assert.strictEqual(absent.rearm, null);
assert.strictEqual(absent.outcome, "NO_QUALIFYING_RETURN_TO_CAP");

assert.throws(() => capFromTrace({ leg_identity: "BAD", first_flag: { values_compared: {} } }), /missing integer pair cap/);
assert.throws(() => capRearmReceipt({ first_flag: { layer: "ANCHOR" } }, []), /PLACEMENT_CAP/);

process.stdout.write("window1 V28 anchor+cap policy tests: PASS (13 assertions)\n");
