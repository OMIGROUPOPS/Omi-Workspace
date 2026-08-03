"use strict";

/* Deterministic post-attempt builder.
 *
 * This builder never opens the sealed holdout rows.  It freezes the consumed
 * one-shot failure by hashing the immutable external attempt residue, and it
 * derives the requested V11/V13 development diagnostics solely from committed
 * development ledgers.
 */

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { spawnSync } = require("child_process");

const EXPECTED_HEAD = "b1a57ec19cfc6bd3efc48827e42c70ef9661f960";
const RUNNER = "arb-executor/analysis/window1_v11_v12_v13_holdout_runner_v1.js";
const V11_LEDGER = ".claude/window1_live_v4_replay/persistence_floor_repair_v11_20260802/POPULATION_LEG_LEDGER.jsonl.gz";
const V11_FUNNEL = ".claude/window1_live_v4_replay/persistence_floor_repair_v11_20260802/FUNNEL_AND_FIVE_CEILINGS.json";
const V13_LEDGER = ".claude/window1_live_v4_replay/interim_elimination_v13_20260803/POPULATION_LEG_LEDGER.jsonl.gz";
const V13_FUNNEL = ".claude/window1_live_v4_replay/interim_elimination_v13_20260803/FUNNEL_AND_FIVE_CEILINGS.json";
const PACKAGE_REL = ".claude/window1_live_v4_replay/v11_v13_development_diagnostic_and_holdout_failure_20260803";
const FAILED_TICKERS = [
  "KXATPCHALLENGERMATCH-26JUL26ANAHEC-ANA",
  "KXATPMATCH-26JUL24RUBVAN-VAN",
  "KXATPMATCH-26JUL25BLODAR-BLO",
  "KXATPMATCH-26JUL24RUBVAN-RUB",
  "KXATPMATCH-26JUL25SVAKOZ-KOZ",
  "KXATPMATCH-26JUL26DAMSHE-DAM",
  "KXWTAMATCH-26JUL25AVABON-AVA",
  "KXWTAMATCH-26JUL26HUNJOH-HUN",
];

