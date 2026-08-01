#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/honest_fill_model_20260801");
const contract = JSON.parse(fs.readFileSync(path.join(root, "HONEST_FILL_MODEL_CONTRACT.json")));
const fills = JSON.parse(fs.readFileSync(path.join(root, "FOUR_FILL_CLASSIFICATION.json")));
const pairs = JSON.parse(fs.readFileSync(path.join(root, "PAIR_COMPLETION_RESCORING.json")));
const determinism = JSON.parse(fs.readFileSync(path.join(root, "DETERMINISM_RECEIPT.json")));

assert.strictEqual(contract.score_free, true);
assert.strictEqual(contract.quantity_contracts, 5);
assert.deepStrictEqual(contract.precedence, ["PROVEN_TAKER", "PROVEN_MAKER", "UNPROVEN"]);
assert.strictEqual(contract.unproven_credit_law, "UNPROVEN rows are not completions.");
assert.strictEqual(contract.source_clock_binding.same_epoch_basis, true);
assert.strictEqual(contract.source_clock_binding.directly_comparable_across_distinct_seconds, true);
assert.strictEqual(contract.source_clock_binding.authoritative_cross_stream_order_within_same_second, false);

assert.strictEqual(fills.score_free, true);
assert.strictEqual(fills.replay_credit_rows, 4);
assert.strictEqual(fills.PROVEN_MAKER, 0);
assert.strictEqual(fills.PROVEN_TAKER, 3);
assert.strictEqual(fills.UNPROVEN, 1);
assert.strictEqual(fills.credited_leg_rows_under_honest_model, 3);
assert.strictEqual(fills.rows.length, 4);
assert.deepStrictEqual(Object.fromEntries(fills.rows.map((row) => [row.leg_id, row.fill_class])), {
  BIG: "PROVEN_TAKER",
  HUR: "UNPROVEN",
  NIK: "PROVEN_TAKER",
  VRB: "PROVEN_TAKER",
});
assert.deepStrictEqual(Object.fromEntries(fills.rows.map((row) => [row.leg_id, row.price_region])), {
  BIG: "51_75",
  HUR: "26_50",
  NIK: "26_50",
  VRB: "51_75",
});
assert(fills.rows.every((row) => row.price_region_source.includes("MAKER_TAKER_FILL_AUDIT.json") && row.price_region_source.includes("formed action book")));
assert(fills.rows.every((row) => row.seller_aggressed_print_proof_count === 0));
assert(fills.rows.every((row) => row.replay_same_receipt_credit === false));
assert(fills.rows.every((row) => row.replay_later_receipt_used_as_honest_credit_evidence === false));
assert(fills.rows.filter((row) => row.fill_class === "PROVEN_TAKER").every((row) => row.proven_taker_predicates.all_required));
assert(fills.rows.filter((row) => row.fill_class === "PROVEN_TAKER").every((row) => row.honest_credit_clock.timestamp_epoch === row.action_clock.timestamp_epoch && row.credited_quantity_contracts_under_honest_model === 5));
const hur = fills.rows.find((row) => row.leg_id === "HUR");
assert.strictEqual(hur.exact_timestamp_own_book_snapshot_at_action, false);
assert.strictEqual(hur.own_book_receipt_age_at_action_seconds, 43);
assert.strictEqual(hur.proven_taker_predicates.all_required, false);
assert.strictEqual(hur.proven_maker_predicates.all_required, false);
assert.strictEqual(hur.honest_credit_clock, null);
assert.strictEqual(hur.credited_quantity_contracts_under_honest_model, null);

assert.strictEqual(fills.category_price_region_partitions.length, 2);
assert.deepStrictEqual(fills.category_price_region_partitions.map((row) => [row.category, row.price_region, row.leg_count, row.PROVEN_MAKER, row.PROVEN_TAKER, row.UNPROVEN]), [
  ["ATP_CHALL", "26_50", 2, 0, 1, 1],
  ["ATP_CHALL", "51_75", 2, 0, 2, 0],
]);

assert.strictEqual(pairs.score_free, true);
assert.strictEqual(pairs.event_count, 2);
assert.strictEqual(pairs.completed_pair_count_under_honest_model, 1);
assert.strictEqual(pairs.incomplete_pair_count_under_honest_model, 1);
assert.strictEqual(pairs.performance_metrics, null);
const nikvrb = pairs.rows.find((row) => row.event_id.endsWith("NIKVRB"));
const hurbig = pairs.rows.find((row) => row.event_id.endsWith("HURBIG"));
assert.strictEqual(nikvrb.completed_pair_under_honest_model, true);
assert.strictEqual(nikvrb.pair_fee_class, "TWO_TAKER_LEGS_FEE_ARITHMETIC_REQUIRED");
assert.strictEqual(hurbig.completed_pair_under_honest_model, false);
assert.deepStrictEqual(determinism.volatile_fields, []);
assert.strictEqual(Object.keys(determinism.expected_core_artifact_hashes).length, 5);

process.stdout.write(JSON.stringify({ status: "PASS", assertions: 41, fills: 4, proven_maker: 0, proven_taker: 3, unproven: 1, completed_pairs: 1 }) + "\n");
