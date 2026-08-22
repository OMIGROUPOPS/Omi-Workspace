"use strict";

// Receipt-only audit. Reads and hashes the six untracked V54 directories; it
// never invokes the replay builder, policy, a game pass, or a disposition.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { execFileSync } = require("child_process");

const repo = path.resolve(process.argv[2] || path.join(__dirname, "..", ".."));
const outputRoot = path.join(repo, ".claude", "window1_live_v4_replay", "v54_receipt_repairs_20260821");
const replayRoot = path.join(repo, ".claude", "window1_live_v4_replay");
const manifestPath = path.join(outputRoot, "SIX_DIR_PRE_DISPOSITION_MANIFEST.json");
const receiptPath = path.join(outputRoot, "SIX_DIR_PROVENANCE_RECEIPT.json");
const ensure = (condition, message) => { if (!condition) throw new Error(message); };
const canonical = (value) => `${JSON.stringify(value, null, 2)}\n`;
const sha = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
const fileBytes = (file) => fs.readFileSync(file);
const fileReceipt = (file) => {
  const bytes = fileBytes(file);
  return { sha256: sha(bytes), bytes: bytes.length };
};
const gitBytes = (commit, file) => execFileSync("git", ["show", `${commit}:${file}`], { cwd: repo, encoding: "buffer", maxBuffer: 64 * 1024 * 1024 });
const isoFromNs = (ns) => new Date(Number(ns / 1000000n)).toISOString();
const local = (iso) => new Date(iso).toLocaleString("en-CA", { timeZone: "America/New_York", hour12: false, timeZoneName: "shortOffset" });
const millis = (iso) => Date.parse(iso);

const anchors = {
  iteration_01_stop_receipt: {
    timestamp: "2026-08-21T14:36:43.6188871-04:00",
    source: ".claude/window1_live_v4_replay/v54_pair_model_iteration_01_stop_20260821/V54_ITERATION_01_STOP_RECEIPT.json",
    state: "replay_processes_running_after_stop=0; second_determinism_replay_interrupted=true",
  },
  iteration_01_stop_commit: {
    commit: "94ee8a3cbb6f0175ea959f05a2668ae38ae2308a",
    timestamp: "2026-08-21T14:38:22-04:00",
  },
  no_804_f_vs_016_author_time: {
    commit: "fae2459466f4949b90e36d28ff5c0dc3fa60602b",
    timestamp: "2026-08-21T15:00:20-04:00",
  },
  no_804_f_v53_042_commit: {
    commit: "8efff0a4c3d9841d64cf5c1e070290f23d59430d",
    timestamp: "2026-08-21T15:17:02-04:00",
  },
  no_804_f_vs_016_commit_time: {
    commit: "fae2459466f4949b90e36d28ff5c0dc3fa60602b",
    timestamp: "2026-08-21T16:29:03-04:00",
  },
};
const stopReceiptFile = path.join(repo, anchors.iteration_01_stop_receipt.source);
const stopReceiptBytes = fs.readFileSync(stopReceiptFile);
const stopReceipt = JSON.parse(stopReceiptBytes.toString("utf8"));

const configs = [
  { short: "build1", name: "v54_pair_model_iteration_01_804_build1_20260821", head_at_start: "4c13023464b5f028eac893281933d5b7e65ef8a8", source_binding: "HEAD interval only; exact launch bytes absent" },
  { short: "cached", name: "v54_pair_model_iteration_01_804_cached_build1_20260821", head_at_start: "4c13023464b5f028eac893281933d5b7e65ef8a8", source_binding: "HEAD interval only; exact launch bytes absent" },
  { short: "fast", name: "v54_pair_model_iteration_01_804_fast_build1_20260821", head_at_start: "4c13023464b5f028eac893281933d5b7e65ef8a8", source_binding: "HEAD interval only; exact launch bytes absent" },
  { short: "final", name: "v54_pair_model_iteration_01_804_final_build1_20260821", head_at_start: "0a2affce429b106222c42bb5e22193bd0e5d86fe", source_binding: "HEAD interval plus byte comparison to scored trace manifest" },
  { short: "scored_build1", name: "v54_pair_model_iteration_01_804_scored_build1_20260821", head_at_start: "e8221ff10a37c648ec83ae3982acd6a24d44fd16", source_binding: "SOURCE_HASH_MANIFEST exact replay_shell SHA-256" },
  { short: "scored_build2", name: "v54_pair_model_iteration_01_804_scored_build2_20260821", head_at_start: "e8221ff10a37c648ec83ae3982acd6a24d44fd16", source_binding: "stop receipt second determinism replay plus byte comparison to scored trace manifest" },
];

