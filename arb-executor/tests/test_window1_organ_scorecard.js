#!/usr/bin/env node
"use strict";

const assert = require("assert");
const child = require("child_process");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(__dirname, "../..");
const result = child.spawnSync(
  process.execPath,
  ["arb-executor/analysis/build_window1_organ_scorecard.js", ".", "--check"],
  { cwd: repo, encoding: "utf8" }
);
assert.strictEqual(result.status, 0, result.stderr || result.stdout);
const check = JSON.parse(result.stdout);
assert.strictEqual(check.status, "CHECK_PASS");
assert.strictEqual(check.D, 804);
assert.strictEqual(check.opportunity, 598);
assert.strictEqual(check.frozen_PC, 23);
assert.strictEqual(check.organ_pen, null);
assert.strictEqual(check.retained_execution_changes, 0);

const dir = path.join(repo, ".claude/window1_organ_scorecard_20260731");
const score = JSON.parse(fs.readFileSync(path.join(dir, "ORGAN_SCORECARD.json"), "utf8"));
const defects = JSON.parse(fs.readFileSync(path.join(dir, "DEFECT_LEDGER.json"), "utf8"));
const exact = JSON.parse(fs.readFileSync(path.join(dir, "EXACT_START_VALIDATION.json"), "utf8"));

assert.strictEqual(score.law.D, 804);
assert.strictEqual(score.headline.maker_opportunity_PC, 598);
assert.strictEqual(score.headline.frozen_JOIN_PC, 23);
assert.strictEqual(score.headline.missed_PC_opportunities, 575);
assert.strictEqual(score.authority_ruling.pen_awarded_to, null);
assert.strictEqual(score.authority_ruling.one_authority_chokepoint_armed, false);
assert(score.organ_rows.every((r) => r.signing_authority === false));

assert.strictEqual(defects.retained_changes.length, 0);
assert.strictEqual(defects.defects[0].measured_cost.missed, 575);
assert(defects.defects.some((d) => d.defect === "filled_leg_disables_entry_review"));
assert(defects.forbidden_interpretations.includes("post-fill lower prices authorize a re-buy"));

assert.strictEqual(exact.event_count, 5);
assert.deepStrictEqual(exact.negative_pair_completions.length, 1);
assert(exact.negative_pair_completions[0].includes("NIKVRB|JOIN"));

const liveHash = child.execFileSync("git", ["hash-object", "arb-executor/live_v4.py"], { cwd: repo, encoding: "utf8" }).trim();
assert.strictEqual(liveHash, "01534495161a9f8f53477794a9e30d4483ebe39f");

process.stdout.write("PASS test_window1_organ_scorecard (20 assertions; no scorer/live execution)\n");
