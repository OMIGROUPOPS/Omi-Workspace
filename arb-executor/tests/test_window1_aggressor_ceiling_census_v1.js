#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const out = path.join(repo, ".claude/window1_live_v4_replay/aggressor_ceiling_census_20260801");
const read = (name) => JSON.parse(fs.readFileSync(path.join(out, name), "utf8"));
const hash = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const sum = (rows, key) => rows.reduce((total, row) => total + row[key], 0);

const aggressor = read("AGGRESSOR_SPLIT.json");
const ceiling = read("CEILING_CENSUS.json");
const sources = read("SOURCE_HASH_MANIFEST.json");
const artifacts = read("ARTIFACT_HASH_MANIFEST.json");
const legRows = zlib.gunzipSync(fs.readFileSync(path.join(out, "PER_LEG_AGGRESSOR_CENSUS.jsonl.gz")))
  .toString("utf8").trim().split("\n").map(JSON.parse);

assert.strictEqual(aggressor.score_free, true);
assert.strictEqual(ceiling.score_free, true);
assert.strictEqual(ceiling.ex_post_oracle_only, true);
assert.strictEqual(aggressor.population.events, 804);
assert.strictEqual(aggressor.population.legs, 1608);
assert.strictEqual(aggressor.population.holdout_accessed, false);
assert.deepStrictEqual(aggressor.population.holdout_dates, ["2026-07-24", "2026-07-26"]);
assert.strictEqual(legRows.length, 1608);
assert.strictEqual(new Set(legRows.map((row) => `${row.event_id}|${row.leg}`)).size, 1608);
assert.strictEqual(new Set(legRows.map((row) => row.event_id)).size, 804);

const p = aggressor.print_conservation;
assert.strictEqual(p.lawful_admitted_prints, 126917);
assert.strictEqual(p.buyer_aggressed, 113892);
assert.strictEqual(p.seller_aggressed, 13025);
assert.strictEqual(p.unknown_aggressor, 0);
assert.strictEqual(p.buyer_aggressed + p.seller_aggressed + p.unknown_aggressor, p.lawful_admitted_prints);
assert.strictEqual(p.spread_bound + p.no_prior_bbo + p.equal_timestamp_cross_stream_ambiguous, p.lawful_admitted_prints);
assert.strictEqual(p.equal_timestamp_cross_stream_ambiguous, 0);
assert.strictEqual(p.no_prior_bbo, 994);

for (const key of [
  "by_category_and_starting_price_region",
  "by_category_and_print_price_region",
  "by_category_starting_price_region_and_spread",
  "by_category_starting_price_region_and_scheduled_clock",
  "by_category_starting_price_region_and_exact_bell_clock",
]) {
  const rows = aggressor[key];
  assert.strictEqual(sum(rows, "prints"), p.lawful_admitted_prints, `${key} print conservation`);
  assert.strictEqual(sum(rows, "buyer_aggressed"), p.buyer_aggressed, `${key} BUY conservation`);
  assert.strictEqual(sum(rows, "seller_aggressed"), p.seller_aggressed, `${key} SELL conservation`);
  assert.strictEqual(sum(rows, "unknown_aggressor"), 0, `${key} UNKNOWN conservation`);
  for (const row of rows) {
    assert.strictEqual(row.buyer_aggressed + row.seller_aggressed + row.unknown_aggressor, row.prints);
    assert(Math.abs(row.buyer_rate + row.seller_rate + row.unknown_rate - 1) < 1e-12);
  }
}

const summary = ceiling.summary;
assert.strictEqual(ceiling.controlling_take_ceiling, 516);
assert.strictEqual(summary.events, 804);
assert.strictEqual(summary.take_pair_combined_negative, 516);
assert.strictEqual(summary.take_pair_combined_negative_event_ids.length, 516);
assert.strictEqual(new Set(summary.take_pair_combined_negative_event_ids).size, 516);
assert.strictEqual(summary.maker_pair_combined_negative, 253);
assert.strictEqual(summary.maker_pair_combined_negative_event_ids.length, 253);
assert(summary.maker_pair_combined_negative_event_ids.every((id) => summary.take_pair_combined_negative_event_ids.includes(id)));
assert.strictEqual(summary.maker_both_legs_reachable, 318);
assert.strictEqual(summary.maker_both_legs_reachable_event_ids.length, 318);
assert.strictEqual(summary.take_both_legs_reachable, 786);
assert.strictEqual(summary.reference_missing_events, 182);
assert.strictEqual(summary.boundary_censored_events, 111);
assert.strictEqual(ceiling.events.length, 804);
assert.strictEqual(new Set(ceiling.events.map((row) => row.event_id)).size, 804);

