"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "../..");
const pkg = path.join(root, ".claude/window1_live_v4_replay/v50_first_fill_price_discipline_20260811");
const read = (name) => JSON.parse(fs.readFileSync(path.join(pkg, name), "utf8"));
const sha = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

const status = read("CONSTRUCTION_STATUS.json");
assert.equal(status.status, "BLOCKED_V47_REMAINS_OPERATIVE");

const score = read("ATTRIBUTION_SCORECARD.json");
assert.equal(score.frozen_V47_reproduction.pass, true);
assert.equal(score.rows.length, 2);
assert.equal(score.rows[0].machine, "V47_BASELINE");
assert.equal(score.rows[1].machine, "V50_FIRST_FILL_PRICE_DISCIPLINE");

const receipt = read("CAP_BOUND_RECOVERY_AND_COST_RECEIPT.json");
assert.equal(receipt.sealed_mechanism_evidence.rows, 45);
assert.equal(receipt.sealed_mechanism_evidence.first_fill_richness, 31);
assert.equal(receipt.sealed_mechanism_evidence.genuinely_infeasible, 14);
assert.equal(receipt.sealed_mechanism_evidence.direct_identity_join_to_development, false);
assert.ok(receipt.two_columns.CAP_UNFEASIBLE_RECOVERY.eligible_dev_CAP_UNFEASIBLE_pairs > 0);
assert.equal(receipt.conservation.pass, true);

const acceptance = read("COMPOSITION_ACCEPTANCE_BAR.json");
assert.equal(acceptance.mechanism_bound_checks.V47_baseline_reproduced, true);
assert.equal(acceptance.mechanism_bound_checks.causal_bound_violations_zero, true);
assert.equal(acceptance.mechanism_bound_checks.CAP_BOUND_conservation, true);
assert.equal(acceptance.mechanism_bound_checks.named_no_regressions, false);
assert.equal(acceptance.pass, false);

const named = read("NAMED_V50_RECEIPT.json");
assert.equal(named.assertions.ARNROM_no_regression, false);
assert.equal(named.assertions.KRUFER_no_regression, true);
assert.equal(named.assertions.BOSCOP_no_regression, true);

const determinism = read("DETERMINISM_RECEIPT.json");
assert.equal(determinism.clean_builds, 2);
assert.equal(determinism.byte_identical, true);

const forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json");
assert.equal(forbidden.holdout_accesses, 0);
assert.equal(forbidden.live_accesses, 0);
assert.equal(forbidden.network_runtime_accesses, 0);

const manifest = read("ARTIFACT_HASH_MANIFEST.json");
for (const [name, meta] of Object.entries(manifest.files)) {
  const file = path.join(pkg, name);
  assert.ok(fs.existsSync(file), `missing ${name}`);
  assert.equal(sha(file), meta.sha256, `hash ${name}`);
  assert.equal(fs.statSync(file).size, meta.bytes, `bytes ${name}`);
}

console.log("PASS test_window1_v50_first_fill_price_discipline_package");
