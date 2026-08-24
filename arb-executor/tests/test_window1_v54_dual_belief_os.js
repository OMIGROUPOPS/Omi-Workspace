"use strict";

const assert = require("assert");
const os = require("../analysis/window1_v54_dual_belief_os.js");

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
assert.equal(derivation.derivation.target_basis, "EVIDENCED_TOUCH");
assert.equal(derivation.derivation.evidence_rung, "EVIDENCED_TOUCH");
assert.equal(derivation.derivation.proposed_target_cents, reads.books.value.AAA.bid_cents);
assert.equal(derivation.derivation.stale_prior_path_used, false);
assert.match(derivation.sentence, /TOUCH_RELATION=/);
assert.match(derivation.sentence, /PRICE_AT_EVIDENCED_TOUCH=/);
assert.match(derivation.sentence, /MAP_CELL=/);
assert.match(derivation.sentence, /MAP_P50_CENTS=/);
assert.match(derivation.sentence, /MAP_MEMBERS=/);
assert.match(derivation.sentence, /CHOSEN_DEPTH_CENTS=/);
assert.match(derivation.sentence, /OWN_WINDOW=/);
assert.match(derivation.sentence, /PAIR_STATE=/);
assert.match(derivation.sentence, /EVIDENCE_RUNG=EVIDENCED_TOUCH/);

const untimedNeighborhood = neighborhood.map((row) => ({ ...row, legs: row.legs.map((leg) => ({ ...leg, floor_fraction: null })) }));
const rung2 = os.deriveAction({ state, reads, neighborhood: untimedNeighborhood, legId: "AAA", lineage: { action: "PLACE_REST", target_cents: 38, receipt: "lineage.jsonl#row-r2" }, resources });
assert.equal(rung2.derivation.evidence_rung, "EVIDENCED_TOUCH");
assert.equal(rung2.derivation.proposed_target_cents, reads.books.value.AAA.bid_cents);

const rung3 = os.deriveAction({ state, reads, neighborhood: [], legId: "AAA", lineage: { action: "PLACE_REST", target_cents: 38, receipt: "lineage.jsonl#row-r3" }, resources });
assert.equal(rung3.derivation.evidence_rung, "EVIDENCED_TOUCH");
assert.equal(rung3.derivation.distribution_depth_cents, 0);
assert.equal(rung3.derivation.proposed_target_cents, reads.books.value.AAA.bid_cents);

os.configureTrueBellCellDepthMap({
  kind: "TRUE_BELL_CELL_CONDITIONAL_DEPTH_MAP_V3",
  commit: "ac68e3bc-test",
  path: "TRUE_BELL_CELL_DEPTH_MAP.json",
  sha256: "map-test-sha",
  cells: [{ category: "ATP_MAIN", price_cell: 37, edge_p50_cents: 3, n_legs: 20 }],
});
const timedCorpus = corpus.map((row) => row.event_id === "TEST-EVENT" ? row : ({
  ...row,
  legs: row.legs.map((leg) => ({ ...leg, specialist_record: { kind: "BOUNDED_TWO_BEHAVIOR_FLOOR_CAPTURE", floor_fraction: 0.5, source_receipt: `${row.event_id}|${leg.leg_id}|floor` } })),
}));
const timedNeighborhood = os.retrieveNeighborhood(timedCorpus, vector, "TEST-EVENT", 2, state.receipt);
const mapped = os.deriveAction({ state, reads, neighborhood: timedNeighborhood, legId: "AAA", lineage: { action: "PLACE_REST", target_cents: 38, receipt: "lineage.jsonl#row-map" }, resources });
assert.equal(mapped.derivation.evidence_rung, "TRUE_BELL_CELL_DEPTH_MAP_V3_LICENSED");
assert.equal(mapped.derivation.true_bell_cell_depth_map.licensed, true);
assert.equal(mapped.derivation.proposed_target_cents, 34);
assert.match(mapped.sentence, /MAP_CELL=ATP_MAIN\|37/);
assert.match(mapped.sentence, /MAP_P50_CENTS=3/);