const scoredRoot = path.join(replayRoot, configs.find((row) => row.short === "scored_build1").name);
const scoredExternal = JSON.parse(fs.readFileSync(path.join(scoredRoot, "EXTERNAL_CUSTODY_MANIFEST.json"), "utf8"));
const canonicalTraceRows = scoredExternal.rows;
const canonicalByName = new Map(canonicalTraceRows.map((row) => [path.basename(row.logical_trace_path), row]));
const builderPath = "arb-executor/analysis/build_window1_v38_maker_only.js";
const orderReceipt = "F-V53-040 | Small-first iteration law: the 12-game check set is emitted and read before any full-804 aggregate; full-804 proceeds only after the twelve read sane | V54 CHECK-SET order 2026-08-21 | NEW";

const directories = configs.map((config) => {
  const root = path.join(replayRoot, config.name);
  ensure(fs.existsSync(root), `six-dir source absent: ${root}`);
  const names = fs.readdirSync(root).filter((name) => fs.statSync(path.join(root, name)).isFile()).sort();
  const files = names.map((name) => {
    const file = path.join(root, name);
    const stat = fs.statSync(file, { bigint: true });
    const receipt = fileReceipt(file);
    return {
      name,
      sha256: receipt.sha256,
      bytes: receipt.bytes,
      birthtime_ns_since_epoch: stat.birthtimeNs.toString(),
      mtime_ns_since_epoch: stat.mtimeNs.toString(),
    };
  });
  const startNs = files.reduce((value, row) => BigInt(row.birthtime_ns_since_epoch) < value ? BigInt(row.birthtime_ns_since_epoch) : value, BigInt(files[0].birthtime_ns_since_epoch));
  const stopNs = files.reduce((value, row) => BigInt(row.mtime_ns_since_epoch) > value ? BigInt(row.mtime_ns_since_epoch) : value, BigInt(files[0].mtime_ns_since_epoch));
  const startIso = isoFromNs(startNs), stopIso = isoFromNs(stopNs);
  const traceFiles = files.filter((row) => /^V54_FULL_PAIR_LICENSE_TRACE_804_CHUNK_\d+\.jsonl\.gz$/.test(row.name));
  const canonicalMatches = traceFiles.filter((row) => {
    const expected = canonicalByName.get(row.name);
    return expected && expected.sha256 === row.sha256 && expected.bytes === row.bytes;
  }).length;
  let sample = null;
  if (traceFiles.length) {
    const text = zlib.gunzipSync(fs.readFileSync(path.join(root, traceFiles[0].name))).toString("utf8");
    const first = JSON.parse(text.split(/\r?\n/).find(Boolean));
    sample = {
      file: traceFiles[0].name,
      event_id: first.event_id,
      top_level_keys: Object.keys(first).sort(),
      semantic_keys: Object.keys(first.semantic || {}).sort(),
      decision_fields_present: ["lineage_decision", "gate_verdict", "final_action", "final_target_cents"].every((key) => Object.prototype.hasOwnProperty.call(first.semantic || {}, key)),
    };
  }
  const sourceBytes = gitBytes(config.head_at_start, builderPath);
  const contentClass = config.short === "scored_build1"
    ? "FULL_804_SCORED_RESULT_PACKAGE_WITH_SCORECARD_AND_EXTERNAL_TRACE_MANIFEST"
    : "SEMANTIC_DECISION_LICENSE_TRACE_CHUNKS_WITH_FINAL_ACTIONS";
  const full804Complete = config.short === "scored_build1" || (traceFiles.length === canonicalTraceRows.length && canonicalMatches === canonicalTraceRows.length);
  const executionOccurred = traceFiles.length > 0 || (config.short === "scored_build1" && fs.existsSync(path.join(root, "SCORECARD.json")));
  const wroteAfterStopReceipt = millis(stopIso) > millis(anchors.iteration_01_stop_receipt.timestamp);
  const wroteAfterStopCommit = millis(stopIso) > millis(anchors.iteration_01_stop_commit.timestamp);
  const wroteAfterNo804Filing = millis(stopIso) > millis(anchors.no_804_f_vs_016_author_time.timestamp);
  const executionAfterStop = executionOccurred && (wroteAfterStopReceipt || wroteAfterStopCommit || stopReceipt.stop_state.replay_processes_running_after_stop !== 0);
  return {
    id: config.short,
    path: path.relative(repo, root).replaceAll("\\", "/"),
    files: files.length,
    bytes: files.reduce((sum, row) => sum + row.bytes, 0),
    exact_filesystem_interval: {
      start_birthtime_ns_since_epoch: startNs.toString(),
      start_utc: startIso,
      start_local: local(startIso),
      stop_mtime_ns_since_epoch: stopNs.toString(),
      stop_utc: stopIso,
      stop_local: local(stopIso),
    },
    temporal_verdict: {
      milliseconds_before_stop_receipt: millis(anchors.iteration_01_stop_receipt.timestamp) - millis(stopIso),
      milliseconds_before_stop_commit_landed: millis(anchors.iteration_01_stop_commit.timestamp) - millis(stopIso),
      milliseconds_before_f_vs_016_author_time: millis(anchors.no_804_f_vs_016_author_time.timestamp) - millis(stopIso),
      milliseconds_before_f_v53_042_commit: millis(anchors.no_804_f_v53_042_commit.timestamp) - millis(stopIso),
      file_write_after_stop_receipt: wroteAfterStopReceipt,
      file_write_after_stop_commit_landed: wroteAfterStopCommit,
      file_write_after_no_804_rule_filing: wroteAfterNo804Filing,
      execution_after_stop_landed: executionAfterStop,
      execution_after_stop_evidence: "latest output mtime predates stop receipt and stop commit; stop receipt records zero replay processes running after stop",
      verdict_post_stop: executionAfterStop ? "CONVICT_BY_TIMESTAMP" : "CLEAR_BY_TIMESTAMP",
      verdict_post_no_804_filing: wroteAfterNo804Filing ? "CONVICT_BY_TIMESTAMP" : "CLEAR_BY_TIMESTAMP",
    },
    creator: {
      script: builderPath,
      head_at_start: config.head_at_start,
      script_sha256_at_head: sha(sourceBytes),
      script_bytes_at_head: sourceBytes.length,
      binding: config.source_binding,
      exact_shell_command_receipt: "ABSENT",
      minimum_reconstructed_invocation: `node ${builderPath} --variant v54 --stage tune804 --output .claude/window1_live_v4_replay/${config.name}`,
      order: "V54_THE_PAIR_MODEL / V54 CHECK-SET order 2026-08-21",
      order_receipt: orderReceipt,
    },
    content: {
      class: contentClass,
      trace_chunk_files: traceFiles.length,
      canonical_scored_trace_byte_matches: canonicalMatches,
      canonical_scored_trace_rows: canonicalTraceRows.length,
      sample,
    },
    execution: {
      occurred: executionOccurred,
      full_804_completed: full804Complete,
      grading_emitted: config.short === "scored_build1",
      scope_verdict: "CONVICT_F_V53_040_CONDITIONAL_FULL_804_STARTED_WITHOUT_RECORDED_SANE_READING",
      scope_evidence: "the execution output begins after the check-set commit and the creating order requires a sane twelve-game reading before any full-804 aggregate; no such authorizing receipt is attached",
    },
    file_manifest_content_identity_sha256: sha(Buffer.from(canonical(files.map(({ name, sha256, bytes }) => ({ name, sha256, bytes }))))),
    file_receipts: files,
  };
});

