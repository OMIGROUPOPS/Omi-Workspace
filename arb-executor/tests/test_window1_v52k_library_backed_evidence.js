#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const clean = require("../analysis/window1_n9_clean_store.js");
const underValidation = require("../analysis/window1_v52i_under_validation_store.js");
const v52h = require("../analysis/window1_v52h_remove_pair_lows_precondition.js");
const v52k = require("../analysis/window1_v52k_library_backed_evidence.js");

let tests = 0;
const check = (value, message) => { tests += 1; assert(value, message); };
const equal = (actual, expected, message) => { tests += 1; assert.deepStrictEqual(actual, expected, message); };
const ids = clean.REQUIRED;
const entry = (id) => ({ id, name: `asset-${id}`, status: id === "P6" ? "VALID-NARROW - test" : "VALIDATED - test" });
const source = (id) => ({ inventory: "store_CLEAN", commit: "a".repeat(40), path: `${id}.json`, sha256: "b".repeat(64), status: entry(id).status });
const data = {
  P1: { ATP_MAIN: { "55": { edge_p50: 4, zone: "TEST" } } },
  P2: { discriminators: { tables: { cat: { ATP_MAIN: { n: 10 } }, cell: { "26_50|51_75": { n: 9 } }, mirror: { coherent_inverse: { share: .8 } } } } },
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
v52k.configurePalantir(validation);

equal(validation.boot_assertion.under_validation_loaded, 2);
equal(v52k.tradeTruthCredit, v52h.tradeTruthCredit);
equal(v52k.settlementIdentity, v52h.settlementIdentity);
equal(v52k.jointTargetConservation, v52h.jointTargetConservation);
equal(v52k.adjudicateDisagreement, v52h.adjudicateDisagreement);
const sourceText = fs.readFileSync(path.join(__dirname, "../analysis/window1_v52k_library_backed_evidence.js"), "utf8");
check(!sourceText.includes('require("./window1_v52i_depth_informed_level_selection.js")'), "V52k must not inherit V52i behavior");
check(!sourceText.includes('require("./window1_v52j_role_conditioned_level_selection.js")'), "V52k must not inherit V52j behavior");

const clauses = { judgment_gate: true, machine_read_level_authority: true, full_post_onset_evidence_horizon: true, disagreement_referee: true, palantir_priors: true, pair_entry_conservation: true, joint_target_conservation: true, remove_pair_lows_precondition: true, library_backed_level_evidence: true };
const context = { clauses, category: "ATP_MAIN", priceRegion: "26_50", startingPriceSplit: "26_50|51_75", combinedState: "FALLING", quoteState: "FALLING", pressureState: "FALLING", siblingState: "RISING", row: { ts: 200, receipt: "book#2", ask: 55 } };
const consultation = v52k.continuousConsultation(context);
equal(consultation.N4.library_level_evidence_under_validation.G_GRID.discount_cents, 4);
equal(consultation.N4.library_level_evidence_under_validation.G3.dip_depth_median_cents, 8);
check(consultation.N4.library_level_evidence_under_validation.provenance.every((row) => row.status === "UNDER-VALIDATION_V52I"));
equal(consultation.priors_gate, false);

const license = ({ read = true, min = 50, target = 53 } = {}) => ({
  onset: { passed: true, timestamp_epoch: 100 },
  read: { passed: read, state: "FALLING", quote_path_state: "FALLING", pressure_state: "FALLING", receipt: "book#2" },
  coherence: { disagreement_clear: true }, palantir: consultation,
  level: { proposed_target_cents: target, machine_read_evidence: { evaluation_timestamp_epoch: 200, directional_evidence_timestamp_epoch: 190, evaluation_receipt: "book#2", directional_evidence_receipt: "book#1", directional_evidence_kind: "NEW_LOW_ASK", post_onset_observation_bounds: { min_cents: min, max_cents: 55 }, current_book: { ask: 55 } } },
});
const incumbent = { action: "PLACE_REST", target_cents: 53, placement: { target_cents: 53, authority: "V41_TEST_LEVEL" } };

const selected = v52k.libraryEvidenceSelection(license(), incumbent, {});
check(selected.applicable);
equal(selected.weighting_law, "ROUND(G_GRID_DISCOUNT*G3_RECOVERY + G3_MEDIAN_DIP_DEPTH*(1-G3_RECOVERY))");
equal(selected.prior_values.weighted_discount_cents, 6);
equal(selected.library_supported_floor_cents, 49);
equal(selected.selected_target_cents, 49);
equal(selected.below_shown_range, true);
equal(selected.evidence_authority, "VALIDATED_LIBRARY");
equal(selected.prior_provenance.map((row) => row.asset_id), ["G_GRID_LEVEL_DISCOUNT", "G3_DIP_RECOVERY_GRADIENT"]);
check(selected.prior_provenance.every((row) => row.source_sha256 === "d".repeat(64)));

const decision = v52k.gateDecision({ clauses, birthLicense: license() }, incumbent);
equal(decision.target_cents, 49);
equal(decision.library_backed_level_evidence.final_licensed_target_cents, 49);
equal(decision.birth_license.level.library_backed_level_evidence.library_supported_floor_cents, 49);
equal(decision.birth_license.level.machine_read.evidence.tape_only_post_onset_observation_bounds.min_cents, 50);
check(decision.target_cents < 50, "library-backed target must stand below shown range");

const noRead = v52k.libraryEvidenceSelection(license({ read: false }), incumbent, {});
equal(noRead.applicable, false);
equal(noRead.reason, "POST_ONSET_MACHINE_READ_ABSENT_LIBRARY_CANNOT_BYPASS_CLAUSE_2");
const capped = v52k.libraryEvidenceSelection(license(), incumbent, { siblingStandingTarget: 51 });
equal(capped.applicable, false);
equal(capped.reason, "LIBRARY_FLOOR_INCOMPATIBLE_WITH_CLAUSE_6_PAIR_SUM");
const withinShown = v52k.libraryEvidenceSelection(license({ min: 40 }), incumbent, {});
equal(withinShown.applicable, false);
equal(withinShown.evidence_authority, "POST_ONSET_TAPE");
equal(withinShown.selected_target_cents, 53);

const frozenClauses = { ...clauses, library_backed_level_evidence: false };
const frozenDecision = v52k.gateDecision({ clauses: frozenClauses, birthLicense: license({ min: 40 }) }, incumbent);
const directFrozen = v52h.gateDecision({ clauses: frozenClauses, birthLicense: license({ min: 40 }) }, incumbent);
equal(frozenDecision, directFrozen);

console.log(JSON.stringify({ tests, pass: true }));
