#!/usr/bin/env node
"use strict";

// Diagnostic-only expansion of the frozen quote-shape gate at every joint tick.
// It imports the committed gate helpers by source transformation and never
// changes placement, fill, library, or replay state.

const crypto = require("crypto");
const fs = require("fs");
const Module = require("module");
const path = require("path");

const repo = path.resolve(process.argv[2] || ".");
const eventId = "KXATPCHALLENGERMATCH-26JUL19HURBIG";
const outDir = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_elimination_big_walk_20260731");
const gatePath = path.join(repo, "arb-executor/analysis/build_window1_quote_shape_elimination_replay_v1.js");
const libraryPath = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_elimination_20260731/QUOTE_SHAPE_LIBRARY.json");
const replayPath = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_elimination_20260731/TWO_GAME_REPLAY.json");
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const windowsPath = path.join(repo, ".claude/window1_live_v4_replay/five_exact_full_stack_capacity_20260731/FIVE_GAME_FULL_STACK_RESULTS.json");
const testPath = path.join(repo, "arb-executor/tests/test_hurbig_big_elimination_tick_walk_v1.js");
const DWELL_SECONDS = 10;
const QUANTITY = 5;

function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function parseCsv(text) { const lines = text.trimEnd().split(/\r?\n/), headers = lines.shift().split(","); return lines.map((line) => Object.fromEntries(line.split(",").map((value, index) => [headers[index], value]))); }
function csvCell(value) { if (value === null || value === undefined) return ""; const text = typeof value === "string" ? value : JSON.stringify(value); return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text; }
function region(price) { return price <= 25 ? "le25" : price <= 50 ? "26_50" : price <= 75 ? "51_75" : "ge76"; }
function tminus(seconds) { return seconds >= 0 ? `T-${seconds}s` : `T+${-seconds}s`; }

function loadFrozenHelpers() {
  const source = fs.readFileSync(gatePath, "utf8");
  const replacement = "\nmodule.exports = { loadRows, prefixRows, compatibleShapes, shapeVerdict, directionOf, inverseDirection, directionObserved };\n";
  const patched = source.replace(/\nmain\(\);\s*$/, replacement);
  if (patched === source) throw new Error("unable to expose frozen gate helpers");
  const loaded = new Module(`${gatePath}#diagnostic`, module);
  loaded.filename = gatePath;
  loaded.paths = Module._nodeModulePaths(path.dirname(gatePath));
  loaded._compile(patched, gatePath);
  return loaded.exports;
}

function evaluateState(leg, sibling, row, shapes, tuples, helpers) {
  const verdicts = shapes.map((shapeId) => ({ shape_id: shapeId, verdict: helpers.shapeVerdict(leg.group, shapeId, row.progress_bin) }));
  let state = "INSUFFICIENT_EVIDENCE", reason = "SURVIVING_SHAPES_DISAGREE_OR_LIBRARY_GAP";
  if (row.raw_row_count < 2) reason = "NO_PRIOR_IN_WINDOW_BOOK";
  else if (shapes.length && verdicts.every((item) => item.verdict === "LOWER")) { state = "HOLD"; reason = "ALL_SURVIVING_SHAPES_SAY_LOWER"; }
  else if (shapes.length && verdicts.every((item) => item.verdict === "FLOOR")) {
    if (!leg.last.ask_change_after_first_timestamp) reason = "FLOOR_CONSENSUS_BUT_OWN_MICRO_POSITION_UNOBSERVED";
    else if (!leg.resolved_direction || !sibling.independent_direction || helpers.inverseDirection(leg.resolved_direction) !== sibling.independent_direction || !helpers.directionObserved(sibling, sibling.independent_direction)) reason = "FLOOR_CONSENSUS_BUT_SIBLING_DIRECTION_NOT_INDEPENDENTLY_OBSERVED";
    else if (row.prefix.ask_net !== row.prefix.ask_dip) reason = "FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW";
    else if (row.ask_dwell_seconds >= DWELL_SECONDS && row.top_ask_size >= QUANTITY) { state = "PLACE"; reason = "ALL_SURVIVING_PAIR_CONSTRAINED_SHAPES_SAY_FLOOR_AND_ASK_IS_EXECUTABLE"; }
    else reason = "FLOOR_CONSENSUS_BUT_MICRO_MICRO_NOT_READY";
  }
  return { state, reason, verdicts, pair_tuple_count: tuples.length };
}

