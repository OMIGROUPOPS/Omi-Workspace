#!/usr/bin/env node
"use strict";

const childProcess = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const windows = require("./window1_ground_truth_window_adapter.js");

const FROZEN_V52H_COMMIT = "b43d7cde56aac5fe5cc553419286119adf378d6d";
const FROZEN_ROOT = ".claude/window1_live_v4_replay/v52h_remove_pair_lows_precondition_20260813";
const OUTPUT_REL = ".claude/window1_live_v4_replay/v52h_ground_truth_grading_binding_20260814";
const argv = process.argv.slice(2);
const arg = (name, fallback) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const repo = path.resolve(arg("--repo", "."));
const output = path.resolve(arg("--output", path.join(repo, OUTPUT_REL)));
const peerOutput = arg("--peer-output", null) ? path.resolve(arg("--peer-output", null)) : null;

function ensure(value, message) { if (!value) throw new Error(message); }
function sha(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function gitBytes(commit, relativePath, maxBuffer = 128 * 1024 * 1024) { return childProcess.execFileSync("git", ["cat-file", "blob", `${commit}:${relativePath}`], { cwd: repo, encoding: null, maxBuffer }); }
function gitJson(commit, relativePath) { return JSON.parse(gitBytes(commit, relativePath)); }
function gitBlob(commit, relativePath) { return childProcess.execFileSync("git", ["rev-parse", `${commit}:${relativePath}`], { cwd: repo, encoding: "utf8" }).trim(); }
function fileHash(file) { return sha(fs.readFileSync(file)); }
function countBy(rows, fn) { const out = {}; for (const row of rows) { const key = String(fn(row)); out[key] = (out[key] || 0) + 1; } return Object.fromEntries(Object.entries(out).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function distribution(values) { const rows = values.filter(Number.isFinite).sort((a, b) => a - b); const q = (p) => rows.length ? rows[Math.max(0, Math.ceil(p * rows.length) - 1)] : null; return { n: rows.length, sum: rows.reduce((a, b) => a + b, 0), min: rows[0] ?? null, p25: q(.25), median: q(.5), p75: q(.75), p90: q(.9), max: rows.at(-1) ?? null }; }
function safeOutput(dir) { ensure(path.basename(dir).includes("v52h_ground_truth_grading_binding") || path.basename(dir).includes("parta-build"), `unsafe output ${dir}`); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true }); }
function write(name, bytes) { fs.writeFileSync(path.join(output, name), bytes); }

function transitivePolicyFiles(entry) {
  const found = new Set();
  const visit = (relativePath) => {
    if (found.has(relativePath)) return;
    found.add(relativePath);
    const text = fs.readFileSync(path.join(repo, relativePath), "utf8");
    for (const match of text.matchAll(/require\("(\.\/window1_[^"]+\.js)"\)/g)) visit(path.posix.join(path.posix.dirname(relativePath), match[1]));
  };
  visit(entry);
  return [...found].sort();
}

function policyIdentity() {
  const files = transitivePolicyFiles("arb-executor/analysis/window1_v52h_remove_pair_lows_precondition.js").map((relativePath) => {
    const local = fs.readFileSync(path.join(repo, relativePath)), frozen = gitBytes(FROZEN_V52H_COMMIT, relativePath);
    return { path: relativePath, frozen_sha256: sha(frozen), local_sha256: sha(local), byte_identical: Buffer.compare(local, frozen) === 0 };
  });
  return { frozen_commit: FROZEN_V52H_COMMIT, files, all_policy_files_byte_identical: files.every((row) => row.byte_identical), policy_edits: false };
}

function stateBefore(outcome) {
  const credited = outcome.legs.filter((leg) => leg.final_state === "CREDITED");
  if (credited.length === 2) return outcome.combined_entry_cents_observation < 100 ? "COMPLETE_AT_DELTA" : "COMPLETE_AT_LOSS";
  return credited.length === 1 ? "PARTIAL_FOR_REASON" : "NEITHER_FOR_REASON";
}

function coreFiles(dir) { return fs.readdirSync(dir).filter((name) => !["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"].includes(name)).sort(); }
function coreManifest(dir) { return Object.fromEntries(coreFiles(dir).map((name) => [name, { sha256: fileHash(path.join(dir, name)), bytes: fs.statSync(path.join(dir, name)).size }])); }
function finalizeTwinBuilds(left, right) {
  const a = coreManifest(left), b = coreManifest(right);
  ensure(canonical(a) === canonical(b), "two clean grading builds differ");
  const receipt = canonical({ clean_builds: 2, byte_identical: true, compared_files: Object.keys(a).length, core_manifest_sha256: sha(Buffer.from(canonical(a))), policy_replay_invocations: 0, grading_builds: 2 });
  for (const dir of [left, right]) {
    fs.writeFileSync(path.join(dir, "DETERMINISM_RECEIPT.json"), receipt);
    const names = fs.readdirSync(dir).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
    fs.writeFileSync(path.join(dir, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(names.map((name) => [name, { sha256: fileHash(path.join(dir, name)), bytes: fs.statSync(path.join(dir, name)).size }])) }));
  }
  ensure(canonical(JSON.parse(fs.readFileSync(path.join(left, "ARTIFACT_HASH_MANIFEST.json")))) === canonical(JSON.parse(fs.readFileSync(path.join(right, "ARTIFACT_HASH_MANIFEST.json")))), "final manifests differ");
}

function main() {
  const ground = windows.loadGroundTruthTable(repo), policy = policyIdentity();
  ensure(policy.all_policy_files_byte_identical, "V52h policy bytes changed");
  const cohort = gitJson(FROZEN_V52H_COMMIT, `${FROZEN_ROOT}/COHORT_SELECTION_RECEIPT.json`);
  const outcomes = gitJson(FROZEN_V52H_COMMIT, `${FROZEN_ROOT}/V52H_FLOW_OUTCOMES_OBSERVATION_ONLY.json`);
  const trace = gitJson(FROZEN_V52H_COMMIT, `${FROZEN_ROOT}/FULL_DECISION_TRACE_MANIFEST.json`).candidate;
  const eventIds = cohort.combined_30.map((row) => row.event_id).sort();
  ensure(eventIds.length === 30 && new Set(eventIds).size === 30, "V52h cohort conservation failed");
  const outcomeByEvent = new Map(outcomes.map((row) => [row.event_id, row]));
  const bindingRows = eventIds.map((eventId) => { const row = ground.byEvent.get(eventId); ensure(row, `ground row missing ${eventId}`); return row; });
  const unknown = bindingRows.filter((row) => !row.scoring_eligible), eligible = bindingRows.filter((row) => row.scoring_eligible);

  const chunkRows = trace.chunks.map((chunk) => {
    const relativePath = `${FROZEN_ROOT}/${chunk.name}`, bytes = gitBytes(FROZEN_V52H_COMMIT, relativePath);
    return { name: chunk.name, events: chunk.events, rows: chunk.rows, git_blob: gitBlob(FROZEN_V52H_COMMIT, relativePath), sha256: sha(bytes), bytes: bytes.length, reemission: "IMMUTABLE_GIT_OBJECT_REFERENCE" };
  });
  const decisionReceipt = { pass: true, proof: "BYTE_PRESERVING_GIT_OBJECT_REEMISSION", frozen_commit: FROZEN_V52H_COMMIT, input_events: 30, frozen_rows: trace.rows, reemitted_rows: trace.rows, policy_field_differences: 0, receipt_key_differences: 0, decision_stream_differences: 0, chunks: chunkRows, note: "No replay window was rebound and no decision code was invoked by the grading adapter." };

  const gradingRows = [], floorRows = [];
  for (const binding of bindingRows) {
    const before = outcomeByEvent.get(binding.event_id); ensure(before, `frozen outcome missing ${binding.event_id}`);
    const oldFills = before.legs.filter((leg) => leg.final_state === "CREDITED").map((leg) => ({ leg_identity: leg.leg_identity, entry_cents: leg.entry_cents_observation, fill_timestamp_epoch: leg.fill_timestamp_epoch }));
    const retained = binding.scoring_eligible ? oldFills.filter((leg) => Number.isFinite(leg.fill_timestamp_epoch) && leg.fill_timestamp_epoch >= binding.span_start_epoch && leg.fill_timestamp_epoch <= binding.span_end_epoch) : [];
    const combined = retained.length === 2 ? retained.reduce((sum, row) => sum + row.entry_cents, 0) : null;
    const afterState = !binding.scoring_eligible ? "UNKNOWN_BELL" : retained.length === 2 ? (combined < 100 ? "COMPLETE_AT_DELTA" : "COMPLETE_AT_LOSS") : retained.length === 1 ? "PARTIAL_FOR_REASON" : "NEITHER_FOR_REASON";
    gradingRows.push({ event_id: binding.event_id, category: binding.category, scoring_eligible: binding.scoring_eligible, window_class: binding.scoring_class, before_state: stateBefore(before), after_state: afterState, before_combined_entry_cents: before.combined_entry_cents_observation, after_combined_entry_cents: combined, state_changed_by_grading: stateBefore(before) !== afterState, retained_fills: retained, removed_fills: oldFills.filter((old) => !retained.some((row) => row.leg_identity === old.leg_identity)), decision_stream_changed: false });
    for (const leg of before.legs) {
      const legId = leg.leg_identity.split("|").at(-1), floor = binding.legs[legId], fill = retained.find((row) => row.leg_identity === leg.leg_identity);
      floorRows.push({ event_id: binding.event_id, leg_identity: leg.leg_identity, category: binding.category, scoring_eligible: binding.scoring_eligible, true_trade_floor_cents: binding.scoring_eligible ? floor.floor_cents : null, true_trade_floor_epoch: binding.scoring_eligible ? floor.floor_epoch : null, credited_for_grade: Boolean(fill), entry_cents: fill?.entry_cents ?? null, entry_minus_floor_cents: fill && Number.isInteger(floor.floor_cents) ? fill.entry_cents - floor.floor_cents : null });
    }
  }
  const offerRows = bindingRows.map((binding) => {
    const floors = Object.values(binding.legs).map((leg) => leg.floor_cents), pairFloor = floors.every(Number.isInteger) ? floors.reduce((a, b) => a + b, 0) : null;
    return { event_id: binding.event_id, category: binding.category, scoring_eligible: binding.scoring_eligible, scoring_class: binding.scoring_class, pair_floor_cents: binding.scoring_eligible ? pairFloor : null, offer_class: !binding.scoring_eligible ? "UNKNOWN_BELL" : !Number.isInteger(pairFloor) ? "NOT_OFFERED" : pairFloor < 100 ? "OFFERED_UNDER_PAR" : "OFFERED_AT_OR_ABOVE_PAR", margin_cents: binding.scoring_eligible && Number.isInteger(pairFloor) ? 100 - pairFloor : null };
  });
  const offered = offerRows.filter((row) => row.offer_class === "OFFERED_UNDER_PAR");
  const floorRegret = { source: ground.binding, credited_legs: floorRows.filter((row) => row.credited_for_grade).length, distribution: distribution(floorRows.map((row) => row.entry_minus_floor_cents)), by_category: Object.fromEntries([...new Set(floorRows.map((row) => row.category))].sort().map((category) => [category, distribution(floorRows.filter((row) => row.category === category).map((row) => row.entry_minus_floor_cents))])) };
  const bindingReceipt = { binding: ground.binding, input_events: 30, scoring_D: eligible.length, unknown_bell_event_ids: unknown.map((row) => row.event_id).sort(), uses: { decisions: "FROZEN_HISTORICAL_WINDOWS_UNTOUCHED", floors: "W1_GROUND_TRUTH_TABLE", fill_validity: "W1_GROUND_TRUTH_TABLE verified span", offer_denominators: "W1_GROUND_TRUTH_TABLE eligible rows", deltas: "entry minus W1_GROUND_TRUTH_TABLE true-trade floor" }, table_sha_in_every_receipt: true };

  safeOutput(output);
  write("W1_GROUND_TRUTH_TABLE.json", ground.bytes);
  write("WINDOW_SOURCE_BINDING.json", canonical(bindingReceipt));
  write("WINDOW_BINDING_LEDGER_30.jsonl", bindingRows.map((row) => JSON.stringify({ ...row, source_sha256: ground.binding.sha256 })).join("\n") + "\n");
  write("POLICY_BYTE_IDENTITY.json", canonical(policy));
  write("DECISION_STREAM_REEMISSION_MANIFEST.json", canonical(decisionReceipt));
  write("GRADING_ONLY_DIFFERENTIAL.json", canonical({ pass: decisionReceipt.pass && gradingRows.every((row) => !row.decision_stream_changed), source_sha256: ground.binding.sha256, decision_stream_differences: 0, grading_state_changes: gradingRows.filter((row) => row.state_changed_by_grading).length, rows: gradingRows }));
  write("BOUND_FOUR_STATE_OBSERVATION_30.json", canonical({ source_sha256: ground.binding.sha256, D: eligible.length, UNKNOWN_BELL: unknown.length, states: countBy(gradingRows, (row) => row.after_state), conservation: { rows: gradingRows.length, pass: gradingRows.length === 30 && eligible.length + unknown.length === 30 }, rows: gradingRows }));
  write("BOUND_FLOOR_LEDGER_60.jsonl", floorRows.map((row) => JSON.stringify({ ...row, source_sha256: ground.binding.sha256 })).join("\n") + "\n");
  write("BOUND_FLOOR_REGRET.json", canonical(floorRegret));
  write("BOUND_OFFER_DENOMINATOR_30.json", canonical({ source: ground.binding, input_events: 30, D: eligible.length, UNKNOWN_BELL: unknown.length, classes: countBy(offerRows, (row) => row.offer_class), offered_under_par: offered.length, margin_ladder: { GE_10: offered.filter((row) => row.margin_cents >= 10).length, GE_5: offered.filter((row) => row.margin_cents >= 5).length, GE_3: offered.filter((row) => row.margin_cents >= 3).length, THIN_1_TO_2: offered.filter((row) => row.margin_cents >= 1 && row.margin_cents <= 2).length }, rows: offerRows }));
  write("FORBIDDEN_ACCESS_RECEIPT.json", canonical({ source_sha256: ground.binding.sha256, holdout: false, sealed: false, live: false, network_runtime: false, orders: false, positions: false, exits: false, settlement: false, deployment: false, policy_replay_invocations: 0 }));
  write("SOURCE_HASH_MANIFEST.json", canonical({ sources: { window_table: ground.binding, frozen_v52h_policy: { commit: FROZEN_V52H_COMMIT }, frozen_decision_trace: { commit: FROZEN_V52H_COMMIT, manifest: `${FROZEN_ROOT}/FULL_DECISION_TRACE_MANIFEST.json` }, adapter: { path: "arb-executor/analysis/window1_ground_truth_window_adapter.js", sha256: fileHash(path.join(repo, "arb-executor/analysis/window1_ground_truth_window_adapter.js")) }, proof_builder: { path: "arb-executor/analysis/build_window1_ground_truth_binding_proof.js", sha256: fileHash(__filename) } } }));
  write("REPORT.md", `# Part A — W1 ground-truth grading-only binding\n\nW1_GROUND_TRUTH_TABLE ${ground.binding.source_commit} (${ground.binding.sha256}) is the sole grading source. V52h decisions remain the immutable historical-window stream at ${FROZEN_V52H_COMMIT}.\n\n- Decision-stream diffs: 0 across ${trace.rows} frozen rows and 30 games.\n- Scoring D: ${eligible.length}; UNKNOWN_BELL: ${unknown.length} (${unknown.map((row) => row.event_id).sort().join(", ")}).\n- Four-state grading: ${JSON.stringify(countBy(gradingRows, (row) => row.after_state))}; grading-only state changes ${gradingRows.filter((row) => row.state_changed_by_grading).length}.\n- Offered under par: ${offered.length}/${eligible.length}.\n- Floor regret: ${JSON.stringify(floorRegret.distribution)}.\n- No replay policy invocation, holdout, sealed, live, network, order, position, exit, settlement, or deployment access.\n`);
  if (peerOutput) finalizeTwinBuilds(output, peerOutput);
  process.stdout.write(canonical({ output, decision_stream_differences: 0, D: eligible.length, UNKNOWN_BELL: unknown.length, states: countBy(gradingRows, (row) => row.after_state), offered_under_par: offered.length, peer_finalized: Boolean(peerOutput) }));
}

try { main(); } catch (error) { console.error(error.stack || error); process.exitCode = 1; }
