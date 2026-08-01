#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(data) { return crypto.createHash("sha256").update(data).digest("hex"); }
function digest(file) { const bytes = fs.readFileSync(file); return { bytes: bytes.length, sha256: sha256(bytes) }; }

const args = process.argv.slice(2), value = (name) => { const index = args.indexOf(name); if (index < 0 || !args[index + 1]) throw new Error(`missing ${name}`); return path.resolve(args[index + 1]); };
const left = value("--left"), right = value("--right");
const leftNames = fs.readdirSync(left).filter((name) => name !== "DETERMINISM_RECEIPT.json").sort(), rightNames = fs.readdirSync(right).filter((name) => name !== "DETERMINISM_RECEIPT.json").sort();
if (canonical(leftNames) !== canonical(rightNames)) throw new Error("artifact name mismatch");
const artifacts = {};
for (const name of leftNames) {
  const l = digest(path.join(left, name)), r = digest(path.join(right, name));
  if (l.bytes !== r.bytes || l.sha256 !== r.sha256) throw new Error(`determinism mismatch: ${name}`);
  artifacts[name] = l;
}
const receipt = { schema_version: "WINDOW1_EXPECTED_CLOSE_DETERMINISM_RECEIPT_V1", clean_builds: 2, byte_identical: true, compared_artifacts: leftNames.length, artifacts, second_build_disposition: "TEMPORARY_VALIDATION_OUTPUT_NOT_COMMITTED" };
fs.writeFileSync(path.join(left, "DETERMINISM_RECEIPT.json"), canonical(receipt));
const manifestFile = path.join(left, "ARTIFACT_HASH_MANIFEST.json"), manifest = JSON.parse(fs.readFileSync(manifestFile));
manifest.artifacts["DETERMINISM_RECEIPT.json"] = digest(path.join(left, "DETERMINISM_RECEIPT.json"));
fs.writeFileSync(manifestFile, canonical(manifest));
process.stdout.write(canonical({ status: "PASS", clean_builds: 2, byte_identical: true, compared_artifacts: leftNames.length, receipt_sha256: digest(path.join(left, "DETERMINISM_RECEIPT.json")).sha256 }));
