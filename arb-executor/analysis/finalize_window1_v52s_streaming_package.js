#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const stream = require("stream/promises");
const zlib = require("zlib");

function ensure(value, message) { if (!value) throw new Error(message); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function fileHash(file) { return sha256(fs.readFileSync(file)); }
function writeManifest(dir) {
  const names = fs.readdirSync(dir).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(dir, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(names.map((name) => [name, { sha256: fileHash(path.join(dir, name)), bytes: fs.statSync(path.join(dir, name)).size }])) }));
}
async function writeRows(file, rows) {
  async function* encode() { for (const row of rows) yield `${JSON.stringify(row)}\n`; }
  await stream.pipeline(encode(), zlib.createGzip({ level: 9, mtime: 0 }), fs.createWriteStream(file));
}
async function finalize(dir) {
  const ledger = path.join(dir, "V52S_DEPTH_LIFT_AND_YIELD_LEDGER.json");
  const original = fs.readFileSync(ledger), payload = JSON.parse(original);
  const gz = path.join(dir, "V52S_DEPTH_LIFT_AND_YIELD_LEDGER.jsonl.gz");
  let source = null;
  if (Array.isArray(payload.rows)) {
    const rows = payload.rows;
    await writeRows(gz, rows);
    const summary = { rows_externalized_to: path.basename(gz), count: payload.count, by_kind: payload.by_kind, both_clocks_pass: payload.both_clocks_pass };
    ensure(summary.count === rows.length, `row conservation failed ${dir}`);
    fs.writeFileSync(ledger, canonical(summary));
    source = { sha256: sha256(original), bytes: original.length };
  }
  const summary = JSON.parse(fs.readFileSync(ledger));
  ensure(summary.rows_externalized_to === path.basename(gz) && fs.existsSync(gz), `streaming ledger absent ${dir}`);
  fs.writeFileSync(path.join(dir, "V52S_SERIALIZATION_RECEIPT.json"), canonical({ role: "MECHANICAL_STREAMING_GZIP_ONLY", row_ledger: path.basename(gz), summary: path.basename(ledger), rows: summary.count, policy_bytes_changed: false, decisions_changed: false, scores_changed: false }));
  const diffFile = path.join(dir, "ADDITIONS_ONLY_LANE_DIFF_RECEIPT.json"), diff = JSON.parse(fs.readFileSync(diffFile));
  diff.modified_registration_files = ["arb-executor/analysis/build_window1_v38_maker_only.js", "arb-executor/analysis/window1_v52r_exam_adapter.js"];
  diff.additions = ["arb-executor/analysis/window1_v52s_joint_budget_yield_priority.js", "arb-executor/analysis/window1_v52s_exam_adapter.js", "arb-executor/analysis/build_window1_v52s_joint_budget_yield_priority.js", "arb-executor/analysis/finalize_window1_v52s_streaming_package.js", "arb-executor/tests/test_window1_v52s_joint_budget_yield_priority.js", "arb-executor/docs/research/window1/V52S_JOINT_BUDGET_YIELD_PRIORITY_20260819_ADDENDUM.md", ".claude/window1_live_v4_replay/v52s_joint_budget_yield_priority_804_20260819/*"];
  fs.writeFileSync(diffFile, canonical(diff));
  return { dir, rows: summary.count, source_sha256: source?.sha256 ?? "ALREADY_EXTERNALIZED", source_bytes: source?.bytes ?? null, gzip_sha256: fileHash(gz), gzip_bytes: fs.statSync(gz).size };
}

async function main() {
  const dirs = process.argv.slice(2).map((value) => path.resolve(value));
  ensure(dirs.length === 2, "usage: finalize_window1_v52s_streaming_package.js BUILD_ONE BUILD_TWO");
  const scoreNames = ["TWO_RULER_SCORECARD.json", "V52S_MECHANISM_BAR.json", "V52S_KNIFE_EDGE_68_PRESERVATION.json", "V52S_JOINT_BUDGET_INVARIANT_RECEIPT.json", "V52S_EXPOSURE_DELTA.json", "PER_GAME_OUTCOME_TABLE.jsonl.gz"];
  const before = dirs.map((dir) => Object.fromEntries(scoreNames.map((name) => [name, fileHash(path.join(dir, name))])));
  const receipts = [];
  for (const dir of dirs) receipts.push(await finalize(dir));
  const after = dirs.map((dir) => Object.fromEntries(scoreNames.map((name) => [name, fileHash(path.join(dir, name))])));
  ensure(JSON.stringify(before) === JSON.stringify(after), "score artifact changed during serializer repair");
  const names = fs.readdirSync(dirs[0]).filter((name) => !["DETERMINISM_RECEIPT.json", "ARTIFACT_HASH_MANIFEST.json"].includes(name)).sort();
  const otherNames = fs.readdirSync(dirs[1]).filter((name) => !["DETERMINISM_RECEIPT.json", "ARTIFACT_HASH_MANIFEST.json"].includes(name)).sort();
  ensure(JSON.stringify(names) === JSON.stringify(otherNames), "package name sets differ after serializer repair");
  const mismatches = names.filter((name) => fileHash(path.join(dirs[0], name)) !== fileHash(path.join(dirs[1], name)));
  ensure(mismatches.length === 0, `serializer repair determinism mismatch: ${mismatches.join(",")}`);
  const determinism = { clean_builds: 2, compared_files: names.length, byte_identical: true, mismatches: [], post_build_serialization_repair: "MECHANICAL_STREAMING_GZIP_ONLY" };
  for (const dir of dirs) { fs.writeFileSync(path.join(dir, "DETERMINISM_RECEIPT.json"), canonical(determinism)); writeManifest(dir); }
  ensure(fileHash(path.join(dirs[0], "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(dirs[1], "ARTIFACT_HASH_MANIFEST.json")), "final manifests differ");
  process.stdout.write(canonical({ receipts, score_artifacts_unchanged: true, determinism, manifest_sha256: fileHash(path.join(dirs[0], "ARTIFACT_HASH_MANIFEST.json")) }));
}

main().catch((error) => { console.error(error.stack || String(error)); process.exitCode = 1; });
