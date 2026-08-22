"use strict";

const assert = require("assert");
const os = require("../analysis/window1_v54_functionable_os.js");

const meta = {
  event_id: "TEST-EVENT",
  event_date: "26JUL01",
  category: "ATP_MAIN",
  discovery_epoch: 100,
  bell_epoch: 1000,
  bell_source: "TEST",
  leg_ids: ["AAA", "BBB"],
  anchors_cents: { AAA: 40, BBB: 60 },
  formation_end_epochs: { AAA: 200, BBB: 200 },
};
const state = os.createTapeState(meta);
const books = [
  [110, "AAA", 39, 41, 40, 100, 120], [110, "BBB", 59, 61, 60, 120, 100],
  [150, "AAA", 38, 40, 39, 110, 130], [150, "BBB", 60, 62, 61, 130, 110],
  [210, "AAA", 37, 39, 38, 120, 140], [210, "BBB", 61, 63, 62, 140, 120],
];
for (const [ts, leg, bid, ask, last, bidDepth, askDepth] of books) os.observe(state, leg, { timestamp_epoch: ts, receipt: `${leg}-${ts}`, kind: "BOOK", bid_cents: bid, ask_cents: ask, last_trade_cents: last, bid_depth_5: bidDepth, ask_depth_5: askDepth, bid_1_sz: 10, ask_1_sz: 11 });
os.observe(state, "AAA", { timestamp_epoch: 211, receipt: "print-a", kind: "PRINT", price_cents: 38, size: 5 });
os.observe(state, "BBB", { timestamp_epoch: 211, receipt: "print-b", kind: "PRINT", price_cents: 62, size: 7 });

const reads = os.readAll(state);
assert.equal(Object.keys(reads).length, 16);
for (const name of os.READER_NAMES) {
  assert.equal(reads[name].status, "CONNECTED");
  assert.equal(reads[name].reader, name);
  assert.ok(Array.isArray(reads[name].receipts));
}
assert.equal(reads.anchor_settle.value.formation_progress.AAA, 1);
assert.equal(reads.opening_split.value.sum_cents, 100);
assert.equal(reads.drift.value.AAA.drift_cents, -2);
assert.equal(reads.drift.value.BBB.drift_cents, 2);
state.positions.AAA.credited = true;
state.positions.AAA.entry_cents = 19;
assert.equal(reads.half_pair_state.value.legs.AAA.credited, false, "reader receipt must remain a point-in-time snapshot");

const vector = os.vectorFromReads(state, reads);
const corpus = [
  { event_id: "TEST-EVENT", event_date: "26JUL01", category: "ATP_MAIN", quality: "SELF", vector, legs: [], source_receipts: [] },
  { event_id: "NEIGHBOR-1", event_date: "26JUN01", category: "ATP_MAIN", quality: "RANGE", vector: { ...vector, leg0_drift_cents: -3, leg1_drift_cents: 3 }, legs: [{ leg_id: "N1A", anchor_cents: 40, observed_low_cents: 38, low_cents: 35, floor_fraction: 0.5 }, { leg_id: "N1B", anchor_cents: 60, observed_low_cents: 58, low_cents: 55, floor_fraction: 0.5 }], source_receipts: [{ source_id: "RANGE", row_ref: "range.jsonl#row-1" }] },
  { event_id: "NEIGHBOR-2", event_date: "26MAY01", category: "ATP_CHALL", quality: "HIST", vector: { ...vector, category: "ATP_CHALL", leg0_drift_cents: -10 }, legs: [{ leg_id: "N2A", anchor_cents: 40, observed_low_cents: 36, low_cents: 30, floor_fraction: 0.75 }, { leg_id: "N2B", anchor_cents: 60, observed_low_cents: 56, low_cents: 50, floor_fraction: 0.75 }], source_receipts: [{ source_id: "HIST", row_ref: "historical.csv#line-2" }] },
];
const neighborhood = os.retrieveNeighborhood(corpus, vector, "TEST-EVENT", 2, state.receipt);
assert.equal(neighborhood.length, 2);
assert.ok(neighborhood.every((row) => row.event_id !== "TEST-EVENT"));
assert.equal(neighborhood[0].event_id, "NEIGHBOR-1");
assert.ok(neighborhood[0].score > neighborhood[1].score);

