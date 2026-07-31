#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { runColdReplay } = require("./nikvrb_sibling_shape_cold_replay.js");

const repo = path.resolve(process.argv[2] || ".");
const checkOnly = process.argv.includes("--check");
const outDir = path.join(repo, ".claude/window1_live_v4_replay/nikvrb_sibling_shape_tune_20260731");
const reportPath = path.join(repo, "arb-executor/docs/research/window1/NIKVRB_SIBLING_SHAPE_REPLAY.md");

const INPUTS = {
  clock: [
    ".claude/window1_live_v4_replay/nikvrb_coupling_20260730/NIKVRB_DUAL_BOOK_CLOCK.csv",
    "9ec9ef0fab27cd750a7d3fba1407bc6c6a8955104071f27b67dac6bd7f8965e5",
  ],
  trace: [
    ".claude/window1_live_v4_replay/one_game_nikvrb_20260730/NIKVRB_DECISION_TRACE.json",
    "cf3ecdafc43ff0305ae95addd5a98fc1d53695dbbeae6c7080ad79de0fae1b42",
  ],
  ask68: [
    ".claude/window1_live_v4_replay/nikvrb_decision_autopsy_20260731/NIKVRB_VRB_ASK68_VISITS.csv",
    "383089cc2bf24f060e21de92fb53656341d38a956d49e946434fc6186129f9c1",
  ],
  prior_tree: [
    ".claude/window1_live_v4_replay/nikvrb_decision_tree_20260731/NIKVRB_COUNTERFACTUAL_BRANCHES.json",
    "939064abd665a37644644300ecc622a10384cf4ffcc5f41d0e21d45659137962",
  ],
  live_v4: [
    "arb-executor/live_v4.py",
    "f6fb1d20f3943f7bac26d94ccf1e9d98a5f22762cd3357394adfc8a3b108d760",
  ],
  deploy_config: [
    "arb-executor/config/deploy_v5_live.json",
    "46607d2404d6794c30c6c61fd52d08c9e787a613a1984d8c21204457d5d2472f",
  ],
  time_axis: [
    "arb-executor/analysis/aim_time_axis.py",
    "5cab94e67060cc1bda186fb5ca2fbcde1ab02ce64fd1762209983b02514221ca",
  ],
};

function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function canonical(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
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
      } else if (ch === '"') quoted = false;
      else field += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === ",") {
      row.push(field);
      field = "";
    } else if (ch === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else field += ch;
  }
  if (field || row.length) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }
  const headers = rows.shift();
  return rows.filter((r) => r.length === headers.length)
    .map((r) => Object.fromEntries(headers.map((h, i) => [h, r[i]])));
}

function gzipJsonlBase64(rows) {
  const text = `${rows.map((row) => JSON.stringify(row)).join("\n")}\n`;
  return `${zlib.gzipSync(Buffer.from(text), { level: 9, mtime: 0 }).toString("base64")}\n`;
}

function cleanText(value) {
  return String(value === null || value === undefined ? "" : value).replace(/\|/g, "\\|").replace(/\n/g, " ");
}

const sourceBytes = {};
const sourceManifest = [];
for (const [id, [relative, expected]] of Object.entries(INPUTS)) {
  const bytes = fs.readFileSync(path.join(repo, relative));
  const actual = sha256(bytes);
  if (actual !== expected) throw new Error(`${id} source mismatch ${actual} != ${expected}`);
  sourceBytes[id] = bytes;
  sourceManifest.push({ id, path: relative, bytes: bytes.length, sha256: actual });
}

const rawClock = parseCsv(sourceBytes.clock.toString("utf8"));
const trace = JSON.parse(sourceBytes.trace.toString("utf8"));
const visits = parseCsv(sourceBytes.ask68.toString("utf8"));
if (rawClock.length !== 13123 || visits.length !== 9 || trace.consultations.length !== 5) {
  throw new Error(`frozen input mismatch rows=${rawClock.length} visits=${visits.length} calls=${trace.consultations.length}`);
}

const current = runColdReplay({ rawRows: rawClock, trace, scenario: "current" });
const tuned = runColdReplay({ rawRows: rawClock, trace, scenario: "tuned" });

