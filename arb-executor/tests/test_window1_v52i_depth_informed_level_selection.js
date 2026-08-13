#!/usr/bin/env node
"use strict";

const assert = require("assert");
const clean = require("../analysis/window1_n9_clean_store.js");
const underValidation = require("../analysis/window1_v52i_under_validation_store.js");
const v52h = require("../analysis/window1_v52h_remove_pair_lows_precondition.js");
const v52i = require("../analysis/window1_v52i_depth_informed_level_selection.js");

let tests = 0;
const check = (value, message) => { tests += 1; assert(value, message); };
const equal = (actual, expected, message) => { tests += 1; assert.deepStrictEqual(actual, expected, message); };
const ids = clean.REQUIRED;
const entry = (id) => ({ id, name: `asset-${id}`, status: id === "P6" ? "VALID-NARROW - test" : "VALIDATED - test" });
const source = (id) => ({ inventory: "store_CLEAN", commit: "a".repeat(40), path: `${id}.json`, sha256: "b".repeat(64), status: entry(id).status });
const data = {
  P1: { ATP_MAIN: { "55": { edge_p50: 4, zone: "TEST" } } },
  P2: { discriminators: { tables: { cat: { ATP_MAIN: { n: 10 } }, cell: { "26_50|51_75": { n: 9 } }, mirror: { coherent_inverse: { share: .8 }, incoherent_same: { share: .2 }, mixed_settled: { share: .5 } } } } },
  P4: { accuracy_per_state: { "60m": { FALLING: { n: 8 } } }, accuracy_per_category: { "60m": { ATP_MAIN: { n: 8 } } } },
  P6: { mechanism_classes: { JOIN: 1 } }, P11: { DEV: { by_category: { ATP_MAIN: { INSIDE: 4 } } } },
  P12: { DEV: { total: 74, classes: { ARRIVED: 9 } } }, P13: { sealed: { MIRROR_COHERENCE: { n: 10 } }, cap: { THE_22: { n: 22, vindicated: 20 } } },
  P14: { per_category: { ATP_MAIN: { n_spike: 5, rank: [{ signal: "dwell" }] } } },
};
const manifest = { LABEL: "MACHINE_PALANTIR", store_CLEAN: ids.map(entry), inventory_UNVALIDATED: [], inventory_QUARANTINED: [], inventory_SUPERSEDED: [] };
const assets = { __manifest: { commit: "9".repeat(40), sha256: "8".repeat(64) } };
for (const id of ids) assets[id] = { data: data[id], sources: [source(id)] };
const canonical = clean.makeCleanStore(manifest, assets);
const candidateSource = (id) => ({ inventory: "inventory_UNDER_VALIDATION_V52I", commit: "c".repeat(40), path: `${id}.json`, sha256: "d".repeat(64), status: "UNDER-VALIDATION_V52I" });
const validation = underValidation.makeUnderValidationStore(canonical, {
  G_GRID_LEVEL_DISCOUNT: { entry: { id: "G_GRID_LEVEL_DISCOUNT", status: "UNDER-VALIDATION_V52I" }, data: data.P1, sources: [candidateSource("G_GRID_LEVEL_DISCOUNT")] },
  G3_DIP_RECOVERY_GRADIENT: { entry: { id: "G3_DIP_RECOVERY_GRADIENT", status: "UNDER-VALIDATION_V52I" }, data: { depth_cells: { "ATP_MAIN|26_50": { median: 8, p75: 10, n: 40 } }, recovery_within_60min: { "ATP_MAIN|26_50": .5 } }, sources: [candidateSource("G3_DIP_RECOVERY_GRADIENT")] },
});
v52i.configurePalantir(validation);

equal(validation.boot_assertion.under_validation_loaded, 2);
equal(validation.boot_assertion.unvalidated_loaded, 0);
check(validation.boot_assertion.canonical_clean_store_unchanged);
equal(v52i.tradeTruthCredit, v52h.tradeTruthCredit);
equal(v52i.settlementIdentity, v52h.settlementIdentity);
equal(v52i.jointTargetConservation, v52h.jointTargetConservation);

const context = { clauses: { depth_informed_level_selection: true }, category: "ATP_MAIN", priceRegion: "26_50", startingPriceSplit: "26_50|51_75", combinedState: "FALLING", quoteState: "FALLING", pressureState: "RISING", siblingState: "RISING", row: { ts: 200, receipt: "book#2", ask: 55 } };
const consultation = v52i.continuousConsultation(context);
equal(consultation.under_validation.candidate_ids, ["G_GRID_LEVEL_DISCOUNT", "G3_DIP_RECOVERY_GRADIENT"]);
equal(consultation.N4.depth_candidates_under_validation.G_GRID.discount_cents, 4);
equal(consultation.N4.depth_candidates_under_validation.G3.dip_depth_median_cents, 8);
check(consultation.N4.depth_candidates_under_validation.provenance.every((row) => row.status === "UNDER-VALIDATION_V52I"));
equal(consultation.priors_gate, false);

const authorizedLicense = { onset: { passed: true, timestamp_epoch: 100 }, palantir: consultation, level: { machine_read_evidence: { evaluation_timestamp_epoch: 200, directional_evidence_timestamp_epoch: 190, evaluation_receipt: "book#2", directional_evidence_receipt: "book#1", post_onset_observation_bounds: { min_cents: 40, max_cents: 55 }, current_book: { ask: 55 } } } };
const incumbent = { action: "PLACE_REST", target_cents: 53, placement: { target_cents: 53, authority: "V41_TEST_LEVEL" } };
const selection = v52i.depthSelection(authorizedLicense, incumbent);
check(selection.applicable);
equal(selection.weighted_discount_cents, 6);
equal(selection.live_bounded_candidate_target_cents, 49);
equal(selection.selected_target_cents, 49);
check(selection.target_changed);
equal(selection.priors_gate, false);
check(selection.live_authority_retained);

const unauthorized = v52i.depthSelection({ palantir: consultation, level: {} }, { action: "NO_CALL", target_cents: null });
equal(unauthorized.applicable, false);
equal(unauthorized.reason, "LIVE_MACHINE_READ_AUTHORITY_ABSENT_PRIORS_SILENT");
equal(unauthorized.selected_target_cents, null);

const noCell = v52i.depthCandidates({ category: "WTA_MAIN", priceRegion: "26_50", row: { ask: 55 } });
equal(noCell.G_GRID, null);
equal(noCell.G3, null);
check(noCell.provenance.length === 2);
assert.throws(() => underValidation.makeUnderValidationStore(canonical, {}), /candidate identity mismatch/); tests += 1;

console.log(JSON.stringify({ tests, pass: true }));
