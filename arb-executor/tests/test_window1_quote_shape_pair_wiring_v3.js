#!/usr/bin/env node
"use strict";

const assert = require("assert");
const { completePairTupleSupport, evaluatePairWiringEvidence } = require("../analysis/window1_quote_shape_pair_wiring_v3.js");

const tuples = completePairTupleSupport({
  observedTupleObject: {
    "ATP_MAIN_26_50_UP_AFTER_DIP|ATP_MAIN_26_50_FLAT_UNMOVED": 1,
    "ATP_MAIN_26_50_UP_CONTINUATION|ATP_MAIN_26_50_DOWN_CONTINUATION": 2,
  },
  highShapes: ["ATP_MAIN_26_50_UP_AFTER_DIP", "ATP_MAIN_26_50_UP_CONTINUATION", "ATP_MAIN_26_50_FLAT_UNMOVED"],
  lowShapes: ["ATP_MAIN_26_50_FLAT_UNMOVED", "ATP_MAIN_26_50_DOWN_CONTINUATION"],
});
const flatFlat = tuples.find((row) => row.highShape.endsWith("FLAT_UNMOVED") && row.lowShape.endsWith("FLAT_UNMOVED"));
assert(flatFlat);
assert.strictEqual(flatFlat.n, 0);
assert.strictEqual(flatFlat.support_class, "STRUCTURAL_INVERSE_CLOSURE");
assert.strictEqual(tuples.find((row) => row.highShape.endsWith("UP_CONTINUATION") && row.lowShape.endsWith("DOWN_CONTINUATION")).support_class, "EMPIRICALLY_OBSERVED_PAIR_TUPLE");

const leg = {
  resolved_direction: "UP",
  last: { ask_change_after_first_timestamp: true, strictly_later_same_price_ask_receipt: true, ask_dwell_seconds: 20, top_ask_size: 10, prefix: { ask_net: 1 } },
};
const sibling = {
  survivor_shapes: ["WTA_26_50_DOWN_CONTINUATION"],
  independent_direction: null,
  last: { ask_change_after_first_timestamp: false, strictly_later_same_price_ask_receipt: true, ask_dwell_seconds: 20, top_ask_size: 10, prefix: { ask_net: 0 } },
};
const proof = evaluatePairWiringEvidence({ leg, sibling, dwellSeconds: 10, survivingTuples: [{ highShape: "WTA_51_75_UP_CONTINUATION", lowShape: "WTA_26_50_DOWN_CONTINUATION", n: 3 }], legRole: "highShape" });
assert.strictEqual(proof.inverse_sibling_resolved, true);
assert.strictEqual(proof.inverse_sibling_proof_type, "SINGLE_SURVIVING_INVERSE_PAIR_TUPLE_WITH_SIBLING_OWN_MICRO_RECEIPT");

const noSiblingReceipt = evaluatePairWiringEvidence({ leg, sibling: { ...sibling, last: { ...sibling.last, strictly_later_same_price_ask_receipt: false } }, dwellSeconds: 10, survivingTuples: [{ highShape: "WTA_51_75_UP_CONTINUATION", lowShape: "WTA_26_50_DOWN_CONTINUATION", n: 3 }], legRole: "highShape" });
assert.strictEqual(noSiblingReceipt.inverse_sibling_resolved, false);

const ambiguousTuple = evaluatePairWiringEvidence({ leg, sibling, dwellSeconds: 10, survivingTuples: [{ highShape: "WTA_51_75_UP_CONTINUATION", lowShape: "WTA_26_50_DOWN_CONTINUATION" }, { highShape: "WTA_51_75_UP_AFTER_DIP", lowShape: "WTA_26_50_DOWN_CONTINUATION" }], legRole: "highShape" });
assert.strictEqual(ambiguousTuple.inverse_sibling_resolved, false);

process.stdout.write("window1 quote-shape pair-wiring v3: 8 assertions passed\n");
