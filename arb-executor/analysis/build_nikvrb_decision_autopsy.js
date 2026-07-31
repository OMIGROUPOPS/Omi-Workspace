#!/usr/bin/env node
"use strict";

// Deterministic, read-only-input builder for the NIK-VRB decision-autopsy
// non-decision ledger.  This does not run live_v4 or a scorer.

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const repo = path.resolve(process.argv[2] || ".");
const sourceDir = path.join(
  repo,
  ".claude/window1_live_v4_replay/nikvrb_coupling_20260730"
);
const outputDir = path.join(
  repo,
  ".claude/window1_live_v4_replay/nikvrb_decision_autopsy_20260731"
);
const clockPath = path.join(sourceDir, "NIKVRB_DUAL_BOOK_CLOCK.csv");
const quotePath = path.join(sourceDir, "NIKVRB_DUAL_QUOTE_SERIES.csv");
const livePath = path.join(repo, "arb-executor/live_v4.py");
const configPath = path.join(repo, "arb-executor/config/deploy_v5_live.json");
const decisionTracePath = path.join(
  repo,
  ".claude/window1_live_v4_replay/one_game_nikvrb_20260730/NIKVRB_DECISION_TRACE.json"
);

const PLACED_VRB_65 = Date.parse("2026-07-19T07:15:43-04:00") / 1000;
const NIK_FILL = Date.parse("2026-07-19T10:39:57.500480-04:00") / 1000;
const ACTUAL_BELL = Date.parse("2026-07-19T12:35:00-04:00") / 1000;
const TRAIL_BURST = 5;

function sha256(buf) {
  return crypto.createHash("sha256").update(buf).digest("hex");
}

function requireHash(filePath, expected) {
  const actual = sha256(fs.readFileSync(filePath));
  if (actual !== expected) {
    throw new Error(`source binding mismatch: ${filePath}: ${actual} != ${expected}`);
  }
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') {
        field += '"';
        i += 1;
      } else if (ch === '"') {
        quoted = false;
      } else {
        field += ch;
      }
    } else if (ch === '"') {
      quoted = true;
    } else if (ch === ",") {
      row.push(field);
      field = "";
    } else if (ch === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += ch;
    }
  }
  if (field.length || row.length) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }
  const headers = rows.shift();
  return rows.filter((r) => r.length === headers.length).map((r) =>
    Object.fromEntries(headers.map((h, i) => [h, r[i]]))
  );
}