const expected = {
  vrb_fill_price: 69,
  vrb_fill_et: "2026-07-19T07:15:22.000000-04:00",
  patience_arm_et: "2026-07-19T10:30:39.000000-04:00",
  patience_arm_bid: 24,
  faller_release_et: "2026-07-19T10:40:57.000000-04:00",
  faller_target: 19,
  nik_fill_et: "2026-07-19T11:09:20.922837-04:00",
  nik_fill_price: 19,
};

const tunedPlace = tuned.material_decisions.find((row) => row.action === "PLACE_NIK_19");
if (!tuned.fills.VRB || tuned.fills.VRB.price !== expected.vrb_fill_price
    || tuned.fills.VRB.evidence_et !== expected.vrb_fill_et
    || !tuned.patience || tuned.patience.armed_et !== expected.patience_arm_et
    || tuned.patience.arm_bid !== expected.patience_arm_bid
    || !tunedPlace || tunedPlace.timestamp_et !== expected.faller_release_et
    || !tuned.fills.NIK || tuned.fills.NIK.price !== expected.nik_fill_price
    || tuned.fills.NIK.evidence_et !== expected.nik_fill_et) {
  throw new Error(`cold replay acceptance mismatch ${JSON.stringify({ fills: tuned.fills, patience: tuned.patience, tunedPlace })}`);
}
if (!current.fills.NIK || current.fills.NIK.price !== 21
    || !current.fills.VRB || current.fills.VRB.price !== 69) {
  throw new Error("current orientation branch no longer reproduces NIK21/VRB69");
}

const closes = { NIK: 19, VRB: 83 };
const fillableLows = { NIK: 18, VRB: 70 };
const tunedOutcome = {
  pair_complete: Boolean(tuned.fills.NIK && tuned.fills.VRB),
  pair_cost_cents: tuned.fills.NIK.price + tuned.fills.VRB.price,
  individual_delta_to_close_cents: {
    NIK: tuned.fills.NIK.price - closes.NIK,
    VRB: tuned.fills.VRB.price - closes.VRB,
  },
  combined_delta_to_close_cents:
    tuned.fills.NIK.price - closes.NIK + tuned.fills.VRB.price - closes.VRB,
  gap_to_own_fillable_low_cents: {
    NIK: tuned.fills.NIK.price - fillableLows.NIK,
    VRB: tuned.fills.VRB.price - fillableLows.VRB,
  },
  grading_note: "both legs are independently within one cent of their own frozen fillable low; no aggregate leg offsets the other",
};

const eventKindCounts = {};
for (const row of rawClock) eventKindCounts[row.event_kind] = (eventKindCounts[row.event_kind] || 0) + 1;
const marketReceiptCount = Object.entries(eventKindCounts)
  .filter(([kind]) => kind.startsWith("BBO_") || kind.startsWith("PRINT_"))
  .reduce((sum, [, count]) => sum + count, 0);
const noDecisionCounts = {};
for (const row of tuned.decision_ledger.filter((row) => !row.material)) {
  noDecisionCounts[row.action] = (noDecisionCounts[row.action] || 0) + 1;
}

const firstAsk18 = rawClock.find((row) => Number(row.NIK_ask) === 18);
const firstPrint18 = rawClock.find((row) => row.event_kind === "PRINT_NIK" && Number(row.NIK_print_price) === 18);
const nondecisionSummary = {
  raw_clock_rows: rawClock.length,
  lawful_market_receipts_reconsidered: marketReceiptCount,
  material_decisions: tuned.material_decisions.length,
  repeated_nondecision_counts: noDecisionCounts,
  lock_points: {
    before_first_true_print: "discovery gate: no price authority",
    while_resting: "hold unless a named consultation, fill receipt, T2 sibling-shape resolution, or full-cell release fires",
    patience: "no NIK order until its live bid is one full five-cent cell below the T2 arm bid and VRB remains above its fill",
    after_leg_fill: "that leg's entry route is locked; books and tape remain readable",
    after_pair_fill: "all Window-1 entry routes are locked",
  },
  first_NIK_ask_18: firstAsk18 ? {
    timestamp_et: firstAsk18.timestamp_et,
    tminus_scheduled: firstAsk18.tminus_scheduled,
    tminus_bell: firstAsk18.tminus_actual_bell,
    tuned_state: "PAIR_ENTRY_COMPLETE; NIK already filled 19 on independent print evidence",
  } : null,
  first_NIK_print_18: firstPrint18 ? {
    timestamp_et: firstPrint18.timestamp_et,
    tminus_scheduled: firstPrint18.tminus_scheduled,
    tminus_bell: firstPrint18.tminus_actual_bell,
    tuned_state: "PAIR_ENTRY_COMPLETE; no re-buy",
  } : null,
};

