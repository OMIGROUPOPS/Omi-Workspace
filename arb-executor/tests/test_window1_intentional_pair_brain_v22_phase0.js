#!/usr/bin/env node
"use strict";

const assert = require("assert");
const child = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const repo = path.resolve(__dirname, "../..");
const builder = path.join(repo, "arb-executor/analysis/build_window1_intentional_pair_brain_v22_phase0.js");
const packageDir = path.join(repo, ".claude/window1_live_v4_replay/intentional_pair_brain_v22_phase0_20260804");
const load = (name) => JSON.parse(fs.readFileSync(path.join(packageDir, name), "utf8"));

const ruler = load("PHASE0_CLOSE_RULER_RECEIPT.json");
assert.equal(ruler.status, "STRAIGHT");
assert.equal(ruler.completed_A_variant_pairs, 471);
assert.equal(ruler.completed_A_variant_legs, 942);
assert.equal(ruler.frozen_reference_matches, 942);
assert.equal(ruler.mismatches, 0);
assert.equal(ruler.available_close_legs + ruler.unavailable_or_ambiguous_close_legs, 942);

const failures = load("PHASE0_BOTH_BELOW_CLOSE_FAIL_PAR.json");
assert.equal(failures.prompt_expected_count, 15);
assert.equal(failures.arithmetic_expected_count, 25);
assert.equal(failures.observed_event_count, 25);
assert.equal(failures.events.length, 25);
assert(failures.events.every((row) => row.both_legs_strictly_below_close && !row.pair_under_par));

const cap = load("PHASE0_PAIR_CAP_SOURCE_AUDIT.json");
assert.equal(cap.result, "PAIR CAP: ABSENT");
assert(cap.placement_source.line > 0);
assert.equal(cap.placement_source.sibling_fill_consumed, false);
assert.deepEqual(cap.matching_executable_paths, []);

const blocker = load("V22_CAUSAL_BLOCKER_RECEIPT.json");
assert.equal(blocker.status, "BLOCKED_BEFORE_PHASE_1");
assert.equal(blocker.V22_replay_executed, false);
assert.equal(blocker.V22_score_emitted, false);
assert.deepEqual(new Set(blocker.blockers.map((row) => row.input)), new Set(["OWN_CLOSE_ESTIMATE_AT_DECISION_TIME", "OWN_MAKER_FLOOR_AT_FIRST_SHAPE_PAIR_RESOLUTION"]));

const one = fs.mkdtempSync(path.join(os.tmpdir(), "w1-v22-one-"));
const two = fs.mkdtempSync(path.join(os.tmpdir(), "w1-v22-two-"));
try {
  for (const target of [one, two]) child.execFileSync("node", [builder, "--repo", repo, "--output", target], { cwd: repo, stdio: "pipe" });
  const namesOne = fs.readdirSync(one).sort();
  const namesTwo = fs.readdirSync(two).sort();
  assert.deepEqual(namesOne, namesTwo);
  for (const name of namesOne) assert(fs.readFileSync(path.join(one, name)).equals(fs.readFileSync(path.join(two, name))), `non-deterministic ${name}`);
} finally {
  fs.rmSync(one, { recursive: true, force: true });
  fs.rmSync(two, { recursive: true, force: true });
}

process.stdout.write("window1 V22 phase0: 5 checks passed\n");
