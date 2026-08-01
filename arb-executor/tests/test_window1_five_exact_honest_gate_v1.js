#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(__dirname, "../..");
const file = path.join(repo, ".claude/window1_live_v4_replay/five_exact_pair_wiring_honest_20260801/FIVE_GAME_HONEST_GATE.json");
const receipt = JSON.parse(fs.readFileSync(file));

assert.strictEqual(receipt.cold, true);
assert.strictEqual(receipt.outcome_knowledge_consumed, false);
assert.strictEqual(receipt.event_count, 5);
assert.strictEqual(receipt.leg_count, 10);
assert.strictEqual(receipt.replay_proposed_fill_count, 9);
assert.deepStrictEqual(receipt.honest_fill_class_counts, { PROVEN_MAKER: 0, PROVEN_TAKER: 7, UNPROVEN: 3 });
assert.strictEqual(receipt.honest_completed_pair_count, 2);
assert.strictEqual(receipt.objective_gate_pass_count, 1);
assert.strictEqual(receipt.five_game_gate_passed, false);
assert.strictEqual(receipt.population_804_authorized_by_gate, false);
assert.strictEqual(receipt.population_804_run, false);
assert.strictEqual(receipt.fee_test, "DROPPED_BY_OPERATOR_INSTRUCTION");
assert.strictEqual(receipt.expected_close_forecast, "DROPPED_BY_OPERATOR_INSTRUCTION");

for (const event of receipt.events) {
  assert.strictEqual(event.legs.length, 2);
  for (const leg of event.legs) {
    assert.ok(leg.category);
    assert.ok(leg.price_region);
    assert.strictEqual(leg.pair_reference_cents, "NOT_BOUND");
    assert.strictEqual(leg.delta_to_pair_reference_cents, "NOT_BOUND");
    assert.ok(Array.isArray(leg.fired_predicates) && leg.fired_predicates.length > 0);
    assert.strictEqual(leg.replay_credit_is_not_honest_evidence, true);
    if (leg.honest_fill_class === "PROVEN_TAKER") {
      assert.strictEqual(leg.honest_credit.action_book_exact, true);
      assert.ok(leg.honest_credit.displayed_opposing_capacity_at_or_below_x >= 5);
    }
  }
}

const nik = receipt.events.find((event) => event.event_id.endsWith("NIKVRB"));
assert.strictEqual(nik.objective_gate_pass, true);
const laj = receipt.events.find((event) => event.event_id.endsWith("LAJVAN"));
assert.strictEqual(laj.objective_gate_pass, false);
assert.strictEqual(laj.legs.find((leg) => leg.leg_id === "LAJ").delta_to_own_window1_close_cents, 5);
const bra = receipt.events.find((event) => event.event_id.endsWith("BRAVED")).legs.find((leg) => leg.leg_id === "BRA");
assert.strictEqual(bra.proposed_entry_cents, null);
assert.strictEqual(bra.terminal_reason, "FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW");

console.log("PASS test_window1_five_exact_honest_gate_v1 (five events, ten legs, 804 gate closed)");
