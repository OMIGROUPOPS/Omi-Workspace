#!/usr/bin/env node
"use strict";

import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";

const REPAIR_ROOT = ".claude/window1_live_v4_replay/v54_repair_iteration3_split_graded_retrieval_20260822";
const OUT_ROOT = ".claude/window1_live_v4_replay/lajsva_case_study_v4_20260822";
const V3_ROOT = ".claude/window1_live_v4_replay/lajsva_case_study_v3_20260822";

function canonical(value) { return JSON.stringify(value, null, 2) + "\n"; }
function hash(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function receipt(repo, file) { const bytes = fs.readFileSync(file); return { path: path.relative(repo, file).replaceAll("\\", "/"), bytes: bytes.length, sha256: hash(bytes) }; }

function main() {
  const repo = path.resolve(process.argv[2] ?? process.cwd());
  const expected = process.argv[3] ?? null;
  const templateFile = path.join(repo, "arb-executor", "analysis", "build_lajsva_case_study_v3.mjs");
  const out = path.join(repo, OUT_ROOT);
  fs.rmSync(out, { recursive: true, force: true });

  let source = fs.readFileSync(templateFile, "utf8");
  source = source
    .replace('const REPAIR_ROOT = ".claude/window1_live_v4_replay/v54_repair_iteration2_foundation_conditional_dip_early_riser_20260822";', `const REPAIR_ROOT = "${REPAIR_ROOT}";`)
    .replace('const OUT_ROOT = ".claude/window1_live_v4_replay/lajsva_case_study_v3_20260822";', `const OUT_ROOT = "${OUT_ROOT}";`)
    .replaceAll("V1_V2_V3_SIDE_BY_SIDE.md", "V1_V2_V3_V4_SIDE_BY_SIDE.md")
    .replaceAll("repair iteration 2", "repair iteration 3")
    .replaceAll("LAJSVA v3", "LAJSVA v4")
    .replaceAll("v3 repaired machine", "v4 repaired machine")
    .replaceAll("FOUNDATION_CONDITIONAL_DIP_EARLY_RISER", "SPLIT_GRADED_RETRIEVAL")
    .replaceAll("LAJSVA_CASE_STUDY_V3", "LAJSVA_CASE_STUDY_V4")
    .replaceAll("V3 receipt", "V4 receipt");
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "lajsva-v4-"));
  const generated = path.join(temp, "builder.mjs");
  fs.writeFileSync(generated, source, "utf8");
  try {
    execFileSync(process.execPath, [generated, repo], { cwd: repo, stdio: "pipe", maxBuffer: 64 * 1024 * 1024 });
  } finally {
    fs.rmSync(temp, { recursive: true, force: true });
  }

  const caseReceiptFile = path.join(out, "CASE_STUDY_RECEIPT.json");
  const caseReceipt = JSON.parse(fs.readFileSync(caseReceiptFile, "utf8"));
  const gate = JSON.parse(fs.readFileSync(path.join(repo, REPAIR_ROOT, "REPAIR_GATE_RECEIPT.json"), "utf8"));
  const v3ReceiptFile = path.join(repo, V3_ROOT, "CASE_STUDY_RECEIPT.json");
  const v3 = JSON.parse(fs.readFileSync(v3ReceiptFile, "utf8"));
  const result = caseReceipt.v1_v2_v3?.v3 ?? caseReceipt.v1_v2_v3_v4?.v4 ?? null;
  const spine = `# LAJSVA case-study spine — v1 / v2 / v3 / v4

| version | library / wiring | outcome | status |
|---|---|---|---|
| v1 | future-contaminated path lows; fill handoff absent | 41+53=94, Δ6 | certified outcome / broken reasoning |
| v2 | 698 bounded; 11,811 unbounded; fill receipts wired | LAJ 54 only | self-stopped |
| v3 | Foundation native-bell MINUTE store; binary conditional retrieval | ${v3.v1_v2_v3?.v3?.completed ? `${v3.v1_v2_v3.v3.pair_cents}, Δ${v3.v1_v2_v3.v3.delta_cents}` : "partial"} | ${v3.self_stop ? "self-stopped" : "gate pass"} |
| v4 | strict pre-bell trade minutes; continuous graded retrieval; derived live-window split | ${result?.completed ? `${result.pair_cents}, Δ${result.delta_cents}` : "partial"} | ${gate.self_stop ? `self-stop: ${gate.stop_reason}` : "gate pass"} |

V3 receipt: ${V3_ROOT}/CASE_STUDY_RECEIPT.json@sha256:${hash(fs.readFileSync(v3ReceiptFile))}

V4 gate: ${REPAIR_ROOT}/REPAIR_GATE_RECEIPT.json@sha256:${hash(fs.readFileSync(path.join(repo, REPAIR_ROOT, "REPAIR_GATE_RECEIPT.json")))}
`;
  fs.writeFileSync(path.join(out, "V1_V2_V3_V4_SIDE_BY_SIDE.md"), spine, "utf8");
  caseReceipt.label = "LAJSVA_CASE_STUDY_V4_SPLIT_GRADED_RETRIEVAL";
  caseReceipt.v1_v2_v3_v4 = { v1: "COMPLETE_94_DELTA_6_BROKEN_REASONING", v2: "PARTIAL", v3: v3.v1_v2_v3?.v3 ?? null, v4: result };
  delete caseReceipt.v1_v2_v3;
  caseReceipt.panel_b.cascade_shown_as_receipts = true;
  caseReceipt.scope.full_804_run = false;
  fs.writeFileSync(caseReceiptFile, canonical(caseReceipt), "utf8");

  const determinismFile = path.join(out, "DETERMINISM_RECEIPT.json");
  fs.rmSync(determinismFile, { force: true });
  const names = fs.readdirSync(out).filter((name) => !["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"].includes(name)).sort();
  const rows = names.map((name) => receipt(repo, path.join(out, name)));
  const manifest = { label: "LAJSVA_CASE_STUDY_V4_MANIFEST", files: rows, all_under_50_mb: rows.every((row) => row.bytes <= 50 * 1024 * 1024) };
  fs.writeFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), canonical(manifest), "utf8");
  const manifestHash = hash(fs.readFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json")));
  if (expected && expected !== manifestHash) throw new Error(`CASE_STUDY_V4_DETERMINISM_FAILED ${expected} != ${manifestHash}`);
  if (expected) {
    fs.writeFileSync(determinismFile, canonical({ label: "LAJSVA_CASE_STUDY_V4_DETERMINISM_X2", two_clean_builds: true, first_manifest_sha256: expected, second_manifest_sha256: manifestHash, byte_identical: true }), "utf8");
    const finalRows = [...rows, receipt(repo, determinismFile)];
    fs.writeFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), canonical({ label: "LAJSVA_CASE_STUDY_V4_MANIFEST", files: finalRows, all_under_50_mb: finalRows.every((row) => row.bytes <= 50 * 1024 * 1024) }), "utf8");
  }
  process.stdout.write(canonical({ output: OUT_ROOT, result, self_stop: gate.self_stop, manifest_sha256: manifestHash }));
}

main();
