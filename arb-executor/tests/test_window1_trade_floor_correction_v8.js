#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const out = path.join(repo, ".claude/window1_live_v4_replay/trade_floor_correction_v8_20260802");
const read = (name) => JSON.parse(fs.readFileSync(path.join(out, name), "utf8"));
const jsonlGz = (name) => zlib.gunzipSync(fs.readFileSync(path.join(out, name))).toString("utf8").trim().split(/\r?\n/).map(JSON.parse);
const sha256 = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");

const summary = read("DUAL_FLOOR_SUMMARY.json");
const classes = read("ASK_FLOOR_CLASS_RECONCILIATION.json");
const ceiling = read("CEILING_RECOMPUTATION.json");
const legs = jsonlGz("DUAL_FLOOR_LEG_LEDGER.jsonl.gz");
const events = jsonlGz("TRADE_FLOOR_EVENT_LEDGER.jsonl.gz");

assert.strictEqual(legs.length, 1608);
assert.strictEqual(events.length, 804);
assert.strictEqual(new Set(legs.map((row) => row.leg_identity)).size, 1608);
assert.strictEqual(new Set(events.map((row) => row.event_id)).size, 804);
assert.deepStrictEqual(ceiling.aggregate, {
  events: 804,
  ask_capacity_take_ceiling: 516,
  ask_target_seller_print_maker_ceiling: 253,
  any_trade_low_price_ceiling: 580,
  both_absolute_trade_lows_seller_aggressed_ceiling: 295,
  seller_aggressed_trade_floor_ceiling: 371,
  any_trade_size5_floor_ceiling: 558,
  seller_aggressed_size5_trade_floor_ceiling: 336,
});

assert.strictEqual(summary.aggregate_leg_floor_census.trade_low_below_ask_low, 597);
assert.strictEqual(summary.aggregate_leg_floor_census.trade_low_equals_ask_low, 687);
assert.strictEqual(summary.aggregate_leg_floor_census.trade_low_above_ask_low, 85);
assert.strictEqual(summary.aggregate_leg_floor_census.directly_comparable_ask_and_trade_floors, 1369);
assert.strictEqual(summary.aggregate_leg_floor_census.blank_source_window1_close, 301);
assert.strictEqual(summary.by_category_and_price_region.reduce((n, row) => n + row.legs, 0), 1608);

const above = classes.former_ask_floor_above_close;
const equal = classes.former_ask_floor_equals_close;
assert.strictEqual(above.legs, 317);
assert.strictEqual(above.corrected_close_available, 50);
assert.strictEqual(above.v7_blank_close_coerced_to_zero, 267);
assert.strictEqual(above.traded_low_available, 114);
assert.strictEqual(above.exact_close_price_print_sell, 42);
assert.strictEqual(equal.legs, 477);
assert.strictEqual(equal.corrected_close_available, 477);
assert.strictEqual(equal.traded_low_available, 477);
assert.strictEqual(equal.exact_close_price_print_sell, 41);

for (const leg of legs) {
  if (leg.positive_window1_provable) {
    assert.ok(Number.isFinite(leg.guarded_left_ts));
    assert.ok(Number.isFinite(leg.guarded_right_ts));
    assert.ok(leg.guarded_left_ts <= leg.guarded_right_ts);
  } else {
    assert.strictEqual(leg.lowest_traded_price_proof, null);
  }
  if (leg.lowest_traded_price_proof) {
    assert.strictEqual(leg.lowest_traded_price_proof.price_cents, leg.lowest_traded_price_cents);
    assert.ok(leg.lowest_traded_price_proof.prints.length >= 1);
    for (const print of leg.lowest_traded_price_proof.prints) {
      assert.ok(print.timestamp_epoch >= leg.guarded_left_ts && print.timestamp_epoch <= leg.guarded_right_ts);
      assert.ok(["BUY", "SELL", "UNKNOWN"].includes(print.aggressor_side));
      assert.ok(print.size > 0);
      assert.strictEqual(print.price_cents, leg.lowest_traded_price_cents);
    }
  }
  if (leg.any_trade_size5_floor) assert.ok(leg.any_trade_size5_floor.size >= 5);
  if (leg.seller_aggressed_size5_trade_floor) {
    assert.ok(leg.seller_aggressed_size5_trade_floor.size >= 5);
    assert.strictEqual(leg.seller_aggressed_size5_trade_floor.aggressor_side, "SELL");
  }
  if (leg.latest_print_at_frozen_close) {
    assert.strictEqual(leg.latest_print_at_frozen_close.price_cents, leg.own_window1_close_cents);
    assert.ok(leg.latest_print_at_frozen_close.seconds_before_guarded_right_edge >= 0);
  }
}

for (const event of events) {
  assert.strictEqual(Object.keys(event.legs).length, 2);
  assert.strictEqual(event.ask_capacity_take_ceiling_reconciliation_match, true);
  assert.strictEqual(event.ask_target_seller_print_maker_ceiling_reconciliation_match, true);
  assert.match(event.price_only_warning, /does not itself prove five-contract capacity/);
}

for (const value of Object.values(summary.metrics_and_performance_fields)) assert.strictEqual(value, null);
assert.strictEqual(summary.clock_law.directly_comparable, true);

const sources = read("SOURCE_HASH_MANIFEST.json");
for (const [relative, proof] of Object.entries(sources.committed)) {
  const file = path.join(repo, relative);
  assert.strictEqual(sha256(fs.readFileSync(file)), proof.sha256);
  assert.strictEqual(fs.statSync(file).size, proof.bytes);
}
for (const access of Object.values(sources.forbidden_access)) assert.strictEqual(access, false);

process.stdout.write("PASS test_window1_trade_floor_correction_v8: 1608 legs, 804 events, 0 failures\n");
