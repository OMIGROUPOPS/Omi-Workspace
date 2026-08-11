"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "../..");
const pkg = path.join(root, ".claude/window1_live_v4_replay/v50r_one_directional_price_discipline_20260811");
const read = (name) => JSON.parse(fs.readFileSync(path.join(pkg, name), "utf8"));
const sha = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

const status = read("CONSTRUCTION_STATUS.json");
assert.ok(["PASS_MECHANISM_BOUND", "BLOCKED_V47_REMAINS_OPERATIVE"].includes(status.status));

const score = read("ATTRIBUTION_SCORECARD.json");
assert.equal(score.frozen_V47_reproduction.pass, true);
assert.equal(score.rows.length, 2);
assert.equal(score.rows[0].machine, "V47_BASELINE");
assert.equal(score.rows[1].machine, "V50_FIRST_FILL_PRICE_DISCIPLINE");

const control = read("CONTROL_BINDING.json");
assert.equal(control.schema_version, "window1-v50r-one-directional-first-fill-price-discipline-control-v1");
assert.equal(control.architecture.price_not_timing, true);
assert.equal(control.architecture.clocks_as_decision_inputs.length, 0);

const named = read("NAMED_V50_RECEIPT.json");
assert.equal(typeof named.assertions.ARNROM_at_or_better_89, "boolean");
assert.equal(typeof named.assertions.PUTJEA_withheld, "boolean");

const acceptance = read("COMPOSITION_ACCEPTANCE_BAR.json");
assert.equal(acceptance.mechanism_bound_checks.V47_baseline_reproduced, true);
assert.equal(acceptance.mechanism_bound_checks.causal_bound_violations_zero, true);
assert.equal(acceptance.mechanism_bound_checks.CAP_BOUND_conservation, true);
assert.equal(acceptance.mechanism_bound_checks.named_no_regressions, named.pass);
assert.equal(status.status === "PASS_MECHANISM_BOUND", acceptance.pass);
if (acceptance.pass) {
  assert.equal(named.assertions.ARNROM_at_or_better_89, true);
  assert.equal(named.assertions.PUTJEA_withheld, true);
} else {
  assert.ok(!named.assertions.ARNROM_at_or_better_89 || !named.assertions.PUTJEA_withheld || !named.pass);
}

const receipt = read("CAP_BOUND_RECOVERY_AND_COST_RECEIPT.json");
assert.equal(receipt.conservation.pass, true);
assert.equal(receipt.sealed_mechanism_evidence.direct_identity_join_to_development, false);

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

console.log("PASS test_window1_v50r_one_directional_price_discipline_package");
