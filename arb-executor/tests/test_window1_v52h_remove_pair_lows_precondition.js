#!/usr/bin/env node
"use strict";

const assert = require("assert");
const clean = require("../analysis/window1_n9_clean_store.js");
const v52g = require("../analysis/window1_v52g_joint_target_conservation.js");
const v52h = require("../analysis/window1_v52h_remove_pair_lows_precondition.js");

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
v52h.configurePalantir(clean.makeCleanStore(manifest, assets));

assert.equal(v52h.fullPostOnsetRead, v52g.fullPostOnsetRead);
assert.equal(v52h.fullPostOnsetAuthority, v52g.fullPostOnsetAuthority);
assert.equal(v52h.observePostOnsetEvidence, v52g.observePostOnsetEvidence);
assert.equal(v52h.tradeTruthCredit, v52g.tradeTruthCredit);
assert.equal(v52h.continuousConsultation, v52g.continuousConsultation);
const normalized = v52h.normalizedClauses({ remove_pair_lows_precondition: true });
assert.equal(normalized.remove_pair_lows_precondition, true);
assert.equal(normalized.joint_target_conservation, true);
assert.equal(normalized.pair_entry_conservation, true);

const context = { category: "ATP_MAIN", startingPriceSplit: "26_50|51_75", combinedState: "FALLING", quoteState: "FALLING", pressureState: "RISING", siblingState: "RISING", row: { ts: 200, receipt: "book#2", ask: 55 } };
const baseLicense = {
  onset: { passed: true, timestamp_epoch: 100 }, read: { passed: true }, diary: { passed: true },
  coherence: { lows_under_par: false, lows_sum_cents: 103, disagreement_firing: false, disagreement_clear: true },
  palantir: v52h.continuousConsultation(context),
  level: { authority: "V41_TEST_LEVEL", machine_read_evidence: { evaluation_timestamp_epoch: 200, directional_evidence_timestamp_epoch: 190, evaluation_receipt: "book#2", directional_evidence_receipt: "book#1", post_onset_observation_bounds: { min_cents: 45, max_cents: 55 }, current_book: { ask: 55 } } },
};
const incumbent = { action: "PLACE_REST", target_cents: 45, placement: { target_cents: 45, authority: "V41_TEST_LEVEL" } };
const inputs = { clauses: { palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true }, birthLicense: baseLicense, activeTarget: null, pairCap: null, siblingCredited: false, siblingStandingTarget: 50 };
const blocked = v52g.gateDecision(inputs, incumbent);
assert.equal(blocked.judgment_gate.failure, "PAIR_POST_ONSET_LOWS_NOT_UNDER_PAR");
const licensed = v52h.gateDecision({ ...inputs, clauses: { ...inputs.clauses, remove_pair_lows_precondition: true } }, incumbent);
assert.equal(licensed.judgment_gate.failure, null);
assert.equal(licensed.action, "PLACE_REST");
assert.equal(licensed.target_cents, 45);
assert.equal(licensed.birth_license.coherence.lows_under_par, false);
assert.equal(licensed.birth_license.clause_4_market_proof_precondition.removed_from_licensing, true);
assert.equal(licensed.birth_license.clause_4_market_proof_precondition.original_lows_sum_cents, 103);

const disagreementLicense = { ...baseLicense, coherence: { ...baseLicense.coherence, disagreement_firing: true, disagreement_clear: false } };
const disagreement = v52h.gateDecision({ ...inputs, clauses: { ...inputs.clauses, remove_pair_lows_precondition: true }, birthLicense: disagreementLicense }, incumbent);
assert.equal(disagreement.judgment_gate.failure, "FIRING_DISAGREEMENT_ACTIVE");
assert.equal(disagreement.birth_license.clause_4_market_proof_precondition.disagreement_referee_untouched, true);

const conserved = v52h.gateDecision({ ...inputs, clauses: { ...inputs.clauses, remove_pair_lows_precondition: true }, siblingStandingTarget: 60 }, incumbent);
assert.equal(conserved.target_cents, 39);
assert.equal(conserved.birth_license.joint_target_conservation.passed, true);
assert.equal(conserved.target_cents + 60, 99);
assert.equal(v52h.marketProofReceipt(baseLicense.coherence).recorded_as_telemetry, true);

console.log(JSON.stringify({ tests: 24, pass: true }));