const clockBySequence = new Map(rawClock.map((row) => [Number(row.sequence), row]));
const visualOrder = (order) => {
  const start = clockBySequence.get(order.action_sequence);
  const end = clockBySequence.get(order.end_sequence);
  return {
    leg: order.leg,
    price: order.price,
    quantity: order.quantity,
    start_sequence: order.action_sequence,
    start_et: order.action_et,
    start_tminus_scheduled: start.tminus_scheduled,
    start_tminus_bell: start.tminus_actual_bell,
    end_sequence: order.end_sequence,
    end_et: order.end_et,
    end_tminus_scheduled: end.tminus_scheduled,
    end_tminus_bell: end.tminus_actual_bell,
    end_reason: order.end_reason,
    authority: order.authority,
  };
};
const visualAcceptance = {
  schema_version: "NIKVRB_VISUAL_ACCEPTANCE_V1",
  clock_source: INPUTS.clock[0],
  clock_sha256: INPUTS.clock[1],
  current_orientation_branch: {
    orders: current.order_intervals.map(visualOrder),
    fills: current.fills,
  },
  corrected_sibling_shape_branch: {
    orders: tuned.order_intervals.map(visualOrder),
    fills: tuned.fills,
  },
  acceptance_marks: {
    VRB: "both branches rest 69 before strict ask 68 credits 69",
    NIK_current: "21 remains resting until the later public print 19 credits 21",
    NIK_corrected: "21 cancels at T-119.350 scheduled; 19 rests from T-109.050 until public print 19 credits 19 at T-80.651",
    later_ask_18: "arrives at T-57.483 scheduled after pair-entry lock; no re-buy",
  },
};

const visitDecisions = visits.map((visit) => ({
  visit: Number(visit.visit),
  time_et: visit.valid_from_et,
  tminus_scheduled: visit.tminus_scheduled_at_start,
  tminus_bell: visit.tminus_bell_at_start,
  book: `${visit.quote_state_bid}/${visit.quote_state_ask}`,
  current: visit.decision,
  tuned: Number(visit.visit) === 1
    ? "NO_ORDER_YET__VRB_DISCOVERY_NOT_COMPLETE"
    : Number(visit.visit) === 2
      ? "STRICT_ASK_68_CREDITS_RESTING_69_BEFORE_REPRICE"
      : "VRB_ALREADY_FILLED_69__ENTRY_PHASE_LOCKED",
  english: Number(visit.visit) === 1
    ? "The ask reached 68 before VRB had a verified discovery call, so the OS had no lawful order to hold or move."
    : Number(visit.visit) === 2
      ? "The 69 riser bid was already resting. Ask 68 was strictly through it, so fill accounting signed 69 before the resting manager could cancel."
      : "VRB was already filled at 69. The repeated ask-68 pulse updated shape memory but could not trigger another entry.",
}));

const material = tuned.material_decisions.map((row, i) => ({
  decision_number: i + 1,
  timestamp_et: row.timestamp_et,
  tminus_scheduled: row.tminus_scheduled,
  tminus_bell: row.tminus_bell,
  joint_observation: row.joint_observation,
  shapes: row.shapes,
  organ: row.organ,
  organ_returns: row.organ_returns || null,
  door_opened: row.door_opened,
  signer: row.signer,
  action: row.action,
  declined: row.declined,
  code_path: row.code_path,
  english: row.english,
}));

