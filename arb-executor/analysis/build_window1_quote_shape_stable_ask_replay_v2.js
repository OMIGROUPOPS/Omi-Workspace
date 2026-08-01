#!/usr/bin/env node
"use strict";

// Cold, score-free five-game replay for the stable same-price ask correction.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const EVENTS = [
  "KXATPCHALLENGERMATCH-26JUL19HURBIG",
  "KXATPCHALLENGERMATCH-26JUL19NIKVRB",
  "KXATPMATCH-26JUL12LAJVAN",
  "KXWTACHALLENGERMATCH-26JUL16BRAVED",
  "KXWTAMATCH-26JUL20KORJIM",
].sort();
const TWO_GAME_EVENTS = new Set([
  "KXATPCHALLENGERMATCH-26JUL19HURBIG",
  "KXATPCHALLENGERMATCH-26JUL19NIKVRB",
]);

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function rel(repo, file) { return path.relative(repo, file).replaceAll("\\", "/"); }
function writeJson(file, value) { fs.writeFileSync(file, canonical(value)); }
function run(script, args, cwd) {
  const result = spawnSync(process.execPath, [script, ...args], { cwd, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });
  if (result.status !== 0) throw new Error(`${path.basename(script)} failed (${result.status})\n${result.stdout}\n${result.stderr}`);
  return result.stdout;
}
function hashFile(repo, file) { const bytes = fs.readFileSync(file); return { path: rel(repo, file), bytes: bytes.length, sha256: sha256(bytes) }; }
function signed(value) { return Number.isInteger(value) ? `${value >= 0 ? "+" : ""}${value}` : "NULL"; }

