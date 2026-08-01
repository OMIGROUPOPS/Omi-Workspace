#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const { evaluateMicroPositionEvidence } = require("../analysis/window1_quote_shape_micro_position_v2.js");

const siblingDown = { independent_direction: "DOWN", last: { ask_change_after_first_timestamp: true, prefix: { ask_net: -2 } } };
const stableLeg = { resolved_direction: "UP", last: { ask_change_after_first_timestamp: false, strictly_later_same_price_ask_receipt: true, ask_dwell_seconds: 10, top_ask_size: 1 } };
const stable = evaluateMicroPositionEvidence({ leg: stableLeg, sibling: siblingDown, dwellSeconds: 10 });
assert.strictEqual(stable.own_micro_position_observed, true);
assert.strictEqual(stable.evidence_type, "STRICTLY_LATER_SAME_PRICE_ASK_RECEIPT");
assert.strictEqual(stable.stable_same_price_receipt, true);
assert.strictEqual(stable.inverse_sibling_resolved, true);

const firstReceipt = evaluateMicroPositionEvidence({ leg: { ...stableLeg, last: { ...stableLeg.last, strictly_later_same_price_ask_receipt: false } }, sibling: siblingDown, dwellSeconds: 10 });
assert.strictEqual(firstReceipt.own_micro_position_observed, false);
const noDwell = evaluateMicroPositionEvidence({ leg: { ...stableLeg, last: { ...stableLeg.last, ask_dwell_seconds: 9 } }, sibling: siblingDown, dwellSeconds: 10 });
assert.strictEqual(noDwell.own_micro_position_observed, false);
const noCapacity = evaluateMicroPositionEvidence({ leg: { ...stableLeg, last: { ...stableLeg.last, top_ask_size: 0 } }, sibling: siblingDown, dwellSeconds: 10 });
assert.strictEqual(noCapacity.own_micro_position_observed, false);
const wrongSibling = evaluateMicroPositionEvidence({ leg: stableLeg, sibling: { ...siblingDown, independent_direction: "UP" }, dwellSeconds: 10 });
assert.strictEqual(wrongSibling.own_micro_position_observed, true);
assert.strictEqual(wrongSibling.inverse_sibling_resolved, false);

const repo = path.resolve(__dirname, "../..");
const out = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_stable_ask_20260731");
const replay = JSON.parse(fs.readFileSync(path.join(out, "FIVE_GAME_REPLAY.json")));
const summary = JSON.parse(fs.readFileSync(path.join(out, "FIVE_GAME_SUMMARY.json")));
const transition = JSON.parse(fs.readFileSync(path.join(out, "STABLE_SAME_PRICE_TRANSITION_RECEIPT.json")));
const v1Identity = JSON.parse(fs.readFileSync(path.join(out, "V1_BYTE_IDENTITY_RECEIPT.json")));
const library = JSON.parse(fs.readFileSync(path.join(out, "QUOTE_SHAPE_LIBRARY_LEAVE_FIVE_OUT.json")));
const event = (id) => summary.events.find((row) => row.event_id === id);
const leg = (eventId, legId) => event(eventId).legs.find((row) => row.leg_id === legId);

assert.strictEqual(replay.cold, true);
assert.strictEqual(replay.score_free, true);
assert.strictEqual(replay.outcome_knowledge_consumed, false);
assert.strictEqual(summary.population_804_run, false);
assert.strictEqual(summary.event_count, 5);
assert.strictEqual(replay.events.length, 5);
assert.deepStrictEqual(library.excluded_cold_test_events, summary.library_training_exclusions);
assert.strictEqual(library.excluded_cold_test_events.length, 5);
assert.strictEqual(leg("KXATPCHALLENGERMATCH-26JUL19NIKVRB", "VRB").entry_cents, 68);
assert.strictEqual(leg("KXATPCHALLENGERMATCH-26JUL19NIKVRB", "NIK").entry_cents, 18);
assert.strictEqual(leg("KXATPCHALLENGERMATCH-26JUL19HURBIG", "HUR").entry_cents, 38);
assert.strictEqual(leg("KXATPCHALLENGERMATCH-26JUL19HURBIG", "BIG").entry_cents, 55);
assert.strictEqual(event("KXATPCHALLENGERMATCH-26JUL19HURBIG").completed_pair, true);
assert.strictEqual(event("KXATPCHALLENGERMATCH-26JUL19HURBIG").combined_entry_cents, 93);
assert.strictEqual(event("KXATPCHALLENGERMATCH-26JUL19HURBIG").combined_own_window1_close_cents, 102);
assert.strictEqual(event("KXATPCHALLENGERMATCH-26JUL19HURBIG").combined_delta_to_own_window1_closes_cents, -9);
assert.strictEqual(leg("KXATPCHALLENGERMATCH-26JUL19HURBIG", "BIG").stable_same_price_rule_fired, true);
assert.strictEqual(transition.stable_same_price_placements.some((row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL19HURBIG" && row.leg_id === "BIG" && row.price_cents === 55), true);
assert.strictEqual(transition.strict_fill_chronology_violations.length, 0);
assert.strictEqual(v1Identity.default_v1_semantics_unchanged, true);
assert.strictEqual(v1Identity.files.length, 3);
assert.strictEqual(v1Identity.files.every((row) => row.byte_identical), true);
for (const replayEvent of summary.events) for (const replayLeg of replayEvent.legs) {
  assert.strictEqual(replayLeg.pair_reference_cents, "NOT_BOUND");
  assert.strictEqual(replayLeg.delta_to_pair_reference_cents, "NOT_BOUND");
  if (!replayLeg.fill) continue;
  assert.strictEqual(replayLeg.fill.quantity, 5);
  assert.strictEqual(replayLeg.fill.evidence_ts > replayLeg.placement.action_ts, true);
  assert.notStrictEqual(replayLeg.fill.evidence_receipt, replayLeg.placement.own_book_receipt_at_action);
}
assert.strictEqual(fs.existsSync(path.join(out, "POPULATION_804_RESULTS.json")), false);

process.stdout.write("PASS test_window1_quote_shape_stable_ask_v2 (37 static assertions plus per-fill invariants; synthetic seam + five cold games; no scorer/804)\n");