const resources = os.EXPECTED_RESOURCE_IDS.map((id) => ({ id, status: "CONNECTED", receipt: `${id}-receipt` }));
const derivation = os.deriveAction({ state, reads, neighborhood, legId: "AAA", lineage: { action: "PLACE_REST", target_cents: 38, receipt: "lineage.jsonl#row-1" }, resources });
assert.equal(derivation.sentence_action_assertion.equal, true);
assert.equal(derivation.citation_receipt_assertion.equal, true);
assert.match(derivation.sentence, /ACTION=/);
assert.match(derivation.sentence, /CR-[0-9a-f]{64}/);
assert.equal(derivation.pair_conservation.at_or_below_99, true);
assert.equal(derivation.resources_consulted.length, 0, "connectivity must not be mislabeled as consultation");
assert.ok(Object.values(derivation.citation_receipts).every((row) => row.captured_at_receipt === state.receipt));
assert.equal(derivation.derivation.target_basis, "FITNESS_WEIGHTED_BLEND");
assert.equal(derivation.derivation.evidence_rung, "FITNESS_WEIGHTED_BLEND");
assert.equal(derivation.derivation.basis_weights.length, 4);
assert.ok(Math.abs(derivation.derivation.basis_weights.reduce((total, row) => total + row.normalized_weight, 0) - 1) < 1e-12);
assert.ok(derivation.derivation.basis_weights.filter((row) => row.available).every((row) => row.normalized_weight > 0));
assert.equal(derivation.derivation.stale_prior_path_used, false);
assert.match(derivation.sentence, /TOUCH_RELATION=/);
assert.match(derivation.sentence, /time-conditioned remaining-dip/);
assert.match(derivation.sentence, /CHOSEN_DEPTH_CENTS=/);
assert.match(derivation.sentence, /OWN_WINDOW=/);
assert.match(derivation.sentence, /PAIR_STATE=/);
assert.match(derivation.sentence, /FITNESS_WEIGHTS=TIME_BEARING_NEIGHBORS:/);

const untimedNeighborhood = neighborhood.map((row) => ({ ...row, legs: row.legs.map((leg) => ({ ...leg, floor_fraction: null })) }));
const untimedBlend = os.deriveAction({ state, reads, neighborhood: untimedNeighborhood, legId: "AAA", lineage: { action: "PLACE_REST", target_cents: 38, receipt: "lineage.jsonl#row-r2" }, resources });
assert.equal(untimedBlend.derivation.evidence_rung, "FITNESS_WEIGHTED_BLEND");
assert.equal(untimedBlend.derivation.basis_weights.find((row) => row.basis === "TIME_BEARING_NEIGHBORS").normalized_weight, 0);
assert.ok(untimedBlend.derivation.basis_weights.find((row) => row.basis === "GRADED_NEIGHBORS").normalized_weight > 0);

const ownReflexBlend = os.deriveAction({ state, reads, neighborhood: [], legId: "AAA", lineage: { action: "PLACE_REST", target_cents: 38, receipt: "lineage.jsonl#row-r3" }, resources });
assert.equal(ownReflexBlend.derivation.evidence_rung, "FITNESS_WEIGHTED_BLEND");
assert.equal(ownReflexBlend.derivation.basis_weights.find((row) => row.basis === "TIME_BEARING_NEIGHBORS").normalized_weight, 0);
assert.equal(ownReflexBlend.derivation.basis_weights.find((row) => row.basis === "GRADED_NEIGHBORS").normalized_weight, 0);
assert.ok(ownReflexBlend.derivation.basis_weights.find((row) => row.basis === "OWN_TAPE_PRESENCE").normalized_weight > 0);
assert.equal(ownReflexBlend.derivation.proposed_target_cents, reads.books.value.AAA.bid_cents);

const splitState = os.createTapeState(meta);
splitState.positions.AAA.standing_target_cents = 60;
splitState.positions.BBB.standing_target_cents = 36;
const splitReads = { half_pair_state: { value: { legs: { AAA: { ...splitState.positions.AAA }, BBB: { ...splitState.positions.BBB } } } } };
function splitRow(legId, target, grade) {
  const actionStatement = `ACTION=HOLD_REST; TARGET_CENTS=${target}; ACTIVE_TARGET_BEFORE_CENTS=${target}.`;
  return {
    leg_id: legId,
    action: { action: "HOLD_REST", target_cents: target, reason: "INCUMBENT" },
    derivation: { lawful_unallocated_target_cents: target, derived_target_cents: target, allocation_priority_grade: grade },
    sentence: `ALLOCATION=INCUMBENT-PENDING-JOINT-DERIVATION. ${actionStatement}`,
    sentence_action_assertion: { expected_statement: actionStatement, equal: true },
    pair_conservation: { at_or_below_99: true },
  };
}
const splitRows = [splitRow("AAA", 60, 1), splitRow("BBB", 41, 3)];
os.allocatePairActions({ state: splitState, reads: splitReads, derivations: splitRows });
assert.equal(splitRows[0].action.target_cents, 58, "lower-grade plan yields the larger continuous share");
assert.equal(splitRows[1].action.target_cents, 41, "higher-grade plan retains its fresh target");
assert(splitRows.every((row) => row.pair_conservation.at_or_below_99));
assert(splitRows.every((row) => row.sentence.includes("ALLOCATION=GRADED-CONTINUOUS-SPLIT")));
assert(splitRows.every((row) => row.derivation.allocation.stale_prior_consumed === false));
assert(splitRows.every((row) => row.derivation.allocation.from_cents !== row.derivation.allocation.to_cents));