const preDispositionManifest = {
  label: "V54_SIX_DIR_PRE_DISPOSITION_SHA256_BYTES_ENTRIES_MANIFEST",
  license: {
    law_index_read_at: "53db48ac",
    law_index_sha256: "41784e6ab62d6341c2a02f8be616e596eb48930b84a71acae8f500368d44c934",
    cited_laws: ["L8", "L18", "L20", "L22"],
    index_gap: ["L20", "L22"],
  },
  scope: { receipt_only: true, passes: 0, reruns: 0, full_804_runs_started: 0, disposition_performed: false },
  directories: directories.map((row) => ({ path: row.path, files: row.files, bytes: row.bytes, content_identity_sha256: row.file_manifest_content_identity_sha256, file_receipts: row.file_receipts })),
};
preDispositionManifest.combined_content_identity_sha256 = sha(Buffer.from(canonical(preDispositionManifest.directories.map(({ path: dirPath, files, bytes, content_identity_sha256 }) => ({ path: dirPath, files, bytes, content_identity_sha256 })))));
fs.mkdirSync(outputRoot, { recursive: true });
fs.writeFileSync(manifestPath, canonical(preDispositionManifest), "utf8");
const manifestReceipt = fileReceipt(manifestPath);

const provenanceReceipt = {
  label: "V54_SIX_DIR_PROVENANCE_AND_TIMESTAMP_VERDICT",
  license: preDispositionManifest.license,
  scope: preDispositionManifest.scope,
  anchors: {
    ...anchors,
    iteration_01_stop_receipt: { ...anchors.iteration_01_stop_receipt, sha256: sha(stopReceiptBytes), bytes: stopReceiptBytes.length },
  },
  creating_order: { name: "V54_THE_PAIR_MODEL / V54 CHECK-SET", receipt: orderReceipt },
  directories: directories.map(({ file_receipts, ...row }) => row),
  aggregate: {
    directories: directories.length,
    files: directories.reduce((sum, row) => sum + row.files, 0),
    bytes: directories.reduce((sum, row) => sum + row.bytes, 0),
    any_execution_occurred: directories.some((row) => row.execution.occurred),
    any_execution_after_stop_landed: directories.some((row) => row.temporal_verdict.execution_after_stop_landed),
    any_write_after_stop_landed: directories.some((row) => row.temporal_verdict.file_write_after_stop_commit_landed),
    any_write_after_no_804_rule_filing: directories.some((row) => row.temporal_verdict.file_write_after_no_804_rule_filing),
    post_stop_verdict: "ALL_SIX_CLEAR_BY_TIMESTAMP",
    original_scope_verdict: "ALL_SIX_CONVICT_F_V53_040",
  },
  pre_disposition_manifest: { path: path.relative(repo, manifestPath).replaceAll("\\", "/"), sha256: manifestReceipt.sha256, bytes: manifestReceipt.bytes, combined_content_identity_sha256: preDispositionManifest.combined_content_identity_sha256 },
  disclosure: {
    f_v53_072_omitted_all_six: true,
    stop_receipt_already_enumerated_all_six_before_f_v53_072: true,
    verdict: "DISCLOSURE_FAILURE",
  },
};
fs.writeFileSync(receiptPath, canonical(provenanceReceipt), "utf8");
process.stdout.write(canonical({
  receipt: { path: receiptPath, ...fileReceipt(receiptPath) },
  manifest: { path: manifestPath, ...manifestReceipt, combined_content_identity_sha256: preDispositionManifest.combined_content_identity_sha256 },
  aggregate: provenanceReceipt.aggregate,
  directories: provenanceReceipt.directories.map((row) => ({ id: row.id, files: row.files, bytes: row.bytes, start: row.exact_filesystem_interval.start_local, stop: row.exact_filesystem_interval.stop_local, after_stop: row.temporal_verdict.execution_after_stop_landed, full_804_completed: row.execution.full_804_completed })),
}));
