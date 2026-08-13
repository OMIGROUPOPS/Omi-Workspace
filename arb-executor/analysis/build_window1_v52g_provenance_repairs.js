#!/usr/bin/env node
"use strict";

const child = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const ONSET_FORENSICS_COMMIT = "68a58029c0a6b84eda7750b185861f75d381cd49";
const ONSET_FORENSICS_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/ONSET_FORENSICS_113.json";
const V52E_EXAM_COMMIT = "4716657a18519d5b90705eb20030a66f5491a91b";
const V52E_EVENT_LEDGER_PATH = ".claude/window1_live_v4_replay/v52e_disposition_804_four_state_20260813/MARKET_EVENT_LEDGER_804.jsonl.gz";
const DEFAULT_OUTPUT = ".claude/window1_live_v4_replay/v52g_provenance_repairs_20260813";

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const index = argv.indexOf(name); return index < 0 ? fallback : argv[index + 1]; };
const repo = path.resolve(arg("--repo", "."));
const output = path.resolve(arg("--output", path.join(repo, DEFAULT_OUTPUT)));
const compare = arg("--compare", null) ? path.resolve(arg("--compare", null)) : null;

function ensure(value, message) { if (!value) throw new Error(message); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function fileHash(file) { return sha256(fs.readFileSync(file)); }
function gitShow(commit, objectPath) { return child.execFileSync("git", ["show", `${commit}:${objectPath}`], { cwd: repo, maxBuffer: 1024 * 1024 * 1024 }); }
function gitObjectType(commit) { return child.execFileSync("git", ["cat-file", "-t", commit], { cwd: repo, encoding: "utf8" }).trim(); }
function gitHead() { return child.execFileSync("git", ["rev-parse", "HEAD"], { cwd: repo, encoding: "utf8" }).trim(); }
function lineOf(relativePath, fragment) {
  const lines = fs.readFileSync(path.join(repo, relativePath), "utf8").split(/\r?\n/);
  const index = lines.findIndex((line) => line.includes(fragment));
  ensure(index >= 0, `line anchor missing ${relativePath}: ${fragment}`);
  return index + 1;
}
function gzipRows(rows) {
  const body = rows.map((row) => JSON.stringify(row)).join("\n");
  return zlib.gzipSync(Buffer.from(`${body}${body ? "\n" : ""}`), { level: 9, mtime: 0 });
}
function readGzipRows(bytes) {
  const text = zlib.gunzipSync(bytes).toString("utf8").trim();
  return text ? text.split("\n").map(JSON.parse) : [];
}
function write(name, bytes) { fs.writeFileSync(path.join(output, name), bytes); }
function safeOutput(dir) {
  ensure(path.basename(dir).includes("v52g_provenance_repairs"), `unsafe output ${dir}`);
  ensure(dir !== repo && dir !== path.parse(dir).root, `unsafe output ${dir}`);
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
}

function nestedLeg(forensics, code, leg) {
  const game = forensics.rows.find((row) => row.code === code);
  ensure(game?.legs?.[leg], `onset row missing ${code}|${leg}`);
  return { game, row: game.legs[leg] };
}

function buildOnsetReceipts(bytes) {
  const source = JSON.parse(bytes.toString("utf8"));
  ensure(source.summary?.agree === 199 && source.summary?.disagree === 27, "onset divergence conservation changed");
  ensure(source.divergent_legs?.length === 27, "expected 27 divergent onset legs");
  const reattested = source.divergent_legs.map((item) => {
    const { game, row } = nestedLeg(source, item.code, item.leg);
    ensure(row.runtime_onset_ts === item.runtime && row.census_sel === item.census, `divergent identity mismatch ${item.code}|${item.leg}`);
    return {
      code: item.code,
      event_category: game.cat,
      leg: item.leg,
      canonical_input_grain: "RUNTIME_MATERIALIZED_RECEIPT_STREAM_RESAMPLED_BY_FROZEN_60_SECOND_ONSET_ADAPTER",
      canonical_onset_timestamp_epoch: item.runtime,
      canonical_candidate: row.runtime_cand,
      first_runtime_receipt_at_or_after_onset_epoch: row.runtime_first_passed,
      fit_local_minute_grid_onset_timestamp_epoch: item.census,
      canonical_minus_rejected_grid_seconds: item.runtime - item.census,
      reattested: true,
      behavior_changed: false,
    };
  }).sort((a, b) => a.code.localeCompare(b.code) || a.leg.localeCompare(b.leg));
  const sleeper = [];
  for (const game of source.rows) {
    for (const [leg, row] of Object.entries(game.legs)) {
      if (!(Number.isFinite(row.floor_first_print_tmin) && Number.isFinite(row.runtime_passed_tmin) && row.floor_first_print_tmin < row.runtime_passed_tmin)) continue;
      sleeper.push({
        code: game.code,
        event_category: game.cat,
        leg,
        offered_floor_cents: row.floor,
        offered_floor_first_print_tmin: row.floor_first_print_tmin,
        canonical_runtime_onset_tmin: row.runtime_passed_tmin,
        rejected_fit_grid_onset_tmin: row.onset_tmin,
        reachable_under_canonical_runtime_input: row.floor_first_print_tmin >= row.runtime_passed_tmin,
        reachable_under_rejected_fit_grid_counterfactual: row.floor_first_print_tmin >= row.onset_tmin,
        canonical_sleep_seconds: Math.round((row.runtime_passed_tmin - row.floor_first_print_tmin) * 60),
      });
    }
  }
  sleeper.sort((a, b) => a.code.localeCompare(b.code) || a.leg.localeCompare(b.leg));
  ensure(sleeper.length === 11, `expected 11 sleeper offers, found ${sleeper.length}`);
  ensure(sleeper.every((row) => !row.reachable_under_canonical_runtime_input), "canonical runtime input unexpectedly reaches a sleeper offer");
  ensure(sleeper.every((row) => row.reachable_under_rejected_fit_grid_counterfactual), "rejected grid counterfactual does not reach every sleeper offer");
  const receipt = {
    label: "V52G_PART1_ONSET_INPUT_GRAIN_UNIFICATION_RECEIPT",
    repair_class: "RECEIPTS_ONLY_NO_POLICY_OR_SCORE_CHANGE",
    controlling_source: { commit: ONSET_FORENSICS_COMMIT, path: ONSET_FORENSICS_PATH, sha256: sha256(bytes), bytes: bytes.length },
    canonical_choice: {
      input: "RUNTIME_MATERIALIZED_RECEIPT_STREAM_RESAMPLED_BY_FROZEN_60_SECOND_ONSET_ADAPTER",
      reason: "This is the only input available to the executing machine at receipt grain and preserves frozen clause 1. The fit-local minute grid is an analysis reconstruction and is not substituted into the decision path.",
      frozen_onset_code: "arb-executor/analysis/window1_v52_stability_onset.js",
      behavior_changed: false,
    },
    conservation: {
      legs_in_source: 226,
      canonical_agreements: 199,
      divergent_legs_reattested: reattested.length,
      total: 199 + reattested.length,
      pass: 199 + reattested.length === 226 && reattested.every((row) => row.reattested),
    },
    sleeper_offers: {
      source_count: sleeper.length,
      become_reachable_under_canonical_runtime_input: sleeper.filter((row) => row.reachable_under_canonical_runtime_input).map((row) => `${row.code}|${row.leg}`),
      become_reachable_only_under_rejected_fit_grid_counterfactual: sleeper.filter((row) => row.reachable_under_rejected_fit_grid_counterfactual).map((row) => `${row.code}|${row.leg}`),
      ruling: "ZERO_RETROACTIVE_REACHABILITY; ALL_ELEVEN_REMAIN_HISTORICAL_SLEEPER_OFFERS_UNDER_THE_FROZEN_RUNTIME_INPUT",
    },
  };
  return { receipt, reattested, sleeper };
}

function buildMissingBlockReceipts(bytes) {
  const events = readGzipRows(bytes);
  ensure(events.length === 804, `expected V52e event ledger D=804, found ${events.length}`);
  const targets = events.filter((event) => /MATMOR|CORSAC/.test(event.event_id)).sort((a, b) => a.event_id.localeCompare(b.event_id));
  ensure(targets.length === 2, `expected MATMOR and CORSAC, found ${targets.length}`);
  const sourcePath = "arb-executor/analysis/build_window1_v38_maker_only.js";
  const lines = {
    span_bound_without_order_validation: lineOf(sourcePath, "left: span.w1_left_epoch, right: span.w1_right_epoch"),
    replay_receipt_loop_entry: lineOf(sourcePath, "for (const base of replayBases)"),
    gate_block_counter_only_inside_decision_receipt: lineOf(sourcePath, "leg.judgment_gate_blocks[failure]"),
    terminal_reason_without_gate_block: lineOf(sourcePath, "leg.terminal_reason = leg.decision_count === 0"),
  };
  const rows = [];
  for (const event of targets) {
    ensure(event.w1_left_epoch > event.w1_right_epoch, `${event.event_id} span is no longer inverted`);
    for (const leg of Object.values(event.legs).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity))) {
      ensure(leg.decision_rows === 0 && Object.keys(leg.block_counts ?? {}).length === 0, `${leg.leg_identity} no longer has the missing-record fingerprint`);
      rows.push({
        record_type: "TERMINAL_GATE_BLOCK_PROVENANCE",
        event_id: event.event_id,
        leg_identity: leg.leg_identity,
        ticker: leg.ticker,
        category: event.category,
        price_region: event.starting_price_split,
        gate_verdict: "NO_GATE_EVALUATION",
        blocked_clause: "PRE_MATCH_SPAN_INVALID_LEFT_AFTER_RIGHT",
        compared_values: { w1_left_epoch: event.w1_left_epoch, w1_right_epoch: event.w1_right_epoch, left_minus_right_seconds: event.w1_left_epoch - event.w1_right_epoch },
        decision_receipts: leg.decision_rows,
        prior_gate_block_records: Object.keys(leg.block_counts ?? {}).length,
        terminal_reason: leg.terminal_reason,
        score_or_policy_changed: false,
        recording_repair: "SYNTHESIZED_TERMINAL_PROVENANCE_ROW_NOT_A_FABRICATED_GATE_EVALUATION",
      });
    }
  }
  ensure(rows.length === 4, `expected four repaired leg records, found ${rows.length}`);
  const receipt = {
    label: "V52G_PART1_MATMOR_CORSAC_MISSING_GATE_BLOCK_RECORDING_REPAIR",
    repair_class: "RECEIPTS_ONLY_NO_POLICY_OR_SCORE_CHANGE",
    controlling_source: { commit: V52E_EXAM_COMMIT, path: V52E_EVENT_LEDGER_PATH, sha256: sha256(bytes), bytes: bytes.length, events: events.length },
    root_cause: {
      exact: "Both events bind w1_left_epoch later than w1_right_epoch. The simulator therefore consumes zero in-span two-sided-book receipts. Gate-block counters exist only inside the decision-receipt branch; terminalization assigns NO_TWO_SIDED_BOOK_DECISION_INSIDE_EDGE but emits no gate-block row.",
      source_file: sourcePath,
      lines,
      defect_class: "EXPORT_RECORDING_HOLE_AFTER_INVALID_PRE_MATCH_SPAN",
      policy_evaluation_occurred: false,
    },
    repair: {
      row_type: "TERMINAL_GATE_BLOCK_PROVENANCE",
      semantics: "Records why no gate evaluation was possible. It does not claim PASS, FLAG, or any evaluated predicate.",
      rows: rows.length,
      affected_events: targets.map((event) => event.event_id),
      behavior_changed: false,
      scores_changed: false,
    },
    conservation: { events: 2, legs: 4, emitted_rows: rows.length, exactly_one_row_per_affected_leg: new Set(rows.map((row) => row.leg_identity)).size === 4, pass: rows.length === 4 },
  };
  return { receipt, rows };
}

