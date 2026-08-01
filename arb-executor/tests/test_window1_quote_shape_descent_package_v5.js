"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/five_exact_descent_verdict_v5_20260801");
const distribution = JSON.parse(fs.readFileSync(path.join(root, "DESCENT_TO_FINAL_REACHABLE_LOW_DISTRIBUTIONS.json")));
const gate = JSON.parse(fs.readFileSync(path.join(root, "FIVE_GAME_HONEST_GATE.json")));
const replay = JSON.parse(fs.readFileSync(path.join(root, "FIVE_GAME_DESCENT_VERDICT_V5_REPLAY.json")));

assert.strictEqual(distribution.training_events, 681);
assert.strictEqual(distribution.training_legs, 1343);
assert.strictEqual(distribution.group_count, 16);
assert.strictEqual(distribution.shape_count, 94);
assert.strictEqual(distribution.excluded_events.length, 5);
assert.deepStrictEqual(distribution.invented_numeric_thresholds, []);
for (const cell of distribution.cells) {
  assert.strictEqual(cell.distribution.support_n + cell.distribution.censored_n, cell.shape_members);
  assert.strictEqual(Object.values(cell.distribution.counts).reduce((sum, n) => sum + n, 0), cell.distribution.support_n);
}
const byLeg = new Map(gate.events.flatMap((event) => event.legs.map((leg) => [`${event.event_id}|${leg.leg_id}`, leg])));
assert.strictEqual(byLeg.get("KXATPCHALLENGERMATCH-26JUL19HURBIG|BIG").proposed_entry_cents, 55);
assert.strictEqual(byLeg.get("KXATPCHALLENGERMATCH-26JUL19HURBIG|HUR").proposed_entry_cents, 38);
assert.strictEqual(byLeg.get("KXATPCHALLENGERMATCH-26JUL19NIKVRB|NIK").proposed_entry_cents, 18);
assert.strictEqual(byLeg.get("KXATPCHALLENGERMATCH-26JUL19NIKVRB|VRB").proposed_entry_cents, 68);
assert.strictEqual(byLeg.get("KXATPMATCH-26JUL12LAJVAN|LAJ").proposed_entry_cents, null);
assert.strictEqual(byLeg.get("KXWTACHALLENGERMATCH-26JUL16BRAVED|VED").proposed_entry_cents, null);
assert.strictEqual(byLeg.get("KXWTAMATCH-26JUL20KORJIM|JIM").proposed_entry_cents, null);
assert.strictEqual(gate.five_game_gate_passed, false);
assert.strictEqual(gate.population_804_run, false);
assert.strictEqual(replay.outcome_knowledge_consumed, false);

console.log("PASS test_window1_quote_shape_descent_package_v5");
