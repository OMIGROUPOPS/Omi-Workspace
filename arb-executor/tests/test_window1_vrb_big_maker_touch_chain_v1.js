#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/vrb_big_maker_touch_chain_20260801");
const receipt = JSON.parse(fs.readFileSync(path.join(root, "MAKER_TOUCH_EXECUTION_RECEIPT.json")));
const rows = (name) => zlib.gunzipSync(fs.readFileSync(path.join(root, name))).toString("utf8").trimEnd().split("\n").map(JSON.parse);
const plainRows = (name) => fs.readFileSync(path.join(root, name), "utf8").trimEnd().split("\n").map(JSON.parse);
const bid67 = rows("VRB_BID67_TICKS.jsonl.gz");
const ask68 = rows("VRB_ASK68_TICKS.jsonl.gz");
const big55 = rows("BIG_ASK55_TICKS.jsonl.gz");

assert.strictEqual(receipt.score_free, true);
assert.strictEqual(receipt.vrb.early_ask_68_episode_count, 9);
assert.strictEqual(receipt.vrb.early_67x68_episode_count, 9);
assert.strictEqual(receipt.vrb.early_67x68_state_seconds, 641);
assert.strictEqual(receipt.vrb.bid_67_episode_containing_credit.state_interval_seconds_until_next_change, 1128);
assert.strictEqual(receipt.vrb.bid_67_episode_containing_credit.receipt_count, 235);
assert.strictEqual(receipt.vrb.seconds_from_first_bid_67_to_first_ask_68, 2646);
assert.strictEqual(receipt.vrb.every_early_ask_68_tick_had_bid_67, true);
assert.strictEqual(receipt.vrb.resting_67_fill_proven_in_early_chain, false);
assert.strictEqual(receipt.vrb.true_prints_from_first_book_through_1128_episode.length, 1);
assert.strictEqual(receipt.vrb.true_prints_from_first_book_through_1128_episode[0].price, 70);
assert.strictEqual(receipt.vrb.true_prints_from_first_book_through_1128_episode[0].aggressor_side, "BUY");
assert.strictEqual(receipt.vrb.seller_aggressor_true_prints_at_or_below_67.length, 0);
assert.strictEqual(bid67.length, 443);
assert.strictEqual(ask68.length, 60);
assert(bid67.every((row) => row.bid === 67 && row.ask_at_same_tick === row.ask));
assert(ask68.every((row) => row.ask === 68 && row.bid_at_same_tick === 67));
assert(bid67.every((row) => Number.isFinite(row.t_minus_scheduled_seconds) && Number.isFinite(row.t_minus_actual_bell_seconds)));
assert(ask68.every((row) => Number.isFinite(row.t_minus_scheduled_seconds) && Number.isFinite(row.t_minus_actual_bell_seconds)));

assert.strictEqual(receipt.big.ask_55_tick_count, 464);
assert.strictEqual(receipt.big.ask_55_observed_receipt_span_seconds, 14807);
assert.strictEqual(receipt.big.ask_55_state_seconds_until_next_changed_ask_receipt, 14815);
assert.deepStrictEqual(receipt.big.bid_episodes_while_ask_55.map((row) => [row.value, row.observed_receipt_span_seconds, row.state_interval_seconds_until_next_change, row.receipt_count]), [
  [54, 3524, 3625, 101],
  [53, 8785, 8785, 180],
  [54, 2397, 2397, 178],
  [55, 0, 8, 5],
]);
assert.strictEqual(receipt.big.true_prints_while_ask_55.length, 7);
assert.strictEqual(receipt.big.true_prints_while_ask_55.filter((row) => row.price === 55).length, 5);
assert.strictEqual(receipt.big.true_prints_while_ask_55.every((row) => row.aggressor_side === "BUY"), true);
assert.strictEqual(receipt.big.seller_aggressor_true_prints_at_or_below_54.length, 0);
assert.strictEqual(receipt.big.resting_54_fill_proven, false);
assert.strictEqual(big55.length, 464);
assert(big55.every((row) => row.ask === 55 && row.spread === row.ask - row.bid));
assert.deepStrictEqual(plainRows("VRB_BID67_TICKS.jsonl"), bid67);
assert.deepStrictEqual(plainRows("VRB_ASK68_TICKS.jsonl"), ask68);
assert.deepStrictEqual(plainRows("BIG_ASK55_TICKS.jsonl"), big55);

process.stdout.write(JSON.stringify({ status: "PASS", assertions: 33, vrb_bid67_ticks: bid67.length, vrb_ask68_ticks: ask68.length, big_ask55_ticks: big55.length }) + "\n");
