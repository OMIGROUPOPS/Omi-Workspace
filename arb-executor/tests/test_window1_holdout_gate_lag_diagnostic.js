#!/usr/bin/env node
"use strict";

const assert = require("assert");
const { lowerOutcome, candidateFromEvaluations, compareTerminal } = require("../analysis/build_window1_holdout_gate_lag_diagnostic_v1.js");

assert.strictEqual(lowerOutcome({ book: { ask: 55 } }, 55), "BOTTOMED_AT_REFUSAL");
assert.strictEqual(lowerOutcome({ book: { ask: 55 } }, 53), "WENT_LOWER_AFTER_REFUSAL");
assert.strictEqual(lowerOutcome(null, 53), "UNAVAILABLE");

const rows = [
  { ask_minus_observed_low_cents: 1, ask_dwell_seconds: 9, top_ask_size: 10, fresh_own_book_receipt: true, best_ask_cents: 51 },
  { ask_minus_observed_low_cents: 2, ask_dwell_seconds: 10, top_ask_size: 5, fresh_own_book_receipt: true, best_ask_cents: 52 },
  { ask_minus_observed_low_cents: 1, ask_dwell_seconds: 10, top_ask_size: 5, fresh_own_book_receipt: false, best_ask_cents: 51 },
];
assert.strictEqual(candidateFromEvaluations(rows, 1), null);
assert.strictEqual(candidateFromEvaluations(rows, 2).best_ask_cents, 52);

const terminal = { proposed_entry_cents: null, honest_fill_class: "UNPROVEN", honest_credited_entry_cents: null, own_window1_close_cents: 50, own_bell_price_cents: 51, own_ask_reachable_low_cents: 48, terminal_reason: "X", placement: null };
assert.doesNotThrow(() => compareTerminal(terminal, { ...terminal }, "SYNTHETIC|A"));
assert.throws(() => compareTerminal(terminal, { ...terminal, terminal_reason: "Y" }, "SYNTHETIC|A"), /trace changed terminal_reason/);

process.stdout.write("window1 holdout gate-lag diagnostic tests: PASS (7 assertions)\n");
