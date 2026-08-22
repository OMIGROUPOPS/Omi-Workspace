"use strict";

const assert = require("assert");
const os = require("../analysis/window1_v54_functionable_os.js");

function neighbor(eventId, observedLow, finalLow, score = 1) {
  return {
    event_id: eventId,
    score,
    coverage: 1,
    quality: "FOUNDATION_MINUTE_BELL_BOUNDED",
    grain: "MINUTE",
    licensed_layers: ["MACRO", "MICRO"],
    legs: [{ anchor_cents: 41, observed_low_cents: observedLow, low_cents: finalLow, low_basis: "TRUE_TRADE" }],
  };
}

const noDip = os.conditionalNeighborLeg([
  neighbor("A", 41, 41),
  neighbor("B", 41, 40),
  neighbor("C", 41, 41),
  neighbor("D", 39, 35),
], 0, { anchor_cents: 41, true_trade_low_cents: null, book_path_low_cents: 41, true_trade_count: 0 });
assert.equal(noDip.own_evidence.dip_state, "NO_DIP_OBSERVED");
assert.equal(noDip.rows.length, 4);
assert.equal(noDip.excluded.length, 0);
assert.equal(noDip.conditional_remaining_dip_distribution_cents.q50, 0);
assert.equal(noDip.derived_floor_cents, 41);
assert.equal(noDip.binary_state_gate_used, false);
assert.equal(noDip.legacy_blanket_low_ratio_used, false);

const dipped = os.conditionalNeighborLeg([
  neighbor("A", 39, 37),
  neighbor("B", 39, 38),
  neighbor("C", 41, 40),
], 0, { anchor_cents: 41, true_trade_low_cents: 39, book_path_low_cents: 38, true_trade_count: 2 });
assert.equal(dipped.own_evidence.basis, "TRUE_TRADE");
assert.equal(dipped.rows.length, 3);
assert.equal(dipped.conditional_remaining_dip_distribution_cents.q50, 1);
assert.equal(dipped.derived_floor_cents, 38);
assert(dipped.rows.every((row) => Number.isFinite(row.evidence_match_grade)));

const state = os.createTapeState({ event_id: "TEST", category: "ATP_MAIN", discovery_epoch: 0, leg_ids: ["AAA", "BBB"], anchors_cents: { AAA: 40, BBB: 60 }, formation_end_epochs: { AAA: 1, BBB: 1 } });
os.observe(state, "AAA", { kind: "PRINT", timestamp_epoch: 2, receipt: "P1", price_cents: 39, size: 2 });
os.observe(state, "AAA", { kind: "PRINT", timestamp_epoch: 3, receipt: "P2", price_cents: 37, size: 3 });
os.observe(state, "BBB", { kind: "BOOK", timestamp_epoch: 3, receipt: "B1", bid_cents: 59, ask_cents: 61, last_trade_cents: 60 });
const reads = os.readAll(state);
assert.equal(reads.lows_travel.value.AAA.true_trade_low_cents, 37);
assert.equal(reads.lows_travel.value.AAA.true_trade_high_cents, 39);
assert.equal(reads.lows_travel.value.AAA.true_trade_count, 2);
assert(os.EXPECTED_RESOURCE_IDS.includes("FOUNDATION_PER_MINUTE_UNIVERSE"));
assert(os.EXPECTED_RESOURCE_IDS.includes("SPIKE_ATLAS"));

process.stdout.write("window1_v54_repair_iteration2: PASS\n");
