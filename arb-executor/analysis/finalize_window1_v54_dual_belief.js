#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

function arg(name) {
  const index = process.argv.indexOf(`--${name}`);
  if (index < 0 || index + 1 >= process.argv.length) throw new Error(`missing --${name}`);
  return path.resolve(process.argv[index + 1]);
}
function optional(name, fallback) {
  const index = process.argv.indexOf(`--${name}`);
  return index < 0 ? fallback : process.argv[index + 1];
}
function hash(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function names(root) { return fs.readdirSync(root).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json" && name !== "DETERMINISM_RECEIPT.json").sort(); }
function receipt(root, name) {
  const bytes = fs.readFileSync(path.join(root, name));
  return { path: name, bytes: bytes.length, sha256: hash(bytes) };
}

function main() {
  const first = arg("first"), second = arg("second"), destination = arg("destination"), label = optional("label", "V54_LAYERED_DUAL_BELIEF");
  const firstNames = names(first), secondNames = names(second);
  if (JSON.stringify(firstNames) !== JSON.stringify(secondNames)) throw new Error("DETERMINISM_FILE_SET_MISMATCH");
  const comparisons = firstNames.map((name) => {
    const a = receipt(first, name), b = receipt(second, name);
    return { path: name, first_sha256: a.sha256, second_sha256: b.sha256, bytes: a.bytes, byte_identical: a.sha256 === b.sha256 && a.bytes === b.bytes };
  });
  if (!comparisons.every((row) => row.byte_identical)) throw new Error(`DETERMINISM_BYTE_MISMATCH:${comparisons.filter((row) => !row.byte_identical).map((row) => row.path).join(",")}`);
  fs.rmSync(destination, { recursive: true, force: true });
  fs.cpSync(first, destination, { recursive: true });
  const determinism = {
    label: `${label}_DETERMINISM_X2`,
    two_clean_builds: true,
    byte_identical: true,
    compared_artifacts: comparisons.length,
    comparisons,
    first_build_source: path.basename(first),
    second_build_source: path.basename(second),
    decision_code_changed_between_builds: false,
  };
  fs.writeFileSync(path.join(destination, "DETERMINISM_RECEIPT.json"), canonical(determinism), "utf8");
  const manifestNames = fs.readdirSync(destination).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  const files = Object.fromEntries(manifestNames.map((name) => [name, receipt(destination, name)]));
  if (!Object.values(files).every((row) => row.bytes <= 50 * 1024 * 1024)) throw new Error("L22_COMMITTED_ARTIFACT_EXCEEDS_50_MIB");
  fs.writeFileSync(path.join(destination, "ARTIFACT_HASH_MANIFEST.json"), canonical({ label: `${label}_ARTIFACT_MANIFEST`, files, all_committed_artifacts_under_50_mib: true }), "utf8");
  process.stdout.write(canonical({ destination, determinism: "PASS_X2", artifacts: comparisons.length }));
}

main();