function main() {
  const args = process.argv.slice(2), value = (name, fallback) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : fallback; };
  const repo = path.resolve(value("--repo", "."));
  const privateRoot = path.resolve(value("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
  const outDir = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/quote_shape_stable_ask_20260731")));
  const workers = value("--workers", "8");
  const libraryBuilder = path.join(repo, "arb-executor/analysis/build_window1_quote_shape_library_v1.js");
  const replayBuilder = path.join(repo, "arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js");
  const microModule = path.join(repo, "arb-executor/analysis/window1_quote_shape_micro_position_v2.js");
  const oldReplayPath = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_elimination_20260731/TWO_GAME_REPLAY.json");
  const oldLibraryPath = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_elimination_20260731/QUOTE_SHAPE_LIBRARY.json");
  const oldDiagnosisPath = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_elimination_big_walk_20260731/BIG_ELIMINATION_DIAGNOSIS.json");
  const fiveFrozenPath = path.join(repo, ".claude/window1_live_v4_replay/five_exact_full_stack_capacity_20260731/FIVE_GAME_FULL_STACK_RESULTS.json");
  const referencePath = path.join(repo, ".claude/window1_live_v4_replay/live_book_initial_aim_20260731/REPLAY_AND_REFERENCE_PANEL.json");
  const quoteLedgerPath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
  const libraryPath = path.join(outDir, "QUOTE_SHAPE_LIBRARY_LEAVE_FIVE_OUT.json");
  const replayPath = path.join(outDir, "FIVE_GAME_REPLAY.json");
  fs.mkdirSync(outDir, { recursive: true });

  run(libraryBuilder, ["--repo", repo, "--private-root", privateRoot, "--output", libraryPath, "--exclude-events", EVENTS.join(","), "--workers", workers], repo);
  run(replayBuilder, ["--repo", repo, "--private-root", privateRoot, "--output", outDir, "--library", libraryPath, "--targets", EVENTS.join(","), "--receipt-name", path.basename(replayPath), "--stable-same-price-confirmation"], repo);

  const legacyDir = path.join(outDir, ".legacy_v1_byte_check");
  if (fs.existsSync(legacyDir)) throw new Error(`legacy check path already exists: ${legacyDir}`);
  fs.mkdirSync(legacyDir);
  run(replayBuilder, ["--repo", repo, "--private-root", privateRoot, "--output", legacyDir, "--library", oldLibraryPath], repo);
  const legacyNames = ["TWO_GAME_REPLAY.json", "HURBIG_QUOTE_SHAPE_REPLAY.svg", "NIKVRB_QUOTE_SHAPE_REPLAY.svg"];
  const legacyIdentity = legacyNames.map((name) => { const generated = fs.readFileSync(path.join(legacyDir, name)), frozen = fs.readFileSync(path.join(repo, ".claude/window1_live_v4_replay/quote_shape_elimination_20260731", name)); return { path: name, generated_sha256: sha256(generated), frozen_sha256: sha256(frozen), byte_identical: generated.equals(frozen) }; });
  fs.rmSync(legacyDir, { recursive: true });
  if (legacyIdentity.some((row) => !row.byte_identical)) throw new Error(`V1 byte identity failed: ${JSON.stringify(legacyIdentity)}`);

  const replay = JSON.parse(fs.readFileSync(replayPath));
  const library = JSON.parse(fs.readFileSync(libraryPath));
  const oldReplay = JSON.parse(fs.readFileSync(oldReplayPath));
  if (replay.events.length !== EVENTS.length || replay.events.map((event) => event.event_id).sort().join("|") !== EVENTS.join("|")) throw new Error("five-event replay identity mismatch");
  if (library.excluded_cold_test_events.join("|") !== EVENTS.join("|")) throw new Error("leave-five-out exclusion mismatch");

  const eventRows = replay.events.map((event) => {
    const legs = Object.entries(event.legs).sort().map(([legId, leg]) => ({
      leg_id: legId,
      status: leg.status,
      entry_cents: leg.entry_cents,
      pair_reference_cents: "NOT_BOUND",
      delta_to_pair_reference_cents: "NOT_BOUND",
      own_window1_close_cents: leg.own_window1_close_cents,
      delta_to_own_window1_close_cents: leg.delta_to_own_window1_close_cents,
      own_bell_price_cents: leg.own_bell_price_cents,
      delta_to_own_bell_price_cents: leg.delta_to_own_bell_price_cents,
      own_ask_reachable_low_cents: leg.own_ask_reachable_low_cents,
      delta_to_own_ask_reachable_low_cents: leg.delta_to_own_ask_reachable_low_cents,
      placement: leg.placement,
      fill: leg.fill,
      stable_same_price_rule_fired: leg.placement?.micro_position_evidence_type === "STRICTLY_LATER_SAME_PRICE_ASK_RECEIPT",
      surviving_shapes_at_placement: leg.surviving_shapes_at_placement,
      terminal_reason: leg.terminal_reason,
    }));
    const completed = legs.every((leg) => leg.status === "CREDITED");
    const combinedEntry = completed ? legs.reduce((sum, leg) => sum + leg.entry_cents, 0) : null;
    const combinedClose = legs.reduce((sum, leg) => sum + leg.own_window1_close_cents, 0);
    return { event_id: event.event_id, category: event.category, completed_pair: completed, combined_entry_cents: combinedEntry, combined_own_window1_close_cents: combinedClose, combined_delta_to_own_window1_closes_cents: completed ? combinedEntry - combinedClose : null, legs };
  });
  const byId = Object.fromEntries(eventRows.map((event) => [event.event_id, event]));
  const entry = (eventId, legId) => byId[eventId].legs.find((leg) => leg.leg_id === legId).entry_cents;
  const acceptance = {
    nikvrb_vrb_68: entry("KXATPCHALLENGERMATCH-26JUL19NIKVRB", "VRB") === 68,
    nikvrb_nik_18: entry("KXATPCHALLENGERMATCH-26JUL19NIKVRB", "NIK") === 18,
    hurbig_hur_38: entry("KXATPCHALLENGERMATCH-26JUL19HURBIG", "HUR") === 38,
    hurbig_big_55: entry("KXATPCHALLENGERMATCH-26JUL19HURBIG", "BIG") === 55,
  };
  if (Object.values(acceptance).some((passed) => !passed)) throw new Error(`required two-game acceptance failed: ${JSON.stringify(acceptance)}`);

  const allFills = eventRows.flatMap((event) => event.legs.filter((leg) => leg.fill).map((leg) => ({ event_id: event.event_id, ...leg })));
  const chronologyViolations = allFills.filter((leg) => !(leg.fill.evidence_ts > leg.placement.action_ts) || leg.fill.evidence_receipt === leg.placement.own_book_receipt_at_action);
  if (chronologyViolations.length) throw new Error(`fill chronology violation: ${JSON.stringify(chronologyViolations)}`);
  const stablePlacements = eventRows.flatMap((event) => event.legs.filter((leg) => leg.stable_same_price_rule_fired).map((leg) => ({ event_id: event.event_id, leg_id: leg.leg_id, action_ts: leg.placement.action_ts, price_cents: leg.placement.price_cents, own_receipt: leg.placement.own_book_receipt_at_action, sibling_receipt: leg.placement.sibling_book_receipt_at_action, fill_receipt: leg.fill?.evidence_receipt ?? null })));
  const oldById = Object.fromEntries(oldReplay.events.map((event) => [event.event_id, event]));
  const comparison = eventRows.filter((event) => TWO_GAME_EVENTS.has(event.event_id)).flatMap((event) => event.legs.map((leg) => { const before = oldById[event.event_id].legs[leg.leg_id]; return { event_id: event.event_id, leg_id: leg.leg_id, before_status: before.status, before_entry_cents: before.entry_cents, after_status: leg.status, after_entry_cents: leg.entry_cents, moved_cents: Number.isInteger(before.entry_cents) && Number.isInteger(leg.entry_cents) ? leg.entry_cents - before.entry_cents : null, stable_same_price_rule_fired: leg.stable_same_price_rule_fired }; }));

  const summary = {
    schema_version: "WINDOW1_QUOTE_SHAPE_STABLE_ASK_FIVE_GAME_SUMMARY_V2",
    cold: true,
    score_free: true,
    population_804_run: false,
    outcome_knowledge_consumed_by_decisions: false,
    event_count: eventRows.length,
    library_training_exclusions: library.excluded_cold_test_events,
    acceptance,
    completed_pair_count: eventRows.filter((event) => event.completed_pair).length,
    stable_same_price_placement_count: stablePlacements.length,
    strict_fill_chronology_violation_count: chronologyViolations.length,
    events: eventRows,
  };
  const twoGame = { schema_version: "WINDOW1_QUOTE_SHAPE_STABLE_ASK_TWO_GAME_SUBSET_V2", cold: true, score_free: true, source_five_game_replay_sha256: sha256(fs.readFileSync(replayPath)), events: eventRows.filter((event) => TWO_GAME_EVENTS.has(event.event_id)) };
  const transitionReceipt = {
    schema_version: "WINDOW1_STABLE_SAME_PRICE_TRANSITION_RECEIPT_V2",
    defect_source: hashFile(repo, oldDiagnosisPath),
    before_law: "own micro-position required ask_change_after_first_timestamp=true",
    after_law: "own micro-position accepts a distinct own ask receipt strictly later than the current ask-episode start when own receipt dwell>=10 seconds and displayed top-ask size>0; inverse sibling resolution remains independently required",
    placement_capacity_law: "top-ask displayed quantity >=5",
    fill_law: "a distinct own ask receipt with source timestamp strictly later than action; ask<=X; dwell>=10 seconds; displayed capacity at/below X>=5",
    same_receipt_action_fill_forbidden: true,
    stable_same_price_placements: stablePlacements,
    two_game_before_after: comparison,
    defect_effect: {
      before: "HURBIG BIG had no credited entry and the pair was incomplete",
      after: "BIG is credited at 55 on a distinct strictly later own ask receipt; HUR remains 38; combined entry is 93 versus combined own closes 102",
      moved: "BIG NULL->55; HUR 38->38; pair incomplete->complete; combined close delta NULL->-9"
    },
    strict_fill_chronology_violations: chronologyViolations,
  };
  writeJson(path.join(outDir, "FIVE_GAME_SUMMARY.json"), summary);
  writeJson(path.join(outDir, "TWO_GAME_SUBSET.json"), twoGame);
  writeJson(path.join(outDir, "STABLE_SAME_PRICE_TRANSITION_RECEIPT.json"), transitionReceipt);
  writeJson(path.join(outDir, "V1_BYTE_IDENTITY_RECEIPT.json"), { schema_version: "WINDOW1_QUOTE_SHAPE_V1_BYTE_IDENTITY_RECEIPT", default_v1_semantics_unchanged: true, files: legacyIdentity });

  const branchRaw = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/quote_shape_stable_ask_20260731";
  const table = eventRows.flatMap((event) => event.legs.map((leg) => `| ${event.event_id} | ${event.category} | ${leg.leg_id} | ${leg.status} | ${leg.entry_cents ?? "NULL"} | NOT_BOUND | NOT_BOUND | ${leg.own_window1_close_cents} | ${signed(leg.delta_to_own_window1_close_cents)} | ${leg.own_bell_price_cents} | ${signed(leg.delta_to_own_bell_price_cents)} | ${leg.own_ask_reachable_low_cents} | ${signed(leg.delta_to_own_ask_reachable_low_cents)} | ${leg.stable_same_price_rule_fired ? "FIRED" : "DID_NOT_FIRE"} |`));
  const pairTable = eventRows.map((event) => `| ${event.event_id} | ${event.completed_pair} | ${event.combined_entry_cents ?? "NULL"} | ${event.combined_own_window1_close_cents} | ${signed(event.combined_delta_to_own_window1_closes_cents)} |`);
  const report = [
    "# Stable same-price ask confirmation — two-game and five-game cold replay",
    "",
    "Score-free. No 804 replay. All five validation events were excluded before the quote-shape library was fitted.",
    "",
    `Raw five-game replay: ${branchRaw}/FIVE_GAME_REPLAY.json`,
    "",
    `Summary and per-leg references: ${branchRaw}/FIVE_GAME_SUMMARY.json`,
    "",
    `Transition receipt: ${branchRaw}/STABLE_SAME_PRICE_TRANSITION_RECEIPT.json`,
    "",
    "## Per-leg result",
    "",
    "| Event | Category | Leg | Status | Entry | Independent pair ref | Pair delta | Own W1 close | Delta | Bell | Delta | Ask-reachable low | Delta | Stable same-price rule |",
    "|---|---|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---|",
    ...table,
    "",
    "## Pair delta against both own closes",
    "",
    "| Event | Completed | Combined entry | Combined own closes | Signed delta |",
    "|---|---|---:|---:|---:|",
    ...pairTable,
    "",
    "## Causal law",
    "",
    "The same-price confirmation is an own-book receipt, not elapsed sibling-clock time. Placement may use it only after the inverse sibling direction is independently resolved. The placement receipt cannot fill the new order; credit requires a distinct own ask receipt with a strictly later source timestamp and proven five-contract displayed capacity.",
    "",
    "## Validation boundary",
    "",
    "This is five predeclared exact-start games, not the 804. No scoring, tuning, ranking, or population conclusion is authorized.",
    "",
  ].join("\n");
  fs.writeFileSync(path.join(outDir, "REPORT.md"), report);

  const sourceManifest = {
    schema_version: "WINDOW1_QUOTE_SHAPE_STABLE_ASK_SOURCE_MANIFEST_V2",
    sources: [libraryBuilder, replayBuilder, microModule, __filename, oldReplayPath, oldLibraryPath, oldDiagnosisPath, fiveFrozenPath, referencePath, quoteLedgerPath].map((file) => hashFile(repo, file)),
    private_tick_sources: "hash-bound individually inside QUOTE_SHAPE_LIBRARY_LEAVE_FIVE_OUT.json",
    forbidden_sources: ["holdout", "live", "orders", "positions", "exits", "settlement", "DCA", "Window 2"],
  };
  writeJson(path.join(outDir, "SOURCE_HASH_MANIFEST.json"), sourceManifest);
  const artifactNames = fs.readdirSync(outDir).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  writeJson(path.join(outDir, "ARTIFACT_HASH_MANIFEST.json"), { schema_version: "WINDOW1_QUOTE_SHAPE_STABLE_ASK_ARTIFACT_MANIFEST_V2", artifacts: artifactNames.map((name) => hashFile(outDir, path.join(outDir, name))) });
  process.stdout.write(canonical({ status: "BUILT", acceptance, completed_pair_count: summary.completed_pair_count, stable_same_price_placement_count: stablePlacements.length, events: eventRows.map((event) => ({ event_id: event.event_id, completed_pair: event.completed_pair, combined_entry_cents: event.combined_entry_cents, combined_close_cents: event.combined_own_window1_close_cents, combined_delta_cents: event.combined_delta_to_own_window1_closes_cents, legs: Object.fromEntries(event.legs.map((leg) => [leg.leg_id, { entry: leg.entry_cents, close: leg.own_window1_close_cents, low: leg.own_ask_reachable_low_cents, stable_same_price_rule_fired: leg.stable_same_price_rule_fired }])) })) }));
}

main();
