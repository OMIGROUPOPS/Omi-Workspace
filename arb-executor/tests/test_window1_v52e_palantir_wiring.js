#!/usr/bin/env node
"use strict";

const assert = require("assert");
const clean = require("../analysis/window1_n9_clean_store.js");
const v52d = require("../analysis/window1_v52d_disagreement_referee.js");
const v52e = require("../analysis/window1_v52e_palantir_wiring.js");

const ids = clean.REQUIRED;
const entry = (id) => ({ id, name: `asset-${id}`, status: id === "P6" ? "VALID-NARROW - test" : "VALIDATED - test" });
const source = (id) => ({ inventory: "store_CLEAN", commit: "a".repeat(40), path: `${id}.json`, sha256: "b".repeat(64), status: entry(id).status });
const data = {
  P1: { ATP_MAIN: { "35": { edge_p50: 2 } } },
  P2: { discriminators: { tables: { cat: { ATP_MAIN: { n: 10 } }, cell: { "26_50|51_75": { n: 9 } }, mirror: { coherent_inverse: { share: 0.8 }, incoherent_same: { share: 0.2 }, mixed_settled: { share: 0.5 } } } } },
  P4: { accuracy_per_state: { "60m": { FALLING: { n: 8 } } }, accuracy_per_category: { "60m": { ATP_MAIN: { n: 8 } } } },
  P6: { mechanism_classes: { JOIN: 1 } },
  P11: { DEV: { by_category: { ATP_MAIN: { INSIDE: 4, AT_BBO: 6 } } } },
  P12: { DEV: { total: 74, classes: { ARRIVED: 9 } } },
  P13: { sealed: { MIRROR_COHERENCE: { n: 10 } }, cap: { THE_22: { n: 22, vindicated: 20 } } },
  P14: { per_category: { ATP_MAIN: { n_spike: 5, rank: [{ signal: "dwell" }] } } },
};
const manifest = { LABEL: "MACHINE_PALANTIR", store_CLEAN: ids.map(entry), inventory_UNVALIDATED: [], inventory_QUARANTINED: [], inventory_SUPERSEDED: [] };
const assets = { __manifest: { commit: "9".repeat(40), sha256: "8".repeat(64) } };
for (const id of ids) assets[id] = { data: data[id], sources: [source(id)] };
const store = clean.makeCleanStore(manifest, assets);
assert.equal(store.boot_assertion.passed, true);
assert.equal(store.boot_assertion.loaded_ids.length, 8);
assert.throws(() => clean.makeCleanStore({ ...manifest, store_CLEAN: manifest.store_CLEAN.map((row) => row.id === "P1" ? { ...row, status: "UNVALIDATED" } : row) }, assets), /non-validated CLEAN status refused/);
assert.equal(v52e.configurePalantir(store).passed, true);

const context = { category: "ATP_MAIN", priceRegion: "26_50", startingPriceSplit: "26_50|51_75", combinedState: "FALLING", quoteState: "FALLING", pressureState: "RISING", siblingState: "RISING", row: { ts: 200, receipt: "book#2", ask: 35 } };
const palantir = v52e.continuousConsultation(context);
assert.equal(palantir.continuous_at_decision_time, true);
assert.equal(palantir.priors_gate, false);
assert.equal(palantir.N2.node, "N2");
assert.equal(palantir.N4.grid.edge_p50, 2);
assert.equal(palantir.N4.decision_time_cell_source, "CURRENT_QUALIFYING_BOOK_ASK_NOT_EX_POST_CLOSE");
assert.equal(palantir.N5.node, "N5");
assert(palantir.N2.provenance.every((row) => row.status.startsWith("VALID")));

const license = {
  onset: { passed: true, timestamp_epoch: 100 },
  read: { passed: true }, diary: { passed: true }, coherence: { lows_under_par: true, disagreement_clear: true }, palantir,
  level: { machine_read_evidence: { evaluation_timestamp_epoch: 200, directional_evidence_timestamp_epoch: 190, evaluation_receipt: "book#2", directional_evidence_receipt: "book#1", post_onset_observation_bounds: { min_cents: 30, max_cents: 35 }, current_book: { ask: 35 } } },
};
const rescue = v52e.machineReadLevel(license, { action: "PLACE_REST", target_cents: 40, placement: { target_cents: 40, authority: "V41_TEST" } });
assert.equal(rescue.authorized, true);
assert.equal(rescue.palantir_rescue, true);
assert.equal(rescue.target_cents, 33);
const preserved = v52e.machineReadLevel(license, { action: "PLACE_REST", target_cents: 31, placement: { target_cents: 31, authority: "V41_TEST" } });
assert.equal(preserved.authorized, true);
assert.equal(preserved.palantir_rescue, false);
assert.equal(preserved.target_cents, 31);

const tieState = v52d.emptyReadState(0);
tieState.referee_support_by_direction.FALLING = { direction: "FALLING", evidence_class: "DEPTH_PRESSURE", evidence_class_rank: 1, timestamp_epoch: 20, receipt: "same", magnitude_cents: 0.25 };
const adjudicated = v52e.adjudicateDisagreement({ quote: { state: "FALLING" }, pressure: "RISING", row: { ts: 20, receipt: "same", depth_ratio: 0.75 }, readState: tieState, siblingState: "RISING", palantir });
assert.equal(adjudicated.resolved, true);
assert.equal(adjudicated.status, "ADJUDICATED_N5_STRICTLY_STRONGER_VALIDATED_BASE_RATE");
assert.equal(adjudicated.palantir_priors_consumed, true);
assert.equal(adjudicated.prior_role, "INFORMANT_NEVER_GATE");

assert.equal(v52e.fullPostOnsetRead, v52d.fullPostOnsetRead);
assert.equal(v52e.fullPostOnsetAuthority, v52d.fullPostOnsetAuthority);
assert.equal(v52e.observePostOnsetEvidence, v52d.observePostOnsetEvidence);
assert.equal(v52e.firstFailure, v52d.firstFailure);
assert.equal(v52e.tradeTruthCredit, v52d.tradeTruthCredit);
assert.equal(v52e.normalizedClauses({ palantir_priors: true }).palantir_priors, true);

console.log(JSON.stringify({ tests: 31, pass: true }));
