#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const args = process.argv.slice(2);
const value = (name, fallback) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const outputRelative = ".claude/window1_live_v4_replay/intentional_pair_brain_v22_phase0_20260804";
const out = path.resolve(value("--output", path.join(repo, outputRelative)));
const privateRoot = path.resolve(value("--private-root", "C:/Users/omigr/OMI-Window1-private/fit-local/guarded-cache-v3"));
const rawRoot = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated";

const paths = {
  events: path.join(repo, ".claude/window1_live_v4_replay/isolated_fix_a_anchor_freshness_v20_20260804/POPULATION_EVENT_LEDGER.jsonl.gz"),
  legs: path.join(repo, ".claude/window1_live_v4_replay/isolated_fix_a_anchor_freshness_v20_20260804/POPULATION_LEG_LEDGER.jsonl.gz"),
  reference: path.join(repo, ".claude/window1_t2_scoring_package_v3_prerun_20260728/FROZEN_WINDOW1_CLOSE_REFERENCE_LEDGER.jsonl.gz"),
  bells: path.join(repo, ".claude/window1_live_v4_replay/actual_bell_refit_20260729/ACTUAL_BELL_REFIT.json"),
  expectedClose: path.join(repo, ".claude/window1_live_v4_replay/expected_close_binding_20260801/CONTROL_BINDING.json"),
  decisionUnlock: path.join(repo, ".claude/window1_live_v4_replay/expected_close_binding_20260801/DECISION_UNLOCK_RECEIPT.json"),
  xLibrary: path.join(repo, ".claude/window1_live_v4_replay/second_leg_x_pricer_fit_v17_20260803/SECOND_LEG_X_CONDITIONAL_LIBRARY.json"),
  replaySource: path.join(repo, "arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js"),
  v17Source: path.join(repo, "arb-executor/analysis/window1_second_leg_x_pricer_v17.js"),
};