const summary = {
  schema_version: "NIKVRB_SIBLING_SHAPE_COLD_REPLAY_V1",
  event: trace.event,
  scope: "one-event cold replay; score-free; no population inference; live_v4 unchanged",
  candidate: {
    name: "orientation_riser_plus_sibling_shape_faller_patience",
    orientation_riser: "existing orientation-conditioned live-bid branch",
    faller_patience_arm: "first lawful receipt inside existing T2 bucket when sibling riser remains above fill after at least one raw quote recurrence",
    faller_release: "current faller bid moves one existing five-cent price cell below its arm bid while sibling support remains intact",
    faller_price_authority: "current lawful non-crossed external best bid; no table and no future low",
  },
  current_outcome: {
    fills: current.fills,
    pair_complete: true,
    pair_cost_cents: current.fills.NIK.price + current.fills.VRB.price,
    individual_delta_to_close_cents: {
      NIK: current.fills.NIK.price - closes.NIK,
      VRB: current.fills.VRB.price - closes.VRB,
    },
    combined_delta_to_close_cents:
      current.fills.NIK.price - closes.NIK + current.fills.VRB.price - closes.VRB,
    gap_to_own_fillable_low_cents: {
      NIK: current.fills.NIK.price - fillableLows.NIK,
      VRB: current.fills.VRB.price - fillableLows.VRB,
    },
  },
  tuned_outcome: tunedOutcome,
  exact_acceptance: expected,
  fluidity: nondecisionSummary,
  vrb_ask_68_visits: visitDecisions,
  live_v4_modified: false,
  population_run: false,
};

function bookText(book) {
  return `${book.bid ?? "—"}/${book.ask ?? "—"}/${book.last ?? "—"}; spread ${book.spread ?? "—"}; dwell ${book.dwell_seconds ?? "—"}s; last ${book.last_trade_provenance.state}`;
}

function returnsText(row) {
  if (!row.organ_returns) return "none";
  return Object.entries(row.organ_returns)
    .map(([key, value]) => `${key}=${typeof value === "object" ? JSON.stringify(value) : value}`)
    .join("; ");
}

const materialRows = material.map((row) => `| ${row.decision_number} | ${cleanText(row.tminus_scheduled)} / ${cleanText(row.tminus_bell)} | NIK ${cleanText(bookText(row.joint_observation.NIK))}; VRB ${cleanText(bookText(row.joint_observation.VRB))} | ${cleanText(row.shapes.VRB)} / ${cleanText(row.shapes.NIK)} | ${cleanText(row.organ)} → ${cleanText(row.door_opened)} | ${cleanText(returnsText(row))} | ${cleanText(row.signer)} | ${cleanText(row.action)}; overwritten/declined ${cleanText(row.declined)} |`).join("\n");

const visitRows = visitDecisions.map((row) => `| ${row.visit} | ${row.tminus_scheduled} / ${row.tminus_bell} | ${row.book} | ${cleanText(row.english)} |`).join("\n");
const noDecisionRows = Object.entries(noDecisionCounts)
  .sort((a, b) => b[1] - a[1])
  .map(([action, count]) => `| ${action} | ${count.toLocaleString("en-US")} | ${action.includes("PATIENCE") ? "Sibling shape had armed patience; the local one-cell release had not fired." : action.includes("COMPLETE") ? "The credited fill locked entry while books and tape remained readable." : action.startsWith("HOLD_") ? "The existing resting order remained lawful and no named transition fired." : "No causal entry door was open."} |`)
  .join("\n");

