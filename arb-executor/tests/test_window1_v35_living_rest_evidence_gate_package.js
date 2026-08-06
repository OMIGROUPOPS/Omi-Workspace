"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const ROOT = path.resolve(__dirname, "..", "..");
const OUT = path.join(ROOT, ".claude/window1_live_v4_replay/v35_living_rest_evidence_gate_20260806");
const read = (name) => JSON.parse(fs.readFileSync(path.join(OUT, name), "utf8"));
const rows = (name) => zlib.gunzipSync(fs.readFileSync(path.join(OUT, name))).toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);

const control = read("CONTROL_BINDING.json");
const score = read("SCORECARD_TWO_COLUMN.json");
const edge = read("HARD_RIGHT_EDGE_RECEIPT.json");
const rest = read("REST_SANITY.json");
const bleed = read("BLEED_CENSUS_DELTA.json");
const named = read("NAMED_REGRESSION_RECEIPT.json");
const diff = read("DIFFERENTIAL_VS_V34_W1.json");
const close = read("CLOSE_TELEMETRY_ISOLATION_RECEIPT.json");
const forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
const determinism = read("DETERMINISM_RECEIPT.json");
const parts = read("FULL_DECISION_TRACE_PARTS.json");
const actionParts = read("ACTION_AND_FILL_TRACE_PARTS.json");

assert.strictEqual(control.machine.V34_W1_baseline_commit, "e56d79a2aee1f392b3bee5a0adad099c7f011976");
assert.strictEqual(control.machine.clock_decision_inputs.length, 0);
assert.strictEqual(score.STRICT_LAW.aggregate.D, 804);
assert.strictEqual(score.CENSUS_PRICED.aggregate.D, 804);
assert.strictEqual(score.STRICT_LAW.aggregate.close_based_grade, null);
assert.strictEqual(score.CENSUS_PRICED.aggregate.close_based_grade, null);
assert.strictEqual(edge.post_edge_action_or_fill_or_cap_arm_rows, 0);
assert.strictEqual(edge.post_edge_state_update_rows, 0);
assert.strictEqual(rest.STRICT_LAW.aggregate.non_exact_target_receipts, 0);
assert.strictEqual(rest.CENSUS_PRICED.aggregate.non_exact_target_receipts, 0);
assert.strictEqual(rest.STRICT_LAW.aggregate.max_abs_gap_cents, 0);
assert.strictEqual(bleed.STRICT_LAW.conservation.pass, true);
assert.strictEqual(bleed.CENSUS_PRICED.conservation.pass, true);
assert.strictEqual(named.NO_FIRST_FLICKER_OVERPAY["KXATPCHALLENGERMATCH-26JUL12KRALOR|LOR"].prohibited_taker_count, 0);
assert.strictEqual(named.NO_FIRST_FLICKER_OVERPAY["KXATPCHALLENGERMATCH-26JUL12ARNROM|ROM"].prohibited_taker_count, 0);
assert.strictEqual(named.NO_FIRST_FLICKER_OVERPAY["KXATPCHALLENGERMATCH-26JUL12BOSCOP|BOS"].prohibited_taker_count_while_downward_evidence_live, 0);
assert.strictEqual(diff.STRICT_LAW.conservation.pass, true);
assert.strictEqual(diff.CENSUS_PRICED.conservation.pass, true);
assert.strictEqual(close.strict_invariant, true);
assert.strictEqual(close.census_invariant, true);
assert.strictEqual(forbidden.holdout_accesses, 0);
assert.strictEqual(forbidden.live_accesses, 0);
assert.strictEqual(forbidden.network_runtime_accesses, 0);
assert.strictEqual(rows("STRICT_EVENT_LEDGER.jsonl.gz").length, 804);
assert.strictEqual(rows("CENSUS_PRICED_EVENT_LEDGER.jsonl.gz").length, 804);
assert.strictEqual(determinism.builds, 2);
assert.strictEqual(determinism.byte_identical, true);
assert(parts.parts.length >= 2);
assert(parts.parts.every((row) => row.bytes <= parts.max_part_bytes));
assert(actionParts.parts.length >= 1);
assert(actionParts.parts.every((row) => row.bytes <= actionParts.max_part_bytes));

console.log("PASS test_window1_v35_living_rest_evidence_gate_package");