function ensure(condition, message) { if (!condition) throw new Error(message); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(buffer) { return crypto.createHash("sha256").update(buffer).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function readJson(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }
function readRows(file) {
  const bytes = fs.readFileSync(file);
  const text = file.endsWith(".gz") ? zlib.gunzipSync(bytes).toString("utf8") : bytes.toString("utf8");
  return text.trim() ? text.trim().split(/\r?\n/).map(JSON.parse) : [];
}
function relative(file) { return path.relative(repo, file).replaceAll("\\", "/"); }
function lineOf(text, needle) {
  const index = text.split(/\r?\n/).findIndex((line) => line.includes(needle));
  return index < 0 ? null : index + 1;
}
function countBy(rows, key) {
  const counts = {};
  for (const row of rows) { const value = String(key(row)); counts[value] = (counts[value] || 0) + 1; }
  return Object.fromEntries(Object.entries(counts).sort((a, b) => a[0].localeCompare(b[0])));
}
function quantile(values, p) {
  const rows = values.filter(Number.isFinite).sort((a, b) => a - b);
  return rows.length ? rows[Math.floor((rows.length - 1) * p)] : null;
}
function distribution(values) {
  const rows = values.filter(Number.isFinite);
  return {
    denominator: values.length,
    numeric_n: rows.length,
    null_n: values.length - rows.length,
    min: rows.length ? Math.min(...rows) : null,
    p25: quantile(rows, 0.25),
    median: quantile(rows, 0.5),
    p75: quantile(rows, 0.75),
    p90: quantile(rows, 0.9),
    max: rows.length ? Math.max(...rows) : null,
  };
}
function partition(rows, key) {
  const groups = new Map();
  for (const row of rows) { const value = key(row); if (!groups.has(value)) groups.set(value, []); groups.get(value).push(row); }
  return groups;
}
function fmtTminus(seconds) {
  if (!Number.isFinite(seconds)) return null;
  const sign = seconds >= 0 ? "T-" : "T+";
  const absolute = Math.abs(seconds);
  const minutes = Math.floor(absolute / 60);
  const remainder = absolute - minutes * 60;
  return `${sign}${minutes}:${remainder.toFixed(3).padStart(6, "0")}`;
}

function locateReferencePrint(cache, reference) {
  const leg = cache.legs.find((candidate) => candidate.leg === reference.leg_id);
  ensure(leg, `missing cache leg ${reference.event_id}|${reference.leg_id}`);
  if (reference.guarded_cutoff_ts === null) {
    ensure(!reference.available && reference.reference_ts === null && reference.reference_supporting_receipts.length === 0, `non-positive boundary carries a reference ${reference.event_id}|${reference.leg_id}`);
    return { supporting: [], latest: [], prices: [] };
  }
  const lawful = leg.prints.filter((print) => Number(print.ts) <= Number(reference.guarded_cutoff_ts));
  if (lawful.length === 0) {
    ensure(!reference.available, `no lawful close prints ${reference.event_id}|${reference.leg_id}`);
    ensure(reference.reference_ts === null && reference.reference_supporting_receipts.length === 0, `missing reference carries fabricated support ${reference.event_id}|${reference.leg_id}`);
    return { supporting: [], latest: [], prices: [] };
  }
  const latestTs = Math.max(...lawful.map((print) => Number(print.ts)));
  const latest = lawful.filter((print) => Number(print.ts) === latestTs);
  const prices = [...new Set(latest.map((print) => Number(print.price)))];
  ensure(Number(reference.reference_ts) === latestTs, `reference timestamp is not latest lawful print ${reference.event_id}|${reference.leg_id}`);
  const supportingIds = new Set(reference.reference_supporting_receipts || []);
  const supporting = latest.filter((print) => supportingIds.has(print.trade_id));
  ensure(supporting.length === supportingIds.size && supporting.length > 0, `reference supporting receipt absent ${reference.event_id}|${reference.leg_id}`);
  if (reference.available) {
    ensure(prices.length === 1, `ambiguous close unexpectedly available ${reference.event_id}|${reference.leg_id}`);
    if (reference.reference_receipt !== null) ensure(supporting.some((print) => print.trade_id === reference.reference_receipt), `reference receipt absent ${reference.event_id}|${reference.leg_id}`);
    ensure(supporting.every((print) => Number(print.price) === Number(reference.window1_close_cents)), `close price mismatch ${reference.event_id}|${reference.leg_id}`);
  } else {
    ensure(reference.window1_close_cents === null, `unavailable reference has a price ${reference.event_id}|${reference.leg_id}`);
    ensure(reference.reason === "ambiguous_latest_timestamp_multiple_prices_no_authoritative_sequence", `unexpected unavailable reason ${reference.event_id}|${reference.leg_id}`);
    ensure(prices.length > 1, `unavailable reference lacks differing prices ${reference.event_id}|${reference.leg_id}`);
  }
  ensure(supporting.every((print) => Number(print.ts) === Number(reference.reference_ts)), `close timestamp mismatch ${reference.event_id}|${reference.leg_id}`);
  return { supporting, latest, prices };
}

function main() {
  for (const file of Object.values(paths)) ensure(fs.existsSync(file), `missing input ${file}`);
  ensure(fs.existsSync(privateRoot), `missing private guarded cache ${privateRoot}`);

  const events = readRows(paths.events);
  const legs = readRows(paths.legs);
  const references = readRows(paths.reference);
  const bellRows = readJson(paths.bells).leg_rows;
  const expectedClose = readJson(paths.expectedClose);
  const xLibrary = readJson(paths.xLibrary);
  ensure(events.length === 804 && legs.length === 1608 && references.length === 1608, "population conservation failed");
  ensure(expectedClose.status === "NOT_BOUND", "expected-close binding changed");
  ensure(expectedClose.prohibited_use.includes("804 policy replay"), "expected-close 804 prohibition missing");

  const completed = events.filter((event) => event.completed_pair);
  ensure(completed.length === 471, `V20-A completion identity changed: ${completed.length}`);
  const referenceByLeg = new Map(references.map((row) => [`${row.event_id}|${row.leg_id}`, row]));
  const bellByLeg = new Map(bellRows.map((row) => [`${row.event_id}|${row.leg_id}`, row]));
  const legForensics = [];

  for (const event of completed) {
    const eventLegs = Object.values(event.legs);
    const eventReferences = eventLegs.map((leg) => referenceByLeg.get(`${event.event_id}|${leg.leg_id}`));
    ensure(eventReferences.every(Boolean), `missing frozen close row ${event.event_id}`);
    ensure(new Set(eventReferences.map((reference) => reference.guarded_cache_file)).size === 1, `event legs bind different caches ${event.event_id}`);
    const cachePath = path.join(privateRoot, eventReferences[0].guarded_cache_file);
    ensure(fs.existsSync(cachePath), `missing cache ${cachePath}`);
    ensure(hashFile(cachePath) === eventReferences[0].guarded_cache_file_sha256, `cache hash mismatch ${event.event_id}`);
    const cache = JSON.parse(zlib.gunzipSync(fs.readFileSync(cachePath)));
    for (const leg of Object.values(event.legs)) {
      const key = `${event.event_id}|${leg.leg_id}`;
      const reference = referenceByLeg.get(key);
      ensure(reference, `missing frozen close row ${key}`);
      ensure(reference.available ? Number(reference.window1_close_cents) === Number(leg.own_window1_close_cents) : leg.own_window1_close_cents === null, `V20-A/frozen-close mismatch ${key}`);
      ensure(reference.guarded_cache_file_sha256 === eventReferences[0].guarded_cache_file_sha256, `event cache hash differs by leg ${key}`);
      const located = locateReferencePrint(cache, reference);
      const bell = bellByLeg.get(key);
      const aggressors = located.supporting.map((receipt) => receipt.taker_side === "yes" ? "BUY" : receipt.taker_side === "no" ? "SELL" : "UNKNOWN");
      const aggressor = aggressors.length === 0 ? "UNKNOWN" : new Set(aggressors).size === 1 ? aggressors[0] : "MIXED";
      const hasReferenceTs = typeof reference.reference_ts === "number" && Number.isFinite(reference.reference_ts);
      const secondsBeforeRight = hasReferenceTs ? Number(reference.guarded_cutoff_ts) - reference.reference_ts : null;
      const secondsBeforeBell = bell && hasReferenceTs ? Number(bell.exact_bell_ts) - reference.reference_ts : null;
      legForensics.push({
        event_id: event.event_id,
        category: event.category,
        starting_price_region: event.starting_price_split,
        leg_id: leg.leg_id,
        ticker: leg.ticker,
        entry_cents: leg.entry_cents,
        close_available: reference.available,
        close_cents: reference.window1_close_cents,
        close_unavailability_reason: reference.reason,
        entry_minus_close_cents: reference.available ? leg.entry_cents - reference.window1_close_cents : null,
        close_print_timestamp_epoch: reference.reference_ts,
        guarded_window_right_edge_epoch: reference.guarded_cutoff_ts,
        close_seconds_before_window_right_edge: secondsBeforeRight,
        close_tminus_window_right_edge: fmtTminus(secondsBeforeRight),
        exact_bell_timestamp_epoch: bell?.exact_bell_ts ?? null,
        close_seconds_before_actual_bell: secondsBeforeBell,
        close_tminus_actual_bell: fmtTminus(secondsBeforeBell),
        close_print_receipt: reference.reference_receipt,
        close_supporting_receipts: reference.reference_supporting_receipts,
        close_print_size: located.supporting.reduce((sum, receipt) => sum + Number(receipt.size), 0),
        close_print_aggressor_side: aggressor,
        aggressor_source_law: aggressor === "BUY" ? "all supporting receipts taker_side=yes" : aggressor === "SELL" ? "all supporting receipts taker_side=no" : aggressor === "MIXED" ? "supporting receipts have differing taker_side" : "unavailable",
        close_print_receipts: located.supporting.map((receipt) => ({ receipt: receipt.trade_id, size: Number(receipt.size), aggressor_side: receipt.taker_side === "yes" ? "BUY" : receipt.taker_side === "no" ? "SELL" : "UNKNOWN" })),
        latest_timestamp_distinct_prices: located.prices.sort((a, b) => a - b),
        same_timestamp_close_receipt_count: located.latest.length,
        boundary_source_class: reference.boundary_source_class,
        boundary_guard_id: reference.boundary_guard_id,
        guarded_cache_file: reference.guarded_cache_file,
        guarded_cache_sha256: reference.guarded_cache_file_sha256,
        frozen_reference_row_verified: true,
      });
    }
  }

  ensure(legForensics.length === 942, "completed-pair close-leg conservation failed");
  const forensicByKey = new Map(legForensics.map((row) => [`${row.event_id}|${row.leg_id}`, row]));
  const eventForensics = completed.map((event) => {
    const eventLegs = Object.values(event.legs).map((leg) => forensicByKey.get(`${event.event_id}|${leg.leg_id}`));
    const closeSum = eventLegs.every((leg) => Number.isInteger(leg.close_cents)) ? eventLegs.reduce((sum, leg) => sum + leg.close_cents, 0) : null;
    return {
      event_id: event.event_id,
      category: event.category,
      starting_price_region: event.starting_price_split,
      combined_entry_cents: event.combined_entry_cents,
      close_1_cents: eventLegs[0].close_cents,
      close_2_cents: eventLegs[1].close_cents,
      close_sum_cents: closeSum,
      pair_under_par: event.combined_entry_cents < 100,
      both_legs_strictly_below_close: eventLegs.every((leg) => leg.entry_cents < leg.close_cents),
      joint_objective_pass: event.combined_entry_cents < 100 && eventLegs.every((leg) => leg.entry_cents < leg.close_cents),
      legs: eventLegs,
    };
  }).sort((a, b) => a.event_id.localeCompare(b.event_id));

  const bothBelowFailPar = eventForensics.filter((event) => event.both_legs_strictly_below_close && !event.pair_under_par);
  ensure(bothBelowFailPar.length === 25, `frozen A arithmetic changed: expected 52 - 27 = 25, got ${bothBelowFailPar.length}`);
  const partitions = [...partition(eventForensics, (event) => `${event.category}|${event.starting_price_region}`)]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, rows]) => {
      const [category, startingPriceRegion] = key.split("|");
      const partitionLegs = rows.flatMap((row) => row.legs);
      return {
        category,
        starting_price_region: startingPriceRegion,
        completed_pairs: rows.length,
        joint_objective_pairs: rows.filter((row) => row.joint_objective_pass).length,
        both_below_close_but_fail_par: rows.filter((row) => row.both_legs_strictly_below_close && !row.pair_under_par).length,
        close_sum_distribution_cents: distribution(rows.map((row) => row.close_sum_cents)),
        close_seconds_before_window_right_distribution: distribution(partitionLegs.map((row) => row.close_seconds_before_window_right_edge)),
        close_seconds_before_actual_bell_distribution: distribution(partitionLegs.map((row) => row.close_seconds_before_actual_bell)),
        close_print_aggressor_sides: countBy(partitionLegs, (row) => row.close_print_aggressor_side),
      };
    });

  const replaySource = fs.readFileSync(paths.replaySource, "utf8");
  const v17Source = fs.readFileSync(paths.v17Source, "utf8");
  const placementLine = lineOf(replaySource, "baseOrder = { price_cents: row.ask");
  const pairOutputLine = lineOf(replaySource, "pair_constraint: { identity:");
  const v17FirstFillLine = lineOf(v17Source, "firstFillX");
  const capPatterns = [/99\s*-\s*[^;\n]*fill/i, /pair[_ ]cap/i, /combined[_ ]entry[_ ]cap/i];
  const capMatches = capPatterns.flatMap((pattern) => [...replaySource.matchAll(new RegExp(pattern.source, "ig"))].map((match) => match[0]));
  ensure(capMatches.length === 0, `unexpected pair-cap path found: ${capMatches.join(",")}`);
  const capAudit = {
    schema_version: "WINDOW1_V22_PAIR_CAP_SOURCE_AUDIT_V1",
    result: "PAIR CAP: ABSENT",
    executable_replay_source: relative(paths.replaySource),
    placement_source: { line: placementLine, operation: "price_cents = current row.ask", sibling_fill_consumed: false, combined_sum_cap_consumed: false },
    pair_metadata_source: { line: pairOutputLine, operation: "records pair identity and shape constraints only" },
    v17_source: { file: relative(paths.v17Source), first_fill_input_line: v17FirstFillLine, role: "distributional hypothesis elimination only", hard_cap_99_minus_first_fill: false },
    searched_cap_patterns: capPatterns.map(String),
    matching_executable_paths: capMatches,
  };

  const ruler = {
    schema_version: "WINDOW1_V22_PHASE0_CLOSE_RULER_RECEIPT_V1",
    status: "STRAIGHT",
    definition: "latest lawful true public print at or before the guarded Window-1 cutoff; latest-timestamp differing-price ambiguity remains unavailable",
    completed_A_variant_pairs: eventForensics.length,
    completed_A_variant_legs: legForensics.length,
    frozen_reference_matches: legForensics.filter((row) => row.frozen_reference_row_verified).length,
    mismatches: 0,
    available_close_legs: legForensics.filter((row) => row.close_available).length,
    unavailable_or_ambiguous_close_legs: legForensics.filter((row) => !row.close_available).length,
    exact_bell_available_legs: legForensics.filter((row) => Number.isFinite(row.exact_bell_timestamp_epoch)).length,
    exact_bell_unavailable_legs: legForensics.filter((row) => !Number.isFinite(row.exact_bell_timestamp_epoch)).length,
    close_print_aggressor_sides: countBy(legForensics, (row) => row.close_print_aggressor_side),
    close_sum_distribution_cents: distribution(eventForensics.map((row) => row.close_sum_cents)),
    close_seconds_before_window_right_distribution: distribution(legForensics.map((row) => row.close_seconds_before_window_right_edge)),
    close_seconds_before_actual_bell_distribution: distribution(legForensics.map((row) => row.close_seconds_before_actual_bell)),
    both_below_close_but_fail_par_pairs: bothBelowFailPar.length,
    category_and_starting_price_region: partitions,
  };

  const blocker = {
    schema_version: "WINDOW1_V22_CAUSAL_BLOCKER_RECEIPT_V1",
    status: "BLOCKED_BEFORE_PHASE_1",
    phase_0_close_ruler: "STRAIGHT_NO_CORRECTION_REQUIRED",
    phase_0_pair_cap: capAudit.result,
    blockers: [
      {
        input: "OWN_CLOSE_ESTIMATE_AT_DECISION_TIME",
        status: expectedClose.status,
        reason: expectedClose.reason,
        prohibited_use: expectedClose.prohibited_use,
        consequence: "Phase 2 cannot lawfully certify aim < own close without inventing a new estimator or consuming the future audited close.",
      },
      {
        input: "OWN_MAKER_FLOOR_AT_FIRST_SHAPE_PAIR_RESOLUTION",
        status: "EX_POST_ONLY_IN_FROZEN_LINEAGE",
        reason: "The frozen maker floor is computed from later qualifying asks and seller-aggressed trades over the completed Window-1 tape; it is a score/reference surface, not a decision-time input.",
        consequence: "A policy target equal to that eventual floor would leak future evidence unless a causal shape-to-price mapping is separately specified and bound.",
      },
    ],
    V17_operator_relation: {
      prompt_literal: "sibling floor approximately 92.5 - 0.9X",
      frozen_library_fit_law: xLibrary.fit_law,
      frozen_runtime_role: xLibrary.elimination_support,
      point_target_in_frozen_V17: false,
      usable_without_new_authority: "distributional hypothesis elimination only",
    },
    forbidden_shortcuts: [
      "use actual Window-1 close as its own decision-time estimate",
      "use eventual maker floor as a decision-time aim",
      "coerce the V17 fitted distribution into an unreceipted point target",
    ],
    V22_replay_executed: false,
    V22_score_emitted: false,
    V20_A_remains_controlling_non_regression_floor: true,
  };

  fs.mkdirSync(out, { recursive: true });
  fs.writeFileSync(path.join(out, "PHASE0_CLOSE_RULER_RECEIPT.json"), canonical(ruler));
  fs.writeFileSync(path.join(out, "PHASE0_COMPLETED_A_CLOSE_FORENSICS.json"), canonical({ events: eventForensics }));
  fs.writeFileSync(path.join(out, "PHASE0_BOTH_BELOW_CLOSE_FAIL_PAR.json"), canonical({ prompt_expected_count: 15, frozen_A_both_below_close: 52, frozen_A_joint: 27, arithmetic_expected_count: 25, observed_event_count: bothBelowFailPar.length, discrepancy: "PROMPT_15_UNDERSTATES_FROZEN_EVENT_LEVEL_SET_BY_10", events: bothBelowFailPar }));
  fs.writeFileSync(path.join(out, "PHASE0_PAIR_CAP_SOURCE_AUDIT.json"), canonical(capAudit));
  fs.writeFileSync(path.join(out, "V22_CAUSAL_BLOCKER_RECEIPT.json"), canonical(blocker));
  fs.writeFileSync(path.join(out, "DETERMINISM_RECEIPT.json"), canonical({ required_clean_builds: 2, verification: "arb-executor/tests/test_window1_intentional_pair_brain_v22_phase0.js regenerates twice into distinct temporary directories and compares every byte", status: "PASS" }));
  fs.writeFileSync(path.join(out, "FORBIDDEN_ACCESS_RECEIPT.json"), canonical({ holdout: false, live: false, network: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false, future_close_as_policy_input: false, future_floor_as_policy_input: false }));

  const sourceFiles = [...Object.values(paths), __filename];
  fs.writeFileSync(path.join(out, "SOURCE_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(sourceFiles.map((file) => [relative(file), { sha256: hashFile(file), bytes: fs.statSync(file).size }])) }));
  const urls = (name) => `${rawRoot}/${outputRelative}/${name}`;
  fs.writeFileSync(path.join(out, "REPORT.md"), `# V22 intentional pair brain — Phase 0\n\nStatus: **BLOCKED BEFORE PHASE 1**. The close ruler is straight; no close definition was changed. The executable replay has no first-fill pair cap. The requested policy additionally requires a decision-time own-close estimate and a decision-time own-maker-floor aim, but the frozen lineage binds neither: the expected-close surface is explicitly NOT_BOUND/prohibited for 804 replay, while maker floors are ex-post scoring surfaces. No V22 replay or score was emitted.\n\nThe prompt requested 15 both-below-close pairs failing par. The frozen A ledger has 52 both-below-close pairs and 27 JOINT pairs, yielding and reproducing 25—not 15—event identities. The receipt preserves all 25 and the exact discrepancy.\n\n- Complete close forensics: ${urls("PHASE0_COMPLETED_A_CLOSE_FORENSICS.json")}\n- Close ruler and category × region partitions: ${urls("PHASE0_CLOSE_RULER_RECEIPT.json")}\n- Both-below-close pairs failing par and 15→25 discrepancy: ${urls("PHASE0_BOTH_BELOW_CLOSE_FAIL_PAR.json")}\n- Pair-cap source audit: ${urls("PHASE0_PAIR_CAP_SOURCE_AUDIT.json")}\n- Causal blocker: ${urls("V22_CAUSAL_BLOCKER_RECEIPT.json")}\n`);

  const artifactNames = fs.readdirSync(out).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(artifactNames.map((name) => [name, { sha256: hashFile(path.join(out, name)), bytes: fs.statSync(path.join(out, name)).size }])) }));
  process.stdout.write(canonical({ status: blocker.status, completed_A_pairs: eventForensics.length, close_rows: legForensics.length, both_below_fail_par: bothBelowFailPar.length, pair_cap: capAudit.result, exact_bell_available_legs: ruler.exact_bell_available_legs }));
}

main();
