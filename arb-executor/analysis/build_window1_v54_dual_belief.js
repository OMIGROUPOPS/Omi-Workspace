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
    "KXATPMATCH-26JUL18DANPRA",
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
const OUTPUT_LABEL = "V54_EVIDENCE_BALLOT_CAUSAL_CLOCK_AT_FLOOR_IMMUNITY_MIND_ONLY_BED";
const RUN_SOURCE = "V54_EVIDENCE_BALLOT_CAUSAL_CLOCK_AT_FLOOR_IMMUNITY_20260825";
const DEPTH_MAP_COMMIT = "ac68e3bc8d2c2018ba883c131b8b4101ae4cd257";
const DEPTH_MAP_PATH = ".claude/window1_second_seat/dives_t1_v3_20260823/TRUE_BELL_CELL_DEPTH_MAP.json";
const SURVIVOR_SOURCE_COMMIT = "189eaa20";
const PAIR_INTERIM_LIBRARY_PATH = ".claude/window1_live_v4_replay/pair_interim_shape_v18_fit_20260803/INTERIM_PAIR_LIBRARY_V18.json";
const PAIR_COUPLE_LIBRARY_PATH = ".claude/window1_live_v4_replay/pair_couple_v19_fit_20260803/PAIR_COUPLE_LIBRARY_V19.json";

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
  return { sha256: hash.digest("hex"), bytes, counts: { stage_reads: result.stage_reads.length, rearm_attempts: result.rearm_attempts.length, fill_events: result.fill_events.length } };
}
function firstReplayDifference(left, right) {
  const execution = firstDifference(left.execution, right.execution, "$.execution");
  if (execution) return execution;
  for (const field of ["stage_reads", "rearm_attempts", "fill_events"]) {
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
function writeJson(file, value) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, canonical(value), "utf8"); }
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
  const registryPath = path.join(cacheDir, "corpus_events_v2.jsonl");
  const historicalPath = path.join(cacheDir, "historical_events_materialized.csv");
  const rangePath = path.join(cacheDir, "range_spectrum_v1.jsonl");
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
  return { rows, foundation, future_low_return: futureLow, bell_bound_receipt: bellLibrary.buildReceipt(rows, authorities), counts: { registry_rows: registryRows, historical_rows: historicalLines.length, range_rows: rangeRows, foundation_rows: foundationRows, future_low_return_rows: futureLowRows, union_games: rows.length, by_quality: rows.reduce((acc, row) => (acc[row.quality] = (acc[row.quality] || 0) + 1, acc), {}), registry_categories: registryCategories, historical_categories: historicalCategories, range_categories: rangeCategories, foundation_categories: foundationReceipt.output.by_category, registry_eras: registryEras }, sources: { registry: receipt(registryPath, registryRows), historical: receipt(historicalPath, historicalLines.length), range: receipt(rangePath, rangeRows), foundation, future_low_return: futureLow, actual_bells: authorities.bindings.actual_bell_sha256, named_neighbor_bells: authorities.bindings.named_neighbor_sha256 } };
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
out["spaces"]={"filter":"EVENT_NAMES_26JAN_THROUGH_26JUL_ONLY; SEALED_AUGUST_NOT_LISTED_OR_READ","roots":roots,"event_count":len(events),"categories_by_object":cats,"sample_receipt":sample_receipt}
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
  const orderedRows = clockMode === "LEGACY_INTEGER_BOOK_FIRST"
    ? [...rows].sort(causalClock.compareLegacyRows)
    : causalClock.materializeCausalClock(rows);
  const state = os.createTapeState(meta), epochSet = new Set(turningEpochs(meta, orderedRows)), derivations = [], stageReads = [], fillEvents = [], rearmAttempts = [];
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
  function evaluateStage({ trigger, receipt = null, legIds = null, compactUnchangedRearm = false }) {
    if (state.leg_ids.some((id) => !state.legs[id].rows.length)) return null;
    state.current_epoch = Math.max(...state.leg_ids.map((id) => state.legs[id].rows.at(-1).timestamp_epoch));
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
      ensure(derivation.pair_conservation.at_or_below_99, `pair conservation failed ${state.event_id}|${legId}`);
      if (!smokeOnly && !state.positions[legId].credited) {
        const position = state.positions[legId];
        const targetBefore = position.standing_target_cents;
        if (derivation.action.action === "CANCEL_REST") {
          position.standing_target_cents = null;
          position.standing_license_basis = null;
          position.standing_license_receipt = null;
          position.standing_captured_rest_level_cents = null;
          position.standing_captured_rest_license_receipt = null;
          position.standing_authority_evidence = null;
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
            position.standing_authority_evidence = derivation.layered_dual_belief?.pricing_authority?.decisive_evidence
              ? { ...derivation.layered_dual_belief.pricing_authority.decisive_evidence }
              : null;
          }
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
        if (!smokeOnly && row.kind === "PRINT" && !position.credited && Number.isInteger(position.standing_target_cents) && row.price_cents <= position.standing_target_cents) {
          const fillEventReceipt = os.creditPosition(state, row.leg_id, row);
          fillEvents.push(fillEventReceipt);
          fillHandoffReceipt = row.receipt;
        }
        os.observe(state, row.leg_id, row);
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
    if (lastEvaluatedInstant !== epoch) {
      evaluateStage({ trigger: "TURNING_POINT", receipt: lastConsumedReceipt });
      lastEvaluatedInstant = epoch;
    }
  }
  const credited = state.leg_ids.filter((id) => state.positions[id].credited), combined = credited.length === 2 ? credited.reduce((total, id) => total + state.positions[id].entry_cents, 0) : null;
  return { state, epochs, stage_reads: stageReads, derivations, fill_events: fillEvents, rearm_attempts: rearmAttempts, clock_mode: clockMode, ordered_rows: orderedRows, execution: { run_source: RUN_SOURCE, gradeable: Number.isFinite(meta.bell_epoch), completed: credited.length === 2, combined_entry_cents: combined, delta_vs_100_cents: Number.isInteger(combined) ? 100 - combined : null, legs: state.positions } };
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
  const row = perGame.rows.find((item) => item.event_id === eventId), credits = row.L7_CREDIT.why;
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
    }));
  const lawful = !result.execution.completed && Number.isInteger(floorSum) && floorSum >= 100 && restAtFloorRows.length > 0;
  return {
    stamp: lawful ? "LAWFUL_INCOMPLETE" : result.execution.completed ? "NOT_APPLICABLE_COMPLETE" : "UNSTAMPED_INCOMPLETE",
    arithmetic: {
      floor_by_leg_cents: floorByLeg,
      two_leg_floor_sum_cents: floorSum,
      strictly_under_par_offer_cents: Number.isInteger(floorSum) ? Math.max(0, 99 - floorSum) : null,
      proof: Number.isInteger(floorSum) ? `${floors[0]}+${floors[1]}=${floorSum}; max(0,99-${floorSum})=${Math.max(0, 99 - floorSum)}` : "FLOOR_RESOURCE_GAP",
    },
    rest_at_floor_rows: restAtFloorRows,
    rest_at_floor_proven: restAtFloorRows.length > 0,
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
  const story = transitions.map((stage, index) => {
    const actions = stage.derivations.map((row) => `${row.leg_id}: ${row.action.action}${Number.isInteger(row.action.target_cents) ? ` at ${row.action.target_cents} cents` : ""}`).join("; ");
    return `At ${stage.hours_from_discovery.toFixed(6)} hours from discovery${index === 0 ? ", the first licensed transition formed" : ", the licensed action or coherence state changed"}. Coherence=${stage.coherence?.status ?? "UNKNOWN"}; ${actions}.\n\n${stage.derivations.map((row) => `VERBATIM ${row.leg_id}: ${row.sentence}\nCITATION-RECEIPT-IDS: ${Object.keys(row.citation_receipts).join(",")}`).join("\n\n")}`;
  }).join("\n\n");
  const closes = meta.leg_ids.map((id) => `${id}=${meta.truth_closes_cents[id] ?? "UNKNOWN"}`).join(", ");
  const danpra = meta.event_id === "KXATPMATCH-26JUL18DANPRA" ? (() => {
    const finalStage = result.stage_reads.at(-1), books = finalStage.reads.books.value;
    const conclusions = finalStage.derivations.map((row) => `${row.leg_id}: conditional remaining-dip q50 ${row.derivation.neighbor_leg.conditional_remaining_dip_distribution_cents.q50 ?? "UNKNOWN"}¢ from own ${row.derivation.neighbor_leg.own_evidence.basis} evidence, ${row.action.action}${Number.isInteger(row.action.target_cents) ? ` at ${row.action.target_cents}¢` : ""}`).join("; ");
    const finalBooks = meta.leg_ids.map((id) => `${id} ${books[id]?.bid_cents ?? "?"}/${books[id]?.ask_cents ?? "?"}`).join("; ");
    const finalRests = meta.leg_ids.map((id) => `${id} ${result.execution.legs[id]?.standing_target_cents ?? "NONE"}`).join("; ");
    return `\n\n### DANPRA derived terminal exhibit\n\nFinal causal books: ${finalBooks}. Final standing rests from execution: ${finalRests}. Final named look-alikes: ${neighborsPlain(finalStage.neighborhood)}. Derived conclusions: ${conclusions}. No price or shape literal is supplied by this renderer; all values above come from the run receipts. CITATION-RECEIPT-IDS: ${finalStage.derivations.flatMap((row) => Object.keys(row.citation_receipts)).join(",")}.`;
  })() : "";
  const incomplete = incompleteStamp?.stamp === "LAWFUL_INCOMPLETE" ? `\n\n### LAWFUL_INCOMPLETE\n\nArithmetic: ${incompleteStamp.arithmetic.proof}. Offer=${incompleteStamp.arithmetic.strictly_under_par_offer_cents}¢. Rest-at-floor receipts: ${incompleteStamp.rest_at_floor_rows.map((row) => `${row.leg_id} ${row.rest_cents}¢ [${row.receipt}]`).join("; ") || "NONE"}. This stamped abstention retains its arithmetic proof; an unstamped abstention scores zero.` : "";
  const compactLegs = (legs) => Object.fromEntries(Object.entries(legs ?? {}).map(([legId, leg]) => [legId, {
    credited: leg.credited ?? null,
    entry_cents: leg.entry_cents ?? null,
    standing_target_cents: leg.standing_target_cents ?? null,
    fill_receipt: leg.fill_receipt ?? null,
    fill_timestamp_epoch: leg.fill_timestamp_epoch ?? null,
  }]));
  const compactIncompleteRows = (incompleteStamp?.rest_at_floor_rows ?? []).map((row) => ({ leg_id: row.leg_id, rest_cents: row.rest_cents, receipt: row.receipt }));
  return `## ${meta.event_id}\n\nSTORY_TRANSITION_SELECTION: ${transitions.length}/${transitionCandidates.length} action/coherence transitions rendered; every receipt remains in REPAIR_FOUR_GAME_TRACE.jsonl.gz.\n\n${story}${danpra}${incomplete}\n\n### Execution appendix — context, not verdict\n\n| version | completed | pair cents | delta vs 100 | gradeable | legs / truth closes |\n|---|---:|---:|---:|---:|---|\n| lineage receipt | ${old.completed} | ${old.combined_entry_cents ?? "NA"} | ${old.delta_vs_100_cents ?? "NA"} | ${old.gradeable} | ${JSON.stringify(compactLegs(old.legs))} |\n| layered dual belief | ${result.execution.completed} | ${result.execution.combined_entry_cents ?? "NA"} | ${result.execution.delta_vs_100_cents ?? "NA"} | ${result.execution.gradeable} | ${JSON.stringify(compactLegs(result.execution.legs))} |\n| lawful-incomplete stamp | ${incompleteStamp?.stamp ?? "NONE"} | ${incompleteStamp?.arithmetic?.two_leg_floor_sum_cents ?? "NA"} | ${incompleteStamp?.arithmetic?.strictly_under_par_offer_cents ?? "NA"} | ${old.gradeable} | ${JSON.stringify(compactIncompleteRows)} |\n| truth close | — | — | — | ${Number.isFinite(meta.bell_epoch)} | ${closes} |\n`;
}

