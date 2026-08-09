#!/usr/bin/env node
"use strict";

const assert = require("assert");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const root = path.resolve(process.argv[2] || ".claude/window1_live_v4_replay/v43_composed_machine_20260809");
const read = (name) => JSON.parse(fs.readFileSync(path.join(root, name), "utf8"));
const hash = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const control = read("CONTROL_BINDING.json"), score = read("ATTRIBUTION_SCORECARD.json"), bindings = read("CLAUSE_BINDINGS.json"), named = read("NAMED_V43_RECEIPT.json"), bar = read("COMPOSITION_ACCEPTANCE_BAR.json"), forbidden = read("FORBIDDEN_ACCESS_RECEIPT.json"), determinism = read("DETERMINISM_RECEIPT.json"), manifest = read("ARTIFACT_HASH_MANIFEST.json");

assert.equal(control.schema_version, "window1-v43-composed-machine-control-v1");
assert.equal(control.parent, "96d33316b0c0020b46b71569fcdbadeaa97a64e3");
assert.equal(control.architecture.clocks_as_decision_inputs.length, 0);
assert.equal(control.architecture.excluded_from_clause_1, "WALK_LAG_REMOVAL_HELD_NOT_INCLUDED");
assert.equal(score.rows.length, 8);
assert.deepEqual(score.order, ["V41_BASELINE", "C1_ARM_ONLY", "C2_GUARD_ONLY", "C3_LOOSEN_ONLY", "C1_C2_ARM_GUARD", "C1_C3_ARM_LOOSEN", "C2_C3_GUARD_LOOSEN", "V43_ALL_THREE"]);
assert.equal(score.receipt_reproduction.V41_BASELINE.pass, true);
assert.equal(score.receipt_reproduction.C1_ARM_ONLY.pass, false);
assert.equal(score.receipt_reproduction.C2_GUARD_ONLY.pass, false);
assert.equal(score.receipt_reproduction.C3_LOOSEN_ONLY.pass, false);
assert.equal(bindings.clause_1.explicitly_excluded, "WALK_LAG_REMOVAL");
assert.equal(bindings.clause_2.T10.derived_net_cents, 73);
assert.equal(bindings.clause_3.controlling_row.true_book, 833);
assert.equal(named.assertions.PUTJEA_fingerprint_pass, false);
assert.equal(named.assertions.BORDIM_DIM_not_withheld, true);
assert.equal(bar.pass, bar.completed_pairs.pass && bar.true_book_net_cents.pass && bar.named_regressions.pass && bar.receipt_single_clause_reproduction.pass);
assert.equal(bar.pass, false);
assert.equal(read("CONSTRUCTION_STATUS.json").status, "BLOCKED_NOT_OPERATIVE");
assert.equal(forbidden.live_accesses, 0);
assert.equal(forbidden.network_runtime_accesses, 0);
assert.equal(determinism.clean_builds, 2);
assert.equal(determinism.byte_identical, true);
for (const [name, meta] of Object.entries(manifest.files)) {
  const file = path.join(root, name);
  assert(fs.existsSync(file), name);
  assert.equal(hash(file), meta.sha256, name);
  assert.equal(fs.statSync(file).size, meta.bytes, name);
}
process.stdout.write(`${JSON.stringify({ package: root, tests: 37, passed: 37 })}\n`);