const uncitedCorpus = [{ ...corpus[1], source_receipts: ["BARE_SOURCE_LABEL"] }];
assert.throws(
  () => os.retrieveNeighborhood(uncitedCorpus, vector, "TEST-EVENT", 1, state.receipt),
  /CITATION_RECEIPT_BUILD_VIOLATION NEIGHBOR_ROW_RECEIPT_MISSING/,
);

const beforeFormation = os.createTapeState(meta);
os.observe(beforeFormation, "AAA", { timestamp_epoch: 150, receipt: "pre-a", kind: "BOOK", bid_cents: 39, ask_cents: 41, last_trade_cents: 40 });
os.observe(beforeFormation, "BBB", { timestamp_epoch: 150, receipt: "pre-b", kind: "BOOK", bid_cents: 59, ask_cents: 61, last_trade_cents: 60 });
const beforeReads = os.readAll(beforeFormation), beforeVector = os.vectorFromReads(beforeFormation, beforeReads), beforeNeighbors = os.retrieveNeighborhood(corpus, beforeVector, "TEST-EVENT", 2, beforeFormation.receipt);
const blocked = os.deriveAction({ state: beforeFormation, reads: beforeReads, neighborhood: beforeNeighbors, legId: "AAA", lineage: { action: "PLACE_REST", target_cents: 38, receipt: "lineage.jsonl#row-0" }, resources });
assert.equal(blocked.action.action, "HOLD_REST");
assert.equal(blocked.action.target_cents, null);
assert.match(blocked.sentence, /ACTION=HOLD_REST; TARGET_CENTS=NONE/);

const noTape = os.createTapeState(meta);
const noTapeReads = os.readAll(noTape);
const noEvidenceBlend = os.deriveAction({ state: noTape, reads: noTapeReads, neighborhood: [], legId: "AAA", lineage: { action: "PLACE_REST", target_cents: 38, receipt: "lineage.jsonl#row-r4" }, resources });
assert.equal(noEvidenceBlend.derivation.evidence_rung, "FITNESS_WEIGHTED_BLEND");
assert.equal(noEvidenceBlend.derivation.proposed_target_cents, null);
assert.equal(noEvidenceBlend.action.action, "HOLD_REST");

const handoff = os.createTapeState(meta);
for (const [ts, leg, bid, ask, last, bidDepth, askDepth] of books) os.observe(handoff, leg, { timestamp_epoch: ts, receipt: `handoff-${leg}-${ts}`, kind: "BOOK", bid_cents: bid, ask_cents: ask, last_trade_cents: last, bid_depth_5: bidDepth, ask_depth_5: askDepth, bid_1_sz: 10, ask_1_sz: 11 });
handoff.positions.AAA.standing_target_cents = 38;
const fillRow = { timestamp_epoch: 212, receipt: "trade-fill-a", kind: "PRINT", price_cents: 38, size: 5 };
const fillReceipt = os.creditPosition(handoff, "AAA", fillRow);
os.observe(handoff, "AAA", fillRow);
assert.equal(fillReceipt.citation_type, "FILL_EVENT");
assert.equal(handoff.positions.AAA.entry_cents, 38);
const handoffReads = os.readAll(handoff), handoffVector = os.vectorFromReads(handoff, handoffReads);
assert.equal(handoffVector.half_pair_credited_count, 1);
assert.equal(handoffVector.leg0_credited_entry_cents, 38);
const handoffNeighbors = os.retrieveNeighborhood(corpus, handoffVector, "TEST-EVENT", 2, handoff.receipt);
assert.ok(handoffNeighbors.every((row) => row.query_fingerprint_sha256));
const handoffDerivation = os.deriveAction({ state: handoff, reads: handoffReads, neighborhood: handoffNeighbors, legId: "BBB", lineage: { action: "PLACE_REST", target_cents: 60, receipt: "lineage.jsonl#row-fill" }, resources });
assert.ok(handoffDerivation.derivation.fill_handoff_receipt_id);
assert.match(handoffDerivation.sentence, /trade receipt trade-fill-a/);
assert.match(handoffDerivation.sentence, /re-posed query/);
assert.ok(handoffDerivation.sentence.includes(handoffDerivation.derivation.fill_handoff_receipt_id));

console.log("window1_v54_functionable_os: PASS");
