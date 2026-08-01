#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_maker_insufficient_diagnosis_20260801");
const maker = JSON.parse(fs.readFileSync(path.join(root, "MAKER_TAKER_FILL_AUDIT.json")));
const insufficient = JSON.parse(fs.readFileSync(path.join(root, "INSUFFICIENT_PREDICATE_DIAGNOSIS.json")));
const floors = JSON.parse(fs.readFileSync(path.join(root, "ASK_LOW_DWELL_CAPACITY_LEDGER.json")));

assert.strictEqual(maker.credited_fill_count, 4);
assert.strictEqual(maker.taker_or_marketable_fill_count, 4);
assert.strictEqual(maker.maker_only_creditable_fill_count, 0);
assert.deepStrictEqual(maker.fills.map((row) => row.placement_relation), Array(4).fill("SITTING_AT_ASK_MARKETABLE_BUY"));
assert.deepStrictEqual(maker.fills.map((row) => row.maker_only_live_chokepoint_relation), Array(4).fill("JOINING_BID"));
assert(maker.fills.every((row) => row.original_fill_receipt_reaches_clamped_maker_price === false));
assert.deepStrictEqual(Object.fromEntries(maker.fills.map((row) => [row.leg_id, [row.order_price_cents, row.action_book.bid, row.action_book.ask, row.maker_fee_total_cents_for_five_contract_order, row.taker_fee_total_cents_for_five_contract_order]])), {
  BIG: [55, 54, 55, 3, 9],
  HUR: [38, 37, 38, 3, 9],
  NIK: [18, 17, 18, 2, 6],
  VRB: [68, 67, 68, 2, 8],
});
assert(maker.completed_pairs.every((row) => row.maker_only_completion_valid === false));
assert.deepStrictEqual(Object.fromEntries(maker.completed_pairs.map((row) => [row.event_id.split("26JUL19")[1], [row.price_only_combined_delta_to_own_closes_cents_per_contract, row.taker_fee_adjusted_delta_cents_per_contract]])), {
  HURBIG: [-9, -5.4],
  NIKVRB: [-16, -13.2],
});

assert.strictEqual(insufficient.leg_count, 6);
assert(insufficient.rows.every((row) => row.shape_partition_is_the_226_leg_partition === false));
for (const legId of ["LAJ", "VAN"]) {
  const row = insufficient.rows.find((candidate) => candidate.leg_id === legId);
  assert.strictEqual(row.library_partition.n, 96);
  assert.strictEqual(row.terminal_blocker_class, "LIBRARY_FITTING_PAIR_TUPLE_COVERAGE_DEFECT");
  assert.strictEqual(row.ever_leg_shape_set_collapsed_to_one, true);
  assert.strictEqual(row.ever_pair_constrained_shape_set_collapsed_to_one, false);
  assert.strictEqual(row.terminal_evaluation.pair_constrained_surviving_shapes.length, 0);
}
for (const legId of ["BRA", "VED", "JIM", "KOR"]) {
  const row = insufficient.rows.find((candidate) => candidate.leg_id === legId);
  assert.strictEqual(row.terminal_blocker_class, "PAIR_EVIDENCE_PREDICATE_UNPROVEN");
  assert.strictEqual(row.terminal_evaluation.reason, "FLOOR_CONSENSUS_BUT_SIBLING_DIRECTION_NOT_INDEPENDENTLY_OBSERVED");
  assert.strictEqual(row.terminal_evaluation.pair_constrained_surviving_shapes.length, 1);
}
assert.deepStrictEqual(insufficient.rows.filter((row) => !row.stale_reason_matches_recomputed_terminal).map((row) => row.leg_id).sort(), ["BRA", "KOR", "LAJ"]);

assert.strictEqual(floors.row_count, 6);
assert.deepStrictEqual(Object.fromEntries(floors.rows.map((row) => [row.leg_id, [row.ask_reachable_low_cents, row.proof.dwell_seconds_at_first_proof, row.proof.displayed_capacity_at_or_below_limit, row.signed_low_minus_close_cents]])), {
  LAJ: [45, 114, 883, 0],
  VAN: [50, 25, 351, -7],
  BRA: [40, 10, 2180, -4],
  VED: [57, 13, 4886, 0],
  JIM: [30, 10, 380, -2],
  KOR: [60, 13, 394, -10],
});
assert.deepStrictEqual(Object.fromEntries(floors.event_pairs.map((row) => [row.event_id.split("26JUL").at(-1).replace(/^\d+/, ""), row.discount_left_unharvested_cents])), { LAJVAN: 7, BRAVED: 4, KORJIM: 12 });

const trace = zlib.gunzipSync(fs.readFileSync(path.join(root, "PER_TICK_INSUFFICIENCY_TRACE.jsonl.gz"))).toString("utf8").trimEnd().split("\n").map(JSON.parse);
assert.strictEqual(trace.length, 27617);
assert.deepStrictEqual([...new Set(trace.map((row) => row.leg_id))].sort(), ["BRA", "JIM", "KOR", "LAJ", "VAN", "VED"]);
assert(trace.every((row) => Number.isInteger(row.book.bid) && Number.isInteger(row.book.ask) && row.book.spread === row.book.ask - row.book.bid && Number.isFinite(row.book.ask_dwell_seconds)));
assert(trace.every((row) => Number.isFinite(row.t_minus_scheduled_seconds) && Number.isFinite(row.t_minus_actual_bell_seconds)));

process.stdout.write(JSON.stringify({ status: "PASS", assertions: 38, credited_fills: 4, insufficient_legs: 6, per_tick_rows: trace.length }) + "\n");
