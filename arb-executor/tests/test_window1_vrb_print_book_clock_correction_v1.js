#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/vrb_print_book_clock_correction_20260801");
const receipt = JSON.parse(fs.readFileSync(path.join(root, "PRINT_BOOK_CLOCK_RECEIPT.json")));
const intersection = JSON.parse(fs.readFileSync(path.join(root, "NINE_VISIT_PRINT_INTERSECTION.json")));

assert.strictEqual(receipt.score_free, true);
assert.strictEqual(receipt.correction.status, "TRUE_BUT_MISLEADING_SCOPE");
assert.strictEqual(receipt.print.timestamp_epoch, 1784459636.179481);
assert.strictEqual(receipt.print.price, 70);
assert.strictEqual(receipt.print.size, 0.06);
assert.strictEqual(receipt.print.taker_side, "yes");
assert.strictEqual(receipt.print.aggressor_side, "BUY");
assert.strictEqual(receipt.print.containing_67x68_visit, null);
assert.strictEqual(receipt.print.seconds_after_prior_visit_end, 93.179481);
assert.strictEqual(receipt.print.seconds_before_next_visit_start, 85.820519);
assert.deepStrictEqual([receipt.print.latest_distinct_prior_second_book.bid, receipt.print.latest_distinct_prior_second_book.ask, receipt.print.latest_distinct_prior_second_book.timestamp_epoch], [69, 70, 1784459632]);
assert.strictEqual(receipt.print.same_second_book_rows.length, 2);
assert(receipt.print.same_second_book_rows.every((row) => row.bid === 69 && row.ask === 70 && row.timestamp_epoch === 1784459636));
assert.deepStrictEqual([receipt.print.latest_book_at_or_before_print.bid, receipt.print.latest_book_at_or_before_print.ask], [69, 70]);
assert.strictEqual(receipt.print.ask_at_print_cents, 70);
assert.strictEqual(receipt.print.ask_at_print_established_despite_cross_stream_subsecond_ambiguity, true);
assert.strictEqual(receipt.conservation.visit_count, 9);
assert.strictEqual(receipt.conservation.prints_inside_visits, 0);
assert.strictEqual(receipt.conservation.all_nine_print_empty, true);
assert.strictEqual(receipt.visits.length, 9);
assert(receipt.visits.every((visit) => visit.book.bid === 67 && visit.book.ask === 68 && visit.print_count === 0 && visit.prints.length === 0));
assert.strictEqual(intersection.visits.length, 9);
assert(intersection.visits.every((visit) => visit.print_count === 0));
assert.strictEqual(receipt.clock_binding.same_epoch_basis, true);
assert.strictEqual(receipt.clock_binding.directly_comparable_across_distinct_seconds, true);
assert.strictEqual(receipt.clock_binding.authoritative_cross_stream_order_within_same_second, false);

process.stdout.write(JSON.stringify({ status: "PASS", assertions: 25, visits: 9, prints_inside_visits: 0, ask_at_print: 70 }) + "\n");
