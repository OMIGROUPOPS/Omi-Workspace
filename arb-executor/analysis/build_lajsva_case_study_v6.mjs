#!/usr/bin/env node
"use strict";

import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";

const REPAIR_ROOT = ".claude/window1_live_v4_replay/v54_composition_rebuild_mind_windowed_touch_priced_map_licensed_20260823";
const OUT_ROOT = ".claude/window1_live_v4_replay/lajsva_case_study_v8_20260823";
const PRIOR_ROOT = ".claude/window1_live_v4_replay/lajsva_case_study_v7_20260822";

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
    .replaceAll("CONDITIONAL_DIP_RECEIPT.json", "EVIDENCE_LADDER_RECEIPT.json")
    .replaceAll("V1_V2_V3_SIDE_BY_SIDE.md", "V1_V2_V3_V4_V5_V6_V7_V8_SIDE_BY_SIDE.md")
    .replaceAll("repair iteration 2", "composition rebuild")
    .replaceAll("Foundation + conditional dip + early riser", "mind-windowed, touch-priced, map-licensed composition")
    .replaceAll("this leg's own dip/no-dip state and the q50 remaining dip of same-state, native-bell-bounded MINUTE neighbors", "the mind-selected own-clock window, evidenced touch, and receipt-bound V3 map license")
    .replaceAll("LAJSVA v3", "LAJSVA v8")
    .replaceAll("v3 repaired machine", "v8 composition rebuild")
    .replaceAll("FOUNDATION_CONDITIONAL_DIP_EARLY_RISER", "MIND_WINDOW_TOUCH_MAP_LICENSE")
    .replaceAll("LAJSVA_CASE_STUDY_V3", "LAJSVA_CASE_STUDY_V8")
    .replaceAll("V3 receipt", "V8 receipt");
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "lajsva-v8-"));
  const generated = path.join(temp, "builder.mjs");
  fs.writeFileSync(generated, source, "utf8");
  try {
    execFileSync(process.execPath, [generated, repo], { cwd: repo, stdio: "pipe", maxBuffer: 64 * 1024 * 1024 });
  } finally {
    fs.rmSync(temp, { recursive: true, force: true });
  }

  const baseline = path.join(out, "TRADE_REPORT_BASELINE.md");
  const repair = path.join(out, "TRADE_REPORT_REPAIR.md");
  const reflex = path.join(out, "TRADE_REPORT_REFLEX.md");
  const pattern = path.join(out, "TRADE_REPORT_PATTERN_ENGINE.md");
  fs.renameSync(baseline, reflex);
  fs.renameSync(repair, pattern);

  const caseReceiptFile = path.join(out, "CASE_STUDY_RECEIPT.json");
  const caseReceipt = JSON.parse(fs.readFileSync(caseReceiptFile, "utf8"));
  const gateFile = path.join(repo, REPAIR_ROOT, "REPAIR_GATE_RECEIPT.json");
  const gate = JSON.parse(fs.readFileSync(gateFile, "utf8"));
  const priorReceiptFile = path.join(repo, PRIOR_ROOT, "CASE_STUDY_RECEIPT.json");
  const priorReceipt = JSON.parse(fs.readFileSync(priorReceiptFile, "utf8"));
  const result = caseReceipt.v1_v2_v3?.v3 ?? null;
  const prior = priorReceipt.v1_v2_v3_v4_v5_v6_v7?.v7 ?? null;
  const outcome = (value) => value?.completed ? `${value.pair_cents}, Δ${value.delta_cents}` : "partial";
  const spine = `# LAJSVA case-study spine — v1 / v2 / v3 / v4 / v5 / v6 / v7 / v8

| version | library / wiring | outcome | status |
|---|---|---|---|
| v1 | future-contaminated path lows; fill handoff absent | 41+53=94, Δ6 | certified outcome / broken reasoning |
| v2 | 698 bounded; 11,811 unbounded; fill receipts wired | LAJ 54 only | self-stopped |
| v3 | Foundation native-bell MINUTE store; binary conditional retrieval | partial | self-stopped |
| v4 | strict pre-bell minutes; subtractive graded retrieval; inert split | partial | self-stopped |
| v5 | composition + presence | ${outcome(prior)} | self-stopped |
| v6 | conditioned remaining-dip + own-window + pair-state derived depth | partial | self-stopped |
| v7 | evidence ladder: timed neighbors → neighbors+own-window → own tape → reflex | ${outcome(prior)} | banked prior |
| v8 | mind-selected own-clock windows; touch pricing; V3-map-licensed depth | ${outcome(result)} | ${gate.self_stop ? `self-stop: ${gate.stop_reason}` : "gate pass"} |

V7 receipt: ${PRIOR_ROOT}/CASE_STUDY_RECEIPT.json@sha256:${hash(fs.readFileSync(priorReceiptFile))}

V8 gate: ${REPAIR_ROOT}/REPAIR_GATE_RECEIPT.json@sha256:${hash(fs.readFileSync(gateFile))}
`;
  fs.writeFileSync(path.join(out, "V1_V2_V3_V4_V5_V6_V7_V8_SIDE_BY_SIDE.md"), spine, "utf8");
  caseReceipt.label = "LAJSVA_CASE_STUDY_V8_MIND_WINDOW_TOUCH_MAP_LICENSE";
  caseReceipt.v1_v2_v3_v4_v5_v6_v7_v8 = { v1: "COMPLETE_94_DELTA_6_BROKEN_REASONING", v2: "PARTIAL", v3: "PARTIAL", v4: "PARTIAL", v5: "COMPLETE_99_DELTA_1", v6: "PARTIAL", v7: prior, v8: result };
  delete caseReceipt.v1_v2_v3;
  caseReceipt.panel_b.cascade_shown_as_receipts = true;
  caseReceipt.scope.full_804_run = false;
  caseReceipt.report_file_law = {
    required: ["PANEL_A_PAIR_RENDER.html", "PANEL_B_ENGAGEMENT.html", "PANEL_C_TRADE_REPORTS.html", "TRADE_REPORT_REFLEX.md", "TRADE_REPORT_PATTERN_ENGINE.md", "CASE_STUDY_RECEIPT.json", "ARTIFACT_HASH_MANIFEST.json"],
    missing_is_self_stop: true,
  };
  fs.writeFileSync(caseReceiptFile, canonical(caseReceipt), "utf8");

  const required = caseReceipt.report_file_law.required.filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json");
  const missing = required.filter((name) => !fs.existsSync(path.join(out, name)));
  if (missing.length) throw new Error(`REPORT_FILE_LAW_SELF_STOP ${missing.join(",")}`);
  const determinismFile = path.join(out, "DETERMINISM_RECEIPT.json");
  fs.rmSync(determinismFile, { force: true });
  const names = fs.readdirSync(out).filter((name) => !["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"].includes(name)).sort();
  const rows = names.map((name) => receipt(repo, path.join(out, name)));
  const manifest = { label: "LAJSVA_CASE_STUDY_V8_MANIFEST", files: rows, required_paths_present: true, all_under_50_mb: rows.every((row) => row.bytes <= 50 * 1024 * 1024) };
  fs.writeFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), canonical(manifest), "utf8");
  const manifestHash = hash(fs.readFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json")));
  if (expected && expected !== manifestHash) throw new Error(`CASE_STUDY_V8_DETERMINISM_FAILED ${expected} != ${manifestHash}`);
  if (expected) {
    fs.writeFileSync(determinismFile, canonical({ label: "LAJSVA_CASE_STUDY_V8_DETERMINISM_X2", two_clean_builds: true, first_manifest_sha256: expected, second_manifest_sha256: manifestHash, byte_identical: true }), "utf8");
    const finalRows = [...rows, receipt(repo, determinismFile)];
    fs.writeFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), canonical({ label: "LAJSVA_CASE_STUDY_V8_MANIFEST", files: finalRows, required_paths_present: true, all_under_50_mb: finalRows.every((row) => row.bytes <= 50 * 1024 * 1024) }), "utf8");
  }
  process.stdout.write(canonical({ output: OUT_ROOT, result, self_stop: gate.self_stop, required_paths_present: true, manifest_sha256: manifestHash }));
}

main();
