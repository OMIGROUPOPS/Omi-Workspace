#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(__dirname, "../..");
const result = JSON.parse(fs.readFileSync(path.join(repo, ".claude/window1_live_v4_replay/fee_aware_take_census_20260801/FEE_AWARE_TAKE_CENSUS.json")));
assert.strictEqual(result.population_events, 804);
assert.strictEqual(result.capacity_proven_negative_pair_ceiling, 516);
assert.strictEqual(result.rows.length, 516);
assert.strictEqual(result.ex_post_clearing_count + result.ex_post_failing_count, 516);
assert.strictEqual(result.decision_rule_contract.expected_close_source, "NOT_BOUND");
assert.strictEqual(result.decision_rule_contract.executable_now, false);
assert.strictEqual(result.diagnostic_contract.not_a_policy_result, true);
const partitions = Object.values(result.by_category_and_price_region);
assert.strictEqual(partitions.reduce((sum, row) => sum + row.denominator_516_rows, 0), 516);
for (const row of partitions) {
  assert.strictEqual(row.ex_post_clears + row.ex_post_fails, row.denominator_516_rows);
  assert.strictEqual(row.event_ids_clearing.length, row.ex_post_clears);
  assert.strictEqual(row.event_ids_failing.length, row.ex_post_fails);
}
const nikvrb = result.rows.find((row) => row.event_id.endsWith("NIKVRB"));
const hurbig = result.rows.find((row) => row.event_id.endsWith("HURBIG"));
assert(nikvrb && hurbig);
assert.deepStrictEqual([nikvrb.ex_post_actual_close_edge_cents, nikvrb.taker_fee_five_lot_pair_cents, nikvrb.clears_operator_fee_screen], [16, 14, true]);
assert.strictEqual(hurbig.clears_operator_fee_screen, false);
assert(result.rows.every((row) => row.executable_decision_time_ruling === "EXPECTED_CLOSE_NOT_BOUND"));
process.stdout.write(`window1 fee-aware take census: ${12 + partitions.length * 3} assertions passed\n`);
