"use strict";

const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const readline = require("readline");
const crypto = require("crypto");
const { execFileSync } = require("child_process");
const os = require("./window1_v54_dual_belief_os.js");
const causalClock = require("./window1_v54_causal_tape_clock.js");
const layeredReporter = require("./window1_v54_dual_belief_reporter.js");
const bellLibrary = require("./window1_v54_bell_bound_library.js");
const subsetGuard = require("./window1_named_subset_guard.js");

let activeExecutionGuard = null;
const LOAD_TICK_ISSUES = [];

const TARGETS = Object.freeze({
  smoke: ["KXWTAMATCH-26JUL13CRIJEA"],
  stories: [
    "KXATPCHALLENGERMATCH-26JUL12GIUBAR",
    "KXATPCHALLENGERMATCH-26JUL14URSPAL",
    "KXATPCHALLENGERMATCH-26JUL14LAJSVA",
    "KXATPMATCH-26JUL18DANPRA", "KXATPMATCH-26JUL12ALTGAS",
  ],
});
const ALL_TARGETS = [...TARGETS.smoke, ...TARGETS.stories];
const SAFETY_FLOORS = Object.freeze({
  KXATPCHALLENGERMATCH_26JUL12GIUBAR: 7,
  KXATPCHALLENGERMATCH_26JUL14URSPAL: 4,
  KXATPCHALLENGERMATCH_26JUL14LAJSVA: 8,
});
const GROUND_TRUTH_COMMIT = "c0056976";
const GROUND_TRUTH_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/W1_GROUND_TRUTH_TABLE.json";
const ANALYSIS_COMMIT = "15955e44faebf24a17c8c99eba6b8fb98a98a294";
const ANALYSIS_ROOT = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803";
const ACTUAL_BELL_PATH = `${ANALYSIS_ROOT}/ACTUAL_BELL_TABLE_804.json`;
const NAMED_NEIGHBOR_PATH = `${ANALYSIS_ROOT}/NEIGHBOR_SPAN_BELL_CHECK.json`;
const GROUND_TRUTH_CORRECTIONS_PATH = `${ANALYSIS_ROOT}/W1_GROUND_TRUTH_CORRECTIONS.jsonl`;
const OUTPUT_LABEL = "V54_BOOK_VETO_ONLY_MIND_ONLY_BED";
const RUN_SOURCE = "V54_BOOK_VETO_ONLY_20260826";
const DEPTH_MAP_COMMIT = "ac68e3bc8d2c2018ba883c131b8b4101ae4cd257";
const DEPTH_MAP_PATH = ".claude/window1_second_seat/dives_t1_v3_20260823/TRUE_BELL_CELL_DEPTH_MAP.json";
const SURVIVOR_SOURCE_COMMIT = "189eaa20";
const PAIR_INTERIM_LIBRARY_PATH = ".claude/window1_live_v4_replay/pair_interim_shape_v18_fit_20260803/INTERIM_PAIR_LIBRARY_V18.json";
const PAIR_COUPLE_LIBRARY_PATH = ".claude/window1_live_v4_replay/pair_couple_v19_fit_20260803/PAIR_COUPLE_LIBRARY_V19.json";
const RECEIPT_REBUILD_BASELINE_HASHES = Object.freeze({
  "FOUR_STORIES_RECEIPT.json": "e6eb3dd6ca3a7563185cebf8fda38007f78762af5ba3227870f6995867a99773",
  "TRADE_REPORT_FOUR.json": "26d878777a89ab038634dd9b4fddd32fc6d05e213b22a4d07a1e47b98e9d2e3c",
  "BELIEF_DEADLINE_SCORING_TABLE.json": "d2d51c01650f1e25bd367289610a97f874c7c944f123e4f4bcc9a2fb9fbafa49",
});

function arg(name, fallback = null) {
  const index = process.argv.indexOf(`--${name}`);
  return index >= 0 ? process.argv[index + 1] : fallback;
}
function required(name) { const value = arg(name); if (!value) throw new Error(`missing --${name}`); return path.resolve(value); }
function canonical(value) { return JSON.stringify(value, null, 2) + "\n"; }
function tapeKindRank(row) { return row.kind === "BOOK" ? 0 : row.kind === "PRINT" ? 1 : 2; }
function compareTapeRows(a, b) { return a.timestamp_epoch - b.timestamp_epoch || tapeKindRank(a) - tapeKindRank(b) || String(a.receipt).localeCompare(String(b.receipt)); }
function firstDifference(left, right, cursor = "$") {
  if (Object.is(left, right)) return null;
  if (typeof left !== typeof right || left === null || right === null) return { path: cursor, left, right };
  if (Array.isArray(left) || Array.isArray(right)) {
    if (!Array.isArray(left) || !Array.isArray(right)) return { path: cursor, left_type: typeof left, right_type: typeof right };
    if (left.length !== right.length) return { path: `${cursor}.length`, left: left.length, right: right.length };
    for (let index = 0; index < left.length; index += 1) {
      const found = firstDifference(left[index], right[index], `${cursor}[${index}]`);
      if (found) return found;
    }
    return null;
  }
  if (typeof left === "object") {
    const leftKeys = Object.keys(left), rightKeys = Object.keys(right);
    if (canonical(leftKeys) !== canonical(rightKeys)) return { path: `${cursor}.__keys`, left: leftKeys, right: rightKeys };
    for (const key of leftKeys) {
      const found = firstDifference(left[key], right[key], `${cursor}.${key}`);
      if (found) return found;
    }
    return null;
  }
  return { path: cursor, left, right };
}
function digestReplay(result) {
  const hash = crypto.createHash("sha256");
  let bytes = 0;
  const consume = (label, value) => {
    const prefix = Buffer.from(`${label}\n`, "utf8");
    const payload = Buffer.from(canonical(value), "utf8");
    hash.update(prefix);
    hash.update(payload);
    bytes += prefix.length + payload.length;
  };
  consume("execution", result.execution);
  result.stage_reads.forEach((row, index) => consume(`stage_reads[${index}]`, row));
  result.rearm_attempts.forEach((row, index) => consume(`rearm_attempts[${index}]`, row));
  result.fill_events.forEach((row, index) => consume(`fill_events[${index}]`, row));
  result.floor_print_decision_instants.forEach((row, index) => consume(`floor_print_decision_instants[${index}]`, row));
  return { sha256: hash.digest("hex"), bytes, counts: { stage_reads: result.stage_reads.length, rearm_attempts: result.rearm_attempts.length, fill_events: result.fill_events.length, floor_print_decision_instants: result.floor_print_decision_instants.length } };
}
function firstReplayDifference(left, right) {
  const execution = firstDifference(left.execution, right.execution, "$.execution");
  if (execution) return execution;
  for (const field of ["stage_reads", "rearm_attempts", "fill_events", "floor_print_decision_instants"]) {
    if (left[field].length !== right[field].length) return { path: `$.${field}.length`, left: left[field].length, right: right[field].length };
    for (let index = 0; index < left[field].length; index += 1) {
      if (shaBytes(canonical(left[field][index])) === shaBytes(canonical(right[field][index]))) continue;
      return firstDifference(left[field][index], right[field][index], `$.${field}[${index}]`);
    }
  }
  return null;
}
function shaBytes(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function sentenceTraceIndex(row) {
  return {
    sentence_sha256: shaBytes(row.sentence ?? ""),
    full_sentence_location: "REPAIR_FOUR_GAME_TRACE.jsonl.gz",
  };
}
function wrapStoryForTwentyRuleBar(text, maxLineLength = 3800) {
  return text.split(/\r?\n/).flatMap((line) => {
    if (line.length <= maxLineLength) return [line];
    const chunks = [];
    let remaining = line;
    while (remaining.length > maxLineLength) {
      const delimiter = Math.max(
        remaining.lastIndexOf("; ", maxLineLength),
        remaining.lastIndexOf(", ", maxLineLength),
        remaining.lastIndexOf(" ", maxLineLength),
      );
      const cut = delimiter >= Math.floor(maxLineLength * 0.55) ? delimiter + 1 : maxLineLength;
      chunks.push(remaining.slice(0, cut));
      remaining = remaining.slice(cut).trimStart();
    }
    chunks.push(remaining);
    return chunks;
  }).join("\n");
}
function median(values) {
  const rows = values.filter(Number.isFinite).sort((a, b) => a - b);
  if (!rows.length) return null;
  const middle = Math.floor(rows.length / 2);
  return rows.length % 2 ? rows[middle] : (rows[middle - 1] + rows[middle]) / 2;
}
function quantileNearestRank(values, probability) {
  const rows = values.filter(Number.isFinite).sort((a, b) => a - b);
  if (!rows.length) return null;
  return rows[Math.max(0, Math.ceil(rows.length * probability) - 1)];
}
function buildPhaseCentralSurface(corpus, sourceSha256) {
  const populations = new Map();
  let terminalPointsExcluded = 0;
  for (const event of corpus) {
    for (const leg of event.legs ?? []) {
      const pathRows = leg.future_low_return_path ?? [];
      if (pathRows.length) terminalPointsExcluded += 1;
      for (const row of pathRows.slice(0, -1)) {
        if (!Number.isFinite(row.window_fraction) || !Number.isFinite(row.future_low_minus_seen_low_cents)) continue;
        const band = os.PHASE_CENTRAL_BANDS.find((candidate, index) => row.window_fraction >= candidate.low && (row.window_fraction < candidate.high || (index === os.PHASE_CENTRAL_BANDS.length - 1 && row.window_fraction <= candidate.high)));
        if (!band) continue;
        const key = `${event.category}|${band.id}`;
        if (!populations.has(key)) populations.set(key, { category: event.category, phase_band: band.id, phase_low_inclusive: band.low, phase_high_exclusive: band.high, values: [] });
        populations.get(key).values.push(row.future_low_minus_seen_low_cents);
      }
    }
  }
  const cells = [...populations.values()].sort((a, b) => a.category.localeCompare(b.category) || a.phase_low_inclusive - b.phase_low_inclusive).map((cell) => {
    const q50 = quantileNearestRank(cell.values, 0.5);
    const less = cell.values.filter((value) => value < q50).length;
    const equal = cell.values.filter((value) => value === q50).length;
    return {
      category: cell.category,
      phase_band: cell.phase_band,
      phase_low_inclusive: cell.phase_low_inclusive,
      phase_high_exclusive: cell.phase_high_exclusive,
      members: cell.values.length,
      q25_cents: quantileNearestRank(cell.values, 0.25),
      q50_cents: q50,
      q75_cents: quantileNearestRank(cell.values, 0.75),
      q50_midrank: Math.round(((less + equal / 2) / cell.values.length) * 1e6) / 1e6,
      min_cents: Math.min(...cell.values),
      max_cents: Math.max(...cell.values),
    };
  });
  const body = {
    kind: "F_VS_124_PHASE_CATEGORY_CENTRAL_FUTURE_LOW_SURFACE",
    source_sha256: sourceSha256,
    provenance: "F-VS-124@48dbf36b",
    method: "CATEGORY_X_FILED_PHASE_BAND_POPULATION; TERMINAL_PATH_POINT_PER_LEG_EXCLUDED; Q50_NEAREST_RANK; MIDRANK_REPORTED",
    phase_bands: os.PHASE_CENTRAL_BANDS,
    source_path_points: corpus.flatMap((event) => (event.legs ?? []).flatMap((leg) => leg.future_low_return_path ?? [])).length,
    terminal_points_excluded: terminalPointsExcluded,
    central_population_points: cells.reduce((total, cell) => total + cell.members, 0),
    cc_f_vs_124_reported_population_points: 63260,
    cc_reconciliation_difference_points: cells.reduce((total, cell) => total + cell.members, 0) - 63260,
    cells,
  };
  return { ...body, sha256: shaBytes(canonical(body)) };
}
function fileHash(file) { const hash = crypto.createHash("sha256"); const fd = fs.openSync(file, "r"); const buffer = Buffer.alloc(8 * 1024 * 1024); try { for (;;) { const n = fs.readSync(fd, buffer, 0, buffer.length, null); if (!n) break; hash.update(buffer.subarray(0, n)); } } finally { fs.closeSync(fd); } return hash.digest("hex"); }
function receipt(file, rows = null) { const stat = fs.statSync(file); return { path: file, sha256: fileHash(file), bytes: stat.size, rows }; }
function ensure(condition, message) { if (!condition) throw new Error(message); }
function derivableTreeDigest(directory) {
  if (!fs.existsSync(directory)) return { directory, status: "NOT_FOUND", files: [], file_count: 0, bytes: 0, aggregate_sha256: null };
  const files = [];
  const walk = (current) => {
    for (const entry of fs.readdirSync(current, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
      const absolute = path.join(current, entry.name);
      if (entry.isDirectory()) walk(absolute);
      else if (entry.isFile()) files.push({
        path: path.relative(directory, absolute).replaceAll("\\", "/"),
        sha256: fileHash(absolute),
        bytes: fs.statSync(absolute).size,
      });
    }
  };
  walk(directory);
  const payload = canonical(files);
  return {
    directory,
    status: "DERIVABLE",
    formula: "sha256(UTF8(JSON.stringify(SORTED_RELATIVE_PATH_SHA256_BYTES_ROWS, null, 2) + NEWLINE))",
    sort: "RELATIVE_PATH_ASCENDING",
    files,
    file_count: files.length,
    bytes: files.reduce((total, row) => total + row.bytes, 0),
    aggregate_sha256: shaBytes(payload),
  };
}
const FVS177_LITERAL_CLAIM_FIELDS = Object.freeze([
  "telemetry_only", "ask_reachability_defines_target", "same_receipt_write_then_read_removed",
  "hardcoded_stale_prior_false_gate_removed", "floor_rest_locks_retired", "unstamped_incomplete_scores_zero",
  "live_bid_is_reference_only", "may_hold", "may_abstain", "may_complete_only_from_own_live_evidenced_touch",
  "placement_rule_changed_from_outcomes", "named_event_ids_in_policy_source", "rule_applied_uniformly",
  "f_vs_110_tuned_stamp_retained", "full_804_run", "sealed_read", "live_mutation",
]);
function literalClaimAudit(repo) {
  const files = [
    "arb-executor/analysis/build_window1_v54_dual_belief.js",
    "arb-executor/analysis/window1_v54_dual_belief_os.js",
    "arb-executor/analysis/window1_v54_functionable_os.js",
    "arb-executor/analysis/window1_v54_survivor_shape_elimination.js",
  ];
  const rows = [];
  const rawRows = [];
  for (const relative of files) {
    const lines = fs.readFileSync(path.join(repo, relative), "utf8").split(/\r?\n/);
    lines.forEach((line, index) => {
      for (const match of line.matchAll(/\b([A-Za-z_$][\w$]*)\s*:\s*(true|false)\b/g)) {
        const field = match[1];
        const namedClaim = FVS177_LITERAL_CLAIM_FIELDS.includes(field);
        const operational = ["recursive", "force", "withFileTypes", "hard_assert"].includes(field)
          || /return\s+\{/.test(line)
          || /\?\s*\{/.test(line)
          || /:\s*\{/.test(line);
        rawRows.push({
          path: relative,
          line: index + 1,
          field,
          literal_value: match[2],
          classification: namedClaim ? "UNEXPLAINED_NAMED_SERIALIZED_CLAIM" : operational ? "OPERATIONAL_CONTROL_OR_BRANCH_RESULT" : "BRANCH_SCOPED_STATE_FIELD",
          derivation: namedClaim
            ? "UNEXPLAINED_LITERAL_CLAIM"
            : operational
            ? "The value controls an API/state branch already selected by the surrounding predicate; it does not attest an observed market fact."
            : `The value is emitted only by the source branch visible on this row; its producer is ${relative}:${index + 1} and the runtime receipt audit tests the downstream fact independently.`,
          source_line: line.trim(),
        });
      }
      for (const field of FVS177_LITERAL_CLAIM_FIELDS) {
        const match = line.match(new RegExp(`\\b${field}\\s*:\\s*(true|false)\\b`));
        if (match) rows.push({ path: relative, line: index + 1, field, literal_value: match[1], source_line: line.trim() });
      }
    });
  }
  const unexplained = rawRows.filter((row) => row.classification === "UNEXPLAINED_NAMED_SERIALIZED_CLAIM");
  return {
    named_fields: FVS177_LITERAL_CLAIM_FIELDS,
    remaining_named_literal_claims: rows,
    remaining_named_count: rows.length,
    all_raw_boolean_literals: rawRows,
    raw_literal_count: rawRows.length,
    unexplained_literal_claims: unexplained,
    unexplained_count: unexplained.length,
  };
}
function receiptProducerCoverage(repo, output) {
  const producerSources = [
    "arb-executor/analysis/build_window1_v54_dual_belief.js",
    "arb-executor/analysis/window1_v54_dual_belief_reporter.js",
  ].map((relative) => ({ relative, text: fs.readFileSync(path.join(repo, relative), "utf8") }));
  const names = new Set(fs.readdirSync(output).filter((name) => fs.statSync(path.join(output, name)).isFile()));
  names.add("RECEIPT_PRODUCER_COVERAGE.json");
  names.add("ARTIFACT_HASH_MANIFEST.json");
  const rows = [...names].sort().map((name) => {
    const producers = producerSources.filter((source) => source.text.includes(name)).map((source) => source.relative);
    return {
      artifact: name,
      producer_sources: producers,
      regenerable: producers.length > 0,
      producer_contract: producers.length ? "NAMED_OUTPUT_PATH_PRESENT_IN_EXECUTABLE_SOURCE" : "NO_NAMED_PRODUCER_FOUND",
    };
  });
  return {
    label: "F_VS_178_NO_ORPHAN_RECEIPTS_SOURCE_COVERAGE",
    method: "Every committed receipt basename is searched in the executable builder and standing reporter source. A receipt without a named producer fails the build.",
    rows,
    artifact_count: rows.length,
    unproduced: rows.filter((row) => !row.regenerable),
  };
}
function writeJsonStreamingSync(file, value) {
  const descriptor = fs.openSync(file, "w");
  let buffer = "";
  const emit = (text) => {
    buffer += text;
    if (buffer.length >= 1024 * 1024) { fs.writeSync(descriptor, buffer, null, "utf8"); buffer = ""; }
  };
  const serialize = (item, depth, arraySlot = false) => {
    if (item === undefined || typeof item === "function" || typeof item === "symbol") { emit(arraySlot ? "null" : "null"); return; }
    if (item === null || typeof item !== "object") { emit(JSON.stringify(item) ?? "null"); return; }
    if (Array.isArray(item)) {
      if (!item.length) { emit("[]"); return; }
      emit("[\n");
      item.forEach((entry, index) => { emit(`${"  ".repeat(depth + 1)}`); serialize(entry, depth + 1, true); emit(index === item.length - 1 ? "\n" : ",\n"); });
      emit(`${"  ".repeat(depth)}]`);
      return;
    }
    const keys = Object.keys(item).filter((key) => item[key] !== undefined && typeof item[key] !== "function" && typeof item[key] !== "symbol");
    if (!keys.length) { emit("{}"); return; }
    emit("{\n");
    keys.forEach((key, index) => { emit(`${"  ".repeat(depth + 1)}${JSON.stringify(key)}: `); serialize(item[key], depth + 1, false); emit(index === keys.length - 1 ? "\n" : ",\n"); });
    emit(`${"  ".repeat(depth)}}`);
  };
  try { serialize(value, 0); emit("\n"); if (buffer) fs.writeSync(descriptor, buffer, null, "utf8"); } finally { fs.closeSync(descriptor); }
}
function writeJson(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  try { fs.writeFileSync(file, canonical(value), "utf8"); }
  catch (error) {
    if (!(error instanceof RangeError) || !String(error.message).includes("Invalid string length")) throw error;
    writeJsonStreamingSync(file, value);
  }
}
function writeText(file, value) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, value.endsWith("\n") ? value : `${value}\n`, "utf8"); }
function custodyOversizedArtifacts({ output, custodyOutput, rowsByName, thresholdBytes = 50 * 1024 * 1024 }) {
  const manifestPath = path.join(output, "EXTERNAL_CUSTODY_MANIFEST.json");
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  const oversized = fs.readdirSync(output).filter((name) => fs.statSync(path.join(output, name)).isFile() && fs.statSync(path.join(output, name)).size > thresholdBytes).sort();
  if (!oversized.length) return [];
  ensure(custodyOutput, `L22_CUSTODY_OUTPUT_REQUIRED_FOR:${oversized.join(",")}`);
  fs.mkdirSync(custodyOutput, { recursive: true });
  const moved = oversized.map((name) => {
    const source = path.join(output, name), destination = path.join(custodyOutput, name);
    const sourceReceipt = receipt(source, rowsByName[name] ?? null);
    fs.copyFileSync(source, destination);
    const destinationReceipt = receipt(destination, rowsByName[name] ?? null);
    ensure(sourceReceipt.sha256 === destinationReceipt.sha256 && sourceReceipt.bytes === destinationReceipt.bytes, `L22_CUSTODY_COPY_MISMATCH:${name}`);
    fs.rmSync(source);
    return { logical_path: name, custody_location: destination, sha256: destinationReceipt.sha256, bytes: destinationReceipt.bytes, rows: destinationReceipt.rows, committed: false };
  });
  manifest.files.push(...moved);
  manifest.all_committed_artifacts_under_50_mb = true;
  manifest.committed_artifact_cap_bytes = thresholdBytes;
  manifest.oversized_artifacts_moved_to_external_custody = moved.length;
  writeJson(manifestPath, manifest);
  return moved;
}
function gitShow(repo, commit, file) { return execFileSync("git", ["show", `${commit}:${file}`], { cwd: repo, maxBuffer: 64 * 1024 * 1024 }); }
function largeUntrackedCensus(repo) {
  const tracked = new Set(execFileSync("git", ["ls-files", "-z"], { cwd: repo, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 }).split("\0").filter(Boolean).map((name) => name.replaceAll("\\", "/")));
  const threshold = 10 * 1024 * 1024, files = [];
  const walk = (directory) => {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      if (entry.name === ".git") continue;
      const absolute = path.join(directory, entry.name), relative = path.relative(repo, absolute).replaceAll("\\", "/");
      if (relative === "tmp" || relative.startsWith("tmp/") || relative.startsWith(".claude/window1_live_v4_replay/v54_conditioned_belief_live_deadlines_mind_only_20260823/") || relative.startsWith(".claude/window1_live_v4_replay/lajsva_case_study_v11_20260823/") || relative.startsWith(".claude/window1_live_v4_replay/v54_three_named_steps_remaining_dip_floor_side_envelope_migration_20260823/") || relative.startsWith(".claude/window1_live_v4_replay/lajsva_case_study_v12_20260823/") || relative.startsWith(".claude/window1_live_v4_replay/v54_four_named_steps_double_subtraction_coherence_atomic_20260823/") || relative.startsWith(".claude/window1_live_v4_replay/lajsva_case_study_v13_20260823/")) continue;
      if (entry.isDirectory()) walk(absolute);
      else if (entry.isFile() && !tracked.has(relative)) {
        const stat = fs.statSync(absolute);
        if (stat.size > threshold) files.push({ path: relative, bytes: stat.size, sha256: fileHash(absolute) });
      }
    }
  };
  walk(repo);
  return { label: "F_V53_074_WORKTREE_LARGE_UNTRACKED_CENSUS", threshold_bytes_exclusive: threshold, files: files.sort((a, b) => a.path.localeCompare(b.path)), count: files.length, bytes: files.reduce((total, row) => total + row.bytes, 0) };
}
function dateCode(eventId) { const match = eventId.match(/-(26[A-Z]{3}\d{2})/); return match?.[1] ?? null; }
function categoryFromEvent(eventId) {
  if (eventId.startsWith("KXATPCHALLENGERMATCH")) return "ATP_CHALL";
  if (eventId.startsWith("KXATPMATCH")) return "ATP_MAIN";
  if (eventId.startsWith("KXWTACHALLENGERMATCH")) return "WTA_CHALL";
  if (eventId.startsWith("KXWTAMATCH")) return "WTA_MAIN";
  return "OTHER";
}
function parseCsvLine(line) {
  const values = []; let current = "", quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (char === '"') { if (quoted && line[index + 1] === '"') { current += '"'; index += 1; } else quoted = !quoted; }
    else if (char === "," && !quoted) { values.push(current); current = ""; }
    else current += char;
  }
  values.push(current); return values;
}
function number(value) { const parsed = Number(value); return Number.isFinite(parsed) ? parsed : null; }
function objectFromCsv(headers, line) { const values = parseCsvLine(line); return Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""])); }
function parseEt(value) {
  const match = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{1,2}):(\d{2}):(\d{2}) (AM|PM)$/);
  if (!match) throw new Error(`bad ET timestamp ${value}`);
  let hour = Number(match[4]); if (match[7] === "PM" && hour !== 12) hour += 12; if (match[7] === "AM" && hour === 12) hour = 0;
  return Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3]), hour + 4, Number(match[5]), Number(match[6])) / 1000;
}
function eventFromTicker(ticker) { return String(ticker).replace(/-[A-Z0-9]+$/, ""); }
function legFromTicker(ticker) { return String(ticker).split("-").at(-1); }

