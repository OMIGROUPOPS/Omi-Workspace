#!/usr/bin/env node
"use strict";

const assert = require("assert");
const v52c = require("../analysis/window1_v52c_full_post_onset_read.js");
const v52d = require("../analysis/window1_v52d_disagreement_referee.js");

assert.equal(v52d.fullPostOnsetRead, v52c.fullPostOnsetRead);
assert.equal(v52d.fullPostOnsetAuthority, v52c.fullPostOnsetAuthority);
assert.equal(v52d.machineReadLevel, v52c.machineReadLevel);
assert.equal(v52d.gateDecision, v52c.gateDecision);
assert.equal(v52d.firstFailure, v52c.firstFailure);
assert.equal(v52d.normalizedClauses({ disagreement_referee: true }).disagreement_referee, true);
assert.equal(v52d.normalizedClauses({}).disagreement_referee, undefined);

const state = v52d.emptyReadState(100);
v52d.observePostOnsetEvidence(state, { kind: "BOOK", ts: 100, receipt: "book#1", bid: 30, ask: 32, spread: 2 });
v52d.observePostOnsetEvidence(state, { kind: "BOOK", ts: 101, receipt: "book#2", bid: 29, ask: 31, spread: 2 });
const quote = v52d.fullPostOnsetRead(state, { ts: 101, receipt: "book#2" });
assert.equal(quote.state, "FALLING");
const classWinner = v52d.adjudicateDisagreement({ quote, pressure: "RISING", row: { ts: 101, receipt: "book#2", depth_ratio: 0.8 }, readState: state });
assert.equal(classWinner.resolved, true);
assert.equal(classWinner.winner.reading, "FALLING");
assert.equal(classWinner.winner.evidence_class, "QUOTE_PATH");
assert.equal(classWinner.loser.evidence_class, "DEPTH_PRESSURE");
assert.equal(classWinner.comparison.decisive_field, "evidence_class_rank");
assert.equal(classWinner.palantir_priors_consumed, false);
assert.equal(classWinner.N9_post_bell_consumed, false);
assert.equal(classWinner.historical_inputs_consumed, false);

const newer = v52d.compareBacking(
  { evidence_class_rank: 2, timestamp_epoch: 11, magnitude: 1 },
  { evidence_class_rank: 2, timestamp_epoch: 10, magnitude: 99 },
);
assert.deepEqual(newer, { comparison_field: "timestamp_epoch", result: 1 });
const larger = v52d.compareBacking(
  { evidence_class_rank: 2, timestamp_epoch: 11, magnitude: 2 },
  { evidence_class_rank: 2, timestamp_epoch: 11, magnitude: 1 },
);
assert.deepEqual(larger, { comparison_field: "magnitude", result: 1 });
assert.deepEqual(v52d.compareBacking(
  { evidence_class_rank: 2, timestamp_epoch: 11, magnitude: 2 },
  { evidence_class_rank: 2, timestamp_epoch: 11, magnitude: 2 },
), { comparison_field: "EXACT_TIE", result: 0 });

const tieState = v52d.emptyReadState(0);
tieState.referee_support_by_direction.FALLING = { direction: "FALLING", evidence_class: "DEPTH_PRESSURE", evidence_class_rank: 1, timestamp_epoch: 20, receipt: "same", magnitude_cents: 0.25 };
const tie = v52d.adjudicateDisagreement({
  quote: { state: "FALLING" },
  pressure: "RISING",
  row: { ts: 20, receipt: "same", depth_ratio: 0.75 },
  readState: tieState,
});
assert.equal(tie.resolved, false);
assert.equal(tie.status, "HONEST_TIE_FREEZE_STANDS");
assert.equal(tie.winner, null);
assert.equal(tie.loser, null);

const noFire = v52d.adjudicateDisagreement({ quote: { state: "RISING" }, pressure: "RISING", row: { ts: 20, receipt: "same", depth_ratio: 0.7 }, readState: state });
assert.equal(noFire.firing, false);
assert.equal(noFire.resolved, false);

console.log(JSON.stringify({ tests: 31, pass: true }));
