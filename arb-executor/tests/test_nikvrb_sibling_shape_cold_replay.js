#!/usr/bin/env node
"use strict";

const assert = require("assert");
const child = require("child_process");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const repo = path.resolve(__dirname, "../..");
const run = child.spawnSync(
  process.execPath,
  ["arb-executor/analysis/build_nikvrb_sibling_shape_reference.js", ".", "--check"],
  { cwd: repo, encoding: "utf8" }
);
assert.strictEqual(run.status, 0, run.stderr || run.stdout);
const build = JSON.parse(run.stdout);
assert.strictEqual(build.status, "CHECK_PASS");
assert.strictEqual(build.source_rows, 13123);
assert.strictEqual(build.ledger_rows, 13123);
assert.deepStrictEqual(build.current, { NIK: 21, VRB: 69 });
assert.deepStrictEqual(build.tuned, { NIK: 19, VRB: 69, combined_delta: -14 });
assert.strictEqual(build.population_run, false);
assert.strictEqual(build.live_v4_modified, false);

const dir = path.join(
  repo,
  ".claude/window1_live_v4_replay/nikvrb_sibling_shape_tune_20260731"
);
const readJson = (name) => JSON.parse(fs.readFileSync(path.join(dir, name), "utf8"));
const summary = readJson("NIKVRB_REPLAY_SUMMARY.json");
const decisions = readJson("NIKVRB_MATERIAL_DECISIONS.json");
const currentOrders = readJson("NIKVRB_CURRENT_ORDER_INTERVALS.json");
const tunedOrders = readJson("NIKVRB_TUNED_ORDER_INTERVALS.json");
const nondecisions = readJson("NIKVRB_NONDECISION_CENSUS.json");
const visual = readJson("NIKVRB_VISUAL_ACCEPTANCE.json");

assert.strictEqual(summary.current_outcome.individual_delta_to_close_cents.NIK, 2);
assert.strictEqual(summary.current_outcome.individual_delta_to_close_cents.VRB, -14);
assert.strictEqual(summary.tuned_outcome.individual_delta_to_close_cents.NIK, 0);
assert.strictEqual(summary.tuned_outcome.individual_delta_to_close_cents.VRB, -14);
assert.strictEqual(summary.tuned_outcome.gap_to_own_fillable_low_cents.NIK, 1);
assert.strictEqual(summary.tuned_outcome.gap_to_own_fillable_low_cents.VRB, -1);

const arm = decisions.find((row) => row.action === "CANCEL_NIK_21__WAIT");
const release = decisions.find((row) => row.action === "PLACE_NIK_19");
const nikFill = decisions.find((row) => row.action === "CREDIT_NIK_FILL_19");
const vrbFill = decisions.find((row) => row.action === "CREDIT_VRB_FILL_69");
assert.ok(arm && release && nikFill && vrbFill);
assert.strictEqual(arm.timestamp_et, "2026-07-19T10:30:39.000000-04:00");
assert.strictEqual(arm.joint_observation.NIK.bid, 24);
assert.strictEqual(arm.joint_observation.VRB.bid, 73);
assert.strictEqual(arm.organ_returns.sibling_completed_quote_recurrences, 97);
assert.strictEqual(release.timestamp_et, "2026-07-19T10:40:57.000000-04:00");
assert.strictEqual(release.organ_returns.bid_drop, 5);
assert.strictEqual(release.signer, "LIVE_NIK_BID");
assert.strictEqual(nikFill.signer, "PRICE_REACHED");
assert.strictEqual(vrbFill.signer, "STRICT_ASK_CERTAIN_FILL");

const tuned21 = tunedOrders.find((row) => row.leg === "NIK" && row.price === 21);
const tuned19 = tunedOrders.find((row) => row.leg === "NIK" && row.price === 19);
const current21 = currentOrders.find((row) => row.leg === "NIK" && row.price === 21);
assert.strictEqual(tuned21.end_reason, "SIBLING_RISER_SHAPE_RESOLVED");
assert.strictEqual(tuned19.action_et, "2026-07-19T10:40:57.000000-04:00");
assert.strictEqual(tuned19.end_reason, "FILLED_PRICE_REACHED");
assert.strictEqual(current21.end_reason, "FILLED_PRICE_REACHED");
assert.ok(tuned19.end_epoch > tuned19.action_epoch);
assert.ok(tuned19.end_sequence > tuned19.action_sequence);

const ledgerText = zlib.gunzipSync(Buffer.from(
  fs.readFileSync(path.join(dir, "NIKVRB_DECISION_PROCESS_ENGLISH.jsonl.gz.b64"), "utf8").trim(),
  "base64"
)).toString("utf8").trim();
const ledger = ledgerText.split("\n").map(JSON.parse);
assert.strictEqual(ledger.length, 13123);
assert.strictEqual(ledger[0].sequence, 1);
assert.strictEqual(ledger[ledger.length - 1].sequence, 13123);
assert.strictEqual(
  ledger.find((row) => row.timestamp_et === "2026-07-19T11:32:31.000000-04:00").action,
  "NO_CALL__PAIR_ENTRY_COMPLETE"
);
assert.strictEqual(nondecisions.first_NIK_ask_18.tuned_state.includes("already filled 19"), true);
assert.strictEqual(visual.current_orientation_branch.fills.NIK.price, 21);
assert.strictEqual(visual.corrected_sibling_shape_branch.fills.NIK.price, 19);
assert.strictEqual(
  visual.corrected_sibling_shape_branch.orders.find((row) => row.leg === "NIK" && row.price === 19).start_tminus_scheduled,
  "T-109.050"
);

const liveBlob = child.execFileSync(
  "git", ["hash-object", "arb-executor/live_v4.py"], { cwd: repo, encoding: "utf8" }
).trim();
assert.strictEqual(liveBlob, "01534495161a9f8f53477794a9e30d4483ebe39f");

process.stdout.write("PASS test_nikvrb_sibling_shape_cold_replay (46 assertions; one cold game; no population/live execution)\n");