function manifest() {
  const files = fs.readdirSync(output).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  return { files: Object.fromEntries(files.map((name) => [name, { sha256: fileHash(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size }])) };
}

function main() {
  ensure(gitObjectType(ONSET_FORENSICS_COMMIT) === "commit", "onset commit is not a commit");
  ensure(gitObjectType(V52E_EXAM_COMMIT) === "commit", "V52e exam commit is not a commit");
  safeOutput(output);
  const onsetBytes = gitShow(ONSET_FORENSICS_COMMIT, ONSET_FORENSICS_PATH);
  const examBytes = gitShow(V52E_EXAM_COMMIT, V52E_EVENT_LEDGER_PATH);
  const onset = buildOnsetReceipts(onsetBytes);
  const missing = buildMissingBlockReceipts(examBytes);
  write("ONSET_INPUT_GRAIN_UNIFICATION_RECEIPT.json", canonical(onset.receipt));
  write("ONSET_DIVERGENT_27_REATTESTATION.jsonl.gz", gzipRows(onset.reattested));
  write("SLEEPER_OFFER_REACHABILITY_RECEIPT.json", canonical({ label: "SLEEPER_OFFER_REACHABILITY_UNDER_CANONICAL_INPUT", rows: onset.sleeper, conservation: { rows: onset.sleeper.length, canonical_reachable: onset.sleeper.filter((row) => row.reachable_under_canonical_runtime_input).length, rejected_grid_counterfactual_reachable: onset.sleeper.filter((row) => row.reachable_under_rejected_fit_grid_counterfactual).length, pass: onset.sleeper.length === 11 } }));
  write("MATMOR_CORSAC_MISSING_GATE_BLOCK_REPAIR.json", canonical(missing.receipt));
  write("MATMOR_CORSAC_REEMITTED_GATE_BLOCK_ROWS.jsonl.gz", gzipRows(missing.rows));
  write("CONTROL_BINDING.json", canonical({ head_at_build: gitHead(), scope: "PART_1_PROVENANCE_REPAIRS_ONLY", policy_changed: false, score_changed: false, V52g_iteration_6_executed: false }));
  const report = `# V52g Part 1 — provenance repairs only\n\nThe canonical onset input is the runtime materialized receipt stream resampled by the frozen 60-second onset adapter. All 27 divergent legs are re-attested to that input. Zero of the eleven sleeper offers becomes retroactively reachable; all eleven would become reachable only under the rejected fit-local minute-grid counterfactual, which would change frozen clause 1.\n\nMATMOR and CORSAC each have an inverted pre-match span (left later than right). No gate evaluation occurred. Four terminal provenance rows now state that fact explicitly without fabricating a gate result. Policy bytes and score artifacts are unchanged. V52g Iteration 6 has not run.\n`;
  write("REPORT.md", report);
  const filesBeforeDeterminism = fs.readdirSync(output).sort();
  let determinism = { clean_builds: 1, byte_identical: null, role: "FIRST_BUILD" };
  if (compare) {
    const mismatches = filesBeforeDeterminism.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name)));
    const extra = fs.readdirSync(compare).filter((name) => ![...filesBeforeDeterminism, "DETERMINISM_RECEIPT.json", "ARTIFACT_HASH_MANIFEST.json"].includes(name));
    ensure(!mismatches.length && !extra.length, `determinism mismatch ${[...mismatches, ...extra].join(",")}`);
    determinism = { clean_builds: 2, compared_files: filesBeforeDeterminism.length, byte_identical: true, mismatches: [] };
  }
  write("DETERMINISM_RECEIPT.json", canonical(determinism));
  write("ARTIFACT_HASH_MANIFEST.json", canonical(manifest()));
  if (compare) {
    fs.writeFileSync(path.join(compare, "DETERMINISM_RECEIPT.json"), canonical(determinism));
    fs.writeFileSync(path.join(compare, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(fs.readdirSync(compare).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort().map((name) => [name, { sha256: fileHash(path.join(compare, name)), bytes: fs.statSync(path.join(compare, name)).size }])) }));
    ensure(fileHash(path.join(compare, "ARTIFACT_HASH_MANIFEST.json")) === fileHash(path.join(output, "ARTIFACT_HASH_MANIFEST.json")), "final artifact manifests differ");
  }
  process.stdout.write(canonical({ output, onset: onset.receipt.conservation, sleeper: onset.receipt.sleeper_offers, missing_block: missing.receipt.conservation, determinism }));
}

main();
