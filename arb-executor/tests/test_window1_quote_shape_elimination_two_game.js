#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(__dirname, "../..");
const dir = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_elimination_20260731");
const library = JSON.parse(fs.readFileSync(path.join(dir, "QUOTE_SHAPE_LIBRARY.json")));
const replay = JSON.parse(fs.readFileSync(path.join(dir, "TWO_GAME_REPLAY.json")));

assert.strictEqual(replay.score_free, true);
assert.strictEqual(replay.cold, true);
assert.strictEqual(replay.outcome_knowledge_consumed, false);
assert.deepStrictEqual(replay.events.map((row) => row.event_id).sort(), [
  "KXATPCHALLENGERMATCH-26JUL19HURBIG",
  "KXATPCHALLENGERMATCH-26JUL19NIKVRB",
]);
assert.deepStrictEqual(library.excluded_cold_test_events, replay.events.map((row) => row.event_id).sort());
assert.strictEqual(library.feature_contract.no_print_shape_dependency, true);
assert.ok(library.feature_contract.full_path.includes("median_ask_episode_dwell"));
assert.ok(library.feature_contract.full_path.includes("mean_spread"));
assert.ok(library.feature_contract.full_path.includes("quote_rate"));
assert.ok(library.feature_contract.full_path.includes("mean_log_top_ask_size"));
assert.ok(library.feature_contract.full_path.includes("mean_log_top5_ask_depth"));

const byEvent = Object.fromEntries(replay.events.map((row) => [row.event_id, row]));
const nikvrb = byEvent.KXATPCHALLENGERMATCH_26JUL19NIKVRB || byEvent["KXATPCHALLENGERMATCH-26JUL19NIKVRB"];
const hurbig = byEvent.KXATPCHALLENGERMATCH_26JUL19HURBIG || byEvent["KXATPCHALLENGERMATCH-26JUL19HURBIG"];

assert.strictEqual(nikvrb.legs.VRB.entry_cents, 68);
assert.strictEqual(nikvrb.legs.VRB.own_ask_reachable_low_cents, 68);
assert.strictEqual(nikvrb.legs.NIK.entry_cents, 18);
assert.strictEqual(nikvrb.legs.NIK.own_ask_reachable_low_cents, 18);
assert.strictEqual(hurbig.legs.HUR.entry_cents <= 41, true);
assert.notStrictEqual(hurbig.legs.HUR.entry_cents, 47);
assert.strictEqual(hurbig.legs.BIG.status, "INSUFFICIENT_EVIDENCE");
assert.strictEqual(hurbig.legs.BIG.entry_cents, null);

for (const event of replay.events) {
  assert.strictEqual(event.pair_constraint.identity, "two outcomes sum to 100");
  for (const leg of Object.values(event.legs)) {
    assert.strictEqual(leg.pair_reference_cents, "NOT_BOUND");
    assert.strictEqual(leg.delta_to_pair_reference_cents, "NOT_BOUND");
    if (!leg.fill) continue;
    assert.strictEqual(leg.fill.quantity, 5);
    assert.strictEqual(leg.fill.evidence_ts > leg.placement.action_ts, true);
    assert.strictEqual(leg.fill.ask_dwell_seconds >= 10, true);
    assert.strictEqual(leg.fill.capacity >= 5, true);
    assert.strictEqual(leg.placement.same_receipt_fill_forbidden, true);
    assert.ok(leg.surviving_shapes_at_placement.length > 0);
  }
}

assert.strictEqual(hurbig.legs.BIG.decision_changes.some((row) => row.reason === "FLOOR_CONSENSUS_BUT_OWN_MICRO_POSITION_UNOBSERVED"), true);
assert.strictEqual(nikvrb.legs.VRB.decision_changes.some((row) => row.state === "INSUFFICIENT_EVIDENCE"), true);
assert.strictEqual(nikvrb.legs.NIK.decision_changes.some((row) => row.state === "HOLD"), true);
assert.strictEqual(hurbig.legs.HUR.decision_changes.some((row) => row.state === "HOLD"), true);

process.stdout.write("PASS test_window1_quote_shape_elimination_two_game (two cold games only; 53 assertions; no scorer/population replay)\n");
