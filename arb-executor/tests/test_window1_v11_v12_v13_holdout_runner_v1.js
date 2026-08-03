#!/usr/bin/env node
"use strict";

const assert = require("assert");
const {
  tickerIdentity,
  capacityFloor,
  pairNegative,
  distribution,
  metrics,
} = require("../analysis/window1_v11_v12_v13_holdout_runner_v1.js");
const { supportClass } = require("../analysis/build_window1_v11_v13_development_and_holdout_failure_v1.js");

const id = tickerIdentity("KXATPCHALLENGERMATCH-26JUL24DRACHI-CHI.csv.gz");
assert.deepStrictEqual(id, {
  event_id: "KXATPCHALLENGERMATCH-26JUL24DRACHI",
  leg_id: "CHI",
  ticker: "KXATPCHALLENGERMATCH-26JUL24DRACHI-CHI",
  category: "ATP_CHALL",
  event_date: "2026-07-24",
});
assert.strictEqual(tickerIdentity("KXATPCHALLENGERMATCH-26JUL23OLD-X.csv.gz"), null);

const books = [
  { ts: 100, ordinal: 2, ask: 55, asks: [[55, 3], [56, 4]] },
  { ts: 105, ordinal: 3, ask: 55, asks: [[55, 3], [56, 4]] },
  { ts: 110, ordinal: 4, ask: 55, asks: [[55, 3], [56, 4]] },
];
assert.deepStrictEqual(capacityFloor(books, 110), {
  limit_cents: 56,
  evidence_ts: 110,
  dwell_seconds: 10,
  displayed_capacity: 7,
  source_ordinal: 4,
  right_endpoint_carry: false,
});
assert.strictEqual(capacityFloor(books.slice(0, 2), 105), null);
assert.strictEqual(pairNegative([40, 55], [42, 60]), true);
assert.strictEqual(pairNegative([42, 60], [42, 60]), false);
assert.deepStrictEqual(distribution([0, 1, null], 3), {
  denominator: 3, available: 2, unavailable: 1,
  min: 0, p25: 0, median: 0, p75: 0, p90: 0, max: 1,
  exact_counts: { 0: 1, 1: 1, UNAVAILABLE: 1 },
});

const leg = (entry, askFloor, tradeFloor, acted = true) => ({
  acted,
  credited: Number.isInteger(entry),
  entry_cents: entry,
  entry_minus_qualifying_ask_floor_cents: Number.isInteger(entry) ? entry - askFloor : null,
  entry_minus_objective_traded_low_cents: Number.isInteger(entry) ? entry - tradeFloor : null,
  non_action_level: acted ? null : "MACRO_SHAPE",
  terminal_reason: acted ? "FILLED" : "UNRESOLVED",
});
const event = {
  completed_pair: true,
  pair_under_par: true,
  both_legs_strictly_below_close: true,
  legs: [leg(40, 40, 39), leg(55, 55, 54)],
  ceilings: Object.fromEntries(["absolute_traded_low", "traded_low_print_size_at_least_five", "capacity_proven_ask_floor", "lowest_seller_aggressed_trade_floor", "maker_reachable"].map((x) => [x, true])),
};
const m = metrics([event]);
assert.strictEqual(m.completed_pairs, 1);
assert.strictEqual(m.pairs_under_par, 1);
assert.strictEqual(m.execution_floor_pair_pass, 1);
assert.strictEqual(m.objective_trade_floor_pair_pass, 0);
assert.strictEqual(m.ceiling_comparison.maker_reachable.ceiling_events, 1);

assert.strictEqual(supportClass({ credited: true, qualifying_ask_floor_cents: 40, honest_fill_class: "PROVEN_TAKER", entry_minus_qualifying_ask_floor_cents: 0 }), "GENUINE_CATCH_AT_EXACT_QUALIFYING_ASK_FLOOR");
assert.strictEqual(supportClass({ credited: true, qualifying_ask_floor_cents: 40, honest_fill_class: "PROVEN_TAKER", entry_minus_qualifying_ask_floor_cents: 1 }), "GENUINE_NEAR_CATCH_WITHIN_ONE_CENT_OF_FLOOR");
assert.strictEqual(supportClass({ credited: true, qualifying_ask_floor_cents: 40, honest_fill_class: "PROVEN_TAKER", entry_minus_qualifying_ask_floor_cents: 2 }), "REAL_EXECUTABLE_ASK_BUT_TWO_PLUS_CENTS_ABOVE_FLOOR");
assert.strictEqual(supportClass({ credited: false, qualifying_ask_floor_cents: 40, honest_fill_class: "UNPROVEN", entry_minus_qualifying_ask_floor_cents: null }), "NO_LAWFUL_ASK_SUPPORT");

console.log(JSON.stringify({ status: "PASS", assertions: 18, holdout_access: false, network_access: false }));