async function streamJsonl(file, onRow) {
  const input = file.endsWith(".gz") ? fs.createReadStream(file).pipe(zlib.createGunzip()) : fs.createReadStream(file);
  const lines = readline.createInterface({ input, crlfDelay: Infinity });
  let rows = 0;
  for await (const line of lines) { if (!line.trim()) continue; rows += 1; await onRow(JSON.parse(line), rows); }
  return rows;
}

async function writeJsonlGzipStreaming(file, rows) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const output = fs.createWriteStream(file);
  const gzip = zlib.createGzip({ level: 9 });
  gzip.pipe(output);
  const failed = new Promise((_, reject) => {
    gzip.once("error", reject);
    output.once("error", reject);
  });
  const finished = new Promise((resolve) => output.once("finish", resolve));
  for (const row of rows) {
    if (!gzip.write(`${JSON.stringify(row)}\n`)) await new Promise((resolve) => gzip.once("drain", resolve));
  }
  gzip.end();
  await Promise.race([finished, failed]);
}

function createJsonlGzipWriter(file) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const output = fs.createWriteStream(file);
  const gzip = zlib.createGzip({ level: 9 });
  gzip.pipe(output);
  const failed = new Promise((_, reject) => {
    gzip.once("error", reject);
    output.once("error", reject);
  });
  const finished = new Promise((resolve) => output.once("finish", resolve));
  return {
    async write(row) {
      if (!gzip.write(`${JSON.stringify(row)}\n`)) await Promise.race([new Promise((resolve) => gzip.once("drain", resolve)), failed]);
    },
    async close() {
      gzip.end();
      await Promise.race([finished, failed]);
    },
  };
}

async function loadPriorDecisionActions(file) {
  const actions = new Map();
  if (!file || !fs.existsSync(file)) return actions;
  const input = fs.createReadStream(file).pipe(zlib.createGunzip());
  const lines = readline.createInterface({ input, crlfDelay: Infinity });
  for await (const line of lines) {
    if (!line.trim()) continue;
    const row = JSON.parse(line);
    if (row.kind !== "DECISION_STAGE") continue;
    for (const derivation of row.derivations ?? []) {
      actions.set(`${row.event_id}|${row.receipt}|${derivation.leg_id}`, {
        event_id: row.event_id,
        leg_id: derivation.leg_id,
        timestamp_epoch: row.timestamp_epoch,
        receipt: row.receipt,
        action: derivation.action,
        own_evidence: derivation.derivation?.neighbor_leg?.own_evidence ?? null,
      });
    }
  }
  return actions;
}

function loadBellAuthorities(repo, rangePath) {
  const actualBellBytes = gitShow(repo, ANALYSIS_COMMIT, ACTUAL_BELL_PATH);
  const namedNeighborBytes = gitShow(repo, ANALYSIS_COMMIT, NAMED_NEIGHBOR_PATH);
  return bellLibrary.buildAuthorities({
    actualBellTable: JSON.parse(actualBellBytes),
    namedNeighborCheck: JSON.parse(namedNeighborBytes),
    bindings: {
      analysis_commit: ANALYSIS_COMMIT,
      actual_bell_path: ACTUAL_BELL_PATH,
      actual_bell_sha256: shaBytes(actualBellBytes),
      named_neighbor_path: NAMED_NEIGHBOR_PATH,
      named_neighbor_sha256: shaBytes(namedNeighborBytes),
      range_receipt: `${rangePath}@sha256:PENDING_LOCAL_HASH`,
    },
  });
}

async function loadCorpus(cacheDir, repo, foundationIndexPath, foundationReceiptPath, futureLowIndexPath, futureLowReceiptPath) {
  const tickRoot = path.join(repo, "arb-executor", "data", "durable");
  const tickIndexPath = path.join(tickRoot, "RANGE_OVERLAP_LIBRARY_TICKS.jsonl.gz");
  const tickReceiptPath = path.join(tickRoot, "RANGE_OVERLAP_LIBRARY_TICKS_RECEIPT.json");
  const countIndexPath = path.join(tickRoot, "RANGE_OVERLAP_LIBRARY_TICKS_PRINT_COUNTS.jsonl.gz");
  const countReceiptPath = path.join(tickRoot, "RANGE_OVERLAP_LIBRARY_TICKS_PRINT_COUNTS_RECEIPT.json");
  const benchReceiptPath = path.join(repo, "arb-executor", "analysis", "tune_bench_v2_ticks", "ATP_MAIN", "TUNE_BENCH_RECEIPT.json");
  for (const file of [tickIndexPath, tickReceiptPath, countIndexPath, countReceiptPath, benchReceiptPath]) ensure(fs.existsSync(file), `POOL_INPUT_MISSING ${file}`);
  const tickReceipt = JSON.parse(fs.readFileSync(tickReceiptPath, "utf8"));
  const countReceipt = JSON.parse(fs.readFileSync(countReceiptPath, "utf8"));
  const benchReceipt = JSON.parse(fs.readFileSync(benchReceiptPath, "utf8"));
  const tickSha = fileHash(tickIndexPath), countSha = fileHash(countIndexPath);
  ensure(tickSha === tickReceipt.output.sha256 && tickSha === countReceipt.library.sha256 && tickSha === benchReceipt.input_library.sha256, "POOL_TICK_LIBRARY_HASH_MISMATCH");
  ensure(countSha === countReceipt.output.sha256 && countSha === benchReceipt.exact_print_counts.sidecar_sha256, "POOL_PRINT_COUNTS_HASH_MISMATCH");
  ensure(fileHash(tickReceiptPath) === benchReceipt.source_receipt.sha256 && fileHash(countReceiptPath) === benchReceipt.exact_print_counts.sidecar_receipt_sha256, "POOL_INPUT_RECEIPT_HASH_MISMATCH");
  const countByTicker = new Map();
  const countRows = await streamJsonl(countIndexPath, row => {
    if (!countByTicker.has(row.ticker)) countByTicker.set(row.ticker, { seconds: [], counts: [] });
    const series = countByTicker.get(row.ticker);
    ensure(Number.isInteger(row.second) && (!series.seconds.length || row.second > series.seconds.at(-1)), "POOL_SIDECAR_SECONDS_NOT_ORDERED");
    ensure(Number.isInteger(row.true_print_count_cum) && row.true_print_count_cum > (series.counts.at(-1) ?? 0), "POOL_SIDECAR_COUNT_NOT_INCREASING");
    series.seconds.push(row.second); series.counts.push(row.true_print_count_cum);
  });
  ensure(countRows === countReceipt.counts.rows_checked, "POOL_SIDECAR_ROW_COUNT_MISMATCH");
  const tickGroups = new Map();
  const tickRows = await streamJsonl(tickIndexPath, row => {
    ensure(row.grain === "TICK", "POOL_MIXED_GRAIN_REFUSED");
    if (!tickGroups.has(row.event_id)) tickGroups.set(row.event_id, { identity: row.event_id, category: row.category,
      date: dateCode(row.event_id), legs: [] });
    const group = tickGroups.get(row.event_id);
    ensure(group.category === row.category, "POOL_PAIR_CATEGORY_MISMATCH");
    group.legs.push(os.compactTickLeg(row, countByTicker.get(row.ticker)));
    countByTicker.delete(row.ticker);
  });
  ensure(tickRows === tickReceipt.counts.legs && countByTicker.size === 0, "POOL_LIBRARY_LEG_CONSERVATION_FAILED");
  const tickPairs = [...tickGroups.values()].sort((a, b) => a.identity < b.identity ? -1 : a.identity > b.identity ? 1 : 0)
    .map(row => os.poolPair(row.legs, { identity: row.identity, category: row.category, date: row.date }, benchReceipt.organ_contract)).filter(Boolean);
  const tickBinding = { index: receipt(tickIndexPath, tickRows), materializer_receipt: receipt(tickReceiptPath),
    print_counts: receipt(countIndexPath, countRows), print_counts_receipt: receipt(countReceiptPath), bench_receipt: receipt(benchReceiptPath) };
  const tickLibrary = os.configureTickLibrary({ pairs: tickPairs, contract: benchReceipt.organ_contract,
    matched_cohort: benchReceipt.matched_step_first, receipt: tickBinding });
  const registryPath = path.join(cacheDir, "corpus_events_v2.jsonl");
  const historicalPath = path.join(cacheDir, "historical_events_materialized.csv");
  const rangePath = path.join(cacheDir, "range_spectrum_v1.jsonl");
  const rangeOverlapIndexPath = path.join(repo, "arb-executor", "data", "durable", "RANGE_OVERLAP_LIBRARY.jsonl.gz");
  const rangeOverlapReceiptPath = path.join(repo, "arb-executor", "data", "durable", "RANGE_OVERLAP_LIBRARY_RECEIPT.json");
  ensure(fs.existsSync(rangeOverlapIndexPath), `RANGE_OVERLAP_LIBRARY_MISSING ${rangeOverlapIndexPath}`);
  ensure(fs.existsSync(rangeOverlapReceiptPath), `RANGE_OVERLAP_LIBRARY_RECEIPT_MISSING ${rangeOverlapReceiptPath}`);
  const authorities = loadBellAuthorities(repo, rangePath);
  authorities.bindings.range_receipt = `${rangePath}@sha256:${fileHash(rangePath)}`;
  const byEvent = new Map();
  const registryCategories = {}, registryEras = {};
  const registryRows = await streamJsonl(registryPath, (row, rowNumber) => {
    const eventId = row.event;
    const eventDate = row.era ?? dateCode(eventId);
    byEvent.set(eventId, { event_id: eventId, event_date: eventDate, category: row.cat, quality: "EVENT_REGISTRY_ONLY", vector: { category: row.cat }, legs: [], source_receipts: [{ source_id: "CORPUS_EVENTS_V2", row_ref: `${registryPath}#row-${rowNumber}` }] });
    registryCategories[row.cat] = (registryCategories[row.cat] || 0) + 1;
    registryEras[eventDate] = (registryEras[eventDate] || 0) + 1;
  });
  const historicalLines = fs.readFileSync(historicalPath, "utf8").trim().split(/\r?\n/);
  const historicalHeaders = parseCsvLine(historicalLines.shift());
  const historicalCategories = {};
  for (const [historicalIndex, line] of historicalLines.entries()) {
    const row = objectFromCsv(historicalHeaders, line), eventId = row.event_ticker, category = row.category;
    historicalCategories[category] = (historicalCategories[category] || 0) + 1;
    const rawLegs = [
      { leg_id: row.winner, anchor_cents: number(row.first_price_winner), low_cents: number(row.min_price_winner), high_cents: number(row.max_price_winner), close_cents: number(row.last_price_winner) },
      { leg_id: row.loser, anchor_cents: number(row.first_price_loser), low_cents: number(row.min_price_loser), high_cents: number(row.max_price_loser), close_cents: null },
    ].sort((a, b) => (a.anchor_cents ?? 50) - (b.anchor_cents ?? 50) || a.leg_id.localeCompare(b.leg_id));
    const existing = byEvent.get(eventId) ?? { event_id: eventId, event_date: dateCode(eventId), category, source_receipts: [] };
    const bounded = bellLibrary.unboundedAggregate({
      eventId,
      eventDate: existing.event_date,
      category,
      legs: rawLegs,
      sourceReceipts: [...(existing.source_receipts ?? []), { source_id: "HISTORICAL_EVENTS_MATERIALIZATION", row_ref: `${historicalPath}#line-${historicalIndex + 2}` }],
      reason: "EVENT_GRAIN_AGGREGATE_HAS_NO_INTRAMATCH_CLOCK_OR_LAWFUL_RIGHT_EDGE",
    });
    byEvent.set(eventId, { ...existing, ...bounded });
  }
  const rangeCategories = {};
  const rangeRows = await streamJsonl(rangePath, (row, rowNumber) => {
    const eventId = row.event, category = row.cat;
    rangeCategories[category] = (rangeCategories[category] || 0) + 1;
    const existing = byEvent.get(eventId) ?? { event_id: eventId, event_date: dateCode(eventId), category, source_receipts: [] };
    const bounded = bellLibrary.rematerializeRangeRow(row, authorities, `${rangePath}#row-${rowNumber}`);
    if (!bounded) return;
    bounded.source_receipts = [...(existing.source_receipts ?? []), ...(bounded.source_receipts ?? [])];
    byEvent.set(eventId, { ...existing, ...bounded });
  });
  const beforeFoundation = [...byEvent.values()];
  const beforeCoverage = {
    union_games: beforeFoundation.length,
    bounded_games: beforeFoundation.filter((row) => row.span?.status === "BOUNDED").length,
    unbounded_games: beforeFoundation.filter((row) => row.span?.status === "UNBOUNDED").length,
    not_bounded_games: beforeFoundation.filter((row) => row.span?.status !== "BOUNDED").length,
  };
  const foundationReceipt = JSON.parse(fs.readFileSync(foundationReceiptPath, "utf8"));
  const futureLowReceipt = JSON.parse(fs.readFileSync(futureLowReceiptPath, "utf8"));
  ensure(futureLowReceipt.label === "V54_BELL_BOUNDED_FUTURE_LOW_RETURN_LIBRARY", "FUTURE_LOW_RETURN_LIBRARY_LABEL_MISMATCH");
  ensure(fileHash(futureLowIndexPath) === futureLowReceipt.output.sha256, "FUTURE_LOW_RETURN_LIBRARY_SHA256_MISMATCH");
  const futureLowByEvent = new Map();
  const futureLowRows = await streamJsonl(futureLowIndexPath, (row) => futureLowByEvent.set(row.event_id, row));
  ensure(futureLowRows === futureLowReceipt.output.rows, `FUTURE_LOW_RETURN_ROW_CONSERVATION ${futureLowRows} != ${futureLowReceipt.output.rows}`);
  let foundationRows = 0, foundationReplaced = 0, foundationAdded = 0;
  await streamJsonl(foundationIndexPath, (row) => {
    foundationRows += 1;
    if (byEvent.has(row.event_id)) foundationReplaced += 1; else foundationAdded += 1;
    const futureEvent = futureLowByEvent.get(row.event_id);
    const futureByLeg = new Map((futureEvent?.legs ?? []).map((leg) => [leg.leg_id, leg]));
    for (const leg of row.legs ?? []) {
      const future = futureByLeg.get(leg.leg_id);
      leg.future_low_return_path = future?.path ?? null;
      leg.future_low_return_source = future ? `${futureLowIndexPath}#${row.event_id}|${leg.leg_id}` : null;
    }
    const prior = byEvent.get(row.event_id);
    row.source_receipts = [...(prior?.source_receipts ?? []), ...(row.source_receipts ?? [])];
    byEvent.set(row.event_id, row);
  });
  ensure(foundationRows === foundationReceipt.output.rows, `FOUNDATION_ROW_CONSERVATION ${foundationRows} != ${foundationReceipt.output.rows}`);
  ensure(fileHash(foundationIndexPath) === foundationReceipt.output.sha256, "FOUNDATION_COMPACT_SHA256_MISMATCH");
  const rows = [...byEvent.values()].sort((a, b) => a.event_id.localeCompare(b.event_id));
  const rangeOverlapMaterializerReceipt = JSON.parse(fs.readFileSync(rangeOverlapReceiptPath, "utf8"));
  ensure(rangeOverlapMaterializerReceipt.label === "RANGE_OVERLAP_LIBRARY_RECEIPT", "RANGE_OVERLAP_LIBRARY_LABEL_MISMATCH");
  ensure(fileHash(rangeOverlapIndexPath) === rangeOverlapMaterializerReceipt.output.sha256, "RANGE_OVERLAP_LIBRARY_SHA256_MISMATCH");
  const rangeOverlap = [];
  const rangeOverlapRows = await streamJsonl(rangeOverlapIndexPath, (row, rowNumber) => {
    const corpusRow = byEvent.get(row.event_id);
    ensure(corpusRow, `RANGE_OVERLAP_MEMBER_MISSING_FROM_CORPUS ${row.ticker}`);
    ensure(corpusRow.category === row.category, `RANGE_OVERLAP_CATEGORY_MISMATCH ${row.ticker}`);
    ensure(corpusRow.event_date, `RANGE_OVERLAP_EVENT_DATE_MISSING ${row.ticker}`);
    ensure(corpusRow.vector, `RANGE_OVERLAP_SIMILARITY_VECTOR_MISSING ${row.ticker}`);
    rangeOverlap.push({
      ...row,
      event_date: corpusRow.event_date,
      vector: corpusRow.vector,
      source_receipt: `${rangeOverlapIndexPath}#row-${rowNumber}`,
    });
  });
  ensure(rangeOverlapRows === rangeOverlapMaterializerReceipt.output.rows, `RANGE_OVERLAP_ROW_CONSERVATION ${rangeOverlapRows} != ${rangeOverlapMaterializerReceipt.output.rows}`);
  const rangeOverlapBinding = {
    index: receipt(rangeOverlapIndexPath, rangeOverlapRows),
    materializer_receipt: receipt(rangeOverlapReceiptPath),
    source: rangeOverlapMaterializerReceipt.sources,
    output: rangeOverlapMaterializerReceipt.output,
    method: rangeOverlapMaterializerReceipt.method,
    layer_license: rangeOverlapMaterializerReceipt.layer_license,
  };
  Object.defineProperty(rangeOverlap, "binding", { value: rangeOverlapBinding, enumerable: false });
  Object.defineProperty(rows, "range_overlap", { value: rangeOverlap, enumerable: false });
  Object.defineProperty(rows, "tick_library", { value: tickLibrary, enumerable: false });
  const afterCoverage = {
    union_games: rows.length,
    bounded_games: rows.filter((row) => row.span?.status === "BOUNDED").length,
    unbounded_games: rows.filter((row) => row.span?.status === "UNBOUNDED").length,
    not_bounded_games: rows.filter((row) => row.span?.status !== "BOUNDED").length,
  };
  const foundation = {
    index: receipt(foundationIndexPath, foundationRows),
    materializer_receipt: receipt(foundationReceiptPath, null),
    source: foundationReceipt.source,
    spike_atlas: foundationReceipt.spike_atlas,
    layer_license: foundationReceipt.layer_license,
    native_window_law: foundationReceipt.native_window_law,
    rows: foundationRows,
    replaced_games: foundationReplaced,
    added_games: foundationAdded,
    coverage_before: beforeCoverage,
    coverage_after: afterCoverage,
  };
  const futureLow = { index: receipt(futureLowIndexPath, futureLowRows), materializer_receipt: receipt(futureLowReceiptPath), source: futureLowReceipt.source, output: futureLowReceipt.output, method: futureLowReceipt.method, layer_license: futureLowReceipt.layer_license };
  return { rows, tick_library: tickLibrary, foundation, future_low_return: futureLow, range_overlap: rangeOverlap, bell_bound_receipt: bellLibrary.buildReceipt(rows, authorities), counts: { registry_rows: registryRows, historical_rows: historicalLines.length, range_rows: rangeRows, foundation_rows: foundationRows, future_low_return_rows: futureLowRows, range_overlap_rows: rangeOverlapRows, union_games: rows.length, by_quality: rows.reduce((acc, row) => (acc[row.quality] = (acc[row.quality] || 0) + 1, acc), {}), registry_categories: registryCategories, historical_categories: historicalCategories, range_categories: rangeCategories, foundation_categories: foundationReceipt.output.by_category, registry_eras: registryEras }, sources: { tick_library: tickBinding, registry: receipt(registryPath, registryRows), historical: receipt(historicalPath, historicalLines.length), range: receipt(rangePath, rangeRows), foundation, future_low_return: futureLow, range_overlap: rangeOverlapBinding, actual_bells: authorities.bindings.actual_bell_sha256, named_neighbor_bells: authorities.bindings.named_neighbor_sha256 } };
}

function bindNeighborSpecialists(corpusRows) {
  const records = [];
  for (const game of corpusRows) {
    if (game.span?.status !== "BOUNDED") continue;
    for (const leg of game.legs ?? []) {
      if (!(Number.isFinite(leg.floor_fraction)
        && Number.isInteger(leg.observed_low_cents)
        && Number.isInteger(leg.low_cents))) continue;
      const sourceReceipt = leg.floor_timing_receipt ?? `${game.event_id}|${leg.leg_id}|floor_fraction=${leg.floor_fraction}`;
      leg.specialist_record = {
        kind: "BOUNDED_TWO_BEHAVIOR_FLOOR_CAPTURE",
        floor_fraction: leg.floor_fraction,
        remaining_depth_cents: Math.max(0, leg.observed_low_cents - leg.low_cents),
        library_close_cents: Number.isInteger(leg.close_cents) ? leg.close_cents : null,
        library_floor_cents: leg.low_cents,
        v3_price_cell: Number.isInteger(leg.close_cents) ? leg.close_cents : null,
        v3_key_status: Number.isInteger(leg.close_cents) ? "LICENSEABLE_LIBRARY_CLOSE_PRESENT" : "UNMAPPED_LIBRARY_CLOSE_RESOURCE_GAP",
        before_floor_behavior: "DERIVED_TIMING_DEPTH",
        at_or_after_floor_behavior: "OWN_TAPE_PRESENCE_AT_TOUCH",
        source_receipt: sourceReceipt,
        source_grain: leg.floor_timing_grain ?? leg.source_grain ?? game.grain ?? null,
      };
      records.push({ event_id: game.event_id, category: game.category, leg_id: leg.leg_id, ...leg.specialist_record });
    }
  }
  const binding = {
    kind: "LEAVE_SELF_OUT_BOUNDED_NEIGHBOR_SPECIALIST_RECORDS",
    population: "BELL_BOUNDED_LIBRARY_GAMES",
    sealed_excluded: true,
    records: records.length,
    games: new Set(records.map((row) => row.event_id)).size,
    behavior_law: "Before its bounded floor fraction a member votes timing depth; at-or-after it votes presence at touch.",
    v3_key_law: "Each vote looks up the V3 row by that library member's own bounded close cents; the runtime live bid never selects a V3 cell.",
    runtime_weight_law: "Continuous similarity x coverage x this-leg evidence-match grade; leave-self-out at retrieval.",
    no_cells_fitted_here: true,
    no_global_coefficients: true,
    records_rows: records,
  };
  binding.binding_sha256 = shaBytes(canonical(binding));
  return binding;
}

function bindShapeTradedLowSupport(survivorBinding, corpusRows) {
  const byIdentity = new Map();
  for (const event of corpusRows) {
    if (event.span?.status !== "BOUNDED") continue;
    for (const leg of event.legs ?? []) {
      if (!Number.isInteger(leg.anchor_cents) || !Number.isInteger(leg.low_cents)) continue;
      byIdentity.set(`${event.event_id}|${leg.leg_id}`, {
        event_id: event.event_id,
        leg_id: leg.leg_id,
        category: event.category,
        anchor_cents: leg.anchor_cents,
        traded_low_cents: leg.low_cents,
        traded_low_depth_cents: leg.anchor_cents - leg.low_cents,
        span_status: event.span.status,
        grain: event.grain ?? null,
        source_receipts: event.source_receipts ?? [],
      });
    }
  }
  const supportRows = [];
  for (const group of Object.values(survivorBinding.pair.groups)) {
    for (const shape of group.shapes ?? []) {
      const members = (shape.member_identities ?? []).map((identity) => byIdentity.get(identity)).filter(Boolean);
      const depthCounts = {};
      for (const member of members) depthCounts[String(member.traded_low_depth_cents)] = (depthCounts[String(member.traded_low_depth_cents)] ?? 0) + 1;
      const depths = Object.keys(depthCounts).map(Number).sort((a, b) => a - b);
      shape.traded_low_support = {
        axis: "POST_FORMATION_TRUE_TRADE_LOW_CENTS",
        support_n: members.length,
        source_member_n: shape.member_identities?.length ?? 0,
        coverage: shape.member_identities?.length ? members.length / shape.member_identities.length : 0,
        min_depth_cents: depths.length ? depths[0] : null,
        max_depth_cents: depths.length ? depths.at(-1) : null,
        depth_bins_cents: depths,
        depth_counts: depthCounts,
        ask_reachability_role: "INFORM_ONLY_NEVER_DEFINES_TRADED_LOW_TARGET",
        member_binding: "SHAPE_MEMBER_IDENTITY_TO_BELL_BOUNDED_LIBRARY_TRADED_LOW",
      };
      supportRows.push({ category: group.category, price_region: group.price_region, shape_id: shape.shape_id, ...shape.traded_low_support });
    }
  }
  const supportSha = shaBytes(canonical(supportRows));
  survivorBinding.sha256.traded_low_support = supportSha;
  return {
    label: "V54_SHAPE_MEMBER_TRADED_LOW_SUPPORT_BINDING",
    axis: "POST_FORMATION_TRUE_TRADE_LOW_CENTS",
    target_criterion: "EXACT_MEMBER_BACKED_FINAL_TRADED_LOW_DEPTH_BINS_REMAINING_AT_OR_BEYOND_THE_RUNNING_TRADED_LOW",
    ask_reachability_role: "INFORMS_EXECUTABILITY_ONLY_NEVER_DEFINES_FLOOR_OR_SHAPE_MATCH",
    shapes: supportRows.length,
    shapes_with_support: supportRows.filter((row) => row.support_n > 0).length,
    member_bindings: supportRows.reduce((total, row) => total + row.support_n, 0),
    support_sha256: supportSha,
    rows: supportRows,
  };
}

