#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

function arg(name) { const index = process.argv.indexOf(`--${name}`); if (index < 0 || !process.argv[index + 1]) throw new Error(`missing --${name}`); return path.resolve(process.argv[index + 1]); }
function canonical(value) { return JSON.stringify(value, null, 2) + "\n"; }
function sha(file) { const digest = crypto.createHash("sha256"), fd = fs.openSync(file, "r"), buffer = Buffer.alloc(8 * 1024 * 1024); try { for (;;) { const count = fs.readSync(fd, buffer, 0, buffer.length, null); if (!count) break; digest.update(buffer.subarray(0, count)); } } finally { fs.closeSync(fd); } return digest.digest("hex"); }
function snapshot(root) { return Object.fromEntries(fs.readdirSync(root).filter((name) => name !== "DETERMINISM_RECEIPT.json").sort().map((name) => { const file = path.join(root, name), stat = fs.statSync(file); return [name, { sha256: sha(file), bytes: stat.size }]; })); }

const repo = arg("repo"), output = arg("output");
const builder = path.join(repo, "arb-executor", "analysis", "build_window1_v54_functionable_v6.js");
const forwardedNames = ["repo", "cache", "private", "walk", "output", "foundation-index", "foundation-receipt", "remote-receipt"];
const forwarded = forwardedNames.flatMap((name) => [`--${name}`, arg(name)]);
const runs = [];
for (let pass = 1; pass <= 2; pass += 1) {
  fs.mkdirSync(output, { recursive: true });
  for (const name of fs.readdirSync(output)) fs.rmSync(path.join(output, name), { recursive: true, force: true });
  const stdout = execFileSync(process.execPath, [builder, ...forwarded], { cwd: repo, encoding: "utf8", maxBuffer: 128 * 1024 * 1024 });
  runs.push({ pass, stdout_sha256: crypto.createHash("sha256").update(stdout).digest("hex"), files: snapshot(output) });
}
const namesEqual = JSON.stringify(Object.keys(runs[0].files)) === JSON.stringify(Object.keys(runs[1].files));
const differences = [...new Set([...Object.keys(runs[0].files), ...Object.keys(runs[1].files)])].filter((name) => JSON.stringify(runs[0].files[name]) !== JSON.stringify(runs[1].files[name]));
const receipt = {
  label: "V54_REPAIR_ITERATION3_DETERMINISM_X2",
  two_clean_builds: true,
  same_output_path_each_pass: true,
  names_equal: namesEqual,
  byte_identical: namesEqual && differences.length === 0 && runs[0].stdout_sha256 === runs[1].stdout_sha256,
  differences,
  policy_files: ["arb-executor/analysis/window1_v54_functionable_os.js", "arb-executor/analysis/build_window1_v54_functionable_v6.js"],
  passes: runs,
};
if (!receipt.byte_identical) throw new Error(`DETERMINISM_FAILED ${JSON.stringify(differences)}`);
const receiptPath = path.join(output, "DETERMINISM_RECEIPT.json");
fs.writeFileSync(receiptPath, canonical(receipt), "utf8");
const manifestPath = path.join(output, "ARTIFACT_HASH_MANIFEST.json"), manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8")), stat = fs.statSync(receiptPath);
manifest.files["DETERMINISM_RECEIPT.json"] = { path: "DETERMINISM_RECEIPT.json", sha256: sha(receiptPath), bytes: stat.size, rows: null };
fs.writeFileSync(manifestPath, canonical(manifest), "utf8");
process.stdout.write(canonical({ output, byte_identical: true, compared_files: Object.keys(runs[0].files).length, determinism_receipt: receiptPath }));