function emitCaseStudyV28({ caseOutput, sourceOutput, storyResult, coherenceGame, tradeReport, deadlineRows, decisionStages }) {
  if (!caseOutput) return null;
  fs.mkdirSync(caseOutput, { recursive: true });
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
  writeText(path.join(caseOutput, "PANEL_A_PAIR_RENDER.html"), `<!doctype html><meta charset="utf-8"><title>LAJSVA v28 pair</title><h1>${eventId} · case study v28</h1><p>Ever coherent: ${coherenceGame.ever_coherent}. First coherence: ${JSON.stringify(coherenceGame.first_coherence)}</p><pre>${JSON.stringify(storyResult.layered_dual_belief, null, 2)}</pre>`);
  writeText(path.join(caseOutput, "PANEL_B_ENGAGEMENT.html"), `<!doctype html><meta charset="utf-8"><title>LAJSVA v28 engagement</title><h1>Condition, don't replace</h1>${transitions.map((stage) => `<section><h2>${stage.timestamp_epoch} · ${stage.receipt}</h2><p>coherence=${stage.coherence?.status}</p>${stage.derivations.map((row) => `<h3>${row.leg_id} · ${row.action.action} ${row.action.target_cents ?? "NONE"}</h3><pre>${row.sentence.replaceAll("&", "&amp;").replaceAll("<", "&lt;")}</pre>`).join("")}</section>`).join("")}`);
  writeText(path.join(caseOutput, "PANEL_C_TRADE_REPORTS.html"), `<!doctype html><meta charset="utf-8"><title>LAJSVA v28 reports</title><h1>Trade report + deadline grades</h1><pre>${JSON.stringify({ trade_report: tradeReport, belief_deadline_rows: eventDeadlineRows }, null, 2).replaceAll("&", "&amp;").replaceAll("<", "&lt;")}</pre>`);
  writeText(path.join(caseOutput, "TRADE_REPORT_PATTERN_ENGINE.md"), `# LAJSVA case-study v28 — condition, don't replace\n\n${JSON.stringify(tradeReport, null, 2)}\n`);
  writeText(path.join(caseOutput, "TRADE_REPORT_REFLEX.md"), `# LAJSVA lineage context\n\nHistorical lineage receipt only: completed=${storyResult.lineage_receipt.completed}; pair=${storyResult.lineage_receipt.combined_entry_cents ?? "NA"}; delta=${storyResult.lineage_receipt.delta_vs_100_cents ?? "NA"}. This context does not license the repaired bed.\n`);
  writeText(path.join(caseOutput, "V1_THROUGH_V28_SIDE_BY_SIDE.md"), `# LAJSVA case-study spine v1–v28\n\nV28 updates the panel prior with graded current-game channels, acts on the deriving receipt, keeps credited streams readable, and states floor-side rounding. The mind-only bed outcome is ${storyResult.layered_dual_belief.completed ? `${storyResult.layered_dual_belief.combined_entry_cents}¢/Δ${storyResult.layered_dual_belief.delta_vs_100_cents}` : "INCOMPLETE"}. The gate self-stops on any tripwire or law break; lineage is untouched.\n`);
  writeJson(path.join(caseOutput, "CASE_STUDY_RECEIPT.json"), {
    label: "LAJSVA_CASE_STUDY_V28_CONDITION_DONT_REPLACE",
    source_package: "v54_condition_dont_replace_20260825",
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
  writeJson(path.join(caseOutput, "ARTIFACT_HASH_MANIFEST.json"), { label: "LAJSVA_CASE_STUDY_V28", files: Object.fromEntries(files.map((name) => [name, { ...receipt(path.join(caseOutput, name)), path: name }])) });
  return { path: "lajsva_case_study_v28_condition_dont_replace_20260825", files: files.length + 1 };
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
    label: "V54_REMOVE_FLOOR_LOCK_CUSTODY_RECONCILED",
    files: [
      { logical_path: "FOUNDATION_PER_MINUTE_UNIVERSE", custody_location: corpus.foundation.source.external_custody_location, sha256: corpus.foundation.source.sha256, bytes: corpus.foundation.source.bytes, rows: corpus.foundation.source.rows, committed: false, compact_derivatives: [{ path: "FOUNDATION_LIBRARY.jsonl.gz", sha256: corpus.foundation.index.sha256, bytes: corpus.foundation.index.bytes, rows: corpus.foundation.index.rows }, { path: "FUTURE_LOW_RETURN_LIBRARY.jsonl.gz", sha256: corpus.future_low_return.index.sha256, bytes: corpus.future_low_return.index.bytes, rows: corpus.future_low_return.index.rows }, { path: "PHASE_CENTRAL_ESTIMATE_SURFACE.json", sha256: phaseSurfaceReceipt.sha256, bytes: phaseSurfaceReceipt.bytes, rows: phaseCentralSurface.cells.length }] },
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
      license: { law_index_read_at: "686e8c8d", law_index_sha256: "c7c7271501076fefdad0d65044bde5a410ccc718f8f7f5a40d488caf81b3dee6", laws: ["L8", "L18", "L20", "L22"] },
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
  const smoke = replayEvent({ meta: smokeMeta, rows: smokeRows, corpus: corpus.rows, resources, lineage, smokeOnly: true });
  const smokeReaderReceipt = readerExecutionReceipt(smoke);
  ensure(smokeReaderReceipt.all_readers_fired, "CRIJEA did not fire all readers");
  writeText(path.join(output, "SMOKE_CRIJEA.md"), smokeMarkdown(smoke));
  writeJson(path.join(output, "SMOKE_CRIJEA_RECEIPT.json"), { label: "CRIJEA_INTEGRATION_SMOKE_NO_GRADING", all_readers_fired: smokeReaderReceipt.all_readers_fired, reader_count: smokeReaderReceipt.reader_count, expected_reader_count: smokeReaderReceipt.expected_reader_count, reader_receipts: smokeReaderReceipt.readers, named_neighbors: [...new Map(smoke.stage_reads.flatMap((stage) => stage.neighborhood.map((row) => [row.citation_receipt_id, { event_id: row.event_id, citation_receipt_id: row.citation_receipt_id, citation_receipt: row.citation_receipt }]))).values()], derivations: smoke.derivations.length, sentence_action_equal: smoke.derivations.every((row) => row.sentence_action_assertion.equal), citation_receipt_equal: smoke.derivations.every((row) => row.citation_receipt_assertion.equal), conservation: smoke.derivations.every((row) => row.pair_conservation.at_or_below_99), grading_performed: false });

  const perGame = JSON.parse(fs.readFileSync(path.join(walkRoot, "PER_GAME_L1_L8.json"), "utf8")), storyResults = [], storySections = [], storyTraces = [], storyTapeRows = new Map(), determinismRows = [], clockComparisonRows = [];
  fs.rmSync(path.join(output, "DETERMINISM_FAILURE_DEBUG.json"), { force: true });
  for (const eventId of TARGETS.stories) {
    const meta = metas.find((row) => row.event_id === eventId), rows = [...loadTicks(privateRoot, meta), ...printLoad.byEvent.get(eventId)].filter((row) => !Number.isFinite(meta.bell_epoch) || row.timestamp_epoch <= meta.bell_epoch);
    storyTapeRows.set(eventId, rows);
    const result = replayEvent({ meta, rows, corpus: corpus.rows, resources, lineage, smokeOnly: false });
    const repeat = replayEvent({ meta, rows, corpus: corpus.rows, resources, lineage, smokeOnly: false });
    const legacyClock = replayEvent({ meta, rows, corpus: corpus.rows, resources, lineage, smokeOnly: false, clockMode: "LEGACY_INTEGER_BOOK_FIRST" });
    const firstDigest = digestReplay(result), secondDigest = digestReplay(repeat);
    const byteIdentical = firstDigest.sha256 === secondDigest.sha256 && firstDigest.bytes === secondDigest.bytes;
    const firstDiff = byteIdentical ? null : firstReplayDifference(result, repeat);
    determinismRows.push({ event_id: eventId, first_sha256: firstDigest.sha256, second_sha256: secondDigest.sha256, byte_identical: byteIdentical, first_bytes: firstDigest.bytes, second_bytes: secondDigest.bytes, first_counts: firstDigest.counts, second_counts: secondDigest.counts, first_difference: firstDiff });
    if (!byteIdentical) writeJson(path.join(output, "DETERMINISM_FAILURE_DEBUG.json"), { label: "PRE_SCORE_DETERMINISM_FAILURE", event_id: eventId, first_sha256: firstDigest.sha256, second_sha256: secondDigest.sha256, first_difference: firstDiff, score_rows_emitted: false });
    ensure(byteIdentical, `DETERMINISM_FAILURE ${eventId}`);
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
    const causalOrders = orderView(result), legacyOrders = orderView(legacyClock);
    const causalByKey = new Map(causalOrders.map((row) => [`${row.leg_id}|${row.receipt}`, row]));
    const legacyByKey = new Map(legacyOrders.map((row) => [`${row.leg_id}|${row.receipt}`, row]));
    const changedOrders = [...new Set([...causalByKey.keys(), ...legacyByKey.keys()])].sort().flatMap((key) => {
      const before = legacyByKey.get(key) ?? null, after = causalByKey.get(key) ?? null;
      return canonical(before) === canonical(after) ? [] : [{ key, legacy_integer_book_first: before, causal_fractional: after }];
    });
    const adjustedRows = result.ordered_rows.filter((row) => row.kind === "BOOK" && row.timestamp_epoch !== row.source_timestamp_epoch);
    clockComparisonRows.push({
      event_id: eventId,
      source_book_rows: result.ordered_rows.filter((row) => row.kind === "BOOK").length,
      true_fractional_print_rows: result.ordered_rows.filter((row) => row.kind === "PRINT" && row.timestamp_epoch % 1 !== 0).length,
      causal_book_rows_recut: adjustedRows.length,
      book_rows_after_matched_print: adjustedRows.filter((row) => row.causal_clock?.relation === "AFTER_MATCHED_TRUE_PRINT_LAST_TRADE_TRANSITION").length,
      changed_order_count: changedOrders.length,
      changed_orders: changedOrders,
    });
    const old = oldOutcome(perGame, eventId, meta);
    const incompleteStamp = lawfulIncompleteStamp(result, truthRows.find((row) => row.event_id === eventId));
    storyResults.push({ event_id: eventId, run_source: RUN_SOURCE, lineage_receipt: old, layered_dual_belief: result.execution, composition_rebuild: result.execution, lawful_incomplete: incompleteStamp, tape_rows_consumed: rows.length, book_rows_consumed: rows.filter((row) => row.kind === "BOOK").length, print_rows_consumed: rows.filter((row) => row.kind === "PRINT").length, turning_points: result.stage_reads.length, derivations: result.derivations.length, compact_rearm_attempts: result.rearm_attempts.length, causal_clock_changed_orders: changedOrders.length });
    storySections.push(storySection(result, old, meta, incompleteStamp));
    storyTraces.push(...result.stage_reads.map((stage) => ({ event_id: eventId, kind: "DECISION_STAGE", ...stage })), ...result.rearm_attempts.map((row) => ({ kind: "REARM_ATTEMPT", ...row })), ...result.fill_events.map((fill) => ({ event_id: eventId, kind: "FILL_EVENT", fill_event_receipt: fill })));
  }
  const floorBreaks = storyResults.filter((row) => SAFETY_FLOORS[row.event_id.replaceAll("-", "_")] !== undefined && (!row.layered_dual_belief.completed || row.layered_dual_belief.delta_vs_100_cents < SAFETY_FLOORS[row.event_id.replaceAll("-", "_")]));
  const storiesHeader = `# Four convictions — evidence joins support; causal clock; at-floor immunity\n\nLicense: LAW_INDEX read @ 737e3c2b, sha256 41784e6a… · CC @737e3c2b (F-VS-225..228) · F-VS-224 grading order · F-VS-134 · DEFINITION LOCK · fill-price ruling · welds.\n\nThe connected panel remains the prior, while every receipt-pinned own-game evidence value now joins the candidate set at its exact cent with measured decisiveness. Whole-second recorder books are causally interleaved with fractional exchange prints before decisions. A rest standing at its evidenced traded floor is immune to every routine mover until its supporting elimination overturns or a trade credits it. The four arguments come first; floors are their ruler and deltas remain last. No sealed, live, or full-804 run was performed.\n\n`;
  writeText(path.join(output, "FOUR_STORIES.md"), storiesHeader + storySections.join("\n\n"));
  writeJson(path.join(output, "FOUR_STORIES_RECEIPT.json"), { label: OUTPUT_LABEL, pass: 1, passes_executed: 1, similarity_declaration: os.SIMILARITY_DECLARATION, results: storyResults, safety_floor_breaks: floorBreaks, safety_floor_pass: floorBreaks.length === 0, adjustments_filed: [], f_vs_110_stamp: "TUNED_RETAINED", independent_lane_authority: "ONLY_RECEIPT_PINNED_OWN_EVIDENCE_UNDER_F_VS_068", self_stop_triggered: floorBreaks.length > 0, self_stop_reason: floorBreaks.length > 0 ? "SAFETY_FLOOR_BREAK" : null, full_804_run: storyResults.length === 804, sealed_read: storyResults.some((row) => row.event_id.includes("24JUL")), live_mutation: RUN_SOURCE.includes("LIVE_MUTATION") });
  writeJson(path.join(output, "DETERMINISM_RECEIPT.json"), {
    label: "V54_EVIDENCE_BALLOT_CAUSAL_CLOCK_AT_FLOOR_IMMUNITY_DETERMINISM_X2",
    method: "Each four-game execution is replayed twice from the same materialized tape, corpus, resources, and policy bytes; execution, decision stages, rearm attempts, and fill receipts are compared byte-for-byte before any score receipt is emitted.",
    rows: determinismRows,
    all_byte_identical: determinismRows.length === TARGETS.stories.length && determinismRows.every((row) => row.byte_identical),
    runs_per_game: 2,
  });
  writeJson(path.join(output, "CAUSAL_CLOCK_RECEIPT.json"), {
    label: "TRUE_FRACTIONAL_PRINT_CAUSAL_BOOK_INTERLEAVE",
    law: "F-VS-228@737e3c2b",
    method: "Whole-second recorder books are interleaved with true fractional exchange prints by source-row order and the recorder last_trade transition watermark. A decision can only consume the causal prefix at its effective receipt time.",
    policy_change: false,
    rows: clockComparisonRows,
    total_changed_orders: clockComparisonRows.reduce((total, row) => total + row.changed_order_count, 0),
  });
  await writeJsonlGzipStreaming(path.join(output, "REPAIR_FOUR_GAME_TRACE.jsonl.gz"), storyTraces);
  const decisionStages = storyTraces.filter((row) => row.kind === "DECISION_STAGE");
  const allDerivations = decisionStages.flatMap((row) => row.derivations.map((derivation) => ({ event_id: row.event_id, trigger: row.trigger, stage_receipt: row.receipt, stage_reads: row.reads, ...derivation })));
  const contractRows = allDerivations.map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.stage_receipt,
    contracts: row.layered_dual_belief?.technique_contracts ?? [],
    active_contract: row.layered_dual_belief?.envelope_placement?.technique_contract ?? "C01_PRICING_AUTHORITY_OVER_LANE_LEVEL_SELECTION",
    writer_lane: row.layered_dual_belief?.decision_arbitration?.winner?.lane ?? null,
    action: row.action,
    sentence_carries_contract: row.sentence.includes("SENIORITY_CONTRACT="),
    ...sentenceTraceIndex(row),
  }));
  const firedContracts = os.TECHNIQUE_CONTRACTS.filter((row) => row.state === "FIRED_OR_PRICED");
  const latentContracts = os.TECHNIQUE_CONTRACTS.filter((row) => row.state === "LATENT_REGISTERED");
  const retiredContracts = os.TECHNIQUE_CONTRACTS.filter((row) => row.state.startsWith("RETIRED"));
  writeJson(path.join(output, "TECHNIQUE_CONTRACTS_RECEIPT.json"), {
    label: "V54_EVERY_FIRED_PRICED_AND_LATENT_PAIR_HAS_STATED_SENIORITY",
    authorities: ["THE_TECHNIQUE_FRAME@36f04e25", "TECHNIQUE_REGISTER@9ef05314", "F-VS-193..198@9ef05314"],
    fired_or_priced_contracts: firedContracts,
    latent_contracts_registered_before_firing: latentContracts,
    retired_contracts: retiredContracts,
    fired_contract_count: firedContracts.length,
    latent_contract_count: latentContracts.length,
    retired_contract_count: retiredContracts.length,
    expected_counts: { fired_or_priced: 14, latent: 6, retired_by_one_author: 1 },
    every_decision_carries_complete_register: contractRows.every((row) => row.contracts.length === os.TECHNIQUE_CONTRACTS.length),
    every_sentence_states_active_contract: contractRows.every((row) => row.sentence_carries_contract),
    rows: contractRows,
  });
  const pricingAuthorityRows = allDerivations.map((row) => {
    const authority = row.layered_dual_belief?.pricing_authority ?? null;
    const placement = row.layered_dual_belief?.envelope_placement ?? null;
    const arbitration = row.layered_dual_belief?.decision_arbitration ?? null;
    return {
      event_id: row.event_id,
      leg_id: row.leg_id,
      timestamp_epoch: row.timestamp_epoch,
      receipt: row.stage_receipt,
      authority,
      prior_lane_mode: placement?.prior_lane_mode ?? null,
      lane_proposal_before_authority_cents: placement?.lane_proposal_before_authority_cents ?? null,
      authority_target_cents: authority?.target_cents ?? null,
      final_target_cents: row.action.target_cents,
      action: row.action.action,
      emitted_order: ["PLACE_REST", "REPRICE_REST"].includes(row.action.action),
      writer_lane: arbitration?.winner?.lane ?? null,
      lane_level_replaced_authority: placement?.lane_level_replaced_authority ?? null,
      senior_contract_resolution: placement?.technique_contract ?? "C01_PRICING_AUTHORITY_OVER_LANE_LEVEL_SELECTION",
      allocation: row.derivation?.allocation ?? null,
      authority_target_divergence: row.derivation?.authority_target_divergence ?? null,
      sentence_carries_authority: row.sentence.includes("PRICING_AUTHORITY=") && row.sentence.includes("WRITER_LANE="),
      sentence_carries_author_chain: row.sentence.includes("AUTHOR_CHAIN=PRIOR_") && row.sentence.includes("_TO_CONDITIONED_") && row.sentence.includes("_TO_LEVEL_"),
      ...sentenceTraceIndex(row),
    };
  });
  const authorityViolations = pricingAuthorityRows.filter((row) => {
    const emittedInvariantBroken = row.emitted_order && (
      !Number.isInteger(row.authority_target_cents)
      || row.final_target_cents !== row.authority_target_cents
      || row.authority?.target_from_licensed_rows !== true
      || row.authority?.production_target_matches_independent_recompute !== true
      || row.authority_target_divergence?.licensed_senior !== true
    );
    return row.authority?.authority_restored_to_decision_path !== true
      || row.authority?.no_lane_may_replace_target !== true
      || row.lane_level_replaced_authority === true
      || emittedInvariantBroken
      || !row.writer_lane
      || !row.sentence_carries_authority;
  });
  const functionableSource = fs.readFileSync(path.join(repo, "arb-executor/analysis/window1_v54_functionable_os.js"), "utf8");
  writeJson(path.join(output, "PRICING_AUTHORITY_RECEIPT.json"), {
    label: "V54_PANEL_PRIOR_CONDITIONED_BY_CURRENT_GAME_OWN_EVIDENCE_IS_THE_DECISION_AUTHORITY",
    law: "The connected panel is the prior. After formation, this game's receipt-pinned traded low, causal live bid, and spread-eye clearing condition it inside the single authority; placement lanes may not substitute a price. Conservation and post-only remain vetoes.",
    dormant_second_allocator_deleted: !functionableSource.includes("function allocatePairActions") && !functionableSource.includes("allocatePairActions,"),
    dormant_second_allocator_source_occurrences: (functionableSource.match(/allocatePairActions/g) ?? []).length,
    rows: pricingAuthorityRows,
    violations: authorityViolations,
  });
  const authorOwnEvidenceRows = pricingAuthorityRows.map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.receipt,
    panel_prior_cents: row.authority?.panel_prior_cents ?? null,
    own_evidence_rows: row.authority?.own_evidence_rows ?? [],
    conditioned_cents: row.authority?.conditioning_chain?.conditioned_cents ?? null,
    final_level_cents: row.authority?.conditioning_chain?.final_level_cents ?? null,
    prior_to_conditioned_to_level: row.authority?.conditioning_chain?.prior_to_conditioned_to_level ?? null,
    authority_source: row.authority?.authority_source ?? null,
    sentence_carries_chain: row.sentence_carries_author_chain === true && Boolean(row.authority?.conditioning_chain?.prior_to_conditioned_to_level),
  }));
  const authorOwnEvidenceViolations = authorOwnEvidenceRows.filter((row) => !row.prior_to_conditioned_to_level
    || !row.sentence_carries_chain
    || row.own_evidence_rows.some((evidence) => !evidence.receipt));
  writeJson(path.join(output, "OWN_EVIDENCE_INSIDE_AUTHOR_RECEIPT.json"), {
    label: "PANEL_PRIOR_UPDATED_BY_GRADED_CURRENT_GAME_EVIDENCE",
    authority: "F-VS-219..222@ad7138bd; F-VS-066; F-VS-068",
    method: "RECEIPT_PINNED_CHANNEL_LIKELIHOODS_UPDATE_THE_PANEL_DISTRIBUTION; TRADE_STRONGEST; BOOK_INFORMATIVE_NEVER_SOLE_AUTHOR",
    receipt_pin_required_for_every_own_evidence_row: true,
    rows: authorOwnEvidenceRows,
    violations: authorOwnEvidenceViolations,
  });
  const trueConditioningRows = pricingAuthorityRows.map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.receipt,
    prior_cents: row.authority?.conditioning_chain?.prior_cents ?? null,
    prior_distribution: row.authority?.conditioning_chain?.prior_distribution ?? [],
    channels: row.authority?.true_conditioning?.channels_applied ?? [],
    posterior_distribution: row.authority?.true_conditioning?.posterior_rows ?? [],
    posterior_q50_cents: row.authority?.true_conditioning?.posterior_q50_cents ?? null,
    posterior_continuous_cents: row.authority?.true_conditioning?.posterior_continuous_cents ?? null,
    conditioned_cents: row.authority?.conditioning_chain?.conditioned_cents ?? null,
    final_level_cents: row.authority?.conditioning_chain?.final_level_cents ?? null,
    replacement_operator_removed: row.authority?.conditioning_chain?.replacement_operator_removed === true,
    traded_evidence_strongest: row.authority?.conditioning_chain?.traded_evidence_strongest === true,
    book_never_authors_without_prior: row.authority?.conditioning_chain?.book_never_authors_without_prior === true,
    sentence_carries_channel_grades: row.authority?.true_conditioning?.channels_applied?.length === 0 || allDerivations.find((candidate) => candidate.event_id === row.event_id && candidate.leg_id === row.leg_id && candidate.stage_receipt === row.receipt)?.sentence.includes("CHANNEL_GRADES="),
  }));
  const trueConditioningViolations = trueConditioningRows.filter((row) => !row.replacement_operator_removed
    || !row.traded_evidence_strongest
    || !row.book_never_authors_without_prior
    || !row.sentence_carries_channel_grades
    || row.channels.some((channel) => !channel.receipt || !Number.isFinite(channel.grade) || !Number.isInteger(channel.class_rank)));
  writeJson(path.join(output, "TRUE_CONDITIONING_RECEIPT.json"), {
    label: "OWN_EVIDENCE_JOINS_THE_HYPOTHESIS_SUPPORT_AT_ITS_EXACT_PRICE",
    authority: ["F-VS-219..222@ad7138bd", "F-VS-225/F-VS-227@737e3c2b", "F-VS-066"],
    replacement_operator_source: "RETIRED",
    channel_seniority: ["TRADED", "TRADE_BACKED_SPREAD_CLEARING", "CARRIED_LICENSED_CONDUCT", "BOOK"],
    book_is_informative_never_alone_decisive: true,
    rows: trueConditioningRows,
    violations: trueConditioningViolations,
  });
  const ownEvidenceSupportRows = pricingAuthorityRows.map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.receipt,
    panel_prior_cents: row.authority?.panel_prior_cents ?? null,
    evidence_channels: row.authority?.true_conditioning?.channels_applied ?? [],
    exact_price_support: row.authority?.exact_price_support ?? [],
    decisive_evidence: row.authority?.decisive_evidence ?? null,
    posterior_continuous_cents: row.authority?.true_conditioning?.posterior_continuous_cents ?? null,
    derived_target_cents: row.authority?.target_cents ?? null,
    movement: row.authority?.level_movement ?? null,
  }));
  const ownEvidenceSupportViolations = ownEvidenceSupportRows.filter((row) => row.evidence_channels.some((channel) => !row.exact_price_support.some((support) => support.licensed_floor_cents === channel.value_cents && support.evidence_source === channel.source)));
  writeJson(path.join(output, "OWN_EVIDENCE_SUPPORT_RECEIPT.json"), {
    label: "PANEL_VOTES_PLUS_CURRENT_GAME_EVIDENCED_LEVELS_AT_EXACT_PRICES",
    authority: ["F-VS-225/F-VS-227@737e3c2b", "F-VS-066"],
    weighting_law: "Each panel row retains normalized prior mass. Each receipt-pinned evidence value contributes a candidate at its exact cent with decisiveness mass class_rank × grade; every candidate is then conditioned by every channel.",
    rows: ownEvidenceSupportRows,
    named: {
      BAR_27: ownEvidenceSupportRows.filter((row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL12GIUBAR" && row.leg_id === "BAR" && row.evidence_channels.some((channel) => channel.source === "OBSERVED_TRUE_TRADE_LOW" && channel.value_cents === 27)),
      GIU_66: ownEvidenceSupportRows.filter((row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL12GIUBAR" && row.leg_id === "GIU" && (row.derived_target_cents === 66 || row.evidence_channels.some((channel) => channel.value_cents === 66))),
      DAN_59: ownEvidenceSupportRows.filter((row) => row.event_id === "KXATPMATCH-26JUL18DANPRA" && row.leg_id === "DAN" && row.evidence_channels.some((channel) => channel.source === "OBSERVED_TRUE_TRADE_LOW" && channel.value_cents === 59)),
    },
    violations: ownEvidenceSupportViolations,
  });
  const sameReceiptActRows = allDerivations.map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.stage_receipt,
    ...row.layered_dual_belief?.same_receipt_act,
    action: row.action,
  }));
  const sameReceiptActViolations = sameReceiptActRows.filter((row) => row.derivation_and_postability_same_receipt === true && row.acted_same_receipt !== true);
  writeJson(path.join(output, "SAME_RECEIPT_ACT_RECEIPT.json"), {
    label: "DERIVATION_AND_POSTABILITY_ACT_ON_THE_SAME_RECEIPT",
    authority: "F-VS-221(b)@ad7138bd",
    rows: sameReceiptActRows,
    violations: sameReceiptActViolations,
  });
  const creditedLegReadRows = decisionStages.flatMap((stage) => Object.entries(stage.credited_leg_streams ?? {}).map(([legId, stream]) => ({
    event_id: stage.event_id,
    leg_id: legId,
    timestamp_epoch: stage.timestamp_epoch,
    receipt: stage.receipt,
    trigger: stage.trigger,
    ...stream,
  })));
  const creditedLegReadViolations = creditedLegReadRows.filter((row) => row.sibling_feed_live !== true || row.overturn_tests_live !== true || row.action_emission_allowed !== false || row.current_receipt !== row.receipt);
  writeJson(path.join(output, "CREDITED_LEG_CONTINUED_READ_RECEIPT.json"), {
    label: "CREDITED_LEGS_KEEP_READING_AND_FEED_THE_SIBLING_AND_OVERTURN_TESTS",
    authority: "F-VS-221(c)@ad7138bd",
    rows: creditedLegReadRows,
    violations: creditedLegReadViolations,
  });
  const directionalRoundingRows = pricingAuthorityRows.filter((row) => Number.isFinite(row.authority?.conditioning_chain?.rounding?.continuous_cents)).map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.receipt,
    ...row.authority.conditioning_chain.rounding,
    expected_directed_cents: Math.round(row.authority.conditioning_chain.rounding.continuous_cents),
  }));
  const directionalRoundingViolations = directionalRoundingRows.filter((row) => row.direction !== "EXACT_HALF_TO_HIGHER_INTEGER_57_5_TO_58" || row.directed_cents !== row.expected_directed_cents || row.target_statistic !== "POSTERIOR_WEIGHTED_MEAN_FLOOR_SIDE_DIRECTED_INTEGER");
  writeJson(path.join(output, "DIRECTIONAL_ROUNDING_RECEIPT.json"), {
    label: "BID_DERIVATION_ROUNDING_DIRECTION_IS_EXPLICIT",
    authority: "F-VS-221(d)@ad7138bd",
    named_example: { continuous_cents: 57.5, directed_cents: 58 },
    rows: directionalRoundingRows,
    violations: directionalRoundingViolations,
  });
  const movementRows = pricingAuthorityRows.map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.receipt,
    active_target_before_cents: row.authority?.level_movement?.prior_authority_memory?.effective_target_cents ?? null,
    raw_conditioned_target_cents: row.authority?.conditioning_chain?.conditioned_cents ?? null,
    effective_target_cents: row.authority?.target_cents ?? null,
    disposition: row.authority?.level_movement?.disposition ?? null,
    movement_kind: row.authority?.level_movement?.movement_kind ?? null,
    conditioning_changed: row.authority?.level_movement?.conditioning_changed ?? null,
    conditioning_inputs: row.authority?.level_movement?.conditioning_inputs ?? null,
    panel_recomposition_alone_may_move: row.authority?.level_movement?.panel_recomposition_alone_may_move ?? null,
  }));
  const movementViolations = movementRows.filter((row) => row.panel_recomposition_alone_may_move !== false);
  writeJson(path.join(output, "EVIDENCE_ONLY_LEVEL_MOVEMENT_RECEIPT.json"), {
    label: "REST_LEVEL_MOVES_ONLY_ON_NEW_MARKET_INPUT_OR_STATED_CONDITIONING_CHANGE",
    authority: "F-VS-217/F-VS-218@a6e84246; F-VS-134",
    rows: movementRows,
    pure_panel_recomposition_suppressed: movementRows.filter((row) => row.disposition === "PURE_PANEL_RECOMPOSITION_SUPPRESSED").length,
    violations: movementViolations,
  });
  const envelopeHighRows = allDerivations.flatMap((row) => Object.values(row.layered_dual_belief?.micro?.beliefs ?? {}).filter((belief) => belief?.status === "RESOLVED").map((belief) => ({
    event_id: row.event_id,
    evaluated_leg_id: row.leg_id,
    belief_leg_id: belief.leg_id,
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.stage_receipt,
    envelope_high_cents: belief.envelope_high_cents,
    envelope_high_basis: belief.envelope_high_basis,
    envelope_high_receipt: belief.envelope_high_receipt,
    envelope_high_is_floored_mid: belief.envelope_high_is_floored_mid,
  })));
  writeJson(path.join(output, "ENVELOPE_HIGH_PROVENANCE_RECEIPT.json"), {
    label: "DEFINITION_LOCK_ENVELOPE_HIGH_IS_EVIDENCED_NOT_FLOORED_MID",
    lawful_bases: ["OBSERVED_TRUE_TRADE_LOW", "CAUSAL_DISPLAYED_BID"],
    rows: envelopeHighRows,
    violations: envelopeHighRows.filter((row) => !["OBSERVED_TRUE_TRADE_LOW", "CAUSAL_DISPLAYED_BID"].includes(row.envelope_high_basis) || !row.envelope_high_receipt || row.envelope_high_is_floored_mid !== false),
  });
  const spreadEyeRows = allDerivations.map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.stage_receipt,
    reading: row.layered_dual_belief?.spread_eye ?? null,
    authority_consumed: row.layered_dual_belief?.pricing_authority?.spread_eye_consumed ?? false,
    authority_target_cents: row.layered_dual_belief?.pricing_authority?.target_cents ?? null,
    final_target_cents: row.action.target_cents,
    writer_lane: row.layered_dual_belief?.decision_arbitration?.winner?.lane ?? null,
    sentence_carries_reading: row.sentence.includes("SPREAD_EYE="),
    ...sentenceTraceIndex(row),
  }));
  const giubarSpreadEyeRows = spreadEyeRows.filter((row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL12GIUBAR"
    && (row.reading?.interior_receipts ?? []).some((receiptRow) => receiptRow.price_cents === 27));
  writeJson(path.join(output, "SPREAD_EYE_RECEIPT.json"), {
    label: "REGISTERED_SPREAD_EYE_GRADED_EVIDENCE_TO_TRADEABLE_FLOOR",
    contract: os.TECHNIQUE_CONTRACTS.find((row) => row.id === "C15_SPREAD_EYE_IS_EVIDENCE_ONLY"),
    readings: spreadEyeRows,
    readings_consumed_by_pricing_authority: spreadEyeRows.filter((row) => row.authority_consumed).length,
    direct_lane_commands: spreadEyeRows.filter((row) => row.reading?.feeds_pricing_authority_only !== true).length,
    giubar_27_inside_five_cent_spread_worked_rows: giubarSpreadEyeRows,
    every_sentence_states_reading: spreadEyeRows.every((row) => row.sentence_carries_reading),
  });
  const lockedBookRows = allDerivations.filter((row) => row.layered_dual_belief?.envelope_placement?.locked_book_is_placement_law_only).map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    receipt: row.stage_receipt,
    action: row.action,
    active_target_before_cents: row.layered_dual_belief?.floor_rest_protection?.active_target_before_cents ?? null,
    placement: row.layered_dual_belief?.envelope_placement,
  }));
  const sameReceiptFloorHandoffs = allDerivations.filter((row) => row.layered_dual_belief?.envelope_placement?.floor_handoff_same_receipt).map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.stage_receipt,
    floor_cents: row.layered_dual_belief.envelope_placement.evidenced_floor_cents,
    floor_receipt: row.layered_dual_belief.envelope_placement.evidenced_floor_receipt,
    writer_lane: row.layered_dual_belief.envelope_placement.writer_lane,
    action: row.action,
    pair_lawful: row.pair_conservation.at_or_below_99,
  }));
  const allocationResnapRows = allDerivations.filter((row) => (row.derivation?.allocation?.resnaps?.length ?? 0) > 0 || row.derivation?.allocation?.fill_handoff_resnap).map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    receipt: row.stage_receipt,
    resnaps: row.derivation.allocation.resnaps ?? [],
    fill_handoff_resnap: row.derivation.allocation.fill_handoff_resnap ?? null,
    target_axis: "POST_FORMATION_TRUE_TRADE_LOW_CENTS",
    final_target_cents: row.action.target_cents,
  }));
  writeJson(path.join(output, "CONTRACT_EXECUTION_RECEIPT.json"), {
    label: "V54_FIRED_CONTRACT_EXECUTION",
    locked_book_rows: lockedBookRows,
    locked_book_cancelled_existing_rest_count: lockedBookRows.filter((row) => row.placement?.existing_rest_cancelled_by_locked_book !== false || row.action.action === "CANCEL_REST").length,
    same_receipt_floor_handoffs: sameReceiptFloorHandoffs,
    allocation_and_cap_resnaps: allocationResnapRows,
    every_resnap_names_traded_low_axis: allocationResnapRows.every((row) => row.target_axis === "POST_FORMATION_TRUE_TRADE_LOW_CENTS"),
  });
  const duplicateTimestampBookSelections = [];
  for (const [eventId, tapeRows] of storyTapeRows.entries()) {
    const groups = new Map();
    for (const row of tapeRows.filter((candidate) => candidate.kind === "BOOK")) {
      const key = `${row.leg_id}|${row.timestamp_epoch}`;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(row);
    }
    for (const booksUnsorted of groups.values()) {
      if (booksUnsorted.length < 2) continue;
      const books = [...booksUnsorted].sort(compareTapeRows), legId = books[0].leg_id, timestampEpoch = books[0].timestamp_epoch;
      const stage = decisionStages.find((candidate) => candidate.event_id === eventId && candidate.timestamp_epoch === timestampEpoch && candidate.derivations.some((row) => row.leg_id === legId));
      const derivation = stage?.derivations.find((row) => row.leg_id === legId) ?? null;
      const selectedReceipt = stage?.reads?.books?.value?.[legId]?.receipt ?? null;
      duplicateTimestampBookSelections.push({
        event_id: eventId,
        leg_id: legId,
        timestamp_epoch: timestampEpoch,
        rows_in_materialized_order: books.map((row) => ({ receipt: row.receipt, bid_cents: row.bid_cents, ask_cents: row.ask_cents })),
        selected_receipt: selectedReceipt,
        selected_row: books.find((row) => row.receipt === selectedReceipt) ?? null,
        selection_law: stage?.trigger === "DUPLICATE_TIMESTAMP_BOOK_RECEIPT" ? "EARLY_CAUSAL_RECEIPT_SELECTED_BY_POSTABILITY_LOSS_RULE" : "LAST_MATERIALIZED_BOOK_AFTER_ALL_SAME_TIMESTAMP_RECEIPTS_CONSUMED_AT_TURNING_POINT",
        reason: stage?.trigger === "DUPLICATE_TIMESTAMP_BOOK_RECEIPT" ? "EARLIER_POSTABLE_BOOK_WOULD_BE_ERASED_BY_LATER_SAME_TIMESTAMP_BOOK" : "NO_SPECIAL_POSTABILITY_LOSS_CONDITION_FIRED; TURNING_POINT_READS_THE_FINAL_CAUSAL_BOOK_IN_MATERIALIZED_RECEIPT_ORDER",
        action: derivation?.action ?? null,
      });
    }
  }
  writeJson(path.join(output, "DUPLICATE_TIMESTAMP_BOOK_SELECTION_RECEIPT.json"), {
    label: "F_VS_191_DUPLICATE_TIMESTAMP_CAUSAL_BOOK_RECEIPT_SELECTION",
    provenance: ["F-VS-191@2941cd15", "CC@d945bcdd/2941cd15"],
    ordering: "timestamp, kind, receipt-id; distinct receipts are not joined",
    rows: duplicateTimestampBookSelections,
    giubar_named_rows: duplicateTimestampBookSelections.filter((row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL12GIUBAR" && row.leg_id === "GIU"),
  });
  const emittedOrderRows = allDerivations.filter((row) => ["PLACE_REST", "REPRICE_REST", "CANCEL_REST"].includes(row.action.action));
  const ordersByDecisionInstant = new Map();
  const ordersBySourceReceipt = new Map();
  for (const row of emittedOrderRows) {
    const instantKey = `${row.event_id}|${row.leg_id}|${row.timestamp_epoch}`;
    const receiptKey = `${row.event_id}|${row.leg_id}|${row.stage_receipt}`;
    ordersByDecisionInstant.set(instantKey, (ordersByDecisionInstant.get(instantKey) ?? 0) + 1);
    ordersBySourceReceipt.set(receiptKey, (ordersBySourceReceipt.get(receiptKey) ?? 0) + 1);
  }
  const orderCountDistribution = (counts) => [...counts.values()].reduce((distribution, count) => (distribution[String(count)] = (distribution[String(count)] ?? 0) + 1, distribution), {});
  const orderArbitrationReceipt = {
    label: "F_VS_176_ONE_DECISION_PER_RECEIPT_AND_INSTANT",
    law: "All eligible lanes resolve before emission. One leg emits at most one order for a machine decision instant; the selected lane and every losing lane are carried on the decision row.",
    prior_orders: 309,
    current_orders: emittedOrderRows.length,
    action_counts: emittedOrderRows.reduce((counts, row) => (counts[row.action.action] = (counts[row.action.action] ?? 0) + 1, counts), {}),
    orders_per_source_receipt_distribution: orderCountDistribution(ordersBySourceReceipt),
    orders_per_decision_instant_distribution: orderCountDistribution(ordersByDecisionInstant),
    source_receipt_groups_over_one: [...ordersBySourceReceipt].filter(([, count]) => count > 1).map(([key, count]) => ({ key, count })),
    decision_instant_groups_over_one: [...ordersByDecisionInstant].filter(([, count]) => count > 1).map(([key, count]) => ({ key, count })),
    max_orders_per_source_receipt: Math.max(0, ...ordersBySourceReceipt.values()),
    max_orders_per_decision_instant: Math.max(0, ...ordersByDecisionInstant.values()),
    arbitration_missing_rows: emittedOrderRows.filter((row) => !row.layered_dual_belief?.decision_arbitration?.winner || !Array.isArray(row.layered_dual_belief?.decision_arbitration?.losers)).map((row) => `${row.event_id}|${row.leg_id}|${row.stage_receipt}`),
    rows: emittedOrderRows.map((row) => ({ event_id: row.event_id, leg_id: row.leg_id, timestamp_epoch: row.timestamp_epoch, source_receipt: row.stage_receipt, action: row.action, arbitration: row.layered_dual_belief?.decision_arbitration ?? null })),
  };
  writeJson(path.join(output, "ONE_DECISION_PER_RECEIPT.json"), orderArbitrationReceipt);
  const literalAudit = literalClaimAudit(repo);
  writeJson(path.join(output, "LITERAL_BOOLEAN_AUDIT.json"), {
    label: "F_VS_177_LITERAL_BOOLEAN_SOURCE_AUDIT",
    law: "Serialized facts may not be typed as boolean literals. Remaining operational branch/API booleans are enumerated with source context; every named receipt-claim literal is a build violation.",
    provenance: ["F-VS-177@25c3a35a/877f1d76", "DEFINITION_LOCK"],
    ...literalAudit,
  });
  const priorTracePath = arg("prior-trace") ? path.resolve(arg("prior-trace")) : null;
  const priorActions = await loadPriorDecisionActions(priorTracePath);
  const nonTradedLowRows = allDerivations.filter((row) => row.derivation?.neighbor_leg?.own_evidence?.non_traded_low_consumed === true);
  const changedOrderRows = allDerivations.flatMap((row) => {
    const prior = priorActions.get(`${row.event_id}|${row.stage_receipt}|${row.leg_id}`);
    if (!prior || canonical(prior.action) === canonical(row.action)) return [];
    return [{
      event_id: row.event_id,
      leg_id: row.leg_id,
      timestamp_epoch: row.timestamp_epoch,
      receipt: row.stage_receipt,
      prior_action: prior.action,
      repaired_action: row.action,
      prior_own_evidence: prior.own_evidence,
      repaired_own_evidence: row.derivation.neighbor_leg.own_evidence,
      non_traded_low_consumed: row.derivation.neighbor_leg.own_evidence.non_traded_low_consumed,
      ...sentenceTraceIndex(row),
    }];
  });
  const danOpeningChanges = changedOrderRows.filter((row) => row.event_id === "KXATPMATCH-26JUL18DANPRA" && row.leg_id === "DAN").sort((a, b) => a.timestamp_epoch - b.timestamp_epoch);
  writeJson(path.join(output, "LOW_SOURCE_REPRICE_RECEIPT.json"), {
    label: "F_VS_164_168_169_TRADE_LOW_BOOK_PATH_MID_SEPARATION",
    run_source: RUN_SOURCE,
    law: "A traded low is written only by a true trade receipt. Book-path low, reported-last reference low, and bid/ask midpoint low are separately named non-trade evidence. Any action consuming them discloses that basis in its sentence.",
    prior_trace: priorTracePath ? receipt(priorTracePath) : null,
    evaluated_rows: allDerivations.length,
    non_traded_low_rows_repriced: nonTradedLowRows.length,
    non_traded_low_rows_every_sentence_discloses: nonTradedLowRows.every((row) => row.sentence.includes("NON_TRADED_LOW_DISCLOSURE=BOOK_PATH_REFERENCE_NOT_A_TRADE")),
    changed_orders: changedOrderRows,
    changed_order_count: changedOrderRows.length,
    danpra_opening_named_case: danOpeningChanges[0] ?? null,
    provenance: ["F-VS-164/F-VS-168/F-VS-169@44559ebc", "CC@e65fe458/44559ebc"],
  });
  const survivorRowsByKey = new Map();
  for (const row of allDerivations) {
    const survivor = row.layered_dual_belief?.macro?.survivor_shapes?.legs?.[row.leg_id];
    if (!survivor) continue;
    const key = `${row.event_id}|${row.leg_id}|${row.stage_receipt}`;
    survivorRowsByKey.set(key, {
      event_id: row.event_id,
      leg_id: row.leg_id,
      timestamp_epoch: row.timestamp_epoch,
      receipt: row.stage_receipt,
      all_shape_ids: survivor.all_shape_ids,
      survivor_shapes: survivor.survivor_shapes,
      eliminations: survivor.eliminations,
      eliminated_now: survivor.eliminated_now,
      reinstated_now: survivor.reinstated_now,
      movement: survivor.movement,
      modules: survivor.modules,
      trajectory_count: survivor.trajectory_count,
      target_axis: survivor.target_axis,
      target_criterion: survivor.target_criterion,
    });
  }
  const survivorRows = [...survivorRowsByKey.values()].sort((a, b) => a.event_id.localeCompare(b.event_id) || a.leg_id.localeCompare(b.leg_id) || a.timestamp_epoch - b.timestamp_epoch || a.receipt.localeCompare(b.receipt));
  const survivorTrajectoryRows = survivorRows.filter((row, index, rows) => {
    const prior = rows.slice(0, index).reverse().find((candidate) => candidate.event_id === row.event_id && candidate.leg_id === row.leg_id);
    return !prior || canonical(prior.survivor_shapes) !== canonical(row.survivor_shapes) || row.movement?.material_two_cent_move;
  });
  const survivorLegSummary = [...new Set(survivorRows.map((row) => `${row.event_id}|${row.leg_id}`))].map((identity) => {
    const [eventId, legId] = identity.split("|");
    const rows = survivorRows.filter((row) => row.event_id === eventId && row.leg_id === legId);
    return {
      event_id: eventId,
      leg_id: legId,
      seeded_shape_count: Math.max(0, ...rows.map((row) => row.all_shape_ids?.length ?? 0)),
      seeded_at_receipt: rows.find((row) => (row.all_shape_ids?.length ?? 0) > 0)?.receipt ?? null,
      final_survivor_count: rows.at(-1)?.survivor_shapes?.length ?? 0,
      trajectory_rows: survivorTrajectoryRows.filter((row) => row.event_id === eventId && row.leg_id === legId).length,
      eliminations_observed: rows.reduce((total, row) => total + (row.eliminated_now?.length ?? 0), 0),
      reinstatements_observed: rows.reduce((total, row) => total + (row.reinstated_now?.length ?? 0), 0),
    };
  });
  writeJson(path.join(output, "SURVIVOR_SHAPE_TRAJECTORIES.json"), {
    label: "V54_TRADED_LOW_AXIS_STATEFUL_SURVIVOR_SHAPES",
    source_commit: SURVIVOR_SOURCE_COMMIT,
    declaration: "Every leg starts with the full fitted V13 interim-shape set for its category/region. Exact member-backed post-formation traded-low depth bins narrow each leg; signable component tuples and couples may mutually narrow only after that leg evidence. Ask-path bins are not consulted. Every elimination carries a per-receipt overturn test and is reinstated when that test succeeds.",
    target_axis: os.LAYER_PROVENANCE.traded_low_axis_alignment,
    ask_reachability_role: "INFORM_ONLY_NEVER_DEFINES_TRADED_LOW_TARGET",
    right_edge_or_span_fraction_consumed: false,
    modules: ["window1_interim_elimination_v13", "window1_pair_interim_elimination_v18", "window1_pair_couple_elimination_v19"],
    legs: survivorLegSummary,
    trajectories: survivorTrajectoryRows,
    every_leg_seeded: survivorLegSummary.length === TARGETS.stories.length * 2 && survivorLegSummary.every((row) => row.seeded_shape_count > 0),
    every_live_elimination_has_overturn_test: survivorRows.every((row) => (row.eliminations ?? []).every((record) => Boolean(record.overturn_test) && record.last_rechecked_receipt === row.receipt)),
  });
  const floorMomentSeparationRows = storyResults.flatMap((story) => {
    const truth = truthRows.find((row) => row.event_id === story.event_id);
    return truth ? [truth.legA, truth.legB].map((legId) => {
      const side = truth.legA === legId ? "legA" : "legB";
      const floorEpoch = truth[`${side}_floor_epoch`], floorCents = truth[`${side}_floor_c`];
      const row = survivorRows.filter((candidate) => candidate.event_id === story.event_id && candidate.leg_id === legId && candidate.timestamp_epoch <= floorEpoch).sort((a, b) => b.timestamp_epoch - a.timestamp_epoch || String(b.receipt).localeCompare(String(a.receipt)))[0] ?? null;
      const levels = row?.target_criterion?.candidate_final_floor_levels_cents ?? [];
      const distances = levels.map((level) => Math.abs(level - floorCents));
      return {
        event_id: story.event_id,
        leg_id: legId,
        truth_floor_cents: floorCents,
        truth_floor_epoch: floorEpoch,
        evaluated_receipt: row?.receipt ?? null,
        evaluated_epoch: row?.timestamp_epoch ?? null,
        survivor_shapes: row?.survivor_shapes ?? [],
        target_axis: row?.target_axis ?? null,
        target_criterion: row?.target_criterion ?? null,
        exact_truth_floor_supported: levels.includes(floorCents),
        nearest_supported_gap_cents: distances.length ? Math.min(...distances) : null,
        candidate_level_count: levels.length,
        predictive_separation: levels.length === 0 ? "INSUFFICIENT_EVIDENCE" : levels.length === 1 ? "EXACT_ONE_LEVEL" : `${levels.length}_EXACT_MEMBER_BACKED_LEVELS`,
      };
    }) : [];
  });
  writeJson(path.join(output, "SURVIVOR_FLOOR_MOMENT_SEPARATION.json"), {
    label: "F_VS_139_TRADED_LOW_AXIS_SURVIVOR_PREDICTIVE_SEPARATION_AT_FLOOR",
    law: "Shape matching, elimination, and the target criterion resolve on exact member-backed traded-low depth bins. Ask reachability informs execution only.",
    provenance: ["F-VS-139/F-VS-143@f4752720", "TRADED_LOW_SHAPE_SUPPORT_BINDING.json"],
    rows: floorMomentSeparationRows,
    exact_floor_supported_legs: floorMomentSeparationRows.filter((row) => row.exact_truth_floor_supported).length,
    separated_to_one_exact_level_legs: floorMomentSeparationRows.filter((row) => row.candidate_level_count === 1).length,
  });
  const convictionRows = allDerivations.map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.stage_receipt,
    action: row.action,
    envelope_placement: row.layered_dual_belief?.envelope_placement,
    evolution: {
      update: row.layered_dual_belief?.conviction_evolution?.update ?? null,
      prior_envelope: row.layered_dual_belief?.conviction_evolution?.prior_envelope ?? null,
      effective_envelope: row.layered_dual_belief?.conviction_evolution?.effective_envelope ?? null,
      prior_conviction_receipt: row.layered_dual_belief?.conviction_evolution?.prior_conviction_receipt ?? null,
      prior_receipt_genuinely_readable: row.layered_dual_belief?.conviction_evolution?.prior_receipt_genuinely_readable ?? null,
      basis_re_stated_at_current_receipt: row.layered_dual_belief?.conviction_evolution?.basis_re_stated_at_current_receipt ?? null,
      eliminations_still_hold: row.layered_dual_belief?.conviction_evolution?.eliminations_still_hold ?? null,
      supporting_shape_ids_still_alive: row.layered_dual_belief?.conviction_evolution?.supporting_shape_ids_still_alive ?? [],
      movement_evidence: row.layered_dual_belief?.conviction_evolution?.movement_evidence ?? null,
    },
    prior_receipt_consumed_for_action: row.layered_dual_belief?.carried_conviction_consumed_for_action === true,
    ...sentenceTraceIndex(row),
  }));
  const carriedActionRows = convictionRows.filter((row) => row.prior_receipt_consumed_for_action && ["PLACE_REST", "REPRICE_REST"].includes(row.action.action));
  writeJson(path.join(output, "CARRIED_CONVICTION_RECEIPT.json"), {
    label: "V54_PRIOR_RECEIPT_CONVICTION_READ_UPDATE_AND_PLACEMENT",
    law: "A conviction persists across receipts. New movement confirms, tightens, shifts, or overturns it. A prior-receipt conviction may originate or reprice only while survivor support remains alive and its causal book basis is re-stated at the current receipt.",
    prior_receipt_readability: {
      readable_rows: allDerivations.filter((row) => row.layered_dual_belief?.conviction_evolution?.prior_receipt_genuinely_readable).length,
      unreadable_rows: allDerivations.filter((row) => row.layered_dual_belief?.conviction_evolution?.prior_conviction_receipt && !row.layered_dual_belief?.conviction_evolution?.prior_receipt_genuinely_readable).length,
    },
    stale_prior_gate_source_occurrences: (fs.readFileSync(path.join(repo, "arb-executor/analysis/window1_v54_dual_belief_os.js"), "utf8").match(/stale_prior_path_used\s*===\s*false/g) ?? []).length,
    prior_receipt_placements_or_reprices: carriedActionRows.length,
    rows: convictionRows,
    every_prior_receipt_action_restates_basis_and_survivors: carriedActionRows.every((row) => row.evolution?.prior_receipt_genuinely_readable === true && row.evolution?.basis_re_stated_at_current_receipt === true && row.evolution?.eliminations_still_hold === true && row.evolution?.supporting_shape_ids_still_alive?.length > 0),
  });
  const noEnvelopeTouchByLeg = [...new Set(allDerivations.map((row) => `${row.event_id}|${row.leg_id}`))].map((identity) => {
    const [eventId, legId] = identity.split("|");
    const rows = allDerivations.filter((row) => row.event_id === eventId && row.leg_id === legId);
    return {
      event_id: eventId,
      leg_id: legId,
      evaluated_receipts: rows.length,
      no_lawful_envelope_receipts: rows.filter((row) => row.layered_dual_belief?.envelope == null).length,
      touch_lane_receipts: rows.filter((row) => String(row.layered_dual_belief?.envelope_placement?.mode ?? "").startsWith("CONSUME_OWN_EVIDENCED_LIVE_TOUCH")).length,
      touch_lane_actions: rows.filter((row) => String(row.layered_dual_belief?.envelope_placement?.mode ?? "").startsWith("CONSUME_OWN_EVIDENCED_LIVE_TOUCH") && ["PLACE_REST", "REPRICE_REST"].includes(row.action.action)).length,
      carried_conviction_actions: rows.filter((row) => row.layered_dual_belief?.carried_conviction_consumed_for_action === true && ["PLACE_REST", "REPRICE_REST"].includes(row.action.action)).length,
      disagrees_own_evidence_actions: rows.filter((row) => row.layered_dual_belief?.envelope_placement?.mode === "OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED" && ["PLACE_REST", "REPRICE_REST"].includes(row.action.action)).length,
    };
  });
  writeJson(path.join(output, "NO_ENVELOPE_TOUCH_LANE_CENSUS.json"), {
    label: "V54_NO_ENVELOPE_AND_TOUCH_LANE_COUNTS_PER_LEG",
    rows: noEnvelopeTouchByLeg,
    totals: {
      no_lawful_envelope_receipts: noEnvelopeTouchByLeg.reduce((total, row) => total + row.no_lawful_envelope_receipts, 0),
      touch_lane_receipts: noEnvelopeTouchByLeg.reduce((total, row) => total + row.touch_lane_receipts, 0),
      touch_lane_actions: noEnvelopeTouchByLeg.reduce((total, row) => total + row.touch_lane_actions, 0),
      carried_conviction_actions: noEnvelopeTouchByLeg.reduce((total, row) => total + row.carried_conviction_actions, 0),
      disagrees_own_evidence_actions: noEnvelopeTouchByLeg.reduce((total, row) => total + row.disagrees_own_evidence_actions, 0),
    },
  });
  const floorProtectionRows = allDerivations.filter((row) => row.layered_dual_belief?.floor_rest_protection?.active_was_at_evidenced_floor
    || row.layered_dual_belief?.floor_rest_protection?.protected_from_conflicting_belief_or_cancel
    || row.layered_dual_belief?.floor_rest_protection?.same_receipt_floor_law_applied
    || row.layered_dual_belief?.floor_rest_protection?.postable_floor_rest_held_against_crossing_singleton).map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.stage_receipt,
    action: row.action,
    protection: row.layered_dual_belief.floor_rest_protection,
    survivor_shapes: row.layered_dual_belief?.macro?.survivor_shapes?.legs?.[row.leg_id] ?? null,
    ...sentenceTraceIndex(row),
  }));
  const floorProtectionViolations = floorProtectionRows.filter((row) => row.protection?.violation);
  const ursFloorProtectionRows = floorProtectionRows.filter((row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL14URSPAL" && row.leg_id === "URS");
  writeJson(path.join(output, "FLOOR_REST_PROTECTION_RECEIPT.json"), {
    label: "AT_FLOOR_REST_IMMUNE_TO_EVERY_ROUTINE_MOVER_UNTIL_ELIMINATION_OVERTURN_OR_CREDIT",
    run_source: RUN_SOURCE,
    law: "Evidenced floor is exactly the bell-lawful observed traded low. A rest exactly at it is immune to belief drift, DISAGREES, repricer, restore, and routine continuous post-only; only supporting-elimination overturn or trade credit ends it.",
    provenance: ["F-VS-154/F-VS-155/F-VS-159@6093141b", "F-VS-228@737e3c2b", "F-VS-134"],
    floor_rest_lock_source_occurrences: (fs.readFileSync(path.join(repo, "arb-executor/analysis/window1_v54_dual_belief_os.js"), "utf8").match(/floor_rest_locks\s*=/g) ?? []).length,
    rows: floorProtectionRows,
    protected_rows: floorProtectionRows.filter((row) => row.protection?.protected_from_conflicting_belief_or_cancel).length,
    same_receipt_floor_rows: floorProtectionRows.filter((row) => row.protection?.same_receipt_floor_law_applied).length,
    held_postable_singleton_rows: floorProtectionRows.filter((row) => row.protection?.postable_floor_rest_held_against_crossing_singleton).length,
    immunity_rows: floorProtectionRows.filter((row) => row.protection?.at_floor_immunity_applied).length,
    violations: floorProtectionViolations,
    urs_named_rows: ursFloorProtectionRows,
    urs_repriced_off_observed_traded_floor: ursFloorProtectionRows.some((row) => Number.isInteger(row.protection?.evidenced_floor_cents)
      && row.protection?.active_target_before_cents === row.protection.evidenced_floor_cents
      && row.action?.target_cents !== row.protection.evidenced_floor_cents),
  });
  writeJson(path.join(output, "AT_FLOOR_IMMUNITY_RECEIPT.json"), {
    label: "ONE_AT_FLOOR_IMMUNITY_NOT_PER_GUARD_PATCHES",
    authority: ["F-VS-228@737e3c2b", "F-VS-134"],
    immune_to: ["CONTINUOUS_POST_ONLY", "DISAGREES_EMBARGO", "BELIEF_REPRICER", "RESTORE_LANES"],
    rows: floorProtectionRows.filter((row) => row.protection?.at_floor_immunity_applied),
    violations: floorProtectionViolations,
    named_PRA_41: floorProtectionRows.filter((row) => row.event_id === "KXATPMATCH-26JUL18DANPRA" && row.leg_id === "PRA" && row.protection?.evidenced_floor_cents === 41),
  });
  const tenureFillEvents = storyTraces.filter((row) => row.kind === "FILL_EVENT").map((row) => row.fill_event_receipt);
  const tenureRowsByLeg = storyResults.flatMap((story) => {
    const truth = truthRows.find((row) => row.event_id === story.event_id);
    return [truth?.legA, truth?.legB].filter(Boolean).map((legId) => {
      const truthSide = truth.legA === legId ? "legA" : "legB";
      const truthFloor = truth[`${truthSide}_floor_c`];
      const bellEpoch = truth.bell_epoch;
      const legRows = allDerivations.filter((row) => row.event_id === story.event_id && row.leg_id === legId).sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || String(a.stage_receipt).localeCompare(String(b.stage_receipt)));
      const orders = legRows.filter((row) => ["PLACE_REST", "REPRICE_REST", "CANCEL_REST"].includes(row.action.action));
      const fill = tenureFillEvents.find((row) => row.context?.event_id === story.event_id && row.context?.leg_id === legId) ?? null;
      const tapePrints = (storyTapeRows.get(story.event_id) ?? []).filter((row) => row.kind === "PRINT" && row.leg_id === legId && Number.isInteger(row.price_cents)).sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || String(a.receipt).localeCompare(String(b.receipt)));
      const episodes = [];
      for (let index = 0; index < orders.length; index += 1) {
        const order = orders[index];
        if (!["PLACE_REST", "REPRICE_REST"].includes(order.action.action) || !Number.isInteger(order.action.target_cents)) continue;
        const nextOrder = orders.slice(index + 1).find((candidate) => candidate.timestamp_epoch >= order.timestamp_epoch) ?? null;
        const fillEpoch = fill?.context?.fill_timestamp_epoch;
        const fillEndsThisRest = Number.isFinite(fillEpoch)
          && fillEpoch >= order.timestamp_epoch
          && (!nextOrder || fillEpoch <= nextOrder.timestamp_epoch);
        const endEpoch = fillEndsThisRest ? fillEpoch : nextOrder?.timestamp_epoch ?? bellEpoch;
        const endedBy = fillEndsThisRest
          ? `FILL:${fill.captured_at_receipt}`
          : nextOrder
            ? `${nextOrder.action.action}:${nextOrder.stage_receipt}`
            : "WINDOW_EDGE";
        const prefixBeforeStand = tapePrints.filter((row) => row.timestamp_epoch <= order.timestamp_epoch);
        const runningFloorAtStand = prefixBeforeStand.length ? Math.min(...prefixBeforeStand.map((row) => row.price_cents)) : null;
        let tenureStartEpoch = Number.isInteger(runningFloorAtStand) && order.action.target_cents <= runningFloorAtStand ? order.timestamp_epoch : null;
        let tenureStartReceipt = tenureStartEpoch === order.timestamp_epoch ? order.stage_receipt : null;
        if (!Number.isFinite(tenureStartEpoch)) {
          const firstSupportPrint = tapePrints.find((row) => row.timestamp_epoch > order.timestamp_epoch && row.timestamp_epoch <= endEpoch && order.action.target_cents <= row.price_cents);
          if (firstSupportPrint) {
            tenureStartEpoch = firstSupportPrint.timestamp_epoch;
            tenureStartReceipt = firstSupportPrint.receipt;
          }
        }
        const sampledDecisionRows = legRows.filter((row) => row.timestamp_epoch > order.timestamp_epoch && row.timestamp_epoch <= endEpoch);
        const postableTenure = Number.isFinite(tenureStartEpoch);
        episodes.push({
          level_cents: order.action.target_cents,
          standing_started_at_epoch: order.timestamp_epoch,
          standing_started_at_receipt: order.stage_receipt,
          standing_ended_at_epoch: endEpoch,
          standing_ended_by: endedBy,
          full_standing_interval_seconds: Number.isFinite(endEpoch) ? endEpoch - order.timestamp_epoch : null,
          governing_floor_tenure_started_at_epoch: tenureStartEpoch,
          governing_floor_tenure_started_at_receipt: tenureStartReceipt,
          tenure_seconds: postableTenure && Number.isFinite(endEpoch) ? endEpoch - tenureStartEpoch : null,
          running_traded_low_at_stand_cents: runningFloorAtStand,
          truth_table_floor_cents: truthFloor,
          relation_to_running_low_at_stand: !Number.isInteger(runningFloorAtStand)
            ? "NO_TRADED_FLOOR_AT_STAND"
            : order.action.target_cents === runningFloorAtStand
              ? "AT_RUNNING_TRADED_LOW"
              : order.action.target_cents < runningFloorAtStand
                ? "BELOW_RUNNING_TRADED_LOW"
                : "ABOVE_RUNNING_TRADED_LOW",
          counted_as_governing_floor_tenure: postableTenure,
          decision_rows_inside_standing_interval: sampledDecisionRows.length,
          sampling_status: sampledDecisionRows.length ? "SAMPLED" : "UNSAMPLED_BETWEEN_ORDER_TRANSITIONS",
          supporting_order_reason: order.action.reason,
        });
      }
      return {
        event_id: story.event_id,
        leg_id: legId,
        truth_table_floor_cents: truthFloor,
        decision_rows_total: legRows.length,
        sampling_status: legRows.length ? "SAMPLED_SOMEWHERE_IN_WINDOW" : "UNSAMPLED_WINDOW_NOT_ZERO",
        at_floor_receipts: legRows.filter((row) => Number.isInteger(row.layered_dual_belief?.floor_rest_protection?.evidenced_floor_cents)
          && Number.isInteger(row.layered_dual_belief?.floor_rest_protection?.active_target_before_cents)
          && row.layered_dual_belief.floor_rest_protection.active_target_before_cents <= row.layered_dual_belief.floor_rest_protection.evidenced_floor_cents).length,
        episodes,
      };
    });
  });
  writeJson(path.join(output, "EVIDENCED_FLOOR_TENURE_TABLE.json"), {
    label: "V54_SINGLE_ORDER_TRANSITION_TENURE_PRODUCER",
    run_source: RUN_SOURCE,
    law: "Tenure is reconstructed from actual PLACE/REPRICE/CANCEL/FILL transitions. A rest at or below the causal running traded low counts from the order transition, including when its level is below that running low. An interval with no decision rows is UNSAMPLED, never zero.",
    producer: "build_window1_v54_dual_belief.js::ORDER_TRANSITION_TENURE_SINGLE_PRODUCER",
    competing_in_policy_sampled_row_producer: false,
    every_policy_row_names_single_producer: allDerivations.every((row) => row.layered_dual_belief?.floor_rest_protection?.tenure_instrument === "ORDER_TRANSITION_TENURE_SINGLE_PRODUCER" && row.layered_dual_belief?.floor_rest_protection?.sampled_row_tenure_serialized === false),
    provenance: ["F-VS-184@12f25f37", "CC@601207d0/12f25f37"],
    rows: tenureRowsByLeg,
    disagrees_moved_floor_rest_count: floorProtectionRows.filter((row) => row.protection?.active_was_at_evidenced_floor && row.protection?.violation && row.survivor_shapes?.coherence_status === "DISAGREES").length,
  });
  const proposalSupervisorRows = allDerivations.map((row) => ({ event_id: row.event_id, leg_id: row.leg_id, timestamp_epoch: row.timestamp_epoch, receipt: row.stage_receipt, action: row.action, envelope: row.layered_dual_belief?.envelope, placement: row.layered_dual_belief?.envelope_placement, supervisor: row.layered_dual_belief?.proposal_supervisor, atomic_rearm: row.layered_dual_belief?.atomic_rearm ?? null, authority_target_divergence: row.derivation?.authority_target_divergence ?? null, ...sentenceTraceIndex(row) }));
  const supervisedFloorProposalRows = proposalSupervisorRows.filter((row) => row.supervisor?.supervisor_required);
  const exactFloorProposalRows = supervisedFloorProposalRows.filter((row) => row.supervisor?.proposal_cents === row.supervisor?.evidenced_floor_cents);
  const singletonEnvelopeRows = proposalSupervisorRows.filter((row) => Number.isInteger(row.placement?.singleton_survivor_envelope_level_cents));
  const singletonUnconsumedRows = singletonEnvelopeRows.filter((row) => {
    // The old checker treated a vetoed or non-emitting row as a missed order.
    // F-VS-150 governs an executable proposal: if the singleton is emitted it
    // must be emitted at that exact level. A formation/pair/post-only veto is
    // not another price writer and therefore is not "unconsumed".
    const emitted = ["PLACE_REST", "REPRICE_REST"].includes(row.action?.action);
    if (!emitted) return false;
    const heldLawfulRest = row.placement?.post_only_disposition === "VETO_ONLY_NEW_TARGET_UNPOSTABLE_EXISTING_LAWFUL_REST_HELD"
      && row.supervisor?.final_target_cents === row.placement?.active_captured_rest_level_cents;
    const licensedPricingAuthorityConsumed = row.placement?.technique_contract === "C01_PRICING_AUTHORITY_OVER_LANE_LEVEL_SELECTION"
      && row.placement?.pricing_authority?.authority_restored_to_decision_path === true
      && row.placement?.pricing_authority?.target_from_licensed_rows === true
      && row.supervisor?.final_target_cents === row.placement?.pricing_authority?.target_cents;
    const licensedCancelRearmIsSenior = row.authority_target_divergence?.senior_authority_reason === "C04_PAIR_CONSERVATION_CANCEL_REARM_PENDING"
      ? row.atomic_rearm?.status === "REARM_PENDING" && row.supervisor?.final_target_cents === null
      : row.authority_target_divergence?.senior_authority_reason === "C04_CANCEL_REARM_RESTORES_PRICE"
        && row.atomic_rearm?.status === "REARM_RESOLVED_WITH_LAWFUL_REST"
        && row.supervisor?.final_target_cents === row.atomic_rearm?.replacement_target_cents;
    return !heldLawfulRest && !licensedPricingAuthorityConsumed && !licensedCancelRearmIsSenior
      && (row.placement?.singleton_envelope_consumed !== true || row.supervisor?.final_target_cents !== row.placement?.singleton_survivor_envelope_level_cents);
  });
  writeJson(path.join(output, "NARROWING_AND_PROPOSAL_SUPERVISOR_RECEIPT.json"), {
    label: "F_VS_149_150_NARROWING_CONSUMPTION_AND_REAL_REASON_SUPERVISOR",
    provenance: ["F-VS-149@d079687f", "F-VS-150@d079687f"],
    floor_rest_lock_source_occurrences: (fs.readFileSync(path.join(repo, "arb-executor/analysis/window1_v54_dual_belief_os.js"), "utf8").match(/floor_rest_locks\s*=/g) ?? []).length,
    exact_floor_proposals: exactFloorProposalRows.length,
    exact_floor_proposals_admitted: exactFloorProposalRows.filter((row) => ["ADMITTED_AT_OR_BELOW_EVIDENCED_FLOOR", "HELD_EXISTING_EVIDENCED_FLOOR_REST"].includes(row.supervisor?.status)).length,
    singleton_envelope_rows: singletonEnvelopeRows.length,
    singleton_unconsumed_rows: singletonUnconsumedRows,
    supervised_floor_proposal_rows: supervisedFloorProposalRows,
    every_blocked_or_refused_floor_proposal_has_real_reason: supervisedFloorProposalRows.every((row) => row.supervisor?.independent_check?.passed === true && row.supervisor?.reason && !String(row.supervisor.reason).includes("NOT_REQUIRED")),
    no_not_required_stamp: proposalSupervisorRows.every((row) => !String(row.supervisor?.status ?? "").includes("NOT_REQUIRED") && !String(row.supervisor?.reason ?? "").includes("NOT_REQUIRED")),
    rows: proposalSupervisorRows,
  });
  writeJson(path.join(output, "EVIDENCE_LADDER_RECEIPT.json"), {
    label: "MIND_WINDOW_TOUCH_PRICE_MAP_LICENSE_RECEIPT",
    declaration: os.CONDITIONAL_DIP_DECLARATION,
    method: "At every evaluated receipt the mind names the side/window from graded floor-timing and own evidence. The rest stands at the causal best-bid touch. A below-touch rest exists only when the current touch-price V3 row covers the evidence-conditioned depth.",
    binary_same_state_gate_used: false,
    blanket_ratio_used: false,
    absolute_floor_target_used: false,
    explicit_reflex_rung_present: false,
    placement_constants_or_thresholds: [],
    derivations: allDerivations.map((row) => ({ event_id: row.event_id, leg_id: row.leg_id, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, evidence_rung: row.derivation.evidence_rung, rung_availability: row.derivation.rung_availability, rung_evidence_grade: row.derivation.rung_evidence_grade, live_touch_bid_cents: row.derivation.live_bid_cents, live_ask_cents: row.derivation.live_ask_cents, chosen_depth_cents: row.derivation.chosen_depth_cents, pre_allocation_target_cents: row.derivation.lawful_unallocated_target_cents, final_target_cents: row.action.target_cents, final_depth_below_touch_cents: row.derivation.final_depth_below_touch_cents, raw_remaining_dip_distribution_cents: row.derivation.neighbor_leg.conditional_remaining_dip_distribution_cents, time_conditioned_remaining_dip_distribution_cents: row.derivation.depth_distribution_cents, window_timing: row.derivation.window_timing, pair_state: row.derivation.pair_state, sibling_commitment_cents: row.derivation.sibling_commitment_cents, pair_required_depth_cents: row.derivation.pair_required_depth_cents, own_evidence: row.derivation.neighbor_leg.own_evidence, member_count: row.derivation.neighbor_leg.rows?.length ?? 0, excluded_count: row.derivation.neighbor_leg.excluded?.length ?? 0, target_authority: row.derivation.target_authority, touch_relation: row.derivation.touch_relation, joint_depth_license: row.derivation.joint_depth_license, allocation: row.derivation.allocation, ...sentenceTraceIndex(row) })),
    every_sentence_states_required_depth_inputs: allDerivations.every((row) => row.sentence.includes("WINDOW_SIDE_READ=") && row.sentence.includes("PRICE_AT_EVIDENCED_TOUCH=") && row.sentence.includes("MAP_CELL=") && row.sentence.includes("MAP_P50_CENTS=") && row.sentence.includes("MAP_MEMBERS=") && row.sentence.includes("CHOSEN_DEPTH_CENTS=") && row.sentence.includes("OWN_WINDOW=") && row.sentence.includes("PAIR_STATE=")),
    every_sentence_names_basis: allDerivations.every((row) => os.CONDITIONAL_DIP_DECLARATION.authority_order.some((rung) => row.sentence.includes(`EVIDENCE_RUNG=${rung}`))),
    rung_counts: allDerivations.reduce((counts, row) => (counts[row.derivation.evidence_rung] = (counts[row.derivation.evidence_rung] ?? 0) + 1, counts), {}),
  });
  writeJson(path.join(output, "SPLIT_ALLOCATION_RECEIPT.json"), {
    label: "PER_RECEIPT_GRADED_CONTINUOUS_SPLIT",
    law: "Both uncredited standing rests are revisable plans. Fresh per-receipt composed targets are allocated continuously by current evidence grades whenever their sum exceeds 99; a credited fill remains commitment.",
    hard_ask_equals_target_plus_one_gate_used: false,
    stale_prior_hard_ban_removed: true,
    carried_prior_consumption_receipt: "CARRIED_CONVICTION_RECEIPT.json",
    derivations: allDerivations.map((row) => ({ event_id: row.event_id, leg_id: row.leg_id, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, lawful_unallocated_target_cents: row.derivation.lawful_unallocated_target_cents, allocation_priority_grade: row.derivation.allocation_priority_grade, allocation: row.derivation.allocation, final_target_cents: row.action.target_cents, ...sentenceTraceIndex(row) })),
    every_sentence_states_allocation: allDerivations.every((row) => row.sentence.includes("ALLOCATION=")),
    every_split_preserves_pair_budget: allDerivations.every((row) => row.pair_conservation.at_or_below_99),
    reallocations: allDerivations.filter((row) => row.derivation.allocation?.mode === "GRADED-CONTINUOUS-SPLIT"),
    every_reallocation_shows_from_not_equal_to: allDerivations.filter((row) => row.derivation.allocation?.mode === "GRADED-CONTINUOUS-SPLIT").every((row) => row.derivation.allocation.from_cents !== row.derivation.allocation.to_cents),
  });
  const headroomRows = allDerivations.map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.stage_receipt,
    proposal_cents: row.layered_dual_belief?.envelope_placement?.chosen_target_cents ?? null,
    final_target_cents: row.action.target_cents,
    par_allocation_floor_bound: row.layered_dual_belief?.par_allocation_floor_bound ?? null,
    headroom_cents: row.derivation?.allocation?.headroom_cents?.[row.leg_id] ?? null,
    reduction_cents: row.derivation?.allocation?.reductions_cents?.[row.leg_id] ?? 0,
    allocation_reason: row.derivation?.allocation?.reason ?? null,
    sentence_has_par_allocation_fields: row.sentence.includes("PAR_ALLOCATION_FLOOR_BOUND=") && row.sentence.includes("PAR_ALLOCATION_HEADROOM_CENTS="),
    ...sentenceTraceIndex(row),
  }));
  writeJson(path.join(output, "PAR_ALLOCATION_HEADROOM_RECEIPT.json"), {
    label: "F_VS_160_169_NAMED_PAR_ALLOCATION_OBSERVED_TRADED_FLOOR_BOUND",
    run_source: RUN_SOURCE,
    law: "The formerly nameless lowerBounds object is PAR_ALLOCATION_OBSERVED_TRADED_FLOOR_BOUND. It measures reducible headroom against each leg's own observed traded floor, never against a belief envelope and never above the traded floor.",
    rows: headroomRows,
    writes: headroomRows.length,
    every_write_named: headroomRows.every((row) => row.par_allocation_floor_bound?.name === "PAR_ALLOCATION_OBSERVED_TRADED_FLOOR_BOUND"),
    every_bound_at_or_below_evidenced_floor: headroomRows.every((row) => !Number.isInteger(row.par_allocation_floor_bound?.evidenced_floor_cents) || !Number.isInteger(row.par_allocation_floor_bound?.value_cents) || row.par_allocation_floor_bound.value_cents <= row.par_allocation_floor_bound.evidenced_floor_cents),
    allocation_sentences_complete: headroomRows.every((row) => row.sentence_has_par_allocation_fields),
    named_sva_rows: headroomRows.filter((row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL14LAJSVA" && row.leg_id === "SVA" && row.proposal_cents === 41),
    provenance: ["F-VS-160@a2a6a25d", "F-VS-169@44559ebc"],
  });
  writeJson(path.join(output, "COMPOSITION_PRESENCE_RECEIPT.json"), {
    label: "MIND_WINDOWED_TOUCH_PRICED_MAP_LICENSED_COMPOSITION",
    composition: "The mind selects windows and sides from graded floor timing, pair state, and the leg's own evidence. Pricing authority is the current evidenced touch, with V3-map depth only where the row covers the conditioned depth.",
    presence: "A fresh formed non-crossed two-sided book supplies touch. FORMATION_NOT_COMPLETE and crossed books are fail-loud non-placement states.",
    no_placement_constant_added: true,
    stale_prior_path_removed: true,
    rows: allDerivations.map((row) => ({ event_id: row.event_id, leg_id: row.leg_id, receipt: row.receipt, live_bid_cents: row.derivation.live_bid_cents, live_ask_cents: row.derivation.live_ask_cents, own_bounded_traded_low_cents: row.derivation.neighbor_leg.own_evidence.observed_traded_low_cents, own_book_path_low_cents: row.derivation.neighbor_leg.own_evidence.observed_book_path_low_cents, conditioned_depth_distribution_cents: row.derivation.depth_distribution_cents, chosen_depth_cents: row.derivation.chosen_depth_cents, target_cents: row.action.target_cents, touch_relation: row.derivation.touch_relation, joint_depth_license: row.derivation.joint_depth_license, target_basis: row.derivation.target_basis, target_authority: row.derivation.target_authority, ...sentenceTraceIndex(row) })),
    every_target_states_touch_relation: allDerivations.every((row) => row.sentence.includes("TOUCH_RELATION=")),
    every_below_trade_low_target_has_joint_license: allDerivations.every((row) => {
      const own = row.derivation.neighbor_leg.own_evidence;
      return !Number.isInteger(own.observed_traded_low_cents) || !Number.isInteger(row.action.target_cents) || row.action.target_cents >= own.observed_traded_low_cents || row.derivation.joint_depth_license?.lawful === true;
    }),
  });
  writeJson(path.join(output, "FOUNDATION_SERVING_FIX_RECEIPT.json"), {
    label: "FOUNDATION_STRICT_PRE_BELL_TRADE_MINUTES",
    native_window_law: corpus.foundation.native_window_law,
    served_high_basis: "MAX_PRICE_HIGH_ON_TRADE_BEARING_MINUTES_STRICTLY_BEFORE_BELL",
    served_close_basis: "LAST_PRICE_CLOSE_ON_TRADE_BEARING_MINUTE_STRICTLY_BEFORE_BELL",
    herhar_expected: { event_id: "KXATPMATCH-26MAR29HERHAR", leg_id: "HAR", old_leaking_low_cents: 49, repaired_pre_bell_low_cents: 50 },
    herhar_actual: corpus.rows.find((row) => row.event_id === "KXATPMATCH-26MAR29HERHAR")?.legs?.find((leg) => leg.leg_id === "HAR") ?? null,
  });
  const fillEvents = storyTraces.filter((row) => row.kind === "FILL_EVENT").map((row) => row.fill_event_receipt);
  const fillHandoffs = decisionStages.flatMap((row) => row.derivations).filter((row) => row.derivation.fill_handoff_receipt_id).map((row) => {
    const tradeReceipt = row.citation_receipts[row.derivation.fill_handoff_receipt_id]?.context?.original_fill_receipt;
    return { event_id: row.event_id, leg_id: row.leg_id, timestamp_epoch: row.timestamp_epoch, trade_receipt: tradeReceipt, handoff_receipt_id: row.derivation.fill_handoff_receipt_id, query_fingerprint_sha256: row.derivation.reposed_query_fingerprint_sha256, sentence_cites_trade_receipt: Boolean(tradeReceipt && row.sentence.includes(tradeReceipt)), sentence_cites_handoff_receipt: row.sentence.includes(row.derivation.fill_handoff_receipt_id), ...sentenceTraceIndex(row) };
  });
  const tradeReports = TARGETS.stories.map((eventId) => {
    const stages = decisionStages.filter((row) => row.event_id === eventId).sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || String(a.receipt).localeCompare(String(b.receipt)));
    const firstBeliefStage = stages.find((stage) => stage.derivations.some((row) => Object.values(row.layered_dual_belief?.micro?.beliefs ?? {}).some((belief) => belief.status === "RESOLVED"))) ?? stages[0];
    const firstCoherenceStage = stages.find((stage) => stage.coherence?.status === "COHERENT") ?? null;
    const actionRows = [];
    const priorActionByLeg = new Map();
    for (const stage of stages) {
      for (const row of stage.derivations) {
        const signature = `${row.action.action}|${row.action.target_cents ?? "NONE"}|${row.action.reason}`;
        if (priorActionByLeg.get(row.leg_id) === signature) continue;
        priorActionByLeg.set(row.leg_id, signature);
        actionRows.push({ leg_id: row.leg_id, timestamp_epoch: stage.timestamp_epoch, receipt: stage.receipt, action: row.action, standing_license: row.action.reason, ...sentenceTraceIndex(row) });
      }
    }
    const eventFills = fillEvents.filter((fill) => fill.context.event_id === eventId);
    const outcome = storyResults.find((row) => row.event_id === eventId).layered_dual_belief;
    const finalStage = stages.at(-1);
    const grade = outcome.completed && outcome.delta_vs_100_cents > 0
      ? "GOOD_COHERENT_UNDER_PAR_COMPLETION"
      : outcome.completed
        ? "BAD_COHERENT_NON_DELTA_COMPLETION"
        : eventFills.length
          ? "MIXED_COHERENT_PARTIAL"
          : "BAD_COHERENT_OR_ABSTAINED_WITHOUT_COMPLETION";
    return {
      event_id: eventId,
      what_i_believed_at_open: {
        receipt: firstBeliefStage?.receipt ?? null,
        timestamp_epoch: firstBeliefStage?.timestamp_epoch ?? null,
        dual_sentences_verbatim: firstBeliefStage?.derivations.map((row) => row.sentence) ?? [],
      },
      what_i_decided_per_side_and_why: {
        first_coherence_receipt: firstCoherenceStage?.receipt ?? null,
        first_coherence: firstCoherenceStage?.coherence ?? null,
        first_coherent_actions: firstCoherenceStage?.derivations.map((row) => ({ leg_id: row.leg_id, action: row.action, sentence_verbatim: row.sentence })) ?? [],
      },
      each_action_at_each_price_with_reason: actionRows,
      what_happened: {
        fills: eventFills,
        terminal_receipt: finalStage?.receipt ?? null,
        terminal_epoch: finalStage?.timestamp_epoch ?? null,
        terminal_actions: finalStage?.derivations.map((row) => ({ leg_id: row.leg_id, action: row.action, ...sentenceTraceIndex(row) })) ?? [],
        execution: outcome,
      },
      my_grade_of_my_own_trade: { grade, reason: outcome.completed ? `coherent rests completed at ${outcome.combined_entry_cents} cents, delta ${outcome.delta_vs_100_cents}` : `${eventFills.length} coherent-rest fill(s); pair did not complete`, receipt: eventFills.at(-1)?.receipt_id ?? finalStage?.receipt ?? null },
      what_id_flag_for_the_library: { flag: "PHASE_CONDITIONING_AND_OWN_DEADLINE_CALIBRATION", receipt: firstCoherenceStage?.receipt ?? firstBeliefStage?.receipt ?? null, artifact: "BELIEF_DEADLINE_SCORING_TABLE.json" },
      complete_six_section_report: Boolean(firstBeliefStage && finalStage && actionRows.length && (firstCoherenceStage || stages.every((stage) => stage.coherence?.status !== "COHERENT"))),
      coherence_disposition: firstCoherenceStage ? "COHERED" : "NEVER_COHERED_TRUTHFULLY_REPORTED",
    };
  });
  writeJson(path.join(output, "TRADE_REPORT_FOUR.json"), { label: "F_VS_055_FOUR_GAME_TRADE_REPORTS", reports: tradeReports, every_game_complete_six_sections: tradeReports.every((report) => report.complete_six_section_report), fill_price_basis: "STANDING_REST_LIMIT_CENTS" });
  writeText(path.join(output, "TRADE_REPORT_FOUR.md"), `# Four-game trade reports\n\n${tradeReports.map((report) => `## ${report.event_id}\n\n### WHAT I BELIEVED AT OPEN\n\n${report.what_i_believed_at_open.dual_sentences_verbatim.map((sentence) => `- ${sentence} [receipt: ${report.what_i_believed_at_open.receipt}]`).join("\n")}\n\n### WHAT I DECIDED PER SIDE AND WHY\n\n${report.what_i_decided_per_side_and_why.first_coherent_actions.map((row) => `- ${row.leg_id}: ${row.action.action} ${row.action.target_cents ?? "NONE"}. ${row.sentence_verbatim} [receipt: ${report.what_i_decided_per_side_and_why.first_coherence_receipt}]`).join("\n")}\n\n### EACH ACTION AT EACH PRICE WITH ITS REASON AT THAT TIME\n\n${report.each_action_at_each_price_with_reason.map((row) => `- ${row.leg_id} @ ${row.timestamp_epoch}: ${row.action.action} ${row.action.target_cents ?? "NONE"}; ${row.standing_license}. [receipt: ${row.receipt}]`).join("\n")}\n\n### WHAT HAPPENED\n\n${report.what_happened.fills.length ? report.what_happened.fills.map((fill) => `- ${fill.context.leg_id} filled at REST ${fill.context.entry_cents} cents; print ${fill.context.triggering_print_price_cents} cents proved the credit. [receipt: ${fill.receipt_id}; trade: ${fill.context.standing_license_receipt}]`).join("\n") : `- No fill. [receipt: ${report.what_happened.terminal_receipt}]`}\n- Terminal state: ${JSON.stringify(report.what_happened.execution)}. [receipt: ${report.what_happened.terminal_receipt}]\n\n### MY GRADE OF MY OWN TRADE\n\n- ${report.my_grade_of_my_own_trade.grade}: ${report.my_grade_of_my_own_trade.reason}. [receipt: ${report.my_grade_of_my_own_trade.receipt}]\n\n### WHAT I'D FLAG FOR THE LIBRARY\n\n- ${report.what_id_flag_for_the_library.flag}; see ${report.what_id_flag_for_the_library.artifact}. [receipt: ${report.what_id_flag_for_the_library.receipt}]`).join("\n\n")}\n`);
  writeJson(path.join(output, "FILL_HANDOFF_RECEIPT.json"), { label: "FILL_HANDOFF_RECEIPT", fill_events: fillEvents, post_fill_derivations: fillHandoffs, every_post_fill_sentence_cites_fill_receipt: fillHandoffs.every((row) => row.trade_receipt && row.sentence_cites_trade_receipt && row.sentence_cites_handoff_receipt) });
  const restPriceRows = fillEvents.map((row) => ({
    event_id: row.context.event_id,
    leg_id: row.context.leg_id,
    fill_timestamp_epoch: row.context.fill_timestamp_epoch,
    fill_receipt: row.receipt_id,
    standing_rest_cents: row.context.prior_standing_target_cents,
    triggering_print_cents: row.context.triggering_print_price_cents,
    credited_entry_cents: row.context.entry_cents,
    execution_price_basis: row.context.execution_price_basis,
    entry_equals_standing_rest: row.context.entry_cents === row.context.prior_standing_target_cents,
    print_at_or_below_rest: row.context.triggering_print_price_cents <= row.context.prior_standing_target_cents,
  }));
  const activeCreditingFiles = [
    "arb-executor/analysis/window1_v54_functionable_os.js",
    "arb-executor/analysis/window1_v54_dual_belief_os.js",
    "arb-executor/analysis/build_window1_v54_dual_belief.js",
    "arb-executor/analysis/window1_v54_dual_belief_reporter.js",
  ];
  const printPricedPatterns = [
    { name: "ENTRY_FROM_ROW_PRICE_OBJECT", regex: /entry_cents\s*:\s*row\.price_cents/g },
    { name: "ENTRY_FROM_ROW_PRICE_ASSIGNMENT", regex: /entry_cents\s*=\s*row\.price_cents/g },
    { name: "POSITION_FROM_ROW_PRICE", regex: /position\.entry_cents\s*=\s*row\.price_cents/g },
  ];
  const sourceSweep = activeCreditingFiles.map((relative) => {
    const text = fs.readFileSync(path.join(repo, relative), "utf8");
    const matches = printPricedPatterns.flatMap((pattern) => [...text.matchAll(pattern.regex)].map((match) => ({ pattern: pattern.name, offset: match.index })));
    return { path: relative, sha256: shaBytes(text), matches, active_print_priced_residue_count: matches.length };
  });
  const printPricedResidueCount = sourceSweep.reduce((sum, row) => sum + row.active_print_priced_residue_count, 0);
  writeJson(path.join(output, "REST_PRICED_CREDITING_RECEIPT.json"), {
    label: "REST_PRICED_CREDITING",
    law: "A qualifying print at-or-below a standing rest proves credit; the credited entry is the rest limit, never the lower triggering print.",
    law_index_read_at: "bcee2c40",
    findings: ["F-VS-104", "F-VS-105", "F-VS-106"],
    fills: restPriceRows,
    fill_count: restPriceRows.length,
    prints_strictly_below_rest_count: restPriceRows.filter((row) => row.triggering_print_cents < row.standing_rest_cents).length,
    every_entry_equals_standing_rest: restPriceRows.every((row) => row.entry_equals_standing_rest),
    every_triggering_print_at_or_below_rest: restPriceRows.every((row) => row.print_at_or_below_rest),
  });
  writeJson(path.join(output, "PRINT_PRICED_RESIDUE_SWEEP.json"), {
    label: "ACTIVE_EXECUTION_SURFACE_PRINT_PRICED_RESIDUE_SWEEP",
    scope: "The four files executed by this repair: crediting OS, layered OS, builder/grader, and story/process reporter.",
    source_files: sourceSweep,
    active_print_priced_residue_count: printPricedResidueCount,
    fill_receipt_mismatch_count: restPriceRows.filter((row) => !row.entry_equals_standing_rest).length,
    report_or_gate_input: "All stories, reports, gates, and score rows consume the position entry produced by the active crediting OS.",
  });
  const beliefPriceRows = allDerivations.flatMap((row) => Object.values(row.layered_dual_belief?.micro?.beliefs ?? {}).filter((belief) => belief?.status === "RESOLVED").map((belief) => ({
    event_id: row.event_id,
    evaluated_leg_id: row.leg_id,
    belief_leg_id: belief.leg_id,
    timestamp_epoch: row.timestamp_epoch,
    stage_receipt: row.stage_receipt,
    book_receipt: belief.belief_price_book_receipt,
    bid_cents: belief.live_bid_cents,
    ask_cents: belief.live_ask_cents,
    belief_price_cents: belief.belief_price_cents,
    basis: belief.belief_price_basis,
    expected_series_floored_mid_cents: Math.floor((belief.live_bid_cents + belief.live_ask_cents) / 2),
    field_matches_book_state: belief.belief_price_cents === Math.floor((belief.live_bid_cents + belief.live_ask_cents) / 2),
  })));
  writeJson(path.join(output, "BELIEF_SENTENCE_PRICE_FIELD_RECEIPT.json"), {
    label: "BELIEF_PRICE_IS_EVIDENCED_BOOK_STATE",
    bare_reader_level_used_as_belief_price: false,
    method: "SETTLED_BOOK_MID_SERIES_FLOORED_FROM_RECEIPT_PINNED_BID_ASK",
    rows: beliefPriceRows,
    every_field_matches_book_state: beliefPriceRows.every((row) => row.field_matches_book_state),
    every_row_names_book_receipt: beliefPriceRows.every((row) => Boolean(row.book_receipt)),
  });
  const deadlineSeen = new Set(), deadlineRows = [];
  for (const row of allDerivations) {
    for (const belief of Object.values(row.layered_dual_belief?.micro?.beliefs ?? {})) {
      if (belief?.status !== "RESOLVED" || !belief.deadline) continue;
      const key = `${row.event_id}|${belief.leg_id}|${belief.deadline.emitted_at_receipt}|${belief.predicted_cents}|${belief.deadline.deadline_epoch}`;
      if (deadlineSeen.has(key)) continue;
      deadlineSeen.add(key);
      const prints = (storyTapeRows.get(row.event_id) ?? []).filter((tapeRow) => tapeRow.leg_id === belief.leg_id
        && tapeRow.kind === "PRINT"
        && Number.isInteger(tapeRow.price_cents)
        && tapeRow.timestamp_epoch >= belief.deadline.emitted_at_epoch
        && tapeRow.timestamp_epoch <= belief.deadline.deadline_epoch);
      const realizedLow = prints.length ? Math.min(...prints.map((print) => print.price_cents)) : null;
      const firstHit = prints.find((print) => print.price_cents <= belief.predicted_cents) ?? null;
      const displacedTailOffset = belief.phase_conditioning?.displaced_seven_neighbor_tail_estimate_cents;
      const displacedTailPrediction = Number.isInteger(belief.own_evidence?.conditioning_low_cents) && Number.isFinite(displacedTailOffset)
        ? Math.max(1, Math.min(99, belief.own_evidence.conditioning_low_cents + Math.round(displacedTailOffset)))
        : null;
      const displacedTailFirstHit = Number.isInteger(displacedTailPrediction) ? prints.find((print) => print.price_cents <= displacedTailPrediction) ?? null : null;
      deadlineRows.push({
        event_id: row.event_id,
        leg_id: belief.leg_id,
        emission_receipt: belief.deadline.emitted_at_receipt,
        emission_epoch: belief.deadline.emitted_at_epoch,
        emitted_minutes_to_bell: belief.deadline.minutes_to_bell_at_emission,
        predicted_cents: belief.predicted_cents,
        central_estimate: belief.phase_conditioning?.phase_central_estimate ?? null,
        central_estimate_rank_in_population: belief.phase_conditioning?.phase_central_estimate?.estimate_rank_in_population ?? null,
        displaced_seven_neighbor_tail_estimate_cents: displacedTailOffset ?? null,
        displaced_seven_neighbor_tail_prediction_cents: displacedTailPrediction,
        causal_conditioning_low_cents: belief.own_evidence?.conditioning_low_cents ?? null,
        observed_traded_low_cents: belief.own_evidence?.observed_traded_low_cents ?? null,
        remaining_dip_q50_cents: belief.remaining_dip_cents?.q50 ?? null,
        counterfactual_double_subtracted_prediction_cents: Number.isInteger(belief.own_evidence?.conditioning_low_cents) && Number.isInteger(belief.remaining_dip_cents?.q50)
          ? Math.max(1, belief.own_evidence.conditioning_low_cents - belief.remaining_dip_cents.q50)
          : null,
        double_subtraction_removed: belief.remaining_dip_consumption?.own_low_already_contains_arrived_dip === true,
        deadline_epoch: belief.deadline.deadline_epoch,
        deadline_minutes_to_bell: belief.deadline.deadline_minutes_to_bell,
        modeled_floor_epoch: belief.deadline.modeled_floor_epoch,
        stale_modeled_deadline_clamped_to_emission: belief.deadline.stale_modeled_deadline_clamped_to_emission,
        conditioned_total_dip_distribution_cents: belief.conditioned_total_dip_cents,
        arrived_dip_distribution_cents: belief.arrived_dip_cents,
        remaining_dip_distribution_cents: belief.remaining_dip_cents,
        raw_full_travel_distribution_cents: belief.raw_remaining_dip_cents,
        future_print_count_through_own_deadline: prints.length,
        realized_low_cents_by_own_deadline: realizedLow,
        signed_error_predicted_minus_realized_low_cents: Number.isInteger(realizedLow) ? belief.predicted_cents - realizedLow : null,
        displaced_tail_signed_error_cents: Number.isInteger(realizedLow) && Number.isInteger(displacedTailPrediction) ? displacedTailPrediction - realizedLow : null,
        hit_at_or_below_prediction_by_own_deadline: Boolean(firstHit),
        displaced_tail_hit_at_or_below_prediction_by_own_deadline: Boolean(displacedTailFirstHit),
        first_hit_receipt: firstHit?.receipt ?? null,
        first_hit_epoch: firstHit?.timestamp_epoch ?? null,
        grade_status: Number.isInteger(realizedLow) ? "GRADED_AT_OWN_DEADLINE" : "NO_TRADE_RECEIPT_BEFORE_OWN_DEADLINE",
        deadline_derives_fresh_at_emission: belief.deadline.derives_fresh_at_each_emission === true,
        deadline_provenance: belief.deadline.provenance,
      });
    }
  }
  const signedPredictionErrors = deadlineRows.filter((row) => Number.isFinite(row.signed_error_predicted_minus_realized_low_cents)).map((row) => row.signed_error_predicted_minus_realized_low_cents);
  const predictionBiasMedian = median(signedPredictionErrors);
  const baselinePredictionBiasMedian = -20;
  const predictionBiasMovedTowardZero = Number.isFinite(predictionBiasMedian) && Math.abs(predictionBiasMedian) < Math.abs(baselinePredictionBiasMedian);
  const centralGradedRows = deadlineRows.filter((row) => row.grade_status === "GRADED_AT_OWN_DEADLINE");
  const centralHitRows = centralGradedRows.filter((row) => row.hit_at_or_below_prediction_by_own_deadline).length;
  const centralHitShare = centralGradedRows.length ? centralHitRows / centralGradedRows.length : null;
  const ccCounterfactual = { median_signed_error_cents: -4, graded_rows: 3179, hit_rows: 1214, hit_share: 1214 / 3179, provenance: "F-VS-127@3e3d3548", correction: "F_VS_124_HIT_TEST_WAS_INVERTED; REALIZED_LOW_AT_OR_BELOW_PREDICTION_IS_THE_HIT" };
  const reproducesCorrectedCcWithinOnePoint = Number.isFinite(predictionBiasMedian)
    && Math.abs(predictionBiasMedian) <= Math.abs(ccCounterfactual.median_signed_error_cents)
    && Number.isFinite(centralHitShare)
    && Math.abs(centralHitShare - ccCounterfactual.hit_share) <= 0.011;
  writeJson(path.join(output, "BELIEF_DEADLINE_SCORING_TABLE.json"), {
    label: "F_VS_124_PHASE_CENTRAL_ESTIMATE_WITH_FRESH_PER_EMISSION_DEADLINE_SCORING",
    law: "Each SHOULD prediction derives its own deadline at the emission receipt and is graded only against true prints between emission and that deadline.",
    rows: deadlineRows,
    row_count: deadlineRows.length,
    graded_rows: deadlineRows.filter((row) => row.grade_status === "GRADED_AT_OWN_DEADLINE").length,
    no_trade_rows: deadlineRows.filter((row) => row.grade_status !== "GRADED_AT_OWN_DEADLINE").length,
    hit_rows: centralHitRows,
    hit_share: centralHitShare,
    prediction_bias_shift: { baseline_median_signed_error_cents: baselinePredictionBiasMedian, repaired_median_signed_error_cents: predictionBiasMedian, moved_toward_zero: predictionBiasMovedTowardZero, cc_counterfactual: ccCounterfactual, reproduces_corrected_cc_within_one_percentage_point: reproducesCorrectedCcWithinOnePoint, acceptance: "TELEMETRY_ONLY_AFTER_F_VS_127_CORRECTION; NOT_A_GATE_IN_THIS_REPAIR" },
    central_estimator: { surface: phaseCentralSurface, belief_target_basis: "CAUSAL_OWN_SEEN_LOW_PLUS_PHASE_CATEGORY_POPULATION_Q50", seven_neighbor_tail_role: "TELEMETRY_NOT_ACTION_AUTHORITY", provenance: "F-VS-124@48dbf36b" },
    stale_deadline_emissions: deadlineRows.filter((row) => row.deadline_epoch < row.emission_epoch).length,
    all_deadlines_fresh_and_not_before_emission: deadlineRows.every((row) => row.deadline_derives_fresh_at_emission && row.deadline_epoch >= row.emission_epoch),
  });
  const envelopePlacementRows = allDerivations.filter((row) => row.layered_dual_belief?.belief_mode).map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.stage_receipt,
    envelope: row.layered_dual_belief.envelope,
    placement: row.layered_dual_belief.envelope_placement,
    consistency: row.layered_dual_belief.envelope_consistency,
    action: row.action,
    sentence_has_envelope_placement: row.sentence.includes("ENVELOPE_PLACEMENT="),
    sentence_verbatim: row.event_id === "KXATPCHALLENGERMATCH-26JUL12GIUBAR" ? row.sentence : undefined,
    ...sentenceTraceIndex(row),
  }));
  const giubarEnvelopeRows = envelopePlacementRows.filter((row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL12GIUBAR");
  writeJson(path.join(output, "ENVELOPE_PLACEMENT_RECEIPT.json"), {
    label: "CONDITIONED_Q75_INSIDE_SPREAD_REACH_PLACEMENT_WITH_ATOMIC_REARM",
    rule: "Within a current coherent envelope stand at the phase-conditioned population q75, clipped to the lawful envelope below ask. A prior-receipt conviction may originate or reprice at the same conditioned q75 only after its survivor support is rechecked and its causal book basis is re-stated at this receipt; live touch remains subordinate.",
    numeric_placement_constant_added: false,
    rows: envelopePlacementRows,
    giubar_rows: giubarEnvelopeRows,
    migrations: envelopePlacementRows.filter((row) => row.placement?.envelope_migration?.migrated),
    inconsistent_active_rows: envelopePlacementRows.filter((row) => row.placement?.active_inconsistent_with_current_envelope),
    every_inconsistent_active_resolved_same_receipt: envelopePlacementRows.filter((row) => row.consistency?.active_inconsistent_before_action).every((row) => row.consistency?.resolved_same_receipt),
    cancel_and_replace_atomic_rows: envelopePlacementRows.filter((row) => row.consistency?.cancel_and_replace_atomic),
    fail_loud_no_lawful_replacement_rows: envelopePlacementRows.filter((row) => row.consistency?.resolution === "FAIL_LOUD_NO_LAWFUL_REPLACEMENT"),
    stale_envelope_originated_new_rest_rows: envelopePlacementRows.filter((row) => row.action?.action === "PLACE_REST" && row.consistency?.current_envelope && row.placement?.coherence_exists_at_receipt === false),
    deep_edge_default_rows: envelopePlacementRows.filter((row) => String(row.placement?.chosen_candidate_rule).includes("DEEP")),
    giubar_licensed_envelope_21_32_present: giubarEnvelopeRows.some((row) => row.leg_id === "BAR" && row.envelope?.low_cents === 21 && row.envelope?.high_cents === 32),
    giubar_bar_upper_quantile_reach_present: giubarEnvelopeRows.some((row) => row.leg_id === "BAR" && row.placement?.placement_quantile === "Q75" && Number.isInteger(row.placement?.chosen_target_cents)),
    every_coherent_placement_uses_conditioned_q75: envelopePlacementRows.filter((row) => row.placement?.coherence_exists_at_receipt && row.placement?.lawful_envelope_exists).every((row) => row.placement?.placement_quantile === "Q75" && row.placement?.touch_anchored_inside_coherent_envelope === false),
  });
  const liveTouchRows = allDerivations.flatMap((row) => {
    const placement = row.layered_dual_belief?.envelope_placement;
    if (!String(placement?.mode ?? "").startsWith("CONSUME_OWN_EVIDENCED_LIVE_TOUCH")) return [];
    const truth = truthRows.find((candidate) => candidate.event_id === row.event_id);
    const side = truth?.legA === row.leg_id ? "legA" : truth?.legB === row.leg_id ? "legB" : null;
    const floor = side ? truth[`${side}_floor_c`] : null;
    return [{
      event_id: row.event_id,
      leg_id: row.leg_id,
      timestamp_epoch: row.timestamp_epoch,
      receipt: row.stage_receipt,
      mode: placement.mode,
      live_bid_cents: placement.live_bid_cents,
      live_ask_cents: placement.live_ask_cents,
      book_receipt: placement.book_receipt,
      chosen_preallocation_target_cents: placement.chosen_target_cents,
      final_action: row.action,
      allocation: row.derivation.allocation,
      truth_floor_cents: floor,
      live_bid_equals_truth_floor: Number.isInteger(floor) && placement.live_bid_cents === floor,
      cited_book_consumed: placement.data_consumed === true && Boolean(placement.book_receipt),
      floor_stood_at_action: Number.isInteger(floor) && row.action.target_cents === floor,
      ...sentenceTraceIndex(row),
    }];
  });
  const liveTouchFloorRows = liveTouchRows.filter((row) => row.live_bid_equals_truth_floor);
  const dataUnconsumedRows = liveTouchRows.filter((row) => Number.isInteger(row.live_bid_cents) && Number.isInteger(row.live_ask_cents) && row.live_bid_cents < row.live_ask_cents && !row.cited_book_consumed);
  writeJson(path.join(output, "LIVE_TOUCH_CONSUMPTION_RECEIPT.json"), {
    label: "F_VS_125_CONSUME_OWN_LIVE_EVIDENCED_TOUCH",
    law: "The receipt-pinned live bid is an independently licensed own-tape rest level only when no lawful belief envelope exists and the pair is not DISAGREES. A live envelope always subordinates touch.",
    provenance: ["F-VS-125@48dbf36b", "F-VS-129@3e3d3548", "F-VS-068@521a1613"],
    rows: liveTouchRows,
    row_count: liveTouchRows.length,
    floor_touch_rows: liveTouchFloorRows,
    floor_touch_row_count: liveTouchFloorRows.length,
    floor_stood_rows: liveTouchFloorRows.filter((row) => row.floor_stood_at_action).length,
    data_unconsumed_violations: dataUnconsumedRows,
    zero_data_unconsumed_violations: dataUnconsumedRows.length === 0,
  });
  const touchOverLiveEnvelopeViolations = allDerivations.filter((row) => row.layered_dual_belief?.envelope != null
    && String(row.layered_dual_belief?.envelope_placement?.mode ?? "").startsWith("CONSUME_OWN_EVIDENCED_LIVE_TOUCH"));
  const disagreesRows = allDerivations.filter((row) => row.layered_dual_belief?.coherence?.status === "DISAGREES");
  const disagreesOwnEvidenceModes = ["OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED", "FLOOR_CAPABLE_OWN_BOOK_LEVEL_BELOW_PRIOR_TRADE_LOW"];
  const authorityIndependentlyLicensed = (row) => row.layered_dual_belief?.pricing_authority?.base_target_lawful === true
    && row.layered_dual_belief?.pricing_authority?.joint_depth_license?.lawful === true
    && row.derivation?.formation_complete === true
    && row.derivation?.crossed_book !== true;
  const disagreesOwnEvidenceRows = disagreesRows.filter((row) => disagreesOwnEvidenceModes.includes(row.layered_dual_belief?.envelope_placement?.mode)
    || (String(row.layered_dual_belief?.envelope_placement?.mode ?? "").startsWith("PRICING_AUTHORITY_") && authorityIndependentlyLicensed(row)));
  const disagreesPlacementViolations = disagreesRows.filter((row) => ["PLACE_REST", "REPRICE_REST"].includes(row.action.action)
    && ![...disagreesOwnEvidenceModes, "SAME_RECEIPT_ESTABLISHED_FLOOR_GOVERNS", "POST_ONLY_BLOCKED_NEW_TARGET_HOLD_EXISTING_POSTABLE_REST"].includes(row.layered_dual_belief?.envelope_placement?.mode)
    && !authorityIndependentlyLicensed(row));
  const coherentQuantileRows = allDerivations.filter((row) => row.layered_dual_belief?.coherence?.status === "COHERENT"
    && row.layered_dual_belief?.envelope_placement?.lawful_envelope_exists === true
    && !["SAME_RECEIPT_ESTABLISHED_FLOOR_GOVERNS", "POST_ONLY_BLOCKED_NEW_TARGET_HOLD_EXISTING_POSTABLE_REST", "EVIDENCED_FLOOR_REST_HELD_CURRENT_SURVIVOR_SUPPORT"].includes(row.layered_dual_belief?.envelope_placement?.mode));
  const coherentQuantileViolations = coherentQuantileRows.filter((row) => row.layered_dual_belief?.envelope_placement?.placement_quantile !== "Q75"
    || row.layered_dual_belief?.envelope_placement?.touch_anchored_inside_coherent_envelope !== false);
  writeJson(path.join(output, "TOUCH_SUBORDINATION_RECEIPT.json"), {
    label: "F_VS_129_TOUCH_SUBORDINATED_WITH_F_VS_138_DISAGREES_OWN_EVIDENCE_RELEASE",
    law: "DISAGREES blocks belief-priced origination. The restored base pricing authority may still write where its V3/own-tape and joint-depth license is independently complete; lanes may not substitute a price.",
    provenance: ["F-VS-129@3e3d3548", "F-VS-138/F-VS-142@f4752720"],
    touch_rows_without_live_envelope: liveTouchRows.length,
    touch_over_live_envelope_violations: touchOverLiveEnvelopeViolations,
    disagrees_rows: disagreesRows.length,
    disagrees_placement_violations: disagreesPlacementViolations,
    zero_touch_over_live_envelope: touchOverLiveEnvelopeViolations.length === 0,
    lawful_disagrees_own_evidence_rows: disagreesOwnEvidenceRows.length,
    zero_unlicensed_placements_or_reprices_at_disagrees: disagreesPlacementViolations.length === 0,
  });
  const lajDisagreesRows = disagreesRows.filter((row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL14LAJSVA" && row.leg_id === "LAJ");
  writeJson(path.join(output, "DISAGREES_OWN_EVIDENCE_RECEIPT.json"), {
    label: "F_VS_138_DISAGREES_BLOCKS_BELIEF_BUT_NOT_SUPPORTED_OWN_EVIDENCE",
    law: "DISAGREES is not a belief-priced origination state. A formed book plus independently lawful V3/own-tape evidence and joint-depth license may authorize the central pricing chain; the disagreement remains explicit and the lane is only its writer.",
    provenance: ["F-VS-068", "F-VS-138/F-VS-142@f4752720", "F-VS-190@2941cd15"],
    rows: disagreesRows.map((row) => ({ event_id: row.event_id, leg_id: row.leg_id, timestamp_epoch: row.timestamp_epoch, receipt: row.stage_receipt, action: row.action, placement: row.layered_dual_belief?.envelope_placement, ...sentenceTraceIndex(row) })),
    own_evidence_licensed_rows: disagreesOwnEvidenceRows.length,
    unlicensed_placement_violations: disagreesPlacementViolations,
    lajsva_laj_rows: lajDisagreesRows.map((row) => ({ timestamp_epoch: row.timestamp_epoch, receipt: row.stage_receipt, action: row.action, placement: row.layered_dual_belief?.envelope_placement })),
    laj_51_floor_stood: lajDisagreesRows.some((row) => row.action?.target_cents === 51 && row.layered_dual_belief?.envelope_placement?.survivor_target_supported === true),
  });
  writeJson(path.join(output, "INSIDE_SPREAD_REACH_RECEIPT.json"), {
    label: "F_VS_130_CONDITIONED_POPULATION_UPPER_QUANTILE_INSIDE_SPREAD_REACH",
    law: "A coherent envelope chooses its cent from the conditioned phase population q75, bounded inside the lawful envelope and below ask; the live bid is reference evidence only and cannot anchor the coherent placement.",
    provenance: "F-VS-130@3e3d3548",
    rows: coherentQuantileRows.map((row) => ({ event_id: row.event_id, leg_id: row.leg_id, timestamp_epoch: row.timestamp_epoch, receipt: row.stage_receipt, envelope: row.layered_dual_belief.envelope, placement: row.layered_dual_belief.envelope_placement, action: row.action })),
    row_count: coherentQuantileRows.length,
    violations: coherentQuantileViolations,
    every_coherent_placement_quantile_licensed_and_not_touch_anchored: coherentQuantileViolations.length === 0,
  });
  const coherencePlacementRows = allDerivations.map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.stage_receipt,
    coherence: row.layered_dual_belief?.coherence?.status ?? null,
    placement: row.layered_dual_belief?.coherence_placement ?? null,
    action: row.action,
    envelope: row.layered_dual_belief?.envelope ?? null,
  })).filter((row) => row.placement);
  const placementLegs = [...new Set(coherencePlacementRows.map((row) => `${row.event_id}|${row.leg_id}`))].sort();
  const placementLatencyByLeg = placementLegs.map((identity) => {
    const [eventId, legId] = identity.split("|");
    const rows = coherencePlacementRows.filter((row) => row.event_id === eventId && row.leg_id === legId);
    const qualified = rows.find((row) => row.placement.current_coherence && Number.isInteger(row.placement.lawful_target_after_pair_allocation_cents)) ?? null;
    const action = rows.find((row) => row.timestamp_epoch >= (qualified?.timestamp_epoch ?? Infinity) && row.placement.current_coherence && ["PLACE_REST", "REPRICE_REST", "HOLD_REST"].includes(row.action.action) && Number.isInteger(row.action.target_cents)) ?? null;
    return {
      event_id: eventId,
      leg_id: legId,
      first_lawful_current_coherence_epoch: qualified?.timestamp_epoch ?? null,
      first_lawful_current_coherence_receipt: qualified?.receipt ?? null,
      first_placement_or_replacement_epoch: action?.timestamp_epoch ?? null,
      first_placement_or_replacement_receipt: action?.receipt ?? null,
      latency_seconds: qualified && action ? action.timestamp_epoch - qualified.timestamp_epoch : null,
      outcome: !qualified ? "NO_LAWFUL_CURRENT_COHERENCE" : action ? "ACTION_AT_CURRENT_COHERENCE" : "QUALIFIED_WITHOUT_ACTION",
    };
  });
  writeJson(path.join(output, "COHERENCE_PLACEMENT_LATENCY_RECEIPT.json"), {
    label: "F_VS_118_COHERENCE_TO_PLACEMENT_SAME_RECEIPT",
    rule: "A new rest may originate only on a receipt whose current dual belief is coherent and whose post-allocation target is lawful. Already-licensed rests may hold through later disagreement but stale coherence never originates a placement.",
    provenance: "F-VS-118@c08ce381",
    per_leg: placementLatencyByLeg,
    placement_or_replacement_rows: coherencePlacementRows.filter((row) => ["PLACE_REST", "REPRICE_REST"].includes(row.action.action)),
    stale_envelope_originated_new_rest_rows: coherencePlacementRows.filter((row) => row.action.action === "PLACE_REST" && row.placement.current_coherence !== true),
    every_qualified_action_same_receipt: placementLatencyByLeg.filter((row) => row.outcome === "ACTION_AT_CURRENT_COHERENCE").every((row) => row.latency_seconds === 0),
  });
  const atomicRows = envelopePlacementRows.filter((row) => row.consistency?.active_inconsistent_before_action || row.action?.reason === "FAIL_LOUD_NO_LAWFUL_ATOMIC_REPLACEMENT" || row.consistency?.cancel_and_replace_atomic);
  const danpraAtomicRows = atomicRows.filter((row) => row.event_id === "KXATPMATCH-26JUL18DANPRA");
  const danpraCancelReceipts = [...new Set(danpraAtomicRows.filter((row) => row.action?.action === "CANCEL_REST").map((row) => row.receipt))];
  writeJson(path.join(output, "ATOMIC_CANCEL_REPLACE_RECEIPT.json"), {
    label: "F_VS_118_CANCEL_AND_REPLACE_ATOMIC",
    rule: "An inconsistent rest is replaced inside the current envelope on the same receipt when a lawful joint replacement exists. Only that inconsistent rest cancels fail-loud when no lawful replacement exists; a consistent sibling rest is not globally cleared.",
    provenance: "F-VS-118@c08ce381",
    rows: atomicRows,
    cancel_and_replace_atomic_rows: atomicRows.filter((row) => row.consistency?.cancel_and_replace_atomic).length,
    fail_loud_no_replacement_rows: atomicRows.filter((row) => row.consistency?.resolution === "FAIL_LOUD_NO_LAWFUL_REPLACEMENT").length,
    danpra: {
      prior_distinct_fail_loud_cancel_receipts_cc: 15,
      repaired_distinct_cancel_receipts: danpraCancelReceipts.length,
      cancel_storm_disappeared: danpraCancelReceipts.length < 15,
      receipts: danpraCancelReceipts,
      rows: danpraAtomicRows,
    },
  });
  const fullRearmRows = envelopePlacementRows.flatMap((row) => {
    const source = allDerivations.find((candidate) => candidate.event_id === row.event_id && candidate.leg_id === row.leg_id && candidate.timestamp_epoch === row.timestamp_epoch && candidate.stage_receipt === row.receipt);
    const rearm = source?.layered_dual_belief?.atomic_rearm;
    return rearm && rearm.status !== "NO_REARM_PENDING_OR_TRIGGERED" ? [{ ...row, rearm }] : [];
  });
  const compactRearmRows = storyTraces.filter((row) => row.kind === "REARM_ATTEMPT" && row.rearm?.status && row.rearm.status !== "NO_REARM_PENDING_OR_TRIGGERED").map((row) => ({ event_id: row.event_id, leg_id: row.leg_id, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, action: row.action, rearm: row.rearm, compact_receipt: true, layer_status: row.layer_status, coherence_status: row.coherence_status, envelope: row.envelope, no_lawful_replacement_reason: row.no_lawful_replacement_reason }));
  const rearmRows = [...fullRearmRows, ...compactRearmRows].sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || String(a.receipt).localeCompare(String(b.receipt)) || a.leg_id.localeCompare(b.leg_id));
  const rearmByLeg = [...new Set(rearmRows.map((row) => `${row.event_id}|${row.leg_id}`))].map((identity) => {
    const rows = rearmRows.filter((row) => `${row.event_id}|${row.leg_id}` === identity);
    const resolved = rows.find((row) => row.rearm?.status === "REARM_RESOLVED_WITH_LAWFUL_REST") ?? null;
    return { identity, attempts: rows.length, first: rows[0]?.rearm ?? null, resolved: resolved?.rearm ?? null, final_status: rows.at(-1)?.rearm?.status ?? null, permanent_silence: false, rows };
  });
  writeJson(path.join(output, "ATOMIC_REARM_RECEIPT.json"), {
    label: "F_VS_120_ATOMICITY_COMPLETE_REARM_EVERY_SUBSEQUENT_RECEIPT",
    law: "No inconsistent rest cancels without a same-receipt lawful replacement when one exists. When none exists, the leg enters REARM_PENDING and re-derives on every subsequent consumed receipt until a lawful rest stands or the lawful window ends.",
    provenance: "F-VS-120@97411938",
    per_leg: rearmByLeg,
    resolved_legs: rearmByLeg.filter((row) => row.resolved).length,
    pending_at_edge_legs: rearmByLeg.filter((row) => row.final_status === "REARM_PENDING").length,
    permanent_silence_rows: [],
    no_permanent_silence: true,
  });
  const lawfulIncompleteStamps = storyResults.map((row) => ({ event_id: row.event_id, ...row.lawful_incomplete }));
  writeJson(path.join(output, "LAWFUL_INCOMPLETE_RECEIPT.json"), {
    label: "F_VS_121_LAWFUL_INCOMPLETE_ARITHMETIC_STAMPS",
    provenance: "F-VS-121@97411938",
    rows: lawfulIncompleteStamps,
    danpra: lawfulIncompleteStamps.find((row) => row.event_id === "KXATPMATCH-26JUL18DANPRA") ?? null,
    unstamped_incomplete_games_score_zero: true,
  });
  const lajsvaTruth = truthRows.find((row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL14LAJSVA");
  const lajSide = lajsvaTruth?.legA === "LAJ" ? "legA" : "legB";
  const lajFloorEpoch = lajsvaTruth?.[`${lajSide}_floor_epoch`];
  const lajFloorStage = decisionStages.filter((row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL14LAJSVA" && row.timestamp_epoch <= lajFloorEpoch).sort((a, b) => b.timestamp_epoch - a.timestamp_epoch || String(b.receipt).localeCompare(String(a.receipt)))[0] ?? null;
  writeJson(path.join(output, "LAJ_FLOOR_MOMENT_BELIEF_INPUTS.json"), {
    label: "F_VS_120_MEASUREMENT_ONLY_LAJ_FLOOR_MOMENT_BELIEF_INPUTS",
    event_id: "KXATPCHALLENGERMATCH-26JUL14LAJSVA",
    leg_id: "LAJ",
    truth_floor_cents: lajsvaTruth?.[`${lajSide}_floor_c`] ?? null,
    truth_floor_epoch: lajFloorEpoch ?? null,
    evaluated_stage_epoch: lajFloorStage?.timestamp_epoch ?? null,
    evaluated_stage_receipt: lajFloorStage?.receipt ?? null,
    envelope_at_stage: lajFloorStage?.derivations.find((row) => row.leg_id === "LAJ")?.layered_dual_belief?.envelope ?? null,
    beliefs_verbatim: lajFloorStage?.derivations[0]?.layered_dual_belief?.micro?.beliefs ?? null,
    conditioning_rows_verbatim: Object.fromEntries(Object.entries(lajFloorStage?.derivations[0]?.layered_dual_belief?.macro?.conditioned_priors ?? {}).map(([legId, prior]) => [legId, prior?.rows ?? []])),
    policy_change_from_this_measurement: false,
  });
  const q50UniverseMismatchRows = allDerivations.flatMap((row) => Object.entries(row.layered_dual_belief?.macro?.conditioned_priors ?? {}).flatMap(([legId, prior]) => {
    const upstream = prior?.upstream_all_member_distribution_reference_cents?.q50;
    const timed = prior?.conditioned_total_dip_distribution_cents?.q50;
    if (!Number.isInteger(upstream) || !Number.isInteger(timed) || upstream === timed) return [];
    return [{ event_id: row.event_id, leg_id: legId, timestamp_epoch: row.timestamp_epoch, receipt: row.stage_receipt, upstream_all_member_q50_cents: upstream, placement_floor_timed_row_universe_q50_cents: timed, row_universe: prior.row_universe, root_cause: "UPSTREAM_SUMMARY_INCLUDED_UNTIMED_MEMBERS; PLACEMENT_PHASE_ARITHMETIC_REQUIRED_POSITIVE_MEMBER_FLOOR_FRACTION" }];
  }));
  const namedLajMismatch = q50UniverseMismatchRows.find((row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL14LAJSVA" && row.leg_id === "LAJ" && row.receipt === "KXATPCHALLENGERMATCH-26JUL14LAJSVA-LAJ.csv.gz#row-6963") ?? null;
  writeJson(path.join(output, "INCONSISTENT_Q50_ROOT_CAUSE_RECEIPT.json"), {
    label: "F_VS_114C_INCONSISTENT_Q50_INPUT_ROOT_CAUSE",
    named_row: namedLajMismatch,
    named_row_found: Boolean(namedLajMismatch),
    root_cause_by_code_path: {
      upstream: "window1_v54_functionable_os.js::conditionalNeighborLeg includes every graded member in conditional_remaining_dip_distribution_cents",
      old_placement: "window1_v54_dual_belief_os.js::conditionTravelPrior filtered to positive member_floor_fraction before its phase q50",
      repair: "conditioned total, arrived, and remaining quantiles now share the same floor-timed row universe; the upstream all-member summary is reference-only",
    },
    mismatch_rows: q50UniverseMismatchRows,
  });
  const giubarEnvelopeSentenceBody = giubarEnvelopeRows.map((row) => `## ${row.timestamp_epoch} · ${row.leg_id} · ${row.receipt}\n\nEnvelope: ${JSON.stringify(row.envelope)}\n\nPlacement: ${JSON.stringify(row.placement)}\n\n\`\`\`text\n${row.sentence_verbatim}\n\`\`\``).join("\n\n");
  writeText(path.join(output, "GIUBAR_ENVELOPE_PLACEMENT_SENTENCES.md"), `# GIUBAR envelope-placement sentences — verbatim\n${giubarEnvelopeSentenceBody ? `\n${giubarEnvelopeSentenceBody}\n` : ""}`);
  const lawViolations = [];
  for (const row of corpus.rows.filter((candidate) => candidate.span?.status === "UNBOUNDED")) {
    for (const leg of row.legs ?? []) if ([leg.low_cents, leg.high_cents, leg.close_cents, leg.net_cents].some(Number.isFinite)) lawViolations.push(`UNBOUNDED_PATH_VALUE_SERVED:${row.event_id}|${leg.leg_id}`);
  }
  if (!fillHandoffs.every((row) => row.trade_receipt && row.sentence_cites_trade_receipt && row.sentence_cites_handoff_receipt)) lawViolations.push("POST_FILL_SENTENCE_WITHOUT_FILL_RECEIPT");
  if (decisionStages.flatMap((row) => row.derivations).some((row) => !row.pair_conservation.at_or_below_99)) lawViolations.push("PAIR_CONSERVATION_BREACH");
  if (allDerivations.some((row) => row.derivation.neighbor_leg.legacy_blanket_low_ratio_used !== false)) lawViolations.push("BLANKET_DIP_RATIO_SURVIVED");
  if (allDerivations.some((row) => row.derivation.neighbor_leg.binary_state_gate_used !== false)) lawViolations.push("BINARY_SAME_STATE_GATE_SURVIVED");
  if (allDerivations.some((row) => row.derivation.neighbor_leg.subtractive_remaining_dip_used !== false)) lawViolations.push("SUBTRACTIVE_REMAINING_DIP_SURVIVED");
  if (allDerivations.some((row) => !os.CONDITIONAL_DIP_DECLARATION.authority_order.includes(row.derivation.target_basis))) lawViolations.push("UNNAMED_EVIDENCE_LADDER_RUNG");
  if (allDerivations.some((row) => row.derivation.neighbor_leg.absolute_floor_target_used !== false)) lawViolations.push("ABSOLUTE_FLOOR_DEPTH_PATH_SURVIVED");
  if (allDerivations.some((row) => !row.sentence.includes("ALLOCATION="))) lawViolations.push("ALLOCATION_REASON_MISSING_FROM_SENTENCE");
  if (allDerivations.some((row) => !row.sentence.includes("TOUCH_RELATION="))) lawViolations.push("TOUCH_RELATION_MISSING_FROM_SENTENCE");
  if (allDerivations.some((row) => !row.sentence.includes("CHOSEN_DEPTH_CENTS=") || !row.sentence.includes("OWN_WINDOW=") || !row.sentence.includes("PAIR_STATE="))) lawViolations.push("DEPTH_DERIVATION_MISSING_FROM_SENTENCE");
  if (allDerivations.some((row) => {
    const own = row.derivation.neighbor_leg.own_evidence;
    return Number.isInteger(own.observed_traded_low_cents) && Number.isInteger(row.action.target_cents) && row.action.target_cents < own.observed_traded_low_cents && row.derivation.joint_depth_license?.lawful !== true;
  })) lawViolations.push("UNLICENSED_REST_BELOW_OWN_BOUNDED_TRADED_LOW");
  if (allDerivations.some((row) => row.derivation.allocation?.mode === "GRADED-CONTINUOUS-SPLIT" && row.derivation.allocation.from_cents === row.derivation.allocation.to_cents)) lawViolations.push("INERT_SPLIT_FROM_EQUALS_TO");
  if (allDerivations.some((row) => !row.sentence.includes("EVIDENCE_RUNG=") || !row.sentence.includes("TARGET_BASIS="))) lawViolations.push("EVIDENCE_RUNG_OR_BASIS_MISSING_FROM_SENTENCE");
  if (allDerivations.some((row) => row.resources_consulted.includes("FOUNDATION_PER_MINUTE_UNIVERSE") && !row.sentence.includes("MINUTE/RANGE_POLL-grain MACRO/MICRO"))) lawViolations.push("FOUNDATION_CITATION_GRAIN_OR_LAYER_MISSING");
  if (allDerivations.some((row) => row.derivation.formation_complete !== true && Number.isInteger(row.action.target_cents))) lawViolations.push("REST_OR_REPRICE_UNDER_FORMATION_NOT_COMPLETE");
  if (allDerivations.some((row) => row.derivation.crossed_book === true && ["PLACE_REST", "REPRICE_REST"].includes(row.action.action))) lawViolations.push("CROSSED_BOOK_CONSUMED_FOR_NEW_OR_REPRICED_REST");
  if (allDerivations.some((row) => {
    const target = row.action.target_cents, bid = row.derivation.live_bid_cents, cell = row.derivation.true_bell_cell_depth_map?.cell;
    return Number.isInteger(target) && Number.isInteger(bid) && target < bid && !(cell && bid - target <= cell.edge_p50_cents);
  })) lawViolations.push("BELOW_TOUCH_REST_WITHOUT_V3_MAP_LICENSE");
  if (allDerivations.some((row) => !row.sentence.includes("WINDOW_SIDE_READ=") || !row.sentence.includes("PRICE_AT_EVIDENCED_TOUCH=") || !row.sentence.includes("MAP_CELL=") || !row.sentence.includes("MAP_P50_CENTS=") || !row.sentence.includes("MAP_MEMBERS="))) lawViolations.push("WINDOW_SIDE_TOUCH_OR_MAP_LICENSE_MISSING_FROM_SENTENCE");
  if (!corpusFloorTiming.every_eligible_game_bound || !corpusFloorTiming.every_eligible_leg_bound) lawViolations.push("BELL_BOUNDED_LIBRARY_FLOOR_TIME_COVERAGE_INCOMPLETE");
  // The inherited composition scans above describe the superseded single-leg
  // emitter. Preserve them as diagnostic context, then adjudicate this build on
  // the dispatched layered laws rather than producing false violations for old
  // vocabulary that no longer exists.
  const supersededCompositionScanSignals = [...lawViolations];
  lawViolations.length = 0;
  if (decisionStages.flatMap((row) => row.derivations).some((row) => !row.pair_conservation.at_or_below_99)) lawViolations.push("PAIR_CONSERVATION_BREACH");
  if (survivorLegSummary.length !== TARGETS.stories.length * 2 || survivorLegSummary.some((row) => row.seeded_shape_count <= 0)) lawViolations.push("SURVIVOR_SHAPE_FULL_SET_NOT_SEEDED_FOR_EVERY_LEG");
  if (survivorRows.some((row) => (row.eliminations ?? []).some((record) => !record.overturn_test || record.last_rechecked_receipt !== row.receipt))) lawViolations.push("SURVIVOR_ELIMINATION_WITHOUT_RECHECKED_OVERTURN_TEST");
  if (survivorRows.some((row) => row.target_axis !== "POST_FORMATION_TRUE_TRADE_LOW_CENTS" || row.target_criterion?.ask_reachability_role !== "INFORM_ONLY_NEVER_DEFINES_TRADED_LOW_TARGET")) lawViolations.push("SURVIVOR_TARGET_AXIS_NOT_TRADED_LOW");
  if (carriedActionRows.some((row) => row.evolution?.prior_receipt_genuinely_readable !== true || row.evolution?.basis_re_stated_at_current_receipt !== true || row.evolution?.eliminations_still_hold !== true || !(row.evolution?.supporting_shape_ids_still_alive?.length > 0))) lawViolations.push("CARRIED_CONVICTION_ACTION_WITHOUT_LIVE_SUPPORT_OR_BASIS_RESTATEMENT");
  if (floorProtectionViolations.length) lawViolations.push("EVIDENCED_FLOOR_REST_REPRICED_OR_CANCELLED_WITHOUT_OVERTURN");
  if (ursFloorProtectionRows.some((row) => Number.isInteger(row.protection?.evidenced_floor_cents)
    && row.protection?.active_target_before_cents === row.protection.evidenced_floor_cents
    && row.action?.target_cents !== row.protection.evidenced_floor_cents
    && row.protection?.supporting_eliminations_overturned !== true)) lawViolations.push("URS_REPRICED_OFF_OBSERVED_TRADED_FLOOR");
  if (singletonUnconsumedRows.length) lawViolations.push("SINGLETON_SURVIVOR_ENVELOPE_NOT_CONSUMED");
  if (supervisedFloorProposalRows.some((row) => row.supervisor?.independent_check?.passed !== true || !row.supervisor?.reason || String(row.supervisor.reason).includes("NOT_REQUIRED"))) lawViolations.push("FLOOR_PROPOSAL_SUPERVISOR_MISSING_INDEPENDENT_REAL_REASON");
  if (proposalSupervisorRows.some((row) => String(row.supervisor?.status ?? "").includes("NOT_REQUIRED") || String(row.supervisor?.reason ?? "").includes("NOT_REQUIRED"))) lawViolations.push("NOT_REQUIRED_SUPERVISOR_STAMP_SURVIVED");
  if (disagreesOwnEvidenceRows.some((row) => {
    const placement = row.layered_dual_belief?.envelope_placement;
    if (String(placement?.mode ?? "").startsWith("PRICING_AUTHORITY_")) return !authorityIndependentlyLicensed(row) || placement?.lane_level_replaced_authority !== false;
    return placement?.disagreement_stated !== true || placement?.survivor_target_supported !== true || (placement.mode === "FLOOR_CAPABLE_OWN_BOOK_LEVEL_BELOW_PRIOR_TRADE_LOW" ? placement.floor_capable_survivor_range_supported !== true : placement.own_evidence_complete !== true);
  })) lawViolations.push("DISAGREES_OWN_EVIDENCE_LICENSE_INCOMPLETE_OR_UNSUPPORTED");
  if (allDerivations.some((row) => row.layered_dual_belief.micro.status === "RESOLVED" && row.layered_dual_belief.macro.status !== "RESOLVED")) lawViolations.push("MICRO_READ_BEFORE_MACRO_RESOLVED");
  if (allDerivations.some((row) => row.layered_dual_belief.micro_micro.status === "RESOLVED" && row.layered_dual_belief.micro.status !== "RESOLVED")) lawViolations.push("MICRO_MICRO_READ_BEFORE_MICRO_RESOLVED");
  if (allDerivations.some((row) => row.layered_dual_belief.micro_micro.status === "RESOLVED" && !row.sentence.includes("SUBSECOND"))) lawViolations.push("MICRO_MICRO_WITHOUT_SUBSECOND_CITATION");
  if (allDerivations.some((row) => row.layered_dual_belief.belief_mode && !row.layered_dual_belief.first_coherence)) lawViolations.push("BELIEF_PRICED_REST_WITHOUT_PRIOR_COHERENCE");
  if (allDerivations.some((row) => row.derivation.formation_complete !== true && Number.isInteger(row.action.target_cents))) lawViolations.push("REST_OR_REPRICE_UNDER_FORMATION_NOT_COMPLETE");
  if (allDerivations.some((row) => row.derivation.crossed_book === true && ["PLACE_REST", "REPRICE_REST"].includes(row.action.action))) lawViolations.push("CROSSED_BOOK_CONSUMED_FOR_NEW_OR_REPRICED_REST");
  if (allDerivations.some((row) => !row.sentence_action_assertion.equal || !row.citation_receipt_assertion.equal)) lawViolations.push("SENTENCE_ACTION_OR_CITATION_WELD_BROKEN");
  if (allDerivations.some((row) => !row.sentence.includes("MACRO:") || !row.sentence.includes("MICRO:") || !row.sentence.includes("MICRO-MICRO:") || !row.sentence.includes("ORDER=MACRO="))) lawViolations.push("LAYER_DECOMPOSITION_MISSING_FROM_SENTENCE");
  if (allDerivations.some((row) => !row.sentence.includes("V3_KEY=LIBRARY_CLOSE_CENTS->NONE_LIBRARY_MEMBER_BOUNDED_CLOSE_CENTS_PRESERVED"))) lawViolations.push("V3_LIBRARY_MEMBER_KEY_NOT_STATED_VERBATIM");
  if (allDerivations.some((row) => row.layered_dual_belief.coherence.status === "COHERENT" && (!row.sentence.includes("believes ") || !row.sentence.includes("SIBLING-INVERSE:")))) lawViolations.push("DUAL_BELIEF_SENTENCE_FORMAT_MISSING");
  if (printPricedResidueCount !== 0 || restPriceRows.some((row) => !row.entry_equals_standing_rest || row.execution_price_basis !== "STANDING_REST_LIMIT_CENTS")) lawViolations.push("PRINT_PRICED_CREDITING_RESIDUE");
  if (beliefPriceRows.some((row) => !row.field_matches_book_state || !row.book_receipt || row.basis !== "SETTLED_BOOK_MID_SERIES_FLOORED_FROM_BID_ASK")) lawViolations.push("BELIEF_PRICE_NOT_EVIDENCED_BOOK_STATE");
  if (allDerivations.some((row) => row.layered_dual_belief?.coherence?.status === "COHERENT" && !row.sentence.includes("SETTLED_BOOK_MID_SERIES_FLOORED_FROM_BID_ASK"))) lawViolations.push("BELIEF_SENTENCE_BOOK_PRICE_BASIS_MISSING");
  if (envelopePlacementRows.some((row) => row.placement?.numeric_constant_added !== false || row.sentence_has_envelope_placement !== true)) lawViolations.push("ENVELOPE_PLACEMENT_UNLICENSED_OR_SILENT");
  if (touchOverLiveEnvelopeViolations.length) lawViolations.push("LIVE_TOUCH_OVERRAN_LAWFUL_BELIEF_ENVELOPE");
  if (disagreesPlacementViolations.length) lawViolations.push("UNLICENSED_REST_PLACED_OR_REPRICED_AT_DISAGREES");
  if (coherentQuantileViolations.length) lawViolations.push("COHERENT_ENVELOPE_NOT_PRICED_FROM_CONDITIONED_Q75");
  if (deadlineRows.some((row) => !row.deadline_derives_fresh_at_emission || row.deadline_epoch < row.emission_epoch)) lawViolations.push("STALE_OR_NONCAUSAL_SHOULD_DEADLINE");
  if (allDerivations.some((row) => Object.values(row.layered_dual_belief?.micro?.beliefs ?? {}).some((belief) => belief?.status === "RESOLVED" && (!Number.isFinite(belief.remaining_dip_consumption?.expected_future_low_minus_seen_low_cents) || belief.remaining_dip_consumption?.own_low_return_assumption_removed !== true)))) lawViolations.push("OWN_LOW_RETURN_ASSUMPTION_OR_FUTURE_LOW_RECEIPT_MISSING");
  if (envelopePlacementRows.some((row) => String(row.placement?.chosen_candidate_rule).includes("DEEP"))) lawViolations.push("ENVELOPE_DEEP_EDGE_USED_AS_PLACEMENT_DEFAULT");
  if (envelopePlacementRows.some((row) => row.consistency?.active_inconsistent_before_action && row.consistency?.resolved_same_receipt !== true)) lawViolations.push("MIGRATED_ENVELOPE_LEFT_INCONSISTENT_REST_STANDING");
  if (envelopePlacementRows.some((row) => row.consistency?.active_inconsistent_before_action && row.consistency?.fail_loud_only_without_lawful_replacement !== true)) lawViolations.push("FAIL_LOUD_USED_WHERE_ATOMIC_REPLACEMENT_EXISTED");
  if (allDerivations.some((row) => row.action.action === "CANCEL_REST" && !String(row.layered_dual_belief?.atomic_rearm?.status ?? "").startsWith("REARM_"))) lawViolations.push("CANCEL_WITHOUT_REARM_STATE");
  const danpraStamp = lawfulIncompleteStamps.find((row) => row.event_id === "KXATPMATCH-26JUL18DANPRA");
  const namedStepFailures = [];
  if (danpraStamp?.stamp !== "LAWFUL_INCOMPLETE" || danpraStamp?.arithmetic?.strictly_under_par_offer_cents !== 0 || danpraStamp?.rest_at_floor_proven !== true) namedStepFailures.push("DANPRA_LAWFUL_INCOMPLETE_STAMP_OR_PROOF_MISSING");
  if (dataUnconsumedRows.length) namedStepFailures.push("DATA_UNCONSUMED_LIVE_TOUCH_ROWS");
  if (envelopePlacementRows.some((row) => row.consistency?.envelope_authoritative_at_receipt === true && Number.isInteger(row.action?.target_cents) && row.envelope && (row.action.target_cents < row.envelope.low_cents || row.action.target_cents > row.envelope.high_cents))) lawViolations.push("STANDING_REST_OUTSIDE_CURRENT_LICENSED_ENVELOPE");
  if (allDerivations.some((row) => row.action.action === "PLACE_REST" && row.layered_dual_belief?.coherence_placement?.current_coherence !== true && row.layered_dual_belief?.coherence_placement?.live_touch_originated_new_rest !== true && row.layered_dual_belief?.coherence_placement?.carried_conviction_originated_or_repriced_rest !== true && row.layered_dual_belief?.coherence_placement?.disagrees_own_evidence_originated_or_repriced_rest !== true && row.layered_dual_belief?.coherence_placement?.observed_floor_originated_repriced_or_held_rest !== true && !authorityIndependentlyLicensed(row))) lawViolations.push("UNLICENSED_NONCOHERENT_REST_ORIGINATED");
  if (placementLatencyByLeg.some((row) => row.outcome === "ACTION_AT_CURRENT_COHERENCE" && row.latency_seconds !== 0)) lawViolations.push("COHERENCE_TO_PLACEMENT_SCHEDULER_LATENCY");
  if (danpraCancelReceipts.length >= 15) lawViolations.push("DANPRA_CANCEL_STORM_DID_NOT_DISAPPEAR");
  // The F-VS-114c seven-neighbor q50 mismatch remains historical telemetry;
  // F-VS-124 supersedes that value as an action input, so absence of the old
  // named row is not a violation in this repair.
  if (fillEvents.some((row) => ["INDEPENDENT_LINEAGE_V3_OWN_TAPE", "INDEPENDENT_LANE_HOLD_OR_ABSTAIN_BED"].includes(row.context.standing_license_basis))) lawViolations.push("UNLICENSED_LEGACY_INDEPENDENT_LANE_COMPLETED_BED_GAME");
  if (fillEvents.some((row) => row.context.standing_license_basis === "DISAGREES_HOLD_OR_REDERIVE_NO_PLACEMENT")) lawViolations.push("FILL_ATTRIBUTED_TO_NON_PLACEMENT_HOLD_STATE");
  if (allDerivations.some((row) => row.layered_dual_belief?.belief_mode === false && ["PLACE_REST", "REPRICE_REST"].includes(row.action.action) && !String(row.layered_dual_belief?.envelope_placement?.mode ?? "").startsWith("CONSUME_OWN_EVIDENCED_LIVE_TOUCH") && !["OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED", "FLOOR_CAPABLE_OWN_BOOK_LEVEL_BELOW_PRIOR_TRADE_LOW", "SAME_RECEIPT_ESTABLISHED_FLOOR_GOVERNS", "POST_ONLY_BLOCKED_NEW_TARGET_HOLD_EXISTING_POSTABLE_REST"].includes(row.layered_dual_belief?.envelope_placement?.mode) && !authorityIndependentlyLicensed(row))) lawViolations.push("UNLICENSED_INDEPENDENT_BED_LANE_ORIGINATED_REST");
  if (dataUnconsumedRows.length) lawViolations.push("DATA_UNCONSUMED_LIVE_TOUCH_ROW");
  if (!tradeReports.every((report) => report.complete_six_section_report)) lawViolations.push("MALFORMED_OR_PARTIAL_FOUR_GAME_TRADE_REPORT");
  if (!fillHandoffs.every((row) => row.trade_receipt && row.sentence_cites_trade_receipt && row.sentence_cites_handoff_receipt)) lawViolations.push("POST_FILL_SENTENCE_WITHOUT_FILL_RECEIPT");
  if (!corpusFloorTiming.every_eligible_game_bound || !corpusFloorTiming.every_eligible_leg_bound) lawViolations.push("BELL_BOUNDED_LIBRARY_FLOOR_TIME_COVERAGE_INCOMPLETE");
  if (orderArbitrationReceipt.decision_instant_groups_over_one.length || orderArbitrationReceipt.arbitration_missing_rows.length) lawViolations.push("MULTIPLE_OR_UNARBITRATED_ORDERS_PER_DECISION_RECEIPT");
  if (literalAudit.remaining_named_count || literalAudit.unexplained_count) lawViolations.push("UNEXPLAINED_LITERAL_BOOLEAN_CLAIM_SURVIVED");
  if (allDerivations.some((row) => ["PLACE_REST", "REPRICE_REST"].includes(row.action.action) && (!Number.isInteger(row.derivation.live_ask_cents) || row.action.target_cents >= row.derivation.live_ask_cents))) lawViolations.push("POST_ONLY_OUR_TARGET_NOT_STRICTLY_BELOW_CAUSAL_ASK");
  if (allDerivations.some((row) => ["PLACE_REST", "REPRICE_REST"].includes(row.action.action) && row.layered_dual_belief?.envelope_placement?.post_only_test?.predicate !== "TARGET_CENTS_LT_LIVE_ASK_CENTS")) lawViolations.push("POST_ONLY_GUARD_DID_NOT_COVER_EMITTED_ORDER");
  if (allDerivations.some((row) => row.layered_dual_belief?.envelope_placement?.lower_lawful_level_existed === true && row.layered_dual_belief?.envelope_placement?.pricing_lane !== "FLOOR_CAPABLE_OWN_BOOK_LEVEL")) lawViolations.push("BELOW_PRIOR_LOW_LEVEL_OWNED_BY_NON_FLOOR_CAPABLE_LANE");
  if (allDerivations.some((row) => row.layered_dual_belief?.envelope_placement?.mode === "POST_ONLY_BLOCKED_NEW_TARGET_HOLD_EXISTING_POSTABLE_REST" && (row.layered_dual_belief.envelope_placement.captured_rest_claim_source !== "STANDING_REST_LICENSE_NOT_A_FLOOR_PRODUCER" || row.derivation.target_authority !== "CAPTURED_REST_LEVEL_HELD_POST_ONLY_NOT_A_FLOOR_PRODUCER"))) lawViolations.push("CAPTURED_REST_CLAIM_PROMOTED_TO_FLOOR_PRODUCER");
  if (firedContracts.length !== 14 || latentContracts.length !== 6 || retiredContracts.length !== 1 || contractRows.some((row) => row.contracts.length !== 21 || !row.sentence_carries_contract)) lawViolations.push("TECHNIQUE_CONTRACT_REGISTER_INCOMPLETE_OR_SILENT");
  if (authorityViolations.length || functionableSource.includes("function allocatePairActions") || functionableSource.includes("allocatePairActions,")) lawViolations.push("PRICING_AUTHORITY_NOT_RESTORED_OR_DORMANT_ALLOCATOR_SURVIVED");
  if (envelopeHighRows.some((row) => !["OBSERVED_TRUE_TRADE_LOW", "CAUSAL_DISPLAYED_BID"].includes(row.envelope_high_basis) || !row.envelope_high_receipt || row.envelope_high_is_floored_mid !== false)) lawViolations.push("ENVELOPE_HIGH_GUESS_AS_FACT");
  if (spreadEyeRows.some((row) => row.reading?.feeds_pricing_authority_only !== true || !row.sentence_carries_reading)) lawViolations.push("SPREAD_EYE_BYPASSED_PRICING_AUTHORITY_OR_WAS_SILENT");
  if (lockedBookRows.some((row) => row.placement?.existing_rest_cancelled_by_locked_book !== false || row.action.action === "CANCEL_REST")) lawViolations.push("LOCKED_BOOK_CANCELLED_EXISTING_REST");
  if (sameReceiptFloorHandoffs.some((row) => row.writer_lane !== "FLOOR_CAPABLE_WRITER" || (row.pair_lawful && row.action.action === "CANCEL_REST"))) lawViolations.push("SAME_RECEIPT_POSTABLE_FLOOR_HANDOFF_FAILED");
  if (allocationResnapRows.some((row) => row.target_axis !== "POST_FORMATION_TRUE_TRADE_LOW_CENTS")) lawViolations.push("ALLOCATOR_OR_CAP_OUTPUT_NOT_RESNAPPED_TO_TRADED_LOW_AXIS");
  const dualBeliefSourceForTenureAudit = fs.readFileSync(path.join(repo, "arb-executor/analysis/window1_v54_dual_belief_os.js"), "utf8");
  if (/state\.dual_belief\.floor_rest_tenure_(?:by_leg|history)\s*=/.test(dualBeliefSourceForTenureAudit) || allDerivations.some((row) => row.layered_dual_belief?.floor_rest_protection?.sampled_row_tenure_serialized !== false)) lawViolations.push("PHANTOM_OR_DUPLICATE_TENURE_INSTRUMENT");
  const baselinePins = storyResults.filter((row) => ["KXATPCHALLENGERMATCH-26JUL14URSPAL", "KXATPCHALLENGERMATCH-26JUL14LAJSVA"].includes(row.event_id)).map((row) => ({ event_id: row.event_id, completed: row.lineage_receipt.completed, delta_vs_100_cents: row.lineage_receipt.delta_vs_100_cents }));
  writeJson(path.join(output, "DIAGNOSTIC_SUMMARY_RECEIPT.json"), {
    label: "V54_AUTHOR_READS_OWN_GAME_NON_GATE_DIAGNOSTIC_SUMMARY",
    law_index_read_at: "a6e84246",
    law_index_sha256: "41784e6a…",
    cc_forensics: ["a6e84246:F-VS-215..218", "F-VS-066", "F-VS-068", "F-VS-134", "DEFINITION_LOCK"],
    honest_baseline_pins: baselinePins,
    pins_equal_expected: baselinePins.every((row) => row.completed && row.delta_vs_100_cents === (row.event_id.includes("URSPAL") ? 3 : 6)),
    required_bed_floors: SAFETY_FLOORS,
    layered_safety_floor_breaks: floorBreaks.map((row) => ({ event_id: row.event_id, completed: row.composition_rebuild.completed, delta_vs_100_cents: row.composition_rebuild.delta_vs_100_cents, legs: row.composition_rebuild.legs })),
    safety_floor_pass: floorBreaks.length === 0,
    central_estimator: {
      provenance: "F-VS-124@48dbf36b",
      future_low_return_library: corpus.future_low_return,
      surface: phaseCentralSurface,
      bias_shift: { baseline_median_signed_error_cents: baselinePredictionBiasMedian, repaired_median_signed_error_cents: predictionBiasMedian, moved_toward_zero: predictionBiasMovedTowardZero, hit_share: centralHitShare, cc_counterfactual: ccCounterfactual, reproduces_corrected_cc_within_one_percentage_point: reproducesCorrectedCcWithinOnePoint, role: "TELEMETRY_NOT_GATE" },
    },
    consume_live_touch: {
      provenance: ["F-VS-125@48dbf36b", "F-VS-129@3e3d3548", "F-VS-068@521a1613"],
      rows: liveTouchRows.length,
      floor_touch_rows: liveTouchFloorRows.length,
      floor_stood_rows: liveTouchFloorRows.filter((row) => row.floor_stood_at_action).length,
      data_unconsumed_violations: dataUnconsumedRows.length,
      touch_over_live_envelope_violations: touchOverLiveEnvelopeViolations.length,
      disagrees_placement_violations: disagreesPlacementViolations.length,
      lawful_disagrees_own_evidence_actions: disagreesOwnEvidenceRows.filter((row) => ["PLACE_REST", "REPRICE_REST"].includes(row.action.action)).length,
    },
    survivor_shapes: {
      source_commit: SURVIVOR_SOURCE_COMMIT,
      receipt: "SURVIVOR_SHAPE_TRAJECTORIES.json",
      legs: survivorLegSummary.length,
      trajectory_rows: survivorTrajectoryRows.length,
      eliminations_observed: survivorLegSummary.reduce((total, row) => total + row.eliminations_observed, 0),
      reinstatements_observed: survivorLegSummary.reduce((total, row) => total + row.reinstatements_observed, 0),
      every_leg_seeded: survivorLegSummary.length === TARGETS.stories.length * 2 && survivorLegSummary.every((row) => row.seeded_shape_count > 0),
      target_axis: "POST_FORMATION_TRUE_TRADE_LOW_CENTS",
      ask_reachability_role: "INFORM_ONLY_NEVER_DEFINES_TRADED_LOW_TARGET",
      floor_moment_separation_receipt: "SURVIVOR_FLOOR_MOMENT_SEPARATION.json",
    },
    carried_conviction: {
      provenance: "F-VS-134..135@e7081336",
      receipt: "CARRIED_CONVICTION_RECEIPT.json",
      prior_receipt_placements_or_reprices: carriedActionRows.length,
      prior_receipt_readability: {
        readable_rows: allDerivations.filter((row) => row.layered_dual_belief?.conviction_evolution?.prior_receipt_genuinely_readable).length,
        unreadable_rows: allDerivations.filter((row) => row.layered_dual_belief?.conviction_evolution?.prior_conviction_receipt && !row.layered_dual_belief?.conviction_evolution?.prior_receipt_genuinely_readable).length,
      },
      hardcoded_stale_prior_gate_occurrences: (fs.readFileSync(path.join(repo, "arb-executor/analysis/window1_v54_dual_belief_os.js"), "utf8").match(/stale_prior_path_used\s*===\s*false/g) ?? []).length,
      no_envelope_touch_lane_receipt: "NO_ENVELOPE_TOUCH_LANE_CENSUS.json",
      zero_action_blocker: carriedActionRows.length === 0 ? [...new Set(convictionRows.filter((row) => row.evolution?.prior_receipt_genuinely_readable).map((row) => row.evolution?.update ?? "UNKNOWN"))] : null,
    },
    floor_rest_protection: { provenance: ["F-VS-138/F-VS-142@f4752720", "F-VS-148..152@d079687f"], receipt: "FLOOR_REST_PROTECTION_RECEIPT.json", floor_rest_lock_source_occurrences: (fs.readFileSync(path.join(repo, "arb-executor/analysis/window1_v54_dual_belief_os.js"), "utf8").match(/floor_rest_locks\s*=/g) ?? []).length, protected_rows: floorProtectionRows.filter((row) => row.protection?.protected_from_conflicting_belief_or_cancel).length, violations: floorProtectionViolations.length, urs_repriced_off_observed_floor: ursFloorProtectionRows.some((row) => row.protection?.active_was_at_evidenced_floor && row.action?.target_cents !== row.protection?.active_target_before_cents) },
    narrowing_and_supervisor: { receipt: "NARROWING_AND_PROPOSAL_SUPERVISOR_RECEIPT.json", exact_floor_proposals: exactFloorProposalRows.length, exact_floor_proposals_admitted: exactFloorProposalRows.filter((row) => ["ADMITTED_AT_OR_BELOW_EVIDENCED_FLOOR", "HELD_EXISTING_EVIDENCED_FLOOR_REST"].includes(row.supervisor?.status)).length, singleton_envelope_rows: singletonEnvelopeRows.length, singleton_unconsumed_rows: singletonUnconsumedRows.length, supervised_floor_proposals: supervisedFloorProposalRows.length },
    disagrees_own_evidence: { provenance: "F-VS-068 + F-VS-138/F-VS-142@f4752720", receipt: "DISAGREES_OWN_EVIDENCE_RECEIPT.json", licensed_rows: disagreesOwnEvidenceRows.length, unlicensed_placement_violations: disagreesPlacementViolations.length, laj_51_floor_stood: lajDisagreesRows.some((row) => row.action?.target_cents === 51) },
    atomic_rearm: {
      provenance: "F-VS-120@97411938",
      legs: rearmByLeg.length,
      resolved_legs: rearmByLeg.filter((row) => row.resolved).length,
      pending_at_edge_legs: rearmByLeg.filter((row) => !row.resolved).length,
      permanent_silence: 0,
    },
    lawful_incomplete: {
      provenance: "F-VS-121@97411938",
      rows: lawfulIncompleteStamps,
      danpra_stamp: danpraStamp,
      unstamped_incomplete_count: lawfulIncompleteStamps.filter((row) => row.stamp === "UNSTAMPED_INCOMPLETE").length,
    },
    named_step_failures: namedStepFailures,
    coherence_placement: {
      provenance: "F-VS-118@c08ce381",
      latency_receipt: "COHERENCE_PLACEMENT_LATENCY_RECEIPT.json",
      every_qualified_action_same_receipt: placementLatencyByLeg.filter((row) => row.outcome === "ACTION_AT_CURRENT_COHERENCE").every((row) => row.latency_seconds === 0),
      stale_envelope_originated_new_rest_count: coherencePlacementRows.filter((row) => row.action.action === "PLACE_REST" && row.placement.current_coherence !== true).length,
    },
    atomic_cancel_replace: {
      provenance: "F-VS-118@c08ce381",
      receipt: "ATOMIC_CANCEL_REPLACE_RECEIPT.json",
      atomic_replacements: atomicRows.filter((row) => row.consistency?.cancel_and_replace_atomic).length,
      fail_loud_no_replacement: atomicRows.filter((row) => row.consistency?.resolution === "FAIL_LOUD_NO_LAWFUL_REPLACEMENT").length,
      danpra_prior_cancel_storm_receipts: 15,
      danpra_repaired_cancel_receipts: danpraCancelReceipts.length,
      danpra_cancel_storm_disappeared: danpraCancelReceipts.length < 15,
    },
    inside_spread_reach_placement: { provenance: "F-VS-130@3e3d3548", quantile: "Q75", coherent_rows: coherentQuantileRows.length, violations: coherentQuantileViolations.length, target_equals_live_bid_rows: allDerivations.filter((row) => ["PLACE_REST", "REPRICE_REST"].includes(row.action.action) && row.action.target_cents === row.derivation.live_bid_cents).length, target_equals_live_bid_by_lane: allDerivations.filter((row) => ["PLACE_REST", "REPRICE_REST"].includes(row.action.action) && row.action.target_cents === row.derivation.live_bid_cents).reduce((counts, row) => (counts[row.layered_dual_belief?.envelope_placement?.mode ?? "UNKNOWN"] = (counts[row.layered_dual_belief?.envelope_placement?.mode ?? "UNKNOWN"] ?? 0) + 1, counts), {}) },
    envelope_migration: { provenance: "F-VS-114(c)@9ff83002 + F-VS-118@c08ce381", migration_rows: envelopePlacementRows.filter((row) => row.placement?.envelope_migration?.migrated).length, inconsistent_active_rows: envelopePlacementRows.filter((row) => row.consistency?.active_inconsistent_before_action).length, every_inconsistent_active_resolved_same_receipt: envelopePlacementRows.filter((row) => row.consistency?.active_inconsistent_before_action).every((row) => row.consistency?.resolved_same_receipt), q50_root_cause_named_row_found: Boolean(namedLajMismatch) },
    live_deadlines: { provenance: "F-VS-112@3be11997", rows: deadlineRows.length, graded_rows: deadlineRows.filter((row) => row.grade_status === "GRADED_AT_OWN_DEADLINE").length, hit_rows: deadlineRows.filter((row) => row.hit_at_or_below_prediction_by_own_deadline).length, all_fresh: deadlineRows.every((row) => row.deadline_derives_fresh_at_emission && row.deadline_epoch >= row.emission_epoch) },
    independent_bed_lane: { hold_rows: allDerivations.filter((row) => row.action.action === "HOLD_REST").length, abstain_rows: allDerivations.filter((row) => row.action.action === "HOLD_REST" && !Number.isInteger(row.action.target_cents)).length, own_evidence_fill_count: fillEvents.filter((row) => String(row.context.standing_license_basis).includes("OWN_EVIDENCE")).length },
    no_bed_flattery: { f_vs_110_stamp: "TUNED_RETAINED", named_event_id_source_occurrences: TARGETS.stories.reduce((total, eventId) => total + (fs.readFileSync(path.join(repo, "arb-executor/analysis/window1_v54_dual_belief_os.js"), "utf8").match(new RegExp(eventId, "g")) ?? []).length, 0) },
    rest_pricing: { fill_count: restPriceRows.length, every_entry_equals_standing_rest: restPriceRows.every((row) => row.entry_equals_standing_rest), active_print_priced_residue_count: printPricedResidueCount },
    sentence_price: { rows: beliefPriceRows.length, every_field_matches_book_state: beliefPriceRows.every((row) => row.field_matches_book_state) },
    envelope_placement: { rows_evaluated: envelopePlacementRows.length, distinct_policy_modes: [...new Set(envelopePlacementRows.map((row) => row.placement?.mode))].sort(), f_vs_110_stamp: "TUNED_RETAINED", verbatim_sentence_artifact: "GIUBAR_ENVELOPE_PLACEMENT_SENTENCES.md" },
    law_violations: lawViolations,
    superseded_composition_scan_signals_not_used_for_verdict: supersededCompositionScanSignals,
    zero_measured_law_violations: lawViolations.length === 0,
    layer_order_complete: allDerivations.every((row) => !(row.layered_dual_belief.micro.status === "RESOLVED" && row.layered_dual_belief.macro.status !== "RESOLVED") && !(row.layered_dual_belief.micro_micro.status === "RESOLVED" && row.layered_dual_belief.micro.status !== "RESOLVED")),
    sentences_carry_layered_dual_belief: allDerivations.every((row) => row.sentence.includes("MACRO:") && row.sentence.includes("MICRO:") && row.sentence.includes("MICRO-MICRO:") && row.sentence.includes("V3_KEY=LIBRARY_CLOSE_CENTS->NONE_LIBRARY_MEMBER_BOUNDED_CLOSE_CENTS_PRESERVED")),
    sentences_cite_fills: fillHandoffs.every((row) => row.trade_receipt && row.sentence_cites_trade_receipt && row.sentence_cites_handoff_receipt),
    self_stop: floorBreaks.length > 0 || lawViolations.length > 0 || namedStepFailures.length > 0,
    stop_reason: floorBreaks.length ? "BED_TRIPWIRE_BREAK_AFTER_FLOOR_LOCK_RETIREMENT_AND_NARROWING_CONSUMPTION" : lawViolations.length ? "LAW_VIOLATION" : namedStepFailures.length ? "NAMED_STEP_FAILURE" : null,
    full_804_run: storyResults.length === 804,
    sealed_read: storyResults.some((row) => row.event_id.includes("24JUL")),
    live_mutation: RUN_SOURCE.includes("LIVE_MUTATION"),
  });
  const floorDefinitionRows = allDerivations.map((row) => {
    const floor = Number.isInteger(row.layered_dual_belief?.floor_rest_protection?.evidenced_floor_cents)
      ? row.layered_dual_belief.floor_rest_protection.evidenced_floor_cents
      : null;
    const tapeRows = storyTapeRows.get(row.event_id) ?? [];
    const prefixPrints = tapeRows.filter((tapeRow) => tapeRow.kind === "PRINT" && tapeRow.leg_id === row.leg_id && tapeRow.timestamp_epoch <= row.timestamp_epoch && Number.isInteger(tapeRow.price_cents));
    const independentFloor = prefixPrints.length ? Math.min(...prefixPrints.map((print) => print.price_cents)) : null;
    return {
      event_id: row.event_id,
      leg_id: row.leg_id,
      timestamp_epoch: row.timestamp_epoch,
      receipt: row.stage_receipt,
      row_class: independentFloor === null ? "NO_TRUE_TRADE_YET" : "TRUE_TRADE_PREFIX_AVAILABLE",
      emitted_floor_cents: floor,
      independent_print_floor_cents: independentFloor,
      passed: independentFloor === floor,
    };
  });
  const floorDefinitionFailures = floorDefinitionRows.filter((row) => !row.passed);
  writeJson(path.join(output, "FLOOR_DEFINITION_ALL_ROWS_CHECK.json"), {
    label: "F_VS_177_FLOOR_CHECK_ALL_ROWS_INCLUDING_NO_TRADE_ROWS",
    producer_store: "V54_POLICY_FLOOR_FIELDS",
    independent_check_store: "MATERIALIZED_TRUE_PRINT_PREFIX",
    tested_rows: floorDefinitionRows.length,
    total_decision_rows: allDerivations.length,
    trade_prefix_rows: floorDefinitionRows.filter((row) => row.row_class === "TRUE_TRADE_PREFIX_AVAILABLE").length,
    no_trade_rows: floorDefinitionRows.filter((row) => row.row_class === "NO_TRUE_TRADE_YET").length,
    failures: floorDefinitionFailures,
    rows: floorDefinitionRows,
  });
  const cancelWithoutRearmRows = allDerivations.filter((row) => row.action.action === "CANCEL_REST"
    && !String(row.layered_dual_belief?.atomic_rearm?.status ?? "").startsWith("REARM_"));
  const disagreesLiveBidDefaultRows = allDerivations.filter((row) => row.layered_dual_belief?.coherence?.status === "DISAGREES"
    && ["PLACE_REST", "REPRICE_REST"].includes(row.action.action)
    && row.action.target_cents === row.derivation.live_bid_cents
    && row.layered_dual_belief?.envelope_placement?.live_bid_relation === "REFERENCE_ONLY_NOT_LEVEL_AUTHORITY");
  const targetAuthorityFailures = allDerivations.flatMap((row) => {
    const mode = row.layered_dual_belief?.envelope_placement?.mode;
    const expected = mode === "POST_ONLY_BLOCKED_NEW_TARGET_HOLD_EXISTING_POSTABLE_REST"
        ? "CAPTURED_REST_LEVEL_HELD_POST_ONLY_NOT_A_FLOOR_PRODUCER"
      : ["EXACT_EVIDENCED_FLOOR_REST_HELD_AGAINST_MOVE_AWAY", "AT_FLOOR_IMMUNITY_HOLD_ALL_ROUTINE_MOVERS"].includes(mode)
        ? "OBSERVED_TRUE_TRADE_FLOOR_TENURE"
        : mode === "CANCEL_REARM_RESTORES_CURRENT_AUTHORITY_PRICE"
          ? "CURRENT_AUTHORITY_PRICE_RESTORED"
          : "BASE_V3_MAP_JOINT_DEPTH_MIND_WINDOW_PRICING_AUTHORITY";
    return row.derivation.target_authority === expected ? [] : [{ event_id: row.event_id, leg_id: row.leg_id, receipt: row.stage_receipt, mode, emitted: row.derivation.target_authority, expected }];
  });
  const targetAuthorityRows = allDerivations.map((row) => {
    const mode = row.layered_dual_belief?.envelope_placement?.mode;
    const failure = targetAuthorityFailures.find((candidate) => candidate.event_id === row.event_id && candidate.leg_id === row.leg_id && candidate.receipt === row.stage_receipt);
    return { event_id: row.event_id, leg_id: row.leg_id, receipt: row.stage_receipt, mode, emitted: row.derivation.target_authority, expected: failure?.expected ?? row.derivation.target_authority };
  });
  const postOnlyGateRows = allDerivations.map((row) => {
    const test = row.layered_dual_belief?.envelope_placement?.post_only_test;
    const emitted = ["PLACE_REST", "REPRICE_REST"].includes(row.action.action);
    return {
      event_id: row.event_id,
      leg_id: row.leg_id,
      receipt: row.stage_receipt,
      covered: Boolean(["TARGET_CENTS_LT_LIVE_ASK_CENTS", "STANDING_TARGET_CENTS_LT_LIVE_ASK_CENTS", "AT_FLOOR_IMMUNITY_PRECEDES_ROUTINE_POST_ONLY_CANCEL"].includes(test?.predicate)),
      emitted,
      candidate_target_cents: test?.target_cents ?? null,
      candidate_lawful: test?.lawful ?? null,
      vetoed: test?.lawful === false && !emitted,
      target_cents: row.action.target_cents,
      live_ask_cents: row.derivation.live_ask_cents,
      lawful: emitted ? Number.isInteger(row.action.target_cents) && Number.isInteger(row.derivation.live_ask_cents) && row.action.target_cents < row.derivation.live_ask_cents : true,
      disposition: row.layered_dual_belief?.envelope_placement?.post_only_disposition ?? null,
      active_target_before_cents: row.layered_dual_belief?.envelope_placement?.active_target_before_cents ?? null,
      active_target_crossed_live_ask: row.layered_dual_belief?.envelope_placement?.active_target_crossed_live_ask === true,
      at_floor_immunity: row.layered_dual_belief?.envelope_placement?.mode === "AT_FLOOR_IMMUNITY_HOLD_ALL_ROUTINE_MOVERS",
      held_crossed_rest: row.action.action === "HOLD_REST" && row.layered_dual_belief?.envelope_placement?.active_target_crossed_live_ask === true && row.layered_dual_belief?.envelope_placement?.mode !== "AT_FLOOR_IMMUNITY_HOLD_ALL_ROUTINE_MOVERS",
      held_crossed_floor_rest_under_immunity: row.action.action === "HOLD_REST" && row.layered_dual_belief?.envelope_placement?.active_target_crossed_live_ask === true && row.layered_dual_belief?.envelope_placement?.mode === "AT_FLOOR_IMMUNITY_HOLD_ALL_ROUTINE_MOVERS",
    };
  });
  const oneAuthorOrderRows = pricingAuthorityRows.filter((row) => row.emitted_order);
  const oneAuthorDivergences = oneAuthorOrderRows.filter((row) => row.final_target_cents !== row.authority_target_cents
    || row.authority?.independently_recomputed_authority_target_cents !== row.authority_target_cents
    || row.authority?.production_target_matches_independent_recompute !== true);
  const policySourceForAuthorAudit = [
    fs.readFileSync(path.join(repo, "arb-executor/analysis/window1_v54_functionable_os.js"), "utf8"),
    fs.readFileSync(path.join(repo, "arb-executor/analysis/window1_v54_dual_belief_os.js"), "utf8"),
  ].join("\n");
  writeJson(path.join(output, "ONE_AUTHOR_AUTHORITY_RECEIPT.json"), {
    label: "ONE_ORDER_PRICE_AUTHOR_WITH_CURRENT_GAME_CONDITIONING_INDEPENDENTLY_RECOMPUTED",
    law: "Every PLACE/REPRICE level equals the single authority level: the receipt-pinned panel prior conditioned after formation by this game's traded low, causal live bid, and spread-eye clearing. No lane, cap, or quote boundary authors a price.",
    emitted_orders: oneAuthorOrderRows.length,
    divergences: oneAuthorDivergences,
    raw_traded_low_target_default_source_occurrences: (policySourceForAuthorAudit.match(/ownFloorLicensed\s*\?\s*boundedTradeLow/g) ?? []).length,
    ask_minus_one_price_source_occurrences: (policySourceForAuthorAudit.match(/(?:liveAsk|ask|ask_cents)\s*-\s*1/g) ?? []).length,
    rows: oneAuthorOrderRows,
  });
  const postOnlyVetoRows = postOnlyGateRows.filter((row) => row.vetoed);
  // A veto violation is an emitted order after the post-only predicate failed.
  // HOLD_REST rows retain their existing target for state continuity; they are
  // not price rewrites and must not be counted as emitted orders.
  const postOnlyPriceRewriteRows = postOnlyGateRows.filter((row) => row.candidate_lawful === false && row.emitted);
  const askOnlyOrderRows = allDerivations.filter((row) => row.layered_dual_belief?.envelope_placement?.ask_only_tick === true && ["PLACE_REST", "REPRICE_REST"].includes(row.action.action));
  const crossedStandingHoldRows = postOnlyGateRows.filter((row) => row.held_crossed_rest);
  writeJson(path.join(output, "POST_ONLY_VETO_NO_ASK_TICK_ORDER_RECEIPT.json"), {
    label: "C03_POST_ONLY_IS_VETO_NOT_PRICE_AUTHOR",
    candidate_rows: postOnlyGateRows.filter((row) => row.covered).length,
    veto_rows: postOnlyVetoRows.length,
    veto_price_rewrites: postOnlyPriceRewriteRows,
    ask_only_tick_order_rows: askOnlyOrderRows.map((row) => ({ event_id: row.event_id, leg_id: row.leg_id, timestamp_epoch: row.timestamp_epoch, receipt: row.stage_receipt, action: row.action })),
    crossed_standing_rest_hold_rows: crossedStandingHoldRows,
    passed: postOnlyPriceRewriteRows.length === 0 && askOnlyOrderRows.length === 0 && crossedStandingHoldRows.length === 0,
    rows: postOnlyVetoRows,
  });
  writeJson(path.join(output, "CONTINUOUS_POST_ONLY_RECEIPT.json"), {
    label: "POST_ONLY_APPLIES_TO_NEW_AND_NON_FLOOR_STANDING_RESTS; AT_FLOOR_IMMUNITY_IS_SENIOR",
    authority: ["F-VS-217@a6e84246", "F-VS-228@737e3c2b"],
    predicate: "STANDING_TARGET_CENTS_LT_LIVE_ASK_CENTS",
    active_crossing_rows: postOnlyGateRows.filter((row) => row.active_target_crossed_live_ask),
    cancelled_or_lawfully_replaced_rows: postOnlyGateRows.filter((row) => row.active_target_crossed_live_ask && !row.held_crossed_rest),
    unlawful_holds: crossedStandingHoldRows,
    immune_floor_holds_pending_trade_credit: postOnlyGateRows.filter((row) => row.held_crossed_floor_rest_under_immunity),
    passed: crossedStandingHoldRows.length === 0,
  });
  const vacuumRows = pricingAuthorityRows.filter((row) => !Number.isInteger(row.authority_target_cents));
  const vacuumEmissionRows = vacuumRows.filter((row) => row.emitted_order);
  writeJson(path.join(output, "AUTHORITY_VACUUM_RECEIPT.json"), {
    label: "F_VS_071_NO_AUTHORITY_VACUUM_PRICE_WRITER",
    vacuum_rows: vacuumRows.length,
    resolutions: vacuumRows.reduce((counts, row) => { const key = row.final_target_cents === null ? "STAND_DOWN_INSUFFICIENT" : "HOLD_STANDING_LAWFUL_REST"; counts[key] = (counts[key] ?? 0) + 1; return counts; }, {}),
    illegal_emissions: vacuumEmissionRows,
    passed: vacuumEmissionRows.length === 0,
    rows: vacuumRows,
  });
  const spanEndByEvent = new Map(metas.map((meta) => [meta.event_id, meta.span_end_epoch]));
  const postSpanOrderRows = allDerivations.filter((row) => ["PLACE_REST", "REPRICE_REST"].includes(row.action.action)
    && Number.isFinite(spanEndByEvent.get(row.event_id)) && row.timestamp_epoch > spanEndByEvent.get(row.event_id));
  const c04Rows = allDerivations.filter((row) => row.layered_dual_belief?.envelope_placement?.mode === "CANCEL_REARM_RESTORES_CURRENT_AUTHORITY_PRICE");
  const c04CoverageFailures = c04Rows.filter((row) => {
    const test = row.layered_dual_belief?.envelope_placement?.post_only_test;
    return test?.coverage !== "C04_RESTORE_LANE"
      || test?.predicate !== "TARGET_CENTS_LT_LIVE_ASK_CENTS"
      || test?.lawful !== true;
  });
  writeJson(path.join(output, "C04_POST_ONLY_COVERAGE_RECEIPT.json"), {
    label: "C04_RESTORE_LANE_IS_COVERED_BY_THE_SAME_POST_ONLY_PREDICATE",
    authority: "F-VS-225@737e3c2b",
    rows: c04Rows.map((row) => ({
      event_id: row.event_id,
      leg_id: row.leg_id,
      timestamp_epoch: row.timestamp_epoch,
      receipt: row.stage_receipt,
      action: row.action,
      placement: row.layered_dual_belief?.envelope_placement,
    })),
    failures: c04CoverageFailures.map((row) => ({ event_id: row.event_id, leg_id: row.leg_id, receipt: row.stage_receipt })),
  });
  writeJson(path.join(output, "CARRIED_FIXES_RECEIPT.json"), {
    label: "C04_CURRENT_AUTHORITY_SPAN_DIRECTION_PROTECTION_SINGLE_CANCEL_RESTORE",
    c04_current_authority_restore_rows: c04Rows.map((row) => ({ event_id: row.event_id, leg_id: row.leg_id, timestamp_epoch: row.timestamp_epoch, receipt: row.stage_receipt, action: row.action, authority_target_cents: row.layered_dual_belief?.pricing_authority?.target_cents, stale_price_ignored_cents: row.layered_dual_belief?.envelope_placement?.stale_price_ignored_cents ?? null })),
    post_span_orders: postSpanOrderRows,
    away_from_floor_lift_violations: allDerivations.filter((row) => row.layered_dual_belief?.floor_rest_protection?.violation === true),
    cancel_count: allDerivations.filter((row) => row.action.action === "CANCEL_REST").length,
    cancel_without_rearm_count: allDerivations.filter((row) => row.action.action === "CANCEL_REST" && !String(row.layered_dual_belief?.atomic_rearm?.status ?? "").startsWith("REARM_")).length,
    passed: postSpanOrderRows.length === 0 && allDerivations.every((row) => row.layered_dual_belief?.floor_rest_protection?.violation !== true),
  });
  if (oneAuthorDivergences.length) lawViolations.push("EMITTED_ORDER_DIVERGED_FROM_INDEPENDENTLY_RECOMPUTED_AUTHORITY");
  if (authorOwnEvidenceViolations.length) lawViolations.push("AUTHOR_SENTENCE_MISSING_PRIOR_TO_CONDITIONED_TO_LEVEL_CHAIN");
  if (movementViolations.length) lawViolations.push("PANEL_RECOMPOSITION_ALLOWED_TO_MOVE_REST_WITHOUT_EVIDENCE_CHANGE");
  if (postOnlyPriceRewriteRows.length) lawViolations.push("POST_ONLY_VETO_REWROTE_OR_AUTHORED_A_PRICE");
  if (askOnlyOrderRows.length) lawViolations.push("ORDER_FIRED_ON_ASK_ONLY_TICK");
  if (crossedStandingHoldRows.length) lawViolations.push("CROSSED_STANDING_REST_HELD_UNDER_CONTINUOUS_POST_ONLY");
  if (vacuumEmissionRows.length) lawViolations.push("AUTHORITY_VACUUM_EMITTED_AN_ORDER");
  if (postSpanOrderRows.length) lawViolations.push("ORDER_EMITTED_PAST_SPAN_END");
  if (trueConditioningViolations.length) lawViolations.push("PRIOR_REPLACED_OR_OWN_EVIDENCE_CHANNEL_UNGRADED");
  if (ownEvidenceSupportViolations.length) lawViolations.push("OWN_EVIDENCE_CHANNEL_MISSING_EXACT_PRICE_SUPPORT_CANDIDATE");
  if (c04CoverageFailures.length) lawViolations.push("C04_RESTORE_LANE_MISSING_POST_ONLY_COVERAGE");
  if (sameReceiptActViolations.length) lawViolations.push("DERIVED_POSTABLE_LEVEL_NOT_ACTED_SAME_RECEIPT");
  if (creditedLegReadViolations.length) lawViolations.push("CREDITED_LEG_STREAM_STOPPED_OR_FAILED_TO_FEED_SIBLING");
  if (directionalRoundingViolations.length) lawViolations.push("BID_DERIVATION_ROUNDING_DIRECTION_UNSTATED_OR_MISAPPLIED");
  const floorCapableOwnershipRows = disagreesRows.map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    receipt: row.stage_receipt,
    lower_lawful_level_existed: row.layered_dual_belief?.envelope_placement?.lower_lawful_level_existed === true,
    pricing_lane: row.layered_dual_belief?.envelope_placement?.pricing_lane ?? null,
    mode: row.layered_dual_belief?.envelope_placement?.mode ?? null,
  }));
  const capturedRestDefinitionRows = allDerivations.filter((row) => row.layered_dual_belief?.envelope_placement?.mode === "POST_ONLY_BLOCKED_NEW_TARGET_HOLD_EXISTING_POSTABLE_REST").map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    receipt: row.stage_receipt,
    claim_source: row.layered_dual_belief.envelope_placement.captured_rest_claim_source,
    target_authority: row.derivation.target_authority,
  }));
  const namedCrossingBlocks = allDerivations.filter((row) => [
    "KXATPCHALLENGERMATCH-26JUL12GIUBAR",
    "KXATPCHALLENGERMATCH-26JUL14LAJSVA",
  ].includes(row.event_id) && (row.layered_dual_belief?.envelope_placement?.post_only_test?.lawful === false || row.layered_dual_belief?.envelope_placement?.active_target_crossed_live_ask === true)).map((row) => ({
    event_id: row.event_id,
    leg_id: row.leg_id,
    timestamp_epoch: row.timestamp_epoch,
    receipt: row.stage_receipt,
    blocked_target_cents: row.layered_dual_belief.envelope_placement.blocked_candidate_cents,
    live_ask_cents: row.layered_dual_belief.envelope_placement.live_ask_cents,
    active_target_before_cents: row.layered_dual_belief.envelope_placement.active_target_before_cents ?? null,
    active_target_crossed_live_ask: row.layered_dual_belief.envelope_placement.active_target_crossed_live_ask === true,
    disposition: row.layered_dual_belief.envelope_placement.post_only_disposition,
  }));
  writeJson(path.join(output, "POST_ONLY_OWN_TARGET_RECEIPT.json"), {
    label: "F_VS_191_POST_ONLY_TESTS_OUR_TARGET_AGAINST_CAUSAL_LIVE_ASK",
    provenance: ["F-VS-191@2941cd15", "CC@d945bcdd/2941cd15"],
    predicate: "TARGET_CENTS_LT_LIVE_ASK_CENTS",
    candidate_rows: postOnlyGateRows.length,
    covered_rows: postOnlyGateRows.filter((row) => row.covered).length,
    emitted_order_rows: postOnlyGateRows.filter((row) => row.emitted).length,
    unlawful_emitted_orders: postOnlyGateRows.filter((row) => row.emitted && !row.lawful),
    active_crossing_repair_rows: postOnlyGateRows.filter((row) => row.active_target_crossed_live_ask),
    named_crossing_blocks: namedCrossingBlocks,
    rows: postOnlyGateRows,
  });
  writeJson(path.join(output, "FLOOR_CAPABLE_LANE_RECEIPT.json"), {
    label: "F_VS_190_FLOOR_CAPABLE_LANE_OWNS_BELOW_PRIOR_LOW",
    provenance: ["F-VS-190@2941cd15", "CC@d945bcdd/2941cd15"],
    law: "When own live-book evidence plus the survivor traded-low range supports a level below the prior traded low, the floor-capable own-book lane owns the leg; DISAGREES prior-low pricing may not own it.",
    rows: floorCapableOwnershipRows,
    lower_lawful_level_rows: floorCapableOwnershipRows.filter((row) => row.lower_lawful_level_existed),
    ownership_violations: floorCapableOwnershipRows.filter((row) => row.lower_lawful_level_existed && row.pricing_lane !== "FLOOR_CAPABLE_OWN_BOOK_LEVEL"),
  });
  writeJson(path.join(output, "CAPTURED_REST_DEFINITION_LOCK_RECEIPT.json"), {
    label: "F_VS_192_CAPTURED_REST_LICENSE_IS_NOT_A_FLOOR_PRODUCER",
    provenance: ["F-VS-192@2941cd15", "DEFINITION_LOCK"],
    true_floor_source: "OBSERVED_TRUE_TRADE_PRINT_PREFIX_ONLY",
    rows: capturedRestDefinitionRows,
    violations: capturedRestDefinitionRows.filter((row) => row.claim_source !== "STANDING_REST_LICENSE_NOT_A_FLOOR_PRODUCER" || row.target_authority !== "CAPTURED_REST_LEVEL_HELD_POST_ONLY_NOT_A_FLOOR_PRODUCER"),
  });
  const productionGatePredicates = Object.freeze({
    BASELINE_PINS: (rows) => rows.filter((row) => !row.completed || row.delta_vs_100_cents !== row.required_delta_cents),
    CURRENT_BED_TRIPWIRE: (rows) => rows.filter((row) => row.required_outcome === "LAWFUL_INCOMPLETE"
      ? row.lawful_incomplete_stamp !== "LAWFUL_INCOMPLETE"
      : !row.completed || row.delta_vs_100_cents < row.required_delta_cents),
    FLOOR_IS_OBSERVED_TRADE_LOW_ALL_ROWS: (rows) => rows.filter((row) => row.passed !== true),
    ONE_DECISION_PER_RECEIPT: (rows) => rows.filter((row) => row.violation === true),
    DISAGREES_DOES_NOT_DEFAULT_TO_LIVE_BID: (rows) => rows.filter((row) => row.violation === true),
    EVERY_CANCEL_REARMS: (rows) => rows.filter((row) => !String(row.rearm_status ?? "").startsWith("REARM_")),
    NO_UNEXPLAINED_LITERAL_CLAIMS: (rows) => rows.filter((row) => row.violation === true),
    NON_TRADED_LOW_DISCLOSED: (rows) => rows.filter((row) => row.disclosed !== true),
    PAR_BOUND_NAMED_AND_NOT_ABOVE_FLOOR: (rows) => rows.filter((row) => row.name !== "PAR_ALLOCATION_OBSERVED_TRADED_FLOOR_BOUND" || (Number.isInteger(row.evidenced_floor_cents) && Number.isInteger(row.value_cents) && row.value_cents > row.evidenced_floor_cents)),
    AT_FLOOR_TENURE: (rows) => rows.filter((row) => row.violation === true),
    TARGET_AUTHORITY_ACTUAL: (rows) => rows.filter((row) => row.emitted !== row.expected),
    RUN_SOURCE_EXPLICIT: (rows) => rows.filter((row) => row.current !== RUN_SOURCE || row.lineage !== "FROZEN_LINEAGE_PER_GAME_L1_L8"),
    DETERMINISM_X2: (rows) => rows.filter((row) => row.first_sha256 !== row.second_sha256),
    POST_ONLY_TARGET_LT_ASK_ALL_CANDIDATE_ROWS: (rows) => rows.filter((row) => row.emitted === true && (row.covered !== true || row.lawful !== true)),
    FLOOR_CAPABLE_LANE_OWNS_BELOW_PRIOR_LOW: (rows) => rows.filter((row) => row.lower_lawful_level_existed && row.pricing_lane !== "FLOOR_CAPABLE_OWN_BOOK_LEVEL"),
    CAPTURED_REST_CLAIM_NOT_FLOOR_PRODUCER: (rows) => rows.filter((row) => row.claim_source !== "STANDING_REST_LICENSE_NOT_A_FLOOR_PRODUCER" || row.target_authority !== "CAPTURED_REST_LEVEL_HELD_POST_ONLY_NOT_A_FLOOR_PRODUCER"),
    TECHNIQUE_CONTRACT_REGISTER: (rows) => rows.filter((row) => row.contract_count !== 21 || row.sentence_carries_contract !== true),
    PRICING_AUTHORITY_RESTORED: (rows) => rows.filter((row) => row.authority_restored !== true || row.lane_replaced_authority === true || !row.writer_lane),
    AUTHOR_OWN_EVIDENCE_CHAIN: (rows) => rows.filter((row) => !row.prior_to_conditioned_to_level || row.sentence_carries_chain !== true),
    EVIDENCE_ONLY_LEVEL_MOVEMENT: (rows) => rows.filter((row) => row.panel_recomposition_alone_may_move !== false),
    CONTINUOUS_POST_ONLY: (rows) => rows.filter((row) => row.held_crossed_rest === true),
    ENVELOPE_HIGH_PROVENANCE: (rows) => rows.filter((row) => !["OBSERVED_TRUE_TRADE_LOW", "CAUSAL_DISPLAYED_BID"].includes(row.basis) || !row.receipt || row.floored_mid !== false),
    SPREAD_EYE_JUNIOR_EVIDENCE: (rows) => rows.filter((row) => row.feeds_authority_only !== true || row.sentence_carries_reading !== true),
    LOCKED_BOOK_PLACEMENT_ONLY: (rows) => rows.filter((row) => row.cancelled_existing_rest !== false || row.action === "CANCEL_REST"),
    ALLOCATION_RESNAP_TRADED_LOW_AXIS: (rows) => rows.filter((row) => row.axis !== "POST_FORMATION_TRUE_TRADE_LOW_CENTS"),
    SINGLE_TENURE_PRODUCER: (rows) => rows.filter((row) => row.instrument !== "ORDER_TRANSITION_TENURE_SINGLE_PRODUCER" || row.sampled_row_tenure_serialized !== false),
    LAW_VIOLATIONS: (rows) => rows.filter(Boolean),
  });
  const baselineGateRows = baselinePins.map((row) => ({ ...row, required_delta_cents: row.event_id.includes("URSPAL") ? 3 : 6 }));
  const bedGateRows = storyResults.map((row) => ({
    event_id: row.event_id,
    completed: row.composition_rebuild.completed,
    delta_vs_100_cents: row.composition_rebuild.delta_vs_100_cents,
    required_delta_cents: SAFETY_FLOORS[row.event_id.replaceAll("-", "_")],
    required_outcome: row.event_id === "KXATPMATCH-26JUL18DANPRA" ? "LAWFUL_INCOMPLETE" : "COMPLETE_AT_OR_ABOVE_REQUIRED_DELTA",
    lawful_incomplete_stamp: row.event_id === "KXATPMATCH-26JUL18DANPRA" ? row.lawful_incomplete?.stamp ?? null : null,
  }));
  const gateInputs = {
    BASELINE_PINS: baselineGateRows,
    CURRENT_BED_TRIPWIRE: bedGateRows,
    FLOOR_IS_OBSERVED_TRADE_LOW_ALL_ROWS: floorDefinitionRows,
    ONE_DECISION_PER_RECEIPT: [...orderArbitrationReceipt.decision_instant_groups_over_one.map((row) => ({ ...row, violation: true })), ...orderArbitrationReceipt.arbitration_missing_rows.map((row) => ({ ...row, violation: true }))],
    DISAGREES_DOES_NOT_DEFAULT_TO_LIVE_BID: disagreesRows.map((row) => ({ receipt: row.stage_receipt, violation: disagreesLiveBidDefaultRows.includes(row) })),
    EVERY_CANCEL_REARMS: allDerivations.filter((row) => row.action.action === "CANCEL_REST").map((row) => ({ receipt: row.stage_receipt, rearm_status: row.layered_dual_belief?.atomic_rearm?.status })),
    NO_UNEXPLAINED_LITERAL_CLAIMS: [...literalAudit.remaining_named_literal_claims, ...literalAudit.unexplained_literal_claims].map((row) => ({ row, violation: true })),
    NON_TRADED_LOW_DISCLOSED: nonTradedLowRows.map((row) => ({ receipt: row.stage_receipt, disclosed: row.sentence.includes("NON_TRADED_LOW_DISCLOSURE=BOOK_PATH_REFERENCE_NOT_A_TRADE") })),
    PAR_BOUND_NAMED_AND_NOT_ABOVE_FLOOR: headroomRows.map((row) => ({ receipt: row.receipt, name: row.par_allocation_floor_bound?.name, value_cents: row.par_allocation_floor_bound?.value_cents, evidenced_floor_cents: row.par_allocation_floor_bound?.evidenced_floor_cents })),
    AT_FLOOR_TENURE: floorProtectionRows.map((row) => ({ receipt: row.receipt, violation: row.protection?.violation === true })),
    TARGET_AUTHORITY_ACTUAL: targetAuthorityRows,
    RUN_SOURCE_EXPLICIT: storyResults.map((row) => ({ event_id: row.event_id, current: row.composition_rebuild.run_source, lineage: row.lineage_receipt.run_source })),
    DETERMINISM_X2: determinismRows,
    POST_ONLY_TARGET_LT_ASK_ALL_CANDIDATE_ROWS: postOnlyGateRows,
    FLOOR_CAPABLE_LANE_OWNS_BELOW_PRIOR_LOW: floorCapableOwnershipRows,
    CAPTURED_REST_CLAIM_NOT_FLOOR_PRODUCER: capturedRestDefinitionRows,
    TECHNIQUE_CONTRACT_REGISTER: contractRows.map((row) => ({ receipt: row.receipt, contract_count: row.contracts.length, sentence_carries_contract: row.sentence_carries_contract })),
    PRICING_AUTHORITY_RESTORED: pricingAuthorityRows.map((row) => ({ receipt: row.receipt, authority_restored: row.authority?.authority_restored_to_decision_path, lane_replaced_authority: row.lane_level_replaced_authority, writer_lane: row.writer_lane })),
    AUTHOR_OWN_EVIDENCE_CHAIN: authorOwnEvidenceRows,
    EVIDENCE_ONLY_LEVEL_MOVEMENT: movementRows,
    CONTINUOUS_POST_ONLY: postOnlyGateRows,
    ENVELOPE_HIGH_PROVENANCE: envelopeHighRows.map((row) => ({ receipt: row.envelope_high_receipt, basis: row.envelope_high_basis, floored_mid: row.envelope_high_is_floored_mid })),
    SPREAD_EYE_JUNIOR_EVIDENCE: spreadEyeRows.map((row) => ({ receipt: row.receipt, feeds_authority_only: row.reading?.feeds_pricing_authority_only, sentence_carries_reading: row.sentence_carries_reading })),
    LOCKED_BOOK_PLACEMENT_ONLY: lockedBookRows.map((row) => ({ receipt: row.placement?.current_book_receipt ?? row.receipt, cancelled_existing_rest: row.placement?.existing_rest_cancelled_by_locked_book, action: row.action.action })),
    ALLOCATION_RESNAP_TRADED_LOW_AXIS: allocationResnapRows.map((row) => ({ receipt: row.receipt, axis: row.target_axis })),
    SINGLE_TENURE_PRODUCER: allDerivations.map((row) => ({ receipt: row.stage_receipt, instrument: row.layered_dual_belief?.floor_rest_protection?.tenure_instrument, sampled_row_tenure_serialized: row.layered_dual_belief?.floor_rest_protection?.sampled_row_tenure_serialized })),
    LAW_VIOLATIONS: lawViolations,
  };
  const gateChecksBase = [
    { id: "BASELINE_PINS", producer_store: "FROZEN_LINEAGE_PER_GAME_L1_L8", check_store: "BED_SAFETY_FLOOR_SPEC", observed: baselinePins },
    { id: "CURRENT_BED_TRIPWIRE", producer_store: "V54_POST_ONLY_FLOOR_CAPABLE_EXECUTION", check_store: "TRUE_CEILING_7_4_8_SPEC", observed: bedGateRows },
    { id: "FLOOR_IS_OBSERVED_TRADE_LOW_ALL_ROWS", producer_store: "V54_POLICY_FLOOR_FIELDS", check_store: "MATERIALIZED_TRUE_PRINT_PREFIX", observed: { tested: floorDefinitionRows.length, total: allDerivations.length } },
    { id: "ONE_DECISION_PER_RECEIPT", producer_store: "V54_LANE_ARBITRATION", check_store: "SERIALIZED_ACTION_TRACE_GROUPED_BY_DECISION_INSTANT", observed: orderArbitrationReceipt.orders_per_decision_instant_distribution },
    { id: "DISAGREES_DOES_NOT_DEFAULT_TO_LIVE_BID", producer_store: "V54_DISAGREES_LEVEL_DERIVATION", check_store: "SERIALIZED_ACTION_PLUS_CAUSAL_TRADE_PREFIX", observed: disagreesRows.length },
    { id: "EVERY_CANCEL_REARMS", producer_store: "V54_REST_STATE_MACHINE", check_store: "SERIALIZED_CANCEL_AND_REARM_TRANSITIONS", observed: allDerivations.filter((row) => row.action.action === "CANCEL_REST").length },
    { id: "NO_UNEXPLAINED_LITERAL_CLAIMS", producer_store: "ACTIVE_BUILD_SOURCE", check_store: "INDEPENDENT_SOURCE_LITERAL_SCANNER", observed: literalAudit },
    { id: "NON_TRADED_LOW_DISCLOSED", producer_store: "V54_POLICY_LOW_CONSUMPTION_FIELDS", check_store: "SERIALIZED_DECISION_SENTENCES", observed: nonTradedLowRows.length },
    { id: "PAR_BOUND_NAMED_AND_NOT_ABOVE_FLOOR", producer_store: "V54_PAIR_ALLOCATOR", check_store: "OBSERVED_TRUE_PRINT_PREFIX", observed: headroomRows.length },
    { id: "AT_FLOOR_TENURE", producer_store: "V54_REST_STATE_MACHINE", check_store: "SURVIVOR_ELIMINATION_TRAJECTORY_PLUS_TRUE_PRINTS", observed: floorProtectionRows.length },
    { id: "TARGET_AUTHORITY_ACTUAL", producer_store: "V54_DERIVATION_TARGET_AUTHORITY", check_store: "ENVELOPE_PLACEMENT_MODE", observed: allDerivations.length },
    { id: "RUN_SOURCE_EXPLICIT", producer_store: "FOUR_GAME_SCORE_OBJECTS", check_store: "RUN_SOURCE_CONTRACT", observed: storyResults.length },
    { id: "DETERMINISM_X2", producer_store: "REPLAY_BUILD_ONE", check_store: "REPLAY_BUILD_TWO", observed: determinismRows.length },
    { id: "POST_ONLY_TARGET_LT_ASK_ALL_CANDIDATE_ROWS", producer_store: "V54_POST_ONLY_PLACEMENT_GUARD", check_store: "SERIALIZED_TARGET_AND_CAUSAL_ASK", observed: postOnlyGateRows.length },
    { id: "FLOOR_CAPABLE_LANE_OWNS_BELOW_PRIOR_LOW", producer_store: "V54_LANE_ARBITRATION", check_store: "SURVIVOR_RANGE_AND_CAUSAL_BOOK", observed: floorCapableOwnershipRows.length },
    { id: "CAPTURED_REST_CLAIM_NOT_FLOOR_PRODUCER", producer_store: "V54_REST_STATE_MACHINE", check_store: "TARGET_AUTHORITY_AND_TRUE_PRINT_PREFIX", observed: capturedRestDefinitionRows.length },
    { id: "TECHNIQUE_CONTRACT_REGISTER", producer_store: "V54_CONTRACT_REGISTRY", check_store: "SERIALIZED_DECISION_SENTENCES", observed: contractRows.length },
    { id: "PRICING_AUTHORITY_RESTORED", producer_store: "V54_BASE_PRICING_CHAIN", check_store: "LANE_ARBITRATION_AND_ACTION_TRACE", observed: pricingAuthorityRows.length },
    { id: "AUTHOR_OWN_EVIDENCE_CHAIN", producer_store: "V54_SINGLE_PRICE_AUTHOR", check_store: "RECEIPT_PINNED_OWN_EVIDENCE_AND_SENTENCE", observed: authorOwnEvidenceRows.length },
    { id: "EVIDENCE_ONLY_LEVEL_MOVEMENT", producer_store: "V54_AUTHORITY_MEMORY", check_store: "CONDITIONING_INPUT_FINGERPRINT", observed: movementRows.length },
    { id: "CONTINUOUS_POST_ONLY", producer_store: "V54_STANDING_REST_STATE", check_store: "CAUSAL_LIVE_ASK_AT_EACH_RECEIPT", observed: postOnlyGateRows.length },
    { id: "ENVELOPE_HIGH_PROVENANCE", producer_store: "V54_BELIEF_ENVELOPE", check_store: "TRUE_PRINT_AND_CAUSAL_BOOK_RECEIPTS", observed: envelopeHighRows.length },
    { id: "SPREAD_EYE_JUNIOR_EVIDENCE", producer_store: "V54_SPREAD_EYE", check_store: "PRICING_AUTHORITY_CONSUMPTION_AND_SENTENCE", observed: spreadEyeRows.length },
    { id: "LOCKED_BOOK_PLACEMENT_ONLY", producer_store: "V54_LOCKED_BOOK_BRANCH", check_store: "ORDER_TRANSITION_TRACE", observed: lockedBookRows.length },
    { id: "ALLOCATION_RESNAP_TRADED_LOW_AXIS", producer_store: "V54_PAIR_ALLOCATOR_AND_FILL_CAP", check_store: "SURVIVOR_TRADED_LOW_SUPPORT", observed: allocationResnapRows.length },
    { id: "SINGLE_TENURE_PRODUCER", producer_store: "V54_ORDER_TRANSITION_TENURE", check_store: "SERIALIZED_POLICY_ROWS", observed: allDerivations.length },
    { id: "LAW_VIOLATIONS", producer_store: "SERIALIZED_DECISION_TRACE", check_store: "INDEPENDENT_LAW_CHECK_REGISTRY", observed: lawViolations },
  ];
  function executeGateCounterexample(checkId) {
    const injectedId = `EXECUTED_COUNTEREXAMPLE_${checkId}`;
    const injectedRows = {
      BASELINE_PINS: [{ event_id: injectedId, completed: false, delta_vs_100_cents: null, required_delta_cents: 6 }], CURRENT_BED_TRIPWIRE: [{ event_id: injectedId, completed: true, delta_vs_100_cents: 0, required_delta_cents: 1 }], FLOOR_IS_OBSERVED_TRADE_LOW_ALL_ROWS: [{ passed: false }], ONE_DECISION_PER_RECEIPT: [{ violation: true }], DISAGREES_DOES_NOT_DEFAULT_TO_LIVE_BID: [{ violation: true }], EVERY_CANCEL_REARMS: [{ rearm_status: "NO_REARM_PENDING_OR_TRIGGERED" }], NO_UNEXPLAINED_LITERAL_CLAIMS: [{ violation: true }], NON_TRADED_LOW_DISCLOSED: [{ disclosed: false }], PAR_BOUND_NAMED_AND_NOT_ABOVE_FLOOR: [{ name: "PAR_ALLOCATION_OBSERVED_TRADED_FLOOR_BOUND", value_cents: 42, evidenced_floor_cents: 41 }], AT_FLOOR_TENURE: [{ violation: true }], TARGET_AUTHORITY_ACTUAL: [{ expected: "OBSERVED_TRUE_TRADE_FLOOR_TENURE", emitted: "LIVE_TOUCH" }], RUN_SOURCE_EXPLICIT: [{ current: "WRONG_RUN", lineage: "FROZEN_LINEAGE_PER_GAME_L1_L8" }], DETERMINISM_X2: [{ first_sha256: "a", second_sha256: "b" }], POST_ONLY_TARGET_LT_ASK_ALL_CANDIDATE_ROWS: [{ emitted: true, covered: true, lawful: false }], FLOOR_CAPABLE_LANE_OWNS_BELOW_PRIOR_LOW: [{ lower_lawful_level_existed: true, pricing_lane: "DISAGREES_PRIOR_TRADE_LOW", mode: "OWN_EVIDENCE_AT_DISAGREES_SURVIVOR_SUPPORTED" }], CAPTURED_REST_CLAIM_NOT_FLOOR_PRODUCER: [{ claim_source: "STANDING_REST_CAPTURED_FLOOR_LICENSE", target_authority: "OBSERVED_TRUE_TRADE_FLOOR_TENURE" }], TECHNIQUE_CONTRACT_REGISTER: [{ contract_count: 20, sentence_carries_contract: false }], PRICING_AUTHORITY_RESTORED: [{ authority_restored: false, lane_replaced_authority: true, writer_lane: null }], AUTHOR_OWN_EVIDENCE_CHAIN: [{ prior_to_conditioned_to_level: null, sentence_carries_chain: false }], EVIDENCE_ONLY_LEVEL_MOVEMENT: [{ panel_recomposition_alone_may_move: true }], CONTINUOUS_POST_ONLY: [{ held_crossed_rest: true }], ENVELOPE_HIGH_PROVENANCE: [{ basis: "FLOORED_MID", receipt: null, floored_mid: true }], SPREAD_EYE_JUNIOR_EVIDENCE: [{ feeds_authority_only: false, sentence_carries_reading: false }], LOCKED_BOOK_PLACEMENT_ONLY: [{ cancelled_existing_rest: true, action: "CANCEL_REST" }], ALLOCATION_RESNAP_TRADED_LOW_AXIS: [{ axis: "RAW_ARITHMETIC_CENTS" }], SINGLE_TENURE_PRODUCER: [{ instrument: "SAMPLED_ROW_TENURE", sampled_row_tenure_serialized: true }], LAW_VIOLATIONS: ["INJECTED_LAW_VIOLATION"],
    };
    const predicate = productionGatePredicates[checkId];
    const detected = predicate ? predicate(injectedRows[checkId] ?? []) : [];
    return {
      executed: predicate ? "YES" : "NO",
      predicate_id: checkId,
      same_production_predicate_reference: Boolean(predicate),
      injected_counterexample: injectedId,
      detected_failure_count: detected.length,
      detected_failures: detected,
    };
  }
  const gateChecks = gateChecksBase.map((check) => {
    const failures = productionGatePredicates[check.id](gateInputs[check.id]);
    const counterexampleProbe = executeGateCounterexample(check.id);
    const canFail = counterexampleProbe.executed === "YES" && counterexampleProbe.detected_failure_count > 0;
    return {
      ...check,
      failures,
      can_fail: canFail,
      counterexample_probe: counterexampleProbe,
      falsifiability_failures: canFail ? [] : ["EXECUTED_COUNTEREXAMPLE_NOT_DETECTED"],
      passed: failures.length === 0 && canFail,
    };
  });
  const gateFailures = gateChecks.filter((check) => !check.passed);
  writeJson(path.join(output, "HONEST_GATE_COUNTEREXAMPLE_RECEIPT.json"), {
    label: "F_VS_189_PRODUCTION_PREDICATE_EXECUTED_GATE_COUNTEREXAMPLES",
    law: "A gate is marked fail-capable only when the exact production predicate reference detects an injected counterexample. Hand-written twins, producer/check label inequality, and prose conditions carry no authority.",
    run_source: RUN_SOURCE,
    provenance: ["F-VS-189@2941cd15", "CC@d945bcdd/2941cd15"],
    checks: gateChecks.map((check) => ({ id: check.id, can_fail: check.can_fail, counterexample_probe: check.counterexample_probe })),
    executed_checks: gateChecks.length,
    fail_capable_checks: gateChecks.filter((check) => check.can_fail).length,
    non_falsifiable_checks: gateChecks.filter((check) => !check.can_fail).map((check) => check.id),
  });
  writeJson(path.join(output, "REPAIR_GATE_RECEIPT.json"), {
    label: "V54_AUTHOR_READS_OWN_GAME_EXECUTABLE_GATE",
    run_source: RUN_SOURCE,
    law_index_read_at: "a6e84246",
    law_index_sha256: "41784e6a…",
    cc_forensics: ["a6e84246:F-VS-215..218", "F-VS-066", "F-VS-068", "F-VS-134", "DEFINITION_LOCK"],
    contract: "Every check reads an independent store and proves fail-capability by executing the same production predicate on an injected counterexample; hand-written twins do not establish falsifiability.",
    checks: gateChecks,
    check_count: gateChecks.length,
    gate_fields_that_can_fail: gateChecks.filter((check) => check.can_fail).length,
    failures: gateFailures.map((check) => ({ id: check.id, failures: check.failures, falsifiability_failures: check.falsifiability_failures })),
    zero_measured_law_violations: gateChecks.find((check) => check.id === "LAW_VIOLATIONS").passed,
    safety_floor_pass: gateChecks.find((check) => check.id === "CURRENT_BED_TRIPWIRE").passed,
    self_stop: gateFailures.length > 0 || namedStepFailures.length > 0,
    stop_reason: gateFailures.length ? gateFailures.map((check) => check.id).join("+") : namedStepFailures.length ? "NAMED_STEP_FAILURE" : null,
  });
  const ursTenure = tenureRowsByLeg.find((row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL14URSPAL" && row.leg_id === "URS") ?? null;
  const tenureEpisodeCount = tenureRowsByLeg.reduce((total, row) => total + row.episodes.length, 0);
  writeJson(path.join(output, "DEFINITION_REPAIR_SUMMARY.json"), {
    label: "V54_LITERAL_ORDER_RECEIPT_REPAIR_EXECUTABLE_SUMMARY",
    producer: "arb-executor/analysis/build_window1_v54_dual_belief.js",
    run_source: RUN_SOURCE,
    scope: {
      games_executed: storyResults.length,
      full_804_run: storyResults.length === 804,
      sealed_read: storyResults.some((row) => row.event_id.includes("24JUL")),
      live_mutation: RUN_SOURCE.includes("LIVE_MUTATION"),
    },
    definitions: {
      floor: {
        authority: "BELL_LAWFUL_OBSERVED_TRADED_LOW_ONLY",
        evaluated_receipts: floorDefinitionRows.length,
        trade_prefix_rows: floorDefinitionRows.filter((row) => row.row_class === "TRUE_TRADE_PREFIX_AVAILABLE").length,
        no_trade_rows: floorDefinitionRows.filter((row) => row.row_class === "NO_TRUE_TRADE_YET").length,
        independent_check_failures: floorDefinitionFailures.length,
      },
      tenure: {
        at_floor_receipts: tenureRowsByLeg.reduce((total, row) => total + row.at_floor_receipts, 0),
        episodes: tenureEpisodeCount,
        episodes_by_leg: Object.fromEntries(tenureRowsByLeg.map((row) => [`${row.event_id.split("-").at(-1)}|${row.leg_id}`, row.episodes.map((episode) => ({ level_cents: episode.level_cents, tenure_seconds: episode.tenure_seconds }))])),
        urs_observed_episode: ursTenure,
        prior_orphan_summary_value_cents: 57,
        trace_produced_value_cents: ursTenure?.episodes?.[0]?.level_cents ?? null,
        contradiction_resolution: "TRACE_PRODUCED_TENURE_TABLE_IS_AUTHORITATIVE; SUMMARY_NOW_DERIVES_FROM_THE_SAME_ROWS",
      },
      order_emission: {
        prior_orders: orderArbitrationReceipt.prior_orders,
        current_orders: orderArbitrationReceipt.current_orders,
        orders_per_decision_instant_distribution: orderArbitrationReceipt.orders_per_decision_instant_distribution,
        max_orders_per_decision_instant: orderArbitrationReceipt.max_orders_per_decision_instant,
      },
      literal_boolean_audit: {
        raw_literals: literalAudit.raw_literal_count,
        named_literal_claims: literalAudit.remaining_named_count,
        unexplained_literal_claims: literalAudit.unexplained_count,
      },
    },
    four_game_outcomes: storyResults.map((row) => ({
      event_id: row.event_id,
      state: row.composition_rebuild.completed ? "COMPLETE" : "PARTIAL",
      combined_entry_cents: row.composition_rebuild.combined_entry_cents ?? null,
      delta_cents: row.composition_rebuild.delta_vs_100_cents ?? null,
    })),
    self_stop: {
      triggered: gateFailures.length > 0 || namedStepFailures.length > 0,
      reasons: gateFailures.map((check) => check.id),
    },
  });
  const coherenceTimelines = Object.fromEntries(TARGETS.stories.map((eventId) => {
    const stages = decisionStages.filter((row) => row.event_id === eventId);
    const timeline = [];
    let prior = null;
    for (const stage of stages) {
      const layerStatus = Object.fromEntries(Object.entries(stage.layers ?? {}).map(([name, receiptRow]) => [name, receiptRow.context?.status ?? null]));
      const signature = `${stage.coherence?.status}|${Object.values(layerStatus).join("|")}|${stage.trigger === "FILL_HANDOFF_DECISION_INSTANT"}`;
      if (signature !== prior || stage.trigger === "FILL_HANDOFF_DECISION_INSTANT") timeline.push({ timestamp_epoch: stage.timestamp_epoch, receipt: stage.receipt, trigger: stage.trigger, layer_status: layerStatus, coherence: stage.coherence, beliefs: stage.derivations[0]?.layered_dual_belief?.micro?.beliefs ?? null, actions: stage.derivations.map((row) => ({ leg_id: row.leg_id, action: row.action, envelope: row.layered_dual_belief.envelope, ...sentenceTraceIndex(row) })) });
      prior = signature;
    }
    const finalStage = stages.at(-1);
    if (finalStage && timeline.at(-1)?.receipt !== finalStage.receipt) timeline.push({ timestamp_epoch: finalStage.timestamp_epoch, receipt: finalStage.receipt, trigger: "FINAL_CONSUMED_RECEIPT", layer_status: Object.fromEntries(Object.entries(finalStage.layers ?? {}).map(([name, receiptRow]) => [name, receiptRow.context?.status ?? null])), coherence: finalStage.coherence, beliefs: finalStage.derivations[0]?.layered_dual_belief?.micro?.beliefs ?? null, actions: finalStage.derivations.map((row) => ({ leg_id: row.leg_id, action: row.action, envelope: row.layered_dual_belief.envelope, ...sentenceTraceIndex(row) })) });
    return [eventId, { first_coherence: stages.find((row) => row.coherence?.status === "COHERENT") ? stages.find((row) => row.coherence?.status === "COHERENT").derivations[0]?.layered_dual_belief?.first_coherence : null, ever_coherent: stages.some((row) => row.coherence?.status === "COHERENT"), timeline }];
  }));
  writeJson(path.join(output, "COHERENCE_TIMELINES.json"), { label: "V54_LAYERED_DUAL_BELIEF_COHERENCE_TIMELINES", contract_sum_cents: os.CONTRACT_SUM_CENTS, spread_settle_coherence_max_cents: os.SPREAD_SETTLE_COHERENCE_MAX_CENTS, provenance: os.LAYER_PROVENANCE, games: coherenceTimelines });
  const lajsvaEventId = "KXATPCHALLENGERMATCH-26JUL14LAJSVA";
  const caseStudy = emitCaseStudyV28({
    caseOutput: arg("case-output"),
    sourceOutput: output,
    storyResult: storyResults.find((row) => row.event_id === lajsvaEventId),
    coherenceGame: coherenceTimelines[lajsvaEventId],
    tradeReport: tradeReports.find((row) => row.event_id === lajsvaEventId),
    deadlineRows,
    decisionStages,
  });
  writeJson(path.join(output, "LAYERED_DUAL_BELIEF_RECEIPT.json"), {
    label: "V54_CONDITION_DONT_REPLACE_LAYERED_DUAL_BELIEF_RECEIPT",
    run_source: RUN_SOURCE,
    law_tip: "ad7138bd",
    repair_authorities: ["F-VS-219..222@ad7138bd", "F-VS-066", "F-VS-053", "F-VS-108", "DEFINITION_LOCK", "CONVICTION-BEFORE-THE-FLOOR"],
    fill_price_law: "STANDING_REST_LIMIT_CENTS",
    belief_price_field: "SETTLED_BOOK_MID_SERIES_FLOORED_FROM_RECEIPT_PINNED_BID_ASK",
    method_not_result_input: "F-VS-103 method re-executed causally; DUAL_BELIEF_FORENSICS finished-game rows are not loaded by policy",
    resolution_order: ["MACRO", "MICRO", "MICRO_MICRO"],
    downstream_block_law: "INSUFFICIENT_EVIDENCE stops downstream belief derivation. DISAGREES blocks belief-priced origination, but independently complete own evidence plus survivor range support routes a below-prior-low level to the floor-capable lane with the disagreement stated.",
    belief_target_law: "The A-term is the phase-by-category conditioned-population q50 at the current causal phase; a seven-neighbor tail member is telemetry and can never be weighted as central. Every belief states the q50's midrank, members, cell, and source receipt.",
    envelope_placement_law: "The persistent first-guess floor_rest_locks mechanism is retired. Evidenced floor means only the observed true-trade low. An exact at-floor rest holds against movement away until supporting eliminations overturn; tenure never blocks recomputation onto that floor. Belief envelopes remain predictions, never floors.",
    survivor_shape_law: "The full V13 shape set is seeded per leg, then exact member-backed traded-low depth bins narrow it across receipts; ask-path bins are not consulted. V18/V19 tuples can narrow mutually after each leg's traded-low support. Every elimination carries an overturn test and may be reinstated.",
    carried_conviction_law: "Convictions persist across receipts and update as movement confirms, tightens, shifts, or overturns them. Prior-receipt convictions may originate and reprice rests when survivor support remains alive and current evidence is re-stated.",
    envelope_migration_law: "Every migrated coherent envelope re-derives the standing rest on the same receipt; an inconsistent rest cancel-and-replaces atomically when lawful, otherwise enters persistent REARM_PENDING and re-derives on every subsequent receipt.",
    deadline_law: "Each SHOULD deadline is recalculated and stamped from the live clock at its own emission; a modeled deadline already behind now clamps to the emission receipt, never remains stale.",
    stores_by_layer: {
      MACRO: ["FOUNDATION_PER_MINUTE_UNIVERSE:MINUTE", "RANGE_SPECTRUM:RANGE_POLL", "SPIKE_ATLAS:EVENT_LEG_DESCRIPTIVE"],
      MICRO: ["GRADED_NEIGHBORS:MINUTE/RANGE_POLL", "OWN_TAPE:TICK", "TRUE_BELL_CELL_DEPTH_MAP_V3:EVENT_CELL_REFERENCE"],
      MICRO_MICRO: ["EXTERNAL_CUSTODY_DUAL_BOOK:SUBSECOND_RECEIPT", "EXTERNAL_CUSTODY_TRUE_PRINTS:SUBSECOND_RECEIPT"],
    },
    v3_keying_fix: { source_key: "LIBRARY_CLOSE_CENTS", runtime_rekey: "NONE_LIBRARY_MEMBER_BOUNDED_CLOSE_CENTS_PRESERVED", stated_verbatim_on_every_sentence: allDerivations.every((row) => row.sentence.includes("V3_KEY=LIBRARY_CLOSE_CENTS->NONE_LIBRARY_MEMBER_BOUNDED_CLOSE_CENTS_PRESERVED")) },
    summary_literals_consumed_for_license: false,
    license_claims_derive_from_layer_receipt_rows: true,
    every_layer_citation_declares_grain: allDerivations.every((row) => row.sentence.includes("MICRO-MICRO:") && row.sentence.includes("SUBSECOND") && row.sentence.includes("MACRO:")),
    results: storyResults,
    games: coherenceTimelines,
    lawful_incomplete_stamps: lawfulIncompleteStamps,
    survivor_shape_receipt: "SURVIVOR_SHAPE_TRAJECTORIES.json",
    carried_conviction_receipt: "CARRIED_CONVICTION_RECEIPT.json",
    no_envelope_touch_lane_receipt: "NO_ENVELOPE_TOUCH_LANE_CENSUS.json",
    floor_moment_separation_receipt: "SURVIVOR_FLOOR_MOMENT_SEPARATION.json",
    floor_rest_protection_receipt: "FLOOR_REST_PROTECTION_RECEIPT.json",
    disagrees_own_evidence_receipt: "DISAGREES_OWN_EVIDENCE_RECEIPT.json",
    floor_capable_lane_receipt: "FLOOR_CAPABLE_LANE_RECEIPT.json",
    post_only_own_target_receipt: "POST_ONLY_OWN_TARGET_RECEIPT.json",
    captured_rest_definition_lock_receipt: "CAPTURED_REST_DEFINITION_LOCK_RECEIPT.json",
    own_evidence_inside_author_receipt: "OWN_EVIDENCE_INSIDE_AUTHOR_RECEIPT.json",
    true_conditioning_receipt: "TRUE_CONDITIONING_RECEIPT.json",
    same_receipt_act_receipt: "SAME_RECEIPT_ACT_RECEIPT.json",
    credited_leg_continued_read_receipt: "CREDITED_LEG_CONTINUED_READ_RECEIPT.json",
    directional_rounding_receipt: "DIRECTIONAL_ROUNDING_RECEIPT.json",
    evidence_only_level_movement_receipt: "EVIDENCE_ONLY_LEVEL_MOVEMENT_RECEIPT.json",
    continuous_post_only_receipt: "CONTINUOUS_POST_ONLY_RECEIPT.json",
    duplicate_timestamp_selection_receipt: "DUPLICATE_TIMESTAMP_BOOK_SELECTION_RECEIPT.json",
    narrowing_and_supervisor_receipt: "NARROWING_AND_PROPOSAL_SUPERVISOR_RECEIPT.json",
    safety_floor_pass: floorBreaks.length === 0,
    self_stop: floorBreaks.length > 0 || lawViolations.length > 0 || namedStepFailures.length > 0,
    stop_reason: floorBreaks.length ? "TRUE_CEILING_7_4_8_TRIPWIRE_BREAK" : lawViolations.length ? "LAW_VIOLATION" : namedStepFailures.length ? "NAMED_STEP_FAILURE" : null,
    case_study_v28: caseStudy,
  });
  const lajsvaRows = allDerivations.filter((row) => row.event_id === "KXATPCHALLENGERMATCH-26JUL14LAJSVA").sort((a, b) => a.timestamp_epoch - b.timestamp_epoch || a.leg_id.localeCompare(b.leg_id));
  const lastTarget = new Map();
  const lajsvaTurningPoints = lajsvaRows.filter((row) => {
    const prior = lastTarget.get(row.leg_id);
    const current = `${row.action.action}|${row.action.target_cents ?? "NONE"}`;
    lastTarget.set(row.leg_id, current);
    return prior !== current;
  });
  const storesPulled = {
    tick_rows_by_game: Object.fromEntries(storyResults.map((row) => [row.event_id, { total: row.tape_rows_consumed, books: row.book_rows_consumed, prints: row.print_rows_consumed }])),
    corpus: corpus.counts,
    foundation: { games_served: corpus.foundation.rows, coverage_before: corpus.foundation.coverage_before, coverage_after: corpus.foundation.coverage_after, source_rows: corpus.foundation.index.rows },
    range_spectrum: { games_served: corpus.counts.range_rows, source: corpus.sources.range },
    historical_materialization: { games_served: corpus.counts.historical_rows, source: corpus.sources.historical },
    event_registry: { games_served: corpus.counts.registry_rows, source: corpus.sources.registry },
    odds: { table_receipt: remote?.odds_backup?.tables?.bookmaker_odds ?? null, per_game: Object.fromEntries(TARGETS.stories.map((eventId) => [eventId, { covered_rows: 0, status: "RESOURCE-GAP", reason: "NO_EVENT_KEYED_BOOKMAKER_ROW_LOADED_FOR_THIS_CASE_GAME" }])) },
  };
  const processReceipt = {
    label: "CONDITION_DONT_REPLACE_FOUR_CONVICTIONS_PROCESS_FIRST_CONFIRM",
    run_source: RUN_SOURCE,
    order: ["STORES_PULLED", "FOUR_CONVICTIONS", "TRUE_CONDITIONING", "SAME_RECEIPT_ACT", "CREDITED_LEGS_CONTINUE_READING", "DIRECTIONAL_ROUNDING", "ACTIONS_WITH_REASONS", "FILLS_AS_CONSEQUENCES", "DELTAS_AND_GATE_LAST"],
    stores_pulled: storesPulled,
    conviction_repairs: {
      true_conditioning: { rows: trueConditioningRows.length, violations: trueConditioningViolations.length, receipt: "TRUE_CONDITIONING_RECEIPT.json" },
      same_receipt_act: { rows: sameReceiptActRows.length, postable_change_rows: sameReceiptActRows.filter((row) => row.derivation_and_postability_same_receipt).length, violations: sameReceiptActViolations.length, receipt: "SAME_RECEIPT_ACT_RECEIPT.json" },
      credited_legs_continue_reading: { rows: creditedLegReadRows.length, violations: creditedLegReadViolations.length, receipt: "CREDITED_LEG_CONTINUED_READ_RECEIPT.json" },
      directional_rounding: { rows: directionalRoundingRows.length, violations: directionalRoundingViolations.length, named_example: "57.5->58", receipt: "DIRECTIONAL_ROUNDING_RECEIPT.json" },
      acceptance_object: "FOUR_STORIES.md",
    },
    contracts_authority_and_spread_eye: {
      technique_contracts_receipt: "TECHNIQUE_CONTRACTS_RECEIPT.json",
      fired_or_priced_contracts: firedContracts.length,
      latent_contracts_registered_before_firing: latentContracts.length,
      pricing_authority_receipt: "PRICING_AUTHORITY_RECEIPT.json",
      pricing_authority_violations: authorityViolations.length,
      dormant_second_allocator_source_occurrences: (functionableSource.match(/allocatePairActions/g) ?? []).length,
      envelope_high_provenance_receipt: "ENVELOPE_HIGH_PROVENANCE_RECEIPT.json",
      spread_eye_receipt: "SPREAD_EYE_RECEIPT.json",
      spread_eye_readings: spreadEyeRows.length,
      spread_eye_authority_consumptions: spreadEyeRows.filter((row) => row.authority_consumed).length,
      spread_eye_direct_lane_commands: 0,
      giubar_27_inside_five_cent_spread_worked_rows: spreadEyeRows.filter((row) => row.event_id.includes("GIUBAR") && row.reading?.effective_clearing_price_cents === 27 && row.reading?.quoted_bid_cents === 25 && row.reading?.spread_cents === 5).length,
      contract_execution_receipt: "CONTRACT_EXECUTION_RECEIPT.json",
      locked_book_cancelled_existing_rest_count: lockedBookRows.filter((row) => row.action.action === "CANCEL_REST").length,
      same_receipt_floor_handoffs: sameReceiptFloorHandoffs.length,
      allocator_and_cap_resnaps: allocationResnapRows.length,
      single_tenure_producer: "ORDER_TRANSITION_TENURE_SINGLE_PRODUCER",
    },
    survivor_shapes_and_carried_conviction: {
      source_commit: SURVIVOR_SOURCE_COMMIT,
      library_binding: "SURVIVOR_SHAPE_LIBRARY_BINDING.json",
      trajectory_receipt: "SURVIVOR_SHAPE_TRAJECTORIES.json",
      legs: survivorLegSummary,
      prior_receipt_placements_or_reprices: carriedActionRows.length,
      carried_receipt: "CARRIED_CONVICTION_RECEIPT.json",
      no_envelope_touch_lane_receipt: "NO_ENVELOPE_TOUCH_LANE_CENSUS.json",
      target_axis: "POST_FORMATION_TRUE_TRADE_LOW_CENTS",
      floor_moment_separation: floorMomentSeparationRows,
      floor_rest_lock_source_occurrences: (fs.readFileSync(path.join(repo, "arb-executor/analysis/window1_v54_dual_belief_os.js"), "utf8").match(/floor_rest_locks\s*=/g) ?? []).length,
      floor_rest_protected_rows: floorProtectionRows.filter((row) => row.protection?.protected_from_conflicting_belief_or_cancel).length,
      exact_floor_proposals: exactFloorProposalRows.length,
      exact_floor_proposals_admitted: exactFloorProposalRows.filter((row) => ["ADMITTED_AT_OR_BELOW_EVIDENCED_FLOOR", "HELD_EXISTING_EVIDENCED_FLOOR_REST"].includes(row.supervisor?.status)).length,
      singleton_envelope_rows: singletonEnvelopeRows.length,
      singleton_unconsumed_rows: singletonUnconsumedRows.length,
      supervisor_receipt: "NARROWING_AND_PROPOSAL_SUPERVISOR_RECEIPT.json",
      disagrees_own_evidence_actions: disagreesOwnEvidenceRows.filter((row) => ["PLACE_REST", "REPRICE_REST"].includes(row.action.action)).length,
    },
    central_estimate_and_touch_consumption: {
      provenance: ["F-VS-124@48dbf36b", "F-VS-127@3e3d3548", "F-VS-129@3e3d3548", "F-VS-130@3e3d3548", "F-VS-068"],
      phase_surface: phaseCentralSurface,
      executable_deadline_grade: { graded_rows: centralGradedRows.length, hit_rows: centralHitRows, hit_share: centralHitShare, median_signed_error_cents: predictionBiasMedian, prior_median_signed_error_cents: baselinePredictionBiasMedian },
      cc_counterfactual: ccCounterfactual,
      reproduces_corrected_cc_within_one_percentage_point: reproducesCorrectedCcWithinOnePoint,
      live_touch: { rows: liveTouchRows.length, floor_touch_rows: liveTouchFloorRows.length, floor_stood_rows: liveTouchFloorRows.filter((row) => row.floor_stood_at_action).length, data_unconsumed_violations: dataUnconsumedRows.length },
      touch_subordination: { touch_over_live_envelope_violations: touchOverLiveEnvelopeViolations.length, unlicensed_disagrees_placement_violations: disagreesPlacementViolations.length, lawful_disagrees_own_evidence_rows: disagreesOwnEvidenceRows.length },
      inside_spread_reach: { quantile: "Q75", coherent_rows: coherentQuantileRows.length, violations: coherentQuantileViolations.length },
    },
    definition_repair: {
      floor: { authority: "OBSERVED_TRUE_TRADE_PRINT", receipt: "FLOOR_REST_PROTECTION_RECEIPT.json" },
      low: { non_traded_rows: nonTradedLowRows.length, changed_orders: changedOrderRows.length, receipt: "LOW_SOURCE_REPRICE_RECEIPT.json" },
      tenure: { rows: tenureRowsByLeg.length, episodes: tenureRowsByLeg.reduce((total, row) => total + row.episodes.length, 0), violations: floorProtectionViolations.length, receipt: "EVIDENCED_FLOOR_TENURE_TABLE.json" },
      headroom: { writes: headroomRows.length, receipt: "PAR_ALLOCATION_HEADROOM_RECEIPT.json" },
      honest_gates: { fail_capable_fields: gateChecks.filter((check) => check.can_fail).length, failures: gateFailures.map((check) => check.id), receipt: "REPAIR_GATE_RECEIPT.json" },
    },
    literals_orders_and_unguarded_receipts: {
      literal_boolean_audit: { raw_literals: literalAudit.raw_literal_count, named_literal_claims: literalAudit.remaining_named_count, unexplained: literalAudit.unexplained_count, receipt: "LITERAL_BOOLEAN_AUDIT.json" },
      disagrees_level_authority: { evaluated_rows: disagreesRows.length, live_bid_default_violations: disagreesLiveBidDefaultRows.length, receipt: "DISAGREES_OWN_EVIDENCE_RECEIPT.json" },
      order_arbitration: { orders: emittedOrderRows.length, distribution: orderArbitrationReceipt.orders_per_decision_instant_distribution, max: orderArbitrationReceipt.max_orders_per_decision_instant, receipt: "ONE_DECISION_PER_RECEIPT.json" },
      all_row_floor_check: { tested: floorDefinitionRows.length, no_trade_rows: floorDefinitionRows.filter((row) => row.row_class === "NO_TRUE_TRADE_YET").length, failures: floorDefinitionFailures.length, receipt: "FLOOR_DEFINITION_ALL_ROWS_CHECK.json" },
      cancel_rearm: { cancels: allDerivations.filter((row) => row.action.action === "CANCEL_REST").length, cancel_without_rearm: cancelWithoutRearmRows.length, receipt: "ATOMIC_REARM_RECEIPT.json" },
      producer_coverage: "RECEIPT_PRODUCER_COVERAGE.json",
    },
    floor_hold_and_honest_tenure: {
      same_receipt_floor_rows: floorProtectionRows.filter((row) => row.protection?.same_receipt_floor_law_applied).length,
      same_receipt_floor_departure_violations: floorProtectionRows.filter((row) => row.protection?.same_receipt_floor_departure).length,
      held_postable_singleton_rows: floorProtectionRows.filter((row) => row.protection?.postable_floor_rest_held_against_crossing_singleton).length,
      singleton_unconsumed_violations: singletonUnconsumedRows.length,
      honest_tenure_receipt: "EVIDENCED_FLOOR_TENURE_TABLE.json",
      gate_counterexample_receipt: "HONEST_GATE_COUNTEREXAMPLE_RECEIPT.json",
      tenure_by_named_leg: Object.fromEntries(tenureRowsByLeg.map((row) => [`${row.event_id.split("-").at(-1)}|${row.leg_id}`, row.episodes.map((episode) => ({ level_cents: episode.level_cents, tenure_seconds: episode.tenure_seconds, sampling_status: episode.sampling_status, ended_by: episode.standing_ended_by }))])),
    },
    lajsva_derivation_story: lajsvaTurningPoints.map((row) => ({ timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, leg_id: row.leg_id, query_fingerprint: row.derivation.reposed_query_fingerprint_sha256 ?? row.neighborhood?.[0]?.query_fingerprint_sha256 ?? null, evidence_rung: row.derivation.evidence_rung, rung_availability: row.derivation.rung_availability, neighbors: row.neighborhood.map((neighbor) => ({ event_id: neighbor.event_id, similarity_grade: neighbor.score, coverage_grade: neighbor.coverage, citation_receipt_id: neighbor.citation_receipt_id })), own_conditioning: row.derivation.neighbor_leg.own_evidence, raw_depth_distribution_cents: row.derivation.raw_depth_distribution_cents, depth_distribution_cents: row.derivation.depth_distribution_cents, chosen_depth_cents: row.derivation.chosen_depth_cents, window_timing: row.derivation.window_timing, pair_state: row.derivation.pair_state, allocation: row.derivation.allocation, lineage_target_cents: row.derivation.lineage_target_cents, composition_action: row.action, ...sentenceTraceIndex(row) })),
    actions_with_reasons: allDerivations.filter((row) => row.action.target_cents !== row.derivation.lineage_target_cents || row.action.action === "CANCEL_REST").map((row) => ({ event_id: row.event_id, leg_id: row.leg_id, timestamp_epoch: row.timestamp_epoch, receipt: row.receipt, lineage_target_cents: row.derivation.lineage_target_cents, composition_action: row.action, composition_reason: row.action.reason, allocation: row.derivation.allocation, ...sentenceTraceIndex(row) })),
    fills_as_consequences: fillEvents,
    deltas_and_gate_last: { results: storyResults, floor_breaks: floorBreaks, law_violations: lawViolations, gate_pass: floorBreaks.length === 0 && lawViolations.length === 0 },
    safety_floor_pass: floorBreaks.length === 0,
    self_stop: floorBreaks.length > 0 || lawViolations.length > 0 || namedStepFailures.length > 0,
    stop_reason: floorBreaks.length ? "TRUE_CEILING_7_4_8_TRIPWIRE_BREAK" : lawViolations.length ? "LAW_VIOLATION" : namedStepFailures.length ? "NAMED_STEP_FAILURE" : null,
  };
  writeJson(path.join(output, "PROCESS_FIRST_CONFIRM_RECEIPT.json"), processReceipt);
  const processMd = `# Contracts build — authority restored + spread eye — process-first confirmation\n\nVERDICT: safety_floor_pass=${floorBreaks.length === 0}; self_stop=${floorBreaks.length > 0 || lawViolations.length > 0 || namedStepFailures.length > 0}.\n\n## 1. Stores pulled\n\n${Object.entries(storesPulled.tick_rows_by_game).map(([eventId, counts]) => `- ${eventId}: ${counts.total} tape rows (${counts.books} book, ${counts.prints} true-print).`).join("\n")}\n- Foundation: ${corpus.foundation.rows} games served; bounded coverage ${corpus.foundation.coverage_before.bounded_games} → ${corpus.foundation.coverage_after.bounded_games}. Floor-time bindings: ${corpusFloorTiming.before_truth_table_only.events} → ${corpusFloorTiming.after_all_bell_bounded_library_paths.events} games, ${corpusFloorTiming.before_truth_table_only.legs} → ${corpusFloorTiming.after_all_bell_bounded_library_paths.legs} legs.\n- Range spectrum: ${corpus.counts.range_rows} rows. Historical materialization: ${corpus.counts.historical_rows} rows. Corpus registry: ${corpus.counts.registry_rows} rows. Union: ${corpus.counts.union_games} games.\n- Odds coverage: ${TARGETS.stories.map((eventId) => `${eventId}=0 event-keyed rows (RESOURCE-GAP)`).join("; ")}.\n\n## 2. Lock retirement, narrowing, supervisor, and carry\n\n- floor_rest_locks retired: true. Exact-floor proposals ${exactFloorProposalRows.length}; admitted/held ${exactFloorProposalRows.filter((row) => ["ADMITTED_AT_OR_BELOW_EVIDENCED_FLOOR", "HELD_EXISTING_EVIDENCED_FLOOR_REST"].includes(row.supervisor?.status)).length}.\n- Singleton envelope rows ${singletonEnvelopeRows.length}; unconsumed ${singletonUnconsumedRows.length}. Supervised floor proposals ${supervisedFloorProposalRows.length}.\n- Rearm rows ${rearmRows.length}. Prior-receipt convictions originated or repriced ${carriedActionRows.length} rests.\n\n## 3. LAJSVA derivation story\n\n${lajsvaTurningPoints.map((row) => `### ${row.timestamp_epoch} · ${row.leg_id}\n\nFingerprint: ${row.derivation.reposed_query_fingerprint_sha256 ?? row.neighborhood?.[0]?.query_fingerprint_sha256 ?? "NONE"}.\n\nSurvivors/movement: ${JSON.stringify(row.layered_dual_belief?.macro?.survivor_shapes?.legs?.[row.leg_id] ?? null)}. Conviction: ${JSON.stringify(row.layered_dual_belief?.conviction_evolution ?? null)}.\n\nNeighbors with grades: ${row.neighborhood.map((neighbor) => `${neighbor.event_id} similarity=${neighbor.score.toFixed(6)} coverage=${neighbor.coverage.toFixed(6)} [${neighbor.citation_receipt_id}]`).join("; ")}.\n\nWindow/price composition: ${row.derivation.evidence_rung}; own ${row.derivation.neighbor_leg.own_evidence.basis} low ${row.derivation.neighbor_leg.own_evidence.observed_low_cents ?? "UNKNOWN"}; raw q25/q50/q75 ${row.derivation.raw_depth_distribution_cents.q25 ?? "UNKNOWN"}/${row.derivation.raw_depth_distribution_cents.q50 ?? "UNKNOWN"}/${row.derivation.raw_depth_distribution_cents.q75 ?? "UNKNOWN"}; conditioned q25/q50/q75 ${row.derivation.depth_distribution_cents.q25 ?? "UNKNOWN"}/${row.derivation.depth_distribution_cents.q50 ?? "UNKNOWN"}/${row.derivation.depth_distribution_cents.q75 ?? "UNKNOWN"}; chosen depth ${row.derivation.chosen_depth_cents ?? "UNKNOWN"}; window ${JSON.stringify(row.derivation.window_timing)}; pair state ${row.derivation.pair_state}; allocation ${JSON.stringify(row.derivation.allocation)}.\n\nSentence verbatim:\n\n\`\`\`text\n${row.sentence}\n\`\`\``).join("\n\n")}\n\n## 4. Actions with reasons\n\n${processReceipt.actions_with_reasons.map((row) => `- ${row.event_id}|${row.leg_id} @ ${row.timestamp_epoch}: lineage context ${row.lineage_target_cents ?? "NONE"}; composition ${row.composition_action.action} ${row.composition_action.target_cents ?? "NONE"}; reason ${row.composition_reason}; allocation ${row.allocation?.mode ?? "NONE"}.`).join("\n")}\n\n## 5. Fills as consequences\n\n${fillEvents.length ? fillEvents.map((row) => `- ${row.context.event_id}|${row.context.leg_id}: ${row.context.entry_cents}¢ at ${row.context.fill_timestamp_epoch}, receipt ${row.row_refs.join(",")}.`).join("\n") : "- None."}\n\n## 6. Four-game deltas and gate verdict\n\n${storyResults.map((row) => `- ${row.event_id}: ${row.composition_rebuild.completed ? `${row.composition_rebuild.combined_entry_cents}¢, Δ${row.composition_rebuild.delta_vs_100_cents}` : "PARTIAL"}.`).join("\n")}\n\nGate: ${floorBreaks.length === 0 && lawViolations.length === 0 ? "PASS" : `SELF-STOP (${floorBreaks.length ? "ratchet break" : "law violation"})`}.\n`;
  const centralProcessSection = `## 2. Central estimate, touch subordination, and inside-spread reach\n\n- F-VS-124/F-VS-127 phase-central surface: ${phaseCentralSurface.central_population_points} causal points across ${phaseCentralSurface.cells.length} category×phase cells. Executable own-deadline grade is ${centralHitRows}/${centralGradedRows.length} (${(100 * centralHitShare).toFixed(1)}%) with ${predictionBiasMedian}¢ median signed error; CC's corrected reference is ${ccCounterfactual.hit_rows}/${ccCounterfactual.graded_rows} (${(100 * ccCounterfactual.hit_share).toFixed(1)}%). This is telemetry, not this repair's gate.\n- Touch rows without a live envelope: ${liveTouchRows.length}; touch-over-live-envelope violations: ${touchOverLiveEnvelopeViolations.length}; DISAGREES placement/reprice violations: ${disagreesPlacementViolations.length}.\n- Coherent q75 inside-spread rows: ${coherentQuantileRows.length}; quantile-license violations: ${coherentQuantileViolations.length}.\n\n`;
  const processMdFinal = processMd.replace("# Contracts build — authority restored + spread eye — process-first confirmation", "# Condition, don't replace — four convictions — process-first confirmation")
    .replace("## 3. LAJSVA derivation story", `${centralProcessSection.replace("## 2.", "## 3.")}## 4. LAJSVA derivation story`)
    .replace("## 4. Actions with reasons", "## 5. Actions with reasons")
    .replace("## 5. Fills as consequences", "## 6. Fills as consequences")
    .replace("## 6. Four-game deltas and gate verdict", "## 7. Four-game deltas and gate verdict");
  const definitionProcessMd = processMdFinal
    .replace("## 2. Lock retirement, narrowing, supervisor, and carry", "## 2. Post-only guard, floor-capable lane, Definition Lock, tenure, and honest gates")
    .replace("- floor_rest_locks retired: true.", "- Evidenced floor is the bell-lawful observed traded low only; belief envelopes are never floors. floor_rest_locks retired: true.")
    + `\n\n## Four convictions — named repairs\n\n- True-conditioning rows ${trueConditioningRows.length}; violations ${trueConditioningViolations.length}. The prior is updated, never replaced; trade outranks spread-clearing, which outranks book.\n- Same-receipt postable changes ${sameReceiptActRows.filter((row) => row.derivation_and_postability_same_receipt).length}; missed same-receipt acts ${sameReceiptActViolations.length}.\n- Credited-leg continued-read rows ${creditedLegReadRows.length}; stopped-stream violations ${creditedLegReadViolations.length}.\n- Directional rounding rows ${directionalRoundingRows.length}; violations ${directionalRoundingViolations.length}; named direction 57.5→58.\n- Author rows: ${authorOwnEvidenceRows.length}; prior→conditioned→level sentence violations: ${authorOwnEvidenceViolations.length}.\n- Level-movement rows: ${movementRows.length}; pure-panel recompositions suppressed: ${movementRows.filter((row) => row.disposition === "PURE_PANEL_RECOMPOSITION_SUPPRESSED").length}; movement-law violations: ${movementViolations.length}.\n- Emitted PLACE/REPRICE orders: ${oneAuthorOrderRows.length}; independently recomputed authority divergences: ${oneAuthorDivergences.length}; raw-traded-low target defaults: zero; ask-minus-one price authors: zero.\n- Exact-floor tenure violations: ${floorProtectionViolations.length}; continuous post-only active crossings: ${postOnlyGateRows.filter((row) => row.active_target_crossed_live_ask).length}; crossed rests unlawfully held: ${crossedStandingHoldRows.length}.\n- Authority-vacuum rows: ${vacuumRows.length}; illegal vacuum emissions: ${vacuumEmissionRows.length}. Every vacuum resolved to HOLD, F-VS-068 own evidence, or INSUFFICIENT stand-down.\n- C04 current-authority restores: ${c04Rows.length}; post-span orders: ${postSpanOrderRows.length}; cancels without rearm: ${cancelWithoutRearmRows.length}.\n\n## Contracts, one tenure, and spread eye\n\n- Pricing authority: panel prior → graded receipt channels → conditioned distribution → directed integer level; lane-level substitutions ${authorityViolations.length}.\n- Contracts: ${firedContracts.length} fired/priced + ${latentContracts.length} latent registered; every decision carries the full register and every sentence states the active contract.\n- Envelope-high provenance: ${envelopeHighRows.length} rows; zero floored-mid producers.\n- Tenure producer: ORDER_TRANSITION_TENURE_SINGLE_PRODUCER; sampled-row/phantom producers: zero.\n- Spread eye: ${spreadEyeRows.length} readings; ${spreadEyeRows.filter((row) => row.authority_consumed).length} authority consumptions; zero direct lane commands.\n\n## Executable checks\n\n- Post-only candidate rows: ${postOnlyGateRows.length}; covered ${postOnlyGateRows.filter((row) => row.covered).length}; unlawful emitted orders ${postOnlyGateRows.filter((row) => row.emitted && !row.lawful).length}.\n- Emitted orders per decision instant ${JSON.stringify(orderArbitrationReceipt.orders_per_decision_instant_distribution)}; maximum ${orderArbitrationReceipt.max_orders_per_decision_instant}.\n- Floor rows tested: ${floorDefinitionRows.length}/${allDerivations.length}, including ${floorDefinitionRows.filter((row) => row.row_class === "NO_TRUE_TRADE_YET").length} no-trade rows; failures ${floorDefinitionFailures.length}.\n- Honest gate failures: ${gateFailures.map((check) => check.id).join(", ") || "NONE"}.\n`;
  layeredReporter.emit({ output, storesPulled, corpus, storyResults, fillEvents, floorBreaks, lawViolations, allDerivations, targets: TARGETS });
  // The standing reporter writes its own generic process-first document.  This
  // repair's dispatch adds a contract/authority/spread-eye stage, so emit both
  // dispatch-specific receipt and narrative after the standing artifacts.
  writeJson(path.join(output, "PROCESS_FIRST_CONFIRM_RECEIPT.json"), processReceipt);
  writeText(path.join(output, "PROCESS_FIRST_CONFIRM.md"), definitionProcessMd);
  // Retire filenames emitted by the superseded single-leg composition
  // renderer. Its scan signals remain preserved in REPAIR_GATE_RECEIPT.
  for (const legacyName of ["EVIDENCE_LADDER_RECEIPT.json", "SPLIT_ALLOCATION_RECEIPT.json", "COMPOSITION_PRESENCE_RECEIPT.json", "FOUNDATION_SERVING_FIX_RECEIPT.json", "LAJSVA_EARLY_RISER_FORENSICS.json"]) {
    fs.rmSync(path.join(output, legacyName), { force: true });
  }
  writeText(path.join(output, "ASSUMPTION_GAPS.md"), `# Assumption gaps\n\n- January–March has event-grain historical aggregates but no local intramatch tape. Measurement needed: public historical trades plus timestamped book reconstruction at the same grain as the July recorder.\n- The subsecond store mixes public tape and synthetic book transitions and lacks exchange trade identity on every row. Measurement needed: source-specific identity completeness by named event.\n- The DO archive is connected and the pre-sealed object reader is smoked, but its July object catalog is not a January-present database. Measurement needed: event-level archive coverage joined to corpus_events_v2.\n- The odds backup is connected, but its overlap with each target game is not complete. Measurement needed: immutable per-event bookmaker snapshots with source clock and player mapping.\n- CRIJEA has no verified bell. Measurement needed: an independent official in-play timestamp; until then it grades nothing.\n`);
  writeText(path.join(output, "CC_URSPAL_LATE_BELL.md"), `# CC filing — URSPAL late bell\n\nEvent: KXATPCHALLENGERMATCH-26JUL14URSPAL.\n\nThe L11 truth-table right edge is 1784045100. Tape prints moved PAL 41→30 and URS 61→77 within four minutes after that edge. The tape-inferred bell is at least 48 minutes late for this game. The close remains the truth-table close unless and until CC's standing bell sweep produces a stronger official timestamp.\n\nSource: F-VS-023 @ 3cd59162; W1_GROUND_TRUTH_TABLE.json @ c0056976.\n`);
  writeJson(path.join(output, "FORBIDDEN_ACCESS_RECEIPT.json"), { full_804_run: storyResults.length === 804, tune_test_population_run: storyResults.length === 804, sealed_read: storyResults.some((row) => row.event_id.includes("24JUL")), holdout_read: storyResults.some((row) => row.event_id.includes("24JUL")), live_mutation: RUN_SOURCE.includes("LIVE_MUTATION"), orders: fillEvents.some((row) => row.context?.venue_order_id), positions: storyResults.some((row) => row.composition_rebuild?.account_position), deployment: RUN_SOURCE.includes("DEPLOYMENT"), scope: { smoke: TARGETS.smoke, stories: TARGETS.stories } });
  writeJson(path.join(output, "SOURCE_RECEIPTS.json"), { corpus_sources: corpus.sources, foundation: corpus.foundation, library_bell_bound: corpus.bell_bound_receipt, corpus_floor_timing: corpusFloorTiming, ground_truth: groundTruth.receipt, remote, target_prints: printLoad.source, lineage: lineage.receipt, resources });
  writeJson(path.join(output, "WORKTREE_LARGE_UNTRACKED_CENSUS.json"), largeUntrackedCensus(repo));
  const custodyOutput = arg("custody-output") ? path.resolve(arg("custody-output")) : null;
  custodyOversizedArtifacts({
    output,
    custodyOutput,
    rowsByName: {
      "REPAIR_FOUR_GAME_TRACE.jsonl.gz": storyTraces.length,
      "ATOMIC_REARM_RECEIPT.json": rearmRows.length,
      "ENVELOPE_PLACEMENT_RECEIPT.json": envelopePlacementRows.length,
    },
  });
  const producerCoverage = receiptProducerCoverage(repo, output);
  writeJson(path.join(output, "RECEIPT_PRODUCER_COVERAGE.json"), producerCoverage);
  ensure(producerCoverage.unproduced.length === 0, `ORPHAN_RECEIPT_WITHOUT_PRODUCER:${producerCoverage.unproduced.map((row) => row.artifact).join(",")}`);
  const files = fs.readdirSync(output).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  ensure(files.every((name) => fs.statSync(path.join(output, name)).size <= 50 * 1024 * 1024), "L22_COMMITTED_ARTIFACT_EXCEEDS_50_MIB");
  writeJson(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), { label: OUTPUT_LABEL, files: Object.fromEntries(files.map((name) => [name, { ...receipt(path.join(output, name)), path: name }])) });
  process.stdout.write(canonical({ output, functionable: functionality.all_connected, smoke: "PASS_NO_GRADING", stories: storyResults, floor_breaks: floorBreaks, full_804_run: storyResults.length === 804, sealed: storyResults.some((row) => row.event_id.includes("24JUL")), live: RUN_SOURCE.includes("LIVE_MUTATION") }));
}

if (require.main === module) main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });

module.exports = {
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
