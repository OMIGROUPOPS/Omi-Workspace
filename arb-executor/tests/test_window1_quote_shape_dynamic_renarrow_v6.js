"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(__dirname, "../..");
const root = path.join(repo, ".claude/window1_live_v4_replay/five_exact_dynamic_renarrow_v6_20260801");
const library = JSON.parse(fs.readFileSync(path.join(root, "QUOTE_SHAPE_LIBRARY_DYNAMIC_RENARROW_V6.json")));
const replay = JSON.parse(fs.readFileSync(path.join(root, "FIVE_GAME_DYNAMIC_RENARROW_V6_REPLAY.json")));
const gate = JSON.parse(fs.readFileSync(path.join(root, "FIVE_GAME_HONEST_GATE.json")));

assert.strictEqual(library.training_events, 681);
assert.strictEqual(library.training_legs, 1343);
assert.strictEqual(Object.keys(library.groups).length, 16);
assert.strictEqual(Object.values(library.groups).reduce((sum, group) => sum + group.shapes.length, 0), 94);
assert.strictEqual(replay.schema_version, "WINDOW1_QUOTE_SHAPE_DYNAMIC_RENARROW_REPLAY_V6");
assert.strictEqual(replay.cold, true);
assert.strictEqual(replay.outcome_knowledge_consumed, false);

const replayLegs = new Map(replay.events.flatMap((event) => Object.entries(event.legs).map(([leg, row]) => [`${event.event_id}|${leg}`, row])));
const entries = {
  "KXATPCHALLENGERMATCH-26JUL19HURBIG|BIG": 55,
  "KXATPCHALLENGERMATCH-26JUL19HURBIG|HUR": 38,
  "KXATPCHALLENGERMATCH-26JUL19NIKVRB|NIK": 18,
  "KXATPCHALLENGERMATCH-26JUL19NIKVRB|VRB": 68,
  "KXATPMATCH-26JUL12LAJVAN|LAJ": 45,
  "KXATPMATCH-26JUL12LAJVAN|VAN": 50,
  "KXWTACHALLENGERMATCH-26JUL16BRAVED|BRA": 40,
  "KXWTACHALLENGERMATCH-26JUL16BRAVED|VED": 57,
  "KXWTAMATCH-26JUL20KORJIM|JIM": 31,
  "KXWTAMATCH-26JUL20KORJIM|KOR": 60,
};
for (const [identity, entry] of Object.entries(entries)) assert.strictEqual(replayLegs.get(identity).entry_cents, entry, identity);

const laj = replayLegs.get("KXATPMATCH-26JUL12LAJVAN|LAJ");
assert(laj.macro_reclassifications.some((row) => row.eliminated_stale_shapes.includes("ATP_MAIN_26_50_FLAT_UNMOVED") && row.re_narrowed_shapes.includes("ATP_MAIN_26_50_DOWN_REBOUND")));
const ved = replayLegs.get("KXWTACHALLENGERMATCH-26JUL16BRAVED|VED");
assert(ved.macro_reclassifications.some((row) => row.eliminated_stale_shapes.includes("WTA_CHALL_51_75_UP_CONTINUATION") && row.re_narrowed_shapes.includes("WTA_CHALL_51_75_DOWN_REBOUND")));
const jim = replayLegs.get("KXWTAMATCH-26JUL20KORJIM|JIM");
assert(jim.macro_reclassifications.some((row) => row.eliminated_stale_shapes.includes("WTA_MAIN_26_50_FLAT_UNMOVED")));
assert(jim.macro_reclassifications.length >= 2);
assert.strictEqual(jim.surviving_shapes_at_placement[0].shape_id, "WTA_MAIN_26_50_DOWN_CONTINUATION");
const bra = replayLegs.get("KXWTACHALLENGERMATCH-26JUL16BRAVED|BRA");
assert.strictEqual(bra.surviving_shapes_at_placement[0].temporal_authority, "CAUSALLY_NEAREST_ZERO_DESCENT_MEMBER");
assert.deepStrictEqual(bra.surviving_shapes_at_placement[0].selected_member_remaining_min_deltas, [0]);
assert(replay.events.find((event) => event.event_id.endsWith("KORJIM")).pair_constraint.dynamic_current_path_inverse_closures.length > 0);

assert.deepStrictEqual(gate.honest_fill_class_counts, { PROVEN_MAKER: 0, PROVEN_TAKER: 10, UNPROVEN: 0 });
assert.strictEqual(gate.honest_completed_pair_count, 5);
assert.strictEqual(gate.objective_gate_pass_count, 3);
assert.strictEqual(gate.five_game_gate_passed, false);
assert.strictEqual(gate.population_804_authorized_by_gate, false);
assert.strictEqual(gate.population_804_run, false);
for (const event of gate.events) for (const leg of event.legs) {
  assert.strictEqual(leg.pair_reference_cents, "NOT_BOUND");
  assert.strictEqual(leg.delta_to_pair_reference_cents, "NOT_BOUND");
  assert.strictEqual(leg.honest_fill_class, "PROVEN_TAKER");
}

console.log("PASS test_window1_quote_shape_dynamic_renarrow_v6 (five-game gate remains closed; no 804 run)");