assert.strictEqual(ceiling.partitions.length, 29);
assert.strictEqual(sum(ceiling.partitions, "events"), 804);
assert.strictEqual(sum(ceiling.partitions, "take_pair_combined_negative"), 516);
assert.strictEqual(sum(ceiling.partitions, "maker_pair_combined_negative"), 253);
assert.strictEqual(sum(ceiling.partitions, "maker_both_legs_reachable"), 318);
assert.strictEqual(sum(ceiling.partitions, "take_both_legs_reachable"), 786);

const recon = ceiling.guarded_cache_floor_reconciliation;
assert.strictEqual(recon.frozen_raw_tick_ceiling, 516);
assert.strictEqual(recon.guarded_cache_same_law_rederived_ceiling, 515);
assert.deepStrictEqual(recon.frozen_only_event_ids, [
  "KXATPMATCH-26JUL12CINHEM",
  "KXATPMATCH-26JUL12MOLFAU",
]);
assert.deepStrictEqual(recon.guarded_cache_only_event_ids, ["KXATPCHALLENGERMATCH-26JUL17HOLBOU"]);
assert.strictEqual(recon.guarded_cache_strict_later_capacity_ceiling, 512);
assert.deepStrictEqual(recon.strict_later_missing_from_frozen_event_ids, [
  "KXATPMATCH-26JUL12CINHEM",
  "KXATPMATCH-26JUL12MOLFAU",
  "KXATPMATCH-26JUL18MARJOR",
  "KXWTACHALLENGERMATCH-26JUL16FEISAM",
]);
assert.deepStrictEqual(recon.strict_later_extra_event_ids, []);

for (const row of legRows) {
  assert.strictEqual(row.aggressor_counts.prints, row.aggressor_counts.buyer_aggressed + row.aggressor_counts.seller_aggressed + row.aggressor_counts.unknown_aggressor);
  if (row.maker_reachable_at_frozen_target) {
    assert.strictEqual(row.maker_reachable_at_frozen_target.aggressor_side, "SELL");
    assert.strictEqual(row.maker_reachable_at_frozen_target.aggressor_source_law, "taker_side=no");
    assert(row.maker_reachable_at_frozen_target.print_price_cents <= row.maker_reachable_at_frozen_target.target_price_cents);
  }
}

assert.strictEqual(Object.keys(sources.sources.private_guarded_cache_v3).length, 804);
for (const rel of [
  ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv",
  ".claude/window1_start_guard_corrected_20260724/REAL_START_LEDGER_V5.jsonl",
  ".claude/window1_live_v4_replay/live_book_initial_aim_20260731/RAW_CAPACITY_FLOOR_SCAN.json",
  ".claude/window1_live_v4_replay/live_book_initial_aim_20260731/ASK_10S_FIVE_CONTRACT_CEILING.json",
]) {
  assert(sources.sources[rel]);
  assert.strictEqual(hash(path.join(repo, rel)), sources.sources[rel].sha256);
}
for (const [name, receipt] of Object.entries(artifacts.artifacts)) {
  const file = path.join(out, name);
  assert.strictEqual(fs.statSync(file).size, receipt.bytes, `${name} bytes`);
  assert.strictEqual(hash(file), receipt.sha256, `${name} sha256`);
}

for (const forbidden of ["score", "performance", "holdout_rows", "selection", "ranking"]) {
  assert(!Object.prototype.hasOwnProperty.call(ceiling, forbidden), `unexpected populated field: ${forbidden}`);
}

process.stdout.write(JSON.stringify({
  status: "PASS",
  tests: 78,
  events: 804,
  legs: 1608,
  prints: p.lawful_admitted_prints,
  buyer_aggressed: p.buyer_aggressed,
  seller_aggressed: p.seller_aggressed,
  take_ceiling: summary.take_pair_combined_negative,
  maker_ceiling: summary.maker_pair_combined_negative,
  maker_both_legs: summary.maker_both_legs_reachable,
}) + "\n");
