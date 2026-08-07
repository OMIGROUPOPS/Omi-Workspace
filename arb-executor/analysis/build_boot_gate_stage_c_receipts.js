"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const cp = require("child_process");

function arg(name) {
  const i = process.argv.indexOf(name);
  if (i < 0 || !process.argv[i + 1]) throw new Error(`${name} required`);
  return process.argv[i + 1];
}
function sha(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}
function blob(repo, rel) {
  return cp.execFileSync("git", ["hash-object", rel], { cwd: repo, encoding: "utf8" }).trim();
}
function writeJson(file, value) {
  fs.writeFileSync(file, JSON.stringify(value, null, 2) + "\n", "utf8");
}

const repo = path.resolve(arg("--repo"));
const pkg = path.resolve(repo, arg("--package"));
const out = path.resolve(arg("--output"));
fs.mkdirSync(out, { recursive: true });

const sources = [
  "arb-executor/live_v4.py",
  "arb-executor/v36_shadow_brain.py",
  "arb-executor/analysis/window1_v29r3_standing_floor_release_policy.js",
  "arb-executor/analysis/window1_v32_no_chase_state_machine.js",
  "arb-executor/analysis/window1_v34_dual_side_residency_machine.js",
  "arb-executor/analysis/window1_v35_living_rest_evidence_gate.js",
  "arb-executor/analysis/window1_v36_state_directional_rest_mature_floor.js",
  "arb-executor/tests/test_exit_cell_fail_loud.py",
  "arb-executor/tests/test_stage_c_v36_shadow.py",
  "arb-executor/tests/test_window1_v29r3_standing_floor_release_policy.js",
  "arb-executor/tests/test_boot_gate_stage_c_cutover_prep.js",
  "arb-executor/analysis/build_boot_gate_stage_c_receipts.js",
];
const sourceRows = sources.map((rel) => {
  const file = path.join(repo, rel);
  return { path: rel, bytes: fs.statSync(file).size, sha256: sha(file), git_blob: blob(repo, rel) };
});
writeJson(path.join(out, "SOURCE_HASH_MANIFEST.json"), {
  schema_version: "stage-c-source-hash-manifest-v1",
  runtime_commit: "896de4108a855abb75fd6bc31330445579f2f2fb",
  files: sourceRows,
});

const ignored = new Set(["SOURCE_HASH_MANIFEST.json", "ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"]);
const artifactRows = fs.readdirSync(pkg).filter((name) => !ignored.has(name)).sort().map((name) => {
  const file = path.join(pkg, name);
  return { path: name, bytes: fs.statSync(file).size, sha256: sha(file) };
});
writeJson(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), {
  schema_version: "stage-c-artifact-hash-manifest-v1",
  files: artifactRows,
});
console.log(JSON.stringify({ status: "PASS", source_files: sourceRows.length, artifacts: artifactRows.length }));