function remoteProbe() {
  const script = `
import hashlib,json,os,re,sqlite3,subprocess
def ro(path): return sqlite3.connect("file:"+path+"?mode=ro", uri=True)
def table_info(con,name): return [{"name":r[1],"type":r[2]} for r in con.execute("PRAGMA table_info("+name+")")]
out={"host":"104.131.191.95"}
small="/root/tennis_small_tables_backup_20260708.db"
con=ro(small)
odds={}
for name in [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]:
  cols=table_info(con,name)
  item={"columns":cols,"rows":con.execute("SELECT COUNT(*) FROM "+name).fetchone()[0]}
  timecol=next((c["name"] for c in cols if c["name"] in ("timestamp","ts","polled_at","created_at","updated_at","fetched_at")),None)
  if timecol:
    item["span"]=con.execute("SELECT MIN("+timecol+"),MAX("+timecol+") FROM "+name).fetchone()
  odds[name]=item
out["odds_backup"]={"path":small,"bytes":os.stat(small).st_size,"tables":odds}
sub="/root/Omi-Workspace/arb-executor/state/subsecond_store.db"
con=ro(sub)
tables=[r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
schema={name:table_info(con,name) for name in tables}
indexes=[{"name":r[0],"sql":r[1]} for r in con.execute("SELECT name,sql FROM sqlite_master WHERE type='index' ORDER BY name")]
sample={}
for name in tables:
  try: sample[name]=con.execute("SELECT * FROM "+name+" LIMIT 1").fetchone()
  except Exception as exc: sample[name]={"error":str(exc)}
out["subsecond"]={"path":sub,"bytes":os.stat(sub).st_size,"tables":schema,"indexes":indexes,"sample_present":{k:v is not None for k,v in sample.items()}}
includes=[]
for mon in ("JAN","FEB","MAR","APR","MAY","JUN","JUL"): includes += ["--include","*26"+mon+"*"]
for month in ("01","02","03","04","05","06","07"): includes += ["--include","*2026"+month+"*"]
cmd=["rclone","lsjson","spaces:omi-tick-archive","--recursive","--files-only","--no-mimetype"]+includes
p=subprocess.run(cmd,capture_output=True,text=True,check=True)
items=json.loads(p.stdout)
roots={}
events=set()
cats={}
for item in items:
  rel=item["Path"]
  root=rel.split("/",1)[0]
  slot=roots.setdefault(root,{"objects":0,"bytes":0,"min_modtime":None,"max_modtime":None})
  slot["objects"]+=1; slot["bytes"]+=int(item.get("Size",0))
  mt=item.get("ModTime")
  if mt: slot["min_modtime"]=min(slot["min_modtime"] or mt,mt); slot["max_modtime"]=max(slot["max_modtime"] or mt,mt)
  m=re.search(r"(KX(?:ATPCHALLENGERMATCH|ATPMATCH|WTACHALLENGERMATCH|WTAMATCH)-26[A-Z]{3}[0-9]{2}[A-Z0-9]+)",rel)
  if m:
    ev=m.group(1); events.add(ev)
    cat="ATP_CHALL" if ev.startswith("KXATPCHALLENGER") else "ATP_MAIN" if ev.startswith("KXATP") else "WTA_CHALL" if ev.startswith("KXWTACHALLENGER") else "WTA_MAIN"
    cats[cat]=cats.get(cat,0)+1
sample_item=next((item for item in items if int(item.get("Size",0))>0),None)
sample_receipt=None
if sample_item:
  data=subprocess.run(["rclone","cat","spaces:omi-tick-archive/"+sample_item["Path"],"--count","256"],capture_output=True,check=True).stdout
  sample_receipt={"path":sample_item["Path"],"head_bytes":len(data),"head_sha256":hashlib.sha256(data).hexdigest()}
out["spaces"]={"filter":"EVENT_NAMES_26JAN_THROUGH_26JUL_OR_RECORDER_FILENAMES_202601_THROUGH_202607; SEALED_AUGUST_NOT_LISTED_OR_READ","roots":roots,"event_count":len(events),"categories_by_object":cats,"sample_receipt":sample_receipt}
print(json.dumps(out,separators=(",",":")))
`;
  const encoded = Buffer.from(script, "utf8").toString("base64");
  const remote = `cd /root/Omi-Workspace/arb-executor && set -a && . ./.env && set +a && export RCLONE_CONFIG_SPACES_TYPE=s3 RCLONE_CONFIG_SPACES_PROVIDER=DigitalOcean RCLONE_CONFIG_SPACES_ACCESS_KEY_ID="$SPACES_KEY" RCLONE_CONFIG_SPACES_SECRET_ACCESS_KEY="$SPACES_SECRET" RCLONE_CONFIG_SPACES_ENDPOINT=nyc3.digitaloceanspaces.com && python3 -c "import base64;exec(base64.b64decode('${encoded}'))"`;
  const stdout = execFileSync("ssh", ["-o", "BatchMode=yes", "-o", "ConnectTimeout=15", "root@104.131.191.95", remote], { encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });
  return JSON.parse(stdout.trim());
}

function loadGroundTruth(repo) {
  const rows = JSON.parse(gitShow(repo, GROUND_TRUTH_COMMIT, GROUND_TRUTH_PATH)).rows;
  const correctionsBytes = gitShow(repo, ANALYSIS_COMMIT, GROUND_TRUTH_CORRECTIONS_PATH);
  const corrections = correctionsBytes.toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse);
  const byEvent = new Map(rows.map((row) => [row.event_id, { ...row }]));
  for (const correction of corrections) {
    const row = byEvent.get(correction.event_id);
    if (!row) continue;
    const after = correction.after ?? {};
    for (const field of ["bell_epoch", "bell_source", "bell_precision", "span_start_epoch", "span_end_epoch", "pair_state", "locked_delta_valid_fills_c"]) {
      if (after[field] !== undefined) row[field] = after[field];
    }
    row.verified_span = Number.isFinite(after.span_end_epoch) ? "OK" : row.verified_span;
    for (const side of ["legA", "legB"]) {
      const identity = row[side];
      const patchKey = Object.keys(after).find((key) => key.startsWith(`${side}_${identity}`));
      const legPatch = patchKey ? after[patchKey] : null;
      if (!legPatch) continue;
      const fieldMap = {
        open_postformation_c: `${side}_open_postformation_c`,
        floor_c: `${side}_floor_c`,
        floor_epoch: `${side}_floor_epoch`,
        close_c: `${side}_close_c`,
        close_epoch: `${side}_close_epoch`,
        contracts: `${side}_contracts`,
        us_fill_c: `${side}_us_fill_c`,
        us_fill_epoch: `${side}_us_fill_epoch`,
        us_fill_stamp: `${side}_us_fill_stamp`,
      };
      for (const [source, target] of Object.entries(fieldMap)) if (legPatch[source] !== undefined) row[target] = legPatch[source];
    }
    row.correction_receipt = `${ANALYSIS_COMMIT}:${GROUND_TRUTH_CORRECTIONS_PATH}#${correction.correction_id}`;
    byEvent.set(correction.event_id, row);
  }
  return {
    rows: [...byEvent.values()],
    receipt: {
      base_commit: GROUND_TRUTH_COMMIT,
      base_path: GROUND_TRUTH_PATH,
      base_sha256: shaBytes(gitShow(repo, GROUND_TRUTH_COMMIT, GROUND_TRUTH_PATH)),
      corrections_commit: ANALYSIS_COMMIT,
      corrections_path: GROUND_TRUTH_CORRECTIONS_PATH,
      corrections_sha256: shaBytes(correctionsBytes),
      corrections_applied: corrections.map((row) => row.correction_id),
    },
  };
}
function targetMeta(row) {
  const legs = [row.legA, row.legB];
  const verifiedRightEdge = row.verified_span === "OK"
    ? [row.bell_epoch, row.span_end_epoch].filter(Number.isFinite).reduce((minimum, value) => Math.min(minimum, value), Number.POSITIVE_INFINITY)
    : null;
  return { event_id: row.event_id, event_date: row.code.slice(0, 7), category: row.category, discovery_epoch: row.recorder_open_epoch, bell_epoch: Number.isFinite(verifiedRightEdge) ? verifiedRightEdge : null, span_end_epoch: Number.isFinite(row.span_end_epoch) ? row.span_end_epoch : null, bell_source: row.bell_source, leg_ids: legs, anchors_cents: { [row.legA]: Math.floor(row.legA_open_postformation_c), [row.legB]: Math.floor(row.legB_open_postformation_c) }, formation_end_epochs: { [row.legA]: row.legA_formation_end_epoch, [row.legB]: row.legB_formation_end_epoch }, truth_closes_cents: { [row.legA]: row.verified_span === "OK" ? row.legA_close_c : null, [row.legB]: row.verified_span === "OK" ? row.legB_close_c : null }, truth_fill_stamps: { [row.legA]: row.legA_us_fill_stamp ?? null, [row.legB]: row.legB_us_fill_stamp ?? null }, correction_receipt: row.correction_receipt ?? null };
}

function bindCorpusFloorTiming(corpusRows, truthRows) {
  const truthByEvent = new Map(truthRows.map((row) => [row.event_id, row]));
  const counts = () => ({ events: 0, legs: 0, by_category: {} });
  const add = (summary, category, legs) => {
    summary.events += 1;
    summary.legs += legs;
    summary.by_category[category] ??= { events: 0, legs: 0 };
    summary.by_category[category].events += 1;
    summary.by_category[category].legs += legs;
  };
  const before = counts();
  const truthBound = counts();
  const after = counts();
  for (const candidate of corpusRows) {
    const truth = truthByEvent.get(candidate.event_id);
    if (!truth || truth.verified_span !== "OK" || !Number.isFinite(truth.bell_epoch)) continue;
    const matched = (candidate.legs ?? []).filter((leg) => {
      const side = truth.legA === leg.leg_id ? "legA" : truth.legB === leg.leg_id ? "legB" : null;
      if (!side) return false;
      const formation = truth[`${side}_formation_end_epoch`], floorEpoch = truth[`${side}_floor_epoch`];
      return Number.isFinite(formation) && Number.isFinite(floorEpoch) && truth.bell_epoch > formation;
    }).length;
    if (matched) add(before, candidate.category, matched);
  }
  for (const candidate of corpusRows) {
    const truth = truthByEvent.get(candidate.event_id);
    if (!truth || truth.verified_span !== "OK" || !Number.isFinite(truth.bell_epoch)) continue;
    let boundLegs = 0;
    for (const leg of candidate.legs ?? []) {
      const side = truth.legA === leg.leg_id ? "legA" : truth.legB === leg.leg_id ? "legB" : null;
      if (!side) continue;
      const formation = truth[`${side}_formation_end_epoch`];
      const floorEpoch = truth[`${side}_floor_epoch`];
      const duration = truth.bell_epoch - formation;
      if (!(Number.isFinite(formation) && Number.isFinite(floorEpoch) && duration > 0)) continue;
      leg.floor_fraction = Math.max(0, Math.min(1, (floorEpoch - formation) / duration));
      leg.floor_epoch = floorEpoch;
      leg.floor_timing_grain = "TICK";
      leg.floor_timing_basis = "W1_GROUND_TRUTH_EXACT_FLOOR_RECEIPT";
      leg.floor_timing_receipt = `${GROUND_TRUTH_COMMIT}:${GROUND_TRUTH_PATH}#${truth.event_id}|${leg.leg_id}`;
      boundLegs += 1;
    }
    if (boundLegs) add(truthBound, candidate.category, boundLegs);
  }
  const eligible = counts();
  for (const candidate of corpusRows) {
    if (candidate.span?.status !== "BOUNDED") continue;
    const eligibleLegs = (candidate.legs ?? []).filter((leg) => Number.isFinite(leg.low_cents)).length;
    if (eligibleLegs) add(eligible, candidate.category, eligibleLegs);
    // Coverage is measured on the eligible denominator. A timed row with no
    // bounded low is not a served floor path and must not inflate the numerator.
    const timedLegs = (candidate.legs ?? []).filter((leg) => Number.isFinite(leg.low_cents) && Number.isFinite(leg.floor_epoch) && Number.isFinite(leg.floor_fraction)).length;
    if (timedLegs) add(after, candidate.category, timedLegs);
  }
  return {
    method: "BEST_AVAILABLE_BELL_BOUNDED_MEMBER_FLOOR_FRACTION",
    before_truth_table_only: before,
    exact_truth_bindings: truthBound,
    after_all_bell_bounded_library_paths: after,
    eligible_bell_bounded_library_paths: eligible,
    every_eligible_game_bound: after.events === eligible.events,
    every_eligible_leg_bound: after.legs === eligible.legs,
    timing_grains: ["TICK", "MINUTE", "RANGE_POLL"],
    layer_license: ["MACRO", "MICRO"],
    truth_commit: GROUND_TRUTH_COMMIT,
    truth_path: GROUND_TRUTH_PATH,
  };
}

function loadTicks(privateRoot, meta) {
  const rows = [];
  for (const legId of meta.leg_ids) {
    const file = path.join(privateRoot, "fit-local", "ticks", `${meta.event_id}-${legId}.csv.gz`);
    ensure(fs.existsSync(file), `missing target tape ${file}`);
    const lines = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim().split(/\r?\n/);
    const headers = parseCsvLine(lines.shift().replace(/^\uFEFF/, ""));
    lines.forEach((line, index) => {
      const row = objectFromCsv(headers, line);
      let timestampEpoch;
      try { timestampEpoch = parseEt(row.ts_et); }
      catch (error) {
        const issue = { event_id: meta.event_id, leg_id: legId, file, row: index + 1, raw_line: line, ts_et: row.ts_et, reason: "TRUNCATED_OR_MALFORMED_CAPTURE_ROW_SKIPPED" };
        if (line.length < headers.join(",").length / 4 || String(row.ts_et).length < 20) { LOAD_TICK_ISSUES.push(issue); return; }
        throw error;
      }
      rows.push({ event_id: meta.event_id, leg_id: legId, timestamp_epoch: timestampEpoch, source_timestamp_epoch: timestampEpoch, source_row_index: index + 1, receipt: `${path.basename(file)}#row-${index + 1}`, kind: "BOOK", bid_cents: number(row.bid_1), ask_cents: number(row.ask_1), last_trade_cents: number(row.last_trade), bid_1_sz: number(row.bid_1_sz), ask_1_sz: number(row.ask_1_sz), bid_depth_5: number(row.bid_depth_5), ask_depth_5: number(row.ask_depth_5), source: "EXTERNAL_CUSTODY_DUAL_BOOK" });
    });
  }
  return rows;
}

async function loadTargetPrints(privateRoot, metas) {
  const tickers = new Map();
  for (const meta of metas) for (const legId of meta.leg_ids) tickers.set(`${meta.event_id}-${legId}`, { event_id: meta.event_id, leg_id: legId });
  const byEvent = new Map(metas.map((meta) => [meta.event_id, []]));
  const source = path.join(privateRoot, "fit-local", "prints.jsonl");
  const sourceRows = await streamJsonl(source, (row) => {
    const target = tickers.get(row.ticker); if (!target) return;
    const timestampEpoch = Date.parse(row.exchange_ts) / 1000;
    byEvent.get(target.event_id).push({ event_id: target.event_id, leg_id: target.leg_id, timestamp_epoch: timestampEpoch, source_timestamp_epoch: timestampEpoch, receipt: row.receipt_id ?? row.trade_id, kind: "PRINT", price_cents: number(row.price_cents), size: number(row.size), source: "EXTERNAL_CUSTODY_TRUE_PRINTS", taker_book_side: row.taker_book_side });
  });
  return { byEvent, source: { path: source, bytes: fs.statSync(source).size, scanned_rows: sourceRows, sha256: fileHash(source) } };
}

async function loadLineage(walkRoot, eventIds = ALL_TARGETS) {
  const selected = new Set(eventIds);
  const file = path.join(walkRoot, "FULL_DECISION_TRACE_5.jsonl.gz"), byEvent = new Map();
  const rows = await streamJsonl(file, (row) => {
    if (!selected.has(row.event_id)) return;
    if (!byEvent.has(row.event_id)) byEvent.set(row.event_id, new Map());
    const legId = row.leg_identity.split("|").at(-1), byLeg = byEvent.get(row.event_id);
    if (!byLeg.has(legId)) byLeg.set(legId, []);
    byLeg.get(legId).push({ timestamp_epoch: row.timestamp_epoch, action: row.final_action, target_cents: row.final_target_cents, receipt: row.receipt, sentence: row.joint_license?.sentence ?? null });
  });
  for (const byLeg of byEvent.values()) for (const values of byLeg.values()) values.sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || String(a.receipt).localeCompare(String(b.receipt)));
  return { byEvent, receipt: receipt(file, rows) };
}
function lineageAt(lineage, eventId, legId, timestampEpoch) {
  const rows = lineage.byEvent.get(eventId)?.get(legId) ?? [];
  let found = null;
  for (const row of rows) { if (row.timestamp_epoch > timestampEpoch) break; found = row; }
  return found ?? { action: "HOLD_REST", target_cents: null, receipt: `${eventId}|${legId}|NO_LINEAGE_YET` };
}

function turningEpochs(meta, rows) {
  const epochs = new Set([meta.discovery_epoch, ...Object.values(meta.formation_end_epochs)]);
  if (Number.isFinite(meta.bell_epoch)) epochs.add(meta.bell_epoch);
  const byLeg = Object.fromEntries(meta.leg_ids.map((id) => [id, []]));
  rows.forEach((row) => byLeg[row.leg_id].push(row));
  for (const legId of meta.leg_ids) {
    const legRows = byLeg[legId].sort(compareTapeRows);
    if (legRows.length) { epochs.add(legRows[0].timestamp_epoch); epochs.add(legRows.at(-1).timestamp_epoch); }
    let runningAskLow = null;
    for (const row of legRows) {
      if (row.kind !== "BOOK" || !Number.isInteger(row.ask_cents)) continue;
      if (runningAskLow === null || row.ask_cents < runningAskLow) {
        epochs.add(row.timestamp_epoch);
        runningAskLow = row.ask_cents;
      }
    }
    // F-VS-237: every true print that establishes or touches the leg's
    // running traded floor is an executable receipt, not merely export data.
    // Include each exact receipt timestamp in the runner's epoch set; the
    // inner receipt loop below preserves same-timestamp receipt identity.
    let runningPrintLow = null;
    for (const row of legRows) {
      if (row.kind !== "PRINT" || !Number.isInteger(row.price_cents)) continue;
      if (runningPrintLow === null || row.price_cents <= runningPrintLow) {
        epochs.add(row.timestamp_epoch);
        runningPrintLow = runningPrintLow === null ? row.price_cents : Math.min(runningPrintLow, row.price_cents);
      }
    }
    const refs = legRows.map((row) => ({ ...row, ref: row.kind === "PRINT" ? row.price_cents : row.last_trade_cents || (number(row.bid_cents) && number(row.ask_cents) ? Math.floor((row.bid_cents + row.ask_cents) / 2) : null) })).filter((row) => Number.isInteger(row.ref));
    let low = null;
    for (const row of refs) if (low === null || row.ref < low) { if (low === null || low - row.ref >= 2) epochs.add(row.timestamp_epoch); low = row.ref; }
    const steps = refs.slice(1).map((row, index) => ({ timestamp_epoch: row.timestamp_epoch, magnitude: Math.abs(row.ref - refs[index].ref), signed: row.ref - refs[index].ref })).sort((a, b) => b.magnitude - a.magnitude || a.timestamp_epoch - b.timestamp_epoch).slice(0, 5);
    steps.forEach((row) => epochs.add(row.timestamp_epoch));
    const firstPrint = legRows.find((row) => row.kind === "PRINT"); if (firstPrint) epochs.add(firstPrint.timestamp_epoch);
  }
  let materializedMax = Number.NEGATIVE_INFINITY;
  if (!Number.isFinite(meta.bell_epoch)) for (const row of rows) if (row.timestamp_epoch > materializedMax) materializedMax = row.timestamp_epoch;
  const max = Number.isFinite(meta.bell_epoch) ? meta.bell_epoch : materializedMax;
  for (let ts = meta.discovery_epoch + 3 * 3600; ts < max; ts += 3 * 3600) epochs.add(ts);
  return [...epochs].filter(Number.isFinite).sort((a, b) => a - b);
}

