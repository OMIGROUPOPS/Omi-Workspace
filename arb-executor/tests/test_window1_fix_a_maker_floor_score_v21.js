#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/fix_a_maker_floor_score_v21_20260804");
const score = JSON.parse(fs.readFileSync(path.join(root, "FIX_A_MAKER_FLOOR_SCORE.json"), "utf8"));
const rows = zlib.gunzipSync(fs.readFileSync(path.join(root, "FIX_A_RECOVERED_LEG_MAKER_FLOOR_LEDGER.jsonl.gz")))
  .toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);

assert.strictEqual(rows.length, 337);
assert.strictEqual(score.aggregate.recovered_legs, 337);
assert.strictEqual(score.conservation.partition_rows, 337);
assert.strictEqual(score.conservation.reference_joined, 337);
assert.strictEqual(score.conservation.missing_reference, 0);
assert.strictEqual(score.conservation.maker_floor_recomputation_mismatches, 0);
assert.strictEqual(score.conservation.qualifying_ask_mismatches, 0);
assert.strictEqual(score.category_x_price_region.length, 16);
assert.strictEqual(score.category_x_price_region.reduce((n, cell) => n + cell.recovered_legs, 0), 337);

for (const row of rows) {
  const candidates = [row.qualifying_ask_floor_cents, row.seller_aggressed_traded_low_cents]
    .filter(Number.isInteger);
  assert.ok(candidates.length > 0, row.leg_identity);
  assert.strictEqual(row.maker_floor_cents, Math.min(...candidates), row.leg_identity);
  assert.strictEqual(row.entry_minus_maker_floor_cents, row.entry_cents - row.maker_floor_cents, row.leg_identity);
  assert.strictEqual(row.entry_minus_qualifying_ask_floor_cents, row.entry_cents - row.qualifying_ask_floor_cents, row.leg_identity);
  assert.ok(row.entry_minus_maker_floor_cents >= 0, row.leg_identity);
}

assert.deepStrictEqual(score.aggregate.maker_floor_buckets, {
  EXACT_MAKER_FLOOR: 66,
  FOUR_TO_NINE_ABOVE_MAKER_FLOOR: 13,
  ONE_CENT_ABOVE_MAKER_FLOOR: 168,
  TEN_OR_MORE_ABOVE_MAKER_FLOOR: 11,
  TWO_TO_THREE_ABOVE_MAKER_FLOOR: 79,
});
assert.deepStrictEqual(score.aggregate.maker_floor_source, {
  ASK_AND_SELLER_TIE: 72,
  QUALIFYING_ASK_RESIDENCY: 114,
  SELLER_AGGRESSED_TRADED_LOW: 151,
});
assert.strictEqual(score.aggregate.gap_to_maker_floor.total_numeric_cents, 726);
assert.strictEqual(score.aggregate.gap_to_qualifying_ask_floor.total_numeric_cents, 501);
process.stdout.write("PASS test_window1_fix_a_maker_floor_score_v21 (337 rows, 16 cells)\n");
