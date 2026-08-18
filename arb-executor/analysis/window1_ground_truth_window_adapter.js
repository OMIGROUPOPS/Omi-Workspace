"use strict";

const crypto = require("crypto");
const childProcess = require("child_process");

const GROUND_TRUTH_COMMIT = "c0056976c446afcb4d9603796a2e06c068ee94d6";
const GROUND_TRUTH_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/W1_GROUND_TRUTH_TABLE.json";
const GROUND_TRUTH_GIT_BLOB = "4fe8975b8d824f5a942fa407561ce664452a3e73";
const GROUND_TRUTH_SHA256 = "f7bc71d8e615859db272d841e125bc4836a685d82bb2d6769762c9bc19e56729";
const GROUND_TRUTH_BYTES = 1426420;

function sha256(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

function ensure(value, message) {
  if (!value) throw new Error(message);
}

function loadGroundTruthTable(repo) {
  const object = `${GROUND_TRUTH_COMMIT}:${GROUND_TRUTH_PATH}`;
  const bytes = childProcess.execFileSync("git", ["cat-file", "blob", object], {
    cwd: repo,
    encoding: null,
    maxBuffer: GROUND_TRUTH_BYTES + 1024,
  });
  ensure(bytes.length === GROUND_TRUTH_BYTES, `W1 ground-truth byte count changed: ${bytes.length}`);
  ensure(sha256(bytes) === GROUND_TRUTH_SHA256, "W1 ground-truth SHA-256 mismatch");
  const table = JSON.parse(bytes.toString("utf8"));
  ensure(table.LABEL === "W1_GROUND_TRUTH_TABLE", "W1 ground-truth label mismatch");
  ensure(table.conservation?.rows === 804 && table.rows?.length === 804, "W1 ground-truth population mismatch");
  const byEvent = new Map();
  for (const row of table.rows) {
    ensure(typeof row.event_id === "string" && row.event_id.length > 0, "W1 ground-truth event identity missing");
    ensure(!byEvent.has(row.event_id), `duplicate W1 ground-truth event ${row.event_id}`);
    const unknown = row.bell_source === "UNKNOWN";
    const settlementNoMatch = row.bell_source === "SETTLEMENT_NO_MATCH";
    ensure(unknown ? !Number.isFinite(row.bell_epoch) : (settlementNoMatch || Number.isFinite(row.bell_epoch)), `W1 ground-truth bell/source contradiction ${row.event_id}`);
    ensure(settlementNoMatch ? !Number.isFinite(row.bell_epoch) && Number.isFinite(row.span_end_epoch) : true, `SETTLEMENT_NO_MATCH span contradiction ${row.event_id}`);
    ensure(unknown ? row.verified_span === "UNKNOWN" : true, `UNKNOWN_BELL span is not UNKNOWN ${row.event_id}`);
    byEvent.set(row.event_id, Object.freeze({
      event_id: row.event_id,
      code: row.code,
      category: row.category,
      bell_epoch: Number.isFinite(row.bell_epoch) ? row.bell_epoch : null,
      bell_source: row.bell_source,
      bell_precision: row.bell_precision,
      w1_left_epoch: Number.isFinite(row.w1_left_epoch) ? row.w1_left_epoch : null,
      verified_span: row.verified_span,
      span_start_epoch: Number.isFinite(row.span_start_epoch) ? row.span_start_epoch : null,
      span_end_epoch: Number.isFinite(row.span_end_epoch) ? row.span_end_epoch : null,
      legs: Object.freeze({
        [row.legA]: Object.freeze({ leg_id: row.legA, formation_end_epoch: Number.isFinite(row.legA_formation_end_epoch) ? row.legA_formation_end_epoch : null, open_postformation_cents: Number.isInteger(row.legA_open_postformation_c) ? row.legA_open_postformation_c : null, floor_cents: Number.isInteger(row.legA_floor_c) ? row.legA_floor_c : null, floor_epoch: Number.isFinite(row.legA_floor_epoch) ? row.legA_floor_epoch : null }),
        [row.legB]: Object.freeze({ leg_id: row.legB, formation_end_epoch: Number.isFinite(row.legB_formation_end_epoch) ? row.legB_formation_end_epoch : null, open_postformation_cents: Number.isInteger(row.legB_open_postformation_c) ? row.legB_open_postformation_c : null, floor_cents: Number.isInteger(row.legB_floor_c) ? row.legB_floor_c : null, floor_epoch: Number.isFinite(row.legB_floor_epoch) ? row.legB_floor_epoch : null }),
      }),
      scoring_class: unknown ? "UNKNOWN_BELL" : settlementNoMatch ? "VERIFIED_PREMATCH_SPAN_NO_MATCH" : "VERIFIED_BELL",
      scoring_eligible: !unknown,
    }));
  }
  const unknown = [...byEvent.values()].filter((row) => !row.scoring_eligible);
  ensure(unknown.length === 20, `W1 UNKNOWN_BELL conservation mismatch ${unknown.length}`);
  return Object.freeze({
    bytes,
    table,
    byEvent,
    binding: Object.freeze({
      label: "W1_GROUND_TRUTH_TABLE",
      source_commit: GROUND_TRUTH_COMMIT,
      source_path: GROUND_TRUTH_PATH,
      git_blob: GROUND_TRUTH_GIT_BLOB,
      sha256: GROUND_TRUTH_SHA256,
      bytes: GROUND_TRUTH_BYTES,
      sole_grading_source: true,
      policy_replay_window_source: "HISTORICAL_VARIANT_WINDOW_UNTOUCHED",
      right_edge_law: "PER_GAME_VERIFIED_BELL_EPOCH; SETTLEMENT_NO_MATCH_USES_TABLE_VERIFIED_SPAN_END",
      unknown_bell_law: "EXCLUDED_FROM_ALL_SCORING_DENOMINATORS_AND_REPORTED_AS_OWN_CLASS",
    }),
  });
}

function bindWindow(span, groundTruth) {
  const row = groundTruth.byEvent.get(span.event_id);
  ensure(row, `event absent from W1 ground-truth table ${span.event_id}`);
  ensure(row.category === span.category, `category mismatch against W1 ground truth ${span.event_id}`);
  return Object.freeze({
    ...row,
    left_epoch: row.w1_left_epoch,
    floor_left_epoch: row.span_start_epoch,
    right_epoch: row.span_end_epoch,
    legacy_left_epoch: span.w1_left_epoch,
    legacy_right_epoch: span.w1_right_epoch,
    left_delta_seconds: Number.isFinite(row.w1_left_epoch) ? row.w1_left_epoch - span.w1_left_epoch : null,
    right_delta_seconds: Number.isFinite(row.span_end_epoch) ? row.span_end_epoch - span.w1_right_epoch : null,
    consumption_role: "GRADING_ONLY",
    policy_fields_overwritten: false,
  });
}

function scoringEligible(rows) {
  return rows.filter((row) => row.window_binding?.scoring_eligible !== false);
}

module.exports = {
  GROUND_TRUTH_COMMIT,
  GROUND_TRUTH_PATH,
  GROUND_TRUTH_GIT_BLOB,
  GROUND_TRUTH_SHA256,
  GROUND_TRUTH_BYTES,
  loadGroundTruthTable,
  bindWindow,
  scoringEligible,
};