const report = `# NIK–VRB sibling-shape cold replay

## Result

The tune changes the faller at the joint-tree level, not by choosing a deeper table row. The current orientation-conditioned branch buys VRB at **69** and NIK at **21**: NIK is two cents above its own 19 close and three cents above its own 18 fillable low, so the pair's combined success depends on VRB carrying it. In the corrected branch VRB still rests **69** at T−316.033 scheduled / T−321.033 bell and is credited by strict ask 68 at T−314.633 / T−319.633. NIK rests 21 early, but at the first lawful receipt inside the existing T2 timing bucket the realized VRB pulse path cancels that exposure. NIK then waits unexposed until its own live bid falls one complete existing five-cent cell, from 24 to 19. The current bid signs 19 at T−109.050 / T−114.050; a strictly later public print at 19 credits it at T−80.651 / T−85.651.

The frozen close references are VRB 83 and NIK 19. Individual deltas are **−14** and **0**; combined delta is **−14**. Against each leg's own frozen fillable low, VRB 69 is one cent better than the print floor via strict ask and NIK 19 is one cent above its 18 low. The result no longer depends on one leg paying for a bad sibling entry. Any letter grade still depends on the separately declared N-cent tolerance; this replay does not invent it.

## The tune

1. Orientation still opens VRB's riser-near-now door and NIK's faller door.
2. At the first receipt inside the already-existing T2 bucket (60–120 minutes before schedule), the joint reader asks whether the riser is still above its fill and has completed a causal raw-quote recurrence. If yes, the riser shape is *realized*, and the inverse faller order is cancelled into patience.
3. Patience releases only when the faller's own live bid has moved one existing five-cent price cell below the arm bid while the sibling remains above its fill. The current external bid signs the price. No ATLAS depth and no future low participates.
4. The release receipt cannot fill its new order. Only a strictly later print or strict ask can credit it.

Implementation path: buildConsultations → ColdReplay.process:siblingShapePatienceArm → ColdReplay.process:fallerPatienceRelease → ColdReplay._fillEvidence → ColdReplay._fill in arb-executor/analysis/nikvrb_sibling_shape_cold_replay.js. Production live_v4.py is byte-identical to the parent and is not armed by this one-event tune.

## Every material decision, in order

The complete receipt-by-receipt English ledger is frozen as NIKVRB_DECISION_PROCESS_ENGLISH.jsonl.gz.b64 (base64-wrapped deterministic gzip so repository LF normalization cannot corrupt it). This table is the readable state-changing spine. Every row contains both books, spread, dwell, last-trade provenance, both shape calls, the organ, opened door, signer, action, declined action, and code path.

| # | Scheduled / bell | Joint observation (bid/ask/last) | Shape call: VRB / NIK | Organ and door | Organ returns | Price signer | Action and overwritten/declined action |
|---:|---|---|---|---|---|---|---|
${materialRows}

## What the shapes mean

- **VRB riser, climbing with pulses:** expect the useful VRB entry early, before T2. A divot is a recurrence opportunity, not evidence that the path has reversed.
- **NIK inverse faller:** while VRB keeps resolving upward, NIK's early depth is not terminal. The useful NIK move is expected after the T2 door opens, so an early table-generated bid loses authority when the sibling shape becomes realized.
- **Late faller impulse:** one full live price-cell move on NIK, with VRB still above its fill, changes “wait” into “rest at the current bid.” It predicts a retouch/print at the new live level; it does not predict an unseen 18.

## VRB's nine ask-68 visits

| Visit | Scheduled / bell | VRB book | Tuned decision in English |
|---:|---|---|---|
${visitRows}

The pre-orientation OS cancelled 67 on visit 2, reconceived 65, then repeated quiet-staircase HOLD. Both the current orientation branch and this tuned branch instead let fill accounting consume ask 68 against the already-resting 69 before the resting manager runs. Visits 3–9 are therefore shape observations, not entry decisions.

## NIK's late slide and the non-decisions

At T−119.350 / T−124.350, the joint-shape organ cancels 21 and deliberately has no NIK order. From there, every receipt asks the same causal question: has NIK's **live bid** moved a full five-cent cell from 24 while VRB remains above 69? Until the answer is yes, the result is a named patience HOLD with no order.

At T−109.050 / T−114.050, NIK's bid first reaches 19 while the ask is 27 and VRB is 73/77. The full cell has arrived. The live bid signs 19. The order rests for 1,703.923 seconds. At T−80.651 / T−85.651, a positive-size public print at 19 fills it. When ask later reaches 18 at ${nondecisionSummary.first_NIK_ask_18.tminus_scheduled} / ${nondecisionSummary.first_NIK_ask_18.tminus_bell}, the OS believes both entries are complete; it records the lower book but correctly declines a fourth entry or re-buy.

| Repeated decision | Receipts | English reason |
|---|---:|---|
${noDecisionRows}

## How fluid the process is

The cold clock contains **${rawClock.length.toLocaleString("en-US")}** ordered rows, of which **${marketReceiptCount.toLocaleString("en-US")}** are BBO or true-print receipts. Each receipt refreshes the joint observation and reaches a named gate, but only **${tuned.material_decisions.length}** state-changing decisions occur. Reconsideration is therefore frequent; authority changes are sparse.

The chain unlocks only on: a lawful discovery consultation, strict fill evidence, entry into the existing T2 timing bucket with a resolved sibling shape, a full live price-cell move on the faller, or the Window-1 boundary. It locks at three places: missing discovery evidence, a resting-order HOLD without a named trigger, and the filled-phase gate. The important repair is that the T2 sibling-shape transition now sits *before* the filled-phase lock on NIK; 21 is cancelled while entry is still reachable.

## Scope fence

This is a cold, one-event, score-free replay against frozen July 19 chronology. It reads no future row at a decision, runs no 804-event population, changes no production candidate, and does not modify or execute live_v4.py. The full ledger makes the silences explicit rather than treating absence of an action as absence of a decision.
`;

