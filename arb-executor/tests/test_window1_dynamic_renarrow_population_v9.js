#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const out = path.join(repo, ".claude/window1_live_v4_replay/dynamic_renarrow_population_v9_20260802");
const read = (name) => JSON.parse(fs.readFileSync(path.join(out, name), "utf8"));
const rows = (name) => zlib.gunzipSync(fs.readFileSync(path.join(out, name))).toString("utf8").trim().split(/\r?\n/).map(JSON.parse);
const hash = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

const summary = read("POPULATION_SUMMARY.json");
const funnel = read("FUNNEL_RECEIPT.json");
const nonaction = read("NONACTION_CAUSE_CENSUS.json");
const legs = rows("POPULATION_LEG_LEDGER.jsonl.gz");
const events = rows("POPULATION_EVENT_LEDGER.jsonl.gz");

assert.strictEqual(legs.length, 1608);
assert.strictEqual(events.length, 804);
assert.strictEqual(new Set(legs.map((leg) => leg.leg_identity)).size, 1608);
assert.strictEqual(summary.close_law.close_available_legs, 1307);
assert.strictEqual(summary.close_law.close_unavailable_legs, 301);
assert.strictEqual(summary.close_law.properly_late_close_legs, 835);
assert.strictEqual(summary.close_law.both_closes_properly_late_events, 305);
assert.strictEqual(summary.close_law.properly_late_threshold_seconds, 300);
assert.strictEqual(summary.properly_late_close_individual_leg_slice.legs, 835);
assert.strictEqual(summary.properly_late_close_pair_cohort.leg_funnel.legs, 610);
assert.deepStrictEqual(summary.all_population.ceilings, { events: 804, absolute_traded_low: 580, traded_low_print_size_at_least_five: 558, capacity_proven_ask_floor: 516, lowest_seller_aggressed_trade_floor: 371, maker_reachable: 253 });
assert.strictEqual(funnel.all_population.legs, 1608);
assert.strictEqual(funnel.all_population.acted, 628);
assert.strictEqual(funnel.all_population.credited, 628);
assert.strictEqual(funnel.all_population.action_drop, 980);
assert.strictEqual(nonaction.total_nonacting_legs, 980);
assert.strictEqual(funnel.all_population.completed_pairs, 137);
assert.strictEqual(funnel.all_population.pairs_under_par, 72);
assert.strictEqual(funnel.all_population.final_under_par_and_both_below_close, 11);
assert.strictEqual(summary.all_population.event_performance.both_legs_strictly_below_close, 17);
assert.strictEqual(summary.properly_late_close_pair_cohort.event_performance.completed_pairs, 55);
assert.strictEqual(summary.properly_late_close_pair_cohort.event_performance.pairs_under_par, 29);
assert.strictEqual(summary.properly_late_close_pair_cohort.event_performance.under_par_and_both_legs_strictly_below_close, 6);
assert.strictEqual(nonaction.primary_causes.ASK_DID_NOT_RETURN_AFTER_CONSENSUS, 328);
assert.strictEqual(nonaction.primary_causes.FLOOR_CONSENSUS_NEVER_REACHED, 215);
assert.strictEqual(Object.values(nonaction.primary_causes).reduce((sum, value) => sum + value, 0), 980);
assert.strictEqual(Object.values(funnel.all_population.event_patterns).reduce((sum, value) => sum + value, 0), 804);
assert.strictEqual(summary.event_partitions_by_category_and_starting_price_split.reduce((sum, cell) => sum + cell.all_population.D, 0), 804);
assert.strictEqual(summary.leg_partitions_by_category_and_price_region.reduce((sum, cell) => sum + cell.legs, 0), 1608);

for (const leg of legs) {
  if (leg.close_status === "CLOSE_UNAVAILABLE") assert.strictEqual(leg.close_cents, null);
  if (leg.close_status === "PROPERLY_LATE_CLOSE") assert.ok(leg.close_seconds_before_guarded_right <= 300);
  if (leg.credited && Number.isInteger(leg.ask_capacity_floor_cents)) assert.strictEqual(leg.entry_minus_ask_floor_cents, leg.entry_cents - leg.ask_capacity_floor_cents);
  if (leg.credited && Number.isInteger(leg.traded_low_cents)) assert.strictEqual(leg.entry_minus_traded_low_cents, leg.entry_cents - leg.traded_low_cents);
}
for (const event of events) assert.strictEqual(event.leg_ids.length, 2);

const sources = read("SOURCE_HASH_MANIFEST.json");
for (const [relative, proof] of Object.entries(sources.files)) {
  const file = path.join(repo, relative);
  assert.strictEqual(hash(file), proof.sha256);
  assert.strictEqual(fs.statSync(file).size, proof.bytes);
}
for (const accessed of Object.values(sources.forbidden_access)) assert.strictEqual(accessed, false);

process.stdout.write("PASS test_window1_dynamic_renarrow_population_v9: 804 events, 1608 legs, 0 failures\n");