function csvEscape(value) {
  const s = value === null || value === undefined ? "" : String(value);
  return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

function writeCsv(filePath, columns, rows) {
  const lines = [columns.join(",")];
  for (const row of rows) {
    lines.push(columns.map((c) => csvEscape(row[c])).join(","));
  }
  fs.writeFileSync(filePath, `${lines.join("\n")}\n`, "utf8");
}

function epoch(row) {
  return Date.parse(row.timestamp_et) / 1000;
}

function numberOrBlank(value) {
  return value === "" ? "" : Number(value);
}

requireHash(livePath, "f6fb1d20f3943f7bac26d94ccf1e9d98a5f22762cd3357394adfc8a3b108d760");
requireHash(configPath, "46607d2404d6794c30c6c61fd52d08c9e787a613a1984d8c21204457d5d2472f");
requireHash(decisionTracePath, "cf3ecdafc43ff0305ae95addd5a98fc1d53695dbbeae6c7080ad79de0fae1b42");
const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
const requiredConfig = {
  best_bid_aware_repost: true,
  combined_goal: 97,
  completion_reprice: true,
  contention_drop_enforced: false,
  leg2_reshuffle: true,
  orientation_live: false,
  pair_class_steer_enabled: false,
  reaim_on_sibling_arrival: true,
  repost_hold_same_price: true,
  staircase_hold_at_bid: true,
  staircase_hold_trail_burst: 5,
  staircase_hold_volatility_trail: true,
  window_truth_live: true,
};
for (const [key, expected] of Object.entries(requiredConfig)) {
  if (config[key] !== expected) {
    throw new Error(`config binding mismatch: ${key}=${config[key]} expected ${expected}`);
  }
}

const clockBytes = fs.readFileSync(clockPath);
const quoteBytes = fs.readFileSync(quotePath);
const clock = parseCsv(clockBytes.toString("utf8"));
const quotes = parseCsv(quoteBytes.toString("utf8"));
const printTimes = clock
  .filter((r) => r.event_kind === "PRINT_NIK" || r.event_kind === "PRINT_VRB")
  .map(epoch)
  .sort((a, b) => a - b);

function recentPrints(ts) {
  let n = 0;
  for (const p of printTimes) {
    if (p > ts) break;
    if (p >= ts - 60) n += 1;
  }
  return n;
}

const nonDecisions = [];
for (const row of clock) {
  const ts = epoch(row);
  if (row.event_kind === "BBO_VRB" && ts >= PLACED_VRB_65 && ts < NIK_FILL) {
    const age = ts - PLACED_VRB_65;
    const recent = recentPrints(ts);
    const cadence = age < 60;
    if (!cadence && recent >= TRAIL_BURST) {
      throw new Error(`unexpected volatile VRB callback at ${row.timestamp_et}`);
    }
    nonDecisions.push({
      sequence: row.sequence,
      timestamp_et: row.timestamp_et,
      tminus_scheduled: row.tminus_scheduled,
      tminus_actual_bell: row.tminus_actual_bell,
      leg: "VRB",
      phase: "ENTRY_RESTING_AT_65_BEFORE_NIK_FILL",
      bid: numberOrBlank(row.VRB_bid),
      ask: numberOrBlank(row.VRB_ask),
      last_trade: numberOrBlank(row.VRB_last),
      rolling_true_print_count_60s: recent,
      router_return: "LAWFUL_PRESENCE_CONTINUE",
      manager_eligible: true,
      signed_non_decision: cadence ? "HOLD_CADENCE" : "HOLD_STAIRCASE_QUIET_FIFO",
      code_path: cadence
        ? "live_v4.py:13242-13247"
        : "live_v4.py:13248-13263",
      overwritten_or_unreached: cadence
        ? "all target/repost organs below cadence gate"
        : "best-bid mismatch, target recomputation, window-truth, cohort, and cancel/repost organs",
    });
  }
  if (row.event_kind === "BBO_NIK" && ts > NIK_FILL && ts <= ACTUAL_BELL) {
    nonDecisions.push({
      sequence: row.sequence,
      timestamp_et: row.timestamp_et,
      tminus_scheduled: row.tminus_scheduled,
      tminus_actual_bell: row.tminus_actual_bell,
      leg: "NIK",
      phase: "ACTIVE_AFTER_CREDITED_FILL_24",
      bid: numberOrBlank(row.NIK_bid),
      ask: numberOrBlank(row.NIK_ask),
      last_trade: numberOrBlank(row.NIK_last),
      rolling_true_print_count_60s: recentPrints(ts),
      router_return: "LAWFUL_PRESENCE_CONTINUE",
      manager_eligible: false,
      signed_non_decision: "NO_ENTRY_MANAGER_CALL_POST_FILL",
      code_path: "live_v4.py:11401-11402;12394-12399;9783-9785",
      overwritten_or_unreached: "all entry target, fourth-move, and move/repost organs",
    });
  }
}

const visitRows = [];
const ask68States = quotes.filter((r) => r.VRB_ask === "68");
for (let i = 0; i < ask68States.length; i += 1) {
  const q = ask68States[i];
  const start = Date.parse(q.valid_from_et) / 1000;
  const end = Date.parse(q.valid_to_et) / 1000;
  const bboRows = clock.filter((r) =>
    r.event_kind === "BBO_VRB" && epoch(r) >= start && epoch(r) < end
  );
  const direct68 = bboRows.filter((r) => r.VRB_ask === "68").length;
  let decision;
  let pathName;
  if (i === 0) {
    decision = "NO_ORDER_YET; SKIP_NO_FRESH_TRADE";
    pathName = "live_v4.py:4775-4808;11464-11472";
  } else if (i === 1) {
    decision = "RESPONDED: CANCEL_67_AS_MARKETABLE_STALE; RECONCEIVE_65; THEN_CADENCE_HOLD";
    pathName = "live_v4.py:9058-9095;4739-5009;12029-12164;13242-13247";
  } else {
    decision = "HOLD_STAIRCASE_QUIET_FIFO";
    pathName = "live_v4.py:13248-13263";
  }
  visitRows.push({
    visit: i + 1,
    valid_from_et: q.valid_from_et,
    valid_to_et: q.valid_to_et,
    tminus_scheduled_at_start: q.valid_from_tminus_scheduled,
    tminus_bell_at_start: q.valid_from_tminus_bell,
    duration_seconds: Number(q.duration_seconds),
    quote_state_bid: Number(q.VRB_bid),
    quote_state_ask: Number(q.VRB_ask),
    vrb_bbo_receipts_during_state: bboRows.length,
    raw_rows_directly_stamped_ask_68: direct68,
    decision,
    code_path: pathName,
  });
}

const vrbRows = nonDecisions.filter((r) => r.leg === "VRB");
const nikRows = nonDecisions.filter((r) => r.leg === "NIK");
const vrbCadence = vrbRows.filter((r) => r.signed_non_decision === "HOLD_CADENCE");
const vrbQuiet = vrbRows.filter((r) => r.signed_non_decision === "HOLD_STAIRCASE_QUIET_FIFO");
const recentDistribution = Object.fromEntries(
  [...new Set(vrbRows.map((r) => r.rolling_true_print_count_60s))]
    .sort((a, b) => a - b)
    .map((n) => [String(n), vrbRows.filter((r) => r.rolling_true_print_count_60s === n).length])
);

if (vrbRows.length !== 874) throw new Error(`VRB callback conservation ${vrbRows.length} != 874`);
if (nikRows.length !== 5534) throw new Error(`NIK callback conservation ${nikRows.length} != 5534`);
if (vrbCadence.length !== 6) throw new Error(`VRB cadence conservation ${vrbCadence.length} != 6`);
if (vrbQuiet.length !== 868) throw new Error(`VRB quiet conservation ${vrbQuiet.length} != 868`);
if (ask68States.length !== 9) throw new Error(`ask-68 visit conservation ${ask68States.length} != 9`);
if (visitRows.reduce((n, r) => n + r.duration_seconds, 0) !== 641) {
  throw new Error("ask-68 duration conservation failed");
}

fs.mkdirSync(outputDir, { recursive: true });
const ledgerPath = path.join(outputDir, "NIKVRB_NON_DECISION_LEDGER.csv");
const visitPath = path.join(outputDir, "NIKVRB_VRB_ASK68_VISITS.csv");
const censusPath = path.join(outputDir, "NIKVRB_SILENCE_CENSUS.json");
const manifestPath = path.join(outputDir, "SOURCE_AND_ARTIFACT_HASH_MANIFEST.json");

writeCsv(ledgerPath, [
  "sequence", "timestamp_et", "tminus_scheduled", "tminus_actual_bell", "leg",
  "phase", "bid", "ask", "last_trade", "rolling_true_print_count_60s",
  "router_return", "manager_eligible", "signed_non_decision", "code_path",
  "overwritten_or_unreached",
], nonDecisions);
writeCsv(visitPath, [
  "visit", "valid_from_et", "valid_to_et", "tminus_scheduled_at_start",
  "tminus_bell_at_start", "duration_seconds", "quote_state_bid", "quote_state_ask",
  "vrb_bbo_receipts_during_state", "raw_rows_directly_stamped_ask_68",
  "decision", "code_path",
], visitRows);

const census = {
  schema_version: "nikvrb-decision-autopsy-silence-census-v1",
  event: "KXATPCHALLENGERMATCH-26JUL19NIKVRB",
  build_law: "read frozen dual-book and quote-series artifacts; do not execute live_v4 or score",
  clocks: {
    scheduled_start_et: "2026-07-19T12:30:00-04:00",
    actual_bell_et: "2026-07-19T12:35:00-04:00",
    vrb_65_placement_et: "2026-07-19T07:15:43-04:00",
    nik_fill_evidence_et: "2026-07-19T10:39:57.500480-04:00",
  },
  vrb_65_hold: {
    own_bbo_callbacks: vrbRows.length,
    cadence_gate_returns: vrbCadence.length,
    staircase_quiet_fifo_returns: vrbQuiet.length,
    volatility_trail_returns: 0,
    rolling_60s_true_print_count_distribution: recentDistribution,
    maximum_rolling_60s_true_print_count: Math.max(...vrbRows.map((r) => r.rolling_true_print_count_60s)),
    configured_burst_required: TRAIL_BURST,
  },
  vrb_ask_68: {
    quote_state_visits: visitRows.length,
    total_residency_seconds: visitRows.reduce((n, r) => n + r.duration_seconds, 0),
    bbo_receipts_during_quote_state_intervals: visitRows.reduce((n, r) => n + r.vrb_bbo_receipts_during_state, 0),
    raw_rows_directly_stamped_ask_68: visitRows.reduce((n, r) => n + r.raw_rows_directly_stamped_ask_68, 0),
    correction: "visit 1 predates any VRB order; visit 2 caused 67 cancellation and 65 reconception",
  },
  nik_post_fill: {
    own_bbo_callbacks_to_actual_bell: nikRows.length,
    callbacks_with_ask_at_or_below_24: nikRows.filter((r) => Number(r.ask) <= 24).length,
    manager_calls: 0,
    reason: "entry fill set phase=active, so entry_resting manager guard was false",
  },
  source_hashes: {
    NIKVRB_DUAL_BOOK_CLOCK_csv_sha256: sha256(clockBytes),
    NIKVRB_DUAL_QUOTE_SERIES_csv_sha256: sha256(quoteBytes),
  },
  output_hashes: {
    NIKVRB_NON_DECISION_LEDGER_csv_sha256: sha256(fs.readFileSync(ledgerPath)),
    NIKVRB_VRB_ASK68_VISITS_csv_sha256: sha256(fs.readFileSync(visitPath)),
  },
};
fs.writeFileSync(censusPath, `${JSON.stringify(census, null, 2)}\n`, "utf8");

const boundPaths = [
  "arb-executor/live_v4.py",
  "arb-executor/config/deploy_v5_live.json",
  "arb-executor/analysis/build_nikvrb_decision_autopsy.js",
  "arb-executor/docs/research/window1/NIKVRB_DECISION_AUTOPSY.md",
  ".claude/window1_live_v4_replay/one_game_nikvrb_20260730/NIKVRB_DECISION_TRACE.json",
  ".claude/window1_live_v4_replay/nikvrb_coupling_20260730/NIKVRB_DUAL_BOOK_CLOCK.csv",
  ".claude/window1_live_v4_replay/nikvrb_coupling_20260730/NIKVRB_DUAL_QUOTE_SERIES.csv",
  ".claude/window1_live_v4_replay/nikvrb_decision_autopsy_20260731/NIKVRB_NON_DECISION_LEDGER.csv",
  ".claude/window1_live_v4_replay/nikvrb_decision_autopsy_20260731/NIKVRB_VRB_ASK68_VISITS.csv",
  ".claude/window1_live_v4_replay/nikvrb_decision_autopsy_20260731/NIKVRB_SILENCE_CENSUS.json",
];
const manifest = {
  schema_version: "nikvrb-decision-autopsy-hash-manifest-v1",
  git_head_parent: "77be1254a0a6fa157e650bf64ef51d3c5f0c91f7",
  files: Object.fromEntries(boundPaths.map((relativePath) => {
    const bytes = fs.readFileSync(path.join(repo, relativePath));
    return [relativePath, { sha256: sha256(bytes), size_bytes: bytes.length }];
  })),
  absent_bound_trace: {
    path_from_prior_receipt: "../one_game_nikvrb_final_20260730/runs/KXATPCHALLENGERMATCH-26JUL19NIKVRB/trace.json",
    expected_sha256: "5dd923fb3636926165e651668954f6b778e9d4c8811b2254f3102a9aa05302cc",
    status: "NOT_PRESENT_NOT_COMMITTED",
    consequence: "do not manufacture exact timestamps for the nine post-fill VRB move/reposts",
  },
};
fs.writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");

process.stdout.write(`${JSON.stringify({
  output_dir: path.relative(repo, outputDir).replace(/\\/g, "/"),
  non_decision_rows: nonDecisions.length,
  vrb_rows: vrbRows.length,
  nik_rows: nikRows.length,
  ask68_visits: visitRows.length,
  manifest_sha256: sha256(fs.readFileSync(manifestPath)),
}, null, 2)}\n`);
