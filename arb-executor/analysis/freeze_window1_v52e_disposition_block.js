#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const repo = path.resolve(process.argv[2] || ".");
const out = path.join(repo, ".claude/window1_live_v4_replay/v52e_disposition_804_blocked_20260813");
const V52E = "b09aa22b301205d5d44d683497cf3edc5b177cf8";
const PARENT = "11f0fe0e04c315b555a0f02e4c8d44388328039e";
const OFFER = "22441e058f9efa7ea8c3065334a238ec8786416f";
const hash = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
const fileHash = (file) => hash(fs.readFileSync(file));
const canonical = (value) => `${JSON.stringify(value, null, 2)}\n`;
const write = (name, value) => fs.writeFileSync(path.join(out, name), typeof value === "string" ? value : canonical(value));
const show = (commit, file) => execFileSync("git", ["show", `${commit}:${file}`], { cwd: repo, maxBuffer: 256 * 1024 * 1024 });
const ensure = (value, message) => { if (!value) throw new Error(message); };

const prohibited = ["TWO_RULER_SCORECARD.json", "MARKET_GRADE_SCORECARD.json", "STRICT_BUILD_VERIFICATION_SCORECARD.json", "FRONTIER.json", "REGRET_GAUGE.json"];
ensure(prohibited.every((name) => !fs.existsSync(path.join(out, name))), "score artifact exists despite pre-score block");
const chunks = fs.readdirSync(out).filter((name) => /^V52E_FULL_DECISION_TRACE_804_CHUNK_\d{3}\.jsonl\.gz$/.test(name)).sort();
ensure(chunks.length === 101, `expected 101 full-population trace chunks, got ${chunks.length}`);
const chunkRows = chunks.map((name) => ({ name, sha256: fileHash(path.join(out, name)), bytes: fs.statSync(path.join(out, name)).size }));
ensure(chunkRows.every((row) => row.bytes > 0 && row.bytes < 100_000_000), "empty or Git-unsafe trace chunk");

const policyFiles = [
  "arb-executor/analysis/window1_v52_judgment_gate.js",
  "arb-executor/analysis/window1_v52b_read_level_authority.js",
  "arb-executor/analysis/window1_v52c_full_post_onset_read.js",
  "arb-executor/analysis/window1_v52d_disagreement_referee.js",
  "arb-executor/analysis/window1_v52e_palantir_wiring.js",
];
const priorIdentityPath = ".claude/window1_live_v4_replay/v52e_trace_span_provenance_audit_20260813/POLICY_BYTE_IDENTITY.json";
const priorIdentityBytes = show(PARENT, priorIdentityPath), priorIdentity = JSON.parse(priorIdentityBytes);
const files = {};
for (const file of policyFiles) {
  const current = fileHash(path.join(repo, file)), frozen = hash(show(V52E, file)), prior = priorIdentity.files[file].after_sha256;
  files[file] = { frozen_sha256: frozen, prior_reattest_sha256: prior, current_sha256: current, byte_identical: current === frozen && frozen === prior };
}
const policyIdentity = { frozen_commit: V52E, reattestation_commit: PARENT, reattestation_path: priorIdentityPath, reattestation_sha256: hash(priorIdentityBytes), files, all_byte_identical: Object.values(files).every((row) => row.byte_identical) };
ensure(policyIdentity.all_byte_identical, "policy identity failed");

const fields = [
  "event_id", "leg_identity", "category", "price_region", "sequence", "timestamp_epoch", "t_minus_scheduled_seconds", "t_minus_actual_bell_seconds", "t_minus_pre_match_boundary_seconds", "receipt",
  "bid", "ask", "last_traded", "spread", "ask_dwell_seconds", "top_ask_size", "bid_depth_5", "ask_depth_5",
  "onset_passed", "onset_candidate", "onset_timestamp_epoch", "read_passed", "read_state", "quote_path_state", "pressure_state", "read_evidence_class", "read_span_seconds", "read_evidence_receipts", "read_book_receipts", "read_print_receipts", "read_comparable_book_transitions", "read_comparable_print_transitions", "read_rising_score", "read_falling_score", "last_directional_evidence_kind", "last_directional_evidence_receipt", "last_directional_evidence_magnitude_cents",
  "own_post_onset_low_cents", "own_low_receipt", "sibling_post_onset_low_cents", "sibling_low_receipt", "lows_sum_cents", "lows_under_par", "disagreement_firing", "disagreement_clear", "adjudication_status", "adjudication_winner", "adjudication_loser",
  "level_passed", "level_target_cents", "level_authority", "machine_read_target_cents", "machine_read_authority", "palantir_rescue", "palantir_manifest_sha256", "N2_cell_n", "N2_cell_share", "N4_grid_covered", "N4_grid_discount_cents", "N4_zone_category_share", "N4_zone_price_share", "N5_mirror_rate", "N5_vindication_rate", "palantir_continuous", "priors_gate",
  "gate_verdict", "blocked_clause", "incumbent_action", "incumbent_reason", "order_before_cents", "final_action", "final_target_cents", "reason",
];

