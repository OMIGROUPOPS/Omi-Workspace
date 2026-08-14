#!/usr/bin/env node
"use strict";

const assert = require("assert");
const onset = require("../analysis/window1_v52l_causal_stability_onset.js");

const base = { event_id: "SYNTH", left: 0, right: 600, legs: { A: {}, B: {} } };
const books = (offset) => [
  { ts: 0, bid: 48 + offset, ask: 52 + offset, spread: 4 },
  { ts: 60, bid: 49 + offset, ask: 51 + offset, spread: 2 },
  { ts: 120, bid: 49 + offset, ask: 50 + offset, spread: 1 },
  { ts: 10000, bid: 1, ask: 99, spread: 98 },
];
const tapes = new Map([["A", books(0)], ["B", books(0).map((row) => ({ ...row, bid: 100 - row.ask, ask: 100 - row.bid }))]]);
const prints = new Map([["A", [{ ts: 60 }, { ts: 120 }]], ["B", [{ ts: 60 }, { ts: 120 }]]]);
const first = onset.computeEventOnsets(base, tapes, prints);
const perturbed = onset.computeEventOnsets({ ...base, right: -999999 }, tapes, prints);
assert.deepStrictEqual(first, perturbed);
assert.strictEqual(first.A.right_edge_consumed, false);
assert.strictEqual(first.B.right_edge_consumed, false);
assert.strictEqual(first.A.full_span_fit, false);
assert.strictEqual(first.B.full_span_fit, false);
assert.ok(first.A.selected);
assert.ok(first.B.selected);
assert.ok(first.A.maximum_consumed_timestamp_epoch <= first.A.selected.timestamp_epoch);
assert.ok(first.B.maximum_consumed_timestamp_epoch <= first.B.selected.timestamp_epoch);
assert.strictEqual(onset.assertRightEdgeIndependence(base, tapes, prints).pass, true);

const futureChanged = new Map([...tapes].map(([id, rows]) => [id, rows.map((row) => row.ts === 10000 ? { ...row, bid: 45, ask: 55, spread: 10 } : row)]));
assert.deepStrictEqual(first, onset.computeEventOnsets(base, futureChanged, prints));
const split = onset.neutralTwoSegmentSplit([{ timestamp_epoch: 0, x: 5 }, { timestamp_epoch: 1, x: 1 }], "x");
assert.strictEqual(split.before_n, 1);
assert.strictEqual(split.after_n, 1);
process.stdout.write(`${JSON.stringify({ assertions: 14, failures: 0, right_edge_independent: true })}\n`);
