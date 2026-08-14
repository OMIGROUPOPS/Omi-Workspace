#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const clean = require("../analysis/window1_n9_clean_store.js");
const underValidation = require("../analysis/window1_v52i_under_validation_store.js");
const v52h = require("../analysis/window1_v52h_remove_pair_lows_precondition.js");
const v52j = require("../analysis/window1_v52j_role_conditioned_level_selection.js");

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
v52j.configurePalantir(validation);

equal(validation.boot_assertion.under_validation_loaded, 2);
equal(v52j.tradeTruthCredit, v52h.tradeTruthCredit);
equal(v52j.settlementIdentity, v52h.settlementIdentity);
equal(v52j.jointTargetConservation, v52h.jointTargetConservation);
check(!Object.prototype.hasOwnProperty.call(v52j, "depthSelection"), "V52j must not inherit V52i symmetric depthSelection");
const sourceText = fs.readFileSync(path.join(__dirname, "../analysis/window1_v52j_role_conditioned_level_selection.js"), "utf8");
check(!sourceText.includes('require("./window1_v52i_depth_informed_level_selection.js")'), "V52j must call V52h directly");

const clauses = { role_conditioned_level_selection: true };
const context = (own, sibling) => ({ clauses, category: "ATP_MAIN", priceRegion: "26_50", startingPriceSplit: "26_50|51_75", combinedState: own, quoteState: own, pressureState: own, siblingState: sibling, siblingReadEvidence: { state: sibling, receipt: "sib#1", directional_evidence_receipt: "sib#0" }, row: { ts: 200, receipt: "book#2", ask: 55 } });
const consultation = v52j.continuousConsultation(context("FALLING", "RISING"));
equal(consultation.N4.depth_candidates_under_validation.G_GRID.discount_cents, 4);
equal(consultation.N4.depth_candidates_under_validation.G3.dip_depth_median_cents, 8);
equal(consultation.N4.pair_role_inputs.sibling_read.receipt, "sib#1");
check(consultation.N4.depth_candidates_under_validation.provenance.every((row) => row.status === "UNDER-VALIDATION_V52I"));
equal(consultation.priors_gate, false);

const license = (own, sibling = "RISING") => ({ onset: { passed: true, timestamp_epoch: 100 }, read: { passed: true, state: own, quote_path_state: own, pressure_state: own, receipt: "book#2" }, coherence: { disagreement_clear: true }, palantir: v52j.continuousConsultation(context(own, sibling)), level: { machine_read_evidence: { evaluation_timestamp_epoch: 200, directional_evidence_timestamp_epoch: 190, evaluation_receipt: "book#2", directional_evidence_receipt: "book#1", directional_evidence_kind: "NEW_LOW_ASK", post_onset_observation_bounds: { min_cents: 40, max_cents: 55 }, current_book: { ask: 55 } } } });
const incumbent = { action: "PLACE_REST", target_cents: 53, placement: { target_cents: 53, authority: "V41_TEST_LEVEL" } };

const falling = v52j.roleConditionedSelection(license("FALLING"), incumbent);
check(falling.applicable);
equal(falling.role_assignment.own_role, "FALLING");
equal(falling.role_assignment.sibling_role, "RISING");
equal(falling.role_assignment.pair_read_coherence, "INVERSE_COHERENT");
equal(falling.weighted_discount_cents, 6);
equal(falling.selected_target_cents, 49);
check(falling.target_changed);

for (const role of ["RISING", "SETTLED", null]) {
  const selected = v52j.roleConditionedSelection(license(role), incumbent);
  equal(selected.applicable, false);
  equal(selected.selected_target_cents, 53);
  equal(selected.target_changed, false);
}
equal(v52j.roleConditionedSelection(license("RISING"), incumbent).reason, "RISING_USES_OWN_NEAR_SUPPORT_FROZEN_EVIDENCE_BACKED_LEVEL");
equal(v52j.roleConditionedSelection(license("SETTLED"), incumbent).reason, "SETTLED_OR_INSUFFICIENT_USES_FROZEN_EVIDENCE_BACKED_LEVEL");
equal(v52j.pairRoleCoherence("FALLING", "FALLING"), "SAME_DIRECTION_DISAGREEMENT");
equal(v52j.pairRoleCoherence("FALLING", "RISING"), "INVERSE_COHERENT");

const fallingDecision = v52j.gateDecision({ clauses, birthLicense: license("FALLING") }, incumbent);
equal(fallingDecision.target_cents, 49);
equal(fallingDecision.role_conditioned_level_selection.role_assignment.own_role, "FALLING");
const risingDecision = v52j.gateDecision({ clauses, birthLicense: license("RISING") }, incumbent);
equal(risingDecision.target_cents, 53);
equal(risingDecision.role_conditioned_level_selection.role_assignment.own_role, "RISING");
check(fallingDecision.role_conditioned_level_selection.role_assignment.own_read_evidence.receipt === "book#2");
check(fallingDecision.role_conditioned_level_selection.role_assignment.sibling_read_evidence.receipt === "sib#1");

console.log(JSON.stringify({ tests, pass: true }));
