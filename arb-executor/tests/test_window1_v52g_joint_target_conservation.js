#!/usr/bin/env node
"use strict";

const assert = require("assert");
const clean = require("../analysis/window1_n9_clean_store.js");
const v52f = require("../analysis/window1_v52f_pair_entry_conservation.js");
const v52g = require("../analysis/window1_v52g_joint_target_conservation.js");

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
v52g.configurePalantir(clean.makeCleanStore(manifest, assets));

assert.equal(v52g.fullPostOnsetRead, v52f.fullPostOnsetRead);
assert.equal(v52g.fullPostOnsetAuthority, v52f.fullPostOnsetAuthority);
assert.equal(v52g.observePostOnsetEvidence, v52f.observePostOnsetEvidence);
assert.equal(v52g.tradeTruthCredit, v52f.tradeTruthCredit);
assert.equal(v52g.continuousConsultation, v52f.continuousConsultation);
const normalized = v52g.normalizedClauses({ joint_target_conservation: true });
assert.equal(normalized.joint_target_conservation, true);
assert.equal(normalized.pair_entry_conservation, true);

const open = v52g.jointTargetConservation({ siblingCredited: false }, 48);
assert.equal(open.reason, "COUNTERPART_TARGET_NOT_YET_LICENSED");
assert.equal(open.licensed_target_cents, 48);
assert.equal(open.target_changed, false);
const standing = v52g.jointTargetConservation({ siblingCredited: false, siblingStandingTarget: 60 }, 45);
assert.equal(standing.counterpart_kind, "STANDING_SIDE");
assert.equal(standing.max_lawful_target_cents, 39);
assert.equal(standing.licensed_target_cents, 39);
assert.equal(standing.arithmetic, "39+60=99<=99");
assert.equal(standing.target_changed, true);
const bought = v52g.jointTargetConservation({ siblingCredited: true, siblingEntryCents: 49, siblingStandingTarget: 80 }, 55);
assert.equal(bought.counterpart_kind, "BOUGHT_SIDE");
assert.equal(bought.licensed_target_cents, 50);
assert.equal(bought.passed, true);
assert.throws(() => v52g.jointTargetConservation({ siblingStandingTarget: 0 }, 50), /counterpart cents unlawful/);
assert.throws(() => v52g.jointTargetConservation({ siblingStandingTarget: 50 }, 101), /proposed target unlawful/);

const context = { category: "ATP_MAIN", startingPriceSplit: "26_50|51_75", combinedState: "FALLING", quoteState: "FALLING", pressureState: "RISING", siblingState: "RISING", row: { ts: 200, receipt: "book#2", ask: 55 } };
const license = {
  onset: { passed: true, timestamp_epoch: 100 }, read: { passed: true }, diary: { passed: true }, coherence: { lows_under_par: true, disagreement_clear: true }, palantir: v52g.continuousConsultation(context),
  level: { authority: "V41_TEST_LEVEL", machine_read_evidence: { evaluation_timestamp_epoch: 200, directional_evidence_timestamp_epoch: 190, evaluation_receipt: "book#2", directional_evidence_receipt: "book#1", post_onset_observation_bounds: { min_cents: 45, max_cents: 55 }, current_book: { ask: 55 } } },
};
const incumbent = { action: "PLACE_REST", target_cents: 45, placement: { target_cents: 45, authority: "V41_TEST_LEVEL" } };
const decision = v52g.gateDecision({ clauses: { palantir_priors: true, joint_target_conservation: true }, birthLicense: license, activeTarget: null, pairCap: null, siblingCredited: false, siblingStandingTarget: 60 }, incumbent);
assert.equal(decision.action, "PLACE_REST");
assert.equal(decision.target_cents, 39);
assert.equal(decision.birth_license.level.pre_clause_6_target_cents, 45);
assert.equal(decision.birth_license.joint_target_conservation.counterpart_kind, "STANDING_SIDE");
assert.equal(decision.target_cents + 60, 99);
const postCredit = v52g.gateDecision({ clauses: { palantir_priors: true, joint_target_conservation: true }, birthLicense: license, activeTarget: 51, pairCap: 50, siblingCredited: true, siblingEntryCents: 49, siblingStandingTarget: null }, { ...incumbent, target_cents: 51 });
assert(postCredit.target_cents <= 50);
assert(postCredit.target_cents + 49 <= 99);
assert.equal(postCredit.birth_license.pair_entry_conservation.passed, true);
assert.equal(postCredit.birth_license.joint_target_conservation.passed, true);

console.log(JSON.stringify({ tests: 31, pass: true }));
