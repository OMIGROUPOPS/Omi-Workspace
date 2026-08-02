"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/consensus_lag_repair_v10_20260802");
const json = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
const jsonl = (name) => zlib.gunzipSync(fs.readFileSync(path.join(root, name))).toString("utf8").trim().split(/\r?\n/).map(JSON.parse);

const lag = json("LAG_DIAGNOSIS_SUMMARY.json");
const lower = json("LOWER_VERDICT_SPLIT.json");
const summary = json("POPULATION_SUMMARY.json");
const funnel = json("FUNNEL_RECEIPT.json");
const deterministic = json("DETERMINISM_RECEIPT.json");
const legs = jsonl("POPULATION_LEG_LEDGER.jsonl.gz");
const events = jsonl("POPULATION_EVENT_LEDGER.jsonl.gz");
const artifactManifest = json("ARTIFACT_HASH_MANIFEST.json");
const sourceManifest = json("SOURCE_HASH_MANIFEST.json");
const hash = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");

assert.strictEqual(lag.controlling_class_legs, 328);
assert.strictEqual(lag.counterfactual_full_consensus_at_low_fill_prize, 291);
assert.deepStrictEqual(lag.temporal_order, { LOW_BEFORE_CONSENSUS: 312, CONSENSUS_BEFORE_LOW: 8, TIMING_UNAVAILABLE: 6, SAME_TIMESTAMP: 2 });
assert.strictEqual(lower.controlling_class_legs, 215);
assert.deepStrictEqual(lower.first_decline_outcomes, { ASK_WENT_LOWER_AFTER_FIRST_DECLINE: 95, BOTTOMED_AT_FIRST_DECLINED_ASK: 88, NO_ACTIONABLE_LOWER_RECEIPT: 32 });
assert.strictEqual(events.length, 804);
assert.strictEqual(legs.length, 1608);
assert.strictEqual(events.filter((x) => x.both_closes_properly_late).length, 305);
assert.strictEqual(funnel.full_population.ceiling_comparison.absolute_traded_low.ceiling_events, 580);
assert.strictEqual(funnel.full_population.ceiling_comparison.traded_low_print_size_at_least_five.ceiling_events, 558);
assert.strictEqual(funnel.full_population.ceiling_comparison.capacity_proven_ask_floor.ceiling_events, 516);
assert.strictEqual(funnel.full_population.ceiling_comparison.lowest_seller_aggressed_trade_floor.ceiling_events, 371);
assert.strictEqual(funnel.full_population.ceiling_comparison.maker_reachable.ceiling_events, 253);
assert.strictEqual(summary.movement.lost_action_legs, 0);
assert.strictEqual(summary.repair.no_new_instrument, true);
assert.strictEqual(summary.repair.no_forecast, true);
assert.strictEqual(summary.repair.no_fee_test, true);
assert.deepStrictEqual(summary.performance_fields, { C: null, PC: null, IC: null, S: null, ranking: null, selection: null });
assert.strictEqual(legs.every((x) => Object.hasOwn(x, "qualifying_ask_floor_cents") && Object.hasOwn(x, "objective_traded_low_cents")), true);
assert.strictEqual(deterministic.byte_identical, true);
assert.strictEqual(deterministic.cold_repaired_replays, 2);
assert.strictEqual(Object.values(funnel.full_population.no_action_terminal_reasons).reduce((a, b) => a + b, 0), funnel.full_population.no_action_legs);
assert.strictEqual(funnel.category_and_starting_price_partitions.reduce((n, x) => n + x.full_population.events, 0), 804);
assert.strictEqual(funnel.category_and_starting_price_partitions.reduce((n, x) => n + x.strict_late_close_cohort.events, 0), 305);
assert.strictEqual(Object.entries(artifactManifest.files).every(([name, item]) => hash(fs.readFileSync(path.join(root, name))) === item.sha256), true);
assert.strictEqual(Object.entries(sourceManifest.files).every(([name, item]) => hash(fs.readFileSync(path.join(repo, name))) === item.sha256), true);

process.stdout.write(`${JSON.stringify({ status: "PASS", assertions: 27, events: events.length, legs: legs.length })}\n`);