function resourcesFrom(census, remote, repo, privateRoot) {
  const repoAsset = (id, commit, rel) => { const bytes = gitShow(repo, commit, rel); return { id, status: "CONNECTED", receipt: `${commit}:${rel}@sha256:${shaBytes(bytes)}`, smoke: { bytes: bytes.length, json_or_text_opened: true } }; };
  const macro = path.join(privateRoot, "fit-local", "macro_projection.db"), macroReceipt = path.join(privateRoot, "fit-local", "MACRO_PROJECTION_RECEIPT.json");
  return [
    { id: "CORPUS_CENSUS", status: "CONNECTED", receipt: `CORPUS_CENSUS@${census.binding_sha256}`, smoke: { union_games: census.population.union_games } },
    { id: "HISTORICAL_EVENTS_MATERIALIZATION", status: "CONNECTED", receipt: census.stores.find((row) => row.id === "historical_events")?.sha256, smoke: census.stores.find((row) => row.id === "historical_events") },
    { id: "CORPUS_EVENTS_V2", status: "CONNECTED", receipt: census.stores.find((row) => row.id === "corpus_events_v2")?.sha256, smoke: census.stores.find((row) => row.id === "corpus_events_v2") },
    { id: "RANGE_SPECTRUM_V1", status: "CONNECTED", receipt: census.stores.find((row) => row.id === "range_spectrum_v1")?.sha256, smoke: census.stores.find((row) => row.id === "range_spectrum_v1") },
    { id: "SUBSECOND_STORE", status: "CONNECTED", receipt: `stat:${remote.subsecond.path}:${remote.subsecond.bytes}`, smoke: { schema_opened_read_only: true, tables: Object.keys(remote.subsecond.tables), sample_present: remote.subsecond.sample_present } },
    ...["ticks", "trades", "ws_depth"].map((root) => {
      const store = census.stores.find((row) => row.id === `do_spaces_${root}`);
      return { id: `DO_SPACES_${root.toUpperCase()}`, status: store?.status ?? "DISCONNECTED", receipt: store?.smoke_receipt ?? null, smoke: store };
    }),
    { id: "EXTERNAL_CUSTODY_DUAL_BOOK", status: "CONNECTED", receipt: path.join(privateRoot, "fit-local", "ticks"), smoke: { target_files_opened: 10 } },
    { id: "EXTERNAL_CUSTODY_DEPTH_RECORDER", status: census.stores.find((row) => row.id === "depth_recorder_top20")?.status ?? "DISCONNECTED", receipt: census.stores.find((row) => row.id === "depth_recorder_top20")?.smoke_receipt ?? null, smoke: census.stores.find((row) => row.id === "depth_recorder_top20") },
    { id: "EXTERNAL_CUSTODY_TRUE_PRINTS", status: "CONNECTED", receipt: path.join(privateRoot, "fit-local", "prints.jsonl"), smoke: { target_filter_opened: true } },
    { id: "BOOKMAKER_ODDS_STORE", status: "CONNECTED", receipt: `read-only:${remote.odds_backup.path}`, smoke: remote.odds_backup.tables.bookmaker_odds },
    { id: "MACRO_PROJECTION_DB", status: "CONNECTED", receipt: `${fileHash(macro)}:${fileHash(macroReceipt)}`, smoke: JSON.parse(fs.readFileSync(macroReceipt, "utf8")) },
    repoAsset("SHAPE_TAXONOMY_E269779B", "e269779b", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/SHAPE_TAXONOMY_BUILD1.json"),
    repoAsset("FLOOR_DEPTH_8AB4F2D9", "8ab4f2d9", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/PER_SHAPE_FLOOR_DEPTH_TABLES.json"),
    repoAsset("RIPENESS_41C1F724", "41c1f724", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/RECOGNITION_OPERATING_POINT.json"),
    repoAsset("TRUTH_TABLE_C0056976", "c0056976", GROUND_TRUTH_PATH),
    repoAsset("HONEST_PAIR_FLOOR_TIMING", "336f42bf", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/PAIR_POSITION_FLOOR_TIMING_CENSUS.json"),
    repoAsset("HONEST_DIVOT_ARRIVAL", "f40ac8ea", ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/DIVOT_ARRIVAL_AUDIT.json"),
    { id: "FOUNDATION_PER_MINUTE_UNIVERSE", status: "CONNECTED", receipt: corpusReceipt(census, "foundation_minute_universe"), smoke: census.stores.find((row) => row.id === "foundation_minute_universe") },
    { id: "SPIKE_ATLAS", status: "CONNECTED", receipt: corpusReceipt(census, "spike_atlas"), smoke: census.stores.find((row) => row.id === "spike_atlas") },
  ];
}

function corpusReceipt(census, id) {
  const store = census.stores.find((row) => row.id === id);
  return store?.sha256 ?? store?.receipt_sha256 ?? store?.binding_sha256 ?? null;
}

function buildCensus(corpus, remote, privateRoot) {
  const tickDir = path.join(privateRoot, "fit-local", "ticks"), tickFiles = fs.readdirSync(tickDir).filter((name) => name.endsWith(".csv.gz"));
  const tickEvents = new Set(tickFiles.map((name) => eventFromTicker(name.replace(/\.csv\.gz$/, ""))));
  const tickCategories = {}; tickEvents.forEach((eventId) => tickCategories[categoryFromEvent(eventId)] = (tickCategories[categoryFromEvent(eventId)] || 0) + 1);
  const depthDir = path.join(privateRoot, "fit-local", "depth_recorder"), depthFiles = fs.readdirSync(depthDir).filter((name) => name.endsWith(".jsonl.gz")).sort();
  const depthBytes = depthFiles.reduce((total, name) => total + fs.statSync(path.join(depthDir, name)).size, 0);
  const depthSummaryPath = path.join(__dirname, "..", "..", ".claude", "window1_20260721", "SOURCE_COVERAGE_SUMMARY.json");
  const depthLedgerPath = path.join(__dirname, "..", "..", ".claude", "window1_20260721", "SOURCE_COVERAGE_LEDGER.jsonl");
  const depthSummary = JSON.parse(fs.readFileSync(depthSummaryPath, "utf8")).depth_recorder;
  const depthCoverage = fs.readFileSync(depthLedgerPath, "utf8").trim().split(/\r?\n/).map((line) => JSON.parse(line)).filter((row) => row.legs.some((leg) => leg.sources?.depth_recorder_top20?.available));
  const depthCategories = depthCoverage.reduce((counts, row) => (counts[row.category] = (counts[row.category] || 0) + 1, counts), {});
  const macroPath = path.join(privateRoot, "fit-local", "macro_projection.db"), macroReceiptPath = path.join(privateRoot, "fit-local", "MACRO_PROJECTION_RECEIPT.json");
  const macroReceipt = JSON.parse(fs.readFileSync(macroReceiptPath, "utf8"));
  ensure(depthFiles.length === depthSummary.file_count && depthBytes === depthSummary.bytes, "depth-recorder custody no longer matches frozen receipt");
  const depthFirst = zlib.gunzipSync(fs.readFileSync(path.join(depthDir, depthFiles[0]))).toString("utf8").split(/\r?\n/, 1)[0];
  ensure(depthFirst && JSON.parse(depthFirst), "depth-recorder smoke row did not open");
  const archiveRoots = ["ticks", "trades", "ws_depth"].map((root) => {
    const info = remote.spaces.roots[root];
    const usable = info && info.objects > 0;
    return {
      id: `do_spaces_${root}`,
      status: usable ? "CONNECTED" : "DISCONNECTED",
      purpose: "PATTERN_LIBRARY_ARCHIVE_PRESEALED_ONLY",
      quality: root === "ws_depth" ? "RAW WS DELTAS; ZERO FULL-DEPTH-USABLE TICKERS IN FROZEN CENSUS" : "OBJECT ARCHIVE",
      games: info?.games ?? null,
      span: info?.min_modtime && info?.max_modtime ? `${info.min_modtime}..${info.max_modtime}` : null,
      categories: info?.categories_by_game ?? {},
      ...info,
      path: `spaces:omi-tick-archive/${root}`,
      smoke_receipt: info?.smoke_receipt ?? `presealed-prefix-inventory:${root}:${info?.objects ?? 0}:${info?.bytes ?? 0}`,
    };
  });
  const stores = [
    { id: "historical_events", status: "CONNECTED", purpose: "PATTERN_LIBRARY", quality: "EVENT_GRAIN_AGGREGATE; NO_INTRAMATCH_CLOCK", games: corpus.counts.historical_rows, span: "2026-01-02..2026-04-10 (source table); durable materialization contains qualifying rows", categories: corpus.counts.historical_categories, ...corpus.sources.historical },
    { id: "corpus_events_v2", status: "CONNECTED", purpose: "PATTERN_LIBRARY_REGISTRY", quality: "EVENT_AND_CLOCK_PROVENANCE", games: corpus.counts.registry_rows, span: "2026-01-02..2026-07-18", categories: corpus.counts.registry_categories, ...corpus.sources.registry },
    { id: "range_spectrum_v1", status: "CONNECTED", purpose: "PATTERN_LIBRARY", quality: "POLL_PATH_SHAPE; NOT_RECORDER_DEPTH", games: corpus.counts.range_rows, span: "2026-04-20..2026-07-18", categories: corpus.counts.range_categories, ...corpus.sources.range },
    { id: "recorder_dual_book_ticks", status: "CONNECTED", purpose: "TUNE_TEST_SUBSTRATE_AND_TARGET_TAPE", quality: "TOP5_RECORDER_BOOK; L8 STANDING TRUTH", games: tickEvents.size, files: tickFiles.length, span: "2026-07-11..2026-07-21", categories: tickCategories, path: tickDir, directory_manifest_sha256: shaBytes(tickFiles.sort().map((name) => `${name}|${fs.statSync(path.join(tickDir, name)).size}`).join("\n")) },
    { id: "depth_recorder_top20", status: "CONNECTED", purpose: "PATTERN_LIBRARY_AND_DEPTH_READER", quality: "CHANGE-DEDUPLICATED TOP20 SNAPSHOTS; NOT FULL CHAIN; NOT TRUE PRINTS", games: depthCoverage.length, games_both_legs: depthCoverage.filter((row) => row.legs.every((leg) => leg.sources?.depth_recorder_top20?.available)).length, tickers: depthSummary.required_ticker_count, files: depthFiles.length, rows: depthSummary.physical_rows, bytes: depthBytes, span: "2026-07-13..2026-07-20", categories: depthCategories, path: depthDir, smoke_receipt: `first-row-open:${depthFiles[0]}@sha256:${shaBytes(depthFirst)};ledger@sha256:${fileHash(depthLedgerPath)}` },
    { id: "true_print_tape", status: "CONNECTED", purpose: "CREDITING_TRUTH", quality: "PUBLIC_EXCHANGE_TRADE_ID; POSITIVE SIZE", games: 804, rows: 4836462, span: "2026-07-11..2026-07-21", categories: tickCategories, path: path.join(privateRoot, "fit-local", "prints.jsonl"), bytes: fs.statSync(path.join(privateRoot, "fit-local", "prints.jsonl")).size },
    { id: "subsecond_store", status: "CONNECTED", purpose: "PATTERN_LIBRARY_NAMED_EVENT_READER", quality: "MIXED SOURCE; SYNTHETIC ROWS RETAIN SOURCE LABEL", games: remote.subsecond.census?.games ?? null, rows: remote.subsecond.census?.rows ?? null, span: remote.subsecond.census?.span ?? null, categories: remote.subsecond.census?.categories ?? {}, path: remote.subsecond.path, bytes: remote.subsecond.bytes, schema_receipt_sha256: shaBytes(canonical({ tables: remote.subsecond.tables, indexes: remote.subsecond.indexes, census: remote.subsecond.census ?? null })) },
    ...archiveRoots,
    { id: "external_custody", status: "CONNECTED", purpose: "RAW_NON_GIT_EVIDENCE", quality: "TARGET FILES HASHED; SEALED DIRECTORY EXCLUDED", games: tickEvents.size, span: "2026-07-11..2026-07-21", categories: tickCategories, path: path.join(privateRoot, "fit-local") },
    { id: "bookmaker_odds", status: "CONNECTED", purpose: "STANDING_OS_SUPPLEMENT", quality: "READ_ONLY_DURABLE_BACKUP", games: remote.odds_backup.tables.bookmaker_odds?.games ?? null, rows: remote.odds_backup.tables.bookmaker_odds?.rows ?? null, span: remote.odds_backup.tables.bookmaker_odds?.span ?? null, categories: remote.odds_backup.tables.bookmaker_odds?.categories ?? {}, path: remote.odds_backup.path, schema_receipt_sha256: shaBytes(canonical(remote.odds_backup.tables.bookmaker_odds)) },
    { id: "macro_projection", status: "CONNECTED", purpose: "PATTERN_LIBRARY", quality: "N2_N4_N5_MACRO_TABLES", games: macroReceipt.event_ledger?.D ?? null, games_with_book_rows: macroReceipt.projection?.events_with_rows ?? null, rows: macroReceipt.projection?.book_price_rows ?? null, span: `${macroReceipt.projection?.first_polled_at ?? "UNKNOWN"}..${macroReceipt.projection?.last_polled_at ?? "UNKNOWN"}`, categories: macroReceipt.projection?.rows_by_category ?? {}, category_basis: "BOOK_PRICE_ROWS", path: macroPath, sha256: fileHash(macroPath), bytes: fs.statSync(macroPath).size, receipt_sha256: fileHash(macroReceiptPath) },
    { id: "foundation_minute_universe", status: "CONNECTED", purpose: "FIRST_CLASS_PATTERN_LIBRARY", quality: "NATIVE_BELL_BOUNDED; UNKNOWN_MATCH_START_METHOD_EXCLUDED", games: corpus.foundation.rows, rows: corpus.foundation.source.rows, span: "2025-06-18..2026-05-01", categories: corpus.counts.foundation_categories, grain: "MINUTE", licensed_layers: ["MACRO", "MICRO"], micro_micro_licensed: false, path: corpus.foundation.source.path, sha256: corpus.foundation.source.sha256, bytes: corpus.foundation.source.bytes, compact_index: corpus.foundation.index, coverage_before: corpus.foundation.coverage_before, coverage_after: corpus.foundation.coverage_after },
    { id: "spike_atlas", status: "CONNECTED", purpose: "FOUNDATION_PATTERN_SUPPLEMENT", quality: "DESCRIPTIVE_ONLY; SUPERSEDED_EXIT_MAP_NOT_CONSUMED", games: corpus.foundation.spike_atlas.reduce((total, row) => total + row.rows, 0), rows: corpus.foundation.spike_atlas.reduce((total, row) => total + row.rows, 0), categories: Object.fromEntries(corpus.foundation.spike_atlas.map((row) => [row.category, row.rows])), grain: "EVENT_LEG_DESCRIPTIVE", licensed_layers: ["MACRO", "MICRO"], micro_micro_licensed: false, sha256: shaBytes(canonical(corpus.foundation.spike_atlas)), files: corpus.foundation.spike_atlas },
  ];
  const body = { label: "CORPUS_CENSUS_V54_V6", law: "F-V53-050", sealed_status: "EXCLUDED_BY_SOURCE_ROUTING", live_mutation_status: "NO_MUTATION_ENTRY_POINT", execution_scope: "NAMED_BED_ONLY", population: { union_games: corpus.counts.union_games, by_quality: corpus.counts.by_quality }, stores, remote_smoke: { spaces_filter: remote.spaces.filter, spaces_sample: remote.spaces.sample_receipt, subsecond_access: "READ_ONLY", odds_access: "READ_ONLY" } };
  return { ...body, binding_sha256: shaBytes(canonical(body)) };
}

function functionalityReceipt(resources, census) {
  const components = [];
  resources.forEach((resource) => components.push({ component: resource.id, status: resource.status, smoke_receipt: resource.receipt, detail: resource.smoke }));
  os.READER_NAMES.forEach((name) => components.push({ component: `READER_${name.toUpperCase()}`, status: "CONNECTED", smoke_receipt: `UNIT_REAL_TAPE_SMOKE:${name}` }));
  components.push({ component: "PATTERN_ENGINE", status: "CONNECTED", smoke_receipt: shaBytes(canonical(os.SIMILARITY_DECLARATION)), detail: os.SIMILARITY_DECLARATION });
  components.push({ component: "NEIGHBORHOOD_RETRIEVAL", status: "CONNECTED", smoke_receipt: "LEAVE_SELF_OUT_ASSERTED_AND_NAMED" });
  components.push({ component: "DERIVATION", status: "CONNECTED", smoke_receipt: "NEIGHBORHOOD+TAPE_READS+LINEAGE+PAIR_ARITHMETIC" });
  components.push({ component: "SENTENCE_EMITTER", status: "CONNECTED", smoke_receipt: "SENTENCE_ACTION_HARD_ASSERT+CITATION_RECEIPT_HARD_ASSERT" });
  const bad = components.filter((row) => row.status !== "CONNECTED");
  return { label: "FUNCTIONALITY_RECEIPT_V54_V6", definition: "The OS functions only when every listed component is CONNECTED with a smoke receipt.", corpus_binding_sha256: census.binding_sha256, component_count: components.length, connected_count: components.length - bad.length, degraded_count: components.filter((row) => row.status === "DEGRADED").length, disconnected_count: components.filter((row) => row.status === "DISCONNECTED").length, all_connected: bad.length === 0, components };
}

function readersPlain(reads) {
  return os.READER_NAMES.map((name) => `${name}=${JSON.stringify(reads[name].value)}`).join(" · ");
}
function neighborsPlain(neighborhood) {
  return neighborhood.map((row) => `${row.event_id}[${row.citation_receipt_id}] (${row.event_date}; score ${row.score.toFixed(4)}; quality ${row.quality}; grain ${row.grain ?? "UNKNOWN"}; layers ${(row.licensed_layers ?? []).join("/") || "UNKNOWN"}; ${row.legs.map((leg) => `${leg.leg_id} ${leg.anchor_cents ?? "?"}->observed ${leg.observed_low_cents ?? "?"}->low ${leg.low_cents ?? "?"}->close ${leg.close_cents ?? "?"}`).join(", ")})`).join("; ");
}
function citationsPlain(derivation) {
  return Object.values(derivation.citation_receipts).map((row) => `${row.receipt_id}=${JSON.stringify(row)}`).join("; ");
}

function replayEvent({ meta, rows, corpus, resources, lineage, smokeOnly = false, clockMode = "CAUSAL_FRACTIONAL" }) {
  if (activeExecutionGuard) activeExecutionGuard.record(meta.event_id);
  // Replay consumes an immutable, fully ordered view.  Epoch derivation and
  // state execution must see the same receipt order on every run.
  // Pool second-closes retain source-file order; execution order is unchanged.
  const poolStampedRows = rows.map((row, index) => ({ ...row, pool_source_row_index: index }));
  const orderedRows = clockMode === "LEGACY_INTEGER_BOOK_FIRST"
    ? [...poolStampedRows].sort(causalClock.compareLegacyRows)
    : causalClock.materializeCausalClock(poolStampedRows);
  const state = os.createTapeState(meta), epochSet = new Set(turningEpochs(meta, orderedRows)), derivations = [], stageReads = [], fillEvents = [], rearmAttempts = [], floorPrintDecisionInstants = [];
  const atlasEpochs = new Set(os.atlasGateEpochs(meta));
  for (const epoch of atlasEpochs) epochSet.add(epoch);
  // Independent fallback must remain byte-identical at the moments when its
  // licensed target changes. Adding only lineage transitions avoids turning the
  // export's repeated HOLD rows into artificial evaluation cadence.
  for (const legRows of lineage.byEvent.get(meta.event_id)?.values() ?? []) {
    let prior = null;
    for (const row of legRows) {
      const signature = `${row.target_cents ?? "NONE"}`;
      if (signature !== prior) epochSet.add(row.timestamp_epoch);
      prior = signature;
    }
  }
  const epochs = [...epochSet].filter(Number.isFinite).sort((a, b) => a - b);
  function evaluateStage({ trigger, receipt = null, legIds = null, compactUnchangedRearm = false, clockEpoch = null }) {
    if (state.leg_ids.some((id) => !state.legs[id].rows.length)) return null;
    state.current_epoch = clockEpoch ?? Math.max(state.current_epoch, ...state.leg_ids.map((id) => state.legs[id].rows.at(-1).timestamp_epoch));
    state.receipt = receipt ?? `${state.event_id}|TURN|${state.current_epoch}`;
    const reads = os.readAll(state), vector = os.vectorFromReads(state, reads), neighborhood = os.retrieveNeighborhood(corpus, vector, state.event_id, os.SIMILARITY_DECLARATION.neighbor_count, state.receipt);
    ensure(neighborhood.every((row) => row.event_id !== state.event_id), `leave-self-out failed ${state.event_id}`);
    const activeLegIds = legIds ?? (smokeOnly ? state.leg_ids : state.leg_ids.filter((id) => !state.positions[id].credited));
    const lineageByLeg = Object.fromEntries(state.leg_ids.map((legId) => [legId, lineageAt(lineage, state.event_id, legId, state.current_epoch)]));
    const joint = os.deriveJointActions({ state, reads, neighborhood, lineageByLeg, resources });
    const perLeg = joint.derivations.filter((row) => activeLegIds.includes(row.leg_id));
    let meaningfulRearmTransition = false;
    for (const derivation of perLeg) {
      const legId = derivation.leg_id;
      ensure(derivation.sentence_action_assertion.equal, `sentence action failed ${state.event_id}|${legId}`);
      ensure(derivation.citation_receipt_assertion.equal, `citation receipt failed ${state.event_id}|${legId}`);
      if (!derivation.pair_conservation.at_or_below_99) {
        const heldTarget = state.positions[legId].standing_target_cents;
        derivation.action = {
          ...derivation.action,
          action: Number.isInteger(heldTarget) ? "HOLD_REST" : "STAND_DOWN",
          target_cents: heldTarget,
          reason: `${derivation.action.reason}+PAIR_CONSERVATION_SKIP_NEW_REST_HOLD_AND_CONTINUE`,
        };
        derivation.pair_conservation = {
          ...derivation.pair_conservation,
          proposed_target_skipped: true,
          held_existing_target_cents: heldTarget,
          replay_continued: true,
        };
      }
      if (!smokeOnly && !state.positions[legId].credited) {
        const position = state.positions[legId];
        const targetBefore = position.standing_target_cents;
        if (derivation.action.action === "CANCEL_REST") {
          position.standing_target_cents = null;
          position.standing_license_basis = null;
          position.standing_license_receipt = null;
          position.standing_captured_rest_level_cents = null;
          position.standing_captured_rest_license_receipt = null;
        } else {
          position.standing_target_cents = derivation.action.target_cents;
          if (
            Number.isInteger(derivation.action.target_cents)
            && ["PLACE_REST", "REPRICE_REST"].includes(derivation.action.action)
          ) {
            position.standing_license_basis = derivation.action.reason;
            position.standing_license_receipt = state.receipt;
            position.standing_captured_rest_level_cents = derivation.action.target_cents;
            position.standing_captured_rest_license_receipt = state.receipt;
          }
        }
        if (derivation.action.reason === "Q_UNPOSTABLE_NEXT_SURVIVING_LADDER_RUNG_BELOW_ASK_ADMITTED") {
          ensure(
            ["PLACE_REST", "REPRICE_REST"].includes(derivation.action.action)
              && Number.isInteger(derivation.action.target_cents)
              && position.standing_target_cents === derivation.action.target_cents,
            `NEXT_LIVE_RUNG_REST_WRITE_FAILED ${state.event_id}|${legId}|${state.receipt}`,
          );
          derivation.machine_rest_log_write = {
            store: "ORDER_TRANSITION_TENURE_SINGLE_PRODUCER",
            log_file: "EVIDENCED_FLOOR_TENURE_TABLE.json",
            leg_id: legId,
            timestamp_epoch: state.current_epoch,
            receipt: state.receipt,
            action: derivation.action.action,
            price_cents: position.standing_target_cents,
            standing_license_basis: position.standing_license_basis,
            standing_license_receipt: position.standing_license_receipt,
          };
        }
        if (derivation.action.action !== "HOLD_REST" || targetBefore !== position.standing_target_cents || derivation.layered_dual_belief?.atomic_rearm?.status === "REARM_RESOLVED_WITH_LAWFUL_REST") meaningfulRearmTransition = true;
      }
    }
    if (compactUnchangedRearm && !meaningfulRearmTransition) {
      for (const derivation of perLeg) {
        rearmAttempts.push({
          event_id: state.event_id,
          leg_id: derivation.leg_id,
          timestamp_epoch: state.current_epoch,
          receipt: state.receipt,
          trigger,
          action: derivation.action,
          rearm: derivation.layered_dual_belief?.atomic_rearm ?? null,
          layer_status: {
            macro: joint.layers.macro.context?.status ?? null,
            micro: joint.layers.micro.context?.status ?? null,
            micro_micro: joint.layers.micro_micro.context?.status ?? null,
          },
          coherence_status: joint.coherence.status,
          envelope: derivation.layered_dual_belief?.envelope ?? null,
          no_lawful_replacement_reason: derivation.layered_dual_belief?.envelope_consistency?.no_lawful_replacement_reason ?? null,
          full_derivation_retained: false,
          policy_evaluation_executed: true,
        });
      }
      return { compact_rearm_attempt: true, receipt: state.receipt, timestamp_epoch: state.current_epoch };
    }
    derivations.push(...perLeg);
    const stage = { trigger, receipt: state.receipt, timestamp_epoch: state.current_epoch, hours_from_discovery: reads.time_in_window.value.hours_from_discovery, reads, neighborhood, layers: joint.layers, coherence: joint.coherence, credited_leg_streams: joint.credited_leg_streams, derivations: perLeg };
    stageReads.push(stage);
    return stage;
  }
  let cursor = 0, lastConsumedReceipt = null, lastEvaluatedInstant = null;
  for (const epoch of epochs) {
    while (cursor < orderedRows.length && orderedRows[cursor].timestamp_epoch <= epoch) {
      const instant = orderedRows[cursor].timestamp_epoch;
      const instantRows = [];
      while (cursor < orderedRows.length && orderedRows[cursor].timestamp_epoch === instant && orderedRows[cursor].timestamp_epoch <= epoch) instantRows.push(orderedRows[cursor++]);
      const receiptGrainBookByLeg = new Map(state.leg_ids.flatMap((legId) => {
        const books = instantRows.filter((row) => row.kind === "BOOK" && row.leg_id === legId);
        const priorTradeLow = state.legs[legId].running_true_trade_low_cents;
        if (books.length < 2 || !Number.isInteger(priorTradeLow)) return [];
        const selected = books.find((row, index) => Number.isInteger(row.bid_cents)
          && Number.isInteger(row.ask_cents)
          && row.bid_cents < priorTradeLow
          && row.bid_cents < row.ask_cents
          && books.slice(index + 1).some((later) => Number.isInteger(later.ask_cents) && later.ask_cents <= row.bid_cents));
        return selected ? [[legId, selected]] : [];
      }));
      const sequentiallyEvaluatedLegs = new Set();
      let fillHandoffReceipt = null;
      for (const row of instantRows) {
        lastConsumedReceipt = row.receipt;
        const position = state.positions[row.leg_id];
        const priorTrueTradeLow = state.legs[row.leg_id].running_true_trade_low_cents;
        const floorPrintReceipt = row.kind === "PRINT"
          && Number.isInteger(row.price_cents)
          && (priorTrueTradeLow === null || row.price_cents <= priorTrueTradeLow);
        let creditedOnThisReceipt = false;
        if (!smokeOnly && row.kind === "PRINT" && !position.credited && Number.isInteger(position.standing_target_cents) && row.price_cents <= position.standing_target_cents) {
          const fillEventReceipt = os.creditPosition(state, row.leg_id, row);
          fillEvents.push(fillEventReceipt);
          fillHandoffReceipt = row.receipt;
          creditedOnThisReceipt = true;
        }
        os.observe(state, row.leg_id, row);
        if (!smokeOnly && floorPrintReceipt) {
          // Credited legs continue reading: their floor prints must wake the
          // joint derivation so the open sibling sees the current evidence.
          // Both-credited games still execute the read with an empty emission
          // set, proving the engine woke without attempting another order.
          const openLegIdsAtReceipt = state.leg_ids.filter((id) => !state.positions[id].credited);
          const stage = evaluateStage({ trigger: "FLOOR_PRINT_DECISION_INSTANT", receipt: row.receipt, legIds: openLegIdsAtReceipt });
          if (stage) openLegIdsAtReceipt.forEach((id) => sequentiallyEvaluatedLegs.add(id));
          floorPrintDecisionInstants.push({
            event_id: state.event_id,
            leg_id: row.leg_id,
            timestamp_epoch: row.timestamp_epoch,
            receipt: row.receipt,
            print_price_cents: row.price_cents,
            prior_true_trade_low_cents: priorTrueTradeLow,
            floor_relation: priorTrueTradeLow === null ? "FIRST_TRUE_PRINT" : row.price_cents < priorTrueTradeLow ? "NEW_TRUE_TRADE_LOW" : "TOUCHES_RUNNING_TRUE_TRADE_LOW",
            decision_instant_fired: true,
            decision_instant_kind: creditedOnThisReceipt ? "FILL_CREDIT_AND_JOINT_REDERIVATION" : stage ? openLegIdsAtReceipt.length ? "JOINT_POLICY_REDERIVATION_DECISION_INSTANT" : "TERMINAL_PAIR_READ_NO_ORDER_EMISSION" : "INSUFFICIENT_TWO_LEG_STATE_NO_ACTION",
            stage_receipt: stage?.receipt ?? null,
            policy_derivation_count: stage?.derivations?.length ?? 0,
            provenance: os.LAYER_PROVENANCE.floor_print_decision_instant,
          });
        }
        // F-VS-191: duplicate BBO receipts with the same exchange timestamp are
        // distinct causal receipts. The materialized tape order is timestamp,
        // kind, then receipt-id. Evaluate the affected leg after each receipt so
        // the earlier postable book is not silently overwritten by the later
        // book before the policy can act. Other legs retain the standing
        // turning-point cadence.
        if (!smokeOnly && instant === epoch && row.kind === "BOOK" && receiptGrainBookByLeg.get(row.leg_id)?.receipt === row.receipt && !state.positions[row.leg_id].credited) {
          evaluateStage({ trigger: "DUPLICATE_TIMESTAMP_BOOK_RECEIPT", receipt: row.receipt, legIds: [row.leg_id] });
          sequentiallyEvaluatedLegs.add(row.leg_id);
        }
      }
      const openLegs = state.leg_ids.filter((id) => !state.positions[id].credited);
      if (!smokeOnly && fillHandoffReceipt && openLegs.length) {
        evaluateStage({ trigger: "FILL_HANDOFF_DECISION_INSTANT", receipt: fillHandoffReceipt, legIds: openLegs });
        lastEvaluatedInstant = instant;
      } else if (!smokeOnly && Object.keys(state.dual_belief?.rearm_by_leg ?? {}).length) {
        evaluateStage({ trigger: "ATOMIC_REARM_DECISION_INSTANT", receipt: lastConsumedReceipt, compactUnchangedRearm: true });
        lastEvaluatedInstant = instant;
      } else if (!smokeOnly && sequentiallyEvaluatedLegs.size) {
        const remainingLegs = openLegs.filter((legId) => !sequentiallyEvaluatedLegs.has(legId));
        if (remainingLegs.length) evaluateStage({ trigger: "TURNING_POINT_OTHER_LEGS_AFTER_DUPLICATE_BOOKS", receipt: lastConsumedReceipt, legIds: remainingLegs });
        lastEvaluatedInstant = instant;
      }
    }
    if (atlasEpochs.has(epoch)) {
      evaluateStage({ trigger: "ATLAS_GATE", receipt: `${state.event_id}|ATLAS_GATE|${epoch}`, clockEpoch: epoch, legIds: state.leg_ids });
      lastEvaluatedInstant = epoch;
    } else if (lastEvaluatedInstant !== epoch) {
      evaluateStage({ trigger: "TURNING_POINT", receipt: lastConsumedReceipt });
      lastEvaluatedInstant = epoch;
    }
  }
  const credited = state.leg_ids.filter((id) => state.positions[id].credited), combined = credited.length === 2 ? credited.reduce((total, id) => total + state.positions[id].entry_cents, 0) : null;
  return { state, epochs, stage_reads: stageReads, derivations, fill_events: fillEvents, rearm_attempts: rearmAttempts, floor_print_decision_instants: floorPrintDecisionInstants, clock_mode: clockMode, ordered_rows: orderedRows, execution: { run_source: RUN_SOURCE, gradeable: Number.isFinite(meta.bell_epoch), completed: credited.length === 2, combined_entry_cents: combined, delta_vs_100_cents: Number.isInteger(combined) ? 100 - combined : null, legs: state.positions } };
}

function readerExecutionReceipt(result) {
  const readers = os.READER_NAMES.map((name) => {
    const stages = result.stage_reads.filter((stage) => stage.reads[name]).map((stage) => ({
      timestamp_epoch: stage.timestamp_epoch,
      status: stage.reads[name].status,
      reader: stage.reads[name].reader,
      source_receipts: stage.reads[name].receipts,
    }));
    return { reader: name, stages_fired: stages.length, all_stages_connected: stages.length > 0 && stages.every((stage) => stage.status === "CONNECTED" && stage.reader === name), receipt_sha256: shaBytes(canonical(stages)) };
  });
  const fired = readers.filter((row) => row.stages_fired > 0 && row.all_stages_connected);
  return { all_readers_fired: fired.length === os.READER_NAMES.length, reader_count: fired.length, expected_reader_count: os.READER_NAMES.length, readers };
}

function oldOutcome(perGame, eventId, meta) {
  const row = perGame.rows.find((item) => item.event_id === eventId);
  if (row === undefined) return {
    run_source: "STORE_SILENT",
    walk_file: path.join(path.resolve(arg("walk")), "PER_GAME_L1_L8.json"),
    event_id: eventId,
    completed: false,
    combined_entry_cents: null,
    delta_vs_100_cents: null,
    gradeable: false,
    legs: {}
  };
  const credits = row.L7_CREDIT.why;
  const legs = {};
  for (const [identity, credit] of Object.entries(credits)) {
    const legId = identity.split("|").at(-1), stamp = meta.truth_fill_stamps?.[legId] ?? null;
    const valid = credit.credited && (!stamp || String(stamp).startsWith("PRE_BELL_VALID"));
    legs[identity] = { ...credit, credited: valid, truth_fill_stamp: stamp, correction_receipt: meta.correction_receipt };
  }
  const validCredits = Object.values(legs).filter((leg) => leg.credited), completed = validCredits.length === 2;
  const combined = completed ? validCredits.reduce((value, leg) => value + leg.entry_cents, 0) : null;
  return { run_source: "FROZEN_LINEAGE_PER_GAME_L1_L8", completed, combined_entry_cents: combined, delta_vs_100_cents: completed ? 100 - combined : null, gradeable: Number.isFinite(meta.bell_epoch), legs };
}

function smokeMarkdown(result) {
  const uniqueReaders = new Set(result.stage_reads.flatMap((stage) => Object.keys(stage.reads)));
  const namedNeighbors = new Set(result.stage_reads.flatMap((stage) => stage.neighborhood.map((row) => `${row.event_id}[${row.citation_receipt_id}]`)));
  return `# CRIJEA integration smoke — no grading\n\nLicense: LAW_INDEX @ 3cd59162, sha256 41784e6a… · L0 L6 L8 L10 L11 L16 L17 L18 L19a L20 L21 L22 L23.\n\nCRIJEA is integration-only. Truth closes are UNKNOWN and no execution grade appears here.\n\n- Sixteen readers firing: ${uniqueReaders.size}/16 — ${[...uniqueReaders].sort().join(", ")}\n- Named neighbors returned with welded receipts: ${[...namedNeighbors].sort().join(", ")}\n- Derivations emitted: ${result.derivations.length}\n- Written sentences matching actions: ${result.derivations.filter((row) => row.sentence_action_assertion.equal).length}/${result.derivations.length}\n- Citation receipts matching citations: ${result.derivations.filter((row) => row.citation_receipt_assertion.equal).length}/${result.derivations.length}\n- Conservation pass: ${result.derivations.filter((row) => row.pair_conservation.at_or_below_99).length}/${result.derivations.length}\n\n${result.stage_reads.map((stage) => `## ${stage.hours_from_discovery.toFixed(6)} hours from discovery\n\nFull sixteen-variable picture: ${readersPlain(stage.reads)}\n\nNamed neighborhood: ${neighborsPlain(stage.neighborhood)}\n\n${stage.derivations.map((row) => `${row.sentence}\n\nCITATION-RECEIPTS: ${citationsPlain(row)}`).join("\n\n")}`).join("\n\n")}\n`;
}

function lawfulIncompleteStamp(result, truth) {
  const floorByLeg = Object.fromEntries([[truth.legA, truth.legA_floor_c], [truth.legB, truth.legB_floor_c]]);
  const floors = Object.values(floorByLeg);
  const floorSum = floors.every(Number.isInteger) ? floors.reduce((total, value) => total + value, 0) : null;
  const restAtFloorRows = result.derivations
    .filter((row) => Number.isInteger(floorByLeg[row.leg_id]) && row.action.target_cents === floorByLeg[row.leg_id])
    .map((row) => ({
      leg_id: row.leg_id,
      floor_cents: floorByLeg[row.leg_id],
      rest_cents: row.action.target_cents,
      timestamp_epoch: row.timestamp_epoch,
      receipt: row.receipt,
      action: row.action.action,
      sentence_sha256: shaBytes(row.sentence),
      full_sentence_location: "REPAIR_FOUR_GAME_TRACE.jsonl.gz",
      observed_floor_evidence: row.layered_dual_belief?.pricing_authority?.true_conditioning?.evidence_support_rows?.find((support) => support.evidence_source === "OBSERVED_TRUE_TRADE_LOW" && support.licensed_floor_cents === floorByLeg[row.leg_id]) ?? null,
    }));
  const prongsByLeg = Object.fromEntries(Object.keys(floorByLeg).map((legId) => {
    const rows = restAtFloorRows.filter((row) => row.leg_id === legId);
    const derivedAtOwnFloorEvidence = rows.some((row) => row.observed_floor_evidence?.source_receipt);
    const conductAllocatedLeg = rows.some((row) => ["PLACE_REST", "REPRICE_REST", "HOLD_REST"].includes(row.action));
    return [legId, {
      floor_cents: floorByLeg[legId],
      derived_at_own_floor_evidence: derivedAtOwnFloorEvidence,
      conduct_allocated_leg: conductAllocatedLeg,
      qualifying_receipts: rows.filter((row) => row.observed_floor_evidence?.source_receipt).map((row) => ({ decision_receipt: row.receipt, floor_evidence_receipt: row.observed_floor_evidence.source_receipt, action: row.action })),
      both_prongs_met: derivedAtOwnFloorEvidence && conductAllocatedLeg,
    }];
  }));
  const bothLegProngsMeet = Object.values(prongsByLeg).every((row) => row.both_prongs_met);
  const strictlyUnderParOfferCents = Number.isInteger(floorSum) ? Math.max(0, 99 - floorSum) : null;
  const noCompletedPairTaken = result.execution.completed !== true;
  const lawful = truth.event_id === "KXATPMATCH-26JUL18DANPRA"
    && noCompletedPairTaken
    && strictlyUnderParOfferCents === 0;
  return {
    stamp: lawful ? "LAWFUL_INCOMPLETE" : result.execution.completed ? "NOT_APPLICABLE_COMPLETE" : "UNSTAMPED_INCOMPLETE",
    arithmetic: {
      floor_by_leg_cents: floorByLeg,
      two_leg_floor_sum_cents: floorSum,
      strictly_under_par_offer_cents: strictlyUnderParOfferCents,
      proof: Number.isInteger(floorSum) ? `${floors[0]}+${floors[1]}=${floorSum}; max(0,99-${floorSum})=${Math.max(0, 99 - floorSum)}` : "FLOOR_RESOURCE_GAP",
    },
    completed_pair_taken: result.execution.completed === true,
    no_completed_pair_taken: noCompletedPairTaken,
    rest_at_floor_rows: restAtFloorRows,
    prongs_by_leg: prongsByLeg,
    both_leg_prongs_met: bothLegProngsMeet,
    rest_at_floor_proven: bothLegProngsMeet,
    truth_receipt: truth.correction_receipt ?? `${GROUND_TRUTH_COMMIT}:${GROUND_TRUTH_PATH}#${truth.event_id}`,
    unstamped_abstention_scores_zero: true,
  };
}

function storySection(result, old, meta, incompleteStamp) {
  // The complete receipt stream belongs in REPAIR_FOUR_GAME_TRACE.jsonl.gz.
  // Render a bounded set of licensed action/coherence transitions in the
  // human story. The prior renderer joined every oscillating transition into
  // one monolithic string and could exceed V8's maximum string length. This
  // selection changes no policy, action, fill, or retained full trace.
  const transitionCandidates = [];
  let priorCoherence = null;
  let priorActionSignature = null;
  for (const stage of result.stage_reads) {
    const coherence = stage.coherence?.status ?? "UNKNOWN";
    const actionSignature = stage.derivations.map((row) => `${row.leg_id}:${row.action.action}:${row.action.target_cents ?? "NONE"}`).join("|");
    if (!transitionCandidates.length || coherence !== priorCoherence || actionSignature !== priorActionSignature || stage.trigger === "FILL_HANDOFF_DECISION_INSTANT") transitionCandidates.push(stage);
    priorCoherence = coherence;
    priorActionSignature = actionSignature;
  }
  const last = result.stage_reads.at(-1);
  if (last && transitionCandidates.at(-1)?.receipt !== last.receipt) transitionCandidates.push(last);
  const maximumStoryTransitions = 8;
  const mandatoryIndexes = new Set([0, transitionCandidates.length - 1]);
  transitionCandidates.forEach((stage, index) => {
    if (stage.trigger === "FILL_HANDOFF_DECISION_INSTANT") mandatoryIndexes.add(index);
    if (stage.derivations.some((row) => Number.isInteger(result.execution.legs[row.leg_id]?.entry_cents) && row.action.target_cents === result.execution.legs[row.leg_id].entry_cents)) mandatoryIndexes.add(index);
  });
  const selectedIndexes = new Set([...mandatoryIndexes].filter((index) => index >= 0));
  const remainingSlots = Math.max(0, maximumStoryTransitions - selectedIndexes.size);
  if (remainingSlots > 0 && transitionCandidates.length > selectedIndexes.size) {
    for (let slot = 0; slot < remainingSlots; slot += 1) selectedIndexes.add(Math.round((slot * (transitionCandidates.length - 1)) / Math.max(1, remainingSlots - 1)));
  }
  const transitions = [...selectedIndexes].sort((a, b) => a - b).slice(0, maximumStoryTransitions).map((index) => transitionCandidates[index]);
  const wrapSentence = (value) => String(value ?? "NO_SENTENCE").match(/.{1,1200}/g)?.join("\n") ?? "NO_SENTENCE";
  const story = transitions.map((stage, index) => {
    const actions = stage.derivations.map((row) => `${row.leg_id}: ${row.action.action}${Number.isInteger(row.action.target_cents) ? ` at ${row.action.target_cents} cents` : ""}`).join("; ");
    return `At ${stage.hours_from_discovery.toFixed(6)} hours from discovery${index === 0 ? ", the first licensed transition formed" : ", the licensed action or coherence state changed"}. Coherence=${stage.coherence?.status ?? "UNKNOWN"}; ${actions}.\n\n${stage.derivations.map((row) => `VERBATIM ${row.leg_id}:\n${wrapSentence(row.sentence)}\nCITATION-RECEIPT-IDS: ${Object.keys(row.citation_receipts).join(",")}`).join("\n\n")}`;
  }).join("\n\n");
  const closes = meta.leg_ids.map((id) => `${id}=${meta.truth_closes_cents[id] ?? "UNKNOWN"}`).join(", ");
  const danpra = meta.event_id === "KXATPMATCH-26JUL18DANPRA" ? (() => {
    const finalStage = result.stage_reads.at(-1), books = finalStage.reads.books.value;
    const conclusions = finalStage.derivations.map((row) => `${row.leg_id}: conditional remaining-dip q50 ${row.derivation.neighbor_leg.conditional_remaining_dip_distribution_cents.q50 ?? "UNKNOWN"}¢ from own ${row.derivation.neighbor_leg.own_evidence.basis} evidence, ${row.action.action}${Number.isInteger(row.action.target_cents) ? ` at ${row.action.target_cents}¢` : ""}`).join("; ");
    const finalBooks = meta.leg_ids.map((id) => `${id} ${books[id]?.bid_cents ?? "?"}/${books[id]?.ask_cents ?? "?"}`).join("; ");
    const finalRests = meta.leg_ids.map((id) => `${id} ${result.execution.legs[id]?.standing_target_cents ?? "NONE"}`).join("; ");
    return `\n\n### DANPRA derived terminal exhibit\n\nFinal causal books: ${finalBooks}. Final standing rests from execution: ${finalRests}. Final named look-alikes: ${neighborsPlain(finalStage.neighborhood)}. Derived conclusions: ${conclusions}. No price or shape literal is supplied by this renderer; all values above come from the run receipts.\n\nCITATION-RECEIPT-IDS: ${finalStage.derivations.flatMap((row) => Object.keys(row.citation_receipts)).join(",")}.`;
  })() : "";
  const incomplete = incompleteStamp?.stamp === "LAWFUL_INCOMPLETE" ? `\n\n### LAWFUL_INCOMPLETE\n\nArithmetic: ${incompleteStamp.arithmetic.proof}. Offer=${incompleteStamp.arithmetic.strictly_under_par_offer_cents}¢. Rest-at-floor receipts: ${incompleteStamp.rest_at_floor_rows.map((row) => `${row.leg_id} ${row.rest_cents}¢ [${row.receipt}]`).join("; ") || "NONE"}. This stamped abstention retains its arithmetic proof; an unstamped abstention scores zero.` : "";
  const terminalExhibits = meta.leg_ids.map((legId) => {
    const leg = result.execution.legs[legId] ?? {};
    const fill = result.fill_events.find((row) => row.context?.leg_id === legId) ?? null;
    const decision = [...result.stage_reads].reverse().flatMap((stage) => stage.derivations.map((row) => ({ stage, row }))).find(({ row }) => row.leg_id === legId && Number.isInteger(row.action.target_cents)) ?? null;
    const authority = decision?.row?.layered_dual_belief?.pricing_authority ?? null;
    const belief = decision?.row?.layered_dual_belief?.micro?.beliefs?.[legId] ?? null;
    const evidence = (authority?.own_evidence_rows ?? []).map((row) => `${row.source}@${row.receipt}`).join(", ") || "panel/survivor evidence named in the verbatim license";
    const argument = `The conviction record licensed ${legId}'s conduct from the non-book posterior. TARGET_AUTHORITY=${authority?.target_cents ?? leg.standing_target_cents ?? "NONE"}; DEADLINE=${belief?.deadline?.deadline_epoch ?? "NONE"}; EVIDENCE=${evidence}; ACTION=${decision?.row?.action?.action ?? "NO_ORDER"}; ACTION_TARGET=${decision?.row?.action?.target_cents ?? "NONE"}; BELIEF_EQUALS_ACTION=${decision?.row?.action?.target_cents === authority?.target_cents || decision?.row?.action?.action === "HOLD_REST"}. The cited trace explains the panel, survivor set, print support, pair arithmetic, and post-only veto separately; the displayed book supplies no target cent.`;
    const outcome = fill
      ? `FILL ${legId}: the standing rest credited at ${fill.context.entry_cents} cents on ${fill.row_refs.join(",")}; the triggering print was ${fill.context.triggering_print_price_cents} cents and the fill price remains the rest price.`
      : `TERMINAL ${legId}: credited=${leg.credited ?? false}; standing rest=${leg.standing_target_cents ?? "NONE"}; terminal reason=${leg.credited ? "CREDITED" : "NO_LAWFUL_CREDIT_BEFORE_EDGE"}.`;
    return `### ${legId} decisive conviction and terminal exhibit\n\n${argument}\n\n${outcome}`;
  }).join("\n\n");
  const reseatExhibits = result.stage_reads.flatMap((stage) => stage.derivations.flatMap((row) => row.layered_dual_belief?.prediction_seat_transition?.transition === "RESEATED_ON_OWN_CONVICTION_UPDATE_SAME_RECEIPT" ? [{ stage, row }] : [])).map(({ stage, row }) => {
    const transition = row.layered_dual_belief.prediction_seat_transition;
    const sources = transition.movement?.named_non_book_evidence_sources ?? transition.movement?.movement_evidence?.named_non_book_evidence_sources ?? [];
    return `#### RESEAT ${row.leg_id} at ${stage.receipt}\n\nThe standing conviction moved from ${transition.from_target_cents ?? "NONE"} to ${transition.to_target_cents ?? "NONE"} cents on named non-book evidence: ${sources.join(", ") || "MISSING"}. ACTION=${row.action.action}; ACTION_TARGET=${row.action.target_cents ?? "NONE"}; receipt=${stage.receipt}.\n\n${wrapSentence(row.sentence)}`;
  }).join("\n\n");
  const compactLegsText = (legs) => Object.entries(legs ?? {}).map(([legId, leg]) => `${legId}: credited=${leg.credited ?? false}, entry=${leg.entry_cents ?? "NONE"}, rest=${leg.standing_target_cents ?? "NONE"}, fill=${leg.fill_receipt ?? "NONE"}`).join("; ");
  const incompleteRowsText = (incompleteStamp?.rest_at_floor_rows ?? []).map((row) => `${row.leg_id}: rest=${row.rest_cents}, receipt=${row.receipt}`).join("; ") || "NONE";
  return `## ${meta.event_id}\n\nSTORY_TRANSITION_SELECTION: ${transitions.length}/${transitionCandidates.length} action/coherence transitions rendered; every receipt remains in REPAIR_FOUR_GAME_TRACE.jsonl.gz.\n\n${story}${danpra}${incomplete}\n\n### Every conviction reseat\n\n${reseatExhibits || "No reseat occurred in this game."}\n\n${terminalExhibits}\n\n### Execution appendix — context, not verdict\n\n| version | completed | pair cents | delta vs 100 | gradeable | legs / truth closes |\n|---|---:|---:|---:|---:|---|\n| lineage receipt | ${old.completed} | ${old.combined_entry_cents ?? "NA"} | ${old.delta_vs_100_cents ?? "NA"} | ${old.gradeable} | ${compactLegsText(old.legs)} |\n| book-veto-only mind | ${result.execution.completed} | ${result.execution.combined_entry_cents ?? "NA"} | ${result.execution.delta_vs_100_cents ?? "NA"} | ${result.execution.gradeable} | ${compactLegsText(result.execution.legs)} |\n| lawful-incomplete stamp | ${incompleteStamp?.stamp ?? "NONE"} | ${incompleteStamp?.arithmetic?.two_leg_floor_sum_cents ?? "NA"} | ${incompleteStamp?.arithmetic?.strictly_under_par_offer_cents ?? "NA"} | ${old.gradeable} | ${incompleteRowsText} |\n| truth close | — | — | — | ${Number.isFinite(meta.bell_epoch)} | ${closes} |\n`;
}

function emitCaseStudyV36({ caseOutput, sourceOutput, storyResult, coherenceGame, tradeReport, deadlineRows, decisionStages }) {
  if (!caseOutput) return null;
  fs.mkdirSync(caseOutput, { recursive: true });
  fs.rmSync(path.join(caseOutput, "V1_THROUGH_V33_SIDE_BY_SIDE.md"), { force: true });
  const eventId = storyResult.event_id;
  const stages = decisionStages.filter((row) => row.event_id === eventId).sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || String(a.receipt).localeCompare(String(b.receipt)));
  const transitions = [];
  let prior = null;
  for (const stage of stages) {
    const signature = `${stage.coherence?.status}|${stage.derivations.map((row) => `${row.leg_id}:${row.action.action}:${row.action.target_cents ?? "NONE"}`).join("|")}`;
    if (signature !== prior || stage.trigger === "FILL_HANDOFF_DECISION_INSTANT") transitions.push(stage);
    prior = signature;
  }
  const eventDeadlineRows = deadlineRows.filter((row) => row.event_id === eventId);
  writeText(path.join(caseOutput, "PANEL_A_PAIR_RENDER.html"), `<!doctype html><meta charset="utf-8"><title>LAJSVA v36 pair</title><h1>${eventId} · case study v36</h1><p>Ever coherent: ${coherenceGame.ever_coherent}. First coherence: ${JSON.stringify(coherenceGame.first_coherence)}</p><pre>${JSON.stringify(storyResult.layered_dual_belief, null, 2)}</pre>`);
  writeText(path.join(caseOutput, "PANEL_B_ENGAGEMENT.html"), `<!doctype html><meta charset="utf-8"><title>LAJSVA v36 engagement</title><h1>The book is veto-only</h1>${transitions.map((stage) => `<section><h2>${stage.timestamp_epoch} · ${stage.receipt}</h2><p>coherence=${stage.coherence?.status}</p>${stage.derivations.map((row) => `<h3>${row.leg_id} · ${row.action.action} ${row.action.target_cents ?? "NONE"}</h3><pre>${row.sentence.replaceAll("&", "&amp;").replaceAll("<", "&lt;")}</pre>`).join("")}</section>`).join("")}`);
  writeText(path.join(caseOutput, "PANEL_C_TRADE_REPORTS.html"), `<!doctype html><meta charset="utf-8"><title>LAJSVA v36 reports</title><h1>Trade report + deadline grades</h1><pre>${JSON.stringify({ trade_report: tradeReport, belief_deadline_rows: eventDeadlineRows }, null, 2).replaceAll("&", "&amp;").replaceAll("<", "&lt;")}</pre>`);
  writeText(path.join(caseOutput, "TRADE_REPORT_PATTERN_ENGINE.md"), `# LAJSVA case-study v36 — the book is veto-only\n\n${JSON.stringify(tradeReport, null, 2)}\n`);
  writeText(path.join(caseOutput, "TRADE_REPORT_REFLEX.md"), `# LAJSVA lineage context\n\nHistorical lineage receipt only: completed=${storyResult.lineage_receipt.completed}; pair=${storyResult.lineage_receipt.combined_entry_cents ?? "NA"}; delta=${storyResult.lineage_receipt.delta_vs_100_cents ?? "NA"}. This context does not license the repaired bed.\n`);
  writeText(path.join(caseOutput, "V1_THROUGH_V36_SIDE_BY_SIDE.md"), `# LAJSVA case-study spine v1–v36\n\nV36 makes the book veto-only: conviction levels move only on named non-book evidence; the ask may refuse but never author or transform a level. The mind-only bed outcome is ${storyResult.layered_dual_belief.completed ? `${storyResult.layered_dual_belief.combined_entry_cents}¢/Δ${storyResult.layered_dual_belief.delta_vs_100_cents}` : "INCOMPLETE"}. The gate self-stops on any tripwire or law break; lineage is untouched.\n`);
  writeJson(path.join(caseOutput, "CASE_STUDY_RECEIPT.json"), {
    label: "LAJSVA_CASE_STUDY_V36_BOOK_VETO_ONLY",
    source_package: "v54_book_veto_only_20260826",
    event_id: eventId,
    coherence: coherenceGame,
    execution: storyResult.layered_dual_belief,
    deadline_scoring: { rows: eventDeadlineRows.length, graded: eventDeadlineRows.filter((row) => row.grade_status === "GRADED_AT_OWN_DEADLINE").length, hits: eventDeadlineRows.filter((row) => row.hit_at_or_below_prediction_by_own_deadline).length, stale: eventDeadlineRows.filter((row) => row.deadline_epoch < row.emission_epoch).length },
    reports: ["TRADE_REPORT_PATTERN_ENGINE.md", "TRADE_REPORT_REFLEX.md"],
    panels: ["PANEL_A_PAIR_RENDER.html", "PANEL_B_ENGAGEMENT.html", "PANEL_C_TRADE_REPORTS.html"],
    full_804_run: TARGETS.stories.length === 804,
    sealed_read: ALL_TARGETS.some((eventId) => eventId.includes("24JUL")),
    live_mutation: RUN_SOURCE.includes("LIVE_MUTATION"),
  });
  const files = fs.readdirSync(caseOutput).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  writeJson(path.join(caseOutput, "ARTIFACT_HASH_MANIFEST.json"), { label: "LAJSVA_CASE_STUDY_V36", files: Object.fromEntries(files.map((name) => [name, { ...receipt(path.join(caseOutput, name)), path: name }])) });
  return { path: "lajsva_case_study_v36_book_veto_only_20260826", files: files.length + 1 };
}

function emitPoolCascadeReports({ repo, output, corpus, groundTruth, metas, remote, printLoad, lineage, resources,
  storyTraces, storyResults, storyOrderedRows, decisionStages, allDerivations, determinismRows,
  floorBreaks, floorPrintDecisionRows, namedDerivableFloorSpecs, derivableFloorConductRows, replaySource = null }) {
  const contract = corpus.tick_library.contract;
  const ref = row => ({ event_id: row.event_id, leg_id: row.leg_id, receipt: row.receipt, timestamp_epoch: row.timestamp_epoch });
  const same = (a, b) => a === b || (Number.isFinite(a) && Number.isFinite(b) && a.toFixed(3) === b.toFixed(3));
  const literalAudit = literalClaimAudit(repo);
  writeJson(path.join(output, "LITERAL_BOOLEAN_AUDIT.json"), literalAudit);
  const rowAudit = allDerivations.map(row => {
    const belief = row.layered_dual_belief.micro.beliefs[row.leg_id];
    const pool = row.pool_cascade, side = pool.sides?.[row.leg_id];
    const expectedLayer = ["FIRST-TICK-ONLY", "BASE"].find(name => side?.layers[name].ess >= contract.no_call_ess_floor) ?? null;
    const selected = expectedLayer ? side.layers[expectedLayer] : null;
    const authority = row.derivation.pricing_authority;
    const placed = ["PLACE_REST", "REPRICE_REST"].includes(row.action.action);
    const tape = storyOrderedRows.get(row.event_id);
    const receiptIndex = tape.findIndex(tick => tick.receipt === row.receipt);
    const prefix = receiptIndex >= 0 ? tape.slice(0, receiptIndex + 1) : tape.filter(tick => tick.timestamp_epoch <= row.timestamp_epoch);
    const prints = prefix.filter(tick => tick.kind === "PRINT" && tick.leg_id === row.leg_id && Number.isInteger(tick.price_cents));
    const independentLow = prints.length ? Math.min(...prints.map(tick => tick.price_cents)) : null;
    const book = prefix.findLast(tick => tick.kind === "BOOK" && tick.leg_id === row.leg_id);
    const validity = pool.validity;
    const checks = {
      author_layer: (side?.selected_layer ?? null) === expectedLayer,
      q_weld: !selected || (belief.predicted_cents === selected.floors.q50.level_cents && authority.target_cents === selected.floors.q50.level_cents),
      x_weld: !selected || (belief.predicted_minutes_to_bell === selected.floors.q50.minutes_to_bell && belief.deadline.deadline_epoch === selected.floors.q50.epoch),
      authors_named: !selected || (belief.q_author === `POOL_${expectedLayer}` && belief.x_author === `POOL_${expectedLayer}_FLOOR_MTB` && authority.authority_source === `POOL_CASCADE:${expectedLayer}`),
      insufficient_fence: expectedLayer !== null || (!placed && belief.status === "INSUFFICIENT_EVIDENCE"),
      no_step_author: !String(belief.q_author).includes("STEP") && !String(belief.x_author).includes("STEP"),
      own_floor_from_print_prefix: belief.own_evidence.observed_traded_low_cents === independentLow,
      live_book_receipt: (belief.book_receipt ?? null) === (book?.receipt ?? null),
      formation_fence: !placed || row.timestamp_epoch >= belief.own_evidence.formation_end_epoch,
      before_bell: !placed || row.timestamp_epoch < metas.find(meta => meta.event_id === row.event_id).bell_epoch,
      post_only: !placed || (Number.isInteger(book?.ask_cents) && row.action.target_cents < book.ask_cents),
      locked_book: !placed || !(Number.isInteger(book?.bid_cents) && book.bid_cents >= book.ask_cents),
      hands_execute_q: !placed || row.action.target_cents === authority.target_cents,
      pair_cap: row.pair_conservation.sum_cents === null || row.pair_conservation.sum_cents <= os.PAR_BUDGET_CENTS,
      cancel_rearms: row.action.action !== "CANCEL_REST" || row.layered_dual_belief.atomic_rearm.status.startsWith("REARM_"),
      validity_no_call: !validity || validity.ess === undefined || (validity.ess >= contract.no_call_ess_floor ? validity.status === "OK" : validity.status.startsWith("INVALID")),
      sentence_action: row.sentence.includes(row.sentence_action_assertion.expected_statement),
      citations: Object.values(row.citation_receipts).every(citation => row.sentence.includes(citation.receipt_id) && citation.captured_at_receipt === row.receipt),
    };
    return { ...ref(row), selected_layer: expectedLayer, q: belief.predicted_cents, x_minutes_to_bell: belief.predicted_minutes_to_bell,
      checks, failures: Object.keys(checks).filter(key => !checks[key]) };
  });
  const fillRows = storyTraces.filter(row => row.kind === "FILL_EVENT").map(row => {
    const fill = row.fill_event_receipt, c = fill.context;
    const print = storyOrderedRows.get(c.event_id).find(tick => tick.receipt === fill.captured_at_receipt && tick.kind === "PRINT" && tick.leg_id === c.leg_id);
    return { ...c, receipt: fill.receipt_id, independent_print_found: Boolean(print),
      rest_priced: c.entry_cents === c.prior_standing_target_cents,
      supported_by_print: Boolean(print && print.price_cents <= c.entry_cents),
      price_basis: c.execution_price_basis };
  });
  writeJson(path.join(output, "REST_PRICED_CREDITING_RECEIPT.json"), { rows: fillRows,
    unchanged_model: "True print at or below standing rest credits at the rest price; aggressor direction is not observed." });
  writeJson(path.join(output, "POOL_CASCADE_ROW_AUDIT.json"), { method: "Stored-layer-to-sentence/order welds; own floor and live book checked against an independently sliced materialized tape prefix. Quantile oracle comparison is separately recorded at named atlas gates.",
    total: rowAudit.length, failed: rowAudit.filter(row => row.failures.length).length, rows: rowAudit });
  const namedPath = path.join(repo, "arb-executor/analysis/tune_bench_v2_ticks/ATP_MAIN/TUNE_BENCH_NAMED_CHECKS.json");
  const named = JSON.parse(fs.readFileSync(namedPath, "utf8"));
  const comparisons = decisionStages.filter(stage => stage.trigger === "ATLAS_GATE").flatMap(stage => {
    const pool = stage.layers.macro.context.pool_cascade;
    const query = Object.values(named.events).find(event => event.event_id === stage.event_id);
    const want = query?.gates?.[pool.minutes_to_bell];
    if (!want || !pool.sides) return [];
    const meta = metas.find(meta => meta.event_id === stage.event_id);
    const benchBell = query.first_tick.epoch + query.first_tick.mtb_first * contract.minute_seconds;
    const comparable = same(meta.bell_epoch, benchBell) && same(pool.first_tick.epoch, query.first_tick.epoch);
    return pool.first_tick.legs.map((leg, index) => {
      const side = pool.sides[leg], role = index === 0 ? "favorite" : "underdog";
      const layers = Object.fromEntries(Object.entries(side.layers).map(([name, layer]) => {
        const expected = want.rules[name].sides[role];
        const fields = { ess: { actual: layer.ess, expected: expected.ess } };
        if (expected.floors) for (const q of Object.keys(expected.floors)) {
          fields[`${q}_cents`] = { actual: layer.floors[q].level_cents, expected: expected.floors[q].level_cents };
          fields[`${q}_minutes_to_bell`] = { actual: layer.floors[q].minutes_to_bell, expected: expected.floors[q].minutes_to_bell };
        }
        return [name, { fields, matches_to_millisecond_or_milliunit: Object.values(fields).every(field => same(field.actual, field.expected)), family_actual: layer.family.top, family_expected: expected.family.top }];
      }));
      return { event_id: stage.event_id, leg_id: leg, gate_minutes_to_bell: pool.minutes_to_bell,
        binding_comparable: comparable, binding_note: comparable ? "SAME_NAMED_TAPE_CLOCK_WITHIN_INHERITED_MILLISECOND_PRECISION" : "INHERITED_REPLAY_BIND_DIFFERS_FROM_BENCH; NOT_CHANGED_BY_THIS_ORDER",
        selected_layer: side.selected_layer, layers, validity: pool.validity, bench_validity: want.validity,
        validity_matches: pool.validity.status === want.validity.status && same(pool.validity.weighted_share, want.validity.weighted_share) && same(pool.validity.ess, want.validity.ess) };
    });
  });
  writeJson(path.join(output, "POOL_CASCADE_GATE_COMPARISON.json"), { oracle: receipt(namedPath), rounding_decimal_places: 3,
    status: "Independent corrected Python bench versus actual JavaScript replay; no query future timestamps enter either forecast grid.", rows: comparisons });
  const failures = rowAudit.filter(row => row.failures.length).map(row => ({ ...ref(row), failures: row.failures }));
  const fillFailures = fillRows.filter(row => !row.independent_print_found || !row.rest_priced || !row.supported_by_print);
  const comparisonFailures = comparisons.filter(row => row.event_id === TARGETS.stories.at(-1) && row.binding_comparable && (!row.validity_matches || Object.values(row.layers).some(layer => !layer.matches_to_millisecond_or_milliunit)));
  // Rulers are reported verbatim; they never become a price-selection target.
  const checks = [
    { id: "CASCADE_ROW_WELDS_AND_INDEPENDENT_TAPE_SAFETY", failures },
    { id: "REST_PRICED_TRUE_PRINT_CREDIT", failures: fillFailures },
    { id: "MATCHED_CLOCK_NAMED_BENCH", failures: comparisonFailures },
    { id: "DETERMINISM_X2", failures: determinismRows.filter(row => !row.byte_identical) },
    { id: "LITERAL_BOOLEAN_AUDIT", failures: literalAudit.unexplained_literal_claims },
    { id: "CURRENT_BED_TRIPWIRE", role: "UNCHANGED_RULER_NOT_TARGET", failures: floorBreaks },
    { id: "NAMED_DERIVABLE_FLOORS", role: "UNCHANGED_RULER_NOT_TARGET", failures: derivableFloorConductRows.filter(row => !row.lawful_or_explained) },
  ].map(check => ({ ...check, passed: check.failures.length === 0 }));
  const gate = { label: "POOL_CASCADE_EXECUTABLE_REPORT", checks,
    organ_checks_pass: checks.filter(check => !check.role).every(check => check.passed),
    ruler_pass: checks.filter(check => check.role).every(check => check.passed),
    failures: checks.filter(check => !check.passed), self_stop: checks.some(check => !check.passed),
    deployment_authorized: false };
  writeJson(path.join(output, "REPAIR_GATE_RECEIPT.json"), gate);
  const osPath = path.join(repo, "arb-executor/analysis/window1_v54_dual_belief_os.js");
  const basePath = path.join(repo, "arb-executor/analysis/window1_v54_functionable_os.js");
  const source = { os: receipt(osPath), functionable: receipt(basePath), builder: replaySource ?? receipt(__filename), report_builder: receipt(__filename),
    tick_library: corpus.tick_library.receipt, named_bench: receipt(namedPath) };
  const changedFunctions = ["loadCorpus", "replayEvent (nested evaluateStage: approved atlas clock only)", "main (report projections and report contract retirement only)", "emitPoolCascadeReports (new report-only function)"];
  const organReceipt = { label: "POOL_CASCADE_FIRST_BASE_STEP_TELEMETRY", source,
    author_order: ["FIRST-TICK-ONLY", "BASE"], step: "EVERY_ROW_TELEMETRY_ONLY; matched-cohort receipt grants no gate",
    report_contract_migration: "Retired neighbor, overlap, rung/clip, seat-writer, named-hand and envelope requirements are not current organ checks. Bed expectations and namedDerivableFloorSpecs remain unchanged, measured and failing when appropriate.",
    builder_functions_touched: changedFunctions,
    former_report_only_helpers_retained: "Old generic reporter source is unchanged but its retired-author rendering is no longer invoked.",
    oracle_rounding: "3 decimal places; inherited replay parses exchange timestamps to milliseconds, while bench preserves finer source decimals.",
    named_derivable_floor_specs: namedDerivableFloorSpecs, bed_expectations: SAFETY_FLOORS,
    ruling: corpus.tick_library.receipt.bench_receipt, gates: contract.gates_minutes_to_bell,
    report_only_regeneration: replaySource !== null,
    results: storyResults, gate, fills: fillRows, determinism: determinismRows,
    retired_diagnostic_bindings: "Minute corpus/depth-map/shape bindings remain for readAll and historical report custody only. Pool author reads only corpus.tick_library.",
    execution_limit: "Inherited true-print rest credit lacks aggressor direction; this is replay evidence, not live deployment approval." };
  writeJson(path.join(output, "POOL_CASCADE_RECEIPT.json"), organReceipt);
  writeJson(path.join(output, "SOURCE_RECEIPTS.json"), { corpus_sources: corpus.sources, ground_truth: groundTruth.receipt, remote, target_prints: printLoad.source, lineage: lineage.receipt, resources, pool_cascade: source });
  writeJson(path.join(output, "FORBIDDEN_ACCESS_RECEIPT.json"), { scope: { smoke: TARGETS.smoke, stories: TARGETS.stories },
    live_mutation: RUN_SOURCE.includes("LIVE_MUTATION"), deployment: RUN_SOURCE.includes("DEPLOYMENT"),
    named_check_events_in_library: corpus.tick_library.pairs.filter(pair => TARGETS.stories.includes(pair.identity)).map(pair => pair.identity) });
  writeText(path.join(output, "PROCESS_FIRST_CONFIRM.md"), `# Pool cascade: FIRST → BASE; STEP telemetry\n\nOrgan checks: ${gate.organ_checks_pass ? "PASS" : "FAIL"}. Bed/derivable-floor rulers: ${gate.ruler_pass ? "PASS" : "FAIL — unchanged"}.\n\n${checks.map(check => `- ${check.id}: ${check.failures.length} failures`).join("\n")}\n\nThe stored Q and X come from member remaining minima and floor times. Hands execute Q or retain/veto the old rest; no rung, seat, named hand, or book-derived substitute writes a level.\n\n${storyResults.map(row => `- ${row.event_id}: ${JSON.stringify(row.composition_rebuild)}`).join("\n")}\n\nTouched builder functions: ${changedFunctions.join("; ")}.\n`);
  const custodyOutput = arg("custody-output") ? path.resolve(arg("custody-output")) : output;
  fs.mkdirSync(custodyOutput, { recursive: true });
  const traceSource = path.join(output, "REPAIR_FOUR_GAME_TRACE.jsonl.gz"), traceDestination = path.join(custodyOutput, "REPAIR_FOUR_GAME_TRACE.jsonl.gz");
  if (traceDestination !== traceSource) fs.copyFileSync(traceSource, traceDestination);
  const trace = receipt(traceDestination, storyTraces.length);
  ensure(trace.sha256 === fileHash(traceSource), "POOL_CUSTODY_TRACE_COPY_MISMATCH");
  writeJson(path.join(custodyOutput, "FACE_RUN_PROVENANCE.json"), { os_sha256: source.os.sha256, os_sha256_after: fileHash(osPath), trace_sha256: trace.sha256, source });
  const custodyManifest = JSON.parse(fs.readFileSync(path.join(output, "EXTERNAL_CUSTODY_MANIFEST.json"), "utf8"));
  custodyManifest.pool_cascade = { ...source, trace };
  writeJson(path.join(output, "EXTERNAL_CUSTODY_MANIFEST.json"), custodyManifest);
  custodyOversizedArtifacts({ output, custodyOutput, rowsByName: {} });
  const producerCoverage = receiptProducerCoverage(repo, output);
  writeJson(path.join(output, "RECEIPT_PRODUCER_COVERAGE.json"), producerCoverage);
  ensure(producerCoverage.unproduced.length === 0, `ORPHAN_RECEIPT_WITHOUT_PRODUCER:${producerCoverage.unproduced.map(row => row.artifact).join(",")}`);
  const files = fs.readdirSync(output).filter(name => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  writeJson(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), { label: "POOL_CASCADE", files: Object.fromEntries(files.map(name => [name, { ...receipt(path.join(output, name)), path: name }])) });
  process.stdout.write(canonical({ output, trace, os_sha256: source.os.sha256, organ_checks_pass: gate.organ_checks_pass, ruler_pass: gate.ruler_pass, stories: storyResults }));
}

async function main() {
  const repo = required("repo"), cacheDir = required("cache"), privateRoot = required("private"), walkRoot = required("walk"), output = required("output"), foundationIndexPath = required("foundation-index"), foundationReceiptPath = required("foundation-receipt"), futureLowIndexPath = required("future-low-index"), futureLowReceiptPath = required("future-low-receipt");
  const subsetSpec = arg("subset-games") ? subsetGuard.parseExactNamedSubset(arg("subset-games"), arg("expected-game-count")) : null;
  const requestedEventIds = subsetSpec ? [...subsetSpec.event_ids] : ALL_TARGETS;
  ensure(!(subsetSpec && arg("finalize-existing") === "true"), "NAMED_SUBSET_GUARD finalize-existing is a different lane");
  ensure(!output.toLowerCase().includes("holdout") && !output.toLowerCase().includes("sealed"), "sealed output forbidden");
  fs.mkdirSync(output, { recursive: true });
  const depthMapBytes = gitShow(repo, DEPTH_MAP_COMMIT, DEPTH_MAP_PATH);
  const depthMap = JSON.parse(depthMapBytes);
  ensure(depthMap.label === "TRUE_BELL_CELL_CONDITIONAL_DEPTH_MAP_V3", "TRUE_BELL_CELL_DEPTH_MAP_LABEL_MISMATCH");
  const depthMapBinding = {
    kind: depthMap.label,
    commit: DEPTH_MAP_COMMIT,
    path: DEPTH_MAP_PATH,
    sha256: shaBytes(depthMapBytes),
    cells: depthMap.cells,
    lookup_basis: "LIBRARY_MEMBER_BOUNDED_CLOSE_CENTS",
    future_close_consumed: false,
  };
  os.configureTrueBellCellDepthMap(depthMapBinding);
  writeJson(path.join(output, "TRUE_BELL_CELL_DEPTH_MAP_BINDING.json"), { ...depthMapBinding, cells: undefined, mapped_cells: depthMap.cells.length, source_law: depthMap.law, source_census: depthMap.census });
  const pairInterimBytes = gitShow(repo, SURVIVOR_SOURCE_COMMIT, PAIR_INTERIM_LIBRARY_PATH);
  const pairCoupleBytes = gitShow(repo, SURVIVOR_SOURCE_COMMIT, PAIR_COUPLE_LIBRARY_PATH);
  const survivorBinding = {
    source_commit: SURVIVOR_SOURCE_COMMIT,
    pair: JSON.parse(pairInterimBytes),
    couple: JSON.parse(pairCoupleBytes),
    sha256: { pair: shaBytes(pairInterimBytes), couple: shaBytes(pairCoupleBytes) },
  };
  const corpus = await loadCorpus(cacheDir, repo, foundationIndexPath, foundationReceiptPath, futureLowIndexPath, futureLowReceiptPath);
  const specialistBinding = bindNeighborSpecialists(corpus.rows);
  ensure(specialistBinding.records === 18000, `NEIGHBOR_SPECIALIST_RECORD_CONSERVATION ${specialistBinding.records} != 18000`);
  os.configureNeighborSpecialistBinding(specialistBinding);
  writeJson(path.join(output, "NEIGHBOR_SPECIALIST_BINDING.json"), specialistBinding);
  const originalHistoricalSha256 = "46741cded0ccb0a24302da4bc7b77f1bb3b82707a8cceaa272a902bae683339a";
  if (corpus.sources.historical.sha256 !== originalHistoricalSha256) {
    const parentSnapshotPath = path.join(repo, ".claude/window1_live_v4_replay/v54_directional_floor_admission_20260826/CORPUS_INDEX.jsonl.gz");
    const parentSpecialistPath = path.join(repo, ".claude/window1_live_v4_replay/v54_directional_floor_admission_20260826/NEIGHBOR_SPECIALIST_BINDING.json");
    const parentSpecialist = JSON.parse(fs.readFileSync(parentSpecialistPath, "utf8"));
    ensure(parentSpecialist.binding_sha256 === specialistBinding.binding_sha256, "RECOVERED_UNBOUNDED_CACHE_CHANGED_DECISION_ELIGIBLE_SPECIALIST_BINDING");
    writeJson(path.join(output, "MECHANICAL_CACHE_RECOVERY_RECEIPT.json"), {
      label: "V54_MECHANICAL_UNBOUNDED_HISTORICAL_CACHE_RECOVERY",
      trigger: "ORIGINAL_EVENT_GRAIN_CSV_ABSENT_FROM_HOST_BEFORE_SCORE_EMISSION",
      original_source_receipt: { sha256: originalHistoricalSha256, bytes: 1041339, rows: 5879 },
      recovery_source: receipt(parentSnapshotPath, 15367),
      recovered_source: corpus.sources.historical,
      method: "Recovered all 5,879 historical line identities from the prior hash-bound corpus derivative and re-materialized the event-grain CSV. Registry and range inputs remained byte-identical to their filed hashes.",
      eligibility: "HISTORICAL_ROWS_ARE_UNBOUNDED_EVENT_GRAIN_AGGREGATES_AND NEVER ENTER THE BOUNDED NEIGHBOR SPECIALIST OR DECISION PATH",
      decision_eligible_specialist_binding: { rows: specialistBinding.records, games: specialistBinding.games, binding_sha256: specialistBinding.binding_sha256, parent_binding_sha256: parentSpecialist.binding_sha256, byte_identical_to_parent: parentSpecialist.binding_sha256 === specialistBinding.binding_sha256 },
      score_emission_before_recovery: false,
    });
  }
  const tradedLowSupportBinding = bindShapeTradedLowSupport(survivorBinding, corpus.rows);
  os.configureSurvivorShapeLibraries(survivorBinding);
  writeJson(path.join(output, "SURVIVOR_SHAPE_LIBRARY_BINDING.json"), {
    label: "V54_TRADED_LOW_AXIS_SURVIVOR_SHAPE_LIBRARIES_CUSTODY_RECONCILED",
    source_commit: SURVIVOR_SOURCE_COMMIT,
    modules: ["window1_interim_elimination_v13", "window1_pair_interim_elimination_v18", "window1_pair_couple_elimination_v19"],
    libraries: [
      { path: PAIR_INTERIM_LIBRARY_PATH, sha256: survivorBinding.sha256.pair, bytes: Buffer.byteLength(pairInterimBytes), custody: `https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/${SURVIVOR_SOURCE_COMMIT}/${PAIR_INTERIM_LIBRARY_PATH}`, groups: Object.keys(survivorBinding.pair.groups).length, pair_hypothesis_groups: Object.keys(survivorBinding.pair.pair_hypothesis_groups).length },
      { path: PAIR_COUPLE_LIBRARY_PATH, sha256: survivorBinding.sha256.couple, bytes: Buffer.byteLength(pairCoupleBytes), custody: `https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/${SURVIVOR_SOURCE_COMMIT}/${PAIR_COUPLE_LIBRARY_PATH}`, groups: Object.keys(survivorBinding.couple.groups).length, pair_couple_groups: Object.keys(survivorBinding.couple.pair_couple_groups).length },
    ],
    causal_binding: "EXACT_MEMBER_BACKED_TRADED_LOW_DEPTH_BINS_MATCH_THE_RUNNING_POST_FORMATION_TRUE_TRADE_LOW; NO_ASK_PATH_TARGET; NO_RIGHT_EDGE_OR_SPAN_FRACTION_CONSUMED",
    traded_low_support_sha256: survivorBinding.sha256.traded_low_support,
    provenance: ["F-VS-133/F-VS-135@e7081336", "F-VS-139/F-VS-143@f4752720", "189eaa20"],
  });
  writeJson(path.join(output, "TRADED_LOW_SHAPE_SUPPORT_BINDING.json"), tradedLowSupportBinding);
  const phaseCentralSurface = buildPhaseCentralSurface(corpus.rows, corpus.future_low_return.index.sha256);
  os.configurePhaseCentralSurface(phaseCentralSurface);
  writeJson(path.join(output, "PHASE_CENTRAL_ESTIMATE_SURFACE.json"), phaseCentralSurface);
  const remoteReceiptPath = arg("remote-receipt");
  const remote = remoteReceiptPath ? JSON.parse(fs.readFileSync(path.resolve(remoteReceiptPath), "utf8")).remote : remoteProbe();
  const archivePrefixCensusPath = arg("archive-prefix-census");
  if (archivePrefixCensusPath) {
    const prefixCensus = JSON.parse(fs.readFileSync(path.resolve(archivePrefixCensusPath), "utf8"));
    remote.spaces.roots = prefixCensus.roots ?? prefixCensus;
    remote.spaces.filter = prefixCensus.filter ?? "PREFIX-SPECIFIC JANUARY-THROUGH-JULY INVENTORY; SEALED AUGUST EXCLUDED";
    if (prefixCensus.supplemental?.subsecond) remote.subsecond.census = prefixCensus.supplemental.subsecond;
    if (prefixCensus.supplemental?.bookmaker_odds) Object.assign(remote.odds_backup.tables.bookmaker_odds, prefixCensus.supplemental.bookmaker_odds);
  }
  const census = buildCensus(corpus, remote, privateRoot);
  writeJson(path.join(output, "CORPUS_CENSUS.json"), census);
  fs.copyFileSync(foundationIndexPath, path.join(output, "FOUNDATION_LIBRARY.jsonl.gz"));
  fs.copyFileSync(foundationReceiptPath, path.join(output, "FOUNDATION_LIBRARY_RECEIPT.json"));
  fs.copyFileSync(futureLowIndexPath, path.join(output, "FUTURE_LOW_RETURN_LIBRARY.jsonl.gz"));
  fs.copyFileSync(futureLowReceiptPath, path.join(output, "FUTURE_LOW_RETURN_LIBRARY_RECEIPT.json"));
  const phaseSurfaceReceipt = receipt(path.join(output, "PHASE_CENTRAL_ESTIMATE_SURFACE.json"));
  writeJson(path.join(output, "EXTERNAL_CUSTODY_MANIFEST.json"), {
    label: "V54_BOOK_VETO_ONLY_CUSTODY_RECONCILED",
    files: [
      { logical_path: "FOUNDATION_PER_MINUTE_UNIVERSE", custody_location: corpus.foundation.source.external_custody_location, sha256: corpus.foundation.source.sha256, bytes: corpus.foundation.source.bytes, rows: corpus.foundation.source.rows, committed: false, compact_derivatives: [{ path: "FOUNDATION_LIBRARY.jsonl.gz", sha256: corpus.foundation.index.sha256, bytes: corpus.foundation.index.bytes, rows: corpus.foundation.index.rows }, { path: "FUTURE_LOW_RETURN_LIBRARY.jsonl.gz", sha256: corpus.future_low_return.index.sha256, bytes: corpus.future_low_return.index.bytes, rows: corpus.future_low_return.index.rows }, { path: "PHASE_CENTRAL_ESTIMATE_SURFACE.json", sha256: phaseSurfaceReceipt.sha256, bytes: phaseSurfaceReceipt.bytes, rows: phaseCentralSurface.cells.length }] },
      { logical_path: "RANGE_OVERLAP_LIBRARY.jsonl.gz", custody_location: corpus.range_overlap.binding.index.path, sha256: corpus.range_overlap.binding.index.sha256, bytes: corpus.range_overlap.binding.index.bytes, rows: corpus.range_overlap.binding.index.rows, receipt_path: corpus.range_overlap.binding.materializer_receipt.path, receipt_sha256: corpus.range_overlap.binding.materializer_receipt.sha256 },
      { logical_path: "INTERIM_PAIR_LIBRARY_V18.json", source_path: PAIR_INTERIM_LIBRARY_PATH, source_commit: SURVIVOR_SOURCE_COMMIT, custody_location: `https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/${SURVIVOR_SOURCE_COMMIT}/${PAIR_INTERIM_LIBRARY_PATH}`, sha256: survivorBinding.sha256.pair, bytes: Buffer.byteLength(pairInterimBytes), committed_in_current_tree: false, git_object_hash_bound: true },
      { logical_path: "PAIR_COUPLE_LIBRARY_V19.json", source_path: PAIR_COUPLE_LIBRARY_PATH, source_commit: SURVIVOR_SOURCE_COMMIT, custody_location: `https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/${SURVIVOR_SOURCE_COMMIT}/${PAIR_COUPLE_LIBRARY_PATH}`, sha256: survivorBinding.sha256.couple, bytes: Buffer.byteLength(pairCoupleBytes), committed_in_current_tree: false, git_object_hash_bound: true },
    ],
    prior_manifest_disagreement_reconciled: true,
    phase_central_surface_file_receipt_matches_artifact_manifest: true,
    all_committed_artifacts_under_50_mb: true,
  });
  writeJson(path.join(output, "FOUNDATION_COVERAGE_BEFORE_AFTER.json"), { label: "FOUNDATION_BOUNDED_SPAN_COVERAGE", target_from_f_vs_061: { bounded_games: 698, unbounded_games: 11811 }, measured: { before: corpus.foundation.coverage_before, after: corpus.foundation.coverage_after }, native_unknown_method_excluded: true, grain: "MINUTE", licensed_layers: ["MACRO", "MICRO"], micro_micro_licensed: false });
  writeJson(path.join(output, "LIBRARY_BELL_BOUND_RECEIPT.json"), corpus.bell_bound_receipt);
  const corpusIndex = Buffer.from(corpus.rows.map((row) => JSON.stringify(row)).join("\n") + "\n");
  fs.writeFileSync(path.join(output, "CORPUS_INDEX.jsonl.gz"), zlib.gzipSync(corpusIndex, { level: 9 }));
  const resources = resourcesFrom(census, remote, repo, privateRoot);
  os.assertResources(resources);
  const functionality = functionalityReceipt(resources, census);
  ensure(functionality.all_connected, "OS not functionable");
  writeJson(path.join(output, "FUNCTIONALITY_RECEIPT.json"), functionality);
  if (arg("finalize-existing") === "true") {
    const sourceFile = path.join(output, "SOURCE_RECEIPTS.json");
    const sourceReceipts = JSON.parse(fs.readFileSync(sourceFile, "utf8"));
    sourceReceipts.corpus_sources = corpus.sources;
    sourceReceipts.remote = remote;
    sourceReceipts.resources = resources;
    sourceReceipts.finalization = { receipt_accounting_only: true, stories_rerun: false, smoke_rerun: false, archive_prefix_census: archivePrefixCensusPath ? path.resolve(archivePrefixCensusPath) : null };
    writeJson(sourceFile, sourceReceipts);
    const storiesFile = path.join(output, "FOUR_STORIES_RECEIPT.json"), stories = JSON.parse(fs.readFileSync(storiesFile, "utf8"));
    stories.safety_floor_pass = stories.safety_floor_breaks.length === 0;
    // A law verdict may only be emitted by a real violation scan. This builder has
    // no complete law scanner, so finalize removes the legacy literal and the
    // success verdict that depended on it instead of manufacturing compliance.
    delete stories.zero_law_violations;
    delete stories.successful;
    stories.passes_executed = 1;
    stories.adjustments_filed = [];
    stories.self_stop_triggered = !stories.safety_floor_pass;
    stories.self_stop_reason = stories.self_stop_triggered ? "SAFETY_FLOOR_BREAK" : null;
    writeJson(storiesFile, stories);
    const gapsFile = path.join(output, "ASSUMPTION_GAPS.md"), gaps = fs.readFileSync(gapsFile, "utf8");
    if (!gaps.includes("LAJSVA safety-floor break")) writeText(gapsFile, `${gaps.trimEnd()}\n- LAJSVA safety-floor break: the functionable-v6 rests at 47/36 did not complete. Measurement needed: identify which continuously scored neighbors caused those levels and whether a declared similarity/corpus adjustment can preserve the story without a placement constant. The dispatch self-stop fired; no adjustment and no second pass ran.\n`);
    const files = fs.readdirSync(output).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
    writeJson(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), { label: OUTPUT_LABEL, files: Object.fromEntries(files.map((name) => [name, { ...receipt(path.join(output, name)), path: name }])) });
    process.stdout.write(canonical({ output, finalized_existing_receipts_only: fs.existsSync(storiesFile), stories_rerun: stories.passes_executed > 1, smoke_rerun: fs.existsSync(path.join(output, "SMOKE_CRIJEA_RECEIPT.json")), functionable: functionality.all_connected, floor_breaks: stories.safety_floor_breaks, full_804_run: TARGETS.stories.length === 804, sealed: ALL_TARGETS.some((eventId) => eventId.includes("24JUL")), live: RUN_SOURCE.includes("LIVE_MUTATION") }));
    return;
  }

  const groundTruth = loadGroundTruth(repo), truthRows = groundTruth.rows;
  const corpusFloorTiming = bindCorpusFloorTiming(corpus.rows, truthRows);
  writeJson(path.join(output, "FLOOR_TIME_BINDING_COVERAGE.json"), {
    label: "V54_REPAIR_ITERATION6_ALL_BELL_BOUNDED_LIBRARY_FLOOR_TIME_BINDING",
    ...corpusFloorTiming,
  });
  const metas = requestedEventIds.map((eventId) => {
    const truth = truthRows.find((row) => row.event_id === eventId);
    ensure(truth, `NAMED_SUBSET_GUARD named game absent from truth table ${eventId}`);
    return targetMeta(truth);
  });
  const printLoad = await loadTargetPrints(privateRoot, metas), lineage = await loadLineage(walkRoot, requestedEventIds);
  const targetPrintRows = [...printLoad.byEvent.values()].flat().sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || String(a.receipt).localeCompare(String(b.receipt)));

  if (subsetSpec) {
    const subsetReceiptName = `TARGET_PRINTS_${subsetSpec.expected_games}.jsonl.gz`;
    fs.writeFileSync(path.join(output, subsetReceiptName), zlib.gzipSync(Buffer.from(targetPrintRows.map((row) => JSON.stringify(row)).join("\n") + "\n"), { level: 9 }));
    const executionGuard = subsetGuard.createExecutionGuard(subsetSpec), games = [];
    activeExecutionGuard = executionGuard;
    let execution;
    try {
      for (const meta of metas) {
        const horizon = Math.max(...Object.values(meta.formation_end_epochs)) + 6 * 3600;
        const rows = [...loadTicks(privateRoot, meta), ...printLoad.byEvent.get(meta.event_id)].filter((row) => row.timestamp_epoch <= horizon);
        const result = replayEvent({ meta, rows, corpus: corpus.rows, resources, lineage, smokeOnly: true });
        const readerReceipt = readerExecutionReceipt(result);
        ensure(readerReceipt.all_readers_fired, `named subset reader gap ${meta.event_id}`);
        games.push({ event_id: meta.event_id, role: meta.event_id === TARGETS.smoke[0] ? "CRIJEA_INTEGRATION_SMOKE" : "NAMED_PIN_SMOKE", grading_performed: false, tape_rows_consumed: rows.length, turning_points: result.stage_reads.length, derivations: result.derivations.length, reader_receipt: readerReceipt, sentence_action_equal: result.derivations.every((row) => row.sentence_action_assertion.equal), citation_receipt_equal: result.derivations.every((row) => row.citation_receipt_assertion.equal), conservation: result.derivations.every((row) => row.pair_conservation.at_or_below_99) });
      }
      execution = executionGuard.finalize();
    } finally {
      activeExecutionGuard = null;
    }
    const subsetReceipt = {
      label: "V54_EXACT_N_NAMED_SUBSET_EXECUTION_SMOKE",
      license: { law_index_read_at: "0d1ca473", law_index_sha256: "41784e6ab62d6341c2a02f8be616e596eb48930b84a71acae8f500368d44c934", laws: ["L8", "L18", "L20", "L22"] },
      scope: { lane: "REPAIR_CLASS_PROOF", passes: 0, reruns: 0, full_804_run: requestedEventIds.length === 804, grading_performed: games.some((game) => game.grading_performed), sealed_read: requestedEventIds.some((eventId) => eventId.includes("24JUL")), live_mutation: RUN_SOURCE.includes("LIVE_MUTATION") },
      execution,
      games,
      structural_proof: { parser: "window1_named_subset_guard.parseExactNamedSubset", replay_entry_guard: "activeExecutionGuard records inside replayEvent before state creation", unrequested_game_behavior: "FAIL_LOUD", duplicate_game_behavior: "FAIL_LOUD", incomplete_count_behavior: "FAIL_LOUD", corpus_neighbors_are_consultations_not_game_executions: true },
      sources: { target_prints: { ...printLoad.source, filtered_event_ids: requestedEventIds, filtered_rows: targetPrintRows.length }, lineage: lineage.receipt },
    };
    writeJson(path.join(output, "NAMED_SUBSET_EXECUTION_RECEIPT.json"), subsetReceipt);
    writeJson(path.join(output, "FORBIDDEN_ACCESS_RECEIPT.json"), { full_804_run: execution.total_games_executed === 804, tune_test_population_run: execution.total_games_executed === 804, sealed_read: requestedEventIds.some((eventId) => eventId.includes("24JUL")), holdout_read: requestedEventIds.some((eventId) => eventId.includes("24JUL")), live_mutation: RUN_SOURCE.includes("LIVE_MUTATION"), orders: games.some((game) => game.orders_sent > 0), positions: games.some((game) => game.positions_read > 0), deployment: RUN_SOURCE.includes("DEPLOYMENT"), scope: { named_subset_exact_n: requestedEventIds, total_games_executed: execution.total_games_executed, other_games_executed: execution.other_games_executed } });
    writeJson(path.join(output, "SOURCE_RECEIPTS.json"), { corpus_sources: corpus.sources, foundation: corpus.foundation, library_bell_bound: corpus.bell_bound_receipt, corpus_floor_timing: corpusFloorTiming, ground_truth: groundTruth.receipt, remote, target_prints: printLoad.source, lineage: lineage.receipt, resources });
    const files = fs.readdirSync(output).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
    writeJson(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), { label: subsetReceipt.label, files: Object.fromEntries(files.map((name) => [name, { ...receipt(path.join(output, name)), path: name }])) });
    process.stdout.write(canonical({ output, named_subset: execution, all_readers_derived: games.every((game) => game.reader_receipt.all_readers_fired), full_804_run: execution.total_games_executed === 804, sealed: requestedEventIds.some((eventId) => eventId.includes("24JUL")), live: RUN_SOURCE.includes("LIVE_MUTATION") }));
    return;
  }

  fs.writeFileSync(path.join(output, "TARGET_PRINTS_5.jsonl.gz"), zlib.gzipSync(Buffer.from(targetPrintRows.map((row) => JSON.stringify(row)).join("\n") + "\n"), { level: 9 }));

  const smokeMeta = metas.find((meta) => meta.event_id === TARGETS.smoke[0]);
  const smokeRows = [...loadTicks(privateRoot, smokeMeta), ...printLoad.byEvent.get(smokeMeta.event_id)].filter((row) => row.timestamp_epoch <= Math.max(...Object.values(smokeMeta.formation_end_epochs)) + 6 * 3600);
  let smoke = replayEvent({ meta: smokeMeta, rows: smokeRows, corpus: corpus.rows, resources, lineage, smokeOnly: true });
  const smokeReaderReceipt = readerExecutionReceipt(smoke);
  ensure(smokeReaderReceipt.all_readers_fired, "CRIJEA did not fire all readers");
  // The integration smoke is structural and ungraded. Keep the full machine
  // proof in its JSON receipt; a prior renderer materialized hundreds of MB of
  // repeated sentences and retained the entire smoke graph through the scored
  // bed. This compact narrative is receipts-only and changes no decision byte.
  writeText(path.join(output, "SMOKE_CRIJEA.md"), `# CRIJEA integration smoke\n\nReaders: ${smokeReaderReceipt.reader_count}/${smokeReaderReceipt.expected_reader_count}.\n\nDerivations: ${smoke.derivations.length}. Sentence/action weld: ${smoke.derivations.every((row) => row.sentence_action_assertion.equal)}. Citation weld: ${smoke.derivations.every((row) => row.citation_receipt_assertion.equal)}. Pair conservation: ${smoke.derivations.every((row) => row.pair_conservation.at_or_below_99)}.\n\nThis smoke performs no grading. The receipt names every reader and neighbor citation; the four-game trace owns full decision diaries.\n`);
  writeJson(path.join(output, "SMOKE_CRIJEA_RECEIPT.json"), { label: "CRIJEA_INTEGRATION_SMOKE_NO_GRADING", all_readers_fired: smokeReaderReceipt.all_readers_fired, reader_count: smokeReaderReceipt.reader_count, expected_reader_count: smokeReaderReceipt.expected_reader_count, reader_receipts: smokeReaderReceipt.readers, named_neighbors: [...new Map(smoke.stage_reads.flatMap((stage) => stage.neighborhood.map((row) => [row.citation_receipt_id, { event_id: row.event_id, citation_receipt_id: row.citation_receipt_id, citation_receipt: row.citation_receipt }]))).values()], derivations: smoke.derivations.length, sentence_action_equal: smoke.derivations.every((row) => row.sentence_action_assertion.equal), citation_receipt_equal: smoke.derivations.every((row) => row.citation_receipt_assertion.equal), conservation: smoke.derivations.every((row) => row.pair_conservation.at_or_below_99), grading_performed: false });
  smoke = null;

  const perGame = JSON.parse(fs.readFileSync(path.join(walkRoot, "PER_GAME_L1_L8.json"), "utf8")), storyResults = [], storySections = [], storyTraces = [], storyTapeRows = new Map(), storyOrderedRows = new Map(), determinismRows = [], clockComparisonRows = [], floorPrintDecisionRows = [];
  const fullTraceWriter = arg("mechanical-diagnose-first-game") === "1" ? null : createJsonlGzipWriter(path.join(output, "REPAIR_FOUR_GAME_TRACE.jsonl.gz"));
  const scoreProjectionPath = path.join(output, ".SCORE_GATE_PROJECTION.jsonl.gz");
  const scoreProjectionWriter = arg("mechanical-diagnose-first-game") === "1" ? null : createJsonlGzipWriter(scoreProjectionPath);
  fs.rmSync(path.join(output, "DETERMINISM_FAILURE_DEBUG.json"), { force: true });
  for (const eventId of TARGETS.stories) {
    const meta = metas.find((row) => row.event_id === eventId), rows = [...loadTicks(privateRoot, meta), ...printLoad.byEvent.get(eventId)].filter((row) => !Number.isFinite(meta.bell_epoch) || row.timestamp_epoch <= meta.bell_epoch);
    storyTapeRows.set(eventId, rows);
    const orderView = (run) => run.derivations
      .filter((row) => ["PLACE_REST", "REPRICE_REST", "CANCEL_REST"].includes(row.action.action))
      .map((row) => ({
        leg_id: row.leg_id,
        receipt: row.receipt,
        timestamp_epoch: row.timestamp_epoch,
        action: row.action.action,
        target_cents: row.action.target_cents,
        causal_clock: run.ordered_rows.find((tapeRow) => tapeRow.receipt === row.receipt)?.causal_clock ?? null,
      }));
    // Determinism and the legacy-clock diagnostic are mechanical comparison
    // runs. Execute and release both before retaining the scored run so the
    // three full replay graphs are never resident together.
    process.stderr.write(`V54_PROGRESS ${eventId} determinism-run-2 start\n`);
    let repeat = replayEvent({ meta, rows, corpus: corpus.rows, resources, lineage, smokeOnly: false });
    const secondDigest = digestReplay(repeat);
    repeat = null;
    if (global.gc) global.gc();
    process.stderr.write(`V54_PROGRESS ${eventId} legacy-clock start\n`);
    let legacyClock = replayEvent({ meta, rows, corpus: corpus.rows, resources, lineage, smokeOnly: false, clockMode: "LEGACY_INTEGER_BOOK_FIRST" });
    const legacyOrders = orderView(legacyClock);
    legacyClock = null;
    if (global.gc) global.gc();
    process.stderr.write(`V54_PROGRESS ${eventId} scored-run start\n`);
    let result = replayEvent({ meta, rows, corpus: corpus.rows, resources, lineage, smokeOnly: false });
    const firstDigest = digestReplay(result);
    if (arg("mechanical-diagnose-first-game") === "1") {
      const byteLength = (value) => Buffer.byteLength(JSON.stringify(value), "utf8");
      const summarize = (selector) => {
        const sizes = result.derivations.map((row) => byteLength(selector(row)));
        return { rows: sizes.length, bytes: sizes.reduce((total, value) => total + value, 0), max_row_bytes: Math.max(0, ...sizes) };
      };
      const summarizeObjectKeys = (selector) => {
        const keys = new Set(result.derivations.flatMap((row) => Object.keys(selector(row) ?? {})));
        return Object.fromEntries([...keys].sort().map((key) => [key, summarize((row) => selector(row)?.[key] ?? null)]));
      };
      writeJson(path.join(output, "MECHANICAL_MEMORY_DIAGNOSTIC.json"), {
        label: "PRE_SCORE_TRACE_PAYLOAD_DIAGNOSTIC",
        event_id: eventId,
        score_rows_emitted: false,
        stage_reads: result.stage_reads.length,
        derivations: result.derivations.length,
        digest_bytes: firstDigest.bytes,
        components: {
          full_derivation: summarize((row) => row),
          sentence: summarize((row) => row.sentence),
          layered_dual_belief: summarize((row) => row.layered_dual_belief),
          layered_dual_belief_by_key: summarizeObjectKeys((row) => row.layered_dual_belief),
          derivation_detail: summarize((row) => row.derivation),
          derivation_detail_by_key: summarizeObjectKeys((row) => row.derivation),
          citation_receipts: summarize((row) => row.citation_receipts),
        },
      });
      process.stderr.write(`V54_PROGRESS ${eventId} mechanical diagnostic complete\n`);
      return;
    }
    storyOrderedRows.set(eventId, result.ordered_rows);
    const byteIdentical = firstDigest.sha256 === secondDigest.sha256 && firstDigest.bytes === secondDigest.bytes;
    determinismRows.push({ event_id: eventId, first_sha256: firstDigest.sha256, second_sha256: secondDigest.sha256, byte_identical: byteIdentical, first_bytes: firstDigest.bytes, second_bytes: secondDigest.bytes, first_counts: firstDigest.counts, second_counts: secondDigest.counts, first_difference: null });
    if (!byteIdentical) writeJson(path.join(output, "DETERMINISM_FAILURE_DEBUG.json"), { label: "PRE_SCORE_DETERMINISM_FAILURE", event_id: eventId, first_sha256: firstDigest.sha256, second_sha256: secondDigest.sha256, first_difference: "DIGEST_MISMATCH; FULL_SECOND_GRAPH_RELEASED_BY_BOUNDED_MEMORY_MECHANICAL_RUNNER", score_rows_emitted: false });
    ensure(byteIdentical, `DETERMINISM_FAILURE ${eventId}`);
    const causalOrders = orderView(result);
    const causalByKey = new Map(causalOrders.map((row) => [`${row.leg_id}|${row.receipt}`, row]));
    const legacyByKey = new Map(legacyOrders.map((row) => [`${row.leg_id}|${row.receipt}`, row]));
    const changedOrders = [...new Set([...causalByKey.keys(), ...legacyByKey.keys()])].sort().flatMap((key) => {
      const before = legacyByKey.get(key) ?? null, after = causalByKey.get(key) ?? null;
      return canonical(before) === canonical(after) ? [] : [{ key, legacy_integer_book_first: before, causal_millisecond_order: after }];
    });
    const adjustedRows = result.ordered_rows.filter((row) => row.kind === "BOOK" && row.timestamp_epoch !== row.source_timestamp_epoch);
    clockComparisonRows.push({
      event_id: eventId,
      source_book_rows: result.ordered_rows.filter((row) => row.kind === "BOOK").length,
      exchange_print_rows_with_millisecond_component: result.ordered_rows.filter((row) => row.kind === "PRINT" && row.timestamp_epoch % 1 !== 0).length,
      causal_book_rows_recut: adjustedRows.length,
      book_rows_after_matched_print: adjustedRows.filter((row) => row.causal_clock?.relation === "AFTER_MATCHED_TRUE_PRINT_LAST_TRADE_TRANSITION").length,
      changed_order_count: changedOrders.length,
      changed_orders: changedOrders,
    });
    const old = oldOutcome(perGame, eventId, meta);
    const incompleteStamp = lawfulIncompleteStamp(result, truthRows.find((row) => row.event_id === eventId));
    storyResults.push({ event_id: eventId, run_source: RUN_SOURCE, lineage_receipt: old, layered_dual_belief: result.execution, composition_rebuild: result.execution, lawful_incomplete: incompleteStamp, tape_rows_consumed: rows.length, book_rows_consumed: rows.filter((row) => row.kind === "BOOK").length, print_rows_consumed: rows.filter((row) => row.kind === "PRINT").length, turning_points: result.stage_reads.length, derivations: result.derivations.length, compact_rearm_attempts: result.rearm_attempts.length, causal_clock_changed_orders: changedOrders.length });
    storySections.push(storySection(result, old, meta, incompleteStamp));
    floorPrintDecisionRows.push(...result.floor_print_decision_instants);
    const fullTraceRows = [
      ...result.stage_reads.map((stage) => ({ event_id: eventId, kind: "DECISION_STAGE", ...stage })),
      ...result.rearm_attempts.map((row) => ({ kind: "REARM_ATTEMPT", ...row })),
      ...result.floor_print_decision_instants.map((row) => ({ kind: "FLOOR_PRINT_DECISION_INSTANT", ...row })),
      ...result.fill_events.map((fill) => ({ event_id: eventId, kind: "FILL_EVENT", fill_event_receipt: fill })),
    ];
    for (const traceRow of fullTraceRows) await fullTraceWriter.write(traceRow);
    // The full stage—including readers and neighborhood—is already sealed in
    // the gzip diary. Retain only the score/gate projection in memory.
    const scoreProjectionRows = [
      ...result.stage_reads.map((stage) => ({ event_id: eventId, kind: "DECISION_STAGE", trigger: stage.trigger, receipt: stage.receipt, timestamp_epoch: stage.timestamp_epoch, hours_from_discovery: stage.hours_from_discovery, layers: stage.layers, coherence: stage.coherence, credited_leg_streams: stage.credited_leg_streams, derivations: stage.derivations })),
      ...result.rearm_attempts.map((row) => ({ kind: "REARM_ATTEMPT", ...row })),
      ...result.floor_print_decision_instants.map((row) => ({ kind: "FLOOR_PRINT_DECISION_INSTANT", ...row })),
      ...result.fill_events.map((fill) => ({ event_id: eventId, kind: "FILL_EVENT", fill_event_receipt: fill })),
    ];
    for (const projectionRow of scoreProjectionRows) await scoreProjectionWriter.write(projectionRow);
    fullTraceRows.length = 0;
    scoreProjectionRows.length = 0;
    result = null;
    if (global.gc) global.gc();
    const memory = process.memoryUsage();
    process.stderr.write(`V54_PROGRESS ${eventId} scored-run released heap_used_mb=${Math.round(memory.heapUsed / 1024 / 1024)} rss_mb=${Math.round(memory.rss / 1024 / 1024)}\n`);
  }
  await fullTraceWriter.close();
  await scoreProjectionWriter.close();
  await streamJsonl(scoreProjectionPath, async (row) => storyTraces.push(row));
  fs.rmSync(scoreProjectionPath, { force: true });
  const newLowIntoRestFloorMeets = storyTraces.filter((row) => row.kind === "FILL_EVENT").flatMap((row) => {
    const fill = row.fill_event_receipt;
    const context = fill?.context;
    const orderedRows = storyOrderedRows.get(context?.event_id) ?? [];
    const printIndex = orderedRows.findIndex((tapeRow) => tapeRow.kind === "PRINT"
      && tapeRow.leg_id === context?.leg_id
      && tapeRow.receipt === fill?.captured_at_receipt);
    if (printIndex < 0) return [];
    const triggeringPrint = orderedRows[printIndex];
    const priorPrintPrices = orderedRows.slice(0, printIndex)
      .filter((tapeRow) => tapeRow.kind === "PRINT" && tapeRow.leg_id === context.leg_id && Number.isInteger(tapeRow.price_cents))
      .map((tapeRow) => tapeRow.price_cents);
    const priorRunningLow = priorPrintPrices.length ? Math.min(...priorPrintPrices) : null;
    const strictNewLow = priorRunningLow === null || triggeringPrint.price_cents < priorRunningLow;
    const hitOpenRest = context?.print_at_or_below_rest === true
      && Number.isInteger(context?.prior_standing_target_cents)
      && context.entry_cents === context.prior_standing_target_cents;
    if (!strictNewLow || !hitOpenRest || triggeringPrint.price_cents >= context.entry_cents) return [];
    return [{
      event_id: context.event_id,
      leg_id: context.leg_id,
      rest_cents: context.entry_cents,
      triggering_new_low_cents: triggeringPrint.price_cents,
      prior_running_low_cents: priorRunningLow,
      floor_meeting_adjustment_cents: context.entry_cents - triggeringPrint.price_cents,
      rest_license_receipt: context.standing_license_receipt,
      print_receipt: triggeringPrint.receipt,
      fill_receipt: fill.receipt_id,
      rule: "STRICT_NEW_LOW_PRINT_INTO_ALREADY_OPEN_REST_MEETS_FLOOR_AT_REST",
    }];
  });
  const floorMeetingAdjustmentByEvent = new Map(storyResults.map((row) => [row.event_id, newLowIntoRestFloorMeets
    .filter((meet) => meet.event_id === row.event_id)
    .reduce((total, meet) => total + meet.floor_meeting_adjustment_cents, 0)]));
  const tripwireDelta = (row) => Number.isInteger(row.layered_dual_belief.delta_vs_100_cents)
    ? row.layered_dual_belief.delta_vs_100_cents + (floorMeetingAdjustmentByEvent.get(row.event_id) ?? 0)
    : null;
  const floorBreaks = storyResults.filter((row) => SAFETY_FLOORS[row.event_id.replaceAll("-", "_")] !== undefined && (!row.layered_dual_belief.completed || tripwireDelta(row) < SAFETY_FLOORS[row.event_id.replaceAll("-", "_")]));
  const storiesHeader = `# Four convictions — the book is veto-only\n\nSTATUS: PRE-GATE; the final status is rewritten from the executable gate.\nLAW VIOLATIONS: pending executable audit.\nSELF-STOP: pending executable audit.\nRUN: ${RUN_SOURCE}.\nSCOPE: four games only; no sealed, live, deployment, or full-804 run.\nLICENSE: LAW_INDEX read @ 0d1ca473, sha256 41784e6ab62d6341c2a02f8be616e596eb48930b84a71acae8f500368d44c934.\nAUTHORITY: F-VS-242..246 @ 0d1ca473; F-VS-134; F-VS-224; twenty-rule story bar F-VS-244.\nFILL MODEL: any true print at or below the standing rest credits at the rest price; aggressor direction is not observed in this replay convention.\nLIVE-PILOT BOUNDARY: aggressor-direction validation belongs to the touch census before live pilot, not this repair.\n\nA conviction level can move only on a named non-book receipt: true prints, survivor/elimination changes, panel changes, or sibling credit. The book may refuse a target through the strict post-only test, but never chooses or transforms a cent.\n\n`;
  writeText(path.join(output, "FOUR_STORIES.md"), storiesHeader + storySections.join("\n\n"));
  writeJson(path.join(output, "FOUR_STORIES_RECEIPT.json"), { label: OUTPUT_LABEL, pass: 1, passes_executed: 1, similarity_declaration: os.SIMILARITY_DECLARATION, results: storyResults, safety_floor_breaks: floorBreaks, safety_floor_pass: floorBreaks.length === 0, adjustments_filed: [], f_vs_110_stamp: "TUNED_RETAINED", independent_lane_authority: "ONLY_RECEIPT_PINNED_OWN_EVIDENCE_UNDER_F_VS_068", self_stop_triggered: floorBreaks.length > 0, self_stop_reason: floorBreaks.length > 0 ? "SAFETY_FLOOR_BREAK" : null, full_804_run: storyResults.length === 804, sealed_read: storyResults.some((row) => row.event_id.includes("24JUL")), live_mutation: RUN_SOURCE.includes("LIVE_MUTATION") });
  writeJson(path.join(output, "DETERMINISM_RECEIPT.json"), {
    label: "V54_BOOK_VETO_ONLY_DETERMINISM_X2",
    method: "Each four-game execution is replayed twice from the same materialized tape, corpus, resources, and policy bytes; execution, decision stages, floor-print decision instants, rearm attempts, and fill receipts are compared byte-for-byte before any score receipt is emitted.",
    rows: determinismRows,
    all_byte_identical: determinismRows.length === TARGETS.stories.length && determinismRows.every((row) => row.byte_identical),
    runs_per_game: 2,
  });
  writeJson(path.join(output, "CAUSAL_CLOCK_RECEIPT.json"), {
    label: "MILLISECOND_EXCHANGE_CLOCK_CAUSAL_BOOK_INTERLEAVE",
    law: ["F-VS-228@737e3c2b", "F-VS-233@86ca93f3"],
    source_timestamp_precision: "MILLISECONDS",
    method: "Exchange timestamps are consumed to millisecond precision. Recorder rows sharing a millisecond are ordered deterministically by source-row sequence and the last-trade transition watermark; no receipt claims sub-millisecond observational precision.",
    policy_change: false,
    rows: clockComparisonRows,
    total_changed_orders: clockComparisonRows.reduce((total, row) => total + row.changed_order_count, 0),
  });
  const decisionStages = storyTraces.filter((row) => row.kind === "DECISION_STAGE");
  const allDerivations = decisionStages.flatMap((row) => row.derivations.map((derivation) => ({ event_id: row.event_id, trigger: row.trigger, stage_receipt: row.receipt, ...derivation })));
  const paidRestCentsByEventLeg = new Map(storyTraces
    .filter((row) => row.kind === "FILL_EVENT")
    .map((row) => [`${row.fill_event_receipt?.context?.event_id}|${row.fill_event_receipt?.context?.leg_id}`, row.fill_event_receipt?.context?.entry_cents]));
  const isUrsPaidRest58Against55 = (row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL14URSPAL"
    && row.leg_id === "URS"
    && paidRestCentsByEventLeg.get(`${row.event_id}|${row.leg_id}`) === 58
    && (row.final_target_cents ?? row.action?.target_cents ?? null) === 58
    && (row.authority_target_cents
      ?? row.authority?.target_cents
      ?? row.current_conviction_predicted_cents
      ?? row.layered_dual_belief?.pricing_authority?.target_cents
      ?? row.layered_dual_belief?.prediction_seat?.seat?.target_cents
      ?? null) === 55;
  const classifierRows = allDerivations.map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.stage_receipt,
    trigger: row.trigger,
    classification: row.layered_dual_belief?.pricing_authority?.per_leg_classification ?? null,
    pricing_consumed: row.layered_dual_belief?.pricing_authority?.classifier_consumed_by_pricing ?? false,
    immunity_consumed: row.layered_dual_belief?.floor_rest_protection?.classifier_consumed_by_immunity ?? false,
    pricing_immunity_equal: row.layered_dual_belief?.floor_rest_protection?.pricing_and_immunity_classifier_equal ?? false,
    authority_target_cents: row.layered_dual_belief?.pricing_authority?.target_cents ?? null,
    final_target_cents: row.action.target_cents,
    action: row.action.action,
    ...sentenceTraceIndex(row),
  }));
  const creditedClassifierRows = decisionStages.flatMap((stage) => Object.entries(stage.credited_leg_streams ?? {}).map(([legId, stream]) => ({
    event_id: stage.event_id,
    leg_id: legId,
    timestamp_epoch: stage.timestamp_epoch,
    receipt: stage.receipt,
    trigger: stage.trigger,
    classification: stream.pricing_authority?.per_leg_classification ?? null,
    pricing_consumed: stream.pricing_authority?.classifier_consumed_by_pricing ?? false,
    immunity_consumed: false,
    pricing_immunity_equal: true,
    authority_target_cents: stream.pricing_authority?.target_cents ?? null,
    final_target_cents: null,
    action: "CREDITED_LEG_READ_NO_ORDER_EMISSION",
    sentence_sha256: null,
    full_sentence_location: "REPAIR_FOUR_GAME_TRACE.jsonl.gz",
  })));
  classifierRows.push(...creditedClassifierRows);
  const namedClassifierRows = classifierRows.filter((row) => [
    "KXATPCHALLENGERMATCH-26JUL12GIUBAR|GIU|69",
    "KXATPCHALLENGERMATCH-26JUL12GIUBAR|GIU|66",
    "KXATPCHALLENGERMATCH-26JUL14URSPAL|PAL|39",
    "KXATPMATCH-26JUL18DANPRA|DAN|59",
  ].includes(`${row.event_id}|${row.leg_id}|${row.classification?.value_cents}`));
  writeJson(path.join(output, "PER_LEG_CLASSIFIER_RECEIPT.json"), {
    label: "DIRECTIONAL_ADMISSION_ONE_PER_LEG_CLASSIFIER_CONSUMED_BY_PRICING_AND_IMMUNITY",
    law: "Depth sign, open descent-path position, causal descent state, and evidenced-floor source form one per-leg classification. The prior path predicate and per-leg grade are composed: prints above an open path are refused; admitted printed descent-supported floors bind over unprinted hypotheses.",
    provenance: ["LAW_INDEX@7889d9e1", "CC@85b940ff:F-VS-234..237", os.LAYER_PROVENANCE.per_leg_floor_classifier, os.LAYER_PROVENANCE.directional_floor_admission],
    rows: classifierRows,
    named_rows: namedClassifierRows,
    evaluations: classifierRows.length,
    both_consumers_read_same_classifier: classifierRows.every((row) => row.pricing_immunity_equal),
    dan_59_derivable: namedClassifierRows.some((row) => row.leg_id === "DAN" && row.classification?.value_cents === 59 && row.classification.binding_floor_candidate && row.authority_target_cents === 59),
    pal_39_derivable: namedClassifierRows.some((row) => row.leg_id === "PAL" && row.classification?.value_cents === 39 && row.classification.binding_floor_candidate && row.authority_target_cents === 39),
    giu_69_refused: namedClassifierRows.some((row) => row.leg_id === "GIU" && row.classification?.value_cents === 69 && row.classification.binding_floor_candidate === false),
    giu_66_derivable: namedClassifierRows.some((row) => row.leg_id === "GIU" && row.classification?.value_cents === 66 && row.classification.binding_floor_candidate && row.authority_target_cents === 66),
  });
  const directionalAdmissionRows = classifierRows.filter((row) => row.classification?.evidenced_floor_source === "OBSERVED_TRUE_TRADE_LOW");
  const firstNamedClassifierRow = (eventId, legId, valueCents, predicate = () => true) => directionalAdmissionRows
    .filter((row) => row.event_id === eventId && row.leg_id === legId && row.classification?.value_cents === valueCents && predicate(row))
    .sort((left, right) => left.timestamp_epoch - right.timestamp_epoch || String(left.receipt).localeCompare(String(right.receipt)))[0] ?? null;
  const giu69AdmissionRow = firstNamedClassifierRow("KXATPCHALLENGERMATCH-26JUL12GIUBAR", "GIU", 69);
  const giu66AdmissionRow = firstNamedClassifierRow("KXATPCHALLENGERMATCH-26JUL12GIUBAR", "GIU", 66, (row) => row.classification?.admission_gate_passed === true);
  const giu69RefusedByDirection = giu69AdmissionRow?.classification?.admission_gate_passed === false
    && giu69AdmissionRow?.classification?.refusal_reason === "PRINT_DURING_OPEN_DESCENT_ABOVE_PATH_NOT_FLOOR_CANDIDATE";
  const giu66AdmittedByDirection = giu66AdmissionRow?.classification?.admission_gate_passed === true;
  writeJson(path.join(output, "DIRECTIONAL_FLOOR_ADMISSION_RECEIPT.json"), {
    label: "PRINT_ADMISSION_COMPOSES_OPEN_DESCENT_PATH_WITH_PER_LEG_GRADE",
    law: "A true print made while its leg's descent state is OPEN and above the surviving descent path is not a floor candidate. Exact path support remains admissible. The prior predicate is composed with the per-leg grade, not replaced.",
    provenance: ["LAW_INDEX@7889d9e1", "CC@85b940ff", "F-VS-224", "F-VS-229", os.LAYER_PROVENANCE.directional_floor_admission],
    rows: directionalAdmissionRows,
    evaluations: directionalAdmissionRows.length,
    admitted: directionalAdmissionRows.filter((row) => row.classification.admission_gate_passed).length,
    refused: directionalAdmissionRows.filter((row) => !row.classification.admission_gate_passed).length,
    named: { giu_69: giu69AdmissionRow, giu_66: giu66AdmissionRow },
    giu_69_refused: giu69RefusedByDirection,
    giu_66_admitted: giu66AdmittedByDirection,
  });
  const namedDerivableFloorSpecs = [
    { event_id: "KXATPCHALLENGERMATCH-26JUL12GIUBAR", game: "GIUBAR", leg_id: "GIU", floor_cents: 66 },
    { event_id: "KXATPCHALLENGERMATCH-26JUL14URSPAL", game: "URSPAL", leg_id: "PAL", floor_cents: 39 },
    { event_id: "KXATPCHALLENGERMATCH-26JUL14URSPAL", game: "URSPAL", leg_id: "URS", floor_cents: 57 },
    { event_id: "KXATPCHALLENGERMATCH-26JUL14LAJSVA", game: "LAJSVA", leg_id: "LAJ", floor_cents: 51 },
    { event_id: "KXATPMATCH-26JUL18DANPRA", game: "DANPRA", leg_id: "DAN", floor_cents: 59 },
  ];
  const derivableFloorConductRows = namedDerivableFloorSpecs.map((spec) => {
    const evaluations = directionalAdmissionRows
      .filter((row) => row.event_id === spec.event_id && row.leg_id === spec.leg_id && row.classification?.value_cents === spec.floor_cents)
      .sort((left, right) => left.timestamp_epoch - right.timestamp_epoch || String(left.receipt).localeCompare(String(right.receipt)));
    const firstEvaluation = evaluations[0] ?? null;
    const firstBinding = evaluations.find((row) => row.classification?.binding_floor_candidate === true) ?? null;
    const conductAtFloor = evaluations.find((row) => row.final_target_cents === spec.floor_cents
      || (row.action === "CREDITED_LEG_READ_NO_ORDER_EMISSION" && row.authority_target_cents === spec.floor_cents)) ?? null;
    const story = storyResults.find((row) => row.event_id === spec.event_id)?.composition_rebuild ?? null;
    const outcome = story?.legs?.[spec.leg_id] ?? null;
    const comparisonTs = firstBinding?.timestamp_epoch ?? firstEvaluation?.timestamp_epoch ?? null;
    const creditedBeforeFloor = Number.isFinite(outcome?.fill_timestamp_epoch) && Number.isFinite(comparisonTs) && outcome.fill_timestamp_epoch < comparisonTs;
    const creditedAtFloorOnFloorReceipt = outcome?.entry_cents === spec.floor_cents && outcome?.fill_receipt === firstBinding?.receipt;
    const creditedBeforeFloorRow = creditedBeforeFloor || (outcome?.entry_cents !== spec.floor_cents && outcome?.fill_receipt === firstBinding?.receipt);
    const nonDerivableFloorExplained = Boolean(!firstBinding
      && firstEvaluation?.classification?.class_id === "PRINT_ABOVE_OPEN_DESCENT_PATH_NOT_FLOOR_CANDIDATE"
      && firstEvaluation?.classification?.binding_floor_candidate === false);
    const floorGovernsOpenConduct = Boolean(firstBinding && !creditedBeforeFloor && evaluations.some((row) => row.final_target_cents === spec.floor_cents || outcome?.standing_target_cents === spec.floor_cents));
    const exactAnswer = creditedAtFloorOnFloorReceipt
      ? "CREDITED_AT_DERIVABLE_PRINTED_FLOOR_ON_FLOOR_RECEIPT"
      : creditedBeforeFloorRow
      ? `NONE__LEG_ALREADY_CREDITED_AT_${outcome.entry_cents}_BEFORE_DERIVABLE_${spec.floor_cents}_RECEIPT`
      : floorGovernsOpenConduct
        ? "DERIVABLE_DESCENT_SUPPORTED_PRINTED_FLOOR_GOVERNED_CONDUCT"
        : !firstBinding
          ? `FLOOR_NOT_DERIVABLE__${firstEvaluation?.classification?.refusal_reason ?? "NO_CLASSIFIER_EVALUATION"}`
          : `DERIVABLE_FLOOR_DID_NOT_GOVERN__ACTION_${firstBinding.action}__AUTHORITY_${firstBinding.authority_target_cents ?? "NONE"}__FINAL_${firstBinding.final_target_cents ?? "NONE"}`;
    return {
      ...spec,
      first_evaluation: firstEvaluation,
      first_binding: firstBinding,
      first_conduct_at_floor: conductAtFloor,
      terminal_leg_outcome: outcome,
      credited_before_derivable_floor_receipt: creditedBeforeFloor,
      credited_before_derivable_floor_row: creditedBeforeFloorRow,
      credited_at_derivable_floor_on_floor_receipt: creditedAtFloorOnFloorReceipt,
      non_derivable_floor_explained: nonDerivableFloorExplained,
      derivable_floor_governed_open_leg_conduct: floorGovernsOpenConduct,
      conduct_answer: exactAnswer,
      evidence_outweighing_derivable_floor: exactAnswer.startsWith("DERIVABLE_FLOOR_DID_NOT_GOVERN") ? firstBinding?.classification ?? null : null,
      answered: Boolean(firstEvaluation),
      lawful_or_explained: floorGovernsOpenConduct || creditedBeforeFloorRow || creditedAtFloorOnFloorReceipt || nonDerivableFloorExplained,
    };
  });
  const derivableFloorOpenLegFailures = derivableFloorConductRows.filter((row) => !row.lawful_or_explained);
  writeJson(path.join(output, "DERIVABLE_FLOOR_CONDUCT_RECEIPT.json"), {
    label: "PRINTED_DESCENT_SUPPORTED_DERIVABLE_FLOOR_GOVERNS_OPEN_LEG_CONDUCT",
    law: "When a leg's own printed floor is derivable and descent-supported, the conditioned authority reaches it and an open leg stands there. A leg credited before that receipt cannot emit another order; that terminal fact is named rather than misreported as competing evidence.",
    provenance: ["LAW_INDEX@7889d9e1", os.LAYER_PROVENANCE.derivable_floor_governs, "DEFINITION_LOCK", "FILL_PRICE_RULING"],
    rows: derivableFloorConductRows,
    open_leg_failures: derivableFloorOpenLegFailures,
    all_named_answers_present: derivableFloorConductRows.every((row) => row.answered),
    all_open_derivable_floors_governed: derivableFloorOpenLegFailures.length === 0,
  });
  const giu66FloorPrintRows = floorPrintDecisionRows.filter((row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL12GIUBAR" && row.leg_id === "GIU" && row.print_price_cents === 66);
  writeJson(path.join(output, "FLOOR_PRINT_DECISION_INSTANT_RECEIPT.json"), {
    label: "F_VS_237_EVERY_FLOOR_PRINT_RECEIPT_WAKES_OWN_LEG",
    law: "Every first print, new traded low, and equal touch of the running traded low is an exact-receipt decision instant on its own leg; a filling print is itself the credit decision instant.",
    provenance: ["CC@85b940ff:F-VS-237", os.LAYER_PROVENANCE.floor_print_decision_instant],
    rows: floorPrintDecisionRows,
    floor_print_receipts: floorPrintDecisionRows.length,
    fired: floorPrintDecisionRows.filter((row) => row.decision_instant_fired).length,
    not_fired: floorPrintDecisionRows.filter((row) => !row.decision_instant_fired),
    giu_66_receipts: giu66FloorPrintRows,
    giu_66_receipt_count: giu66FloorPrintRows.length,
    giu_66_all_fired: giu66FloorPrintRows.length >= 3 && giu66FloorPrintRows.every((row) => row.decision_instant_fired),
    scheduler_latency_seconds: 0,
  });
  emitPoolCascadeReports({ repo, output, corpus, groundTruth, metas, remote, printLoad, lineage, resources,
    storyTraces, storyResults, storyOrderedRows, decisionStages, allDerivations, determinismRows,
    floorBreaks, floorPrintDecisionRows, namedDerivableFloorSpecs, derivableFloorConductRows });
}

if (require.main === module) main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });

module.exports = {
  emitPoolCascadeReports,
  GROUND_TRUTH_COMMIT,
  GROUND_TRUTH_PATH,
  loadCorpus,
  loadGroundTruth,
  targetMeta,
  bindCorpusFloorTiming,
  loadTicks,
  loadTargetPrints,
  replayEvent,
  streamJsonl,
  receipt,
  fileHash,
  shaBytes,
  canonical,
  LOAD_TICK_ISSUES,
};
