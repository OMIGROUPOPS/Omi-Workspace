#!/usr/bin/env node
"use strict";

const assert = require("assert");
const clean = require("../analysis/window1_n9_clean_store.js");
const v52e = require("../analysis/window1_v52e_palantir_wiring.js");
const v52f = require("../analysis/window1_v52f_pair_entry_conservation.js");

const ids = clean.REQUIRED;
const entry = (id) => ({ id, name: `asset-${id}`, status: id === "P6" ? "VALID-NARROW - test" : "VALIDATED - test" });
const source = (id) => ({ inventory: "store_CLEAN", commit: "a".repeat(40), path: `${id}.json`, sha256: "b".repeat(64), status: entry(id).status });
const data = {
  P1: { ATP_MAIN: { "55": { edge_p50: 2 } } },
  P2: { discriminators: { tables: { cat: { ATP_MAIN: { n: 10 } }, cell: { "26_50|51_75": { n: 9 } }, mirror: { coherent_inverse: { share: 0.8 }, incoherent_same: { share: 0.2 }, mixed_settled: { share: 0.5 } } } } },
  P4: { accuracy_per_state: { "60m": { FALLING: { n: 8 } } }, accuracy_per_category: { "60m": { ATP_MAIN: { n: 8 } } } },
  P6: { mechanism_classes: { JOIN: 1 } }, P11: { DEV: { by_category: { ATP_MAIN: { INSIDE: 4 } } } },
  P12: { DEV: { total: 74, classes: { ARRIVED: 9 } } }, P13: { sealed: { MIRROR_COHERENCE: { n: 10 } }, cap: { THE_22: { n: 22, vindicated: 20 } } },
  P14: { per_category: { ATP_MAIN: { n_spike: 5, rank: [{ signal: "dwell" }] } } },
};
const manifest = { LABEL: "MACHINE_PALANTIR", store_CLEAN: ids.map(entry), inventory_UNVALIDATED: [], inventory_QUARANTINED: [], inventory_SUPERSEDED: [] };
const assets = { __manifest: { commit: "9".repeat(40), sha256: "8".repeat(64) } };
for (const id of ids) assets[id] = { data: data[id], sources: [source(id)] };
const store = clean.makeCleanStore(manifest, assets);
v52f.configurePalantir(store);

assert.equal(v52f.fullPostOnsetRead, v52e.fullPostOnsetRead);
assert.equal(v52f.fullPostOnsetAuthority, v52e.fullPostOnsetAuthority);
assert.equal(v52f.observePostOnsetEvidence, v52e.observePostOnsetEvidence);
assert.equal(v52f.firstFailure, v52e.firstFailure);
assert.equal(v52f.tradeTruthCredit, v52e.tradeTruthCredit);
assert.equal(v52f.continuousConsultation, v52e.continuousConsultation);
assert.equal(v52f.machineReadLevel, v52e.machineReadLevel);
assert.equal(v52f.normalizedClauses({ pair_entry_conservation: true }).pair_entry_conservation, true);

const noSibling = v52f.settlementIdentity({ siblingCredited: false }, 51);
assert.equal(noSibling.applicable, false); assert.equal(noSibling.licensed_target_cents, 51); assert.equal(noSibling.passed, true);
const bounded = v52f.settlementIdentity({ siblingCredited: true, siblingEntryCents: 49, pairCap: 50 }, 51);
assert.equal(bounded.max_lawful_target_cents, 50); assert.equal(bounded.licensed_target_cents, 50); assert.equal(bounded.target_changed, true); assert.equal(bounded.passed, true); assert.equal(bounded.arithmetic, "50+49=99<100");
const already = v52f.settlementIdentity({ siblingCredited: true, siblingEntryCents: 49, pairCap: 50 }, 50);
assert.equal(already.target_changed, false); assert.equal(already.passed, true);
assert.throws(() => v52f.settlementIdentity({ siblingCredited: true, siblingEntryCents: 49, pairCap: 51 }, 51), /pair-cap mismatch/);

const context = { category: "ATP_MAIN", startingPriceSplit: "26_50|51_75", combinedState: "FALLING", quoteState: "FALLING", pressureState: "RISING", siblingState: "RISING", row: { ts: 200, receipt: "book#2", ask: 55 } };
const palantir = v52f.continuousConsultation(context);
const license = {
  onset: { passed: true, timestamp_epoch: 100 }, read: { passed: true }, diary: { passed: true }, coherence: { lows_under_par: true, disagreement_clear: true }, palantir,
  level: { machine_read_evidence: { evaluation_timestamp_epoch: 200, directional_evidence_timestamp_epoch: 190, evaluation_receipt: "book#2", directional_evidence_receipt: "book#1", post_onset_observation_bounds: { min_cents: 45, max_cents: 55 }, current_book: { ask: 55 } } },
};
const incumbent = { action: "PLACE_REST", target_cents: 51, placement: { target_cents: 51, authority: "V41_TEST" } };
const decision = v52f.gateDecision({ clauses: { palantir_priors: true, pair_entry_conservation: true }, birthLicense: license, activeTarget: 50, siblingCredited: true, siblingEntryCents: 49, pairCap: 50 }, incumbent);
assert.equal(decision.action, "HOLD_REST"); assert.equal(decision.target_cents, 50); assert.equal(decision.birth_license.level.pre_clause_5_target_cents, 51); assert.equal(decision.birth_license.level.target_cents, 50); assert.equal(decision.birth_license.pair_entry_conservation.passed, true); assert.equal(decision.target_cents + 49, 99);
const absent = v52f.gateDecision({ clauses: { palantir_priors: true, pair_entry_conservation: true }, birthLicense: { ...license, read: { passed: false } }, activeTarget: 50, siblingCredited: true, siblingEntryCents: 49, pairCap: 50 }, incumbent);
assert.equal(absent.judgment_gate.failure, "NO_TAPE_MACHINE_READ_ABSENT"); assert.equal(absent.birth_license.pair_entry_conservation.reached, false);

console.log(JSON.stringify({ tests: 27, pass: true }));