const splitState = os.createTapeState(meta);
splitState.positions.AAA.standing_target_cents = 60;
splitState.positions.BBB.standing_target_cents = 36;
const splitReads = { half_pair_state: { value: { legs: { AAA: { ...splitState.positions.AAA }, BBB: { ...splitState.positions.BBB } } } } };
function splitRow(legId, target, grade) {
  const actionStatement = `ACTION=HOLD_REST; TARGET_CENTS=${target}; ACTIVE_TARGET_BEFORE_CENTS=${target}.`;
  const liveAsk = target + 1;
  return {
    leg_id: legId,
    action: { action: "HOLD_REST", target_cents: target, reason: "INCUMBENT" },
    derivation: {
      lawful_unallocated_target_cents: target,
      derived_target_cents: target,
      allocation_priority_grade: grade,
      live_bid_cents: target,
      live_ask_cents: liveAsk,
      formation_complete: true,
      formed_two_sided_book: true,
      crossed_book: false,
      true_bell_cell_depth_map: { cell: { edge_p50_cents: 5 } },
    },
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
const rung4 = os.deriveAction({ state: noTape, reads: noTapeReads, neighborhood: [], legId: "AAA", lineage: { action: "PLACE_REST", target_cents: 38, receipt: "lineage.jsonl#row-r4" }, resources });
assert.equal(rung4.derivation.evidence_rung, "EVIDENCED_TOUCH");
assert.equal(rung4.derivation.proposed_target_cents, null);
assert.equal(rung4.action.action, "HOLD_REST");
assert.equal(rung4.action.target_cents, null);

const handoff = os.createTapeState(meta);
for (const [ts, leg, bid, ask, last, bidDepth, askDepth] of books) os.observe(handoff, leg, { timestamp_epoch: ts, receipt: `handoff-${leg}-${ts}`, kind: "BOOK", bid_cents: bid, ask_cents: ask, last_trade_cents: last, bid_depth_5: bidDepth, ask_depth_5: askDepth, bid_1_sz: 10, ask_1_sz: 11 });
handoff.positions.AAA.standing_target_cents = 38;
handoff.positions.AAA.standing_license_basis = "LAYERED_COHERENT_ENVELOPE";
handoff.positions.AAA.standing_license_receipt = "belief-license-receipt";
const fillRow = { timestamp_epoch: 212, receipt: "trade-fill-a", kind: "PRINT", price_cents: 36, size: 5 };
const fillReceipt = os.creditPosition(handoff, "AAA", fillRow);
os.observe(handoff, "AAA", fillRow);
assert.equal(fillReceipt.citation_type, "FILL_EVENT");
assert.equal(handoff.positions.AAA.entry_cents, 38);
assert.equal(fillReceipt.context.entry_cents, 38);
assert.equal(fillReceipt.context.triggering_print_price_cents, 36);
assert.equal(fillReceipt.context.execution_price_basis, "STANDING_REST_LIMIT_CENTS");
assert.equal(fillReceipt.context.standing_license_basis, "LAYERED_COHERENT_ENVELOPE");
assert.equal(fillReceipt.context.standing_license_receipt, "belief-license-receipt");
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

const jointState = os.createTapeState(meta);
for (const [ts, leg, bid, ask, last, bidDepth, askDepth] of books) os.observe(jointState, leg, { timestamp_epoch: ts, receipt: `joint-${leg}-${ts}`, kind: "BOOK", bid_cents: bid, ask_cents: ask, last_trade_cents: last, bid_depth_5: bidDepth, ask_depth_5: askDepth, bid_1_sz: 10, ask_1_sz: 11 });
os.observe(jointState, "AAA", { timestamp_epoch: 211, receipt: "joint-print-a", kind: "PRINT", price_cents: 38, size: 5 });
os.observe(jointState, "BBB", { timestamp_epoch: 211, receipt: "joint-print-b", kind: "PRINT", price_cents: 62, size: 7 });
const jointReads = os.readAll(jointState), jointVector = os.vectorFromReads(jointState, jointReads);
const jointCorpus = [
  { event_id: "JOINT-N1", event_date: "26JUN01", category: "ATP_MAIN", quality: "FOUNDATION_MINUTE_BELL_BOUNDED", grain: "MINUTE", licensed_layers: ["MACRO", "MICRO"], vector: jointVector, legs: [{ leg_id: "JA", anchor_cents: 40, observed_low_cents: 38, low_cents: 36, floor_fraction: 0.5, future_low_return_path: [{ window_fraction: 0, seen_true_trade_low_cents: 38, strict_future_true_trade_low_cents: 39, future_low_minus_seen_low_cents: 1, source_row_ref: "minute#ja" }], future_low_return_source: "future-low#ja" }, { leg_id: "JB", anchor_cents: 60, observed_low_cents: 58, low_cents: 58, floor_fraction: 0.5, future_low_return_path: [{ window_fraction: 0, seen_true_trade_low_cents: 58, strict_future_true_trade_low_cents: 57, future_low_minus_seen_low_cents: -1, source_row_ref: "minute#jb" }], future_low_return_source: "future-low#jb" }], source_receipts: [{ source_id: "FOUNDATION", row_ref: "foundation.jsonl#row-1" }] },
];
const jointNeighborhood = os.retrieveNeighborhood(jointCorpus, jointVector, "TEST-EVENT", 1, jointState.receipt);
os.configurePhaseCentralSurface({
  kind: "F_VS_124_PHASE_CATEGORY_CENTRAL_FUTURE_LOW_SURFACE",
  sha256: "surface-test-sha",
  source_sha256: "future-low-test-sha",
  cells: [{ category: "ATP_MAIN", phase_band: "P00_10", phase_low_inclusive: 0, phase_high_exclusive: 0.1, members: 101, q25_cents: -1, q50_cents: 0, q75_cents: 1, q50_midrank: 0.51 }],
});
const joint = os.deriveJointActions({ state: jointState, reads: jointReads, neighborhood: jointNeighborhood, lineageByLeg: { AAA: { action: "PLACE_REST", target_cents: 37, receipt: "lineage#aaa" }, BBB: { action: "PLACE_REST", target_cents: 61, receipt: "lineage#bbb" } }, resources });
assert.equal(joint.layers.macro.context.status, "RESOLVED");
assert.equal(joint.layers.micro.context.status, "RESOLVED");
assert.equal(joint.layers.micro_micro.context.status, "RESOLVED");
assert.equal(joint.coherence.status, "COHERENT");
assert.equal(joint.derivations.length, 2);
assert(joint.derivations.every((row) => row.sentence.includes("MACRO:") && row.sentence.includes("MICRO:") && row.sentence.includes("MICRO-MICRO:")));
assert(joint.derivations.every((row) => row.sentence.includes("SETTLED_BOOK_MID_SERIES_FLOORED_FROM_BID_ASK")));
assert(joint.derivations.every((row) => row.sentence.includes("book-receipt=")));
assert(joint.derivations.every((row) => Object.values(row.layered_dual_belief.micro.beliefs).every((belief) => belief.status !== "RESOLVED" || belief.belief_price_cents === Math.floor((belief.live_bid_cents + belief.live_ask_cents) / 2))));
assert(joint.derivations.every((row) => row.layered_dual_belief.envelope_placement.numeric_constant_added === false));
assert(joint.derivations.every((row) => row.sentence.includes("ENVELOPE_PLACEMENT=")));
assert(joint.derivations.every((row) => row.sentence.includes("SOURCE_KEY=LIBRARY_CLOSE_CENTS") || row.sentence.includes("V3_KEY=LIBRARY_CLOSE_CENTS->CURRENT_CAUSAL_BEST_BID_CENTS")));
assert(joint.derivations.every((row) => row.pair_conservation.at_or_below_99));
assert(joint.derivations.every((row) => Object.values(row.layered_dual_belief.macro.conditioned_priors).every((prior) => prior.remaining_dip_distribution_cents.q50 <= prior.conditioned_total_dip_distribution_cents.q50)), "remaining travel must be total minus arrived");
assert.equal(joint.derivations[0].layered_dual_belief.macro.conditioned_priors.AAA.remaining_dip_distribution_cents.q50, 2);
assert.equal(joint.derivations[0].layered_dual_belief.macro.conditioned_priors.BBB.remaining_dip_distribution_cents.q50, 0);
assert.equal(joint.derivations[0].layered_dual_belief.micro.beliefs.AAA.predicted_cents, 38, "belief target must add the phase-central strict-future-low offset to the causal seen low");
assert.equal(joint.derivations[0].layered_dual_belief.micro.beliefs.AAA.remaining_dip_consumption.expected_future_low_minus_seen_low_cents, 0);
assert.equal(joint.derivations[0].layered_dual_belief.micro.beliefs.AAA.phase_conditioning.phase_central_estimate.estimate_rank_in_population, 0.51);
assert(joint.derivations.every((row) => row.sentence.includes("CENTRAL_ESTIMATE_RANK=0.51")));
assert.equal(joint.derivations[0].layered_dual_belief.micro.beliefs.AAA.remaining_dip_consumption.own_low_return_assumption_removed, true);
assert(joint.derivations.every((row) => row.layered_dual_belief.coherence_placement.current_coherence));
assert(joint.derivations.filter((row) => row.action.action === "PLACE_REST").every((row) => row.layered_dual_belief.coherence_placement.qualification_to_action_latency_seconds === 0));
assert(joint.derivations.every((row) => row.layered_dual_belief.coherence_placement.stale_envelope_originated_new_rest === false));
assert(joint.derivations.every((row) => Object.values(row.layered_dual_belief.micro.beliefs).every((belief) => belief.deadline.deadline_epoch >= belief.deadline.emitted_at_epoch && belief.deadline.derives_fresh_at_each_emission)));
assert(joint.derivations.every((row) => row.sentence.includes("remaining-dip=total-minus-arrived=") && row.sentence.includes("deadline-emitted-now=")));

const noOpinionState = os.createTapeState(meta);
for (const [ts, leg, bid, ask, last, bidDepth, askDepth] of books) os.observe(noOpinionState, leg, { timestamp_epoch: ts, receipt: `noop-${leg}-${ts}`, kind: "BOOK", bid_cents: bid, ask_cents: ask, last_trade_cents: last, bid_depth_5: bidDepth, ask_depth_5: askDepth, bid_1_sz: 10, ask_1_sz: 11 });
const noOpinionReads = os.readAll(noOpinionState);
const noOpinion = os.deriveJointActions({ state: noOpinionState, reads: noOpinionReads, neighborhood: [], lineageByLeg: { AAA: { action: "PLACE_REST", target_cents: 37, receipt: "lineage#aaa" }, BBB: { action: "PLACE_REST", target_cents: 61, receipt: "lineage#bbb" } }, resources });
assert.deepEqual(noOpinion.derivations.map((row) => row.action.target_cents), [37, 61]);
assert(noOpinion.derivations.every((row) => row.action.action === "PLACE_REST"));
assert(noOpinion.derivations.every((row) => row.action.reason === "OWN_EVIDENCED_LIVE_TOUCH_ENVELOPE_NULL"));
assert(noOpinion.derivations.every((row) => row.layered_dual_belief.independent_lane_may_complete === true));
assert(noOpinion.derivations.every((row) => row.layered_dual_belief.envelope_placement.mode === "CONSUME_OWN_EVIDENCED_LIVE_TOUCH_WHILE_ENVELOPE_NULL"));

console.log("window1_v54_dual_belief_os: PASS");
