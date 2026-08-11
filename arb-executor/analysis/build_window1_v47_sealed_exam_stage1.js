#!/usr/bin/env node
"use strict";

// Policy-free union freezer for the corrected 171 and the post-Stage-B
// capture stream.  It performs the decision-relevant Git touch audit before
// emitting the final event list and REAL_START-method boundary ledger.

const child = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const argv = process.argv.slice(2);
const arg = (name, fallback = null) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const required = (name) => { const value = arg(name); if (!value) throw new Error(`${name} required`); return value; };
const repo = path.resolve(arg("--repo", path.join(__dirname, "../..")));
const output = path.resolve(required("--output"));
const provisionalInputs = arg("--provisional-inputs", "false") === "true";

const sha = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
const hashFile = (file) => sha(fs.readFileSync(file));
const canonical = (value) => `${JSON.stringify(value, null, 2)}\n`;
const compact = (value) => JSON.stringify(value);
const readJson = (file) => JSON.parse(fs.readFileSync(file, "utf8"));
const readJsonl = (file) => fs.readFileSync(file, "utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
const readList = (file) => fs.readFileSync(file, "utf8").split(/\r?\n/).filter(Boolean);
const countBy = (rows, fn) => Object.fromEntries([...rows.reduce((map, row) => map.set(fn(row), (map.get(fn(row)) || 0) + 1), new Map())].sort(([a], [b]) => String(a).localeCompare(String(b))));
function ensure(value, message) { if (!value) throw new Error(message); }
function write(name, value) { fs.writeFileSync(path.join(output, name), typeof value === "string" ? value : canonical(value)); }
function copy(name, source) { fs.copyFileSync(source, path.join(output, name)); }
function parseEt(value) {
  const match = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!match) return null;
  let hour = Number(match[4]); if (match[7] === "AM" && hour === 12) hour = 0; if (match[7] === "PM" && hour !== 12) hour += 12;
  return Date.parse(`${match[1]}-${match[2]}-${match[3]}T${String(hour).padStart(2, "0")}:${match[5]}:${match[6]}-04:00`) / 1000;
}

const CAPTURE_ONLY_PATH_PARTS = [
  "window1_fresh_holdout_seal_20260806",
  "BOOT_GATE_STAGE_B_RECORDER_SEAL_20260806_ADDENDUM.md",
  "window1_holdout_capture_registry.py",
];

function commitPaths(commit) {
  return child.execFileSync("git", ["show", "--format=", "--name-only", commit], { cwd: repo, encoding: "utf8", maxBuffer: 16 * 1024 * 1024 }).split(/\r?\n/).filter(Boolean);
}

function touchAudit(event) {
  const since = event.first_tagged_utc || "2026-08-06T00:00:00Z";
  const raw = child.execFileSync("git", ["log", "--all", `--since=${since}`, "--fixed-strings", `-S${event.event_id}`, "--format=%H%x09%cI%x09%s", "--", ".claude", "arb-executor"], { cwd: repo, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 }).trim();
  const hits = raw ? raw.split(/\r?\n/).filter(Boolean).map((line) => {
    const [commit, committed_at, ...subjectParts] = line.split("\t");
    const paths = commitPaths(commit);
    const captureOnly = paths.length > 0 && paths.every((candidate) => CAPTURE_ONLY_PATH_PARTS.some((part) => candidate.includes(part)));
    return { commit, committed_at, subject: subjectParts.join("\t"), paths, classification: captureOnly ? "CAPTURE_CLASS_NOT_TOUCH" : "DECISION_RELEVANT_TOUCH" };
  }) : [];
  return { event_id: event.event_id, first_tagged_utc: since, hits, decision_relevant_hits: hits.filter((row) => row.classification === "DECISION_RELEVANT_TOUCH"), pass: hits.every((row) => row.classification === "CAPTURE_CLASS_NOT_TOUCH") };
}

