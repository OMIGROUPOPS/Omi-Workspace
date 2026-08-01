#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const { completePairTupleSupport } = require("./window1_quote_shape_pair_wiring_v3.js");

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }

function main() {
  const args = process.argv.slice(2), get = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
  const repo = path.resolve(get("--repo", "."));
  const diagnosisPath = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_maker_insufficient_diagnosis_20260801/INSUFFICIENT_PREDICATE_DIAGNOSIS.json");
  const libraryPath = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_stable_ask_20260731/QUOTE_SHAPE_LIBRARY_LEAVE_FIVE_OUT.json");
  const outDir = path.resolve(get("--output", path.join(repo, ".claude/window1_live_v4_replay/pair_wiring_correction_20260801")));
  const diagnosis = JSON.parse(fs.readFileSync(diagnosisPath)), library = JSON.parse(fs.readFileSync(libraryPath));
  const byPair = new Map();
  for (const row of diagnosis.rows) {
    const key = row.pair_shape_tuple_context.key;
    if (!byPair.has(key)) byPair.set(key, row);
  }
  const closures = {};
  for (const [key, row] of byPair) {
    const [category, highRegion, lowRegion] = key.split("|");
    const highGroup = library.groups[`${category}|${highRegion}`], lowGroup = library.groups[`${category}|${lowRegion}`];
    if (!highGroup || !lowGroup) throw new Error(`missing marginal group for ${key}`);
    const completed = completePairTupleSupport({ observedTupleObject: library.pair_shape_tuples[key] || {}, highShapes: highGroup.shapes.map((shape) => shape.shape_id), lowShapes: lowGroup.shapes.map((shape) => shape.shape_id) });
    closures[key] = {
      observed_count: Object.keys(library.pair_shape_tuples[key] || {}).length,
      completed_count: completed.length,
      structural_rows: completed.filter((tuple) => tuple.support_class === "STRUCTURAL_INVERSE_CLOSURE"),
    };
  }
  const laj = diagnosis.rows.find((row) => row.leg_id === "LAJ"), van = diagnosis.rows.find((row) => row.leg_id === "VAN");
  const missingTuple = `${laj.terminal_evaluation.leg_surviving_shapes[0].shape_id}|${van.terminal_evaluation.leg_surviving_shapes[0].shape_id}`;
  const lajClosure = closures[laj.pair_shape_tuple_context.key];
  if (!lajClosure.structural_rows.some((row) => `${row.highShape}|${row.lowShape}` === missingTuple)) throw new Error(`LAJ/VAN tuple not restored: ${missingTuple}`);
  const predicateRows = diagnosis.rows.filter((row) => ["BRA", "VED", "JIM", "KOR"].includes(row.leg_id)).map((row) => ({
    event_id: row.event_id,
    category: row.category,
    price_region: row.price_region,
    leg_id: row.leg_id,
    timestamp_epoch: row.terminal_evaluation.timestamp_epoch,
    t_minus_scheduled_seconds: row.terminal_evaluation.t_minus_scheduled_seconds,
    t_minus_actual_bell_seconds: row.terminal_evaluation.t_minus_actual_bell_seconds,
    surviving_pair_tuple_count: row.terminal_evaluation.surviving_pair_tuple_count,
    surviving_shape: row.terminal_evaluation.pair_constrained_surviving_shapes[0]?.shape_id ?? null,
    own_micro_position_observed: row.terminal_evaluation.checks.own_micro_position_observed,
    own_micro_position_evidence_type: row.terminal_evaluation.micro_position_evidence_type,
    old_inverse_sibling_resolved: row.terminal_evaluation.checks.inverse_sibling_resolved,
    v3_inverse_sibling_proof_available: row.terminal_evaluation.surviving_pair_tuple_count === 1 && row.terminal_evaluation.checks.own_micro_position_observed,
    source_receipt: row.terminal_evaluation.source_receipt,
  }));
  if (predicateRows.length !== 4 || predicateRows.some((row) => !row.v3_inverse_sibling_proof_available)) throw new Error("four singleton predicate fixtures did not conserve");
  const receipt = {
    schema_version: "WINDOW1_PAIR_WIRING_CORRECTION_RECEIPT_V3",
    score_free: true,
    replay_executed: false,
    population_run_executed: false,
    defect_one: {
      affected_candidate_rows: 4,
      law_before: "Sibling direction had to be independently signed from a nonzero/zero own ask-net after an ask transition, even after the pair constraint had one inverse tuple left and both legs had own micro receipts.",
      law_after: "One inverse pair tuple may satisfy the sibling proof only if the sibling shape remains alive and the sibling has its own ask transition or stable-same-price micro receipt.",
      rows: predicateRows,
    },
    defect_two: {
      event_id: laj.event_id,
      pair_key: laj.pair_shape_tuple_context.key,
      observed_tuple_count: laj.pair_shape_tuple_context.initial_tuple_count,
      missing_terminal_tuple: missingTuple,
      old_terminal_tuple_count: 0,
      completed_library_contains_tuple: true,
      tuple_support_class: "STRUCTURAL_INVERSE_CLOSURE",
      tuple_empirical_count: 0,
      constraint: "Only inverse-compatible marginal shapes are added; observed tuples are retained unchanged and generated tuples never receive empirical n.",
      caveat: "This repairs sparse pair-denominator coverage. It is not validation that LAJ/VAN should be traded or that FLAT/FLAT predicts a floor.",
    },
    closure_by_category_and_price_region_pair: closures,
    sources: {
      diagnosis: { path: path.relative(repo, diagnosisPath).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(diagnosisPath)) },
      leave_five_out_library: { path: path.relative(repo, libraryPath).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(libraryPath)) },
    },
  };
  fs.mkdirSync(outDir, { recursive: true });
  const output = path.join(outDir, "PAIR_WIRING_CORRECTION_RECEIPT.json");
  fs.writeFileSync(output, canonical(receipt));
  fs.writeFileSync(path.join(outDir, "SOURCE_HASH_MANIFEST.json"), canonical({ schema_version: "WINDOW1_PAIR_WIRING_SOURCE_MANIFEST_V3", sources: receipt.sources }));
  const rawBase = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/pair_wiring_correction_20260801";
  fs.writeFileSync(path.join(outDir, "REPORT.md"), [
    "# Pair-wiring correction V3 — score-free specification",
    "",
    `Raw receipt: ${rawBase}/PAIR_WIRING_CORRECTION_RECEIPT.json`,
    "",
    "BRA, VED, JIM, and KOR each had one surviving inverse pair tuple and their own micro-position receipt. V2 nevertheless required a second independent direction sign. V3 accepts the singleton tuple only when the sibling shape remains alive and the sibling has its own later ask receipt.",
    "",
    `LAJ/VAN missing tuple: \`${missingTuple}\`. It is added with \`n=0\` and \`STRUCTURAL_INVERSE_CLOSURE\`; it is not relabeled empirical support.`,
    "",
    "No five-game replay was run because the upstream decision-time expected-close authority remains NOT_BOUND.",
    "",
  ].join("\n"));
  fs.writeFileSync(path.join(outDir, "DETERMINISM_RECEIPT.json"), canonical({ schema_version: "WINDOW1_PAIR_WIRING_DETERMINISM_RECEIPT_V3", canonical_json_lf: true, receipt_sha256: sha256(fs.readFileSync(output)), expected_rebuild_identity: "BYTE_IDENTICAL" }));
  const artifacts = fs.readdirSync(outDir).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort().map((name) => { const bytes = fs.readFileSync(path.join(outDir, name)); return { path: name, bytes: bytes.length, sha256: sha256(bytes) }; });
  fs.writeFileSync(path.join(outDir, "ARTIFACT_HASH_MANIFEST.json"), canonical({ schema_version: "WINDOW1_PAIR_WIRING_ARTIFACT_MANIFEST_V3", artifacts }));
  process.stdout.write(canonical({ status: "BUILT", predicate_rows: predicateRows.length, missing_tuple: missingTuple, output_sha256: sha256(fs.readFileSync(output)) }));
}

main();
