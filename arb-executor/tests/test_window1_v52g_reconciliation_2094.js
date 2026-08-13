#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const out = path.join(repo, ".claude/window1_live_v4_replay/v52g_reconciliation_2094_and_flip_traces_20260813");
const read = (name) => JSON.parse(fs.readFileSync(path.join(out, name)));
const rows = (name) => zlib.gunzipSync(fs.readFileSync(path.join(out, name))).toString().trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);

const summary = read("RECONCILIATION_SUMMARY.json");
assert.equal(summary.source_reported_moments, 2094);
assert.equal(summary.independently_materialized_moments, 2093);
assert.equal(summary.unexplained_source_residue, 1);
assert.equal(summary.source_anomaly_already_terminal, 2093);
assert.equal(summary.crediting_defects, 0);
assert.equal(summary.corrected_four_state_census_emitted, false);
assert.equal(summary.corrected_capture_emitted, false);
assert.equal(summary.stop_for_operator_review, true);
assert.equal(summary.conservation.pass, true);

const materialized = rows("RECONCILIATION_2093_MATERIALIZED_MOMENTS.jsonl.gz");
assert.equal(materialized.length, 2093);
assert.equal(new Set(materialized.map((row) => row.source_anomaly_identity)).size, 2093);
assert(materialized.every((row) => row.runner_actual_state_at_exact_print_receipt === "ALREADY_TERMINAL"));
assert(materialized.every((row) => row.verdict === "EXPORT_GRAIN_ILLUSION"));
assert(materialized.every((row) => row.runner_fill.fill_timestamp_epoch <= row.print.timestamp_epoch));

const flipSummary = read("V52F_V52G_FLIP_SUMMARY.json");
assert.deepEqual(flipSummary.event_ids, ["KXWTAMATCH-26JUL13CRIJEA", "KXWTAMATCH-26JUL19BRAVON"]);
assert.equal(flipSummary.baseline_complete_at_delta, 2);
assert.equal(flipSummary.candidate_complete_at_delta, 0);
assert.equal(flipSummary.baseline_candidate_delta, -2);
assert.equal(flipSummary.rows_only, true);
const flipRows = rows("V52F_V52G_FLIP_TRACES_ROWS_ONLY.jsonl.gz");
assert(flipRows.some((row) => row.row_type === "V52F_DECISION_TRACE_AT_DIVERGENCE"));
assert(flipRows.some((row) => row.row_type === "V52G_DECISION_TRACE_AT_DIVERGENCE"));
assert(flipRows.some((row) => row.row_type === "CLAUSE_6_DECISION_DIFFERENTIAL"));
assert(flipRows.some((row) => row.row_type === "V52G_PAIR_BUDGET_TIME_SERIES"));
assert(flipRows.some((row) => row.row_type === "FORWARD_TRUTH_PRINT"));
assert(flipRows.some((row) => row.row_type === "TERMINAL_FOUR_STATE_OBSERVATION"));

const determinism = read("DETERMINISM_RECEIPT.json");
assert.equal(determinism.clean_builds, 2);
assert.equal(determinism.byte_identical, true);
assert.deepEqual(determinism.mismatches, []);
const forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
for (const key of ["sealed", "holdout", "deployment", "live", "network", "orders", "positions", "exits", "settlement", "DCA", "policy_edits", "policy_replay"]) assert.equal(forbidden[key], false, key);
assert.equal(forbidden.scorer_invocations, 0);

process.stdout.write("window1 v52g reconciliation 2094: 35 assertions passed\n");
