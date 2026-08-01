#!/usr/bin/env node
"use strict";

const assert = require("assert");
const child = require("child_process");
const fs = require("fs");
const path = require("path");
const { capacityProvenAskFloor } = require("../analysis/build_window1_live_book_initial_aim_replay.js");

const repo = path.resolve(__dirname, "../..");
const out = path.join(repo, ".claude/window1_live_v4_replay/live_book_initial_aim_20260731");

const proof = capacityProvenAskFloor([
  { ts: 100, bid: 19, ask: 20, asks: [[20, 4], [21, 8]], source_receipt: "synthetic#1" },
  { ts: 109, bid: 18, ask: 20, asks: [[20, 4], [21, 8]], source_receipt: "synthetic#2" },
  { ts: 110, bid: 18, ask: 20, asks: [[20, 5], [21, 8]], source_receipt: "synthetic#3" },
], 110);
assert.equal(proof.limit_cents, 20);
assert.equal(proof.displayed_capacity, 5);
assert.equal(proof.dwell_seconds, 10);

const replay = JSON.parse(fs.readFileSync(path.join(out, "REPLAY_AND_REFERENCE_PANEL.json")));
assert.equal(replay.cold, true);
assert.equal(replay.outcome_knowledge_consumed, false);
const nik = replay.corrected_branch.find((row) => row.event_id.endsWith("NIKVRB"));
assert.equal(nik.legs.NIK.entry_cents, 18);
assert.equal(nik.legs.VRB.entry_cents, 68);
assert.equal(nik.legs.NIK.delta_to_pair_reference_cents, "NOT_BOUND");
assert.equal(nik.legs.NIK.change_status.live_book_initial_aim, "FIRED");
const hur = replay.corrected_branch.find((row) => row.event_id.endsWith("HURBIG"));
assert.equal(hur.legs.HUR.entry_cents, 47);
assert.equal(hur.legs.HUR.delta_to_own_window1_close_cents, 5);

const suppression = JSON.parse(fs.readFileSync(path.join(out, "INITIAL_AIM_FILL_SUPPRESSION_CENSUS.json")));
assert.equal(suppression.population_events, 804);
assert.equal(suppression.eligible_initial_aim_below_every_ask_reach_legs, 1137);
assert.equal(suppression.proven_only_exposure_below_every_ask_reach_legs, 983);
assert.equal(suppression.later_exposure_sequence_indeterminate_legs, 154);

const ceiling = JSON.parse(fs.readFileSync(path.join(out, "ASK_10S_FIVE_CONTRACT_CEILING.json")));
assert.equal(ceiling.old_ask_only_10s_negative_ceiling, 532);
assert.equal(ceiling.capacity_proven_ask_only_10s_negative_ceiling, 516);
assert.equal(ceiling.removed_by_capacity_law, 16);

const invalid = JSON.parse(fs.readFileSync(path.join(out, "LEGACY_CAPACITY_INVALIDATION_RECEIPT.json")));
assert.equal(invalid.legacy_fill_assignments, 217);
assert.equal(invalid.legacy_pair_completions, 49);
assert.equal(invalid.creditable_pair_completions_under_current_law, 0);

const forbidden = JSON.parse(fs.readFileSync(path.join(out, "FORBIDDEN_ACCESS_RECEIPT.json")));
assert.equal(forbidden.scorer_imported, false);
assert.equal(forbidden.holdout_access, false);
assert.equal(forbidden.live_access, false);

const checked = child.spawnSync(process.execPath, [path.join(repo, "arb-executor/analysis/build_window1_live_book_initial_aim_replay.js"), repo, "--check"], { cwd: repo, encoding: "utf8", timeout: 120000 });
assert.equal(checked.status, 0, checked.stderr);
assert.match(checked.stdout, /CHECK_PASS/);

console.log("window1 live-book initial-aim replay tests: PASS (18 assertions)");
