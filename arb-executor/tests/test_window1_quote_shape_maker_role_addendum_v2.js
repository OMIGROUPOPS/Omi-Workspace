#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_maker_role_addendum_20260801");
const audit = JSON.parse(fs.readFileSync(path.join(root, "MAKER_ROLE_RECEIPT_AUDIT.json")));
const sequences = JSON.parse(fs.readFileSync(path.join(root, "EXACT_ACTION_TO_CREDIT_SEQUENCE.json")));
const big = JSON.parse(fs.readFileSync(path.join(root, "BIG_FULL_ASK_PROGRESSION.json")));

assert.strictEqual(audit.score_free, true);
assert.strictEqual(audit.fill_count, 4);
assert.strictEqual(audit.receipt_proven_maker_count, 0);
assert.strictEqual(audit.receipt_proven_taker_count, 0);
assert.strictEqual(audit.receipt_role_not_established_count, 4);
assert.strictEqual(audit.marketable_if_submitted_unchanged_count, 4);
assert.strictEqual(audit.replay_same_receipt_credit_count, 0);
assert(audit.fills.every((row) => row.exchange_order_submission_receipt_present === false));
assert(audit.fills.every((row) => row.exchange_order_acknowledgement_present === false));
assert(audit.fills.every((row) => row.exchange_liquidity_role_or_fee_receipt_present === false));
assert(audit.fills.every((row) => row.receipt_proven_liquidity_role === "NOT_ESTABLISHED"));
assert(audit.fills.every((row) => row.receipt_proven_fee_treatment === "NOT_ESTABLISHED"));
assert(audit.fills.every((row) => row.marketability_if_submitted_unchanged_against_action_snapshot === "MARKETABLE_TAKER"));
assert(audit.fills.every((row) => row.live_post_only_relation === "JOINING_BID"));
assert.deepStrictEqual(Object.fromEntries(audit.fills.map((row) => [row.leg_id, [row.own_book_at_action.bid, row.own_book_at_action.ask, row.x_cents, row.displayed_external_ask_size_at_x_when_actioned, row.own_book_receipt_age_at_action_seconds, row.replay_action_to_credit_seconds, row.exact_action_through_credit_sequence_row_count]])), {
  BIG: [54, 55, 55, 817, 0, 5, 5],
  HUR: [37, 38, 38, 10113, 43, 1, 2],
  NIK: [17, 18, 18, 1201, 0, 1, 7],
  VRB: [67, 68, 68, 110, 0, 881, 263],
});
assert.deepStrictEqual(Object.fromEntries(audit.fills.map((row) => [row.leg_id, [row.live_post_only_chokepoint_price_cents, row.raw_minimum_ask_after_action_cents, Boolean(row.ten_second_five_contract_ask_proof_at_or_below_live_clamp)]])), {
  BIG: [54, 55, false],
  HUR: [37, 37, true],
  NIK: [17, 18, false],
  VRB: [67, 68, false],
});
assert(audit.pair_maker_assessment.every((row) => row.maker_only_pair_completion_supported_by_replay_evidence === false));

assert.strictEqual(sequences.fill_count, 4);
for (const sequence of sequences.sequences) {
  assert.strictEqual(sequence.rows[0].source_receipt, sequence.own_book_receipt_at_action);
  assert.strictEqual(sequence.rows.at(-1).source_receipt, sequence.fill_receipt);
  assert(sequence.rows.at(-1).timestamp_epoch > sequence.rows[0].timestamp_epoch || sequence.leg_id === "HUR");
}

assert.strictEqual(big.valid_raw_book_receipts, 13541);
assert.strictEqual(big.ask_episode_count, 26);
assert.strictEqual(big.minimum_best_ask_entire_window_cents, 55);
assert.strictEqual(big.minimum_best_ask_before_or_at_action_cents, 55);
assert.strictEqual(big.minimum_best_ask_strictly_after_action_cents, 55);
assert.strictEqual(big.ask_ever_below_55, false);
assert.strictEqual(big.ask_ever_below_action_x, false);
assert.strictEqual(big.action_episode.ask_cents, 55);
assert.strictEqual(big.action_episode.start_receipt.endsWith("#row-1404"), true);
assert.strictEqual(big.action_episode.end_receipt_inclusive.endsWith("#row-1867"), true);
assert.strictEqual(big.action_episode.observed_receipt_span_seconds, 14807);
assert.strictEqual(big.action_episode.state_interval_seconds_until_next_change, 14815);
assert.strictEqual(big.action_episode.receipt_count, 464);
assert.strictEqual(big.participant_identity_available, false);
assert.strictEqual(big.seller_count_at_55_establishable, false);

process.stdout.write(JSON.stringify({ status: "PASS", assertions: 39, fill_rows: 4, exact_sequence_rows: sequences.sequences.reduce((sum, row) => sum + row.rows.length, 0), big_book_rows: big.valid_raw_book_receipts, big_ask_episodes: big.ask_episode_count }) + "\n");