function oldEvents(list, admissionRows) {
  const byId = new Map(admissionRows.map((row) => [row.event_id, row]));
  return list.map((eventId) => {
    const row = byId.get(eventId); ensure(row?.passed && row.legs?.length === 2, `old admission missing ${eventId}`);
    return {
      event_id: eventId,
      category: row.category,
      source_partition: "CORRECTED_171_06EDE026",
      touch_classification: "PRIOR_V36_V35_EXAM_CONSUMPTION_DISCLOSED_OPERATOR_EXPLICITLY_REAUTHORIZED_FOR_V47",
      legs: row.legs.map((leg) => ({
        ticker: leg.ticker,
        leg_id: leg.ticker.slice(eventId.length + 1),
        sha256: leg.sha256,
        bytes: leg.bytes,
        path_basename: path.basename(leg.path),
        private_root_class: "HOLDOUT_EXAM_20260807_TAPES",
        authoritative_from_epoch: parseEt(leg.first_timestamp_et),
        authoritative_through_epoch: parseEt(leg.last_timestamp_et),
        formed_rows: leg.csv_rows,
      })),
    };
  });
}

function main() {
  ensure(!fs.existsSync(output), `output already exists ${output}`);
  fs.mkdirSync(output, { recursive: true });
  const oldListFile = path.resolve(required("--old-event-list"));
  const oldAdmissionFile = path.resolve(required("--old-admission"));
  const oldBoundaryFile = path.resolve(required("--old-boundary"));
  const newDeclarationFile = path.resolve(required("--new-declaration"));
  const newBoundaryFile = path.resolve(required("--new-boundary"));
  const newExclusionsFile = path.resolve(required("--new-exclusions"));
  const newMetadataFile = path.resolve(required("--new-metadata"));
  const newSummaryFile = path.resolve(required("--new-summary"));
  const registryFile = path.resolve(required("--registry"));
  const registryStateFile = path.resolve(required("--registry-state"));
  const registryPolicyFile = path.resolve(required("--registry-policy"));
  const materializationFile = path.resolve(required("--materialization"));
  const printReceiptFile = provisionalInputs ? null : path.resolve(required("--print-repull-receipt"));
  const rawMemberListFile = path.resolve(required("--raw-member-list"));
  const failedMemberListFile = path.resolve(required("--failed-member-list"));
  const filterLogFile = path.resolve(required("--filter-log"));

  const oldList = readList(oldListFile);
  ensure(oldList.length === 171 && hashFile(oldListFile) === "06ede0264a196bbebc005785c3ffdee5a840afe1a617f86f0354eedf65ac4313", "corrected old-171 identity mismatch");
  const old = oldEvents(oldList, readJsonl(oldAdmissionFile));
  const oldBoundary = new Map(readJsonl(oldBoundaryFile).map((row) => [row.event_id, row]));
  ensure(oldBoundary.size === 171 && hashFile(oldBoundaryFile) === "70f8b28749d8e1fd60e64af6e3ced41e556b2a20e5898ec692f0e4f7081b7c0a", "old boundary identity mismatch");

  const newDeclaration = readJson(newDeclarationFile);
  const newCandidates = newDeclaration.events || [];
  const touchRows = newCandidates.map(touchAudit);
  const readinessRows = newCandidates.map((event) => ({
    event_id: event.event_id,
    capture_quality_flags: event.capture_quality_flags || [],
    hard_pre_bell_span_complete: (event.capture_quality_flags || []).length === 0,
    disposition: (event.capture_quality_flags || []).length === 0 ? "EXAM_READY" : "SEALED_ELIGIBLE_NOT_MATURE_NOT_TOUCHED",
  }));
  const readyIds = new Set(readinessRows.filter((row) => row.hard_pre_bell_span_complete).map((row) => row.event_id));
  const newAdmitted = newCandidates.filter((event) => readyIds.has(event.event_id) && touchRows.find((row) => row.event_id === event.event_id).pass).map((event) => ({
    event_id: event.event_id,
    category: event.category,
    source_partition: "STAGE_B_CAPTURE_ONLY_STREAM",
    first_tagged_utc: event.first_tagged_utc,
    touch_classification: "UNTOUCHED_DECISION_RELEVANT",
    legs: event.legs.map((leg) => ({
      ticker: leg.ticker,
      leg_id: leg.leg_id,
      sha256: leg.sha256,
      bytes: leg.bytes,
      path_basename: path.basename(leg.path),
      private_root_class: "V47_EXAM_NEW_CAPTURE_TAPES",
      authoritative_from_epoch: leg.first_snapshot_epoch,
      authoritative_through_epoch: leg.last_capture_epoch,
      formed_rows: leg.formed_rows_after_snapshot,
    })),
  }));
  const newBoundary = new Map(readJsonl(newBoundaryFile).map((row) => [row.event_id, row]));
  const all = [...old, ...newAdmitted].sort((a, b) => a.event_id.localeCompare(b.event_id));
  ensure(new Set(all.map((row) => row.event_id)).size === all.length, "duplicate union event identity");
  ensure(all.every((event) => event.legs.length === 2), "union event does not have two legs");
  const boundaries = all.map((event) => oldBoundary.get(event.event_id) || newBoundary.get(event.event_id));
  ensure(boundaries.every(Boolean), "union boundary missing");
  const eventListText = all.map((row) => row.event_id).join("\n") + "\n";
  const boundaryText = boundaries.map(compact).join("\n") + "\n";
  const eventListHash = sha(Buffer.from(eventListText));
  const boundaryHash = sha(Buffer.from(boundaryText));
  const printReceipt = provisionalInputs ? null : readJson(printReceiptFile);
  if (!provisionalInputs) {
    ensure(printReceipt.event_N === all.length, "print re-pull population mismatch");
    ensure(printReceipt.leg_N === all.length * 2, "print re-pull leg mismatch");
    ensure(printReceipt.event_list_sha256 === eventListHash, "print re-pull event-list mismatch");
    ensure(printReceipt.nightly_method_spot_reconciliation?.pass === true, "print re-pull N20 reconciliation did not pass");
    ensure(printReceipt.forbidden_access?.policy === 0 && printReceipt.forbidden_access?.score_rows === 0, "print re-pull crossed policy/score boundary");
  }
  const rawMembers = readList(rawMemberListFile);
  const failedMembers = readList(failedMemberListFile);
  const filterDiagnostics = readList(filterLogFile);
  ensure(rawMembers.length === 37, "frozen raw member count mismatch");
  ensure(failedMembers.length === 0, "filtered raw gzip integrity failure exists");

  write("FROZEN_EVENT_LIST.txt", eventListText);
  write("PRE_MATCH_BOUNDARY_LEDGER.jsonl", boundaryText);
  write("FROZEN_POPULATION_DECLARATION.json", {
    schema_version: "window1-v47-sealed-exam-population-v1",
    status: all.length >= 60 ? "ADMITTED" : "STOP_N_LT_60",
    N: all.length,
    legs: all.length * 2,
    partitions: countBy(all, (row) => row.source_partition),
    categories: countBy(all, (row) => row.category),
    precision_classes: countBy(boundaries, (row) => row.precision_class),
    event_list_sha256: eventListHash,
    boundary_ledger_sha256: boundaryHash,
    events: all,
  });
  write("TOUCH_AUDIT.json", {
    schema_version: "window1-v47-sealed-exam-touch-audit-v1",
    law: "Only evaluation, replay, diagnostic, or fix-motivating citation is touch; capture/storage/mechanical accumulation is not.",
    corrected_171: {
      events: 171,
      prior_consumption: "V36_AND_V35_SEALED_EXAM_DISCLOSED",
      V47_consumption_before_this_exam: 0,
      inclusion_authority: "CURRENT_OPERATOR_ORDER_EXPLICITLY_NAMES_CORRECTED_171_AS_REFRESH_BASE",
    },
    capture_stream: { candidates: newCandidates.length, exam_ready_untouched: newAdmitted.length, eligible_not_mature: readinessRows.filter((row) => !row.hard_pre_bell_span_complete).length, excluded_touched: touchRows.filter((row) => !row.pass).length, rows: touchRows },
  });
  write("HARD_PRE_BELL_SPAN_READINESS.json", {
    schema_version: "window1-v47-sealed-exam-hard-edge-readiness-v1",
    law: "A capture-only event remains sealed/eligible but cannot enter this exam until both authoritative leg tapes span the frozen hard pre-bell right edge.",
    policy_invocations: 0,
    score_rows: 0,
    candidates: readinessRows.length,
    exam_ready: readinessRows.filter((row) => row.hard_pre_bell_span_complete).length,
    eligible_not_mature: readinessRows.filter((row) => !row.hard_pre_bell_span_complete).length,
    rows: readinessRows,
  });
  if (!provisionalInputs) copy("PUBLIC_PRINT_REPULL_RECEIPT.json", printReceiptFile);
  copy("CAPTURE_MATERIALIZATION_MANIFEST.json", materializationFile);
  copy("NEW_CAPTURE_DECLARATION.json", newDeclarationFile);
  copy("NEW_CAPTURE_EXCLUSIONS.json", newExclusionsFile);
  copy("NEW_CAPTURE_MARKET_METADATA.json", newMetadataFile);
  copy("NEW_CAPTURE_STAGE1_SUMMARY.json", newSummaryFile);
  copy("FROZEN_RAW_MEMBERS.txt", rawMemberListFile);
  copy("FAILED_RAW_MEMBERS.txt", failedMemberListFile);
  copy("FILTER_PARALLEL_DIAGNOSTICS.log", filterLogFile);
  if (!provisionalInputs) write("PREPARATION_PROCESS_RECEIPT.json", {
    schema_version: "window1-v47-sealed-exam-preparation-v1",
    policy_invocations: 0,
    score_rows: 0,
    scoring_authorization_consumed: false,
    frozen_raw: {
      members: rawMembers.length,
      member_list_sha256: hashFile(rawMemberListFile),
      compressed_bytes: 1849042470,
      expanded_bytes_verified: 12182540404,
      gzip_integrity: "PASS_37_OF_37",
      failed_members: failedMembers.length,
      failed_member_list_sha256: hashFile(failedMemberListFile),
    },
    preprocessing: {
      initial_worker_diagnostics: filterDiagnostics.length,
      exact_diagnostic: "Syntax error: Unterminated quoted string",
      disposition: "NON_AUTHORITATIVE_HELPER_WORKERS; COMPLETE_OUTPUT_INDEPENDENTLY_GZIP_TESTED_AND_MEMBER_CONSERVED",
      obsolete_filter_pipeline_stopped: true,
      recorder_pid_preserved: 3459414,
    },
    materialization: {
      remote_slow_attempt: "STOPPED_PRE_SCORE_WITHOUT_MANIFEST; NOT_USED",
      local_node_initialization_error: "path.basename callback received Array.map index; zero archive rows read; empty output removed",
      authoritative_run: "NODE_STREAMING_LOCAL_RUN2",
      manifest_sha256: hashFile(materializationFile),
    },
    public_print_repull: {
      first_canonicalization: "STOPPED_PRE_SCORE_BEFORE_RECEIPT_TO_AVOID_VPS_OOM; ALL_662_RAW_RECEIPTS_PRESERVED",
      discarded_partial_normalized_bytes: 621411831,
      discarded_partial_normalized_sha256: "709ae0f70542ba0b6f430de7afce787fbd8c4932c1120dba7779632b761186e9",
      repair: "DISK_BACKED_EXACT_TRADE_ID_AND_LINE_HASH; N20_SAMPLE_ROWS_ONLY_IN_MEMORY",
      provisional_unbounded_population: {
        N: 331,
        canonical_rows: 1852616,
        canonical_sha256: "dca9c491e13a136336616e537fcd6bbcd5cd6a9ca5ce25f32954b363861c07df",
        N20_result: "FAIL_15_FAITHFUL_5_ONGOING_EVENTS_WITH_2013_NEW_POST_PULL_TRADES",
        disposition: "NOT_USED; REVEALED_93_CAPTURE_EVENTS_DID_NOT_YET_SPAN_THE_HARD_PRE_BELL_EDGE",
      },
      hard_edge_correction: {
        exam_ready_N: all.length,
        eligible_not_mature_deferred: readinessRows.filter((row) => !row.hard_pre_bell_span_complete).length,
        canonical_scope: "AT_OR_BEFORE_FROZEN_HARD_PRE_BELL_RIGHT_EDGE",
        N20_result: "PASS_20_OF_20",
      },
      authoritative_receipt_sha256: hashFile(printReceiptFile),
    },
  });
  write("STAGE1_CONTROL_BINDING.json", {
    schema_version: "window1-v47-sealed-exam-stage1-control-v1",
    policy_invocations: 0,
    score_rows: 0,
    minimum_N: 60,
    observed_N: all.length,
    pass: all.length >= 60,
    corrected_171: { event_list_sha256: hashFile(oldListFile), boundary_ledger_sha256: hashFile(oldBoundaryFile) },
    capture_registry: { sha256: hashFile(registryFile), state_sha256: hashFile(registryStateFile), policy_sha256: hashFile(registryPolicyFile) },
    capture_materialization_manifest_sha256: hashFile(materializationFile),
    public_print_repull_receipt_sha256: provisionalInputs ? null : hashFile(printReceiptFile),
    new_capture: {
      candidates_after_two_sided_book_admission: newCandidates.length,
      hard_pre_bell_span_ready: readinessRows.filter((row) => row.hard_pre_bell_span_complete).length,
      sealed_eligible_not_mature: readinessRows.filter((row) => !row.hard_pre_bell_span_complete).length,
      touch_clean_admitted: newAdmitted.length,
      declaration_sha256: hashFile(newDeclarationFile),
      boundary_sha256: hashFile(newBoundaryFile),
    },
    frozen_population: { N: all.length, legs: all.length * 2, event_list_sha256: eventListHash, boundary_ledger_sha256: boundaryHash },
  });
  write("FORBIDDEN_ACCESS_RECEIPT.json", { policy_invocations: 0, score_rows: 0, live_engine_access: 0, order_access: 0, position_access: 0, trading_access: 0, tuning: 0, network_access: "CAPTURE_REGISTRY_SSH_AND_PUBLIC_EXCHANGE_METADATA_ONLY" });
  const sourcePaths = [
    "arb-executor/analysis/build_window1_v47_sealed_exam_stage1.js",
    "arb-executor/analysis/window1_v47_exam_capture_materializer.py",
    "arb-executor/analysis/window1_v47_exam_capture_materializer.js",
    "arb-executor/analysis/window1_v47_exam_filter_one.sh",
    "arb-executor/analysis/window1_v47_exam_filter_parallel.sh",
    "arb-executor/analysis/window1_v47_exam_verify_filtered.sh",
    "arb-executor/analysis/window1_v47_exam_verify_filtered.js",
    "arb-executor/analysis/window1_v47_exam_stage1_freeze.py",
    "arb-executor/analysis/window1_v47_exam_print_repull.py",
    "arb-executor/analysis/window1_v47_exam_print_reconcile.py",
    "arb-executor/analysis/window1_v47_sealed_exam_runner.js",
  ];
  write("SOURCE_HASH_MANIFEST.json", { files: Object.fromEntries(sourcePaths.map((rel) => { const file = path.join(repo, rel); return [rel, { sha256: hashFile(file), bytes: fs.statSync(file).size }]; })) });
  const files = fs.readdirSync(output).sort();
  write("ARTIFACT_HASH_MANIFEST.json", { files: Object.fromEntries(files.map((name) => [name, { sha256: hashFile(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size }])) });
  process.stdout.write(canonical({ status: all.length >= 60 ? "PASS" : "STOP", N: all.length, old: 171, new_capture: newAdmitted.length, event_list_sha256: eventListHash, boundary_ledger_sha256: boundaryHash }));
  if (all.length < 60) process.exitCode = 2;
}

main();