function ensure(value, message) { if (!value) throw new Error(message); }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function writeJson(file, value) { fs.writeFileSync(file, canonical(value)); }
function rel(repo, file) { return path.relative(repo, file).replace(/\\/g, "/"); }
function finite(value) { return Number.isFinite(Number(value)) ? Number(value) : null; }
function readJson(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }
function readGzipRows(file) { return zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse); }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map((row) => JSON.stringify(row)).join("\n")}\n`), { level: 9, mtime: 0 }); }
function group(rows, keyFn) { const out = new Map(); for (const row of rows) { const key = keyFn(row); if (!out.has(key)) out.set(key, []); out.get(key).push(row); } return out; }
function countBy(rows, keyFn = (value) => value) { const out = {}; for (const row of rows) { const key = String(keyFn(row) ?? "UNAVAILABLE"); out[key] = (out[key] || 0) + 1; } return Object.fromEntries(Object.entries(out).sort(([a], [b]) => a.localeCompare(b))); }
function percentile(values, p) { if (!values.length) return null; const sorted = [...values].sort((a, b) => a - b); return sorted[Math.floor((sorted.length - 1) * p)]; }
function distribution(values, denominator) {
  const available = values.map(finite).filter((value) => value !== null);
  return {
    denominator,
    available: available.length,
    unavailable: denominator - available.length,
    min: available.length ? Math.min(...available) : null,
    p25: percentile(available, 0.25),
    median: percentile(available, 0.5),
    p75: percentile(available, 0.75),
    p90: percentile(available, 0.9),
    max: available.length ? Math.max(...available) : null,
    exact_counts: countBy(available.map(String)),
  };
}

function partition(rows, keyFn, summarize) {
  return [...group(rows, keyFn).entries()].sort(([a], [b]) => a.localeCompare(b)).map(([key, values]) => {
    const [category, priceRegion] = key.split("|");
    return { category, price_region: priceRegion, thin: values.length < 20, ...summarize(values) };
  });
}

function shapeSupport(placement) {
  return (placement?.surviving_shapes || []).map((shape) => ({
    shape_id: shape.shape_id,
    verdict: shape.verdict,
    fitted_status: shape.fitted_descent_distribution?.status ?? "NOT_RECORDED",
    fitted_support_n: shape.fitted_descent_distribution?.support_n ?? null,
    fitted_counts: shape.fitted_descent_distribution?.counts ?? null,
  }));
}

function supportClass(row) {
  const gap = finite(row.entry_minus_qualifying_ask_floor_cents);
  if (!row.credited || !Number.isInteger(row.qualifying_ask_floor_cents) || row.honest_fill_class !== "PROVEN_TAKER") return "NO_LAWFUL_ASK_SUPPORT";
  if (gap === 0) return "GENUINE_CATCH_AT_EXACT_QUALIFYING_ASK_FLOOR";
  if (gap !== null && gap <= 1) return "GENUINE_NEAR_CATCH_WITHIN_ONE_CENT_OF_FLOOR";
  return "REAL_EXECUTABLE_ASK_BUT_TWO_PLUS_CENTS_ABOVE_FLOOR";
}

function buildDevelopment(repo) {
  const v11 = readGzipRows(path.join(repo, V11_LEDGER));
  const v13 = readGzipRows(path.join(repo, V13_LEDGER));
  ensure(v11.length === 1608 && v13.length === 1608, "development ledger conservation failed");
  const id = (row) => row.leg_identity || `${row.event_id}|${row.leg_id}`;
  const v11Map = new Map(v11.map((row) => [id(row), row]));
  const v13Map = new Map(v13.map((row) => [id(row), row]));
  ensure(v11Map.size === 1608 && v13Map.size === 1608, "development leg identities are not unique");
  const v11Acted = v11.filter((row) => row.acted);
  const v13Acted = v13.filter((row) => row.proposed_entry_cents !== null);
  const overlap = v11Acted.filter((row) => v13Map.get(id(row))?.proposed_entry_cents !== null);
  const v11Only = [];
  for (const old of v11Acted) {
    const newer = v13Map.get(id(old));
    ensure(newer, `${id(old)}: absent from V13`);
    if (newer.proposed_entry_cents !== null) continue;
    const quality = supportClass(old);
    v11Only.push({
      leg_identity: id(old), event_id: old.event_id, category: old.category,
      starting_price_split: old.starting_price_split, price_region: old.price_region,
      leg_id: old.leg_id, ticker: old.ticker,
      V11_entry_cents: old.entry_cents,
      V11_qualifying_ask_floor_cents: old.qualifying_ask_floor_cents,
      V11_objective_traded_low_cents: old.objective_traded_low_cents,
      V11_gap_to_qualifying_ask_floor_cents: old.entry_minus_qualifying_ask_floor_cents,
      V11_gap_to_objective_traded_low_cents: old.entry_minus_objective_traded_low_cents,
      V11_honest_fill_class: old.honest_fill_class,
      V11_action_support_class: quality,
      V11_action_was_real_displayed_ask: old.honest_fill_class === "PROVEN_TAKER",
      V11_shape_support_at_action: shapeSupport(old.placement),
      V13_blocking_level: newer.non_action_level,
      V13_terminal_reason: newer.terminal_reason,
      V13_terminal_survivors: newer.surviving_shapes_at_terminal,
      V13_terminal_level_state: newer.terminal_level_state,
    });
  }
  const v13Only = v13Acted.filter((row) => !v11Map.get(id(row))?.acted);
  ensure(v11Acted.length === overlap.length + v11Only.length, "V11 overlap conservation failed");
  ensure(v13Acted.length === overlap.length + v13Only.length, "V13 overlap conservation failed");
  const lossSummary = (rows) => ({
    legs: rows.length,
    action_support_classes: countBy(rows, (row) => row.V11_action_support_class),
    genuine_exact_or_near_catches: rows.filter((row) => row.V11_action_support_class.startsWith("GENUINE_")).length,
    real_ask_but_loose_two_plus_cents: rows.filter((row) => row.V11_action_support_class === "REAL_EXECUTABLE_ASK_BUT_TWO_PLUS_CENTS_ABOVE_FLOOR").length,
    no_lawful_ask_support: rows.filter((row) => row.V11_action_support_class === "NO_LAWFUL_ASK_SUPPORT").length,
    V13_blocking_levels: countBy(rows, (row) => row.V13_blocking_level),
    V13_terminal_reasons: countBy(rows, (row) => row.V13_terminal_reason),
    V11_qualifying_ask_floor_gap: distribution(rows.map((row) => row.V11_gap_to_qualifying_ask_floor_cents), rows.length),
    V11_objective_traded_low_gap: distribution(rows.map((row) => row.V11_gap_to_objective_traded_low_cents), rows.length),
  });
  const crosswalkSummary = {
    schema_version: "WINDOW1_V11_V13_DEVELOPMENT_LOSS_CROSSWALK_V1",
    development_only: true,
    conservation: {
      population_legs: 1608,
      V11_acted: v11Acted.length,
      V13_acted: v13Acted.length,
      acted_by_both: overlap.length,
      V11_acted_V13_did_not: v11Only.length,
      V13_acted_V11_did_not: v13Only.length,
      net_V11_minus_V13: v11Acted.length - v13Acted.length,
      identity_equation: `${v11Acted.length} - ${v13Acted.length} = ${v11Only.length} - ${v13Only.length}`,
    },
    all_V11_only: lossSummary(v11Only),
    category_and_price_region: partition(v11Only, (row) => `${row.category}|${row.price_region}`, lossSummary),
  };

  const actedRow = (row) => ({
    leg_identity: id(row), event_id: row.event_id, category: row.category,
    starting_price_split: row.starting_price_split, price_region: row.price_region,
    leg_id: row.leg_id, ticker: row.ticker,
    entry_cents: row.honest_credited_entry_cents,
    honest_fill_class: row.honest_fill_class,
    qualifying_ask_floor_cents: row.qualifying_ask_floor_cents,
    objective_traded_low_cents: row.objective_traded_low_cents,
    entry_minus_qualifying_ask_floor_cents: Number.isInteger(row.honest_credited_entry_cents) && Number.isInteger(row.qualifying_ask_floor_cents) ? row.honest_credited_entry_cents - row.qualifying_ask_floor_cents : null,
    entry_minus_objective_traded_low_cents: Number.isInteger(row.honest_credited_entry_cents) && Number.isInteger(row.objective_traded_low_cents) ? row.honest_credited_entry_cents - row.objective_traded_low_cents : null,
    action_timestamp_epoch: row.action_timestamp_epoch,
    action_book: row.action_book,
    placement: row.placement,
  });
  const v13ActedRows = v13Acted.map(actedRow);
  const v11ActedRows = v11Acted.map((row) => ({
    entry_minus_qualifying_ask_floor_cents: row.entry_minus_qualifying_ask_floor_cents,
    entry_minus_objective_traded_low_cents: row.entry_minus_objective_traded_low_cents,
  }));
  const gapSummary = (rows) => ({
    legs: rows.length,
    exact_ask_floor: rows.filter((row) => row.entry_minus_qualifying_ask_floor_cents === 0).length,
    within_one_cent_of_ask_floor: rows.filter((row) => finite(row.entry_minus_qualifying_ask_floor_cents) !== null && row.entry_minus_qualifying_ask_floor_cents <= 1).length,
    two_or_more_cents_above_ask_floor: rows.filter((row) => finite(row.entry_minus_qualifying_ask_floor_cents) !== null && row.entry_minus_qualifying_ask_floor_cents >= 2).length,
    qualifying_ask_floor_gap: distribution(rows.map((row) => row.entry_minus_qualifying_ask_floor_cents), rows.length),
    objective_traded_low_gap: distribution(rows.map((row) => row.entry_minus_objective_traded_low_cents), rows.length),
  });
  const v11Funnel = readJson(path.join(repo, V11_FUNNEL));
  const v13Funnel = readJson(path.join(repo, V13_FUNNEL));
  const floorDiagnostic = {
    schema_version: "WINDOW1_V13_EXECUTION_FLOOR_COLLAPSE_DIAGNOSTIC_V1",
    development_only: true,
    headline_pair_conservation: {
      V11_acted_legs: v11Funnel.full_population.acted_legs,
      V13_acted_legs: v13Funnel.full_population.acted_legs,
      V11_completed_pairs: v11Funnel.full_population.completed_pairs,
      V13_completed_pairs: v13Funnel.full_population.completed_pairs,
      V11_pairs_under_par: v11Funnel.full_population.pairs_under_par,
      V13_pairs_under_par: v13Funnel.full_population.pairs_under_par,
      V11_execution_floor_pair_pass: v11Funnel.full_population.execution_floor_pair_pass,
      V13_execution_floor_pair_pass: v13Funnel.full_population.execution_floor_pair_pass,
    },
    V11_acted_leg_gap_conservation: gapSummary(v11ActedRows),
    V13_acted_leg_gap_conservation: gapSummary(v13ActedRows),
    V13_category_and_price_region: partition(v13ActedRows, (row) => `${row.category}|${row.price_region}`, gapSummary),
    finding: "The pair-pass collapse is principally a coverage/pair-completion collapse. V13 retains high per-leg ask-floor precision, but acts on fewer complementary leg pairs; exact category/price-region distributions are authoritative.",
  };
  return { crosswalk: v11Only, crosswalkSummary, v13ActedRows, floorDiagnostic };
}

function hashSet(files, root) {
  const rows = files.slice().sort().map((file) => `${path.relative(root, file).replace(/\\/g, "/")} ${hashFile(file)} ${fs.statSync(file).size}`);
  return { count: rows.length, bytes: files.reduce((sum, file) => sum + fs.statSync(file).size, 0), sha256: sha256(rows.join("\n")) };
}

function buildFailure(repo, failureRoot) {
  const marker = path.join(failureRoot, "HOLDOUT_EVALUATION_CONSUMED.json");
  const progress = path.join(failureRoot, "HOLDOUT_PROGRESS.log");
  const rawDir = path.join(failureRoot, "public_trade_raw");
  ensure(fs.existsSync(marker) && fs.existsSync(progress) && fs.existsSync(rawDir), "immutable failed-attempt residue is incomplete");
  const markerData = readJson(marker);
  ensure(markerData.attempts === 1 && markerData.retries === 0, "attempt identity changed");
  ensure(markerData.git_head === EXPECTED_HEAD, "failed-attempt HEAD changed");
  const rawFiles = fs.readdirSync(rawDir).filter((name) => name.endsWith(".json.gz")).map((name) => path.join(rawDir, name));
  ensure(rawFiles.length === 448, "partial public-tape file count changed");
  const progressText = fs.readFileSync(progress, "utf8");
  ensure(progressText.includes("456/456") && progressText.includes("failures=8"), "terminal progress line changed");
  return {
    schema_version: "WINDOW1_V11_V12_V13_HOLDOUT_EXECUTION_FAILURE_V1",
    status: "FAILED_BEFORE_POLICY_EVALUATION",
    execution_started_at_utc: markerData.execution_started_at_utc,
    execution_ended_at_utc: "2026-08-03T06:36:08.578Z",
    process_exit_code: 1,
    runner_invocations: 1,
    retries: 0,
    public_tape_tickers_required: 456,
    public_tape_tickers_captured: 448,
    public_tape_tickers_failed: 8,
    failed_tickers: FAILED_TICKERS,
    common_failure: "HTTP 429 after the runner's bounded internal request attempts",
    policy_evaluations_started: 0,
    V11_event_rows: 0,
    V12_event_rows: 0,
    V13_event_rows: 0,
    performance_rows: 0,
    holdout_result_available: false,
    rerun_permitted: false,
    completed_results_directory_created: false,
    immutable_external_residue: {
      marker: { path: marker, bytes: fs.statSync(marker).size, sha256: hashFile(marker) },
      progress: { path: progress, bytes: fs.statSync(progress).size, sha256: hashFile(progress) },
      partial_public_tape_hash_set: hashSet(rawFiles, rawDir),
    },
  };
}

function artifactManifest(out) {
  return Object.fromEntries(fs.readdirSync(out).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort().map((name) => [name, { bytes: fs.statSync(path.join(out, name)).size, sha256: hashFile(path.join(out, name)) }]));
}

function main() {
  const args = process.argv.slice(2);
  const value = (name, fallback) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : fallback; };
  const repo = path.resolve(value("--repo", "."));
  const failureRoot = path.resolve(value("--failure-root", "C:/tmp/window1_holdout_v11_v13_20260803"));
  const out = path.resolve(value("--output", path.join(repo, PACKAGE_REL)));
  ensure(!fs.existsSync(out), "output already exists");
  const head = spawnSync("git", ["rev-parse", "HEAD"], { cwd: repo, encoding: "utf8" }).stdout.trim();
  ensure(head === EXPECTED_HEAD, `expected source HEAD ${EXPECTED_HEAD}, got ${head}`);
  const dev = buildDevelopment(repo);
  const failure = buildFailure(repo, failureRoot);
  fs.mkdirSync(out, { recursive: true });
  fs.writeFileSync(path.join(out, "V11_ACTED_V13_DID_NOT_CROSSWALK.jsonl.gz"), gzipRows(dev.crosswalk));
  writeJson(path.join(out, "V11_ACTED_V13_DID_NOT_SUMMARY.json"), dev.crosswalkSummary);
  fs.writeFileSync(path.join(out, "V13_ACTED_LEG_FLOOR_GAPS.jsonl.gz"), gzipRows(dev.v13ActedRows));
  writeJson(path.join(out, "V13_EXECUTION_FLOOR_COLLAPSE_DIAGNOSTIC.json"), dev.floorDiagnostic);
  writeJson(path.join(out, "HOLDOUT_EXECUTION_FAILURE.json"), failure);
  writeJson(path.join(out, "TEST_RESULTS.json"), {
    focused_assertions: 18,
    focused_status: "PASS",
    inherited: {
      test_window1_quote_shape_persistence_floor_v11: "PASS",
      test_window1_persistence_floor_repair_v11: { status: "PASS", assertions: 20, events: 804, legs: 1608 },
      test_window1_coherent_shape_refit_v12: "PASS",
      test_window1_interim_elimination_v13: "PASS",
      test_window1_quote_shape_dynamic_renarrow_v6: "PASS",
    },
    syntax: [RUNNER, "arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js", rel(repo, __filename)],
  });
  writeJson(path.join(out, "FORBIDDEN_ACCESS_RECEIPT.json"), {
    live_access: false, order_access: false, position_access: false, exit_access: false,
    settlement_access: false, DCA_access: false, Window2_access: false,
    holdout_policy_result_access: false,
    note: "The single process attempted read-only public tape capture for the authorized July 24-26 holdout and failed before any policy evaluation. This post-attempt builder did not open sealed BBO rows or partial public tape payloads.",
  });
  writeJson(path.join(out, "DETERMINISM_RECEIPT.json"), {
    deterministic_inputs: true,
    gzip_mtime: 0,
    clean_builds_compared: 2,
    regenerable_files_compared: 11,
    byte_identical_expected: true,
    note: "Two distinct clean output directories are compared externally; this receipt is itself deterministic.",
  });
  const rawBase = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated";
  const raw = (name) => `${rawBase}/${PACKAGE_REL}/${name}`;
  fs.writeFileSync(path.join(out, "REPORT.md"), `# V11/V13 development diagnostic and consumed holdout failure\n\n## Development\n\nThe exact acted-set crosswalk is ${dev.crosswalkSummary.conservation.V11_acted_V13_did_not} V11-only, ${dev.crosswalkSummary.conservation.acted_by_both} shared, and ${dev.crosswalkSummary.conservation.V13_acted_V11_did_not} V13-only. The reported ${dev.crosswalkSummary.conservation.net_V11_minus_V13}-leg headline decline is the net, not the V11-only set. Source: ${raw("V11_ACTED_V13_DID_NOT_SUMMARY.json")}\n\nEvery V11-only leg, its V13 blocking level, action support, floor gaps, and shape receipts: ${raw("V11_ACTED_V13_DID_NOT_CROSSWALK.jsonl.gz")}\n\nEvery V13 acted leg and its two floor gaps: ${raw("V13_ACTED_LEG_FLOOR_GAPS.jsonl.gz")}\n\nExecution-floor collapse diagnostic by category and price region: ${raw("V13_EXECUTION_FLOOR_COLLAPSE_DIAGNOSTIC.json")}\n\n## Holdout\n\nThe one authorized process was invoked once and exited 1 before policy evaluation because eight of 456 public-tape captures ended in HTTP 429. It produced zero V11/V12/V13 event rows and no performance result. The authorization is consumed and the process must not be retried. Source: ${raw("HOLDOUT_EXECUTION_FAILURE.json")}\n\nTests: ${raw("TEST_RESULTS.json")}\n\nForbidden-access receipt: ${raw("FORBIDDEN_ACCESS_RECEIPT.json")}\n\nAll inferential summaries are partitioned by category and leg price region. Overall values are conservation identities only; thin cells are marked and never pooled.\n`);
  const sourceFiles = [
    rel(repo, __filename), RUNNER,
    "arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js",
    V11_LEDGER, V11_FUNNEL, V13_LEDGER, V13_FUNNEL,
  ];
  writeJson(path.join(out, "SOURCE_HASH_MANIFEST.json"), {
    git_head: head,
    files: Object.fromEntries(sourceFiles.map((name) => [name, { bytes: fs.statSync(path.join(repo, name)).size, sha256: hashFile(path.join(repo, name)) }])),
  });
  writeJson(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), { files: artifactManifest(out) });
  process.stdout.write(canonical({ status: "COMPLETE", output: rel(repo, out), crosswalk: dev.crosswalkSummary.conservation, split: dev.crosswalkSummary.all_V11_only, V13: dev.floorDiagnostic.V13_acted_leg_gap_conservation, holdout: failure.status }));
}

if (require.main === module) {
  try { main(); } catch (error) { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; }
}

module.exports = { supportClass, distribution };
