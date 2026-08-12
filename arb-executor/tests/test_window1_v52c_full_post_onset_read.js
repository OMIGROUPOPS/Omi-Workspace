#!/usr/bin/env node
"use strict";

const assert = require("assert");
const v52b = require("../analysis/window1_v52b_read_level_authority.js");
const v52c = require("../analysis/window1_v52c_full_post_onset_read.js");

assert.equal(v52c.machineReadLevel, v52b.machineReadLevel);
assert.equal(v52c.gateDecision, v52b.gateDecision);
assert.equal(v52c.firstFailure, v52b.firstFailure);
assert.equal(v52c.normalizedClauses({ full_post_onset_evidence_horizon: true }).full_post_onset_evidence_horizon, true);
assert.equal(v52c.normalizedClauses({}).full_post_onset_evidence_horizon, undefined);
assert.equal(v52c.fullPostOnsetAuthority({ disagreement: false, authority: "TRAILING_300S_QUOTE_PATH_PRIMARY" }), "FULL_POST_ONSET_HISTORY_PRIMARY");
assert.equal(v52c.fullPostOnsetAuthority({ disagreement: false, authority: "QUOTE_PATH_AND_JUL6_PRESSURE_AGREE" }), "FULL_POST_ONSET_HISTORY_AND_JUL6_PRESSURE_AGREE");
assert.equal(v52c.fullPostOnsetAuthority({ disagreement: true, authority: "TRAILING_300S_QUOTE_PATH_PRIMARY" }), "FULL_POST_ONSET_HISTORY_VS_JUL6_PRESSURE_DISAGREE");

const state = v52c.emptyReadState(100);
v52c.observePostOnsetEvidence(state, { kind: "BOOK", ts: 99, receipt: "pre", bid: 30, ask: 32 });
assert.equal(state.evidence_receipts, 0);
v52c.observePostOnsetEvidence(state, { kind: "BOOK", ts: 100, receipt: "book#1", bid: 30, ask: 32, spread: 2 });
let read = v52c.fullPostOnsetRead(state, { ts: 100, receipt: "book#1" });
assert.equal(read.receipt, null);
assert.equal(read.full_post_onset_evidence.sufficient, false);
assert.equal(read.full_post_onset_evidence.fixed_horizon_seconds, null);
assert.equal(read.full_post_onset_evidence.replacement_tuning_constant, null);

v52c.observePostOnsetEvidence(state, { kind: "BOOK", ts: 101, receipt: "book#2", bid: 29, ask: 31, spread: 2 });
read = v52c.fullPostOnsetRead(state, { ts: 101, receipt: "book#2" });
assert.equal(read.state, "FALLING");
assert.equal(read.receipt, "book#2");
assert.equal(read.full_post_onset_evidence.consulted.evidence_receipts, 2);

v52c.observePostOnsetEvidence(state, { kind: "PRINT", ts: 1001, receipt: "print#1", price: 31, size: 8, trade_id: "t1" });
read = v52c.fullPostOnsetRead(state, { ts: 1001, receipt: "print#1" });
assert.equal(read.full_post_onset_evidence.first_evidence.receipt, "book#1");
assert.equal(read.full_post_onset_evidence.span_seconds, 901);
assert.equal(read.full_post_onset_evidence.consulted.evidence_receipts, 3);
assert.equal(read.full_post_onset_evidence.weighting_law.includes("ALL_POST_ONSET_EVIDENCE_RETAINS_POSITIVE_WEIGHT"), true);

v52c.observePostOnsetEvidence(state, { kind: "PRINT", ts: 5000, receipt: "print#2", price: 35, size: 7, trade_id: "t2" });
read = v52c.fullPostOnsetRead(state, { ts: 5000, receipt: "print#2" });
assert.equal(read.full_post_onset_evidence.consulted.evidence_receipts, 4);
assert.equal(read.full_post_onset_evidence.first_evidence.receipt, "book#1");
assert.equal(read.full_post_onset_evidence.last_evidence.receipt, "print#2");
assert.equal(read.full_post_onset_evidence.span_seconds, 4900);

assert.throws(() => v52c.observePostOnsetEvidence(v52c.emptyReadState(null), { kind: "BOOK", ts: 1, receipt: "x" }), /requires onset/);
assert.throws(() => v52c.observePostOnsetEvidence(v52c.emptyReadState(0), { kind: "OTHER", ts: 1, receipt: "x" }), /unsupported/);

console.log(JSON.stringify({ tests: 25, pass: true }));