function main() {
  const helpers = loadFrozenHelpers();
  const library = JSON.parse(fs.readFileSync(libraryPath));
  const frozenReplay = JSON.parse(fs.readFileSync(replayPath));
  const quoteRows = parseCsv(fs.readFileSync(quotePath, "utf8")).filter((row) => row.event_id === eventId);
  const windows = JSON.parse(fs.readFileSync(windowsPath));
  const eventWindow = windows.events.find((event) => event.event_id === eventId).window;
  const sources = quoteRows.map((row) => ({ event_id: row.event_id, category: row.category, leg: row.leg, ticker: row.ticker, left: Number(row.left_ts), right: Number(row.right_ts), scheduled: Number(row.scheduled_start_ts), bell: Number(eventWindow.actual_bell_ts) }));
  const legs = sources.map((source) => {
    const loaded = helpers.loadRows(source), rows = helpers.prefixRows(loaded.rows, source.left, source.right);
    return { ...source, rows, first_ask: loaded.rows[0].ask, first_bid: loaded.rows[0].bid, price_region: region(loaded.rows[0].bid), last: null, survivor_shapes: null, resolved_direction: null, independent_direction: null };
  }).sort((a, b) => a.leg.localeCompare(b.leg));
  const high = [...legs].sort((a, b) => b.first_ask - a.first_ask || a.leg.localeCompare(b.leg))[0], low = legs.find((leg) => leg !== high);
  const pairKey = `${high.category}|${high.price_region}|${low.price_region}`, tuplesObject = library.pair_shape_tuples[pairKey] || {};
  let tuples = Object.keys(tuplesObject).map((key) => { const [highShape, lowShape] = key.split("|"); return { highShape, lowShape, n: tuplesObject[key] }; });
  for (const leg of legs) { leg.group = library.groups[`${leg.category}|${leg.price_region}`]; leg.survivor_shapes = leg.group.shapes.map((shape) => shape.shape_id); }
  const indices = Object.fromEntries(legs.map((leg) => [leg.leg, 0])), clock = [...new Set(legs.flatMap((leg) => leg.rows.map((row) => row.ts)))].sort((a, b) => a - b), trace = [], material = [];
  for (let tick = 0; tick < clock.length; tick += 1) {
    const ts = clock[tick], triggerLegs = [];
    for (const leg of legs) {
      let changed = false;
      while (indices[leg.leg] < leg.rows.length && leg.rows[indices[leg.leg]].ts <= ts) { leg.last = leg.rows[indices[leg.leg]++]; changed = true; }
      if (changed) triggerLegs.push(leg.leg);
      if (changed && (leg === high || high.last)) {
        leg.survivor_shapes = helpers.compatibleShapes(leg.group, leg.last, leg.survivor_shapes);
        const ownDirections = [...new Set(leg.survivor_shapes.map(helpers.directionOf))];
        if (!leg.independent_direction && ownDirections.length === 1 && ownDirections[0] !== "UNKNOWN") leg.independent_direction = ownDirections[0];
      }
      const directions = [...new Set(leg.survivor_shapes.map(helpers.directionOf))];
      if (!leg.resolved_direction && directions.length === 1 && directions[0] !== "UNKNOWN") leg.resolved_direction = directions[0];
    }
    for (const sourceLeg of legs) {
      if (!sourceLeg.resolved_direction) continue;
      const sibling = legs.find((leg) => leg !== sourceLeg); if (sibling.resolved_direction) continue;
      const required = helpers.inverseDirection(sourceLeg.resolved_direction), constrained = sibling.survivor_shapes.filter((shapeId) => helpers.directionOf(shapeId) === required);
      if (constrained.length) sibling.survivor_shapes = constrained;
    }
    tuples = tuples.filter((tuple) => high.survivor_shapes.includes(tuple.highShape) && low.survivor_shapes.includes(tuple.lowShape));
    const big = legs.find((leg) => leg.leg === "BIG"), hur = legs.find((leg) => leg.leg === "HUR");
    if (!big.last) continue;
    const bigRow = { ...big.last, ts, ask_dwell_seconds: big.last.ask_dwell_seconds + (ts - big.last.ts), progress_bin: Math.max(0, Math.min(100, Math.floor((ts - big.left) / (big.right - big.left) * 100))) };
    const hurRow = hur.last ? { ...hur.last, ts, ask_dwell_seconds: hur.last.ask_dwell_seconds + (ts - hur.last.ts), progress_bin: Math.max(0, Math.min(100, Math.floor((ts - hur.left) / (hur.right - hur.left) * 100))) } : null;
    const bigShapes = [...new Set(tuples.map((tuple) => tuple.highShape))], evaluated = evaluateState(big, hur, bigRow, bigShapes, tuples, helpers);
    const row = {
      tick: trace.length + 1,
      epoch: ts,
      tminus_scheduled_seconds: big.scheduled - ts,
      tminus_bell_seconds: big.bell - ts,
      trigger_legs: triggerLegs.join("+"),
      big_bid: bigRow.bid,
      big_ask: bigRow.ask,
      big_spread: bigRow.spread,
      big_carried_last: bigRow.carried_last,
      big_ask_dwell_seconds: bigRow.ask_dwell_seconds,
      big_top_ask_size: bigRow.top_ask_size,
      big_top5_ask_depth: bigRow.top5_ask_depth,
      big_ask_net: bigRow.prefix.ask_net,
      big_ask_dip: bigRow.prefix.ask_dip,
      big_own_later_ask_transition: bigRow.ask_change_after_first_timestamp,
      big_surviving_shapes: evaluated.verdicts.map((item) => `${item.shape_id}:${item.verdict}`).join("|"),
      big_pair_tuple_count: evaluated.pair_tuple_count,
      big_state: evaluated.state,
      big_reason: evaluated.reason,
      big_receipt: big.last.receipt,
      hur_bid: hurRow?.bid ?? null,
      hur_ask: hurRow?.ask ?? null,
      hur_spread: hurRow?.spread ?? null,
      hur_carried_last: hurRow?.carried_last ?? null,
      hur_ask_dwell_seconds: hurRow?.ask_dwell_seconds ?? null,
      hur_top_ask_size: hurRow?.top_ask_size ?? null,
      hur_top5_ask_depth: hurRow?.top5_ask_depth ?? null,
      hur_ask_net: hurRow?.prefix.ask_net ?? null,
      hur_independent_direction: hur.independent_direction,
      hur_direction_observed: hur.independent_direction ? helpers.directionObserved(hur, hur.independent_direction) : false,
      hur_receipt: hur.last?.receipt ?? null
    };
    trace.push(row);
    const prior = material[material.length - 1]; if (!prior || prior.big_state !== row.big_state || row.big_state === "PLACE") material.push(row);
  }
  const frozenBig = frozenReplay.events.find((event) => event.event_id === eventId).legs.BIG, fields = ["epoch", "big_state", "big_reason", "big_bid", "big_ask", "big_ask_dwell_seconds", "big_receipt"];
  const expected = frozenBig.decision_changes.map((row) => ({ epoch: row.ts, big_state: row.state, big_reason: row.reason, big_bid: row.book?.bid ?? null, big_ask: row.book?.ask ?? null, big_ask_dwell_seconds: row.book?.ask_dwell_seconds ?? null, big_receipt: row.receipt }));
  const selfCheckMismatches = [];
  for (let i = 0; i < Math.max(material.length, expected.length); i += 1) for (const field of fields) if ((material[i]?.[field] ?? null) !== (expected[i]?.[field] ?? null)) selfCheckMismatches.push({ index: i, field, diagnostic: material[i]?.[field] ?? null, frozen: expected[i]?.[field] ?? null });
  const headers = Object.keys(trace[0]), csv = `${headers.join(",")}\n${trace.map((row) => headers.map((key) => csvCell(row[key])).join(",")).join("\n")}\n`;
  const ask55 = trace.filter((row) => row.big_ask === 55), firstFloorConsensus = trace.find((row) => row.big_ask === 55 && row.big_surviving_shapes && row.big_surviving_shapes.split("|").every((shape) => shape.endsWith(":FLOOR")));
  const firstSiblingDirectionObserved = trace.find((row) => row.hur_direction_observed);
  const summary = {
    schema_version: "HURBIG_BIG_ELIMINATION_TICK_WALK_V1",
    diagnostic_only: true,
    gate_changed: false,
    event_id: eventId,
    leg_id: "BIG",
    joint_ticks: trace.length,
    own_big_trigger_ticks: trace.filter((row) => row.trigger_legs.split("+").includes("BIG")).length,
    sibling_hur_trigger_ticks: trace.filter((row) => row.trigger_legs.split("+").includes("HUR")).length,
    first_observed_floor: ask55.length ? { epoch: ask55[0].epoch, tminus_scheduled_seconds: ask55[0].tminus_scheduled_seconds, tminus_bell_seconds: ask55[0].tminus_bell_seconds, bid: ask55[0].big_bid, ask: 55, spread: ask55[0].big_spread, carried_last: ask55[0].big_carried_last, dwell_seconds: ask55[0].big_ask_dwell_seconds, top_ask_size: ask55[0].big_top_ask_size, top5_ask_depth: ask55[0].big_top5_ask_depth, state: ask55[0].big_state, reason: ask55[0].big_reason, survivors: ask55[0].big_surviving_shapes, receipt: ask55[0].big_receipt } : null,
    ask55_last_observed: ask55.length ? { epoch: ask55[ask55.length - 1].epoch, tminus_scheduled_seconds: ask55[ask55.length - 1].tminus_scheduled_seconds, tminus_bell_seconds: ask55[ask55.length - 1].tminus_bell_seconds, bid: ask55[ask55.length - 1].big_bid, ask: 55, spread: ask55[ask55.length - 1].big_spread, carried_last: ask55[ask55.length - 1].big_carried_last, dwell_seconds: ask55[ask55.length - 1].big_ask_dwell_seconds, top_ask_size: ask55[ask55.length - 1].big_top_ask_size, top5_ask_depth: ask55[ask55.length - 1].big_top5_ask_depth, state: ask55[ask55.length - 1].big_state, reason: ask55[ask55.length - 1].big_reason, survivors: ask55[ask55.length - 1].big_surviving_shapes, receipt: ask55[ask55.length - 1].big_receipt } : null,
    ask55_joint_ticks: ask55.length,
    ask55_max_continuous_dwell_seconds: Math.max(...ask55.map((row) => row.big_ask_dwell_seconds)),
    first_floor_consensus: firstFloorConsensus ? { epoch: firstFloorConsensus.epoch, tminus_scheduled_seconds: firstFloorConsensus.tminus_scheduled_seconds, tminus_bell_seconds: firstFloorConsensus.tminus_bell_seconds, bid: firstFloorConsensus.big_bid, ask: firstFloorConsensus.big_ask, spread: firstFloorConsensus.big_spread, carried_last: firstFloorConsensus.big_carried_last, dwell_seconds: firstFloorConsensus.big_ask_dwell_seconds, top_ask_size: firstFloorConsensus.big_top_ask_size, top5_ask_depth: firstFloorConsensus.big_top5_ask_depth, state: firstFloorConsensus.big_state, reason: firstFloorConsensus.big_reason, survivors: firstFloorConsensus.big_surviving_shapes, hur_ask: firstFloorConsensus.hur_ask, hur_ask_net: firstFloorConsensus.hur_ask_net, hur_independent_direction: firstFloorConsensus.hur_independent_direction, hur_direction_observed: firstFloorConsensus.hur_direction_observed, receipt: firstFloorConsensus.big_receipt } : null,
    first_sibling_direction_observed: firstSiblingDirectionObserved ? { epoch: firstSiblingDirectionObserved.epoch, tminus_scheduled_seconds: firstSiblingDirectionObserved.tminus_scheduled_seconds, tminus_bell_seconds: firstSiblingDirectionObserved.tminus_bell_seconds, big_bid: firstSiblingDirectionObserved.big_bid, big_ask: firstSiblingDirectionObserved.big_ask, big_spread: firstSiblingDirectionObserved.big_spread, big_carried_last: firstSiblingDirectionObserved.big_carried_last, big_ask_dwell_seconds: firstSiblingDirectionObserved.big_ask_dwell_seconds, big_survivors: firstSiblingDirectionObserved.big_surviving_shapes, pair_tuple_count: firstSiblingDirectionObserved.big_pair_tuple_count, hur_bid: firstSiblingDirectionObserved.hur_bid, hur_ask: firstSiblingDirectionObserved.hur_ask, hur_spread: firstSiblingDirectionObserved.hur_spread, hur_carried_last: firstSiblingDirectionObserved.hur_carried_last, hur_ask_dwell_seconds: firstSiblingDirectionObserved.hur_ask_dwell_seconds, hur_ask_net: firstSiblingDirectionObserved.hur_ask_net, hur_direction: firstSiblingDirectionObserved.hur_independent_direction, state: firstSiblingDirectionObserved.big_state, reason: firstSiblingDirectionObserved.big_reason, big_receipt: firstSiblingDirectionObserved.big_receipt, hur_receipt: firstSiblingDirectionObserved.hur_receipt } : null,
    first_own_later_ask_transition: (() => { const row = trace.find((item) => item.big_own_later_ask_transition); return row ? { epoch: row.epoch, bid: row.big_bid, ask: row.big_ask, ask_net: row.big_ask_net, ask_dip: row.big_ask_dip, state: row.big_state, reason: row.big_reason, receipt: row.big_receipt } : null; })(),
    states: Object.fromEntries([...new Set(trace.map((row) => row.big_state))].sort().map((state) => [state, trace.filter((row) => row.big_state === state).length])),
    reasons: Object.fromEntries([...new Set(trace.map((row) => row.big_reason))].sort().map((reason) => [reason, trace.filter((row) => row.big_reason === reason).length])),
    material_state_changes_match_frozen_replay: selfCheckMismatches.length === 0,
    self_check_mismatches: selfCheckMismatches,
    conclusion: "SINGLE_VISIT_FLOOR_STRUCTURAL_WEAKNESS",
    conclusion_basis: "BIG ask 55 arrived on the first formed tick and remained continuously displayed while quote, size, depth, bid, last-trade, and sibling ticks accumulated. The survivor set reached UP_CONTINUATION:FLOOR before the ask left 55, but PLACE remained unavailable solely because BIG had no later-timestamp own ask transition. HURs independently observed DOWN direction was consumed by the pair constraint but could not satisfy BIGs own-micro-position gate."
  };
  const branchRaw = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated";
  const rawWalk = `${branchRaw}/.claude/window1_live_v4_replay/quote_shape_elimination_big_walk_20260731/BIG_EVERY_JOINT_TICK_ELIMINATION_WALK.csv`;
  const rawDiagnosis = `${branchRaw}/.claude/window1_live_v4_replay/quote_shape_elimination_big_walk_20260731/BIG_ELIMINATION_DIAGNOSIS.json`;
  const keyRows = [
    trace[0],
    trace.find((row) => row.big_reason === "SURVIVING_SHAPES_DISAGREE_OR_LIBRARY_GAP"),
    firstFloorConsensus,
    trace.find((row) => row.big_state === "HOLD"),
    trace.find((row) => row.big_ask === 55 && row.big_carried_last === 55 && row.big_reason === "FLOOR_CONSENSUS_BUT_OWN_MICRO_POSITION_UNOBSERVED"),
    firstSiblingDirectionObserved,
    trace.find((row) => row.big_own_later_ask_transition),
    trace.find((row) => row.big_state === "HOLD" && row.big_ask === 60),
    trace.find((row) => row.big_reason === "FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW" && row.big_ask === 59),
  ].filter((row, index, rows) => row && rows.findIndex((other) => other.epoch === row.epoch && other.big_reason === row.big_reason) === index);
  const report = [
    "# BIG every-tick elimination diagnosis",
    "",
    "Diagnostic only. The frozen gate, library, replay, placements, and fills are unchanged.",
    "",
    `Complete ${trace.length.toLocaleString("en-US")} joint-tick walk: ${rawWalk}`,
    "",
    `Machine-readable diagnosis: ${rawDiagnosis}`,
    "",
    "## Material chronology",
    "",
    "The table is a compact index. The linked CSV contains every tick, including both clocks, the joint BIG bid/ask/last/spread/dwell observation, the surviving set, pair-tuple count, state, named missing proof, trigger leg, and both receipts.",
    "",
    "| Tick | T-minus scheduled | T-minus bell | BIG bid / ask / last / spread / ask dwell | Surviving BIG shapes | State | Exact missing proof or action | HUR bid / ask / last / direction observed |",
    "|---:|---:|---:|---|---|---|---|---|",
    ...keyRows.map((row) => `| ${row.tick} | ${tminus(Number(row.tminus_scheduled_seconds))} | ${tminus(Number(row.tminus_bell_seconds))} | ${row.big_bid} / ${row.big_ask} / ${row.big_carried_last ?? "not available"} / ${row.big_spread} / ${row.big_ask_dwell_seconds}s | ${row.big_surviving_shapes.replaceAll("|", "<br>")} | ${row.big_state} | ${row.big_reason} | ${row.hur_bid ?? "not available"} / ${row.hur_ask ?? "not available"} / ${row.hur_carried_last ?? "not available"} / ${row.hur_direction_observed ? row.hur_independent_direction : "not yet independently observed"} |`),
    "",
    "## Answers",
    "",
    "1. **The floor did not arrive too early and disappear before resolution.** BIG's ask 55 was the first formed ask, remained continuously displayed through its last 55 receipt, and accumulated repeated lawful joint ticks. The eliminator reduced BIG to one `UP_CONTINUATION` shape and called `FLOOR` while 55 was still displayed. This was not an evidence-window miss.",
    "",
    "2. **This trace exposes the single-visit-floor structural weakness.** `PLACE` was withheld because `ask_change_after_first_timestamp=false`. When BIG finally supplied a later own-ask transition, the ask had risen above the observed low, so `ask_net != ask_dip` withheld placement. The gate therefore accepts recurrent returns such as VRB but cannot act on a continuously displayed first floor, even after the shape has resolved.",
    "",
    "## Pair constraint",
    "",
    "The eliminator does consume the sibling. HUR's independently observed `DOWN` direction reduces the pair to the inverse `BIG UP_CONTINUATION | HUR DOWN_CONTINUATION` tuple. It still cannot authorize BIG because the micro-micro gate separately requires a later-timestamp transition on BIG's own ask. Sibling evidence constrains the shape set; it does not satisfy that own-leg reachability clause.",
    "",
    "## Evidence a single visit actually supplied",
    "",
    "Without changing the gate, this trace lawfully exposes these contemporaneous inputs: continuous ask-55 dwell; positive displayed ask size and top-five ask depth; repeated raw BBO receipts with authoritative chronology; the joint bid/ask/last/spread observation as bid, last, size, depth, and spread evolve while ask stays 55; and HUR's independently resolved inverse direction. Ask reach remains ask-side only. None of these facts permits same-receipt fill credit, and no new threshold is proposed here.",
    "",
    "## Validation boundary",
    "",
    "This is one cold-game diagnostic against the already frozen two-game replay. It does not validate a replacement gate on the 804 and makes no population claim.",
    "",
  ].join("\n");
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(path.join(outDir, "BIG_EVERY_JOINT_TICK_ELIMINATION_WALK.csv"), csv);
  fs.writeFileSync(path.join(outDir, "BIG_ELIMINATION_DIAGNOSIS.json"), canonical(summary));
  fs.writeFileSync(path.join(outDir, "REPORT.md"), report);
  fs.writeFileSync(path.join(outDir, "SOURCE_HASHES.json"), canonical({ diagnostic_builder: { path: path.relative(repo, __filename).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(__filename)) }, diagnostic_test: { path: path.relative(repo, testPath).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(testPath)) }, gate: { path: path.relative(repo, gatePath).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(gatePath)) }, library: { path: path.relative(repo, libraryPath).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(libraryPath)) }, frozen_replay: { path: path.relative(repo, replayPath).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(replayPath)) }, quote_ledger: { path: path.relative(repo, quotePath).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(quotePath)) }, window_source: { path: path.relative(repo, windowsPath).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(windowsPath)) }, tick_walk: { path: "BIG_EVERY_JOINT_TICK_ELIMINATION_WALK.csv", bytes: Buffer.byteLength(csv), sha256: sha256(Buffer.from(csv)) } }));
  const artifacts = ["BIG_EVERY_JOINT_TICK_ELIMINATION_WALK.csv", "BIG_ELIMINATION_DIAGNOSIS.json", "REPORT.md", "SOURCE_HASHES.json"];
  fs.writeFileSync(path.join(outDir, "ARTIFACT_HASH_MANIFEST.json"), canonical({ schema_version: "HURBIG_BIG_ELIMINATION_ARTIFACT_HASH_MANIFEST_V1", artifacts: artifacts.map((name) => { const bytes = fs.readFileSync(path.join(outDir, name)); return { path: name, bytes: bytes.length, sha256: sha256(bytes) }; }) }));
  process.stdout.write(canonical(summary));
}

main();
