#!/usr/bin/env node
"use strict";

const assert = require("assert");
const { evaluateStableAskSigningSupport } = require("../analysis/window1_quote_shape_stable_signer_v4.js");

const initial = ({ sizeChanged = false, peak = 0, spread = 1, direction = "UP", siblingTransition = false, siblingDirection = "DOWN", siblingNet = -1 } = {}) => evaluateStableAskSigningSupport({
  leg: { resolved_direction: direction, last: { prefix: { ask_net: 0, ask_dip: 0 }, top_ask_size_ever_changed: sizeChanged, ask_peak_cents: peak, confirmation_spread_cents: spread } },
  sibling: { resolved_direction: siblingDirection, last: { ask_change_after_first_timestamp: siblingTransition, prefix: { ask_net: siblingNet } } },
  inverseSiblingResolved: true,
});

assert.deepStrictEqual(initial(), {
  required: true,
  supported: true,
  support_type: "TOP_ASK_PRICE_AND_SIZE_PERSISTED",
  predicates: { top_ask_price_and_size_persisted: true, ask_pulse_exceeded_spread_and_returned: false, resolved_inverse_sibling_has_ask_transition: false },
});
assert.strictEqual(initial({ sizeChanged: true }).supported, false);
assert.strictEqual(initial({ sizeChanged: true, peak: 1, spread: 1 }).supported, false);
assert.strictEqual(initial({ sizeChanged: true, peak: 7, spread: 1 }).support_type, "ASK_PULSE_EXCEEDED_SPREAD_AND_RETURNED");
assert.strictEqual(initial({ sizeChanged: true, peak: 7, spread: 1, direction: "FLAT" }).supported, false);
assert.strictEqual(initial({ sizeChanged: true, siblingTransition: true }).support_type, "RESOLVED_INVERSE_SIBLING_HAS_ASK_TRANSITION");
assert.strictEqual(initial({ sizeChanged: true, siblingTransition: true, siblingNet: 1 }).supported, false);
assert.strictEqual(evaluateStableAskSigningSupport({ leg: { last: { prefix: { ask_net: -1, ask_dip: -1 } } } }).support_type, "DEMONSTRATED_ASK_DESCENT");

console.log("PASS test_window1_quote_shape_stable_signer_v4 (8 assertions)");