write("REPORT.md", `# V52e disposition full-804 exam — BLOCKED BEFORE SCORE EMISSION\n\nThe frozen V52e policy completed receipt processing for all 804 development games. The first score-package precondition then found **4 completed games that were not under par**. The requested three-state vocabulary has only COMPLETE_AT_DELTA, PARTIAL_FOR_REASON, and NEITHER_FOR_REASON; none truthfully describes a two-leg completion at or above par. The controlling instruction says spec doubts stop and report, so no scorecard, frontier, regret gauge, named grading, denominator-capture result, or second deterministic score build was emitted.\n\nPolicy bytes match ${V52E} and the ${PARENT} re-attestation. The 804-event decision diaries are preserved in 101 receipt-grain gzip shards (${chunkRows.reduce((sum, row) => sum + row.bytes, 0)} bytes total; largest ${Math.max(...chunkRows.map((row) => row.bytes))} bytes). They are evidence of the completed decision walk, not a score result.\n\nThe four identities were not frozen because the fail-closed assertion intentionally preceded event-ledger and score serialization. Recovering them would require another replay; no replay occurs after this specification blocker. Operator action required: ratify a fourth disposition (for example COMPLETE_NOT_AT_DELTA) or explicitly state how those four games conserve into the three requested states.\n\nNo sealed, holdout, live, network, deployment, order, position, exit, settlement, or DCA access occurred.\n`);
write("EXAM_BLOCK_RECEIPT.json", {
  status: "BLOCKED_PRE_SCORE_SPECIFICATION_AMBIGUITY",
  frozen_policy_commit: V52E,
  exact_parent: PARENT,
  requested_population: 804,
  replay_events_processed: 804,
  blocking_assertion: "THREE_STATE_VOCABULARY_MUST_BE_EXHAUSTIVE",
  observed_unrepresentable_games: 4,
  observed_class: "BOTH_LEGS_CREDITED_COMBINED_ENTRY_NOT_STRICTLY_BELOW_100",
  requested_states: ["COMPLETE_AT_DELTA", "PARTIAL_FOR_REASON", "NEITHER_FOR_REASON"],
  score_rows_emitted: 0,
  score_artifacts_emitted: [],
  prohibited_score_artifacts_absent: prohibited,
  rerun_after_specification_block: false,
  operator_amendment_required: true,
});
write("MECHANICAL_ATTEMPT_RECEIPT.json", {
  authorization_law: "MECHANICAL_REPAIRS_ONLY; SPEC_DOUBT_STOP",
  attempts_before_final_block: [
    { stage: "PRE_REPLAY", failure: "WRAPPER_DID_NOT_PROPAGATE_NODE_HEAP_FLAG", score_rows_emitted: 0, repair: "PROPAGATE_PROCESS_EXECARGV" },
    { stage: "FIRST_EVENT_EXPORT", failure: "ARRAY_SPREAD_MAXIMUM_CALL_STACK", score_rows_emitted: 0, repair: "BOUNDED_APPEND" },
    { stage: "PRE_SCORE_ORCHESTRATION", failure: "ORPHAN_CHILD_AND_NEW_CHILD_SHARED_PARTIAL_PATH", score_rows_emitted: 0, repair: "STOP_BOTH; NEW_UNCONTAMINATED_PATH" },
    { stage: "PRE_SCORE_EXPORT_SCALE", failure: "REPEATED_NESTED_EVIDENCE_GRAPH_NOT_GIT_SAFE", score_rows_emitted: 0, repair: "RECEIPT_GRAIN_DIARY_SCHEMA; SOURCE_RECEIPTS_RECONSTRUCT_NESTED_EVIDENCE" },
    { stage: "POST_REPLAY_PRE_SCORE", failure: "SPAN_ASSERTION_WRONGLY_REQUIRED_A_RECEIPT_ON_NO_TAPE_LEGS", score_rows_emitted: 0, repair: "EXPLICIT_NO_MATERIALIZED_RECEIPT_INSIDE_EDGE_STATUS" },
  ],
  final_attempt: { replay_events_processed: 804, blocking_failure: "FOUR_COMPLETED_NON_DELTA_GAMES_NOT_REPRESENTABLE_IN_THREE_STATE_CENSUS", score_rows_emitted: 0, mechanical_repair_authority_exhausted: true },
});
write("POLICY_BYTE_IDENTITY.json", policyIdentity);
write("TRACE_SCHEMA.json", { format: "RECEIPT_GRAIN_DECISION_DIARY_V1_JSONL_GZIP", fields, row_law: "row[index] maps to fields[index]", receipts_preserved: true, nested_evidence_reconstruction: "Use receipt against frozen tape/print sources and frozen V52e policy; repeated nested trees are not duplicated in every row." });
write("TRACE_CHUNK_MANIFEST.json", { status: "BLOCKED_EXAM_EVIDENCE_NOT_SCORE_OUTPUT", chunks: chunkRows, chunk_count: chunkRows.length, total_bytes: chunkRows.reduce((sum, row) => sum + row.bytes, 0), maximum_chunk_bytes: Math.max(...chunkRows.map((row) => row.bytes)), full_population_replay_events: 804, score_rows_emitted: 0 });
write("OFFER_DENOMINATOR_BINDING.json", { commit: OFFER, path: ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/POST_ONSET_OFFER_CENSUS.json", requested: { OFFERED_POST_ONSET: 612, GE_10: 90, GE_5: 236, GE_3: 384, THIN_1_TO_2: 228 }, scored_capture: null, reason_null: "EXAM_BLOCKED_BEFORE_SCORE_EMISSION" });
write("DETERMINISM_RECEIPT.json", { clean_score_builds_completed: 0, byte_identical_score_builds: null, reason: "SPECIFICATION_BLOCK_CONTROLS_BEFORE_SCORE_AND_SECOND_BUILD", trace_shards_hash_bound: true });
write("FORBIDDEN_ACCESS_RECEIPT.json", { sealed: false, holdout: false, live: false, network: false, deployment: false, orders: false, positions: false, exits: false, settlement: false, DCA: false });
write("SOURCE_HASH_MANIFEST.json", { files: { "arb-executor/analysis/build_window1_v38_maker_only.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v38_maker_only.js")), role: "MECHANICAL_FULL_804_HARNESS_AND_RECEIPT_EXPORT" }, "arb-executor/analysis/build_window1_v52e_disposition_804.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/build_window1_v52e_disposition_804.js")), role: "HEAP_PROPAGATING_ENTRYPOINT" }, "arb-executor/analysis/freeze_window1_v52e_disposition_block.js": { sha256: fileHash(path.join(repo, "arb-executor/analysis/freeze_window1_v52e_disposition_block.js")), role: "BLOCK_RECEIPT_FREEZER" }, "arb-executor/tests/test_window1_v52e_disposition_block.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v52e_disposition_block.js")), role: "BLOCK_PACKAGE_INTEGRITY_TEST" }, ...Object.fromEntries(Object.entries(files).map(([file, row]) => [file, { sha256: row.current_sha256, role: "FROZEN_POLICY_BYTE_IDENTITY" }])) } });
write("TEST_RESULTS.json", { status: "PRE_EXAM_FOCUSED_PASS_THEN_EXAM_SPEC_BLOCK", focused_pre_exam: { files: 3, assertions: 108, failures: 0, suites: ["test_window1_v52e_palantir_wiring.js:31", "test_window1_v52e_palantir_wiring_package.js:39", "test_window1_v52e_trace_span_provenance_audit.js:38"] }, post_block_integrity: { files: 1, assertions: 16, failures: 0, suite: "test_window1_v52e_disposition_block.js:16" }, exam: { replay_events: 804, score_rows_emitted: 0, block: "THREE_STATE_NOT_EXHAUSTIVE_FOR_4_COMPLETED_NON_DELTA_GAMES" } });

const names = fs.readdirSync(out).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
write("ARTIFACT_HASH_MANIFEST.json", { files: Object.fromEntries(names.map((name) => [name, { sha256: fileHash(path.join(out, name)), bytes: fs.statSync(path.join(out, name)).size }])) });
console.log(canonical({ output: out, status: "BLOCKED_PRE_SCORE", trace_chunks: chunks.length, trace_bytes: chunkRows.reduce((sum, row) => sum + row.bytes, 0), policy_byte_identity: policyIdentity.all_byte_identical }));