const outputMap = new Map();
function addOutput(relative, bytes) {
  outputMap.set(relative, Buffer.isBuffer(bytes) ? bytes : Buffer.from(bytes));
}

addOutput("NIKVRB_REPLAY_SUMMARY.json", canonical(summary));
addOutput("NIKVRB_MATERIAL_DECISIONS.json", canonical(material));
addOutput("NIKVRB_NONDECISION_CENSUS.json", canonical(nondecisionSummary));
addOutput("NIKVRB_VRB_ASK68_TUNED_DECISIONS.json", canonical(visitDecisions));
addOutput("NIKVRB_CURRENT_ORDER_INTERVALS.json", canonical(current.order_intervals));
addOutput("NIKVRB_TUNED_ORDER_INTERVALS.json", canonical(tuned.order_intervals));
addOutput("NIKVRB_VISUAL_ACCEPTANCE.json", canonical(visualAcceptance));
addOutput("NIKVRB_DECISION_PROCESS_ENGLISH.jsonl.gz.b64", gzipJsonlBase64(tuned.decision_ledger));
addOutput("SOURCE_HASH_MANIFEST.json", canonical({ schema_version: "NIKVRB_SIBLING_SHAPE_SOURCE_MANIFEST_V1", sources: sourceManifest }));
addOutput("FORBIDDEN_ACCESS_RECEIPT.json", canonical({
  schema_version: "NIKVRB_SIBLING_SHAPE_FORBIDDEN_ACCESS_V1",
  population_run: false,
  scorer_imported_or_invoked: false,
  live_v4_imported_or_invoked: false,
  live_network_order_position_exit_settlement_access: false,
  holdout_access: false,
  production_file_modified: false,
}));
addOutput("../../../arb-executor/docs/research/window1/NIKVRB_SIBLING_SHAPE_REPLAY.md", report);

const artifactRows = [...outputMap.entries()].map(([relative, bytes]) => ({
  path: relative.startsWith("../") ? "arb-executor/docs/research/window1/NIKVRB_SIBLING_SHAPE_REPLAY.md" : `.claude/window1_live_v4_replay/nikvrb_sibling_shape_tune_20260731/${relative}`,
  bytes: bytes.length,
  sha256: sha256(bytes),
})).sort((a, b) => a.path.localeCompare(b.path));
addOutput("ARTIFACT_HASH_MANIFEST.json", canonical({ schema_version: "NIKVRB_SIBLING_SHAPE_ARTIFACT_MANIFEST_V1", artifacts: artifactRows }));
addOutput("DETERMINISTIC_REGENERATION_RECEIPT.json", canonical({
  schema_version: "NIKVRB_SIBLING_SHAPE_DETERMINISM_V1",
  command: "node arb-executor/analysis/build_nikvrb_sibling_shape_reference.js . --check",
  canonical_json: "JSON.stringify(value, null, 2) plus LF",
  gzip: "level=9, mtime=0; base64 text wrapper protects compressed bytes from repository LF normalization",
  source_rows: rawClock.length,
  ledger_rows: tuned.decision_ledger.length,
  output_hashes: artifactRows,
}));

for (const [relative, bytes] of outputMap.entries()) {
  const target = relative.startsWith("../") ? path.join(outDir, relative) : path.join(outDir, relative);
  if (checkOnly) {
    const existing = fs.readFileSync(target);
    if (!existing.equals(bytes)) throw new Error(`determinism mismatch ${target}`);
  } else {
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, bytes);
  }
}

const result = {
  status: checkOnly ? "CHECK_PASS" : "BUILT",
  event: trace.event,
  source_rows: rawClock.length,
  ledger_rows: tuned.decision_ledger.length,
  material_decisions: tuned.material_decisions.length,
  current: { NIK: current.fills.NIK && current.fills.NIK.price, VRB: current.fills.VRB && current.fills.VRB.price },
  tuned: { NIK: tuned.fills.NIK.price, VRB: tuned.fills.VRB.price, combined_delta: tunedOutcome.combined_delta_to_close_cents },
  patience: tuned.patience,
  population_run: false,
  live_v4_modified: false,
};
process.stdout.write(canonical(result));
