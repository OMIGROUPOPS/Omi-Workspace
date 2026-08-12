#!/usr/bin/env node
"use strict";

const assert = require("assert");
const floor = require("../analysis/window1_machine_anchored_floor.js");

const intervals = floor.buildStandingIntervals([
  { kind: "PLACE_REST", timestamp_epoch: 10, trace_ordinal: 1, receipt: "b10", target_cents: 50 },
  { kind: "REPRICE_REST", timestamp_epoch: 20, trace_ordinal: 2, receipt: "b20", target_cents: 48 },
  { kind: "FILL", timestamp_epoch: 30, trace_ordinal: 3, receipt: "p30" },
], 40);
assert.deepEqual(intervals.map((row) => [row.target_cents, row.start_timestamp_epoch, row.end_timestamp_epoch]), [[50, 10, 20], [48, 20, 30]]);
assert.equal(floor.intervalAt(intervals, 10), null, "the placement receipt cannot fill its own newly posted rest");
assert.equal(floor.intervalAt(intervals, 20).target_cents, 50, "same-timestamp evidence precedes the replacement action");
assert.equal(floor.intervalAt(intervals, 20.001).target_cents, 48);
const cursor = floor.makeIntervalCursor(intervals);
assert.equal(cursor(10), null);
assert.equal(cursor(20).target_cents, 50);
assert.equal(cursor(20.001).target_cents, 48);

const result = floor.evidenceFloor(intervals, [
  { kind: "BOOK", ts: 15, receipt: "q15", bid: 48, ask: 49, spread: 1, ask_dwell_seconds: 10, top_ask_size: 5 },
  { kind: "BOOK", ts: 25, receipt: "q25", bid: 46, ask: 47, spread: 1, ask_dwell_seconds: 9, top_ask_size: 100 },
], [
  { kind: "PRINT", ts: 5, receipt: "p5", trade_id: "t5", price: 40, size: 5, taker_side: "no" },
  { kind: "PRINT", ts: 28, receipt: "p28", trade_id: "t28", price: 46, size: 1, taker_side: "yes" },
]);
assert.equal(result.market_offered_trade_floor.price_cents, 40);
assert.equal(result.machine_quote_floor.price_cents, 49);
assert.equal(result.machine_trade_floor.price_cents, 46);
assert.equal(result.machine_floor.price_cents, 46);
assert.equal(result.machine_floor.channel, "TRUE_TRADE_WHILE_REST_STOOD");
assert.equal(floor.qualifyingAsk({ kind: "BOOK", ask: 20, ask_dwell_seconds: 10, top_ask_size: 5 }), true);
assert.equal(floor.qualifyingAsk({ kind: "BOOK", ask: 20, ask_dwell_seconds: 9, top_ask_size: 5 }), false);

assert.deepEqual(floor.distribution([0, 1, 2, null]), { n: 3, null_n: 1, sum: 3, min: 0, p25: 0, median: 1, p75: 2, p90: 2, max: 2 });
console.log("machine-anchored floor unit tests PASS");
